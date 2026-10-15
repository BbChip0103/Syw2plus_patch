# ESL2608 G1 Windows fault — 0x00464F20

## Evidence and scope

The user reports that stock ESL2608 with the same G1 DLL/HD assets works on
Windows, whereas both `260921_temp/legacy_2608/` variants show a black screen
and exit. User-provided diagnostic output records `0xC0000005`, exception
address/EIP `0x00464F20`, EXE base `0x00400000`, DLL base `0x559B0000`.
Raw text is preserved in shared temp
`20261014_legacy2608_windows_fault_464f20/user-windows-exception.log`.

Exact read-only legacy inputs: normal SHA256
`2e81ec32482070929a4405415f7c8c0635d966b655107aab47194b2f657fe55b`;
fixed-start SHA256
`34c2cb5c1049dcafe751a76686cc7618dae648a9b0b98760df67b98e1cd9330d`.

## Fault instruction / value flow

GNU objdump of the actual normal EXE and REA/Ghidra analysis identify
`FUN_00464EC0` (0x00464EC0–0x00465073), the renderer's surface-lock wrapper:

```text
00464F16  mov esi,[esp+0x214]   ; surface argument after local frame/saved registers
00464F1D  mov [ebp+0x18],edi
00464F20  mov ecx,[esi]        ; fault instruction site
00464F30  call [ecx+0x64]      ; DirectDraw surface Lock
```

The original caller return address is at `ESP+0x210` at this point. Wrapper
`0x00464E20` selects renderer fields `+0x151C` / `+0x1520` as primary/back
surface arguments. The current log does **not** record ESI, the accessed
address, or the AV operation. It therefore does not establish NULL, a stale
surface, or even read-vs-execute AV. No null-guard patch is justified yet.

REA retained function evidence: `ev_eef9dee83698623b233460dfb276fd75b071f2569564dcee8656993e3f1040c9`
(locker), `ev_981b77dd6af53bbaa82b8d00b077b2e16a6ac0cf9e5993a3b91ac0850ddd15db`
(initializer). GNU objdump evidence is separate from REA evidence.

## Ruled-out / unproven hypotheses

- Stock and legacy renderer initializer and lock-wrapper bytes match. Valid
  PE headers, section bounds, fixed EXE base, and matching G1 hook old bytes
  do not prove Windows runtime compatibility, but provide no header repair.
- The historical QHD row-table overrun is not established here. The EXE's
  mode-3 initializer keeps logical height 600; forwarding display mode to
  1600x1200 does not itself change that field. An early primary Lock call also
  precedes the row-table write loop. Do not relocate the table as a guessed fix.
- Previous Wine entry runs forced `WINEDLLOVERRIDES=ddraw=b` and renamed the
  EXE. They omitted app-local `ddraw.dll` (Ultimate ASI Loader 9.7.0, SHA256
  `ad5d8d449ce305caf62cb17d8698ebf17e94f9120ee993d0dd85211dfe14f8dd`)
  and `plugins/syw2x.asi` (SHA256
  `a320872eedd8b94b19ffb57886bc372335fed721770c73ddac63fcd6bd528895`).
- Two native-loader / actual-filename Wine attempts confirmed those modules
  loaded but stopped at helper window/content selection, not at the user's
  crash. They are NOT in-game PASS or crash reproduction. Their runtime
  copies/prefix processes were reclaimed. Further helper repair was stopped.

The Windows failure remains unresolved. A bounded diagnostic-context build
adds registers and AV information only; it is not a product fix. Original
games/EXEs, historical baseline source, current 2614 source and safety pins
remain unchanged.

## Later evidence / current boundary

The user subsequently corrected the Windows outcome: **legacy normal works;
only fixed-start crashes**, in the same complete game folder. The earlier
two-failure report is historical. The supplied fault record does not identify
which legacy variant produced it; do not assign it to the current fixed-start
failure without a fresh record.

After correcting only the private test adapter's owned-descendant window
selection, both actual EXE basenames reached PS3 by natural UI input under
Wine with app-local Ultimate ASI Loader and syw2x.asi loaded. Each has 256
state observations and a 1600x1200 in-game capture. Both used diagnostic DLL
SHA256 `56deacef30a7b68372a7b22935e58a9ac26f0450e6c17685271029a827d8b83b`
(unchanged G1 rendering); no feature-enabling environment overrides or BAT.
Evidence: shared temp `20261014_legacy2608_entry_normal/artifacts/` and
`20261014_legacy2608_entry_fixed_start/artifacts/`. Owned processes/prefixes
and game copies were reclaimed. Trace run-ID/close-summary validation failed;
normal detach/flush is not asserted. Entry proof is separate from that gap.

Exact normal/fixed EXEs differ by only four bytes at two locations:

| VA / file offset | Normal | Fixed | Meaning |
|---|---|---|---|
| 0x0041F2B0 / 0x1F2B0 | 8B | 8A | Byte inside JNE displacement; target changes 0x0041F33F → 0x0041F33E (include INC ESI), not a MOV opcode |
| 0x0042FBB1 / 0x2FBB1 | 0F BF D2 | 8B D3 90 | Random remainder MOVSX EDX,DX replaced by ordinal MOV EDX,EBX + NOP |

The initializer starts EBX at zero. These intentional G9 changes and valid
instruction boundaries do not alone identify a defect. No speculative
instruction rewrite or surface NULL guard has been applied. Current unresolved
scope is **Windows fixed-start only**, not generic G1 or normal legacy startup.
