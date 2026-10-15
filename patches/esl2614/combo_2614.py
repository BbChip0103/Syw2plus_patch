#!/usr/bin/env python3
"""Versioned ESL2614 delivery compositions: G2+G5+G6+G8 and plus G9."""
from __future__ import annotations

import hashlib
from typing import Any

from patches.esl2610 import g6_shift_click_2610, g8_supply_1500_500_5000, pe_extend
from patches.esl2614 import g2_port_2614, g9_fixed_start_2614

VARIANTS = ("g2g5g6g8", "g2g5g6g8g9")


def build(data: bytes, variant: str, *, stock: bytes | None = None,
          bounds_decisions: dict[int, dict[str, Any]] | None = None
          ) -> tuple[bytes, dict[str, Any]]:
    if variant not in VARIANTS:
        raise ValueError(f"variant must be one of {VARIANTS}")
    if hashlib.sha256(data).hexdigest() != g2_port_2614.OFFICIAL_SHA256:
        raise ValueError("2614 composition requires the exact pinned official input")
    image, g2g5 = g2_port_2614.build_g2_g5_candidate(
        data, stock=stock, bounds_decisions=bounds_decisions)
    image, g6 = g6_shift_click_2610.build_candidate(image, require_pinned_base=False)
    image, g8 = g8_supply_1500_500_5000.build_candidate(image, require_pinned_base=False)
    layers: dict[str, Any] = {"g2g5": g2g5, "g6": g6, "g8": g8}
    if variant == "g2g5g6g8g9":
        image, g9 = g9_fixed_start_2614.apply(image, data)
        layers["g9"] = g9
    return image, {
        "schema": "syw2plus.esl2614.combos.v1",
        "variant": variant,
        "layers": ["G2", "G5", "G6", "G8"] + (["G9"] if variant.endswith("g9") else []),
        "input_sha256": hashlib.sha256(data).hexdigest(),
        "candidate_sha256": hashlib.sha256(image).hexdigest(),
        "sections": [name.decode() for name in pe_extend.section_names(image)[-4:]],
        "detail": layers,
    }


def restore(candidate: bytes, original: bytes, variant: str, *, stock: bytes | None = None) -> bytes:
    expected, _ = build(original, variant, stock=stock)
    if candidate != expected:
        raise ValueError("candidate does not match the reproducible ESL2614 composition")
    return original
