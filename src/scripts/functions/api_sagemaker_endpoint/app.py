import json
import boto3
import logging
import os
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

http_api_id=os.environ['HttpApiID']

runtime= boto3.client('sagemaker-runtime')

def lambda_handler(event, context):

    content_type = event.get("headers").get("Content-Type")

    sagemaker_endpoint = event.get('queryStringParameters').get('sagemaker_endpoint')

    if content_type.startswith("text/csv"):
        payload = json.loads(event["payload"])
        user_id = payload["user_id"]
    elif content_type.startswith("application/json"):
        user_id = event["payload"]["user_id"]
    else:
        return {"statusCode": 400, "message": "Bad request. Invalid syntax for this request was provided."}
    try:
        url_template_sucess = f'https://{http_api_id}.execute-api.us-east-1.amazonaws.com/v1/invokeFeatureStore?user_id={user_id}'
        features = requests.get(url_template_sucess)
        response = runtime.invoke_endpoint(
            EndpointName=sagemaker_endpoint,
            Body=payload['body'],
            ContentType='text/csv'        
        )
        result = response['Body'].read().decode()

        return {
            'statusCode': 200,
            'body': json.dumps({'result':result.strip('\n')})
        }
    except Exception as e:
        message = "Bad request. Invalid syntax for this request was provided."
        logger.error(message)
        logger.error(e)
        return {"statusCode": 400, "message": message}
