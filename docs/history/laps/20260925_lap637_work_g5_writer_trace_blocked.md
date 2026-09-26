# 2026-09-25 | lap 637 | 목표 G5

- 날짜/lap/목표: 2026-09-25, lap637, G5 드래그 선택 상한 20→50.
- 역할/가설: hands-on work. lap636 후보의 relocated reader/consumer 수리 뒤에도 count20인 원인을 정적 추측하지 않고, writer가 21번째 칸을 시도하는지와 `0x0041DC40` consumer 경계를 런타임 hardware trace로 구분한다.
- 변경파일: `tools/g5_candidate_drag_probe.py`(opt-in trace gate), `tools/g5_selection_watch_trace.py`(read-only gdb hardware trace). 제품 패치 `patches/selection/g5_selection_cap50_v1.py`는 이번 lap에서 추가 수정하지 않았다. 원본/참고 저장소·EXE·게임 데이터·커밋은 수정하지 않았다.
- source/candidate SHA: protected original `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; lap636 candidate `3877194855f54a8b63ea064a6be9f405485bffcb98286198f9a3f5a785459757`; current tool fingerprints: probe `38ebc2f6…45fc`, trace `9b4de7af…7312`.
- 실행 환경/fixture: `tools.runtime_env.prepare` private runtime, isolated Wine/Xvfb 1600×1200, PS3, owner0 type2×55 dense engine-seeded rows around raw worker slot1198, used `735/1500`, live57. Foreground wrapper waited for probe and gdb; cleanup residual0/source unchanged.
- 추적 명령/증거: `env G5_SELECTION_TRACE_CONTROL=<control> PYTHONPATH=$PWD .venv/bin/python tools/g5_candidate_drag_probe.py --variant candidate ...`와 `gdb -p <game-pid> -batch -nx -x tools/g5_selection_watch_trace.py`; clean run control `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260925_lap637c_g5_writer_trace/`. Raw event SHA `138a3341…7c18`, summary SHA `c260740c…3bfe`.
- trace result: hardware watchpoints on count `0x0108c000` and user-requested `0x0108c050` (`0x0108c000+20*4`) plus hardware breakpoints at consumer `0x0041DC40` and writer entry `0x00412D90` all armed. `consumer_entries=1`, `writer_entries=20`, count writes=20, `user_target` writes=1, no 21st write at `0x0108c054`; all writer returns were `0x0040F7F6`. This proves the observed path issued only 20 writer calls; it does not yet prove whether the drag hit-test or an upstream candidate list supplied only 20.
- first harness attempt: dynamic return hardware breakpoint caused gdb SIGSEGV after useful raw events; it was removed before the clean trace. This is harness failure, not product evidence. The clean trace completed with no gdb fatal error; game teardown produced expected SIGTERM in gdb and `continue_error=program not being run` after probe cleanup.
- probe result: candidate selection remained `count=20`, `unique=20`, movement command nonzero20, process exit2 `FAIL_SELECTION_CAP`; 50/51 boundary, 50-command proof, save/load, G5 PASS are FAIL/SKIP. Candidate artifact `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260925_lap637c_g5_candidate_cap50/probe-result.json`, SHA `003529fb…527ab`.
- Fast/回귀: targeted G5/bridge tests `10 passed`; py_compile PASS. Full `make check` foreground completed **894 passed in 689.10s**, Ruff PASS, compileall PASS, mypy PASS, `CONTEXT_PASS`.
- 판정: **`BLOCKED(candidate_upstream_selection_writer_boundary_unresolved)`**. Evidence is sufficient to reject a blind product-byte edit but insufficient to identify the exact remaining cap safely.

### 승격 작업자가 이어서 검증할 것

1. 같은 candidate/fixture를 새 private runtime에서 재실행하기 전에, `0x0041E220` caller와 `0x0041E1D6` writer-call loop의 `[esp+0x10]` source/count를 equivalent instruction trace로 귀속한다. `0x00412D90` writer가 20 calls만 받은 사실과 consumer 50-entry frame을 혼동하지 않는다.
2. hit-test가 20개만 전달한 것인지, consumer가 50개를 20개로 재구성한 것인지, 다른 unpatched local/packet bound인지 판정한 뒤 old-byte/overlap/restore 회귀를 추가한다. 근거 없는 `0x14→0x32` 추가 패치는 금지한다.
3. 원인과 후보를 독립 확정한 뒤에만 원본 count20 대 후보 count50/51, 50기 명령, canary/save/load를 다시 실행한다. G5 PASS·마일스톤 승인은 아직 없다.
