import secrets
from datetime import datetime, timezone

import bcrypt
import boto3

from common import table_name
from schemas import SessionToken, User

dynamodb = boto3.resource("dynamodb")
users = dynamodb.Table(table_name("users"))
session_tokens = dynamodb.Table(table_name("session-tokens"))

PASSWD_ENCODING = "utf-8"


def hash_password(password: str) -> str:
    result = bcrypt.hashpw(password.encode(PASSWD_ENCODING), bcrypt.gensalt())
    return result.decode(PASSWD_ENCODING)


def verify_password(password: str, stored: str) -> bool:
    return bcrypt.checkpw(
        password.encode(PASSWD_ENCODING), stored.encode(PASSWD_ENCODING)
    )


def generate_session_token() -> str:
    return secrets.token_urlsafe(64)


def verify_session_token(token: str) -> User | None:
    if token == "":
        return None

    resp = session_tokens.get_item(Key={"token": token})
    item: dict | None = resp.get("Item")

    if item == None:
        return None

    token_data = SessionToken(**item)
    expires_at = datetime.fromisoformat(token_data.expires_at)

    if expires_at < datetime.now(timezone.utc):
        return None

    user_resp = users.get_item(
        Key={
            "tenant_id": token_data.tenant_id,
            "user_id": token_data.user_id,
        }
    )
    user_item: dict | None = user_resp.get("Item")

    if user_item == None:
        return None

    return User(**user_item)


def extract_session_token(authorization: str) -> str:
    return authorization.split(" ")[1]


def unauthorized(event):
    return {
        "principalId": "user",
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": "Deny",
                    "Resource": event["methodArn"],
                }
            ],
        },
    }


def authorized(event, user: User):
    return {
        "principalId": user.user_id,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": "Allow",
                    "Resource": event["methodArn"],
                }
            ],
        },
        "context": user.model_dump(),
    }
