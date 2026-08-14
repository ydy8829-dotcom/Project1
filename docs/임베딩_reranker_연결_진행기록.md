# 임베딩·reranker 연결 진행 기록

## 2026-08-14 현재 상태

- 생성 모델 연결: Furiosa Qwen3-8B-FP8 완료
- 임베딩 클라이언트: 구현 완료, OpenAI 호환 `/v1/embeddings` 사용
- reranker 클라이언트: 구현 완료, Furiosa `/v1/rerank` 사용
- FastAPI health 응답에 임베딩·reranker 설정 상태를 표시하도록 확장
- 임베딩 서버가 설정되면 BM25 + 임베딩 cosine 방식으로 자동 전환
- 임베딩 서버가 없으면 기존 BM25 + TF-IDF cosine 방식으로 안전하게 fallback
- reranker 서버가 설정되면 1차 검색 후보를 reranker 점수로 재정렬
- 기존 테스트 4개 통과
- 임베딩·reranker 실제 NPU 서버 기동 및 전후 성능 비교는 원격 서버 확인 후 진행 예정

### 원격 서버 확인 결과

- Qwen3 서버 프로세스: `3378393`
- 실행 모델: `furiosa-ai/Qwen3-8B-FP8`
- 원격 포트: `8001`
- 사용 장치: `npu0~npu7`의 전체 코어
- `furiosa-llm serve`가 `--devices`, `--data-parallel-size`, `--tensor-parallel-size` 옵션을 지원함

현재 Qwen3 서버가 전체 NPU를 점유하므로, 임베딩·reranker를 추가로 실행하기 전에 장치 분할 또는 순차 검증이 필요하다. 현재 생성 서버를 유지한 상태에서 새 모델을 바로 실행하지 않는다.

### 임베딩 API 검증 결과

- 모델: `furiosa-ai/Qwen3-Embedding-0.6B`
- 원격 포트: `8003`
- 로컬 터널 포트: `18003`
- `/v1/embeddings` 호출: 성공
- 입력 2개에 대해 embedding 벡터 2개 반환: 성공
- 사용량: `prompt_tokens=18`, `total_tokens=18`

이 결과로 임베딩 서버와 OpenAI 호환 API 자체는 정상임을 확인했다.

### FastAPI 임베딩 연결 결과

- FastAPI 포트: `8002`
- `embedding_configured: true`: 성공
- 연결 모델: `furiosa-ai/Qwen3-Embedding-0.6B`
- 생성 모델: 현재 미연결 상태
- reranker: 현재 미연결 상태
- 확인 방법: `GET /health`

임베딩 모델이 FastAPI 설정에 반영되었으므로 다음 단계는 실제 질의에서 `bm25+embedding-cosine` 검색 방식이 사용되는지 확인하는 것이다.

### 실제 임베딩 검색 확인

- FastAPI `/api/v1/query` 호출: 성공
- 검색 방식: `bm25+embedding-cosine`
- 임베딩 벡터 기반 검색이 RAG Gateway에 반영됨: 성공
- 생성 Qwen3는 해당 단계에서 중단 상태였으며, 답변 생성이 아닌 검색 계층만 검증함

다음은 reranker 단독 검증이다. NPU 자원 충돌을 피하기 위해 임베딩 서버를 종료한 뒤 reranker를 순차적으로 기동한다.

### Reranker 단독 검증 결과

- 모델: `furiosa-ai/Qwen3-Reranker-0.6B`
- 원격 포트: `8004`
- 로컬 터널 포트: `18004`
- FastAPI `reranker_configured=true`: 성공
- 질의 결과에서 Lam Selective Etch 문서가 1위로 반환됨: 확인
- 후속 보완: API evidence에 rerank 점수와 처리 주체가 표시되도록 수정함

### Reranker 재검증 결과

- `retriever: furiosa-reranker`: evidence 3건에서 확인
- `rerank_score`: 반환 확인
- retrieval method: `bm25+tfidf-cosine+reranker`
- 1위 문서: `Selective Etch Product Family`
- 주의: 세 문서의 rerank 점수가 모두 0.998 이상으로 높았다. API 연결과 순위 재정렬은 확인했지만, 점수의 변별력과 실제 Top-3 개선 효과는 50문항 평가로 별도 측정해야 한다.

## 원격 서버에서 확인해야 할 정보

현재 Qwen3 생성 서버가 여러 NPU를 사용하는지 확인해야 한다. 생성 서버를 유지한 채 임베딩·reranker를 동시에 기동하면 NPU 자원 충돌이 발생할 수 있으므로, 다음 결과를 확인하기 전에는 새 모델 서버를 실행하지 않는다.

```bash
furiosa-smi ps
furiosa-llm serve --help
```

확인할 항목:

- 현재 Qwen3 서버가 사용하는 NPU 수
- `--devices`, `--data-parallel-size` 옵션 지원 여부
- 임베딩·reranker를 별도 장치에 배치할 수 있는지
- 서버 포트를 별도로 지정할 수 있는지

## 예정 포트

```text
생성 Qwen3 서버:       원격 8001 → 로컬 18001
임베딩 서버:           원격 8003 → 로컬 18003
reranker 서버:         원격 8004 → 로컬 18004
FastAPI RAG:           로컬 8002
```

단, 원격 서버의 기존 프로세스와 사용 가능한 NPU를 확인한 뒤 실제 포트를 확정한다.

## 설계 원칙

- 새 모델 서버가 꺼져 있어도 기존 RAG가 중단되지 않아야 한다.
- 임베딩·reranker 적용 전후 동일한 평가셋으로 비교한다.
- 최종 PPT에는 검색 방법, 모델명, 포트, Top-3·MRR·nDCG@3를 함께 기록한다.
