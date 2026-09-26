---
name: patch-validation
description: Validate original PE32 patches without modifying original assets or confusing historical captures with new runtime proof.
---

# Patch validation

Read AGENTS.md and docs/STATUS.md. Run `make doctor` then `make check`.
Verify input SHA, exact expected old/new bytes, unsupported-version rejection,
copy-only output, non-overlap for combined patches and byte-exact restore.
For runtime changes use a private complete game copy, fresh Wine prefix and unused display.
Record candidate SHA and distinguish fresh execution from captured-fixture regression.
Never count ticks across a load rewind. Keep synthetic fixtures explicit.
Write PASS/FAIL/SKIP, commands, evidence and remaining risks to the current work card.
No publishing, commits or original binary writes as a side effect of validation.
