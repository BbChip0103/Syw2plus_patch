#!/usr/bin/env python3
"""G2 layer 3 for ESL 2610-line EXEs: grow the 2610 modules' per-unit state to 4093.

Layer 2 (:mod:`patches.esl2610.g2_newcode_2610`) points the 2610 modules at the
relocated unit arrays, but the modules keep ~50 per-unit arrays of their own,
sized to 1200, in their BSS sections.  Hooks derive a slot from any unit
pointer (``(ptr - pool) / 0x758``) and index those arrays without a range
check, so a unit in slot >= 1200 indexes past them.  This layer moves every
such state section to the image tail with each per-unit array *expanded in
place* from 1200 to 4093 entries:

* the new copy of a section keeps the old byte order; everything after a
  per-unit array shifts by that array's growth.  An address ``v`` in the old
  section maps to ``new_start + (v - old_start) + growth of the arrays that
  end at or before v`` (:meth:`StateSection.map`).  Because the object that
  followed an array still follows its (grown) end, an end-of-array sentinel and
  the next object's address map to the same place -- the same property the
  packed six-array layout relies on -- so end-relative loop operands need no
  per-site disambiguation;
* every absolute operand into a moved section, in every code section, is
  rewritten with that map (fail closed on anything that does not decode);
* operands that hold a section address *in a register* and reach another
  object through a displacement (``mov esi,base ... [esi+eax+disp]``) and
  encoded bases (``(slot + base/stride) * stride``) are listed explicitly;
  :func:`audit_register_bases` finds the candidates.

Sections whose per-unit arrays are only used by unreachable code (``.navdata``)
are not moved.  The PSN portrait cache inside the initialised ``.psndata``
and the ``.enc16`` unit list inside a code section are moved as single
sub-ranges instead.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from patches.esl2610 import g2_scan

STOCK_CAPACITY = 1200
CAPACITY = 4093


@dataclass(frozen=True)
class PerUnit:
    name: str
    base: int
    stride: int

    @property
    def end(self) -> int:
        return self.base + self.stride * STOCK_CAPACITY

    @property
    def capacity(self) -> int:
        return ARRAY_CAPACITY.get(self.name, CAPACITY)

    @property
    def growth(self) -> int:
        return self.stride * (self.capacity - STOCK_CAPACITY)


@dataclass(frozen=True)
class StateSection:
    """A module state range moved whole, per-unit arrays expanded in place."""

    name: str
    start: int
    size: int
    arrays: tuple[PerUnit, ...]
    whole: bool = True  # a whole PE section (False: a sub-range inside one)

    @property
    def end(self) -> int:
        return self.start + self.size

    @property
    def tail(self) -> int:
        """Bytes past the end that still belong to the last array.

        Loops over the last array use end-relative operands (``end + field``,
        e.g. ``cmp eax,end+4`` or ``[ecx+end+4]`` with a negative counter).
        When the last array ends the PE section nothing else can live there.
        """
        if self.whole and self.arrays and self.arrays[-1].end == self.end:
            return 0x40
        return 0

    @property
    def new_size(self) -> int:
        return self.size + sum(a.growth for a in self.arrays)

    def contains(self, value: int) -> bool:
        # inclusive end: a sentinel equal to the section end is still ours
        return self.start <= value <= self.end + self.tail

    def map(self, value: int, new_start: int) -> int:
        if not self.contains(value):
            raise ValueError(f"0x{value:08x} outside {self.name}")
        shift = sum(a.growth for a in self.arrays if a.end <= value)
        return new_start + (value - self.start) + shift

    def validate(self) -> None:
        last = self.start
        for arr in self.arrays:
            if arr.base < last or arr.end > self.end:
                raise ValueError(f"{self.name}: {arr.name} overlaps or leaves the range")
            last = arr.end


def _pu(name: str, base: int, stride: int) -> PerUnit:
    return PerUnit(name, base, stride)


# Ranges and per-unit arrays (classification/out_{A,B,C}.json, merged).
STATE_SECTIONS: tuple[StateSection, ...] = (
    StateSection(".wecache", 0x0114C000, 0x4B00, (_pu("we_cache", 0x0114C000, 0x10),)),
    StateSection(".idldata", 0x01158000, 0x2590, (_pu("idl_slot", 0x01158010, 0x08),)),
    # kill_log, its 256x16 table, then the KIL1 load staging copy of both
    StateSection(".killdat", 0x0115C000, 0x14C18, (
        _pu("kill_log", 0x0115C000, 0x20), _pu("kill_stage", 0x01166600, 0x20))),
    StateSection(".rsidle", 0x01171000, 0x4B10, (_pu("rsidle_slot", 0x01171010, 0x10),)),
    StateSection(".mvstate", 0x01182000, 0xBB94, (_pu("mv_state", 0x01182014, 0x28),)),
    StateSection(".hrstate", 0x01193000, 0x13EE0, (
        _pu("hr_xy_list", 0x01193020, 0x04), _pu("hr_unit", 0x011942E0, 0x40))),
    StateSection(".skstate", 0x011AB000, 0x7090, (_pu("sk_unit", 0x011AB010, 0x18),)),
    StateSection(".healst", 0x011BC000, 0xBBA0, (
        _pu("heal_slot", 0x011BC020, 0x18), _pu("heal_id", 0x011C30A0, 0x10))),
    StateSection(".armyst", 0x011D4000, 0x163E0, (_pu("army_slot", 0x011E3360, 0x18),)),
    StateSection(".cpstate", 0x01200000, 0xE110, (
        _pu("cp_a", 0x01200010, 0x1C), _pu("cp_b", 0x01208350, 0x14))),
    StateSection(".bsstate", 0x01230000, 0xBFD8, (_pu("bs_slot", 0x01230458, 0x28),)),
    StateSection(".farmst", 0x01250000, 0x4B68, (_pu("farm_slot", 0x01250068, 0x10),)),
    StateSection(".atkstat", 0x01270000, 0x28D0, (_pu("atk_slot8", 0x01270350, 0x08),)),
    StateSection(".airstat", 0x01280000, 0xB97C, (
        _pu("air_rec28", 0x01280110, 0x1C), _pu("air_handle", 0x01288450, 0x04),
        _pu("air_tgtcnt", 0x01289D50, 0x01), _pu("air_list", 0x0128A20C, 0x04),
        _pu("air_flag", 0x0128B4CC, 0x01))),
    StateSection(".f2data", 0x01604000, 0x8FBC, (
        _pu("sel_list", 0x01604004, 0x04), _pu("f2_flag", 0x0160CB0C, 0x01))),
    StateSection(".n14data", 0x01616000, 0x36CD6C, (
        _pu("n14_M1", 0x0161609C, 0x414), _pu("n14_M2", 0x01747E5C, 0x04),
        _pu("n14_M3", 0x0174911C, 0x08), _pu("n14_M4", 0x0174B69C, 0x02),
        _pu("n14_M5", 0x0174C004, 0x04), _pu("n14_M6", 0x0174D2D4, 0x10),
        _pu("n14_M7", 0x01751DD4, 0x14), _pu("n14_M8", 0x01757B94, 0x1C))),
    # .navcode/.navdata: the older copy of the n14 path module.  Static
    # reachability finds no caller, but nothing proves it dead, so it gets the
    # same treatment as .n14data instead of keeping 1200 gates.
    StateSection(".navdata", 0x01295000, 0x36375C, (
        _pu("nav_N1", 0x0129508C, 0x414), _pu("nav_N2", 0x013C6E4C, 0x04),
        _pu("nav_N3", 0x013C810C, 0x08), _pu("nav_N4", 0x013CA68C, 0x02),
        _pu("nav_N5", 0x013CB004, 0x04), _pu("nav_N6", 0x013CC2C4, 0x10),
        _pu("nav_N7", 0x013D0DC4, 0x10))),
    StateSection(".a16data", 0x01A03000, 0xAA90, (_pu("a16_path", 0x01A03028, 0x20),)),
    StateSection(".r17data", 0x01A13000, 0xA2000, (
        _pu("r17_B", 0x01A13028, 0x1C), _pu("r17_A", 0x01A1D028, 0x1C),
        _pu("r17_27200", 0x01A27200, 0x20), _pu("r17_30900", 0x01A30900, 0x20),
        _pu("r17_f2mark", 0x01A44200, 0x01), _pu("r17_45010", 0x01A45010, 0x10),
        _pu("r17_4a030", 0x01A4A030, 0x0C), _pu("r17_rt48", 0x01A4E010, 0x20),
        _pu("r17_rt50", 0x01A58010, 0x30), _pu("r17_rt50claim", 0x01A66110, 0x08),
        _pu("r17_gr65", 0x01A8B024, 0x10), _pu("r17_tr72", 0x01A91448, 0x1C),
        _pu("r17_kf79", 0x01AA0010, 0x10), _pu("r17_rs86", 0x01AA502C, 0x18))),
    # Sub-ranges: only the per-unit body moves (initialised data / code sections).
    # PSN2 blob 0x1100000 (0x16000, holds the per-slot portrait cache), its
    # load staging copy 0x1116000 and the 16-byte header 0x112C000
    StateSection(".psndata:psn2", 0x01100000, 0x2C010, (
        _pu("psn_cache", 0x0110C000, 0x10), _pu("psn_stage", 0x01122000, 0x10)), whole=False),
    StateSection(".enc16:list", 0x01141000, 0x12C0, (_pu("enc16_list", 0x01141000, 0x04),),
                 whole=False),
)


def section_for(value: int) -> StateSection | None:
    for sec in STATE_SECTIONS:
        if sec.contains(value):
            return sec
    return None


# Arrays whose base is also encoded divided by a constant (``(slot + base/m)*m``):
# the new base must stay a multiple of m.  (array name, m, encoding sites)
ENCODED_BASES = (
    ("sk_unit", 0x18, (0x011A79E7,)),
    ("heal_slot", 0x18, (0x011B7D3C,)),
    ("heal_id", 0x10, (0x011B78ED, 0x011B7F42, 0x011B8213)),
    ("psn_cache", 0x10, (0x011A7D26,)),
)

# Per-array capacity where a clear loop is unrolled (count must be a multiple).
ARRAY_CAPACITY = {"r17_B": 4095, "f2_flag": 4096, "a16_path": 4096, "sel_list": 4096}


def _array(name: str) -> tuple[StateSection, PerUnit]:
    for sec in STATE_SECTIONS:
        for arr in sec.arrays:
            if arr.name == name:
                return sec, arr
    raise KeyError(name)


def layout(base: int) -> dict[str, int]:
    """New start VA per state section, packed from ``base``.

    Each start is 0x100-aligned and then nudged (4-byte steps) until every
    encoded base in that section lands on its required multiple.
    """
    out: dict[str, int] = {}
    cursor = base
    for sec in STATE_SECTIONS:
        sec.validate()
        cursor = (cursor + 0xFF) & ~0xFF
        need = [(_array(n)[1], m) for n, m, _ in ENCODED_BASES if _array(n)[0] is sec]
        for _ in range(0x1000):
            if all(sec.map(arr.base, cursor) % m == 0 for arr, m in need):
                break
            cursor += 4
        else:
            raise ValueError(f"{sec.name}: no start satisfies the encoded-base alignment")
        out[sec.name] = cursor
        cursor += sec.new_size
    out["__end__"] = cursor
    return out


def map_value(value: int, starts: dict[str, int]) -> int:
    sec = section_for(value)
    if sec is None:
        raise ValueError(f"0x{value:08x} is not in a moved state range")
    return sec.map(value, starts[sec.name])


def absolute_refs(data: bytes, sections: Iterable[str] | None = None):
    """Yield (section, insn, kind, value) for every disp/imm into a moved range."""
    from capstone import x86

    for name, va, vsize, raw_size, raw_ptr in g2_scan._executable_sections(data):  # noqa: SLF001
        if sections is not None and name not in sections:
            continue
        size = min(raw_size, max(vsize, 1)) if vsize else raw_size
        for insn in g2_scan._sweep(data[raw_ptr : raw_ptr + size], va):  # noqa: SLF001
            for op in insn.operands:
                if op.type == x86.X86_OP_IMM:
                    kind, value = "imm", op.imm & 0xFFFFFFFF
                elif op.type == x86.X86_OP_MEM:
                    kind, value = "disp", op.mem.disp & 0xFFFFFFFF
                else:
                    continue
                if section_for(value) is not None:
                    yield name, insn, kind, value


def register_base_uses(data: bytes, window: int = 60):
    """Find ``[reg + disp]`` uses where ``reg`` holds an image address.

    Yields (section, load_insn, use_insn, base_value, disp).  A use is reported
    when the old target ``base + disp`` does not keep its distance to ``base``
    under the address map: a moved base whose target crosses a grown array or
    leaves the range, or a base that does not move (e.g. a bulk record at
    0x893130) whose displacement reaches into a moved range.  Such a
    displacement is relative, never an absolute address.  The forward scan
    stops when ``reg`` is written or control leaves linearly.
    """
    from capstone import x86

    starts = layout(0x02000000)

    def moved(value: int) -> int:
        sec = section_for(value)
        return value if sec is None else sec.map(value, starts[sec.name])

    for name, va, vsize, raw_size, raw_ptr in g2_scan._executable_sections(data):  # noqa: SLF001
        size = min(raw_size, max(vsize, 1)) if vsize else raw_size
        insns = list(g2_scan._sweep(data[raw_ptr : raw_ptr + size], va))  # noqa: SLF001
        for k, ins in enumerate(insns):
            if ins.mnemonic not in ("mov", "lea") or len(ins.operands) != 2:
                continue
            dst, src = ins.operands
            if dst.type != x86.X86_OP_REG:
                continue
            if src.type == x86.X86_OP_IMM and ins.mnemonic == "mov":
                base = src.imm & 0xFFFFFFFF
            elif (src.type == x86.X86_OP_MEM and ins.mnemonic == "lea" and src.mem.base == 0
                  and src.mem.index == 0):
                base = src.mem.disp & 0xFFFFFFFF
            else:
                continue
            if not 0x00400000 <= base < 0x03000000:
                continue
            base_moves = section_for(base) is not None
            reg = dst.reg
            for use in insns[k + 1 : k + 1 + window]:
                for op in use.operands:
                    if (op.type == x86.X86_OP_MEM and op.mem.disp != 0
                            and (op.mem.base == reg
                                 or (op.mem.index == reg and op.mem.scale == 1))):
                        disp = op.mem.disp
                        target = (base + disp) & 0xFFFFFFFF
                        if not base_moves and section_for(target) is None:
                            continue
                        if moved(target) - moved(base) != disp:
                            yield name, ins, use, base, disp
                if use.mnemonic in ("ret", "jmp") or reg in use.regs_access()[1]:
                    break


# Signed/unsigned "x / 1200" ring-cursor divisions (mov r,0x1B4E81B5 ... sar/shr edx,7).
# 0x400C0241 >> (32+10) is exact for x / 4093 on 0..2**20 and fits a signed imul.
DIV_MAGIC_OLD, DIV_MAGIC_NEW = 0x1B4E81B5, 0x400C0241
DIV_SHIFT_OLD, DIV_SHIFT_NEW = 7, 10
DIV_SITES = (0x01292F26, 0x01292F74, 0x01613546, 0x01613594, 0x019D09ED, 0x01A01966,
             0x01A0EA7C, 0x01A11966)


# Byte/dword lengths of the 2610 modules' fixed save blobs and clears, which
# now cover grown per-unit arrays.  (va, old, unit, (from, to)): new value =
# (map(to) - map(from)) / unit.  The blobs keep their magic/version; the grown
# size makes the official EXE reject an expanded blob (it then clears/rebuilds,
# as for a damaged blob) and the KIL1 legacy size is converted in layer 4.
KILL_FROM, KILL_TO = 0x0115C000, 0x01166600  # kill_log + 256x16 table (KIL1 blob)
PSN_FROM, PSN_TO = 0x01100000, 0x01116000  # PSN2 blob
BLOB_LENGTHS = (
    (0x0115B3EB, 0xA600, 1, (KILL_FROM, KILL_TO)),  # KIL1 header size (save)
    (0x0115B3F7, 0xA600, 1, (KILL_FROM, KILL_TO)),  # KIL1 hash length (save)
    (0x0115B41D, 0xA600, 1, (KILL_FROM, KILL_TO)),  # KIL1 write length
    (0x0115B491, 0xA600, 1, (KILL_FROM, KILL_TO)),  # KIL1 read length
    (0x0115B4AD, 0xA600, 1, (KILL_FROM, KILL_TO)),  # KIL1 hash length (load)
    (0x0115B4C7, 0x2980, 4, (KILL_FROM, KILL_TO)),  # KIL1 stage -> kill_log copy
    (0x0115B28A, 0x2980, 4, (KILL_FROM, KILL_TO)),  # new game / pre-load clear
    (0x01091043, 0x16000, 1, (PSN_FROM, PSN_TO)),  # PSN2 hash length
    (0x0109107B, 0x16000, 1, (PSN_FROM, PSN_TO)),  # PSN2 header size (save)
    (0x010910AE, 0x16000, 1, (PSN_FROM, PSN_TO)),  # PSN2 write length
    (0x01091108, 0x16000, 1, (PSN_FROM, PSN_TO)),  # PSN2 header size check (load)
    (0x01091117, 0x16000, 1, (PSN_FROM, PSN_TO)),  # PSN2 read length
    (0x01090DB8, 0x5800, 4, (PSN_FROM, PSN_TO)),  # PSN2 new-game clear
    (0x0109114B, 0x5800, 4, (PSN_FROM, PSN_TO)),  # PSN2 stage -> blob copy
)
# (0x115B485, the KIL1 header size check, is rerouted by layer 4 so that both
# the grown and the official size load.)


def blob_length(pair: tuple[int, int], starts: dict[str, int]) -> int:
    return map_value(pair[1], starts) - map_value(pair[0], starts)


# Initialised data holding a moved address (aligned dword scan of every
# non-code section; all other hits are byte-identical to the stock EXE, i.e.
# not 2610 pointers).  0x4F8FF0 is .sel60's selection-buffer pointer.
DATA_POINTERS = {0x004F8FF0: 0x01604004}


# Three .a16code functions dedupe roster ids in a 38-dword (1216-bit) stack
# bitset; for ids up to 4092 the bitset grows downward by 0x200 bytes:
# (frame sub/add sites, frame size, clear-counter sites, bitset disp sites, base disp)
STACK_BITSETS = (
    ((0x019B1243, 0x019B138E), 0xA0, (0x019B1261,), (0x019B12B2, 0x019B12D8), -0xAC),
    ((0x019B14C9, 0x019B18FE), 0xB4, (0x019B1586, 0x019B182D),
     (0x019B15FA, 0x019B1608, 0x019B1880, 0x019B18A9), -0xC0),
    ((0x019DE806, 0x019DEB73), 0xB4, (0x019DE857,), (0x019DE8A6, 0x019DE8B9), -0xC0),
)
STACK_BITSET_GROW = 0x200
STACK_BITSET_CLEAR = -0x98


def _moved(value: int, starts: dict[str, int], *, tail: int = 0) -> int:
    """Map ``value`` if it is in a moved range (or within ``tail`` past its end)."""
    sec = section_for(value)
    if sec is not None:
        return sec.map(value, starts[sec.name])
    if tail:
        for cand in STATE_SECTIONS:
            if cand.end < value <= cand.end + tail and cand.arrays[-1].end == cand.end:
                return cand.map(cand.end, starts[cand.name]) + (value - cand.end)
    return value


def block_size() -> int:
    starts = layout(0)
    return starts["__end__"]


def apply(image: bytes, base_data: bytes, state_base: int) -> tuple[bytes, dict]:
    """Move the module state to ``state_base`` and raise every capacity constant.

    ``image`` is a layer-1+2 build of ``base_data`` whose ``.g2bss`` has room
    for :func:`block_size` bytes at ``state_base``.
    """
    import hashlib

    from patches.esl2610 import g2_bounds_2610, pe_extend
    from patches.esl2610.g2_newcode_2610 import _insn, _patch_operand

    starts = layout(state_base)
    out = bytearray(image)
    counts = {"absolute": 0, "regbase": 0, "encoded": 0, "raise": 0, "div": 0}
    uses = list(register_base_uses(base_data))
    relative = {(u.address, d & 0xFFFFFFFF) for _, _, u, _, d in uses}
    # 1. absolute operands into moved ranges, every code section
    for name, insn, kind, value in absolute_refs(base_data):
        if insn.mnemonic in ("call", "jmp") or insn.mnemonic.startswith("j"):
            continue  # linear-sweep misdecode of data inside a code section
        if kind == "disp" and (insn.address, value) in relative:
            counts["absolute_skipped_relative"] = counts.get("absolute_skipped_relative", 0) + 1
            continue  # a displacement off a base register: step 2
        _patch_operand(out, insn.address, value, _moved(value, starts), kind=kind)
        counts["absolute"] += 1
    # 2. displacements off a moved base held in a register
    seen: dict[tuple[int, int], int] = {}
    for name, load, use, base, disp in uses:
        key = (use.address, disp & 0xFFFFFFFF)
        if key in seen:
            if seen[key] != base:  # two loads reach one use with different bases
                raise ValueError(f"0x{use.address:08x}: ambiguous base register value")
            continue
        seen[key] = base
        target = (base + disp) & 0xFFFFFFFF
        new = _moved(target, starts, tail=0x40) - _moved(base, starts)
        _patch_operand(out, use.address, disp & 0xFFFFFFFF, new, kind="disp")
        counts["regbase"] += 1
    # 3. bases encoded divided by a constant
    for arr_name, m, sites in ENCODED_BASES:
        sec, arr = _array(arr_name)
        old, new = arr.base // m, sec.map(arr.base, starts[sec.name]) // m
        for va in sites:
            _patch_operand(out, va, old, new)
            counts["encoded"] += 1
    # 4. capacity constants (gates, spans, loop/clear lengths)
    regbase_vas = {u.address for _, _, u, _, _ in uses}
    table = g2_bounds_2610.build_table(base_data, regbase_vas)
    for row in table:
        if row["decision"] != "raise":
            continue
        insn = _insn(bytes(out), row["va"])
        if row["size"] == 4:
            _patch_operand(out, row["va"], row["old"], row["new"], kind=row["kind"])
        else:
            off = pe_extend.va_to_offset(bytes(out), row["va"]) + (
                insn.imm_offset if row["kind"] == "imm" else insn.disp_offset)
            if int.from_bytes(out[off : off + 2], "little") != row["old"] & 0xFFFF:
                raise ValueError(f"0x{row['va']:08x}: 16-bit operand mismatch")
            out[off : off + 2] = (row["new"] & 0xFFFF).to_bytes(2, "little")
        counts["raise"] += 1
    # 4a. stock .text capacity operands the oracle left at 1200
    text_rows = g2_bounds_2610.text_table(base_data, image)
    for row in text_rows:
        if row["decision"] != "raise":
            continue
        insn = _insn(bytes(out), row["va"])
        if row["size"] == 4:
            _patch_operand(out, row["va"], row["old"], row["new"], kind=row["kind"])
        else:
            off = pe_extend.va_to_offset(bytes(out), row["va"]) + (
                insn.imm_offset if row["kind"] == "imm" else insn.disp_offset)
            if int.from_bytes(out[off : off + 2], "little") != row["old"] & 0xFFFF:
                raise ValueError(f"0x{row['va']:08x}: 16-bit operand mismatch")
            out[off : off + 2] = (row["new"] & 0xFFFF).to_bytes(2, "little")
        counts["text_raise"] = counts.get("text_raise", 0) + 1
    # 4b. fixed save-blob / clear lengths that now cover grown arrays
    for va, old, unit, pair in BLOB_LENGTHS:
        length = blob_length(pair, starts)
        if length % unit:
            raise ValueError(f"0x{va:08x}: blob length 0x{length:x} not a multiple of {unit}")
        _patch_operand(out, va, old, length // unit, kind="imm")
        counts["blob_length"] = counts.get("blob_length", 0) + 1
    # 5. pointers stored in initialised data
    for va, old in DATA_POINTERS.items():
        off = pe_extend.va_to_offset(bytes(out), va)
        if int.from_bytes(out[off : off + 4], "little") != old:
            raise ValueError(f"data pointer at 0x{va:08x} does not hold 0x{old:08x}")
        out[off : off + 4] = _moved(old, starts).to_bytes(4, "little")
        counts["data_ptr"] = counts.get("data_ptr", 0) + 1
    # 6. widen the roster-dedupe stack bitsets (their gates are raised in 4.)
    for frame_sites, frame, clears, disps, base in STACK_BITSETS:
        for va in frame_sites:
            _patch_operand(out, va, frame, frame + STACK_BITSET_GROW, kind="imm")
        for va in clears:
            _patch_operand(out, va, STACK_BITSET_CLEAR & 0xFFFFFFFF,
                           (STACK_BITSET_CLEAR - STACK_BITSET_GROW) & 0xFFFFFFFF, kind="imm")
        for va in disps:
            _patch_operand(out, va, base & 0xFFFFFFFF, (base - STACK_BITSET_GROW) & 0xFFFFFFFF,
                           kind="disp")
        counts["stack_bitset"] = counts.get("stack_bitset", 0) + 1
    # 7. divide-by-1200 ring cursors
    for va in DIV_SITES:
        _patch_operand(out, va, DIV_MAGIC_OLD, DIV_MAGIC_NEW, kind="imm")
        cur = va
        for _ in range(6):
            ins = _insn(bytes(out), cur)
            if (ins.mnemonic in ("sar", "shr") and ins.op_str == "edx, 7"):
                off = pe_extend.va_to_offset(bytes(out), cur) + ins.imm_offset
                out[off] = DIV_SHIFT_NEW
                break
            cur += ins.size
        else:
            raise ValueError(f"0x{va:08x}: no 'shr/sar edx,7' after the magic")
        counts["div"] += 1
    result = pe_extend._with_checksum(bytes(out))  # noqa: SLF001
    return result, {
        "schema": "syw2plus.esl2610.g2-state.v1",
        "state_base": hex(state_base),
        "starts": {k: hex(v) for k, v in starts.items()},
        "counts": counts,
        "text_table": {d: sum(r["decision"] == d for r in text_rows)
                       for d in ("oracle", "raise", "keep", "layer2")},
        "table": {"raise": sum(r["decision"] == "raise" for r in table),
                  "keep": sum(r["decision"] == "keep" for r in table),
                  "regbase": sum(r["decision"] == "regbase" for r in table)},
        "candidate_sha256": hashlib.sha256(result).hexdigest(),
    }
