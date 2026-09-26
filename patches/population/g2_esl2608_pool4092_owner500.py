"""Port the pinned ESL2606 4092/500 G2 patch to three exact ESL2608 builds.

The 2608 .psncode/.psndata/.shopai sections occupy the 2606 G2 tail. Keep
them and the original .rsrc in place; append a zero-raw G2 storage section
and an executable section for the versioned save/load wrappers instead.
"""

from __future__ import annotations

import argparse
from dataclasses import replace
import hashlib
from pathlib import Path
import struct
from typing import Any

import pefile

from patches.population.full_tail_relocation_storage_layout_v1 import layout
from patches.population.g2_esl2606_pool4092_owner500 import (
    REFERENCE_SHA256 as LEGACY_SHA256,
    build_candidate as build_legacy_candidate,
)
from patches.population.g2_esl2606_pool10000_owner1200 import ACTIVE_BULK_BASE
from patches.population.g2_full_capacity_persistence_v1 import (
    LOAD_STREAM_FN,
    SAVE_STREAM_FN,
    _call,
    _emit_stream_wrapper,
)
from patches.population.g2_full_capacity_persistence_compat_v1 import (
    _emit_compatible_load_wrapper,
    _emit_legacy_copy_wrapper,
    _emit_load_header_wrapper,
    _emit_save_header_wrapper,
)

IMAGE_BASE = 0x400000
CAPACITY = 4093
TEMPLATE_SHA256 = "ce3465e764af30da83d0ad19b1dd9a5a8e72f357dfa2da078acef229ec20c9ac"
SOURCE_SHA256 = {
    "shop": "0f3334668f5ed37d130726725f421515f031be2856efdde04a9c19ea572627f5",
    "seven": "cade60b2451519ec4e305d91279b1c377cf797c813a939c5b54c2e9b30b176a3",
    "seven_fixed_start": "f5f816eeb3d8b531ff030f4b43b2f2338ccf0d2257a5684b034e1f8dc8ee1973",
}
SOURCE_SECTION_NAMES = (b".text", b".rdata", b".data", b".rsrc", b".psncode", b".psndata", b".shopai")
NON_ADDRESS_CHUNKS = {0x183A9, 0x183BF, 0x18428, 0x1B56E, 0x41444, 0x42FB4, 0x4317F}
EXPECTED_CHUNK_COUNTS = {2: 7, 3: 16, 4: 1315}
CODE_RAW_SIZE = 0x3000
PSN_CACHE_SIZE = 0x10000
PSN_CACHE_USED = CAPACITY * 16
PSN_CODE_SHA256 = "3425437f129a66bc290b97777b089ddc3bec4257c91d8bf23e4f223c0f20a14d"
PSN_OLD_POOL_BASE = 0x66B790
PSN_OLD_CACHE_BASE = 0x110C000
PSN_MARKER_OLD = b"N4K1"
PSN_MARKER_NEW = b"N4K8"
# Complete instruction-operand inventory in the added .psncode section.
PSN_POOL_OPERANDS = {
    0x01090233: 0x0066B790,
    0x0109070E: 0x0066B81E,
    0x0109072D: 0x0066B968,
    0x0109074D: 0x0066B790,
    0x01090957: 0x0078D024,
    0x0109097B: 0x0078D024,
    0x01090990: 0x0078D024,
    0x01091156: 0x0066BEE8,
}
WRAPPER_OFFSETS = (0x2200, 0x2300, 0x2400, 0x2500, 0x2600)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _align(value: int, alignment: int) -> int:
    return (value + alignment - 1) // alignment * alignment


def _chunks(before: bytes, after: bytes, lo: int, hi: int) -> list[tuple[int, int]]:
    if len(before) != len(after):
        raise ValueError("legacy template length mismatch")
    result: list[tuple[int, int]] = []
    pos = lo
    while pos < hi:
        if before[pos] == after[pos]:
            pos += 1
            continue
        start = pos
        while pos < hi and before[pos] != after[pos]:
            pos += 1
        result.append((start, pos))
    return result


def _source_geometry(source: bytes) -> tuple[int, int, int, int, int, int]:
    pe = pefile.PE(data=source, fast_load=True)
    try:
        sections = tuple(s.Name.rstrip(b"\0") for s in pe.sections)
        if sections != SOURCE_SECTION_NAMES or len(source) != 0x105000:
            raise ValueError("unsupported ESL2608 PE section layout")
        if pe.OPTIONAL_HEADER.ImageBase != IMAGE_BASE:
            raise ValueError("unsupported ESL2608 image base")
        if pe.OPTIONAL_HEADER.SectionAlignment != 0x1000 or pe.OPTIONAL_HEADER.FileAlignment != 0x1000:
            raise ValueError("unsupported ESL2608 alignment")
        if int(pe.OPTIONAL_HEADER.SizeOfImage) != 0xD2E000:
            raise ValueError("unexpected ESL2608 SizeOfImage")
        if pe.get_overlay_data_start_offset() is not None:
            raise ValueError("ESL2608 overlay would be displaced")
        last = pe.sections[-1]
        pool_rva = _align(int(last.VirtualAddress) + max(int(last.Misc_VirtualSize), int(last.SizeOfRawData)), 0x1000)
        pool_va = IMAGE_BASE + pool_rva
        section_table = pe.sections[0].get_file_offset()
        if source[section_table + 7 * 40 : section_table + 10 * 40] != bytes(120):
            raise ValueError("new section headers are not empty")
        if pool_rva != 0xD2E000 or section_table + 10 * 40 > int(pe.OPTIONAL_HEADER.SizeOfHeaders):
            raise ValueError("insufficient or unexpected PE section-header space")
        psn = pe.sections[4]
        psn_payload = source[psn.PointerToRawData : psn.PointerToRawData + psn.SizeOfRawData]
        if digest(psn_payload) != PSN_CODE_SHA256:
            raise ValueError("unexpected .psncode payload")
        pe_offset = int(pe.DOS_HEADER.e_lfanew)
        opt_offset = pe_offset + 24
        return pool_rva, pool_va, section_table, pe_offset, opt_offset, int(pe.sections[3].PointerToRawData)
    finally:
        pe.close()


def _port_text(source: bytes, legacy: bytes, template: bytes, out: bytearray, delta: int) -> dict[int, int]:
    geometry = layout(CAPACITY)
    counts = {2: 0, 3: 0, 4: 0}
    list_relative_start = geometry.regions[3].new_start - ACTIVE_BULK_BASE
    list_relative_end = geometry.regions[-1].new_end - ACTIVE_BULK_BASE
    for start, end in _chunks(legacy, template, 0x1000, 0xE5000):
        size = end - start
        if size not in counts or source[start:end] != legacy[start:end]:
            raise ValueError(f"unsupported 2608/G2 .text collision or change at 0x{start:X}")
        if size == 4:
            old_value = struct.unpack_from("<I", template, start)[0]
            if not geometry.regions[0].new_start <= old_value <= geometry.regions[-1].new_end:
                raise ValueError(f"unclassified G2 relocated dword at 0x{start:X}")
            if source[start : start + 4] != legacy[start : start + 4]:
                raise ValueError(f"full dword preimage mismatch at 0x{start:X}")
            struct.pack_into("<I", out, start, old_value + delta)
        elif size == 3:
            old_value = struct.unpack_from("<I", template, start)[0]
            if not list_relative_start - 0x10 <= old_value <= list_relative_end + 0x10:
                raise ValueError(f"unclassified G2 active-list relative dword at 0x{start:X}")
            if source[start : start + 4] != legacy[start : start + 4]:
                raise ValueError(f"full active-relative preimage mismatch at 0x{start:X}")
            struct.pack_into("<I", out, start, old_value + delta)
        elif start in NON_ADDRESS_CHUNKS:
            out[start:end] = template[start:end]
        else:
            raise ValueError(f"unclassified G2 non-address edit at 0x{start:X}")
        counts[size] += 1
    if counts != EXPECTED_CHUNK_COUNTS:
        raise ValueError(f"G2 .text edit inventory changed: {counts}")
    return counts


def _set_marker(code: bytes) -> bytes:
    if code.count(PSN_MARKER_OLD) != 1:
        raise ValueError("G2 save marker operand missing or ambiguous")
    return code.replace(PSN_MARKER_OLD, PSN_MARKER_NEW)


def _legacy_cache_clear(code: bytes, cache_va: int) -> bytes:
    epilogue = bytes.fromhex("58595f5ec3")
    if not code.endswith(epilogue):
        raise ValueError("unexpected legacy fallback epilogue")
    clear = b"\x31\xc0\xbf" + struct.pack("<I", cache_va) + b"\xb9" + struct.pack("<I", PSN_CACHE_USED // 4) + b"\xf3\xab"
    return code[: -len(epilogue)] + clear + epilogue


def _emit_wide_compatible_load_wrapper(start_va: int, flag_va: int, fallback_va: int, sidecars: list[tuple[int, int]]) -> bytes:
    """The sixth 2608 sidecar makes the historical rel8 legacy branch overflow."""
    code = bytearray(b"\x55\x89\xe5\x53")

    def stream(buffer: int | None, size: int | None, original: bool = False) -> None:
        if original:
            code.extend(b"\xff\x75\x14\xff\x75\x10\xff\x75\x0c\xff\x75\x08")
        else:
            assert buffer is not None and size is not None
            code.extend(b"\xff\x75\x14\x6a\x01\x68" + struct.pack("<I", size))
            code.extend(b"\x68" + struct.pack("<I", buffer))
        code.extend(_call(start_va + len(code), LOAD_STREAM_FN))
        code.extend(b"\x83\xc4\x10")

    stream(None, None, original=True)
    code.extend(b"\x89\xc3\x83\x3d" + struct.pack("<I", flag_va) + b"\x01")
    legacy_jump = len(code)
    code.extend(b"\x0f\x85\0\0\0\0")  # jne rel32 to legacy fallback
    for address, size in sidecars:
        stream(address, size)
    done_jump = len(code)
    code.extend(b"\xeb\0")
    legacy = len(code)
    code.extend(_call(start_va + len(code), fallback_va))
    done = len(code)
    code.extend(b"\x89\xd8\x5b\xc9\xc3")
    struct.pack_into("<i", code, legacy_jump + 2, legacy - (legacy_jump + 6))
    if not 0 <= done - (done_jump + 2) <= 127:
        raise ValueError("load-wrapper completion jump exceeds rel8 range")
    code[done_jump + 1] = done - (done_jump + 2)
    if len(code) > 0x100:
        raise ValueError("2608 compatible load wrapper exceeds code cave")
    return bytes(code)


def _wrappers(template: bytes, delta: int, source_rsrc_raw: int, cache_va: int) -> bytes:
    geometry = layout(CAPACITY)
    old_rsrc_va = geometry.rsrc.new_start
    shifted_regions = [replace(region, new_start=region.new_start + delta, new_end=region.new_end + delta) for region in geometry.regions[1:]]
    sidecars_old = [(r.new_start, r.new_end - r.new_start) for r in geometry.regions[1:]]
    sidecars_new = [(r.new_start, r.new_end - r.new_start) for r in shifted_regions]

    def emit(rsrc_va: int, sidecars: list[tuple[int, int]], regions: list[Any]) -> tuple[bytes, ...]:
        return (
            _emit_stream_wrapper(rsrc_va + 0x2200, SAVE_STREAM_FN, sidecars),
            _emit_compatible_load_wrapper(rsrc_va + 0x2300, rsrc_va - 0x100, rsrc_va + 0x2600, sidecars),
            _emit_save_header_wrapper(rsrc_va + 0x2400),
            _emit_load_header_wrapper(rsrc_va + 0x2500, rsrc_va - 0x100),
            _emit_legacy_copy_wrapper(regions),
        )

    original_codes = emit(old_rsrc_va, sidecars_old, list(geometry.regions[1:]))
    expanded_sidecars = [*sidecars_new, (cache_va, PSN_CACHE_USED)]
    new_rsrc_va = old_rsrc_va + delta
    relocated_codes = (
        _emit_stream_wrapper(new_rsrc_va + 0x2200, SAVE_STREAM_FN, expanded_sidecars),
        _emit_wide_compatible_load_wrapper(new_rsrc_va + 0x2300, new_rsrc_va - 0x100, new_rsrc_va + 0x2600, expanded_sidecars),
        _set_marker(_emit_save_header_wrapper(new_rsrc_va + 0x2400)),
        _set_marker(_emit_load_header_wrapper(new_rsrc_va + 0x2500, new_rsrc_va - 0x100)),
        _legacy_cache_clear(_emit_legacy_copy_wrapper(shifted_regions), cache_va),
    )
    raw = bytearray(CODE_RAW_SIZE)
    for offset, original, relocated in zip(WRAPPER_OFFSETS, original_codes, relocated_codes):
        if template[source_rsrc_raw + offset : source_rsrc_raw + offset + len(original)] != original:
            raise ValueError(f"G2 wrapper template mismatch at 0x{offset:X}")
        if offset + len(relocated) > CODE_RAW_SIZE or len(relocated) > 0x100:
            raise ValueError("relocated G2 wrapper exceeds code section")
        raw[offset : offset + len(relocated)] = relocated
    return bytes(raw)


def _port_psncode(source: bytes, out: bytearray, pool_va: int, cache_va: int) -> None:
    psn_raw, psn_va = 0xFC000, 0x01090000
    if digest(source[psn_raw : psn_raw + 0x2000]) != PSN_CODE_SHA256:
        raise ValueError(".psncode source changed")
    for va, old_value in PSN_POOL_OPERANDS.items():
        offset = psn_raw + va - psn_va
        if struct.unpack_from("<I", source, offset)[0] != old_value:
            raise ValueError(f".psncode pool operand mismatch at 0x{va:08x}")
        struct.pack_into("<I", out, offset, pool_va + old_value - PSN_OLD_POOL_BASE)
    for va, old_value, new_value in (
        (0x0109024D, 1200, CAPACITY),  # cache lookup upper bound
        (0x01090257, PSN_OLD_CACHE_BASE, cache_va),
        (0x0109115B, 1199, CAPACITY - 1),  # post-load per-unit reset
    ):
        offset = psn_raw + va - psn_va
        if struct.unpack_from("<I", source, offset)[0] != old_value:
            raise ValueError(f".psncode bound/cache preimage mismatch at 0x{va:08x}")
        struct.pack_into("<I", out, offset, new_value)


def _section(name: bytes, virtual_size: int, virtual_address: int, raw_size: int, raw_pointer: int, characteristics: int) -> bytes:
    if len(name) > 8:
        raise ValueError("PE section name too long")
    return struct.pack("<8sIIIIIIHHI", name, virtual_size, virtual_address, raw_size, raw_pointer, 0, 0, 0, 0, characteristics)


def build_candidate(source: bytes, legacy: bytes, stock: bytes) -> tuple[bytes, dict[str, Any]]:
    variant_hash = digest(source)
    variant = next((name for name, sha in SOURCE_SHA256.items() if sha == variant_hash), None)
    if variant is None:
        raise ValueError("unsupported ESL2608 source SHA256")
    if digest(legacy) != LEGACY_SHA256:
        raise ValueError("unsupported ESL2606 legacy reference SHA256")
    pool_rva, pool_va, section_table, pe_offset, opt_offset, source_rsrc_raw = _source_geometry(source)
    template, template_report = build_legacy_candidate(legacy, stock)
    if digest(template) != TEMPLATE_SHA256:
        raise ValueError("G2 corrected ESL2606 template SHA256 mismatch")
    geometry = layout(CAPACITY)
    delta = pool_va - geometry.regions[0].new_start
    bss_span = geometry.rsrc.new_start - geometry.regions[0].new_start
    code_rva = pool_rva + bss_span
    if code_rva != 0x1493000 or source_rsrc_raw != 0xF9000:
        raise ValueError("unexpected 2608/G2 section placement")
    out = bytearray(source)
    text_counts = _port_text(source, legacy, template, out, delta)
    cache_rva = code_rva + CODE_RAW_SIZE
    cache_va = IMAGE_BASE + cache_rva
    _port_psncode(source, out, pool_va, cache_va)
    raw_offset = len(out)
    out.extend(_wrappers(template, delta, source_rsrc_raw, cache_va))
    out[section_table + 7 * 40 : section_table + 8 * 40] = _section(b".g2bss", bss_span, pool_rva, 0, 0, 0xC0000080)
    out[section_table + 8 * 40 : section_table + 9 * 40] = _section(b".g2code", CODE_RAW_SIZE, code_rva, CODE_RAW_SIZE, raw_offset, 0x60000020)
    out[section_table + 9 * 40 : section_table + 10 * 40] = _section(b".g2psn", PSN_CACHE_SIZE, cache_rva, 0, 0, 0xC0000080)
    struct.pack_into("<H", out, pe_offset + 6, 10)
    struct.pack_into("<I", out, opt_offset + 4, struct.unpack_from("<I", source, opt_offset + 4)[0] + CODE_RAW_SIZE)
    struct.pack_into("<I", out, opt_offset + 12, struct.unpack_from("<I", source, opt_offset + 12)[0] + bss_span + PSN_CACHE_SIZE)
    struct.pack_into("<I", out, opt_offset + 56, cache_rva + PSN_CACHE_SIZE)
    candidate = bytes(out)
    pe = pefile.PE(data=candidate, fast_load=True)
    try:
        if pe.get_warnings() or len(pe.sections) != 10:
            raise ValueError(f"invalid composed PE: {pe.get_warnings()}")
        if [s.Name.rstrip(b"\0") for s in pe.sections[:7]] != list(SOURCE_SECTION_NAMES):
            raise ValueError("2608 sections were not preserved")
        if any(candidate[s.PointerToRawData : s.PointerToRawData + s.SizeOfRawData] != source[s.PointerToRawData : s.PointerToRawData + s.SizeOfRawData] for s in (*pe.sections[1:4], *pe.sections[5:7])):
            raise ValueError("2608 non-text source section payload changed")
    finally:
        pe.close()
    return candidate, {
        "variant": variant,
        "source_sha256": variant_hash,
        "candidate_sha256": digest(candidate),
        "template_sha256": TEMPLATE_SHA256,
        "stock_sha256": template_report["stock_sha256"],
        "usable_slots": 4092,
        "owner_count_seed": 500,
        "pool_base_va": f"0x{pool_va:08x}",
        "code_base_va": f"0x{IMAGE_BASE + code_rva:08x}",
        "psn_cache_va": f"0x{cache_va:08x}",
        "save_marker": PSN_MARKER_NEW.decode(),
        "relocation_delta": f"0x{delta:x}",
        "text_edit_chunks": text_counts,
        "release_status": "RUNTIME_UNVERIFIED",
    }


def create_copy(source: Path, legacy: Path, stock: Path, destination: Path) -> dict[str, Any]:
    inputs = {source.resolve(), legacy.resolve(), stock.resolve()}
    if destination.resolve() in inputs:
        raise ValueError("refusing to overwrite an input EXE")
    candidate, report = build_candidate(source.read_bytes(), legacy.read_bytes(), stock.read_bytes())
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb") as stream:
        stream.write(candidate)
    if digest(destination.read_bytes()) != report["candidate_sha256"]:
        raise ValueError("candidate write verification failed")
    return report


def restore_copy(destination: Path, source: Path, legacy: Path, stock: Path) -> str:
    original = source.read_bytes()
    candidate, _ = build_candidate(original, legacy.read_bytes(), stock.read_bytes())
    if destination.read_bytes() != candidate:
        raise ValueError("refusing restore: destination is not this exact candidate")
    temporary = Path(str(destination) + ".restore.tmp")
    with temporary.open("xb") as stream:
        stream.write(original)
    temporary.replace(destination)
    return digest(original)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("create-copy")
    create.add_argument("source", type=Path)
    create.add_argument("legacy", type=Path)
    create.add_argument("stock", type=Path)
    create.add_argument("destination", type=Path)
    restore = sub.add_parser("restore")
    restore.add_argument("destination", type=Path)
    restore.add_argument("source", type=Path)
    restore.add_argument("legacy", type=Path)
    restore.add_argument("stock", type=Path)
    args = parser.parse_args()
    if args.command == "create-copy":
        print(create_copy(args.source, args.legacy, args.stock, args.destination))
    else:
        print(restore_copy(args.destination, args.source, args.legacy, args.stock))


if __name__ == "__main__":
    main()
