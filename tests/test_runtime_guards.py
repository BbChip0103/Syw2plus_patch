"""Regression guards for the isolated runtime boundary.

These tests mock process boundaries deliberately: no Wine, Xvfb, model CLI,
or real game is started by the test suite.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess

import pytest

from tools import runtime_env


def test_forged_manifest_components_outside_local_runtime_are_refused(tmp_path: Path):
    run = tmp_path / "forged-run"
    run.mkdir()
    manifest = run / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "game": {"root": str(tmp_path / "game")},
                "wine": {"prefix": str(tmp_path / "prefix")},
                "output": {"run_dir": str(run), "evidence_dir": str(tmp_path / "output")},
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(runtime_env.RuntimeSafetyError, match="dedicated private run"):
        runtime_env._manifest(manifest)


def test_busy_prefix_refuses_before_wineserver_launch_or_xvfb(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    run = tmp_path / "run"
    output = run / "output"
    prefix = run / "prefix"
    game = run / "game"
    manifest = run / "manifest.json"
    run.mkdir()
    prefix.mkdir()
    game.mkdir()
    manifest.write_text("{}", encoding="utf-8")
    calls: list[tuple[str, ...]] = []

    monkeypatch.setattr(runtime_env, "check_runtime", lambda _: {"ok": True})
    monkeypatch.setattr(runtime_env, "_manifest", lambda _: ({}, game, prefix, output))
    monkeypatch.setattr(runtime_env, "_prefix_pids", lambda _: [4242])

    def forbidden_run(*args, **kwargs):
        calls.append(tuple(args[0]))
        raise AssertionError("process launch/cleanup must not run for a busy prefix")

    monkeypatch.setattr(runtime_env.subprocess, "Popen", forbidden_run)
    monkeypatch.setattr(runtime_env, "_xvfb", forbidden_run)
    monkeypatch.setattr(runtime_env, "_run", forbidden_run)

    with pytest.raises(runtime_env.RuntimeSafetyError, match="already in use"):
        runtime_env.smoke(manifest, timeout=1)
    assert calls == []


def test_runtime_main_smoke_rejects_failed_cleanup(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    manifest = tmp_path / "manifest.json"
    manifest.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(
        runtime_env,
        "smoke",
        lambda _path, timeout=60: {"cleanup": {"ok": False, "error": "wineserver cleanup failed"}},
    )

    result = runtime_env.runtime_main(["smoke", "--manifest", str(manifest)])

    assert result != 0


def test_inmmserv_window_is_not_registry_error_but_desktop_only_is_not_ready(
    monkeypatch: pytest.MonkeyPatch,
):
    outputs = iter(
        [
            "0x001 root window\n  0x002 _inmmserv diagnostic window\n",
            "0x001 root window\n",
        ]
    )

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(args[0], 0, next(outputs), "")

    monkeypatch.setattr(runtime_env.subprocess, "run", fake_run)

    assert "_inmmserv" in runtime_env._window_tree(":199", 1)
    with pytest.raises(runtime_env.RuntimeSafetyError, match="no X11 game window"):
        runtime_env._window_tree(":199", 1)

