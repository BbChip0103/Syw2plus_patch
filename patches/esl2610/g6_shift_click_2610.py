#!/usr/bin/env python3
"""G6 on ESL 2610: bound the Shift+click membership loop by the selection count.

2610 keeps the original Shift+click handler (``0x41DC40``) with the selection
array moved to ``0x1604004`` (2610/2611 used 100 slots, 2612 is back to 20).  The handler
compacts the selection into a zeroed stack array (count stored at
``[esp+0x10]`` by ``0x41DD74``) and then its second loop (``0x41DD82``) walks
all slots.  Empty slots are unit id 0, whose owner is compared with the
local player ``[0xB63FC4]``; for any seat other than 1P that comparison fails
and the add is aborted.  This is the same fix as the 2608 G6 layer
(``patches/selection/g6_shift_click_count_bound.py``, runtime-verified):
``jmp cave`` at the loop head, and the cave exits the loop once
``edi >= count`` (reloading ``eax`` with the clicked unit, as every loop pass
does, so an empty selection behaves like stock).  The cave lives in a new
``.g6code`` section.
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

HOOK_VA = 0x0041DD82
HOOK_OLD = bytes.fromhex("668b06b96ce36100")  # mov ax,[esi]; mov ecx,0x61E36C
LOOP_RESUME_VA = 0x0041DD8A  # push eax
LOOP_EXIT_VA = 0x0041DDE9  # first instruction after the slot loop
SECTION_NAME = b".g6code"


CLICKED_UNIT_VA = 0x00B938E0  # every loop pass ends with eax = [0xB938E0]


def _cave(cave_va: int) -> bytes:
    # cmp edi,[esp+0x10]; jl cont; mov eax,[clicked]; jmp exit; cont: <old>; jmp resume
    # The exit path reloads eax because the code after the loop pushes it as the
    # clicked unit; with an empty selection the loop body never ran to set it.
    cave = bytearray(
        bytes.fromhex("3b7c2410" "7c0a")
        + b"\xa1" + struct.pack("<I", CLICKED_UNIT_VA)
        + b"\xe9\0\0\0\0"
        + HOOK_OLD
        + b"\xe9\0\0\0\0"
    )
    struct.pack_into("<i", cave, 12, LOOP_EXIT_VA - (cave_va + 16))
    struct.pack_into("<i", cave, 25, LOOP_RESUME_VA - (cave_va + 29))
    return bytes(cave)


def build_candidate(data: bytes, *, require_pinned_base: bool = True) -> tuple[bytes, dict[str, Any]]:
    """Apply G6 to the pinned 2610 EXE (or, for stacking, to a 2610-derived image)."""
    if require_pinned_base:
        pe_extend.verify_base(data)
    if SECTION_NAME in pe_extend.section_names(data):
        raise ValueError("G6 is already applied")
    hook = pe_extend.va_to_offset(data, HOOK_VA)
    if data[hook : hook + len(HOOK_OLD)] != HOOK_OLD:
        raise ValueError("G6 hook site old bytes do not match")
    image = data if pe_extend.free_header_slots(data) else pe_extend.compact_headers(data)
    cave_va = pe_extend.IMAGE_BASE + struct.unpack_from(
        "<I", image, struct.unpack_from("<I", image, 0x3C)[0] + 24 + 56
    )[0]
    out = bytearray(pe_extend.add_section(image, SECTION_NAME, _cave(cave_va), 0x1000, pe_extend.CODE_RX))
    if pe_extend.section_va(out, SECTION_NAME) != cave_va:
        raise ValueError("G6 section was not placed at the first free RVA")
    hook = pe_extend.va_to_offset(out, HOOK_VA)
    out[hook : hook + 8] = b"\xe9" + struct.pack("<i", cave_va - (HOOK_VA + 5)) + b"\x90" * 3
    candidate = pe_extend._with_checksum(bytes(out))
    return candidate, {
        "schema": "syw2plus.esl2610.g6-shift-click-count-bound.v1",
        "input_sha256": hashlib.sha256(data).hexdigest(),
        "candidate_sha256": hashlib.sha256(candidate).hexdigest(),
        "hook_va": hex(HOOK_VA),
        "hook_old": HOOK_OLD.hex(),
        "cave_va": hex(cave_va),
    }


def write_candidate(source: Path, destination: Path) -> dict[str, Any]:
    if destination.resolve() == source.resolve():
        raise ValueError("refusing to overwrite the input EXE")
    candidate, report = build_candidate(source.read_bytes())
    fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(fd, "wb") as handle:
        handle.write(candidate)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="pinned official ESL2610 EXE")
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    print(json.dumps(write_candidate(args.source, args.destination), indent=2))


if __name__ == "__main__":
    main()
