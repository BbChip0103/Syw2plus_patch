from __future__ import annotations

import hashlib
from pathlib import Path
import struct

import pefile
import pytest

from patches.population import g2_esl2608_pool4092_owner500 as mod
from patches.population.full_tail_relocation_storage_layout_v1 import layout


ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT.parent / "260921_temp"
LEGACY = INPUT / "[ESL]Syw2plus 2606_장수7명_전비1600-200-3000.exe"
STOCK = ROOT / "Syw2plus" / "syw2plus_original.exe"
SOURCES = {
    "shop": INPUT / "[ESL]Syw2plus 2608_AI상점개설.exe",
    "seven": INPUT / "[ESL]Syw2plus 2608_AI상점개설_장수7명_전비1600-200-3000.exe",
    "seven_fixed_start": INPUT / "[ESL]Syw2plus 2608_AI상점개설_장수7명_전비1600-200-3000_시작자리고정.exe",
}


@pytest.fixture(scope="module")
def references() -> tuple[bytes, bytes]:
    if not STOCK.is_file() or not LEGACY.is_file() or not all(p.is_file() for p in SOURCES.values()):
        pytest.skip("pinned local stock/ESL references are required")
    return LEGACY.read_bytes(), STOCK.read_bytes()


@pytest.mark.parametrize("variant", list(SOURCES))
def test_builds_three_exact_2608_variants_without_clobbering_shop_sections(
    variant: str, references: tuple[bytes, bytes]
) -> None:
    legacy, stock = references
    source = SOURCES[variant].read_bytes()
    candidate, report = mod.build_candidate(source, legacy, stock)
    assert report["variant"] == variant
    assert report["source_sha256"] == mod.SOURCE_SHA256[variant]
    assert report["candidate_sha256"] == hashlib.sha256(candidate).hexdigest()
    assert report["usable_slots"] == 4092
    assert report["owner_count_seed"] == 500
    assert report["save_marker"] == "N4K8"
    assert len(candidate) == len(source) + mod.CODE_RAW_SIZE
    pe = pefile.PE(data=candidate, fast_load=True)
    try:
        assert not pe.get_warnings()
        assert [s.Name.rstrip(b"\0") for s in pe.sections] == [
            *mod.SOURCE_SECTION_NAMES, b".g2bss", b".g2code", b".g2psn"
        ]
        assert pe.OPTIONAL_HEADER.SizeOfImage == 0x14A6000
        for section in (*pe.sections[1:4], *pe.sections[5:7]):
            start = section.PointerToRawData
            end = start + section.SizeOfRawData
            assert candidate[start:end] == source[start:end]
        bss, code, cache = pe.sections[7:10]
        assert bss.PointerToRawData == 0 and bss.SizeOfRawData == 0
        assert code.PointerToRawData == len(source) and code.SizeOfRawData == mod.CODE_RAW_SIZE
        assert cache.PointerToRawData == 0 and cache.SizeOfRawData == 0
        assert 0x400000 + bss.VirtualAddress == int(report["pool_base_va"], 16)
        assert 0x400000 + code.VirtualAddress == int(report["code_base_va"], 16)
        assert 0x400000 + cache.VirtualAddress == int(report["psn_cache_va"], 16)
        for left, right in zip(pe.sections, pe.sections[1:]):
            assert left.VirtualAddress + max(left.Misc_VirtualSize, left.SizeOfRawData) <= right.VirtualAddress
    finally:
        pe.close()
    for va, old in mod.PSN_POOL_OPERANDS.items():
        offset = 0xFC000 + va - 0x1090000
        assert struct.unpack_from("<I", source, offset)[0] == old
        assert struct.unpack_from("<I", candidate, offset)[0] == (
            int(report["pool_base_va"], 16) + old - mod.PSN_OLD_POOL_BASE
        )
    assert candidate[0xFC000:0xFC000 + 0x2000] != source[0xFC000:0xFC000 + 0x2000]
    for va, expected in (
        (0x0109024D, mod.CAPACITY),
        (0x01090257, int(report["psn_cache_va"], 16)),
        (0x0109115B, mod.CAPACITY - 1),
    ):
        assert struct.unpack_from("<I", candidate, 0xFC000 + va - 0x1090000)[0] == expected
    for call_va, wrapper_offset in (
        (0x440C70, 0x2400), (0x440F0C, 0x2200),
        (0x441040, 0x2500), (0x4412DC, 0x2300),
    ):
        offset = call_va - 0x400000
        assert candidate[offset] == 0xE8
        target = call_va + 5 + struct.unpack_from("<i", candidate, offset + 1)[0]
        assert target == int(report["code_base_va"], 16) + wrapper_offset
    assert source[0xF9000:0xFC000] == candidate[0xF9000:0xFC000]
    assert mod.PSN_MARKER_NEW in candidate[len(source):]
    assert mod.PSN_MARKER_OLD not in candidate[len(source):]


def test_rejects_unknown_version_and_mutated_template_inputs(references: tuple[bytes, bytes]) -> None:
    legacy, stock = references
    source = SOURCES["shop"].read_bytes()
    changed = bytearray(source)
    changed[0x1000] ^= 1
    with pytest.raises(ValueError, match="unsupported ESL2608"):
        mod.build_candidate(bytes(changed), legacy, stock)
    changed_legacy = bytearray(legacy)
    changed_legacy[0x1000] ^= 1
    with pytest.raises(ValueError, match="unsupported ESL2606"):
        mod.build_candidate(source, bytes(changed_legacy), stock)
    changed_stock = bytearray(stock)
    changed_stock[0x1000] ^= 1
    with pytest.raises(ValueError, match="pinned stock"):
        mod.build_candidate(source, legacy, bytes(changed_stock))


def test_2608_legacy_load_branch_reaches_fallback_not_previous_wrapper() -> None:
    geometry = layout(mod.CAPACITY)
    delta = 0xA2000
    code_va = geometry.rsrc.new_start + delta + 0x2300
    cache_va = 0x01896000
    sidecars = [
        (region.new_start + delta, region.new_end - region.new_start)
        for region in geometry.regions[1:]
    ] + [(cache_va, mod.PSN_CACHE_USED)]
    code = mod._emit_wide_compatible_load_wrapper(
        code_va, geometry.rsrc.new_start + delta - 0x100,
        geometry.rsrc.new_start + delta + 0x2600, sidecars,
    )
    branch = code.index(b"\x0f\x85")
    displacement = struct.unpack_from("<i", code, branch + 2)[0]
    target = branch + 6 + displacement
    assert code[target] == 0xE8  # call exact legacy-copy fallback
    assert target == len(code) - 10  # before mov eax,ebx; pop ebx; leave; ret
    assert 0 < target < 0x100


def test_copy_is_exclusive_and_restore_requires_exact_candidate(
    tmp_path: Path, references: tuple[bytes, bytes]
) -> None:
    legacy, stock = references
    source = tmp_path / "source.exe"
    source.write_bytes(SOURCES["shop"].read_bytes())
    legacy_path = tmp_path / "legacy.exe"
    legacy_path.write_bytes(legacy)
    stock_path = tmp_path / "stock.exe"
    stock_path.write_bytes(stock)
    destination = tmp_path / "candidate.exe"
    report = mod.create_copy(source, legacy_path, stock_path, destination)
    assert hashlib.sha256(destination.read_bytes()).hexdigest() == report["candidate_sha256"]
    assert source.read_bytes() == SOURCES["shop"].read_bytes()
    with pytest.raises(FileExistsError):
        mod.create_copy(source, legacy_path, stock_path, destination)
    corrupted = bytearray(destination.read_bytes())
    corrupted[-1] ^= 1
    destination.write_bytes(corrupted)
    with pytest.raises(ValueError, match="refusing restore"):
        mod.restore_copy(destination, source, legacy_path, stock_path)
    candidate, _ = mod.build_candidate(source.read_bytes(), legacy, stock)
    destination.write_bytes(candidate)
    assert mod.restore_copy(destination, source, legacy_path, stock_path) == mod.SOURCE_SHA256["shop"]
    assert destination.read_bytes() == source.read_bytes()
