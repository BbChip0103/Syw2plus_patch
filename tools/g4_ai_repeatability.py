#!/usr/bin/env python3
"""Compare two fixed-seed G4 AI smoke captures without volatile pid/time fields."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


def _keep(mapping: Mapping[str, Any], names: tuple[str, ...]) -> dict[str, Any]:
    return {name: mapping.get(name) for name in names}


def normalized_fixture(evidence: Mapping[str, Any]) -> dict[str, Any]:
    fixture = evidence.get("fixture")
    scene = evidence.get("scene")
    smoke = evidence.get("g4_ai_smoke")
    if not isinstance(fixture, Mapping) or not isinstance(scene, Mapping) or not isinstance(smoke, Mapping):
        raise ValueError("capture lacks fixture/scene/g4_ai_smoke")
    samples = smoke.get("samples")
    if not isinstance(samples, list) or not samples or not isinstance(samples[0], Mapping):
        raise ValueError("capture has no G4 samples")
    normalized_samples: list[dict[str, Any]] = []
    for sample in samples:
        if not isinstance(sample, Mapping):
            raise ValueError("G4 sample is not an object")
        players = sample.get("players")
        units = sample.get("units")
        if not isinstance(players, list) or not isinstance(units, list):
            raise ValueError("G4 sample lacks players/units")
        normalized_samples.append({
            "players": [
                _keep(player, ("owner", "nation", "ai", "rice", "wood", "reserved", "count", "used", "count_cap", "cap", "controller_opcode", "controller_argument"))
                for player in players
                if isinstance(player, Mapping) and player.get("owner") in (0, 1)
            ],
            "units": [
                _keep(unit, ("slot", "type", "owner", "hp", "command", "production_type", "progress", "x", "y"))
                for unit in units
                if isinstance(unit, Mapping)
            ],
        })
    return {
        "fixture_kind": fixture.get("kind"),
        "control_bridge": fixture.get("control_bridge"),
        "memory_writes": fixture.get("memory_writes"),
        "map": scene.get("map"),
        "owners": scene.get("owners"),
        "world_bounds": scene.get("world_bounds"),
        "series": normalized_samples,
        "summary": smoke.get("summary"),
    }


def signature(value: Mapping[str, Any]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _stable_projection(value: Mapping[str, Any]) -> dict[str, Any]:
    projected = json.loads(json.dumps(value))
    summary = projected.get("summary", {})
    if isinstance(summary, dict):
        summary.pop("first_tick", None)
        summary.pop("last_tick", None)
    for sample in projected.get("series", []):
        for unit in sample.get("units", []):
            unit.pop("progress", None)
    return projected


def _max_progress_delta(first: Mapping[str, Any], second: Mapping[str, Any]) -> int | None:
    deltas: list[int] = []
    left_series = first.get("series")
    right_series = second.get("series")
    if not isinstance(left_series, list) or not isinstance(right_series, list):
        return None
    if len(left_series) != len(right_series):
        return None
    for left_sample, right_sample in zip(left_series, right_series, strict=True):
        left_units = left_sample.get("units", [])
        right_units = right_sample.get("units", [])
        if len(left_units) != len(right_units):
            return None
        for left_unit, right_unit in zip(left_units, right_units, strict=True):
            left_progress = left_unit.get("progress")
            right_progress = right_unit.get("progress")
            if not isinstance(left_progress, int) or not isinstance(right_progress, int):
                return None
            deltas.append(abs(left_progress - right_progress))
    return max(deltas, default=0)


def compare(first: Mapping[str, Any], second: Mapping[str, Any]) -> dict[str, Any]:
    left = normalized_fixture(first)
    right = normalized_fixture(second)
    exact_equal = left == right
    stable_left = _stable_projection(left)
    stable_right = _stable_projection(right)
    max_progress_delta = _max_progress_delta(left, right)
    left_summary = left.get("summary", {})
    right_summary = right.get("summary", {})
    tick_deltas = [
        abs(int(left_summary[name]) - int(right_summary[name]))
        for name in ("first_tick", "last_tick")
        if isinstance(left_summary, Mapping)
        and isinstance(right_summary, Mapping)
        and isinstance(left_summary.get(name), int)
        and isinstance(right_summary.get(name), int)
    ]
    max_tick_delta = max(tick_deltas, default=0)
    equal = (
        stable_left == stable_right
        and max_progress_delta is not None
        and max_progress_delta <= 1
        and max_tick_delta <= 1
    )
    classification = "FIXED_FIXTURE_DRIFT"
    if exact_equal:
        classification = "FIXED_FIXTURE_REPEATABLE_EXACT"
    elif equal:
        classification = "FIXED_FIXTURE_REPEATABLE_TOLERANCE"
    return {
        "schema": "syw2plus.g4.ai_repeatability.v1",
        "equal": equal,
        "exact_equal": exact_equal,
        "classification": classification,
        "max_progress_delta": max_progress_delta,
        "max_tick_delta": max_tick_delta,
        "first_signature": signature(stable_left),
        "second_signature": signature(stable_right),
        "first": left,
        "second": right,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("first", type=Path)
    parser.add_argument("second", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = compare(json.loads(args.first.read_text()), json.loads(args.second.read_text()))
    rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    else:
        print(rendered, end="")
    return 0 if report["equal"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
