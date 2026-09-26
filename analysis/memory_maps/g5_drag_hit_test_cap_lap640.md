# G5 drag hit-test cap — lap 640 runtime attribution

- Protected source: `Syw2plus/syw2plus_original.exe`, SHA256
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
- Candidate before this change: `3877194855f54a8b63ea064a6be9f405485bffcb98286198f9a3f5a785459757`.
- Fresh isolated candidate runs used `tools.runtime_env`/private Wine prefix/Xvfb
  at 1600×1200, PS3, owner0 type2×55 dense fixture around slot1198.

## Runtime chain

The read-only gdb trace was armed before the drag and observed one drag call:

`0x0041E03B → call 0x004384B0 → 0x0041E040`.

At `0x004384B0` entry the seven stack arguments were:

`arg1=0x31f83c`, `arg2=0x31f81c`, `arg3=0x46fed8`, `arg4=0x10f8`,
`arg5=0x158`, `arg6=0x129c`, `arg7=0`.

At return, `arg1` held the caller-owned output list: 20 non-zero entries followed
by zero at entry 21. `arg2` held the caller-owned count and contained `20`.
The candidate reader still observed selection `20`, movement `20`, and process
exit `2` (`FAIL_SELECTION_CAP`).

The same run hit `0x0043877A` 26 times inside the append helper. The trace showed
`EAX=0..20`, `EBP=0x0031f81c`, and at the final six calls `EAX=20` while the
instruction compared `AX` against literal `0x14`. This is the runtime-confirmed
upstream cap reached from `FUN_004384B0`; it is not the relocated consumer's
post-processing loop.

## Candidate edit

The minimum candidate edit is the exact four-byte instruction replacement:

`VA 0x0043877A: 66 3d 14 00 → 66 3d 32 00`.

The replacement preserves instruction length and is guarded by old-byte matching.
The relocated 50-entry caller/consumer frame from the prior candidate remains in
place. The new candidate SHA is recorded by the patch builder and probe contract;
the protected source and reference repository remain unchanged.
