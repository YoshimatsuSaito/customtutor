import json
import os

import boto3

from dotenv import load_dotenv

# load .env file
load_dotenv(".env")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
REGION_NAME = os.environ.get("REGION_NAME")


class LambdaAPI:
    """Lambda API for AWS Lambda"""
    def __init__(self, aws_access_key_id: str=AWS_ACCESS_KEY_ID, aws_secret_access_key: str=AWS_SECRET_ACCESS_KEY, region_name: str=REGION_NAME) -> None:
        self.lambda_client = boto3.client("lambda", aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name)

    def invoke(self, topic: str, time_send: str) -> None:
        payload = {"topic": topic, "time_send": time_send}
        self.lambda_client.invoke(
            FunctionName="generate-document",
            InvocationType="Event",
            Payload=json.dumps(payload),
        )
