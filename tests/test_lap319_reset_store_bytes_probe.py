"""Regression tests for lap319's fail-closed folded-byte collector."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROBE_PATH = ROOT / "docs/history/laps/probes/20260912_lap319_work_v7_reset_store_bytes_probe.py"
REPORT_PATH = ROOT / "logs/lap319/lap319_reset_store_bytes.json"
SPEC = importlib.util.spec_from_file_location("lap319_probe", PROBE_PATH)
assert SPEC and SPEC.loader
PROBE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PROBE)


IMAGE_BASE = 0x400000
START = 0x401000
FULL = bytes.fromhex("c7051cbfe50080020000")


def synthetic_image(payload: bytes, *, section_size: int | None = None) -> tuple[bytes, int, list]:
    size = len(payload) if section_size is None else section_size
    sections = [(".text", START - IMAGE_BASE, size, 0x200, size)]
    return bytes(0x200) + payload, IMAGE_BASE, sections


def folded_listing(*, continuation: str = "  401007:\t02 00 00 \n", tail: str = "  40100a:\t90                   \tnop\n") -> str:
    return (
        "  401000:\tc7 05 1c bf e5 00 80 \tmov    DWORD PTR ds:0xe5bf1c,0x280\n"
        + continuation
        + tail
    )


def validate(listing: str, payload: bytes = FULL, *, section_size: int | None = None) -> dict:
    rows, continuations = PROBE.parse_listing(listing)
    image, base, sections = synthetic_image(payload, section_size=section_size)
    return PROBE.collect_folded_instruction(rows, continuations, image, base, sections, START)


def test_normal_folded_listing_reassembles_ten_bytes_and_uses_address_delta():
    result = validate(folded_listing())
    assert result["ok"] is True
    assert result["boundary_length"] == 10
    assert result["column_length"] == 10
    assert result["image_bytes"] == FULL.hex()
    assert result["length_invariant"] is True


def test_missing_continuation_is_rejected_as_a_short_column():
    result = validate(folded_listing(continuation=""))
    assert result["ok"] is False
    assert result["reason"] == "column_shorter_than_address_delta"


def test_truncation_without_a_next_address_boundary_is_rejected():
    listing = "  401000:\tc7 05 1c bf e5 00 80 \tmov    DWORD PTR ds:0xe5bf1c,0x280\n"
    result = validate(listing)
    assert result["ok"] is False
    assert result["reason"] == "missing_next_address_boundary"


def test_continuation_address_gap_is_rejected():
    result = validate(folded_listing(continuation="  401008:\t02 00 00 \n"))
    assert result["ok"] is False
    assert result["reason"] == "continuation_gap"


def test_continuation_overlap_is_rejected():
    result = validate(folded_listing(continuation="  401006:\t02 00 00 \n"))
    assert result["ok"] is False
    assert result["reason"] == "continuation_overlap"


def test_section_range_failure_is_rejected_even_with_a_complete_column():
    result = validate(folded_listing(), section_size=9)
    assert result["ok"] is False
    assert result["reason"] == "pe_read_out_of_range"


def test_real_reset_rows_pass_with_file_values_and_address_boundaries():
    rows, continuations = PROBE.disassemble()
    image = PROBE.EXE.read_bytes()
    base, sections = PROBE.parse_sections(image)
    for address, expected in PROBE.EXPECTED_RESET_BYTES.items():
        result = PROBE.collect_folded_instruction(rows, continuations, image, base, sections, address)
        assert result["ok"] is True
        assert result["boundary_length"] == 10
        assert result["column_length"] == 10
        assert result["image_bytes"] == expected.hex()


def test_report_keeps_original_sha_and_static_scope():
    assert REPORT_PATH.is_file(), "lap319 report must be generated next to the probe"
    report = json.loads(REPORT_PATH.read_text())
    assert report["exe_sha256"] == PROBE.EXPECTED_EXE_SHA
    assert report["verdict"] == "PASS"
    assert report["execution"] is False
    assert report["window"]["instruction_count"] == 753
    assert report["checks"]["passed"] == report["checks"]["count"]
