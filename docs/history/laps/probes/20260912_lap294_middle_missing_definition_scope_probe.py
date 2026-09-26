"""lap294 middle probe — how far does the §4.5.3 missing-definition repair have to reach?

lap293 stopped because the repaired lap280 probe still dies with `KeyError` when a
constant definition disappears, and the re-indexing site is outside the scope
§4.5.3 wrote down.  This probe answers the scope question with measurements
instead of reading:

  (A) With the probe exactly as lap293 left it, remove each of the three unit
      offset definitions in turn.  Where does it die?
  (B) Apply, in a throwaway sandbox only, the narrowest fix §4.5.3 literally
      allows (guard the `refs` loop).  Does that make every mutant report a
      named failure, or does some constant still crash somewhere else?

Read-only with respect to the repository: mutants live in temporary directories,
the original EXE is symlinked, and nothing under the repo is written.

No game, no Wine, no Xvfb, no Stage B.

Usage: .venv/bin/python docs/history/laps/probes/20260912_lap294_middle_missing_definition_scope_probe.py
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
PROBES = REPO / "docs" / "history" / "laps" / "probes"
TARGET = PROBES / "20260912_lap280_middle_s1_crossverify_probe.py"
ENV_MOD = REPO / "tools" / "runtime_env.py"
DRIVER = REPO / "patches" / "population" / "runtime_driver.py"
EXE = REPO / "Syw2plus" / "syw2plus_original.exe"
LAP280_REPORT = REPO / "logs" / "lap280" / "s1_crossverify_probe.json"

# Provenance the escalation recorded.  A mismatch is a fact to report, not a
# reason to rewrite anything.
EXPECTED_SHA = {
    "target_probe": "edefa0e4b82d39034ddd14055e09a651998d2a8c93e5d27ab0f168bc7b47f61d",
    "runtime_env": "dd2ad0439111d6b1e098d0ea771db172847dfa42f04ed085c4567f2ac8500190",
    "runtime_driver": "ae4ff9393247ce31eab7c953b040f7d3c5aa8b0386af025046382c7d4e4291b5",
    "original_exe": "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac",
    "lap280_report": "3d4fe30703a4d3797bd233cb0d8b34026258356807173ec35240e6a86d6a9126",
}

OFFSET_DEFS = {
    "x": "G1_UNIT_X_OFFSET = 0x2A2\n",
    "y": "G1_UNIT_Y_OFFSET = 0x2A4\n",
    "internal_id": "G1_UNIT_INTERNAL_ID_OFFSET = 0x29C\n",
}

# The narrowest edit §4.5.3's wording allows beyond the tuple guard: skip the
# `refs` loop for a field whose definition never made it into `pinned`.
REFS_LOOP_BEFORE = (
    '    for name in ("x", "y", "internal_id"):\n'
    "        abs_addr = UNIT_BASE + pinned[name]\n"
)
REFS_LOOP_AFTER = (
    '    for name in ("x", "y", "internal_id"):\n'
    "        if name not in pinned:\n"
    "            continue\n"
    "        abs_addr = UNIT_BASE + pinned[name]\n"
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def run(script: Path) -> tuple[int, bytes, str]:
    proc = subprocess.run([sys.executable, str(script)], capture_output=True)
    return proc.returncode, proc.stdout, proc.stderr.decode("utf-8", "replace")


def crash_site(stderr: str) -> str | None:
    """Last `probe.py:LINE` frame plus the exception line, or None if clean."""
    if "Traceback" not in stderr:
        return None
    lines = stderr.strip().splitlines()
    frame = ""
    for line in lines:
        m = re.search(r'File "[^"]*", line (\d+), in ', line)
        if m:
            frame = f"line {m.group(1)}"
    return f"{frame}: {lines[-1].strip()}" if frame else lines[-1].strip()


def build_sandbox(root: Path, env_text: str, probe_text: str) -> Path:
    (root / "Syw2plus").mkdir(parents=True)
    (root / "tools").mkdir(parents=True)
    (root / "patches" / "population").mkdir(parents=True)
    (root / "docs" / "history" / "laps" / "probes").mkdir(parents=True)
    (root / "Syw2plus" / EXE.name).symlink_to(EXE)
    (root / "tools" / "runtime_env.py").write_text(env_text, encoding="utf-8")
    (root / "patches" / "population" / "runtime_driver.py").write_text(
        DRIVER.read_text(encoding="utf-8"), encoding="utf-8"
    )
    script = root / "docs" / "history" / "laps" / "probes" / TARGET.name
    script.write_text(probe_text, encoding="utf-8")
    return script


def sweep(probe_text: str, env_text: str) -> dict[str, object]:
    """Run the control plus one definition-removal mutant per constant."""
    out: dict[str, object] = {}
    cases = [("control_unmutated", None)] + [(f"removed_{f}", f) for f in OFFSET_DEFS]
    for tag, field in cases:
        variant = env_text if field is None else env_text.replace(OFFSET_DEFS[field], "")
        if field is not None and variant == env_text:
            out[tag] = {"error": f"anchor absent: {OFFSET_DEFS[field]!r}"}
            continue
        with tempfile.TemporaryDirectory(prefix=f"lap294_{tag}_") as tmp:
            script = build_sandbox(Path(tmp), variant, probe_text)
            code, stdout, stderr = run(script)
        parsed = json.loads(stdout) if stdout else {}
        out[tag] = {
            "exit": code,
            "stdout_bytes": len(stdout),
            "stdout_sha256": sha256_bytes(stdout),
            "failures": parsed.get("failures"),
            "crash": crash_site(stderr),
        }
    return out


def main() -> int:
    failures: list[str] = []
    report: dict[str, object] = {}

    actual = {
        "target_probe": sha256(TARGET),
        "runtime_env": sha256(ENV_MOD),
        "runtime_driver": sha256(DRIVER),
        "original_exe": sha256(EXE),
        "lap280_report": sha256(LAP280_REPORT),
    }
    report["provenance"] = actual
    for key, expected in EXPECTED_SHA.items():
        if actual[key] != expected:
            failures.append(f"{key} sha mismatch: {actual[key]} != {expected}")

    env_text = ENV_MOD.read_text(encoding="utf-8")
    as_is = TARGET.read_text(encoding="utf-8")
    if as_is.count(REFS_LOOP_BEFORE) != 1:
        failures.append("refs loop anchor not found exactly once; the sweep below is not meaningful")
        patched = as_is
    else:
        patched = as_is.replace(REFS_LOOP_BEFORE, REFS_LOOP_AFTER)

    report["as_is"] = sweep(as_is, env_text)
    report["refs_guard_only"] = sweep(patched, env_text)

    # (A) Every constant must crash the same way today — the defect is not
    #     specific to the one constant lap292's review probe happened to mutate.
    for field in OFFSET_DEFS:
        case = report["as_is"][f"removed_{field}"]
        if not case.get("crash") or case.get("stdout_bytes") != 0:
            failures.append(f"as_is/{field}: expected a 0-byte crash, got {case}")

    # (B) The narrowest allowed fix must either cure all three or the scope in
    #     §4.5.3 is provably too small.  Record which.
    still_crashing = [
        field for field in OFFSET_DEFS
        if report["refs_guard_only"][f"removed_{field}"].get("crash")
    ]
    report["refs_guard_only_still_crashing"] = still_crashing
    report["scope_verdict"] = (
        "refs guard alone is sufficient" if not still_crashing
        else "refs guard alone is INSUFFICIENT; unguarded consumers remain"
    )

    control = report["refs_guard_only"]["control_unmutated"]
    if control.get("stdout_sha256") != EXPECTED_SHA["lap280_report"]:
        failures.append(
            "refs guard changes the normal report; it is not a behaviour-preserving fix"
        )

    report["failures"] = failures
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
