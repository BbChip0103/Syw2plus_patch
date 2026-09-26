#!/usr/bin/env python3
"""Hash-guarded fixed-5000 experiment. Create a new EXE copy; never patch the input.

Evidence: analysis/memory_maps/population_5000_runtime_0910.md.
Restore only accepts our exact patched bytes and exact original backup.
"""

from __future__ import annotations
import argparse
import hashlib
from pathlib import Path

ORIGINAL_SHA256 = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"
# Exact-hash profile: these .text file offsets are VA - 0x400000.
EDITS = (
    (0x1B576, bytes.fromhex("66c700dc05"), bytes.fromhex("66c7008813")),
    (0x3FFD4, bytes.fromhex("05dc050000"), bytes.fromhex("b888130000")),
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def patched_bytes(original: bytes) -> bytes:
    if digest(original) != ORIGINAL_SHA256:
        raise ValueError("Unsupported original EXE SHA256")
    result = bytearray(original)
    for offset, before, after in EDITS:
        if result[offset : offset + len(before)] != before or len(before) != len(after):
            raise ValueError("Unexpected instruction bytes/length")
        result[offset : offset + len(before)] = after
    return bytes(result)


def create_copy(source: Path, destination: Path) -> str:
    if source.resolve() == destination.resolve():
        raise ValueError("Refusing to modify the input EXE")
    original = source.read_bytes()
    patched = patched_bytes(original)
    backup = Path(str(destination) + ".original")
    # Exclusive creation prevents overwriting any existing game or backup.
    with backup.open("xb") as stream:
        stream.write(original)
    try:
        with destination.open("xb") as stream:
            stream.write(patched)
    except BaseException:
        backup.unlink()  # Only the new backup created by this invocation.
        raise
    return digest(patched)


def restore(destination: Path) -> str:
    backup = Path(str(destination) + ".original")
    original = backup.read_bytes()
    expected = patched_bytes(original)
    if destination.read_bytes() != expected:
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
