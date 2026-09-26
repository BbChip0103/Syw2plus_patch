# lap410 — G2 unit-pool 1210 actual-runtime spike

## Verdict

**Engineering feasibility: PASS for relocating, allocating, freeing, and reusing
slots above 1200.**
This is not yet a product/stability/save/LAN PASS.

The exact-hash candidate moved `unit_pool`, `unit_existence`, and `unit_age` to
the PE tail, raised the allocator bound to 1210, and fixed every reviewed code
reference (pool 1014, existence 34, age 4).  A fresh private Wine run reached
PS9→PS7→PS3 and the relocated reader observed active slots 1200..1209.

## Exact artifacts

- Pool-only candidate: `a3fd29340fa4d0fbd39b77127ef2d7f1b4993fe9453d0f2d32f981296aa73b41`
- Pool+fixed-5000 candidate: `90ed0bad35821c86553a0a0e163b93c892ff254fe4c1cdaba5a0deb0a31f6b91`
- N=1210 diagnostic bridge: `ee30a21bbeb6357fd8b36bf39a7f82649bb831dfe75a0933278a002ce9ecffd4`
- 12-minute combined-run trace:
  `temp/Syw2plus_patch/g2_capacity/20260920_unit_pool_expansion/lap409_combined_bridge1210_runtime/stability_reuse_watch.jsonl`
  SHA-256 `92fa7bc0288fe0cb6de84bb62dd400bf0ad2e66c900726ced5eb18b92e39ef16`
- Initial combined snapshot SHA-256
  `197ea87c68e9522b45d06c733c36bdbd2d6b56b43a05c82c59e0ffa20ebad9c5`
- Screenshot (external temp only) SHA-256
  `5685272fb014f4bb59fa7f71325a6c7e4a4b9602fe2cfc553ae4e82452efd2fe`

## Runtime observations

1. Original positive control reached PS9 with the same corrected launch
   envelope.  The earlier PS40 result was a legacy-driver bootstrap mismatch,
   not an executable result.
2. Pool-only candidate reached PS3 and created live units in slots 1200..1209.
3. In the first two-owner run, slot 1209 (HQ49) was read at HP 4800, fell to
   HP 0, then its relocated existence entry changed 49→0.  Thus allocation and
   destruction/release above the stock ceiling were both executed.
4. The combined pool+5000 run created 8 owners and the N=1210-aware native
   diagnostic bridge added 141/142 type-5 units per owner.  Immediate snapshot:
   1162 active units, active span 48..1209, all eight caps 5000.  The monitored
   run began at 1165 active, RSS 244096 KiB.
5. The 721-second observation did not crash.  The allocator reached slot 1,
   wrapped, and repeatedly reused released slots with different full IDs.
   Examples: slot 1113 `66649→722009`, slot 1188 `394404→918692`, slot 1196
   `918700→1196`.  Final observed RSS was 251792 KiB.
6. A follow-up N=1250 candidate deliberately placed ordinary combat units in
   slots 1200..1227.  Slot 1219 (type5, owner0) was initially active with full
   ID 984259, was released at elapsed 52.1 s, and after allocator wrap was
   reallocated at elapsed 412.685 s as type110 owner3 with full ID 197827.
   This closes the exact `slot >= 1200 creation → read → death/release → reuse`
   spike condition.  The run had 1170 active units at that PASS sample.
   Evidence `lap411_n1250_runtime/ge1200_reuse_watch.jsonl`, SHA-256
   `ee8fd5209a50d71bf6507bf995abfaca368027d4f957b8f19248d1266246037b`.

## Remaining acceptance gaps

- The relocated existence/age arrays leave the stock bulk save/load ABI.
  Expanded save/load requires an explicit format/translation repair.
- LAN serialization and deterministic peer agreement are untested.
- This was a high-cost assisted load followed by natural AI simulation, not an
  arbitrary-composition 8×5000 release soak.  Supply overshoot via original
  owner-transfer semantics and signed-16 ledger limits remain separate risks.

## Verification

`pytest` over the pool layout, combined builder, executable launch gate, and
project setup: **50 passed in 153.56 s**.  Python compile checks passed.
