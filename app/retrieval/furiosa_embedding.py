import os
from typing import Any

import httpx


class FuriosaEmbeddingClient:
    """Optional OpenAI-compatible embedding client with a small in-memory cache."""

    def __init__(self, base_url: str | None = None, model: str | None = None, timeout: float = 90.0):
        self.base_url = (base_url or os.getenv("FURIOSA_EMBED_BASE_URL", "")).rstrip("/")
        self.model = model or os.getenv("FURIOSA_EMBED_MODEL", "furiosa-ai/Qwen3-Embedding-0.6B")
        self.timeout = timeout
        self._document_vectors: dict[str, list[float]] = {}

    @property
    def enabled(self) -> bool:
        return bool(self.base_url)

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        payload = {"model": self.model, "input": texts}
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(f"{self.base_url}/embeddings", json=payload)
            response.raise_for_status()
            body = response.json()
        rows = sorted(body.get("data", []), key=lambda item: item.get("index", 0))
        return [row["embedding"] for row in rows]

    def document_vectors(self, documents: list[dict[str, Any]]) -> list[list[float]]:
        missing = [item for item in documents if item.get("chunk_id", item.get("title")) not in self._document_vectors]
        if missing:
            vectors = self.embed([item.get("text", "") for item in missing])
            for item, vector in zip(missing, vectors):
                self._document_vectors[item.get("chunk_id", item.get("title"))] = vector
        return [self._document_vectors[item.get("chunk_id", item.get("title"))] for item in documents]
