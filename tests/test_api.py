from fastapi.testclient import TestClient
from app.api.main import app
from app.rag.furiosa_client import FuriosaClient


def test_health():
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["documents"] >= 10


def test_query_returns_official_evidence():
    response = TestClient(app).post("/api/v1/query", json={"question": "selective etch for GAA", "top_k": 3})
    assert response.status_code == 200
    body = response.json()
    assert body["insufficient_evidence"] is False
    assert body["evidence"]
    assert all(item["source_url"].startswith("https://") for item in body["evidence"])


def test_furiosa_response_removes_thinking_tags():
    cleaned = FuriosaClient._clean_response("<think>internal reasoning</think>\n최종 답변")
    assert cleaned == "최종 답변"
