#!/usr/bin/env python3
"""Offline owner-roster count experiment composed with the fixed-supply patch.

This is an evidence-only, private-copy transformation.  It changes the one
normal-new-game owner-count seed from 250 to 1200 after applying the existing
``fixed_supply_5000`` utility; it does not change Unit storage or any runtime
consumer.  All broader mode/reset/save/LAN contracts remain unproven.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

try:
    from patches.population.fixed_supply_5000 import patched_bytes as fixed_supply_bytes
except ModuleNotFoundError:  # direct absolute-path CLI invocation
    import importlib.util

    _spec = importlib.util.spec_from_file_location(
        "fixed_supply_5000", Path(__file__).with_name("fixed_supply_5000.py")
    )
    if _spec is None or _spec.loader is None:
        raise ImportError("fixed_supply_5000 utility is unavailable")
    _module = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_module)
    fixed_supply_bytes = _module.patched_bytes


ORIGINAL_SHA256 = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"
IMAGE_BASE = 0x00400000
OWNER_COUNT_VA = 0x0041B56D
OWNER_COUNT_FILE_OFFSET = OWNER_COUNT_VA - IMAGE_BASE + 1
OWNER_COUNT_BEFORE = bytes.fromhex("fa000000")
OWNER_COUNT_AFTER = bytes.fromhex("b0040000")
OWNER_COUNT_ORIGINAL = 250
OWNER_COUNT_POLICY = 1200
CPU_BUILD_THRESHOLD_ORIGINAL = 50
CPU_BUILD_THRESHOLD_POLICY = 240
NORMAL_MAP_WIDTH = 100
NORMAL_MAP_HEIGHT = 100
NORMAL_MAP_LIVENESS_CALL_VA = 0x00451130
NORMAL_MAP_LIVENESS_RETURN_VA = 0x004513B0
NORMAL_MAP_LIVENESS_EDX_RESTORED = True


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def patched_bytes(original: bytes) -> bytes:
    """Apply fixed supply first, then the single owner-count immediate."""
    if digest(original) != ORIGINAL_SHA256:
        raise ValueError("Unsupported original EXE SHA256")
    result = bytearray(fixed_supply_bytes(original))
    if result[OWNER_COUNT_FILE_OFFSET : OWNER_COUNT_FILE_OFFSET + 4] != OWNER_COUNT_BEFORE:
        raise ValueError("Unexpected owner-count instruction bytes")
    result[OWNER_COUNT_FILE_OFFSET : OWNER_COUNT_FILE_OFFSET + 4] = OWNER_COUNT_AFTER
    return bytes(result)


def create_copy(source: Path, destination: Path) -> str:
    if source.resolve() == destination.resolve():
        raise ValueError("Refusing to modify the input EXE")
    original = source.read_bytes()
    patched = patched_bytes(original)
    backup = Path(str(destination) + ".original")
    with backup.open("xb") as stream:
        stream.write(original)
    try:
        with destination.open("xb") as stream:
            stream.write(patched)
    except BaseException:
        backup.unlink()
        raise
    return digest(patched)


def restore(destination: Path) -> str:
    backup = Path(str(destination) + ".original")
    original = backup.read_bytes()
    if destination.read_bytes() != patched_bytes(original):
        raise ValueError("Refusing restore: destination is not the exact experimental patch")
    destination.write_bytes(original)
    return digest(original)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create-copy")
    create.add_argument("source", type=Path)
    create.add_argument("destination", type=Path)
    undo = commands.add_parser("restore")
    undo.add_argument("destination", type=Path)
    args = parser.parse_args()
    print(
        create_copy(args.source, args.destination)
        if args.command == "create-copy"
        else restore(args.destination)
    )


if __name__ == "__main__":
    main()
