"""Regression tests for lap311's stronger static R2 evidence."""
from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROBE_PATH = ROOT / "docs/history/laps/probes/20260912_lap311_work_v4_mode_writer_order_probe.py"
SPEC = importlib.util.spec_from_file_location("lap311_probe", PROBE_PATH)
assert SPEC and SPEC.loader
PROBE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PROBE)


def test_failure_arm_preserves_the_complete_pre_gate_screen_writer_set():
    instructions = PROBE.parse_text()
    window = [(address, instruction) for address, instruction in instructions if PROBE.MAP_ENTRY <= address < PROBE.MAP_END]
    graph, unresolved = PROBE.build_cfg(window)
    assert not unresolved
    writers = PROBE.screen_writers(window)
    entry_reachable = PROBE.reachable(graph, PROBE.MAP_ENTRY)
    before_gate = writers & {address for address in entry_reachable if address < PROBE.MAP_GATE_BRANCH}
    failure_writers = writers & PROBE.reachable(graph, PROBE.MAP_FAILURE_SEED)
    assert writers == {0x431B79, 0x431B7F, 0x4324B8, 0x4324C2}
    assert failure_writers == before_gate == set()


def test_reverse_postdominators_require_both_success_reset_writers():
    instructions = PROBE.parse_text()
    window = [(address, instruction) for address, instruction in instructions if PROBE.MAP_ENTRY <= address < PROBE.MAP_END]
    graph, _unresolved = PROBE.build_cfg(window)
    reverse = PROBE.reverse_graph(graph)
    postdom = PROBE.dominators(reverse, PROBE.MAP_SUCCESS_RET)
    assert PROBE.MAP_ENTRY in PROBE.reachable(reverse, PROBE.MAP_SUCCESS_RET)
    assert {0x4324B8, 0x4324C2} <= postdom[PROBE.MAP_ENTRY]
    assert {0x4324B8, 0x4324C2} <= postdom[PROBE.MAP_SUCCESS_JOIN]
