#!/usr/bin/env python3
"""Compose the reviewed N=1210 tail-relocated pool with the fixed-5000 patch."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from patches.population.fixed_supply_5000 import EDITS
from patches.population.g2_unit_pool_expansion_v1 import build_candidate as build_pool_candidate


def build_candidate(original: bytes, capacity: int = 1210) -> tuple[bytes, dict[str, Any]]:
    pool_candidate, report = build_pool_candidate(original, capacity)
    out = bytearray(pool_candidate)
    applied: list[dict[str, object]] = []
    for offset, before, after in EDITS:
        if len(before) != len(after) or out[offset : offset + len(before)] != before:
            raise ValueError(f"fixed-supply compose preimage mismatch at 0x{offset:X}")
        out[offset : offset + len(before)] = after
        applied.append({"offset": offset, "before": before.hex(), "after": after.hex()})
    combined = bytes(out)
    return combined, {
        "capacity": capacity,
        "pool_report": report,
        "supply_edits": applied,
        "sha256": hashlib.sha256(combined).hexdigest(),
    }


def write_candidate(original_path: Path, destination: Path, capacity: int = 1210) -> dict[str, Any]:
    candidate, report = build_candidate(original_path.read_bytes(), capacity)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(candidate)
    return report
