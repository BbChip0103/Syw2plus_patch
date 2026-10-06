# 2026-09-30 | lap 798 | G2 ESL2608 Phase-C rally target paired probe

- 실제 provider/model/effort / 지정 역할: Codex native work 세션 / 현재 모델·effort 런타임 미노출 / hands-on 구현.
- 가설 / 사용자 관찰: lap796의 `(450,300)`은 HQ 월드좌표 `(91,54)`와 겹쳐 rally writer가 유효한
  목적지를 갱신하지 못했다. 같은 live slot `0x11`→cell `(776,503)`→action `0x15` 경로에서 HQ
  동쪽 빈 지면 `(600,300)`을 쓰면 `+0x654/+0x656`가 갱신되고 원본·후보가 parity를 보일 것이다.
- 예상 PASS / FAIL 조건: HQ 선택, worker UI 생산, rally field 변화, source 불변, private game copy/prefix
  cleanup 0을 확인한다. hero는 실제 fixture에 유효한 생산 대상·counter가 있으면 별도 PASS로 기록하며,
  없으면 제품 결함으로 추측하지 않고 UNKNOWN으로 남긴다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `tools/g2_esl2608_phase_c_production_probe.py`의 `RALLY_POINT (450,300)→(600,300)` 1개 변경,
  `tests/test_g2_esl2608_phase_c_production_probe.py` 기대값 1개 변경. 도구 SHA
  `d4eb615ae0d917785b2c74495e5b7c55917ffb0519530c6bea678384bc029498`, 테스트 SHA
  `544bf51494a6caeaaeaa7ae979334bc17093d9864d344184bbdb15c278cfcc34`; 커밋 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: normal baseline
  `cade60b2451519ec4e305d91279b1c377cf797c813a939c5b54c2e9b30b176a3`, candidate
  `83c7df80a3273d95d58e7a493866bbb40ad705d10120bc05db660400961fad60`; fixed baseline
  `f5f816eeb3d8b531ff030f4b43b2f2338ccf0d2257a5684b034e1f8dc8ee1973`, candidate
  `1bdcadf9edeccc16d92696e580a60fc71f13a13b6bba22cafb8c9f50e749262f`. Wine win32, private
  Xvfb 1600x1200, ESL2608 overlay, real HQ slot1199, owner0 2-unit fixture, no synthetic units.
- 실행 명령 / 로그 / 캡처 경로 및 해시: targeted `pytest` 4 passed; `make lint` and `make typecheck`
  passed. Four fresh invocations of `tools/g2_esl2608_phase_c_production_probe.py` used
  `local/runtime/esl2608_lap798_{normal,fixed}_{baseline,candidate}` and artifacts under
  `temp/Syw2plus_patch/g2_esl2608_lap798/{normal,fixed}_{baseline,candidate}/`.
  Result SHA: normal baseline `dc60c2eedab25deae6630628f780e396b79400714b8c7a8a9334d58bc8f0d590`,
  normal candidate `d2394b1d87a970c606fe765f69750fdfad727294558677281381eaab4f7f4a07`, fixed baseline
  `595115040967925820971edefe5bf3c69ddcfcc832711f194c22b7bcc2cab06a`, fixed candidate
  `b32d8c65bd4aaf5a1aeeae0433711026be29f76452ee38b0858e8003d1869036`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): Four-way rally/worker paired behavior **PASS**:
  all four selected HQ, issued worker order, produced worker `2→3`, and changed HQ rally `(94,57)→(94,52)`;
  source unchanged, crash/timeout 0, prefix process residue 0, and private game copy removed in all four.
  Hero stage is **UNKNOWN**, not a candidate FAIL: normal baseline/candidate and fixed baseline/candidate
  had no hero order resource/reserved delta, no hero unit, and indexed counter `0→0` (nation1/3 buttons
  `(776,540)`/`(704,540)` respectively). Probe overall status is FAIL only because its legacy all-checks
  verdict includes this unresolved hero check.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: `(600,300)` is now proven distinct from the HQ
  target and the rally input contract is runtime-valid for both EXE families. No product EXE, original,
  reference repository, or protected runtime directory was modified. G2 Phase C hero fixture/counter,
  DxWnd, 24k/144k load, multiplayer, final repair builds, middle review, and user approval remain open.
- 최종 Fast: `make check` **1164 passed, 5 skipped in 729.06s**, exit 0; Ruff/compileall/mypy/
  `CONTEXT_PASS`; `checks/safety.py`=`SAFETY_PASS`; log SHA
  `11a0837a17e5b5eed73e563bd65d1a4fa581c6d854ee5d063f19a12efea86a81`.
- 다음 한 가지: middle independently re-check this lap798 raw and decide whether to issue a valid hero
  fixture/production probe or mark hero as environment/fixture-limited before the next G2 checklist item.
