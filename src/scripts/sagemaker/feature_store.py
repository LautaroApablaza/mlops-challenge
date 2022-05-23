import argparse
import boto3
import time
import pandas as pd

from sagemaker.session import Session
from sagemaker.feature_store.feature_group import FeatureGroup



def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-file', type=str, default='train.csv')
    parser.add_argument('--input-path', type=str, default='/opt/ml/processing/input')
    parser.add_argument('--region', type=str, default="us-east-1")
    parser.add_argument('--s3-path', type=str)
    parser.add_argument('--feature-group', type=str)
    parser.add_argument('--record-identifier', type=str)
    parser.add_argument('--event-time', type=str)
    parser.add_argument('--role-arn', type=str)
    args, _ = parser.parse_known_args()    
    return args

class FeatureStore():
    '''
        '''

    def __init__(self, region : str) -> None:
        self.boto_session = boto3.Session(region=region)
        self.sagemaker_client = self.boto_session.Session(service_name="sagemaker", region_name=region)
        self.featurestore_runtime = self.boto_session.client(service_name="sagemaker-featurestore-runtime",
                                                     region_name=region)

        self.feature_store_session = Session(boto_session=self.boto_session,
                                    sagemaker_client=self.sagemaker_client,
                                    sagemaker_featurestore_runtime_client=self.featurestore_runtime)

    def get_data_for_register(self, data_file : str) -> None:
        self.data = pd.read_csv(data_file)


    def register_features(self, feature_group: str, s3_path : str, record_identifier: str, event_time: str , role_arn: str) -> None:

        self.feature_group = FeatureGroup(name = feature_group, sagemaker_session = self.featurestore_runtime )

        self.feature_group.load_feature_definitions(data_frame = self.data)

        self.feature_group.create(
        s3_uri = s3_path, 
        record_identifier_name = record_identifier,
        event_time_feature_name = event_time,
        role_arn = role_arn,
        enable_online_store = True
        )

        while self.feature_group.describe().get("FeatureGroupStatus") == "Creating":
            time.sleep(5)
        if self.feature_group.describe().get("FeatureGroupStatus") != "Created":
            raise RuntimeError(f"Failed to create feature store")


    def ingest_data(self) -> None:
        self.feature_group.ingest(data_frame = self.data, max_workers = 3, wait = True)

def main() -> None:
    args = parse_args()
    feature_store = FeatureStore(region= args.region)
    feature_store.get_data_for_register(args.data_file)
    feature_store.register_features(args.feature_group, args.s3_path, args.record_identifier, args.event_time, args.role_arn)
    feature_store.ingest_data()

if __name__ == '__main__':
    main()