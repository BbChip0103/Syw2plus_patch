"""No paid sessions: test dry/disabled/STOP and failure gates on private copies."""

import os
from pathlib import Path
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def project(tmp_path):
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
    # Read-only setup pin, no game needed for dry runs and no initial commit.
    subprocess.run(["bash", "checks/safety.sh", "pin"], cwd=root, check=True, capture_output=True)
    return root


def run(project, *args):
    env = dict(
        os.environ,
        LOOP_ENABLE_AGENT="0",
        LOOP_MAX_LAPS="1",
        LOOP_WORKER="codex",
        LOOP_JUDGE="claude",
        LOOP_PATH=os.environ["PATH"],
        LOOP_DRY_RUN="1",
    )
    # Failure if dry mode accidentally tries either agent binary, including --help.
    fakebin = project / "fakebin"
    fakebin.mkdir(exist_ok=True)
    for name in ["codex", "claude"]:
        file = fakebin / name
        file.write_text('#!/bin/sh\ntouch "' + str(project / "agent_called") + '"\nexit 98\n')
        file.chmod(0o755)
    env["LOOP_PATH"] = str(fakebin) + ":" + env["LOOP_PATH"]
    return subprocess.run(
        ["bash", "loop/loopctl.sh", *args],
        cwd=project,
        env=env,
        capture_output=True,
        text=True,
        timeout=20,
    )


def test_dry_fresh_laps_without_agent_or_commit(project):
    result = run(project, "dry", "2")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "max-laps(2)" in result.stdout
    assert (project / "loop/.lap_counter").read_text() == "2"
    assert not (project / "agent_called").exists()
    assert len(list((project / "logs/laps").rglob("lap-*.log"))) == 2
    assert (
        subprocess.run(
            ["git", "rev-parse", "--verify", "HEAD"], cwd=project, capture_output=True
        ).returncode
        != 0
    )


def test_paid_run_disabled_without_removing_stop(project):
    (project / "loop/STOP").touch()
    result = run(project, "run", "1")
    assert result.returncode == 2
    assert (project / "loop/STOP").exists()
    assert not (project / "agent_called").exists()


def test_stop_and_resume_do_not_start_a_session(project):
    assert run(project, "stop").returncode == 0
    assert (project / "loop/STOP").exists()
    assert run(project, "resume").returncode == 0
    assert not (project / "loop/STOP").exists()
    assert not (project / "loop/.lap_counter").exists()


def test_reference_mutation_blocks_loop(project):
    with (project / "docs/reference/original_profile.json").open("a") as stream:
        stream.write(" ")
    result = run(project, "dry", "1")
    assert result.returncode != 0
    assert "safety-violation-at-startup" in result.stdout
    assert not (project / "loop/.lap_counter").exists()
    assert not (project / "agent_called").exists()


def test_bad_numeric_limit_does_not_run_forever(project):
    result = run(project, "dry", "invalid")
    assert result.returncode == 2
    assert "Invalid numeric setting" in result.stderr


def test_service_is_separate_and_fast_gate_is_not_runtime():
    control = (ROOT / "loop/loopctl.sh").read_text()
    assert 'UNIT="syw2plus-patch-loop.service"' in control
    service = (ROOT / "loop/syw2plus-patch-loop.service").read_text()
    assert "SyslogIdentifier=syw2plus-patch-loop" in service
    gate = (ROOT / "tests/test_build.sh").read_text()
    assert "runtime=NOT_RUN" in gate and "make check" in gate


def test_writer_lock_prevents_another_lap(project):
    import fcntl

    with (project / ".git/syw2plus-patch-loop.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        result = run(project, "dry", "1")
    assert result.returncode == 73
    assert not (project / "loop/.lap_counter").exists()


@pytest.mark.parametrize("mutate,expected", [(False, "failed"), (True, "invalidated")])
def test_mock_gate_failure_or_source_drift_is_not_success(project, mutate, expected):
    original = ROOT / "Syw2plus/syw2plus_original.exe"
    if not original.exists():
        pytest.skip("Real-loop original guard requires local EXE; agents remain mocked")
    (project / "Syw2plus").mkdir()
    shutil.copy2(original, project / "Syw2plus/syw2plus_original.exe")
    fakebin = project / "mockbin"
    fakebin.mkdir()
    for name in ["codex", "claude"]:
        file = fakebin / name
        file.write_text("#!/bin/sh\ncat >/dev/null\ntouch loop/FULL_TEST\nexit 0\n")
        file.chmod(0o755)
    (project / "tests").mkdir()
    gate = project / "tests/test_build.sh"
    gate.write_text(
        "#!/bin/sh\n"
        + (
            "echo changed >> gate_input.txt\nexit 0\n"
            if mutate
            else "echo deliberate-test-failure\nexit 7\n"
        )
    )
    env = dict(
        os.environ,
        LOOP_ENABLE_AGENT="1",
        LOOP_DRY_RUN="0",
        LOOP_WORKER="codex",
        LOOP_JUDGE="claude",
        LOOP_MAX_LAPS="1",
        LOOP_PATH=str(fakebin) + ":" + os.environ["PATH"],
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
    evidence = (project / "logs/full-test-latest.result").read_text()
    assert f"validation={expected}" in evidence
    assert ("exit=65" if mutate else "exit=7") in evidence
    assert "FULL TEST FAILED" in result.stdout
