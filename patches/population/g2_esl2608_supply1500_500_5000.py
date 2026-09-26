"""Copy-only supply variant of the two pinned ESL2608 G2 4092/500 builds.

The original 1600+200*heroes G2 executables are input references.  Only the
two immediate operands of the supply-limit formula change; G2 storage, hero
count, start-position and shop patches are not rebuilt or altered here.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


INPUT_SHA256 = {
    "seven": "2642b7f756312eefc7c5515465e1d67a1a10410976fc41e6dd390539ca99aa22",
    "seven_fixed_start": "2f617567438952a6a765f3cccbf93190d9dca6b420a9c53937f79c2fa6225751",
}
INPUT_SIZE = 0x108000
# VA 0x0043FE9E: add ecx, imm32. VA 0x0043FFD4: add eax, imm32.
# .text uses file offset = VA - ImageBase for this pinned PE layout.
PATCHES = (
    (0x3FEA0, bytes.fromhex("c8000000"), bytes.fromhex("f4010000")),
    (0x3FFD5, bytes.fromhex("40060000"), bytes.fromhex("dc050000")),
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_candidate(source: bytes) -> tuple[bytes, dict[str, str]]:
    variant = next((key for key, value in INPUT_SHA256.items() if digest(source) == value), None)
    if variant is None or len(source) != INPUT_SIZE:
        raise ValueError("unsupported ESL2608 G2 1600-200-3000 input SHA256/size")
    result = bytearray(source)
    previous_end = 0
    for offset, old, new in PATCHES:
        if offset < previous_end or len(old) != len(new) or offset + len(old) > len(source):
            raise ValueError("overlapping or out-of-range supply patch")
        if source[offset : offset + len(old)] != old:
            raise ValueError(f"supply preimage mismatch at 0x{offset:x}")
        result[offset : offset + len(new)] = new
        previous_end = offset + len(old)
    candidate = bytes(result)
    assert len(candidate) == len(source)
    return candidate, {
        "variant": variant,
        "source_sha256": digest(source),
        "candidate_sha256": digest(candidate),
        "supply_formula": "1500+500*living_heroes (seven heroes = 5000)",
    }


def create_copy(source: Path, destination: Path) -> dict[str, str]:
    if source.resolve() == destination.resolve():
        raise ValueError("refusing to overwrite input")
    candidate, report = build_candidate(source.read_bytes())
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb") as stream:
        stream.write(candidate)
    if digest(destination.read_bytes()) != report["candidate_sha256"]:
        raise ValueError("candidate write verification failed")
    return report


def restore_copy(destination: Path, source: Path) -> str:
    original = source.read_bytes()
    candidate, _ = build_candidate(original)
    if destination.read_bytes() != candidate:
        raise ValueError("refusing restore: destination is not exact candidate")
    temporary = Path(str(destination) + ".restore.tmp")
    with temporary.open("xb") as stream:
        stream.write(original)
    temporary.replace(destination)
    return digest(original)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("create-copy")
    create.add_argument("source", type=Path)
    create.add_argument("destination", type=Path)
    restore = sub.add_parser("restore")
    restore.add_argument("destination", type=Path)
    restore.add_argument("source", type=Path)
    args = parser.parse_args()
    if args.command == "create-copy":
        print(create_copy(args.source, args.destination))
    else:
        print(restore_copy(args.destination, args.source))


if __name__ == "__main__":
    main()
