# lap786 escalation — lap785 raw SHA transcription conflict; G2 work held

## Stop reason

- The fresh OFF raw is
  `8798fafb8e199b8d7c553f4a42d505d9b60c02551b3a6a737a27cb05414b133b`, but
  `docs/history/laps/20260930_lap785_work_g1_w60_harness_repair_off_on.md` and
  `docs/STATUS.md` record `...133` without the final `b`.
- The first 63 hexadecimal characters agree, so a transcription omission is the leading explanation; it is
  still a raw-vs-record conflict and triggers the session's mandatory escalation rule.
- The ON raw SHA matches its lap785 record exactly. Its preserved verdict reports validator PASS:
  1672 events, converted 246 in PS3/5/7/9, mirror 546, nearest oracle 1.0, dropped 0,
  cleanup PASS; overall remains BLOCKED only because production is UNKNOWN.
- G1 is paused by the newer 2026-09-30 02:1x user directive. This escalation does not close G1, approve S3,
  or turn lap785 into a product PASS.

## Elevated review required

1. Re-hash the lap785 OFF raw at
   `local/runtime/g1_w60_lap785_off_retry/20260930_020047_1653694_0/output/g1_presentation_trace/trace_raw.jsonl`.
   If it is still `...133b` and no second mismatch is found, correct the two narrative transcriptions only;
   do not rerun G1 solely for this one-character omission.
2. Preserve the lap785 G1 evidence as paused/HOLD. Do not decide production raw-only N/A, S3, FEASIBLE,
   G1 PASS, or user approval while G2 has priority.
3. After resolving the provenance typo, hand the following single card to a work-tier Luna/Sonnet worker.

## Next work card — G2 ESL2608 paired checklist and repair

- Pin baselines (read-only): normal ESL2608 `1600-200-3000` SHA
  `cade60b2451519ec4e305d91279b1c377cf797c813a939c5b54c2e9b30b176a3`; fixed-start SHA
  `f5f816eeb3d8b531ff030f4b43b2f2338ccf0d2257a5684b034e1f8dc8ee1973`.
- Pin candidates (read-only): normal `1500-500-5000` G2 SHA
  `83c7df80a3273d95d58e7a493866bbb40ad705d10120bc05db660400961fad60`; fixed-start SHA
  `1bdcadf9edeccc16d92696e580a60fc71f13a13b6bba22cafb8c9f50e749262f`.
- Use identical isolated fixtures for baseline/candidate pairs. Cover drag/ALT/Ctrl/Shift selection,
  Shift+single-click with >20 and group-selected states, 20-unit groups, move/real combat/stop/hold/patrol,
  minimap with original-gate parity, production then UI rally point including officers, DxWnd windowed scroll,
  old/current save-load, mass/high-slot portraits, long ticks, and multiplayer to the supported extent.
- Treat prior Shift-click PASS and production/save-load PASS as references, not current checklist completion.
  Classify each failure as product source, harness/fixture, or DxWnd filename-profile behavior; repair only
  a reproduced implementation defect and rerun the affected fresh pair in the same work lap.
- Do not touch `local/runtime/g2_*`, `*g2shift*`, or the user's existing EXEs. Build two repaired EXEs under
  new exclusive names in `../260921_temp/`, record source/input/output SHA and exact byte scope, and create a
  new readme preserving the N4K8/save-compatibility limits. No commit or push.

