#!/usr/bin/env python3
"""Experimental expanded-layout save/load sidecar for relocated unit arrays.

The stock save stream writes the original bulk block and then serializes live
UnitStruct records, but the five relocated sidecar arrays are outside that
bulk.  This candidate redirects the existing bulk writer/reader calls through
two tiny wrappers in verified zero padding at the end of ``.rsrc``.  Each
wrapper performs the original call and then transfers the relocated
existence, age, category-A, category-B and active-list regions in the same
order.  The post-load 1200-slot walk is also raised to the selected capacity.

This changes the save ABI for expanded candidates.  Compatibility/magic
gating is deliberately a later product gate; this module first proves a
same-candidate round trip without growing the executable or touching originals.
"""

from __future__ import annotations

import hashlib
import struct
from pathlib import Path
from typing import Any

import pefile

from patches.population.full_tail_relocation_storage_layout_v1 import (
    ORIGINAL_SHA256,
    STOCK_CAPACITY,
    layout,
)
from patches.population.g2_full_capacity_supply5000_owner1200_v1 import (
    build_candidate as build_product_candidate,
)

IMAGE_BASE = 0x00400000
SAVE_CALL_VA = 0x00440F0C
LOAD_CALL_VA = 0x004412DC
POSTLOAD_BOUND_VA = 0x00441441
SAVE_STREAM_FN = 0x004DA39F
LOAD_STREAM_FN = 0x004DA4A9
RSRC_CAVE_OFFSET = 0x2200
SAVE_WRAPPER_OFFSET = RSRC_CAVE_OFFSET
LOAD_WRAPPER_OFFSET = RSRC_CAVE_OFFSET + 0x100
RSRC_CODE_END_OFFSET = RSRC_CAVE_OFFSET + 0x200
RSRC_EXECUTE_CODE_FLAGS = 0x20000020


class PersistenceBuildError(RuntimeError):
    pass


def _va_to_file_offset(pe: pefile.PE, va: int) -> int:
    for section in pe.sections:
        start = IMAGE_BASE + int(section.VirtualAddress)
        span = max(int(section.SizeOfRawData), int(section.Misc_VirtualSize))
        if start <= va < start + span:
            return int(section.PointerToRawData) + va - start
    raise PersistenceBuildError(f"VA 0x{va:08x} is outside every section")


def _call(source_va: int, target_va: int) -> bytes:
    return b"\xe8" + struct.pack("<i", target_va - (source_va + 5))


def _emit_stream_wrapper(start_va: int, stream_fn: int, regions: list[tuple[int, int]]) -> bytes:
    code = bytearray(b"\x55\x89\xe5\x53")  # push ebp; mov ebp,esp; push ebx

    def emit_call(buffer: int | None, size: int | None, original: bool = False) -> None:
        if original:
            code.extend(b"\xff\x75\x14\xff\x75\x10\xff\x75\x0c\xff\x75\x08")
        else:
            assert buffer is not None and size is not None
            code.extend(b"\xff\x75\x14\x6a\x01\x68")
            code.extend(struct.pack("<I", size))
            code.extend(b"\x68")
            code.extend(struct.pack("<I", buffer))
        call_va = start_va + len(code)
        code.extend(_call(call_va, stream_fn))
        code.extend(b"\x83\xc4\x10")

    emit_call(None, None, original=True)
    code.extend(b"\x89\xc3")  # preserve the original transfer's return value
    for address, size in regions:
        emit_call(address, size)
    code.extend(b"\x89\xd8\x5b\xc9\xc3")
    if len(code) > 0x100:
        raise PersistenceBuildError(f"stream wrapper is too large: {len(code)} bytes")
    return bytes(code)


def build_candidate(original: bytes, n: int = 4001) -> tuple[bytes, dict[str, Any]]:
    if hashlib.sha256(original).hexdigest() != ORIGINAL_SHA256:
        raise ValueError("original EXE SHA256 mismatch; refusing to build a candidate")
    product, product_report = build_product_candidate(original, n)
    if n == STOCK_CAPACITY:
        return product, {
            "capacity": n,
            "candidate_sha256": hashlib.sha256(product).hexdigest(),
            "product_report": product_report,
            "persistence_sidecar": False,
        }

    result = layout(n)
    sidecars = [(region.new_start, region.new_end - region.new_start) for region in result.regions[1:]]
    out = bytearray(product)
    pe = pefile.PE(data=bytes(out), fast_load=True)
    try:
        rsrc = next(
            (section for section in pe.sections if section.Name.rstrip(b"\0") == b".rsrc"),
            None,
        )
        if rsrc is None:
            raise PersistenceBuildError(".rsrc section missing")
        rsrc_va = IMAGE_BASE + int(rsrc.VirtualAddress)
        if rsrc_va != result.rsrc.new_start:
            raise PersistenceBuildError("relocated .rsrc VA does not match layout")
        if int(rsrc.SizeOfRawData) < RSRC_CODE_END_OFFSET:
            raise PersistenceBuildError(".rsrc raw padding is too small for wrappers")
        raw = int(rsrc.PointerToRawData)
        cave = bytes(out[raw + RSRC_CAVE_OFFSET : raw + RSRC_CODE_END_OFFSET])
        if cave != bytes(len(cave)):
            raise PersistenceBuildError(".rsrc persistence cave is not zero-filled")

        save_va = rsrc_va + SAVE_WRAPPER_OFFSET
        load_va = rsrc_va + LOAD_WRAPPER_OFFSET
        save_code = _emit_stream_wrapper(save_va, SAVE_STREAM_FN, sidecars)
        load_code = _emit_stream_wrapper(load_va, LOAD_STREAM_FN, sidecars)
        out[raw + SAVE_WRAPPER_OFFSET : raw + SAVE_WRAPPER_OFFSET + len(save_code)] = save_code
        out[raw + LOAD_WRAPPER_OFFSET : raw + LOAD_WRAPPER_OFFSET + len(load_code)] = load_code

        section_off = rsrc.get_file_offset()
        struct.pack_into(
            "<I", out, section_off + 8,
            max(int(rsrc.Misc_VirtualSize), RSRC_CODE_END_OFFSET),
        )
        struct.pack_into(
            "<I", out, section_off + 36,
            int(rsrc.Characteristics) | RSRC_EXECUTE_CODE_FLAGS,
        )

        for call_va, old_target, new_target in (
            (SAVE_CALL_VA, SAVE_STREAM_FN, save_va),
            (LOAD_CALL_VA, LOAD_STREAM_FN, load_va),
        ):
            off = _va_to_file_offset(pe, call_va)
            expected = _call(call_va, old_target)
            if bytes(out[off : off + 5]) != expected:
                raise PersistenceBuildError(f"callsite 0x{call_va:08x} old bytes mismatch")
            out[off : off + 5] = _call(call_va, new_target)

        bound_off = _va_to_file_offset(pe, POSTLOAD_BOUND_VA)
        expected_bound = bytes.fromhex("6681fbb004")
        if bytes(out[bound_off : bound_off + len(expected_bound)]) != expected_bound:
            raise PersistenceBuildError("post-load bound old bytes mismatch")
        struct.pack_into("<H", out, bound_off + 3, n)
    finally:
        pe.close()

    candidate = bytes(out)
    if len(candidate) != len(original):
        raise PersistenceBuildError("persistence candidate changed file length")
    return candidate, {
        "capacity": n,
        "candidate_sha256": hashlib.sha256(candidate).hexdigest(),
        "product_report": product_report,
        "persistence_sidecar": True,
        "sidecars": [
            {"name": region.name, "address": f"0x{region.new_start:08x}", "size": region.new_end - region.new_start}
            for region in result.regions[1:]
        ],
        "save_wrapper_va": f"0x{save_va:08x}",
        "load_wrapper_va": f"0x{load_va:08x}",
        "postload_bound": n,
    }


def write_candidate(original_path: Path, destination: Path, n: int = 4001) -> dict[str, Any]:
    if original_path.resolve() == destination.resolve():
        raise ValueError("refusing to overwrite the original EXE")
    candidate, report = build_candidate(original_path.read_bytes(), n)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(candidate)
    return report
