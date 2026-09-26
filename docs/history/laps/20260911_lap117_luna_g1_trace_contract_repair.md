# 2026-09-11 | lap 117 | G1 trace contract repair

- 실제 provider/model/effort / 지정 역할: Codex 실무 작업자 Luna/high 지정. lap116 Sol의
  `docs/plans/20260911_lap116_g1_trace_contract_repair_card.md` 허용 범위만 구현했으며, 상위 방향·
  중간 컨펌·게임 구현은 수행하지 않았다.
- 가설 / 사용자 관찰: 재사용 DirectDraw surface는 기존 clone vtable과 object identity가 유지될
  때만 Surface7 method count 49를 기록해야 하며, trace validator는 owned game window의 정상 종료와
  bridge가 직접 쓴 정확히 하나의 final summary를 관측한 뒤에만 호출되어야 한다.
- 예상 PASS / FAIL 조건: stale pointer/vtable은 fail-closed trace로 남고, summary가 없으면 raw를
  보존한 BLOCKED가 되며, clean close+summary 뒤의 trace만 복사·검증한다. validator 상수, 좌표,
  fixture, 원본 EXE/DLL/game data는 변경하지 않는다.
- 변경 파일 / source fingerprint / 커밋: 시작 SHA는
  `tools/inmm_stub/direct_draw_trace.c=906562e03c83c52f73003a8fd58c06a8ad7981a9e72a2e64729937eef53b077a`,
  `tools/runtime_env.py=48b8aeee07ae02a96f1211ffc29f9a93f461f4afceac5b13f584cb568ccf62b9`,
  `tests/test_direct_draw_abi.py=b921479c2b975654efdfca6c3370f97538964ccb16d7ce3d6dbd9f3e910011ca`,
  `tests/test_runtime_env.py=37ee237f32b107580bdf61b22415bd96143a9a5b5377d421a1bb6ac15d6d7e3f`였다.
  최종 SHA는 `direct_draw_trace.c=2b0bd730da5199f86b9efe1097cdee5aa57ccc2ceef47272db786c04dc8a147c`,
  `runtime_env.py=85e9b1af6978c6a860f1b12cc98fb8520e7765a13c17d3f8a35b79b44773f7f0`,
  `test_direct_draw_abi.py=2b2a49449e2d472defe66c20733d7d8dae708529340ebde6397fc5fb27812c1e`,
  `test_runtime_env.py=5a579685f234ef9f16f920028e141a5743d7bda36dbe8f7d5a4ab48206af68db`이다.
  `tests/test_g1_presentation_trace.py`와 validator는 변경하지 않았다. 커밋·push 없음
  (`LOOP_ALLOW_COMMITS=0`); 변경은 uncommitted로 보존했다.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 SHA는
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, PE32 보호는 PASS다.
  제품 후보·게임 실행은 없다. 저장소 밖 fresh diagnostic bridge build만 수행했으며
  `/tmp/syw2_g1_lap117_bridge.U60uCl/bridge/_inmm.dll` SHA는
  `ba31616010f3381da6d10f57f6507458a434cfd62b2aedb728eeb512eeb38e37`이다. fixture는 native
  compile/build와 synthetic unit tests뿐이며 활성 플레이어·지도·군대는 N/A, 실제 runtime은 SKIP다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: 시작 fingerprint/기존 targeted baseline 확인 후
  `pytest -q tests/test_direct_draw_abi.py tests/test_g1_presentation_trace.py tests/test_runtime_env.py`
  (최종 **69 passed**), 저장소 밖 `.venv/bin/python patches/population/build_runtime_bridge.py
  --out-dir /tmp/syw2_g1_lap117_bridge.U60uCl/bridge`, `make doctor`, `make check`,
  `bash checks/safety.sh check`를 실행했다. 최종 `make check`는 **156 passed**, Ruff/
  compileall/mypy/context 모두 PASS, safety는 `SAFETY_PASS`, doctor top은 `ok=true`·original
  `verified`였다. 게임 run·PNG·runtime manifest는 만들지 않았다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): `surface_record_reusable`가 installed 상태,
  object pointer, clone vtable identity와 wrapped methods를 모두 확인한 뒤에만 49를 기록한다.
  mismatch/capacity/stale record는 `install_status=failed`와 summary failed 경로로 남긴다.
  runner는 observed owned window에 `xdotool windowclose`를 요청하고 process exit+정확히 하나의
  final summary를 bounded wait한 뒤 trace copy/validator를 수행하며, summary 부재 시 raw를
  보존하고 BLOCKED다. 변경 및 기계 검증은 **PASS**; 실제 게임 trace, G1 2배 출력/입력, G1/M1은
  **SKIP/BLOCKED**다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 재사용 surface identity/clone mismatch,
  owned-window close 순서, summary 부재 raw 보존을 회귀로 고정했다. 원본/후보 게임·EXE/DLL 보호,
  전역 kill 금지, validator 상수 유지가 확인됐다. 새 Sol/high가 이 결과를 독립 검수하기 전에는
  fresh runtime 재실행·G1/M1 승격·사용자 승인을 하지 않는다. G2~G4와 사용자 승인은 미검증이다.
- 다음 한 가지: 새 Codex `gpt-5.6-sol`/high가 lap117 source/tests와 machine evidence를 독립
  검수하고, ACCEPT/REVISE 및 다음 fresh runtime 허용 여부를 기록한다.
