# lap240 R6-B-R9 review report provenance

- `20260912_lap240_r6b_r9_review_report.attempt1.json` — first completed run,
  `verdict=FAIL`. The failures were a **probe harness defect**, not an
  implementation defect: the harness returned the moved camera from a fixed
  call-index list, so `read_camera` handed the already-moved value back as the
  minimap `camera_before` and the minimap predicate could never observe a
  change. Every downstream failure (clean path, 3 production cases, 3
  `after_minimap` cases) traced to that single `FAIL_NO_EFFECT`.
- Fix: the harness now returns `[180, 240]` only after the fixed minimap point
  `(150, 520)` has actually been clicked, so the predicate stays honest
  regardless of where an injected read failure shifts the call ordering. No
  product code, threshold, baseline, or golden asset was changed to make the
  probe pass.
- `20260912_lap240_r6b_r9_review_report.json` — the run after the harness fix,
  `verdict=PASS`. Both files are kept; the failed attempt is not deleted.
