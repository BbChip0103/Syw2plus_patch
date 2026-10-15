#!/usr/bin/env python3
"""ESL2614 profile adapter for the already-reviewed G9 fixed-start code."""
from __future__ import annotations

import hashlib
from typing import Any

from patches.esl2610 import g9_fixed_start, pe_extend

OFFICIAL_SHA256 = "ac61a28f84f71d602c581a17c835ec4dbb99aad0341c6755e395549005cf88bf"
EXPECTED_STACK = [b".g2bss", b".g2code", b".g6code", b".g8code"]


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def apply(image: bytes, original: bytes) -> tuple[bytes, dict[str, Any]]:
    """Apply exact G9 sites to an already-composed ESL2614 G2/G5/G6/G8 image."""
    if _sha(original) != OFFICIAL_SHA256:
        raise ValueError("G9 2614 adapter requires the pinned official ESL2614 input")
    if pe_extend.section_names(image)[-4:] != EXPECTED_STACK:
        raise ValueError("G9 2614 requires the composed four-section G2/G6/G8 stack")
    if g9_fixed_start.PROCEDURAL_SECTION in pe_extend.section_names(image):
        raise ValueError("G9 procedure already applied")
    out = bytearray(image)
    for va, old, _new in g9_fixed_start.CHUNKS:
        off = pe_extend.va_to_offset(image, va)
        if bytes(image[off:off + len(old)]) != old:
            raise ValueError(f"G9 2614 exact old bytes mismatch at 0x{va:08x}")
    proc_off = pe_extend.va_to_offset(image, g9_fixed_start.PROCEDURAL_SITE)
    if bytes(image[proc_off:proc_off + len(g9_fixed_start.PROCEDURAL_OLD)]) != g9_fixed_start.PROCEDURAL_OLD:
        raise ValueError("G9 2614 procedural selector preimage mismatch")

    code = bytearray(g9_fixed_start.PROCEDURAL_PREFIX)
    code_va, code_off = g9_fixed_start._stacked_cave(image, len(code) + 4)
    code.extend((g9_fixed_start.PROCEDURAL_CONTINUE - (code_va + len(code) + 4))
                .to_bytes(4, "little", signed=True))
    out[code_off:code_off + len(code)] = code
    detour = b"\xe9" + (code_va - (g9_fixed_start.PROCEDURAL_SITE + 5)).to_bytes(4, "little", signed=True) + b"\x90"
    out[proc_off:proc_off + len(detour)] = detour
    for va, old, new in g9_fixed_start.CHUNKS:
        off = pe_extend.va_to_offset(image, va)
        if bytes(out[off:off + len(old)]) != old:
            raise ValueError(f"G9 2614 chunk changed during composition at 0x{va:08x}")
        out[off:off + len(new)] = new
    candidate = pe_extend._with_checksum(bytes(out))
    return candidate, {
        "schema": "syw2plus.esl2614.g9-fixed-start.v1",
        "input_sha256": _sha(image), "original_sha256": _sha(original),
        "candidate_sha256": _sha(candidate),
        "chunks": [hex(va) for va, _, _ in g9_fixed_start.CHUNKS]
                  + [hex(g9_fixed_start.PROCEDURAL_SITE)],
        "procedural_va": hex(code_va), "procedural_placement": ".g8code+0x20",
        "procedural_code": bytes(code).hex(), "expanded_headers": False,
    }
