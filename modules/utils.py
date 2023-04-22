def make_document(dict_step: dict[str, str]) -> str:
    """chatリストからmarkdownドキュメントを生成する"""
    document = ""
    for step in dict_step.keys():
        document += dict_step[step] + "\n\n"
    return document
