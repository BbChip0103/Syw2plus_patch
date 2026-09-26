# Direct G2 bug hunt — no-bug round 2/3: high-slot production across save/load

User stop rule: three consecutive meaningful reviews without a newly confirmed product bug. Round 1 (high-slot control group) found no bug; this independent round checks a high-slot producer, a mid-production save/load, and actual unit creation. This is not a G2 milestone approval or a G5 queue change.

## Fixture and acceptance criteria

- Pinned ESL2606 original SHA `4a03895d8e6690080714fab7e851c3a0e9d44b7cac47fed78fc21a2f5210c6f8`; private corrected G2 owner500/pool4092 candidate SHA `ce3465e764af30da83d0ad19b1dd9a5a8e72f357dfa2da078acef229ec20c9ac`.
- Separate full private game copies, Wine prefixes and Xvfb displays. Real X11 clicks select the last-slot HQ and order production. No in-process game-state writes. Save slot001 belongs to each private copy.
- Check last-slot HQ selection, resource debit plus nonzero reservation while unit count is unchanged, save file creation, loaded tick earlier than a deliberate 300+ tick later point, restored pending state, and eventual count/used increase with reservation cleared.

## Runs

- Script: `../temp/Syw2plus_patch/g2_portrait_regression/20260925_direct_user_report/high_slot_pending_production_roundtrip_probe.py`.
- First candidate run `local/runtime/g2_pending_production_fixed/` reported `PENDING_PRODUCTION_ROUNDTRIP_FAIL` only because the harness required `loaded_tick <= saved_tick`. Saving consumed about ten ticks after the post-save tick sample; after load the tick was 139 vs sampled 129, but far below pre-load 431. Its reservation and actual production checks passed. This is a harness false alarm, not a product defect.
- Corrected acceptance check requires both saved and loaded ticks to precede the deliberate pre-load 300+ tick point. Fresh original `local/runtime/g2_pending_production_original/*/output/g2_ingame_probe.json`: all five checks pass, HQ slot1199, ticks saved396/pre-load700/loaded406, count2→3, used20→30, reserved10→0, cleanup true.
- Fresh candidate `local/runtime/g2_pending_production_fixed_v2/*/output/g2_ingame_probe.json`: all five checks pass, HQ slot4092, ticks saved397/pre-load699/loaded407, count2→3, used20→30, reserved10→0, cleanup true. Candidate owner cap500; original owner cap250.

**No new product bug found. Consecutive no-bug count: 2/3.** This tests one producer and one queue item in solo play, not sustained 8-owner 5000-supply or network synchronization.
