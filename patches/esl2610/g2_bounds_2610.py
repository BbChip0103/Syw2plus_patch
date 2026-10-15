#!/usr/bin/env python3
"""Capacity-constant table for the G2 4093 layer 3 on ESL 2610-line EXEs.

Every operand in a 2610-new code section whose value belongs to the 1200
family (``k*1200 + c`` and its negation, 32- and 16-bit, plus the last-slot
byte offset ``1199*0x758``) gets exactly one decision:

* ``raise`` -- a unit slot/id gate, a pool byte-span, a loop/clear length over a
  grown per-unit array: the value becomes ``k*cap + c`` with the same sign;
* ``keep`` -- not unit capacity (score/timer constants, the per-player roster
  in the player struct, the 1200-entry selection list kept at 1200, stack
  bitsets whose gates must stay at 1200);
* ``regbase`` -- an end-relative displacement off a section base held in a
  register; :mod:`g2_state_2610` rewrites those from the address map.

Decisions come from the per-module static classification
(``analysis/esl2610/g2_classification_{A,B,C}.json``, three independent
read-only passes over all new sections) plus the explicit overrides below.
:func:`build_table` fails closed on any family operand without a decision.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from capstone import x86

from patches.esl2610 import g2_scan

STOCK = 1200
CAPACITY = 4093
ANALYSIS = Path(__file__).resolve().parents[2] / "analysis" / "esl2610"
STRIDE = g2_scan.UNIT_STRIDE

# Sections whose per-unit state is not grown (only dead code uses it): all of
# their capacity constants stay.
FROZEN_SECTIONS: set[str] = set()  # none: .navdata is grown like .n14data

# Arrays whose clear loops need a capacity that is a multiple of the unroll.
CAP_OVERRIDE = {
    0x01A11581: 4095,  # r17_B clear loop, 3 entries per pass
    0x0160174C: 4096,  # f2_flag clear, 8 per pass (dead code today)
    0x01A017D2: 4096,  # a16_path clear loop, 4 entries per pass
}
# The selection list 0x1604004 stays at 1200 entries: classification rows
# that only guard it are kept.
SELECTION_LIST_NAMES = {"sel_list_d4", "f2_list_1604004"}

# Keep at 1200 although a classification said raise.
# The selection buffer 0x1604004 (stock 1200 entries, moved by ESL into
# .f2data) is filled by whole-army selects (a16 select-all 0x19C5800 walks all
# slots and inserts until the buffer end), so it grows with the pool; its
# clear loops step 8 entries, so its capacity is 4096.  The selection cap the
# player can drag (official 100) is a different limit and is untouched.
SELECTION_CAPACITY = 4096
SELECTION_SITES = {
    0x019A70B8, 0x019C50B8, 0x019A7359, 0x019C5377, 0x019A7480, 0x019A7497,
    0x019C54A0, 0x019C54B4, 0x019C57E2,  # a16 walks/clear of the buffer
    0x0113420A, 0x0113463C,  # .grp60 clears of the buffer (1200 dwords)
}
KEEP_OVERRIDE = {
    # (the three live roster-dedupe stack bitsets are widened by g2_state_2610,
    # so their gates 0x19B1294/0x19B15CF/0x19B1862/0x19DE886 are raised)
    # family values that are not unit capacity (reviewed in context)
    0x01153000: "hook argument check 0x18060", 0x011547B2: "180*180 vision stride",
    0x016026AA: "bulk field 0x892FF8 vs 6000", 0x0161146E: "bulk field 0x892FF8 vs 6000",
    0x016134B5: "score/distance init 6000", 0x019C2DFF: "180*180 map grid offset",
    0x0129143A: "bulk field 0x892FF8 vs 6000 (nav copy of 0x161146E)",
    0x01292E95: "score/distance init 6000 (nav copy of 0x16134B5)",
}
# Raise although no classification row names the instruction.
RAISE_EXTRA = {
    0x01157057: "rep stosd idl_slot body: 2 dwords x 1200",
    0x0115791E: "rep stosd .rsidle header+body: 4 + 4 dwords x 1200",
}


def _family() -> dict[int, tuple[int, int, str, int]]:
    """value -> (k, c, sign, n) with value == sign*(k*n + c)."""
    fam: dict[int, tuple[int, int, str, int]] = {}
    ks = list(range(1, 0x81)) + [0x414, STRIDE]
    for n in (STOCK, STOCK - 1):
        for k in ks:
            for c in ((0, -1, -2, 1, 2, 3, 4) if n == STOCK else (0,)):
                v = k * n + c
                if v < 0x400 or (n == STOCK - 1 and k != STRIDE):
                    continue
                for value, sign in ((v, "+"), ((-v) & 0xFFFFFFFF, "-"), ((-v) & 0xFFFF, "-16")):
                    fam.setdefault(value, (k, c, sign, n))
    return fam


FAMILY = _family()
# Clear-loop starts that also cover a small header: -(header + k*1200).
FAMILY.update({
    0xFFFFB4F0: (0x10, 0x10, "-", STOCK),  # r17 0x1a45000: 0x10 + 1200*0x10
    0xFFFFC790: (0x0C, 0x30, "-", STOCK),  # r17 0x1a4a000: 0x30 + 1200*0xc
    0xFFFF69F0: (0x20, 0x10, "-", STOCK),  # RT48: 0x10 + 1200*0x20
    0xFFFEF970: (0x38, 0x10, "-", STOCK),  # RT50+claim: 0x10 + 1200*(0x30+8)
})


def new_value(old: int, cap: int = CAPACITY) -> int:
    k, c, sign, n = FAMILY[old]
    m = cap if n == STOCK else cap - 1
    v = k * m + c
    if sign == "+":
        return v
    if sign == "-":
        return (-v) & 0xFFFFFFFF
    return (-v) & 0xFFFF


def _classified() -> dict[int, dict[str, Any]]:
    out: dict[int, dict[str, Any]] = {}
    for part in "ABC":
        doc = json.loads((ANALYSIS / f"g2_classification_{part}.json").read_text())
        for row in doc["bound_sites"]:
            out[int(str(row["va"]), 16)] = {**row, "part": part}
    return out


def family_operands(data: bytes):
    """Yield (section, insn, kind, value, size) for every 1200-family operand."""
    for name, va, vsize, raw_size, raw_ptr in g2_scan._executable_sections(data):  # noqa: SLF001
        if name in (".text", ".rsrc"):
            continue
        size = min(raw_size, max(vsize, 1)) if vsize else raw_size
        for insn in g2_scan._sweep(data[raw_ptr : raw_ptr + size], va):  # noqa: SLF001
            for op in insn.operands:
                if op.type == x86.X86_OP_IMM:
                    kind, value, osz = "imm", op.imm & 0xFFFFFFFF, insn.imm_size
                elif op.type == x86.X86_OP_MEM:
                    kind, value, osz = "disp", op.mem.disp & 0xFFFFFFFF, insn.disp_size
                else:
                    continue
                if value not in FAMILY:
                    continue
                # "-16" values also appear as 32-bit immediates after movzx r,r16
                # (only the negative-looking ones, e.g. cmp ecx,0xFB51)
                if FAMILY[value][2] == "-16" and osz != 2 and value < 0xF000:
                    continue
                if FAMILY[value][2] != "-16" and osz not in (4, 2):
                    continue
                if osz == 2 and FAMILY[value][2] == "-":
                    continue
                yield name, insn, kind, value, osz


def build_table(data: bytes, regbase_vas: set[int],
                extra_decisions: dict[int, dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Decide every family operand; raise ValueError listing undecided ones.

    ``extra_decisions`` is an opt-in, version-profile table for a caller that
    has independently mapped new code. Each row must include the exact old
    operand, size, kind, decision, and a rationale. It cannot override an
    existing classification and every supplied address must be consumed.
    The default (2610) path is unchanged.
    """
    cls = _classified()
    extra = dict(extra_decisions or {})
    rows: list[dict[str, Any]] = []
    undecided = []
    prev: list[Any] = []
    for name, insn, kind, value, osz in family_operands(data):
        row = {"va": insn.address, "section": name, "insn": f"{insn.mnemonic} {insn.op_str}",
               "kind": kind, "old": value, "size": osz}
        hit = cls.get(insn.address)
        # second half of "lea r,[x-0x4b0] ; cmp r,-0x4af" pairs carries the lea's verdict
        pair = next((cls[p.address] for p in prev[-3:] if p.address in cls
                     and insn.address - 16 <= p.address < insn.address), None)
        if name in FROZEN_SECTIONS:
            row.update(decision="keep", why="frozen section (dead code, state not grown)")
        elif insn.address in SELECTION_SITES or (
                hit is not None and hit.get("arrays_guarded")
                and set(hit["arrays_guarded"]) <= SELECTION_LIST_NAMES):
            row.update(decision="raise", why="selection buffer grows with the pool", cap=SELECTION_CAPACITY)
        elif insn.address in KEEP_OVERRIDE:
            row.update(decision="keep", why=KEEP_OVERRIDE[insn.address])
        elif insn.address in RAISE_EXTRA:
            row.update(decision="raise", why=RAISE_EXTRA[insn.address])
        elif kind == "disp" and insn.address in regbase_vas:
            row.update(decision="regbase", why="end-relative disp off a section base register")
        elif hit is not None:
            if hit["action"].startswith("raise"):
                row.update(decision="raise", why=f"{hit['part']}:{hit['action']}:{hit.get('value_kind')}")
            else:
                row.update(decision="keep", why=f"{hit['part']}:{hit['why'][:80]}")
        elif pair is not None and pair["action"].startswith("raise") and insn.mnemonic == "cmp":
            row.update(decision="raise", why=f"pair of {pair['part']}:{pair['va']}")
        elif pair is not None and not pair["action"].startswith("raise"):
            row.update(decision="keep", why=f"pair of keep {pair['va']}")
        elif insn.address in extra:
            decision = extra.pop(insn.address)
            required = {"old", "size", "kind", "decision", "why"}
            if not required <= decision.keys():
                raise ValueError(f"0x{insn.address:08x}: incomplete explicit capacity decision")
            if (decision["old"] != value or decision["size"] != osz
                    or decision["kind"] != kind):
                raise ValueError(f"0x{insn.address:08x}: explicit decision preimage mismatch")
            if decision["decision"] not in ("raise", "keep") or not str(decision["why"]).strip():
                raise ValueError(f"0x{insn.address:08x}: invalid explicit capacity decision")
            if "capacity" in decision and (not isinstance(decision["capacity"], int)
                                               or not 1 <= decision["capacity"] <= 0xFFFF):
                raise ValueError(f"0x{insn.address:08x}: invalid explicit capacity")
            row.update(decision=decision["decision"], why=decision["why"])
            if "capacity" in decision:
                row["capacity"] = decision["capacity"]
        else:
            undecided.append(row)
            prev.append(insn)
            continue
        if row["decision"] == "raise":
            cap = row.pop("cap", None) or row.pop("capacity", None) or CAP_OVERRIDE.get(insn.address, CAPACITY)
            row["new"] = new_value(value, cap)
        rows.append(row)
        prev.append(insn)
        prev = prev[-4:]
    if undecided:
        lines = "\n".join(f"  0x{r['va']:08x} {r['section']} {r['insn']}" for r in undecided)
        raise ValueError(f"{len(undecided)} undecided 1200-family operands:\n{lines}")
    if extra:
        addresses = ", ".join(f"0x{va:08x}" for va in sorted(extra))
        raise ValueError(f"unused explicit capacity decisions: {addresses}")
    return rows


# --- .text (stock code) -----------------------------------------------------
# Every .text operand of the 1200 families that can carry a unit capacity
# (k*1200 + c for k in 1, 2, 4 -- slots, existence/age words, list dwords --
# and the pool byte span) is either rewritten by the accepted stock oracle
# (layer 1), raised here, or kept with a recorded reason.  Anything else fails.
TEXT_FAMILY_K = (1, 2, 4, STRIDE)
TEXT_RAISE = {
    0x004183A8: "unit ring cursor: (cursor+1) mod 1200 (idiv ecx)",
    0x004183BE: "unit ring cursor: (cursor+i) mod 1200 (idiv ecx)",
    0x00418425: "unit ring cursor: scan length over all slots",
    0x00422DC7: "game init: construct every UnitStruct in the pool (0x4119F0)",
    0x00444F8A: "slot loop: first matching unit of the local player",
}
TEXT_KEEP = {
    0x0043EE37: "per-player roster count (+0x200A) vs roster capacity 1200 (> official cap 1008)",
    0x00417C3D: "event counter [0xB64FDC] vs 2400, not slot indexed",
    0x00417C96: "event counter [0xB64FDC] vs 2400, not slot indexed",
    0x004C470F: "table of 500..1600 step 100 (values, not a capacity)",
    0x004C4763: "table value 2400", 0x004C4850: "table value 4800",
    0x004C4BB6: "table field offset 0x960", 0x004C5598: "table field offset 0x4B0",
    0x004C5DCC: "table field offset 0x12C0",
    0x004CBA29: "UI object stride 0x4B4", 0x004CBA69: "UI object stride 0x4B4",
    0x004CBAEB: "UI object size 0x4B4", 0x004CBB9A: "UI object size 0x4B4",
    0x004CBCBA: "UI object size 0x4B4", 0x004CBDE3: "UI object stride 0x4B4",
}
TEXT_KEEP_PUSH_RANGE = (0x0049D000, 0x004A8DB0)  # effect/sprite creation arguments


def text_table(base: bytes, layer1: bytes) -> list[dict[str, Any]]:
    """Decide every unit-capacity-shaped .text operand (see TEXT_FAMILY_K)."""
    from patches.esl2610 import pe_extend

    name, va, vsize, raw_size, raw_ptr = next(
        s for s in g2_scan._executable_sections(base) if s[0] == ".text")  # noqa: SLF001
    rows, undecided = [], []
    for insn in g2_scan._sweep(base[raw_ptr : raw_ptr + raw_size], va):  # noqa: SLF001
        for op in insn.operands:
            if op.type == x86.X86_OP_IMM:
                kind, value, osz = "imm", op.imm & 0xFFFFFFFF, insn.imm_size
            elif op.type == x86.X86_OP_MEM:
                kind, value, osz = "disp", op.mem.disp & 0xFFFFFFFF, insn.disp_size
            else:
                continue
            fam = FAMILY.get(value)
            if fam is None or fam[0] not in TEXT_FAMILY_K or osz not in (2, 4):
                continue
            if fam[2] == "-16" and osz != 2 and value < 0xF000:
                continue
            off = pe_extend.va_to_offset(base, insn.address)
            row = {"va": insn.address, "insn": f"{insn.mnemonic} {insn.op_str}", "kind": kind,
                   "old": value, "size": osz}
            if base[off : off + insn.size] != layer1[off : off + insn.size]:
                row.update(decision="oracle", why="rewritten by the accepted stock G2 (layer 1)")
            elif insn.address in TEXT_RAISE:
                row.update(decision="raise", why=TEXT_RAISE[insn.address],
                           new=new_value(value, CAPACITY))
            elif insn.address in TEXT_KEEP:
                row.update(decision="keep", why=TEXT_KEEP[insn.address])
            elif (insn.mnemonic == "push" and TEXT_KEEP_PUSH_RANGE[0] <= insn.address
                  < TEXT_KEEP_PUSH_RANGE[1]):
                row.update(decision="keep", why="effect/sprite creation argument")
            elif insn.address in (0x004A3222, 0x004A3227):
                row.update(decision="layer2", why="game-start exist/age clear (layer 2)")
            else:
                undecided.append(row)
                continue
            rows.append(row)
    if undecided:
        lines = "\n".join(f"  0x{r['va']:08x} {r['insn']}" for r in undecided)
        raise ValueError(f"{len(undecided)} undecided .text capacity operands:\n{lines}")
    return rows
