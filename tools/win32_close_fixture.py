#!/usr/bin/env python3
"""Build and run the isolated PE32 owned-close transport fixture."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
from typing import Any

from tools.win32_close_transport import Win32CloseError, request_owned_win32_close

ROOT = Path(__file__).resolve().parents[1]
CC = "i686-w64-mingw32-gcc"
COMMON = [
    CC, "-m32", "-Wall", "-Wextra", "-O2", "-fno-stack-protector",
    "-mno-stack-arg-probe", "-nostartfiles", "-nodefaultlibs",
    "-Wl,--subsystem,windows",
]
LINK = ["-lkernel32", "-luser32"]


def build(out_dir: Path) -> dict[str, str]:
    """Build both PE32 programs in an out-of-tree directory."""
    out_dir = out_dir.expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    if any(out_dir.iterdir()):
        raise RuntimeError(f"out-of-tree build directory is not empty: {out_dir}")
    outputs = {
        "helper": out_dir / "win32_close_helper.exe",
        "target": out_dir / "win32_close_target.exe",
    }
    sources = {
        "helper": ROOT / "tools/win32_close_helper.c",
        "target": ROOT / "tools/win32_close_target.c",
    }
    for name, output in outputs.items():
        subprocess.run(
            [*COMMON, "-Wl,-e,_WinMain@16", "-o", str(output),
             str(sources[name]), *LINK],
            cwd=out_dir, check=True, capture_output=True, text=True,
        )
    return {name: str(path) for name, path in outputs.items()}


def _start_xvfb() -> tuple[subprocess.Popen[str], str]:
    process = subprocess.Popen(
        ["Xvfb", "-displayfd", "1", "-screen", "0", "1024x768x24", "-nolisten", "tcp"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    assert process.stdout is not None
    number = process.stdout.readline().strip()
    if not number.isdigit():
        process.terminate()
        process.wait(timeout=5)
        raise RuntimeError("Xvfb did not report a display")
    return process, f":{number}"


def _events(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def _run_case(
    target: Path, helper: Path, prefix: Path, display: str, mode: str,
) -> dict[str, Any]:
    env = dict(os.environ, WINEPREFIX=str(prefix), WINEARCH="win32", DISPLAY=display, WINEDEBUG="-all")
    log_path = prefix / "drive_c" / "win32_close_fixture.jsonl"
    log_path.unlink(missing_ok=True)
    target_process = subprocess.Popen(
        ["wine", str(target), "--mode", mode], cwd=target.parent, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    deadline = time.monotonic() + 10
    ready: dict[str, Any] | None = None
    while time.monotonic() < deadline:
        for event in _events(log_path):
            if event.get("event") == "ready":
                ready = event
                break
        if ready is not None:
            break
        if target_process.poll() is not None:
            break
        time.sleep(0.05)
    if ready is None:
        target_process.terminate()
        target_process.wait(timeout=5)
        raise RuntimeError(f"fixture target did not become ready: mode={mode}")
    pid = int(ready["pid"])
    requested_pid = pid if mode == "single" else (pid + 1 if mode == "wrong-pid" else pid)
    try:
        helper_evidence = request_owned_win32_close(helper, requested_pid, env, 10, None)
    except Win32CloseError as exc:
        helper_evidence = exc.evidence
    target_process.wait(timeout=10)
    events = _events(log_path)
    return {
        "mode": mode, "target_pid": pid, "requested_pid": requested_pid,
        "helper_returncode": helper_evidence.get("returncode"),
        "helper_stdout": helper_evidence.get("stdout", ""),
        "helper_stderr": helper_evidence.get("stderr", ""),
        "helper_evidence": helper_evidence,
        "target_returncode": target_process.returncode,
        "target_events": events,
        "wm_close_count": sum(1 for event in events if event.get("event") == "wm_close"),
        "final_marker": any(event.get("event") == "exit" for event in events),
    }


def run_fixture(build_dir: Path, evidence_dir: Path) -> dict[str, Any]:
    """Run one positive and three fail-closed cases in fresh Wine/Xvfb state."""
    helper = build_dir / "win32_close_helper.exe"
    target = build_dir / "win32_close_target.exe"
    if not helper.is_file() or not target.is_file():
        raise RuntimeError("fixture PE32 files are missing; run build first")
    evidence_dir = evidence_dir.expanduser().resolve()
    evidence_dir.mkdir(parents=True, exist_ok=False)
    prefix = Path(tempfile.mkdtemp(prefix="syw2-owned-close-"))
    xvfb, display = _start_xvfb()
    env = dict(os.environ, WINEPREFIX=str(prefix), WINEARCH="win32", DISPLAY=display, WINEDEBUG="-all")
    try:
        subprocess.run(["wineboot", "-u"], env=env, check=True, timeout=30,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        cases = [
            _run_case(target, helper, prefix, display, "single"),
            _run_case(target, helper, prefix, display, "wrong-pid"),
            _run_case(target, helper, prefix, display, "none"),
            _run_case(target, helper, prefix, display, "multiple"),
        ]
        report = {
            "fixture": "fresh PE32 target/helper; fresh Wine prefix; fresh Xvfb",
            "prefix": str(prefix), "display": display, "cases": cases,
            "positive_pass": (
                cases[0]["helper_returncode"] == 0 and cases[0]["wm_close_count"] == 1
                and cases[0]["final_marker"]
            ),
            "negative_fail_closed": all(
                case["helper_returncode"] != 0 and case["wm_close_count"] == 0
                and case["final_marker"] for case in cases[1:]
            ),
        }
        (evidence_dir / "report.json").write_text(json.dumps(report, indent=2) + "\n")
        return report
    finally:
        subprocess.run(["wineserver", "-k"], env=env, check=False,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["wineserver", "-w"], env=env, check=False,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if xvfb.poll() is None:
            xvfb.terminate()
            xvfb.wait(timeout=5)
        shutil.rmtree(prefix, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    build_parser = sub.add_parser("build")
    build_parser.add_argument("--out-dir", type=Path, required=True)
    run_parser = sub.add_parser("run")
    run_parser.add_argument("--build-dir", type=Path, required=True)
    run_parser.add_argument("--evidence-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "build":
        print(json.dumps(build(args.out_dir), indent=2))
        return 0
    report = run_fixture(args.build_dir, args.evidence_dir)
    print(json.dumps(report, indent=2))
    return 0 if report["positive_pass"] and report["negative_fail_closed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
