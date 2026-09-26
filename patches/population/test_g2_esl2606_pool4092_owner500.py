from __future__ import annotations

import hashlib
from pathlib import Path

import pefile
import pytest

from patches.population import g2_esl2606_pool4092_owner500 as mod
from patches.population.fixed_supply_5000 import EDITS as FIXED_SUPPLY_EDITS
from patches.population.full_tail_relocation_storage_layout_v1 import layout


ROOT = Path(__file__).resolve().parents[2]
STOCK = ROOT / "Syw2plus" / "syw2plus_original.exe"
REFERENCE = ROOT.parent / "260921_temp" / "[ESL]Syw2plus 2606_장수7명_전비1600-200-3000.exe"
FIXED_START_REFERENCE = ROOT.parent / "260921_temp" / (
    "[ESL]Syw2plus 2606_장수7명_전비1600-200-3000_시작자리고정.exe"
)


@pytest.fixture(scope="module")
def binaries() -> tuple[bytes, bytes]:
    if not STOCK.exists() or not REFERENCE.exists():
        pytest.skip("local pinned stock and exact normal ESL 2606 reference required")
    return STOCK.read_bytes(), REFERENCE.read_bytes()


def test_builds_one_normal_2606_variant_with_4092_pool_and_500_owner_cap(
    binaries: tuple[bytes, bytes],
) -> None:
    stock, reference = binaries
    candidate, report = mod.build_candidate(reference, stock)

    assert report["variant"] == "2606"
    assert report["capacity_slots"] == 4093
    assert report["usable_slots"] == 4092
    assert report["max_packed_command_slot"] == 4095
    assert report["release_status"] == "RUNTIME_UNVERIFIED"
    assert report["owner_count_cap"] == 500
    assert candidate[mod.OWNER_COUNT_FILE_OFFSET : mod.OWNER_COUNT_FILE_OFFSET + 4] == (
        mod.OWNER_COUNT_AFTER_500
    )
    for offset, before, _after in FIXED_SUPPLY_EDITS:
        assert candidate[offset : offset + len(before)] == reference[offset : offset + len(before)]

    pe = pefile.PE(data=candidate, fast_load=True)
    try:
        rsrc = next(section for section in pe.sections if section.Name.rstrip(b"\0") == b".rsrc")
        data = next(section for section in pe.sections if section.Name.rstrip(b"\0") == b".data")
        mapped = layout(mod.CAPACITY)
        assert 0x400000 + int(rsrc.VirtualAddress) == mapped.rsrc.new_start
        assert 0x400000 + int(data.VirtualAddress) + int(data.Misc_VirtualSize) >= (
            mapped.regions[-1].new_end
        )
    finally:
        pe.close()


def test_idle_hero_portrait_producer_lookup_covers_relocated_high_slots(
    binaries: tuple[bytes, bytes],
) -> None:
    stock, reference = binaries
    candidate, report = mod.build_candidate(reference, stock)
    assert report["producer_lookup_capacity"] == mod.CAPACITY
    for va, before, after in mod.PRODUCER_LOOKUP_EDITS:
        offset = va - 0x00400000
        assert reference[offset : offset + len(before)] == before
        assert candidate[offset : offset + len(after)] == after
    assert len({va for va, _before, _after in mod.PRODUCER_LOOKUP_EDITS}) == 3
    # Original lookup walks only 0..1199; a newly created game can place its
    # only producer in slot 4092, so both modulo sites and loop bound must move.
    assert mod.CAPACITY == 4093


def test_producer_lookup_rejects_unexpected_code_bytes() -> None:
    image = bytearray(b"\0" * 0x19000)
    with pytest.raises(ValueError, match="producer lookup.*old bytes mismatch"):
        mod.apply_producer_lookup_fixups(image)


def test_accepts_only_the_pinned_normal_variant_and_stock(
    binaries: tuple[bytes, bytes],
) -> None:
    stock, reference = binaries
    if FIXED_START_REFERENCE.exists():
        with pytest.raises(ValueError, match="unsupported ESL"):
            mod.build_candidate(FIXED_START_REFERENCE.read_bytes(), stock)
    altered_reference = bytearray(reference)
    altered_reference[0x1000] ^= 1
    with pytest.raises(ValueError, match="unsupported ESL"):
        mod.build_candidate(bytes(altered_reference), stock)

    altered_stock = bytearray(stock)
    altered_stock[0x1000] ^= 1
    with pytest.raises(ValueError, match="pinned stock"):
        mod.build_candidate(reference, bytes(altered_stock))


def test_create_restore_is_copy_only_and_hash_guarded(
    tmp_path: Path, binaries: tuple[bytes, bytes]
) -> None:
    stock, reference = binaries
    source = tmp_path / "reference" / "input.exe"
    source.parent.mkdir()
    source.write_bytes(reference)
    stock_path = tmp_path / "stock.exe"
    stock_path.write_bytes(stock)
    destination = tmp_path / "output" / "candidate.exe"

    report = mod.create_copy(source, stock_path, destination)
    assert report["candidate_sha256"] == hashlib.sha256(destination.read_bytes()).hexdigest()
    assert source.read_bytes() == reference
    assert Path(str(destination) + ".original").read_bytes() == reference

    altered = bytearray(destination.read_bytes())
    altered[0x1200] ^= 1
    destination.write_bytes(altered)
    with pytest.raises(ValueError, match="refusing restore"):
        mod.restore_copy(destination, stock_path)
    # Rebuild the exact candidate through the pure builder before restoring.
    candidate, _ = mod.build_candidate(reference, stock)
    destination.write_bytes(candidate)
    assert mod.restore_copy(destination, stock_path) == mod.digest(reference)
    assert destination.read_bytes() == reference


def test_refuses_writing_beside_reference(tmp_path: Path, binaries: tuple[bytes, bytes]) -> None:
    stock, reference = binaries
    source = tmp_path / "reference.exe"
    source.write_bytes(reference)
    stock_path = tmp_path / "stock.exe"
    stock_path.write_bytes(stock)
    with pytest.raises(ValueError, match="reference EXE directory"):
        mod.create_copy(source, stock_path, tmp_path / "output.exe")
