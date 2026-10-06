from __future__ import annotations

import json

from tools.g1_hd_scale2x_probe import validate_trace


def _trace_row(**overrides: int) -> dict[str, int | str]:
    row: dict[str, int | str] = {
        "event": "mirror2x_present",
        "hd_source": "scale2x",
        "success": 1,
        "nearest_matches": 98,
        "nearest_total": 100,
        "hd_mask_inside_diff_subpixels": 2,
        "hd_mask_outside_diff_subpixels": 0,
        "covered_pixels": 2,
        "stale_pixels": 1,
        "scale2x_blocks": 1,
        "scale2x_subpixel_differences": 2,
        "scale2x_palette_violations": 0,
        "identity_keys": 1,
        "identity_invalid_sources": 0,
        "identity_lookup_misses": 0,
        "elapsed_ms": 1,
    }
    row.update(overrides)
    return row


def _validate(tmp_path, row: dict[str, int | str]) -> dict[str, object]:
    trace = tmp_path / "trace.jsonl"
    trace.write_text(json.dumps(row) + "\n", encoding="utf-8")
    return validate_trace(trace)


def test_v1_accepts_inside_difference_at_exact_coverage_bound(tmp_path) -> None:
    result = _validate(tmp_path, _trace_row())

    assert result["status"] == "PASS", result["errors"]


def test_v1_rejects_inside_difference_above_coverage_bound(tmp_path) -> None:
    result = _validate(tmp_path, _trace_row(hd_mask_inside_diff_subpixels=3))

    assert result["status"] == "BLOCKED"
    assert any(
        "violates V1" in error
        and "covered_pixels=2" in error
        and "stale_pixels=1" in error
        and "inside=3" in error
        for error in result["errors"]
    )


def test_v1_rejects_stale_pixels_above_covered_pixels(tmp_path) -> None:
    result = _validate(tmp_path, _trace_row(covered_pixels=2, stale_pixels=3))

    assert result["status"] == "BLOCKED"
    assert any("violates V1" in error and "stale_pixels=3" in error
               for error in result["errors"])


def test_v1_rejects_missing_coverage_field(tmp_path) -> None:
    row = _trace_row()
    del row["covered_pixels"]
    result = _validate(tmp_path, row)

    assert result["status"] == "BLOCKED"
    assert any("invalid covered_pixels" in error for error in result["errors"])
