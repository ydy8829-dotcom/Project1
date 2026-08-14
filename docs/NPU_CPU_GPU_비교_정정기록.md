# NPU·CPU·GPU 비교 측정 구분 기록

## 정정 내용

기존 NPU 성능 측정은 Qwen3 생성뿐 아니라 FastAPI·검색·Reranker를 포함한 최종 RAG 서비스의 종단간 측정이었다. 이 값은 실제 서비스 성능에는 유효하지만, 하드웨어 간 순수 추론 성능 비교에는 적합하지 않다.

## 공정한 하드웨어 비교

NPU·CPU·GPU 비교에는 Qwen3 생성 서버의 `/v1/chat/completions`만 직접 호출한다. 동일 모델, 동일 질문, 동일 `max_tokens`, 동일 temperature, 동일 반복 횟수를 사용한다.

## 측정 스크립트

```powershell
uv run --with-requirements requirements.txt python scripts\benchmark_qwen_generation.py `
  --base-url http://127.0.0.1:18001/v1 `
  --model furiosa-ai/Qwen3-8B-FP8 `
  --backend npu `
  --repeats 20 `
  --warmup 2 `
  --max-tokens 128
```

CPU·GPU에서도 endpoint와 모델명을 해당 환경에 맞게 바꾸고 동일 명령을 실행한다.

## 기존 NPU 결과의 위치

- 최종 RAG 종단간 성능: `docs/NPU_성능측정_2026-08-14.md`
- 순수 Qwen 하드웨어 비교: `data/evaluation/qwen_*_benchmark.json`
