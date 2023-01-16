import os

import attr
import boto3
import structlog

LOCAL_DYNAMO_ENDPOINT = "http://docker.for.mac.localhost:8000/"
logger = structlog.get_logger(__name__)

if os.getenv("AWS_SAM_LOCAL"):
    dynamodb = boto3.resource("dynamodb", endpoint_url=LOCAL_DYNAMO_ENDPOINT)
    os.environ.setdefault("DYNAMO_TABLE_NAME", "PrompTable")
else:
    dynamodb = boto3.resource("dynamodb")


def _to_dynamo(prompt):
    logger.debug("Saving to dynamo", table_name=os.getenv("DYNAMO_TABLE_NAME"))
    table = dynamodb.Table(os.getenv("DYNAMO_TABLE_NAME"))

    clauses = ", ".join(
        "{field} = :{field}".format(field=field)
        for field in prompt.asdict(
            filter=lambda attr, _: attr.name not in ("id", "used_at")
        )
    )

    table.update_item(
        Key={"id": prompt.id, "used_at": prompt.created_at},
        UpdateExpression="SET %s" % clauses,
        ExpressionAttributeValues={
            ":{field}".format(field=field): value
            for field, value in prompt.asdict().items()
            if field not in ("id", "used_at")
        },
    )


@attr.s
class Prompts:
    def save(prompt):
        _to_dynamo(prompt)
        return prompt
