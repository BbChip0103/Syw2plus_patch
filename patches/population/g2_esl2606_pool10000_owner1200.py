#!/usr/bin/env python3
"""Compose a diagnostic G2 storage patch with either exact ESL 2606 variant.

The ESL executables are not the pinned stock binary.  Build the known stock
capacity/persistence patch first, then replay the *verified* ESL delta.  Three
instruction-level collisions have explicit handling below.  This deliberately
does not adopt the stock candidate's fixed-5000 supply policy or F4 ledger.

Do not release the 10,000-slot result: the original command wire format packs
the unit slot in 12 bits. Slots 4096 and above select/render but cannot obey
normal movement or production commands. ``create_copy`` fails closed until a
separate, validated command-format repair exists.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import struct
from pathlib import Path
from typing import Any

from patches.population.fixed_owner_count_1200 import (
    OWNER_COUNT_AFTER,
    OWNER_COUNT_FILE_OFFSET,
)
from patches.population.fixed_supply_5000 import EDITS as FIXED_SUPPLY_EDITS
from patches.population.full_tail_relocation_storage_layout_v1 import (
    ORIGINAL_SHA256,
    layout,
)
from patches.population.g2_full_capacity_persistence_compat_v1 import (
    build_candidate as build_stock_candidate,
)

CAPACITY = 10001  # slot zero is reserved: 10,000 usable slots
MAX_PACKED_COMMAND_SLOT = 0x0FFF
REFERENCE_SHA256 = {
    "4a03895d8e6690080714fab7e851c3a0e9d44b7cac47fed78fc21a2f5210c6f8": "2606",
    "daf0b6a07f01d04397018924f9dd0c6ff414148c0547adc2d5c9e0b403a58523": "2606_fixed_start",
}

# Verified against both exact SHA-pinned ESL files.  At 0x47BA0F the ESL code
# NOPs a stock UnitStruct test.  At 0x47E51A it adds a segment prefix and
# changes the immediate; the UnitStruct absolute operand consequently moves
# one byte.  No other ESL delta intersects the G2 capacity patch.
NOP_TEST_OFFSET = 0x7BA0F
NOP_TEST_STOCK = bytes.fromhex("f68668b9660002750c")
NOP_TEST_ESL = b"\x90" * 9
PREFIXED_WRITE_OFFSET = 0x7E51A
PREFIXED_WRITE_STOCK = bytes.fromhex("c704cd90b9660064000000")
PREFIXED_WRITE_ESL = bytes.fromhex("3ec704cd90b9660020030000")
PREFIXED_WRITE_ADDRESS_OFFSET = PREFIXED_WRITE_OFFSET + 4
PREFIXED_WRITE_OLD_ADDRESS = 0x0066B990

# ESL2606-only repair: FUN_004A39CE addresses the active-list base/count
# through EBX-relative displacements from the stock bulk-state base.  Keep
# this out of the historical stock composer; these are exact, non-overlapping
# instruction bytes from the pinned executable and are applied only below.
ACTIVE_BULK_BASE = 0x00892410
ACTIVE_BULK_RELATIVE_SITES = {
    0x004A39DA: ("count", bytes.fromhex("6639bbf8340e00")),
    0x004A39E6: ("base", bytes.fromhex("668bb453982b0e00")),
    0x004A3A1B: ("count", bytes.fromhex("663bbbf8340e00")),
}


def apply_active_bulk_relative_fixups(candidate: bytearray, capacity: int) -> dict[str, int]:
    """Patch the three ESL active-list EBX-relative operands in-place."""
    active = layout(capacity).regions[5]
    values = {
        "base": active.new_start - ACTIVE_BULK_BASE,
        "count": active.new_start + active.array_new_span - ACTIVE_BULK_BASE,
    }
    patched: dict[str, int] = {}
    for va, (kind, old_bytes) in ACTIVE_BULK_RELATIVE_SITES.items():
        offset = va - 0x00400000
        actual = bytes(candidate[offset : offset + len(old_bytes)])
        if actual != old_bytes:
            raise ValueError(
                f"active bulk site 0x{va:08x}: old bytes mismatch "
                f"(expected {old_bytes.hex()}, found {actual.hex()})"
            )
        new_value = values[kind] & 0xFFFFFFFF
        struct.pack_into("<I", candidate, offset + len(old_bytes) - 4, new_value)
        patched[f"0x{va:08x}"] = new_value
    return patched


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_candidate(
    reference: bytes, stock: bytes, capacity: int = CAPACITY
) -> tuple[bytes, dict[str, Any]]:
    variant_sha = digest(reference)
    if variant_sha not in REFERENCE_SHA256:
        raise ValueError("unsupported ESL 2606 reference SHA256")
    if digest(stock) != ORIGINAL_SHA256:
        raise ValueError("pinned stock EXE SHA256 mismatch")
    if len(reference) != len(stock):
        raise ValueError("ESL/stock lengths differ")
    if stock[NOP_TEST_OFFSET : NOP_TEST_OFFSET + 9] != NOP_TEST_STOCK:
        raise ValueError("stock NOP-test old bytes mismatch")
    if reference[NOP_TEST_OFFSET : NOP_TEST_OFFSET + 9] != NOP_TEST_ESL:
        raise ValueError("ESL NOP-test bytes mismatch")
    if stock[PREFIXED_WRITE_OFFSET : PREFIXED_WRITE_OFFSET + 11] != PREFIXED_WRITE_STOCK:
        raise ValueError("stock unit-write old bytes mismatch")
    if reference[PREFIXED_WRITE_OFFSET : PREFIXED_WRITE_OFFSET + 12] != PREFIXED_WRITE_ESL:
        raise ValueError("ESL prefixed unit-write bytes mismatch")

    stock_candidate, stock_report = build_stock_candidate(stock, capacity)
    changed_by_g2 = {i for i, (old, new) in enumerate(zip(stock, stock_candidate)) if old != new}
    changed_by_esl = {i for i, (old, new) in enumerate(zip(stock, reference)) if old != new}
    supply_spans = {
        i for offset, before, _after in FIXED_SUPPLY_EDITS
        for i in range(offset, offset + len(before))
    }
    allowed_collision = (
        supply_spans
        | set(range(NOP_TEST_OFFSET, NOP_TEST_OFFSET + len(NOP_TEST_ESL)))
        | set(range(PREFIXED_WRITE_OFFSET, PREFIXED_WRITE_OFFSET + len(PREFIXED_WRITE_ESL)))
    )
    unexpected = (changed_by_g2 & changed_by_esl) - allowed_collision
    if unexpected:
        raise ValueError(f"unclassified ESL/G2 byte collision at 0x{min(unexpected):x}")

    result = bytearray(stock_candidate)
    for offset in changed_by_esl:
        if offset not in allowed_collision:
            result[offset] = reference[offset]

    # Preserve the complete original 1600+200*hero instructions, including
    # bytes equal to stock that the fixed-5000 patch would otherwise replace.
    for offset, before, after in FIXED_SUPPLY_EDITS:
        if stock[offset : offset + len(before)] != before:
            raise ValueError(f"stock supply old bytes mismatch at 0x{offset:x}")
        if stock_candidate[offset : offset + len(after)] != after:
            raise ValueError(f"fixed-supply candidate mismatch at 0x{offset:x}")
        result[offset : offset + len(before)] = reference[offset : offset + len(before)]

    result[NOP_TEST_OFFSET : NOP_TEST_OFFSET + len(NOP_TEST_ESL)] = NOP_TEST_ESL
    result[PREFIXED_WRITE_OFFSET : PREFIXED_WRITE_OFFSET + len(PREFIXED_WRITE_ESL)] = (
        PREFIXED_WRITE_ESL
    )
    new_unit_address = layout(capacity).regions[0].new_start + (
        PREFIXED_WRITE_OLD_ADDRESS - layout(1200).regions[0].old_start
    )
    struct.pack_into("<I", result, PREFIXED_WRITE_ADDRESS_OFFSET, new_unit_address)
    active_bulk_fixups = apply_active_bulk_relative_fixups(result, capacity)

    if result[OWNER_COUNT_FILE_OFFSET : OWNER_COUNT_FILE_OFFSET + 4] != OWNER_COUNT_AFTER:
        raise ValueError("owner count is not 1200")
    for offset, before, _after in FIXED_SUPPLY_EDITS:
        if result[offset : offset + len(before)] != reference[offset : offset + len(before)]:
            raise ValueError("ESL supply policy was not preserved")
    candidate = bytes(result)
    return candidate, {
        "variant": REFERENCE_SHA256[variant_sha],
        "reference_sha256": variant_sha,
        "stock_sha256": ORIGINAL_SHA256,
        "candidate_sha256": digest(candidate),
        "capacity_slots": capacity,
        "usable_slots": capacity - 1,
        "max_packed_command_slot": MAX_PACKED_COMMAND_SLOT,
        "release_status": (
            "BLOCKED_12_BIT_COMMAND_SLOT"
            if capacity - 1 > MAX_PACKED_COMMAND_SLOT
            else "RUNTIME_UNVERIFIED"
        ),
        "owner_count_cap": 1200,
        "supply_policy": "1600+200*living_heroes (up to 7 = 3000)",
        "stock_patch_sha256": stock_report["candidate_sha256"],
        "esl_delta_bytes": len(changed_by_esl),
        "g2_delta_bytes": len(changed_by_g2),
        "classified_collision_bytes": len(changed_by_g2 & changed_by_esl),
        "prefixed_unit_address": f"0x{new_unit_address:08x}",
        "active_bulk_relative_fixups": active_bulk_fixups,
    }


def create_copy(source: Path, stock_path: Path, destination: Path) -> dict[str, Any]:
    source_real = source.resolve()
    destination_real = destination.resolve()
    if source_real == destination_real or destination_real.is_relative_to(source_real.parent):
        raise ValueError("refusing to write in the reference EXE directory")
    if CAPACITY - 1 > MAX_PACKED_COMMAND_SLOT:
        raise ValueError(
            "12-bit command slot encoding supports at most slot 4095; "
            "10,000-slot candidate is unplayable and release is blocked"
        )
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
    backup = Path(str(destination) + ".original")
    reference = backup.read_bytes()
    expected, _report = build_candidate(reference, stock_path.read_bytes())
    if destination.read_bytes() != expected:
        raise ValueError("destination is not the exact candidate; refusing restore")
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
