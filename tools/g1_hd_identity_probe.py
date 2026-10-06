"""Validate the opt-in P2 identity asset ledger in a completed trace."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


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


def validate_trace(path: Path, *, threshold: float = 0.999) -> dict[str, Any]:
    errors: list[str] = []
    try:
        events = _events(path)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        return {"status": "BLOCKED", "errors": [f"trace unreadable: {exc}"]}
    mirror = [row for row in events if row.get("event") == "mirror2x_present"]
    if not mirror:
        errors.append("no mirror2x_present records")
    identity = [row for row in mirror if row.get("hd_source") == "identity"]
    if len(identity) != len(mirror):
        errors.append("one or more present records did not use identity source")
    ratios: list[float] = []
    for index, row in enumerate(identity):
        matches, total = row.get("nearest_matches"), row.get("nearest_total")
        if not isinstance(matches, int) or not isinstance(total, int) or total <= 0:
            errors.append(f"identity record {index} lacks nearest oracle")
        else:
            ratio = matches / total
            ratios.append(ratio)
            if ratio < threshold:
                errors.append(f"identity record {index} nearest ratio {ratio:.6f} < {threshold:.6f}")
        for field in ("identity_pixels", "identity_keys", "identity_invalid_sources", "identity_events",
                      "identity_lookup_hits", "identity_lookup_misses", "identity_cache_inserts",
                      "identity_cache_hits", "identity_cache_misses", "identity_cache_refreshes",
                      "identity_negative_lookup_attempts",
                      "identity_negative_lookup_misses", "identity_key_mismatches", "stale_pixels"):
            if not isinstance(row.get(field), int) or row[field] < 0:
                errors.append(f"identity record {index} has invalid {field}")
        if isinstance(row.get("identity_lookup_misses"), int) and row["identity_lookup_misses"] != 0:
            errors.append(f"identity record {index} has key lookup misses")
    max_pixels = max((row.get("identity_pixels", 0) for row in identity), default=0)
    max_keys = max((row.get("identity_keys", 0) for row in identity), default=0)
    max_events = max((row.get("identity_events", 0) for row in identity), default=0)
    max_invalid = max((row.get("identity_invalid_sources", 0) for row in identity), default=0)
    max_lookup_hits = max((row.get("identity_lookup_hits", 0) for row in identity), default=0)
    max_lookup_misses = max((row.get("identity_lookup_misses", 0) for row in identity), default=0)
    max_cache_inserts = max((row.get("identity_cache_inserts", 0) for row in identity), default=0)
    max_cache_hits = max((row.get("identity_cache_hits", 0) for row in identity), default=0)
    max_cache_misses = max((row.get("identity_cache_misses", 0) for row in identity), default=0)
    max_cache_refreshes = max((row.get("identity_cache_refreshes", 0) for row in identity), default=0)
    max_negative_lookup_attempts = max((row.get("identity_negative_lookup_attempts", 0) for row in identity), default=0)
    max_negative_lookup_misses = max((row.get("identity_negative_lookup_misses", 0) for row in identity), default=0)
    max_key_mismatches = max((row.get("identity_key_mismatches", 0) for row in identity), default=0)
    stale = sum(row.get("stale_pixels", 0) for row in identity if isinstance(row.get("stale_pixels"), int))
    if max_pixels <= 0:
        errors.append("identity ledger has no mapped pixels")
    if max_keys <= 0 or max_events <= 0:
        errors.append("identity ledger has no stable source keys/events")
    if max_invalid != 0:
        errors.append(f"identity ledger rejected {max_invalid} source samples")
    if max_lookup_hits <= 0:
        errors.append("identity output has no key-bound block lookups")
    if max_lookup_misses != 0:
        errors.append(f"identity output had {max_lookup_misses} key lookup misses")
    if max_cache_inserts <= 0 or max_cache_hits <= 0 or max_cache_misses <= 0:
        errors.append("identity output lacks cache insert/hit/miss evidence")
    if max_negative_lookup_misses <= 0:
        errors.append("identity output lacks altered-key lookup miss evidence")
    if max_negative_lookup_attempts <= 0:
        errors.append("identity output lacks altered-key lookup attempt evidence")
    if max_negative_lookup_misses > max_negative_lookup_attempts:
        errors.append("identity altered-key misses exceed lookup attempts")
    if max_key_mismatches <= 0:
        errors.append("identity output lacks negative key-mismatch evidence")
    if max_key_mismatches != max_negative_lookup_misses:
        errors.append("identity key-mismatch count is not backed by altered-key lookup misses")
    summary = next((row for row in reversed(events) if row.get("event") == "summary"), None)
    if summary is None:
        errors.append("trace has no final summary")
    return {
        "status": "PASS" if not errors else "BLOCKED",
        "errors": errors,
        "trace_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "mirror_present_count": len(mirror),
        "identity_present_count": len(identity),
        "nearest_oracle_min": min(ratios) if ratios else None,
        "identity_pixels_max": max_pixels,
        "identity_keys_max": max_keys,
        "identity_events_max": max_events,
        "identity_invalid_sources_max": max_invalid,
        "identity_lookup_hits_max": max_lookup_hits,
        "identity_lookup_misses_max": max_lookup_misses,
        "identity_cache_inserts_max": max_cache_inserts,
        "identity_cache_hits_max": max_cache_hits,
        "identity_cache_misses_max": max_cache_misses,
        "identity_cache_refreshes_max": max_cache_refreshes,
        "identity_negative_lookup_attempts_max": max_negative_lookup_attempts,
        "identity_negative_lookup_misses_max": max_negative_lookup_misses,
        "identity_key_mismatches_max": max_key_mismatches,
        "stale_pixels_total": stale,
        "same_frame_metrics": bool(identity),
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--threshold", type=float, default=0.999)
    args = parser.parse_args()
    result = validate_trace(args.trace, threshold=args.threshold)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 2)
