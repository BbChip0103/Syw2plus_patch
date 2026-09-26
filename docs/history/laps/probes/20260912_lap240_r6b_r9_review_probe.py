"""lap240 middle-tier review probe for G1 R6-B-R9 direct selection-reader failures.

Independently re-derives, game-free, whether every direct (non-poll)
``read_selection`` call inside ``_g1_run_input_sequence`` is fail-closed with
stage/read-point/exception provenance, whether the production read point stays
BLOCKED while later inputs continue, and whether the untouched PASS path and
polling classifications stay intact.

The harness is written from scratch for this review: it does not import or
reuse the work tier's ``tests/test_runtime_env.py`` fixtures.  No process
memory is read, no product asset is touched, and no game/Wine/Xvfb run is
started.  Mutation cases load a *copy* of ``tools/runtime_env.py`` in a
temporary directory so the real source is never modified.  The report is
written with exclusive creation so an existing report is never overwritten
(R6-B-R7 rule).
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import struct
import sys
import tempfile
import time
from pathlib import Path
from types import ModuleType
from typing import Any, Callable
from unittest import mock

REPO = Path(__file__).resolve().parents[4]
SOURCE = REPO / "tools" / "runtime_env.py"
sys.path.insert(0, str(REPO / "tools"))

import runtime_env  # noqa: E402

CONTENT_CROP = (0, 0, 1600, 1200)
SCALE = (2.0, 2.0)

# Independently scripted selection states.  ``unit_select`` must move 0 -> >=1,
# ``drag_select`` must show a count-or-identity response.
S_EMPTY = {"count": 0, "selected_slot": None, "selected_type": "UNKNOWN", "tick": 10}
S_ONE = {"count": 1, "selected_slot": 1199, "selected_type": 70, "tick": 11}
S_TWO = {"count": 2, "selected_slot": 1198, "selected_type": 21, "tick": 12}

# Direct read points in source order, independently read off the call sites.
DIRECT_POINTS: tuple[tuple[int, str, str], ...] = (
    (1, "unit_select", "before_click"),
    (3, "production", "before_production"),
    (4, "drag_select", "before_drag"),
    (6, "drag_select", "after_drag"),
    (7, "minimap", "before_minimap"),
    (8, "minimap", "after_minimap"),
)
RAISING_POINTS = tuple(item for item in DIRECT_POINTS if item[1] != "production")

INJECTED: dict[str, Callable[[], BaseException]] = {
    "oserror": lambda: OSError("injected direct selection read failure"),
    "valueerror": lambda: ValueError("injected direct selection read failure"),
    "structerror": lambda: struct.error("injected direct selection read failure"),
}


def _scripted_reads() -> list[dict[str, Any]]:
    """The clean call sequence: 1 before_click, 2 poll, 3..8 as documented."""

    return [
        dict(S_EMPTY),  # 1 before_click
        dict(S_ONE),    # 2 unit_select poll -> count >= 1
        dict(S_ONE),    # 3 before_production
        dict(S_ONE),    # 4 before_drag
        dict(S_TWO),    # 5 drag poll -> responded
        dict(S_TWO),    # 6 after_drag
        dict(S_TWO),    # 7 before_minimap
        dict(S_TWO),    # 8 after_minimap
    ]


def run_sequence(
    module: ModuleType, directory: Path, *,
    fail_call: int | None = None, exc_kind: str = "oserror",
) -> dict[str, Any]:
    """Drive one full input sequence against ``module`` with a fake clock."""

    directory.mkdir(parents=True, exist_ok=True)
    reads = _scripted_reads()
    calls = {"n": 0}
    clicks: list[tuple[int, int]] = []
    drags: list[tuple[int, int, int, int]] = []
    flushes = {"n": 0}
    snapshots: list[list[dict[str, Any]]] = []
    # The camera only moves once the fixed minimap point has been clicked, so
    # the minimap predicate stays honest no matter where a read failure shifts
    # the call ordering.
    minimap_clicked = {"done": False}
    clock = [1000.0]

    def read_selection() -> dict[str, Any]:
        calls["n"] += 1
        if fail_call is not None and calls["n"] == fail_call:
            raise INJECTED[exc_kind]()
        index = min(calls["n"], len(reads)) - 1
        return dict(reads[index])

    def read_camera() -> list[int]:
        return [180, 240] if minimap_clicked["done"] else [100, 100]

    def send_click(x: int, y: int) -> None:
        clicks.append((x, y))
        if (x, y) == (150, 520):
            minimap_clicked["done"] = True

    inputs: list[dict[str, Any]] = []
    evidence: dict[str, Any] = {}

    def flush() -> None:
        flushes["n"] += 1
        module._g1_flush_input_stage(directory, evidence, inputs)
        snapshots.append(json.loads(json.dumps(inputs)))

    def wait(reader, predicate, message, **kwargs):
        return module._wait_state(
            reader, predicate, clock[0], 90.0, message, **kwargs,
        )

    error: BaseException | None = None
    with mock.patch.object(module.time, "monotonic", lambda: clock[0]), \
         mock.patch.object(module.time, "sleep",
                           lambda seconds: clock.__setitem__(0, clock[0] + seconds)):
        started = clock[0]
        try:
            module._g1_run_input_sequence(
                inputs=inputs, content_crop=CONTENT_CROP, scale=SCALE,
                capture=lambda tag: {"status": "CAPTURED", "tag": tag},
                runtime_state=lambda: {"ps": 3, "tick": 42},
                game_state=lambda: {"ps": 3, "tick": 42},
                read_selection=read_selection, read_camera=read_camera, wait=wait,
                click=send_click,
                drag=lambda x, y, tx, ty: drags.append((x, y, tx, ty)),
                read_production_cell=lambda: {"status": "UNAVAILABLE"},
                flush=flush, started=started, timeout=90.0,
            )
        except BaseException as exc:  # noqa: BLE001 - probe records any escape
            error = exc

    on_disk = json.loads((directory / "evidence.json").read_text(encoding="utf-8"))
    return {
        "error_type": type(error).__name__ if error is not None else None,
        "error_classification": getattr(error, "classification", None),
        "inputs": inputs,
        "on_disk_inputs": on_disk.get("inputs", []),
        "flush_count": flushes["n"],
        "snapshots": snapshots,
        "clicks": clicks,
        "drags": drags,
        "read_calls": calls["n"],
    }


def _by_tag(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {item["tag"]: item for item in items if "tag" in item}


def check_clean(module: ModuleType, root: Path) -> dict[str, Any]:
    """The unmodified PASS path must stay PASS with production BLOCKED."""

    result = run_sequence(module, root / "clean")
    by_tag = _by_tag(result["inputs"])
    results = {tag: item.get("result") for tag, item in by_tag.items()}
    unknowns = [item.get("result") for item in result["inputs"]
                if str(item.get("result", "")).startswith("UNKNOWN")]
    ok = (
        result["error_type"] is None
        and results == {"unit_select": "PASS", "production": "BLOCKED",
                        "drag_select": "PASS", "minimap": "PASS"}
        and not unknowns
        and result["clicks"] == [(410, 270), (150, 520)]
        and result["drags"] == [(350, 180, 550, 350)]
        and by_tag["production"].get("waited") is False
        and "selection_read_failure" not in by_tag["production"]
    )
    return {"ok": ok, "results": results, "clicks": result["clicks"],
            "drags": result["drags"], "unknown_results": unknowns,
            "error_type": result["error_type"]}


def check_raising_point(
    module: ModuleType, root: Path, call: int, tag: str, point: str, exc_kind: str,
) -> dict[str, Any]:
    """A direct failure must fail-close with provenance and be flushed to disk."""

    result = run_sequence(module, root / f"{point}_{exc_kind}", fail_call=call,
                          exc_kind=exc_kind)
    by_tag = _by_tag(result["inputs"])
    on_disk = _by_tag(result["on_disk_inputs"])
    entry = by_tag.get(tag, {})
    disk_entry = on_disk.get(tag, {})
    observation = entry.get("wait_observation") or {}
    provenance = observation.get("first_read_error_provenance")
    expected_prefix = {
        "oserror": "OSError:", "valueerror": "ValueError:", "structerror": "error:",
    }[exc_kind]
    findings = {
        "raised_wait_timeout": result["error_classification"] == "UNKNOWN_STATE_READ_FAILURE",
        "record_result": entry.get("result") == "UNKNOWN_STATE_READ_FAILURE",
        "record_timeout_cause": entry.get("timeout_cause") == "UNKNOWN_STATE_READ_FAILURE",
        "stage": observation.get("stage") == tag,
        "read_point": observation.get("direct_read_point") == point,
        "direct_reader": observation.get("direct_reader") == "selection",
        "direct_reader_failure": observation.get("direct_reader_failure") is True,
        "no_polls_counted": observation.get("poll_count") == 0
        and observation.get("poll_attempt_count") == 0,
        "error_counted": observation.get("direct_read_error_count") == 1
        and observation.get("read_error_count") == 1,
        "provenance_typed": isinstance(provenance, str)
        and provenance.startswith(expected_prefix),
        "provenance_first_equals_last":
            provenance == observation.get("last_read_error_provenance"),
        "predicate_not_observed": entry.get("predicate_observed") is False,
        "flushed_to_disk": disk_entry.get("result") == "UNKNOWN_STATE_READ_FAILURE",
        "no_pass_on_failed_stage": entry.get("result") != "PASS",
    }
    return {"ok": all(findings.values()), "findings": findings,
            "error_classification": result["error_classification"],
            "clicks": result["clicks"], "drags": result["drags"]}


def check_production_point(module: ModuleType, root: Path, exc_kind: str) -> dict[str, Any]:
    """The production read point must stay BLOCKED and not suppress later inputs."""

    result = run_sequence(module, root / f"production_{exc_kind}", fail_call=3,
                          exc_kind=exc_kind)
    by_tag = _by_tag(result["inputs"])
    production = by_tag.get("production", {})
    failure = production.get("selection_read_failure") or {}
    findings = {
        "no_escape": result["error_type"] is None,
        "blocked": production.get("result") == "BLOCKED",
        "not_waited": production.get("waited") is False,
        "failure_recorded": failure.get("direct_reader_failure") is True,
        "failure_point": failure.get("direct_read_point") == "before_production",
        "failure_stage": failure.get("stage") == "production",
        "later_stages_ran": [item.get("tag") for item in result["inputs"]] == [
            "unit_select", "production", "drag_select", "minimap"],
        "later_inputs_sent": result["clicks"] == [(410, 270), (150, 520)]
        and result["drags"] == [(350, 180, 550, 350)],
        "later_stages_pass": by_tag.get("drag_select", {}).get("result") == "PASS"
        and by_tag.get("minimap", {}).get("result") == "PASS",
    }
    return {"ok": all(findings.values()), "findings": findings}


def check_uncovered_exception(module: ModuleType, root: Path) -> dict[str, Any]:
    """A reader bug outside the covered types must not be silently classified."""

    directory = root / "uncovered"
    directory.mkdir(parents=True, exist_ok=True)
    reads = _scripted_reads()
    calls = {"n": 0}
    clock = [1000.0]
    inputs: list[dict[str, Any]] = []
    evidence: dict[str, Any] = {}

    clicked = {"done": False}

    def read_selection() -> dict[str, Any]:
        calls["n"] += 1
        if calls["n"] == 4:
            raise KeyError("unmodelled reader defect")
        return dict(reads[min(calls["n"], len(reads)) - 1])

    def click(x: int, y: int) -> None:
        if (x, y) == (150, 520):
            clicked["done"] = True

    error: BaseException | None = None
    with mock.patch.object(module.time, "monotonic", lambda: clock[0]), \
         mock.patch.object(module.time, "sleep",
                           lambda s: clock.__setitem__(0, clock[0] + s)):
        try:
            module._g1_run_input_sequence(
                inputs=inputs, content_crop=CONTENT_CROP, scale=SCALE,
                capture=lambda tag: {"status": "CAPTURED", "tag": tag},
                runtime_state=lambda: {"ps": 3, "tick": 42},
                game_state=lambda: {"ps": 3, "tick": 42},
                read_selection=read_selection,
                read_camera=lambda: [180, 240] if clicked["done"] else [100, 100],
                wait=lambda reader, predicate, message, **kw: module._wait_state(
                    reader, predicate, clock[0], 90.0, message, **kw),
                click=click, drag=lambda *a: None,
                read_production_cell=lambda: {"status": "UNAVAILABLE"},
                flush=lambda: module._g1_flush_input_stage(directory, evidence, inputs),
                started=clock[0], timeout=90.0,
            )
        except BaseException as exc:  # noqa: BLE001
            error = exc
    findings = {
        "propagated": isinstance(error, KeyError),
        "not_classified_as_read_failure":
            getattr(error, "classification", None) != "UNKNOWN_STATE_READ_FAILURE",
        "no_pass_claimed": all(item.get("result") != "PASS"
                               for item in inputs if item.get("tag") == "drag_select"),
    }
    return {"ok": all(findings.values()), "findings": findings,
            "error_type": type(error).__name__ if error is not None else None}


def _load_mutant(source: str, workdir: Path, name: str) -> ModuleType:
    path = workdir / f"{name}.py"
    path.write_text(source, encoding="utf-8")
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


MUTATIONS: tuple[tuple[str, str, str], ...] = (
    (
        "narrow_catch_to_oserror",
        "    try:\n        return read_selection()\n"
        "    except (OSError, ValueError, struct.error) as exc:",
        "    try:\n        return read_selection()\n    except OSError as exc:",
    ),
    (
        "relax_classification_to_fail_no_effect",
        'classification="UNKNOWN_STATE_READ_FAILURE",\n            last=None,',
        'classification="FAIL_NO_EFFECT",\n            last=None,',
    ),
    (
        "drop_read_point_provenance",
        '"direct_read_point": read_point,',
        '"direct_read_point": None,',
    ),
    (
        "swallow_direct_failure",
        "    try:\n        return read_selection()\n"
        "    except (OSError, ValueError, struct.error) as exc:",
        '    try:\n        return read_selection()\n'
        '    except (OSError, ValueError, struct.error) as exc:\n'
        '        if read_point == "after_drag":\n'
        '            return {"count": 2, "selected_slot": 1198, "selected_type": 21}',
    ),
    (
        "production_failure_aborts_later_inputs",
        "    except _G1WaitTimeout as exc:\n        # Production remains fail-closed",
        "    except _G1WaitTimeout as exc:\n        raise\n        # Production remains fail-closed",
    ),
)


def run_mutations(root: Path) -> list[dict[str, Any]]:
    original = SOURCE.read_text(encoding="utf-8")
    out: list[dict[str, Any]] = []
    for index, (name, old, new) in enumerate(MUTATIONS):
        occurrences = original.count(old)
        if occurrences != 1:
            out.append({"mutation": name, "applied": False, "detected": False,
                        "reason": f"anchor occurrences={occurrences}"})
            continue
        workdir = root / f"mut_{index}"
        workdir.mkdir(parents=True, exist_ok=True)
        module = _load_mutant(original.replace(old, new), workdir, f"runtime_env_mut{index}")
        checks: list[bool] = []
        for call, tag, point in RAISING_POINTS:
            for kind in INJECTED:
                checks.append(check_raising_point(
                    module, workdir / "raise", call, tag, point, kind)["ok"])
        for kind in INJECTED:
            checks.append(check_production_point(module, workdir / "prod", kind)["ok"])
        checks.append(check_clean(module, workdir / "clean")["ok"])
        out.append({"mutation": name, "applied": True, "detected": not all(checks),
                    "failed_checks": sum(1 for item in checks if not item),
                    "total_checks": len(checks)})
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    report: dict[str, Any] = {
        "lap": 240,
        "role": "middle",
        "scope": "G1 R6-B-R9 direct selection-reader failure diagnosis",
        "source": {
            "path": "tools/runtime_env.py",
            "sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        },
        "game_runs": 0,
        "product_assets_changed": 0,
    }
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        report["direct_call_sites"] = _direct_call_sites()
        report["clean_path"] = check_clean(runtime_env, root / "base")
        raising: list[dict[str, Any]] = []
        for call, tag, point in RAISING_POINTS:
            for kind in INJECTED:
                item = check_raising_point(
                    runtime_env, root / "base" / "raise", call, tag, point, kind)
                item.update({"read_point": point, "stage": tag, "exception": kind})
                raising.append(item)
        report["raising_points"] = raising
        report["production_point"] = [
            dict(check_production_point(runtime_env, root / "base" / "prod", kind),
                 exception=kind)
            for kind in INJECTED
        ]
        report["uncovered_exception"] = check_uncovered_exception(
            runtime_env, root / "base")
        report["mutations"] = run_mutations(root / "mut")

    failures = (
        [item for item in report["raising_points"] if not item["ok"]]
        + [item for item in report["production_point"] if not item["ok"]]
    )
    report["summary"] = {
        "raising_cases": len(report["raising_points"]),
        "raising_failures": len(
            [item for item in report["raising_points"] if not item["ok"]]),
        "production_cases": len(report["production_point"]),
        "production_failures": len(
            [item for item in report["production_point"] if not item["ok"]]),
        "clean_path_ok": report["clean_path"]["ok"],
        "uncovered_exception_ok": report["uncovered_exception"]["ok"],
        "call_site_coverage_ok": report["direct_call_sites"]["ok"],
        "mutations_total": len(report["mutations"]),
        "mutations_detected": sum(1 for item in report["mutations"] if item["detected"]),
    }
    verdict_ok = (
        not failures
        and report["clean_path"]["ok"]
        and report["uncovered_exception"]["ok"]
        and report["direct_call_sites"]["ok"]
        and report["summary"]["mutations_detected"] == report["summary"]["mutations_total"]
    )
    report["verdict"] = "PASS" if verdict_ok else "FAIL"

    args.report.parent.mkdir(parents=True, exist_ok=True)
    with open(args.report, "x", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps(report["summary"], ensure_ascii=False, sort_keys=True))
    print(f"verdict={report['verdict']}")
    return 0 if verdict_ok else 1


def _direct_call_sites() -> dict[str, Any]:
    """Every direct call site in the sequence must be a covered read point."""

    import ast
    import inspect
    tree = ast.parse(inspect.getsource(runtime_env._g1_run_input_sequence))
    points: list[str] = []
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "_g1_read_selection_stage"):
            for keyword in node.keywords:
                if keyword.arg == "read_point" and isinstance(keyword.value, ast.Constant):
                    points.append(str(keyword.value.value))
    covered = [point for _, _, point in DIRECT_POINTS]
    return {"ok": sorted(points) == sorted(covered) and len(points) == len(set(points)),
            "found": points, "covered": covered}


if __name__ == "__main__":
    raise SystemExit(main())
