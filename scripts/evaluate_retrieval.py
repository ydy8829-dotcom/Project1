"""Generate and run a deterministic 50-question retrieval evaluation set.

This evaluates retrieval only; it does not call the LLM, so it is cheap and
repeatable. The generated set is intentionally marked as synthetic until a
domain expert reviews the expected document labels.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.normalization.query_normalizer import load_terms, normalize_query  # noqa: E402
from app.retrieval.hybrid_retriever import HybridRetriever  # noqa: E402
from app.retrieval.furiosa_embedding import FuriosaEmbeddingClient  # noqa: E402
from app.retrieval.furiosa_reranker import FuriosaReranker  # noqa: E402

METADATA = ROOT / "data" / "metadata" / "documents.jsonl"
EVAL_DIR = ROOT / "data" / "evaluation"
DATASET = EVAL_DIR / "evaluation_set.jsonl"
RESULT = ROOT / "data" / "evaluation" / "retrieval_results.json"


def load_documents() -> list[dict]:
    documents = [json.loads(line) for line in METADATA.read_text(encoding="utf-8").splitlines() if line.strip()]
    for document in documents:
        content = document.get("content", document.get("text", ""))
        metadata_text = " ".join(str(document.get(key, "")) for key in ("title", "company", "process", "sub_process", "product_name", "product_family", "application", "device_structure", "technology_keywords"))
        document["text"] = f"{metadata_text} {content}".strip()
    return documents


def make_dataset(documents: list[dict]) -> list[dict]:
    rows: list[dict] = []
    templates = [
        "{title}의 핵심 공정 또는 적용 분야는 무엇인가?",
        "{title}에서 다루는 주요 기술 키워드는 무엇인가?",
        "{title}은 어떤 소자 구조나 제조 응용에 사용되는가?",
    ]
    for doc in documents:
        keywords = [str(x) for x in doc.get("technology_keywords", [])]
        applications = [str(x) for x in doc.get("application", [])]
        structures = [str(x) for x in doc.get("device_structure", [])]
        answer_terms = list(dict.fromkeys(keywords[:4] + applications[:3] + structures[:2]))
        for index, template in enumerate(templates, 1):
            rows.append({
                "question_id": f"S{len(rows)+1:03d}",
                "question": template.format(title=doc["title"]),
                "question_type": "synthetic_document_lookup",
                "expected_documents": [doc["title"]],
                "relevant_documents": [{"title": doc["title"], "relevance": 3}],
                "expected_keywords": answer_terms,
                "expected_claims": [],
                "forbidden_claims": [],
                "expected_answer": doc.get("content", "")[:500],
                "source_url": doc.get("source_url", ""),
                "page_number": doc.get("page_number"),
                "review_status": "synthetic_seed_needs_domain_review",
            })
    # Five cross-document questions test company/process terminology.
    extras = [
        ("GAA 관련 선택적 식각과 선택적 질화 증착 문서는 무엇인가?", ["Selective Etch Product Family", "Producer Precision Selective Nitride PECVD"]),
        ("3D NAND와 고종횡비 식각을 다루는 Lam 문서는 무엇인가?", ["Vantex Product Family", "Etch"]),
        ("ALD로 high-k 또는 유전체 박막을 다루는 Applied 문서는 무엇인가?", ["Endura Trillium ALD", "Olympia ALD"]),
        ("웨이퍼 세정과 wet etch를 다루는 Lam 문서는 무엇인가?", ["Reliant Clean Products", "SP Series Product Family"]),
        ("TSV 또는 wafer-level packaging 관련 증착 문서는 무엇인가?", ["Our Processes"]),
    ]
    for question, expected in extras:
        rows.append({
            "question_id": f"S{len(rows)+1:03d}",
            "question": question,
            "question_type": "synthetic_cross_document",
            "expected_documents": expected,
            "relevant_documents": [{"title": title, "relevance": 3 if index == 0 else 2} for index, title in enumerate(expected)],
            "expected_keywords": [],
            "expected_claims": [],
            "forbidden_claims": [],
            "expected_answer": "",
            "source_url": "",
            "page_number": None,
            "review_status": "synthetic_seed_needs_domain_review",
        })
    return rows[:50]


def write_dataset(rows: list[dict]) -> None:
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    DATASET.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")


def evaluate(rows: list[dict], documents: list[dict]) -> dict:
    terms = load_terms(ROOT / "data" / "dictionaries" / "semiconductor_terms.csv")
    embedding_client = FuriosaEmbeddingClient()
    reranker = FuriosaReranker()
    retriever = HybridRetriever(documents, embedding_client=embedding_client)
    details = []
    for row in rows:
        normalized = normalize_query(row["question"], terms)
        candidates = retriever.search(normalized["normalized"], 10)
        results = reranker.rerank(normalized["normalized"], candidates, 10) if reranker.enabled else candidates
        ranked = [item.get("title", "") for item in results]
        relevance = {item["title"]: item.get("relevance", 1) for item in row.get("relevant_documents", [])}
        expected = set(relevance) or set(row["expected_documents"])
        rank = next((i + 1 for i, title in enumerate(ranked) if title in expected), None)
        dcg = sum((relevance.get(title, 0) / math.log2(i + 2)) for i, title in enumerate(ranked[:3]))
        ideal = sorted(relevance.values(), reverse=True)[:3]
        idcg = sum((value / math.log2(i + 2)) for i, value in enumerate(ideal)) or 1
        details.append({"question_id": row["question_id"], "question": row["question"], "expected_documents": row["expected_documents"], "ranked_documents": ranked[:5], "hit_top_1": rank == 1, "hit_top_3": rank is not None and rank <= 3, "first_relevant_rank": rank})
        details[-1]["ndcg_at_3"] = round(dcg / idcg, 4)
    n = len(details) or 1
    ranks = [x["first_relevant_rank"] for x in details if x["first_relevant_rank"]]
    metrics = {
        "dataset_size": len(details),
        "dataset_status": "synthetic_seed_needs_domain_review",
        "top_1_accuracy": round(sum(x["hit_top_1"] for x in details) / n, 4),
        "top_3_accuracy": round(sum(x["hit_top_3"] for x in details) / n, 4),
        "mrr": round(sum(1 / rank for rank in ranks) / n, 4),
        "recall_at_3": round(sum(x["hit_top_3"] for x in details) / n, 4),
        "mean_ndcg_at_3": round(sum(x["ndcg_at_3"] for x in details) / n, 4),
        "rank_distribution": dict(sorted(Counter(ranks).items())),
        "retrieval": {
            "method": "bm25+embedding-cosine+reranker" if reranker.enabled and embedding_client.enabled else (
                "bm25+tfidf-cosine+reranker" if reranker.enabled else (
                    "bm25+embedding-cosine" if embedding_client.enabled else "bm25+tfidf-cosine"
                )
            ),
            "keyword_weight": retriever.keyword_weight,
            "vector_weight": retriever.vector_weight,
            "embedding_configured": embedding_client.enabled,
            "reranker_configured": reranker.enabled,
        },
        "details": details,
    }
    RESULT.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evaluate-only", action="store_true")
    args = parser.parse_args()
    documents = load_documents()
    rows = [json.loads(line) for line in DATASET.read_text(encoding="utf-8").splitlines() if line.strip()] if args.evaluate_only and DATASET.exists() else make_dataset(documents)
    if not args.evaluate_only:
        write_dataset(rows)
    metrics = evaluate(rows, documents)
    print(json.dumps({k: v for k, v in metrics.items() if k != "details"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
