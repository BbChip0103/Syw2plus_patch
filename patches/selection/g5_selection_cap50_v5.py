#!/usr/bin/env python3
"""v4 with the R3 sparse-selection gate fix (``docs/history/laps/
20260927_lap721_middle_g5_v4_r1_confirmed_falsified_r3_sparse_gap.md``,
``loop/ESCALATE_SOL`` lap721 section, 2026-09-28 01:30 user direction step ②).

lap721's independent review confirmed v4's chunk-wrapper is byte-identical to
v3 below the order-type gate: ``check_count`` looks only at the live
selection-array *count* field, and if it is ``<= 20`` falls straight through
to the original, unchunked function body -- which copies a fixed
``entries[0:20]`` window regardless of what is actually alive further into
the (fixed-capacity, 50-slot) array. lap721 also confirmed (independently of
this project's earlier R1 leak claim) that the array is written by an
in-place-zero removal routine with no compaction: a unit that dies while
selected leaves its own slot zeroed, but every other selected unit's slot
stays exactly where it was. So a selection that starts at 50 (living in
``entries[0:50]``) and loses enough units to *any* index < 20 that its count
drops to <= 20, while survivors remain at index >= 20, hits the intersection
of both facts: the count-only gate sends the order down the unchunked path,
which never even reads ``entries[20:50]`` -- the survivors receive nothing.
This is R3, and this module is the fix v4's own docstring predicted for it
(v4 residual risk R1/R3 paragraph): the gate becomes "count > 20 **or**
``entries[20:50]`` contains a live (nonzero) slot", not "count > 20" alone.

Everything else -- the inverted order-type gate that picks whether to even
consult ``check_count`` at all, the three fixed-size chunk copy windows, the
80-byte backup/restore, the relocated original body -- is v4's, byte-for-byte
unless this docstring's fix requires touching it. Only ``check_count``'s body
changes: it gains a 30-dword scan of ``entries[20:50]`` (``CHUNK1_OFFSET`` is
already the address of ``entries[20]``, and it is contiguous through
``entries[49]`` since the whole array is one 50-slot allocation), preserving
whatever registers it uses (``esi``, ``ecx``) across both exits so it makes
no assumption about what the caller needs live in either the chunked or the
unchunked path -- neither v3 nor v4 assumed anything about ``eax`` past this
point either, so this fix does not narrow that existing assumption.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import keystone
import pefile

from patches.selection import g5_selection_cap50_v2 as v2
from patches.selection import g5_selection_cap50_v3 as v3
from patches.selection import g5_selection_cap50_v4 as v4

IMAGE_BASE = v4.IMAGE_BASE
ORIGINAL_SHA256 = v4.ORIGINAL_SHA256
SELECTION_BASE = v4.SELECTION_BASE
TARGET_CAPACITY = v4.TARGET_CAPACITY
STOCK_CAPACITY = v4.STOCK_CAPACITY

ENTRIES = v4.ENTRIES
CHUNK_UNITS = v4.CHUNK_UNITS
CHUNK1_OFFSET = v4.CHUNK1_OFFSET
CHUNK2_OFFSET = v4.CHUNK2_OFFSET
CHUNK2_REAL_UNITS = v4.CHUNK2_REAL_UNITS
SPARSE_SCAN_UNITS = TARGET_CAPACITY - CHUNK_UNITS  # entries[20:50], 30 dwords

HOOK_SITE = v4.HOOK_SITE
HOOK_OLD = v4.HOOK_OLD
BODY_END = v4.BODY_END
BODY_LEN = v4.BODY_LEN
EXTERNAL_CALLS = v4.EXTERNAL_CALLS
CAVE_BASE = v4.CAVE_BASE
CAVE_LIMIT = v4.CAVE_LIMIT

_MOVSD = v4._MOVSD
_STOSD = v4._STOSD

KNOWN_NON_ORDER_SINGLES = v4.KNOWN_NON_ORDER_SINGLES
KNOWN_NON_ORDER_RANGES = v4.KNOWN_NON_ORDER_RANGES

_OLD_COUNT_CHECK = f"""check_count:
    movzx eax, word ptr [{hex(SELECTION_BASE)}]
    cmp eax, {CHUNK_UNITS}
    jle original_body
"""
_NEW_COUNT_CHECK = f"""check_count:
    movzx eax, word ptr [{hex(SELECTION_BASE)}]
    cmp eax, {CHUNK_UNITS}
    jg do_chunk

    push esi
    push ecx
    mov esi, {hex(CHUNK1_OFFSET)}
    mov ecx, {SPARSE_SCAN_UNITS}
sparse_scan:
    cmp dword ptr [esi], 0
    jne sparse_found
    add esi, 4
    dec ecx
    jnz sparse_scan
    pop ecx
    pop esi
    jmp original_body
sparse_found:
    pop ecx
    pop esi

do_chunk:
"""

if _OLD_COUNT_CHECK not in v4._WRAPPER_ASM:
    raise RuntimeError("v4 check_count anchor text not found; v5 cannot patch it")

# v4's wrapper is v3's text with only the leading order-type gate replaced;
# it carries v3's check_count block through unchanged. Swap only that block.
_WRAPPER_ASM = v4._WRAPPER_ASM.replace(_OLD_COUNT_CHECK, _NEW_COUNT_CHECK, 1)


class BuildAbortedError(RuntimeError):
    """Raised when a pinned byte, PE invariant, or assembler output does not match."""


def _va_to_file_offset(pe: pefile.PE, va: int) -> int:
    return v4._va_to_file_offset(pe, va)


def _assemble_wrapper() -> bytes:
    ks = keystone.Ks(keystone.KS_ARCH_X86, keystone.KS_MODE_32)
    encoding, _count = ks.asm(_WRAPPER_ASM, CAVE_BASE)
    if encoding is None or len(encoding) < 1:
        raise BuildAbortedError("keystone produced no wrapper bytes")
    if encoding[-1] != 0x90:
        raise BuildAbortedError("expected trailing nop placeholder for original_body label")
    return bytes(encoding[:-1])


def build_candidate(original: bytes) -> tuple[bytes, dict[str, Any]]:
    # v4.build_candidate() builds on top of v2; reuse that same base directly
    # (v4 itself is only a gate swap over v3, which is a gate swap over v2).
    candidate_v2, v2_report = v2.build_candidate(original)
    out = bytearray(candidate_v2)
    pe = pefile.PE(data=bytes(out), fast_load=True)
    try:
        body_off = _va_to_file_offset(pe, HOOK_SITE)
        body_bytes = bytes(out[body_off : body_off + BODY_LEN])

        wrapper_bytes = _assemble_wrapper()
        body_addr = CAVE_BASE + len(wrapper_bytes)
        cave_end = body_addr + BODY_LEN
        if cave_end > CAVE_LIMIT:
            raise BuildAbortedError(
                f"cave overflow: wrapper+body ends at 0x{cave_end:08x} > limit 0x{CAVE_LIMIT:08x}"
            )
        relocated_body = v3._relocate_body(body_bytes, body_addr)
        cave_bytes = wrapper_bytes + relocated_body

        cave_off = _va_to_file_offset(pe, CAVE_BASE)
        existing = bytes(out[cave_off : cave_off + len(cave_bytes)])
        if existing != bytes(len(cave_bytes)):
            raise BuildAbortedError("cave region is not zero-filled before write")
        out[cave_off : cave_off + len(cave_bytes)] = cave_bytes

        v3._patch_exact(out, pe, HOOK_SITE, HOOK_OLD, v3._hook(HOOK_SITE, CAVE_BASE, HOOK_OLD))
    finally:
        pe.close()

    if len(out) != len(original):
        raise BuildAbortedError("candidate changed raw file length")
    candidate = bytes(out)
    report = {
        "schema": "syw2plus.g5-selection-cap50-chunked-order-dispatch-candidate.v5",
        "status": "SELECTION_CAP50_CHUNKED_ORDER_DISPATCH_SPARSE_GATE",
        "original_sha256": ORIGINAL_SHA256,
        "v2_candidate_sha256": v2_report["candidate_sha256"],
        "candidate_sha256": hashlib.sha256(candidate).hexdigest(),
        "hook": {
            "site": hex(HOOK_SITE),
            "cave_base": hex(CAVE_BASE),
            "body_addr": hex(body_addr),
            "cave_end_exclusive": hex(cave_end),
            "wrapper_bytes": len(wrapper_bytes),
            "body_bytes": len(relocated_body),
        },
        "chunking": {
            "unit_cap_per_dispatch": CHUNK_UNITS,
            "chunks": [
                {"source": "in place (entries[0:20])", "units": CHUNK_UNITS},
                {"source": hex(CHUNK1_OFFSET), "units": CHUNK_UNITS},
                {"source": hex(CHUNK2_OFFSET), "units": CHUNK2_REAL_UNITS, "padded_to": CHUNK_UNITS},
            ],
            "gate": (
                "v4's inverted order-type gate unchanged; check_count gate widened to "
                "'count>20 OR entries[20:50] has a nonzero slot' (R3 fix)"
            ),
            "known_non_order_singles": [hex(v) for v in KNOWN_NON_ORDER_SINGLES],
            "known_non_order_ranges": [[hex(lo), hex(hi)] for lo, hi in KNOWN_NON_ORDER_RANGES],
        },
        "record_format": "unchanged; 60-byte record, 20-word unit-list, issued up to 3 times per order",
        "v2_report": v2_report,
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
