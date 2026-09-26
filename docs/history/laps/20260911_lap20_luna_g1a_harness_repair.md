# 2026-09-11 | lap 20 | 목표 G1-A 하네스 의미 회귀 최소 수리

- 실제 provider/model/effort / 지정 역할: Codex work role; 계약상 `gpt-5.6-luna`/high 대상. 현재 런타임은 정확한 모델 ID/effort를 노출하지 않아 실제값은 미확인.
- 가설 / 사용자 관찰: lap19 반려는 게임 원본 결함이 아니라 setup evidence 계약/회귀 공백이다. 실제 `g1-baseline`을 재실행하지 않고, 회귀가 selector 양쪽 초기분기와 `1→0→1`, 중립 커서, PS5 경계 및 ready control 지역 변화를 직접 고정하면 다음 middle 확인을 허용할 수 있다.
- 예상 PASS / FAIL 조건: 허용 파일만 변경하고 selector/endpoint 회귀가 의미 조건을 통과하며 targeted runtime tests, `make check`, `checks/safety.sh check`가 모두 PASS하면 work PASS. 필수 gate 실패 또는 근거 충돌이면 변경을 보존하고 `loop/ESCALATE_SOL`로 승격한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): `tools/runtime_env.py` SHA256 `fa8474af6fcaf06e2bfe3800bc8baaec1c26260770ddbb1c9517119518776dd1`, `tests/test_runtime_env.py` SHA256 `ec6eef2898b53cec4833c63755d4a43101288ea8747e3159e940705e3c0711c2`. 게임 코드/EXE/DLL/assets 및 보존 run은 변경 없음. 커밋 없음, unborn HEAD.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본/후보 EXE 기대 SHA256 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 바이너리 후보 없음. 새 게임 실행 없음. 테스트는 Wine/X11 없는 pure/mock 경계 fixture이며 실제 활성 플레이어·지도·군대 수치는 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `.venv/bin/python -m pytest -q tests/test_runtime_env.py tests/test_runtime_guards.py` → 18 passed. `make check` → 88 passed, Ruff/compileall/mypy8/`CONTEXT_PASS`. `checks/safety.sh check` → `SAFETY_PASS`. `g1-baseline`, 게임, 새 PNG, 패치 old/new/restore는 실행하지 않음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): selector initial `1`은 multiplayer click 후 normalized `0`, initial `0`은 click을 건너뛰고 solo `0→1`로 진행하는 회귀 **PASS**. 양쪽 selector capture는 `(760,40)` 중립 cursor를 요구 **PASS**. confirm transient PS4/5/6→stable PS5 및 ready PS5 유지/local ready crop hash 변화, start PS5→PS3/tick>0 판정 **PASS**. 실제 원본 UI/ready control 화면/PS5→PS3/전투/1600×1200 출력은 **SKIP**.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 전체 화면 SHA 변화만으로 ready 성공을 인정하지 않고 player-0 ready 주변 `(84,39,100,80)` content crop SHA 변화를 별도 요구한다. 새 middle이 두 파일 SHA와 실제 경계를 독립 검수해야 하며, G1-A 실행·G1~G4 제품 판정·사용자 승인은 없음.
- 다음 한 가지: 새 Codex `gpt-5.6-sol`/high middle이 lap20 후보를 독립 확인하고 PASS/REVISE를 기록한다. PASS 전에는 게임을 실행하지 않는다.
