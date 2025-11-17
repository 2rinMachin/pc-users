import boto3

from common import auth, table_name
from common.auth import verify_session_token

dynamodb = boto3.resource("dynamodb")
users = dynamodb.Table(table_name("users"))
session_tokens = dynamodb.Table(table_name("session-tokens"))


def handler(event, context):
    tenant_id = event.get("pathParameters", {}).get("tenant_id")
    authorization = str(event["headers"]["Authorization"])

    token = auth.extract_session_token(authorization)
    user = verify_session_token(token)

    if user == None:
        return auth.unauthorized(event)

    if tenant_id != None and user.tenant_id != tenant_id:
        return auth.unauthorized(event)

    return auth.authorized(event, user)
