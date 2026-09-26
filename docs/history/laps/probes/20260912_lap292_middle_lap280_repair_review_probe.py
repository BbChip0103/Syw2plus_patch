"""Independent middle review of the lap291 repair of the lap280 cross-verify probe.

Four questions, none of them answered by trusting the lap291 record:

  1. Provenance — do the repaired probe, the two implementation modules it now
     reads, the original executable and the authoritative lap280 report still
     carry the SHAs the history files recorded?
  2. Reproduction — does a fresh run of the repaired probe exit 0 with an empty
     ``failures`` list and emit a report that is **byte-identical** to the
     preserved ``logs/lap280/s1_crossverify_probe.json``?
  3. Companion invariance — do the four probes that were re-run alongside it
     still reproduce their recorded report SHAs byte for byte?
  4. Falsifying power — this review builds its OWN mutants, not the two the
     lap291 record cites.  Five of them, each in a private sandbox, covering
     the value drift, the *missing definition* case that produced the original
     ``NoneType`` crash, a literal-for-constant regression, a wrong-constant
     regression, and an unmutated control.

Read-only with respect to the repository: the original executable, the
implementation modules and every repository probe are only ever read.  Mutants
live under a private temporary directory and reach the executable by symlink.
No game, Wine, Xvfb, Stage B, harness run or PNG.

Usage: .venv/bin/python docs/history/laps/probes/20260912_lap292_middle_lap280_repair_review_probe.py
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
PROBES = REPO / "docs" / "history" / "laps" / "probes"
PYTHON = REPO / ".venv" / "bin" / "python"

TARGET = PROBES / "20260912_lap280_middle_s1_crossverify_probe.py"
ENV_MOD = REPO / "tools" / "runtime_env.py"
DRIVER = REPO / "patches" / "population" / "runtime_driver.py"
EXE = REPO / "Syw2plus" / "syw2plus_original.exe"
LAP280_REPORT = REPO / "logs" / "lap280" / "s1_crossverify_probe.json"

# Recorded by lap280/lap282/lap289/lap290/lap291 — see docs/history/laps/.
EXPECTED_SHA = {
    "target_probe": "100f991b3abfa6d075a35facf9a9e479c1d2092ebb4d6245688cfe73cb999f84",
    "runtime_env": "dd2ad0439111d6b1e098d0ea771db172847dfa42f04ed085c4567f2ac8500190",
    "runtime_driver": "ae4ff9393247ce31eab7c953b040f7d3c5aa8b0386af025046382c7d4e4291b5",
    "original_exe": "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac",
    "lap280_report": "3d4fe30703a4d3797bd233cb0d8b34026258356807173ec35240e6a86d6a9126",
}

COMPANIONS = {
    "lap279": ("20260912_lap279_middle_s1_serializer_probe.py",
               "e848c940ee6d4c437b3b4d0223dfc606bb46fff08698241ee7a55913c9db2ddd"),
    "lap282": ("20260912_lap282_middle_unit_offset_review_probe.py",
               "e0f07f3a4352c51959919fc0b5eb6bc1f907a09596ae3e5d5d8d8c5e46f4be08"),
    "lap284_middle": ("20260912_lap284_middle_runtime_contract_probe.py",
                      "2870383083dea5f1914a732d9d6ec468352a4f11f6854a46fd105e7673d52d60"),
    "lap284_work": ("20260912_lap284_work_save_layout_probe.py",
                    "7381b5f7ebbc99a6a6d9e9cdc0ce95b3bcbaf6237645d521b83c59eba5cbfb81"),
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def run(script: Path) -> tuple[int, bytes, str]:
    proc = subprocess.run([str(PYTHON), str(script)], capture_output=True)
    return proc.returncode, proc.stdout, proc.stderr.decode("utf-8", "replace")


def build_sandbox(root: Path, env_text: str, driver_text: str) -> Path:
    """Lay out a private tree whose parents[4] is ``root`` and patch two files."""
    probe_dir = root / "docs" / "history" / "laps" / "probes"
    probe_dir.mkdir(parents=True)
    (root / "tools").mkdir()
    (root / "patches" / "population").mkdir(parents=True)
    (root / "Syw2plus").mkdir()
    (root / "Syw2plus" / EXE.name).symlink_to(EXE)
    (root / "tools" / ENV_MOD.name).write_text(env_text, encoding="utf-8")
    (root / "patches" / "population" / DRIVER.name).write_text(driver_text, encoding="utf-8")
    shutil.copy2(TARGET, probe_dir / TARGET.name)
    return probe_dir / TARGET.name


def main() -> int:
    failures: list[str] = []
    report: dict[str, object] = {}

    # (1) Provenance.
    actual_sha = {
        "target_probe": sha256(TARGET),
        "runtime_env": sha256(ENV_MOD),
        "runtime_driver": sha256(DRIVER),
        "original_exe": sha256(EXE),
        "lap280_report": sha256(LAP280_REPORT),
    }
    report["provenance"] = actual_sha
    for key, expected in EXPECTED_SHA.items():
        if actual_sha[key] != expected:
            failures.append(f"{key} sha mismatch: {actual_sha[key]} != {expected}")

    # (2) Reproduction against the preserved lap280 artifact, not against a claim.
    code, stdout, stderr = run(TARGET)
    parsed = json.loads(stdout) if stdout else {}
    report["fresh_run"] = {
        "exit": code,
        "stdout_sha256": sha256_bytes(stdout),
        "failures": parsed.get("failures"),
        "byte_identical_to_lap280_log": stdout == LAP280_REPORT.read_bytes(),
        "stderr_bytes": len(stderr),
    }
    if code != 0:
        failures.append(f"repaired probe exited {code}: {stderr.strip()[:200]}")
    if parsed.get("failures") != []:
        failures.append(f"repaired probe reported failures: {parsed.get('failures')}")
    if stdout != LAP280_REPORT.read_bytes():
        failures.append("fresh report is not byte-identical to logs/lap280/s1_crossverify_probe.json")

    # (3) Companion invariance.
    companions: dict[str, object] = {}
    for tag, (name, expected) in COMPANIONS.items():
        c_code, c_out, c_err = run(PROBES / name)
        got = sha256_bytes(c_out)
        companions[tag] = {"exit": c_code, "stdout_sha256": got, "matches_record": got == expected}
        if c_code != 0:
            failures.append(f"companion {tag} exited {c_code}: {c_err.strip()[:160]}")
        if got != expected:
            failures.append(f"companion {tag} report drifted: {got} != {expected}")
    report["companions"] = companions

    # (4) This review's own mutants.
    env_text = ENV_MOD.read_text(encoding="utf-8")
    driver_text = DRIVER.read_text(encoding="utf-8")
    for anchor in ("G1_UNIT_X_OFFSET = 0x2A2", "G1_UNIT_Y_OFFSET = 0x2A4",
                   "x=h(G1_UNIT_X_OFFSET)"):
        if anchor not in (env_text if anchor.startswith("G1_") else driver_text):
            failures.append(f"mutation anchor absent, mutants are not meaningful: {anchor!r}")

    mutants = {
        # The original defect class: the named definition disappears.  Before the
        # lap291 repair this path raised AttributeError on None; it must now be a
        # recorded failure instead of a crash.
        "env_definition_removed": (
            env_text.replace("G1_UNIT_Y_OFFSET = 0x2A4\n", ""), driver_text,
            "G1_UNIT_Y_OFFSET definition missing from tools/runtime_env.py"),
        "env_value_drifted": (
            env_text.replace("G1_UNIT_X_OFFSET = 0x2A2", "G1_UNIT_X_OFFSET = 0x2A3"),
            driver_text, "runtime_driver unit offsets drifted"),
        "driver_relapsed_to_literal": (
            env_text, driver_text.replace("x=h(G1_UNIT_X_OFFSET)", "x=h(0x2A2)"),
            "runtime_driver does not bind x to G1_UNIT_X_OFFSET"),
        "driver_bound_to_wrong_constant": (
            env_text, driver_text.replace("x=h(G1_UNIT_X_OFFSET)", "x=h(G1_UNIT_Y_OFFSET)"),
            "runtime_driver does not bind x to G1_UNIT_X_OFFSET"),
        "control_unmutated": (env_text, driver_text, None),
    }

    results: dict[str, object] = {}
    for tag, (env_variant, driver_variant, needle) in mutants.items():
        with tempfile.TemporaryDirectory(prefix=f"lap292_{tag}_") as tmp:
            script = build_sandbox(Path(tmp), env_variant, driver_variant)
            m_code, m_out, m_err = run(script)
        m_parsed = json.loads(m_out) if m_out else {}
        m_failures = m_parsed.get("failures", [])
        results[tag] = {
            "exit": m_code,
            "failures": m_failures,
            "stdout_sha256": sha256_bytes(m_out),
            "traceback": "Traceback" in m_err,
        }
        if needle is None:
            if m_code != 0 or m_failures != []:
                failures.append(f"control sandbox did not reproduce a clean run: {m_failures}")
            if sha256_bytes(m_out) != EXPECTED_SHA["lap280_report"]:
                failures.append("control sandbox report differs from the repository run")
            continue
        if m_code != 1:
            failures.append(f"mutant {tag} exited {m_code}, expected 1")
        if "Traceback" in m_err:
            failures.append(f"mutant {tag} crashed instead of reporting a failure")
        if not any(needle in f for f in m_failures):
            failures.append(f"mutant {tag} did not report {needle!r}: {m_failures}")
    report["mutants"] = results

    report["failures"] = failures
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
