# G2 offline newgame-init engineering batch — 2026-09-17 19:20 KST

## Verdict
**Engineering partial GO; full G2 active and incomplete. No game launch.**
Priority remains actual eight participants, each supply cap 5000, arbitrary legitimate composition and stable production/combat/death/reuse/save/load/supported LAN; actual 24k/144k evidence is still required.

## Implemented / verified
- Existing original-only PE builder now composes the existing fixed-supply-5000 utility (five actually changed bytes), without modifying original input.
- One operative RW/non-executable `.g2stg` contains six 4001-slot engineering arenas and three WORD counters. 4001 is not proven final capacity adequacy.
- A separate RX/non-writable `.g2ini` wrapper calls original `4A3060` once, preserves its returned registers/flags/DF/stack, copies old 1200-entry prefixes and three counters into those same operative arrays, and zeroes the 2801-entry tails. No Unit body, original bulk clear, removal or owner ledger changes.
- Stub: 183 bytes, 51 decoded instructions. Old 120 typed operands and three allocator operands retain the existing operative storage identity.
- Fresh full Fast: **598 passed in 100.86s**. Ruff, compileall, standard mypy ten files, explicit offline-module mypy, context and shell checks passed; source pre/post pins and protected original/shared pins matched. Sol independent 23 tests and raw instruction audit: GO for this inactive engineering batch only.
- Canonical and legacy launchers reject the actual incomplete candidate before launching processes. Informational inspect output is not ABI certification.

## Frozen evidence
Raw case: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/g2_capacity/20260917_offline_newgame_init_v1_v3/`.
Candidate SHA256: `f092ecbfe800bff3420afffdd0d73d33ae97ab7076586530d2e39011b114047c`.
Module SHA256: `e029a263d29fc5da90cf09432e44235b920ca9b5e972e64a81ea1e24659d1977`.
Tests SHA256: `d4aebdca9ebcad2eea5a4300019717ab28c3b8b73d3f1017b0a79549b7fa7ba2`.
Exact five source files are archived in `frozen_source_bundle`; `archive_receipt.json`, `root_newgame_init_card_verification.json`, `paired_fast.log`, and pre/post pin logs remain outside the repository.

## Rejected results retained
First newgame-init candidate `e9e99d...280923` initialized unused duplicate arrays instead of operative storage. Root rejected it, author removed the duplicates, and decoded-destination regression assertions now lock array identity. A subsequent weak geometry assertion was also rejected and corrected before final validation. Old cases are preserved, not promoted.

## Next finite batch / limits
Sol conditional GO: raw recipe for creator `443190`, register `48BC00`, plus unchanged body-pointer lineage audit `48B000`/direct `411A00`. Expected 13 address operands only, exact original bytes and local CFG bounds required before implementation. No recursive census, no getter-fault chasing, no third guard trial.
Transitive constructor calls, removal/reset, owner capacity, spatial bounds, expanded save/load and LAN remain unresolved; this is not creation closure, restart/load closure or runtime approval.
