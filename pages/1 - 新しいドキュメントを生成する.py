from datetime import datetime

import pytz
import streamlit as st

from modules.cloud_storage_operations import CloudStorageAPI
from modules.prompt_controller import BulkGenerator, QuestionAnsweringGenerator

# setting of page
st.set_page_config(
    page_title="Custom Tutor",
    page_icon=":robot_face:",
    layout="wide",
)
jst = pytz.timezone("Asia/Tokyo")

# Initialize session_state if not already
if "generated" not in st.session_state:
    st.session_state.generated = False

if "qa_gen" not in st.session_state:
    st.session_state.qa_gen = None

if "document" not in st.session_state:
    st.session_state.document = None

if "topic" not in st.session_state:
    st.session_state.topic = None

# title
st.title("新しい教材を生成する")

# input form
topic = st.text_input("学びたいトピック (例: Python入門): ")

# generate steps sequentially
if st.button("ドキュメントを生成する"):
    st.session_state.topic = topic

    generator = BulkGenerator(topic=st.session_state.topic)
    with st.spinner("ドキュメント作成中..."):
        generator.generate_document()

    st.session_state.document = generator.document
    st.session_state.qa_gen = QuestionAnsweringGenerator(topic=generator.topic, document=st.session_state.document)
    st.session_state.generated = True

# display each step
if st.session_state.generated and st.session_state.topic == topic:
    st.markdown("---")
    col_doc, col_qa = st.columns([7, 3])
    col_doc.markdown(st.session_state.document)
    question = col_qa.text_area("質問を入力してみよう: ", height=50)
    if col_qa.button("質問する"):
        with col_qa:
            with st.spinner("回答生成中..."):
                answer = st.session_state.qa_gen.generate_answer(question=question)
        col_qa.write(answer)

    st.markdown("---")

    rating = st.slider("ドキュメントを評価する(1~5)", min_value=0.0, max_value=5.0, value=0.0, step=1.0)
    if st.button("ドキュメントをクラウドストレージに登録してシェアする"):
        if rating < 1:
            st.warning("1から5の間で評価してください。")
        else:
            # to make the dir name unique
            current_time = datetime.now(jst)
            formatted_time = current_time.strftime("%Y%m%d%H%M%S")
            dir_name = f"{topic}_{formatted_time}"

            # data to export
            data_to_export = {
                "document": st.session_state.document,
                "topic": st.session_state.topic,
            }
            
            # export to cloud storage
            cloud_storage_api = CloudStorageAPI()
            cloud_storage_api.set_resource()
            cloud_storage_api.write_pkl_to_s3(data_to_export, f"{dir_name}/document.pkl")
            cloud_storage_api.write_pkl_to_s3([rating], f"{dir_name}/rating.pkl")
            st.info("クラウドストレージに登録しました！")

else:
    st.warning("ドキュメントを生成してください")
