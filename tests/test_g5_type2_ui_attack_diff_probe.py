"""Regression contract for the diff-based type2 UI attack probe."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

from tools.g5_type2_ui_attack_diff_probe import (
    ATTACKER_OFFSET_FROM_WORKER,
    DIFF_ROI,
    DIFF_THRESHOLD,
    PHASE_A_ATTACKER_WORLD,
    PHASE_A_TARGET_WORLD,
    RETRY_OFFSETS,
    TARGET_OFFSET_FROM_ATTACKER,
    candidate_click_points,
    main,
    run_probe,
    sprite_diff_centroid,
)


def _write_solid(path: Path, size: tuple[int, int], color: tuple[int, int, int]) -> None:
    Image.fromarray(np.full((size[1], size[0], 3), color, dtype=np.uint8)).save(path)


def test_offsets_keep_phases_isolated_and_in_bounds() -> None:
    assert ATTACKER_OFFSET_FROM_WORKER != (0, 0)
    assert TARGET_OFFSET_FROM_ATTACKER != (0, 0)
    assert all(0 <= v < 180 for v in PHASE_A_ATTACKER_WORLD)
    assert all(0 <= v < 180 for v in PHASE_A_TARGET_WORLD)
    assert PHASE_A_ATTACKER_WORLD != PHASE_A_TARGET_WORLD
    # Phase A must stay far from the worker-relative phase B anchor so it
    # never contributes a pixel to a phase B before/after diff.
    assert all(v > 100 for v in PHASE_A_ATTACKER_WORLD)


def test_target_offset_is_farther_than_lap672s_contaminated_distance() -> None:
    prior_distance = (3 ** 2 + 1 ** 2) ** 0.5
    new_distance = sum(v ** 2 for v in TARGET_OFFSET_FROM_ATTACKER) ** 0.5
    assert new_distance > prior_distance


def test_sprite_diff_centroid_finds_a_synthetic_new_square(tmp_path: Path) -> None:
    before = tmp_path / "before.png"
    after = tmp_path / "after.png"
    _write_solid(before, (200, 200), (10, 10, 10))
    canvas = np.full((200, 200, 3), (10, 10, 10), dtype=np.uint8)
    canvas[40:60, 90:110] = (250, 30, 30)
    Image.fromarray(canvas).save(after)
    result = sprite_diff_centroid(before, after, roi=(0, 0, 200, 200), threshold=30)
    assert result["pixel_count"] == 400
    assert result["centroid"] == [100, 50]
    assert result["bbox"] == {"x0": 90, "x1": 109, "y0": 40, "y1": 59}


def test_sprite_diff_centroid_empty_when_nothing_changed(tmp_path: Path) -> None:
    before = tmp_path / "before.png"
    after = tmp_path / "after.png"
    _write_solid(before, (100, 100), (5, 5, 5))
    _write_solid(after, (100, 100), (5, 5, 5))
    result = sprite_diff_centroid(before, after)
    assert result["pixel_count"] == 0
    assert result["centroid"] is None


def test_sprite_diff_centroid_stability_reference_excludes_ambient_blob(tmp_path: Path) -> None:
    reference = tmp_path / "reference.png"
    before = tmp_path / "before.png"
    after = tmp_path / "after.png"
    base = np.full((200, 200, 3), (10, 10, 10), dtype=np.uint8)
    _write_solid(reference, (200, 200), (10, 10, 10))
    # An ambient region (e.g. idle animation) is already different in
    # "before" relative to "reference", before anything new has spawned.
    ambient = base.copy()
    ambient[10:30, 10:30] = (200, 200, 10)
    Image.fromarray(ambient).save(before)
    # "after" keeps animating that same ambient region on its own schedule
    # (a different color again, so a naive before/after diff would still
    # flag it) and separately adds one genuinely new blob elsewhere.
    sprite = base.copy()
    sprite[10:30, 10:30] = (10, 200, 200)
    sprite[100:120, 150:170] = (30, 200, 30)
    Image.fromarray(sprite).save(after)
    result = sprite_diff_centroid(
        before, after, roi=(0, 0, 200, 200), threshold=30, stability_reference_path=reference,
    )
    assert result["ambient_excluded_pixels"] > 0
    assert result["confident_single_blob"] is True
    assert result["bbox"] == {"x0": 150, "x1": 169, "y0": 100, "y1": 119}


def test_sprite_diff_centroid_flags_unconfident_when_no_blob_fits_sprite_size(tmp_path: Path) -> None:
    before = tmp_path / "before.png"
    after = tmp_path / "after.png"
    _write_solid(before, (200, 200), (10, 10, 10))
    canvas = np.full((200, 200, 3), (10, 10, 10), dtype=np.uint8)
    canvas[0:200, 0:100] = (250, 30, 30)  # far larger than any plausible unit sprite
    Image.fromarray(canvas).save(after)
    result = sprite_diff_centroid(
        before, after, roi=(0, 0, 200, 200), threshold=30, min_blob_pixels=40, max_blob_pixels=4000,
    )
    assert result["confident_single_blob"] is False
    assert result["pixel_count"] > 4000


def test_sprite_diff_centroid_respects_roi(tmp_path: Path) -> None:
    before = tmp_path / "before.png"
    after = tmp_path / "after.png"
    _write_solid(before, (200, 200), (10, 10, 10))
    canvas = np.full((200, 200, 3), (10, 10, 10), dtype=np.uint8)
    canvas[190:195, 90:95] = (250, 30, 30)  # inside the HUD band, outside DIFF_ROI
    Image.fromarray(canvas).save(after)
    result = sprite_diff_centroid(before, after, roi=(0, 0, 200, 180), threshold=30)
    assert result["pixel_count"] == 0


def test_default_diff_roi_excludes_the_bottom_command_hud() -> None:
    assert DIFF_ROI == (0, 0, 1600, 480)
    assert DIFF_THRESHOLD > 0


def test_candidate_click_points_starts_centered_and_dedupes() -> None:
    points = candidate_click_points((500, 300))
    assert points[0] == (500, 300)
    assert len(points) == len(set(points))
    assert len(points) <= len(RETRY_OFFSETS)


def test_candidate_click_points_drops_out_of_viewport_offsets() -> None:
    points = candidate_click_points((4, 4))
    assert all(0 <= x <= 1580 and 0 <= y <= 460 for x, y in points)
    assert (4 - 8, 4 - 8) not in points


def test_module_exposes_runtime_entry_points() -> None:
    assert callable(run_probe)
    assert callable(main)
