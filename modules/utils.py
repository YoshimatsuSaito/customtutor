import os
import pickle

import boto3
import streamlit as st

from dotenv import load_dotenv

# load .env file
load_dotenv(".env")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = os.environ.get("BUCKET_NAME")


def get_resource(aws_access_key_id: str, aws_secret_access_key: str) -> boto3.resource:
    s3_resource = boto3.resource(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )
    return s3_resource

def make_document(dict_step: dict[str, str]) -> str:
    """chatリストからmarkdownドキュメントを生成する"""
    document = ""
    for step in dict_step.keys():
        document += dict_step[step] + "\n\n"
    return document


def set_export_section(document: str, topic: str, num_steps:int, dict_step: dict[str, str]):
    """生成したドキュメントのエクスポートセクションを設定する"""
    # download document and pickle data
    st.markdown("---")
    col_download_doc, col_download_pickle, col_export_cloud = st.columns([1, 1, 1])
    data_to_export = {
        "dict_step": dict_step,
        "topic": topic,
        "num_steps": num_steps,
    }
    with col_download_doc:
        # download document
        st.download_button(
            label="Download Document",
            data=document,
            file_name=f"{topic}.md",
            mime="text/markdown",
        )
    with col_download_pickle:
        # download pickle data
        pickle_data = pickle.dumps(data_to_export)
        st.download_button(
            label="Download Pickle Data",
            data=pickle_data,
            file_name=f"{topic}.pkl",
            mime="application/octet-stream",
        )
    with col_export_cloud:
        # export to cloud
        if st.button("Export to Cloud"):
            # TODO: duplicate topic check
            s3_resource = get_resource(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
            write_pkl_to_s3(s3_resource, data_to_export, BUCKET_NAME, f"{topic}.pkl")
            st.info(f"export {topic}.pkl to cloud storage")


def read_pkl_from_s3(file_name):
    """
    read pickle file from S3
    """
    s3_resource = get_resource(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    s3_resource_bucket = s3_resource.Bucket(BUCKET_NAME)
    data = pickle.loads(s3_resource_bucket.Object(file_name).get()["Body"].read())
    return data


def write_pkl_to_s3(s3_resource, file, bucket_name, file_name):
    """
    write pickle file to s3
    """
    pickle_byte_obj = pickle.dumps(file)
    s3_resource_output_object = s3_resource.Object(bucket_name, file_name)
    s3_resource_output_object.put(Body=pickle_byte_obj)


def get_list_file(path=None):
    """get file list saved in S3"""
    s3_resource = get_resource(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    if path is None:
        folder_info_obj = s3_resource.Bucket(BUCKET_NAME).objects.all()
    else:
        folder_info_obj = s3_resource.Bucket(BUCKET_NAME).objects.filter(Prefix=path)
    list_file = [i.key for i in folder_info_obj if ".pkl" in i.key]
    return list_file