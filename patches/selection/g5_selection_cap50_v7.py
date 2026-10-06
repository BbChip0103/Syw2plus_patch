#!/usr/bin/env python3
"""v6 plus a save/load shadow mirror for the raw (non-group) selection.

lap739 (``docs/history/laps/
20260928_lap739_work_g5_checklist_f_saveload_selection_regression.md``,
``loop/ESCALATE_SOL`` lap739 section, operator direction 2026-09-28 14:05)
found that a raw drag selection (no Ctrl+digit group assignment) does not
survive save/load in v1..v6: the stock save/load routines bulk-copy a fixed
memory window (``push 0xe397c; push 0x00892410; call 0x004da39f`` on save,
the mirror ``call 0x004da4a9`` on load -- addresses independently confirmed
by this project's own G2 persistence experiment,
``patches/population/g2_full_capacity_persistence_v1.py``, and by
``analysis/memory_maps/g2_supply_ledger_200c_site_inventory_lap509_20260923.md``
line 108-109) that includes the *legacy* selection count/entries at
``0x00899024``/``0x00899028``. v1's ``DIRECT_SITES`` relocated every known
live reader/writer of those two addresses to the new ``SELECTION_BASE``
(``0x0108c000``) and never wrote them again, so the bulk-saved window always
captures zero there, regardless of how large the live (relocated) selection
is -- this reproduces exactly lap739's observation (original raw selection
round-trips through save/load; candidate's never does).

Fix: hook the two block-transfer call sites themselves (not the many
individual selection consumers) with a shadow mirror that runs entirely in
already-allocated, file-backed padding inside the relocated ``.rsrc``
section's own raw data (``0x0108d000 + 0x20f0 .. + 0x3000``, confirmed zero
in the v6 candidate and unused by any resource directory content -- the same
kind of raw section padding ``g2_full_capacity_persistence_v1.py`` already
uses for its own code cave, just a different physical byte range since that
module's candidate has a different relocated layout):

- ``SAVE_WRAPPER`` replaces the ``call 0x004da39f`` at ``0x00440f0c`` with a
  ``call`` to itself. It reads the live selection count from
  ``SELECTION_BASE`` (capped to the stock 20 capacity), writes that count and
  the first ``min(count, 20)`` entries into the legacy
  ``0x00899024``/``0x00899028`` window (zero-filling any unused legacy
  slots), then tail-jumps into the original ``0x004da39f`` with the stack
  completely untouched -- the bulk block it is about to copy to disk now
  contains a valid, save-compatible shadow of the live selection.
- ``LOAD_WRAPPER`` replaces the ``call 0x004da4a9`` at ``0x004412dc``. It
  re-issues the original call with the same four arguments (the standard
  "re-push from an ebp frame, call, clean up" idiom this project already
  uses in ``g2_full_capacity_persistence_v1._emit_stream_wrapper``), which
  performs the real load of the bulk block (repopulating
  ``0x00899024``/``0x00899028`` from the save file exactly as stock does),
  and then mirrors those legacy values back into ``SELECTION_BASE`` so the
  relocated live selection reflects what was actually saved.

This changes no file offsets, block sizes, or call counts in the save
stream -- it only ensures a live memory window that was already being copied
verbatim gets a meaningful value first (save) and is propagated back to the
relocated live copy afterward (load). A vanilla original EXE reading a v7
save, or v7 reading a vanilla/v1..v6 save, sees exactly the same
20-capacity legacy bytes it always could; nothing new is read past the end
of the existing block.

Scope note (explicitly accepted, not silently dropped): only the first 20
of a >20-entry live selection round-trip through save/load this way, the
same ceiling the stock game itself has always had. Preserving entries
21..50 would require extending the on-disk save format (a new trailing
block or magic-gated region) and was not attempted in this lap -- see the
module docstring's "next" pointer in the accompanying lap doc for the
follow-up plan (append a block at the true end of the save stream, after
the last existing block and before the file is finalized, so no reader that
stops after its own known reads ever sees it).
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

from patches.selection import g5_selection_cap50_v3 as v3
from patches.selection import g5_selection_cap50_v6 as v6

IMAGE_BASE = v6.IMAGE_BASE
ORIGINAL_SHA256 = v6.ORIGINAL_SHA256
SELECTION_BASE = v6.SELECTION_BASE
STOCK_CAPACITY = v6.STOCK_CAPACITY
TARGET_CAPACITY = v6.TARGET_CAPACITY

LEGACY_COUNT_ADDR = 0x00899024
LEGACY_ENTRIES_ADDR = 0x00899028

SAVE_CALL_VA = 0x00440F0C
LOAD_CALL_VA = 0x004412DC
STREAM_SAVE_FN = 0x004DA39F
STREAM_LOAD_FN = 0x004DA4A9

SAVE_CALL_OLD = bytes.fromhex("e8 8e 94 09 00")
LOAD_CALL_OLD = bytes.fromhex("e8 c8 91 09 00")

RSRC_CAVE_OFFSET = 0x2100
SAVE_WRAPPER_OFFSET = RSRC_CAVE_OFFSET
LOAD_WRAPPER_OFFSET = RSRC_CAVE_OFFSET + 0x80
RSRC_CODE_END_OFFSET = RSRC_CAVE_OFFSET + 0x100
RSRC_EXECUTE_CODE_FLAGS = 0x20000020


class BuildAbortedError(RuntimeError):
    """Raised when a pinned byte, PE invariant, or assembler output does not match."""


def _va_to_file_offset(pe: pefile.PE, va: int) -> int:
    return v6._va_to_file_offset(pe, va)


def _call(source_va: int, target_va: int) -> bytes:
    return b"\xe8" + struct.pack("<i", target_va - (source_va + 5))


_MIRROR_TO_LEGACY = f"""
    mov ecx, dword ptr [{hex(SELECTION_BASE)}]
    cmp ecx, {STOCK_CAPACITY}
    jle keep_count
    mov ecx, {STOCK_CAPACITY}
keep_count:
    mov dword ptr [{hex(LEGACY_COUNT_ADDR)}], ecx
    mov ebx, ecx
    mov esi, {hex(SELECTION_BASE + 4)}
    mov edi, {hex(LEGACY_ENTRIES_ADDR)}
    rep movsd dword ptr [edi], dword ptr [esi]
    mov ecx, {STOCK_CAPACITY}
    sub ecx, ebx
    xor eax, eax
    rep stosd dword ptr [edi], eax
"""

_MIRROR_FROM_LEGACY = f"""
    mov ecx, dword ptr [{hex(LEGACY_COUNT_ADDR)}]
    cmp ecx, {STOCK_CAPACITY}
    jle keep_count
    mov ecx, {STOCK_CAPACITY}
keep_count:
    mov dword ptr [{hex(SELECTION_BASE)}], ecx
    mov ebx, ecx
    mov esi, {hex(LEGACY_ENTRIES_ADDR)}
    mov edi, {hex(SELECTION_BASE + 4)}
    rep movsd dword ptr [edi], dword ptr [esi]
    mov ecx, {STOCK_CAPACITY}
    sub ecx, ebx
    xor eax, eax
    rep stosd dword ptr [edi], eax
"""

_SAVE_WRAPPER_ASM = f"""
    pushad
    {_MIRROR_TO_LEGACY}
    popad
    jmp {hex(STREAM_SAVE_FN)}
"""

_LOAD_WRAPPER_ASM = f"""
    push ebp
    mov ebp, esp
    push dword ptr [ebp+0x14]
    push dword ptr [ebp+0x10]
    push dword ptr [ebp+0xc]
    push dword ptr [ebp+0x8]
    call {hex(STREAM_LOAD_FN)}
    add esp, 0x10
    pushad
    {_MIRROR_FROM_LEGACY}
    popad
    pop ebp
    ret
"""


def _assemble(asm: str, address: int) -> bytes:
    ks = keystone.Ks(keystone.KS_ARCH_X86, keystone.KS_MODE_32)
    encoding, _count = ks.asm(asm, address)
    if encoding is None or len(encoding) < 1:
        raise BuildAbortedError("keystone produced no bytes")
    return bytes(encoding)


def build_candidate(original: bytes) -> tuple[bytes, dict[str, Any]]:
    candidate_v6, v6_report = v6.build_candidate(original)
    out = bytearray(candidate_v6)
    pe = pefile.PE(data=bytes(out), fast_load=True)
    try:
        rsrc = next(
            (section for section in pe.sections if section.Name.rstrip(b"\0") == b".rsrc"),
            None,
        )
        if rsrc is None:
            raise BuildAbortedError(".rsrc section missing")
        rsrc_va = IMAGE_BASE + int(rsrc.VirtualAddress)
        if rsrc_va != SELECTION_BASE + 0x1000:
            raise BuildAbortedError(f"unexpected relocated .rsrc VA 0x{rsrc_va:08x}")
        if int(rsrc.SizeOfRawData) < RSRC_CODE_END_OFFSET:
            raise BuildAbortedError(".rsrc raw padding is too small for the save/load wrappers")
        raw = int(rsrc.PointerToRawData)
        cave = bytes(out[raw + RSRC_CAVE_OFFSET : raw + RSRC_CODE_END_OFFSET])
        if cave != bytes(len(cave)):
            raise BuildAbortedError(".rsrc save/load cave region is not zero-filled")

        save_va = rsrc_va + SAVE_WRAPPER_OFFSET
        load_va = rsrc_va + LOAD_WRAPPER_OFFSET
        save_code = _assemble(_SAVE_WRAPPER_ASM, save_va)
        load_code = _assemble(_LOAD_WRAPPER_ASM, load_va)
        if len(save_code) > LOAD_WRAPPER_OFFSET - SAVE_WRAPPER_OFFSET:
            raise BuildAbortedError(f"save wrapper too large: {len(save_code)} bytes")
        if len(load_code) > RSRC_CODE_END_OFFSET - LOAD_WRAPPER_OFFSET:
            raise BuildAbortedError(f"load wrapper too large: {len(load_code)} bytes")

        out[raw + SAVE_WRAPPER_OFFSET : raw + SAVE_WRAPPER_OFFSET + len(save_code)] = save_code
        out[raw + LOAD_WRAPPER_OFFSET : raw + LOAD_WRAPPER_OFFSET + len(load_code)] = load_code

        section_off = rsrc.get_file_offset()
        struct.pack_into(
            "<I", out, section_off + 8,
            max(int(rsrc.Misc_VirtualSize), RSRC_CODE_END_OFFSET),
        )
        struct.pack_into(
            "<I", out, section_off + 36,
            int(rsrc.Characteristics) | RSRC_EXECUTE_CODE_FLAGS,
        )

        for call_va, old_bytes, target_fn, wrapper_va in (
            (SAVE_CALL_VA, SAVE_CALL_OLD, STREAM_SAVE_FN, save_va),
            (LOAD_CALL_VA, LOAD_CALL_OLD, STREAM_LOAD_FN, load_va),
        ):
            off = _va_to_file_offset(pe, call_va)
            expected = _call(call_va, target_fn)
            if old_bytes != expected:
                raise BuildAbortedError(
                    f"0x{call_va:08x}: pinned old bytes do not match expected call to 0x{target_fn:08x}"
                )
            actual = bytes(out[off : off + 5])
            if actual != expected:
                raise BuildAbortedError(
                    f"0x{call_va:08x}: old bytes mismatch expected={expected.hex()} actual={actual.hex()}"
                )
            out[off : off + 5] = _call(call_va, wrapper_va)
    finally:
        pe.close()

    if len(out) != len(original):
        raise BuildAbortedError("candidate changed raw file length")
    candidate = bytes(out)
    report = {
        "schema": "syw2plus.g5-selection-cap50-saveload-shadow-candidate.v7",
        "status": "SELECTION_CAP50_SAVELOAD_LEGACY_SHADOW_20",
        "original_sha256": ORIGINAL_SHA256,
        "v6_candidate_sha256": v6_report["candidate_sha256"],
        "candidate_sha256": hashlib.sha256(candidate).hexdigest(),
        "hooks": {
            "save": {"site": hex(SAVE_CALL_VA), "wrapper_va": hex(save_va), "bytes": len(save_code)},
            "load": {"site": hex(LOAD_CALL_VA), "wrapper_va": hex(load_va), "bytes": len(load_code)},
        },
        "rsrc_cave": {
            "offset": hex(RSRC_CAVE_OFFSET),
            "end_exclusive": hex(RSRC_CODE_END_OFFSET),
        },
        "shadow_capacity": STOCK_CAPACITY,
        "known_limit": (
            "only the first 20 live selection entries round-trip through save/load; "
            "entries 21..50 are not preserved (same ceiling as the stock game)"
        ),
        "v6_report": v6_report,
    }
    return candidate, report


def restore_candidate(candidate: bytes, original: bytes) -> bytes:
    v3.v1.verify_original(original)
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
