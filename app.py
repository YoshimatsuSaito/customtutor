import streamlit as st

from modules.prompt_controller import (
    SequentialGenerator,
    QuestionAnsweringGenerator,
)

# setting of page
st.set_page_config(
    page_title="Custom Tutor",
    page_icon=":robot_face:",
    layout="wide",
)
# title
st.title("Custom Tutor")

# input form
topic = st.text_input("Enter the topic you want to learn (e.g. Introduction to Python): ")
num_steps = st.selectbox("Select the number of steps to learn the topic", list(range(1, 11)), index=4)

# Initialize session_state if not already
if "generated" not in st.session_state:
    st.session_state.generated = False

if "qa_gen" not in st.session_state:
    st.session_state.qa_gen = None

if "dict_step" not in st.session_state:
    st.session_state.dict_step = None

# generate steps sequentially
if st.button("Generate Document"):
    generator = SequentialGenerator(topic=topic, num_steps=num_steps)
    progress_bar = st.progress(0)
    for step in range(1, num_steps + 1):
        with st.spinner(f"Generating step {step} of {num_steps}..."):
            generator.generate_step(step)
        progress = step / num_steps
        progress_bar.progress(progress)

    # convert chat to document
    generator.make_dict_step()
    generator.make_document()

    st.session_state.dict_step = generator.dict_step
    st.session_state.qa_gen = QuestionAnsweringGenerator(dict_step=generator.dict_step)
    st.session_state.generated = True

# display each step
if st.session_state.generated:
    for step in range(1, num_steps + 1):
        col1, col2 = st.columns([7, 3])

        generated_step = st.session_state.dict_step[str(step)]
        col1.markdown(generated_step)
        col2.subheader(f"Q & A of Step {step}")
        question = col2.text_area("Enter the question to document: ", key=f"question: {step}")
        if col2.button("Generate Answer", key=f"generate_answer: {step}"):
            with col2:
                with st.spinner(f"Generating answer..."):
                    answer = st.session_state.qa_gen.generate_answer(question=question, step=str(step))
            col2.write(answer)
else:
    st.write("Please generate a document first.")
