# 2026-09-25 | lap 636 | 목표 G5

- 날짜/lap/목표: 2026-09-25, lap636, G5 드래그 선택 상한 20→50.
- 가설: 후보가 새 relocated selection storage를 읽어도 20에서 멈춘 원인은 (a) indexed selection readers 3곳의 relocation이 old-byte 길이 오류로 적용되지 않은 것과 (b) selection consumer `0x0041DC40`의 잔여 20-entry local-list 상한이라고 보았다.
- 변경파일: `patches/selection/g5_selection_cap50_v1.py`, `patches/selection/test_g5_selection_cap50_v1.py`, `tools/g5_candidate_drag_probe.py`(후보 SHA 갱신). 원본/참고 저장소·EXE·게임 데이터·커밋은 수정하지 않았다.
- 원본/후보 SHA: protected original `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; candidate `3877194855f54a8b63ea064a6be9f405485bffcb98286198f9a3f5a785459757`.
- 패치 범위: indexed reader old bytes에 누락된 trailing `00`을 보강해 `0x0041EC71/0x0041ED5E/0x0041EEAF`를 실제 relocated base로 고쳤다. `0x0041DC40` consumer의 frame `0x98→0x230`, local-list zero/scan 상한 `0x14→0x32`, 기존 임시 word buffer `0x80→0x200`, 양 epilogue를 함께 old-byte 고정했다.
- 실행명령: `.venv/bin/python -m pytest -q patches/selection/test_g5_selection_cap50_v1.py tests/test_g5_selection_inventory.py patches/population/test_runtime_bridge_contract.py`; `.venv/bin/python tools/g5_candidate_drag_probe.py --variant candidate --runtime-root local/runtime/g5-lap636-candidate --artifact-root /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260925_lap636_g5_candidate_cap50`.
- 기계 결과: targeted `10 passed`; py_compile PASS; candidate build length unchanged and SHA matched. 전체 `make check`는 필수 runtime 실패 뒤 실행하지 않아 SKIP이다.
- runtime fixture/environment: fresh private `tools.runtime_env.prepare` copy, isolated Wine/Xvfb `1600x1200`, PS3 tick2; owner0, type2×55 dense rows around raw worker slot1198, used `735/1500`, live57; source before/after SHA unchanged, cleanup residual0/ok=true.
- runtime 결과: candidate relocated reader `0x0108c000`, capacity50이었으나 selection `count=20`, unique20, movement command nonzero20, process exit2(`FAIL_SELECTION_CAP`). Artifact/provenance/captures: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20250925_lap636_g5_candidate_cap50/`; probe-result SHA는 해당 `probe-result.json`을 참조한다.
- PASS/FAIL/SKIP: original prior dense baseline `20/20`은 lap635 근거로 보존; 이번 patch targeted PASS; candidate 50/51·50기 명령·save/load·G5 PASS FAIL/SKIP; source safety/cleanup PASS.
- 다음행동/승격: `loop/ESCALATE_SOL` §184로 승격. 승격 작업자는 candidate runtime에서 selection writer 호출/count 및 `0x0041DC40` 진입을 hardware watchpoint 또는 equivalent trace로 독립 대조하고, 새 후보를 만들기 전 20-entry 원인을 확정해야 한다. 그 전에는 재실행·G5 PASS·save/load를 주장하지 않는다.
