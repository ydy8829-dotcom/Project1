# NPU·GPU 성능 비교 검토 결과

## 현재 수치

| 지표 | Furiosa NPU | NVIDIA GPU |
|---|---:|---:|
| 모델 | Qwen3-8B-FP8 | unsloth/Qwen3-8B-bnb-4bit |
| 장치 | npu4~npu7 | RTX 4060 |
| 평균 응답시간 | 1.737초 | 6.851초 |
| P95 응답시간 | 2.124초 | 8.351초 |
| 생성 토큰 처리량 | 62.232 tokens/sec | 15.705 tokens/sec |
| 요청 처리량 | 0.576 req/sec | 0.146 req/sec |

## 정확한 해석

현재 결과만 보면 NPU 실행 구성이 GPU 실행 구성보다 빠른 결과를 보였다. 그러나 다음 조건이 달라 엄밀한 동일 조건 하드웨어 우열 비교로 확정할 수 없다.

- NPU는 FP8, GPU는 NF4 4-bit 양자화다.
- NPU는 Furiosa-LLM OpenAI API 호출 시간이고 GPU는 로컬 PyTorch에서 tokenizer와 생성 시간을 함께 측정했다.
- NPU는 4개 NPU 장치, GPU는 RTX 4060 1개 장치다.
- GPU 결과는 질문 목록을 UTF-8 정상 문자열로 수정한 스크립트 기준으로 재측정하는 것이 바람직하다.

따라서 PPT의 메인 제목은 다음처럼 작성한다.

> Qwen3-8B 계열 NPU·GPU 실행 구성 성능 비교(측정 조건 상이점 포함)

“NPU가 GPU보다 우수하다”는 단정 대신, 측정된 실행 구성에서 NPU가 더 낮은 지연시간과 높은 토큰 처리량을 보였다고 표현한다.

## RNGD Chat의 위치

RNGD Chat/Chat Playground는 보조 성능 자료로 제시한다.

- TTFT
- TPOT
- E2E latency
- TPS
- 카드별 Power

RNGD Chat은 Qwen3 모델 추론과 RNGD 시스템 지표를 실시간으로 보여주는 도구이며, 문서 검색·Reranker·출처 생성을 포함한 최종 RAG 성능을 대체하지 않는다.

## 재측정 권장

GPU PC에서 수정된 `scripts/benchmark_qwen_gpu.py`를 다시 실행하여 동일한 한국어 질문 세트로 결과를 갱신한다. 갱신 전 기존 GPU 결과는 `기존 측정값(조건 차이 주석 필요)`으로 표시한다.
