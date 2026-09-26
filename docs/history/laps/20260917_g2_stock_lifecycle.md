# G2 stock save/fresh-load lifecycle (2026-09-17)

Added a narrow `g2_stock_lifecycle("save"|"load", ...)` validator and exact
`g1-baseline --g2-stock-lifecycle` mode guards. It is restricted to the exact
G2 creation goal/candidate, rejects G4 intervention mixing, requires stock
stress for save, and requires stock stress disabled for fresh-load. The
validator does not launch a runtime, write memory, create/copy save files, or
retry native operations; the caller supplies the existing private op2/op3
result and snapshots.

Save validation requires a previously absent private `save/save###.dat` or
`SaveFiles/save###` file, byte hash, native op2/PS3/main-thread/profile witness,
actual type-cost reads through type52, eight live owners with 145 units and
used5000/count145/global1160, unique full IDs/slots, and owner4 HQ49 pending
command15/type7/progress100/res10 stable tick-bracket evidence. Fresh-load
also requires a byte-identical save copy, fresh PS7 creation, native op3, and
exact all-owner ledger/full-ID/slot/owner/type/HP mapping equality. Optional
raw pending 384/388/38C fields are reported as stable witnesses only, never as
atomic or first-postload proof. Death release, LAN, and product PASS remain out
of scope.

Validation: lifecycle plus stock/G2/runtime tests pass with Ruff and mypy; no
game, Wine, DLL build, or protected input was run or changed.
