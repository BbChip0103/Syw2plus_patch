#!/usr/bin/env python3
"""G7 H-G7s (R5): keep the solo seat in the save file instead of recomputing it from a lobby snapshot.

User play (2026-10-06) showed that the R4b recompute (``g7_title_load_seat_restore``) puts a game started at a
seat other than 1P back into seat 0, both for title and in-game loads.  R5 does not depend on how the seat was chosen:
the G5SC save block (``0x18A7800``) ends with ``jmp fclose`` (``0x18A7832``).  A save hook writes a 16-byte header
(``'G7LS'``, version 1, ``[0xB63FC4]`` local index, ``word [0x4ED848]`` solo flag as a dword) and the live lobby table
``0x632C9C`` (0x170 bytes) after the G5SC block.  The G5SC load block (``0x18A7880``) ends with ``jmp fclose``
(``0x18A78D6``).  A load hook, only when this file carried G5SC and both the saved and current game are solo, reads the
header and table into ``.g5bss`` scratch, and only if both reads are complete copies the table back and restores the
local index.  Anything else (no trailer, other version, local >= 8, multiplayer) changes nothing, so older saves keep
the original in-game load behaviour.

Applies to the two pinned G5-selection ports of the ESL2608 G2 EXEs, or to the same port already carrying the G6
candidate (``g6_shift_click_count_bound``).  ``restore_candidate`` returns the exact input.
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
G5CODE_VA = g6.G5CODE_VA
G5CODE_SIZE = g6.G5CODE_SIZE
FCLOSE_VA = 0x004DA97C
SAVE_HOOK_VA = 0x018A7832  # tail ``jmp fclose`` of the G5SC save block
LOAD_HOOK_VA = 0x018A78D6  # tail ``jmp fclose`` of the G5SC load block
HOOK_OLD = {SAVE_HOOK_VA: bytes.fromhex("e94531c3fe"), LOAD_HOOK_VA: bytes.fromhex("e9a130c3fe")}
SAVE_CAVE_VA = G5CODE_VA + 0xD00  # G6 cave is at +0xC00 (23 bytes); port code ends at +0x8DA
LOAD_CAVE_VA = G5CODE_VA + 0xE00
SCRATCH_VA = 0x018A6E00  # .g5bss: 16-byte header, then the 0x170-byte table (port uses only up to 0x18A68D0)
SCRATCH_SIZE = 0x180
TAG = 0x534C3747  # 'G7LS'
VERSION = 1
SAVE_CAVE = bytes.fromhex(
    "609cc705006e8a0147374c53c705046e8a0101000000a1c43fb600a3086e8a010fb70548d84e00a30c6e8a01"
    "ff7424286a016a1068006e8a01e86126c3fe83c410ff7424286a016870010000689c2c6300e84926c3fe83c4109d61e91c2cc3fe"
)
LOAD_CAVE = bytes.fromhex(
    "609c66833d48d84e00010f8586000000813dd0688a0147355343757aff7424286a016a1068006e8a01e87b26c3fe83c41083f8"
    "017560813d006e8a0147374c537554833d046e8a0101754b833d0c6e8a01017542833d086e8a01087339ff7424286a01687001"
    "000068106e8a01e83726c3fe83c41083f801751cbe106e8a01bf9c2c6300b95c000000fcf3a5a1086e8a01a3c43fb6009d61"
    "e9df2ac3fe"
)
CAVES = {SAVE_CAVE_VA: SAVE_CAVE, LOAD_CAVE_VA: LOAD_CAVE}
HOOK_TO_CAVE = {SAVE_HOOK_VA: SAVE_CAVE_VA, LOAD_HOOK_VA: LOAD_CAVE_VA}


def _file_offset(pe: pefile.PE, va: int) -> int:
    return g6._file_offset(pe, va)


def _hook_bytes(hook_va: int) -> bytes:
    return b"\xe9" + struct.pack("<i", HOOK_TO_CAVE[hook_va] - (hook_va + 5))


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


def _locate(base: bytes) -> tuple[pefile.PE, str, bool]:
    sha = hashlib.sha256(base).hexdigest()
    port, stacked = (base, False) if sha in PORT_SHA256.values() else (_strip_g6(base), True)
    if port is None:
        raise ValueError("input is not a pinned G5 port (optionally with the G6 candidate) on the ESL2608 G2 EXEs")
    variant = next(k for k, v in PORT_SHA256.items() if v == hashlib.sha256(port).hexdigest())
    pe = pefile.PE(data=base)
    names = [section.Name.rstrip(b"\0") for section in pe.sections]
    if names[-1] != b".g5code" or IMAGE_BASE + pe.sections[-1].VirtualAddress != G5CODE_VA:
        raise ValueError("port .g5code section is not at the pinned VA")
    bss = next((s for s in pe.sections if s.Name.rstrip(b"\0") == b".g5bss"), None)
    if bss is None or not (
        IMAGE_BASE + bss.VirtualAddress <= SCRATCH_VA
        and SCRATCH_VA + SCRATCH_SIZE <= IMAGE_BASE + bss.VirtualAddress + bss.Misc_VirtualSize
    ):
        raise ValueError("port .g5bss does not contain the scratch range")
    return pe, variant, stacked


def build_candidate(base: bytes) -> tuple[bytes, dict[str, Any]]:
    pe, variant, stacked = _locate(base)
    out = bytearray(base)
    for hook_va, old in HOOK_OLD.items():
        offset = _file_offset(pe, hook_va)
        if base[offset : offset + len(old)] != old:
            raise ValueError(f"hook site 0x{hook_va:08x} old bytes do not match")
        out[offset : offset + len(old)] = _hook_bytes(hook_va)
    for cave_va, body in CAVES.items():
        offset = _file_offset(pe, cave_va)
        if cave_va + len(body) > G5CODE_VA + G5CODE_SIZE or any(base[offset : offset + len(body)]):
            raise ValueError(f"cave 0x{cave_va:08x} is not a free zero run")
        out[offset : offset + len(body)] = body
    candidate = bytes(out)
    return candidate, {
        "schema": "syw2plus.g7-save-trailer-local-restore.v1",
        "variant": variant,
        "stacked_on_g6": stacked,
        "base_sha256": hashlib.sha256(base).hexdigest(),
        "candidate_sha256": hashlib.sha256(candidate).hexdigest(),
        "hooks": {hex(va): old.hex() for va, old in HOOK_OLD.items()},
        "caves": {hex(va): len(body) for va, body in CAVES.items()},
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
