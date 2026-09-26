"""Regression contract for the type2-attacker UI attack probe."""

from __future__ import annotations

from tools.g5_type2_ui_attack_probe import (
    ATTACKER_OFFSET_FROM_WORKER,
    TARGET_OFFSET_FROM_ATTACKER,
    X_SWEEP_OFFSETS,
    Y_SWEEP_OFFSETS,
    main,
    run_probe,
)


def test_offsets_keep_attacker_and_target_distinct_and_in_bounds() -> None:
    assert ATTACKER_OFFSET_FROM_WORKER != (0, 0)
    assert TARGET_OFFSET_FROM_ATTACKER != (0, 0)
    assert all(abs(v) < 20 for v in ATTACKER_OFFSET_FROM_WORKER)
    assert all(abs(v) < 20 for v in TARGET_OFFSET_FROM_ATTACKER)


def test_y_sweep_offsets_are_upward_only_and_bounded() -> None:
    assert Y_SWEEP_OFFSETS[0] == 0
    assert all(dy <= 0 for dy in Y_SWEEP_OFFSETS)
    assert Y_SWEEP_OFFSETS == sorted(Y_SWEEP_OFFSETS, reverse=True)
    assert min(Y_SWEEP_OFFSETS) >= -80


def test_x_sweep_offsets_start_centered_and_bounded() -> None:
    assert X_SWEEP_OFFSETS[0] == 0
    assert all(abs(dx) <= 80 for dx in X_SWEEP_OFFSETS)


def test_module_exposes_runtime_entry_points() -> None:
    assert callable(run_probe)
    assert callable(main)
