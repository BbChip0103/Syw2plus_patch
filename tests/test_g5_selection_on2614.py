from __future__ import annotations

import pytest

from patches.selection.g5_selection_on2614 import (
    PATCH_SITES,
    PatchError,
    TARGET_CAPACITY,
    apply_sites,
)


def test_g5_2614_patch_changes_only_five_pinned_thresholds() -> None:
    offsets = (8, 32, 48, 80, 112)
    image = bytearray(160)
    for site, offset in zip(PATCH_SITES, offsets, strict=True):
        image[offset:offset + len(site.old)] = site.old

    candidate, audit = apply_sites(bytes(image), offsets)

    assert TARGET_CAPACITY == 100
    assert len(audit) == 5
    assert all(entry["old"] != entry["new"] for entry in audit)
    assert [candidate[offset:offset + len(site.new)] for site, offset in zip(PATCH_SITES, offsets, strict=True)] == [
        site.new for site in PATCH_SITES
    ]
    assert {index for index, (before, after) in enumerate(zip(image, candidate, strict=True)) if before != after} == {
        offset + index
        for site, offset in zip(PATCH_SITES, offsets, strict=True)
        for index, (before, after) in enumerate(zip(site.old, site.new, strict=True))
        if before != after
    }


def test_g5_2614_patch_fails_closed_on_old_byte_mismatch() -> None:
    offsets = (8, 32, 48, 80, 112)
    image = bytearray(160)
    for site, offset in zip(PATCH_SITES, offsets, strict=True):
        image[offset:offset + len(site.old)] = site.old
    image[32] ^= 0x01

    with pytest.raises(PatchError, match="old bytes mismatch"):
        apply_sites(bytes(image), offsets)


def test_g5_2614_patch_rejects_overlapping_or_out_of_range_offsets() -> None:
    image = bytearray(160)
    for site, offset in zip(PATCH_SITES[:4], (8, 32, 48, 80), strict=True):
        image[offset:offset + len(site.old)] = site.old
    image[8:8 + len(PATCH_SITES[0].old)] = PATCH_SITES[0].old
    with pytest.raises(PatchError, match="overlaps"):
        apply_sites(bytes(image), (8, 8, 48, 80, 112))
    for site, offset in zip(PATCH_SITES[:4], (8, 32, 48, 80), strict=True):
        image[offset:offset + len(site.old)] = site.old
    with pytest.raises(PatchError, match="outside image"):
        apply_sites(bytes(image), (8, 32, 48, 80, 158))
