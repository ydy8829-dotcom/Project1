# Qwen3 NPU·GPU 실행 구성 비교

| 지표 | NPU | GPU | 관측 비율 |
|---|---:|---:|---:|
| 평균 응답시간 | 1.737초 | 6.851초 | NPU 약 3.94배 빠름 |
| P95 응답시간 | 2.124초 | 8.351초 | NPU 약 3.93배 빠름 |
| 생성 토큰 처리량 | 62.232 tokens/sec | 15.705 tokens/sec | NPU 약 3.96배 높음 |
| 요청 처리량 | 0.576 req/sec | 0.146 req/sec | NPU 약 3.95배 높음 |

## 측정 조건

- NPU: Qwen3-8B-FP8, Furiosa-LLM OpenAI API, npu4~npu7
- GPU: unsloth/Qwen3-8B-bnb-4bit, PyTorch CUDA, NVIDIA GeForce RTX 4060
- 반복: 20회, 워밍업 2회, `max_tokens=128`
- NPU와 GPU 모두 동일한 UTF-8 한국어 질문 세트를 사용한 결과 파일 기준

## 해석 제한

두 환경의 양자화(FP8 대 NF4), 실행 경로(API 대 로컬 PyTorch), 장치 수(4개 NPU 대 1개 GPU)가 다르다. 따라서 위 수치는 “측정된 실행 구성의 관측 결과”로 제시하며, 동일 하드웨어 조건의 절대적 우열로 표현하지 않는다.
