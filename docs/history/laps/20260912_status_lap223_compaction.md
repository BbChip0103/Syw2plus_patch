# STATUS pre-compaction snapshot — lap 223

R6-B work 완료 후 safety line-limit 위반 시점의 `docs/STATUS.md` 원문이다.

- pre-compaction SHA256: `ccfcd63ab540a17a9ba779a525f06e978684ad2382338d968da50e8e263aa46e`
- line count: `184`

---

# STATUS — 매 바퀴 갱신하는 기억

## 지금 상태

G1~G4는 제품 단위로 모두 미완료다. G1은 원본 800×600 논리 구도/UI를 유지한 1600×1200
정수 2배 출력, G2는 8인 전비 5000과 실제 개체 풀/메모리 확장, G3은 최대 16인, G4는
길찾기·자유대전 AI 개선이다.

DxWrapper 후보는 fresh runtime에서 1600×1200 client/capture, 800×600 logical, 2×2 scale,
선변환 없는 입력, PS9→PS7→PS3와 30초 지속 렌더를 확인했다. WM_CLOSE 후 teardown 미완료는
builtin ddraw 대조로 DxWrapper native 경로에 귀속했으며 P6 Lock 계측은 주차했다.

카드2 Stage A A-1~A-16과 Stage B R1~R5-C/N1~N3은 원본·후보 공용 입력, production
fail-closed, menu 대칭, 단일 최종 evidence flush, 선택 slot/type 관측, 비교기와 입력 손상
fail-closed를 구현했다. 각 bounded repair는 Luna/high 작업 뒤 Opus5/high가 독립 검수했다.

사용자는 2026-09-12 01:03 KST “승인. 루프 계속 돌아”로 Stage B evidence가 성립할 때까지
bounded repair→fresh validation을 승인했다. blind retry, 같은 run 재사용, 보호 자산 변경은 금지다.

lap204의 fresh 원본 run은 PS3에서 unit_select count 0→1, slot/type 1199/70을 관측했고 정상
production 비활성을 BLOCKED로 남긴 뒤 drag에서 count>=2를 못 봐 중단됐다. 그러나 선택 identity가
1199/70→1198/21로 바뀌어 실제 효과가 있었으므로, lap205 Opus 검수는 `FAIL_NO_EFFECT`와
`count>=2`를 근거 없는 판정식 결함으로 확정했다. 후보는 실행하지 않았다.

R5-B 오프라인 비교기는 menu/좌표, scene, 선택 변화, minimap camera를 원본↔후보로 비교한다.
F1(camera 필드 누락 PASS), F4(input_errors 무시), F5(누락·비문자열 tag 무시)는 수리 후 lap209와
lap211 Opus 검수로 승인됐다. 최신 `make check`는 232 passed, safety PASS다.

lap211이 확정한 **F6**(후보 selector flow가 tag 없는 `OBSERVED` 레코드를 만들어 올바른 후보
run도 F5+F4로 항상 INCONCLUSIVE가 되던 생산자 비대칭)는 lap212 work가 공용 tagged recorder로
수리했고, **lap213 middle이 게임 실행 없이 독립 검수해 승인(PASS)** 했다. 후보/원본 recorder
closure 소스가 이름을 빼고 동일하며, 후보 closure 원본 소스로 `_g1_selector_flow`를 구동한 두
분기 모두 untagged 0 / comparator input_errors 0 / 기록당 즉시 flush / 논리좌표+2× geometry를
보였다. 수리 전 stub 형태는 음성 대조에서 여전히 error로 잡힌다. 승인은 F6 한정이며 후보
Stage B run을 열지 않는다.

모델 라우팅은 Luna/high(work), Claude Opus5/high(middle/judge), Astra/medium(strategy)이다.
Astra는 큰 분기·교착에만 약 10 lap당 1회 이하로 사용한다. 마지막 Astra는 runtime lap213 추가 세션(근거 충돌 승격)이었다.

| 목표 | 판정 | 현재 근거 / 미충족 |
|---|---|---|
| G1 1600×1200 원본 구성 | 미완료 | 표시·논리 좌표 증거 있음; F6 승인(lap213), F6-R1 가드 검수 PASS(lap216), F3 검수 PASS(lap218), **F2 검수 PASS(lap221)**, R6-B work 구현(lap222); S1 장면 통제·R6-B middle 검수·F2-R1/F2-R2·F3-R1/R2·fresh pair·WM_CLOSE 미해결 |
| G2 8인 전비5000 안정성 | 미완료 | 숫자 패치 외 8인 부하·개체 풀/메모리 확장 증명 없음 |
| G3 최대16인 | 미완료 | 9~16인 로비/상태/통신/시뮬레이션 미구현 |
| G4 길찾기/AI 난이도 | 미완료 | 원본 대비 지표·개선 구현 없음 |

## 다음 한 가지

다음은 새 middle 세션이 **R6-B work 결과와 이번 바퀴의 필수 gate 실패·수리·최종 증거**를
독립 검수한다. 그 뒤 상위 tier(Astra/사용자)가 **S1 장면 통제**와 신규 **G1-F2-R2**를 함께 재결한다.
lap214가 원본 binary 두 run을 비교해
`UNKNOWN_SCENE_MISMATCH`를 재현했다 — nation과 owner1 스폰이 run마다 랜덤이고 seed가 노출되지
않아, **승인된 fresh pair 1회는 F2/F3/R6-B를 다 고쳐도 비교 가능한 장면을 얻는다는 보장이 없다.**
이는 판정 술어가 아니라 실험 설계 문제이며 middle 범위를 넘는다. 근거는
`docs/history/laps/20260912_lap214_middle_oracle_readjudication.md`.

F2 identity 재정의는 lap219 gate 실패 → lap220 수리 → **lap221 middle 독립 검수 PASS(범위 한정)**로
닫혔다. 이후 순서는 R6-B → 비차단 G1-F2-R1(evidence 없는 폴백) → G1-F3-R1(잠재 PASS 세탁) →
G1-F3-R2(판정력 침식) → G1-F6-R2(flush 배선 가드)이며 각 건은 다음 middle이 독립 검수한다.
계획 승인이지 제품/마일스톤 승인이 아니다.

lap222 work가 R6-B를 구현했다. `drag_select`는 `count>=2` 대신 입력 전후 count 또는
`(selected_slot, selected_type)` 변화로 응답을 판정하며, 동일 상태는 계속 FAIL/timeout이다.
count 1→1 identity 변화 fixture를 포함한 targeted 6 passed와 최종 `make check` 239 passed /
Ruff/compileall/mypy/CONTEXT_PASS, safety `SAFETY_PASS`를 얻었다. 첫 `make check`는 최종
`drag_pass` 대입부의 잔여 `count>=2` 때문에 238 passed/1 failed였으므로 이번 바퀴는 사용자
지시에 따라 승격하며 R6-B 완료·제품 PASS로 닫지 않는다.

## 지금 막힌 것 (Blockers)

- 원본/제품 EXE·DLL/assets/baseline/golden 변경, evidence 재사용, 무변경 blind retry, PASS 완화 금지.
- production 클릭 금지. 정상 비활성은 BLOCKED로 남기고 후속 입력은 계속한다.
- **S1 장면 통제(신규, 최상위 차단):** 원본↔원본 pair도 `UNKNOWN_SCENE_MISMATCH`다. run A/B의
  nation이 2·2 ↔ 3·1, owner0 type이 [31,58] ↔ [21,70], owner1 상대 offset이 (-71,71) ↔ (-21,-50)로
  달랐고 `replay_seed_observed=false`다. comparator scene gate는 옳고 fail-closed이며 완화 금지다.
  S1 재결 전 후보 Stage B run·원본 재실행·R6-A/R6-C 착수는 계속 금지.
- **F2/F3/R6-B는 lap214 middle이 재결했다.** F2는 lap221 middle 검수로 닫혔고
  R6-B는 lap222 work 구현됐지만 필수 gate 1회 실패가 있어 middle 검수 전이다. 절대 slot 동일성은
  FAIL 술어에서 빼고 `(owner, type, 상대 world offset)`으로 해소한다. `FAIL_NO_EFFECT`는 카드
  FAIL로 상속하지 않고 `UNKNOWN_DISPUTED_ORACLE`→overall `INCONCLUSIVE`로 닫되 **PASS 경로를
  절대 만들지 않는다**. `count>=2`는 근거 0으로 기각하고 "선택 상태가 응답했다"로 대체한다.
- **F2는 lap221 middle 독립 검수 PASS(범위 한정).** 저장소 fixture를 쓰지 않는 12 case probe가 전부
  예측과 일치했고, 400 sample 무작위 sweep의 overall `PASS` 74건은 모두 scene PASS·input_errors 0·
  slot 동일·정규화 identity 동일·count delta 동일·양측 result PASS를 만족했다(새 PASS 경로 0).
  slot·type이 같고 같은 type 2기의 위치만 교환된 case는 `FAIL`이므로 이 수리는 FAIL 판정력을
  **넓혔다**. `cast(int, slot)`은 `_is_int` 가드 뒤 런타임 무연산이라 의미 중립이다. 승인은
  comparator semantics 한정이며 후보 Stage B run 금지는 그대로다.

- **G1-F2-R1(신규, 비차단):** `_stage_report`가 evidence 인자 없이 호출되면 identity가 절대
  `[slot, type]`로 되돌아가 PASS를 낸다(`tools/compare_g1_stage_b.py:271~281`). 현재 유일한 호출자
  `compare_evidence`는 항상 evidence를 넘기므로 도달 불가지만, 주석이 근거로 든 "직접 호출 probe"는
  저장소에 존재하지 않는다. F3-R1과 같은 부류이며 evidence를 필수로 만들거나 없을 때
  `INCONCLUSIVE`로 닫는다. 새 PASS 경로는 만들지 않는다.

- **G1-F2-R2(신규, 비차단, 상위 tier 재결 사항):** `UNKNOWN_SLOT_CORRESPONDENCE` 강등 때문에 카드
  overall PASS는 **원본/후보 run이 동일한 엔진 slot id를 낼 때만** 가능하다. lap214가 run별 랜덤
  스폰과 `replay_seed_observed=false`를 재현했으므로, S1을 장면 일치만으로 푸는 해법은 카드 PASS에
  충분하지 않다. S1 해법이 slot id 결정성까지 주든지, slot 강등을 상위 tier가 재결해야 한다.
  middle은 완화하지 않는다.
- **F3(lap217 구현)은 lap218 middle 독립 검수 PASS(범위 한정).** 저장소 fixture를 쓰지 않는
  18 case probe에서 disputed 경로의 overall PASS는 0이고, 보고 해시·수치(targeted 12 / Fast 236 /
  `SAFETY_PASS` / 보존 pair `INCONCLUSIVE`)가 재현됐다. 승인은 comparator semantics 한정이며
  후보 Stage B run 금지는 그대로다.
- **G1-F3-R1(신규, 비차단, 잠재 PASS 세탁):** `after.last` 폴백이 source result와 무관하게 항상
  켜져, result `PASS` + timeout shape `after`(probe B1)와 손상된 비Mapping `after.selection`을
  `last`로 대체하는 경우(B2)가 overall PASS가 된다. 현재 producer에서는 도달 불가지만 comparator는
  producer 결합에 기대면 안 된다. 수리 범위는 handoff lap218 절.
- **G1-F3-R2(신규, 비차단, 판정력 침식, middle 재결 완료):** `disputed = any(result != "PASS")`가
  timeout이 아닌 하드 `FAIL`(`runtime_env.py:2556` minimap)까지 흡수해 실제 parity 실패가 카드
  FAIL 대신 `INCONCLUSIVE`가 된다(probe B3). disputed 집합을 `FAIL_NO_EFFECT`/
  `UNKNOWN_BUDGET_EXHAUSTED`/`UNKNOWN_OBSERVATION_WINDOW_TRUNCATED`로 좁히고, 하드 `FAIL`은 FAIL,
  미지 result·키 누락은 `INCONCLUSIVE`로 닫는다. 새 PASS 경로는 만들지 않는다.
- **F6는 lap213에 승인됐으나 후보 run은 계속 금지:** 이전 보존 후보 evidence는 여전히 untagged
  `OBSERVED`를 포함하므로 재사용하지 않는다.
- **G1-F6-R1: lap216 middle 독립 검수 PASS(범위 한정).** 가드를 독립 재구현해 실제 producer 2종은
  위반 0, 회귀 변이 3종(과거 `OBSERVED` stub / helper 없는 직접 append / flow 인자에서 recorder 제거)은
  6/6 차단을 확인했다. 가드의 주장은 "우회 불가"가 아니라 "lap211/212가 겪은 세 형태를 막는다"이다.
- **G1-F6-R2(신규, 비차단):** recorder가 helper를 호출하되 `flush`만 죽인 변이는 가드도 comparator도
  잡지 못한다(untagged 0 / `input_errors` 0 / flush 0회). 실패한 selector stage 기록이 유실되므로
  기록당 flush 배선을 고정하는 가드가 필요하다. PASS 세탁은 아니며 유실 stage는 `INCONCLUSIVE`로 닫힌다.
- random seed 미노출로 scene 불일치는 Tier-2 UNKNOWN이다. minimap은 camera 절대 목적지를 비교한다.
- 후보 WM_CLOSE teardown 결함은 출시 전 미해결이며 실제 후보 scene/input evidence도 아직 없다.
- G2~G4는 제품 증거가 없다.

## 검증 상태

- lap146~170: 후보 2배 표시·입력·지속 렌더 확인, close 결함 귀속, Astra가 G1 증거 우선 결정.
- lap171~203: Stage A와 R1~R5-C/N1~N3 구현·독립 승인, pair run 인가.
- lap204~205: fresh 원본 drag 중단 보존; Opus가 실제 효과와 판정식 결함을 확정.
- lap206~209: R5-B 및 F1/F4 수리·독립 승인, Fast 229/safety PASS.
- lap210~211: F5 수리·25 fixture 독립 승인, F6 생산자 비대칭 확정, Fast 231/safety PASS.
- lap212: F6 producer 수리·selector recorder 회귀, Fast 232/safety PASS, 게임 0회.
- lap213: F6 독립 검수 PASS(소스 동일성·양 분기 구동·음성 대조·해시 재현), duplicate-tag 가설 반증,
  G1-F6-R1 회귀 공백 발견, Fast 232/safety PASS, 게임 0회.
- lap213 Astra 추가 세션: 근거 충돌로 ESCALATE, 구현 0; 기존 세 소스 SHA 일치만 새로 확인.
- lap214: F2/F3/R6-B 원자료 재결 완료(세 건 모두 근거·fixture 대응), 신규 S1 장면 통제 차단 발견,
  원본↔원본 pair `UNKNOWN_SCENE_MISMATCH` 재현, 소스 4종 SHA 무변경, Fast 232/safety PASS, 게임 0회.
- lap215: G1-F6-R1 producer 가드 테스트 추가, targeted 6 passed, Fast 234/safety PASS, 게임 0회.
- lap216: F6-R1 가드 독립 검수 PASS(14 case 전부 예상대로: 실제 2종 통과, 회귀 변이 6/6 차단,
  공백 변이 6/6 미차단), 신규 비차단 G1-F6-R2(flush 배선) 발견, 소스 3종 SHA 무변경,
  targeted 6 passed, Fast 234/safety PASS, 게임 0회.
- lap217: F3 comparator 수리 및 `after.last` selection/camera 회귀 3종 추가, targeted 12 passed,
  Fast 236/safety PASS, 보존 pair `INCONCLUSIVE`/historical untagged errors 유지, 게임 0회.
- lap218: F3 독립 검수 PASS(18 case 전부 예측 일치, disputed 경로 PASS 0), 신규 비차단
  G1-F3-R1/F3-R2 발견 및 F3-R2 disputed 집합 재결, 소스 해시 4종 재현, targeted 12 passed,
  Fast 236/safety PASS, 게임 0회, 코드 변경 0.
- lap219: F2 identity bounded repair를 적용하고 targeted 14 passed, 보존 pair
  `INCONCLUSIVE`/`NOT_COMPARED`, safety PASS를 확인했다. 그러나 `make check`의 pytest 238,
  Ruff/compileall 뒤 mypy가 `tools/compare_g1_stage_b.py:270`의 `Any | None`→`int` 대입에서
  실패했다. 필수 gate 실패이므로 이번 바퀴는 ESCALATE이며 F2 PASS/완료로 승격하지 않는다.
- lap220: F2 타입 경계를 `cast(int, slot)`으로 수리했다. targeted 14 passed, 독립 4-case probe
  PASS, `make check` 238 passed/Ruff/compileall/mypy 10 files/`CONTEXT_PASS`, safety
  `SAFETY_PASS`. 보존 pair는 `INCONCLUSIVE`/`NOT_COMPARED`/exit 2 및 후보 historical tag 오류가
  불변이다. 게임 실행 0회, PNG 0장. F2는 다음 middle 독립 검수 대기이며 제품/마일스톤 PASS가 아니다.
- lap221: F2 독립 검수 PASS(12 case 전부 예측 일치, 400 sample sweep 위반 0, slot/위치 교환 FAIL 신규
  확인), 신규 비차단 G1-F2-R1/F2-R2 발견, 소스 3종 SHA 무변경, targeted 14 passed, Fast 238/mypy 10/
  safety `SAFETY_PASS`, 보존 pair `INCONCLUSIVE`/exit 2 불변, 게임 0회, 코드 변경 0.
- lap222: R6-B 구현. 공용 선택 응답 술어가 count 또는 selected identity 변화를 인정하고
  동일 상태는 FAIL/timeout으로 유지한다. 첫 `make check`는 238 passed/1 failed(잔여
  `drag_pass`의 count>=2)였고, 수리 후 targeted 6 passed, 최종 Fast 239 passed/Ruff/compileall/
  mypy 10/`CONTEXT_PASS`, safety `SAFETY_PASS`; 게임 0회, PNG 0장. 필수 gate 실패 이력으로
  `loop/ESCALATE_SOL`에 승격하며 middle 독립 검수 전이다.
- latest: `docs/history/laps/20260912_lap221_middle_f2_identity_review.md`;
  probe: `docs/history/laps/probes/20260912_lap221_f2_identity_review_{probe.py,report.json}`;
  이전: `docs/history/laps/20260912_lap220_work_f2_gate_repair.md`;
  probe: `docs/history/laps/probes/20260912_lap220_f2_identity_probe_{.py,_report.json}`;
  이전: `docs/history/laps/20260912_lap219_work_f2_identity.md`;
  probe: `docs/history/laps/probes/20260912_lap218_f3_comparator_review_{probe.py,report.json}`;
  이전: `docs/history/laps/20260912_lap216_middle_f6_r1_guard_review.md`;
  probe: `docs/history/laps/probes/20260912_lap216_f6_r1_guard_review_{probe.py,report.json}`;
  이전: `docs/history/laps/20260912_lap215_work_f6_r1_guard.md`;
  이전: `docs/history/laps/20260912_lap214_middle_oracle_readjudication.md`;
  probe: `docs/history/laps/probes/20260912_lap214_oracle_readjudication_{probe.py,report.json}`;
  이전: `docs/history/laps/20260912_lap213_astra_escalation.md`;
  이전 middle 검수: `docs/history/laps/20260912_lap213_middle_f6_review.md`;
  probe: `docs/history/laps/probes/20260912_lap213_f6_producer_review_{probe.py,report.json}`.
  검수 대상 work 기록: `docs/history/laps/20260912_lap217_work_f3_comparator.md`;
  최신 work: `docs/history/laps/20260912_lap222_work_r6b_selection_response.md`.
- pre-compaction 원문: `docs/history/laps/20260912_status_lap211_compaction.md`.

## 바퀴 기록

- lap2~221 및 STATUS 원문: `docs/history/laps/`; probe 원본은 그 아래 `probes/`.
- current escalation: `loop/ESCALATE_SOL`; handoff: `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`.
