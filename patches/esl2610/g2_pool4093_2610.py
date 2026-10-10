#!/usr/bin/env python3
"""G2 unit-pool expansion (1200 -> 4093 slots) for the official ESL 2613 EXE.

User decision 2026-10-09: on the pinned official EXE, expand the global unit pool
from 1200 to 4093 slots (12-bit slot limit ~4095, same ceiling as the accepted
2608 G2), keep the official per-player unit cap 1008 and the official supply
formula (1500 + 200/general).  Only G2, composable with the separate G6 layer.

The accepted 2608 G2 relocated six unit-capacity arrays and shifted every
``.text`` operand into them.  2613 adds ~40 code sections and ~24 BSS sections
that reference the stock arrays (940 operands, :mod:`g2_scan`), gate units with
1200-sized bounds and keep ~50 per-unit arrays of their own.  The build is the
four layers of :mod:`patches.esl2610.g2_full_2610` (stock-oracle ``.text``
replay, module operand retargeting, module state growth to 4093 with every
capacity constant raised, save/load sidecars); each layer audits its own
coverage and raises on anything unclassified.  Without the stock oracle EXE
the build raises :class:`G2BuildBlocked`.  The official per-player cap 1008
and the official supply formula are not touched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from patches.esl2610 import g2_scan, pe_extend

CAPACITY = 4093  # 12-bit command-slot ceiling is 4095; slot zero reserved
USABLE_SLOTS = CAPACITY - 1


class G2BuildBlocked(RuntimeError):
    """Raised when the operand inventory still has unresolved blockers."""

    def __init__(self, report: dict[str, Any]) -> None:
        self.report = report
        kinds = ", ".join(f"{u['kind']}({u['count']})" for u in report["unresolved"])
        super().__init__(
            f"G2 4093 build blocked by {report['unresolved_count']} unresolved "
            f"operand class(es): {kinds}. See the inventory report; each must be "
            "relocated/resized and runtime-verified before a 2610 candidate can be emitted."
        )


STOCK_ORACLE = Path(__file__).resolve().parents[2] / "Syw2plus" / "syw2plus_original.exe"


def build_candidate(
    data: bytes, *, stock: bytes | None = None, require_pinned_base: bool = True
) -> tuple[bytes, dict[str, Any]]:
    """Build the 4093-slot candidate (layers 1-4 of :mod:`g2_full_2610`).

    The operand inventory below is the fail-closed contract: every class it
    reports is resolved by a layer whose ``apply`` audits its own coverage and
    raises on anything unclassified (layer 2: the 940 module operands and the
    pool/exist end sentinels; layer 3: the per-unit module state and every
    1200-family constant; layer 4: save/load).  The stock EXE is the accepted
    G2 oracle for ``.text``; without it the build is blocked.
    """
    if require_pinned_base:
        pe_extend.verify_base(data)
    inventory = g2_scan.build_inventory(data, require_pinned_base=require_pinned_base)
    report = inventory.to_report()
    if stock is None:
        if not STOCK_ORACLE.exists():
            report["unresolved"].append({"kind": "stock_oracle_missing", "count": 1})
            report["unresolved_count"] = len(report["unresolved"])
            raise G2BuildBlocked(report)
        stock = STOCK_ORACLE.read_bytes()
    from patches.esl2610 import g2_full_2610

    candidate, full = g2_full_2610.build_candidate(data, stock)
    full["inventory"] = {k: report[k] for k in ("total_sites", "text_sites", "new_section_sites")}
    full["inventory_resolved_by"] = {
        "new_code_unit_capacity_refs": "layer2 g2_newcode_2610",
        "capacity_bound_checks": "layer1 stock oracle (.text) + layer3 g2_bounds_2610",
        "new_perunit_bss_sized_1200": "layer3 g2_state_2610",
    }
    return candidate, full


def create_copy(source: Path, destination: Path) -> dict[str, Any]:
    """Copy-only writer (exclusive create): emits a candidate or fails closed.

    Never overwrites the input.  Verifies the written bytes rebuild-equal to
    the candidate before returning.
    """
    if destination.resolve() == source.resolve():
        raise ValueError("refusing to overwrite the input EXE")
    data = source.read_bytes()
    candidate, report = build_candidate(data)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb") as handle:
        handle.write(candidate)
    if destination.read_bytes() != candidate:
        raise ValueError("candidate write verification failed")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    inv = sub.add_parser("inventory", help="print the fail-closed operand inventory")
    inv.add_argument("source", type=Path)
    inv.add_argument("--json", type=Path)
    create = sub.add_parser("create-copy", help="emit a candidate (fails closed today)")
    create.add_argument("source", type=Path)
    create.add_argument("destination", type=Path)
    args = parser.parse_args()
    if args.command == "inventory":
        report = g2_scan.build_inventory(args.source.read_bytes()).to_report()
        if args.json:
            args.json.write_text(json.dumps(report, indent=2))
        keys = ("input_sha256", "total_sites", "unresolved_count", "release_status")
        print(json.dumps({k: report[k] for k in keys}, indent=2))
    else:
        try:
            print(json.dumps(create_copy(args.source, args.destination), indent=2))
        except G2BuildBlocked as exc:
            print(str(exc))
            raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
