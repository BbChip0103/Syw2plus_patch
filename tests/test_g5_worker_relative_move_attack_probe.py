"""Regression contract for the worker-relative destination math (no game runtime)."""

from __future__ import annotations

from tools.g5_worker_relative_move_attack_probe import (
    PRIMARY_DEST_OFFSET,
    FALLBACK_DEST_OFFSET,
    ATTACK_PRIMARY_DEST_OFFSET,
    ATTACK_FALLBACK_DEST_OFFSET,
    SAFE_SCREEN_BOX,
    _in_safe_box,
)


def test_dest_offsets_are_outside_the_dense_fixture_grid_footprint() -> None:
    # dense_fixture_requests covers dx in -3..3, dy in -3..4; both worker-
    # relative destination candidates must sit just beyond that footprint so
    # they land on ground already proven open by the fixture spawn.
    assert PRIMARY_DEST_OFFSET[1] > 4
    assert FALLBACK_DEST_OFFSET[1] < -3


def test_attack_dest_offsets_never_equal_the_move_dest_offsets() -> None:
    # lap683 middle: a shared destination between MOVE and ATTACK cannot show
    # whether the attack broadcast itself reached every selected unit, since
    # units already sitting on that tile from the MOVE phase confound the
    # read. The attack candidates must be a disjoint set of tiles.
    move_offsets = {PRIMARY_DEST_OFFSET, FALLBACK_DEST_OFFSET}
    attack_offsets = {ATTACK_PRIMARY_DEST_OFFSET, ATTACK_FALLBACK_DEST_OFFSET}
    assert move_offsets.isdisjoint(attack_offsets)


def test_in_safe_box_accepts_interior_and_rejects_outside() -> None:
    x0, x1, y0, y1 = SAFE_SCREEN_BOX

    assert _in_safe_box((x0, y0))
    assert _in_safe_box((x1, y1))
    assert _in_safe_box(((x0 + x1) / 2, (y0 + y1) / 2))
    assert not _in_safe_box((x0 - 1, y0))
    assert not _in_safe_box((x0, y1 + 1))
