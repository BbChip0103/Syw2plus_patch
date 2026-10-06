# Sol / middle independent review request — lap866 G1 P4b B' HOLD

This is a hands-on work handoff for independent diagnosis, not a milestone submission. Keep G1 B' on HOLD. Do not start C fresh3, P5, another input pair, or claim G1 completion before reviewing this evidence.

## Request

Independently recalculate the r4/r5 saved-scene pairs and decide whether the candidate-only unit-state divergence after RIGHT is a product difference or an observation/timing artifact. Work must not directly patch game implementation; if a concrete harness repair is justified, return its exact scope to the work role.

## Evidence

- Work record: `docs/history/laps/20261002_lap866_work_g1_p4b_scroll_ack_scene_parity_hold.md`.
- r4 pair/raw: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261002_lap866_p4b_scroll_ack_r4/pair-result.json`, lane `probe-result.json`, `trace_raw.jsonl`.
- r5 pair SHA256 `5349b4288e3e056a95832f5e327eae9d5fc5af9742214f676f94faf0fab2b1f4`; pair path `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261002_lap866_p4b_scroll_ack_r5/pair-result.json`.
- r5 candidate raw SHA256 `ae2c8fbcfafa499df3aa436af2c42b71726b0b9d83b020a2b113701644104f07`; baseline raw SHA256 `c3eabf685e581419d83af6290fb21d36b17dfa3b9634c7008f84525fe93a23b6`.
- r5: both ready ACKs, DOWN/RIGHT key receipts, exact camera sequence `[158,101]→[159,102]→[160,101]`, keyup stability, source and cleanup pass. Candidate fixed first20/last20 p50 `337648.5/355734`; DOWN/RIGHT 30-present coverage p50 `365287/353683`; Scale2x validator and both scroll gates pass.
- Loaded scene and DOWN post-action state match. RIGHT post-action differs; final candidate has 566 units vs baseline 564. Owner caps match. RIGHT stable ticks were 24656/24674; both recorded 36-tick post-action observation windows. Pair verdict remains HOLD.
- r4 showed the reverse pattern: DOWN post-action differed, RIGHT matched, final scene matched. Do not infer parity from camera/coverage gates alone.

## Review outputs required

1. Recompute r5 action scene equality, unit records, tick windows, and raw hashes from source raw files; compare with r4.
2. Determine whether current tick samples demonstrate equal simulation progress at the scene snapshots. If not, explain why and specify the smallest falsifiable next probe without overwriting existing raw.
3. Record middle decision `PASS` or `HOLD` and the exact next work scope. Keep B' HOLD and do not treat this as G1 milestone approval.
