#!/usr/bin/env python3
"""lap275 middle — independent review of the lap274 F3-R2-R1 repair.

Written fresh for this review. It does NOT import the lap274 regression test.
Game/Wine/Xvfb budget is zero; only offline synthetic fixtures are used.

Checks
  A. Producer vocabulary derived by this probe's own AST walk over
     tools/runtime_env.py (every literal reaching `classification=` and every
     literal in the `classification = (... if ... else ...)` chain) equals the
     comparator's `_DISPUTED_SOURCE_RESULTS`, in both directions.
  B. The classification really reaches the field the comparator reads
     (`inputs[i]["result"]`) via record_timeout.
  C. Exhaustive matrix over an extended result vocabulary: stage status and
     overall status for every (baseline_result, candidate_result) pair.
  D. No non-(PASS,PASS) pair yields a stage PASS.
  E. Invariants: hard FAIL priority, scene-mismatch gate, slot demotion,
     production NOT_COMPARED.
"""
from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from tools.compare_g1_stage_b import (  # noqa: E402
    _DISPUTED_SOURCE_RESULTS,
    compare_evidence,
)

PRODUCER = ROOT / "tools" / "runtime_env.py"


# --- A: independent AST extraction of the producer vocabulary --------------
def producer_vocabulary() -> set[str]:
    tree = ast.parse(PRODUCER.read_text(encoding="utf-8"))
    found: set[str] = set()

    def literals(node: ast.AST) -> set[str]:
        """All str constants reachable through conditional expressions."""
        out: set[str] = set()
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            out.add(node.value)
        elif isinstance(node, ast.IfExp):
            out |= literals(node.body)
            out |= literals(node.orelse)
        return out

    for node in ast.walk(tree):
        # keyword argument: raise _G1WaitTimeout(..., classification=<expr>)
        if isinstance(node, ast.Call):
            for kw in node.keywords:
                if kw.arg == "classification":
                    found |= literals(kw.value)
        # assignment: classification = (<IfExp chain>)
        if isinstance(node, ast.Assign):
            names = {t.id for t in node.targets if isinstance(t, ast.Name)}
            if "classification" in names:
                found |= literals(node.value)
    return found


# --- B: the classification reaches inputs[i]["result"] ---------------------
def classification_reaches_result() -> bool:
    """record_timeout passes exc.classification positionally as `result`."""
    tree = ast.parse(PRODUCER.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if not (isinstance(node, ast.FunctionDef) and node.name == "record_timeout"):
            continue
        for call in ast.walk(node):
            if not (isinstance(call, ast.Call) and isinstance(call.func, ast.Name)
                    and call.func.id == "record"):
                continue
            # record(stage_entry, tag, x, y, before, expected, after, actual, result, extra)
            if len(call.args) < 9:
                continue
            arg = call.args[8]
            if (isinstance(arg, ast.Attribute) and arg.attr == "classification"
                    and isinstance(arg.value, ast.Name) and arg.value.id == "exc"):
                return True
    return False


# --- C/D/E: synthetic fixtures --------------------------------------------
def make_evidence(results: dict[str, str | None], *,
                  slot_shift: int = 0,
                  drop_result: frozenset[str] = frozenset()) -> dict:
    """Offline synthetic Stage B evidence in the real comparator schema."""
    units = [
        {"slot": 1199 + slot_shift, "owner": 0, "type": 7,
         "world": {"x": 100, "y": 200}},
        {"slot": 1200 + slot_shift, "owner": 0, "type": 21,
         "world": {"x": 140, "y": 200}},
        {"slot": 5, "owner": 1, "type": 70, "world": {"x": 900, "y": 800}},
    ]
    sel_slot = 1199 + slot_shift
    inputs: list[dict] = []
    for tag in ("unit_select", "drag_select"):
        entry: dict = {
            "tag": tag,
            "content": [10, 20] if tag == "unit_select" else [12, 22],
            "before": {"selection": {"count": 0, "selected_slot": sel_slot,
                                     "selected_type": 7}},
            "after": {"selection": {"count": 1, "selected_slot": sel_slot,
                                    "selected_type": 7}},
        }
        if tag == "drag_select":
            entry["before"]["drag_to"] = {"content": [300, 400]}
        if tag not in drop_result:
            entry["result"] = results[tag]
        inputs.append(entry)
    minimap: dict = {
        "tag": "minimap",
        "content": [30, 40],
        "before": {"camera": [0, 0]},
        "after": {"camera": [512, 256]},
    }
    if "minimap" not in drop_result:
        minimap["result"] = results["minimap"]
    inputs.append(minimap)
    inputs.append({"tag": "production", "content": [1, 1], "result": "BLOCKED"})
    return {
        "scene": {"unit_slots": units,
                  "world_bounds": {"width": 4096, "height": 4096}},
        "inputs": inputs,
    }


def stage_of(report, tag):
    return report["stages"][tag]["status"]


def main() -> int:
    failures: list[str] = []
    notes: dict[str, object] = {}

    # --- A ---
    vocab = producer_vocabulary()
    declared = set(_DISPUTED_SOURCE_RESULTS)
    notes["producer_vocabulary"] = sorted(vocab)
    notes["comparator_declared"] = sorted(declared)
    notes["producer_only"] = sorted(vocab - declared)
    notes["comparator_only"] = sorted(declared - vocab)
    if vocab != declared:
        failures.append(f"A: vocabulary drift producer={sorted(vocab)} "
                        f"comparator={sorted(declared)}")
    if len(vocab) != 6:
        failures.append(f"A: expected 6 species, got {len(vocab)}")

    # --- B ---
    reaches = classification_reaches_result()
    notes["classification_reaches_result_field"] = reaches
    if not reaches:
        failures.append("B: classification does not reach inputs[i]['result']")

    # --- C/D: exhaustive matrix ---
    extended = sorted(vocab) + ["PASS", "FAIL", "BLOCKED", "SKIP",
                                "TOTALLY_UNKNOWN_TOKEN", None, 12345]
    expected_stage = {}
    for value in extended:
        if value == "PASS":
            expected_stage[repr(value)] = "PASS"
        elif value == "FAIL":
            expected_stage[repr(value)] = "FAIL"
        elif isinstance(value, str) and value in vocab:
            expected_stage[repr(value)] = "UNKNOWN_DISPUTED_ORACLE"
        else:
            expected_stage[repr(value)] = "INCONCLUSIVE"

    matrix = []
    pass_pairs = []
    for b in extended:
        for c in extended:
            base = make_evidence({t: b for t in ("unit_select", "drag_select",
                                                 "minimap")})
            cand = make_evidence({t: c for t in ("unit_select", "drag_select",
                                                 "minimap")})
            report = compare_evidence(base, cand)
            st = stage_of(report, "unit_select")
            matrix.append({"baseline": b, "candidate": c, "stage": st,
                           "overall": report["status"]})
            if st == "PASS":
                pass_pairs.append((b, c))
            # expected stage: hard FAIL wins, then disputed, then inconclusive
            if b == "FAIL" or c == "FAIL":
                want = "FAIL"
            elif (isinstance(b, str) and b in vocab) or (isinstance(c, str) and c in vocab):
                want = "UNKNOWN_DISPUTED_ORACLE"
            elif b == "PASS" and c == "PASS":
                want = "PASS"
            else:
                want = "INCONCLUSIVE"
            if st != want:
                failures.append(f"C: ({b!r},{c!r}) stage={st} want={want}")
            # overall must never be PASS unless stage is PASS everywhere
            if report["status"] == "PASS" and not (b == "PASS" and c == "PASS"):
                failures.append(f"D: overall PASS for ({b!r},{c!r})")
            if report["production"]["status"] != "NOT_COMPARED":
                failures.append(f"E: production compared for ({b!r},{c!r})")

    notes["matrix_cells"] = len(matrix)
    notes["stage_pass_pairs"] = [[b, c] for b, c in pass_pairs]
    if pass_pairs != [("PASS", "PASS")]:
        failures.append(f"D: unexpected PASS pairs {pass_pairs}")

    # --- E: missing result key must not be treated as disputed or PASS ---
    for tag in ("unit_select", "drag_select", "minimap"):
        base = make_evidence({t: "PASS" for t in ("unit_select", "drag_select", "minimap")},
                             drop_result=frozenset({tag}))
        cand = make_evidence({t: "PASS" for t in ("unit_select", "drag_select", "minimap")})
        report = compare_evidence(base, cand)
        if stage_of(report, tag) != "INCONCLUSIVE" or report["status"] != "INCONCLUSIVE":
            failures.append(f"E: missing result for {tag} -> "
                            f"{stage_of(report, tag)}/{report['status']}")

    # --- E: scene gate overrides everything, including hard FAIL ---
    base = make_evidence({t: "FAIL" for t in ("unit_select", "drag_select", "minimap")})
    cand = make_evidence({t: "FAIL" for t in ("unit_select", "drag_select", "minimap")})
    cand["scene"]["unit_slots"][0]["type"] = 99
    report = compare_evidence(base, cand)
    notes["scene_gate"] = {"overall": report["status"],
                           "stage": stage_of(report, "unit_select")}
    if report["status"] != "UNKNOWN_SCENE_MISMATCH":
        failures.append(f"E: scene gate overall={report['status']}")
    if stage_of(report, "unit_select") != "UNKNOWN_SCENE_MISMATCH":
        failures.append("E: scene gate did not mask stages")

    # --- E: slot demotion on an otherwise-PASS pair ---
    base = make_evidence({t: "PASS" for t in ("unit_select", "drag_select", "minimap")})
    cand = make_evidence({t: "PASS" for t in ("unit_select", "drag_select", "minimap")},
                         slot_shift=-1000)
    report = compare_evidence(base, cand)
    notes["slot_demotion"] = {"overall": report["status"],
                              "unit_select": stage_of(report, "unit_select"),
                              "drag_select": stage_of(report, "drag_select")}
    if stage_of(report, "unit_select") != "UNKNOWN_SLOT_CORRESPONDENCE":
        failures.append(f"E: slot demotion -> {stage_of(report, 'unit_select')}")
    if report["status"] != "INCONCLUSIVE":
        failures.append(f"E: slot demotion overall={report['status']}")

    # --- M0 control: identical evidence with all-PASS results ---
    base = make_evidence({t: "PASS" for t in ("unit_select", "drag_select", "minimap")})
    report = compare_evidence(base, copy.deepcopy(base))
    notes["control_pass"] = report["status"]
    if report["status"] != "PASS":
        failures.append(f"M0: control did not PASS ({report['status']})")

    out = {"verdict": "PASS" if not failures else "FAIL",
           "failures": failures, "notes": notes}
    print(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
