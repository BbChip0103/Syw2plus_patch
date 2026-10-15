# lap1258 G1 H-HDLAYOUT — fresh middle adjudication required

Role boundary: lap1258 was hands-on work. Stop before self-approving the runtime evidence. No commit, delivery, deploy, STOP, or milestone approval.

## Change and evidence

- Work record: `docs/history/laps/20261011_lap1258_work_g1_hdlayout_sidecar.md`.
- Current source changes are uncommitted and preserved. Modified sources: converter `tools/g1_hd_convert.py`; probe injection `tools/g1_saved_scene_probe.py`; DLL loader/telemetry `tools/inmm_stub/g1_hd_asset.c`, `.h`, `direct_draw_trace.c`; focused regression `tests/test_g1_hd_convert.py`.
- Converter produced read-only-derived sibling sidecars at shared temp `20261011_lap1258_hdlayout/sibling_tree_v3/`: 39,155 idx8 files, 782 `.hd` folders, 39,937 total files, 1,060,085,276 bytes. Source game, original assets, original pack, and upscaler input were unchanged.
- Official ESL2613 + 2612 save006 pair, sidecars installed only in private candidate game, no `SYW2_G1_HD_PACK`: PASS; 1,093 candidate presents, hit917, reject/stale/fallback/safety0, source unchanged and owned cleanup PASS. Pair result SHA `7f8772a0ea6d0ce044a8f808b080f1bdd243b1cab879e6dc59f2bf319dc82eb1`; candidate trace SHA `824753eb6f5cb2eddf072b56f64c74347554bc1cc9bcdb0fdaecf1b53f4f3a51`.
- New game run1: aggregate PASS and 1,198 dwell presents/HD100%, stale/fallback/safety0, but the full candidate trace recorded one pack reject at PS3 seq1727/tick334463767. Result SHA `03dad80c75610dfc202d10fe6a74e6795863a5cb28835e3aaa3af97eda2e6a5a`; trace SHA `94aafab389a6c10da318b34bc2c1d69832b3d76370d959e64bd0b15522f08264`. This run had no HD key-log, so the asset/writer was not identified.
- Same-config new game diagnostic retry with HD key logging: aggregate PASS, 1,197 dwell presents/HD100%, hit373, reject/stale/fallback/safety0, source unchanged and cleanup PASS. Result SHA `b49903fbd45a10c209e40faf4fbe07f62dbb4bf1c8cd986df1c99003a10258a2`; trace SHA `0206cf04a50175969d6a3282e6fe7369c06660851472a5e32d3704ac73130719`. The first reject did not reproduce; its cause remains UNKNOWN.
- `make check`: exit0, 2,194 passed/9 skipped, 835.57s; log SHA `56433ccf41923f2e866291ed6311e4475f611d467de4a0f81895fc768fb80767`. Focused HD tests 121 passed; lint/typecheck, mingw DLL build, safety/context/diff checks passed.

## Required middle judgment

Independently inspect the sidecar mapping/runtime lookup and both new-game traces. Decide whether run1's one reject can be technically accepted as an isolated UNKNOWN, or whether a narrowly instrumented rerun/repair is required before the next queue. Preserve both results; do not convert run1 to PASS or weaken the reject gate. If more evidence is needed, identify the smallest probe that will capture the rejected digest/writer and compare it with the generated index. Do not repeat the full Fast or pair without a concrete need; they already passed on the same current sources.

Other scope: no Windows/user trial, no delivery, no G1 milestone completion, no 24k/144k/multiplayer claim. Private game copies and all run-owned processes are gone; prefixes, logs, raw, manifests, and shared sidecar output are retained. `loop/.lap_counter` remains 1258; no `loop/STOP`.
