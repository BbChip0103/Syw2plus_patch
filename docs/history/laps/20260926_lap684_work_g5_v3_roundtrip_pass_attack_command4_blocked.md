# 2026-09-26 | lap 684 | 목표 G5

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5`(세션 보고 모델ID), 실무(구현·실행), high. 이번 lap에서 실제 코드/테스트를 수정하고 격리 실행했다.
- 가설 / 사용자 관찰: 2026-09-26 16:15 운영자 확인(lap683 충돌 해소)이 지시한 다음 한 가지 그대로 —
  v3 `e5004764…` 하나로 ① `tools/g5_candidate_drag_probe.py` roundtrip을 v2가 아닌 v3 기준으로 원본·후보 fresh 실행,
  ② 공격 판정을 `command(+0x290)==4` ever-matched 누적 기준으로 바꾸고(`pending!=1` 금지) 이동과 **다른 새 목적지**로 원본·후보 각 실행.
- 예상 PASS / FAIL 조건: roundtrip은 후보 `50/50/50`·51번째(56개 중 6개) 미선택·group20+field49·fault 0, 원본 `20/20/20`이면 PASS.
  공격은 `command==4` ever-matched가 공격 가능 유닛(worker 제외) 전원이면 PASS; 원본·후보 모두 0이면 목적지를 바꿔 1회 재시도 후 BLOCKED.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  - `tools/g5_candidate_drag_probe.py`: import를 `g5_selection_cap50_v2`→`v3`로, `TARGET_SHA`를 v2 `ae495fa5…`→v3 `e5004764…`로 교체(다른 파일은 각자 v2를 독립 임포트하므로 영향 없음, 확인함).
  - `tools/g5_worker_relative_move_attack_probe.py`: 이동과 공격이 같은 목적지를 쓰던 lap682 결함을 고쳐 `ATTACK_PRIMARY_DEST_OFFSET=(3,6)`/`ATTACK_FALLBACK_DEST_OFFSET=(-3,6)`(이동 목적지 dy=6 행과 같은 검증된 열린 땅이지만 dx가 다름)을 추가. worker를 공격판정 모집단에서 제외(`attack_capable_slots`). 공격 목적지 world 좌표에 실제 owner1 type2 표적을 자체보정 좌표로 정확히 배치해 클릭이 빈 땅이 아닌 실제 표적에 닿게 함. raw `command` 히스토그램·`target_match_count` 기록 추가.
  - `tests/test_g5_worker_relative_move_attack_probe.py`: 새 공격/이동 목적지 오프셋이 겹치지 않음을 확인하는 회귀 1건 추가.
  - 제품 EXE/원본/바이너리 0 변경. 커밋 없음(`LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  - 보호 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(모든 실행 전후 재해시 일치, `source_unchanged=true` 6/6).
  - 후보 `e5004764e945350a0391d69035f8c8f0d305fcca7d6aaa54066836bac3de6977`(직접 재빌드해 이번 세션에서 재확인, lap680~683과 동일 SHA).
  - 격리 Wine/Xvfb 1600×1200, PS3 solo owner0, worker slot1198 앵커 dense 7×8 type2 55기(지도 시드 미고정, self-calibration 방식).

## 실행 명령 / 로그 / 캡처 경로 및 해시

1. `PYTHONPATH=. .venv/bin/python -m tools.g5_candidate_drag_probe --variant original --ui-roundtrip --artifact-root .../20260926_lap684_g5_v3_roundtrip_original/run1` → `probe-result.json` SHA256 `d1ab2899…9fe2e4`.
2. 동일 `--variant candidate --ui-roundtrip` → `probe-result.json` SHA256 `ee439e0e…9784f59`.
3. `PYTHONPATH=. .venv/bin/python -m tools.g5_worker_relative_move_attack_probe --variant candidate --artifact-root .../candidate_run1` (지면-only 새 목적지) → SHA256 `207c8602…1710f926`.
4. 동일 `--variant original --artifact-root .../original_run1` → SHA256 `6df25d7f…24b9a37ab`.
5. 위 두 실행이 공격 0/0으로 나와 lap683 지시("무효 입력 시 목적지 바꿔 1회 재시도")에 따라 실제 owner1 표적을 목적지 world 좌표에 배치하는 두 번째 방법으로 재시도: `--variant candidate --artifact-root .../candidate_run2_target` → SHA256 `19e6b3de…f80280f01`; `--variant original --artifact-root .../original_run2_target` → SHA256 `7e911bc0…1245917dcc`.
6. `PYTHONPATH=. .venv/bin/python -m pytest -q tests/test_g5_candidate_drag_probe.py tests/test_g5_worker_relative_move_attack_probe.py patches/selection/test_g5_selection_cap50_v{1,2,3}.py` → **22 passed**.
7. `make check` foreground(nohup+폴링, lap659 방식) → **973 passed in 648.20s**, `ruff`/`compileall`/`mypy`/`checks/context_limits.py` 모두 PASS. 로그 `logs/gates/20260926_lap684_make_check.log`.
8. `bash checks/safety.sh check` → `SAFETY_PASS`.
9. 실행 후 `local/runtime/g5-lap684-attack-{original,candidate}-run{1,2}*/*/game` 사본(각 ~2.2GB) 삭제, output/manifest/prefix/로그는 보존. 디스크 33GB 여유로 복귀.

## 측정값 / 판정

**① v3 roundtrip — PASS(양쪽 모두).**
- 원본: `selected/recalled/loaded-recalled` 20/20/20(unique 20), `move_selection` 20, `movement_command_nonzero` 20, save 생성, cleanup ok, source 불변. `status=PASS_ORIGINAL_CAP20`.
- 후보: `selected/recalled/loaded-recalled` 50/50/50(unique 50), `ui_roundtrip.checks` 7개 전부 True(`selected_50`·`group_stored_stock20_plus_overflow49`(stored group1_count=20, fixture group_counts `{-1:6, 1:49}` = 55개 fixture 중 49가 그룹1, 6이 미선택 → 56개 후보(worker+55) 중 50 선택, 6 미선택과 정확히 일치)·`deselected`·`recalled_50`·`save_created`·`group_retained_after_load`·`recalled_50_after_load`). `move_selection` 50, `movement_command_nonzero` 50, crash/exception 없음(fault 0). `status=PASS_UI_ROUNDTRIP`, `candidate_sha256`/`private_exe_sha256` 모두 `e5004764…` 일치.
- lap683가 요구한 항목(51번째 미선택·group20+field49·fault 0·원본20/20/20) 전부 v3 기준으로 재확인됐다.

**② 공격 `command==4` paired — 4회 실행 모두 0, BLOCKED.**
- run1(지면 클릭만, 이동과 다른 새 목적지 `[±3,6]`): 후보 0/49, `raw_command_histogram={'1':48,'3':1}`; 원본 0/19, `{'1':18,'3':1}`. 둘 다 `command==4`가 단 1건도 없다(순수 idle/이동 잔여값뿐).
- run2(같은 새 목적지의 world 좌표에 owner1 type2 실제 표적을 자체보정으로 정확히 배치 후 클릭): 후보 0/49(`target_match_count=0`, `observed_target_uids=[]`), 원본 0/19(동일). 후보 run2는 이동 phase도 이 특정 실행에서 2/50만 수렴했지만(지형 변이, 별개 이슈) 공격 목적지·판정 자체는 원인이 아니다 — 원본 run2는 이동 20/20 정상인데도 공격은 동일하게 0.
- 4회 전부 `source_unchanged=true`, `cleanup.ok=true`, SHA 불변.
- 결론: lap667~682(9~15회 이상, 스프라이트 클릭·건물 클릭·공격이동 지면클릭·같은 목적지 paired 등)에 이어, **목적지를 이동과 명확히 분리하고 실제 표적을 그 자리에 배치해도** UI 클릭 기반 공격 입력은 `command==4`를 한 번도 만들지 못했다(원본·후보 동일하게 0). lap681의 유일한 양성 신호("41/50")는 이동과 동일한 고정 픽셀에서 나왔고 lap682·684 모두 그 픽셀·그 방법을 재현하지 못했다 — 재현 불가능한 단발성 관측으로 재확인.
- 판정: **BLOCKED**(lap683가 명시한 계약대로 — "원본·후보 모두 0이면 목적지 바꿔 1회 재시도 후 BLOCKED로 기록"). G5 공격 판정을 UI 클릭으로 계속 시도하는 것은 이 lap으로 중단하고 middle/strategy가 방법 자체를 재정의해야 한다.

## 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태

- 회귀 22 passed, `make check` 973 passed, ruff/compileall/mypy/`CONTEXT_PASS`/`SAFETY_PASS` 모두 PASS. 제품 EXE/원본 0 변경.
- v3 roundtrip은 이번 lap에서 처음으로 PASS 기준을 완전히 충족했다(lap683가 요구한 그대로). 공격 브로드캐스트 50은 여전히 미해결이며, 이번 lap은 "UI 클릭이 방법 자체로 부적합하다"는 기존 가설을 원본·후보 대조와 실제 표적 배치까지 포함해 가장 강하게 재확인했다.
- 멀티 동기화는 계속 `UNKNOWN`. 사용자 milestone 승인 없음.

## 추가 조치 (2026-09-26 16:35 운영자 방향 반영, 같은 lap 안에서 계속)

middle 회부 전 운영자가 STATUS.md에 새 방향을 남겼다: 공격 판정을 살아있는 `+0x290==4`(원본에서도 0으로 나와
판정 기준 자체가 입력과 안 맞음)에서 **`+0x384` pending 워드의 정확한 값 `0x1000004`**(lap678 writer trace가 확인한
공격 전용 값, 이동은 `0x1000003`)로 바꾸라는 지시다. `tools/g5_worker_relative_move_attack_probe.py`의 ATTACK
phase를 다시 써서 클릭 직후 3초를 0.1s 간격으로 표본화하며 ① 순간 최대 정확값 카운트, ② 누적("한 번이라도"
`command==4`에 도달한 슬롯 수, `ever_command4_count`), ③ 그 순간의 `pending_xy`가 목적지 world와 일치하는 수를
함께 기록하도록 구현했다. 원본·후보 각 2회 재실행(총 4회, 이동과 분리된 새 목적지 유지):

| 실행 | 순간 최대(pending==0x1000004) | **누적 ever `command==4`** | pending_xy 일치 |
|---|---|---|---|
| 원본 run1 (19명 중) | 19/19 | **19/19** | 19/19 |
| 원본 run2 (19명 중) | 17/19 | **19/19** | 19/19 |
| 후보 run1 (49명 중) | 36/49 | **1/49** | 0/49 |
| 후보 run2 (49명 중) | 25/49 | **0/49** | 49/49 |

**판정: 원본 PASS(2/2 재현, `ever_command4_count`=100%), 후보 FAIL(2/2 재현, 1/49·0/49).** 순간 최대값은 두 변형
모두 표본 간격(0.1s) 탓에 흔들리지만(원본도 17~19로 흔들림), 3초 누적 "한 번이라도 `command==4`에 도달했는가"는
원본에서 완전히 안정적으로 100%가 나오고 후보에서는 두 번 모두 거의 0에 머문다 — 이는 하네스 잡음이 아니라
**후보(v3)가 이동(`command==3`, lap682: 50/50 안정) 주문은 청크 분할로 온전히 처리하면서 공격(`command==4`) 주문은
청크 분할이 있어도 선택 인원 대부분에게 실제 살아있는 공격 상태로 이어지지 못한다**는 재현 가능한 차이다.
`pending_xy`(목적지 좌표, 이동 성분)는 후보 run2에서 49/49로 온전히 전파됐는데 공격 전용 pending 워드·`command==4`
전환만 실패하는 패턴은, 주문 타입 4가 타입 3과 공유하지 않는 별도 필드(공격 전용 플래그/타겟)가 청크 경계를
넘을 때 손실되거나 경쟁 상태에 빠진다는 가설과 일치한다.

## 다음 한 가지

새 middle 세션이 G5 2단을 재검수한다: **v3 roundtrip(①)과 이동 paired(lap682)는 PASS로 승인 가능하다.**
**공격 브로드캐스트(②)는 이번 lap의 정정된 판정(`ever_command4_count`, 3초 누적)으로 원본 2/2 100% 대비
후보 2/2 ≤1/49의 재현 가능한 FAIL이다** — 이전의 "UI 클릭 자체가 안 된다"는 BLOCKED 결론은 판정 필드가
잘못되어 있었을 뿐이었음이 이번에 밝혀졌다. 다음 work는 middle 없이: 이 표에서 확인된 원본 100%/후보 ~0%
격차의 원인을, `patches/selection/g5_selection_cap50_v3.py`의 청크 재호출 사이에서 order-type별로 다르게
쓰이는 필드(특히 타입4 전용 target/공격 플래그, xy와 달리 각 청크가 자기 자신의 슬롯에만 쓰는지)를 gdb로
직접 추적해 원인을 좁히고 최소 수정 후 이 4-run 표를 다시 재현한다(원본·후보 각 2회, `ever_command4_count`
기준). 그 결과를 가지고서만 새 middle이 G5 2단을 다시 검수한다.
