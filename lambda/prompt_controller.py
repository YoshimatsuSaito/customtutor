import ast
import os

import openai

openai.api_key = os.environ.get("OPENAI_API_KEY")


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
        - マークダウン形式であること（ドキュメント内へのアンカーリンクは作成しないでください）
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
