#!/usr/bin/env python3
"""lap258 middle-tier independent review probe for R26 (stage_budget_state).

C0  targeted + adjacent test selection in the real repository
C1  independent expectation matrix written from the documented contract
C2  depth-matched mirror M0 control (must equal the real repository result)
C3  mutation kills, with out-of-range kill counting

No game, Wine, Xvfb or PNG.  Read-only against the repository: mutations are
applied to a throwaway mirror under /tmp only.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
SUT = REPO / "tools" / "runtime_env.py"
TESTS = REPO / "tests" / "test_runtime_env.py"
PY = REPO / ".venv" / "bin" / "python"

R26_TEST = "test_g1_direct_selection_reader_stage_budget_exhaustion_is_semantic"
R15_TEST = "test_g1_direct_selection_reader_failure_precedes_exhausted_run_budget"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def counts(out: str) -> dict[str, int]:
    tail = out.strip().splitlines()[-1] if out.strip() else ""
    return {
        key: int(num)
        for num, key in re.findall(r"(\d+) (passed|failed|error|errors|deselected)", tail)
    }


# --------------------------------------------------------------------------
# C1: expectation model written from the contract, NOT from the SUT source.
#
# Contract (lap256 middle handoff + R26 work record):
#   stage_budget := G1_INPUT_STAGE_BUDGETS.get(stage)
#   no configured budget                      -> STAGE_BUDGET_UNAVAILABLE
#   budget configured but stage start unknown -> STAGE_START_UNKNOWN
#   finished at/after stage_started+budget    -> STAGE_BUDGET_EXHAUSTED
#   otherwise                                 -> WITHIN_STAGE_BUDGET
#   stage_budget_exhausted is True iff the state is STAGE_BUDGET_EXHAUSTED
#   classification is always UNKNOWN_STATE_READ_FAILURE
#   finished_elapsed      = max(0, finished - started)
#   remaining_budget_after= max(0, started + timeout - finished)
#   run_budget_exhausted  = remaining_budget_after <= 0
# --------------------------------------------------------------------------
BUDGETS = {"unit_select": 10.0, "drag_select": 10.0, "minimap": 10.0}


def expected(stage, stage_started, started, finished, timeout):
    budget = BUDGETS.get(stage)
    if budget is None:
        state = "STAGE_BUDGET_UNAVAILABLE"
    elif stage_started is None:
        state = "STAGE_START_UNKNOWN"
    elif finished >= stage_started + budget:
        state = "STAGE_BUDGET_EXHAUSTED"
    else:
        state = "WITHIN_STAGE_BUDGET"
    remaining = max(0.0, started + timeout - finished)
    return {
        "stage_budget": budget,
        "stage_budget_state": state,
        "stage_budget_exhausted": state == "STAGE_BUDGET_EXHAUSTED",
        "finished_elapsed": round(max(0.0, finished - started), 3),
        "remaining_budget_after": round(remaining, 3),
        "run_budget_exhausted": remaining <= 0.0,
        "stage_started_elapsed": (
            None if stage_started is None else round(max(0.0, stage_started - started), 3)
        ),
        "classification": "UNKNOWN_STATE_READ_FAILURE",
    }


def c1_matrix() -> dict[str, object]:
    sys.path.insert(0, str(REPO / "tools"))
    import runtime_env  # noqa: PLC0415

    stages = ["unit_select", "drag_select", "minimap", "production", "menu"]
    starts = [None, 0.0, 4.25, 100.0]
    offsets = [0.0, 0.001, 5.0, 9.999, 10.0, 10.001, 14.25, 30.0]
    run_started, timeout = 0.0, 10.0
    cases = mismatches = 0
    details: list[dict[str, object]] = []
    seen_states: dict[str, int] = {}

    for stage in stages:
        for stage_started in starts:
            for offset in offsets:
                finished = (0.0 if stage_started is None else stage_started) + offset
                monotonic = runtime_env.time.monotonic
                runtime_env.time.monotonic = lambda f=finished: f
                try:
                    def unreadable():
                        raise OSError("probe injected direct read failure")

                    try:
                        runtime_env._g1_read_selection_stage(
                            unreadable, stage=stage, read_point="probe",
                            started=run_started, timeout=timeout,
                            stage_started=stage_started,
                        )
                        actual = {"classification": "NO_RAISE"}
                    except runtime_env._G1WaitTimeout as exc:
                        obs = exc.observation
                        actual = {
                            key: obs[key] for key in (
                                "stage_budget", "stage_budget_state",
                                "stage_budget_exhausted", "finished_elapsed",
                                "remaining_budget_after", "run_budget_exhausted",
                                "stage_started_elapsed",
                            )
                        }
                        actual["classification"] = exc.classification
                finally:
                    runtime_env.time.monotonic = monotonic

                want = expected(stage, stage_started, run_started, finished, timeout)
                cases += 1
                seen_states[want["stage_budget_state"]] = (
                    seen_states.get(want["stage_budget_state"], 0) + 1
                )
                if actual != want:
                    mismatches += 1
                    details.append({
                        "stage": stage, "stage_started": stage_started,
                        "finished": finished, "expected": want, "actual": actual,
                    })

    return {
        "cases": cases, "mismatches": mismatches,
        "state_distribution": seen_states, "mismatch_details": details[:10],
    }


MUTATIONS: list[tuple[str, str, str, str]] = [
    ("M1", "state pinned WITHIN_STAGE_BUDGET",
     '        stage_budget_state = (\n            "STAGE_BUDGET_UNAVAILABLE"',
     '        stage_budget_state = (\n            "WITHIN_STAGE_BUDGET"\n            if True\n            else "STAGE_BUDGET_UNAVAILABLE"'),
    ("M2", "state pinned STAGE_BUDGET_EXHAUSTED",
     '        stage_budget_state = (\n            "STAGE_BUDGET_UNAVAILABLE"',
     '        stage_budget_state = (\n            "STAGE_BUDGET_EXHAUSTED"\n            if True\n            else "STAGE_BUDGET_UNAVAILABLE"'),
    ("M3", "UNAVAILABLE collapsed into START_UNKNOWN",
     '            "STAGE_BUDGET_UNAVAILABLE"\n            if stage_budget is None',
     '            "STAGE_START_UNKNOWN"\n            if stage_budget is None'),
    ("M4", "START_UNKNOWN collapsed into WITHIN_STAGE_BUDGET",
     '            else "STAGE_START_UNKNOWN"\n            if stage_started is None',
     '            else "WITHIN_STAGE_BUDGET"\n            if stage_started is None'),
    ("M5", "priority reordered: unknown start checked before missing budget",
     '            "STAGE_BUDGET_UNAVAILABLE"\n            if stage_budget is None\n            else "STAGE_START_UNKNOWN"\n            if stage_started is None',
     '            "STAGE_START_UNKNOWN"\n            if stage_started is None\n            else "STAGE_BUDGET_UNAVAILABLE"\n            if stage_budget is None'),
    ("M6", "state boundary >= weakened to >",
     '            else "STAGE_BUDGET_EXHAUSTED"\n            if finished >= stage_started + stage_budget',
     '            else "STAGE_BUDGET_EXHAUSTED"\n            if finished > stage_started + stage_budget'),
    ("M7", "legacy boolean pinned True",
     '            "stage_budget_exhausted": bool(\n                stage_budget is not None',
     '            "stage_budget_exhausted": bool(\n                True or stage_budget is not None'),
    ("M8", "EXHAUSTED collapsed into WITHIN_STAGE_BUDGET",
     '            else "STAGE_BUDGET_EXHAUSTED"\n            if finished >= stage_started + stage_budget',
     '            else "WITHIN_STAGE_BUDGET"\n            if finished >= stage_started + stage_budget'),
]


def main() -> int:
    report: dict[str, object] = {
        "lap": 258, "role": "middle", "item": "R26",
        "sut_sha256": sha(SUT), "tests_sha256": sha(TESTS),
    }

    # C0 -- targeted + adjacent tests in the real repository.
    c0 = run([str(PY), "-m", "pytest", "-q", str(TESTS), "-k",
              "stage_budget or direct_selection_reader or read_failure"], REPO)
    report["C0"] = {"returncode": c0.returncode, "counts": counts(c0.stdout)}

    # C1 -- independent matrix.
    report["C1"] = c1_matrix()

    # C2/C3 -- depth-matched mirror.
    tmp = Path(tempfile.mkdtemp(prefix="lap258_r26_"))
    mirror = tmp / REPO.name
    for rel in ("tools", "tests", "pyproject.toml"):
        src = REPO / rel
        dst = mirror / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
    mirror_tests = mirror / "tests" / "test_runtime_env.py"
    mirror_sut = mirror / "tools" / "runtime_env.py"
    original = mirror_sut.read_text()

    real_full = run([str(PY), "-m", "pytest", "-q", str(TESTS)], REPO)
    m0 = run([str(PY), "-m", "pytest", "-q", str(mirror_tests)], mirror)
    report["C2"] = {
        "real_counts": counts(real_full.stdout), "mirror_counts": counts(m0.stdout),
        "equal": counts(real_full.stdout) == counts(m0.stdout),
        "returncode": m0.returncode,
    }

    r26_scope = {R26_TEST, R15_TEST}
    results = []
    for name, label, old, new in MUTATIONS:
        if old not in original:
            results.append({"id": name, "label": label, "applied": False})
            continue
        mirror_sut.write_text(original.replace(old, new, 1))
        res = run([str(PY), "-m", "pytest", "-q", str(mirror_tests), "--tb=no", "-q"], mirror)
        failed_names = sorted(set(re.findall(r"^FAILED (\S+?)(?:\[|\s|$)", res.stdout, re.M)))
        failed_short = sorted({n.split("::")[-1] for n in failed_names})
        in_scope = [n for n in failed_short if n in r26_scope]
        out_scope = [n for n in failed_short if n not in r26_scope]
        results.append({
            "id": name, "label": label, "applied": True,
            "counts": counts(res.stdout),
            "killed": bool(in_scope),
            "in_scope_kills": in_scope, "out_of_scope_kills": out_scope,
        })
        mirror_sut.write_text(original)

    report["C3"] = {
        "mutations": results,
        "survivors": [r["id"] for r in results if r.get("applied") and not r["killed"]],
        "out_of_scope_total": sorted({
            n for r in results for n in r.get("out_of_scope_kills", [])
        }),
    }
    shutil.rmtree(tmp, ignore_errors=True)

    out = Path(__file__).with_name(Path(__file__).stem.replace("_probe", "") + "_report.json")
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
