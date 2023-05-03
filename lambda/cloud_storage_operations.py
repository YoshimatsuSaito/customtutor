import os
import pickle
from typing import Any

import boto3

BUCKET_NAME = os.environ.get("BUCKET_NAME")


class CloudStorageAPI:
    """Cloud Storage API for AWS S3
    TODO: error handling"""
    def __init__(self, bucket_name: str=BUCKET_NAME):
        self.bucket_name = bucket_name
        self.s3_resource = None

    def set_resource(self) -> None:
        """set s3 resource"""
        self.s3_resource = boto3.resource("s3")

    def read_pkl_from_s3(self, file_name) -> Any:
        """read pickle file from S3"""
        s3_resource_bucket = self.s3_resource.Bucket(self.bucket_name)
        data = pickle.loads(s3_resource_bucket.Object(file_name).get()["Body"].read())
        return data

    def write_pkl_to_s3(self, file, file_name) -> None:
        """write pickle file to s3"""
        pickle_byte_obj = pickle.dumps(file)
        s3_resource_output_object = self.s3_resource.Object(self.bucket_name, file_name)
        s3_resource_output_object.put(Body=pickle_byte_obj)

    def get_list_topic(self) -> list[str]:
        """get file list saved in S3"""
        bucket = self.s3_resource.Bucket(self.bucket_name)
        list_topicdir = []
        for obj in bucket.objects.all():
            topicdir = obj.key.split('/')[0]
            if topicdir not in list_topicdir:
                list_topicdir.append(topicdir)
        return list_topicdir
    