# 검색 성능 비교표

| 지표 | 기준선(BM25+TF-IDF) | Embedding 적용(BM25+Embedding) | Reranker 적용(BM25+TF-IDF+Reranker) |
|---|---:|---:|---:|
| Top-1 정확도 | 6% | 18% | 90% |
| Top-3 정확도/Recall@3 | 38% | 68% | 92% |
| MRR | 0.2919 | 0.4242 | 0.9117 |
| 평균 nDCG@3 | 0.2406 | 0.4427 | 0.8994 |

## 평가 조건

- 평가 문항: 50문항
- 기준선: BM25 + TF-IDF cosine
- 비교군: BM25 + Qwen3-Embedding-0.6B cosine
- Reranker: 미적용
- Reranker 적용군: Qwen3-Reranker-0.6B 단독 재순위화
- 평가셋 상태: 합성 seed 데이터이며 도메인 전문가 검토 필요
