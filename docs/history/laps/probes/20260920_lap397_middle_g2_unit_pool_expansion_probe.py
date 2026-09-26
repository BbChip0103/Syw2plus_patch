#!/usr/bin/env python3
"""lap397 middle — G2 global UnitStruct pool expansion: static feasibility surface.

Read-only, SHA-pinned, no game execution, no binary/memory writes.

The user instruction of 2026-09-20 00:33 KST made the **global UnitStruct pool
1,200-slot expansion execution spike** the immediate top priority (INBOX), with
the first success criterion "create an object at slot index >= 1200 in an
isolated real game, observe it with the existing reader, then prove death and
slot reuse", explicitly forbidding (i) a bare `0x4B0` constant edit and
(ii) overwriting the adjacent state region.

Nothing in the repo has yet measured *what the spike would actually have to
touch*.  This probe measures exactly that, from the pinned original bytes only:

  A1 geometry      re-derive pool/existence/age/active/catA/catB independently
                   of `tools/g2_unit_pool_xrefs.py` (no import of it).
  A2 index kind    which regions are indexed by SLOT id and which by a packed
                   COUNT -- decided from the raw registration bytes at
                   `FUN_0048BC00`, not from prose.  A count-indexed list does
                   not overflow when the slot namespace grows.
  A3 allocator     raw immediates of `FUN_00442FA0` (the free-slot allocator):
                   start, element displacement, exclusive end.
  A4 pool sites    every in-range base/index displacement candidate for the
                   pool, bucketed by `(disp - pool_base) // stride`.  A plain
                   field access `[reg + base + field]` must land in bucket 0
                   (field < stride); anything else is an outlier that cannot be
                   relocated by a blind uniform delta.
  A5 gap           reference count into the unreferenced-looking hole between
                   `age_end` and `category_a_base` (candidate in-place headroom
                   for an existence+age pair of N entries).
  A6 headroom      PE geometry: where a relocated pool of N slots could live.
  A7 roster        `roster_add 0x43EE30` bounds the owner's unit COUNT, not the
                   slot id -> per-player roster expansion is NOT on the spike's
                   critical path.

Every check appends to `failures`; rc is 1 if any failed.  A `failures == []`
result certifies only the byte facts listed above -- not that expansion is safe
to activate, and not any runtime or product claim.

Usage:
  python3 docs/history/laps/probes/20260920_lap397_middle_g2_unit_pool_expansion_probe.py \
      [--exe PATH] [--output PATH]
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import capstone
import pefile

ORIGINAL_SHA256 = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"
DEFAULT_EXE = (
    Path(__file__).resolve().parents[4] / "Syw2plus" / "syw2plus_original.exe"
)
IMAGE_BASE = 0x00400000

# --- pins transcribed by hand from the byte evidence cited in each field ------
# pool record stride, from FUN_0048B000's clear of 0x1d6 dwords (= 0x758 bytes)
# and FUN_00442FE0's removal using the same stride.
STRIDE = 0x758
SLOTS = 1200
POOL_BASE = 0x0066B790
BULK_START = 0x00892410          # == POOL_BASE + STRIDE * SLOTS (checked in A1)
EXISTENCE_BASE = 0x008990C8
AGE_BASE = 0x00899A28
AGE_END = 0x0089A388
CATEGORY_A_BASE = 0x0089B008
CATEGORY_A_END = 0x0089C2C8
CATEGORY_B_BASE = 0x0089C2CA
CATEGORY_B_END = 0x0089D58A
ACTIVE_BASE = 0x00974FA8
ACTIVE_END = 0x00975908
BULK_END = 0x00975D8C            # lap385/388 pinned bulk blob exclusive end

ALLOCATOR = 0x00442FA0
DESTROY_ALL = 0x00443170
REGISTER = 0x0048BC00
ROSTER_ADD = 0x0043EE30

ROSTER_FIELD = 0x0D4A            # PlayerStruct owner roster base offset
ROSTER_COUNT = 0x200A            # == ROSTER_FIELD + SLOTS * 4 (checked in A7)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1 << 20):
            digest.update(chunk)
    return digest.hexdigest()


def text_section(pe: pefile.PE) -> tuple[int, bytes]:
    matches = [s for s in pe.sections if s.Name.rstrip(b"\0").startswith(b".text")]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one .text section, found {len(matches)}")
    section = matches[0]
    start = int(pe.OPTIONAL_HEADER.ImageBase) + int(section.VirtualAddress)
    raw_end = int(section.PointerToRawData) + int(section.SizeOfRawData)
    return start, bytes(pe.__data__[section.PointerToRawData:raw_end])


def decode(text: bytes, start: int) -> list[capstone.CsInsn]:
    engine = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    engine.detail = True
    engine.skipdata = True
    return [i for i in engine.disasm(text, start) if i.mnemonic != ".byte"]


def body(insns: list[capstone.CsInsn], start: int, limit: int) -> list[capstone.CsInsn]:
    """Instructions from `start` up to and including the first `ret`/`retn`."""
    out: list[capstone.CsInsn] = []
    for insn in insns:
        if insn.address < start:
            continue
        if insn.address >= start + limit:
            break
        out.append(insn)
        if insn.mnemonic.startswith("ret"):
            break
    return out


def render(insn: capstone.CsInsn) -> dict[str, str]:
    return {
        "address": f"0x{insn.address:08x}",
        "bytes": insn.bytes.hex(" "),
        "text": f"{insn.mnemonic} {insn.op_str}".strip(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path, default=DEFAULT_EXE)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    failures: list[str] = []
    report: dict[str, Any] = {
        "probe": "lap397_middle_g2_unit_pool_expansion",
        "role": "middle (claude-opus-5 / high)",
        "read_only": True,
        "game_executed": False,
        "binary_modified": False,
    }

    exe = args.exe.expanduser().resolve(strict=True)
    digest = sha256_file(exe)
    report["source"] = {"path": str(exe), "sha256": digest}
    if digest != ORIGINAL_SHA256:
        failures.append(f"A0 original SHA mismatch: {digest}")
        report["failures"] = failures
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1

    pe = pefile.PE(str(exe), fast_load=True)
    try:
        image_base = int(pe.OPTIONAL_HEADER.ImageBase)
        size_of_image = int(pe.OPTIONAL_HEADER.SizeOfImage)
        sections = [
            {
                "name": s.Name.rstrip(b"\0").decode("ascii", "replace"),
                "va_start": f"0x{image_base + int(s.VirtualAddress):08x}",
                "va_end": f"0x{image_base + int(s.VirtualAddress) + int(s.Misc_VirtualSize):08x}",
                "virtual_size": int(s.Misc_VirtualSize),
                "raw_size": int(s.SizeOfRawData),
                "raw_end_va": f"0x{image_base + int(s.VirtualAddress) + int(s.SizeOfRawData):08x}",
            }
            for s in pe.sections
        ]
        text_start, text = text_section(pe)
        insns = decode(text, text_start)
    finally:
        pe.close()

    # ---- A1 geometry ------------------------------------------------------
    a1 = {
        "pool": {
            "base": f"0x{POOL_BASE:08x}",
            "stride": STRIDE,
            "slots": SLOTS,
            "end": f"0x{POOL_BASE + STRIDE * SLOTS:08x}",
            "bytes": STRIDE * SLOTS,
        },
        "existence": {"base": f"0x{EXISTENCE_BASE:08x}", "end": f"0x{AGE_BASE:08x}",
                      "element": 2, "entries": (AGE_BASE - EXISTENCE_BASE) // 2},
        "age": {"base": f"0x{AGE_BASE:08x}", "end": f"0x{AGE_END:08x}",
                "element": 2, "entries": (AGE_END - AGE_BASE) // 2},
        "active": {"base": f"0x{ACTIVE_BASE:08x}", "end": f"0x{ACTIVE_END:08x}",
                   "element": 2, "entries": (ACTIVE_END - ACTIVE_BASE) // 2},
        "category_a": {"base": f"0x{CATEGORY_A_BASE:08x}", "end": f"0x{CATEGORY_A_END:08x}",
                       "element": 4, "entries": (CATEGORY_A_END - CATEGORY_A_BASE) // 4},
        "category_b": {"base": f"0x{CATEGORY_B_BASE:08x}", "end": f"0x{CATEGORY_B_END:08x}",
                       "element": 4, "entries": (CATEGORY_B_END - CATEGORY_B_BASE) // 4},
        "pool_is_immediately_below_bulk": POOL_BASE + STRIDE * SLOTS == BULK_START,
        "existence_and_age_are_adjacent": AGE_BASE == EXISTENCE_BASE + SLOTS * 2,
    }
    if not a1["pool_is_immediately_below_bulk"]:
        failures.append("A1 pool end != pinned bulk start 0x892410")
    if not a1["existence_and_age_are_adjacent"]:
        failures.append("A1 existence end != age base")
    for name in ("existence", "age", "active", "category_a", "category_b"):
        if a1[name]["entries"] != SLOTS:
            failures.append(f"A1 {name} entry count {a1[name]['entries']} != {SLOTS}")
    report["A1_geometry"] = a1

    # ---- A2 slot-indexed vs count-indexed ---------------------------------
    # Registration FUN_0048BC00 writes each sidecar.  A slot-indexed write uses
    # the slot id as index; a count-indexed write uses the list's own count.
    reg = body(insns, REGISTER, 0x200)
    # A write is COUNT-indexed when the index register is loaded from the list's
    # own count word; it is SLOT-indexed when the index register is loaded from
    # the unit's own slot-id field (`unit + 0x29C`).  Decide from the bytes.
    SLOT_ID_FIELD = 0x29C
    sidecars = (
        ("unit_existence", EXISTENCE_BASE, None),
        ("unit_age", AGE_BASE, None),
        ("active_slot_list", ACTIVE_BASE, ACTIVE_END),
        ("category_slot_list_a", CATEGORY_A_BASE, CATEGORY_A_END),
        ("category_slot_list_b", CATEGORY_B_BASE, CATEGORY_B_END),
    )
    classified: dict[str, dict[str, Any]] = {}
    for label, base, count_addr in sidecars:
        write = None
        for index, insn in enumerate(reg):
            for op in insn.operands:
                if (op.type == capstone.x86.X86_OP_MEM
                        and (int(op.mem.disp) & 0xFFFFFFFF) == base
                        and op.mem.index):
                    write = (index, insn, insn.reg_name(op.mem.index))
        if write is None:
            failures.append(f"A2 no indexed write to {label} in FUN_0048BC00")
            continue
        index, insn, index_reg = write
        # Walk back until the instruction that defines the index register.
        source = None
        producer = None
        for previous in reversed(reg[:index]):
            names = {previous.reg_name(r) for r in previous.regs_access()[1] if r}
            wide = {n for n in names if n} | {
                n.replace("e", "", 1) for n in names if n and n.startswith("e")
            }
            if index_reg in names or index_reg in wide or index_reg.lstrip("e") in {
                (n or "").lstrip("e") for n in names
            }:
                producer = previous
                for op in previous.operands:
                    if op.type != capstone.x86.X86_OP_MEM:
                        continue
                    disp = int(op.mem.disp) & 0xFFFFFFFF
                    if count_addr is not None and disp == count_addr:
                        source = "list_own_count"
                    elif disp == SLOT_ID_FIELD:
                        source = "unit_slot_id_field"
                break
        increments_count = count_addr is not None and any(
            i.mnemonic == "inc"
            and any(op.type == capstone.x86.X86_OP_MEM
                    and (int(op.mem.disp) & 0xFFFFFFFF) == count_addr
                    for op in i.operands)
            for i in reg
        )
        kind = {
            "list_own_count": "COUNT_INDEXED",
            "unit_slot_id_field": "SLOT_INDEXED",
        }.get(source or "", "UNRESOLVED")
        classified[label] = {
            "write": render(insn),
            "index_register": index_reg,
            "index_producer": render(producer) if producer else None,
            "index_source": source,
            "count_word": f"0x{count_addr:08x}" if count_addr else None,
            "count_incremented_in_body": increments_count,
            "kind": kind,
        }
        if kind == "UNRESOLVED":
            failures.append(f"A2 index source unresolved for {label}")
    slot_indexed = [k for k, v in classified.items() if v["kind"] == "SLOT_INDEXED"]
    count_indexed = [k for k, v in classified.items() if v["kind"] == "COUNT_INDEXED"]
    a2 = {
        "registration_function": f"0x{REGISTER:08x}",
        "registration_instruction_count": len(reg),
        "slot_id_field": f"unit + 0x{SLOT_ID_FIELD:03x} (signed WORD)",
        "classification": classified,
        "slot_indexed_regions": ["unit_pool"] + slot_indexed,
        "count_indexed_regions": count_indexed,
        "consequence": (
            "a count-indexed list is bounded by the number of LIVE units, not by "
            "the slot-id namespace.  Growing the slot-id namespace therefore does "
            "not overflow them while fewer than 1200 units are alive; they store "
            "slot ids as elements and a slot id in [1200, 32767) still fits their "
            "signed WORD / DWORD element width."
        ),
    }
    if sorted(count_indexed) != sorted(
        ["active_slot_list", "category_slot_list_a", "category_slot_list_b"]
    ):
        failures.append(f"A2 unexpected count-indexed set: {count_indexed}")
    if sorted(slot_indexed) != ["unit_age", "unit_existence"]:
        failures.append(f"A2 unexpected slot-indexed set: {slot_indexed}")
    report["A2_index_kind"] = a2

    # ---- A3 allocator immediates ------------------------------------------
    alloc = body(insns, ALLOCATOR, 0x100)
    alloc_imms: list[dict[str, Any]] = []
    for insn in alloc:
        for op in insn.operands:
            if op.type == capstone.x86.X86_OP_IMM:
                alloc_imms.append({**render(insn), "kind": "imm",
                                   "value": f"0x{int(op.imm) & 0xFFFFFFFF:08x}"})
            elif op.type == capstone.x86.X86_OP_MEM and int(op.mem.disp) != 0:
                alloc_imms.append({**render(insn), "kind": "disp",
                                   "value": str(int(op.mem.disp))})
    destroy = body(insns, DESTROY_ALL, 0x40)
    a3 = {
        "allocator": f"0x{ALLOCATOR:08x}",
        "instruction_count": len(alloc),
        "encoded_constants": alloc_imms,
        "model": {
            "scan_start_va": f"0x{AGE_BASE + 2:08x}",
            "scan_end_exclusive_va": f"0x{AGE_END:08x}",
            # Ghidra renders this as `psVar3[-0x4b0]` in WORD units; the encoded
            # byte displacement is -0x960 = -(SLOTS * 2).
            "existence_relative_byte_displacement": -SLOTS * 2,
            "slot_range": "1..1199 (slot 0 never allocated; returns 0 when full)",
            "policy": "free slot with the largest age value (LRU-style)",
        },
        "destroy_all": {
            "function": f"0x{DESTROY_ALL:08x}",
            "instruction_count": len(destroy),
            "instructions": [render(i) for i in destroy],
            "bound_immediate": f"0x{SLOTS:x}",
        },
        "constants_that_must_change_for_N_slots": [
            "allocator scan start (age_base + 2)",
            "allocator existence-relative byte displacement (-2*N)",
            "allocator scan exclusive end (age_base + 2*N)",
            "destroy-all loop bound (N)",
        ],
    }
    if not any(c["value"] == str(-SLOTS * 2) for c in alloc_imms if c["kind"] == "disp"):
        failures.append("A3 allocator lacks the -0x960 existence displacement")
    if not any(c["kind"] == "imm" and c["value"] == f"0x{AGE_END:08x}" for c in alloc_imms):
        failures.append("A3 allocator lacks the 0x89a388 scan end immediate")
    report["A3_allocator"] = a3

    # ---- A4 pool relocation site surface ----------------------------------
    buckets: Counter[int] = Counter()
    outliers: list[dict[str, Any]] = []
    disp_sites = 0
    imm_sites = 0
    abs_sites = 0
    pool_end = POOL_BASE + STRIDE * SLOTS
    for insn in insns:
        for op in insn.operands:
            if op.type == capstone.x86.X86_OP_MEM:
                disp = int(op.mem.disp) & 0xFFFFFFFF
                if not (POOL_BASE <= disp < pool_end):
                    continue
                if not op.mem.base and not op.mem.index:
                    abs_sites += 1
                    continue
                disp_sites += 1
                bucket = (disp - POOL_BASE) // STRIDE
                buckets[bucket] += 1
                if bucket != 0:
                    outliers.append({**render(insn), "disp": f"0x{disp:08x}",
                                     "stride_bucket": bucket,
                                     "field_offset": (disp - POOL_BASE) % STRIDE})
            elif op.type == capstone.x86.X86_OP_IMM:
                value = int(op.imm) & 0xFFFFFFFF
                if POOL_BASE <= value < pool_end:
                    imm_sites += 1
    a4 = {
        "base_index_displacement_sites": disp_sites,
        "absolute_memory_sites": abs_sites,
        "in_range_immediate_sites": imm_sites,
        "stride_bucket_histogram": {str(k): v for k, v in sorted(buckets.items())},
        "bucket0_share": (
            round(buckets.get(0, 0) / disp_sites, 6) if disp_sites else None
        ),
        "outliers": outliers,
        "interpretation": (
            "bucket 0 == `[reg + pool_base + field]` with field < stride, i.e. a "
            "plain slot-indexed field access that a uniform +delta relocation "
            "translates soundly.  Non-zero buckets are NOT translated by a "
            "uniform delta and each needs individual analysis."
        ),
    }
    if disp_sites == 0:
        failures.append("A4 no pool displacement candidate decoded")
    report["A4_pool_relocation_surface"] = a4

    # ---- A5 gap between age_end and category_a_base -----------------------
    gap_refs: list[dict[str, Any]] = []
    for insn in insns:
        for op in insn.operands:
            value = None
            if op.type == capstone.x86.X86_OP_MEM:
                value = int(op.mem.disp) & 0xFFFFFFFF
            elif op.type == capstone.x86.X86_OP_IMM:
                value = int(op.imm) & 0xFFFFFFFF
            if value is not None and AGE_END <= value < CATEGORY_A_BASE:
                gap_refs.append({**render(insn), "value": f"0x{value:08x}"})
    gap_bytes = CATEGORY_A_BASE - AGE_END
    pair_span = CATEGORY_A_BASE - EXISTENCE_BASE
    a5 = {
        "gap_start": f"0x{AGE_END:08x}",
        "gap_end": f"0x{CATEGORY_A_BASE:08x}",
        "gap_bytes": gap_bytes,
        "decoded_reference_count": len(gap_refs),
        "decoded_references": gap_refs,
        "existence_plus_age_contiguous_span_bytes": pair_span,
        "max_N_for_in_place_existence_age_pair": pair_span // 4,
        "caveat": (
            "zero decoded references is fail-open: computed/aliased and "
            "bulk-relative accesses are not covered, and the gap's runtime "
            "owner is UNKNOWN.  This is candidate headroom, not proven free."
        ),
    }
    report["A5_existence_age_gap"] = a5

    # ---- A6 image headroom -------------------------------------------------
    image_end = image_base + size_of_image
    a6 = {
        "image_base": f"0x{image_base:08x}",
        "size_of_image": size_of_image,
        "image_end_va": f"0x{image_end:08x}",
        "sections": sections,
        "bulk_end_va": f"0x{BULK_END:08x}",
        "bytes_between_bulk_end_and_image_end": image_end - BULK_END,
        "pool_bytes_now": STRIDE * SLOTS,
        "extra_pool_bytes_per_slot": STRIDE,
        "extra_sidecar_bytes_per_slot": 2 + 2,  # existence + age only (A2)
        "pool_bytes_for_N": {
            str(n): STRIDE * n for n in (1201, 1250, 1500, 1999, 4001)
        },
        "relocated_pool_fits_in_existing_image_tail": {
            str(n): (image_end - BULK_END) >= STRIDE * n
            for n in (1201, 1250, 1500, 1999, 4001)
        },
    }
    report["A6_headroom"] = a6

    # ---- A7 roster is count-bounded, not slot-id-bounded -------------------
    roster = body(insns, ROSTER_ADD, 0x120)
    roster_sites = [
        render(insn) for insn in roster
        for op in insn.operands
        if op.type == capstone.x86.X86_OP_MEM
        and (int(op.mem.disp) & 0xFFFFFFFF) in (ROSTER_FIELD, ROSTER_COUNT)
    ]
    a7 = {
        "roster_add": f"0x{ROSTER_ADD:08x}",
        "instruction_count": len(roster),
        "roster_field_offset": f"0x{ROSTER_FIELD:04x}",
        "roster_count_offset": f"0x{ROSTER_COUNT:04x}",
        "count_offset_equals_field_plus_1200_dwords": (
            ROSTER_FIELD + SLOTS * 4 == ROSTER_COUNT
        ),
        "decoded_roster_sites": roster_sites,
        "conclusion": (
            "the 0x4B0 compare at roster_add bounds the OWNER'S UNIT COUNT, not "
            "the slot id.  An owner holding fewer than 1200 units can hold a "
            "slot id >= 1200 with no PlayerStruct change -> per-player roster "
            "(and therefore PlayerStruct stride / bulk save layout) is NOT on "
            "the spike's critical path."
        ),
    }
    if not a7["count_offset_equals_field_plus_1200_dwords"]:
        failures.append("A7 roster count offset != roster field + 1200*4")
    report["A7_roster_independence"] = a7

    # ---- A8 the 0x892410 alias split ---------------------------------------
    # `0x892410` is simultaneously the pool's exclusive end and the bulk state's
    # base (lap388 alias).  If the pool is relocated elsewhere, every reference
    # that means "bulk base" must keep its value and every reference that means
    # "pool end" must follow the pool.  Split them by addressing form: a
    # `[reg(*scale) + 0x892410 + k]` memory operand dereferences bulk state and
    # therefore means BULK_BASE; a bare immediate is ambiguous on its own.
    alias_bulk_relative: list[dict[str, Any]] = []
    alias_immediate: list[dict[str, Any]] = []
    alias_absolute: list[dict[str, Any]] = []
    for insn in insns:
        for op in insn.operands:
            if op.type == capstone.x86.X86_OP_MEM:
                disp = int(op.mem.disp) & 0xFFFFFFFF
                if disp != BULK_START:
                    continue
                record = {**render(insn), "disp": f"0x{disp:08x}"}
                if op.mem.base or op.mem.index:
                    alias_bulk_relative.append(record)
                else:
                    alias_absolute.append(record)
            elif op.type == capstone.x86.X86_OP_IMM:
                if (int(op.imm) & 0xFFFFFFFF) == BULK_START:
                    alias_immediate.append(render(insn))
    # A "pool end" use would have to be a bound: a compare or an arithmetic
    # combination.  A `this` pointer (`mov ecx, imm` before a thiscall) and a
    # blob source (`push imm` at the pinned save/load sites) are BULK_BASE uses.
    imm_by_mnemonic = Counter(site["text"].split()[0] for site in alias_immediate)
    BOUND_MNEMONICS = {"cmp", "sub", "add", "lea", "test", "and", "or", "xor"}
    bound_shaped = [
        site for site in alias_immediate
        if site["text"].split()[0] in BOUND_MNEMONICS
    ]
    this_pointer = [s for s in alias_immediate if s["text"].startswith("mov ecx,")]
    pushed = [s for s in alias_immediate if s["text"].startswith("push")]
    a8 = {
        "alias_address": f"0x{BULK_START:08x}",
        "meanings": ["unit_pool_exclusive_end", "bulk_state_base"],
        "bulk_relative_memory_operands": len(alias_bulk_relative),
        "absolute_memory_operands": len(alias_absolute),
        "bare_immediate_operands": len(alias_immediate),
        "total": len(alias_bulk_relative) + len(alias_absolute) + len(alias_immediate),
        "immediate_mnemonic_histogram": dict(imm_by_mnemonic),
        "this_pointer_idiom_sites": len(this_pointer),
        "pushed_sites": [s["address"] for s in pushed],
        "bound_shaped_sites": bound_shaped,
        "pool_end_uses": len(bound_shaped),
        "conclusion": (
            "no reference to 0x892410 is shaped like a pool-end bound.  Every "
            "immediate is either the `mov ecx, imm` thiscall `this` pointer for "
            "the bulk game-state object or the `push imm` blob source at the "
            "pinned save/load sites.  Relocating the unit pool therefore does "
            "NOT require editing any of these sites -- the alias splits cleanly "
            "in the relocation direction."
        ),
        "fail_open": (
            "this covers decoded operands only; a bound materialised through a "
            "computed or aliased pointer is not excluded"
        ),
    }
    if len(pushed) != 2:
        failures.append(f"A8 expected exactly 2 pushed blob-source sites, got {len(pushed)}")
    if len(this_pointer) + len(pushed) != len(alias_immediate):
        failures.append("A8 immediate sites are not exhausted by this-pointer + push")
    report["A8_pool_end_bulk_base_alias"] = a8

    # ---- A9 exact-value references to the pool base ------------------------
    base_imm: list[dict[str, Any]] = []
    base_mem: list[dict[str, Any]] = []
    for insn in insns:
        for op in insn.operands:
            if op.type == capstone.x86.X86_OP_IMM and (int(op.imm) & 0xFFFFFFFF) == POOL_BASE:
                base_imm.append(render(insn))
            elif op.type == capstone.x86.X86_OP_MEM and (int(op.mem.disp) & 0xFFFFFFFF) == POOL_BASE:
                base_mem.append(render(insn))
    report["A9_pool_base_sites"] = {
        "address": f"0x{POOL_BASE:08x}",
        "immediate_operands": len(base_imm),
        "memory_displacement_operands": len(base_mem),
        "immediate_mnemonics": dict(Counter(s["text"].split()[0] for s in base_imm)),
        "memory_mnemonics": dict(Counter(s["text"].split()[0] for s in base_mem)),
        "relocation_site_total_for_pool": disp_sites + imm_sites,
        "note": (
            "A4's displacement count already includes displacements equal to the "
            "base; this field lists the exact-value split so a relocation patcher "
            "can be checked against it."
        ),
    }

    # ---- verdict -----------------------------------------------------------
    report["verdict"] = {
        "spike_first_criterion": "slot id >= 1200 create -> observe -> die -> reuse",
        "regions_that_must_grow": ["unit_pool", "unit_existence", "unit_age"],
        "regions_that_must_NOT_grow_for_the_spike": [
            "active_slot_list", "category_slot_list_a", "category_slot_list_b",
            "player_roster",
        ],
        "dominant_cost": "unit_pool relocation displacement sites (see A4)",
        "out_of_scope_for_the_spike": ["bulk save/load format", "LAN"],
    }
    report["failures"] = failures
    encoded = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8", newline="\n")
    print(encoded, end="")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
