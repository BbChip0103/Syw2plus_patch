"""Regression tests for lap313's D1-D4 R2 probe repairs."""
from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROBE_PATH = ROOT / "docs/history/laps/probes/20260912_lap313_work_v5_mode_writer_order_probe.py"
SPEC = importlib.util.spec_from_file_location("lap313_probe", PROBE_PATH)
assert SPEC and SPEC.loader
PROBE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PROBE)


def test_pre_gate_uses_cfg_dominance_when_address_order_is_misleading():
    # The writer address is numerically after the gate, but every entry->gate
    # path passes it.  An address comparison would incorrectly return empty.
    entry, writer, gate, exit_node = 0x100, 0x300, 0x200, 0x400
    graph = {
        entry: {writer},
        writer: {gate, writer},
        gate: {exit_node},
        exit_node: set(),
    }
    assert PROBE.pre_gate_screen_writers(graph, entry, gate, {writer}) == {writer}


def test_pre_gate_excludes_writer_reached_only_after_gate():
    entry, gate, writer, exit_node = 0x100, 0x200, 0x300, 0x400
    graph = {
        entry: {gate},
        gate: {writer},
        writer: {exit_node},
        exit_node: set(),
    }
    assert PROBE.pre_gate_screen_writers(graph, entry, gate, {writer}) == set()


def test_gate_facts_are_pinned_from_instruction_bytes():
    rows = PROBE.parse_listing()
    window = [row for row in rows if PROBE.MAP_ENTRY <= row[0] < PROBE.MAP_END]
    facts = PROBE.gate_byte_facts(window)
    assert facts["gate_is_conditional_branch"]
    assert facts["gate_taken_target_is_success_join"]
    assert facts["failure_arm_returns_zero"]


def test_probe_removes_dead_runtime_expectation_and_numeric_pre_gate_test():
    source = PROBE_PATH.read_text()
    assert "EXPECTED_RUNTIME_WRITERS" not in source
    assert "address < MAP_GATE_BRANCH" not in source
