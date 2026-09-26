# 2026-09-11 | lap 15 | pytest LOOP_* 환경 격리 독립 컨펌

- 실제 provider/model/effort / 지정 역할: Codex `gpt-5.6-sol`/high, middle 독립 검수. 게임 코드·하네스 hands-on 수정 없음.
- 가설 / 사용자 관찰: lap14의 autouse fixture가 부모 `LOOP_*`만 제거하면 저장소 기본 routing과 테스트별 명시 override가 분리되고, controller 반환코드 수리의 요구 게이트가 clean routing에서 재현된다.
- 예상 PASS / FAIL 조건: source SHA 일치, `PATH` 유지와 테스트별 override 유효, targeted 17/combined 26/Fast 84/safety PASS, raw exit75가 worker 2회·middle 0회·marker 없음·STOP·최종 nonzero·fail-streak 종료이면 CONFIRM. 하나라도 다르면 재시도·게임 실행 없이 승격.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 구현 변경 없음. 판정 기록으로 `docs/STATUS.md`, `docs/work/active/LOOP_ESCALATION_RETURN_CODE_REPAIR.md`, 이 파일을 갱신하고 소진된 `loop/ESCALATE_SOL`은 아래 원문을 보존한 뒤 제거. 검수 시작 SHA256은 `tests/conftest.py` `b992731fc87c3f4b923af1f3fa51f653c8749ec978d0eff300c27bf17a9dd440`, `tests/test_model_routing.py` `abbcd69cea46336751592b9b9cc8508802b2ec4faf991aebc81d6c649b43d137`, `loop/loop.sh` `c272af40b02b8fede480d52baa22cf790fcf8d21cf3a1cb8e630b1c60bb4d974`, lap14 기록 `ed449a5523e2400a2d83cd07772f5d632f8946468ed56a6cdb95bbd5d075dddb`, 제거 전 marker `0c7ff2016ee8c2f05cfa429b5d1a967a8fbf98814a07f47772aa877173b5b79a`. 갱신 후 `docs/STATUS.md`는 `5aab8e999d9cc1d4f8084bbf025df308c1f21f77d4cf3118af12f52031b5d043`, 수리 카드는 `f48c9f3792f4fa4d43a0c2bcc9824eb1022be1a5bc81d4e96deb470e1bbd1164`. 커밋 없음/unborn HEAD, `LOOP_ALLOW_COMMITS=0`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 게임 EXE/DLL과 원본 미실행·무변경. 부모 환경에 16개 `LOOP_*` 이름이 존재한 상태에서 pytest private copy와 fake Codex/Claude를 사용했다. 활성 플레이어/지도/군대 없음; 실제 게임 증거가 아닌 합성 loop fixture다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `env | sed ... | sort`; `rg -n "os\\.environ|LOOP_|PATH" tests --glob '*.py'`; `.venv/bin/python -m pytest -q tests/test_model_routing.py`; `.venv/bin/python -m pytest -q tests/test_model_routing.py tests/test_patch_loop.py`; `make check`; `checks/safety.sh check`; 최신 raw 파일과 상태를 `sha256sum`/`wc`/`rg`/`test -f`로 확인. raw log `/tmp/pytest-of-dev_00/pytest-277/test_raw_worker_exit75_without1/patch/logs/loop-2026-09-11.log` SHA256 `be1152f914f909ed4256c2584da7a0ed7d64df4ab6b18bee074413340f372452`, calls SHA256 `7cba680c740c1472e4ec5ea7357bd322c1cfe08b147b5b6ced7a62384ff2fbbf`. 캡처 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): source SHA PASS. fixture는 `LOOP_*`만 제거하고 `PATH`는 보존하며 각 테스트가 subprocess env override를 제거 후 다시 주입함을 정적 확인. targeted `17 passed in 5.86s`; combined `26 passed in 9.50s`; Fast `84 passed in 10.59s`, Ruff/compileall/mypy 8 files/`CONTEXT_PASS`; safety `SAFETY_PASS`. raw calls는 Codex work 정확히 2줄, Claude/middle 0회, lap1/lap2 `exit=75`, `연속 실패 1/2`·`2/2`, `이유=fail-streak`, STOP 존재, marker 및 max-laps terminal 없음. 최종 exit1은 통과한 회귀의 명시 assertion으로 재확인. **CONFIRMED**.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: controller와 테스트 환경 격리 수리의 2단 기술 컨펌만 완료. G1~G4 판정 변화와 사용자 마일스톤 승인 없음. 실제 PS7→PS3, G1 입력 5종, 출력 2배는 계속 미검증이며 게임은 이번 세션에서 SKIP.
- 다음 한 가지: 새 Codex `gpt-5.6-luna`/high work가 `docs/work/active/G1_A_EXECUTION_CARD.md`의 현행 범위대로 중단 run의 미승인 하네스 제안을 검토·소유하고 targeted Fast/`make check` PASS 뒤 새 격리 원본 run 1회만 수행한다. 필수 게이트나 run 실패 시 재시도하지 않고 증거와 marker를 남긴다.

## 소진 전 `loop/ESCALATE_SOL` 원문

```text
lap=14
reason=work_tier_test_environment_isolation_repair_complete_middle_review_required
role_requested=Fresh Codex gpt-5.6-sol/high or Claude Code claude-opus-5/high middle independent confirmation
required=Review tests/conftest.py autouse removal of inherited LOOP_* only; confirm PATH and per-test env overrides remain effective. Independently verify targeted 17 pass, combined model-routing+patch-loop 26 pass, make check 84 pass with ruff/compileall/mypy/context pass, checks/safety.sh check SAFETY_PASS, and raw worker exit75 fail-streak evidence: worker 2 calls, middle 0, no marker, STOP, final nonzero, no max-laps termination. Do not run the game or resume G1-A until this review is complete.
evidence=tests/conftest.py SHA256 b992731fc87c3f4b923af1f3fa51f653c8749ec978d0eff300c27bf17a9dd440; loop/loop.sh SHA256 c272af40b02b8fede480d52baa22cf790fcf8d21cf3a1cb8e630b1c60bb4d974 unchanged; tests/test_model_routing.py SHA256 abbcd69cea46336751592b9b9cc8508802b2ec4faf991aebc81d6c649b43d137 unchanged from lap12. Raw log: /tmp/pytest-of-dev_00/pytest-272/test_raw_worker_exit75_without1/patch/logs/loop-2026-09-11.log.
preserve=No commit, no game execution, no G1-G4 status promotion. Preserve tests/conftest.py, lap14 history, STATUS, and this marker for middle review.
```
