import streamlit as st

from modules.prompt_controller import SequentialGenerator, IndependentGenerator


# title 
st.title("Custom Tutor")

# input form
topic = st.text_input("Enter the topic you want to learn (e.g. Introduction to Python): ")
num_steps = st.selectbox("Select the number of steps to learn the topic", list(range(1, 11)), index=4)
mode = st.selectbox("Choose mode", ["Sequential Generation", "Independent Generation"])


if mode == "Sequential Generation":
    # session control
    if "seq_gen" not in st.session_state:
        st.session_state.seq_gen = None
    if st.session_state.seq_gen is None or st.session_state.seq_gen.topic != topic or st.session_state.seq_gen.num_steps != num_steps:
        st.session_state.seq_gen = SequentialGenerator(topic=topic, num_steps=num_steps)

    # generate steps sequentially
    if st.button("Generate Document"):
        for step in range(1, num_steps+1):
            st.session_state.seq_gen.generate_step(step)
            generated_step = st.session_state.seq_gen.list_message[-1]["content"]
            st.markdown(generated_step)

elif mode == "Independent Generation":
    # session control
    if "ind_gen" not in st.session_state:
        st.session_state.ind_gen = None
    if st.session_state.ind_gen is None or st.session_state.ind_gen.topic != topic or st.session_state.ind_gen.num_steps != num_steps:
        st.session_state.ind_gen = IndependentGenerator(topic=topic, num_steps=num_steps)

    # generate each step independently
    if st.button("Generate Document"):
        for step in range(1, num_steps+1):
            st.session_state.ind_gen.generate_a_step(step)
            generated_step = st.session_state.ind_gen.dict_generated_step[step]
            st.markdown(generated_step)
