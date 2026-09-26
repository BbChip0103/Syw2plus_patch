"""lap232 middle-tier independent probe for G1-R6-B-R6 (`_wait_state` read-failure closure).

The probe is deliberately independent of `tests/test_runtime_env.py`: it restates the
lap230 C5 contract plus the surrounding invariants R6-B-R2/R3/R4 must keep, then compares
observed behaviour against the expectation for each case.

R6-B-R7 note: the output path is NOT hardcoded.  It defaults to a lap-unique name and
refuses to overwrite an existing report unless --force is given, so re-runs cannot
destroy earlier lap evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from tools import compare_g1_stage_b  # noqa: E402
from tools import runtime_env  # noqa: E402

DEFAULT_OUTPUT = Path(__file__).with_name("20260912_lap232_r6b_r6_review_report.json")


class FakeClock:
    """Deterministic monotonic clock; `sleep` advances it."""

    def __init__(self, start: float = 0.0) -> None:
        self.now = start

    def monotonic(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.now += seconds


def run_wait(
    reader: Callable[[bool], dict[str, Any]],
    predicate: Callable[[dict[str, Any]], bool],
    *,
    clock_start: float = 0.0,
    started: float = 0.0,
    timeout: float = 10.0,
    stage: str | None = "drag_select",
    stage_budget: float | None = 1.0,
    stage_started: float | None = 0.0,
    wait_observation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Call `_wait_state` under a fake clock and return a structured outcome."""

    clock = FakeClock(clock_start)
    real_monotonic, real_sleep = runtime_env.time.monotonic, runtime_env.time.sleep
    runtime_env.time.monotonic = clock.monotonic  # type: ignore[assignment]
    runtime_env.time.sleep = clock.sleep  # type: ignore[assignment]
    observation = wait_observation if wait_observation is not None else {}
    try:
        value = runtime_env._wait_state(
            reader, predicate, started, timeout, "probe wait",
            stage=stage, stage_budget=stage_budget, stage_started=stage_started,
            wait_observation=observation,
        )
    except runtime_env._G1WaitTimeout as exc:
        return {
            "outcome": "timeout",
            "classification": exc.classification,
            "observation": exc.observation,
            "observation_is_caller_dict": exc.observation is observation,
            "last": exc.last,
        }
    except runtime_env.RuntimeSafetyError as exc:
        return {"outcome": "safety_error", "message": str(exc), "observation": observation}
    else:
        return {"outcome": "returned", "value": value, "observation": observation}
    finally:
        runtime_env.time.monotonic = real_monotonic  # type: ignore[assignment]
        runtime_env.time.sleep = real_sleep  # type: ignore[assignment]


def sequence_reader(items: list[Any]) -> Callable[[bool], dict[str, Any]]:
    """Replay `items`; an Exception instance is raised, a dict is returned.

    The final item repeats forever so the poll window decides the poll count.
    """

    state = {"i": 0}

    def read(_detailed: bool) -> dict[str, Any]:
        index = min(state["i"], len(items) - 1)
        state["i"] += 1
        item = items[index]
        if isinstance(item, BaseException):
            raise item
        return dict(item)

    return read


SOUND = {"count": 1, "selected_slot": 1199, "selected_type": 70}
CORRUPT = {"count": 2, "selected_slot": None, "selected_type": "UNKNOWN"}
NEGATIVE = {"count": -1, "selected_slot": 1199, "selected_type": 70}
EMPTY = {"count": 0, "selected_slot": None, "selected_type": "UNKNOWN"}


def selection_predicate(before: dict[str, Any], diagnostics: dict[str, Any]):
    def predicate(item: dict[str, Any]) -> bool:
        return runtime_env._g1_selection_responded(before, item, diagnostics=diagnostics)

    return predicate


def cases() -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []

    def add(name: str, expected: str, observed: str, detail: dict[str, Any]) -> None:
        results.append({
            "case": name,
            "expected": expected,
            "observed": observed,
            "verdict": "AGREES" if expected == observed else "DEFECT",
            "detail": detail,
        })

    # --- C5a: no successful observation at all -------------------------------
    out = run_wait(sequence_reader([OSError("read failed")]), lambda _i: False)
    obs = out.get("observation", {})
    add(
        "C5a_all_reads_fail",
        "UNKNOWN_STATE_READ_FAILURE|polls=0|errors>0|no_selection_observation",
        "{}|polls={}|errors{}|{}".format(
            out.get("classification"),
            obs.get("poll_count"),
            ">0" if int(obs.get("read_error_count", 0)) > 0 else "=0",
            "no_selection_observation" if "selection_observation" not in obs
            else "selection_observation_present",
        ),
        {"poll_attempt_count": obs.get("poll_attempt_count"),
         "read_error_count": obs.get("read_error_count"),
         "first_read_error_provenance": obs.get("first_read_error_provenance"),
         "last_read_error_provenance": obs.get("last_read_error_provenance")},
    )

    # --- C5b: sound polls then an unreadable tail ----------------------------
    diagnostics: dict[str, Any] = {}
    out = run_wait(
        sequence_reader([SOUND, SOUND, OSError("process gone")]),
        selection_predicate(SOUND, diagnostics),
        wait_observation=diagnostics,
    )
    obs = out.get("observation", {})
    selection = obs.get("selection_observation", {})
    # `_G1WaitTimeout` shallow-copies the observation, so identity is expected to
    # differ; what matters is that the caller's own dict (which `stage_wait`
    # stores on the stage entry) also shows the relabelled status.
    caller_status = diagnostics.get("selection_observation", {}).get("status")
    add(
        "C5b_sound_then_unreadable_tail",
        "UNKNOWN_STATE_READ_FAILURE|status=UNAVAILABLE|polls<attempts|caller_status=UNAVAILABLE",
        "{}|status={}|{}|caller_status={}".format(
            out.get("classification"),
            selection.get("status"),
            "polls<attempts" if int(obs.get("poll_count", 0)) < int(obs.get("poll_attempt_count", 0))
            else "polls>=attempts",
            caller_status,
        ),
        {"poll_count": obs.get("poll_count"),
         "poll_attempt_count": obs.get("poll_attempt_count"),
         "read_error_count": obs.get("read_error_count"),
         "stale_last": out.get("last")},
    )

    # --- exception-type coverage --------------------------------------------
    for label, exc in (
        ("value_error", ValueError("bad struct payload")),
        ("struct_error", struct.error("unpack requires a buffer")),
    ):
        out = run_wait(sequence_reader([SOUND, exc]), lambda _i: False)
        obs = out.get("observation", {})
        add(
            f"exception_type_{label}",
            "UNKNOWN_STATE_READ_FAILURE|errors>0",
            "{}|errors{}".format(
                out.get("classification"),
                ">0" if int(obs.get("read_error_count", 0)) > 0 else "=0",
            ),
            {"first_read_error_provenance": obs.get("first_read_error_provenance")},
        )

    # --- read errors in the middle, final observation sound ------------------
    diagnostics = {}
    out = run_wait(
        sequence_reader([SOUND, OSError("transient"), SOUND, SOUND]),
        selection_predicate(SOUND, diagnostics),
        wait_observation=diagnostics,
    )
    obs = out.get("observation", {})
    selection = obs.get("selection_observation", {})
    add(
        "readable_tail_keeps_hard_fail",
        "FAIL_NO_EFFECT|status=SOUND|errors=1",
        "{}|status={}|errors={}".format(
            out.get("classification"), selection.get("status"), obs.get("read_error_count"),
        ),
        {"note": "pre-existing hard-FAIL semantics must survive when the final read succeeds",
         "poll_count": obs.get("poll_count"),
         "poll_attempt_count": obs.get("poll_attempt_count")},
    )

    # --- corrupted final observation after a read error ----------------------
    diagnostics = {}
    out = run_wait(
        sequence_reader([OSError("transient"), CORRUPT]),
        selection_predicate(SOUND, diagnostics),
        wait_observation=diagnostics,
    )
    obs = out.get("observation", {})
    selection = obs.get("selection_observation", {})
    add(
        "corrupted_tail_after_read_error",
        "UNKNOWN_SELECTION_OBSERVATION_CORRUPTED|status=CORRUPTED",
        "{}|status={}".format(out.get("classification"), selection.get("status")),
        {"corrupted_poll_count": selection.get("corrupted_poll_count"),
         "read_error_count": obs.get("read_error_count")},
    )

    # --- corruption history survives the UNAVAILABLE relabel -----------------
    diagnostics = {}
    out = run_wait(
        sequence_reader([CORRUPT, OSError("process gone")]),
        selection_predicate(SOUND, diagnostics),
        wait_observation=diagnostics,
    )
    obs = out.get("observation", {})
    selection = obs.get("selection_observation", {})
    add(
        "corruption_history_preserved_under_unavailable",
        "UNKNOWN_STATE_READ_FAILURE|status=UNAVAILABLE|corrupted>=1|provenance_kept",
        "{}|status={}|corrupted{}|{}".format(
            out.get("classification"),
            selection.get("status"),
            ">=1" if int(selection.get("corrupted_poll_count", 0)) >= 1 else "=0",
            "provenance_kept" if selection.get("first_corruption_provenance") is not None
            and selection.get("last_corruption_provenance") is not None else "provenance_lost",
        ),
        {"corrupted_poll_count": selection.get("corrupted_poll_count"),
         "before_sound": selection.get("before_sound"),
         "after_sound": selection.get("after_sound")},
    )

    # --- precedence: budget exhaustion outranks read failure -----------------
    out = run_wait(
        sequence_reader([OSError("read failed")]), lambda _i: False,
        timeout=1.0, stage_budget=2.0,
    )
    obs = out.get("observation", {})
    add(
        "precedence_budget_exhausted",
        "UNKNOWN_BUDGET_EXHAUSTED|errors>0",
        "{}|errors{}".format(
            out.get("classification"),
            ">0" if int(obs.get("read_error_count", 0)) > 0 else "=0",
        ),
        {"note": "read evidence must still be preserved in the observation",
         "read_error_count": obs.get("read_error_count")},
    )

    # --- precedence: window truncation outranks read failure -----------------
    out = run_wait(
        sequence_reader([OSError("read failed")]), lambda _i: False,
        clock_start=8.0, timeout=20.0, stage_budget=10.0, stage_started=0.0,
    )
    obs = out.get("observation", {})
    add(
        "precedence_window_truncated",
        "UNKNOWN_OBSERVATION_WINDOW_TRUNCATED|errors>0",
        "{}|errors{}".format(
            out.get("classification"),
            ">0" if int(obs.get("read_error_count", 0)) > 0 else "=0",
        ),
        {"read_error_count": obs.get("read_error_count"),
         "window_truncated": obs.get("window_truncated")},
    )

    # --- zero poll attempts must never be a hard FAIL ------------------------
    out = run_wait(
        sequence_reader([SOUND]), lambda _i: False,
        clock_start=1.5, timeout=20.0, stage_budget=1.0, stage_started=0.0,
    )
    obs = out.get("observation", {})
    add(
        "zero_attempts_not_hard_fail",
        "not_FAIL_NO_EFFECT|attempts=0",
        "{}|attempts={}".format(
            "not_FAIL_NO_EFFECT" if out.get("classification") != "FAIL_NO_EFFECT"
            else "FAIL_NO_EFFECT",
            obs.get("poll_attempt_count"),
        ),
        {"classification": out.get("classification"),
         "poll_count": obs.get("poll_count")},
    )

    # --- PASS path is untouched ----------------------------------------------
    diagnostics = {}
    out = run_wait(
        sequence_reader([OSError("transient"), {"count": 2, "selected_slot": 1198,
                                                "selected_type": 21}]),
        selection_predicate(SOUND, diagnostics),
        wait_observation=diagnostics,
    )
    obs = out.get("observation", {})
    selection = obs.get("selection_observation", {})
    add(
        "pass_path_unchanged",
        "returned|status=SOUND|errors=1",
        "{}|status={}|errors={}".format(
            out.get("outcome"), selection.get("status"), obs.get("read_error_count"),
        ),
        {"value": out.get("value"), "poll_count": obs.get("poll_count")},
    )

    # --- non-G1 callers keep the RuntimeSafetyError contract ------------------
    out = run_wait(
        sequence_reader([OSError("read failed")]), lambda _i: False,
        stage=None, stage_budget=None, stage_started=None, timeout=1.0,
    )
    add(
        "non_g1_caller_raises_safety_error",
        "safety_error",
        str(out.get("outcome")),
        {"message": out.get("message")},
    )

    # --- R6-B-R2/R3/R4 predicate semantics are unchanged ----------------------
    for label, before, after, expected_responded, expected_status in (
        ("count_1_to_0_unchanged_r6b_r2_dispute", SOUND, EMPTY, True, "SOUND"),
        ("negative_count_still_corrupted", SOUND, NEGATIVE, False, "CORRUPTED"),
        ("non_int_count_still_corrupted", SOUND, {"count": "1", "selected_slot": 1199,
                                                  "selected_type": 70}, False, "CORRUPTED"),
        ("identity_change_still_responds", SOUND, {"count": 1, "selected_slot": 1198,
                                                   "selected_type": 21}, True, "SOUND"),
    ):
        diagnostics = {}
        responded = runtime_env._g1_selection_responded(before, after, diagnostics=diagnostics)
        status = diagnostics["selection_observation"]["status"]
        add(
            f"semantics_{label}",
            f"responded={expected_responded}|status={expected_status}",
            f"responded={responded}|status={status}",
            {"before": before, "after": after},
        )

    # --- end to end: a read-failure stage must never compare as PASS ---------
    def unit_select_stage(result: str, after: dict[str, Any]) -> dict[str, Any]:
        return {
            "tag": "unit_select",
            "content": [410, 270],
            "before": {"selection": dict(SOUND)},
            "after": after,
            "result": result,
        }

    baseline_stage = unit_select_stage(
        "PASS", {"selection": {"count": 2, "selected_slot": 1198, "selected_type": 21}},
    )
    for label, stale_last in (
        ("stale_identical", dict(SOUND)),
        ("stale_looks_like_a_change", {"count": 2, "selected_slot": 1198, "selected_type": 21}),
    ):
        candidate_stage = unit_select_stage(
            "UNKNOWN_STATE_READ_FAILURE",
            {"wait": "not observed", "last": stale_last},
        )
        report = compare_g1_stage_b._stage_report(
            "unit_select", baseline_stage, candidate_stage,
        )
        add(
            f"comparator_read_failure_not_pass_{label}",
            "not_PASS",
            "PASS" if report.get("status") == "PASS" else "not_PASS",
            {"status": report.get("status"), "reason": report.get("reason"),
             "source_results": report.get("source_results")},
        )

    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--force", action="store_true",
                        help="allow overwriting an existing report (default: refuse)")
    args = parser.parse_args(argv)
    if args.output.exists() and not args.force:
        print(f"refusing to overwrite existing evidence: {args.output}")
        return 2

    results = cases()
    source = Path(runtime_env.__file__).read_bytes()
    report = {
        "probe": Path(__file__).name,
        "lap": 232,
        "target": "G1-R6-B-R6",
        "source_sha256": hashlib.sha256(source).hexdigest(),
        "totals": {
            "cases": len(results),
            "agrees": sum(1 for item in results if item["verdict"] == "AGREES"),
            "defects": sum(1 for item in results if item["verdict"] == "DEFECT"),
        },
        "cases": results,
    }
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                           encoding="utf-8")
    for item in results:
        print(f"{item['verdict']:8} {item['case']}: expected={item['expected']} "
              f"observed={item['observed']}")
    print(json.dumps(report["totals"]))
    return 0 if report["totals"]["defects"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
