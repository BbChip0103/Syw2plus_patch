"""lap234 middle-tier independent probe for G1-R6-B-R5.

Reviews the lap233 reader-based corruption regression without running the game.
Three independent axes:

A. REACHABILITY - build a minimal byte-level reader fixture from the pinned
   address constants only (not the repository test helper) and check which
   observations `_read_g1_selection_evidence` can really emit.
B. FAIL-CLOSE - feed those real reader observations to
   `_g1_selection_responded` and record status/return value.
C. NON-VACUITY - mutate `_g1_selection_responded` in memory and re-run the
   lap233 test to confirm the new regression actually fails on a weakened guard.

Writes a JSON report. The output path refuses to overwrite an existing file
(R6-B-R7 is still open at work tier); pass an explicit path to override.
"""

from __future__ import annotations

import json
from pathlib import Path
import struct
import sys
import traceback

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))

from tools import runtime_env  # noqa: E402


def make_reader(
    *,
    count: int = 1,
    slot: int = 7,
    active: int = 1,
    unit_type: int = 58,
    fail_at: str | None = None,
    short_type_read: bool = False,
):
    """Minimal reader covering only what `_read_g1_selection_evidence` touches."""

    count_addr = runtime_env.G1_SELECTION_COUNT_ADDRESS
    slot_addr = runtime_env.G1_SELECTION_FIRST_SLOT_ADDRESS
    exists_addr = runtime_env.G1_UNIT_EXISTS_BASE_ADDRESS + slot * 2
    type_addr = (
        runtime_env.G1_UNIT_BASE_ADDRESS
        + slot * runtime_env.G1_UNIT_STRIDE
        + runtime_env.G1_UNIT_TYPE_OFFSET
    )
    targets = {"count": count_addr, "slot": slot_addr, "exists": exists_addr, "type": type_addr}

    def read(address: int, size: int) -> bytes:
        if fail_at is not None and address == targets[fail_at]:
            raise OSError(f"injected read failure at {fail_at}")
        if address == count_addr:
            return struct.pack("<i", count)
        if address == slot_addr:
            return struct.pack("<h", slot)
        if address == exists_addr:
            return struct.pack("<h", active)
        if address == type_addr:
            return b"" if short_type_read else struct.pack("<B", unit_type)
        raise AssertionError(f"probe fixture read an unexpected address 0x{address:08X}")

    return read


def observe(**kwargs) -> dict:
    try:
        return {"ok": True, "evidence": runtime_env._read_g1_selection_evidence(make_reader(**kwargs))}
    except Exception as exc:  # noqa: BLE001 - the probe records escapes on purpose
        return {"ok": False, "escaped": f"{type(exc).__name__}: {exc}"}


def sound(evidence: dict) -> bool:
    diag: dict = {}
    runtime_env._g1_selection_responded(evidence, evidence, diagnostics=diag)
    return diag["selection_observation"]["status"] == "SOUND"


HEALTHY = {}


def reachability_cases() -> list[dict]:
    cases = [
        ("A1_healthy", {}, "SOUND", None),
        ("A2_c4_identity_read_failure", {"fail_at": "exists"}, "CORRUPTED", "OSError:"),
        ("A3_c5_inactive_slot", {"active": 0}, "CORRUPTED", "_CommandCellSnapshotError:"),
        ("A4_d1_negative_count", {"count": -1}, "CORRUPTED", "_CommandCellSnapshotError:"),
        ("A5_count_above_pool", {"count": 1201}, "CORRUPTED", "_CommandCellSnapshotError:"),
        ("A6_slot_out_of_range", {"slot": 1200}, "CORRUPTED", "_CommandCellSnapshotError:"),
        ("A7_unit_type_zero", {"unit_type": 0}, "CORRUPTED", "_CommandCellSnapshotError:"),
        ("A8_struct_error_short_type", {"short_type_read": True}, "CORRUPTED", "error:"),
        ("A9_type_addr_read_failure", {"fail_at": "type"}, "CORRUPTED", "OSError:"),
        # A10/A12: `_read_selection` runs before the reader's try/except, so a
        # read failure at the selection count/first-slot words escapes the
        # reader entirely instead of becoming a CORRUPTED observation.  That is
        # by design and is absorbed by `_wait_state` (R6-B-R6 read_error_count
        # -> UNKNOWN_STATE_READ_FAILURE) and by the g1_baseline OSError handler.
        # attempt1 of this probe expected CORRUPTED here and recorded a DEFECT;
        # the expectation was wrong, the implementation is not.
        ("A10_slot_addr_read_failure", {"fail_at": "slot"}, "ESCAPES", None),
        ("A11_count_zero", {"count": 0, "slot": -1}, "SOUND", "no selected unit"),
        ("A12_count_addr_read_failure", {"fail_at": "count"}, "ESCAPES", None),
    ]
    results = []
    for name, kwargs, expected_status, provenance_prefix in cases:
        got = observe(**kwargs)
        if not got["ok"]:
            status = "ESCAPES"
            evidence = None
            provenance = got["escaped"]
        else:
            evidence = got["evidence"]
            status = "SOUND" if sound(evidence) else "CORRUPTED"
            provenance = evidence.get("selected_type_provenance")
        agrees = status == expected_status and (
            provenance_prefix is None or (provenance or "").startswith(provenance_prefix)
            or (provenance_prefix in (provenance or ""))
        )
        results.append({
            "case": name,
            "fixture": kwargs,
            "expected_status": expected_status,
            "observed_status": status,
            "count": None if evidence is None else evidence.get("count"),
            "selected_slot": None if evidence is None else evidence.get("selected_slot"),
            "selected_type": None if evidence is None else evidence.get("selected_type"),
            "provenance": provenance,
            "verdict": "AGREES" if agrees else "DEFECT",
        })
    return results


def failclose_cases() -> list[dict]:
    """Every corrupted reader observation must fail-close in both directions."""

    healthy = observe()["evidence"]
    corrupted = {
        "c4": observe(fail_at="exists"),
        "c5": observe(active=0),
        "c7_before": observe(active=0),
        "d1": observe(count=-1),
        "type_zero": observe(unit_type=0),
        "slot_range": observe(slot=1200),
        "struct_error": observe(short_type_read=True),
    }
    results = []
    for name, got in corrupted.items():
        evidence = got["evidence"]
        for direction, before, after in (
            (f"{name}_after", healthy, evidence),
            (f"{name}_before", evidence, healthy),
        ):
            diag: dict = {}
            responded = runtime_env._g1_selection_responded(before, after, diagnostics=diag)
            observation = diag["selection_observation"]
            ok = responded is False and observation["status"] == "CORRUPTED"
            results.append({
                "case": direction,
                "responded": responded,
                "status": observation["status"],
                "corrupted_poll_count": observation["corrupted_poll_count"],
                "first_corruption_preserved": observation["first_corruption_provenance"] is not None,
                "verdict": "AGREES" if ok else "DEFECT",
            })
    # PASS path must stay open: sound observations with a real change still respond.
    changed = observe(slot=8, unit_type=59)["evidence"]
    diag = {}
    responded = runtime_env._g1_selection_responded(healthy, changed, diagnostics=diag)
    results.append({
        "case": "pass_path_identity_change",
        "responded": responded,
        "status": diag["selection_observation"]["status"],
        "corrupted_poll_count": diag["selection_observation"]["corrupted_poll_count"],
        "first_corruption_preserved": False,
        "verdict": "AGREES" if responded is True and diag["selection_observation"]["status"] == "SOUND" else "DEFECT",
    })
    return results


MUTANTS = {
    "M1_ignore_unknown_type": lambda before, after, diagnostics=None: _mutant(
        before, after, diagnostics, allow_unknown_type=True),
    "M2_allow_negative_count": lambda before, after, diagnostics=None: _mutant(
        before, after, diagnostics, allow_negative_count=True),
    "M3_always_sound": lambda before, after, diagnostics=None: _mutant(
        before, after, diagnostics, always_sound=True),
}


def _mutant(before, after, diagnostics, *, allow_unknown_type=False,
            allow_negative_count=False, always_sound=False) -> bool:
    def is_sound(observation) -> bool:
        if always_sound:
            return True
        count = observation.get("count")
        if type(count) is not int:
            return False
        if count < 0 and not allow_negative_count:
            return False
        if count <= 0:
            return True
        if allow_unknown_type:
            return True
        return (
            type(observation.get("selected_slot")) is int
            and observation.get("selected_type") != "UNKNOWN"
        )

    before_sound, after_sound = is_sound(before), is_sound(after)
    if diagnostics is not None:
        diagnostics["selection_observation"] = {
            "status": "SOUND" if before_sound and after_sound else "CORRUPTED",
            "before_sound": before_sound, "after_sound": after_sound,
            "before": dict(before), "after": dict(after),
            "corrupted_poll_count": 0,
            "first_corruption_provenance": None, "last_corruption_provenance": None,
        }
    if not before_sound or not after_sound:
        return False
    return (before.get("count") != after.get("count")
            or (before.get("selected_slot"), before.get("selected_type"))
            != (after.get("selected_slot"), after.get("selected_type")))


def mutation_cases() -> list[dict]:
    """A weakened guard must make the lap233 reader regression fail."""

    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "lap233_tests", REPO / "tests" / "test_runtime_env.py")
    lap233_tests = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lap233_tests)

    target = lap233_tests.test_g1_selection_response_rejects_reader_generated_corruption
    subject = getattr(target, "__wrapped__", target)
    cases = ["c4_read_failure", "c5_inactive_slot", "c7_recovery", "d1_negative_count"]
    results = []
    original = runtime_env._g1_selection_responded
    try:
        baseline_failures = []
        for case in cases:
            try:
                subject(case)
            except Exception:  # noqa: BLE001
                baseline_failures.append(case)
        results.append({
            "mutant": "M0_unmutated",
            "failing_cases": baseline_failures,
            "expectation": "no case fails",
            "verdict": "AGREES" if not baseline_failures else "DEFECT",
        })
        for name, mutant in MUTANTS.items():
            runtime_env._g1_selection_responded = mutant
            failing = []
            for case in cases:
                try:
                    subject(case)
                except Exception:  # noqa: BLE001
                    failing.append(case)
            runtime_env._g1_selection_responded = original
            results.append({
                "mutant": name,
                "failing_cases": failing,
                "expectation": "at least one case fails",
                "verdict": "AGREES" if failing else "DEFECT",
            })
    finally:
        runtime_env._g1_selection_responded = original
    return results


def main() -> int:
    default = Path(__file__).with_name("20260912_lap234_r6b_r5_review_report.json")
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else default
    if out.exists():
        print(f"REFUSING to overwrite existing report: {out}")
        return 2
    print(f"runtime_env module file: {runtime_env.__file__}")
    report = {
        "lap": 234,
        "runtime_env_module_file": runtime_env.__file__,
        "role": "middle (claude-opus-5/high)",
        "subject": "G1-R6-B-R5 reader-based corruption regression (lap233)",
        "runtime_env_sha256": None,
        "reachability": reachability_cases(),
        "fail_close": failclose_cases(),
        "mutation": mutation_cases(),
    }
    import hashlib
    report["runtime_env_sha256"] = hashlib.sha256(
        (REPO / "tools" / "runtime_env.py").read_bytes()).hexdigest()
    report["tests_sha256"] = hashlib.sha256(
        (REPO / "tests" / "test_runtime_env.py").read_bytes()).hexdigest()
    sections = ("reachability", "fail_close", "mutation")
    report["summary"] = {
        section: {
            "total": len(report[section]),
            "agrees": sum(1 for row in report[section] if row["verdict"] == "AGREES"),
            "defects": [row for row in report[section] if row["verdict"] == "DEFECT"],
        }
        for section in sections
    }
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for section in sections:
        summary = report["summary"][section]
        print(f"{section}: {summary['agrees']}/{summary['total']} AGREES")
    print(f"report: {out}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:  # noqa: BLE001
        traceback.print_exc()
        raise SystemExit(1)
