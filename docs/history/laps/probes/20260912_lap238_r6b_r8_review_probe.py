"""lap238 middle-tier review probe for G1 R6-B-R8 read-error coverage.

Independently re-derives the classification of `_wait_state` over the full
16-case error mask of a 4-poll window, plus the effect-observed return path.
Game-free: the reader is a fake-clock sequence, no process memory is read and
no product asset is touched. The report is written with exclusive creation so
an existing report is never overwritten (R6-B-R7 rule).
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from pathlib import Path
from typing import Any
from unittest import mock

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "tools"))

import runtime_env  # noqa: E402

BEFORE = {"count": 1, "selected_slot": 1199, "selected_type": 70}
RESPONDED = {"count": 2, "selected_slot": 1198, "selected_type": 21}


def _run(err_mask: tuple[int, ...], *, respond_last: bool = False) -> tuple[str, dict[str, Any]]:
    clock = [0.0]
    reads: list[Any] = []
    for index, failed in enumerate(err_mask):
        if failed:
            reads.append(OSError("transient selected-unit read failed"))
        elif respond_last and index == len(err_mask) - 1:
            reads.append(dict(RESPONDED))
        else:
            reads.append(dict(BEFORE))

    def reader(_detailed: bool) -> dict[str, Any]:
        item = reads.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item

    observation: dict[str, Any] = {}
    with mock.patch.object(runtime_env.time, "monotonic", lambda: clock[0]), \
         mock.patch.object(runtime_env.time, "sleep",
                           lambda seconds: clock.__setitem__(0, clock[0] + seconds)):
        try:
            runtime_env._wait_state(
                reader,
                lambda item: runtime_env._g1_selection_responded(
                    BEFORE, item, diagnostics=observation),
                started=0.0, timeout=10.0, message="selection did not change",
                stage="drag_select", stage_budget=1.0, stage_started=0.0,
                wait_observation=observation,
            )
        except runtime_env._G1WaitTimeout as exc:
            return exc.classification, exc.observation
        return "RETURNED_EFFECT_OBSERVED", observation


def _expected(err_mask: tuple[int, ...]) -> str:
    """The contract the lap237 work tier declared, restated independently."""
    errors = sum(err_mask)
    if errors > 0 and (errors == len(err_mask) or err_mask[-1]):
        return "UNKNOWN_STATE_READ_FAILURE"
    if errors / len(err_mask) > 0.25:
        return "UNKNOWN_STATE_READ_COVERAGE"
    return "FAIL_NO_EFFECT"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    cases: list[dict[str, Any]] = []
    for mask in itertools.product([0, 1], repeat=4):
        classification, observation = _run(mask)
        expected = _expected(mask)
        selection = observation.get("selection_observation")
        cases.append({
            "error_mask": "".join(str(bit) for bit in mask),
            "read_error_count": observation["read_error_count"],
            "poll_attempt_count": observation["poll_attempt_count"],
            "read_error_ratio": observation["read_error_ratio"],
            "threshold_ratio": observation["read_error_coverage_threshold_ratio"],
            "exceeds_threshold": observation["read_error_coverage_exceeds_threshold"],
            "classification": classification,
            "expected": expected,
            "selection_status": selection.get("status") if isinstance(selection, dict) else None,
            "agrees": classification == expected,
            "is_pass": classification == "PASS",
        })

    effect_cases = []
    for mask in [(0, 0, 0, 0), (1, 0, 0, 0), (1, 1, 1, 0)]:
        classification, observation = _run(mask, respond_last=True)
        effect_cases.append({
            "error_mask": "".join(str(bit) for bit in mask),
            "classification": classification,
            "read_error_ratio": observation["read_error_ratio"],
            "coverage_gated": classification != "RETURNED_EFFECT_OBSERVED",
        })

    source = (REPO / "tools" / "runtime_env.py").read_bytes()
    report = {
        "schema": "lap238-r6b-r8-review-1",
        "source_sha256": hashlib.sha256(source).hexdigest(),
        "threshold_constant": runtime_env.G1_INPUT_MAX_READ_ERROR_RATIO,
        "cases": cases,
        "mismatches": [case["error_mask"] for case in cases if not case["agrees"]],
        "pass_routes_in_no_effect_matrix": [
            case["error_mask"] for case in cases if case["is_pass"]],
        "effect_observed_cases": effect_cases,
        "verdict": "AGREES" if all(case["agrees"] for case in cases)
        and not any(case["is_pass"] for case in cases) else "DEFECT",
    }
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    print(report["verdict"], report["source_sha256"])
    return 0 if report["verdict"] == "AGREES" else 2


if __name__ == "__main__":
    raise SystemExit(main())
