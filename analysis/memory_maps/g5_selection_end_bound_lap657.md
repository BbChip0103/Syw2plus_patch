# G5 selection storage end bound — lap 657 static attribution

- Protected source: `syw2plus_original.exe`, SHA256
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
- Candidate inspected: `6f6a4f859be4b2281ec2014e817b7692adf2d04226b0ac14b3ac32ac06f4e091` (lap655).

## Stock layout

| VA | Meaning |
|---|---|
| `0x00899024` | selection count (dword) |
| `0x00899028` | entry 0 (dword handle: low word slot, high word aux) |
| `0x00899078` | exclusive end = `0x00899028 + 20*4` |

`0x00899078` is referenced exactly 14 times (all loop-end compares), matching
`END_SITES` in `patches/selection/g5_selection_cap50_v1.py`.

## Defect in candidate

The builder maps the end to `SELECTION_BASE + SELECTION_BYTES` = `0x0108C0C8`,
but entries start at `SELECTION_BASE + 4`, so every relocated loop covers only
49 entries. The correct exclusive end is `SELECTION_BASE + 4 + 50*4` =
`0x0108C0CC` (still below `CONTROL_GROUP_BASE` `0x0108C100`).

Writer affected: `FUN_00412D90` add path `0x412E3C..0x412E57` (free-slot scan,
`jge 0x412E73` when full) still sets the unit selected byte and returns 1, so a
50th hit-test result is dropped from storage. Reached from consumer
`FUN_0041DC40` `0x41E1C9..0x41E1E6` via `0x40F7D0`.

Hit-test append cap `0x0043877A cmp ax,0x32` is correct (count 0..49 accepted).
Runtime match: lap653–655 selection 49/56 = 56 − 6 (hit-test cap) − 1 (storage bound).
