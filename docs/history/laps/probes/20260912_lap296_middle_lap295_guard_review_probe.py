"""lap296 middle review — independent check of the lap295 bounded repair.

lap295 (work tier) guarded the two unprotected ``pinned`` consumers that
``G1_S1_MIDDLE_ACCEPTANCE_LAP277.md`` §4.6.3 located at line 156 and line 167 of
``20260912_lap280_middle_s1_crossverify_probe.py``.  This review does not trust
the lap295 record.  It re-measures §4.6.4's three success conditions and then
asks two questions the earlier reviews did not:

  1. Did the guards cost the probe any falsifying power?  A value that drifts,
     a binding that relapses to a literal and a wrong accessor offset must all
     still be reported, not silently skipped by the new ``in pinned`` tests.
  2. Is the §4.6.3 invariant ("no unguarded ``pinned`` indexing after the
     missing-definition branch") actually complete?  ``type`` and ``owner`` do
     not come from ``tools/runtime_env.py`` at all — they are scraped out of
     ``runtime_driver.py`` with an unguarded ``re.search(...).group(1)``.  The
     W2 blocker in docs/STATUS.md asks work tier to promote those same magic
     literals to named constants, which is exactly the edit this probe mutates.

Read-only with respect to the repository: the original executable, the two
implementation modules and every repository probe are only ever read.  Mutants
live in a private temporary tree and reach the executable through a symlink.
No game, no Wine, no Xvfb, no Stage B, no runtime budget, no PNG.

Usage: .venv/bin/python docs/history/laps/probes/20260912_lap296_middle_lap295_guard_review_probe.py
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

# What this review expects to find *before* it runs anything.  The target probe
# SHA is the one lap295 recorded as its post-repair state; the two review probes
# must still be the untouched artifacts §4.6.4 item 5 pins.
EXPECTED_SHA = {
    "target_probe": "88d8628119cab28457fe32ce02e0be823e940e4a64a5f6b43da251daf2d9a18d",
    "lap292_review_probe": "2aaac7a08619cc4135f4540582e611d07aa980e5380b5ec5255688cf33491335",
    "lap294_scope_probe": "8fe0d2575005b4d647e85c0c4377a2d132fc872a30a1e939e8b78171671ec469",
    "runtime_env": "dd2ad0439111d6b1e098d0ea771db172847dfa42f04ed085c4567f2ac8500190",
    "runtime_driver": "ae4ff9393247ce31eab7c953b040f7d3c5aa8b0386af025046382c7d4e4291b5",
    "original_exe": "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac",
    "lap280_report": "3d4fe30703a4d3797bd233cb0d8b34026258356807173ec35240e6a86d6a9126",
}

PROBE_SHA_PATHS = {
    "target_probe": TARGET,
    "lap292_review_probe": PROBES / "20260912_lap292_middle_lap280_repair_review_probe.py",
    "lap294_scope_probe": PROBES / "20260912_lap294_middle_missing_definition_scope_probe.py",
    "runtime_env": ENV_MOD,
    "runtime_driver": DRIVER,
    "original_exe": EXE,
    "lap280_report": LAP280_REPORT,
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

# Anchors every mutation depends on.  If one is gone the mutants prove nothing.
ANCHORS = {
    "env:G1_UNIT_X_OFFSET = 0x2A2": ENV_MOD,
    "env:G1_UNIT_Y_OFFSET = 0x2A4": ENV_MOD,
    "env:G1_UNIT_INTERNAL_ID_OFFSET = 0x29C": ENV_MOD,
    "driver:internal_id=i(G1_UNIT_INTERNAL_ID_OFFSET)": DRIVER,
    "driver:type=u[0x8D]": DRIVER,
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def run(script: Path) -> tuple[int, bytes, str]:
    proc = subprocess.run([str(PYTHON), str(script)], capture_output=True)
    return proc.returncode, proc.stdout, proc.stderr.decode("utf-8", "replace")


def sandbox(root: Path, env_text: str, driver_text: str) -> Path:
    """Private tree whose ``parents[4]`` is ``root``; two modules are replaced."""
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

    # (1) Provenance — including proof that neither review probe was edited.
    actual = {key: sha256(path) for key, path in PROBE_SHA_PATHS.items()}
    report["provenance"] = actual
    for key, expected in EXPECTED_SHA.items():
        if actual[key] != expected:
            failures.append(f"{key} sha mismatch: {actual[key]} != {expected}")

    # (2) §4.6.4 condition 1 — fresh normal run against the preserved artifact.
    code, stdout, stderr = run(TARGET)
    parsed = json.loads(stdout) if stdout else {}
    report["fresh_run"] = {
        "exit": code,
        "stdout_bytes": len(stdout),
        "stdout_sha256": sha256_bytes(stdout),
        "failures": parsed.get("failures"),
        "byte_identical_to_lap280_log": stdout == LAP280_REPORT.read_bytes(),
        "stderr_bytes": len(stderr),
    }
    if code != 0:
        failures.append(f"normal run exited {code}: {stderr.strip()[:200]}")
    if parsed.get("failures") != []:
        failures.append(f"normal run reported failures: {parsed.get('failures')}")
    if stdout != LAP280_REPORT.read_bytes():
        failures.append("normal report is not byte-identical to logs/lap280/s1_crossverify_probe.json")

    # (3) §4.6.4 condition 2 — companion invariance.
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

    env_text = ENV_MOD.read_text(encoding="utf-8")
    driver_text = DRIVER.read_text(encoding="utf-8")
    for anchor, path in ANCHORS.items():
        text = env_text if path is ENV_MOD else driver_text
        if anchor.split(":", 1)[1] not in text:
            failures.append(f"mutation anchor absent, mutants prove nothing: {anchor!r}")

    def drop(name: str) -> str:
        line = next(l for l in env_text.splitlines() if l.startswith(f"{name} = "))
        return env_text.replace(line + "\n", "")

    # (4) This review's own mutants.  Groups A and B are graded; group C is a
    #     measurement of a blind spot and is recorded without a verdict.
    mutants = {
        # A — §4.6.4 condition 3: every missing definition must become a named
        #     failure with a non-empty report, never a traceback.
        "A_removed_x": (drop("G1_UNIT_X_OFFSET"), driver_text,
                        ["G1_UNIT_X_OFFSET definition missing from tools/runtime_env.py"]),
        "A_removed_y": (drop("G1_UNIT_Y_OFFSET"), driver_text,
                        ["G1_UNIT_Y_OFFSET definition missing from tools/runtime_env.py"]),
        "A_removed_internal_id": (drop("G1_UNIT_INTERNAL_ID_OFFSET"), driver_text,
                                  ["G1_UNIT_INTERNAL_ID_OFFSET definition missing "
                                   "from tools/runtime_env.py"]),
        # B — the guards must not have cost the probe any falsifying power.
        "B_value_drifted": (
            env_text.replace("G1_UNIT_INTERNAL_ID_OFFSET = 0x29C",
                             "G1_UNIT_INTERNAL_ID_OFFSET = 0x298"),
            driver_text,
            ["runtime_driver unit offsets drifted",
             "accessor 0x40F540 does not read the internal_id field"]),
        "B_binding_relapsed": (
            env_text,
            driver_text.replace("internal_id=i(G1_UNIT_INTERNAL_ID_OFFSET)",
                                "internal_id=i(0x29C)"),
            ["runtime_driver does not bind internal_id to G1_UNIT_INTERNAL_ID_OFFSET"]),
        "control_unmutated": (env_text, driver_text, []),
    }

    results: dict[str, object] = {}
    for tag, (env_variant, driver_variant, needles) in mutants.items():
        with tempfile.TemporaryDirectory(prefix=f"lap296_{tag}_") as tmp:
            script = sandbox(Path(tmp), env_variant, driver_variant)
            m_code, m_out, m_err = run(script)
        m_parsed = json.loads(m_out) if m_out else {}
        m_failures = m_parsed.get("failures", [])
        results[tag] = {
            "exit": m_code,
            "stdout_bytes": len(m_out),
            "stdout_sha256": sha256_bytes(m_out),
            "failures": m_failures,
            "crash": m_err.strip().splitlines()[-1] if "Traceback" in m_err else None,
        }
        if not needles:
            if m_code != 0 or m_failures != []:
                failures.append(f"control did not reproduce a clean run: {m_code} {m_failures}")
            if sha256_bytes(m_out) != EXPECTED_SHA["lap280_report"]:
                failures.append("control report differs from the repository run")
            continue
        if m_code != 1:
            failures.append(f"mutant {tag} exited {m_code}, expected 1")
        if not m_out:
            failures.append(f"mutant {tag} produced a 0-byte report")
        if "Traceback" in m_err:
            failures.append(f"mutant {tag} crashed instead of reporting: {m_err.strip()[-160:]}")
        for needle in needles:
            if not any(needle in f for f in m_failures):
                failures.append(f"mutant {tag} did not report {needle!r}: {m_failures}")
    report["mutants"] = results

    # (C) Blind-spot measurement, not a verdict.  ``type``/``owner`` are scraped
    #     from runtime_driver.py by an unguarded ``re.search(...).group(1)``.
    #     The W2 blocker asks work tier to replace exactly these literals with
    #     named constants; this measures what that edit would do to the probe.
    blind: dict[str, object] = {}
    for tag, variant in {
        "C_w2_type_promoted_to_constant":
            driver_text.replace("type=u[0x8D]", "type=u[G1_UNIT_TYPE_OFFSET]"),
        "C_w2_owner_promoted_to_constant":
            driver_text.replace("owner=u[0x8E]", "owner=u[G1_UNIT_OWNER_OFFSET]"),
    }.items():
        with tempfile.TemporaryDirectory(prefix=f"lap296_{tag}_") as tmp:
            script = sandbox(Path(tmp), env_text, variant)
            b_code, b_out, b_err = run(script)
        blind[tag] = {
            "exit": b_code,
            "stdout_bytes": len(b_out),
            "crash": b_err.strip().splitlines()[-1] if "Traceback" in b_err else None,
            "named_failure": bool(json.loads(b_out).get("failures")) if b_out else False,
        }
    report["blind_spot_w2"] = blind
    report["blind_spot_verdict"] = (
        "unguarded"
        if any(v["crash"] for v in blind.values())
        else "guarded"
    )

    report["failures"] = failures
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
