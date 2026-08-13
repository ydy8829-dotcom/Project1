import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from app.normalization.query_normalizer import load_terms, normalize_query
from app.retrieval.hybrid_retriever import HybridRetriever
from app.rag.answer_generator import generate_answer

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
            row["text"] = row.get("content", row.get("text", ""))
            row.setdefault("chunk_id", row.get("title", "document"))
            rows.append(row)
    return rows


app = FastAPI(title="Semiconductor Equipment Technical RAG Copilot", version="0.2.0")
documents = load_documents()
retriever = HybridRetriever(documents)
terms = load_terms(DICTIONARY)


class QueryRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


@app.get("/health")
def health():
    return {"status": "ok", "service": "technical-rag-copilot", "documents": len(documents)}


@app.get("/api/v1/documents")
def list_documents():
    return {"count": len(documents), "documents": [{k: d.get(k) for k in ("title", "company", "process", "document_type", "source_url")} for d in documents]}


@app.post("/api/v1/query")
def query(request: QueryRequest):
    normalized = normalize_query(request.question, terms)
    evidence = retriever.search(normalized["normalized"], request.top_k)
    answer = generate_answer(request.question, evidence)
    answer["query"] = normalized
    answer["retrieval"] = {"method": "bm25+tfidf-cosine", "keyword_weight": retriever.keyword_weight, "vector_weight": retriever.vector_weight}
    return answer


@app.post("/api/v1/ingest")
def ingest():
    global documents, retriever
    documents = load_documents()
    retriever = HybridRetriever(documents)
    return {"status": "ok", "documents": len(documents)}
