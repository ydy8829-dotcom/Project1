"""Benchmark local CUDA generation with a 4-bit Qwen3-8B model."""
from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

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
    parser.add_argument("--model", default="unsloth/Qwen3-8B-bnb-4bit")
    parser.add_argument("--repeats", type=int, default=20)
    parser.add_argument("--warmup", type=int, default=2)
    parser.add_argument("--max-tokens", type=int, default=128)
    args = parser.parse_args()

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA GPU is required; torch.cuda.is_available() returned False")

    tokenizer = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        device_map="cuda:0",
        torch_dtype=torch.bfloat16,
    )
    model.eval()

    rows: list[dict[str, object]] = []
    for index in range(args.warmup + args.repeats):
        question = QUESTIONS[index % len(QUESTIONS)]
        messages = [
            {"role": "system", "content": "Answer using only the supplied question context. Be concise."},
            {"role": "user", "content": f"Question: {question} /no_think"},
        ]
        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(prompt, return_tensors="pt").to("cuda:0")
        torch.cuda.synchronize()
        started = time.perf_counter()
        with torch.inference_mode():
            generated = model.generate(
                **inputs,
                max_new_tokens=args.max_tokens,
                do_sample=False,
                use_cache=True,
            )
        torch.cuda.synchronize()
        elapsed = time.perf_counter() - started
        completion_tokens = int(generated.shape[-1] - inputs.input_ids.shape[-1])
        if index >= args.warmup:
            rows.append({
                "index": index - args.warmup + 1,
                "question": question,
                "latency_seconds": round(elapsed, 4),
                "completion_tokens": completion_tokens,
                "tokens_per_second": round(completion_tokens / elapsed, 3) if elapsed else None,
            })

    latencies = [float(row["latency_seconds"]) for row in rows]
    total_tokens = sum(int(row["completion_tokens"]) for row in rows)
    total_time = sum(latencies)
    result = {
        "benchmark": "qwen_generation_only",
        "backend": "gpu",
        "execution": "local PyTorch CUDA generation; tokenizer and GPU generation are timed together",
        "model": args.model,
        "model_family": "Qwen3-8B",
        "quantization": "bitsandbytes 4-bit NF4",
        "device": torch.cuda.get_device_name(0),
        "cuda_version": torch.version.cuda,
        "requests": len(rows),
        "warmup_requests": args.warmup,
        "average_latency_seconds": round(statistics.mean(latencies), 4),
        "min_latency_seconds": round(min(latencies), 4),
        "max_latency_seconds": round(max(latencies), 4),
        "p95_latency_seconds": round(p95(latencies), 4),
        "tokens_per_second": round(total_tokens / total_time, 3) if total_time else None,
        "requests_per_second": round(len(rows) / total_time, 4) if total_time else None,
        "max_tokens": args.max_tokens,
        "peak_allocated_vram_mib": round(torch.cuda.max_memory_allocated(0) / 1024**2, 1),
        "peak_reserved_vram_mib": round(torch.cuda.max_memory_reserved(0) / 1024**2, 1),
        "rows": rows,
        "comparison_limitations": [
            "NPU 기준은 Furiosa Qwen3-8B-FP8 OpenAI API의 종단간 응답시간이고 GPU는 로컬 PyTorch 호출이다.",
            "동일 Qwen3-8B 계열이지만 NPU는 FP8, GPU는 NF4 4-bit 양자화여서 절대 성능의 공정한 우열 결론에는 한계가 있다.",
            "GPU 전력은 WDDM 환경에서 nvidia-smi가 Power Draw를 제공할 때만 별도로 기록한다.",
        ],
    }
    output = ROOT / "data" / "evaluation" / "qwen_gpu_benchmark.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "rows"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
