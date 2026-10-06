lap: 847
date: 2026-10-02 KST
role: middle
status: RAW_PERFORMANCE_EVIDENCE_CONFLICT
target: G1 W70 P3 gate HOLD; P4 transition prohibited

User stop/escalation condition applies: prior performance PASS interpretation conflicts with actual raw simulation counters.
Detailed evidence and explicit work-tier handoff:
docs/history/laps/20261002_lap847_middle_g1_w70_p3_performance_conflict_escalate.md
Independent recomputation:
/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/lap847_middle_review/recompute.py
/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/lap847_middle_review/review.json
review_sha256=c544f3130d8e293c8485bb1919283728e60f3f95d5a0b9c3110505928f366cdb

Promoted middle must verify:
1. direct_draw_trace.c reads game_tick from 0x9B5210, while runtime_driver.state reads actual simulation tick from 0x8924B8.
2. Protected-original 0x42329F loads _imeGetTime IAT 0x4E5294; 0x42334A calls it and 0x423352 stores its clock return at 0x9B5210.
3. Existing perf4/5/6 post-load action snapshots yield candidate actual tick-rate deltas -38.873199/-38.500290/-39.712340 percent. These diagnostic windows have unequal action/capture costs and wall-clock timestamps; request a controlled monotonic fixed-window measurement, not another elapsed-clock-span PASS.
4. Baseline primary timing histogram caps at2048, candidate counts255/258/248; reported +15/+14/+14ms p95 deltas are not independently reconstructed same-window PS3 quantiles.
5. Preserve source-matched Scale2x/capture/selection/empty/drag partial evidence and minimap ORIGINAL_PARITY_UNKNOWN. Product minimap/production stay UNKNOWN/HOLD.

Confirm HOLD and hand the bounded measurement repair to work tier: actual sim counter plus monotonic elapsed seconds in load-free PS3 windows, comparable PS3 present timing samples, then three fresh pairs with original -5%/+16ms thresholds. Work tier profiles and repairs any reproduced slowdown; middle does not implement game changes. No P4/milestone closure until valid performance evidence is independently accepted. The current single queue is docs/STATUS.md.

Previous lap844 marker preserved byte-exact in docs/history/20261002_lap847_prior_lap844_escalate_sol_archive.md.
No game code/binary changes, no new game run, no original/reference writes, no commits. Final make check is FAST only; final outcome belongs to STATUS and logs/gates/lap847-middle-fast.log/.exit.
