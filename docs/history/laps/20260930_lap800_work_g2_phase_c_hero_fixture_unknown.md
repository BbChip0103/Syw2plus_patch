# 2026-09-30 | lap 800 | G2 ESL2608 Phase-C hero fixture work

- 날짜/lap/목표: 2026-09-30 / 800 / G2 ESL2608 두 EXE Phase-C hero 생산 gate 확인.
- 가설: live HQ type과 TypeSpec `flags&0x8`, 생산표 prerequisite를 결합하고 native engine fixture로 prerequisite unit을 제공하면 실제 UI hero 생산이 된다.
- 변경파일: `tools/g2_esl2608_phase_c_production_probe.py`, `tests/test_g2_esl2608_phase_c_production_probe.py`, `docs/STATUS.md`.
- 원본·후보 SHA: normal baseline `cade60b2451519ec4e305d91279b1c377cf797c813a939c5b54c2e9b30b176a3`; candidate pinned `83c7df80a3273d95d58e7a493866bbb40ad705d10120bc05db660400961fad60` (candidate runtime 미실행). 변경 도구 SHA `ad230a975ddbce7cd6887b49be9b815e1f59349240e41d921bcba368a0a95e23`, 테스트 SHA `41521f8389b463835cdd5f4fb882b0f86fab3d3b4d343b60e26f05a1e6064308`.
- 실행명령: `pytest tests/test_g2_esl2608_phase_c_production_probe.py`; `make lint`; `make typecheck`; fresh `python3 tools/g2_esl2608_phase_c_production_probe.py --lane normal --variant baseline` r1~r5, private Wine/win32/Xvfb/1600x1200, artifact `temp/Syw2plus_patch/g2_esl2608_lap800/normal_baseline_r5/`.
- 수치/fixture: r5 live HQ type49, hero kind94 (`flags=6152`, bit3 set), prerequisite kind37. Native `op5` created one real engine unit37; map `100x100`; `prereq_owned_cache=0` for 10s; UI hero order/generation `0`, hero counter `0→0`; worker/rally path remained previously proven. Fixture is synthetic/native-engine and prerequisite-only, never counted as hero evidence.
- 판정: r1 FAIL (fixed coordinate outside live map); r2 FAIL (live slot7 omitted); r3 FAIL (grid y `539/575`); each cause was traced and repaired. r4/r5 FAIL for hero, with exact gate observation `PlayerStruct+0x315C[37]=0`; classify **UNKNOWN(fixture contract)**, not product FAIL. r5 source unchanged, private game removed, prefix residue0; raw SHA `97d6ebf35f979d028ff65e6a8833a3be46531d4f50ac387fb1cd3e5ecb0a97c6`.
- PASS/FAIL/SKIP: targeted tests 4 PASS; Ruff/compileall/mypy PASS; runtime hero FAIL/UNKNOWN; no candidate/fixed-start 4-way because baseline gate-legal fixture was not established.
- 다음행동: do not retry the same native seed fixture; proceed to DxWnd/profile windowed scroll paired check, then 24k/144k load and multiplayer. Hero remains unverified.
