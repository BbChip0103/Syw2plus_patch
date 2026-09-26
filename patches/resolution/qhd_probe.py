#!/usr/bin/env python3
"""Reversible research-only QHD patch. See original_qhd_probe_0910.md.
Not a released patch; preserves original simulation and replaces terrain caching
with full redraw. Only distinct SHA-pinned input/output paths are accepted.
"""

import argparse
import hashlib
import json
import pathlib
import shutil
import struct
import capstone
import pefile

SHA = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"
BASE = 0x400000
WIDTH, HEIGHT, RADIUS = 2560, 1440, 64


def digest(data):
    return hashlib.sha256(data).hexdigest()


def align(n, a):
    return (n + a - 1) // a * a


def build(data):
    if digest(data) != SHA:
        raise ValueError("Unsupported binary SHA256")
    pe = pefile.PE(data=data)
    out = bytearray(data)
    changes = []

    def edit(va, old, new, why):
        pos = pe.get_offset_from_rva(va - BASE)
        if len(old) != len(new) or data[pos : pos + len(old)] != old:
            raise ValueError(f"Instruction mismatch at {va:#x}")
        if out[pos : pos + len(old)] != old:
            raise ValueError(f"Overlapping patch at {va:#x}")
        out[pos : pos + len(old)] = new
        changes.append(dict(va=hex(va), offset=pos, old=old.hex(), new=new.hex(), reason=why))

    def u32(va, old, new, why):
        edit(va, struct.pack("<I", old), struct.pack("<I", new), why)

    last = pe.sections[-1]
    rva = align(last.VirtualAddress + last.Misc_VirtualSize, pe.OPTIONAL_HEADER.SectionAlignment)
    raw = align(len(out), pe.OPTIONAL_HEADER.FileAlignment)
    buffer = BASE + rva
    mask = buffer + align(WIDTH * HEIGHT, 4096)
    row_table = mask + 0x10000
    size = mask - buffer + 0x12000
    section = struct.pack(
        "<8sIIIIIIHHI", b".qhd\0\0\0\0", size, rva, align(size, 4096), raw, 0, 0, 0, 0, 0xC0000040
    )
    head = last.get_file_offset() + 40
    if head + 40 > pe.OPTIONAL_HEADER.SizeOfHeaders or any(out[head : head + 40]):
        raise ValueError("No empty PE section header")
    out[head : head + 40] = section
    struct.pack_into(
        "<H",
        out,
        pe.FILE_HEADER.get_field_absolute_offset("NumberOfSections"),
        len(pe.sections) + 1,
    )
    struct.pack_into(
        "<I",
        out,
        pe.OPTIONAL_HEADER.get_field_absolute_offset("SizeOfImage"),
        align(rva + size, 4096),
    )
    out.extend(bytes(raw - len(out)))
    out.extend(bytes(mask - buffer))
    out.extend(b"\x01" * 0x10000)
    out.extend(bytes(0x2000))
    out.extend(bytes(align(size, 4096) - size))
    for va, old, new, label in [
        (0x464505, 800, WIDTH, "mode width"),
        (0x46450C, 600, HEIGHT, "mode height"),
        (0x432912, 512, HEIGHT, "terrain height"),
        (0x432917, 832, WIDTH, "terrain stride"),
        (0x43291C, 0xBA3D30, buffer, "terrain storage"),
        (0x432955, 511, HEIGHT - 1, "terrain clip bottom"),
        (0x43295A, 831, WIDTH - 1, "terrain clip right"),
        (0x41BF40, 0xBA3D30, buffer, "composite storage"),
        (0x41BF45, 512, HEIGHT, "composite height"),
        (0x41BF4A, 832, WIDTH, "composite width"),
    ]:
        u32(va, old, new, label)
    u32(
        0x464990,
        0x4F0,
        row_table - 0xE5BF18,
        "relocate height-indexed row table; avoid DDraw metadata overflow",
    )
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    md.detail = True

    def insns(start, end):
        return md.disasm(pe.get_data(start - BASE, end - start), start)

    # These constants occur only in viewport setup in this bounded function.
    for i in insns(0x41B480, 0x41B570):
        if i.imm_size == 4 and i.operands[-1].type == capstone.x86.X86_OP_IMM:
            val = i.operands[-1].imm
            if val in (831, 511):
                u32(
                    i.address + i.imm_offset,
                    val,
                    WIDTH - 1 if val == 831 else HEIGHT - 1,
                    "viewport",
                )
    clear_va = 0x4E4B00
    clear = (
        b"\x9c\x60\xfc\x31\xc0\xbf"
        + struct.pack("<I", buffer)
        + b"\xb9"
        + struct.pack("<I", WIDTH * HEIGHT // 4)
        + b"\xf3\xab\x61\x9d"
    )
    clear += b"\xe9" + struct.pack("<i", 0x433019 - (clear_va + len(clear) + 5))
    edit(
        clear_va,
        bytes(len(clear)),
        clear,
        "clear private framebuffer on redraw; preserve registers and flags",
    )
    text_section = pe.sections[0]
    virtual_size = clear_va + len(clear) - BASE - text_section.VirtualAddress
    if virtual_size > text_section.SizeOfRawData:
        raise ValueError("Clear trampoline exceeds code padding")
    struct.pack_into(
        "<I", out, text_section.get_field_absolute_offset("Misc_VirtualSize"), virtual_size
    )
    old = pe.get_data(0x43296C - BASE, 5)
    edit(
        0x43296C,
        old,
        b"\xe9" + struct.pack("<i", clear_va - (0x43296C + 5)),
        "always redraw via clear trampoline; bypass fixed scrolling",
    )
    # Bounds only, not multiplication/shift 16 or pixel advance 0x43347c.
    for start, end in [(0x4324E0, 0x432911), (0x433019, 0x4332B5), (0x4332F0, 0x434070)]:
        for i in insns(start, end):
            if i.address in (0x43347C, 0x434038):
                continue
            if (
                i.mnemonic in ("add", "sub")
                and i.imm_size in (1, 2)
                and i.operands[-1].type == capstone.x86.X86_OP_IMM
                and i.operands[-1].imm == 16
            ):
                off = i.imm_offset
                edit(
                    i.address + off,
                    bytes(i.bytes[off : off + i.imm_size]),
                    RADIUS.to_bytes(i.imm_size, "little"),
                    "camera scan radius",
                )
            if (
                i.mnemonic == "lea"
                and i.disp_size == 1
                and i.operands[-1].type == capstone.x86.X86_OP_MEM
                and i.operands[-1].mem.disp == -16
            ):
                edit(
                    i.address + i.disp_offset,
                    b"\xf0",
                    bytes([256 - RADIUS]),
                    "camera scan lower bound",
                )
    for start, end in [
        (0x4351D0, 0x435400),
        (0x435680, 0x435B90),
        (0x435B90, 0x435E40),
        (0x435E40, 0x4360F0),
        (0x4360F0, 0x4363A0),
    ]:
        for i in insns(start, end):
            if i.disp_size == 4 and any(
                o.type == capstone.x86.X86_OP_MEM and o.mem.disp == 0x105796C for o in i.operands
            ):
                u32(
                    i.address + i.disp_offset,
                    0x105796C,
                    mask + 0x8000,
                    "private all-dirty mask (padded)",
                )
    pefile.PE(data=bytes(out)).close()
    return bytes(out), dict(
        source_sha256=SHA,
        patched_sha256=digest(out),
        width=WIDTH,
        height=HEIGHT,
        terrain_va=hex(buffer),
        dirty_va=hex(mask + 0x8000),
        row_table_va=hex(row_table),
        clear_trampoline_va=hex(clear_va),
        changes=changes,
    )


def apply(source, target):
    if source.resolve() == target.resolve() or target.exists():
        raise ValueError("Output must be a new distinct file")
    data = source.read_bytes()
    patched, manifest = build(data)
    backup = target.with_suffix(target.suffix + ".original-backup")
    if backup.exists():
        raise ValueError("Backup already exists")
    backup.write_bytes(data)
    target.write_bytes(patched)
    target.with_suffix(target.suffix + ".patch.json").write_text(
        json.dumps(manifest, indent=2) + "\n"
    )
    return manifest


def restore(target):
    backup = target.with_suffix(target.suffix + ".original-backup")
    manifest = json.loads(target.with_suffix(target.suffix + ".patch.json").read_text())
    if (
        digest(backup.read_bytes()) != SHA
        or digest(target.read_bytes()) != manifest["patched_sha256"]
    ):
        raise ValueError("Restore refuses modified output/backup")
    shutil.copyfile(backup, target)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="command", required=True)
    a = sub.add_parser("apply")
    a.add_argument("source", type=pathlib.Path)
    a.add_argument("target", type=pathlib.Path)
    a = sub.add_parser("restore")
    a.add_argument("target", type=pathlib.Path)
    args = ap.parse_args()
    if args.command == "apply":
        print(json.dumps(apply(args.source, args.target), indent=2))
    else:
        restore(args.target)
