# 2026-09-25 | lap 619 | 목표 G4

- 실제 provider/model/effort / 지정 역할: Codex native, exact model/effort 비노출 / middle(진단·계획·확인).
- 가설 / 사용자 관찰: lap618 W1P의 provenance 계약은 의도대로 fail-closed이고, 남은 mypy 2건은 동작 결함이 아니라 이질적 `provenance` dict의 지역 타입 추론 문제다.
- 예상 PASS / FAIL 조건: 코드·회귀·카드 범위가 일치하고 targeted/safety가 통과하며 mypy가 동일 두 줄만 재현되면 `ACCEPT(scope/logic) / BLOCKED(typecheck)`; 다른 실패나 의미 변경이 있으면 REJECT.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 게임/제품/하네스 source·binary·raw 변경 0. 이 기록, `docs/STATUS.md`, `loop/ESCALATE_SOL` §169만 문서 변경. 진입 validation fingerprint `1fe8f8b0d91f1fc22b283442acaf122c68885482`; `tools/runtime_env.py` SHA `42aeff7779e454d5d6c2ceb73256735e91369e6cab94b94c87dcdf553e04833a`, `tests/test_runtime_env.py` SHA `7030dd1f8bca3329b79f8c37a781a2dffe4aac2e7cfd1ca67f6f5b5101f364cd`; 커밋 없음/uncommitted.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본·후보 EXE/DLL 및 게임 미실행, 활성 플레이어·지도·군대 없음. 검수 fixture는 `tmp_path` synthetic JSONL 활성 2행과 disabled/missing/empty/external-symlink cases.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `.venv/bin/python -m pytest -q tests/test_runtime_env.py -k g4_shadow_provenance` → 5 passed; `.venv/bin/python -m pytest -q tests/test_runtime_env.py tests/test_runtime_guards.py` → 165 passed/1.57s; `bash checks/safety.sh check` → `SAFETY_PASS`; Makefile과 동일한 10-file mypy 명령 → `runtime_env.py:7935-7936` 2 errors/exit1; `.venv/bin/python checks/context_limits.py` → `CONTEXT_PASS`. 캡처 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): 카드 범위·파일 SHA·환경 allowlist·private-prefix/symlink/missing/empty/SHA/row-count 계약을 대조해 **ACCEPT(scope/logic) / BLOCKED(typecheck)**. `provenance`가 이질적 dict라 `provenance["g4_ai_shadow"]`가 `object`로 추론되는 것이 직접 원인이다. Fast 완료·G4 `FEASIBLE_BASELINE`·제품 PASS 아님.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: targeted와 safety는 새로 통과했으나 전체 Fast는 알려진 mypy blocker 때문에 재실행하지 않았다. 다음 work는 helper 결과를 `dict[str, Any]` 지역 변수로 한 번만 받아 provenance 기록과 verdict가 같은 값을 참조하게 하고, fail-closed 식과 5개 회귀를 그대로 유지해야 한다. 사용자 승인 없음.
- 다음 한 가지: work tier가 위 최소 타입 수리 후 targeted pytest·safety·`make check`를 새로 완주한다. 그 전 게임/runtime probe·raw backfill·bridge/제품 AI 변경·fresh 예산 개방 금지.
