import argparse
import os
import boto3
import time

from sagemaker.session import Session
from sagemaker.feature_store.feature_group import FeatureGroup

REGION = "us-central-1"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--test-size', type=float, default=0.1)
    parser.add_argument('--data-file', type=str, default='train.csv')
    args, _ = parser.parse_known_args()    
    return args

class FeatureStore():

    def __init__(self, region) -> None:
        self.sagemaker_session = boto3.Session(service_name="sagemaker", region_name=region)
        feature_store_runtime = boto_session.client(service_name="sagemaker-featurestore-runtime", region_name=REGION)

    def wait_for_feature_group_creation_complete(feature_group: FeatureGroup) -> None:
        status = feature_group.describe().get("FeatureGroupStatus")
        while status == "Creating":
            print("Waiting for Feature Group Creation")
            time.sleep(5)
            status = feature_group.describe().get("FeatureGroupStatus")
        if status != "Created":
            raise RuntimeError(f"Failed to create feature group {feature_group.name}")
        print(f"FeatureGroup {feature_group.name} successfully created.")


    def feature_store_session() -> Session:
        boto_session = boto3.Session(region_name=REGION)
        sagemaker_client = boto_session.client(service_name="sagemaker", region_name=REGION)
        feature_store_runtime = boto_session.client(service_name="sagemaker-featurestore-runtime", region_name=REGION)

        feature_store_session = Session(
            boto_session=boto_session,
            sagemaker_client=sagemaker_client,
            sagemaker_featurestore_runtime_client=feature_store_runtime
        )

        return feature_store_session

    def register_features(**context) -> None:

        config = context['ti'].xcom_pull(key='config')

        model_config = config['model']
        stage_config = _get_stage_config("register_features", config)

        fs_session = feature_store_session()

        data = _download_data_for_register_features(model_config, stage_config)  

        feature_group_name = stage_config['feature_group']

        record_identifier_name = stage_config['record_identifier']
        event_time_feature_name = stage_config['loan_date']
        

        data = data.rename(
            columns={event_time_feature_name: "EventTime"}
        )

        feature_group = FeatureGroup(name = feature_group_name, sagemaker_session = fs_session)

        feature_group.load_feature_definitions(data_frame = data)

        feature_group.create(
        s3_uri = stage_config['s3_path'], 
        record_identifier_name = record_identifier_name,
        event_time_feature_name = event_time_feature_name,
        role_arn = model_config['role'],
        enable_online_store = True
        )

        _wait_for_feature_group_creation_complete(feature_group=feature_group)

        feature_group.ingest(data_frame = data, max_workers = 3, wait = True)

    def main() -> None:
        pass

if __name__ == '__main__':
    main()