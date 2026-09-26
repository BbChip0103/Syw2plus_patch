# 2026-09-12 | lap 222 | 목표 G1 Stage B — R6-B 선택 응답 술어

- 실제 provider/model/effort / 지정 역할: Codex hands-on implementation work tier / high.
- 가설 / 사용자 관찰: `drag_select`의 `count>=2`는 band-select 대상에 대한 근거 없는 절대
  가정이다. 입력 전후 count 또는 선택 identity가 변하면 엔진 응답으로 관측하고, 둘 다 같으면
  계속 무반응 FAIL/timeout으로 닫아야 한다.
- 예상 PASS / FAIL 조건: count 변화 또는 `(selected_slot, selected_type)` 변화는 PASS,
  두 값 모두 불변은 FAIL/timeout, 절대 `count>=2` 게이트는 실행 경로에 없어야 한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `tools/runtime_env.py` sha256
  `9e607407b10b593710406b4beb250386640c118e4655a5de46a7a1954d8c5e80`,
  `tests/test_runtime_env.py` sha256
  `12f1a2f31ad3437e5234bef9912883781ddb4275f6999a3ef47c21e75a5befc4`.
  R6-B는 `_g1_selection_responded` 추가와 drag wait/final gate 변경이다. 커밋 없음
  (`LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 게임 실행 0회,
  원본/후보 EXE·DLL/assets/baseline/golden/evidence 0회 변경, Wine/Xvfb/PNG 미사용.
  회귀 fixture는 격리된 synthetic selection mapping이며 `count=1`, identity
  `1199/70→1198/21`로 실제 lap204 관측 형태를 재현한다. G1 실제 활성 인원/지도/군대 측정은
  수행하지 않았다.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `.venv/bin/python -m pytest -q tests/test_runtime_env.py -k 'g1_selection_response or
  g1_selection_sequence or g1_input_verdict'` → 6 passed.
  첫 `make check` → 238 passed / 1 failed: 최종 `drag_pass` 대입부에 잔여 `count>=2`가
  있어 `test_g1_shared_input_sequence_blocks_production_but_reaches_later_stages` 실패.
  수리 후 `make check` → 239 passed, Ruff/compileall/mypy 10 files, `CONTEXT_PASS`.
  `LOOP_DRY_RUN=0 bash checks/safety.sh check` → `SAFETY_PASS`.
  `rg` 실행 경로 검사에서 `count>=2`는 0건(회귀 assertion 문자열 제외).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): targeted/final Fast/safety = PASS. 첫 필수
  Fast gate = FAIL 후 bounded repair로 재통과했으나, 사용자 세션 계약상 필수 gate 실패 이력을
  숨기지 않고 **ESCALATE**한다. R6-B work gate 및 middle 독립 검수는 미완료다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: `count 1→1` identity 변화가 응답으로
  진행되고 동일 상태는 응답하지 않는 단위 계약을 고정했다. 절대 slot correspondence,
  S1 장면 통제, G1-F2-R1/R2, F3-R1/R2, WM_CLOSE, G2~G4는 미해결이다. 후보 Stage B와 원본
  재실행은 금지하며 사용자 제품/마일스톤 승인은 없다. 다음 middle이 독립 probe와 최종 gate를
  검수해야 한다.
- 다음 한 가지: 새 middle 세션이 R6-B 변경·첫 gate 실패·수리 후 최종 수치를 독립 검수하고,
  승인 전에는 G1-F2-R1 또는 게임 실행으로 진행하지 않는다.
