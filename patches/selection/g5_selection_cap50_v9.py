#!/usr/bin/env python3
"""v8 plus a one-site hook that zeroes the relocated selection array on every
new-game start, matching the original's own invariant.

lap752 (``docs/history/laps/
20260928_lap752_middle_g5_f_s3_newgame_init_gap_v9_handoff.md``) found -- by
static disassembly, not runtime -- that the stock game-state initializer
``0x004A3060`` (called from three sites, ``0x0041B9C0``, ``0x0041BC4F``, and
``0x004C3E59``, every game start and "play again") does two things to the
legacy selection window after its own bulk ``rep stosd`` zeroes the whole
``0x00892410``-based save-state block:

- ``0x004A3168 mov dword ptr [esi+0x6c14], ebx`` zeroes the legacy selection
  *count* (``[this+0x6c14]`` aliases ``0x00899024``, the same field v1's
  ``DIRECT_SITES`` relocated away from) a second, explicit time;
- ``0x004A31EB``..``0x004A321A`` loops 20 times zeroing the legacy *entries*
  window and two unrelated 20-word arrays.

v1..v8 relocated every live selection reader/writer to a new 50-slot array
at ``SELECTION_BASE`` (``0x0108C000``) and never re-pointed this
new-game-init code at it, so the new array is *never* explicitly cleared on
a fresh game start. Its emptiness on a real new game has depended entirely on
an unrelated invariant: that every unit removed during the *previous* game's
teardown called the deselect half of the toggle at ``0x00412D90`` (dec path,
``0x00412ED2``), which happens to also clear the new array's slots one at a
time. lap751 confirmed that invariant holds for "play again" (restart uses
the teardown/dec path, not the load wrapper), but the *original* game does
not rely on teardown at all -- it clears the selection state directly and
unconditionally at every new-game entry point, independent of whatever
happened before. That is a real behavioral gap, not just an unproven
analogy: a caller who reaches ``0x004A3060`` through any path that skips
full unit teardown (or if ``0x00412D97``'s early-return guard,
``word ptr [0x00B93988] == 1``, ever suppresses the dec) would start a new
game with a stale >20-entry live selection in the relocated array while the
legacy window it mirrors from is correctly zero -- silently reintroducing
the exact invariant break class v7/v8 already had to fix once (H-STALE-TAIL).

Fix: hook the single instruction at ``0x004A3168`` (6 bytes,
``89 9e 14 6c 00 00``) with a ``jmp`` into a small cave that reproduces the
original ``mov [esi+0x6c14], ebx`` untouched, then additionally zero-fills
the entire relocated selection array (``SELECTION_BASE`` .. ``+0xcc``, the
count dword plus all 50 entry dwords) before jumping back to
``0x004A316E``, the byte immediately after the original instruction. No
other byte of the hooked function changes, the replacement is exactly 6
bytes (``jmp rel32`` + 1 ``nop``) so nothing downstream needs to shift, and
every register the surrounding code still reads after this point (``esi``,
``ebx``; ``eax``/``ecx``/``edi`` are all re-initialized by the immediately
following code before their next read, confirmed by disassembly) is
preserved via ``pushad``/``popad`` regardless. The cave lives in the same
``.rsrc`` raw padding v7/v8 already use for their own wrappers
(``RSRC_CAVE_OFFSET`` ``0x2100``..``0x2200``), immediately after it
(``0x2200``..``0x2240``), confirmed zero-filled in the original file and
untouched by every earlier candidate in this chain.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

import keystone
import pefile

from patches.selection import g5_selection_cap50_v8 as v8

IMAGE_BASE = v8.IMAGE_BASE
ORIGINAL_SHA256 = v8.ORIGINAL_SHA256
SELECTION_BASE = v8.SELECTION_BASE
STOCK_CAPACITY = v8.STOCK_CAPACITY
TARGET_CAPACITY = v8.TARGET_CAPACITY
SELECTION_DWORDS = 1 + TARGET_CAPACITY  # count dword + 50 entry dwords = 0x33

RSRC_CODE_END_OFFSET = v8.RSRC_CODE_END_OFFSET  # 0x2200, end of v7/v8's own cave

NEWGAME_HOOK_VA = 0x004A3168
NEWGAME_HOOK_OLD = bytes.fromhex("89 9e 14 6c 00 00")
NEWGAME_RESUME_VA = NEWGAME_HOOK_VA + len(NEWGAME_HOOK_OLD)

# Callers of 0x004A3060 (informational only -- every one of them reaches the
# same hooked instruction, so the hook covers all of them regardless of
# which is attributed at runtime): 0x0041B9C0, 0x0041BC4F, 0x004C3E59.
NEWGAME_INIT_CALLERS = (0x0041B9C0, 0x0041BC4F, 0x004C3E59)

NEWGAME_CAVE_OFFSET = RSRC_CODE_END_OFFSET
NEWGAME_CAVE_END_OFFSET = NEWGAME_CAVE_OFFSET + 0x40

BuildAbortedError = v8.BuildAbortedError

_NEWGAME_ZERO_ASM = f"""
    mov dword ptr [esi+0x6c14], ebx
    pushad
    mov edi, {hex(SELECTION_BASE)}
    mov ecx, {SELECTION_DWORDS}
    xor eax, eax
    rep stosd dword ptr es:[edi], eax
    popad
    jmp {hex(NEWGAME_RESUME_VA)}
"""


def _va_to_file_offset(pe: pefile.PE, va: int) -> int:
    return v8._va_to_file_offset(pe, va)


def _assemble(asm: str, address: int) -> bytes:
    ks = keystone.Ks(keystone.KS_ARCH_X86, keystone.KS_MODE_32)
    encoding, _count = ks.asm(asm, address)
    if encoding is None or len(encoding) < 1:
        raise BuildAbortedError("keystone produced no bytes")
    return bytes(encoding)


def _jmp_rel32(source_va: int, target_va: int) -> bytes:
    return b"\xe9" + struct.pack("<i", target_va - (source_va + 5))


def build_candidate(original: bytes) -> tuple[bytes, dict[str, Any]]:
    candidate_v8, v8_report = v8.build_candidate(original)
    out = bytearray(candidate_v8)
    pe = pefile.PE(data=bytes(out), fast_load=True)
    try:
        rsrc = next((s for s in pe.sections if s.Name.rstrip(b"\0") == b".rsrc"), None)
        if rsrc is None:
            raise BuildAbortedError(".rsrc section missing")
        rsrc_va = IMAGE_BASE + int(rsrc.VirtualAddress)
        if rsrc_va != SELECTION_BASE + 0x1000:
            raise BuildAbortedError(f"unexpected relocated .rsrc VA 0x{rsrc_va:08x}")
        if int(rsrc.SizeOfRawData) < NEWGAME_CAVE_END_OFFSET:
            raise BuildAbortedError(".rsrc raw padding is too small for the new-game-init cave")
        raw = int(rsrc.PointerToRawData)
        cave = bytes(out[raw + NEWGAME_CAVE_OFFSET : raw + NEWGAME_CAVE_END_OFFSET])
        if cave != bytes(len(cave)):
            raise BuildAbortedError("new-game-init cave region is not zero-filled")

        hook_off = _va_to_file_offset(pe, NEWGAME_HOOK_VA)
        actual_hook_old = bytes(out[hook_off : hook_off + len(NEWGAME_HOOK_OLD)])
        if actual_hook_old != NEWGAME_HOOK_OLD:
            raise BuildAbortedError(
                f"0x{NEWGAME_HOOK_VA:08x}: pinned old bytes mismatch "
                f"expected={NEWGAME_HOOK_OLD.hex()} actual={actual_hook_old.hex()}"
            )

        cave_va = rsrc_va + NEWGAME_CAVE_OFFSET
        cave_code = _assemble(_NEWGAME_ZERO_ASM, cave_va)
        if len(cave_code) > NEWGAME_CAVE_END_OFFSET - NEWGAME_CAVE_OFFSET:
            raise BuildAbortedError(f"new-game-init cave too large: {len(cave_code)} bytes")

        hook_new = _jmp_rel32(NEWGAME_HOOK_VA, cave_va) + b"\x90"
        if len(hook_new) != len(NEWGAME_HOOK_OLD):
            raise BuildAbortedError("hook replacement changed instruction length")

        out[raw + NEWGAME_CAVE_OFFSET : raw + NEWGAME_CAVE_OFFSET + len(cave_code)] = cave_code
        out[hook_off : hook_off + len(hook_new)] = hook_new

        section_off = rsrc.get_file_offset()
        struct.pack_into(
            "<I", out, section_off + 8,
            max(int(rsrc.Misc_VirtualSize), NEWGAME_CAVE_END_OFFSET),
        )
        if int(rsrc.Characteristics) & v8.v7.RSRC_EXECUTE_CODE_FLAGS != v8.v7.RSRC_EXECUTE_CODE_FLAGS:
            raise BuildAbortedError(".rsrc is not already marked executable by v7/v8")
    finally:
        pe.close()

    if len(out) != len(original):
        raise BuildAbortedError("candidate changed raw file length")
    candidate = bytes(out)
    report = {
        "schema": "syw2plus.g5-selection-cap50-newgame-init-candidate.v9",
        "status": "SELECTION_CAP50_NEWGAME_INIT_ZEROED",
        "original_sha256": ORIGINAL_SHA256,
        "v8_candidate_sha256": v8_report["candidate_sha256"],
        "candidate_sha256": hashlib.sha256(candidate).hexdigest(),
        "hooks": {
            "newgame_init": {
                "site": hex(NEWGAME_HOOK_VA),
                "resume": hex(NEWGAME_RESUME_VA),
                "cave_va": hex(cave_va),
                "bytes": len(cave_code),
                "callers": [hex(a) for a in NEWGAME_INIT_CALLERS],
            },
        },
        "rsrc_cave": {
            "offset": hex(NEWGAME_CAVE_OFFSET),
            "end_exclusive": hex(NEWGAME_CAVE_END_OFFSET),
        },
        "known_limit": (
            "only closes the H-NEWGAME-INIT gap (relocated selection array not "
            "zeroed by the original's own new-game/restart initializer); does not "
            "change save/load behavior (v7/v8 scope) or persist entries 21..50 to disk"
        ),
        "v8_report": v8_report,
    }
    return candidate, report


def restore_candidate(candidate: bytes, original: bytes) -> bytes:
    v8.v7.v3.v1.verify_original(original)
    expected, _report = build_candidate(original)
    if hashlib.sha256(candidate).digest() != hashlib.sha256(expected).digest():
        raise ValueError("candidate SHA256 mismatch; refusing to restore unknown bytes")
    return bytes(original)


def write_candidate(original_path: Path, destination: Path) -> dict[str, Any]:
    if destination.resolve() == original_path.resolve():
        raise ValueError("refusing to overwrite the original EXE")
    original = original_path.read_bytes()
    patched, report = build_candidate(original)
    destination.write_bytes(patched)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    print(json.dumps(write_candidate(args.original, args.destination), indent=2))


if __name__ == "__main__":
    main()
