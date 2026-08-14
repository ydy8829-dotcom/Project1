# Scaffold 설계서

## 1. 아키텍처

```text
PDF/HTML
  ↓
Loader → Metadata → Chunker → JSONL
                                  ↓
                    BM25 Index + Vector Index
                                  ↓
Question → Normalizer → Hybrid Retriever → Reranker
                                  ↓
                         Evidence-first Generator
                                  ↓
                    FastAPI / Streamlit / Evaluation
```

## 2. 폴더 구조

```text
semiconductor_rag_copilot/
├─ app/
│  ├─ api/main.py
│  ├─ api/routes/query.py
│  ├─ core/config.py
│  ├─ ingestion/pdf_loader.py
│  ├─ ingestion/chunker.py
│  ├─ normalization/query_normalizer.py
│  ├─ retrieval/bm25_retriever.py
│  ├─ retrieval/hybrid_retriever.py
│  ├─ rag/answer_generator.py
│  └─ ui/streamlit_app.py
├─ data/raw/ data/processed/ data/evaluation/
├─ scripts/ingest_documents.py
├─ tests/
├─ PRD.md SCAFFOLD.md README.md
├─ requirements.txt .env.example
└─ pyproject.toml
```

`data/raw`는 사용자가 별도로 수집한 데이터셋을 연결하는 위치다. 원본 데이터셋은 Git에 커밋하지 않으며 `.env`의 `DATASET_ROOT` 또는 `--input-dir`로 다른 위치를 지정할 수 있게 한다.

## 3. 모듈 책임

| 모듈 | 책임 |
|---|---|
| ingestion | PDF/HTML 파싱, 청킹, 메타데이터 생성 |
| normalization | 반도체 용어·제조사·약어 정규화 |
| retrieval | BM25, 벡터, 하이브리드 검색 |
| rag | context 제한 답변, 인용 검증 |
| api | 외부 질의·헬스체크·문서 API |
| ui | 검색·필터·근거 시각화 |
| evaluation | 50문항 및 검색·답변 지표 |

## 4. 데이터 스키마

문서: `document_id, title, manufacturer, product_family, product_name, process, document_type, source_url, local_path, content_hash, collected_at`

청크: `chunk_id, document_id, chunk_index, text, page_number, section_title, manufacturer, product_name, process, source_url`

평가: `question_id, question, question_type, expected_documents, expected_keywords, expected_answer, source_url, page_number`

## 5. 질의 흐름

1. 질문 원문 저장
2. 제조사·제품·공정·약어 추출
3. 동의어 확장
4. BM25 및 벡터 검색
5. 점수 정규화·결합
6. top-k 근거 구성
7. LLM 또는 MOCK 답변 생성
8. 인용 검증
9. 답변·근거·신뢰도 반환

## 6. 초기 환경변수

`APP_ENV`, `MOCK_LLM`, `EMBEDDING_PROVIDER`, `LLM_PROVIDER`, `OPENAI_API_KEY`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST`, `HYBRID_KEYWORD_WEIGHT`, `HYBRID_VECTOR_WEIGHT`

## 7. 데이터셋 연결 방식

```powershell
python scripts\ingest_documents.py --input-dir "D:\datasets\semiconductor_docs" --output-dir data\processed
```

PDF·HTML·CSV·Excel 등 실제 데이터 형식에 맞는 loader를 연결한다. 원본 파일은 프로젝트에 복사하지 않고 경로·해시·메타데이터만 기록한다.

## 8. 실행 단계

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts\ingest_documents.py --input-dir "D:\datasets\semiconductor_docs"
uvicorn app.api.main:app --reload
streamlit run app\ui\streamlit_app.py
pytest -q
```
