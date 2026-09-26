# 2026-09-12 | lap 240 | 목표 G1 Stage B — R6-B-R9 middle 독립 검수

- 실제 provider/model/effort / 지정 역할: Claude Code middle tier / claude-opus-5 / high /
  진단·계획·확인. 게임 코드 hands-on 수정 없음(`tools/` 해시 불변으로 확인).
- 가설 / 사용자 관찰: lap239 work가 주장한 "직접 selection reader 실패 5지점 fail-close +
  production 계속 진행 + 기존 polling/PASS 불변"이 work의 테스트 하네스와 **독립적으로** 재현되며,
  실패를 놓치는 하네스가 아닌지를 변이로 확인한다.
- 예상 PASS / FAIL 조건: 독립 하네스에서 (a) `_g1_run_input_sequence` 안의 모든 직접
  `_g1_read_selection_stage` 호출점이 열거된 read point와 정확히 일치하고, (b) 5개 raising 지점이
  `OSError`/`ValueError`/`struct.error` 전부에서 `UNKNOWN_STATE_READ_FAILURE`로 닫히며 stage 레코드가
  **디스크에 flush된 뒤** 예외가 전파되고, (c) production 지점은 `BLOCKED`+진단 보존으로 후속
  drag/minimap을 계속하며, (d) 무결 경로는 PASS/PASS/BLOCKED/PASS 그대로이고, (e) 미모델링 예외는
  read-failure로 위장되지 않으며, (f) 주입한 변이 5종을 전부 검출하면 PASS. 하나라도 어긋나면 FAIL.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `docs/history/laps/probes/20260912_lap240_r6b_r9_review_probe.py`
  `3fba3ca05f5b295de3dfb7a59437871f4aa43e66204d28724e424b6c07e7a913`,
  `docs/history/laps/probes/20260912_lap240_r6b_r9_review_report.json`
  `647bdb1ce55eb3f6c1ea4b8571d58125c180db978f37ac015c71b60ad74c7bbd`,
  `…_review_report.attempt1.json`, `…_review_report.PROVENANCE.md`, `docs/STATUS.md`,
  `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`, `loop/ESCALATE_SOL`, 본 기록.
  검수 대상 `tools/runtime_env.py` `bb10cd84…918d2dab`, `tests/test_runtime_env.py`
  `a2454b94…6cedc372`는 lap239 기록과 동일하며 이번 바퀴에 변경하지 않았다.
  uncommitted; `LOOP_ALLOW_COMMITS=0`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 EXE pin
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변; 후보 없음,
  게임/Wine/Xvfb 실행 0회, PNG 0장, 활성 플레이어·지도·군대 N/A. fixture는 이번 검수를 위해 새로
  작성한 fake selection/camera reader와 fake-clock이며, work의 `tests/test_runtime_env.py`
  하네스를 재사용하지 않았다. 실제 프로세스 메모리는 읽지 않았다. 변이 케이스는 `tools/runtime_env.py`
  **사본**을 임시 디렉터리에 적재해 실행했고 원본 파일은 건드리지 않았다(위 해시로 확인).
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `.venv/bin/python docs/history/laps/probes/20260912_lap240_r6b_r9_review_probe.py --report
  docs/history/laps/probes/20260912_lap240_r6b_r9_review_report.json` → `verdict=PASS`;
  동일 경로 재실행 → `FileExistsError`(R6-B-R7 비덮어쓰기 재확인);
  `make check` → 263 passed, Ruff/compileall/mypy 10 files, `CONTEXT_PASS`;
  `LOOP_DRY_RUN=0 bash checks/safety.sh check` → `SAFETY_PASS`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): R6-B-R9 범위 **PASS**.
  - call-site 열거: AST로 찾은 직접 호출 read point 6개가 `before_click`/`before_production`/
    `before_drag`/`after_drag`/`before_minimap`/`after_minimap`와 정확히 일치, 중복 0.
  - raising 15-case(5지점 × 3예외) 불일치 0. 각 케이스에서 record `result`·`timeout_cause`
    = `UNKNOWN_STATE_READ_FAILURE`, `direct_reader=selection`, `direct_reader_failure=True`,
    read point 일치, `poll_count=0`/`poll_attempt_count=0`, `direct_read_error_count=1`,
    first==last provenance가 예외 타입 접두사와 일치, `predicate_observed=False`,
    그리고 예외 전파 **전에** `evidence.json`에 해당 레코드가 이미 기록됨을 디스크에서 확인했다.
  - production 3-case: 예외 탈출 0, `BLOCKED`/`waited=False` 유지, `selection_read_failure`에
    stage/read point/provenance 보존, 입력 순서 `unit_select→production→drag_select→minimap`,
    클릭 `[(410,270),(150,520)]`·드래그 `[(350,180,550,350)]` 그대로, 후속 stage PASS.
  - 무결 경로: PASS/BLOCKED/PASS/PASS, UNKNOWN 0건 — 기존 PASS 경로 완화 없음.
  - 미모델링 예외(`KeyError`): read-failure로 분류되지 않고 그대로 전파, PASS 주장 0건.
  - 변이 5/5 검출 — catch를 `OSError`로 축소, classification을 `FAIL_NO_EFFECT`로 완화,
    `direct_read_point` 제거, `after_drag` 실패를 가짜 성공으로 삼킴, production 실패가 후속 입력을
    중단. 전부 위 체크에서 FAIL로 잡혔다.
  - 제품 G1/R6-B 전체/Stage B는 **SKIP**(게임 실행 0회).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 이번 바퀴는 lap239 work에 대한 **middle 범위
  승인**이며 사용자 마일스톤 승인이 아니다. 첫 probe 실행은 `verdict=FAIL`이었으나 원인은
  하네스가 고정 call-index로 카메라를 돌려줘 minimap `camera_before`가 이미 이동값이던 **probe 결함**
  이었고, 제품 코드/임계값/baseline/golden은 통과를 위해 바꾸지 않았다. 실패 시도는
  `…attempt1.json`과 `…PROVENANCE.md`로 보존했다.
  비차단 신규 발견 2건:
  - **R6-B-R14**: production 레코드의 `before/after.selection`은 read 실패 시에도
    `{"status":"UNAVAILABLE","count":null}`이라 "읽지 않음"과 "읽기 실패"가 최상위에서 구별되지
    않는다. provenance는 `selection_read_failure`에 보존되고 production은 어차피 `BLOCKED`라
    완화는 아니다. R6-B-R12와 같은 계열의 표기 문제다.
  - **R6-B-R15**: `_g1_read_selection_stage`는 run budget이 이미 소진된 순간의 직접 실패도
    무조건 `UNKNOWN_STATE_READ_FAILURE`로 닫는다(`remaining_budget_after=0.0`으로 재현 확인).
    `_wait_state`는 같은 상황에서 `UNKNOWN_BUDGET_EXHAUSTED`를 우선한다. 둘 다 UNKNOWN이라
    PASS 완화는 아니지만 분류 provenance가 갈린다. 또한 production 경로는 예외 속성인
    `remaining_budget_after`/`finished_elapsed`가 레코드에 남지 않는다.
  S1/F2-R2, R6-B-R2, WM_CLOSE, G2~G4는 미해결이며 Stage B run과 게임 실행은 계속 금지다.
- 다음 한 가지: 새 work tier(Luna/Sonnet5 high)가 **R6-B-R10**(probe 쓰기 불가 경로 분류)을
  게임 없이 한 건만 구현하고 회귀를 남긴다. 그 뒤 R11 → R12 → R13 → R14 → R15 → F2-R1 → F3-R1 →
  F3-R2 → F6-R2. R14/R15는 provenance 정밀도 항목이며 R10을 막지 않는다.
