import boto3

from common import auth, response, table_name

dynamodb = boto3.resource("dynamodb")
session_tokens = dynamodb.Table(table_name("session-tokens"))


def handler(event, context):
    authorization = str(event["headers"]["Authorization"])
    token = auth.extract_session_token(authorization)

    session_tokens.delete_item(Key={"token": token})
    return response(204, None)
