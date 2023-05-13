from datetime import datetime

import pytz
import streamlit as st

# from modules.lambda_operations import LambdaAPI
from modules.prompt_controller import BulkGenerator

# setting of page
st.set_page_config(
    page_title="Custom Tutor",
    page_icon=":robot_face:",
    layout="wide",
)
jst = pytz.timezone("Asia/Tokyo")

st.title("Custom Tutor")
str_markdown = """
- 学びたいトピックを入力すると、AIが学習用のドキュメントを生成します。
"""
st.markdown(str_markdown)


# Initialize session_state if not already
if "topic" not in st.session_state:
    st.session_state.topic = None

if "generated" not in st.session_state:
    st.session_state.generated = None

if "generator" not in st.session_state:
    st.session_state.generator = None

# create cols
col1, col2 = st.columns(2)

# input form
topic = col1.text_area("学びたいトピック")

# generate documents
# if st.button("ドキュメントを生成する"):
#     # to make the document name unique
#     current_time = datetime.now(jst)
#     formatted_time = current_time.strftime("%Y%m%d%H%M%S")

#     # make lambda generate document
#     st.session_state.topic = topic
#     lambda_api = LambdaAPI()
#     lambda_api.invoke(topic=st.session_state.topic, time_send=formatted_time)

#     st.info(f"""
#     ドキュメントの作成を開始しました（完了まで数分かかります）。\n

#     作成が完了すると、サイドバーの「ドキュメントを読み込む」から、下記の名前でドキュメントを読み込むことができますので確認してみましょう。\n

#     ドキュメント名: {st.session_state.topic}_{formatted_time} \n

#     作成されたドキュメントの品質は高い場合もあれば、低い場合もあります。今後の改善のため、また、有用なドキュメントを見つけやすくするため、ドキュメントの品質を評価いただけると幸いです。\n
    
#     【注】
#     ドキュメントの生成が終わる前に新たなドキュメント作成のリクエストを送信すると、正常にドキュメントが作成されません。
#     """)

# generate documents locally
if col1.button("ドキュメントを新規にローカルで生成する"):
    # to make the document name unique
    current_time = datetime.now(jst)
    formatted_time = current_time.strftime("%Y%m%d%H%M%S")

    # make lambda generate document
    st.session_state.topic = topic
    st.session_state.generator = BulkGenerator(topic=st.session_state.topic)
    with st.spinner("ドキュメントを生成しています..."):
        st.session_state.generator.generate_document()
    st.session_state.generated = True

# adjust content of document
if st.session_state.generated is True:
    adjusting_point = col2.text_area("ドキュメントの調整")

    # adjust content of document
    if col2.button("ドキュメント内容を調整する"):
        with st.spinner("ドキュメントを調整しています..."):
            st.session_state.generator.adjust_document(adjusting_point)

# show document
if st.session_state.generated is True:
    st.markdown(st.session_state.generator.document)
