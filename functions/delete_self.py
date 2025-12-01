import boto3

from common import PROJECT_NAME, response, table_name
from schemas import AuthorizedUser

dynamodb = boto3.resource("dynamodb")
events = boto3.client("events")


users = dynamodb.Table(table_name("users"))


def handler(event, context):
    user = AuthorizedUser(**event["requestContext"]["authorizer"])

    tenant_id = event["pathParameters"]["tenant_id"]

    users.delete_item(Key={"tenant_id": tenant_id, "user_id": user.user_id})

    events.put_events(
        Entries=[
            {
                "Source": f"{PROJECT_NAME}.users",
                "DetailType": "user.deleted",
                "Detail": user.model_dump_json(),
            }
        ]
    )

    return response(204, None)
