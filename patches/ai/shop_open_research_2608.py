#!/usr/bin/env python3
"""Build a copy-only 2608 candidate that exposes shop-opening research to AI.

The 2608 AI selector at ``0x00406C70`` walks a 143-row table at
``0x004EC514`` (18 bytes per row, followed by a ``0xFFFE`` sentinel).  The
three market buildings have only the existing resource-value research (RID
27) in that table; the game data nevertheless contains the shop-opening
research flag (RID 20).  This candidate relocates the table to a new PE
section, appends one RID-20 row for each market building, and rewrites every
selector reference to the relocated base.

This module is deliberately copy-only.  ``build_candidate`` works on bytes
and never writes its input.  ``write_candidate`` creates a fresh destination
with exclusive creation, and ``restore_candidate`` is an exact inverse for a
candidate produced by this module.  It does not launch Wine/the game.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any

IMAGE_BASE = 0x00400000
ORIGINAL_SHA256 = "bf39cb73f395d677a1c27fda01698f849b23973a39fd9be8b22af0010cb60f27"
ORIGINAL_FILE_SIZE = 0x104000
ORIGINAL_SIZE_OF_IMAGE = 0xD2D000
ORIGINAL_SIZE_OF_INITIALIZED_DATA = 0xBB0000
SECTION_ALIGNMENT = 0x1000
FILE_ALIGNMENT = 0x1000

OLD_TABLE_VA = 0x004EC514
OLD_TABLE_FILE_OFFSET = 0x000EC514
TABLE_STRIDE = 18
OLD_ROW_COUNT = 143
OLD_TABLE_LEN = OLD_ROW_COUNT * TABLE_STRIDE + 2  # rows + 0xFFFE sentinel
TABLE_SHA256 = "86e6fd94f604b0045005734ba3ef1c5b3343dc7914d5e3bf33e003f6140ae85c"
SELECTOR_START = 0x00406C70
SELECTOR_END = 0x00406E98

# The XLSX and the 2608 data table identify these as building kinds 48, 57,
# and 73.  RID 27 remains in all three original rows; these are additions,
# not substitutions.  The remaining fields use the same ``unset`` encoding
# as the corresponding existing RID-27 rows.
SHOP_BUILDINGS = (0x30, 0x39, 0x49)
SHOP_RESEARCH_RID = 20
EXISTING_RESOURCE_RESEARCH_RID = 27
UNSET = 0xFFFF


@dataclass(frozen=True)
class SelectorReference:
    """One absolute table address embedded in a selector instruction."""

    va: int
    immediate_offset: int
    table_offset: int
    old_bytes: bytes

    @property
    def field_va(self) -> int:
        return self.va + self.immediate_offset


SELECTOR_REFERENCES: tuple[SelectorReference, ...] = (
    SelectorReference(
        0x00406C81, 3, 0,
        bytes.fromhex("66 83 3d 14 c5 4e 00 fe"),
    ),
    SelectorReference(
        0x00406C95, 1, 4,
        bytes.fromhex("b8 18 c5 4e 00"),
    ),
    SelectorReference(
        0x00406D38, 3, 8,
        bytes.fromhex("66 8b b0 1c c5 4e 00"),
    ),
    SelectorReference(
        0x00406D3F, 3, 0,
        bytes.fromhex("0f bf a8 14 c5 4e 00"),
    ),
    SelectorReference(
        0x00406D4D, 3, 10,
        bytes.fromhex("66 8b b8 1e c5 4e 00"),
    ),
    SelectorReference(
        0x00406DB7, 3, 12,
        bytes.fromhex("66 8b b0 20 c5 4e 00"),
    ),
    SelectorReference(
        0x00406DE7, 3, 14,
        bytes.fromhex("66 8b b0 22 c5 4e 00"),
    ),
    SelectorReference(
        0x00406E17, 3, 16,
        bytes.fromhex("66 8b 90 24 c5 4e 00"),
    ),
    SelectorReference(
        0x00406E62, 3, 6,
        bytes.fromhex("66 8b 80 1a c5 4e 00"),
    ),
    SelectorReference(
        0x00406E76, 3, 4,
        bytes.fromhex("66 8b 80 18 c5 4e 00"),
    ),
)


class BuildAbortedError(RuntimeError):
    """Raised when a source does not match the pinned 2608 layout."""


def _align(value: int, alignment: int) -> int:
    if alignment <= 0 or alignment & (alignment - 1):
        raise ValueError(f"unsupported non-power-of-two alignment: {alignment:#x}")
    return (value + alignment - 1) & -alignment


def _u16(data: bytes | bytearray, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def _u32(data: bytes | bytearray, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def _section_table(data: bytes | bytearray) -> tuple[int, int, int, int, int]:
    if len(data) < 0x40 or data[:2] != b"MZ":
        raise BuildAbortedError("not a DOS/PE image")
    pe_offset = _u32(data, 0x3C)
    if pe_offset + 24 > len(data) or data[pe_offset : pe_offset + 4] != b"PE\0\0":
        raise BuildAbortedError("bad PE signature")
    number_sections = _u16(data, pe_offset + 6)
    optional_size = _u16(data, pe_offset + 20)
    optional = pe_offset + 24
    if optional + optional_size > len(data) or _u16(data, optional) != 0x10B:
        raise BuildAbortedError("2608 patch requires PE32")
    section_alignment = _u32(data, optional + 32)
    file_alignment = _u32(data, optional + 36)
    if section_alignment != SECTION_ALIGNMENT or file_alignment != FILE_ALIGNMENT:
        raise BuildAbortedError("unsupported PE section/file alignment")
    table = optional + optional_size
    if table + number_sections * 40 > len(data):
        raise BuildAbortedError("truncated section table")
    return pe_offset, number_sections, optional, table, optional_size


def _sections(data: bytes | bytearray) -> list[dict[str, int | bytes]]:
    _pe, count, _optional, table, _size = _section_table(data)
    result: list[dict[str, int | bytes]] = []
    for index in range(count):
        off = table + index * 40
        result.append(
            {
                "index": index,
                "header": off,
                "name": bytes(data[off : off + 8]).rstrip(b"\0"),
                "virtual_size": _u32(data, off + 8),
                "virtual_address": _u32(data, off + 12),
                "raw_size": _u32(data, off + 16),
                "raw_pointer": _u32(data, off + 20),
                "characteristics": _u32(data, off + 36),
            }
        )
    return result


def _va_to_file_offset(data: bytes | bytearray, va: int, length: int = 1) -> int:
    if va < IMAGE_BASE:
        raise BuildAbortedError(f"VA below image base: {va:#x}")
    rva = va - IMAGE_BASE
    for section in _sections(data):
        start = int(section["virtual_address"])
        raw_size = int(section["raw_size"])
        if start <= rva and rva + length <= start + raw_size:
            offset = int(section["raw_pointer"]) + (rva - start)
            if offset + length > len(data):
                break
            return offset
    raise BuildAbortedError(f"VA is not backed by file bytes: {va:#x}+{length:#x}")


def _section_by_name(data: bytes | bytearray, name: bytes) -> dict[str, int | bytes]:
    matches = [section for section in _sections(data) if section["name"] == name]
    if len(matches) != 1:
        raise BuildAbortedError(f"expected exactly one {name!r} section, got {len(matches)}")
    return matches[0]


def verify_original(data: bytes) -> None:
    """Fail closed unless ``data`` is the pinned 2608 input byte-for-byte."""

    if len(data) != ORIGINAL_FILE_SIZE:
        raise ValueError(f"2608 source size mismatch: {len(data):#x}")
    digest = hashlib.sha256(data).hexdigest()
    if digest != ORIGINAL_SHA256:
        raise ValueError(f"2608 source SHA256 mismatch: {digest}")


def _research_row(building: int, rid: int = SHOP_RESEARCH_RID) -> bytes:
    return struct.pack(
        "<9H", 0x000F, building, UNSET, rid, UNSET, UNSET, UNSET, UNSET, UNSET
    )


def _read_old_table(data: bytes) -> bytes:
    table_offset = _va_to_file_offset(data, OLD_TABLE_VA, OLD_TABLE_LEN)
    if table_offset != OLD_TABLE_FILE_OFFSET:
        raise BuildAbortedError(
            f"2608 table file offset changed: {table_offset:#x} != {OLD_TABLE_FILE_OFFSET:#x}"
        )
    table = data[table_offset : table_offset + OLD_TABLE_LEN]
    rows = table[: OLD_ROW_COUNT * TABLE_STRIDE]
    if hashlib.sha256(table).hexdigest() != TABLE_SHA256:
        raise BuildAbortedError("2608 AI table bytes do not match the pinned table")
    for index in range(OLD_ROW_COUNT):
        if rows[index * TABLE_STRIDE : index * TABLE_STRIDE + 2] == b"\xfe\xff":
            raise BuildAbortedError(f"AI table sentinel appeared early at row {index}")
    if table[-2:] != b"\xfe\xff":
        raise BuildAbortedError("AI table sentinel is not 0xFFFE")
    return table


def _check_selector_references(data: bytes) -> dict[int, list[int]]:
    """Check both pinned instruction bytes and completeness of all old refs."""

    text = _section_by_name(data, b".text")
    text_raw = int(text["raw_pointer"])
    text_bytes = data[text_raw : text_raw + int(text["raw_size"])]
    expected: dict[int, list[int]] = {}
    for ref in SELECTOR_REFERENCES:
        if not SELECTOR_START <= ref.va < SELECTOR_END:
            raise BuildAbortedError(f"selector ref outside FUN0x406C70: {ref.va:#x}")
        off = _va_to_file_offset(data, ref.va, len(ref.old_bytes))
        if data[off : off + len(ref.old_bytes)] != ref.old_bytes:
            raise BuildAbortedError(f"selector old bytes mismatch at {ref.va:#x}")
        field_file_offset = off + ref.immediate_offset
        old_value = _u32(data, field_file_offset)
        expected.setdefault(old_value, []).append(field_file_offset - text_raw)

    # Every old table absolute address in executable code must be one of the
    # ten selector fields above.  This catches a newly discovered selector
    # reference instead of silently leaving it pointed at the old table.
    found: dict[int, list[int]] = {}
    old_values = set(expected)
    for rel in range(0, len(text_bytes) - 3):
        value = _u32(text_bytes, rel)
        if value in old_values:
            found.setdefault(value, []).append(rel)
    if found != expected:
        raise BuildAbortedError(
            "selector table-reference inventory changed: "
            f"expected={expected!r} found={found!r}"
        )
    return expected


def _new_section_geometry(data: bytes, payload_len: int) -> dict[str, int]:
    _pe, count, _optional, table, _size = _section_table(data)
    sections = _sections(data)
    if any(section["name"] == b".shopai" for section in sections):
        raise BuildAbortedError("candidate section .shopai already exists")
    section_alignment = _u32(data, _optional + 32)
    file_alignment = _u32(data, _optional + 36)
    va_end = max(
        int(section["virtual_address"])
        + max(int(section["virtual_size"]), int(section["raw_size"]))
        for section in sections
    )
    raw_end = max(
        int(section["raw_pointer"]) + int(section["raw_size"]) for section in sections
    )
    new_va = _align(va_end, section_alignment)
    new_raw = _align(len(data), file_alignment)
    raw_size = _align(payload_len, file_alignment)
    header_end = table + (count + 1) * 40
    size_headers = _u32(data, _optional + 60)
    if header_end > size_headers or header_end > new_raw:
        raise BuildAbortedError("no room for an additional PE section header")
    if new_raw < raw_end:
        raise BuildAbortedError("new section raw range overlaps an existing section")
    virtual_end = new_va + payload_len
    image_end = _align(virtual_end, section_alignment)
    if image_end >= 2**32 or new_va >= 2**32:
        raise BuildAbortedError("new section exceeds PE32 address range")
    for section in sections:
        old_start = int(section["virtual_address"])
        old_end = old_start + max(int(section["virtual_size"]), int(section["raw_size"]))
        if not (new_va >= old_end or virtual_end <= old_start):
            raise BuildAbortedError("new section virtual range overlaps an existing section")
    return {
        "header": table + count * 40,
        "number_sections_before": count,
        "virtual_address": new_va,
        "virtual_size": payload_len,
        "raw_pointer": new_raw,
        "raw_size": raw_size,
        "size_of_image": image_end,
        "raw_end_before": raw_end,
    }


def _patch_selector_refs(
    out: bytearray, geometry: dict[str, int], expected: dict[int, list[int]]
) -> list[dict[str, str | int]]:
    new_base = IMAGE_BASE + geometry["virtual_address"]
    changed: list[dict[str, str | int]] = []
    for ref in SELECTOR_REFERENCES:
        off = _va_to_file_offset(out, ref.va, len(ref.old_bytes))
        old_value = _u32(out, off + ref.immediate_offset)
        new_value = new_base + ref.table_offset
        if old_value != OLD_TABLE_VA + ref.table_offset:
            raise BuildAbortedError(
                f"selector ref value mismatch at {ref.va:#x}: {old_value:#x}"
            )
        struct.pack_into("<I", out, off + ref.immediate_offset, new_value)
        changed.append(
            {
                "va": f"0x{ref.va:08x}",
                "table_offset": ref.table_offset,
                "old_value": f"0x{old_value:08x}",
                "new_value": f"0x{new_value:08x}",
            }
        )
    # The inventory is consumed here so callers cannot accidentally bypass
    # the complete-reference check when adding another selector site.
    if sum(len(v) for v in expected.values()) != len(SELECTOR_REFERENCES):
        raise BuildAbortedError("selector inventory/reference count mismatch")
    return changed


def build_candidate(original: bytes) -> tuple[bytes, dict[str, Any]]:
    """Return ``(candidate_bytes, report)`` without mutating ``original``."""

    verify_original(original)
    old_table = _read_old_table(original)
    expected_refs = _check_selector_references(original)
    additions = b"".join(_research_row(building) for building in SHOP_BUILDINGS)
    payload = old_table[:-2] + additions + old_table[-2:]
    geometry = _new_section_geometry(original, len(payload))
    out = bytearray(original)

    pe_offset, count, optional, _table, _optional_size = _section_table(out)
    header = geometry["header"]
    if any(out[header : header + 40]):
        raise BuildAbortedError("new section header slot is not zero-filled")
    # Add a read-only initialized-data section.  The selector only reads this
    # table; no executable permission is needed.
    out[header : header + 8] = b".shopai\0"
    struct.pack_into("<IIII", out, header + 8, geometry["virtual_size"], geometry["virtual_address"], geometry["raw_size"], geometry["raw_pointer"])
    struct.pack_into("<I", out, header + 36, 0x40000040)
    struct.pack_into("<H", out, pe_offset + 6, count + 1)
    struct.pack_into("<I", out, optional + 56, geometry["size_of_image"])
    # IMAGE_OPTIONAL_HEADER.SizeOfInitializedData is the aggregate raw size
    # of initialized-data sections.  Keep the pinned value's deliberately
    # nonstandard baseline and account for this new section, as the PE32
    # section-addition contract requires.
    struct.pack_into(
        "<I", out, optional + 8, ORIGINAL_SIZE_OF_INITIALIZED_DATA + geometry["raw_size"]
    )
    if geometry["raw_pointer"] > len(out):
        out.extend(b"\0" * (geometry["raw_pointer"] - len(out)))
    out.extend(payload)
    out.extend(b"\0" * (geometry["raw_size"] - len(payload)))
    changed_refs = _patch_selector_refs(out, geometry, expected_refs)
    candidate = bytes(out)
    report: dict[str, Any] = {
        "version": "esl2608-ai-shop-open-v1",
        "original_sha256": ORIGINAL_SHA256,
        "candidate_sha256": hashlib.sha256(candidate).hexdigest(),
        "original_size": len(original),
        "candidate_size": len(candidate),
        "old_table_va": f"0x{OLD_TABLE_VA:08x}",
        "old_table_file_offset": f"0x{OLD_TABLE_FILE_OFFSET:08x}",
        "old_table_sha256": TABLE_SHA256,
        "old_row_count": OLD_ROW_COUNT,
        "new_row_count": OLD_ROW_COUNT + len(SHOP_BUILDINGS),
        "table_stride": TABLE_STRIDE,
        "added_rows": [
            {"building": building, "research_rid": SHOP_RESEARCH_RID}
            for building in SHOP_BUILDINGS
        ],
        "new_section": {
            "name": ".shopai",
            "va": f"0x{IMAGE_BASE + geometry['virtual_address']:08x}",
            "rva": f"0x{geometry['virtual_address']:08x}",
            "virtual_size": geometry["virtual_size"],
            "raw_offset": f"0x{geometry['raw_pointer']:08x}",
            "raw_size": geometry["raw_size"],
        },
        "selector_fixups": changed_refs,
        "runtime_status": "static-only; game/Wine not launched",
    }
    return candidate, report


def restore_candidate(candidate: bytes) -> bytes:
    """Restore a candidate produced by :func:`build_candidate` exactly."""

    sections = _sections(candidate)
    matches = [section for section in sections if section["name"] == b".shopai"]
    if len(matches) != 1:
        raise ValueError("candidate must contain exactly one .shopai section")
    section = matches[0]
    if int(section["raw_pointer"]) != ORIGINAL_FILE_SIZE:
        raise ValueError("unexpected .shopai raw placement")
    if int(section["raw_pointer"]) + int(section["raw_size"]) != len(candidate):
        raise ValueError("candidate has unexpected trailing data")
    payload = candidate[int(section["raw_pointer"]) :]
    expected_additions = b"".join(_research_row(building) for building in SHOP_BUILDINGS)
    expected_payload_len = OLD_TABLE_LEN - 2 + len(expected_additions) + 2
    if int(section["virtual_size"]) != expected_payload_len:
        raise ValueError("candidate .shopai virtual size is not canonical")
    if int(section["raw_size"]) != _align(expected_payload_len, FILE_ALIGNMENT):
        raise ValueError("candidate .shopai raw size is not canonical")
    if int(section["characteristics"]) != 0x40000040:
        raise ValueError("candidate .shopai characteristics are not canonical")
    existing_sections = [item for item in sections if item["name"] != b".shopai"]
    section_alignment = _u32(candidate, _section_table(candidate)[2] + 32)
    expected_rva = _align(
        max(
            int(item["virtual_address"])
            + max(int(item["virtual_size"]), int(item["raw_size"]))
            for item in existing_sections
        ),
        section_alignment,
    )
    if int(section["virtual_address"]) != expected_rva:
        raise ValueError("candidate .shopai RVA is not canonical")
    _pe, _count, optional, _table, _size = _section_table(candidate)
    expected_image_size = _align(expected_rva + expected_payload_len, section_alignment)
    if _u32(candidate, optional + 56) != expected_image_size:
        raise ValueError("candidate SizeOfImage is not canonical")
    if _u32(candidate, optional + 8) != ORIGINAL_SIZE_OF_INITIALIZED_DATA + int(section["raw_size"]):
        raise ValueError("candidate SizeOfInitializedData is not canonical")
    if payload[: OLD_ROW_COUNT * TABLE_STRIDE] != candidate[OLD_TABLE_FILE_OFFSET : OLD_TABLE_FILE_OFFSET + OLD_ROW_COUNT * TABLE_STRIDE]:
        raise ValueError("candidate table prefix does not match preserved original rows")
    expected_payload = candidate[OLD_TABLE_FILE_OFFSET : OLD_TABLE_FILE_OFFSET + OLD_TABLE_LEN - 2] + expected_additions + b"\xfe\xff"
    if payload[: len(expected_payload)] != expected_payload:
        raise ValueError("candidate .shopai payload is not this patch's table")
    if payload[len(expected_payload) :] != b"\0" * (len(payload) - len(expected_payload)):
        raise ValueError("candidate .shopai padding is not canonical")

    out = bytearray(candidate[:ORIGINAL_FILE_SIZE])
    pe_offset, count, optional, table, _size = _section_table(out)
    if count != 7:
        raise ValueError(f"unexpected candidate section count: {count}")
    # Restore all selector immediates to their pinned old values and remove
    # exactly the section header that this builder added.
    for ref in SELECTOR_REFERENCES:
        off = _va_to_file_offset(out, ref.va, len(ref.old_bytes))
        if out[off : off + len(ref.old_bytes)] != ref.old_bytes[: ref.immediate_offset] + struct.pack("<I", IMAGE_BASE + int(section["virtual_address"]) + ref.table_offset) + ref.old_bytes[ref.immediate_offset + 4 :]:
            raise ValueError(f"candidate selector bytes mismatch at {ref.va:#x}")
        out[off : off + len(ref.old_bytes)] = ref.old_bytes
    struct.pack_into("<H", out, pe_offset + 6, count - 1)
    struct.pack_into("<I", out, optional + 56, ORIGINAL_SIZE_OF_IMAGE)
    struct.pack_into("<I", out, optional + 8, ORIGINAL_SIZE_OF_INITIALIZED_DATA)
    out[table + (count - 1) * 40 : table + count * 40] = b"\0" * 40
    restored = bytes(out)
    verify_original(restored)
    return restored


def write_candidate(original_path: Path, destination: Path) -> dict[str, Any]:
    """Read a pinned source and create a new candidate without overwriting."""

    if destination.resolve() == original_path.resolve():
        raise ValueError("refusing to overwrite the 2608 source")
    if destination.exists():
        raise FileExistsError(f"refusing to overwrite existing candidate: {destination}")
    original = original_path.read_bytes()
    candidate, report = build_candidate(original)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb") as handle:
        handle.write(candidate)
    report_path = destination.with_suffix(destination.suffix + ".json")
    with report_path.open("x", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    report = write_candidate(args.original, args.destination)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
