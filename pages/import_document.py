import pickle

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

# title
st.title("Import document")

data_from_cloud = None
cloud_storage_api = CloudStorageAPI()
cloud_storage_api.set_resource()
list_topic = cloud_storage_api.get_list_topic()
topic_name = st.selectbox("Choose a documnt to import from cloud storage", list_topic)
if st.button("Import Cloud File"):
    data_from_cloud = cloud_storage_api.read_pkl_from_s3(f"{topic_name}/document.pkl")
        
if data_from_cloud is not None:
    st.session_state.dict_step_imported = data_from_cloud["dict_step"]
    st.session_state.document_imported = make_document(dict_step=st.session_state.dict_step_imported)
    st.session_state.topic_imported = data_from_cloud["topic"]
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
    # rating = st.slider("Rating this document", 0.0, 5.0, 2.5, 0.5)
    # if st.button("Submit Rating"):
    #     cloud_storage_api = CloudStorageAPI()
    #     cloud_storage_api.set_resource()
    #     cloud_storage_api.write_pkl_to_s3(rating, f"{topic}.pkl")
    #     st.info(f"Send your rating: {rating}")
    

else:
    st.warning("Please import a pickle file.")
