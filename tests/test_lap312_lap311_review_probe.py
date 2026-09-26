"""Regression tests for the lap312 middle review of the lap311 V4 repair.

These recompute the review's two axes from the SHA-pinned original image using
methods that do not import the lap311 probe, so a defect in lap311's objdump
parser or dominator fixpoint cannot make them pass.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROBE_PATH = ROOT / "docs/history/laps/probes/20260912_lap312_middle_lap311_v4_review_probe.py"
SPEC = importlib.util.spec_from_file_location("lap312_review_probe", PROBE_PATH)
assert SPEC and SPEC.loader
PROBE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PROBE)


def test_raw_byte_census_finds_exactly_four_absolute_screen_stores():
    text_base, blob = PROBE.load_text_section()
    census = PROBE.scan_absolute_writers(text_base, blob)
    assert census["unclassified"] == []
    assert set(census["store_sites"]) == {"0x431b79", "0x431b7f", "0x4324b8", "0x4324c2"}
    assert census["reference_kinds"].get("store/mov-moffs32-eax", 0) == 0
    assert all(
        PROBE.MAP_ENTRY <= int(address, 16) < PROBE.MAP_END for address in census["store_sites"]
    )


def test_gate_bytes_name_the_failure_arm_correctly():
    text_base, blob = PROBE.load_text_section()
    offset = PROBE.MAP_GATE_BRANCH - text_base
    assert blob[offset : offset + 2].hex() == PROBE.GATE_BYTES
    assert PROBE.MAP_GATE_BRANCH + 2 + blob[offset + 1] == PROBE.MAP_SUCCESS_JOIN
    failure_offset = PROBE.MAP_FAILURE_SEED - text_base
    assert blob[failure_offset : failure_offset + 10].hex() == PROBE.FAILURE_ARM_BYTES


def test_cut_test_reproduces_reset_writers_and_keeps_a_working_control():
    window = PROBE.disassemble_window()
    successors, unresolved = PROBE.build_successors(window)
    assert not unresolved
    for writer in PROBE.ALL_WRITERS:
        assert PROBE.cuts(successors, PROBE.MAP_ENTRY, PROBE.MAP_SUCCESS_RET, writer)
    for writer in PROBE.RESET_WRITERS:
        assert PROBE.cuts(successors, PROBE.MAP_SUCCESS_JOIN, PROBE.MAP_SUCCESS_RET, writer)
    # falsification control: an off-path node must not cut the success return
    assert not PROBE.cuts(successors, PROBE.MAP_ENTRY, PROBE.MAP_SUCCESS_RET, PROBE.MAP_FAILURE_RET)


def test_no_direct_screen_writer_follows_the_640x480_reset():
    window = PROBE.disassemble_window()
    successors, _unresolved = PROBE.build_successors(window)
    after = PROBE.reachable(successors, PROBE.RESET_WRITERS[1]) - {PROBE.RESET_WRITERS[1]}
    assert not (after & set(PROBE.ALL_WRITERS))
    failure_arm = PROBE.reachable(successors, PROBE.MAP_FAILURE_SEED)
    assert PROBE.MAP_SUCCESS_RET not in failure_arm
    assert not (failure_arm & set(PROBE.ALL_WRITERS))
