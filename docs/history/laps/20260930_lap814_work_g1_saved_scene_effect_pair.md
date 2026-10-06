# lap814 work — G1 saved-scene effect-based input pair

- 날짜/lap: 2026-09-30 / lap814
- 목표: lap813 handoff대로 동일 `save006.dat` 장면에서 selection/drag, gate=1 minimap, controlled production을 baseline 800 vs W60 ON으로 paired 재측정.
- 가설: count/camera 단일 즉시 샘플 대신 selection slot 목록·semantic effect polling·gate 원복을 사용하면 sample race와 자연 tick을 분리할 수 있다.
- 변경파일: `tools/g1_saved_scene_probe.py`, `tests/test_g1_saved_scene_probe.py`. 제품 EXE/원본/참고 저장소/bridge 코드는 변경하지 않았다.
- 원본/후보 SHA: 보호 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, save006 `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`; bridge source unchanged.
- 실행: `PYTHONPATH=. .venv/bin/python tools/g1_saved_scene_probe.py --runtime-root local/runtime/g1_saved_scene_lap814_r3 --artifact-root /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/g1_saved_scene_lap814_r3`; fresh private game/prefix/Xvfb, baseline 800×600, candidate `SYW2_G1_NATIVE_2X_BLIT=1` + `SYW2_G1_MIRROR2X=1`, synthetic=false.
- r1/r2: r1 slot dword 전체를 slot으로 읽은 오류, empty point가 빈 땅이 아닌 오류, camera-only minimap 판정, Stop 셀 production 오인 가능성을 확인했다. r2에서 slot/empty/gate/unit-effect를 수리했다. r3은 drag rectangle `(100,40)->(400,220)`로 재실행했다. 모든 실패 artifact는 `temp/Syw2plus_patch/g1_saved_scene_lap814[_r2]`에 보존했다.
- 수치/PASS: r3 scene exact equal; selection `982→151`, empty `1→0`, drag exact `[124,140,151,170]`; minimap gate `00000000→01000000→00000000`, camera `[158,101]` 불변이나 selected type111 command `1→3`/production field 변화 양쪽 동일; candidate trace `events1478`, converted242, mirror366, primitive13761, covered129835, nearest oracle1.0; crash0, source unchanged, game removed, prefix residue0. (`events1690`/mirror578/primitive23547은 lap815 middle이 raw로 확인한 r2 수치의 단순 전사 오류여서 r3 수치로 정정.)
- production: owner0/type111 target selection은 확인했으나 `(670,490)` UI 셀은 Stop으로 관측되어 worker queue `command15/production_type7/reserved+10` 효과는 `UNKNOWN`이다. 자연 tick 자원 변화는 효과로 세지 않았다.
- 검증: targeted pytest `5 passed`, Ruff/compileall/diff-check PASS. 최종 Fast `make lint`→`make typecheck`→`make check`와 safety는 다음 기록에 fresh로 남긴다.
- 다음행동: 새 middle이 r3 pair-result/raw SHA와 selection/drag/minimap effect를 독립 재계산하고, production mapping을 UNKNOWN으로 수용하거나 근거 있는 고정 production-cell probe를 지정한다. G1 완료/사용자 승인은 선언하지 않는다.
