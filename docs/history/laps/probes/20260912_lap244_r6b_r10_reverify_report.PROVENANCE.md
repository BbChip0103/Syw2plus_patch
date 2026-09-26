# lap244 middle R6-B-R10 re-review — probe attempt provenance

attempt1 (`...reverify_report.attempt1.json`, verdict=FAIL) is preserved as the raw record of a
**review-harness** defect, not a subject defect. The harness scored the three existing-evidence
cases (C09/C10/C11) with `output_created == False`, but those fixtures create the file at the
output path by construction, so `Path.exists()` is True before the run as well. The subject
(`20260912_lap228_r6b_r3_review_probe.py`) behaved correctly in all three: `exit 2`, the
`refusing to overwrite existing evidence` classification, no traceback, fixture bytes preserved.

Repair: the harness now records `existed_before` and requires a refusal to leave path existence
unchanged, and a healthy run to create a report that did not already exist. No subject file,
test, threshold, or product artefact was changed. An earlier crash (`FileNotFoundError` on the
earliness workdir) was a missing `mkdir(parents=True)` in the harness and produced no report.
