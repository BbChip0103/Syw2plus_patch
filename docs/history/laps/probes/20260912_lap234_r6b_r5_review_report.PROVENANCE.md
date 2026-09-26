# lap234 R6-B-R5 review probe — report provenance

- `..._report.attempt1.json`: first run. Case `A10_slot_addr_read_failure` expected
  `CORRUPTED` and was scored `DEFECT`. The expectation was wrong, not the implementation:
  `_read_selection` executes before the `try` in `_read_g1_selection_evidence`, so an
  OSError at the selection count/first-slot words escapes the reader (same as `A12`).
  That escape is absorbed by `_wait_state` (`read_error_count` →
  `UNKNOWN_STATE_READ_FAILURE`, R6-B-R6) and by the `g1_baseline` OSError handler,
  so it is fail-closed one level up.
- `..._report.json`: rerun after correcting only the `A10` expectation. No probe logic,
  no fixture, and no product/test code changed between the two runs.
- Both files are kept. Neither run is reconstructed or edited after the fact.
