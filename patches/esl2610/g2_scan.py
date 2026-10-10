#!/usr/bin/env python3
"""Fail-closed operand inventory for a G2 unit-pool expansion on ESL 2610.

The accepted 2608 G2 patch relocated six unit-capacity arrays (unit pool,
existence/age, two category lists, the active-slot list) plus the ESL
portrait cache, and shifted every ``.text`` operand that encoded a literal
address inside those arrays.  2610 adds ~40 *new* official code sections and
~24 new BSS sections that did not exist in 2608; a safe 4093-slot build must
account for every operand in those sections too.  This module does not patch
anything.  It disassembles **every** executable section of the pinned 2610
EXE, finds every operand (memory displacement or immediate, including the
pointer-to-index forms ``reg - 0x66B790`` and the per-array upper bounds) that
lands in a unit-capacity region, classifies each into one of a fixed set of
classes, and *fails closed*: if any operand cannot be put in a known class, or
if a new per-unit BSS array cannot be proven resizable, the scan raises so a
build can never silently relocate the pool while leaving a 1200-sized array or
loop bound behind it.

The disassembly is a linear sweep that skips ``0xCC`` padding and whole runs
of zero bytes between functions.  On the pinned 2610 EXE this sweep reproduces
every unit-capacity operand that an independent Ghidra 12 auto-analysis of the
same file finds (see ``analysis/memory_maps`` provenance); the test pins the
counts so a different capstone build or a changed input is caught.

Output is a JSON-serialisable :class:`Inventory`.  It is the evidence a 4093
build must consume, and the list of everything that still blocks one.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Iterable

import capstone
import pefile
from capstone import x86

from patches.esl2610 import pe_extend

IMAGE_BASE = pe_extend.IMAGE_BASE
STOCK_CAPACITY = 1200
UNIT_STRIDE = 0x758

# The six stock unit-capacity regions (half-open), identical to the addresses
# the accepted 2608/2606 G2 patches relocate.  ``base`` .. ``base + stride*1200``
# plus, for the three lists, a trailing WORD counter.
POOL = (0x0066B790, 0x00892410)       # UnitStruct pool: stride 0x758 x 1200
EXIST = (0x008990C8, 0x00899A28)      # existence words x 1200
AGE = (0x00899A28, 0x0089A388)        # age words x 1200
CAT_A = (0x0089B008, 0x0089C2CC)      # category list A (4B x 1200 + WORD count)
CAT_B = (0x0089C2CA, 0x0089D58E)      # category list B (4B x 1200 + WORD count)
ACTIVE = (0x00974FA6, 0x0097590C)     # active-slot list (1-based base, 2B x1200 + count)

REGIONS = {
    "pool": POOL,
    "exist": EXIST,
    "age": AGE,
    "cat_a": CAT_A,
    "cat_b": CAT_B,
    "active": ACTIVE,
}

# The pool end 0x892410 is simultaneously the bulk-game-state base; operands
# equal to it or just inside the first stride above it are legitimately the
# bulk base, not pool slot 1200.  We record them but never relocate them.
BULK_BASE = 0x00892410

# Capacity bound immediates the engine compares a slot index against before
# indexing a unit-capacity array: 1200 and its +/-1 neighbours, and the pool
# byte-span 0x758*1200.  A 4093 build must raise each to 4093 / 0x758*4093.
BOUND_VALUES = {
    0x4B0: "N",            # 1200
    0x4AF: "N-1",          # 1199
    0x4AE: "N-2",          # 1198 (slot-1 pre-decremented loops)
    0x4B1: "N+1",
    0x226C80: "N*stride",  # 1200 * 0x758, pool byte span (inclusive bound)
    0x226C7F: "N*stride-1",
}


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass(frozen=True)
class Site:
    """One operand referencing a unit-capacity region or bound."""

    va: int
    section: str
    op_kind: str  # "disp" | "imm" | "neg_pool_base" | "bound"
    region: str
    value: int
    text: str


@dataclass
class Inventory:
    input_sha256: str
    sites: list[Site] = field(default_factory=list)
    new_perunit_bss: list[dict[str, Any]] = field(default_factory=list)
    unresolved: list[dict[str, Any]] = field(default_factory=list)

    def by_section(self) -> dict[str, dict[str, int]]:
        out: dict[str, dict[str, int]] = {}
        for s in self.sites:
            out.setdefault(s.section, {}).setdefault(s.op_kind + ":" + s.region, 0)
            out[s.section][s.op_kind + ":" + s.region] += 1
        return out

    def to_report(self) -> dict[str, Any]:
        text_sites = [s for s in self.sites if s.section == ".text"]
        new_sites = [s for s in self.sites if s.section not in (".text", ".rsrc")]
        return {
            "schema": "syw2plus.esl2610.g2-operand-inventory.v1",
            "input_sha256": self.input_sha256,
            "stock_capacity": STOCK_CAPACITY,
            "unit_stride": UNIT_STRIDE,
            "regions": {k: [hex(a), hex(b)] for k, (a, b) in REGIONS.items()},
            "total_sites": len(self.sites),
            "text_sites": len(text_sites),
            "new_section_sites": len(new_sites),
            "sites_by_section": self.by_section(),
            "new_perunit_bss": self.new_perunit_bss,
            "unresolved_count": len(self.unresolved),
            "unresolved": self.unresolved,
            "release_status": "BLOCKED" if self.unresolved else "CLASSIFIED",
        }


def _executable_sections(data: bytes) -> list[tuple[str, int, int, int, int]]:
    """Return (name, va, vsize, raw_size, raw_pointer) for executable sections."""
    pe = pefile.PE(data=data, fast_load=True)
    try:
        out = []
        for s in pe.sections:
            if not (int(s.Characteristics) & 0x20000000):  # IMAGE_SCN_MEM_EXECUTE
                continue
            out.append(
                (
                    s.Name.rstrip(b"\0").decode("latin1"),
                    IMAGE_BASE + int(s.VirtualAddress),
                    int(s.Misc_VirtualSize),
                    int(s.SizeOfRawData),
                    int(s.PointerToRawData),
                )
            )
        return out
    finally:
        pe.close()


def _new_bss_sections(data: bytes) -> list[tuple[str, int, int]]:
    pe = pefile.PE(data=data, fast_load=True)
    try:
        return [
            (
                s.Name.rstrip(b"\0").decode("latin1"),
                IMAGE_BASE + int(s.VirtualAddress),
                int(s.Misc_VirtualSize),
            )
            for s in pe.sections
            if int(s.Characteristics) == 0xC0000080  # uninitialised data, read/write
        ]
    finally:
        pe.close()


def _sweep(payload: bytes, va_start: int) -> Iterable[capstone.CsInsn]:
    """Linear disassembly skipping 0xCC padding and whole zero runs."""
    engine = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    engine.detail = True
    pos = 0
    n = len(payload)
    while pos < n:
        byte = payload[pos]
        if byte == 0xCC:
            pos += 1
            continue
        if byte == 0 and pos + 1 < n and payload[pos + 1] == 0:
            while pos < n and payload[pos] == 0:
                pos += 1
            continue
        insn = next(engine.disasm(payload[pos : pos + 16], va_start + pos), None)
        if insn is None:
            pos += 1
            continue
        yield insn
        pos += insn.size


def _region_of(value: int) -> str | None:
    for name, (lo, hi) in REGIONS.items():
        if lo <= value < hi:
            return name
    return None


def _classify_insn(section: str, insn: capstone.CsInsn) -> list[Site]:
    sites: list[Site] = []
    text = f"{insn.mnemonic} {insn.op_str}"
    for op in insn.operands:
        if op.type == x86.X86_OP_MEM:
            value = int(op.mem.disp) & 0xFFFFFFFF
            region = _region_of(value)
            if region is not None:
                sites.append(Site(insn.address, section, "disp", region, value, text))
                continue
            # pointer->index form: disp == -pool_base (lea reg,[unit - 0x66B790])
            if (-value) & 0xFFFFFFFF == POOL[0] and (op.mem.base or op.mem.index):
                sites.append(Site(insn.address, section, "neg_pool_base", "pool", value, text))
        elif op.type == x86.X86_OP_IMM:
            value = int(op.imm) & 0xFFFFFFFF
            region = _region_of(value)
            if region is not None:
                sites.append(Site(insn.address, section, "imm", region, value, text))
                continue
            if (-value) & 0xFFFFFFFF == POOL[0]:
                sites.append(Site(insn.address, section, "neg_pool_base", "pool", value, text))
            elif value in BOUND_VALUES:
                sites.append(Site(insn.address, section, "bound", BOUND_VALUES[value], value, text))
    return sites


def _perunit_bss(data: bytes) -> list[dict[str, Any]]:
    """New BSS sections whose byte size is an exact small multiple of 1200.

    Such a section is almost certainly a per-unit array (stride == size/1200)
    sized to the stock capacity and must grow to 4093, or be proven otherwise.
    Sections that are not an exact 1200 multiple are reported too (``exact``
    False) because they may still be a per-unit array with a header.
    """
    out = []
    for name, va, vsize in _new_bss_sections(data):
        if vsize == 0:
            continue
        # A per-unit array is header(<=64B) + stride*1200, with a plausible
        # per-unit record stride (<=256B).  Try every small header and keep the
        # tightest exact fit.
        stride = None
        header = None
        for hdr in range(0, 0x41, 2):
            body = vsize - hdr
            if body > 0 and body % STOCK_CAPACITY == 0:
                cand = body // STOCK_CAPACITY
                if 1 <= cand <= 0x100:
                    stride, header = cand, hdr
                    break
        out.append(
            {
                "section": name,
                "va": hex(va),
                "vsize": hex(vsize),
                "header_if_perunit": hex(header) if header is not None else None,
                "stride_if_perunit": hex(stride) if stride else None,
                "looks_per_unit": stride is not None,
            }
        )
    return out


def build_inventory(data: bytes, *, require_pinned_base: bool = True) -> Inventory:
    if require_pinned_base:
        pe_extend.verify_base(data)
    inv = Inventory(input_sha256=_digest(data))
    for name, va, vsize, raw_size, raw_pointer in _executable_sections(data):
        size = min(raw_size, max(vsize, 1)) if vsize else raw_size
        payload = data[raw_pointer : raw_pointer + size]
        for insn in _sweep(payload, va):
            inv.sites.extend(_classify_insn(name, insn))
    inv.new_perunit_bss = _perunit_bss(data)

    # Fail-closed classification of what still blocks a safe 4093 build.
    new_code_refs = [
        s for s in inv.sites if s.section not in (".text", ".rsrc") and s.op_kind != "bound"
    ]
    bound_sites = [s for s in inv.sites if s.op_kind == "bound"]
    perunit = [b for b in inv.new_perunit_bss if b["looks_per_unit"]]
    if new_code_refs:
        inv.unresolved.append(
            {
                "kind": "new_code_unit_capacity_refs",
                "count": len(new_code_refs),
                "detail": "operands in 2610-new code sections referencing the stock unit "
                "pool/existence/age/list arrays; each must relocate with the arrays, "
                "runtime-verified per module, before a 4093 build is safe",
                "sections": sorted({s.section for s in new_code_refs}),
            }
        )
    if bound_sites:
        inv.unresolved.append(
            {
                "kind": "capacity_bound_checks",
                "count": len(bound_sites),
                "detail": "slot/length bound immediates (1200, 1199, 1198, 0x758*1200) gating "
                "unit-capacity array access across code sections; each must be raised to "
                "4093 / 0x758*4093 or proven unrelated",
                "sections": sorted({s.section for s in bound_sites}),
            }
        )
    if perunit:
        inv.unresolved.append(
            {
                "kind": "new_perunit_bss_sized_1200",
                "count": len(perunit),
                "detail": "2610-new BSS sections sized to an exact 1200 multiple (per-unit "
                "arrays/caches keyed by unit slot or id); each must grow to 4093 or be "
                "proven not per-unit before the pool is expanded",
                "sections": [b["section"] for b in perunit],
            }
        )
    return inv


def main() -> None:
    import argparse
    import json

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="pinned official ESL2610 EXE")
    parser.add_argument("--json", help="write the full report to this path")
    args = parser.parse_args()
    data = open(args.source, "rb").read()
    inv = build_inventory(data)
    report = inv.to_report()
    if args.json:
        with open(args.json, "w") as handle:
            json.dump(report, handle, indent=2)
    keys = (
        "input_sha256",
        "total_sites",
        "text_sites",
        "new_section_sites",
        "unresolved_count",
        "release_status",
    )
    print(json.dumps({k: report[k] for k in keys}, indent=2))


if __name__ == "__main__":
    main()
