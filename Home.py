import pytz
from datetime import datetime

import streamlit as st

from modules.cloud_storage_operations import CloudStorageAPI
from modules.prompt_controller import convert_to_dict, create_table_of_contents, stream_chapter
from modules.utils import get_n_chapter_to_generate

st.set_page_config(
    page_title="Custom Tutor",
    page_icon=":robot_face:",
    layout="wide",
)
jst = pytz.timezone("Asia/Tokyo")

# initialize session_state if not already
if "generated" not in st.session_state:
    st.session_state.generated = False

if "dict_table_of_contents" not in st.session_state:
    st.session_state.dict_table_of_contents = None

if "str_table_of_contents" not in st.session_state:
    st.session_state.str_table_of_contents = None

if "topic" not in st.session_state:
    st.session_state.topic = None

if "document" not in st.session_state:
    st.session_state.document = ""

if "dict_document_chapter" not in st.session_state:
    st.session_state.dict_document_chapter = dict()


# title
st.title("テック学習のための教材生成")

# input form
topic = st.text_input("トピック (例: Python入門): ")

# 注釈
with st.expander("使い方"):
    st.markdown(
        """
        - トピックには、任意のキーワードを入れることができますが、主にプログラミング等のIT技術学習のための教材を生成することを想定しています。
        - 「ドキュメントの作成を始める」を押すと、ドキュメントの目次が作成されます。
        - 目次が作成されたら、「次のチャプターを作成する」を押すと、目次の中でまだ作成されていない最初のチャプターのドキュメントが生成されます。
        - ※ ブラウザの画面を更新するとそれまで作成したドキュメントが初期化されます。
        - ※ チャプターの作成中に再度「次のチャプターを作成する」を押すと、該当のチャプターが最初から作成され直されてしまいます。
        - ※ チャプター生成中に、`Bad message format`エラーやOpenAIのAPIエラーが出ることがありますが、再び「次のチャプターを作成する」ボタンを押してドキュメントの作成を再開できます。
        - ※ 生成されたドキュメントの内容が正しいとは限らないことに注意してください。
        """
    )
    
# ボタンが押されたら、目次を作成する
if st.button("ドキュメントの作成を始める"):
    with st.spinner("構成を考えています..."):
        # jsonに変換できる形式で出力が得られない場合があるので、10回までリトライする
        is_success = False
        n_stop = 0
        while not is_success and n_stop < 10:
            table_of_contents = create_table_of_contents(topic)
            try:
                st.session_state.dict_table_of_contents = convert_to_dict(table_of_contents)
                is_success = True
            except:
                n_stop += 1
        if not is_success:
            st.error("目次の作成に失敗しました。やり直してください。")
        else:
            # セッション情報としてのtopicを固定する
            st.session_state.topic = topic
            # 目次の作成を新たに行う際、generatedをTrueからFalseに戻す。これにより、前回の目次で作成したドキュメントを消去する
            st.session_state.generated = False
            # 目次の作成を新たに行う際はドキュメントを初期化しておく
            st.session_state.dict_document_chapter = dict()
            st.session_state.document = ""
            st.session_state.document += f"# {st.session_state.topic}\n"
            st.session_state.str_table_of_contents = ""
            for n_chapter, chapter in st.session_state.dict_table_of_contents.items():
                st.session_state.str_table_of_contents += f"{n_chapter}. {chapter}\n"
            st.session_state.document += st.session_state.str_table_of_contents


# 目次が作成されていて、かつ、全体のドキュメント生成が終わっていない場合にドキュメントを生成する
if st.session_state.dict_table_of_contents is not None and st.session_state.generated is False:
    # ドキュメントセクションの冒頭：タイトル、目次を表示する
    st.markdown("---")
    st.title(st.session_state.topic)
    st.markdown(st.session_state.str_table_of_contents)

    # 各時点でそこまでに作成したドキュメント全体の表示場所
    chapters_so_far_placeholder = st.empty()
    # 各時点で生成中のドキュメントの逐次表示場所
    chapter_at_the_moment_placeholder = st.empty()

    # それまでに作成しているドキュメント（各項目単位）を表示する
    with chapters_so_far_placeholder.container():
        if len(st.session_state.dict_document_chapter) > 0:
            for _, document_chapter in st.session_state.dict_document_chapter.items():
                st.markdown(document_chapter)

    if st.button("次のチャプターを作成する"):
        # 目次の項目ごとに、ドキュメントを生成し、逐次表示したい
        # 作成すべきチャプター番号を得る
        n_chapter_to_generate = get_n_chapter_to_generate(
            st.session_state.dict_document_chapter,
            st.session_state.dict_table_of_contents,
        )

        # すべてのチャプター作成が終わっていたらこのwhile処理を終わらせる
        if n_chapter_to_generate is None:
            # 全体の作成が終わったら、この分岐でドキュメントを生成するのをやめ、後続の全体表示でドキュメントを表示させる
            st.session_state.generated = True
            st.info("全チャプターの作成が完了しました")
            st.experimental_rerun()
        # まだ作成していないチャプターがある場合、streamで作成し、それをempty箇所に表示する
        else:
            # stream表示
            res_stream = stream_chapter(
                st.session_state.topic,
                st.session_state.dict_table_of_contents,
                n_chapter_to_generate,
            )
            collected_messages = []
            for chunk in res_stream:
                chunk_message = chunk.choices[0].delta.content  # extract the message
                if chunk_message is None:
                    continue
                collected_messages.append(chunk_message)  # save the message
                with chapter_at_the_moment_placeholder.container():
                    document_so_far = "".join(collected_messages)
                    st.markdown(document_so_far)
            # そのチャプターの生成が終わったら、全体ドキュメントとチャプタードキュメントを更新する
            st.session_state.document += f"{document_so_far}\n"
            st.session_state.dict_document_chapter[n_chapter_to_generate] = f"{document_so_far}\n"

            # 全チャプターの作成が終わっていたら、状態を更新する
            if len(st.session_state.dict_document_chapter) == len(st.session_state.dict_table_of_contents):
                st.session_state.generated = True
                st.info("全チャプターの作成が完了しました")
                st.experimental_rerun()
            
# 全体のドキュメント作成が終わっていたら、それを表示する
elif st.session_state.generated is True:
    st.markdown(st.session_state.document)

    # 評価とともにクラウドストレージに登録できるようにする
    st.markdown("---")
    rating = st.slider("ドキュメントを評価する(1~5)", min_value=0.0, max_value=5.0, value=0.0, step=1.0)
    if st.button("ドキュメントをクラウドストレージに登録してシェアする"):
        if rating < 1:
            st.warning("1から5の間で評価してください。")
        else:
            # to make the dir name unique
            current_time = datetime.now(jst)
            formatted_time = current_time.strftime("%Y%m%d%H%M%S")
            dir_name = f"{st.session_state.topic}_{formatted_time}"

            # data to export
            data_to_export = {
                "document": st.session_state.document,
                "topic": st.session_state.topic,
            }
            
            # export to cloud storage
            cloud_storage_api = CloudStorageAPI()
            cloud_storage_api.set_resource()
            cloud_storage_api.write_pkl_to_s3(data_to_export, f"{dir_name}/document.pkl")
            cloud_storage_api.write_pkl_to_s3([rating], f"{dir_name}/rating.pkl")
            st.info("クラウドストレージに登録しました！")
