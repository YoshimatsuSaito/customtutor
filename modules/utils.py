def make_document(dict_step: dict[str, str]) -> str:
    """chatリストからmarkdownドキュメントを生成する"""
    document = ""
    for step in dict_step.keys():
        document += dict_step[step] + "\n\n"
    return document


def get_n_chapter_to_generate(
    dict_document_chapter: dict[int, str],
    dict_table_of_contents: dict[int, str],
) -> int:
    """作成すべきチャプター番号を得る"""
    # まだ何も作っていなければ最初のチャプター
    if len(dict_document_chapter) == 0:
        return 1
    # 既に全てのチャプターを作成していればNone
    if len(dict_document_chapter) == len(dict_table_of_contents):
        return None
    # それ以外は、作成済みのチャプターの最大値+1
    return max(list(dict_document_chapter.keys())) + 1