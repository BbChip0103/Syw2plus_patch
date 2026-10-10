#!/usr/bin/env python3
"""Keep the 2608 AI table editable at its original address after .shopai.

:mod:`shop_open_research_2608` relocated the 143-row AI production/research
table from ``0x004EC514`` to the ``.shopai`` section so that three RID-20
rows could be appended.  The selector ``0x00406C70`` then only reads the
copy, so OllyDbg edits made at the familiar 2608 address no longer reach the
AI (gunpowder prerequisites, extra production rows, ascension units, ...).

This layer hooks the selector entry: every call first copies the 143 original
rows (``0x004EC514``, without the sentinel) over the first 143 rows of
``.shopai`` and then runs the original ``sub esp,0xCC``.  The appended shop
rows and their sentinel are never touched.  The old table becomes the single
source of truth again; ``.shopai`` is only a working copy.

The cave lives in ``.shopai``'s existing raw padding (same mapped page), so no
section is added and SizeOfImage does not change.  ``.shopai`` becomes
readable/writable/executable.  Copy-only: inputs are never written.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

IMAGE_BASE = 0x00400000
INPUT_SHA256 = {
    "r5-normal": "b582fb1969e8e08076cc69ef93bd99669f65baefebfb9e4d4f88c2b8d90a2dfd",
    "r5-fixed-start": "acf5bd3d7f4657d95cc9bc4db3621dd4184d823416719095c3b714f0f0cbf1a4",
    "r5-g1-normal": "9fe0e9f367f4db03e9765a86be548770322b4aff54e449f0720f37982273aa62",
    "r5-g1-fixed-start": "bfddd8d8ac697efd28d415e0132343695c0b95f4f56ae45aa5a9027452fafad9",
}

OLD_TABLE_VA = 0x004EC514
OLD_TABLE_FILE_OFFSET = 0x000EC514
ROW_COUNT = 143
TABLE_STRIDE = 18
COPY_LEN = ROW_COUNT * TABLE_STRIDE  # 2574: rows only, never the sentinel

SHOPAI_VA = 0x0112D000
SHOPAI_FILE_OFFSET = 0x00104000
SHOPAI_PAYLOAD_LEN = 0xA46  # 146 rows + sentinel
SHOPAI_RAW_SIZE = 0x1000
OLD_CHARACTERISTICS = 0x40000040  # initialized data | read
NEW_CHARACTERISTICS = 0xE0000040  # initialized data | execute | read | write

HOOK_VA = 0x00406C70
HOOK_FILE_OFFSET = HOOK_VA - IMAGE_BASE
HOOK_OLD = bytes.fromhex("81 ec cc 00 00 00")  # sub esp,0xCC
HOOK_RESUME_VA = HOOK_VA + len(HOOK_OLD)

CAVE_RVA_IN_SECTION = 0xA48
CAVE_VA = SHOPAI_VA + CAVE_RVA_IN_SECTION
CAVE_FILE_OFFSET = SHOPAI_FILE_OFFSET + CAVE_RVA_IN_SECTION


def _cave() -> bytes:
    body = b"".join(
        (
            b"\x56\x57\x51",  # push esi; push edi; push ecx (ecx = unit)
            b"\xfc",  # cld
            b"\xbe" + struct.pack("<I", OLD_TABLE_VA),  # mov esi,old table
            b"\xbf" + struct.pack("<I", SHOPAI_VA),  # mov edi,.shopai
            b"\xb9" + struct.pack("<I", COPY_LEN // 4),  # mov ecx,643
            b"\xf3\xa5",  # rep movsd
            b"\x66\xa5",  # movsw (2574 = 643*4 + 2)
            b"\x59\x5f\x5e",  # pop ecx; pop edi; pop esi
            HOOK_OLD,
        )
    )
    jmp_from = CAVE_VA + len(body) + 5
    return body + b"\xe9" + struct.pack("<i", HOOK_RESUME_VA - jmp_from)


def _hook() -> bytes:
    return b"\xe9" + struct.pack("<i", CAVE_VA - (HOOK_VA + 5)) + b"\x90"


def _u32(data: bytes | bytearray, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def _shopai_header(data: bytes | bytearray) -> int:
    pe = _u32(data, 0x3C)
    count = struct.unpack_from("<H", data, pe + 6)[0]
    table = pe + 24 + struct.unpack_from("<H", data, pe + 20)[0]
    found = [
        table + i * 40
        for i in range(count)
        if bytes(data[table + i * 40 : table + i * 40 + 8]) == b".shopai\0"
    ]
    if len(found) != 1:
        raise ValueError(f"expected exactly one .shopai section, got {len(found)}")
    return found[0]


def _check_layout(data: bytes | bytearray, *, applied: bool) -> int:
    header = _shopai_header(data)
    vsize, rva, raw_size, raw = struct.unpack_from("<IIII", data, header + 8)
    if (IMAGE_BASE + rva, raw, raw_size) != (SHOPAI_VA, SHOPAI_FILE_OFFSET, SHOPAI_RAW_SIZE):
        raise ValueError(".shopai placement is not the pinned R5 layout")
    cave = _cave()
    expected = (
        (CAVE_RVA_IN_SECTION + len(cave), NEW_CHARACTERISTICS, _hook(), cave)
        if applied
        else (SHOPAI_PAYLOAD_LEN, OLD_CHARACTERISTICS, HOOK_OLD, b"\0" * len(cave))
    )
    actual = (
        vsize,
        _u32(data, header + 36),
        bytes(data[HOOK_FILE_OFFSET : HOOK_FILE_OFFSET + len(HOOK_OLD)]),
        bytes(data[CAVE_FILE_OFFSET : CAVE_FILE_OFFSET + len(cave)]),
    )
    if actual != expected:
        raise ValueError(f"{'applied' if applied else 'source'} sync layout mismatch")
    pad = data[SHOPAI_FILE_OFFSET + SHOPAI_PAYLOAD_LEN : CAVE_FILE_OFFSET]
    tail = data[CAVE_FILE_OFFSET + len(cave) : SHOPAI_FILE_OFFSET + SHOPAI_RAW_SIZE]
    if any(pad) or any(tail):
        raise ValueError(".shopai padding is not zero")
    return header


def build_candidate(source: bytes) -> tuple[bytes, dict[str, Any]]:
    """Return ``(candidate, report)`` for a pinned R5/R5_G1 input."""

    digest = hashlib.sha256(source).hexdigest()
    variant = next((k for k, v in INPUT_SHA256.items() if v == digest), None)
    if variant is None:
        raise ValueError(f"input SHA256 is not a pinned R5 EXE: {digest}")
    header = _check_layout(source, applied=False)
    if source[OLD_TABLE_FILE_OFFSET : OLD_TABLE_FILE_OFFSET + COPY_LEN] != source[
        SHOPAI_FILE_OFFSET : SHOPAI_FILE_OFFSET + COPY_LEN
    ]:
        raise ValueError(".shopai rows do not mirror the old 2608 table")
    cave = _cave()
    out = bytearray(source)
    struct.pack_into("<I", out, header + 8, CAVE_RVA_IN_SECTION + len(cave))
    struct.pack_into("<I", out, header + 36, NEW_CHARACTERISTICS)
    out[HOOK_FILE_OFFSET : HOOK_FILE_OFFSET + len(HOOK_OLD)] = _hook()
    out[CAVE_FILE_OFFSET : CAVE_FILE_OFFSET + len(cave)] = cave
    candidate = bytes(out)
    _check_layout(candidate, applied=True)
    report = {
        "version": "esl2608-ai-shop-table-sync-v1",
        "variant": variant,
        "source_sha256": digest,
        "candidate_sha256": hashlib.sha256(candidate).hexdigest(),
        "hook_va": f"0x{HOOK_VA:08x}",
        "cave_va": f"0x{CAVE_VA:08x}",
        "cave_len": len(cave),
        "copy": f"0x{OLD_TABLE_VA:08x}+{COPY_LEN} -> 0x{SHOPAI_VA:08x}",
        "runtime_status": "static + emulated selector; game/Wine not launched",
    }
    return candidate, report


def restore_candidate(candidate: bytes) -> bytes:
    """Exact inverse of :func:`build_candidate`."""

    header = _check_layout(candidate, applied=True)
    cave = _cave()
    out = bytearray(candidate)
    struct.pack_into("<I", out, header + 8, SHOPAI_PAYLOAD_LEN)
    struct.pack_into("<I", out, header + 36, OLD_CHARACTERISTICS)
    out[HOOK_FILE_OFFSET : HOOK_FILE_OFFSET + len(HOOK_OLD)] = HOOK_OLD
    out[CAVE_FILE_OFFSET : CAVE_FILE_OFFSET + len(cave)] = b"\0" * len(cave)
    restored = bytes(out)
    if hashlib.sha256(restored).hexdigest() not in INPUT_SHA256.values():
        raise ValueError("restored bytes are not a pinned R5 EXE")
    return restored


def write_candidate(source_path: Path, destination: Path) -> dict[str, Any]:
    if destination.resolve() == source_path.resolve():
        raise ValueError("refusing to overwrite the source")
    if destination.exists():
        raise FileExistsError(f"refusing to overwrite existing candidate: {destination}")
    candidate, report = build_candidate(source_path.read_bytes())
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb") as handle:
        handle.write(candidate)
    with destination.with_suffix(destination.suffix + ".json").open("x", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    print(json.dumps(write_candidate(args.source, args.destination), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
