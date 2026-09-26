"""Fail-closed unit checks for the PE32 owned Win32 close boundary."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess

import pytest

from tools import win32_close_transport


def _trace(path: Path, pids: list[int]) -> None:
    path.write_text("".join(json.dumps({"run_id": "run-1", "pid": pid}) + "\n" for pid in pids))


def test_read_owned_win32_pid_requires_one_positive_pid(tmp_path: Path):
    trace = tmp_path / "install.jsonl"
    _trace(trace, [42, 42])
    assert win32_close_transport.read_owned_win32_pid(trace, "run-1")["pid"] == 42

    _trace(trace, [42, 43])
    with pytest.raises(win32_close_transport.Win32CloseError, match="expected one pid"):
        win32_close_transport.read_owned_win32_pid(trace, "run-1")

    _trace(trace, [0])
    with pytest.raises(win32_close_transport.Win32CloseError, match="non-positive"):
        win32_close_transport.read_owned_win32_pid(trace, "run-1")


def test_helper_result_requires_exact_single_match_and_post(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    helper = tmp_path / "helper.exe"
    helper.write_bytes(b"PE32 fixture")
    result = {"status": "PASS", "requested_pid": 42, "matched_hwnd": "0x00000001",
              "matched_thread": 7, "match_count": 1, "post_result": True}

    monkeypatch.setattr(
        win32_close_transport.subprocess, "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args[0], 0, json.dumps(result) + "\n", "",
        ),
    )
    evidence = win32_close_transport.request_owned_win32_close(
        helper, 42, {"WINEPREFIX": "private"}, 1, None,
    )
    assert evidence["result"] == result
    assert evidence["argv"] == ["wine", str(helper), "--pid", "42"]

    failed = dict(result, match_count=2, post_result=False, status="FAIL")
    monkeypatch.setattr(
        win32_close_transport.subprocess, "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args[0], 2, json.dumps(failed) + "\n", "",
        ),
    )
    with pytest.raises(win32_close_transport.Win32CloseError, match="rejected"):
        win32_close_transport.request_owned_win32_close(
            helper, 42, {"WINEPREFIX": "private"}, 1, None,
        )
