# ESL2606 G2 idle-hero portrait → producer lookup (2026-09-25)

## Scope and identities

- Normal ESL2606 reference SHA256 `4a03895d8e6690080714fab7e851c3a0e9d44b7cac47fed78fc21a2f5210c6f8` (read only).
- Delivered-but-held G2 owner500/pool4092 candidate SHA256 `af7880d28e16c177e28a2d7cb9dc17307e7f152732443818088ac28b342ba3f3`.
- Private three-instruction correction SHA256 `ce3465e764af30da83d0ad19b1dd9a5a8e72f357dfa2da078acef229ec20c9ac`; **not released**.
- PE32 `.text` VA/file mapping at these sites: `file_offset = VA - 0x00400000`.

## Call and bytes

`FUN_0049B2C0` registers idle recruitable-hero portrait callback `LAB_0049B2A0`. Its `0x0049B2B3` call enters `FUN_0049B9F0`; at `0x0049BA0E` (`e8 8d c9 f7 ff`) this calls producer lookup `FUN_004183A0`. On success, `0x0049BA16` validates the unit, `0x0049BA28/37` obtains coordinates, and `0x0049BA45` requests camera movement via `FUN_004A3D80`. The latter call path is byte-identical in reference and held candidate. The defect is upstream in the producer search:

| VA | Held bytes | Meaning | Corrected bytes |
|---|---|---|---|
| `0x004183A8` | `b9 b0 04 00 00` | initial modulo divisor 1200 | `b9 fd 0f 00 00` (4093) |
| `0x004183BE` | `b9 b0 04 00 00` | scan modulo divisor 1200 | `b9 fd 0f 00 00` (4093) |
| `0x00418425` | `66 81 fb b0 04` | scan limit 1200 | `66 81 fb fd 0f` (4093) |

The corrected candidate still has 4092 *usable* slots, because slot 0 is reserved and all three operands need the total 4093-slot geometry. `FUN_004183A0`'s UnitStruct/existence absolute references were already relocated; only the search limit was stale. These exact instructions are guarded in `patches/population/g2_esl2606_pool4092_owner500.py`, with preimage/non-overlap and copy-only/restore tests. Unrelated occurrences of `1200` must not be globally replaced.

## Fresh runtime comparison, explicit fixture

Raw runs under `local/runtime/g2_portrait_synthetic_{old,fixed}/`, isolated full game copies and separate Wine prefixes/displays; screenshots under shared `temp/Syw2plus_patch/captures/`. `runtime_env.prepare` leaves `game/syw2plus_original.exe` at the pinned **stock** SHA `b56986…a8ac`; the launched `game/portrait_probe.exe` is a separately copied old/fixed ESL probe EXE, and each JSON `source_sha256` names that probe, not the manifest's stock EXE. Both runs loaded the same stock `save006.dat`, which naturally displays two idle recruitable portraits. A private-process **synthetic high-slot fixture** copied the actually selected type-53 producer from slot 887 to slot 4092, changed its internal ID low word to 4092, copied existence/age, and temporarily cleared existence of the five matching low-slot producers `[887,892,964,1025,1045]`. Original EXE/save/game input bytes were not changed. Before click, camera was `[49,159]`, visible portrait at `(366,565)`.

- Held candidate click: camera `[49,159]` → `[49,159]` (no jump), process remained PS3; raw `local/runtime/g2_portrait_synthetic_old/*/output/portrait_probe.json`.
- Corrected private candidate click: camera `[49,159]` → `[158,95]`, PS3; raw `local/runtime/g2_portrait_synthetic_fixed/*/output/portrait_probe.json`.
- Three clean runs of unmodified `save006.dat` on reference, held candidate and corrected candidate each made both portrait clicks jump. This is a **low-slot control**, not proof that the held candidate works when the producer is above 1199.
- Fresh corrected **private probe EXE** new-game smoke passed worker selection/move, HQ selection/production, ESC and cleanup; raw `local/runtime/g2_portraitfix_smoke/*/output/g2_ingame_probe.json`.
- A separate fresh corrected private probe EXE new game saved slot 1 **inside its private game copy**, then loaded that file in the same process. High active slots 4089–4092 retained identical existence values and internal IDs before/after; raw `local/runtime/g2_portrait_roundtrip/*/output/g2_ingame_probe.json` (`ROUNDTRIP_PASS`, cleanup true). This is a four-unit early-game roundtrip, not a 500-owner cap or long-soak proof.

Thus the 1200 scan is a confirmed *high-slot portrait navigation* regression under the controlled fixture. A naturally recruited high-slot hero click, long play, eight simultaneous players, save/reload roundtrip of a high-slot **recruitable producer** and LAN remain untested. No bug-free or release claim follows.

## Audit false positives / unresolved

Five `0x0089A388` indexed references at `0x0043E887`, `0x0047F447`, `0x0047F8DE`, `0x0049B373`, `0x004A7F3F` were initially flagged as old `unit_age` end. Decompilation shows their index is `unit_kind + owner*200` (or related type count), not `slot`; `0x0089A388` is also the start of a distinct, fixed-size 8×200 WORD per-type count table ending at `0x0089B008`. **Do not relocate these five as age-array bugs.**

`0x00422DC7` still loops 1200 pool records, but its callee chain `FUN_0048AFF0` → `FUN_004119F0` is a no-op in this binary. `0x004A3222` clears the old existence/age arrays, but private fresh new-game→`save006.dat` load left high-slot existence zero and high-slot unit IDs zero; a same-process restart after a synthetic unused age-cell sentinel `0x4444` cleared that sentinel and re-entered PS3. These narrow observations do **not** prove that `0x004A3222` itself handles relocated arrays or that every reset path is safe; no writer trace was collected. The raw 1200 constants alone are not confirmed user-visible defects. The first load probe's `RESET_FAIL` was a harness false positive: it treated nonzero dead-slot age values (2) as live units despite `existence=0` and `ID=0`. The first restart probe's `RESET_FAIL` was another harness failure: it stopped at the confirmation dialog (PS23), without actually restarting. Neither is product-failure evidence.

A bounded Capstone `.text` immediate-1200 scan of the corrected probe found 23 remaining instructions. Many `push 0x4B0` sites in `FUN_0049BEB0` are unit-type metadata arguments; several in `FUN_004A86D0` are `FUN_004A8100` graphic/UI arguments. `0x0043EE37` is the distinct 1200 defensive owner-roster bound (the ESL500 edit seeds the per-owner roster policy, not this check), and `0x00444F8A` is a separate 1200-entry table/config parse. This scan does not prove all indirect bounds safe, but it rules out treating every literal 1200 as a pool limit.
