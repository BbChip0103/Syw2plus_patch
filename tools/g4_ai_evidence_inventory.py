#!/usr/bin/env python3
"""Validate preserved original-game free-battle AI evidence without launching it."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


EXPECTED = {
    "combat": "454cadd415fa08bbb06bd50889bb11de73407f4460017c6c89408ed88d0e3258",
    "series": "84ae1910dd1336837ef9448bf9b1b73737db0b1033718926e01b66411729e570",
    "controller": "71fb32a2b955331b05b51cc3d63cb03db9fe9efb6c6ba08228066e0f25b9b2b2",
    "capture_tool": "c1948faffccfc3721a1d88c8862535bf9dfb2ca122e7e1c67061fad617a17a21",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_report(paths: dict[str, Path]) -> dict[str, Any]:
    hashes = {name: _sha256(path) for name, path in paths.items()}
    pinned = {name: hashes[name] == EXPECTED[name] for name in EXPECTED}
    combat = json.loads(paths["combat"].read_text(encoding="utf-8"))
    series = json.loads(paths["series"].read_text(encoding="utf-8"))
    controller = json.loads(paths["controller"].read_text(encoding="utf-8"))
    summary = combat.get("summary", {})
    metric_available = (
        all(pinned.values())
        and summary.get("sample_count", 0) > 1
        and summary.get("hp_decrease_same_unit", 0) > 0
        and summary.get("min_faction_gap") == 0
        and isinstance(series, list) and len(series) > 1
        and controller.get("sample_count", 0) > 1
    )
    return {
        "schema": "syw2plus.g4.ai_evidence_inventory.v1",
        "observational_only": True,
        "source_repository_read_only": True,
        "classification": (
            "BASELINE_METRIC_AVAILABLE_PATCH_BLOCKED"
            if metric_available else "BASELINE_EVIDENCE_INVALID"
        ),
        "activation_allowed": False,
        "hashes": {
            name: {"path": str(paths[name]), "sha256": hashes[name],
                   "expected": EXPECTED[name], "pinned": pinned[name]}
            for name in EXPECTED
        },
        "original_behavior_metrics": {
            "combat_sample_count": summary.get("sample_count"),
            "slot_disappearances": summary.get("slot_disappearances"),
            "hp_decrease_events": summary.get("hp_decrease_events"),
            "hp_decrease_same_unit": summary.get("hp_decrease_same_unit"),
            "low_hp_disappearances": summary.get("low_hp_disappearances"),
            "min_faction_gap": summary.get("min_faction_gap"),
            "production_series_samples": len(series) if isinstance(series, list) else None,
            "production_series_last_t": series[-1].get("t") if isinstance(series, list) and series else None,
            "production_series_last_count": series[-1].get("count") if isinstance(series, list) and series else None,
            "controller_sample_count": controller.get("sample_count"),
            "controller_transition_count": len(controller.get("transitions", [])),
        },
        "what_this_proves": [
            "The original free-battle AI has measurable production, movement/contact and combat outcomes.",
            "A behavioral metric/oracle can be defined; G4 AI is not blocked by total absence of original evidence.",
        ] if metric_available else [],
        "remaining_patch_gates": [
            "fresh reproducible original run under this patch repository harness",
            "difficulty-setting identity and at least two fixed scenario fixtures",
            "candidate intervention point with rollback and deterministic/LAN risk analysis",
            "original-vs-candidate repeated comparison and regression thresholds",
        ],
        "conclusion": (
            "Use the preserved evidence to design the first AI benchmark; do not treat it as permission "
            "to patch strategy constants or controller code."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    root = Path(__file__).resolve().parents[1]
    source = root.parent / "Syw2plus_re"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=source)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    capture_root = args.source / "plan_c/verification/captures/original"
    paths = {
        "combat": capture_root / "free_battle_combat_evidence_inmm_0730/combat_evidence.json",
        "series": capture_root / "free_battle_unit_series_inmm_0727/original_unit_series_long240.json",
        "controller": capture_root / "free_battle_controller_opcode_inmm_0730/controller_opcode.json",
        "capture_tool": args.source / "plan_c/tools/capture_ingame_combat_evidence_0730.py",
    }
    report = build_report(paths)
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if report["classification"] == "BASELINE_METRIC_AVAILABLE_PATCH_BLOCKED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
