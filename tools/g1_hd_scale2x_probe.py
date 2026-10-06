"""Validate the bounded P3 palette-index Scale2x trace contract."""

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


def validate_trace(path: Path) -> dict[str, Any]:
    errors: list[str] = []
    try:
        events = _events(path)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        return {"status": "BLOCKED", "errors": [f"trace unreadable: {exc}"]}
    mirror = [row for row in events if row.get("event") == "mirror2x_present"]
    records = [row for row in mirror if row.get("hd_source") == "scale2x"]
    if not mirror:
        errors.append("no mirror2x_present records")
    if len(records) != len(mirror):
        errors.append("one or more present records did not use scale2x source")
    required = (
        "nearest_matches", "nearest_total", "hd_mask_inside_diff_subpixels",
        "hd_mask_outside_diff_subpixels", "covered_pixels", "stale_pixels",
        "scale2x_blocks",
        "scale2x_subpixel_differences", "scale2x_palette_violations",
        "identity_keys", "identity_invalid_sources", "identity_lookup_misses",
        "elapsed_ms",
    )
    inside_diffs = 0
    subpixel_diffs = 0
    palette_violations = 0
    outside_diffs = 0
    for index, row in enumerate(records):
        if row.get("success") != 1:
            errors.append(f"scale2x record {index} did not complete successfully")
        row_valid = True
        for field in required:
            if not isinstance(row.get(field), int) or row[field] < 0:
                errors.append(f"scale2x record {index} has invalid {field}")
                row_valid = False
        if row_valid and row["nearest_total"] <= 0:
            errors.append(f"scale2x record {index} has no nearest denominator")
            row_valid = False
        if row_valid and row["nearest_matches"] > row["nearest_total"]:
            errors.append(f"scale2x record {index} has more nearest matches than samples")
            row_valid = False
        if row_valid:
            covered = row["covered_pixels"]
            stale = row["stale_pixels"]
            inside = row["hd_mask_inside_diff_subpixels"]
            if stale > covered:
                errors.append(
                    f"scale2x record {index} violates V1: covered_pixels={covered}, "
                    f"stale_pixels={stale}, inside={inside}"
                )
                row_valid = False
            elif inside > 2 * (covered - stale):
                errors.append(
                    f"scale2x record {index} violates V1: covered_pixels={covered}, "
                    f"stale_pixels={stale}, inside={inside}"
                )
                row_valid = False
        if row.get("identity_invalid_sources") != 0:
            errors.append(f"scale2x record {index} rejected an input source")
        if row.get("identity_lookup_misses") != 0:
            errors.append(f"scale2x record {index} missed a key-bound lookup")
        if not row_valid:
            continue
        if row_valid:
            deficit = row["nearest_total"] - row["nearest_matches"]
            inside = row["hd_mask_inside_diff_subpixels"]
            if inside * 4 < deficit or inside > deficit:
                errors.append(
                    f"scale2x record {index} has inside differences outside "
                    f"the nearest-deficit bounds: deficit={deficit}, inside={inside}"
                )
        inside_diffs += row.get("hd_mask_inside_diff_subpixels", 0)
        outside_diffs += row.get("hd_mask_outside_diff_subpixels", 0)
        subpixel_diffs = max(subpixel_diffs, row.get("scale2x_subpixel_differences", 0))
        palette_violations = max(palette_violations, row.get("scale2x_palette_violations", 0))
    if not records:
        errors.append("no scale2x present records")
    if outside_diffs != 0:
        errors.append(f"nearest differences escaped the HD mask: {outside_diffs}")
    if inside_diffs <= 0 or subpixel_diffs <= 0:
        errors.append("no scale2x subpixel difference was observed inside the mask")
    if palette_violations != 0:
        errors.append(f"scale2x emitted {palette_violations} non-source palette indices")
    if max((row.get("scale2x_blocks", 0) for row in records), default=0) <= 0:
        errors.append("scale2x generated no asset blocks")
    return {
        "status": "PASS" if not errors else "BLOCKED",
        "errors": errors,
        "trace_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "mirror_present_count": len(mirror),
        "scale2x_present_count": len(records),
        "hd_mask_inside_diff_subpixels_total": inside_diffs,
        "hd_mask_outside_diff_subpixels_total": outside_diffs,
        "scale2x_subpixel_differences_max": subpixel_diffs,
        "scale2x_palette_violations_max": palette_violations,
        "scale2x_blocks_max": max((row.get("scale2x_blocks", 0) for row in records), default=0),
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--trace", type=Path, required=True)
    args = parser.parse_args()
    result = validate_trace(args.trace)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["status"] == "PASS" else 2)
