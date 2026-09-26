#!/usr/bin/env python3
"""Safe environment probes plus isolated original-game runtime smoke tools.

The probe functions are side-effect free.  The explicit ``prepare`` and
``smoke`` commands are the only functions that create a private copy/prefix
or launch a game; they never patch binaries, start loop services, or start a
model session.
"""

from __future__ import annotations

import ctypes.util
from dataclasses import dataclass
import datetime as _datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import time
import argparse
import fcntl
from typing import Any, Callable, Mapping, Sequence


REQUIRED_TOOLS: tuple[str, ...] = (
    "wine",
    "wineboot",
    "Xvfb",
    "scrot",
    "xwininfo",
    "xdotool",
    "wineserver",
    "i686-w64-mingw32-gcc",
    "make",
)
REQUIRED_LIBRARIES: tuple[str, ...] = ("X11", "Xtst")
MODEL_CLIS: tuple[str, ...] = ("codex", "claude")
DEFAULT_MANIFEST = Path("local/runtime_manifest.json")
ManifestValidator = Callable[[Mapping[str, Any]], object]
Which = Callable[[str], str | None]
FindLibrary = Callable[[str], str | None]
Runner = Callable[..., subprocess.CompletedProcess[str]]


@dataclass(frozen=True)
class ToolStatus:
    name: str
    path: str | None

    @property
    def present(self) -> bool:
        return self.path is not None


@dataclass(frozen=True)
class LibraryStatus:
    name: str
    path: str | None

    @property
    def present(self) -> bool:
        return self.path is not None


def probe_tools(which: Which = shutil.which) -> dict[str, ToolStatus]:
    """Locate every runtime executable without invoking any executable."""

    return {name: ToolStatus(name, which(name)) for name in REQUIRED_TOOLS}


def probe_libraries(find_library: FindLibrary = ctypes.util.find_library) -> dict[str, LibraryStatus]:
    """Locate the X11 libraries needed by the input helpers."""

    return {name: LibraryStatus(name, find_library(name)) for name in REQUIRED_LIBRARIES}


def _version_environment(path: str) -> dict[str, str]:
    """Provide only a minimal environment to a model CLI version probe.

    In particular, API keys, session identifiers, proxy settings, and model
    configuration are not inherited by the subprocess.
    """

    executable_dir = str(Path(path).parent)
    inherited_path = os.environ.get("PATH", "")
    return {
        "PATH": executable_dir + os.pathsep + inherited_path,
        "LANG": "C",
        "LC_ALL": "C",
    }


def _version_line(result: subprocess.CompletedProcess[str]) -> str | None:
    output = (result.stdout or "").splitlines() + (result.stderr or "").splitlines()
    for line in output:
        line = line.strip()
        if line:
            # Keep diagnostics bounded and avoid accidentally echoing a CLI log.
            return line[:200]
    return None


def probe_model_clis(
    which: Which = shutil.which,
    runner: Runner = subprocess.run,
) -> dict[str, dict[str, object]]:
    """Report model CLI presence and ``--version`` output only.

    A successful version probe is not evidence that a model is installed,
    authenticated, reachable, or usable.  The subprocess receives no API or
    session environment and never receives a prompt.
    """

    report: dict[str, dict[str, object]] = {}
    for name in MODEL_CLIS:
        path = which(name)
        if path is None:
            report[name] = {"present": False, "path": None, "version": None}
            continue
        try:
            result = runner(
                [path, "--version"],
                capture_output=True,
                text=True,
                check=False,
                timeout=5,
                env=_version_environment(path),
            )
            report[name] = {
                "present": True,
                "path": path,
                "version": _version_line(result),
                "version_exit": result.returncode,
            }
        except (OSError, subprocess.SubprocessError) as exc:
            report[name] = {
                "present": True,
                "path": path,
                "version": None,
                "version_error": type(exc).__name__,
            }
    return report


# ---------------------------------------------------------------------------
# Explicit setup/smoke lane.  Keep this separate from the read-only probes
# above: callers must opt in to any process or filesystem side effects.

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = (REPO_ROOT.parent / "Syw2plus_re" / "Syw2plus").resolve()
DEFAULT_RUNTIME_ROOT = REPO_ROOT / "local" / "runtime"
SCREENSHOT_ROOT = Path("/home/dev_00/sharedfolder/260320_Syw2plus/temp")
ORIGINAL_EXE = "syw2plus_original.exe"
ORIGINAL_SHA256 = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"
ORIGINAL_EXE_SIZE = 1_032_192
WIN32_CLOSE_HELPER_ENV = "SYW2_WIN32_CLOSE_HELPER"
G1_SETUP_POINTS: dict[str, tuple[int, int]] = {
    "multiplayer_mode": (344, 169),
    "solo_mode": (462, 169),
    "connection_confirm": (608, 564),
    "lobby_start": (608, 564),
}
# This content point is outside the two mode controls and is used for selector
# captures so cursor/hover pixels cannot masquerade as a selection.
G1_NEUTRAL_POINT: tuple[int, int] = (760, 40)
G1_SELECTOR_STATE_ADDRESSES: dict[str, int] = {
    "multiplayer": 0x0106A6A4,
    "solo": 0x0106A86C,
}
G1_COMMITTED_MODE_ADDRESS = 0x004ED848
G1_LOCAL_PLAYER_INDEX_ADDRESS = 0x00B63FC4
G1_READY_STATE_BASE_ADDRESS = 0x00632CF0
G1_LOCAL_PLAYER_RANGE = range(8)
G1_SELECTION_COUNT_ADDRESS = 0x00899024
G1_SELECTION_FIRST_SLOT_ADDRESS = 0x00899028
G1_UNIT_EXISTS_BASE_ADDRESS = 0x008990C8
G1_UNIT_BASE_ADDRESS = 0x0066B790
G1_UNIT_STRIDE = 0x758
G1_UNIT_TYPE_OFFSET = 0x8D
G1_UNIT_INTERNAL_ID_OFFSET = 0x29C
G1_UNIT_X_OFFSET = 0x2A2
G1_UNIT_Y_OFFSET = 0x2A4
G1_SELECTED_UNIT_COMMAND_STATE_OFFSET = 0x94
G1_UNIT_SLOT_RANGE = range(1200)
G1_UNIT_TYPE_TABLE_BASE_ADDRESS = 0x0066BE88
G1_COMMAND_BRANCH_TYPE_FLAGS_BASE_ADDRESS = 0x009B524C
G1_COMMAND_BRANCH_TYPE_FLAGS_STRIDE = 0x394
G1_COMMAND_BRANCH_REQUIRED_MASK = 0x08
G1_COMMAND_BRANCH_CALL_ADDRESS = 0x0049B6D0
G1_COMMAND_CELL_POOL_BASE_ADDRESS = 0x00B38A38
G1_COMMAND_CELL_POOL_FIRST_SLOT = 1
G1_COMMAND_CELL_POOL_STRIDE = 0x124
G1_COMMAND_CELL_POOL_ALLOCATOR_START = 0x00B38B5C
G1_COMMAND_CELL_POOL_ALLOCATOR_END = 0x00B3AC70
G1_COMMAND_CELL_POOL_COUNT = (
    G1_COMMAND_CELL_POOL_ALLOCATOR_END - G1_COMMAND_CELL_POOL_ALLOCATOR_START
) // G1_COMMAND_CELL_POOL_STRIDE
G1_COMMAND_CELL_POOL_SLOTS = range(
    G1_COMMAND_CELL_POOL_FIRST_SLOT,
    G1_COMMAND_CELL_POOL_FIRST_SLOT + G1_COMMAND_CELL_POOL_COUNT,
)
G1_COMMAND_CELL_POOL_READ_SIZE = (
    G1_COMMAND_CELL_POOL_ALLOCATOR_END - G1_COMMAND_CELL_POOL_ALLOCATOR_START
)
G1_COMMAND_CELL_READ_SIZE = 0x5C
G1_COMMAND_CELL_TARGET = (670, 490)
G1_COMMAND_CELL_GROUPS = (2, 3, 4, 5)
G1_COMMAND_CELL_DIAGNOSTIC_ATTEMPTS = 16
G1_COMMAND_CELL_ACTIVE_OFFSET = 0x00
G1_COMMAND_CELL_GROUP_OFFSET = 0x04
G1_COMMAND_CELL_X_OFFSET = 0x08
G1_COMMAND_CELL_Y_OFFSET = 0x0C
G1_COMMAND_CELL_WIDTH_OFFSET = 0x10
G1_COMMAND_CELL_HEIGHT_OFFSET = 0x14
G1_COMMAND_CELL_CATEGORY_OFFSET = 0x4C
G1_COMMAND_CELL_FLAG_OFFSET = 0x50
G1_COMMAND_CELL_CLICK_CALLBACK_OFFSET = 0x54
G1_COMMAND_CELL_HIT_CALLBACK_OFFSET = 0x58
G1_COMMAND_CELL_CLICK_CALLBACK = 0x0049B530
G1_COMMAND_CELL_HIT_CALLBACK = 0x0049B640
G1_ALTERNATE_UI_COUNT_OFFSET = 0x6BE
G1_ALTERNATE_UI_RECORDS_OFFSET = 0x6C2
G1_ALTERNATE_UI_RECORD_COUNT = 10
G1_ALTERNATE_UI_RECORD_STRIDE = 4
G1_ALTERNATE_UI_FLAGS_BASE_ADDRESS = 0x00893118
G1_ALTERNATE_UI_FLAG_STRIDE = 2
G1_ALTERNATE_UI_GEOMETRY_BASE_ADDRESS = 0x009E2BA4
G1_ALTERNATE_UI_GEOMETRY_FIELD_NAMES = ("base_x", "base_y", "x_pitch", "height")
G1_PRIMARY_COMMAND_TABLE_BASE_ADDRESS = 0x008930A6
G1_PRIMARY_COMMAND_TABLE_READ_SIZE = 0x60
G1_PRIMARY_COMMAND_TABLE_WORD_COUNT = 12
G1_PRIMARY_COMMAND_TABLE_BLOCKS: tuple[tuple[str, int], ...] = (
    ("A6", 0x00),
    ("BE", 0x18),
    ("D6", 0x30),
    ("EE", 0x48),
)
# These map dimensions are read-only offsets already documented by the
# population runtime bridge; they are used here only for G1 scene matching.
G1_MAP_WIDTH_ADDRESS = 0x00B3DE34
G1_MAP_HEIGHT_ADDRESS = 0x00B3DE36

# R1 is deliberately isolated from the production G1 input/evidence path.
# These addresses are the statically verified original-program fields from
# docs/work/active/G1_R1_MIDDLE_ENVELOPE_LAP326.md.
G1_R1_WAIT_PS_STATES: tuple[int, int] = (9, 35)
G1_R1_PROGRAM_STATE_ADDRESS = 0x004ED818
G1_R1_PENDING_STATE_ADDRESS = 0x00B92CC0
G1_R1_ORIGIN_ADDRESS = 0x01088B5C
G1_R1_ORIGIN_READ_SIZE = 6
G1_R1_CLICK_POINT: tuple[int, int] = (296, 505)
G1_R1_PS9_STAGE_BUDGET = 40.0
G1_R1_PS35_STAGE_BUDGET = 20.0
# S1 reuses the already bounded PS35-stage budget; it does not create a new
# runtime budget or extend the enclosing run deadline.
G1_S1_PS3_WAIT_SECONDS = G1_R1_PS35_STAGE_BUDGET
G1_S1_TOTAL_DEADLINE = 150.0
G1_S1_CLEANUP_RESERVE = 10.0
G1_S1_STAGE_BUDGETS: dict[str, float] = {
    "prepare": 60.0,
    "launch_to_ps9": 40.0,
    "input_to_ps35": 20.0,
    "direct_pre": 2.0,
    "load_trigger": 5.0,
    "ps3_wait": 10.0,
    "post_finalize": 3.0,
    "cleanup": 10.0,
}


class RuntimeSafetyError(RuntimeError):
    """Input crossed an environment boundary; fail closed."""


class _G1WaitTimeout(RuntimeSafetyError):
    """A G1 input wait ended without a predicate result."""

    def __init__(
        self, message: str, *, classification: str, last: Mapping[str, Any] | None,
        finished_elapsed: float, remaining_budget_after: float,
        observation: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(f"{classification}: {message}")
        self.classification = classification
        self.last = dict(last) if isinstance(last, Mapping) else last
        self.finished_elapsed = finished_elapsed
        self.remaining_budget_after = remaining_budget_after
        self.predicate_observed = False
        self.observation = dict(observation) if observation is not None else {}


class _G1R1CollectionError(RuntimeSafetyError):
    """A bounded R1 origin sample could not be collected."""

    def __init__(self, *, site: str, original_error: str,
                 diagnostics: Mapping[str, Any]) -> None:
        super().__init__(f"R1 {site} origin read failed: {original_error}")
        self.site = site
        self.original_error = original_error
        self.diagnostics = dict(diagnostics)


class _G1R1CandidatePreconditionError(RuntimeSafetyError):
    """A candidate-only gate failed before the single permitted click."""

    def __init__(self, reason: str, *, details: Mapping[str, Any] | None = None) -> None:
        super().__init__(reason)
        self.reason = reason
        self.details = dict(details) if details is not None else {}


class _CommandCellSnapshotError(RuntimeSafetyError):
    """One command-cell snapshot was incomplete or internally inconsistent."""

    def __init__(
        self,
        message: str,
        raw_summary: list[dict[str, Any]],
        branch_evidence: Mapping[str, Any] | None = None,
        alternate_snapshot: Mapping[str, Any] | None = None,
        primary_snapshot: Mapping[str, Any] | None = None,
        retryable: bool = True,
    ) -> None:
        super().__init__(message)
        self.raw_summary = raw_summary
        self.branch_evidence = dict(branch_evidence) if branch_evidence is not None else None
        self.alternate_snapshot = (
            dict(alternate_snapshot) if alternate_snapshot is not None else None
        )
        self.primary_snapshot = (
            dict(primary_snapshot) if primary_snapshot is not None else None
        )
        self.retryable = retryable
        self.command_cell_diagnostics: list[dict[str, Any]] | None = None


def _real(path: Path) -> Path:
    return path.expanduser().resolve(strict=False)


def _reject_path_links(path: Path) -> None:
    current = Path(os.path.abspath(os.path.expanduser(str(path))))
    for part in current.parents:
        if part.is_symlink():
            raise RuntimeSafetyError(f"symlink path component refused: {part}")
    if current.is_symlink():
        raise RuntimeSafetyError(f"symlink path refused: {current}")


def _under(path: Path, parent: Path) -> bool:
    try:
        _real(path).relative_to(_real(parent))
    except ValueError:
        return False
    return True


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    tmp.replace(path)


def _protected_roots() -> tuple[Path, ...]:
    return tuple(_real(p) for p in (REPO_ROOT / "Syw2plus", REPO_ROOT.parent / "Syw2plus"))


def validate_original_source(source: Path) -> tuple[Path, Path]:
    """Validate a real, complete source and the exact original executable."""
    _reject_path_links(source)
    source = source.expanduser()
    source = _real(source)
    if source.is_symlink() or not source.is_dir():
        raise RuntimeSafetyError(f"unsafe source directory: {source}")
    if any(source == root or root in source.parents for root in _protected_roots()):
        raise RuntimeSafetyError(f"unsafe/protected source directory: {source}")
    exe = source / ORIGINAL_EXE
    if exe.is_symlink() or not exe.is_file():
        raise RuntimeSafetyError(f"missing or linked original executable: {exe}")
    digest = _sha256(exe)
    if digest != ORIGINAL_SHA256:
        raise RuntimeSafetyError(f"original SHA-256 mismatch: {digest}")
    return source, exe


def _reject_links(root: Path) -> None:
    for base, dirs, files in os.walk(root, followlinks=False):
        for name in (*dirs, *files):
            item = Path(base) / name
            if item.is_symlink():
                raise RuntimeSafetyError(f"symlink input/output refused: {item}")


def _assert_private_copy(source: Path, copy: Path) -> None:
    _reject_links(copy)
    for base, dirs, files in os.walk(copy, followlinks=False):
        for name in (*dirs, *files):
            item = Path(base) / name
            source_item = source / item.relative_to(copy)
            if source_item.exists() and (item.stat().st_dev, item.stat().st_ino) == (source_item.stat().st_dev, source_item.stat().st_ino):
                raise RuntimeSafetyError(f"hardlinked input detected: {item}")


def _new_run(runtime_root: Path) -> Path:
    runtime_root = _real(runtime_root)
    if not _under(runtime_root, REPO_ROOT / "local" / "runtime"):
        raise RuntimeSafetyError("runtime output must remain under local/runtime")
    runtime_root.mkdir(parents=True, exist_ok=True)
    stamp = _datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    for suffix in range(100):
        run = runtime_root / f"{stamp}_{os.getpid()}_{suffix}"
        try:
            run.mkdir()
            return run
        except FileExistsError:
            continue
    raise RuntimeSafetyError("unable to allocate a dedicated runtime output")


def _run(
    argv: list[str], *, env: Mapping[str, str], timeout: float, log: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    if timeout <= 0:
        raise RuntimeSafetyError("timeout must be positive")
    handle: Any = log.open("a", encoding="utf-8") if log is not None else subprocess.PIPE
    try:
        result = subprocess.run(
            argv, env=dict(env), stdout=handle, stderr=subprocess.STDOUT,
            text=True, timeout=timeout, check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeSafetyError(f"timeout running {' '.join(argv)}") from exc
    finally:
        if log is not None:
            handle.close()
    if result.returncode:
        raise RuntimeSafetyError(f"command failed ({result.returncode}): {' '.join(argv)}")
    return result


def _move_pointer_exact(
    env: Mapping[str, str], target: tuple[int, int], *, timeout: float,
    log: Any | None = None, poll_interval: float = 0.05,
) -> dict[str, Any]:
    """Move the pointer and prove its root coordinates on a private display."""
    if timeout <= 0:
        raise RuntimeSafetyError("pointer verification timeout must be positive")
    if poll_interval <= 0:
        raise RuntimeSafetyError("pointer verification poll interval must be positive")
    target_x, target_y = target
    if target_x < 0 or target_y < 0:
        raise RuntimeSafetyError(f"pointer target must be non-negative: {target}")

    requested = [target_x, target_y]
    move_argv = ["xdotool", "mousemove", str(target_x), str(target_y)]
    deadline = time.monotonic() + timeout
    before: tuple[int, int] | None = None
    last_observed: tuple[int, int] | None = None
    query_result: dict[str, Any] | None = None
    move_result: dict[str, Any] | None = None

    def diagnostic_error(reason: str) -> RuntimeSafetyError:
        return RuntimeSafetyError(
            f"{reason}; requested={requested}; before={list(before) if before is not None else None}; "
            f"last_observed={list(last_observed) if last_observed is not None else None}; "
            f"query={query_result}; command={move_result}"
        )

    def query_position() -> tuple[int, int]:
        nonlocal query_result
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise diagnostic_error("pointer position query deadline exceeded")
        argv = ["xdotool", "getmouselocation", "--shell"]
        try:
            result = subprocess.run(
                argv, env=dict(env), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, timeout=min(2, remaining), check=False,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            query_result = {"argv": argv, "returncode": None, "error": type(exc).__name__}
            raise diagnostic_error("pointer position query failed") from exc
        query_result = {"argv": argv, "returncode": result.returncode}
        if result.returncode:
            raise diagnostic_error(f"pointer position query failed ({result.returncode})")
        values: dict[str, int] = {}
        for line in (result.stdout or "").splitlines():
            key, separator, value = line.partition("=")
            if separator and key in {"X", "Y"}:
                try:
                    values[key] = int(value.strip(), 10)
                except ValueError as exc:
                    raise diagnostic_error("pointer position query was malformed") from exc
        if "X" not in values or "Y" not in values:
            raise diagnostic_error("pointer position query was malformed")
        return values["X"], values["Y"]

    before = query_position()
    last_observed = before
    if before == target:
        return {
            "requested_root": requested,
            "before_root": list(before),
            "last_observed_root": list(last_observed),
            "move": {"argv": move_argv, "attempted": False,
                     "reason": "already_at_target", "returncode": None},
            "verified": True,
        }

    try:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise diagnostic_error("pointer move deadline exceeded")
        result = subprocess.run(
            move_argv, env=dict(env),
            stdout=log if log is not None else subprocess.PIPE,
            stderr=log if log is not None else subprocess.PIPE,
            text=True, timeout=min(2, remaining), check=False,
        )
        move_result = {"argv": move_argv, "attempted": True, "returncode": result.returncode}
    except (OSError, subprocess.SubprocessError) as exc:
        move_result = {"argv": move_argv, "attempted": True,
                       "returncode": None, "error": type(exc).__name__}
        raise diagnostic_error("pointer move failed") from exc
    if move_result["returncode"]:
        raise diagnostic_error(f"pointer move failed ({move_result['returncode']})")

    polls = 0
    while time.monotonic() < deadline:
        last_observed = query_position()
        polls += 1
        if last_observed == target:
            move_result["polls"] = polls
            return {
                "requested_root": requested,
                "before_root": list(before),
                "last_observed_root": list(last_observed),
                "move": move_result,
                "verified": True,
            }
        remaining = deadline - time.monotonic()
        if remaining > 0:
            time.sleep(min(poll_interval, remaining))

    raise diagnostic_error("pointer did not reach requested root coordinate")


def prepare(
    source: Path = DEFAULT_SOURCE, *, runtime_root: Path = DEFAULT_RUNTIME_ROOT,
    bridge: Path | None = None, timeout: float = 60,
) -> dict[str, object]:
    """Copy the complete source and create a newly-owned 32-bit Wine prefix."""
    source, source_exe = validate_original_source(source)
    runtime_root_real = _real(runtime_root)
    if _under(source, runtime_root_real) or _under(runtime_root_real, source):
        raise RuntimeSafetyError("source and runtime output must not contain one another")
    _reject_links(source)
    run = _new_run(runtime_root_real)
    game = run / "game"
    prefix = run / "prefix"
    evidence = run / "output"
    evidence.mkdir()
    try:
        shutil.copytree(source, game, symlinks=False)
        _assert_private_copy(source, game)
        copied_exe = game / ORIGINAL_EXE
        if _sha256(copied_exe) != ORIGINAL_SHA256:
            raise RuntimeSafetyError("private original executable failed post-copy hash")
        support = {
            name: _sha256(game / name)
            for name in ("_inmm.dll", "_inmm_orig.dll", "dxwrapper.dll", "ddraw.dll", "syw2x.dll")
            if (game / name).is_file()
        }
        instrumented = bridge is not None
        bridge_hash: str | None = None
        if bridge is not None:
            _reject_path_links(bridge)
            bridge = bridge.expanduser()
            if bridge.is_symlink() or not bridge.is_file():
                raise RuntimeSafetyError(f"unsafe diagnostic bridge: {bridge}")
            bridge = _real(bridge)
            bridge_hash = _sha256(bridge)
            shutil.copy2(bridge, game / "_inmm.dll")
            support["_inmm.dll"] = _sha256(game / "_inmm.dll")
        prefix.mkdir()
        owner = {"run_dir": str(run), "prefix": str(prefix), "owner": "runtime_env.prepare"}
        _write_json(prefix / ".syw2plus-runtime-owner.json", owner)
        env = dict(os.environ, WINEPREFIX=str(prefix), WINEARCH="win32", WINEDEBUG="-all",
                   LANG="ko_KR.UTF-8", LC_ALL="ko_KR.UTF-8", WINEDLLOVERRIDES="ddraw=b")
        prep_log_path = evidence / "prepare.log"
        prep_log = prep_log_path.open("a", encoding="utf-8")
        prep_xvfb: subprocess.Popen[Any] | None = None
        prep_setup_ok = False
        try:
            # Even wineboot/reg import run on a new private display.  This
            # prevents inherited desktop/session state from entering the new prefix.
            prep_xvfb, prep_display = _xvfb(prep_log)
            env["DISPLAY"] = prep_display
            _run(["wineboot", "-u"], env=env, timeout=timeout, log=prep_log_path)
            registry_imported = False
            private_reg = game / "_inmm.reg"
            if private_reg.is_file():
                _run(["wine", "reg", "import", str(private_reg)], env=env, timeout=timeout,
                     log=prep_log_path)
                registry_imported = True
            _run(["wineserver", "-k"], env=env, timeout=timeout, log=prep_log_path)
            _run(["wineserver", "-w"], env=env, timeout=timeout, log=prep_log_path)
            if _prefix_pids(prefix):
                raise RuntimeSafetyError("new Wine prefix still has processes after setup cleanup")
            prep_setup_ok = True
        finally:
            # On a wineboot/reg-import failure, still clean only this newly
            # owned prefix before removing the failed run directory.
            if not prep_setup_ok:
                try:
                    _run(["wineserver", "-k"], env=env, timeout=10, log=prep_log_path)
                    _run(["wineserver", "-w"], env=env, timeout=10, log=prep_log_path)
                except (RuntimeSafetyError, UnboundLocalError):
                    pass
            if prep_xvfb is not None and prep_xvfb.poll() is None:
                prep_xvfb.terminate()
                try:
                    prep_xvfb.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    prep_xvfb.kill()
            prep_log.close()
        manifest = {
            "manifest_version": 1,
            "run_id": run.name,
            "source": {"root": str(source), "exe": ORIGINAL_EXE, "exe_sha256": _sha256(source_exe),
                       "read_only_policy": "agent-read-only; OS write protection not asserted",
                       "copy_mode": "copytree; symlinks/hardlinks rejected"},
            "game": {"root": str(game), "exe": str(copied_exe), "exe_sha256": _sha256(copied_exe),
                     "support_dll_sha256": support, "support_modules_present": sorted(support),
                     "diagnostic_bridge_overridden": instrumented,
                     "diagnostic_bridge_sha256": bridge_hash},
            "wine": {"prefix": str(prefix), "arch": "win32", "created_new": True, "private": True},
            "output": {"run_dir": str(run), "evidence_dir": str(evidence)},
            "runtime_config": {"screen": "1024x768x24", "private_display": True,
                               "input": "one XTest title random-game click (184,560)", "timeouts_max_seconds": 90,
                               "locale": "ko_KR.UTF-8", "wine_dll_overrides": "ddraw=b",
                               "private_inmm_registry_imported": registry_imported,
                               "loops_or_services_started": False,
                               "feature_patch_execution_observed": "unknown (startup smoke only)"},
        }
        _write_json(run / "manifest.json", manifest)
        return manifest
    except Exception as exc:
        # Preserve logs and provenance for diagnosis; never erase a failed
        # runtime that may still have a Wine process attached.
        try:
            _write_json(run / "output" / "prepare_failure.json", {"error": repr(exc), "run_dir": str(run)})
        except OSError:
            pass
        raise


def _manifest(path: Path) -> tuple[dict[str, object], Path, Path, Path]:
    path = _real(path)
    try:
        data = json.loads(path.read_text())
        game = _real(Path(data["game"]["root"]))  # type: ignore[index]
        prefix = _real(Path(data["wine"]["prefix"]))  # type: ignore[index]
        run = _real(Path(data["output"]["run_dir"]))  # type: ignore[index]
        output = _real(Path(data["output"]["evidence_dir"]))  # type: ignore[index]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise RuntimeSafetyError(f"invalid runtime manifest: {path}") from exc
    if path != run / "manifest.json":
        raise RuntimeSafetyError("manifest is not in its dedicated run directory")
    canonical_root = _real(REPO_ROOT / "local" / "runtime")
    if not _under(run, canonical_root) or game != run / "game" or prefix != run / "prefix" or output != run / "output":
        raise RuntimeSafetyError("manifest components are outside its dedicated private run")
    return data, game, prefix, output


def check_runtime(path: Path) -> dict[str, object]:
    path = _real(path)
    data, game, prefix, output = _manifest(path)
    game_data = data.get("game")
    if not isinstance(game_data, dict):
        raise RuntimeSafetyError("manifest game section is invalid")
    exe = game / ORIGINAL_EXE
    expected = game_data.get("exe_sha256")
    if not game.is_dir() or game.is_symlink() or not exe.is_file() or exe.is_symlink():
        raise RuntimeSafetyError("private game copy is missing/linked")
    if expected != ORIGINAL_SHA256 or _sha256(exe) != ORIGINAL_SHA256:
        raise RuntimeSafetyError("runtime executable is not the verified original")
    recorded_support = game_data.get("support_dll_sha256")
    if not isinstance(recorded_support, dict):
        raise RuntimeSafetyError("manifest support module hashes are missing")
    for name, expected_hash in recorded_support.items():
        module = game / str(name)
        if not module.is_file() or module.is_symlink() or _sha256(module) != expected_hash:
            raise RuntimeSafetyError(f"support module hash changed: {name}")
    raw_source = Path(data["source"]["root"])  # type: ignore[index]
    if raw_source.is_symlink():
        raise RuntimeSafetyError("manifest source is a symlink")
    source, _ = validate_original_source(raw_source)
    if source == game:
        raise RuntimeSafetyError("source and private game copy are identical")
    _assert_private_copy(source, game)
    marker = prefix / ".syw2plus-runtime-owner.json"
    if not prefix.is_dir() or prefix.is_symlink() or not marker.is_file():
        raise RuntimeSafetyError("Wine prefix is missing or foreign")
    owner = json.loads(marker.read_text())
    if owner.get("run_dir") != str(path.parent) or owner.get("prefix") != str(prefix):
        raise RuntimeSafetyError("Wine prefix ownership marker mismatch")
    return {"ok": True, "manifest": str(path), "game_root": str(game), "prefix": str(prefix),
            "output": str(output), "exe_sha256": ORIGINAL_SHA256,
            "diagnostic_bridge_overridden": bool(game_data.get("diagnostic_bridge_overridden", False))}


def _display_busy(number: int) -> bool:
    return Path(f"/tmp/.X{number}-lock").exists() or Path(f"/tmp/.X11-unix/X{number}").exists()


def _xvfb(log: Any, screen: str = "1024x768x24") -> tuple[subprocess.Popen[Any], str]:
    if not re.fullmatch(r"\d{3,4}x\d{3,4}x(?:24|32)", screen):
        raise RuntimeSafetyError(f"invalid Xvfb screen: {screen}")
    for number in range(90, 200):
        if _display_busy(number):
            continue
        display = f":{number}"
        proc = subprocess.Popen(["Xvfb", display, "-nolisten", "tcp", "-screen", "0", screen], stdout=log, stderr=log)
        time.sleep(0.25)
        if proc.poll() is None:
            return proc, display
        proc.wait()
    raise RuntimeSafetyError("no unused private Xvfb display in :90..:199")


def _proc(pid: int) -> dict[str, object]:
    result: dict[str, object] = {"pid": pid, "alive": Path(f"/proc/{pid}").exists()}
    try:
        for line in Path(f"/proc/{pid}/status").read_text(errors="replace").splitlines():
            key, _, value = line.partition(":")
            if key in {"State", "VmRSS", "VmSize", "Threads"}:
                result[key] = value.strip()
        result["cmdline"] = Path(f"/proc/{pid}/cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace").strip()
    except OSError as exc:
        result["read_error"] = str(exc)
    return result


def _owned_runtime_process_pids(root_pid: int, proc_root: Path = Path("/proc")) -> list[int]:
    """Return only the process tree rooted at the owned launcher PID."""
    pending = [root_pid]
    seen: set[int] = set()
    while pending:
        pid = pending.pop(0)
        if pid in seen:
            continue
        seen.add(pid)
        children_path = proc_root / str(pid) / "task" / str(pid) / "children"
        try:
            children = [int(value) for value in children_path.read_text().split()]
        except (OSError, ValueError):
            children = []
        pending.extend(child for child in children if child not in seen)
    return sorted(seen)


def _linux_stat_record(stat_path: Path, identity: int, identity_key: str) -> dict[str, object]:
    """Read the bounded liveness fields from one Linux ``/proc`` stat record."""
    raw = stat_path.read_text()
    closing_paren = raw.rfind(")")
    if closing_paren < 0:
        raise ValueError(f"malformed {stat_path}")
    fields = raw[closing_paren + 2:].split()
    # The slice begins at field 3 (state): utime/stime are fields 14/15 and
    # num_threads is field 20 in the complete proc stat record.
    if len(fields) <= 17:
        raise ValueError(f"short {stat_path}")
    return {identity_key: identity, "state": fields[0], "utime": int(fields[11]),
            "stime": int(fields[12]), "threads": int(fields[17])}


def _linux_process_stat(pid: int, proc_root: Path = Path("/proc")) -> dict[str, object]:
    return _linux_stat_record(proc_root / str(pid) / "stat", pid, "pid")


def _linux_thread_stats(
    pid: int, proc_root: Path = Path("/proc"), limit: int = 64,
) -> list[dict[str, object]]:
    """Read bounded per-thread CPU/state records for one owned process."""
    task_root = proc_root / str(pid) / "task"
    try:
        task_dirs = sorted(
            (item for item in task_root.iterdir() if item.is_dir() and item.name.isdigit()),
            key=lambda item: int(item.name),
        )[:limit]
    except OSError:
        return []

    details: list[dict[str, object]] = []
    for task_dir in task_dirs:
        tid = int(task_dir.name)
        try:
            details.append(_linux_stat_record(task_dir / "stat", tid, "tid"))
        except (OSError, ValueError) as exc:
            details.append({"tid": tid, "read_error": str(exc)})
    return details


def _owned_runtime_process_snapshot(
    root_pid: int, proc_root: Path = Path("/proc"), thread_limit: int = 64,
) -> list[dict[str, object]]:
    """Capture liveness for the owned launcher and its current descendants."""
    snapshot: list[dict[str, object]] = []
    for pid in _owned_runtime_process_pids(root_pid, proc_root):
        try:
            record = _linux_process_stat(pid, proc_root)
            record["threads_detail"] = _linux_thread_stats(pid, proc_root, thread_limit)
            snapshot.append(record)
        except (OSError, ValueError) as exc:
            snapshot.append({"pid": pid, "alive": False, "read_error": str(exc)})
    return snapshot


def _existing_state(prefix: Path) -> dict[str, object]:
    """Read metadata (never mutate) for state files made by existing tooling."""
    result: dict[str, object] = {}
    for name in ("inmm_state_log.jsonl", "inmm_control_request.json", "inmm_control_result.json"):
        path = prefix / "drive_c" / name
        if not path.exists():
            continue
        try:
            result[name] = {"bytes": path.stat().st_size, "mtime": path.stat().st_mtime}
        except OSError as exc:
            result[name] = {"read_error": str(exc)}
    return result


def _remaining(started: float, limit: float) -> float:
    remaining = limit - (time.monotonic() - started)
    if remaining <= 0:
        raise RuntimeSafetyError("smoke deadline exceeded")
    return remaining


def _normalize_state(state: dict[str, object], process: dict[str, object]) -> dict[str, object]:
    value = dict(state)
    ps = value.get("ps")
    if isinstance(ps, int):
        value["ps"] = ps & 0xFFFF
    rss = process.get("VmRSS")
    if isinstance(rss, str):
        match = re.search(r"(\d+)", rss)
        if match:
            value["rss_bytes"] = int(match.group(1)) * 1024
    return value


def _prefix_pids(prefix: Path) -> list[int]:
    marker = f"WINEPREFIX={prefix}".encode()
    found: list[int] = []
    for item in Path("/proc").iterdir():
        if not item.name.isdigit():
            continue
        try:
            if marker in item.joinpath("environ").read_bytes().split(b"\0"):
                found.append(int(item.name))
        except OSError:
            pass
    return found


def _window_tree(display: str, deadline: float) -> str:
    """Return private X11 window metadata and reject known _inmm error dialogs."""
    result = subprocess.run(["xwininfo", "-root", "-tree"], env=dict(os.environ, DISPLAY=display),
                            capture_output=True, text=True, timeout=min(10, deadline), check=True)
    tree = result.stdout
    lowered = tree.lower()
    if "registry information is invalid" in lowered:
        raise RuntimeSafetyError("original startup stopped at the _inmm registry error dialog")
    windows = [line for line in tree.splitlines() if "0x" in line and "root" not in line.lower()]
    if not windows:
        raise RuntimeSafetyError("original startup produced no X11 game window")
    return tree[-8000:]


def _window_ids(tree: str) -> set[str]:
    return set(re.findall(r"0x[0-9a-fA-F]+", tree))


def _game_window_candidates(tree: str) -> list[tuple[str, int, int]]:
    candidates: list[tuple[str, int, int]] = []
    for line in tree.splitlines():
        match = re.search(r"(0x[0-9a-fA-F]+).*?\b(\d{3,4})x(\d{3,4})\+", line)
        if not match:
            continue
        width, height = int(match.group(2)), int(match.group(3))
        if 700 <= width <= 1000 and 500 <= height <= 700:
            candidates.append((match.group(1), width, height))
    return candidates


def _capture_screenshot(
    display: str, run_id: str, pid: int, tag: str, deadline: float,
    crop: tuple[int, int, int, int] | None = None,
) -> tuple[Path, dict[str, object]]:
    SCREENSHOT_ROOT.mkdir(parents=True, exist_ok=True)
    path = SCREENSHOT_ROOT / f"{_datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{run_id}_{pid}_{tag}_{time.time_ns()}.png"
    argv = ["scrot"]
    if crop is not None:
        argv.extend(["-a", ",".join(str(value) for value in crop)])
    argv.append(str(path))
    subprocess.run(argv, env=dict(os.environ, DISPLAY=display),
                   timeout=min(10, deadline), check=True)
    raw = path.read_bytes()
    dimensions: list[int] | None = None
    if raw[:8] == b"\x89PNG\r\n\x1a\n" and raw[12:16] == b"IHDR":
        dimensions = [int.from_bytes(raw[16:20], "big"), int.from_bytes(raw[20:24], "big")]
    return path, {"path": str(path), "sha256": hashlib.sha256(raw).hexdigest(), "dimensions": dimensions}


def _presentation_trace_install_gate(
    trace_path: Path, install_copy: Path, run_id: str,
) -> dict[str, object]:
    """Copy and validate the bounded install record before any input/capture."""
    install_copy.parent.mkdir(parents=True, exist_ok=True)
    try:
        raw = trace_path.read_bytes()
    except OSError as exc:
        raise RuntimeSafetyError(f"presentation trace install record is missing: {exc}") from exc
    install_copy.write_bytes(raw)
    if len(raw) > 1024 * 1024:
        raise RuntimeSafetyError("presentation trace install record exceeds the 1 MiB gate limit")
    try:
        lines = raw.decode("utf-8").splitlines()
        events = [json.loads(line) for line in lines if line.strip()]
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeSafetyError(f"presentation trace install record is malformed: {exc}") from exc
    if not events or any(not isinstance(item, dict) for item in events):
        raise RuntimeSafetyError("presentation trace install record has no object events")
    if any(item.get("run_id") != run_id for item in events):
        raise RuntimeSafetyError("presentation trace install record has a mismatched run_id")
    if any(item.get("install_status") == "failed" for item in events):
        raise RuntimeSafetyError("presentation trace install failed before first input")
    complete = [item for item in events
                if item.get("event") == "install"
                and item.get("install_status") == "active"
                and item.get("stage") == "complete"]
    if len(complete) != 1:
        raise RuntimeSafetyError("presentation trace has no unique active complete install before first input")
    return {"status": "PASS", "event_count": len(events), "stage": "complete",
            "install_trace": str(install_copy),
            "install_trace_sha256": hashlib.sha256(raw).hexdigest()}


def _trace_finalization_state(trace_path: Path, run_id: str) -> dict[str, object]:
    """Report whether the bridge has emitted one final summary for this run."""
    try:
        raw = trace_path.read_bytes()
    except FileNotFoundError:
        return {"ready": False, "reason": "trace missing", "summary_count": 0}
    except OSError as exc:
        return {"ready": False, "reason": f"trace read failed: {exc}", "summary_count": 0}
    try:
        events = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return {"ready": False, "reason": f"trace malformed: {exc}", "summary_count": 0}
    if not events or any(not isinstance(item, dict) for item in events):
        return {"ready": False, "reason": "trace has no object events", "summary_count": 0}
    if any(item.get("run_id") != run_id for item in events):
        return {"ready": False, "reason": "trace has a mismatched run_id", "summary_count": 0}
    summaries = [item for item in events if item.get("event") == "summary"]
    if len(summaries) != 1:
        return {"ready": False, "reason": f"expected one summary, observed {len(summaries)}",
                "summary_count": len(summaries), "event_count": len(events)}
    if events[-1].get("event") != "summary":
        return {"ready": False, "reason": "summary is not the final trace event",
                "summary_count": 1, "event_count": len(events)}
    return {"ready": True, "reason": "one final summary observed", "summary_count": 1,
            "event_count": len(events), "summary": summaries[0]}


def _read_owned_win32_pid(trace_path: Path, run_id: str) -> dict[str, Any]:
    """Read the single Win32 PID recorded by the diagnostic trace."""
    from tools.win32_close_transport import Win32CloseError, read_owned_win32_pid

    try:
        return read_owned_win32_pid(trace_path, run_id)
    except Win32CloseError as exc:
        raise RuntimeSafetyError(str(exc)) from exc


def _request_owned_game_close(
    display: str, win32_pid: int, close_helper: Path, env: Mapping[str, str],
    deadline: float, log: Any,
) -> dict[str, Any]:
    """Post WM_CLOSE through the PE32 helper after exact Win32 ownership checks."""
    from tools.win32_close_transport import Win32CloseError, request_owned_win32_close

    try:
        return request_owned_win32_close(
            close_helper, win32_pid, dict(env, DISPLAY=display), deadline, log,
        )
    except Win32CloseError as exc:
        detail = f"; evidence={exc.evidence}" if exc.evidence else ""
        raise RuntimeSafetyError(f"owned Win32 close transport failed: {exc}{detail}") from exc


def _wait_for_clean_trace_close(
    proc: subprocess.Popen[Any], trace_path: Path, run_id: str,
    started: float, timeout: float, poll_interval: float = 0.05,
    liveness_samples: list[dict[str, object]] | None = None,
    liveness_delay: float = 5.0,
    program_state_reader: Callable[[], object] | None = None,
    finalization_program_state: list[dict[str, object]] | None = None,
    screenshot_capture: Callable[[str], Mapping[str, object]] | None = None,
    finalization_screenshots: list[dict[str, object]] | None = None,
    finalization_started: float | None = None,
    program_state_interval: float = 1.0,
) -> dict[str, object]:
    """Require process exit and the bridge's own final summary before copying a trace."""
    last: dict[str, object] = {"ready": False, "reason": "trace finalization not checked",
                               "summary_count": 0}
    observation_started = (time.monotonic() if finalization_started is None
                           else finalization_started)
    next_program_state_at = observation_started
    if program_state_reader is not None and finalization_program_state is None:
        finalization_program_state = []
    if screenshot_capture is not None and finalization_screenshots is None:
        finalization_screenshots = []
    screenshot_deadlines = (
        (observation_started + 5.0, "close_plus_5s"),
        (started + timeout - 5.0, "timeout_minus_5s"),
    )
    screenshot_index = 0
    if liveness_samples is not None:
        root_pid = getattr(proc, "pid", None)
        liveness_samples.append({
            "sample": 1,
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "processes": (_owned_runtime_process_snapshot(root_pid)
                          if isinstance(root_pid, int) else []),
        })
    second_liveness_at = time.monotonic() + liveness_delay
    while time.monotonic() - started < timeout:
        now = time.monotonic()
        if (program_state_reader is not None and finalization_program_state is not None
                and now >= next_program_state_at
                and len(finalization_program_state) < 120):
            sample: dict[str, object] = {"elapsed_seconds": round(now - started, 3)}
            try:
                state = program_state_reader()
                ps = state.get("ps") if isinstance(state, Mapping) else state
                if not isinstance(ps, int):
                    raise ValueError("program state reader returned no integer ps")
                sample["ps"] = ps
                tick = state.get("tick") if isinstance(state, Mapping) else None
                if isinstance(tick, int):
                    sample["tick"] = tick
                else:
                    sample["tick_error"] = "program state reader returned no integer tick"
            except Exception as exc:  # preserve an observation failure in evidence
                sample["error"] = f"{type(exc).__name__}: {exc}"
            finalization_program_state.append(sample)
            next_program_state_at = now + max(program_state_interval, 0.01)

        while (screenshot_capture is not None
               and finalization_screenshots is not None
               and screenshot_index < len(screenshot_deadlines)
               and now >= screenshot_deadlines[screenshot_index][0]):
            _deadline, tag = screenshot_deadlines[screenshot_index]
            record = dict(screenshot_capture(tag))
            record.setdefault("tag", tag)
            finalization_screenshots.append(record)
            screenshot_index += 1

        if liveness_samples is not None and len(liveness_samples) == 1 \
                and time.monotonic() >= second_liveness_at:
            liveness_samples.append({
                "sample": 2,
                "elapsed_seconds": round(time.monotonic() - started, 3),
                "processes": (_owned_runtime_process_snapshot(root_pid)
                              if isinstance(root_pid, int) else []),
            })
        exited = proc.poll() is not None
        last = _trace_finalization_state(trace_path, run_id)
        if exited and bool(last.get("ready")):
            return {"status": "PASS", "process_exit": proc.returncode, **last}
        if exited:
            raise RuntimeSafetyError(
                f"presentation trace clean finalization blocked: {last.get('reason')}"
            )
        time.sleep(min(poll_interval, max(timeout - (time.monotonic() - started), 0.001)))
    raise RuntimeSafetyError(
        "presentation trace clean finalization timed out; "
        f"process_exited={proc.poll() is not None}; state={last}"
    )


def _finalize_presentation_trace(
    display: str, win32_pid: int, close_helper: Path, env: Mapping[str, str], log: Any,
    proc: subprocess.Popen[Any], trace_path: Path, run_id: str,
    started: float, timeout: float, evidence: dict[str, Any] | None = None,
    program_state_reader: Callable[[], object] | None = None,
    screenshot_capture: Callable[[str], Mapping[str, object]] | None = None,
) -> dict[str, object]:
    """Request owned Win32 close, then wait for process exit and bridge summary."""
    close = _request_owned_game_close(
        display, win32_pid, close_helper, env, _remaining(started, timeout), log,
    )
    finalization: dict[str, object] = {"close_transport": close}
    if evidence is not None:
        evidence["trace_finalization"] = finalization
    liveness_samples: list[dict[str, object]] = []
    finalization_program_state: list[dict[str, object]] = []
    finalization_screenshots: list[dict[str, object]] = []
    if evidence is not None:
        evidence["finalization_program_state"] = finalization_program_state
        evidence["finalization_screenshots"] = finalization_screenshots
    try:
        finalization_started = time.monotonic()
        finalization.update(_wait_for_clean_trace_close(
            proc, trace_path, run_id, started, timeout, liveness_samples=liveness_samples,
            program_state_reader=program_state_reader,
            finalization_program_state=finalization_program_state,
            screenshot_capture=screenshot_capture,
            finalization_screenshots=finalization_screenshots,
            finalization_started=finalization_started,
        ))
    except (OSError, RuntimeSafetyError):
        if evidence is not None:
            evidence["finalization_liveness"] = liveness_samples
            evidence["trace_finalization"] = finalization
        raise
    if evidence is not None:
        evidence["trace_finalization"] = finalization
    return finalization


def _observe_ps3_dwell(
    requested_seconds: float,
    state_reader: Callable[[], Mapping[str, Any]],
    screenshot_capture: Callable[[str], Mapping[str, object]],
    *,
    monotonic: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
) -> dict[str, object] | None:
    """Observe PS3 before close, without injecting game input."""
    if requested_seconds <= 0:
        return None

    started = monotonic()
    samples: list[dict[str, object]] = []
    screenshots: list[dict[str, object]] = []
    capture_offsets = (1.0, 10.0, 20.0, 30.0)
    capture_index = 0
    next_sample = 1.0
    while next_sample <= requested_seconds or (
        capture_index < len(capture_offsets)
        and capture_offsets[capture_index] <= requested_seconds
    ):
        next_capture = (capture_offsets[capture_index]
                        if capture_index < len(capture_offsets) else float("inf"))
        next_event = min(next_sample, next_capture)
        target = started + next_event
        delay = target - monotonic()
        if delay > 0:
            sleep(delay)
        elapsed = round(monotonic() - started, 3)
        if next_sample <= next_event and len(samples) < 60:
            sample: dict[str, object] = {"elapsed_seconds": elapsed}
            try:
                state = state_reader()
                ps = state.get("ps")
                if isinstance(ps, int):
                    sample["ps"] = ps
                else:
                    sample["error"] = "program state reader returned no integer ps"
                tick = state.get("tick")
                if isinstance(tick, int):
                    sample["tick"] = tick
                else:
                    sample["tick_error"] = "program state reader returned no integer tick"
            except Exception as exc:  # preserve observation failures in evidence
                sample["error"] = f"{type(exc).__name__}: {exc}"
            samples.append(sample)
            next_sample += 1.0
        if next_capture <= next_event:
            tag = f"ps3_dwell_plus_{int(next_capture)}s"
            record: dict[str, object] = {"tag": tag}
            try:
                record.update(screenshot_capture(tag))
            except Exception as exc:  # a capture failure must not abort the probe
                record["error"] = f"{type(exc).__name__}: {exc}"
            screenshots.append(record)
            capture_index += 1

    return {"requested_seconds": requested_seconds, "samples": samples,
            "screenshots": screenshots}


def _preserve_raw_presentation_trace(trace_path: Path, raw_copy: Path) -> None:
    """Keep the live trace exact bytes when clean finalization cannot complete."""
    if trace_path.is_file():
        raw_copy.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(trace_path, raw_copy)


def _preserve_dxwrapper_logs(
    game: Path, output_dir: Path, dxwrapper_config: dict[str, Any],
) -> None:
    """Copy private dxwrapper logs into run output and record their hashes."""
    logs_dir = output_dir / "wrapper_logs"
    records: list[dict[str, object]] = []
    for source in sorted(game.glob("dxwrapper-*.log"), key=lambda path: path.name):
        if source.is_symlink() or not source.is_file():
            continue
        destination = logs_dir / source.name
        logs_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        records.append({"source": str(source), "path": str(destination),
                        "sha256": _sha256(destination), "bytes": destination.stat().st_size})
    dxwrapper_config["wrapper_logs"] = records


def _finalize_copy_validate_presentation_trace(
    display: str, win32_pid: int, close_helper: Path, env: Mapping[str, str], log: Any,
    proc: subprocess.Popen[Any], trace_path: Path, raw_copy: Path, trace_copy: Path,
    run_id: str, started: float, timeout: float, capture: Mapping[str, Any],
    evidence: dict[str, Any],
    program_state_reader: Callable[[], object] | None = None,
    screenshot_capture: Callable[[str], Mapping[str, object]] | None = None,
) -> None:
    """Only copy and validate a trace after owned close, exit, and final summary."""
    try:
        evidence["trace_finalization"] = _finalize_presentation_trace(
            display, win32_pid, close_helper, env, log, proc, trace_path,
            run_id, started, timeout, evidence,
            program_state_reader=program_state_reader,
            screenshot_capture=screenshot_capture,
        )
        shutil.copy2(trace_path, trace_copy)
        evidence["trace"] = {"path": str(trace_copy), "sha256": _sha256(trace_copy),
                              "bytes": trace_copy.stat().st_size}
        from tools.check_g1_presentation_trace import validate as validate_trace
        evidence["validator"] = validate_trace(trace_copy, capture=capture)
    except (OSError, RuntimeSafetyError):
        _preserve_raw_presentation_trace(trace_path, raw_copy)
        raise


def _xwininfo_details(display: str, window_id: str, deadline: float) -> dict[str, Any]:
    result = subprocess.run(["xwininfo", "-id", window_id], env=dict(os.environ, DISPLAY=display),
                            capture_output=True, text=True, timeout=min(10, deadline), check=True)
    values: dict[str, object] = {"id": window_id, "raw_sha256": hashlib.sha256(result.stdout.encode()).hexdigest()}
    patterns = {
        "x": r"Absolute upper-left X:\s+(-?\d+)",
        "y": r"Absolute upper-left Y:\s+(-?\d+)",
        "width": r"Width:\s+(\d+)",
        "height": r"Height:\s+(\d+)",
        "border": r"Border width:\s+(\d+)",
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, result.stdout)
        if not match:
            raise RuntimeSafetyError(f"xwininfo missing {key} for {window_id}")
        values[key] = int(match.group(1))
    return values


def _game_window_ids(
    tree: str, *, allowed_sizes: tuple[tuple[int, int], ...] = ((800, 600),)
) -> tuple[str, str | None]:
    """Return the top-level original window and its same-size content child."""
    lines = tree.splitlines()
    outer: str | None = None
    outer_index = -1
    for index, line in enumerate(lines):
        if "syw2plus_original.exe" not in line:
            continue
        match = re.search(r"(0x[0-9a-fA-F]+).*?\b(\d{3,4})x(\d{3,4})\+", line)
        if match and (int(match.group(2)), int(match.group(3))) in allowed_sizes:
            outer, outer_index = match.group(1), index
            break
    if outer is None:
        candidates = _game_window_candidates(tree)
        if not candidates:
            sizes = ", ".join(f"{width}x{height}" for width, height in allowed_sizes)
            raise RuntimeSafetyError(f"no original game window in allowed sizes: {sizes}")
        outer = candidates[0][0]
        outer_index = next((i for i, line in enumerate(lines) if outer in line), -1)
    child: str | None = None
    if outer_index >= 0:
        for line in lines[outer_index + 1:]:
            if len(line) - len(line.lstrip()) <= len(lines[outer_index]) - len(lines[outer_index].lstrip()):
                break
            match = re.search(r"(0x[0-9a-fA-F]+).*?\b(\d{3,4})x(\d{3,4})\+", line)
            if (match and match.group(1) != outer
                    and (int(match.group(2)), int(match.group(3))) in allowed_sizes):
                child = match.group(1)
                break
    return outer, child


def _presentation_logical_surface_contract(trace_path: Path) -> dict[str, Any]:
    """Require the DirectDraw trace to retain the original 800x600 logical surface."""
    try:
        events = [json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines()
                  if line.strip()]
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeSafetyError(f"presentation trace logical-surface evidence is malformed: {exc}") from exc
    if not events or any(not isinstance(event, dict) for event in events):
        raise RuntimeSafetyError("presentation trace logical-surface evidence has no object events")

    modes = [event for event in events if event.get("event") == "set_display_mode"]
    if not modes:
        raise RuntimeSafetyError("presentation trace has no set_display_mode evidence")
    last_mode = modes[-1]
    if [last_mode.get("width"), last_mode.get("height")] != [800, 600]:
        raise RuntimeSafetyError("presentation trace last logical display mode is not 800x600")

    primary_creates = [
        event for event in events
        if event.get("event") == "create_surface"
        and isinstance(event.get("descriptor"), dict)
        and event["descriptor"].get("flags") == 33
        and event["descriptor"].get("backbuffer_count") == 1
    ]
    if not primary_creates:
        raise RuntimeSafetyError("presentation trace primary surface creation evidence is missing")
    primary_create = primary_creates[-1]
    surface = primary_create.get("returned_surface")
    descriptors = [
        event for event in events
        if event.get("event") == "get_surface_desc"
        and event.get("surface") == surface
    ]
    if not descriptors:
        raise RuntimeSafetyError("presentation trace primary surface descriptor evidence is missing")
    primary_descriptor = descriptors[-1].get("actual_desc")
    if not isinstance(primary_descriptor, dict) or [
        primary_descriptor.get("width"), primary_descriptor.get("height")
    ] != [800, 600]:
        raise RuntimeSafetyError("presentation trace primary surface is not 800x600")

    return {
        "status": "PASS",
        "logical_content_size": [800, 600],
        "last_set_display_mode": {
            "seq": last_mode.get("seq"),
            "width": last_mode.get("width"),
            "height": last_mode.get("height"),
            "bpp": last_mode.get("bpp"),
        },
        "primary_surface": {
            "create_seq": primary_create.get("seq"),
            "surface": surface,
            "descriptor_seq": descriptors[-1].get("seq"),
            "actual_desc": primary_descriptor,
        },
    }


def _read_surface(read_memory: Callable[[int, int], bytes], ps: int) -> dict[str, Any]:
    raw = read_memory(0x00E5BF18, 0x18)
    values = struct.unpack("<6I", raw[:24]) if len(raw) >= 24 else ()
    viewport_raw = read_memory(0x00B3AC80, 0x10)
    viewport = struct.unpack("<4i", viewport_raw)
    return {
        "ps": ps,
        "renderer_address": "0x00E5BF18",
        "viewport_address": "0x00B3AC80",
        "raw_hex": raw.hex(),
        "fields": ["mode", "width", "height", "bpp", "stride", "current_height"],
        "values": list(values),
        "viewport": list(viewport),
        "expected_composition": "800x600 surface; viewport bounds are renderer evidence, not output scaling",
    }


def _read_selection(read_memory: Callable[[int, int], bytes]) -> dict[str, object]:
    count = struct.unpack("<i", read_memory(G1_SELECTION_COUNT_ADDRESS, 4))[0]
    first = struct.unpack("<h", read_memory(G1_SELECTION_FIRST_SLOT_ADDRESS, 2))[0]
    return {"address": "0x00899024", "first_address": "0x00899028", "count": count, "first_slot": first}


def _read_g1_selection_evidence(read_memory: Callable[[int, int], bytes]) -> dict[str, Any]:
    """Read selection counts plus best-effort selected slot/type evidence."""

    selection = dict(_read_selection(read_memory))
    count_value = selection.get("count")
    if not isinstance(count_value, int):
        selection.update({
            "selected_slot": None,
            "selected_type": "UNKNOWN",
            "selected_type_provenance": "selection count was not an integer",
        })
        return selection
    count = count_value
    try:
        identity = _read_g1_command_selection_identity(read_memory, selection_count=count)
    except (_CommandCellSnapshotError, OSError, struct.error) as exc:
        selection.update({
            "selected_slot": selection.get("first_slot") if count > 0 else None,
            "selected_type": "UNKNOWN",
            "selected_type_provenance": f"{type(exc).__name__}: {exc}",
        })
        return selection

    identity_selection = identity["selection"]
    identity_unit = identity.get("unit")
    selection["selected_slot"] = (
        identity_selection.get("first_slot") if isinstance(identity_selection, Mapping) else None
    )
    selection["selected_type"] = (
        identity_unit.get("type") if isinstance(identity_unit, Mapping) else "UNKNOWN"
    )
    if selection["selected_type"] == "UNKNOWN":
        selection["selected_type_provenance"] = (
            "no selected unit: selection count is zero"
            if count == 0 else "selected-unit identity did not include a type"
        )
    else:
        selection["selected_type_provenance"] = (
            "approved selected-unit identity: "
            "G1_UNIT_BASE_ADDRESS + slot*G1_UNIT_STRIDE + G1_UNIT_TYPE_OFFSET"
        )
    return selection


def _command_cell_raw_summary(raw_pool: bytes) -> list[dict[str, Any]]:
    """Keep bounded, relevant fields from nonzero pool records."""

    summary: list[dict[str, Any]] = []
    for slot in G1_COMMAND_CELL_POOL_SLOTS:
        offset = (slot - G1_COMMAND_CELL_POOL_FIRST_SLOT) * G1_COMMAND_CELL_POOL_STRIDE
        raw = raw_pool[offset:offset + G1_COMMAND_CELL_READ_SIZE]
        if len(raw) < G1_COMMAND_CELL_READ_SIZE or not any(raw):
            continue
        x, y, width, height = struct.unpack_from("<4i", raw, G1_COMMAND_CELL_X_OFFSET)
        summary.append({
            "slot": slot,
            "active": struct.unpack_from("<I", raw, G1_COMMAND_CELL_ACTIVE_OFFSET)[0],
            "group": struct.unpack_from("<I", raw, G1_COMMAND_CELL_GROUP_OFFSET)[0],
            "geometry": {"x": x, "y": y, "width": width, "height": height},
            "category": struct.unpack_from("<I", raw, G1_COMMAND_CELL_CATEGORY_OFFSET)[0],
            "flag": struct.unpack_from("<I", raw, G1_COMMAND_CELL_FLAG_OFFSET)[0],
            "callbacks": {
                "click": f"0x{struct.unpack_from('<I', raw, G1_COMMAND_CELL_CLICK_CALLBACK_OFFSET)[0]:08X}",
                "hit": f"0x{struct.unpack_from('<I', raw, G1_COMMAND_CELL_HIT_CALLBACK_OFFSET)[0]:08X}",
            },
        })
    return summary


def _read_g1_command_branch_predicates(
    read_memory: Callable[[int, int], bytes],
    selected_slot: int,
    unit_type: int,
    *,
    phase: str,
) -> dict[str, Any]:
    """Read the original two conditions guarding the 0x0049B6D0 call."""

    type_flags_address = (
        G1_COMMAND_BRANCH_TYPE_FLAGS_BASE_ADDRESS
        + unit_type * G1_COMMAND_BRANCH_TYPE_FLAGS_STRIDE
    )
    selected_state_address = (
        G1_UNIT_BASE_ADDRESS
        + selected_slot * G1_UNIT_STRIDE
        + G1_SELECTED_UNIT_COMMAND_STATE_OFFSET
    )
    type_flags = struct.unpack("<B", read_memory(type_flags_address, 1))[0]
    selected_state = struct.unpack("<I", read_memory(selected_state_address, 4))[0]
    type_predicate = (type_flags & G1_COMMAND_BRANCH_REQUIRED_MASK) != 0
    selected_predicate = selected_state == 0
    return {
        "phase": phase,
        "call_address": f"0x{G1_COMMAND_BRANCH_CALL_ADDRESS:08X}",
        "type_predicate": {
            "address": f"0x{type_flags_address:08X}",
            "raw_value": type_flags,
            "mask": f"0x{G1_COMMAND_BRANCH_REQUIRED_MASK:02X}",
            "masked_value": type_flags & G1_COMMAND_BRANCH_REQUIRED_MASK,
            "passes": type_predicate,
        },
        "selected_unit_predicate": {
            "address": f"0x{selected_state_address:08X}",
            "offset": f"0x{G1_SELECTED_UNIT_COMMAND_STATE_OFFSET:02X}",
            "raw_value": selected_state,
            "passes": selected_predicate,
        },
        "eligible": type_predicate and selected_predicate,
    }


def _g1_command_branch_values(evidence: Mapping[str, Any]) -> tuple[int, int]:
    return (
        int(evidence["type_predicate"]["raw_value"]),
        int(evidence["selected_unit_predicate"]["raw_value"]),
    )


def _read_g1_alternate_ui_snapshot(
    read_memory: Callable[[int, int], bytes], selected_slot: int
) -> dict[str, Any]:
    """Capture the false-branch UI-list inputs without trusting its count."""

    if selected_slot not in G1_UNIT_SLOT_RANGE:
        raise _CommandCellSnapshotError(
            f"alternate UI selected-unit slot is out of bounds: {selected_slot}", []
        )
    unit_address = G1_UNIT_BASE_ADDRESS + selected_slot * G1_UNIT_STRIDE
    count_address = unit_address + G1_ALTERNATE_UI_COUNT_OFFSET
    records_address = unit_address + G1_ALTERNATE_UI_RECORDS_OFFSET
    count_raw = read_memory(count_address, 2)
    records_raw = read_memory(
        records_address,
        G1_ALTERNATE_UI_RECORD_COUNT * G1_ALTERNATE_UI_RECORD_STRIDE,
    )
    flags_raw = read_memory(
        G1_ALTERNATE_UI_FLAGS_BASE_ADDRESS,
        G1_ALTERNATE_UI_RECORD_COUNT * G1_ALTERNATE_UI_FLAG_STRIDE,
    )
    geometry_raw = read_memory(G1_ALTERNATE_UI_GEOMETRY_BASE_ADDRESS, 8)
    if len(count_raw) != 2 or len(records_raw) != 40 or len(flags_raw) != 20 or len(geometry_raw) != 8:
        raise _CommandCellSnapshotError(
            "alternate UI raw snapshot has an unexpected block size", []
        )

    count = struct.unpack("<H", count_raw)[0]
    records = [
        {
            "index": index,
            "address": f"0x{records_address + index * G1_ALTERNATE_UI_RECORD_STRIDE:08X}",
            "raw_words": list(struct.unpack_from("<2H", records_raw, index * 4)),
        }
        for index in range(G1_ALTERNATE_UI_RECORD_COUNT)
    ]
    flags = [
        {
            "index": index,
            "address": f"0x{G1_ALTERNATE_UI_FLAGS_BASE_ADDRESS + index * G1_ALTERNATE_UI_FLAG_STRIDE:08X}",
            "raw_value": struct.unpack_from("<H", flags_raw, index * 2)[0],
        }
        for index in range(G1_ALTERNATE_UI_RECORD_COUNT)
    ]
    geometry_values = list(struct.unpack("<4H", geometry_raw))
    snapshot = {
        "selected_slot": selected_slot,
        "unit_address": f"0x{unit_address:08X}",
        "count": {
            "address": f"0x{count_address:08X}",
            "offset": f"0x{G1_ALTERNATE_UI_COUNT_OFFSET:02X}",
            "raw_value": count,
            "raw_hex": count_raw.hex(),
        },
        "records": {
            "address": f"0x{records_address:08X}",
            "offset": f"0x{G1_ALTERNATE_UI_RECORDS_OFFSET:02X}",
            "count": G1_ALTERNATE_UI_RECORD_COUNT,
            "stride": f"0x{G1_ALTERNATE_UI_RECORD_STRIDE:02X}",
            "raw_hex": records_raw.hex(),
            "values": records,
        },
        "flags": {
            "address": f"0x{G1_ALTERNATE_UI_FLAGS_BASE_ADDRESS:08X}",
            "count": G1_ALTERNATE_UI_RECORD_COUNT,
            "stride": f"0x{G1_ALTERNATE_UI_FLAG_STRIDE:02X}",
            "raw_hex": flags_raw.hex(),
            "values": flags,
        },
        "geometry": {
            "address": f"0x{G1_ALTERNATE_UI_GEOMETRY_BASE_ADDRESS:08X}",
            "fields": dict(zip(G1_ALTERNATE_UI_GEOMETRY_FIELD_NAMES, geometry_values)),
            "raw_hex": geometry_raw.hex(),
        },
    }
    if count > G1_ALTERNATE_UI_RECORD_COUNT:
        raise _CommandCellSnapshotError(
            f"alternate UI count is out of bounds: {count}", [], alternate_snapshot=snapshot
        )
    return snapshot


def _g1_alternate_ui_values(snapshot: Mapping[str, Any]) -> tuple[Any, ...]:
    """Return only observed values for before/after coherence comparison."""

    count = snapshot["count"]["raw_value"]
    records = tuple(
        tuple(record["raw_words"]) for record in snapshot["records"]["values"]
    )
    flags = tuple(flag["raw_value"] for flag in snapshot["flags"]["values"])
    geometry = tuple(snapshot["geometry"]["fields"].values())
    return (count, records, flags, geometry)


def _read_g1_primary_command_table(
    read_memory: Callable[[int, int], bytes],
) -> dict[str, Any]:
    """Capture the raw primary 12-slot table without assigning field meaning."""

    raw = read_memory(
        G1_PRIMARY_COMMAND_TABLE_BASE_ADDRESS, G1_PRIMARY_COMMAND_TABLE_READ_SIZE
    )
    if len(raw) != G1_PRIMARY_COMMAND_TABLE_READ_SIZE:
        raise _CommandCellSnapshotError(
            f"primary command-table snapshot has wrong size: {len(raw)}", []
        )
    blocks: dict[str, dict[str, Any]] = {}
    for name, offset in G1_PRIMARY_COMMAND_TABLE_BLOCKS:
        block_raw = raw[offset:offset + G1_PRIMARY_COMMAND_TABLE_WORD_COUNT * 2]
        if len(block_raw) != G1_PRIMARY_COMMAND_TABLE_WORD_COUNT * 2:
            raise _CommandCellSnapshotError(
                f"primary command-table block {name} has wrong size: {len(block_raw)}", []
            )
        blocks[name] = {
            "address": f"0x{G1_PRIMARY_COMMAND_TABLE_BASE_ADDRESS + offset:08X}",
            "count": G1_PRIMARY_COMMAND_TABLE_WORD_COUNT,
            "stride": "0x02",
            "raw_hex": block_raw.hex(),
            "values": [
                {
                    "index": index,
                    "address": f"0x{G1_PRIMARY_COMMAND_TABLE_BASE_ADDRESS + offset + index * 2:08X}",
                    "raw_value": struct.unpack_from("<H", block_raw, index * 2)[0],
                }
                for index in range(G1_PRIMARY_COMMAND_TABLE_WORD_COUNT)
            ],
        }
    return {
        "address": f"0x{G1_PRIMARY_COMMAND_TABLE_BASE_ADDRESS:08X}",
        "size": G1_PRIMARY_COMMAND_TABLE_READ_SIZE,
        "raw_hex": raw.hex(),
        "blocks": blocks,
    }


def _g1_primary_command_table_values(snapshot: Mapping[str, Any]) -> tuple[Any, ...]:
    return tuple(
        tuple(entry["raw_value"] for entry in snapshot["blocks"][name]["values"])
        for name, _offset in G1_PRIMARY_COMMAND_TABLE_BLOCKS
    )


def _g1_production_click_if_authorized(
    _production_cell: Mapping[str, Any], _click: Callable[[], None]
) -> dict[str, str]:
    """Keep the unresolved primary/action mapping from authorizing a mouse click."""

    del _production_cell, _click
    return {
        "status": "BLOCKED",
        "reason": "production click blocked: primary field/action and worker mapping are not approved",
    }


def _read_g1_selection_count(read_memory: Callable[[int, int], bytes]) -> int:
    """Read only the selection count before any selected-unit detail reads."""

    return struct.unpack("<i", read_memory(G1_SELECTION_COUNT_ADDRESS, 4))[0]


def _read_g1_command_selection_identity(
    read_memory: Callable[[int, int], bytes],
    *,
    selection_count: int | None = None,
) -> dict[str, Any]:
    """Read the selected-unit identity that must bracket one pool snapshot."""

    if selection_count is None:
        selection_count = _read_g1_selection_count(read_memory)
    if not 0 <= selection_count <= len(G1_UNIT_SLOT_RANGE):
        raise _CommandCellSnapshotError(
            f"unsupported selected-unit count: {selection_count}", [], retryable=False
        )
    if selection_count == 0:
        return {"selection": {"count": selection_count}}
    selected_slot = struct.unpack("<h", read_memory(G1_SELECTION_FIRST_SLOT_ADDRESS, 2))[0]
    if selected_slot not in G1_UNIT_SLOT_RANGE:
        raise _CommandCellSnapshotError(f"unsupported selected-unit slot: {selected_slot}", [])

    unit_address = G1_UNIT_BASE_ADDRESS + selected_slot * G1_UNIT_STRIDE
    active = struct.unpack(
        "<h", read_memory(G1_UNIT_EXISTS_BASE_ADDRESS + selected_slot * 2, 2)
    )[0]
    if active == 0:
        raise _CommandCellSnapshotError(f"selected unit slot is not active: {selected_slot}", [])
    unit_type = struct.unpack("<B", read_memory(unit_address + G1_UNIT_TYPE_OFFSET, 1))[0]
    if unit_type == 0:
        raise _CommandCellSnapshotError(f"selected unit has unsupported type: {unit_type}", [])

    return {
        "selection": {"count": selection_count, "first_slot": selected_slot},
        "unit": {"active": active, "type": unit_type, "address": f"0x{unit_address:08X}"},
    }


def _g1_command_selection_values(identity: Mapping[str, Any]) -> tuple[int, int, int, int]:
    selection = identity["selection"]
    unit = identity["unit"]
    return (
        int(selection["count"]),
        int(selection["first_slot"]),
        int(unit["active"]),
        int(unit["type"]),
    )


def _read_g1_command_cell_provenance_once(
    read_memory: Callable[[int, int], bytes],
    target: tuple[int, int] = G1_COMMAND_CELL_TARGET,
) -> dict[str, Any]:
    """Read and validate one selected-unit/pool snapshot."""

    before_count = _read_g1_selection_count(read_memory)
    if before_count != 1:
        raise _CommandCellSnapshotError(
            "primary command-table snapshot requires exactly one selected unit",
            [],
            {
                "selection_count_guard": {
                    "required": 1,
                    "observed": before_count,
                    "before": {"count": before_count},
                    "primary_read": False,
                }
            },
            retryable=False,
        )
    before_identity = _read_g1_command_selection_identity(
        read_memory, selection_count=before_count
    )
    primary_before = _read_g1_primary_command_table(read_memory)
    selected_slot = int(before_identity["selection"]["first_slot"])
    unit_type = int(before_identity["unit"]["type"])
    type_address = G1_UNIT_TYPE_TABLE_BASE_ADDRESS + unit_type * G1_UNIT_STRIDE
    type_values = list(struct.unpack("<4I", read_memory(type_address, 16)))
    branch_before = _read_g1_command_branch_predicates(
        read_memory, selected_slot, unit_type, phase="before_pool"
    )
    alternate_before = (
        _read_g1_alternate_ui_snapshot(read_memory, selected_slot)
        if not branch_before["eligible"]
        else None
    )

    pool = read_memory(G1_COMMAND_CELL_POOL_ALLOCATOR_START, G1_COMMAND_CELL_POOL_READ_SIZE)
    after_identity = _read_g1_command_selection_identity(read_memory)
    if after_identity["selection"]["count"] == 0:
        raw_summary = _command_cell_raw_summary(pool)
        branch_evidence = {
            "call_address": f"0x{G1_COMMAND_BRANCH_CALL_ADDRESS:08X}",
            "selected_slot": selected_slot,
            "unit_type": unit_type,
            "before_pool": {**before_identity},
            "after_pool": {**after_identity},
            "selection_identity_stable": False,
            "predicate_stable": False,
            "alternate_ui_stable": False,
            "stable": False,
            "eligible": False,
        }
        raise _CommandCellSnapshotError(
            "selection identity changed during command-cell pool read",
            raw_summary,
            branch_evidence,
            primary_snapshot={"before": primary_before, "after": None, "stable": False},
        )
    primary_after = _read_g1_primary_command_table(read_memory)
    after_slot = int(after_identity["selection"]["first_slot"])
    after_type = int(after_identity["unit"]["type"])
    branch_after = _read_g1_command_branch_predicates(read_memory, after_slot, after_type, phase="after_pool")
    alternate_after = (
        _read_g1_alternate_ui_snapshot(read_memory, after_slot)
        if not branch_after["eligible"]
        else None
    )
    selection_stable = _g1_command_selection_values(before_identity) == _g1_command_selection_values(after_identity)
    branch_stable = _g1_command_branch_values(branch_before) == _g1_command_branch_values(branch_after)
    alternate_stable = (
        alternate_before is not None
        and alternate_after is not None
        and _g1_alternate_ui_values(alternate_before)
        == _g1_alternate_ui_values(alternate_after)
    )
    primary_stable = _g1_primary_command_table_values(primary_before) == _g1_primary_command_table_values(primary_after)
    primary_snapshot = {
        "before": primary_before,
        "after": primary_after,
        "stable": primary_stable,
    }
    branch_evidence = {
        "call_address": f"0x{G1_COMMAND_BRANCH_CALL_ADDRESS:08X}",
        "selected_slot": selected_slot,
        "unit_type": unit_type,
        "before_pool": {
            **before_identity,
            **branch_before,
        },
        "after_pool": {
            **after_identity,
            **branch_after,
        },
        "selection_identity_stable": selection_stable,
        "predicate_stable": branch_stable,
        "alternate_ui_stable": alternate_stable,
        "stable": selection_stable and branch_stable,
        "eligible": bool(branch_before["eligible"] and branch_after["eligible"]),
    }
    raw_summary = _command_cell_raw_summary(pool)
    if not selection_stable:
        raise _CommandCellSnapshotError(
            "selection identity changed during command-cell pool read",
            raw_summary,
            branch_evidence,
            primary_snapshot=primary_snapshot,
        )
    if not primary_stable:
        raise _CommandCellSnapshotError(
            "primary command-table snapshot changed during command-cell pool read",
            raw_summary,
            branch_evidence,
            primary_snapshot=primary_snapshot,
        )
    if not branch_stable:
        raise _CommandCellSnapshotError(
            "49B6D0 predicate changed during command-cell pool read",
            raw_summary,
            branch_evidence,
            {"before": alternate_before, "after": alternate_after, "stable": alternate_stable},
            primary_snapshot,
        )
    if not branch_evidence["eligible"]:
        if not alternate_stable:
            raise _CommandCellSnapshotError(
                "alternate UI snapshot changed during command-cell pool read",
                raw_summary,
                branch_evidence,
                {"before": alternate_before, "after": alternate_after, "stable": False},
                primary_snapshot,
            )
        raise _CommandCellSnapshotError(
            "49B6D0 ineligible: original command-cell creation predicates are false",
            raw_summary,
            branch_evidence,
            {"before": alternate_before, "after": alternate_after, "stable": True},
            primary_snapshot,
        )
    if len(pool) != G1_COMMAND_CELL_POOL_READ_SIZE:
        raise _CommandCellSnapshotError(
            f"command-cell pool snapshot has wrong size: {len(pool)}",
            raw_summary,
            branch_evidence,
            primary_snapshot=primary_snapshot,
        )
    cells: list[dict[str, Any]] = []
    for slot in G1_COMMAND_CELL_POOL_SLOTS:
        offset = (slot - G1_COMMAND_CELL_POOL_FIRST_SLOT) * G1_COMMAND_CELL_POOL_STRIDE
        address = G1_COMMAND_CELL_POOL_BASE_ADDRESS + slot * G1_COMMAND_CELL_POOL_STRIDE
        raw = pool[offset:offset + G1_COMMAND_CELL_READ_SIZE]
        active_value = struct.unpack_from("<I", raw, G1_COMMAND_CELL_ACTIVE_OFFSET)[0]
        group = struct.unpack_from("<I", raw, G1_COMMAND_CELL_GROUP_OFFSET)[0]
        click_callback = struct.unpack_from("<I", raw, G1_COMMAND_CELL_CLICK_CALLBACK_OFFSET)[0]
        hit_callback = struct.unpack_from("<I", raw, G1_COMMAND_CELL_HIT_CALLBACK_OFFSET)[0]
        if not active_value or group not in G1_COMMAND_CELL_GROUPS:
            continue
        if click_callback != G1_COMMAND_CELL_CLICK_CALLBACK or hit_callback != G1_COMMAND_CELL_HIT_CALLBACK:
            continue
        x, y, width, height = struct.unpack_from("<4i", raw, G1_COMMAND_CELL_X_OFFSET)
        cells.append({
            "slot": slot,
            "address": f"0x{address:08X}",
            "active": active_value,
            "group": group,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "category": struct.unpack_from("<I", raw, G1_COMMAND_CELL_CATEGORY_OFFSET)[0],
            "flag": struct.unpack_from("<I", raw, G1_COMMAND_CELL_FLAG_OFFSET)[0],
            "callbacks": {
                "click": f"0x{click_callback:08X}",
                "hit": f"0x{hit_callback:08X}",
            },
        })

    cells.sort(key=lambda cell: int(cell["group"]))
    if len(cells) != len(G1_COMMAND_CELL_GROUPS) or tuple(cell["group"] for cell in cells) != G1_COMMAND_CELL_GROUPS:
        raise _CommandCellSnapshotError(
            f"expected one command cell for each group 2..5, got {cells}",
            raw_summary,
            branch_evidence,
            primary_snapshot=primary_snapshot,
        )

    target_x, target_y = target
    hits = [
        cell for cell in cells
        if int(cell["x"]) < target_x < int(cell["x"]) + int(cell["width"])
        and int(cell["y"]) < target_y < int(cell["y"]) + int(cell["height"])
    ]
    if len(hits) != 1:
        raise _CommandCellSnapshotError(
            f"command-cell target must have one strict hit, got {len(hits)}",
            raw_summary,
            branch_evidence,
            primary_snapshot=primary_snapshot,
        )

    return {
        "selection": after_identity["selection"],
        "unit": after_identity["unit"],
        "primary_command_table": primary_snapshot,
        "type_command": {"address": f"0x{type_address:08X}", "values": type_values},
        "command_branch": branch_evidence,
        "target": {"x": target_x, "y": target_y, "hit_group": hits[0]["group"]},
        "cells": cells,
    }


def _read_g1_command_cell_provenance(
    read_memory: Callable[[int, int], bytes],
    executable_sha256: str,
    target: tuple[int, int] = G1_COMMAND_CELL_TARGET,
    *,
    started: float | None = None,
    timeout: float | None = None,
    poll_interval: float = 0.25,
) -> dict[str, Any]:
    """Read one coherent command-cell snapshot, polling only within a caller deadline."""

    if executable_sha256 != ORIGINAL_SHA256:
        raise RuntimeSafetyError("command-cell reader refused unexpected executable SHA-256")
    if (started is None) != (timeout is None):
        raise RuntimeSafetyError("command-cell polling requires both started and timeout")
    if poll_interval <= 0:
        raise RuntimeSafetyError("command-cell poll interval must be positive")

    deadline = None if started is None or timeout is None else started + timeout
    attempts = 0
    diagnostics: list[dict[str, Any]] = []
    last_error: BaseException | None = None
    while True:
        if deadline is not None and time.monotonic() >= deadline:
            failure = RuntimeSafetyError(
                f"command-cell coherent snapshot timed out after {attempts} attempts; "
                f"last_error={last_error}; diagnostics={json.dumps(diagnostics, separators=(',', ':'))}"
            )
            failure.command_cell_diagnostics = diagnostics  # type: ignore[attr-defined]
            raise failure from last_error
        attempts += 1
        try:
            evidence = _read_g1_command_cell_provenance_once(read_memory, target)
            evidence["executable_sha256"] = executable_sha256
            evidence["snapshot_attempts"] = attempts
            return evidence
        except (OSError, ValueError, struct.error, RuntimeSafetyError) as exc:
            last_error = exc
            diagnostics.append({
                "timestamp": time.time(),
                "attempt": attempts,
                "raw": getattr(exc, "raw_summary", []),
                "command_branch": getattr(exc, "branch_evidence", None),
                "alternate_ui": getattr(exc, "alternate_snapshot", None),
                "primary_command_table": getattr(exc, "primary_snapshot", None),
            })
            if len(diagnostics) > G1_COMMAND_CELL_DIAGNOSTIC_ATTEMPTS:
                diagnostics.pop(0)
            branch = getattr(exc, "branch_evidence", None)
            if isinstance(exc, _CommandCellSnapshotError) and not exc.retryable:
                raise
            if (
                isinstance(exc, _CommandCellSnapshotError)
                and branch is not None
                and branch.get("stable") is True
                and branch.get("eligible") is False
                and branch.get("alternate_ui_stable") is True
            ):
                raise
            if deadline is None:
                raise
            remaining = deadline - time.monotonic()
            if remaining > 0:
                time.sleep(min(poll_interval, remaining))


def _record_g1_command_cell_error(
    evidence: dict[str, Any], exc: BaseException
) -> None:
    """Copy bounded command-cell diagnostics into the run result before re-raising."""

    diagnostics = getattr(exc, "command_cell_diagnostics", None)
    if diagnostics is not None:
        evidence["command_cell_diagnostics"] = diagnostics
    branch = getattr(exc, "branch_evidence", None)
    if branch is not None:
        evidence["command_branch"] = branch
    alternate_snapshot = getattr(exc, "alternate_snapshot", None)
    if alternate_snapshot is not None:
        evidence["alternate_ui_snapshot"] = alternate_snapshot
    primary_snapshot = getattr(exc, "primary_snapshot", None)
    if primary_snapshot is not None:
        evidence["primary_command_table"] = primary_snapshot


def _read_camera(read_memory: Callable[[int, int], bytes]) -> list[int]:
    return list(struct.unpack("<2i", read_memory(0x00B42D7C, 8)))


def _g1_input_geometry(
    content_crop: tuple[int, int, int, int], scale: tuple[float, float], x: int, y: int,
) -> dict[str, object]:
    """Describe a logical input and its root coordinate without pre-scaling it."""

    return {
        "content": [x, y],
        "x11": [content_crop[0] + x, content_crop[1] + y],
        "content_crop": {
            "x": content_crop[0], "y": content_crop[1],
            "width": content_crop[2], "height": content_crop[3],
        },
        "scale": list(scale),
    }


def _g1_record_input(
    inputs: list[dict[str, Any]], *, tag: str, x: int, y: int,
    content_crop: tuple[int, int, int, int], scale: tuple[float, float],
    before: object, expected: str, after: object, actual: str, result: str,
    extra: Mapping[str, object] | None = None,
) -> dict[str, Any]:
    """Append the shared baseline/candidate input evidence schema."""

    entry: dict[str, Any] = {
        "tag": tag,
        **_g1_input_geometry(content_crop, scale, x, y),
        "before": before,
        "after": after,
        "expected": expected,
        "actual": actual,
        "result": result,
    }
    if extra:
        entry.update(extra)
    inputs.append(entry)
    return entry


def _g1_record_selector_input(
    inputs: list[dict[str, Any]], *, tag: str, x: int, y: int,
    content_crop: tuple[int, int, int, int], scale: tuple[float, float],
    before: object, expected: str, after: object, actual: str, result: str,
    flush: Callable[[], None],
) -> dict[str, Any]:
    """Record one selector-flow input through the shared schema and flush it."""

    entry = _g1_record_input(
        inputs, tag=tag, x=x, y=y, content_crop=content_crop, scale=scale,
        before=before, expected=expected, after=after, actual=actual, result=result,
    )
    flush()
    return entry


def _g1_menu_input_pass(before: Mapping[str, Any], after: Mapping[str, Any]) -> bool:
    """Use the same PS transition and changed-capture predicate on both paths."""

    before_capture = before.get("screenshot")
    after_capture = after.get("screenshot")
    return (
        before.get("ps") == 9
        and after.get("ps") == 7
        and isinstance(before_capture, Mapping)
        and isinstance(after_capture, Mapping)
        and before_capture.get("sha256") != after_capture.get("sha256")
    )


def _g1_selection_responded(
    before: Mapping[str, Any], after: Mapping[str, Any],
    *, diagnostics: dict[str, Any] | None = None,
) -> bool:
    """Recognize a selection response only when both observations are sound."""

    def observation_is_sound(observation: Mapping[str, Any]) -> bool:
        count = observation.get("count")
        if type(count) is not int:
            return False
        if count < 0:
            return False
        if count == 0:
            return True
        return (
            type(observation.get("selected_slot")) is int
            and observation.get("selected_type") != "UNKNOWN"
        )

    before_sound = observation_is_sound(before)
    after_sound = observation_is_sound(after)
    if diagnostics is not None:
        previous = diagnostics.get("selection_observation")
        previous_count = (
            previous.get("corrupted_poll_count", 0)
            if isinstance(previous, Mapping) else 0
        )
        corrupted_poll_count = (
            previous_count if type(previous_count) is int and previous_count >= 0 else 0
        )
        first_corruption = (
            previous.get("first_corruption_provenance")
            if isinstance(previous, Mapping) else None
        )
        last_corruption = (
            previous.get("last_corruption_provenance")
            if isinstance(previous, Mapping) else None
        )
        if not before_sound or not after_sound:
            corruption_provenance = {
                "before": {
                    "count": before.get("count"),
                    "selected_slot": before.get("selected_slot"),
                    "selected_type": before.get("selected_type"),
                    "selected_type_provenance": before.get("selected_type_provenance"),
                },
                "after": {
                    "count": after.get("count"),
                    "selected_slot": after.get("selected_slot"),
                    "selected_type": after.get("selected_type"),
                    "selected_type_provenance": after.get("selected_type_provenance"),
                },
            }
            corrupted_poll_count += 1
            if first_corruption is None:
                first_corruption = corruption_provenance
            last_corruption = corruption_provenance
        diagnostics["selection_observation"] = {
            "status": "SOUND" if before_sound and after_sound else "CORRUPTED",
            "before_sound": before_sound,
            "after_sound": after_sound,
            "before": dict(before),
            "after": dict(after),
            "corrupted_poll_count": corrupted_poll_count,
            "first_corruption_provenance": first_corruption,
            "last_corruption_provenance": last_corruption,
        }

    if not before_sound or not after_sound:
        return False

    before_identity = (before.get("selected_slot"), before.get("selected_type"))
    after_identity = (after.get("selected_slot"), after.get("selected_type"))
    return before.get("count") != after.get("count") or before_identity != after_identity


def _g1_read_selection_stage(
    read_selection: Callable[[], dict[str, Any]], *, stage: str,
    read_point: str, started: float, timeout: float,
    stage_started: float | None = None,
) -> dict[str, Any]:
    """Read selection outside a poll while preserving a stage-level failure."""

    try:
        return read_selection()
    except (OSError, ValueError, struct.error) as exc:
        finished = time.monotonic()
        provenance = f"{type(exc).__name__}: {exc}"
        stage_budget = G1_INPUT_STAGE_BUDGETS.get(stage)
        finished_elapsed = max(0.0, finished - started)
        remaining_budget_after = max(0.0, started + timeout - finished)
        # Check the configured stage budget before the stage start.  The
        # production reader is intentionally called without stage_started and
        # production has no configured stage budget; that reachable shape is
        # STAGE_BUDGET_UNAVAILABLE, not STAGE_START_UNKNOWN.
        stage_budget_state = (
            "STAGE_BUDGET_UNAVAILABLE"
            if stage_budget is None
            else "STAGE_START_UNKNOWN"
            if stage_started is None
            else "STAGE_BUDGET_EXHAUSTED"
            if finished >= stage_started + stage_budget
            else "WITHIN_STAGE_BUDGET"
        )
        observation = {
            "stage": stage,
            "stage_budget": stage_budget,
            "stage_started_elapsed": round(max(0.0, stage_started - started), 3)
            if stage_started is not None else None,
            "finished_elapsed": round(finished_elapsed, 3),
            "remaining_budget_after": round(remaining_budget_after, 3),
            "stage_budget_exhausted": bool(
                stage_budget is not None
                and stage_started is not None
                and finished >= stage_started + stage_budget
            ),
            # Keep the legacy boolean for callers that only need the deadline
            # result, but expose why false was reported.  In particular,
            # ``False`` can mean an in-window read, an unknown stage start, or
            # a stage with no configured budget.
            "stage_budget_state": stage_budget_state,
            "run_budget_exhausted": remaining_budget_after <= 0.0,
            "direct_reader": "selection",
            "direct_reader_failure": True,
            "direct_read_point": read_point,
            "direct_read_attempt_count": 1,
            "direct_read_error_count": 1,
            "poll_count": 0,
            "poll_attempt_count": 0,
            "read_error_count": 1,
            "first_read_error_provenance": provenance,
            "last_read_error_provenance": provenance,
            "successful_poll_ratio": 0.0,
            "read_error_ratio": None,
            "read_error_coverage_threshold_ratio": G1_INPUT_MAX_READ_ERROR_RATIO,
            "read_error_coverage_exceeds_threshold": None,
            "observation_source": "direct_selection_reader",
        }
        raise _G1WaitTimeout(
            f"{stage} selection reader failed at {read_point}: {provenance}",
            # A direct reader exception is the most specific observation.  It
            # remains UNKNOWN_STATE_READ_FAILURE even when the run deadline
            # was reached at the same instant; budget exhaustion must not hide
            # the failed state read behind UNKNOWN_BUDGET_EXHAUSTED.
            classification="UNKNOWN_STATE_READ_FAILURE",
            last=None,
            finished_elapsed=finished_elapsed,
            remaining_budget_after=remaining_budget_after,
            observation=observation,
        ) from exc


G1_REQUIRED_INPUT_TAGS: tuple[str, ...] = (
    "menu", "unit_select", "production", "drag_select", "minimap",
)
G1_INPUT_STAGE_BUDGETS: dict[str, float] = {
    "unit_select": 10.0,
    "drag_select": 10.0,
    "minimap": 10.0,
}
# A-13/A-14: this is a design assumption based on retaining at least 75% of a
# stage's observation window, not a measurement of pre-poll work.  Real-game
# pre-poll timing is unmeasured; the first Stage B run must record it and
# reassess the threshold.  For a 10s stage, the 25% allowance is 2.5s.
G1_INPUT_MAX_TRUNCATION_RATIO = 0.25
# A read-error-heavy window cannot establish that an input had no effect.  Keep
# the same conservative 25% allowance as pre-poll truncation: at least 75% of
# polling attempts must be readable before a timeout may be a hard no-effect.
G1_INPUT_MAX_READ_ERROR_RATIO = 0.25
G1_INPUT_STAGE_BUDGET_TOTAL = sum(G1_INPUT_STAGE_BUDGETS.values())
if G1_INPUT_STAGE_BUDGET_TOTAL > 31.5:
    raise RuntimeSafetyError("G1 input stage budgets exceed the measured 31.5 second cap")
G1_INPUT_PHASE_WALL_CLOCK_BUDGET = 31.5
G1_PHASE_CAPTURE_TAGS: frozenset[str] = frozenset({
    "selection_after", "production_before", "drag_after", "minimap_after",
})
G1_READ_COVERAGE_FIELDS: tuple[str, ...] = (
    "poll_count", "poll_attempt_count", "read_error_count",
    "successful_poll_ratio", "read_error_ratio",
    "read_error_coverage_threshold_ratio", "read_error_coverage_exceeds_threshold",
    "first_read_error_provenance", "last_read_error_provenance",
)


def _g1_read_coverage(observation: object) -> dict[str, Any] | None:
    """Project poll coverage into a stable, reportable evidence shape."""

    if not isinstance(observation, Mapping):
        return None
    if any(field not in observation for field in G1_READ_COVERAGE_FIELDS):
        return None
    return {field: observation[field] for field in G1_READ_COVERAGE_FIELDS}


def _g1_input_verdict(
    inputs: Sequence[Mapping[str, Any]], *, enabled: bool,
) -> dict[str, Any]:
    """Summarize the required input contract with one shared fail-closed predicate."""

    tag_results: dict[str, list[Any]] = {tag: [] for tag in G1_REQUIRED_INPUT_TAGS}
    read_coverage: dict[str, dict[str, Any]] = {}
    production_records: list[dict[str, Any]] = []
    for item in inputs:
        tag = item.get("tag")
        if tag not in tag_results:
            continue
        tag_results[tag].append(item.get("result"))
        if tag in G1_INPUT_STAGE_BUDGETS:
            coverage = _g1_read_coverage(item.get("read_coverage"))
            if coverage is None:
                coverage = _g1_read_coverage(item.get("wait_observation"))
            if coverage is not None:
                read_coverage[tag] = coverage
        if tag == "production":
            production_records.append({
                "result": item.get("result"),
                "status": item.get("after", {}).get("status")
                if isinstance(item.get("after"), Mapping) else None,
                "waited": item.get("waited"),
                "blocked_reason": item.get("blocked_reason"),
            })
    required_results = [
        item for item in inputs if item.get("tag") in G1_REQUIRED_INPUT_TAGS
    ]
    required_inputs = (
        not enabled
        or len(required_results) == len(G1_REQUIRED_INPUT_TAGS)
        and set(item.get("tag") for item in required_results) == set(G1_REQUIRED_INPUT_TAGS)
        and all(item.get("result") == "PASS" for item in required_results)
    )
    production_blocked = any(
        item.get("tag") == "production" and item.get("result") == "BLOCKED"
        for item in inputs
    )
    return {
        "enabled": enabled,
        "required_inputs": required_inputs,
        "tag_results": tag_results,
        "read_coverage": read_coverage,
        "production_blocked": production_blocked,
        "production_records": production_records,
    }


def _g1_measure_phase_item(
    metrics: dict[str, Any], item: str, operation: Callable[[], Any],
) -> Any:
    """Measure one input-phase operation without changing its result or errors."""

    item_started = time.monotonic()
    try:
        result = operation()
    except Exception as exc:
        metrics.setdefault("items", {})[item] = {
            "status": "ERROR",
            "elapsed_seconds": round(max(0.0, time.monotonic() - item_started), 6),
            "error": f"{type(exc).__name__}: {exc}",
        }
        raise
    record: dict[str, Any] = {
        "status": "PASS",
        "elapsed_seconds": round(max(0.0, time.monotonic() - item_started), 6),
    }
    if isinstance(result, Mapping) and item == "production_provenance":
        record["executable_sha256"] = result.get("executable_sha256")
    metrics.setdefault("items", {})[item] = record
    return result


def _g1_finalize_input_phase(metrics: dict[str, Any], phase_started: float) -> None:
    """Finalize phase timing and make a wall-clock overrun explicit in evidence."""

    if "input_phase_elapsed" in metrics:
        return
    elapsed = round(max(0.0, time.monotonic() - phase_started), 3)
    metrics["budget_seconds"] = G1_INPUT_PHASE_WALL_CLOCK_BUDGET
    metrics["input_phase_elapsed"] = elapsed
    metrics["over_budget"] = elapsed > G1_INPUT_PHASE_WALL_CLOCK_BUDGET
    if metrics["over_budget"]:
        metrics["budget_status"] = "OVER_BUDGET"
        metrics["over_budget_cause"] = {
            "kind": "INPUT_PHASE_WALL_CLOCK_EXCEEDED",
            "limit_seconds": G1_INPUT_PHASE_WALL_CLOCK_BUDGET,
            "elapsed_seconds": elapsed,
            "excess_seconds": round(elapsed - G1_INPUT_PHASE_WALL_CLOCK_BUDGET, 3),
            "measured_items": dict(metrics.get("items", {})),
        }
    else:
        metrics["budget_status"] = "WITHIN_BUDGET"


def _g1_presentation_verdict(
    *, error: str | None, cleanup: Mapping[str, Any],
    validator: Mapping[str, Any], inputs: Sequence[Mapping[str, Any]],
    input_sequence: bool,
) -> dict[str, Any]:
    """Assemble the candidate verdict without hiding input or teardown failures."""

    input_checks = _g1_input_verdict(inputs, enabled=input_sequence)
    cleanup_ok = bool(cleanup.get("ok"))
    validator_ok = validator.get("status") == "PASS"
    return {
        "overall": "PASS" if not error and cleanup_ok and validator_ok
        and bool(input_checks["required_inputs"]) else "BLOCKED",
        "checks": {"required_inputs": input_checks["required_inputs"]},
        "input_checks": input_checks,
        "input_observations": input_checks["tag_results"],
        "production": {
            "blocked": input_checks["production_blocked"],
            "records": input_checks["production_records"],
        },
        "teardown": {
            "error": error,
            "cleanup_ok": cleanup_ok,
            "cleanup": dict(cleanup),
        },
        "error": error,
        "cleanup": cleanup,
        "validator": validator,
        "remaining_risks": ["diagnostic bridge is not stock _inmm.dll", "no product patch or 2x output was implemented", "no second-tier or user milestone approval"],
    }


def _g1_baseline_verdict(
    *, error: str | None, checks: Mapping[str, Any],
    input_checks: Mapping[str, Any], cleanup: Mapping[str, Any],
) -> dict[str, Any]:
    """Assemble the baseline verdict using the same required-input result."""

    return {
        "overall": "PASS" if not error and all(checks.values()) else "FAIL",
        "checks": dict(checks),
        "input_checks": dict(input_checks),
        "error": error,
        "cleanup": cleanup,
        "remaining_risks": ["G1 product patch and 2x output are not implemented or approved",
                            "scene has no exposed replay seed; identifier is same-run fingerprint",
                            "no visual second-tier review or user milestone approval"],
        "next_reversible_probe": {"status": "not authorized by this work card",
                                  "change_point": "none; observational run only", "old_bytes": None,
                                  "exact_version_rejection": "required before any binary patch",
                                  "rollback": "not applicable; no binary was changed"},
    }


def _g1_scene_snapshot(
    scene_state: Mapping[str, Any], read_memory: Callable[[int, int], bytes],
) -> dict[str, Any]:
    """Build the approved, read-only scene identity used before G1 input."""

    players = scene_state.get("players")
    units = scene_state.get("units")
    if not isinstance(players, list) or not isinstance(units, list):
        raise RuntimeSafetyError("PS3 scene lacks detailed player/unit state for parity evidence")

    owner_by_id: dict[int, Mapping[str, Any]] = {
        int(player["owner"]): player for player in players
        if isinstance(player, Mapping) and isinstance(player.get("owner"), int)
    }
    active_counts = {
        owner: sum(1 for unit in units if isinstance(unit, Mapping) and unit.get("owner") == owner)
        for owner in range(8)
    }
    owners = {
        str(owner): {
            "nation": owner_by_id.get(owner, {}).get("nation"),
            "active_units": active_counts[owner],
        }
        for owner in range(8)
    }
    unit_slots = [
        {
            "slot": unit.get("slot"), "owner": unit.get("owner"), "type": unit.get("type"),
            "world": {"x": unit.get("x"), "y": unit.get("y")},
        }
        for unit in units if isinstance(unit, Mapping)
    ]
    owner0_types: list[int] = []
    for item in unit_slots:
        item_type = item.get("type")
        if item.get("owner") == 0 and isinstance(item_type, int):
            owner0_types.append(item_type)
    owner0_types = sorted(set(owner0_types))
    raw_bounds = read_memory(G1_MAP_WIDTH_ADDRESS, 4)
    map_width, map_height = struct.unpack("<2h", raw_bounds)
    if not 1 <= map_width <= 180 or not 1 <= map_height <= 180:
        raise RuntimeSafetyError(
            f"unsupported approved map bounds: width={map_width}, height={map_height}"
        )
    return {
        "owners": owners,
        "unit_slots": unit_slots,
        # No approved read-only discriminator identifies an HQ across fixtures.
        # Preserve explicit provenance instead of treating type 49 as universal
        # or claiming that no HQ exists when the observation is inconclusive.
        "owner0_hq_world": None,
        "owner0_hq_candidates": None,
        "owner0_hq_type": {
            "status": "UNKNOWN",
            "observed_owner0_types": owner0_types,
            "reason": "no approved HQ discriminator; type 49 is fixture-specific",
        },
        "world_bounds": {
            "width": map_width, "height": map_height,
            "width_address": f"0x{G1_MAP_WIDTH_ADDRESS:08X}",
            "height_address": f"0x{G1_MAP_HEIGHT_ADDRESS:08X}",
        },
        "camera": _read_camera(read_memory),
        "tick": scene_state.get("tick"),
    }


def _g1_flush_input_stage(directory: Path, evidence: dict[str, Any], inputs: list[dict[str, Any]]) -> None:
    """Persist each stage before any later input or teardown can block the run."""

    evidence["inputs"] = inputs
    production = next((item for item in inputs if item.get("tag") == "production"), None)
    if isinstance(production, Mapping):
        # A command-cell provenance failure is non-fatal to the remaining input
        # sequence, so the shared runner does not enter its outer except block.
        # Promote the observed diagnostic to the run-level snapshot as well as
        # retaining it in the production input record for top-level readers.
        provenance_error = production.get("provenance_error")
        if provenance_error is not None:
            evidence.setdefault("error", provenance_error)
            # Keep the historical top-level error for compatibility, but make
            # its non-fatal provenance meaning machine-readable.  A later
            # fatal exception may still replace ``error`` without losing this
            # diagnostic context.
            evidence.setdefault("production_provenance_error", provenance_error)
        for key in (
            "command_cell_diagnostics", "command_branch", "alternate_ui_snapshot",
            "primary_command_table",
        ):
            value = production.get(key)
            if value is not None:
                evidence.setdefault(key, value)
    _write_json(directory / "evidence.json", evidence)
    (directory / "inputs.jsonl").write_text(
        "".join(json.dumps(item, ensure_ascii=False) + "\n" for item in inputs),
        encoding="utf-8",
    )


def _g1_run_input_sequence(
    *, inputs: list[dict[str, Any]], content_crop: tuple[int, int, int, int],
    scale: tuple[float, float], capture: Callable[[str], dict[str, Any]],
    runtime_state: Callable[[], Mapping[str, Any]],
    game_state: Callable[[], dict[str, Any]],
    read_selection: Callable[[], dict[str, Any]],
    read_camera: Callable[[], list[int]],
    wait: Callable[..., dict[str, Any]],
    click: Callable[[int, int], None], drag: Callable[[int, int, int, int], None],
    read_production_cell: Callable[[], Mapping[str, Any]],
    flush: Callable[[], None], started: float, timeout: float,
    phase_metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run the shared PS3 input stages for baseline and opt-in candidate runs."""

    def record(
        stage_entry: dict[str, Any] | None, tag: str, x: int, y: int, before: object, expected: str,
        after: object, actual: str, result: str, extra: Mapping[str, object] | None = None,
    ) -> dict[str, Any]:
        if stage_entry is None:
            entry = _g1_record_input(
                inputs, tag=tag, x=x, y=y, content_crop=content_crop, scale=scale,
                before=before, expected=expected, after=after, actual=actual, result=result,
                extra=extra,
            )
        else:
            entry = stage_entry
            entry.update(_g1_input_geometry(content_crop, scale, x, y))
            entry.update({"before": before, "expected": expected, "after": after,
                          "actual": actual, "result": result,
                          "finished_elapsed": round(max(0.0, time.monotonic() - started), 3),
                          "remaining_budget_after": round(max(0.0, started + timeout - time.monotonic()), 3),
                          "predicate_observed": result == "PASS",
                          "finished_tick": after.get("tick") if isinstance(after, Mapping) else None,
                          "stage_status": "complete"})
            if extra:
                entry.update(extra)
        flush()
        return entry

    def phase_capture(tag: str) -> dict[str, Any]:
        if phase_metrics is None or tag not in G1_PHASE_CAPTURE_TAGS:
            return capture(tag)
        return _g1_measure_phase_item(phase_metrics, f"capture:{tag}", lambda: capture(tag))

    def begin_stage(tag: str) -> tuple[dict[str, Any], float, dict[str, Any]]:
        stage_started = time.monotonic()
        entered = dict(runtime_state())
        elapsed = max(0.0, stage_started - started)
        entry: dict[str, Any] = {
            "tag": tag,
            "stage": tag,
            "entered_elapsed": round(elapsed, 3),
            "remaining_budget_before": round(max(0.0, timeout - elapsed), 3),
            "stage_budget": G1_INPUT_STAGE_BUDGETS[tag],
            "entered_tick": entered.get("tick"),
            "stage_status": "running",
        }
        inputs.append(entry)
        flush()
        return entry, stage_started, entered

    def record_timeout(
        stage_entry: dict[str, Any], tag: str, x: int, y: int, before: object,
        expected: str, exc: _G1WaitTimeout,
    ) -> None:
        entry = record(
            stage_entry, tag, x, y, before, expected,
            {"wait": "not observed", "last": exc.last, "tick": exc.last.get("tick")
             if isinstance(exc.last, Mapping) else None},
            f"wait timeout: {exc.classification}", exc.classification,
            {"timeout_cause": exc.classification,
             "predicate_observed": exc.predicate_observed,
             "finished_elapsed": round(exc.finished_elapsed, 3),
             "remaining_budget_after": round(exc.remaining_budget_after, 3),
             "finished_tick": exc.last.get("tick")
             if isinstance(exc.last, Mapping) else None,
             "wait_observation": exc.observation},
        )
        del entry

    def stage_wait(
        stage_entry: dict[str, Any], stage_started: float,
        reader: Callable[[bool], dict[str, Any]],
        predicate: Callable[[dict[str, Any]], bool], message: str,
        wait_observation: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if wait_observation is None:
            wait_observation = {}
        result = wait(  # type: ignore[call-arg]
            reader, predicate, message, stage=stage_entry["stage"],
            stage_budget=stage_entry["stage_budget"], stage_started=stage_started,
            wait_observation=wait_observation,
        )
        stage_entry["wait_observation"] = wait_observation
        coverage = _g1_read_coverage(wait_observation)
        if coverage is not None:
            stage_entry["read_coverage"] = coverage
        return result

    selection_stage, selection_stage_started, selection_before_runtime = begin_stage("unit_select")
    selection_before_camera = read_camera()
    selected_before: dict[str, Any] = {"status": "UNAVAILABLE", "count": None}
    try:
        selected_before = _g1_read_selection_stage(
            read_selection, stage="unit_select", read_point="before_click",
            started=started, timeout=timeout, stage_started=selection_stage_started,
        )
    except _G1WaitTimeout as exc:
        record_timeout(
            selection_stage, "unit_select", 410, 270,
            {"ps": selection_before_runtime.get("ps"), "tick": selection_before_runtime.get("tick"),
             "selection": selected_before, "selection_count": selected_before.get("count"),
             "camera": selection_before_camera, "screenshot": {"status": "NOT_CAPTURED"}},
            "selection count 0->>=1; owner0 HQ visible", exc,
        )
        raise
    selection_png_before = capture("selection_before")
    click(410, 270)
    try:
        selected_after = stage_wait(
            selection_stage, selection_stage_started, lambda _detailed: read_selection(),
            lambda item: int(item.get("count", 0)) >= 1,
            "owner0 HQ selection did not change 0->>=1",
        )
    except _G1WaitTimeout as exc:
        record_timeout(
            selection_stage, "unit_select", 410, 270,
            {"ps": selection_before_runtime.get("ps"), "tick": selection_before_runtime.get("tick"),
             "selection": selected_before, "selection_count": selected_before.get("count"),
             "camera": selection_before_camera, "screenshot": selection_png_before},
            "selection count 0->>=1; owner0 HQ visible", exc,
        )
        raise
    selected_after_runtime = dict(runtime_state())
    selected_after_camera = read_camera()
    selection_png_after = phase_capture("selection_after")
    selected_pass = selected_before.get("count") == 0 and selected_after.get("count", 0) >= 1
    record(
        selection_stage, "unit_select", 410, 270,
        {"ps": selection_before_runtime.get("ps"), "tick": selection_before_runtime.get("tick"),
         "selection": selected_before, "selection_count": selected_before.get("count"),
         "camera": selection_before_camera, "screenshot": selection_png_before},
        "selection count 0->>=1; owner0 HQ visible",
        {"ps": selected_after_runtime.get("ps"), "tick": selected_after_runtime.get("tick"),
         "selection": selected_after, "selection_count": selected_after.get("count"),
         "camera": selected_after_camera, "screenshot": selection_png_after},
        f"count {selected_before.get('count')}->{selected_after.get('count')}; first={selected_after.get('first_slot')}",
        "PASS" if selected_pass else "FAIL",
    )
    if not selected_pass:
        raise RuntimeSafetyError("unit selection did not meet the fixed 0->>=1 expectation")

    production_before_state = game_state()
    production_before_selection: dict[str, Any] = {"status": "UNAVAILABLE", "count": None}
    production_selection_read_failure: dict[str, Any] | None = None
    try:
        production_before_selection = _g1_read_selection_stage(
            read_selection, stage="production", read_point="before_production",
            started=started, timeout=timeout,
        )
    except _G1WaitTimeout as exc:
        # Production remains fail-closed and the later input stages remain
        # reachable, but preserve the direct reader failure on its record.
        production_selection_read_failure = dict(exc.observation)
        # Keep the selection snapshot distinct from the default "not read"
        # shape.  The full stage-level provenance stays in
        # ``selection_read_failure`` below; this flag makes the nested
        # before/after status unambiguously attributable to a read failure.
        production_before_selection = {
            **production_before_selection,
            "read_failure": True,
        }
    production_before_camera = read_camera()
    production_before_png = phase_capture("production_before")
    production_provenance_fields: dict[str, Any] = {}
    try:
        if phase_metrics is None:
            production_cell = read_production_cell()
        else:
            production_cell = _g1_measure_phase_item(
                phase_metrics, "production_provenance", read_production_cell,
            )
    except _CommandCellSnapshotError as exc:
        # Provenance is diagnostic only. Keep production fail-closed, but do not
        # let an expected/incomplete command-cell branch suppress later inputs.
        diagnostic_evidence: dict[str, Any] = {}
        _record_g1_command_cell_error(diagnostic_evidence, exc)
        production_provenance_fields = {
            "provenance_error": f"{type(exc).__name__}: {exc}",
            "command_cell_diagnostics": diagnostic_evidence.get("command_cell_diagnostics"),
            "command_branch": diagnostic_evidence.get("command_branch"),
            "alternate_ui_snapshot": diagnostic_evidence.get("alternate_ui_snapshot"),
            "primary_command_table": diagnostic_evidence.get("primary_command_table"),
        }
        production_cell = {"status": "UNAVAILABLE", **production_provenance_fields}
    blocked = _g1_production_click_if_authorized(production_cell, lambda: None)
    reason = blocked["reason"]
    record(
        None, "production", 670, 490,
        {"ps": production_before_state.get("ps"), "tick": production_before_state.get("tick"),
         "state": production_before_state, "selection": production_before_selection,
         "selection_count": production_before_selection.get("count"),
         "camera": production_before_camera, "screenshot": production_before_png},
        "production click remains fail-closed; no effect wait is entered",
        {"ps": production_before_state.get("ps"), "tick": production_before_state.get("tick"),
         "state": production_before_state, "selection": production_before_selection,
         "selection_count": production_before_selection.get("count"),
         "camera": production_before_camera, "status": "BLOCKED", "waited": False},
        reason, "BLOCKED", {
            "waited": False, "blocked_reason": reason,
            **production_provenance_fields,
            **({"selection_read_failure": production_selection_read_failure}
               if production_selection_read_failure is not None else {}),
        },
    )

    drag_stage, drag_stage_started, drag_before_runtime = begin_stage("drag_select")
    drag_before_camera = read_camera()
    drag_before: dict[str, Any] = {"status": "UNAVAILABLE", "count": None}
    try:
        drag_before = _g1_read_selection_stage(
            read_selection, stage="drag_select", read_point="before_drag",
            started=started, timeout=timeout, stage_started=drag_stage_started,
        )
    except _G1WaitTimeout as exc:
        record_timeout(
            drag_stage, "drag_select", 350, 180,
            {"ps": drag_before_runtime.get("ps"), "tick": drag_before_runtime.get("tick"),
             "selection": drag_before, "selection_count": drag_before.get("count"),
             "camera": drag_before_camera, "screenshot": {"status": "NOT_CAPTURED"},
             "drag_to": _g1_input_geometry(content_crop, scale, 550, 350)},
            "selection state responded to drag input", exc,
        )
        raise
    drag_png_before = capture("drag_before")
    drag(350, 180, 550, 350)
    drag_wait_observation: dict[str, Any] = {}
    try:
        drag_after = stage_wait(
            drag_stage, drag_stage_started, lambda _detailed: read_selection(),
            lambda item: _g1_selection_responded(
                drag_before, item, diagnostics=drag_wait_observation,
            ),
            "owner0 HQ/worker drag did not produce a selection-state response",
            drag_wait_observation,
        )
    except _G1WaitTimeout as exc:
        record_timeout(
            drag_stage, "drag_select", 350, 180,
            {"ps": drag_before_runtime.get("ps"), "tick": drag_before_runtime.get("tick"),
             "selection": drag_before, "selection_count": drag_before.get("count"),
             "camera": drag_before_camera, "screenshot": drag_png_before,
             "drag_to": _g1_input_geometry(content_crop, scale, 550, 350)},
            "selection state responded to drag input", exc,
        )
        raise
    drag_after_runtime = dict(runtime_state())
    drag_after_camera = read_camera()
    try:
        drag_after = _g1_read_selection_stage(
            read_selection, stage="drag_select", read_point="after_drag",
            started=started, timeout=timeout, stage_started=drag_stage_started,
        )
    except _G1WaitTimeout as exc:
        # ``stage_wait`` already returned a sound response; this final direct
        # read is only for the persisted after-state and must still be diagnosed.
        record_timeout(
            drag_stage, "drag_select", 350, 180,
            {"ps": drag_before_runtime.get("ps"), "tick": drag_before_runtime.get("tick"),
             "selection": drag_before, "selection_count": drag_before.get("count"),
             "camera": drag_before_camera, "screenshot": drag_png_before,
             "drag_to": _g1_input_geometry(content_crop, scale, 550, 350)},
            "selection state responded to drag input", exc,
        )
        raise
    drag_png_after = phase_capture("drag_after")
    drag_pass = _g1_selection_responded(drag_before, drag_after)
    record(
        drag_stage, "drag_select", 350, 180,
        {"ps": drag_before_runtime.get("ps"), "tick": drag_before_runtime.get("tick"),
         "selection": drag_before, "selection_count": drag_before.get("count"),
         "camera": drag_before_camera, "screenshot": drag_png_before,
         "drag_to": _g1_input_geometry(content_crop, scale, 550, 350)},
        "selection state responded to drag input",
        {"ps": drag_after_runtime.get("ps"), "tick": drag_after_runtime.get("tick"),
         "selection": drag_after, "selection_count": drag_after.get("count"),
         "camera": drag_after_camera, "screenshot": drag_png_after},
        f"count {drag_before.get('count')}->{drag_after.get('count')}; "
        f"identity {drag_before.get('selected_slot')}/{drag_before.get('selected_type')}->"
        f"{drag_after.get('selected_slot')}/{drag_after.get('selected_type')}",
        "PASS" if drag_pass else "FAIL",
    )
    if not drag_pass:
        raise RuntimeSafetyError("drag selection did not respond to input")

    minimap_stage, minimap_stage_started, minimap_before_runtime = begin_stage("minimap")
    camera_before = read_camera()
    minimap_before_selection: dict[str, Any] = {"status": "UNAVAILABLE", "count": None}
    try:
        minimap_before_selection = _g1_read_selection_stage(
            read_selection, stage="minimap", read_point="before_minimap",
            started=started, timeout=timeout, stage_started=minimap_stage_started,
        )
    except _G1WaitTimeout as exc:
        record_timeout(
            minimap_stage, "minimap", 150, 520,
            {"ps": minimap_before_runtime.get("ps"), "tick": minimap_before_runtime.get("tick"),
             "camera": camera_before, "selection": minimap_before_selection,
             "selection_count": minimap_before_selection.get("count"),
             "screenshot": {"status": "NOT_CAPTURED"}},
            "camera x or y changes", exc,
        )
        raise
    minimap_png_before = capture("minimap_before")
    click(150, 520)
    try:
        camera_after = stage_wait(
            minimap_stage, minimap_stage_started,
            lambda _detailed: {"camera": read_camera(), "tick": runtime_state().get("tick")},
            lambda item: item.get("camera") != camera_before,
            "fixed minimap click did not change camera",
        )
    except _G1WaitTimeout as exc:
        record_timeout(
            minimap_stage, "minimap", 150, 520,
            {"ps": minimap_before_runtime.get("ps"), "tick": minimap_before_runtime.get("tick"),
             "camera": camera_before, "selection": minimap_before_selection,
             "selection_count": minimap_before_selection.get("count"),
             "screenshot": minimap_png_before},
            "camera x or y changes", exc,
        )
        raise
    minimap_after_runtime = dict(runtime_state())
    try:
        minimap_after_selection = _g1_read_selection_stage(
            read_selection, stage="minimap", read_point="after_minimap",
            started=started, timeout=timeout, stage_started=minimap_stage_started,
        )
    except _G1WaitTimeout as exc:
        record_timeout(
            minimap_stage, "minimap", 150, 520,
            {"ps": minimap_before_runtime.get("ps"), "tick": minimap_before_runtime.get("tick"),
             "camera": camera_before, "selection": minimap_before_selection,
             "selection_count": minimap_before_selection.get("count"),
             "screenshot": minimap_png_before},
            "camera x or y changes", exc,
        )
        raise
    minimap_png_after = phase_capture("minimap_after")
    minimap_pass = camera_after.get("camera") != camera_before
    record(
        minimap_stage, "minimap", 150, 520,
        {"ps": minimap_before_runtime.get("ps"), "tick": minimap_before_runtime.get("tick"),
         "camera": camera_before, "selection": minimap_before_selection,
         "selection_count": minimap_before_selection.get("count"), "screenshot": minimap_png_before},
        "camera x or y changes",
        {"ps": minimap_after_runtime.get("ps"), "tick": minimap_after_runtime.get("tick"),
         "camera": camera_after.get("camera"), "selection": minimap_after_selection,
         "selection_count": minimap_after_selection.get("count"), "screenshot": minimap_png_after},
        f"camera {camera_before}->{camera_after.get('camera')}",
        "PASS" if minimap_pass else "FAIL",
    )
    if not minimap_pass:
        raise RuntimeSafetyError("minimap input effect was not observed")
    return {"camera_after_minimap": camera_after.get("camera")}


def _read_lobby_mode(read_memory: Callable[[int, int], bytes]) -> int:
    """Read the committed WORD mode after the PS7 connection confirmation."""

    return struct.unpack("<H", read_memory(G1_COMMITTED_MODE_ADDRESS, 2))[0]


def _read_lobby_selector(read_memory: Callable[[int, int], bytes]) -> dict[str, object]:
    """Read PS7's two control states; exactly one selector must be active."""

    values = {
        name: struct.unpack("<I", read_memory(address, 4))[0]
        for name, address in G1_SELECTOR_STATE_ADDRESSES.items()
    }
    if tuple(values[name] for name in G1_SELECTOR_STATE_ADDRESSES) not in ((1, 0), (0, 1)):
        raise RuntimeSafetyError(f"unsupported PS7 selector one-hot state: {values}")
    values["selected"] = next(name for name, value in values.items() if value == 1)
    return values


def _selector_name(state: Mapping[str, Any]) -> str:
    selector = state.get("selector")
    if not isinstance(selector, Mapping):
        raise RuntimeSafetyError("PS7 selector state is missing")
    values = tuple(selector.get(name) for name in G1_SELECTOR_STATE_ADDRESSES)
    if values not in ((1, 0), (0, 1)):
        raise RuntimeSafetyError(f"unsupported PS7 selector one-hot state: {selector}")
    selected = selector.get("selected")
    expected = "multiplayer" if values == (1, 0) else "solo"
    if selected != expected:
        raise RuntimeSafetyError(f"PS7 selector name disagrees with one-hot state: {selector}")
    return expected


def _g1_neutral_capture(capture: Mapping[str, Any]) -> bool:
    """Require a capture to record the fixed cursor position outside controls."""

    return capture.get("cursor_content") == list(G1_NEUTRAL_POINT)


def _g1_selector_pass(
    initial_selector: str,
    normalized_selector: str | None,
    selected_selector: str,
    selected_ps: int,
    baseline_capture: Mapping[str, Any],
    selected_capture: Mapping[str, Any],
) -> bool:
    """Validate selector object transitions without reading committed mode."""

    if initial_selector not in {"multiplayer", "solo"}:
        return False
    if initial_selector == "solo" and normalized_selector != "multiplayer":
        return False
    if initial_selector == "multiplayer" and normalized_selector is not None:
        return False
    return (
        selected_ps == 7
        and selected_selector == "solo"
        and _g1_neutral_capture(baseline_capture)
        and _g1_neutral_capture(selected_capture)
        and selected_capture.get("sha256") != baseline_capture.get("sha256")
    )


def _g1_selector_flow(
    read_state: Callable[[], Mapping[str, Any]],
    wait_for: Callable[[Callable[[Mapping[str, Any]], bool], str], Mapping[str, Any]],
    click: Callable[[str, tuple[int, int]], None],
    capture_neutral: Callable[[str], Mapping[str, Any]],
    record: Callable[..., object],
) -> tuple[dict[str, Any], Mapping[str, Any], str]:
    """Run and record the visible selector's conditional setup flow."""

    state7 = dict(read_state())
    initial_selector = _selector_name(state7)
    selector_baseline = capture_neutral("lobby_selector_before")
    selector_baseline_state = state7.get("selector")
    selector_baseline_name = initial_selector
    multiplayer_point = G1_SETUP_POINTS["multiplayer_mode"]
    if initial_selector == "solo":
        click("multiplayer_mode", multiplayer_point)
        normalized_state = dict(wait_for(
            lambda item: item.get("ps") == 7 and _selector_name(item) == "multiplayer",
            "visible multiplayer selector did not become the active one-hot control",
        ))
        normalized_png = capture_neutral("multiplayer_mode_normalized")
        record(
            "multiplayer_mode_normalize", *multiplayer_point,
            {"ps": state7.get("ps"), "selector": state7.get("selector"),
             "screenshot": selector_baseline},
            "PS remains 7 and the multiplayer selector becomes one-hot active",
            {"ps": normalized_state.get("ps"), "selector": normalized_state.get("selector"),
             "screenshot": normalized_png},
            f"PS{state7.get('ps')}->PS{normalized_state.get('ps')}; "
            f"selector {initial_selector}->{_selector_name(normalized_state)}",
            "PASS",
        )
        selector_baseline = normalized_png
        selector_baseline_state = normalized_state.get("selector")
        selector_baseline_name = _selector_name(normalized_state)
    else:
        record(
            "multiplayer_mode_normalize", *multiplayer_point,
            {"ps": state7.get("ps"), "selector": state7.get("selector"),
             "screenshot": selector_baseline},
            "initial multiplayer selector is already active; no normalization click is required",
            {"ps": state7.get("ps"), "selector": state7.get("selector"),
             "screenshot": selector_baseline},
            "initial multiplayer selector already active; click skipped",
            "SKIP",
        )

    solo_point = G1_SETUP_POINTS["solo_mode"]
    solo_before = {"ps": state7.get("ps"), "selector": selector_baseline_state,
                   "screenshot": selector_baseline}
    click("solo_mode", solo_point)
    solo_state = dict(wait_for(
        lambda item: item.get("ps") == 7 and _selector_name(item) == "solo",
        "visible solo selector did not become the active one-hot control",
    ))
    solo_after_png = capture_neutral("solo_mode_selected")
    solo_pass = _g1_selector_pass(
        initial_selector, selector_baseline_name if initial_selector == "solo" else None,
        _selector_name(solo_state), int(solo_state.get("ps", -1)),
        selector_baseline, solo_after_png,
    )
    record(
        "solo_mode_setup", *solo_point, solo_before,
        "PS remains 7, solo selector becomes one-hot active, and neutral-cursor selector capture changes",
        {"ps": solo_state.get("ps"), "selector": solo_state.get("selector"),
         "screenshot": solo_after_png},
        f"PS{state7.get('ps')}->PS{solo_state.get('ps')}; "
        f"selector {selector_baseline_name}->{_selector_name(solo_state)}",
        "PASS" if solo_pass else "FAIL",
    )
    if not solo_pass:
        raise RuntimeSafetyError("single-player setup input effect was not observed")
    return solo_state, solo_after_png, initial_selector


def _g1_confirm_endpoint_pass(
    preprocess_ps: int, lobby_ps: int, committed_mode: int, screenshot_changed: bool,
) -> bool:
    """Validate confirm's PS boundary and the post-confirm committed solo mode."""

    return preprocess_ps in {4, 5, 6} and lobby_ps == 5 and committed_mode == 1 and screenshot_changed


def _read_local_ready_state(read_memory: Callable[[int, int], bytes]) -> dict[str, int]:
    """Read the original solo auto-ready state for the active local slot."""

    local_index = struct.unpack("<I", read_memory(G1_LOCAL_PLAYER_INDEX_ADDRESS, 4))[0]
    if local_index not in G1_LOCAL_PLAYER_RANGE:
        raise RuntimeSafetyError(f"unsupported local player index: {local_index}")
    ready_address = G1_READY_STATE_BASE_ADDRESS + local_index * 4
    ready_value = struct.unpack("<I", read_memory(ready_address, 4))[0]
    if ready_value not in {0, 1}:
        raise RuntimeSafetyError(f"unsupported local ready DWORD: {ready_value}")
    return {"local_index": local_index, "ready_address": ready_address, "ready_value": ready_value}


def _g1_ready_endpoint_pass(
    lobby_ps: int,
    ready_ps: int,
    committed_mode: int,
    ready_state: Mapping[str, Any],
) -> bool:
    """Require PS5 stability and the original local slot's auto-ready state."""

    return (
        lobby_ps == 5
        and ready_ps == 5
        and committed_mode == 1
        and ready_state.get("local_index") in G1_LOCAL_PLAYER_RANGE
        and ready_state.get("ready_value") == 1
    )


def _g1_start_endpoint_pass(before_ps: int, after_state: Mapping[str, Any]) -> bool:
    """Validate the visible local-lobby start boundary PS5 -> PS3 with a live tick."""

    tick = after_state.get("tick")
    return before_ps == 5 and after_state.get("ps") == 3 and isinstance(tick, int) and tick > 0


def _module_evidence(pid: int) -> dict[str, object]:
    maps_path = Path(f"/proc/{pid}/maps")
    try:
        maps_raw = maps_path.read_bytes()
    except OSError as exc:
        raise RuntimeSafetyError(f"cannot read process maps: {exc}") from exc
    text_maps = maps_raw.decode(errors="replace")
    modules: dict[str, dict[str, Any]] = {}
    for line in text_maps.splitlines():
        fields = line.split(maxsplit=5)
        if len(fields) != 6:
            continue
        path = fields[5].strip()
        lowered = path.lower()
        if "syw2plus_original.exe" not in lowered and "ddraw" not in lowered:
            continue
        entry = modules.setdefault(path, {"path": path, "mapped_ranges": 0})
        entry["mapped_ranges"] = int(entry["mapped_ranges"]) + 1
    if not any("syw2plus_original.exe" in path.lower() for path in modules):
        raise RuntimeSafetyError("process maps do not contain the verified original EXE")
    if not any("ddraw" in path.lower() for path in modules):
        raise RuntimeSafetyError("process maps do not identify a DirectDraw module")
    for path, entry in modules.items():
        if path.startswith("["):
            entry["sha256"] = None
            entry["hash_error"] = "kernel pseudo-mapping has no file to hash"
            continue
        module = Path(path)
        if not module.is_file():
            entry["sha256"] = None
            entry["hash_error"] = "mapped path is not a regular file"
            continue
        entry["sha256"] = _sha256(module)
    unhashable = [path for path, item in modules.items() if item.get("sha256") is None]
    if unhashable:
        raise RuntimeSafetyError(f"relevant mapped module cannot be hashed: {unhashable[0]}")
    return {
        "pid": pid,
        "maps_path": str(maps_path),
        "maps_sha256": hashlib.sha256(maps_raw).hexdigest(),
        "maps_raw": text_maps,
        "modules": list(modules.values()),
        "interpretation": "verified EXE and DirectDraw-related mapped files are regular files and were rehashed",
    }


def _json_fingerprint(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def _wait_state(
    read_state: Callable[[bool], dict[str, Any]],
    predicate: Callable[[dict[str, Any]], bool],
    started: float,
    timeout: float,
    message: str,
    *,
    stage: str | None = None,
    stage_budget: float | None = None,
    stage_started: float | None = None,
    wait_observation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if stage_budget is not None and stage_budget <= 0:
        raise RuntimeSafetyError("G1 input stage budget must be positive")
    wait_started = time.monotonic()
    run_deadline = started + timeout
    stage_window_deadline = (
        wait_started + stage_budget if stage_budget is not None else run_deadline
    )
    stage_deadline = (
        min(run_deadline, stage_started + stage_budget)
        if stage_budget is not None and stage_started is not None else stage_window_deadline
    )
    natural_stage_deadline = (
        stage_started + stage_budget
        if stage_budget is not None and stage_started is not None else stage_window_deadline
    )
    run_deadline_clamped = bool(
        stage_budget is not None and stage_started is not None
        and run_deadline < natural_stage_deadline
    )
    run_deadline_clamp_seconds = (
        max(0.0, natural_stage_deadline - run_deadline)
        if run_deadline_clamped else 0.0
    )
    # `truncation_seconds` describes pre-poll work only. A run-deadline clamp
    # is recorded separately so budget exhaustion cannot contaminate the
    # observed pre-poll distribution or its threshold comparison.
    truncation_seconds = (
        max(0.0, wait_started - stage_started)
        if stage_budget is not None and stage_started is not None else 0.0
    )
    truncation_threshold_seconds = (
        stage_budget * G1_INPUT_MAX_TRUNCATION_RATIO
        if stage_budget is not None else None
    )
    truncation_ratio = (
        truncation_seconds / stage_budget
        if stage_budget is not None else None
    )
    truncation_threshold_ratio = (
        G1_INPUT_MAX_TRUNCATION_RATIO if stage_budget is not None else None
    )
    truncation_exceeds_threshold = bool(
        truncation_ratio is not None
        and truncation_threshold_ratio is not None
        and truncation_ratio > truncation_threshold_ratio
    )
    window_truncated = bool(
        stage_budget is not None and stage_started is not None
        and wait_started > stage_started
        and not run_deadline_clamped
        and truncation_exceeds_threshold
    )
    observation = wait_observation if wait_observation is not None else {}
    observation.update({
        "stage": stage,
        "stage_budget": stage_budget,
        "stage_started_elapsed": round(max(0.0, stage_started - started), 3)
        if stage_started is not None else None,
        "wait_started_elapsed": round(max(0.0, wait_started - started), 3),
        "effective_poll_window": round(max(0.0, stage_deadline - wait_started), 3),
        "run_deadline_clamped": run_deadline_clamped,
        "run_deadline_clamp_seconds": round(run_deadline_clamp_seconds, 3),
        "truncation_seconds": round(truncation_seconds, 3),
        "truncation_threshold_seconds": round(truncation_threshold_seconds, 3)
        if truncation_threshold_seconds is not None else None,
        # Keep enough precision to reconstruct the strict comparison near the
        # boundary; truncation_seconds remains a human-readable legacy field.
        "truncation_ratio": round(truncation_ratio, 9)
        if truncation_ratio is not None else None,
        "truncation_threshold_ratio": truncation_threshold_ratio,
        "truncation_exceeds_threshold": truncation_exceeds_threshold
        if stage_budget is not None else None,
        "window_truncated": window_truncated,
        "poll_count": 0,
        "poll_attempt_count": 0,
        "read_error_count": 0,
        "first_read_error_provenance": None,
        "last_read_error_provenance": None,
        "first_poll_elapsed": None,
        "last_poll_elapsed": None,
        "successful_poll_ratio": 0.0,
        "read_error_ratio": 0.0,
        "read_error_coverage_threshold_ratio": G1_INPUT_MAX_READ_ERROR_RATIO,
        "read_error_coverage_exceeds_threshold": False,
    })
    last: dict[str, Any] | None = None
    last_poll_was_read_error = False

    def update_read_coverage() -> None:
        attempts = int(observation["poll_attempt_count"])
        successes = int(observation["poll_count"])
        errors = int(observation["read_error_count"])
        if attempts <= 0:
            return
        read_error_ratio = errors / attempts
        observation["successful_poll_ratio"] = round(successes / attempts, 9)
        observation["read_error_ratio"] = round(read_error_ratio, 9)
        observation["read_error_coverage_exceeds_threshold"] = (
            read_error_ratio > G1_INPUT_MAX_READ_ERROR_RATIO
        )

    while time.monotonic() < stage_deadline:
        poll_started = time.monotonic()
        observation["poll_attempt_count"] = int(observation["poll_attempt_count"]) + 1
        poll_elapsed = round(max(0.0, poll_started - started), 3)
        try:
            current = read_state(True)
        except (OSError, ValueError, struct.error) as exc:
            provenance = f"{type(exc).__name__}: {exc}"
            observation["read_error_count"] = int(observation["read_error_count"]) + 1
            if observation["first_read_error_provenance"] is None:
                observation["first_read_error_provenance"] = provenance
            observation["last_read_error_provenance"] = provenance
            last_poll_was_read_error = True
        else:
            observation["poll_count"] = int(observation["poll_count"]) + 1
            if observation["first_poll_elapsed"] is None:
                observation["first_poll_elapsed"] = poll_elapsed
            observation["last_poll_elapsed"] = poll_elapsed
            last_poll_was_read_error = False
            last = current
            if predicate(last):
                update_read_coverage()
                finished = time.monotonic()
                observation["finished_elapsed"] = round(max(0.0, finished - started), 3)
                observation["observed_seconds"] = round(max(0.0, finished - wait_started), 3)
                observation["remaining_budget_after"] = round(
                    max(0.0, run_deadline - finished), 3,
                )
                return last
        update_read_coverage()
        time.sleep(0.25)
    finished = time.monotonic()
    remaining = max(0.0, run_deadline - finished)
    observation["finished_elapsed"] = round(max(0.0, finished - started), 3)
    observation["observed_seconds"] = round(max(0.0, finished - wait_started), 3)
    observation["remaining_budget_after"] = round(remaining, 3)
    selection_observation_corrupted = (
        isinstance(observation.get("selection_observation"), Mapping)
        and observation["selection_observation"].get("status") == "CORRUPTED"
    )
    read_observation_unavailable = (
        int(observation["read_error_count"]) > 0
        and (int(observation["poll_count"]) == 0 or last_poll_was_read_error)
    )
    read_error_coverage_insufficient = bool(
        observation["read_error_coverage_exceeds_threshold"]
    )
    if (
        (read_observation_unavailable or read_error_coverage_insufficient)
        and isinstance(observation.get("selection_observation"), Mapping)
    ):
        selection_observation = dict(observation["selection_observation"])
        # Preserve a corruption diagnosis already made by the selection
        # predicate.  Read coverage can independently make the timeout
        # UNKNOWN, but it must not hide the more specific bad observation or
        # its provenance behind UNAVAILABLE (R6-B-R12).
        if selection_observation.get("status") != "CORRUPTED":
            selection_observation["status"] = "UNAVAILABLE"
        observation["selection_observation"] = selection_observation
    classification = (
        "UNKNOWN_BUDGET_EXHAUSTED" if remaining <= 0.0
        else "UNKNOWN_OBSERVATION_WINDOW_TRUNCATED" if window_truncated
        else "UNKNOWN_STATE_READ_FAILURE" if read_observation_unavailable
        else "UNKNOWN_STATE_READ_COVERAGE" if read_error_coverage_insufficient
        else "UNKNOWN_SELECTION_OBSERVATION_CORRUPTED" if selection_observation_corrupted
        else "FAIL_NO_EFFECT"
    ) if stage is not None else None
    if classification is None:
        raise RuntimeSafetyError(message + (f"; last={last}" if last is not None else ""))
    raise _G1WaitTimeout(
        message + (f"; last={last}" if last is not None else ""),
        classification=classification,
        last=last,
        finished_elapsed=max(0.0, finished - started),
        remaining_budget_after=remaining,
        observation=observation,
    )


def _g1_r1_read_wait_state(
    read_memory: Callable[[int, int], bytes],
) -> dict[str, int]:
    """Read only the independent state fields used by the R1 gate."""

    ps_word_raw = read_memory(G1_R1_PROGRAM_STATE_ADDRESS, 2)
    if len(ps_word_raw) != 2:
        raise ValueError(f"program-state WORD read returned {len(ps_word_raw)}/2 bytes")
    ps_dword_raw = read_memory(G1_R1_PROGRAM_STATE_ADDRESS, 4)
    if len(ps_dword_raw) != 4:
        raise ValueError(f"program-state DWORD read returned {len(ps_dword_raw)}/4 bytes")
    pending_raw = read_memory(G1_R1_PENDING_STATE_ADDRESS, 2)
    if len(pending_raw) != 2:
        raise ValueError(f"pending-state WORD read returned {len(pending_raw)}/2 bytes")
    return {
        "ps": struct.unpack("<h", ps_word_raw)[0],
        "ps_word": struct.unpack("<h", ps_word_raw)[0],
        "ps_dword": struct.unpack("<i", ps_dword_raw)[0],
        "pending_state": struct.unpack("<h", pending_raw)[0],
    }


def g1_s1_load_evidence(
    fixture_path: Path, *, fixture_name: str, group_word: int, selected_index: int,
    post: Mapping[str, Any] | None = None, output: Path | None = None,
    read_memory: Callable[[int, int], bytes] | None = None,
    pre_snapshot: Mapping[str, Any] | None = None,
    post_snapshot: Mapping[str, Any] | None = None,
    trigger: Callable[[], object] | None = None,
    wait_timeout: float = G1_S1_PS3_WAIT_SECONDS,
) -> dict[str, Any]:
    """Run the isolated S1 evaluator, optionally over direct process reads.

    The no-reader form remains an offline classifier.  A production caller
    must inject the private runtime reader and one approved load trigger.  The
    event-boundary adapter then calls ``read_post_player_structs`` and reads
    ``GROUP_WORD_ADDRESS``/``PROGRAM_STATE_ADDRESS`` directly for its bounded
    pre/wait/post sequence; caller-supplied ``ps``/``open_succeeded``/raw
    strings cannot become load evidence.
    """

    from tools import s1_load_evidence

    if read_memory is None:
        result = s1_load_evidence.evaluate(
            fixture_path=fixture_path, fixture_name=fixture_name,
            group_word=group_word, selected_index=selected_index, post=post,
        )
    else:
        del pre_snapshot, post_snapshot
        if trigger is None:
            result = s1_load_evidence.evaluate(
                fixture_path=fixture_path, fixture_name=fixture_name,
                group_word=group_word, selected_index=selected_index,
                post={
                    "collector_error": {
                        "classification": "EVENT_TRIGGER_MISSING",
                        "message": "live S1 evidence requires one approved load trigger",
                    },
                    "event_boundary": {
                        "status": "UNKNOWN",
                        "classification": "EVENT_TRIGGER_MISSING",
                        "trigger_invocations": 0,
                    },
                },
            )
            if output is not None:
                s1_load_evidence._write_new_json(output, result)
            return result
        try:
            collected = s1_load_evidence.collect_load_event_boundary(
                read_memory, trigger=trigger, timeout=wait_timeout,
                player_reader=lambda reader: s1_load_evidence.read_post_player_structs(reader),
            )
            result = s1_load_evidence.evaluate(
                fixture_path=fixture_path, fixture_name=fixture_name,
                group_word=group_word, selected_index=selected_index, post=collected,
            )
        except (s1_load_evidence.S1ReadError, s1_load_evidence.S1EventBoundaryError) as exc:
            if isinstance(exc, s1_load_evidence.S1EventBoundaryError):
                error = {
                    "classification": exc.classification,
                    "message": str(exc),
                    "event_boundary": exc.boundary,
                }
                event_boundary = exc.boundary
            else:
                error = {
                    "message": str(exc), "owner": exc.owner,
                    "address": hex(exc.address), "requested": exc.requested,
                    "actual": exc.actual,
                }
                event_boundary = None
            failure_post: dict[str, Any] = {"collector_error": error}
            if event_boundary is not None:
                failure_post["event_boundary"] = event_boundary
            result = s1_load_evidence.evaluate(
                fixture_path=fixture_path, fixture_name=fixture_name,
                group_word=group_word, selected_index=selected_index,
                post=failure_post,
            )
    if output is not None:
        s1_load_evidence._write_new_json(output, result)
    return result


def _s1_stage_timeout(
    command_started: float, stage_started: float, stage_budget: float,
    *, reserve: float = G1_S1_CLEANUP_RESERVE,
) -> float:
    """Return a subprocess timeout bounded by both the stage and cleanup reserve."""

    stage_remaining = stage_budget - (time.monotonic() - stage_started)
    total_remaining = command_started + G1_S1_TOTAL_DEADLINE - time.monotonic() - reserve
    remaining = min(stage_remaining, total_remaining)
    if remaining <= 0:
        raise RuntimeSafetyError("S1 stage deadline expired before owned subprocess")
    return remaining


def _s1_file_identity(path: Path, *, expected_size: int, expected_sha256: str) -> dict[str, Any]:
    """Record a pinned file identity without following links or accepting partial files."""

    identity: dict[str, Any] = {
        "path": str(path), "expected_size": expected_size, "expected_sha256": expected_sha256,
        "actual_size": None, "actual_sha256": None, "status": "NO_RUN",
    }
    if path.is_symlink() or not path.is_file():
        identity["reason"] = "missing or linked file"
        return identity
    try:
        identity["actual_size"] = path.stat().st_size
        identity["actual_sha256"] = _sha256(path)
    except OSError as exc:
        identity["reason"] = f"identity read failed: {exc}"
        return identity
    if identity["actual_size"] != expected_size or identity["actual_sha256"] != expected_sha256:
        identity["reason"] = "pinned size/SHA mismatch"
        return identity
    identity["status"] = "PASS"
    return identity


def _s1_snapshot_sources(output: Path) -> dict[str, Any]:
    """Copy the exact Python/helper inputs into a fresh, non-overwritable snapshot."""

    snapshot_dir = output / "source_snapshot"
    snapshot_dir.mkdir()
    paths = (
        Path(__file__),
        REPO_ROOT / "tools" / "s1_load_evidence.py",
        REPO_ROOT / "tools" / "x11_mouse_click.py",
    )
    records: list[dict[str, Any]] = []
    for source in paths:
        _reject_path_links(source)
        if not source.is_file():
            raise RuntimeSafetyError(f"S1 source snapshot input is missing: {source}")
        destination = snapshot_dir / source.name
        if destination.exists() or destination.is_symlink():
            raise RuntimeSafetyError(f"refusing to overwrite S1 source snapshot: {destination}")
        shutil.copy2(source, destination)
        records.append({
            "source": str(source), "snapshot": str(destination),
            "size": destination.stat().st_size, "sha256": _sha256(destination),
        })
    return {"directory": str(snapshot_dir), "files": records}


def _s1_public_snapshot(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    """Drop the private in-process provenance token before JSON serialization."""

    return {key: value for key, value in snapshot.items() if key != "_collector_token"}


def _s1_cleanup(
    *, children: Sequence[subprocess.Popen[Any]], xvfb: subprocess.Popen[Any] | None,
    prefix: Path, env: Mapping[str, str], log_path: Path, command_started: float,
) -> dict[str, Any]:
    """Stop only this run's processes inside the fixed ten-second reserve."""

    cleanup_started = time.monotonic()
    total_deadline = command_started + G1_S1_TOTAL_DEADLINE
    cleanup_deadline = min(total_deadline, cleanup_started + G1_S1_CLEANUP_RESERVE)
    cleanup_error: str | None = None
    for child in children:
        if child.poll() is None:
            child.terminate()
    while time.monotonic() < cleanup_deadline and any(child.poll() is None for child in children):
        time.sleep(min(0.05, max(0.0, cleanup_deadline - time.monotonic())))
    for child in children:
        if child.poll() is None and time.monotonic() < cleanup_deadline:
            child.kill()
    for child in children:
        if child.poll() is None:
            continue
        try:
            remaining = cleanup_deadline - time.monotonic()
            if remaining > 0:
                child.wait(timeout=min(1.0, remaining))
        except (subprocess.TimeoutExpired, ValueError):
            pass
    try:
        remaining = cleanup_deadline - time.monotonic()
        if remaining > 0:
            _run(["wineserver", "-k"], env=env, timeout=min(5.0, remaining), log=log_path)
        remaining = cleanup_deadline - time.monotonic()
        if remaining > 0:
            _run(["wineserver", "-w"], env=env, timeout=min(5.0, remaining), log=log_path)
    except RuntimeSafetyError as exc:
        cleanup_error = str(exc)
    if xvfb is not None and xvfb.poll() is None:
        xvfb.terminate()
        try:
            remaining = cleanup_deadline - time.monotonic()
            if remaining > 0:
                xvfb.wait(timeout=min(5.0, remaining))
        except (subprocess.TimeoutExpired, ValueError):
            if xvfb.poll() is None and time.monotonic() < cleanup_deadline:
                xvfb.kill()
    residue = _prefix_pids(prefix)
    cleanup_finished = time.monotonic()
    cleanup = {
        "started_elapsed": round(cleanup_started - command_started, 3),
        "finished_elapsed": round(cleanup_finished - command_started, 3),
        "elapsed_seconds": round(cleanup_finished - cleanup_started, 3),
        "deadline_seconds": G1_S1_CLEANUP_RESERVE,
        "deadline_type": "cleanup_reserve_and_artifact_finalize",
        "total_deadline_elapsed": round(total_deadline - command_started, 3),
        "finalization_deadline_elapsed": round(cleanup_deadline - command_started, 3),
        "owned_launchers_stopped": all(child.poll() is not None for child in children),
        "xvfb_stopped": xvfb is None or xvfb.poll() is not None,
        "prefix_target": str(prefix), "global_kill_used": False,
        "prefix_processes_after": residue, "residue_pids": residue,
        "error": cleanup_error,
    }
    cleanup["ok"] = bool(cleanup["owned_launchers_stopped"] and cleanup["xvfb_stopped"]
                          and not residue and cleanup_error is None
                          and cleanup_finished <= total_deadline)
    if cleanup_finished > total_deadline and cleanup_error is None:
        cleanup["error"] = "cleanup exceeded the hard 150 second command deadline"
    return cleanup


def g1_s1_original_load_evidence(
    source: Path = DEFAULT_SOURCE, *, runtime_root: Path = DEFAULT_RUNTIME_ROOT,
) -> dict[str, Any]:
    """Own one bounded original save000 load observation from copy to cleanup.

    This is the only S1 path that launches the original game.  It creates a
    fresh private copy/prefix through :func:`prepare`, uses exactly one menu
    click for PS9->PS35 and one strict-interior load click, and writes one new
    artifact after owned cleanup.  It intentionally performs no memory writes.
    """

    from tools import s1_load_evidence as s1

    command_started = time.monotonic()
    operation_deadline = command_started + G1_S1_TOTAL_DEADLINE - G1_S1_CLEANUP_RESERVE
    fixture_spec = s1.FIXTURES["save000.dat"]
    prepare_started = command_started
    source_real, source_exe = validate_original_source(source)
    source_fixture = source_real / "save" / fixture_spec.name
    source_fixture_identity = _s1_file_identity(
        source_fixture, expected_size=fixture_spec.expected_size,
        expected_sha256=fixture_spec.expected_sha256,
    )
    if source_fixture_identity["status"] != "PASS":
        raise RuntimeSafetyError("NO_RUN: protected source save000 identity is not pinned")
    if time.monotonic() - prepare_started > G1_S1_STAGE_BUDGETS["prepare"]:
        raise RuntimeSafetyError("S1 prepare stage exceeded its 60 second cap")
    manifest = prepare(
        source_real, runtime_root=runtime_root,
        timeout=_s1_stage_timeout(command_started, prepare_started, G1_S1_STAGE_BUDGETS["prepare"]),
    )
    if time.monotonic() - prepare_started > G1_S1_STAGE_BUDGETS["prepare"]:
        raise RuntimeSafetyError("S1 prepare stage exceeded its 60 second cap")
    manifest_path = _real(Path(str(manifest["output"]["run_dir"]))) / "manifest.json"  # type: ignore[index]
    checked = check_runtime(manifest_path)
    data, game, prefix, output = _manifest(manifest_path)
    run_id = manifest_path.parent.name
    artifact_path = output / "s1_original_load_evidence.json"
    artifact_temp_path = artifact_path.with_name(f".{artifact_path.name}.tmp")
    log_path = output / "s1_original_load_evidence.log"
    evidence: dict[str, Any] = {
        "status": "UNKNOWN",
        "classification": "NOT_STARTED",
        "scope": {
            "game_started": False, "wine_started": False, "xvfb_started": False,
            "memory_writes": False, "product_g1_pass": False,
        },
        "run_id": run_id,
        "manifest": checked,
        "deadline_seconds": G1_S1_TOTAL_DEADLINE,
        "operation_deadline_seconds": G1_S1_TOTAL_DEADLINE - G1_S1_CLEANUP_RESERVE,
        "fixture": {
            "name": fixture_spec.name, "group_word": 0, "selected_index": 1,
            "synthetic": False, "resource_grant": False,
            "path": str(game / "save" / fixture_spec.name),
            "expected_size": fixture_spec.expected_size,
            "expected_sha256": fixture_spec.expected_sha256,
        },
        "source_fixture": source_fixture_identity,
        "candidate_fixture": None,
        "source_exe": _s1_file_identity(
            source_exe, expected_size=ORIGINAL_EXE_SIZE, expected_sha256=ORIGINAL_SHA256,
        ),
        "candidate_exe": None,
        "stages": {},
        "input": {
            "ps9_to_ps35": {"count": 0, "logical": list(G1_R1_CLICK_POINT)},
            "load_trigger": {"count": 0, "logical": [400, 131], "scale": [1.0, 1.0]},
        },
        "reads": {
            "program_state": {"address": hex(s1.PROGRAM_STATE_ADDRESS), "width": 2, "wait_raw": []},
            "origin": {"address": hex(G1_R1_ORIGIN_ADDRESS), "width": G1_R1_ORIGIN_READ_SIZE},
        },
        "cleanup": None,
    }
    evidence["stages"]["prepare"] = {
        "status": "PASS", "start_elapsed": round(prepare_started - command_started, 3),
        "end_elapsed": round(time.monotonic() - command_started, 3),
        "elapsed_seconds": round(time.monotonic() - prepare_started, 3),
    }
    children: list[subprocess.Popen[Any]] = []
    xvfb: subprocess.Popen[Any] | None = None
    proc: subprocess.Popen[Any] | None = None
    display = ""
    error: str | None = None
    prepared_payload: str | None = None
    log = log_path.open("a", encoding="utf-8")

    try:
        if (_prefix_pids(prefix) or _existing_state(prefix)
                or artifact_path.exists() or artifact_path.is_symlink()
                or artifact_temp_path.exists() or artifact_temp_path.is_symlink()):
            raise RuntimeSafetyError("S1 original load requires a fresh private prefix and output")
        candidate_exe = game / ORIGINAL_EXE
        candidate_fixture = game / "save" / fixture_spec.name
        evidence["candidate_exe"] = _s1_file_identity(
            candidate_exe, expected_size=source_exe.stat().st_size,
            expected_sha256=ORIGINAL_SHA256,
        )
        evidence["candidate_fixture"] = _s1_file_identity(
            candidate_fixture, expected_size=fixture_spec.expected_size,
            expected_sha256=fixture_spec.expected_sha256,
        )
        evidence["source_snapshot"] = _s1_snapshot_sources(output)
        identity_ok = (
            evidence["source_exe"]["status"] == "PASS"
            and evidence["candidate_exe"]["status"] == "PASS"
            and evidence["source_fixture"]["status"] == "PASS"
            and evidence["candidate_fixture"]["status"] == "PASS"
        )
        if not identity_ok:
            evidence.update({"status": "NO_RUN", "classification": "IDENTITY_MISMATCH"})
        else:
            env = dict(
                os.environ, WINEPREFIX=str(prefix), WINEARCH="win32", WINEDEBUG="-all",
                LANG="ko_KR.UTF-8", LC_ALL="ko_KR.UTF-8", WINEDLLOVERRIDES="ddraw=b",
            )
            launch_started = time.monotonic()
            xvfb, display = _xvfb(log, "1600x1200x24")
            evidence["scope"]["xvfb_started"] = True
            env["DISPLAY"] = display
            shell = subprocess.Popen(
                ["wine", "explorer", "/desktop=Default,1600x1200"],
                cwd=game, env=env, stdout=log, stderr=log,
            )
            children.append(shell)
            evidence["scope"]["wine_started"] = True
            proc = subprocess.Popen(
                ["wine", str(game / ORIGINAL_EXE)], cwd=game, env=env,
                stdout=log, stderr=log,
            )
            children.append(proc)
            evidence["scope"]["game_started"] = True
            from patches.population.runtime_driver import read as process_read

            def read_memory(address: int, size: int) -> bytes:
                if proc is None:
                    raise RuntimeSafetyError("S1 process was not launched")
                return process_read(proc.pid, address, size)

            wait_raw: list[dict[str, Any]] = evidence["reads"]["program_state"]["wait_raw"]

            def read_ps(_detailed: bool) -> dict[str, Any]:
                raw = read_memory(s1.PROGRAM_STATE_ADDRESS, 2)
                if len(raw) != 2:
                    raise ValueError("program-state WORD read returned a partial record")
                wait_raw.append({
                    "elapsed_seconds": round(time.monotonic() - command_started, 3),
                    "address": hex(s1.PROGRAM_STATE_ADDRESS), "width": 2, "raw_hex": raw.hex(" "),
                })
                return {"ps": int.from_bytes(raw, "little", signed=False)}

            wait_observation: dict[str, Any] = {}
            ps9_started = launch_started
            state9 = _wait_state(
                read_ps, lambda item: item.get("ps") == 9,
                command_started, G1_S1_TOTAL_DEADLINE - G1_S1_CLEANUP_RESERVE,
                "S1 original load did not reach PS=9", stage="launch_to_ps9",
                stage_budget=G1_S1_STAGE_BUDGETS["launch_to_ps9"],
                stage_started=ps9_started, wait_observation=wait_observation,
            )
            ps9_end = time.monotonic()
            evidence["stages"]["launch_to_ps9"] = {
                "status": "PASS", "state": state9, "observation": wait_observation,
                "start_elapsed": round(ps9_started - command_started, 3),
                "end_elapsed": round(ps9_end - command_started, 3),
                "elapsed_seconds": round(ps9_end - ps9_started, 3),
            }

            input_started = time.monotonic()
            tree = _window_tree(display, _s1_stage_timeout(command_started, input_started, 20.0))
            outer_id, content_id = _game_window_ids(tree)
            if content_id is None:
                raise RuntimeSafetyError("S1 original game window has no 800x600 content child")
            root_match = re.search(r"Window id: (0x[0-9a-fA-F]+) \(the root window\)", tree)
            if root_match is None:
                raise RuntimeSafetyError("S1 X11 root window id is missing")
            root_info = _xwininfo_details(display, root_match.group(1), _s1_stage_timeout(command_started, input_started, 20.0))
            content_info = _xwininfo_details(display, content_id, _s1_stage_timeout(command_started, input_started, 20.0))
            if (int(root_info["width"]), int(root_info["height"])) != (1600, 1200):
                raise RuntimeSafetyError("S1 Xvfb root is not 1600x1200")
            if (int(content_info["width"]), int(content_info["height"])) != (800, 600):
                raise RuntimeSafetyError("S1 game content crop is not exactly 800x600")
            content_crop = (int(content_info["x"]), int(content_info["y"]), 800, 600)
            first_root = [content_crop[0] + G1_R1_CLICK_POINT[0], content_crop[1] + G1_R1_CLICK_POINT[1]]
            focus = subprocess.run(
                ["xdotool", "windowfocus", outer_id], env=env, stdout=log, stderr=log,
                timeout=_s1_stage_timeout(command_started, input_started, 20.0), check=True,
            )
            first_click_argv = [sys.executable, str(REPO_ROOT / "tools/x11_mouse_click.py"), "--display", display, *map(str, first_root)]
            click = subprocess.run(
                first_click_argv, env=env, stdout=log, stderr=log,
                timeout=_s1_stage_timeout(command_started, input_started, 20.0), check=True,
            )
            evidence["input"]["ps9_to_ps35"].update({
                "count": 1, "root": first_root, "content_crop": list(content_crop),
                "target_window": outer_id, "focus_exit": focus.returncode, "inject_exit": click.returncode,
                "argv": first_click_argv,
                "helper_sha256": _sha256(REPO_ROOT / "tools" / "x11_mouse_click.py"),
            })
            ps35_started = time.monotonic()
            state35 = _wait_state(
                read_ps, lambda item: item.get("ps") == 35,
                command_started, G1_S1_TOTAL_DEADLINE - G1_S1_CLEANUP_RESERVE,
                "S1 original load did not reach PS=35", stage="input_to_ps35",
                stage_budget=G1_S1_STAGE_BUDGETS["input_to_ps35"],
                stage_started=ps35_started, wait_observation={},
            )
            input_end = time.monotonic()
            evidence["stages"]["input_to_ps35"] = {
                "status": "PASS", "state": state35,
                "start_elapsed": round(input_started - command_started, 3),
                "end_elapsed": round(input_end - command_started, 3),
                "elapsed_seconds": round(input_end - input_started, 3),
            }

            pre_started = time.monotonic()
            pre = s1.read_s1_snapshot(read_memory, phase="pre")
            origin_pre = _g1_r1_read_origin_checked(read_memory, site="s1_pre")
            pre_elapsed = time.monotonic() - pre_started
            pre_end = time.monotonic()
            evidence["stages"]["direct_pre"] = {
                "status": "PASS", "start_elapsed": round(pre_started - command_started, 3),
                "end_elapsed": round(pre_end - command_started, 3),
                "elapsed_seconds": round(pre_end - pre_started, 3),
            }
            evidence["pre"] = {"snapshot": _s1_public_snapshot(pre), "origin": origin_pre}
            if (pre.get("ps"), pre.get("group_word"), pre.get("selected_index")) != (35, 0, 1):
                raise RuntimeSafetyError("S1 direct pre did not observe PS35/group0/slot1")
            if pre_elapsed > G1_S1_STAGE_BUDGETS["direct_pre"]:
                raise RuntimeSafetyError("S1 direct pre stage exceeded its 2 second cap")

            trigger_started: float | None = None
            trigger_evidence = evidence["input"]["load_trigger"]

            def trigger() -> int:
                nonlocal trigger_started
                trigger_started = time.monotonic()
                trigger_root = [content_crop[0] + 400, content_crop[1] + 131]
                focus_result = subprocess.run(
                    ["xdotool", "windowfocus", outer_id], env=env, stdout=log, stderr=log,
                    timeout=_s1_stage_timeout(command_started, trigger_started, G1_S1_STAGE_BUDGETS["load_trigger"]), check=True,
                )
                trigger_argv = [sys.executable, str(REPO_ROOT / "tools/x11_mouse_click.py"), "--display", display, *map(str, trigger_root)]
                click_result = subprocess.run(
                    trigger_argv, env=env, stdout=log, stderr=log,
                    timeout=_s1_stage_timeout(command_started, trigger_started, G1_S1_STAGE_BUDGETS["load_trigger"]), check=True,
                )
                trigger_evidence.update({
                    "count": 1, "root": trigger_root, "content_crop": list(content_crop),
                    "target_window": outer_id, "focus_exit": focus_result.returncode,
                    "inject_exit": click_result.returncode, "argv": trigger_argv,
                    "helper_sha256": _sha256(REPO_ROOT / "tools" / "x11_mouse_click.py"),
                    "invocation_count": 1,
                    "stage_start_elapsed": round(trigger_started - command_started, 3),
                    "stage_end_elapsed": round(time.monotonic() - command_started, 3),
                    "stage_elapsed_seconds": round(time.monotonic() - trigger_started, 3),
                })
                trigger_elapsed = time.monotonic() - trigger_started
                if trigger_elapsed > G1_S1_STAGE_BUDGETS["load_trigger"]:
                    raise RuntimeSafetyError(
                        f"S1 load trigger stage exceeded its {G1_S1_STAGE_BUDGETS['load_trigger']} second cap"
                    )
                if time.monotonic() > operation_deadline:
                    raise RuntimeSafetyError("S1 load trigger exceeded the operation deadline")
                return 1

            def precondition(sample: Mapping[str, Any]) -> Mapping[str, Any]:
                if (sample.get("ps"), sample.get("group_word"), sample.get("selected_index")) != (35, 0, 1):
                    raise RuntimeSafetyError("S1 precondition changed before load trigger")
                return {"ps": 35, "group_word": 0, "selected_index": 1, "origin": origin_pre}

            collected = s1.collect_load_event_boundary(
                read_memory, trigger=trigger, timeout=G1_S1_STAGE_BUDGETS["ps3_wait"],
                precondition=precondition, pre_snapshot=pre, event_started=pre_started,
                event_deadline=operation_deadline,
                post_timeout=G1_S1_STAGE_BUDGETS["post_finalize"],
            )
            evidence["event_boundary"] = collected["event_boundary"]
            evidence["post"] = _s1_public_snapshot(collected["post"])
            post_started = float(collected["event_boundary"].get("post_started", time.monotonic()))
            ps3_end = time.monotonic()
            trigger_elapsed_start = trigger_started if trigger_started is not None else ps3_end
            boundary_wait_start = trigger_started if trigger_started is not None else post_started
            wait_elapsed = ps3_end - trigger_elapsed_start
            boundary_wait_elapsed = post_started - boundary_wait_start
            if boundary_wait_elapsed > G1_S1_STAGE_BUDGETS["ps3_wait"]:
                raise RuntimeSafetyError(
                    f"S1 PS3 wait stage exceeded its {G1_S1_STAGE_BUDGETS['ps3_wait']} second cap"
                )
            evidence["stages"]["ps3_wait"] = {
                "status": "PASS", "wait": collected["event_boundary"].get("wait_ps", []),
                "start_elapsed": round(trigger_started - command_started, 3) if trigger_started is not None else None,
                "end_elapsed": round(post_started - command_started, 3),
                "elapsed_seconds": round(boundary_wait_elapsed, 3),
                "post_snapshot_elapsed_seconds": round(wait_elapsed - boundary_wait_elapsed, 3),
            }
            result = s1.evaluate(
                fixture_path=candidate_fixture, fixture_name=fixture_spec.name,
                group_word=0, selected_index=1, post=collected,
            )
            evidence["evaluation"] = result
            for key in ("fixture_identity", "fixture_players", "pre_ps3_players", "post_ps3_players",
                        "load", "reader", "reason", "failures"):
                if key in result:
                    evidence[key] = result[key]
            evidence["status"] = result.get("status", "UNKNOWN")
            evidence["classification"] = result.get("classification", "UNKNOWN")
            # Prepare the payload while the post-finalize clock is still open.
            # Cleanup is deliberately added later so the final artifact cannot
            # exist before owned teardown has completed.
            prepared_payload = s1.prepare_json_payload(evidence)
            post_end = time.monotonic()
            post_elapsed = post_end - post_started
            if post_elapsed > G1_S1_STAGE_BUDGETS["post_finalize"]:
                raise RuntimeSafetyError(
                    f"S1 post/evaluate/payload stage exceeded its {G1_S1_STAGE_BUDGETS['post_finalize']} second cap"
                )
            if post_end > operation_deadline:
                raise RuntimeSafetyError("S1 post/evaluate/payload stage exceeded the operation deadline")
            evidence["stages"]["post_finalize"] = {
                "status": "PASS" if result.get("status") == "PASS" else "UNKNOWN",
                "start_elapsed": round(post_started - command_started, 3),
                "end_elapsed": round(post_end - command_started, 3),
                "elapsed_seconds": round(post_elapsed, 3),
                "includes": ["post_snapshot", "evaluate", "payload_prepare"],
                "payload_bytes": len(prepared_payload.encode("utf-8")),
            }
    except (OSError, subprocess.SubprocessError, RuntimeSafetyError, ValueError, struct.error,
            s1.S1ReadError, s1.S1EventBoundaryError) as exc:
        error = f"{type(exc).__name__}: {exc}"
        evidence.setdefault("failure", {})
        evidence["failure"].update({"error": error, "last_raw": evidence["reads"]["program_state"].get("wait_raw", [])[-1:]})
        if isinstance(exc, s1.S1EventBoundaryError):
            evidence["event_boundary"] = exc.boundary
            evidence["classification"] = exc.classification
        elif isinstance(exc, _G1WaitTimeout):
            evidence["classification"] = exc.classification
            evidence["wait_observation"] = exc.observation
        elif isinstance(exc, _G1R1CollectionError):
            evidence["classification"] = "COLLECTION_ERROR"
            evidence["collection_error"] = exc.diagnostics
        elif evidence.get("classification") == "NOT_STARTED":
            evidence["classification"] = "UNKNOWN"
        if isinstance(exc, RuntimeSafetyError):
            evidence["status"] = "UNKNOWN"
            if evidence.get("classification") in {"NOT_STARTED", "UNKNOWN"}:
                evidence["classification"] = "STAGE_FAILURE"
    finally:
        try:
            cleanup = _s1_cleanup(
                children=children, xvfb=xvfb, prefix=prefix,
                env=env if "env" in locals() else {"WINEPREFIX": str(prefix)},
                log_path=log_path, command_started=command_started,
            )
        except Exception as exc:
            cleanup = {
                "ok": False, "error": f"{type(exc).__name__}: {exc}",
                "deadline_type": "cleanup_reserve_and_artifact_finalize",
                "prefix_target": str(prefix), "residue_pids": _prefix_pids(prefix),
            }
        evidence["cleanup"] = cleanup
        evidence["elapsed_seconds"] = round(time.monotonic() - command_started, 3)
        evidence["provenance"] = {
            "manifest_sha256": _sha256(manifest_path), "display": display,
            "prefix": str(prefix), "game_root": str(game),
            "environment": {key: (env.get(key) if "env" in locals() else None)
                             for key in ("DISPLAY", "WINEPREFIX", "WINEARCH", "LANG", "LC_ALL", "WINEDLLOVERRIDES")},
            "harness_sha256": {
                "tools/runtime_env.py": _sha256(Path(__file__)),
                "tools/s1_load_evidence.py": _sha256(REPO_ROOT / "tools" / "s1_load_evidence.py"),
                "tools/x11_mouse_click.py": _sha256(REPO_ROOT / "tools" / "x11_mouse_click.py"),
            },
            "command": "runtime_env.py g1-s1-original-load-evidence",
            "observational_only": True,
        }
        if not cleanup.get("ok", False):
            prior_status = evidence.get("status")
            evidence["status"] = "UNKNOWN"
            evidence["classification"] = "CLEANUP_FAILURE"
            evidence.setdefault("failure", {})["cleanup"] = {
                "prior_status": prior_status,
                "cleanup": cleanup,
                "residue_pids": cleanup.get("residue_pids", cleanup.get("prefix_processes_after", [])),
            }
            error = error or (
                "S1 cleanup failed: "
                f"{cleanup.get('error') or 'owned teardown did not complete'}"
            )
        try:
            log.close()
        except OSError:
            pass
        cleanup_artifact_deadline = cleanup.get("finalization_deadline_elapsed")
        if not isinstance(cleanup_artifact_deadline, (int, float)):
            cleanup_artifact_deadline = G1_S1_TOTAL_DEADLINE
        final_deadline = command_started + float(cleanup_artifact_deadline)
        final_started = time.monotonic()
        try:
            if final_started > final_deadline:
                raise RuntimeSafetyError("S1 final artifact deadline expired; final artifact was not installed")
            # Re-serialize after cleanup so the one installed artifact contains
            # cleanup/residue/deadline evidence.  The pre-cleanup serialization
            # above is the payload part of the three-second post window.
            evidence["artifact"] = {
                "path": str(artifact_path), "status": "INSTALLED",
                "install_count": 1,
            }
            final_payload = s1.prepare_json_payload(evidence)
            if time.monotonic() > final_deadline:
                raise RuntimeSafetyError("S1 final artifact deadline expired during payload finalization")
            s1._install_new_json_payload(artifact_path, final_payload, deadline=final_deadline)
            if time.monotonic() > final_deadline:
                # The installer also enforces this, but keep the command
                # boundary fail-closed if a test or alternate installer does
                # not honor the optional deadline.
                if artifact_path.is_file() and not artifact_path.is_symlink():
                    artifact_path.unlink()
                raise RuntimeSafetyError("S1 final artifact deadline expired during atomic install")
            evidence["artifact"]["elapsed_seconds"] = round(time.monotonic() - final_started, 3)
        except (OSError, TimeoutError, FileExistsError) as exc:
            error = error or f"artifact finalization failed: {exc}"
            evidence["status"] = "UNKNOWN"
            evidence["classification"] = "ARTIFACT_FINALIZATION_FAILURE"
            evidence.setdefault("failure", {})["artifact"] = {
                "error": str(exc), "path": str(artifact_path),
                "temporary_path": str(artifact_temp_path),
                "deadline_type": "hard_total_deadline",
            }
        except RuntimeSafetyError as exc:
            error = error or str(exc)
            evidence["status"] = "UNKNOWN"
            evidence["classification"] = "ARTIFACT_FINALIZATION_FAILURE"
            evidence.setdefault("failure", {})["artifact"] = {
                "error": str(exc), "path": str(artifact_path),
                "temporary_path": str(artifact_temp_path),
                "deadline_type": "hard_total_deadline",
            }
    if error is not None:
        raise RuntimeSafetyError(error)
    return evidence


def _g1_r1_read_origin(
    read_memory: Callable[[int, int], bytes],
) -> dict[str, int]:
    """Read x, y, and tag as one contiguous six-byte observation."""

    raw = read_memory(G1_R1_ORIGIN_ADDRESS, G1_R1_ORIGIN_READ_SIZE)
    if len(raw) != G1_R1_ORIGIN_READ_SIZE:
        raise ValueError(
            f"origin sample read returned {len(raw)}/{G1_R1_ORIGIN_READ_SIZE} bytes"
        )
    x, y, tag = struct.unpack("<hhh", raw)
    return {"x": x, "y": y, "tag": tag}


def _g1_r1_origin_error_diagnostics(exc: BaseException, *, site: str) -> dict[str, Any]:
    """Preserve read failure shape without treating a partial sample as data."""

    message = str(exc)
    actual_match = re.search(r"(?:got|returned)\s+(-?\d+)/(\d+)", message)
    actual_size = int(actual_match.group(1)) if actual_match is not None else None
    requested_size = int(actual_match.group(2)) if actual_match is not None else G1_R1_ORIGIN_READ_SIZE
    return {
        "errno": exc.errno if isinstance(exc, OSError) else None,
        "requested_size": requested_size,
        "actual_size": actual_size,
        "site": {
            "address": hex(G1_R1_ORIGIN_ADDRESS),
            "function": "_g1_r1_read_origin",
            "phase": site,
        },
        "exception_type": type(exc).__name__,
        "message": message,
    }


def _g1_r1_read_origin_checked(
    read_memory: Callable[[int, int], bytes], *, site: str,
) -> dict[str, int]:
    """Read an R1 origin sample and expose collection failures as structured errors."""

    try:
        return _g1_r1_read_origin(read_memory)
    except (OSError, ValueError, struct.error) as exc:
        raise _G1R1CollectionError(
            site=site,
            original_error=str(exc),
            diagnostics=_g1_r1_origin_error_diagnostics(exc, site=site),
        ) from exc


def _g1_r1_failure_record(
    *,
    mode: str,
    reason: str,
    observation: Mapping[str, Any] | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    """Build a conservative R1 failure record without treating it as PASS."""

    record: dict[str, Any] = {
        "status": "UNKNOWN",
        "classification": mode,
        "reason": reason,
    }
    if observation is not None:
        record["observation"] = dict(observation)
    if error is not None:
        record["error"] = error
    return record


def _g1_r1_wait_failure_record(exc: _G1WaitTimeout) -> dict[str, Any]:
    """Map shared wait classifications to the R1 four-mode vocabulary."""

    mode = "TIMEOUT" if exc.classification == "UNKNOWN_BUDGET_EXHAUSTED" else (
        "COLLECTION_ERROR" if "READ" in exc.classification else "UNREACHED"
    )
    return _g1_r1_failure_record(
        mode=mode,
        reason="R1 wait ended without a valid target observation",
        observation=exc.observation,
        error=str(exc),
    )


def _g1_r1_collection_failure_record(
    exc: _G1R1CollectionError, *, evidence: Mapping[str, Any],
) -> dict[str, Any]:
    """Record an origin collection error while retaining the surrounding evidence."""

    observation = dict(evidence)
    observation["collection_error"] = exc.diagnostics
    return _g1_r1_failure_record(
        mode="COLLECTION_ERROR",
        reason=f"R1 {exc.site} origin read failed",
        observation=observation,
        error=exc.original_error,
    )


def _g1_r1_compare_origin(
    pre: Mapping[str, Any], post: Mapping[str, Any],
) -> dict[str, Any]:
    """Classify the gated post sample; unchanged zero origin stays UNKNOWN."""

    pre_values = [pre.get("x"), pre.get("y"), pre.get("tag")]
    post_values = [post.get("x"), post.get("y"), post.get("tag")]
    unchanged = pre_values == post_values
    zero_unchanged = unchanged and post_values == [0, 0, 0]
    if zero_unchanged:
        return _g1_r1_failure_record(
            mode="REACHED_UNCHANGED",
            reason="PS=35 was observed but the gated origin sample stayed at pre=(0,0,0)",
            observation={"pre": pre_values, "post": post_values},
        )
    if unchanged:
        return _g1_r1_failure_record(
            mode="REACHED_UNCHANGED",
            reason="PS=35 was observed but the gated origin sample did not change",
            observation={"pre": pre_values, "post": post_values},
        )
    return {
        "status": "OBSERVED",
        "classification": "REACHED_CHANGED",
        "observation": {"pre": pre_values, "post": post_values},
    }


def _g1_r1_candidate_geometry_gate(
    root_info: Mapping[str, Any], content_info: Mapping[str, Any],
) -> dict[str, Any]:
    """Require a 1600x1200 root and a 1600x1200 physical logical surface."""

    root_size = [root_info.get("width"), root_info.get("height")]
    content_size = [content_info.get("width"), content_info.get("height")]
    if root_size != [1600, 1200]:
        raise _G1R1CandidatePreconditionError(
            "candidate root geometry is not 1600x1200",
            details={"root": dict(root_info), "content_child": dict(content_info)},
        )
    if content_size != [1600, 1200]:
        raise _G1R1CandidatePreconditionError(
            "candidate content child is not 1600x1200",
            details={"root": dict(root_info), "content_child": dict(content_info)},
        )
    return {
        "root": dict(root_info),
        "content_child": dict(content_info),
        "physical_size": [1600, 1200],
        "logical_size": [800, 600],
        "scale": [2.0, 2.0],
        "content_crop": {
            "x": int(content_info["x"]), "y": int(content_info["y"]),
            "width": 1600, "height": 1200,
        },
    }


def _g1_r1_candidate_click_geometry(
    content_crop: tuple[int, int, int, int],
) -> dict[str, object]:
    """Record the logical R1 point without applying the presentation scale."""

    if content_crop[2:] != (1600, 1200):
        raise _G1R1CandidatePreconditionError(
            "candidate input crop is not 1600x1200",
            details={"content_crop": list(content_crop)},
        )
    geometry = _g1_input_geometry(content_crop, (2.0, 2.0), *G1_R1_CLICK_POINT)
    geometry["scale_applied"] = [1.0, 1.0]
    return geometry


def _g1_r1_candidate_module_gate(
    module_evidence: Mapping[str, Any], game: Path,
    support_hashes: Mapping[str, Any],
) -> dict[str, Any]:
    """Require the private ddraw.dll and reject a loaded syw2x.dll."""

    modules = module_evidence.get("modules")
    if not isinstance(modules, list):
        raise _G1R1CandidatePreconditionError(
            "candidate module evidence has no module list",
            details={"module_evidence": dict(module_evidence)},
        )
    maps_raw = str(module_evidence.get("maps_raw", "")).lower()
    if "syw2x.dll" in maps_raw:
        raise _G1R1CandidatePreconditionError(
            "candidate loaded the forbidden syw2x.dll",
            details={"module_evidence": dict(module_evidence)},
        )
    ddraw = [item for item in modules if isinstance(item, Mapping)
             and "ddraw" in str(item.get("path", "")).lower()]
    private_ddraw = _real(game / "ddraw.dll")
    if len(ddraw) != 1:
        raise _G1R1CandidatePreconditionError(
            "candidate module gate did not find exactly one DirectDraw module",
            details={"ddraw_modules": ddraw},
        )
    loaded_path = _real(Path(str(ddraw[0]["path"])))
    expected_hash = support_hashes.get("ddraw.dll")
    if loaded_path != private_ddraw or ddraw[0].get("sha256") != expected_hash:
        raise _G1R1CandidatePreconditionError(
            "candidate DirectDraw module is not the private verified ddraw.dll",
            details={"loaded": dict(ddraw[0]), "expected_path": str(private_ddraw),
                     "expected_sha256": expected_hash},
        )
    return {
        "status": "PASS",
        "private_ddraw": str(private_ddraw),
        "private_ddraw_sha256": ddraw[0].get("sha256"),
        "syw2x_loaded": False,
        "modules": [dict(item) for item in modules if isinstance(item, Mapping)],
    }


def _g1_r1_candidate_wait_failure_record(exc: _G1WaitTimeout) -> dict[str, Any]:
    """Map shared waits to the candidate envelope's public failure vocabulary."""

    if exc.classification == "UNKNOWN_BUDGET_EXHAUSTED":
        mode = "TIMEOUT"
    elif "READ" in exc.classification:
        mode = "COLLECTION_ERROR"
    else:
        mode = "NOT_REACHED"
    return _g1_r1_failure_record(
        mode=mode, reason="candidate R1 wait ended without a valid target observation",
        observation=exc.observation, error=str(exc),
    )


def _g1_r1_candidate_precondition_record(
    exc: _G1R1CandidatePreconditionError,
) -> dict[str, Any]:
    """Record a candidate gate failure without allowing a click or a pass."""

    return _g1_r1_failure_record(
        mode="BLOCKED_PRECONDITION", reason=exc.reason,
        observation=exc.details, error=str(exc),
    )


def _g1_r1_candidate_compare_origin(
    pre: Mapping[str, Any], post: Mapping[str, Any],
) -> dict[str, Any]:
    """Use the original comparison, exposing unchanged results as NO_CHANGE."""

    result = _g1_r1_compare_origin(pre, post)
    if result.get("classification") == "REACHED_UNCHANGED":
        result["classification"] = "NO_CHANGE"
    return result


def _g1_r1_candidate_cleanup_record(
    *, owned_launchers_stopped: bool, xvfb_stopped: bool,
    prefix_target: Path, prefix_processes_after: list[int], cleanup_error: str | None,
    dxwrapper_config_restored: bool, dxwrapper_config_error: str | None = None,
) -> dict[str, Any]:
    """Build the candidate cleanup contract without weakening failed restores."""

    cleanup: dict[str, Any] = {
        "owned_launchers_stopped": owned_launchers_stopped,
        "xvfb_stopped": xvfb_stopped,
        "prefix_target": str(prefix_target),
        "global_kill_used": False,
        "prefix_processes_after": list(prefix_processes_after),
        "error": cleanup_error,
        "dxwrapper_config_restored": dxwrapper_config_restored,
    }
    if dxwrapper_config_error is not None:
        cleanup["dxwrapper_config_error"] = dxwrapper_config_error
    cleanup["ok"] = bool(
        owned_launchers_stopped and xvfb_stopped and not prefix_processes_after
        and cleanup_error is None and dxwrapper_config_restored
        and dxwrapper_config_error is None
    )
    return cleanup


def g1_r1_candidate_load_origin(
    manifest_path: Path, *, screen: str = "1600x1200x24", timeout: float = 90,
) -> dict[str, Any]:
    """Run the bounded candidate-dxwrapper R1 observation exactly once."""

    if timeout <= 0 or timeout > 90:
        raise RuntimeSafetyError(
            "g1-r1-candidate-load-origin timeout must be between 1 and 90 seconds"
        )
    if screen != "1600x1200x24":
        raise RuntimeSafetyError(
            "g1-r1-candidate-load-origin requires the fixed 1600x1200x24 screen"
        )
    checked = check_runtime(manifest_path)
    data, game, prefix, output = _manifest(manifest_path)
    wine_data = data.get("wine")
    game_data = data.get("game")
    if not isinstance(wine_data, dict) or wine_data.get("created_new") is not True:
        raise RuntimeSafetyError("candidate R1 requires a newly prepared manifest")
    if not isinstance(game_data, dict):
        raise RuntimeSafetyError("candidate R1 requires a valid game manifest")
    artifact_path = output / "r1_load_origin_candidate.json"
    if _prefix_pids(prefix) or _existing_state(prefix) or artifact_path.exists():
        raise RuntimeSafetyError("candidate R1 requires an unused private prefix and output")
    output.mkdir(parents=True, exist_ok=True)
    lock_path = output.parent / ".r1-load-origin-candidate.lock"
    lock = lock_path.open("a+", encoding="utf-8")
    try:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
        lock.close()
        raise RuntimeSafetyError("candidate R1 already owns this prefix") from exc

    log_path = output / "r1_load_origin_candidate.log"
    log = log_path.open("a", encoding="utf-8")
    run_id = _real(manifest_path).parent.name + "-candidate"
    started = time.monotonic()
    env = dict(
        os.environ, WINEPREFIX=str(prefix), WINEARCH="win32", WINEDEBUG="-all",
        LANG="ko_KR.UTF-8", LC_ALL="ko_KR.UTF-8", WINEDLLOVERRIDES="ddraw=n,b",
    )
    children: list[subprocess.Popen[Any]] = []
    xvfb: subprocess.Popen[Any] | None = None
    proc: subprocess.Popen[Any] | None = None
    display = ""
    error: str | None = None
    dxwrapper_install: dict[str, object] | None = None
    dxwrapper_uninstall: dict[str, object] | None = None
    dxwrapper_cleanup_error: str | None = None
    stage_timeline: dict[str, dict[str, float]] = {}
    pending_samples: list[dict[str, Any]] = []
    evidence: dict[str, Any] = {
        "variant": "candidate-dxwrapper-2x",
        "status": "UNKNOWN",
        "classification": "NOT_STARTED",
        "manifest": checked,
        "run_id": run_id,
        "screen": screen,
        "timeout_seconds": timeout,
        "fixture": {
            "kind": "new private copy; default two-player random game",
            "synthetic": False, "memory_writes": False, "resource_grant": False,
        },
        "addresses": {
            "program_state_word": hex(G1_R1_PROGRAM_STATE_ADDRESS),
            "pending_state_word": hex(G1_R1_PENDING_STATE_ADDRESS),
            "origin_x_y_tag": hex(G1_R1_ORIGIN_ADDRESS),
        },
        "wait_ps_states": list(G1_R1_WAIT_PS_STATES),
        "input": {
            "client": list(G1_R1_CLICK_POINT), "root": None,
            "scale_applied": [1.0, 1.0], "count": 0,
        },
        "pending_state": pending_samples,
        "ps_word": [], "ps_dword": [],
        "origin_tag": {"pre": None, "post": None},
        "stage_timeline": stage_timeline,
        "dxwrapper_config": {
            "enabled": True, "winedlloverrides": "ddraw=n,b",
            "ini_original_sha256": None, "ini_candidate_sha256": None,
        },
    }

    def stage_start(name: str) -> float:
        value = time.monotonic()
        stage_timeline[name] = {"started_elapsed": round(value - started, 3)}
        return value

    def stage_end(name: str, value: float) -> None:
        ended = time.monotonic()
        stage_timeline[name].update({
            "ended_elapsed": round(ended - started, 3),
            "duration_seconds": round(max(0.0, ended - value), 3),
        })

    def preserve_failure(mode: str, reason: str, *, observation: Mapping[str, Any] | None = None) -> None:
        evidence.update(_g1_r1_failure_record(
            mode=mode, reason=reason, observation=observation, error=error,
        ))

    try:
        from patches.resolution import dxwrapper_config

        install_started = stage_start("prepare_and_install")
        evidence["dxwrapper_config"]["ini_original_sha256"] = _sha256(game / "dxwrapper.ini")
        dxwrapper_install = dxwrapper_config.install_private(game)
        evidence["dxwrapper_config"]["install"] = dxwrapper_install
        evidence["dxwrapper_config"]["ini_candidate_sha256"] = dxwrapper_install["patched_sha256"]
        stage_end("prepare_and_install", install_started)

        launch_started = stage_start("launch_and_ps9")
        xvfb, display = _xvfb(log, screen)
        env["DISPLAY"] = display
        shell = subprocess.Popen(
            ["wine", "explorer", "/desktop=Default,1600x1200"],
            cwd=game, env=env, stdout=log, stderr=log,
        )
        children.append(shell)
        time.sleep(1)
        _remaining(started, timeout)
        proc = subprocess.Popen(
            ["wine", str(game / ORIGINAL_EXE)], cwd=game, env=env,
            stdout=log, stderr=log,
        )
        children.append(proc)
        if str(REPO_ROOT) not in sys.path:
            sys.path.insert(0, str(REPO_ROOT))
        from patches.population.runtime_driver import read as read_memory

        def read_for_process(address: int, size: int) -> bytes:
            return read_memory(proc.pid, address, size)  # type: ignore[union-attr]

        def read_wait_state(_detailed: bool) -> dict[str, Any]:
            current = _g1_r1_read_wait_state(read_for_process)
            elapsed = round(time.monotonic() - started, 3)
            sample = {
                "elapsed_seconds": elapsed,
                "ps_word": current["ps_word"],
                "ps_dword": current["ps_dword"],
                "pending_state": current["pending_state"],
            }
            pending_samples.append(sample)
            evidence["ps_word"].append({"elapsed_seconds": elapsed, "value": current["ps_word"]})
            evidence["ps_dword"].append({"elapsed_seconds": elapsed, "value": current["ps_dword"]})
            return current

        wait_observation: dict[str, Any] = {}
        state9 = _wait_state(
            read_wait_state, lambda item: item.get("ps") == G1_R1_WAIT_PS_STATES[0],
            started, timeout, "candidate R1 did not reach PS=9", stage="candidate_ps9",
            stage_budget=G1_R1_PS9_STAGE_BUDGET, stage_started=started,
            wait_observation=wait_observation,
        )
        pre = _g1_r1_read_origin_checked(read_for_process, site="pre")
        evidence["pre"] = {"state": state9, "origin": pre}
        evidence["origin_tag"]["pre"] = pre["tag"]
        if [pre["x"], pre["y"], pre["tag"]] != [0, 0, 0]:
            raise _G1R1CandidatePreconditionError(
                "candidate PS=9 origin was not (0,0,0)",
                details={"expected": [0, 0, 0], "observed": [pre["x"], pre["y"], pre["tag"]]},
            )
        stage_end("launch_and_ps9", launch_started)

        gate_started = stage_start("geometry_and_module_gate")
        try:
            module_evidence = _module_evidence(proc.pid)  # type: ignore[union-attr]
        except RuntimeSafetyError as exc:
            raise _G1R1CandidatePreconditionError(
                "candidate module gate could not verify the mapped modules",
                details={"error": str(exc)},
            ) from exc
        evidence["modules"] = module_evidence
        evidence["module_gate"] = _g1_r1_candidate_module_gate(
            module_evidence, game, game_data.get("support_dll_sha256", {})
            if isinstance(game_data.get("support_dll_sha256"), Mapping) else {},
        )
        tree = _window_tree(display, _remaining(started, timeout))
        outer_id, content_id = _game_window_ids(tree, allowed_sizes=((1600, 1200),))
        if content_id is None:
            raise _G1R1CandidatePreconditionError(
                "candidate 1600x1200 game window has no 1600x1200 content child",
                details={"outer_id": outer_id, "tree_sha256": hashlib.sha256(tree.encode()).hexdigest()},
            )
        root_match = re.search(r"Window id: (0x[0-9a-fA-F]+) \(the root window\)", tree)
        if not root_match:
            raise _G1R1CandidatePreconditionError(
                "candidate X11 tree has no root window", details={"tree_sha256": hashlib.sha256(tree.encode()).hexdigest()}
            )
        root_info = _xwininfo_details(display, root_match.group(1), _remaining(started, timeout))
        content_info = _xwininfo_details(display, content_id, _remaining(started, timeout))
        evidence["window"] = _g1_r1_candidate_geometry_gate(root_info, content_info)
        evidence["window"]["tree_sha256"] = hashlib.sha256(tree.encode()).hexdigest()
        content_crop = (
            int(content_info["x"]), int(content_info["y"]), 1600, 1200,
        )
        stage_end("geometry_and_module_gate", gate_started)

        input_started = stage_start("click_and_ps35")
        focus = subprocess.run(
            ["xdotool", "windowfocus", outer_id], env=env, stdout=log,
            stderr=log, timeout=min(10, _remaining(started, timeout)), check=True,
        )
        click_geometry = _g1_r1_candidate_click_geometry(content_crop)
        x11 = click_geometry.get("x11")
        if not isinstance(x11, list) or len(x11) != 2 or not all(isinstance(value, int) for value in x11):
            raise RuntimeSafetyError("candidate click geometry has no integer root coordinates")
        root_x, root_y = x11
        click = subprocess.run(
            [sys.executable, str(REPO_ROOT / "tools/x11_mouse_click.py"), "--display", display,
             str(root_x), str(root_y)], env=env, stdout=log, stderr=log,
            timeout=min(10, _remaining(started, timeout)), check=True,
        )
        evidence["input"].update({
            **click_geometry, "root": [root_x, root_y], "target_window": outer_id,
            "focus_exit": focus.returncode, "inject_exit": click.returncode, "count": 1,
        })
        wait_observation = {}
        ps35_started = time.monotonic()
        state35 = _wait_state(
            read_wait_state, lambda item: item.get("ps") == G1_R1_WAIT_PS_STATES[1],
            started, timeout, "candidate R1 click did not reach PS=35", stage="candidate_ps35",
            stage_budget=G1_R1_PS35_STAGE_BUDGET, stage_started=ps35_started,
            wait_observation=wait_observation,
        )
        post = _g1_r1_read_origin_checked(read_for_process, site="post")
        evidence["post"] = {"state": state35, "origin": post}
        evidence["origin_tag"]["post"] = post["tag"]
        evidence.update(_g1_r1_candidate_compare_origin(pre, post))
        stage_end("click_and_ps35", input_started)
    except _G1WaitTimeout as exc:
        error = str(exc)
        evidence["wait_observation"] = exc.observation
        evidence.update(_g1_r1_candidate_wait_failure_record(exc))
    except _G1R1CollectionError as exc:
        error = exc.original_error
        evidence.update(_g1_r1_collection_failure_record(exc, evidence=evidence))
    except _G1R1CandidatePreconditionError as exc:
        error = str(exc)
        evidence.update(_g1_r1_candidate_precondition_record(exc))
    except (OSError, subprocess.SubprocessError, RuntimeSafetyError, ValueError, struct.error) as exc:
        error = str(exc)
        mode = "TIMEOUT" if time.monotonic() >= started + timeout else "COLLECTION_ERROR"
        preserve_failure(mode, "candidate R1 observation failed before a valid result", observation=evidence)
    finally:
        cleanup_started = stage_start("cleanup")
        for child in children:
            if child.poll() is None:
                child.terminate()
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline and any(child.poll() is None for child in children):
            time.sleep(0.05)
        for child in children:
            if child.poll() is None:
                child.kill()
        for child in children:
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass
        cleanup_error: str | None = None
        try:
            _run(["wineserver", "-k"], env=env, timeout=10, log=log_path)
            _run(["wineserver", "-w"], env=env, timeout=10, log=log_path)
        except RuntimeSafetyError as exc:
            cleanup_error = str(exc)
        if dxwrapper_install is not None:
            try:
                from patches.resolution import dxwrapper_config

                dxwrapper_uninstall = dxwrapper_config.uninstall_private(game)
                evidence["dxwrapper_config"]["uninstall"] = dxwrapper_uninstall
            except (OSError, ValueError) as exc:
                dxwrapper_cleanup_error = str(exc)
        try:
            _preserve_dxwrapper_logs(game, output, evidence["dxwrapper_config"])
        except OSError as exc:
            evidence["dxwrapper_config"]["wrapper_logs_error"] = str(exc)
            if error is None:
                error = f"candidate dxwrapper log capture failed: {exc}"
        if xvfb is not None and xvfb.poll() is None:
            xvfb.terminate()
            try:
                xvfb.wait(timeout=5)
            except subprocess.TimeoutExpired:
                xvfb.kill()
        cleanup = _g1_r1_candidate_cleanup_record(
            owned_launchers_stopped=all(child.poll() is not None for child in children),
            xvfb_stopped=xvfb is None or xvfb.poll() is not None,
            prefix_target=prefix, prefix_processes_after=_prefix_pids(prefix),
            cleanup_error=cleanup_error,
            dxwrapper_config_restored=dxwrapper_install is None or dxwrapper_uninstall is not None,
            dxwrapper_config_error=dxwrapper_cleanup_error,
        )
        evidence["cleanup"] = cleanup
        stage_end("cleanup", cleanup_started)
        evidence["elapsed_seconds"] = round(time.monotonic() - started, 3)
        if not cleanup["ok"] and error is None:
            error = "candidate R1 cleanup incomplete; inspect r1_load_origin_candidate.json"
        if error is not None:
            evidence["error"] = error
        evidence["provenance"] = {
            "manifest_sha256": _sha256(_real(manifest_path)),
            "original_exe_sha256": _sha256(game / ORIGINAL_EXE),
            "expected_original_exe_sha256": ORIGINAL_SHA256,
            "support_dll_sha256": game_data.get("support_dll_sha256", {}),
            "command": f"runtime_env.py g1-r1-candidate-load-origin --manifest {manifest_path} --screen {screen} --timeout {timeout}",
            "environment": {key: env.get(key) for key in ("DISPLAY", "WINEPREFIX", "WINEARCH", "LANG", "LC_ALL", "WINEDLLOVERRIDES")},
            "display": display, "prefix": str(prefix), "game_root": str(game),
            "harness_sha256": {"tools/runtime_env.py": _sha256(Path(__file__))},
            "dxwrapper_config": evidence["dxwrapper_config"],
            "observational_only": True,
        }
        _write_json(artifact_path, evidence)
        log.close()
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
        lock.close()
    if error is not None:
        raise RuntimeSafetyError(error)
    return evidence


def g1_r1_load_origin(
    manifest_path: Path, *, screen: str = "1600x1200x24", timeout: float = 90,
) -> dict[str, Any]:
    """Run the bounded, read-only R1 load-origin observation.

    This is a research lane: it records one real click and origin samples in
    ``r1_load_origin.json`` but never feeds the production G1 evidence path.
    """

    if timeout <= 0 or timeout > 90:
        raise RuntimeSafetyError("g1-r1-load-origin timeout must be between 1 and 90 seconds")
    if screen != "1600x1200x24":
        raise RuntimeSafetyError("g1-r1-load-origin requires the fixed 1600x1200x24 screen")
    checked = check_runtime(manifest_path)
    data, game, prefix, output = _manifest(manifest_path)
    wine_data = data.get("wine")
    if not isinstance(wine_data, dict) or wine_data.get("created_new") is not True:
        raise RuntimeSafetyError("g1-r1-load-origin requires a newly prepared manifest")
    if _prefix_pids(prefix) or _existing_state(prefix) or (output / "r1_load_origin.json").exists():
        raise RuntimeSafetyError("g1-r1-load-origin requires an unused private prefix and output")
    output.mkdir(parents=True, exist_ok=True)
    lock_path = output.parent / ".r1-load-origin.lock"
    lock = lock_path.open("a+", encoding="utf-8")
    try:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
        lock.close()
        raise RuntimeSafetyError("R1 load-origin already owns this prefix") from exc
    log_path = output / "r1_load_origin.log"
    log = log_path.open("a", encoding="utf-8")
    env = dict(os.environ, WINEPREFIX=str(prefix), WINEARCH="win32", WINEDEBUG="-all",
               LANG="ko_KR.UTF-8", LC_ALL="ko_KR.UTF-8", WINEDLLOVERRIDES="ddraw=b")
    run_id = _real(manifest_path).parent.name
    started = time.monotonic()
    children: list[subprocess.Popen[Any]] = []
    xvfb: subprocess.Popen[Any] | None = None
    proc: subprocess.Popen[Any] | None = None
    display = ""
    error: str | None = None
    evidence: dict[str, Any] = {
        "status": "UNKNOWN",
        "classification": "NOT_STARTED",
        "manifest": checked,
        "run_id": run_id,
        "screen": screen,
        "timeout_seconds": timeout,
        "fixture": {
            "kind": "new private copy; default two-player random game",
            "synthetic": False,
            "memory_writes": False,
            "resource_grant": False,
        },
        "addresses": {
            "program_state_word": hex(G1_R1_PROGRAM_STATE_ADDRESS),
            "pending_state_word": hex(G1_R1_PENDING_STATE_ADDRESS),
            "origin_x_y_tag": hex(G1_R1_ORIGIN_ADDRESS),
        },
        "wait_ps_states": list(G1_R1_WAIT_PS_STATES),
        "input": {"client": list(G1_R1_CLICK_POINT), "count": 0, "root": None},
        "pending_state": [],
        "origin_tag": {"pre": None, "post": None},
        "ps_word": {"pre": None, "post": None},
        "ps_dword": {"pre": None, "post": None},
    }

    def preserve_failure(mode: str, reason: str, *, observation: Mapping[str, Any] | None = None) -> None:
        evidence.update(_g1_r1_failure_record(mode=mode, reason=reason, observation=observation,
                                              error=error))

    try:
        xvfb, display = _xvfb(log, screen)
        env["DISPLAY"] = display
        shell = subprocess.Popen(["wine", "explorer", "/desktop=Default,1600x1200"],
                                 cwd=game, env=env, stdout=log, stderr=log)
        children.append(shell)
        time.sleep(1)
        if time.monotonic() >= started + timeout:
            raise RuntimeSafetyError("R1 load-origin deadline exceeded before game launch")
        proc = subprocess.Popen(["wine", str(game / ORIGINAL_EXE)], cwd=game,
                                env=env, stdout=log, stderr=log)
        children.append(proc)
        if str(REPO_ROOT) not in sys.path:
            sys.path.insert(0, str(REPO_ROOT))
        from patches.population.runtime_driver import read as read_memory

        def read_for_process(address: int, size: int) -> bytes:
            return read_memory(proc.pid, address, size)  # type: ignore[union-attr]

        pending_samples: list[dict[str, Any]] = evidence["pending_state"]

        def read_wait_state(_detailed: bool) -> dict[str, Any]:
            current = _g1_r1_read_wait_state(read_for_process)
            pending_samples.append({
                "elapsed_seconds": round(time.monotonic() - started, 3),
                "ps_word": current["ps_word"],
                "ps_dword": current["ps_dword"],
                "pending_state": current["pending_state"],
            })
            return current

        wait_observation: dict[str, Any] = {}
        state9 = _wait_state(
            read_wait_state,
            lambda item: item.get("ps") == G1_R1_WAIT_PS_STATES[0],
            started, timeout, "R1 did not reach PS=9", stage="r1_ps9",
            stage_budget=G1_R1_PS9_STAGE_BUDGET, stage_started=started,
            wait_observation=wait_observation,
        )
        pre = _g1_r1_read_origin_checked(read_for_process, site="pre")
        evidence["pre"] = {"state": state9, "origin": pre}
        evidence["origin_tag"]["pre"] = pre["tag"]
        evidence["ps_word"]["pre"] = state9["ps_word"]
        evidence["ps_dword"]["pre"] = state9["ps_dword"]
        evidence["precondition"] = {
            "expected_origin": [0, 0, 0],
            "observed_origin": [pre["x"], pre["y"], pre["tag"]],
            "pass": [pre["x"], pre["y"], pre["tag"]] == [0, 0, 0],
        }
        if not evidence["precondition"]["pass"]:
            preserve_failure("BLOCKED_PRECONDITION", "P1 precondition failed: PS=9 origin was not (0,0,0)",
                             observation=evidence["precondition"])
        else:
            tree = _window_tree(display, _remaining(started, timeout))
            outer_id, content_id = _game_window_ids(tree)
            if content_id is None:
                raise RuntimeSafetyError("R1 original game window has no 800x600 content child")
            root_match = re.search(r"Window id: (0x[0-9a-fA-F]+) \(the root window\)", tree)
            if not root_match:
                raise RuntimeSafetyError("R1 root window id is missing from X11 tree")
            root_info = _xwininfo_details(display, root_match.group(1), _remaining(started, timeout))
            content_info = _xwininfo_details(display, content_id, _remaining(started, timeout))
            if (int(root_info["width"]), int(root_info["height"])) != (1600, 1200):
                raise RuntimeSafetyError("R1 private Xvfb root is not 1600x1200")
            if (int(content_info["width"]), int(content_info["height"])) != (800, 600):
                raise RuntimeSafetyError("R1 game content crop is not exactly 800x600")
            content_crop = (int(content_info["x"]), int(content_info["y"]), 800, 600)
            evidence["window"] = {
                "root": root_info,
                "content_child": content_info,
                "content_crop": {"x": content_crop[0], "y": content_crop[1], "width": 800, "height": 600},
            }
            focus = subprocess.run(["xdotool", "windowfocus", outer_id], env=env,
                                   stdout=log, stderr=log,
                                   timeout=min(10, _remaining(started, timeout)), check=True)
            root_x, root_y = content_crop[0] + G1_R1_CLICK_POINT[0], content_crop[1] + G1_R1_CLICK_POINT[1]
            click = subprocess.run(
                [sys.executable, str(REPO_ROOT / "tools/x11_mouse_click.py"), "--display", display,
                 str(root_x), str(root_y)], env=env, stdout=log, stderr=log,
                timeout=min(10, _remaining(started, timeout)), check=True,
            )
            evidence["input"].update({
                "root": [root_x, root_y], "target_window": outer_id,
                "focus_exit": focus.returncode, "inject_exit": click.returncode, "count": 1,
            })
            wait_observation = {}
            ps35_stage_started = time.monotonic()
            state35 = _wait_state(
                read_wait_state,
                lambda item: item.get("ps") == G1_R1_WAIT_PS_STATES[1],
                started, timeout, "R1 load click did not reach PS=35", stage="r1_ps35",
                stage_budget=G1_R1_PS35_STAGE_BUDGET, stage_started=ps35_stage_started,
                wait_observation=wait_observation,
            )
            post = _g1_r1_read_origin_checked(read_for_process, site="post")
            evidence["post"] = {"state": state35, "origin": post}
            evidence["origin_tag"]["post"] = post["tag"]
            evidence["ps_word"]["post"] = state35["ps_word"]
            evidence["ps_dword"]["post"] = state35["ps_dword"]
            evidence.update(_g1_r1_compare_origin(pre, post))
    except _G1WaitTimeout as exc:
        error = str(exc)
        evidence["wait_observation"] = exc.observation
        evidence.update(_g1_r1_wait_failure_record(exc))
    except _G1R1CollectionError as exc:
        error = exc.original_error
        evidence.update(_g1_r1_collection_failure_record(exc, evidence=evidence))
    except (OSError, subprocess.SubprocessError, RuntimeSafetyError, ValueError, struct.error) as exc:
        error = str(exc)
        if evidence.get("input", {}).get("count") == 1:
            mode = "COLLECTION_ERROR" if evidence.get("post") is not None else "TIMEOUT"
        else:
            mode = "COLLECTION_ERROR"
        preserve_failure(mode, "R1 observation failed before a valid result", observation=evidence)
    finally:
        for child in children:
            if child.poll() is None:
                child.terminate()
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline and any(child.poll() is None for child in children):
            time.sleep(0.05)
        for child in children:
            if child.poll() is None:
                child.kill()
        for child in children:
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass
        cleanup_error: str | None = None
        try:
            _run(["wineserver", "-k"], env=env, timeout=10, log=log_path)
            _run(["wineserver", "-w"], env=env, timeout=10, log=log_path)
        except RuntimeSafetyError as exc:
            cleanup_error = str(exc)
        if xvfb is not None and xvfb.poll() is None:
            xvfb.terminate()
            try:
                xvfb.wait(timeout=5)
            except subprocess.TimeoutExpired:
                xvfb.kill()
        cleanup = {
            "owned_launchers_stopped": all(child.poll() is not None for child in children),
            "xvfb_stopped": xvfb is None or xvfb.poll() is not None,
            "prefix_target": str(prefix), "global_kill_used": False,
            "prefix_processes_after": _prefix_pids(prefix), "error": cleanup_error,
        }
        cleanup["ok"] = bool(cleanup["owned_launchers_stopped"] and cleanup["xvfb_stopped"]
                              and not cleanup["prefix_processes_after"] and cleanup_error is None)
        evidence["cleanup"] = cleanup
        evidence["elapsed_seconds"] = round(time.monotonic() - started, 3)
        evidence["provenance"] = {
            "manifest_sha256": _sha256(_real(manifest_path)),
            "original_exe_sha256": _sha256(game / ORIGINAL_EXE),
            "expected_original_exe_sha256": ORIGINAL_SHA256,
            "command": f"runtime_env.py g1-r1-load-origin --manifest {manifest_path} --screen {screen} --timeout {timeout}",
            "environment": {key: env.get(key) for key in ("DISPLAY", "WINEPREFIX", "WINEARCH", "LANG", "LC_ALL", "WINEDLLOVERRIDES")},
            "harness_sha256": {"tools/runtime_env.py": _sha256(Path(__file__))},
            "observational_only": True,
        }
        _write_json(output / "r1_load_origin.json", evidence)
        log.close()
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
        lock.close()
        if not bool(cleanup["ok"]) and error is None:
            error = "R1 runtime cleanup incomplete; inspect r1_load_origin.json"
    if error is not None:
        raise RuntimeSafetyError(error)
    return evidence


def g1_baseline(manifest_path: Path, *, screen: str = "1600x1200x24", timeout: float = 90) -> dict[str, Any]:
    """Collect the no-patch G1-A boundary evidence in one fresh private run."""
    if timeout <= 0 or timeout > 90:
        raise RuntimeSafetyError("g1-baseline timeout must be between 1 and 90 seconds")
    if screen != "1600x1200x24":
        raise RuntimeSafetyError("g1-baseline requires the fixed 1600x1200x24 screen")
    checked = check_runtime(manifest_path)
    data, game, prefix, output = _manifest(manifest_path)
    wine_data = data.get("wine")
    if not isinstance(wine_data, dict) or wine_data.get("created_new") is not True:
        raise RuntimeSafetyError("g1-baseline requires a newly prepared manifest")
    if _prefix_pids(prefix) or _existing_state(prefix) or (output / "g1_a").exists():
        raise RuntimeSafetyError("g1-baseline requires an unused private prefix and output")
    g1_dir = output / "g1_a"
    g1_dir.mkdir()
    run_id = _real(manifest_path).parent.name
    started = time.monotonic()
    log_path = output / "g1-baseline.log"
    log = log_path.open("a", encoding="utf-8")
    env = dict(os.environ, WINEPREFIX=str(prefix), WINEARCH="win32", WINEDEBUG="-all",
               LANG="ko_KR.UTF-8", LC_ALL="ko_KR.UTF-8", WINEDLLOVERRIDES="ddraw=b")
    children: list[subprocess.Popen[Any]] = []
    screenshots: list[dict[str, Any]] = []
    inputs: list[dict[str, Any]] = []
    evidence: dict[str, Any] = {"manifest": checked, "screen": screen, "timeout_seconds": timeout,
                               "screenshots": screenshots, "fixture": {
                                   "kind": "new private copy; default two-player random game",
                                   "synthetic": False, "memory_writes": False,
                                   "control_bridge": False, "resource_grant": False,
                               }}
    error: str | None = None
    cleanup: dict[str, Any] = {}
    content_crop: tuple[int, int, int, int] | None = None
    display = ""
    proc: subprocess.Popen[Any] | None = None
    input_phase_metrics: dict[str, Any] = {"items": {}}
    input_phase_started: float | None = None
    try:
        xvfb, display = _xvfb(log, screen)
        env["DISPLAY"] = display
        shell = subprocess.Popen(["wine", "explorer", "/desktop=Default,1600x1200"], cwd=game,
                                 env=env, stdout=log, stderr=log)
        children.append(shell)
        time.sleep(1)
        try:
            baseline_tree = _window_tree(display, _remaining(started, timeout))
        except RuntimeSafetyError:
            baseline_tree = ""
        proc = subprocess.Popen(["wine", str(game / ORIGINAL_EXE)], cwd=game, env=env,
                                stdout=log, stderr=log)
        children.append(proc)
        if str(REPO_ROOT) not in sys.path:
            sys.path.insert(0, str(REPO_ROOT))
        from patches.population.runtime_driver import read as read_memory
        from patches.population.runtime_driver import state as read_game_state

        def read(pid: int, address: int, size: int) -> bytes:
            return read_memory(pid, address, size)

        def state(detailed: bool = True) -> dict[str, Any]:
            return read_game_state(proc.pid, detailed)  # type: ignore[union-attr]

        tree = ""
        state9 = _wait_state(state, lambda item: item.get("ps") == 9,
                             started, timeout, "original title/menu state PS=9 not reached")
        tree = _window_tree(display, _remaining(started, timeout))
        if baseline_tree and _window_ids(tree) <= _window_ids(baseline_tree):
            raise RuntimeSafetyError("no new original game window beyond Wine desktop")
        outer_id, content_id = _game_window_ids(tree)
        if content_id is None:
            raise RuntimeSafetyError("original game window has no 800x600 content child")
        root_match = re.search(r"Window id: (0x[0-9a-fA-F]+) \(the root window\)", tree)
        if not root_match:
            raise RuntimeSafetyError("root window id is missing from X11 tree")
        root_info = _xwininfo_details(display, root_match.group(1), _remaining(started, timeout))
        game_info = _xwininfo_details(display, outer_id, _remaining(started, timeout))
        content_info = _xwininfo_details(display, content_id, _remaining(started, timeout))
        if (int(root_info["width"]), int(root_info["height"])) != (1600, 1200):
            raise RuntimeSafetyError("private Xvfb root is not 1600x1200")
        if (int(content_info["width"]), int(content_info["height"])) != (800, 600):
            raise RuntimeSafetyError("game content crop is not exactly 800x600")
        content_crop = (int(content_info["x"]), int(content_info["y"]), 800, 600)
        input_scale = (1.0, 1.0)
        evidence["window"] = {"root": root_info, "virtual_desktop": [1600, 1200],
                               "game_window": game_info, "content_child": content_info,
                               "content_crop": {"x": content_crop[0], "y": content_crop[1],
                                                 "width": 800, "height": 600},
                               "tree_sha256": hashlib.sha256(tree.encode()).hexdigest(),
                               "tree": tree}
        evidence["modules"] = _module_evidence(proc.pid)
        def read_for_process(address: int, size: int) -> bytes:
            return read(proc.pid, address, size)  # type: ignore[union-attr]
        surface9 = _read_surface(read_for_process, 9)
        evidence["surface_ps9"] = surface9

        def capture(tag: str) -> dict[str, Any]:
            _path, record = _capture_screenshot(display, run_id, proc.pid, tag,
                                                 _remaining(started, timeout), content_crop)
            screenshots.append(record)
            return record

        def flush_input_stage() -> None:
            _g1_flush_input_stage(g1_dir, evidence, inputs)

        def input_click(tag: str, x: int, y: int, before: object, expected: str,
                        after: object, actual: str, passed: bool) -> dict[str, Any]:
            entry = _g1_record_input(
                inputs, tag=tag, x=x, y=y, content_crop=content_crop, scale=input_scale,
                before=before, expected=expected, after=after, actual=actual,
                result="PASS" if passed else "FAIL",
            )
            flush_input_stage()
            return entry

        def input_record(tag: str, x: int, y: int, before: object, expected: str,
                         after: object, actual: str, result: str) -> dict[str, Any]:
            return _g1_record_selector_input(
                inputs, tag=tag, x=x, y=y, content_crop=content_crop, scale=input_scale,
                before=before, expected=expected, after=after, actual=actual, result=result,
                flush=flush_input_stage,
            )

        def capture_neutral(tag: str) -> dict[str, Any]:
            neutral_x, neutral_y = G1_NEUTRAL_POINT
            pointer = _move_pointer_exact(
                env, (content_crop[0] + neutral_x, content_crop[1] + neutral_y),  # type: ignore[index]
                timeout=_remaining(started, timeout), log=log,
            )
            time.sleep(min(0.15, _remaining(started, timeout)))
            record = capture(tag)
            record["cursor_content"] = list(G1_NEUTRAL_POINT)
            record["cursor_root"] = pointer
            return record

        before_title_png = capture("title_before_menu")
        title_x, title_y = content_crop[0] + 184, content_crop[1] + 560  # type: ignore[index]
        focus = subprocess.run(["xdotool", "windowfocus", outer_id], env=env, stdout=log, stderr=log,
                               timeout=min(10, _remaining(started, timeout)), check=True)
        click = subprocess.run([sys.executable, str(REPO_ROOT / "tools/x11_mouse_click.py"),
                                "--display", display, str(title_x), str(title_y)], env=env,
                               stdout=log, stderr=log, timeout=min(10, _remaining(started, timeout)), check=True)
        state7 = _wait_state(state, lambda item: item.get("ps") == 7,
                             started, timeout, "title menu click did not reach PS=7")
        after_title_png = capture("lobby_after_menu")
        menu_before = {"ps": state9.get("ps"), "screenshot": before_title_png}
        menu_after = {"ps": state7.get("ps"), "screenshot": after_title_png}
        input_click(
            "menu", 184, 560, menu_before, "PS9->PS7 and screenshot changes", menu_after,
            f"PS{state9.get('ps')}->PS{state7.get('ps')}; focus={focus.returncode}; click={click.returncode}",
            _g1_menu_input_pass(menu_before, menu_after),
        )
        if inputs[-1]["result"] != "PASS":
            raise RuntimeSafetyError("menu input effect did not pass")

        def selector_state() -> dict[str, Any]:
            return {"ps": state(False).get("ps"),
                    "selector": _read_lobby_selector(read_for_process)}

        def selector_state_for_wait(_detailed: bool) -> dict[str, Any]:
            return selector_state()

        def click_selector(_tag: str, point: tuple[int, int]) -> None:
            x, y = point
            subprocess.run(
                [sys.executable, str(REPO_ROOT / "tools/x11_mouse_click.py"), "--display", display,
                 str(content_crop[0] + x), str(content_crop[1] + y)],  # type: ignore[index]
                env=env, stdout=log, stderr=log,
                timeout=min(10, _remaining(started, timeout)), check=True,
            )

        def wait_selector(
            predicate: Callable[[Mapping[str, Any]], bool], message: str,
        ) -> Mapping[str, Any]:
            return _wait_state(selector_state_for_wait, predicate, started, timeout, message)

        solo_state, solo_after_png, _initial_selector = _g1_selector_flow(
            selector_state, wait_selector, click_selector, capture_neutral, input_record,
        )

        confirm_x, confirm_y = G1_SETUP_POINTS["connection_confirm"]
        subprocess.run([sys.executable, str(REPO_ROOT / "tools/x11_mouse_click.py"), "--display", display,
                        str(content_crop[0] + confirm_x), str(content_crop[1] + confirm_y)],  # type: ignore[index]
                       env=env, stdout=log, stderr=log,
                       timeout=min(10, _remaining(started, timeout)), check=True)
        preprocess_state = _wait_state(
            state, lambda item: item.get("ps") in {4, 5, 6}, started, timeout,
            "single-player connection confirm did not enter local lobby preprocessing",
        )
        lobby_state = _wait_state(
            state, lambda item: item.get("ps") == 5, started, timeout,
            "local random-game confirm did not reach PS=5 lobby",
        )
        committed_mode = _read_lobby_mode(read_for_process)
        lobby_png = capture_neutral("local_lobby_ready")
        input_click("connection_confirm_setup", confirm_x, confirm_y,
                    {"ps": solo_state.get("ps"), "selector": solo_state.get("selector"),
                     "screenshot": solo_after_png},
                    "PS7 enters PS4/5/6 preprocessing, reaches PS5, and commits solo mode WORD=1",
                    {"preprocess_ps": preprocess_state.get("ps"), "ps": lobby_state.get("ps"),
                     "committed_mode": committed_mode, "screenshot": lobby_png},
                    f"PS7->PS{preprocess_state.get('ps')}->PS{lobby_state.get('ps')}; "
                    f"committed_mode={committed_mode}",
                    _g1_confirm_endpoint_pass(
                        int(preprocess_state.get("ps", -1)), int(lobby_state.get("ps", -1)),
                        committed_mode,
                        lobby_png.get("sha256") != solo_after_png.get("sha256"),
                    ))
        if inputs[-1]["result"] != "PASS":
            raise RuntimeSafetyError("local random-game lobby setup was not observed")

        def ready_state_for_wait(_detailed: bool) -> dict[str, Any]:
            return {"ps": state(False).get("ps"), **_read_local_ready_state(read_for_process)}

        ready_state = _wait_state(
            ready_state_for_wait,
            lambda item: item.get("ps") == 5 and item.get("ready_value") == 1,
            started, timeout,
            "solo local ready DWORD was not set for the active local slot",
        )
        ready_pass = _g1_ready_endpoint_pass(
            int(lobby_state.get("ps", -1)), int(ready_state.get("ps", -1)),
            committed_mode, ready_state,
        )
        inputs.append({
            "tag": "player0_ready_auto",
            "content": None,
            "x11": None,
            "before": {"ps": lobby_state.get("ps"), "committed_mode": committed_mode},
            "expected": "confirm commits solo mode=1; active local slot index 0..7 has ready DWORD=1; PS remains 5",
            "after": ready_state,
            "actual": f"PS{lobby_state.get('ps')}->PS{ready_state.get('ps')}; "
                       f"local={ready_state.get('local_index')}; ready={ready_state.get('ready_value')}",
            "result": "PASS" if ready_pass else "FAIL",
        })
        if not ready_pass:
            raise RuntimeSafetyError("solo local ready DWORD setup gate was not observed")

        start_x, start_y = G1_SETUP_POINTS["lobby_start"]
        subprocess.run([sys.executable, str(REPO_ROOT / "tools/x11_mouse_click.py"), "--display", display,
                        str(content_crop[0] + start_x), str(content_crop[1] + start_y)],  # type: ignore[index]
                       env=env, stdout=log, stderr=log,
                       timeout=min(10, _remaining(started, timeout)), check=True)
        scene_state = _wait_state(
            state,
            lambda item: item.get("ps") == 3 and isinstance(item.get("tick"), int) and item["tick"] > 0,
            started, timeout, "visible local-lobby start did not reach PS=3",
        )
        scene_png = capture_neutral("scene_after_lobby_start")
        input_click("lobby_start_setup", start_x, start_y,
                    {"ps": ready_state.get("ps"), "screenshot": lobby_png},
                    "PS5->PS3 with tick>0 through the visible local-lobby start",
                    {"ps": scene_state.get("ps"), "tick": scene_state.get("tick"),
                     "screenshot": scene_png},
                    f"PS{ready_state.get('ps')}->PS{scene_state.get('ps')}; tick={scene_state.get('tick')}",
                    _g1_start_endpoint_pass(int(ready_state.get("ps", -1)), scene_state))
        surface3 = _read_surface(read_for_process, 3)
        evidence["surface_ps3"] = surface3
        if not (surface9.get("values", [])[1:3] == [800, 600] and surface3.get("values", [])[1:3] == [800, 600]):
            raise RuntimeSafetyError("original 800x600 render surface was not observed at PS9 and PS3")

        players = scene_state.get("players", [])
        units = scene_state.get("units", [])
        active_counts = {owner: sum(1 for unit in units if isinstance(unit, dict) and unit.get("owner") == owner)
                         for owner in (0, 1)}
        nations = {owner: players[owner].get("nation") for owner in (0, 1)
                   if isinstance(players, list) and len(players) > owner and isinstance(players[owner], dict)}
        if any(active_counts[owner] < 1 for owner in (0, 1)) or any(not nations.get(owner) for owner in (0, 1)):
            raise RuntimeSafetyError("PS3 scene lacks active units and nonzero nations for owners 0 and 1")
        scene_snapshot = _g1_scene_snapshot(scene_state, read_for_process)
        scene_id = _json_fingerprint({"state": scene_state, "title": state9, "fixture": evidence["fixture"]})
        evidence["scene"] = {"ps": scene_state.get("ps"), "tick": scene_state.get("tick"),
                              "map": "default two-player random game; map name/seed not exposed by approved read-only offsets",
                              "reproduction_identifier": {"kind": "same-run state fingerprint", "value": scene_id,
                                                            "replay_seed_observed": False},
                              "owners": scene_snapshot["owners"],
                              "unit_slots": scene_snapshot["unit_slots"],
                              "owner0_hq_world": scene_snapshot["owner0_hq_world"],
                              "owner0_hq_candidates": scene_snapshot["owner0_hq_candidates"],
                              "owner0_hq_type": scene_snapshot["owner0_hq_type"],
                              "world_bounds": scene_snapshot["world_bounds"],
                              "camera": scene_snapshot["camera"], "synthetic": False}
        flush_input_stage()

        def baseline_click(x: int, y: int) -> None:
            subprocess.run([sys.executable, str(REPO_ROOT / "tools/x11_mouse_click.py"), "--display", display,
                            str(content_crop[0] + x), str(content_crop[1] + y)], env=env, stdout=log, stderr=log,
                           timeout=min(10, _remaining(started, timeout)), check=True)

        def baseline_drag(x: int, y: int, to_x: int, to_y: int) -> None:
            subprocess.run([sys.executable, str(REPO_ROOT / "tools/x11_mouse_click.py"), "--display", display,
                            str(content_crop[0] + x), str(content_crop[1] + y), "--drag-to",
                            str(content_crop[0] + to_x), str(content_crop[1] + to_y)],
                           env=env, stdout=log, stderr=log,
                           timeout=min(10, _remaining(started, timeout)), check=True)

        def baseline_wait(reader, predicate, message, **kwargs):
            return _wait_state(reader, predicate, started, timeout, message, **kwargs)

        input_phase_started = time.monotonic()

        def baseline_production_cell() -> Mapping[str, Any]:
            if "production_cell" not in evidence:
                evidence["production_cell"] = _read_g1_command_cell_provenance(
                    read_for_process, _sha256(game / ORIGINAL_EXE),
                    started=started, timeout=timeout,
                )
            return evidence["production_cell"]

        input_result = _g1_run_input_sequence(
            inputs=inputs, content_crop=content_crop, scale=input_scale, capture=capture,
            runtime_state=lambda: state(False), game_state=state,
            read_selection=lambda: _read_g1_selection_evidence(read_for_process),
            read_camera=lambda: _read_camera(read_for_process), wait=baseline_wait,
            click=baseline_click, drag=baseline_drag,
            read_production_cell=baseline_production_cell, flush=flush_input_stage,
            started=started, timeout=timeout, phase_metrics=input_phase_metrics,
        )
        _g1_finalize_input_phase(input_phase_metrics, input_phase_started)
        evidence["input_phase"] = input_phase_metrics
        evidence["scene"]["camera_after_minimap"] = input_result["camera_after_minimap"]  # type: ignore[index]
        evidence["boundary"] = {"render_surface": "surface_ps9/surface_ps3; read-only singleton fields",
                                 "display_scale": "1600x1200 Xvfb and Wine virtual desktop, no game patch",
                                 "x11_content": "window.content_child and exact 800x600 crop",
                                 "input_inverse": "fixed content coordinates plus content-child origin",
                                 "game_input": "real XTest mouse events; effects read from PS/selection/camera/player state",
                                 "evidence_vs_inference": "surface/module/state are observed; crop mapping is derived from xwininfo geometry"}
    except (OSError, subprocess.SubprocessError, RuntimeSafetyError, ValueError, struct.error) as exc:
        error = str(exc)
        if input_phase_started is not None:
            _g1_finalize_input_phase(input_phase_metrics, input_phase_started)
            evidence["input_phase"] = input_phase_metrics
        evidence["error"] = error
        _record_g1_command_cell_error(evidence, exc)
    finally:
        for child in children:
            if child.poll() is None:
                child.terminate()
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline and any(child.poll() is None for child in children):
            time.sleep(0.05)
        for child in children:
            if child.poll() is None:
                child.kill()
        for child in children:
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass
        cleanup_error: str | None = None
        try:
            _run(["wineserver", "-k"], env=env, timeout=10, log=log_path)
            _run(["wineserver", "-w"], env=env, timeout=10, log=log_path)
        except RuntimeSafetyError as exc:
            cleanup_error = str(exc)
        if "xvfb" in locals() and xvfb.poll() is None:
            xvfb.terminate()
            try:
                xvfb.wait(timeout=5)
            except subprocess.TimeoutExpired:
                xvfb.kill()
        cleanup = {"owned_launchers_stopped": all(child.poll() is not None for child in children),
                   "xvfb_stopped": "xvfb" not in locals() or xvfb.poll() is not None,
                   "prefix_target": str(prefix), "global_kill_used": False,
                   "prefix_processes_after": _prefix_pids(prefix), "error": cleanup_error}
        cleanup["ok"] = bool(cleanup["owned_launchers_stopped"] and cleanup["xvfb_stopped"] and
                              not cleanup["prefix_processes_after"] and cleanup_error is None)
        evidence["cleanup"] = cleanup
        if input_phase_started is not None:
            _g1_finalize_input_phase(input_phase_metrics, input_phase_started)
            evidence["input_phase"] = input_phase_metrics
        evidence["elapsed_seconds"] = round(time.monotonic() - started, 3)
        # Keep the stage flush useful after teardown/errors as well: the final
        # evidence snapshot must contain the same diagnostic fields as output/.
        _write_json(g1_dir / "evidence.json", evidence)
        provenance = {"manifest_sha256": _sha256(_real(manifest_path)),
                      "original_exe_sha256": _sha256(game / ORIGINAL_EXE),
                      "expected_original_exe_sha256": ORIGINAL_SHA256,
                      "command": f"runtime_env.py g1-baseline --manifest {manifest_path} --screen {screen} --timeout {timeout}",
                      "environment": {key: env.get(key) for key in ("DISPLAY", "WINEPREFIX", "WINEARCH", "LANG", "LC_ALL", "WINEDLLOVERRIDES")},
                      "display": display, "prefix": str(prefix), "game_root": str(game),
                      "harness_sha256": {"tools/runtime_env.py": _sha256(Path(__file__))},
                      "observational_only": True}
        _write_json(g1_dir / "provenance.json", provenance)
        _write_json(g1_dir / "window.json", evidence.get("window", {"status": "SKIP"}))
        _write_json(g1_dir / "surface.json", {"ps9": evidence.get("surface_ps9", {"status": "SKIP"}),
                                               "ps3": evidence.get("surface_ps3", {"status": "SKIP"})})
        _write_json(g1_dir / "modules.json", evidence.get("modules", {"status": "SKIP"}))
        _write_json(g1_dir / "scene.json", evidence.get("scene", {"status": "SKIP"}))
        (g1_dir / "inputs.jsonl").write_text("".join(json.dumps(item, ensure_ascii=False) + "\n" for item in inputs), encoding="utf-8")
        (g1_dir / "boundary.md").write_text(
            "# G1-A boundary\n\n" + json.dumps(evidence.get("boundary", {"status": "SKIP"}), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")
        input_checks = _g1_input_verdict(inputs, enabled=True)
        checks = {"original_hash": evidence.get("manifest", {}).get("exe_sha256") == ORIGINAL_SHA256,  # type: ignore[union-attr]
                  "private_1600x1200_root": evidence.get("window", {}).get("virtual_desktop") == [1600, 1200],  # type: ignore[union-attr]
                  "800x600_content_crop": evidence.get("window", {}).get("content_crop", {}).get("width") == 800 and  # type: ignore[union-attr]
                  evidence.get("window", {}).get("content_crop", {}).get("height") == 600,  # type: ignore[union-attr]
                  "surface_ps9_ps3": "surface_ps9" in evidence and "surface_ps3" in evidence,
                  "modules_hashed": "modules" in evidence,
                  "required_inputs": input_checks["required_inputs"],
                  "cleanup": bool(cleanup.get("ok")),
                  "same_run_scene": "scene" in evidence}
        verdict = _g1_baseline_verdict(
            error=error, checks=checks, input_checks=input_checks, cleanup=cleanup,
        )
        _write_json(g1_dir / "verdict.json", verdict)
        _write_json(output / "g1_baseline.json", evidence)
        log.close()
        if not bool(cleanup.get("ok")) and error is None:
            error = "runtime cleanup incomplete; inspect output/g1_a/verdict.json"
    if error is not None:
        raise RuntimeSafetyError(error)
    return verdict


def g1_presentation_trace(
    manifest_path: Path, *, screen: str = "1600x1200x24", timeout: float = 90,
    close_helper: Path | None = None, dxwrapper_2x: bool = False,
    ps3_dwell_seconds: float = 0.0, g1_input_sequence: bool = False,
) -> dict[str, Any]:
    """Run one opt-in DirectDraw provenance trace from PS9 through PS3."""
    if timeout <= 0 or timeout > 90:
        raise RuntimeSafetyError("g1-presentation-trace timeout must be between 1 and 90 seconds")
    if ps3_dwell_seconds < 0:
        raise RuntimeSafetyError("g1-presentation-trace PS3 dwell must not be negative")
    if g1_input_sequence and ps3_dwell_seconds > 0:
        raise RuntimeSafetyError("g1 input sequence and PS3 dwell cannot overlap")
    if screen != "1600x1200x24":
        raise RuntimeSafetyError("g1-presentation-trace requires the fixed 1600x1200x24 screen")
    if close_helper is None:
        configured = os.environ.get(WIN32_CLOSE_HELPER_ENV)
        close_helper = Path(configured) if configured else None
    if close_helper is None:
        raise RuntimeSafetyError(
            f"g1-presentation-trace requires --win32-close-helper or {WIN32_CLOSE_HELPER_ENV}"
        )
    close_helper = close_helper.expanduser().resolve(strict=False)
    if close_helper.suffix.lower() != ".exe" or not close_helper.is_file() or close_helper.is_symlink():
        raise RuntimeSafetyError(f"invalid Win32 close helper: {close_helper}")
    checked = check_runtime(manifest_path)
    data, game, prefix, output = _manifest(manifest_path)
    game_data = data.get("game")
    if not isinstance(game_data, dict) or game_data.get("diagnostic_bridge_overridden") is not True:
        raise RuntimeSafetyError("g1-presentation-trace requires a diagnostic bridge manifest")
    if _prefix_pids(prefix) or (output / "g1_presentation_trace").exists():
        raise RuntimeSafetyError("g1-presentation-trace requires an unused private prefix and output")

    trace_dir = output / "g1_presentation_trace"
    trace_dir.mkdir()
    run_id = _real(manifest_path).parent.name + "-presentation"
    started = time.monotonic()
    log_path = output / "g1-presentation-trace.log"
    log = log_path.open("a", encoding="utf-8")
    override = "ddraw=n,b" if dxwrapper_2x else "ddraw=b"
    env = dict(os.environ, WINEPREFIX=str(prefix), WINEARCH="win32", WINEDEBUG="-all",
               LANG="ko_KR.UTF-8", LC_ALL="ko_KR.UTF-8", WINEDLLOVERRIDES=override,
               SYW2_G1_PRESENT_TRACE="1", SYW2_G1_TRACE_RUN_ID=run_id)
    children: list[subprocess.Popen[Any]] = []
    screenshots: list[dict[str, Any]] = []
    inputs: list[dict[str, Any]] = []
    evidence: dict[str, Any] = {
        "manifest": checked, "screen": screen, "timeout_seconds": timeout,
        "fixture": {"kind": "new private copy; default two-player random game",
                     "synthetic": False, "memory_writes": False,
                     "control_bridge": False, "resource_grant": False,
                     "diagnostic_bridge": True},
        "screenshots": screenshots, "inputs": inputs,
        "dxwrapper_config": {"enabled": dxwrapper_2x, "winedlloverrides": override},
    }
    error: str | None = None
    cleanup: dict[str, Any] = {}
    display = ""
    proc: subprocess.Popen[Any] | None = None
    xvfb: subprocess.Popen[Any] | None = None
    dxwrapper_install: dict[str, object] | None = None
    dxwrapper_uninstall: dict[str, object] | None = None
    dxwrapper_cleanup_error: str | None = None
    input_phase_metrics: dict[str, Any] = {"items": {}}
    input_phase_started: float | None = None
    trace_path = prefix / "drive_c" / "inmm_g1_present_trace.jsonl"
    install_trace_copy = trace_dir / "trace_install.jsonl"
    raw_trace_copy = trace_dir / "trace_raw.jsonl"
    try:
        if dxwrapper_2x:
            from patches.resolution import dxwrapper_config

            dxwrapper_install = dxwrapper_config.install_private(game)
            evidence["dxwrapper_config"]["install"] = dxwrapper_install
        xvfb, display = _xvfb(log, screen)
        env["DISPLAY"] = display
        shell = subprocess.Popen(["wine", "explorer", "/desktop=Default,1600x1200"], cwd=game,
                                 env=env, stdout=log, stderr=log)
        children.append(shell)
        time.sleep(1)
        proc = subprocess.Popen(["wine", str(game / ORIGINAL_EXE)], cwd=game, env=env,
                                stdout=log, stderr=log)
        children.append(proc)
        if str(REPO_ROOT) not in sys.path:
            sys.path.insert(0, str(REPO_ROOT))
        from patches.population.runtime_driver import read as read_memory
        from patches.population.runtime_driver import state as read_game_state

        def state(detailed: bool = True) -> dict[str, Any]:
            return read_game_state(proc.pid, detailed)  # type: ignore[union-attr]

        state9 = _wait_state(state, lambda item: item.get("ps") == 9,
                             started, timeout, "presentation trace did not reach PS=9")
        tree = _window_tree(display, _remaining(started, timeout))
        outer_id, content_id = _game_window_ids(
            tree, allowed_sizes=((800, 600), (1600, 1200)),
        )
        if content_id is None:
            raise RuntimeSafetyError("presentation trace game window has no allowed-size content child")
        root_match = re.search(r"Window id: (0x[0-9a-fA-F]+) \(the root window\)", tree)
        if not root_match:
            raise RuntimeSafetyError("presentation trace root window is missing")
        root_info = _xwininfo_details(display, root_match.group(1), _remaining(started, timeout))
        content_info = _xwininfo_details(display, content_id, _remaining(started, timeout))
        if (int(root_info["width"]), int(root_info["height"])) != (1600, 1200):
            raise RuntimeSafetyError("private Xvfb root is not 1600x1200")
        client_size = (int(content_info["width"]), int(content_info["height"]))
        if client_size not in ((800, 600), (1600, 1200)):
            raise RuntimeSafetyError("presentation trace client must be 800x600 or 1600x1200")
        content_crop = (int(content_info["x"]), int(content_info["y"]), *client_size)
        scale = [client_size[0] / 800, client_size[1] / 600]
        evidence["window"] = {"root": root_info, "virtual_desktop": [1600, 1200],
                               "content_child": content_info, "content_crop": {
                                   "x": content_crop[0], "y": content_crop[1],
                                   "width": client_size[0], "height": client_size[1]},
                               "logical_content_size": [800, 600],
                               "physical_content_size": list(client_size),
                               "scale": scale, "scaled_2x": scale == [2.0, 2.0],
                               "tree_sha256": hashlib.sha256(tree.encode()).hexdigest()}
        input_scale = (float(scale[0]), float(scale[1]))
        evidence["modules"] = _module_evidence(proc.pid)
        loaded_ddraw = [item["path"] for item in evidence["modules"]["modules"]  # type: ignore[index]
                        if isinstance(item, dict) and "ddraw" in str(item.get("path", "")).lower()]
        evidence["dxwrapper_config"]["loaded_ddraw_modules"] = loaded_ddraw
        if dxwrapper_2x:
            private_ddraw = _real(game / "ddraw.dll")
            if not any(_real(Path(str(path))) == private_ddraw for path in loaded_ddraw):
                raise RuntimeSafetyError("dxwrapper 2x run did not load private game/ddraw.dll")

        def read_for_process(address: int, size: int) -> bytes:
            return read_memory(proc.pid, address, size)

        def capture(tag: str) -> dict[str, Any]:
            _path, record = _capture_screenshot(display, run_id, proc.pid, tag,
                                                 _remaining(started, timeout), content_crop)
            screenshots.append(record)
            return record

        def capture_finalization(tag: str) -> Mapping[str, object]:
            _path, record = _capture_screenshot(
                display, run_id, proc.pid, f"finalization_{tag}",
                _remaining(started, timeout), content_crop,
            )
            return record

        def selector_state() -> dict[str, Any]:
            return {"ps": state(False).get("ps"), "selector": _read_lobby_selector(read_for_process)}

        def wait_selector(predicate: Callable[[Mapping[str, Any]], bool], message: str) -> Mapping[str, Any]:
            return _wait_state(lambda _detailed: selector_state(), predicate, started, timeout, message)

        def click_selector(_tag: str, point: tuple[int, int]) -> None:
            x, y = point
            subprocess.run([sys.executable, str(REPO_ROOT / "tools/x11_mouse_click.py"),
                            "--display", display, str(content_crop[0] + x), str(content_crop[1] + y)],
                           env=env, stdout=log, stderr=log,
                           timeout=min(10, _remaining(started, timeout)), check=True)

        def capture_neutral(tag: str) -> dict[str, Any]:
            x, y = G1_NEUTRAL_POINT
            pointer = _move_pointer_exact(
                env, (content_crop[0] + x, content_crop[1] + y),  # type: ignore[index]
                timeout=_remaining(started, timeout), log=log,
            )
            time.sleep(min(0.15, _remaining(started, timeout)))
            record = capture(tag)
            record["cursor_content"] = list(G1_NEUTRAL_POINT)
            record["cursor_root"] = pointer
            return record

        def record_input(tag: str, x: int, y: int, before: object, expected: str,
                         after: object, actual: str, result: str) -> dict[str, Any]:
            return _g1_record_selector_input(
                inputs, tag=tag, x=x, y=y, content_crop=content_crop, scale=input_scale,
                before=before, expected=expected, after=after, actual=actual, result=result,
                flush=flush_input_stage,
            )

        def flush_input_stage() -> None:
            _g1_flush_input_stage(trace_dir, evidence, inputs)

        evidence["trace_gate"] = _presentation_trace_install_gate(trace_path, install_trace_copy, run_id)
        evidence["owned_win32_process"] = _read_owned_win32_pid(install_trace_copy, run_id)
        title_before = capture("ps9_before_menu")
        title_before_state = {"ps": state9.get("ps"), "screenshot": title_before}
        subprocess.run([sys.executable, str(REPO_ROOT / "tools/x11_mouse_click.py"),
                        "--display", display, str(content_crop[0] + 184),
                        str(content_crop[1] + 560)],
                       env=env, stdout=log, stderr=log,
                       timeout=min(10, _remaining(started, timeout)), check=True)
        state7 = _wait_state(state, lambda item: item.get("ps") == 7,
                             started, timeout, "presentation trace menu click did not reach PS=7")
        title_after = capture_neutral("ps7_lobby")
        title_after_state = {"ps": state7.get("ps"), "screenshot": title_after}
        _g1_record_input(
            inputs, tag="menu", x=184, y=560, content_crop=content_crop, scale=input_scale,
            before=title_before_state, expected="PS9->PS7 and screenshot changes",
            after=title_after_state, actual=f"PS{state9.get('ps')}->PS{state7.get('ps')}",
            result="PASS" if _g1_menu_input_pass(title_before_state, title_after_state) else "FAIL",
        )
        flush_input_stage()
        if inputs[-1]["result"] != "PASS":
            raise RuntimeSafetyError("presentation trace menu input effect did not pass")
        _g1_selector_flow(selector_state, wait_selector, click_selector, capture_neutral, record_input)

        confirm_x, confirm_y = G1_SETUP_POINTS["connection_confirm"]
        click_selector("connection_confirm", (confirm_x, confirm_y))
        preprocess = _wait_state(state, lambda item: item.get("ps") in {4, 5, 6},
                                 started, timeout, "presentation trace confirm did not enter local lobby")
        lobby = _wait_state(state, lambda item: item.get("ps") == 5,
                            started, timeout, "presentation trace confirm did not reach PS=5")
        ready = _wait_state(lambda _detailed: {"ps": state(False).get("ps"), **_read_local_ready_state(read_for_process)},
                            lambda item: item.get("ps") == 5 and item.get("ready_value") == 1,
                            started, timeout, "presentation trace local ready state was not observed")
        start_x, start_y = G1_SETUP_POINTS["lobby_start"]
        click_selector("lobby_start", (start_x, start_y))
        scene = _wait_state(state,
                            lambda item: item.get("ps") == 3 and isinstance(item.get("tick"), int)
                            and int(item["tick"]) > 0,
                            started, timeout, "presentation trace did not reach PS=3")
        scene_png = capture_neutral("ps3_scene")
        scene_snapshot = _g1_scene_snapshot(scene, read_for_process)
        scene_id = _json_fingerprint({"state": scene, "title": state9, "fixture": evidence["fixture"]})
        evidence["scene"] = {
            "ps": scene.get("ps"), "tick": scene.get("tick"),
            "map": "default two-player random game; map name/seed not exposed by approved read-only offsets",
            "reproduction_identifier": {"kind": "same-run state fingerprint", "value": scene_id,
                                          "replay_seed_observed": False},
            "owners": scene_snapshot["owners"], "unit_slots": scene_snapshot["unit_slots"],
            "owner0_hq_world": scene_snapshot["owner0_hq_world"],
            "owner0_hq_candidates": scene_snapshot["owner0_hq_candidates"],
            "owner0_hq_type": scene_snapshot["owner0_hq_type"],
            "world_bounds": scene_snapshot["world_bounds"], "camera": scene_snapshot["camera"],
            "synthetic": False,
        }
        flush_input_stage()
        evidence["capture"] = {"run_id": run_id, "ps_before": state9.get("ps"),
                                "ps_after": scene.get("ps"), "tick_after": scene.get("tick"),
                                "client_size": list(client_size),
                                "logical_content_size": [800, 600], "screenshot": scene_png,
                                "preprocess_ps": preprocess.get("ps"),
                                "lobby_ps": lobby.get("ps"), "ready": ready}

        if g1_input_sequence:
            def candidate_click(x: int, y: int) -> None:
                subprocess.run([sys.executable, str(REPO_ROOT / "tools/x11_mouse_click.py"),
                                "--display", display, str(content_crop[0] + x),
                                str(content_crop[1] + y)], env=env, stdout=log, stderr=log,
                               timeout=min(10, _remaining(started, timeout)), check=True)

            def candidate_drag(x: int, y: int, to_x: int, to_y: int) -> None:
                subprocess.run([sys.executable, str(REPO_ROOT / "tools/x11_mouse_click.py"),
                                "--display", display, str(content_crop[0] + x),
                                str(content_crop[1] + y), "--drag-to",
                                str(content_crop[0] + to_x), str(content_crop[1] + to_y)],
                               env=env, stdout=log, stderr=log,
                               timeout=min(10, _remaining(started, timeout)), check=True)

            def candidate_wait(reader, predicate, message, **kwargs):
                return _wait_state(reader, predicate, started, timeout, message, **kwargs)

            def read_production_cell() -> Mapping[str, Any]:
                if "production_cell" not in evidence:
                    evidence["production_cell"] = _read_g1_command_cell_provenance(
                        read_for_process, _sha256(game / ORIGINAL_EXE), started=started, timeout=timeout,
                    )
                return evidence["production_cell"]

            input_phase_started = time.monotonic()
            input_result = _g1_run_input_sequence(
                inputs=inputs, content_crop=content_crop, scale=input_scale, capture=capture,
                runtime_state=lambda: state(False), game_state=state,
                read_selection=lambda: _read_g1_selection_evidence(read_for_process),
                read_camera=lambda: _read_camera(read_for_process), wait=candidate_wait,
                click=candidate_click, drag=candidate_drag,
                read_production_cell=read_production_cell, flush=flush_input_stage,
                started=started, timeout=timeout, phase_metrics=input_phase_metrics,
            )
            _g1_finalize_input_phase(input_phase_metrics, input_phase_started)
            evidence["input_phase"] = input_phase_metrics
            evidence["scene"]["camera_after_minimap"] = input_result["camera_after_minimap"]

        if ps3_dwell_seconds > 0 and not g1_input_sequence:
            dwell = _observe_ps3_dwell(ps3_dwell_seconds, lambda: state(False), capture_neutral)
            if dwell is not None:
                evidence["ps3_dwell"] = dwell

        if not trace_path.is_file():
            raise RuntimeSafetyError("diagnostic DirectDraw trace file was not produced")
        trace_copy = trace_dir / "trace.jsonl"
        _finalize_copy_validate_presentation_trace(
            display, int(evidence["owned_win32_process"]["pid"]), close_helper,
            env, log, proc, trace_path, raw_trace_copy, trace_copy, run_id, started,
            timeout, evidence["capture"], evidence,
            program_state_reader=lambda: state(False),
            screenshot_capture=capture_finalization,
        )
        evidence["logical_surface_contract"] = _presentation_logical_surface_contract(trace_copy)
        if evidence["validator"].get("status") != "PASS":
            raise RuntimeSafetyError("DirectDraw presentation trace validator returned BLOCKED")
    except (OSError, subprocess.SubprocessError, RuntimeSafetyError, ValueError, struct.error) as exc:
        error = str(exc)
        if input_phase_started is not None:
            _g1_finalize_input_phase(input_phase_metrics, input_phase_started)
            evidence["input_phase"] = input_phase_metrics
        evidence["error"] = error
        _record_g1_command_cell_error(evidence, exc)
    finally:
        for child in children:
            if child.poll() is None:
                child.terminate()
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline and any(child.poll() is None for child in children):
            time.sleep(0.05)
        for child in children:
            if child.poll() is None:
                child.kill()
        for child in children:
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass
        cleanup_error: str | None = None
        try:
            _run(["wineserver", "-k"], env=env, timeout=10, log=log_path)
            _run(["wineserver", "-w"], env=env, timeout=10, log=log_path)
        except RuntimeSafetyError as exc:
            cleanup_error = str(exc)
        if dxwrapper_install is not None:
            try:
                from patches.resolution import dxwrapper_config

                dxwrapper_uninstall = dxwrapper_config.uninstall_private(game)
                evidence["dxwrapper_config"]["uninstall"] = dxwrapper_uninstall
            except (OSError, ValueError) as exc:
                dxwrapper_cleanup_error = str(exc)
        if xvfb is not None and xvfb.poll() is None:
            xvfb.terminate()
            try:
                xvfb.wait(timeout=5)
            except subprocess.TimeoutExpired:
                xvfb.kill()
        cleanup = {"owned_launchers_stopped": all(child.poll() is not None for child in children),
                   "xvfb_stopped": xvfb is None or xvfb.poll() is not None,
                   "prefix_target": str(prefix), "global_kill_used": False,
                   "prefix_processes_after": _prefix_pids(prefix), "error": cleanup_error}
        cleanup["dxwrapper_config_restored"] = (
            not dxwrapper_2x or dxwrapper_uninstall is not None
        )
        if dxwrapper_cleanup_error is not None:
            cleanup["dxwrapper_config_error"] = dxwrapper_cleanup_error
        cleanup["ok"] = bool(cleanup["owned_launchers_stopped"] and cleanup["xvfb_stopped"]
                              and not cleanup["prefix_processes_after"] and cleanup_error is None
                              and cleanup["dxwrapper_config_restored"])
        evidence["cleanup"] = cleanup
        if input_phase_started is not None:
            _g1_finalize_input_phase(input_phase_metrics, input_phase_started)
            evidence["input_phase"] = input_phase_metrics
        if dxwrapper_2x:
            try:
                _preserve_dxwrapper_logs(game, trace_dir, evidence["dxwrapper_config"])
            except OSError as exc:
                evidence["dxwrapper_config"]["wrapper_logs_error"] = str(exc)
                if error is None:
                    error = f"dxwrapper wrapper log capture failed: {exc}"
        try:
            _preserve_raw_presentation_trace(trace_path, raw_trace_copy)
        except OSError as exc:
            evidence["trace_copy_error"] = str(exc)
        evidence["elapsed_seconds"] = round(time.monotonic() - started, 3)
        evidence.setdefault("validator", {"status": "BLOCKED", "errors": [error or "trace did not complete"]})
        command = f"runtime_env.py g1-presentation-trace --manifest {manifest_path} --screen {screen} --timeout {timeout}"
        if dxwrapper_2x:
            command += " --dxwrapper-2x"
        if ps3_dwell_seconds > 0:
            command += f" --ps3-dwell-seconds {ps3_dwell_seconds}"
        if g1_input_sequence:
            command += " --g1-input-sequence"
        provenance = {"manifest_sha256": _sha256(_real(manifest_path)),
                      "original_exe_sha256": _sha256(game / ORIGINAL_EXE),
                      "expected_original_exe_sha256": ORIGINAL_SHA256,
                      "command": command,
                      "environment": {key: env.get(key) for key in ("DISPLAY", "WINEPREFIX", "WINEARCH", "LANG", "LC_ALL", "WINEDLLOVERRIDES", "SYW2_G1_PRESENT_TRACE", "SYW2_G1_TRACE_RUN_ID")},
                      "display": display, "prefix": str(prefix), "game_root": str(game),
                      "harness_sha256": {"tools/runtime_env.py": _sha256(Path(__file__))},
                      "diagnostic_bridge_sha256": game_data.get("diagnostic_bridge_sha256"),
                      "dxwrapper_config": evidence["dxwrapper_config"],
                      "observational_only": True}
        _write_json(trace_dir / "provenance.json", provenance)
        _write_json(trace_dir / "evidence.json", evidence)
        verdict = _g1_presentation_verdict(
            error=error, cleanup=cleanup, validator=evidence["validator"],
            inputs=inputs, input_sequence=g1_input_sequence,
        )
        _write_json(trace_dir / "verdict.json", verdict)
        log.close()
    if error is not None:
        raise RuntimeSafetyError(error)
    if not bool(cleanup.get("ok")):
        raise RuntimeSafetyError("presentation trace cleanup incomplete; inspect verdict.json")
    return verdict


def smoke(manifest_path: Path, *, timeout: float = 60) -> dict[str, object]:
    """Launch only the verified original copy for <=90s and collect evidence."""
    if timeout <= 0 or timeout > 90:
        raise RuntimeSafetyError("smoke timeout must be between 1 and 90 seconds")
    checked = check_runtime(manifest_path)
    _, game, prefix, output = _manifest(manifest_path)
    output.mkdir(parents=True, exist_ok=True)
    lock_path = output.parent / ".smoke.lock"
    lock = lock_path.open("a+", encoding="utf-8")
    try:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
        lock.close()
        raise RuntimeSafetyError("runtime smoke already owns this prefix") from exc
    log = (output / "runtime.log").open("a", encoding="utf-8")
    env = dict(os.environ, WINEPREFIX=str(prefix), WINEARCH="win32", WINEDEBUG="-all",
               LANG="ko_KR.UTF-8", LC_ALL="ko_KR.UTF-8", WINEDLLOVERRIDES="ddraw=b")
    if _prefix_pids(prefix):
        lock.close()
        raise RuntimeSafetyError("Wine prefix is already in use")
    children: list[subprocess.Popen[Any]] = []
    screenshots: list[dict[str, object]] = []
    evidence: dict[str, object] = {"manifest": checked, "timeout_seconds": timeout, "screenshots": screenshots,
                                   "input": {"action": "title_random_game", "x": 184, "y": 560,
                                             "expected_ps": 7}}
    run_id = _real(manifest_path).parent.name
    started = time.monotonic()
    xvfb: subprocess.Popen[Any] | None = None
    try:
        xvfb, display = _xvfb(log)
        env["DISPLAY"] = display
        shell = subprocess.Popen(["wine", "explorer", "/desktop=Default,1024x768"], cwd=game, env=env, stdout=log, stderr=log)
        children.append(shell)
        time.sleep(1)
        try:
            baseline_tree = _window_tree(display, _remaining(started, timeout))
        except RuntimeSafetyError:
            baseline_tree = ""
        if time.monotonic() >= started + timeout:
            raise RuntimeSafetyError("smoke deadline exceeded before game launch")
        proc = subprocess.Popen(["wine", str(game / ORIGINAL_EXE)], cwd=game, env=env, stdout=log, stderr=log)
        children.append(proc)
        evidence["display"] = display
        evidence["game_pid"] = proc.pid
        evidence["processes"] = [_proc(p.pid) for p in children]
        # The imported offsets are read-only and guarded by check_runtime's
        # exact original SHA.  Poll until both the real game window and the
        # existing state reader become available; launcher-PID liveness alone
        # is never reported as startup success.
        if str(REPO_ROOT) not in sys.path:
            sys.path.insert(0, str(REPO_ROOT))
        from patches.population.runtime_driver import state as read_game_state
        state: dict[str, object] | None = None
        tree = ""
        state_errors: list[str] = []
        while state is None and time.monotonic() - started < timeout:
            try:
                tree = _window_tree(display, _remaining(started, timeout))
                cmdline = _proc(proc.pid).get("cmdline", "")
                if not isinstance(cmdline, str) or str(game / ORIGINAL_EXE) not in cmdline:
                    raise RuntimeSafetyError("Wine launcher has not become the private original EXE")
                if baseline_tree and tree == baseline_tree:
                    raise RuntimeSafetyError("no new game window beyond Wine desktop")
                candidate_state = read_game_state(proc.pid)
                candidate_ps = candidate_state.get("ps")
                if not isinstance(candidate_ps, int) or (candidate_ps & 0xFFFF) != 9:
                    raise RuntimeSafetyError("original title/menu state PS=9 not reached")
                state = candidate_state
            except RuntimeSafetyError as exc:
                if "_inmm registry error" in str(exc):
                    raise
                state_errors.append(str(exc))
            except (OSError, ValueError, struct.error) as exc:
                state_errors.append(type(exc).__name__)
            if state is None:
                time.sleep(min(0.5, _remaining(started, timeout)))
        if state is None:
            raise RuntimeSafetyError("game readiness/state unavailable before smoke deadline")
        evidence["window_tree_baseline"] = baseline_tree
        baseline_ids = _window_ids(baseline_tree)
        candidates = [item for item in _game_window_candidates(tree) if item[0] not in baseline_ids]
        if not candidates:
            raise RuntimeSafetyError("no new 700x500..1000x700 game window beyond Wine desktop")
        target_id, target_width, target_height = candidates[0]
        evidence["window_tree"] = tree
        evidence["window_ids"] = [item[0] for item in candidates]
        evidence["target_window"] = {"id": target_id, "width": target_width, "height": target_height}
        evidence["readiness"] = "xwininfo game window + read-only original state observed"
        evidence["state_errors_before_ready"] = state_errors[-10:]
        process_state = _proc(proc.pid)
        state_record = _normalize_state(state, process_state)
        evidence["state"] = state_record
        observed_exe_hash = _sha256(game / ORIGINAL_EXE)
        _write_json(output / "session.json", {"game_pid": proc.pid, "exe": str(game / ORIGINAL_EXE),
                                               "exe_sha256": observed_exe_hash,
                                               "expected_original_sha256": ORIGINAL_SHA256,
                                               "display": display, "prefix": str(prefix),
                                               "root": str(game)})
        _write_json(output / "latest.json", state_record)
        (output / "trace.jsonl").write_text(json.dumps(state_record, ensure_ascii=False) + "\n")
        _first, first_record = _capture_screenshot(display, run_id, proc.pid,
                                                  "startup", _remaining(started, timeout))
        screenshots.append(first_record)
        if proc.poll() is None and time.monotonic() - started < timeout:
            time.sleep(min(2, _remaining(started, timeout)))
            focus = subprocess.run(["xdotool", "windowfocus", target_id], env=env, stdout=log, stderr=log,
                                   timeout=min(10, _remaining(started, timeout)), check=True)
            click = subprocess.run([sys.executable, str(REPO_ROOT / "tools/x11_mouse_click.py"),
                                    "--display", display, "184", "560"], env=env, stdout=log,
                                   stderr=log, timeout=min(10, _remaining(started, timeout)), check=True)
            evidence["input"] = {"action": "title_random_game", "x": 184, "y": 560,
                                  "display_private": True, "target_window": target_id,
                                  "focus_exit": focus.returncode, "inject_exit": click.returncode,
                                  "expected_ps": 7}
            _, second_record = _capture_screenshot(display, run_id, proc.pid,
                                                   "after_random_game", _remaining(started, timeout))
            screenshots.append(second_record)
        else:
            raise RuntimeSafetyError("game exited or smoke deadline elapsed before required input")
        try:
            post_state = read_game_state(proc.pid)
            post_record = _normalize_state(post_state, _proc(proc.pid))
            evidence["state_after_input"] = post_record
            evidence["runtime_progress_observed_after_input"] = post_record.get("tick") != state_record.get("tick")
            evidence["input_effect_observed"] = post_record.get("ps") == 7 and state_record.get("ps") == 9
            if not evidence["input_effect_observed"]:
                raise RuntimeSafetyError("title random-game click did not reach expected PS=7 dialog")
            evidence["screenshot_changed"] = screenshots[-1].get("sha256") != screenshots[-2].get("sha256")
            _write_json(output / "latest.json", post_record)
            with (output / "trace.jsonl").open("a", encoding="utf-8") as trace_file:
                trace_file.write(json.dumps(post_record, ensure_ascii=False) + "\n")
        except (OSError, ValueError, struct.error) as exc:
            evidence["state_after_input_error"] = type(exc).__name__
        evidence["processes_after_input"] = [_proc(p.pid) for p in children]
        evidence["existing_state"] = _existing_state(prefix)
        evidence["elapsed_seconds"] = round(time.monotonic() - started, 3)
        _write_json(output / "smoke.json", evidence)
        return evidence
    except (OSError, subprocess.SubprocessError, RuntimeSafetyError) as exc:
        evidence["error"] = str(exc)
        evidence["elapsed_seconds"] = round(time.monotonic() - started, 3)
        _write_json(output / "smoke.json", evidence)
        raise
    finally:
        for child in children:
            if child.poll() is None:
                child.terminate()
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline and any(child.poll() is None for child in children):
            time.sleep(0.05)
        for child in children:
            if child.poll() is None:
                child.kill()
        for child in children:
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass
        cleanup_error: str | None = None
        try:
            _run(["wineserver", "-k"], env=env, timeout=10, log=output / "runtime.log")
            _run(["wineserver", "-w"], env=env, timeout=10, log=output / "runtime.log")
        except RuntimeSafetyError as exc:
            cleanup_error = str(exc)
        if xvfb is not None and xvfb.poll() is None:
            xvfb.terminate()
            try:
                xvfb.wait(timeout=5)
            except subprocess.TimeoutExpired:
                xvfb.kill()
        cleanup: dict[str, object] = {
            "owned_launchers_stopped": all(child.poll() is not None for child in children),
            "xvfb_stopped": xvfb is None or xvfb.poll() is not None,
            "prefix_target": str(prefix),
            "global_kill_used": False,
            "prefix_processes_after": _prefix_pids(prefix),
            "error": cleanup_error,
        }
        cleanup["ok"] = bool(cleanup["owned_launchers_stopped"] and cleanup["xvfb_stopped"] and
                              not cleanup["prefix_processes_after"] and cleanup_error is None)
        evidence["cleanup"] = cleanup
        try:
            _write_json(output / "smoke.json", evidence)
        except OSError:
            pass
        log.close()
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
        lock.close()
        if not bool(cleanup["ok"]):
            raise RuntimeSafetyError("runtime cleanup incomplete; inspect output/smoke.json")


def runtime_main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare/check/smoke an isolated original game runtime")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    p.add_argument("--runtime-root", type=Path, default=DEFAULT_RUNTIME_ROOT)
    p.add_argument("--bridge", type=Path)
    p.add_argument("--timeout", type=float, default=60)
    c = sub.add_parser("check")
    c.add_argument("--manifest", type=Path, required=True)
    s = sub.add_parser("smoke")
    s.add_argument("--manifest", type=Path, required=True)
    s.add_argument("--timeout", type=float, default=60)
    g = sub.add_parser("g1-baseline")
    g.add_argument("--manifest", type=Path, required=True)
    g.add_argument("--screen", default="1600x1200x24")
    g.add_argument("--timeout", type=float, default=90)
    t = sub.add_parser("g1-presentation-trace")
    t.add_argument("--manifest", type=Path, required=True)
    t.add_argument("--screen", default="1600x1200x24")
    t.add_argument("--timeout", type=float, default=90)
    t.add_argument("--win32-close-helper", type=Path)
    t.add_argument("--dxwrapper-2x", action="store_true")
    t.add_argument("--ps3-dwell-seconds", type=float, default=0.0)
    t.add_argument("--g1-input-sequence", action="store_true")
    r = sub.add_parser("g1-r1-load-origin")
    r.add_argument("--manifest", type=Path, required=True)
    r.add_argument("--screen", default="1600x1200x24")
    r.add_argument("--timeout", type=float, default=90)
    cr = sub.add_parser("g1-r1-candidate-load-origin")
    cr.add_argument("--manifest", type=Path, required=True)
    cr.add_argument("--screen", default="1600x1200x24")
    cr.add_argument("--timeout", type=float, default=90)
    s1 = sub.add_parser("g1-s1-load-evidence")
    s1.add_argument("--fixture", type=Path, required=True)
    s1.add_argument("--fixture-name")
    s1.add_argument("--group-word", type=lambda value: int(value, 0), required=True)
    s1.add_argument("--selected-index", type=lambda value: int(value, 0), required=True)
    s1.add_argument("--post-json", type=Path)
    s1.add_argument("--pid", type=int, help="read two samples from this already-running private game process")
    s1.add_argument("--manifest", type=Path, help="required with --pid to prove the owned private runtime")
    s1.add_argument("--output", type=Path, default=Path("s1_load_evidence.json"))
    s1_original = sub.add_parser("g1-s1-original-load-evidence")
    s1_original.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    s1_original.add_argument("--runtime-root", type=Path, default=DEFAULT_RUNTIME_ROOT)
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            result = prepare(args.source, runtime_root=args.runtime_root, bridge=args.bridge, timeout=args.timeout)
        elif args.command == "check":
            result = check_runtime(args.manifest)
        elif args.command == "smoke":
            result = smoke(args.manifest, timeout=args.timeout)
        elif args.command == "g1-baseline":
            result = g1_baseline(args.manifest, screen=args.screen, timeout=args.timeout)
        elif args.command == "g1-r1-load-origin":
            result = g1_r1_load_origin(args.manifest, screen=args.screen, timeout=args.timeout)
        elif args.command == "g1-r1-candidate-load-origin":
            result = g1_r1_candidate_load_origin(args.manifest, screen=args.screen, timeout=args.timeout)
        elif args.command == "g1-s1-original-load-evidence":
            result = g1_s1_original_load_evidence(args.source, runtime_root=args.runtime_root)
        elif args.command == "g1-s1-load-evidence":
            if args.pid is not None and args.post_json is not None:
                raise RuntimeSafetyError("g1-s1-load-evidence accepts either --pid or --post-json, not both")
            post: Mapping[str, Any] | None = None
            if args.post_json is not None:
                loaded = json.loads(args.post_json.read_text(encoding="utf-8"))
                if not isinstance(loaded, Mapping):
                    raise ValueError("post JSON root must be an object")
                post = loaded
            read_memory: Callable[[int, int], bytes] | None = None
            if args.pid is not None:
                if args.pid <= 0:
                    raise RuntimeSafetyError("g1-s1-load-evidence requires a positive private process PID")
                if args.manifest is None:
                    raise RuntimeSafetyError("g1-s1-load-evidence --pid requires --manifest")
                check_runtime(args.manifest)
                _, _, private_prefix, _ = _manifest(args.manifest)
                if args.pid not in _prefix_pids(private_prefix):
                    raise RuntimeSafetyError("g1-s1-load-evidence PID is not owned by the private Wine prefix")
                from patches.population.runtime_driver import read as process_read

                def read_process_memory(address: int, size: int) -> bytes:
                    return process_read(args.pid, address, size)

                read_memory = read_process_memory
            result = g1_s1_load_evidence(
                args.fixture, fixture_name=args.fixture_name or args.fixture.name,
                group_word=args.group_word, selected_index=args.selected_index,
                post=post, read_memory=read_memory, output=args.output,
            )
        else:
            result = g1_presentation_trace(
                args.manifest, screen=args.screen, timeout=args.timeout,
                close_helper=args.win32_close_helper,
                dxwrapper_2x=args.dxwrapper_2x,
                ps3_dwell_seconds=args.ps3_dwell_seconds,
                g1_input_sequence=args.g1_input_sequence,
            )
    except RuntimeSafetyError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.command == "smoke":
        cleanup = result.get("cleanup")
        if not isinstance(cleanup, dict) or not bool(cleanup.get("ok", False)):
            return 2
    if args.command == "g1-s1-original-load-evidence" and result.get("status") != "PASS":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(runtime_main())
