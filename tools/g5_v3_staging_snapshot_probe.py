#!/usr/bin/env python3
"""Drive the v3 chunked order-dispatch candidate under
``tools/g5_v3_staging_snapshot_trace.py`` to see whether each of the 3
chunked calls to the order-record builder stages an independent record, or
whether back-to-back chunk calls within one click overwrite/clobber the
staging memory before the per-tick consumer can read it.

See that trace script's docstring. This reuses ``g5_v3_chunk_dispatch_probe``'s
runtime setup (fixture, drag, order click) verbatim, only swapping which gdb
script is attached.

Read-only investigation harness: the only product-EXE write is building the
already-approved v3 candidate into a private, isolated game copy (never the
protected original).
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import time
from typing import Any

from tools.g5_v3_chunk_dispatch_probe import run_probe as _base_run_probe
from tools import g5_v3_chunk_dispatch_probe as base
from tools.g5_v3_chunk_dispatch_probe import ProbeError

REPO = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = base.DEFAULT_SOURCE
DEFAULT_RUNTIME_ROOT = REPO / "local" / "runtime" / "g5-lap685-v3-staging-snapshot-trace"
GDB_SCRIPT = REPO / "tools" / "g5_v3_staging_snapshot_trace.py"


def run_trace(pid: int, control: Path, *, order_click) -> dict[str, Any]:
    control.mkdir(parents=True, exist_ok=True)
    armed = control / "armed.json"
    stop_flag = control / "stop.flag"
    summary_path = control / "trace-summary.json"
    events_path = control / "events.jsonl"
    for stale in (armed, stop_flag, summary_path, events_path):
        stale.unlink(missing_ok=True)
    env = dict(os.environ, G5_V3_STAGING_TRACE_CONTROL=str(control))
    log_path = control / "gdb-v3-staging-snapshot.log"
    with log_path.open("w", encoding="utf-8") as log:
        gdb_proc = subprocess.Popen(
            ["gdb", "-p", str(pid), "--batch", "-x", str(GDB_SCRIPT)],
            env=env, stdout=log, stderr=log,
        )
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline and not armed.exists():
            if gdb_proc.poll() is not None:
                raise ProbeError(f"gdb exited before arming (rc={gdb_proc.returncode})")
            time.sleep(0.05)
        if not armed.exists():
            gdb_proc.terminate()
            raise ProbeError("v3 staging-snapshot trace did not arm before timeout")
        time.sleep(0.3)
        try:
            order_click()
        finally:
            time.sleep(2.0)
            stop_flag.write_text("1", encoding="utf-8")
            if gdb_proc.poll() is None:
                gdb_proc.send_signal(signal.SIGINT)
                try:
                    gdb_proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    gdb_proc.send_signal(signal.SIGINT)
                    try:
                        gdb_proc.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        gdb_proc.kill()
                        gdb_proc.wait(timeout=5)
    summary: dict[str, Any] = {}
    if summary_path.exists():
        summary.update(json.loads(summary_path.read_text(encoding="utf-8")))
    else:
        summary["error"] = "no trace-summary.json written"
    events: list[dict[str, Any]] = []
    if events_path.exists():
        for line in events_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                events.append(json.loads(line))
    summary["events"] = events
    return summary


def run_probe(source: Path, runtime_root: Path, artifact_root: Path, order_kind: str) -> dict[str, Any]:
    # Swap in this module's run_trace before delegating to the shared
    # runtime-setup/order-click logic in g5_v3_chunk_dispatch_probe.
    original_run_trace = base.run_trace
    base.run_trace = run_trace
    try:
        return _base_run_probe(source, runtime_root, artifact_root, order_kind)
    finally:
        base.run_trace = original_run_trace


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--runtime-root", type=Path, default=DEFAULT_RUNTIME_ROOT)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--order-kind", choices=["move", "attack"], default="move")
    args = parser.parse_args(argv)
    result = run_probe(args.source, args.runtime_root, args.artifact_root, args.order_kind)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "TRACE_COMPLETE" and result.get("cleanup", {}).get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
