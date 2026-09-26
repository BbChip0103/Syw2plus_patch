#!/usr/bin/env python3
"""lap260 middle-tier independent review probe for R27.

R27 claim: the production-reachable direct-reader failure shape
``(stage_budget=None, stage_started=None)`` is pinned to
``STAGE_BUDGET_UNAVAILABLE``, killing the lap258 survivor M5 (priority
reorder), without weakening the R26/R25/R15 regressions.

C0  targeted + adjacent test selection in the real repository
C1  independent expectation matrix written from the contract, plus a
    static/dynamic check that the production call site really reaches the
    (no budget, no stage start) shape
C2  depth-matched mirror M0 control (must equal the real repository result)
C3  mutation kills with out-of-range kill counting, including the lap258
    survivor M5 and a call-site mutation
C4  load-bearing check: delete only the R27 regression and re-test M5

No game, Wine, Xvfb or PNG.  Read-only against the repository: every mutation
is applied to a throwaway mirror under /tmp only.
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

R27_TEST = "test_g1_production_direct_selection_reader_failure_stays_blocked_and_continues"
R26_TEST = "test_g1_direct_selection_reader_stage_budget_exhaustion_is_semantic"
R15_TEST = "test_g1_direct_selection_reader_failure_precedes_exhausted_run_budget"
SCOPE = {R27_TEST, R26_TEST, R15_TEST}


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
# C1 expectation model, written from the documented contract rather than the
# SUT source:
#   stage_budget := G1_INPUT_STAGE_BUDGETS.get(stage)
#   no configured budget                      -> STAGE_BUDGET_UNAVAILABLE
#   budget configured but stage start unknown -> STAGE_START_UNKNOWN
#   finished at/after stage_started+budget    -> STAGE_BUDGET_EXHAUSTED
#   otherwise                                 -> WITHIN_STAGE_BUDGET
#   (R27: the unavailable-budget arm outranks the unknown-start arm)
#   stage_budget_exhausted is True iff the state is STAGE_BUDGET_EXHAUSTED
#   classification is always UNKNOWN_STATE_READ_FAILURE
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
    seen: dict[str, int] = {}

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
                seen[want["stage_budget_state"]] = seen.get(want["stage_budget_state"], 0) + 1
                if actual != want:
                    mismatches += 1
                    details.append({
                        "stage": stage, "stage_started": stage_started,
                        "finished": finished, "expected": want, "actual": actual,
                    })

    # R27 production-shape check: call with the production defaults (stage
    # "production", stage_started omitted entirely).
    monotonic = runtime_env.time.monotonic
    runtime_env.time.monotonic = lambda: 3.0
    try:
        def unreadable():
            raise OSError("probe injected direct read failure")

        try:
            runtime_env._g1_read_selection_stage(
                unreadable, stage="production", read_point="before_production",
                started=0.0, timeout=10.0,
            )
            production_shape = {"classification": "NO_RAISE"}
        except runtime_env._G1WaitTimeout as exc:
            production_shape = {
                "stage_budget": exc.observation["stage_budget"],
                "stage_started_elapsed": exc.observation["stage_started_elapsed"],
                "stage_budget_state": exc.observation["stage_budget_state"],
                "classification": exc.classification,
            }
    finally:
        runtime_env.time.monotonic = monotonic

    src = SUT.read_text()
    call = re.search(
        r"_g1_read_selection_stage\(\s*\n\s*read_selection, stage=\"production\".*?\n\s*\)",
        src, re.S,
    )
    call_text = call.group(0) if call else ""
    return {
        "cases": cases,
        "mismatches": mismatches,
        "state_distribution": seen,
        "mismatch_details": details[:10],
        "production_default_shape": production_shape,
        "production_call_site_passes_stage_started": "stage_started" in call_text,
        "production_has_configured_budget": "production" in BUDGETS,
        "production_call_site_source": call_text,
    }


MUT_STATE_HEAD = '        stage_budget_state = (\n            "STAGE_BUDGET_UNAVAILABLE"'

MUTATIONS: list[tuple[str, str, str, str]] = [
    ("M1", "state pinned WITHIN_STAGE_BUDGET", MUT_STATE_HEAD,
     '        stage_budget_state = (\n            "WITHIN_STAGE_BUDGET"\n            if True\n            else "STAGE_BUDGET_UNAVAILABLE"'),
    ("M2", "state pinned STAGE_BUDGET_EXHAUSTED", MUT_STATE_HEAD,
     '        stage_budget_state = (\n            "STAGE_BUDGET_EXHAUSTED"\n            if True\n            else "STAGE_BUDGET_UNAVAILABLE"'),
    ("M3", "state pinned STAGE_BUDGET_UNAVAILABLE", MUT_STATE_HEAD,
     '        stage_budget_state = (\n            "STAGE_BUDGET_UNAVAILABLE"\n            if True\n            else "STAGE_BUDGET_UNAVAILABLE"'),
    ("M4", "UNAVAILABLE collapsed into START_UNKNOWN",
     '            "STAGE_BUDGET_UNAVAILABLE"\n            if stage_budget is None',
     '            "STAGE_START_UNKNOWN"\n            if stage_budget is None'),
    ("M5", "priority reordered: unknown start checked before missing budget",
     '            "STAGE_BUDGET_UNAVAILABLE"\n            if stage_budget is None\n            else "STAGE_START_UNKNOWN"\n            if stage_started is None',
     '            "STAGE_START_UNKNOWN"\n            if stage_started is None\n            else "STAGE_BUDGET_UNAVAILABLE"\n            if stage_budget is None'),
    ("M6", "START_UNKNOWN collapsed into WITHIN_STAGE_BUDGET",
     '            else "STAGE_START_UNKNOWN"\n            if stage_started is None',
     '            else "WITHIN_STAGE_BUDGET"\n            if stage_started is None'),
    ("M7", "state boundary >= weakened to >",
     '            else "STAGE_BUDGET_EXHAUSTED"\n            if finished >= stage_started + stage_budget',
     '            else "STAGE_BUDGET_EXHAUSTED"\n            if finished > stage_started + stage_budget'),
    ("M8", "EXHAUSTED collapsed into WITHIN_STAGE_BUDGET",
     '            else "STAGE_BUDGET_EXHAUSTED"\n            if finished >= stage_started + stage_budget',
     '            else "WITHIN_STAGE_BUDGET"\n            if finished >= stage_started + stage_budget'),
    ("M9", "legacy boolean pinned True",
     '            "stage_budget_exhausted": bool(\n                stage_budget is not None',
     '            "stage_budget_exhausted": bool(\n                True or stage_budget is not None'),
    ("M10", "stage_started_elapsed reported as 0.0 instead of None",
     '            "stage_started_elapsed": round(max(0.0, stage_started - started), 3)\n            if stage_started is not None else None,',
     '            "stage_started_elapsed": round(max(0.0, stage_started - started), 3)\n            if stage_started is not None else 0.0,'),
    ("M11", "production call site starts the stage clock (shape change)",
     'read_selection, stage="production", read_point="before_production",\n            started=started, timeout=timeout,',
     'read_selection, stage="production", read_point="before_production",\n            started=started, timeout=timeout, stage_started=started,'),
    ("M12", "production stage gains a configured budget",
     'G1_INPUT_STAGE_BUDGETS: dict[str, float] = {\n    "unit_select": 10.0,',
     'G1_INPUT_STAGE_BUDGETS: dict[str, float] = {\n    "production": 10.0,\n    "unit_select": 10.0,'),
]


def mutate(mirror_sut: Path, mirror_tests: Path, mirror: Path, original: str,
           label_scope: set[str]) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for name, label, old, new in MUTATIONS:
        if old not in original:
            results.append({"id": name, "label": label, "applied": False})
            continue
        mirror_sut.write_text(original.replace(old, new, 1))
        res = run([str(PY), "-m", "pytest", "-q", str(mirror_tests), "--tb=no"], mirror)
        failed = sorted({
            n.split("::")[-1]
            for n in re.findall(r"^FAILED (\S+?)(?:\[|\s|$)", res.stdout, re.M)
        })
        in_scope = [n for n in failed if n in label_scope]
        out_scope = [n for n in failed if n not in label_scope]
        results.append({
            "id": name, "label": label, "applied": True,
            "counts": counts(res.stdout), "killed": bool(in_scope),
            "in_scope_kills": in_scope, "out_of_scope_kills": out_scope,
        })
        mirror_sut.write_text(original)
    return results


def main() -> int:
    report: dict[str, object] = {
        "lap": 260, "role": "middle", "item": "R27",
        "sut_sha256_before": sha(SUT), "tests_sha256_before": sha(TESTS),
    }

    c0 = run([str(PY), "-m", "pytest", "-q", str(TESTS), "-k",
              "stage_budget or direct_selection_reader or read_failure "
              "or production_direct_selection"], REPO)
    report["C0"] = {"returncode": c0.returncode, "counts": counts(c0.stdout)}

    report["C1"] = c1_matrix()

    tmp = Path(tempfile.mkdtemp(prefix="lap260_r27_"))
    mirror = tmp / REPO.name
    for rel in ("tools", "tests", "pyproject.toml"):
        src, dst = REPO / rel, mirror / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src, dst) if src.is_dir() else shutil.copy2(src, dst)
    mirror_sut = mirror / "tools" / "runtime_env.py"
    mirror_tests = mirror / "tests" / "test_runtime_env.py"
    original_sut = mirror_sut.read_text()
    original_tests = mirror_tests.read_text()

    real_full = run([str(PY), "-m", "pytest", "-q", str(TESTS)], REPO)
    m0 = run([str(PY), "-m", "pytest", "-q", str(mirror_tests)], mirror)
    report["C2"] = {
        "real_counts": counts(real_full.stdout), "mirror_counts": counts(m0.stdout),
        "equal": counts(real_full.stdout) == counts(m0.stdout),
        "returncode": m0.returncode,
    }

    results = mutate(mirror_sut, mirror_tests, mirror, original_sut, SCOPE)
    report["C3"] = {
        "mutations": results,
        "survivors": [r["id"] for r in results if r.get("applied") and not r["killed"]],
        "not_applied": [r["id"] for r in results if not r.get("applied")],
        "out_of_scope_total": sorted({
            n for r in results for n in r.get("out_of_scope_kills", [])
        }),
    }

    # C4 -- remove only the R27 regression body and re-run the mutations that
    # R27 is supposed to be responsible for.  Anything that stops dying is
    # load-bearing on R27 alone.
    without_r27 = re.sub(
        r"def " + R27_TEST + r"\(.*?\n(?=\n\ndef |\n\n@)", "", original_tests, flags=re.S,
    )
    removed = without_r27 != original_tests and R27_TEST not in without_r27
    c4: dict[str, object] = {"r27_removed": removed}
    if removed:
        mirror_tests.write_text(without_r27)
        base = run([str(PY), "-m", "pytest", "-q", str(mirror_tests)], mirror)
        c4["baseline_without_r27"] = counts(base.stdout)
        c4["mutations"] = mutate(
            mirror_sut, mirror_tests, mirror, original_sut, SCOPE - {R27_TEST},
        )
        c4["survivors_without_r27"] = [
            r["id"] for r in c4["mutations"] if r.get("applied") and not r["killed"]
        ]
        mirror_tests.write_text(original_tests)
    report["C4"] = c4

    report["sut_sha256_after"] = sha(SUT)
    report["tests_sha256_after"] = sha(TESTS)
    shutil.rmtree(tmp, ignore_errors=True)

    out = Path(__file__).with_name(Path(__file__).stem.replace("_probe", "") + "_report.json")
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
