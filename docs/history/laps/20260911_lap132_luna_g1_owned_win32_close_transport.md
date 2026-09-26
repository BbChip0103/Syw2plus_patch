# 2026-09-11 | lap 132 | G1 종료 transport 경계

- 실제 provider/model/effort / 지정 역할: Codex 실무 작업자 / Luna/high (세션 설정 계약 기준).
- 가설 / 사용자 관찰: 기존 `xdotool windowclose <XID>`는 Win32 client의 정상 종료를 증명하지
  못한다. install trace의 단일 양의 Win32 `pid`를 읽어 PE32 helper가 visible top-level HWND를
  `EnumWindows`/`GetWindowThreadProcessId`로 열거하고 정확히 하나일 때만 `PostMessageA(WM_CLOSE)`를
  호출하면 종료 transport를 X11 destroy와 분리해 증명할 수 있다.
- 예상 PASS / FAIL 조건: single fixture에서 PID/HWND/thread/match/post 결과가 exact하고 target이
  WM_CLOSE→event loop 종료→exit marker를 남긴다. wrong PID·0개 창·복수 창은 helper가 nonzero로
  fail-closed하며 WM_CLOSE 0회여야 한다. helper가 후보를 임의 선택하거나 kill/terminate를 쓰면 FAIL.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `tools/runtime_env.py` SHA256 `2609e7c264b8b701d7e55f3a3a9ce7953e20715b1244978631c9b506e5c896a2`;
  `tools/win32_close_helper.c` `51f71d82912596abd8d938f0bcafaf2f6507ff88d4b4fee88e2af710dd68c4ff`;
  `tools/win32_close_target.c` `cda43cd28c9d77751fae28d3e14b40d801e26b974d1e06ea2a997a58424ade0c`;
  `tools/win32_close_transport.py` `c211d8e5e48339dcdcabb7da0c4205bd2b44503f3145bb109c048943dd768143`;
  `tools/win32_close_fixture.py` `f7f567a10aed115a83c0337354a1863684bc9a837e6940e72bf37b06783e0456`;
  `tests/test_runtime_env.py` `f6ee15091a61127f1c48d56e0cc06821eb01b3b35652f46252602b1314800d5c`;
  `tests/test_win32_close.py` `8763f7ead0e07e38f87cd1cb1eef96a70c6225668de1d934b8f5b32b06ae3d5e`;
  커밋 없음, uncommitted 보존.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 EXE SHA256
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 변경 없음. Ubuntu x86_64,
  Wine/Wineboot, Xvfb, i686-w64-mingw32-gcc. 게임 활성 플레이어/지도/군대는 해당 없음. fresh
  out-of-tree PE32 build: helper `949e7582d47d0ac7f16c138d627345489c2032d5593e46475fdb6996a707ce42`,
  target `65097257a37fab809905a1ae3bd44ac073de1b1415d2406b65d95092736e572`; fresh Wine prefix와
  fresh Xvfb `:3`, report `local/runtime/win32_close_fixture_20260911_165332_runner/report.json`
  SHA256 `ea3f5fec6c60d9a2b86d80d807e73ac04fef9f56fa69ed8b34e9764872aac6fa`.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `python tools/win32_close_fixture.py build --out-dir
  /tmp/...`; `python tools/win32_close_fixture.py run --build-dir /tmp/... --evidence-dir
  local/runtime/win32_close_fixture_20260911_165332_runner`; `pytest -q tests/test_runtime_env.py
  tests/test_win32_close.py`; `make check`; `make doctor`; `bash checks/safety.sh check`. PNG/게임 runtime
  캡처는 실행하지 않았다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): targeted 68 passed, full `make check` 166 passed,
  Ruff/compileall/mypy/context PASS, original doctor SHA PASS, safety PASS. Positive helper result:
  `requested_pid=32`, `matched_hwnd=0x0002004A`, `matched_thread=36`, `match_count=1`,
  `post_result=true`, target `wm_close_count=1`, final marker true. Negative wrong PID, zero-window,
  multiple-window은 모두 helper return 2, post false, wm_close 0, final marker true. Transport fixture
  PASS; actual game runtime and G1 product PASS are SKIP.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: runtime production close path는 `xdotool
  windowclose`를 사용하지 않고 helper 결과를 evidence에 보존한다. 실제 게임 trace의 Win32 PID/HWND
  및 DLL detach는 아직 fresh runtime에서 검증하지 않았다. PS3 전 trace overflow 2개, G1 1600x1200,
  G2~G4, 사용자 승인은 미검증. 다음 Sol/high가 source/test SHA와 fresh fixture를 독립 검수해야 하며
  사람 마일스톤 승인은 없음.
- 다음 한 가지: Sol/high 독립 검수 후 PASS이면 별도 카드로 PS3 전 overflow를 숨기지 않는 bounded
  lossless trace capacity/aggregation을 계획한다. 검수 전 게임 runtime은 실행하지 않는다.
