import ast
import os

import openai
from dotenv import load_dotenv

# load .env file
load_dotenv(".env")
openai.api_key = os.environ.get("OPENAI_API_KEY")


class SequentialGenerator:
    """与えられたトピックとステップ数から、ドキュメント全体を逐次的に生成する
    TODO: max_tokens制限を強制的に解決しているので、langchainなどの使用でより効率的にする"""
    def __init__(
        self,
        topic: str,
        num_steps: int, 
        model_name: str="gpt-3.5-turbo",
        max_tokens: int=4096,
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
    """与えられたステップとステップ数から、ドキュメントの目次を生成し、その目次を所与として、与えられたステップ番号のドキュメントを作成する
    各ドキュメントは、目次とステップ番号との関係でのみ生成される
    TODO: max_tokensによる制限を回避するための方法であるが、ステップ間の関係を構築することができないため、langchainなどによる効率的な実装が求められる
    """
    def __init__(
        self,
        topic: str,
        num_steps: int,
        model_name: str="gpt-3.5-turbo",
        max_tokens: int=4096,
    ) -> None:
        self.topic = topic
        self.num_steps = num_steps
        self.model_name = model_name
        # そのステップのドキュメントを生成してもmax_tokensを超えないようにmax_tokensを適当に調整する
        self.max_tokens_of_each_response = max_tokens - 500
        self.table_of_contents = None
        self.dict_generated_step = dict()
        self.set_table_of_contents()

    def set_table_of_contents(self) -> None:
        """ドキュメントの目次を生成する。これは繰り返し使用する"""
        user_message = f"""
        You are an excellent tutor.
        You generate documents to learn {self.topic} by {self.num_steps} step.
        You must return table of contents.
        Each step should not depend on the content of other steps.
        Output format must be python dict format as follows.
        Step 'insert step number': 'insert step title',...
        """
        list_message = [
            {
                "role": "user", "content": user_message
            }
        ]
        res = openai.ChatCompletion.create(
            model=self.model_name,
            messages=list_message,
            max_tokens=self.max_tokens_of_each_response,
        )
        assistant_message = res["choices"][0]["message"]["content"]
        self.str_table_of_contents = assistant_message
        self.dict_table_of_contents = ast.literal_eval(assistant_message)

    def generate_a_step(self, step_number: int) -> None:
        """生成した目次に従って、与えられたステップ番号のドキュメントを生成する。
        過去に一度生成した文章は再度生成できないようにする（内容が実行のたびに変わるのを防ぐため）
        """
        if step_number in self.dict_generated_step.keys():
            return
        user_message = f"""
        You are an excellent tutor.
        You generate documents to learn "{self.topic}".
        Table of contents of the documents is as follows.

        {self.table_of_contents}

        You must generate documents of step {step_number}.
        The content of the step must stand alone and be independent of the content of other steps.
        Output must be markdown format.
        Output format is as follows.
        
        # Step {step_number}: {self.dict_table_of_contents[f"Step {step_number}"]}
        
        'insert content'

        """
        list_message = [
            {
                "role": "user", "content": user_message
            }
        ]
        res = openai.ChatCompletion.create(
            model=self.model_name,
            messages=list_message,
            max_tokens=self.max_tokens_of_each_response,
        )
        assistant_message = res["choices"][0]["message"]["content"]
        self.dict_generated_step[step_number] = assistant_message


class QuestionAnsweringGenerator:
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
