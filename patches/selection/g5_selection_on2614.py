#!/usr/bin/env python3
"""Re-enable ESL 2613's 100-unit selection thresholds in ESL 2614 only."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

import pefile


ORIGINAL_SHA256 = "ac61a28f84f71d602c581a17c835ec4dbb99aad0341c6755e395549005cf88bf"
TARGET_CAPACITY = 100


@dataclass(frozen=True)
class PatchSite:
    va: int
    old: bytes
    new: bytes
    role: str


# Static 2613↔2614 comparison: these same instructions use 100 in 2613 and
# 20 in 2614. No surrounding instruction or allocation is changed here.
PATCH_SITES = (
    PatchSite(0x0041DC68, bytes.fromhex("b8 14 00 00 00"), bytes.fromhex("b8 64 00 00 00"), "selection count result"),
    PatchSite(0x0041DDE4, bytes.fromhex("83 ff 14"), bytes.fromhex("83 ff 64"), "append capacity check"),
    PatchSite(0x0041DE55, bytes.fromhex("bf 14 00 00 00"), bytes.fromhex("bf 64 00 00 00"), "selection loop bound"),
    PatchSite(0x0043877A, bytes.fromhex("66 3d 14 00"), bytes.fromhex("66 3d 64 00"), "selection count comparison"),
    PatchSite(0x016016D9, bytes.fromhex("83 f9 14"), bytes.fromhex("83 f9 64"), "selection dispatch count"),
)


class PatchError(ValueError):
    """The input PE is not the pinned 2614 build or a patch byte differs."""


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _va_to_offset(pe: pefile.PE, va: int) -> int:
    rva = va - pe.OPTIONAL_HEADER.ImageBase
    for section in pe.sections:
        start = section.VirtualAddress
        end = start + max(section.Misc_VirtualSize, section.SizeOfRawData)
        if start <= rva < end:
            offset = section.PointerToRawData + rva - start
            if offset + 1 > len(pe.__data__):
                break
            return offset
    raise PatchError(f"VA 0x{va:08x} is outside mapped PE sections")


def apply_sites(image: bytes, offsets: tuple[int, ...]) -> tuple[bytes, list[dict[str, object]]]:
    """Apply exact, non-overlapping instruction replacements to a PE image."""
    if len(offsets) != len(PATCH_SITES):
        raise PatchError("patch-site offset count mismatch")
    out = bytearray(image)
    occupied: set[int] = set()
    audit: list[dict[str, object]] = []
    for site, offset in zip(PATCH_SITES, offsets, strict=True):
        if offset < 0 or offset + len(site.old) > len(out):
            raise PatchError(f"0x{site.va:08x}: patch range outside image")
        changed = set(range(offset, offset + len(site.old)))
        if occupied & changed:
            raise PatchError(f"0x{site.va:08x}: patch overlaps another site")
        occupied |= changed
        actual = bytes(out[offset : offset + len(site.old)])
        if actual != site.old:
            raise PatchError(
                f"0x{site.va:08x}: old bytes mismatch expected={site.old.hex()} actual={actual.hex()}"
            )
        out[offset : offset + len(site.old)] = site.new
        audit.append({
            "va": f"0x{site.va:08x}", "offset": offset, "role": site.role,
            "old": site.old.hex(), "new": site.new.hex(),
        })
    result = bytes(out)
    actual_changed = [i for i, (before, after) in enumerate(zip(image, result, strict=True)) if before != after]
    expected_changed = sorted(
        offset + index
        for site, offset in zip(PATCH_SITES, offsets, strict=True)
        for index, (before, after) in enumerate(zip(site.old, site.new, strict=True))
        if before != after
    )
    if actual_changed != expected_changed:
        raise PatchError("output differs outside the approved immediate bytes")
    return result, audit


def build_candidate(image: bytes) -> tuple[bytes, dict[str, object]]:
    """Build the 2614-only candidate with an exact SHA and byte pin."""
    source_sha = _sha256(image)
    if source_sha != ORIGINAL_SHA256:
        raise PatchError(f"2614 SHA mismatch: {source_sha}")
    try:
        pe = pefile.PE(data=image, fast_load=False)
    except pefile.PEFormatError as exc:
        raise PatchError("input is not a readable PE image") from exc
    offsets = tuple(_va_to_offset(pe, site.va) for site in PATCH_SITES)
    candidate, audit = apply_sites(image, offsets)
    del pe
    return candidate, {
        "source_sha256": source_sha,
        "candidate_sha256": _sha256(candidate),
        "target_capacity": TARGET_CAPACITY,
        "patches": audit,
        "revertible": True,
        "revert_method": "replace each new byte sequence with its recorded old bytes at the same VA",
    }
