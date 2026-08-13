# 반도체 공정장비 Technical RAG Copilot PRD

## 1. 프로젝트 개요

Applied Materials와 Lam Research의 공식 공개 PDF·HTML 기술자료를 검색·분석하여 반도체 공정장비와 Etch 공정에 관한 답변을 문서 근거와 함께 제공하는 RAG 기반 기술지원 Copilot이다.

## 2. 문제 정의

- 제품명·모델명·약어·공정 용어가 혼재해 일반 키워드 검색만으로는 문서를 찾기 어렵다.
- 카탈로그와 기술자료의 사양·표·페이지 정보가 검색 과정에서 손실될 수 있다.
- 유사한 장비와 공정 설명이 여러 문서에 분산되어 비교와 근거 확인이 어렵다.
- 문서에 없는 내용을 LLM이 추정하면 기술지원 신뢰성이 떨어진다.

## 3. 목표와 범위

### MVP 목표

`공식 PDF/HTML 수집 → 파싱 → 청킹 → 용어 정규화 → BM25/벡터 하이브리드 검색 → 근거 기반 답변 → 출처 표시`의 전체 흐름을 안정적으로 실행한다.

### 데이터 범위

- 제조사: Applied Materials, Lam Research
- 1차 공정: Etch, Plasma Etch, Dry Etching, Conductor Etch, Dielectric Etch
- 기술 주제: CD Control, Profile Control, Selectivity, Aspect Ratio, Patterning
- 허용: 공식 공개 제품 페이지, 브로슈어, 카탈로그, 애플리케이션·기술 설명자료
- 제외: 뉴스, 개인 블로그, 중고거래, 비공개 Service/Maintenance Manual, 출처 불명 자료

### 데이터셋 운영 원칙

실제 데이터셋은 사용자가 별도로 수집·관리한다. Scaffold에는 원본 PDF·HTML·카탈로그를 포함하지 않으며, 실행 시 환경변수 또는 명령행 인자로 데이터셋 경로를 전달한다. 프로젝트에는 파서 검증을 위한 소형 테스트 fixture만 둘 수 있다.

### 향후 확장

Deposition, CMP, Clean, Lithography 연계, 공정 파라미터 및 웨이퍼맵 분석, 온프레미스 LLM/NPU 배포.

## 4. 사용자와 사용 사례

| 사용자 | 사용 사례 |
|---|---|
| 공정 엔지니어 | Etch 공정과 장비 적용 분야 확인 |
| 장비 엔지니어/CE | 공식 기술자료 기반 점검 후보 확인 |
| 기술영업 | 제품 비교 및 고객 질의 대응 |
| 연구·학습자 | 반도체 장비·공정 개념 학습 |

## 5. 기능 요구사항

### FR-01 문서 적재

별도로 수집한 PDF·HTML 데이터셋을 읽고 페이지, 제목, 섹션, 제조사, 제품명, 공정, URL을 보존한다. SHA-256 해시로 중복 문서를 제거한다.

### FR-02 청킹

페이지와 섹션 경계를 우선 보존하며, 기본 청크 크기 800 tokens, overlap 120 tokens로 설정한다. 표는 가능한 한 한 행의 의미가 훼손되지 않도록 별도 텍스트로 저장한다.

### FR-03 용어 정규화

Etch/식각, Plasma Etch/플라즈마 식각, CD/Critical Dimension, AMAT/Applied Materials, Lam/Lam Research 등을 정규화한다. 원문 질의도 함께 저장한다.

### FR-04 검색

BM25와 임베딩 검색을 각각 수행하고 점수 정규화 후 기본 가중치 0.5:0.5로 결합한다. 제조사·공정·제품군 필터와 Rerank 인터페이스를 제공한다.

### FR-05 답변

검색 context만 사용한다. 문서에 없는 수치·사양·정비 절차를 생성하지 않는다. 답변에는 문서명, 페이지, URL, 인용문을 포함한다.

### FR-06 비교

두 장비의 제조사, 적용 공정, 애플리케이션, 지원 웨이퍼 크기, 구조, CD·선택비·생산성 관련 공개 정보를 동일 기준으로 비교한다. 없는 항목은 확인되지 않음으로 표시한다.

### FR-07 평가

50문항 평가셋, Top-1/Top-3, Recall@K, MRR, Citation Accuracy, Unsupported Claim Rate, 평균 지연시간을 지원한다.

## 6. 비기능 요구사항

- Windows 11, Python 3.11+, PowerShell, VS Code에서 실행
- UTF-8 한글 처리
- API 키 환경변수 관리
- 외부 LLM 없이 MOCK 모드 실행
- 실패 시 이해하기 쉬운 오류 반환
- 근거 없는 답변 최소화
- 수집 시 robots.txt와 rate limit 준수

## 7. 품질 목표

초기 목표는 Top-3 검색 정답률 80% 이상, 답변 근거 포함률 90% 이상이다. 모든 평가 문항에서 문서에 없는 정보를 확정적으로 말하지 않는 것을 우선한다.

## 8. API 요구사항

- `GET /health`: 상태 확인
- `POST /api/v1/query`: 질문, 필터, top_k를 받아 답변·근거 반환
- `POST /api/v1/ingest`: 로컬 문서 적재 실행
- `GET /api/v1/documents`: 적재 문서 목록

## 9. 보안·윤리·데이터 제약

공식 공개자료만 사용하고 문서의 저작권·접근정책을 준수한다. 실제 장비 조작, 안전 우회, 정비 절차를 생성하지 않는다. 공개 문서가 충분하지 않으면 답변을 보류한다.

## 10. 개발 단계

1. 설정·헬스체크
2. 샘플 문서·BM25 검색
3. PDF 적재·청킹·메타데이터
4. 벡터 검색·하이브리드 검색
5. 근거 기반 답변
6. FastAPI·Streamlit
7. 평가셋·Langfuse
8. 제품 비교 및 공정 범위 확장

## 11. 수용 기준

- `python -m compileall app scripts` 성공
- `pytest -q` 성공
- 샘플 질문에 대해 검색 결과와 출처가 표시됨
- 문서에 없는 질문에 대해 추측 답변을 하지 않음
- 실제 PDF의 페이지 번호와 URL이 최종 답변까지 보존됨
- PowerShell 실행 명령이 README와 일치함
