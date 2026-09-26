#!/usr/bin/env python3
"""Measure original mobile-unit displacement and command occupancy in G4 captures."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
from typing import Any, Mapping

ROW_RE = re.compile(r"^\s*\{(0x[0-9A-Fa-f]+)u,.*// type (\d+)\s*$", re.MULTILINE)


def mobile_types(template_header: str) -> set[int]:
    flags = {int(type_id): int(raw_flags, 16) for raw_flags, type_id in ROW_RE.findall(template_header)}
    if len(flags) < 100:
        raise ValueError("unit template header did not expose the expected type rows")
    return {type_id for type_id, value in flags.items() if value & 1}


def summarize(document: Mapping[str, Any], mobile: set[int], minimum_ticks: int = 300) -> dict[str, Any]:
    samples = document.get("g4_ai_smoke", {}).get("samples", [])
    if not isinstance(samples, list):
        raise ValueError("G4 samples are not a list")
    tracks: dict[tuple[int, int, int], dict[str, Any]] = {}
    for sample in samples:
        tick = sample.get("tick")
        units = sample.get("units")
        if not isinstance(tick, int) or not isinstance(units, list):
            raise ValueError("sample tick/units are malformed")
        for unit in units:
            if not isinstance(unit, Mapping):
                continue
            values = [unit.get(key) for key in ("internal_id", "type", "owner", "x", "y", "command")]
            if not all(isinstance(value, int) for value in values):
                raise ValueError("unit movement fields are not integers")
            internal_id, type_id, owner, x, y, command = values
            identity = (internal_id, type_id, owner)
            track = tracks.setdefault(identity, {
                "internal_id": internal_id,
                "type": type_id,
                "owner": owner,
                "first_tick": tick,
                "last_tick": tick,
                "first_position": [x, y],
                "last_position": [x, y],
                "previous_position": [x, y],
                "observations": 0,
                "distance": 0,
                "max_step": 0,
                "commands": Counter(),
            })
            px, py = track["previous_position"]
            step = max(abs(x - px), abs(y - py))
            track["distance"] += step
            track["max_step"] = max(track["max_step"], step)
            track["previous_position"] = [x, y]
            track["last_position"] = [x, y]
            track["last_tick"] = tick
            track["observations"] += 1
            track["commands"][command] += 1
    rows: list[dict[str, Any]] = []
    for track in tracks.values():
        track.pop("previous_position")
        track["commands"] = {str(key): value for key, value in sorted(track["commands"].items())}
        track["lifetime_ticks_observed"] = track["last_tick"] - track["first_tick"]
        track["mobile_type"] = track["type"] in mobile
        rows.append(track)
    rows.sort(key=lambda item: (item["owner"], item["internal_id"], item["type"]))
    owners: dict[str, Any] = {}
    for owner in (0, 1):
        eligible = [row for row in rows if row["owner"] == owner and row["mobile_type"]
                    and row["lifetime_ticks_observed"] >= minimum_ticks]
        stationary = [row for row in eligible if row["distance"] == 0]
        owners[str(owner)] = {
            "eligible_mobile_tracks": len(eligible),
            "moved_tracks": len(eligible) - len(stationary),
            "stationary_tracks": len(stationary),
            "stationary_by_type": dict(sorted(Counter(row["type"] for row in stationary).items())),
            "stationary": stationary,
        }
    return {
        "schema": "syw2plus.g4.unit_movement_outcomes.v1",
        "sample_count": len(samples),
        "minimum_ticks": minimum_ticks,
        "mobile_type_count": len(mobile),
        "owners": owners,
        "tracks": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--template-header", required=True, type=Path)
    parser.add_argument("--minimum-ticks", type=int, default=300)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = summarize(
        json.loads(args.input.read_text()),
        mobile_types(args.template_header.read_text()),
        args.minimum_ticks,
    )
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
