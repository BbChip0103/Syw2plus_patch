"""Regression contract for the screen<->world calibration math (no game runtime)."""

from __future__ import annotations

from tools.g5_screen_world_calibration import decode_xy, fit_affine


def test_decode_xy_handles_signed_and_unsigned_halfwords() -> None:
    assert decode_xy((143 << 16) | 47) == (47, 143)
    assert decode_xy(0) == (0, 0)


def test_fit_affine_recovers_exact_linear_transform_from_three_points() -> None:
    # world = 2*screen_x + 3*screen_y + 10, screen_y - screen_x + 5
    points = [
        ((0, 0), (10, 5)),
        ((1, 0), (12, 4)),
        ((0, 1), (13, 6)),
    ]

    matrix, offset = fit_affine(points)

    for screen, world in points:
        predicted = matrix @ screen + offset
        assert tuple(round(v) for v in predicted) == world


def test_fit_affine_inverts_to_recover_screen_for_a_target_world_point() -> None:
    import numpy as np

    points = [
        ((250, 200), (7, 3)),
        ((500, 200), (15, 3)),
        ((250, 440), (7, 22)),
    ]

    matrix, offset = fit_affine(points)
    matrix_inv = np.linalg.inv(matrix)
    target_world = (11, 12)
    screen = matrix_inv @ (np.array(target_world) - offset)
    predicted_world = matrix @ screen + offset

    assert tuple(round(v) for v in predicted_world) == target_world
