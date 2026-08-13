from app.retrieval.hybrid_retriever import HybridRetriever


def test_hybrid_retrieval_returns_evidence():
    docs = [{"chunk_id": "1", "text": "plasma etch CD control", "title": "doc", "page_number": 1, "source_url": "https://example.com"}]
    result = HybridRetriever(docs).search("plasma etch", 1)
    assert len(result) == 1
    assert result[0]["chunk_id"] == "1"
    assert "hybrid_score" in result[0]
