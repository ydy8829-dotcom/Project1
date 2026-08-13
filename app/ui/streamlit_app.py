import streamlit as st
from app.api.main import retriever, terms
from app.normalization.query_normalizer import normalize_query
from app.rag.answer_generator import generate_answer

st.set_page_config(page_title="Semiconductor RAG Copilot", layout="wide")
st.title("Semiconductor Equipment RAG Copilot")
st.caption("Applied Materials · Lam Research 공식 공개 자료 기반 MVP")
question = st.text_input("질문", placeholder="예: Lam Research의 selective etch는 GAA에 어떻게 적용되나요?")
top_k = st.slider("검색 문서 수", 1, 10, 5)
if st.button("검색") and question:
    normalized = normalize_query(question, terms)
    results = retriever.search(normalized["normalized"], top_k)
    result = generate_answer(question, results)
    st.subheader("답변")
    st.markdown(result["answer"])
    st.metric("신뢰도", f"{result['confidence']:.0%}")
    st.subheader("근거 문서")
    for evidence in result["evidence"]:
        st.markdown(f"**{evidence['title']}**")
        st.caption(evidence["quote"])
        if evidence["source_url"]:
            st.link_button("공식 출처 열기", evidence["source_url"])
    with st.expander("검색 상세"):
        st.json(results)
