# lap1276 H-HDSINGLE source-format exception — middle/strategy adjudication required

## Trigger
The current implementation evidence for one original asset conflicts: `Online/Object/SItem001.Spr` is declared by its header as 64x32, one frame, while its RLE stream consumes 307,200 pixels (the 1920x160 sheet record) rather than the declared 2,048 pixels. The original file is read-only and was not modified.

## Direct raw evidence
- Source: `../[ESL]Syw2plus/Online/Object/SItem001.Spr`
- SHA256: `c1575b2f176f4cdbbc10549701a8168034948bcd30ad138819fa1bee1a4f9281`
- Header `(version,width,height,frames)=(9,64,32,1)`; sheet `(tds,sw,sh)=(48715,1920,160)`; data bytes `48715`.
- Current extractor decodes frame 0 as 64x32 but marks it inexact: it emits 2,048 pixels while the RLE stream represents 307,200. `Online/item/food.txt` references `SItem001.Spr` with frame IDs beyond 0, supporting a sheet interpretation, but does not prove how the game consumes this file.
- Existing history `docs/history/20261008_status_lap1170_precompaction.md` records lap1158's independent H-HDX1 exception for this same file. This lap independently recomputed the raw values above; it did not assume the old record was current proof.

## Work preserved
- Product/test edits remain uncommitted; no original, reference, EXE, or game data was changed.
- Candidate output from `native-layout` is preserved at `../temp/Syw2plus_patch/20261013_lap1276_hdsingle/native_layout_retry1/`: 3,366 files, 1,168,997,818 bytes. The converter reports 135,293 frames, 96,138 default-scale frames, `error_count=1`, `pass=false`; the only reported error is this file's incomplete decode. A preceding failed panel attempt is preserved at `../temp/Syw2plus_patch/20261013_lap1276_hdsingle/native_layout/`.
- Targeted regression tests passed before this raw conflict was reached; the final panel fallback regression also passed. The default-on MinGW DLL build succeeded after C source edits. Full `make check`, the three real-game variant lanes, and candidate round-trip were not run because the one-file parser conflict leaves the complete candidate undefined.

## Requested adjudication
1. Determine from the official game parser/asset references whether this is a 150-cell sprite sheet despite the one-frame header, and how `_hd` must preserve that native representation at 2x.
2. Set a safe, testable policy for this source and any further files whose encoded pixel count disagrees with header dimensions. Do not infer sheet-grid behavior from filename references alone.
3. Review the remaining native-loader boundary: current DLL indexing/decoding handles `.spr` and `.ytl`; BMP native parsing/digest mapping has not been implemented or tested.
4. If the evidence remains insufficient, keep H-HDSINGLE blocked and identify the smallest source/engine probe needed. Once resolved, return implementation to the work role; this handoff does not request a code patch from the reviewer.

No delivery, commit, milestone approval, or product PASS is claimed.
