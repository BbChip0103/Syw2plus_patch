"""Regression contract for the building-target G5 attack diff probe."""

from __future__ import annotations

from tools.g5_building_attack_diff_probe import (
    BUILDING_TYPE,
    MAX_BUILDING_BLOB_PIXELS,
    MIN_BUILDING_BLOB_PIXELS,
    PHASE_A_ATTACKER_WORLD,
    PHASE_A_BUILDING_WORLD,
    RETRY_OFFSETS,
    TARGET_OFFSET_FROM_ATTACKER,
    candidate_click_points,
    main,
    run_probe,
)


def test_building_type_is_the_confirmed_domain_eligible_type46() -> None:
    assert BUILDING_TYPE == 46


def test_phase_a_pair_is_isolated_and_in_bounds() -> None:
    assert all(0 <= v < 180 for v in PHASE_A_ATTACKER_WORLD)
    assert all(0 <= v < 180 for v in PHASE_A_BUILDING_WORLD)
    assert PHASE_A_ATTACKER_WORLD != PHASE_A_BUILDING_WORLD
    assert all(v > 100 for v in PHASE_A_ATTACKER_WORLD)


def test_building_blob_size_band_is_wider_than_a_single_unit_sprite() -> None:
    # lap673's unit-sized band topped out at 4000px; a 3x3-tile building
    # footprint must be allowed to be substantially larger.
    assert MIN_BUILDING_BLOB_PIXELS >= 100
    assert MAX_BUILDING_BLOB_PIXELS > 4000


def test_target_offset_keeps_building_footprint_clear_of_attacker_tile() -> None:
    assert TARGET_OFFSET_FROM_ATTACKER != (0, 0)
    distance = sum(v ** 2 for v in TARGET_OFFSET_FROM_ATTACKER) ** 0.5
    assert distance > 3.16  # farther than lap672's contaminated (3, -1) offset


def test_candidate_click_points_starts_centered_and_dedupes() -> None:
    points = candidate_click_points((500, 300))
    assert points[0] == (500, 300)
    assert len(points) == len(set(points))
    assert len(points) <= len(RETRY_OFFSETS)


def test_candidate_click_points_drops_out_of_viewport_offsets() -> None:
    points = candidate_click_points((4, 4))
    assert all(0 <= x <= 1580 and 0 <= y <= 460 for x, y in points)


def test_module_exposes_runtime_entry_points() -> None:
    assert callable(run_probe)
    assert callable(main)
