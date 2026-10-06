# G1 W70 P5-T-V independent review — lap934 work

## Review scope

Independently review lap934's V1/V2 repair and fresh runtime evidence. This is the next middle review, not a milestone decision. Preserve G1/P5-T HOLD unless the measured criteria and the still-open product requirements support more; do not treat the worker's PASS or process exit as approval.

## Frozen implementation and provenance

- Work record: `docs/history/laps/20261004_lap934_work_g1_p5t_v_lane_repair_and_runtime.md`.
- Recalculation JSON: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261004_lap934_p5t/recalculation.json` (SHA256 `ac76be2c116bb92ce039ecf07a8101957b412bced81263c229775028d16b7f10`, 146 named inputs including all PNG and snapshot files).
- Source `tools/inmm_stub/g1_mirror2x.c` SHA256 `b70d044acb18842ee68a418539ae0f974e1652a615ace8cfa8faa019cb011804`; test `tests/test_g1_mirror2x.py` SHA256 `2b082f481c6043adb41b9ed6e40f2d02b20a7e8a945109806dbbccb19fede32f`.
- Original/private EXE SHA256 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; fixture save006 SHA256 `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`, non-synthetic. Candidate bridge hashes vary by run and are retained in each run's manifest in the recalculation JSON.

## Raw to inspect

All outputs are under `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/`:

- `20261004_lap934_p5t_green/`
- `20261004_lap934_p5t_bprime1/`
- `20261004_lap934_p5t_bprime2/`
- `20261004_lap934_p5t_c1/`
- `20261004_lap934_p5t_c2/`
- `20261004_lap934_p5t_c3/`

For each scroll pair inspect `pair-result.json`, baseline/candidate `probe-result.json`, `trace_raw.jsonl`, five in-process snapshot blobs/trace, and paired `*.png` captures. For C runs inspect both performance-window probe results and histogram traces. Confirm each run's source/fixture/build identity and `cleanup.game_removed=true`, `prefix_processes_after=[]`; independently hash listed raw inputs and recompute gates from raw rather than trusting recalculation JSON.

## Claims to challenge

- V1: the second verifier uses `scratch_b` against `unclipped_ff`; first verifier still uses the 00 lane; mask calculation and bind input remain unchanged. No cache or visual threshold changes.
- V2: the two full allocations and mask allocation, including NULL branches, contribute to `G1_PERF_CLIP_PREPARE`; original replay and identity bind remain excluded.
- GREEN/B′1/B′2: same scene, snapshot ticks `[24692,24728,24788,24824,24860]`, scroll/input/camera parity, active Scale2x, V1/V2/V2s/V2q, 30 valid samples per key, and PT-c ≤52.0ms in two consecutive B′ pairs.
- P-1/P-2: recompute clip mismatch and replay counts for late20 and DOWN/RIGHT windows; do not infer from the source edit.
- PT-d′: late20 tinted calls ≥1530, DOWN ≥3030, RIGHT ≥2180; late20 effective coverage p50 ≥395,960 and stale p50 ≤74,864. `tinted_clip` covered remains a recorded 0, not a gate conversion.
- C1/C2/C3: each pair is 20 seconds; candidate/baseline tick-rate ratio ≥0.95 and p95 delta ≤16ms, dropped present 0, camera fixed.
- PNG direct review: V1/V2/V2s/V2q/Scale2x and UI/world geometry; record any visual/input discrepancy. `old nearest=BLOCKED` is a separate known diagnostic and does not replace these active gate results. `input_effect_comparison=HOLD` remains explicitly unresolved.

## Review output

Record evidence, independent recalculation, PASS/FAIL/HOLD with limits, any source/raw conflicts, and one next work item. Do not edit raw, golden, baseline pins, validator thresholds, or implementation as middle. If evidence materially conflicts, preserve both and follow the loop escalation rule.
