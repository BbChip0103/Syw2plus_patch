"""Regression tests for the lap318 middle review probe.

The parser and byte-source tests use small listings and a synthetic PE image
whose answers can be worked out by hand, so they test the algorithm rather than
restating its output.  The binary-fact tests read the original image directly;
the lap315 and lap316 probe modules are never imported.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
PROBE_PATH = ROOT / "docs/history/laps/probes/20260912_lap318_middle_lap317_f1_scope_review_probe.py"
REPORT_PATH = ROOT / "logs/lap318/lap318_lap317_f1_scope_review.json"
SPEC = importlib.util.spec_from_file_location("lap318_probe", PROBE_PATH)
assert SPEC and SPEC.loader
PROBE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PROBE)


# A two-instruction listing where the first instruction is 10 bytes and objdump
# folds it as 7 bytes plus a 3-byte continuation line, exactly like 0x4324b8.
FOLDED_LISTING = (
    "  4324b8:\tc7 05 1c bf e5 00 80 \tmov    DWORD PTR ds:0xe5bf1c,0x280\n"
    "  4324bf:\t02 00 00 \n"
    "  4324c2:\tb8 01 00 00 00       \tmov    eax,0x1\n"
)


def test_folded_instruction_is_parsed_as_one_row_not_two():
    rows, continuations = PROBE.parse_listing(FOLDED_LISTING)
    assert [address for address, _raw, _text in rows] == [0x4324B8, 0x4324C2]
    assert [address for address, _raw in continuations] == [0x4324BF]


def test_folded_instruction_byte_column_is_truncated_to_seven_bytes():
    rows, _continuations = PROBE.parse_listing(FOLDED_LISTING)
    assert rows[0][1].hex() == "c7051cbfe50080"
    assert len(rows[0][1]) == 7


def test_boundary_length_comes_from_the_address_column_not_the_byte_column():
    rows, _continuations = PROBE.parse_listing(FOLDED_LISTING)
    lengths = PROBE.boundary_lengths(rows, 0x4324C7)
    # 0x4324c2 - 0x4324b8 == 10, even though the byte column shows 7.
    assert lengths[0x4324B8] == 10
    assert lengths[0x4324C2] == 5


def test_last_row_length_uses_the_window_end():
    rows, _continuations = PROBE.parse_listing(FOLDED_LISTING)
    assert PROBE.boundary_lengths(rows, 0x4324D0)[0x4324C2] == 0x4324D0 - 0x4324C2


def _synthetic_image(text_bytes: bytes, image_base: int = 0x400000) -> tuple[bytes, int, list]:
    """One .text section at VA base+0x1000, file offset 0x200."""
    sections = [(".text", 0x1000, len(text_bytes), 0x200, len(text_bytes))]
    image = bytearray(0x200) + bytearray(text_bytes)
    return bytes(image), image_base, sections


def test_virtual_to_raw_maps_inside_the_section_and_refuses_outside():
    _image, base, sections = _synthetic_image(b"\x90" * 16)
    assert PROBE.virtual_to_raw(base, sections, base + 0x1000) == 0x200
    assert PROBE.virtual_to_raw(base, sections, base + 0x1005) == 0x205
    assert PROBE.virtual_to_raw(base, sections, base + 0x2000) is None


def test_pe_bytes_refuses_a_read_that_runs_past_the_section():
    image, base, sections = _synthetic_image(bytes(range(8)))
    assert PROBE.pe_bytes(image, base, sections, base + 0x1000, 8) == bytes(range(8))
    assert PROBE.pe_bytes(image, base, sections, base + 0x1004, 8) is None


def test_truncation_audit_flags_a_folded_row_and_still_calls_it_a_prefix():
    rows, _continuations = PROBE.parse_listing(FOLDED_LISTING)
    text = bytes.fromhex("c7051cbfe50080020000") + bytes.fromhex("b801000000")
    image, base, sections = _synthetic_image(text, image_base=0x400000)
    # Place the synthetic .text so that VA 0x4324b8 is its first byte.
    sections = [(".text", 0x324B8, len(text), 0x200, len(text))]
    lengths = PROBE.boundary_lengths(rows, 0x4324C7)
    audit = PROBE.truncation_audit(rows, lengths, image, base, sections)
    assert audit["folded_instructions"] == ["0x4324b8"]
    assert audit["byte_column_is_prefix_of_image"] is True


def test_truncation_audit_reports_corruption_when_the_column_is_not_a_prefix():
    rows, _continuations = PROBE.parse_listing(FOLDED_LISTING)
    text = bytes.fromhex("ff051cbfe50080020000") + bytes.fromhex("b801000000")
    image, base, sections = _synthetic_image(text)
    sections = [(".text", 0x324B8, len(text), 0x200, len(text))]
    lengths = PROBE.boundary_lengths(rows, 0x4324C7)
    audit = PROBE.truncation_audit(rows, lengths, image, base, sections)
    assert audit["byte_column_is_prefix_of_image"] is False
    assert audit["corrupted_instructions"] == ["0x4324b8"]


def test_contiguous_collection_fails_on_the_gap_a_folded_row_leaves():
    rows, _continuations = PROBE.parse_listing(FOLDED_LISTING)
    # 0x4324b8 + 7 == 0x4324bf, but the next row is 0x4324c2: a 3-byte gap.
    collected, contiguous = PROBE.collect_contiguous_by_column(rows, 0x4324B8, 10)
    assert contiguous is False
    assert collected.hex() == "c7051cbfe50080"


def test_contiguous_collection_succeeds_when_no_row_is_folded():
    listing = "  401000:\t90                   \tnop\n  401001:\tb8 01 00 00 00       \tmov    eax,0x1\n"
    rows, _continuations = PROBE.parse_listing(listing)
    collected, contiguous = PROBE.collect_contiguous_by_column(rows, 0x401000, 6)
    assert contiguous is True
    assert collected.hex() == "90b801000000"


def test_contiguous_collection_fails_when_the_seed_address_is_absent():
    listing = "  401000:\t90                   \tnop\n"
    rows, _continuations = PROBE.parse_listing(listing)
    _collected, contiguous = PROBE.collect_contiguous_by_column(rows, 0x401004, 1)
    assert contiguous is False


@pytest.fixture(scope="module")
def report() -> dict:
    assert REPORT_PATH.is_file(), "lap318 report must be committed next to the probe"
    return json.loads(REPORT_PATH.read_text())


def test_report_confirms_the_lap317_reset_byte_claims(report: dict) -> None:
    resets = report["reset_writers"]
    assert resets["0x4324b8"]["image_bytes"] == "c7051cbfe50080020000"
    assert resets["0x4324c2"]["image_bytes"] == "c70520bfe500e0010000"
    assert all(row["boundary_length"] == 10 for row in resets.values())
    assert all(row["byte_column_length"] == 7 for row in resets.values())


def test_report_records_the_f1_premise_and_leaves_the_numbers_unchanged(report: dict) -> None:
    assert report["window"]["instruction_count"] == 753
    assert report["f1_premise"]["folded_instruction_count"] == 27
    assert report["f1_premise"]["byte_column_is_prefix_of_image"] is True
    assert report["failure_arm"]["touches_a_folded_instruction"] is False
    assert report["all_checks_pass"] is True


def test_report_is_a_static_audit_with_no_execution(report: dict) -> None:
    assert report["execution"] is False
    assert report["exe_sha256"] == PROBE.EXPECTED_EXE_SHA
