#!/usr/bin/env python3
"""Static decode of the AI production/research table `DAT_004EC514`.

Extends `analysis/memory_maps/ai_production_decision_path_00406770_20260923.md`
(lap501), which identified the table's location (143 records, 18 bytes
each, terminated by a nation-mask sentinel word `0xFFFE`) but left its
per-record field layout undecoded ("가장 유력한 정지 원인... 정적으로 알 수 없다").

This module disassembles `FUN_00406C70` (`0x00406C70`, the candidate
picker `FUN_00406B00`/`FUN_00406770` call to select a production or
research target) to recover that layout, then parses the table directly
from the protected original EXE's `.data` bytes. Read-only: it never
launches the game and never writes to the source file.

Record layout (18 bytes, offsets relative to the record base):

    +0x00 (i16) nation_mask   -- OR of 1=Joseon,2=Japan,4=Ming,8=other;
                                 checked against the calling building's
                                 owner's nation bit. Terminator sentinel
                                 is -2 (0xFFFE) at this offset.
    +0x02 (i16) building_type -- matched against the calling building's
                                 own `UnitStruct+0x8D` (type) byte.
    +0x04 (i16) produce_kind  -- the kind this entry would produce, or -1
                                 if this is a *research* entry.
    +0x06 (i16) research_kind -- the kind this entry would research, or
                                 -1 if this is a *production* entry.
                                 (Exactly one of produce_kind/research_kind
                                 is -1 per record; `FUN_00406C70`'s `param_2`
                                 selects which pool -- 0=production selects
                                 produce_kind!=-1, else research_kind!=-1.)
    +0x08 (i16) prereq_count_kind  -- -1 if none, else a kind whose owned
                                 count must be >= prereq_count_min.
    +0x0A (i16) prereq_count_min
    +0x0C (i16) prereq_own_kind_a  -- -1 if none, else a kind the owner
                                 must own >=1 of.
    +0x0E (i16) prereq_own_kind_b  -- second independent "must own >=1"
                                 prerequisite slot, -1 if unused.
    +0x10 (i16) tech_kind      -- -1 if none, else a research kind that
                                 must already be completed (looked up in a
                                 separate tech-definition table; if that
                                 table has no entry for tech_kind the check
                                 is skipped, i.e. treated as satisfied).

A record failing any of the four prerequisite checks above never reaches
`FUN_0043E7F0`'s G-6 gates at all -- `FUN_00406C70` returns -1 and
`FUN_00406B00` abandons the attempt for that AI dispatch. This is a
*fifth* rejection family lap501's `FUN_0043E7F0`-only model did not cover.
"""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Any

IMAGE_BASE = 0x00400000
PRODUCTION_TABLE_VA = 0x004EC514
RECORD_SIZE = 0x12
TERMINATOR_NATION_MASK = -2  # 0xFFFE as signed i16
MAX_RECORDS = 512  # generous static bound; the real table has 143


def _va_to_file_offset(pe, va: int) -> int:
    for section in pe.sections:
        start = IMAGE_BASE + int(section.VirtualAddress)
        raw_size = int(section.SizeOfRawData)
        if start <= va < start + raw_size:
            return int(section.PointerToRawData) + va - start
    raise ValueError(f"VA 0x{va:08x} is not in a raw section")


def _decode_record(data: bytes, offset: int, index: int) -> dict[str, Any] | None:
    nation_mask = struct.unpack_from("<h", data, offset + 0x00)[0]
    if nation_mask == TERMINATOR_NATION_MASK:
        return None
    fields = struct.unpack_from("<hhhhhhhhh", data, offset)
    (
        _nation_mask, building_type, produce_kind, research_kind,
        prereq_count_kind, prereq_count_min, prereq_own_kind_a,
        prereq_own_kind_b, tech_kind,
    ) = fields
    return {
        "index": index,
        "nation_mask": nation_mask & 0xFFFF,
        "building_type": building_type,
        "produce_kind": produce_kind,
        "research_kind": research_kind,
        "prereq_count_kind": prereq_count_kind,
        "prereq_count_min": prereq_count_min,
        "prereq_own_kind_a": prereq_own_kind_a,
        "prereq_own_kind_b": prereq_own_kind_b,
        "tech_kind": tech_kind,
    }


def load_production_table(exe_path: Path) -> list[dict[str, Any]]:
    """Parse every record (production and research) from the protected
    original EXE's on-disk bytes. Read-only file access only."""

    import pefile

    pe = pefile.PE(str(exe_path), fast_load=True)
    try:
        file_offset = _va_to_file_offset(pe, PRODUCTION_TABLE_VA)
        data = pe.__data__
        records: list[dict[str, Any]] = []
        for index in range(MAX_RECORDS):
            offset = file_offset + index * RECORD_SIZE
            record = _decode_record(data, offset, index)
            if record is None:
                break
            records.append(record)
        else:
            raise ValueError("production table did not terminate within MAX_RECORDS")
        return records
    finally:
        pe.close()


def production_records(exe_path: Path) -> list[dict[str, Any]]:
    """Records that can actually be *produced* (excludes research-only)."""

    return [r for r in load_production_table(exe_path) if r["produce_kind"] != -1]


def building_types(records: list[dict[str, Any]]) -> set[int]:
    return {r["building_type"] for r in records}


def records_for_building_type(records: list[dict[str, Any]], building_type: int) -> list[dict[str, Any]]:
    return [r for r in records if r["building_type"] == building_type]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True,
                         help="path to the protected original EXE (read-only)")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)

    all_records = load_production_table(args.source)
    prod = [r for r in all_records if r["produce_kind"] != -1]
    output = {
        "schema": "syw2plus.g4-ai-production-table.v1",
        "total_records": len(all_records),
        "production_count": len(prod),
        "research_count": len(all_records) - len(prod),
        "building_types": sorted(building_types(prod)),
        "records": all_records,
    }
    text = json.dumps(output, indent=2, ensure_ascii=False)
    if args.out is not None:
        args.out.write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
