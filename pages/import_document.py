import pickle

import streamlit as st

from modules.cloud_storage_operations import CloudStorageAPI
from modules.prompt_controller import QuestionAnsweringGenerator
from modules.utils import set_export_section, make_document

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
st.markdown("You can import a document from your local machine or cloud storage.")

# import steps from local file
col_local, col_cloud = st.columns([1, 1])

with col_local:
    uploaded_file = st.file_uploader("Import a local pickle file", type="pkl")

if uploaded_file is not None:
    data_from_local = pickle.load(uploaded_file)
    st.session_state.dict_step_imported = data_from_local["dict_step"]
    st.session_state.document_imported = make_document(dict_step=st.session_state.dict_step_imported)
    st.session_state.topic_imported = data_from_local["topic"]
    st.session_state.num_steps_imported = data_from_local["num_steps"]
    st.session_state.qa_gen_for_imported = QuestionAnsweringGenerator(
        topic=st.session_state.topic_imported, dict_step=st.session_state.dict_step_imported
    )
    st.session_state.imported = True

data_from_cloud = None
with col_cloud:
    cloud_storage_api = CloudStorageAPI()
    cloud_storage_api.set_resource()
    list_file = cloud_storage_api.get_list_pkl_file()
    topic_name = st.selectbox("Choose a documnt to import from cloud storage", list_file)
    if st.button("Import Cloud File"):
        data_from_cloud = cloud_storage_api.read_pkl_from_s3(topic_name)
        
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
    
    # download document and pickle data
    set_export_section(
        document=st.session_state.document_imported.encode(),
        topic=st.session_state.topic_imported,
        num_steps=st.session_state.num_steps_imported,
        dict_step=st.session_state.dict_step_imported,
    )
    
else:
    st.warning("Please import a pickle file.")
