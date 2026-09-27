#!/usr/bin/env python3
"""Static decode of the AI building-construction prerequisite table
`DAT_004EDA24` (STATUS 2026-09-27 14:45 운영자 방향, lap714 후속 v2 step ①:
"AI 건설 결정 루틴... 정적으로 특정").

Extends `analysis/memory_maps/ai_build_faction_gate_0043dbb0_lap515_20260923.md`
(lap515), which identified `FUN_0043DB00`'s two prerequisite reads
(`+0x2FB8`/`+0x315C`, both indexed by a kind value looked up via
`FUN_00422EB0`) but left that lookup table's own layout and contents
undecoded. This module disassembles `FUN_00422EB0` (`0x00422EB0`) to
recover the 20-byte record layout, then parses the table directly from
the protected original EXE's `.data` bytes. Read-only: never launches the
game, never writes to the source file.

Record layout (20 bytes, offsets relative to the record base):

    +0x00 (i32) building_type       -- the key, matched against the
                                        candidate building type/kind
                                        `FUN_0043DBB0`/`FUN_0043DB00` are
                                        evaluating. Terminator: 0.
    +0x04 (i32) prereq_building_type -- 0 if none, else a building type
                                        the owner must already own >=1 of
                                        (checked against player `+0x2FB8`
                                        table, indexed by this value).
    +0x08 (i32) nation_kind          -- the faction worker/detection kind
                                        this building belongs to: 7
                                        (Joseon), 21/70 (Ming, two
                                        sub-blocks), 75 (Japan). Matches
                                        `FUN_0043DBB0`'s roster-driven
                                        `+0x314C/+0x3150/+0x3154/+0x3158`
                                        flags (see
                                        `tools/g4_ai_construction_gate_histogram_probe.py`).
    +0x0C (i32) prereq_own_kind      -- 0 if none, else a kind the owner
                                        must own >=1 of (checked against
                                        player `+0x315C` table -- the same
                                        table/semantics as
                                        `tools/g4_ai_production_table.py`'s
                                        `prereq_own_kind_a/b`, reused here
                                        for buildings).
    +0x10 (i32) cost                 -- construction cost (supply units).

`FUN_0043DB00(this=player, building_type)` calls `FUN_00422EB0(building_type,
&out1, &out2)` to fetch `prereq_building_type` (out1) and `prereq_own_kind`
(out2) for that building_type, then rejects (returns 0) if either
prerequisite is unmet. A `building_type` absent from this table (lookup
returns index-not-found) is treated by `FUN_00422EB0` as "no such record"
(edx stays 0 candidate count is never matched) -- `FUN_0043DB00` then reads
out1/out2 as untouched locals (initialized 0 by the caller), i.e. no
prerequisite is enforced. That is a *caller* fact, not modeled here.
"""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Any

IMAGE_BASE = 0x00400000
CONSTRUCTION_TABLE_VA = 0x004EDA24
RECORD_SIZE = 0x14
MAX_RECORDS = 200  # generous static bound; the real table has 39


def _va_to_file_offset(pe, va: int) -> int:
    for section in pe.sections:
        start = IMAGE_BASE + int(section.VirtualAddress)
        raw_size = int(section.SizeOfRawData)
        if start <= va < start + raw_size:
            return int(section.PointerToRawData) + va - start
    raise ValueError(f"VA 0x{va:08x} is not in a raw section")


def _decode_record(data: bytes, offset: int, index: int) -> dict[str, Any] | None:
    building_type, prereq_building_type, nation_kind, prereq_own_kind, cost = (
        struct.unpack_from("<iiiii", data, offset)
    )
    if building_type == 0:
        return None
    return {
        "index": index,
        "building_type": building_type,
        "prereq_building_type": prereq_building_type,
        "nation_kind": nation_kind,
        "prereq_own_kind": prereq_own_kind,
        "cost": cost,
    }


def load_construction_table(exe_path: Path) -> list[dict[str, Any]]:
    """Parse every record from the protected original EXE's on-disk bytes.
    Read-only file access only."""

    import pefile

    pe = pefile.PE(str(exe_path), fast_load=True)
    try:
        file_offset = _va_to_file_offset(pe, CONSTRUCTION_TABLE_VA)
        data = pe.__data__
        records: list[dict[str, Any]] = []
        for index in range(MAX_RECORDS):
            offset = file_offset + index * RECORD_SIZE
            record = _decode_record(data, offset, index)
            if record is None:
                break
            records.append(record)
        else:
            raise ValueError("construction table did not terminate within MAX_RECORDS")
        return records
    finally:
        pe.close()


def record_for_building_type(records: list[dict[str, Any]], building_type: int) -> dict[str, Any] | None:
    for record in records:
        if record["building_type"] == building_type:
            return record
    return None


# Nation-kind -> live PlayerStruct faction-detection flag offset, from
# lap515's `+0x33B0+kind` table and this lap's fresh `FUN_0043DBB0` jump
# table extraction (selector byte @ 0x0043E098 + (kind-7), 5-way jump
# table @ 0x0043E084): index0=kind7->+0x314C, index1=kind21->+0x3154,
# index2=kind70->+0x3158, index3=kind75->+0x3150, index4=unrecognized
# (no flag ever set -- see module docstring of the histogram probe).
NATION_KIND_TO_FLAG_OFF = {7: 0x314C, 21: 0x3154, 70: 0x3158, 75: 0x3150}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True,
                         help="path to the protected original EXE (read-only)")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)

    records = load_construction_table(args.source)
    output = {
        "schema": "syw2plus.g4-ai-construction-table.v1",
        "total_records": len(records),
        "building_types": sorted(r["building_type"] for r in records),
        "records": records,
    }
    text = json.dumps(output, indent=2, ensure_ascii=False)
    if args.out is not None:
        args.out.write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
