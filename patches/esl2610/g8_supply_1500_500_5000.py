#!/usr/bin/env python3
"""G8 (2026-10-09 user goal): supply limit min(1500 + 500*living heroes, 5000).

The official 2610-line formula is 1500 + 200 per living hero, computed in
``0x43FDD0`` and stored at player ``+0x2012`` by ``0x43FFD9``.  G8 reproduces
the 2608-era "1500-500-5000" variant: the per-hero immediate becomes 500 and,
because 2610 removed the hero limit, a small cave in a new ``.g8code``
section clamps the result to 5000.  The plain G8 build and the G8+G9
(fixed start) build are the two user variants; both are also the load-test
setting for G2.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
from pathlib import Path
from typing import Any

from patches.esl2610 import pe_extend

PER_HERO_VA = 0x0043FE9E
PER_HERO_OLD = bytes.fromhex("81c1c8000000")  # add ecx,200
PER_HERO_NEW = bytes.fromhex("81c1f4010000")  # add ecx,500
BASE_ADD_VA = 0x0043FFD4
BASE_ADD_OLD = bytes.fromhex("05dc050000")  # add eax,1500
STORE_VA = 0x0043FFD9  # mov [ebp+0x2012],ax
SUPPLY_CAP = 5000
SECTION_NAME = b".g8code"


def _cave(cave_va: int) -> bytes:
    body = (
        BASE_ADD_OLD
        + b"\x3d" + struct.pack("<I", SUPPLY_CAP)  # cmp eax,5000
        + b"\x7e\x05"  # jle store
        + b"\xb8" + struct.pack("<I", SUPPLY_CAP)  # mov eax,5000
    )
    return body + b"\xe9" + struct.pack("<i", STORE_VA - (cave_va + len(body) + 5))


def build_candidate(data: bytes, *, require_pinned_base: bool = True) -> tuple[bytes, dict[str, Any]]:
    if require_pinned_base:
        pe_extend.verify_base(data)
    if SECTION_NAME in pe_extend.section_names(data):
        raise ValueError("G8 is already applied")
    for va, old in ((PER_HERO_VA, PER_HERO_OLD), (BASE_ADD_VA, BASE_ADD_OLD)):
        off = pe_extend.va_to_offset(data, va)
        if data[off : off + len(old)] != old:
            raise ValueError(f"supply site 0x{va:08x} old bytes do not match")
    image = data if pe_extend.free_header_slots(data) else pe_extend.compact_headers(data)
    cave_va = pe_extend.IMAGE_BASE + struct.unpack_from(
        "<I", image, struct.unpack_from("<I", image, 0x3C)[0] + 24 + 56
    )[0]
    out = bytearray(pe_extend.add_section(image, SECTION_NAME, _cave(cave_va), 0x1000, pe_extend.CODE_RX))
    if pe_extend.section_va(out, SECTION_NAME) != cave_va:
        raise ValueError("G8 section was not placed at the first free RVA")
    off = pe_extend.va_to_offset(out, PER_HERO_VA)
    out[off : off + len(PER_HERO_NEW)] = PER_HERO_NEW
    off = pe_extend.va_to_offset(out, BASE_ADD_VA)
    out[off : off + 5] = b"\xe9" + struct.pack("<i", cave_va - (BASE_ADD_VA + 5))
    candidate = pe_extend._with_checksum(bytes(out))
    return candidate, {
        "schema": "syw2plus.esl2610.g8-supply-1500-500-5000.v1",
        "formula": "min(1500 + 500*living_heroes, 5000)",
        "input_sha256": hashlib.sha256(data).hexdigest(),
        "candidate_sha256": hashlib.sha256(candidate).hexdigest(),
        "cave_va": hex(cave_va),
    }


def write_candidate(source: Path, destination: Path, *, require_pinned_base: bool = True) -> dict[str, Any]:
    if destination.resolve() == source.resolve():
        raise ValueError("refusing to overwrite the input EXE")
    candidate, report = build_candidate(source.read_bytes(), require_pinned_base=require_pinned_base)
    fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(fd, "wb") as handle:
        handle.write(candidate)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--stacked", action="store_true", help="input is a 2610-line derived image")
    args = parser.parse_args()
    report = write_candidate(args.source, args.destination, require_pinned_base=not args.stacked)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
