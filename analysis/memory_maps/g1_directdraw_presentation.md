# G1 DirectDraw presentation trace map

## Pinned executable

- SHA-256: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
- PE32 image base: `0x00400000`
- `.text`: VMA `0x00401000`, file offset `0x1000`, size `0xE3AE5`
- Source and lap108 private copy: `cmp=0`

## Import thunk and IAT slot

Independent lap109 `objdump -p/-d/-s` and raw-byte extraction establish two distinct addresses:

- code import thunk `0x004D7938`: `ff 25 18 50 4e 00`, decoded as
  `jmp dword ptr [0x004E5018]`;
- `DDRAW.dll` import descriptor: `OriginalFirstThunk RVA 0x000EB0C4`,
  `FirstThunk RVA 0x000E5018`, named member `DirectDrawCreateEx`;
- therefore the writable runtime IAT slot is `0x004E5018`, not the code thunk at
  `0x004D7938`. The on-disk IAT value `0x000EBB68` is the import-by-name RVA and is
  loader-replaced at runtime; it is not the callable runtime target.

The lap108 tracer compares `&ft->u1.Function` with `0x004D7938`, so a correctly parsed
DDRAW descriptor deterministically fails that comparison. The coarse two-event runtime
trace cannot exclude an earlier failure, but this mismatch alone is sufficient to reject
the current install contract.

## DirectDraw7 vtable layout

Installed MinGW header `/usr/i686-w64-mingw32/include/ddraw.h` SHA-256
`ae60c1c78b9669695809be11264f293fff70d33745571d3076f1e5b46b397950` defines:

- `IDirectDraw7`: 30 entries; `CreateSurface` index 6, `SetDisplayMode` index 21;
- `IDirectDrawSurface7`: 49 entries; `Blt` index 5, `BltFast` index 7,
  `Flip` index 11, `GetSurfaceDesc` index 22.

Lap108 uses Surface7 indices 6/8/12/23 and copies 64 entries, so merely correcting the
IAT address would redirect the wrong COM methods and over-read the declared vtable.
The work-tier repair should use typed vtable structs and `sizeof`/named members instead
of integer indices and oversized word counts.

## Remaining runtime facts

The lap108 raw trace has only `install/starting` and
`install/failed(stage=runtime_contract)`. It does not contain the loader-resolved IAT
target, DDRAW module range, DirectDraw object/surface identities, or present event.
Those values require one fresh private run only after the static/runtime guards and
fail-closed runner are repaired and tested.
