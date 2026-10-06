"""Validate the W60 live present records without changing the legacy gate.

The bridge emits one ``mirror2x_present`` record after each eligible primary
present.  This probe deliberately consumes those bounded records directly so
that a missing final summary or an input-stage failure cannot turn absent
metrics into a zero-valued PASS.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


REQUIRED_PROGRAM_STATES = (3, 5, 7, 9)


def _events(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"line {line_number} is not an object")
        rows.append(value)
    return rows


def _ratio(matches: Any, total: Any) -> float | None:
    if not isinstance(matches, int) or not isinstance(total, int) or total <= 0:
        return None
    return matches / total


def validate_native2x_control(trace_path: Path) -> dict[str, Any]:
    """Validate the native-2x, mirror-OFF paired control trace.

    This control deliberately does not claim W60 mirror correctness.  It
    proves the same native 1600x1200 surface/intervention is alive while the
    mirror event stream is absent, so raw input/fixture evidence can be paired
    with the mirror-ON run.
    """

    errors: list[str] = []
    try:
        events = _events(trace_path)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        return {"status": "BLOCKED", "errors": [f"trace unreadable: {exc}"]}
    summary = next((event for event in reversed(events) if event.get("event") == "summary"), None)
    if summary is None or events[-1].get("event") != "summary":
        errors.append("control trace has no final summary")
    else:
        if summary.get("dropped_count") != 0 or summary.get("aggregate_output_dropped_count") != 0:
            errors.append("control trace dropped records")
        if summary.get("event_count") != len(events) - 1:
            errors.append("control summary event_count does not match raw event count")
    if any(event.get("event") == "mirror2x_present" for event in events):
        errors.append("control trace unexpectedly contains mirror2x_present records")
    primary_creates = [
        event for event in events
        if event.get("event") == "create_surface"
        and isinstance(event.get("descriptor"), dict)
        and event["descriptor"].get("flags") == 33
        and event["descriptor"].get("backbuffer_count") == 1
    ]
    if not primary_creates:
        errors.append("control trace has no primary surface creation")
    else:
        primary = primary_creates[-1].get("returned_surface")
        descriptors = [
            event for event in events
            if event.get("event") == "get_surface_desc" and event.get("surface") == primary
        ]
        actual = descriptors[-1].get("actual_desc") if descriptors else None
        if not isinstance(actual, dict) or [actual.get("width"), actual.get("height")] != [1600, 1200]:
            errors.append("control trace primary surface is not 1600x1200")
    return {
        "status": "PASS" if not errors else "BLOCKED",
        "errors": errors,
        "trace_sha256": hashlib.sha256(trace_path.read_bytes()).hexdigest(),
        "event_count": len(events),
        "mirror_present_count": sum(event.get("event") == "mirror2x_present" for event in events),
        "same_frame_metrics": False,
    }


def validate_trace(
    trace_path: Path, *, threshold: float = 0.999,
    required_states: Iterable[int] = REQUIRED_PROGRAM_STATES,
) -> dict[str, Any]:
    """Return a conservative W60 verdict from one completed raw JSONL trace."""

    errors: list[str] = []
    try:
        events = _events(trace_path)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        return {"status": "BLOCKED", "errors": [f"trace unreadable: {exc}"]}
    presents = [
        event for event in events
        if event.get("event") in {"blt", "blt_fast"}
        and event.get("destination_is_primary") == 1
    ]
    converted = [event for event in presents if event.get("converted") == 1]
    mirror = [event for event in events if event.get("event") == "mirror2x_present"]
    converted_states = sorted({
        state for event in converted
        if isinstance((state := event.get("program_state")), int)
    })
    required = list(required_states)
    missing_states = [state for state in required if state not in converted_states]
    if missing_states:
        errors.append(f"converted primary present missing program states: {missing_states}")
    if not mirror:
        errors.append("no live mirror2x_present records")

    oracle_ratios: list[float] = []
    covered = 0
    primitive_calls = 0
    performance_samples = 0
    present_elapsed_ms: list[int] = []
    primitive_elapsed_ms_total: list[int] = []
    primitive_elapsed_ms_max: list[int] = []
    primitive_reinvoke_counts: list[int] = []
    for index, event in enumerate(mirror):
        if event.get("success") != 1:
            errors.append(f"mirror record {index} did not complete successfully")
        if event.get("fallback") != 0:
            errors.append(f"mirror record {index} used the fallback present path")
        if event.get("source_width") != 800 or event.get("source_height") != 600:
            errors.append(f"mirror record {index} has a non-800x600 source")
        if event.get("destination_width") != 1600 or event.get("destination_height") != 1200:
            errors.append(f"mirror record {index} has a non-1600x1200 destination")
        if not isinstance(event.get("source_identity"), str) or not isinstance(
            event.get("destination_identity"), str
        ):
            errors.append(f"mirror record {index} is missing surface identity provenance")
        if not isinstance(event.get("source_rect"), dict) or not isinstance(
            event.get("destination_rect"), dict
        ):
            errors.append(f"mirror record {index} is missing effective rect provenance")
        if not isinstance(event.get("source_hash_fnv1a32"), str) or not isinstance(
            event.get("destination_hash_fnv1a32"), str
        ):
            errors.append(f"mirror record {index} is missing source/present hashes")
        if not isinstance(event.get("source_dump_hex"), str) or not isinstance(
            event.get("destination_dump_hex"), str
        ):
            errors.append(f"mirror record {index} is missing bounded source/present dumps")
        ratio = _ratio(event.get("nearest_matches"), event.get("nearest_total"))
        if ratio is None:
            errors.append(f"mirror record {index} has no same-frame oracle denominator")
        else:
            oracle_ratios.append(ratio)
            if ratio < threshold or event.get("same_frame_oracle") != 1:
                errors.append(
                    f"mirror record {index} nearest oracle {ratio:.6f} is below {threshold:.6f}"
                )
        if isinstance(event.get("covered_pixels"), int):
            covered = max(covered, event["covered_pixels"])
        if isinstance(event.get("primitive_call_count"), int):
            primitive_calls = max(primitive_calls, event["primitive_call_count"])
        for key, values in (
            ("elapsed_ms", present_elapsed_ms),
            ("primitive_reinvoke_elapsed_ms_total", primitive_elapsed_ms_total),
            ("primitive_reinvoke_elapsed_ms_max", primitive_elapsed_ms_max),
            ("primitive_reinvoke_count", primitive_reinvoke_counts),
        ):
            value = event.get(key)
            if not isinstance(value, int) or value < 0:
                errors.append(f"mirror record {index} has invalid {key}")
            else:
                values.append(value)
        if all(isinstance(event.get(key), int) for key in (
            "elapsed_ms", "primitive_reinvoke_elapsed_ms_total",
            "primitive_reinvoke_elapsed_ms_max", "primitive_reinvoke_count")):
            performance_samples += 1
        if event.get("primitive_install_success") != 1:
            errors.append(f"mirror record {index} lacks successful primitive installation evidence")

    summary = next((event for event in reversed(events) if event.get("event") == "summary"), None)
    if summary is None:
        errors.append("trace has no final summary; live metrics are not treated as finalized")
    if primitive_calls <= 0 or covered <= 0:
        errors.append("trace has no positive primitive coverage evidence")
    if performance_samples != len(mirror):
        errors.append("trace is missing complete primitive/present performance evidence")
    return {
        "status": "PASS" if not errors else "BLOCKED",
        "errors": errors,
        "trace_sha256": hashlib.sha256(trace_path.read_bytes()).hexdigest(),
        "event_count": len(events),
        "primary_present_count": len(presents),
        "converted_present_count": len(converted),
        "converted_program_states": converted_states,
        "required_program_states": required,
        "mirror_present_count": len(mirror),
        "primitive_call_count": primitive_calls,
        "covered_pixels_max": covered,
        "performance_samples": performance_samples,
        "present_elapsed_ms_max": max(present_elapsed_ms) if present_elapsed_ms else None,
        "primitive_reinvoke_elapsed_ms_total_max": max(primitive_elapsed_ms_total)
        if primitive_elapsed_ms_total else None,
        "primitive_reinvoke_elapsed_ms_max": max(primitive_elapsed_ms_max)
        if primitive_elapsed_ms_max else None,
        "primitive_reinvoke_count_max": max(primitive_reinvoke_counts)
        if primitive_reinvoke_counts else None,
        "nearest_oracle_min": min(oracle_ratios) if oracle_ratios else None,
        "same_frame_metrics": bool(mirror),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--threshold", type=float, default=0.999)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    verdict = validate_trace(args.trace, threshold=args.threshold)
    payload = json.dumps(verdict, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if verdict["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
