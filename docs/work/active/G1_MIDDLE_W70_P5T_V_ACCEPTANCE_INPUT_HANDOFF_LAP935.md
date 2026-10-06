# G1 P5-T-V partial acceptance / input work handoff — lap935

Middle independently accepts lap934's lane/timer repair and GREEN/B′1/B′2/C1~C3 evidence as **PASS(partial)**. G1 remains HOLD. This is no milestone closure; thresholds, original assets, mirror scope, raw and golden are unchanged.

## Accepted evidence

- Current `g1_mirror2x.c` SHA256 `b70d044acb18842ee68a418539ae0f974e1652a615ace8cfa8faa019cb011804`, test SHA256 `2b082f481c6043adb41b9ed6e40f2d02b20a7e8a945109806dbbccb19fede32f`; 48 build inputs × 6 builds/current and 6 bridge hashes match. 159 named evidence inputs independently hashed.
- First clip comparison remains 00↔00, second is FF↔FF. Two full allocations and mask allocation, including NULL paths, are accumulated before success branches; replay/bind are excluded. Full sentinel fill, mask, LUT key, visible comparison and rollback scope remain intact. Actual allocation-failure injection/forced rollback is untested; the source regression is not that proof.
- 30-present DOWN/RIGHT intervals: GREEN 48.897/49.379ms, B′1 49.310/49.414ms, B′2 49.621/49.828ms. Every sample precedes its observation tick. A transitioned-camera present at the input tick is legal (B′2); no strict `sim_tick > input_tick` rule is introduced.
- Late20 before DOWN: tinted calls1562, clip mismatch0, replay14, coverage449969.5, stale25783.5. DOWN/RIGHT replay102/58 and tinted calls3091/2227. P-1~P-4/PT-d′ PASS, V5 not triggered. `tinted_clip` covered0 counts first-time coverage, so it does not establish absent rendering or destination dependence; P-5's permitted zero branch remains a limitation.
- Snapshot30 decoded states: five exact ticks × two lanes × three pairs, all equal. V1 6881 presents/0 violations; Scale2x six runs PASS. PNG15 scroll pairs independently recomputed V2/s/q PASS; geometry/HUD and C loaded pairs directly viewed. C20-second ratios0.999999423/1.000002468/0.999953308, p95Δ7/8/7ms, drop0, fixed camera.
- Full PS3 effective coverage medians are 92.5159/92.5150/92.5148% (scroll pairs) and 93.7177/93.7177/93.7181% (C). These are this fixture's measured coverage, not whole-product/second-scene acceptance.

## Next work: actual input proof in the unscrolled fixture (FEASIBLE)

One hypothesis: the fixed slot151 click belongs to the loaded `[158,101]` fixture but runs after terrain scroll moves the camera to `[160,101]`. Source `tools/g1_saved_scene_probe.py` performs that fixed click after scroll; lap934 selection is UNKNOWN/empty in both lanes. This explains why those executions cannot certify the intended target; it does not explain all minimap/production behavior.

1. Work tier immediately runs the existing probe in an isolated baseline/candidate pair with `--hd-source scale2x` and **without `--terrain-scroll`, snapshot or performance-window flags**. Use save006, the current source and explicit private runtime/artifact roots. Check ≥20GiB before launch, wait to completion, remove only this run's game copies. Do not begin another planning lap.
2. Measure selection slot151, empty-click count0, exact selected IDs after drag, minimap gate bytes/camera and production HQ slot1199/witness type7. Record logical/root coordinates, camera and selected IDs. A changed count alone is not a final-input proof. Existing minimap/production original-parity UNKNOWN stays UNKNOWN unless an actual effect is demonstrated in both lanes.
3. B′1 candidate drag PNG shows a building portrait and no drag rectangle while the action record eventually reports slot278, and baseline PNG retains the rectangle. Their capture/action times are not bound, so neither proves same-state UI parity or a renderer regression. In the new input probe record button-up, settled selection and subsequent present/capture state; repair the traceable capture/input harness if needed, then rerun under PROMPT③. Do not weaken validators or replace expected151 with whatever was accidentally selected.
4. If stock also cannot select151 at the original camera, ground one minimal coordinate/hit-target correction in the stock screenshot/live target before changing the harness; hand-on changes belong to work. Preserve raw and old failures. No game logic change is preauthorized by this diagnosis.
5. Targeted tests/build for any changed harness, active Scale2x/V1/V2/s/q and geometry checks, final Fast after documents, then a fresh middle review. Stop on genuine source/raw conflict or safety risk under the session escalation rule.

GDI, second scene, final input/whole HD contract, census defects and user milestone approval remain open. Do not restart G2/G5/G3/G4. Current queue stays only in STATUS.
