# 2026-09-30 | lap 810 | 목표 G1

- 실제 provider/model/effort / 지정 역할: Codex native 세션 / work tier hands-on 구현·검증.
- 가설 / 사용자 관찰: S1/S2가 `FEASIBLE`로 독립 수용된 뒤, 원본 HUD resource draw의 정적 계약
  `sprite id=0x24, frame=0, x=10,y=3, 20x24`를 W60 mirror에서 한 번 명시 패턴으로 치환하면
  최종 1600 캡처의 마스크 내부는 2x2 복제가 아니고 외부는 불변임을 증명할 수 있다.
- 예상 PASS / FAIL 조건: fresh private Wine32/Xvfb 1600x1200에서 원본 EXE SHA 불변, S3 raw
  event 1건, pattern mask 315 opaque pixels, 최종 캡처 mask 내부 비복제·mask 밖 동일. 없으면
  `BLOCKED(candidate correctness)`로 유지한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `tools/inmm_stub/g1_mirror2x.c`, `.h`, `direct_draw_trace.c`, `tools/g1_s3_probe.py`,
  `tools/runtime_env.py`, `tests/test_g1_s3_pattern.py`; 모두 uncommitted, 커밋 없음
  (`LOOP_ALLOW_COMMITS=0`). EXE/원본/참고 저장소는 변경하지 않았다. 최종 bridge DLL SHA는
  `f3163e2074644f9d54b73ff5df8ebf82820731e507adf9d04b4c976f7393476a`이다.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본 및 모든 private
  copy EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; Wine32/private
  prefix/Xvfb 1600x1200, default two-player random, synthetic=false, diagnostic render/input
  bridge only. S3 fixture is original `fnt/resource.spr` registry contract (id 0x24/frame 0);
  final successful run used no type49 requirement because S3 target is the HUD resource row.
- 실행 명령 / 로그 / 캡처 경로 및 해시: targeted pytest/build; fresh control
  `local/runtime/g1_s3_lap810_r4/20260930_142519_51820_0/` raw SHA
  `59a3e922622032b512dfbeec20f68c63cf803d89f472b3af82bc6228b74b28a8`; fresh S3
  `local/runtime/g1_s3_lap810_pattern_r5/20260930_143150_74969_0/` raw SHA
  `17a1ea036d45734c236331542ae89647524c0b1171c491ff54566f15ebf2ce9d`; control PNG
  `20260930_142558_20260930_142519_51820_0-presentation_53551_ps3_scene_1790745958042745636.png`;
  S3 PNG
  `20260930_143218_20260930_143150_74969_0-presentation_76471_ps3_scene_1790746338537953331.png`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): targeted S3/mirror tests `14 passed`; final S3
  validator `PASS`, 246 converted presents across PS3/5/7/9, 545 mirror presents, primitive calls
  21233, S3 event 1, pattern pixels 315, nearest minimum `0.99934375` (the explicit S3 frame is
  the sole oracle waiver). PNG paired analysis: resource rect changed 945 pixels, all 315 opaque
  mask blocks are nonuniform 2x2, outside-mask difference 0. Earlier r1/r2 malformed JSON was
  traced to Win32 `wsprintfA` length truncation; r3/r4 invisible pattern was traced to overlay
  lifetime/visible-primary timing and fixed by persistent present plus destination overlay.
  Production input remains `UNKNOWN` in the generic G1 harness for both runs; this does not alter
  S3 proof and is not promoted to G1 product PASS.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: source EXE unchanged; private game copies
  removed, prefixes residue0, cleanup PASS. S3 bridge path is opt-in and diagnostic-only. New
  middle/Sol independent review, full primitive coverage, final original/candidate input parity,
  G1 product PASS, and user milestone approval remain incomplete. Existing control generic verdict
  is `BLOCKED` only because production is UNKNOWN; its presentation validator is PASS.
- 다음 한 가지: 새 middle/컨펌 세션이 lap810 S3 raw·PNG·source SHA와 mask calculation을
  독립 재검산하고 S3를 수용할지 판정한다. 그 전에는 G1 PASS/사용자 승인/다음 목표 전환을
  선언하지 않는다.
