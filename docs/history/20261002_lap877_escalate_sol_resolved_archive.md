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

## lap877 ordinary middle confirmation — unresolved evidence conflict

- Prior lap876 marker preserved byte-exact in `docs/history/20261002_lap877_prior_lap876_escalate_sol_archive.md` (SHA256 `eefdb55bafa25796968c5c98f58c08c16fd1453a5090f4ffaf9c77ccf069d0fe`). Original evidence and its HOLD are retained above.
- Independent SHA/build42+bridge/DLL/raw checks MATCH; r1 RIGHT has units5 and FINAL units3 different, players0/created0/removed0. r2/r3 diff0 retained. Each lane has568 units at DOWN,572 at RIGHT; FINAL r1 has572 whereas r2/r3 have573, further limiting cross-run comparison. First *recorded* divergence is RIGHT24824; no per-tick full-state observations locate the first actual divergence.
- Material correction: r1 tick plan is loaded24572/input24692,24788/observe24728,24824/final24860. r2/r3 are loaded24574/input24694,24790/observe24730,24826/final24862. Plans match WITHIN each pair, not ACROSS all three. Thus two passes are not same-tick controls for r1. Whether this explains r1 is UNKNOWN.
- Stable PS/tick/camera is not completed phase or quiescence. The prior bounded 0x41C961 acceptance was fixed-camera tick24862 diagnostics, not scrolling tick24824/24860 unit/HP/production-progress proof. Keep B'/G1 HOLD; no C/P5/milestone acceptance.
- Escalated reviewer must inspect these corrected conditions and explicitly bound the next observation-only work repair: preserve common absolute input/observation ticks and ALL captured fields; compare baseline-baseline then baseline-candidate at proved completed return/all-stop with quiescence in the same scroll scene. Current rice-only owner6 tick&7=6 CLI cannot supply r1 controls at ticks ending in0/4; observer adaptation, if needed, goes to work tier. No game/DLL/validator/threshold/original edits or field filtering are authorized here.
- Ordinary middle session stops for substantive record/raw conflict under the current user instruction. New full Fast and runtime SKIP; prior Fast is not current fingerprint verification. Details: `docs/history/laps/20261002_lap877_middle_g1_p4b_bprime_tick_plan_conflict_handoff.md`. Recalculation SHA256 `19031b5a96ca942c424e96c06eebd08aea516498c0791d4fe8d13af1702ccc99` under shared temp `20261002_lap877_middle_review/`.
