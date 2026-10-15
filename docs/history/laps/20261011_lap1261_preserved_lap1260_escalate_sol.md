# lap1260 G1 H-HDLAYOUT reject diagnosis / H-G1VARIANT gate

## Work completed

- Fresh official2613 + 2612 data, same sibling `.hd` sidecar, no `SYW2_G1_HD_PACK`, with `SYW2_G1_HD_KEY_LOG` configured before game start. New-game baseline/candidate PASS; candidate 1200 dwell presents, HD100%, stale/fallback/safety0, cleanup/source unchanged PASS. Full raw absolute `hd_pack_rejects` max=1, so do not describe this as whole-run reject0.
- Reject repeats and is identified: `writer=0x00466EA0`, digest `44c611f6`, palette `cecc4681`, 96x112, `src=0x0633AE98`; `written=5257`, `pack_opaque=5261`, `opaque_unwritten=4`. Generated index maps to `fnt/tree_plus.spr.hd/0000.idx8` (43,008 bytes). This is an asset silhouette guard rejection due four extra opaque pixels, not a traced code defect or demonstrated visible/safety fault. Keep fail-closed behavior and raw.
- Detailed record: `docs/history/laps/20261011_lap1260_work_g1_hd_reject_and_variant_layout_handoff.md`. Result SHA `63dcb301b1baf2b8e4d676c7068779b9553f6f9a584cda6fdc8fc03a6e5c79d1`; key-log SHA `84eaef270355bd914012545a0dcc0266cc16145291a30241dd2118c191a9962f`. Private game copies removed; prefixes/raw/key log/manifests retained. No code/test change or Fast rerun.

## Required middle decision before variant runtime

Both staged EXEs:
- G2+G6+G8 SHA256 `1e83466eab020818a6c0e9057508d71451af3ee1098af43ebefc20de8ab96e3d`
- G2+G6+G8+G9 SHA256 `b612109b8cd9e313927871a5a35f28cc09b9c95f80626c938f4d42192cb00556`

`objdump -h` shows `.g2bss` at VMA `0x01AB5000`, size `0x01891000`. Current G1 DLL includes hardcoded stock unit pool/existence references `0x0066B790` / `0x008990C8` (stride `0x758`, count1200) in `control_executor.c`, `ai_shadow.c`, `sfx_hook.c`, and `g1_state_snapshot.c`; probe bridge also defaults to stock pool base. Some paths are opt-in, so the impact on display-only HD rendering is not proven, but control/unit-state evidence is incompatible unless relocated or disabled.

Decide whether H-G1VARIANT may proceed as a display-only boot/new-game/save006 pair with stock-unit-reading features explicitly inactive, or whether a G2-aware bridge/module fixture is required first. Then hand off to work. Do not adapt addresses by guessing, and do not label any G1 milestone complete. No variant runtime launched this lap.
