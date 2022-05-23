import json
import boto3
import logging


logger = logging.getLogger()
logger.setLevel(logging.INFO)

stepfunction = boto3.client('stepfunctions')

def lambda_handler(event, context):

    type= event.get('queryStringParameters').get('type')
    token= event.get('queryStringParameters').get('token')

    try:   
    
        if type =='success':
            stepfunction.send_task_success(
            taskToken=token,
            output="{}"
        )
        else:
            stepfunction.send_task_failure(
            taskToken=token
            
        )
    
        return {
            'statusCode': 200,
            'body': json.dumps('Responded to Step Function')
        }
    except Exception as e:
        message = "Bad request. Invalid syntax for this request was provided."
        logger.error(message)
        logger.error(e)
        return {"statusCode": 400, "message": message}  
