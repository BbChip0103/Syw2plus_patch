# 2026-09-29 | lap 779 | 목표 G1 W60 입력 전달 계측·격리 runtime

- 실제 provider/model/effort / 지정 역할: Codex native work; hands-on 구현.
- 가설 / 사용자 관찰: lap778 ON 누락은 30ms XTest timing 또는 W60 입력 변환 경계일 수 있다. 실제 root, down/up/hold,
  WndProc/GetCursorPos physical→logical 수신을 남기고 충분한 hold/focus로 재시도한다.
- 예상 PASS / FAIL 조건: ON이 PS9/7/5/3, tick≥300, converted/mirror/oracle/summary/crash0/cleanup을 남긴다.
  production은 승인된 mapping이 없으므로 기존 fail-closed BLOCKED를 유지한다. OFF control은 별도 paired 증거다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): `tools/x11_mouse_click.py` `eab6e264…81c0`,
  `tools/runtime_env.py` `dab8a795…0bb8`, `tools/inmm_stub/direct_draw_trace.c` `d47d6e53…e2bf`,
  `tools/inmm_stub/g1_mirror2x.c` `059dd5b7…7842`, `tools/inmm_stub/g1_mirror2x.h` `d2c8cb6b…84e9`;
  bridge `_inmm.dll` `2f4be33e…df096`; 커밋 없음(`LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; fresh private full copy/prefix/Xvfb
  1600×1200, Wine32, default two-player random, synthetic=false, game memory write는 진단 minimap gate만
  `0x0097597c: 00000000→01000000→00000000`, W60 input/present bridge만 개입.
- 실행 명령 / 로그 / 캡처 경로 및 해시: targeted `pytest tests/test_g1_mirror2x.py` 11 passed; bridge
  `make -C tools/inmm_stub all`; fresh final `make check` log
  `logs/gates/full-test-20260929-lap779-final3-makecheck.output` SHA
  `2147c4809ed33051048d1aa9a1fe925b4916a79bd59fb10aa109964253c7042d`, exit 0;
  `bash checks/safety.sh check` `SAFETY_PASS`; `make doctor` original verified. 최종 ON manifest
  `local/runtime/g1_w60_lap779_final_runtime/20260929_233332_380802_0/manifest.json`은 원본 SHA와 bridge
  `2f4be33e…df096`를 고정한다. evidence `4cfffedff5e4b305a3f28ef3802a1ac4791ac1268bf36dee5c8da76959b8d171`,
  verdict `dd7381ab7d984dd8a6a976f8ca11a789153970640467d822f8a1ae6a19fa6e06`, input raw
  `1e744719cdc6b9900b52c499b53c3f6fb46ca40afd1178524d99cc2054696b7f`, trace
  `54d88587cf1ca1194623ab588d4c55f1fcf42603f5ded54ea4b967fbf877704d`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): 최종 ON은 PS9/7/5/3 converted 543, mirror 543,
  nearest oracle min 1.0, primitive calls 19,195, covered max 125,889, PS3 tick 301, camera
  `[91,54]→[49,49]`, input raw 319 events, delivery 8건, WndProc button physical/logical과 down/up,
  root/hold 120ms(드래그150ms) 증거, gate restore PASS, cleanup PASS. menu/unit/drag/minimap PASS;
  production은 승인 mapping 부재로 BLOCKED이므로 전체 verdict는 BLOCKED이며 제품 G1 PASS가 아니다.
  OFF paired run은 PS3 tick3까지 도달했으나 native-split no-mirror trace가 2048 cap을 채워 summary 0,
  `BLOCKED(trace event cap)`; legacy validator 완화는 하지 않았다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: `make check` **1147 passed, 5 skipped**,
  Ruff/compileall/mypy/context PASS, `SAFETY_PASS`; G1 W60 S1/S2 runtime evidence는 현재 work 결과지만
  middle 독립 검수·S3·원본/후보 전체 paired·사용자 승인은 미완료. OFF cap blocker와 production BLOCKED를
  숨기지 않는다. final ON의 `overall=BLOCKED`는 production fail-closed 계약 때문이다.
- 다음 한 가지: 새 middle이 현재 source/최종 ON raw와 OFF cap raw를 독립 재계산하고, OFF summary를 보존할
  bounded trace 집계만 수리·재측정한 뒤 S3 판단을 한다. S3/FEASIBLE/G1 PASS/사용자 승인은 금지.
