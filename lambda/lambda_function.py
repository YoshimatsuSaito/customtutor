import json
import os

import openai

from cloud_storage_operations import CloudStorageAPI
from prompt_controller import BulkGenerator

openai.api_key = os.environ.get("OPENAI_API_KEY")


def lambda_handler(event, context):
    # generate document
    topic = event["topic"]
    time_send = event["time_send"]
    
    generator = BulkGenerator(topic=topic)
    generator.generate_document()
    data_to_export = {
        "document": generator.document,
        "topic": topic,
    }

    # export to s3
    cloud_storage_api = CloudStorageAPI()
    cloud_storage_api.set_resource()
    cloud_storage_api.write_pkl_to_s3(data_to_export, f"{topic}_{time_send}/document.pkl")
    