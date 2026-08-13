import os
from typing import Any

import httpx


class FuriosaClient:
    """Small OpenAI-compatible client for a Furiosa-LLM server."""

    def __init__(self, base_url: str | None = None, model: str | None = None, timeout: float = 90.0):
        self.base_url = (base_url or os.getenv("FURIOSA_BASE_URL", "")).rstrip("/")
        self.model = model or os.getenv("FURIOSA_MODEL", "furiosa-ai/Qwen3-8B-FP8")
        self.timeout = timeout

    @property
    def enabled(self) -> bool:
        return bool(self.base_url)

    def chat(self, question: str, evidence: list[dict[str, Any]], max_tokens: int = 500) -> dict[str, Any]:
        if not self.enabled:
            raise RuntimeError("FURIOSA_BASE_URL is not configured")
        context = "\n\n".join(
            f"[{i}] {item.get('title', 'Official document')}\n{item.get('text', '')}\nSource: {item.get('source_url', '')}"
            for i, item in enumerate(evidence[:5], 1)
        )
        payload = {
            "model": self.model,
            "temperature": 0.1,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": "You are a semiconductor equipment technical RAG assistant. Use only the supplied official document evidence. Separate facts directly stated in the evidence from interpretation. Do not invent specifications or numbers. If the evidence is insufficient, say so. Always cite the relevant source URL."},
                {"role": "user", "content": f"Document evidence:\n{context}\n\nQuestion:\n{question} /no_think"},
            ],
        }
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(f"{self.base_url}/chat/completions", json=payload)
            response.raise_for_status()
            body = response.json()
        choice = (body.get("choices") or [{}])[0]
        message = choice.get("message") or {}
        content = message.get("content")
        if not content:
            raise RuntimeError(f"Furiosa returned no content (finish_reason={choice.get('finish_reason')})")
        return {"text": content, "model": body.get("model", self.model), "usage": body.get("usage", {}), "finish_reason": choice.get("finish_reason")}
