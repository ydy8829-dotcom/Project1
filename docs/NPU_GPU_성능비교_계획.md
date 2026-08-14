# NPU·GPU 성능 비교 계획

## 프로젝트 요구사항과의 관계

제출요건의 성능 비교는 동일한 AI 서비스를 NPU와 GPU 환경에서 실행하고 응답속도·추론시간·처리량·전력소비를 비교하는 것이다. Embedding과 Reranker의 모델별 측정은 RAG 구성요소 분석이며, NPU·GPU 비교의 대체물이 아니다.

## 공정한 비교 조건

- 동일 모델: Qwen3-8B 계열
- 동일 질문 세트: 동일한 20~50개 질문
- 동일 출력 조건: `max_tokens`, temperature, 입력 문서 수
- 동일 동시성: 순차 요청과 동시 요청을 구분
- 동일 결과 지표: 평균·P95 응답시간, tokens/sec, 처리량, 전력

## 현재 상태

- Furiosa NPU: Qwen3-8B-FP8 서비스 실행 및 RAG 연동 완료
- NPU 구성요소: Embedding·Reranker 별도 실행 및 검색 평가 완료
- 로컬 Windows: `nvidia-smi` 명령을 사용할 수 없어 GPU 실측 환경은 아직 확인되지 않음

## 주의사항

GPU 실측 없이 “NPU가 GPU보다 우수하다”고 결론 내리지 않는다. GPU 장비가 확보되지 않으면 NPU 실측 결과와 GPU 비교 미수행 사유를 투명하게 기록한다.

## 2026-08-14 GPU 측정 업데이트

GPU PC에서 RTX 4060 기반 Qwen3-8B 4-bit PyTorch 측정 결과가 추가되었다. GPU 측정은 완료되었으나 NPU의 FP8·Furiosa API·4개 NPU 구성과 GPU의 NF4·PyTorch·RTX 4060 1개 구성은 조건이 다르므로, 결과는 실행 구성 비교로 제시하고 엄밀한 동일 조건 하드웨어 우열 결론은 보류한다. 상세 검토는 `docs/NPU_GPU_성능비교_검토결과.md`에 기록했다.
