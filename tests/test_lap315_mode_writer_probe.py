"""Regression tests for the lap315 R2 fail-open repairs."""
from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROBE_PATH = ROOT / "docs/history/laps/probes/20260912_lap315_work_v6_mode_writer_order_probe.py"
SPEC = importlib.util.spec_from_file_location("lap315_probe", PROBE_PATH)
assert SPEC and SPEC.loader
PROBE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PROBE)


def test_indirect_jump_is_unresolved_without_fall_through():
    window = [
        (0x1000, "jmp    DWORD PTR [eax*4+0x464b68]"),
        (0x1003, "nop"),
    ]
    graph, unresolved = PROBE.build_cfg(window)
    assert graph[0x1000] == set()
    assert any("indirect/unparsed branch" in entry for entry in unresolved)


def test_register_indirect_jump_is_unresolved_without_fall_through():
    window = [
        (0x1000, "jmp    eax"),
        (0x1002, "nop"),
    ]
    graph, unresolved = PROBE.build_cfg(window)
    assert graph[0x1000] == set()
    assert any("jmp    eax" in entry for entry in unresolved)


def test_direct_branch_outside_window_is_still_reported_unresolved():
    window = [(0x1000, "jne    0x9999"), (0x1002, "nop")]
    graph, unresolved = PROBE.build_cfg(window)
    assert graph[0x1000] == {0x1002}
    assert any("outside window" in entry for entry in unresolved)


def test_failure_arm_collection_rejects_a_gap_before_the_expected_length():
    rows = [
        (PROBE.MAP_FAILURE_SEED, b"\x5f", "pop edi"),
        (PROBE.MAP_FAILURE_SEED + 2, b"\x5d", "pop ebp"),
    ]
    collected, contiguous, consumed = PROBE.collect_contiguous_bytes(
        rows, PROBE.MAP_FAILURE_SEED, len(PROBE.FAILURE_ARM_BYTES)
    )
    assert collected == b"\x5f"
    assert not contiguous
    assert consumed == 1


def test_real_gate_facts_require_and_report_contiguous_failure_arm():
    rows = PROBE.parse_listing()
    window = [row for row in rows if PROBE.MAP_ENTRY <= row[0] < PROBE.MAP_END]
    facts = PROBE.gate_byte_facts(window)
    assert facts["gate_is_conditional_branch"]
    assert facts["gate_taken_target_is_success_join"]
    assert facts["failure_arm_is_contiguous"]
    assert facts["failure_arm_returns_zero"]


def test_real_r2_report_marks_empty_pre_gate_as_vacuous():
    rows = PROBE.parse_listing()
    map_rows = [row for row in rows if PROBE.MAP_ENTRY <= row[0] < PROBE.MAP_END]
    map_window = [(address, instruction) for address, _raw, instruction in map_rows]
    graph, unresolved = PROBE.build_cfg(map_window)
    assert not unresolved
    writers = PROBE.screen_writers(map_window)
    pre_gate = PROBE.pre_gate_screen_writers(graph, PROBE.MAP_ENTRY, PROBE.MAP_GATE_BRANCH, writers)
    assert pre_gate == set()
    assert PROBE.reachable(graph, PROBE.MAP_FAILURE_SEED) & writers == set()
