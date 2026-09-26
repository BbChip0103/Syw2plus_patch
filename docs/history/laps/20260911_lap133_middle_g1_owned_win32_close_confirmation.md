# 2026-09-11 | lap 133 | G1 owned Win32 close transport 독립 검수

- 실제 provider/model/effort / 지정 역할: Codex 중간 검수 / Sol/high (세션 지정 역할 계약 기준).
- 가설 / 사용자 관찰: lap132의 source SHA가 그대로이고 production runner가 install trace의 단일 양의
  Win32 PID만 helper에 넘기며, fresh PE32 fixture가 단일 owned HWND에만 WM_CLOSE를 전달하고 0/복수/
  wrong PID에서 fail-closed하면 종료 transport 구현을 middle confirmation할 수 있다.
- 예상 PASS / FAIL 조건: 7개 source/test SHA 일치, helper의 EnumWindows/PID/visible/single-match 계약,
  `close -> process exit -> exactly one summary -> copy -> validator` 순서, helper 실패 raw 보존/validator 0회,
  fresh 양·음성 fixture, targeted/Fast/doctor/safety가 모두 PASS해야 한다. 실제 게임 runtime/G1은 SKIP한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 구현·게임 파일 변경 없음. 검수 SHA는
  `tools/runtime_env.py=2609e7c264b8b701d7e55f3a3a9ce7953e20715b1244978631c9b506e5c896a2`,
  `tools/win32_close_helper.c=51f71d82912596abd8d938f0bcafaf2f6507ff88d4b4fee88e2af710dd68c4ff`,
  `tools/win32_close_target.c=cda43cd28c9d77751fae28d3e14b40d801e26b974d1e06ea2a997a58424ade0c`,
  `tools/win32_close_transport.py=c211d8e5e48339dcdcabb7da0c4205bd2b44503f3145bb109c048943dd768143`,
  `tools/win32_close_fixture.py=f7f567a10aed115a83c0337354a1863684bc9a837e6940e72bf37b06783e0456`,
  `tests/test_runtime_env.py=f6ee15091a61127f1c48d56e0cc06821eb01b3b35652f46252602b1314800d5c`,
  `tests/test_win32_close.py=8763f7ead0e07e38f87cd1cb1eef96a70c6225668de1d934b8f5b32b06ae3d5e`로
  lap132와 모두 일치한다. 판정 문서 `docs/STATUS.md`, 다음 handoff와 본 이력만 변경하고 처리한
  `loop/ESCALATE_SOL` SHA256 `a87ed7768a21627d9b99622f52a1a5a9cc7e60d184f6f3ade5d3b84aa1c82f93`는
  아래 원문 보존 후 제거했다. `LOOP_ALLOW_COMMITS=0`, 커밋/푸시 없음.
  최종 `docs/STATUS.md` SHA256은 `b5f790681ad49164e3b2ccfa21c7cc1893d23283f219fe2c5c384fcb40c0176f`,
  handoff SHA256은 `724adb867803b2f1c19c59bcf6246c8b0c6cfe43315680f303690a6ff0a79fd1`이며
  본 self-referential lap 파일 해시는 생략한다.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본 EXE SHA256
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` verified/무변경. 후보 제품 없음.
  fresh out-of-tree helper SHA `e3b7799f155030536ae4ab11c89778b335c26b8b7736d8ba930beaf16ba4c8ac`,
  target SHA `3c15a374d836524dcbf38f969b1c11db62ecaa8672e1be6db0177b636e21232b`; fresh Wine prefix와
  fresh Xvfb `:3`. 게임 플레이어/지도/군대 해당 없음, synthetic PE32 fixture임을 명시한다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `sha256sum` source/test, `make doctor`, `make check`,
  `.venv/bin/python -m pytest -q tests/test_runtime_env.py tests/test_win32_close.py`, fixture build/run,
  `file`, helper-failure inline probe, `bash checks/safety.sh check`. report는
  `local/runtime/win32_close_fixture_20260911_lap133_sol/report.json` SHA256
  `715677421e2e5748f9f21db38769c39c75a1c4566ed61addb9c52af455836c89`; 게임 runtime/PNG 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): targeted **68 passed**, full **166 passed**,
  Ruff/compileall/mypy/context PASS, doctor original verified/no side effect, safety PASS. positive는
  PID32/HWND `0x0002004A`/thread36/match1/post true/target rc0/WM_CLOSE1/final marker true. wrong PID·0창·
  복수창은 모두 helper rc2/post false/WM_CLOSE0/final marker true. helper-failure 직접 probe는 raw exact
  보존/trace copy 없음/validator 0회다. **MIDDLE CONFIRM PASS**; 실제 게임 runtime/G1은 SKIP.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: production source에 `xdotool windowclose` 호출은
  없고 helper는 terminate/kill을 쓰지 않는다. 실제 게임 PID/HWND, WM_CLOSE 뒤 process exit/DLL detach와
  final summary는 아직 fresh runtime에서 검증하지 않았다. PS3 전 overflow 2개, G1 2배 출력/입력,
  G2~G4와 사용자 승인은 미검증이다. PE patch old/new bytes·restore 검사는 제품 patch가 없어 해당 없음.
- 다음 한 가지: 새 Luna/high work가 `docs/plans/20260911_lap133_g1_trace_capacity_handoff.md` 범위에서
  lossless bounded trace aggregation/validator/synthetic 회귀를 구현·검증하되 게임 runtime은 실행하지 않는다.

## 소진 전 `loop/ESCALATE_SOL` 원문

lap132 Luna/high 실무 결과를 새 Sol/high 세션이 독립 검수할 것.

검수 대상:
- `tools/runtime_env.py`의 finalization이 install trace의 단일 Win32 PID를 읽고,
  `tools/win32_close_transport.py`를 통해 `wine win32_close_helper.exe --pid PID`를 호출하는지 확인.
- `tools/win32_close_helper.c`가 `EnumWindows` + `GetWindowThreadProcessId`로 요청 PID의 visible
  top-level 창을 열거하고 match_count가 정확히 1일 때만 `PostMessageA(WM_CLOSE, 0, 0)`를 호출하며,
  0/복수/잘못된 PID에서 post하지 않는지 확인. terminate/kill/X11 destroy가 close 증거로 쓰이지 않는지 확인.
- fresh out-of-tree i686 PE32 build와 fresh Wine prefix/Xvfb fixture를 재실행해 positive의
  PID/HWND/thread/match/post와 target `wm_close -> exit marker`, negative wrong PID/zero/multiple의
  post=false·wm_close=0을 독립 확인.
- `make check`, `make doctor`, `bash checks/safety.sh check` 및 기록 SHA/report를 대조.

판정 경계:
- 현재 결과는 fixture transport PASS일 뿐 실제 게임 runtime/G1 제품 PASS가 아니다.
- Sol 검수 전 게임 runtime 재실행, PS3 overflow 상수 변경, baseline/golden 승격을 하지 않는다.
- 검수 PASS 뒤에만 다음 별도 작업으로 lossless bounded trace capacity/aggregation을 다룬다.
