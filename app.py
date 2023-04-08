import streamlit as st

from modules.prompt_controller import DocumentGenerator, StepGenerator


# title 
st.title("CustomTutor")

# input form
topic = st.text_input("Input topics that you want to learn (ex. Introduction to python): ")
num_steps = st.selectbox("Number of steps to learn the topic", list(range(1, 11)), index=4)
mode = st.selectbox("Mode", ["Sequential", "Each step"])

if mode == "Sequential":
    # session control
    if "dg" not in st.session_state:
        st.session_state.dg = None
    if st.session_state.dg is None or st.session_state.dg.topic != topic or st.session_state.dg.num_steps != num_steps:
        st.session_state.dg = DocumentGenerator(topic=topic, num_steps=num_steps)

    # generate steps sequentially
    if st.button("Generate documents"):
        for step in range(1, num_steps+1):
            st.session_state.dg.generate_step(step)
            generated_step = st.session_state.dg.list_message[-1]["content"]
            st.markdown(generated_step)

elif mode == "Each step":
    # session control
    if "sg" not in st.session_state:
        st.session_state.sg = None
    if st.session_state.sg is None or st.session_state.sg.topic != topic or st.session_state.sg.num_steps != num_steps:
        st.session_state.sg = StepGenerator(topic=topic, num_steps=num_steps)

    # generate each step independently
    if st.button("Generate documents"):
        for step in range(1, num_steps+1):
            st.session_state.sg.generate_a_step(step)
            generated_step = st.session_state.sg.dict_generated_step[step]
            st.markdown(generated_step)
