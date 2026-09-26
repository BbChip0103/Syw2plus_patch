#!/usr/bin/env python3
"""G2 tail-relocation storage layout mapper (work card W4, lap400 middle).

`base_preserving_storage_layout_v1` grows `unit_pool`/`unit_existence`/
`unit_age` *in place*, cascading a shift onto every foreign block and region
above them (`category_slot_list_a/b`, `active_slot_list`, `PlayerStruct`,
`.rsrc`). lap400's D4 scan showed why that is wrong for these three regions
specifically: at any N > 1200 the grown `unit_pool` footprint physically
overlaps the bulk save/load blob `[0x00892410, 0x00975D8C)` that
`unit_existence`/`unit_age`/`category_slot_list_a/b`/`active_slot_list` are
folded into -- 1,311 `.text` literal sites reference that overlap, none of
which the base-preserving candidate fixed up (see
`docs/history/laps/20260920_lap400_middle_g2_pool_overrun_reject.md`).

This module instead relocates all three arrays, as one combined block, to the
image tail just below `.rsrc` (lap400 D4: exactly one `.text` literal in that
2.18 MB span, a non-address `push` immediate). Every other pinned region and
foreign gap keeps its stock address at *every* N >= STOCK_CAPACITY -- nothing
below `.rsrc` depends on `unit_pool`/`unit_existence`/`unit_age`'s size
anymore, so there is nothing left to cascade. At N == STOCK_CAPACITY this
degenerates to a pure identity map (no relocation, `.rsrc` untouched) --
the required N=1200 regression anchor (work card W4 §4).

Ground facts reused, not re-derived (work card W4 §1):
- `REGIONS[0:3]` (unit_pool/unit_existence/unit_age base + elem_size) and
  `RSRC_BASE_VA`/`RSRC_SIZE`/`PAYLOAD_ENTRY_OFFSETS` come from
  `base_preserving_storage_layout_v1`, the lap380/388 ACCEPTED, closed
  ground-fact source. That module is frozen (lap388 layout-card closure) and
  is not parameterizable with an alternate placement strategy, so the PE
  header patcher below is a small, deliberate duplicate of its procedure
  rather than a modification of frozen code.
- The tail insertion point is `RSRC_BASE_VA` itself (lap400 D4: the 2.18 MB
  virgin span used for the reference scan starts essentially at the current
  `.rsrc` base) -- i.e. the three arrays are inserted exactly where
  `base_preserving_storage_layout_v1` already knows how to insert *a* block
  before `.rsrc`; only the two other regions' contribution to that insertion
  point is removed.
"""

from __future__ import annotations

import argparse
import hashlib
import struct
from dataclasses import dataclass
from pathlib import Path

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

# unit_pool, unit_existence, unit_age -- the only three regions this module
# relocates. The other three `REGIONS` entries (category_slot_list_a/b,
# active_slot_list) are untouched at every capacity; this module does not
# reference them at all.
RELOCATED_REGIONS: tuple = REGIONS[0:3]

# Bulk save/load blob (lap385 pinned): src of save `0x440F02`, dst of load
# `0x4412DC`. Relocating existence/age out of it is *why* save compatibility
# breaks (work card W4 §6) -- not modeled or repaired here.
BULK_BLOB_START = 0x00892410
BULK_BLOB_END = 0x00975D8C


@dataclass(frozen=True)
class TailLayoutResult:
    capacity: int
    regions: tuple[RegionLayout, ...]  # pool, existence, age, in that order
    rsrc: ForeignLayout
    size_of_image: int

    @property
    def relocated(self) -> bool:
        return self.capacity != STOCK_CAPACITY


def layout(n: int) -> TailLayoutResult:
    """Tail-relocation layout for slot capacity `n`.

    At n == STOCK_CAPACITY every region and `.rsrc` map to themselves
    (delta 0) -- the identity anchor. At n > STOCK_CAPACITY, unit_pool,
    unit_existence, unit_age are packed back-to-back starting at
    `RSRC_BASE_VA` (pool first, then existence, then age immediately after
    existence -- the allocator's `[ecx-0x960]`-style adjacency requirement,
    work card W4 §1), and `.rsrc` shifts up by their combined span.
    """
    if n < STOCK_CAPACITY:
        raise ValueError(
            f"capacity must be >= STOCK_CAPACITY ({STOCK_CAPACITY}); shrinking below the pinned "
            "N=1200 baseline is not supported"
        )

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
        size_of_image = _align((rsrc.old_end - IMAGE_BASE), SECTION_ALIGNMENT)
        return TailLayoutResult(capacity=n, regions=regions, rsrc=rsrc, size_of_image=size_of_image)

    regions_out: list[RegionLayout] = []
    cursor = RSRC_BASE_VA
    for spec in RELOCATED_REGIONS:
        old_span = spec.span(STOCK_CAPACITY)
        new_span = spec.span(n)
        new_start = cursor
        regions_out.append(
            RegionLayout(
                name=spec.name,
                old_start=spec.base,
                old_end=spec.base + old_span,
                new_start=new_start,
                new_end=new_start + new_span,
                delta=new_span - old_span,
                elem_size=spec.elem_size,
                array_old_span=old_span,
                array_new_span=new_span,
                count_bytes=spec.count_bytes,
            )
        )
        cursor = new_start + new_span

    raw_rsrc_start = cursor
    new_rsrc_start = _align(raw_rsrc_start, SECTION_ALIGNMENT)
    rsrc = ForeignLayout(
        name="rsrc",
        old_start=RSRC_BASE_VA,
        old_end=RSRC_BASE_VA + RSRC_SIZE,
        new_start=new_rsrc_start,
        new_end=new_rsrc_start + RSRC_SIZE,
        delta=new_rsrc_start - RSRC_BASE_VA,
    )
    if rsrc.new_end >= 2**32:
        raise OverflowError("layout exceeds 32-bit address space")
    size_of_image = _align((rsrc.new_end - IMAGE_BASE), SECTION_ALIGNMENT)
    if size_of_image >= 2**32:
        raise OverflowError("layout exceeds 32-bit address space")

    return TailLayoutResult(
        capacity=n, regions=tuple(regions_out), rsrc=rsrc, size_of_image=size_of_image
    )


def verify_original(data: bytes) -> None:
    if hashlib.sha256(data).hexdigest() != ORIGINAL_SHA256:
        raise ValueError("original EXE SHA256 mismatch; refusing to build a layout artifact")


def _read_section(data: bytes, section_table: int, index: int) -> tuple[bytes, int, int, int, int, int]:
    off = section_table + index * 40
    name = data[off : off + 8].rstrip(b"\0")
    vsz, va, rsz, rp = struct.unpack_from("<IIII", data, off + 8)
    return name, off, vsz, va, rsz, rp


def build_layout_artifact(original: bytes, n: int) -> bytes:
    """Apply the tail-relocation PE geometry for capacity `n` to a copy of
    `original`. Duplicates `base_preserving_storage_layout_v1.build_layout_
    artifact`'s procedure (frozen module, not parameterizable -- see module
    docstring) against this module's own `layout()`.

    Only header/section-table fields and the 9 pinned resource payload RVAs
    change; `.text`'s raw bytes are untouched here (B-2/B-3 code fixups are a
    separate stage, in `g2_unit_pool_expansion_v1`). At n == STOCK_CAPACITY
    this returns bytes identical to `original`.
    """
    verify_original(original)
    result = layout(n)
    out = bytearray(original)

    if not result.relocated:
        return bytes(out)

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
    num_rva_and_sizes = struct.unpack_from("<I", out, opt + 92)[0]
    if num_rva_and_sizes <= 2:
        raise ValueError("resource data directory entry is absent")
    section_table = pe_off + 24 + opt_header_size

    data_idx = rsrc_idx = None
    for i in range(num_sections):
        name, _off, _vsz, _va, _rsz, _rp = _read_section(out, section_table, i)
        if name == b".data":
            data_idx = i
        elif name == b".rsrc":
            rsrc_idx = i
    if data_idx is None or rsrc_idx is None:
        raise ValueError("expected .data/.rsrc sections not found")

    rsrc_delta = result.rsrc.new_start - result.rsrc.old_start
    new_rsrc_rva = result.rsrc.new_start - IMAGE_BASE

    _, data_off, _data_vsz, data_va, _data_rsz, _data_rp = _read_section(out, section_table, data_idx)
    # The relocated block is moved wholesale to the tail, not grown in place:
    # the space `.data` must cover is the *block's absolute extent*
    # (`regions[-1].new_end`), not the sum of per-region growth deltas
    # (lap402 D1 -- `RegionLayout.delta` is array growth, not relocation
    # distance; using it here left slot 10+ of unit_pool and all of
    # unit_existence/unit_age outside every section's mapped range).
    new_data_vsz = result.regions[-1].new_end - (IMAGE_BASE + data_va)
    if data_va + new_data_vsz > new_rsrc_rva:
        raise ValueError("computed .data VirtualSize would overlap the new .rsrc RVA")
    struct.pack_into("<I", out, data_off + 8, new_data_vsz)

    _, rsrc_off, _rsrc_vsz, rsrc_va, rsrc_rsz, rsrc_rp = _read_section(out, section_table, rsrc_idx)
    if IMAGE_BASE + rsrc_va != result.rsrc.old_start:
        raise ValueError(".rsrc section VA does not match the pinned rsrc base")
    struct.pack_into("<I", out, rsrc_off + 12, new_rsrc_rva)

    resource_dir_offset = opt + 96 + 2 * 8
    dir_rva, _dir_size = struct.unpack_from("<II", out, resource_dir_offset)
    if dir_rva != rsrc_va:
        raise ValueError("resource data directory does not alias the .rsrc section start")
    struct.pack_into("<I", out, resource_dir_offset, new_rsrc_rva)

    struct.pack_into("<I", out, opt + 56, result.size_of_image)

    for local_offset in PAYLOAD_ENTRY_OFFSETS:
        field_off = rsrc_rp + local_offset
        old_value = struct.unpack_from("<I", out, field_off)[0]
        struct.pack_into("<I", out, field_off, old_value + rsrc_delta)

    if len(out) != len(original):
        raise ValueError("layout artifact changed file length; no raw bytes should move")
    return bytes(out)


NON_LAUNCHABLE_SUFFIX = ".pelayout"


def write_layout_artifact(original_path: Path, destination: Path, n: int) -> str:
    if destination.suffix != NON_LAUNCHABLE_SUFFIX:
        raise ValueError(f"layout artifact destination must end in {NON_LAUNCHABLE_SUFFIX}")
    if destination.resolve() == original_path.resolve():
        raise ValueError("refusing to overwrite the original EXE")
    if destination.name.lower().replace(NON_LAUNCHABLE_SUFFIX, "") == "syw2plus_original.exe".lower():
        raise ValueError("refusing to shadow the pinned original executable name")
    original = original_path.read_bytes()
    artifact = build_layout_artifact(original, n)
    destination.write_bytes(artifact)
    return hashlib.sha256(artifact).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("capacity", type=int)
    args = parser.parse_args()
    digest = write_layout_artifact(args.original, args.destination, args.capacity)
    print(digest)


if __name__ == "__main__":
    main()
