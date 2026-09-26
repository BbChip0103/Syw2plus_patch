#!/usr/bin/env python3
"""lap226 middle: independent review probe for the lap225 G1-R6-B-R1 repair.

Written for this review.  It imports no repository test helper and reuses no
lap224/lap225 fixture object.  Corrupted observations are produced by driving
the real reader ``_read_g1_selection_evidence`` with synthetic process memory,
never by hand-writing the dict the predicate consumes.

It answers four questions:

1. Do the lap224 defects C4/C5/C7 now fail closed, and are C1~C3 unchanged?
2. Is C6 (count 1->0) still credited, i.e. was R6-B-R2 left untouched?
3. Is the new soundness definition complete for every observation the reader
   can actually emit (including counts the engine can never produce)?
4. Does a corrupted poll keep the wait polling, and does the timeout
   classification describe the *final* observation or any past one?
"""

from __future__ import annotations

import importlib.util
import json
import struct
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "tools" / "runtime_env.py"
SPEC = importlib.util.spec_from_file_location("runtime_env_lap226", SOURCE)
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


def make_reader(count: int, slot: int, active: int, unit_type: int,
                *, raise_on_type: bool = False):
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


HEALTHY = dict(count=1, slot=1199, active=1, unit_type=70)

CASES: list[dict[str, Any]] = [
    {"id": "C1_count_change", "expect": True,
     "intent": "engine responded: band select grew the selection",
     "before": HEALTHY, "after": dict(count=3, slot=1199, active=1, unit_type=70)},
    {"id": "C2_identity_change_lap204", "expect": True,
     "intent": "lap204 form: count 1->1 but the selected unit really changed",
     "before": HEALTHY, "after": dict(count=1, slot=1198, active=1, unit_type=21)},
    {"id": "C3_no_effect", "expect": False,
     "intent": "no engine response at all; must stay FAIL/timeout",
     "before": HEALTHY, "after": dict(HEALTHY)},
    {"id": "C4_after_read_failure", "expect": False,
     "intent": "lap224 C4: observation lost after the drag (transient read failure)",
     "before": HEALTHY,
     "after": dict(count=1, slot=1199, active=1, unit_type=70, raise_on_type=True)},
    {"id": "C5_pool_corruption", "expect": False,
     "intent": "lap224 C5: selected slot went inactive (pool/state damage)",
     "before": HEALTHY, "after": dict(count=1, slot=1199, active=0, unit_type=70)},
    {"id": "C6_selection_lost", "expect": True,
     "intent": "lap224 C6 = deferred R6-B-R2; must still be credited, unchanged",
     "before": HEALTHY, "after": dict(count=0, slot=1199, active=1, unit_type=70)},
    {"id": "C7_degraded_baseline_recovers", "expect": False,
     "intent": "lap224 C7: baseline itself was unreadable; reader healing is not a response",
     "before": dict(count=1, slot=1199, active=1, unit_type=70, raise_on_type=True),
     "after": dict(HEALTHY)},
    # New for lap226: counts the engine cannot produce.
    {"id": "D1_negative_count_after", "expect": False,
     "intent": "corrupt/torn signed read yields count=-1; impossible state, not a response",
     "before": HEALTHY, "after": dict(count=-1, slot=1199, active=1, unit_type=70)},
    {"id": "D2_negative_count_before", "expect": False,
     "intent": "baseline itself is an impossible count=-1; comparison has no sound base",
     "before": dict(count=-1, slot=1199, active=1, unit_type=70), "after": dict(HEALTHY)},
    {"id": "D3_overflow_count_after", "expect": False,
     "intent": "count above the slot range: reader folds to UNKNOWN type, must fail closed",
     "before": HEALTHY, "after": dict(count=0x7FFFFFFF, slot=1199, active=1, unit_type=70)},
    {"id": "D4_type_zero_after", "expect": False,
     "intent": "unit type 0 (unsupported) after the drag is damage, not a response",
     "before": HEALTHY, "after": dict(count=1, slot=1199, active=1, unit_type=0)},
]

results: list[dict[str, Any]] = []
for case in CASES:
    before = observe(**case["before"])
    after = observe(**case["after"])
    diagnostics: dict[str, Any] = {}
    responded = rt._g1_selection_responded(before, after, diagnostics=diagnostics)
    results.append({
        "id": case["id"], "intent": case["intent"],
        "expected_responded": case["expect"], "observed_responded": responded,
        "verdict": "AGREES" if responded == case["expect"] else "DEFECT",
        "before_observation": {k: before.get(k) for k in
                               ("count", "selected_slot", "selected_type",
                                "selected_type_provenance")},
        "after_observation": {k: after.get(k) for k in
                              ("count", "selected_slot", "selected_type",
                               "selected_type_provenance")},
        "diagnostics_status": diagnostics.get("selection_observation", {}).get("status"),
    })


def drive_wait(sequence: list[dict[str, Any]], before: dict[str, Any]) -> dict[str, Any]:
    """Run the real _wait_state over a fixed poll sequence on a fake clock."""

    clock = [0.0]
    real_monotonic, real_sleep = rt.time.monotonic, rt.time.sleep
    rt.time.monotonic = lambda: clock[0]                      # type: ignore[assignment]
    rt.time.sleep = lambda s: clock.__setitem__(0, clock[0] + s)  # type: ignore[assignment]
    polls: list[int] = [0]
    observation: dict[str, Any] = {}

    def read_state(_detailed: bool) -> dict[str, Any]:
        index = min(polls[0], len(sequence) - 1)
        polls[0] += 1
        return sequence[index]

    try:
        returned = rt._wait_state(
            read_state,
            lambda item: rt._g1_selection_responded(before, item, diagnostics=observation),
            started=0.0, timeout=30.0, message="drag response was not observed",
            stage="drag_select", stage_budget=1.0, stage_started=0.0,
            wait_observation=observation,
        )
        outcome = {"outcome": "RESPONDED", "classification": None,
                   "returned_count": returned.get("count"),
                   "returned_type": returned.get("selected_type")}
    except rt._G1WaitTimeout as exc:
        outcome = {"outcome": "TIMEOUT", "classification": exc.classification,
                   "returned_count": None, "returned_type": None}
    finally:
        rt.time.monotonic = real_monotonic                     # type: ignore[assignment]
        rt.time.sleep = real_sleep                             # type: ignore[assignment]
    outcome.update({
        "poll_count": observation.get("poll_count"),
        "last_poll_corrupted": observation.get(
            "selection_observation", {}).get("status"),
    })
    return outcome


healthy_before = observe(**HEALTHY)
corrupt_obs = observe(count=1, slot=1199, active=1, unit_type=70, raise_on_type=True)
sound_unchanged = observe(**HEALTHY)
sound_changed = observe(count=1, slot=1198, active=1, unit_type=21)

waits = [
    {"id": "W1_all_corrupt", "expect_classification": "UNKNOWN_SELECTION_OBSERVATION_CORRUPTED",
     "intent": "every poll corrupted: wait must keep polling and time out as CORRUPTED",
     "result": drive_wait([corrupt_obs], healthy_before)},
    {"id": "W2_corrupt_then_response", "expect_classification": None,
     "intent": "corruption must not end the window; a later real response still wins",
     "result": drive_wait([corrupt_obs, corrupt_obs, sound_changed], healthy_before)},
    {"id": "W3_corrupt_then_sound_no_effect",
     "expect_classification": "FAIL_NO_EFFECT",
     "intent": "one transient corrupt poll, then sound unchanged polls: the run really "
               "had no effect, so a hard FAIL must not be laundered into UNKNOWN",
     "result": drive_wait([corrupt_obs] + [sound_unchanged] * 8, healthy_before)},
]
for item in waits:
    got = item["result"]["classification"]
    item["verdict"] = "AGREES" if got == item["expect_classification"] else "DEFECT"

report = {
    "lap": 226, "role": "middle", "target": "G1-R6-B-R1 (lap225)",
    "source_sha256": rt.hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    "predicate_cases": results,
    "wait_cases": waits,
    "summary": {
        "predicate_agrees": sum(1 for r in results if r["verdict"] == "AGREES"),
        "predicate_defects": [r["id"] for r in results if r["verdict"] == "DEFECT"],
        "wait_defects": [w["id"] for w in waits if w["verdict"] == "DEFECT"],
    },
}
out = Path(__file__).with_name(
    "20260912_lap226_r6b_r1_review_report.json")
out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
for r in results:
    print(f"{r['verdict']:7} {r['id']:32} responded={r['observed_responded']} "
          f"expected={r['expected_responded']} diag={r['diagnostics_status']}")
for w in waits:
    print(f"{w['verdict']:7} {w['id']:32} {w['result']}")
