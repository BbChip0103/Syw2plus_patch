# lap850 P3→P4 stage-boundary — elevated middle decision required

Stop condition: P3 performance gate still FAILS after the three fresh post-repair pairs. Do not declare G1 complete or start P4.

Independent review: `docs/history/laps/20261002_lap850_middle_g1_p3_fixed_window_review_escalate.md`
Work record: `docs/history/laps/20261002_lap849_work_g1_w70_p3_fixed_window_bbox_repair.md`
Current queue: `docs/STATUS.md`
Artifacts: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/lap849_perf_pair5/`, `lap849_perf_pair6/`, `lap849_perf_pair7/`

Confirmed: all 3 pair/build40 input/DLL/original/save/raw/capture hashes match; raw endpoint rate and full histogram reproduce FAIL (ratio 0.504999–0.517499; p95 delta +9/+10/+11ms). Scale2x raw partial PASS is retained.
Review artifact: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/lap850_middle_review/review.json`, SHA256 `af21055ab0ddf73093d7d5971446cf648fdecd563c626ffdac1b2f978574e32a`.

Elevated middle must assess and approve one bounded work-tier profiling/repair slice described in the review:
1. Reinvoke timing is inclusive; distinguish scratch/original/hash+lookup/compare+copy/HD build/compose, with writer/size/full-frame/cache outcome counts. No sole bottleneck is proven.
2. Intermediate state samples were not persisted; add raw tick/PS3/monotonic window samples in work tier. Post-bbox repeated capture SHA is not alone a pre/post repair oracle.
3. Work must implement/probe immediately after scope decision, preserve content invalidation/full-key negative fail-closed and use fresh 3-pair rate≥0.95/p95≤baseline+16ms. No extra ordinary middle narrative lap.

This ordinary middle session did not approve a plan, implement a repair, run fresh Fast/runtime, or cross a milestone. User stage-boundary stop condition requires this handoff and session termination. Prior marker is preserved byte-exact in `docs/history/20261002_lap850_prior_lap849_escalate_sol_archive.md`.

Do not change the threshold, promote old P3 results, or begin P4. Input comparison remains HOLD; minimap is original-parity UNKNOWN and production remains UNKNOWN.
