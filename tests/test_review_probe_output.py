"""Regression coverage for review-probe evidence output boundaries."""

import ast
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
PROBE = ROOT / "docs/history/laps/probes/20260912_lap228_r6b_r3_review_probe.py"


REVIEW_RESULT_NAMES = (
    "NEGATIVE_PATTERNS", "both_negative", "synthetic", "grid_total",
    "surgicality", "waits", "report",
)


def _review_body_lines() -> set[int]:
    """Return review statements that must follow output preflight."""

    tree = ast.parse(PROBE.read_text(encoding="utf-8"), filename=str(PROBE))
    body: set[int] = set()
    found: set[str] = set()
    for node in tree.body:
        targets = [
            target.id
            for target in getattr(node, "targets", [])
            if isinstance(target, ast.Name)
        ]
        hit = set(targets) & set(REVIEW_RESULT_NAMES)
        if not hit:
            continue
        found |= hit
        body.update(range(node.lineno, (node.end_lineno or node.lineno) + 1))

    report_write_lines = {
        child.lineno
        for node in tree.body
        for child in ast.walk(node)
        if isinstance(child, ast.Expr)
        and isinstance(child.value, ast.Call)
        and isinstance(child.value.func, ast.Attribute)
        and isinstance(child.value.func.value, ast.Name)
        and child.value.func.value.id == "json"
        and child.value.func.attr == "dump"
    }
    body |= report_write_lines

    # R30-B anchors on named review results and takes the union of every match.
    # A union is monotone, so moving output preflight below the review body
    # cannot shrink it and a decoy reassignment can only add lines.  M9/M10
    # deliberately fail closed if a review result is renamed: that is a
    # completeness-contract failure, not a coverage kill.
    assert found == set(REVIEW_RESULT_NAMES), (
        f"missing review results: {sorted(set(REVIEW_RESULT_NAMES) - found)}"
    )
    assert report_write_lines, "report write not found"
    return body


def _traced_probe(output: Path) -> tuple[subprocess.CompletedProcess[str], set[int]]:
    """Trace module lines so early refusals cannot hide review-body execution."""

    tracer = output.parent / "profile_probe.py"
    tracer.write_text(
        "import json, runpy, sys\n"
        "target = sys.argv[1]\n"
        "output = sys.argv[3]\n"
        "seen = set()\n"
        "def hook(frame, event, arg):\n"
        "    if event == 'line' and frame.f_code.co_filename == target:\n"
        "        seen.add(frame.f_lineno)\n"
        "    return hook\n"
        "sys.argv = [target, '--output', output]\n"
        "sys.settrace(hook)\n"
        "code = 0\n"
        "try:\n"
        "    runpy.run_path(target, run_name='__main__')\n"
        "except SystemExit as exc:\n"
        "    code = exc.code\n"
        "finally:\n"
        "    sys.settrace(None)\n"
        "print(json.dumps({'code': code, 'seen': sorted(seen)}))\n"
        "sys.exit(code)\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, str(tracer), str(PROBE), "--output", str(output)],
        capture_output=True,
        text=True,
        check=False,
    )
    trace = json.loads(result.stdout.strip().splitlines()[-1])
    return result, set(trace["seen"])


def test_r6b_r7_refuses_to_overwrite_existing_report(tmp_path: Path):
    output = tmp_path / "existing-report.json"
    original = b"preserve this historical evidence\n"
    output.write_bytes(original)

    result = subprocess.run(
        [sys.executable, str(PROBE), "--output", str(output)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 2
    assert "refusing to overwrite existing evidence" in result.stdout
    assert output.read_bytes() == original


def test_r6b_r11_exclusive_create_rejects_dangling_output_symlink(tmp_path: Path):
    """The O_EXCL-style writer must protect paths ``exists()`` cannot see."""

    target = tmp_path / "future-report.json"
    output = tmp_path / "report.json"
    output.symlink_to(target)
    assert not output.exists()

    result = subprocess.run(
        [sys.executable, str(PROBE), "--output", str(output)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 2
    assert "refusing to overwrite existing evidence" in result.stdout
    assert output.is_symlink()
    assert not target.exists()


def test_r6b_r7_writes_to_explicit_new_report_path(tmp_path: Path):
    output = tmp_path / "fresh-report.json"

    result = subprocess.run(
        [sys.executable, str(PROBE), "--output", str(output)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["lap"] == 228
    assert report["summary"]["surgicality_verdict"] == "AGREES"
    assert "report -> " + str(output) in result.stdout


def test_r6b_r10_rejects_missing_parent_before_running_probe(tmp_path: Path):
    output = tmp_path / "missing-parent" / "report.json"

    result = subprocess.run(
        [sys.executable, str(PROBE), "--output", str(output)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 2
    assert "output parent is not a directory" in result.stdout
    assert "Traceback" not in result.stderr
    assert not output.exists()


def test_r6b_r10_rejects_non_directory_parent(tmp_path: Path):
    parent = tmp_path / "parent-file"
    parent.write_text("not a directory\n", encoding="utf-8")
    output = parent / "report.json"

    result = subprocess.run(
        [sys.executable, str(PROBE), "--output", str(output)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 2
    assert "output parent is not a directory" in result.stdout
    assert "Traceback" not in result.stderr
    assert parent.read_text(encoding="utf-8") == "not a directory\n"


def test_r6b_r10_rejects_read_only_parent(tmp_path: Path):
    parent = tmp_path / "read-only"
    parent.mkdir()
    output = parent / "report.json"
    original_mode = parent.stat().st_mode & 0o777
    parent.chmod(0o500)
    try:
        result = subprocess.run(
            [sys.executable, str(PROBE), "--output", str(output)],
            capture_output=True,
            text=True,
            check=False,
        )
    finally:
        parent.chmod(original_mode)

    assert result.returncode == 2
    assert "output parent is not writable" in result.stdout
    assert "Traceback" not in result.stderr
    assert not output.exists()


def test_r6b_r10_classifies_non_searchable_parent_without_traceback(tmp_path: Path):
    parent = tmp_path / "no-search"
    parent.mkdir()
    output = parent / "report.json"
    original_mode = parent.stat().st_mode & 0o777
    parent.chmod(0o600)
    try:
        result = subprocess.run(
            [sys.executable, str(PROBE), "--output", str(output)],
            capture_output=True,
            text=True,
            check=False,
        )
    finally:
        parent.chmod(original_mode)

    assert result.returncode == 2
    assert "output path unavailable" in result.stdout
    assert "Traceback" not in result.stderr
    assert not output.exists()


def test_r6b_r17_existing_evidence_refusal_precedes_review_body(tmp_path: Path):
    output = tmp_path / "existing-report.json"
    output.write_text("preserve this historical evidence\n", encoding="utf-8")

    result, seen = _traced_probe(output)

    assert result.returncode == 2
    assert "refusing to overwrite existing evidence" in result.stdout
    assert not (_review_body_lines() & seen)
    assert output.read_text(encoding="utf-8") == "preserve this historical evidence\n"
