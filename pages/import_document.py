import numpy as np
import streamlit as st

from modules.cloud_storage_operations import CloudStorageAPI
from modules.prompt_controller import QuestionAnsweringGenerator
from modules.utils import make_document

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

if "num_steps_imported" not in st.session_state:
    st.session_state.num_steps_imported = None

if "topic_dir_name" not in st.session_state:
    st.session_state.topic_dir_name = None

# title
st.title("Import document")

# set up cloud storage operator
data_from_cloud = None
cloud_storage_api = CloudStorageAPI()
cloud_storage_api.set_resource()

# get list of topics and ratings
list_topic = cloud_storage_api.get_list_topic()
list_avg_rating = [np.mean(cloud_storage_api.read_pkl_from_s3(f"{topic}/rating.pkl")) for topic in list_topic]

# for user interface
list_option = [f"{topic} ★{avg_rating}" for topic, avg_rating in zip(list_topic, list_avg_rating)]
option = st.selectbox("Choose a documnt to import from cloud storage", list_option)

# get topic(dir) name
num_index = list_option.index(option)
topic = list_topic[num_index]
if st.button("Import Cloud File"):
    data_from_cloud = cloud_storage_api.read_pkl_from_s3(f"{topic}/document.pkl")
        
if data_from_cloud is not None:
    st.session_state.dict_step_imported = data_from_cloud["dict_step"]
    st.session_state.document_imported = make_document(dict_step=st.session_state.dict_step_imported)
    st.session_state.topic_imported = data_from_cloud["topic"]
    st.session_state.topic_dir_name = topic # unique dir name
    st.session_state.num_steps_imported = data_from_cloud["num_steps"]
    st.session_state.qa_gen_for_imported = QuestionAnsweringGenerator(
        topic=st.session_state.topic_imported, dict_step=st.session_state.dict_step_imported
    )
    st.session_state.imported = True


# display each step
if st.session_state.imported:
    st.markdown("---")
    st.title(f"Topic: {st.session_state.topic_imported}")
    for step in range(1, st.session_state.num_steps_imported + 1):
        col_doc, col_qa = st.columns([7, 3])
        generated_step = st.session_state.dict_step_imported[str(step)]
        col_doc.markdown(generated_step)
        col_qa.subheader(f"Q & A of Step {step}")
        question = col_qa.text_area("Enter the question to document: ", key=f"question: {step}")
        if col_qa.button("Generate Answer", key=f"generate_answer: {step}"):
            with col_qa:
                with st.spinner(f"Generating answer..."):
                    answer = st.session_state.qa_gen_for_imported.generate_answer(question=question, step=str(step))
            col_qa.write(answer)

    rating = st.slider("Rating this document (1~5)", min_value=0.0, max_value=5.0, value=0.0, step=1.0)
    if st.button("Send rating"):
        if rating < 1:
            st.warning("Please rate this document between 1 and 5")
        else:
            # read rating from cloud storage
            ratings = cloud_storage_api.read_pkl_from_s3(f"{st.session_state.topic_dir_name}/rating.pkl")
            ratings.append(rating)
            # export to cloud storage
            cloud_storage_api.write_pkl_to_s3(ratings, f"{st.session_state.topic_dir_name}/rating.pkl")
            st.info("Your rating was added.")

else:
    st.warning("Please import a pickle file.")
