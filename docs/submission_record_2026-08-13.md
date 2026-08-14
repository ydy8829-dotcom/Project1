# 제출용 누적 기록 — 반도체 공정장비 Technical RAG Copilot

## 프로젝트 방향

제조 설비 카탈로그·기술매뉴얼 RAG 챗봇을 반도체 공정장비 분야로 전환했다. 목표는 모델명·약어·공정 용어·사양 문서가 섞인 환경에서 키워드 검색과 의미 검색을 결합하고, 답변에 공식 문서 근거를 표시하는 것이다.

## 현재 구현 및 검증 완료

- FastAPI RAG Gateway: 로컬 `8002`
- Furiosa LLM API: SSH 터널 `18001` → 원격 `8001`
- 모델: `furiosa-ai/Qwen3-8B-FP8`
- NPU 모델 API `/v1/models`: 성공
- 문서 검색 → 근거 주입 → Qwen3 답변 생성: 성공
- 검색 방식: BM25 + TF-IDF cosine, keyword/vector `0.55/0.45`
- 문서 출처 URL과 검색 근거를 응답에 포함
- 근거 부족 질문에서 임의의 식각 속도·처리량 수치를 생성하지 않음
- `insufficient_evidence` 메타데이터 보정 로직 추가
- 테스트: `pytest` 4개 통과

## 평가 설계 변경

단일 정답 문서만 비교하는 방식은 최종 평가에 부적절하다. 한 질문에 여러 문서가 답이 될 수 있고, 검색 순위만으로 답변 정확성을 판단할 수 없기 때문이다.

현재 자동 평가에는 다음 필드를 포함하도록 확장했다.

- `relevant_documents`: 관련 문서 목록과 relevance 등급
- `expected_keywords`: 기대 핵심 용어
- `expected_claims`: 최종 검수 단계에서 추가할 핵심 주장
- `forbidden_claims`: 근거 없이 단정하면 안 되는 주장

평가 지표는 Top-1, Recall@3/Top-3, MRR, nDCG@3로 분리한다. 이후 답변 생성 평가에는 근거 지원율·인용 정확도·환각률·거부 정확도를 추가한다.

## 현재 자동 seed baseline

자동 생성 50문항은 아직 `synthetic_seed_needs_domain_review` 상태이다.

- Top-1: 6%
- Recall@3/Top-3: 38%
- MRR: 0.2919
- 평균 nDCG@3: 0.2406
- 목표: 검수된 평가셋 기준 Top-3 80% 이상

이 수치는 최종 성능으로 제출하지 않고, 도메인 검수 후 재측정한 결과를 최종 성능으로 사용한다.

## PPT 캡처 증거

1. `furiosa-smi`에서 RNGD NPU 상태가 보이는 화면
2. Qwen3 모델 로딩 및 Furiosa LLM 서버 `8001` 기동 화면
3. SSH 터널을 통한 `18001/v1/models` 응답 화면
4. Swagger `8002/docs`의 RAG 응답 화면: `answer`, `evidence`, `retrieval`, `llm.provider=furiosa`
5. 근거 부족 질문 결과: `insufficient_evidence=true`, 임의 수치 없음
6. 자동 평가 결과 JSON 또는 표: Top-3, MRR, nDCG@3

## 다음 개발 순서

1. 평가셋 50문항의 문서·근거 문장·기대 주장 도메인 검수
2. 실제 임베딩 모델 연결
3. reranker 연결 및 동일 평가셋 재측정
4. Langfuse trace/evaluation 연동
5. 실무형 웹 UI 개선
6. Chat Playground 기반 TTFT·TPOT·TPS·전력 측정
7. NPU/GPU 동일 조건 비교
