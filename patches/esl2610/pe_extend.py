#!/usr/bin/env python3
"""Shared PE helpers for patches on the official ESL 2610-line executable.

The pinned base is official ESL 2613, applied over the 2612 data overlay.  It
has the same PE section layout as 2612 but restores official 100-entry
selection hooks and adds a pool-relative reference in ``.kills``.

2610 already has 90 sections and its section table ends exactly at the
0x1000 header boundary, so no section can be added as-is.  The bytes between
the DOS header and ``e_lfanew = 0xF8`` are only the DOS stub and the linker
Rich header; :func:`compact_headers` moves the NT headers and section table
down to 0x40, which frees four section-table slots without changing
SizeOfHeaders, any file offset, any RVA or any section byte.

:func:`add_section` then appends a section at the first free RVA (old
SizeOfImage) and at the end of the file, updating NumberOfSections,
SizeOfImage, SizeOfCode/SizeOfInitializedData/SizeOfUninitializedData and the
checksum.  All functions are pure ``bytes -> bytes``.
"""

from __future__ import annotations

import hashlib
import struct
from pathlib import Path

import pefile

REPO = Path(__file__).resolve().parents[2]
BASE_PATH = REPO.parent / "patch_history" / "[ESL]Syw2plus 2613.exe"
BASE_SHA256 = "818721a5e8539f9ed97090a6d64cfdba429d46ec9caaa5671528005b22f5b724"
IMAGE_BASE = 0x00400000
ALIGN = 0x1000  # SectionAlignment; FileAlignment is read from the header
COMPACT_LFANEW = 0x40

CODE_RX = 0x60000020  # code | execute | read
DATA_RW = 0xC0000040  # initialized data | read | write
BSS_RW = 0xC0000080  # uninitialized data | read | write


def verify_base(data: bytes) -> None:
    digest = hashlib.sha256(data).hexdigest()
    if digest != BASE_SHA256:
        raise ValueError(f"input SHA256 is not the pinned ESL2613 EXE: {digest}")


def _align(value: int, alignment: int = ALIGN) -> int:
    return (value + alignment - 1) & -alignment


def _layout(data: bytes | bytearray) -> tuple[int, int, int, int]:
    """Return (e_lfanew, optional header offset, section table offset, count)."""
    lfanew = struct.unpack_from("<I", data, 0x3C)[0]
    if data[lfanew : lfanew + 4] != b"PE\0\0":
        raise ValueError("bad PE signature")
    count = struct.unpack_from("<H", data, lfanew + 6)[0]
    optional_size = struct.unpack_from("<H", data, lfanew + 20)[0]
    optional = lfanew + 24
    return lfanew, optional, optional + optional_size, count


def free_header_slots(data: bytes | bytearray) -> int:
    _lfanew, optional, table, count = _layout(data)
    size_of_headers = struct.unpack_from("<I", data, optional + 60)[0]
    first_raw = min(
        struct.unpack_from("<I", data, table + i * 40 + 20)[0]
        for i in range(count)
        if struct.unpack_from("<I", data, table + i * 40 + 16)[0]
    )
    return (min(size_of_headers, first_raw) - (table + count * 40)) // 40


def compact_headers(data: bytes) -> bytes:
    lfanew, _optional, table, count = _layout(data)
    if lfanew == COMPACT_LFANEW:
        raise ValueError("headers are already compacted")
    if lfanew < COMPACT_LFANEW:
        raise ValueError(f"unexpected e_lfanew 0x{lfanew:x}")
    end = table + count * 40
    out = bytearray(data)
    block = bytes(data[lfanew:end])
    out[COMPACT_LFANEW:end] = block + b"\0" * (end - COMPACT_LFANEW - len(block))
    struct.pack_into("<I", out, 0x3C, COMPACT_LFANEW)
    return _with_checksum(bytes(out))


def _with_checksum(data: bytes) -> bytes:
    pe = pefile.PE(data=data, fast_load=True)
    pe.OPTIONAL_HEADER.CheckSum = 0
    pe.OPTIONAL_HEADER.CheckSum = pe.generate_checksum()
    return bytes(pe.write())


def section_names(data: bytes | bytearray) -> list[bytes]:
    _lfanew, _optional, table, count = _layout(data)
    return [bytes(data[table + i * 40 : table + i * 40 + 8]).rstrip(b"\0") for i in range(count)]


def add_section(data: bytes, name: bytes, payload: bytes, virtual_size: int, characteristics: int) -> bytes:
    """Append one section; ``payload`` empty means an uninitialized (BSS) section."""
    if len(name) > 8:
        raise ValueError("section name longer than 8 bytes")
    if name in section_names(data):
        raise ValueError(f"section {name!r} already exists")
    if free_header_slots(data) < 1:
        raise ValueError("no free section header slot; compact_headers first")
    if len(payload) > virtual_size:
        raise ValueError("payload larger than virtual size")
    _lfanew, optional, table, count = _layout(data)
    size_of_image = struct.unpack_from("<I", data, optional + 56)[0]
    file_align = struct.unpack_from("<I", data, optional + 36)[0]
    raw_size = _align(len(payload), file_align) if payload else 0
    raw_pointer = _align(len(data), file_align) if payload else 0
    out = bytearray(data)
    if payload:
        out.extend(b"\0" * (raw_pointer - len(out)))
        out.extend(payload + b"\0" * (raw_size - len(payload)))
    header = table + count * 40
    out[header : header + 40] = struct.pack(
        "<8sIIIIIIHHI", name, virtual_size, size_of_image, raw_size, raw_pointer,
        0, 0, 0, 0, characteristics,
    )
    struct.pack_into("<H", out, _lfanew + 6, count + 1)
    struct.pack_into("<I", out, optional + 56, size_of_image + _align(virtual_size))
    if characteristics & 0x20:
        field, amount = 4, raw_size
    elif characteristics & 0x80:
        field, amount = 12, _align(virtual_size)
    else:
        field, amount = 8, raw_size
    struct.pack_into("<I", out, optional + field, struct.unpack_from("<I", out, optional + field)[0] + amount)
    return _with_checksum(bytes(out))


def va_to_offset(data: bytes | bytearray, va: int) -> int:
    _lfanew, _optional, table, count = _layout(data)
    rva = va - IMAGE_BASE
    for i in range(count):
        vsize, vaddr, raw_size, raw_pointer = struct.unpack_from("<IIII", data, table + i * 40 + 8)
        if raw_size and vaddr <= rva < vaddr + min(max(vsize, 1), raw_size):
            return raw_pointer + rva - vaddr
    raise ValueError(f"VA 0x{va:08x} is not file-backed")


def section_va(data: bytes | bytearray, name: bytes) -> int:
    _lfanew, _optional, table, count = _layout(data)
    for i in range(count):
        off = table + i * 40
        if bytes(data[off : off + 8]).rstrip(b"\0") == name:
            return IMAGE_BASE + struct.unpack_from("<I", data, off + 12)[0]
    raise ValueError(f"no section {name!r}")
