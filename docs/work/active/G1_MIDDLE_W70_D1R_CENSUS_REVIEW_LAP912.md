# G1 W70 D-1R census independent review — lap912 handoff

- Role: next middle/review session, independent of lap912 implementation. G1 stays HOLD; this is a technical review handoff, not a product or milestone approval.
- Implementation record: `docs/history/laps/20261004_lap912_work_g1_d1r_present_bound_census.md`.
- Inputs: raw, maps, selection screenshot, probe result, and recalculation are under `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261004_lap912_d1r_census_r2/artifacts/census/`.
- Recompute with `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261004_lap912_d1r_census_r2/recalculate.py`; expected `recalculation.json` SHA256 `e0ae99a417fa1c487cd0ad5f4569fc1cc5729ef7dcea60114a99a746473f0a54`. It reads inputs and writes only beside them.
- Independently verify: 9/9 pinned hooks, 64 PS3 boundaries, every locked source pointer/pitch and both binary headers, category IDs 0..10, zero dropped contexts and zero missed DD blits; recalculate the three denominator tables, unknown bbox/rows, per-buffer writer counts, and `calls_ps3`.
- Inspect `present64_vs_loaded.png` (same-run `selection.png` beside present 64 map). `loaded.png` is black in this run and is not the comparison image. Check the panel source surface `0x020D16E0`, 800×203, pitch800, and that all 32 PS3 `set_pixel` samples resolve to it.
- Recorded prediction outcomes: P-a 64/64 bound pitch832; P-b 64 unique payloads; P-c world p50 category9 `325,960`; P-d HUD-row category10 `68,536.5`; P-e unknown last-present 7,251 pixels, bbox `[0,512,798,599]`, p50 rows512–599; P-f 32/32 `set_pixel` samples match the panel surface buffer.
- Review source SHA/raw hashes against the implementation record. Do not edit historical raws, pins, or validator thresholds. If accepted, define the narrow P5-H work scope from the panel buffer evidence; P5-T follows. G1 remains unapproved and incomplete.
