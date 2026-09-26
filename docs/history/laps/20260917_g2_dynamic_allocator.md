# 2026-09-17 — G2 dynamic transplanted allocator slice

## Scope

This bounded fixture executes the SHA-pinned original `FUN_00442FA0` 61-byte
machine-code slice after copying it to dynamically allocated executable memory.
It is not execution at the original game code address and is not original-game
runtime evidence. The fixture does not load the game, spawn units, consume IDs,
or exercise save/LAN paths.

The original bytes are read from file offset `0x42fa0` of the pinned PE32:
`b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
Only three operands are patched for each dynamic pair: age start, the
existence-vs-age displacement, and age exclusive end. All other bytes and
internal control flow remain byte-identical. Dynamic addresses are rejected if
they cross the signed-`jl` boundary used by the original endpoint loop.

## Cases and evidence policy

Guarded dynamic existence/age copies cover capacities 1200, 1201, and 4001.
Each invocation checks both arrays' full state and canaries. The independent
expected model verifies empty/single/multiple free slots, equal-age later-slot
ties, occupied-slot preservation, slot0 protection, 1199→1200 and 3999→4000
boundaries, exhaustion, `0x7fff→0x8000` signed-short wrap, negative ages, and
all-negative no-eligible return 0. The allocator only increments free ages;
the caller owns occupancy and must mark a returned slot.

The bulk sentinel is standalone fixture memory only; it is not proof that the
original game bulk state is safe. Activation remains `NO-GO` and this result
does not close relocation, save, LAN, or product feasibility obligations.

## Owned isolated run (2026-09-17 15:26 KST)

The approved standalone fixture run completed with return code 0 in 18.623800038
seconds. Evidence is retained at
`/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/g2_capacity/20260917_dynamic_allocator/owned_run_20260917_152546/owned_run_evidence.json`.
It reports 12 passing cases across capacities 1200, 1201, and 4001, full-state
comparison, caller-owned occupancy, and `activation: NO-GO`. The fixture SHA was
`8e3dcc536df1ae56441cea1e36defa5dc33fb316c9ba24367551c03fe30b06c1` before and
after; the source pin was
`0272e2e06d1e9ee54a3123738c7a74950041b1e686b35d0057538954d24f59cf`; the
original profile SHA was
`b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`. The
fresh absolute prefix had no residual processes or cleanup errors. This is
transplanted machine-code evidence only, not original-game lifecycle, save,
LAN, or activation evidence.
