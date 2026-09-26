from __future__ import annotations

import hashlib
import struct
from pathlib import Path

import pefile
import pytest

from patches.population import g2_esl2606_pool10000_owner1200 as mod
from patches.population.fixed_owner_count_1200 import OWNER_COUNT_AFTER, OWNER_COUNT_FILE_OFFSET
from patches.population.fixed_supply_5000 import EDITS as FIXED_SUPPLY_EDITS
from patches.population.full_tail_relocation_storage_layout_v1 import layout


ROOT = Path(__file__).resolve().parents[2]
STOCK = ROOT / "Syw2plus" / "syw2plus_original.exe"
REFERENCES = (
    ROOT.parent / "260921_temp" / "[ESL]Syw2plus 2606_장수7명_전비1600-200-3000.exe",
    ROOT.parent / "260921_temp" / "[ESL]Syw2plus 2606_장수7명_전비1600-200-3000_시작자리고정.exe",
)


@pytest.fixture(scope="module")
def binaries() -> tuple[bytes, tuple[bytes, bytes]]:
    if not STOCK.exists() or any(not path.exists() for path in REFERENCES):
        pytest.skip("local pinned stock and exact ESL 2606 references required")
    return STOCK.read_bytes(), tuple(path.read_bytes() for path in REFERENCES)  # type: ignore[return-value]


@pytest.fixture(scope="module")
def candidates(
    binaries: tuple[bytes, tuple[bytes, bytes]],
) -> tuple[tuple[bytes, dict[str, object]], tuple[bytes, dict[str, object]]]:
    stock, references = binaries
    return (mod.build_candidate(references[0], stock), mod.build_candidate(references[1], stock))


def test_two_exact_variants_preserve_supply_and_start_position(
    binaries: tuple[bytes, tuple[bytes, bytes]],
    candidates: tuple[tuple[bytes, dict[str, object]], tuple[bytes, dict[str, object]]],
) -> None:
    _stock, references = binaries
    result_a, report_a = candidates[0]
    result_b, report_b = candidates[1]
    assert [report_a["variant"], report_b["variant"]] == ["2606", "2606_fixed_start"]
    assert all(report["capacity_slots"] == 10001 for report in (report_a, report_b))
    assert all(report["usable_slots"] == 10000 for report in (report_a, report_b))
    assert all(report["max_packed_command_slot"] == 4095 for report in (report_a, report_b))
    assert all(report["release_status"] == "BLOCKED_12_BIT_COMMAND_SLOT" for report in (report_a, report_b))
    assert all(report["owner_count_cap"] == 1200 for report in (report_a, report_b))
    for reference, result in zip(references, (result_a, result_b)):
        assert result[OWNER_COUNT_FILE_OFFSET : OWNER_COUNT_FILE_OFFSET + 4] == OWNER_COUNT_AFTER
        for offset, before, _after in FIXED_SUPPLY_EDITS:
            assert result[offset : offset + len(before)] == reference[offset : offset + len(before)]
        assert result[mod.NOP_TEST_OFFSET : mod.NOP_TEST_OFFSET + 9] == mod.NOP_TEST_ESL
        assert result[mod.PREFIXED_WRITE_OFFSET : mod.PREFIXED_WRITE_OFFSET + 4] == b"\x3e\xc7\x04\xcd"
        assert struct.unpack_from("<I", result, mod.PREFIXED_WRITE_ADDRESS_OFFSET)[0] == 0x0108C200
        assert result[mod.PREFIXED_WRITE_ADDRESS_OFFSET + 4 : mod.PREFIXED_WRITE_OFFSET + 12] == bytes.fromhex("20030000")
        pe = pefile.PE(data=result, fast_load=True)
        try:
            rsrc = next(section for section in pe.sections if section.Name.rstrip(b"\0") == b".rsrc")
            data = next(section for section in pe.sections if section.Name.rstrip(b"\0") == b".data")
            mapped = layout(10001)
            assert mod.CAPACITY == mapped.capacity
            assert 0x400000 + int(rsrc.VirtualAddress) == mapped.rsrc.new_start
            assert 0x400000 + int(data.VirtualAddress) + int(data.Misc_VirtualSize) >= mapped.regions[-1].new_end
        finally:
            pe.close()
    # The only intentional distinction between these exact variants is their
    # four original start-position bytes; all G2 changes must be identical.
    assert {i for i, (a, b) in enumerate(zip(result_a, result_b)) if a != b} == {
        0x1F2B0, 0x2FBB1, 0x2FBB2, 0x2FBB3
    }


def test_rejects_unsupported_version_and_bad_stock(
    binaries: tuple[bytes, tuple[bytes, bytes]],
) -> None:
    stock, references = binaries
    altered = bytearray(references[0])
    altered[0x1000] ^= 1
    with pytest.raises(ValueError, match="unsupported ESL"):
        mod.build_candidate(bytes(altered), stock)
    altered_stock = bytearray(stock)
    altered_stock[0x1000] ^= 1
    with pytest.raises(ValueError, match="pinned stock"):
        mod.build_candidate(references[0], bytes(altered_stock))


def test_esl_active_bulk_relative_fixups_are_exact_and_nonoverlapping() -> None:
    candidate = bytearray(0xB00000)
    for va, (_kind, old_bytes) in mod.ACTIVE_BULK_RELATIVE_SITES.items():
        offset = va - 0x00400000
        candidate[offset : offset + len(old_bytes)] = old_bytes

    patched = mod.apply_active_bulk_relative_fixups(candidate, 4001)
    active = layout(4001).regions[5]
    expected = {
        "0x004a39da": active.new_start + active.array_new_span - mod.ACTIVE_BULK_BASE,
        "0x004a39e6": active.new_start - mod.ACTIVE_BULK_BASE,
        "0x004a3a1b": active.new_start + active.array_new_span - mod.ACTIVE_BULK_BASE,
    }
    assert patched == {key: value & 0xFFFFFFFF for key, value in expected.items()}
    for va, (_kind, old_bytes) in mod.ACTIVE_BULK_RELATIVE_SITES.items():
        offset = va - 0x00400000
        assert candidate[offset : offset + len(old_bytes) - 4] == old_bytes[:-4]
        assert int.from_bytes(candidate[offset + len(old_bytes) - 4 : offset + len(old_bytes)], "little") == patched[f"0x{va:08x}"]

    corrupted = bytearray(candidate)
    va, (_kind, old_bytes) = next(iter(mod.ACTIVE_BULK_RELATIVE_SITES.items()))
    corrupted[va - 0x00400000] ^= 1
    with pytest.raises(ValueError, match="old bytes mismatch"):
        mod.apply_active_bulk_relative_fixups(corrupted, 4001)


def test_diagnostic_candidate_retains_unsafe_12_bit_command_codec(
    binaries: tuple[bytes, tuple[bytes, bytes]],
    candidates: tuple[tuple[bytes, dict[str, object]], tuple[bytes, dict[str, object]]],
) -> None:
    _stock, references = binaries
    # Encoder/decoder old bytes are an explicit release blocker, not proof of
    # a playable 10,000-slot command path.
    sites = {
        0x004AE613: bytes.fromhex("c1e20c"),
        0x004AE619: bytes.fromhex("668917"),
        0x004AE9D2: bytes.fromhex("81e6ff0f0000"),
        0x004AEA35: bytes.fromhex("25ff0f0000"),
    }
    for reference, (candidate, report) in zip(references, candidates):
        for va, old in sites.items():
            offset = va - 0x00400000
            assert reference[offset : offset + len(old)] == old
            assert candidate[offset : offset + len(old)] == old
        assert report["release_status"] == "BLOCKED_12_BIT_COMMAND_SLOT"


def test_release_copy_refuses_known_unplayable_slot_encoding(
    tmp_path: Path, binaries: tuple[bytes, tuple[bytes, bytes]]
) -> None:
    stock, references = binaries
    source = tmp_path / "reference" / "input.exe"
    source.parent.mkdir()
    source.write_bytes(references[0])
    stock_path = tmp_path / "stock.exe"
    stock_path.write_bytes(stock)
    destination = tmp_path / "output" / "patched.exe"
    with pytest.raises(ValueError, match="12-bit.*4095"):
        mod.create_copy(source, stock_path, destination)
    assert source.read_bytes() == references[0]
    assert not destination.exists()
    assert not Path(str(destination) + ".original").exists()


def test_restore_existing_diagnostic_candidate(
    tmp_path: Path, binaries: tuple[bytes, tuple[bytes, bytes]]
) -> None:
    stock, references = binaries
    stock_path = tmp_path / "stock.exe"
    stock_path.write_bytes(stock)
    destination = tmp_path / "patched.exe"
    candidate, report = mod.build_candidate(references[0], stock)
    destination.write_bytes(candidate)
    Path(str(destination) + ".original").write_bytes(references[0])
    assert report["candidate_sha256"] == hashlib.sha256(destination.read_bytes()).hexdigest()
    corrupted = bytearray(destination.read_bytes())
    corrupted[0x1200] ^= 1
    destination.write_bytes(corrupted)
    with pytest.raises(ValueError, match="refusing restore"):
        mod.restore_copy(destination, stock_path)
    corrupted[0x1200] ^= 1
    destination.write_bytes(corrupted)
    assert mod.restore_copy(destination, stock_path) == mod.digest(references[0])
    assert destination.read_bytes() == references[0]


def test_refuses_writing_beside_reference(tmp_path: Path, binaries: tuple[bytes, tuple[bytes, bytes]]) -> None:
    stock, references = binaries
    source = tmp_path / "reference.exe"
    source.write_bytes(references[0])
    stock_path = tmp_path / "stock.exe"
    stock_path.write_bytes(stock)
    with pytest.raises(ValueError, match="reference EXE directory"):
        mod.create_copy(source, stock_path, tmp_path / "output.exe")
