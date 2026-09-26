# lap657 ESCALATE_SOL 보존본

- 원문: `loop/ESCALATE_SOL` 97줄, SHA256 `8f759c2fa8d3e8cb3aa962ca1e19cb9b51a3b8e8d349fe46676af08f0b15c928`
- 처리: lap657 strategy가 49 경계 원인을 특정(`docs/history/laps/20260926_lap657_strategy_g5_selection_end_bound.md`)한 뒤 전문을 여기 보존하고 파일을 해제했다.

---

# lap656 승격 요청 — 49 경계는 hit-test 상한 off-by-one으로 입증되지 않음

- 날짜/lap: 2026-09-26 / 656
- 역할: hands-on work
- 상태: BLOCKED(FAIL-B; 필수 runtime은 lap655에서 선택49/55·명령49)
- 이번 lap 변경: 제품 코드·EXE·원본·참고 저장소·fixture 변경 없음. 독립 정적 대조와 Fast 검증, history/STATUS 갱신만 수행했다.
- 보호 원본 SHA: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변.
- 후보 SHA: `6f6a4f859be4b2281ec2014e817b7692adf2d04226b0ac14b3ac32ac06f4e091`.
- 독립 근거: 원본 `0x0043877A`는 `count >= 0x14`에서 거부하고 append 후 count를 증가한다. 후보 `0x32`는 `count >= 50`에서 거부하므로 count 0..49를 허용한다. 그러므로 lap655의 49/55만으로 `0x32`를 `0x33`으로 바꾸는 off-by-one 수정은 근거가 없다. `FUN_004386E0` 내부 유효성/좌표 판정 또는 `FUN_004384B0` 호출 전 필터를 직접 추적해야 한다.
- Fast 검증: targeted G5/inventory `12 passed`; `make check` `905 passed in 792.26s`; ruff/compileall/mypy/context PASS; `bash checks/safety.sh check`=`SAFETY_PASS`.
- 다음 승격 작업: 동일 fixture/입력을 맹목 재시도하지 말고, fresh isolated original20/candidate50 paired trace에서 `0x004384B0`의 후보별 eligible 호출 수와 `0x004386E0`의 append/return 결과를 수집해 첫 7개(slot1141..1147) 제외를 hit-test/카메라 변환/건물 점유 중 하나로 귀속한다. 그 뒤에만 최소 패치와 새 candidate runtime을 실행한다.
- 상세: `docs/history/laps/20260926_lap656_work_g5_offbyone_escalated.md`.

# lap651 승격 요청 — G5 frame 수리 후 남은 20 전제

- 날짜/lap: 2026-09-26 / 651
- 역할: hands-on work
- 상태: BLOCKED(FAIL-B)
- 이번 변경: `patches/selection/g5_selection_cap50_v1.py`의 FUN_0041DC40 consumer frame `0x230→0x270`, word-buffer clear `0x0a→0x19`, 정적 회귀 테스트 추가; `tools/g5_candidate_drag_probe.py`에 새 후보 SHA 반영.
- 원본 SHA: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` (보호 원본·참고본·로컬 입력 동일, 변경 없음)
- 후보 SHA: `6f6a4f859be4b2281ec2014e817b7692adf2d04226b0ac14b3ac32ac06f4e091`
- 실행: Wine/Xvfb 1600×1200, solo owner0, type2 synthetic 55기 dense 7×8, PS3, 동일 드래그/우클릭 명령.
- 결과: crash 없음·cleanup/source unchanged PASS이나 선택 `42/55` unique, 이동 명령 `42` → G5 측정식 FAIL-B. `50/51`, canary/save/load는 SKIP.
- 증거: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260926_lap651_g5_candidate_frame270/` (probe-result SHA `50f635ef0abece4710611ff322b6be34f092c8df8ceab1f5a6ed590cb0baf4aa`, before/after 캡처 SHA는 lap history 참조). 실행 game 사본은 삭제했고 output/prefix/logs는 보존.
- 검증: targeted 11 passed; `make check` 904 passed, ruff/compileall/mypy/context PASS; `bash checks/safety.sh check` PASS.

승격 작업자가 이어서 할 일:
1. 같은 frame 수리를 반복하지 말고, 선택이 42에서 멈춘 직접 원인을 다음 20 전제에서 독립 확인한다.
2. 우선 `FUN_004AE550` 명령 패커의 고정 20칸과 선택 UI/표시 consumer의 남은 상한을 원본 old bytes·호출 계약으로 대조하고, 범위를 하나로 좁힌다.
3. 원인과 새 최소 변경이 확정된 뒤에만 새 후보를 만들고 동일 fixture로 fresh 실행한다. G5 PASS 조건은 여전히 선택 50·이동 명령 50·51번째 제외·오염/크래시 없음이다.

# lap652 승격 요청 — upper fixture 위치 검증 실패

- 날짜/lap: 2026-09-26 / 652
- 역할: hands-on work
- 상태: BLOCKED(FAIL-B; 필수 fresh runtime 측정 실패)
- 변경: `tools/g5_candidate_drag_probe.py`의 synthetic 55기 fixture y 시작점을 작업자 y+4에서 y-20으로 변경해 화면 상단 배치를 시도했다. 후보 PE32 패치와 원본은 변경하지 않았다.
- 원본 SHA: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` (전후 불변)
- 후보 SHA: `6f6a4f859be4b2281ec2014e817b7692adf2d04226b0ac14b3ac32ac06f4e091`
- 실행: `PYTHONPATH=. .venv/bin/python tools/g5_candidate_drag_probe.py --variant candidate --runtime-root local/runtime/g5-lap652-candidate-fixture-upper --artifact-root /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260926_lap652_g5_candidate_fixture_upper`
- 결과: fixture 요청 55기는 성공했지만 이번 실행 작업자 `(21,92)`, camera `(19,90)`에서 요청 y=72~79가 화면 밖이 되어 선택 `1/55`, 이동 명령 `1`; crash 없음은 확인했으나 G5 측정식은 성립하지 않는다. probe exit `2`, cleanup/source unchanged PASS.
- 증거: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260926_lap652_g5_candidate_fixture_upper/`; `probe-result.json` SHA `fc5b859db25f91a18ecfd708d80daf4482114e3eab403d2844b68505f6811a4f`, before `422e6a094dd0ae803105dd3dde4049dcddc2b8a464fecc0dca4494d46e6387a5`, after `79b24f23161779afa4635c7d73c8fd7ba89241ad0c3cb85a8ff4b866214484ed`.
- 검증: `make doctor` PASS; fixture count/py_compile PASS; `make check` 및 G5 제품 PASS는 필수 runtime 실패 게이트로 실행하지 않았다. 실행 사본 `local/runtime/.../game`은 위생 규칙에 따라 삭제했고 output/manifest/prefix/log는 보존했다.

승격 작업자가 이어서 할 일:
1. 이 y-20 변경을 그대로 재시도하지 말고, minimap 이후 실제 camera 좌표를 기준으로 fixture를 화면 y=120~430에 놓는 계산을 정한다(현재 worker/camera가 lap651과 달라졌음).
2. 같은 후보/원본 보호 조건과 55기 fixture를 유지해 fresh 실행하고, 선택 50·명령 50·51번째 제외를 확인한다.
3. 그 fresh 측정이 성립한 뒤에만 `make check`와 50/51·UI/부대지정/save/load 검증을 이어간다.

# lap653 승격 요청 — worker-centered fixture still selects 49

- 날짜/lap: 2026-09-26 / 653
- 역할: hands-on work
- 상태: BLOCKED(FAIL-B; 필수 fresh runtime selection=49/55)
- 변경: `tools/g5_candidate_drag_probe.py`의 fixture를 anchor slot1198 중심 dx=-3..3, dy=-4..3의 고유 55 cell(`count=1`, anchor 제외)로 바꾸고 생성 직후 `after-fixture.png`를 기록했다. 후보 PE32·보호 원본·참고 저장소는 변경하지 않았다.
- 원본 SHA: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 후보 SHA: `6f6a4f859be4b2281ec2014e817b7692adf2d04226b0ac14b3ac32ac06f4e091`.
- 실행: isolated Wine/Xvfb 1600×1200, PS3 solo owner0, worker/anchor slot1198 type31 `(142,42)`, camera `[140,40]`, synthetic type2 55 at x139..145/y38..45 except `(142,42)`; artifact `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260926_lap653_g5_candidate_worker_grid/`.
- 결과: fixture receipts `55/55`; 생성 직후 캡처에서 55기가 보임; selection `49`, unique `49`; omitted slots `1141..1147`(y=45 행), movement command `49`; crash 없음, cleanup residual0, source unchanged. Probe exit2/status `FAIL_SELECTION_CAP`.
- 검증: fixture contract/py_compile PASS; targeted G5/inventory `11 passed`; `CONTEXT_PASS`; `SAFETY_PASS`. `make check`, 50/51, command50, UI/group/save/load는 필수 runtime FAIL-B 뒤 SKIP. G5 PASS·middle review·사용자 승인은 없음.

승격 작업자가 이어서 할 일:
1. 같은 fixture 계산과 동일 후보를 맹목 재시도하지 말고, y=45 행 7개가 빠지는 직접 원인을 camera/HUD 드래그 경계와 hit-test 중 하나로 독립 귀속한다.
2. 필요하면 방향키로 camera를 이동하는 입력을 포함한 원본 20 대조를 먼저 만들고, 그 대조가 성립한 뒤 candidate fresh를 실행한다.
3. 원인·새 최소 변경·fresh 50/50 측정이 모두 성립하기 전에는 50/51·UI/부대지정/save/load나 G5 PASS를 주장하지 않는다.

# lap654 승격 요청 — 확장 드래그 사각형도 선택 49에서 정지

- 날짜/lap: 2026-09-26 / 654
- 역할: hands-on work
- 상태: BLOCKED(FAIL-B; 필수 fresh runtime selection=49/55)
- 변경: `tools/g5_candidate_drag_probe.py`의 공통 드래그 입력을 `(120,120)→(760,540)`에서 `(200,170)→(730,445)`로 바꿨다. worker-centered 55기 fixture와 후보 PE32 패치는 변경하지 않았다.
- 원본 SHA: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 후보 SHA: `6f6a4f859be4b2281ec2014e817b7692adf2d04226b0ac14b3ac32ac06f4e091`.
- 실행: `PYTHONPATH=. .venv/bin/python tools/g5_candidate_drag_probe.py --variant candidate --runtime-root local/runtime/g5-lap654-candidate-drag-rect --artifact-root /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260926_lap654_g5_candidate_drag_rect`; isolated Wine/Xvfb 1600×1200, PS3 solo owner0, worker `(142,42)`, camera `[140,40]`, synthetic unique 55.
- 결과: fixture `55/55`; candidate selection `49`, unique `49`; selected slots `1148..1198`, omitted `1141..1147` (y=45); movement command `49`; crash 없음·cleanup residual0·source unchanged PASS. Probe exit2/`FAIL_SELECTION_CAP`; result SHA `3d316b0deee46adda81030e0d2ab6589dfda53b7d2c53a049383121f0107fb02`.
- 증거: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260926_lap654_g5_candidate_drag_rect/`; before `b6f1279b46f89e46694a66082997b28abc107d8f924ede3033534bd98abfbf90`, after `bded5e28821f318b52a3192be75d06a7eaa6ff61dd8c359d078604b30efe47a6`. 실행 game 사본은 삭제했고 output/manifest/prefix/log는 보존했다.
- 검증: targeted G5/inventory `11 passed`, py_compile PASS. 필수 runtime 실패로 원본 대조·`make check`·50/51·UI/group/save/load는 SKIP. 제품 G5 PASS·middle review·사용자 승인 없음.

승격 작업자가 이어서 할 일:
1. 동일 fixture/입력을 반복하지 말고 드래그 좌표 변환·camera/HUD 경계와 hit-test 중 하나를 실제 trace로 독립 귀속한다.
2. 원인이 확정되고 최소 변경 근거가 있을 때만 원본 20과 candidate 50을 같은 fresh fixture로 대조한다.
3. 선택50·명령50·51번째 제외·오염/크래시 없음 전에는 G5 PASS 또는 다음 목표 진행을 주장하지 않는다.

# lap655 승격 요청 — positive-Y fixture shift still selects 49

- 날짜/lap: 2026-09-26 / 655
- 역할: hands-on work
- 상태: BLOCKED(FAIL-B; 필수 fresh runtime selection=49/55)
- 변경: `tools/g5_candidate_drag_probe.py`의 worker-centered fixture를 `dy=-3..4`로 한 행 +Y 이동하고, `tests/test_g5_candidate_drag_probe.py`에 55 unique cell 회귀 계약을 추가했다. 후보 PE32·보호 원본·참고 저장소는 변경하지 않았다.
- 원본 SHA: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 후보 SHA: `6f6a4f859be4b2281ec2014e817b7692adf2d04226b0ac14b3ac32ac06f4e091`.
- 실행: isolated Wine/Xvfb 1600×1200, PS3 solo owner0, worker slot1198 `(42,142)`, camera `[40,140]`, synthetic type2 55 at x39..45/y139..146 excluding worker, drag `(200,170)→(730,445)`.
- 결과: fixture `55/55`; candidate selection `49`, unique `49`; movement command `49`; crash 없음·cleanup residual0·source unchanged. Probe exit2/`FAIL_SELECTION_CAP`; result SHA `777e7fd26645371a4ab4e937ed411414608aa99bf24daf35990b2b6efe13beba`; captures before `0b1cb8a2dadc2b8dc5c52f87c7aff07189abbad1f6f33feb92f363c1a217c0b9`, after `a3dfa17111942e2f9cb45c34ee6848a07180e55c8a13021993e1e3cca9c0cae9`.
- 검증: targeted `12 passed`; `make check` `905 passed in 663.64s`, ruff/compileall/mypy/context PASS; `SAFETY_PASS`; source 보호 PASS. 실행 game 사본은 위생 규칙에 따라 제거했고 output/manifest/prefix/log는 보존했다.

승격 작업자가 이어서 할 일:
1. positive-Y fixture와 같은 드래그 사각형을 재시도하지 말고, 49 경계가 hit-test/카메라 변환/건물 점유 중 어디서 생기는지 direct trace 또는 원본 20 paired 대조로 귀속한다.
2. 원인이 확인된 뒤에만 최소 코드 변경과 candidate fresh 실행을 한다. 이번 바퀴는 선택50·명령50·51번째 제외를 입증하지 못했다.
3. G5 제품 PASS·middle review·사용자 milestone 승인은 모두 보류한다.
