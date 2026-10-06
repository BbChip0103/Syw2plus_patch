lap: 848
date: 2026-10-02 KST
role: ordinary_middle
status: RAW_PERFORMANCE_EVIDENCE_CONFLICT_CONFIRMED
target: G1 W70 P3 HOLD; no P4 or milestone transition; no plan approval

Current-session user stop condition applies: prior performance PASS conflicts with actual simulation counter raw.
Evidence/handoff: docs/history/laps/20261002_lap848_middle_g1_p3_conflict_confirmation_handoff.md
Independent raw confirmation: /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/lap848_middle_confirmation/confirmation.json
confirmation_sha256=d7ac5afae7af42bdcacab4bddc82a11bd691583628b11829756b71d1c414b0fc
Trace clock0x9B5210 differs from sim tick0x8924B8. Existing action-window rate deltas=-38.873199/-38.500290/-39.712340%; not a controlled benchmark. Baseline timing samples cap2048; p95 windows are incomparable.
Promoted middle: verify HOLD and authorize bounded work-tier measurement repair described in the lap record, followed by fixed monotonic PS3 sim-rate/present-p95 fresh3-pair validation. Work diagnoses/repairs reproduced slowdown; ordinary middle does not implement or approve its own plan.
Full Fast and runtime this lap: SKIP due explicit user stop-on-evidence-conflict; old exit0 is not current verification. Partial Scale2x evidence preserved. Current single queue is docs/STATUS.md.
Previous marker preserved byte-exact: docs/history/20261002_lap848_prior_lap847_escalate_sol_archive.md, SHA256 2c5caa0f410ee4ca642b8727130592cb37fa250fa41faa666ed8ca058004babe.
No game/harness/binary edits, no game runs, no original/reference writes, no commits.
