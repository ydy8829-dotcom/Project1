import os
import re
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

    @staticmethod
    def _clean_response(text: str) -> str:
        """Remove reasoning markers before exposing the answer in the UI/API."""
        cleaned = re.sub(r"<think>.*?</think>", "", text or "", flags=re.IGNORECASE | re.DOTALL)
        cleaned = re.sub(r"</?think>", "", cleaned, flags=re.IGNORECASE)
        return cleaned.strip()

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
                {"role": "system", "content": "You are a semiconductor equipment technical RAG assistant. Use only the supplied official document evidence. State as facts only claims directly supported by the evidence. If the evidence says only that a process is an application, do not infer an unstated purpose, sequence, mechanism, electrode/gate formation step, performance benefit, or material relationship. Put any unavoidable interpretation under a clearly labeled 'Interpretation' sentence and say it is an inference. Do not invent specifications or numbers. If the evidence is insufficient, say so. Always cite the relevant source URL. LANGUAGE RULE: If the user question contains Korean, write the entire answer in Korean, including headings and the source sentence. Never answer a Korean question in English. Do not output hidden reasoning or <think> tags."},
                {"role": "user", "content": f"Document evidence:\n{context}\n\nQuestion:\n{question} /no_think"},
            ],
        }
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(f"{self.base_url}/chat/completions", json=payload)
            response.raise_for_status()
            body = response.json()
        choice = (body.get("choices") or [{}])[0]
        message = choice.get("message") or {}
        content = self._clean_response(message.get("content", ""))
        if not content:
            raise RuntimeError(f"Furiosa returned no content (finish_reason={choice.get('finish_reason')})")
        return {"text": content, "model": body.get("model", self.model), "usage": body.get("usage", {}), "finish_reason": choice.get("finish_reason")}
