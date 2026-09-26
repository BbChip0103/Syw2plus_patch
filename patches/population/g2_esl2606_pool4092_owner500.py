#!/usr/bin/env python3
"""Compose the pinned normal ESL 2606 variant for a 4092-slot unit pool.

The existing ESL composer remains the diagnostic 10,000-slot release and keeps
its fail-closed copy guard.  This thin composition selects the separately
validated 4093-slot geometry (slot zero is reserved), fixes the idle-hero
portrait's producer search to cover that geometry, then changes the
normal-new-game owner roster seed from 1200 to 500. It never mutates either
input executable and accepts only the exact normal ESL 2606 reference SHA.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any

from patches.population.fixed_owner_count_1200 import OWNER_COUNT_FILE_OFFSET
from patches.population.g2_esl2606_pool10000_owner1200 import (
    MAX_PACKED_COMMAND_SLOT,
    build_candidate as build_esl_candidate,
    digest,
)

CAPACITY = 4093  # slot zero is reserved: 4092 usable slots
USABLE_SLOTS = CAPACITY - 1
OWNER_COUNT_BEFORE_1200 = bytes.fromhex("b0040000")
OWNER_COUNT_AFTER_500 = bytes.fromhex("f4010000")
OWNER_COUNT_POLICY = 500
REFERENCE_SHA256 = "4a03895d8e6690080714fab7e851c3a0e9d44b7cac47fed78fc21a2f5210c6f8"

# FUN_004183A0, called from idle-hero portrait callback FUN_0049B9F0.
# The two modulo operands and traversal bound must agree.  New games can
# place the only producer at slot 4092, which the original 1200-slot walk
# never visits.  These are complete instruction preimages, not a broad search
# and replace of 0x4B0 constants used by unrelated game structures.
PRODUCER_LOOKUP_EDITS = (
    (0x004183A8, bytes.fromhex("b9b0040000"), bytes.fromhex("b9fd0f0000")),
    (0x004183BE, bytes.fromhex("b9b0040000"), bytes.fromhex("b9fd0f0000")),
    (0x00418425, bytes.fromhex("6681fbb004"), bytes.fromhex("6681fbfd0f")),
)


def apply_producer_lookup_fixups(image: bytearray) -> None:
    """Raise only the pinned portrait producer scan from 1200 to 4093 slots."""
    spans = [(va - 0x00400000, va - 0x00400000 + len(old)) for va, old, _ in PRODUCER_LOOKUP_EDITS]
    spans.append((OWNER_COUNT_FILE_OFFSET, OWNER_COUNT_FILE_OFFSET + len(OWNER_COUNT_BEFORE_1200)))
    if any(a0 < b1 and b0 < a1 for i, (a0, a1) in enumerate(spans) for b0, b1 in spans[i + 1 :]):
        raise ValueError("producer lookup edits overlap each other or owner-count edit")
    for va, old, new in PRODUCER_LOOKUP_EDITS:
        offset = va - 0x00400000
        if len(old) != len(new) or bytes(image[offset : offset + len(old)]) != old:
            raise ValueError(f"producer lookup 0x{va:08x} old bytes mismatch")
    for va, old, new in PRODUCER_LOOKUP_EDITS:
        offset = va - 0x00400000
        image[offset : offset + len(old)] = new


def build_candidate(reference: bytes, stock: bytes) -> tuple[bytes, dict[str, Any]]:
    """Build the normal ESL 2606 4093-slot/500-owner candidate.

    ``build_esl_candidate`` performs all pinned stock/ESL, collision, layout,
    active-list, and instruction preimage checks.  The owner edit is kept here
    as a separate exact-preimage composition so no production globals are
    monkey-patched and the historical 1200/10,000 composer is unchanged.
    """
    if digest(reference) != REFERENCE_SHA256:
        raise ValueError("unsupported ESL 2606 reference SHA256")
    candidate, report = build_esl_candidate(reference, stock, CAPACITY)
    out = bytearray(candidate)
    apply_producer_lookup_fixups(out)
    start = OWNER_COUNT_FILE_OFFSET
    end = start + len(OWNER_COUNT_BEFORE_1200)
    if out[start:end] != OWNER_COUNT_BEFORE_1200:
        raise ValueError(f"owner-count compose preimage mismatch at 0x{start:X}")
    out[start:end] = OWNER_COUNT_AFTER_500
    combined = bytes(out)
    final_report = dict(report)
    final_report.update(
        {
            "candidate_sha256": digest(combined),
            "capacity_slots": CAPACITY,
            "usable_slots": USABLE_SLOTS,
            "owner_count_cap": OWNER_COUNT_POLICY,
            "producer_lookup_capacity": CAPACITY,
            "producer_lookup_edits": {
                f"0x{va:08x}": {"before": old.hex(), "after": new.hex()}
                for va, old, new in PRODUCER_LOOKUP_EDITS
            },
            "owner_count_edit": {
                "offset": OWNER_COUNT_FILE_OFFSET,
                "before": OWNER_COUNT_BEFORE_1200.hex(),
                "after": OWNER_COUNT_AFTER_500.hex(),
            },
        }
    )
    return combined, final_report


def create_copy(source: Path, stock_path: Path, destination: Path) -> dict[str, Any]:
    """Create a candidate and exact original backup without overwriting inputs."""
    source_real = source.resolve()
    destination_real = destination.resolve()
    if source_real == destination_real or destination_real.is_relative_to(source_real.parent):
        raise ValueError("refusing to write in the reference EXE directory")
    if USABLE_SLOTS > MAX_PACKED_COMMAND_SLOT:
        raise ValueError("4092-slot candidate exceeds the 12-bit command slot limit")
    reference = source.read_bytes()
    candidate, report = build_candidate(reference, stock_path.read_bytes())
    destination.parent.mkdir(parents=True, exist_ok=True)
    backup = Path(str(destination) + ".original")
    with backup.open("xb") as stream:
        stream.write(reference)
    try:
        with destination.open("xb") as stream:
            stream.write(candidate)
    except BaseException:
        backup.unlink()
        raise
    return report


def restore_copy(destination: Path, stock_path: Path) -> str:
    """Restore only when destination is exactly this composition's candidate."""
    backup = Path(str(destination) + ".original")
    reference = backup.read_bytes()
    expected, _report = build_candidate(reference, stock_path.read_bytes())
    if destination.read_bytes() != expected:
        raise ValueError("refusing restore: destination is not the exact candidate")
    temporary = Path(str(destination) + ".restore.tmp")
    with temporary.open("xb") as stream:
        stream.write(reference)
    os.replace(temporary, destination)
    return digest(reference)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create-copy")
    create.add_argument("source", type=Path)
    create.add_argument("stock", type=Path)
    create.add_argument("destination", type=Path)
    restore = commands.add_parser("restore")
    restore.add_argument("destination", type=Path)
    restore.add_argument("stock", type=Path)
    args = parser.parse_args()
    if args.command == "create-copy":
        print(create_copy(args.source, args.stock, args.destination))
    else:
        print(restore_copy(args.destination, args.stock))


if __name__ == "__main__":
    main()
