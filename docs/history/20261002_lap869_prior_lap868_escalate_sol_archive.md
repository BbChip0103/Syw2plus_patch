# lap868 work → Sol/middle independent review

Status: P4b B' remains HOLD. This handoff is for diagnosis of a same-tick player-state difference; it does not request a G1 milestone decision.

## Work completed

- Scope changed only `tools/g1_saved_scene_probe.py` and `tests/test_g1_saved_scene_probe.py`.
- Implemented one shared absolute tick plan for baseline/candidate input and observation, exact-target invalidation, and a bulk detailed scene read bracketed by sim tick, PS3, camera, and monotonic timestamps.
- Coverage is read from raw after the scene snapshot; complete captured player/unit records and diffs are retained.
- Focused pytest: 25 passed. `make lint` and `make typecheck`: PASS.
- Fresh gdb-free private save006 pair completed; both lane cleanups PASS; game copies removed. Original EXE and fixture SHA matched pinned values.

## Evidence to review

Artifact root: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261002_lap868_p4b_common_tick/`

- `pair-result.json` SHA256 `b8918cbcdc7b64f5bad5b9abb75340c3c2c9f8b99ec459c490a32d72863795cd`
- baseline raw SHA256 `54b1d7fe205380aa93fed2aeb112832de0ebf484316f570d3b194aefd3070549`
- candidate raw SHA256 `7d9ad8ebd043657f0cc492378d0623bc811fe9f4ee5e122177ffe0339cc74b8e`
- common plan loaded24574; DOWN input/scene `24694/24730`; RIGHT `24790/24826`; final `24862`.
- both lanes have exact input tick brackets, exact coherent snapshot brackets, same cameras `[158,101]→[159,102]→[160,101]`. Bulk scene reads took 1.3–3.2ms.
- action snapshots show equal full captured player/unit records. Final unit records remain equal. Final owner6 rice differs: baseline `230207`, candidate `231007`; all other fields in that player record match. Full record/diff is in `pair-result.json`.
- candidate's embedded Scale2x validator PASS (1157 records, outside diff0, palette violations0); coverage DOWN/RIGHT p50 `365287/353683`; cleanup PASS.
- built bridge artifact SHA256 `e7cd906ca33ddf5e6011c537cb4a62f4a6e99410095a1bcd5bbccb6d34b955481`; same-length comparison with lap866 artifact differs at seven PE timestamp/metadata bytes only; section sizes/source input hashes match. Verify only if it affects evidence identity.

## Required middle judgment

1. Independently rehash pair/raw/original/fixture and recompute final owner6 player difference.
2. Decide whether `rice` diverging at common sim tick with coherent snapshots is a real cross-lane state difference or whether the tick/state observation semantics still leave a measurement ambiguity. Do not infer its cause from this one pair.
3. Keep B' HOLD unless the state difference is explained and the complete gate is met. No C fresh3, P5, or user milestone.
4. If it is a real state divergence, preserve records and issue the narrow next work diagnosis; do not modify the original, validator thresholds, or unrelated G2/G5 files.

Work record: `docs/history/laps/20261002_lap868_work_g1_p4b_common_tick_observation_hold.md`.
