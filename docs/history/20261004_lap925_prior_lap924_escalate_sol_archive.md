lap=924
role=ordinary-middle
reason=HOLD_OBSERVATION_WINDOW_CONFLICT
goal=G1 P5-T; G1 HOLD; milestone approval=none
handoff=docs/work/active/G1_MIDDLE_W70_P5T_OBSERVATION_WINDOW_HOLD_LAP924.md
history=docs/history/laps/20261004_lap924_middle_g1_p5t_observation_window_conflict_escalate.md
evidence=/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261004_lap924_middle_p5t_review/recalculation.json
evidence_sha256=baf36422eabd0447c096f246af4120c71a23f2394163ea56cf497bec695d48e4
conflict=lap918 forbids post-observation samples; lap923 Bprime1 accepted DOWN4/RIGHT12 post-boundary samples through post-snapshot max8s polling. Boundary-valid counts=26/18, not30/30. Existing raw PASS remains immutable.
verify=Confirm local Wine 10MHz frequency, snapshot/main-thread input ordering and receipt-anchored upper-bound calculation; independently reproduce late4/12 and normative mismatch. Then hand minimal observer/test repair to work tier; do not implement game code as middle.
work_handoff=tools/g1_saved_scene_probe.py plus related tests: bound30-present sampling to observation boundary, preserve exact input tick pre-arm repair, incomplete remains HOLD, cover late-flush-before-boundary versus newly-generated-after-boundary. Preserve schedule/thresholds/raw/golden/pins. Fresh GREEN+Bprime2+C3 and full Fast before next independent middle review.
stop=User current-session evidence-conflict stop applies. New runtime/full make check SKIP; old process exit0 is not current verification. No commits/deploy/original writes; G2/G5 closed, G3/G4 held.
