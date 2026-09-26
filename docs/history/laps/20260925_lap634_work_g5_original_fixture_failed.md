# 2026-09-25 | lap 634 | G5

- 실제 provider/model/effort / 지정 역할: Codex native session / hands-on work / high.
- 목표 / 가설: lap632 r6의 selection count=1은 fixture visibility 문제일 수 있으므로, 같은 type46×55 engine-seeded fixture를 원본에서 먼저 드래그하면 stock cap20이 관측되고 후보와 비교할 수 있다.
- 예상 PASS / FAIL: 원본 count=20·unique=20, 이후 후보 count=50·unique=50·51번째 미선택·50기 명령 raw. 원본 선행 대조 실패 시 후보 실행 중단.
- 변경 파일 / source fingerprint / 커밋: `tools/g5_candidate_drag_probe.py`에 `--variant original|candidate`, stock/candidate selection reader와 결과 provenance 추가. probe SHA `983a0e675fa0bd4598e030fe2b65e292797ffddef60321be163c5cd1edf7596b`; 제품 EXE/패치/원본/참고 저장소/커밋 0.
- 원본 / 환경 / fixture: protected source `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; fresh private Wine/Xvfb 1600×1200; original variant; owner0/type46/count55, request `(50,50)`, synthetic stock-layout op5 fixture.
- 실행 명령: `.venv/bin/python tools/g5_candidate_drag_probe.py --variant original --runtime-root local/runtime/g5-lap634-original --artifact-root /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260925_lap634_g5_original_drag`.
- 사전/실행 검증: `make doctor` exit0/원본 verified·Wine/Xvfb present; prepare/check PASS; PS3 tick2; fixture receipt `fixture_added=55`, used `1120/1500`, live57; source SHA after unchanged; cleanup residual0/ok=true. Targeted G5 patch tests `8 passed`, probe py_compile PASS.
- 결과: `probe-result.json` status `FAIL_ORIGINAL_SELECTION`; stock base `0x899024`, capacity20, selection before0→after1, raw `0x204ae`, slot1198, unique1; camera after minimap `[19,90]`; move command raw nonzero1. Captures and full provenance are in `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260925_lap634_g5_original_drag/`.
- 판정 / 미검증: `BLOCKED(original_fixture_or_camera_contract)`. 원본 count20 대조가 실패했으므로 후보 count50/51, 50기 명령, save/load와 fresh `make check`는 SKIP. 이 runtime 실패는 G5 제품 실패나 후보 상한 결함으로 귀속하지 않는다.
- 다음 행동 / 승격: 다음 작업자는 raw/capture와 입력으로 camera 이동·화면 내 living-unit 좌표를 독립 검수하고, 원본이 count20이 되는 fixture/camera/drag 계약을 확정한 뒤에만 후보를 재실행한다. `loop/ESCALATE_SOL` §182.
