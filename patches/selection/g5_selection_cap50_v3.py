#!/usr/bin/env python3
"""Split the G5 order-record builder's fixed 20-unit read into up to 3 chunks.

``tools/g5_order_record_builder_trace.py`` (live gdb, hardware watchpoints
correlated against the confirmed order-staging marker at 0x893130) found the
exact root cause of the G5 20-unit order-broadcast cap that v1/v2 could not
close: a single shared "build the 60-byte order record from the current
selection and dispatch it" routine at VA ``0x004AE550``. It already reads the
(v1-relocated, 50-capacity) selection array correctly -- the DIRECT_SITES
patch at ``0x004AE58C`` already retargets it -- but its unit-list loop is
unconditionally bounded by a hardcoded ``mov ebp, 0x14`` (20) at
``0x004AE5F4``, and its scratch/staging record is a fixed 60-byte structure
(20-word unit-list sub-array) reused downstream by the network relay queue
and the local 50-slot dispatch queue.

Static xref search found 22 call sites for this function, all pushing a
"type" argument that matches the previously-catalogued non-order opcode set
(0x52, 0x56, 0x19b, 0x19d-0x1a1, 0x1ae-0x1bc; see lap676's
``g5_command_packer_xrefs.py`` finding) -- none of them issue real unit
orders. Live traces of an actual MOVE and an actual ATTACK-toolbar click
instead land on this function via an indirect call not caught by that scan,
with order-type header words ``3`` and ``4`` respectively, both members of
the already-catalogued real order-code set ``{1, 3, 4, 7, 8, 9}``.

Operator direction (2026-09-26 13:09): do not enlarge the 60-byte record or
its downstream consumers (network packet format, 50-slot queue) -- instead
issue the *same* record up to 3 times, each covering a window of at most 20
selected units, so every existing consumer keeps seeing exactly the shape it
has always handled. This module implements that: a small wrapper is spliced
in at the function's entry (the six-byte ``sub esp, 0x94`` prologue becomes a
five-byte near jump plus one padding byte) that:

- Falls straight through to the untouched original body, unmodified in
  every register/stack respect, for any call whose type argument is not in
  the real-order set, or whose live selection count is <=20 -- this is the
  overwhelming majority of calls (all 22 known UI/notification sites, and
  every pre-G5 <=20-unit order) and its behavior is bit-for-bit identical to
  the original function.
- For a real order type with >20 selected: saves the live 20-entry read
  window (``SELECTION_BASE+4 .. +0x54``) into a 80-byte local-stack scratch
  buffer, then for each of up to 3 chunks of the (already up-to-50-capacity)
  selection array, copies that chunk's <=20 entries into the read window
  (zero-padding the last chunk's unused tail so the original body's own
  per-entry validity check -- ``call 0x416f70; cmp eax, 1`` -- naturally
  skips them, exactly as it already does for an under-20 stock selection),
  and calls the *original, unmodified* function body as a subroutine (it
  reads/writes only its own local frame plus the read window, so calling it
  three times with three different window contents is equivalent to three
  independent order-issue calls). The saved window is restored before
  returning, so no other code ever observes the temporary window rewrite.

lap680 fix: the wrapper reserves its 80-byte scratch buffer with an explicit
``sub esp, 0x50`` right after establishing ``ebp`` -- without it, the buffer
at ``[ebp-0x50, ebp)`` aliases the exact stack slots the subsequent 5-arg
push + ``call original_body`` sequence writes on every chunk (args land at
``[ebp-0x14, ebp-0x4]``, the call's own return address at ``[ebp-0x18]``,
all inside the unreserved buffer). Each chunk call clobbered backup
entries 14-19 with that call's own return address and argument words; the
final restore then copied chunk 2's leftover return address
(``0x004E4E1C``) into live entry 14, whose low word (``0x4E1C`` = 19996) fed
an unrelated, unbounded selection-panel-refresh accessor (``0x0040FED0``)
and reproduced the exact observed page fault (read access to
``0x02A45AAA``). Reserving the buffer's own frame slot keeps every later
push/call strictly below it.

The original function body is copied byte-for-byte into the cave (from the
already v1/v2-patched candidate bytes, so it already contains the
DIRECT_SITES-relocated ``mov esi, SELECTION_BASE+4`` at its own
``0x004AE58C`` offset) with its two external ``call`` rel32 displacements
recomputed for the new address; every other control-transfer in that body is
a short intra-function jump, unaffected by uniform relocation. x86 ``ret``
does not care whether it was reached by ``jmp`` (tail call, returns to the
original external caller) or by ``call`` (returns to this wrapper), so a
single copy of the body serves both the fast-path and the three chunked
calls.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

import capstone
import keystone
import pefile

from patches.selection import g5_selection_cap50_v1 as v1
from patches.selection import g5_selection_cap50_v2 as v2

IMAGE_BASE = v2.IMAGE_BASE
ORIGINAL_SHA256 = v2.ORIGINAL_SHA256
SELECTION_BASE = v2.SELECTION_BASE
TARGET_CAPACITY = v2.TARGET_CAPACITY
STOCK_CAPACITY = v2.STOCK_CAPACITY

ENTRIES = SELECTION_BASE + 4
CHUNK_ENTRY_BYTES = 4
CHUNK_UNITS = 20
CHUNK1_OFFSET = ENTRIES + CHUNK_UNITS * CHUNK_ENTRY_BYTES        # entries[20:40]
CHUNK2_OFFSET = ENTRIES + 2 * CHUNK_UNITS * CHUNK_ENTRY_BYTES    # entries[40:50]
CHUNK2_REAL_UNITS = TARGET_CAPACITY - 2 * CHUNK_UNITS            # 10

HOOK_SITE = 0x004AE550
HOOK_OLD = bytes.fromhex("81 ec 94 00 00 00")  # sub esp, 0x94
BODY_END = 0x004AE654  # exclusive, one byte past the original function's "ret"
BODY_LEN = BODY_END - HOOK_SITE

EXTERNAL_CALLS = (
    # (original call-site VA, absolute target VA)
    (0x004AE5FC, 0x00416F70),
    (0x004AE63F, 0x004A3C10),
)

CAVE_BASE = 0x004E4D50
CAVE_LIMIT = v2.CAVE_END  # 0x004E5000; must not spill past the mapped .text tail

_MOVSD = "rep movsd dword ptr [edi], dword ptr [esi]"
_STOSD = "rep stosd dword ptr [edi], eax"

_WRAPPER_ASM = f"""
    movzx eax, word ptr [esp+8]
    cmp eax, 1
    je check_count
    cmp eax, 3
    je check_count
    cmp eax, 4
    je check_count
    cmp eax, 7
    je check_count
    cmp eax, 8
    je check_count
    cmp eax, 9
    je check_count
    jmp original_body

check_count:
    movzx eax, word ptr [{hex(SELECTION_BASE)}]
    cmp eax, {CHUNK_UNITS}
    jle original_body

    push ebp
    push ebx
    push esi
    push edi
    mov ebp, esp
    sub esp, 0x50

    push esi
    push edi
    push ecx
    lea edi, [ebp-0x50]
    mov esi, {hex(ENTRIES)}
    mov ecx, {CHUNK_UNITS}
    {_MOVSD}
    pop ecx
    pop edi
    pop esi

    push dword ptr [ebp+0x24]
    push dword ptr [ebp+0x20]
    push dword ptr [ebp+0x1c]
    push dword ptr [ebp+0x18]
    push dword ptr [ebp+0x14]
    call original_body
    add esp, 0x14

    push esi
    push edi
    push ecx
    mov esi, {hex(CHUNK1_OFFSET)}
    mov edi, {hex(ENTRIES)}
    mov ecx, {CHUNK_UNITS}
    {_MOVSD}
    pop ecx
    pop edi
    pop esi

    push dword ptr [ebp+0x24]
    push dword ptr [ebp+0x20]
    push dword ptr [ebp+0x1c]
    push dword ptr [ebp+0x18]
    push dword ptr [ebp+0x14]
    call original_body
    add esp, 0x14

    push esi
    push edi
    push ecx
    mov esi, {hex(CHUNK2_OFFSET)}
    mov edi, {hex(ENTRIES)}
    mov ecx, {CHUNK2_REAL_UNITS}
    {_MOVSD}
    xor eax, eax
    mov ecx, {CHUNK_UNITS - CHUNK2_REAL_UNITS}
    {_STOSD}
    pop ecx
    pop edi
    pop esi

    push dword ptr [ebp+0x24]
    push dword ptr [ebp+0x20]
    push dword ptr [ebp+0x1c]
    push dword ptr [ebp+0x18]
    push dword ptr [ebp+0x14]
    call original_body
    add esp, 0x14

    push esi
    push edi
    push ecx
    lea esi, [ebp-0x50]
    mov edi, {hex(ENTRIES)}
    mov ecx, {CHUNK_UNITS}
    {_MOVSD}
    pop ecx
    pop edi
    pop esi

    mov eax, 1
    mov esp, ebp
    pop edi
    pop esi
    pop ebx
    pop ebp
    ret

original_body:
    nop
"""


class BuildAbortedError(RuntimeError):
    """Raised when a pinned byte, PE invariant, or assembler output does not match."""


def _va_to_file_offset(pe: pefile.PE, va: int) -> int:
    return v2._va_to_file_offset(pe, va)


def _patch_exact(out: bytearray, pe: pefile.PE, va: int, old: bytes, new: bytes) -> None:
    if len(old) != len(new):
        raise BuildAbortedError(f"0x{va:08x}: replacement changes instruction length")
    off = _va_to_file_offset(pe, va)
    actual = bytes(out[off : off + len(old)])
    if actual != old:
        raise BuildAbortedError(
            f"0x{va:08x}: old bytes mismatch expected={old.hex()} actual={actual.hex()}"
        )
    out[off : off + len(old)] = new


def _rel32(source: int, target: int) -> bytes:
    return struct.pack("<i", target - (source + 5))


def _hook(site: int, cave: int, old: bytes) -> bytes:
    if len(old) < 5:
        raise BuildAbortedError("hook site is too short for a near jump")
    return b"\xe9" + _rel32(site, cave) + bytes(len(old) - 5)


def _assemble_wrapper() -> bytes:
    ks = keystone.Ks(keystone.KS_ARCH_X86, keystone.KS_MODE_32)
    encoding, _count = ks.asm(_WRAPPER_ASM, CAVE_BASE)
    if encoding is None or len(encoding) < 1:
        raise BuildAbortedError("keystone produced no wrapper bytes")
    if encoding[-1] != 0x90:
        raise BuildAbortedError("expected trailing nop placeholder for original_body label")
    return bytes(encoding[:-1])


def _relocate_body(body: bytes, new_base: int) -> bytes:
    """Copy the original function body, fixing up its two external calls."""
    if len(body) != BODY_LEN:
        raise BuildAbortedError(f"unexpected body length {len(body)} != {BODY_LEN}")
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    out = bytearray(body)
    seen_calls: set[int] = set()
    for insn in md.disasm(body, HOOK_SITE):
        if insn.mnemonic != "call":
            continue
        if not insn.op_str.startswith("0x"):
            raise BuildAbortedError(f"unexpected indirect call in body: {insn}")
        target = int(insn.op_str, 16)
        matches = [t for site, t in EXTERNAL_CALLS if site == insn.address and t == target]
        if not matches:
            raise BuildAbortedError(f"unrecognized external call at 0x{insn.address:08x} -> 0x{target:08x}")
        if len(insn.bytes) != 5 or insn.bytes[0] != 0xE8:
            raise BuildAbortedError(f"external call at 0x{insn.address:08x} is not a 5-byte E8 rel32")
        offset = insn.address - HOOK_SITE
        new_site = new_base + offset
        out[offset + 1 : offset + 5] = _rel32(new_site, target)
        seen_calls.add(insn.address)
    if {site for site, _t in EXTERNAL_CALLS} != seen_calls:
        raise BuildAbortedError("did not find both expected external calls while relocating body")
    return bytes(out)


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
        relocated_body = _relocate_body(body_bytes, body_addr)
        cave_bytes = wrapper_bytes + relocated_body

        cave_off = _va_to_file_offset(pe, CAVE_BASE)
        existing = bytes(out[cave_off : cave_off + len(cave_bytes)])
        if existing != bytes(len(cave_bytes)):
            raise BuildAbortedError("cave region is not zero-filled before write")
        out[cave_off : cave_off + len(cave_bytes)] = cave_bytes

        _patch_exact(out, pe, HOOK_SITE, HOOK_OLD, _hook(HOOK_SITE, CAVE_BASE, HOOK_OLD))
    finally:
        pe.close()

    if len(out) != len(original):
        raise BuildAbortedError("candidate changed raw file length")
    candidate = bytes(out)
    report = {
        "schema": "syw2plus.g5-selection-cap50-chunked-order-dispatch-candidate.v3",
        "status": "SELECTION_CAP50_CHUNKED_ORDER_DISPATCH",
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
            "real_order_types": [1, 3, 4, 7, 8, 9],
        },
        "record_format": "unchanged; 60-byte record, 20-word unit-list, issued up to 3 times per order",
        "v2_report": v2_report,
    }
    return candidate, report


def restore_candidate(candidate: bytes, original: bytes) -> bytes:
    v1.verify_original(original)
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
