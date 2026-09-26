#!/usr/bin/env python3
"""Isolate each v1/v2 G5 edit bundle for the lap685 18:19 bisection plan.

lap685 confirmed two things about the reproducible G5 attack-broadcast
regression (original sustains ``command==4``/``+0x384==ATTACK_PENDING_WORD``
for ~100% of a selection, both v2 and v3 candidates sustain it for ~0%):
chunked dispatch itself is not the cause (v2, which has no chunking, fails
identically to v3), and no leftover literal reference to the stock 20-entry
selection array (``0x899024``/``0x899028``/``0x89902A``/``0x899078``) survives
in the v1-patched executable. The regression is therefore somewhere in one of
the five edit bundles that make up v1+v2, or in an indirect/register-relative
reference that a literal scan cannot see.

Each builder below applies exactly *one* of those bundles directly to the
pinned original executable -- never on top of another bundle -- so a
<=20-unit attack probe (well inside the stock capacity, so none of these
partial candidates need to actually reach 50 selected units to be exercised)
can show whether that bundle alone breaks sustained attack orders. None of
these candidates are a shippable G5 patch; they exist only to localize the
regression to a single bundle before it is fixed in v1/v2/v3 proper.

Bundle map (operator naming, 2026-09-26 18:19):
    G1  -- hit-test append cap only (``HIT_TEST_APPEND_LIMIT_SITES``)
    G2  -- selection-array relocation only (``DIRECT_SITES`` + ``END_SITES``
           + the header/geometry artifact that creates the new storage)
    G3  -- selection-change consumer frame widening only
           (``SELECTION_CONSUMER_LIMIT_SITES``)
    G4  -- control-group ``+0x344`` hooks (v2's H1/H2/H3 caves)
    G5  -- everything else in v1 not covered above (``ROTATION_SITES``,
           the control-group Ctrl+digit rotation cap)

G1/G3/G5 do not touch or depend on the relocated selection storage, so they
patch the plain original bytes and leave the stock array (base
``0x00899024``, capacity 20) untouched. G2 alone performs the header/geometry
change and relocation; it reports capacity 50 (its structural capacity) but a
<=20-unit bisection probe only ever populates the first 20 of that space.

G4 turned out **not** to be isolable on the plain original: v2's H1 hook
site (``0x00445D4E``) overlaps a ``DIRECT_SITES`` operand at ``0x00445D52``,
so v2's pinned "old bytes" only match after v1's relocation has already run.
G4 is instead tested as the delta between ``build_v1_full`` (all of v1, no
hooks) and ``build_v2_full`` (v1 + H1/H2/H3) -- if v1 alone sustains attack
and v2 does not, the hooks are the culprit without needing a hooks-alone
build.
"""

from __future__ import annotations

import hashlib
import struct
from typing import Any, Callable

import pefile

from patches.selection import g5_selection_cap50_v1 as v1
from patches.selection import g5_selection_cap50_v2 as v2

ORIGINAL_SHA256 = v1.ORIGINAL_SHA256
STOCK_SELECTION_BASE = 0x00899024
STOCK_SELECTION_CAPACITY = 20


def _pe(data: bytes) -> pefile.PE:
    return pefile.PE(data=data, fast_load=True)


def _finish(out: bytearray, original: bytes, bundle: str, *, selection_base: int, selection_capacity: int, extra: dict[str, Any] | None = None) -> tuple[bytes, dict[str, Any]]:
    candidate = bytes(out)
    if len(candidate) != len(original):
        raise v1.BuildAbortedError(f"{bundle}: candidate changed raw file length")
    report: dict[str, Any] = {
        "schema": "syw2plus.g5-selection-cap50-bisect-candidate.v1",
        "bundle": bundle,
        "original_sha256": ORIGINAL_SHA256,
        "candidate_sha256": hashlib.sha256(candidate).hexdigest(),
        "selection_base": selection_base,
        "selection_capacity": selection_capacity,
    }
    if extra:
        report.update(extra)
    return candidate, report


def build_g1_hit_test_only(original: bytes) -> tuple[bytes, dict[str, Any]]:
    """Bundle G1: raise the hit-test append cap (``0x0043877A``) alone."""
    v1.verify_original(original)
    out = bytearray(original)
    pe = _pe(bytes(out))
    try:
        for va, old_bytes, new_bytes in v1.HIT_TEST_APPEND_LIMIT_SITES:
            v1._patch_exact(out, pe, va, old_bytes, new_bytes)
    finally:
        pe.close()
    return _finish(
        out, original, "G1_hit_test_cap",
        selection_base=STOCK_SELECTION_BASE, selection_capacity=STOCK_SELECTION_CAPACITY,
        extra={"patched_hit_test_append_limit_sites": len(v1.HIT_TEST_APPEND_LIMIT_SITES)},
    )


def build_g2_relocation_only(original: bytes) -> tuple[bytes, dict[str, Any]]:
    """Bundle G2: relocate the selection array alone (``DIRECT_SITES`` + ``END_SITES``)."""
    stage, geometry = v1._header_artifact(original)
    out = bytearray(stage)
    pe = _pe(bytes(out))
    try:
        for va, old_bytes, old_value in v1.DIRECT_SITES:
            new_value = {
                0x00899024: v1.SELECTION_BASE,
                0x00899028: v1.SELECTION_BASE + 4,
                0x0089902A: v1.SELECTION_BASE + 6,
            }[old_value]
            v1._patch_exact(
                out, pe, va, old_bytes,
                old_bytes.replace(struct.pack("<I", old_value), struct.pack("<I", new_value), 1),
            )
        for va, old_bytes in v1.END_SITES:
            v1._patch_exact(
                out, pe, va, old_bytes,
                old_bytes.replace(
                    struct.pack("<I", 0x00899078),
                    struct.pack("<I", v1.SELECTION_BASE + v1.ENTRY_BYTES + v1.SELECTION_BYTES),
                    1,
                ),
            )
    finally:
        pe.close()
    return _finish(
        out, original, "G2_selection_relocation",
        selection_base=v1.SELECTION_BASE, selection_capacity=v1.TARGET_CAPACITY,
        extra={
            "geometry": geometry,
            "patched_direct_sites": len(v1.DIRECT_SITES),
            "patched_end_sites": len(v1.END_SITES),
            "note": "structural capacity 50, but a <=20-unit bisection probe only populates entries[0:20]",
        },
    )


def build_g3_consumer_only(original: bytes) -> tuple[bytes, dict[str, Any]]:
    """Bundle G3: widen the selection-change consumer frame alone (``0x0041DC40``)."""
    v1.verify_original(original)
    out = bytearray(original)
    pe = _pe(bytes(out))
    try:
        for va, old_bytes, new_bytes in v1.SELECTION_CONSUMER_LIMIT_SITES:
            v1._patch_exact(out, pe, va, old_bytes, new_bytes)
    finally:
        pe.close()
    return _finish(
        out, original, "G3_consumer_frame",
        selection_base=STOCK_SELECTION_BASE, selection_capacity=STOCK_SELECTION_CAPACITY,
        extra={"patched_selection_consumer_sites": len(v1.SELECTION_CONSUMER_LIMIT_SITES)},
    )


def build_v1_full(original: bytes) -> tuple[bytes, dict[str, Any]]:
    """All of v1 (G1+G2+G3+G5 together), no control-group hooks, no chunking.

    This is exactly ``v1.build_candidate``, re-exported under the bisection
    naming so the top-level v1-vs-v2 split can run through the same probe
    plumbing as the single-bundle candidates.
    """
    candidate, v1_report = v1.build_candidate(original)
    return _finish(
        bytearray(candidate), original, "V1_FULL",
        selection_base=v1.SELECTION_BASE, selection_capacity=v1.TARGET_CAPACITY,
        extra={"v1_report": v1_report},
    )


def build_v2_full(original: bytes) -> tuple[bytes, dict[str, Any]]:
    """v1 plus v2's H1/H2/H3 control-group hooks, no chunking.

    G4 ("H3 그룹 호출 케이브") cannot be isolated on the plain original: its
    hook sites (e.g. ``0x00445D52``, inside the H1 site range) are themselves
    ``DIRECT_SITES`` operands, so the hook's pinned "old bytes" only match
    *after* v1's relocation has already run. The valid bisection test for G4
    is therefore V1_FULL vs V2_FULL (this builder), not a hooks-alone patch.
    """
    candidate, v2_report = v2.build_candidate(original)
    return _finish(
        bytearray(candidate), original, "V2_FULL",
        selection_base=v2.SELECTION_BASE, selection_capacity=v2.TARGET_CAPACITY,
        extra={"v2_report": v2_report},
    )


def build_g5_rotation_only(original: bytes) -> tuple[bytes, dict[str, Any]]:
    """Bundle G5 (기타): raise the control-group rotation cap alone (``ROTATION_SITES``)."""
    v1.verify_original(original)
    out = bytearray(original)
    pe = _pe(bytes(out))
    try:
        v1._replace_operand_group(out, pe, v1.ROTATION_SITES, 0x14, v1.TARGET_CAPACITY)
    finally:
        pe.close()
    return _finish(
        out, original, "G5_rotation_cap",
        selection_base=STOCK_SELECTION_BASE, selection_capacity=STOCK_SELECTION_CAPACITY,
        extra={"patched_rotation_sites": len(v1.ROTATION_SITES)},
    )


BUILDERS: dict[str, Callable[[bytes], tuple[bytes, dict[str, Any]]]] = {
    "G1": build_g1_hit_test_only,
    "G2": build_g2_relocation_only,
    "G3": build_g3_consumer_only,
    "G5": build_g5_rotation_only,
    "V1_FULL": build_v1_full,
    "V2_FULL": build_v2_full,
}
