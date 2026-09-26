# 2026-09-11 | lap 150 | 목표 G1

- 날짜/lap/목표: 2026-09-11 KST / 150 / G1 1600×1200 입력 계약
- 가설: config-only 2× presentation에서 하네스가 논리좌표 `(184,560)`를 물리좌표로 선변환하지 않고 그대로 보내면 PS9→PS7이 통과한다.
- 변경파일: `tools/runtime_env.py`, `tools/check_g1_presentation_trace.py`, `tests/test_runtime_env.py`, `tests/test_g1_presentation_trace.py`, `loop/ESCALATE_SOL`
- 원본·후보 SHA: 보호 원본 기대 SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 변경 source SHA는 `loop/ESCALATE_SOL`에 기록. config/EXE/DLL 후보 적용 없음.
- 실행명령: targeted pytest; `make check`; `bash checks/safety.sh check`; fresh helper build; fresh bridge build; `runtime_env.py prepare --source /home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus_re --bridge /tmp/syw2plus_lap150.uf0IeV/bridge/_inmm.dll --timeout 60`.
- 수치: targeted `80 passed`; Fast `179 passed`, Ruff/compileall/mypy/context/safety PASS; helper/bridge RC0; prepare RC2. 새 game copy/prefix/display, 활성 인원/지도/군대/fixture 및 runtime 입력은 N/A — prepare 이전 중단.
- PASS·FAIL·SKIP: 논리 surface/client 계약 구현 및 Fast PASS; fresh prepare **FAIL/BLOCKED**; G1 runtime PS9→PS7/PS3, capture, final summary, validator, cleanup **SKIP**.
- fixture: 게임 fixture 미생성. source read-only 확인 결과 원본은 `/home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus_re/Syw2plus/syw2plus_original.exe`에 있으며 지정 root에는 없다.
- 다음행동: `loop/ESCALATE_SOL`대로 중간 tier가 `prepare` source-root 계약을 판정·명시한 뒤에만 새 격리 runtime 1회를 승인한다. 이번 lap에서 source 경로를 바꾸어 재시도하지 않는다.
