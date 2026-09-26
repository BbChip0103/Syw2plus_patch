from __future__ import annotations

import json
from pathlib import Path

import tools.g4_ai_evidence_inventory as inventory


def _fixtures(tmp_path: Path) -> dict[str, Path]:
    paths = {name: tmp_path / name for name in inventory.EXPECTED}
    paths["combat"].write_text(json.dumps({"summary": {
        "sample_count": 2, "slot_disappearances": 1, "hp_decrease_events": 2,
        "hp_decrease_same_unit": 1, "low_hp_disappearances": 1,
        "min_faction_gap": 0,
    }}), encoding="utf-8")
    paths["series"].write_text(json.dumps([
        {"t": 0, "count": 4}, {"t": 240, "count": 41},
    ]), encoding="utf-8")
    paths["controller"].write_text(json.dumps({
        "sample_count": 2, "transitions": [{"from": 1, "to": 3}],
    }), encoding="utf-8")
    paths["capture_tool"].write_text("capture", encoding="utf-8")
    return paths


def test_valid_inventory_exposes_metric_but_blocks_activation(tmp_path: Path, monkeypatch) -> None:
    paths = _fixtures(tmp_path)
    monkeypatch.setattr(inventory, "_sha256", lambda path: inventory.EXPECTED[path.name])

    report = inventory.build_report(paths)

    assert report["classification"] == "BASELINE_METRIC_AVAILABLE_PATCH_BLOCKED"
    assert report["activation_allowed"] is False
    assert report["original_behavior_metrics"]["min_faction_gap"] == 0
    assert report["remaining_patch_gates"]


def test_inventory_fails_when_original_combat_metric_is_empty(tmp_path: Path, monkeypatch) -> None:
    paths = _fixtures(tmp_path)
    paths["combat"].write_text(json.dumps({"summary": {
        "sample_count": 2, "hp_decrease_same_unit": 0, "min_faction_gap": 10,
    }}), encoding="utf-8")
    monkeypatch.setattr(inventory, "_sha256", lambda path: inventory.EXPECTED[path.name])

    report = inventory.build_report(paths)

    assert report["classification"] == "BASELINE_EVIDENCE_INVALID"
    assert report["what_this_proves"] == []
