#!/usr/bin/env python3
"""Exhaustive static scan for *any* remaining reference to the stock
20-entry selection array (count ``0x899024``, entries ``0x899028``, entries-
end ``0x899078``) that ``patches/selection/g5_selection_cap50_v1.py``'s
``DIRECT_SITES``/``END_SITES``/``ROTATION_SITES`` tables have not already
retargeted to the relocated (50-capacity) array.

2026-09-26 17:55 operator direction: lap685 found ``ever_command4_count``
stays ~0/49 even against the v2 candidate (relocated selection, no chunked
dispatch at all) -- exactly like v3 -- while MOVE keeps working. That rules
chunking out and points at something ATTACK-specific that still reads the
*old* stock array base even after v1's relocation. v1's own ``DIRECT_SITES``
table says it was built from "the lap628 inventory and its old-byte
regression" -- a decoded-immediate scan of a specific byte-pattern family
(mostly ``mov``/``cmp`` opcodes with a 32-bit absolute operand). This script
re-derives that inventory independently with a broader Capstone operand
scan (both ``X86_OP_MEM`` displacement operands and ``X86_OP_IMM``
operands, not just the specific opcode bytes v1 catalogued by hand) across
the *entire* ``.text`` section, then reports every hit whose address is not
already accounted for by v1's site tables -- the residual set is the
concrete, evidence-backed candidate list for what still needs retargeting.

Read-only: disassembles the protected original EXE bytes only, never writes
anything.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import capstone
import pefile

from patches.selection import g5_selection_cap50_v1 as v1
from tools import runtime_env

STOCK_COUNT = 0x00899024
STOCK_ENTRIES = 0x00899028
STOCK_ENTRIES_ALT = 0x0089902A  # v1's one odd-alignment DIRECT_SITES hit
STOCK_ENTRIES_END = 0x00899078
WATCHED_ADDRESSES = {STOCK_COUNT, STOCK_ENTRIES, STOCK_ENTRIES_ALT, STOCK_ENTRIES_END}

# Every address v1 already retargets (DIRECT_SITES/END_SITES/ROTATION_SITES
# are keyed by instruction VA, not the watched address, so build the set of
# already-handled instruction addresses instead).
KNOWN_SITE_ADDRESSES = frozenset(
    {va for va, _old, _oldval in v1.DIRECT_SITES}
    | {va for va, _old in v1.END_SITES}
    | {va for va, _old in v1.ROTATION_SITES}
)


def _section_bytes(pe: pefile.PE) -> tuple[int, bytes]:
    for section in pe.sections:
        if section.Name.rstrip(b"\0") == b".text":
            return v1.IMAGE_BASE + int(section.VirtualAddress), bytes(
                section.get_data(length=int(section.SizeOfRawData))
            )
    raise RuntimeError(".text section not found")


def inventory(executable: Path) -> dict[str, Any]:
    data = executable.read_bytes()
    v1.verify_original(data)
    pe = pefile.PE(data=data, fast_load=True)
    try:
        text_start, text = _section_bytes(pe)
        decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
        decoder.detail = True
        decoder.skipdata = True
        hits: list[dict[str, Any]] = []
        for insn in decoder.disasm(text, text_start):
            if insn.mnemonic == "(bad)" or not insn.bytes:
                continue
            try:
                operands = insn.operands
            except capstone.CsError:
                continue
            for operand in operands:
                watched = None
                if operand.type == capstone.x86.X86_OP_IMM:
                    value = int(operand.imm) & 0xFFFFFFFF
                    if value in WATCHED_ADDRESSES:
                        watched = value
                elif operand.type == capstone.x86.X86_OP_MEM:
                    mem = operand.mem
                    if mem.base == 0 and mem.index == 0:
                        value = int(mem.disp) & 0xFFFFFFFF
                        if value in WATCHED_ADDRESSES:
                            watched = value
                if watched is not None:
                    hits.append({
                        "address": f"0x{insn.address:08x}",
                        "watched_address": f"0x{watched:08x}",
                        "mnemonic": insn.mnemonic,
                        "op_str": insn.op_str,
                        "bytes": insn.bytes.hex(),
                        "already_handled": insn.address in KNOWN_SITE_ADDRESSES,
                    })
                    break
        residual = [item for item in hits if not item["already_handled"]]
        return {
            "schema": "syw2plus.g5-stock-selection-array-xrefs.v1",
            "watched_addresses": [f"0x{addr:08x}" for addr in sorted(WATCHED_ADDRESSES)],
            "text_section_start": f"0x{text_start:08x}",
            "text_section_bytes": len(text),
            "decoded_instructions": sum(1 for _ in decoder.disasm(text, text_start)),
            "known_site_count": len(KNOWN_SITE_ADDRESSES),
            "total_hits": len(hits),
            "residual_hits": residual,
            "residual_count": len(residual),
            "hits": hits,
        }
    finally:
        pe.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=runtime_env.DEFAULT_SOURCE)
    args = parser.parse_args(argv)
    executable = args.source.expanduser().resolve() / runtime_env.ORIGINAL_EXE
    result = inventory(executable)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
