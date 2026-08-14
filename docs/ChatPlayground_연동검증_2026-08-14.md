# Chat Playground·Qwen3 NPU 연동 검증

## 검증 목적

Chat Playground를 최종 RAG UI가 아닌 Qwen3 NPU 추론 성능 확인 도구로 사용하고, 실시간 성능 이벤트가 정상 수신되는지 확인했다.

## 구성

- Qwen3 LLM 서버: 원격 `8001`
- Chat Playground 백엔드: 원격 `8502`
- 로컬 터널: `18502 -> 8502`
- 모델: `furiosa-ai/Qwen3-8B-FP8`
- NPU: Qwen3 npu4~npu7

## 자동 WebSocket 검증 결과

긴 반도체 식각 관련 질문을 Chat Playground WebSocket(`/updates`)로 전송했다.

- WebSocket `INIT`: 성공
- `CREATE`: 성공
- `UPDATE`: Qwen3 스트리밍 토큰 수신
- `INFO_UPDATE`: 정상 수신
- 관측 Power: 40.0W
- 관측 Temperature: 약 40.1℃
- 관측 `tokens_per_sec`: 88
- 관측 `max_tps`: 88

## 해석

Chat Playground는 1초 단위로 성능을 갱신한다. 생성 중에는 TPS가 변하고, 생성이 끝나면 TPS가 0 또는 낮은 값으로 돌아갈 수 있다. Power는 유휴 전력과 추론 전력 차이가 작으면 거의 일정하게 보일 수 있다. 따라서 영상에서는 질문 전송 직후부터 답변 생성 중인 구간을 녹화해야 한다.

## 주의사항

이 검증은 단일 요청에서 관측한 실시간 이벤트 확인이며, 평균 성능값으로 사용하지 않는다. 평균 TTFT·TPOT·E2E·전력은 여러 요청을 반복하여 별도 집계해야 한다. Chat Playground 결과는 Qwen3 모델 추론 성능 자료이고, 최종 RAG 답변 성능은 Streamlit/FastAPI 화면으로 증빙한다.
