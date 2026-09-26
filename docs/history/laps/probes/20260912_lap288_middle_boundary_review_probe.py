"""Independent middle review of the lap287 save-boundary repair.

Three questions, each answered without trusting the lap287 record:

  1. Is ``0x440F5A`` really the terminating ``ret`` of the save entry, and is
     ``0x440F5B`` therefore the correct exclusive end?  Derived here from a raw
     objdump sweep: every branch target inside the window and every ``ret``
     site, plus the padding run and the next function entry.
  2. Do the two new assertions in the lap286 middle probe have falsifying
     power?  Answered by mutating a private copy of that probe and requiring a
     non-empty ``failures`` list for each mutant.
  3. Does the over-wide ``SAVE_END = 0x440FF0`` that still lives in four other
     probes inflate any save-side fwrite count?  Answered by enumerating every
     call site in the gap ``[0x440F5B, 0x440FF0)``.

Read-only: the original executable, the fixtures and the repository probes are
never written.  Mutants are built under a private temporary directory.  No
game, Wine, Xvfb, harness or PNG.
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
EXE = REPO.parent / "Syw2plus" / "syw2plus_original.exe"
EXPECTED_EXE_SHA = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"

SAVE_ENTRY = 0x440C20
CLAIMED_END = 0x440F5B          # exclusive, per the lap287 repair
LEGACY_END = 0x440FF0           # still in four other probes
FWRITE, FREAD = 0x4DA39F, 0x4DA4A9

MIDDLE_PROBE = (REPO / "docs" / "history" / "laps" / "probes"
                / "20260912_lap286_middle_save_layout_review_probe.py")
WORK_PROBE = (REPO / "docs" / "history" / "laps" / "probes"
              / "20260912_lap284_work_save_layout_probe.py")
LAP287_LOG = REPO / "logs" / "lap287" / "work_save_layout_boundary_repair_probe.json"
PYTHON = REPO / ".venv" / "bin" / "python"

LINE_RE = re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2} )+)\s*(\S+)(?:\s+(.*))?$")
IMM_RE = re.compile(r"0x[0-9a-f]+")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def disasm(start: int, stop: int) -> list[tuple[int, str, str]]:
    text = subprocess.run(
        ["objdump", "-d", "-Mintel", "-j", ".text",
         f"--start-address={start:#x}", f"--stop-address={stop:#x}", str(EXE)],
        check=True, capture_output=True, text=True,
    ).stdout
    out = []
    for line in text.splitlines():
        m = LINE_RE.match(line)
        if m:
            out.append((int(m.group(1), 16), m.group(3), (m.group(4) or "").strip()))
    return out


def first_operand(args: str) -> int | None:
    head = args.split()[0] if args.split() else ""
    return int(head, 16) if IMM_RE.fullmatch(head) else None


def boundary_facts() -> dict[str, object]:
    """Re-derive the save entry's end without reusing the claimed constant."""
    code = disasm(SAVE_ENTRY, LEGACY_END)
    rets, escapes, padding_start = [], [], None
    run = 0
    for address, op, args in code:
        if op == "nop":
            run += 1
            if run >= 4 and padding_start is None:
                padding_start = address - (run - 1)
            continue
        run = 0
        if op == "ret":
            rets.append(address)
        if op.startswith("j") and address < CLAIMED_END:
            # Only branches *inside* the claimed window can prove it is too narrow.
            target = first_operand(args)
            if target is not None and not SAVE_ENTRY <= target < CLAIMED_END:
                escapes.append((address, target))
    return {
        "ret_sites_before_claimed_end": [f"{a:#010x}" for a in rets if a < CLAIMED_END],
        "branches_escaping_claimed_window": [f"{a:#010x}->{t:#010x}" for a, t in escapes],
        "first_padding_run_start": f"{padding_start:#010x}" if padding_start else None,
    }


def gap_calls() -> dict[str, list[str]]:
    """Every call site between the repaired end and the legacy end."""
    targets: dict[str, list[str]] = {}
    for address, op, args in disasm(CLAIMED_END, LEGACY_END):
        if op != "call":
            continue
        target = first_operand(args)
        if target is not None:
            targets.setdefault(f"{target:#010x}", []).append(f"{address:#010x}")
    return targets


MUTANTS = {
    # SAVE_END widened back to the pre-repair value, ret rule intact.
    "M1_widened_end": [("SAVE_ENTRY, SAVE_END = 0x440C20, 0x440F5B",
                        "SAVE_ENTRY, SAVE_END = 0x440C20, 0x440FF0")],
    # Widened end *and* the plain-window shape the lap284 work probe still uses.
    "M2_widened_end_plain_window": [
        ("SAVE_ENTRY, SAVE_END = 0x440C20, 0x440F5B",
         "SAVE_ENTRY, SAVE_END = 0x440C20, 0x440FF0"),
        ('        if op == "ret" and address >= furthest_target:\n            return out\n    return out',
         '        if op == "ret" and address >= furthest_target:\n            pass\n    return out'),
        ("            if run >= PAD_RUN:\n                return out",
         "            if run >= PAD_RUN:\n                pass"),
    ],
}


def run_variant(path: Path) -> dict[str, object]:
    proc = subprocess.run([str(PYTHON), str(path)], capture_output=True, text=True)
    report = json.loads(proc.stdout) if proc.stdout.strip() else {}
    failures = report.get("failures", [])
    return {
        "exit_code": proc.returncode,
        "failure_count": len(failures),
        "fread_assertion_fired": any(f"{FREAD:#x}" in f for f in failures),
        "boundary_assertion_fired": any("save body end changed" in f for f in failures),
    }


def build_variants(workdir: Path) -> dict[str, dict[str, object]]:
    source = MIDDLE_PROBE.read_text()
    pinned = source.replace("REPO = Path(__file__).resolve().parents[4]",
                            f'REPO = Path("{REPO}")')
    if pinned == source:
        raise RuntimeError("could not pin REPO in the middle probe copy")
    results: dict[str, dict[str, object]] = {}
    control = workdir / "m0.py"
    control.write_text(pinned)
    results["M0_control"] = run_variant(control)
    for name, edits in MUTANTS.items():
        text = pinned
        for old, new in edits:
            if old not in text:
                raise RuntimeError(f"{name}: anchor missing: {old[:60]!r}")
            text = text.replace(old, new)
        path = workdir / f"{name}.py"
        path.write_text(text)
        results[name] = run_variant(path)
    return results


def main() -> int:
    failures: list[str] = []

    exe_sha = sha256(EXE)
    if exe_sha != EXPECTED_EXE_SHA:
        failures.append(f"original executable SHA mismatch: {exe_sha}")

    facts = boundary_facts()
    if facts["branches_escaping_claimed_window"]:
        failures.append(f"branch leaves the claimed save window: {facts['branches_escaping_claimed_window']}")
    if facts["ret_sites_before_claimed_end"][-1:] != [f"{CLAIMED_END - 1:#010x}"]:
        failures.append(f"last ret before the claimed end is not {CLAIMED_END - 1:#x}: "
                        f"{facts['ret_sites_before_claimed_end']}")
    if facts["first_padding_run_start"] != f"{CLAIMED_END:#010x}":
        failures.append(f"padding does not start at the claimed end: {facts['first_padding_run_start']}")

    gap = gap_calls()
    if f"{FWRITE:#010x}" in gap:
        failures.append(f"the legacy window really did add fwrite sites: {gap[f'{FWRITE:#010x}']}")

    with tempfile.TemporaryDirectory(prefix="lap288_middle_") as tmp:
        mutants = build_variants(Path(tmp))
    if mutants["M0_control"]["exit_code"] != 0 or mutants["M0_control"]["failure_count"]:
        failures.append(f"control run is not clean: {mutants['M0_control']}")
    for name in MUTANTS:
        if mutants[name]["exit_code"] == 0:
            failures.append(f"{name} survived: the repaired assertions do not kill it")
    if not mutants["M2_widened_end_plain_window"]["fread_assertion_fired"]:
        failures.append("the 0x4DA4A9 assertion never fires, even in the plain-window drift")
    if mutants["M1_widened_end"]["fread_assertion_fired"]:
        failures.append("unexpected: M1 fired the fread assertion")

    legacy_end_probes = sorted(
        p.name for p in MIDDLE_PROBE.parent.glob("*.py")
        if p != Path(__file__).resolve()
        and f"{LEGACY_END:#x}".upper()[2:] in p.read_text().upper()
        and "SAVE_END" in p.read_text()
    )

    report = {
        "exe_sha256": exe_sha,
        "boundary": {
            "claimed_exclusive_end": f"{CLAIMED_END:#010x}",
            **facts,
        },
        "gap_between_repaired_and_legacy_end": {
            "range": f"{CLAIMED_END:#010x}..{LEGACY_END:#010x}",
            "call_targets": gap,
            "fwrite_sites": gap.get(f"{FWRITE:#010x}", []),
        },
        "mutation_matrix": mutants,
        "lap287_log_sha256": sha256(LAP287_LOG) if LAP287_LOG.exists() else None,
        "repaired_probe_sha256": sha256(MIDDLE_PROBE),
        "work_probe_sha256": sha256(WORK_PROBE),
        "work_probe_save_end_line": next(
            (line.strip() for line in WORK_PROBE.read_text().splitlines()
             if line.startswith("SAVE_ENTRY, SAVE_END")), None),
        "probes_still_carrying_legacy_end": legacy_end_probes,
        "game_started": False,
        "wine_or_xvfb_started": False,
        "originals_written": False,
        "failures": failures,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
