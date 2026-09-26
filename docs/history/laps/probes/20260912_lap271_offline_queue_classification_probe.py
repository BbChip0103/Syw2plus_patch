#!/usr/bin/env python3
"""lap271 middle-tier classification of the offline defect queue (Astra item 3).

Astra item 3 (lap267) asked the middle tier to decide, per offline defect,
whether it actually sits on a **real Stage B producer/comparator call path**, so
that only the genuine prerequisites block Stage B and historical-probe-only
defects are not mistaken for product gates.  This probe supplies the machine
evidence for that classification; it decides nothing by itself.

Queue under classification: R20, R21, R22, R23, R24, F2-R1, F3-R1, F3-R2, F6-R2.

Producer  = ``tools/runtime_env.py``   (writes g1 Stage B evidence)
Comparator= ``tools/compare_g1_stage_b.py`` (turns two evidence files into a card)

Axes:
  A1  ``_stage_report`` caller census  -> is the F2-R1 evidence=None fallback
      reachable from any real call path?
  A2  ``after.last`` producer census   -> can a stage with ``result == "PASS"``
      ever carry an ``after.last`` shape (F3-R1)?
  A3  F3-R2 reachability, executed against the real comparator with the literal
      result strings the producer flushes ("FAIL", "BLOCKED", "SKIP") plus the
      five timeout classifications the producer can emit today.
  A4  consumer census for ``read_coverage`` / ``read_failure`` / record-level
      ``selection_count`` inside the two gate tools (R23/R24).
  A5  evidence-write ordering in the producer (R21): does the product path have
      the "create the file, then discover the payload is unserialisable" window?
  A6  location census for the harness-only defects (R20/R21/R22).

Nothing in the repository is modified.  No game, Wine, Xvfb or PNG.  Machine
tier 1 evidence only; this is not a product G1 verdict.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT))

COMPARATOR_REL = "tools/compare_g1_stage_b.py"
PRODUCER_REL = "tools/runtime_env.py"
GATE_RELS = (COMPARATOR_REL, "tools/check_runtime_evidence.py")

import tools.compare_g1_stage_b as compare  # noqa: E402


# ---------------------------------------------------------------- A1: F2-R1

def a1_stage_report_callers() -> dict[str, object]:
    """Every real call of ``_stage_report`` must pass both evidence arguments."""
    source = (ROOT / COMPARATOR_REL).read_text(encoding="utf-8")
    tree = ast.parse(source)
    calls: list[dict[str, object]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                and node.func.id == "_stage_report":
            calls.append({
                "line": node.lineno,
                "positional_args": len(node.args),
                "keywords": sorted(kw.arg for kw in node.keywords if kw.arg),
            })
    # Repository-wide reference census outside the defining module.
    external: list[str] = []
    for path in sorted(ROOT.rglob("*.py")):
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith("docs/history/") or rel == COMPARATOR_REL or ".venv" in rel:
            continue
        if "_stage_report" in path.read_text(encoding="utf-8"):
            external.append(rel)
    signature = next(n for n in ast.walk(tree)
                     if isinstance(n, ast.FunctionDef) and n.name == "_stage_report")
    defaulted = [a.arg for a in signature.args.args[-len(signature.args.defaults):]] \
        if signature.args.defaults else []
    return {
        "call_sites": calls,
        "external_reference_files": external,
        "evidence_params_have_none_defaults": defaulted,
        # 5 positional args == tag, baseline, candidate, baseline_evidence,
        # candidate_evidence, i.e. the fallback branch is not taken.
        "all_calls_supply_evidence": all(
            int(c["positional_args"]) >= 5 or {"baseline_evidence", "candidate_evidence"}
            <= set(c["keywords"]) for c in calls),  # type: ignore[arg-type]
    }


# ---------------------------------------------------------------- A2: F3-R1

def a2_after_last_producer() -> dict[str, object]:
    """``after.last`` is only ever written by the timeout recorder."""
    source = (ROOT / PRODUCER_REL).read_text(encoding="utf-8")
    lines = source.splitlines()
    sites = [{"line": i + 1, "text": line.strip()}
             for i, line in enumerate(lines) if '"last":' in line]
    tree = ast.parse(source)
    enclosing: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            segment = "\n".join(lines[node.lineno - 1:(node.end_lineno or node.lineno)])
            if '"last":' in segment:
                enclosing.append(node.name)
    return {
        "after_last_write_sites": sites,
        "enclosing_functions": sorted(set(enclosing)),
        # The single site passes ``exc.classification`` as the stage result, so a
        # stage carrying ``after.last`` is never ``result == "PASS"``.
        "site_count": len(sites),
    }


# ---------------------------------------------------------------- A3: F3-R2

def _scene(offset: int = 0) -> dict[str, object]:
    return {
        "world_bounds": {"width": 4096, "height": 4096},
        "unit_slots": [
            {"slot": 11 + offset, "owner": 0, "type": 7, "world": {"x": 100, "y": 100}},
            {"slot": 12 + offset, "owner": 0, "type": 9, "world": {"x": 140, "y": 100}},
            {"slot": 21 + offset, "owner": 1, "type": 7, "world": {"x": 900, "y": 900}},
        ],
    }


def _selection_stage(tag: str, result: str, *, slot: int, after_count: int) -> dict[str, object]:
    stage: dict[str, object] = {
        "tag": tag,
        "content": [410, 270],
        "before": {"selection": {"status": "OK", "count": 0,
                                 "selected_slot": slot, "selected_type": 7}},
        "after": {"selection": {"status": "OK", "count": after_count,
                                "selected_slot": slot, "selected_type": 7}},
        "result": result,
    }
    if tag == "drag_select":
        before = stage["before"]
        assert isinstance(before, dict)
        before["drag_to"] = {"content": [520, 360]}
    return stage


def _minimap_stage(result: str, *, camera_after: list[int]) -> dict[str, object]:
    return {
        "tag": "minimap",
        "content": [700, 520],
        "before": {"camera": [0, 0]},
        "after": {"camera": camera_after},
        "result": result,
    }


def _evidence(*, slot: int, minimap_result: str, camera_after: list[int],
              select_result: str = "PASS") -> dict[str, object]:
    return {
        "scene": _scene(),
        "inputs": [
            _selection_stage("unit_select", select_result, slot=slot, after_count=1),
            _selection_stage("drag_select", select_result, slot=slot, after_count=2),
            _minimap_stage(minimap_result, camera_after=camera_after),
        ],
    }


PRODUCER_RESULT_STRINGS = ("FAIL", "BLOCKED", "SKIP", "FAIL_NO_EFFECT",
                           "UNKNOWN_BUDGET_EXHAUSTED",
                           "UNKNOWN_OBSERVATION_WINDOW_TRUNCATED",
                           "UNKNOWN_STATE_READ_FAILURE",
                           "UNKNOWN_SELECTION_OBSERVATION_CORRUPTED")


def a3_f3r2_reachability() -> dict[str, object]:
    """A candidate that genuinely failed must still be able to reach card FAIL."""
    cases: dict[str, object] = {}

    # Control: both sides PASS and agree -> card PASS is still reachable.
    control = compare.compare_evidence(
        _evidence(slot=11, minimap_result="PASS", camera_after=[300, 300]),
        _evidence(slot=11, minimap_result="PASS", camera_after=[300, 300]))
    cases["control_both_pass"] = {
        "overall": control["status"],
        "minimap_stage": control["stages"]["minimap"]["status"],
    }

    # The F3-R2 scenario: the candidate's minimap genuinely did not move, and
    # the producer flushed the hard string "FAIL" (tools/runtime_env.py:2844).
    for result in PRODUCER_RESULT_STRINGS:
        report = compare.compare_evidence(
            _evidence(slot=11, minimap_result="PASS", camera_after=[300, 300]),
            _evidence(slot=11, minimap_result=result, camera_after=[0, 0]))
        cases[f"candidate_minimap_result_{result}"] = {
            "overall": report["status"],
            "minimap_stage": report["stages"]["minimap"]["status"],
            "camera_moved_candidate": False,
        }

    # Same defect on the selection axis: a hard FAIL there is also absorbed.
    selection = compare.compare_evidence(
        _evidence(slot=11, minimap_result="PASS", camera_after=[300, 300]),
        _evidence(slot=11, minimap_result="PASS", camera_after=[300, 300],
                  select_result="FAIL"))
    cases["candidate_unit_select_result_FAIL"] = {
        "overall": selection["status"],
        "unit_select_stage": selection["stages"]["unit_select"]["status"],
    }

    # Direction check: does any of this create a *new* PASS?  It must not.
    laundered = [name for name, value in cases.items()
                 if name != "control_both_pass"
                 and isinstance(value, dict) and value.get("overall") == "PASS"]
    return {"cases": cases, "new_pass_paths": laundered}


# ------------------------------------------------------------ A4: R23 / R24

def a4_gate_consumers() -> dict[str, object]:
    fields = ("read_coverage", "read_failure", "selection_count",
              "stage_budget_state")
    census: dict[str, object] = {}
    for field in fields:
        per_file = {}
        for rel in GATE_RELS:
            text = (ROOT / rel).read_text(encoding="utf-8")
            per_file[rel] = text.count(f'"{field}"') + text.count(f"'{field}'")
        census[field] = per_file
    # The comparator's own "selection_count" is a key it *writes* into details,
    # not a record field it reads; record which side of that line each hit is on.
    comparator = (ROOT / COMPARATOR_REL).read_text(encoding="utf-8")
    census["comparator_selection_count_context"] = [
        line.strip() for line in comparator.splitlines() if "selection_count" in line]
    # Fail-closed check: a record whose counts are absent must not reach PASS.
    missing = _evidence(slot=11, minimap_result="PASS", camera_after=[300, 300])
    inputs = missing["inputs"]
    assert isinstance(inputs, list)
    stage = inputs[0]
    assert isinstance(stage, dict)
    after = stage["after"]
    assert isinstance(after, dict)
    after["selection"] = {"status": "UNAVAILABLE", "count": None,
                          "selected_slot": 11, "selected_type": 7}
    report = compare.compare_evidence(
        _evidence(slot=11, minimap_result="PASS", camera_after=[300, 300]), missing)
    census["absent_count_is_fail_closed"] = {
        "overall": report["status"],
        "unit_select_stage": report["stages"]["unit_select"]["status"],
    }
    return census


# ------------------------------------------------------------------ A5: R21

def a5_producer_write_ordering() -> dict[str, object]:
    source = (ROOT / PRODUCER_REL).read_text(encoding="utf-8")
    tree = ast.parse(source)
    writer = next((n for n in ast.walk(tree)
                   if isinstance(n, ast.FunctionDef) and n.name == "_write_json"), None)
    body = "" if writer is None else "\n".join(
        source.splitlines()[writer.lineno - 1:(writer.end_lineno or writer.lineno)])
    return {
        "writer_found": writer is not None,
        "serialises_before_write": "json.dumps" in body and "write_text" in body,
        "atomic_replace": ".replace(" in body,
        "exclusive_create_in_tools": sum(
            len(re.findall(r"""open\(\s*["']x["']""", (ROOT / rel).read_text(encoding="utf-8")))
            for rel in [p.relative_to(ROOT).as_posix()
                        for p in sorted((ROOT / "tools").rglob("*.py"))]),
        "writer_body": body,
    }


# ------------------------------------------------------- A6: R20 / R21 / R22

def a6_harness_locality() -> dict[str, object]:
    markers = {
        "R21_exclusive_create": r"""open\(\s*["']x["']""",
        "R20_mirror_control": r"M0_control",
        "R22_review_probe_test": r"test_review_probe_output",
    }
    census: dict[str, object] = {}
    for name, pattern in markers.items():
        hits = {"tools": 0, "tests": 0, "docs/history/laps/probes": 0}
        for root_name in hits:
            for path in sorted((ROOT / root_name).rglob("*.py")):
                hits[root_name] += len(re.findall(
                    pattern, path.read_text(encoding="utf-8")))
        census[name] = hits
    return census


payload = {
    "lap": 271,
    "item": "offline_queue_stage_b_call_path_classification",
    "role": "middle",
    "astra_item": 3,
    "a1_f2r1_stage_report_callers": a1_stage_report_callers(),
    "a2_f3r1_after_last_producer": a2_after_last_producer(),
    "a3_f3r2_reachability": a3_f3r2_reachability(),
    "a4_r23_r24_gate_consumers": a4_gate_consumers(),
    "a5_r21_producer_write_ordering": a5_producer_write_ordering(),
    "a6_harness_locality": a6_harness_locality(),
}

out_path = HERE.with_name("20260912_lap271_offline_queue_classification_report.json")
if out_path.exists():
    print(f"refusing to overwrite existing evidence: {out_path}")
    raise SystemExit(2)
out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(payload, indent=2, sort_keys=True))
print(f"report -> {out_path}")
