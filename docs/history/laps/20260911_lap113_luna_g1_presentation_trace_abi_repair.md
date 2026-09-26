# 2026-09-11 | lap 113 | G1 DirectDrawCreateEx ABI repair

- 실제 provider/model/effort / 지정 역할: Codex 실무 작업자 범위(Luna/high 지정 카드). 상위 방향·중간
  컨펌은 수행하지 않았고, 다음 새 Sol/high가 독립 검수해야 한다.
- 목표 / 가설 / 예상 판정: lap111이 확정한 `DirectDrawCreateEx` arg2/arg3 ABI 역전을 header와
  원본 caller 순서로 교정하면 잘못된 IID/DD object 해석을 제거하고, 컴파일 회귀 계약이 재발을
  차단한다. corrected build/targeted/Fast/safety는 PASS, fresh trace는 IID→DD→surface→present와
  PS9→PS3가 모두 있어야 PASS이며 하나라도 없으면 BLOCKED다.
- 변경 파일 / fingerprint / 커밋: `tools/inmm_stub/direct_draw_trace.c`
  SHA `906562e03c83c52f73003a8fd58c06a8ad7981a9e72a2e64729937eef53b077a`,
  `tests/test_direct_draw_abi.py` SHA `b921479c2b975654efdfca6c3370f97538964ccb16d7ce3d6dbd9f3e910011ca`.
  커밋 없음(uncommitted); 커밋 허용은 없었다.
- 원본 SHA / 후보 SHA / 환경 / fixture: source/private `/home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus_re/Syw2plus/syw2plus_original.exe`
  및 `/home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus_patch/Syw2plus/syw2plus_original.exe` SHA
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, `cmp=0`, PE32.
  caller `0x00464364..0x00464374`, IID `0x004E5928`, thunk `0x004D7938`, IAT `0x004E5018` old bytes는
  repair card와 일치했다. 제품 후보/게임 EXE 변경은 없고, bridge는 저장소 밖 fresh output이다.
- 실행 명령 / 결과: `pytest -q tests/test_direct_draw_abi.py` **3 passed**; 저장소 밖 Makefile과
  동일한 MinGW build 성공, DLL SHA `b7849b88c116e4767ce41de945be2d6c0cc956a8c2f1eaf079a5cb3e038f2eb1`.
  `make doctor` PASS(top `ok=true`, original verified), `make check` **148 passed**, Ruff/compileall/
  mypy/context PASS, `bash checks/safety.sh check`=`SAFETY_PASS`.
- runtime 명령 / 증거: 새 whole copy/new Win32 prefix/private Xvfb에서
  `.venv/bin/python tools/runtime_env.py g1-presentation-trace --manifest local/runtime/20260911_135729_1465423_0/manifest.json --screen 1600x1200x24 --timeout 90`
  정확히 1회. `runtime check` 및 `make doctor-runtime` PASS. manifest SHA
  `15c92dcfab02c19af135ae4b9081c9e10d1eb9fe7bcb3172aaabe819299b2330`; raw trace
  `local/runtime/20260911_135729_1465423_0/output/g1_presentation_trace/trace_raw.jsonl` SHA
  `891f4eafeef8cccaeeee3f6f00b51431d3f87314983333622e6c2d1682ccb1f6`; evidence SHA
  `3842e0c5c02396fbe3aa508dde73ba1c89804831cef2468df2955b9c77d6a982`; verdict SHA
  `1996af7b1969fa3e88bb6d2a1fc69745d35c85082b6acee10e7c5cda2483bf6c`; provenance SHA
  `5e41454d67eee85e7b68437c74ee36e8c2db5178ed5eafd7853ad3a9bdbec10d`.
- 측정값 / 판정: raw 70 events, install gate PASS. `direct_draw_create_ex` IID is
  `15E65EC0-3B9C-11D2-B92F-00609797EA5B`, DD object `0x01E6D080`, HRESULT 0; several Surface7
  create/desc and two early blt events exist. Menu input before PS9→after PS7 PASS, screenshots are
  800x600 with before SHA `277a0b23b836e30508326efa0295aa0c35f09a6a9fc4f55fa2b121b09ce5b252` and after SHA
  `7f50c8b3203a3c9ca9053828566e931ef59e634f283afc876e4ccb9bd9b915ea`. Live overall **BLOCKED/FAIL**:
  `xdotool mousemove --sync 760 40` timed out after 10 seconds (exit2), no PS3 capture/final summary;
  cleanup `ok=true`, `global_kill_used=false`, `prefix_processes_after=[]`. No retry.
- 회귀 / 남은 위험 / 승인: ABI compile regression is PASS, but native full present identity and G1
  2x output/input remain unverified. No product patch, candidate SHA, G1/M1 PASS, Sol confirmation, or
  user milestone approval. Existing runner/input timeout is not silently reclassified as game crash.
- 다음 한 가지: 새 Sol/high가 this lap's source/test/build and one fresh raw run independently reviews;
  decide separately whether runner/input automation needs a diagnostic card. Do not rerun this live trace
  from the current handoff.
