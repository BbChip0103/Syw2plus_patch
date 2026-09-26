"""Regression checks for the read-only G5 selection-cap inventory."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pefile
import pytest


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "analysis" / "g5_selection_cap_inventory.json"
ORIGINAL = ROOT / "Syw2plus" / "syw2plus_original.exe"
EXPECTED_SHA256 = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"


def _load_inventory() -> dict:
    return json.loads(INVENTORY.read_text(encoding="utf-8"))


def _va_bytes(pe: pefile.PE, image: bytes, va: str, length: int) -> bytes:
    rva = int(va, 16) - pe.OPTIONAL_HEADER.ImageBase
    offset = pe.get_offset_from_rva(rva)
    return image[offset : offset + length]


def test_inventory_layout_and_counts_are_pinned() -> None:
    report = _load_inventory()
    storage = report["selection_storage"]
    assert report["status"] == "FEASIBLE_STATIC_CONDITIONAL"
    assert storage["original_capacity"] == 20
    assert storage["slot_stride_bytes"] == 4
    assert storage["slot_end_exclusive"] == "0x00899078"
    assert len(report["direct_references"]["count_address"]) == 9
    assert len(report["direct_references"]["slot_base_or_element"]) == 28
    assert len(report["direct_references"]["slot_end_exclusive"]) == 14
    assert len(report["slot_index_references"]) == 34
    assert report["command_path"]["caller_count"] == 22


def test_inventory_source_hash_matches_original_when_available() -> None:
    if not ORIGINAL.is_file():
        pytest.skip("private original executable is unavailable")
    assert hashlib.sha256(ORIGINAL.read_bytes()).hexdigest() == EXPECTED_SHA256
    assert _load_inventory()["source"]["sha256"] == EXPECTED_SHA256


def test_every_recorded_old_instruction_bytes_match_pinned_original() -> None:
    if not ORIGINAL.is_file():
        pytest.skip("private original executable is unavailable")
    image = ORIGINAL.read_bytes()
    pe = pefile.PE(str(ORIGINAL), fast_load=True)
    report = _load_inventory()
    records = []
    for group in report["direct_references"].values():
        records.extend(group)
    records.extend(report["slot_index_references"])
    for group in report["fixed_limit_sites"].values():
        records.extend(group)
    for record in records:
        expected = bytes.fromhex(record["old_bytes"])
        actual = _va_bytes(pe, image, record["va"], len(expected))
        assert actual == expected, record["va"]

