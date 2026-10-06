# G1 W70 P4 — terrain tile blitter family (static, lap858)

- Date / lap / role: 2026-10-02, lap858, strategy (Claude Code `claude-fable-5-1`). Read-only static reading; no runtime,
  no EXE/DLL/patch written. Runtime confirmation of every row below is the P4 work lap's job.
- Protected original: `/home/dev_00/sharedfolder/260320_Syw2plus/[ESL]Syw2plus/[HQ]Syw2plus 2002.exe`,
  SHA256 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` (re-hashed this lap).
- Method: `i686-w64-mingw32-objdump -d -Mintel` over `0x435400..0x4356B0`, `0x465190..0x4651D2`, `0x468C30..0x4692D9`,
  plus a whole-image `call 0x468c30..0x4695ff` xref grep. This map supports only the pinned hash above.
- Prior evidence it builds on: lap828 (fixed-buffer writer EIP `0x468C93/0x468C9C`), lap830/831 (asset key
  `(file,frame)` table equality 1061/1061), lap852 (viewport fields `+0x4D0..+0x4DC`).

## Dispatcher `0x00435400` (tile draw, `ret 0x18`)

- `arg1=file`, `arg2=frame`; tile width/height words come from `0xB6529C/0xB652A0 + file*0xBF8`; source pointer is
  `u32(0xB65E8C + file*0xBF8) + u32(0xB65758 + (file*0x2FE+frame)*4)` (same formula lap830 verified at runtime).
- It calls `0x465190(x, y, x+w-1, y+h-1)` on renderer `0xE5BF18`; that routine returns 1 only when the rectangle is
  fully inside the inclusive viewport `+0x4D0..+0x4DC`.
- `ebx` = shade table pointer or 0. When non-zero it is `0xEF9810 + 0xC00 * k` (0xC00 = 3072 bytes per entry),
  `k` derived from the four-neighbour visibility level (`0x4A3510` on `0x892410`) and a per-cell byte.

| call site | condition | callee |
|---|---|---|
| `0x435593` | inside viewport, no shade table | `0x468C30` |
| `0x4355D7` | inside viewport, shade table | `0x468CC0` |
| `0x43561E` | not fully inside, no shade table | `0x468F00` |
| `0x435662` | not fully inside, shade table | `0x4690A0` |

lap830 labelled these four sites `full/clipped/fog/tinted` (362/39/202/458 calls). The label-to-site order in that
trace is not re-derived here; use the address column above, not the labels.

## Callee family (all `thiscall`, `ecx` = renderer `0xE5BF18`)

All five read the destination base from `renderer+0x1514` and the row step from `renderer+0x10` — the same fields the
existing W60/W70 hooks redirect (`G1_RENDERER_BUFFER 0x1514`, `G1_RENDERER_STRIDE 0x10` in `g1_mirror2x.c`).

| address | `ret` | args (stack order) | first bytes | xref callers | behaviour (static) |
|---|---|---|---|---|---|
| `0x00468C30` | `0x10` | `x, y, rows, src` | `83 EC 0C` `0F BF 54 24 14` | `0x435593`, `0x435910` | per row: `[skip][len]` header then `rep movs` of `len` bytes to `dst+skip`. No width argument, no viewport read, no destination read. |
| `0x00468CC0` | `0x18` | `x, y, w, h, src, shade` | `83 EC 10` `53` `56` | `0x4355D7` | same row format; each output byte = renderer LUT chain over (source index, shade byte): palette RGB `+0x419A0`, shade words `+0x6BCA0`, inverse map `+0x19A0`. Shade row step = `w`. No viewport read, no destination read. |
| `0x00468E10` | `0x14` | `x, y, rows, src, lut` | `83 EC 10` `53` `56` | `0x4351BD` | writes `lut[src]` only where row/column parity selects (checkerboard). No viewport read, no destination read. |
| `0x00468F00` | `0x14` | `x, y, w, h, src` | `83 EC 0C` `0F BF 44 24 14` | `0x43561E`, `0x435959` | clipped copy; reads viewport `+0x4D0..+0x4DC`. Body not fully read here. |
| `0x004690A0` | `0x18` | `x, y, w, h, src, shade` | `83 EC 28` `33 C0` | `0x435662` | clipped + same LUT chain as `0x468CC0`; reads viewport. Body not fully read here. |

- Coordinates and sizes are consumed as signed 16-bit (`movsx ... WORD PTR`).
- The first instructions listed are position-independent (no relative operand); instruction boundaries are at
  3+5, 3+1+1, 3+1+1, 3+5 and 3+2 bytes. The work lap must still compare the full old bytes it relocates.
- Tile geometry implied by the shade entry size: 3072 = 64×48. This is an inference, not a measured value.

## What is NOT established here

- Whether these five account for the terrain pixels of a live PS3 frame (share of the 800×600 frame) — the lap821~830
  census maps cover PS9/PS35 presents only, so there is no measured PS3 last-writer breakdown yet.
- Destination independence of `0x468F00`/`0x4690A0` (only key references were read). The A/B sentinel replay decides
  this at runtime: a destination-reading writer yields A≠B and falls back to nearest.
- How often terrain is redrawn per frame, how many distinct `(src, shade)` pairs a scene uses, and the semantic of the
  `0x468E10` caller.
