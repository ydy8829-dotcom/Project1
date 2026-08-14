import os
from typing import Any

import httpx


class FuriosaReranker:
    """Optional OpenAI-compatible Furiosa Qwen3 reranker client."""

    def __init__(self, base_url: str | None = None, model: str | None = None, timeout: float = 60.0):
        self.base_url = (base_url or os.getenv("FURIOSA_RERANK_BASE_URL", "")).rstrip("/")
        self.model = model or os.getenv("FURIOSA_RERANK_MODEL", "furiosa-ai/Qwen3-Reranker-4B")
        self.timeout = timeout

    @property
    def enabled(self) -> bool:
        return bool(self.base_url)

    def rerank(self, query: str, documents: list[dict[str, Any]], top_n: int) -> list[dict[str, Any]]:
        if not self.enabled or not documents:
            return documents[:top_n]
        payload = {
            "model": self.model,
            "query": query,
            "documents": [item.get("text", "") for item in documents],
            "top_n": min(top_n, len(documents)),
            "return_documents": False,
        }
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(f"{self.base_url}/rerank", json=payload)
            response.raise_for_status()
            body = response.json()
        ranked = body.get("results", body.get("data", []))
        output = []
        for item in ranked:
            index = item.get("index")
            if index is None or not 0 <= index < len(documents):
                continue
            row = dict(documents[index])
            row["rerank_score"] = item.get("relevance_score", item.get("score", 0.0))
            row["retriever"] = "furiosa-reranker"
            output.append(row)
        return output[:top_n] if output else documents[:top_n]
