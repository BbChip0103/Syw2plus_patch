# G2 official creation runner guard (2026-09-17)

This bounded change adds an opt-in `g1_baseline` branch for
`_custom_game_chain_inject_g2_eight_seed42` with candidate
`g2_supply_5000.exe`. It requires the exact `fixed_supply_5000.patched_bytes`
candidate and approved diagnostic bridge SHA256
`8de5b96b992db90f0c6e1c8c33d33caada9e52435a4e605b3a2d747764555f65` in both
the private game copy and manifest. G2 artifacts use a caller-provided fresh
absolute directory under `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch`;
the manifest-owned output remains untouched.

Before sampling, the runner requires PS3 readback for owners 0..7, raw six-byte
role/mask records, distinct start points, config/seed fields, unique live unit
slots/full IDs, cap=5000, and live HQ49+worker7 per owner. Extra AI units are
recorded rather than normalized. The evidence field is
`g2_eight_owner_creation`; this branch does not claim product or LAN parity.

Validation: `tests/test_g2_official_creation.py` plus `tests/test_runtime_env.py`
158 passed; Ruff and targeted mypy passed. No game, Wine runtime, DLL build,
source binary, or protected input was changed in this lane.
