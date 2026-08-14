# Furiosa Qwen3 서버 기동 오류 — torch/torchvision 호환성

## 증상

원격 Furiosa 서버에서 다음 명령 실행 시 Qwen3 서버가 시작되지 않았다.

```bash
furiosa-llm serve furiosa-ai/Qwen3-8B-FP8 --port 8001
```

오류 핵심:

```text
RuntimeError: operator torchvision::nms does not exist
```

## 판단

Furiosa 모델 파일·포트·RAG 코드 문제가 아니다. `furiosa_llm` import 과정에서 `transformers`가 `torchvision`을 불러오고, 설치된 `torch`와 `torchvision`의 연산자 호환성이 맞지 않아 중단됐다.

## 현재 영향

- 원격 Qwen3 서버 8001: 기동 실패
- SSH 터널 18001: 아직 연결하지 않음
- FastAPI 8002: Qwen3 연결을 시도하지 않음
- 기존 코드와 임베딩·reranker 구현에는 영향 없음

## 추가 확인 결과

- 전역 `furiosa-llm`: `2026.1.0`
- `torch`: `2.7.0`
- `torchvision`: `0.25.0+cpu`
- `transformers`: `4.57.1`
- NPU 전체를 점유 중인 프로세스: PID `3388533`
- 점유 명령: `/root/lee/furiosa-apps/chat-playground/.venv/bin/furiosa-llm serve furiosa-ai/EXAONE-4.0-32B-FP8 ... --port 8000`

현재는 Qwen3 오류 외에 EXAONE Chat Playground 서버가 8개 NPU를 모두 사용 중이다. 이 프로세스가 다른 사용자 또는 공동 실습 서비스일 수 있으므로 승인 없이 종료하지 않는다.

## 조치 원칙

버전 확인 전 시스템 패키지를 삭제·업데이트하지 않는다. `torch`, `torchvision`, `transformers`, `furiosa-llm` 버전을 먼저 확인하고, Furiosa 제공 환경 또는 관리자 권장 방식으로 복구한다.
