"""Regression contract for the sparse bisection probe's fixture math (no game runtime)."""

from __future__ import annotations

from patches.selection import g5_selection_cap50_bisect as bisect
from tools.g5_bisect_attack_probe import (
    SPARSE_DX,
    SPARSE_DY,
    SPARSE_SEED_COUNT,
    ATTACK_PRIMARY_DEST_OFFSET,
    ATTACK_FALLBACK_DEST_OFFSET,
    SAFE_SCREEN_BOX,
    _in_safe_box,
    sparse_fixture_requests,
)


def test_sparse_grid_is_a_strict_subset_of_the_proven_dense_grid() -> None:
    # dense_fixture_requests (g5_candidate_drag_probe.py) covers dx -3..3,
    # dy -3..4 and is already proven to spawn on open, selectable ground.
    assert min(SPARSE_DX) >= -3 and max(SPARSE_DX) <= 3
    assert min(SPARSE_DY) >= -3 and max(SPARSE_DY) <= 4


def test_sparse_seed_count_is_worker_plus_nineteen() -> None:
    assert SPARSE_SEED_COUNT == 19


def test_sparse_fixture_requests_excludes_the_worker_cell_and_matches_count() -> None:
    worker = {"x": 90, "y": 90}
    requests = sparse_fixture_requests(worker)
    assert len(requests) == SPARSE_SEED_COUNT
    assert all(not (r["x"] == 90 and r["y"] == 90) for r in requests)


def test_attack_dest_offset_is_outside_the_sparse_grid_footprint() -> None:
    assert ATTACK_PRIMARY_DEST_OFFSET[1] > max(SPARSE_DY)
    assert ATTACK_FALLBACK_DEST_OFFSET[1] > max(SPARSE_DY)


def test_in_safe_box_accepts_interior_and_rejects_outside() -> None:
    x0, x1, y0, y1 = SAFE_SCREEN_BOX
    assert _in_safe_box((x0, y0))
    assert _in_safe_box((x1, y1))
    assert not _in_safe_box((x0 - 1, y0))
    assert not _in_safe_box((x0, y1 + 1))


def test_bundle_choices_match_the_bisection_builders() -> None:
    # The CLI's --bundle choices are built from bisect.BUILDERS at import
    # time; confirm the set has not silently drifted apart from the module
    # this probe actually dispatches through.
    assert set(bisect.BUILDERS) == {"G1", "G2", "G3", "G5", "V1_FULL", "V2_FULL"}
