#!/usr/bin/env python3
"""lap224 middle: independent review probe for the lap223 G1 R6-B repair.

Written from scratch for this review.  It imports no repository test helper and
reuses no lap222/lap223 fixture.  It answers three questions:

1. Is the absolute ``count>=2`` gate really gone from the executed drag path?
2. Does ``_g1_selection_responded`` credit the lap204 identity-only response?
3. Can a *degraded or regressed* observation reach ``PASS`` through the new
   predicate?  Degradation is produced by driving the real reader
   ``_read_g1_selection_evidence`` with synthetic memory, not by hand-writing
   the dict the predicate consumes.
"""

from __future__ import annotations

import importlib.util
import inspect
import json
import struct
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "tools" / "runtime_env.py"
SPEC = importlib.util.spec_from_file_location("runtime_env_lap224", SOURCE)
assert SPEC and SPEC.loader
rt = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = rt
SPEC.loader.exec_module(rt)


COUNT_ADDR = rt.G1_SELECTION_COUNT_ADDRESS
SLOT_ADDR = rt.G1_SELECTION_FIRST_SLOT_ADDRESS
EXISTS = rt.G1_UNIT_EXISTS_BASE_ADDRESS
BASE = rt.G1_UNIT_BASE_ADDRESS
STRIDE = rt.G1_UNIT_STRIDE
TYPE_OFF = rt.G1_UNIT_TYPE_OFFSET


def make_reader(count: int, slot: int, active: int, unit_type: int, *, raise_on_type: bool = False):
    """Synthetic process memory for one selected-unit observation."""

    def read_memory(address: int, size: int) -> bytes:
        if address == COUNT_ADDR:
            return struct.pack("<i", count)
        if address == SLOT_ADDR:
            return struct.pack("<h", slot)
        if address == EXISTS + slot * 2:
            return struct.pack("<h", active)
        if address == BASE + slot * STRIDE + TYPE_OFF:
            if raise_on_type:
                raise OSError(5, "process_vm_readv: transient read failure")
            return struct.pack("<B", unit_type)
        raise AssertionError(f"probe did not model address 0x{address:08X}")

    return read_memory


def observe(**kwargs: Any) -> dict[str, Any]:
    return rt._read_g1_selection_evidence(make_reader(**kwargs))


HEALTHY_BEFORE = dict(count=1, slot=1199, active=1, unit_type=70)

CASES: list[dict[str, Any]] = [
    {
        "id": "C1_count_change",
        "intent": "engine responded: band select grew the selection",
        "before": HEALTHY_BEFORE,
        "after": dict(count=3, slot=1199, active=1, unit_type=70),
        "should_pass": True,
    },
    {
        "id": "C2_identity_change_lap204",
        "intent": "lap204 form: count 1->1 but the selected unit really changed",
        "before": HEALTHY_BEFORE,
        "after": dict(count=1, slot=1198, active=1, unit_type=21),
        "should_pass": True,
    },
    {
        "id": "C3_no_effect",
        "intent": "no engine response at all; must stay FAIL/timeout",
        "before": HEALTHY_BEFORE,
        "after": dict(HEALTHY_BEFORE),
        "should_pass": False,
    },
    {
        "id": "C4_after_read_failure",
        "intent": "observation lost after the drag (transient read failure)",
        "before": HEALTHY_BEFORE,
        "after": dict(count=1, slot=1199, active=1, unit_type=70, raise_on_type=True),
        "should_pass": False,
    },
    {
        "id": "C5_pool_corruption",
        "intent": "selected slot went inactive: pool/state damage, not a selection response",
        "before": HEALTHY_BEFORE,
        "after": dict(count=1, slot=1199, active=0, unit_type=70),
        "should_pass": False,
    },
    {
        "id": "C6_selection_lost",
        "intent": "selection regressed 1->0; strictly less evidence than before",
        "before": HEALTHY_BEFORE,
        "after": dict(count=0, slot=1199, active=1, unit_type=70),
        "should_pass": False,
    },
    {
        "id": "C7_degraded_baseline_recovers",
        "intent": "before was already unreadable; the 'change' is the reader healing",
        "before": dict(count=1, slot=1199, active=1, unit_type=70, raise_on_type=True),
        "after": dict(HEALTHY_BEFORE),
        "should_pass": False,
    },
]


def main() -> int:
    source = inspect.getsource(rt._g1_run_input_sequence)
    results: list[dict[str, Any]] = []
    for case in CASES:
        before = observe(**case["before"])
        after = observe(**case["after"])
        responded = rt._g1_selection_responded(before, after)
        results.append({
            "id": case["id"],
            "intent": case["intent"],
            "before_observation": {k: before.get(k) for k in
                                   ("count", "selected_slot", "selected_type",
                                    "selected_type_provenance")},
            "after_observation": {k: after.get(k) for k in
                                  ("count", "selected_slot", "selected_type",
                                   "selected_type_provenance")},
            "responded": responded,
            "expected_pass": case["should_pass"],
            "verdict": "AGREES" if responded == case["should_pass"] else "DEFECT",
        })

    report = {
        "lap": 224,
        "role": "middle (claude-opus-5/high) independent review of lap223 R6-B",
        "source_file": str(SOURCE.relative_to(ROOT)),
        "source_sha256_recorded_by_work": (
            "9e607407b10b593710406b4beb250386640c118e4655a5de46a7a1954d8c5e80"
        ),
        "static_checks": {
            "absolute_count_ge_2_in_executed_path": 'int(item.get("count", 0)) >= 2' in source,
            "drag_wait_uses_responded": "_g1_selection_responded(drag_before, item)" in source,
            "drag_final_gate_uses_responded": (
                "drag_pass = _g1_selection_responded(drag_before, drag_after)" in source
            ),
            "unit_select_gate_unchanged": 'int(item.get("count", 0)) >= 1' in source,
        },
        "cases": results,
        "defects": [r["id"] for r in results if r["verdict"] == "DEFECT"],
        "game_runs": 0,
    }
    out = Path(__file__).with_name(Path(__file__).stem.replace("_probe", "_report") + ".json")
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
