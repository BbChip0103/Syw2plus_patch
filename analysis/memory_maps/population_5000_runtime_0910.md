# Original fixed supply 5000 feasibility — 2026-09-10

## Scope and status

Experimental verification only. Preserve the original EXE and all existing game sessions.
Target fixed supply limit 5000 (not base 5000 plus hero bonuses), retaining original
object-count and shared-slot limits. No claim of LAN support or release readiness.

## Binary identity and confirmed offsets

- Profile: repository `Syw2plus/syw2plus_original.exe`, x86 PE32, 1,032,192 bytes.
- SHA256: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
- LAA unset. Image base 0x400000. For the sites below file offset = VA - image base.
- Fresh original-byte disassembly, not reconstructed Plan C behavior.

| VA | Original bytes | Experimental replacement | Meaning |
|---|---|---|---|
| 0x0041B576 | `66 c7 00 dc 05` | `66 c7 00 88 13` | Initial cap 1500 -> 5000 |
| 0x0043FFD4 | `05 dc 05 00 00` | `b8 88 13 00 00` | Recomputed cap becomes fixed 5000, not 1500 + bonus |

The second replacement preserves instruction length and the following word store at
0x43FFD9. It intentionally does not alter hero accounting preceding the final store.

Sources: `analysis/ghidra_output/FUN_0041b560.c:22-29`,
`FUN_0043fdd0.c:78`, `FUN_0043eda0.c:8-23`, `FUN_0043f0c0.c:9-25`.

## Existing evidence

Original byte-identical .text executed in an isolated ELF32 synthetic-state harness:
20/20 boundary, separate count/pool, recalculation and reservation/accounting assertions
passed. This is NOT actual gameplay. Scratch source/log: `/tmp/syw2_feasibility_20260910/`.

## Runtime proof plan

1. Hash-guarded copied-EXE patch with exact restore test; never edit `Syw2plus/` originals.
2. Private copied game directory, independent Wine prefix and unused Xvfb display.
3. Actual game: persistent cap, original production >2500 and at 5000 boundary.
4. Actual save/load roundtrip; continue simulation/production after load.
5. Report fixture writes explicitly; no hidden count, resource, AI, or production bypasses.
6. Record failures as failures; screenshot/title alone does not prove production.

## Runtime results — feasibility established

**Runtime observed:** the original PE32 game runs fixed supply5000 and true QHD together.
No 64-bit conversion, Plan C simulation, or complete source recovery was needed.
This is an existence proof on this exact executable/profile, not release certification.

### Actual army and production (run3)

A fresh custom battle began with owner0 HQ(type49) and worker(type7), count2/supply20.
The diagnostic bridge called ORIGINAL placement, capacity gate, and spawn functions to
seed 142 type5 units costing35 each. The resource fixture left used20 unchanged before
seeding, and used4990 unchanged after seeding. This is not the earlier run2 inflated-ledger test.

- Tick16: 144 distinct live entities; independently summed original type costs =4990.
- Tick934: original HQ production admitted a worker, deducted rice800, reserved10.
- Tick937: original save011 captured that pending production.
- Tick1653: 145 distinct entities; 142×35 + 2×10 workers + HQ10 =5000;
  reserved0, production complete.
- Tick1657: another worker request was refused, with no reservation and visible
  Korean “전비가 부족합니다”. A raw train function return1 alone was NOT treated as proof.
- Tick1661: original save012 captured the completed army.

The 142-unit initial army was engine-seeded and resources were supplied for the test;
only the final worker used normal timed production. No claim that the whole army was
naturally trained. The captured entity roster, unique IDs, original costs and ledger agree.

### Combined real QHD + supply5000 (run4)

Combined SHA256: `d22904639adf03ddf2b6b3122a64a59131770e5ad85107290229e6932b319abc`.
The current QHD builder plus the two non-overlapping supply instruction edits reproduce
this exact hash in a regression test. The combined manifest records 76 guarded code ranges;
QHD also adds PE section metadata/storage. Another agent restored a separate copy and
verified the exact original hash; the original game directory was not patched.

- Original load012 restored the completed real 145-entity army at used5000.
- Original renderer readback: mode3, width2560, height1440, bpp8, pitch2560, rows1440.
- Real X11 click (1280,730) selected original HQ slot1199; this exceeds the old screen width.
- Original load011 reset the game tick to937 and restored count144, used4990, reserved10.
- Original production resumed and completed once to count145, used5000, reserved0.
- Another production request at5000 was refused without creating a reservation.

The final load reset is explicitly accounted for in endurance measurements; time before
that load is not accumulated toward the final continuous 24k interval.

### QHD is not just an output scaler

See [QHD address-level report](original_qhd_probe_0910.md). The successful patch relocates
fixed terrain/dirty-mask buffers, expands map rendering and clipping, fixes full-redraw
stale pixels, and relocates a 1024-entry row table whose overflow otherwise corrupts a
DirectDraw pointer at row1034. The original rendering path produces native-scale sprites
on a 2560×1440 scene. Standalone real mouse and keyboard camera tests also passed.
This was a fixed-buffer/layout problem, not a prohibition inherent to PE32.

### Evidence and limits

Durable JSON: `patches/population/verification_0910/`; its manifest pins EXE/save hashes.
Private runtime: `/tmp/syw2_supply_runtime_20260910/run{1,2,3,4}`.
Best combined screenshot:
`/home/dev_00/sharedfolder/260320_Syw2plus/temp/20260910_043326_supply5000_combined_5000_qhd.png`.

No native Windows, LAN synchronization, all-map/all-nation/hero coverage, or 144k release
validation is claimed. The QHD HUD anchor/hitbox layout remains unfinished. Ordinary
combat can lower current supply after the boundary check; constant cap5000 does not mean
constant current supply5000. Per-owner count250 and original shared object pool remain.
The initial request's 12-player expansion is NOT established by these tests: the current
player table/one-byte alliance field still use the original eight-player layout
(`player_offsets.md`). A successful supply/resolution patch does not imply 12-player support.

### Reproducibility boundary

The EXE patches themselves do not depend on the diagnostic DLL. The tested environment
uses a private copied game directory, independent Wine prefix and Xvfb, existing
DirectDraw wrapper and short intro fixtures. A copied inmm diagnostic build drives the
original custom-game entry and invokes original functions at the verified outer-loop
call site. This is instrumented original-game execution, not a test on an unmodified
retail installation or evidence for every native Windows driver.


## Final continuous endurance — PASS

After last original load011 at tick937, the captured final epoch starts at969 and
ends at25773: **24,836 continued game ticks**, 743 one-second samples spanning744.13s.
All samples remain original PROGRAM_STATE3; all eight player cap fields remain5000.
Maximum adjacent sampling gap is35 ticks, no later rewind. The independent watcher
passed first at24970 (24,033 ticks). `run4_endurance_summary.json` hashes the retained
full `run4_trace.jsonl`; the regression test independently locates the last load rewind.

AI remained enabled and real combat/production continued: owner0 current supply ranged
1070..5000, ending well below5000 because units died. This is a continuous combined-patch
simulation test, **not** a claim that the maximum army survived or remained at5000
for the whole interval. No FPS benchmark, complete economic correctness proof or
144k release gate is implied.

Verification: 14 focused pytest tests, Python ruff, mypy on the three supply Python
implementation tools, diagnostic C compiler/analyzer review, byte-exact restore checks.
The private runtime was stopped after capture; original EXE SHA remained unchanged.
