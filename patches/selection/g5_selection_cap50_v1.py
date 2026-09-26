#!/usr/bin/env python3
"""Build the first private G5 selection-cap candidate.

This module relocates the stock 20-entry selection table into a newly mapped
zero-backed tail before ``.rsrc``.  The PE geometry follows the accepted B-1
pattern used by ``g2_unit_pool_expansion_v1.py``: no raw bytes move, ``.data``
VirtualSize grows, and ``.rsrc`` plus its resource RVAs move upward.

The adjacent unit-existence array is deliberately not moved.  It is a live
G2 array, not free selection storage.  The candidate reserves a separate
10x50 control-group side-table span for the later W2b work, but does not
rewire the player-structure group fields yet; changing those 20-entry fields
without a structure relocation would corrupt following fields.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

import capstone
import pefile

from patches.population.base_preserving_storage_layout_v1 import (
    IMAGE_BASE,
    ORIGINAL_SHA256,
    PAYLOAD_ENTRY_OFFSETS,
    RSRC_BASE_VA,
    RSRC_SIZE,
    SECTION_ALIGNMENT,
)

STOCK_CAPACITY = 20
TARGET_CAPACITY = 50
ENTRY_BYTES = 4
CONTROL_GROUPS = 10
CONTROL_GROUP_ENTRY_BYTES = 4
CONSUMER_FRAME_BYTES = 0x270
CONSUMER_WORD_BUFFER_OFFSET = 0x200
CONSUMER_CLEAR_DWORDS = 0x19

# The storage is placed at the old .rsrc VA, which is the first byte after the
# mapped .data BSS.  The first 0x100-byte boundary keeps the control-group
# reservation separate from the selection table and makes canaries easy to
# inspect in a debugger.
SELECTION_BASE = RSRC_BASE_VA
CONTROL_GROUP_BASE = SELECTION_BASE + 0x100
SELECTION_BYTES = TARGET_CAPACITY * ENTRY_BYTES
CONTROL_GROUP_BYTES = CONTROL_GROUPS * TARGET_CAPACITY * CONTROL_GROUP_ENTRY_BYTES
STORAGE_END = CONTROL_GROUP_BASE + CONTROL_GROUP_BYTES


class BuildAbortedError(RuntimeError):
    """Raised when a pinned byte or PE invariant does not match."""


def _align(value: int, boundary: int) -> int:
    return (value + boundary - 1) // boundary * boundary


def verify_original(data: bytes) -> None:
    if hashlib.sha256(data).hexdigest() != ORIGINAL_SHA256:
        raise ValueError("original EXE SHA256 mismatch; refusing to build a candidate")


def _read_section(data: bytes, section_table: int, index: int) -> tuple[bytes, int, int, int, int, int]:
    off = section_table + index * 40
    name = data[off : off + 8].rstrip(b"\0")
    vsz, va, rsz, rp = struct.unpack_from("<IIII", data, off + 8)
    return name, off, vsz, va, rsz, rp


def _header_artifact(original: bytes) -> tuple[bytes, dict[str, int]]:
    """Grow the mapped BSS tail and move the resource section in a copy."""
    verify_original(original)
    out = bytearray(original)
    pe_off = struct.unpack_from("<I", out, 0x3C)[0]
    if out[pe_off : pe_off + 4] != b"PE\0\0":
        raise BuildAbortedError("bad PE signature")
    num_sections = struct.unpack_from("<H", out, pe_off + 6)[0]
    opt_size = struct.unpack_from("<H", out, pe_off + 20)[0]
    opt = pe_off + 24
    if struct.unpack_from("<H", out, opt)[0] != 0x10B:
        raise BuildAbortedError("candidate requires PE32")
    section_alignment, file_alignment = struct.unpack_from("<II", out, opt + 32)
    if section_alignment != SECTION_ALIGNMENT or file_alignment != SECTION_ALIGNMENT:
        raise BuildAbortedError("unsupported PE alignment")
    section_table = pe_off + 24 + opt_size
    data_idx = rsrc_idx = None
    for i in range(num_sections):
        name, _off, _vsz, _va, _rsz, _rp = _read_section(out, section_table, i)
        if name == b".data":
            data_idx = i
        elif name == b".rsrc":
            rsrc_idx = i
    if data_idx is None or rsrc_idx is None:
        raise BuildAbortedError("expected .data and .rsrc sections")

    _, data_off, _data_vsz, data_va, _data_rsz, _data_rp = _read_section(
        out, section_table, data_idx
    )
    _, rsrc_off, _rsrc_vsz, rsrc_va, _rsrc_rsz, rsrc_rp = _read_section(
        out, section_table, rsrc_idx
    )
    old_rsrc = IMAGE_BASE + rsrc_va
    if old_rsrc != RSRC_BASE_VA:
        raise BuildAbortedError(f"unexpected .rsrc VA 0x{old_rsrc:08x}")
    new_rsrc = _align(STORAGE_END, SECTION_ALIGNMENT)
    new_rsrc_rva = new_rsrc - IMAGE_BASE
    old_end = IMAGE_BASE + data_va
    new_data_vsz = new_rsrc - old_end
    if new_data_vsz <= 0 or new_rsrc <= STORAGE_END:
        raise BuildAbortedError("storage is not fully covered before .rsrc")

    struct.pack_into("<I", out, data_off + 8, new_data_vsz)
    struct.pack_into("<I", out, rsrc_off + 12, new_rsrc_rva)
    resource_dir = opt + 96 + 2 * 8
    dir_rva, _dir_size = struct.unpack_from("<II", out, resource_dir)
    if dir_rva != rsrc_va:
        raise BuildAbortedError("resource data directory does not alias .rsrc")
    struct.pack_into("<I", out, resource_dir, new_rsrc_rva)
    struct.pack_into("<I", out, opt + 56, _align(new_rsrc - IMAGE_BASE + RSRC_SIZE, SECTION_ALIGNMENT))

    rsrc_delta = new_rsrc - old_rsrc
    for local_offset in PAYLOAD_ENTRY_OFFSETS:
        field = rsrc_rp + local_offset
        old_value = struct.unpack_from("<I", out, field)[0]
        struct.pack_into("<I", out, field, old_value + rsrc_delta)

    return bytes(out), {
        "old_rsrc": old_rsrc,
        "new_rsrc": new_rsrc,
        "rsrc_delta": rsrc_delta,
        "new_data_virtual_size": new_data_vsz,
        "new_size_of_image": _align(new_rsrc - IMAGE_BASE + RSRC_SIZE, SECTION_ALIGNMENT),
    }


def _va_to_file_offset(pe: pefile.PE, va: int) -> int:
    for section in pe.sections:
        start = IMAGE_BASE + int(section.VirtualAddress)
        raw_size = int(section.SizeOfRawData)
        if start <= va < start + raw_size:
            return int(section.PointerToRawData) + va - start
    raise BuildAbortedError(f"VA 0x{va:08x} is not in a raw section")


def _patch_instruction_value(
    out: bytearray, pe: pefile.PE, va: int, old_value: int, new_value: int
) -> None:
    file_off = _va_to_file_offset(pe, va)
    probe = bytes(out[file_off : file_off + 16])
    engine = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    insn = next(engine.disasm(probe, va), None)
    if insn is None or insn.address != va:
        raise BuildAbortedError(f"0x{va:08x}: instruction decode failed")
    encoded = probe[: insn.size]
    needle = struct.pack("<I", old_value & 0xFFFFFFFF)
    positions = [i for i in range(len(encoded) - 3) if encoded[i : i + 4] == needle]
    if len(positions) != 1:
        raise BuildAbortedError(
            f"0x{va:08x}: expected one 0x{old_value:08x} operand, got {len(positions)}"
        )
    pos = file_off + positions[0]
    out[pos : pos + 4] = struct.pack("<I", new_value & 0xFFFFFFFF)


def _patch_exact(out: bytearray, pe: pefile.PE, va: int, old: bytes, new: bytes) -> None:
    off = _va_to_file_offset(pe, va)
    actual = bytes(out[off : off + len(old)])
    if actual != old:
        raise BuildAbortedError(
            f"0x{va:08x}: old bytes mismatch expected={old.hex()} actual={actual.hex()}"
        )
    if len(new) != len(old):
        raise BuildAbortedError(f"0x{va:08x}: replacement changes instruction length")
    out[off : off + len(old)] = new


# Each group is explicit so a changed original cannot silently receive a
# partial relocation.  Values are from the lap628 inventory and its old-byte
# regression; the slot-index array at 0x8990c8 is intentionally absent.
DIRECT_SITES: tuple[tuple[int, bytes, int], ...] = (
    (0x00412E68, bytes.fromhex("a1 24 90 89 00"), 0x00899024),
    (0x00412E6E, bytes.fromhex("a3 24 90 89 00"), 0x00899024),
    (0x00412ECC, bytes.fromhex("a1 24 90 89 00"), 0x00899024),
    (0x00412ED2, bytes.fromhex("a3 24 90 89 00"), 0x00899024),
    (0x0041D360, bytes.fromhex("a1 24 90 89 00"), 0x00899024),
    (0x0041F599, bytes.fromhex("83 3d 24 90 89 00 01"), 0x00899024),
    (0x00498FBA, bytes.fromhex("a1 24 90 89 00"), 0x00899024),
    (0x00499872, bytes.fromhex("39 1d 24 90 89 00"), 0x00899024),
    (0x0049ACD1, bytes.fromhex("a1 24 90 89 00"), 0x00899024),
    (0x00412DBF, bytes.fromhex("b8 28 90 89 00"), 0x00899028),
    (0x00412E3C, bytes.fromhex("b8 28 90 89 00"), 0x00899028),
    (0x00412E61, bytes.fromhex("89 14 8d 28 90 89 00"), 0x00899028),
    (0x00412E9F, bytes.fromhex("b8 28 90 89 00"), 0x00899028),
    (0x00412EBC, bytes.fromhex("66 89 3c 8d 28 90 89 00"), 0x00899028),
    (0x0041708A, bytes.fromhex("be 28 90 89 00"), 0x00899028),
    (0x0041DD48, bytes.fromhex("b8 28 90 89 00"), 0x00899028),
    (0x0041DF50, bytes.fromhex("be 28 90 89 00"), 0x00899028),
    (0x0041E7FE, bytes.fromhex("a1 28 90 89 00"), 0x00899028),
    (0x0041E810, bytes.fromhex("8b 0d 28 90 89 00"), 0x00899028),
    (0x0041EC71, bytes.fromhex("66 8b 34 95 28 90 89 00"), 0x00899028),
    (0x0041ED5E, bytes.fromhex("66 8b 34 95 28 90 89 00"), 0x00899028),
    (0x0041EEAF, bytes.fromhex("66 8b 34 95 28 90 89 00"), 0x00899028),
    (0x0041F03A, bytes.fromhex("be 28 90 89 00"), 0x00899028),
    (0x00445D52, bytes.fromhex("bb 28 90 89 00"), 0x00899028),
    (0x00498FDD, bytes.fromhex("bf 28 90 89 00"), 0x00899028),
    (0x00499040, bytes.fromhex("b8 28 90 89 00"), 0x00899028),
    (0x0049906E, bytes.fromhex("89 15 28 90 89 00"), 0x00899028),
    (0x0049933E, bytes.fromhex("bd 28 90 89 00"), 0x00899028),
    (0x004998B5, bytes.fromhex("b8 28 90 89 00"), 0x00899028),
    (0x004998D2, bytes.fromhex("8b 0c 8d 28 90 89 00"), 0x00899028),
    (0x0049A7DF, bytes.fromhex("66 a1 28 90 89 00"), 0x00899028),
    (0x0049A995, bytes.fromhex("66 a1 28 90 89 00"), 0x00899028),
    (0x0049A9F0, bytes.fromhex("66 a1 28 90 89 00"), 0x00899028),
    (0x0049ACDE, bytes.fromhex("b8 28 90 89 00"), 0x00899028),
    (0x004A4242, bytes.fromhex("b8 28 90 89 00"), 0x00899028),
    (0x004A4261, bytes.fromhex("66 8b 04 8d 28 90 89 00"), 0x00899028),
    (0x004AE58C, bytes.fromhex("be 28 90 89 00"), 0x00899028),
    (0x00412EC4, bytes.fromhex("66 89 3c 8d 2a 90 89 00"), 0x0089902A),
)

END_SITES: tuple[tuple[int, bytes], ...] = (
    (0x00412DD5, bytes.fromhex("3d 78 90 89 00")),
    (0x00412E52, bytes.fromhex("3d 78 90 89 00")),
    (0x00412EB3, bytes.fromhex("3d 78 90 89 00")),
    (0x004170BD, bytes.fromhex("81 fe 78 90 89 00")),
    (0x0041DD69, bytes.fromhex("3d 78 90 89 00")),
    (0x0041DFAF, bytes.fromhex("81 fe 78 90 89 00")),
    (0x0041F068, bytes.fromhex("81 fe 78 90 89 00")),
    (0x00445E0B, bytes.fromhex("81 fb 78 90 89 00")),
    (0x00499012, bytes.fromhex("81 ff 78 90 89 00")),
    (0x0049904F, bytes.fromhex("3d 78 90 89 00")),
    (0x00499577, bytes.fromhex("81 fd 78 90 89 00")),
    (0x004998C9, bytes.fromhex("3d 78 90 89 00")),
    (0x0049ACED, bytes.fromhex("3d 78 90 89 00")),
    (0x004A4258, bytes.fromhex("3d 78 90 89 00")),
)

ROTATION_SITES: tuple[tuple[int, bytes], ...] = (
    (0x0041EC6A, bytes.fromhex("b9 14 00 00 00")),
    (0x0041ED15, bytes.fromhex("83 ff 14")),
    (0x0041ED57, bytes.fromhex("b9 14 00 00 00")),
    (0x0041EDF7, bytes.fromhex("83 ff 14")),
    (0x0041EEA8, bytes.fromhex("b9 14 00 00 00")),
    (0x0041EF39, bytes.fromhex("83 ff 14")),
)

# The selection-change consumer keeps a compact local copy before updating
# the UI/selection state.  Its original 20-entry list occupied [esp+0x30,
# esp+0x7f], while the same frame also used [esp+0x80,...] as a temporary
# word buffer.  Expand the frame and move that temporary buffer to 0x200 so
# the 50-entry list cannot overlap it or the return path.
SELECTION_CONSUMER_LIMIT_SITES: tuple[tuple[int, bytes, bytes], ...] = (
    (0x0041DC40, bytes.fromhex("81 ec 98 00 00 00"), bytes.fromhex("81 ec 70 02 00 00")),
    (0x0041DC53, bytes.fromhex("8d bc 24 80 00 00 00"), bytes.fromhex("8d bc 24 00 02 00 00")),
    (0x0041DC68, bytes.fromhex("b8 14 00 00 00"), bytes.fromhex("b8 32 00 00 00")),
    (0x0041DDE4, bytes.fromhex("83 ff 14"), bytes.fromhex("83 ff 32")),
    (0x0041DE55, bytes.fromhex("bf 14 00 00 00"), bytes.fromhex("bf 32 00 00 00")),
    (0x0041DE8A, bytes.fromhex("66 89 84 4c 80 00 00 00"), bytes.fromhex("66 89 84 4c 00 02 00 00")),
    # This second temporary word follows the original 20-entry list.  Once
    # the list is 50 entries, [esp+0x84] is inside that list and corrupts its
    # later entries/return path; keep the paired temporary at +0x204.
    (0x0041DEBD, bytes.fromhex("66 89 84 24 84 00 00 00"), bytes.fromhex("66 89 84 24 04 02 00 00")),
    (0x0041E010, bytes.fromhex("66 89 9c 04 80 00 00 00"), bytes.fromhex("66 89 9c 04 00 02 00 00")),
    (0x0041E04C, bytes.fromhex("8d 8c 24 80 00 00 00"), bytes.fromhex("8d 8c 24 00 02 00 00")),
    (0x0041E141, bytes.fromhex("66 89 9c 04 80 00 00 00"), bytes.fromhex("66 89 9c 04 00 02 00 00")),
    (0x0041E16F, bytes.fromhex("66 8b b4 54 80 00 00 00"), bytes.fromhex("66 8b b4 54 00 02 00 00")),
    (0x0041E1EC, bytes.fromhex("81 c4 98 00 00 00"), bytes.fromhex("81 c4 70 02 00 00")),
    (0x0041E20A, bytes.fromhex("81 c4 98 00 00 00"), bytes.fromhex("81 c4 70 02 00 00")),
    (0x0041DC4C, bytes.fromhex("b9 0a 00 00 00"), bytes.fromhex("b9 19 00 00 00")),
)

# FUN_004386E0 appends a hit-test result to the caller-owned buffer.  The
# compare is reached from FUN_004384B0 for every eligible unit and was the
# runtime-confirmed upstream cap that kept the relocated consumer at 20.
HIT_TEST_APPEND_LIMIT_SITES: tuple[tuple[int, bytes, bytes], ...] = (
    (0x0043877A, bytes.fromhex("66 3d 14 00"), bytes.fromhex("66 3d 32 00")),
)


def _replace_operand_group(
    out: bytearray, pe: pefile.PE, sites: tuple[tuple[int, bytes], ...], old: int, new: int
) -> None:
    for va, expected in sites:
        _patch_exact(out, pe, va, expected, expected.replace(bytes([old]), bytes([new]), 1))


def build_candidate(original: bytes) -> tuple[bytes, dict[str, Any]]:
    stage, geometry = _header_artifact(original)
    out = bytearray(stage)
    pe = pefile.PE(data=bytes(out), fast_load=True)
    try:
        for va, old_bytes, old_value in DIRECT_SITES:
            new_value = {
                0x00899024: SELECTION_BASE,
                0x00899028: SELECTION_BASE + 4,
                0x0089902A: SELECTION_BASE + 6,
            }[old_value]
            _patch_exact(out, pe, va, old_bytes, old_bytes.replace(struct.pack("<I", old_value), struct.pack("<I", new_value), 1))
        for va, old_bytes in END_SITES:
            _patch_exact(out, pe, va, old_bytes, old_bytes.replace(struct.pack("<I", 0x00899078), struct.pack("<I", SELECTION_BASE + ENTRY_BYTES + SELECTION_BYTES), 1))
        _replace_operand_group(out, pe, ROTATION_SITES, 0x14, TARGET_CAPACITY)
        for va, old_bytes, new_bytes in SELECTION_CONSUMER_LIMIT_SITES:
            _patch_exact(out, pe, va, old_bytes, new_bytes)
        for va, old_bytes, new_bytes in HIT_TEST_APPEND_LIMIT_SITES:
            _patch_exact(out, pe, va, old_bytes, new_bytes)
    finally:
        pe.close()
    if len(out) != len(original):
        raise BuildAbortedError("candidate changed raw file length")
    report = {
        "schema": "syw2plus.g5-selection-cap50-candidate.v1",
        "status": "SELECTION_RELOCATED_GROUP_SIDE_TABLE_RESERVED",
        "original_sha256": ORIGINAL_SHA256,
        "candidate_sha256": hashlib.sha256(bytes(out)).hexdigest(),
        "stock_capacity": STOCK_CAPACITY,
        "target_capacity": TARGET_CAPACITY,
        "selection_base": f"0x{SELECTION_BASE:08x}",
        "selection_end_exclusive": f"0x{SELECTION_BASE + ENTRY_BYTES + SELECTION_BYTES:08x}",
        "control_group_base": f"0x{CONTROL_GROUP_BASE:08x}",
        "control_group_bytes": CONTROL_GROUP_BYTES,
        "geometry": geometry,
        "patched_direct_sites": len(DIRECT_SITES),
        "patched_end_sites": len(END_SITES),
        "patched_rotation_sites": len(ROTATION_SITES),
        "patched_selection_consumer_sites": len(SELECTION_CONSUMER_LIMIT_SITES),
        "patched_hit_test_append_limit_sites": len(HIT_TEST_APPEND_LIMIT_SITES),
        "slot_index_array": "0x008990c8 unchanged",
        "command_packet": "unchanged; 20-entry packet remains pending W2b/command design",
        "control_group_fields": "unchanged; 20-entry PlayerStruct fields remain pending side-table wiring",
    }
    return bytes(out), report


def restore_candidate(candidate: bytes, original: bytes) -> bytes:
    """Restore exactly the pinned original, refusing unknown candidates.

    This is intentionally a byte-identity restore rather than a best-effort
    reverse patch.  It prevents a candidate from a different source SHA or a
    manually edited executable from being mistaken for this patch's output.
    """
    verify_original(original)
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
