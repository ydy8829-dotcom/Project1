# 오류 기록: PowerShell 스크립트 실행 정책 차단

## 발생 상황

최종 FastAPI 실행 스크립트 `scripts/start_final_api.ps1` 실행 시 `PSSecurityException`이 발생했다.

## 원인

Windows PowerShell의 실행 정책이 로컬 `.ps1` 스크립트 실행을 차단하고 있다. 스크립트 내용이나 FastAPI 코드 오류가 아니다.

## 조치

전체 시스템 정책을 변경하지 않고 현재 실행에만 우회 옵션을 적용한다.

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start_final_api.ps1
```

## 보안 판단

`Set-ExecutionPolicy -Scope LocalMachine` 같은 영구 정책 변경은 하지 않는다. 프로젝트 실행 1회에 한정된 우회만 사용한다.

## 상태

FastAPI의 기존 프로세스 종료는 정상 완료되었으며, 위 명령으로 최종 Qwen3+Reranker 구성을 다시 시작할 수 있다.
