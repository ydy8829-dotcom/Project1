$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

# 최종 서비스 구성: Qwen3 생성 + Reranker 재순위화
$env:FURIOSA_BASE_URL = "http://127.0.0.1:18001/v1"
$env:FURIOSA_MODEL = "furiosa-ai/Qwen3-8B-FP8"
$env:FURIOSA_EMBED_BASE_URL = ""
$env:FURIOSA_EMBED_MODEL = ""
$env:FURIOSA_RERANK_BASE_URL = "http://127.0.0.1:18004/v1"
$env:FURIOSA_RERANK_MODEL = "furiosa-ai/Qwen3-Reranker-0.6B"

uv run --cache-dir .uv-cache --with-requirements requirements.txt uvicorn app.api.main:app --reload --reload-dir app --port 8002
