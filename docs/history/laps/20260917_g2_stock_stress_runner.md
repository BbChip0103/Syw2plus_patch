# G2 stock stress runner (2026-09-17)

Added an explicit `g2_stock_stress=True` path to `g1_baseline`. It is enabled
only with the approved eight-owner creation goal, fixed-supply candidate, and
bridge hash. The phase sets `SYW2_SUPPLY_PROBE=1` only in that branch, uses the
existing native supply request/result files. It runs three bounded phases:
all eight native op1(worker) admissions, one op5(type 5, 142) seed per owner,
then joint observation of all worker completions. The op1 return value alone
is not admission evidence: the bridge must provide an atomic before/after
ledger pair and same-HQ full-ID/type49 producer record, followed by a bounded
same-HQ command15/production-type7 plus reservation observation or a genuine
new worker ID. op4/resources,
commands, save/load, retries, and AI normalization are excluded.

The phase has an independent 300-second monotonic deadline, partial external
flushes on every request/error, and is excluded from the existing startup/UI
budget. It enforces native costs, owner cap 242 (eight-slot headroom), global
1199-slot plus pending headroom (including all remaining owners and workers), per-spawn
ledger/roster attribution, worker full-ID completion, and final cost
reconciliation. Result classification is
`ASSISTED_LOCAL_HIGH_COST_ONLY`, never full G2/LAN PASS.

Validation: targeted runtime/G2 tests and new stress guards pass with Ruff and
mypy; no game, Wine, DLL build, or protected input was run or changed.
