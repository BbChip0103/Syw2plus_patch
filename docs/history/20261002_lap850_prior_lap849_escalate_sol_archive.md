# lap849 P3→P4 stage-boundary handoff — middle review required

Stop condition: P3 performance gate still FAILS after the three fresh post-repair pairs. Do not declare G1 complete or start P4.

Work record: `docs/history/laps/20261002_lap849_work_g1_w70_p3_fixed_window_bbox_repair.md`
Current queue: `docs/STATUS.md`
Artifacts: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/lap849_perf_pair5/`, `lap849_perf_pair6/`, `lap849_perf_pair7/`

Next middle session:
1. Independently verify the three `perf_window_meta`/histogram pairs, sim tick monotonic windows, original/save SHA, source unchanged, cleanup and candidate Scale2x parity.
2. Confirm bbox parity and the measured result: baseline ≈20Hz; candidate 10.10–10.35Hz (−48.25% to −49.50%); present p95 delta +9ms to +11ms. Tick criterion is ≥95%; it is not met.
3. Review residual cost evidence: primitive re-invoke 16.78–17.17s per 20s window; 8.3k–8.6k calls; 322–333 identity-cache refreshes; 164.8M–170.1M Scale2x blocks. Decide/authorize one bounded work-tier profiling or cache optimization slice. Hash/compare/copy/Scale2x build time has not yet been separated.

Do not change the threshold, promote old P3 results, or begin P4. Input comparison remains HOLD; minimap is original-parity UNKNOWN and production remains UNKNOWN.
