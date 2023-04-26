from datetime import datetime

import pytz
import streamlit as st

from modules.cloud_storage_operations import CloudStorageAPI
from modules.prompt_controller import SequentialGenerator, QuestionAnsweringGenerator
from modules.utils import make_document

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

if "dict_step" not in st.session_state:
    st.session_state.dict_step = None

if "document" not in st.session_state:
    st.session_state.document = None

if "topic" not in st.session_state:
    st.session_state.topic = None

if "num_steps" not in st.session_state:
    st.session_state.num_steps = None

# title
st.title("Generate new document")

# input form
topic = st.text_input("Enter the topic you want to learn (e.g. Introduction to Python): ")
num_steps = st.selectbox("Select the number of steps to learn the topic", list(range(1, 11)), index=4)

# generate steps sequentially
if st.button("Generate New Document"):
    st.session_state.topic = topic
    st.session_state.num_steps = num_steps

    generator = SequentialGenerator(topic=st.session_state.topic, num_steps=st.session_state.num_steps)
    progress_bar = st.progress(0)
    for step in range(1, num_steps + 1):
        with st.spinner(f"Generating step {step} of {st.session_state.num_steps}..."):
            generator.generate_step(step)
        progress = step / num_steps
        progress_bar.progress(progress)

    # convert chat to document
    generator.make_dict_step()

    st.session_state.dict_step = generator.dict_step
    st.session_state.document = make_document(generator.dict_step)
    st.session_state.qa_gen = QuestionAnsweringGenerator(topic=generator.topic, dict_step=generator.dict_step)
    st.session_state.generated = True

# display each step
if st.session_state.generated and st.session_state.topic == topic and st.session_state.num_steps == num_steps:
    st.markdown("---")
    for step in range(1, num_steps + 1):
        col_doc, col_qa = st.columns([7, 3])
        generated_step = st.session_state.dict_step[str(step)]
        col_doc.markdown(generated_step)
        col_qa.subheader(f"Q & A of Step {step}")
        question = col_qa.text_area("Enter the question to document: ", key=f"question: {step}")
        if col_qa.button("Generate Answer", key=f"generate_answer: {step}"):
            with col_qa:
                with st.spinner(f"Generating answer..."):
                    answer = st.session_state.qa_gen.generate_answer(question=question, step=str(step))
            col_qa.write(answer)

    # export to cloud
    data_to_export = {
        "dict_step": st.session_state.dict_step,
        "topic": st.session_state.topic,
        "num_steps": st.session_state.num_steps,
    }
    st.markdown("---")
    if st.button("Export This Document to Cloud Storage"):
        # to make the dir name unique
        current_time = datetime.now(jst)
        formatted_time = current_time.strftime("%Y%m%d%H%M%S")
        # export to cloud storage
        cloud_storage_api = CloudStorageAPI()
        cloud_storage_api.set_resource()
        cloud_storage_api.write_pkl_to_s3(data_to_export, f"{topic}_{formatted_time}/document.pkl")
        st.info("This document was exported to cloud storage")

else:
    st.warning("Please generate a document first.")
