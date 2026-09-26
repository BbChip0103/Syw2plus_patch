#!/usr/bin/env python3
"""lap270 middle-tier INDEPENDENT review of the shipped R30 contract.

lap268 (middle) approved the R30-B *scope* by swapping a candidate helper into a
mirrored test file.  lap269 (work) implemented it.  This session reviews what was
actually shipped, so unlike lap268 it never substitutes its own helper text: every
mirror carries ``tests/test_review_probe_output.py`` byte-for-byte from the repo
and only the SUT probe (or, for the attribution axis, one assertion line of the
test) is mutated.

Sections:
  C2  mirror control M0 must equal the real repository result.
  C3  mutation matrix M0..M10, each kill attributed to a named mechanism.
  C4  attribution: delete the R17 coverage assertion and re-run the killed
      mutations; survivors there prove R17 is the load-bearing assertion.
  C5  adversarial extension the approved scope did not cover.  M8 aliased *one*
      review result ahead of a relocated refusal; M11 aliases *all seven* plus
      the report write, which is the closure of that family.

Nothing in the repository is modified; all mutations run in a throwaway /tmp
mirror.  No game, Wine, Xvfb or PNG.  Machine tier 1 evidence only.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve()
ROOT = HERE.parents[4]
PROBE_REL = "docs/history/laps/probes/20260912_lap228_r6b_r3_review_probe.py"
TEST_REL = "tests/test_review_probe_output.py"
PYTHON = str(ROOT / ".venv/bin/python")

PREFLIGHT_START, PREFLIGHT_END = 123, 130
ANCHOR = 'try:\n    with args.output.open("x", encoding="utf-8") as stream:\n'
REVIEW_RESULT_NAMES = ("NEGATIVE_PATTERNS", "both_negative", "synthetic",
                       "grid_total", "surgicality", "waits", "report")


def _lift_preflight(text: str) -> tuple[str, str]:
    lines = text.splitlines(keepends=True)
    block = lines[PREFLIGHT_START - 1:PREFLIGHT_END]
    assert block[0].startswith('if __name__ == "__main__":'), block[0]
    rest = "".join(lines[:PREFLIGHT_START - 1] + lines[PREFLIGHT_END:])
    return "".join(block), rest


def mut_rename(text: str) -> str:
    return text.replace("drive_wait", "drive_pause")


def mut_rename_review_result(text: str) -> str:
    return re.sub(r"\bsynthetic\b", "synthetic_grid", text)


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


def mut_alias_all_results(text: str) -> str:
    """C5: the closure of the M8 family.

    Every review result is computed under a private alias and the canonical name
    is (re)bound only *after* a relocated refusal, together with the report write.
    The review body therefore runs in full before the refusal, yet every line the
    R30 contract collects sits below it.
    """

    renamed = text
    for name in REVIEW_RESULT_NAMES:
        renamed = re.sub(rf"(?<![\w.\"']){name}(?![\w\"'])", f"_SRC_{name}", renamed)
    # keep the report payload key names the tests assert on
    renamed = renamed.replace('_SRC_report["summary"]', '_SRC_report["summary"]')
    block, rest = _lift_preflight(renamed)
    rebind = "".join(f"{n} = _SRC_{n}\n" for n in REVIEW_RESULT_NAMES)
    return rest.replace(ANCHOR, block + "\n" + rebind + "\n" + ANCHOR, 1)


MUTATIONS = {
    "M0_control": lambda t: t,
    "M1_rename_only": mut_rename,
    "M2_late_refusal": mut_late_refusal,
    "M3_late_refusal_plus_rename": lambda t: mut_rename(mut_late_refusal(t)),
    "M6_relocate_tail_plus_late_refusal": lambda t: mut_relocate_to_tail(mut_late_refusal(t)),
    "M7_relocate_above_report_write": mut_relocate_before_report,
    "M8_decoy_anchor_above_report_write": mut_decoy_anchor,
    "M9_rename_review_result": mut_rename_review_result,
    "M10_rename_review_result_plus_late_refusal":
        lambda t: mut_rename_review_result(mut_late_refusal(t)),
    "M11_alias_all_results_above_report_write": mut_alias_all_results,
}

R17_ASSERT = "    assert not (_review_body_lines() & seen)\n"
ATTRIBUTION_SUBSET = ("M0_control", "M2_late_refusal", "M3_late_refusal_plus_rename",
                      "M6_relocate_tail_plus_late_refusal",
                      "M7_relocate_above_report_write",
                      "M8_decoy_anchor_above_report_write")


def build_mirror(dest: Path) -> None:
    (dest / "docs/history/laps/probes").mkdir(parents=True)
    (dest / "tools").mkdir(parents=True)
    (dest / "tests").mkdir(parents=True)
    shutil.copy2(ROOT / PROBE_REL, dest / PROBE_REL)
    shutil.copy2(ROOT / "tools/runtime_env.py", dest / "tools/runtime_env.py")
    shutil.copy2(ROOT / TEST_REL, dest / TEST_REL)
    shutil.copy2(ROOT / "tests/conftest.py", dest / "tests/conftest.py")
    shutil.copy2(ROOT / "pyproject.toml", dest / "pyproject.toml")


def classify(stdout: str) -> str:
    if "missing review results" in stdout:
        return "completeness_assert"
    if "report write not found" in stdout:
        return "report_write_assert"
    if "_review_body_lines() & seen" in stdout:
        return "r17_coverage_assert"
    if "assert" in stdout and "failed" in stdout:
        return "other_assert"
    return "none"


def run_suite(mirror: Path) -> dict[str, object]:
    res = subprocess.run(
        [PYTHON, "-m", "pytest", "-q", "tests/test_review_probe_output.py"],
        capture_output=True, text=True, check=False, cwd=str(mirror),
    )
    passed = int(m.group(1)) if (m := re.search(r"(\d+) passed", res.stdout)) else 0
    failed = int(m.group(1)) if (m := re.search(r"(\d+) failed", res.stdout)) else 0
    errors = int(m.group(1)) if (m := re.search(r"(\d+) error", res.stdout)) else 0
    return {"passed": passed, "failed": failed, "errors": errors,
            "kill_reason": classify(res.stdout),
            "tail": res.stdout.strip().splitlines()[-1] if res.stdout.strip() else ""}


def run_matrix(names, drop_r17: bool) -> dict[str, object]:
    out: dict[str, object] = {}
    with tempfile.TemporaryDirectory(prefix="lap270_r30_") as td:
        base = Path(td)
        for name in names:
            mirror = base / name
            build_mirror(mirror)
            src = (mirror / PROBE_REL).read_text(encoding="utf-8")
            (mirror / PROBE_REL).write_text(MUTATIONS[name](src), encoding="utf-8")
            if drop_r17:
                test_text = (mirror / TEST_REL).read_text(encoding="utf-8")
                assert R17_ASSERT in test_text, "R17 assertion line not found"
                (mirror / TEST_REL).write_text(
                    test_text.replace(R17_ASSERT, ""), encoding="utf-8")
            out[name] = run_suite(mirror)
    return out


real = subprocess.run([PYTHON, "-m", "pytest", "-q", TEST_REL],
                      capture_output=True, text=True, check=False, cwd=str(ROOT))
real_passed = int(m.group(1)) if (m := re.search(r"(\d+) passed", real.stdout)) else 0

matrix = run_matrix(list(MUTATIONS), drop_r17=False)
attribution = run_matrix(ATTRIBUTION_SUBSET, drop_r17=True)

survivors = [n for n, r in matrix.items()
             if n != "M0_control" and r["failed"] == 0 and r["errors"] == 0]
attr_survivors = [n for n, r in attribution.items()
                  if n != "M0_control" and r["failed"] == 0 and r["errors"] == 0]

payload = {
    "lap": 270, "item": "R30_independent_review", "role": "middle",
    "helper_source": "repository (not swapped)",
    "real_repo_passed": real_passed,
    "c2_mirror_control_matches_real": matrix["M0_control"]["passed"] == real_passed,
    "c3_matrix": matrix,
    "c3_survivors": survivors,
    "c4_attribution_without_r17": attribution,
    "c4_survivors_without_r17": attr_survivors,
}

out_path = HERE.with_name("20260912_lap270_r30_review_report.json")
if out_path.exists():
    print(f"refusing to overwrite existing evidence: {out_path}")
    raise SystemExit(2)
out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(payload, indent=2, sort_keys=True))
print(f"report -> {out_path}")
