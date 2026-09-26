#!/usr/bin/env python3
"""lap228 middle: independent review probe for the lap227 G1-R6-B-R3 repair.

Written for this review.  It imports no repository test helper and reuses no
lap224/lap225/lap226/lap227 fixture object.  Wherever the real reader can
produce an observation it is driven with synthetic process memory instead of
hand-written dicts, so the probe measures the shipped path, not a restatement
of it.

R6-B-R3 claims: a negative selection ``count`` must be rejected as a corrupted
observation instead of being laundered into "empty selection".  This probe
answers five questions the lap227 work record did not close:

1. REACHABILITY.  Can the real reader actually emit a negative count without
   raising, i.e. was the repaired branch dead code or a live path?
2. COVERAGE.  Is every negative encoding rejected, including the boundary
   value 0x80000000, not only the -1 the work tier tested?
3. SURGICALITY.  Differentially compare the repaired predicate against a
   faithful re-implementation of the pre-lap227 rule over an exhaustive case
   grid: the observable behaviour must differ *only* where count < 0.
4. PRESERVATION.  Is the deferred R6-B-R2 semantics (count 1 -> 0 counts as a
   response) genuinely untouched, including when the lost-selection poll
   carries stale slot/type bytes?
5. WAIT INTEGRATION.  Does a negative-count poll keep the window polling,
   classify a timeout as CORRUPTED, and still lose to a later real response?

The report path is also guarded before the probe body runs.  An output path
whose parent is missing, not a directory, or not writable is rejected with a
classified exit instead of spending the probe budget and ending in a raw
traceback (R6-B-R10).
"""

from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import argparse
import os
import struct
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "tools" / "runtime_env.py"
SPEC = importlib.util.spec_from_file_location("runtime_env_lap228", SOURCE)
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


def make_reader(raw_count: bytes, slot: int, active: int, unit_type: int,
                *, raise_on_type: bool = False):
    """Serve raw bytes for the count so torn/corrupt dwords can be modelled."""

    def read_memory(address: int, size: int) -> bytes:
        if address == COUNT_ADDR:
            return raw_count
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


def observe_raw(raw_count: bytes, slot: int = 1199, active: int = 1,
                unit_type: int = 70, **kwargs: Any) -> dict[str, Any]:
    return rt._read_g1_selection_evidence(
        make_reader(raw_count, slot, active, unit_type, **kwargs)
    )


def observe(count: int, **kwargs: Any) -> dict[str, Any]:
    return observe_raw(struct.pack("<i", count), **kwargs)


DEFAULT_OUTPUT = Path(__file__).with_name(
    "20260912_lap228_r6b_r3_review_report.json")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=DEFAULT_OUTPUT,
        help="JSON report path (default: the lap228 report path; existing files are protected)",
    )
    return parser.parse_args(argv)


def output_refusal(path: Path) -> str | None:
    """Return a classified output-path error before running the probe body."""

    try:
        if path.exists():
            return f"refusing to overwrite existing evidence: {path}"

        parent = path.parent
        if not parent.is_dir():
            return f"refusing to write evidence: output parent is not a directory: {parent}"
        if not os.access(parent, os.W_OK | os.X_OK):
            return f"refusing to write evidence: output parent is not writable: {parent}"
    except OSError as exc:
        return f"refusing to write evidence: output path unavailable: {path}: {exc}"
    return None


if __name__ == "__main__":
    args = parse_args()
    refusal = output_refusal(args.output)
    if refusal is not None:
        print(refusal)
        raise SystemExit(2)
else:
    args = argparse.Namespace(output=DEFAULT_OUTPUT)


# ---------------------------------------------------------------- Q1 + Q2 ---
# Every dword pattern a corrupted/torn 32-bit read can leave at 0x00899024
# whose signed interpretation is negative.  The reader must survive each one
# (reachability) and the predicate must reject each one (coverage).
NEGATIVE_PATTERNS = [
    ("N1_all_ones", b"\xff\xff\xff\xff", -1,
     "uninitialised / freed memory read back as 0xFFFFFFFF"),
    ("N2_int_min", b"\x00\x00\x00\x80", -2147483648,
     "sign bit only: the most negative count representable"),
    ("N3_torn_high_word", b"\x01\x00\x00\xff", -16777215,
     "torn dword: low word plausible, high word garbage"),
    ("N4_small_negative", b"\xfe\xff\xff\xff", -2,
     "off-by-two underflow of a deselect path"),
    ("N5_ascii_garbage", b"\x41\x42\x43\xc4", -1002917822,
     "pointer/text bytes landing on the count field"),
]

reachability: list[dict[str, Any]] = []
for case_id, raw, expected_signed, intent in NEGATIVE_PATTERNS:
    entry: dict[str, Any] = {"id": case_id, "intent": intent,
                             "raw_hex": raw.hex(),
                             "expected_signed_count": expected_signed}
    try:
        obs = observe_raw(raw)
        entry["reader_raised"] = False
        entry["observation"] = {k: obs.get(k) for k in
                                ("count", "selected_slot", "selected_type",
                                 "selected_type_provenance")}
        entry["count_is_negative"] = isinstance(obs.get("count"), int) and obs["count"] < 0
        diagnostics: dict[str, Any] = {}
        healthy = observe(1)
        responded_after = rt._g1_selection_responded(healthy, obs, diagnostics=diagnostics)
        entry["responded_as_after"] = responded_after
        entry["diag_after"] = dict(diagnostics.get("selection_observation", {}))
        diagnostics_b: dict[str, Any] = {}
        responded_before = rt._g1_selection_responded(
            obs, observe(1, slot=1198, unit_type=21), diagnostics=diagnostics_b,
        )
        entry["responded_as_before"] = responded_before
        entry["diag_before"] = dict(diagnostics_b.get("selection_observation", {}))
        # Reachable (reader returned it) AND rejected on both sides, with the
        # diagnostics naming the side that was unsound.
        entry["verdict"] = "AGREES" if (
            entry["count_is_negative"]
            and responded_after is False and responded_before is False
            and entry["diag_after"].get("status") == "CORRUPTED"
            and entry["diag_after"].get("after_sound") is False
            and entry["diag_after"].get("before_sound") is True
            and entry["diag_before"].get("status") == "CORRUPTED"
            and entry["diag_before"].get("before_sound") is False
            and entry["diag_before"].get("after_sound") is True
        ) else "DEFECT"
    except Exception as exc:  # noqa: BLE001 - probe records, never hides
        entry["reader_raised"] = True
        entry["exception"] = f"{type(exc).__name__}: {exc}"
        entry["verdict"] = "DEFECT"
    # Strip the unbounded dict copies the predicate stores for provenance.
    for key in ("diag_after", "diag_before"):
        entry[key] = {k: v for k, v in entry.get(key, {}).items()
                      if k in ("status", "before_sound", "after_sound")}
    reachability.append(entry)

# Both sides negative at once: no sound base and no sound result.
both_diag: dict[str, Any] = {}
both_negative = {
    "id": "N6_both_sides_negative",
    "intent": "baseline and result both impossible: nothing to compare",
    "responded": rt._g1_selection_responded(
        observe(-1), observe(-5), diagnostics=both_diag),
    "diag": {k: v for k, v in both_diag.get("selection_observation", {}).items()
             if k in ("status", "before_sound", "after_sound")},
}
both_negative["verdict"] = "AGREES" if (
    both_negative["responded"] is False
    and both_negative["diag"].get("status") == "CORRUPTED"
    and both_negative["diag"].get("before_sound") is False
    and both_negative["diag"].get("after_sound") is False
) else "DEFECT"
reachability.append(both_negative)

# A negative count carried alongside a fully plausible identity cannot come
# from the reader, but a future caller could hand-build it; the predicate must
# not depend on the reader having already blanked slot/type.
synthetic_diag: dict[str, Any] = {}
synthetic = {
    "id": "N7_negative_with_plausible_identity",
    "intent": "predicate must reject count<0 on its own, not rely on the "
              "reader having blanked slot/type first",
    "responded": rt._g1_selection_responded(
        {"count": 1, "selected_slot": 1199, "selected_type": 70},
        {"count": -1, "selected_slot": 1198, "selected_type": 21},
        diagnostics=synthetic_diag),
    "diag": {k: v for k, v in synthetic_diag.get("selection_observation", {}).items()
             if k in ("status", "before_sound", "after_sound")},
}
synthetic["verdict"] = "AGREES" if (
    synthetic["responded"] is False
    and synthetic["diag"].get("status") == "CORRUPTED"
) else "DEFECT"
reachability.append(synthetic)


# ---------------------------------------------------------------- Q3 -------
# Faithful re-implementation of the pre-lap227 (lap225) rule, transcribed from
# the lap225 record: sound == integer count, and for count > 0 an int slot with
# a known type; count <= 0 was accepted as an empty selection.
def pre_lap227_responded(before: Any, after: Any) -> bool:
    def sound(observation: Any) -> bool:
        count = observation.get("count")
        if type(count) is not int:
            return False
        if count <= 0:
            return True
        return (type(observation.get("selected_slot")) is int
                and observation.get("selected_type") != "UNKNOWN")

    if not sound(before) or not sound(after):
        return False
    return (before.get("count") != after.get("count")
            or (before.get("selected_slot"), before.get("selected_type"))
            != (after.get("selected_slot"), after.get("selected_type")))


COUNTS: list[Any] = [-2147483648, -2, -1, 0, 1, 2, 1200, 0x7FFFFFFF,
                     True, False, 1.0, None, "1"]
SLOTS: list[Any] = [1199, 1198, None]
TYPES: list[Any] = [70, 21, "UNKNOWN"]

grid_total = 0
grid_diffs: list[dict[str, Any]] = []
unexpected_diffs: list[dict[str, Any]] = []
for (bc, bs, bt), (ac, asl, at) in itertools.product(
    itertools.product(COUNTS, SLOTS, TYPES), repeat=2,
):
    before = {"count": bc, "selected_slot": bs, "selected_type": bt}
    after = {"count": ac, "selected_slot": asl, "selected_type": at}
    grid_total += 1
    new = rt._g1_selection_responded(before, after)
    old = pre_lap227_responded(before, after)
    if new == old:
        continue
    negative_involved = (
        (type(bc) is int and bc < 0) or (type(ac) is int and ac < 0)
    )
    record = {"before": before, "after": after, "old": old, "new": new,
              "negative_count_involved": negative_involved}
    grid_diffs.append(record)
    if not (negative_involved and old is True and new is False):
        unexpected_diffs.append(record)

surgicality = {
    "id": "S1_differential_grid",
    "intent": "the repair must only turn previously-credited negative-count "
              "comparisons into rejections, and change nothing else",
    "cases": grid_total,
    "behaviour_changes": len(grid_diffs),
    "changes_all_negative_true_to_false": not unexpected_diffs,
    "unexpected_changes": unexpected_diffs[:5],
    "verdict": "AGREES" if (grid_diffs and not unexpected_diffs) else "DEFECT",
}


# ---------------------------------------------------------------- Q4 -------
# R6-B-R2 is an undecided meaning question; lap227 promised not to touch it.
preservation: list[dict[str, Any]] = []
for case_id, before, after, expect, intent in [
    ("P1_count_1_to_0_via_reader", observe(1), observe(0), True,
     "R6-B-R2 deferred semantics: losing the selection still counts"),
    ("P2_count_0_stale_identity", observe(1),
     {"count": 0, "selected_slot": 4242, "selected_type": "UNKNOWN"}, True,
     "count 0 with stale slot bytes must stay sound, exactly as before"),
    ("P3_count_0_to_0", observe(0), observe(0), False,
     "empty to empty is still no response"),
    ("P4_count_0_to_1", observe(0), observe(1), True,
     "the normal unit_select transition is unaffected"),
    ("P5_identity_change_only", observe(1),
     observe(1, slot=1198, unit_type=21), True,
     "lap204 identity-only change is unaffected"),
    ("P6_no_effect", observe(1), observe(1), False,
     "genuine no-effect must still be a hard FAIL, not laundered"),
]:
    diagnostics = {}
    responded = rt._g1_selection_responded(before, after, diagnostics=diagnostics)
    preservation.append({
        "id": case_id, "intent": intent, "expected": expect,
        "observed": responded,
        "diagnostics_status": diagnostics.get(
            "selection_observation", {}).get("status"),
        "verdict": "AGREES" if responded == expect else "DEFECT",
    })


# ---------------------------------------------------------------- Q5 -------
def drive_wait(sequence: list[dict[str, Any]], before: dict[str, Any]) -> dict[str, Any]:
    clock = [0.0]
    real_monotonic, real_sleep = rt.time.monotonic, rt.time.sleep
    rt.time.monotonic = lambda: clock[0]                          # type: ignore[assignment]
    rt.time.sleep = lambda s: clock.__setitem__(0, clock[0] + s)  # type: ignore[assignment]
    polls = [0]
    observation: dict[str, Any] = {}

    def read_state(_detailed: bool) -> dict[str, Any]:
        index = min(polls[0], len(sequence) - 1)
        polls[0] += 1
        return sequence[index]

    try:
        returned = rt._wait_state(
            read_state,
            lambda item: rt._g1_selection_responded(
                before, item, diagnostics=observation),
            started=0.0, timeout=30.0, message="drag response was not observed",
            stage="drag_select", stage_budget=1.0, stage_started=0.0,
            wait_observation=observation,
        )
        outcome = {"outcome": "RESPONDED", "classification": None,
                   "returned_count": returned.get("count")}
    except rt._G1WaitTimeout as exc:
        outcome = {"outcome": "TIMEOUT", "classification": exc.classification,
                   "returned_count": exc.last.get("count") if exc.last else None}
    finally:
        rt.time.monotonic = real_monotonic                        # type: ignore[assignment]
        rt.time.sleep = real_sleep                                # type: ignore[assignment]
    outcome["poll_count"] = observation.get("poll_count")
    return outcome


healthy_before = observe(1)
negative_poll = observe(-1)
sound_changed = observe(1, slot=1198, unit_type=21)
sound_unchanged = observe(1)

waits = [
    {"id": "W1_negative_every_poll",
     "expect_classification": "UNKNOWN_SELECTION_OBSERVATION_CORRUPTED",
     "expect_outcome": "TIMEOUT",
     "intent": "a permanently negative count must not end the wait early and "
               "must time out as CORRUPTED, never as FAIL_NO_EFFECT",
     "result": drive_wait([negative_poll], healthy_before)},
    {"id": "W2_negative_then_real_response",
     "expect_classification": None, "expect_outcome": "RESPONDED",
     "intent": "a transient negative poll must not consume the window; a real "
               "later response still wins",
     "result": drive_wait([negative_poll, negative_poll, sound_changed],
                          healthy_before)},
    {"id": "W3_negative_then_sound_no_effect",
     "expect_classification": "FAIL_NO_EFFECT", "expect_outcome": "TIMEOUT",
     "intent": "R6-B-R4 exposure check: one transient negative poll followed "
               "by sound unchanged polls is a real no-effect run; if this "
               "reports UNKNOWN, R3 widened the registered R4 laundering",
     "result": drive_wait([negative_poll] + [sound_unchanged] * 8,
                          healthy_before)},
]
for item in waits:
    got = item["result"]
    item["verdict"] = "AGREES" if (
        got["classification"] == item["expect_classification"]
        and got["outcome"] == item["expect_outcome"]
    ) else "DEFECT"

report = {
    "lap": 228, "role": "middle", "target": "G1-R6-B-R3 (lap227)",
    "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    "game_executions": 0,
    "reachability_and_coverage": reachability,
    "surgicality": surgicality,
    "preservation": preservation,
    "wait_cases": waits,
    "summary": {
        "reachability_defects": [r["id"] for r in reachability
                                 if r["verdict"] == "DEFECT"],
        "preservation_defects": [p["id"] for p in preservation
                                 if p["verdict"] == "DEFECT"],
        "wait_defects": [w["id"] for w in waits if w["verdict"] == "DEFECT"],
        "surgicality_verdict": surgicality["verdict"],
    },
}
try:
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write("\n")
except FileExistsError:
    # The existence check above gives a useful early error, while exclusive
    # creation also protects a concurrent rerun from clobbering its evidence.
    print(f"refusing to overwrite existing evidence: {args.output}")
    raise SystemExit(2)
except OSError as exc:
    # The parent can change between the preflight and exclusive creation.
    # Preserve the fail-closed classification rather than leaking a traceback.
    print(f"refusing to write evidence: {args.output}: {exc}")
    raise SystemExit(2)
print(json.dumps(report["summary"], indent=2, sort_keys=True))
print(f"grid cases={surgicality['cases']} changes={surgicality['behaviour_changes']}")
print(f"report -> {args.output}")
