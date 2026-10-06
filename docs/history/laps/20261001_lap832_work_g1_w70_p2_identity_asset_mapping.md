# 2026-10-01 | lap 832 | G1 W70 P2 identity asset mapping

- 실제 provider/model/effort / 지정 역할: current Codex session, work/Luna scope; this surface does not expose a separate provider claim.
- 가설 / 사용자 관찰: `SYW2_G1_HD_SOURCE=identity` can bind original primitive-decoded pixels to stable `(writer, source, dimensions, digest)` keys while preserving the same-frame nearest oracle.
- 예상 PASS / FAIL 조건: candidate fresh save006 pair has identity keys and coverage, nearest oracle `>=0.999`, state parity, stale count, source unchanged, cleanup; unknown input effects remain UNKNOWN.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): `tools/inmm_stub/g1_hd_asset.c`, `.h`, `g1_mirror2x.c`, `.h`, `direct_draw_trace.c`, `Makefile`, `tools/g1_hd_identity_probe.py`, `tools/g1_saved_scene_probe.py`, `tests/test_g1_hd_identity_probe.py`; no commit (`LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: protected original `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; candidate DLL `d457689b0cae89f6a4c33482a764a7437fd1d49d2a7ae0461726e45bac769991`; private Wine32/Xvfb; save006 non-synthetic SHA `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`.
- 실행 명령 / 로그 / 캡처 경로 및 해시: pair command in `analysis/memory_maps/g1_w70_p2_identity_asset_mapping_lap832.md`; gate log `logs/gates/g1-w70-p2-lap832.log`, exit `0`; artifact `../temp/Syw2plus_patch/g1_w70_lap832_p2_identity/`; pair SHA `c329738ab1381f011f9799611cedc5ead7a7c9da58d357f2c32a952404d92046`; candidate trace SHA `aa07b5d89cade7c1621c1f755add0fb450d2a50b5cdfdcd63fc42a6ad7bd9f6d`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): mirror 684; nearest minimum `1.000000`; identity keys/events `188/25442`; identity pixels `182650/480000` (`38.052%`); invalid `0`; stale cumulative `775141`; scene parity/source unchanged/cleanup PASS. P2 identity ledger `PASS(partial)`. Minimap/production UNKNOWN in both lanes; cross-process screenshot nearest ratio `0.939704` is not same-frame oracle.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: targeted pytest `11 passed`; private bridge build passed. No original EXE write. Existing input UNKNOWN remains; persistent stale volume and only 38.052% identity coverage require middle interpretation. P3 Scale2x/GDI/full HD coverage and user approval absent; middle review pending.
- 다음 한 가지: 새 middle/Sol 세션이 this raw and implementation independently reviews P2; accept or repair before P3 Scale2x.

## Fast repair note

The first full `make check` reached `1203 passed, 5 skipped` but failed one
static contract because the new identity fields changed
`mirror_perf_details[420]` to `[600]`. This was a harness-only contract drift,
not a runtime failure; the buffer declaration was restored to the pinned 420
bytes before the second Fast attempt.
