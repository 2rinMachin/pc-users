from common import response
from schemas import AuthorizedUser


def handler(event, context):
    print("WHAT THE FUCK")
    user = AuthorizedUser(**event["requestContext"]["authorizer"])
    return response(200, user)
