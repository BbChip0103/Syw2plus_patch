#!/usr/bin/env python3
"""Port the approved G5 v10 selection-cap50 candidate onto the ESL2608 G2 EXEs.

G5 v10 (``g5_selection_cap50_v10``, approved SHA ``c3ceaa25...``) is built only
on the protected original.  The two ESL2608 G2 deliverables keep the original
VA layout for ``.text``/``.data`` but (a) already use the original ``.text``
slack where v10 keeps its hook caves, (b) keep their own ``.rsrc`` at the VA
v10 uses for relocated selection storage, and (c) relocate six unit regions
(pool, existence, age, two category lists, active list) into ``.g2bss`` with a
4093-slot capacity.

The port therefore builds v10 from the original, then transplants the
original→v10 difference onto a G2 EXE:

- in-place ``.text`` edits are copied byte-for-byte after rebasing any operand
  that points at v10-owned storage/caves;
- the ``.text`` and ``.rsrc`` caves move to a new ``.g5code`` section and the
  selection/control-group storage moves to a new zero-backed ``.g5bss``;
- cave operands that address a G2-relocated unit region are rebased with the
  same geometry G2 used, and the two 1200-slot unit scans become 4093 scans;
- the save/load legacy-mirror hooks at ``0x440F0C``/``0x4412DC`` (also hooked
  by G2) chain G5 → G2 instead of G5 → CRT ``fwrite``/``fread``;
- v10's 50-entry sidecar is NOT kept at ``0x440F1E``/``0x4412EE``: more stream
  blocks follow that call (``0x4464B0``/``0x40F4B0`` and ESL's ``PSN2`` block), so
  a save without the sidecar would be read 4 bytes out of phase.  The port
  instead writes/reads the sidecar in ESL's save/load tail right before its
  ``fclose`` (``0x10910C1``/``0x109118C``), i.e. at the true end of the stream.

Every step is hash- or byte-guarded; any unclassified operand aborts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
from pathlib import Path
from typing import Any

import capstone

from patches.population.full_tail_relocation_storage_layout_v1 import layout
from patches.population.g2_esl2608_pool4092_owner500 import CAPACITY as G2_CAPACITY
from patches.selection import g5_selection_cap50_v10 as v10

IMAGE_BASE = 0x400000
V10_SHA256 = "c3ceaa25dea98232234759a332b867d92a669f63a03c3f453d3199cc329ebfad"
G2_SHA256 = {
    "normal": "83c7df80a3273d95d58e7a493866bbb40ad705d10120bc05db660400961fad60",
    "fixed_start": "1bdcadf9edeccc16d92696e580a60fc71f13a13b6bba22cafb8c9f50e749262f",
}
G2_SECTION_NAMES = (
    b".text", b".rdata", b".data", b".rsrc", b".psncode",
    b".psndata", b".shopai", b".g2bss", b".g2code", b".g2psn",
)
G2_POOL_VA = 0x0112E000
G2_SAVE_WRAPPER = 0x01895200
G2_LOAD_WRAPPER = 0x01895300

# v10 layout (original-based build).
TEXT_RAW_END = 0x1000 + 0xE3AE5  # original .text VirtualSize; caves live past it
V10_STORAGE = (0x0108C000, 0x0108D000)
V10_TEXT_CAVE = (0x004E4C00, 0x004E5000)
V10_RSRC_CAVE = (0x0108F100, 0x0108F400)
V10_RSRC_VA, V10_RSRC_RAW = 0x0108D000, 0xF9000
TEXT_FUNCS = (0x004E4C00, 0x004E4C80, 0x004E4CC0, 0x004E4D50, 0x004E4F90)
RSRC_FUNCS = (0x0108F100, 0x0108F180, 0x0108F200)  # v7 save, v8 load, v9 new-game
V10_APPEND_SITES = (0x00440F1E, 0x004412EE)  # left as G2's original fwrite/fread calls
RSRC_DATA = ((0x0108F240, 4),)  # "G5SC" sidecar magic literal
UNIT_SCAN_BOUNDS = (0x004E4C46, 0x004E4D37)  # cmp esi, 1200 in H1/H3
STOCK_UNIT_COUNT = 1200
V7_SAVE_TAILJMP = 0x0108F131  # jmp fwrite  -> jmp G2 save wrapper
V8_LOAD_CALL = 0x0108F18F  # call fread -> call G2 load wrapper
SAVE_STREAM_FN, LOAD_STREAM_FN = 0x004DA39F, 0x004DA4A9
CHAINED_HOOK_SITES = {0x00440F0C: G2_SAVE_WRAPPER, 0x004412DC: G2_LOAD_WRAPPER}
FCLOSE_FN = 0x004DA97C
PSN_CODE_VA, PSN_CODE_RAW = 0x01090000, 0xFC000
SAVE_CLOSE_SITE = 0x010910C1  # ESL save tail: call fclose (after PSN2 block)
LOAD_CLOSE_SITE = 0x0109118C  # ESL load tail: call fclose (after PSN2 block)
SIDECAR_MAGIC = b"G5SC"
SELECTION_ARRAY_BYTES = 4 + 50 * 4

# Port layout, appended after .g2psn.
G5BSS_VA = 0x018A6000
G5CODE_VA = 0x018A7000
SECTION_SIZE = 0x1000
RSRC_CAVE_SHIFT = 0x400  # rsrc caves land at .g5code+0x400
SAVE_TAIL_VA = G5CODE_VA + 0x800
LOAD_TAIL_VA = G5CODE_VA + 0x880
MAGIC_SCRATCH_VA = G5BSS_VA + 0x8D0  # v10's scratch dword, rebased

_MD = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
_MD.detail = True


class PortAbortedError(RuntimeError):
    """Raised when an input or operand does not match the pinned inventory."""


def _g2_region_map() -> list[tuple[int, int, int]]:
    geometry = layout(G2_CAPACITY)
    esl_delta = G2_POOL_VA - geometry.regions[0].new_start
    return [(r.old_start, r.old_end, r.new_start + esl_delta) for r in geometry.regions]


G2_REGIONS = _g2_region_map()


def _in(value: int, span: tuple[int, int]) -> bool:
    return span[0] <= value < span[1]


def relocate_code_va(va: int) -> int | None:
    if _in(va, V10_TEXT_CAVE):
        return G5CODE_VA + va - V10_TEXT_CAVE[0]
    if _in(va, V10_RSRC_CAVE):
        return G5CODE_VA + RSRC_CAVE_SHIFT + va - V10_RSRC_CAVE[0]
    return None


def relocate_value(value: int) -> int | None:
    """Map an absolute v10 address to the port; None means unchanged."""
    if _in(value, V10_STORAGE):
        return G5BSS_VA + value - V10_STORAGE[0]
    code = relocate_code_va(value)
    if code is not None:
        return code
    for old_start, old_end, new_start in G2_REGIONS:
        if old_start <= value < old_end:
            return new_start + value - old_start
    return None


def _v10_offset(va: int) -> int:
    if _in(va, V10_TEXT_CAVE) or IMAGE_BASE + 0x1000 <= va < V10_TEXT_CAVE[1]:
        return va - IMAGE_BASE
    if _in(va, V10_RSRC_CAVE):
        return va - V10_RSRC_VA + V10_RSRC_RAW
    raise PortAbortedError(f"0x{va:08x} is outside the v10 transplant ranges")


def _decode_function(image: bytes, start: int, limit: int) -> list[capstone.CsInsn]:
    """Linear-decode one cave function up to its zero-filled tail."""
    off = _v10_offset(start)
    end_off = off + (limit - start)
    code_end = end_off
    while code_end > off and image[code_end - 1] == 0:
        code_end -= 1
    insns: list[capstone.CsInsn] = []
    cursor = off
    while cursor < code_end:
        insn = next(_MD.disasm(image[cursor : cursor + 16], start + cursor - off), None)
        if insn is None:
            raise PortAbortedError(f"cave decode failed at 0x{start + cursor - off:08x}")
        insns.append(insn)
        cursor += insn.size
    if cursor < code_end or cursor > end_off:
        raise PortAbortedError(f"cave function 0x{start:08x} does not decode cleanly")
    return insns


def _branch_rel(insn: capstone.CsInsn) -> tuple[int, int] | None:
    """Return (field_offset, field_size) for a relative branch, else None."""
    b = insn.bytes
    if b[0] in (0xE8, 0xE9) and insn.size == 5:
        return 1, 4
    if b[0] == 0x0F and 0x80 <= b[1] <= 0x8F and insn.size == 6:
        return 2, 4
    if (b[0] == 0xEB or 0x70 <= b[0] <= 0x7F or b[0] in (0xE0, 0xE1, 0xE2, 0xE3)) and insn.size == 2:
        return 1, 1
    return None


def _operand_fields(insn: capstone.CsInsn) -> list[tuple[int, int, int]]:
    """(field_offset, size, value) for every 32-bit imm/disp operand."""
    fields = []
    for op in insn.operands:
        if op.type == capstone.x86.X86_OP_IMM and insn.imm_size == 4:
            fields.append((insn.imm_offset, 4, op.imm & 0xFFFFFFFF))
        elif op.type == capstone.x86.X86_OP_MEM and insn.disp_size == 4:
            fields.append((insn.disp_offset, 4, op.mem.disp & 0xFFFFFFFF))
    return fields


def _transplant_caves(image: bytes, code: bytearray) -> dict[str, Any]:
    special_targets = {V7_SAVE_TAILJMP: G2_SAVE_WRAPPER, V8_LOAD_CALL: G2_LOAD_WRAPPER}
    stats = {"rel32": 0, "abs": 0, "unit_scan_bounds": 0, "chained": 0}
    seen_bounds: set[int] = set()
    seen_special: set[int] = set()
    for funcs, cave in ((TEXT_FUNCS, V10_TEXT_CAVE), (RSRC_FUNCS, V10_RSRC_CAVE)):
        limits = [*funcs[1:], cave[1]]
        # Data literals inside the cave bound the preceding function.
        for data_va, _size in RSRC_DATA:
            limits = [data_va if f < data_va < lim else lim for f, lim in zip(funcs, limits)]
        for start, limit in zip(funcs, limits):
            for insn in _decode_function(image, start, limit):
                new_va = relocate_code_va(insn.address)
                assert new_va is not None
                raw = bytearray(insn.bytes)
                rel = _branch_rel(insn)
                if rel is not None:
                    field, size = rel
                    target = insn.operands[0].imm & 0xFFFFFFFF
                    if insn.address in special_targets:
                        if target not in (SAVE_STREAM_FN, LOAD_STREAM_FN):
                            raise PortAbortedError(f"unexpected chain target at 0x{insn.address:08x}")
                        target_new = special_targets[insn.address]
                        seen_special.add(insn.address)
                        stats["chained"] += 1
                    else:
                        target_new = relocate_code_va(target) or target
                    disp = target_new - (new_va + insn.size)
                    if size == 1:
                        if not -128 <= disp <= 127 or disp != target - (insn.address + insn.size):
                            raise PortAbortedError(f"rel8 changed at 0x{insn.address:08x}")
                    else:
                        struct.pack_into("<i", raw, field, disp)
                        stats["rel32"] += 1
                else:
                    for field, size, value in _operand_fields(insn):
                        if value in (STOCK_UNIT_COUNT,):
                            if insn.address not in UNIT_SCAN_BOUNDS:
                                raise PortAbortedError(f"unclassified 1200 at 0x{insn.address:08x}")
                            struct.pack_into("<I", raw, field, G2_CAPACITY)
                            seen_bounds.add(insn.address)
                            stats["unit_scan_bounds"] += 1
                            continue
                        new_value = relocate_value(value)
                        if new_value is not None:
                            struct.pack_into("<I", raw, field, new_value)
                            stats["abs"] += 1
                off = new_va - G5CODE_VA
                code[off : off + insn.size] = raw
    for data_va, size in RSRC_DATA:
        src = _v10_offset(data_va)
        dst = relocate_code_va(data_va) - G5CODE_VA  # type: ignore[operator]
        code[dst : dst + size] = image[src : src + size]
    if seen_bounds != set(UNIT_SCAN_BOUNDS) or seen_special != set(special_targets):
        raise PortAbortedError("unit-scan bound or chain inventory changed")
    return stats


def _diff_ranges(a: bytes, b: bytes, start: int, end: int) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    i = start
    while i < end:
        if a[i] != b[i]:
            j = i
            while j < end and a[j] != b[j]:
                j += 1
            ranges.append((i, j))
            i = j
        else:
            i += 1
    return ranges


def _port_inplace(original: bytes, image: bytes, g2: bytes, out: bytearray) -> dict[str, Any]:
    ranges = _diff_ranges(original, image, 0x1000, TEXT_RAW_END)
    patched = 0
    fixups = 0
    chained = []
    for start, end in ranges:
        va = IMAGE_BASE + start
        hook_va = next((h for h in (*CHAINED_HOOK_SITES, *V10_APPEND_SITES) if h < va <= h + 4), None)
        if hook_va is not None:
            continue
        if g2[start:end] != original[start:end]:
            raise PortAbortedError(f"G2 collides with G5 in-place edit at 0x{va:08x}")
        out[start:end] = image[start:end]
        patched += end - start
    # Rebase every 32-bit field inside or overlapping an edited range.
    for start, end in ranges:
        if any(h < IMAGE_BASE + start <= h + 4 for h in V10_APPEND_SITES):
            continue
        for w in range(start - 3, end):
            va = IMAGE_BASE + w
            value = struct.unpack_from("<I", image, w)[0]
            if image[w - 1] in (0xE8, 0xE9) or (image[w - 2] == 0x0F and 0x80 <= image[w - 1] <= 0x8F):
                target = (va + 4 + struct.unpack_from("<i", image, w)[0]) & 0xFFFFFFFF
                new_target = relocate_code_va(target)
                if new_target is not None:
                    struct.pack_into("<i", out, w, new_target - (va + 4))
                    fixups += 1
                    continue
            new_value = relocate_value(value) if _in(value, V10_STORAGE) else None
            if new_value is not None:
                struct.pack_into("<I", out, w, new_value)
                fixups += 1
    # Chain the two save/load hooks G2 also owns.
    for site, g2_target in CHAINED_HOOK_SITES.items():
        off = site - IMAGE_BASE
        g2_rel = struct.unpack_from("<i", g2, off + 1)[0]
        if g2[off] != 0xE8 or site + 5 + g2_rel != g2_target:
            raise PortAbortedError(f"G2 hook at 0x{site:08x} is not the pinned wrapper call")
        v_rel = struct.unpack_from("<i", image, off + 1)[0]
        g5_target = relocate_code_va(site + 5 + v_rel)
        if image[off] != 0xE8 or g5_target is None:
            raise PortAbortedError(f"v10 hook at 0x{site:08x} is not a cave call")
        struct.pack_into("<i", out, off + 1, g5_target - (site + 5))
        chained.append(hex(site))
    return {"ranges": len(ranges), "bytes": patched, "fixups": fixups, "chained_sites": chained}


def _call(src: int, target: int, opcode: int = 0xE8) -> bytes:
    return bytes([opcode]) + struct.pack("<i", target - (src + 5))


def _stream_call(code: bytearray, start_va: int, fn: int, buffer: int, size: int) -> None:
    """push [ebp+8]; push 1; push size; push buffer; call fn; add esp,16."""
    code += b"\xff\x75\x08\x6a\x01\x68" + struct.pack("<I", size) + b"\x68" + struct.pack("<I", buffer)
    code += _call(start_va + len(code), fn) + b"\x83\xc4\x10"


def emit_save_tail(magic_va: int) -> bytes:
    """fclose(f) wrapper: append magic + full 50-entry array, then tail-jump fclose."""
    code = bytearray(b"\x55\x89\xe5")
    _stream_call(code, SAVE_TAIL_VA, SAVE_STREAM_FN, magic_va, 4)
    _stream_call(code, SAVE_TAIL_VA, SAVE_STREAM_FN, G5BSS_VA, SELECTION_ARRAY_BYTES)
    code += b"\x5d" + _call(SAVE_TAIL_VA + len(code) + 1, FCLOSE_FN, 0xE9)
    return bytes(code)


def emit_load_tail() -> bytes:
    """fclose(f) wrapper: read the trailing sidecar only when its magic matches."""
    code = bytearray(b"\x55\x89\xe5")
    _stream_call(code, LOAD_TAIL_VA, LOAD_STREAM_FN, MAGIC_SCRATCH_VA, 4)
    code += b"\x83\xf8\x01\x75\x00"  # cmp eax,1; jne done
    jne1 = len(code) - 1
    code += b"\x81\x3d" + struct.pack("<I", MAGIC_SCRATCH_VA) + SIDECAR_MAGIC + b"\x75\x00"
    jne2 = len(code) - 1
    _stream_call(code, LOAD_TAIL_VA, LOAD_STREAM_FN, G5BSS_VA, SELECTION_ARRAY_BYTES)
    code += b"\x83\x3d" + struct.pack("<I", G5BSS_VA) + b"\x32\x7e\x0a"  # cmp [count],50; jle done
    code += b"\xc7\x05" + struct.pack("<I", G5BSS_VA) + struct.pack("<I", 50)
    done = len(code)
    for pos in (jne1, jne2):
        code[pos] = done - (pos + 1)
    code += b"\x5d" + _call(LOAD_TAIL_VA + len(code) + 1, FCLOSE_FN, 0xE9)
    return bytes(code)


def _hook_close_sites(g2: bytes, out: bytearray) -> list[str]:
    hooked = []
    for site, wrapper in ((SAVE_CLOSE_SITE, SAVE_TAIL_VA), (LOAD_CLOSE_SITE, LOAD_TAIL_VA)):
        off = site - PSN_CODE_VA + PSN_CODE_RAW
        if g2[off : off + 5] != _call(site, FCLOSE_FN) or g2[off - 1] != 0x56:  # push esi; call fclose
            raise PortAbortedError(f"ESL fclose tail at 0x{site:08x} is not pinned")
        out[off : off + 5] = _call(site, wrapper)
        hooked.append(hex(site))
    return hooked


def _section_header(name: bytes, vsize: int, rva: int, rsize: int, rptr: int, flags: int) -> bytes:
    return name.ljust(8, b"\0") + struct.pack("<IIIIIIHHI", vsize, rva, rsize, rptr, 0, 0, 0, 0, flags)


def _append_sections(out: bytearray, code: bytes) -> None:
    pe_off = struct.unpack_from("<I", out, 0x3C)[0]
    nsec = struct.unpack_from("<H", out, pe_off + 6)[0]
    opt_size = struct.unpack_from("<H", out, pe_off + 20)[0]
    opt = pe_off + 24
    table = opt + opt_size
    names = tuple(bytes(out[table + i * 40 : table + i * 40 + 8]).rstrip(b"\0") for i in range(nsec))
    if names != G2_SECTION_NAMES:
        raise PortAbortedError(f"unexpected G2 section table {names}")
    headers_size = struct.unpack_from("<I", out, opt + 60)[0]
    if table + (nsec + 2) * 40 > headers_size or any(out[table + nsec * 40 : table + (nsec + 2) * 40]):
        raise PortAbortedError("no free section header slots")
    last = table + (nsec - 1) * 40
    last_vsize, last_rva = struct.unpack_from("<II", out, last + 8)
    if IMAGE_BASE + last_rva + last_vsize != G5BSS_VA:
        raise PortAbortedError("G2 image end is not the pinned .g5bss VA")
    if len(out) % SECTION_SIZE:
        raise PortAbortedError("G2 file is not section aligned")
    raw_ptr = len(out)
    out[table + nsec * 40 : table + (nsec + 1) * 40] = _section_header(
        b".g5bss", SECTION_SIZE, G5BSS_VA - IMAGE_BASE, 0, 0, 0xC0000080
    )
    out[table + (nsec + 1) * 40 : table + (nsec + 2) * 40] = _section_header(
        b".g5code", SECTION_SIZE, G5CODE_VA - IMAGE_BASE, SECTION_SIZE, raw_ptr, 0x60000020
    )
    struct.pack_into("<H", out, pe_off + 6, nsec + 2)
    struct.pack_into("<I", out, opt + 56, G5CODE_VA - IMAGE_BASE + SECTION_SIZE)
    out.extend(code)


def build_candidate(original: bytes, g2: bytes) -> tuple[bytes, dict[str, Any]]:
    v10.v9.v8.v7.v3.v1.verify_original(original)
    g2_sha = hashlib.sha256(g2).hexdigest()
    variant = next((k for k, v in G2_SHA256.items() if v == g2_sha), None)
    if variant is None:
        raise ValueError("G2 EXE SHA256 is not a pinned ESL2608 G2 deliverable")
    image, _v10_report = v10.build_candidate(original)
    if hashlib.sha256(image).hexdigest() != V10_SHA256:
        raise PortAbortedError("v10 rebuild does not match the approved SHA256")
    out = bytearray(g2)
    inplace = _port_inplace(original, image, g2, out)
    code = bytearray(SECTION_SIZE)
    caves = _transplant_caves(image, code)
    magic_va = relocate_code_va(RSRC_DATA[0][0])
    assert magic_va is not None
    for va, blob in ((SAVE_TAIL_VA, emit_save_tail(magic_va)), (LOAD_TAIL_VA, emit_load_tail())):
        if len(blob) > 0x80:
            raise PortAbortedError("sidecar tail wrapper exceeds its slot")
        code[va - G5CODE_VA : va - G5CODE_VA + len(blob)] = blob
    close_hooks = _hook_close_sites(g2, out)
    _append_sections(out, bytes(code))
    candidate = bytes(out)
    return candidate, {
        "schema": "syw2plus.g5-v10-on-esl2608-g2-port.v1",
        "variant": variant,
        "g2_sha256": g2_sha,
        "v10_sha256": V10_SHA256,
        "candidate_sha256": hashlib.sha256(candidate).hexdigest(),
        "selection_base": hex(G5BSS_VA),
        "selection_count_va": hex(G5BSS_VA),
        "sidecar": {"save_close_site": hex(SAVE_CLOSE_SITE), "load_close_site": hex(LOAD_CLOSE_SITE),
                    "save_tail": hex(SAVE_TAIL_VA), "load_tail": hex(LOAD_TAIL_VA),
                    "hooked": close_hooks, "position": "end of stream (after ESL PSN2 block)"},
        "g5code_va": hex(G5CODE_VA),
        "unit_scan_count": G2_CAPACITY,
        "inplace": inplace,
        "caves": caves,
    }


def write_candidate(original_path: Path, g2_path: Path, destination: Path) -> dict[str, Any]:
    resolved = destination.resolve()
    if resolved in (original_path.resolve(), g2_path.resolve()):
        raise ValueError("refusing to overwrite an input EXE")
    candidate, report = build_candidate(original_path.read_bytes(), g2_path.read_bytes())
    fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(fd, "wb") as handle:
        handle.write(candidate)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", type=Path)
    parser.add_argument("g2", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    print(json.dumps(write_candidate(args.original, args.g2, args.destination), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
