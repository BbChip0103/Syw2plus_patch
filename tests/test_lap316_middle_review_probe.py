"""Regression tests for the lap316 middle review probe.

The graph tests use fixtures whose answers can be worked out by hand, so they
test the algorithm rather than restating its output.  The binary-fact tests
cross-check the probe against the raw PE image and against the *stored* lap315
report file read as data; the lap315 probe module is never imported.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROBE_PATH = ROOT / "docs/history/laps/probes/20260912_lap316_middle_lap315_v6_review_probe.py"
LAP315_REPORT = ROOT / "logs/lap315/lap315_v6_mode_writer_order.json"
SPEC = importlib.util.spec_from_file_location("lap316_probe", PROBE_PATH)
assert SPEC and SPEC.loader
PROBE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PROBE)


def test_witness_path_avoids_a_blocked_node_when_a_detour_exists():
    # 1 -> {2, 3}; 2 -> 4; 3 -> 4.  Blocking 2 must still leave 1 -> 3 -> 4.
    graph = {1: {2, 3}, 2: {4}, 3: {4}, 4: set()}
    path = PROBE.witness_path(graph, 1, 4, frozenset({2}))
    assert path == [1, 3, 4]


def test_witness_path_is_none_when_the_blocked_node_is_a_cut_vertex():
    graph = {1: {2}, 2: {3}, 3: set()}
    assert PROBE.witness_path(graph, 1, 3, frozenset({2})) is None


def test_breadth_first_excludes_blocked_nodes_and_their_subtrees():
    graph = {1: {2}, 2: {3}, 3: set(), 4: set()}
    assert PROBE.breadth_first(graph, 1) == {1, 2, 3}
    assert PROBE.breadth_first(graph, 1, frozenset({2})) == {1}


def test_register_indirect_jump_gets_no_edge_and_is_unresolved():
    window = [(0x1000, "jmp    *%eax"), (0x1002, "nop")]
    graph, unresolved, indirect = PROBE.build_graph(window)
    assert graph[0x1000] == set()
    assert len(unresolved) == 1 and len(indirect) == 1


def test_memory_indirect_jump_table_gets_no_edge_and_is_unresolved():
    window = [(0x1000, "jmp    *0x464b68(,%eax,4)"), (0x1007, "nop")]
    graph, unresolved, indirect = PROBE.build_graph(window)
    assert graph[0x1000] == set()
    assert indirect and "0x1000" in indirect[0]


def test_conditional_branch_keeps_fall_through_but_flags_a_target_outside_the_window():
    window = [(0x1000, "jne    0x9999"), (0x1002, "nop")]
    graph, unresolved, _indirect = PROBE.build_graph(window)
    assert graph[0x1000] == {0x1002}
    assert any("outside window" in entry for entry in unresolved)


def test_pe_reader_matches_the_known_gate_and_failure_arm_bytes():
    data, sections, image_base = PROBE.load_pe()
    read = PROBE.make_reader(data, sections, image_base)
    assert read(PROBE.GATE, 2).hex() == "750a"
    assert read(PROBE.FAILURE_SEED, 10).hex() == "5f5e5d33c05b83c434c3"


def test_objdump_byte_column_is_reassembled_for_wrapped_instructions():
    """A wrapped instruction must yield its full length, not objdump's 7 bytes."""
    _rows, columns, continuation_count = PROBE.disassemble_att()
    assert continuation_count > 0
    # 0x4324b8 is a ten-byte immediate store that objdump wraps across two lines.
    assert columns[0x4324B8] == "c7051cbfe50080020000"


def test_stored_lap315_report_counts_agree_with_this_independent_derivation():
    stored = json.loads(LAP315_REPORT.read_text())["map_cfg"]
    rows, _columns, _continuation = PROBE.disassemble_att()
    window = [(address, text) for address, text in rows if PROBE.MAP_ENTRY <= address < PROBE.MAP_END]
    graph, unresolved, _indirect = PROBE.build_graph(window)
    assert stored["instruction_count"] == len(window)
    assert stored["unresolved_branches"] == unresolved == []
    assert stored["entry_reachable_instruction_count"] == len(PROBE.breadth_first(graph, PROBE.MAP_ENTRY))
    assert stored["failure_arm_instruction_count"] == len(PROBE.breadth_first(graph, PROBE.FAILURE_SEED))
    assert stored["success_arm_instruction_count"] == len(PROBE.breadth_first(graph, PROBE.SUCCESS_JOIN))
