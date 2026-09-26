from pathlib import Path
import struct

import capstone
import pefile
import pytest

from patches.population import g2_full_capacity_persistence_compat_v1 as mod
from patches.population import g2_full_capacity_persistence_v1 as persistence_mod
from patches.population.g2_full_capacity_supply5000_owner1200_v1 import (
    build_candidate as build_product_candidate,
)


ORIGINAL = Path(__file__).resolve().parents[2] / "Syw2plus" / "syw2plus_original.exe"


@pytest.fixture
def original() -> bytes:
    if not ORIGINAL.exists():
        pytest.skip("Local original game required")
    return ORIGINAL.read_bytes()


def _target(data: bytes, va: int) -> int:
    off = va - mod.IMAGE_BASE
    return va + 5 + struct.unpack_from("<i", data, off + 1)[0]


def test_n4001_adds_header_gate_and_writable_bss_flag(original: bytes) -> None:
    candidate, report = mod.build_candidate(original, 4001)
    assert _target(candidate, mod.SAVE_HEADER_CALL_VA) == int(report["save_header_wrapper_va"], 16)
    assert _target(candidate, mod.LOAD_HEADER_CALL_VA) == int(report["load_header_wrapper_va"], 16)
    pe = pefile.PE(data=candidate, fast_load=True)
    try:
        data = next(s for s in pe.sections if s.Name.rstrip(b"\0") == b".data")
        flag = int(report["flag_va"], 16)
        assert mod.IMAGE_BASE + data.VirtualAddress + data.Misc_VirtualSize >= flag + 4
    finally:
        pe.close()


def test_legacy_copy_covers_stock_prefix_and_zeros_every_tail(original: bytes) -> None:
    _candidate, report = mod.build_candidate(original, 4001)
    result = mod.layout(4001)
    code = mod._emit_legacy_copy_wrapper(result.regions[1:])
    engine = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    insns = list(engine.disasm(code, int(report["legacy_copy_wrapper_va"], 16)))
    mov_esi = [int(i.op_str.split(", ")[1], 16) for i in insns if i.mnemonic == "mov" and i.op_str.startswith("esi,")]
    mov_edi = [int(i.op_str.split(", ")[1], 16) for i in insns if i.mnemonic == "mov" and i.op_str.startswith("edi,")]
    expected_esi = []
    expected_edi = []
    for region in result.regions[1:]:
        counted = region.name in {
            "category_slot_list_a",
            "category_slot_list_b",
            "active_slot_list",
        }
        expected_esi.append(region.old_start)
        old_entries_size = region.old_end - region.old_start - (2 if counted else 0)
        expected_edi.extend((region.new_start, region.new_start + old_entries_size))
        if counted:
            expected_esi.append(region.old_end - 2)
            expected_edi.append(region.new_end - 2)
    assert mov_esi == expected_esi
    assert mov_edi == expected_edi


def test_compat_wrappers_are_contained_in_rsrc_cave_without_overlap(original: bytes) -> None:
    candidate, report = mod.build_candidate(original, 4001)
    result = mod.layout(4001)
    pe = pefile.PE(data=candidate, fast_load=True)
    try:
        rsrc = next(s for s in pe.sections if s.Name.rstrip(b"\0") == b".rsrc")
        rsrc_va = mod.IMAGE_BASE + int(rsrc.VirtualAddress)
        rsrc_size = int(rsrc.Misc_VirtualSize)
        assert int(rsrc.Characteristics) & mod.RSRC_EXECUTE_CODE_FLAGS == mod.RSRC_EXECUTE_CODE_FLAGS

        flag_va = int(report["flag_va"], 16)
        save_header_va = int(report["save_header_wrapper_va"], 16)
        load_header_va = int(report["load_header_wrapper_va"], 16)
        fallback_va = int(report["legacy_copy_wrapper_va"], 16)
        load_wrapper_va = rsrc_va + persistence_mod.LOAD_WRAPPER_OFFSET
        sidecars = [
            (region.new_start, region.new_end - region.new_start) for region in result.regions[1:]
        ]

        wrappers = [
            (
                "LOAD_WRAPPER",
                persistence_mod.LOAD_WRAPPER_OFFSET,
                mod._emit_compatible_load_wrapper(load_wrapper_va, flag_va, fallback_va, sidecars),
            ),
            (
                "SAVE_HEADER",
                mod.SAVE_HEADER_WRAPPER_OFFSET,
                mod._emit_save_header_wrapper(save_header_va),
            ),
            (
                "LOAD_HEADER",
                mod.LOAD_HEADER_WRAPPER_OFFSET,
                mod._emit_load_header_wrapper(load_header_va, flag_va),
            ),
            (
                "LEGACY_COPY",
                mod.LEGACY_COPY_WRAPPER_OFFSET,
                mod._emit_legacy_copy_wrapper(result.regions[1:]),
            ),
        ]

        spans: list[tuple[int, int]] = []
        for name, offset, code in wrappers:
            length = len(code)
            end_offset = offset + length
            assert end_offset <= mod.RSRC_COMPAT_END_OFFSET, name
            start_va = rsrc_va + offset
            end_va = rsrc_va + end_offset - 1
            assert rsrc_va <= start_va < rsrc_va + rsrc_size, name
            assert rsrc_va <= end_va < rsrc_va + rsrc_size, name
            spans.append((offset, end_offset))

        for i, (start_a, end_a) in enumerate(spans):
            for start_b, end_b in spans[i + 1 :]:
                assert start_a >= end_b or start_b >= end_a
    finally:
        pe.close()


def test_n1200_has_no_compatibility_header(original: bytes) -> None:
    _candidate, report = mod.build_candidate(original, 1200)
    assert report["compatibility_header"] is False


def test_n1200_compat_and_persistence_are_byte_equal_to_the_product_candidate(
    original: bytes,
) -> None:
    product, _product_report = build_product_candidate(original, 1200)
    persistence_candidate, _persistence_report = persistence_mod.build_candidate(original, 1200)
    compat_candidate, _compat_report = mod.build_candidate(original, 1200)
    assert persistence_candidate == product
    assert compat_candidate == product
