# lap 641 — G5 candidate runtime failure (2026-09-26)

- 날짜/lap/목표: 2026-09-26 / 641 / G5 드래그 선택 상한 20→50.
- 가설: 원본과 동일한 `(120,120)→(760,540)` 드래그에서 11×5 조밀 fixture를 사용하면 후보가 55기 중 50기를 선택하고 명령을 전달한다.
- 변경파일: `tools/g5_candidate_drag_probe.py` — 드래그 사각형을 원본 성공 계약으로 복구하고 fixture를 11×5(count 11×5, y 간격 1)로 변경. 원본/참고 저장소와 EXE는 쓰지 않았다.
- 원본 SHA: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` (before/after 불변).
- 후보 SHA: `a123498ab6378df17536718b7ec64389423fb0b7d0800a417cb3d476a1a9bc98`.

## 실행/fixture

- 명령: `PYTHONPATH=. python3 tools/g5_candidate_drag_probe.py --variant original --runtime-root local/runtime/g5-lap641-original --artifact-root /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260926_lap641_g5_original_control`
- 원본 결과: `PASS_ORIGINAL_CAP20`; isolated Wine/Xvfb 1600×1200, PS3, camera `[161,90]`, owner0 type2×55, used `735/1500`, live57, selection20/unique20, movement20, cleanup residual0.
- 명령: `PYTHONPATH=. python3 tools/g5_candidate_drag_probe.py --variant candidate --runtime-root local/runtime/g5-lap641-candidate --artifact-root /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260926_lap641_g5_candidate_11x5`
- 후보 결과: private EXE SHA와 runtime contract PASS, relocated base `0x0108c000`/capacity50, same camera/drag, fixture requests `(167,96..100)`×11 = 55, selection `36/36`, movement command `36`, status `FAIL_SELECTION_CAP`, process log에 `wine: Unhandled exception 0x80000004`와 crash dialog capture.
- raw/captures/provenance: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260926_lap641_g5_candidate_11x5/`; candidate `probe-result.json`/`probe.log`/before-drag.png/after-drag.png.

## 검증 판정

- PASS: `checks/context_limits.py` → `CONTEXT_PASS`; original control; candidate/source hash guards; private cleanup/source unchanged.
- FAIL/BLOCKED: required candidate selection50 and command50; candidate selected36 unique units only, and crash dialog was observed after command. 51st rejection, save/load, full `make check`, second-tier review, and milestone approval are SKIP.
- `make check` was not rerun after the failed mandatory runtime gate; prior lap640 Fast result is not current runtime verification.

## 승격 작업자가 이어서 검증할 것

1. §189 raw/capture/candidate bytes를 독립 대조해 crash가 selection relocation consumer, command path, fixture overlap, 또는 harness shutdown 중 어디에 귀속되는지 판정한다.
2. 11×5 월드 격자가 실제 `(120,120)→(760,540)` hit-test 안에 몇 개 들어가는지 screen/world 변환과 raw unit positions로 계산하고, `0x0043877A` 패치 효과와 분리한다.
3. 원인·안전 범위가 확정되기 전에는 재시도하지 않는다. 승인된 새 후보에서만 원본20 → 후보50/51 → 명령50 → canary/save-load 순으로 fresh runtime을 연다.

판정: **`BLOCKED(candidate_runtime_36_and_crash)`**. 변경·raw·capture·미커밋 상태를 보존했다.
