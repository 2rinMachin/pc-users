import boto3

from common import response, table_name
from schemas import UserResponseDto

dynamodb = boto3.resource("dynamodb")
users = dynamodb.Table(table_name("users"))


def handler(event, context):
    tenant_id = event["pathParameters"]["tenant_id"]
    user_id = event["pathParameters"]["user_id"]

    resp = users.get_item(Key={"tenant_id": tenant_id, "user_id": user_id})
    item: dict | None = resp.get("Item")

    if item == None:
        return response(404, {"message": "User not found."})

    return response(200, UserResponseDto(**item))
