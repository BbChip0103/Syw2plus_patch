#!/usr/bin/env python3
"""Verify a frozen expanded-pool save/load evidence bundle offline."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct
from typing import Any


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_bundle(
    run_dir: Path,
    *,
    capacity: int = 4001,
    sidecar_name: str = "frozen4000_sidecars.bin",
    save_name: str = "save097.dat",
    snapshot_name: str = "frozen4000_snapshot.json",
) -> dict[str, Any]:
    sidecar = (run_dir / sidecar_name).read_bytes()
    save = (run_dir / save_name).read_bytes()
    snapshot = json.loads((run_dir / snapshot_name).read_text())
    expected_size = capacity * 14 + 6
    if len(sidecar) != expected_size:
        raise ValueError(f"sidecar size {len(sidecar)} != {expected_size}")

    offset = 0

    def words(count: int) -> tuple[int, ...]:
        nonlocal offset
        values = struct.unpack_from(f"<{count}H", sidecar, offset)
        offset += count * 2
        return values

    existence = words(capacity)
    words(capacity)  # ages participate in the byte-exact check below
    category_a = words(capacity * 2 + 1)
    category_b = words(capacity * 2 + 1)
    active = words(capacity + 1)
    assert offset == len(sidecar)

    live = {slot for slot, value in enumerate(existence) if value}
    active_count = active[-1]
    if active_count > capacity:
        active_slots: tuple[int, ...] = ()
    else:
        active_slots = active[:active_count]
    active_set = set(active_slots)
    units = snapshot.get("state", snapshot).get("units", [])
    save_offsets: list[int] = []
    start = 0
    while True:
        found = save.find(sidecar, start)
        if found < 0:
            break
        save_offsets.append(found)
        start = found + 1

    checks = {
        "sidecar_size": len(sidecar) == expected_size,
        "snapshot_count": len(units) == len(live),
        "category_a_count": category_a[-1] <= capacity,
        "category_b_count": category_b[-1] == len(live),
        "active_count": active_count == len(live),
        "active_unique": len(active_set) == active_count,
        "active_exact": active_set == live,
        "serialized_once": len(save_offsets) == 1,
        "serialized_bytes_exact": bool(save_offsets)
        and save[save_offsets[0] : save_offsets[0] + len(sidecar)] == sidecar,
    }
    return {
        "ok": all(checks.values()),
        "capacity": capacity,
        "live": len(live),
        "snapshot_units": len(units),
        "category_a_count": category_a[-1],
        "category_b_count": category_b[-1],
        "active_count": active_count,
        "active_unique": len(active_set),
        "missing": sorted(live - active_set),
        "unexpected": sorted(active_set - live),
        "save_size": len(save),
        "save_offsets": save_offsets,
        "sidecar_sha256": _sha256(sidecar),
        "serialized_sha256": (
            _sha256(save[save_offsets[0] : save_offsets[0] + len(sidecar)])
            if save_offsets
            else None
        ),
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--capacity", type=int, default=4001)
    args = parser.parse_args()
    report = verify_bundle(args.run_dir, capacity=args.capacity)
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
