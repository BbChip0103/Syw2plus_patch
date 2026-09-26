#!/usr/bin/env python3
"""lap252 middle: independent review of the lap251 G1-R6-B-R14 repair.

lap251 claims that when the *direct* production selection reader fails, the
nested ``before/after.selection`` snapshots on the production input record are
no longer indistinguishable from the "never read" default: they must carry
``status="UNAVAILABLE"``, ``count=None`` and ``read_failure=True``.  It further
claims production stays ``BLOCKED`` with no click and no effect wait, the
pre-existing ``selection_read_failure`` provenance survives, the later drag and
minimap stages still run, and a *successful* production read leaves no marker.
Its evidence is "targeted 4 passed" plus the full Fast suite.  Passing tests do
not show the marker is load-bearing, do not show it is confined to the
production stage, and do not show the failure-only condition is asserted.

This probe rebuilds the check from scratch:

C0. BASELINE.  Do the shipped R14 cases pass against the real repository?
C1. INDEPENDENT MATRIX.  Drive ``_g1_run_input_sequence`` with a harness
    written here (state advanced by the *input* stubs, not by a read counter,
    so it is invariant to where a read failure is injected) over every direct
    selection read point plus both poll points plus the clean run, and compare
    the flushed evidence against an expectation model written from the stated
    contract.  The model asserts both presence (production read point) and
    absence (every other read point) of the marker.
C1b. CONSUMER SCAN.  Does anything outside tools/runtime_env.py read the new
    ``read_failure`` field?  R23 recorded the same question for read_coverage.
C2. MIRROR CONTROL (M0).  Does an unmutated, depth-matched copy of the
    repository reproduce the real tests/test_runtime_env.py result?  Without
    this control a relocation failure reads as a "kill" (lap246 R20 lesson).
C3. MUTATIONS.  Against that mirror: (M1) marker removed, (M2) marker applied
    unconditionally, (M3) marker count set to 0 instead of None, (M4) the
    stage-level ``selection_read_failure`` provenance dropped, (M5) production
    read failure re-raised instead of continuing.  Each must kill at least one
    shipped test, otherwise that part of R14 is unasserted.

No game, Wine, Xvfb or PNG capture is involved; the probe is pure Python.
The report path is guarded before the body runs (R6-B-R7/R10) and the payload
is serialised *before* the file is exclusively created (R6-B-R11), so a
serialisation failure cannot leave truncated evidence behind (lap248 R21).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
RUNTIME_ENV = ROOT / "tools" / "runtime_env.py"
TEST_FILE = ROOT / "tests" / "test_runtime_env.py"
PYTHON = ROOT / ".venv" / "bin" / "python"

sys.path.insert(0, str(ROOT / "tools"))
import runtime_env  # noqa: E402


# --- mutation anchors -----------------------------------------------------
MARKER_ANCHOR = (
        "        production_before_selection = {\n"
        "            **production_before_selection,\n"
        '            "read_failure": True,\n'
        "        }\n"
)
PROVENANCE_ANCHOR = (
            '            **({"selection_read_failure": production_selection_read_failure}\n'
            "               if production_selection_read_failure is not None else {}),\n"
)
CATCH_ANCHOR = (
        "        production_selection_read_failure = dict(exc.observation)\n"
)

MUTATIONS: dict[str, tuple[str, str]] = {
    # Revert R14: the nested snapshot goes back to the ambiguous default.
    "M1_marker_removed": (MARKER_ANCHOR, ""),
    # Over-strong variant: mark every production snapshot, including successes.
    "M2_marker_always_applied": (MARKER_ANCHOR, (
        "        production_before_selection = {\n"
        "            **production_before_selection,\n"
        '            "read_failure": True,\n'
        "        }\n"
    ) + '    production_before_selection = {**production_before_selection, "read_failure": True}\n'),
    # Wrong sentinel: a 0 count would read as "nothing was selected".
    "M3_marker_count_zeroed": (MARKER_ANCHOR, (
        "        production_before_selection = {\n"
        "            **production_before_selection,\n"
        '            "read_failure": True,\n'
        '            "count": 0,\n'
        "        }\n"
    )),
    # Drop the stage-level provenance R14 promised to preserve.
    "M4_stage_provenance_dropped": (PROVENANCE_ANCHOR, ""),
    # Stop continuing after a production read failure.
    "M5_production_failure_reraised": (CATCH_ANCHOR, (
        "        production_selection_read_failure = dict(exc.observation)\n"
        "        raise\n"
    )),
}

R14_TESTS = {
    "test_g1_production_selection_snapshots_mark_direct_read_failure_unavailable",
    "test_g1_production_selection_snapshot_has_no_failure_marker_on_success",
    "test_g1_production_direct_selection_reader_failure_stays_blocked_and_continues",
    "test_g1_shared_input_sequence_blocks_production_but_reaches_later_stages",
}


def output_refusal(path: Path) -> str | None:
    try:
        if path.exists() or path.is_symlink():
            return f"refusing to overwrite existing evidence: {path}"
        parent = path.parent
        if not parent.is_dir():
            return f"refusing to write evidence: output parent is not a directory: {parent}"
        if not os.access(parent, os.W_OK | os.X_OK):
            return f"refusing to write evidence: output parent is not writable: {parent}"
    except OSError as exc:
        return f"refusing to write evidence: output path unavailable: {path}: {exc}"
    return None


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_pytest(root: Path, args: list[str]) -> dict[str, object]:
    proc = subprocess.run(
        [str(PYTHON), "-m", "pytest", "-p", "no:cacheprovider", "-q", *args],
        cwd=str(root), capture_output=True, text=True, timeout=900,
    )
    stdout = proc.stdout + proc.stderr
    failed: set[str] = set()
    for line in stdout.splitlines():
        if not (line.startswith("FAILED ") or line.startswith("ERROR ")):
            continue
        node = line.split(" ", 1)[1].split(" - ")[0].strip()
        if "::" not in node:
            continue
        failed.add(node.split("::")[-1].split("[")[0])
    summary = [
        ln for ln in stdout.splitlines()
        if " passed" in ln or " failed" in ln or " error" in ln
    ]
    return {
        "returncode": proc.returncode,
        "failed_tests": sorted(failed),
        "summary": summary[-1] if summary else "",
    }


# --------------------------------------------------------------------------
# C1: independent harness.
#
# Selection state is advanced by the click/drag stubs, never by a read
# counter, so injecting a failure at read point N does not shift what later
# read points observe.  The shipped test helper keys its fixture off a read
# counter; that coupling is exactly what this probe refuses to inherit.
# --------------------------------------------------------------------------
READ_POINTS = (
    "unit_select/before_click",      # 1 direct
    "unit_select/poll",              # 2 poll (tolerated by _wait_state)
    "production/before_production",  # 3 direct
    "drag_select/before_drag",       # 4 direct
    "drag_select/poll",              # 5 poll
    "drag_select/after_drag",        # 6 direct
    "minimap/before_minimap",        # 7 direct
    "minimap/after_minimap",         # 8 direct
)
DIRECT_POINTS = {
    "unit_select/before_click": ("unit_select", "before_click"),
    "production/before_production": ("production", "before_production"),
    "drag_select/before_drag": ("drag_select", "before_drag"),
    "drag_select/after_drag": ("drag_select", "after_drag"),
    "minimap/before_minimap": ("minimap", "before_minimap"),
    "minimap/after_minimap": ("minimap", "after_minimap"),
}


def drive(run_dir: Path, fail_at: str | None) -> dict[str, object]:
    run_dir.mkdir(parents=True)
    inputs: list[dict[str, object]] = []
    evidence: dict[str, object] = {}
    clicks: list[tuple[int, int]] = []
    drags: list[tuple[int, int, int, int]] = []
    camera = [7, 6]
    tick = {"n": 10}
    phase = {"count": 0, "slot": 7, "type": 58}
    reads = {"n": 0, "fired": False}

    def read_selection() -> dict[str, object]:
        reads["n"] += 1
        index = reads["n"]
        # One-shot injection.  A tolerated poll retry consumes an extra read,
        # so only the first matching ordinal may fire; the returned state is
        # input-driven and stays correct however many reads happen.
        if (
            fail_at is not None and not reads["fired"]
            and index <= len(READ_POINTS) and READ_POINTS[index - 1] == fail_at
        ):
            reads["fired"] = True
            raise OSError("injected direct selection read failure")
        if phase["count"] == 0:
            return {"status": "OK", "count": 0, "selected_slot": None,
                    "selected_type": None}
        return {"status": "OK", "count": phase["count"],
                "selected_slot": phase["slot"], "selected_type": phase["type"]}

    def click(x: int, y: int) -> None:
        clicks.append((x, y))
        if (x, y) == (410, 270):
            phase.update(count=1, slot=7, type=58)
        if (x, y) == (150, 520):
            camera[:] = [81, 0]

    def do_drag(x: int, y: int, to_x: int, to_y: int) -> None:
        drags.append((x, y, to_x, to_y))
        phase.update(count=2, slot=9, type=58)

    def runtime_state() -> dict[str, object]:
        tick["n"] += 1
        return {"ps": 3, "tick": tick["n"]}

    def wait(reader, predicate, message, **kwargs):
        # Model _wait_state: poll repeatedly, tolerate transient read errors.
        last: dict[str, object] = {}
        for _ in range(3):
            try:
                last = reader(True)
            except OSError:
                continue
            if predicate(last):
                return last
        raise runtime_env._G1WaitTimeout(
            message, classification="UNKNOWN_SELECTION_OBSERVATION_CORRUPTED",
            last=last, finished_elapsed=1.0, remaining_budget_after=80.0,
            observation=kwargs["wait_observation"],
        )

    def read_production_cell() -> dict[str, object]:
        return {"status": "UNKNOWN", "primary_field": None}

    outcome = "completed"
    try:
        runtime_env._g1_run_input_sequence(
            inputs=inputs, content_crop=(37, 41, 1600, 1200), scale=(2.0, 2.0),
            capture=lambda tag: {"sha256": tag, "dimensions": [1600, 1200]},
            runtime_state=runtime_state,
            game_state=lambda: {"ps": 3, "tick": tick["n"], "players": []},
            read_selection=read_selection, read_camera=lambda: list(camera),
            wait=wait, click=click, drag=do_drag,
            read_production_cell=read_production_cell,
            flush=lambda: runtime_env._g1_flush_input_stage(run_dir, evidence, inputs),
            started=time.monotonic() - 1.0, timeout=90.0,
        )
    except runtime_env._G1WaitTimeout as exc:
        outcome = f"wait_timeout:{exc.classification}"
    except runtime_env.RuntimeSafetyError as exc:
        outcome = f"safety_error:{exc}"
    except OSError as exc:
        outcome = f"oserror:{exc}"
    runtime_env._g1_flush_input_stage(run_dir, evidence, inputs)
    flushed = json.loads((run_dir / "evidence.json").read_text(encoding="utf-8"))
    return {"flushed": flushed, "clicks": clicks, "drags": drags, "outcome": outcome}


def observed(result: dict[str, object]) -> dict[str, object]:
    flushed = result["flushed"]
    records = [item for item in flushed["inputs"] if "result" in item]
    by_tag = {item["tag"]: item for item in records}
    marked: list[str] = []
    for item in records:
        for side in ("before", "after"):
            state = item.get(side)
            selection = state.get("selection") if isinstance(state, dict) else None
            if isinstance(selection, dict) and "read_failure" in selection:
                marked.append(f"{item['tag']}/{side}={selection['read_failure']}")
    production = by_tag.get("production")
    prod_view: dict[str, object] | None = None
    if production is not None:
        prod_view = {
            "result": production.get("result"),
            "waited": production.get("waited"),
            "before_selection": production["before"].get("selection"),
            "after_selection": production["after"].get("selection"),
            "selection_read_failure_point": (
                production.get("selection_read_failure", {}) or {}
            ).get("direct_read_point"),
        }
    return {
        "tags": [item["tag"] for item in records],
        "results": {item["tag"]: item["result"] for item in records},
        "marked_selections": sorted(marked),
        "production": prod_view,
        "clicks": result["clicks"],
        "drags": result["drags"],
        "outcome": result["outcome"],
    }


def expected(fail_at: str | None) -> dict[str, object]:
    """Expectation model written from the stated R14 contract."""

    full_tags = ["unit_select", "production", "drag_select", "minimap"]
    full_clicks = [(410, 270), (150, 520)]
    full_drags = [(350, 180, 550, 350)]
    clean_production = {
        "result": "BLOCKED", "waited": False,
        "before_selection": {"status": "OK", "count": 1, "selected_slot": 7,
                             "selected_type": 58},
        "after_selection": {"status": "OK", "count": 1, "selected_slot": 7,
                            "selected_type": 58},
        "selection_read_failure_point": None,
    }
    # Poll-point failures are tolerated by the wait loop: the run completes and
    # no stage may carry the production read-failure marker.
    if fail_at is None or fail_at.endswith("/poll"):
        return {"tags": full_tags, "marked_selections": [],
                "production": clean_production,
                "clicks": full_clicks, "drags": full_drags,
                "results": {"unit_select": "PASS", "production": "BLOCKED",
                            "drag_select": "PASS", "minimap": "PASS"},
                "outcome": "completed"}
    tag, point = DIRECT_POINTS[fail_at]
    if tag == "production":
        # R14: the only continuing failure.  Marker present on both nested
        # snapshots, production still fail-closed, later stages still run.
        marker = {"status": "UNAVAILABLE", "count": None, "read_failure": True}
        return {
            "tags": full_tags, "marked_selections": [
                "production/after=True", "production/before=True",
            ],
            "production": {
                "result": "BLOCKED", "waited": False,
                "before_selection": marker, "after_selection": marker,
                "selection_read_failure_point": "before_production",
            },
            "clicks": full_clicks, "drags": full_drags,
            "results": {"unit_select": "PASS", "production": "BLOCKED",
                        "drag_select": "PASS", "minimap": "PASS"},
            "outcome": "completed",
        }
    # Every other direct read point aborts its stage as a read failure and
    # must not produce the marker anywhere.
    stages_before = {"unit_select": [], "drag_select": ["unit_select", "production"],
                     "minimap": ["unit_select", "production", "drag_select"]}[tag]
    if tag == "unit_select":
        clicks: list[tuple[int, int]] = []
    elif tag == "minimap" and point == "after_minimap":
        clicks = full_clicks
    else:
        clicks = [(410, 270)]
    drags = full_drags if (
        "drag_select" in stages_before or point == "after_drag"
    ) else []
    results = {s: ("BLOCKED" if s == "production" else "PASS") for s in stages_before}
    results[tag] = "UNKNOWN_STATE_READ_FAILURE"
    return {
        "tags": stages_before + [tag], "marked_selections": [],
        "production": clean_production if "production" in stages_before else None,
        "clicks": clicks, "drags": drags, "results": results,
        "outcome": "wait_timeout:UNKNOWN_STATE_READ_FAILURE",
    }


def matrix(stage: Path) -> dict[str, object]:
    mismatches: list[dict[str, object]] = []
    cases: list[str] = []
    for index, fail_at in enumerate([None, *READ_POINTS]):
        label = fail_at or "none"
        cases.append(label)
        got = observed(drive(stage / f"case{index}", fail_at))
        want = expected(fail_at)
        diff = {
            key: {"want": want[key], "got": got[key]}
            for key in want if got.get(key) != want[key]
        }
        if diff:
            mismatches.append({"case": label, "diff": diff})
    return {"cases": cases, "case_count": len(cases), "mismatches": mismatches}


def consumer_scan() -> dict[str, object]:
    hits: list[str] = []
    for path in sorted((ROOT / "tools").glob("*.py")) + sorted((ROOT / "checks").glob("*")):
        if not path.is_file() or path.name == "runtime_env.py":
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if "read_failure" in text:
            hits.append(str(path.relative_to(ROOT)))
    return {"consumers_outside_runtime_env": hits, "count": len(hits)}


def build_mirror(stage: Path) -> Path:
    # Match the real repository's path depth (5 components under "/").
    mirror = stage / "sharedfolder" / "260320_Syw2plus" / "Syw2plus_patch"
    mirror.parent.mkdir(parents=True)
    shutil.copytree(
        ROOT, mirror,
        ignore=shutil.ignore_patterns(
            ".git", "__pycache__", "local", "logs", ".venv", ".pytest_cache",
        ),
    )
    return mirror


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    refusal = output_refusal(args.output)
    if refusal is not None:
        print(refusal, file=sys.stderr)
        return 2

    report: dict[str, object] = {
        "lap": 252,
        "role": "middle",
        "subject": "G1-R6-B-R14 production direct selection read-failure marking",
        "source_sha256": {
            "tools/runtime_env.py": sha256(RUNTIME_ENV),
            "tests/test_runtime_env.py": sha256(TEST_FILE),
        },
        "game_executions": 0,
        "wine_executions": 0,
    }

    report["c0_baseline"] = run_pytest(ROOT, [
        "tests/test_runtime_env.py", "-k", " or ".join(sorted(R14_TESTS)),
    ])
    with tempfile.TemporaryDirectory(prefix="lap252_r14_matrix_") as tmp:
        report["c1_matrix"] = matrix(Path(tmp))
    report["c1b_consumers"] = consumer_scan()

    source = RUNTIME_ENV.read_text(encoding="utf-8")
    anchors = {
        "marker": MARKER_ANCHOR in source,
        "provenance": PROVENANCE_ANCHOR in source,
        "catch": CATCH_ANCHOR in source,
    }
    report["anchors_present"] = anchors
    if not all(anchors.values()):
        report["c2_mirror_control"] = {"skipped": "mutation anchor not found"}
        report["c3_mutations"] = {"skipped": "mutation anchor not found"}
    else:
        with tempfile.TemporaryDirectory(prefix="lap252_r14_") as tmp:
            mirror = build_mirror(Path(tmp))
            target = mirror / "tools" / "runtime_env.py"
            pristine = target.read_text(encoding="utf-8")
            report["c2_mirror_control"] = run_pytest(mirror, ["tests/test_runtime_env.py"])
            mutants: dict[str, object] = {}
            for name, (anchor, replacement) in MUTATIONS.items():
                mutated = pristine.replace(anchor, replacement)
                if mutated == pristine:
                    mutants[name] = {"error": "anchor did not apply"}
                    continue
                target.write_text(mutated, encoding="utf-8")
                shutil.rmtree(mirror / "tools" / "__pycache__", ignore_errors=True)
                result = run_pytest(mirror, ["tests/test_runtime_env.py"])
                killed = set(result["failed_tests"])
                result["killed_r14"] = sorted(killed & R14_TESTS)
                result["killed_other"] = sorted(killed - R14_TESTS)
                mutants[name] = result
                target.write_text(pristine, encoding="utf-8")
            report["c3_mutations"] = mutants

    baseline_ok = report["c0_baseline"]["returncode"] == 0
    matrix_ok = not report["c1_matrix"]["mismatches"]
    control = report.get("c2_mirror_control", {})
    control_ok = control.get("returncode") == 0
    mutants = report.get("c3_mutations", {})
    mutation_ok = bool(mutants) and all(
        isinstance(item, dict) and item.get("failed_tests")
        for item in mutants.values()
    )
    report["verdict"] = {
        "c0_baseline": "PASS" if baseline_ok else "FAIL",
        "c1_matrix": "PASS" if matrix_ok else "FAIL",
        "c2_mirror_control": "PASS" if control_ok else "FAIL",
        "c3_mutations": "PASS" if mutation_ok else "FAIL",
        "overall": "PASS" if (
            baseline_ok and matrix_ok and control_ok and mutation_ok
        ) else "FAIL",
    }

    # R21 lesson: serialise first so a payload defect cannot leave a truncated
    # evidence file that R6-B-R7 then refuses to let us replace.
    payload = json.dumps(report, indent=2, sort_keys=True, default=str) + "\n"
    with args.output.open("x", encoding="utf-8") as stream:
        stream.write(payload)
    print(json.dumps(report["verdict"], indent=2))
    print(json.dumps(report["c1_matrix"]["mismatches"], indent=2)[:4000])
    return 0 if report["verdict"]["overall"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
