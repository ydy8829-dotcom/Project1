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
