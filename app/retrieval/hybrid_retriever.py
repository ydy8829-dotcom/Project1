import math
from collections import Counter
from app.retrieval.bm25_retriever import BM25Retriever


class HybridRetriever:
    """Offline hybrid MVP: BM25 plus a lightweight TF-IDF cosine signal."""

    def __init__(self, documents: list[dict], keyword_weight: float = 0.55, vector_weight: float = 0.45):
        self.documents = documents
        self.keyword_weight = keyword_weight
        self.vector_weight = vector_weight
        self.bm25 = BM25Retriever(documents)
        self.term_counts = [Counter(self.bm25._tokenize(d.get("text", ""))) for d in documents]

    def _vector_score(self, query: str, counts: Counter) -> float:
        query_counts = Counter(self.bm25._tokenize(query))
        if not query_counts or not counts:
            return 0.0
        n = max(1, len(self.documents))
        def weight(token: str, freq: int) -> float:
            df = sum(1 for row in self.term_counts if token in row)
            return (1 + math.log(freq)) * math.log((n + 1) / (df + 1))
        q = {t: weight(t, f) for t, f in query_counts.items()}
        d = {t: weight(t, f) for t, f in counts.items()}
        dot = sum(q[t] * d.get(t, 0.0) for t in q)
        qnorm = math.sqrt(sum(v * v for v in q.values()))
        dnorm = math.sqrt(sum(v * v for v in d.values()))
        return dot / (qnorm * dnorm) if qnorm and dnorm else 0.0

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        if not self.documents:
            return []
        bm25_results = self.bm25.search(query, len(self.documents))
        by_id = {r.get("chunk_id", i): r for i, r in enumerate(bm25_results)}
        max_bm25 = max((r.get("bm25_score", 0.0) for r in bm25_results), default=0.0)
        results = []
        for i, doc in enumerate(self.documents):
            match = by_id.get(doc.get("chunk_id", i), {})
            bm25 = match.get("bm25_score", 0.0)
            bm25_norm = bm25 / max_bm25 if max_bm25 > 0 else 0.0
            vector = self._vector_score(query, self.term_counts[i])
            score = self.keyword_weight * bm25_norm + self.vector_weight * vector
            results.append({**doc, "bm25_score": bm25, "vector_score": vector, "hybrid_score": score, "score": score})
        return sorted(results, key=lambda item: item["score"], reverse=True)[:top_k]
