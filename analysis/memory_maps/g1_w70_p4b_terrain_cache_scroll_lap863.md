# G1 W70 P4b — terrain cache scroll shift and cache→frame copy (static + lap862 raw, lap863)

- Date / lap / role: 2026-10-02, lap863, strategy (Claude Code `claude-fable-5-1`). Read-only static reading plus
  recomputation of existing lap862 raw. No runtime, no EXE/DLL/patch written. Runtime confirmation of the hook design
  built on this map is the P4b work lap's job.
- Protected original: `/home/dev_00/sharedfolder/260320_Syw2plus/[ESL]Syw2plus/[HQ]Syw2plus 2002.exe`,
  SHA256 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` (re-hashed this lap).
- Method: `i686-w64-mingw32-objdump -d -Mintel` over `0x4324E0..0x4332F0`, `0x41BF20..0x41BFB0`, `0x41C820..0x41C880`,
  `0x4245C0..0x424660`, `0x4DB1D0..0x4DB230`, plus a whole-image `call` xref grep for `0x41BF20`, `0x4324E0`, `0x4332F0`,
  `0x466280`, `0x464E00`. Reference decompile `Syw2plus_re/analysis/ghidra_output/FUN_004324e0.c` /
  `FUN_0041bf20.c` was used only as a reading aid; every row below was matched against the pinned bytes.
  This map supports only the pinned hash above.
- Builds on: lap828 (fixed terrain buffer `0x00BA3D30..0x00C0BD30`, 832×512, writer EIP inside `0x468C30`),
  lap858 (blitter family), `hqcdd_external_display_map_20260921.md` (external names for `0x4324E0`/`0x41BF20`/`0x466280`),
  `original_qhd_probe_0910.md` (`0x43296C` branch, cache binder).

## Data flow (static)

1. `0x004324E0` (cache update, `ecx` = `0xB3DDA8`, called from `0x41C85D`) binds the renderer `0xE5BF18` to the static
   cache with `0x464E00(0xBA3D30, 832, 512)` (call at `0x432925`) and sets the clip to `(0,0,831,511)`
   (`0x432954..0x432967`, `call 0x465130`). All five terrain blitters therefore write **into the cache**, in cache
   coordinates — consistent with the lap862 gdb traces: every `asset_blitter_call` event has renderer buffer
   `0xba3d30`, stride 832 (r3 candidate 1061/1061, r3 baseline 969/969, r4 candidate 1186/1186, r4 baseline 1040/1040).
2. `0x43296C..0x432989`: `[this+0x597D]==1` (camera moved) or `[this+0x597C]==1` (full redraw) enters the update,
   otherwise jump to `0x4332B5`. Full redraw clears `+0x597C` and marks the whole 13×16 dirty-block table at
   `0x0105796C` (`0x432992..0x4329AC`).
3. Camera-moved path (`0x4329F5` onward): current camera `[this+0x4FD4]`,`[this+0x4FD8]` is compared with the previous
   camera words `[0x01057968]`,`[0x0105796A]`. For eight exact deltas the cache content is **shifted in place by the CRT
   `memmove` at `0x004DB1D0`**, only the newly exposed block row/columns are marked dirty, and only those tiles are
   redrawn through the blitters. Table below.
4. `0x0041BF20` (called from `0x424622`): `0x464EC0([0x0104FB2C])` lock, then `0x466280(0,0,832,512,0xBA3D30)` at
   `0x41BF57`, then `0x465080([0x0104FB2C])`. This is the per-frame **cache → battlefield surface copy at (0,0)**; it does
   not shift anything. `0x4332F0` (overlays/sprites) is called separately from `0x41BF9A`.
5. Frame function entered at `0x4245D0` calls `0x41C770` first (the range containing the `call 0x4324E0` at `0x41C85D`;
   the function boundary between `0x41C770` and `0x41C970` was not verified), then runs a phase gate: the copy
   `call 0x41BF20` at `0x424622` executes only when `[0x00B93E00]==0`, after which `[0x00B93E00]` is set to 1 and the
   function returns. The cache update and the cache→surface copy are therefore **not locked to the same invocation**.
   Later phases were not read.

## In-cache shift call sites (all `call 0x4DB1D0`, cdecl `memmove(dst, src, n)`, inside `0x4324E0`)

`row` = 832 bytes (`0x340`), 32 rows = `0x6800`, `0x61800` = 832×480, `0x300` = 768.

| call site | old bytes | camera delta (cur − prev) | dst | src | n | loop | content moves |
|---|---|---|---|---|---|---|---|
| `0x432A2D` | `E8 9E 87 0A 00` | (+1,+1) | `0xBA3D30` | `0xBAA530` | `0x61800` | once | up 32 rows |
| `0x432AB5` | `E8 16 87 0A 00` | (−1,−1) | `0xBAA530` | `0xBA3D30` | `0x61800` | once | down 32 rows |
| `0x432B38` | `E8 93 86 0A 00` | (−1,+1) | `edi` | `edi−0x40` | `0x300` | `edi=0xBA3D70`, `+0x340` while `<0xC0BD70` (512 rows) | right 64 px |
| `0x432BD4` | `E8 F7 85 0A 00` | (+1,−1) | `edi` | `edi+0x40` | `0x300` | `edi=0xBA3D30`, `+0x340` while `<0xC0BD30` (512 rows) | left 64 px |
| `0x432C7C` | `E8 4F 85 0A 00` | (0,+2) | `edi−0x67C0` | `edi` | `0x300` | `edi=0xBAA530`, `+0x340` while `<0xC0BD30` (480 rows) | up 32 rows, right 64 px |
| `0x432D4E` | `E8 7D 84 0A 00` | (−2,0) | `edi` | `edi−0x6840` | `0x300` | `edi=0xC0BA30`, `−0x340` while `≥0xBAA570` (480 rows) | down 32 rows, right 64 px |
| `0x432E1D` | `E8 AE 83 0A 00` | (0,−2) | `edi` | `edi−0x67C0` | `0x300` | `edi=0xC0B9F0`, `−0x340` while `≥0xBAA530` (480 rows) | down 32 rows, left 64 px |
| `0x432ED2` | `E8 F9 82 0A 00` | (+2,0) | `edi−0x6840` | `edi` | `0x300` | `edi=0xBAA570`, `+0x340` while `<0xC0BD70` (480 rows) | up 32 rows, left 64 px |

- `dst`/`src` follow the push order (`push n; push src; push dst`). The camera-delta column is this lap's reading of the
  compare chain and is informational: a mirror wrapper must follow the actual `(dst, src, n)` arguments, not the delta.
- Every per-row call moves a run that stays inside one cache row at both ends (`x` offset 0 or 64, length 768).
  The two single calls move whole rows (`dx = 0`).
- After each shift the code marks one dirty row or column block set (e.g. `0x0105797B + 0x10*k`, k<13 for the bottom
  row; `0x0105796C..0x0105797B` dword fills for a column) and, near the map edge, clears a strip with
  `0x465FC0(x0,y0,x1,y1,0)`. Other deltas fall through to `0x432F82` (not read).
- `0x004DB1D0` first bytes: `55 8B EC 57 56 8B 75 0C 8B 4D 10 8B 7D 08`. `cmp edi,esi / jbe` forward copy, otherwise
  `cmp edi,esi+n / jb 0x4DB368` backward copy → overlap-safe `memmove`. The first 8 bytes are position independent
  (1+2+1+1+3).

## Cache → frame copy

| item | value |
|---|---|
| function | `0x0041BF20`, only direct `call` xref `0x424622` |
| lock / unlock | `0x464EC0([0x0104FB2C])` at `0x41BF35`, `0x465080([0x0104FB2C])` at `0x41BF68` |
| copy call | `0x41BF57`: `E8 24 A3 04 00`, args pushed `0xBA3D30, 0x200, 0x340, 0, 0` → `0x466280(x=0, y=0, w=832, h=512, src=0xBA3D30)` |
| `0x466280` | thiscall, `ret 0x14`, first bytes `8B 41 0C 53 99 83 E2 07` (already pinned in `g1_census.c`); 16 direct call sites image-wide, `0x41BF57` is the one read here that passes the cache (the other 15 were not read) |

## lap862 raw that this map explains (recomputed this lap from the candidate `trace_raw.jsonl`)

| run | PS3 present (seq) | camera | terrain calls (rle/shade/clip/clip-shade) | covered | stale | covered−stale |
|---|---|---|---|---|---|---|
| r3 | 1564 | [158,101] | 346/29/124/210 | 330,658 | 2,360 | 328,298 (68.4%) |
| r3 | 1565 | [159,102] | 362/38/156/281 (+128) | 344,557 | 30,313 | 314,244 (65.5%) |
| r3 | 1566 | [159,102] | unchanged | 314,734 | 210,468 | 104,266 (21.7%) |
| r4 | 1582 | [158,101] | 346/29/124/210 | 331,812 | 1,937 | 329,875 (68.7%) |
| r4 | 1583 | [159,102] | 362/38/156/281 (+128) | 346,066 | 30,979 | 315,087 (65.6%) |
| r4 | 1584 | [160,103] | 377/48/190/356 (+134) | 344,157 | 240,644 | 103,513 (21.6%) |
| r4 | 1585 | [160,103] | unchanged | 103,918 | 42,632 | 61,286 (12.8%) |

- Fixed camera before the key: `covered−stale` 68.4–70.6% of 480,000 in both runs (6–7 presents).
- One (+1,+1) step triggers only 128 blitter calls (a full redraw is 709) and, one present later, 210,468 covered
  pixels fail the present value check at once. The step's own present loses ~30k (≈ the 800×32 redrawn strip that the
  mirror applied before the frame showed it).
- Raw SHA256: r3 `70d6e94c5c5eed0b6f9bfbb0eda4cee109c98457d6b9aa2b62f49f57f460dbdb`,
  r4 `f16a78a2285683df1c634295ab008a936babeb25c9b85923fbf1a7106e53d0cc` (re-hashed this lap).

## What is NOT established here

- The phases of the frame function after the first, and the exact reason the copy lags the update by one present
  (only the phase gate and the raw one-present lag are established).
- The `0x432F82` fall-through for other camera deltas (minimap jump, larger steps) and the edge-of-map branches.
- Any other writer into the cache besides the five blitters, `0x4DB1D0` and `0x465FC0` (e.g. the `0x435910`/`0x435959`
  call sites, the references to `0xBA3D30` at `0x41AF40`/`0x43191C`).
- That the destination surface `[0x0104FB2C]` maps cache (x,y) to frame (x,y) for all frames; it is supported by the
  fixed-camera coverage (the mirror compares cache bytes against frame bytes at the same coordinates) but was not read.
