# G1 W70 unclipped replay viewport fields (lap852)

- Protected original: `/home/dev_00/sharedfolder/260320_Syw2plus/[ESL]Syw2plus/[HQ]Syw2plus 2002.exe`
- SHA256: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
- Method: read-only `i686-w64-mingw32-objdump -d -Mintel` at `0x00465130..0x00465210`.
- `0x00465130` is the pinned renderer clip setter. It stores four stack arguments on `ecx`:
  - first argument → renderer `+0x4D0`
  - second argument → `+0x4D4`
  - third argument → `+0x4D8`
  - fourth argument → `+0x4DC`
- `0x00465160` initializes `+0x4D0/+0x4D4` to `0`, and `+0x4D8/+0x4DC` to renderer `width-1` / `height-1`.
  This confirms inclusive right/bottom bounds and the full PS3 viewport `(0,0,799,599)` for an 800×600 renderer.
- `0x00465190` compares a point against those four fields. The implementation therefore saves the exact four old
  `LONG` values, temporarily sets `(0,0,799,599)` around only the private `(0,0)` primitive replay, then immediately
  restores all four values before comparing replay pixels to the current clipped draw.
- The same pinned disassembly was checked at the hooked targets: `0x00466D50` reads viewport bounds to clip its
  writes and contains no stores to `+0x4D0..+0x4DC`; `0x004664D0` writes decoded rows through the renderer buffer
  and stride and does not read or write viewport fields. Neither target rewrites the viewport.
- Both targets address destination rows through renderer `+0x10` stride. The private replay capture therefore has
  that renderer stride even though its logical width is `w`; comparisons must index private rows with the replay
  stride, while stored cache rows are packed to `w` by `g1_hd_asset_bind_identity_frame`.
- This map supports only the pinned original hash above. It does not establish renderer fields in other executable builds.
