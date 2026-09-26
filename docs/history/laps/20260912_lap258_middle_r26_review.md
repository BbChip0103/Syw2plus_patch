# 2026-09-12 | lap 258 | 목표 G1 — R26 독립 검수 (middle)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5`/high / middle(진단·계획·컨펌).
  게임 코드 hands-on 수정 없음. 검수 산출물(probe/기록/STATUS/handoff)만 작성했다.
- 가설 / 사용자 관찰: lap257 work는 `_g1_read_selection_stage`의 직접 reader 실패 관측에
  `stage_budget_state`를 추가해 `stage_budget_exhausted=false`가 뭉뚱그린 세 상태를 구별했다고
  주장한다. lap254가 R15에서 겪은 것과 같은 "필드는 맞지만 회귀가 그 값을 붙잡지 않는" 결함이
  남아 있는지 독립 측정으로 확인한다.
- 예상 PASS / FAIL 조건: PASS = (C0) 대상·인접 테스트 통과, (C1) 계약으로부터 독립 작성한 기대
  모델과 실측 불일치 0, (C2) 깊이 일치 미러 M0가 실저장소 결과와 동일, (C3) 상태 고정·상태 축약·
  경계·우선순위 변이 **생존 0** 및 범위 밖 사살 0. 하나라도 생존하면 **범위 승인 FAIL(커버리지)**.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  신규 `docs/history/laps/probes/20260912_lap258_r26_review_probe.py`,
  `..._report.json`, 본 기록, `docs/STATUS.md`,
  `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`, `loop/ESCALATE_SOL`.
  SUT는 검수 전후 동일: `tools/runtime_env.py`
  `f54932b50c6de5c575699ade11947fcea93219ab7a8b2a69e845137b301dfec4`,
  `tests/test_runtime_env.py`
  `96e4c0916dc4c1ac1565615cd6a5ba2ae709a2ca5d8ebbb1fdeef6890e552838` (lap257 기록값과 일치).
  uncommitted, `LOOP_ALLOW_COMMITS=0`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 EXE pin
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변; 제품 EXE/DLL/assets/
  baseline/golden 변경 0. Python 3.13.5/.venv, fake `time.monotonic` + 주입 `OSError`,
  `/tmp` 깊이 일치 미러. 실제 게임/Wine/Xvfb/PNG 0회; 플레이어·지도·군대 N/A.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - probe `.venv/bin/python docs/history/laps/probes/20260912_lap258_r26_review_probe.py`
    (exit 0), 리포트 `docs/history/laps/probes/20260912_lap258_r26_review_report.json`.
  - `make check` = `279 passed`, Ruff/compileall/mypy 10 source files, `CONTEXT_PASS`.
  - `LOOP_DRY_RUN=0 bash checks/safety.sh check` = `SAFETY_PASS`. 캡처 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **R26 범위 승인 FAIL (커버리지)**.
  - **C0 PASS** — 대상+인접 선택 14 passed / 130 deselected.
  - **C1 PASS** — 독립 행렬 160-case 불일치 0. stage 5종(`unit_select`/`drag_select`/`minimap`/
    `production`/`menu`) × `stage_started` {None, 0.0, 4.25, 100.0} × stage 상대 offset
    {0, .001, 5, 9.999, 10.0, 10.001, 14.25, 30}. 네 상태 모두 관측
    (UNAVAILABLE 64 / EXHAUSTED 36 / WITHIN 36 / START_UNKNOWN 24). 기대 모델은 SUT 소스가 아니라
    lap256 handoff와 R26 계약 문장에서 작성했고, 분류는 160건 전부 `UNKNOWN_STATE_READ_FAILURE`,
    boolean은 160건 전부 `state == STAGE_BUDGET_EXHAUSTED`와 일치했다.
  - **C2 PASS** — 미러 M0 144 passed = 실저장소 `tests/test_runtime_env.py` 144 passed.
  - **C3 FAIL** — 변이 8종 중 **M5 생존**. 범위 밖 사살 0건.
    M1(상태 `WITHIN` 고정)·M2(상태 `EXHAUSTED` 고정)·M3(`UNAVAILABLE`→`START_UNKNOWN` 축약)·
    M4(`START_UNKNOWN`→`WITHIN` 축약)·M6(`>=`→`>` 경계)·M7(boolean 상수 True)·
    M8(`EXHAUSTED`→`WITHIN` 축약)은 각각 R26 4-case 회귀가 사살했다.
    **M5 = 우선순위 역전**(`stage_started is None`을 `stage_budget is None`보다 먼저 검사)은
    144 passed로 **전부 통과**한다.
  - M5는 이론적 변이가 아니라 **production에서 실제로 도달하는 유일한 조합**을 바꾼다.
    `tools/runtime_env.py:2636`의 production stage 호출은 `stage_started`를 아예 넘기지 않으므로
    `stage_started=None`이고, `production`은 `G1_INPUT_STAGE_BUDGETS`에 없어 `stage_budget=None`이다.
    실측: 그 호출 형태의 현재 출력은 `stage_budget_state="STAGE_BUDGET_UNAVAILABLE"`이고
    M5 적용 시 `"STAGE_START_UNKNOWN"`으로 바뀌지만 테스트는 하나도 깨지지 않는다.
    R26의 유일한 production case 회귀는 `("production", 0.0, ...)`, 즉 **실제로는 발생하지 않는**
    `stage_started=0.0`을 고정하고 있다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 제품 동작 결함은 관측되지 않았다. 결함은
  lap254 M4와 같은 **증거 강도**이며, 두 unknown 상태가 겹칠 때의 우선순위가 계약으로도 회귀로도
  고정돼 있지 않다. 소비자 수는 여전히 0이다(`stage_budget_state`/`stage_budget_exhausted`를 읽는
  코드는 `tools/runtime_env.py` 밖에 없다 — R23/R24와 같은 계열). 제품 G1 증거와 사용자 마일스톤
  승인은 없다. S1/F2-R2, R6-B-R2, R19~R24, WM_CLOSE, G2~G4는 미해결.
- 다음 한 가지: work tier(Luna 또는 Sonnet5/high)가 **R27**을 구현한다 — production 호출과 같은
  `(budget 없음, stage_started=None)` 조합을 회귀로 고정해 우선순위 역전 변이가 죽게 하고,
  `UNAVAILABLE`이 `START_UNKNOWN`보다 우선한다는 계약을 명시한다. SUT 로직 변경이 필요하다고
  판단되면 근거를 남기고 middle로 되돌린다. 승인 뒤 offline 큐는 R19다.
