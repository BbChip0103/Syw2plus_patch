# 2026-09-12 | lap 191 | 목표 G1

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high / **middle tier
  (진단·계획·확인)**. 게임 코드 hands-on 수정 없음, 게임 run 0회. lap190 work 결과의 독립 검수와
  `49B6D0 ineligible` 예외 경로의 수리 범위 확정이 배정 작업이다.
- 가설 / 사용자 관찰: lap190과 `loop/ESCALATE_SOL`은 `49B6D0 ineligible`을 **하네스 계약 불일치**로
  보고, "예외를 BLOCKED로 바꾸고 계속"하는 수리를 제안했다. 검수 가설은 그 귀인이 맞는지,
  그리고 production 레코드 누락이 정말 계약 결함인지였다.
  **결과: 그 귀인은 틀렸다.** `49B6D0 ineligible`은 원본의 정상·기대 분기이며,
  이미 lap57/lap61에서 독립 확인된 사실이다.
- 예상 PASS / FAIL 조건: lap190이 남긴 6개 해시가 재계산과 일치하고, 소스 경로가 기록대로면
  검수 성립. 예외 원인이 하네스 결함이 아니라 원본 정상 거동으로 판명되면 제안된 수리 범위를
  기각하고 새 범위를 발행한다.

## 독립 검수 결과 (1단)

lap190 기록의 6개 해시를 재계산해 **전부 일치**했다. source/tests 변경 없음.
`tools/runtime_env.py=db2113a7f1cf0fbe41f5c4ccb187a71bb9e7adbae371dd8486db46c8dabc4226`,
`tests/test_runtime_env.py=0ea2788b99220f66d7c3341b4f39a3f6dcfa09b2bd937ba8810e2a6494b1c61a`,
`manifest.json=1368053078b01dc3aef290319aa4d8e2cee476cf7b36bf222228eb4716a4a6f9`,
`g1_a/evidence.json=b266c2293422e7ef5181814078d6f07519639b7b7a1da857fb3f60cd6a16b4e2`,
`g1_a/verdict.json=6d1a47f451c1b5c86e647b5d7acfaa9a2399d55089641e0453dac8069603199c`,
`g1_a/inputs.jsonl=fbbed345b24610e556072fc364aa99f0297b98d259fb08a74c1c96ae13fd6e45`.

**lap190이 놓친 산출물:** 전체 evidence dict는 `g1_a/evidence.json`이 아니라
`output/g1_baseline.json`(191158 bytes)에 기록된다. `g1_a/evidence.json`은
`_g1_flush_input_stage`의 **마지막 flush 스냅샷**일 뿐이라 `error`/`command_branch`/
`alternate_ui_snapshot`/`primary_command_table`이 없다. lap190 기록과 `ESCALATE_SOL`은
flush 스냅샷만 인용해 "진단 데이터 없음"을 전제했으나, **근본 원인 데이터는 처음부터 보존돼 있었다.**

## 근본 원인 (RC) — 원본 정상 거동을 하네스가 치명적 오류로 취급

`output/g1_baseline.json`의 `command_branch`:

- 선택 유닛 slot **1199**, type **58**, `selection.count=1`, 식별자 before/after 안정.
- `type_predicate`: `0x009C21D4` raw `0x10`, mask `0x08` → masked `0` → **false**.
  주소 산식 검증: `0x009B524C + 58*0x394 = 0x009C21D4` 로 하네스 계산은 정확하다.
- `selected_unit_predicate` `0x00891D4C+0x94 = 0` → true. `stable=true`, `eligible=false`.

이 값들은 `analysis/memory_maps/player_offsets.md:536` **lap57 Sol 독립 검수**가 기록한
`0x009C21D4=0x10, &0x08=0`, `0x00891D4C=0`, slot1199/type58과 **완전히 동일**하다.
lap57의 결론은 이미 다음과 같았다: 원본은 `0x0049B6D0`이 아니라 `0x004992EC` false branch로 가며,
**type58은 시각·상태상 선택된 HQ가 맞아도 group2..5 command-cell 대상이 아니다.**
lap61(`:558`)은 한 걸음 더 나아가 "`49B6D0 ineligible` 관측 자체는 맞지만 이를 HQ 생산 실패로
읽을 수 없다"와 "group2..5는 HQ 생산의 필수 gate가 아니며 12-slot table이 선행 경계"를 확정했다.

이번 run의 자체 스냅샷이 lap61을 다시 확증한다:

- `primary_command_table` `0x008930A6` 12-slot 배열 = `1, 10, 14, 17, 115, 190, 72, 329` + 4×0.
  **비어 있지 않다 — HQ의 primary command table은 tick7에 이미 8개 항목으로 살아 있다.**
- `alternate_ui_snapshot`: count `0x00892376=0`, records 10개 전부 0, flags 10개 전부 0.

즉 `G1_COMMAND_CELL_TARGET=(670,490)`이 겨냥하는 group2..5 cell은 **이 HQ에는 존재하지 않는 것이
정상**이고, 실제 command UI는 primary 12-slot table이다. 하네스만 이 정상 분기를 `RuntimeSafetyError`로
올려 run을 끝냈다.

**부수 확인 — `owner0_hq_type=49` 하드코딩이 틀렸다.** `tools/runtime_env.py:2190`은 HQ를 type49로
고정하므로 이 fixture에서 `owner0_hq_candidates=0`, `owner0_hq_world=null`이 나온다. 그러나
`analysis/memory_maps/original_qhd_probe_0910.md:64`는 slot1199를 **원본 HQ 초상/스탯 패널로
독립 확증**했다. type49는 `population_5000_runtime_0910.md:50`의 **custom battle**(HQ type49 +
worker type7) 기록에서 온 값이고, lap60은 같은 slot1199를 **type70**으로 관측했다.
HQ type은 fixture/nation에 따라 49/58/70으로 달라지므로 type49 고정 술어는 HQ를 식별할 수 없다.

## 하네스 결함 (게임 결함 아님)

- **H1 (주): 증거 수집 실패가 무관한 검사를 중단시킨다.** `tools/runtime_env.py:2354`의
  `read_production_cell()`이 무방비로 호출된다. 그런데 `_g1_production_click_if_authorized`(:1561)는
  `del _production_cell`로 인자를 **아예 쓰지 않고 무조건 BLOCKED를 반환**한다. 즉 provenance는
  판정 입력이 아니라 순수 증거인데, 그 읽기 실패가 production 레코드와 그 뒤의
  `drag_select`/`minimap`까지 전부 없앤다. 이 두 단계는 command cell과 무관하다.
- **H2: A-1 불변식이 나중 추가로 회귀했다.** 카드2 A-1은 "production fail-closed를 중단에서
  기록하고 계속으로" 바꾸는 것이었고 클릭 계층에서는 구현됐다. 이후 추가된 provenance 읽기가
  A-1이 없앤 **BLOCKED 이전 중단**을 정확히 되살렸고, A-1 테스트가 그 경로를 덮지 않았다.
- **H3: 거짓 PASS 위험.** `unit_select` PASS 술어는 `count>=1`뿐인데 기록된 기대 문자열은
  "owner0 HQ visible"(:2336)이다. type을 검사하지 않으므로 이 PASS는 자기 주장을 증명하지 않는다.
  `drag_select`의 "HQ and worker"(:2403)도 같다.
- **H4: 후보 경로 진단 비대칭.** baseline except(:3156)는 `_record_g1_command_cell_error`를
  부르지만 후보 except(:3530)는 부르지 않는다. 후보에서 같은 일이 나면 진단이 전부 사라진다.
- **H5: flush 산출물 불완전.** 위 "lap190이 놓친 산출물" 항목. `g1_a/evidence.json`과
  `verdict.json`만 보면 원인 재구성이 불가능하다.

- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 이 lap 기록, `docs/STATUS.md`,
  `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`(Stage B-R 절 추가), `loop/ESCALATE_SOL`.
  **source/tests/EXE/DLL/assets/baseline/golden 변경 없음.** uncommitted, `LOOP_ALLOW_COMMITS=0`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 검수 대상은 lap190 run.
  보호 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, 후보 N/A.
  default two-player random game, PS3 tick7, owner0/1 각 nation2·active 2,
  unit_slots `1196 owner1 type31`, `1197 owner1 type58`, `1198 owner0 type31`, `1199 owner0 type58`,
  world_bounds 180×180, camera `[161,90]`, map/seed 미노출. 이번 lap의 게임 run은 **0회**.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `make check` → **209 passed**, Ruff/compileall/mypy/
  `CONTEXT_PASS`; `bash checks/safety.sh check` → **SAFETY_PASS**. 산출물 검사는 읽기 전용으로
  `local/runtime/20260912_010714_2914723_0/output/`에서 수행했다. 새 캡처 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): lap190 해시 6/6 일치 **PASS**.
  lap190·ESCALATE_SOL의 "하네스 계약 불일치" 귀인 **기각(REJECTED)** — 원본 정상 분기다.
  H1~H5 하네스 결함 **확인**. Fast 209 / SAFETY_PASS. G1 제품 판정은 **미완료 유지**.
  Stage B 재실행 **SKIP**(승인 소진 + 수리 미완).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 이것은 **모델 기술 컨펌**이며 제품 합격이 아니다.
  H3 때문에 lap190의 `unit_select: PASS`는 "HQ를 선택했다"의 증거로 쓰면 안 된다(선택 자체는
  slot1199=HQ로 별도 확증됨). 미해결 질문: tick7에서 alternate list가 완전히 비어 있는 것이
  "너무 이른 시점"인지 "type58 HQ는 원래 alternate list를 안 쓰는지" 아직 UNKNOWN이다.
  사용자 승인은 원본1회+후보1회였고 **원본1회는 lap190에서 소진**됐다. 재실행은 새 승인이 필요하다.
- 다음 한 가지: work tier가 Stage B-R의 R1~R4(게임 run 금지, 하네스·테스트만)를 구현한다.
  R5(입력 시퀀스가 무엇을 단언해야 하는가)는 승인 경계이므로 `loop/ESCALATE_SOL`로 올린다.
