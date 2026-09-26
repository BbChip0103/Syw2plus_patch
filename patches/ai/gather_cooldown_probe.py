#!/usr/bin/env python3
"""Reversible private-copy probe: gather-intent cooldown 200 -> 100 ticks.

This measurement candidate changes one immediate in FUN_0043F5D0 case 3,
which selects opcode 0x03 and dispatches FUN_004B03D0 (gather-site cycling).
It never modifies the source input and is not a release patch.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

ORIGINAL_SHA256 = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"
EDIT_OFFSET = 0x3F8B6
BEFORE = bytes.fromhex("3dc8000000")
AFTER = bytes.fromhex("3d64000000")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def patched_bytes(original: bytes) -> bytes:
    if digest(original) != ORIGINAL_SHA256:
        raise ValueError("Unsupported original EXE SHA256")
    result = bytearray(original)
    if result[EDIT_OFFSET : EDIT_OFFSET + len(BEFORE)] != BEFORE:
        raise ValueError("Unexpected FUN_0043F5D0 case-3 gather-cooldown bytes")
    result[EDIT_OFFSET : EDIT_OFFSET + len(AFTER)] = AFTER
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
        raise ValueError("Refusing restore: destination is not the exact gather-cooldown probe")
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
    print(create_copy(args.source, args.destination) if args.command == "create-copy" else restore(args.destination))


if __name__ == "__main__":
    main()
