#!/usr/bin/env python3
"""G2 base-preserving, non-uniform tail-storage layout mapper.

Pure geometry.  Given a candidate slot capacity N, computes a piecewise-linear
address map for the six pinned N=1200 storage regions (unit_pool, unit
existence/age arrays, category slot lists A/B with their trailing WORD
counts, active_slot_list with its trailing WORD count) and the fixed-size
foreign blocks and `.rsrc` section that sit between/above them in the
original `.data` BSS tail.  `unit_pool` is the lowest region, so its base
never moves (`cumulative_insert_below(unit_pool.base) == 0`) -- that is the
"base-preserving" property this module is named for.

This module does not perform code operand fixups, does not build a runnable
candidate EXE, and does not launch anything.  `build_layout_artifact` and
`write_layout_artifact` produce a private, non-launchable PE-layout artifact
(header/section-table geometry only) for record-keeping; the accessor code
inventory that would need to be patched to actually run the game against a
different capacity lives in the frozen `offline_storage_v1` module and is out
of scope here.

Ground facts and their provenance (do not re-derive; see
docs/work/active/G2_BASE_PRESERVING_STORAGE_OPUS_PLAN_20260918.md and
docs/history/laps/20260918_lap381_middle_g2_c1_h1_closed.md):

- The six region base addresses and element sizes below are read from
  `tools/g2_relocation_manifest_evidence.json` / the lap380 structural
  table, cross-checked byte-for-byte against the pinned original EXE by
  `docs/history/laps/probes/20260918_lap380_middle_g2_tail_layout_facts_probe.py`.
- catA/catB/active_slot_list each end in a live WORD counter that occupies
  the two bytes immediately after the array (lap381 C1: WORD, not DWORD, no
  overlap).  This module folds that counter into the region's span so the
  region's own new/old end is the true next byte after the region.
- The `0x89A388` gap is an 8x200 WORD matrix (H1, lap381: shape confirmed,
  semantics UNKNOWN) -- it is treated as a plain foreign block: fixed size,
  address only shifts by cumulative growth below it.
- The whole tail lives in `.data` BSS (raw_end VA `0x4F9000`); the only
  section above the tail is `.rsrc`.  Expanding the six regions only grows
  `.data`'s VirtualSize -- no raw file bytes move.  `.rsrc`'s raw pointer
  and raw size are therefore invariant; only its VirtualAddress (and the
  resource directory's RVA, and the 9 payload `OffsetToData` RVAs inside the
  unmoved raw resource data) shift.
"""

from __future__ import annotations

import argparse
import hashlib
import struct
from dataclasses import dataclass
from pathlib import Path

ORIGINAL_SHA256 = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"
IMAGE_BASE = 0x400000
STOCK_CAPACITY = 1200
SECTION_ALIGNMENT = 0x1000

# `4001`/`9601`/`9904` are engineering probe values only (lap379/lap380
# history) -- never a default capacity.  Callers supply N explicitly.
ENGINEERING_TEST_CAPACITIES = (4001, 9601, 9904)

# `.rsrc`'s pinned N=1200 geometry (probe-verified: RVA/size match datadir[2]
# exactly, raw pointer/size come from the section header).
RSRC_BASE_VA = IMAGE_BASE + 0x00C8C000
RSRC_SIZE = 0x20F0
RSRC_RAW_POINTER = 0x000F9000

# Offsets, local to `.rsrc`'s raw bytes, of the 4-byte OffsetToData field of
# each IMAGE_RESOURCE_DATA_ENTRY leaf.  Independently re-derived by walking
# the resource directory tree of the pinned original EXE (9 leaves: icon
# group/icon RT_ICON x4, RT_DIALOG x2, RT_STRING, RT_GROUP_ICON, RT_VERSION
# by directory ID; only the byte offsets matter here, not the resource
# semantics).
PAYLOAD_ENTRY_OFFSETS = (
    0x1A8,
    0x1B8,
    0x1C8,
    0x1D8,
    0x1E8,
    0x1F8,
    0x208,
    0x218,
    0x228,
)

# The bulk save/load block's pinned N=1200 length: the immediate operand
# pushed at save site `0x440F02` (length arg to the write call) and read at
# load site `0x4412DC` (`fread` length). Ground fact, not inferred -- see
# `bulk_state_base` (the same block's start) and lap385's acceptance record.
BULK_OLD_LENGTH = 0x000E397C

# The pinned 8-PlayerStruct array: base `0x956770`, unchanged stride `0x3ABC`,
# unchanged element count 8 (Astra 2026-09-18 major-branch decision --
# `g2_capacity/20260918_post_layout_major_decision.json` -- "PlayerStruct
# array preserves eight members and stride 0x3ABC"). It sits entirely inside
# `gap_after_category_slot_list_b`, a size-invariant foreign block, so its
# own span never scales with capacity; only its base address shifts.
PLAYER_STRUCT_BASE = 0x00956770
PLAYER_STRUCT_STRIDE = 0x00003ABC
PLAYER_STRUCT_COUNT = 8


@dataclass(frozen=True)
class RegionSpec:
    name: str
    base: int
    elem_size: int
    count_bytes: int  # 0, or 2 for a trailing live WORD counter

    def span(self, capacity: int) -> int:
        return self.elem_size * capacity + self.count_bytes


# Six pinned N=1200 regions, in ascending address order.
REGIONS: tuple[RegionSpec, ...] = (
    RegionSpec("unit_pool", 0x0066B790, 0x758, 0),
    RegionSpec("unit_existence", 0x008990C8, 2, 0),
    RegionSpec("unit_age", 0x00899A28, 2, 0),
    RegionSpec("category_slot_list_a", 0x0089B008, 4, 2),
    RegionSpec("category_slot_list_b", 0x0089C2CA, 4, 2),
    RegionSpec("active_slot_list", 0x00974FA8, 2, 2),
)


def _align(value: int, boundary: int) -> int:
    return (value + boundary - 1) // boundary * boundary


@dataclass(frozen=True)
class RegionLayout:
    name: str
    old_start: int
    old_end: int
    new_start: int
    new_end: int
    delta: int  # array span growth (array_new_span - array_old_span) -- NOT an address shift
    elem_size: int
    array_old_span: int
    array_new_span: int
    count_bytes: int


@dataclass(frozen=True)
class ForeignLayout:
    name: str
    old_start: int
    old_end: int
    new_start: int
    new_end: int
    delta: int  # address shift: new_start - old_start (cumulative insertion below this block)


@dataclass(frozen=True)
class LayoutResult:
    capacity: int
    regions: tuple[RegionLayout, ...]
    foreign_blocks: tuple[ForeignLayout, ...]
    size_of_image: int

    def entries_in_address_order(self) -> tuple[RegionLayout | ForeignLayout, ...]:
        combined: list[RegionLayout | ForeignLayout] = [*self.regions, *self.foreign_blocks]
        combined.sort(key=lambda e: e.old_start)
        return tuple(combined)

    @property
    def bulk_state_base(self) -> int:
        """The `0x892410` (N=1200) triple alias, derived -- never a hardcoded constant.

        This is `unit_pool.new_end` (`regions[0].new_end`), which at the pinned
        N=1200 baseline is simultaneously:

        1. `unit_pool`'s half-open-interval end (`unit_pool.base + 0x758*N`).
        2. The bulk save block's start -- the immediate operand pushed at the
           save site `0x440F02` (source) and the `fread` destination at the
           load site `0x4412DC`.
        3. The live game-state base -- the start of the region the running
           game treats as the live (non-bulk) simulation state.

        Not modeled here: this address is also the start of a *separate*,
        fixed-length bulk block `[0x892410, +0xE397C)` that folds the
        existence/age/category-A/category-B/active_slot_list regions into one
        contiguous blob distinct from `unit_pool` (which sits below the bulk
        block, not inside it). Expanding capacity shifts this address by
        `0x758*(N-1200)` (this module's `unit_pool` growth) *and* separately
        inflates the bulk blob's own interior by `14*(N-1200)` bytes -- both
        deltas are hardcoded push immediates in the original binary, and
        neither is computed or fixed up by this module (lap385 measurement:
        N=4001 needs a new bulk start of `0xD97DE8` and a new bulk length of
        `0xED2AA`; see the plan doc and lap385 middle acceptance record for
        provenance).
        """
        return self.regions[0].new_end

    @property
    def bulk_length(self) -> int:
        """The bulk save/load block's total length for this capacity.

        `BULK_OLD_LENGTH` (the pinned N=1200 length, `0xE397C`) grown by
        exactly the five regions folded *inside* the blob --
        `unit_existence`, `unit_age`, `category_slot_list_a`,
        `category_slot_list_b`, `active_slot_list` (`regions[1:]`).
        `unit_pool` (`regions[0]`) is excluded: it sits below the blob, not
        inside it, and already only shifts `bulk_state_base` itself.

        This reproduces the Astra 2026-09-18 major-branch decision's pinned
        equation `newBULKlength = 0xE397C + 14*(N-1200)` without hardcoding
        `14`: `sum(elem_size for elem_size in (2, 2, 4, 4, 2)) == 14` falls
        out of the same `REGIONS` table `bulk_state_base` already uses.
        Still not modeled: the length/address immediates this describes are
        hardcoded pushes in the original binary: this module derives the
        *value*, it does not fix up the executable.
        """
        return BULK_OLD_LENGTH + sum(region.delta for region in self.regions[1:])

    @property
    def bulk_end(self) -> int:
        """The bulk block's exclusive end address: `bulk_state_base + bulk_length`."""
        return self.bulk_state_base + self.bulk_length


def _chain() -> list[tuple[str, RegionSpec | tuple[str, int, int]]]:
    """Ascending-address chain of ("region", RegionSpec) and ("foreign", (name, base, size))
    at the pinned N=1200 baseline.  Foreign gaps are derived, not hardcoded: whatever
    space is left between one fixed point and the next becomes an implicit foreign
    block, so a transcription error in a gap size cannot silently diverge from the
    region base addresses that are the actual pinned facts.
    """
    items: list[tuple[str, RegionSpec | tuple[str, int, int]]] = []
    for i, region in enumerate(REGIONS):
        items.append(("region", region))
        region_end = region.base + region.span(STOCK_CAPACITY)
        next_base = REGIONS[i + 1].base if i + 1 < len(REGIONS) else RSRC_BASE_VA
        gap = next_base - region_end
        if gap < 0:
            raise ValueError(f"pinned regions overlap after {region.name}")
        if gap > 0:
            items.append(("foreign", (f"gap_after_{region.name}", region_end, gap)))
    items.append(("rsrc", ("rsrc", RSRC_BASE_VA, RSRC_SIZE)))
    return items


def layout(n: int) -> LayoutResult:
    """Piecewise-linear layout for slot capacity `n`.  `n` must be supplied by the
    caller; there is no default (contract point 7 -- 4001/9601/9904 are test values
    only, never a module default).
    """
    if n < STOCK_CAPACITY:
        raise ValueError(
            f"capacity must be >= STOCK_CAPACITY ({STOCK_CAPACITY}); shrinking below the pinned "
            "N=1200 baseline is not supported -- a discarded slot's address would silently map "
            "outside its own region (contract point 3)"
        )

    regions: list[RegionLayout] = []
    foreign_blocks: list[ForeignLayout] = []
    running_delta = 0
    for kind, item in _chain():
        if kind == "region":
            spec = item
            assert isinstance(spec, RegionSpec)
            old_span = spec.span(STOCK_CAPACITY)
            new_span = spec.span(n)
            new_start = spec.base + running_delta
            regions.append(
                RegionLayout(
                    name=spec.name,
                    old_start=spec.base,
                    old_end=spec.base + old_span,
                    new_start=new_start,
                    new_end=new_start + new_span,
                    delta=new_span - old_span,
                    elem_size=spec.elem_size,
                    array_old_span=spec.elem_size * STOCK_CAPACITY,
                    array_new_span=spec.elem_size * n,
                    count_bytes=spec.count_bytes,
                )
            )
            running_delta += new_span - old_span
        elif kind == "foreign":
            name, base, size = item  # type: ignore[misc]
            new_start = base + running_delta
            foreign_blocks.append(
                ForeignLayout(
                    name=name,
                    old_start=base,
                    old_end=base + size,
                    new_start=new_start,
                    new_end=new_start + size,
                    delta=new_start - base,
                )
            )
        else:  # rsrc: same shift as any foreign block, but its new base must also
            # satisfy SectionAlignment -- it is a real PE section start, not just an
            # address inside one.
            name, base, size = item  # type: ignore[misc]
            raw_new_start = base + running_delta
            new_start = _align(raw_new_start, SECTION_ALIGNMENT)
            foreign_blocks.append(
                ForeignLayout(
                    name=name,
                    old_start=base,
                    old_end=base + size,
                    new_start=new_start,
                    new_end=new_start + size,
                    delta=new_start - base,
                )
            )

    rsrc = foreign_blocks[-1]
    if rsrc.name != "rsrc":
        raise ValueError("internal chain-ordering invariant violated")
    size_of_image = _align((rsrc.new_end - IMAGE_BASE), SECTION_ALIGNMENT)
    if size_of_image >= 2**32 or rsrc.new_end >= 2**32:
        raise OverflowError("layout exceeds 32-bit address space")

    return LayoutResult(
        capacity=n,
        regions=tuple(regions),
        foreign_blocks=tuple(foreign_blocks),
        size_of_image=size_of_image,
    )


@dataclass(frozen=True)
class MappedAddress:
    kind: str  # "region" | "foreign" | "unmappable"
    old_va: int
    new_va: int | None
    block_name: str | None


def map_va(old_va: int, n: int) -> MappedAddress:
    """Map a VA from the pinned N=1200 image into the layout for capacity `n`.

    Returns exactly one of three kinds -- never silently identity/zero for an
    address this module has no basis to map (contract point 3):

    - "region": inside one of the six storage regions (array part or trailing
      count part); `new_va` is populated.
    - "foreign": inside a size-invariant foreign block (a gap, the H1 matrix,
      or `.rsrc`); `new_va` is populated.
    - "unmappable": outside every tracked block (e.g. below `unit_pool`, or
      past the end of `.rsrc`); `new_va` is `None`.
    """
    result = layout(n)
    for entry in result.entries_in_address_order():
        if not (entry.old_start <= old_va < entry.old_end):
            continue
        if isinstance(entry, RegionLayout):
            local = old_va - entry.old_start
            if local < entry.array_old_span:
                new_va = entry.new_start + local
            else:
                count_local = local - entry.array_old_span
                new_va = entry.new_start + entry.array_new_span + count_local
            return MappedAddress("region", old_va, new_va, entry.name)
        local = old_va - entry.old_start
        return MappedAddress("foreign", old_va, entry.new_start + local, entry.name)
    return MappedAddress("unmappable", old_va, None, None)


def mapped_offset(old_base_va: int, old_field_va: int, n: int) -> int:
    """`map_va(field) - map_va(base)` for capacity `n`.

    The only correct way to get a field's offset from a base address after
    remapping. Never reuse the N=1200 `old_field_va - old_base_va`
    difference directly for a *derived* offset: the tail's regions grow at
    different `(N-1200)` rates, so two addresses a fixed distance apart at
    N=1200 are only guaranteed to stay that distance apart if both fall
    inside the same size-invariant (foreign) block or the same untouched
    part of a region -- this function makes that an explicit two-lookup
    computation instead of an assumption.
    """
    base_mapped = map_va(old_base_va, n)
    field_mapped = map_va(old_field_va, n)
    if base_mapped.new_va is None or field_mapped.new_va is None:
        raise ValueError("mapped_offset: base or field address is unmappable at this capacity")
    return field_mapped.new_va - base_mapped.new_va


@dataclass(frozen=True)
class PlayerStructLayout:
    new_base: int
    new_end: int
    stride: int
    count: int


def player_struct_layout(n: int) -> PlayerStructLayout:
    """Map the pinned 8-PlayerStruct array into the layout for capacity `n`.

    Base `PLAYER_STRUCT_BASE`, stride `PLAYER_STRUCT_STRIDE`, count
    `PLAYER_STRUCT_COUNT` are all pinned and unchanged by capacity (Astra
    2026-09-18: "PlayerStruct array preserves eight members and stride
    0x3ABC"). Only the base address shifts, because the array sits entirely
    inside `gap_after_category_slot_list_b`, a size-invariant foreign block.

    `new_end` is computed via `mapped_offset` against the array's last byte
    (an exclusive-end probe), not by re-adding the pinned N=1200 span to
    `new_base` -- that would be exactly the identity-offset assumption
    `mapped_offset` exists to avoid. Both endpoints are required to land in
    the *same* foreign block; a straddle means the ground facts above are
    stale and this must not silently guess a span.
    """
    old_end = PLAYER_STRUCT_BASE + PLAYER_STRUCT_COUNT * PLAYER_STRUCT_STRIDE
    base_mapped = map_va(PLAYER_STRUCT_BASE, n)
    last_byte_mapped = map_va(old_end - 1, n)
    if base_mapped.kind != "foreign" or last_byte_mapped.kind != "foreign":
        raise ValueError("PlayerStruct no longer maps entirely inside a tracked foreign block")
    if base_mapped.block_name != last_byte_mapped.block_name:
        raise ValueError("PlayerStruct straddles two tail blocks; ground facts are stale")
    new_base = base_mapped.new_va
    assert new_base is not None
    new_end = new_base + mapped_offset(PLAYER_STRUCT_BASE, old_end - 1, n) + 1
    return PlayerStructLayout(
        new_base=new_base,
        new_end=new_end,
        stride=PLAYER_STRUCT_STRIDE,
        count=PLAYER_STRUCT_COUNT,
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
    """Apply the §3.6 PE geometry for capacity `n` to a copy of `original`.

    Only header/section-table fields and the 9 pinned resource payload RVAs
    change.  No section's raw bytes move (the whole tail is BSS; `.rsrc`'s
    raw pointer/size are invariant), so this never touches code, never does
    an operand fixup, and is not a runnable candidate: none of the ~130
    frozen accessor instructions in `offline_storage_v1` know about the new
    addresses this produces.  `original` is read, never written.
    """
    verify_original(original)
    result = layout(n)
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

    rsrc_layout = result.foreign_blocks[-1]
    if rsrc_layout.name != "rsrc":
        raise ValueError("internal layout-ordering invariant violated")
    rsrc_delta = rsrc_layout.new_start - rsrc_layout.old_start
    new_rsrc_rva = rsrc_layout.new_start - IMAGE_BASE

    _, data_off, data_vsz, data_va, _data_rsz, _data_rp = _read_section(out, section_table, data_idx)
    # Shift .data's declared VirtualSize by the same raw (pre-alignment) growth as
    # everything else below `.rsrc`, so the original's un-covered slack between
    # .data's nominal end and `.rsrc`'s start (linker padding, not a tracked
    # region) is preserved rather than silently squeezed out.  At n=STOCK_CAPACITY
    # total_growth is 0, which is what keeps build_layout_artifact byte-identical
    # to `original` -- the artifact-level half of the N=1200 identity anchor.
    total_growth = sum(region.delta for region in result.regions)
    new_data_vsz = data_vsz + total_growth
    if data_va + new_data_vsz > new_rsrc_rva:
        raise ValueError("computed .data VirtualSize would overlap the new .rsrc RVA")
    struct.pack_into("<I", out, data_off + 8, new_data_vsz)

    _, rsrc_off, _rsrc_vsz, rsrc_va, rsrc_rsz, rsrc_rp = _read_section(out, section_table, rsrc_idx)
    if IMAGE_BASE + rsrc_va != rsrc_layout.old_start:
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
    """Write a private, non-launchable PE-layout artifact and return its SHA256.

    Refuses to write anywhere that looks like it could be picked up as a
    candidate EXE: the destination must use the reserved `.pelayout` suffix,
    must not equal the source path, and must not be named after the pinned
    original executable.
    """
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
