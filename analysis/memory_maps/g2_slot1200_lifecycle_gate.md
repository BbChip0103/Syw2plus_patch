# G2 slot-1200 lifecycle gate (static closure)

**Status: `NO-GO` for activation.** This is a bounded static gate for the
slot-1200 path, not a patch proposal, game run, or claim that the dynamic
allocator fixture proves game behavior. Evidence is the protected original
Ghidra output under the sibling tree
`../Syw2plus_re/analysis/ghidra_output/` plus raw PE32 disassembly of the same
pinned original; all `analysis/ghidra_output/...` citations below refer to that
sibling protected tree, not a patch-local directory. The protected original
binary remains unchanged. This report was initially created at the sibling
`Syw2plus_re` path and then root-relocated here; that documented path repair is
archived at
`/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/g2_capacity/20260917_dynamic_allocator/reference_doc_path_repair/repair.json`.

## Reachable create/register path

`FUN_00443190` (`0x443190`) is the observed creator: after its type gate and
counter update it calls `FUN_0048b000` (`analysis/ghidra_output/FUN_00443190.c:21-32`).
`FUN_0048b000` clears `0x1d6` dwords (`0x758` bytes), calls `FUN_00411A00`,
then calls `FUN_0047F8F0`, `FUN_0040E900`, `FUN_0048BC00`, `FUN_0048B210`, and
`FUN_0048DDD0` (`FUN_0048b000.c:14-19,63-69`). Thus a slot-1200 change is
already coupled to reset/initialization and these callees; the creator is not
an isolated pool write.

`FUN_0048BC00` is the registration edge (`FUN_0048bc00.c:5-30`, raw
`0x48bc00..0x48bd10`):

| state | original expression / fixup | observed operation |
|---|---|---|
| unit pool | `0x66b790 + slot * 0x758` | object was cleared by `FUN_0048B000`; removal uses the same byte stride (`FUN_00442FE0.c:14-15`) |
| existence | `0x8990c8 + slot * 2` | stores the unit type byte from `unit + 0x8d` into the existence word (raw `0x48BC4E` zero-extends the byte); zeroes on removal (`FUN_0048bc00.c:15`, `FUN_00442FE0.c:44-45`) |
| age | `0x899a28 + slot * 2` | register/removal reset to zero (`FUN_0048bc00.c:16`, `FUN_00442fe0.c:44-45`) |
| active list | `0x974fa8 + active_count * 2`, count `0x975908` | writes slot, stores active index at unit `+0x2a0`, increments count (`FUN_0048bc00.c:17-19`) |
| category A | `0x89b008 + count * 4`, count/end `0x89c2c8` | appends a dword slot/full-ID-like value (`FUN_0048bc00.c:20-23`) |
| category B | `0x89c2ca + count * 4`, count/end `0x89d58a` | appends a dword slot/full-ID-like value (`FUN_0048bc00.c:24-27`) |
| owner roster | `player + 0xd4a + owner_count * 4`, count `+0x200a` | `FUN_0043EE30` appends slot ID and updates used/building counts (`FUN_0043ee30.c:7-20`) |
| reset/owner/map | `FUN_0043EE30(slot)` and `FUN_004A3760(...)` | owner roster and spatial/map registration (`FUN_0048bc00.c:5,28`) |

The raw instruction at **`0x48BCAE`** is `89 14 8d 08 b0 89 00`,
`mov [0x89b008 + ecx*4], edx`. The decompiler's apparent scale-2 form is
wrong; relocation must use the raw encoded scale 4. Raw disassembly likewise
confirms the active write at `0x48BC7D`, category-B scale 4, and owner base
`0x956770` near `0x48BCF7`.

## Removal, reset, and one concrete consumer

`FUN_00442FE0` (`0x442fe0..0x443170`) is the removal path. It checks
existence, derives the pool record, removes map/spatial state, swap-removes the
active list, decrements active count, removes category entries, calls
`FUN_0043EEC0(owner, slot)`, and resets existence/age
(`FUN_00442fe0.c:11-45`). `FUN_0043EEC0` shifts the owner roster and decrements
owner count/used/building fields (`FUN_0043eec0.c:17-42`). `FUN_00443170` then
calls removal for `i=0..0x4af` (`FUN_00443170.c:4-13`), an explicit 1200-slot
bound. Map and category cleanup further reach `FUN_0048C3E0`, `FUN_004A37B0`,
`FUN_004A3620`, and `FUN_004A3690` (callgraph and `FUN_00442FE0.c:16-43`).

One actual full-ID consumer is `FUN_004B1830` (`0x4b1830`): it reads the
four-byte owner-roster entry at `player + 0xd4a + i*4`, passes that untruncated
value to `FUN_00417010`, then uses its low-word slot to index the unit pool
and may call `FUN_0043F4C0` and `FUN_004AEDE0`
(`FUN_004b1830.c:15-45`). This establishes a reachable full-ID-shaped call
site, but not the complete ID namespace or its network meaning. A concrete
normal-game active/tick/render consumer is `FUN_004332F0`: its active loop
reads `active[i]`, checks `existence[slot]`, derives the unit base with the
`0x758`-byte pool stride, and reads the **WORD command** at unit `+0x290`
(`DAT_0066BA20[slot*0x3ac]` in Ghidra's WORD indexing, where `0x3ac` WORDs
are `0x758` bytes). It compares command states 7/16 and then calls
`FUN_00409360`, `FUN_0048B3C0`, and `FUN_004786D0`
(`FUN_004332f0.c:190-201`; raw load at `0x433947` is
`mov cx, word [eax+0x66ba20]`). This is the existing unit command field,
not a new independent type array; the type byte at `unit+0x8d` and its
`0x394`-record table are separate. Its category-A loop likewise
consumes the list and count (`FUN_004332f0.c:360-369`), while registration's
`FUN_004A3760` is the observed spatial/map initializer. These prove reachable
consumer shapes, not that every consumer or the semantic meaning of every
32-bit list value is closed. Other active/category consumers include
`FUN_00431AB0` and `FUN_0043D910`; active-list consumers also occur in
`FUN_00444770`, `FUN_004447F0`, `FUN_00444870`, `FUN_004448E0`, and
`FUN_0048F250`.

## Save/load and hard-boundary blockers

`FUN_00440C20` bulk-saves from `0x892410` and then calls `FUN_0040F4B0`
(`FUN_00440c20.c:66-69`); `FUN_00440FF0` bulk-loads from the same boundary and
calls `FUN_0040F4F0` (`FUN_00440ff0.c:81-84`). The roster save/load loops in
`FUN_0040F4B0.c:5-19` and `FUN_0040f4f0.c:5-28` iterate existence entries up to
`0x899a28`, so a new slot range needs save ordering/version semantics, not only
an allocator bound edit. The owner append rejects counts beyond `0x4af`
(`FUN_0043ee30.c:7-13`); `FUN_0043EDA0` also gates owner count/capacity and calls
the selector (`FUN_0043eda0.c:8-22`). These are direct lifecycle blockers.

## Closure decision

**Can implement now:** preserve the exact known raw operands and function-role
map in a relocation manifest; retain the dynamic fixture as transplanted
machine-code evidence only. The static data-flow above identifies the direct
unit/existence/age/active/category/owner/reset fixups and a real consumer.

**Cannot activate:** the normal-game closure is incomplete. The creator's
initializers, owner roster/full-ID semantics, map/spatial and category swap
removal, all active/category tick/render consumers, bulk save/load version and
order, and LAN ID/protocol/rejection behavior are not closed. The observed
1200-slot destroy loop and owner cap are additional hard bounds. No proof yet
covers create→active→consume→remove→reuse for slot 1200 in the game, and no
single static slice proves all 1491 historical candidates. Therefore this gate
retains `activation: NO-GO`; it does not declare the broader G2 relocation
impossible.

### Evidence policy

The owned run recorded in
`docs/history/laps/20260917_g2_dynamic_allocator.md` is 12 passing standalone
cases at capacities 1200/1201/4001, but explicitly says “transplanted machine
code; not game.” It cannot discharge the lifecycle, save, LAN, or activation
obligations above.


## 2026-09-17 17:24 KST bounded closure / correction

The previous registration description calling **4A3760 spatial/map initialization
was too strong**. It increments an owner×200+TYPE WORD counter at
bulk-this+7F78; 4A37B0 decrements it. Neither produces the spatial map WORD.
Raw local closure is recorded in the external
g2_capacity/20260917_six_arena_closure directory under the agreed temp root:

- 4332F0 active-command loop433918..43397F: six paired disp32 fixups,
  signed WORD list/count, slot*1880, command field+290, same body pointer to
  409360/48B3C0/4786D0. root_active_loop_recipe.json.
- Its category-A loop433EC3..433F15: five paired fixups, DWORD entry stride4
  but signed lowWORD slot read and WORD count. root_category_a_loop_recipe.json.
- 48DDD0→412A30→47B5F0 neighbor-aura edge: signed map WORD→416FD0→
  slot*1880; all33 neighbor unit-field/base operands plus416FD0's3
  existence/HP/active operands translated as a LOCAL36-fixup unit.
  496380 reads TYPE metadata; 413CB0 heals the corrected body pointer relative
  to+B4/+120. Sol independently checked all36 oldbytes/file-offset/encoding
  pairs. root_neighbor_aura_recipe.json. No complete consumer closure claim.

The actual spatial-map producer is48BD10: raw48BE4C→48BE53 and
48C07F→48C086 copy body's lowWORD fullID+29C into the B43728 map;
48BF4A→48BF51 and48C278→48C27F do likewise for B4372C.
Map x/y bounds and row-index calculation are separate from pool-slot bounds.
4368D0 reads B4372C; it does not impose1200 or validate the returned slot.

A FIRST concrete remaining normal-AI consumer is periodic48DDD0→415020:
it scans the **169 sector buckets, each225 WORD entries** at943D0A and
WORD counts95661C. Producer4A4100 uses bulk-relative B18FA/C420C,
tests sector<169 and count<225, and silently skips insertion otherwise.
Reset4A40E0 clears169 WORD counts. Coordinate helpers40F5C0/40F5E0
themselves have slot-derived old pool fields+2A2/+2A4 requiring fixups.
Thus direct absolute pool-address inventories alone omit relevant
bulk-relative accesses; category swap-removal4A3620/4A3690 similarly uses
bulk-relative8BF8/9EB8/9EBA/B17A (old category lists/counters).

Whether225 is justified for every legal ground/air/special mix by occupancy,
or needs relocation/restriding with this product change, is **UNRESOLVED**.
This is not observed overflow/OOM or proof expansion is impossible.
The required full allowed-TYPE positive/zero-cost bounds are also UNKNOWN;
4001/9601 remain diagnostic arithmetic. The next implementation review must
close this reachable spatial-bucket unit, not generate another NO-GO emitter.
Raw: root_map_producer_queue_raw.txt and
root_sector_bucket_category_relative_raw.txt. No game/source/DLL changes.
