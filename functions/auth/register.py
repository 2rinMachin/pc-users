import os
import uuid

import boto3
from boto3.dynamodb.conditions import Key
from pydantic import BaseModel

from common import PROJECT_NAME, STAGE, auth, parse_body, response, table_name
from schemas import User, UserResponseDto, UserRole

TOPIC_ARN = os.environ["ORDER_ARRIVALS_TOPIC_ARN"]


class RegisterRequest(BaseModel):
    email: str
    username: str
    password: str
    role: UserRole


dynamodb = boto3.resource("dynamodb")
events = boto3.client("events")

users = dynamodb.Table(table_name("users"))


def handler(event, context):
    tenant_id = event["pathParameters"]["tenant_id"]

    data, err = parse_body(RegisterRequest, event)
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

    if resp["Count"] > 0:
        return response(409, {"message": "User with email already exists."})

    id = str(uuid.uuid4())
    hashed_pw = auth.hash_password(data.password)

    new_user = User(
        tenant_id=tenant_id,
        user_id=id,
        email=data.email.strip(),
        username=data.username.strip(),
        password=hashed_pw,
        role=data.role,
    )

    users.put_item(Item=new_user.model_dump())

    events.put_events(
        Entries=[
            {
                "Source": f"{PROJECT_NAME}-{STAGE}.users",
                "DetailType": "user.created",
                "Detail": new_user.model_dump_json(),
            }
        ]
    )

    return response(
        201, UserResponseDto.model_validate(new_user.model_dump()).model_dump_json()
    )
