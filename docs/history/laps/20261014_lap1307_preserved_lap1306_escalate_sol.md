lap1306 work → fresh middle/Sol independent review.

Scope: review only the two root-assigned H-HDGUARD repairs and their exact evidence; do not widen the known mirror-validator BLOCKED into a new runtime/retest gate.

Changed files:
- tools/inmm_stub/direct_draw_trace.c: mirror_pack_details buffer 1000 → 1200, enough for the test-calculated 1014 bytes plus NUL with margin.
- tests/test_g1_hd_native_reader.py: add source-SHA index rows for BMP/sheet success and truncation fixtures; fail-closed guard unchanged.

Evidence: docs/history/laps/20261014_lap1306_work_hdguard_failures_repair.md. Both previously failing tests pass; scoped five-file pytest set 164 passed; make lint/typecheck PASS; rebuilt default-on WINMM DLL SHA256 f32ee6190716e705a0376213adbe8fc0722d9a3abdaed07f248bdd4766912655. Isolated official ESL2614 private-copy run PASS: PS3 60.755s/1216 presents, HD min100%, source/pack rejects0, trace drop/overflow0, close and cleanup PASS. Source EXE SHA ac61a28f84f71d602c581a17c835ec4dbb99aad0341c6755e395549005cf88bf. Result/raw hashes are in the lap record.

Known separate limit: mirror validator remains BLOCKED (2382 nearest-oracle entries, min 0.614677); Scale2x validator PASS. Do not treat this existing validator state as a regression or G1 acceptance. Windows, full make check, delivery and user milestone acceptance remain pending.

Middle review should independently compare the two code/test diffs, inspect the RED→GREEN test evidence, confirm DLL/result/raw identities and the 60.755s summary/cleanup, then report scoped technical acceptance or a concrete discrepancy. If accepted, root decides the already-authorized single full make check before delivery. Do not re-run the game or expand tests absent a concrete mismatch.
