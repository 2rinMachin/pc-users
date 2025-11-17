from datetime import datetime, timedelta, timezone

import boto3
from boto3.dynamodb.conditions import Key
from pydantic import BaseModel

from common import auth, parse_body, response, table_name
from schemas import SessionToken, User


class LoginRequest(BaseModel):
    email: str
    password: str


dynamodb = boto3.resource("dynamodb")
users = dynamodb.Table(table_name("users"))
session_tokens = dynamodb.Table(table_name("session-tokens"))


def handler(event, context):
    tenant_id = event["pathParameters"]["tenant_id"]

    data, err = parse_body(LoginRequest, event)
    if err != None:
        return err

    assert data != None

    resp = users.query(
        IndexName="tenant-email-idx",
        KeyConditionExpression=(
            Key("tenant_id").eq(tenant_id) & Key("email").eq(data.email)
        ),
        Limit=1,
    )

    if resp["Count"] == 0:
        return response(401, {"message": "Invalid credentials."})

    items: list[dict] = resp["Items"]
    user = User(**items[0])

    if not auth.verify_password(data.password, user.password):
        return response(401, {"message": "Invalid credentials."})

    token_value = auth.generate_session_token()
    expires_at = datetime.now(timezone.utc) + timedelta(hours=8)

    token = SessionToken(
        token=token_value,
        tenant_id=user.tenant_id,
        user_id=user.user_id,
        expires_at=expires_at.isoformat(),
    )

    session_tokens.put_item(Item=token.model_dump())

    return response(200, {"token": token_value})
