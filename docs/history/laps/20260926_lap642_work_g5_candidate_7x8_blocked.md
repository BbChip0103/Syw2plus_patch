# 날짜 | lap 642 | 목표 G5

- 실제 provider/model/effort / 지정 역할: Codex hands-on 구현 작업자 / native session.
- 가설 / 사용자 관찰: lap641의 36기 및 `0x80000004`가 gdb hardware trace 잔재인지 확인하기 위해 trace 없는 clean candidate와 더 좁은 7×8 fixture를 사용한다.
- 예상 PASS / FAIL 조건: 동일 original이 `PASS_ORIGINAL_CAP20`; candidate가 `count=50`, unique50, 명령50이면 다음 경계 검증으로 진행. 원본 대조 또는 candidate 필수 runtime이 실패하면 BLOCKED/승격.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): `tools/g5_candidate_drag_probe.py` fixture를 11×5에서 7×8로 변경(마지막 행 6기), 합계55/map-range guard 추가. SHA `45460b196d8e76406f1781638ea55fe2457f392503145cfadf664bc94ceb4f26`; 커밋 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: protected source `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` before/after 동일; candidate `a123498ab6378df17536718b7ec64389423fb0b7d0800a417cb3d476a1a9bc98`; isolated Wine/Xvfb 1600×1200, solo owner0, synthetic type2×55, `5000/5000`, selection storage candidate `0x0108c000`/50.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `.venv/bin/python tools/g5_candidate_drag_probe.py --variant original --runtime-root local/runtime/g5-lap642-original-7x8 --artifact-root /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260926_lap642_g5_original_7x8`; 같은 명령 `--variant candidate`와 `g5-lap642-candidate-7x8`; raw/provenance/capture는 두 artifact 디렉터리에 보존.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): original `PASS_ORIGINAL_CAP20`, count/movement20, cleanup/source PASS. candidate clean run `selection=36`, unique36, movement36, exit2 `FAIL_SELECTION_CAP`; log에 `wine: Unhandled illegal instruction at address 047A0480`; cleanup/source PASS. **BLOCKED**.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: py_compile 및 7×8 합계55 검증 PASS. 제품 G5, 50/51, 50기 명령, save/load, full `make check`, middle 독립 검수, 사용자 승인은 미완료.
- 다음 한 가지: 승격 작업자가 candidate raw/capture/bytes를 독립 대조해 36의 hit-test 범위와 illegal-instruction 시점을 귀속한 뒤, 원인 확정 후보에서만 original20→candidate50/51→command50을 fresh 실행한다.
