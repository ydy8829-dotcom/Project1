def generate_answer(question: str, evidence: list[dict]) -> dict:
    if not evidence or evidence[0].get("score", 0) <= 0:
        return {"answer": "수집된 공식 문서에서 질문과 직접 연결되는 근거를 찾지 못했습니다.", "intent": "unknown", "entities": [], "evidence": [], "confidence": 0.0, "insufficient_evidence": True}
    bullets = []
    citations = []
    for item in evidence[:3]:
        text = item.get("text", "").strip().replace("\n", " ")
        bullets.append(f"- {item.get('title', '문서')}: {text[:360]}")
        citations.append({"title": item.get("title", ""), "page_number": item.get("page_number"), "source_url": item.get("source_url", ""), "quote": text[:240]})
    return {"answer": "질문과 관련된 공식 문서 근거입니다.\n\n" + "\n".join(bullets), "intent": "technical_lookup", "entities": [], "evidence": citations, "confidence": round(min(0.95, 0.45 + evidence[0].get("score", 0.0) * 0.5), 3), "insufficient_evidence": False}
