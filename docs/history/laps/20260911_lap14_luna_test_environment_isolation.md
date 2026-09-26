# 2026-09-11 | lap 14 | pytest LOOP_* 환경 격리 수리

- 실제 provider/model/effort / 지정 역할: Codex work tier, 계약상 `gpt-5.6-luna`/high hands-on 구현.
- 가설 / 사용자 관찰: 부모 세션의 `LOOP_MIDDLE_PROVIDER=claude` 상속이 routing 회귀를 오염시키므로,
  pytest autouse fixture가 모든 상속 `LOOP_*`를 제거하면 저장소 기본값과 테스트별 override가 분리된다.
- 예상 PASS / FAIL 조건: `PATH`는 유지되고 명시 `env` override는 살아 있어야 한다. targeted/combined/
  전체 Fast 및 safety가 PASS해야 하며, raw exit75는 worker 2회·middle 0회·marker 없음·fail-streak
  STOP·최종 nonzero여야 한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `tests/conftest.py` 신규 추가, SHA256 `b992731fc87c3f4b923af1f3fa51f653c8749ec978d0eff300c27bf17a9dd440`.
  기존 `tests/test_model_routing.py` SHA256 `abbcd69cea46336751592b9b9cc8508802b2ec4faf991aebc81d6c649b43d137` 유지.
  커밋 없음, `LOOP_ALLOW_COMMITS=0`, unborn HEAD.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 게임 EXE/DLL 미실행.
  테스트는 private copy와 fake Codex/Claude 실행 파일을 사용했고, 부모 환경에는
  `LOOP_MIDDLE_PROVIDER=claude`, `LOOP_JUDGE=claude`, `LOOP_ENABLE_AGENT=1`이 존재했다.
  활성 플레이어/지도/군대 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  1. `.venv/bin/python -m pytest -q tests/test_model_routing.py` → `17 passed in 6.94s`.
  2. `.venv/bin/python -m pytest -q tests/test_patch_loop.py` → `9 passed in 3.66s`.
  3. `.venv/bin/python -m pytest -q tests/test_model_routing.py tests/test_patch_loop.py` →
     `26 passed in 9.66s`.
  4. `make check` → `84 passed`, ruff PASS, compileall PASS, mypy PASS, `CONTEXT_PASS`.
  5. `checks/safety.sh check` → `SAFETY_PASS`.
  raw exit75 로그는 pytest private fixture의 보존 로그
  `/tmp/pytest-of-dev_00/pytest-272/test_raw_worker_exit75_without1/patch/logs/loop-2026-09-11.log`에
  남았고, lap1/lap2 각각 `exit=75`, `연속 실패 1/2`, `연속 실패 2/2`, `이유=fail-streak` 및
  `LOOP DOWN`을 실제 확인했다. calls는 `codex` 2회, middle 0회, `loop/ESCALATE_SOL` 없음,
  `loop/STOP` 생성, `max-laps(2)` 없음이었다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): targeted PASS, adjacent PASS, combined PASS,
  전체 Fast PASS, safety PASS. raw exit75 계약 PASS. fixture는 합성 private loop fixture이며
  실제 게임 증거가 아니다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: `loop/loop.sh`, `loop/env.sh`,
  `loop/env.local.sh`, 기대값은 변경하지 않았다. G1~G4 및 사용자 마일스톤 승인 없음.
  다음 middle 세션의 독립 검수 전에는 work 결과를 최종 승인으로 승격하지 않는다.
- 다음 한 가지: 새 Sol/Opus5 middle 세션이 `tests/conftest.py`의 격리 범위, 위 Fast 수치,
  raw exit75 실제 로그와 원본/후보 SHA를 독립 확인한 뒤 G1-A 재개 여부를 판정한다.
