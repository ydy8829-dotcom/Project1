# Retrieval evaluation — 2026-08-13

## Automated execution

```powershell
$env:UV_CACHE_DIR=(Join-Path (Get-Location) '.uv-cache')
uv run --no-project --with rank-bm25 python scripts\evaluate_retrieval.py
```

The script creates `data/evaluation/evaluation_set.jsonl` with 50 deterministic seed questions and writes detailed results to `data/evaluation/retrieval_results.json`.

## Current baseline

| Metric | Result |
|---|---:|
| Dataset size | 50 |
| Top-1 accuracy | 6% |
| Top-3 accuracy | 38% |
| MRR | 0.2919 |
| Retrieval | BM25 + TF-IDF cosine |
| Keyword/vector weight | 0.55 / 0.45 |

The target is Top-3 accuracy >= 80%. The current result does not meet the target.

## Interpretation

The first run was 20% Top-3. Adding title, company, process, product, application, device-structure, and technology-keyword metadata to the search index raised it to 38%. The remaining gap is expected because the seed questions are synthetic and some cross-document questions have overlapping valid sources. These labels must be reviewed by a semiconductor-domain reviewer before using the score as a final project claim.

## Next improvement

Tune query normalization and retrieval weights, add a real reranker, and replace or review the synthetic labels. Report both the unreviewed seed score and the reviewed benchmark score in the final PPT.
