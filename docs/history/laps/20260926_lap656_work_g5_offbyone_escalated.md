# 날짜 | lap 656 | 목표 G5

- 날짜/lap/목표: 2026-09-26 / 656 / 드래그 1회 선택 상한 20→50.
- 실제 provider/model/지정 역할: Codex native session / hands-on work / high.
- 가설: lap655의 반복 선택 `49/55`가 `0x0043877A`의 50 상한 off-by-one인지 정적으로 판정한다.
- 이전 필수 runtime 근거: 후보 SHA `6f6a4f859be4b2281ec2014e817b7692adf2d04226b0ac14b3ac32ac06f4e091`, isolated Wine/Xvfb 1600×1200, PS3 solo owner0, unique synthetic type2 55기, 선택49·명령49·crash 없음. 실행 artifact는 lap655 history에 보존했다.
- 독립 판정: 보호 원본 `0x0043877A`는 `mov ax,[ebp] → cmp ax,0x14 → jge reject → append → inc [ebp]`이다. 후보의 `0x32`는 `count >= 50`만 거부하므로 count 0..49에서 append를 허용한다. 따라서 현재 49 결과만으로 이 비교의 off-by-one은 입증되지 않는다. `FUN_004386E0`의 유효성/좌표 필터 또는 호출 전 필터가 남은 원인 후보이며, 직접 runtime trace 없이는 구현 근거가 불명확하다.
- 변경파일: 제품 코드/EXE/원본/참고 저장소/테스트 fixture 변경 없음. `docs/history/laps/20260926_lap656_work_g5_offbyone_escalated.md`, `docs/STATUS.md`, `loop/ESCALATE_SOL` 기록만 갱신.
- 원본/후보 SHA: 보호 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변; 재계산 후보 SHA `6f6a4f859be4b2281ec2014e817b7692adf2d04226b0ac14b3ac32ac06f4e091`.
- 실행/검증 명령: `.venv/bin/python -m pytest -q patches/selection/test_g5_selection_cap50_v1.py tests/test_g5_candidate_drag_probe.py tests/test_g5_selection_inventory.py`; `make check`; `bash checks/safety.sh check`.
- 결과: targeted `12 passed`; `make check` `905 passed in 792.26s`; ruff/compileall/mypy/context PASS; `SAFETY_PASS`. 제품 필수 runtime은 lap655에서 FAIL-B였고, 동일 fixture/입력 맹목 재시도는 하지 않아 이번 lap에서는 SKIP.
- fixture/수치: lap655 worker slot1198 `(42,142)`, camera `[40,140]`, fixture x39..45/y139..146에서 worker cell 제외, drag `(200,170)→(730,445)`, fixture receipt55/55, selected slots1148..1195+1198, omitted1141..1147, command49.
- 판정: **BLOCKED(FAIL-B; static off-by-one hypothesis not sufficient)**. G5 제품 PASS·middle 독립 검수·사용자 승인은 없음.
- 다음 행동: 승격 작업자가 동일 fixture를 재실행하지 말고 `FUN_004386E0` 진입/반환과 `0x004384B0` 호출 전 필터를 fresh original20/candidate50 paired trace로 비교해 첫 7개 제외의 직접 원인을 귀속한다. 원인 확인 전 최소 패치·fresh candidate 실행·G5 PASS를 금지한다.
