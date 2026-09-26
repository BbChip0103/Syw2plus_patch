# 2026-09-26 | lap 640 | 목표 G5

- 날짜/lap/목표: 2026-09-26, lap 640, G5 드래그 선택 상한 20→50.
- 가설: `FUN_004384B0`이 caller local list/count를 20에서 자르는 실제 원인은 호출 경로의 `FUN_004386E0` append 비교일 수 있다.
- 원본·후보 SHA: protected source `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; candidate after exact patch `a123498ab6378df17536718b7ec64389423fb0b7d0800a417cb3d476a1a9bc98`.
- 변경 파일: `patches/selection/g5_selection_cap50_v1.py`, its test, `tools/g5_selection_upstream_trace.py`, `tools/g5_candidate_drag_probe.py`, `analysis/g5_selection_cap_inventory.json`, `analysis/memory_maps/g5_drag_hit_test_cap_lap640.md`. Original/reference repositories and committed files were not modified.

## Evidence and execution

- Fresh isolated Wine/Xvfb 1600×1200, PS3, owner0 type2×55 dense fixture around slot1198, `used=735/1500`, `live=57`, private cleanup residual0/source unchanged.
- Read-only gdb trace at `0x004384B0` recorded one drag call from `0x0041E03B`, seven arguments, first-argument output list, and second-argument count pointer. The stock candidate list had 20 non-zero entries and count20.
- The same trace hit `0x0043877A` 26 times. At the final calls `EAX=20`, `EBP=0x0031f81c`, and the original instruction compared `AX` with `0x14`. Exact candidate edit: `0x0043877A: 66 3d 14 00 → 66 3d 32 00`.
- Patched candidate trace confirmed the new compare value `0x32`, 26 append-helper calls, count26, and writer26; no crash. Raw traces: `temp/Syw2plus_patch/20260925_lap640d_g5_hit_append_limit/` and `20260926_lap640g_g5_patched_trace/`.
- A patched candidate probe with the prior drag rectangle measured selection21/movement21, proving the old 20 cap was passed but not proving 50.
- To make the fixture/drag input cover the content, probe input was changed from `(120,120)→(760,540)` to `(20,20)→(780,470)`, above the command UI.
- Required original control with the new identical drag input failed: selection5, unique5, movement5, exit2. Candidate execution after this failed control was intentionally skipped. Raw original result: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260926_lap640h_g5_original_full_drag/probe-result.json`.

## Validation

- Targeted patch/inventory/runtime tests: 173 passed; later full `make check`: **897 passed in 591.82s**; Ruff, compileall, mypy, and `CONTEXT_PASS` passed; `bash checks/safety.sh` returned `SAFETY_PASS`.
- PASS: exact old-byte guard, candidate SHA, runtime source protection, patched literal observed, cleanup/source invariants.
- FAIL/BLOCKED: required original same-input control was 5 rather than the expected stock cap20. G5 50/51, 50-unit command, save/load, independent second-tier review, and milestone approval remain unverified.

## Next action

The promotion worker must first resolve why the new full-content drag produces stock count5 while the earlier dense control produced count20: independently fix/verify the camera, drag rectangle, and living-unit visibility contract on the original. Only after a fresh original count20 control may the `a123498a…` candidate be rerun for count50, 51st rejection, 50 commands, and subsequent save/load.
