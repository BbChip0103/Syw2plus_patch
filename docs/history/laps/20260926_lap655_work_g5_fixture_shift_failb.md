# 날짜 | lap 655 | 목표 G5

- 날짜/lap/목표: 2026-09-26 / 655 / 드래그 1회 선택 상한 20→50.
- 실제 provider/model/지정 역할: Codex native session / hands-on work / high.
- 가설 / 사용자 관찰: lap654에서 `(200,170)→(730,445)`로 사각형을 넓혀도 y=45 행 7기가 빠졌다. 건물 footprint 겹침 가설을 검증하기 위해 worker `(x=42,y=142)` 중심 fixture를 `dy=-4..3`에서 `dy=-3..4`로 한 행 +Y 이동한다.
- 예상 PASS / FAIL 조건: candidate fixture55, selection50, unique50, 이동 명령50, crash/오염 없음이면 PASS; fresh runtime이 50 미만이면 FAIL-B/승격.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): `tools/g5_candidate_drag_probe.py` fixture range 변경 SHA `39ea60ac2da6e4a9d802e37a89c48065d118e8eeb71ba09430aae4ade25ada29`; `tests/test_g5_candidate_drag_probe.py` 회귀 계약 추가 SHA `ab18449c12719359edc617965ade9fa8b5b7a2da5dd41bdf399872dd04ee52d1`; 제품 바이너리·원본·참고 저장소·커밋 0.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; candidate `6f6a4f859be4b2281ec2014e817b7692adf2d04226b0ac14b3ac32ac06f4e091`; isolated Wine/Xvfb 1600×1200, PS3 solo owner0, worker slot1198 type7 `(42,142)`, synthetic type2 55 unique cells x39..45/y139..146 excluding worker cell.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `PYTHONPATH=. .venv/bin/python tools/g5_candidate_drag_probe.py --variant candidate --runtime-root local/runtime/g5-lap655-candidate-fixture-shift --artifact-root /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260926_lap655_g5_candidate_fixture_shift`; artifact `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260926_lap655_g5_candidate_fixture_shift/`; result `777e7fd26645371a4ab4e937ed411414608aa99bf24daf35990b2b6efe13beba`; before `0b1cb8a2dadc2b8dc5c52f87c7aff07189abbad1f6f33feb92f363c1a217c0b9`; after `a3dfa17111942e2f9cb45c34ee6848a07180e55c8a13021993e1e3cca9c0cae9`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): fixture receipt/fixture_units `55/55`; camera `[40,140]`; selection `49`, unique `49`; selected worker slot1198 plus fixture slots1148..1195, omitted fixture slots1141..1147; 이동 명령 `49`; crash 없음; cleanup residual `0`; source unchanged `true`; probe exit `2`, `FAIL_SELECTION_CAP`. Candidate 필수 fresh 실패로 원본 paired run·50/51·UI/group/save/load는 SKIP.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: fixture targeted test 및 G5/inventory `12 passed`; `make check` `905 passed in 663.64s`, ruff/compileall/mypy/context PASS; `bash checks/safety.sh check` PASS. G5 제품 PASS·middle 독립 검수·사용자 승인 없음. positive-Y 한 행 이동과 확대 사각형에도 같은 49 경계가 재현되어 건물 footprint 단독 가설은 입증되지 않았다. 실행 game 사본은 trash로 제거하고 output/manifest/prefix/log/captures는 보존했다.
- 다음 한 가지: 승격 작업자는 동일 fixture/range/사각형을 반복하지 말고, fixture slots1141..1147이 실제로 hit-test/카메라 변환/건물 점유 중 어디서 제외되는지 direct trace 또는 paired original 20 대조로 특정한 뒤 최소 변경을 정한다.

판정: **`BLOCKED(FAIL-B: positive-Y fixture shift still selects 49/55)`**.
