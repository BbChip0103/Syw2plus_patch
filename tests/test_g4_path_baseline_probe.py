"""Regression contract for the G4 path baseline probe's pure logic (no game runtime)."""

from __future__ import annotations

import math

import numpy as np

from tools.g4_path_baseline_probe import (
    CAMERA_PAN_TARGET_DISTANCE_TILES,
    LONG_DISTANCE_OFFSET_MAGNITUDES,
    OBSTACLE_ROW_OFFSET_MAGNITUDE,
    STAGNATION_TICKS,
    ARRIVAL_RADIUS_TILES,
    TRACE_TIMEOUT_S,
    _safe_box_margin,
    _screen_to_world,
    compute_metrics,
    main as probe_main,
    pan_candidate_ok,
    safe_screen_box,
)


def test_long_distance_offset_magnitudes_exceed_lap682_baseline() -> None:
    # lap682's own proven MOVE destinations are dy=+6/dy=-4 (magnitude <= 6);
    # every escalation candidate here must be strictly farther than that.
    assert all(magnitude > 6 for magnitude in LONG_DISTANCE_OFFSET_MAGNITUDES)
    assert list(LONG_DISTANCE_OFFSET_MAGNITUDES) == sorted(LONG_DISTANCE_OFFSET_MAGNITUDES, reverse=True)


def test_safe_screen_box_is_derived_from_measured_window() -> None:
    box = safe_screen_box(800, 600)
    x0, x1, y0, y1 = box
    assert (x0, x1) == (40, 760)
    assert y0 == 40
    assert y1 == 480  # 600 * (480/600) HUD cutoff


def test_safe_box_margin_sign() -> None:
    box = safe_screen_box(800, 600)
    x0, x1, y0, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    assert _safe_box_margin((cx, cy), box) > 0
    assert _safe_box_margin((x0, cy), box) == 0
    assert _safe_box_margin((x0 - 1, cy), box) < 0
    assert _safe_box_margin((cx, y1 + 1), box) < 0


def test_screen_to_world_applies_affine_forward() -> None:
    matrix = np.array([[2.0, 0.0], [0.0, 2.0]])
    offset = np.array([10.0, -5.0])
    world = _screen_to_world((3, 4), matrix, offset)
    assert world == (16.0, 3.0)


def test_pan_candidate_ok_requires_both_bounds_and_distance() -> None:
    worker_start = (50, 50)
    # far enough and on the map: accepted
    ok, dist = pan_candidate_ok((50, 50 + CAMERA_PAN_TARGET_DISTANCE_TILES), worker_start, CAMERA_PAN_TARGET_DISTANCE_TILES)
    assert ok is True
    assert dist == CAMERA_PAN_TARGET_DISTANCE_TILES
    # far enough but off the 180x180 map: rejected
    ok, _ = pan_candidate_ok((-1, 50), worker_start, CAMERA_PAN_TARGET_DISTANCE_TILES)
    assert ok is False
    # on the map but short of the target distance: rejected
    ok, _ = pan_candidate_ok((50, 55), worker_start, CAMERA_PAN_TARGET_DISTANCE_TILES)
    assert ok is False


def test_obstacle_row_offset_is_larger_than_dense_fixture_gap() -> None:
    # dense_fixture_requests excludes dy=-4 (starts its grid at -3) to dodge
    # the base footprint; the obstacle destination must reach past that row.
    assert OBSTACLE_ROW_OFFSET_MAGNITUDE > 4


def _rows(entries: list[tuple[int, int, int, int]]) -> list[dict]:
    return [
        {"slot": slot, "x": x, "y": y, "command": command, "hp": 100}
        for slot, x, y, command in entries
    ]


def test_compute_metrics_detects_arrival_and_path_ratio() -> None:
    # Slot 1 walks in a straight line from (0, 0) all the way to destination
    # (10, 0), one tile per tick; it enters ARRIVAL_RADIUS_TILES (3) of the
    # destination at x=7 (tick 7), and its total path length equals the
    # straight-line distance, so path_ratio is 1.0.
    destination = (10, 0)
    samples = []
    for tick, x in enumerate(range(0, 11)):
        rows = _rows([(1, x, 0, 3)])
        for row in rows:
            row["distance_to_destination"] = math.hypot(row["x"] - destination[0], row["y"] - destination[1])
        samples.append({"tick": tick, "rows": rows})
    trace = {"samples": samples}
    metrics = compute_metrics(trace, [1], destination, {1: (0, 0)})
    row = metrics["per_slot"][0]
    assert row["arrived"] is True
    assert row["arrival_tick"] == 7
    assert row["path_ratio"] == 1.0
    assert metrics["arrival_rate"] == 1.0


def test_compute_metrics_flags_stagnation_without_requiring_arrival() -> None:
    # Slot 2 never moves from (0, 0) while non-idle (command == 3), and never
    # gets within ARRIVAL_RADIUS_TILES of a far destination.
    destination = (50, 0)
    tick_count = STAGNATION_TICKS + 5
    samples = []
    for tick in range(tick_count):
        rows = _rows([(2, 0, 0, 3)])
        for row in rows:
            row["distance_to_destination"] = math.hypot(row["x"] - destination[0], row["y"] - destination[1])
        samples.append({"tick": tick, "rows": rows})
    trace = {"samples": samples}
    metrics = compute_metrics(trace, [2], destination, {2: (0, 0)})
    row = metrics["per_slot"][0]
    assert row["arrived"] is False
    assert row["path_length"] == 0.0
    assert row["stagnation_runs"], "a >=STAGNATION_TICKS unchanged-position run must be recorded"
    assert row["stagnation_runs"][0]["length_ticks"] >= STAGNATION_TICKS
    assert metrics["stagnating_slot_count"] == 1
    assert destination[0] - 0 > ARRIVAL_RADIUS_TILES


def test_cli_trace_timeout_s_defaults_to_module_constant_and_is_overridable(
    tmp_path, monkeypatch,
) -> None:
    # lap711 v3 hypothesis test: --trace-timeout-s must default to the
    # existing TRACE_TIMEOUT_S (so every prior invocation without the flag
    # is unaffected) but be overridable so a fresh run can probe whether a
    # longer movement-trace window raises arrival_rate.
    captured: dict = {}

    def fake_run_probe(source, runtime_root, artifact_root, *, scenario, variant, trace_timeout_s):
        captured["trace_timeout_s"] = trace_timeout_s
        return {"status": "PATH_TRACE_COMPLETE", "cleanup": {"ok": True}}

    monkeypatch.setattr("tools.g4_path_baseline_probe.run_probe", fake_run_probe)

    probe_main(["--artifact-root", str(tmp_path / "default")])
    assert captured["trace_timeout_s"] == TRACE_TIMEOUT_S

    probe_main(["--artifact-root", str(tmp_path / "override"), "--trace-timeout-s", "165"])
    assert captured["trace_timeout_s"] == 165.0
