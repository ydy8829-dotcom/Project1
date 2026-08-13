import re
from rank_bm25 import BM25Okapi

TOKEN_RE = re.compile(r"[A-Za-z0-9가-힣]+")


class BM25Retriever:
    def __init__(self, documents: list[dict]):
        self.documents = documents
        self.tokens = [self._tokenize(d.get("text", "")) for d in documents]
        self.index = BM25Okapi(self.tokens) if documents else None

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return TOKEN_RE.findall(text.lower())

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        if not self.index or not query.strip():
            return []
        scores = self.index.get_scores(self._tokenize(query))
        order = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        return [{**self.documents[i], "bm25_score": float(scores[i]), "retriever": "bm25"} for i in order]
