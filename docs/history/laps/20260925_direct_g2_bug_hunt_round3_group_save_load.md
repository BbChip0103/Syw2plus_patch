# Direct G2 bug hunt — no-bug round 3/3: high-slot control group survives save/load

This is the third consecutive bounded review without a newly confirmed product bug after the portrait-navigation defect was fixed. It checks a persistence/identity path not established by round 1's live-session group hotkeys or round 2's producer queue persistence. It is not a claim of general bug absence or G2 milestone acceptance.

## Fixture and acceptance criteria

- ESL2606 original SHA `4a03895d8e6690080714fab7e851c3a0e9d44b7cac47fed78fc21a2f5210c6f8`; corrected private owner500/pool4092 candidate SHA `ce3465e764af30da83d0ad19b1dd9a5a8e72f357dfa2da078acef229ec20c9ac`.
- Distinct full private game copies, prefixes and Xvfb displays; real clicks and `Ctrl+1`/`1` keys; no in-process state writes. One owner0 worker at the highest occupied startup slot is selected and stored in group 1, then saved to private slot001, reloaded, deselected and recalled.
- Check selected high slot, group count 1, same stored internal ID after load, and same unit slot selected by post-load hotkey. Observe original as control.

## Runs and verdict

- Script `../temp/Syw2plus_patch/g2_portrait_regression/20260925_direct_user_report/high_slot_group_save_load_probe.py`.
- Original `local/runtime/g2_group_save_original/*/output/g2_ingame_probe.json`: `GROUP_SAVE_LOAD_PASS`, all six checks true, cleanup true. Selected/recalled slot1198; stored ID132270; post-load group count1 and ID132270.
- Candidate `local/runtime/g2_group_save_fixed/*/output/g2_ingame_probe.json`: `GROUP_SAVE_LOAD_PASS`, all six checks true, cleanup true. Selected/recalled slot4091; stored ID135163; post-load group count1 and ID135163.

**No new bug found. Consecutive no-bug count: 3/3.** The explicit stop rule is met for this bounded hunt. Remaining untested risks include destroyed/reused high-slot identity, 20-member groups, natural recruited hero portraits, long eight-owner/5000-supply play, and multiplayer sync. The corrected candidate remains private; the older delivered trial remains held.
