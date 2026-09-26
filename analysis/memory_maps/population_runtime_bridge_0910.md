# Original supply runtime probe bridge — 2026-09-10

Diagnostic instrumentation, not a shipping population patch. Original profile:
`Syw2plus/syw2plus_original.exe`, SHA256
`b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
Sources below are ORIGINAL Ghidra output, corroborated using pefile/Capstone.

## Execution boundary

`FUN_00423150.c:49–82` is the outer Windows message/game dispatch loop.
Its `imeGetTime` call at VA `0x42334A` has bytes `FF D6`, returning to
`0x42334C`, before program-state dispatch and outside unit traversal.
The private stub calls the probe only for this exact return address, on the
thread owning the largest visible current-process window, with recursion guard.
Other `_imeGetTime` callers MUST NOT execute probe requests. Explicit process
environment `SYW2_SUPPLY_PROBE=1` additionally enables this diagnostic.

## Allowed actions and verified addresses

* Train: cdecl `0x4AF5E0(internal_unit_id,type,1)`, bytes
  `53 66 8B 5C 24 0C 56 57`; original AI uses this route at
  `FUN_00406b00.c:48`, command table lookup and enqueue at
  `FUN_004af5e0.c:9–20`. Return 1 alone does NOT prove enqueue: no-match also
  returns 1. Observe actual reservation/progress/new unit.
* Save/load: cdecl `0x440C20(slot)` / `0x440FF0(slot)`, bytes respectively
  `8B 4C 24 04 81 EC 00 01` / `8B 4C 24 04 81 EC 04 01`.
  `FUN_00440a80` uses `%ssave\\save%d%02d.dat`: prefix at `0x9E8930`,
  category word at `0x66966C`, slot argument. The slot remains on the stack
  across the category getter and becomes the final wsprintf argument.
  Use ONLY a private game copy with private saves. Loading replaces current
  game state. The caller is before the next game dispatch, not inside a unit.
* Resource fixture: original thiscall setters `0x43ED60(owner,rice)` and
  `0x43ED80(owner,wood)` update normal fields and doubled shadow values
  (`FUN_0043eb70`/`FUN_0043eb90`). Set ONLY explicit used-supply word +0x200C;
  do not change supply cap, count, progress, AI flags, or production checks.

Player base `0x956770`, stride `0x3ABC`: rice +0x14, wood +0x18,
reserved +0x1C (int32); count +0x200A, used +0x200C, cap +0x2012 (int16).
Unit base `0x66B790`, stride `0x758`: type +0x8D (byte), owner +0x8E (byte),
HP +0xB4 (int32), internal ID +0x29C (int32), command +0x290 (int16),
progress +0x1F8 (int32), production type +0x320 (int32).
Existence words at `0x8990C8`, slots 1–1199. Logic tick `0x8924B8`;
program state word `0x4ED818`. These are original layout facts, not Plan C.

### Unit identity and coordinate offsets (lap281 static promotion)

The work-tier reader in `patches/population/runtime_driver.py` uses the following
named constants from `tools/runtime_env.py`:

| field | record offset | width / decode | slot-0 absolute address |
|---|---:|---|---:|
| `internal_id` | `+0x29C` | 4 bytes, little-endian signed int | `0x66BA2C` |
| `x` | `+0x2A2` | 2 bytes, little-endian signed WORD | `0x66BA32` |
| `y` | `+0x2A4` | 2 bytes, little-endian signed WORD | `0x66BA34` |

Static provenance was rechecked against the original PE32 SHA256
`b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` with:
`objdump -D -Mintel -j .text`. The original text contains 115 references to
`WORD PTR [reg+0x66BA32]` and 115 to `WORD PTR [reg+0x66BA34]`; representative
paired reads are `0x4069C7/0x4069D1` and `0x40815D/0x40816B`, with signed
`movsx` reads also present. Accessor `0x40F540` computes `slot*0x758` as
`eax*8` after `eax=slot*235` and reads `DWORD [eax*8+0x66BA2C]`; the adjacent
accessors at `0x40F5D0` and `0x40F5F0` read the x/y WORDs. This is static
layout provenance only; it does not establish runtime determinism or product
acceptance.

## Protocol and verification boundary

Build a PRIVATE copy of existing inmm stub sources using
`patches/population/build_runtime_bridge.py --out-dir /tmp/PRIVATE/build`.
No repository stub source or original DLL is replaced by the builder.
Start the isolated process with `SYW2_SUPPLY_PROBE=1`.

Atomically replace `C:\\supply_probe_request.txt` with eight unsigned decimal
integers: `id op owner slot type rice wood used` (nonzero increasing id).
Ops: 0 snapshot; 1 train; 2 save; 3 load; 4 fixture. Unused fields are zero.
Save/load slot range 0–99; train slot range 1–1199, type 0–199.
Wait for matching id in `C:\\supply_probe_result.json`; append-only results
also go to `C:\\supply_probe_log.jsonl`. Requests are consumed at most once
per process by monotonically increasing id. All actions require PS=3.

Result `ok` means request validation/execution succeeded, NOT production
success. `raw_return` is original function return; snapshots expose ledger,
live roster count and requested producer state. Fixtures deliberately make
the starting used-supply ledger synthetic. Any report must distinguish this
from a naturally accumulated army, uninstrumented play, and LAN correctness.

Static signature gates reject incompatible call targets. They are not an
entire-file identity proof: the runtime driver owns SHA256/patch provenance.
No full-game result is asserted by this document.

## Bounded coherent-army fixture (op 5)

This operation seeds 1–142 real type-5 units using original engine routines;
it does not train that unit and does not debit resources. This distinction
must remain explicit even when a later real training action reaches 5000.
Inputs use `type=5`, `rice=x`, `wood=y`, `used=count` (0 means 1); `slot`
is unused. Candidate search begins at x,y and advances row-major with wrap,
limited to one map traversal or 10000 candidates, whichever is smaller.
Each candidate uses the original placement validator; every spawn rechecks
reserved-supply headroom and the original cap/count gate. All are executed
within the same outer-loop callback, not by advancing game ticks.
Partial progress is explicit: `fixture_added` counts verified spawns and
`fixture_attempts` counts candidate checks. `ok=false` does NOT imply no
units were added. Do not retry without inspecting the updated roster.

Original `FUN_0042ecb0` is a thiscall terrain/footprint occupancy validator.
This map is `0xB3DDA8`: width/height offsets +0x8C/+0x8E resolve to
`0xB3DE34/36`; occupant grid +0x5980 resolves to `0xB43728`.
The normal HQ placement helper `FUN_004144a0` calls it for candidate positions.
Call `0x42ECB0(map,x,y,width,height,-1,-1,0,0)`: the last four arguments
describe a zero-sized excluded producer rectangle. It rejects occupied
cells and ground terrain flag mask `0x236A`, with full footprint bounds.
Prologue bytes: `83 EC 18 53 55 56 8B 74`.

The fixture is restricted to type 5, original runtime cost 35, positive small
footprint at `0x9B523E/40 + type*0x394`, and no building/naval/hero flags
(`0x9B524C + type*0x394` bits 2/4/8). It additionally respects existing
reserved supply before calling original `0x43EDA0(player,type,0)`.
Then cdecl `0x443190(type,allocatedSlot,x,y,1,100,owner)` runs original sprite
loading/spawn/registration (`FUN_00443190`, `FUN_0048b000`, `FUN_0048bc00`).
Prologue bytes: `55 8B 6C 24 08 0F BF C5`. The normal HQ uses this same
call at `0x47F633`, corroborating its seven stack arguments.
No direct roster, count, cap, progress or used-supply writes occur in op 5.
Afterward validate existence/type/owner and exactly one count increment plus
the original supply cost. A mismatch is a fail-stop diagnostic, not rollback.
The driver must stop on `spawn_accounting_mismatch`, not keep seeding units.
