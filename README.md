# customtutor
try to make app that generates documents about anything you want to learn

# function to implement
- ユーザからのトピックとステップ数の入力を受け付け、学習用のドキュメントを出力する: DONE
    - 出力は各トピックごとに出力することとし、一つのトピックの出力が終わり次第、そのトピックを出力することとしたい: DONE
    - 文字数制限対策として下記の2モードを実装する: DONE
        - max_tokensによる強制調整: DONE
        - 目次を最初に作らせて、一つずつstepを作らせる: DONE（but非採用）
        - langchainによるより効率的な実装に変える: PENDING
- 出力された教材に対して、調整を加える（難易度や粒度についての調整を自然言語で加えることができる）
    - 出力された全教材を入力として与えて、調整言語によって調整させる（max_tokensによる強制調整の場合）
    - 各ステップごとに、調整を逐次与える(目次を最初に作らせてstepを作らせる場合)
- 各stepの内容について、質問しながら学習ができるようにする（画面の左右でdocumentと質問を展開できるようなイメージ）: DONE
    - 生成した教材を改めて与えて、それを所与とした質問に答える方式(max_tokensの調整が必要になる): DONE
- 出力された教材をmarkdownで保存することができる: DONE
- 後から保存されたmarkdownを登録し直すことでセッションを再開できるようにする: DONE
- ユーザが生成した教材で良かったものをS3に登録し、呼び出せるようにする: DONE