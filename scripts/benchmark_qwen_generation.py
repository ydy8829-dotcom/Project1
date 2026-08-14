"""Benchmark only Qwen generation for fair CPU/NPU/GPU comparison."""
from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
QUESTIONS = [
    "반도체 식각 공정에서 선택비가 중요한 이유를 설명하라.",
    "GAA 구조에서 SiGe 제거가 언급되는 문서 근거를 요약하라.",
    "RIE와 ALE의 차이를 제공된 근거 범위에서 설명하라.",
    "HAR etch와 3D 구조의 관계를 문서 근거로 설명하라.",
    "문서에 처리량 수치가 없을 때 어떻게 답변해야 하는가?",
]


def p95(values: list[float]) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, round((len(ordered) - 1) * 0.95))]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True, help="OpenAI-compatible /v1 endpoint")
    parser.add_argument("--model", required=True)
    parser.add_argument("--backend", required=True, help="npu, cpu, or gpu")
    parser.add_argument("--repeats", type=int, default=20)
    parser.add_argument("--warmup", type=int, default=2)
    parser.add_argument("--max-tokens", type=int, default=128)
    args = parser.parse_args()

    rows = []
    with httpx.Client(timeout=180.0) as client:
        for index in range(args.warmup + args.repeats):
            question = QUESTIONS[index % len(QUESTIONS)]
            payload = {
                "model": args.model,
                "temperature": 0.1,
                "max_tokens": args.max_tokens,
                "messages": [
                    {"role": "system", "content": "Answer using only the supplied question context. Be concise."},
                    {"role": "user", "content": f"Question: {question} /no_think"},
                ],
            }
            started = time.perf_counter()
            response = client.post(f"{args.base_url.rstrip('/')}/chat/completions", json=payload)
            response.raise_for_status()
            elapsed = time.perf_counter() - started
            if index >= args.warmup:
                body = response.json()
                usage = body.get("usage", {})
                tokens = usage.get("completion_tokens", 0) or 0
                rows.append({"latency_seconds": elapsed, "completion_tokens": tokens})

    latencies = [row["latency_seconds"] for row in rows]
    total_tokens = sum(row["completion_tokens"] for row in rows)
    total_time = sum(latencies)
    result = {
        "benchmark": "qwen_generation_only",
        "backend": args.backend,
        "base_url": args.base_url,
        "model": args.model,
        "requests": len(rows),
        "average_latency_seconds": round(statistics.mean(latencies), 4),
        "min_latency_seconds": round(min(latencies), 4),
        "max_latency_seconds": round(max(latencies), 4),
        "p95_latency_seconds": round(p95(latencies), 4),
        "tokens_per_second": round(total_tokens / total_time, 3) if total_time else None,
        "requests_per_second": round(len(rows) / total_time, 4) if total_time else None,
        "max_tokens": args.max_tokens,
    }
    output = ROOT / "data" / "evaluation" / f"qwen_{args.backend}_benchmark.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
