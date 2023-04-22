import pickle

import streamlit as st

from modules.cloud_storage_operations import CloudStorageAPI


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
            label="Download This Document",
            data=document,
            file_name=f"{topic}.md",
            mime="text/markdown",
        )
    with col_download_pickle:
        # download pickle data
        pickle_data = pickle.dumps(data_to_export)
        st.download_button(
            label="Download This Document As Pickle Data",
            data=pickle_data,
            file_name=f"{topic}.pkl",
            mime="application/octet-stream",
        )
    with col_export_cloud:
        # export to cloud
        if st.button("Export This Document to Cloud Storage"):
            # TODO: duplicate topic check
            cloud_storage_api = CloudStorageAPI()
            cloud_storage_api.set_resource()
            cloud_storage_api.write_pkl_to_s3(data_to_export, f"{topic}.pkl")
            st.info(f"export {topic}.pkl to cloud storage")

