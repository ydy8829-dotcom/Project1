# NPU 장치 사용 정책

앞으로 이 프로젝트는 `npu4`, `npu5`, `npu6`, `npu7` 범위 안에서 사용합니다. 한 모델을 실행할 때 네 장치를 모두 지정하지 않고, 모델별로 필요한 장치만 지정합니다.

- 사용 가능 범위: `npu4~npu7`
- 미사용 장치: `npu0~npu3`
- `furiosa-llm serve` 실행 시 반드시 `--devices`를 명시합니다.
- 자동으로 사용 가능한 전체 NPU를 선택하게 두지 않습니다.
- 실행 전 `furiosa-smi ps`로 실제 점유 장치를 확인합니다.

## 기본 실행 원칙

모델 하나를 한 장치에 먼저 배정합니다.

```bash
--devices npu:4
```

예정 배정은 다음과 같습니다.

```text
Qwen3 생성 모델: npu4
Embedding 모델:  npu5
Reranker 모델:   npu6
예비:            npu7
```

단, 모델 기동 시 메모리·병렬 설정 오류가 발생하면 해당 모델에 한해 `npu4,npu5`처럼 범위를 넓혀 다시 검증합니다.

## Qwen3 실행 예시

```bash
furiosa-llm serve furiosa-ai/Qwen3-8B-FP8 \
  --port 8001 \
  --devices npu:4
```

Embedding과 Reranker는 각각 `npu5`, `npu6`에 배정해 동시 실행을 시도합니다. 모델이 단일 장치에서 실행되지 않으면 필요한 최소 장치 수를 확인한 후 배정을 조정합니다.

## 확인 명령

```bash
furiosa-smi ps
```

출력에 프로젝트 프로세스가 `npu4`~`npu7`만 사용하는지 확인합니다.
