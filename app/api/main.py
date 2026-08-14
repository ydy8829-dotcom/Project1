import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from app.normalization.query_normalizer import load_terms, normalize_query
from app.retrieval.hybrid_retriever import HybridRetriever
from app.rag.answer_generator import generate_answer
from app.rag.furiosa_client import FuriosaClient
from app.retrieval.furiosa_reranker import FuriosaReranker
from app.retrieval.furiosa_embedding import FuriosaEmbeddingClient

ROOT = Path(__file__).resolve().parents[2]
METADATA = ROOT / "data" / "metadata" / "documents.jsonl"
DICTIONARY = ROOT / "data" / "dictionaries" / "semiconductor_terms.csv"


def load_documents(path: Path = METADATA) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            content = row.get("content", row.get("text", ""))
            metadata_text = " ".join(str(row.get(key, "")) for key in ("title", "company", "process", "sub_process", "product_name", "product_family", "application", "device_structure", "technology_keywords"))
            row["text"] = f"{metadata_text} {content}".strip()
            row.setdefault("chunk_id", row.get("title", "document"))
            rows.append(row)
    return rows


app = FastAPI(title="Semiconductor Equipment Technical RAG Copilot", version="0.2.0")
documents = load_documents()
terms = load_terms(DICTIONARY)
llm = FuriosaClient()
reranker = FuriosaReranker()
embedder = FuriosaEmbeddingClient()
retriever = HybridRetriever(documents, embedding_client=embedder)


class QueryRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


@app.get("/health")
def health():
    return {"status": "ok", "service": "technical-rag-copilot", "documents": len(documents), "furiosa_configured": llm.enabled, "furiosa_model": llm.model if llm.enabled else None, "embedding_configured": embedder.enabled, "embedding_model": embedder.model if embedder.enabled else None, "reranker_configured": reranker.enabled, "reranker_model": reranker.model if reranker.enabled else None}


@app.get("/api/v1/documents")
def list_documents():
    return {"count": len(documents), "documents": [{k: d.get(k) for k in ("title", "company", "process", "document_type", "source_url")} for d in documents]}


@app.post("/api/v1/query")
def query(request: QueryRequest):
    normalized = normalize_query(request.question, terms)
    evidence = retriever.search(normalized["normalized"], min(10, max(request.top_k, 5)))
    if reranker.enabled:
        evidence = reranker.rerank(request.question, evidence, request.top_k)
    else:
        evidence = evidence[:request.top_k]
    answer = generate_answer(request.question, evidence, llm)
    answer["query"] = normalized
    base_method = "bm25+embedding-cosine" if embedder.enabled else "bm25+tfidf-cosine"
    answer["retrieval"] = {"method": f"{base_method}+reranker" if reranker.enabled else base_method, "keyword_weight": retriever.keyword_weight, "vector_weight": retriever.vector_weight, "embedding_model": embedder.model if embedder.enabled else None, "reranker": reranker.model if reranker.enabled else None}
    return answer


@app.post("/api/v1/ingest")
def ingest():
    global documents, retriever
    documents = load_documents()
    retriever = HybridRetriever(documents, embedding_client=embedder)
    return {"status": "ok", "documents": len(documents)}
