import ast
import os
from typing import Union

import openai
import streamlit as st
# from dotenv import load_dotenv

# load .env file
# load_dotenv(".env")
openai.api_key = st.secrets["OPENAI_API_KEY"]


class SequentialGenerator:
    """与えられたトピックとステップ数から、ドキュメント全体を逐次的に生成する
    TODO: max_tokens制限を強制的に解決しているので、langchainなどの使用でより効率的にする"""
    def __init__(
        self,
        topic: str,
        num_steps: int, 
        model_name: str="gpt-4",
        max_tokens: int=8192,
    ) -> None:
        self.topic = topic
        self.num_steps = num_steps
        self.model_name = model_name
        # 全ステップのドキュメントを生成してもmax_tokensを超えないように各ステップのmax_tokensを制限する
        self.max_tokens_of_each_response = int(max_tokens / (self.num_steps + 1))
        # chatリストを格納する
        self.list_message: list[dict[str, str]] = []
        # 各ステップのドキュメント部分のみを格納する
        self.dict_step: dict[str, str] = dict()
        # ドキュメント全体を結合したmarkdownを格納する
        self.document: str = ""
        # システムメッセージの設定
        self.set_system_message()
    
    def set_system_message(self) -> None:
        """ドキュメント生成についての設定をシステムメッセージに与える
        ひとまず言語設定はしないことにする. 以下のようなメッセージである程度制御できるが不安定. やるなら明示的に言語を指定する.
        You must output as same language as input (ex. If input is Japanese, output must be Japanese).
        """
        system_message = f"""
        You are an excellent tutor.
        You generate documents to learn "{self.topic}" by {self.num_steps} step.
        You must return each step if user input "Generate step : 'step number'".
        You must not generate multiple steps at once.
        Output of each step must be markdown format.
        Each step format is as follows.
        
        # Step 'insert step number': 'insert step title'
        
        'insert content'

        """
        self.list_message.append(
            {
                "role": "system", "content": system_message
            }
        )

    def generate_step(self, step: int):
        """ステップ番号を受け取り、そのステップのドキュメントを生成した上でchatリストに加える
        各ステップの生成が終わるごとに外部で表記をしたいので、全体の一括生成は行わない
        """
        self.list_message.append(
            {
                "role": "user", "content": f"Generate step: {step}"
            }
        )
        res = openai.ChatCompletion.create(
            model=self.model_name,
            messages=self.list_message,
            max_tokens=self.max_tokens_of_each_response,
        )
        assistant_message = res["choices"][0]["message"]["content"]
        self.list_message.append(
            {
                "role": "assistant", "content": assistant_message
            }
        )
    
    def make_dict_step(self):
        """chatリストからステップごとのドキュメントを抽出する"""
        for message in self.list_message:
            if message["role"] == "assistant":
                content = message["content"]
                step = content.split("# Step ")[1].split(":")[0]
                self.dict_step[step] = content

class IndependentGenerator:
    """与えられたステップとステップ数から、ドキュメントの目次を生成し、その目次を所与として、与えられたステップ番号のドキュメントを作成する"""
    def __init__(
        self,
        topic: str,
        model_name: str="gpt-3.5-turbo",
        max_tokens: int=4096,
    ) -> None:
        self.topic = topic
        self.model_name = model_name
        # そのステップのドキュメントを生成してもmax_tokensを超えないようにmax_tokensを適当に調整する
        self.max_tokens = int(max_tokens / 2.5)
        self.dict_table_of_contents = None
        self.dict_document = dict()
        self.set_table_of_contents()

    def set_table_of_contents(self) -> None:
        """ドキュメントの目次を生成する。これは繰り返し使用する"""
        user_message = f"""
            「{self.topic}」というタイトルで教材を作りたい。
            教材を作るにあたり、ユーザが段階的に技能を身に着けられるよう、テーマを分解したい。
            適切なサブトピック、つまり、教材の目次、を作成せよ。

            出力の形式は以下のjson形式とする。

            {{
                {{1}}:{{サブトピック名}},
                {{2}}:{{サブトピック名}},
                ...
            }}
        """
        is_success = False
        n_stop = 0
        while not is_success and n_stop < 10:
            res = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[{"role": "user", "content": user_message}],
                max_tokens=self.max_tokens,
            )
            table_of_contents = res["choices"][0]["message"]["content"]
            try:
                self.dict_table_of_contents = ast.literal_eval(table_of_contents)
                is_success = True
            except:
                n_stop += 1
        
        if not is_success:
            raise Exception("Failed to generate table of contents.")

    def generate_a_document(self, key: Union[str, int]) -> None:
        """生成した目次のkeyを与え、そのkeyのドキュメントを生成する"""

        user_message = f"""
            「{self.topic}」というタイトルで教材を作成している。
            
            教材の目次は、以下である。
            {self.dict_table_of_contents}
            このうち、あなたは、「{self.dict_table_of_contents[key]}」の部分を作成する担当となった。

            以下の要件を満たしたドキュメントを生成せよ。
            - マークダウン形式であること
            - 「{self.dict_table_of_contents[key]}」に関するスキルや知識を習得するために必要な情報を網羅したものであること
            - ユーザが実際に試すことのできる実践的な内容が含まれていること
            - 他の教材を参照することなく、そのドキュメントだけで学習可能であること
            - 他の目次の項目に関わる部分は極力含めないこと
        """
        res = openai.ChatCompletion.create(
            model=self.model_name,
            messages=[{"role": "user", "content": user_message}],
            max_tokens=self.max_tokens,
        )
        document = res["choices"][0]["message"]["content"]
        self.dict_document[key] = document


class StepQuestionAnsweringGenerator:
    """与えられた文章を元にした回答を行う
    chat形式にすると複雑化するので、一旦は毎度一問一答形式で答える"""
    def __init__(self, topic: str, dict_step: dict[str, str], model_name="gpt-3.5-turbo", max_tokens=4096) -> None:
        self.topic = topic
        self.dict_step = dict_step
        self.model_name = model_name
        # 文字数制限対策のために雑に調整
        self.max_tokens_of_each_response = int(max_tokens / 3)
    
    def generate_answer(self, step: str, question: str) -> str:
        """質問に対する回答を生成する"""
        user_message = f"""
        You are an excellent tutor.
        You must generate helpful answer to the question below.
        {question}

        The answer must be based on the document below.
        {self.dict_step[step]}

        You must consider that the document is a part of the document to learn {self.topic}.

        If question is not directly related to the document and topic, you must mention about that and return the answer of the question based on your general knowledge.
        
        Your answer must be simple and short without compromising the intent of the question and without reducing the information in the answer.
        """

        list_message = [
            {
                "role": "user", "content": user_message
            },
        ]
        res = openai.ChatCompletion.create(
            model=self.model_name,
            messages=list_message,
            max_tokens=self.max_tokens_of_each_response,
        )
        assistant_message = res["choices"][0]["message"]["content"]
        return assistant_message


class BulkGenerator:
    """与えられたトピックとステップ数から、ドキュメント全体を一括で生成する"""
    def __init__(
        self,
        topic: str,
        model_name: str="gpt-4",
        max_tokens: int=8192,
    ) -> None:
        self.topic = topic
        self.model_name = model_name
        # 雑な文字数制限対策
        self.max_tokens = int(max_tokens / 2)
        # chatリストを格納する
        self.list_message: list[dict[str, str]] = []
        # システムメッセージの設定
        self.set_system_message()
        self.document = None
    
    def set_system_message(self) -> None:
        """ドキュメント生成についての設定をシステムメッセージに与える
        TODO: 本来はシステムメッセージをクラスの中でハードコーディングしないほうがいいと思われる"""
        system_message = f"""
        「{self.topic}」というタイトルで教材を生成してください。
        教材は以下の要件を満たすものとします。
        - マークダウン形式であること
        - 教材は適切な項目ごとに分割されていること（必要に応じて、ステップで区切ってください）
        - 各段階を学習することでトピックに関するスキルや知識を段階的に高められること
        - トピックに関するスキルや知識を習得するために必要な情報を網羅したものであること
        - ユーザが実際に試すことのできる実践的な内容が含まれていること
        - 完結していること（他の教材を参照することなく、単体で学習できること）
        """
        self.list_message.append(
            {
                "role": "system", "content": system_message
            }
        )

    def generate_document(self):
        """ドキュメントを一括で生成する"""
        self.list_message.append(
            {
                "role": "user", "content": "Generate document"
            }
        )
        res = openai.ChatCompletion.create(
            model=self.model_name,
            messages=self.list_message,
            max_tokens=self.max_tokens,
        )
        assistant_message = res["choices"][0]["message"]["content"]
        self.list_message.append(
            {
                "role": "assistant", "content": assistant_message
            }
        )
        self.document = assistant_message


class QuestionAnsweringGenerator:
    """与えられた文章を元にした回答を行う
    chat形式にすると複雑化するので、一旦は毎度一問一答形式で答える"""
    def __init__(self, topic: str, document: str, model_name="gpt-4", max_tokens=8192) -> None:
        self.topic = topic
        self.document = document
        self.model_name = model_name
        # 雑な文字数制限対策
        self.max_tokens = int(max_tokens / 3)
    
    def generate_answer(self, question: str) -> str:
        """質問に対する回答を生成する"""
        user_message = f"""
        下記の質問にわかりやすく答えてください。
        「{question}」

        回答の際には下記のドキュメント内容を踏まえてください。
        「{self.document}」

        もし質問がドキュメントに直接関連がない場合は、その旨を指摘したうえで、一般的な知識に基づいて回答してください。
        """

        list_message = [
            {
                "role": "user", "content": user_message
            },
        ]
        res = openai.ChatCompletion.create(
            model=self.model_name,
            messages=list_message,
            max_tokens=self.max_tokens,
        )
        assistant_message = res["choices"][0]["message"]["content"]
        return assistant_message
    

def create_table_of_contents(topic: str, model_name: str="gpt-3.5-turbo", max_tokens: int=2048) -> str:
    """目次を生成する"""
    user_message = f"""
        「{topic}」というタイトルで教材を作りたい。
        ユーザが段階的に技能を身に着けられるよう、テーマを分解し、適切なサブトピック、つまり、教材の目次、を作成せよ。
        「{topic}」を学ぶにあたって、最低限度必要だと考えられるサブトピックのみを作成せよ。

        出力の形式は以下のjson形式とする。

        {{
            {{1}}:{{サブトピック名}},
            {{2}}:{{サブトピック名}},
            ...
        }}
    """
    res = openai.ChatCompletion.create(
        model=model_name,
        messages=[{"role": "user", "content": user_message}],
        max_tokens=max_tokens,
    )
    table_of_contents = res["choices"][0]["message"]["content"]
    return table_of_contents


def convert_to_dict(table_of_contents: str) -> dict[int, str]:
    """目次をstringから所定の形式のdictに変換する"""
    _dict = ast.literal_eval(table_of_contents)
    dict_table_of_contents = {int(k): v for k, v in _dict.items()}
    return dict_table_of_contents


def stream_chapter(
    topic: str, 
    dict_table_of_contents: dict[int, str], 
    chapter: int, 
    model_name: str="gpt-3.5-turbo", 
    max_tokens: int=3072,
) -> str:
    """生成した目次のkeyを与え、そのkeyのドキュメントを生成する"""

    user_message = f"""
        「{topic}」というタイトルで教材を作成している。
        
        教材の目次は、以下である。
        {dict_table_of_contents}
        このうち、あなたは、「{dict_table_of_contents[chapter]}」の部分を作成する担当となった。
        担当部分に関して、読者がスキルや知識を習得できる素晴らしいドキュメントを作成せよ。

        以下の要件を満たしたドキュメントを生成せよ。
        - マークダウン形式であること
        - コードサンプルのような、ユーザが実際に試すことのできる実践的な内容が含まれていること
        - 担当部分以外の項目に関わる説明をあなたの担当部分の中に含めないこと
        - # {chapter}. {dict_table_of_contents[chapter]} という見出しで始まること
    """
    res_stream = openai.ChatCompletion.create(
        model=model_name,
        messages=[{"role": "user", "content": user_message}],
        max_tokens=max_tokens,
        stream=True,
    )

    return res_stream