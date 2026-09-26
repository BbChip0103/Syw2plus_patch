"""Read-only setup/runtime diagnostics and manifest-hook contracts."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from tools import runtime_env


ROOT = Path(__file__).resolve().parents[1]


def test_fake_missing_tool_is_reported_without_invocation():
    statuses = runtime_env.probe_tools(lambda name: "/fake/bin/" + name if name == "make" else None)

    assert statuses["make"].present
    assert statuses["wine"].present is False
    assert statuses["Xvfb"].path is None


def test_require_runtime_fails_without_manifest_and_tools(tmp_path: Path):
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools/check_setup.py"),
            "--require-runtime",
            "--runtime-manifest",
            str(tmp_path / "missing.json"),
        ],
        cwd=ROOT,
        env={"PATH": str(tmp_path)},
        capture_output=True,
        text=True,
        check=False,
    )

    report = json.loads(result.stdout)
    assert result.returncode == 1
    assert report["ok"] is False
    assert report["runtime"]["manifest"]["valid"] is False
    assert report["runtime"]["missing_tools"]
    assert report["runtime"]["side_effects"] is False


def test_manifest_validation_uses_runtime_environment_contract(tmp_path: Path):
    path = tmp_path / "runtime.json"
    path.write_text("{}", encoding="utf-8")

    try:
        runtime_env.check_runtime(path)
    except runtime_env.RuntimeSafetyError as exc:
        assert "invalid runtime manifest" in str(exc)
    else:  # pragma: no cover - a malformed manifest must never pass
        raise AssertionError("malformed manifest was accepted")


def test_model_probe_uses_version_only_and_does_not_pass_process_environment():
    calls: list[tuple[list[str], dict[str, str]]] = []

    def runner(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append((command, kwargs["env"]))  # type: ignore[arg-type]
        return subprocess.CompletedProcess(command, 0, "codex 1.0\n", "")

    result = runtime_env.probe_model_clis(lambda name: "/bin/" + name, runner)

    assert result["codex"]["version"] == "codex 1.0"
    assert all(command[1:] == ["--version"] for command, _ in calls)
    assert all("OPENAI_API_KEY" not in env for _, env in calls)
