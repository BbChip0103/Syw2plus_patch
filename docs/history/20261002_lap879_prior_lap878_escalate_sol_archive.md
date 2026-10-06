# lap878 — escalate to middle/Sol

Scope: G1 W70 P4b; bounded observer-only scroll phase diagnostic. B'/G1 remain HOLD. Do not run another game/runtime attempt until the tick conflict is independently explained.

Authority: `docs/history/laps/20261002_elevated_g1_p4b_scroll_phase_scope_decision.md` authorized only observation edits to `tools/g1_saved_scene_probe.py` and its test, with fixed r1 schedule and full stopped-thread/state evidence. It forbids game/DLL/validator/threshold edits and says stop on unprovable completion/quiescence or unexplained state/input mismatch.

Work result: lap878 added phase-only multi-checkpoint observer and tests. Focused tests: 41 passed; ruff and py_compile passed. Full make check was not run; no current fingerprint PASS. Original EXE/save hashes match pinned values. Five diagnostic roots are preserved under `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261002_lap878_p4b_scroll_phase_triplet{,_r2,_r3,_r4,_r5}/`.

Blocking evidence: r5 baselineA, baselineB and candidate each failed at the same absolute RIGHT input target: target/observer phase tick 24788, but `runtime_driver` read 24728 before and after injection. Raw shows 24692 entry+return followed by repeated unmatched return records at 24728; no complete 24824/24860 snapshots or stopped-state proof. Cause is UNKNOWN. Per-session record and raw SHAs: `docs/history/laps/20261002_lap878_work_g1_p4b_scroll_phase_diagnostic_hold.md`.

Next owner (Sol/middle): independently inspect r5 `probe-result.json`, phase-events, `gdb.log`, generated `observer.py`, and code; explain whether the tick discrepancy is observer phase semantics, stale/incorrect pause handshake, or remote memory read timing. Verify that one checkpoint proves exact same-thread entry→terminal return, complete stopped-thread census through bulk read/release, and exact input delivery on its registered tick. If not provable within the approved observation-only scope, return a concrete BLOCKED/NOT_FEASIBLE finding to strategy. Do not reinterpret 24728 as 24788, filter raw events, relax criteria, call 0x41C961 a general boundary, enter C/P5, or claim B'/G1 PASS.
