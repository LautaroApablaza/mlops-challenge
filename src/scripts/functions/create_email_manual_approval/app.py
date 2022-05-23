import json
import os
import boto3
import urllib.parse
import logging


logger = logging.getLogger()
logger.setLevel(logging.INFO)

sns = boto3.client('sns')
sns_arn=os.environ['SNSArn']
http_api_id=os.environ['HttpApiID']

def lambda_handler(event, context):

    content_type = event["headers"].get("Content-Type")

    if content_type.startswith("text/csv"):
        payload = json.loads(event["payload"])
        s3_model_metrics_output = payload['s3_model_metrics_output']
        task_token= payload['token']
    elif content_type.startswith("application/json"):
        s3_model_metrics_output = event["payload"]['s3_model_metrics_output']
        task_token= event["payload"]['token']
    else:
        return {"statusCode": 400, "message": "Bad request. Invalid syntax for this request was provided."}  

    url_sucess = f'https://{http_api_id}.execute-api.us-east-1.amazonaws.com/v1/respond?type=success&{urllib.parse.urlencode({"token":{task_token}})}'
    
    url_fail = f'https://{http_api_id}.execute-api.us-east-1.amazonaws.com/v1/respond?type=fail&{urllib.parse.urlencode({"token":{task_token}})}'
    
    msg_body = f'''
        Please find the metrics of the model in the S3 bucket {s3_model_metrics_output}.
        
        Please select one of the following options in order to continue with the next steps in the workflow.
        
        Accept: {url_sucess}

        Reject: {url_fail}

    '''
    try: 
        response = sns.publish(
            TopicArn=sns_arn,    
            Message=msg_body,
            Subject='Approve or Reject',
            MessageStructure='string'
        )
        return {
            'statusCode': 200,
            'body': json.dumps('Email send to Approve or Reject')
        } 
    except Exception as e:
        message = "Bad request. Invalid syntax for this request was provided."
        logger.error(message)
        logger.error(e)
        return {"statusCode": 400, "message": message}  


