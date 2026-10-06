# G1 lap936 input capture review — lap937 ordinary middle

Verdict: **selection semantics PASS(partial); HOLD_POST_RELEASE_PRESENT_UNPROVEN**.
G1 remains HOLD. This is neither milestone closure nor a renderer regression verdict.
The user requires preservation/escalation when implementation evidence is unclear.

## Independently checked

- 73 existing artifact files hashed; 48 bridge build inputs match current source. Probe SHA `28ef2deab769c5d373be1fb3ba6ae51b87c4bcea16ea6dc45ff07b153d133164`, test SHA `d7a879d2db2072c04ee0188a4f5b18f7e46315411704923191ac59998ac7c3d4` match lap936.
- Protected EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, non-synthetic save006 `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`, bridge DLL `923fd1e149a638f3a7ab086beb9aca549c76988e00caafa83dcbc2b62f8da8f1` match direct hashes/build metadata.
- Both lanes: target151, empty count0, drag `[124,140,151,170]`; wait.final and before/after-capture selection records exactly equal. Delivered button-up true. PNG/source-copy hashes match. Drag PNGs directly viewed: same layout and no visible drag rectangle; different transient messages remain, so exact same-frame equality is not claimed.
- Both final raw report cleanup/game_removed true, no prefix processes; their game directories are absent. This checks preserved cleanup evidence, not a new game run.
- Minimap gate restored, camera `[158,101]→[158,101]`; production UNKNOWN. These stay UNKNOWN. Past P5-T-V/B′/C acceptance is unchanged.

## Specific evidence gap and source defects

1. `tools/g1_saved_scene_probe.py:3483` records the last primary present **before** `_inject`. The caller at 3491 passes this value to a helper documented as requiring presents **after release** (`2227`). Present rows during the 322.28ms candidate injection qualify. Final raw supplies after_seq1028 and seq1052/1056, but injection records have no release timestamp/sequence linked to this trace. Their actual ordering relative to button-up is UNKNOWN; they are not proved to precede release either.
2. `3510`–`3517` candidate binding PASS does not require `post_input_presents.status == PASS`. UNKNOWN can still produce binding PASS. The selection equality checks only capture-before == capture-after, not equality to the settled selection; the final r3 raw happens to satisfy all three independently.
3. Controlled read-only fixture: pre-input10, presents11/12, separately designated release20. `_wait_for_post_input_presents(...after_seq=10)` returns PASS with only pre-release rows. This demonstrates the caller-boundary gap, not an actual game timing failure. Existing focused tests all pass and do not cover this boundary.

Recalculation + reproduction script: shared temp `20261004_lap937_middle_input_review/`; `recalculation.json` SHA256 `668093726f67c39dbe4f0723be0cb3b2e08747ff7c55f3799904e7747802e2c7`. Original lap936 raw stays byte-for-byte untouched.

## Promoted verification → work-tier handoff (FEASIBLE, bounded harness repair)

Verify the above caller/binding defects against current source and the preserved counterexample; do not repeat full static planning or treat exit0 as approval. Then hand implementation to work tier:

1. After `_inject` returns with button-up, conservatively read the latest primary-present seq, record it explicitly as the post-release boundary, and wait for two successful candidate presents strictly after that boundary. Keep the existing baseline NOT_INSTRUMENTED/PASS_WITH_LIMITS limitation explicit; do not invent baseline frame proof.
2. Candidate binding requires the fresh-present gate PASS and settled selection == capture-before == capture-after. Propagate binding failure to the relevant capture acceptance; semantic selected IDs may still pass independently. Add regressions for during-injection-only rows, no later presents, UNKNOWN barrier and changed settled/capture state. Do not change game logic, thresholds or expected IDs.
3. Immediately run the same unscrolled private original/Scale2x pair. Record post-release boundary/two fresh seq/capture state, wait to completion, remove only owned game copies. Fix attributable harness/input defects and rerun within the work lap under PROMPT③. Then continue the already authorized minimap valid-coordinate/camera pair; production follows its working scene. No G2/G5/G3/G4 restart.

This ordinary middle session makes no hands-on implementation changes and does not claim promoted authority. Full Fast/new runtime are SKIP at the user evidence-gap stop; doctor/lint/typecheck/focused checks and preservation audit are reported in STATUS. `loop/ESCALATE_SOL` carries the explicit next verification.
