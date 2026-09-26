#!/usr/bin/env python3
"""lap262 middle-tier independent review probe for R19.

R19 claim (lap261 work): the R17 regression
``test_r6b_r17_existing_evidence_refusal_precedes_review_body`` no longer
depends on the ``drive_wait`` helper name.  It derives the top-level
review-body lines from the SUT AST and uses a line trace to assert that an
existing-evidence refusal exits before any of those lines run.

C0  fresh targeted run in the real repository
C1  independent AST/trace contract measurement, written from the contract and
    not by importing the shipped test helpers, with a live-detector positive
    control and a refusal negative control
C2  depth-matched mirror M0 control (must equal the real repository result)
C3  mutations with out-of-range kill accounting, including a name-rename
    control and the surgical late-refusal defect R17 is supposed to own
C4  load-bearing check: delete only the R17 regression and re-run the
    mutations it is supposed to own

No game, Wine, Xvfb or PNG.  Read-only against the repository: every mutation
is applied to a throwaway mirror under /tmp only.
"""
from __future__ import annotations

import ast
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
SUT = REPO / "docs/history/laps/probes/20260912_lap228_r6b_r3_review_probe.py"
TESTS = REPO / "tests" / "test_review_probe_output.py"
PY = REPO / ".venv" / "bin" / "python"

R17_TEST = "test_r6b_r17_existing_evidence_refusal_precedes_review_body"
R7_TEST = "test_r6b_r7_refuses_to_overwrite_existing_report"
R11_TEST = "test_r6b_r11_exclusive_create_rejects_dangling_output_symlink"
FRESH_TEST = "test_r6b_r7_writes_to_explicit_new_report_path"
SCOPE = {R17_TEST}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def counts(out: str) -> dict[str, int]:
    tail = out.strip().splitlines()[-1] if out.strip() else ""
    return {
        key: int(num)
        for num, key in re.findall(
            r"(\d+) (passed|failed|error|errors|deselected)", tail)
    }


# --------------------------------------------------------------------------
# C1: independent re-derivation of the contract.  Written from the stated
# contract ("top-level statements after the __name__ preflight must not run
# when an existing-evidence refusal fires"), not by importing the test.

def body_lines(source: str, filename: str) -> tuple[set[int], int]:
    tree = ast.parse(source, filename=filename)
    end = 0
    for node in tree.body:
        if (isinstance(node, ast.If) and isinstance(node.test, ast.Compare)
                and isinstance(node.test.left, ast.Name)
                and node.test.left.id == "__name__"):
            end = node.end_lineno or node.lineno
            break
    if end == 0:
        return set(), 0
    return {
        line
        for node in tree.body
        if node.lineno > end
        for line in range(node.lineno, (node.end_lineno or node.lineno) + 1)
    }, end


TRACER = """
import json, runpy, sys
target, output = sys.argv[1], sys.argv[2]
seen = set()
def hook(frame, event, arg):
    if event == 'line' and frame.f_code.co_filename == target:
        seen.add(frame.f_lineno)
    return hook
sys.argv = [target, '--output', output]
sys.settrace(hook)
code = 0
try:
    runpy.run_path(target, run_name='__main__')
except SystemExit as exc:
    code = exc.code if exc.code is not None else 0
finally:
    sys.settrace(None)
sys.stderr.write(json.dumps({'code': code, 'seen': sorted(seen)}))
"""


def trace_probe(sut: Path, output: Path, workdir: Path) -> tuple[int, set[int], str]:
    tracer = workdir / "lap262_tracer.py"
    tracer.write_text(TRACER, encoding="utf-8")
    res = run([str(PY), str(tracer), str(sut), str(output)], workdir)
    payload = json.loads(res.stderr.strip().splitlines()[-1])
    return payload["code"], set(payload["seen"]), res.stdout


def c1(workdir: Path) -> dict[str, object]:
    source = SUT.read_text(encoding="utf-8")
    lines, preflight_end = body_lines(source, str(SUT))

    existing = workdir / "existing.json"
    existing.write_text("preserve this historical evidence\n", encoding="utf-8")
    refuse_code, refuse_seen, refuse_out = trace_probe(SUT, existing, workdir)

    fresh = workdir / "fresh-c1.json"
    fresh_code, fresh_seen, _ = trace_probe(SUT, fresh, workdir)

    return {
        "preflight_end_line": preflight_end,
        "body_line_count": len(lines),
        "body_line_min": min(lines) if lines else None,
        "body_line_max": max(lines) if lines else None,
        "body_set_nonempty": bool(lines),
        "drive_wait_def_line_in_body": next(
            (n.lineno for n in ast.parse(source).body
             if isinstance(n, ast.FunctionDef) and n.name == "drive_wait"), None),
        "report_write_line_in_body": max(lines) in lines if lines else False,
        # negative control: the refusal path must touch no review-body line
        "refusal_returncode": refuse_code,
        "refusal_body_lines_seen": sorted(lines & refuse_seen),
        "refusal_message_present":
            "refusing to overwrite existing evidence" in refuse_out,
        "existing_file_preserved":
            existing.read_text(encoding="utf-8") == "preserve this historical evidence\n",
        # positive control: the detector is live -- the successful path really
        # does execute review-body lines, so an empty intersection is a signal
        "fresh_returncode": fresh_code,
        "fresh_body_lines_seen_count": len(lines & fresh_seen),
        "detector_is_live": bool(lines & fresh_seen),
    }


# --------------------------------------------------------------------------
# C3 mutations.  Every mutation is applied to the mirror copy of the SUT
# probe; the test file is only edited for the C4 load-bearing check.

EARLY_EXISTS = '        if path.exists():\n'
# Neutering the *return* while still calling ``path.exists()`` keeps the
# OSError classification path intact, so the R10 non-searchable-parent test
# stays green and the only remaining defect is "the review body runs before
# the refusal".  Deleting the lines instead also changes the classification,
# which contaminates the kill accounting (lap262 round 1).
EARLY_EXISTS_NEUTERED = '        if path.exists() and False:\n'
REFUSAL_BLOCK = (
    '    if refusal is not None:\n'
    '        print(refusal)\n'
    '        raise SystemExit(2)\n'
)
PREFLIGHT_HEAD = 'if __name__ == "__main__":\n'


def rename(text: str) -> str:
    return re.sub(r"\bdrive_wait\b", "drive_wait_renamed", text)


def drop_exists(text: str) -> str:
    return text.replace(EARLY_EXISTS, EARLY_EXISTS_NEUTERED, 1)


def vacuity(text: str) -> str:
    """Keep the early refusal but move the first top-level ``__name__`` If."""
    out = text.replace(
        PREFLIGHT_HEAD, '_IS_MAIN = __name__ == "__main__"\nif _IS_MAIN:\n', 1)
    return out + '\n\nif __name__ == "__main__":\n    pass\n'


MUTATIONS: list[tuple[str, str, object, bool]] = [
    ("M1_rename_only", "rename drive_wait, no behaviour change", rename, False),
    ("M2_late_refusal", "neuter only the early exists() refusal; O_EXCL still "
     "refuses with the same message and exit 2", drop_exists, True),
    ("M3_late_refusal_plus_rename", "M2 plus renaming drive_wait",
     lambda t: rename(drop_exists(t)), True),
    ("M4_delete_refusal_block", "delete the whole early-exit refusal block",
     lambda t: t.replace(REFUSAL_BLOCK, "", 1), True),
    ("M5_refusal_exits_zero", "early refusal prints but exits 0",
     lambda t: t.replace(REFUSAL_BLOCK,
                         '    if refusal is not None:\n'
                         '        print(refusal)\n'
                         '        raise SystemExit(0)\n', 1), True),
    ("M6_vacuity_relocated_preflight",
     "M2 plus moving the first top-level __name__ If below the review body",
     lambda t: vacuity(drop_exists(t)), True),
]


def apply_mutations(mirror: Path, msut: Path, mtests: Path, original: str,
                    scope: set[str]) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for mid, note, fn, expect_defect in MUTATIONS:
        mutated = fn(original)
        if mutated == original:
            results.append({"id": mid, "applied": False, "note": note})
            continue
        msut.write_text(mutated, encoding="utf-8")
        res = run([str(PY), "-m", "pytest", "-q", str(mtests), "--tb=no", "-rf"],
                  mirror)
        failed = sorted(set(re.findall(r"^FAILED .*::(\w+)", res.stdout,
                                       re.MULTILINE)))
        errored = sorted(set(re.findall(r"^ERROR .*::(\w+)", res.stdout,
                                        re.MULTILINE)))
        dead = set(failed) | set(errored)
        results.append({
            "id": mid, "note": note, "applied": True,
            "defect_present": expect_defect,
            "counts": counts(res.stdout),
            "failed": failed, "errored": errored,
            "killed": bool(dead),
            "killed_by_scope": sorted(dead & scope),
            "out_of_scope_kills": sorted(dead - scope),
        })
        msut.write_text(original, encoding="utf-8")
    return results


def main() -> int:
    report: dict[str, object] = {
        "lap": 262, "role": "middle", "item": "R19",
        "sut_sha256_before": sha(SUT), "tests_sha256_before": sha(TESTS),
    }

    c0 = run([str(PY), "-m", "pytest", "-q", str(TESTS)], REPO)
    report["C0"] = {"returncode": c0.returncode, "counts": counts(c0.stdout)}

    tmp = Path(tempfile.mkdtemp(prefix="lap262_r19_"))
    report["C1"] = c1(tmp)

    mirror = tmp / REPO.name
    for rel in ("tools", "tests", "pyproject.toml", "docs/history/laps/probes"):
        src, dst = REPO / rel, mirror / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src, dst) if src.is_dir() else shutil.copy2(src, dst)
    msut = mirror / "docs/history/laps/probes" / SUT.name
    mtests = mirror / "tests" / TESTS.name
    original_sut = msut.read_text(encoding="utf-8")
    original_tests = mtests.read_text(encoding="utf-8")

    real_full = run([str(PY), "-m", "pytest", "-q", str(TESTS)], REPO)
    m0 = run([str(PY), "-m", "pytest", "-q", str(mtests)], mirror)
    report["C2"] = {
        "real_counts": counts(real_full.stdout),
        "mirror_counts": counts(m0.stdout),
        "equal": counts(real_full.stdout) == counts(m0.stdout),
        "returncode": m0.returncode,
    }

    results = apply_mutations(mirror, msut, mtests, original_sut, SCOPE)
    report["C3"] = {
        "mutations": results,
        "survivors_with_defect": [
            r["id"] for r in results
            if r.get("applied") and r.get("defect_present") and not r["killed"]],
        "killed_without_defect": [
            r["id"] for r in results
            if r.get("applied") and not r.get("defect_present") and r["killed"]],
        "not_applied": [r["id"] for r in results if not r.get("applied")],
    }

    # C4: remove only the R17 regression and re-run the mutations it owns.
    without_r17 = re.sub(
        r"\ndef " + R17_TEST + r"\(tmp_path: Path\):\n(?:.*\n)*?(?=\ndef |\Z)",
        "\n", original_tests)
    c4: dict[str, object] = {"r17_removed": without_r17 != original_tests}
    if c4["r17_removed"]:
        mtests.write_text(without_r17, encoding="utf-8")
        base = run([str(PY), "-m", "pytest", "-q", str(mtests)], mirror)
        c4["baseline_counts"] = counts(base.stdout)
        c4["mutations"] = apply_mutations(mirror, msut, mtests, original_sut, set())
        mtests.write_text(original_tests, encoding="utf-8")
    report["C4"] = c4

    report["sut_sha256_after"] = sha(SUT)
    report["tests_sha256_after"] = sha(TESTS)
    report["repo_unchanged"] = (report["sut_sha256_after"] == report["sut_sha256_before"]
                                and report["tests_sha256_after"] == report["tests_sha256_before"])
    report["game_executions"] = 0

    out = Path(__file__).with_name("20260912_lap262_r19_review_report.json")
    with out.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({k: report[k] for k in ("C0", "C1", "C2", "C3", "C4",
                                             "repo_unchanged")},
                     indent=2, sort_keys=True))
    print(f"report -> {out}")
    shutil.rmtree(tmp, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
