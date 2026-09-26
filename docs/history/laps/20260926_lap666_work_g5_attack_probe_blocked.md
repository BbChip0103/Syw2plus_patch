# 2026-09-26 | lap 666 | 목표 G5

- 실제 provider/model/effort / 지정 역할: Codex native hands-on work / high; 중간 tier 이관 조건을 확인하기 위한 probe 구현.
- 가설 / 사용자 관찰: 기존 lap665의 빈 지면 우클릭은 이동만 증명한다. owner1 전투형 type2 적을 같은 isolated fixture에 만들고 실제 우클릭 후 선택 유닛의 공격 command와 target slot을 raw로 읽으면 G5 공격 조건을 판정할 수 있다.
- 예상 PASS / FAIL 조건: 후보 50기 모두 command=4 및 target=적 slot, 원본 paired 20기 모두 동일; fixture·cleanup·원본 SHA 불변. 그 외는 FAIL/승격.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): `tools/g5_candidate_drag_probe.py`, `tests/test_g5_candidate_drag_probe.py`; EXE patch 0, 커밋 0, source 변경 0.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 후보 `ae495fa5a1498597c265ad9bcae6444f564ade92adb311a3c413c4fb9996b5b7`; private Wine/Xvfb 1600×1200, PS3 solo owner0, synthetic owner0 type2 55기 + owner1 type2 적 1기.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `python tools/g5_candidate_drag_probe.py --variant candidate --attack-probe`를 fresh 격리 runtime에서 4회 실행. 최신 JSON `temp/Syw2plus_patch/20260926_lap666d_g5_attack_candidate/probe-result.json` SHA `9cb26ba9…8adbcc`; 최신 `after-fixture.png` SHA `ba05b02c…4130f7`, `before-attack.png` SHA `f99d1fe2…4e28f`, `after-attack.png` SHA `cec7a249…503833`. 각 실행 cleanup=true, source_unchanged=true.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): probe/회귀 `4 passed`, ruff/compileall PASS. 후보 선택은 50/50이었으나 4회 모두 공격 `attack_command_count=0`, `target_match_count=0`, `pass=false`; 우클릭 결과는 `command=3`, `target=0`(이동/비표적). 첫 실행은 이 실패를 잘못 `PASS_UI_ROUNDTRIP`으로 라벨링했으나 fail-closed 판정으로 수리했다. 공격 필수 게이트 FAIL-B; 원본 paired 및 제품 G5 승격은 실행하지 않았다. 후행 `make check`: `917 passed in 709.85s`, Ruff/compileall/mypy/CONTEXT PASS; `bash checks/safety.sh check`: `SAFETY_PASS`.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 후보 패치 SHA는 4회 동일하고 게임 EXE 변경 없음. 적 fixture는 생성됐지만 화면 입력 좌표/게임 공격 hit-test 또는 공격 opcode·target 필드 귀속이 미해결이다. G5 2단 `HOLD`, 멀티 동기화 UNKNOWN, 사용자 승인 없음.
- 다음 한 가지: 승격 작업자가 먼저 원본에 동일 입력을 fresh 실행해 `command=3,target=0`이 재현되는지 확인하고, 그 뒤 최신 캡처/raw로 적 sprite hit-test 좌표 및 실제 공격 opcode/target 필드를 독립 귀속한다. 귀속 후 한 곳만 수정하고 candidate50 대 original20 paired probe를 fresh 실행한다.
