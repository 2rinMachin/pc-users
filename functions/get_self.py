from common import response
from schemas import UserResponseDto


def handler(event, context):
    user = UserResponseDto(**event["requestContext"]["authorizer"])
    return response(200, user)
