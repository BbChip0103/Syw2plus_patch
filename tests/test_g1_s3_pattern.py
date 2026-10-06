"""Regression contracts for the opt-in G1 S3 resource pattern proof."""

from __future__ import annotations

import json
from pathlib import Path

from tools.g1_s3_probe import validate_s3_trace


ROOT = Path(__file__).resolve().parents[1]


def _present(*, marked: bool) -> dict[str, object]:
    return {
        "event": "mirror2x_present",
        "success": 1,
        "fallback": 0,
        "source_width": 800,
        "source_height": 600,
        "destination_width": 1600,
        "destination_height": 1200,
        "source_identity": "0x1",
        "destination_identity": "0x2",
        "source_rect": {"left": 0, "top": 0, "right": 800, "bottom": 600},
        "destination_rect": {"left": 0, "top": 0, "right": 1600, "bottom": 1200},
        "source_hash_fnv1a32": "0x1",
        "destination_hash_fnv1a32": "0x2",
        "source_dump_hex": "00",
        "destination_dump_hex": "0000",
        "nearest_matches": 1 if marked else 1920000,
        "nearest_total": 1920000,
        "same_frame_oracle": 0 if marked else 1,
        "covered_pixels": 315 if marked else 10,
        "stale_pixels": 0,
        "elapsed_ms": 1,
        "primitive_reinvoke_elapsed_ms_total": 1,
        "primitive_reinvoke_elapsed_ms_max": 1,
        "primitive_reinvoke_count": 2,
        "primitive_install_success": 1,
        "primitive_call_count": 2,
    }


def test_s3_trace_waives_only_the_marked_pattern_oracle(tmp_path: Path) -> None:
    events = []
    for state in (3, 5, 7, 9):
        events.extend([
            {"event": "blt", "program_state": state, "destination_is_primary": 1, "converted": 1},
            _present(marked=False),
        ])
    events.extend([
        {"event": "s3_pattern", "sprite_id": 0x24, "frame": 0,
         "x": 10, "y": 3, "width": 20, "height": 24, "pattern_pixels": 315},
        {"event": "mirror2x_metrics", "s3_pattern_applied": 1, "s3_pattern_pixels": 315},
        {"event": "summary"},
    ])
    path = tmp_path / "trace.jsonl"
    path.write_text("\n".join(json.dumps(item) for item in events) + "\n", encoding="utf-8")
    verdict = validate_s3_trace(path)
    assert verdict["status"] == "PASS"
    assert verdict["sprite"] == {
        "id": 0x24, "frame": 0, "logical_origin": [10, 3], "dimensions": [20, 24],
    }


def test_s3_trace_rejects_unmarked_or_multiple_pattern_presents(tmp_path: Path) -> None:
    events = [
        {"event": "blt", "program_state": 3, "destination_is_primary": 1, "converted": 1},
        _present(marked=False),
        {"event": "summary"},
    ]
    path = tmp_path / "trace.jsonl"
    path.write_text("\n".join(json.dumps(item) for item in events) + "\n", encoding="utf-8")
    verdict = validate_s3_trace(path)
    assert verdict["status"] == "BLOCKED"
    assert any("marked S3 present" in error for error in verdict["errors"])


def test_s3_bridge_is_opt_in_and_pins_resource_target() -> None:
    source = (ROOT / "tools/inmm_stub/g1_mirror2x.c").read_text(encoding="utf-8")
    assert 'G1_S3_PATTERN_ENV "SYW2_G1_S3_PATTERN"' in source
    assert "x == 10u && y == 3u && width == 20u && height == 24u" in source
    assert "g_s3_pattern_applied" in source
    assert "base ^ 0x03u" in source
    assert "s3_overlay_destination" in source
