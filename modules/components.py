import streamlit as st


def set_export_section(document: str, topic: str, num_steps:int, dict_step: dict[str, str]):
    """生成したドキュメントのエクスポートセクションを設定する"""
    # download document and pickle data
    with col_rating:
        rating = st.slider("Rating this document", 0.0, 5.0, 2.5, 0.5)
        if st.button("Submit Rating"):
            st.info(f"rating: {rating}")
