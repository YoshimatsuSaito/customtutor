import streamlit as st

st.title("Custom Tutor")

str_markdown = """
- 学びたいトピックと学びたいステップ数を入力すると、AIが学習用のドキュメントを生成します。
- 生成されたドキュメントに対して疑問があれば、AIが答えてくれます。
- 生成したドキュメントはクラウドストレージに登録でき、ユーザ間でシェアできます。

早速サイドバーから機能を選択してみましょう！
"""
st.markdown(str_markdown)
