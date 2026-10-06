#!/usr/bin/env python3
"""G6 H-G6a: bound the Shift+click membership loop by the compacted selection count.

The Shift+click handler at ``0x41DC40`` compacts the selection array into a zeroed
stack array (count in ``[esp+0x10]``), then its second loop (``0x41DD82``) walks all
50 slots.  Empty slots hold unit id 0, whose owner is compared with the local player
(``[0xB63FC4]``); for any local player other than 0 the comparison fails, so the
handler aborts the add (``[esp+0x28] = 1`` -> ``0x41DE40``).  Bounding the loop by
the compacted count removes the phantom id-0 comparison and leaves every real slot
check unchanged.

The patch applies only to the two pinned G5-selection ports on the ESL2608 G2 EXEs.
It rewrites the 8 bytes at the loop head into ``jmp cave; nop*3`` and adds one cave
in the zero tail of ``.g5code``.  ``restore_candidate`` returns the exact input.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
from pathlib import Path
from typing import Any

import pefile

IMAGE_BASE = 0x400000
PORT_SHA256 = {
    "normal": "0e28ef57f8eb1f674df544ef84889bd2c51224720a09d0a18122e55f8399d257",
    "fixed_start": "703deaf4c07b44975417f6835c569d65fa03adc2272ff6c75866da4723cd6ea0",
}
HOOK_VA = 0x0041DD82
HOOK_OLD = bytes.fromhex("668b06b96ce36100")  # mov ax,[esi]; mov ecx,0x61E36C
LOOP_RESUME_VA = 0x0041DD8A  # push eax (after the two replaced instructions)
LOOP_EXIT_VA = 0x0041DDE9  # first instruction after the 50-slot loop
G5CODE_VA = 0x018A7000
G5CODE_SIZE = 0x1000
CAVE_VA = G5CODE_VA + 0xC00  # port code ends at +0x8DA; +0x900..+0x1000 is zero
CAVE_TEMPLATE = bytes.fromhex("3b7c2410" "0f8d00000000" + HOOK_OLD.hex() + "e900000000")


def _file_offset(pe: pefile.PE, va: int) -> int:
    for section in pe.sections:
        start = IMAGE_BASE + section.VirtualAddress
        if start <= va < start + max(section.Misc_VirtualSize, section.SizeOfRawData):
            return va - start + section.PointerToRawData
    raise ValueError(f"VA 0x{va:08x} is not inside any section")


def _cave_bytes() -> bytes:
    cave = bytearray(CAVE_TEMPLATE)
    struct.pack_into("<i", cave, 6, LOOP_EXIT_VA - (CAVE_VA + 10))
    struct.pack_into("<i", cave, 19, LOOP_RESUME_VA - (CAVE_VA + 23))
    return bytes(cave)


def _hook_bytes() -> bytes:
    return b"\xe9" + struct.pack("<i", CAVE_VA - (HOOK_VA + 5)) + b"\x90\x90\x90"


def _locate(base: bytes) -> tuple[int, int, str]:
    sha = hashlib.sha256(base).hexdigest()
    variant = next((k for k, v in PORT_SHA256.items() if v == sha), None)
    if variant is None:
        raise ValueError("input SHA256 is not a pinned G5 port on the ESL2608 G2 EXEs")
    pe = pefile.PE(data=base)
    if pe.sections[-1].Name.rstrip(b"\0") != b".g5code" or (
        IMAGE_BASE + pe.sections[-1].VirtualAddress != G5CODE_VA
    ):
        raise ValueError("port .g5code section is not at the pinned VA")
    return _file_offset(pe, HOOK_VA), _file_offset(pe, CAVE_VA), variant


def build_candidate(base: bytes) -> tuple[bytes, dict[str, Any]]:
    hook, cave, variant = _locate(base)
    cave_bytes = _cave_bytes()
    if base[hook : hook + 8] != HOOK_OLD:
        raise ValueError("hook site old bytes do not match")
    if CAVE_VA + len(cave_bytes) > G5CODE_VA + G5CODE_SIZE or any(base[cave : cave + len(cave_bytes)]):
        raise ValueError("cave range is not a free zero run")
    out = bytearray(base)
    out[hook : hook + 8] = _hook_bytes()
    out[cave : cave + len(cave_bytes)] = cave_bytes
    candidate = bytes(out)
    return candidate, {
        "schema": "syw2plus.g6-shift-click-count-bound.v1",
        "variant": variant,
        "base_sha256": hashlib.sha256(base).hexdigest(),
        "candidate_sha256": hashlib.sha256(candidate).hexdigest(),
        "hook_va": hex(HOOK_VA),
        "hook_old": HOOK_OLD.hex(),
        "cave_va": hex(CAVE_VA),
        "cave_size": len(cave_bytes),
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
    parser.add_argument("base", type=Path, help="pinned G5 selection-50 ESL2608 G2 port EXE")
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    print(json.dumps(write_candidate(args.base, args.destination), indent=2))


if __name__ == "__main__":
    main()
