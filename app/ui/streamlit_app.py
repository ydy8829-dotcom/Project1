from __future__ import annotations

import os
from datetime import datetime

import httpx
import streamlit as st


DEFAULT_API = os.getenv("RAG_API_URL", "http://127.0.0.1:8002")

st.set_page_config(page_title="Semiconductor Equipment RAG Copilot", page_icon="⚙️", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.hero { padding: 1.2rem 1.4rem; border-radius: 14px; background: linear-gradient(110deg,#0b1f35,#123f5c); color: white; margin-bottom: 1rem; }
.hero h1 { margin: 0; font-size: 2rem; }
.hero p { margin: .35rem 0 0; color: #c8d9e8; }
.source-card { border: 1px solid #d9e2ec; border-radius: 10px; padding: .8rem 1rem; margin: .5rem 0; background: #fbfdff; }
.muted { color: #627386; font-size: .88rem; }
</style>
""", unsafe_allow_html=True)

if "history" not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    st.header("검색 설정")
    api_url = st.text_input("RAG API 주소", DEFAULT_API).rstrip("/")
    top_k = st.slider("검색 문서 수", 1, 10, 5)
    st.divider()
    st.caption("반도체 공정장비 기술문서 기반 Copilot")
    if st.button("연결 상태 새로고침", use_container_width=True):
        st.rerun()
    st.subheader("예시 질문")
    examples = [
        "Lam Research의 selective etch는 GAA에 어떻게 적용되는가?",
        "GAA 공정에서 SiGe removal이 언급된 문서는 무엇인가?",
        "Lam Research 장비의 정확한 식각 속도와 처리량은 얼마인가?",
    ]
    selected_example = st.radio("질문 선택", examples, label_visibility="collapsed")

try:
    health = httpx.get(f"{api_url}/health", timeout=5).json()
    api_ok = health.get("status") == "ok"
except Exception as exc:
    health = {"status": "error", "detail": str(exc)}
    api_ok = False

st.markdown('<div class="hero"><h1>Semiconductor Equipment Technical RAG Copilot</h1><p>공정·장비·제품 문서를 검색하고, 공식 근거와 함께 기술 답변을 확인합니다.</p></div>', unsafe_allow_html=True)

status_cols = st.columns(4)
status_cols[0].metric("API 상태", "정상" if api_ok else "연결 실패")
status_cols[1].metric("문서 수", health.get("documents", "-"))
status_cols[2].metric("생성 모델", "연결" if health.get("furiosa_configured") else "미연결")
status_cols[3].metric("검색 보강", "Embedding" if health.get("embedding_configured") else ("Reranker" if health.get("reranker_configured") else "기본"))

st.subheader("기술 질의")
question = st.text_area("질문", value=selected_example, height=90, placeholder="예: GAA에서 selective etch가 어떤 공정에 사용되는가?")
submit = st.button("문서 근거로 답변 생성", type="primary", use_container_width=True)

if submit:
    if not question.strip():
        st.warning("질문을 입력하세요.")
    elif not api_ok:
        st.error("RAG API에 연결할 수 없습니다. FastAPI 실행 상태와 주소를 확인하세요.")
    else:
        with st.spinner("문서 검색 및 답변 생성 중..."):
            try:
                response = httpx.post(f"{api_url}/api/v1/query", json={"question": question, "top_k": top_k}, timeout=120)
                response.raise_for_status()
                result = response.json()
                st.session_state.history.insert(0, {"time": datetime.now().strftime("%H:%M:%S"), "question": question, "result": result})
            except Exception as exc:
                st.error(f"질의 처리 실패: {exc}")

if st.session_state.history:
    current = st.session_state.history[0]
    result = current["result"]
    st.divider()
    left, right = st.columns([2.1, 1])
    with left:
        st.subheader("답변")
        if result.get("insufficient_evidence"):
            st.warning("문서 근거가 충분하지 않습니다. 사양 수치나 장비 조건은 원문 매뉴얼을 추가 확인하세요.")
        st.markdown(result.get("answer", "답변이 없습니다."))
        st.caption(f"질의 시각: {current['time']}")
    with right:
        st.subheader("판정 정보")
        st.metric("신뢰도", f"{result.get('confidence', 0):.0%}")
        llm = result.get("llm", {})
        retrieval = result.get("retrieval", {})
        st.write("답변 모델", llm.get("model") or llm.get("provider", "미상"))
        st.write("검색 방식", retrieval.get("method", "미상"))
        st.write("근거 충분성", "부족" if result.get("insufficient_evidence") else "충분")
    st.subheader("근거 문서")
    for index, evidence in enumerate(result.get("evidence", []), 1):
        with st.container(border=True):
            title = evidence.get("title", "문서")
            st.markdown(f"**{index}. {title}**")
            st.caption(evidence.get("source_url", "출처 없음"))
            st.write(evidence.get("quote", ""))
            meta = {key: evidence[key] for key in ("retriever", "rerank_score", "hybrid_score") if key in evidence}
            if meta:
                st.json(meta, expanded=False)
    with st.expander("검색·LLM 원본 응답"):
        st.json(result, expanded=False)

with st.expander("서비스 상태 상세"):
    st.json(health, expanded=False)

if len(st.session_state.history) > 1:
    with st.expander(f"최근 질의 기록 ({len(st.session_state.history)-1}건)"):
        for item in st.session_state.history[1:6]:
            st.write(f"{item['time']} — {item['question']}")
