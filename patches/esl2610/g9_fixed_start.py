#!/usr/bin/env python3
"""G9: fixed start positions on the pinned ESL 2613-line EXE.

Port of the ESL 2606 "시작자리고정" variant (two in-place chunks, see
``patches/ai/shop_open_legacy_combos_2608.py`` FIXED_START_CHUNKS and
``analysis/memory_maps/esl2608_shop_ai_static_20260925.md``):

* ``0x41F2B0``: the ``jne`` at ``0x41F2AE`` lands on ``0x41F33E`` (``inc esi``)
  instead of ``0x41F33F``, so the start-slot counter also advances for seats
  that are skipped;
* ``0x42FBB1``: ``movsx edx,dx`` (random remainder) becomes ``mov edx,ebx;
  nop`` so the start location is chosen by the loop index.

The two legacy chunks handle the fixed-map route.  The procedural-map route
also needs its dynamic AX index overridden: its native helper is still called
for RNG/auxiliary side effects, but output row ``i`` must consume input pair
``i``.  Standalone official builds add a dedicated executable section.  The
pinned stacked V8 uses its verified, owned ``.g8code`` zero tail instead, so
it needs no 95th section or expanded PE headers.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
from pathlib import Path
from typing import Any

from patches.esl2610 import pe_extend

CHUNKS = (
    (0x0041F2B0, bytes.fromhex("8b"), bytes.fromhex("8a")),
    (0x0042FBB1, bytes.fromhex("0fbfd2"), bytes.fromhex("8bd390")),
)
CONTEXT = 0x40
# 0x80-byte windows; source contexts were carried from the legacy 2606/2608
# patch sites and verified unchanged in the pinned ESL2613 source.
CONTEXT_SHA256 = {
    0x0041F2B0: "6c9ae09ee5849fe255f866e9b45c2bdfe7a4a8cd462b5b16eaeedbbf3fd0add7",
    0x0042FBB1: "8b4bcc5c2aa19f194de72ec7b4982e56e66ba184a2918af466cbae1945ab7832",
}
STACKED_V8_SHA256 = "1e83466eab020818a6c0e9057508d71451af3ee1098af43ebefc20de8ab96e3d"
PROCEDURAL_SITE = 0x0044F079
PROCEDURAL_CONTINUE = 0x0044F07F
PROCEDURAL_OLD = bytes.fromhex("0fbfd083c40c")  # movsx edx,ax; add esp,0xc
PROCEDURAL_CONTEXT_SHA256 = "0a34f201f21769dac84a0f364e4d1a0d24f3340931e87adc090c6a3bea92a554"
PROCEDURAL_SECTION = b".g9proc"  # retained for standalone and historical r10 builds
STACKED_PROCEDURAL_SECTION = b".g8code"
STACKED_PROCEDURAL_CAVE_OFFSET = 0x20
STACKED_SECTIONS = [b".g2bss", b".g2code", b".g6code", b".g8code"]
# At 44F079 ESP is still entry_ESP-0x3c: the helper's three caller-cleaned
# arguments have not yet been removed.  The original count is [entry_ESP+4],
# hence WORD[ESP+0x40] here (not +0x34, which is scratch at entry_ESP-8).
# movsx edx,word ptr [esp+40h]; sub edx,ebp; add esp,0ch; jmp rel32
PROCEDURAL_PREFIX = bytes.fromhex("0fbf5424402bd583c40ce9")
def _context_digest(data: bytes, va: int) -> str:
    off = pe_extend.va_to_offset(data, va)
    return hashlib.sha256(data[off - CONTEXT : off + CONTEXT]).hexdigest()


def _stacked_cave(
    data: bytes | bytearray, length: int, *, require_zero: bool = True
) -> tuple[int, int]:
    """Return (VA, file offset) for the pinned V8 zero tail in ``.g8code``."""
    if pe_extend.section_names(data)[-4:] != STACKED_SECTIONS:
        raise ValueError("G9 cave placement requires the pinned ESL2613 V8 section layout")
    _lfanew, _optional, table, count = pe_extend._layout(data)
    for i in range(count):
        off = table + i * 40
        if bytes(data[off : off + 8]).rstrip(b"\0") != STACKED_PROCEDURAL_SECTION:
            continue
        virtual_size, rva, raw_size, raw_ptr = struct.unpack_from("<IIII", data, off + 8)
        start = STACKED_PROCEDURAL_CAVE_OFFSET
        end = start + length
        if end > virtual_size or end > raw_size:
            raise ValueError("G9 procedural code does not fit the pinned .g8code raw/virtual range")
        if require_zero and any(data[raw_ptr + start : raw_ptr + end]):
            raise ValueError("G9 procedural cave preimage is not zero")
        # The exact V8 SHA pin is the primary ownership proof; this local check
        # also makes accidental movement into the existing G8 body impossible.
        if any(data[raw_ptr : raw_ptr + start][22:]):
            raise ValueError("G9 procedural cave overlaps nonzero .g8code content")
        return pe_extend.IMAGE_BASE + rva + start, raw_ptr + start
    raise ValueError("pinned V8 image has no .g8code section")


def _with_g9_section_slot(data: bytes) -> tuple[bytes, bool]:
    """Make exactly one section-header slot without moving any RVA.

    The official image plus G2/G6/G8 fills all four slots released by header
    compaction.  Expand the headers by one FileAlignment before the first raw
    section only when necessary.  Refuse PE layouts with file-offset metadata
    that this G9-local operation cannot safely rebase.
    """
    if pe_extend.free_header_slots(data) > 0:
        return data, False
    lfanew, optional, table, count = pe_extend._layout(data)
    file_align = int.from_bytes(data[optional + 36 : optional + 40], "little")
    size_headers = int.from_bytes(data[optional + 60 : optional + 64], "little")
    first_raw = min(
        int.from_bytes(data[table + i * 40 + 20 : table + i * 40 + 24], "little")
        for i in range(count)
        if int.from_bytes(data[table + i * 40 + 16 : table + i * 40 + 20], "little")
    )
    if file_align <= 0 or first_raw != size_headers:
        raise ValueError("cannot safely expand G9 section table: header/first-raw boundary differs")
    # IMAGE_FILE_HEADER.PointerToSymbolTable is a file offset.
    if int.from_bytes(data[lfanew + 12 : lfanew + 16], "little"):
        raise ValueError("cannot safely expand G9 section table with COFF symbols")
    # Security directory VA is a file offset; debug records contain raw pointers.
    number_dirs = int.from_bytes(data[optional + 92 : optional + 96], "little")
    dirs = optional + 96
    if number_dirs > 4 and any(data[dirs + 4 * 8 : dirs + 5 * 8]):
        raise ValueError("cannot safely expand G9 section table with a certificate directory")
    if number_dirs > 6 and any(data[dirs + 6 * 8 : dirs + 7 * 8]):
        raise ValueError("cannot safely expand G9 section table with a debug directory")
    # Conservatively reject any section raw pointer that would be split by the
    # insertion.  Existing RVAs and virtual layout remain completely intact.
    for i in range(count):
        off = table + i * 40
        raw_size = int.from_bytes(data[off + 16 : off + 20], "little")
        raw_ptr = int.from_bytes(data[off + 20 : off + 24], "little")
        if raw_size and raw_ptr < first_raw:
            raise ValueError("cannot safely expand G9 section table across a section raw range")
    if any(data[table + count * 40 : first_raw]):
        raise ValueError("cannot safely expand G9 section table: reserved header padding is not zero")
    out = bytearray(data)
    out[first_raw:first_raw] = b"\0" * file_align
    for i in range(count):
        ptr_off = table + i * 40 + 20
        raw_ptr = int.from_bytes(out[ptr_off : ptr_off + 4], "little")
        raw_size = int.from_bytes(out[ptr_off - 4 : ptr_off], "little")
        if raw_size and raw_ptr >= first_raw:
            out[ptr_off : ptr_off + 4] = (raw_ptr + file_align).to_bytes(4, "little")
    out[optional + 60 : optional + 64] = (size_headers + file_align).to_bytes(4, "little")
    return bytes(out), True


def restore_candidate(data: bytes) -> bytes:
    """Undo a G9 build and return its exact stacked V8 source bytes.

    Current stacked builds use the pinned ``.g8code`` zero tail and restore
    only the three G9 preimages plus hook bytes.  Historical builds put a new
    G9 section at EOF; when its header expanded, reverse the FileAlignment
    insertion, raw pointers, and header counters. Unsupported layouts are
    refused rather than approximately repaired.
    """
    names = pe_extend.section_names(data)
    if not names:
        raise ValueError("not a G9 candidate")
    lfanew, optional, table, count = pe_extend._layout(data)
    file_align = int.from_bytes(data[optional + 36 : optional + 40], "little")
    size_headers = int.from_bytes(data[optional + 60 : optional + 64], "little")
    stacked_cave = names[-4:] == STACKED_SECTIONS
    if stacked_cave:
        section_va, code_off = _stacked_cave(
            data, len(PROCEDURAL_PREFIX) + 4, require_zero=False
        )
        vsize = raw_size = raw_ptr = 0  # structural removal is not needed
    else:
        if names[-1] != PROCEDURAL_SECTION or count < 1:
            raise ValueError("not a G9 procedural-section candidate")
        new_header = table + (count - 1) * 40
        vsize, rva, raw_size, raw_ptr = struct.unpack_from("<IIII", data, new_header + 8)
        if not raw_size or raw_ptr + raw_size != len(data):
            raise ValueError("G9 section is not the final file payload")
        if raw_size != pe_extend._align(len(PROCEDURAL_PREFIX) + 4, file_align):
            raise ValueError("unexpected G9 section raw size")
        section_va = pe_extend.IMAGE_BASE + rva
        code_off = raw_ptr
    expected_code = bytearray(PROCEDURAL_PREFIX)
    expected_code.extend((PROCEDURAL_CONTINUE - (section_va + len(expected_code) + 4)).to_bytes(4, "little", signed=True))
    if data[code_off : code_off + len(expected_code)] != expected_code:
        raise ValueError("G9 section code preimage mismatch")
    proc_off = pe_extend.va_to_offset(data, PROCEDURAL_SITE)
    expected_detour = b"\xe9" + (section_va - (PROCEDURAL_SITE + 5)).to_bytes(4, "little", signed=True) + b"\x90"
    if data[proc_off : proc_off + len(PROCEDURAL_OLD)] != expected_detour:
        raise ValueError("G9 procedural detour preimage mismatch")
    for va, old, new in CHUNKS:
        off = pe_extend.va_to_offset(data, va)
        if data[off : off + len(new)] != new:
            raise ValueError(f"G9 fixed-map preimage mismatch at 0x{va:08x}")
    marker_off = pe_extend.va_to_offset(data, 0x004ED7F8)
    if data[marker_off : marker_off + len(b"[ESL]2613")] != b"[ESL]2613":
        raise ValueError("G9 rollback only supports ESL2613")
    if not stacked_cave and data[table + (count - 1) * 40 : table + count * 40] != data[new_header : new_header + 40]:
        raise ValueError("malformed G9 section header")
    # Reject layouts whose raw file offsets live outside section headers.
    if int.from_bytes(data[lfanew + 12 : lfanew + 16], "little"):
        raise ValueError("cannot restore G9 image with COFF symbols")
    dirs = optional + 96
    number_dirs = int.from_bytes(data[optional + 92 : optional + 96], "little")
    if number_dirs > 4 and any(data[dirs + 4 * 8 : dirs + 5 * 8]):
        raise ValueError("cannot restore G9 image with a certificate directory")
    if number_dirs > 6 and any(data[dirs + 6 * 8 : dirs + 7 * 8]):
        raise ValueError("cannot restore G9 image with a debug directory")

    if stacked_cave:
        out = bytearray(data)
        if any(out[code_off : code_off + len(expected_code)]):
            out[code_off : code_off + len(expected_code)] = b"\0" * len(expected_code)
    else:
        old_sections = count - 1
        old_first_raw = min(
            int.from_bytes(data[table + i * 40 + 20 : table + i * 40 + 24], "little")
            for i in range(old_sections)
            if int.from_bytes(data[table + i * 40 + 16 : table + i * 40 + 20], "little")
        ) - file_align
        expanded = size_headers == old_first_raw + file_align
        if not expanded:
            raise ValueError("exact G9 rollback supports the expanded stacked-V8 header layout only")
        if old_first_raw < table + old_sections * 40 or old_first_raw > size_headers - file_align:
            raise ValueError("G9 rollback section table does not fit the expanded header")

        out = bytearray(data[:raw_ptr])
        # Remove the section and restore the old PE section table/pointers.
        out[new_header : new_header + 40] = b"\0" * 40
        out[lfanew + 6 : lfanew + 8] = old_sections.to_bytes(2, "little")
        out[optional + 56 : optional + 60] = (
            int.from_bytes(data[optional + 56 : optional + 60], "little") - pe_extend._align(vsize)
        ).to_bytes(4, "little")
        out[optional + 4 : optional + 8] = (
            int.from_bytes(data[optional + 4 : optional + 8], "little") - raw_size
        ).to_bytes(4, "little")
        out[optional + 60 : optional + 64] = (size_headers - file_align).to_bytes(4, "little")
        for i in range(old_sections):
            ptr_off = table + i * 40 + 20
            old_size = int.from_bytes(out[ptr_off - 4 : ptr_off], "little")
            old_ptr = int.from_bytes(out[ptr_off : ptr_off + 4], "little")
            if old_size and old_ptr >= old_first_raw + file_align:
                out[ptr_off : ptr_off + 4] = (old_ptr - file_align).to_bytes(4, "little")
        out[table + old_sections * 40 : old_first_raw + file_align] = b"\0" * (
            old_first_raw + file_align - (table + old_sections * 40)
        )
        del out[old_first_raw : old_first_raw + file_align]
    for va, old, _new in CHUNKS:
        off = pe_extend.va_to_offset(out, va)
        out[off : off + len(old)] = old
    proc_off = pe_extend.va_to_offset(out, PROCEDURAL_SITE)
    out[proc_off : proc_off + len(PROCEDURAL_OLD)] = PROCEDURAL_OLD
    restored = pe_extend._with_checksum(bytes(out))
    if pe_extend.section_names(restored)[-4:] != STACKED_SECTIONS:
        raise ValueError("restored image does not have the expected V8 section closure")
    if hashlib.sha256(restored).hexdigest() != STACKED_V8_SHA256:
        raise ValueError("G9 rollback did not restore the pinned ESL2613 V8 bytes")
    return restored


def build_candidate(data: bytes, *, require_pinned_base: bool = True) -> tuple[bytes, dict[str, Any]]:
    if require_pinned_base:
        pe_extend.verify_base(data)
    marker_off = pe_extend.va_to_offset(data, 0x004ED7F8)
    if data[marker_off : marker_off + len(b"[ESL]2613")] != b"[ESL]2613":
        raise ValueError("G9 only supports the pinned ESL2613 version marker")
    if not require_pinned_base:
        expected_stack = [b".g2bss", b".g2code", b".g6code", b".g8code"]
        if pe_extend.section_names(data)[-4:] != expected_stack:
            raise ValueError("G9 stacked input must be the pinned ESL2613 V8 (G2/G6/G8) section layout")
        if hashlib.sha256(data).hexdigest() != STACKED_V8_SHA256:
            raise ValueError("G9 stacked input SHA256 is not the pinned ESL2613 V8 image")
    if PROCEDURAL_SECTION in pe_extend.section_names(data):
        raise ValueError("G9 procedural section already exists")
    out = bytearray(data)
    # Verify every preimage before any structural edit.  The third site is in
    # the procedural selector and is shared by official and stacked inputs.
    for va, old, new in CHUNKS:
        off = pe_extend.va_to_offset(data, va)
        if data[off : off + len(old)] != old:
            raise ValueError(f"G9 site 0x{va:08x} old bytes do not match (already applied?)")
        if _context_digest(data, va) != CONTEXT_SHA256[va]:
            raise ValueError(f"G9 context around 0x{va:08x} differs from the pinned 2610-line code")
    proc_off = pe_extend.va_to_offset(data, PROCEDURAL_SITE)
    if data[proc_off : proc_off + len(PROCEDURAL_OLD)] != PROCEDURAL_OLD:
        raise ValueError("G9 procedural selector old bytes do not match (already applied?)")
    if _context_digest(data, PROCEDURAL_SITE) != PROCEDURAL_CONTEXT_SHA256:
        raise ValueError("G9 procedural selector context differs from the pinned ESL 2613 path")

    image = bytes(out)
    if require_pinned_base:
        image = pe_extend.compact_headers(image)
        image, expanded_headers = _with_g9_section_slot(image)
        code_va = int.from_bytes(
            image[pe_extend._layout(image)[1] + 56 : pe_extend._layout(image)[1] + 60], "little"
        ) + pe_extend.IMAGE_BASE
        code_off = None
    else:
        # The pinned stacked V8 already consumes every compacted header slot.
        # Its verified zero tail has enough executable padding for this stub,
        # avoiding a 95th section and the Windows loader's header/RVA overlap.
        code_va, code_off = _stacked_cave(image, len(PROCEDURAL_PREFIX) + 4)
        expanded_headers = False
    code = bytearray(PROCEDURAL_PREFIX)
    return_va = PROCEDURAL_CONTINUE
    return_disp = return_va - (code_va + len(code) + 4)
    code.extend(return_disp.to_bytes(4, "little", signed=True))
    if code_off is None:
        image = pe_extend.add_section(image, PROCEDURAL_SECTION, bytes(code), len(code), pe_extend.CODE_RX)
        section_va = pe_extend.section_va(image, PROCEDURAL_SECTION)
        if section_va != code_va:
            raise ValueError("G9 procedural section VA changed unexpectedly")
    else:
        image = bytearray(image)
        image[code_off : code_off + len(code)] = code
        image = bytes(image)
        section_va = code_va
    proc_off = pe_extend.va_to_offset(image, PROCEDURAL_SITE)
    detour_disp = code_va - (PROCEDURAL_SITE + 5)
    detour = b"\xe9" + detour_disp.to_bytes(4, "little", signed=True) + b"\x90"
    if len(detour) != len(PROCEDURAL_OLD):
        raise AssertionError("G9 procedural detour must replace exactly six bytes")
    image = bytearray(image)
    image[proc_off : proc_off + len(detour)] = detour
    for va, old, new in CHUNKS:
        off = pe_extend.va_to_offset(image, va)
        if image[off : off + len(old)] != old:
            raise ValueError(f"G9 site 0x{va:08x} changed while extending the section table")
        image[off : off + len(new)] = new
    candidate = pe_extend._with_checksum(bytes(image))
    return candidate, {
        "schema": "syw2plus.esl2613.g9-fixed-start.v3",
        "chunks": [hex(va) for va, _old, _new in CHUNKS] + [hex(PROCEDURAL_SITE)],
        "input_sha256": hashlib.sha256(data).hexdigest(),
        "candidate_sha256": hashlib.sha256(candidate).hexdigest(),
        "procedural_section_va": hex(code_va),
        "procedural_placement": "new-section" if code_off is None else "pinned-.g8code-zero-tail",
        "procedural_file_offset": hex(code_off) if code_off is not None else None,
        "procedural_code_hex": bytes(code).hex(),
        "expanded_headers": expanded_headers,
    }


def write_candidate(source: Path, destination: Path, *, require_pinned_base: bool = True) -> dict[str, Any]:
    if destination.resolve() == source.resolve():
        raise ValueError("refusing to overwrite the input EXE")
    candidate, report = build_candidate(source.read_bytes(), require_pinned_base=require_pinned_base)
    fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(fd, "wb") as handle:
        handle.write(candidate)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--stacked", action="store_true", help="input is the pinned ESL2613 V8 image")
    args = parser.parse_args()
    report = write_candidate(args.source, args.destination, require_pinned_base=not args.stacked)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
