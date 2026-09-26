#!/usr/bin/env python3
"""lap264 middle-tier independent review of R28.

R28 (lap263 work) added two assertions to ``_review_body_lines()`` in
``tests/test_review_probe_output.py``: the AST-derived review-body line set must
be non-empty, and it must contain the independently located ``json.dump`` report
write.  The claim is that this closes the lap262 M6 survivor (relocating the
first top-level ``__name__`` If below the review body emptied the set and made
``assert not (body & seen)`` vacuously true).

This probe re-derives the contract from the SUT without importing the shipped
test helper, runs a depth-matched mirror control, and re-measures the mutation
matrix -- including a new relocation mutant the R28 anchor does not constrain.

No game, Wine, Xvfb or PNG.  Read-only against the repository; every mutation is
applied to a throwaway /tmp mirror.
"""

from __future__ import annotations

import ast
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

report: dict[str, object] = {"lap": 264, "item": "R28", "role": "middle"}


# ----------------------------------------------------------------- helpers ---
def sha256(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


def derive_contract(src: str) -> dict[str, object]:
    """Independent re-derivation; deliberately does NOT import the test helper."""
    tree = ast.parse(src)
    preflight = [
        n for n in tree.body
        if isinstance(n, ast.If)
        and isinstance(n.test, ast.Compare)
        and isinstance(n.test.left, ast.Name)
        and n.test.left.id == "__name__"
    ]
    if not preflight:
        return {"preflight_count": 0, "preflight_end": None, "body_lines": [],
                "json_dump_line": None}
    end = preflight[0].end_lineno
    body: set[int] = set()
    for n in tree.body:
        if n.lineno > end:
            body.update(range(n.lineno, (n.end_lineno or n.lineno) + 1))
    dumps = [
        c.lineno
        for n in tree.body
        for c in ast.walk(n)
        if isinstance(c, ast.Expr) and isinstance(c.value, ast.Call)
        and isinstance(c.value.func, ast.Attribute)
        and isinstance(c.value.func.value, ast.Name)
        and c.value.func.value.id == "json" and c.value.func.attr == "dump"
    ]
    return {
        "preflight_count": len(preflight),
        "preflight_start": preflight[0].lineno,
        "preflight_end": end,
        "body_lines": sorted(body),
        "json_dump_line": dumps[0] if dumps else None,
        "json_dump_in_body": bool(dumps) and dumps[0] in body,
    }


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
contract = derive_contract(src)
report["C1_contract"] = {
    k: v for k, v in contract.items() if k != "body_lines"
} | {
    "body_line_count": len(contract["body_lines"]),          # type: ignore[arg-type]
    "body_first": contract["body_lines"][0],                 # type: ignore[index]
    "body_last": contract["body_lines"][-1],                 # type: ignore[index]
}

body_set = set(contract["body_lines"])                       # type: ignore[arg-type]
with tempfile.TemporaryDirectory(prefix="lap264_c1_") as td:
    work = Path(td)
    ok_code, ok_seen, _ = trace_probe(ROOT / PROBE_REL, work / "fresh.json", work)
    existing = work / "existing.json"
    existing.write_text("preserve this historical evidence\n", encoding="utf-8")
    ref_code, ref_seen, ref_out = trace_probe(ROOT / PROBE_REL, existing, work)
    report["C1_controls"] = {
        "positive_rc": ok_code,
        "positive_body_lines_executed": len(ok_seen & body_set),
        "refusal_rc": ref_code,
        "refusal_body_lines_executed": len(ref_seen & body_set),
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
    names = sorted(set(re.findall(r"(test_[A-Za-z0-9_]+)", res.stdout)))
    return {"rc": res.returncode, "passed": passed, "failed": failed,
            "errors": errors, "tail": tail, "failing_names": names}


# --------------------------------------------------------------- mutations ---
PREFLIGHT_BLOCK_START = contract["preflight_start"]   # type: ignore[index]
PREFLIGHT_BLOCK_END = contract["preflight_end"]       # type: ignore[index]
ANCHOR = 'try:\n    with args.output.open("x", encoding="utf-8") as stream:\n'


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
    """New mutant: move the whole preflight block down to just above the report write.

    The review body then executes in full before the existing-evidence refusal --
    exactly the defect R17 exists to catch -- but the AST-derived body set stays
    non-empty and still contains the ``json.dump`` anchor R28 pins.
    """
    lines = text.splitlines(keepends=True)
    block = lines[PREFLIGHT_BLOCK_START - 1:PREFLIGHT_BLOCK_END]
    assert block[0].startswith('if __name__ == "__main__":')
    rest = lines[:PREFLIGHT_BLOCK_START - 1] + lines[PREFLIGHT_BLOCK_END:]
    joined = "".join(rest)
    assert ANCHOR in joined
    return joined.replace(ANCHOR, "".join(block) + "\n\n" + ANCHOR, 1)


MUTATIONS = {
    "M0_control": lambda t: t,
    "M1_rename_only": mut_rename,
    "M2_late_refusal": mut_late_refusal,
    "M3_late_refusal_plus_rename": lambda t: mut_rename(mut_late_refusal(t)),
    "M6_relocate_tail_plus_late_refusal": lambda t: mut_relocate_to_tail(mut_late_refusal(t)),
    "M7_relocate_above_report_write": mut_relocate_before_report,
}

# Test-side variants for the load-bearing (C4) checks.
R28_GUARD = re.compile(
    r"\n    # R19 anchors.*?return body_lines\n", re.S)


def strip_r28(test_text: str) -> str:
    replacement = "\n    return body_lines\n"
    out, n = R28_GUARD.subn(replacement, test_text)
    assert n == 1, "R28 guard block not located"
    return out


def strip_r17(test_text: str) -> str:
    marker = "def test_r6b_r17_existing_evidence_refusal_precedes_review_body"
    idx = test_text.index(marker)
    return test_text[:idx].rstrip("\n") + "\n"


results: dict[str, object] = {}
survivors: list[str] = []

with tempfile.TemporaryDirectory(prefix="lap264_mut_") as td:
    base = Path(td)
    for name, fn in MUTATIONS.items():
        mirror = base / name
        build_mirror(mirror)
        mutated = fn((mirror / PROBE_REL).read_text(encoding="utf-8"))
        (mirror / PROBE_REL).write_text(mutated, encoding="utf-8")
        outcome = run_suite(mirror)
        outcome["mutant_contract"] = {
            k: (len(v) if k == "body_lines" else v)            # type: ignore[arg-type]
            for k, v in derive_contract(mutated).items()
        }
        results[name] = outcome
        if name != "M0_control" and outcome["failed"] == 0 and outcome["errors"] == 0:
            survivors.append(name)

    # ---- direct defect measurement for the relocation mutants -------------
    # Map executed mutant lines back to baseline line numbers so "how much of the
    # review body ran before the refusal" is measured against the same contract.
    anchor_baseline = src[:src.index(ANCHOR)].count("\n") + 1
    shift = PREFLIGHT_BLOCK_END - PREFLIGHT_BLOCK_START + 1
    insert_len = shift + 2
    anchor_mut = anchor_baseline - shift

    def m7_to_baseline(m: int) -> int | None:
        if m < PREFLIGHT_BLOCK_START:
            return m
        if m < anchor_mut:
            return m + shift
        if m < anchor_mut + insert_len:
            return None
        return m - insert_len + shift

    defect_trace: dict[str, object] = {"_map": {
        "anchor_baseline_line": anchor_baseline, "shift": shift,
        "insert_len": insert_len, "anchor_mutant_line": anchor_mut}}
    for name in ("M6_relocate_tail_plus_late_refusal", "M7_relocate_above_report_write"):
        mirror = base / name
        work = mirror / "_trace"
        work.mkdir(exist_ok=True)
        existing = work / "existing.json"
        existing.write_text("preserve this historical evidence\n", encoding="utf-8")
        code, seen, out = trace_probe(mirror / PROBE_REL, existing, work)
        mutated_text = (mirror / PROBE_REL).read_text(encoding="utf-8")
        if name.startswith("M7"):
            executed = {b for m in seen if (b := m7_to_baseline(m)) is not None
                        and b in body_set}
        else:
            executed = seen & body_set
        defect_trace[name] = {
            "rc": code,
            "refusal_message": "refusing to overwrite existing evidence" in out,
            "baseline_body_lines_executed_before_refusal": len(executed),
            "baseline_body_line_total": len(body_set),
            "shipped_helper_body_line_count": len(
                derive_contract(mutated_text)["body_lines"]),  # type: ignore[arg-type]
            "evidence_preserved": existing.read_text(encoding="utf-8")
            == "preserve this historical evidence\n",
        }

    # ---- C4 load-bearing --------------------------------------------------
    c4: dict[str, object] = {}
    for variant, strip in (("without_R28_guard", strip_r28), ("without_R17_test", strip_r17)):
        for name in ("M2_late_refusal", "M3_late_refusal_plus_rename",
                     "M6_relocate_tail_plus_late_refusal", "M7_relocate_above_report_write"):
            mirror = base / f"{variant}__{name}"
            build_mirror(mirror)
            mutated = MUTATIONS[name]((mirror / PROBE_REL).read_text(encoding="utf-8"))
            (mirror / PROBE_REL).write_text(mutated, encoding="utf-8")
            (mirror / TEST_REL).write_text(
                strip((mirror / TEST_REL).read_text(encoding="utf-8")), encoding="utf-8")
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

out_path = Path(__file__).with_name("20260912_lap264_r28_review_report.json")
if out_path.exists():
    print(f"refusing to overwrite existing evidence: {out_path}")
    raise SystemExit(2)
out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps({
    "C1_controls": report["C1_controls"],
    "survivors": survivors,
    "defect_trace": defect_trace,
}, indent=2, sort_keys=True))
print(f"report -> {out_path}")
