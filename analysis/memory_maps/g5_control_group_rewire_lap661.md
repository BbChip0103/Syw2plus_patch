# G5 control groups (Ctrl+digit) — lap 661 static map and rewire contract

- Protected source: `syw2plus_original.exe`, SHA256 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` (read only).
- Base candidate inspected: v1 `6c8f73ba5626a978abaa09bb56adc46ee5da39bdd16d05c71285ce10d8f20b25` (rebuilt in memory, not written).
- Method: capstone/pefile disassembly + rel32/imm xref scan of `.text` (lap661 stdout, no artifact).

## Stock layout

Group object `G = 0x009570F4 + player*0x3ABC` (= PlayerStruct `0x956770` + `0x984`), one per player (AI too).

| G offset | Meaning |
|---|---|
| `+0x016` | entries, 10 groups × 20 × dword handle (`g*0x50 + i*4`; low word slot, high word aux) |
| `+0x336` | count[10] word |
| `+0x34A` / `+0x35E` | center x/y [10] (`FUN_00445FF0` average of live entries) |
| `+0x372` / `+0x386` / `+0x39A` | group type / region / flag [10] |

Unit record `0x0066B790 + slot*0x758`: owner byte `+0x8E`, hp `+0xB4`, handle `+0x29C`, selectable byte `+0x31C`,
**group field `+0x344`** (dword; `-1` = none). Spawn init `0x00411AD7` writes `-1`. Setter `FUN_0040F750(slot, g)`.
Existence word array `0x008990C8` (1200 slots, stock layout).

## Member functions (all `ecx = G`)

| Function | Role | Callers |
|---|---|---|
| `0x00445CD0` | assign selection to group g (Ctrl+digit) | only `0x0041D4F0` (local player `[0xB63FC4]`) |
| `0x00445E30` | recall group g (digit) | `0x0041D533..0x0041D7FD` (local player) |
| `0x004460A0` | double-tap recall → camera center via `0x00445FF0` | key handler |
| `0x00445A90` | remove handle from all groups (death/convert), compacts, disband at 0 via `0x00445A20` | `0x409CB8 0x40CAA8 0x44305F 0x47602F 0x476F0D` |
| `0x00445B80` | append one unit, **rejects when 20 full** | AI `0x476064`, `0x4B211A` |
| `0x00445FF0` / `0x004460F0` | center / type update | AI `0x43CDC9`, `0x4B1F46` + members |

AI also reads entries/counts directly: `0x43CB35 0x43CF79..0x43D60D` (`0x95710A`/`0x95742A` absolute, stride 20 hardcoded) and `0x4B2080/0x4B20E5`.
**Control groups are the AI squad storage.** Any global widening changes G4 AI behavior; lap661 rejects it.

Readers of unit `+0x344`: badge draw `0x00409640` (local-owned units, field ≥ 0 → group digit sprite), AI `0x00443032`, `0x00475FFA/0x476034`, `0x004B1653` (`== -1` eligibility).

Save: bulk `0x892410..+0xE397C` (includes all PlayerStruct/G) at `0x00440F0C`/`0x004412DC`; unit records `0x758` bytes each for every existing slot at `FUN_0040F4B0` → **unit `+0x344` is persisted**.

## Defect in v1 candidate (current `6c8f73ba…`)

Assign phase B walks the relocated selection to its end (`0x445E0B cmp ebx,0x0108C0CC` = 50) and stores selection index i at `G+0x16+g*0x50+i*4`
with no bound, incrementing `count[g]` each time. With >20 selected this **overwrites groups g+1, g+2 entries**, and for g=9 writes past
`+0x336` into counts/center/type/region/flag (`+0x336..+0x3AE`). lap660 `group1_count=50` is direct evidence. Do not use v1 for Ctrl+digit beyond 20.

## Chosen rewire (lap661 strategy): unit-field-authoritative overflow, save format unchanged

- PlayerStruct G layout and every AI/removal/center/type function stay byte-identical. G holds the first ≤20 members exactly as stock (count ≤ 20).
- Members 21..50 are represented only by the unit group field `+0x344 == g` (local-owned units). The reserved side-table `0x0108C100` is **not used**.
- Save/load: no format change. Bulk restores ≤20 entries; unit records restore `+0x344`, so recall rebuilds 50 after load. Stock EXE loading a candidate save sees valid ≤20 groups + badges.

| Hook | Site (v1 bytes) | Cave behavior |
|---|---|---|
| H1 assign pre-clear | `0x00445D4E` `8b 54 24 14 bb 04 c0 08 01` → `jmp cave; nop×4` | pushad; for slot 0..1199: exists && `(int8)unit+0x8E == [0xB63FC4]` && `unit+0x344 == ebx(g)` → `unit+0x344 = -1`; popad; replay `mov edx,[esp+0x14]; mov ebx,0x0108C004`; `jmp 0x00445D57` |
| H2 assign store bound | `0x00445DCB` `8b 44 24 10 66 c7 00 00 00` → `jmp cave; nop×4` | `cmp ebx,0x0108C054` (entry base + 20×4); `jb` → replay `mov eax,[esp+0x10]; mov word [eax],0; jmp 0x00445DD4`; else `mov eax,[esp+0x24]; push eax; mov dx,[ebx]; push edx; mov ecx,0x0061E36C; call 0x0040F750; mov ebp,[esp+0x18]; jmp 0x00445E01` |
| H3 recall overflow | `0x00445ED1` `85 db 0f 84 de 00 00 00` → `jmp cave; nop×3` | pushad; for slot 0..1199: exists && owner==local && `unit+0x344 == ebp(g)` && `0x416F40(slot)` && `0x40F790(slot)==1` && `dword [0x0108C000] < 50` → `0x40F7D0(slot,1,0)` (ecx `0x0061E36C`), nonzero → `inc dword [esp+0x10]` (pushad ebx); popad; `test ebx,ebx; je 0x00445FB7; jmp 0x00445ED9` |

Cave: `.text` zero tail `0x004E4AE5..0x004E4FFF` (1307 B, verified zero in v1). Use `0x004E4C00..` (avoid old QHD probe `0x004E4B00`), raise `.text` VirtualSize to cover cave end (≤ raw `0xE4000`), following `patches/resolution/qhd_probe.py` precedent.
Dedupe in H3 relies on `FUN_00412D90` mode 1 returning 0 for an already-selected handle (`0x412DBF..0x412E13`); the `< 50` guard avoids its full-table phantom-flag path (lap657).

Accepted edges (disclosed): double-tap camera center and group type use first ≤20 members; if all first-20 die the stock disband runs but field members stay recallable;
a converted enemy unit whose stock `0x445B80` add fails keeps its old field (stock badge already shows it) and becomes recallable. Pool scan uses the stock 1200-slot layout; a G2-integrated candidate must remap `0x8990C8`/`0x66B790`/1200.
Multiplayer: groups and unit field writes are local UI state in stock too; sync impact is recorded as not measured.
