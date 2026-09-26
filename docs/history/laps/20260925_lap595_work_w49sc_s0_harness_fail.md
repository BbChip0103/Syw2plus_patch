# 2026-09-25 | lap 595 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Codex native / hands-on work. 계획·컨펌·제품 구현은 하지 않았다.
- 가설 / 사용자 관찰: W49SC D1 S0가 실제 UI에서 활성8명·지도 선택 조작을 찾고, 그 뒤에만 화면 1회를 시작할 수 있는지 확인한다.
- 예상 PASS / FAIL 조건: D9 통과 후 S0가 시작 버튼 없이 조작별 전후 receipt를 남기면 D2로 진행; 필수 실행 하네스가 예상 밖 종료하면 재실행하지 않고 승격한다.
- 변경 파일 / source fingerprint / 커밋: 공유 temp 새 runner `.../20260925_lap595_w49sc_corrected_lobby_once/w49sc_run.py`와 파생 bridge만 생성했다. 현재 runner SHA `ccc9fa0aebbadbb44200112eb75f9a30c2397f5a52e35f88d6ff79847b540a98`; 제품 source·원본·기존 runner/raw·커밋 변경0.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, 결합 후보 `dfdc91adb88a732d96dff96f78648f03406003bffce1b22a7e5836317f963883`, 격리 Wine32/Xvfb `:6560`, 게임 전 로비라 활성·지도·군대 fixture 미성립.
- 실행 명령 / 로그 / 캡처 경로 및 해시: D9 criterion 2회 canonical `8bf9c5ae…5071`, `py_compile`, `SAFETY_PASS`, 부모 runner SHA `82d08bd1…5357d0` 확인 후 `python3 .../w49sc_run.py --s0`를 foreground 1회 실행. 로비 PNG `temp/.../captures/20260925_095009_lap595_w49sc_lobby_before.png` SHA `2e694f10…5b17`; summary `.../run_summary.json` SHA는 실행 당시 보존.
- 측정값 / 판정: PS9→PS7→PS5 로비까지 도달했으나 첫 S0 후보 조작에서 `TypeError: click() takes 4 positional arguments but 5 were given`로 `RUN_ERROR`; 시작 버튼 0회, `captures=[]`, `samples/events=0B`. 원본 전후 SHA 동일, 현재 `:6560` lock 및 기록 PID 잔류 없음. **필수 실행 하네스 예상 밖 실패 → STOP/승격.**
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 실제 UI 조작·활성8·100×100·H-path·G2 PASS는 미검증이다. 우클릭 지원을 `x11_mouse_click.py --button`으로 고친 현재 runner는 실행되지 않았으므로, 승격 작업자가 D9와 S0 receipt/cleanup 계약을 독립 검수해야 한다. 사용자 승인·마일스톤 전환 없음.
- 다음 한 가지: `loop/ESCALATE_SOL` §145의 승격 작업자가 현재 runner의 click 계약 수정과 D7 summary 순서를 검수하고, 재실행 허용 여부를 판정한다. 이 세션은 재실행하지 않는다.
