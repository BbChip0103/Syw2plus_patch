"""Regression tests for the lap314 middle review probe.

The synthetic graph tests have independently derivable answers, so they test the
cut-based dominator algorithm itself rather than restating it.  The binary tests
cross-check the lap314 probe's own derivation against the lap313 report file, so
a drift in either artifact breaks the pair.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROBE_PATH = ROOT / "docs/history/laps/probes/20260912_lap314_middle_lap313_v5_review_probe.py"
LAP313_REPORT = ROOT / "logs/lap313/lap313_v5_mode_writer_order.json"

SPEC = importlib.util.spec_from_file_location("lap314_review_probe", PROBE_PATH)
assert SPEC and SPEC.loader
PROBE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PROBE)


def test_cut_dominators_include_a_node_every_path_must_cross():
    entry, loop_body, gate, exit_node = 0x100, 0x300, 0x200, 0x400
    graph = {
        entry: {loop_body},
        loop_body: {gate, loop_body},
        gate: {exit_node},
        exit_node: set(),
    }
    # loop_body sits numerically after the gate but dominates it.
    assert PROBE.dominators_by_cut(graph, entry, gate) == {entry, loop_body, gate}


def test_cut_dominators_exclude_a_node_on_only_one_branch():
    entry, left, right, gate = 0x100, 0x200, 0x300, 0x400
    graph = {entry: {left, right}, left: {gate}, right: {gate}, gate: set()}
    assert PROBE.dominators_by_cut(graph, entry, gate) == {entry, gate}


def test_cut_dominators_are_empty_when_the_target_is_unreachable():
    entry, island = 0x100, 0x200
    graph = {entry: set(), island: set()}
    assert PROBE.dominators_by_cut(graph, entry, island) == set()


def test_indirect_branch_is_reported_unresolved_and_gets_no_fabricated_edge():
    window = [
        (0x1000, b"\xff\x24\x85", "jmp    DWORD PTR [eax*4+0x464b68]"),
        (0x1003, b"\x90", "nop"),
    ]
    graph, unresolved = PROBE.build_cfg(window)
    assert graph[0x1000] == set()
    assert any("indirect" in entry for entry in unresolved)


def test_direct_branch_outside_the_window_is_reported_unresolved():
    window = [(0x1000, b"\x75\x02", "jne    0x9999"), (0x1002, b"\x90", "nop")]
    graph, unresolved = PROBE.build_cfg(window)
    assert graph[0x1000] == {0x1002}
    assert any("outside window" in entry for entry in unresolved)


def test_lap314_derivation_agrees_with_the_lap313_report_file():
    rows = PROBE.listing()
    window = [row for row in rows if PROBE.MAP_ENTRY <= row[0] < PROBE.MAP_END]
    graph, unresolved = PROBE.build_cfg(window)
    writers = {a for a, _raw, text in window if PROBE.WRITER_RE.search(text)}
    failure = PROBE.reachable(graph, PROBE.FAILURE_SEED)
    success = PROBE.reachable(graph, PROBE.SUCCESS_JOIN)

    report = json.loads(LAP313_REPORT.read_text())
    r2 = report["r2_failure_arm_writer_set_comparison"]
    assert unresolved == []
    assert PROBE.fmt(writers) == r2["all_screen_writers_in_map_window"]
    assert PROBE.fmt(writers & failure) == r2["failure_arm_screen_writers"]
    assert PROBE.fmt(writers & success) == r2["success_arm_screen_writers"]
    assert len(window) == report["map_cfg"]["instruction_count"]
    assert len(failure) == report["map_cfg"]["failure_arm_instruction_count"]
    assert len(success) == report["map_cfg"]["success_arm_instruction_count"]
