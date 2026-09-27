#!/usr/bin/env python3
"""Safe environment probes plus isolated original-game runtime smoke tools.

The probe functions are side-effect free.  The explicit ``prepare`` and
``smoke`` commands are the only functions that create a private copy/prefix
or launch a game; they never patch binaries, start loop services, or start a
model session.
"""

from __future__ import annotations

import ctypes.util
import collections
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
# 2026-09-26 사용자 결정: 원본 게임 기준 경로를 [ESL]Syw2plus/로 전환(보호 원본 EXE는
# 그 안의 "[HQ]Syw2plus 2002.exe", SHA는 기존과 동일). 옛 경로(Syw2plus_re/Syw2plus)는
# 읽기 전용 참고로 보존하며 기본 소스로는 더 이상 쓰지 않는다.
DEFAULT_SOURCE = (REPO_ROOT.parent / "[ESL]Syw2plus").resolve()
LEGACY_SOURCE = (REPO_ROOT.parent / "Syw2plus_re" / "Syw2plus").resolve()
DEFAULT_RUNTIME_ROOT = REPO_ROOT / "local" / "runtime"
SCREENSHOT_ROOT = Path("/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/captures")
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
G1_S1_LOAD_BUTTON_POINT: tuple[int, int] = (316, 372)
G1_S1_MINIMAP_PROBE_POINT: tuple[int, int] = (35, 560)
G1_S1_DESELECT_PROBE_POINT: tuple[int, int] = (400, 220)
G1_S1_DRAG_PROBE_BOUNDS: tuple[int, int, int, int] = (520, 200, 780, 455)
G1_S1_SLOT_NAV_MAX_PRESSES = 12
G1_S1_SLOT_NAV_BUDGET = 5.0
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


G4_AI_SHADOW_ENV = "INMM_AI_SHADOW"
G4_AI_SHADOW_RELATIVE_PATH = Path("drive_c") / "inmm_ai_shadow.jsonl"
G4_POSTLOAD_MIN_ROWS = 17
G4_POSTLOAD_WAIT_BUDGET = 45.0
G4_POSTLOAD_POLL_INTERVAL = 0.2


def _g4_wait_for_postload_rows(
    prefix: Path, *, deadline: float, min_rows: int = G4_POSTLOAD_MIN_ROWS,
    poll_interval: float = G4_POSTLOAD_POLL_INTERVAL,
) -> dict[str, Any]:
    """Poll the private shadow artifact until the bounded post-load window fills.

    Read-only: this only gives the already-running private game process real
    time to emit AI-shadow rows before the caller proceeds to teardown. It
    does not install, judge, or PASS/FAIL the post-load contract itself.
    """

    shadow_path = prefix / G4_AI_SHADOW_RELATIVE_PATH
    attempts = 0
    marker_count = 0
    postload_rows = 0
    last_error: str | None = None
    while True:
        attempts += 1
        try:
            lines = shadow_path.read_text(encoding="utf-8").splitlines()
            events = [json.loads(line) for line in lines if line.strip()]
            marker_indices = [i for i, e in enumerate(events) if e.get("event") == "load_complete"]
            marker_count = len(marker_indices)
            if marker_count >= 1:
                last_marker_index = marker_indices[-1]
                postload_rows = sum(
                    1 for e in events[last_marker_index + 1 :] if e.get("event") == "ai_shadow"
                )
            last_error = None
        except (OSError, json.JSONDecodeError) as exc:
            last_error = f"{type(exc).__name__}: {exc}"
        if marker_count >= 1 and postload_rows >= min_rows:
            break
        if time.monotonic() >= deadline:
            break
        time.sleep(poll_interval)
    return {
        "attempts": attempts, "marker_count": marker_count,
        "postload_rows": postload_rows, "min_rows_observed": postload_rows >= min_rows,
        "error": last_error,
    }


def _g4_postload_contract(
    events: list[dict[str, Any]], *, expected_run_id: str,
) -> dict[str, Any]:
    """Validate the bounded marker/first-edge sequence without trusting summaries."""

    markers = [event for event in events if event.get("event") == "load_complete"]
    rows = [event for event in events if event.get("event") == "ai_shadow"]
    result: dict[str, Any] = {
        "pass": False, "marker_count": len(markers), "postload_rows": 0,
        "error": None,
    }
    try:
        if len(markers) != 1:
            raise RuntimeSafetyError(f"G4 exact post-load requires one marker, got {len(markers)}")
        marker = markers[0]
        if marker.get("run_id") != expected_run_id or marker.get("result") != 1:
            raise RuntimeSafetyError("G4 exact post-load marker identity/result is invalid")
        marker_seq = marker["seq"]
        tpre, tload = marker["tpre"], marker["tload"]
        if not isinstance(marker_seq, int) or not isinstance(tpre, int) or not isinstance(tload, int):
            raise RuntimeSafetyError("G4 exact post-load marker has non-integer timing")
        if marker.get("candidate_present") is not False or marker.get("candidate_issue_count") != 0:
            raise RuntimeSafetyError("G4 exact post-load marker has candidate activity")
        if not isinstance(marker.get("source"), dict):
            raise RuntimeSafetyError("G4 exact post-load marker source is missing")
        if marker.get("next_owner") != ((tload + 1) & 7):
            raise RuntimeSafetyError("G4 exact post-load marker owner is inconsistent")
        if any(event.get("run_id") != expected_run_id for event in events):
            raise RuntimeSafetyError("G4 exact post-load event run_id mismatch")
        raw_sequences = [event.get("seq") for event in events]
        if any(not isinstance(seq, int) for seq in raw_sequences):
            raise RuntimeSafetyError("G4 exact post-load sequence is not strictly monotonic")
        sequences: list[int] = [seq for seq in raw_sequences if isinstance(seq, int)]
        if sequences != sorted(set(sequences)):
            raise RuntimeSafetyError("G4 exact post-load sequence is not strictly monotonic")
        marker_index = events.index(marker)
        post_rows = [event for event in rows if events.index(event) > marker_index]
        result["postload_rows"] = len(post_rows)
        if len(post_rows) < 17:
            raise RuntimeSafetyError("G4 exact post-load bounded window is incomplete")
        first = post_rows[0]
        if first.get("seq") != marker_seq + 1 or first.get("tick") != tload + 1:
            raise RuntimeSafetyError("G4 exact post-load first edge is not adjacent to marker")
        if (first.get("pid"), first.get("tid")) != (marker.get("pid"), marker.get("tid")):
            raise RuntimeSafetyError("G4 exact post-load marker/edge thread identity mismatch")
        expected_owner = first["tick"] & 7
        if first.get("owner") != expected_owner:
            raise RuntimeSafetyError("G4 exact post-load first edge owner mismatch")
        if first.get("entry_ecx") != 0x956770 + expected_owner * 0x3ABC:
            raise RuntimeSafetyError("G4 exact post-load first edge ECX mismatch")
        raw_mode = first.get("raw_mode")
        mode = ("program_state", "committed_local", "scenario_selector", "network_mode",
                "network_modal", "gate_a", "gate_b")
        if not isinstance(raw_mode, dict) or tuple(raw_mode.get(key) for key in mode) != (3, 1, 0, 0, 0, 0, 0):
            raise RuntimeSafetyError("G4 exact post-load first edge mode mismatch")
        if first.get("original_call") != "forwarded_once":
            raise RuntimeSafetyError("G4 exact post-load first edge was not forwarded exactly once")
        if first.get("tick_rewind") != ((tload + 1) < tpre):
            raise RuntimeSafetyError("G4 exact post-load tick rewind predicate mismatch")
        # A 0==0 match (marker full_id/slot both 0, first row source.live
        # False) is vacuous: find_source() in ai_shadow.c zeroes every field
        # and reports live=FALSE when the owner has no live unit, so an
        # all-zero marker/edge pair "agrees" without ever proving the
        # load-boundary source identity survived the load. Fail closed on
        # that case instead of accepting the empty match (lap701 finding).
        marker_full_id, marker_slot = marker["source"].get("full_id"), marker["source"].get("slot")
        if not isinstance(marker_full_id, int) or not isinstance(marker_slot, int) or marker_full_id == 0 or marker_slot == 0:
            raise RuntimeSafetyError("G4 exact post-load marker source is absent (no live unit for owner)")
        if (marker_full_id & 0xFFFF) != marker_slot:
            raise RuntimeSafetyError("G4 exact post-load marker source full_id/slot mismatch")
        if first.get("source", {}).get("live") is not True:
            raise RuntimeSafetyError("G4 exact post-load first edge source is not live")
        # The marker's "source" object embeds "owner" (see ai_shadow.c
        # append_source); the shadow row instead carries "owner" as its own
        # top-level field and omits it from the nested "source" object. Same
        # authoritative value, different JSON location per each event's
        # documented schema (card §3) — compare accordingly, not key-for-key.
        if marker["source"].get("owner") != first.get("owner"):
            raise RuntimeSafetyError("G4 exact post-load marker/edge source mismatch")
        source_keys = ("full_id", "slot", "command", "pending", "pending_xy")
        if {key: marker["source"].get(key) for key in source_keys} != {
            key: first.get("source", {}).get(key) for key in source_keys
        }:
            raise RuntimeSafetyError("G4 exact post-load marker/edge source mismatch")
        window = post_rows[:17]
        if any(row.get("load_marker_seq") != marker_seq for row in window):
            raise RuntimeSafetyError("G4 exact post-load marker sequence is not attached to the window")
        if len({row.get("tick") for row in window}) != len(window):
            raise RuntimeSafetyError("G4 exact post-load window has duplicate ticks")
        if any(row.get("same_tick_reentry") is not False for row in window):
            raise RuntimeSafetyError("G4 exact post-load window contains same-tick reentry")
        if any(row.get("candidate_present") is not False or row.get("candidate_issue_count") != 0 for row in window):
            raise RuntimeSafetyError("G4 exact post-load window has candidate activity")
        result.update({"pass": True, "marker_seq": marker_seq, "first_seq": first["seq"]})
    except (KeyError, TypeError, ValueError, RuntimeSafetyError) as exc:
        result["error"] = str(exc)
    return result


def _g4_shadow_provenance(
    prefix: Path, env: Mapping[str, str | None], *,
    require_postload: bool = False, expected_run_id: str | None = None,
) -> dict[str, Any]:
    """Record the opt-in G4 shadow artifact without trusting external paths."""

    requested = env.get(G4_AI_SHADOW_ENV)
    shadow_path = prefix / G4_AI_SHADOW_RELATIVE_PATH
    result: dict[str, Any] = {
        "enabled": requested == "1",
        "environment_value": requested if requested == "1" else None,
        "relative_path": str(G4_AI_SHADOW_RELATIVE_PATH),
        "path": str(_real(shadow_path)),
        "private_prefix": False,
        "exists": False,
        "sha256": None,
        "row_count": None,
        "marker_count": 0,
        "postload": None,
        "status": "DISABLED" if requested != "1" else "FAIL",
        "pass": False,
        "error": None,
    }
    if requested != "1":
        return result

    try:
        _reject_path_links(prefix)
        _reject_path_links(shadow_path)
        resolved_prefix = _real(prefix)
        resolved_shadow = _real(shadow_path)
        if not _under(resolved_shadow, resolved_prefix):
            raise RuntimeSafetyError("G4 shadow path escaped the private Wine prefix")
        result["path"] = str(resolved_shadow)
        result["private_prefix"] = True
        if not shadow_path.is_file() or shadow_path.is_symlink():
            raise RuntimeSafetyError("G4 shadow artifact is missing or linked")
        result["exists"] = True
        if shadow_path.stat().st_size <= 0:
            raise RuntimeSafetyError("G4 shadow artifact is empty")
        rows = 0
        events: list[dict[str, Any]] = []
        with shadow_path.open("r", encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, start=1):
                if not line.strip():
                    raise RuntimeSafetyError(
                        f"G4 shadow artifact has an empty row at line {line_number}"
                    )
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise RuntimeSafetyError(
                        f"G4 shadow artifact row {line_number} is not an object"
                    )
                rows += 1
                events.append(value)
        if rows == 0:
            raise RuntimeSafetyError("G4 shadow artifact has no rows")
        result["sha256"] = _sha256(shadow_path)
        result["row_count"] = rows
        result["marker_count"] = sum(event.get("event") == "load_complete" for event in events)
        if require_postload:
            if expected_run_id is None:
                raise RuntimeSafetyError("G4 exact post-load provenance requires a run_id")
            result["postload"] = _g4_postload_contract(
                events, expected_run_id=expected_run_id,
            )
            if result["postload"]["pass"] is not True:
                raise RuntimeSafetyError(str(result["postload"].get("error") or "post-load contract failed"))
        result["status"] = "PASS"
        result["pass"] = True
    except (OSError, RuntimeSafetyError, TypeError, ValueError) as exc:
        result["error"] = str(exc)
    return result


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    tmp.replace(path)


def _protected_roots() -> tuple[Path, ...]:
    return tuple(_real(p) for p in (REPO_ROOT / "Syw2plus", REPO_ROOT.parent / "Syw2plus"))


def validate_original_source(source: Path) -> tuple[Path, Path]:
    """Validate a real, complete source and find the exact original executable.

    The original executable is identified by SHA-256/size, not a fixed file
    name: different source roots ship it under different names (e.g.
    ``syw2plus_original.exe`` vs ``[HQ]Syw2plus 2002.exe``).
    """
    _reject_path_links(source)
    source = source.expanduser()
    source = _real(source)
    if source.is_symlink() or not source.is_dir():
        raise RuntimeSafetyError(f"unsafe source directory: {source}")
    if any(source == root or root in source.parents for root in _protected_roots()):
        raise RuntimeSafetyError(f"unsafe/protected source directory: {source}")
    preferred = source / ORIGINAL_EXE
    preferred_digest: str | None = None
    if preferred.exists() or preferred.is_symlink():
        if preferred.is_symlink() or not preferred.is_file():
            raise RuntimeSafetyError(f"missing or linked original executable: {preferred}")
        preferred_digest = _sha256(preferred)
        if preferred_digest == ORIGINAL_SHA256:
            return source, preferred
    for candidate in sorted(source.glob("*.exe")):
        if candidate == preferred or candidate.is_symlink() or not candidate.is_file():
            continue
        if _sha256(candidate) == ORIGINAL_SHA256:
            return source, candidate
    if preferred_digest is not None:
        # A file already sits at the conventional name but its content is
        # wrong; surface that distinctly from "nothing here at all".
        raise RuntimeSafetyError(f"original SHA-256 mismatch: {preferred_digest}")
    raise RuntimeSafetyError(
        f"original executable (expected SHA-256 {ORIGINAL_SHA256}) not found under {source}"
    )


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
        copied_source_exe = game / source_exe.name
        if _sha256(copied_source_exe) != ORIGINAL_SHA256:
            raise RuntimeSafetyError("private original executable failed post-copy hash")
        copied_exe = game / ORIGINAL_EXE
        if copied_exe != copied_source_exe:
            # Source ships the original under a different file name (e.g. the
            # new [ESL]Syw2plus root); keep the conventional ORIGINAL_EXE name
            # inside the private copy so every downstream ``game / ORIGINAL_EXE``
            # reference keeps working unchanged.
            shutil.copy2(copied_source_exe, copied_exe)
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
            "source": {"root": str(source), "exe": source_exe.name, "exe_sha256": _sha256(source_exe),
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
    native_2x_stretch: bool = False,
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
        from tools.check_g1_presentation_trace import validate_native_split
        if native_2x_stretch:
            evidence["validator"] = validate_native_split(trace_copy, capture=capture)
        else:
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


def _module_evidence(pid: int, executable_name: str = ORIGINAL_EXE) -> dict[str, object]:
    maps_path = Path(f"/proc/{pid}/maps")
    try:
        maps_raw = maps_path.read_bytes()
    except OSError as exc:
        raise RuntimeSafetyError(f"cannot read process maps: {exc}") from exc
    text_maps = maps_raw.decode(errors="replace")
    executable_key = executable_name.lower()
    modules: dict[str, dict[str, Any]] = {}
    for line in text_maps.splitlines():
        fields = line.split(maxsplit=5)
        if len(fields) != 6:
            continue
        path = fields[5].strip()
        lowered = path.lower()
        if executable_key not in lowered and "ddraw" not in lowered:
            continue
        entry = modules.setdefault(path, {"path": path, "mapped_ranges": 0})
        entry["mapped_ranges"] = int(entry["mapped_ranges"]) + 1
    if not any(executable_key in path.lower() for path in modules):
        raise RuntimeSafetyError("process maps do not contain the launched verified executable")
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
    dxwrapper_2x: bool = False, minimap_probe: bool = False, deselect_probe: bool = False,
    ps35_screenshot: bool = False, drag_probe: bool = False,
    bridge: Path | None = None, g4_exact_postload: bool = False,
    g4_load_fixture: str | None = None,
) -> dict[str, Any]:
    """Own one bounded original save000 load observation from copy to cleanup.

    This is the only S1 path that launches the original game.  It creates a
    fresh private copy/prefix through :func:`prepare`, uses exactly one menu
    click for PS9->PS35 and one strict-interior load click, and writes one new
    artifact after owned cleanup.  It intentionally performs no memory writes.

    ``g4_load_fixture`` is an opt-in override of the default save000 fixture,
    usable only together with ``g4_exact_postload`` (e.g. to pick save006.dat
    when save000's deterministic next-load owner has no live unit — see
    G4_W2_EXACT_POSTLOAD_MARKER_LAP623 card §7). It must name an entry already
    pinned in ``s1.FIXTURES``.
    """

    from tools import s1_load_evidence as s1

    if g4_exact_postload and bridge is None:
        raise RuntimeSafetyError("G4 exact post-load requires an explicit --bridge")
    if bridge is not None and not g4_exact_postload:
        raise RuntimeSafetyError("G4 --bridge requires --g4-exact-postload")
    if g4_load_fixture is not None and not g4_exact_postload:
        raise RuntimeSafetyError("G4 --g4-load-fixture requires --g4-exact-postload")
    if g4_load_fixture is not None and g4_load_fixture not in s1.FIXTURES:
        raise RuntimeSafetyError(f"G4 --g4-load-fixture is not a pinned fixture: {g4_load_fixture}")

    command_started = time.monotonic()
    operation_deadline = command_started + G1_S1_TOTAL_DEADLINE - G1_S1_CLEANUP_RESERVE
    fixture_spec = s1.FIXTURES[g4_load_fixture or "save000.dat"]
    prepare_started = command_started
    source_real, source_exe = validate_original_source(source)
    source_fixture = source_real / "save" / fixture_spec.name
    source_fixture_identity = _s1_file_identity(
        source_fixture, expected_size=fixture_spec.expected_size,
        expected_sha256=fixture_spec.expected_sha256,
    )
    if source_fixture_identity["status"] != "PASS":
        raise RuntimeSafetyError(f"NO_RUN: protected source {fixture_spec.name} identity is not pinned")
    if time.monotonic() - prepare_started > G1_S1_STAGE_BUDGETS["prepare"]:
        raise RuntimeSafetyError("S1 prepare stage exceeded its 60 second cap")
    manifest = prepare(
        source_real, runtime_root=runtime_root,
        bridge=bridge,
        timeout=_s1_stage_timeout(command_started, prepare_started, G1_S1_STAGE_BUDGETS["prepare"]),
    )
    if time.monotonic() - prepare_started > G1_S1_STAGE_BUDGETS["prepare"]:
        raise RuntimeSafetyError("S1 prepare stage exceeded its 60 second cap")
    manifest_path = _real(Path(str(manifest["output"]["run_dir"]))) / "manifest.json"  # type: ignore[index]
    checked = check_runtime(manifest_path)
    data, game, prefix, output = _manifest(manifest_path)
    run_id = manifest_path.parent.name
    variant = "candidate-dxwrapper-2x" if dxwrapper_2x else "original"
    artifact_name = "s1_candidate_load_evidence.json" if dxwrapper_2x else "s1_original_load_evidence.json"
    artifact_path = output / artifact_name
    artifact_temp_path = artifact_path.with_name(f".{artifact_path.name}.tmp")
    log_path = output / "s1_original_load_evidence.log"
    evidence: dict[str, Any] = {
        "status": "UNKNOWN",
        "classification": "NOT_STARTED",
        "variant": variant,
        "scope": {
            "game_started": False, "wine_started": False, "xvfb_started": False,
            "memory_writes": False, "product_g1_pass": False,
        },
        "run_id": run_id,
        "g4_exact_postload": g4_exact_postload,
        "manifest": checked,
        "deadline_seconds": G1_S1_TOTAL_DEADLINE,
        "operation_deadline_seconds": G1_S1_TOTAL_DEADLINE - G1_S1_CLEANUP_RESERVE,
        "fixture": {
            "name": fixture_spec.name, "group_word": 0, "selected_index": fixture_spec.selected_index,
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
            "load_trigger": {"count": 0, "logical": list(G1_S1_LOAD_BUTTON_POINT), "scale": [1.0, 1.0]},
        },
        "minimap_probe": {"enabled": minimap_probe, "status": "NOT_RUN"},
        "deselect_probe": {"enabled": deselect_probe, "status": "NOT_RUN"},
        "ps35_screenshot": {"enabled": ps35_screenshot, "status": "NOT_CAPTURED"},
        "drag_probe": {"enabled": drag_probe, "status": "NOT_RUN"},
        "reads": {
            "program_state": {"address": hex(s1.PROGRAM_STATE_ADDRESS), "width": 2, "wait_raw": []},
            "origin": {"address": hex(G1_R1_ORIGIN_ADDRESS), "width": G1_R1_ORIGIN_READ_SIZE},
        },
        "cleanup": None,
        "dxwrapper_config": {
            "enabled": dxwrapper_2x,
            "winedlloverrides": "ddraw=n,b" if dxwrapper_2x else "ddraw=b",
        },
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
    dxwrapper_install: dict[str, object] | None = None
    log = log_path.open("a", encoding="utf-8")

    try:
        if (_prefix_pids(prefix) or _existing_state(prefix)
                or artifact_path.exists() or artifact_path.is_symlink()
                or artifact_temp_path.exists() or artifact_temp_path.is_symlink()):
            raise RuntimeSafetyError("S1 original load requires a fresh private prefix and output")
        candidate_exe = game / ORIGINAL_EXE
        candidate_fixture = game / "save" / fixture_spec.name
        if dxwrapper_2x:
            from patches.resolution import dxwrapper_config

            dxwrapper_install = dxwrapper_config.install_private(game)
            evidence["dxwrapper_config"]["install"] = dxwrapper_install
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
                LANG="ko_KR.UTF-8", LC_ALL="ko_KR.UTF-8",
                WINEDLLOVERRIDES="ddraw=n,b" if dxwrapper_2x else "ddraw=b",
            )
            if g4_exact_postload:
                env["INMM_AI_SHADOW"] = "1"
                env["INMM_G4_RUN_ID"] = run_id
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
            expected_content_size = (1600, 1200) if dxwrapper_2x else (800, 600)
            if dxwrapper_2x:
                outer_id, content_id = _game_window_ids(
                    tree, allowed_sizes=(expected_content_size,),
                )
            else:
                outer_id, content_id = _game_window_ids(tree)
            if content_id is None:
                raise RuntimeSafetyError(
                    f"S1 {variant} game window has no {expected_content_size[0]}x{expected_content_size[1]} content child"
                )
            root_match = re.search(r"Window id: (0x[0-9a-fA-F]+) \(the root window\)", tree)
            if root_match is None:
                raise RuntimeSafetyError("S1 X11 root window id is missing")
            root_info = _xwininfo_details(display, root_match.group(1), _s1_stage_timeout(command_started, input_started, 20.0))
            content_info = _xwininfo_details(display, content_id, _s1_stage_timeout(command_started, input_started, 20.0))
            if (int(root_info["width"]), int(root_info["height"])) != (1600, 1200):
                raise RuntimeSafetyError("S1 Xvfb root is not 1600x1200")
            if (int(content_info["width"]), int(content_info["height"])) != expected_content_size:
                raise RuntimeSafetyError(
                    f"S1 game content crop is not exactly {expected_content_size[0]}x{expected_content_size[1]}"
                )
            if dxwrapper_2x:
                modules = _module_evidence(proc.pid)
                game_manifest = data.get("game")
                support_hashes = (
                    game_manifest.get("support_dll_sha256", {})
                    if isinstance(game_manifest, Mapping) else {}
                )
                evidence["module_gate"] = _g1_r1_candidate_module_gate(
                    modules, game, support_hashes,
                )
            content_crop = (
                int(content_info["x"]), int(content_info["y"]),
                expected_content_size[0], expected_content_size[1],
            )
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

            if fixture_spec.selected_index != 1:
                # PS35 entry hard-initializes the highlighted slot to 1
                # (0x4D5CA0, see docs/history/laps/20260912_lap362_...); a
                # non-default fixture (save006.dat, slot 7) needs an explicit
                # list-cursor move before the Load click, verified by
                # re-reading SELECTED_INDEX_ADDRESS rather than assuming any
                # fixed number of keypresses worked.
                nav_started = time.monotonic()
                nav_observations: list[dict[str, Any]] = []
                nav_attempts = 0
                while True:
                    raw_index = read_memory(s1.SELECTED_INDEX_ADDRESS, 2)
                    current_index = int.from_bytes(raw_index, "little", signed=False) if len(raw_index) == 2 else None
                    nav_observations.append({
                        "attempt": nav_attempts, "selected_index": current_index,
                        "elapsed_seconds": round(time.monotonic() - nav_started, 3),
                    })
                    if current_index == fixture_spec.selected_index:
                        break
                    if nav_attempts >= G1_S1_SLOT_NAV_MAX_PRESSES or time.monotonic() > operation_deadline:
                        evidence["stages"]["slot_navigation"] = {
                            "status": "FAIL", "attempts": nav_attempts, "observations": nav_observations,
                            "start_elapsed": round(nav_started - command_started, 3),
                            "end_elapsed": round(time.monotonic() - command_started, 3),
                            "elapsed_seconds": round(time.monotonic() - nav_started, 3),
                        }
                        raise RuntimeSafetyError(
                            "S1 slot navigation could not reach "
                            f"selected_index={fixture_spec.selected_index} within "
                            f"{G1_S1_SLOT_NAV_MAX_PRESSES} DOWN presses (last observed {current_index})"
                        )
                    nav_key_argv = [sys.executable, str(REPO_ROOT / "tools/x11_send_keys.py"),
                                     "--display", display, "DOWN"]
                    subprocess.run(
                        nav_key_argv, env=env, stdout=log, stderr=log,
                        timeout=_s1_stage_timeout(command_started, nav_started, G1_S1_SLOT_NAV_BUDGET), check=True,
                    )
                    nav_attempts += 1
                    time.sleep(0.15)
                evidence["stages"]["slot_navigation"] = {
                    "status": "PASS", "attempts": nav_attempts, "observations": nav_observations,
                    "start_elapsed": round(nav_started - command_started, 3),
                    "end_elapsed": round(time.monotonic() - command_started, 3),
                    "elapsed_seconds": round(time.monotonic() - nav_started, 3),
                    "helper_sha256": _sha256(REPO_ROOT / "tools" / "x11_send_keys.py"),
                }
                if time.monotonic() > operation_deadline:
                    raise RuntimeSafetyError("S1 slot navigation exceeded the operation deadline")

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
            if (pre.get("ps"), pre.get("group_word"), pre.get("selected_index")) != (35, 0, fixture_spec.selected_index):
                raise RuntimeSafetyError(
                    f"S1 direct pre did not observe PS35/group0/slot{fixture_spec.selected_index}"
                )
            if pre_elapsed > G1_S1_STAGE_BUDGETS["direct_pre"]:
                raise RuntimeSafetyError("S1 direct pre stage exceeded its 2 second cap")
            if ps35_screenshot:
                capture_started = time.monotonic()
                menu_path, menu_record = _capture_screenshot(
                    display, run_id, proc.pid, "s1_ps35_load_menu",
                    _s1_stage_timeout(command_started, capture_started, 3.0), crop=content_crop,
                )
                if menu_record.get("dimensions") != list(expected_content_size):
                    raise RuntimeSafetyError("S1 PS35 screenshot does not match content dimensions")
                capture_elapsed = time.monotonic() - capture_started
                if capture_elapsed > 3.0:
                    raise RuntimeSafetyError("S1 PS35 screenshot exceeded its 3 second cap")
                evidence["ps35_screenshot"] = {
                    "enabled": True, "status": "PASS", "path": str(menu_path),
                    "capture": menu_record, "elapsed_seconds": round(capture_elapsed, 3),
                }

            trigger_started: float | None = None
            trigger_finished: float | None = None
            trigger_evidence = evidence["input"]["load_trigger"]

            def trigger() -> int:
                nonlocal trigger_started, trigger_finished
                trigger_started = time.monotonic()
                trigger_root = [
                    content_crop[0] + G1_S1_LOAD_BUTTON_POINT[0],
                    content_crop[1] + G1_S1_LOAD_BUTTON_POINT[1],
                ]
                focus_result = subprocess.run(
                    ["xdotool", "windowfocus", outer_id], env=env, stdout=log, stderr=log,
                    timeout=_s1_stage_timeout(command_started, trigger_started, G1_S1_STAGE_BUDGETS["load_trigger"]), check=True,
                )
                trigger_argv = [sys.executable, str(REPO_ROOT / "tools/x11_mouse_click.py"), "--display", display, *map(str, trigger_root)]
                click_result = subprocess.run(
                    trigger_argv, env=env, stdout=log, stderr=log,
                    timeout=_s1_stage_timeout(command_started, trigger_started, G1_S1_STAGE_BUDGETS["load_trigger"]), check=True,
                )
                trigger_finished = time.monotonic()
                trigger_evidence.update({
                    "count": 1, "root": trigger_root, "content_crop": list(content_crop),
                    "target_window": outer_id, "focus_exit": focus_result.returncode,
                    "inject_exit": click_result.returncode, "argv": trigger_argv,
                    "helper_sha256": _sha256(REPO_ROOT / "tools" / "x11_mouse_click.py"),
                    "invocation_count": 1,
                    "stage_start_elapsed": round(trigger_started - command_started, 3),
                    "stage_end_elapsed": round(trigger_finished - command_started, 3),
                    "stage_elapsed_seconds": round(trigger_finished - trigger_started, 3),
                })
                trigger_elapsed = trigger_finished - trigger_started
                if trigger_elapsed > G1_S1_STAGE_BUDGETS["load_trigger"]:
                    raise RuntimeSafetyError(
                        f"S1 load trigger stage exceeded its {G1_S1_STAGE_BUDGETS['load_trigger']} second cap"
                    )
                if time.monotonic() > operation_deadline:
                    raise RuntimeSafetyError("S1 load trigger exceeded the operation deadline")
                return 1

            def precondition(sample: Mapping[str, Any]) -> Mapping[str, Any]:
                if (sample.get("ps"), sample.get("group_word"), sample.get("selected_index")) != (
                    35, 0, fixture_spec.selected_index,
                ):
                    raise RuntimeSafetyError("S1 precondition changed before load trigger")
                return {"ps": 35, "group_word": 0, "selected_index": fixture_spec.selected_index, "origin": origin_pre}

            collected = s1.collect_load_event_boundary(
                read_memory, trigger=trigger, timeout=G1_S1_STAGE_BUDGETS["ps3_wait"],
                precondition=precondition, pre_snapshot=pre, event_started=pre_started,
                event_deadline=operation_deadline,
                post_timeout=G1_S1_STAGE_BUDGETS["post_finalize"],
            )
            evidence["event_boundary"] = collected["event_boundary"]
            evidence["post"] = _s1_public_snapshot(collected["post"])
            post_started = float(collected["event_boundary"].get("post_started", time.monotonic()))
            screenshot_path, screenshot_record = _capture_screenshot(
                display, run_id, proc.pid, "s1_ps3_scene",
                _s1_stage_timeout(command_started, post_started, G1_S1_STAGE_BUDGETS["post_finalize"]),
                crop=content_crop,
            )
            evidence["screenshot"] = {"phase": "ps3", "capture": screenshot_record,
                                      "outside_repo": str(screenshot_path)}
            ps3_end = time.monotonic()
            boundary_wait_start = trigger_finished if trigger_finished is not None else post_started
            wait_elapsed = ps3_end - boundary_wait_start
            boundary_wait_elapsed = post_started - boundary_wait_start
            if boundary_wait_elapsed > G1_S1_STAGE_BUDGETS["ps3_wait"]:
                raise RuntimeSafetyError(
                    f"S1 PS3 wait stage exceeded its {G1_S1_STAGE_BUDGETS['ps3_wait']} second cap"
                )
            evidence["stages"]["ps3_wait"] = {
                "status": "PASS", "wait": collected["event_boundary"].get("wait_ps", []),
                "start_elapsed": round(boundary_wait_start - command_started, 3),
                "end_elapsed": round(post_started - command_started, 3),
                "elapsed_seconds": round(boundary_wait_elapsed, 3),
                "post_snapshot_elapsed_seconds": round(wait_elapsed - boundary_wait_elapsed, 3),
            }
            result = s1.evaluate(
                fixture_path=candidate_fixture, fixture_name=fixture_spec.name,
                group_word=0, selected_index=fixture_spec.selected_index, post=collected,
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
            if g4_exact_postload:
                postload_wait_started = time.monotonic()
                postload_wait = _g4_wait_for_postload_rows(
                    prefix,
                    deadline=min(operation_deadline, postload_wait_started + G4_POSTLOAD_WAIT_BUDGET),
                )
                evidence["stages"]["g4_postload_wait"] = {
                    "status": "PASS" if postload_wait["min_rows_observed"] else "UNKNOWN",
                    "start_elapsed": round(postload_wait_started - command_started, 3),
                    "end_elapsed": round(time.monotonic() - command_started, 3),
                    "elapsed_seconds": round(time.monotonic() - postload_wait_started, 3),
                    **postload_wait,
                }
            if minimap_probe and result.get("status") == "PASS":
                probe_started = time.monotonic()
                camera_before = _read_camera(read_memory)
                # DxWrapper enlarges the pixels, but its mouse translation
                # expects unscaled game-coordinate injection (as in menu/load).
                presentation_scale = 2 if dxwrapper_2x else 1
                probe_root = [content_crop[0] + G1_S1_MINIMAP_PROBE_POINT[0],
                              content_crop[1] + G1_S1_MINIMAP_PROBE_POINT[1]]
                probe_argv = [sys.executable, str(REPO_ROOT / "tools/x11_mouse_click.py"),
                              "--display", display, *map(str, probe_root)]
                subprocess.run(probe_argv, env=env, stdout=log, stderr=log,
                               timeout=_s1_stage_timeout(command_started, probe_started, 5.0), check=True)
                probe = evidence["minimap_probe"]
                probe.update({"status": "UNKNOWN", "logical": list(G1_S1_MINIMAP_PROBE_POINT),
                              "input_scale": 1, "presentation_scale": presentation_scale,
                              "root": probe_root, "camera_before": camera_before,
                              "click_count": 1, "argv": probe_argv})
                camera_after = camera_before
                while time.monotonic() - probe_started < 5.0 and time.monotonic() < operation_deadline:
                    camera_after = _read_camera(read_memory)
                    if camera_after != camera_before:
                        break
                    time.sleep(0.1)
                probe.update({"camera_after": camera_after,
                              "elapsed_seconds": round(time.monotonic() - probe_started, 3),
                              "status": "PASS" if camera_after != camera_before else "FAIL_NO_EFFECT"})
                if probe["status"] != "PASS":
                    evidence["status"] = "UNKNOWN"
                    evidence["classification"] = "MINIMAP_PROBE_NO_CAMERA_RESPONSE"
            if deselect_probe and result.get("status") == "PASS":
                probe_started = time.monotonic()
                selected_before = _read_selection(read_memory)
                probe = evidence["deselect_probe"]
                probe.update({"status": "UNKNOWN", "logical": list(G1_S1_DESELECT_PROBE_POINT),
                              "input_scale": 1, "presentation_scale": 2 if dxwrapper_2x else 1,
                              "selection_before": selected_before})
                selected_before_count = selected_before.get("count")
                if not isinstance(selected_before_count, int):
                    raise ValueError("PS3 selection count is not an integer")
                if selected_before_count < 1:
                    probe["status"] = "SKIP_NO_INITIAL_SELECTION"
                else:
                    x, y = G1_S1_DESELECT_PROBE_POINT
                    root = [content_crop[0] + x, content_crop[1] + y]
                    argv = [sys.executable, str(REPO_ROOT / "tools/x11_mouse_click.py"),
                            "--display", display, *map(str, root)]
                    subprocess.run(argv, env=env, stdout=log, stderr=log,
                                   timeout=_s1_stage_timeout(command_started, probe_started, 5.0), check=True)
                    probe.update({"root": root, "argv": argv, "click_count": 1})
                    selected_after = selected_before
                    selected_after_count = selected_before_count
                    while time.monotonic() - probe_started < 5.0 and time.monotonic() < operation_deadline:
                        selected_after = _read_selection(read_memory)
                        count_value = selected_after.get("count")
                        if not isinstance(count_value, int):
                            raise ValueError("PS3 selection count changed to a noninteger")
                        selected_after_count = count_value
                        if selected_after_count == 0:
                            break
                        time.sleep(0.1)
                    probe.update({"selection_after": selected_after,
                                  "elapsed_seconds": round(time.monotonic() - probe_started, 3),
                                  "status": "PASS" if selected_after_count == 0 else "FAIL_NO_EFFECT"})
                if probe["status"] != "PASS":
                    evidence["status"] = "UNKNOWN"
                    evidence["classification"] = "DESELECT_PROBE_NO_EFFECT"
            if drag_probe and result.get("status") == "PASS":
                probe_started = time.monotonic()
                x, y, to_x, to_y = G1_S1_DRAG_PROBE_BOUNDS
                clear_root = [content_crop[0] + G1_S1_DESELECT_PROBE_POINT[0],
                              content_crop[1] + G1_S1_DESELECT_PROBE_POINT[1]]
                clear_argv = [sys.executable, str(REPO_ROOT / "tools/x11_mouse_click.py"),
                              "--display", display, *map(str, clear_root)]
                subprocess.run(clear_argv, env=env, stdout=log, stderr=log,
                               timeout=_s1_stage_timeout(command_started, probe_started, 5.0), check=True)
                selected_before = _read_selection(read_memory)
                before_count = selected_before.get("count")
                if not isinstance(before_count, int):
                    raise ValueError("drag preselection count is not an integer")
                probe = evidence["drag_probe"]
                probe.update({"status": "UNKNOWN", "clear_count": 1, "clear_root": clear_root,
                              "selection_before": selected_before,
                              "logical_bounds": list(G1_S1_DRAG_PROBE_BOUNDS),
                              "input_scale": 1, "presentation_scale": 2 if dxwrapper_2x else 1})
                if before_count != 0:
                    probe["status"] = "FAIL_CLEAR_NOT_OBSERVED"
                else:
                    root = [content_crop[0] + x, content_crop[1] + y]
                    to_root = [content_crop[0] + to_x, content_crop[1] + to_y]
                    argv = [sys.executable, str(REPO_ROOT / "tools/x11_mouse_click.py"),
                            "--display", display, *map(str, root), "--drag-to", *map(str, to_root)]
                    subprocess.run(argv, env=env, stdout=log, stderr=log,
                                   timeout=_s1_stage_timeout(command_started, probe_started, 5.0), check=True)
                    probe.update({"drag_count": 1, "root_bounds": [*root, *to_root], "argv": argv})
                    selected_after = selected_before
                    after_count = before_count
                    while time.monotonic() - probe_started < 5.0 and time.monotonic() < operation_deadline:
                        selected_after = _read_selection(read_memory)
                        count_value = selected_after.get("count")
                        if not isinstance(count_value, int):
                            raise ValueError("drag selection count became noninteger")
                        after_count = count_value
                        if after_count > 0:
                            break
                        time.sleep(0.1)
                    probe.update({"selection_after": selected_after,
                                  "elapsed_seconds": round(time.monotonic() - probe_started, 3),
                                  "status": "PASS" if after_count > 0 else "FAIL_NO_EFFECT"})
                if probe["status"] != "PASS":
                    evidence["status"] = "UNKNOWN"
                    evidence["classification"] = "DRAG_PROBE_NO_SELECTION_RESPONSE"
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
        if g4_exact_postload:
            try:
                exact_provenance = _g4_shadow_provenance(
                    prefix, env if "env" in locals() else {},
                    require_postload=True, expected_run_id=run_id,
                )
            except (OSError, RuntimeSafetyError, TypeError, ValueError) as exc:
                exact_provenance = {
                    "status": "FAIL", "pass": False,
                    "error": f"{type(exc).__name__}: {exc}",
                }
            evidence["g4_exact_postload"] = exact_provenance
            if exact_provenance.get("pass") is not True:
                evidence["status"] = "UNKNOWN"
                evidence["classification"] = "POSTLOAD_CONTRACT_FAILURE"
        if dxwrapper_install is not None:
            try:
                from patches.resolution import dxwrapper_config

                evidence["dxwrapper_config"]["uninstall"] = dxwrapper_config.uninstall_private(game)
                evidence["dxwrapper_config"]["restored"] = True
            except (OSError, ValueError) as exc:
                evidence["dxwrapper_config"]["restored"] = False
                evidence["dxwrapper_config"]["restore_error"] = f"{type(exc).__name__}: {exc}"
                cleanup["ok"] = False
                cleanup["error"] = evidence["dxwrapper_config"]["restore_error"]
            try:
                _preserve_dxwrapper_logs(game, output, evidence["dxwrapper_config"])
            except OSError as exc:
                evidence["dxwrapper_config"]["wrapper_logs_error"] = f"{type(exc).__name__}: {exc}"
        evidence["elapsed_seconds"] = round(time.monotonic() - command_started, 3)
        evidence["provenance"] = {
            "manifest_sha256": _sha256(manifest_path), "display": display,
            "prefix": str(prefix), "game_root": str(game),
            "environment": {key: (env.get(key) if "env" in locals() else None)
                             for key in ("DISPLAY", "WINEPREFIX", "WINEARCH", "LANG", "LC_ALL", "WINEDLLOVERRIDES",
                                         "INMM_AI_SHADOW", "INMM_G4_RUN_ID")},
            "harness_sha256": {
                "tools/runtime_env.py": _sha256(Path(__file__)),
                "tools/s1_load_evidence.py": _sha256(REPO_ROOT / "tools" / "s1_load_evidence.py"),
                "tools/x11_mouse_click.py": _sha256(REPO_ROOT / "tools" / "x11_mouse_click.py"),
            },
            "command": (
                "runtime_env.py g1-s1-candidate-load-evidence"
                if dxwrapper_2x else "runtime_env.py g1-s1-original-load-evidence"
            ),
            "g4_exact_postload": g4_exact_postload,
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


def _g4_ai_metric_summary(samples: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    disappearances = 0
    hp_decreases = 0
    gaps: list[int] = []
    previous: dict[int, Mapping[str, Any]] = {}
    controller_series: list[tuple[int, int]] = []
    for sample in samples:
        raw_units = sample.get("units", [])
        units = [unit for unit in raw_units if isinstance(unit, Mapping)] if isinstance(raw_units, list) else []
        current = {int(unit["slot"]): unit for unit in units if isinstance(unit.get("slot"), int)}
        disappearances += len(previous.keys() - current.keys())
        for slot, unit in current.items():
            before = previous.get(slot)
            if before is None:
                continue
            identity = (unit.get("internal_id"), unit.get("type"), unit.get("owner"))
            before_identity = (before.get("internal_id"), before.get("type"), before.get("owner"))
            hp = unit.get("hp")
            before_hp = before.get("hp")
            if identity == before_identity and isinstance(hp, int) and isinstance(before_hp, int) and hp < before_hp:
                hp_decreases += 1
        owner0 = [(unit.get("x"), unit.get("y")) for unit in units if unit.get("owner") == 0]
        owner1 = [(unit.get("x"), unit.get("y")) for unit in units if unit.get("owner") == 1]
        valid0 = [(x, y) for x, y in owner0 if isinstance(x, int) and isinstance(y, int)]
        valid1 = [(x, y) for x, y in owner1 if isinstance(x, int) and isinstance(y, int)]
        if valid0 and valid1:
            gaps.append(min(max(abs(ax - bx), abs(ay - by)) for ax, ay in valid0 for bx, by in valid1))
        players = sample.get("players", [])
        if isinstance(players, list):
            controller_owner = next(
                (player for player in players if isinstance(player, Mapping) and player.get("owner") == 1),
                None,
            )
            if controller_owner is not None:
                opcode = controller_owner.get("controller_opcode")
                argument = controller_owner.get("controller_argument")
                if isinstance(opcode, int) and isinstance(argument, int):
                    controller_series.append((opcode, argument))
        previous = current
    counts = [len(sample.get("units", [])) for sample in samples if isinstance(sample.get("units"), list)]
    ticks = [sample.get("tick") for sample in samples if isinstance(sample.get("tick"), int)]
    return {
        "sample_count": len(samples),
        "first_tick": ticks[0] if ticks else None,
        "last_tick": ticks[-1] if ticks else None,
        "first_unit_count": counts[0] if counts else None,
        "last_unit_count": counts[-1] if counts else None,
        "slot_disappearances": disappearances,
        "hp_decrease_same_unit": hp_decreases,
        "min_faction_gap": min(gaps) if gaps else None,
        "controller_nonzero_samples": sum(opcode != 0 for opcode, _ in controller_series),
        "controller_transition_count": sum(
            before != after for before, after in zip(controller_series, controller_series[1:])
        ),
        "controller_opcodes_observed": sorted({opcode for opcode, _ in controller_series if opcode}),
    }


G4_FIXED_CHAIN_GOALS = frozenset({
    "_custom_game_chain_inject_seed1",
    "_custom_game_chain_inject_seed7",
    "_custom_game_chain_inject_seed42",
    "_custom_game_chain_inject_ming_japan_seed1",
    "_custom_game_chain_inject_ming_joseon_seed1",
})
G4_CANDIDATE_EXES = {
    "g4_controller_cadence_50.exe": "FUN_0043F5D0 case-2 build-intent cooldown 100->50",
    "g4_gather_cooldown_100.exe": "FUN_0043F5D0 case-3 gather-intent cooldown 200->100",
    "g4_production_crowd_cap_14.exe": "FUN_00406B00 G-7 H-CROWD density cap 7->14",
}
G4_INTERVENTION_GOALS = frozenset({
    "_g4_issue_idle_attack_probe",
    "_g4_idle_waypoint_reinforcement_probe",
})
G2_CREATION_GOAL = "_custom_game_chain_inject_g2_eight_seed42"
G2_CREATION_CANDIDATE = "g2_supply_5000.exe"
G2_APPROVED_BRIDGE_SHA256 = "8de5b96b992db90f0c6e1c8c33d33caada9e52435a4e605b3a2d747764555f65"
# This is the separately reviewed native fail-stop relocation build.  The
# ordinary 8de5 bridge remains a distinct gate and is never accepted here.
G2_RELOCATION_DIAG_BRIDGE_SHA256: str | None = (
    "8a2da2eafc4e9fb47960f7ecfebf697b3ef8ed23472e0c6745969e80737d3688"
)
# The family-accessor build is deliberately a separate review/pin boundary.
# It must not silently reuse the approved 47-fixup relocation DLL.
G2_FAMILY_ACCESSOR_MODE = "g2_six_arena_family_accessor_v1"
G2_FAMILY_ACCESSOR_BRIDGE_SHA256: str | None = (
    "71244523c24dcfe5986929a1ccb580e377f895e5de1355ccdd91614b3cfd541f"
)
G2_ARTIFACT_ROOT = Path("/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch")
G2_LIFECYCLE_MODES = ("save", "load")
# This lane is deliberately separate from the ordinary 10--20 second G2
# sampling budget.  It is an opt-in observer only; no caller is allowed to
# infer activation or product completion from its duration milestone.
G2_STOCK_OBSERVATION_TICKS = 24_000
G2_STOCK_OBSERVATION_WALL_SECONDS = 45 * 60
G2_STOCK_OBSERVATION_SAMPLE_SECONDS = 5.0
G2_STOCK_OBSERVATION_MIN_SNAPSHOT_SECONDS = 2.0
G2_STOCK_24K_SAVE_SHA256 = "b9fcbeb771b8c584fcec2598b4f58046e0f6ef04ca206823dacf5ae09b18c510"
G2_STOCK_24K_WITNESS_SHA256 = "b57f168dbb968fcc488baa6c41088d782922d051a3cd823b44e90b60c4a0a06e"
G2_RELOCATION_DIAG_MODE = "g2_six_arena_failstop_v1"
G2_RELOCATION_DIAG_MAGIC = 0x524C4631
G2_RELOCATION_DIAG_RAW_SIZE = 4096
G2_RELOCATION_DIAG_VERSION = 1
G2_RELOCATION_DIAG_MANIFEST = struct.Struct("<49I")
G2_RELOCATION_DIAG_FAULT = struct.Struct("<20I")
G2_FAMILY_PROGRESS_OFFSET = 3328
G2_FAMILY_PROGRESS_MAGIC = 0x524C5032
G2_FAMILY_PROGRESS = struct.Struct("<152I")
G2_FAMILY_IDENTITY_COUNT = 16
G2_FAMILY_PROGRESS_COMPLETE = 2
G2_FAMILY_PROGRESS_EXPECTED_TICKS = 256
G2_FAMILY_PROGRESS_DEADLINE_MS = 20_000


def _g2_relocation_diag_build_manifest(
    path: Path, *, game: Path,
) -> dict[str, Any]:
    """Validate the external, separately built relocation diagnostic.

    The normal G2 bridge and the relocation bridge are deliberately different
    gates.  ``path`` is an external manifest produced by the native writer;
    no DLL is copied or deployed by this function.
    """
    if G2_RELOCATION_DIAG_BRIDGE_SHA256 is None and G2_FAMILY_ACCESSOR_BRIDGE_SHA256 is None:
        raise RuntimeSafetyError("G2 relocation diagnostic bridge hash is not separately reviewed")
    if not path.is_absolute() or path.is_symlink():
        raise RuntimeSafetyError("G2 relocation diagnostic build manifest must be an absolute regular file")
    build_path = _real(path)
    if not _under(build_path, _real(G2_ARTIFACT_ROOT)):
        raise RuntimeSafetyError("G2 relocation diagnostic build manifest must remain under the approved temp root")
    if not build_path.is_file():
        raise RuntimeSafetyError("G2 relocation diagnostic build manifest is missing")
    try:
        manifest = json.loads(build_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise RuntimeSafetyError("invalid G2 relocation diagnostic build manifest") from exc
    mode = manifest.get("diagnostic_mode") if isinstance(manifest, dict) else None
    if (not isinstance(manifest, dict)
            or mode not in (G2_RELOCATION_DIAG_MODE, G2_FAMILY_ACCESSOR_MODE)
            or manifest.get("diagnostic_only") is not True):
        raise RuntimeSafetyError("G2 relocation diagnostic build manifest mode is not exact")
    reviewed_sha = (G2_RELOCATION_DIAG_BRIDGE_SHA256
                    if mode == G2_RELOCATION_DIAG_MODE
                    else G2_FAMILY_ACCESSOR_BRIDGE_SHA256)
    if reviewed_sha is None:
        raise RuntimeSafetyError("G2 relocation diagnostic bridge hash is not separately reviewed")
    source = manifest.get("source")
    if source is not None:
        if not isinstance(source, dict) or source.get("mode") != "original":
            raise RuntimeSafetyError("relocation diagnostic source mode must be original")
        if source.get("original_exe_sha256") != ORIGINAL_SHA256:
            raise RuntimeSafetyError("relocation diagnostic original source SHA-256 mismatch")
    elif manifest.get("original_source_sha256") not in (None, ORIGINAL_SHA256):
        raise RuntimeSafetyError("relocation diagnostic original source SHA-256 mismatch")
    stub_inputs = manifest.get("original_stub_inputs")
    if not isinstance(stub_inputs, dict) or not stub_inputs or any(
        not isinstance(value, str) or len(value) != 64 for value in stub_inputs.values()
    ):
        raise RuntimeSafetyError("relocation diagnostic original/diagnostic source hashes are missing")
    diag_source_sha = manifest.get("diagnostic_source_sha256")
    if diag_source_sha is not None and (not isinstance(diag_source_sha, str) or len(diag_source_sha) != 64):
        raise RuntimeSafetyError("relocation diagnostic source SHA-256 is malformed")
    expected_patch_count = 47 if mode == G2_RELOCATION_DIAG_MODE else 120
    if manifest.get("capacity") != 1201:
        raise RuntimeSafetyError("relocation diagnostic capacity contract mismatch")
    if manifest.get("patch_count") != expected_patch_count:
        raise RuntimeSafetyError("relocation diagnostic fixup count does not match the selected mode")
    if mode == G2_FAMILY_ACCESSOR_MODE:
        progress_schema = manifest.get("progress_schema")
        if (not isinstance(progress_schema, dict)
                or progress_schema.get("offset") != G2_FAMILY_PROGRESS_OFFSET
                or progress_schema.get("fixed_size") != G2_FAMILY_PROGRESS.size
                or progress_schema.get("expected_ticks") != G2_FAMILY_PROGRESS_EXPECTED_TICKS
                or progress_schema.get("deadline_ms") != G2_FAMILY_PROGRESS_DEADLINE_MS
                or progress_schema.get("identity_records") != G2_FAMILY_IDENTITY_COUNT
                or progress_schema.get("completion_status") != G2_FAMILY_PROGRESS_COMPLETE):
            raise RuntimeSafetyError("family accessor progress schema is not exact")
    dll_sha = manifest.get("dll_sha256")
    if dll_sha != reviewed_sha:
        raise RuntimeSafetyError("relocation diagnostic DLL SHA-256 is not separately reviewed")
    dll_path_value = manifest.get("dll_path", manifest.get("dll"))
    if not isinstance(dll_path_value, str) or not Path(dll_path_value).is_absolute():
        raise RuntimeSafetyError("relocation diagnostic DLL path must be absolute")
    dll_path = _real(Path(dll_path_value))
    if dll_path.is_symlink() or not dll_path.is_file() or _sha256(dll_path) != dll_sha:
        raise RuntimeSafetyError("relocation diagnostic DLL path/hash validation failed")
    actual_dll_sha = _sha256(dll_path)
    return {
        "manifest_path": str(build_path),
        "manifest_sha256": _sha256(build_path),
        "mode": mode,
        "source_original_sha256": (
            source.get("original_exe_sha256") if isinstance(source, dict)
            else manifest.get("original_source_sha256", ORIGINAL_SHA256)
        ),
        "diagnostic_source_sha256": diag_source_sha,
        "dll_path": str(dll_path),
        "dll_sha256": dll_sha,
        "actual_dll_sha256": actual_dll_sha,
        "capacity": manifest["capacity"],
        "patch_count": manifest["patch_count"],
        "game_root": str(_real(game)),
    }


def _g2_relocation_diag_raw(path: Path) -> dict[str, Any]:
    """Read and validate the native fixed-POD fail-stop raw artifact."""
    if not path.is_file() or path.is_symlink():
        return {"status": "BLOCKED", "reason": "relocation raw artifact missing"}
    try:
        raw = path.read_bytes()
    except OSError as exc:
        return {"status": "BLOCKED", "reason": f"relocation raw artifact unreadable: {exc}"}
    if len(raw) != G2_RELOCATION_DIAG_RAW_SIZE:
        return {"status": "BLOCKED", "reason": "relocation raw artifact size invalid", "size": len(raw)}
    manifest = G2_RELOCATION_DIAG_MANIFEST.unpack_from(raw)
    magic, version, marker_offset, capacity, patch_count, arena_count, request_id, original_caller = manifest[:8]
    old_bytes_checked, patch_bytes_written, tick_before, tick_after = (
        manifest[20], manifest[21], manifest[22], manifest[23]
    )
    if magic != G2_RELOCATION_DIAG_MAGIC or version != G2_RELOCATION_DIAG_VERSION:
        return {"status": "BLOCKED", "reason": "relocation raw artifact magic/version invalid", "size": len(raw)}
    request_words = list(manifest[27:35])
    guard_begin, guard_end = manifest[39], manifest[40]
    copy_compare_ok, tail_zero_ok, stage = manifest[41], manifest[42], manifest[43]
    patch_manifest_offset, patch_manifest_count = manifest[44], manifest[45]
    if marker_offset != 512 or capacity != 1201 or patch_count != 47 or arena_count != 6:
        return {"status": "BLOCKED", "reason": "relocation raw artifact is partial or not fully applied", "size": len(raw)}
    if request_words != [request_id, 6, 0, 0, 0, 0, 0, 0]:
        return {"status": "BLOCKED", "reason": "relocation raw request words are not the exact one-shot op6 request", "size": len(raw)}
    if (manifest[35] != 3 or manifest[36] != 1 or manifest[37] == 0
            or manifest[37] != manifest[38]
            or any(value > 1200 for value in manifest[46:49])
            or guard_begin != 0x0066C000 or guard_begin >= guard_end
            or guard_end != 0x00892000 or copy_compare_ok != 1 or tail_zero_ok != 1
            or stage != 5 or manifest[24] != 0 or manifest[26] != 0x47424631
            or patch_manifest_offset != 640 or patch_manifest_count != 47):
        return {"status": "BLOCKED", "reason": "relocation raw native stage/guard/copy evidence is incomplete", "size": len(raw)}
    patch_records: list[dict[str, int]] = []
    patch_record = struct.Struct("<5I")
    try:
        for index in range(patch_manifest_count):
            instruction, old_operand, new_operand, length, operand_offset = patch_record.unpack_from(
                raw, patch_manifest_offset + index * patch_record.size
            )
            if (instruction == 0 or not 1 <= length <= 16
                    or operand_offset + 4 > length):
                return {"status": "BLOCKED", "reason": "relocation raw patch manifest record is invalid", "size": len(raw)}
            patch_records.append({
                "instruction": instruction, "old_operand": old_operand,
                "new_operand": new_operand, "length": length,
                "operand_offset": operand_offset,
            })
    except struct.error:
        return {"status": "BLOCKED", "reason": "relocation raw patch manifest is truncated", "size": len(raw)}
    fault = G2_RELOCATION_DIAG_FAULT.unpack_from(raw, marker_offset)
    if fault[0] != G2_RELOCATION_DIAG_MAGIC or fault[1] != G2_RELOCATION_DIAG_VERSION:
        return {"status": "BLOCKED", "reason": "relocation raw artifact fault marker was not published last", "size": len(raw)}
    if (original_caller != 0x0042334C or old_bytes_checked != 47 or patch_bytes_written != 47
            or fault[2] != 0xC0000005 or fault[4] < 2
            or fault[5] not in (0, 1, 8) or fault[9] != fault[5]
            or fault[7] == 0 or fault[8] == 0 or fault[18] == 0 or fault[18] != fault[7]):
        return {"status": "BLOCKED", "reason": "relocation raw artifact caller/fixup evidence invalid", "size": len(raw)}
    return {
        "status": "PASS",
        "classification": "OBSERVED_RELOCATION_DIAGNOSTIC_FAULT",
        "path": str(path),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "size": len(raw),
        "magic": f"0x{magic:08x}",
        "version": version,
        "marker_offset": marker_offset,
        "armed": True,
        "applied_fixups": patch_bytes_written,
        "copied_arenas": arena_count,
        "known_fixups": patch_count,
        "request_id": request_id,
        "request_words": request_words,
        "native_status": manifest[24],
        "source_sha256_protected": manifest[25],
        "raw_fault_path_marker": manifest[26],
        "tick_before": tick_before,
        "tick_after": tick_after,
        "initial_ps3": manifest[35],
        "initial_profile": manifest[36],
        "caller_thread": manifest[37],
        "window_thread": manifest[38],
        "guard_begin": guard_begin,
        "guard_end": guard_end,
        "copy_compare_ok": copy_compare_ok,
        "tail_zero_ok": tail_zero_ok,
        "stage": stage,
        "patch_manifest_offset": patch_manifest_offset,
        "patch_manifest_count": patch_manifest_count,
        "counter_active_initial": manifest[46],
        "counter_cata_initial": manifest[47],
        "counter_catb_initial": manifest[48],
        "patch_records": patch_records,
        "native_thread_id": fault[8],
        "exception_code": fault[2],
        "exception_flags": fault[3],
        "parameter_count": fault[4],
        "access_type": fault[5],
        "fault_address": fault[6],
        "exception_pc": fault[7],
        "registers": {"eax": fault[10], "ebx": fault[11], "ecx": fault[12],
                       "edx": fault[13], "esi": fault[14], "edi": fault[15],
                       "ebp": fault[16], "esp": fault[17], "eip": fault[18],
                       "eflags": fault[19]},
    }


def _g2_relocation_diag_native_op(prefix: Path, *, timeout: float = 10.0) -> dict[str, Any]:
    """Issue exactly one op6 request and collect the fail-stop raw artifact."""
    if timeout <= 0 or timeout > 10:
        raise RuntimeSafetyError("relocation diagnostic native op timeout must be between 0 and 10 seconds")
    request_id = int(time.monotonic_ns() % 2_000_000_000) + 100_000
    drive_c = prefix / "drive_c"
    request_path = drive_c / "supply_probe_request.txt"
    result_path = drive_c / "supply_probe_result.json"
    raw_path = drive_c / "g2_relocation_fault.bin"
    drive_c.mkdir(parents=True, exist_ok=True)
    temporary = request_path.with_name("supply_probe_request.tmp")
    temporary.write_text(f"{request_id} 6 0 0 0 0 0 0\n", encoding="ascii")
    temporary.replace(request_path)
    deadline = time.monotonic() + timeout
    response: dict[str, Any] | None = None
    raw_evidence: dict[str, Any] = {"status": "BLOCKED", "reason": "relocation raw artifact not published"}
    while time.monotonic() < deadline:
        try:
            candidate = json.loads(result_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            candidate = None
        if isinstance(candidate, dict) and candidate.get("id") == request_id:
            response = candidate
        if raw_path.is_file():
            # The native writer pre-creates and zeroes the 4096-byte mapping
            # before arming.  Do not treat existence as publication: reread
            # until the first-AV marker and complete POD are visible.
            raw_evidence = _g2_relocation_diag_raw(raw_path)
            if raw_evidence.get("status") == "PASS":
                break
        time.sleep(0.05)
    if raw_evidence.get("status") == "PASS" and raw_evidence.get("request_id") != request_id:
        raw_evidence = {
            "status": "BLOCKED",
            "reason": "relocation raw request id does not match the one-shot request",
            "observed_request_id": raw_evidence.get("request_id"),
            "expected_request_id": request_id,
        }
    complete = raw_evidence.get("status") == "PASS"
    return {
        "status": (
            "OBSERVED_RELOCATION_DIAGNOSTIC_FAULT"
            if complete else "BLOCKED_RELOCATION_DIAGNOSTIC_BOUNDARY"
        ),
        "armed": complete,
        "applied": complete and raw_evidence.get("applied_fixups") == 47,
        "request": {"id": request_id, "op": 6, "owner": 0, "slot": 0,
                    "fields": [request_id, 6, 0, 0, 0, 0, 0, 0]},
        "response": response,
        "raw": raw_evidence,
        "timed_out": response is None and raw_evidence.get("status") != "PASS",
    }


def _g2_family_accessor_raw(path: Path) -> dict[str, Any]:
    """Validate the family build's fixed 4096-byte progress witness."""
    if not path.is_file() or path.is_symlink():
        return {"status": "BLOCKED", "reason": "family progress artifact missing"}
    try:
        raw = path.read_bytes()
    except OSError as exc:
        return {"status": "BLOCKED", "reason": f"family progress artifact unreadable: {exc}"}
    if len(raw) != G2_RELOCATION_DIAG_RAW_SIZE:
        return {"status": "BLOCKED", "reason": "family progress artifact size invalid", "size": len(raw)}
    manifest = G2_RELOCATION_DIAG_MANIFEST.unpack_from(raw)
    fault = G2_RELOCATION_DIAG_FAULT.unpack_from(raw, 512)
    fault_valid = (fault[0] == G2_RELOCATION_DIAG_MAGIC and fault[1] == G2_RELOCATION_DIAG_VERSION
                   and fault[2] == 0xC0000005 and fault[4] >= 2 and fault[5] in (0, 1, 8)
                   and fault[9] == fault[5] and fault[7] != 0 and fault[8] != 0
                   and fault[18] == fault[7])
    context = {"present": fault_valid, "exception_code": fault[2],
               "parameter_count": fault[4], "access_type": fault[5],
               "fault_address": fault[6], "exception_pc": fault[7],
               "exception_thread": fault[8], "eip": fault[18]}
    def blocked(reason: str) -> dict[str, Any]:
        return {"status": "BLOCKED", "reason": reason, "request_id": manifest[6],
                "request_words": list(manifest[27:35]), "fault": context}
    if (manifest[0] != G2_RELOCATION_DIAG_MAGIC or manifest[1] != G2_RELOCATION_DIAG_VERSION
            or manifest[2] != 512 or manifest[3] != 1201 or manifest[4] != 120
            or manifest[5] != 6 or manifest[6] == 0 or manifest[7] != 0x0042334C
            or manifest[20] != 120 or manifest[21] != 120
            or list(manifest[27:35]) != [manifest[6], 6, 0, 0, 0, 0, 0, 0]
            or manifest[35] != 3 or manifest[36] != 1
            or manifest[37] == 0 or manifest[37] != manifest[38]
            or manifest[39] != 0x0066C000 or manifest[40] != 0x00892000
            or manifest[41] != 1 or manifest[42] != 1 or manifest[43] != 5
            or manifest[44] != 640 or manifest[45] != 120 or manifest[24] != 0
            or manifest[26] != 0x47424631):
        return blocked("family base manifest is incomplete")
    records: list[dict[str, int]] = []
    patch_record = struct.Struct("<5I")
    for index in range(120):
        instruction, old_operand, new_operand, length, operand_offset = patch_record.unpack_from(
            raw, 640 + index * patch_record.size
        )
        if instruction == 0 or not 1 <= length <= 16 or operand_offset + 4 > length:
            return blocked("family patch record is invalid")
        records.append({"instruction": instruction, "old_operand": old_operand,
                        "new_operand": new_operand, "length": length,
                        "operand_offset": operand_offset})
    values = G2_FAMILY_PROGRESS.unpack_from(raw, G2_FAMILY_PROGRESS_OFFSET)
    if (values[0] != G2_FAMILY_PROGRESS_MAGIC or values[1] != 1
            or values[2] != G2_FAMILY_PROGRESS_COMPLETE
            or values[8] < G2_FAMILY_PROGRESS_EXPECTED_TICKS
            or values[9] != G2_FAMILY_PROGRESS_EXPECTED_TICKS
            or values[10] != G2_FAMILY_PROGRESS_DEADLINE_MS
            or values[5] - values[4] < G2_FAMILY_PROGRESS_EXPECTED_TICKS
            or values[11] == 0 or values[11] != values[12]
            or values[13] != 1201 or values[14] != 6
            or list(values[15:18]) != [47, 73, 120]
            or list(values[18:20]) != [16, 16] or values[20] != 16
            or any(value > 1201 for value in values[21:24])):
        return blocked("family progress completion contract is incomplete")
    identities: list[dict[str, int]] = []
    owners: dict[int, set[int]] = {owner: set() for owner in range(8)}
    slots: set[int] = set()
    full_ids: set[int] = set()
    for index in range(G2_FAMILY_IDENTITY_COUNT):
        row = values[24 + index * 8:32 + index * 8]
        slot, full_id, owner, unit_type, hp, active, category_a, category_b = row
        if (not 1 <= slot < 1200 or slot in slots or full_id in full_ids
                or (full_id & 0xFFFF) != slot or not 0 <= owner < 8
                or unit_type not in (49, 7) or not 0 < hp < 0x80000000 or active != 1
                or category_a not in (0, 1) or category_b not in (0, 1)):
            return blocked("family identity record is invalid")
        slots.add(slot)
        full_ids.add(full_id)
        owners[owner].add(unit_type)
        identities.append({"slot": slot, "full_id": full_id, "owner": owner,
                           "type": unit_type, "hp": hp, "active": active,
                           "category_a": category_a, "category_b": category_b})
    if any(types != {49, 7} for types in owners.values()):
        return blocked("family identities do not contain HQ49 and worker7 for every owner")
    result: dict[str, Any] = {
        "status": "PASS", "classification": "BOUNDED256TICK_NEW_ARENA_WITNESS",
        "path": str(path), "sha256": hashlib.sha256(raw).hexdigest(), "size": len(raw),
        "request_id": manifest[6],
        "request_words": list(manifest[27:35]),
        "manifest_patch_count": manifest[4], "patch_records": records,
        "progress": {"status": values[2], "start_tick": values[4], "end_tick": values[5],
                      "observed_tick": values[6], "sample_count": values[7],
                      "unique_tick_count": values[8], "expected_ticks": values[9],
                      "deadline_ms": values[10], "caller_thread": values[11],
                      "window_thread": values[12], "capacity": values[13],
                      "arena_count": values[14], "patch_count": values[15],
                      "family_patch_count": values[16], "patch_union_count": values[17],
                      "identities": identities, "counter_active": values[21],
                      "counter_cata": values[22], "counter_catb": values[23]},
        "fault": context,
    }
    if fault_valid:
        # Family qualification is progress-only.  Preserve a first-AV record
        # for diagnosis, but never promote it to a family witness.
        result["status"] = "BLOCKED"
        result["reason"] = "first AV occurred before the complete family progress witness"
    return result


def _g2_family_initial_identities(snapshot: Mapping[str, Any]) -> list[dict[str, int]]:
    """Freeze the exact 16 natural units before the one-shot native op."""
    units = snapshot.get("units")
    if not isinstance(units, list) or len(units) != G2_FAMILY_IDENTITY_COUNT:
        raise RuntimeSafetyError("family accessor requires exactly 16 initial units")
    result: list[dict[str, int]] = []
    seen_slots: set[int] = set()
    seen_ids: set[int] = set()
    for unit in units:
        if not isinstance(unit, Mapping):
            raise RuntimeSafetyError("family initial identity is malformed")
        slot, full_id, owner, unit_type = (unit.get("slot"), unit.get("internal_id"),
                                           unit.get("owner"), unit.get("type"))
        if (not isinstance(slot, int) or not 1 <= slot < 1200 or slot in seen_slots
                or not isinstance(full_id, int) or full_id <= 0 or full_id in seen_ids
                or (full_id & 0xFFFF) != slot or not isinstance(owner, int) or not 0 <= owner < 8
                or not isinstance(unit_type, int) or unit_type not in (49, 7)):
            raise RuntimeSafetyError("family initial identity slot/full-ID/owner/type gate failed")
        seen_slots.add(slot)
        seen_ids.add(full_id)
        result.append({"slot": slot, "full_id": full_id, "owner": owner, "type": unit_type})
    return sorted(result, key=lambda item: (item["slot"], item["full_id"]))


def _g2_family_accessor_native_op(
    prefix: Path, *, timeout: float = 20.0,
    expected_identities: list[dict[str, int]] | None = None,
) -> dict[str, Any]:
    """Issue one op6 and await the complete 256-tick family witness."""
    if timeout <= 0 or timeout > 20:
        raise RuntimeSafetyError("family accessor timeout must be between 1 and 20 seconds")
    request_id = int(time.monotonic_ns() % 2_000_000_000) + 100_000
    drive_c = prefix / "drive_c"
    request_path = drive_c / "supply_probe_request.txt"
    result_path = drive_c / "supply_probe_result.json"
    raw_path = drive_c / "g2_relocation_fault.bin"
    drive_c.mkdir(parents=True, exist_ok=True)
    temporary = request_path.with_name("supply_probe_request.tmp")
    temporary.write_text(f"{request_id} 6 0 0 0 0 0 0\n", encoding="ascii")
    temporary.replace(request_path)
    deadline = time.monotonic() + timeout
    response: dict[str, Any] | None = None
    raw_evidence: dict[str, Any] = {"status": "BLOCKED", "reason": "family progress not published"}
    while time.monotonic() < deadline:
        try:
            candidate = json.loads(result_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            candidate = None
        if isinstance(candidate, dict) and candidate.get("id") == request_id:
            response = candidate
        if raw_path.is_file():
            raw_evidence = _g2_family_accessor_raw(raw_path)
            if raw_evidence.get("status") == "PASS":
                break
            if isinstance(raw_evidence.get("fault"), dict) and raw_evidence["fault"].get("present"):
                break
        time.sleep(0.05)
    complete = raw_evidence.get("status") == "PASS"
    if complete and isinstance(response, dict) and response.get("op") != 6:
        raw_evidence = {"status": "BLOCKED", "reason": "family native response operation is not op6",
                        "request_id": raw_evidence.get("request_id"), "fault": raw_evidence.get("fault")}
        complete = False
    if complete and raw_evidence.get("request_id") != request_id:
        raw_evidence = {"status": "BLOCKED",
                        "reason": "family raw request id does not match the one-shot request",
                        "observed_request_id": raw_evidence.get("request_id"),
                        "expected_request_id": request_id,
                        "fault": raw_evidence.get("fault")}
        complete = False
    identity_match: bool | None = None
    if complete and expected_identities is not None:
        observed = raw_evidence.get("progress", {}).get("identities", [])
        observed_ids = sorted(
            [{key: int(item[key]) for key in ("slot", "full_id", "owner", "type")} for item in observed],
            key=lambda item: (item["slot"], item["full_id"]),
        ) if isinstance(observed, list) and all(isinstance(item, Mapping) for item in observed) else []
        identity_match = observed_ids == expected_identities
        if not identity_match:
            raw_evidence = {**raw_evidence, "status": "BLOCKED",
                            "reason": "family completion identities differ from the pre-op scene snapshot",
                            "expected_identities": expected_identities,
                            "observed_identities": observed_ids}
            complete = False
    return {"status": raw_evidence.get("classification") if complete
            else "BLOCKED_RELOCATION_DIAGNOSTIC_BOUNDARY", "armed": complete,
            "request": {"id": request_id, "op": 6, "owner": 0, "slot": 0,
                        "fields": [request_id, 6, 0, 0, 0, 0, 0, 0]},
            "response": response, "raw": raw_evidence,
            "expected_identities": expected_identities, "identity_match": identity_match,
            "timed_out": (not complete and not (
                isinstance(raw_evidence.get("fault"), dict)
                and raw_evidence["fault"].get("present")
            ))}


def _g2_lifecycle_native_op(
    prefix: Path, *, op: int, owner: int, slot: int, timeout: float = 30.0,
) -> dict[str, Any]:
    """Issue exactly one existing bridge op2/op3 and retain its raw response."""
    if op not in (2, 3) or not (0 <= owner < 8) or not (0 <= slot < 100):
        raise RuntimeSafetyError("lifecycle native op requires op2/op3, owner0..7, slot0..99")
    started = time.monotonic()
    request_path = prefix / "drive_c" / "supply_probe_request.txt"
    result_path = prefix / "drive_c" / "supply_probe_result.json"
    request_id = int(time.monotonic_ns() % 2_000_000_000) + 100_000
    request_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = request_path.with_name("supply_probe_request.tmp")
    temporary.write_text(f"{request_id} {op} {owner} {slot} 0 0 0 0\n", encoding="ascii")
    temporary.replace(request_path)
    deadline = started + min(30.0, timeout)
    while time.monotonic() < deadline:
        try:
            result = json.loads(result_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            time.sleep(0.05)
            continue
        if isinstance(result, dict) and result.get("id") == request_id:
            return result
        time.sleep(0.05)
    raise RuntimeSafetyError(f"lifecycle native op{op} timed out")


def _g2_lifecycle_stock_preflight(
    snapshot: Mapping[str, Any], read_memory: Callable[[int, int], bytes],
    pending: Mapping[str, Any],
) -> str | None:
    """Check the strict live stock/pending gate before native op2."""
    players = snapshot.get("players")
    units = snapshot.get("units")
    if not isinstance(players, list) or not isinstance(units, list) or len(units) != 1160:
        return "strict stock roster must contain global1160 live units"
    costs: dict[int, int] = {}
    try:
        for unit_type in range(53):
            raw = read_memory(0x9B5228 + unit_type * 0x394 + 0x10, 2)
            if len(raw) != 2:
                return "native cost read through type52 was incomplete"
            costs[unit_type] = struct.unpack("<h", raw)[0]
    except (OSError, ValueError, struct.error):
        return "native cost read through type52 failed"
    ids: set[int] = set()
    slots: set[int] = set()
    for unit in units:
        if not isinstance(unit, Mapping):
            return "stock roster contains malformed unit"
        unit_id, slot, owner, unit_kind, hp = (
            unit.get("internal_id"), unit.get("slot"), unit.get("owner"),
            unit.get("type"), unit.get("hp"),
        )
        if (not isinstance(unit_id, int) or unit_id <= 0 or unit_id in ids
                or not isinstance(slot, int) or not (1 <= slot < 1200) or slot in slots
                or not isinstance(owner, int) or not (0 <= owner < 8)
                or not isinstance(unit_kind, int) or unit_kind not in costs
                or not isinstance(hp, (int, float)) or hp <= 0):
            return "stock full-ID/slot-owner-type/HP gate failed"
        ids.add(unit_id)
        slots.add(slot)
    for owner in range(8):
        player = next((item for item in players
                       if isinstance(item, Mapping) and item.get("owner") == owner), None)
        owned = [unit for unit in units if unit.get("owner") == owner]
        if (player is None or player.get("cap") != 5000 or player.get("used") != 5000
                or player.get("count") != 145 or player.get("reserved") not in (0, 10)
                or len(owned) != 145
                or sum(costs[int(unit["type"])] for unit in owned) != 5000):
            return f"owner {owner} strict used5000/count145/cost gate failed"
    pending_id = pending.get("internal_id")
    pending_unit = next((unit for unit in units if unit.get("internal_id") == pending_id), None)
    if (pending.get("owner") != 4 or pending.get("type") != 49
            or pending.get("command") != 15 or pending.get("production_type") != 7
            or pending.get("progress") != 100 or pending.get("reserved") != 10
            or pending_unit is None or pending_unit.get("owner") != 4
            or pending_unit.get("type") != 49):
        return "owner4 same-HQ pending progress100/res10 gate failed"
    return None


def _g4_send_control_goal(prefix: Path, goal: str, timeout_seconds: float) -> dict[str, Any]:
    request_id = f"g4-seeded-{time.time_ns()}"
    request = {
        "version": "1",
        "request_id": request_id,
        "goal": goal,
        "timeout_ms": int(timeout_seconds * 1000),
    }
    _write_json(prefix / "drive_c" / "inmm_control_request.json", request)
    deadline = time.monotonic() + timeout_seconds + 5
    result_path = prefix / "drive_c" / "inmm_control_result.json"
    while time.monotonic() < deadline:
        try:
            result = json.loads(result_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            time.sleep(0.05)
            continue
        if result.get("request_id") == request_id:
            return result
        time.sleep(0.05)
    raise RuntimeSafetyError(f"G4 control goal timed out: {goal}")


def _g2_initial_creation_gate(
    scene_state: Mapping[str, Any], read_memory: Callable[[int, int], bytes],
) -> dict[str, Any]:
    """Validate the observed eight-owner creation boundary without normalizing it."""
    failures: list[str] = []
    players = scene_state.get("players")
    units = scene_state.get("units")
    if not isinstance(players, list) or not isinstance(units, list):
        return {"status": "BLOCKED", "failures": ["missing detailed PS3 players/units"]}
    by_owner = {
        int(player["owner"]): player for player in players
        if isinstance(player, Mapping) and isinstance(player.get("owner"), int)
    }
    if set(by_owner) != set(range(8)):
        failures.append("PS3 player owners are not exactly 0..7")
    identity_ids = [unit.get("internal_id") for unit in units if isinstance(unit, Mapping)]
    slots = [unit.get("slot") for unit in units if isinstance(unit, Mapping)]
    valid_ids = all(isinstance(value, int) and value > 0 for value in identity_ids)
    valid_slots = all(isinstance(value, int) and 1 <= value < 1200 for value in slots)
    if (len(identity_ids) != len(units) or len(slots) != len(units) or not valid_ids or not valid_slots
            or len(identity_ids) != len(set(identity_ids))
            or len(slots) != len(set(slots))):
        failures.append("live unit full IDs are missing or not unique")
    records: list[dict[str, Any]] = []
    starts: list[dict[str, int]] = []
    owner_units: dict[str, dict[str, int]] = {}
    for owner in range(8):
        player = by_owner.get(owner)
        if player is None:
            continue
        if not player.get("nation"):
            failures.append(f"owner {owner} has no nation")
        expected_ai = 0 if owner == 0 else 1
        if player.get("ai") != expected_ai:
            failures.append(f"owner {owner} ai role mismatch")
        if not isinstance(player.get("count"), int) or player["count"] < 2:
            failures.append(f"owner {owner} lacks two starting units in ledger")
        if not isinstance(player.get("used"), int) or player["used"] < 20:
            failures.append(f"owner {owner} used ledger is below natural HQ+worker cost")
        if player.get("cap") != 5000:
            failures.append(f"owner {owner} supply cap is not 5000")
        if player.get("reserved") != 0:
            failures.append(f"owner {owner} has pre-existing reserved supply")
        raw = read_memory(0x00956770 + owner * 0x3ABC, 6)
        if len(raw) != 6:
            failures.append(f"owner {owner} raw six-byte role record is incomplete")
            continue
        self_mask = 1 << owner
        if raw[1] != owner or raw[3] != self_mask or raw[4] != (0xFF ^ self_mask):
            failures.append(f"owner {owner} self/enemy masks or player number mismatch")
        if raw[2] != expected_ai:
            failures.append(f"owner {owner} raw ai role mismatch")
        records.append({"owner": owner, "raw_hex": raw.hex(" ")})
        x = struct.unpack("<i", read_memory(0x00B3DE58 + owner * 0x338, 4))[0]
        y = struct.unpack("<i", read_memory(0x00B3DE5C + owner * 0x338, 4))[0]
        starts.append({"owner": owner, "x": x, "y": y})
        if not (0 <= x < 100 and 0 <= y < 100):
            failures.append(f"owner {owner} start point is outside 0..99")
        owned = [unit for unit in units if isinstance(unit, Mapping) and unit.get("owner") == owner]
        hq = [unit for unit in owned if unit.get("type") == 49 and unit.get("hp", 0) > 0]
        worker = [unit for unit in owned if unit.get("type") == 7 and unit.get("hp", 0) > 0]
        if not hq or not worker:
            failures.append(f"owner {owner} lacks live natural HQ49+worker7")
        owner_units[str(owner)] = {
            "ledger_count": int(player.get("count", -1)),
            "ledger_used": int(player.get("used", -1)),
            "reserved": int(player.get("reserved", -1)),
            "live_units": len(owned),
            "hq49": len(hq),
            "worker7": len(worker),
            "extra_units_preserved": max(0, len(owned) - 2),
        }
    config = {
        "game_mode_d42": struct.unpack("<H", read_memory(0x00632D42, 2))[0],
        "game_type_d44": struct.unpack("<H", read_memory(0x00632D44, 2))[0],
        "map_selector_d48": struct.unpack("<H", read_memory(0x00632D48, 2))[0],
        "map_size_d4a": struct.unpack("<H", read_memory(0x00632D4A, 2))[0],
        "seed_d92": struct.unpack("<H", read_memory(0x00632D92, 2))[0],
    }
    if config != {"game_mode_d42": 0, "game_type_d44": 2, "map_selector_d48": 0,
                  "map_size_d4a": 0, "seed_d92": 42}:
        failures.append("G2 creation config/seed fields do not match requested diagnostic")
    if len({(item["x"], item["y"]) for item in starts}) != len(starts):
        failures.append("owner starting points are not distinct")
    return {
        "status": "PASS" if not failures else "BLOCKED",
        "failures": failures,
        "records": records,
        "starts": starts,
        "owners": owner_units,
        "config": config,
        "extra_ai_units_preserved": any(item["extra_units_preserved"] for item in owner_units.values()),
        "normalization_performed": False,
    }


def _g2_stock_stress_phase(
    prefix: Path, output: Path, state: Callable[[bool], dict[str, Any]],
    read_memory: Callable[[int, int], bytes], max_seconds: float = 300.0,
) -> dict[str, Any]:
    """Run one fail-stop, native op5/op1 eight-owner stress phase."""
    phase_started = time.monotonic()
    deadline = phase_started + min(300.0, max_seconds)
    request_path = prefix / "drive_c" / "supply_probe_request.txt"
    result_path = prefix / "drive_c" / "supply_probe_result.json"
    evidence: dict[str, Any] = {
        "status": "UNKNOWN", "pass": False, "requests": [], "owners": {},
        "phase_elapsed_seconds": 0.0, "operations": "native_op1_then_op5_per_owner",
        "op4_used": False, "resource_writes": False, "retries": 0,
    }
    next_id = 1

    def flush() -> None:
        evidence["phase_elapsed_seconds"] = round(time.monotonic() - phase_started, 3)
        _write_json(output / "g2_stock_stress.json", evidence)

    def stop(reason: str, status: str = "PARTIAL_UNKNOWN") -> dict[str, Any]:
        evidence["status"] = status
        evidence["stop_reason"] = reason
        flush()
        return evidence

    def snapshot() -> dict[str, Any]:
        if time.monotonic() >= deadline:
            raise TimeoutError("G2 stock stress phase deadline expired before snapshot")
        return state(True)

    def request(op: int, owner: int, slot: int, unit_type: int, x: int, y: int, count: int) -> dict[str, Any]:
        nonlocal next_id
        if time.monotonic() >= deadline:
            raise TimeoutError("G2 stock stress phase deadline expired")
        request_id = next_id
        next_id += 1
        payload = f"{request_id} {op} {owner} {slot} {unit_type} {x} {y} {count}\n"
        temporary = request_path.with_name("supply_probe_request.tmp")
        temporary.write_text(payload, encoding="ascii")
        temporary.replace(request_path)
        while time.monotonic() < deadline:
            try:
                result = json.loads(result_path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                time.sleep(0.05)
                continue
            if result.get("id") == request_id:
                evidence["requests"].append(result)
                flush()
                return result
            time.sleep(0.05)
        raise TimeoutError(f"G2 stock request timed out: {request_id}")

    def owner_state(snapshot: Mapping[str, Any], owner: int) -> Mapping[str, Any] | None:
        players = snapshot.get("players")
        if not isinstance(players, list):
            return None
        return next((item for item in players if isinstance(item, Mapping) and item.get("owner") == owner), None)

    def owner_units(snapshot: Mapping[str, Any], owner: int) -> list[Mapping[str, Any]]:
        units = snapshot.get("units")
        return [item for item in units if isinstance(item, Mapping) and item.get("owner") == owner] if isinstance(units, list) else []

    def ledger_ok(snapshot: Mapping[str, Any]) -> bool:
        players = snapshot.get("players")
        units = snapshot.get("units")
        if not isinstance(players, list) or not isinstance(units, list) or len(units) > 1199:
            return False
        ids: set[int] = set()
        slots: set[int] = set()
        for unit in units:
            if not isinstance(unit, Mapping):
                return False
            unit_id = unit.get("internal_id")
            slot = unit.get("slot")
            owner = unit.get("owner")
            if (not isinstance(unit_id, int) or unit_id <= 0 or unit_id in ids
                    or not isinstance(slot, int) or not (1 <= slot < 1200) or slot in slots
                    or not isinstance(owner, int) or not (0 <= owner < 8)):
                return False
            ids.add(unit_id)
            slots.add(slot)
        for owner in range(8):
            item = owner_state(snapshot, owner)
            if item is None or item.get("cap") != 5000:
                return False
            # Eight owners retain eight ordinary-cap slots as headroom.
            if not isinstance(item.get("count"), int) or item["count"] > 242:
                return False
        return True

    try:
        costs: dict[int, int] = {}
        for unit_type in range(200):
            if time.monotonic() >= deadline:
                return stop("G2 stock stress phase deadline expired during cost read")
            costs[unit_type] = struct.unpack(
                "<h", read_memory(0x9B5228 + unit_type * 0x394 + 0x10, 2)
            )[0]
        if costs.get(5) != 35 or costs.get(7) != 10 or costs.get(49) != 10:
            return stop("native type-cost table does not match 5=35, 7=10, 49=10", "UNKNOWN")
        evidence["native_costs"] = {
            "type5": costs[5], "type7": costs[7], "type49": costs[49], "table_count": len(costs),
        }
        starts: dict[int, tuple[int, int]] = {}
        for owner in range(8):
            if time.monotonic() >= deadline:
                return stop("G2 stock stress phase deadline expired during start read")
            x = struct.unpack("<i", read_memory(0x00B3DE58 + owner * 0x338, 4))[0]
            y = struct.unpack("<i", read_memory(0x00B3DE5C + owner * 0x338, 4))[0]
            if not (0 <= x < 100 and 0 <= y < 100):
                return stop(f"owner {owner} native start point is outside 0..99")
            starts[owner] = (x, y)
        if len(set(starts.values())) != 8:
            return stop("native owner start points are not eight distinct coordinates")
        evidence["starts"] = {str(owner): {"x": xy[0], "y": xy[1]} for owner, xy in starts.items()}

        records: dict[int, dict[str, Any]] = {}
        # Phase 1: admit one native HQ worker for every owner.  Do not wait
        # for completion here; later owners must receive the same admission
        # opportunity before earlier workers age.
        for owner in range(8):
            before = snapshot()
            player = owner_state(before, owner)
            units_before = owner_units(before, owner)
            if player is None or not ledger_ok(before):
                return stop(f"owner {owner} initial ledger/global-cap gate failed")
            if (player.get("used") != 20 or player.get("reserved") != 0
                    or player.get("count") != 2 or player.get("cap") != 5000):
                return stop(f"owner {owner} train-first natural HQ/worker ledger gate failed")
            hqs = [unit for unit in units_before if unit.get("type") == 49 and unit.get("hp", 0) > 0]
            workers = [unit for unit in units_before if unit.get("type") == 7 and unit.get("hp", 0) > 0]
            if not hqs or not workers:
                return stop(f"owner {owner} lacks live HQ49+worker7 before native op1")
            hq = hqs[0]
            hq_slot = hq.get("slot")
            hq_id = hq.get("internal_id")
            if (not isinstance(hq_slot, int) or not (1 <= hq_slot < 1200)
                    or not isinstance(hq_id, int) or hq_id <= 0):
                return stop(f"owner {owner} HQ slot/full ID is invalid")
            initial_ids = {
                unit.get("internal_id") for unit in units_before
                if isinstance(unit.get("internal_id"), int)
            }
            result = request(1, owner, hq_slot, 7, 0, 0, 0)
            result_before = result.get("before")
            result_after = result.get("after")
            producer = result.get("producer")
            producer_id = producer.get("id") if isinstance(producer, Mapping) else None
            if (result.get("op") != 1 or result.get("owner") != owner or result.get("ps") != 3
                    or result.get("ok") is not True or result.get("raw_return") != 1
                    or not isinstance(result_before, Mapping) or not isinstance(result_after, Mapping)
                    or not isinstance(producer, Mapping)
                    or result_before.get("used") != 20 or result_before.get("reserved") != 0
                    or result_before.get("count") != 2 or result_before.get("cap") != 5000
                    or producer.get("id") != hq_id or producer_id != hq_id
                    or producer.get("slot") != hq_slot or producer.get("type") != 49
                    or producer.get("owner") != owner
                    or not isinstance(producer.get("command"), int)
                    or not isinstance(producer.get("production_type"), int)
                    or not isinstance(producer.get("progress"), int)
                    or result_after.get("used") not in (20, 30)
                    or result_after.get("reserved") not in (0, 10)):
                return stop(f"owner {owner} native op1 lacks atomic same-HQ witness; no retry")

            admission_snapshot: dict[str, Any] | None = None
            admission_mode = ""
            admission_deadline = min(deadline, time.monotonic() + 2.0)
            while time.monotonic() < admission_deadline:
                current = snapshot()
                current_player = owner_state(current, owner)
                current_units = owner_units(current, owner)
                current_hq = next((unit for unit in current_units
                                   if unit.get("internal_id") == hq_id), None)
                current_progress = current_hq.get("progress") if isinstance(current_hq, Mapping) else None
                new_workers = [unit for unit in current_units
                               if unit.get("internal_id") not in initial_ids
                               and unit.get("owner") == owner and unit.get("type") == 7]
                hq_started = (isinstance(current_hq, Mapping)
                              and current_hq.get("type") == 49
                              and current_hq.get("slot") == hq_slot
                              and current_hq.get("owner") == owner
                              and current_hq.get("command") == 15
                              and current_hq.get("production_type") == 7
                              and isinstance(current_progress, int)
                              and current_progress >= 0
                              and isinstance(current_player, Mapping)
                              and current_player.get("reserved") == 10)
                worker_born = (isinstance(current_player, Mapping)
                               and current_player.get("used") == 30
                               and current_player.get("reserved") == 0
                               and bool(new_workers))
                if hq_started or worker_born:
                    admission_snapshot = current
                    admission_mode = "pending_same_hq" if hq_started else "immediate_worker_birth"
                    break
                time.sleep(0.1)
            if admission_snapshot is None:
                return stop(f"owner {owner} native op1 admission was not observed; no retry")
            admission_player = owner_state(admission_snapshot, owner)
            if admission_player is None or admission_player.get("reserved") not in (0, 10):
                return stop(f"owner {owner} native op1 admission ledger is malformed")
            admission_units = owner_units(admission_snapshot, owner)
            admission_workers = [unit for unit in admission_units
                                 if unit.get("internal_id") not in initial_ids
                                 and unit.get("owner") == owner and unit.get("type") == 7]
            records[owner] = {
                "initial_ids": initial_ids, "hq_id": hq_id, "hq_slot": hq_slot,
                "admission": admission_snapshot, "admission_mode": admission_mode,
                "op1": {"raw_return": result.get("raw_return"), "before": dict(result_before),
                        "after": dict(result_after), "producer": dict(producer),
                        "new_worker_ids": sorted(int(item["internal_id"]) for item in admission_workers
                                                  if isinstance(item.get("internal_id"), int))},
            }
            evidence["owners"].setdefault(str(owner), {})["op1"] = {
                **records[owner]["op1"], "pending_reserved": admission_player.get("reserved"),
                "admission_mode": admission_mode,
            }
            flush()

        # Phase 2: seed one exact 142-unit native fixture for every admitted
        # owner.  Natural ledger changes invalidate that owner's precondition;
        # never normalize, retry, or write resources to recover it.
        for owner in range(8):
            record = records[owner]
            seed_before = snapshot()
            seed_player = owner_state(seed_before, owner)
            seed_units_before = owner_units(seed_before, owner)
            if seed_player is None or not ledger_ok(seed_before):
                return stop(f"owner {owner} pre-seed ledger/global-cap gate failed")
            seed_used = seed_player.get("used")
            seed_reserved = seed_player.get("reserved")
            seed_count = seed_player.get("count")
            if (not isinstance(seed_used, int) or not isinstance(seed_reserved, int)
                    or (seed_used, seed_reserved) not in ((20, 10), (30, 0))
                    or not isinstance(seed_count, int) or seed_player.get("cap") != 5000):
                return stop(f"owner {owner} native op1 state is not pending/completed")
            expected_worker_ids = set(record["op1"]["new_worker_ids"])
            current_worker_ids = {unit.get("internal_id") for unit in seed_units_before
                                  if unit.get("type") == 7 and unit.get("owner") == owner}
            if expected_worker_ids and not expected_worker_ids.issubset(current_worker_ids):
                return stop(f"owner {owner} native worker identity changed before op5")
            if (seed_used + seed_reserved + 142 * costs[5] > 5000
                    or seed_count + 142 + 1 > 242):
                return stop(f"owner {owner} lacks op5 supply/count headroom after op1")
            before_units = seed_before.get("units", [])
            players_before = seed_before.get("players", [])
            pending_slots = sum(
                max(0, int(item.get("reserved", 0)) // costs[7])
                for item in players_before if isinstance(item, Mapping) and isinstance(item.get("reserved"), int)
            ) if isinstance(players_before, list) else 0
            remaining_seeds = 8 - owner
            # All eight admitted workers remain conservatively budgeted, while
            # pending_slots separately accounts for queued workers and organic
            # reservations already occupying the native pool.
            if (not isinstance(before_units, list)
                    or len(before_units) + pending_slots + 142 * remaining_seeds + 8 > 1199):
                return stop(f"owner {owner} lacks global 1199-slot headroom after op1")
            x, y = starts[owner]
            result = request(5, owner, 0, 5, x, y, 142)
            result_before = result.get("before")
            result_after = result.get("after")
            producer = result.get("producer")
            if (result.get("op") != 5 or result.get("owner") != owner or result.get("ps") != 3
                    or result.get("ok") is not True or result.get("raw_return") != 1
                    or result.get("fixture_added") != 142
                    or not isinstance(result_before, Mapping) or not isinstance(result_after, Mapping)
                    or not isinstance(producer, Mapping)
                    or producer.get("owner") != owner or producer.get("type") != 5
                    or not isinstance(producer.get("id"), int) or not (1 <= producer.get("slot", 0) < 1200)
                    or result_after.get("used") != result_before.get("used", 0) + 4970
                    or result_after.get("count") != result_before.get("count", 0) + 142):
                return stop(f"owner {owner} op5 partial/accounting failure; no retry")
            after = snapshot()
            after_player = owner_state(after, owner)
            new_ids = {unit.get("internal_id") for unit in owner_units(after, owner)} - {
                unit.get("internal_id") for unit in seed_units_before
            }
            new_units = [unit for unit in owner_units(after, owner) if unit.get("internal_id") in new_ids]
            new_type5 = [unit for unit in new_units if unit.get("type") == 5 and unit.get("owner") == owner]
            after_count = after_player.get("count") if after_player is not None else None
            after_used = after_player.get("used") if after_player is not None else None
            after_reserved = after_player.get("reserved") if after_player is not None else None
            legal_post_seed = (after_used == seed_used + 4970 and after_reserved == seed_reserved)
            if seed_used == 20:
                legal_post_seed = legal_post_seed or (after_used == 5000 and after_reserved == 0)
            if (after_player is None or not isinstance(after_count, int)
                    or not isinstance(after_used, int) or not isinstance(after_reserved, int)
                    or not legal_post_seed or after_count < seed_count + 142
                    or len(new_type5) < 142 or producer.get("id") not in new_ids):
                return stop(f"owner {owner} op5 roster/ledger mismatch; no retry")
            record["seed_before"] = seed_before
            record["post_seed"] = after
            evidence["owners"].setdefault(str(owner), {})["op5"] = {
                "fixture_added": result.get("fixture_added"), "fixture_attempts": result.get("fixture_attempts"),
                "before": result_before, "after": result_after,
                "producer": dict(producer),
                "new_type5_ids": sorted(item for item in new_ids if isinstance(item, int)),
                "organic_extra_units": max(0, len(new_units) - 142),
                "worker_pending_during_seed": seed_reserved == 10,
            }
            flush()

        # Phase 3: jointly observe all native worker completions.  This keeps
        # the eight-owner admission/seed phase from aging owner 0 alone.
        completed: set[int] = set()
        while len(completed) < 8 and time.monotonic() < deadline:
            current = snapshot()
            if not ledger_ok(current):
                return stop("joint completion roster/ledger identity gate failed")
            for owner in range(8):
                if owner in completed:
                    continue
                record = records[owner]
                current_player = owner_state(current, owner)
                current_units = owner_units(current, owner)
                new_workers = [unit for unit in current_units
                               if unit.get("internal_id") not in record["initial_ids"]
                               and unit.get("owner") == owner and unit.get("type") == 7]
                if (current_player is not None and current_player.get("used") == 5000
                        and current_player.get("reserved") == 0):
                    expected = set(record["op1"]["new_worker_ids"])
                    if not new_workers or (expected and not expected.issubset(
                            {unit.get("internal_id") for unit in new_workers})):
                        return stop(f"owner {owner} reached used=5000 without attributable worker")
                    completed.add(owner)
                    evidence["owners"].setdefault(str(owner), {})["completion"] = {
                        "used": current_player.get("used"), "reserved": current_player.get("reserved"),
                        "new_worker_ids": sorted(int(item["internal_id"]) for item in new_workers
                                                 if isinstance(item.get("internal_id"), int)),
                        "native_op1_completed": True,
                    }
                    flush()
            if len(completed) < 8:
                time.sleep(0.1)
        if len(completed) != 8:
            return stop("joint native worker completion timed out")
        final = snapshot()
        final_players = [owner_state(final, owner) for owner in range(8)]
        if (not ledger_ok(final)
                or any(item is None or item.get("used") != 5000 or item.get("reserved") != 0
                       for item in final_players)):
            return stop("final eight-owner cap/used ledger gate failed")
        reconcile: dict[str, int] = {}
        for owner in range(8):
            units = owner_units(final, owner)
            if any(not isinstance(unit.get("type"), int) or unit["type"] not in costs for unit in units):
                return stop(f"owner {owner} has an unpriced final unit")
            cost_sum = sum(costs[int(unit["type"])] for unit in units)
            reconcile[str(owner)] = cost_sum
            final_player = owner_state(final, owner)
            if final_player is None or cost_sum != final_player.get("used"):
                return stop(f"owner {owner} final native cost reconciliation failed")
        evidence["cost_reconciliation"] = reconcile
        evidence["status"] = "PASS"
        evidence["pass"] = True
        evidence["classification"] = "ASSISTED_LOCAL_HIGH_COST_ONLY"
        flush()
        return evidence
    except Exception as exc:
        return stop(str(exc))


def g2_stock_lifecycle(
    mode: str,
    *,
    stock_snapshot: Mapping[str, Any],
    read_memory: Callable[[int, int], bytes],
    native_result: Mapping[str, Any],
    save_path: Path,
    save_slot: int,
    save_previously_absent: bool,
    expected_save_sha256: str,
    pending_witness: Mapping[str, Any],
    fresh_snapshot: Mapping[str, Any] | None = None,
    loaded_snapshot: Mapping[str, Any] | None = None,
    loaded_save_path: Path | None = None,
    raw_pending_witness: Mapping[str, Any] | None = None,
    output: Path | None = None,
) -> dict[str, Any]:
    """Validate one narrow G2 stock save or fresh-load lifecycle boundary.

    The caller owns the already-prepared private runtime and native op2/op3
    invocation.  This function only accepts the resulting snapshots and
    witnesses; it never writes game memory, creates save files, normalizes a
    roster, or retries a native operation.
    """
    evidence: dict[str, Any] = {
        "status": "BLOCKED", "pass": False, "mode": mode,
        "memory_writes": False, "normalization_performed": False,
        "native_retries": 0, "product_pass_claim": False,
        "limitations": [
            "narrow G2 stock save/fresh-load boundary only",
            "stable pending witness is not atomic or first-postload proof",
            "no death-release, LAN, campaign, or full product PASS claim",
        ],
    }

    def fail(reason: str, status: str = "BLOCKED") -> dict[str, Any]:
        evidence["status"] = status
        evidence["pass"] = False
        evidence["reason"] = reason
        if output is not None:
            _write_json(output / "g2_stock_lifecycle.json", evidence)
        return evidence

    if output is not None:
        output_real = _real(output)
        if (not output.is_absolute() or not _under(output_real, _real(G2_ARTIFACT_ROOT))
                or output.exists() or output.is_symlink()):
            output = None
            return fail("lifecycle output must be a fresh absolute directory under the approved temp root")
    if mode not in G2_LIFECYCLE_MODES:
        return fail("lifecycle mode must be exactly save or load")
    if not isinstance(stock_snapshot, Mapping) or not isinstance(native_result, Mapping):
        return fail("stock snapshot/native result is malformed")
    if not isinstance(pending_witness, Mapping):
        return fail("pending HQ stable witness is missing")
    if not isinstance(save_slot, int) or not (1 <= save_slot < 100) or save_previously_absent is not True:
        return fail("lifecycle save slot must be a previously-absent slot 1..99")
    if (not isinstance(expected_save_sha256, str)
            or re.fullmatch(r"[0-9a-fA-F]{64}", expected_save_sha256) is None):
        return fail("lifecycle save hash is not a SHA-256")
    if save_path.is_symlink() or not save_path.is_file() or save_path.stat().st_size <= 0:
        return fail("private lifecycle save file is missing or linked")
    if save_path.name.lower() not in {f"save{save_slot:03d}", f"save{save_slot:03d}.dat"}:
        return fail("save path basename does not match the selected native slot")
    if save_path.parent.name.lower() != "save":
        return fail("save path must be the private game/save directory")
    actual_hash = _sha256(save_path)
    if actual_hash.lower() != expected_save_sha256.lower():
        return fail("private save hash mismatch")
    evidence["save_file"] = {
        "path": str(save_path), "slot": save_slot,
        "sha256": actual_hash, "previously_absent": True,
    }

    def costs() -> dict[int, int] | None:
        result: dict[int, int] = {}
        try:
            for unit_type in range(53):
                raw = read_memory(0x9B5228 + unit_type * 0x394 + 0x10, 2)
                if len(raw) != 2:
                    return None
                result[unit_type] = struct.unpack("<h", raw)[0]
        except (OSError, struct.error, ValueError):
            return None
        return result

    native_costs = costs()
    if native_costs is None or native_costs.get(5) != 35 or native_costs.get(7) != 10 \
            or native_costs.get(49) != 10:
        return fail("native cost reads 0..52 are incomplete or unexpected")
    evidence["native_costs"] = {
        "type5": native_costs[5], "type7": native_costs[7],
        "type49": native_costs[49], "max_type_read": 52,
    }

    def roster(snapshot: Mapping[str, Any], *, initial: bool = False) -> tuple[dict[int, Mapping[str, Any]], list[Mapping[str, Any]]] | None:
        players = snapshot.get("players")
        units = snapshot.get("units")
        if not isinstance(players, list) or not isinstance(units, list):
            return None
        by_owner = {
            int(item["owner"]): item for item in players
            if isinstance(item, Mapping) and isinstance(item.get("owner"), int)
        }
        if set(by_owner) != set(range(8)):
            return None
        if initial:
            if len(units) != 16:
                return None
        elif len(units) != 1160:
            return None
        ids: set[int] = set()
        slots: set[int] = set()
        for unit in units:
            if not isinstance(unit, Mapping):
                return None
            unit_id, slot, owner, unit_type, hp = (
                unit.get("internal_id"), unit.get("slot"), unit.get("owner"),
                unit.get("type"), unit.get("hp"),
            )
            if (not isinstance(unit_id, int) or unit_id <= 0 or unit_id in ids
                    or not isinstance(slot, int) or not (1 <= slot < 1200) or slot in slots
                    or not isinstance(owner, int) or not (0 <= owner < 8)
                    or not isinstance(unit_type, int) or unit_type not in native_costs
                    or not isinstance(hp, (int, float)) or hp <= 0):
                return None
            ids.add(unit_id)
            slots.add(slot)
        for owner in range(8):
            player = by_owner[owner]
            owner_units = [unit for unit in units if unit.get("owner") == owner]
            if (player.get("cap") != 5000
                    or player.get("count") != (2 if initial else 145)
                    or player.get("used") != (20 if initial else 5000)
                    or player.get("reserved") not in (0, 10)
                    or len(owner_units) != (2 if initial else 145)):
                return None
            if not initial:
                cost_sum = sum(native_costs[int(unit["type"])] for unit in owner_units)
                if cost_sum != player.get("used"):
                    return None
        return ({int(owner): player for owner, player in by_owner.items()}, units)

    stock_roster = roster(stock_snapshot)
    if stock_roster is None:
        return fail("stock snapshot is not exact live 8-owner used5000/count145/global1160")
    evidence["stock_roster"] = {"owners": 8, "units": 1160, "cost_reconciled": True}
    # Persist the exact expected witness consumed by the second fresh load;
    # summaries alone cannot prove full-ID/slot restoration.
    evidence["stock_snapshot"] = stock_snapshot

    pending_owner = pending_witness.get("owner")
    pending_id = pending_witness.get("internal_id")
    pending_slot = pending_witness.get("slot")
    if (pending_owner != 4 or not isinstance(pending_id, int) or pending_id <= 0
            or not isinstance(pending_slot, int) or not (1 <= pending_slot < 1200)
            or pending_witness.get("type") != 49
            or pending_witness.get("command") != 15
            or pending_witness.get("production_type") != 7
            or pending_witness.get("progress") != 100
            or pending_witness.get("reserved") != 10
            or pending_witness.get("stable_tick") is not True
            or not isinstance(pending_witness.get("tick_before"), int)
            or not isinstance(pending_witness.get("tick_after"), int)
            or pending_witness["tick_before"] > pending_witness["tick_after"]):
        return fail("owner4 pending HQ stable tick-bracket witness is invalid")
    stock_pending = next((unit for unit in stock_roster[1]
                          if unit.get("internal_id") == pending_id), None)
    if (stock_pending is None or stock_pending.get("slot") != pending_slot
            or stock_pending.get("owner") != 4 or stock_pending.get("type") != 49
            or stock_pending.get("command") != pending_witness.get("command")
            or stock_pending.get("production_type") != pending_witness.get("production_type")
            or stock_pending.get("progress") != pending_witness.get("progress")):
        return fail("owner4 pending HQ identity is not present in stock roster")
    evidence["pending_hq"] = dict(pending_witness)
    evidence["pending_witness"] = dict(pending_witness)
    evidence["save_sha256"] = actual_hash

    required_native = {"op": 2 if mode == "save" else 3, "ps": 3}
    provenance = native_result.get("provenance")
    if any(native_result.get(key) != value for key, value in required_native.items()) \
            or not isinstance(native_result.get("owner"), int) \
            or not (0 <= native_result["owner"] < 8) \
            or native_result.get("ok") is not True \
            or native_result.get("raw_return") != 1 \
            or not isinstance(native_result.get("thread"), int) \
            or not isinstance(provenance, Mapping) \
            or provenance.get("bridge_sha256") != G2_APPROVED_BRIDGE_SHA256 \
            or provenance.get("caller") != "0x42334C" \
            or provenance.get("thread_check") != "window_thread_equals_current_thread":
        return fail("native save/load op witness is invalid")
    evidence["native_result"] = dict(native_result)

    if mode == "save":
        evidence["status"] = "PASS"
        evidence["pass"] = True
        evidence["classification"] = "G2_STOCK_SAVE_BOUNDARY_PASS"
    else:
        if fresh_snapshot is None or loaded_snapshot is None or loaded_save_path is None:
            return fail("fresh-load requires fresh creation and loaded snapshots/files")
        if fresh_snapshot.get("ps") != 3:
            return fail("fresh-load requires the original PS3 eight-owner creation boundary")
        fresh_roster = roster(fresh_snapshot, initial=True)
        loaded_roster = roster(loaded_snapshot)
        if fresh_roster is None or loaded_roster is None:
            return fail("fresh PS7 creation or loaded roster is malformed")
        if (loaded_save_path.is_symlink() or not loaded_save_path.is_file()
                or loaded_save_path.stat().st_size <= 0) \
                or _sha256(loaded_save_path).lower() != expected_save_sha256.lower():
            return fail("fresh-load save copy is not byte-identical")
        stock_by_id = {int(unit["internal_id"]): unit for unit in stock_roster[1]}
        loaded_by_id = {int(unit["internal_id"]): unit for unit in loaded_roster[1]}
        if set(stock_by_id) != set(loaded_by_id):
            return fail("loaded full-ID roster does not match saved stock roster")
        for unit_id, saved in stock_by_id.items():
            loaded = loaded_by_id[unit_id]
            if any(loaded.get(key) != saved.get(key) for key in ("slot", "owner", "type", "hp")):
                return fail("loaded unit slot/owner/type/HP identity mismatch")
        for owner in range(8):
            saved_player = stock_roster[0][owner]
            loaded_player = loaded_roster[0][owner]
            if any(loaded_player.get(key) != saved_player.get(key)
                   for key in ("count", "cap", "used", "reserved")):
                return fail("loaded owner ledger mismatch")
        loaded_pending = next((unit for unit in loaded_roster[1]
                               if unit.get("internal_id") == pending_id), None)
        if (loaded_pending is None or loaded_pending.get("slot") != pending_slot
                or loaded_pending.get("owner") != 4 or loaded_pending.get("type") != 49
                or loaded_pending.get("command") != pending_witness.get("command")
                or loaded_pending.get("production_type") != pending_witness.get("production_type")
                or loaded_pending.get("progress") != pending_witness.get("progress")):
            return fail("loaded owner4 pending HQ identity mismatch")
        evidence["loaded_roster"] = {"owners": 8, "units": 1160, "full_id_mapping_equal": True}
        evidence["status"] = "PASS"
        evidence["pass"] = True
        evidence["classification"] = "G2_STOCK_FRESH_LOAD_BOUNDARY_PASS"
    if raw_pending_witness is not None:
        raw_before = raw_pending_witness.get("before")
        raw_after = raw_pending_witness.get("after")
        if isinstance(raw_before, Mapping) and isinstance(raw_after, Mapping) \
                and all(isinstance(raw_before.get(key), int) and raw_before.get(key) == raw_after.get(key)
                        for key in ("384", "388", "38C")):
            evidence["raw_pending_stable_witness"] = dict(raw_pending_witness)
        else:
            evidence["raw_pending_stable_witness"] = {"status": "UNKNOWN"}
    if output is not None:
        if not output.is_absolute() or not _under(_real(output), _real(G2_ARTIFACT_ROOT)):
            return fail("lifecycle output must be under the approved absolute temp root")
        if output.exists():
            return fail("lifecycle output must be fresh")
        output.mkdir(parents=True)
        _write_json(output / "g2_stock_lifecycle.json", evidence)
    return evidence


_g2_stock_lifecycle_validator = g2_stock_lifecycle


def validate_g2_stock_24k_observation_gate(
    *,
    enabled: bool,
    goal: str | None = None,
    candidate: str | None = None,
    bridge_sha256: str | None = None,
    lifecycle: str | None = None,
    stock_stress: bool = False,
    intervention_goal: str | None = None,
    intervention_delay: float = 0,
    relocation_diagnostic: bool = False,
    fresh_creation_gate: Mapping[str, Any] | None = None,
    load_result: Mapping[str, Any] | None = None,
    post_load_effects: Mapping[str, Any] | None = None,
    target_ticks: int = G2_STOCK_OBSERVATION_TICKS,
    wall_seconds: float = G2_STOCK_OBSERVATION_WALL_SECONDS,
) -> dict[str, Any]:
    """Validate the explicit, default-off 24k stock observation contract.

    This gate is intentionally stricter than the ordinary G2 sampler.  It
    accepts only the already-approved fixed-supply creation followed by the
    witnessed native fresh-load boundary; it never prepares a runtime,
    invokes a bridge, writes game memory, or launches a process.
    """
    if not enabled:
        return {"enabled": False, "status": "DISABLED", "observation_opt_in": False}
    if goal != G2_CREATION_GOAL:
        raise RuntimeSafetyError("G2 24k observation requires the exact creation goal")
    if candidate != G2_CREATION_CANDIDATE:
        raise RuntimeSafetyError("G2 24k observation requires the approved fixed-supply candidate")
    if bridge_sha256 != G2_APPROVED_BRIDGE_SHA256:
        raise RuntimeSafetyError("G2 24k observation requires the approved 8de5 bridge")
    if lifecycle != "load":
        raise RuntimeSafetyError("G2 24k observation requires lifecycle=load")
    if stock_stress or intervention_goal is not None or intervention_delay != 0:
        raise RuntimeSafetyError("G2 24k observation cannot combine stress or interventions")
    if relocation_diagnostic:
        raise RuntimeSafetyError("G2 24k observation cannot combine relocation diagnostics")
    if target_ticks != G2_STOCK_OBSERVATION_TICKS:
        raise RuntimeSafetyError("G2 24k observation tick target is fixed at 24000")
    if wall_seconds != G2_STOCK_OBSERVATION_WALL_SECONDS:
        raise RuntimeSafetyError("G2 24k observation wall ceiling is fixed at 45 minutes")
    if not isinstance(fresh_creation_gate, Mapping) or fresh_creation_gate.get("status") != "PASS":
        raise RuntimeSafetyError("G2 24k observation requires a passed fresh 16-unit creation gate")
    if (not isinstance(load_result, Mapping)
            or load_result.get("status") != "PASS"
            or load_result.get("classification") != "G2_STOCK_FRESH_LOAD_BOUNDARY_PASS"
            or load_result.get("save_sha256") != G2_STOCK_24K_SAVE_SHA256
            or load_result.get("witness_sha256") != G2_STOCK_24K_WITNESS_SHA256):
        raise RuntimeSafetyError("G2 24k observation requires the exact approved save/witness fresh-load PASS")
    if not isinstance(post_load_effects, Mapping):
        raise RuntimeSafetyError("G2 24k observation requires explicit post-load side-effect gates")
    if (post_load_effects.get("ui_actions") != 0
            or post_load_effects.get("input_actions") != 0
            or post_load_effects.get("bridge_requests") != 0
            or post_load_effects.get("save_actions") != 0
            or post_load_effects.get("stress_interventions") is not False):
        raise RuntimeSafetyError("G2 24k observation forbids post-load UI, bridge, input, save, or intervention actions")
    return {
        "enabled": True, "status": "PASS", "observation_opt_in": True,
        "goal": goal, "candidate": candidate, "bridge_sha256": bridge_sha256,
        "lifecycle": lifecycle, "target_ticks": target_ticks,
        "wall_seconds": wall_seconds, "post_load_effects": dict(post_load_effects),
        "save_sha256": G2_STOCK_24K_SAVE_SHA256,
        "witness_sha256": G2_STOCK_24K_WITNESS_SHA256,
        "product_pass_claim": False,
    }


def _g2_observation_reader(reader: Callable[..., Mapping[str, Any]], detailed: bool) -> Mapping[str, Any]:
    """Call a state reader using the existing ``state(detailed)`` contract."""
    value = reader(detailed)
    if not isinstance(value, Mapping):
        raise RuntimeSafetyError("G2 observation state reader returned a non-object")
    return value


def _g2_observation_snapshot(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    """Copy one full state without assigning semantic meaning to raw fields."""
    players = snapshot.get("players")
    units = snapshot.get("units")
    tick = snapshot.get("tick")
    ps = snapshot.get("ps")
    if not isinstance(players, list) or not isinstance(units, list) or not isinstance(tick, int):
        raise RuntimeSafetyError("G2 observation snapshot lacks players, units, or integer tick")
    if ps != 3:
        raise RuntimeSafetyError(f"G2 observation left PS3 (observed {ps!r})")
    owners: dict[int, dict[str, Any]] = {}
    for player in players:
        if not isinstance(player, Mapping) or not isinstance(player.get("owner"), int):
            raise RuntimeSafetyError("G2 observation roster contains a malformed owner")
        owner = int(player["owner"])
        if owner in owners or not 0 <= owner < 8:
            raise RuntimeSafetyError("G2 observation roster is not exactly one record per owner")
        record = dict(player)
        # Keep all supplied resource/ledger fields; they are observations, not
        # a normalized cost identity.  JSON validation below catches opaque
        # test doubles before they can corrupt the streamed evidence.
        json.dumps(record)
        owners[owner] = record
    if set(owners) != set(range(8)):
        raise RuntimeSafetyError("G2 observation requires all eight owner rosters")
    copied_units: list[dict[str, Any]] = []
    occupied_dead: list[dict[str, Any]] = []
    live: list[dict[str, Any]] = []
    by_slot: dict[int, int] = {}
    for unit in units:
        if not isinstance(unit, Mapping):
            raise RuntimeSafetyError("G2 observation unit record is malformed")
        unit_id: Any = unit.get("internal_id")
        if not isinstance(unit_id, int):
            unit_id = unit.get("full_id")
        unit_slot: Any = unit.get("slot")
        unit_owner: Any = unit.get("owner")
        unit_type: Any = unit.get("type")
        hp: Any = unit.get("hp")
        if (not isinstance(unit_id, int) or unit_id <= 0
                or not isinstance(unit_slot, int) or not 0 <= unit_slot < 1200
                or unit_slot in by_slot or not isinstance(unit_owner, int) or not 0 <= unit_owner < 8
                or not isinstance(unit_type, int) or not isinstance(hp, (int, float))):
            raise RuntimeSafetyError("G2 observation unit identity/slot/owner fields are malformed")
        by_slot[unit_slot] = unit_id
        copied = dict(unit)
        json.dumps(copied)
        copied_units.append(copied)
        identity = {"slot": unit_slot, "full_id": unit_id, "owner": unit_owner,
                    "type": unit_type, "hp": hp}
        if hp > 0:
            live.append(identity)
        else:
            occupied_dead.append(identity)
    return {
        "ps": ps, "tick": tick, "players": [owners[i] for i in range(8)],
        "units": copied_units,
        "roster_by_owner": {str(i): owners[i] for i in range(8)},
        "occupied_unit_count": len(copied_units),
        "live_unit_count": len(live),
        "occupied_dead_unit_count": len(occupied_dead),
        "occupied_dead_units": occupied_dead,
        "live_units": live,
        "slot_to_full_id": {str(slot): unit_id for slot, unit_id in by_slot.items()},
    }


def g2_stock_24k_observe(
    output: Path,
    *,
    enabled: bool = False,
    goal: str | None = None,
    candidate: str | None = None,
    bridge_sha256: str | None = None,
    lifecycle: str | None = None,
    stock_stress: bool = False,
    intervention_goal: str | None = None,
    intervention_delay: float = 0,
    relocation_diagnostic: bool = False,
    fresh_creation_gate: Mapping[str, Any] | None = None,
    load_result: Mapping[str, Any] | None = None,
    post_load_effects: Mapping[str, Any] | None = None,
    snapshot_reader: Callable[[bool], Mapping[str, Any]] | None = None,
    light_reader: Callable[[], Mapping[str, Any]] | None = None,
    process_reader: Callable[[], Mapping[str, Any]] | None = None,
    active_list_reader: Callable[[], Mapping[str, Any]] | None = None,
    monotonic: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
    target_ticks: int = G2_STOCK_OBSERVATION_TICKS,
    wall_seconds: float = G2_STOCK_OBSERVATION_WALL_SECONDS,
    sample_seconds: float = G2_STOCK_OBSERVATION_SAMPLE_SECONDS,
) -> dict[str, Any]:
    """Stream a bounded post-load stock observation; never mutates game state.

    ``snapshot_reader`` is the existing ``state(detailed)`` reader.  A
    separate ``light_reader`` may provide the before/after tick bracket.  The
    function deliberately returns a duration milestone, timeout, or partial
    classification rather than a gameplay/product PASS.
    """
    if not enabled:
        return {"status": "DISABLED", "observation_opt_in": False,
                "product_pass_claim": False, "samples": 0}
    gate = validate_g2_stock_24k_observation_gate(
        enabled=True, goal=goal, candidate=candidate, bridge_sha256=bridge_sha256,
        lifecycle=lifecycle, stock_stress=stock_stress, intervention_goal=intervention_goal,
        intervention_delay=intervention_delay, relocation_diagnostic=relocation_diagnostic,
        fresh_creation_gate=fresh_creation_gate, load_result=load_result,
        post_load_effects=post_load_effects, target_ticks=target_ticks,
        wall_seconds=wall_seconds,
    )
    if snapshot_reader is None:
        raise RuntimeSafetyError("G2 24k observation requires a post-load snapshot reader")
    if sample_seconds < G2_STOCK_OBSERVATION_MIN_SNAPSHOT_SECONDS:
        raise RuntimeSafetyError("G2 full snapshots must be at least 2 seconds apart")
    output = _real(output)
    if (not output.is_absolute() or output.exists() or output.is_symlink()
            or not _under(output, _real(G2_ARTIFACT_ROOT))):
        raise RuntimeSafetyError("G2 observation output must be a fresh absolute directory under the approved temp root")
    output.mkdir(parents=True)
    samples_path = output / "samples.jsonl"
    summary_path = output / "summary.json"
    read_light = light_reader or (lambda: _g2_observation_reader(snapshot_reader, False))
    started = monotonic()
    deadline = started + wall_seconds
    previous_tick: int | None = None
    first_tick: int | None = None
    previous_by_slot: dict[int, int] = {}
    samples = 0
    events: list[dict[str, Any]] = []
    event_count = 0
    errors: list[dict[str, Any]] = []
    status = "OBSERVING"
    reason: str | None = None
    last_tick: int | None = None
    next_sample = started
    previous_wall = started
    active_mismatch_signature: tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]] | None = None
    active_mismatch_streak = 0

    def record_event(event: dict[str, Any]) -> None:
        nonlocal event_count
        event_count += 1
        if len(events) < 256:
            events.append(event)

    summary: dict[str, Any] = {
        "schema": "syw2plus.g2.stock_24k_observation_summary.v1",
        "status": status, "product_pass_claim": False, "gate": gate,
        "target_ticks": target_ticks, "wall_seconds": wall_seconds,
        "sample_seconds": sample_seconds, "samples": 0, "events": events,
        "errors": errors, "death_reuse": "NOT_OBSERVED",
    }
    try:
        with samples_path.open("w", encoding="utf-8") as stream:
            while True:
                now = monotonic()
                if now < previous_wall:
                    status, reason = "INVALID_CLOCK_PARTIAL", "monotonic clock moved backwards"
                    break
                previous_wall = now
                if now >= deadline:
                    status, reason = "TIMEOUT_PARTIAL", "45-minute wall ceiling before 24000 original ticks"
                    break
                if now < next_sample:
                    sleep(min(next_sample - now, max(0.0, deadline - now)))
                    continue
                try:
                    before = read_light()
                    full = _g2_observation_snapshot(_g2_observation_reader(snapshot_reader, True))
                    after = read_light()
                    tick_before, tick_after = before.get("tick"), after.get("tick")
                    if not isinstance(tick_before, int) or not isinstance(tick_after, int):
                        raise RuntimeSafetyError("tick bracket did not contain integer ticks")
                    tick = int(full["tick"])
                    ps_before, ps_after = before.get("ps"), after.get("ps")
                    if ps_before is not None and ps_before != 3 or ps_after is not None and ps_after != 3:
                        status, reason = "NON_PS3_PARTIAL", "light PS bracket left PS3"
                    if first_tick is None:
                        first_tick = tick
                    if previous_tick is not None and tick < previous_tick:
                        status, reason = "TICK_REVERSAL_PARTIAL", "original tick decreased; wrap/reversal is not success"
                    if status == "OBSERVING" and tick < first_tick:
                        status, reason = "TICK_REVERSAL_PARTIAL", "original tick reversed from loaded start"
                    process = None
                    if process_reader is not None:
                        process = dict(process_reader())
                        if process.get("alive") is False:
                            status, reason = "PROCESS_EXIT_PARTIAL", "owned process reported exited"
                    current_by_slot = {int(k): int(v) for k, v in full["slot_to_full_id"].items()}
                    active_list = dict(active_list_reader()) if active_list_reader is not None else None
                    if active_list is not None:
                        exact = active_list.get("exact_set_match") is True
                        if exact:
                            active_mismatch_signature = None
                            active_mismatch_streak = 0
                        else:
                            signature = (
                                tuple(int(item) for item in active_list.get("duplicates", [])),
                                tuple(int(item) for item in active_list.get("missing", [])),
                                tuple(int(item) for item in active_list.get("unexpected", [])),
                            )
                            active_mismatch_streak = (
                                active_mismatch_streak + 1
                                if signature == active_mismatch_signature else 1
                            )
                            active_mismatch_signature = signature
                            record_event({
                                "kind": "active_list_mismatch",
                                "tick": tick,
                                "streak": active_mismatch_streak,
                                "duplicates": list(signature[0]),
                                "missing": list(signature[1]),
                                "unexpected": list(signature[2]),
                            })
                            if active_mismatch_streak >= 2:
                                status, reason = (
                                    "ACTIVE_LIST_MISMATCH_PARTIAL",
                                    "same stock active-list mismatch persisted across two samples",
                                )
                    for slot, old_id in previous_by_slot.items():
                        if slot not in current_by_slot:
                            record_event({"kind": "identity_disappeared", "slot": slot,
                                          "previous_full_id": old_id,
                                          "death_status": "NOT_OBSERVED"})
                        elif current_by_slot[slot] != old_id:
                            record_event({"kind": "same_slot_identity_changed", "slot": slot,
                                          "previous_full_id": old_id,
                                          "current_full_id": current_by_slot[slot],
                                          "reuse_claimed": False,
                                          "death_status": "NOT_OBSERVED"})
                    record = {
                        "schema": "syw2plus.g2.stock_24k_observation_sample.v1",
                        "sample": samples + 1,
                        "elapsed_wall_seconds": round(monotonic() - started, 3),
                        "tick_bracket": {"before": tick_before, "snapshot": tick,
                                         "after": tick_after,
                                         "ps_before": ps_before, "ps_after": ps_after,
                                         "crossed_ticks": tick_before != tick_after,
                                         "atomic_ledger_proof": False},
                        "tick_delta_from_loaded": tick - first_tick,
                        "process": process,
                        "snapshot": full,
                        "active_list": active_list,
                    }
                    stream.write(json.dumps(record, ensure_ascii=False) + "\n")
                    stream.flush()
                    samples += 1
                    previous_by_slot, previous_tick, last_tick = current_by_slot, tick, tick
                    post_read = monotonic()
                    if post_read < previous_wall:
                        status, reason = "INVALID_CLOCK_PARTIAL", "monotonic clock moved backwards after read"
                    elif post_read > deadline:
                        status, reason = "TIMEOUT_PARTIAL", "reader returned after the 45-minute wall ceiling"
                    else:
                        previous_wall = post_read
                    if status == "OBSERVING" and tick - first_tick >= target_ticks:
                        status, reason = "PASS_DURATION_MILESTONE", "24000 original ticks observed after load"
                    if status != "OBSERVING":
                        break
                except Exception as exc:
                    errors.append({"sample": samples + 1, "error": f"{type(exc).__name__}: {exc}"})
                    status, reason = "READ_ERROR_PARTIAL", str(exc)
                    break
                next_sample += sample_seconds
                if next_sample <= monotonic():
                    next_sample = monotonic() + sample_seconds
    finally:
        summary.update({
            "status": status, "reason": reason, "samples": samples,
            "first_tick": first_tick, "last_tick": last_tick,
            "attained_tick_delta": (last_tick - first_tick)
            if isinstance(first_tick, int) and isinstance(last_tick, int) else None,
            "elapsed_wall_seconds": round(max(0.0, monotonic() - started), 3),
            "event_count": event_count, "events_truncated": event_count > len(events),
            "events": events, "errors": errors,
            "death_reuse": "NOT_OBSERVED" if not any(
                event.get("kind") == "same_slot_identity_changed" for event in events
            ) else "IDENTITY_REUSE_OBSERVED_DEATH_UNPROVEN",
            "product_pass_claim": False,
            "limitations": [
                "streamed process_vm/state snapshots are tick-bracketed, not atomic",
                "occupancy/dead-object distinction reflects the approved reader, not a full existence-table proof",
                "no death->reuse causality, save, LAN, economy, or product PASS claim",
                "PSS/RSS/process samples are not game heap or 32-bit OOM proof",
            ],
        })
        _write_json(summary_path, summary)
    return summary


def _g2_stock_active_list_snapshot(
    read_memory: Callable[[int, int], bytes],
) -> dict[str, Any]:
    """Read the stock active list and compare it with the stock existence table."""
    active_count = struct.unpack("<H", read_memory(0x00975908, 2))[0]
    if active_count > 1200:
        raise RuntimeSafetyError("stock active-list count exceeded 1200")
    active = list(struct.unpack(
        f"<{active_count}H", read_memory(0x00974FA8, active_count * 2)
    )) if active_count else []
    exists = struct.unpack("<1200H", read_memory(0x008990C8, 2400))
    existence_slots = {slot for slot, value in enumerate(exists) if value}
    active_slots = set(active)
    counts = collections.Counter(active)
    duplicates = sorted(slot for slot, count in counts.items() if count > 1)
    missing = sorted(existence_slots - active_slots)
    unexpected = sorted(active_slots - existence_slots)
    return {
        "active_count": active_count,
        "active_unique": len(active_slots),
        "existence_count": len(existence_slots),
        "duplicates": duplicates,
        "missing": missing,
        "unexpected": unexpected,
        "exact_set_match": (
            active_count == len(active_slots) == len(existence_slots)
            and not missing and not unexpected
        ),
    }



def _g2_stock_24k_load_file_pins(game: Path, expected_path: Path) -> dict[str, Any]:
    """Fail closed on the approved save/witness bytes before a new G2 run."""
    expected_path = _real(expected_path)
    if (not expected_path.is_absolute() or expected_path.is_symlink()
            or not expected_path.is_file()
            or _sha256(expected_path).lower() != G2_STOCK_24K_WITNESS_SHA256):
        raise RuntimeSafetyError("G2 24k observer requires the pinned fresh-load witness JSON")
    try:
        expected = json.loads(expected_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise RuntimeSafetyError("G2 24k observer witness JSON is unreadable") from exc
    if not isinstance(expected, Mapping) or expected.get("save_sha256", expected.get("sha256")) != G2_STOCK_24K_SAVE_SHA256:
        raise RuntimeSafetyError("G2 24k observer witness does not pin the approved save bytes")
    save_path = game / "save" / "save001.dat"
    if (save_path.is_symlink() or not save_path.is_file()
            or _sha256(save_path).lower() != G2_STOCK_24K_SAVE_SHA256):
        raise RuntimeSafetyError("G2 24k observer requires the pinned private save copy")
    return {
        "witness_sha256": G2_STOCK_24K_WITNESS_SHA256,
        "save_sha256": G2_STOCK_24K_SAVE_SHA256,
        "witness_path": str(expected_path),
        "save_path": str(save_path),
    }


def _g2_stock_24k_dispatch_after_load(
    *, requested: bool, load_result: Mapping[str, Any] | None,
    invoke: Callable[[], Mapping[str, Any]],
) -> dict[str, Any]:
    """Dispatch exactly once only after the pinned native load boundary passes."""
    if not requested:
        return {"status": "DISABLED", "collector_calls": 0,
                "post_load_actions": {"ui": 0, "bridge": 0, "input": 0}}
    valid = (
        isinstance(load_result, Mapping)
        and load_result.get("status") == "PASS"
        and load_result.get("pass") is True
        and load_result.get("classification") == "G2_STOCK_FRESH_LOAD_BOUNDARY_PASS"
        and load_result.get("save_sha256") == G2_STOCK_24K_SAVE_SHA256
        and load_result.get("witness_sha256") == G2_STOCK_24K_WITNESS_SHA256
    )
    if not valid:
        return {
            "status": "SKIPPED_LOAD_NOT_PASS", "collector_calls": 0,
            "reason": "pinned fresh-load boundary did not pass",
            "post_load_actions": {"ui": 0, "bridge": 0, "input": 0},
        }
    observation = invoke()
    return {
        "status": "COLLECTOR_INVOKED", "collector_calls": 1,
        "observation": dict(observation),
        "post_load_actions": {"ui": 0, "bridge": 0, "input": 0},
    }


def _g2_lifecycle_phase(
    prefix: Path, game: Path, output: Path, state: Callable[[bool], dict[str, Any]],
    read_memory: Callable[[int, int], bytes], *, mode: str, slot: int,
    expected_path: Path | None = None,
) -> dict[str, Any]:
    """Run exactly one native op2/op3 in an already-running G2 PS3 process."""
    started = time.monotonic()
    result: dict[str, Any] = {
        "status": "BLOCKED", "pass": False, "mode": mode, "slot": slot,
        "native_calls": 0, "memory_writes": False, "normalization_performed": False,
    }
    lifecycle_dir = output / f"g2_lifecycle_{mode}"
    save_path = game / "save" / f"save{slot:03d}.dat"

    def pending_witness(snapshot: Mapping[str, Any]) -> dict[str, Any] | None:
        players = snapshot.get("players")
        units = snapshot.get("units")
        if not isinstance(players, list) or not isinstance(units, list):
            return None
        owner4 = next((item for item in players
                       if isinstance(item, Mapping) and item.get("owner") == 4), None)
        hq = next((item for item in units
                   if isinstance(item, Mapping) and item.get("owner") == 4
                   and item.get("type") == 49 and item.get("hp", 0) > 0), None)
        tick = snapshot.get("tick")
        if (owner4 is None or hq is None or owner4.get("reserved") != 10
                or hq.get("command") != 15 or hq.get("production_type") != 7
                or hq.get("progress") != 100 or not isinstance(tick, int)):
            return None
        return {
            "owner": 4, "internal_id": hq.get("internal_id"), "slot": hq.get("slot"),
            "type": 49, "command": 15, "production_type": 7, "progress": 100,
            "reserved": 10, "stable_tick": True, "tick_before": tick, "tick_after": tick,
        }

    def provenance(raw: dict[str, Any]) -> dict[str, Any]:
        raw["provenance"] = {
            "bridge_sha256": G2_APPROVED_BRIDGE_SHA256,
            "caller": "0x42334C",
            "thread_check": "window_thread_equals_current_thread",
        }
        return raw

    try:
        if mode == "save":
            if lifecycle_dir.exists() or save_path.exists() or save_path.is_symlink():
                result["reason"] = "save slot is not previously absent"
            else:
                stock = state(True)
                pending_before = pending_witness(stock)
                pending_after = pending_witness(state(True))
                if pending_before is None or pending_after is None \
                        or pending_before["internal_id"] != pending_after["internal_id"]:
                    result["reason"] = "owner4 pending HQ gate failed before op2"
                elif (preflight_reason := _g2_lifecycle_stock_preflight(
                        stock, read_memory, pending_before)) is not None:
                    result["reason"] = preflight_reason
                else:
                    pending_before["tick_after"] = pending_after["tick_after"]
                    raw = provenance(_g2_lifecycle_native_op(
                        prefix, op=2, owner=0, slot=slot, timeout=30.0,
                    ))
                    result["native_calls"] = 1
                    if (not save_path.is_file() or save_path.is_symlink()
                            or save_path.stat().st_size <= 0):
                        result["reason"] = "native op2 did not create a fresh save file"
                    else:
                        result = _g2_stock_lifecycle_validator(
                            "save", stock_snapshot=stock, read_memory=read_memory,
                            native_result=raw, save_path=save_path, save_slot=slot,
                            save_previously_absent=True,
                            expected_save_sha256=_sha256(save_path),
                            pending_witness=pending_before, output=lifecycle_dir,
                        )
        elif mode == "load":
            if expected_path is None or expected_path.is_symlink() or not expected_path.is_file():
                result["reason"] = "load expected witness path is missing or linked"
            else:
                expected = json.loads(expected_path.read_text(encoding="utf-8"))
                expected_stock = expected.get("stock_snapshot") if isinstance(expected, Mapping) else None
                expected_pending = expected.get("pending_witness") if isinstance(expected, Mapping) else None
                expected_hash = (expected.get("save_sha256", expected.get("sha256"))
                                 if isinstance(expected, Mapping) else None)
                if (not isinstance(expected_stock, Mapping) or not isinstance(expected_pending, Mapping)
                        or not isinstance(expected_hash, str) or not save_path.is_file()
                        or save_path.is_symlink() or save_path.stat().st_size <= 0
                        or _sha256(save_path).lower() != expected_hash.lower()):
                    result["reason"] = "expected save witness/private save copy mismatch"
                else:
                    fresh = state(True)
                    units = fresh.get("units")
                    players = fresh.get("players")
                    by_owner = {owner: [unit for unit in units if unit.get("owner") == owner]
                                for owner in range(8)} if isinstance(units, list) else {}
                    fresh_gate = (fresh.get("ps") == 3 and isinstance(players, list)
                                  and isinstance(units, list)
                                  and len(units) == 16
                                  and all(len(by_owner.get(owner, [])) == 2
                                          and any(unit.get("type") == 49 for unit in by_owner[owner])
                                          and any(unit.get("type") == 7 for unit in by_owner[owner])
                                          for owner in range(8)))
                    if not fresh_gate:
                        result["reason"] = "fresh PS3 eight-owner HQ49/worker7 gate failed before op3"
                    else:
                        raw = provenance(_g2_lifecycle_native_op(
                            prefix, op=3, owner=0, slot=slot, timeout=30.0,
                        ))
                        result["native_calls"] = 1
                        loaded = state(True)
                        result = _g2_stock_lifecycle_validator(
                            "load", stock_snapshot=expected_stock, read_memory=read_memory,
                            native_result=raw, save_path=save_path, save_slot=slot,
                            save_previously_absent=True, expected_save_sha256=expected_hash,
                            pending_witness=expected_pending, fresh_snapshot=fresh,
                            loaded_snapshot=loaded, loaded_save_path=save_path,
                            output=lifecycle_dir,
                        )
        else:
            result["reason"] = "lifecycle mode must be exactly save or load"
    except (OSError, ValueError, RuntimeSafetyError, TypeError, struct.error) as exc:
        result["reason"] = str(exc)
    result["elapsed_seconds"] = round(time.monotonic() - started, 3)
    if lifecycle_dir.is_dir():
        _write_json(lifecycle_dir / "g2_stock_lifecycle.json", result)
    return result


def g1_baseline(
    manifest_path: Path,
    *,
    screen: str = "1600x1200x24",
    timeout: float = 90,
    g4_sample_seconds: float = 0,
    g4_sample_period: float = 2.0,
    g4_chain_goal: str | None = None,
    g4_candidate_exe: str | None = None,
    g4_intervention_goal: str | None = None,
    g4_intervention_delay: float = 0,
    g2_artifact_output: Path | None = None,
    g2_stock_stress: bool = False,
    g2_stock_lifecycle: str | None = None,
    g2_lifecycle_slot: int = 1,
    g2_lifecycle_expected: Path | None = None,
    g2_relocation_diag_build: Path | None = None,
    g2_stock_24k_observation: bool = False,
) -> dict[str, Any]:
    """Collect the no-patch G1-A boundary evidence in one fresh private run."""
    if timeout <= 0 or timeout > 90:
        raise RuntimeSafetyError("g1-baseline timeout must be between 1 and 90 seconds")
    if screen != "1600x1200x24":
        raise RuntimeSafetyError("g1-baseline requires the fixed 1600x1200x24 screen")
    if g4_sample_seconds < 0 or g4_sample_seconds > 300:
        raise RuntimeSafetyError("g1-baseline G4 sampling must be between 0 and 300 seconds")
    if g4_sample_period < 0.05 or g4_sample_period > 2.0:
        raise RuntimeSafetyError("g1-baseline G4 sample period must be between 0.05 and 2 seconds")
    g2_mode = g4_chain_goal == G2_CREATION_GOAL
    g2_relocation_mode = g2_relocation_diag_build is not None
    if g2_stock_24k_observation:
        if not g2_mode or g2_stock_lifecycle != "load" or g2_lifecycle_slot != 1:
            raise RuntimeSafetyError("G2 24k observation requires the exact slot-1 fresh-load lifecycle")
        if g2_stock_stress or g2_relocation_mode or g4_sample_seconds or g4_intervention_goal is not None or g4_intervention_delay:
            raise RuntimeSafetyError("G2 24k observation forbids stress, relocation, intervention, and G4 sampling")
    if g2_stock_stress and not g2_mode:
        raise RuntimeSafetyError("G2 stock stress requires the exact G2 creation goal")
    if g2_stock_stress and (g4_intervention_goal is not None or g4_intervention_delay):
        raise RuntimeSafetyError("G2 stock stress cannot be mixed with G4 interventions")
    if g2_stock_lifecycle is not None and g2_stock_lifecycle not in G2_LIFECYCLE_MODES:
        raise RuntimeSafetyError("G2 stock lifecycle mode must be exactly save or load")
    if g2_stock_lifecycle is not None and not g2_mode:
        raise RuntimeSafetyError("G2 stock lifecycle requires the exact G2 creation goal")
    if g2_stock_lifecycle is not None and (g4_intervention_goal is not None or g4_intervention_delay):
        raise RuntimeSafetyError("G2 stock lifecycle cannot be mixed with G4 interventions")
    if g2_stock_lifecycle == "save" and not g2_stock_stress:
        raise RuntimeSafetyError("G2 stock save lifecycle requires stock stress")
    if g2_stock_lifecycle == "load" and g2_stock_stress:
        raise RuntimeSafetyError("G2 fresh-load lifecycle requires stock stress disabled")
    if g2_stock_lifecycle is not None and not (1 <= g2_lifecycle_slot < 100):
        raise RuntimeSafetyError("G2 lifecycle slot must be between 1 and 99")
    if g2_stock_lifecycle == "save" and g2_lifecycle_expected is not None:
        raise RuntimeSafetyError("G2 save lifecycle does not accept an expected load witness")
    if g2_stock_lifecycle == "load":
        if g2_lifecycle_expected is None or not g2_lifecycle_expected.is_absolute():
            raise RuntimeSafetyError("G2 load lifecycle requires an absolute expected witness path")
        expected_real = _real(g2_lifecycle_expected)
        if (not _under(expected_real, _real(G2_ARTIFACT_ROOT))
                or g2_lifecycle_expected.is_symlink() or not expected_real.is_file()):
                raise RuntimeSafetyError("G2 load expected witness must be an external approved file")
    if g2_relocation_mode:
        if not g2_mode:
            raise RuntimeSafetyError("G2 relocation diagnostic requires the exact G2 creation goal")
        if g2_stock_stress or g2_stock_lifecycle is not None:
            raise RuntimeSafetyError("G2 relocation diagnostic cannot be mixed with stock stress/lifecycle")
        if g4_intervention_goal is not None or g4_intervention_delay:
            raise RuntimeSafetyError("G2 relocation diagnostic cannot be mixed with G4 interventions")
        if g4_sample_seconds:
            raise RuntimeSafetyError("G2 relocation diagnostic suppresses normal sampling")
    if g4_chain_goal is not None and not g2_mode and g4_chain_goal not in G4_FIXED_CHAIN_GOALS:
        raise RuntimeSafetyError("g1-baseline G4 chain goal is not an approved fixed-seed goal")
    if g4_chain_goal is not None and not g4_sample_seconds and not g2_relocation_mode and not g2_stock_24k_observation:
        raise RuntimeSafetyError("g1-baseline G4 chain goal requires G4 sampling")
    if g4_candidate_exe is not None and not g2_mode and g4_candidate_exe not in G4_CANDIDATE_EXES:
        raise RuntimeSafetyError("g1-baseline G4 candidate executable is not approved")
    if g4_candidate_exe is not None and (g4_chain_goal is None or (not g4_sample_seconds and not g2_relocation_mode and not g2_stock_24k_observation)):
        raise RuntimeSafetyError("g1-baseline G4 candidate requires fixed-seed sampling")
    if g4_intervention_goal is not None and g4_intervention_goal not in G4_INTERVENTION_GOALS:
        raise RuntimeSafetyError("g1-baseline G4 intervention goal is not approved")
    if g4_intervention_goal is not None and (g4_chain_goal is None or not g4_sample_seconds):
        raise RuntimeSafetyError("g1-baseline G4 intervention requires fixed-seed sampling")
    if g4_intervention_goal is not None and not (0 <= g4_intervention_delay < g4_sample_seconds):
        raise RuntimeSafetyError("g1-baseline G4 intervention delay must be inside the sample window")
    if g4_intervention_goal is None and g4_intervention_delay:
        raise RuntimeSafetyError("g1-baseline G4 intervention delay requires an intervention goal")
    if g2_mode and g4_candidate_exe != G2_CREATION_CANDIDATE:
        raise RuntimeSafetyError("G2 creation requires the approved fixed-supply candidate")
    if not g2_mode and g2_artifact_output is not None:
        raise RuntimeSafetyError("G2 artifact output is only valid for the G2 creation goal")
    if g2_mode:
        if not g2_relocation_mode and not g2_stock_24k_observation and not 10 <= g4_sample_seconds <= 20:
            raise RuntimeSafetyError("G2 creation sampling must be between 10 and 20 seconds")
        if g2_artifact_output is None:
            raise RuntimeSafetyError("G2 creation requires an external artifact output directory")
        if not g2_artifact_output.is_absolute():
            raise RuntimeSafetyError("G2 artifact output must be an absolute path")
        artifact_output = _real(g2_artifact_output)
        _reject_path_links(artifact_output)
        if artifact_output == _real(G2_ARTIFACT_ROOT) or not _under(artifact_output, G2_ARTIFACT_ROOT):
            raise RuntimeSafetyError("G2 artifact output must be a fresh absolute directory under the approved temp root")
        if artifact_output.exists():
            raise RuntimeSafetyError("G2 artifact output directory must not already exist")
    else:
        artifact_output = None
    checked = check_runtime(manifest_path)
    data, game, prefix, output = _manifest(manifest_path)
    manifest_output = output
    relocation_build: dict[str, Any] | None = None
    g2_family_mode = False
    if g2_relocation_mode:
        assert g2_relocation_diag_build is not None
        relocation_build = _g2_relocation_diag_build_manifest(g2_relocation_diag_build, game=game)
        g2_family_mode = relocation_build["mode"] == G2_FAMILY_ACCESSOR_MODE
    if g2_mode:
        game_data = data.get("game")
        recorded_support = game_data.get("support_dll_sha256") if isinstance(game_data, dict) else None
        bridge = game / "_inmm.dll"
        if g2_relocation_mode:
            expected_bridge = (G2_FAMILY_ACCESSOR_BRIDGE_SHA256 if g2_family_mode
                               else G2_RELOCATION_DIAG_BRIDGE_SHA256)
            if (expected_bridge is None or not isinstance(recorded_support, dict)
                    or recorded_support.get("_inmm.dll") != expected_bridge):
                raise RuntimeSafetyError("G2 relocation diagnostic bridge manifest hash is not approved")
        else:
            expected_bridge = G2_APPROVED_BRIDGE_SHA256
            if not isinstance(recorded_support, dict) or recorded_support.get("_inmm.dll") != G2_APPROVED_BRIDGE_SHA256:
                raise RuntimeSafetyError("G2 creation requires the approved diagnostic bridge manifest hash")
            if not bridge.is_file() or bridge.is_symlink() or _sha256(bridge) != G2_APPROVED_BRIDGE_SHA256:
                raise RuntimeSafetyError("G2 creation requires the approved diagnostic bridge file hash")
        if g2_relocation_mode and (not bridge.is_file() or bridge.is_symlink() or _sha256(bridge) != expected_bridge):
            raise RuntimeSafetyError("G2 creation requires the approved diagnostic bridge file hash")
    g2_stock_24k_file_pins: dict[str, Any] | None = None
    if g2_stock_24k_observation:
        assert g2_lifecycle_expected is not None
        g2_stock_24k_file_pins = _g2_stock_24k_load_file_pins(game, g2_lifecycle_expected)
    launch_exe = game / ORIGINAL_EXE
    if g4_candidate_exe is not None:
        if str(REPO_ROOT) not in sys.path:
            sys.path.insert(0, str(REPO_ROOT))
        if g2_mode:
            from patches.population.fixed_supply_5000 import patched_bytes
            launch_exe = game / G2_CREATION_CANDIDATE
            expected_candidate = patched_bytes((game / ORIGINAL_EXE).read_bytes())
            if launch_exe.is_symlink() or not launch_exe.is_file() or launch_exe.read_bytes() != expected_candidate:
                raise RuntimeSafetyError("G2 candidate executable bytes do not match fixed_supply_5000.patched_bytes")
        elif g4_candidate_exe == "g4_controller_cadence_50.exe":
            from patches.ai.controller_cadence_probe import patched_bytes
        elif g4_candidate_exe == "g4_production_crowd_cap_14.exe":
            from patches.ai.g4_production_crowd_cap_v1 import patched_bytes
        else:
            from patches.ai.gather_cooldown_probe import patched_bytes

        launch_exe = game / g4_candidate_exe
        if launch_exe.is_symlink() or not launch_exe.is_file():
            raise RuntimeSafetyError("approved G4 candidate executable is missing/linked")
        expected_candidate = patched_bytes((game / ORIGINAL_EXE).read_bytes())
        if launch_exe.read_bytes() != expected_candidate:
            raise RuntimeSafetyError(
                "G2 candidate executable bytes do not match fixed_supply_5000.patched_bytes"
                if g2_mode else "approved G4 candidate executable bytes do not match"
            )
    if g2_relocation_mode:
        game_data = data.get("game")
        actual_support = game_data.get("support_dll_sha256") if isinstance(game_data, dict) else None
        private_bridge = game / "_inmm.dll"
        expected_bridge = (G2_FAMILY_ACCESSOR_BRIDGE_SHA256 if g2_family_mode
                           else G2_RELOCATION_DIAG_BRIDGE_SHA256)
        if (not isinstance(actual_support, dict)
                or actual_support.get("_inmm.dll") != expected_bridge
                or not private_bridge.is_file() or _sha256(private_bridge) != expected_bridge):
            raise RuntimeSafetyError("private game copy does not contain the reviewed relocation diagnostic DLL")
    if g2_mode:
        assert artifact_output is not None
        artifact_output.mkdir(parents=True)
        output = artifact_output
    wine_data = data.get("wine")
    if not isinstance(wine_data, dict) or wine_data.get("created_new") is not True:
        raise RuntimeSafetyError("g1-baseline requires a newly prepared manifest")
    if _prefix_pids(prefix) or _existing_state(prefix) or (output / "g1_a").exists():
        raise RuntimeSafetyError("g1-baseline requires an unused private prefix and output")
    g1_dir = output / "g1_a"
    g1_dir.mkdir()
    run_id = _real(manifest_path).parent.name
    started = time.monotonic()
    wall_started = started
    log_path = output / "g1-baseline.log"
    log = log_path.open("a", encoding="utf-8")
    env = dict(os.environ, WINEPREFIX=str(prefix), WINEARCH="win32", WINEDEBUG="-all",
               LANG="ko_KR.UTF-8", LC_ALL="ko_KR.UTF-8", WINEDLLOVERRIDES="ddraw=b")
    if g2_stock_stress or g2_stock_lifecycle is not None:
        env["SYW2_SUPPLY_PROBE"] = "1"
    if g2_relocation_mode:
        env["SYW2_SUPPLY_PROBE"] = "1"
        env["SYW2_G2_RELOCATION_DIAG"] = "1"
    children: list[subprocess.Popen[Any]] = []
    screenshots: list[dict[str, Any]] = []
    inputs: list[dict[str, Any]] = []
    evidence: dict[str, Any] = {"manifest": checked, "screen": screen, "timeout_seconds": timeout,
                               "screenshots": screenshots,
                               "stock_24k_observation_requested": g2_stock_24k_observation,
                               "fixture": {
                                   "kind": "new private copy; default two-player random game",
                                   "synthetic": False, "memory_writes": False,
                                   "control_bridge": False, "resource_grant": False,
                               }}
    if g2_mode:
        evidence["g2_runtime"] = {
            "goal": G2_CREATION_GOAL,
            "candidate": G2_CREATION_CANDIDATE,
            "approved_bridge_sha256": (
                (G2_FAMILY_ACCESSOR_BRIDGE_SHA256 if g2_family_mode
                 else G2_RELOCATION_DIAG_BRIDGE_SHA256)
                if g2_relocation_mode else G2_APPROVED_BRIDGE_SHA256
            ),
            "artifact_output": str(output),
            "manifest_output_preserved": str(manifest_output),
            "stock_stress_requested": g2_stock_stress,
            "lifecycle_mode": g2_stock_lifecycle,
            "lifecycle_slot": g2_lifecycle_slot,
            "lifecycle_expected": str(g2_lifecycle_expected) if g2_lifecycle_expected is not None else None,
            "relocation_diagnostic_requested": g2_relocation_mode,
            "family_accessor_requested": g2_family_mode,
            "relocation_diagnostic_build": relocation_build,
            "product_pass_claim": False,
        }
    error: str | None = None
    cleanup: dict[str, Any] = {}
    content_crop: tuple[int, int, int, int] | None = None
    display = ""
    proc: subprocess.Popen[Any] | None = None
    input_phase_metrics: dict[str, Any] = {"items": {}}
    input_phase_started: float | None = None
    observation_mode = False
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
        proc = subprocess.Popen(["wine", str(launch_exe)], cwd=game, env=env,
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
        evidence["modules"] = _module_evidence(proc.pid, launch_exe.name)
        def read_for_process(address: int, size: int) -> bytes:
            return read(proc.pid, address, size)  # type: ignore[union-attr]
        surface9 = _read_surface(read_for_process, 9)
        evidence["surface_ps9"] = surface9
        if g4_candidate_exe is not None:
            evidence["candidate"] = {
                "name": g4_candidate_exe,
                "sha256": _sha256(launch_exe),
                "probe": ("fixed_supply_5000.patched_bytes; approved G2 creation candidate"
                          if g2_mode else G4_CANDIDATE_EXES[g4_candidate_exe]),
                "release_patch": False,
            }

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

        if g4_chain_goal is not None:
            chain_result = _g4_send_control_goal(
                prefix, g4_chain_goal, min(30.0, _remaining(started, timeout))
            )
            if chain_result.get("ok") is not True:
                raise RuntimeSafetyError(
                    f"G4 fixed-seed chain failed: {chain_result.get('reason', 'unknown')}"
                )
            scene_state = _wait_state(
                state,
                lambda item: item.get("ps") == 3
                and isinstance(item.get("tick"), int)
                and item["tick"] > 0,
                started, timeout, "G4 fixed-seed chain did not reach PS=3",
            )
            scene_png = capture_neutral("scene_after_g4_fixed_seed_chain")
            evidence["fixture"].update({
                "kind": (f"diagnostic eight-owner original creation chain: {g4_chain_goal}"
                          if g2_mode else f"diagnostic fixed-seed chain: {g4_chain_goal}"),
                "synthetic": True,
                "memory_writes": True,
                "control_bridge": True,
            })
            inputs.append({
                "tag": "g4_fixed_seed_chain_setup",
                "content": None,
                "x11": None,
                "before": {"ps": state7.get("ps")},
                "expected": "approved fixed-seed bridge reaches PS3 with tick>0",
                "after": {"ps": scene_state.get("ps"), "tick": scene_state.get("tick"),
                          "screenshot": scene_png},
                "actual": f"goal={g4_chain_goal}; result={chain_result.get('reason')}; "
                          f"PS={scene_state.get('ps')}; tick={scene_state.get('tick')}",
                "result": "PASS",
            })
            flush_input_stage()
            scene_map = (f"diagnostic eight-owner creation map: {g4_chain_goal}"
                         if g2_mode else f"diagnostic fixed-seed two-player random game: {g4_chain_goal}")
            scene_seed_observed = True
            scene_synthetic = True
        else:
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
            scene_map = "default two-player random game; map name/seed not exposed by approved read-only offsets"
            scene_seed_observed = False
            scene_synthetic = False

        surface3 = _read_surface(read_for_process, 3)
        evidence["surface_ps3"] = surface3
        if not (surface9.get("values", [])[1:3] == [800, 600] and surface3.get("values", [])[1:3] == [800, 600]):
            raise RuntimeSafetyError("original 800x600 render surface was not observed at PS9 and PS3")

        players = scene_state.get("players", [])
        units = scene_state.get("units", [])
        if g2_mode:
            creation_gate = _g2_initial_creation_gate(scene_state, read_for_process)
            evidence["g2_eight_owner_creation"] = creation_gate
            if creation_gate.get("status") != "PASS":
                raise RuntimeSafetyError(
                    "G2 eight-owner creation gate failed: "
                    + "; ".join(str(item) for item in creation_gate.get("failures", []))
                )
            if g2_relocation_mode:
                # The native op may terminate the private game after publishing
                # the fixed raw artifact.  Do not read the old unit body, run
                # normal G1 UI, or attribute a consumer failure after arming.
                family_initial_identities: list[dict[str, int]] | None = None
                if g2_family_mode:
                    family_initial_identities = _g2_family_initial_identities(scene_state)
                    evidence["g2_family_initial_identities"] = family_initial_identities
                evidence["g2_relocation_diagnostic"] = (
                    _g2_family_accessor_native_op(
                        prefix, expected_identities=family_initial_identities,
                    ) if g2_family_mode else _g2_relocation_diag_native_op(prefix)
                )
                raise RuntimeSafetyError(
                    "relocation diagnostic completed; normal G1 tail suppressed"
                )
        else:
            active_counts = {owner: sum(1 for unit in units if isinstance(unit, dict) and unit.get("owner") == owner)
                             for owner in (0, 1)}
            nations = {owner: players[owner].get("nation") for owner in (0, 1)
                       if isinstance(players, list) and len(players) > owner and isinstance(players[owner], dict)}
            if any(active_counts[owner] < 1 for owner in (0, 1)) or any(not nations.get(owner) for owner in (0, 1)):
                raise RuntimeSafetyError("PS3 scene lacks active units and nonzero nations for owners 0 and 1")
        scene_snapshot = _g1_scene_snapshot(scene_state, read_for_process)
        scene_id = _json_fingerprint({"state": scene_state, "title": state9, "fixture": evidence["fixture"]})
        evidence["scene"] = {"ps": scene_state.get("ps"), "tick": scene_state.get("tick"),
                              "map": scene_map,
                              "reproduction_identifier": {"kind": "same-run state fingerprint", "value": scene_id,
                                                            "replay_seed_observed": scene_seed_observed},
                              "owners": scene_snapshot["owners"],
                              "unit_slots": scene_snapshot["unit_slots"],
                              "owner0_hq_world": scene_snapshot["owner0_hq_world"],
                              "owner0_hq_candidates": scene_snapshot["owner0_hq_candidates"],
                              "owner0_hq_type": scene_snapshot["owner0_hq_type"],
                              "world_bounds": scene_snapshot["world_bounds"],
                              "camera": scene_snapshot["camera"], "synthetic": scene_synthetic}
        flush_input_stage()

        if g2_stock_stress:
            stress_started = time.monotonic()
            try:
                evidence["g2_stock_stress"] = _g2_stock_stress_phase(
                    prefix, output, state, read_for_process, max_seconds=300.0,
                )
            except Exception as exc:
                evidence["g2_stock_stress"] = {
                    "status": "UNKNOWN", "pass": False, "stop_reason": str(exc),
                    "phase_elapsed_seconds": time.monotonic() - stress_started,
                }
            finally:
                stress_elapsed = time.monotonic() - stress_started
                evidence["g2_stock_stress"]["phase_elapsed_seconds"] = round(stress_elapsed, 3)
                # This bounded stress phase is outside the startup/UI-tail
                # budget, matching the existing G4 observation-window rule.
                started += stress_elapsed
                flush_input_stage()

        if g2_stock_lifecycle is not None:
            lifecycle_started = time.monotonic()
            try:
                evidence["g2_stock_lifecycle"] = _g2_lifecycle_phase(
                    prefix, game, output, state, read_for_process,
                    mode=g2_stock_lifecycle, slot=g2_lifecycle_slot,
                    expected_path=g2_lifecycle_expected,
                )
            except (OSError, RuntimeSafetyError, ValueError, TypeError, struct.error) as exc:
                evidence["g2_stock_lifecycle"] = {
                    "status": "BLOCKED", "pass": False,
                    "mode": g2_stock_lifecycle, "slot": g2_lifecycle_slot,
                    "native_calls": 0, "reason": str(exc),
                }
            evidence["g2_stock_lifecycle"]["elapsed_seconds"] = round(
                time.monotonic() - lifecycle_started, 3
            )
            lifecycle_result = evidence["g2_stock_lifecycle"]
            if g2_stock_24k_file_pins is not None and isinstance(lifecycle_result, dict):
                lifecycle_result.update(g2_stock_24k_file_pins)
            if g2_stock_24k_observation:
                def owned_process_sample() -> dict[str, Any]:
                    owned = proc
                    return {"pid": owned.pid, "alive": owned.poll() is None} if owned is not None else {"pid": None, "alive": False}

                def invoke_stock_observer() -> Mapping[str, Any]:
                    return g2_stock_24k_observe(
                        output / "g2_stock_24k_observation", enabled=True,
                        goal=G2_CREATION_GOAL, candidate=G2_CREATION_CANDIDATE,
                        bridge_sha256=G2_APPROVED_BRIDGE_SHA256, lifecycle="load",
                        stock_stress=False, intervention_goal=None, intervention_delay=0,
                        relocation_diagnostic=False,
                        fresh_creation_gate=creation_gate,
                        load_result=lifecycle_result,
                        post_load_effects={
                            "ui_actions": 0, "input_actions": 0, "bridge_requests": 0,
                            "save_actions": 0, "stress_interventions": False,
                        },
                        snapshot_reader=lambda detailed: state(detailed),
                        light_reader=lambda: state(False),
                        process_reader=owned_process_sample,
                        active_list_reader=lambda: _g2_stock_active_list_snapshot(
                            read_for_process
                        ),
                    )

                dispatch = _g2_stock_24k_dispatch_after_load(
                    requested=True, load_result=lifecycle_result, invoke=invoke_stock_observer,
                )
                evidence["g2_stock_24k_observation"] = dispatch
                if dispatch.get("status") != "COLLECTOR_INVOKED":
                    raise RuntimeSafetyError("G2 24k observation requires a passing fresh-load boundary")
                observation_mode = True
            else:
                flush_input_stage()

        if g4_sample_seconds:
            samples: list[dict[str, Any]] = []
            sample_phase_started = time.monotonic()
            sample_deadline = sample_phase_started + g4_sample_seconds
            intervention_sent = False
            if g4_intervention_goal is not None:
                # Publish the request before its delay elapses so an
                # intervention failure cannot erase the already-collected
                # samples or the requested metadata in the outer error path.
                evidence["g4_intervention"] = {
                    "goal": g4_intervention_goal,
                    "requested_delay_seconds": g4_intervention_delay,
                    "status": "requested",
                    "result": None,
                }
            sampling_error: str | None = None
            try:
                while time.monotonic() < sample_deadline:
                    sample_elapsed = time.monotonic() - sample_phase_started
                    if (g4_intervention_goal is not None and not intervention_sent
                            and sample_elapsed >= g4_intervention_delay):
                        intervention = evidence["g4_intervention"]
                        intervention["elapsed_seconds"] = round(sample_elapsed, 3)
                        try:
                            intervention["result"] = _g4_send_control_goal(
                                prefix, g4_intervention_goal, 5,
                            )
                            intervention["status"] = "completed"
                        except (OSError, subprocess.SubprocessError, RuntimeSafetyError,
                                ValueError, struct.error) as exc:
                            intervention["status"] = "error"
                            intervention["error"] = str(exc)
                            raise
                        intervention_sent = True
                    observation = state(True)
                    samples.append({
                        "elapsed_seconds": round(g4_sample_seconds - max(0.0, sample_deadline - time.monotonic()), 3),
                        "ps": observation.get("ps"),
                        "tick": observation.get("tick"),
                        "players": observation.get("players", []),
                        "units": observation.get("units", []),
                    })
                    time.sleep(min(g4_sample_period, max(0.0, sample_deadline - time.monotonic())))
            except (OSError, subprocess.SubprocessError, RuntimeSafetyError,
                    ValueError, struct.error) as exc:
                sampling_error = str(exc)
                raise
            finally:
                evidence["g4_ai_smoke"] = {
                    "requested_seconds": g4_sample_seconds,
                    "requested_period": g4_sample_period,
                    "observational_only": True,
                    "samples": samples,
                    "summary": _g4_ai_metric_summary(samples),
                    "error": sampling_error,
                }
                # The general G1 safety budget excludes this explicitly
                # requested, bounded observation window. Startup/input waits
                # retain the original 90-second ceiling on all exits.
                started += time.monotonic() - sample_phase_started
                flush_input_stage()

        if observation_mode:
            evidence["post_load_tail_suppressed"] = {
                "status": "SUPPRESSED",
                "ui": 0, "bridge": 0, "input": 0,
                "reason": "bounded G2 24k observer owns the post-load window",
            }
        else:
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
        evidence["elapsed_seconds"] = round(time.monotonic() - wall_started, 3)
        # Keep the stage flush useful after teardown/errors as well: the final
        # evidence snapshot must contain the same diagnostic fields as output/.
        _write_json(g1_dir / "evidence.json", evidence)
        g4_shadow_provenance: dict[str, Any] = _g4_shadow_provenance(prefix, env)
        provenance = {"manifest_sha256": _sha256(_real(manifest_path)),
                      "original_exe_sha256": _sha256(game / ORIGINAL_EXE),
                      "expected_original_exe_sha256": ORIGINAL_SHA256,
                      "command": (
                          f"runtime_env.py g1-baseline --manifest {manifest_path} "
                          f"--screen {screen} --timeout {timeout}"
                          + (f" --g4-sample-seconds {g4_sample_seconds}" if g4_sample_seconds else "")
                          + (f" --g4-sample-period {g4_sample_period}" if g4_sample_period != 2.0 else "")
                          + (f" --g4-chain-goal {g4_chain_goal}" if g4_chain_goal else "")
                          + (f" --g4-candidate-exe {g4_candidate_exe}" if g4_candidate_exe else "")
                          + (f" --g4-intervention-goal {g4_intervention_goal}" if g4_intervention_goal else "")
                          + (f" --g4-intervention-delay {g4_intervention_delay}" if g4_intervention_goal else "")
                          + (f" --g2-artifact-output {artifact_output}" if g2_mode else "")
                          + (" --g2-stock-stress" if g2_stock_stress else "")
                          + (f" --g2-stock-lifecycle {g2_stock_lifecycle}" if g2_stock_lifecycle else "")
                          + (f" --g2-lifecycle-slot {g2_lifecycle_slot}" if g2_stock_lifecycle else "")
                          + (f" --g2-lifecycle-expected {g2_lifecycle_expected}" if g2_lifecycle_expected else "")
                          + (f" --g2-relocation-diag-build {g2_relocation_diag_build}" if g2_relocation_diag_build else "")
                          + (" --g2-stock-24k-observation" if g2_stock_24k_observation else "")
                      ),
                      "environment": {key: env.get(key) for key in ("DISPLAY", "WINEPREFIX", "WINEARCH", "LANG", "LC_ALL", "WINEDLLOVERRIDES", G4_AI_SHADOW_ENV)},
                      "g4_ai_shadow": g4_shadow_provenance,
                      "display": display, "prefix": str(prefix), "game_root": str(game),
                      "launched_exe": str(launch_exe), "launched_exe_sha256": _sha256(launch_exe),
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
                  "same_run_scene": "scene" in evidence,
                  "g4_shadow_provenance": (
                      not g4_shadow_provenance["enabled"]
                      or g4_shadow_provenance["pass"]
                  )}
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
    native_2x_blit: bool = False, native_2x_stretch: bool = False,
    ps3_dwell_seconds: float = 0.0,
    g1_input_sequence: bool = False,
) -> dict[str, Any]:
    """Run one opt-in DirectDraw provenance trace from PS9 through PS3."""
    if timeout <= 0 or timeout > 90:
        raise RuntimeSafetyError("g1-presentation-trace timeout must be between 1 and 90 seconds")
    if ps3_dwell_seconds < 0:
        raise RuntimeSafetyError("g1-presentation-trace PS3 dwell must not be negative")
    if g1_input_sequence and ps3_dwell_seconds > 0:
        raise RuntimeSafetyError("g1 input sequence and PS3 dwell cannot overlap")
    if native_2x_blit and dxwrapper_2x:
        raise RuntimeSafetyError("--native-2x-blit and --dxwrapper-2x are mutually exclusive")
    if native_2x_stretch and not native_2x_blit:
        raise RuntimeSafetyError("--native-2x-stretch requires --native-2x-blit")
    if native_2x_stretch and dxwrapper_2x:
        raise RuntimeSafetyError("--native-2x-stretch and --dxwrapper-2x are mutually exclusive")
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
    if native_2x_blit:
        env["SYW2_G1_NATIVE_2X_BLIT"] = "1"
    if native_2x_stretch:
        env["SYW2_G1_NATIVE_2X_STRETCH"] = "1"
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
        "native_2x_blit": {"enabled": native_2x_blit,
                            "environment": "SYW2_G1_NATIVE_2X_BLIT=1" if native_2x_blit else None},
        "native_2x_stretch": {"enabled": native_2x_stretch,
                               "environment": "SYW2_G1_NATIVE_2X_STRETCH=1" if native_2x_stretch else None},
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
            native_2x_stretch=native_2x_stretch,
            program_state_reader=lambda: state(False),
            screenshot_capture=capture_finalization,
        )
        if native_2x_stretch:
            evidence["native_split_contract"] = evidence["validator"]
        else:
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
        if native_2x_blit:
            command += " --native-2x-blit"
        if native_2x_stretch:
            command += " --native-2x-stretch"
        provenance = {"manifest_sha256": _sha256(_real(manifest_path)),
                      "original_exe_sha256": _sha256(game / ORIGINAL_EXE),
                      "expected_original_exe_sha256": ORIGINAL_SHA256,
                      "command": command,
                      "environment": {key: env.get(key) for key in ("DISPLAY", "WINEPREFIX", "WINEARCH", "LANG", "LC_ALL", "WINEDLOVERRIDES", "SYW2_G1_PRESENT_TRACE", "SYW2_G1_TRACE_RUN_ID", "SYW2_G1_NATIVE_2X_BLIT", "SYW2_G1_NATIVE_2X_STRETCH")},
                      "display": display, "prefix": str(prefix), "game_root": str(game),
                      "harness_sha256": {"tools/runtime_env.py": _sha256(Path(__file__))},
                      "diagnostic_bridge_sha256": game_data.get("diagnostic_bridge_sha256"),
                      "dxwrapper_config": evidence["dxwrapper_config"],
                      "observational_only": not (native_2x_blit or native_2x_stretch),
                      "intervention_scope": ([
                          "set_display_mode_exact_800x600x8_to_1600x1200x8",
                          "ps3_present_bltfast_to_blt_2x",
                      ] if native_2x_stretch else ([] if not native_2x_blit else [
                          "set_display_mode_exact_800x600x8_to_1600x1200x8"
                      ]))}
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
    g.add_argument("--g4-sample-seconds", type=float, default=0.0)
    g.add_argument("--g4-sample-period", type=float, default=2.0)
    g.add_argument("--g4-chain-goal", choices=sorted(set(G4_FIXED_CHAIN_GOALS) | {G2_CREATION_GOAL}))
    g.add_argument("--g4-candidate-exe", choices=sorted(set(G4_CANDIDATE_EXES) | {G2_CREATION_CANDIDATE}))
    g.add_argument("--g2-artifact-output", type=Path)
    g.add_argument("--g2-stock-stress", action="store_true")
    g.add_argument("--g2-stock-lifecycle", choices=G2_LIFECYCLE_MODES)
    g.add_argument("--g2-lifecycle-slot", type=int, default=1)
    g.add_argument("--g2-lifecycle-expected", type=Path)
    g.add_argument("--g2-relocation-diag-build", type=Path)
    g.add_argument("--g2-stock-24k-observation", action="store_true")
    g.add_argument("--g4-intervention-goal", choices=sorted(G4_INTERVENTION_GOALS))
    g.add_argument("--g4-intervention-delay", type=float, default=0.0)
    t = sub.add_parser("g1-presentation-trace")
    t.add_argument("--manifest", type=Path, required=True)
    t.add_argument("--screen", default="1600x1200x24")
    t.add_argument("--timeout", type=float, default=90)
    t.add_argument("--win32-close-helper", type=Path)
    t.add_argument("--dxwrapper-2x", action="store_true")
    t.add_argument("--native-2x-blit", action="store_true")
    t.add_argument("--native-2x-stretch", action="store_true")
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
    s1_original.add_argument("--minimap-probe", action="store_true")
    s1_original.add_argument("--deselect-probe", action="store_true")
    s1_original.add_argument("--ps35-screenshot", action="store_true")
    s1_original.add_argument("--drag-probe", action="store_true")
    s1_original.add_argument("--bridge", type=Path)
    s1_original.add_argument("--g4-exact-postload", action="store_true")
    s1_original.add_argument("--g4-load-fixture", choices=["save006.dat"])
    s1_candidate = sub.add_parser("g1-s1-candidate-load-evidence")
    s1_candidate.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    s1_candidate.add_argument("--runtime-root", type=Path, default=DEFAULT_RUNTIME_ROOT)
    s1_candidate.add_argument("--minimap-probe", action="store_true")
    s1_candidate.add_argument("--deselect-probe", action="store_true")
    s1_candidate.add_argument("--ps35-screenshot", action="store_true")
    s1_candidate.add_argument("--drag-probe", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            result = prepare(args.source, runtime_root=args.runtime_root, bridge=args.bridge, timeout=args.timeout)
        elif args.command == "check":
            result = check_runtime(args.manifest)
        elif args.command == "smoke":
            result = smoke(args.manifest, timeout=args.timeout)
        elif args.command == "g1-baseline":
            result = g1_baseline(
                args.manifest,
                screen=args.screen,
                timeout=args.timeout,
                g4_sample_seconds=args.g4_sample_seconds,
                g4_sample_period=args.g4_sample_period,
                g4_chain_goal=args.g4_chain_goal,
                g4_candidate_exe=args.g4_candidate_exe,
                g4_intervention_goal=args.g4_intervention_goal,
                g4_intervention_delay=args.g4_intervention_delay,
                g2_artifact_output=args.g2_artifact_output,
                g2_stock_stress=args.g2_stock_stress,
                g2_stock_lifecycle=args.g2_stock_lifecycle,
                g2_lifecycle_slot=args.g2_lifecycle_slot,
                g2_lifecycle_expected=args.g2_lifecycle_expected,
                g2_relocation_diag_build=args.g2_relocation_diag_build,
                g2_stock_24k_observation=args.g2_stock_24k_observation,
            )
        elif args.command == "g1-r1-load-origin":
            result = g1_r1_load_origin(args.manifest, screen=args.screen, timeout=args.timeout)
        elif args.command == "g1-r1-candidate-load-origin":
            result = g1_r1_candidate_load_origin(args.manifest, screen=args.screen, timeout=args.timeout)
        elif args.command == "g1-s1-original-load-evidence":
            load_kwargs: dict[str, Any] = {}
            if args.minimap_probe:
                load_kwargs["minimap_probe"] = True
            if args.deselect_probe:
                load_kwargs["deselect_probe"] = True
            if args.ps35_screenshot:
                load_kwargs["ps35_screenshot"] = True
            if args.drag_probe:
                load_kwargs["drag_probe"] = True
            if args.bridge is not None:
                load_kwargs["bridge"] = args.bridge
            if args.g4_exact_postload:
                load_kwargs["g4_exact_postload"] = True
            if args.g4_load_fixture is not None:
                load_kwargs["g4_load_fixture"] = args.g4_load_fixture
            result = g1_s1_original_load_evidence(
                args.source, runtime_root=args.runtime_root,
                **load_kwargs,
            )
        elif args.command == "g1-s1-candidate-load-evidence":
            candidate_load_kwargs: dict[str, Any] = {}
            if args.minimap_probe:
                candidate_load_kwargs["minimap_probe"] = True
            if args.deselect_probe:
                candidate_load_kwargs["deselect_probe"] = True
            if args.ps35_screenshot:
                candidate_load_kwargs["ps35_screenshot"] = True
            if args.drag_probe:
                candidate_load_kwargs["drag_probe"] = True
            result = g1_s1_original_load_evidence(
                args.source, runtime_root=args.runtime_root, dxwrapper_2x=True,
                **candidate_load_kwargs,
            )
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
                native_2x_blit=args.native_2x_blit,
                native_2x_stretch=args.native_2x_stretch,
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
    if args.command in {"g1-s1-original-load-evidence", "g1-s1-candidate-load-evidence"} and result.get("status") != "PASS":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(runtime_main())
