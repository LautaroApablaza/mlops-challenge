import os,traceback, json
import logging
import boto3
from time import sleep

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sm_client = boto3.client("sagemaker-featurestore-runtime")
feature_group = os.environ["FeatureGroup"]

def lambda_handler(event, context):

    content_type = event["headers"].get("Content-Type")

    if content_type.startswith("text/csv"):
        payload = json.loads(event["payload"])
        user_id = payload["user_id"]
    elif content_type.startswith("application/json"):
        user_id = event["payload"]["user_id"]
    else:
        return {"statusCode": 400, "message": "Bad request. Invalid syntax for this request was provided."}  

    try:
        response = sm_client.get_record(
            FeatureGroupName= feature_group,
            RecordIdentifierValueAsString= user_id)
    
        record = response["Record"]

        features = {feature["FeatureName"]: feature["ValueAsString"] for feature in record}
 
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": content_type,
            },
            "body": features,
        }

    except Exception as e:
        message = "Bad request. Invalid syntax for this request was provided."
        logger.error(message)
        logger.error(e)
        return {"statusCode": 400, "message": message}  


