#!/usr/bin/env python3
"""Build G5 v2 variants with exactly one of H1/H2/H3 removed.

lap686 localized the dense-50 attack-broadcast regression to v2's control-group
hooks: V1_FULL alone sustains ``ever_command4_count`` for 18/49 selected units,
while V2_FULL (v1 + H1/H2/H3) collapses to 0/49. That is a delta test across
*all three* hooks at once. This module isolates which hook (or combination)
does the damage by building three variants, each v1 in full plus exactly two
of the three hooks -- so the run that recovers sustained attack orders names
the missing hook as the interference source.
"""

from __future__ import annotations

import hashlib
from typing import Any

import pefile

from patches.selection import g5_selection_cap50_v1 as v1
from patches.selection import g5_selection_cap50_v2 as v2

ORIGINAL_SHA256 = v1.ORIGINAL_SHA256
SELECTION_BASE = v2.SELECTION_BASE
TARGET_CAPACITY = v2.TARGET_CAPACITY

HOOKS = ("H1", "H2", "H3")


def build_candidate(original: bytes, *, skip: str) -> tuple[bytes, dict[str, Any]]:
    if skip not in HOOKS:
        raise ValueError(f"skip must be one of {HOOKS}, got {skip!r}")
    candidate_v1, v1_report = v1.build_candidate(original)
    out = bytearray(candidate_v1)
    pe = pefile.PE(data=bytes(out), fast_load=True)
    applied: list[str] = []
    try:
        for name, site, old, cave in (
            ("H1", v2.H1_SITE, v2.H1_OLD, v2.H1_CAVE),
            ("H2", v2.H2_SITE, v2.H2_OLD, v2.H2_CAVE),
            ("H3", v2.H3_SITE, v2.H3_OLD, v2.H3_CAVE),
        ):
            if name == skip:
                continue
            v2._patch_exact(out, pe, site, old, v2._hook(site, cave, old))
            applied.append(name)
        cave_report = v2._write_caves(out, pe)
    finally:
        pe.close()

    if len(out) != len(original):
        raise v1.BuildAbortedError("candidate changed raw file length")
    candidate = bytes(out)
    report: dict[str, Any] = {
        "schema": "syw2plus.g5-selection-cap50-v2-partial-candidate.v1",
        "skip": skip,
        "applied_hooks": applied,
        "original_sha256": ORIGINAL_SHA256,
        "v1_candidate_sha256": v1_report["candidate_sha256"],
        "candidate_sha256": hashlib.sha256(candidate).hexdigest(),
        "selection_base": SELECTION_BASE,
        "selection_capacity": TARGET_CAPACITY,
        "cave": cave_report,
    }
    return candidate, report
