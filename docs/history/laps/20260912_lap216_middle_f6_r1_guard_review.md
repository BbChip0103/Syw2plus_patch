# 2026-09-12 | lap 216 | 목표 G1 — lap215 F6-R1 producer 가드 독립 검수

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5`/high, middle tier
  (진단·계획·컨펌). hands-on 게임/런타임 코드 수정 없음. 문서·probe만 작성했다.
- 가설 / 사용자 관찰: lap215가 추가한 AST 가드가 "producer closure가 tagged helper를 우회하는
  회귀"를 실제로 차단한다면, 가드를 독립 재구현해 **원본 소스는 통과**시키고 **F6 회귀 형태의
  변이 소스는 실패**시켜야 한다. 통과/실패가 변이와 무관하면 가드는 장식이다.
- 예상 PASS / FAIL 조건:
  PASS = (a) 두 실제 producer 소스에서 위반 0, (b) 회귀 변이(과거 `OBSERVED` stub / helper를
  안 쓰는 직접 append / flow 인자에서 recorder 제거)가 양쪽 producer 모두에서 위반 >0,
  (c) lap215가 보고한 targeted 6 passed·Fast 234·SAFETY_PASS와 production 소스 무변경 재현.
  FAIL = 회귀 변이 중 하나라도 통과하거나, 보고 수치/해시가 재현되지 않는 경우.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  신규 `docs/history/laps/probes/20260912_lap216_f6_r1_guard_review_probe.py`
  sha256 `4e50aa61b25bc13989c80b61409a6b0038c6521c6919396551591ec5831af5c4`,
  신규 `docs/history/laps/probes/20260912_lap216_f6_r1_guard_review_report.json`
  sha256 `a2522d6f435853146f2e3ee55236cd94b99277a563d2c24d6c141b3d49b57eb4`,
  본 기록, `docs/STATUS.md`, `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`,
  `loop/ESCALATE_SOL`. 커밋 없음(`LOOP_ALLOW_COMMITS=0`).
  재현한 소스 해시(모두 이전 기록과 일치):
  `tools/runtime_env.py` `398c2b8ae4980a5c2ddd44bffba2e5330701341a575b5ad4cc519e8ad790322f`
  (lap213/214와 동일 = lap215가 런타임 코드를 건드리지 않았다는 주장 확인),
  `tools/compare_g1_stage_b.py` `7730170e610b2e4a39bb02119dd3ec73ad606b6b034d8c43f255f8a07c729ca4`
  (동일), `tests/test_runtime_env.py`
  `601ebfc821cf98804741c07bc07780019708d799632ab9a839947f75ea010528` (lap215 기록과 일치;
  lap213의 `97d8ee15…`에서 테스트 파일만 바뀌었다).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  **게임 실행 0회, PNG 0장, Wine/Xvfb 미사용.** 원본·후보 바이너리/보존 evidence/baseline/
  golden 변경 0. fixture는 `tools/runtime_env.py`의 실제 producer 소스(AST)와, 후보 recorder를
  실제 `_g1_selector_flow` + 실제 comparator `_inputs_by_tag`로 구동한 in-process 하네스다.
  플레이어/지도/군대는 해당 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `.venv/bin/python docs/history/laps/probes/20260912_lap216_f6_r1_guard_review_probe.py`
  → 위 report.json (exit 0).
  `.venv/bin/python -m pytest -q tests/test_runtime_env.py -k '…guard… or selector_flow or
  selector_input_recorder'` → `6 passed, 105 deselected`.
  `make check` → `234 passed in 40.51s`, Ruff PASS, compileall PASS, mypy Success(10 files),
  `CONTEXT_PASS`. `LOOP_DRY_RUN=0 bash checks/safety.sh check` → `SAFETY_PASS`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  **판정 = PASS(범위 한정) + 신규 비차단 결함 1건(G1-F6-R2).**
  7 case × 2 producer = 14 case 모두 예상과 일치(`unexpected: []`).
  - 실제 소스 2/2 위반 0. 후보 recorder를 실제 flow로 구동하면 tagged 2건, untagged 0,
    comparator `input_errors` 0, flush 2회(기록당 1회).
  - 회귀 변이 **6/6 차단**: `observed_stub`(→ `helper_calls=0`, `observed_stub_constant_present`),
    `silent_bypass`(→ `helper_calls=0`), `flow_wiring_dropped`(→ `flow_recorder_argument_missing`).
    lap215의 주장은 자기 테스트 본문과 독립적으로 재현된다.
  - 가드 공백 변이 **6/6 미차단**(가드는 통과). 하위 영향은 서로 다르다:
    · `conditional_bypass`(helper 호출 수는 1이지만 한 분기에서 untagged 직접 append) →
      가드 통과, 그러나 comparator가 `inputs[1].tag is missing or is not a string`으로 잡는다.
    · `tag_laundered`(`tag=None`으로 helper 호출) → 가드 통과, comparator가 2건 모두 잡는다.
    · **`flush_dropped`(`flush=lambda: None`) → 가드도 comparator도 아무것도 잡지 못한다**
      (untagged 0, `input_errors` 0, flush 0회). `_g1_flush_input_stage`는 "각 stage를 이후
      입력/teardown이 막기 전에 영속화"하는 장치이고, `_g1_selector_flow`는 solo 실패 시
      `RuntimeSafetyError`를 던지므로, flush가 빠지면 **실패한 selector stage의 기록이 그대로
      유실**된다. lap213이 확인한 "기록당 즉시 flush" 성질은 현재 어떤 기계 검사로도 고정돼 있지
      않다. (유실된 stage는 comparator에서 `required input stage is missing` → `INCONCLUSIVE`로
      닫히므로 PASS 세탁 경로는 아니다 — 이는 lap207/208에서 확인된 동작의 승계이며 이번 바퀴에
      새로 재실행하지 않았다. UNKNOWN으로 표시한다.)
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  판정 의미(F1/F4/F5 fail-closed, F2/F3/R6-B 재결)는 이 바퀴에서 바꾸지 않았다. 승인은
  **G1-F6-R1 한정 기술 검수**이며 제품 G1 PASS나 마일스톤 사용자 승인이 아니다. S1 장면 통제
  차단은 유효하므로 후보 Stage B run·원본 재실행·R6-A/R6-C는 계속 금지다. 가드의 범위 주장은
  "recorder가 helper를 우회하지 못한다"가 아니라 "**lap211/212가 실제로 겪은 세 회귀 형태를
  막는다**"로 좁혀 읽어야 한다. 가드가 keyword 인자/wrapper 형태의 정상 리팩터링을 fail-closed로
  막는 성질(과잉 엄격)은 안전 방향이므로 수리 대상이 아니다.
- 다음 한 가지: work tier는 예정대로 **F3 comparator 수리**를 진행한다. 신규 **G1-F6-R2**
  (producer recorder의 `flush` 배선 회귀 가드)는 비차단이므로 F2 · R6-B 뒤 큐 끝에 넣는다.
  S1 재결은 상위 tier(Astra/사용자)에 그대로 남는다.
