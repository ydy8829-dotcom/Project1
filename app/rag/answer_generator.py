import re
from typing import Any


def evidence_view(evidence: list[dict]) -> tuple[list[str], list[dict[str, Any]]]:
    bullets = []
    citations = []
    for item in evidence[:3]:
        text = item.get("text", "").strip().replace("\n", " ")
        bullets.append(f"- {item.get('title', 'Official document')}: {text[:360]}")
        citation = {"title": item.get("title", ""), "page_number": item.get("page_number"), "source_url": item.get("source_url", ""), "quote": text[:240]}
        for key in ("retriever", "rerank_score", "hybrid_score", "bm25_score", "vector_score"):
            if key in item:
                citation[key] = item[key]
        citations.append(citation)
    return bullets, citations


def generate_answer(question: str, evidence: list[dict], llm: Any = None) -> dict:
    if not evidence or evidence[0].get("score", 0) <= 0:
        return {"answer": "수집된 공식 문서에서 질문과 직접 연결되는 근거를 찾지 못했습니다.", "intent": "unknown", "entities": [], "evidence": [], "confidence": 0.0, "insufficient_evidence": True, "llm": {"provider": "none"}}
    bullets, citations = evidence_view(evidence)
    result = {"answer": "질문과 관련된 공식 문서 근거입니다.\n\n" + "\n".join(bullets), "intent": "technical_lookup", "entities": [], "evidence": citations, "confidence": round(min(0.95, 0.45 + evidence[0].get("score", 0.0) * 0.5), 3), "insufficient_evidence": False, "llm": {"provider": "fallback"}}
    if llm and llm.enabled:
        try:
            generated = llm.chat(question, evidence)
            result["answer"] = generated["text"]
            result["llm"] = {"provider": "furiosa", **{k: generated[k] for k in ("model", "usage", "finish_reason")}}
            # Align the machine-readable flag with an explicit abstention in the answer.
            # Retrieval can return related documents even when they do not contain the
            # requested specification or numeric value.
            abstention_markers = (
                r"제공되지 않았",
                r"확인할 수 없",
                r"찾을 수 없",
                r"not provided",
                r"not available",
                r"cannot be found",
            )
            if any(re.search(marker, generated["text"], re.IGNORECASE) for marker in abstention_markers):
                result["insufficient_evidence"] = True
                result["confidence"] = min(result["confidence"], 0.35)
        except Exception as exc:
            result["llm"] = {"provider": "fallback", "error": str(exc)}
    return result
