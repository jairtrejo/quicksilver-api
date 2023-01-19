import os

import attr
import boto3
import structlog

from quicksilver.prompt import Prompt

LOCAL_DYNAMO_ENDPOINT = "http://docker.for.mac.localhost:8000/"
logger = structlog.get_logger(__name__)

if os.getenv("AWS_SAM_LOCAL"):
    dynamodb = boto3.resource("dynamodb", endpoint_url=LOCAL_DYNAMO_ENDPOINT)
    os.environ.setdefault("DYNAMO_TABLE_NAME", "PrompTable")
else:
    dynamodb = boto3.resource("dynamodb")


def _to_dynamo(prompt):
    table = dynamodb.Table(os.getenv("DYNAMO_TABLE_NAME"))

    writable = {
        field: value
        for field, value in prompt.asdict().items()
        if field != "id" and not (field == "used_at" and value is None)
    }

    clauses = ", ".join(
        "{field} = :{field}".format(field=field) for field in writable
    )

    table.update_item(
        Key={"id": prompt.id},
        UpdateExpression="SET %s" % clauses,
        ExpressionAttributeValues={
            ":{field}".format(field=field): value
            for field, value in writable.items()
        },
    )


def _from_dynamo(prompt_id):
    table = dynamodb.Table(os.getenv("DYNAMO_TABLE_NAME"))

    row = table.get_item(Key={"id": prompt_id})
    prompt_data = row.get("Item", None)

    return prompt_data


@attr.s
class Prompts:
    def save(prompt):
        _to_dynamo(prompt)
        return prompt

    @classmethod
    def from_id(cls, prompt_id):
        prompt_data = _from_dynamo(prompt_id)

        prompt = None
        if prompt_data:
            prompt = Prompt(**prompt_data)

        return prompt

    @classmethod
    def unused_ids(cls):
        table = dynamodb.Table(os.getenv("DYNAMO_TABLE_NAME"))
        response = table.scan(
            IndexName="created_at",
            Select="ALL_PROJECTED_ATTRIBUTES",
            ScanFilter={
                "used_at": {
                    "AttributeValueList": [],
                    "ComparisonOperator": "NULL",
                }
            },
        )

        return [item["id"] for item in response["Items"]]
