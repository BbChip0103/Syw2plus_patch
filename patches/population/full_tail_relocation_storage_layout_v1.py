#!/usr/bin/env python3
"""Relocate every unit-capacity-dependent array to the PE image tail.

The earlier tail relocation candidate intentionally moved only the UnitStruct
pool plus the existence/age arrays.  That is enough to address and recycle
slots >=1200, but not enough to keep more than 1200 units alive at once: the
two category lists and the global active-slot list still have stock-sized
storage.  This module keeps that proven candidate intact and defines the next
reversible experiment, which relocates all six capacity-dependent regions.

At capacity 1200 the mapping is byte-identical to the original.  At larger
capacities the regions are packed below a page-aligned relocated .rsrc
section.  The three list counters remain trailing WORDs, so their addresses
move by both the region relocation delta and the array-growth delta.
"""

from __future__ import annotations

import hashlib
import struct
from dataclasses import dataclass

from patches.population.base_preserving_storage_layout_v1 import (
    IMAGE_BASE,
    ORIGINAL_SHA256,
    PAYLOAD_ENTRY_OFFSETS,
    REGIONS,
    RSRC_BASE_VA,
    RSRC_SIZE,
    SECTION_ALIGNMENT,
    STOCK_CAPACITY,
    ForeignLayout,
    RegionLayout,
    _align,
)

RELOCATED_REGIONS = REGIONS


@dataclass(frozen=True)
class FullTailLayoutResult:
    capacity: int
    regions: tuple[RegionLayout, ...]
    rsrc: ForeignLayout
    size_of_image: int

    @property
    def relocated(self) -> bool:
        return self.capacity != STOCK_CAPACITY


def layout(n: int) -> FullTailLayoutResult:
    if n < STOCK_CAPACITY:
        raise ValueError(f"capacity must be >= STOCK_CAPACITY ({STOCK_CAPACITY})")

    if n == STOCK_CAPACITY:
        regions = tuple(
            RegionLayout(
                name=spec.name,
                old_start=spec.base,
                old_end=spec.base + spec.span(STOCK_CAPACITY),
                new_start=spec.base,
                new_end=spec.base + spec.span(STOCK_CAPACITY),
                delta=0,
                elem_size=spec.elem_size,
                array_old_span=spec.elem_size * STOCK_CAPACITY,
                array_new_span=spec.elem_size * STOCK_CAPACITY,
                count_bytes=spec.count_bytes,
            )
            for spec in RELOCATED_REGIONS
        )
        rsrc = ForeignLayout(
            name="rsrc",
            old_start=RSRC_BASE_VA,
            old_end=RSRC_BASE_VA + RSRC_SIZE,
            new_start=RSRC_BASE_VA,
            new_end=RSRC_BASE_VA + RSRC_SIZE,
            delta=0,
        )
        return FullTailLayoutResult(
            capacity=n,
            regions=regions,
            rsrc=rsrc,
            size_of_image=_align(rsrc.old_end - IMAGE_BASE, SECTION_ALIGNMENT),
        )

    regions_out: list[RegionLayout] = []
    cursor = RSRC_BASE_VA
    for spec in RELOCATED_REGIONS:
        old_array_span = spec.elem_size * STOCK_CAPACITY
        new_array_span = spec.elem_size * n
        old_span = old_array_span + spec.count_bytes
        new_span = new_array_span + spec.count_bytes
        regions_out.append(
            RegionLayout(
                name=spec.name,
                old_start=spec.base,
                old_end=spec.base + old_span,
                new_start=cursor,
                new_end=cursor + new_span,
                delta=new_span - old_span,
                elem_size=spec.elem_size,
                array_old_span=old_array_span,
                array_new_span=new_array_span,
                count_bytes=spec.count_bytes,
            )
        )
        cursor += new_span

    new_rsrc_start = _align(cursor, SECTION_ALIGNMENT)
    rsrc = ForeignLayout(
        name="rsrc",
        old_start=RSRC_BASE_VA,
        old_end=RSRC_BASE_VA + RSRC_SIZE,
        new_start=new_rsrc_start,
        new_end=new_rsrc_start + RSRC_SIZE,
        delta=new_rsrc_start - RSRC_BASE_VA,
    )
    size_of_image = _align(rsrc.new_end - IMAGE_BASE, SECTION_ALIGNMENT)
    if rsrc.new_end >= 2**32 or size_of_image >= 2**32:
        raise OverflowError("layout exceeds 32-bit address space")
    return FullTailLayoutResult(n, tuple(regions_out), rsrc, size_of_image)


def _read_section(data: bytes, section_table: int, index: int) -> tuple[bytes, int, int, int, int, int]:
    off = section_table + index * 40
    name = data[off : off + 8].rstrip(b"\0")
    vsz, va, rsz, rp = struct.unpack_from("<IIII", data, off + 8)
    return name, off, vsz, va, rsz, rp


def build_layout_artifact(original: bytes, n: int) -> bytes:
    if hashlib.sha256(original).hexdigest() != ORIGINAL_SHA256:
        raise ValueError("original EXE SHA256 mismatch; refusing to build a candidate")
    result = layout(n)
    if not result.relocated:
        return bytes(original)

    out = bytearray(original)
    pe_off = struct.unpack_from("<I", out, 0x3C)[0]
    if out[pe_off : pe_off + 4] != b"PE\0\0":
        raise ValueError("bad PE signature")
    num_sections = struct.unpack_from("<H", out, pe_off + 6)[0]
    opt_header_size = struct.unpack_from("<H", out, pe_off + 20)[0]
    opt = pe_off + 24
    if struct.unpack_from("<H", out, opt)[0] != 0x10B:
        raise ValueError("not a PE32 optional header")
    section_alignment, file_alignment = struct.unpack_from("<II", out, opt + 32)
    if section_alignment != SECTION_ALIGNMENT or file_alignment != SECTION_ALIGNMENT:
        raise ValueError("unsupported section/file alignment")
    section_table = pe_off + 24 + opt_header_size

    data_idx = rsrc_idx = None
    for index in range(num_sections):
        name, *_ = _read_section(out, section_table, index)
        if name == b".data":
            data_idx = index
        elif name == b".rsrc":
            rsrc_idx = index
    if data_idx is None or rsrc_idx is None:
        raise ValueError("expected .data/.rsrc sections not found")

    new_rsrc_rva = result.rsrc.new_start - IMAGE_BASE
    rsrc_delta = result.rsrc.delta
    _, data_off, _data_vsz, data_va, _data_rsz, _data_rp = _read_section(
        out, section_table, data_idx
    )
    new_data_vsz = result.regions[-1].new_end - (IMAGE_BASE + data_va)
    if data_va + new_data_vsz > new_rsrc_rva:
        raise ValueError("computed .data VirtualSize would overlap the new .rsrc RVA")
    struct.pack_into("<I", out, data_off + 8, new_data_vsz)

    _, rsrc_off, _rsrc_vsz, rsrc_va, _rsrc_rsz, rsrc_rp = _read_section(
        out, section_table, rsrc_idx
    )
    if IMAGE_BASE + rsrc_va != result.rsrc.old_start:
        raise ValueError(".rsrc section VA does not match the pinned rsrc base")
    struct.pack_into("<I", out, rsrc_off + 12, new_rsrc_rva)

    resource_dir_offset = opt + 96 + 2 * 8
    directory_rva, _directory_size = struct.unpack_from("<II", out, resource_dir_offset)
    if directory_rva != rsrc_va:
        raise ValueError("resource data directory does not alias the .rsrc section start")
    struct.pack_into("<I", out, resource_dir_offset, new_rsrc_rva)
    struct.pack_into("<I", out, opt + 56, result.size_of_image)

    for local_offset in PAYLOAD_ENTRY_OFFSETS:
        field_off = rsrc_rp + local_offset
        old_value = struct.unpack_from("<I", out, field_off)[0]
        struct.pack_into("<I", out, field_off, old_value + rsrc_delta)

    if len(out) != len(original):
        raise ValueError("layout artifact changed file length")
    return bytes(out)
