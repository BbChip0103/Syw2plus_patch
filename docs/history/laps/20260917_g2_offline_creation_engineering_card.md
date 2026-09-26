# G2 offline creation integration — 2026-09-17 19:41 KST

## Verdict / scope
**GO: inactive engineering partial only. Full eight-player supply5000 stable-play objective remains active and unverified. No game/Wine run.**

Creator `443190` now constructs the Unit pointer using the operative UnitArena. Register `48BC00` uses the same relocated existence/age/active/category arrays and counters. Exactly13 disp32 operands were added separately from the unchanged frozen120 accessor family. Original CALL/control/body clearing/owner ledger/type-table/BULK bytes remain unchanged. Raw category lists have DWORD scale4.

## Verification
- Corrected RAW recipe `0694c732b488fba4fba3e4fbbceede4b36692db71290cac67434946e1d707994`:13 literal instruction records,52 unique operand bytes, complete reachable local CFG counts71/52/133/335. Root and Sol independently decoded original bytes and branches/CALLs/RETs.
- Actual candidate differs prior newgame-init candidatef092 at exactly52 bytes, all approved operands.133 typed destinations use the existing primary ABI. Six-arena geometry, CAP5000 composition and183-byte initialization wrapper are unchanged.
- Repaired strict validator rejects conflicting semantic metadata, partial overlaps and hard-reserved allocator/init/CAP collisions; genuinely identical full records produce an identical candidate.
- Fresh whole Fast **608 passed in112.68s**; Ruff/compileall/standard mypy10/explicit offline mypy1/context/shell checks passed. Five source pre/post and four protected original/shared hashes matched. Sol independent33 tests/no skips and reproduced all collision negatives: engineering GO.
- Actual current candidate is rejected by canonical and legacy launchers before process launch. All initialization/consumer/owner/spatial/save/LAN completion contracts remain false.

## Frozen artifacts
Case: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/g2_capacity/20260917_offline_creation_integration_v1/candidate_v2/`.
EXE: `8873b95d59340493831d02124be7fb2ce524b6dbda090d6d81fa8dcebee6b585`.
Module: `68419ed9dd982122f8c7793b949d2bad7635932a58a95030ef30279b83d17271`.
Tests: `d33ffa704b0a9286080513630177a3ff0bd6dbc8a14c04014ca346c894fc7fff`.
Exact five-source archive, root_creation_card_verification.json, archive_receipt.json and fresh logs remain external.

## Rejected results retained
First RAW recipe included owner ledger counters, omitted an active counter read and absorbed following opcode bytes. It was rejected, preserved and replaced by independently decoded literal records. First code batch passed603 tests but its validator accepted matching old bytes with conflicting target semantics; root reproduced corrupted Unit pointer target and Sol rejected it. The fixed batch passes new regressions; the old source/candidate/logs remain preserved, not promoted.

## Following bounded work
Owner registration/removal `43EE30/43EEC0` direct four Unit-field address operands, after pinned recipec334/root+Sol conditional GO. Owner1200 roster guard and accounting remain original. Removal searches low WORD ID, not generation-qualified DWORD; preserve behavior and do not claim fullID correctness from this local audit. Transitive creation/removal, owner capacity, spatial, expanded save/load, supportedLAN and actual24k/144k remain unresolved. No fault chasing/third guard run.
