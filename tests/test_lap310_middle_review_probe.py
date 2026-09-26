"""Regression tests for the lap310 middle review probe's cleanup solver.

Unlike a table-echo test, these assert values the probe *derives* from the
SHA-pinned image: the two call-cleanup amounts and the resolved import name.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROBE_PATH = ROOT / "docs/history/laps/probes/20260912_lap310_middle_lap309_v3_review_probe.py"
SPEC = importlib.util.spec_from_file_location("lap310_probe", PROBE_PATH)
assert SPEC and SPEC.loader
PROBE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PROBE)


def _image() -> "PROBE.Image":
    return PROBE.Image(PROBE.EXE.read_bytes())


def test_cleanup_amounts_are_solved_not_assumed():
    join_a, _v, _i, offsets_a = PROBE.walk(
        [entry for entry in PROBE.CALLEE_DECODE if entry[0] < PROBE.CALLEE_JOIN], set(PROBE.PATH_A_SKIP)
    )
    join_b, join_b_v, _ib, _ob = PROBE.walk(
        [entry for entry in PROBE.CALLEE_DECODE if entry[0] < PROBE.CALLEE_JOIN], set()
    )
    solved_v = (join_b - join_a) // join_b_v
    const_b, v_b, i_b, _offsets_b = PROBE.walk(PROBE.CALLEE_DECODE, set())
    solved_i = (const_b - v_b * solved_v) // i_b
    assert (solved_v, solved_i) == (4, 16)
    assert offsets_a[PROBE.CALLEE_ARG1_READ] == 4


def test_import_slot_resolves_to_a_four_argument_stdcall():
    name = _image().import_name_for_slot(PROBE.IMPORT_SLOT)
    assert name == "MessageBoxA"
    assert PROBE.STDCALL_ARITY[name] * 4 == 16


def test_failure_arm_seed_is_the_branch_fall_through():
    assert PROBE.MAP_FAILURE_SEED == PROBE.MAP_GATE_BRANCH + 2
    assert PROBE.MAP_FAILURE_SEED != PROBE.MAP_FAILURE_RET
