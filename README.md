# Semiconductor Equipment Technical RAG Copilot MVP

현재 구현은 `data/metadata/documents.jsonl`의 15개 공식 seed 문서를 자동 로드한다. 검색은 BM25와 경량 TF-IDF cosine 점수를 결합하며, 외부 LLM 없이 근거 문장을 그대로 제시하는 오프라인 MVP다.

## 실행

```powershell
uv run --with-requirements requirements.txt uvicorn app.api.main:app --reload
uv run --with-requirements requirements.txt streamlit run app/ui/streamlit_app.py
uv run --with-requirements requirements.txt pytest -q
```

`uv`가 없다면 Python 3.11+ 가상환경을 만든 뒤 `pip install -r requirements.txt`를 실행한다.

## API

- `GET /health`
- `GET /api/v1/documents`
- `POST /api/v1/query` — `{ "question": "...", "top_k": 5 }`
- `POST /api/v1/ingest` — metadata JSONL 재로드

답변은 검색 근거가 있을 때만 생성되며, 수치 사양·Service Manual·비공개 문서를 추정하지 않는다. 오류 기록은 `docs/incident_log.md`에 남긴다.

Applied Materials·Lam Research 공식 공개자료를 대상으로 Etch 공정장비 질의응답을 수행하는 학습·개발용 Scaffold입니다.

## 빠른 시작

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python scripts\ingest_documents.py
uvicorn app.api.main:app --reload
```

다른 PowerShell 창에서:

```powershell
streamlit run app\ui\streamlit_app.py
pytest -q
```

## 별도 수집 데이터셋 연결

실제 데이터셋은 이 프로젝트에 포함하지 않습니다. 별도 수집한 데이터셋을 그대로 보관하고 다음처럼 경로를 지정해 적재합니다.

```powershell
python scripts\ingest_documents.py --input-dir "D:\datasets\semiconductor_docs" --output-dir data\processed
```

경로를 지정하지 않으면 기본값 `data/raw`를 사용합니다. 원본 데이터셋은 저작권·용량·보안 문제로 Git에 커밋하지 마세요. 현재 API와 UI의 샘플 fixture는 실행 확인용이며 실제 데이터 적재 후 인덱스 연결이 필요합니다.

## 주의

이 프로젝트는 공개 문서 기반 검색 보조 도구입니다. 실제 장비의 안전·정비 절차를 대신하지 않으며, 근거 없는 사양을 생성하지 않도록 설계합니다.
