# 2026-09-30 | lap 820 | work | G1 W70 P1 writer census

- 날짜/lap/목표/가설: 2026-09-30, lap820, G1 W70 P1. SYW2_G1_CENSUS=1을 별도
  measurement-only detour로 설치하면 원본 primitive 호출 규약을 보존하면서 writer별 old-byte
  설치·호출·인자 표본·DirectDraw surface event를 save006에서 수집할 수 있다는 가설.
- 변경파일/원본·후보SHA: 신규 tools/inmm_stub/g1_census.c, tools/inmm_stub/g1_census.h,
  tests/test_g1_census.py; tools/inmm_stub/Makefile, tools/inmm_stub/direct_draw_trace.c,
  tools/runtime_env.py, tools/g1_saved_scene_probe.py 연결 변경. 보호 원본
  [HQ]Syw2plus 2002.exe SHA256 b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac,
  save006 SHA256 616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064; EXE는
  수정하지 않았고 커밋하지 않았다.
- 실행환경/fixture: read-only [ESL]Syw2plus source, 새 Wine32 private prefix/Xvfb
  1600x1200, save006 비합성 fixture, loaded PS3 scene. census-only r1/r2/r3 모두 private
  game 사본 삭제 및 prefix process residue 0.
- 실행명령/로그: make -C tools/inmm_stub all; pytest -q tests/test_g1_census.py
  tests/test_g1_mirror2x.py; python3 -m py_compile tools/g1_saved_scene_probe.py;
  pytest -q tests/test_g1_saved_scene_probe.py tests/test_g1_census.py; 세 번의
  tools/g1_saved_scene_probe.py --census-only 실행. raw:
  g1_w70_lap820_p1_saved/census/census_raw.jsonl SHA
  78c64e92dc6d3105c00f6e3c1123b9422b1121115a2edeec7c22c28719a44cef,
  r2 a3dc377a9c687c86c9224a9bc92c293ea2bbeb35b5ce65a40bb04a8ea347c814,
  r3 73eab15cea6e02db25685b3c3dcb1f2b575042a83dcd2b0f273003cbc81acc6a.
- 수치/판정: 각 raw 304행 = install8 + primitive_call256 + surface_write32 + summary8.
  세 실행 모두 8/8 target active, arity 5×5 + 6×2 + SetPixel 3×1, writer별 32 sample/summary,
  DirectDraw event32, crash0, cleanup PASS. r1 summary call count은
  rle_clip 11184, rle_plain 21420, rect_fill 3258, block_copy 2501,
  rect_border 1351, rle_tinted_clip 6739, rle_tinted 39664, set_pixel 6473;
  r2/r3도 같은 target set과 ABI 설치를 재현했다.
- PASS/FAIL/SKIP/UNKNOWN: P1 hook/install/raw collection PASS(partial). 정적 old-byte
  guards와 실행 설치는 PASS. dest_read는 296/296 unknown; last-writer map, unique-pixel
  attribution, present별 >=95% coverage는 아직 수집하지 않았으므로 P1 overall HOLD.
  random presentation selector control은 새 runtime 두 번 모두 PS13으로 이탈해 raw로 쓰지
  않고 보존했으며, save006 경로로 우회했다. 이는 G1 완료/사용자 승인 근거가 아니다.
- 다음행동: P1 후속 work에서 census에 논리 800×600 last-writer map·writer별 unique pixel/
  bbox·present 경계와 destination-read falsifiable probe를 추가하고, 같은 save006 fresh
  baseline/W70 pair를 다시 수집한다. G1_CENSUS는 기존 W60과 동시 활성하지 않는다.
