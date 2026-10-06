# 2026-09-30 | lap 792 | 목표 G2 ESL2608 Phase C

- 실제 provider/model/effort / 지정 역할: Codex native main session(런타임에 정확한 모델 ID·effort 미노출) / hands-on work.
- 가설 / 사용자 관찰: Phase-B 다음으로 두 lane·두 variant에서 실제 UI 생산→집결지 지정→장수 포함 경로를 비교한다. 제품 EXE와 원본은 읽기 전용이고 각 실행은 private Wine/game/prefix/Xvfb를 사용한다.
- 예상 PASS / FAIL 조건: HQ UI 선택, worker 생산 및 count/slot 증가, UI 집결지 입력 뒤 HQ `+0x654/+0x656` 변화와 생산물 cmd3/도착, 장수 type/count 변화, source unchanged·cleanup PASS.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): `tools/g2_esl2608_phase_c_production_probe.py`, `tests/test_g2_esl2608_phase_c_production_probe.py`; 제품 EXE·원본·`../260921_temp` 변경 없음; uncommitted.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: normal baseline `cade60b2451519ec4e305d91279b1c377cf797c813a939c5b54c2e9b30b176a3`, derived candidate `83c7df80a3273d95d58e7a493866bbb40ad705d10120bc05db660400961fad60`; fixed/candidate는 source contract만 검증하고 UI blocker에서 실행 보류. fresh 1600×1200 Wine/Xvfb, ESL2608 Data overlay, 새 게임 owner0 2 units/HQ UI production, synthetic spawn 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `python3 tools/g2_esl2608_phase_c_production_probe.py --lane normal --variant baseline ...`; raw는 `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/g2_esl2608_lap792/normal_baseline*/probe-result.json`. 네 baseline iterations raw SHA는 `a8acdf47…`, `e21815a4…`, `a6b75fa3…`, `9f713f04…`; 모두 source unchanged/game removed/prefix 0.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): worker UI 생산은 fresh 4회 모두 count `2→3`, owner0 신규 type7/cmd3, 자원·reserved 변화까지 관측. R 후보 `(704,503)`과 지도 좌표 `(560,330)`, `(450,300)`은 선택을 해제했지만 HQ rally `+0x654/+0x656`는 변화하지 않아 UI 집결 계약 **BLOCKED(harness)**. 영웅 수 `+0x980`은 새 게임 `0→0`; 후보 `(738,540)`, `(776,540)`도 장수 type/count 변화를 만들지 않아 **UNKNOWN**, 제품 결함으로 승격하지 않음. Phase C 네 조합 paired는 미완료.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: first run의 기존 HQ/worker 오분류를 owner0 전체 snapshot으로 수정했고, 집결 raw 필드와 생산 완료 대기를 추가했다. targeted pytest `2 passed`, compileall PASS. G2 Phase A/B의 기존 4-way PASS와 제품 후보 SHA는 유지하되 Phase C·배포·승인으로 승격하지 않는다. 승격 작업자 검증을 위해 `loop/ESCALATE_SOL` 생성.
- 다음 한 가지: 원본 fresh UI에서 실제 집결지 버튼/단축키·유효 target과 장수 생산 fixture를 독립 확정한 뒤 네 조합 Phase C paired 재실행.

- **운영자 정정(2026-09-30, lap793 승격 처리):** "fresh 4회 모두 worker `2→3`"은 부정확했다. 첫 raw `a8acdf47…9bf71`은 하네스 사전수리(시작 시 존재 HQ/일꾼을 신규 생산물로 오분류, 집결 필드 미판독) 이전 실행으로 `count 2→2`·구형 rally 판정이며 **판정에서 제외**한다. 유효 raw는 수리 후 3회이며 worker `2→3`, rally 필드 불변, hero `0→0`이다. 현 probe는 마지막 raw 이후 수정됐으므로 다음 work가 현 스키마로 fresh 재실행한다.
