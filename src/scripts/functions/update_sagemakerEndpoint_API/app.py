import os,traceback, json
import logging
import boto3
from time import sleep

logger = logging.getLogger()
logger.setLevel(logging.INFO)

http_api_id=os.environ['HttpApiID']
sns_arn=os.environ['SNSArn']

sns = boto3.client('sns')
sagemaker=boto3.client('sagemaker')

def lambda_handler(event, context):

    sagemaker_endpoint= event['EndpointName']
    try:

        sagemaker_response = sagemaker.describe_endpoint(
                    EndpointName=sagemaker_endpoint
                )        
        status = sagemaker_response['EndpointStatus']

        while status == 'Creating':
            sagemaker_response = sagemaker.describe_endpoint(
                    EndpointName=sagemaker_endpoint
                )           
            status = sagemaker_response['EndpointStatus']
            sleep(10)
        
        if status == 'InService':
            msg_body=''
            url_template_sucess = f'https://{http_api_id}.execute-api.us-east-1.amazonaws.com/v1/invokeSagemakerAPI?sagemaker_endpoint={sagemaker_endpoint}'
            msg_body = f'''
            API Sagemaker Inference Endpoint: {url_template_sucess}            
            '''
        
            sns_response = sns.publish(
                TopicArn=sns_arn,    
                Message=msg_body,
                Subject='Sagemaker Inference endpoint',
                MessageStructure='string'
            )
            return {
            'statusCode': 200,
            'body': json.dumps('Email sent with API endpoint')
            }
        else:
            message = f'ERROR creating Sagemaker Endpoint {status} '
            logger.error(message)
            logger.error(e)
            return {"statusCode": 400, "message": message}
             
    except Exception as e:
        message = f'ERROR creating Sagemaker Endpoint {status} '
        logger.error(message)
        logger.error(e)
        return {"statusCode": 400, "message": message}
