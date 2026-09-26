# 2026-09-25 | lap 618 | 목표 G4

- 실제 provider/model/effort / 지정 역할: Codex native hands-on work session; exact model/effort 비노출 / 일반 작업자.
- 가설 / 사용자 관찰: `g1-baseline` provenance allowlist에 `INMM_AI_SHADOW`와 private shadow JSONL의 검증된 path/SHA/row count를 추가하면 W1R의 shadow 활성화 근거를 fail-closed로 보존할 수 있다.
- 예상 PASS / FAIL 조건: 활성 private JSONL은 env=`1`, private path, 존재, 유효 JSONL, SHA, row count가 모두 기록되어 PASS; 비활성·missing·empty·외부 symlink는 PASS로 승격되지 않음. 필수 Fast가 실패하면 `BLOCKED`로 승격하고 재시도하지 않음.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): `tools/runtime_env.py` SHA `42aeff7779e454d5d6c2ceb73256735e91369e6cab94b94c87dcdf553e04833a`; `tests/test_runtime_env.py` SHA `7030dd1f8bca3329b79f8c37a781a2dffe4aac2e7cfd1ca67f6f5b5101f364cd`; `docs/STATUS.md`, `loop/ESCALATE_SOL`; 커밋 없음/uncommitted.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본·후보 EXE/DLL 변경 없음, candidate SHA 없음. 게임/runtime 미실행, 활성 플레이어·지도·군대 없음. fixture는 `tmp_path` 아래 synthetic JSONL 2행, disabled/missing/empty/symlink cases뿐이며 제품 fixture가 아님.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `.venv/bin/python -m pytest -q tests/test_runtime_env.py -k g4_shadow_provenance` → 5 passed; `.venv/bin/python -m pytest -q tests/test_runtime_env.py tests/test_runtime_guards.py` → 165 passed; `bash checks/safety.sh check` → `SAFETY_PASS`; `.venv/bin/python -m ruff check tools/runtime_env.py tests/test_runtime_env.py` → PASS; `make check` → tests 851 passed/502.04s, Ruff/compileall PASS, mypy exit2 at `tools/runtime_env.py:7935-7936`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): 구현·targeted 회귀는 PASS. 필수 `make check`는 mypy `Value of type "object" is not indexable` 2건으로 **BLOCKED(typecheck)**. 게임0, raw/backfill0, bridge/제품 수정0, 커밋0.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 새 provenance helper는 활성 env/path/SHA/row-count 및 비활성·missing·empty·외부 symlink을 잠근다. mypy 오류가 남아 전체 검증 완료가 아니며, next middle/승격 작업자가 타입을 좁힌 뒤 targeted·safety·전체 Fast를 독립 검수해야 한다. G4 PASS/FEASIBLE_BASELINE·사용자 승인은 없음.
- 다음 한 가지: `tools/runtime_env.py:7935-7936` 타입 오류를 fail-closed 의미 변경 없이 수리하고 전체 Fast를 새로 실행한다. 그 전 게임 실행·raw backfill·bridge/제품 AI 변경·G4 승격 금지.
