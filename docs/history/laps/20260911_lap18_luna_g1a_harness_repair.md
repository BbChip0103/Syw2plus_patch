# 2026-09-11 | lap 18 | 목표 G1-A 하네스 최소 수리

- 실제 provider/model/effort / 지정 역할: Codex work role; 계약상 `gpt-5.6-luna`/high 대상. 현재 런타임은 정확한 모델 ID/effort를 노출하지 않아 실제값은 미확인.
- 가설 / 사용자 관찰: lap16의 `1→1` selector 관측과 PS5 정체는 4바이트 reader, 정규화 없는 입력, PS7 endpoint 대기의 결합된 하네스 결함이다. 원본 정적 근거에 맞춘 최소 수리로 다음 G1-A 실행의 입력/상태 경계를 복구한다.
- 예상 PASS / FAIL 조건: selector를 WORD 2바이트로 읽고 초기1이면 `(344,169)`에서 `1→0`, `(462,169)`에서 필수 `0→1`, 두 캡처를 `(760,40)` 중립 커서에서 수집하며 confirm/ready가 PS5를 유지하면 회귀 PASS. 필수 Fast/safety 실패면 즉시 보존·승격한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): `tools/runtime_env.py`, `tests/test_runtime_env.py`; 게임 코드/EXE/DLL/asset/보존 run 변경 없음. 커밋 없음, unborn HEAD. 변경 후 SHA: runtime_env `caccb0a8c40bf115a2ae5a1f422f84af2241302f00215fdb9f4818ca2f1d4c85`, test_runtime_env `1fa42c3328428c6de44ef1d81c7f1d490902003b0fa8d58d5d24831cd894b63a`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본/후보 EXE SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 바이너리 후보 없음. 새 게임 실행 없음. lap16의 private Wine win32/Xvfb `:91`/1600×1200×24/기본2인 임의게임은 실패 자료로만 보존·대조했고 활성 전투/군대 증거 아님.
- 실행 명령 / 로그 / 캡처 경로 및 해시: 이전 lap16 run과 lap17 정적 `objdump` 근거를 독립 대조. `.venv/bin/python -m pytest -q tests/test_runtime_env.py tests/test_runtime_guards.py` → 14 passed. `make check` → 84 passed, Ruff/compileall/mypy8/`CONTEXT_PASS`. `checks/safety.sh check` → `SAFETY_PASS`. 게임/`g1-baseline` 재실행·새 PNG는 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): `_read_lobby_mode`는 `0x004ED848`에서 2바이트 `<H>`로 읽음 **PASS**. 초기1 조건부 `(344,169)` `1→0` 및 solo `(462,169)` `0→1` 계획·중립 커서 `(760,40)` 캡처 **PASS(코드/회귀 범위)**. confirm/ready와 전투 진입 캡처도 중립 커서 기준으로 정리했고 안정 endpoint PS5 **PASS(코드/회귀 범위)**. 실제 원본 UI/PS5→PS3/전투/2배 출력 **SKIP**.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: targeted/Fast/safety 회귀 없음. 새 middle이 변경 SHA와 입력 순서를 독립 확인해야 하며, 그 전에는 G1-A 새 run을 허용하지 않는다. G1~G4 제품 판정과 사용자 승인은 없음.
- 다음 한 가지: 새 Codex `gpt-5.6-sol`/high middle이 lap18 변경을 독립 검수하고 PASS/REVISE를 기록한다. 게임은 재실행하지 않는다.
