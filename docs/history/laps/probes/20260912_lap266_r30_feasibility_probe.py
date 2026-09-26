#!/usr/bin/env python3
"""lap266 middle-tier feasibility check for the proposed R30 contract.

R17/R19/R28/R29 all derive the "review body" as a line interval between two
*movable* anchors, so each lap a relocation mutant shrinks or empties the set
(lap262 M6, lap264 M7, lap266 M8).  This probe checks -- in throwaway /tmp
mirrors only -- whether a structural, relocation-proof derivation closes the
whole class at once:

    body = union of line ranges of every module top-level statement that is not
           an import, a def/class, the module docstring, or a ``__name__``
           preflight If.

Nothing in the repository is modified.  The shipped test stays untouched; this
is planning evidence for the work tier, not an implementation.

No game, Wine, Xvfb or PNG.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
PROBE_REL = "docs/history/laps/probes/20260912_lap228_r6b_r3_review_probe.py"
TEST_REL = "tests/test_review_probe_output.py"
PYTHON = str(ROOT / ".venv/bin/python")

PREFLIGHT_START, PREFLIGHT_END = 123, 130
ANCHOR = 'try:\n    with args.output.open("x", encoding="utf-8") as stream:\n'


def _lift_preflight(text: str) -> tuple[str, str]:
    lines = text.splitlines(keepends=True)
    block = lines[PREFLIGHT_START - 1:PREFLIGHT_END]
    assert block[0].startswith('if __name__ == "__main__":'), block[0]
    rest = "".join(lines[:PREFLIGHT_START - 1] + lines[PREFLIGHT_END:])
    return "".join(block), rest


def mut_rename(text: str) -> str:
    return text.replace("drive_wait", "drive_pause")


def mut_late_refusal(text: str) -> str:
    return text.replace("        if path.exists():\n",
                        "        if path.exists() and False:\n", 1)


def mut_relocate_to_tail(text: str) -> str:
    out = text.replace('if __name__ == "__main__":\n',
                       '_IS_MAIN = __name__ == "__main__"\nif _IS_MAIN:\n', 1)
    return out + '\n\nif __name__ == "__main__":\n    pass\n'


def mut_relocate_before_report(text: str) -> str:
    block, rest = _lift_preflight(text)
    return rest.replace(ANCHOR, block + "\n\n" + ANCHOR, 1)


def mut_decoy_anchor(text: str) -> str:
    renamed = text.replace("NEGATIVE_PATTERNS", "NEG_PATTERNS_SRC")
    block, rest = _lift_preflight(renamed)
    return rest.replace(ANCHOR, block + "\nNEGATIVE_PATTERNS = NEG_PATTERNS_SRC\n\n" + ANCHOR, 1)


MUTATIONS = {
    "M0_control": lambda t: t,
    "M1_rename_only": mut_rename,
    "M2_late_refusal": mut_late_refusal,
    "M3_late_refusal_plus_rename": lambda t: mut_rename(mut_late_refusal(t)),
    "M6_relocate_tail_plus_late_refusal": lambda t: mut_relocate_to_tail(mut_late_refusal(t)),
    "M7_relocate_above_report_write": mut_relocate_before_report,
    "M8_decoy_anchor_above_report_write": mut_decoy_anchor,
}

R30_HELPER = '''def _review_body_lines() -> set[int]:
    """Return review statements that must follow output preflight."""

    tree = ast.parse(PROBE.read_text(encoding="utf-8"), filename=str(PROBE))
    body: set[int] = set()
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef,
                             ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            continue
        if (isinstance(node, ast.If) and isinstance(node.test, ast.Compare)
                and isinstance(node.test.left, ast.Name)
                and node.test.left.id == "__name__"):
            continue
        body.update(range(node.lineno, (node.end_lineno or node.lineno) + 1))

    report_write_line = next(
        child.lineno
        for node in tree.body
        for child in ast.walk(node)
        if isinstance(child, ast.Expr)
        and isinstance(child.value, ast.Call)
        and isinstance(child.value.func, ast.Attribute)
        and isinstance(child.value.func.value, ast.Name)
        and child.value.func.value.id == "json"
        and child.value.func.attr == "dump"
    )
    # R30: the body is every module-level review statement, located structurally
    # rather than as an interval between two movable anchors.  Relocating the
    # preflight If or adding a decoy anchor cannot shrink this set.
    assert report_write_line in body, "report write must be inside the review body"
    return body
'''


def swap_helper(test_text: str) -> str:
    start = test_text.index("def _review_body_lines() -> set[int]:")
    end = test_text.index("def _traced_probe(")
    return test_text[:start] + R30_HELPER + "\n\n" + test_text[end:]


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
    )
    passed = int(m.group(1)) if (m := re.search(r"(\d+) passed", res.stdout)) else 0
    failed = int(m.group(1)) if (m := re.search(r"(\d+) failed", res.stdout)) else 0
    errors = int(m.group(1)) if (m := re.search(r"(\d+) error", res.stdout)) else 0
    return {"passed": passed, "failed": failed, "errors": errors,
            "tail": res.stdout.strip().splitlines()[-1] if res.stdout.strip() else ""}


results: dict[str, object] = {}
with tempfile.TemporaryDirectory(prefix="lap266_r30_") as td:
    base = Path(td)
    for name, fn in MUTATIONS.items():
        mirror = base / name
        build_mirror(mirror)
        text = (mirror / PROBE_REL).read_text(encoding="utf-8")
        (mirror / PROBE_REL).write_text(fn(text), encoding="utf-8")
        (mirror / TEST_REL).write_text(
            swap_helper((mirror / TEST_REL).read_text(encoding="utf-8")), encoding="utf-8")
        results[name] = run_suite(mirror)

survivors = [n for n, r in results.items()
             if n != "M0_control" and r["failed"] == 0 and r["errors"] == 0]
payload = {"lap": 266, "item": "R30_feasibility", "role": "middle",
           "results": results, "survivors": survivors}

out_path = HERE.with_name("20260912_lap266_r30_feasibility_report.json")
if out_path.exists():
    print(f"refusing to overwrite existing evidence: {out_path}")
    raise SystemExit(2)
out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(payload, indent=2, sort_keys=True))
print(f"report -> {out_path}")
