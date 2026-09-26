# 2026-09-26 | lap 651 | 목표 G5

- 날짜/lap/목표: 2026-09-26 / 651 / 드래그 1회 선택 상한 20→50.
- 역할/provider: hands-on work, Codex native session, high. 지정 역할을 넘는 방향 변경은 하지 않음.
- 가설: lap650의 귀속대로 FUN_0041DC40의 `0x230` frame과 10-dword clear가 50-entry word buffer를 침범하므로 `0x270` frame과 25-dword clear로 수리하면 50 선택까지 도달한다.
- 변경파일: `patches/selection/g5_selection_cap50_v1.py`, `patches/selection/test_g5_selection_cap50_v1.py`, `tools/g5_candidate_drag_probe.py`, `docs/STATUS.md`, `loop/ESCALATE_SOL`.
- 원본/후보 SHA: 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 후보 `6f6a4f859be4b2281ec2014e817b7692adf2d04226b0ac14b3ac32ac06f4e091`. 원본 보호본·참고본·로컬 입력 SHA 동일.
- 패치 범위: `0x0041DC40` sub, `0x0041E1EC`/`0x0041E20A` add를 `0x270`으로 변경; `0x0041DC4C` clear `b9 0a...`→`b9 19...`; candidate expected SHA 갱신. 원본/참고 저장소·커밋 0.
- 실행명령: `PYTHONPATH=. .venv/bin/python tools/g5_candidate_drag_probe.py --variant candidate --runtime-root local/runtime/g5-lap651-candidate-frame270 --artifact-root /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260926_lap651_g5_candidate_frame270`.
- 환경/fixture: 격리 Wine prefix와 Xvfb `1600x1200x24`; solo owner0, PS3; stock-layout diagnostic op5 engine-seeded synthetic type2 55기, 7×8 dense rows, anchor slot1198, 실제 입력 드래그 `(120,120)→(760,540)` 후 우클릭 `(760,540)`, tick 3→15.
- 결과: fixture 55기 생성 PASS; crash/예외 없이 실행 종료, cleanup `ok=true`, source unchanged `true`; 선택 `42`/unique `42`, 이동 명령 nonzero `42`. probe status `FAIL_SELECTION_CAP` (FAIL-B). 캡처 before `2dbbc3ec640c4847c70b39f64c5e390811d91747d508444a5ef4b2b2b8b3a43a`, after `4eeea9c54e9d76cc1ec0edd947dbb422decfda923c268cf120a7718dc3ea95c2`.
- 실행 산출물: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260926_lap651_g5_candidate_frame270/`; `probe-result.json` SHA `50f635ef0abece4710611ff322b6be34f092c8df8ceab1f5a6ed590cb0baf4aa`, `candidate-provenance.json` SHA `38893087b680cbda72bed995c1ee4bdeaef85ebdd011c96c23da86d3275b9307`, `probe.log` SHA `444bb425fd89e5c627ee783a44aa62744ee997dd6ae14e04106482cd7f1531b9`.
- 검사: targeted G5/inventory `11 passed`; `make check` `904 passed in 650.05s`, ruff PASS, compileall PASS, mypy PASS, context PASS; `bash checks/safety.sh check` PASS. 50/51·canary/save/load SKIP. 게임 `local/runtime/.../game` 사본은 회차 종료 위생 규칙에 따라 삭제하고 output/prefix/로그는 보존.
- 판정/다음행동: `FAIL-B`, 제품 G5 PASS 아님. 같은 frame을 재시도하지 말고 승격 작업자가 `FUN_004AE550` 명령 패커 및 남은 UI/표시 20 전제를 원본 old bytes·호출 계약으로 좁힌 뒤, 최소 수정 후 fresh 실행한다. `loop/ESCALATE_SOL` 생성.
