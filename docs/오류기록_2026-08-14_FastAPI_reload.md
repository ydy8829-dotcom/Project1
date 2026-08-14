# FastAPI 재시작 반복 및 환경변수 미적용 기록

## 증상

- FastAPI 8002 자체는 정상 기동했다.
- `WatchFiles detected changes`가 반복되며 서버가 여러 번 재시작됐다.
- `.uv-cache` 내부 파일 변경도 reload 원인으로 감지됐다.
- `/health`에는 기존 Qwen 설정이 남고 임베딩 설정이 적용되지 않았다.

## 원인

- `--reload` 감시 범위에 프로젝트 내부 `.uv-cache`가 포함됐다.
- `$env:` 환경변수는 입력한 PowerShell 창에만 적용되는데, FastAPI를 실행한 창에 임베딩 환경변수를 설정하지 않았다.

## 조치

- FastAPI 창에서 `Ctrl+C`로 완전히 종료한다.
- 같은 창에서 환경변수를 다시 설정한다.
- `--reload-dir app`으로 애플리케이션 코드만 감시한다.

## 재발 방지 실행 명령

```powershell
cd "C:\Users\ydy00\OneDrive\Desktop\ai 프로젝트\260813_자료수집\Project1"
$env:FURIOSA_BASE_URL=""
$env:FURIOSA_EMBED_BASE_URL="http://127.0.0.1:18003/v1"
$env:FURIOSA_EMBED_MODEL="furiosa-ai/Qwen3-Embedding-0.6B"
$env:FURIOSA_RERANK_BASE_URL=""
uv run --with-requirements requirements.txt uvicorn app.api.main:app --reload --reload-dir app --port 8002
```
