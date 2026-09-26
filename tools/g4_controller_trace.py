#!/usr/bin/env python3
"""Compare dense fixed-seed controller opcode episode traces."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


def episodes(samples: Sequence[Mapping[str, Any]], owner: int) -> list[dict[str, int]]:
    result: list[dict[str, int]] = []
    active: int | None = None
    for sample in samples:
        players = sample.get("players")
        if not isinstance(players, list) or owner >= len(players) or not isinstance(players[owner], Mapping):
            raise ValueError("sample lacks indexed player controller state")
        player = players[owner]
        tick = sample.get("tick")
        opcode = player.get("controller_opcode")
        argument = player.get("controller_argument")
        if not isinstance(tick, int) or not isinstance(opcode, int) or not isinstance(argument, int):
            raise ValueError("controller sample fields are not integers")
        if opcode and active != opcode:
            result.append({"tick": tick, "opcode": opcode, "argument": argument})
            active = opcode
        elif not opcode:
            active = None
    return result


def compare(first: Mapping[str, Any], second: Mapping[str, Any], tick_tolerance: int = 3) -> dict[str, Any]:
    first_samples = first.get("g4_ai_smoke", {}).get("samples", [])
    second_samples = second.get("g4_ai_smoke", {}).get("samples", [])
    owners: dict[str, Any] = {}
    passed = True
    for owner in (0, 1):
        left = episodes(first_samples, owner)
        right = episodes(second_samples, owner)
        left_events = [(item["opcode"], item["argument"]) for item in left]
        right_events = [(item["opcode"], item["argument"]) for item in right]
        tick_deltas = [right_item["tick"] - left_item["tick"]
                       for left_item, right_item in zip(left, right, strict=False)]
        owner_pass = (
            left_events == right_events
            and len(left) == len(right)
            and all(abs(delta) <= tick_tolerance for delta in tick_deltas)
        )
        passed = passed and owner_pass
        owners[str(owner)] = {
            "pass": owner_pass,
            "first": left,
            "second": right,
            "event_sequence_equal": left_events == right_events,
            "tick_deltas": tick_deltas,
            "max_abs_tick_delta": max((abs(delta) for delta in tick_deltas), default=0),
        }
    return {
        "schema": "syw2plus.g4.controller_trace_compare.v1",
        "classification": "CONTROLLER_TRACE_REPEATABLE" if passed else "CONTROLLER_TRACE_DRIFT",
        "pass": passed,
        "tick_tolerance": tick_tolerance,
        "owners": owners,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("first", type=Path)
    parser.add_argument("second", type=Path)
    parser.add_argument("--tick-tolerance", type=int, default=3)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = compare(json.loads(args.first.read_text()), json.loads(args.second.read_text()), args.tick_tolerance)
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered)
    else:
        print(rendered, end="")
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
