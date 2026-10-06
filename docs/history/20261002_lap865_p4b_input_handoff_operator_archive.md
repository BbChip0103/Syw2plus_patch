# lap865 middle: G1 P4b HOLD — unresolved input and post-scroll scene evidence

User-directed escalation: preserve evidence and end this ordinary middle session.
No C gate, P5 implementation, milestone completion, or new runtime in this session.
Previous lap864 marker is preserved byte-exact in
`docs/history/20261002_lap865_prior_lap864_escalate_sol_archive.md`.
Review: `docs/history/laps/20261002_lap865_middle_g1_p4b_input_parity_hold_handoff.md`.
Recomputed artifact:
`/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261002_lap865_middle_p4b_review/recomputed.json`
SHA256 `1b2affe15058cadc1c6bdfe9502e8dc72881c7bfa03a028ad6a1d0bd48f8f355`.

Confirmed: original/fixture/pair/raw/DLL and all 42 build inputs match. Candidate
DOWN/RIGHT 30-present p50 365324/352704, layer moves 1/512, transfers30 each,
unsupported/outside diff0; unchanged Scale2x validator PASS1203. Legacy errors1203
are exclusively nearest-oracle differences, expected under scale2x gate (not a
legacy PASS). Source-matched runtime output is partial, not B' or G1 completion.

Conflict: baseline DOWN [158,101]->[171,114], candidate ->[159,102]. Receiver
WndProc down/up timestamps differ by2/29ms but do not measure actual XTest hold.
Post-scroll scene false: baseline560/candidate563 unit records, candidate-only
slots35/36/37, owner2 cap2100/2300. Direct cause UNKNOWN; do not normalize away.
Fixed camera before DOWN has14 samples; first20/last20 persistence unproven.

Confirmed harness defects: arm file followed immediately by keydown without
receiver installation acknowledgement; camera movement cannot release the key
until receiver_down exists; action camera sampled before keyup with no one-cell
requirement or post-release settle check. These can bias input measurement, but
existing raw lacks emission/ready/baseline camera timeline to establish the
13-step cause. Do not call product parity PASS or repeatedly re-review the same
raw without obtaining the missing evidence.

Elevated Sol must verify this diagnosis, post-scroll scene difference, and the
bounded handoff. Then explicitly return hands-on work to Luna/Sonnet work tier:
1. Same opt-in receiver-ready ack in both lanes, wait before keydown; failure INVALID.
2. Preserve emission monotonic, ready/receipt and camera timestamps. Release at
   first camera change independently of receipt availability; finally keyup on
   timeout/exception. No gdb or lane fallback, no EXE/game-logic writes.
3. Observe stable camera after keyup; DOWN(+1,+1), RIGHT(+1,-1), identical per-key
   and final camera in both lanes. Missing receipt/overshoot/no change INVALID.
4. Behavioral regressions for delayed receiver, readiness failure, late camera
   movement and release on exception; then new gdb-free same-save paired runtime.
   Recompute both30-present gates plus fixed first20/last20 persistence and explain
   or repair scene mismatch using actual progression evidence. Do not relax gates.
5. Implement->diagnose->repair->rerun traceable defects within the work session
   per PROMPT③. Only independent B' full PASS permits C fresh3; D-1 precedes P5.

Fresh doctor/lint/typecheck and focused36 tests PASS. Full make check, DLL build,
new runtime SKIP under the user's immediate-conflict escalation/end instruction.
Previous lap864 full Fast is not current-fingerprint verification. No source
implementation, original writes, commits, or user milestone approval this session.
