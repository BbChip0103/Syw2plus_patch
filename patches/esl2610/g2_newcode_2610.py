#!/usr/bin/env python3
"""G2 layer 2 for ESL 2610-line EXEs: retarget the official modules at relocated arrays.

:mod:`patches.esl2610.g2_spike_build` relocates the six stock unit-capacity
arrays for ``.text`` only.  The ~40 official code sections (modules) keep 940
operands into the stock arrays, so on the spike every module sees an empty
world: live runs show no unit ever dies (no combat, kills 0, all per-unit
module state 0) while the control fights normally.  This layer rewrites those
operands so the modules see the relocated arrays again.

Every operand is classified, fail-closed:

* inventory sites (:mod:`patches.esl2610.g2_scan`) of kind ``disp``/``imm`` are
  relocated with :func:`g2_reloc_2610.relocate_value`; ``neg_pool_base`` sites
  become ``-new_pool``.  :data:`KEEP_SITES` lists the few that are not
  addresses (COFF debug-directory timestamps inside the module headers, a bit
  mask, an unused thiscall ``this``);
* pool-end sentinels (``cmp reg, 0x892410+f``), negated pool ends
  (``lea r,[x-0x892410]``) and exist-array ends (``cmp reg, 0x899A28``) are not
  inside the six regions, so the scanner never sees them; they are listed
  explicitly and every operand in those value windows must be either listed
  or a known bulk-state operand, otherwise :func:`apply` raises;
* the three divisibility tests ``imul x,0x14B2A7C3; add x,K; ror x,3`` encode
  ``K = -pool * inv(0x758/8)`` and are recomputed for the new pool;
* one ESL ``.text`` write the stock oracle cannot replay (``0x47E51A``, a
  ``ds:``-prefixed unit-field store) is relocated here.

``clamp`` is the slot count a module may reach through those sentinels.  With
the default 1200 every module keeps working on slots 1..1199 exactly as in the
official EXE (its own 1200-sized per-unit arrays and ``< 1200`` gates are left
untouched) and ignores slots >= 1200.  Raising a module to 4093 needs its
per-unit arrays grown first; that is the next layer, done module by module.
"""

from __future__ import annotations

import hashlib
from typing import Any

import capstone
from capstone import x86

from patches.esl2610 import g2_reloc_2610, g2_scan, pe_extend

STOCK_CAPACITY = g2_scan.STOCK_CAPACITY
UNIT_STRIDE = g2_scan.UNIT_STRIDE
POOL_BASE, POOL_END = g2_scan.POOL
EXIST_BASE, EXIST_END = g2_scan.EXIST
POOL_SPAN = POOL_END - POOL_BASE  # 0x226C80

# Inventory sites that are not addresses into the six arrays.
KEEP_SITES = {
    0x011EB004: "COFF debug-directory timestamp 0x6ABD08BE (.jpopen header data)",
    0x011EC004: "COFF debug-directory timestamp 0x6ABD0E68 (.krbuild header data)",
    0x011F2004: "COFF debug-directory timestamp 0x6ABD8C68 (.closeco header data)",
    0x019DDB74: "bit mask 0x80000E for bt (state set), not an address",
    0x01090956: "this=0x78D024 passed to 0x1090700, which ignores ecx",
    0x0109097A: "this=0x78D024 passed to 0x1090700, which ignores ecx",
    0x0109098F: "this=0x78D024 passed to 0x1090700, which ignores ecx",
}

# ``cmp reg, 0x892410 + f``: pointer-range checks / pool walks ending at slot 1200.
POOL_END_CMP_SITES = (
    0x011372DF, 0x011373AC, 0x01144386, 0x01145A81, 0x01149547, 0x01601207,
    0x0199402D, 0x019948BE, 0x01998121, 0x01998669, 0x019AD795, 0x019B4C1F,
    0x019B560A, 0x019BC8A9, 0x019BF599, 0x019BF93D, 0x019C582A, 0x019D01C3,
    0x019D080A, 0x019D4899, 0x01A0E02A,
)
# ``lea r,[x-0x892410]`` / ``add r,-0x892410`` paired with ``cmp r,-span``.
POOL_END_NEG_SITES = (
    0x019A902B, 0x019AD02B, 0x019B100A, 0x019B2066, 0x019B406C, 0x019B494D,
    0x019B8169, 0x019BA066, 0x019BC02B, 0x019BE08C, 0x019BF27B, 0x019D3139,
    0x019DC008, 0x019DD312, 0x019DEC74,
)
# Immediates in the pool-end window that are the bulk game-state object.
POOL_END_BULK_SITES = {
    0x01090F9A: "mov ecx,0x892410 (bulk this)", 0x0112DC6F: "mov ecx,0x892410 (bulk this)",
    0x01138175: "mov ecx,0x8929B4 (bulk+0x5A4 this)",
    0x011F3702: "mov edx,0x8924C4 (bulk RNG field)", 0x011F3952: "mov edx,0x8924C4",
    0x0123C862: "mov edx,0x8924C4", 0x0123CAB2: "mov edx,0x8924C4",
    0x012555F4: "mov ecx,0x8924C4",
    0x0160235A: "cmp ecx,0x892410 (this is bulk?)", 0x016023A2: "cmp ecx,0x892410",
    0x01602476: "cmp ecx,0x892410", 0x01602545: "cmp ecx,0x892410",
    0x01602550: "cmp ecx,0x892410",
    0x0199119F: "mov ecx,0x892410 (bulk this)", 0x01991356: "mov ecx,0x892410",
    0x01991633: "mov ecx,0x892410", 0x0199A1DD: "mov ecx,0x892410",
    0x019A7681: "cmp ecx,0x892410 (this is bulk?)", 0x019A76A7: "cmp ecx,0x892410",
}
# ``cmp reg, 0x899A28``: walks over the existence words ending at slot 1200.
# (0x899A28 is also the age-array base; in the packed layout both coincide,
# but these sites are loop ends, so they follow ``clamp``.)
EXIST_END_SITES = (
    0x011908C0, 0x01191351, 0x011B7A97, 0x011B81DB, 0x011EC60C, 0x011F3D81,
    0x0123CEE1, 0x019A9464, 0x019B2532, 0x019BA529, 0x019E034E, 0x019EC3C3,
)
# ``imul x, 0x14B2A7C3 ; add x, K ; ror x, 3 ; cmp x, 0x22DC0D``: K = -pool*inv.
DIV_TEST_INV = 0x14B2A7C3  # inverse of 0x758/8 = 0xEB mod 2**32
DIV_TEST_SITES = (0x019B1023, 0x019B4962, 0x019BF294)
# ESL .text write the stock oracle cannot replay (segment-prefixed encoding).
TEXT_EXTRA_SITES = (0x0047E51A,)

# Methods of the bulk game-state object (this = 0x892410, called with
# ``mov ecx,0x892410``) reach the category lists, the active list and the
# exist/age words *relative to this*, so neither the scanner nor the stock
# oracle sees them.  The vision rebuild 0x4A3800 walks the active list this
# way: left on the stock list (count 0) no unit reveals the map and no unit
# ever auto-acquires a target.  (va, old disp); new disp = new address - this.
BULK_BASE = 0x00892410
TEXT_BULK_RELATIVE = (
    (0x004A3622, 0x9EB8), (0x004A3642, 0x8BF8), (0x004A364A, 0x8BF8), (0x004A366E, 0x8BF8),
    (0x004A3675, 0x9EB8), (0x004A3692, 0x9EB8), (0x004A36A0, 0xB17A), (0x004A36BA, 0x9EBA),
    (0x004A36C2, 0x9EBA), (0x004A36DF, 0x9EB6), (0x004A36E6, 0x9EBA), (0x004A36ED, 0xB17A),
    (0x004A39DA, 0xE34F8), (0x004A39E6, 0xE2B98), (0x004A3A1B, 0xE34F8),
    (0x004A321C, 0x7618),  # lea eax,[this+age]: game-start clear of exist/age
)
# That clear loop: ``mov ecx,1200`` entries and ``[eax-2*1200]`` (exist below age).
TEXT_BULK_CLEAR_COUNT = 0x004A3222
TEXT_BULK_CLEAR_EXIST = 0x004A3227

_MD = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
_MD.detail = True


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _insn(image: bytes, va: int) -> capstone.CsInsn:
    off = pe_extend.va_to_offset(image, va)
    insn = next(_MD.disasm(image[off : off + 16], va), None)
    if insn is None:
        raise ValueError(f"cannot decode instruction at 0x{va:08x}")
    return insn


def _patch_operand(out: bytearray, va: int, old: int, new: int, *, kind: str | None = None) -> str:
    """Rewrite the 4-byte disp/imm equal to ``old`` in the instruction at ``va``."""
    insn = _insn(bytes(out), va)
    hits = []
    if kind in (None, "disp") and insn.disp_size == 4 and (insn.disp & 0xFFFFFFFF) == old:
        hits.append(insn.disp_offset)
    if kind in (None, "imm") and insn.imm_size == 4:
        for op in insn.operands:
            if op.type == x86.X86_OP_IMM and (op.imm & 0xFFFFFFFF) == old:
                hits.append(insn.imm_offset)
                break
    if len(hits) != 1:
        raise ValueError(f"0x{va:08x} '{insn.mnemonic} {insn.op_str}': expected one 4-byte "
                         f"operand 0x{old:08x}, found {len(hits)}")
    off = pe_extend.va_to_offset(bytes(out), va) + hits[0]
    if int.from_bytes(out[off : off + 4], "little") != old:
        raise ValueError(f"0x{va:08x}: old operand bytes mismatch")
    out[off : off + 4] = (new & 0xFFFFFFFF).to_bytes(4, "little")
    return f"{insn.mnemonic} {insn.op_str}"


def _window_audit(data: bytes) -> None:
    """Every pool-end / negated-end operand in new code must be classified."""
    known = set(POOL_END_CMP_SITES) | set(POOL_END_NEG_SITES) | set(POOL_END_BULK_SITES) | set(
        DIV_TEST_SITES)
    for name, va, vsize, raw_size, raw_ptr in g2_scan._executable_sections(data):  # noqa: SLF001
        if name in (".text", ".rsrc"):
            continue
        size = min(raw_size, max(vsize, 1)) if vsize else raw_size
        for insn in g2_scan._sweep(data[raw_ptr : raw_ptr + size], va):  # noqa: SLF001
            for op in insn.operands:
                if op.type == x86.X86_OP_IMM:
                    v = op.imm & 0xFFFFFFFF
                    hit = POOL_END <= v < POOL_END + UNIT_STRIDE or v == (-POOL_END) & 0xFFFFFFFF
                elif op.type == x86.X86_OP_MEM:
                    v = op.mem.disp & 0xFFFFFFFF
                    hit = v == (-POOL_END) & 0xFFFFFFFF  # bulk fields as disp are data, kept
                else:
                    continue
                if hit and insn.address not in known:
                    raise ValueError(f"unclassified pool-end operand at 0x{insn.address:08x}: "
                                     f"{insn.mnemonic} {insn.op_str}")


def apply(image: bytes, base_data: bytes, six_base: int, *, clamp: int = STOCK_CAPACITY
          ) -> tuple[bytes, dict[str, Any]]:
    """Apply layer 2 to ``image`` (a layer-1 build of ``base_data``).

    ``base_data`` is the unmodified 2610-line EXE the inventory is taken from;
    ``six_base`` the VA of the relocated six-array block in ``image``.
    """
    if not STOCK_CAPACITY <= clamp <= g2_reloc_2610.CAPACITY:
        raise ValueError(f"clamp must be in [1200, 4093], got {clamp}")
    inv = g2_scan.build_inventory(base_data, require_pinned_base=False)
    _window_audit(base_data)
    geo = g2_reloc_2610._GEO_BY_NAME  # noqa: SLF001
    pack = g2_reloc_2610._PACK_BASE  # noqa: SLF001
    new_pool = six_base + (geo["unit_pool"].new_start - pack)
    new_exist = six_base + (geo["unit_existence"].new_start - pack)
    out = bytearray(image)
    counts = {"relocated": 0, "neg_pool_base": 0, "kept": 0, "pool_end_cmp": 0,
              "pool_end_neg": 0, "exist_end": 0, "div_test": 0, "text_extra": 0}
    exist_end = set(EXIST_END_SITES)
    seen_exist_end = set()
    for site in inv.sites:
        if site.section in (".text", ".rsrc") or site.op_kind == "bound":
            continue
        if site.va in KEEP_SITES:
            counts["kept"] += 1
            continue
        if site.op_kind == "neg_pool_base":
            _patch_operand(out, site.va, site.value, -new_pool)
            counts["neg_pool_base"] += 1
        elif site.va in exist_end:
            if site.value != EXIST_END:
                raise ValueError(f"0x{site.va:08x} listed as exist end but is 0x{site.value:08x}")
            _patch_operand(out, site.va, EXIST_END, new_exist + 2 * clamp, kind="imm")
            seen_exist_end.add(site.va)
            counts["exist_end"] += 1
        else:
            if site.value == EXIST_END:
                raise ValueError(f"0x{site.va:08x}: 0x899A28 must be classified (age base vs "
                                 "exist end)")
            _patch_operand(out, site.va, site.value,
                           g2_reloc_2610.relocate_value(site.value, six_base), kind=site.op_kind)
            counts["relocated"] += 1
    if seen_exist_end != exist_end:
        raise ValueError(f"exist-end sites missing from inventory: {sorted(exist_end - seen_exist_end)}")
    end = new_pool + UNIT_STRIDE * clamp
    for va in POOL_END_CMP_SITES:
        insn = _insn(bytes(out), va)
        old = next(op.imm & 0xFFFFFFFF for op in insn.operands if op.type == x86.X86_OP_IMM)
        if not POOL_END <= old < POOL_END + UNIT_STRIDE:
            raise ValueError(f"0x{va:08x}: not a pool-end sentinel")
        _patch_operand(out, va, old, end + (old - POOL_END), kind="imm")
        counts["pool_end_cmp"] += 1
    for va in POOL_END_NEG_SITES:
        _patch_operand(out, va, (-POOL_END) & 0xFFFFFFFF, -end)
        counts["pool_end_neg"] += 1
    for va in DIV_TEST_SITES:
        _patch_operand(out, va, (-POOL_BASE * DIV_TEST_INV) & 0xFFFFFFFF,
                       -new_pool * DIV_TEST_INV, kind="imm")
        counts["div_test"] += 1
    for va in TEXT_EXTRA_SITES:
        insn = _insn(bytes(out), va)
        old = insn.disp & 0xFFFFFFFF
        _patch_operand(out, va, old, g2_reloc_2610.relocate_value(old, six_base), kind="disp")
        counts["text_extra"] += 1
    for va, disp in TEXT_BULK_RELATIVE:
        new = (g2_reloc_2610.relocate_value(BULK_BASE + disp, six_base) - BULK_BASE) & 0xFFFFFFFF
        have = _insn(bytes(out), va).disp & 0xFFFFFFFF
        if have != disp:  # layer 1 (the accepted stock oracle) already rebased this one
            counts["text_bulk_by_oracle"] = counts.get("text_bulk_by_oracle", 0) + 1
            continue
        _patch_operand(out, va, disp, new, kind="disp")
        counts["text_bulk"] = counts.get("text_bulk", 0) + 1
    # the clear covers every slot (capacity, not clamp: it runs at game start)
    cap = g2_reloc_2610.CAPACITY
    for va, old, new, kind in ((TEXT_BULK_CLEAR_COUNT, STOCK_CAPACITY, cap, "imm"),
                               (TEXT_BULK_CLEAR_EXIST, (-2 * STOCK_CAPACITY) & 0xFFFFFFFF,
                                (-2 * cap) & 0xFFFFFFFF, "disp")):
        ins = _insn(bytes(out), va)
        have = (ins.disp if kind == "disp" else ins.operands[-1].imm) & 0xFFFFFFFF
        if have != new:
            _patch_operand(out, va, old, new, kind=kind)
            counts["text_bulk"] = counts.get("text_bulk", 0) + 1
    result = pe_extend._with_checksum(bytes(out))  # noqa: SLF001
    return result, {
        "schema": "syw2plus.esl2610.g2-newcode.v1",
        "clamp": clamp,
        "new_pool": hex(new_pool),
        "new_exist": hex(new_exist),
        "counts": counts,
        "candidate_sha256": _digest(result),
    }
