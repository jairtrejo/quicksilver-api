import json
import os
from functools import wraps

import attr
import structlog
from inflection import camelize, underscore

import quicksilver.logconfig as logconfig

logger = structlog.get_logger(__name__)


@attr.s
class Response:
    """
    An HTTP response
    """

    status_code = attr.ib()
    body = attr.ib(default=None)
    headers = attr.ib(factory=dict)

    def set_cookie(self, name, value):
        self.headers["Set-Cookie"] = name + "=" + value
        return self

    def asdict(self):
        response = {"statusCode": self.status_code}
        if self.body is not None:
            response["body"] = self.body
        if len(self.headers) != 0:
            response["headers"] = self.headers

        return response


def api_handler(*args, model=None):
    """
    A decorator for API call handlers

    Args:
        model (class): An attr class to build an instance from JSON body.
    """

    def to_handler(f):
        """
        A decorator for API call handlers

        Args:
            f (function): A function that returns a :class:`Response`, or a
            JSON serializable value.
        """

        @wraps(f)
        def api_method(event, context):
            logconfig.configure()
            log = logger.new(
                request_id=context.aws_request_id,
                method=event["httpMethod"],
                resource=event["resource"],
            )

            # Query parameters
            query_parameters = event.get("queryStringParameters", {}) or {}

            # Authorization
            auth_context = event.get("requestContext", {}).get(
                "authorizer", None
            )

            if auth_context and auth_context["principalId"] != "anonymous":
                log = log.bind(user=auth_context["lyft_id"])

            # Model
            if model:
                try:
                    instance = model(
                        **{
                            underscore(k): v
                            for k, v in json.loads(event["body"]).items()
                        }
                    )
                except TypeError as e:
                    logger.error(
                        "Invalid model",
                        model=model,
                        body=event["body"],
                        exc_info=e,
                    )

                    return Response(
                        status_code=400,
                        body=json.dumps(
                            {
                                "message": "Invalid {model}".format(
                                    model=model.__name__
                                )
                            }
                        ),
                    ).asdict()

            try:
                args = [instance] if model else []
                kwargs = {
                    **query_parameters,
                    **(
                        {"auth_context": auth_context}
                        if auth_context
                        and auth_context["principalId"] != "anonymous"
                        else {}
                    ),
                }

                response = f(*args, **kwargs)

            except TypeError as e:
                logger.error(
                    "Validation error", args=args, kwargs=kwargs, exc_info=e
                )

                response = Response(
                    status_code=400,
                    body=json.dumps({"message": "Invalid request parameters"}),
                )

            except Exception as e:
                logger.error(
                    "Unexpected error", args=args, kwargs=kwargs, exc_info=e
                )
                response = Response(
                    status_code=500,
                    body=json.dumps({"message": "Internal Server Error"}),
                )

            if not response:
                response = Response(status_code=404)

            elif isinstance(response, dict):
                body = json.dumps(
                    {
                        camelize(k, uppercase_first_letter=False): v
                        for k, v in response.items()
                    }
                )
                response = Response(status_code=200, body=body)

            elif not isinstance(response, Response):
                body = json.dumps(
                    {
                        camelize(k, uppercase_first_letter=False): v
                        for k, v in response.asdict().items()
                    }
                )
                response = Response(status_code=200, body=body)

            if 200 <= response.status_code < 300:
                logger.info(
                    "Success", response=response, status=response.status_code
                )
            else:
                logger.info(
                    "Failure", response=response, status=response.status_code
                )

            response.headers["Access-Control-Allow-Origin"] = os.getenv(
                "CORS_DOMAIN"
            )
            response.headers["Access-Control-Allow-Headers"] = "Authorization"

            return response.asdict()

        return api_method

    if len(args):
        # The @api_handler(Model) use case
        return to_handler(args[0])

    else:
        # The plain @api_handler use case
        return to_handler
