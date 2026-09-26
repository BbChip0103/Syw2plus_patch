#!/usr/bin/env python3
"""Add a versioned header and stock-save fallback to expanded persistence."""

from __future__ import annotations

import hashlib
import struct
from typing import Any

import pefile

from patches.population.full_tail_relocation_storage_layout_v1 import layout
from patches.population.g2_full_capacity_persistence_v1 import (
    IMAGE_BASE,
    LOAD_STREAM_FN,
    LOAD_WRAPPER_OFFSET,
    PersistenceBuildError,
    RSRC_EXECUTE_CODE_FLAGS,
    SAVE_STREAM_FN,
    _call,
    _va_to_file_offset,
    build_candidate as build_persistence_candidate,
)

SAVE_HEADER_CALL_VA = 0x00440C70
LOAD_HEADER_CALL_VA = 0x00441040
SAVE_HEADER_WRAPPER_OFFSET = 0x2400
LOAD_HEADER_WRAPPER_OFFSET = 0x2500
LEGACY_COPY_WRAPPER_OFFSET = 0x2600
RSRC_COMPAT_END_OFFSET = 0x2700
FLAG_GAP_FROM_RSRC = 0x100
MARKER_A = int.from_bytes(b"S2P1", "little")
MARKER_B = int.from_bytes(b"N4K1", "little")
MARKER_OFFSET = 0x38


def _emit_save_header_wrapper(start_va: int) -> bytes:
    code = bytearray(b"\x8b\x44\x24\x04")  # mov eax,[esp+4]
    code.extend(b"\xc7\x40" + bytes([MARKER_OFFSET]) + struct.pack("<I", MARKER_A))
    code.extend(b"\xc7\x40" + bytes([MARKER_OFFSET + 4]) + struct.pack("<I", MARKER_B))
    jump_va = start_va + len(code)
    code.extend(b"\xe9" + struct.pack("<i", SAVE_STREAM_FN - (jump_va + 5)))
    return bytes(code)


def _emit_load_header_wrapper(start_va: int, flag_va: int) -> bytes:
    code = bytearray(b"\x55\x89\xe5\x53")
    code.extend(b"\xff\x75\x14\xff\x75\x10\xff\x75\x0c\xff\x75\x08")
    call_va = start_va + len(code)
    code.extend(_call(call_va, LOAD_STREAM_FN))
    code.extend(b"\x83\xc4\x10\x89\xc3\x8b\x4d\x08")
    code.extend(b"\x81\x79" + bytes([MARKER_OFFSET]) + struct.pack("<I", MARKER_A))
    first_jne = len(code)
    code.extend(b"\x75\x00")
    code.extend(b"\x81\x79" + bytes([MARKER_OFFSET + 4]) + struct.pack("<I", MARKER_B))
    second_jne = len(code)
    code.extend(b"\x75\x00")
    code.extend(b"\xc7\x05" + struct.pack("<I", flag_va) + struct.pack("<I", 1))
    done_jump = len(code)
    code.extend(b"\xeb\x00")
    legacy = len(code)
    code.extend(b"\xc7\x05" + struct.pack("<I", flag_va) + struct.pack("<I", 0))
    done = len(code)
    code.extend(b"\x89\xd8\x5b\xc9\xc3")
    code[first_jne + 1] = legacy - (first_jne + 2)
    code[second_jne + 1] = legacy - (second_jne + 2)
    code[done_jump + 1] = done - (done_jump + 2)
    return bytes(code)


def _emit_legacy_copy_wrapper(regions: list[Any]) -> bytes:
    code = bytearray(b"\x56\x57\x51\x50\xfc")  # preserve regs; cld
    for region in regions:
        old_size = region.old_end - region.old_start
        new_size = region.new_end - region.new_start
        if old_size % 2 or new_size % 2 or new_size < old_size:
            raise PersistenceBuildError(f"unsupported legacy region geometry: {region.name}")
        has_trailing_count = region.name in {
            "category_slot_list_a",
            "category_slot_list_b",
            "active_slot_list",
        }
        old_entries_size = old_size - 2 if has_trailing_count else old_size
        new_entries_size = new_size - 2 if has_trailing_count else new_size
        code.extend(b"\xbe" + struct.pack("<I", region.old_start))
        code.extend(b"\xbf" + struct.pack("<I", region.new_start))
        code.extend(b"\xb9" + struct.pack("<I", old_entries_size // 4))
        code.extend(b"\xf3\xa5")
        if old_entries_size % 4:
            code.extend(b"\x66\xa5")
        tail = new_entries_size - old_entries_size
        code.extend(b"\x31\xc0")
        code.extend(b"\xbf" + struct.pack("<I", region.new_start + old_entries_size))
        code.extend(b"\xb9" + struct.pack("<I", tail // 4))
        code.extend(b"\xf3\xab")
        if tail % 4:
            code.extend(b"\x66\xab")
        if has_trailing_count:
            code.extend(b"\xbe" + struct.pack("<I", region.old_end - 2))
            code.extend(b"\xbf" + struct.pack("<I", region.new_end - 2))
            code.extend(b"\x66\xa5")
    code.extend(b"\x58\x59\x5f\x5e\xc3")
    if len(code) > 0x100:
        raise PersistenceBuildError(f"legacy copy wrapper is too large: {len(code)} bytes")
    return bytes(code)


def _emit_compatible_load_wrapper(
    start_va: int,
    flag_va: int,
    fallback_va: int,
    regions: list[tuple[int, int]],
) -> bytes:
    code = bytearray(b"\x55\x89\xe5\x53")

    def stream(buffer: int | None, size: int | None, original: bool = False) -> None:
        if original:
            code.extend(b"\xff\x75\x14\xff\x75\x10\xff\x75\x0c\xff\x75\x08")
        else:
            assert buffer is not None and size is not None
            code.extend(b"\xff\x75\x14\x6a\x01\x68" + struct.pack("<I", size))
            code.extend(b"\x68" + struct.pack("<I", buffer))
        call_va = start_va + len(code)
        code.extend(_call(call_va, LOAD_STREAM_FN))
        code.extend(b"\x83\xc4\x10")

    stream(None, None, original=True)
    code.extend(b"\x89\xc3\x83\x3d" + struct.pack("<I", flag_va) + b"\x01")
    legacy_jump = len(code)
    code.extend(b"\x75\x00")
    for address, size in regions:
        stream(address, size)
    done_jump = len(code)
    code.extend(b"\xeb\x00")
    legacy = len(code)
    call_va = start_va + len(code)
    code.extend(_call(call_va, fallback_va))
    done = len(code)
    code.extend(b"\x89\xd8\x5b\xc9\xc3")
    code[legacy_jump + 1] = legacy - (legacy_jump + 2)
    code[done_jump + 1] = done - (done_jump + 2)
    if len(code) > 0x100:
        raise PersistenceBuildError(f"compatible load wrapper is too large: {len(code)} bytes")
    return bytes(code)


def build_candidate(original: bytes, n: int = 4001) -> tuple[bytes, dict[str, Any]]:
    candidate, base_report = build_persistence_candidate(original, n)
    if n == 1200:
        return candidate, {"capacity": n, "compatibility_header": False, "base": base_report}

    result = layout(n)
    out = bytearray(candidate)
    pe = pefile.PE(data=candidate, fast_load=True)
    try:
        rsrc = next(s for s in pe.sections if s.Name.rstrip(b"\0") == b".rsrc")
        data = next(s for s in pe.sections if s.Name.rstrip(b"\0") == b".data")
        rsrc_va = IMAGE_BASE + int(rsrc.VirtualAddress)
        raw = int(rsrc.PointerToRawData)
        if int(rsrc.SizeOfRawData) < RSRC_COMPAT_END_OFFSET:
            raise PersistenceBuildError(".rsrc padding is too small for compatibility wrappers")
        cave = bytes(out[raw + SAVE_HEADER_WRAPPER_OFFSET : raw + RSRC_COMPAT_END_OFFSET])
        if cave != bytes(len(cave)):
            raise PersistenceBuildError("compatibility cave is not zero-filled")

        flag_va = rsrc_va - FLAG_GAP_FROM_RSRC
        data_end = flag_va + 4 - (IMAGE_BASE + int(data.VirtualAddress))
        if data_end >= int(rsrc.VirtualAddress) - int(data.VirtualAddress):
            raise PersistenceBuildError("compatibility flag overlaps .rsrc")
        struct.pack_into("<I", out, data.get_file_offset() + 8, max(int(data.Misc_VirtualSize), data_end))

        save_header_va = rsrc_va + SAVE_HEADER_WRAPPER_OFFSET
        load_header_va = rsrc_va + LOAD_HEADER_WRAPPER_OFFSET
        fallback_va = rsrc_va + LEGACY_COPY_WRAPPER_OFFSET
        sidecars = [(region.new_start, region.new_end - region.new_start) for region in result.regions[1:]]
        save_header = _emit_save_header_wrapper(save_header_va)
        load_header = _emit_load_header_wrapper(load_header_va, flag_va)
        fallback = _emit_legacy_copy_wrapper(result.regions[1:])
        load_wrapper = _emit_compatible_load_wrapper(
            rsrc_va + LOAD_WRAPPER_OFFSET, flag_va, fallback_va, sidecars
        )
        for offset, code in (
            (SAVE_HEADER_WRAPPER_OFFSET, save_header),
            (LOAD_HEADER_WRAPPER_OFFSET, load_header),
            (LEGACY_COPY_WRAPPER_OFFSET, fallback),
        ):
            out[raw + offset : raw + offset + len(code)] = code
        out[raw + LOAD_WRAPPER_OFFSET : raw + LOAD_WRAPPER_OFFSET + 0x100] = bytes(0x100)
        out[raw + LOAD_WRAPPER_OFFSET : raw + LOAD_WRAPPER_OFFSET + len(load_wrapper)] = load_wrapper

        struct.pack_into(
            "<I", out, rsrc.get_file_offset() + 8,
            max(int(rsrc.Misc_VirtualSize), RSRC_COMPAT_END_OFFSET),
        )
        struct.pack_into(
            "<I", out, rsrc.get_file_offset() + 36,
            int(rsrc.Characteristics) | RSRC_EXECUTE_CODE_FLAGS,
        )
        for call_va, old_target, new_target in (
            (SAVE_HEADER_CALL_VA, SAVE_STREAM_FN, save_header_va),
            (LOAD_HEADER_CALL_VA, LOAD_STREAM_FN, load_header_va),
        ):
            off = _va_to_file_offset(pe, call_va)
            if bytes(out[off : off + 5]) != _call(call_va, old_target):
                raise PersistenceBuildError(f"header callsite mismatch at 0x{call_va:08x}")
            out[off : off + 5] = _call(call_va, new_target)
    finally:
        pe.close()

    compatible = bytes(out)
    return compatible, {
        "capacity": n,
        "candidate_sha256": hashlib.sha256(compatible).hexdigest(),
        "compatibility_header": True,
        "marker": (MARKER_A.to_bytes(4, "little") + MARKER_B.to_bytes(4, "little")).decode(),
        "flag_va": f"0x{flag_va:08x}",
        "save_header_wrapper_va": f"0x{save_header_va:08x}",
        "load_header_wrapper_va": f"0x{load_header_va:08x}",
        "legacy_copy_wrapper_va": f"0x{fallback_va:08x}",
        "legacy_prefix_capacity": 1200,
        "base": base_report,
    }
