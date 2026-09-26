"""Role routing is inspectable without enabling or invoking paid sessions."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def project(tmp_path: Path) -> Path:
    root = tmp_path / "patch"
    for name in ["loop", "checks", "docs"]:
        shutil.copytree(
            ROOT / name,
            root / name,
            ignore=shutil.ignore_patterns(
                "__pycache__", ".lap_counter", "STOP", "env.local.sh", "FULL_TEST", "ESCALATE_SOL"
            ),
        )
    shutil.copy2(ROOT / ".gitignore", root / ".gitignore")
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["bash", "checks/safety.sh", "pin"], cwd=root, check=True, capture_output=True)
    fakebin = root / "fakebin"
    fakebin.mkdir()
    for name in ["codex", "claude"]:
        path = fakebin / name
        path.write_text(f'#!/bin/sh\ntouch "{root / "agent_called"}"\nexit 98\n')
        path.chmod(0o755)
    return root


def dry(project: Path, role: str, **overrides: str) -> subprocess.CompletedProcess[str]:
    env = dict(
        os.environ,
        LOOP_ENABLE_AGENT="0",
        LOOP_DRY_RUN="1",
        LOOP_MAX_LAPS="1",
        LOOP_PATH=str(project / "fakebin") + ":" + os.environ["PATH"],
        LOOP_TEE_STDOUT="0",
        **overrides,
    )
    return subprocess.run(
        ["bash", "loop/loopctl.sh", "dry", role],
        cwd=project,
        env=env,
        capture_output=True,
        text=True,
        timeout=20,
    )


def latest_lap(project: Path) -> str:
    logs = sorted((project / "logs/laps").glob("*/lap-*.log"))
    assert logs
    return logs[-1].read_text()


def require_original_fixture() -> None:
    if not (ROOT / "Syw2plus/syw2plus_original.exe").is_file():
        pytest.skip("enabled dispatch mock requires the local original guard fixture")


@pytest.mark.parametrize(
    ("role", "expected"),
    [
        ("work", "-m gpt-5.6-luna -c model_reasoning_effort=high"),
        ("astra", "-m gpt-6-astra -c model_reasoning_effort=medium"),
    ],
)
def test_codex_roles_have_fixed_model_and_role_effort(project: Path, role: str, expected: str):
    result = dry(project, role)
    assert result.returncode == 0, result.stdout + result.stderr
    output = latest_lap(project)
    assert expected in output
    assert "resume" not in output and "continue" not in output
    assert not (project / "agent_called").exists()


def test_explicit_claude_work_and_middle_alternatives(project: Path):
    result = dry(project, "work", LOOP_WORKER="claude", LOOP_MIDDLE_PROVIDER="claude")
    assert result.returncode == 0, result.stdout + result.stderr
    output = latest_lap(project)
    assert "claude --print" in output
    assert "--model claude-sonnet-5" in output
    assert "--effort high" in output
    assert "--model claude-opus-5" in output
    assert not (project / "agent_called").exists()


def test_strategy_defaults_to_astra_even_when_other_claude_roles_are_selected(project: Path):
    result = dry(project, "astra", LOOP_WORKER="claude", LOOP_MIDDLE_PROVIDER="claude")
    assert result.returncode == 0, result.stdout + result.stderr
    output = latest_lap(project)
    assert "-m gpt-6-astra -c model_reasoning_effort=medium" in output
    assert "claude --print" not in output.split("--- 실행되었을 명령", 1)[1].split("--- 중간", 1)[0]
    assert not (project / "agent_called").exists()


def test_strategy_can_switch_to_explicit_claude_fable(project: Path):
    result = dry(
        project,
        "astra",
        LOOP_STRATEGY_PROVIDER="claude",
        LOOP_WORKER="codex",
        LOOP_MIDDLE_PROVIDER="codex",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    output = latest_lap(project)
    command = output.split("--- 실행되었을 명령", 1)[1].split("--- 중간", 1)[0]
    assert "claude --print" in command
    assert "--model claude-fable-5" in command
    assert "--effort medium" in command
    assert "gpt-6-astra" not in command
    assert not (project / "agent_called").exists()


def test_fable_strategy_high_is_an_explicit_override(project: Path):
    result = dry(
        project,
        "astra",
        LOOP_STRATEGY_PROVIDER="claude",
        LOOP_ASTRA_EFFORT="high",
    )
    assert result.returncode == 0, result.stdout + result.stderr
    output = latest_lap(project)
    assert "--model claude-fable-5 --effort high" in output
    assert not (project / "agent_called").exists()


def test_invalid_strategy_provider_is_rejected_before_session(project: Path):
    result = dry(project, "astra", LOOP_STRATEGY_PROVIDER="auto")
    assert result.returncode != 0
    logs = "\n".join(path.read_text() for path in (project / "logs").glob("loop-*.log"))
    assert "LOOP_STRATEGY_PROVIDER" in logs
    assert not (project / "agent_called").exists()


def test_astra_high_is_an_explicit_override(project: Path):
    result = dry(project, "astra", LOOP_ASTRA_EFFORT="high")
    assert result.returncode == 0, result.stdout + result.stderr
    output = latest_lap(project)
    assert "-m gpt-6-astra -c model_reasoning_effort=high" in output
    assert not (project / "agent_called").exists()


def test_models_reports_selected_fable_strategy_without_agent_call(project: Path):
    env = dict(
        os.environ,
        LOOP_STRATEGY_PROVIDER="claude",
        LOOP_PATH=str(project / "fakebin") + ":" + os.environ["PATH"],
    )
    result = subprocess.run(
        ["bash", "loop/loopctl.sh", "models"],
        cwd=project,
        env=env,
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "strategy -> claude/claude-fable-5 effort=medium" in result.stdout
    assert "No automatic fallback" in result.stdout
    assert not (project / "agent_called").exists()


def test_strategy_is_astra_command_but_disabled_by_default(project: Path):
    (project / "loop/STOP").touch()
    env = dict(
        os.environ,
        LOOP_ENABLE_AGENT="0",
        LOOP_PATH=str(project / "fakebin") + ":" + os.environ["PATH"],
    )
    result = subprocess.run(
        ["bash", "loop/loopctl.sh", "strategy", "1"],
        cwd=project,
        env=env,
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 2
    assert (project / "loop/STOP").exists()
    assert not (project / "agent_called").exists()


@pytest.mark.parametrize(
    "extra",
    [
        "-c model_reasoning_effort=low",
        "-c model=bad-model",
        "--config model=bad-model",
        "--config model_reasoning_effort=low",
        "-cmodel=bad-model",
        "-mfoo-model",
    ],
)
def test_conflicting_codex_extra_is_rejected_before_session(project: Path, extra: str):
    result = dry(project, "work", LOOP_CODEX_EXTRA=extra)
    assert result.returncode != 0
    logs = "\n".join(path.read_text() for path in (project / "logs").glob("loop-*.log"))
    assert "cannot override fixed role model/effort" in logs
    assert not (project / "agent_called").exists()


def test_enabled_work_dispatches_codex_model_and_high_effort_without_resume(project: Path):
    require_original_fixture()
    (project / "Syw2plus").mkdir()
    shutil.copy2(ROOT / "Syw2plus/syw2plus_original.exe", project / "Syw2plus/syw2plus_original.exe")
    calls = project / "calls"
    fake = project / "fakebin/codex"
    fake.write_text(
        f'#!/bin/sh\nprintf "codex:%s\\n" "$*" >> "{calls}"\ncat >/dev/null\nexit 0\n'
    )
    fake.chmod(0o755)
    env = dict(
        os.environ,
        LOOP_ENABLE_AGENT="1",
        LOOP_DRY_RUN="0",
        LOOP_WORKER="codex",
        LOOP_MIDDLE_PROVIDER="codex",
        LOOP_MAX_LAPS="1",
        LOOP_PATH=str(project / "fakebin") + ":" + os.environ["PATH"],
    )
    result = subprocess.run(
        ["bash", "loop/loopctl.sh", "run", "1"],
        cwd=project,
        env=env,
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    command = calls.read_text()
    assert "-m gpt-5.6-luna" in command
    assert "-c model_reasoning_effort=high" in command
    assert "resume" not in command and "continue" not in command


def test_enabled_plan_uses_explicit_claude_opus_middle_model(project: Path):
    require_original_fixture()
    (project / "Syw2plus").mkdir()
    shutil.copy2(ROOT / "Syw2plus/syw2plus_original.exe", project / "Syw2plus/syw2plus_original.exe")
    calls = project / "calls"
    fake = project / "fakebin/claude"
    fake.write_text(
        f'#!/bin/sh\nprintf "claude:%s\\n" "$*" >> "{calls}"\ncat >/dev/null\nexit 0\n'
    )
    fake.chmod(0o755)
    env = dict(
        os.environ,
        LOOP_ENABLE_AGENT="1",
        LOOP_DRY_RUN="0",
        LOOP_MIDDLE_PROVIDER="claude",
        LOOP_MAX_LAPS="1",
        LOOP_PATH=str(project / "fakebin") + ":" + os.environ["PATH"],
    )
    result = subprocess.run(
        ["bash", "loop/loopctl.sh", "plan", "1"],
        cwd=project,
        env=env,
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    command = calls.read_text()
    assert "--model claude-opus-5" in command
    assert "--effort high" in command
    assert "--resume" not in command and "--continue" not in command
    logs = "\n".join(path.read_text() for path in (project / "logs").glob("loop-*.log"))
    assert "worker=claude/claude-opus-5" in logs


def test_enabled_strategy_dispatches_explicit_claude_fable(project: Path):
    require_original_fixture()
    (project / "Syw2plus").mkdir()
    shutil.copy2(ROOT / "Syw2plus/syw2plus_original.exe", project / "Syw2plus/syw2plus_original.exe")
    calls = project / "calls"
    fake = project / "fakebin/claude"
    fake.write_text(
        f'#!/bin/sh\nprintf "claude:%s\\n" "$*" >> "{calls}"\ncat >/dev/null\nexit 0\n'
    )
    fake.chmod(0o755)
    env = dict(
        os.environ,
        LOOP_ENABLE_AGENT="1",
        LOOP_DRY_RUN="0",
        LOOP_STRATEGY_PROVIDER="claude",
        LOOP_JUDGE="codex",
        LOOP_MAX_LAPS="1",
        LOOP_PATH=str(project / "fakebin") + ":" + os.environ["PATH"],
    )
    result = subprocess.run(
        ["bash", "loop/loopctl.sh", "strategy", "1"],
        cwd=project,
        env=env,
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    command = calls.read_text()
    assert "--model claude-fable-5" in command
    assert "--effort medium" in command
    assert "gpt-6-astra" not in command
    assert "--resume" not in command and "--continue" not in command


def test_worker_escalation_stops_for_explicit_middle_review(project: Path):
    require_original_fixture()
    (project / "Syw2plus").mkdir()
    shutil.copy2(ROOT / "Syw2plus/syw2plus_original.exe", project / "Syw2plus/syw2plus_original.exe")
    calls = project / "calls"
    (project / "fakebin/codex").write_text(
        f'#!/bin/sh\nprintf "codex:%s\\n" "$*" >> "{calls}"\ntouch loop/ESCALATE_SOL\ncat >/dev/null\nexit 0\n'
    )
    (project / "fakebin/claude").write_text(
        f'#!/bin/sh\nprintf "claude:%s\\n" "$*" >> "{calls}"\ncat >/dev/null\nexit 0\n'
    )
    for path in [project / "fakebin/codex", project / "fakebin/claude"]:
        path.chmod(0o755)
    env = dict(
        os.environ,
        LOOP_ENABLE_AGENT="1",
        LOOP_DRY_RUN="0",
        LOOP_WORKER="codex",
        LOOP_MIDDLE_PROVIDER="claude",
        LOOP_MAX_LAPS="2",
        LOOP_PATH=str(project / "fakebin") + ":" + os.environ["PATH"],
    )
    result = subprocess.run(
        ["bash", "loop/loopctl.sh", "run", "2"],
        cwd=project,
        env=env,
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 75, result.stdout + result.stderr
    command = calls.read_text()
    assert command.count("codex:") == 1
    assert "codex:exec" in command and "-m gpt-5.6-luna" in command
    assert "claude:--print" not in command and "--model claude-opus-5" not in command
    assert "--model claude-sonnet-5" not in command
    assert (project / "loop/ESCALATE_SOL").is_file()
    assert "middle review pending" in result.stdout


def test_raw_worker_exit75_without_marker_uses_generic_failure_retry(project: Path):
    require_original_fixture()
    (project / "Syw2plus").mkdir()
    shutil.copy2(ROOT / "Syw2plus/syw2plus_original.exe", project / "Syw2plus/syw2plus_original.exe")
    calls = project / "calls"
    (project / "fakebin/codex").write_text(
        f'#!/bin/sh\nprintf "codex:%s\\n" "$*" >> "{calls}"\ncat >/dev/null\nexit 75\n'
    )
    for path in [project / "fakebin/codex", project / "fakebin/claude"]:
        path.chmod(0o755)
    env = dict(
        os.environ,
        LOOP_ENABLE_AGENT="1",
        LOOP_DRY_RUN="0",
        LOOP_WORKER="codex",
        LOOP_MIDDLE_PROVIDER="codex",
        LOOP_MAX_LAPS="2",
        LOOP_SLEEP_SECONDS="0",
        LOOP_FAIL_BACKOFF_SECONDS="0",
        LOOP_PATH=str(project / "fakebin") + ":" + os.environ["PATH"],
    )
    result = subprocess.run(
        ["bash", "loop/loopctl.sh", "run", "2"],
        cwd=project,
        env=env,
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert calls.read_text().count("codex:") == 2
    assert not (project / "loop/ESCALATE_SOL").exists()
    assert "연속 실패 1/5" in result.stdout
    assert "연속 실패 2/5" in result.stdout
    assert "max-laps(2)" in result.stdout
    assert "middle-review-pending" not in result.stdout


def test_raw_worker_exit75_without_marker_hits_fail_streak_stop(project: Path):
    require_original_fixture()
    (project / "Syw2plus").mkdir()
    shutil.copy2(ROOT / "Syw2plus/syw2plus_original.exe", project / "Syw2plus/syw2plus_original.exe")
    calls = project / "calls"
    (project / "fakebin/codex").write_text(
        f'#!/bin/sh\nprintf "codex:%s\\n" "$*" >> "{calls}"\ncat >/dev/null\nexit 75\n'
    )
    for path in [project / "fakebin/codex", project / "fakebin/claude"]:
        path.chmod(0o755)
    env = dict(
        os.environ,
        LOOP_ENABLE_AGENT="1",
        LOOP_DRY_RUN="0",
        LOOP_WORKER="codex",
        LOOP_MIDDLE_PROVIDER="codex",
        LOOP_MAX_FAIL_STREAK="2",
        LOOP_MAX_LAPS="2",
        LOOP_SLEEP_SECONDS="0",
        LOOP_FAIL_BACKOFF_SECONDS="0",
        LOOP_PATH=str(project / "fakebin") + ":" + os.environ["PATH"],
    )
    result = subprocess.run(
        ["bash", "loop/loopctl.sh", "run", "2"],
        cwd=project,
        env=env,
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 1, result.stdout + result.stderr
    assert calls.read_text().count("codex:") == 2
    assert not (project / "loop/ESCALATE_SOL").exists()
    assert "middle-review-pending" not in result.stdout
    assert "연속 실패 1/2" in result.stdout
    assert "연속 실패 2/2" in result.stdout
    assert "이유=fail-streak" in result.stdout
    assert "max-laps(2)" not in result.stdout
    assert (project / "loop/STOP").is_file()
