# 날짜 | lap 654 | 목표 G5

- 날짜/lap/목표: 2026-09-26 / 654 / 드래그 1회 선택 상한 20→50.
- 실제 provider/model/지정 역할: Codex native session / hands-on work / high.
- 가설 / 사용자 관찰: lap653의 49 선택은 y=45 행이 드래그 시작 경계 밖에 있을 수 있으므로, 동일 worker-centered 55기 fixture를 유지하고 HUD 위까지 드래그 사각형을 `(200,170)→(730,445)`로 넓힌다.
- 예상 PASS / FAIL 조건: candidate selection=50, unique=50, 이동 명령=50, 51번째 제외, crash/오염 없음이면 PASS; 필수 fresh runtime이 50에 못 미치면 FAIL-B/승격.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): `tools/g5_candidate_drag_probe.py`; SHA `654d5f2b98f99e89b2392f32e770a32db6ee8a1da1c5c3ae67cd6c9e031c1dff`; `DRAG_START=(200,170)`, `DRAG_END=(730,445)`를 후보/원본 공통 입력으로 사용; 제품 바이너리·원본·참고 저장소·커밋 0.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; candidate `6f6a4f859be4b2281ec2014e817b7692adf2d04226b0ac14b3ac32ac06f4e091`; isolated Wine/Xvfb 1600×1200, PS3 solo owner0, worker slot1198 type7 `(142,42)`, camera `[140,40]`, synthetic type2 55 unique cells x139..145/y38..45 excluding worker cell.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `PYTHONPATH=. .venv/bin/python tools/g5_candidate_drag_probe.py --variant candidate --runtime-root local/runtime/g5-lap654-candidate-drag-rect --artifact-root /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260926_lap654_g5_candidate_drag_rect`; artifact `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260926_lap654_g5_candidate_drag_rect/`; result SHA `3d316b0deee46adda81030e0d2ab6589dfda53b7d2c53a049383121f0107fb02`; before `b6f1279b46f89e46694a66082997b28abc107d8f924ede3033534bd98abfbf90`; after `bded5e28821f318b52a3192be75d06a7eaa6ff61dd8c359d078604b30efe47a6`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): fixture units `55`; selection `49`, unique `49`; selected slots `1148..1198`; omitted `1141..1147` (y=45); movement command nonzero `49`; crash 없음; cleanup residual `0`; source unchanged `true`; probe exit `2`, `FAIL_SELECTION_CAP`; candidate 필수 실패로 원본 대조·50/51·UI/group/save/load는 SKIP.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: targeted G5/inventory `11 passed`; py_compile PASS; source 보호 PASS. `make check` 및 middle independent review는 fresh runtime FAIL-B 뒤 중단. G5 제품 PASS·사용자 milestone approval 없음. 확장 사각형에도 같은 7기가 빠져 단순 상단 경계 가설은 미확정이며, 좌표 변환/camera/HUD와 hit-test 중 원인은 독립 trace가 필요하다. 실행 game 사본은 삭제하고 manifest/output/prefix/log는 보존했다.
- 다음 한 가지: 승격 작업자가 동일 fixture/입력을 반복하지 말고 실제 드래그 좌표 변환 또는 hit-test 경로를 독립 trace해 y=45 7기 제외 원인을 특정한 뒤, 그 근거로 원본 20·candidate 50 fresh 대조를 수행한다.

판정: **`BLOCKED(FAIL-B: expanded drag rectangle still selects 49/55)`**.
