# lap904 → Sol independent review required

## Why this is escalated

P4c-M fresh green pair passed V1, V2, V2s, Scale2x validation, scene equality, source safety and cleanup. Two subsequent fresh P4b-S B' pairs both passed the existing Scale2x/V1 gate, V2s, scroll/snapshot parity, scene equality, source safety and cleanup, but failed the new required V2 capture gate after selection/scroll. The same world-right dark region is visible in candidate selection captures. The evidence does not yet distinguish a renderer/cache-transfer defect from cross-process capture timing or input-state mismatch. Do not declare P4c/B' complete or begin C from these results.

## Required Sol review

1. Independently recalculate pair1/2 V2 black counts from the preserved PNGs and verify the candidate-only black coordinates, with source SHA, capture tag, camera and relevant present range. Confirm the observed right-edge wedge from the PNGs.
2. Correlate the world-right region with candidate trace coverage/stale/last writer/cache-layer move and transfer events. Compare selection/minimap/production captures with each lane's action snapshots and capture barriers.
3. Decide whether the evidence identifies a renderer/cache-transfer defect or an invalid cross-process visual comparison caused by input/capture-state mismatch. Keep V1/V2/V2s limits and comparison fields unchanged; do not infer cause from timing alone.
4. Resolve whether `input_effect_comparison` HOLDs (`selection_target`, `minimap_gate_restore`, `production_effect`) are upstream evidence needed for this visual gate or separate unknowns. Give one bounded next work action; no threshold edits, D-1/P5 or C before V2 is resolved.

## Preserved evidence

- Detailed lap record: `docs/history/laps/20261003_lap904_work_g1_p4cm_mask_green_bprime_v2_hold.md`.
- Green pair: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/captures/20261003_2047_lap904_p4cm_green_r4/`; `pair-result.json` SHA256 `ed4b0c89cdefb4f34c385ae2a54703a308cc07455a537de0e5ee1ca485992b88`; trace SHA256 `bc8e42b117267bd37cb8be437743c203f7e19b95cc28d6454ff8e3ebebd6b991`.
- B' pair1: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261003_lap904_p4bs_pair1/`; pair SHA256 `6ea0f5aa6587d00c878761215fc22383521cfbe5ee6c6af85acf4aacc59d4cef`; trace SHA256 `fa2983eebc14b3a33cf0dc975c0a439b73e7d9e5eacd580543e932d87d558e04`.
- B' pair2: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261003_lap904_p4bs_pair2/`; pair SHA256 `fca83f271deaa1f6c747f53b3ecc84e724e62db63c6fcfd1787e8e111f32f4f4`; trace SHA256 `51d5ef2fde8609e19517d399ddf3cc1e62166945c4e5df1a931065431dace538`.
- Current uncommitted implementation/test files and their SHA256 are enumerated in the detailed lap record. Original EXE SHA256 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` and save006 SHA256 `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064` matched.

## Current state

- G1 P4c/B' HOLD; no product or milestone approval.
- Current edits are preserved uncommitted. No original/reference write, commit, deploy, or threshold change.
- `make lint` and `make typecheck` pass; focused tests 155 pass. Final `make check` runs after this record and will be summarized in STATUS.
- Continue only after Sol supplies an evidence-grounded attribution and one bounded next work action. No user reauthorization is required for ordinary local work.
