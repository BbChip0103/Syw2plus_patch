# 2026-09-30 | lap 801 | G2 ESL2608 DxWnd/profile windowed-scroll work

- 실제 provider/model/effort / 지정 역할: Codex work session; hands-on implementation.
- 가설 / 사용자 관찰: 두 새 ESL2608 EXE의 DxWnd profile 누락이 창모드·스크롤 실패 원인일 수 있다.
- 예상 PASS / FAIL 조건: baseline/candidate 각 lane에서 private DxWnd profile이 target을 띄우고
  800x600 window, arrow-key camera delta, right-edge camera delta, crash0을 paired 확인.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `tools/g2_esl2608_dxwnd_scroll_probe.py`, `tests/test_g2_esl2608_dxwnd_scroll_probe.py`,
  `docs/STATUS.md`, `loop/ESCALATE_SOL`; no EXE/source/commit.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  normal baseline `cade60b2451519ec4e305d91279b1c377cf797c813a939c5b54c2e9b30b176a3`,
  fixed baseline `f5f816eeb3d8b531ff030f4b43b2f2338ccf0d2257a5684b034e1f8dc8ee1973`,
  normal candidate `83c7df80a3273d95d58e7a493866bbb40ad705d10120bc05db660400961fad60`,
  fixed candidate `1bdcadf9edeccc16d92696e580a60fc71f13a13b6bba22cafb8c9f50e749262f`.
  Wine 9.0, private win32 prefix/Xvfb 1600x1200, no gameplay fixture reached.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `PYTHONPATH=. python3 tools/g2_esl2608_dxwnd_scroll_probe.py --lane normal --variant baseline ...`.
  r1~r3 artifacts `temp/Syw2plus_patch/g2_esl2608_lap801/dxwnd_normal_baseline{,_r2,_r3}/`;
  r4 profile `C:\dxwnd` writable bundle; r5 profile C: target copy.
  GUI screenshot `temp/Syw2plus_patch/g2_esl2608_lap801/dxwnd-gui.png` records the r3 Z: profile
  warning “No write capability on dxwnd.ini”.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  r1 FAIL=launcher PID was read as game (invalid memory); r2/r3 FAIL=DxWnd target PID absent;
  r4 FAIL=private C: writable profile still no target; r5 FAIL=C: target copy still no target child.
  Control: same DxWnd bundle/profile successfully launched `notepad.exe` under `/r:1`, so DxWnd CLI
  itself is live. G2 product status is **UNKNOWN/BLOCKED(env: DxWnd game target launch)**, not product FAIL.
  Baseline/candidate paired gameplay and scroll evidence: SKIP.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: targeted profile tests **2 passed**; final
  `make check` **1166 passed, 5 skipped in 728.44s**, Ruff/compileall/mypy/CONTEXT_PASS,
  `checks/safety.py` `SAFETY_PASS`, exit0; log SHA
  `193414003f67f3801acd789bb88a3aa13fc9e711c95ebb4e96bfade83111cccb`.
  No middle review or user approval. Existing source/candidate SHA and private game cleanup PASS on all runs.
- 다음 한 가지: Sol/middle independently inspect the DxWnd target-launch blocker and choose a supported
  Windows/DxWnd environment or a documented static filename-profile alternative before paired rerun.
