#!/usr/bin/env python3
"""G2 UnitStruct pool expansion candidate builder (lap400 work, W4).

Builds a genuinely runnable candidate EXE whose UnitStruct pool holds
`CAPACITY` slots instead of the stock 1200, per work card
`docs/work/active/G2_UNIT_POOL_RELOCATION_SPIKE_LAP400.md` (W4), which
superseded W3 (`G2_UNIT_POOL_EXPANSION_SPIKE_LAP397.md`).

Three layers, applied in order to a private in-memory copy of the pinned
original bytes (the original file itself is only ever read):

  B-1  PE-header growth (`.data` VirtualSize, `.rsrc` RVA/SizeOfImage,
       9 resource payload offsets) -- delegates byte-for-byte to
       `tail_relocation_storage_layout_v1.build_layout_artifact` (W4),
       which relocates unit_pool/unit_existence/unit_age as one combined
       block to the image tail below `.rsrc`, instead of growing them in
       place (lap400 REJECT: in-place growth overlaps 1,311 live `.text`
       literal sites in the bulk save/load blob -- see
       `docs/history/laps/20260920_lap400_middle_g2_pool_overrun_reject.md`).
  B-2  Four allocator/destroy-all immediate/displacement constants
       (`0x00442FAC`, `0x00442FB1`, `0x00442FD1`, `0x0044317D`), each
       verified against its pinned old bytes before being overwritten.
  B-3  Every `.text` instruction operand (memory displacement or
       immediate) that encodes a literal address inside the stock
       [pool_base, pool_base+stride*1200) / [existence_base, +2*1200) /
       [age_base, +2*1200) ranges is re-scanned (not hand-transcribed)
       and shifted by that region's uniform address delta.  A region
       whose sites are not all uniformly translatable (an "outlier",
       lap397 A4) or a site whose operand encoding cannot be
       unambiguously located in the instruction's own bytes aborts the
       whole build -- this module never guesses or patches partially.

imm operands (lap439/W19 root-cause repair): a literal in
[base, old_end) is only a real pool/existence/age address in two shapes
seen anywhere in this binary -- a straight `mov reg, base` load, or a
`cmp reg, base` end-of-array-walk boundary guarded by a same-register
`add reg, elem_size` a few instructions earlier. Everything else in range
(bit masks, call-argument words, another loop's own bound that happens to
land in [base, old_end) by coincidence) is rejected. `0x00421349` and
`0x0048F4B4` (lap398 FO-4) and `0x0040F051` and 7 siblings (lap439, the
actual W18/P2 fault root cause) are all `cmp reg, pool_base(+-0x20)`
preceded by `add reg, 0x8c` -- a completely unrelated 50-entry table's own
stride, not this region's -- so the structural rule rejects all of them
without naming a single VA. See `IMM_SITE_CLASSIFICATION` and
`_classify_imm_operand` below; that table is a completeness/consistency
oracle (every in-range imm site must appear in it, and the recorded
verdict must agree with the structural rule), not the accept/reject
decision itself.

Capacity choice: `CAPACITY = 1210` (the work card's own suggested N=1300
is not needed either way). Under tail relocation the old N<=1217
`category_slot_list_a/b`/FO-3-gap collision ceiling (W3-era, in-place
growth only) no longer applies -- W4 §1 confirms the relocated arrays
occupy virgin image-tail space, disjoint from every other region at any
N. 1210 is kept anyway because it is already enough to exercise slot ids
up to 1209, and the work card asks to keep N small.
"""

from __future__ import annotations

import argparse
import hashlib
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import capstone
import pefile

try:
    from patches.population.tail_relocation_storage_layout_v1 import (
        ORIGINAL_SHA256,
        RELOCATED_REGIONS as REGIONS,
        build_layout_artifact,
        layout,
    )
except ModuleNotFoundError:  # direct absolute-path CLI invocation
    import importlib.util

    _spec = importlib.util.spec_from_file_location(
        "tail_relocation_storage_layout_v1",
        Path(__file__).with_name("tail_relocation_storage_layout_v1.py"),
    )
    if _spec is None or _spec.loader is None:
        raise ImportError("tail_relocation_storage_layout_v1 is unavailable")
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    ORIGINAL_SHA256 = _mod.ORIGINAL_SHA256
    REGIONS = _mod.RELOCATED_REGIONS
    build_layout_artifact = _mod.build_layout_artifact
    layout = _mod.layout

IMAGE_BASE = 0x00400000
STOCK_CAPACITY = 1200

# N=1300 was the work card's suggestion; see module docstring for why this
# module uses 1210 instead (catA/catB/FO-3-gap collision at N>=1218-1224).
CAPACITY = 1210

# REGIONS[0..2] == unit_pool, unit_existence, unit_age (lap382-388 pinned).
POOL_BASE = REGIONS[0].base
POOL_STRIDE = REGIONS[0].elem_size
POOL_OLD_END = POOL_BASE + POOL_STRIDE * STOCK_CAPACITY
EXISTENCE_BASE = REGIONS[1].base
EXISTENCE_OLD_END = EXISTENCE_BASE + REGIONS[1].elem_size * STOCK_CAPACITY
AGE_BASE = REGIONS[2].base
AGE_OLD_END = AGE_BASE + REGIONS[2].elem_size * STOCK_CAPACITY

# W19 Step 1 (docs/work/active/G2_IMM_FIXUP_FALSE_POSITIVE_REPAIR_LAP439.md):
# every imm-operand site the pool/existence/age scan can find in the pinned
# original, forward-disassembled and classified by hand against its actual
# instruction semantics. Full evidence/reasoning:
# temp/Syw2plus_patch/g2_capacity/20260921_lap440_imm_fixup_repair/
# imm_classification.json. Keyed by VA because each site's surrounding code
# differs; see LIST_REGION_IMM_VALUE_CLASSIFICATION in
# g2_full_unit_capacity_v1.py for the analogous table for the
# category/active-list scanner, which is keyed by value instead (all of its
# current sites share one address, loaded identically 72 times).
IMM_SITE_CLASSIFICATION: dict[int, str] = {
    0x00401BC2: "NOT_ADDRESS",  # test eax, 0x800000 -- bit-23 mask
    0x004010B7: "NOT_ADDRESS",  # push 0x800807 -- call-arg flags word
    0x004010E4: "NOT_ADDRESS",  # push 0x801007 -- call-arg flags word
    0x0040F051: "NOT_ADDRESS",  # cmp ebx, 0x66b7b0 -- unrelated 0x8c-stride table bound (P2 fault root cause)
    0x00421349: "NOT_ADDRESS",  # cmp ebx, 0x66b790 -- lap398 FO-4, same unrelated 0x8c-stride table (its own base)
    0x0048F4B4: "NOT_ADDRESS",  # cmp edx, 0x66b790 -- lap398 FO-4, same unrelated 0x8c-stride table (its own base)
    0x0040F4B7: "ADDRESS",  # mov edi, 0x66b790 -- genuine pool base load
    0x0040F4BC: "ADDRESS",  # mov esi, 0x8990c8 -- genuine existence base load
    0x0040F4E1: "ADDRESS",  # cmp esi, 0x899a28 -- existence-walk exclusive end (== age base)
    0x0040F4F8: "ADDRESS",  # mov esi, 0x66b790 -- genuine pool base load
    0x0040F4FD: "ADDRESS",  # mov ebx, 0x8990c8 -- genuine existence base load
    0x0040F52F: "ADDRESS",  # cmp ebx, 0x899a28 -- existence-walk exclusive end (== age base)
    0x0041334E: "NOT_ADDRESS",  # cmp ebp, 0x66b7b0 -- same unrelated table bound
    0x00420582: "NOT_ADDRESS",  # cmp edx, 0x66b7b0 -- same unrelated table bound
    0x00420A5B: "NOT_ADDRESS",  # cmp ecx, 0x66b7b0 -- same unrelated table bound
    0x00420CEA: "NOT_ADDRESS",  # cmp edx, 0x66b7b0 -- same unrelated table bound
    0x00420DB7: "NOT_ADDRESS",  # cmp edx, 0x66b7b0 -- same unrelated table bound
    0x00422DC2: "ADDRESS",  # mov esi, 0x66b790 -- genuine pool base load (per-slot init loop)
    0x0042152B: "NOT_ADDRESS",  # cmp ebx, 0x66b7b0 -- same unrelated table bound
    0x004720A0: "NOT_ADDRESS",  # test dword ptr [esi+0x1d8], 0x800000 -- bit-23 mask
    0x004748EA: "NOT_ADDRESS",  # test dword ptr [esi+0x1dc], 0x800000 -- bit-23 mask
    0x00491723: "NOT_ADDRESS",  # push 0x67f6f8 -- COLORREF arg, next insn `call SetTextColor`
    0x0049D37C: "NOT_ADDRESS",  # push 0x800010 -- call-arg flags word
    0x004A3FAF: "NOT_ADDRESS",  # cmp eax, 0x66b7b0 -- same unrelated table bound
    0x004A8385: "NOT_ADDRESS",  # test esi, 0x800000 -- bit-23 mask
    0x004A86F4: "NOT_ADDRESS",  # push 0x800000 -- call-arg flags word
    0x004A8724: "NOT_ADDRESS",  # push 0x800000 -- call-arg flags word
    0x004A8793: "NOT_ADDRESS",  # push 0x800000 -- call-arg flags word
    0x004A8801: "NOT_ADDRESS",  # push 0x800000 -- call-arg flags word
    0x004A886D: "NOT_ADDRESS",  # push 0x800000 -- call-arg flags word
    0x004A88A4: "NOT_ADDRESS",  # push 0x800000 -- call-arg flags word
    0x004A88D9: "NOT_ADDRESS",  # push 0x800000 -- call-arg flags word
    0x004A9F8C: "NOT_ADDRESS",  # push 0x870087 -- switch-table constant
    0x004A9F98: "NOT_ADDRESS",  # push 0x878700 -- switch-table constant
}

# The only two mnemonics that ever encode this region's own address as an
# imm operand anywhere in this binary (see IMM_SITE_CLASSIFICATION).
_ADDRESS_LOAD_MNEMONICS = frozenset({"mov"})
_ADDRESS_BOUNDARY_MNEMONICS = frozenset({"cmp"})
# Both known genuine boundary checks (0x40f4e1/0x40f52f) find their guarding
# `add reg, elem_size` within 2 instructions; both known false positives
# (0x421349/0x48f4b4, plus the P2 fault root cause 0x40f051 and siblings)
# have a *different*-register or *different*-stride add in between. 6 gives
# ample margin without matching into a prior, unrelated loop.
_BOUNDARY_LOOKBACK_WINDOW = 6


def _find_matching_stride_add(
    insns: list[capstone.CsInsn], index: int, reg: int, elem_size: int
) -> bool:
    """Search backward for the nearest `add <reg>, <imm>` and report whether
    its step equals `elem_size`. This is what actually distinguishes a
    genuine end-of-array-walk `cmp reg, region_base` from a coincidental
    value collision with some unrelated loop's own bound: a real walk over
    this region increments its pointer by this region's own element size;
    a colliding unrelated loop (lap398 FO-4, lap439 P2 root cause) does not.
    """
    lo = max(0, index - _BOUNDARY_LOOKBACK_WINDOW)
    for prior in insns[lo:index][::-1]:
        if prior.mnemonic != "add":
            continue
        ops = prior.operands
        if len(ops) != 2 or ops[0].type != capstone.x86.X86_OP_REG or ops[0].reg != reg:
            continue
        if ops[1].type != capstone.x86.X86_OP_IMM:
            return False
        return (int(ops[1].imm) & 0xFFFFFFFF) == elem_size
    return False


def _classify_imm_operand(
    insns: list[capstone.CsInsn],
    index: int,
    insn: capstone.CsInsn,
    value: int,
    base: int,
    elem_size: int,
    classification: dict[int, str],
    key: int,
) -> str:
    """Rule-based imm accept/reject (W19 Step 2 -- no VA denylist).

    Computes a structural verdict from the instruction itself (see module
    docstring), then requires it to agree with the recorded classification
    for `key`. Disagreement, or `key` missing from `classification`
    entirely, aborts the build instead of guessing -- this is what makes
    the classification table a consistency oracle rather than a denylist:
    it does not by itself decide anything, and a bug in the structural
    rule can never silently apply because it would immediately conflict
    with the recorded evidence.
    """
    bucket = value - base
    if insn.mnemonic in _ADDRESS_LOAD_MNEMONICS and bucket == 0:
        structural = "ADDRESS"
    elif (
        insn.mnemonic in _ADDRESS_BOUNDARY_MNEMONICS
        and bucket == 0
        and insn.operands
        and insn.operands[0].type == capstone.x86.X86_OP_REG
        and _find_matching_stride_add(insns, index, insn.operands[0].reg, elem_size)
    ):
        structural = "ADDRESS"
    else:
        structural = "NOT_ADDRESS"

    recorded = classification.get(key)
    if recorded is None:
        raise BuildAbortedError(
            f"unclassified imm site at 0x{insn.address:08x} value=0x{value:08x} "
            f"({insn.mnemonic} {insn.op_str}); Step1 classification required "
            "before this can be built"
        )
    if recorded != structural:
        raise BuildAbortedError(
            f"imm site at 0x{insn.address:08x} value=0x{value:08x}: structural "
            f"rule says {structural}, Step1 classification says {recorded} -- "
            "refusing to build on disagreement"
        )
    return structural

# B-2: (va, old_bytes, imm_or_disp_byte_offset_in_encoding, width, kind)
# kind "imm": value replaced is a plain trailing imm32.
# kind "disp32": value replaced is the mod r/m disp32 field (may be negative).
B2_SITES: tuple[dict[str, Any], ...] = (
    {
        "va": 0x00442FAC,
        "old_bytes": bytes.fromhex("b92a9a8900"),
        "old_value": 0x00899A2A,
        "new_value": lambda n: layout(n).regions[2].new_start + 2,
        "note": "allocator scan start = new_age_base + 2",
    },
    {
        "va": 0x00442FB1,
        "old_bytes": bytes.fromhex("6683b9a0f6ffff00"),
        "old_value": -1200 * 2 & 0xFFFFFFFF,
        "new_value": lambda n: (-n * 2) & 0xFFFFFFFF,
        "note": "allocator existence-relative displacement = -2N",
    },
    {
        "va": 0x00442FD1,
        "old_bytes": bytes.fromhex("81f988a38900"),
        "old_value": 0x0089A388,
        "new_value": lambda n: layout(n).regions[2].new_end,
        "note": "allocator scan exclusive end = new_age_base + 2N",
    },
    {
        "va": 0x0044317D,
        "old_bytes": bytes.fromhex("81feb0040000"),
        "old_value": 0x000004B0,
        "new_value": lambda n: n,
        "note": "destroy-all loop bound = N",
    },
)

# The four B-2 sites are patched with their own domain-specific formula (not
# a plain region +delta -- e.g. the -2N existence-relative displacement is
# not itself an address in any region's range).  One of them (0x00442FAC,
# `mov ecx, age_base+2`) also numerically falls inside the generic unit_age
# immediate scan; excluding all four here avoids applying a second, generic
# (and for that one site, correct-by-coincidence-only) patch on top of B-2.
B2_EXCLUDED_VAS = frozenset(site["va"] for site in B2_SITES)


class BuildAbortedError(RuntimeError):
    """Raised instead of guessing when a fixup site cannot be unambiguously applied."""


@dataclass(frozen=True)
class FixupSite:
    va: int
    region: str
    op_kind: str  # "disp" | "imm"
    old_value: int
    new_value: int


def verify_original(data: bytes) -> None:
    if hashlib.sha256(data).hexdigest() != ORIGINAL_SHA256:
        raise ValueError("original EXE SHA256 mismatch; refusing to build a candidate")


def _text_section(pe: pefile.PE) -> tuple[int, int, bytes]:
    matches = [s for s in pe.sections if s.Name.rstrip(b"\0") == b".text"]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one .text section, found {len(matches)}")
    section = matches[0]
    va_start = IMAGE_BASE + int(section.VirtualAddress)
    raw_start = int(section.PointerToRawData)
    raw_end = raw_start + int(section.SizeOfRawData)
    return va_start, raw_start, bytes(pe.__data__[raw_start:raw_end])


def _decode(text: bytes, start: int) -> list[capstone.CsInsn]:
    engine = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    engine.detail = True
    engine.skipdata = True
    return [i for i in engine.disasm(text, start) if i.mnemonic != ".byte"]


def _region_sites(
    insns: list[capstone.CsInsn], region: str, base: int, old_end: int, elem_size: int
) -> list[FixupSite]:
    """Every disp/imm operand in `.text` whose literal value falls in
    `[base, old_end)`, excluding the FO-4 static-table sites.

    A memory-operand (disp) site is only accepted in "bucket 0" -- i.e. its
    field offset `disp - base` is `< elem_size` -- meaning the literal
    encodes a `[reg(+idx) + base + field]` plain field access with the slot
    selected dynamically by the register; a uniform `+delta` then always
    lands on the same field of the same (possibly relocated) slot,
    regardless of which slot the register holds at runtime.  A disp outside
    bucket 0, or with neither a base nor an index register (so nothing
    dynamic could be adding a slot offset), is treated the same way lap398
    treated FO-4: a suspicious coincidental-value collision that must be
    verified by hand, not blindly patched -- so this raises instead.

    An immediate-operand (imm) site is only accepted if `_classify_imm_operand`
    (module-level, W19 Step 2) rules it a genuine address: an imm is not
    self-evidently one just because its value falls in range -- see
    IMM_SITE_CLASSIFICATION and the lap439 P2 fault root cause it fixes.
    """
    sites: list[FixupSite] = []
    for index, insn in enumerate(insns):
        if insn.address in B2_EXCLUDED_VAS:
            continue
        for op in insn.operands:
            if op.type == capstone.x86.X86_OP_MEM:
                disp = int(op.mem.disp) & 0xFFFFFFFF
                if not (base <= disp < old_end):
                    continue
                if not op.mem.base and not op.mem.index:
                    raise BuildAbortedError(
                        f"{region}: absolute-memory site at 0x{insn.address:08x} "
                        "cannot be translated by a uniform delta"
                    )
                if disp - base >= elem_size:
                    raise BuildAbortedError(
                        f"{region}: stride-bucket outlier at 0x{insn.address:08x} "
                        f"disp=0x{disp:08x} field_offset=0x{disp - base:x} "
                        f"(>= elem_size 0x{elem_size:x})"
                    )
                sites.append(FixupSite(insn.address, region, "disp", disp, disp))
            elif op.type == capstone.x86.X86_OP_IMM:
                value = int(op.imm) & 0xFFFFFFFF
                if not (base <= value < old_end):
                    continue
                verdict = _classify_imm_operand(
                    insns, index, insn, value, base, elem_size,
                    IMM_SITE_CLASSIFICATION, insn.address,
                )
                if verdict == "NOT_ADDRESS":
                    continue
                sites.append(FixupSite(insn.address, region, "imm", value, value))
    return sites


def collect_fixup_sites(original: bytes) -> dict[str, list[FixupSite]]:
    """Re-scan `.text` (never hand-transcribed) for every pool/existence/age
    literal-address site, per work card §B-3."""
    pe = pefile.PE(data=original, fast_load=True)
    try:
        text_va, _text_raw, text_bytes = _text_section(pe)
    finally:
        pe.close()
    insns = _decode(text_bytes, text_va)
    return {
        "unit_pool": _region_sites(insns, "unit_pool", POOL_BASE, POOL_OLD_END, POOL_STRIDE),
        "unit_existence": _region_sites(
            insns, "unit_existence", EXISTENCE_BASE, EXISTENCE_OLD_END, REGIONS[1].elem_size
        ),
        "unit_age": _region_sites(
            insns, "unit_age", AGE_BASE, AGE_OLD_END, REGIONS[2].elem_size
        ),
    }


def _va_to_file_offset(pe: pefile.PE, va: int) -> int:
    for section in pe.sections:
        start = IMAGE_BASE + int(section.VirtualAddress)
        if start <= va < start + int(section.SizeOfRawData):
            return int(section.PointerToRawData) + (va - start)
    raise ValueError(f"0x{va:08x} is not inside any raw section")


def _patch_literal(out: bytearray, pe: pefile.PE, insn_va: int, old_value: int, new_value: int) -> None:
    """Locate the unique 4-byte little-endian encoding of `old_value` inside
    the instruction starting at `insn_va` and overwrite it with `new_value`.
    Aborts (never guesses) if the encoding is missing or not unique.
    """
    file_off = _va_to_file_offset(pe, insn_va)
    # Instructions in this ISA are at most 15 bytes; probe a safe span and
    # then re-decode to find this instruction's *own* length. A fixed-size
    # window (without re-decoding) can bleed into the next instruction(s) --
    # a read-modify-write triplet like `mov edi,[ecx*8+lit]; add edi,eax;
    # mov [ecx*8+lit],edi` encodes the same literal twice within 16 bytes of
    # the first occurrence, producing a false "not unique" abort (or worse,
    # patching the wrong occurrence) despite each instruction's own encoding
    # being perfectly unambiguous on its own.
    probe = bytes(out[file_off : file_off + 16])
    engine = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    decoded = next(engine.disasm(probe, insn_va), None)
    if decoded is None or decoded.address != insn_va:
        raise BuildAbortedError(f"0x{insn_va:08x}: could not re-decode instruction to bound its length")
    window = probe[: decoded.size]
    needle = struct.pack("<I", old_value & 0xFFFFFFFF)
    positions = [i for i in range(len(window) - 3) if window[i : i + 4] == needle]
    if len(positions) != 1:
        raise BuildAbortedError(
            f"0x{insn_va:08x}: expected exactly one encoding of 0x{old_value:08x} "
            f"in the instruction window, found {len(positions)}"
        )
    out[file_off + positions[0] : file_off + positions[0] + 4] = struct.pack(
        "<I", new_value & 0xFFFFFFFF
    )


def build_candidate(original: bytes, n: int = CAPACITY) -> tuple[bytes, dict[str, Any]]:
    """Build the N-slot pool candidate from a private copy of `original`.
    `original` is only ever read.  Returns (patched_bytes, report)."""
    verify_original(original)
    if n < STOCK_CAPACITY:
        raise ValueError(f"capacity must be >= {STOCK_CAPACITY}")

    # B-1: PE header growth (delegates to the ACCEPTED lap388 calculator).
    stage_b1 = build_layout_artifact(original, n)
    out = bytearray(stage_b1)
    pe = pefile.PE(data=bytes(out), fast_load=True)
    try:
        # B-2: four allocator/destroy-all constants, old-bytes verified.
        b2_applied: list[dict[str, Any]] = []
        for site in B2_SITES:
            va = site["va"]
            file_off = _va_to_file_offset(pe, va)
            actual = bytes(out[file_off : file_off + len(site["old_bytes"])])
            if actual != site["old_bytes"]:
                raise BuildAbortedError(
                    f"B-2 site 0x{va:08x}: old bytes mismatch "
                    f"(expected {site['old_bytes'].hex()}, found {actual.hex()})"
                )
            old_value = site["old_value"]
            new_value = site["new_value"](n)
            _patch_literal(out, pe, va, old_value, new_value)
            b2_applied.append(
                {
                    "va": f"0x{va:08x}",
                    "old_value": f"0x{old_value & 0xFFFFFFFF:08x}",
                    "new_value": f"0x{new_value & 0xFFFFFFFF:08x}",
                    "note": site["note"],
                }
            )

        # B-3: re-scanned pool/existence/age literal-address fixups.
        sites_by_region = collect_fixup_sites(bytes(stage_b1))
        result = layout(n)
        deltas = {
            "unit_pool": result.regions[0].new_start - result.regions[0].old_start,
            "unit_existence": result.regions[1].new_start - result.regions[1].old_start,
            "unit_age": result.regions[2].new_start - result.regions[2].old_start,
        }
        b3_applied: dict[str, int] = {}
        for region, sites in sites_by_region.items():
            delta = deltas[region]
            count = 0
            for site in sites:
                new_value = (site.old_value + delta) & 0xFFFFFFFF
                if new_value == site.old_value:
                    continue  # delta==0 (unit_pool): genuinely a no-op, not a skipped fixup.
                _patch_literal(out, pe, site.va, site.old_value, new_value)
                count += 1
            b3_applied[region] = count
    finally:
        pe.close()

    if len(out) != len(original):
        raise BuildAbortedError("candidate changed file length; no raw bytes should move")

    report = {
        "capacity": n,
        "stock_capacity": STOCK_CAPACITY,
        "original_sha256": ORIGINAL_SHA256,
        "candidate_sha256": hashlib.sha256(bytes(out)).hexdigest(),
        "b1_pe_header": "delegated to tail_relocation_storage_layout_v1.build_layout_artifact",
        "b2_constants": b2_applied,
        "b3_fixup_site_counts": b3_applied,
        "b3_imm_classification": {
            "address": sorted(
                f"0x{va:08x}" for va, v in IMM_SITE_CLASSIFICATION.items() if v == "ADDRESS"
            ),
            "not_address": sorted(
                f"0x{va:08x}" for va, v in IMM_SITE_CLASSIFICATION.items() if v == "NOT_ADDRESS"
            ),
        },
        "deltas": {k: f"0x{v:08x}" if v >= 0 else f"-0x{-v:08x}" for k, v in deltas.items()},
    }
    return bytes(out), report


def write_candidate(original_path: Path, destination: Path, n: int = CAPACITY) -> dict[str, Any]:
    if destination.resolve() == original_path.resolve():
        raise ValueError("refusing to overwrite the original EXE")
    original = original_path.read_bytes()
    patched, report = build_candidate(original, n)
    destination.write_bytes(patched)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--capacity", type=int, default=CAPACITY)
    args = parser.parse_args()
    report = write_candidate(args.original, args.destination, args.capacity)
    import json

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
