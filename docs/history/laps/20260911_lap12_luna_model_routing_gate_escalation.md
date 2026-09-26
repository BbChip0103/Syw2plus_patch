# 2026-09-11 | lap 12 | model-routing 회귀 게이트 환경 충돌 승격

- 실제 provider/model/effort / 지정 역할: Codex work 세션; 저장소 계약상 Codex `gpt-5.6-luna`/high 실무 역할. 현재 대화 모델의 실제 ID는 노출되지 않음.
- 가설 / 사용자 관찰: lap11 handoff의 raw worker `exit75` fail-streak 회귀를 `tests/test_model_routing.py`에 추가하면 `LOOP_MAX_FAIL_STREAK=2`에서 STOP/nonzero 계약을 측정할 수 있다. 기존 테스트 두 개는 유지한다.
- 예상 PASS / FAIL 조건: 새 테스트는 worker 2회, middle 0회, marker 없음, `연속 실패 1/2`, `연속 실패 2/2`, `이유=fail-streak`, `STOP`, 최종 exit1을 확인해야 한다. targeted 전체는 PASS해야 한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): `tests/test_model_routing.py`에 `test_raw_worker_exit75_without_marker_hits_fail_streak_stop`만 추가했다. 커밋 없음/unborn HEAD. 후보 SHA256 `tests/test_model_routing.py`=`abbcd69cea46336751592b9b9cc8508802b2ec4faf991aebc81d6c649b43d137`; `loop/loop.sh`=`c272af40b02b8fede480d52baa22cf790fcf8d21cf3a1cb8e630b1c60bb4d974`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 게임 원본/후보 EXE는 실행하지 않았다. 격리 pytest 프로젝트와 fake Codex worker를 사용했다. 호출 환경에는 `LOOP_MIDDLE_PROVIDER=claude`, `LOOP_JUDGE=claude`, `LOOP_ENABLE_AGENT=1`이 상속되어 있었다. 실제 플레이어/지도/군대 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `.venv/bin/python -m pytest -q tests/test_model_routing.py`; 캡처 없음. 결과 `1 failed, 16 passed in 5.98s`. 실패는 기존 `test_codex_roles_have_fixed_model_and_high_effort`의 middle parameter이며 Claude middle command가 관측됐다. 새 회귀를 포함한 targeted gate가 필수 실패했으므로 인접/전체 Fast는 실행하지 않았다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): 새 회귀 포함 targeted gate **FAIL**. 실패 출력은 기대한 `-m gpt-5.6-sol -c model_reasoning_effort=high` 대신 `claude --print --model claude-opus-5 --effort high`를 기록했다. 환경 상속만의 문제인지 테스트 격리 결함인지는 **UNKNOWN**.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 기대값을 낮추거나 재시도하지 않았다. `loop/ESCALATE_SOL`에 middle handoff를 보존했다. 게임/G1-A는 실행하지 않았고, G1~G4 판정·사용자 승인 없음.
- 다음 한 가지: 새 Sol/Opus5 middle 세션이 환경 상속 원인과 테스트 격리 계약을 독립 판정하고, 명시적 clean routing 환경의 재검증 여부를 정한다. 그 전에는 인접/전체 Fast나 G1-A를 진행하지 않는다.
