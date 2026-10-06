# 2026-09-28 direct G2 Shift+click selection investigation

## Scope and pinned inputs

- User-reported target: `[ESL]Syw2plus 2608_AI상점개설_장수7명_전비1500-500-5000_시작자리고정_G2_개인500_공용4092.exe`, SHA-256 `1bdcadf9edeccc16d92696e580a60fc71f13a13b6bba22cafb8c9f50e749262f`.
- Matched fixed-start, unexpanded original: `...전비1600-200-3000_시작자리고정.exe`, SHA-256 `f5f816eeb3d8b531ff030f4b43b2f2338ccf0d2257a5684b034e1f8dc8ee1973`.
- Both inputs remained byte-identical before/after. No patch EXE was produced and nothing under `260921_temp` was written. This is a bounded G2 bug investigation, not an eight-player/5000-supply or G5 approval.

## Static first, before game execution

`i686-w64-mingw32-objdump -D -Mintel` plus byte-range comparison of the two SHA-pinned files:

| Path | Observation |
|---|---|
| `0x0041DCD0..0x0041DEAF` click-selection dispatcher and `0x00412D90..0x00412F20` add/remove | Byte-identical. The dispatcher has `0x14` (=20) iterations for the stock selection array, not a 1200-unit-pool gate. Add writes the selection handle at `0x00899028` and increments count `0x00899024`. |
| `0x0040F7D0` slot-to-unit selection wrapper | Only pool base operand changed: `0x0066B790` → `0x0112E000`; call to `0x00412D90` unchanged. |
| `0x0040F560`, `0x0040FD60`, `0x00416FD0` | Pool/existence operands are relocated (`0x0112E0xx`, `0x018849F8`); no old pool base in these inspected helpers. |
| `0x004384B0` hit-test path | Inspected changed operands are relocated active-list addresses; no uncovered 1200 bound in this inspected path. |

The old `0x00899024/28` addresses here are the **still-stock 20-entry selection buffer**, not missed unit-pool relocation. This is a path-local inspection, not a claim that every G2 call site was exhaustively audited.

## Fresh, paired runtime comparison

Procedure: `tools.runtime_env.prepare` made separate complete game copies, Wine prefixes and unused Xvfb displays. Private copies received the ESL2608 asset overlay (18 files, per-run `output/overlays.json`) and only the SHA-pinned EXE was copied to private `game/probe_orig.exe` or `game/probe_g2.exe`. X11 clicks and key events used the read-only `../temp/Syw2plus_patch/20260928_g2_shift_click_add/sprobe.py` (SHA-256 `b2c7d0004d73dbb1624ea41fd0431a54daedb657696e6b4a7d6ceb2e83400438`); selection count and all 20 DWORD handles were read from the live process. Probe source and direct raw JSONL are preserved under `local/runtime/20260928_g2shift_verify3_{original,candidate}/`, with a fresh low-slot original recheck under `local/runtime/20260928_g2shift_verify4_original_low/`.

| Test | Original | Reported G2 EXE | Verdict |
|---|---|---|---|
| Fresh game, one worker plain-click then second worker Shift+click | slot1198 `1` → slots1198,1193 `2` | slot4091 `1` → slots4091,4087 `2` | PASS, high-slot addition works in this fixture |
| Shift+click selected second worker, then click again | `2→1→2` | `2→1→2` | PASS, removal/re-addition |
| Ctrl+1, ground deselect, `1` recall | `2→0→2`, same handles | `2→0→2`, same handles | PASS |
| Ground deselect, double-click worker | same two slots selected | same two slots selected | PASS |
| Legacy `save006.dat` (SHA-256 `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`) loaded into separate private copies; plain-click low slot148, Shift+click low slot124 | `1→2`, slots148,124 | `1→2`, slots148,124 | PASS, low-slot addition works in this save scene |

The legacy save is a real historical save fixture, not freshly generated play; it is used only to put **live low-numbered slots** in view. It was copied into private `game/save/` and never changed in the source directory. Raw files record actual screen coordinates, hover slot, handle and tick. High-slot paired captures: `../temp/Syw2plus_patch/captures/20260928_032027_g2shift_{orig,g2}_after_shift_add.png`; low original capture: `.../20260928_032551_g2shift_orig_low_shift_add.png`. Candidate low raw is `verify3_candidate/.../output/iprobe_g2.jsonl` at `sclick 270 20` (slots148,124). The two low tests are the same save/slots but separate real-time runs, not synchronized tick-for-tick; the dynamic battle can kill units, so both runs verified target existence and owner before the click.

Two earlier private setup attempts entered PS40/tick0 **in both binaries** because the ESL2608 asset overlay was incomplete. Those runs were discarded as environment failures; the later full-overlay copies reached PS9/PS3. No PS40 result was attributed to G2.

## Gates and disposition

- `make doctor`: PASS (optional default runtime manifest absent; each run had its own manifest).
- Targeted G2 tests: `10 passed in 71.68s`; `bash checks/safety.sh check`: `SAFETY_PASS`.
- All `20260928_g2shift_verify*` owned prefixes: residual process list `[]`; source EXE hashes unchanged.
- `make check` was attempted in a background shell but that shell was reaped before completion; **no full-gate PASS is claimed**. No product code was edited, so this does not gate a candidate release.
- Result: **reported Shift+click-add failure not reproduced** in the tested high- or low-slot conditions. No simple old-pool-address/1200-cap defect was found in the inspected path, so no speculative EXE patch was made. The exact user play state (unit type, selected group, clicked target, save, camera/UI overlap, and current selection count) remains unmeasured; the reported issue is not dismissed as false.

## Same-day live video requested by user

A fresh private `runtime_env.prepare` run, `local/runtime/20260928_g2shift_video/20260928_105837_3020853_0/`, executed the same SHA-pinned G2 EXE. The game randomly chose nation 1; a second worker was produced by actual UI clicks, and the live hit-test found owned worker slots 4091 and 4087. Direct 800×600 Xvfb screen recording is `../temp/Syw2plus_patch/captures/20260928_110000_G2_shift_click_live_raw.mp4` (SHA-256 `9b8d0cec14bfc19aa0a04da456c2408436e595dfd39da2c135e93b7c1c0c9ffc`). The same frames with explanatory subtitles, not simulated gameplay, are `.../20260928_110000_G2_shift_click_live_annotated.mp4` (SHA-256 `bc625a4865ad294897b82a903b0f3366ef49db19291c465387c917b6a6bb9766`). Both are 19.67 s, 800×600, H.264; the annotated file decoded without errors.

Raw `output/iprobe_g2video.jsonl` records plain click `(405,300)` leaving one selected worker `[4091]`, then three actual Shift+clicks at `(405,340)` changing the count and selected slots `1 [4091] → 2 [4091,4087] → 1 [4091] → 2 [4091,4087]`. The plain click replaced a selected building, so its **count** was `1→1`; it did select the worker. Companion metadata is `../temp/Syw2plus_patch/captures/20260928_110000_G2_shift_click_live_evidence.json`. The source EXE SHA remained pinned, run status was `DONE`, and owned Wine-prefix residual processes were `[]`. Earlier video setup attempts with other random nations or without two visible owned workers did not produce accepted video evidence; the final recording is a new successful execution, not a montage of earlier screenshots. This still does not reproduce the user's exact play state.
