# G2 six-arena relocation diagnostic runtime boundary

This lane adds a **default-off, one-shot diagnostic boundary** to
`tools/runtime_env.py`; it is not a 1200→1201 allocator implementation and
does not claim consumer safety, normal G2 completion, save/load, or LAN
correctness.

## Activation contract

`g1_baseline(..., g2_relocation_diag_build=ABSOLUTE_BUILD_MANIFEST)` requires
the exact G2 creation goal and `g2_supply_5000.exe`, rejects stock stress,
stock lifecycle, G4 interventions, and ordinary sampling, and requires a
fresh artifact directory under the approved external temp root. The reviewed
DLL SHA is fixed only for the separately reviewed diagnostic build; an absent
or altered pin is fail-closed. Existing 8de5 stock/G4 gates remain separate.

The build manifest contract is intentionally singular and is pinned to the
Sol-reviewed private DLL SHA-256
`8a2da2eafc4e9fb47960f7ecfebf697b3ef8ed23472e0c6745969e80737d3688`:

```json
{
  "diagnostic_only": true,
  "diagnostic_mode": "g2_six_arena_failstop_v1",
  "capacity": 1201,
  "patch_count": 47,
  "dll": "/absolute/private/_inmm.dll",
  "dll_sha256": "<reviewed SHA>",
  "original_stub_inputs": {"path": "<64-hex SHA>"}
}
```

The private game copy must contain the same reviewed DLL; no shared/canonical
deployment is performed by the runtime harness. A missing/overridden review
pin remains fail-closed.

## Native op/raw contract

After the existing PS3 eight-owner creation gate and before old unit readers,
the harness writes exactly one request:

```text
<request_id> 6 0 0 0 0 0 0
```

The native fail-stop writer publishes exactly 4096 bytes at
`C:\\g2_relocation_fault.bin`. The 49-DWORD (196-byte) native
`diag_manifest_t` keeps the first 27 DWORDs, then records the exact eight
request words, initial PS3/profile, caller/window threads, old-pool guard
range, copy/tail checks, stage, patch-manifest offset/count, and initial
counters (including `initial_ps3 == 3`, `profile_check_ok == 1`, status 0,
and the recorded caller/window-thread identity). The fixed fault marker offset is 512 and the 20-DWORD
`diag_fault_record_t` begins there; 47 five-DWORD patch records begin at
offset 640. The harness requires stage 5, copy/tail checks, exact guard
interior, all 47 valid patch records, magic `0x524C4631`, version 1, capacity
1201, patch count 47, arena count 6, original caller `0x0042334C`, guard
interior `0x0066C000..0x00892000`, patch
bytes written 47, and the fault marker/version published last. It retains
request ID, copy ticks, exception thread, fault address, exception PC, and
register context without inventing main-thread/profile equivalence; a null
fault address is valid, while PC/EIP must be equal and nonzero.

Only a complete armed/applied raw record is classified
`OBSERVED_RELOCATION_DIAGNOSTIC_FAULT`; malformed, partial, missing, or
unpublished records are `BLOCKED_RELOCATION_DIAGNOSTIC_BOUNDARY`. The normal
G1 UI/sample tail is suppressed after op6, while cleanup and artifact flushing
remain fail-closed and separate from the movement/product verdict.

Validation: `tests/test_g2_relocation_diag.py` (15 tests), plus the existing G2
stock/lifecycle/creation guards (42 targeted tests total).
