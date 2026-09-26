# lap248 R12 review report — attempt provenance

## attempt1 (`20260912_lap248_r12_review_report.attempt1.json`, 41 bytes, truncated)

Probe harness defect, **not** a product finding and **not** an R12 measurement.
`run_pytest` returned `failed_tests` as a `set`, so the probe completed every
phase (C0~C3) and then died inside `json.dump` with
`TypeError: Object of type set is not JSON serializable`.

The R6-B-R11 exclusive-create convention (`args.output.open("x")`) had already
created the report file before serialization began, so the failure left a
41-byte truncated artifact on disk. attempt1 contains **no** measurement and
is preserved only because the loop contract forbids deleting evidence files.

Consequence worth queueing (**R21**, harness-convention defect, no product
impact): the shared probe output convention creates the evidence file before
the payload is known to be serializable, so any writer-side failure both loses
the run and — via the R6-B-R7 "refuse to overwrite existing evidence" guard —
blocks the retry at the same path. A serialize-then-exclusive-create order (or
exclusive create of a sibling temp plus `os.link`/rename) removes the window
without weakening R7/R10/R11.

## attempt2 (`20260912_lap248_r12_review_report.json`)

Same probe, `failed_tests` serialized with `sorted(...)`, no other change; this
is the attempt that carries the lap248 measurements. The mirror, the mutations
and the 81-case matrix were re-run from scratch for attempt2.
