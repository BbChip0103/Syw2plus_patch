# lap839 ESCALATE_SOL archive

- archived in lap841 after the requested work repair was independently accepted
- original SHA256: `879bb5bf2f0d0a46b76f758d47575f64509f3212c4ecdd446c46b67bbccce5c3`

```text
lap: 839
date: 2026-10-01
role: middle
status: HOLD/work-repair-required
target: G1 W70 P2 altered-key negative cache lookup

Evidence conflict:
- lap838 fixed the stale-frame branch: content changes evict and reinstall the owned frame; raw independently reproduces refresh 2735, normal lookup miss0, nearest 1.0, invalid/drop0.
- The lap838 narrative says the altered writer takes an actual lookup path, but `g1_hd_asset_probe_negative_key_mismatch()` never searches `g_keys`. It copies the current key, flips `writer`, then sets `altered.identity_frame=NULL` before calling the block reader.
- The block reader never reads `writer`; removing `altered.writer ^= 1u` would leave the forced miss unchanged. `identity_negative_lookup_misses` and `identity_key_mismatches` are then incremented manually, so raw equality 64810/64810 does not prove full-key rejection.
- Current validator checks only counter presence/equality and therefore accepts this synthetic negative. Full evidence is in `docs/history/laps/20261001_lap839_middle_g1_w70_p2_negative_lookup_review_hold.md`.

Work-tier handoff:
1. Factor the full-key table search used by `g1_hd_asset_begin()` and call that same search from the negative probe with an altered writer. Do not force `identity_frame=NULL` before lookup.
2. Add a regression that fails if writer alteration is removed or if a mismatched request can reuse the current key. Record lookup attempts/misses separately from manual assertions.
3. Run a fresh private save006 scroll pair with source SHA pinned. Acceptance: normal lookup miss0, actual altered full-key lookup miss>0, negative miss=mismatch, invalid0, trace/aggregate drop0, nearest>=0.999, scene/source/cleanup PASS. Do not start P3 before a new middle review.
```
