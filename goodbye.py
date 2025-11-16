import json
import boto3
import random


def handler(event, context) :
    dynamodb =  boto3.resource('dynamodb')
    users = dynamodb.Table('pc-users-users')

    new_user = {
        'tenant_id': 'local-1',
        'user_id': str(random.randint(0, 1000000))
    }

    users.put_item(Item=new_user)

    return {
        'statusCode': 200,
        'headers': { 'Content-Type': 'application/json' },
        "body": json.dumps(new_user),
    }
