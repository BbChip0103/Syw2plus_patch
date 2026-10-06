# G1 P5-T independent review handoff — lap923 work

P5-T final-source runtime work completed. This is a regular next-tier review, not G1 or user milestone approval.

## Review targets

- Independently verify original EXE SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, save006 SHA `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`, the final probe/tests SHA recorded in `docs/history/laps/20261004_lap923_work_g1_p5t_current_source_pairs.md`, build inputs, candidate executable and DLL.
- Recompute GREEN/B′1/B′2 pair gates from the six final raw pair JSONs and inspect the paired PNGs. Confirm five snapshot ticks against lap888, exact input ticks, camera action, 30-present coverage and cleanup.
- Recompute C1–C3 ratios and p95 deltas from raw histograms/windows; do not infer runtime proof from the full Fast test.
- Review the trace at fixed camera `[158,101]`: late effective p50 is about 395.5k/480k, while last-20 stale p50 is about 74.9k. The tinted writer counters show `rle_tinted` covered 11.4k–13.0k pixels and `rle_tinted_clip` covered 0. Decide whether stale reduction is supported; do not claim it from current aggregate values alone.
- Confirm semantic input comparison remains HOLD and G1 remains HOLD. Open issues include HD coverage ≥90%, input-effect evidence, GDI, second scene, final input, and user milestone approval.

## Raw locations

- Final scroll pairs: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261004_063623_lap923_p5t_{green_final,bprime1_final,bprime2_final}/pair-result.json`
- Final C pairs: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261004_062209_lap923_p5t_{c1,c2,c3}/pair-result.json`
- Detailed run chronology, failed pre-fix attempts and hashes: `docs/history/laps/20261004_lap923_work_g1_p5t_current_source_pairs.md`

Independently classify P5-T as accepted, partial, or held and update STATUS. Preserve all existing raw, thresholds and historical failed attempts.
