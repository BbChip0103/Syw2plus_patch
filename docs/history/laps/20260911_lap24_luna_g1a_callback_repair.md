# 2026-09-11 | lap 24 | 목표 G1-A runtime callback repair

- 실제 provider/model/effort / 지정 역할: Codex 실무 work 세션, 계약상 `gpt-5.6-luna`/high. 현재 런타임은 실제 model ID/effort를 노출하지 않아 실제값은 미확인.
- 가설 / 사용자 관찰: `_wait_state`가 bool 인자를 전달하는 계약에 맞춘 명시적 selector reader adapter와 좁은 타입 주석을 적용하면 lap22의 selector callback `TypeError`가 제거되고, 기존 무인자 `_g1_selector_flow` mock 회귀는 유지된다.
- 예상 PASS / FAIL 조건: production selector가 계속 `state(False)`를 사용하고, `_wait_state` reader가 `Callable[[bool], dict[str, Any]]`로 고정되며, `True` 전달 회귀·양쪽 selector 초기 분기·targeted/Fast/safety가 통과해야 한다. 게임 재실행은 하지 않는다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): `tools/runtime_env.py`, `tests/test_runtime_env.py`만 구현/회귀 변경. 이전 SHA는 각각 `fa8474af6fcaf06e2bfe3800bc8baaec1c26260770ddbb1c9517119518776dd1`, `ec6eef2898b53cec4833c63755d4a43101288ea8747e3159e940705e3c0711c2`; 후보 SHA는 각각 `b091a8ae83e5332c1d5dc17cb979531fcafc19bdf3368f56b4c094d24560195c`, `d15a3580b2fd9d0bc209ca62015bc659f3a0d8982d33ea559b7645f1306baa75`. 커밋 없음, unborn HEAD, `LOOP_ALLOW_COMMITS=0`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 게임/EXE/DLL/assets 변경 및 실행 없음. 원본 SHA는 lap23 보존값 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; fixture·실제 활성 플레이어·지도·군대 수치는 이번 lap에서 없음. lap22 run `local/runtime/20260911_022220_235549_0`과 산출물은 보존.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `.venv/bin/python -m pytest -q tests/test_runtime_env.py tests/test_runtime_guards.py` → PASS; `make check` → PASS; `bash checks/safety.sh check` → `SAFETY_PASS`. 새 게임, `g1-baseline`, 새 PNG, 패치 old/new/restore는 실행하지 않음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): targeted `19 passed in 0.04s`; Fast `89 passed in 10.98s`, Ruff/compileall/mypy 8 files 및 `CONTEXT_PASS`; safety PASS. `_wait_state`는 bool reader annotation을 사용하고 selector/selection/camera wait reader가 명시적 bool parameter를 받는다. 기존 양쪽 selector flow 테스트는 유지. runtime harness repair 1단 PASS; G1-A 실제 게임/제품 G1~G4 판정은 SKIP/미완료.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: `TypeError` catch나 무인자 fallback은 추가하지 않았다. 새 Sol/high가 후보 SHA·실제 호출 경로·회귀를 독립 확인해야 하며, 그 전에는 새 G1-A run을 실행하지 않는다. 사용자 마일스톤 승인 없음.
- 다음 한 가지: 새 Codex `gpt-5.6-sol`/high middle이 후보 두 파일과 targeted/Fast/safety 결과를 독립 확인하고, 확인 후에만 G1-A 새 격리 원본 run 허용 여부를 판정한다.
