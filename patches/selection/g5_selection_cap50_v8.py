#!/usr/bin/env python3
"""v7 plus a full 50-slot zero-fill in the load-wrapper's legacy mirror.

lap746 (``docs/history/laps/20260928_lap746_work_g5_checklist_f_h_stale_tail_runtime_confirmed.md``,
``loop/ESCALATE_SOL`` lap745 section handoff) found *at runtime*, not just
statically, that v7's ``LOAD_WRAPPER`` only zero-fills
``entries[count:STOCK_CAPACITY]`` (20) after mirroring the legacy (<=20)
selection back into the relocated 50-slot array. ``entries[20:50]`` keep
whatever they held immediately before the load ran. Paired against the
original (capacity 20, no tail possible), the v7 candidate, when a >20
selection was kept live across a save/load:

- broke the "count == number of non-zero slots" invariant right after load
  (``count=20``, ``nonzero_count=50``);
- let the v5 chunk-dispatch gate route a subsequent move command to all 30
  stale-tail units outside the just-loaded 20-entry selection
  (``commanded_outside_legit_selection`` was non-empty, 30/30 of the tail);
- drove the live count negative (``-30``) after a plain deselect, because the
  deselect path removes every unit still flagged "selected" (unit byte 0),
  not just the ones the count-based array still agrees are selected;
- and, when a save was issued immediately afterward while count was
  negative, hung the game indefinitely with the save screen stuck at
  ``ps==23`` and every player record's rice/wood/unit counts zeroed -- the
  empirical shape of the catastrophic ``rep movsd``/``rep stosd`` risk the
  static review predicted (a negative count, sign-extended, read back as a
  ~4G-dword unsigned repeat count).

Fix: the load wrapper already computes "how many entries are left to clear"
as ``<a fixed capacity> - count``; only that fixed capacity was wrong. It
used ``STOCK_CAPACITY`` (20), copied from the save wrapper's own zero-fill,
where 20 is correct because the *legacy* buffer truly only has 20 slots. The
load wrapper writes into the *relocated* 50-slot array, so its own zero-fill
must clear ``entries[count:TARGET_CAPACITY]`` (50), not
``entries[count:20]``. This changes a single immediate operand inside the
existing instruction sequence. The call site, the save wrapper, the
``.rsrc`` cave layout/offsets, and every byte outside the load wrapper's own
cave region are unchanged from v7 -- this module patches v7's own build
output in place rather than re-deriving it from v6, so that scope is
enforced structurally, not just by convention.

Scope note carried over from v7, unchanged: only the first 20 of a >20-entry
live selection round-trip through the save *file itself* (same ceiling as
the stock game). This candidate does not change what gets persisted to
disk; it only ensures the in-memory tail no longer contains stale pre-load
values after a load, closing the invariant break/command-leak/negative-count
path above.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import keystone
import pefile

from patches.selection import g5_selection_cap50_v7 as v7

IMAGE_BASE = v7.IMAGE_BASE
ORIGINAL_SHA256 = v7.ORIGINAL_SHA256
SELECTION_BASE = v7.SELECTION_BASE
STOCK_CAPACITY = v7.STOCK_CAPACITY
TARGET_CAPACITY = v7.TARGET_CAPACITY
LEGACY_COUNT_ADDR = v7.LEGACY_COUNT_ADDR
LEGACY_ENTRIES_ADDR = v7.LEGACY_ENTRIES_ADDR
SAVE_CALL_VA = v7.SAVE_CALL_VA
LOAD_CALL_VA = v7.LOAD_CALL_VA
STREAM_SAVE_FN = v7.STREAM_SAVE_FN
STREAM_LOAD_FN = v7.STREAM_LOAD_FN
RSRC_CAVE_OFFSET = v7.RSRC_CAVE_OFFSET
SAVE_WRAPPER_OFFSET = v7.SAVE_WRAPPER_OFFSET
LOAD_WRAPPER_OFFSET = v7.LOAD_WRAPPER_OFFSET
RSRC_CODE_END_OFFSET = v7.RSRC_CODE_END_OFFSET
RSRC_EXECUTE_CODE_FLAGS = v7.RSRC_EXECUTE_CODE_FLAGS

BuildAbortedError = v7.BuildAbortedError

_MIRROR_FROM_LEGACY_FULL_TAIL = f"""
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
    mov ecx, {TARGET_CAPACITY}
    sub ecx, ebx
    xor eax, eax
    rep stosd dword ptr [edi], eax
"""

if v7._MIRROR_FROM_LEGACY.strip() == _MIRROR_FROM_LEGACY_FULL_TAIL.strip():
    raise BuildAbortedError(
        "v7 load-wrapper mirror already zero-fills the full 50-slot tail; v8 has nothing left to fix"
    )

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
    {_MIRROR_FROM_LEGACY_FULL_TAIL}
    popad
    pop ebp
    ret
"""


def _va_to_file_offset(pe: pefile.PE, va: int) -> int:
    return v7._va_to_file_offset(pe, va)


def _assemble(asm: str, address: int) -> bytes:
    ks = keystone.Ks(keystone.KS_ARCH_X86, keystone.KS_MODE_32)
    encoding, _count = ks.asm(asm, address)
    if encoding is None or len(encoding) < 1:
        raise BuildAbortedError("keystone produced no bytes")
    return bytes(encoding)


def build_candidate(original: bytes) -> tuple[bytes, dict[str, Any]]:
    candidate_v7, v7_report = v7.build_candidate(original)
    out = bytearray(candidate_v7)
    pe = pefile.PE(data=bytes(out), fast_load=True)
    try:
        rsrc = next((section for section in pe.sections if section.Name.rstrip(b"\0") == b".rsrc"), None)
        if rsrc is None:
            raise BuildAbortedError(".rsrc section missing")
        rsrc_va = IMAGE_BASE + int(rsrc.VirtualAddress)
        if rsrc_va != SELECTION_BASE + 0x1000:
            raise BuildAbortedError(f"unexpected relocated .rsrc VA 0x{rsrc_va:08x}")
        raw = int(rsrc.PointerToRawData)
        load_va = rsrc_va + LOAD_WRAPPER_OFFSET

        old_load_code = _assemble(v7._LOAD_WRAPPER_ASM, load_va)
        actual = bytes(out[raw + LOAD_WRAPPER_OFFSET: raw + LOAD_WRAPPER_OFFSET + len(old_load_code)])
        if actual != old_load_code:
            raise BuildAbortedError("v7 load wrapper bytes do not match the expected pinned old bytes")

        new_load_code = _assemble(_LOAD_WRAPPER_ASM, load_va)
        cave_budget = RSRC_CODE_END_OFFSET - LOAD_WRAPPER_OFFSET
        if len(new_load_code) > cave_budget:
            raise BuildAbortedError(f"load wrapper too large: {len(new_load_code)} bytes > {cave_budget}")
        # Clear the old wrapper's full footprint first so a shorter new
        # encoding cannot leave a stale tail of old opcode bytes behind.
        out[raw + LOAD_WRAPPER_OFFSET: raw + RSRC_CODE_END_OFFSET] = bytes(cave_budget)
        out[raw + LOAD_WRAPPER_OFFSET: raw + LOAD_WRAPPER_OFFSET + len(new_load_code)] = new_load_code
    finally:
        pe.close()

    if len(out) != len(original):
        raise BuildAbortedError("candidate changed raw file length")
    candidate = bytes(out)
    report = {
        "schema": "syw2plus.g5-selection-cap50-saveload-shadow-candidate.v8",
        "status": "SELECTION_CAP50_SAVELOAD_LEGACY_SHADOW_TAIL_CLEARED",
        "original_sha256": ORIGINAL_SHA256,
        "v7_candidate_sha256": v7_report["candidate_sha256"],
        "candidate_sha256": hashlib.sha256(candidate).hexdigest(),
        "hooks": {
            "load": {"site": hex(LOAD_CALL_VA), "wrapper_va": hex(load_va), "bytes": len(new_load_code)},
        },
        "fix": "load-wrapper zero-fill widened from entries[count:20] to entries[count:50]",
        "known_limit": (
            "only the first 20 live selection entries round-trip through the save file itself; "
            "entries 21..50 are still not persisted to disk (same ceiling as v7/the stock game) -- "
            "this candidate only ensures the in-memory tail no longer contains stale pre-load "
            "values after a load"
        ),
        "v7_report": v7_report,
    }
    return candidate, report


def restore_candidate(candidate: bytes, original: bytes) -> bytes:
    v7.v3.v1.verify_original(original)
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
