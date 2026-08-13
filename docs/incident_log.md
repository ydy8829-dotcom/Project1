# 오류·수정 기록(시말서)

## 2026-08-13 / 1차 실행 환경 오류

- 상황: `python` 및 `pytest` 명령을 직접 실행했으나 Windows 실행 환경에 Python 본체와 pytest 명령이 등록되어 있지 않아 테스트가 시작되지 않음.
- 원인: 프로젝트 가상환경이 아직 생성되지 않았고 WindowsApps 실행 별칭만 존재함.
- 조치: 프로젝트 내부 `.uv-cache`를 사용하도록 설정한 `uv run`으로 정적 컴파일과 테스트를 수행함.
- 재발 방지: README에 `uv run` 대체 실행법을 추가하고, 배포 전 `python -m compileall`과 pytest를 모두 실행한다.

## 2026-08-13 / 데이터 복사 경로 오류

- 상황: 수집 데이터 디렉터리를 처음 복사할 때 PowerShell `Copy-Item`의 `-LiteralPath` 인자에 원본과 목적지를 함께 전달하여 복사가 실패했고, 재시도 과정에서 중첩 디렉터리가 생성됨.
- 원인: `-Destination`을 명시하지 않은 경로 인자 사용.
- 조치: 올바른 목적지에 핵심 파일을 다시 복사하고 애플리케이션은 `data/metadata/documents.jsonl` 등 정규 경로만 사용하도록 고정함.
- 재발 방지: 데이터 경로를 실행 전 `Test-Path`로 확인하고 복사 명령에는 항상 `-Destination`을 명시한다.

## 2026-08-13 / 정규화 테스트 실패

- 상황: `AMAT plasma etch CD` 정규화 테스트에서 `critical dimension` 확장이 누락됨.
- 원인: 새 용어 사전 로더에 CD alias를 반영하지 않음.
- 조치: `critical dimension -> cd` 매핑을 추가.
- 상태: 수정 후 재검증 예정.

## 2026-08-13 / API 스모크 테스트 명령 오류

- 상황: pytest 통과 후 PowerShell 해시테이블 표현식을 Python `-c`의 JSON 인자로 직접 삽입해 Python SyntaxError가 발생함.
- 원인: 셸 문법과 Python 문법을 한 명령문 안에서 혼용함.
- 조치: JSON 문자열을 Python 코드 내부에서 직접 전달하는 방식으로 스모크 테스트를 재실행한다.
- 재발 방지: 복합 셸 명령 대신 별도 테스트 파일 또는 단순한 리터럴 JSON을 사용한다.

## 2026-08-13 / API 스모크 테스트 재시도 명령 오류

- 상황: 셸 인용부호가 다시 해석되어 Python 문자열의 URL·JSON 따옴표가 제거되고 SyntaxError가 재발함.
- 원인: PowerShell과 실행 도구의 다중 인용부호 처리 차이.
- 조치: 동일 검증을 재사용 가능한 pytest 케이스로 전환하고, 직접 명령 스모크 테스트 의존을 제거한다.
- 재발 방지: API 검증은 `pytest` 테스트 파일로 유지하고 셸에서는 단일 명령만 실행한다.

## 2026-08-13 / ingestion CLI import 오류

- 상황: `python scripts/ingest_documents.py` 실행 시 `ModuleNotFoundError: app` 발생.
- 원인: Python이 실행 파일 디렉터리인 `scripts`만 import 경로에 넣고 프로젝트 루트를 자동으로 넣지 않음.
- 조치: 스크립트 시작 시 프로젝트 루트를 `sys.path`에 추가.
- 재발 방지: CLI 스크립트는 프로젝트 루트에서 직접 실행하는 경우와 파일 경로 실행 모두를 테스트한다.

## 2026-08-13 / 제출 PPTX 텍스트 추출 오류

- 상황: PowerShell `Expand-Archive`가 `.pptx` 확장자를 직접 지원하지 않아 추출이 실패했고, 내부 slide XML 일부는 기존 인코딩/태그 손상으로 엄격한 XML 파싱도 실패함.
- 원인: PPTX는 ZIP 컨테이너이므로 `.zip` 복사본이 필요하며, 원본의 한국어 텍스트가 깨진 상태로 저장되어 있음.
- 조치: ZIP 복사본으로 컨테이너를 풀고 정규식 기반 텍스트 추출을 수행했다. 제출 요건은 `docs/process_record.md`에 재정리했다.
- 재발 방지: 원본 PPTX는 수정하지 않고, 제출용 PPT 생성 시 정상 UTF-8 텍스트를 새 슬라이드에 입력하며 원본은 참고자료로 보존한다.

## 2026-08-13 / Furiosa NPU 실측 환경 미확인

- 상황: 현재 개발 PC에서 `furiosa-llm`, `furiosa`, `npu-smi` 명령과 NPU serving port를 확인하지 못했다.
- 원인: Furiosa NPU 서버/SDK가 이 실행 환경에 연결되어 있지 않음.
- 조치: 실측 수치는 생성하지 않고, NPU 연결 후 기록할 필드와 단계만 `docs/process_record.md`에 정의했다.
- 재발 방지: NPU/GPU 성능 수치는 반드시 동일 모델·동일 프롬프트·동일 하드웨어 조건에서 실제 측정한 값만 PPT에 반영한다.

## 2026-08-13 / 자동 원격 실행 차단

- 상황: 자동으로 `ssh furiosa`를 실행해 NPU 모델 서버를 시작하려 했으나 현재 Codex 실행 환경에는 사용자의 SSH 별칭/설정이 전달되지 않아 `furiosa` 호스트를 해석할 수 없었다.
- 원인: 사용자의 PowerShell 세션과 Codex 도구 실행 환경이 서로 다른 SSH 설정·인증 컨텍스트를 사용함.
- 조치: 원격 서버에서 모델을 실행했다고 가장하지 않고 실행을 중단했다. 사용자 터미널에서 실행할 단일 명령을 제공해야 한다.
- 재발 방지: 원격 실행 전 `ssh -G furiosa`와 `ssh furiosa 'hostname'` 연결 검증을 통과한 뒤에만 모델 로딩 명령을 실행한다.

## 2026-08-13 / Qwen3 reasoning 토큰 고갈

- 상황: `/v1/chat/completions` 응답에서 `message.content`가 `null`이고 `reasoning`만 반환되며 `finish_reason=length`가 발생함.
- 원인: Qwen3 thinking 모드가 `max_tokens=300`을 reasoning에 모두 사용해 최종 답변을 생성할 토큰이 부족했음.
- 조치: 일반 RAG 답변 테스트에서는 질문 끝에 `/no_think`를 넣고, `max_tokens`를 500 이상으로 설정한다. 심층 추론 실험은 별도 실험으로 분리한다.
- 재발 방지: `content` null, `finish_reason=length`, reasoning token 비율을 API 후처리에서 검사하고 재시도 정책을 둔다.

## 2026-08-13 / 문서 근거 테스트의 해석 과잉

- 상황: 근거 주입 테스트는 성공했지만, 모델이 원문에 직접 없는 "게이트 구조 형성에 필요한 SiGe 층"이라는 설명을 추가함.
- 원인: 모델이 문서의 GAA·SiGe removal 관계를 일반 반도체 지식으로 확장 해석함.
- 조치: 최종 프롬프트에서 직접 근거와 해석을 분리하고, 문서에 없는 세부 공정 설명은 불확실성 표시를 붙이도록 수정할 예정.
- 재발 방지: citation accuracy와 unsupported claim rate를 별도 평가 지표로 측정한다.
