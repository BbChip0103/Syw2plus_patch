#!/usr/bin/env python3
"""Build the G5 cap-50 candidate with safe control-group overflow storage.

The v1 candidate relocates the selection buffer and makes drag selection reach
50, but its Ctrl+digit writer still stores all 50 handles in the stock
20-entry PlayerStruct field.  This layer keeps the stock group structure for
the first 20 members and represents members 21..50 in the persisted unit
record's ``+0x344`` group field.  The three small trampolines are deliberately
kept separate from v1 so the v1 SHA and its rollback contract remain useful.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

import pefile

from patches.selection import g5_selection_cap50_v1 as v1


IMAGE_BASE = v1.IMAGE_BASE
ORIGINAL_SHA256 = v1.ORIGINAL_SHA256
STOCK_CAPACITY = v1.STOCK_CAPACITY
TARGET_CAPACITY = v1.TARGET_CAPACITY
SELECTION_BASE = v1.SELECTION_BASE
SELECTION_BYTES = v1.SELECTION_BYTES
CONTROL_GROUP_BASE = v1.CONTROL_GROUP_BASE
CONTROL_GROUP_BYTES = v1.CONTROL_GROUP_BYTES
STORAGE_END = v1.STORAGE_END
SECTION_ALIGNMENT = v1.SECTION_ALIGNMENT

UNIT_BASE = 0x0066B790
UNIT_STRIDE = 0x758
UNIT_GROUP_OFFSET = 0x344
UNIT_OWNER_OFFSET = 0x8E
UNIT_EXISTS_BASE = 0x008990C8
LOCAL_PLAYER = 0x00B63FC4
UNIT_SCAN_END = 1200

H1_SITE = 0x00445D4E
H1_OLD = bytes.fromhex("8b 54 24 14 bb 04 c0 08 01")
H1_CAVE = 0x004E4C00

H2_SITE = 0x00445DCB
H2_OLD = bytes.fromhex("8b 44 24 10 66 c7 00 00 00")
H2_CAVE = 0x004E4C80

H3_SITE = 0x00445ED1
H3_OLD = bytes.fromhex("85 db 0f 84 de 00 00 00")
H3_CAVE = 0x004E4CC0

CAVE_END = 0x004E5000  # exclusive; last byte remains inside .text raw data

# These bytes were assembled once with Keystone 0.9.2 and are kept inline so
# the production patcher has no assembler dependency.  All calls/branches are
# absolute-address-derived rel32 encodings for this fixed original build.
H1_CODE = bytes.fromhex(
    "6031f666833c75c890890000743789f08d3c40c1e70429f78d3cbf8d3cfd90b76600"
    "8b874403000039d875190fbe878e0000003b05c43fb600750ac78744030000ffffffff"
    "4681feb00400007cb5618b542414bb04c00801e9fa10f6ff"
)
H2_CODE = bytes.fromhex(
    # Overflow entries write the unit field directly.  Calling FUN_0040F750
    # through this hook preserved the field write but changed the relocated
    # selection count from 50 to 21 at runtime; keep the exact setter effect
    # without crossing that call boundary.
    "81fb54c00801721d0fb70369c05807000005d4ba6600"
    "8b4c242489088b6c2418e95c11f6ff8b44241066c7000000e92111f6ff"
)
H3_CODE = bytes.fromhex(
    # FUN_0040F790 uses ret 4, so its one pushed argument is already removed
    # by the callee.  The old add esp,4 skipped one dword in pushad's saved
    # frame and made the first overflow recall return with a shifted stack.
    # Keep the payload length stable so all following rel32 branches retain
    # their original displacement; the three bytes are inert padding.
    "6031f6837c241032737566833c75c890890000746189f050e86322f3ff83c404"
    "85c0745289f08d3c40c1e70429f78d3cbf8d3cfd90b766008b874403000039e87534"
    "0fbe878e0000003b05c43fb600752556e879aaf2ff90909083f80175176a006a0156"
    "b96ce36100e8a2aaf2ff85c07404ff4424104681feb00400007c846185db0f846f12f6"
    "ffe98c11f6ff"
)

IMMUTABLE_RANGES = (
    (0x00445A20, 0x00445CCB),
    (0x00445FF0, 0x00446177),
    (0x0043CB00, 0x0043D650),
    (0x004B1F20, 0x004B2150),
)


class BuildAbortedError(RuntimeError):
    """Raised when the pinned executable or a patch invariant differs."""


def _rel32(source: int, target: int) -> bytes:
    return struct.pack("<i", target - (source + 5))


def _va_to_file_offset(pe: pefile.PE, va: int) -> int:
    return v1._va_to_file_offset(pe, va)


def _patch_exact(out: bytearray, pe: pefile.PE, va: int, old: bytes, new: bytes) -> None:
    if len(old) != len(new):
        raise BuildAbortedError(f"0x{va:08x}: replacement changes instruction length")
    off = _va_to_file_offset(pe, va)
    actual = bytes(out[off : off + len(old)])
    if actual != old:
        raise BuildAbortedError(
            f"0x{va:08x}: old bytes mismatch expected={old.hex()} actual={actual.hex()}"
        )
    out[off : off + len(old)] = new


def _hook(site: int, cave: int, old: bytes) -> bytes:
    if len(old) < 5:
        raise BuildAbortedError("hook site is too short for a near jump")
    return b"\xe9" + _rel32(site, cave) + bytes(len(old) - 5)


def _write_caves(out: bytearray, pe: pefile.PE) -> dict[str, int]:
    text = next((s for s in pe.sections if s.Name.rstrip(b"\0") == b".text"), None)
    if text is None:
        raise BuildAbortedError("expected .text section")
    text_start = IMAGE_BASE + int(text.VirtualAddress)
    text_raw_end = text_start + int(text.SizeOfRawData)
    if not text_start <= H1_CAVE < CAVE_END <= text_raw_end:
        raise BuildAbortedError("cave is outside .text raw data")

    for address, payload in ((H1_CAVE, H1_CODE), (H2_CAVE, H2_CODE), (H3_CAVE, H3_CODE)):
        if address + len(payload) > CAVE_END:
            raise BuildAbortedError(f"cave payload exceeds reserved range at 0x{address:08x}")
        offset = _va_to_file_offset(pe, address)
        if bytes(out[offset : offset + len(payload)]) != bytes(len(payload)):
            raise BuildAbortedError(f"cave is not zero-filled at 0x{address:08x}")
        out[offset : offset + len(payload)] = payload

    virtual_size = CAVE_END - text_start
    if virtual_size > int(text.SizeOfRawData):
        raise BuildAbortedError(".text VirtualSize would exceed raw section size")
    if virtual_size < int(text.Misc_VirtualSize):
        raise BuildAbortedError("unexpected .text VirtualSize already beyond cave")
    struct.pack_into("<I", out, text.get_field_absolute_offset("Misc_VirtualSize"), virtual_size)
    return {
        "text_virtual_size": virtual_size,
        "text_raw_size": int(text.SizeOfRawData),
        "cave_end_exclusive": CAVE_END,
    }


def build_candidate(original: bytes) -> tuple[bytes, dict[str, Any]]:
    candidate_v1, v1_report = v1.build_candidate(original)
    out = bytearray(candidate_v1)
    pe = pefile.PE(data=bytes(out), fast_load=True)
    try:
        _patch_exact(out, pe, H1_SITE, H1_OLD, _hook(H1_SITE, H1_CAVE, H1_OLD))
        _patch_exact(out, pe, H2_SITE, H2_OLD, _hook(H2_SITE, H2_CAVE, H2_OLD))
        _patch_exact(out, pe, H3_SITE, H3_OLD, _hook(H3_SITE, H3_CAVE, H3_OLD))
        cave_report = _write_caves(out, pe)
    finally:
        pe.close()

    if len(out) != len(original):
        raise BuildAbortedError("candidate changed raw file length")
    candidate = bytes(out)
    report = {
        "schema": "syw2plus.g5-selection-cap50-control-groups-candidate.v2",
        "status": "SELECTION_CAP50_UNIT_FIELD_CONTROL_GROUPS",
        "original_sha256": ORIGINAL_SHA256,
        "v1_candidate_sha256": v1_report["candidate_sha256"],
        "candidate_sha256": hashlib.sha256(candidate).hexdigest(),
        "stock_capacity": STOCK_CAPACITY,
        "target_capacity": TARGET_CAPACITY,
        "selection_base": f"0x{SELECTION_BASE:08x}",
        "selection_end_exclusive": f"0x{SELECTION_BASE + 4 + SELECTION_BYTES:08x}",
        "control_group_base": f"0x{CONTROL_GROUP_BASE:08x}",
        "control_group_bytes": CONTROL_GROUP_BYTES,
        "geometry": v1_report["geometry"],
        "hooks": {
            "H1": {"site": hex(H1_SITE), "cave": hex(H1_CAVE), "behavior": "clear local unit +0x344 == group"},
            "H2": {"site": hex(H2_SITE), "cave": hex(H2_CAVE), "behavior": "stock first 20; overflow direct unit +0x344 write"},
            "H3": {"site": hex(H3_SITE), "cave": hex(H3_CAVE), "behavior": "recall local unit-field members through 50"},
        },
        "unit_field": hex(UNIT_GROUP_OFFSET),
        "unit_scan": {"base": hex(UNIT_BASE), "stride": hex(UNIT_STRIDE), "count": UNIT_SCAN_END},
        "cave": cave_report,
        "patched_v1_sites": {
            "direct": len(v1.DIRECT_SITES),
            "end": len(v1.END_SITES),
            "rotation": len(v1.ROTATION_SITES),
            "consumer": len(v1.SELECTION_CONSUMER_LIMIT_SITES),
            "hit_test": len(v1.HIT_TEST_APPEND_LIMIT_SITES),
        },
        "control_group_layout": "stock PlayerStruct first 20; unit +0x344 authoritative for 21..50",
        "save_format": "unchanged; unit records already persist +0x344",
        "command_packet": "unchanged; prior drag-50 command evidence remains in scope",
        "immutable_ranges": [[hex(start), hex(end)] for start, end in IMMUTABLE_RANGES],
    }
    return candidate, report


def restore_candidate(candidate: bytes, original: bytes) -> bytes:
    v1.verify_original(original)
    expected, _report = build_candidate(original)
    if hashlib.sha256(candidate).digest() != hashlib.sha256(expected).digest():
        raise ValueError("candidate SHA256 mismatch; refusing to restore unknown bytes")
    return bytes(original)


def write_candidate(original_path: Path, destination: Path) -> dict[str, Any]:
    if destination.resolve() == original_path.resolve():
        raise ValueError("refusing to overwrite the original EXE")
    original = original_path.read_bytes()
    patched, report = build_candidate(original)
    destination.write_bytes(patched)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    print(json.dumps(write_candidate(args.original, args.destination), indent=2))


if __name__ == "__main__":
    main()
