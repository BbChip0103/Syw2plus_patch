#!/usr/bin/env python3
"""lap381 middle read-only probe: close C1 (count width) and test H1 (0xC80 gap).

lap380's escalation asked to settle C1 "from original bytes".  The lap381 tail
probe established that every one of the six storage regions lives in .data BSS
(all above raw_end 0x4f9000), so the addresses in question have **no bytes in the
file at all**.  The only original-byte evidence that exists is the code that
touches them: the x86 operand-size of each access.

C1 asks whether 0x0089C2C8 is a DWORD count (which would overlap the low two
bytes of category_slot_list_b[0] at 0x0089C2CA) or a WORD count (which fits the
2-byte gap exactly).  A 0x66 operand-size prefix, a WORD register operand, or a
movzx/movsx r32, word ptr form settles it.

H1 asks whether the 0xC80 = 3200 B gap at 0x0089A388..0x0089B008 is the fixed
8 x 200 WORD matrix.  Size coincidence is not evidence; the access width and the
span of distinct referenced addresses inside the gap are.

Reads bytes only.  Never writes, never patches, never launches the game.
"""

from __future__ import annotations

import hashlib
import struct
from collections import defaultdict
from pathlib import Path

from capstone import CS_ARCH_X86, CS_MODE_32, Cs
from capstone.x86 import X86_OP_MEM

REPO = Path(__file__).resolve().parents[4]
ORIGINAL = REPO / "Syw2plus/syw2plus_original.exe"
ORIGINAL_SHA256 = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"

IMAGE_BASE = 0x400000

# C1 targets: the list-A end/count alias and the list-B base two bytes above it,
# plus the same-shaped alias at the list-B end.
CAT_A_BASE = 0x0089B008
CAT_A_END_COUNT = 0x0089C2C8
CAT_B_BASE = 0x0089C2CA
CAT_B_END_COUNT = 0x0089D58A

# H1 target: the gap between unit_age end and category_slot_list_a base.
AGE_END = 0x0089A388
GAP_END = 0x0089B008
GAP_SIZE = GAP_END - AGE_END

# The active_slot_list end carries the same end/count alias shape; it is included
# so the verdict covers the whole family rather than one instance.
ACTIVE_SLOT_END_COUNT = 0x00975908

C1_TARGETS = {
    "cat_a_base": CAT_A_BASE,
    "cat_a_end_count": CAT_A_END_COUNT,
    "cat_b_base": CAT_B_BASE,
    "cat_b_end_count": CAT_B_END_COUNT,
    "active_slot_end_count": ACTIVE_SLOT_END_COUNT,
}

failures: list[str] = []


def check(name: str, condition: bool, detail: str) -> None:
    print(f"[{'PASS' if condition else 'FAIL'}] {name}: {detail}")
    if not condition:
        failures.append(name)


def load_text_section(data: bytes) -> tuple[int, bytes]:
    """Return (virtual address, bytes) of .text."""
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    nsec = struct.unpack_from("<H", data, pe + 6)[0]
    optsz = struct.unpack_from("<H", data, pe + 20)[0]
    sec_table = pe + 24 + optsz
    for i in range(nsec):
        off = sec_table + i * 40
        name = data[off : off + 8].rstrip(b"\0").decode("ascii", "replace")
        vsz, va, rsz, rp = struct.unpack_from("<IIII", data, off + 8)
        if name == ".text":
            return IMAGE_BASE + va, data[rp : rp + min(rsz, vsz + 0x1000)]
    raise SystemExit("no .text section")


def recover_instructions(text_va: int, text: bytes, literal: int) -> list:
    """Find instructions whose memory operand displacement equals `literal`.

    Scans for the 4-byte little-endian literal, then walks back up to 15 bytes
    looking for a decode whose extent covers the literal and whose memory operand
    really resolves to it.  This avoids trusting a single linear disassembly pass
    over a section that also contains data and alignment padding.
    """
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    md.detail = True
    needle = struct.pack("<I", literal)
    candidates: list = []
    seen: set[int] = set()
    pos = text.find(needle)
    while pos != -1:
        for back in range(1, 16):
            start = pos - back
            if start < 0:
                break
            try:
                insn = next(md.disasm(text[start : start + 16], text_va + start, 1))
            except StopIteration:
                continue
            if insn.size <= back or start + insn.size < pos + 4:
                continue
            for op in insn.operands:
                if op.type != X86_OP_MEM:
                    continue
                mem = op.mem
                if mem.disp & 0xFFFFFFFF != literal or mem.base != 0:
                    continue
                if insn.address in seen:
                    continue
                seen.add(insn.address)
                candidates.append((insn, op.size, mem.index != 0, mem.scale))
        pos = text.find(needle, pos + 1)

    # A backward scan necessarily re-decodes each real instruction at every
    # offset inside it that still yields a valid decode.  The dominant case here
    # is a 0x66 operand-size prefix: `66 ff 05 <disp32>` (inc word) also decodes
    # at +1 as `ff 05 <disp32>` (inc dword), which would invert the C1 verdict.
    # The real instruction is the one that starts first; anything starting
    # strictly inside an accepted decode is an artifact of the scan, not code.
    # Verified against linear disassembly of 0x48bc92..0x48bcd9 and the five H1
    # sites: this rule reproduces the linear stream exactly.
    accepted: list = []
    covered_until = -1
    for entry in sorted(candidates, key=lambda e: e[0].address):
        insn = entry[0]
        if insn.address < covered_until:
            continue
        accepted.append(entry)
        covered_until = insn.address + insn.size
    return accepted


def main() -> int:
    data = ORIGINAL.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    check("original_sha256", digest == ORIGINAL_SHA256, digest)
    if digest != ORIGINAL_SHA256:
        return 1

    text_va, text = load_text_section(data)
    print(f"[INFO] .text va={hex(text_va)} size={hex(len(text))}")
    print()

    # ---------------- C1 ----------------
    widths: dict[str, set[int]] = {}
    for label, addr in C1_TARGETS.items():
        hits = recover_instructions(text_va, text, addr)
        widths[label] = {size for _insn, size, _idx, _scale in hits}
        print(f"[INFO] {label} {hex(addr)}: {len(hits)} referencing instruction(s)")
        for insn, size, indexed, scale in hits:
            print(
                f"[INFO]   {hex(insn.address)}  {insn.mnemonic:<7} {insn.op_str}"
                f"   | operand_bytes={size} indexed={indexed} scale={scale}"
            )
        print()

    count_widths = (
        widths["cat_a_end_count"]
        | widths["cat_b_end_count"]
        | widths["active_slot_end_count"]
    )
    check(
        "c1_count_alias_is_referenced_at_all",
        bool(count_widths),
        f"observed operand sizes={sorted(count_widths) or 'none'}",
    )
    # The decisive question: does any access to the count alias read/write 4 bytes?
    check(
        "c1_count_alias_never_accessed_as_dword",
        4 not in count_widths,
        f"sizes={sorted(count_widths)} -> "
        + (
            "WORD-only, manifest 'dword count' label is an error; the 2 B gap IS the count"
            if count_widths and 4 not in count_widths
            else "a 4-byte access exists: the count really overlaps cat_b[0]"
        ),
    )
    check(
        "c1_cat_b_base_element_width_is_dword",
        widths["cat_b_base"] == {4} if widths["cat_b_base"] else False,
        f"cat_b_base sizes={sorted(widths['cat_b_base']) or 'none'} "
        f"(manifest claims elem=4)",
    )
    print()

    # ---------------- H1 ----------------
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    md.detail = True
    gap_refs: dict[int, list] = defaultdict(list)
    for delta in range(0, GAP_SIZE):
        addr = AGE_END + delta
        needle = struct.pack("<I", addr)
        if text.find(needle) == -1:
            continue
        for insn, size, indexed, scale in recover_instructions(text_va, text, addr):
            gap_refs[addr].append((insn, size, indexed, scale))

    print(
        f"[INFO] H1 gap {hex(AGE_END)}..{hex(GAP_END)} "
        f"size={GAP_SIZE} (= 8*200*2 if the matrix hypothesis holds)"
    )
    print(f"[INFO] distinct referenced addresses inside gap: {len(gap_refs)}")
    gap_sizes: set[int] = set()
    for addr in sorted(gap_refs):
        for insn, size, indexed, scale in gap_refs[addr]:
            gap_sizes.add(size)
            print(
                f"[INFO]   {hex(addr)} <- {hex(insn.address)}  "
                f"{insn.mnemonic:<7} {insn.op_str}  | operand_bytes={size} "
                f"indexed={indexed} scale={scale}"
            )

    check(
        "h1_gap_is_referenced_by_code",
        bool(gap_refs),
        f"{len(gap_refs)} distinct address(es), operand sizes={sorted(gap_sizes) or 'none'}",
    )
    # H1 predicts WORD element accesses.  A 4-byte access anywhere in the gap
    # refutes the "8 x 200 WORD matrix" reading of this block.
    check(
        "h1_gap_accesses_are_word_only",
        bool(gap_sizes) and gap_sizes <= {2},
        f"sizes={sorted(gap_sizes) or 'none'} -> "
        + (
            "WORD element, consistent with a WORD matrix"
            if gap_sizes and gap_sizes <= {2}
            else "inconsistent with the 8x200 WORD matrix hypothesis"
        ),
    )
    gap_scales = {
        scale for refs in gap_refs.values() for _i, _s, _idx, scale in refs
    }
    check(
        "h1_gap_indexing_is_word_scaled",
        gap_scales == {2},
        f"index scales={sorted(gap_scales) or 'none'} (WORD element => *2)",
    )
    check(
        "h1_gap_size_is_8_rows_of_200_words",
        GAP_SIZE == 8 * 200 * 2,
        f"{GAP_SIZE} == 8*200*2 ({8 * 200 * 2})",
    )

    # Geometry alone cannot separate "8 rows of 200" from "200 rows of 8".  The
    # row stride is settled by the address arithmetic feeding the index: two
    # anchored sites build 200*i + j before scaling by 2.  Anchors are linear
    # decode starts verified by hand in this lap.
    print()
    for anchor, want in ((0x49B36A, 0x49B373), (0x47F8D2, 0x47F8DE)):
        stream = []
        off = anchor - text_va
        for insn in md.disasm(text[off : (want - text_va) + 16], anchor):
            stream.append(f"{hex(insn.address)} {insn.mnemonic} {insn.op_str}")
            if insn.address >= want:
                break
        print(f"[INFO] index chain feeding {hex(want)}:")
        for line in stream:
            print(f"[INFO]   {line}")
        # 5*x, then 5*that = 25*x, then +idx*8 => 200*x + idx.
        multiply_chain = sum(
            1 for line in stream if "lea" in line and "*4]" in line
        )
        check(
            f"h1_row_stride_200_at_{hex(want)}",
            multiply_chain >= 2 and any("*8]" in line for line in stream),
            f"two *5 lea steps ({multiply_chain}) plus an *8 step => 200*row + col",
        )

    print()
    print(f"failures={failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
