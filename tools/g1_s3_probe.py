"""Validate the opt-in G1 S3 resource-sprite pattern trace.

S3 intentionally breaks the nearest-neighbour oracle for one marked sprite.
The regular W60 validator remains strict; this validator only waives that
single, explicitly marked record and still requires the live primitive/present
evidence to be complete.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from tools.g1_mirror2x_probe import _events, validate_trace


RESOURCE_SPRITE_ID = 0x24
RESOURCE_FRAME = 0
RESOURCE_X = 10
RESOURCE_Y = 3
RESOURCE_WIDTH = 20
RESOURCE_HEIGHT = 24


def validate_s3_trace(trace_path: Path) -> dict[str, Any]:
    """Return a conservative verdict for one completed S3 raw trace."""

    base = validate_trace(trace_path)
    try:
        events = _events(trace_path)
    except (OSError, UnicodeDecodeError, ValueError):
        return {"status": "BLOCKED", "errors": ["trace unreadable"], **base}

    pattern_events = [event for event in events if event.get("event") == "s3_pattern"]
    errors = [
        error for error in base.get("errors", [])
        if "nearest oracle" not in error
    ]
    if len(pattern_events) != 1:
        errors.append(f"expected exactly one marked S3 present, got {len(pattern_events)}")
    else:
        event = pattern_events[0]
        if event.get("pattern_pixels", 0) <= 0:
            errors.append("S3 marked present has no covered pattern pixels")
        if event.get("sprite_id") != RESOURCE_SPRITE_ID or event.get("frame") != RESOURCE_FRAME:
            errors.append("S3 marked present lacks resource id 0x24 frame 0 identity")
        if [event.get("x"), event.get("y"), event.get("width"), event.get("height")] != [
                RESOURCE_X, RESOURCE_Y, RESOURCE_WIDTH, RESOURCE_HEIGHT,
            ]:
            errors.append("S3 marked present target geometry is not the resource frame contract")
    metrics = [event for event in events if event.get("event") == "mirror2x_metrics"]
    if not metrics or metrics[-1].get("s3_pattern_applied") != 1:
        errors.append("final mirror metrics do not confirm S3 pattern application")
    if metrics and metrics[-1].get("s3_pattern_pixels", 0) <= 0:
        errors.append("final mirror metrics report zero S3 pattern pixels")
    return {
        **base,
        "status": "PASS" if not errors else "BLOCKED",
        "errors": errors,
        "trace_sha256": hashlib.sha256(trace_path.read_bytes()).hexdigest(),
        "sprite": {
            "id": RESOURCE_SPRITE_ID,
            "frame": RESOURCE_FRAME,
            "logical_origin": [RESOURCE_X, RESOURCE_Y],
            "dimensions": [RESOURCE_WIDTH, RESOURCE_HEIGHT],
        },
        "pattern_present_count": len(pattern_events),
        "nearest_oracle_waiver": "one explicitly marked resource frame only",
    }
