# G2 ESL2608 Phase-C hero/rally static judgment — lap802

## Scope

This is the lap802 static close requested by the 2026-09-30 09:58 operator
instruction. It does not replace the missing runtime hero fixture. Protected
baseline and the two existing candidate EXEs were read only.

Inputs:

- baseline normal: `../260921_temp/[ESL]Syw2plus 2608_AI상점개설_장수7명_전비1600-200-3000.exe`
  SHA256 `cade60b2451519ec4e305d91279b1c377cf797c813a939c5b54c2e9b30b176a3`
- candidate normal: `../260921_temp/[ESL]Syw2plus 2608_AI상점개설_장수7명_전비1500-500-5000_G2_개인500_공용4092.exe`
  SHA256 `83c7df80a3273d95d58e7a493866bbb40ad705d10120bc05db660400961fad60`
- candidate fixed-start: `../260921_temp/[ESL]Syw2plus 2608_AI상점개설_장수7명_전비1500-500-5000_시작자리고정_G2_개인500_공용4092.exe`
  SHA256 `1bdcadf9edeccc16d92696e580a60fc71f13a13b6bba22cafb8c9f50e749262f`

Commands:

```text
sha256sum <three EXEs>
objdump -Mintel -d <baseline> | rg "43e7f0|412540|4af400|4af5e0|+0x654|+0x656"
objdump -Mintel -d --start-address/--stop-address <baseline>  # 0x406b00, 0x412540, 0x43e7f0, 0x48d180, 0x48b080
python3 read-only byte comparison of baseline and each candidate at the paths below
```

## Baseline paths

### HQ rally writer

`FUN_00412540` is the UI command writer. For command `0x15` it writes the
packed map target into the selected object passed in `ecx`:

```text
0x00412540..0x004125D3
  compare action == 0x15
  [ecx+0x654] = low16(target)
  [ecx+0x656] = high16(target)
  call 0x004A9A40
```

The caller at `0x00412659` supplies the selected object's command payload;
the writer has no lookup of a newly produced unit and no hero-specific branch.

### Hero production/eligibility path

The production decision path at `0x00406B00` calls `0x0043E7F0` at
`0x00406B68`. The same eligibility function is called from the hero-related
branch at `0x0048D1B7`; that branch then emits the event through
`0x004AF400` at `0x0048D22B`. `FUN_0043E7F0` contains the indexed hero-count
gate at `[ecx+0x980]` (`0x0043E8F7..0x0043E906`). The normal production
completion path in the AI selector calls `0x004AF5E0` at `0x00406C5C`.

These calls do not call `FUN_00412540`, and no hero-specific code reads an
HQ's `+0x654/+0x656` fields.

### New-unit initialization / rally fields

The exhaustive disassembly search for `+0x654/+0x656` found these writes:

- `0x00411B85/0x00411B8C`: new unit initialization clears both fields.
- `0x00412589/0x00412590` and `0x004125A5/0x004125AF`: the HQ/UI writer above.
- `0x0048B12F/0x0048B136`: a type-flagged unit receives its own spawn
  coordinates plus three; this is not a copy from an HQ.

The only relevant read is the command/dispatch path at `0x0047F793`, which
consumes the unit's own rally fields. No cross-object `HQ rally -> completed
unit` copy is present in the baseline static path. Therefore the user report
that a produced hero may not follow an HQ rally is consistent with original
behavior, but the lap800 fixture did not establish a runtime hero order and
does not prove the report either way.

## Candidate diff judgment

Both candidates have identical relevant results:

```text
0x00412540..0x00412600  diff bytes: 0
0x0043E7F0..0x0043E914  diff bytes: 0
0x0048B080..0x0048B1AF  diff bytes: 0
0x0048D180..0x0048D23F  diff bytes: 0
0x004AF400..0x004AF461  diff bytes: 0
0x004AF5E0..0x004AF647  diff bytes: 0
```

The candidate changes in nearby `.text` are relocation operands for the new
unit pool (`0x00406C09/0x00406C16`, `0x0043EE82`, and related pool references)
plus the two documented supply immediates at `0x0043FEA0` and `0x0043FFD5`.
They do not alter the hero eligibility/counter instructions, the HQ rally
writer, or the unit initialization instructions listed above. `.rdata`,
`.data`, `.rsrc`, `.psndata`, and `.shopai` payloads are unchanged by the
candidate comparison.

## Judgment

`HERO_RALLY_STATIC = ORIGINAL_PARITY / RUNTIME_UNKNOWN`.

The G2 candidate does not touch the baseline hero-specific or HQ-rally
implementation paths. The hero runtime fixture remains unverified because
lap800 could not obtain the prerequisite ownership cache; this is not a G2
product FAIL. Close the hero subtask and continue with Phase D (minimap gate
parity, real combat, and high-slot portrait checks). Keep the separate DxWnd
result as `BLOCKED(env: DxWnd game target launch)`.
