"""Owned Win32 close transport used by the diagnostic trace runner."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import time
from typing import Any, Mapping


class Win32CloseError(RuntimeError):
    """A helper invocation or its machine-readable result failed closed."""

    def __init__(self, message: str, evidence: Mapping[str, Any] | None = None) -> None:
        super().__init__(message)
        self.evidence = dict(evidence or {})


def read_owned_win32_pid(trace_path: Path, run_id: str) -> dict[str, Any]:
    """Read exactly one positive Win32 PID from the install trace snapshot."""
    try:
        raw = trace_path.read_bytes()
        events = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Win32CloseError(f"owned Win32 PID trace read failed: {exc}") from exc
    if not events or any(not isinstance(item, dict) for item in events):
        raise Win32CloseError("owned Win32 PID trace has no object events")
    if any(item.get("run_id") != run_id for item in events):
        raise Win32CloseError("owned Win32 PID trace has a mismatched run_id")
    raw_pids = [item.get("pid") for item in events]
    if any(not isinstance(pid, int) or isinstance(pid, bool) or pid <= 0 for pid in raw_pids):
        raise Win32CloseError("owned Win32 PID trace contains a non-positive or non-integer pid")
    pids = sorted(set(raw_pids))
    if len(pids) != 1:
        raise Win32CloseError(f"owned Win32 PID trace expected one pid, observed {pids}")
    return {
        "pid": pids[0],
        "event_count": len(events),
        "trace": str(trace_path),
        "trace_sha256": hashlib.sha256(raw).hexdigest(),
    }


def request_owned_win32_close(
    helper: Path, pid: int, env: Mapping[str, str], deadline: float, log: Any,
) -> dict[str, Any]:
    """Run the PE32 helper and require its exact single-window PASS result."""
    if pid <= 0:
        raise Win32CloseError("owned Win32 close requested with non-positive pid")
    if deadline <= 0:
        raise Win32CloseError("owned Win32 close deadline must be positive")
    helper = helper.expanduser().resolve(strict=False)
    if helper.suffix.lower() != ".exe" or not helper.is_file() or helper.is_symlink():
        raise Win32CloseError(f"owned Win32 close helper is not a regular PE32 file: {helper}")
    argv = ["wine", str(helper), "--pid", str(pid)]
    started = time.monotonic()
    try:
        result = subprocess.run(
            argv, env=dict(env), cwd=str(helper.parent), capture_output=True,
            text=True, timeout=min(10, deadline), check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise Win32CloseError(f"owned Win32 close helper failed to launch: {exc}") from exc
    stdout = (result.stdout or "").strip()
    stderr = (result.stderr or "").strip()
    if log is not None:
        if stdout:
            log.write(stdout + "\n")
        if stderr:
            log.write(stderr + "\n")
        log.flush()
    lines = [line for line in stdout.splitlines() if line.strip()]
    evidence: dict[str, Any] = {
        "argv": argv, "returncode": result.returncode,
        "stdout": stdout, "stderr": stderr,
        "elapsed_seconds": round(time.monotonic() - started, 3),
    }
    if len(lines) != 1:
        raise Win32CloseError("owned Win32 close helper did not emit exactly one JSON result", evidence)
    try:
        payload = json.loads(lines[0])
    except json.JSONDecodeError as exc:
        raise Win32CloseError(f"owned Win32 close helper emitted malformed JSON: {exc}", evidence) from exc
    if not isinstance(payload, dict):
        raise Win32CloseError("owned Win32 close helper result is not an object", evidence)
    evidence["result"] = payload
    if (
        result.returncode != 0 or payload.get("status") != "PASS" or
        payload.get("requested_pid") != pid or payload.get("match_count") != 1 or
        payload.get("post_result") is not True or not payload.get("matched_hwnd") or
        not isinstance(payload.get("matched_thread"), int) or payload.get("matched_thread", 0) <= 0
    ):
        raise Win32CloseError("owned Win32 close helper rejected the close request", evidence)
    return evidence
