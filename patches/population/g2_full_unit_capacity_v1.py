#!/usr/bin/env python3
"""Runnable experimental candidate with all six unit-capacity arrays relocated."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import capstone
import pefile

from patches.population.base_preserving_storage_layout_v1 import REGIONS, STOCK_CAPACITY
from patches.population.full_tail_relocation_storage_layout_v1 import (
    ORIGINAL_SHA256,
    build_layout_artifact,
    layout,
)
from patches.population.g2_unit_pool_expansion_v1 import (
    B2_EXCLUDED_VAS,
    BuildAbortedError,
    FixupSite,
    _classify_imm_operand,
    _decode,
    _patch_literal,
    _region_sites,
    _text_section,
    _va_to_file_offset,
)

IMAGE_BASE = 0x00400000

# FUN_00442FE0 removes an active slot by copying the last list element from
# ``active_base + active_count*2 - 2``.  The compiler encoded that expression
# with the displacement ``active_base - 2`` at two sites, so a half-open scan
# beginning at active_base cannot discover them.  They are explicit aliases,
# not the unrelated DWORD immediately before the list at 0x00974FA4.
ACTIVE_LAST_ELEMENT_ALIAS_SITES = (0x00443075, 0x0044308C)
ACTIVE_LAST_ELEMENT_OLD_DISPLACEMENT = 0x00974FA6

# The category swap-removal helpers receive the stock bulk-state base
# (0x892410) in ECX and address both category arrays through small relative
# displacements.  Absolute-address scanning cannot discover these operands.
# Keep the exact instruction inventory explicit, including the compiler's
# ``base - 4 + count*4`` aliases used to load the final DWORD.
CATEGORY_BULK_BASE = 0x00892410
CATEGORY_A_BULK_SITES = {
    0x004A3622: "count",
    0x004A3642: "base",
    0x004A364A: "base",
    0x004A3667: "last",
    0x004A366E: "base",
    0x004A3675: "count",
}
CATEGORY_B_BULK_SITES = {
    # The stock instruction at 0x004A3692 loads category-A's count even
    # though the rest of FUN_004A3690 searches, swaps and decrements the
    # category-B list.  At expanded saturation this prevents B removal,
    # lets a later B insertion write B[capacity] over B_count/active[0], and
    # was observed as full-id 0x0003xxxx becoming active slot 3.  Point the
    # helper's loop/last-element index at its own B count.
    0x004A3692: "self_count",
    0x004A36A0: "count",
    0x004A36BA: "base",
    0x004A36C2: "base",
    0x004A36DF: "last",
    0x004A36E6: "base",
    0x004A36ED: "count",
}



# W19 Step 2 (docs/work/active/G2_IMM_FIXUP_FALSE_POSITIVE_REPAIR_LAP439.md
# §2 point 5): the `_list_region_sites` imm branch needs the same
# classification-oracle guard as `_region_sites`. Keyed by value, not VA:
# every imm site this scanner currently finds for category_slot_list_a/b
# (0) and active_slot_list (72, all `mov reg, 0x974fa8` -- the array's own
# base) shares one of a small number of distinct values, so a value-keyed
# table both covers all 72 sites and still aborts on any future novel
# value instead of silently accepting it.
LIST_REGION_IMM_VALUE_CLASSIFICATION: dict[int, str] = {
    0x00974FA8: "ADDRESS",  # active_slot_list base, loaded identically at 72 call sites
}


def _bulk_category_sites(region_index: int, n: int) -> list[FixupSite]:
    spec = REGIONS[region_index]
    mapped = layout(n).regions[region_index]
    inventory = CATEGORY_A_BULK_SITES if region_index == 3 else CATEGORY_B_BULK_SITES
    if n == STOCK_CAPACITY and region_index == 4:
        inventory = {
            va: kind for va, kind in inventory.items() if kind != "self_count"
        }
    old_count = spec.base + spec.elem_size * STOCK_CAPACITY
    new_count = mapped.new_start + spec.elem_size * n
    category_a = REGIONS[3]
    old_category_a_count = category_a.base + category_a.elem_size * STOCK_CAPACITY
    values = {
        "base": (spec.base - CATEGORY_BULK_BASE, mapped.new_start - CATEGORY_BULK_BASE),
        "last": (spec.base - 4 - CATEGORY_BULK_BASE, mapped.new_start - 4 - CATEGORY_BULK_BASE),
        "count": (old_count - CATEGORY_BULK_BASE, new_count - CATEGORY_BULK_BASE),
        "self_count": (
            old_category_a_count - CATEGORY_BULK_BASE,
            new_count - CATEGORY_BULK_BASE,
        ),
    }
    return [
        FixupSite(va, spec.name, "disp", *values[kind])
        for va, kind in inventory.items()
    ]


def verify_original(data: bytes) -> None:
    if hashlib.sha256(data).hexdigest() != ORIGINAL_SHA256:
        raise ValueError("original EXE SHA256 mismatch; refusing to build a candidate")


def _list_region_sites(
    insns: list[capstone.CsInsn], region_index: int, n: int
) -> list[FixupSite]:
    spec = REGIONS[region_index]
    mapped = layout(n).regions[region_index]
    old_array_end = spec.base + spec.elem_size * STOCK_CAPACITY
    old_end = old_array_end + spec.count_bytes
    new_count = mapped.new_start + spec.elem_size * n
    sites: list[FixupSite] = []
    for index, insn in enumerate(insns):
        for operand in insn.operands:
            value: int | None = None
            kind = ""
            if operand.type == capstone.x86.X86_OP_MEM:
                value = int(operand.mem.disp) & 0xFFFFFFFF
                kind = "disp"
            elif operand.type == capstone.x86.X86_OP_IMM:
                value = int(operand.imm) & 0xFFFFFFFF
                kind = "imm"
            if value is None or not spec.base <= value < old_end:
                continue
            if kind == "imm":
                # W19 Step 2: same rule as _region_sites, applied here too --
                # keyed by value (not VA) because every current site is the
                # identical `mov reg, spec.base` idiom repeated at 72 call
                # sites for active_slot_list; a coincidental collision with
                # some unrelated value would be unclassified and abort the
                # build instead of silently mis-relocating it.
                verdict = _classify_imm_operand(
                    insns, index, insn, value, spec.base, spec.elem_size,
                    LIST_REGION_IMM_VALUE_CLASSIFICATION, value,
                )
                if verdict == "NOT_ADDRESS":
                    continue
            if value < old_array_end:
                new_value = mapped.new_start + (value - spec.base)
            else:
                new_value = new_count + (value - old_array_end)
            sites.append(FixupSite(insn.address, spec.name, kind, value, new_value))
    return sites


def collect_fixup_sites(original: bytes, n: int) -> dict[str, list[FixupSite]]:
    """Note (W19 §2 point 5): the REGIONS[:3] branch below calls the *same*
    `_region_sites` function `g2_unit_pool_expansion_v1.collect_fixup_sites`
    calls -- not a second, independently-written scanner. This was never a
    real cross-check for those three regions: a bug in `_region_sites`
    (e.g. the lap439 imm false positive) reproduces identically here rather
    than being caught by disagreement. The actual independent verification
    for pool/existence/age is `IMM_SITE_CLASSIFICATION`, produced by hand
    from the pinned original's disassembly, not derived from this code.
    """
    pe = pefile.PE(data=original, fast_load=True)
    try:
        text_va, _text_raw, text_bytes = _text_section(pe)
    finally:
        pe.close()
    insns = _decode(text_bytes, text_va)
    result = layout(n)

    sites: dict[str, list[FixupSite]] = {}
    for index, spec in enumerate(REGIONS[:3]):
        old_end = spec.base + spec.elem_size * STOCK_CAPACITY
        scanned = _region_sites(insns, spec.name, spec.base, old_end, spec.elem_size)
        delta = result.regions[index].new_start - spec.base
        sites[spec.name] = [
            FixupSite(site.va, site.region, site.op_kind, site.old_value, site.old_value + delta)
            for site in scanned
        ]
    for index in range(3, 6):
        sites[REGIONS[index].name] = _list_region_sites(insns, index, n)
    sites[REGIONS[3].name].extend(_bulk_category_sites(3, n))
    sites[REGIONS[4].name].extend(_bulk_category_sites(4, n))
    active = result.regions[5]
    sites[REGIONS[5].name].extend(
        FixupSite(
            va,
            REGIONS[5].name,
            "disp",
            ACTIVE_LAST_ELEMENT_OLD_DISPLACEMENT,
            active.new_start - 2,
        )
        for va in ACTIVE_LAST_ELEMENT_ALIAS_SITES
    )
    return sites


def _b2_sites(n: int) -> tuple[dict[str, Any], ...]:
    result = layout(n)
    age = result.regions[2]
    return (
        {
            "va": 0x00442FAC,
            "old_bytes": bytes.fromhex("b92a9a8900"),
            "old_value": 0x00899A2A,
            "new_value": age.new_start + 2,
            "note": "allocator scan start = relocated age base + 2",
        },
        {
            "va": 0x00442FB1,
            "old_bytes": bytes.fromhex("6683b9a0f6ffff00"),
            "old_value": (-STOCK_CAPACITY * 2) & 0xFFFFFFFF,
            "new_value": (-n * 2) & 0xFFFFFFFF,
            "note": "allocator existence-relative displacement = -2N",
        },
        {
            "va": 0x00442FD1,
            "old_bytes": bytes.fromhex("81f988a38900"),
            "old_value": 0x0089A388,
            "new_value": age.new_start + age.array_new_span,
            "note": "allocator scan exclusive end",
        },
        {
            "va": 0x0044317D,
            "old_bytes": bytes.fromhex("81feb0040000"),
            "old_value": STOCK_CAPACITY,
            "new_value": n,
            "note": "destroy-all loop bound",
        },
    )


def build_candidate(original: bytes, n: int = 1250) -> tuple[bytes, dict[str, Any]]:
    verify_original(original)
    if n < STOCK_CAPACITY:
        raise ValueError(f"capacity must be >= {STOCK_CAPACITY}")

    stage_b1 = build_layout_artifact(original, n)
    out = bytearray(stage_b1)
    pe = pefile.PE(data=bytes(out), fast_load=True)
    try:
        b2_applied: list[dict[str, Any]] = []
        for site in _b2_sites(n):
            file_off = _va_to_file_offset(pe, site["va"])
            actual = bytes(out[file_off : file_off + len(site["old_bytes"])])
            if actual != site["old_bytes"]:
                raise BuildAbortedError(
                    f"B-2 site 0x{site['va']:08x}: old bytes mismatch "
                    f"(expected {site['old_bytes'].hex()}, found {actual.hex()})"
                )
            _patch_literal(out, pe, site["va"], site["old_value"], site["new_value"])
            b2_applied.append(
                {
                    "va": f"0x{site['va']:08x}",
                    "old_value": f"0x{site['old_value'] & 0xFFFFFFFF:08x}",
                    "new_value": f"0x{site['new_value'] & 0xFFFFFFFF:08x}",
                    "note": site["note"],
                }
            )

        sites_by_region = collect_fixup_sites(original, n)
        applied_counts: dict[str, int] = {}
        for region, sites in sites_by_region.items():
            count = 0
            for site in sites:
                if site.va in B2_EXCLUDED_VAS:
                    continue
                if site.new_value == site.old_value:
                    continue
                _patch_literal(out, pe, site.va, site.old_value, site.new_value)
                count += 1
            applied_counts[region] = count
    finally:
        pe.close()

    if len(out) != len(original):
        raise BuildAbortedError("candidate changed file length")
    candidate = bytes(out)
    result = layout(n)
    return candidate, {
        "capacity": n,
        "stock_capacity": STOCK_CAPACITY,
        "original_sha256": ORIGINAL_SHA256,
        "candidate_sha256": hashlib.sha256(candidate).hexdigest(),
        "b2_constants": b2_applied,
        "fixup_site_counts": {name: len(value) for name, value in sites_by_region.items()},
        "applied_fixup_counts": applied_counts,
        "imm_classification_source": "IMM_SITE_CLASSIFICATION + LIST_REGION_IMM_VALUE_CLASSIFICATION",
        "regions": {
            region.name: {
                "old_start": f"0x{region.old_start:08x}",
                "new_start": f"0x{region.new_start:08x}",
                "new_end": f"0x{region.new_end:08x}",
            }
            for region in result.regions
        },
    }


def write_candidate(original_path: Path, destination: Path, n: int = 1250) -> dict[str, Any]:
    if destination.resolve() == original_path.resolve():
        raise ValueError("refusing to overwrite the original EXE")
    candidate, report = build_candidate(original_path.read_bytes(), n)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(candidate)
    return report
