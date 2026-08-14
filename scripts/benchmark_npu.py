"""Benchmark the end-to-end NPU-backed RAG API."""
from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "evaluation" / "npu_benchmark_latest.json"

QUESTIONS = [
    "Lam Research의 selective etch는 GAA에 어떻게 적용되는가?",
    "반도체 공정에서 HAR etch는 어떤 구조에 사용되는가?",
    "GAA 공정에서 SiGe removal의 문서 근거는 무엇인가?",
    "Lam Research의 RIE와 ALE는 어떻게 설명되는가?",
    "식각 장비의 정확한 처리량 수치가 문서에 제공되는가?",
]


def percentile(values: list[float], level: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    index = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * level)))
    return ordered[index]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8002")
    parser.add_argument("--repeats", type=int, default=20)
    parser.add_argument("--warmup", type=int, default=2)
    args = parser.parse_args()

    url = args.url.rstrip("/")
    rows: list[dict] = []
    with httpx.Client(timeout=180.0) as client:
        health = client.get(f"{url}/health").json()
        for index in range(args.warmup):
            question = QUESTIONS[index % len(QUESTIONS)]
            client.post(f"{url}/api/v1/query", json={"question": question, "top_k": 5}).raise_for_status()
        for index in range(args.repeats):
            question = QUESTIONS[index % len(QUESTIONS)]
            started = time.perf_counter()
            try:
                response = client.post(f"{url}/api/v1/query", json={"question": question, "top_k": 5})
                response.raise_for_status()
                body = response.json()
                elapsed = time.perf_counter() - started
                usage = body.get("llm", {}).get("usage", {})
                completion_tokens = usage.get("completion_tokens", 0) or 0
                rows.append({
                    "index": index + 1,
                    "question": question,
                    "latency_seconds": round(elapsed, 4),
                    "completion_tokens": completion_tokens,
                    "tokens_per_second": round(completion_tokens / elapsed, 3) if completion_tokens else None,
                    "retrieval_method": body.get("retrieval", {}).get("method"),
                    "success": True,
                })
            except Exception as exc:
                rows.append({"index": index + 1, "question": question, "success": False, "error": str(exc)})

    successful = [row for row in rows if row.get("success")]
    latencies = [row["latency_seconds"] for row in successful]
    total_tokens = sum(row.get("completion_tokens", 0) or 0 for row in successful)
    total_time = sum(latencies)
    metrics = {
        "benchmark": "end_to_end_npu_rag_api",
        "api_url": url,
        "warmup_requests": args.warmup,
        "measured_requests": args.repeats,
        "successful_requests": len(successful),
        "success_rate": round(len(successful) / args.repeats, 4) if args.repeats else 0,
        "average_latency_seconds": round(statistics.mean(latencies), 4) if latencies else None,
        "min_latency_seconds": round(min(latencies), 4) if latencies else None,
        "max_latency_seconds": round(max(latencies), 4) if latencies else None,
        "p95_latency_seconds": round(percentile(latencies, 0.95), 4) if latencies else None,
        "throughput_requests_per_second": round(len(successful) / total_time, 4) if total_time else None,
        "total_completion_tokens": total_tokens,
        "completion_tokens_per_second": round(total_tokens / total_time, 3) if total_time else None,
        "health": health,
        "rows": rows,
        "limitations": [
            "측정값은 로컬 PC에서 FastAPI를 거쳐 NPU 모델 서버까지 포함한 종단간 지연시간이다.",
            "전력소비는 별도 furiosa-smi 표본 측정이 필요하다.",
            "GPU와의 비교는 동일 조건의 GPU 측정 후에만 결론낼 수 있다.",
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in metrics.items() if key not in {"rows", "health"}}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
