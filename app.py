import streamlit as st

st.title("Custom Tutor")

str_markdown = """
- LLM will generate a document with the topic you want to learn by the number of steps you want to learn.
- You can ask questions about the document and LLM will answer your questions.
- Everyone who uses this app can export the document to Cloud Storage and import those documents to this app.

Go to sidebar and select the function which you want to use!
"""
st.markdown(str_markdown)
