# G1 P4b tick/rice writer — user-authorized read-only xrefs (2026-10-02)

## Pinned input and limits

- Original `Syw2plus/syw2plus_original.exe` SHA256 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, PE32 image base `0x400000`. This file was only read; no patch or runtime was made.
- Prior lap868 `pair-result.json` SHA256 `b8918cbcdc7b64f5bad5b9abb75340c3c2c9f8b99ec459c490a32d72863795cd`. Its final captured owner6 rice is baseline `230207`, candidate `231007` at bracketed tick `24862`; reads took `1.323275` and `2.346356` ms respectively. Both brackets are stable, not atomic or equal completed-phase proof.
- Commands: `sha256sum` on the pinned EXE/pair; `i686-w64-mingw32-objdump -d -Mintel --start-address=... --stop-address=...` on the pinned EXE; Python `pefile.get_offset_from_rva` to cross-check the bytes below. Addresses and bytes are for this exact SHA only.

## Static sequence (evidence, not runtime trace)

| VA | File offset | Pinned old bytes | Meaning |
|---|---:|---|---|
| `0x41C8C0` | `0x1C8C0` | `a1 b8 24 89 00 40 83 f8 14 a3 b8 24 89 00` | Load `0x8924B8`, increment, then store new tick at `0x41C8C9`. |
| `0x41C8F3` | `0x1C8F3` | `e8 48 02 00 00` | Later in the same function, call `0x41CB40`; return address is `0x41C8F8`. |
| `0x41CBB6` | `0x1CBB6` | `8b ce e8 13 32 02 00` | Within `0x41CB40`, call `0x43FDD0` with each player pointer; loop advances by `0x3ABC` for eight entries. |
| `0x41CBC6` | `0x1CBC6` | `a1 b8 24 89 00 83 e0 07` | Read the already-written tick and select `tick & 7`. The following arithmetic is `0x3ABC * owner`, added to player base `0x956770`. |
| `0x41CBE5` | `0x1CBE5` | `e8 e6 29 02 00` | Call selected player's `0x43F5D0` after tick storage. |
| `0x43ED64` | `0x3ED64` | `89 41 14` | In `0x43ED60`, write a DWORD to `PlayerStruct+0x14` (rice). |
| `0x43F8DA` | `0x3F8DA` | `e8 81 f4 ff ff` | One conditional path within `0x43F5D0` calls that rice setter. This path also changes wood, so it is **not** identified as the observed +800 cause. |
| `0x40B099` | `0xB099` | `8d 0c 95 70 67 95 00 e8 3b 3f 03 00` | A unit-owner path forms the player pointer and calls rice-add helper `0x43EFE0`. |
| `0x40B1A6` | `0xB1A6` | `8d 0c 95 70 67 95 00 e8 2e 3e 03 00` | A second unit-owner path does the same. |

At tick `24862`, `tick & 7 = 6`, and player6 rice VA is `0x956770 + 6*0x3ABC + 0x14 = 0x96C7EC`. `0x43EFB0` subtracts a caller-supplied rice amount and `0x43EFE0` adds one; both call `0x43ED60`. The two unit-owner add callsites compute a variable amount from unit fields; no static evidence ties either to the observed +800. Other callers/direct or bulk writes are not excluded. This xref does **not** identify which writer produced the +800 observation.

## Consequence and unproved boundary

`tools/g1_saved_scene_probe.py:282-348` reads tick before/after a sequential player/bitmap/unit bulk read. Because the pinned code publishes the new tick **before** calling player processing, a stable tick can bracket either an in-progress or a completed player update. The lap868 snapshot therefore cannot by itself classify the +800 as a committed simulation difference or a capture-phase artifact. The cross-process monotonic timestamps are not an equal-phase synchronization mechanism.

`0x41C8F8` is only a **candidate** post-`0x41CB40` observation point. No runtime breakpoint, writer event, thread identity, absence of other-thread writes, or phase-matched baseline control has been established. Do not use this address as an approved synchronization boundary, remove rice from parity, or accept B'. The next gated step would need a separately authorized probe/runtime trace that records the exact writer, old/new value, thread, and call sequence, then fresh private baseline-baseline and baseline-candidate controls at a proven completed boundary.

## lap874 bounded runtime observation (2026-10-02; not independent approval)

- Fresh read-only disassembly on the same pinned EXE shows the enclosing update continues after `0x41C8F8`: it performs timer/bookkeeping operations through `0x41C95B`, then returns at `0x41C961`. Old bytes at `0x41C8CE` are the next branch `72 23` after tick store `0x41C8C9`; old byte at `0x41C961` is `c3` (`ret`). Player-processing entry remains `0x41CB40`. Therefore `0x41C8F8` is interior, not the enclosing update return.
- lap874 used GDB hardware breakpoints at tick-published `0x41C8CE`, player processing `0x41CB40`, and enclosing return `0x41C961`, plus a hardware write watchpoint on owner6 rice `0x96C7EC`. The observer confirmed GDB all-stop and read full captured player/unit state while stopped at `0x41C961`. This establishes a bounded same-process observation point for that fixture/run; it does **not** independently approve `0x41C961` as a universal product synchronization boundary.
- The watched store was consistently post-store PC `0x43ED67`; the bytes immediately before it were `89 41 14`, identifying store instruction VA `0x43ED64` on this pinned image. Runtime thread global number was 1; each observed write had old/new values and occurred within the enclosing update interval. This does not exclude writers to other owners' rice fields.
- Fresh baseline×2 and Scale2x candidate×1 controls target absolute tick24862. Each had 195 owner6 rice writes; the target snapshot had tick before/after24862, PS3, camera[158,101], 8 player records/573 units, and owner6 rice231007. Full captured player/unit state hashes all matched `5ea805c8cca2d04c827d9e8d973b1ebe9ba7f868950eae604ee8598ae0b87ba7`.
- Raw artifact paths and hashes are in `docs/history/laps/20261002_lap874_work_g1_p4b_rice_phase_observer_controls.md`. The fresh control resolves the observed single-tick mismatch under this bounded fixture but needs independent middle review; it is not B' PASS or G1 acceptance.
