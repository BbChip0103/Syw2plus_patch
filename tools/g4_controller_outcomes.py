#!/usr/bin/env python3
"""Summarize controller opcode residence windows from dense G4 samples."""

from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


def _player(sample: Mapping[str, Any], owner: int) -> Mapping[str, Any]:
    players = sample.get("players")
    if not isinstance(players, list) or owner >= len(players) or not isinstance(players[owner], Mapping):
        raise ValueError("sample lacks indexed player state")
    return players[owner]


def _unit_count(sample: Mapping[str, Any], owner: int) -> int:
    units = sample.get("units")
    if not isinstance(units, list):
        raise ValueError("sample units are not a list")
    return sum(isinstance(unit, Mapping) and unit.get("owner") == owner for unit in units)


def _snapshot(sample: Mapping[str, Any], owner: int) -> dict[str, int]:
    player = _player(sample, owner)
    tick = sample.get("tick")
    if not isinstance(tick, int):
        raise ValueError("sample tick is not an integer")
    result = {"tick": tick, "units": _unit_count(sample, owner)}
    for key in ("rice", "wood", "reserved", "count", "used"):
        value = player.get(key)
        if not isinstance(value, int):
            raise ValueError(f"player {key} is not an integer")
        result[key] = value
    return result


def windows(samples: Sequence[Mapping[str, Any]], owner: int) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    active: dict[str, Any] | None = None
    previous_sample: Mapping[str, Any] | None = None
    for sample in samples:
        player = _player(sample, owner)
        opcode = player.get("controller_opcode")
        argument = player.get("controller_argument")
        if not isinstance(opcode, int) or not isinstance(argument, int):
            raise ValueError("controller fields are not integers")
        if active is not None and opcode != active["opcode"]:
            assert previous_sample is not None
            end = _snapshot(previous_sample, owner)
            start = active.pop("start")
            active.update({
                "end": end,
                "duration_ticks": end["tick"] - start["tick"],
                "sample_count": active.pop("samples"),
                "released_to_zero": opcode == 0,
                "delta": {key: end[key] - start[key]
                          for key in ("units", "rice", "wood", "reserved", "count", "used")},
                "truncated": False,
            })
            result.append(active)
            active = None
        if opcode and active is None:
            active = {
                "opcode": opcode,
                "argument": argument,
                "start": _snapshot(sample, owner),
                "samples": 0,
            }
        if active is not None:
            active["samples"] += 1
        previous_sample = sample
    if active is not None and previous_sample is not None:
        end = _snapshot(previous_sample, owner)
        start = active.pop("start")
        active.update({
            "end": end,
            "duration_ticks": end["tick"] - start["tick"],
            "sample_count": active.pop("samples"),
            "released_to_zero": False,
            "delta": {key: end[key] - start[key]
                      for key in ("units", "rice", "wood", "reserved", "count", "used")},
            "truncated": True,
        })
        result.append(active)
    return result


def summarize(document: Mapping[str, Any]) -> dict[str, Any]:
    samples = document.get("g4_ai_smoke", {}).get("samples", [])
    if not isinstance(samples, list):
        raise ValueError("G4 samples are not a list")
    owners: dict[str, Any] = {}
    for owner in (0, 1):
        owner_windows = windows(samples, owner)
        grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
        for window in owner_windows:
            grouped[window["opcode"]].append(window)
        owners[str(owner)] = {
            "windows": owner_windows,
            "by_opcode": {
                str(opcode): {
                    "count": len(items),
                    "released_to_zero": sum(item["released_to_zero"] for item in items),
                    "truncated": sum(item["truncated"] for item in items),
                    "max_duration_ticks": max(item["duration_ticks"] for item in items),
                    "total_duration_ticks": sum(item["duration_ticks"] for item in items),
                }
                for opcode, items in sorted(grouped.items())
            },
        }
    return {
        "schema": "syw2plus.g4.controller_outcomes.v1",
        "sample_count": len(samples),
        "owners": owners,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = summarize(json.loads(args.input.read_text()))
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
