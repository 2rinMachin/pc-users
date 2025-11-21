import boto3
from boto3.dynamodb.conditions import Key

from common import table_name
from schemas import SessionToken, User

dynamodb = boto3.resource("dynamodb")
session_tokens = dynamodb.Table(table_name("session-tokens"))


def handler(event, context):
    user = User(**event["detail"])

    tokens = session_tokens.query(
        IndexName="tenant-user-idx",
        KeyConditionExpression=(
            Key("tenant_id").eq(user.tenant_id) & Key("user_id").eq(user.user_id)
        ),
    )

    if not "Items" in tokens:
        return

    items: list[dict] | None = tokens["Items"]

    with session_tokens.batch_writer() as batch:
        for item in items:
            token_data = SessionToken(**item)
            batch.delete_item(Key={"token": token_data.token})
