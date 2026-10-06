# G1 lap941 minimap input pair — independent middle review

## Scope

Independently review the final lap941 saved-scene pair for the narrow minimap command effect only. Do not treat camera movement, production, or overall G1 as passed. The earlier runtime from `20261004_lap941_minimap_pair` is superseded by the final source-matched pair below and remains preserved.

## Frozen evidence

- Pair: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261004_lap941_minimap_pair_final/pair-result.json`, SHA256 `9c2c1592a9ec67f852d329cfa21617f30a0a1e3d0ca12941acab7f69a1569c15`.
- Lane result/raw/PNG/log: `baseline/` and `candidate/` below `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261004_lap941_minimap_pair_final/`.
- Fixture/source: original EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; non-synthetic save006 `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`.
- Baseline/candidate minimap PNGs are 800×600 / 1600×1200 and copied to the sibling shared `captures/` paths recorded in each lane's `probe-result.json`.

## Work result to challenge independently

Both lanes recorded the active drag selection `[124,140,151,170]`, all four as owner 0 with types `[98,13,111,16]`. A plain right-click at known center `(90,553)` changed all four units' raw `pending_xy` to the same values in both lanes: `[5767258,5767259,5832794,5963864]`; camera remained `[158,101]`. Gate `0x97597c` changed from `00000000` to diagnostic `01000000` and restored exactly to `00000000`. Minimap result and diagnostic parity are PASS. Pair-wide input status remains HOLD because the later HQ production selection is empty; production, camera recentering, and minimap camera movement are UNKNOWN/not passed.

## Review actions

Recompute the pair's minimap selection/owner/type/pending-coordinate changes from the lane JSON, verify source/save identity and exact gate restore, check both cleanup records and the PNG hashes/dimensions against the copied captures. Report PASS(partial) or HOLD with the specific discrepancy. Preserve G1 HOLD and hand off the next STATUS item; no milestone or user approval is implied.
