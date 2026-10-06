#!/usr/bin/env python3
"""v3's chunk wrapper with the order-type gate inverted (2026-09-27 15:49
operator direction, step (2), first/recommended option).

``docs/history/laps/20260927_direct_g5_v3_command_coverage.md`` found that
the v3 candidate (``g5_selection_cap50_v3.py``) receives STOP, HOLD, and
PATROL group commands on only exactly 20 of 50 selected units -- the same
20-unit cap v3 was built to remove for MOVE/ATTACK. v3's wrapper only routes
a call through the chunked (up to 50-unit) dispatch path when its order-type
header (``word ptr [esp+8]``) is a member of a small explicit whitelist,
``{1, 3, 4, 7, 8, 9}`` (the "known real order types" from lap679/680's live
MOVE/ATTACK traces); every other header value -- including STOP, HOLD, and
PATROL's, whatever they turn out to be -- falls straight through to the
original, unchunked, hard-20-unit function body.

This module keeps v3's chunking mechanics byte-for-byte (the 80-byte backup
buffer, the three 20-unit chunk copies, the relocated original body) and
only replaces the *gate*: instead of an explicit "known real order types"
allow-list, it uses lap676's independently-verified "known non-order /
UI-notification opcode" set -- the 22 call sites ``tools/
g5_command_packer_xrefs.py`` statically inventoried and ``docs/history/
laps/20260926_lap676_work_g5_command_packer_xref_falsified.md`` catalogued
as *not* unit-order dispatch (15 of them a single sticky-flag-flush loop,
the rest isolated UI/notification events):

    {0x52, 0x56, 0x19b, 0x19d-0x1a1, 0x1ae-0x1bc}

A header in that set still falls through unchunked (bit-for-bit identical to
v3 for those 22 known non-order call sites). Any other header -- the six
already-confirmed real order types, STOP/HOLD/PATROL, and any order type
this project has not yet catalogued -- now takes the chunked path whenever
the live selection exceeds 20. This is deliberately more conservative than
enumerating STOP/HOLD/PATROL's measured header values one at a time: lap717
found the live selection-count/order-type header is not observable through
a non-invasive breakpoint at the wrapper's own entry point even for
confirmed-working MOVE orders (echoing lap681's identical finding on v3),
so this project does not have a reliable live measurement of STOP/HOLD/
PATROL's actual header values to whitelist individually. Inverting the gate
sidesteps that gap: it does not need to know the new types' exact values,
only that they are not among the 22 already-proven-harmless ones.

**2026-09-27 lap719 middle independent review correction:** the paragraph
above (as originally written) is wrong about where the behavioral risk sits,
and is kept only for history; do not rely on it. Re-running lap676's own tool
against the raw original found that only 21 of its 22 call sites carry a
fixed immediate opcode, and that set is ``{0x52, 0x56, 0x1a0, 0x1a1,
0x1ae..0x1bc}`` -- ``0x19b`` and ``0x19d..0x19f`` are not the opcode of any
call site (harmless to list, since they never fire, but lap676's claim that
they were observed there is incorrect). The 22nd call site, at ``0x41F0A4``,
carries no fixed immediate at all: its opcode argument is the **runtime
global ``word [0x892ffe]``**, and this is the site actually responsible for
real unit-order dispatch (move/attack under v3, and now STOP/HOLD/PATROL
under v4) -- lap676 misclassified it as a non-order notification call. So the
21 fixed-immediate sites are not a hazard: all 21 are inside this module's
non-order set, so v4 sends them down the same unchunked, unchanged path as
v3 and the original, for every selection size. The only place v4's behavior
differs from v3 is at ``0x41F0A4``, and only when its runtime opcode index is
outside v3's ``{1, 3, 4, 7, 8, 9}`` whitelist while the live selection is
>20 -- which is precisely the intended fix, not new exposure. The real
residual risks are orthogonal to this paragraph: (R1) the three copy windows
this wrapper always fills (``entries[0:20]``, ``[20:40]``, ``[40:50]``) are
sized to the selection *capacity*, not the live *count* -- shrinking a live
selection from 50 down to 21-49 may leave stale handles in the tail windows
that still get dispatched (unmeasured before lap719; see
``tools/g5_selection_shrink_leak_probe.py``); (R2) any as-yet-unmeasured
order button whose runtime index at ``0x41F0A4`` happens to still land
inside this module's non-order set would silently keep the 20-unit cap.
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

IMAGE_BASE = v3.IMAGE_BASE
ORIGINAL_SHA256 = v3.ORIGINAL_SHA256
SELECTION_BASE = v3.SELECTION_BASE
TARGET_CAPACITY = v3.TARGET_CAPACITY
STOCK_CAPACITY = v3.STOCK_CAPACITY

ENTRIES = v3.ENTRIES
CHUNK_UNITS = v3.CHUNK_UNITS
CHUNK1_OFFSET = v3.CHUNK1_OFFSET
CHUNK2_OFFSET = v3.CHUNK2_OFFSET
CHUNK2_REAL_UNITS = v3.CHUNK2_REAL_UNITS

HOOK_SITE = v3.HOOK_SITE
HOOK_OLD = v3.HOOK_OLD
BODY_END = v3.BODY_END
BODY_LEN = v3.BODY_LEN
EXTERNAL_CALLS = v3.EXTERNAL_CALLS
CAVE_BASE = v3.CAVE_BASE
CAVE_LIMIT = v3.CAVE_LIMIT

_MOVSD = v3._MOVSD
_STOSD = v3._STOSD

# lap676's statically-verified non-order/UI-notification opcode inventory
# (individual values plus the two contiguous runs): NOT a member of this set
# now means "chunk if the live selection is >20", the inverse of v3's small
# explicit allow-list.
KNOWN_NON_ORDER_SINGLES = (0x52, 0x56, 0x19B)
KNOWN_NON_ORDER_RANGES = ((0x19D, 0x1A1), (0x1AE, 0x1BC))

_GATE_ASM = f"""
    movzx eax, word ptr [esp+8]
    cmp eax, {hex(KNOWN_NON_ORDER_SINGLES[0])}
    je original_body
    cmp eax, {hex(KNOWN_NON_ORDER_SINGLES[1])}
    je original_body
    cmp eax, {hex(KNOWN_NON_ORDER_SINGLES[2])}
    je original_body
    cmp eax, {hex(KNOWN_NON_ORDER_RANGES[0][0])}
    jb check_count
    cmp eax, {hex(KNOWN_NON_ORDER_RANGES[0][1])}
    jbe original_body
    cmp eax, {hex(KNOWN_NON_ORDER_RANGES[1][0])}
    jb check_count
    cmp eax, {hex(KNOWN_NON_ORDER_RANGES[1][1])}
    jbe original_body
    jmp check_count
"""

# The rest of the wrapper (count gate, 80-byte backup buffer, three chunked
# dispatch calls, restore, tail) is byte-for-byte v3's -- only the leading
# gate above differs.
_CHECK_COUNT_LABEL = "check_count:"
_WRAPPER_ASM = _GATE_ASM + _CHECK_COUNT_LABEL + v3._WRAPPER_ASM.split(_CHECK_COUNT_LABEL, 1)[1]


class BuildAbortedError(RuntimeError):
    """Raised when a pinned byte, PE invariant, or assembler output does not match."""


def _va_to_file_offset(pe: pefile.PE, va: int) -> int:
    return v3._va_to_file_offset(pe, va)


def _assemble_wrapper() -> bytes:
    ks = keystone.Ks(keystone.KS_ARCH_X86, keystone.KS_MODE_32)
    encoding, _count = ks.asm(_WRAPPER_ASM, CAVE_BASE)
    if encoding is None or len(encoding) < 1:
        raise BuildAbortedError("keystone produced no wrapper bytes")
    if encoding[-1] != 0x90:
        raise BuildAbortedError("expected trailing nop placeholder for original_body label")
    return bytes(encoding[:-1])


def build_candidate(original: bytes) -> tuple[bytes, dict[str, Any]]:
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
        "schema": "syw2plus.g5-selection-cap50-chunked-order-dispatch-candidate.v4",
        "status": "SELECTION_CAP50_CHUNKED_ORDER_DISPATCH_INVERTED_GATE",
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
            "gate": "inverted: chunk unless header is a known non-order/UI-notification opcode",
            "known_non_order_singles": [hex(v) for v in KNOWN_NON_ORDER_SINGLES],
            "known_non_order_ranges": [[hex(lo), hex(hi)] for lo, hi in KNOWN_NON_ORDER_RANGES],
            "v3_real_order_types_whitelist_replaced": [1, 3, 4, 7, 8, 9],
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
