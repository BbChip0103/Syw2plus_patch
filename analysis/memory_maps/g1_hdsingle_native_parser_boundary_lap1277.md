# H-HDSINGLE native-parser boundary — lap1277 middle, 2026-10-13

Target: official `../patch_history/[ESL]Syw2plus 2613.exe`, SHA256
`818721a5e8539f9ed97090a6d64cfdba429d46ec9caaa5671528005b22f5b724`.
Read-only static analysis; no game execution or binary patch. Do not apply these addresses to another version.

## Observed bytes / source

- `0x00463D60` opens a filename, reads/checks version 9 at `0x00463DAF`, then reads 0xBF4 header bytes at `0x00463DE0`.
- `0x00463DEB` reads object +0xBC8; `0x00463DF2` passes it to allocation; `0x00463DFA` stores the payload pointer at +0xBF4; `0x00463E1F`–`0x00463E2A` use that count for the payload read. This transport does not resolve SItem's frame interpretation.
- `0x00463E50` is a separate sheet-to-stream encoding candidate: +0xBCC/+0xBD0 are divided by +4/+8 at `0x00463E6C`/`0x00463E77`, then a grid is iterated and FE/count bytes emitted. Its input/call relationship to SItem loading is UNKNOWN; it is not evidence that the reader splits this file into 150 cells.
- `0x004672E0`: REA Hopper static pseudocode consumes an RLE pointer and draw dimensions; it has no original-header interpretation. REA Evidence ID `ev_516f475f148cee2af520a400c56160343e2b117979060521f611cec7c075f371`.
- Shell Capstone byte disassembly is separate from REA Evidence. Linear-sweep instruction matches were only discovery candidates; bounded function disassembly establishes the instructions listed above, not runtime execution.

## Source-format conflict / remaining boundary

`Online/Object/SItem001.Spr` SHA256 `c1575b2f176f4cdbbc10549701a8168034948bcd30ad138819fa1bee1a4f9281`, 51,775 bytes:
header `(9,64,32,1)`, sheet `(48715,1920,160)`, payload 48,715 bytes, RLE 307,200 pixels.
Current extractor marks frame 0 inexact. Food references 31 frame IDs, range 5..119; this supports a sheet hypothesis but does not prove its indexing.

Current `tools/inmm_stub/g1_hd_asset.c:635` scans all `_hd.*` names; `load_hd_single_file` requires a version-9 SPR/ YTL header, so a native BMP cannot register. BMP decoding/mapping is absent. A successful DLL compile or Python BMP writer does not prove native BMP use.

## Smallest next evidence

Follow the exact official loader's incoming callers to the routine selecting frame offsets and draw dimensions, and bind the SItem path if present. Confirm whether the file reaches that path, how frame 0 and a referenced nonzero frame resolve, and whether the whole sheet or individual streams are used. If static linkage cannot answer it, work may use one isolated, read-only asset-load observation with the same fields. Do not invent 150 frames, truncate the stream, or silently skip the file to make a complete-candidate result pass.

Raw: shared `../temp/Syw2plus_patch/20261013_lap1277_middle_hdsingle/` contains `raw_review.json`, `loader_463d50.asm`, `loader_4640b0.asm`, `header_immediates.txt`, and complete `rea_4672e0.json`. No broad analysis or additional environment setup is required by this handoff.
