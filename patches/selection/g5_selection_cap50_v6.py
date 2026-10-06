#!/usr/bin/env python3
"""v5 plus a death-time control-group cleanup fix (G5 checklist (D) residual,
``docs/history/laps/20260928_lap732_work_g5_checklist_d_shift_add_death_recall.md``,
``loop/ESCALATE_SOL`` lap732 section, 2026-09-28 09:05 operator direction).

lap732 found that recalling a >20-member group after some members die can
resurrect a subset of the dead as "ghosts" in the candidate build only (the
original, capped at 20, never showed this). Static disassembly of the
*pristine original* executable (this module's own investigation, not carried
over from any prior lap doc) pins the mechanism precisely:

- The stock recall function (``FUN_00445E30``) walks the PlayerStruct's own
  fixed 20-slot group array (``G+0x16+g*0x50``, byte-identical between
  original and candidate -- H1/H2/H3 never touch this function) and, for
  every stored slot, gates selection on ``FUN_0040F790(slot) == 1`` (the
  "selectable" byte at ``unit+0x31C``) -- exactly the same live gate v2's H3
  cave already uses for its unit-field overflow scan (``unit+0x344``,
  members 21..50).
- The stock death handler (``FUN_00409C70``) never touches ``unit+0x31C``
  itself. The only thing it does to disentangle a dying unit from group
  bookkeeping is call ``FUN_00445A90(G, handle)`` once
  (``0x00409CB8``, unconditional), which searches the *same* fixed 20-slot
  array for an entry whose low/high words exactly match the live
  ``dword[unit+0x29C]`` handle, and only clears ``unit+0x344`` back to -1 for
  that one matched entry -- it does not touch entries in *other* groups'
  20-slot arrays by unit-field content, and it does nothing at all for a
  member whose only membership record is the unit's own ``+0x344`` field
  (candidate members 21..50), because that never lived in any 20-slot array
  to search.
- In the 41-member group lap732 exercised, this project's own captured
  ``fixture_unit_group_snapshot`` reads (``docs/history/laps/
  20260928_lap732_work_g5_checklist_d_shift_add_death_recall.md`` artifact
  JSON) show the recorded ``unit+0x29C`` handle for a member is stable from
  assign time through the post-death recall (it is derived fresh from the
  unit's own record on every read, and nothing in this code path ever
  writes it), which rules out a "handle drifted so the match failed"
  explanation. The remaining, still only partially pinned mechanism is some
  combination of (a) the two-stage assign this scenario exercised (an
  initial 40-member Ctrl+1, a "1"-recall re-ordering, one more Shift-click,
  then a redefining Ctrl+1) leaving a subset of the physical 20-slot array
  in a state ``FUN_00445A90``'s exact-match search does not clear, and/or
  (b) the stock engine's own per-tick death cleanup (existence/selectable
  finalization) not having caught up yet inside the short post-kill delay
  this project's probes use, at the larger population scale a 50-member
  group's fixture requires -- and this module deliberately does not require
  resolving which of those it is, because the fix below is correct either
  way.

Fix: this module adds one more hook, H4, at the *call site* to
``FUN_00445A90`` inside ``FUN_00409C70`` (``0x00409CB8``, a 5-byte ``call``
instruction -- exactly enough room for a ``jmp`` trampoline with no NOP
padding needed). The H4 cave first performs the original call unchanged
(same argument/receiver setup as stock, untouched), then unconditionally
does one more, narrower and more robust cleanup for the dying unit alone:
read its still-valid ``unit+0x344`` group id (skip entirely if -1, i.e. not
a member of anything); if a member, recompute that one group's own PlayerStruct
base (``0x9570F4 + owner*0x3ABC``, the same formula ``FUN_00409C70`` already
computes once for the ``FUN_00445A90`` call) and scan *only that one group's*
20-slot array (not all 10 -- the dying unit cannot be a member of more than
one group at a time) for any entry whose **low word (slot) alone** matches
the dying unit's own slot (``unit+0x29C``'s low word) -- deliberately not
requiring a high-word/aux match the way ``FUN_00445A90``'s own search does,
since a slot number is unique to at most one live unit and this scan is
scoped to the exact group the field says the unit belongs to, so a
low-word-only match cannot legitimately name a different unit. Any match is
zeroed in place (mirroring what ``FUN_00445A90``/the stock assign-clear loop
already do for entries they do find). Finally it force-writes
``unit+0x344 = -1`` via the existing setter (``FUN_0040F750``), which is a
safe no-op if ``FUN_00445A90`` had already done so. This guarantees H3's
live overflow scan can never see a stale ``+0x344 == g`` for a unit that has
died, regardless of why the 20-slot array match did or did not succeed, and
it is scoped tightly enough (one group's 20 entries, one unit, one call
site, no change to any of H1/H2/H3 or the stock assign/recall bodies) that
it cannot affect any already-PASSing G5 behavior (drag, move, attack, group
assign/recall of live members, save/load).
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import keystone
import pefile

from patches.selection import g5_selection_cap50_v3 as v3
from patches.selection import g5_selection_cap50_v5 as v5

IMAGE_BASE = v5.IMAGE_BASE
ORIGINAL_SHA256 = v5.ORIGINAL_SHA256
SELECTION_BASE = v5.SELECTION_BASE
TARGET_CAPACITY = v5.TARGET_CAPACITY
STOCK_CAPACITY = v5.STOCK_CAPACITY

UNIT_BASE = 0x0066B790
UNIT_STRIDE = 0x758
UNIT_GROUP_OFFSET = 0x344     # dword; -1 = no group
UNIT_HANDLE_OFFSET = 0x29C    # word (self-slot); dword read forms (slot, aux)
UNIT_OWNER_OFFSET = 0x8E
PLAYER_GROUP_BASE = 0x009570F4
PLAYER_STRIDE = 0x3ABC
GROUP_ENTRIES_OFFSET = 0x16
GROUP_STRIDE = 0x50           # 20 entries * 4 bytes per group

H4_SITE = 0x00409CB8
H4_OLD = bytes.fromhex("e8 d3 bd 03 00")  # call 0x00445a90
H4_TARGET = 0x00445A90
H4_RETURN = 0x00409CBD  # instruction right after the original 5-byte call

# Free, verified-zero tail space after v5's own wrapper+body in the same
# cave block v2 opened (0x004E4C00..0x004E5000, the .text raw-data end) --
# v5's wrapper+relocated body ends at 0x004E4F84 (v3.CAVE_BASE=0x4E4D50 +
# len(v5 wrapper 304B) + BODY_LEN 260B); H4 starts 12 bytes further in for a
# clean gap and needs 106 bytes, ending at 0x004E4FFA, six bytes inside the
# 0x004E5000 limit.
H4_CAVE = 0x004E4F90
CAVE_LIMIT = v3.CAVE_LIMIT

_H4_ASM = f"""
    call {hex(H4_TARGET)}
    pushad
    mov eax, dword ptr [esi+{hex(UNIT_GROUP_OFFSET)}]
    cmp eax, -1
    je done
    movzx ecx, word ptr [esi+{hex(UNIT_HANDLE_OFFSET)}]
    movsx edx, byte ptr [esi+{hex(UNIT_OWNER_OFFSET)}]
    lea ebx, [edx+edx*2]
    shl ebx, 4
    sub ebx, edx
    lea ebx, [ebx+ebx*4]
    shl ebx, 4
    sub ebx, edx
    lea ebx, [ebx*4+{hex(PLAYER_GROUP_BASE)}]
    imul eax, eax, {hex(GROUP_STRIDE)}
    add ebx, eax
    lea edi, [ebx+{hex(GROUP_ENTRIES_OFFSET)}]
    mov esi, 0x14
scan_loop:
    movzx eax, word ptr [edi]
    cmp ax, cx
    jne next_entry
    mov word ptr [edi], 0
    mov word ptr [edi+2], 0
next_entry:
    add edi, 4
    dec esi
    jnz scan_loop
    push -1
    push ecx
    call 0x0040f750
done:
    popad
    jmp {hex(H4_RETURN)}
"""


class BuildAbortedError(RuntimeError):
    """Raised when a pinned byte, PE invariant, or assembler output does not match."""


def _va_to_file_offset(pe: pefile.PE, va: int) -> int:
    return v5._va_to_file_offset(pe, va)


def _assemble_h4() -> bytes:
    ks = keystone.Ks(keystone.KS_ARCH_X86, keystone.KS_MODE_32)
    encoding, _count = ks.asm(_H4_ASM, H4_CAVE)
    if encoding is None or len(encoding) < 1:
        raise BuildAbortedError("keystone produced no H4 bytes")
    return bytes(encoding)


def build_candidate(original: bytes) -> tuple[bytes, dict[str, Any]]:
    candidate_v5, v5_report = v5.build_candidate(original)
    out = bytearray(candidate_v5)
    pe = pefile.PE(data=bytes(out), fast_load=True)
    try:
        site_off = _va_to_file_offset(pe, H4_SITE)
        actual = bytes(out[site_off : site_off + len(H4_OLD)])
        if actual != H4_OLD:
            raise BuildAbortedError(
                f"0x{H4_SITE:08x}: old bytes mismatch expected={H4_OLD.hex()} actual={actual.hex()}"
            )

        h4_bytes = _assemble_h4()
        h4_end = H4_CAVE + len(h4_bytes)
        if h4_end > CAVE_LIMIT:
            raise BuildAbortedError(f"H4 cave overflow: ends at 0x{h4_end:08x} > limit 0x{CAVE_LIMIT:08x}")

        cave_off = _va_to_file_offset(pe, H4_CAVE)
        existing = bytes(out[cave_off : cave_off + len(h4_bytes)])
        if existing != bytes(len(h4_bytes)):
            raise BuildAbortedError("H4 cave region is not zero-filled before write")
        out[cave_off : cave_off + len(h4_bytes)] = h4_bytes

        v3._patch_exact(out, pe, H4_SITE, H4_OLD, v3._hook(H4_SITE, H4_CAVE, H4_OLD))
    finally:
        pe.close()

    if len(out) != len(original):
        raise BuildAbortedError("candidate changed raw file length")
    candidate = bytes(out)
    report = {
        "schema": "syw2plus.g5-selection-cap50-death-recall-cleanup-candidate.v6",
        "status": "SELECTION_CAP50_DEATH_RECALL_GROUP_CLEANUP",
        "original_sha256": ORIGINAL_SHA256,
        "v5_candidate_sha256": v5_report["candidate_sha256"],
        "candidate_sha256": hashlib.sha256(candidate).hexdigest(),
        "hook": {
            "site": hex(H4_SITE),
            "cave_base": hex(H4_CAVE),
            "cave_end_exclusive": hex(H4_CAVE + len(h4_bytes)),
            "bytes": len(h4_bytes),
            "behavior": (
                "after the original FUN_00445A90(G, handle) call, additionally clear the "
                "dying unit's own group-array entry by slot-only match within its own "
                "group's 20-slot array (not all 10), then force unit+0x344=-1"
            ),
        },
        "v5_report": v5_report,
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
