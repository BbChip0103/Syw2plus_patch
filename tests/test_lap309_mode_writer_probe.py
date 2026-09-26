"""Regression tests for the lap309 static probe's stack model."""
from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROBE_PATH = ROOT / "docs/history/laps/probes/20260912_lap309_work_v3_mode_writer_order_probe.py"
SPEC = importlib.util.spec_from_file_location("lap309_probe", PROBE_PATH)
assert SPEC and SPEC.loader
PROBE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PROBE)


def test_call_convention_cleanup_is_explicit():
    assert PROBE.stack_adjustment("call   0x4db933", PROBE.CALLEE_LOG_CALL, PROBE.CALL_CLEANUP_BYTES) == 0
    assert PROBE.stack_adjustment("call   DWORD PTR [ecx+0x28]", PROBE.CALLEE_VCALL, PROBE.CALL_CLEANUP_BYTES) == -4
    assert PROBE.stack_adjustment("call   DWORD PTR ds:0x4e51cc", PROBE.CALLEE_IMPORT_CALL, PROBE.CALL_CLEANUP_BYTES) == -16


def test_corrected_model_has_one_depth_at_single_ret():
    instructions = PROBE.parse_text()
    callee = [(address, instruction) for address, instruction in instructions if PROBE.CALLEE <= address < PROBE.CALLEE_END]
    depths, offsets = PROBE.walk_depths(callee, PROBE.CALLEE, PROBE.CALL_CLEANUP_BYTES)
    assert depths[PROBE.CALLEE_JOIN] == {0x100}
    assert depths[PROBE.CALLEE_RET] == {0}
    assert offsets[PROBE.CALLEE_ARG1_READ] == {4}
    assert offsets[PROBE.CALLEE_JOIN] == {8}
