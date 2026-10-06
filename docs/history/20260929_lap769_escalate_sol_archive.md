# lap 769 승격 — G5 v10 미니맵 세 모드 2단 제한부 PASS, 사용자 3단 마일스톤 경계

## 현재 판정

- lap768 원본20/v10 50 raw를 독립 재계산해 이동·공격(어택땅)·순찰의 `pending_xy` 전원 변화와 명령 종류 원본 parity를 확인했다.
- 이동 즉시 command3은 20/20·50/50, 공격은 command3 19/20·49/50+transient pending4 각1, 순찰 지연 command35는 20/20·50/50이다. fixture 55/55, gate 0→1, LUT16200, trace fatal0, alive/cleanup/source unchanged도 일치한다.
- 보호 원본 `b56986e0…8ac`에서 v10 `c3ceaa25…fad` 결정적 재빌드·copy-only·원복·버전/경로/unknown 거부 PASS. 현재 source `make check` 1136 passed·5 skipped, `SAFETY_PASS`.
- 기술 2단은 `PASS_WITH_LIMITS`: A/B/C/D/F/H PASS, E 조건부, G `BLOCKED(env)` 수용. 정상 로비 `game_type==3` UI 접근성·실제 LAN·기존 N/A/edge 제한은 유지한다.
- 작업 중 최신 사용자 사전 승인(18:4x)이 도착했다: lap769가 `PASS_WITH_LIMITS`면 재질문 없이 G5 v10을 알려진 한계와 함께 3단 승인·종료하고, 다음은 G1이며 G2 전체 점검은 G1 뒤로 순연한다. 기술 조건은 충족했지만 이 세션은 마일스톤 경계에서 직접 마감하지 말라는 호출 지시를 따른다.

## 승격 작업자가 이어서 검증할 한 가지

후보 SHA·위 제한·사전 승인 조건 충족을 확인해 APPROVALS에 G5 v10 3단 승인·종료를 기록하고, 사용자에게 재질문하지 않은 채 STATUS의 다음 한 가지를 G1(원본 구도 유지 1600×1200) 착수로 전환한다. 상세 `docs/history/laps/20260929_lap769_middle_g5_v10_minimap_modes_review_pass_escalate.md`.

# lap 768 승격 — G5 미니맵 이동·공격·순찰 paired PASS, 사용자 3단 마일스톤 경계

## 현재 판정

- lap768 work가 새 격리 game/prefix/display에서 owner0/type2 55기 fixture를 만들고 원본20/v10 50을 paired 실행했다.
- 진단 gate `0x97597c`는 양쪽 `0→1`로 열렸고, 이동·공격·순찰 버튼 뒤 미니맵 좌클릭에서 `pending_xy`가 각각 원본 `20/20/20`, v10 `50/50/50` 전원 변화했다. 원시 명령 신호도 move command3, attack pending4 관측, patrol command35로 대응했다.
- 양쪽 probe `PASS_MINIMAP_MODES_*`, trace fatal 없음, alive/cleanup/source unchanged PASS. v10 후보 SHA `c3ceaa25…fad`, 원본 SHA `b56986e0…8ac`.
- 집중 pytest 5 passed, `make check` 1136 passed·5 skipped, ruff/compileall/mypy/context/`SAFETY_PASS`. 이 결과는 진단 write 조건이며 정상 game_type UI·멀티·G5 A~H 독립 검수·사용자 승인을 대체하지 않는다.

## 승격 작업자가 이어서 검증할 한 가지

middle/승격 작업자가 lap768 raw JSON·fixture·입력 계약·후보 SHA를 독립 재검수하고, 기존 G5 v10 `PASS_WITH_LIMITS` 제한(G `BLOCKED(env)`, E 조건부, 정상 game_type UI 미검증, N/A/edge)을 함께 확인해 사용자 G5 3단 판단에 재상정한다. 사용자 판단 전 G5 종료·G1 재개를 하지 않는다. 상세 `docs/history/laps/20260929_lap768_work_g5_minimap_command_modes_paired.md`.

# lap 767 승격 — G5 v10 2단 제한부 PASS, 사용자 3단 마일스톤 경계

## 현재 판정

- lap766 original20/v10 50 paired raw를 lap767 middle이 독립 재계산했다. 양쪽 Shift 추가 `1→2`, 제거
  `2→1`, anchor1 제거·anchor2 유지·anchor1 명령 배제, 선택 상한20/50가 모두 일치한다.
- lap765 `2→0/0→1` raw는 첫 Shift 클릭부터 비anchor slot `1149`가 섞여 있었고 paired 정상 전이에서
  재현되지 않았다. 제품 회귀가 아닌 단일 실행 이상치로 해소한다.
- 보호 원본 `b56986e0…8ac` → v10 `c3ceaa25…fad` 결정적 build/copy-only/원복·버전 거부·diff 범위 PASS.
  selection patch 59 passed, 현재 source `make check` 1134 passed·5 skipped, `SAFETY_PASS`.
- 기술 2단은 `PASS_WITH_LIMITS`: A/B/C/D/F/H PASS, E 조건부, G `BLOCKED(env)` 수용. 정상 game_type
  미니맵 UI 경로·E 가림·기존 N/A/edge·실멀티 동기화 제한은 유지한다. 제품/사용자 승인은 아니다.

## 승격 작업자가 이어서 검증할 한 가지

lap767 상세 기록과 후보 SHA·제한 목록을 확인해 G5 v10을 사용자 3단 마일스톤 판단에 재상정한다.
사용자가 승인하기 전에는 G5 종료나 G1 재개를 선언하지 않는다. 상세
`docs/history/laps/20260929_lap767_middle_g5_v10_shift_recheck_pass_escalate.md`.

# lap 766 승격 — G5 v10 Shift paired는 이상치 미재현, 새 middle 독립 재검수 필요

## 현재 판정

- lap766 work가 보호 원본20/v10 50을 새 Wine prefix/Xvfb와 동일 synthetic 55기 fixture로 fresh paired 실행했다.
- 양쪽 Shift 단일 추가는 `1→2`, 제거는 `2→1`; anchor 제거·잔여 anchor 유지·잔여 anchor 명령 배제와 20/50 선택 상한이 모두 PASS했다.
- 원본/candidate JSON SHA는 각각 `5e8f742d901a2332f57db3654823c9aff55f15eefda6922a9af099a4762deb7f`, `813435cb69fdc9b52ac364441da9897af7ced48cac0b884587885ce162863bf4`다. `source_unchanged`와 cleanup은 양쪽 PASS, 전체 Fast는 `1134 passed, 5 skipped`다.
- lap765의 `2→0/0→1`은 이번 계약에서 재현되지 않았지만, 이것만으로 G5 A~H 전체 PASS나 사용자 3단 승인을 선언하지 않는다.

## 승격 작업자가 이어서 검증할 한 가지

새 middle(Sol/Opus5)이 lap765 및 lap766 raw의 fixture·클릭 계약·후보 v10 SHA를 독립 대조하고 G5 A~H 전체 판정을 갱신한다. G 멀티 `BLOCKED(env)`, 정상 game_type 미니맵 경로 미검증, E 조건부 및 기존 N/A/edge 제한은 유지한다. 그 판정과 사용자 3단 판단 전에는 G5 종료·G1 재개를 하지 않는다.

# lap 765 이전 기록 — G5 v10 전체 middle HOLD, Shift paired 귀속 필요

## lap765 당시 판정

- v10 재빌드/byte-exact 원복, 항목 (1) 50기 save/load·양방향 호환, 항목 (2) 수확 V 및 진단 gate
  미니맵 원본20/v10 50, `make check` 1134 passed·5 skipped, `SAFETY_PASS`는 독립 대조에서 수용했다.
- fresh v10 핵심 coverage는 full drag 4종·double-click·51번째 거부·이동/정지/홀드/순찰 50/50 PASS.
- 그러나 Shift 단일 추가가 `2→0`, 제거가 `0→1`(`removed_anchor1=false`, `kept_anchor2=false`)로
  과거 승인 패턴 `2→3`, `2→1`과 충돌했다. `status=COMPLETE`/exit 0은 의미 PASS가 아니다.
- 원본 paired가 없어 제품 회귀와 현재 coverage 하네스의 클릭 좌표/타이밍 문제를 구분하지 못했다.
  그래서 G5 A~H 전체는 `HOLD`; 사용자 milestone 재상정과 G1 재개를 금지한다.
- raw JSON SHA256 `660f1d2ea595a9a63323c19fbf60cf30c65cb8dec692e964086d633b66d2cb31`, 상세
  `docs/history/laps/20260929_lap765_middle_g5_v10_final_review_hold_shift_click.md`.

## 승격 작업자가 이어서 검증할 한 가지

work tier가 현재 `tools/g5_command_coverage_probe.py` 그대로 original20과 v10 50을 fresh paired 1회
실행해 Shift add/remove를 대조한다. 원본도 같은 실패면 전용 `tools/g5_shift_click_add_probe.py`의
안정된 클릭 계약과 비교해 coverage 하네스만 최소 수리하고 paired 재실행한다. 원본 PASS·v10 FAIL이면
v10의 인게임 선택 상태 오염을 귀속해 최소 수리한다. 성공 후 새 middle이 raw를 독립 재검수한다.

# lap 764 승격 — G5 사용자 항목 (2) work PASS, middle 독립 재검수 경계

## 현재 판정

- lap764 work가 v2 probe와 회귀 테스트를 추가했다. 원본과 v10을 각각 새 Wine prefix/Xvfb에서
  명시적 owner0/type2 55기 fixture로 실행했고, 보호 원본/참고 저장소/제품 EXE 원본은 쓰지 않았다.
- 진단 write `0x97597c=1`은 격리 게임 프로세스에만 적용했다. LUT non-`0xff`는 16200/32400,
  실제 baked center `(90,553)` 우클릭을 사용했다.
- 원본: 선택20/20, `pending_xy` 20/20 변화, 명령 필드20/20 변화, hit-test 성공2967회.
- v10 후보 `c3ceaa25dea98232234759a332b867d92a669f63a03c3f453d3199cc329ebfad`: 선택50/50,
  `pending_xy` 50/50 변화, 명령 필드50/50 변화, hit-test 성공1441회.
- 두 실행 모두 crash0, `alive_at_end`, `cleanup.ok`, `source_unchanged` PASS. 실행 game 사본 3개는
  삭제하고 manifest/output/prefix/log/JSON/capture를 보존했다.
- `make doctor` PASS; `make check` 1134 passed·5 skipped; compileall/ruff/mypy/context PASS.
  상세 `docs/history/laps/20260929_lap764_work_g5_minimap_command_effect_paired_pass.md`.

## 승격 작업자가 이어서 검증할 한 가지

새 middle(Sol/Opus5)이 v10 기준 사용자 항목 (1)+(2)와 G5 A~H 전체를 독립 재검수한다. 특히
lap764의 진단 조건(`game_type` 정상 UI 경로 미확인, `0x97597c` 강제 write)을 제품 정상 경로와
분리해 판정하고, G 멀티 `BLOCKED(env)`·E 조건부·N/A 항목을 제한으로 명시한다. 이 재검수와
사용자 3단 판단 전에는 G5 종료나 G1 재개를 선언하지 않는다.

# lap 665 승격 — G5 2단 전체 승인 HOLD, 공격 명령 50 증거 필요

## 현재 판정

- lap664의 선택/호출/이동/save-load 50 결과는 독립 검수에서 제한 승인했다.
- DESIGN G5의 실제 적 대상 공격 명령 50은 미검증이므로 전체 2단은 `INCONCLUSIVE/HOLD`다.
- 제품 G5 PASS·멀티 동기화 PASS·사용자 milestone 승인은 선언하지 않는다.
- 보호 원본 SHA: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
- 최종 후보 SHA: `ae495fa5a1498597c265ad9bcae6444f564ade92adb311a3c413c4fb9996b5b7`.

## 이번 바퀴 근거

- 후보/원본 JSON·capture SHA 전부 일치, 원본에서 재빌드한 후보가 보존 artifact와 byte-identical `ae495fa5…`다.
- 후보 selected/recalled/loaded-recalled `50/50/50`, movement nonzero50, stock group20+field49; 원본 `20/20/20`, movement20.
- disassembly에서 `0x40F790 ret4`, H3 `0x4E4D17`의 추가 cleanup 제거, `0x40F7D0` 3인자 호출을 확인했다.
- fresh targeted G5 `14 passed`, `SAFETY_PASS`, `CONTEXT_PASS`; lap664 full 로그의 `914 passed`와 lint/type/context PASS를 확인했다.
- `tools/g5_candidate_drag_probe.py`는 빈 지면 우클릭 후 command nonzero만 세며 적 표적·공격 opcode/target을 만들거나 판별하지 않는다. 상세 `docs/history/laps/20260926_lap665_middle_g5_independent_review_incomplete.md`.

## 승격 작업자가 이어서 검증할 한 가지

work tier가 기존 동일 55기 fixture에 명시적 적 표적을 추가하고 50기 선택 후 실제 공격 입력을 보낸다. candidate는 50기 모두의 공격 command/target이 그 표적을 가리키고, 원본 paired는 20기만 그러는지를 raw로 기록하며 예외·cleanup·source 불변도 확인한다. 실패하면 공격 패커/consumer 한 곳만 귀속해 수정·재실행하고, 성공하면 새 중간 tier가 전체 G5 2단을 다시 검수한다. 멀티 동기화는 계속 `UNKNOWN`으로 별도 표시한다.

# lap 666 승격 — 실제 적 대상 공격 probe 필수 게이트 FAIL-B

## 현재 판정

- `tools/g5_candidate_drag_probe.py`에 owner1 type2 적 fixture, 실제 우클릭, 선택 유닛별 command/target raw 판정을 추가했다.
- 후보 `ae495fa5a1498597c265ad9bcae6444f564ade92adb311a3c413c4fb9996b5b7`는 4회 fresh 격리 실행에서 선택 `50/50`을 유지했지만 공격 판정은 모두 `attack_command_count=0`, `target_match_count=0`, `pass=false`였다.
- 최신 캡처에서 적 fixture 생성은 보였으나 우클릭 결과가 `command=3,target=0`인 비표적 이동으로 남았다. 첫 probe의 잘못된 PASS 라벨은 코드에서 fail-closed로 수리했다.
- 후보 EXE SHA·보호 원본 SHA·cleanup/source 불변은 유지됐다. G5 제품 PASS·2단 승인·사용자 milestone 승인은 선언하지 않는다.

## 승격 작업자가 이어서 검증해야 할 한 가지

최신 `20260926_lap666d_g5_attack_candidate`와 동일 입력을 먼저 원본에 fresh 실행해 `command=3,target=0`이 원본에서도 재현되는지 확인한다. 그 뒤 raw/capture로 실제 적 sprite hit-test 좌표 및 원본 우클릭 공격 opcode/target 저장 필드를 귀속하고, 한 가지 최소 probe/패치만 적용해 candidate50 대 original20 fresh paired 공격 실행을 수행한다. 필수 공격 게이트가 닫히기 전에는 G5 2단 재검수나 사용자 승인으로 넘기지 않는다.

# lap 667 승격 — 원본 공격 입력도 귀속 실패

## 현재 판정

- 원본 보호 SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`는 네 fresh 격리 실행 모두 불변이었다.
- 원본 선택 대조는 매번 `20/20`, cleanup은 성공했지만 공격 판정은 모두 `attack_command_count=0`, `target_match_count=0`, `pass=false`였다.
- 우클릭 `(548,476)`, 화면 crop에서 귀속한 우클릭 `(715,460)`, 화면 중심 우클릭 `(548,450)`, `A` 후 `(548,450)` 좌클릭 모두 공격 opcode/target을 만들지 못했다.
- 현재 probe 변경은 `tools/g5_candidate_drag_probe.py`와 `tests/test_g5_candidate_drag_probe.py`에만 있으며, 후보 EXE/원본은 수정하지 않았다. 후보50 paired와 제품 G5 승격은 중단한다.

## 이번 바퀴 근거

- 회귀 `PYTHONPATH=. pytest -q tests/test_g5_candidate_drag_probe.py` → `4 passed`; `python3 -m compileall` → PASS.
- 직접 `ruff` 실행은 PATH에 없어 이번 바퀴에서 수행하지 못했다. `make check`와 후보 fresh 실행도 필수 원본 공격 귀속 실패 후 중단했다.
- 원본 결과 JSON SHA: `ff36fc6d…40a6a54`(old click), `6bbab5b7…98286f8`(715,460), `bfdb518a…1b47de4`(548,450), `bc88a457…604fbe7`(A+좌클릭). 전체 artifact는 `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260926_lap667_g5_attack_original*`에 보존했다.
- 현재 파일 SHA: `tools/g5_candidate_drag_probe.py`=`f927a79d…963920c`, `tests/test_g5_candidate_drag_probe.py`=`8c472dd6…3859b14`; 보호 원본과 runtime copy SHA는 모두 일치했다.

## 승격 작업자가 이어서 검증해야 할 한 가지

최신 원본 raw/capture에서 실제 공격 조작 계약을 독립 귀속한다. 특히 `A` 키가 실제 공격 모드로 전환됐는지, owner1 type2가 hit-test 가능한 적인지, 공격 command의 실제 opcode와 target field/handle 표현이 `+0x290/+0x64A`인지 확인한 뒤, 한 가지 최소 probe 또는 제품 수리만 적용한다. 귀속 전 `FUN_004AE550` 수정, 후보50 실행, G5 2단 재검수, 사용자 승인 승격은 금지한다.

# lap 668 승격 — 공격 field reader 수정 후에도 원본 target 귀속 FAIL-B

## 현재 판정

- `tools/g5_candidate_drag_probe.py`의 공격 reader를 `+0x290/+0x384/+0x388/+0x38C`로 교체하고 명령 직후·수 tick 뒤 두 샘플을 보존했다. 회귀 4개, compileall, diff-check, `SAFETY_PASS`, `CONTEXT_PASS`.
- 보호 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`은 두 fresh 격리 실행 모두 불변. selection `20/20`, cleanup `true`.
- fresh1은 적 `(49,145)`에 click `(548,450)` 후 raw `pending_xy=(47,143)`, 공격 상태 8/20, target UID 0/20. fresh2는 적 `(149,141)`에 click `(580,450)` 후 raw `pending_xy=(148,143)`, 공격 상태 5/20, target UID 0/20.
- 필수 원본 공격 gate가 2회 연속 `FAIL-B`이므로 후보50 paired, `make check`, G5 2단 검수 및 사용자 승격은 중단한다. 제품 EXE/원본 변경은 없다.
- 결과 JSON과 캡처는 `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/g5_lap668_original_attack*`에 보존했고, 약 2.2GB인 각 회차 `game` 사본만 삭제했다. 상세 `docs/history/laps/20260926_lap668_work_g5_attack_fields_blocked.md`.

## 승격 작업자가 이어서 검증해야 할 한 가지

최신 두 raw/capture를 독립 대조해 화면→world hit-test 변환과 owner1 type2 적의 실제 selectable/hit-test 조건을 확정한다. target UID가 `+0x38C`에 쓰이는 실제 입력을 귀속한 뒤에만 한 가지 최소 probe 보정 후 original20→candidate50 paired fresh를 수행한다. 그 전에는 `FUN_004AE550` 수정과 G5 2단/사용자 승인 승격을 금지한다.

# lap 670 승격 — 좌표 확정, 공격 target UID는 여전히 미해결

## 현재 판정

- 새 진단 `tools/g5_screen_world_calibration.py`(제품 EXE 미변경)로 같은 실행 안에서 9점 우클릭 move 샘플을 모아 `world=M@screen+c` 아핀 변환을 풀었다. 역변환으로 계산한 클릭은 두 fresh 원본 모두 적 정확 좌표와 완전히 일치했다(잔차<0.44tile). **화면→world hit-test는 이제 확정이다.**
- 같은 정확 좌표에서 `A`+좌클릭은 여전히 `+0x38C`(target uid)=0을 유지했다. run1은 `+0x290=3`(이동), run2는 `+0x290=8`(제3의 상태, 아직 미해석)로 두 실행 결과가 서로 달랐다.
- G2에서 이미 검증된 원본 issuer(`FUN_00415480`, bridge op=8)를 같은 fixture에 교차검증했지만 직전 UI 클릭이 이미 `+0x290`을 8로 바꿔둔 오염된 상태 위에서 실행돼 원인이 분리되지 않았다(`raw_return=0`, `+0x38C=0`).
- side byte(`players[].b5`, owner0=0·owner1=1)는 서로 달라 NF-a(같은 편 거부) 가설은 배제된다(G2 lap524/525 선례와 일치).
- 보호 원본 SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`는 두 fresh 모두 불변. 후보 EXE는 미실행. 상세 `docs/history/laps/20260926_lap670_work_g5_screen_world_calibration.md`.

## 승격 작업자가 이어서 검증해야 할 한 가지

다음 work는 middle 없이: ① op8 진단을 **사전 UI 공격 클릭 없이 첫 명령으로** 재실행해 오염되지 않은 `raw_return`/`+0x384/+0x388/+0x38C`을 확인, ② run2의 `command=8`이 `FUN_0048DDD0` 점프표(`0x48ea5c`)의 어떤 분기인지 정적으로 확인, ③ 등각 스프라이트가 타일 바닥보다 화면 위쪽에 그려질 가능성을 감안해 계산된 클릭 y좌표를 위로 tile-height 단위로 스윕하며 A+좌클릭 후 `+0x38C` 귀속을 재확인한다. 세 가지 원인이 좁혀지기 전에는 `FUN_004AE550` 수정, candidate50 paired 실행, G5 2단/사용자 승인 승격을 금지한다.

# lap 673 승격 — 화면 diff UI 공격 클릭 3회 연속 FAIL, 판정 방식 재정의 요청

## 현재 판정

- 2026-09-26 09:25 지시(좌표계산 폐기, 스폰 전후 캡처 diff로 새 스프라이트 중심 클릭)를 구현해 원본-only 2회 실행(mobile type2 target, run1 무보정/run2 안정성필터+성분라벨링). 09:55 지시(히트박스가 큰 owner1 건물 type46으로 목표 변경, op8로 도메인 게이트 선확인 후 우클릭)를 같은 세션에서 즉시 이어 구현해 1회 추가 실행. 3회 모두 UI 클릭 PASS 실패.
- **양성 확정 사실 2건(모두 라이브 op8로 확인, 클릭 문제와 무관)**: ① 스폰 직후 저tick에서 bridge op8은 type2→type2, type2→type46 모두 깨끗하게 성공(`raw_return=1`,`order_accepted=true`,`command=4`,target uid 일치) — lap672가 관찰한 "op8이 tick이 높을수록 거부 사유가 달라짐"은 type/도메인 문제가 아니라 시간경과(느린 UI 흐름) 때문임을 확정. ② `type46` 건물은 정적 분석대로 `+0x1BC==1`(공격 대상 자격)이 라이브 op8로도 재확인됨.
- **클릭 경로 실패의 재현되는 패턴**: diff+안정성필터+8연결 성분 라벨링 파이프라인은 **공격자(owner0) 자신의 스프라이트는 2/2 실행 모두 확실하게 격리**했다(both times: bbox 약 26×31px, confident_single_blob=true). 그러나 **목표(owner1) 스프라이트는 2/2 실행 모두 안정성 필터에 의해 과도하게 제외**됐다 — 사후 분석으로 그 이유가 "목표 배치 좌표가 화면의 국소 고잡음 영역(예: run2는 공격자 위쪽, building run1은 화면 우하단 구석)과 우연히 겹쳤기 때문"으로 좁혀졌다. 화면 중앙부 크롭의 기준-프레임 평균 diff는 7.0으로 낮아(카메라 드리프트 아님, ±3px 시프트로도 개선 없음) 잡음이 전역이 아니라 산재한 국소 영역임을 확인했다.
- 보호 원본 SHA `b56986e0…c9c08a8ac`는 3회 실행 모두 불변. `source_unchanged=true`·`cleanup.ok=true` 3/3. `make check` 944 passed, ruff/compileall/mypy/`CONTEXT_PASS`·`SAFETY_PASS` 모두 PASS(로그 `logs/gates/lap673_make_check_2.log`). 상세 `docs/history/laps/20260926_lap673_work_g5_type2_ui_attack_diff_probe.md`.
- 09:55 지시가 명시한 "3회 안에 안 되면 strategy로 G5 공격 판정 방식 자체를 재정의" 기준에 도달했다(lap672 좌표계산 6회 + lap673 diff 3회 = 누적 9회, 클릭 기반 PASS 0회).

## 승격 작업자가 이어서 검증해야 할 한 가지

strategy(Opus5/Astra)는 다음 중 하나를 판정한다: (a) diff 파이프라인을 폐기하지 않고 목표 배치를 화면 중앙 안전지대로 제한 + 안정성 기준을 연속 다중 프레임으로 늘려 국소 고잡음 영역을 사전 회피하는 최소 보정으로 계속할지, (b) 오너별 색상 채널 시그니처 등 diff와 다른 hit-test 방식으로 전환할지, (c) UI 클릭 자체를 G5 공격 판정 기준에서 빼고 op8류 라이브 엔진 주문(이미 type2→type2·type2→type46 모두 PASS 확인됨)만으로 "제품이 공격을 지원한다"는 판정 기준을 재정의할지. 어느 쪽이든 다음 work가 middle 없이 바로 구현·실행하도록 방법을 하나만 좁혀 지시한다. candidate50 실행과 G5 2단/사용자 승인 승격은 이 판정 전까지 금지한다.

## 운영자 해소 (2026-09-26 10:31)
**2026-09-26 10:31 운영자 판정(strategy 대행, lap673 승격 해소):** 적 스프라이트/건물 클릭은 G5와 무관한 측정 도구 문제라 **중단**한다. G5 공격 판정을 다음으로 재정의: ① UI 드래그로 50기 선택(이미 검증된 경로) → ② **A+지면 좌클릭(공격 이동)** 또는 공격 버튼+지면 클릭으로 명령 발행 — 스프라이트를 맞힐 필요 없음 → ③ 선택 전원의 `+0x384/+0x388`(pending cmd/xy) 또는 `+0x290`이 공격이동 계열로 바뀐 유닛 수를 센다(원본 20 / 후보 50 paired). ④ 목적지 근처에 owner1 적(op8 게이트 PASS 확인된 type2/type46)을 두어 도착 후 자동교전으로 `+0x290==4` 유닛 수도 보조 지표로 기록. 50 중 20만 받으면 그때 `FUN_004AE550` 20칸 복사를 분할 발행으로 고친다. 이 판정 방식은 확정이며 추가 strategy 회부 없이 work가 바로 구현·실행한다. ESCALATE_SOL의 lap673 섹션은 이 결정으로 해소.

# lap 674 승격 — 지면 클릭 공격이동 브로드캐스트, 두 입력 경로 모두 반증

## 현재 판정

- 10:31 판정을 그대로 구현(`tools/g5_attack_move_broadcast_probe.py`): 드래그50 선택 → 목적지 지면 클릭(A핫키 또는 공격툴바버튼) → 선택 전원의 command/pending 계열 판정. 원본-only 3회 실행.
- run1은 목적지 화면좌표(989,393)가 **실제 렌더 캔버스(약 800×600) 밖 검은 여백**이라 클릭이 완전히 무효였다(20기 전원 변화 0). 목적지 오프셋을 (0,-10)으로 좁혀 캔버스 안(732,181)으로 수정.
- run2(A핫키+지면클릭)·run3(공격툴바버튼+지면클릭) 모두 목적지가 owner1 목표와 **같은 지점**이었음에도 **선택된 19/19 신선한 type2 유닛 전원이 평범한 이동 명령(command=3)만 받았다** — 공격 계열(`command==4`/`pending&0xffff==4`)로 전환된 신선 유닛은 0/19. worker(이전 lap의 잔여 비정상 상태)에서만 노이즈성 순간 플래그 1회 관측.
- 이는 lap667~673의 스프라이트 클릭 9회 실패에 더해, **UI 클릭(키보드 A핫키·공격 툴바버튼 둘 다) 기반 공격 명령이 이 하네스에서 단 한 번도 성공한 적이 없다**는 훨씬 강한 수렴 증거다. 반면 엔진 자체 issuer(bridge op8)는 매번 확실히 성공한다.
- 보호 원본 SHA `b56986e0…c9c08a8ac`는 3회 실행 모두 불변. `source_unchanged=true`·`cleanup.ok=true` 3/3. `make check` 953 passed, ruff/compileall/mypy/`CONTEXT_PASS`·`SAFETY_PASS` 모두 PASS. 상세 `docs/history/laps/20260926_lap674_work_g5_attack_move_broadcast_blocked.md`.
- 10:31 지시의 "추가 strategy 회부 없이 work가 구현" 전제가 실제 실행 증거로 반증됐으므로(서로 충돌하는 실제 증거 예외 조항), candidate50 실행 전에 승격한다.

## 승격 작업자가 이어서 검증할 한 가지

strategy(Opus5/Astra)는 다음 중 하나를 판정한다: (a) UI 클릭 기반 공격 판정을 G5 기준에서 제외하고 엔진 자체 issuer(op8, type2→type2·type2→type46 라이브 PASS 기확인)로 "제품이 공격을 지원한다"는 판정으로 재정의, (b) 합성 XTest 클릭이 이 엔진의 공격 입력 코드 경로에서 왜 매번 실패하는지(호버/타겟 캐시 갱신 메시지 누락 등) 근본 원인을 정적/동적으로 추적, (c) 다른 입력 주입 방식(SendInput류, 직접 WM_LBUTTONDOWN 포스트 등) 시도. 어느 쪽이든 다음 work가 middle 없이 바로 구현·실행하도록 방법을 하나만 좁혀 지시한다. candidate50 실행과 G5 2단/사용자 승인 승격은 이 판정 전까지 금지한다.

## 운영자 해소 (2026-09-26 11:05, lap675)
**2026-09-26 11:05 운영자 판정(strategy 대행, lap675 승격 해소 — 추가 strategy 회부 금지):** 합성 클릭으로 공격 입력을 만드는 경로(스프라이트/건물/공격이동, 총 12회+)는 G5와 무관한 도구 한계로 **종료**한다((b)(c) 기각). (a)를 보강한 (a')로 판정한다: 공격 여부는 op8(엔진 issuer)로 이미 양성 확정. G5의 실제 위험은 **선택 전원에게 명령을 퍼뜨리는 경로(`FUN_004AE550` 패커, 20칸 고정 복사)**다. 따라서 work는 ① 우클릭/명령 핸들러가 선택 목록 전체에 명령을 발행할 때 부르는 **선택-브로드캐스트 함수**(패커 `FUN_004AE550`을 거치는 호출자)를 정적으로 찾아, ② 브리지에서 그 함수를 직접 호출(cmd=공격, target=owner1 적 uid)해 UI 드래그로 선택한 전원에게 퍼지는지 센다(`+0x384` 공격 계열 또는 `+0x290==4`, `+0x38C==적 uid`). ③ 원본 20 / 후보 50 paired. 후보가 20만 받으면 즉시 패커를 분할 발행 또는 50칸으로 고쳐 재실행(구현 우선). lap675 관측(공격툴바/A핫키 지면클릭 → 선택 19/19 이동 명령 수신)은 브로드캐스트 자체는 작동함을 보이는 보조 증거로 기록.

# lap 676 승격 — lap675 전제(FUN_004AE550=명령 브로드캐스트) 정적 반증

## 현재 판정

- lap675(11:05 운영자 판정)는 다음 work가 "선택 전원에게 명령을 퍼뜨리는 경로 = `FUN_004AE550` 패커"의 호출자를 정적으로 찾아 브리지에서 cmd=공격으로 직접 호출하라고 지시했다.
- 이번 lap은 호출자를 찾기 전 `tools/g5_command_packer_xrefs.py`(capstone decoded-call-immediate 전용, `.text` 전수)로 `FUN_004AE550`의 실제 22개 직접 호출 지점을 xref 검증했다.
- **결과: 22곳 전부 유닛 주문 코드(1/3/4/7/8/9)와 무관한 opcode(`0x52,0x56,0x19b,0x19d,0x19e,0x19f,0x1a0,0x1a1,0x1ae..0x1bc`)만 사용한다.** 15곳은 단일 함수(`0x48ec30`)가 구조체 sticky 플래그 14개를 순회하며 플래그별로 한 번씩 flush하는 알림성 구조이며, "우클릭 시 선택 전체에 명령 발행" 패턴이 아니다.
- **알려진 주문 발행 함수 4개(`FUN_00415480` op8 issuer, `FUN_00415880` 대체, `FUN_00445D30` 부대지정, `FUN_0040F7D0` order consumer) 중 어느 것도 `FUN_004AE550`을 직접 호출하지 않는다**(각 본문 +0x2000B 스캔, decoded call-immediate 0건).
- `FUN_004AE550`이 전역 선택 배열(`0x00899028`, lap627이 이미 "선택 엔트리 배열 20칸"으로 확정)을 읽는 것 자체는 사실이나 소비처(`call 0x4a3c10`, this=`0x892410`)는 명령 발행이 아니라 UI/알림 이벤트로 보인다(미확정).
- 회귀 `tests/test_g5_command_packer_xrefs.py` 3 passed, ruff/compileall PASS, `SAFETY_PASS`. 제품 EXE/원본 0 변경. 상세 `analysis/memory_maps/g5_command_packer_xref_falsification_lap676.md`, `docs/history/laps/20260926_lap676_work_g5_command_packer_xref_falsified.md`.
- lap675 지시의 핵심 전제가 정적 증거로 반증되었으므로(서로 충돌하는 실제 증거 예외 조항), 브리지 직접 호출 구현·candidate50 실행 전에 승격한다.

## 승격 작업자가 이어서 판정할 한 가지

strategy(Opus5/Astra)는 다음 중 하나를 판정한다: (a) 실제 주문 발행 경로를 `FUN_0048DDD0` 점프표(`0x48ea5c`, `0x48ec30` 함수와는 다른 코드 — 혼동 금지)의 각 분기를 xref로 추적해 새로 특정하고 그 경로에서 선택 배열 20칸 상한이 실제로 재현되는지 확인, (b) `FUN_004AE550`의 실제 소비자(`0x4a3c10`, this=`0x892410`)를 문자열 테이블 대조로 UI/알림 시스템임을 확정하고 G5 공격 판정 자체를 op8류 라이브 issuer(단일 유닛, 기확인 PASS) 기준으로만 재정의(선택 50 전체 브로드캐스트 요구를 완화), (c) 간접/레지스터 호출 스캔(데이터플로우)으로 `FUN_004AE550` 호출자 후보를 넓혀 우클릭 핸들러와의 연결을 다시 찾는다. 어느 쪽이든 다음 work가 middle 없이 바로 실행하도록 방법을 하나만 좁혀 지시한다. `FUN_004AE550` 수정, candidate50 paired 실행, G5 2단/사용자 승인 승격은 이 판정 전까지 금지한다.

## 운영자 해소 (2026-09-26 11:15, lap676)
**2026-09-26 11:15 운영자 판정(strategy 대행, lap676 승격 해소 — 추가 strategy 회부 금지):** lap676 반증 수용: `FUN_004AE550`은 명령 브로드캐스트가 아니다(수정 대상에서 제외). 핵심 사실: lap664에서 UI 이동 명령은 선택 50기 전원에게 전달됐다 ⇒ 선택 목록 전체를 도는 명령 발행 루프가 이미 50을 처리한다. 방법 하나로 좁힌다(a 변형): ① **이동 명령이 50기에 퍼진 실제 루프**를 찾는다 — 정적으로는 재배치된 선택 카운트(`0x0108C000`)/엔트리(`+4`)를 읽는 코드 중 유닛별 주문 함수(`FUN_00415480`/`FUN_00415880`/`FUN_00445D30`/`FUN_0040F7D0` 또는 `FUN_0048DDD0` 분기)를 부르는 루프; 필요하면 후보 런타임에서 UI 이동 1회 중 해당 주문 함수 진입 횟수를 세는 방식으로 동적 확인. ② 그 루프의 공격 분기가 같은 선택 카운트를 쓰는지, 별도 0x14 상한이 없는지 확인. ③ 그 루프 함수를 브리지로 직접 호출(cmd=공격, target=owner1 적 uid)해 원본20/후보50 paired로 `+0x290==4`·`+0x38C==적 uid` 유닛 수를 센다. 후보가 20에서 끊기면 그 상한을 고친다(구현 우선).

## 운영자 해소 (2026-09-26 13:09, lap678)
**2026-09-26 13:09 운영자 결정(lap678 결과 반영, 방식 지정):** 명령 레코드 구조체를 20→50word로 키우고 네트워크 스테이징(`0x893130`)·로컬 큐(`0x8931e8`)를 함께 바꾸는 안은 **멀티플레이 패킷 형식이 바뀌므로 채택하지 않는다.** 대신 **20기씩 분할 발행**: 스택 빌더(선택 배열을 읽어 20칸 레코드를 채우는 곳)를 찾아, 재배치된 선택(`0x0108C000` count, `+4` 엔트리)을 20개 단위 청크로 나눠 **같은 명령 레코드를 청크 수만큼(최대 3회) 발행**하는 코드 케이브로 감싼다. 레코드 형식·크기·네트워크/큐 구조는 원본 그대로 유지 → 멀티 호환 영향 최소. 순서: ① hardware watchpoint로 스택 빌더 특정(lap678 다음 한 가지 ①) → ② 분할 발행 케이브 구현 → ③ 원본20/후보50 paired(이동·공격 둘 다 `+0x384` 수신 50/50) 재실행. 구현 우선, 실패 시 같은 lap에서 원인 찾아 재시도.

## 운영자 판정 (2026-09-26 16:08, lap682 → middle 검수 요청)
**2026-09-26 16:08 운영자 판정(lap682 승격 해소):** 이동 paired PASS(원본20/20·후보50/50, 2/2 재현)와 lap680/681 후보 공격 브로드캐스트 증거(공격툴바+지면 클릭 → `+0x384` 공격 pending 50/50, 1초 내 `command==4` 41/50)로 G5 명령 브로드캐스트 50을 판정 근거로 삼는다. UI 공격 수렴 0은 원본도 0이라 하네스 한계(제품 결함 아님)로 기록. op8 반복호출 방식은 브로드캐스트 경로를 거치지 않아 채택하지 않는다. **다음: G5 전체(v3 후보: 드래그50·그룹/호출/저장로드50·이동 paired·공격 브로드캐스트·v3 크래시 수정)를 middle 독립 검수로 올린다.** middle은 필요하면 공격 원본 paired 1회(같은 공격툴바+지면 클릭, pending 기준)를 요구할 수 있다.

# lap 683 middle 검수 — G5 v3 2단 HOLD, 16:08 판정 근거와 raw 충돌

## 현재 판정

- 후보 `e5004764e945350a0391d69035f8c8f0d305fcca7d6aaa54066836bac3de6977`(lap680~682 artifact 4개 exe SHA 일치), 보호 원본 `b56986e0…c9c08a8ac` 불변.
- **승인:** v3 크래시 수정(청크 3회 각 1 hit, packed 50, fatal 없음, SHA 핀 테스트 PASS). 이동 paired(lap682 후보 `command==3` 50/50 @0.15s, 원본 20/20).
- **불인정:** 공격 브로드캐스트50. lap680의 "`+0x384` 공격 pending 50/50" 판정식은 `pending_command != 1`이다. raw는 `0x1000001`×49(xy `0x2e002b`)+`0x10001`×1이고, 같은 phase `after_units`는 `command==3` 35/`command==1` 15/**`command==4` 0**이다. 공격 계열 >20 신호는 lap681 후보 1회 `command==4` 41/50뿐이며, 원본 paired가 없고 lap682에서는 후보 0/50·원본 0/20으로 재현되지 않았다.
- **미실행:** v3 기준 부대지정/호출/save-load/51번째 미선택 roundtrip. `tools/g5_candidate_drag_probe.py`의 TARGET_SHA는 여전히 v2 `ae495fa5…`다. v3 wrapper는 선택 entries를 백업·복원하며, lap680 크래시가 바로 그 entries 오염이었으므로 회귀를 다시 확인해야 한다.
- 전체 G5 2단 `HOLD/INCONCLUSIVE`, 제품 G5 PASS·사용자 milestone 승인 없음, 멀티 동기화 `UNKNOWN`. 상세 `docs/history/laps/20260926_lap683_middle_g5_v3_independent_review_hold.md`.

## 승격 작업자가 이어서 검증할 한 가지

work tier가 v3 `e5004764…` 하나로 원본 paired를 실행한다. ① roundtrip 도구를 v3 SHA로 갱신하고 원본·후보를 fresh로 돌린다. PASS = 후보 `50/50/50`·51번째 미선택·group20+field49·fault 0, 원본 `20/20/20`. ② 공격 판정을 `command(+0x290)==4` ever-matched로 바꾸고(`pending!=1` 금지) raw 분포를 저장한다. 공격툴바+지면클릭을 이동 목적지와 다른 새 목적지에 보내 원본·후보 각 2회 실행한다. PASS = 공격 가능 유닛 전원. 둘 다 끝나면 새 middle이 G5 2단을 재검수한다. 운영자 16:08 판정이 "pending 50/50"을 근거로 삼은 부분은 이 raw와 충돌하므로 운영자/strategy가 확인한다.

## 운영자 확인 (2026-09-26 16:15, lap683 충돌 해소)
**2026-09-26 16:15 운영자 확인(lap683 충돌 해소):** lap683 middle 판정을 수용하고 16:08 운영자 판정의 '공격 50' 근거(`pending!=1` 계수)는 **철회**한다. 다음 work는 lap683 지시 그대로: v3 하나로 ① 부대지정/호출/저장·로드 roundtrip(후보 50/50/50·51번째 미선택, 원본 20/20/20) ② 공격 paired(`command==4` 누적 기준, 이동과 다른 새 목적지, 원본·후보 각 2회). 공격 UI가 원본에서도 0이면 같은 lap에서 원인을 좁혀 재시도(구현 우선). 끝나면 새 middle 재검수.

# lap 684 승격 — v3 roundtrip PASS, 공격 판정 필드 정정 후 재현 가능한 FAIL로 좁혀짐

## 현재 판정

- 후보 `e5004764e945350a0391d69035f8c8f0d305fcca7d6aaa54066836bac3de6977`(재빌드 SHA 확인), 보호 원본 `b56986e0…c9c08a8ac` 불변(10회 실행 모두 재해시 일치).
- **① v3 roundtrip: PASS.** `tools/g5_candidate_drag_probe.py`를 v2→v3로 갱신해 원본·후보 fresh 실행. 후보 `selected/recalled/loaded-recalled` 50/50/50(unique), `group_stored_stock20_plus_overflow49`(`{-1:6,1:49}`) 포함 ui_roundtrip.checks 7/7 True, crash 없음. 원본 20/20/20. `status=PASS_UI_ROUNDTRIP`/`PASS_ORIGINAL_CAP20`.
- **② 공격 브로드캐스트: 판정 필드 자체가 틀려 있었다.** `command(+0x290)==4` 살아있는 상태로 이동과 다른 새 목적지(±3,6)에 지면클릭 2회+실제 표적 배치 재시도 2회(총 원본2·후보2) → **전부 0**(원본 0/19, 후보 0/49). 원본까지 0인 것은 lap683가 요구한 "재시도 후 BLOCKED" 계약대로였지만, 그 사실 자체가 판정 지표(`command==4`)가 이 입력에 맞지 않음을 보여준다.
- 같은 lap 안에서 STATUS.md에 도착한 16:35 운영자 방향(판정 지표를 `+0x384==0x1000004`+3초 누적 `ever_command4_count`로 교체)을 즉시 구현·재실행: **원본 2/2 100%(19/19, 19/19)**로 완전히 재현. **후보 2/2는 1/49, 0/49**로 재현 가능한 실패. 이동(`command==3`, 같은 청크분할 경로)은 이미 lap682에서 50/50 PASS다.
- `pending_xy`(좌표)는 후보 run2에서 49/49까지 전파돼(이동 성분은 살아있음) 공격 전용 필드/플래그만 청크 경계에서 실패하는 것으로 원인이 좁혀졌으나 gdb 확인은 아직 없다.
- 회귀 22 passed, `make check` 973 passed(648s), ruff/compileall/mypy/`CONTEXT_PASS`/`SAFETY_PASS` 모두 PASS. 신규 테스트 1개(이동/공격 목적지 불일치 회귀), 제품 EXE/원본 0 변경. 상세 `docs/history/laps/20260926_lap684_work_g5_v3_roundtrip_pass_attack_command4_blocked.md`.

## 승격 작업자가 이어서 검증할 한 가지

middle이 roundtrip PASS와 이동 paired(lap682)를 승인할지 확인하고, 공격은 이번 lap이 처음으로 얻은 "원본100% vs 후보≤1/49" 재현 가능한 결함을 근거로 `HOLD`가 아니라 명시적 **FAIL**로 기록할지 판정한다. 그 뒤 다음 work가 middle 없이: gdb로 `patches/selection/g5_selection_cap50_v3.py`의 청크 재호출 3회 사이에서 order-type4(공격) 전용 필드(공격 플래그/타겟, xy 스테이징과 달리 취급되는지)가 각 청크 호출 뒤 보존/복원되는지 직접 추적해 원인을 특정하고 최소 수정 후 원본·후보 각 2회(`ever_command4_count` 기준)로 lap684의 4-run 표를 재현·개선한다.

## 운영자 판정 (2026-09-26 18:19, lap685)
**2026-09-26 18:19 운영자 판정(lap685 승격 해소, middle 생략 — 반증 2건은 raw로 명확):** 재배치 이후 공통 회귀 확정 + 옛 배열 리터럴 잔여 0 ⇒ 원인은 v1 편집 묶음 중 하나. **추적 대신 이분 탐색(bisection)으로 간다.** v1/v2 편집을 묶음별로 나눈 후보들을 빌드한다: (G1) hit-test cap `0x43877A`만, (G2) 선택 저장 재배치(DIRECT/END_SITES)만, (G3) 소비자 `FUN_0041DC40` 프레임 0x98→0x270 + 클리어 카운트, (G4) H3 그룹 호출 케이브, (G5') 기타. 각 후보를 원본 대비 **20기 이하 선택**(드래그 20)으로 lap684 probe(`ever_command4_count`) 1회씩 돌려 공격이 깨지는 묶음을 찾는다(원본 19/19 기준). 깨지는 묶음 안에서 다시 반으로 나눠 1개 편집까지 좁히고, 그 편집을 고친 뒤 v3 전체로 원본20/후보50 공격 paired 2회. 특히 G3(프레임 확장으로 `[esp+X]` 참조 하나가 안 따라갔을 가능성)을 먼저 의심.

## 운영자 판정 (2026-09-26 20:15, lap688 → middle 재검수)
**2026-09-26 20:15 운영자 판정(lap688 N=5 반영):** 공격 반복 측정 — 원본(선택20·가능19) `ever_command4` 19/19/5/11/4(중앙 11, 58%), v3 후보(선택50·가능49) 30/33/49/27/32(중앙 32, 65%), **후보 5/5회 모두 20 초과**. 원본 자체 변동이 크므로 비율 동등 이상 + 매회 20 초과를 공격 브로드캐스트 50의 근거로 삼는다. **다음: G5 전체 middle 독립 재검수**(드래그50·51번째 거부, 그룹/호출/저장로드 50/50/50(lap684), 이동 paired 20/50(lap682), 공격 N=5(lap688), v3 크래시 수정(lap680), make check). 멀티 영향 메모(명령 레코드 형식 불변, 20기 단위 최대 3회 발행 → 패킷 수 최대 3배) 포함 요청.

# lap 689 middle 검수 — G5 2단 단일플레이 조건부 PASS, 사용자 milestone 경계

## 현재 판정

- 후보 v3 `e5004764e945350a0391d69035f8c8f0d305fcca7d6aaa54066836bac3de6977`(lap688 artifact exe 5개 재해시 일치), 보호 원본 `b56986e0…c9c08a8ac` 불변.
- raw 직접 파싱으로 원본20 대비 재확인: 드래그 50(55기 중 5기 미선택), 부대 저장/호출/저장로드 50/50/50(lap684), 이동 ever 50/50(lap682), 크래시0, UI 스크린샷 나란히 대조 깨짐 없음, make check 1003 passed(lap688 로그), targeted 7 passed, `SAFETY_PASS`.
- **공격 근거 정정:** 20:15 판정의 `ever_command4` "매회 20 초과"는 표적 무관 command4를 세며 비표적 uid가 관측돼 자동교전 오염 가능 → 근거로 불인정. 대신 같은 artifact의 후보-1/2 t=0.0 스냅샷 49기 동시 `pending==0x1000004`+클릭 xy 49/49(3청크 전부), 후보-3 49/49 `pending_target_uid`=스폰 표적 handle로 공격 50 전달 승인. 원본은 같은 조건 19/19.
- G5 2단 **조건부 PASS(단일플레이)**. 멀티 동기화 `UNKNOWN`(명령당 동일 60B 레코드 최대 3회 발행, lockstep 묶음·50슬롯 dispatch 큐 소모·혼합 피어 미확인). 제품 G5 PASS·사용자 milestone 승인은 선언하지 않는다. 상세 `docs/history/laps/20260926_lap689_middle_g5_full_independent_review_conditional_pass.md`.

## 승격 작업자/운영자가 이어서 할 한 가지

이 lap은 마일스톤 경계(2단 → 사용자 3단)다. 운영자/strategy가 ① 공격 근거를 `ever_command4`에서 pending-word로 교체한 이 판정을 수용할지 확인하고, ② 사용자에게 G5 단일플레이 milestone 판단(멀티 `UNKNOWN` 별도)을 올린다. 판단 대기 중 독립 작업은 work 1건(비차단): `tools/g5_worker_relative_move_attack_probe.py` 82~97·127~128행의 반증된 "스폰 위치 혼잡" 주석 정정(선택: 슬롯별 누적 `ever_pending_exact` 기록). G5 제품 EXE는 변경하지 않는다. 사용자 승인 후 다음 목표(G2 전비10000/G1/G4) 우선순위는 strategy가 정한다.

## 운영자 판정 (2026-09-27 00:05, lap694)
**2026-09-27 00:05 운영자 판정(lap694 승격 해소, strategy 대행):** (b) **전역 풀 확장**을 채택. (a) 고비용 타입으로 우회해 10000을 채우는 것은 실제 플레이(전비10000이면 유닛 수가 많아짐)를 대표하지 않아 기각. 다음 work: 이미 실전 검증된 G2 ESL 계열 풀 재배치(`patches/population/g2_esl2608_pool4092_owner500.py`/`g2_esl2606_pool4092_owner500.py`, 개인500·공용4092, 초상화 슬롯 수정 포함)를 **보호 원본(b56986e0) 기준 전비10000 후보에 이식**(구현 우선) → lap694 8인 probe 재실행으로 owner0~7 전원 `used=10000` 확인 → 저장/로드 1회. 개인 상한이 1인 10000 도달에 부족하면 500→1250 등 필요한 값으로 올리되 8×개인 ≤ 풀 조건 유지.

# lap 698 middle 검수 — G2 8인×10000 조건부 부분 PASS, 방향 판정 필요(근거 충돌)

## 현재 판정

- 보호 원본 `b56986e0…c9c08a8ac` 재해시 일치. 후보를 원본에서 독립 재빌드 → `11aa9e796805d3e0c29b55de957d003c521e74f9aeddf4e3478bd743842e5b53`, lap695/696/697 JSON과 byte-identical.
- lap697 `probe-result.json`(SHA `95cb79cb…54ff27`) 직접 파싱: owner0~7 `used=10000,count=156,count_cap=500`, 전역 live=active_slot_list=bitmap=owner합=1248, 중복0, 저장/로드 후 동일. targeted pytest 22 passed, `SAFETY_PASS`.
- **근거 충돌:** fixture type103(cost65)은 type_costs 83종 중 최고가(중앙값15, <20이 59종). 명령 wire가 슬롯을 하위 12비트로 압축(`0x004AE613 shl edx,12`, `and 0x0FFF`; `analysis/memory_maps/g2_esl2606_command_slot12_boundary_20260925.md`)해 풀 상한 4095 → 개인 cap을 1250으로 올려도 1인 평균 ~511기 천장, 평균 비용≥~20 군대만 8×10000 도달. 00:05 운영자 판정이 기각한 "고비용 우회"와 같은 범주.
- 부가: 전 구간 tick 3→21(안정성·전투·생산 미측정), 저장 직후 무변경 로드(비판별, tick 21→20만 약한 신호), bridge SHA 문서값 `28980e42…`와 JSON 불일치(진단용).
- 판정: 2단 `CONDITIONAL PARTIAL PASS`(용량·회계·풀 무결성, 고비용 fixture 한정) / G2 제품 `HOLD`. 사용자 milestone 요청 없음. 상세 `docs/history/laps/20260927_lap698_middle_g2_supply10000_independent_review_hold.md`.

## 승격 작업자/운영자가 이어서 할 한 가지

strategy(Astra/Fable)/운영자가 G2 방향을 정한다: (A) "8×10000 = 평균 비용≥20 군대" 해석을 사용자에게 올리고 현 후보(4092/500)로 안정성 단계 진행, 또는 (B) 명령 wire 슬롯 12비트 확장(13비트 이상; 모든 생산자·소비자·저장·멀티 호환 검증)으로 풀 ≥8000~10000 + 개인 cap ~1250. 판정 대기 중 비차단 work 1건(A/B 공통, EXE 무변경, probe 확장만): ① 대표 혼합(비용10/15/20/35/65) 1인 주입으로 cap500 도달 시 used 실측, ② 저장→유닛 1기 제거/추가→로드로 판별형 복원, ③ 수천 tick 진행 후 1248 무결성 재확인.

## 사용자 판단 (2026-09-27 03:21, lap698/699 해소)
**2026-09-27 03:21 사용자 판단(AskUserQuestion 응답):** "현 한계 인정. 전비 상한 10000은 포기하고 기존 전비 상한 5000으로 만족". **G2 목표를 전비5000(달성 판단 유지)으로 되돌리고 10000 트랙 종료.** 10000 후보(lap691~699, `g2_supply10000_*`)와 증거는 보존만 하고 더 진행하지 않는다. A/B 판정 대기 해소. **다음 우선순위(운영자 결정): G4 — 길찾기/자유대전 AI**(STATUS 표: AI 개선 제품 비교·post-load·사용자 승인 미충족). 다음 work는 G4의 마지막 미충족 항목 중 post-load(저장/로드 후 AI 개선 유지) 확인부터 구현 우선으로 진행. G1은 그 다음.

# lap 719 middle 검수 — G5 v4 2단 CONDITIONAL PASS, 승인 후보 교체 경계

## 현재 판정

- 보호 원본 `b56986e0…c9c08a8ac` 재해시 일치. v4 후보를 원본에서 독립 재빌드 → `0e472792410ddc87eb5eee9809c99761da61d8afa23e73638db0fae5e10f9cbb`(lap717/718 일치), 대상 pytest 9 passed, 후보 raw 전부 `private_exe_sha256`=v4.
- raw 재파싱: 정지·홀드·순찰(버튼·단축키) 후보 50/50 vs 원본 20/20, 지면 이동 50/50, ALT/Ctrl/Shift 전체 드래그 50, 부대지정/저장로드 PASS. 공격은 lap689 인정 지표(t=0 `pending==0x1000004`)로 v4 2/5회 49/49 = v3·원본과 같은 패턴.
- 정정: lap676 opcode 집합 중 `0x19b/0x19d~0x19f`는 어느 호출부에도 없고, `0x41F0A4`는 비명령이 아니라 런타임 `word [0x892ffe]`(명령 버튼 인덱스) 실제 명령 발행 호출부다. 즉치 21곳은 v4에서도 원본 동작 → 반전 게이트 안전. v4 docstring 42~55행 위험 서술은 사실과 반대.
- 판정: v4 2단 `CONDITIONAL PASS`(단일플레이, 측정 명령 한정). 멀티 `UNKNOWN`. 사용자 milestone 승인은 v3 `e5004764…` 대상이었으므로 v4 교체는 선언하지 않는다. 상세 `docs/history/laps/20260927_lap719_middle_g5_v4_independent_review_conditional_pass.md`.

## 승격 작업자/운영자가 이어서 할 한 가지

운영자/사용자가 ① v4를 승인된 G5 후보로 교체할지, ② G5 종료 후 G1(1600×1200 원본 구성) 재개를 판단한다. 판단 대기 중 비차단 work 1건(EXE 무변경): 잔여 R1 — v4에서 50 선택 → 부분 드래그로 약 25기 재선택 → 정지 → `0x1000002`가 선택 유닛에만 가고 미선택 유닛은 불변인지, 원본(20→약10 재선택) paired 1회씩 raw로 확인. 같은 work가 v4 docstring 위험 서술과 `analysis/memory_maps/g5_command_packer_xref_falsification_lap676.md`의 opcode 집합·`0x41F0A4` 분류를 정정한다. R1 FAIL이면 청크 호출 수를 선택 수(`[0x108c000]`) 기준으로 제한하는 v5를 만들고 정지·이동·공격·R1을 재측정한다.

# lap 721 middle 검수 — G5 v4 R1 확정 FALSIFIED, 새 R3(희소 선택)로 조건부 유지

## 현재 판정

- lap720 raw 3개(`8c387f64…`/`b56aef77…`/`cee5fbef…`) SHA·독립 재계산 일치: 누출0·누락0, 축소 후 버퍼 꼬리 전부 0. v4 재빌드 `0e472792…` 일치, pytest 4 passed, `SAFETY_PASS`.
- 원본 disasm: 선택 제거 `0x412E9F..0x412EFC`는 일치 칸을 제자리 0화(압축 없음)+count−1, 명령 본문 `0x4AE587..0x4AE623`은 고정20칸 복사+`0x416F70` 유효성 검사 → **R1 확정 FALSIFIED**.
- **새 R3(PLAUSIBLE, v3·v4 공통, 원본 대비 회귀 가능):** 선택 배열이 구멍 있는 집합인데 래퍼 게이트는 `count>20`일 때만 청크. 50선택 후 사망/해제로 count≤20이 되고 생존 칸이 인덱스≥20에 남으면 원본 본문(`entries[0:20]`만)으로 가 그 유닛은 명령을 못 받는다. 제거 호출부 후보 7곳(`0x409C8E` 등).
- v4 2단은 CONDITIONAL PASS 유지(확정 승격 불가). 승인된 v3에도 걸리므로 사용자 교체/G1 재개 확인은 R3 결과 뒤 권고. 상세 `docs/history/laps/20260927_lap721_middle_g5_v4_r1_confirmed_falsified_r3_sparse_gap.md`.

## 승격 작업자/운영자가 이어서 할 한 가지

work tier R3 probe: v4 드래그50 → 실제 입력/이벤트(Shift+클릭·초상화 해제 우선, 불가 시 fixture 사망, 방식 명시)로 인덱스 0..29 쪽 30기 제거 → 전체 버퍼로 count≤20·생존 칸 인덱스≥20 확인 → STOP → `unit+0x384`=`0x1000002` 수신 수. 인덱스≥20 미수신이면 같은 lap에서 v5(`check_count`를 "`entries[20:50]`에 비0 칸 존재 시 청크"로, 나머지 v4 동일) → R3·명령범위·축소 probe·부대지정/저장로드·`make check` 재측정 → 새 middle 검수.

## 사용자 판단 (2026-09-28 01:27, lap719/720 해소)
**2026-09-28 01:27 사용자 판단(AskUserQuestion 응답):** "v4 승인, 바로 G1". **G5 확정 후보를 v4(`patches/selection/g5_selection_cap50_v4.py`)로 교체·승인**(단일플레이; 정지·홀드·순찰 50/50, 이동·공격·그룹·저장로드·ALT/Ctrl/Shift 드래그 유지, 선택 축소 누출 0, 크래시 0). 미확인 메모: 멀티 동기화, 미니맵 우클릭(격리 환경 무반응), R2. 실사용 EXE는 나중에. **다음 최우선: G1 — 원본과 같은 화면 구성을 유지한 1600×1200 고해상도.** 다음 work는 기존 G1 기록(`docs/history/laps/*g1*`, `analysis/memory_maps/*g1*|*resolution*`)으로 현재 상태·막힌 지점을 요약하고, 구현 우선으로 가장 작은 다음 후보를 만들어 격리 실행 캡처로 원본(800×600) 대비 구도 동일성·HUD 배치·깨짐을 확인.

# lap 732 work 보고 — G5 체크리스트 (D) 신규 R3-유사 결함(후보 v5, 사망 후 그룹 호출)

## 현재 판정 (work tier, 정보 제공용 — middle 독립 검수 아님)

- 신규 `tools/g5_group_shift_add_death_recall_probe.py`(원본 1회·후보 v5 1회)로 (D) 잔여 두 항목을
  한 fixture·한 실행으로 측정. 보호 원본 `b56986e0…c9c08a8ac`, 후보 v5
  `29e61074c622c77debb5053a412e3337fc8100f1eda29bd68efb163b1a9ee146` 둘 다 `source_unchanged=true`.
- **Shift+숫자 자체("Shift+1")는 원본·v5 둘 다 그룹 인원을 전혀 늘리지 않는다**(원본 6/6, v5는
  add_steps만큼 반복 무반응). xdotool 별도 keydown/keyup 방식과 단일 chord(`key shift+1`) 방식
  둘 다 동일하게 무반응이었고(실패 가설 2회, PROMPT.md ③ 기준 결론), Ctrl+1(지정)·"1"(호출)은 같은
  세션에서 정상 동작해 입력 전달 경로 자체는 검증됨 — **이 실행 파일의 번호-키 핸들러에 Shift 분기가
  아예 없는 것으로 판단**(lap727의 ALT/Ctrl 같은종류선택·포트레이트 해제와 같은 종류의 "미지원,
  회귀 아님" 판정, 원본·v5 동일).
- **대안 메커니즘("1" 호출 → Shift+클릭으로 현재 선택에 추가 → Ctrl+1 재지정")은 원본·v5 둘 다
  정확히 +1 확인**(원본 14→15, v5 40→41, 새 유닛만 추가되고 기존 멤버 유지) — 그룹 인원을
  늘리는 것 자체는 가능함을 확인.
- **신규 발견(FAIL, 후보 v5 한정): 사망 후 그룹 호출에서 죽은 유닛 일부가 생존자처럼 재선택된다.**
  원본: 15명 그룹에서 앞/중간/뒤 섞어 3명 사망(op10, 사망 직전 미선택 상태) 후 그룹 호출 →
  survivor 12명 정확히 일치, 유령 없음, 이동 브로드캐스트 12/12 PASS. **후보 v5: 41명 그룹에서
  10명 사망**(front 3 + middle 4 + rear 3, 사망 직전 전원 미선택) **후 그룹 호출 → 37명이
  선택됨(기대 31명), 죽은 10명 중 6명(front 3 전원 + middle 3/4)이 유령처럼 재선택에 포함되고
  나머지 4명(middle 1 + rear 3 전원)만 정상 제외됨.** 사망 자체는 원본·v5 둘 다 동일하게 성공
  확인됨(`op10.dead_flag_after=1` 10/10, `selected_before=0` 10/10) — 사망 처리 자체가 아니라
  **그룹 호출이 죽은 유닛을 걸러내는 경로**의 결함으로 보인다. 같은 실행에서 사망 없이 41명 전원을
  호출했을 때는 정확히 40명(그 시점 그룹 크기) 재현돼 **호출 메커니즘 자체는 살아있는 그룹에서는
  정상**임이 함께 확인됨 — 결함은 "사망 후"에만 나타난다.
- **추정(정적 미확인, 추측으로 표시):** 관찰 패턴(일부만 유령, 나머지는 정상 제외)이 R3와 형태가
  유사하다 — lap724가 정적으로 확인한 "그룹은 레거시 20슬롯 struct(`GROUP1_BASE_ADDRESS`) +
  유닛 자체 필드(`unit+0x344`) 이중 저장" 구조를 볼 때, 호출 시 레거시 20슬롯 struct 쪽 경로는
  사망 여부를 재확인하지 않고 스냅샷 그대로 재선택하고, `unit+0x344` 오버플로 스캔 경로만 생존
  여부를 걸러내는 것이 아닐까 추정된다 — 그러나 이번 lap은 이 가설을 disasm으로 확인하지
  않았다(추측).
- R3(선택 배열, `SELECTION_BASE`)와 이번 그룹 결함(`GROUP1_BASE_ADDRESS`/`unit+0x344`)은
  **서로 다른 메모리 구조**임은 이미 lap724가 정적으로 확인한 사실이다(추측 아님) — 다만 두
  구조가 "20개 한정 경로 vs 확장 경로" 라는 같은 종류의 버그 패턴을 공유하는 것으로 보인다는
  점은 이번 lap의 추정이다.
- 원본은 이 결함이 없다(15명 중 3명 사망 시나리오에서 정상). **(D)는 이 결함 때문에 미완료다.**
  make check(아래) PASS는 이 신규 발견과 무관 — probe/제품 코드 자체는 lint/type/test 기준
  깨끗하다는 뜻일 뿐, 그룹 호출 결함을 고친다는 뜻이 아니다.
- 상세 `docs/history/laps/20260928_lap732_work_g5_checklist_d_shift_add_death_recall.md`.

## 승격 작업자/운영자가 이어서 할 한 가지

이 발견은 마일스톤 경계(G5 (D) 완료 및 G5 종료 여부)에 직접 닿으므로 work tier가 임의로 다음
후보를 만들지 않는다. middle/strategy가 판단할 것: ① 이 R3-유사 그룹 호출 결함의 우선순위(다른
(E)~(H) 항목보다 먼저 고칠지, 최소 근거 disasm으로 정확한 코드 경로부터 특정할지), ② 사용 규모
(원본에서 재현되지 않는, v5 50-cap 확장에서만 나타나는 결함이므로 R3와 같은 "확장 자체가 만든
신규 버그" 계열로 분류할지). 다음 work가 착수한다면(승인 후): disasm으로 그룹 호출 루틴(추정
`FUN_0040F7D0` 계열, 호출 시 20슬롯 struct/오버플로 스캔 두 경로의 실제 분기 조건)을 특정하고,
front/middle/rear 각 위치별로 어떤 인덱스가 유령으로 남는지 재현성 있게 좁힌 뒤 v6 후보로 수정,
이번 probe(`tools/g5_group_shift_add_death_recall_probe.py`)로 원본·v5 동일 시나리오 재측정.

## 이 섹션은 lap733(v6 H4 훅)의 수정으로 해소됐다 — (D) 참고, 아래는 새 lap739 승격.

# lap 739 승격 — (F) raw 드래그 선택 자체는 저장/로드에서 살아남지 못함(후보 v6 한정), 세이브 형식 호환은 확인됨

## 현재 판정 (work tier, 정보 제공용 — middle 독립 검수 아님, 03:36 판정에 따라 middle은 A~H 전체 완료 후 한 번에)

- 보호 원본 `b56986e0…c9c08a8ac`(3회 실행 전후 불변), 후보 v6 `fdc913b5f42dc7cc2dcb258d3ecac43e2a2a79a24e4ce10ee362e8ded173805f`.
- **부대(Ctrl+숫자 그룹) 저장/로드는 재확인 PASS**(checks 7/7, lap724/734와 동일 패턴) — (D)/(F)의 그룹 경로는 이상 없음.
- **신규 FAIL(후보 v6 한정): 부대 지정 없이 그냥 드래그로 고른 raw 선택 자체는 저장→로드에서 사라진다.** 원본은 저장 시점 raw 선택(20)이 로드 후 그대로 복원됨(로드 직전 라이브 값은 명시적으로 0으로 디셀렉트해 뒀는데도 저장 당시 값 20으로 되돌아감 — 세이브 파일 자체가 raw 선택을 인코딩하는 원본의 실제 기능임을 확증). 후보 v6는 저장 시점 50이었어도 로드 직후 raw 선택이 항상 0이다. 그룹1 재호출("1")로는 정상 복원되므로(원본 20, 후보 50) 완전한 기능 손실은 아니고 우회로가 있다.
- **근본 원인 확정(정적):** `patches/selection/g5_selection_cap50_v1.py`가 레거시 선택 주소 `0x00899024`의 알려진 읽기/쓰기 참조 전부(10곳)를 새 `SELECTION_BASE`로 재배치해 레거시 주소를 완전히 방치한다. 원본의 세이브 직렬화가 그 주소(또는 인접 블록)를 그대로 디스크에 옮기는 방식이라면, v1~v6 전부에서 그 주소는 항상 0이므로 세이브에도 항상 0이 기록된다 — 관측과 정확히 일치.
- **원본 세이브 호환(별개 질문): PASS.** 완전 무패치 원본 실행 파일이 후보 v6가 만든 세이브 파일을 자신의 저장 디렉터리에 주입받아 크래시/행 없이 정상 로드(`PASS_CROSSLOAD_NO_CRASH`, `ps==3`·`tick>0`). 로드 후 그룹1 스냅샷(`group1_count=20, group1_first_id=132270`)이 후보 자신의 로드 결과와 완전히 일치 — 레거시 20슬롯 그룹 데이터의 바이트 호환성이 교차 확인됨. 세이브 "형식"은 깨지지 않았다.
- 크래시 0(3/3), `source_unchanged` 3/3, `make check` 1111 passed(858.42s), ruff/mypy/`CONTEXT_PASS`/`SAFETY_PASS` 전부 PASS. 제품 EXE/원본 0 변경. 상세 `docs/history/laps/20260928_lap739_work_g5_checklist_f_saveload_selection_regression.md`.

## 승격 작업자/운영자가 이어서 할 한 가지

마일스톤 경계(G5 (F) 완료 여부)라 work tier가 임의로 v7을 만들지 않는다. middle/strategy가 판단할 것: ① (F-2)를 지금 고칠지(레거시 주소 `0x00899024`에 min(count,20) 그림자 값을 계속 유지하는 최소 훅 — 정확한 세이브 직렬화 함수/범위는 아직 정적으로 특정 안 됨, 다음 조사 대상) 또는 그룹-재호출 우회로 충분하다고 보아 (F)를 "부분 PASS(그룹 경로만, raw 드래그 선택 자체는 NOT SUPPORTED로 문서화)"로 마감할지, ② 이 결함이 R3/(D) 사망-후-호출보다 범위가 넓다는(원본은 0~20 전체가 세이브에서 살아남는데 후보는 0~50 전체가 죽는다) 점을 우선순위 판단에 반영할지. 다음 work가 착수한다면(승인 후): 원본 disasm으로 실제 세이브 직렬화 루틴이 `0x00899024` 블록을 읽는 정확한 주소 범위·타이밍을 특정하고, 그 지점에 레거시 뷰를 유지하는 최소 훅을 설계해 원본·후보 paired 재측정.

## 운영자 해소 (2026-09-28 14:05, lap739 → 다음 work v7)
**2026-09-28 14:05 운영자 판정(lap739 F-2 FAIL, 최우선 수정):** ①을 채택 — 지금 고친다(그룹-재호출 우회로 마감하지 않음). 다음 work(v7, 구현 우선): 저장 직전 새 선택의 앞 20개를 레거시 영역에 미러링(원본 세이브 호환 유지) + 21~50번째는 원본 포맷을 깨지 않는 방법(세이브 파일 뒤 추가 블록 또는 여유 영역)으로 보존, 로드 직후 역복원. 불가하면 최소한 앞 20기 복원(원본 동작과 동일 이상)으로 가고 50기 복원 불가 사유를 기록. 원본/v7 paired로 F-2 재측정 + 원본 세이브를 v7에서 로드(역방향 호환) + 핵심 회귀. lap739이 이번 lap 안에서 `tools/g5_stock_selection_array_xrefs.py`를 재실행해 **레거시 주소의 정적 잔여 xref가 0**(44 hits 전부 v1 site 테이블로 이미 처리됨)임을 미리 확인해 뒀다 — 세이브 직렬화가 이 주소를 건드린다면 리터럴 즉치가 아니라 레지스터/오프셋 간접 주소이므로, 다음 work는 정적 재스캔이 아니라 gdb 하드웨어 watchpoint로 저장·로드 각각의 순간 그 주소를 실제로 건드리는 PC부터 잡는다(lap640대 watchpoint 선례와 동일 기법). 이 섹션(lap739 승격)은 이 판정으로 해소.

# lap 744 승격 — G5 체크리스트 A~H 전부 채움, work tier가 더할 실 증거 없음(마일스톤 경계)

## 현재 판정 (work tier, 이번 세션은 신규 실행/변경 0건 — 검토만)

- STATUS.md/INBOX.md/APPROVALS.md를 읽은 결과: lap743까지 G5 체크리스트 (A)~(H) 전부가
  PASS 또는 BLOCKED(사유 기재)로 채워졌다 — A~F PASS(기준 후보 v7), G는
  `BLOCKED(env: native ipxwrapper crashes on room creation, wine9.0)`로 누적 4개 override 조합
  실패 후 최종 확정, H는 8019 tick 장시간 반복 명령 PASS(crash 0, 선택회귀 0).
- 2026-09-28 03:36 및 16:35 운영자 판정 원문 모두 동일하게 "체크리스트 전체가 채워진 뒤 middle이
  한 번에 독립 재검수"를 다음 단계로 명시했다. AGENTS.md/PROMPT.md의 1단(기계)→2단(다음 새 세션
  독립 검수)→3단(사용자 마일스톤 확인) 구조상 이 2단은 middle(Opus5/Sol) 전용이며 work tier
  역할 경계 밖이다(`docs/MODEL_ROUTING.md`: "실무는 큰 방향 결정이나 자기 작업의 최종 승인까지
  맡지 않는다").
- 현재 목표 우선순위(INBOX 상시 지시, 2026-09-27 15:20)상 G5가 최우선이고 G5가 이 middle 재검수를
  통과하기 전엔 G1 재개가 명시적으로 금지돼 있다(2026-09-28 01:31 지시). G2/G4는 이미 종료/보류,
  G3는 중단 — 즉 이 재검수를 건너뛰고 착수할 수 있는 **다른 목표가 현재 하나도 없다.**
  `docs/feedback/INBOX.md`의 상시 지시("재요약만 하는 회차 금지")에 따라 이미 존재하는 lap
  기록을 다시 요약/정리하는 것도 유효한 work tier 산출물이 아니라고 판단해 착수하지 않았다.
- `checks/context_limits.py check` = `CONTEXT_PASS`(STATUS 87줄/180, INBOX 78줄/400,
  APPROVALS 293줄/300 — 압축 불필요), 디스크 여유 124G(20G 기준 위생 조치 불필요), 제품 코드/EXE
  변경 없음, git 신규 파일은 전부 lap723~743이 이미 만든 미커밋 증거(이번 세션이 추가/삭제한 파일
  없음).

## 승격 작업자가 이어서 검증할 한 가지

middle(Opus5/Sol, high)이 STATUS.md 헤더 압축 포인터와 `docs/history/laps/20260928_lap7{17..43}_*.md`
전체(특히 lap742/743의 G BLOCKED 근거, lap740의 v7 저장/로드 미러링, lap738의 체력바 46/50 밀집
아티팩트 결론)를 근거로 G5 체크리스트 (A)~(H)를 한 번에 독립 재검수하고, PASS면 G5 milestone을
사용자에게 재상정(멀티는 BLOCKED로 명시, 21~50번째 세이브 미보존은 알려진 제한으로 명시)한 뒤
G1(1600×1200 원본 구성)을 다음 work로 지정한다. FAIL/조건부면 남은 결함과 담당 후보(v7 기준)를
work tier에 구체적으로 되돌린다. 이 세션(lap744)은 재현/변경 없이 종료한다.

# lap 745 middle 검수 — G5 A~H 전체 재검수 HOLD, F에 새 결함 경로 H-STALE-TAIL(work handoff)

## 현재 판정 (middle, Claude Code `claude-opus-5-5`/high)

- 독립 확인: 보호 원본 `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe`(`b56986e0…`)에서 v7 재빌드 → `30efafa0…`
  일치. v6→v7 차이 17구간(`.rsrc` 헤더·콜사이트 `0x440f0c`/`0x4412dc`·캐이브 `0x108f100..1c9`), v5→v6
  10구간(`0x409cb8`·캐이브 `0x4e4f90..`). G5 pytest 53 passed, `SAFETY_PASS`, `CONTEXT_PASS`. lap740 F·
  lap743 H raw JSON 재계산 일치.
- 항목: A PASS(불변식 보완 필요), B/C/D/H PASS, E 조건부, G `BLOCKED(env)` 수용, **F HOLD**.
- **H-STALE-TAIL(정적 확인, 런타임 미검증):** `LOAD_WRAPPER`가 count(≤20)와 entries[0:20]만 쓰고
  `0x108f1bc: mov ecx,0x14`로 entries[20:50]을 로드 직전 값 그대로 둔다. v7에서 count 쓰기는 inc
  `0x412e6e`/dec `0x412ed2`+래퍼뿐 → 로드 시 21번째 이후 칸이 살아 있으면 count/칸 불일치, 비선택 유닛
  명령(v5 청크 게이트), 해제 시 count 음수, 음수 count 저장 시 `SAVE_WRAPPER` `rep movsd` 크래시 가능.
  기존 probe `selection_snapshot`은 `range(count)`만 읽어 한 번도 관측되지 않았다.
- H 정정: `moving_count`=`command!=0` 유닛 수(stop/hold 뒤에도 50) — 명령별 50 전달 증거 아님.
- 사용자 milestone 재상정·G1 착수 하지 않는다.

## 이어서 할 한 가지 (work tier, 구현 우선)

`tools/g5_candidate_drag_probe.py` roundtrip 재사용, 선택 50칸 전부 raw·유닛별 명령 opcode/목적지 변화로
수신 계수, 원본1·v7 1 paired: S1 50 선택 유지한 채 로드→이동→빈지면 해제→재드래그→저장(크래시), S2
저장 당시 21~50 유닛 byte`+0`·체력바·재선택 가능성, S3 50 선택→메인 메뉴→새 게임 이월. PASS=모든 시점
count==0 아닌 칸 수·로드된 선택 밖 명령 0·해제 후 0/전부 0·크래시 0. FAIL이면 최소 v8(`0x108f1bc`
`mov ecx,0x32`로 50칸 0 채움, S3는 초기화 지점 1곳 귀속) + 바이트범위 pytest + `make check` + F·핵심 회귀,
그 뒤 새 middle이 F만 재검수. 상세 `docs/history/laps/20260928_lap745_middle_g5_a_h_independent_review_hold_stale_tail.md`.

# lap 750 middle 검수 — G5 v8 최종 재검수 HOLD(좁음), lap748 S5 raw 공허·S3 새 게임 이월 미검증

## 현재 판정 (middle, Claude Code `claude-opus-5-5`/high)

- 독립 확인: 보호 원본 `b56986e0…`에서 v7 `30efafa0…`·v8 `ef46d1ac…` 재빌드 일치, `cmp` = 파일 `0xFB1BD`
  1바이트(`0x108f1bc mov ecx,0x14→0x32`). G5 pytest 9 passed, `make check` 1115 passed·5 skipped(868.05s),
  `SAFETY_PASS`/`CONTEXT_PASS`. 게임 실행 0회, 제품 코드 0 변경.
- A~E·H PASS(E 조건부), G `BLOCKED(env)` 수용, 홀드버튼 PASS — 단 lap749의 "청크 재발행 3초 초과" 설명은
  raw 불일치(lap749 3회 중 2회가 t≈0.05에 50/50), 실제 원인은 `observe()`가 클릭 반환 후 샘플을 시작해
  한-샘플 transient를 놓치는 race.
- **근거 충돌:** lap748/STATUS/INBOX는 S5("불러오기" 다른 판)가 "50 선택 이월 없음"을 보였다고 했으나
  raw `s5_load_different.selection_before`는 count=0·전칸0(S4 재시작 직후 실행, fixture도 소멸) — 시험 공허.
  저장 창 로드는 `0x4412dc`(v8 `LOAD_WRAPPER`) 한 곳뿐이라 S1 runtime + 정적 귀속으로만 수용.
- **남은 실제 위험 S3:** v8 새 선택 배열 count 쓰기는 inc `0x412e6e`·dec `0x412ed2`·`LOAD_WRAPPER`뿐,
  `.text`의 `0x899024/0x899028` 절대참조 0건. 새 게임 초기화가 레거시 영역만 비우면 50칸이 새 판에 이월될
  수 있고, S4 재시작 0/0의 초기화 주체가 귀속되지 않아 일반화 불가. 사용자 milestone 재상정·G1 착수 안 함.

## 승격 작업자가 이어서 검증할 한 가지

work tier 1 lap: (1) `tools/g5_stale_tail_probe.py`에 "50 드래그→다시하기→50칸 dump" 단독 모드를 추가해
v7로 1회 — 21~50칸이 남으면 재시작은 로드 경로 초기화(새 게임 보장 없음), 0이면 유닛 해체(dec) 경로.
(2) 원본/v8 paired로 순정 로비 직후 `초기메뉴`가 메인 메뉴로 가는지 확인, 가면 50 선택→초기메뉴→새 게임→
50칸 dump. (3) (1)이 로드 경로이고 (2)가 불가/FAIL이면 v9(새 게임 초기화 지점 1곳에 새 배열 0 채움) +
바이트범위 pytest·`make check`·S1/S4·핵심 회귀. S5는 50 재드래그 후 실행하도록 순서 수정. 이후 새 middle이
F만 재검수 → PASS면 사용자 milestone 재상정. 상세
`docs/history/laps/20260928_lap750_middle_g5_v8_final_review_hold_s3_s5_gap.md`.

# lap 751 승격 — G5 (F) S3 귀속·실측 처리 완료, middle 최종 재검수 요청

## 현재 판정 (work, Claude Code `claude-sonnet-5`/high)

- lap750 middle 핸드오프의 두 실험을 처리했다. `tools/g5_stale_tail_probe.py`에 `--restart-dump-only`·
  `--menu-exit-fresh` 게이트 2개만 추가(기존 S1~S5 분기 무변경, 새 플래그 미사용 시 이전 lap 동작과 동일).
- **① v7 restart-dump-only = `RESTART_DUMP_TAIL_CLEARED`**: 드래그 50 후 저장/로드 없이 곧장 재시작
  (다시하기), `full_dump` 전/후 비교 — 재시작 전 count=50·nonzero=50, 재시작 후 count=0·nonzero=0·50칸
  전부 0. v7의 `LOAD_WRAPPER`는 20칸만 0 채우므로 재시작이 그 경로였다면 21~50칸이 남아야 했다 — 남지
  않았으므로 재시작은 유닛 해체(dec, `0x412ed2`) 경로로 확정(핸드오프가 사전 등록한 두 해석 중 하나 확정).
- **② 원본·v8 menu-exit-fresh(fixture/선택 생성 전) = 둘 다 `MENU_EXIT_FRESH_BLOCKED_SAME_AS_FIXTURED`**:
  `ps` 23→3 즉시 복귀, 메인 메뉴(`ps==9`) 도달 없음 — lap747의 "원본도 동일 재현"이 fixture/선택 상태와
  무관한 환경/원본 고유 제약임을 fixture 없는 최소 조건에서도 재확인.
- 핸드오프 branching(③)의 v9 트리거 조건("①이 로드 경로이고 ②가 불가")이 성립하지 않는다(①이 정반대:
  좁은 경로가 아닌 더 넓은 해체 경로) → **v9 미착수, 제품 코드 0 변경**.
- `pytest`(v7/v8 selection) 9 passed, `make check` 1115 passed·5 skipped(783.17s),
  ruff/mypy/`CONTEXT_PASS`/`SAFETY_PASS` 전부 PASS. 3회 실행 전부 `source_unchanged=true`·
  `cleanup.ok=true`(고아 프로세스 0). 보호 원본 `b56986e0…`, v7 `30efafa0…`, v8 `ef46d1ac…` 전부 기존
  기록과 재빌드 일치.
- **주의: 이것은 S3가 재시작과 같은 초기화 함수를 탄다는 직접 증거가 아니라 유추(analogy)다.** S3
  (초기메뉴→새 게임)는 여전히 이 하네스에서 실측 불가(`BLOCKED(env)`)로 남는다. 사용자 milestone
  재상정·G1 착수는 이 lap이 선언하지 않는다.

## 승격 작업자가 이어서 판단할 한 가지

middle이 v8 기준 G5 (F)를 최종 재검수한다: ①②의 새 증거(재시작=해체 경로 확정, 메뉴 전환 제약=
fixture 무관 환경 제약 확정)로 S3를 "미확정 실제 위험"에서 "BLOCKED(env) + 낮은 유추 위험"으로
재분류해 F를 PASS 처리할지, 아니면 재시작 핸들러와 새 게임 초기화 루틴이 실제로 같은 함수를
호출하는지 정적 대조(gdb 워치포인트로 재시작 시 entries[20:50]을 누가 쓰는지 caller 특정, 또는 xref
비교)까지 요구할지 결정한다. PASS 처리 시 알려진 제한(G 멀티 BLOCKED(env), 부대 미지정 선택 로드 후
20기, 미니맵 우클릭/능력 v UNKNOWN, 건설·승선 N/A, S3 BLOCKED(env)+analogy, S5 정적 귀속)을 명시해
사용자 milestone 재상정 여부를 정한다. 상세
`docs/history/laps/20260928_lap751_work_g5_s3_restart_attribution_menu_exit_env_confirmed.md`.

# lap 752 middle 검수 — G5 v8 (F) HOLD 유지, S3 analogy 거부: 원본 새 게임 초기화가 선택을 직접 0으로 만드나 v8 새 배열은 빠짐(work handoff)

## 현재 판정

- 모델/역할: Claude Code `claude-opus-5-5`/high, middle. 게임 실행 0회, 제품 코드 0 변경(문서만).
- 보호 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, v8 재빌드
  `ef46d1acd55af2f6007824bb416b3c991ae4afb195fb369b3e86b5ee9182ff08` 일치.
- **H-NEWGAME-INIT(정적 확정):** 원본 `0x4a3060`(게임 상태 `this=0x892410` 초기화, 호출자 `0x41b9c0`/
  `0x41bc4f`/`0x4c3e59`)은 저장 창 전체 `rep stosd`(0x38e5f dword) + `0x4a3168 mov [esi+0x6c14],ebx`
  (레거시 선택 count=0) + `0x4a31eb` 20칸 엔트리 0 루프로 게임 시작마다 선택을 비운다. v8 새 배열
  `0x0108C000..+0xCC`는 창 밖이라 어떤 게임 시작 초기화도 비우지 않는다(v8 `0x0108C000` 참조 `.text`10·
  `.rsrc`2, 0 채우기는 로드 래퍼뿐). lap751 "재시작=해체(dec)" 결과는 원본의 이중 보장 중 하나만 보여 준다.
- G5 v8 = `HOLD(좁은 조건부)`. 사용자 milestone 재상정·G1 착수 안 함. (A) 표는 this-상대 쓰기 2건 누락.

## 승격 작업자(work tier)가 이어서 검증할 한 가지

v9 = v8 + `0x4a3168` 1지점(`89 9E 14 6C 00 00` → `jmp cave; nop`, cave: 원 명령 + push edi/ecx/eax, `mov edi,
0x0108C000; mov ecx,0x33; xor eax,eax; rep stosd`, pop, `jmp 0x4a316e`) 빌드·pytest 고정. 로비 게임 시작·
"다시하기"에서 어느 4A3060 호출자가 불리는지 1회 귀속. 게임 시작/재시작 직전 새 배열에 가짜 stale(count=50,
선택 플래그 없는 유닛 슬롯)을 주입한 paired probe: v8 잔존(갭 실증)/v9 0/원본(레거시 영역 주입) 0. v8이
잔존하지 않으면 주체를 기록하고 v9 불필요 판정. 회귀 `make check` + S1/S2/S4 + lap747 핵심 coverage, (A)
표 보완. PASS 뒤 새 middle이 F 재검수. 상세
`docs/history/laps/20260928_lap752_middle_g5_f_s3_newgame_init_gap_v9_handoff.md`.

# lap 754 middle 검수 — G5 v9 (F) PASS, A~H 2단 판정 완료 → 사용자 3단 milestone 재상정(마일스톤 경계)

## 현재 판정

- 모델/역할: Claude Code `claude-opus-5-5`/high, middle. 게임 실행 0회, 제품 코드 0 변경(문서·(A) 표만).
- 보호 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, v8 `ef46d1ac…`, **v9
  `18181cdef6c787a2be9a3cf78a2851eb4d764074c972e2b13690f27af0fd2017`** 재빌드 일치.
- 정적: v8→v9 diff = hook+cave+헤더, `0x4a3060` 호출자 3곳 전수(모두 `this=0x892410`, 절대참조 0), hook은
  무조건 경로, this-상대 선택 disp 2건뿐. runtime(lap753 raw 재계산): 원본 CLEARED / v8 PERSISTED / v9 CLEARED,
  v9 S1/S2/S4 원본 패리티. 1단 `make check` 1122 passed·5 skipped, `SAFETY_PASS`/`CONTEXT_PASS`.
- **A~H(v9): A·B·C·D·F·H PASS, E 조건부, G `BLOCKED(env)` 수용.** G5 종료·G1 착수는 선언하지 않음.

## 승격 작업자/사람이 이어서 판단할 한 가지

이것은 제품 판정이 아니라 **사용자 3단 milestone 경계**다. 사용자가 G5 v9를 알려진 제한(G 멀티 BLOCKED(env),
부대 미지정 선택 로드 후 20기, 미니맵 우클릭/능력 v UNKNOWN, 건설·승선 N/A, 체력바 46/50 가림 PLAUSIBLE,
S3 초기메뉴 UI env 미실측, S5 정적 귀속, 간접호출 정적 미증명·R2, 부대 H1~H3 edge)과 함께 승인하면 G1을
재개하고, 반려하면 지정 항목만 다음 work가 처리한다. 승인 전 추가 G5 work/middle 회차는 필요 없다. 상세
`docs/history/laps/20260928_lap754_middle_g5_f_s3_v9_review_pass_milestone_resubmit.md`.

## 사용자 판단 (2026-09-29 00:59, lap754 해소)
**2026-09-29 00:59 사용자 판단(AskUserQuestion):** G5 v9 milestone **보류**. 추가 확인 항목: **(1) 부대 미지정 드래그 50기 선택이 저장/로드 후 50기 전부 복원**(현재 앞 20기만; 원본 세이브 형식과 양방향 호환 유지 조건 — 원본 EXE가 v10 세이브를 열어도 크래시 없이 앞 20기, v10이 원본 세이브를 열어도 정상), **(2) 미니맵 우클릭 이동과 특수능력 v를 실제로 동작하는 조건에서 원본20/후보50 paired 확인**(격리 환경에서 미니맵이 검게 그려지고 무반응인 원인 — 렌더/입력 좌표/미니맵 활성 조건 — 을 찾고, v는 설명서·툴팁·대상 조건 탐색). 멀티·초기메뉴 경로는 알려진 제한 유지. G1 재개 금지. 진행: work가 (1)을 먼저 구현(v10: 21~50번째 엔트리를 저장 창 안의 미사용 영역 또는 세이브 파일 뒤 추가 블록에 보존, 로드 시 복원) → paired 재측정 + 회귀, 그 다음 (2). 끝나면 middle 재검수 후 사용자 재상정.
