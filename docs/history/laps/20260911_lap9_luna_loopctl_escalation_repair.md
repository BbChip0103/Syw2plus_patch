# 2026-09-11 | lap 9 | loop escalation 반환코드 marker 수리

- 실제 provider/model/effort / 지정 역할: Codex; 현재 대화 모델의 실제 ID는 노출되지 않음 / 사용자 지정 hands-on work, 계약상 Codex `gpt-5.6-luna`/high.
- 가설 / 사용자 관찰: 명시적 `loop/ESCALATE_SOL` marker가 있을 때만 `rc=75`를 terminal middle-review handoff로 취급해야 하며, marker 없는 raw worker exit75는 generic nonzero fail-streak/retry 경로를 보존해야 한다.
- 예상 PASS / FAIL 조건: marker fixture는 exit75·marker 보존·worker 1회·middle 0회; raw exit75 fixture는 marker 없이 worker 2회 재시도·generic fail-streak 로그·`max-laps(2)` 정상 종료; 인접 suite와 Fast 모두 PASS.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): `loop/loop.sh`, `tests/test_model_routing.py`만 구현 변경. 커밋 없음/unborn HEAD. 후보 SHA: `loop/loop.sh` `c272af40b02b8fede480d52baa22cf790fcf8d21cf3a1cb8e630b1c60bb4d974`, `tests/test_model_routing.py` `01ea5d3fa43d348d87bfcf243787aeb663678e86327db769eee328ec36388d1e`. 기존 `loop/ESCALATE_SOL` SHA `aed5728763aaa81a677935ba69f4550be762e92219c9509f69811fad881e476e` 보존.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 게임/후보 EXE 변경·실행 없음; 격리된 pytest 임시 프로젝트, local original guard fixture, fake worker가 각각 marker 생성 또는 raw exit75를 반환. 실제 플레이어/지도/군대 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `bash -n loop/loop.sh`; `.venv/bin/python -m pytest -q tests/test_model_routing.py::test_worker_escalation_stops_for_explicit_middle_review`; `.venv/bin/python -m pytest -q tests/test_model_routing.py::test_raw_worker_exit75_without_marker_uses_generic_failure_retry`; `.venv/bin/python -m pytest -q tests/test_model_routing.py tests/test_patch_loop.py`; `make check`; `sha256sum loop/loop.sh tests/test_model_routing.py loop/ESCALATE_SOL`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): syntax PASS; targeted 2 PASS; 인접 25 PASS/7.96s; 전체 `make check` 83 PASS/9.03s, Ruff PASS, compileall PASS, mypy 8 files PASS, `CONTEXT_PASS`. 실제 게임/G1-A는 SKIP(이번 카드 범위 밖 및 escalation 보류).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: `main`은 `rc=75 && -f ESCALATE_SOL`일 때만 terminal 처리한다. marker 없는 raw exit75는 2회 호출, `연속 실패 1/5`, `연속 실패 2/5`, `max-laps(2)`를 확인했다. 새 Sol/Opus5 middle 독립 확인 전이며 사용자 마일스톤 승인 없음. G1~G4 판정 없음.
- 다음 한 가지: 새 Codex `gpt-5.6-sol`/high middle 세션이 두 파일의 후보 SHA와 targeted·인접·Fast 결과를 독립 확인하고, 통과 전에는 G1-A를 재개하지 않는다.
