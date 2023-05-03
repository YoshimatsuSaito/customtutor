from datetime import datetime

import pytz
import streamlit as st

from modules.lambda_operations import LambdaAPI

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
    # to make the document name unique
    current_time = datetime.now(jst)
    formatted_time = current_time.strftime("%Y%m%d%H%M%S")

    # make lambda generate document
    st.session_state.topic = topic
    lambda_api = LambdaAPI()
    lambda_api.invoke(topic=st.session_state.topic, time_send=formatted_time)

    st.info(f"""
    ドキュメントの作成を開始しました。\n
    作成には数分かかります。\n

    生成が完了したら、サイドバーの「ドキュメントを読み込む」から、下記の名前でドキュメントを読み込むことができますので確認してみましょう。\n

    ドキュメント名: {st.session_state.topic}_{formatted_time} \n

    【注】
    ドキュメントの生成が終わる前に新たなドキュメント作成のリクエストを送信すると、正常にドキュメントが作成されません。ご注意ください。
    """)
