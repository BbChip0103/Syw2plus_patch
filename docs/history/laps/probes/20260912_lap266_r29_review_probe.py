#!/usr/bin/env python3
"""lap266 middle-tier independent review of R29.

R29 (lap265 work) re-anchored ``_review_body_lines()`` in
``tests/test_review_probe_output.py``: the review body is now the closed line
interval from the first top-level ``NEGATIVE_PATTERNS`` assignment through the
independently located ``json.dump`` report write, instead of "every top-level
statement below the first ``__name__`` preflight If".  The claim is that this
closes the lap264 M7 survivor (moving the preflight block down to just above the
report write, so the whole review body runs before the existing-evidence
refusal, while the shipped helper's body set stayed non-empty and still held the
``json.dump`` anchor).

This probe re-derives both contracts from the SUT without importing the shipped
test helper, runs a depth-matched mirror control, re-measures the lap264
mutation matrix, and adds a new relocation mutant aimed at R29's own anchor.

No game, Wine, Xvfb or PNG.  Read-only against the repository; every mutation is
applied to a throwaway /tmp mirror.
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[4]
PROBE_REL = "docs/history/laps/probes/20260912_lap228_r6b_r3_review_probe.py"
TEST_REL = "tests/test_review_probe_output.py"
PYTHON = str(ROOT / ".venv/bin/python")

report: dict[str, object] = {"lap": 266, "item": "R29", "role": "middle"}


# ----------------------------------------------------------------- helpers ---
def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _top_level_dump_lines(tree: ast.Module) -> list[int]:
    return [
        child.lineno
        for node in tree.body
        for child in ast.walk(node)
        if isinstance(child, ast.Expr)
        and isinstance(child.value, ast.Call)
        and isinstance(child.value.func, ast.Attribute)
        and isinstance(child.value.func.value, ast.Name)
        and child.value.func.value.id == "json"
        and child.value.func.attr == "dump"
    ]


def derive_r29_contract(src: str) -> dict[str, object]:
    """Re-derive R29's interval contract; deliberately does NOT import the test."""
    tree = ast.parse(src)
    anchors = [
        node.lineno
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(t, ast.Name) and t.id == "NEGATIVE_PATTERNS"
            for t in node.targets
        )
    ]
    dumps = _top_level_dump_lines(tree)
    preflight = [
        n for n in tree.body
        if isinstance(n, ast.If)
        and isinstance(n.test, ast.Compare)
        and isinstance(n.test.left, ast.Name)
        and n.test.left.id == "__name__"
    ]
    start = anchors[0] if anchors else None
    end = dumps[0] if dumps else None
    body = set(range(start, end + 1)) if (start is not None and end is not None) else set()
    return {
        "anchor_count": len(anchors),
        "anchor_lines": anchors,
        "review_start": start,
        "report_write_line": end,
        "json_dump_count": len(dumps),
        "preflight_count": len(preflight),
        "preflight_start": preflight[0].lineno if preflight else None,
        "preflight_end": preflight[0].end_lineno if preflight else None,
        "body_lines": sorted(body),
    }


def derive_semantic_body(src: str) -> set[int]:
    """Role-independent notion of "review body": every executable module-level
    statement that is not an import, a def/class, or the ``__name__`` preflight
    If.  Unlike an interval between two movable anchors, this set cannot be
    shrunk by relocating the preflight or by adding a decoy anchor."""
    tree = ast.parse(src)
    body: set[int] = set()
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef,
                             ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        if (isinstance(node, ast.If) and isinstance(node.test, ast.Compare)
                and isinstance(node.test.left, ast.Name)
                and node.test.left.id == "__name__"):
            continue
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            continue  # module docstring
        body.update(range(node.lineno, (node.end_lineno or node.lineno) + 1))
    return body


TRACER = (
    "import json, runpy, sys\n"
    "target = sys.argv[1]\n"
    "seen = set()\n"
    "def hook(frame, event, arg):\n"
    "    if event == 'line' and frame.f_code.co_filename == target:\n"
    "        seen.add(frame.f_lineno)\n"
    "    return hook\n"
    "sys.argv = [target] + sys.argv[2:]\n"
    "sys.settrace(hook)\n"
    "code = 0\n"
    "try:\n"
    "    runpy.run_path(target, run_name='__main__')\n"
    "except SystemExit as exc:\n"
    "    code = exc.code\n"
    "finally:\n"
    "    sys.settrace(None)\n"
    "sys.stderr.write(json.dumps({'code': code, 'seen': sorted(seen)}))\n"
)


def trace_probe(probe: Path, output: Path, workdir: Path) -> tuple[int, set[int], str]:
    tracer = workdir / "_trace.py"
    tracer.write_text(TRACER, encoding="utf-8")
    res = subprocess.run(
        [PYTHON, str(tracer), str(probe), "--output", str(output)],
        capture_output=True, text=True, check=False, cwd=str(workdir),
    )
    payload = json.loads(res.stderr.strip().splitlines()[-1])
    return payload["code"], set(payload["seen"]), res.stdout


# --------------------------------------------------------------------- C1 ---
src = (ROOT / PROBE_REL).read_text(encoding="utf-8")
contract = derive_r29_contract(src)
body_set = set(contract["body_lines"])                       # type: ignore[arg-type]
semantic_set = derive_semantic_body(src)
report["C1_contract"] = {
    k: v for k, v in contract.items() if k != "body_lines"
} | {
    "body_line_count": len(body_set),
    "body_first": min(body_set),
    "body_last": max(body_set),
    "semantic_body_line_count": len(semantic_set),
    "semantic_minus_helper": len(semantic_set - body_set),
    "helper_minus_semantic": len(body_set - semantic_set),
}

with tempfile.TemporaryDirectory(prefix="lap266_c1_") as td:
    work = Path(td)
    ok_code, ok_seen, _ = trace_probe(ROOT / PROBE_REL, work / "fresh.json", work)
    existing = work / "existing.json"
    existing.write_text("preserve this historical evidence\n", encoding="utf-8")
    ref_code, ref_seen, ref_out = trace_probe(ROOT / PROBE_REL, existing, work)
    report["C1_controls"] = {
        "positive_rc": ok_code,
        "positive_helper_body_lines_executed": len(ok_seen & body_set),
        "positive_semantic_body_lines_executed": len(ok_seen & semantic_set),
        "refusal_rc": ref_code,
        "refusal_helper_body_lines_executed": len(ref_seen & body_set),
        "refusal_semantic_body_lines_executed": len(ref_seen & semantic_set),
        "refusal_message": "refusing to overwrite existing evidence" in ref_out,
        "evidence_preserved": existing.read_text(encoding="utf-8")
        == "preserve this historical evidence\n",
    }


# ------------------------------------------------------------------ mirror ---
def build_mirror(dest: Path) -> None:
    (dest / "docs/history/laps/probes").mkdir(parents=True)
    (dest / "tools").mkdir(parents=True)
    (dest / "tests").mkdir(parents=True)
    shutil.copy2(ROOT / PROBE_REL, dest / PROBE_REL)
    shutil.copy2(ROOT / "tools/runtime_env.py", dest / "tools/runtime_env.py")
    shutil.copy2(ROOT / TEST_REL, dest / TEST_REL)
    shutil.copy2(ROOT / "tests/conftest.py", dest / "tests/conftest.py")
    shutil.copy2(ROOT / "pyproject.toml", dest / "pyproject.toml")


def run_suite(mirror: Path) -> dict[str, object]:
    res = subprocess.run(
        [PYTHON, "-m", "pytest", "-q", "tests/test_review_probe_output.py"],
        capture_output=True, text=True, check=False, cwd=str(mirror),
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    tail = res.stdout.strip().splitlines()[-1] if res.stdout.strip() else ""
    passed = int(m.group(1)) if (m := re.search(r"(\d+) passed", res.stdout)) else 0
    failed = int(m.group(1)) if (m := re.search(r"(\d+) failed", res.stdout)) else 0
    errors = int(m.group(1)) if (m := re.search(r"(\d+) error", res.stdout)) else 0
    return {"rc": res.returncode, "passed": passed, "failed": failed,
            "errors": errors, "tail": tail}


# --------------------------------------------------------------- mutations ---
PREFLIGHT_START = contract["preflight_start"]   # type: ignore[index]
PREFLIGHT_END = contract["preflight_end"]       # type: ignore[index]
ANCHOR = 'try:\n    with args.output.open("x", encoding="utf-8") as stream:\n'


def _lift_preflight(text: str) -> tuple[str, str]:
    """Return (preflight block text, text with that block removed)."""
    lines = text.splitlines(keepends=True)
    block = lines[PREFLIGHT_START - 1:PREFLIGHT_END]
    assert block[0].startswith('if __name__ == "__main__":'), block[0]
    rest = "".join(lines[:PREFLIGHT_START - 1] + lines[PREFLIGHT_END:])
    return "".join(block), rest


def mut_rename(text: str) -> str:
    return text.replace("drive_wait", "drive_pause")


def mut_late_refusal(text: str) -> str:
    """Keep the exists() call and its OSError classification, skip the refusal."""
    assert "        if path.exists():\n" in text
    return text.replace("        if path.exists():\n",
                        "        if path.exists() and False:\n", 1)


def mut_relocate_to_tail(text: str) -> str:
    """lap262 M6: first top-level ``__name__`` If no longer precedes the body."""
    out = text.replace(
        'if __name__ == "__main__":\n',
        '_IS_MAIN = __name__ == "__main__"\nif _IS_MAIN:\n', 1)
    out += '\n\nif __name__ == "__main__":\n    pass\n'
    return out


def mut_relocate_before_report(text: str) -> str:
    """lap264 M7: preflight block moved down to just above the report write."""
    block, rest = _lift_preflight(text)
    assert ANCHOR in rest
    return rest.replace(ANCHOR, block + "\n\n" + ANCHOR, 1)


def mut_decoy_anchor(text: str) -> str:
    """NEW lap266 M8: M7 plus a decoy that moves R29's own anchor.

    The real constant is renamed and a late ``NEGATIVE_PATTERNS`` alias is placed
    *below* the relocated preflight block.  ``_review_body_lines()`` then pins a
    handful of trailing lines that the refusal never reaches, while the entire
    review body still executes before the existing-evidence refusal -- the exact
    defect R17 exists to catch.
    """
    renamed = text.replace("NEGATIVE_PATTERNS", "NEG_PATTERNS_SRC")
    block, rest = _lift_preflight(renamed)
    assert ANCHOR in rest
    injection = block + "\nNEGATIVE_PATTERNS = NEG_PATTERNS_SRC\n\n"
    return rest.replace(ANCHOR, injection + ANCHOR, 1)


MUTATIONS = {
    "M0_control": lambda t: t,
    "M1_rename_only": mut_rename,
    "M2_late_refusal": mut_late_refusal,
    "M3_late_refusal_plus_rename": lambda t: mut_rename(mut_late_refusal(t)),
    "M6_relocate_tail_plus_late_refusal": lambda t: mut_relocate_to_tail(mut_late_refusal(t)),
    "M7_relocate_above_report_write": mut_relocate_before_report,
    "M8_decoy_anchor_above_report_write": mut_decoy_anchor,
}

# Test-side variants for the load-bearing (C4) checks.
R29_GUARD = re.compile(r"\n    # R29 anchors.*?\n    \)\n", re.S)


def strip_r29(test_text: str) -> str:
    """Drop only R29's ordering assertion, keeping the interval derivation."""
    out, n = R29_GUARD.subn("\n", test_text)
    assert n == 1, "R29 guard block not located"
    return out


def restore_r28_anchor(test_text: str) -> str:
    """Revert R29's anchor to R28's preflight-relative one (pre-R29 behaviour)."""
    old = """    review_start = next(
        node.lineno
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "NEGATIVE_PATTERNS"
            for target in node.targets
        )
    )
"""
    new = """    preflight_end = next(
        node.end_lineno
        for node in tree.body
        if isinstance(node, ast.If)
        and isinstance(node.test, ast.Compare)
        and isinstance(node.test.left, ast.Name)
        and node.test.left.id == "__name__"
    )
    review_start = preflight_end + 1
"""
    assert old in test_text, "R29 anchor block not located"
    return test_text.replace(old, new, 1)


def strip_r17(test_text: str) -> str:
    marker = "def test_r6b_r17_existing_evidence_refusal_precedes_review_body"
    idx = test_text.index(marker)
    return test_text[:idx].rstrip("\n") + "\n"


results: dict[str, object] = {}
survivors: list[str] = []

with tempfile.TemporaryDirectory(prefix="lap266_mut_") as td:
    base = Path(td)
    for name, fn in MUTATIONS.items():
        mirror = base / name
        build_mirror(mirror)
        mutated = fn((mirror / PROBE_REL).read_text(encoding="utf-8"))
        (mirror / PROBE_REL).write_text(mutated, encoding="utf-8")
        outcome = run_suite(mirror)
        mc = derive_r29_contract(mutated)
        outcome["mutant_contract"] = {
            k: (len(v) if k == "body_lines" else v) for k, v in mc.items()
        }
        results[name] = outcome
        if name != "M0_control" and outcome["failed"] == 0 and outcome["errors"] == 0:
            survivors.append(name)

    # ---- direct defect measurement for the relocation mutants -------------
    # Measure, in the mutant's own numbering, how much of its *semantic* review
    # body executes before the refusal.  A defect mutant that runs the review
    # body and still passes the shipped suite is an uncaught regression.
    defect_trace: dict[str, object] = {}
    for name in ("M6_relocate_tail_plus_late_refusal",
                 "M7_relocate_above_report_write",
                 "M8_decoy_anchor_above_report_write"):
        mirror = base / name
        work = mirror / "_trace"
        work.mkdir(exist_ok=True)
        existing = work / "existing.json"
        existing.write_text("preserve this historical evidence\n", encoding="utf-8")
        code, seen, out = trace_probe(mirror / PROBE_REL, existing, work)
        mutated_text = (mirror / PROBE_REL).read_text(encoding="utf-8")
        mut_semantic = derive_semantic_body(mutated_text)
        mut_helper = set(derive_r29_contract(mutated_text)["body_lines"])  # type: ignore[arg-type]
        defect_trace[name] = {
            "rc": code,
            "refusal_message": "refusing to overwrite existing evidence" in out,
            "semantic_body_lines_executed_before_refusal": len(seen & mut_semantic),
            "semantic_body_line_total": len(mut_semantic),
            "shipped_helper_body_line_count": len(mut_helper),
            "shipped_helper_body_lines_executed": len(seen & mut_helper),
            "evidence_preserved": existing.read_text(encoding="utf-8")
            == "preserve this historical evidence\n",
        }

    # ---- C4 load-bearing --------------------------------------------------
    c4: dict[str, object] = {}
    variants = (
        ("without_R29_assert", strip_r29),
        ("with_R28_anchor", restore_r28_anchor),
        ("without_R17_test", strip_r17),
    )
    for variant, transform in variants:
        for name in ("M2_late_refusal", "M3_late_refusal_plus_rename",
                     "M6_relocate_tail_plus_late_refusal",
                     "M7_relocate_above_report_write",
                     "M8_decoy_anchor_above_report_write"):
            mirror = base / f"{variant}__{name}"
            build_mirror(mirror)
            mutated = MUTATIONS[name]((mirror / PROBE_REL).read_text(encoding="utf-8"))
            (mirror / PROBE_REL).write_text(mutated, encoding="utf-8")
            (mirror / TEST_REL).write_text(
                transform((mirror / TEST_REL).read_text(encoding="utf-8")),
                encoding="utf-8")
            c4[f"{variant}/{name}"] = run_suite(mirror)

report["C2_C3_mutations"] = results
report["C3_survivors"] = survivors
report["C3_defect_trace"] = defect_trace
report["C4_load_bearing"] = c4
report["fingerprints"] = {
    TEST_REL: sha256(ROOT / TEST_REL),
    PROBE_REL: sha256(ROOT / PROBE_REL),
    "tools/runtime_env.py": sha256(ROOT / "tools/runtime_env.py"),
}

out_path = Path(__file__).with_name("20260912_lap266_r29_review_report.json")
if out_path.exists():
    print(f"refusing to overwrite existing evidence: {out_path}")
    raise SystemExit(2)
out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps({
    "C1_contract": report["C1_contract"],
    "C1_controls": report["C1_controls"],
    "survivors": survivors,
    "defect_trace": defect_trace,
}, indent=2, sort_keys=True))
print(f"report -> {out_path}")
