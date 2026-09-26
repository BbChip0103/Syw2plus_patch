# 2026-09-26 | lap 652 | 목표 G5

- 날짜/lap/목표: 2026-09-26 / 652 / 드래그 1회 선택 상한 20→50.
- 역할/provider: hands-on work, Codex native session, high.
- 가설: lap651의 42/55는 fixture가 화면 하단 UI에 가려진 결과이므로, 작업자 y보다 20 map cells 위에 55기(7×8) fixture를 놓으면 전부 화면에 들어온다.
- 예상 PASS/FAIL: 후보 crash 없음, selection unique=50, 이동 명령=50, 51번째 제외.
- 변경파일: `tools/g5_candidate_drag_probe.py`; fixture `start_y = worker.y - 20`. 후보 패치/원본 EXE/참고 저장소는 변경하지 않았다.
- 원본/후보 SHA: 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 후보 `6f6a4f859be4b2281ec2014e817b7692adf2d04226b0ac14b3ac32ac06f4e091`.
- 실행환경/fixture: private full copy, fresh Wine prefix, Xvfb 1600×1200; solo owner0, type2 synthetic 55, 7×8 dense rows, same minimap click/drag `(120,120)→(760,540)`/right-click.
- 실행명령: `PYTHONPATH=. .venv/bin/python tools/g5_candidate_drag_probe.py --variant candidate --runtime-root local/runtime/g5-lap652-candidate-fixture-upper --artifact-root /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260926_lap652_g5_candidate_fixture_upper`.
- 측정값: 실제 worker `(21,92)`, camera `(19,90)`, fixture requests x=25 y=72..79, receipts 55/55; selection `1/55`, unique `1`, movement command `1`; crash 없음; probe exit 2 = `FAIL_SELECTION_CAP`.
- 증거: artifact root 위, `probe-result.json` SHA `fc5b859db25f91a18ecfd708d80daf4482114e3eab403d2844b68505f6811a4f`; before PNG `422e6a094dd0ae803105dd3dde4049dcddc2b8a464fecc0dca4494d46e6387a5`; after PNG `79b24f23161779afa4635c7d73c8fd7ba89241ad0c3cb85a8ff4b866214484ed`; source after SHA equals original.
- 검증: `make doctor` PASS; py_compile 및 fixture 총량 정적 확인 PASS; targeted pytest/`make check`는 fresh runtime 측정 실패 후 중단(SKIP). 실행 game 사본은 삭제했고 output/manifest/prefix/log는 보존.
- 판정: `BLOCKED`/`FAIL-B`; y-20 계산은 현재 camera에 비해 fixture를 화면 밖에 배치했다. 같은 변경 재시도 금지.
- 다음 한 가지: 승격 작업자가 minimap 이후 camera를 기준으로 화면 y=120~430에 들어오는 map 좌표를 정하고, 그 계산을 독립 검수한 뒤 fresh candidate를 실행한다.
