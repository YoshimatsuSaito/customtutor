import numpy as np
import streamlit as st

from modules.cloud_storage_operations import CloudStorageAPI
from modules.prompt_controller import QuestionAnsweringGenerator

# setting of page
st.set_page_config(
    page_title="Custom Tutor",
    page_icon=":robot_face:",
    layout="wide",
)

# Initialize session_state if not already
if "imported" not in st.session_state:
    st.session_state.imported = False

if "qa_gen_for_imported" not in st.session_state:
    st.session_state.qa_gen_for_imported = None

if "dict_step_imported" not in st.session_state:
    st.session_state.dict_step_imported = None

if "document_imported" not in st.session_state:
    st.session_state.document_imported = None

if "topic_imported" not in st.session_state:
    st.session_state.topic_imported = None

if "topic_dir_name" not in st.session_state:
    st.session_state.topic_dir_name = None

# title
st.title("ドキュメントを読み込む")

# set up cloud storage operator
data_from_cloud = None
cloud_storage_api = CloudStorageAPI()
cloud_storage_api.set_resource()

# get list of topics and ratings
list_topic = cloud_storage_api.get_list_topic()
list_avg_rating = [np.mean(cloud_storage_api.read_pkl_from_s3(f"{topic}/rating.pkl")) for topic in list_topic]

# for user interface
list_option = [f"{topic} ★{avg_rating}" for topic, avg_rating in zip(list_topic, list_avg_rating)]
option = st.selectbox("読み込むドキュメントを選ぶ", list_option)

# get topic(dir) name
num_index = list_option.index(option)
topic = list_topic[num_index]
if st.button("読み込む"):
    data_from_cloud = cloud_storage_api.read_pkl_from_s3(f"{topic}/document.pkl")
        
if data_from_cloud is not None:
    st.session_state.document_imported = data_from_cloud["document"]
    st.session_state.topic_imported = data_from_cloud["topic"]
    st.session_state.topic_dir_name = topic # unique dir name
    st.session_state.qa_gen_for_imported = QuestionAnsweringGenerator(
        topic=st.session_state.topic_imported, document=st.session_state.document_imported
    )
    st.session_state.imported = True


# display each step
if st.session_state.imported:
    st.markdown("---")
    st.title(f"Topic: {st.session_state.topic_imported}")
    col_doc, col_qa = st.columns([7, 3])
    col_doc.markdown(st.session_state.document_imported)
    question = col_qa.text_area("質問を入力してみよう: ", height=10)
    if col_qa.button("質問する"):
        with col_qa:
            with st.spinner("回答生成中..."):
                answer = st.session_state.qa_gen_for_imported.generate_answer(question=question)
        col_qa.write(answer)

    st.markdown("---")
    rating = st.slider("ドキュメントを評価する(1~5)", min_value=0.0, max_value=5.0, value=0.0, step=1.0)
    if st.button("評価を送る"):
        if rating < 1:
            st.warning("1から5の間で評価してください。")
        else:
            # read rating from cloud storage
            ratings = cloud_storage_api.read_pkl_from_s3(f"{st.session_state.topic_dir_name}/rating.pkl")
            ratings.append(rating)
            # export to cloud storage
            cloud_storage_api.write_pkl_to_s3(ratings, f"{st.session_state.topic_dir_name}/rating.pkl")
            st.info("Your rating was added.")

else:
    st.warning("ドキュメントを読み込んでください。")
