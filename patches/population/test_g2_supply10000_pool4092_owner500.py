from pathlib import Path

import pefile
import pytest

from patches.population import g2_supply10000_pool4092_owner500 as mod
from patches.population.g2_full_capacity_persistence_compat_v1 import (
    build_candidate as build_compat_candidate,
)

ORIGINAL = Path(__file__).resolve().parents[2] / "Syw2plus" / "syw2plus_original.exe"


@pytest.fixture
def original() -> bytes:
    if not ORIGINAL.exists():
        pytest.skip("Local original game required")
    return ORIGINAL.read_bytes()


def test_rejects_wrong_version() -> None:
    with pytest.raises(ValueError, match="SHA256"):
        mod.build_candidate(b"not the original")


def test_capacity_and_owner_policy(original: bytes) -> None:
    candidate, report = mod.build_candidate(original)
    assert report["capacity_slots"] == 4093
    assert report["usable_slots"] == 4092
    assert report["owner_count_cap"] == 500
    assert report["supply_cap"] == 10000
    assert 8 * report["owner_count_cap"] <= report["usable_slots"]
    pe = pefile.PE(data=candidate, fast_load=True)
    try:
        assert not pe.get_warnings()
    finally:
        pe.close()


def test_only_the_three_documented_edits_differ_from_the_compat_chain(original: bytes) -> None:
    compat_candidate, _compat_report = build_compat_candidate(original, mod.CAPACITY)
    candidate, report = mod.build_candidate(original)
    assert len(candidate) == len(compat_candidate)
    allowed: set[int] = set()
    for edit in report["supply_edits"]:
        offset = int(edit["offset"], 16)
        allowed.update(range(offset, offset + len(bytes.fromhex(edit["after"]))))
    owner_offset = int(report["owner_count_edit"]["offset"], 16)
    allowed.update(range(owner_offset, owner_offset + len(bytes.fromhex(report["owner_count_edit"]["after"]))))
    for va_hex, after_hex in report["producer_lookup_edits"].items():
        offset = int(va_hex, 16) - 0x00400000
        allowed.update(range(offset, offset + len(bytes.fromhex(after_hex))))
    changed = {i for i, (a, b) in enumerate(zip(compat_candidate, candidate)) if a != b}
    assert changed <= allowed
    assert changed  # sanity: something actually changed


def test_supply_cap_is_10000_not_5000(original: bytes) -> None:
    candidate, _report = mod.build_candidate(original)
    assert candidate[0x1B579:0x1B57B] == (10000).to_bytes(2, "little")
    assert candidate[0x3FFD5:0x3FFD9] == (10000).to_bytes(4, "little")


def test_owner_cap_is_500_not_1200(original: bytes) -> None:
    candidate, _report = mod.build_candidate(original)
    offset = mod.OWNER_COUNT_FILE_OFFSET
    assert candidate[offset : offset + 4] == (500).to_bytes(4, "little")


def test_producer_lookup_bound_matches_capacity(original: bytes) -> None:
    candidate, _report = mod.build_candidate(original)
    for va, _old, new in mod.PRODUCER_LOOKUP_EDITS:
        offset = va - 0x00400000
        assert candidate[offset : offset + len(new)] == new


def test_copy_restore_preserves_input(original: bytes, tmp_path: Path) -> None:
    source = tmp_path / "input.exe"
    source.write_bytes(original)
    target = tmp_path / "candidate.exe"
    report = mod.create_copy(source, target)
    assert source.read_bytes() == original
    assert target.read_bytes() == mod.build_candidate(original)[0]
    assert mod.restore_copy(target, source) == mod.digest(original)
    assert target.read_bytes() == original
    assert report["candidate_sha256"] == mod.digest(mod.build_candidate(original)[0])


def test_rejects_input_as_target(original: bytes, tmp_path: Path) -> None:
    source = tmp_path / "input.exe"
    source.write_bytes(original)
    with pytest.raises(ValueError, match="input"):
        mod.create_copy(source, source)
    assert source.read_bytes() == original


def test_restore_refuses_unknown_modification(original: bytes, tmp_path: Path) -> None:
    source = tmp_path / "input.exe"
    source.write_bytes(original)
    target = tmp_path / "candidate.exe"
    mod.create_copy(source, target)
    target.write_bytes(b"changed externally")
    with pytest.raises(ValueError, match="exact candidate"):
        mod.restore_copy(target, source)
    assert target.read_bytes() == b"changed externally"
