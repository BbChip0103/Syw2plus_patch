"""Regression contract for the clean-op8/y-sweep attack attribution probe."""

from __future__ import annotations

from tools.g5_attack_hit_offset_probe import Y_SWEEP_OFFSETS, main, run_probe


def test_y_sweep_offsets_are_upward_only_and_bounded() -> None:
    assert Y_SWEEP_OFFSETS[0] == 0
    assert all(dy <= 0 for dy in Y_SWEEP_OFFSETS)
    assert Y_SWEEP_OFFSETS == sorted(Y_SWEEP_OFFSETS, reverse=True)
    assert min(Y_SWEEP_OFFSETS) >= -80


def test_module_exposes_runtime_entry_points() -> None:
    assert callable(run_probe)
    assert callable(main)
