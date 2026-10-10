# 2026-10-10 | lap1241 | G1 middle — stale253 independent review / work handoff

- Role: fresh Codex App middle (diagnosis/plan/confirmation), designated Sol/high
  per MODEL_ROUTING; this surface does not expose resolved launch ID. No hands-on
  game/harness implementation or provider/model fallback.
- Claim and success criterion: independently confirm lap1240 mask/input/writer raw,
  compare existing primitive-A contract against exact 2613 bytes, then decide the
  smallest executable work probe. Confirmation means matching raw values, not G1
  completion. STOP absent; runtime counter1241 read only. Documents initially
  STATUS87/INBOX260/APPROVALS36, below required130/350/250 limits.
- Hypothesis: a covered screen pixel's snapshot becomes inconsistent during the
  transition to the building-selection input. Cache drift, later screen write and
  mirror/replay failure are alternatives, not established causes. A write observed
  in a separate stale-free run is insufficient grounds for repair.
- Changed files: this lap, STATUS, preserved previous ESCALATE, new memory map,
  ignored `loop/ESCALATE_SOL`; review script/JSON/disassembly only in shared temp.
  No source/test/EXE/DLL/pin/golden/APPROVALS edits, commit, delivery or milestone.

## Inputs / independent evidence

- HQ2002 original SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`;
  official2613 SHA `818721a5e8539f9ed97090a6d64cfdba429d46ec9caaa5671528005b22f5b724`;
  save006 SHA `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`.
  Previous actual environment: original→2612 overlay→2613 EXE, private Wine
  game/prefix/display1600×1200×24. Non-synthetic save006, 8 player records/559 units;
  active combatants unmeasured, not G2 load proof. This session fresh game runs0.
- Read-only independent command: `.venv/bin/python ../temp/Syw2plus_patch/20261010_lap1241_middle_review/review.py`.
  Output `review.json` SHA `446d63196accd02719f41f268d8217736f891e1691890837a1750ba6ef5cc9f4`.
  Both pair SHA match lap1240. All72 binary masks checked against their pixel counts
  and same-tick PS3 trace rows; raw traces/input/masks/watch/drift match their stored
  SHA, four lane EXE pins/owned close/summary1/run ID/drop0/detach/flush/cleanup match.
  Six relevant current/copied bridge sources per run match recorded build inputs;
  host probe/test SHA match each execution snapshot. No current full Fast claim.
- Candidate DLLs: repro `19693c4c5d307fdbb40f720c6832d23340f3e859075c4b868c05f2e26835f05b`;
  watch DLL hash is recorded and verified in `review.json`. Separate builds are not
  asserted byte-identical. Original/source protection is checked below.
- Repro: exactly ordinal62 stale253, bbox x435–466/y180–199; ord61/63 stale0.
  All three chosen watch samples equal mask value2. Game tick312079905,
  trace completion312079916, cursor move312079906, left-down312079955.
  Click is +50ms after game tick / +39ms after completion; the cursor movement
  falls within that frame's tick-to-completion interval. Timing correlation does
  not establish the rendering order or causal writer.
- Watch: selected masks stale0; `t:x` p66/sample2/EIP0x466E67/value228/guard1,
  same p66 layer sample `scr=snap=228,cov=1,cache=lexp=93` is a normal composition.
  Exact old bytes/disassembly and interpretation are in
  `analysis/memory_maps/g1_stale253_2613_primitive_a_lap1241.md`.
- **Semantic correction to lap1240:** its +9ms uses the present tick, not a writer
  timestamp. Hardware-hit raw has no `tick` or `ts_ms`, so exact hit time and ordering
  against mouse-down are UNKNOWN. Original lap1240 text/raw is preserved; this does
  not erase the stale253 observation. `st[]` is a filtered stack scan, not a confirmed
  caller chain. `guard1` alone does not prove recursion/bypass.
- Moved layer sample points do not move the fixed `t:r` rectangles/cache-overlap
  event geometry. Use `t:s` values at the new points; do not interpret old rectangle
  counters/`ev[]` as a writer record for the new bbox.

## Decision / immediate work handoff

Raw observation confirmation PASS; **repair basis BLOCKED (writer UNKNOWN)**.
Existing diagnostic probe is **FEASIBLE**. No further planning-only session is needed
before a work-tier actual product probe. Preserve this decision in ESCALATE_SOL
because the earlier hit-time inference cannot authorize a game-code repair.

Work ownership: execute existing `tools/g1_saved_scene_probe.py`; initial source
changes0. Do not change unrelated G2 files or validators. Use fresh own runtime root,
prefix and empty display; retain raw/prefix/output and remove only own completed game.
First measure the same event with layer sampling and no hardware write watch:

```sh
PYTHONPATH=. .venv/bin/python -u tools/g1_saved_scene_probe.py \
  --runtime-root local/runtime/lapNEXT_stale253_layer \
  --artifact-root ../temp/Syw2plus_patch/YYYYMMDD_lapNEXT_stale253_layer \
  --hd-source scale2x --esl2613 \
  --candidate-no-present-trace --candidate-no-unit-ticks \
  --stale-mask 55-90 --stale-mask-state 3 \
  --layer-drift --drift-samples '438,182;450,185;462,197'
```

The symbolic lap/date are replaced with the next actual runner counter/date.
Join by run identity, PS3 ordinal and game tick (watch label is the upcoming drift
present, not a universal ordinal). Carry forward `t:s` only when no new sample row
was emitted, because unchanged sample values are intentionally omitted. For each
mask-stale sample, compare screen/snapshot/coverage and cache/layer expected on that
same present; this partitions cache drift from a screen-only change without adding
diagnostic code. If that run localizes a screen-only event, use the existing
`--screen-watch --screen-watch-state 3` probe to seek a same-run stale writer; if
cache-only, existing `--screen-watch-cache` is the appropriate branch. A hit from
another stale-free run cannot close attribution. `scr != cache` by itself is normal
for overlaid units/cursors and does not prove cache drift.

Success: diagnostic sample stale and mask value2 agree in the same run/present,
then an actual writer/replay path is tied to that event. Non-reproduction is
NOT_REPRODUCED with run count and options; sample outside new event is UNKNOWN.
Do not require a speculative repair or manufacture a pass. Use one work lap/60min
or two failed hypotheses for the feasibility decision; traceable harness/input
defects are repaired and rerun in work tier under PROMPT③, without an artificial
one-execution cap. If missing same-event evidence persists, report that concrete
blocker instead of adding another strategy/review/card chain.

## Validation / limits

- Targeted existing contracts: `.venv/bin/python -m pytest -q tests/test_g1_mirror2x.py -k 'mirror_bridge_is_opt_in_and_pins_both_primitive_entries or mirror_reinvoke_uses_one_frame_width or clipped_replay_viewport or stale_mask_helper or layer_drift_sample_override or drift_samples_override or layer_drift_diagnostic'`.
  **7 passed,39 deselected/0.13s**, `logs/gates/lap1241-middle-focused.log`.
- Full make check/lint/typecheck, fresh DLL build/rollback and actual game: SKIP,
  document-only middle change; focused contracts and historical SHA review are not
  new runtime or full Fast approval. User-injected old full-test source does not match
  current source and was not reused as current PASS. Final document/safety evidence
  is appended below after writes.
- Windows/DxWnd, combat,24k/144k,multiplayer,user G1 acceptance: unverified.
  No product completion/next milestone boundary is crossed. Previous ESCALATE
  byte-exact copy `20261010_lap1241_preserved_lap1240_escalate_sol.txt` retained.
- Next action lives in STATUS only; this section is the immutable work contract
  arising from this review. No new user approval request or trial delivery.

- Final checks: `checks/safety.py check --require-game` SAFETY_PASS (original/protected pin unchanged), `checks/context_limits.py` CONTEXT_PASS, `git diff --check` exit0. Logs `logs/gates/lap1241-middle-{safety,context,diff-check}.log`; targeted log SHA `619fd8b4c5aa64dff71d0023cf728f6830d7c4636837e819ae17303e2a398f88`. STATUS91 before this final evidence line, INBOX260/APPROVALS36. No long-running command/game started; targeted command completed. Counter1241 unchanged.
