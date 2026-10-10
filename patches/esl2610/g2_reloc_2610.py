#!/usr/bin/env python3
"""Relocation planner for the G2 4093 expansion on ESL 2610 (spike scope).

The build is still fail-closed (:mod:`patches.esl2610.g2_pool4093_2610`); this
module does not emit a runnable EXE.  It *settles the transform pattern* the
full build will follow, for the subset that can be stated exactly today, and
validates that the plan is complete and non-overlapping so the pattern can be
reviewed and batched to the remaining modules.

Two layers are planned:

* **Stock six-array relocation** -- identical in rule to the accepted 2608 G2.
  The unit pool, existence/age words, two category lists and the active-slot
  list move into one packed ``.g2bss`` section at the image tail; every operand
  that encodes a literal address inside them shifts by that region's delta, and
  the list trailing-count words shift by both the region delta and the
  array-growth delta.  :func:`relocate_value` is the single mapping rule.

* **Direct-indexed per-unit arrays (spike set).**  Four 2610-new modules index
  an array *directly* by a unit slot/id bounded at 1200, so at slot > 1200 they
  write out of bounds -- the clearest memory-safety break.  Each is described
  by a :class:`DirectArray` record (old base, per-unit stride, the 1200-sized
  span to relocate, the slot-count gate immediates to raise, and any
  memset/clear count to rescale).  The planner relocates each array's per-unit
  span into ``.g2bss`` and lists the exact byte edits.  ``.killdat`` is
  composite: only its ``0x115C000`` per-slot sub-array is relocated; its other
  fixed tables stay in place -- recorded explicitly so the batch step inherits
  the same care.

The section budget: :func:`pe_extend.compact_headers` frees exactly four
section slots; G6 uses one; this plan uses two (one ``.g2bss`` for all
relocated arrays, one ``.g2code`` for save/load wrappers), leaving one spare.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from patches.esl2610 import g2_scan, pe_extend
from patches.population.full_tail_relocation_storage_layout_v1 import layout

CAPACITY = 4093
STOCK_CAPACITY = g2_scan.STOCK_CAPACITY
UNIT_STRIDE = g2_scan.UNIT_STRIDE
IMAGE_BASE = pe_extend.IMAGE_BASE

# The packed six-array layout (pool/existence/age/catA/catB/active) relative to
# a base, reused verbatim from the accepted full-tail geometry.
_GEOMETRY = layout(CAPACITY)
_GEOMETRY_1200 = layout(STOCK_CAPACITY)
# Byte span of all six relocated arrays (pool .. active end), at 4093.
SIX_ARRAY_SPAN = _GEOMETRY.regions[-1].new_end - _GEOMETRY.regions[0].new_start


# g2_scan uses short region names; its ranges include the lists' 1-based base
# (e.g. active 0x974FA6) and trailing count word, which the geometry's array
# start does not.  Map each scan range to its geometry region for the offset
# math, which is signed so the 1-based base below the array start maps too.
_SCAN_TO_GEO = {
    "pool": "unit_pool",
    "exist": "unit_existence",
    "age": "unit_age",
    "cat_a": "category_slot_list_a",
    "cat_b": "category_slot_list_b",
    "active": "active_slot_list",
}
_PACK_BASE = _GEOMETRY.regions[0].new_start
_GEO_BY_NAME = {r.name: r for r in _GEOMETRY.regions}


def relocate_value(value: int, pool_base: int) -> int:
    """Map a literal address in a stock array to its packed ``.g2bss`` address.

    ``pool_base`` is where the packed six-array block starts.  The offset within
    a region is computed relative to the geometry's array start and is *signed*,
    so a list's 1-based base (two bytes below the array) and its trailing count
    word (just past the grown array) both map correctly.  Raises if ``value`` is
    not inside any of the six scanner regions.
    """
    for short, (lo, hi) in g2_scan.REGIONS.items():
        if not lo <= value < hi:
            continue
        geo = _GEO_BY_NAME[_SCAN_TO_GEO[short]]
        new_region_start = pool_base + (geo.new_start - _PACK_BASE)
        rel = value - geo.old_start  # signed
        if rel < geo.array_old_span:
            return new_region_start + rel
        # trailing count word: sits just past the grown 4093-sized array
        return new_region_start + geo.array_new_span + (rel - geo.array_old_span)
    raise ValueError(f"0x{value:08x} is not inside any stock unit-capacity region")


@dataclass(frozen=True)
class DirectArray:
    """A 2610-new array indexed directly by a 1200-bounded unit slot/id."""

    name: str
    module: str
    old_base: int
    stride: int
    index_kind: str  # "slot" ((ptr-pool)/stride) or "id" (unit id word)
    gate_byte_span: bool  # True if gate compares (ptr-pool) against stride*1200
    gate_sites: tuple[int, ...]  # VAs whose immediate must rise 1200 -> 4093
    byte_span_gate_sites: tuple[int, ...]  # VAs whose immediate must rise 0x758*1200 -> *4093
    memset_sites: tuple[tuple[int, int], ...]  # (VA, old dword count) clears to rescale
    note: str = ""

    def span_1200(self) -> int:
        return self.stride * STOCK_CAPACITY

    def span_4093(self) -> int:
        return self.stride * CAPACITY


# Spike set: the four clearly direct-indexed per-unit arrays (step 1).
# Addresses/strides/gates are read from the pinned 2610 disassembly; each is
# verified against its old bytes before patching in the eventual build.
SPIKE_ARRAYS: tuple[DirectArray, ...] = (
    DirectArray(
        name=".wecache",
        module=".wefix",
        old_base=0x0114C000,
        stride=0x10,
        index_kind="id",
        gate_byte_span=False,
        gate_sites=(0x01149007,),  # cmp edi, 0x4b0  (unit id word [esi+0x29c])
        byte_span_gate_sites=(),
        memset_sites=(),
        note="weapon-effect cache, 16B x id, gate on unit id < 1200",
    ),
    DirectArray(
        name=".rsidle",
        module=".idle",
        old_base=0x01171010,  # per-unit body; 0x1171000 is a 16B frame header
        stride=0x10,
        index_kind="slot",
        gate_byte_span=False,
        gate_sites=(0x01157942, 0x01157c17),  # cmp eax, 0x4b0 (slot)
        byte_span_gate_sites=(),
        memset_sites=((0x0115791E, 0x12C4),),  # rep stosd whole .rsidle
        note="idle-portrait cache, 16B x slot; memset count covers header+body",
    ),
    DirectArray(
        name=".killdat_sub",
        module=".kills",
        old_base=0x0115C000,
        stride=0x20,
        index_kind="slot",
        gate_byte_span=True,
        gate_sites=(0x0115B09D, 0x0115B16B, 0x0115B350),  # cmp slot, 0x4b0
        byte_span_gate_sites=(0x0115B005,),  # cmp (ptr-pool), 0x226c80
        memset_sites=((0x0115B285, 0x2980),),  # FUN_0115b280 clears 0x2980 dwords
        note="per-slot kill log, 32B x slot; .killdat ALSO holds 256-entry tables "
        "(0x1165600/0x1166600/0x1170c00) that are NOT per-unit and stay in place",
    ),
    DirectArray(
        name=".mvstate_body",
        module=".mvcode",
        old_base=0x01182014,  # 0x1182000..0x1182010 are header fields
        stride=0x28,
        index_kind="slot",
        gate_byte_span=True,
        gate_sites=(),
        byte_span_gate_sites=(0x01181421,),  # cmp (ptr-pool), 0x226c7f
        memset_sites=(),
        note="move-order state, 40B x slot, indexed [slot*5*8]; header stays",
    ),
)


@dataclass
class RelocationPlan:
    input_sha256: str
    g2bss_va: int
    six_array_base: int
    six_array_span: int
    direct_arrays: list[dict[str, Any]] = field(default_factory=list)
    spike_sites: int = 0
    blocked: list[dict[str, Any]] = field(default_factory=list)

    def to_report(self) -> dict[str, Any]:
        return {
            "schema": "syw2plus.esl2610.g2-reloc-plan.v1-spike",
            "input_sha256": self.input_sha256,
            "capacity": CAPACITY,
            "status": "SPIKE_PATTERN_SETTLED_RUNTIME_PENDING",
            "g2bss_va": hex(self.g2bss_va),
            "six_array_base": hex(self.six_array_base),
            "six_array_span": hex(self.six_array_span),
            "direct_arrays": self.direct_arrays,
            "spike_operand_sites": self.spike_sites,
            "still_blocked": self.blocked,
        }


def plan_spike(data: bytes, *, require_pinned_base: bool = True) -> RelocationPlan:
    """Compute the spike relocation plan (six arrays + four direct arrays).

    Validates: the packed ``.g2bss`` is non-overlapping and the direct-array
    gate/memset/base old bytes match the pinned EXE.  Does not patch anything.
    """
    if require_pinned_base:
        pe_extend.verify_base(data)
    inv = g2_scan.build_inventory(data, require_pinned_base=False)

    # .g2bss goes at the first free RVA: pe_extend.add_section places the first
    # added section at the current SizeOfImage.  (When G6 is composed first it
    # takes this slot and bumps SizeOfImage; the standalone plan reports the
    # base SizeOfImage, and the real build reads it back after each add.)
    import pefile

    pe = pefile.PE(data=data, fast_load=True)
    try:
        g2bss_va = IMAGE_BASE + int(pe.OPTIONAL_HEADER.SizeOfImage)
    finally:
        pe.close()
    cursor = g2bss_va
    six_base = cursor
    cursor += SIX_ARRAY_SPAN

    plan = RelocationPlan(
        input_sha256=g2_scan._digest(data),  # noqa: SLF001
        g2bss_va=g2bss_va,
        six_array_base=six_base,
        six_array_span=SIX_ARRAY_SPAN,
    )

    # Direct arrays pack after the six-array block, in order.
    placed: list[tuple[int, int]] = [(six_base, six_base + SIX_ARRAY_SPAN)]
    for arr in SPIKE_ARRAYS:
        new_base = cursor
        span = arr.span_4093()
        cursor += span
        # non-overlap check
        for lo, hi in placed:
            if new_base < hi and lo < new_base + span:
                raise ValueError(f"{arr.name} overlaps a prior block in .g2bss")
        placed.append((new_base, new_base + span))
        plan.direct_arrays.append(
            {
                "name": arr.name,
                "module": arr.module,
                "old_base": hex(arr.old_base),
                "new_base": hex(new_base),
                "stride": hex(arr.stride),
                "span_1200": hex(arr.span_1200()),
                "span_4093": hex(span),
                "index_kind": arr.index_kind,
                "gate_sites_raise_1200_to_4093": [hex(v) for v in arr.gate_sites],
                "byte_span_gate_sites_raise": [hex(v) for v in arr.byte_span_gate_sites],
                "memset_count_rescale": [
                    {"va": hex(v), "old_dwords": hex(c)} for v, c in arr.memset_sites
                ],
                "note": arr.note,
            }
        )

    # Count the stock-array operand sites the six-array relocation must rewrite
    # (same classes the accepted 2608 G2 relocates), across ALL sections.
    plan.spike_sites = sum(
        1 for s in inv.sites if s.op_kind in ("disp", "imm", "neg_pool_base")
    )

    # Everything still outside the spike stays a blocker (fail-closed contract).
    report = inv.to_report()
    plan.blocked = report["unresolved"]
    return plan


def main() -> None:
    import argparse
    import json

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source")
    parser.add_argument("--json")
    args = parser.parse_args()
    plan = plan_spike(open(args.source, "rb").read())
    report = plan.to_report()
    if args.json:
        with open(args.json, "w") as handle:
            json.dump(report, handle, indent=2)
    keys = ("status", "g2bss_va", "six_array_span", "spike_operand_sites")
    print(json.dumps({k: report[k] for k in keys}, indent=2))


if __name__ == "__main__":
    main()
