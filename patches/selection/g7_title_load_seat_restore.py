#!/usr/bin/env python3
"""G7 H-G7r: restore the solo lobby seat table after a load, then let the game recompute the local player.

The save stream ends its fixed blocks with ``0x632F7C`` (0x170 bytes), the copy of the live lobby table
``0x632C9C`` the game took at game start.  A title-screen load in a new process leaves the live table empty,
so ``0x43AF40`` (own id -> first matching table slot) finds nothing and the local player index
``[0xB63FC4]`` stays 0: the player is put in seat 0 or told "defeated".  The game's own ps handler ``0x424DA0``
copies the snapshot back the same way, but the load path never does.

The patch hooks the first instruction after the load's ``fclose`` (``0x441310``).  For solo games
(``word [0x4ED848] == 1``) its cave copies snapshot -> live table (0x5C dwords), clears the local index (H-G7x R4b:
``0x43AF40`` leaves it untouched when nothing matches, so a 1P save loaded in a seat-2 game kept seat 2), calls
``0x43AF40(&0xB63FC4)`` and resumes with the replaced ``mov ebp,[0xB3AF2C]``.  The save format is unchanged, so existing saves are fixed.

Applies to the two pinned G5-selection ports of the ESL2608 G2 EXEs, or to the same port already carrying the
G6 candidate (``g6_shift_click_count_bound``); the two caves and hook sites do not overlap.
``restore_candidate`` returns the exact input.
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

from patches.selection import g6_shift_click_count_bound as g6

IMAGE_BASE = g6.IMAGE_BASE
PORT_SHA256 = g6.PORT_SHA256
HOOK_VA = 0x00441310
HOOK_OLD = bytes.fromhex("8b2d2cafb300")  # mov ebp,[0xB3AF2C]
RESUME_VA = 0x00441316
RESTORE_CALL_TARGET_VA = 0x0043AF40
G5CODE_VA = g6.G5CODE_VA
G5CODE_SIZE = g6.G5CODE_SIZE
CAVE_VA = G5CODE_VA + 0xD00  # G6 cave is at +0xC00 (23 bytes); port code ends at +0x8DA
CAVE_TEMPLATE = bytes.fromhex(
    "609c"  # pushad; pushfd
    "66833d48d84e0001"  # cmp word [0x4ED848],1 (solo game)
    "7529"  # jne skip
    "be7c2f6300"  # mov esi,0x632F7C (saved lobby snapshot)
    "bf9c2c6300"  # mov edi,0x632C9C (live lobby table)
    "b95c000000"  # mov ecx,0x5C
    "fc"  # cld
    "f3a5"  # rep movsd
    "c705c43fb60000000000"  # mov dword [0xB63FC4],0 (no first match -> seat 0, not the previous game's seat)
    "68c43fb600"  # push 0xB63FC4 (local player index)
    "e800000000"  # call 0x43AF40
    "83c404"  # add esp,4
    "9d61"  # skip: popfd; popad
    + HOOK_OLD.hex()
    + "e900000000"  # jmp 0x441316
)
CALL_OFFSET = 45
JMP_OFFSET = 61
SKIP_OFFSET = 53


def _file_offset(pe: pefile.PE, va: int) -> int:
    return g6._file_offset(pe, va)


def _cave_bytes() -> bytes:
    cave = bytearray(CAVE_TEMPLATE)
    struct.pack_into("<i", cave, CALL_OFFSET + 1, RESTORE_CALL_TARGET_VA - (CAVE_VA + CALL_OFFSET + 5))
    struct.pack_into("<i", cave, JMP_OFFSET + 1, RESUME_VA - (CAVE_VA + JMP_OFFSET + 5))
    return bytes(cave)


def _hook_bytes() -> bytes:
    return b"\xe9" + struct.pack("<i", CAVE_VA - (HOOK_VA + 5)) + b"\x90"


def _strip_g6(base: bytes) -> bytes | None:
    """The pinned port behind ``base`` if ``base`` is exactly that port plus the G6 candidate, else None."""
    pe = pefile.PE(data=base)
    hook = g6._file_offset(pe, g6.HOOK_VA)
    cave = g6._file_offset(pe, g6.CAVE_VA)
    if base[hook : hook + 8] != g6._hook_bytes():
        return None
    port = bytearray(base)
    port[hook : hook + 8] = g6.HOOK_OLD
    port[cave : cave + len(g6.CAVE_TEMPLATE)] = bytes(len(g6.CAVE_TEMPLATE))
    if hashlib.sha256(port).hexdigest() not in PORT_SHA256.values():
        return None
    try:
        rebuilt, _report = g6.build_candidate(bytes(port))
    except ValueError:
        return None
    return bytes(port) if rebuilt == base else None


def _locate(base: bytes) -> tuple[int, int, str, bool]:
    sha = hashlib.sha256(base).hexdigest()
    port, stacked = (base, False) if sha in PORT_SHA256.values() else (_strip_g6(base), True)
    if port is None:
        raise ValueError("input is not a pinned G5 port (optionally with the G6 candidate) on the ESL2608 G2 EXEs")
    variant = next(k for k, v in PORT_SHA256.items() if v == hashlib.sha256(port).hexdigest())
    pe = pefile.PE(data=base)
    if pe.sections[-1].Name.rstrip(b"\0") != b".g5code" or (
        IMAGE_BASE + pe.sections[-1].VirtualAddress != G5CODE_VA
    ):
        raise ValueError("port .g5code section is not at the pinned VA")
    return _file_offset(pe, HOOK_VA), _file_offset(pe, CAVE_VA), variant, stacked


def build_candidate(base: bytes) -> tuple[bytes, dict[str, Any]]:
    hook, cave, variant, stacked = _locate(base)
    cave_bytes = _cave_bytes()
    if base[hook : hook + len(HOOK_OLD)] != HOOK_OLD:
        raise ValueError("hook site old bytes do not match")
    if CAVE_VA + len(cave_bytes) > G5CODE_VA + G5CODE_SIZE or any(base[cave : cave + len(cave_bytes)]):
        raise ValueError("cave range is not a free zero run")
    out = bytearray(base)
    out[hook : hook + len(HOOK_OLD)] = _hook_bytes()
    out[cave : cave + len(cave_bytes)] = cave_bytes
    candidate = bytes(out)
    return candidate, {
        "schema": "syw2plus.g7-title-load-seat-restore.v1",
        "variant": variant,
        "stacked_on_g6": stacked,
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
    parser.add_argument("base", type=Path, help="pinned G5 port EXE (optionally with the G6 candidate applied)")
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    print(json.dumps(write_candidate(args.base, args.destination), indent=2))


if __name__ == "__main__":
    main()
