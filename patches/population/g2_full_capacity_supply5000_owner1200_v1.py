#!/usr/bin/env python3
"""Compose the 4001-slot experiment with supply 5000 and owner cap 1200."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from patches.population.fixed_owner_count_1200 import (
    OWNER_COUNT_AFTER,
    OWNER_COUNT_BEFORE,
    OWNER_COUNT_FILE_OFFSET,
)
from patches.population.g2_full_unit_capacity_supply5000_v1 import (
    build_candidate as build_supply_capacity_candidate,
)


def build_candidate(original: bytes, capacity: int = 4001) -> tuple[bytes, dict[str, Any]]:
    candidate, report = build_supply_capacity_candidate(original, capacity)
    out = bytearray(candidate)
    start = OWNER_COUNT_FILE_OFFSET
    end = start + len(OWNER_COUNT_BEFORE)
    if out[start:end] != OWNER_COUNT_BEFORE:
        raise ValueError(f"owner-count compose preimage mismatch at 0x{start:X}")
    out[start:end] = OWNER_COUNT_AFTER
    combined = bytes(out)
    return combined, {
        "capacity": capacity,
        "capacity_supply_report": report,
        "owner_count_edit": {
            "offset": OWNER_COUNT_FILE_OFFSET,
            "before": OWNER_COUNT_BEFORE.hex(),
            "after": OWNER_COUNT_AFTER.hex(),
        },
        "sha256": hashlib.sha256(combined).hexdigest(),
    }


def write_candidate(original_path: Path, destination: Path, capacity: int = 4001) -> dict[str, Any]:
    candidate, report = build_candidate(original_path.read_bytes(), capacity)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(candidate)
    return report
