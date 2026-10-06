# 2026-09-30 | lap 808 | 목표 G1

- 실제 provider/model/effort / 지정 역할: Codex native 세션 / work tier hands-on 구현·검증.
- 가설: lap807 HOLD의 원인은 OFF가 type70·gate0, ON이 type49·gate1인 비paired fixture이다. 선택형
  type49/nation1 계약과 동일 minimap gate를 양쪽에 적용하면 raw-only production parity와 W60
  presentation evidence를 한 쌍으로 판정할 수 있다.
- 변경파일: `tools/runtime_env.py`, `tools/g1_mirror2x_probe.py`,
  `tests/test_runtime_env.py`, `tests/test_g1_presentation_trace.py`.
  원본/참고 저장소·EXE·게임 데이터는 쓰지 않았다. 현재 SHA:
  `runtime_env.py b0cdaa08…e542`, `g1_mirror2x_probe.py 8fe1a906…6ea8`,
  `test_runtime_env.py 3c6be60b…f1e2`, `test_g1_presentation_trace.py 30a84e8b…29f4`.
- 원본/후보 SHA: 보호 원본 및 두 private game copy 모두
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
  공통 diagnostic bridge `a3e9165e…d2ff`; PE32 close helper `b3cdf8a2…36b`.
  두 run 모두 `[ESL]Syw2plus` source, Wine32/private prefix/Xvfb 1600×1200, synthetic=false.
- 구현: `--g1-minimap-gate`를 native mirror OFF에도 허용하고 old bytes `00000000` → `01000000` →
  exact restore를 양쪽에 기록했다. `--g1-type49-fixture`는 owner0 nation1·관측 type49를
  fail-closed로 요구하고 실제 selection type49도 확인한다. native2x mirror-OFF control은
  1600×1200 primary/no mirror raw validator로 판정하며 W60 PASS로 오인하지 않는다.
- fresh 실행 control OFF:
  `local/runtime/g1_w60_lap808/20260930_132225_3714932_0/`;
  manifest SHA `a1856e63…a62f`, raw SHA
  `60549c03fbd0c4d0753d63a0f57e022ed1600c37b485655dfff89163737a5116`.
  fixture PASS, menu/unit/drag/minimap PASS, production raw-only UNKNOWN/no-effect,
  command-table raw hex identical, control validator PASS event752 mirror0,
  cleanup/prefix residue0; private game copy removed.
- fresh 실행 candidate ON:
  `local/runtime/g1_w60_lap808/20260930_132050_3706673_0/`;
  manifest SHA `6a537edc…7ec2`, raw SHA
  `b9929bacfdecd63d0669099326a091d5e025623e428441c374859dc8aa28c904`.
  fixture PASS, menu/unit/drag/minimap PASS, production raw-only UNKNOWN/no-effect,
  converted PS3/5/7/9=246, mirror548, primitive21291, covered125889,
  nearest oracle1.0, summary/drop/malformed PASS, cleanup/prefix residue0;
  candidate W60 validator PASS and private game copy removed.
- paired comparison: both observed owner0 nation1/types `[7,49]`, selected type49, raw A6[0]=1,
  identical primary command-table raw hex, same gate old/written/restored bytes, production has no
  native state effect in either run => `N/A(original parity)` at raw-only level. Start coordinates differ
  because the game is still a fresh random scene; semantic fixture contract, not unobserved replay seed,
  is the accepted pairing boundary.
- 회귀/검증: targeted `196 passed`; Ruff PASS; compileall PASS; mypy targeted PASS; `make lint` PASS;
  `make typecheck` PASS. Final `make check` is run once after this record/status/handoff is written.
- 판정: **work PASS / G1 remains HOLD pending fresh middle independent review**. S3/FEASIBLE/G1 PASS/
  사용자 승인은 선언하지 않는다.
- 다음 행동: Sol/Opus5 middle이 두 raw/evidence/command-table와 source SHA를 독립 재계산하고,
  type49 semantic fixture pairing과 native2x control boundary를 수용할지 판정한다.
