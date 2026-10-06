# lap876 escalation to Sol — G1 P4b B' captured-state parity HOLD

## Evidence

- Work ran the existing gdb-free `--terrain-scroll --hd-source scale2x` pair 3 times with pinned non-synthetic `save006.dat` (SHA `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`) and protected original EXE (SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`). No source, DLL, validator, threshold, original, fixture, or prior raw was edited.
- r1 pair result: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261002_lap876_p4b_bprime/pair-result.json` SHA `004890a142fe76ac70c070b573733b07f74a8ce335111c87ab08d715441163ee`; B' HOLD because lane state differed at common tick24824 (5 unit records) and final tick24860 (3 unit records).
- r2 pair result: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261002_lap876_p4b_bprime_r2/pair-result.json` SHA `655ef398aa6137c581ea38f1505f723ef36f349f5f7d1e1dd1d5cf2e1937cd1e`; captured-state equality and B' PASS.
- r3 pair result: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261002_lap876_p4b_bprime_r3/pair-result.json` SHA `29aaf9d7ca46198494999a5ba7e02c648d281c686f526d12ade7d8f7b41f96a2`; captured-state equality and B' PASS.
- Across all runs: same key order, one-step camera outcomes and target ticks; candidate fixed and scroll coverage above thresholds; outside diff0; supported layer move/transfer counters; crash0; source unchanged and private game-copy cleanup PASS. Focused probe tests: 33 passed. B' is still HOLD because one fresh run failed full captured-state parity and the cause is not known.

## Required next review

1. Independently inspect the three pair-result JSONs and corresponding baseline/candidate `probe-result.json` and `trace_raw.jsonl` files. Identify the first divergence before or at tick24824 in r1, then compare the same fields/ticks in r2/r3.
2. Decide whether the captured-state comparison is measuring an allowed B' invariant, an existing pair/harness ordering issue, or an unexplained runtime behavior. Preserve the r1 HOLD and both passing results; do not average them or discard r1.
3. Keep G1/B' HOLD pending that decision. Do not start C, change validator/thresholds, modify game/DLL/source, or reinterpret the mismatch as harmless without evidence. Return any probe/test-only repair scope to work; any game/DLL repair requires a separate explicit decision.

Detailed work record: `docs/history/laps/20261002_lap876_work_g1_p4b_bprime_intermittent_capture_hold_escalate.md`.
