#!/usr/bin/env python3
"""ESL 2613 combo deliverables with G2 (user goal 2026-10-10).

* V8  = official 2613 + G2 (4093 global unit pool) + G6 (Shift+click bound)
  + G8 (supply min(1500 + 500*heroes, 5000));
* V89 = V8 + G9 (fixed start).

Layer order is fixed: G2 first (it compacts the headers and adds ``.g2bss`` and
``.g2code``), then G6 (``.g6code``), G8 (``.g8code``) and G9 (in place).  That
uses exactly the four section slots ``compact_headers`` frees.  The official
per-player cap 1008 and the official supply code are untouched by G2; G8 is
the only supply change.  Copy-only writer; the input is never modified.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from patches.esl2610 import (
    g2_pool4093_2610,
    g6_shift_click_2610,
    g8_supply_1500_500_5000,
    g9_fixed_start,
    pe_extend,
)

VARIANTS = ("v8", "v89")


def build(data: bytes, variant: str, *, stock: bytes | None = None) -> tuple[bytes, dict[str, Any]]:
    if variant not in VARIANTS:
        raise ValueError(f"variant must be one of {VARIANTS}")
    pe_extend.verify_base(data)
    image, g2 = g2_pool4093_2610.build_candidate(data, stock=stock)
    image, g6 = g6_shift_click_2610.build_candidate(image, require_pinned_base=False)
    image, g8 = g8_supply_1500_500_5000.build_candidate(image, require_pinned_base=False)
    report: dict[str, Any] = {"g2": g2, "g6": g6, "g8": g8}
    if variant == "v89":
        image, report["g9"] = g9_fixed_start.build_candidate(image, require_pinned_base=False)
    return image, {
    "schema": "syw2plus.esl2613.g2-combo.v1",
        "variant": variant,
        "layers": ["G2", "G6", "G8"] + (["G9"] if variant == "v89" else []),
        "input_sha256": hashlib.sha256(data).hexdigest(),
        "candidate_sha256": hashlib.sha256(image).hexdigest(),
        "sections": [n.decode() for n in pe_extend.section_names(image)[-4:]],
        "detail": report,
    }


def write_candidate(source: Path, destination: Path, variant: str) -> dict[str, Any]:
    if destination.resolve() == source.resolve():
        raise ValueError("refusing to overwrite the input EXE")
    candidate, report = build(source.read_bytes(), variant)
    fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(fd, "wb") as handle:
        handle.write(candidate)
    if destination.read_bytes() != candidate:
        raise ValueError("candidate write verification failed")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="pinned official ESL 2613 EXE")
    parser.add_argument("destination", type=Path)
    parser.add_argument("--variant", choices=VARIANTS, required=True)
    args = parser.parse_args()
    print(json.dumps(write_candidate(args.source, args.destination, args.variant), indent=2))


if __name__ == "__main__":
    main()
