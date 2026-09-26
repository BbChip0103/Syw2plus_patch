# 2026-09-12 | lap 214 | 목표 G1 Stage B — F2/F3/R6-B 판정 계약 재결

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high, middle tier
  (진단·계획·확인). 게임 실행 0회, Stage B 0회, 구현 0건, PNG 0장.
  이 세션은 코드/테스트를 수정하지 않았다.
- 가설 / 사용자 관찰: lap207/209/211/213이 승격시킨 F2(절대 slot 동일성), F3(`FAIL_NO_EFFECT`
  상속과 `after.last` 미판독), R6-B(`count>=2`)를 **보존된 원자료**로 재결할 수 있다.
- 예상 PASS / FAIL 조건: 세 쟁점 각각에 (a) 원문 근거 위치, (b) 실제 관측, (c) 양성/음성/누락
  fixture 판정이 대응하면 재결 성립. 근거가 없거나 상충하면 해당 항목은 BLOCKED로 남긴다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 제품 source/tests/EXE/DLL/assets/
  baseline/golden/보존 evidence 변경 0. 검수 대상 해시(모두 lap213 기록과 일치, 무변경):
  `tools/runtime_env.py` `398c2b8ae4980a5c2ddd44bffba2e5330701341a575b5ad4cc519e8ad790322f`,
  `tests/test_runtime_env.py` `97d8ee154391a533677fe37dc04ee868bef39b2f6244ee3508fdac9d25818def`,
  `tools/compare_g1_stage_b.py` `7730170e610b2e4a39bb02119dd3ec73ad606b6b034d8c43f255f8a07c729ca4`,
  `tests/test_compare_g1_stage_b.py` `0f1ba54794aef7f9999c61093410438b19009df05a33a41c50955b3239d68b52`.
  신규 문서/probe만: 이 기록, `docs/STATUS.md`,
  `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`, `loop/ESCALATE_SOL`,
  `docs/history/laps/probes/20260912_lap214_oracle_readjudication_probe.py`,
  `docs/history/laps/probes/20260912_lap214_oracle_readjudication_report.json`.
  모두 uncommitted (`LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 검수 대상은 보존된
  **원본 binary 두 run**이며 후보는 실행하지 않았다.
  run A `local/runtime/20260912_010714_2914723_0/output/g1_a/evidence.json`
  sha `b266c2293422e7ef5181814078d6f07519639b7b7a1da857fb3f60cd6a16b4e2`,
  run B `local/runtime/20260912_022912_3830565_0/output/g1_a/evidence.json`
  sha `ec6ef7e00ca7c2e33d0fdb9f056dcf905425b57c7f559d05edb3b3349a7bbc12` (lap204/205 기록과 동일).
  둘 다 default two-player solo, world_bounds 180×180, owner0/owner1 각 active 2, seed 미노출.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `python3 docs/history/laps/probes/20260912_lap214_oracle_readjudication_probe.py`
  (저장소 테스트를 import하지 않고 자체 fixture를 만든다) → 리포트 JSON.
  `python3 tools/compare_g1_stage_b.py <run A> <run B>` → `UNKNOWN_SCENE_MISMATCH`, exit 2.
  게이트 재집행: `make check` → **232 passed** / Ruff All checks passed / compileall /
  mypy Success(10 files) / `CONTEXT_PASS`, `LOOP_DRY_RUN=0 bash checks/safety.sh check`
  → `SAFETY_PASS`. 새 PNG 0장, 새 run 0건.

## 측정값 / 판정

### S1 (신규, 차단, F2/F3/R6-B보다 상위) — pair에 장면 대조군이 없다

**원본 binary 두 run을 서로 비교하면 `UNKNOWN_SCENE_MISMATCH`(exit 2)다.** 패치가 개입하지
않은 원본↔원본 pair조차 같은 장면으로 인정되지 않는다. 원인은 run마다 랜덤화되는 항목 둘이다.

| 항목 | run A (010714) | run B (022912) |
|---|---|---|
| owner0 / owner1 nation | 2 / 2 | 3 / 1 |
| owner0 unit types | [31, 58] | [21, 70] |
| owner1 unit types | [31, 58] | [7, 49] |
| owner1 상대 world offset | (-71,71), (-73,69) | (-21,-50), (-23,-52) |
| world_bounds | 180×180 | 180×180 |
| `replay_seed_observed` | false | false |

owner0의 상대 배치(anchor 기준 (0,0)과 (-2,-2))와 slot 배열만 두 run에서 같다. 즉 nation과
owner1 스폰 위치가 run마다 바뀌고, 승인된 read-only 오프셋으로는 seed를 노출하거나 고정할
수단이 없다. 따라서 **승인된 fresh pair 1회는 F2/F3/R6-B를 전부 고쳐도 비교 가능한 장면을
얻는다는 보장이 없다.** 이것은 판정 술어 문제가 아니라 실험 설계(장면 통제) 문제이며 middle
단독 범위를 넘는다 → 승격한다. comparator의 scene gate 자체는 옳고 fail-closed다. 결함은
"거의 항상 걸린다"는 점이며, 완화로 통과시키는 것은 금지된 baseline 수정에 해당한다.

### F2 재결 — **조건부 반려.** slot은 안정적이나 판정 술어로는 부적절, 실제 결함은 type이다

- 근거 있음: slot `1196~1199`와 slot→owner 매핑이 두 run에서 **동일**했다
  (`slot_ids_equal_across_runs: true`, `slot_to_owner_equal: true`). 풀 상단부터 내려오는
  결정적 할당으로 보이며, 따라서 lap207이 제기한 "절대 slot은 근거가 전혀 없다"는 표현은
  원자료로는 과했다.
- 근거 없음: 그 안정성은 **원본 binary 두 run(n=2)** 에서만 관측됐다. 패치된 후보에서도
  같은 할당이 유지된다는 근거는 0이며, G2(전비/유닛 상한)·G3(최대 16인) 패치는 유닛 풀과
  플레이어 슬롯을 바꾸므로 정확히 이 가정을 깨는 변경이다. 미래의 후보에 대해 hard FAIL
  술어로 쓸 수 없다.
- **실제 결함은 slot이 아니라 type이다.** `selected_identity`는 `[slot, type]` 동일성을
  요구하는데 type은 nation 종속이고 nation은 run마다 랜덤이다(위 표). 원본 두 run조차
  type이 달랐다. probe: slot만 다른 동등 장면 → 현행 stage `FAIL`,
  type만 다른 동등 장면 → 현행 overall `FAIL`, 완전 동일 pair → `PASS`.
- 재결: **절대 slot 동일성을 FAIL 술어로 쓰지 않는다.** `selected_slot`은 그 run의
  `scene.unit_slots`로 해소해 `(owner, type, anchor 기준 상대 world offset)` 튜플로 바꾸고
  그 튜플을 pair 간에 비교한다. 이 좌표계는 comparator가 이미 scene signature에서 쓰는 것과
  같고(`_unit_records`), 같은 type이 중복돼도 위치가 달라 유일하게 해소된다. slot 불일치
  자체는 관측으로 기록하되 판정은 `UNKNOWN_SLOT_CORRESPONDENCE`(FAIL 아님)다. type 비교는
  scene gate(owner0/owner1 type 집합 일치)를 통과한 pair에서만 의미가 있으므로 순서를 유지한다.
  해소 실패(선택 slot이 scene에 없음)는 INCONCLUSIVE다.

### F3 재결 — **반려 확정.** `FAIL_NO_EFFECT`를 카드 FAIL로 상속하면 안 된다

- 원자료가 라벨을 반증한다. run B의 `drag_select` 레코드는 `result=FAIL_NO_EFFECT`이면서
  같은 레코드의 `after.last`가 `count 1`, `first_slot 1199→1198`, `selected_type 70→21`을
  담고 있다(`identity_changed: true`). "효과 없음"은 자기 payload와 모순된다.
- comparator는 그 관측을 **읽을 수조차 없다.** timeout 레코드의 `after`는
  `{"wait":…, "last":…, "tick":…}` 이라 `after.selection`이 없고
  (`after_has_selection_key: false`), `_selection()`은 `None`을 돌려준다. 그리고
  `tools/compare_g1_stage_b.py:173`이 그보다 먼저 `result != "PASS"` → `FAIL`로 닫는다.
- **결정적 증명:** 이 레코드를 baseline과 candidate **양쪽에** 넣은 자기 자신과의 pair
  (정의상 최대 parity)도 stage `FAIL`이다. 현행 계약에서는 비트 동일한 후보조차 이 stage를
  통과할 수 없다. 따라서 이 판정은 원본↔후보 동등성을 재는 술어가 아니다.
- 재결: timeout 레코드의 `result`는 카드 FAIL로 **상속하지 않는다**. `UNKNOWN_DISPUTED_ORACLE`
  로 분리하고 overall은 `INCONCLUSIVE`로 닫는다. 이는 FAIL을 푸는 방향이므로
  **불변 조건을 함께 못박는다: `UNKNOWN_DISPUTED_ORACLE`은 어떤 경로로도 stage PASS나 overall
  PASS를 만들지 못한다.** comparator는 timeout 레코드에서 `after.last`를 관측 소스로 읽되
  shape가 stage마다 다르다 — `unit_select`/`drag_select`는 `last`가 selection dict 그 자체,
  `minimap`은 `{"camera":…, "tick":…}`. `last`가 없거나 Mapping이 아니면 `INCONCLUSIVE`다.
- 상류 원인은 별건이다. `tools/runtime_env.py:2914-2917`의 분류기가 "예산 남음 + 관측창
  미절단"인 **모든** 술어 미충족을 `FAIL_NO_EFFECT`로 찍는다. 이 오라벨 자체의 수리는 R6-A이며
  같은 바퀴에 넣지 않는다.

### R6-B 재결 — **`count>=2` 기각.** 근거가 존재한 적이 없다

- 문서 근거: `analysis/memory_maps/`에 band-select 의미(건물 포함 여부)에 대한 역어셈블·관측
  기록이 **0건**이다(`band|drag` grep 유일 히트는 `player_offsets.md:665`의 무관한 산문).
  근거는 하네스 자신의 기대 문자열 `"selection count >=2 for HQ and worker"`뿐이다.
- 원자료: 드래그 (350,180)→(550,350) 후 `count 1→1`, `first_slot 1199(type70)→1198(type21)`.
  엔진은 응답했고 이동 유닛 한 기를 재선택했다. `count>=2`는 "건물도 band-select 대상"이라는
  **미증명 가정**을 판정식에 넣은 것이다. lap205가 캡처로 두 유닛의 사각형 포함을 이미 확인했으므로
  기하 미포함으로는 설명되지 않는다.
- 재결: 절대 `count>=2`를 drag 성공 술어로 쓰지 않는다. 근거 있는 최소 술어는 **"드래그 입력에
  선택 상태가 응답했다"** = `count` 또는 `(selected_slot, selected_type)` 중 하나가 before와
  다르다. Stage B의 목적인 parity는 그 위에서 "원본과 후보가 같은 응답을 보였는가"로 판정한다.
  응답 자체가 없으면 그대로 FAIL(무응답)로 닫는다.
- 잔여 UNKNOWN(재결과 무관): type70(건물)이 band-select에서 범주적으로 제외되는지는 1 run으로
  증명되지 않았다. 어느 쪽이든 `count>=2`는 무근거이므로 재결은 이 잔여에 의존하지 않는다.

### Astra 요구 fixture 대조표 (현행 → 재결 후)

| 쟁점 | fixture | 현행 판정 | 재결 후 |
|---|---|---|---|
| F2 | slot만 다른 동등 장면 | `FAIL` (probe 확인) | `UNKNOWN_SLOT_CORRESPONDENCE` |
| F2 | type/위치가 실제 다른 장면 | `FAIL` / scene mismatch | 동일 (scene gate에서 닫힘) |
| F2 | 같은 type 중복으로 대응 불명 | 판정 불가 | 상대 world offset으로 유일 해소 |
| F3 | 실제 변화 + `FAIL_NO_EFFECT` | `FAIL` (자기 자신과의 pair도 FAIL) | `UNKNOWN_DISPUTED_ORACLE` → overall `INCONCLUSIVE` |
| F3 | 실제 무변화 | `FAIL` | `UNKNOWN_DISPUTED_ORACLE` → `INCONCLUSIVE` (PASS 경로 없음) |
| F3 | `after.last` 누락/손상/비 Mapping | `FAIL` | `INCONCLUSIVE` |
| R6-B | count=1 + identity 변화 | 런타임 `RuntimeSafetyError`로 run 중단 | 응답 관측 → stage 계속 |
| R6-B | 동일 선택 유지(무변화) | 중단 | 무응답 `FAIL` |
| R6-B | 복수 선택 | PASS | PASS(응답 관측) |
| R6-B | 관측 누락 | 중단 | `INCONCLUSIVE` |

- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 코드 변경 0이므로 회귀 없음. F1/F4/F5의
  fail-closed 동작은 이번 재결이 건드리지 않으며 유지해야 한다. F3 수리는 FAIL→INCONCLUSIVE
  방향의 **완화**를 포함하므로 "PASS 경로 없음" 불변 조건을 회귀 테스트로 고정하지 않으면
  위험하다. S1(장면 통제)은 미해결이며 fresh pair의 가치를 직접 좌우한다. 이번 재결은
  middle의 기술 판정이고 제품 G1 PASS·마일스톤 사용자 승인이 아니다. 다음 새 세션이 독립 검수한다.
- 다음 한 가지: S1을 상위 tier(Astra/사용자)가 재결하기 전까지 Stage B 후보 run·원본 재실행·
  R6-A/R6-C는 계속 금지다. 그 사이 work tier는 게임 실행 없는 오프라인 수리를 한 바퀴 한 건씩
  진행한다: (1) G1-F6-R1 가드, (2) F3 comparator 수리, (3) F2 identity 재정의,
  (4) R6-B 런타임 술어 재정의. 각 건은 다음 middle이 독립 검수한다.

## 이번 바퀴 변경 파일 해시 (uncommitted, LOOP_ALLOW_COMMITS=0)

```
cf07ab7609d674cd897516d549be6a939b273ad016ab595276af5ebf8f94058a  docs/STATUS.md
c765490c72b336a90e780d5b1ccf1edf9de3958cb31fded2fb13b58eeb284bf3  docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md
0d32f74bc9d6c00498dc126f9e23acb9c302875bf7a181c74e6937a2be4bf7e2  docs/history/laps/20260912_lap214_middle_oracle_readjudication.md
572e6d217e23e1a9fb4bdaeeb3d63a75fd9f9e8d61e3b6adfe2d4915500c47f1  docs/history/laps/probes/20260912_lap214_oracle_readjudication_probe.py
442acb3327409758260813c8d1c8f394681e44616c813cc9927c62d73c4ee2ca  docs/history/laps/probes/20260912_lap214_oracle_readjudication_report.json
cc9f0850c1c5f9e213eaa05f123f097c4ba412469c5283794d7abdd9c061ac73  loop/ESCALATE_SOL
```

게이트는 문서 변경 후 재집행했다: `make check` 232 passed / Ruff / compileall /
mypy Success(10 files) / `CONTEXT_PASS`, `LOOP_DRY_RUN=0 bash checks/safety.sh check` `SAFETY_PASS`.
