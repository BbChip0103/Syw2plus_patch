"""Regression tests for lap320's independent review collector.

The synthetic listings below are small enough to derive by hand: one folded
10-byte store at 0x401000 whose continuation carries the last three bytes.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROBE_PATH = ROOT / "docs/history/laps/probes/20260912_lap320_middle_lap319_f1_review_probe.py"
REPORT_PATH = ROOT / "logs/lap320/lap320_lap319_f1_review.json"
SPEC = importlib.util.spec_from_file_location("lap320_probe", PROBE_PATH)
assert SPEC and SPEC.loader
PROBE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PROBE)

START = 0x401000
IMAGE_BASE = 0x400000
FULL = bytes.fromhex("c7051cbfe50080020000")
MAIN_ROW = "  401000:\tc7 05 1c bf e5 00 80 \tmov    DWORD PTR ds:0xe5bf1c,0x280\n"
CONTINUATION = "  401007:\t02 00 00 \n"
TAIL = "  40100a:\t90                   \tnop\n"


def synthetic_image(payload: bytes, raw_size: int | None = None):
    size = len(payload) if raw_size is None else raw_size
    sections = [
        {
            "name": ".text",
            "virtual_address": START - IMAGE_BASE,
            "virtual_size": size,
            "raw_pointer": 0x200,
            "raw_size": size,
        }
    ]
    return bytes(0x200) + payload, sections


def resolve(listing: str):
    rows, continuation_rows = PROBE.split_listing(listing)
    continuations = {row["address"]: row["bytes"] for row in continuation_rows}
    window = PROBE.attach_boundaries(rows, PROBE.window_instructions(rows, START, START + 0x100))
    return window, continuations


def test_split_listing_separates_continuations_from_instruction_rows():
    rows, continuations = PROBE.split_listing(MAIN_ROW + CONTINUATION + TAIL)
    assert [row["address"] for row in rows] == [0x401000, 0x40100A]
    assert [row["address"] for row in continuations] == [0x401007]
    assert rows[0]["bytes"] == FULL[:7]


def test_boundary_length_comes_from_the_next_listing_address():
    window, _ = resolve(MAIN_ROW + CONTINUATION + TAIL)
    assert window[0]["length"] == 10
    assert len(window[0]["bytes"]) == 7


def test_folded_instruction_reassembles_to_the_full_ten_bytes():
    window, continuations = resolve(MAIN_ROW + CONTINUATION + TAIL)
    column, reason = PROBE.reassemble_column(window[0], continuations)
    assert reason is None
    assert column == FULL


def test_missing_continuation_row_is_rejected():
    window, continuations = resolve(MAIN_ROW + TAIL)
    column, reason = PROBE.reassemble_column(window[0], continuations)
    assert reason == "missing_continuation_row"
    assert column == FULL[:7]


def test_continuation_running_past_the_next_address_is_rejected():
    window, continuations = resolve(MAIN_ROW + CONTINUATION + "  401008:\t90 \tnop\n")
    column, reason = PROBE.reassemble_column(window[0], continuations)
    assert reason == "column_overruns_next_instruction"
    assert len(column) == 10


def test_missing_next_address_boundary_is_rejected():
    window, continuations = resolve(MAIN_ROW + CONTINUATION)
    column, reason = PROBE.reassemble_column(window[0], continuations)
    assert reason == "missing_next_address_boundary"
    assert column == FULL[:7]


def test_file_slice_refuses_reads_past_the_section_raw_size():
    image, sections = synthetic_image(FULL, raw_size=9)
    assert PROBE.file_slice(image, IMAGE_BASE, sections, START, 10) is None
    assert PROBE.file_slice(image, IMAGE_BASE, sections, START, 9) == FULL[:9]


def test_file_slice_returns_exact_bytes_inside_the_section():
    image, sections = synthetic_image(FULL)
    assert PROBE.file_slice(image, IMAGE_BASE, sections, START, 10) == FULL


def test_screen_writer_decoder_accepts_both_direct_store_encodings():
    assert PROBE.decode_screen_writer(FULL) == 0xE5BF1C
    assert PROBE.decode_screen_writer(bytes.fromhex("892d1cbfe500")) == 0xE5BF1C
    assert PROBE.decode_screen_writer(bytes.fromhex("893d20bfe500")) == 0xE5BF20


def test_screen_writer_decoder_rejects_other_targets_and_truncated_columns():
    assert PROBE.decode_screen_writer(bytes.fromhex("c70588acb3000f030000")) is None
    assert PROBE.decode_screen_writer(FULL[:7]) is None
    assert PROBE.decode_screen_writer(bytes.fromhex("8b0d1cbfe500")) is None


def test_report_records_a_static_middle_review_that_passed():
    assert REPORT_PATH.is_file(), "lap320 report must be generated next to the probe"
    report = json.loads(REPORT_PATH.read_text())
    assert report["exe_sha256"] == PROBE.EXPECTED_EXE_SHA
    assert report["execution"] is False
    assert report["verdict"] == "PASS"
    assert report["failures"] == []
    assert report["derived"]["counts"]["window"] == 753
    assert report["derived"]["counts"]["folded"] == 27
    assert report["check_counts"]["passed"] == report["check_counts"]["count"]
