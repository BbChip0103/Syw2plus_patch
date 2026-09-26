# Direct G2 bug hunt — no-bug round 1/3: high-slot control group

User stop rule: three consecutive **meaningful** reviews without a newly confirmed product bug. Prior portrait review found one confirmed bug, so this starts at 0; this round tests a distinct hotkey/control-group path. It does not approve/release the G2 candidate or supersede G5's STATUS queue.

## Hypothesis and contract

A globally high-slot worker may be selectable/movable yet fail `Ctrl+1` group store or `1` recall because the original group array is 10×20 DWORD identities and its validation/selection path may use an old pool boundary. Before running, success was fixed as: (1) actual PS3 worker selection; (2) group-1 count=1 and stored internal ID equals selected unit ID; (3) deliberate deselection=0; (4) `1` selects the identical slot again; (5) same input path works on the pinned ESL2606 original control. Input is real X11 key events; no in-process unit or ledger writes.

## Byte/address evidence

Reference and corrected private probe EXE share the `0x0041D4E9` `lea ecx,[edx*4+0x9570f4]` call setup for `FUN_00445CD0` (group store). Group records start at owner0 `0x009570F4+0x16`, group1 first DWORD at `+0x50`; group1 count is at `0x009570F4+0x336+2`. `FUN_00445E30` recall validates each stored slot through `FUN_00416F40`. All private probe binaries were separate copies inside full isolated game copies; manifest `game/syw2plus_original.exe` remained stock SHA, and JSON `source_sha256` names the launched probe EXE.

## Runs and verdict

- One first-pass probe read the group count from `0x00956770` (PlayerStruct head) instead of group substructure `0x009570F4`, reporting `GROUP_FAIL` in **both** original and candidate, even though both recalled the worker. This was a harness-address error, not a product failure. Raw preserved under `local/runtime/g2_group_{original,fixed}/`.
- Corrected probe script: `../temp/Syw2plus_patch/g2_portrait_regression/20260925_direct_user_report/high_slot_control_group_probe.py`. Fresh separate runs under `local/runtime/g2_group_v2_{original,fixed}/`; both report `GROUP_PASS`, cleanup true.
- Original: selected slot1198; stored group1 count1/ID132270; after empty-ground deselect count0; `1` recalled slot1198.
- Corrected private ESL candidate SHA `ce3465e7…9ec20c9ac`: selected slot4091; stored group1 count1/ID135163; after deselect count0; `1` recalled slot4091.

**No new bug found in this axis. Consecutive no-bug count: 1/3.** This one-unit, one-group early-game test does not prove 20-unit group capacity, destroyed/reused identity handling, group persistence across save/load, eight-player behavior or multiplayer sync. Next independent review should target a different high-slot lifecycle/user path rather than counting another phrasing of this same result.
