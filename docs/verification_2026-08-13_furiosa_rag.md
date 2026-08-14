# Furiosa RAG end-to-end verification

- Local FastAPI endpoint: `http://127.0.0.1:8002`
- Furiosa endpoint through SSH tunnel: `http://127.0.0.1:18001/v1`
- Model: `furiosa-ai/Qwen3-8B-FP8`
- Result: `llm.provider=furiosa`, `finish_reason=stop`, `reasoning_tokens=1`
- Retrieval: `bm25+tfidf-cosine`, keyword weight `0.55`, vector weight `0.45`
- Evidence: 3 official-source records returned, including Lam Selective Etch Product Family.
- Usage observed: prompt 547, completion 139, total 686 tokens. This is server-side inference usage, not a user OpenAI token charge.
- Evidence screenshot target: JSON fields `answer`, `evidence`, `retrieval`, and `llm.provider`.
- Quality follow-up: the answer included an interpretation about protecting adjacent structures; directly supported facts and interpretations must be separated in the final evaluation.
- Display issue: Korean text appeared as `?` in PowerShell output. Use Swagger UI or UTF-8 PowerShell settings for screenshots.

## Quality correction

The first generated answer said that SiGe removal is used to form an electrode structure. The supplied evidence supports only the narrower claim that SiGe removal is an application for GAA. The system prompt was tightened to prohibit unstated process purpose, sequence, mechanism, or structure-formation claims. Re-run the same query after the FastAPI reload and compare the answer.

Local verification note: a Codex-side compile/test attempt was blocked by the local `uv` cache permission error. The user-side API integration test itself completed successfully with `provider=furiosa` and `finish_reason=stop`.
