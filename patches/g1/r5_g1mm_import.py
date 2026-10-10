#!/usr/bin/env python3
"""G1 R5 bundle: point the pinned ESL2608 R5 EXEs at ``_G1MM.dll`` instead of ``_inmm.dll``.

The EXE has exactly one ``_INMM.dll`` string (the import descriptor name, file offset 0xEBB5E).
Replacing it with the same-length ``_G1MM.dll`` makes the Windows/Wine loader pick the G1
default-on DLL for this EXE only; the stock ``_inmm.dll`` in the same folder stays untouched.
Only the two bytes ``IN`` -> ``G1`` change (the name is matched case-insensitively by the loader).
The PE checksum field is 0 in the inputs and is left alone.  ``restore_candidate`` returns the exact input.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

IMPORT_NAME_OFFSET = 0xEBB5E
OLD_NAME = b"_INMM.dll\x00"
NEW_NAME = b"_G1MM.dll\x00"
# Neighbouring import-name bytes pin the site (previous import name, hint word, next import name).
CONTEXT_BEFORE = b"_imeBeginPeriod\x00"
CONTEXT_AFTER = b"\t\x00DirectDrawCreateEx\x00"
BASE_SHA256 = {
    "normal": "b582fb1969e8e08076cc69ef93bd99669f65baefebfb9e4d4f88c2b8d90a2dfd",
    "fixed_start": "acf5bd3d7f4657d95cc9bc4db3621dd4184d823416719095c3b714f0f0cbf1a4",
}


def _variant(base: bytes) -> str:
    sha = hashlib.sha256(base).hexdigest()
    variant = next((k for k, v in BASE_SHA256.items() if v == sha), None)
    if variant is None:
        raise ValueError("input SHA256 is not a pinned ESL2608 R5 EXE")
    return variant


def _check_site(data: bytes, name: bytes) -> None:
    start = IMPORT_NAME_OFFSET
    if data[start : start + len(name)] != name:
        raise ValueError("import name site bytes do not match")
    if data[start - len(CONTEXT_BEFORE) : start] != CONTEXT_BEFORE:
        raise ValueError("import name preceding context does not match")
    after = start + len(name)
    if data[after : after + len(CONTEXT_AFTER)] != CONTEXT_AFTER:
        raise ValueError("import name following context does not match")


def build_candidate(base: bytes) -> tuple[bytes, dict[str, Any]]:
    variant = _variant(base)
    _check_site(base, OLD_NAME)
    if base.count(OLD_NAME[:-1]) != 1:
        raise ValueError("input does not contain exactly one _INMM.dll string")
    out = bytearray(base)
    out[IMPORT_NAME_OFFSET : IMPORT_NAME_OFFSET + len(NEW_NAME)] = NEW_NAME
    candidate = bytes(out)
    changed = [i for i, (a, b) in enumerate(zip(base, candidate)) if a != b]
    if len(candidate) != len(base) or len(changed) != 2:
        raise ValueError("unexpected change set")
    return candidate, {
        "schema": "syw2plus.g1-r5-g1mm-import.v1",
        "variant": variant,
        "base_sha256": hashlib.sha256(base).hexdigest(),
        "candidate_sha256": hashlib.sha256(candidate).hexdigest(),
        "site_offset": hex(IMPORT_NAME_OFFSET),
        "changed_offsets": [hex(i) for i in changed],
        "old": OLD_NAME[:-1].decode(),
        "new": NEW_NAME[:-1].decode(),
    }


def restore_candidate(candidate: bytes, base: bytes) -> bytes:
    expected, _report = build_candidate(base)
    if candidate != expected:
        raise ValueError("candidate bytes do not match the pinned build; refusing to restore")
    return bytes(base)


def write_candidate(base_path: Path, destination: Path) -> dict[str, Any]:
    if destination.resolve() == base_path.resolve():
        raise ValueError("refusing to overwrite the input EXE")
    candidate, report = build_candidate(base_path.read_bytes())
    fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(fd, "wb") as handle:
        handle.write(candidate)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base", type=Path, help="pinned ESL2608 R5 EXE (normal or fixed-start)")
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    print(json.dumps(write_candidate(args.base, args.destination), indent=2))


if __name__ == "__main__":
    main()
