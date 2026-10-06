# 2026-09-29 | lap 773 | 목표 G1 W60 correctness 수리 및 paired runtime

- 실제 provider/model/effort / 지정 역할: Codex native work, hands-on 구현 작업자; high.
- 가설 / 사용자 관찰: coverage 초기화·논리 stride 인덱스·same-frame snapshot·detour rollback을
  고치면 W60 S2가 raw로 검증 가능하고, content-keyed present가 native 1600 화면에서 메뉴/PS3를
  변환한다.
- 예상 PASS / FAIL 조건: 회귀·bridge build·Fast PASS; off/on fresh paired에서 converted,
  primitive calls/covered/stale, nearest oracle, input parity, crash0, tick≥300 모두 확인.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `tools/inmm_stub/g1_mirror2x.c` `cba7d3431b381b37f46e1266d94f4ede1e4a3eb3a8dc14be38e7165a349b11c8`,
  `tools/inmm_stub/g1_mirror2x.h` `408754ae29dd58e957983f5177491fb5bca1a053adc20a7aacea2452a8b0455f`,
  `tools/inmm_stub/direct_draw_trace.c` `59f10729e11f9b8fe856c75f943ee00383f4cfdb2999e60a9c899ebda93811c5`,
  `tests/test_g1_mirror2x.py` `08fd0c3e5347622130bf82d874aebf615f60d169646abc59afeb6ec4819eeecd`; 커밋 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 EXE
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; fresh out-of-tree
  bridge `_inmm.dll` `d635e7c097dc547155f81408c090f9813a859b0d4f4a28ebf8872c7927bbc`;
  private game copy/prefix/Xvfb 1600×1200, default two-player random, synthetic=false.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `pytest -q tests/test_g1_mirror2x.py` 8 passed; `make -C tools/inmm_stub` PASS;
  `make check` **1144 passed, 5 skipped in 665.77s**, ruff/compileall/mypy/context PASS;
  `bash checks/safety.sh check` `SAFETY_PASS`; `make doctor` original verified.
  off manifest `local/runtime/20260929_200331_2483158_0`, raw
  `local/runtime/20260929_200331_2483158_0/output/g1_presentation_trace/trace_raw.jsonl`
  SHA `70d571f9706161e92d0031a692fe1ac0e9ffa2649f58351e8e9611da5f3bcd68`, capture
  `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/captures/20260929_200426_20260929_200331_2483158_0-presentation_2486785_ps3_scene_1790679866784271838.png`.
  on manifest `local/runtime/20260929_200523_2491296_0`, raw
  `local/runtime/20260929_200523_2491296_0/output/g1_presentation_trace/trace_raw.jsonl`
  SHA `e4a8f2ced70a0f28ea70ecae65cfe8f77cfbf955535946e298cd2c61c8fa26ea`, capture
  `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/captures/20260929_200551_20260929_200523_2491296_0-presentation_2492580_ps3_scene_1790679951738027594.png`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): code/Fast/build/safety PASS. off menu·unit·drag PASS,
  minimap `FAIL_NO_EFFECT` at gate=0, cleanup PASS. W60 on `mirror2x_install` raw has
  `primitive_install_success=1`, but PS9/PS7/PS3 primary source is `1600×1200`, all observed
  `converted=0`; no primitive call/covered/stale/metrics raw, same gate=0 minimap
  `FAIL_NO_EFFECT`, cleanup PASS. **S1/S2 runtime BLOCKED; G1 not promoted.**
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: source/EXE unchanged and no commit.
  W60 source identity/rect path is unresolved; live metrics are not emitted at a usable frame
  boundary. No middle independent review or user milestone approval.
- 다음 한 가지: `loop/ESCALATE_SOL`의 승격 작업자가 native 1600 self-source 경로와 live metrics를
  먼저 수리·검증한 뒤, gate=1 `(90,553)` off/on paired oracle을 새 환경에서 재실행한다.
