# G1 / ESL2613 G2 variants — lap1261 display probe boundary

2026-10-11 middle read-only adjudication; no runtime compatibility claim.
Evidence: shared `temp/Syw2plus_patch/20261011_lap1261_middle_variant_boundary/evidence.json`,
SHA256 `77e58803e1ac16f4800230e18c9f4537e50d565111fb247a38328bb49cdd5062`.

## Exact inputs and address evidence

Both read-only delivered inputs are 2,003,968 bytes:

- `[ESL]Syw2plus 2613_G2_G6_G8.exe`: `1e83466eab020818a6c0e9057508d71451af3ee1098af43ebefc20de8ab96e3d`.
- `[ESL]Syw2plus 2613_G2_G6_G8_G9_자리고정.exe`: `b612109b8cd9e313927871a5a35f28cc09b9c95f80626c938f4d42192cb00556`.

Both PE section tables have `.g2bss` VA `0x01AB5000`, virtual size `0x01891000`.
The existing packed geometry (`patches/esl2610/g2_runtime_layout_2610.py`)
derives capacity4093, stride`0x758`, existence`0x0220B9F8`.
Independent Capstone decode of each exact EXE also confirms:

| VA | Exact bytes | Instruction |
| --- | --- | --- |
| `0x00442FE9` | `66391c7df8b92002` | `cmp word ptr [edi*2 + 0x0220B9F8], bx` |
| `0x00443010` | `8d8e0050ab01` | `lea ecx, [esi + 0x01AB5000]` |
| `0x0044301B` | `8a860050ab01` | `mov al, byte ptr [esi + 0x01AB5000]` |

These are static address facts for these two SHAs. They do not authorize
other versions, pool writes, full save compatibility or arbitrary remapping.

## Activation, not mere presence of constants

- `tools/inmm_stub/inmm_stub.c:478`: ordinary build calls
  `sfx_probe_live_units()` automatically at PS3. `INMM_STUB_SFX_PROBE=0`
  has an effect **only** under `SYW2_G1_DEFAULT_ON` (`:385`, `:479`).
  The probe calls engine functions using stock-pool-derived unit types;
  it is not a harmless host read. Current diagnostic DLL cannot be reused
  unchanged by merely setting that environment variable.
- `inmm_stub.c:342`: any nonempty `INMM_STUB_NO_UNIT_TICKS` disables stock
  unit dumps. Explicitly set `1` in both lanes.
- `ai_shadow.c:117`: `INMM_AI_SHADOW=1` activates stock-unit shadow hooks.
  Keep it unset/0. `g1_state_snapshot.c:122` requires ticks/dir/run-id;
  remove those variables. Its payload still has stock1200 geometry.
- `patches/population/runtime_bridge.c:116`: supply operations require
  `SYW2_SUPPLY_PROBE=1`; exclude this module from the display build.
  A fresh prefix must have no control request file, so the executor's
  stock-unit operations are not invoked.
- `inmm_stub.c:81,460`: `UNIT0_QUEUE_CNT` remains a guarded read-only watch
  of `0x0066BB2C`. It can be logged but is invalid unit evidence on G2.
  Its presence is not proof of pool writes or a reproduced crash.
- `tools/g1_saved_scene_probe.py:7164` builds the ordinary diagnostic DLL
  with capacity1200. `:652`, `:4520` read stock arrays; `:4136` selects the
  official EXE, not either variant. `--scene-actions none` does not repair
  the initial detailed scene read. Current full pair is incompatible.
- Builder `--unit-pool-base/--unit-existence-base` adapts only its copied
  `runtime_bridge.c`; it does not adapt inmm dumps, SFX, snapshot, executor,
  host scene readers. Do not claim that those flags fix all paths.

## Decision

**FEASIBLE for a display-only probe with a different, explicit build profile;
HOLD for the unchanged diagnostic/full-unit pair.** Work should reuse the
existing private-copy build machinery and Makefile `default-on` target
without `runtime_bridge.c`, install the resulting DLL as `_inmm.dll` only in
each private game, and explicitly disable the above diagnostics. Preserve
the HD implementation and report the new DLL SHA/build flags. This confirms
presentation/load survival only; unit-state/input/production parity needs
an independently verified G2-aware reader if requested later.

No stock address rewrite, approved bridge pin change, EXE edit or fallback
guard weakening is authorized. Full work instructions are in
`docs/history/laps/20261011_lap1261_middle_g1_variant_display_boundary_handoff.md`.
