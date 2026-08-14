# 프로젝트 실행·실험·제출 기록

> 이 문서는 최종 발표 PPT를 만들 때 사용할 수 있도록 실행 과정, 설정, 결과, 성능 수치, 오류 수정 내용을 누적 관리하는 원장이다. 수치는 실제 실행 결과만 기록하고 추정값은 `미측정`으로 표시한다.

## 1. 프로젝트 개요

- 프로젝트: Semiconductor Equipment Technical RAG Copilot
- 목표: Applied Materials·Lam Research 공식 반도체 장비/공정 자료 기반 질의응답
- MVP 공정: Etch, Deposition, CMP/Clean
- 현재 저장소: `https://github.com/ydy8829-dotcom/Project1`
- 기록 시작일: 2026-08-13

## 2. 목표 아키텍처

```text
OpenWebUI / LibreChat / Streamlit
              ↓
       FastAPI RAG Gateway
              ↓
 Query normalization → BM25 + TF-IDF → reranker
              ↓
      Furiosa OpenAI-compatible API
              ↓
             LLM/NPU
```

## 3. 실행 단계 체크리스트

### Phase 0 — 현재 기준선

- [x] 공식 문서 seed 15건 적재
- [x] 반도체 용어 사전 적재
- [x] BM25 + 경량 TF-IDF 하이브리드 검색
- [x] FastAPI `/health`, `/api/v1/query`, `/api/v1/documents`
- [x] Streamlit UI
- [x] pytest 4건 통과
- [x] Python compileall 통과
- [ ] 50문항 평가셋과 Top-3/Recall/MRR 측정

### Phase 1 — Furiosa NPU 단독 검증

- [ ] NPU 장치/드라이버 확인
- [ ] Furiosa SDK·Furiosa-LLM 버전 기록
- [ ] 지원 모델과 모델 artifact 확인
- [ ] `/v1/models` 확인
- [ ] `/v1/chat/completions` 한글 질의 확인
- [ ] 10회 latency/throughput 측정

실행 결과 — FUR-QWEN3-8B-001 (2026-08-13):

- Host: `edu-hanyang-3`
- NPU: RNGD 8장 인식, 모델 로그상 7개 DP device 사용
- Model: `furiosa-ai/Qwen3-8B-FP8`
- Parameters loaded: 8.8 GiB
- max_kv_len: 268760
- Server: `http://0.0.0.0:8001`
- Startup: 성공 (`Application startup complete`)
- API 응답 시간/처리량: 아직 측정 전
- 참고: `LTW Backend` compatibility warning과 Hugging Face unauthenticated warning은 서버 기동 실패가 아닌 경고

API 검증 결과 — FUR-QWEN3-8B-001:

- `GET http://127.0.0.1:8001/v1/models`: 성공
- Exposed model: `furiosa-ai/Qwen3-8B-FP8`
- Artifact: `qwen3-8b-fp8-b4e5762f15-7f200bf07a-2607212049.fxb`
- max_model_len: `40960`
- API status: 정상

응답 테스트 결과 — FUR-QWEN3-8B-001:

- API 호출 자체: 성공
- `finish_reason`: `length`
- `message.content`: `null`
- `reasoning_tokens`: `299`
- 원인: `max_tokens=300`에서 Qwen3 thinking이 토큰을 모두 소비
- 후속 설정: 일반 RAG 응답은 `/no_think`, `max_tokens>=500`으로 재검증

문서 근거 주입 테스트 — FUR-GROUND-001 (2026-08-13):

- 입력 근거: Lam Research Selective Etch Product Family 공개 설명
- 질문: GAA에서 selective etch가 어떻게 사용되는가
- 결과: 성공. GAA, SiGe removal, selectivity, 정밀도 및 공식 출처 URL을 답변에 포함
- API: `finish_reason=stop`, `content` 정상 생성
- 사용량: prompt 200, completion 159, reasoning 1 tokens
- 품질 주의: "게이트 구조 형성에 필요한 SiGe 층"은 원문 직접 인용이 아닌 모델 해석으로 판단됨
- 개선: system prompt에 `직접 근거`와 `추론`을 구분하고, 추론 문장에는 `문서 근거에 따른 해석` 표시를 요구

공식 Quick Start 기준 실행 후보:

```bash
uv pip install --upgrade --torch-backend=auto furiosa-llm
furiosa-llm serve furiosa-ai/Qwen3-32B-FP8 --host 127.0.0.1 --port 8001
```

초기에는 외부 공개를 피하기 위해 loopback에만 바인딩한다. Windows의 RAG API에서 원격 NPU 서버를 호출할 때는 SSH 터널을 사용한다.

```powershell
ssh -N -L 8001:127.0.0.1:8001 furiosa
```

검증 endpoint:

```bash
curl http://127.0.0.1:8001/v1/models
curl http://127.0.0.1:8001/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"EMPTY","messages":[{"role":"user","content":"HAR etch와 GAA의 관계를 설명해줘."}]}'
```

후보 모델은 장비·메모리 여건을 확인한 뒤 선택한다. 최신 공식 문서에는 Qwen3, Qwen3-Embedding, Qwen3-Reranker, EXAONE, K-EXAONE 및 Solar Open 항목이 안내되어 있다.

기록 필드:

```text
date, host, npu_model, sdk_version, llm_version, model_id,
context_length, prompt_tokens, completion_tokens,
time_to_first_token_ms, total_latency_ms, tokens_per_second,
error, notes
```

### Phase 2 — FastAPI RAG + LLM

- [ ] `OPENAI_BASE_URL` 환경변수 연결
- [ ] 검색 근거를 system/user prompt에 주입
- [ ] 근거 없는 수치 생성 차단
- [ ] 답변별 source_url/citation 반환
- [ ] mock fallback과 Furiosa backend 비교

### Phase 3 — Reranker

- [ ] Top-10 후보 생성
- [ ] reranker Top-3 재정렬
- [ ] Top-1/Top-3/Recall@K/MRR 비교
- [ ] CPU reranker와 NPU reranker 비교

### Phase 4 — UI

- [ ] Streamlit 기준 기능 확인
- [ ] OpenWebUI OpenAI-compatible connection 연결
- [ ] LibreChat custom endpoint 연결
- [ ] 동일 질문·동일 모델·동일 근거로 UI 결과 비교

## 4. 성능 기록

| 실험 ID | 날짜 | Backend | Model | Reranker | 질문 수 | Top-1 | Top-3 | Recall@K | MRR | 평균 지연(ms) | 비고 |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---|
| BASE-001 | 2026-08-13 | local FastAPI | 없음 | 없음 | 미측정 | 미측정 | 미측정 | 미측정 | 미측정 | 미측정 | pytest/API smoke만 완료 |

## 5. 데이터 기록

- 공식 seed 문서: 15건
- Applied Materials: Etch 2, Deposition 4
- Lam Research: Etch 5, Deposition 2, Clean 2
- 비공개 Service/Maintenance/Error Code 문서: 수집하지 않음
- 민감정보: 현재 확인된 API key/token 없음

## 6. 오류·시말서 색인

| ID | 내용 | 상태 | 상세 |
|---|---|---|---|
| ERR-001 | Python/pytest 명령 미등록 | 해결 | `docs/incident_log.md` |
| ERR-002 | 데이터 복사 경로 중첩 | 해결 | `docs/incident_log.md` |
| ERR-003 | CD 용어 정규화 누락 | 해결 | `docs/incident_log.md` |
| ERR-004 | API 스모크 명령 인용부호 오류 | 해결 | `docs/incident_log.md` |
| ERR-005 | ingestion CLI import 경로 오류 | 해결 | `docs/incident_log.md` |
| ERR-006 | PPTX Expand-Archive 확장자 오류 | 해결 예정 | ZIP 복사본으로 재추출 |

## 7. 제출 PPT 생성용 목차 데이터

1. 문제 정의: 모델명·약어·공정·표 정보가 섞인 반도체 장비 문서 검색의 어려움
2. 해결 목표: 공식 자료 기반 반도체 장비 Technical RAG Copilot
3. 데이터 수집: Applied Materials/Lam Research, Etch/Deposition/CMP/Clean
4. 시스템 구성: ingestion → normalization → hybrid retrieval → reranker → LLM → UI
5. 구현 화면: FastAPI Swagger, Streamlit, OpenWebUI/LibreChat 연결 화면
6. Furiosa NPU: 장치, 모델, API 호환, latency/throughput 결과
7. 검색 성능: baseline 대비 reranker 적용 결과
8. 답변 품질: citation accuracy, unsupported claim rate, 사례
9. 오류와 개선: `docs/incident_log.md` 요약
10. 보안·배포: 공개 공식 자료, 비공개 문서 제외, 온프레미스 가능성
11. 한계와 다음 단계

## 8. 변경 이력

- 2026-08-13: 프로젝트 기록 원장 생성

## 9. 제출 PPT 증빙 매트릭스

각 항목은 설명, 재현 명령, 스크린샷, 재생 가능한 동영상, 결과 파일을 함께 관리한다. 아직 확보하지 않은 증빙은 `미확보`로 기록하고 임의로 채우지 않는다.

| 제출 요구사항 | 설명 기록 | 실행/재현 | 이미지 | 동영상 | 상태 |
|---|---|---|---|---|---|
| FuriosaAI NPU 기반 AI 서비스 구축 과정 | 본 문서 1~3장 | Furiosa 서버 접속·모델 서버 실행 | NPU 상태 화면 필요 | 사용자 화면 녹화 필요 | 부분 완료 |
| 전체 시스템 아키텍처/파이프라인 | 본 문서 2장 | 코드·서비스 실행 | 아키텍처 도식 필요 | 선택 | 부분 완료 |
| Furiosa NPU API/외부 AI API | API 구조 기록 필요 | `/v1/models`, `/v1/chat/completions` | curl 결과 필요 | 사용자 화면 녹화 필요 | 부분 완료 |
| LLM/LVM API endpoint 모델 테스트 | Qwen3 LLM 완료 | curl 명령 재현 가능 | 응답 JSON 필요 | 사용자 화면 녹화 필요 | LLM 완료 |
| Front-end/Back-end/DB 개발환경 | 기술 스택 기록 필요 | FastAPI/Streamlit 실행 | 실행 화면 필요 | 사용자 화면 녹화 필요 | 부분 완료 |
| 사용 SW 목록 | README/본 문서 | 버전 명령 필요 | 버전 출력 필요 | 선택 | 부분 완료 |
| FuriosaAI SDK 기능별 수행 | SMI/LLM 기능 기록 필요 | `furiosa-smi`, `furiosa-llm` | 명령 결과 필요 | 사용자 화면 녹화 필요 | 부분 완료 |
| NPU Pod 환경 모델 서버 | Pod 여부 확인 필요 | 환경·배포 명령 필요 | Pod 화면 필요 | 사용자 화면 녹화 필요 | 미확인 |
| NPU Pod 환경 설명 | 별도 기술 설명 필요 | 네트워크/볼륨/포트 기록 | 구조도 필요 | 선택 | 미확인 |
| Furiosa Sample 코드 실행 | sample 종류 선택 필요 | 코드와 결과 저장 | 결과 이미지 필요 | 사용자 화면 녹화 필요 | 미확보 |
| AI 응용 프로그램 배포 | RAG Gateway 배포 필요 | 실행 명령/URL 기록 | 서비스 화면 필요 | 사용자 화면 녹화 필요 | 부분 완료 |
| 최종 AI 서비스 결과 | RAG+LLM 통합 필요 | 최종 실행 재현 | 최종 UI 필요 | 사용자 화면 녹화 필요 | 미완료 |
| NPU/GPU 성능 비교 | 동일 조건 실험 필요 | benchmark script 필요 | 그래프 필요 | 선택 | 미측정 |

## 10. 증빙 파일 규칙

```text
evidence/
  screenshots/
    01_npu_status.png
    02_model_server_ready.png
    03_v1_models.json.png
    04_chat_completion.json.png
    05_rag_ui.png
  videos/
    01_npu_login_and_status.mp4
    02_model_server_start.mp4
    03_api_test.mp4
    04_rag_service_demo.mp4
  results/
    api_responses.jsonl
    benchmark.csv
    environment.txt
```

동영상은 화면의 터미널·브라우저·UI와 실행 시간을 포함해 녹화하고, PPT에는 MP4를 직접 삽입하거나 로컬 파일 링크/QR을 추가한다. 토큰·비밀번호·SSH 개인키·내부 IP가 화면에 노출되지 않도록 녹화 전에 확인한다.

## 11. 현재 확보된 실제 증빙

- Furiosa 서버 hostname: `edu-hanyang-3`
- RNGD NPU 8장 인식 화면 텍스트
- `furiosa-ai/Qwen3-8B-FP8` 모델 로드 로그
- `GET /v1/models` 성공 JSON
- 근거 주입 chat completion 성공 JSON
- 로컬 FastAPI/Streamlit 코드 및 pytest 결과

현재 확보된 것은 텍스트 로그와 JSON 결과이며, 실제 화면 이미지·재생 가능한 동영상은 아직 `evidence/`에 없다.

## 12. PPT 활용 가능 논리 — 모델 선택과 비교 설계

### Qwen3-8B-FP8을 MVP 기준 모델로 선택한 이유

- Furiosa RNGD 1장으로 실행 가능한 공식 pre-compiled artifact다.
- 현재 프로젝트의 Furiosa 서버에서 실제 모델 로드와 OpenAI-compatible `/v1/models` 응답을 확인했다.
- 한국어·영어 질의를 처리할 수 있어 한국 반도체 기술지원 챗봇의 초기 검증에 적합하다.
- 32B·100B급보다 모델 다운로드·기동·반복 테스트 부담이 낮다.
- Furiosa의 Qwen3-Embedding 및 Qwen3-Reranker로 확장할 때 계열을 통일할 수 있다.

### 모델 비교와 하드웨어 비교의 구분

PPT에서는 다음 두 실험을 구분한다.

```text
모델 품질 비교:
Qwen3-8B vs EXAONE-4.0-32B vs Solar Open
→ 한국어 품질, 근거 준수율, citation accuracy, 응답 완성도, 지연시간

하드웨어 성능 비교:
동일 모델·동일 질문·동일 문서를 Furiosa NPU와 GPU에서 실행
→ 응답속도, 추론시간, 처리량, 전력소비, 자원 사용량
```

PPT의 핵심 요구사항인 NPU/GPU 성능 비교는 하드웨어 비교이며, 모델 비교는 Qwen3-8B를 MVP 기준으로 선택한 이유와 최종 모델 선정 근거를 보완한다. 실제 측정 전에는 특정 모델이 우수하다고 단정하지 않는다.

### 발표용 한 문장

`Qwen3-8B-FP8은 Furiosa RNGD 1장에서 실행 가능한 공식 모델이며, 한국어 지원·OpenAI 호환 API·낮은 초기 검증 부담을 이유로 MVP 기준 모델로 선정했다. 이후 동일 질문셋으로 모델 품질과 NPU/GPU 하드웨어 성능을 분리 비교한다.`

## 13. 다음 검증 단계

```text
Windows SSH tunnel
  ↓
Project1 FastAPI의 FURIOSA_BASE_URL 연결
  ↓
질문 정규화·BM25/TF-IDF 검색
  ↓
상위 문서 근거를 Qwen3 prompt에 삽입
  ↓
Qwen3 답변 + source_url 반환
  ↓
groundedness/citation/latency 테스트
```

다음 단계의 합격 조건:

- 검색된 Lam/Applied 공식 문서 내용이 답변에 반영된다.
- 문서에 없는 수치·사양은 생성하지 않는다.
- 답변에 source URL이 포함된다.
- `message.content`가 null이 아니다.
- `finish_reason=stop` 또는 정상적인 length 처리가 된다.
- 통합 호출 latency와 token 사용량을 기록한다.

구현 예정/완료 메모:

- [x] `FURIOSA_BASE_URL`과 `FURIOSA_MODEL` 환경변수 기반 Furiosa OpenAI-compatible client 추가
- [x] 문서 근거를 system/user prompt에 자동 주입
- [x] `/no_think`, 낮은 temperature, max token 제한 적용
- [x] Furiosa 장애 시 문서 근거 fallback 유지
- [ ] SSH tunnel 환경에서 실제 통합 호출 검증

## 14. Furiosa `chat-playground` 적용 판단

공식 `furiosa-apps/chat-playground`는 RAG 애플리케이션이 아니라, Furiosa-LLM의 대화형 추론과 RNGD 시스템 지표를 한 화면에서 보여주는 성능·시연용 레퍼런스 앱이다. 공식 README가 추적하는 지표는 TPS, TTFT, TPOT, E2E latency, 카드별 power(W)다.

### 목적

- NPU 모델 서버가 실제로 응답하는지 시각적으로 시연
- 응답 품질과 함께 추론 성능을 관찰
- PPT의 응답속도·추론시간·처리량·전력소비 항목에 사용할 증빙 화면 확보
- Furiosa NPU 기반 서비스 구축·배포 과정을 보여주는 데모 화면 제공

### 현재 적용 판단

현재는 Project1의 핵심 RAG 통합보다 먼저 적용하지 않는다. Chat Playground는 모델 서버와 성능 지표를 검증하는 보조 앱이며, 우리 문서 검색·citation·grounded answer를 대신하지 않는다. 현재 Qwen3-8B 서버를 유지한 채 RAG Gateway 통합을 먼저 완료한다.

### 적용 시점

다음 두 조건이 충족된 직후 적용한다.

1. `Project1 FastAPI → 문서 검색 → Furiosa Qwen3 답변` 통합 테스트 통과
2. 동일 질문셋으로 모델·NPU 성능 측정을 시작할 준비 완료

그때 Chat Playground는 다음 용도로 사용한다.

- Qwen3-8B-FP8의 TTFT/TPOT/E2E/TPS/power 측정
- Qwen3-8B와 EXAONE-4.0-32B의 시연·성능 비교
- PPT용 성능 대시보드 캡처

공식 예시는 EXAONE-4.0-32B 서버를 8000번 포트에서 띄우고 Chat Playground backend를 8001번 포트에서 실행하는 구조다. 현재 서버는 Qwen3-8B를 8001번 포트에 사용하므로, 적용 시 포트를 `LLM 8001`, `playground 8002`처럼 분리해야 한다. 공식 앱은 production용이 아닌 reference 용도이므로 최종 RAG UI로 채택하지 않는다.
