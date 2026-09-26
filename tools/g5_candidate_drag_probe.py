#!/usr/bin/env python3
"""Run one isolated G5 original/candidate drag and command probe.

The runtime is prepared and checked as an original first.  Only the private
copy inside that fresh run is then replaced with the pinned G5 candidate for a
candidate run; the protected source tree and the original runtime manifest are
never edited.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Callable, Mapping, cast

from patches.selection import g5_selection_cap50_v3 as g5
from tools import runtime_env
from patches.population.runtime_driver import read as read_memory
from patches.population.runtime_driver import state as read_state


REPO = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = runtime_env.DEFAULT_SOURCE
DEFAULT_RUNTIME_ROOT = REPO / "local" / "runtime" / "g5-lap632-candidate"
ORIGINAL_SHA = runtime_env.ORIGINAL_SHA256
# lap683 middle handoff: roundtrip must run against the v3 chunked-dispatch
# candidate (crash fix), not the v2 SHA the tool was pinned to through lap665.
TARGET_SHA = "e5004764e945350a0391d69035f8c8f0d305fcca7d6aaa54066836bac3de6977"
STOCK_SELECTION_BASE = 0x00899024
STOCK_SELECTION_CAPACITY = 20
SEED_TYPE = 2
VISIBLE_WORKER_SLOT = 1198
SEED_COUNT = 55
SELECTION_ENTRY_BYTES = 4
UNIT_BASE = 0x0066B790
UNIT_STRIDE = 0x758
UNIT_COMMAND_OFFSET = 0x290
UNIT_PENDING_COMMAND_OFFSET = 0x384
UNIT_PENDING_XY_OFFSET = 0x388
UNIT_PENDING_TARGET_UID_OFFSET = 0x38C
UNIT_X_OFFSET = 0x2A2
UNIT_Y_OFFSET = 0x2A4
UNIT_OWNER_OFFSET = 0x8E
UNIT_HP_OFFSET = 0xB4
UNIT_SELECTABLE_OFFSET = 0x31C
UNIT_GROUP_OFFSET = 0x344
DRAG_START = (200, 170)
DRAG_END = (730, 445)
# The minimap click leaves the worker two tiles inside the camera origin for
# every paired fixture observed so far.  Keep the target relative to that live
# worker rather than assuming a map-specific absolute coordinate.
ATTACK_TARGET_OFFSET = (7, -1)
# Keep the owner-1 fixture outside the worker-centered grid while keeping it
# above the command HUD.  Raw ``pending_xy`` proved that (548, 450) maps to
# worker-grid cell (47, 143), so it issued an attack-move with no target UID.
ATTACK_TARGET_SCREEN = (580, 450)
GROUP_CURRENT_ADDRESS = 0x0089312C
GROUP1_BASE_ADDRESS = 0x009570F4
GROUP1_COUNT_OFFSET = 0x338
GROUP1_FIRST_ID_OFFSET = 0x66
PAUSE_SAVE_POINT = (400, 238)
PAUSE_LOAD_POINT = (400, 272)
SAVE_SLOT_POINT = (340, 166)
SAVE_ACTION_POINT = (316, 372)
SAVE_MENU_RETURN_POINT = (464, 372)
RESUME_POINT = (400, 132)
DESELECT_POINT = (550, 400)


class ProbeError(RuntimeError):
    """A candidate contract or runtime observation failed closed."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def wait_for_selection_trace_gate(pid: int, artifact_root: Path) -> None:
    """Pause immediately before the drag until an external gdb trace is armed.

    The gate is opt-in so ordinary G5 probes retain their existing behavior.
    The trace process only reads game memory and configures hardware debug
    registers; the probe remains the sole owner of input and cleanup.
    """
    control_text = os.environ.get("G5_SELECTION_TRACE_CONTROL")
    if not control_text:
        return
    control = Path(control_text).expanduser().resolve()
    control.mkdir(parents=True, exist_ok=True)
    write_json(control / "game_pid.json", {
        "pid": pid,
        "artifact_root": str(artifact_root),
        "candidate_selection_base": hex(g5.SELECTION_BASE),
    })
    armed = control / "armed.json"
    ready = control / "probe_ready.json"
    proceed = control / "continue.flag"
    tick_ready = control / "tick_ready.json"
    write_json(control / "drag_gate.json", {
        "ready_for_external_trace": True,
        "pid": pid,
        "t": time.time(),
    })
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline and not armed.exists():
        time.sleep(0.05)
    if not armed.exists():
        raise ProbeError("selection trace did not arm before drag gate timeout")
    write_json(ready, {"ready": True, "pid": pid, "t": time.time()})
    # The return-slot trace must let the game run before input is injected.
    # This opt-in second gate is deliberately separate from ``continue.flag``
    # so an attach/continue race cannot make a paused game look like a drag
    # failure.
    required = tick_ready if os.environ.get("G5_SELECTION_TICK_GATE") else proceed
    while time.monotonic() < deadline and not required.exists():
        time.sleep(0.05)
    if not required.exists():
        raise ProbeError(f"selection trace gate missing before drag timeout: {required.name}")


def wait_for_ui_trace_gate(pid: int, artifact_root: Path) -> None:
    """Pause before Ctrl+1 while a read-only gdb return trace is attached."""
    control_text = os.environ.get("G5_UI_TRACE_CONTROL")
    if not control_text:
        return
    control = Path(control_text).expanduser().resolve()
    control.mkdir(parents=True, exist_ok=True)
    write_json(control / "game_pid.json", {
        "pid": pid,
        "artifact_root": str(artifact_root),
        "candidate_selection_base": hex(g5.SELECTION_BASE),
        "trace": "FUN_0040F7D0 return",
    })
    write_json(control / "ui_gate.json", {"ready_for_external_trace": True, "pid": pid, "t": time.time()})
    armed = control / "armed.json"
    proceed = control / "continue.flag"
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline and not armed.exists():
        time.sleep(0.05)
    if not armed.exists():
        raise ProbeError("UI trace did not arm before Ctrl+1 gate timeout")
    write_json(control / "probe_ready.json", {"ready": True, "pid": pid, "t": time.time()})
    while time.monotonic() < deadline and not proceed.exists():
        time.sleep(0.05)
    if not proceed.exists():
        raise ProbeError("UI trace did not continue before Ctrl+1 timeout")


class SupplyProbe:
    """Use the pre-existing stock-layout diagnostic fixture protocol."""

    def __init__(self, prefix: Path) -> None:
        self.request = prefix / "drive_c" / "supply_probe_request.txt"
        self.result = prefix / "drive_c" / "supply_probe_result.json"
        self.next_id = 1

    def call(self, *, op: int, owner: int, unit_type: int, x: int, y: int, count: int) -> dict[str, Any]:
        request_id = self.next_id
        self.next_id += 1
        self.request.write_text(
            f"{request_id} {op} {owner} 0 {unit_type} {x} {y} {count}\n",
            encoding="ascii",
        )
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            try:
                result = json.loads(self.result.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                time.sleep(0.05)
                continue
            if result.get("id") == request_id:
                return result
            time.sleep(0.05)
        raise ProbeError(f"supply fixture request timed out: id={request_id}")


def selection_snapshot(pid: int, *, base: int, capacity: int) -> dict[str, Any]:
    count = int.from_bytes(read_memory(pid, base, 4), "little", signed=True)
    if not 0 <= count <= capacity:
        raise ProbeError(f"candidate selection count outside 0..50: {count}")
    raw_entries = [
        int.from_bytes(
            read_memory(pid, base + 4 + index * SELECTION_ENTRY_BYTES, 4),
            "little",
            signed=False,
        )
        for index in range(count)
    ]
    slots = [entry & 0xFFF for entry in raw_entries]
    return {
        "count": count,
        "raw_entries": raw_entries,
        "slots": slots,
        "unique_slots": len(set(slots)),
        "encoding": "slot_low12_or_aux_high_bits",
    }


def fixture_units(pid: int) -> list[dict[str, Any]]:
    exists = read_memory(pid, 0x008990C8, 1200 * 2)
    rows: list[dict[str, Any]] = []
    for slot in range(1, 1200):
        if int.from_bytes(exists[slot * 2:slot * 2 + 2], "little", signed=False) == 0:
            continue
        base = UNIT_BASE + slot * UNIT_STRIDE
        unit_type = int.from_bytes(read_memory(pid, base + 0x8D, 1), "little")
        owner = int.from_bytes(read_memory(pid, base + 0x8E, 1), "little")
        if owner == 0 and unit_type == SEED_TYPE:
            rows.append({
                "slot": slot,
                "x": int.from_bytes(read_memory(pid, base + UNIT_X_OFFSET, 2), "little", signed=True),
                "y": int.from_bytes(read_memory(pid, base + UNIT_Y_OFFSET, 2), "little", signed=True),
            })
    return rows


def unit_snapshot(pid: int, slot: int) -> dict[str, Any]:
    """Read one live unit before seeding so the fixture follows the visible worker."""
    if not 0 < slot < 1200:
        raise ProbeError(f"worker slot outside stock range: {slot}")
    base = UNIT_BASE + slot * UNIT_STRIDE
    return {
        "slot": slot,
        "unit_type": int.from_bytes(read_memory(pid, base + 0x8D, 1), "little"),
        "owner": int.from_bytes(read_memory(pid, base + 0x8E, 1), "little"),
        "x": int.from_bytes(read_memory(pid, base + UNIT_X_OFFSET, 2), "little", signed=True),
        "y": int.from_bytes(read_memory(pid, base + UNIT_Y_OFFSET, 2), "little", signed=True),
    }


def dense_fixture_requests(worker: Mapping[str, Any]) -> list[dict[str, int]]:
    """Return every non-worker cell in the worker-centered 7x8 grid.

    The minimap click changes the camera between runs, so a fixed world-space
    offset is not a reliable visibility contract.  The live worker is the
    stable on-map anchor: populate dx=-3..3 and dy=-3..4 around it, excluding
    the worker's own cell.  The grid is shifted one row toward positive world
    Y so its upper row does not overlap the nearby base footprint.  One unit
    per coordinate keeps the fixture spatial
    rather than relying on stacked units at a single point.
    """
    worker_x = int(worker["x"])
    worker_y = int(worker["y"])
    requests: list[dict[str, int]] = []
    for dy in range(-3, 5):
        for dx in range(-3, 4):
            if dx == 0 and dy == 0:
                continue
            requests.append({"x": worker_x + dx, "y": worker_y + dy, "count": 1})
    if any(not 0 <= item[axis] < 180 for item in requests for axis in ("x", "y")):
        raise ProbeError(f"dense fixture falls outside the 180x180 map: {requests}")
    if sum(item["count"] for item in requests) != SEED_COUNT:
        raise ProbeError(f"dense fixture count mismatch: {requests}")
    return requests


def selected_unit_raw(pid: int, snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for slot in snapshot["slots"]:
        if not 0 < slot < 1200:
            rows.append({"slot": slot, "status": "OUT_OF_STOCK_RANGE"})
            continue
        base = UNIT_BASE + slot * UNIT_STRIDE
        rows.append({
            "slot": slot,
            "command": int.from_bytes(read_memory(pid, base + UNIT_COMMAND_OFFSET, 2), "little", signed=True),
            "pending_command": int.from_bytes(
                read_memory(pid, base + UNIT_PENDING_COMMAND_OFFSET, 4), "little", signed=False,
            ),
            "pending_xy": int.from_bytes(
                read_memory(pid, base + UNIT_PENDING_XY_OFFSET, 4), "little", signed=False,
            ),
            "pending_target_uid": int.from_bytes(
                read_memory(pid, base + UNIT_PENDING_TARGET_UID_OFFSET, 4), "little", signed=False,
            ),
            "x": int.from_bytes(read_memory(pid, base + UNIT_X_OFFSET, 2), "little", signed=True),
            "y": int.from_bytes(read_memory(pid, base + UNIT_Y_OFFSET, 2), "little", signed=True),
            "raw_command_area": read_memory(pid, base + UNIT_COMMAND_OFFSET, 0x110).hex(),
        })
    return rows


def attack_observation(
    before: list[dict[str, Any]], after: list[dict[str, Any]], target_slot: int,
    *, immediate: list[dict[str, Any]] | None = None, target_uid: int | None = None,
) -> dict[str, Any]:
    """Summarize attack state from the unit's live and pending command fields.

    ``+0x290`` is the live command state, while ``+0x384``/``+0x388``/``+0x38c``
    are the pending command, target xy, and target uid.  The pending attack
    word is transient, so the probe accepts evidence from either the
    immediate or delayed sample, but every selected unit must show both an
    attack state and the expected target uid in one sample.
    """
    before_by_slot = {int(row["slot"]): row for row in before}
    delayed_by_slot = {int(row["slot"]): row for row in after}
    immediate_by_slot = {int(row["slot"]): row for row in (immediate or [])}
    expected_uid = target_uid if target_uid is not None else target_slot
    rows: list[dict[str, Any]] = []
    for slot, row in delayed_by_slot.items():
        previous = before_by_slot.get(slot, {})
        samples = [
            ("immediate", immediate_by_slot.get(slot)),
            ("delayed", row),
        ]

        def is_attack(sample: Mapping[str, Any]) -> bool:
            command = sample.get("command")
            pending = sample.get("pending_command")
            return command == 4 or (isinstance(pending, int) and (pending & 0xFFFF) == 4)

        def target_matches(sample: Mapping[str, Any]) -> bool:
            return sample.get("pending_target_uid") == expected_uid

        attack_evidence = next(
            ((label, sample) for label, sample in samples
             if sample is not None and is_attack(sample)),
            (None, None),
        )
        target_evidence = next(
            ((label, sample) for label, sample in samples
             if sample is not None and target_matches(sample)),
            (None, None),
        )
        valid_evidence = next(
            ((label, sample) for label, sample in samples
             if sample is not None and is_attack(sample) and target_matches(sample)),
            (None, None),
        )
        attack_label, attack_sample = attack_evidence
        target_label, target_sample = target_evidence
        valid_label, _ = valid_evidence
        rows.append({
            "slot": slot,
            "command_before": previous.get("command"),
            "command_after": row.get("command"),
            "pending_command_after": row.get("pending_command"),
            "pending_target_uid_after": row.get("pending_target_uid"),
            "attack_command": attack_sample is not None,
            "target_matches": target_sample is not None,
            "attack_evidence_sample": attack_label,
            "target_evidence_sample": target_label,
            "evidence_sample": valid_label,
        })
    command_count = sum(bool(row["attack_command"]) for row in rows)
    target_count = sum(bool(row["target_matches"]) for row in rows)
    return {
        "target_slot": target_slot,
        "target_uid": expected_uid,
        "selected_count": len(rows),
        "rows": rows,
        "attack_command_count": command_count,
        "target_match_count": target_count,
        "all_attack_commands": len(rows) > 0 and command_count == len(rows),
        "all_target_matches": len(rows) > 0 and target_count == len(rows),
        "pass": len(rows) > 0 and command_count == len(rows) and target_count == len(rows),
    }


def fixture_unit_group_snapshot(pid: int, fixture_units: list[Mapping[str, Any]]) -> dict[str, Any]:
    """Capture H2's unit-field writes independently of H3's recall result."""
    rows: list[dict[str, Any]] = []
    for fixture in fixture_units:
        slot = int(fixture["slot"])
        if not 0 < slot < 1200:
            raise ProbeError(f"fixture slot outside stock range: {slot}")
        base = UNIT_BASE + slot * UNIT_STRIDE
        rows.append({
            "slot": slot,
            "owner": int.from_bytes(read_memory(pid, base + UNIT_OWNER_OFFSET, 1), "little"),
            "unit_type": int.from_bytes(read_memory(pid, base + 0x8D, 1), "little"),
            "hp": int.from_bytes(read_memory(pid, base + UNIT_HP_OFFSET, 4), "little"),
            "selectable": int.from_bytes(read_memory(pid, base + UNIT_SELECTABLE_OFFSET, 1), "little"),
            "group": int.from_bytes(read_memory(pid, base + UNIT_GROUP_OFFSET, 4), "little", signed=True),
            "handle": int.from_bytes(read_memory(pid, base + 0x29C, 4), "little"),
        })
    groups: dict[str, int] = {}
    for row in rows:
        key = str(row["group"])
        groups[key] = groups.get(key, 0) + 1
    return {
        "count": len(rows),
        "slots": [row["slot"] for row in rows],
        "group_counts": groups,
        "rows": rows,
        "field": "unit+0x344",
        "selectable_field": "unit+0x31c",
    }


def control_group_snapshot(pid: int) -> dict[str, Any]:
    """Read the stock group-1 record without assuming the candidate is wired."""
    count = int.from_bytes(
        read_memory(pid, GROUP1_BASE_ADDRESS + GROUP1_COUNT_OFFSET, 2),
        "little", signed=True,
    )
    first_id = int.from_bytes(
        read_memory(pid, GROUP1_BASE_ADDRESS + GROUP1_FIRST_ID_OFFSET, 4),
        "little", signed=False,
    )
    current = int.from_bytes(
        read_memory(pid, GROUP_CURRENT_ADDRESS, 2), "little", signed=True,
    )
    return {
        "current_group": current,
        "group1_count": count,
        "group1_first_id": first_id,
    }


def send_key(display: str, key: str, *, ctrl: bool = False, env: Mapping[str, str], log: Any) -> None:
    """Inject one key or Ctrl+key into the private game window."""
    if ctrl:
        argv = ["xdotool", "keydown", "ctrl", "key", key, "keyup", "ctrl"]
    else:
        argv = ["xdotool", "key", key]
    subprocess.run(argv, env=env, stdout=log, stderr=log, timeout=10, check=True)


def capture(display: str, path: Path, log: Any) -> dict[str, Any]:
    result = subprocess.run(
        ["scrot", str(path)], env=dict(os.environ, DISPLAY=display),
        stdout=log, stderr=log, timeout=10, check=False,
    )
    record: dict[str, Any] = {"path": str(path), "returncode": result.returncode}
    if result.returncode == 0 and path.is_file():
        record["sha256"] = sha256(path)
    return record


def run_probe(
    source: Path, runtime_root: Path, artifact_root: Path, *, variant: str,
    ui_roundtrip: bool = False, attack_probe: bool = False,
) -> dict[str, Any]:
    if variant not in {"original", "candidate"}:
        raise ProbeError(f"unsupported variant: {variant}")
    if artifact_root.exists():
        raise ProbeError(f"artifact root must be new: {artifact_root}")
    artifact_root.mkdir(parents=True)
    source = source.expanduser().resolve()
    source_exe = source / runtime_env.ORIGINAL_EXE
    if sha256(source_exe) != ORIGINAL_SHA:
        raise ProbeError("protected source executable SHA mismatch before run")

    candidate_path = artifact_root / "g5_selection_cap50.exe"
    candidate_sha: str | None = None
    if variant == "candidate":
        candidate_path.write_bytes(g5.build_candidate(source_exe.read_bytes())[0])
        candidate_sha = sha256(candidate_path)
        if candidate_sha != TARGET_SHA:
            raise ProbeError(f"G5 candidate SHA mismatch: {candidate_sha}")

    bridge_dir = artifact_root / "stock_bridge"
    subprocess.run(
        [sys.executable, str(REPO / "patches/population/build_runtime_bridge.py"),
         "--out-dir", str(bridge_dir), "--unit-pool-capacity", "1200"],
        cwd=REPO, check=True, env=dict(os.environ, PYTHONPATH=str(REPO)),
    )
    bridge = bridge_dir / "_inmm.dll"
    manifest = runtime_env.prepare(
        source, runtime_root=runtime_root, bridge=bridge, timeout=60,
    )
    manifest_output = manifest.get("output")
    manifest_game = manifest.get("game")
    manifest_wine = manifest.get("wine")
    if not isinstance(manifest_output, Mapping) or not isinstance(manifest_game, Mapping) or not isinstance(manifest_wine, Mapping):
        raise ProbeError("runtime manifest sections are malformed")
    run_dir = manifest_output.get("run_dir")
    game_root = manifest_game.get("root")
    prefix_root = manifest_wine.get("prefix")
    if not all(isinstance(value, str) for value in (run_dir, game_root, prefix_root)):
        raise ProbeError("runtime manifest paths are malformed")
    run_dir_text = cast(str, run_dir)
    game_root_text = cast(str, game_root)
    prefix_root_text = cast(str, prefix_root)
    manifest_path = Path(run_dir_text) / "manifest.json"
    original_check = runtime_env.check_runtime(manifest_path)
    game = Path(game_root_text)
    prefix = Path(prefix_root_text)
    private_exe = game / runtime_env.ORIGINAL_EXE
    if sha256(private_exe) != ORIGINAL_SHA:
        raise ProbeError("private original copy failed pre-install check")

    if variant == "candidate":
        private_exe.write_bytes(candidate_path.read_bytes())
        if sha256(private_exe) != TARGET_SHA:
            raise ProbeError("private candidate SHA verification failed")
    private_exe_sha = sha256(private_exe)
    selection_base = g5.SELECTION_BASE if variant == "candidate" else STOCK_SELECTION_BASE
    selection_capacity = g5.TARGET_CAPACITY if variant == "candidate" else STOCK_SELECTION_CAPACITY
    provenance: dict[str, Any] = {
        "schema": "syw2plus.g5-drag-runtime.v4",
        "variant": variant,
        "source_root": str(source),
        "source_exe_sha256": sha256(source_exe),
        "candidate_source": str(candidate_path) if variant == "candidate" else None,
        "candidate_sha256": candidate_sha,
        "private_run": run_dir_text,
        "private_game": str(game),
        "private_prefix": str(prefix),
        "private_exe": str(private_exe),
        "private_exe_sha256": private_exe_sha,
        "original_manifest_check": original_check,
        "bridge_sha256": sha256(bridge),
        "stock_bridge_pool": {"capacity": 1200, "base": hex(UNIT_BASE)},
        "candidate_selection_storage": {
            "base": hex(selection_base), "capacity": selection_capacity,
        },
    }
    write_json(artifact_root / "candidate-provenance.json", provenance)

    result: dict[str, Any] = {
        "schema": "syw2plus.g5-drag-probe.v3",
        "status": "UNKNOWN",
        "provenance": provenance,
        "fixture": {"owner": 0, "type": SEED_TYPE, "count": SEED_COUNT,
                     "synthetic": True,
                     "method": "stock-layout diagnostic op5 engine-seeded dense rows",
                     "anchor": {"slot": VISIBLE_WORKER_SLOT,
                                "origin": "raw before fixture"}},
        "inputs": [],
        "ui_roundtrip_requested": ui_roundtrip,
        "attack_probe_requested": attack_probe,
    }
    log_path = artifact_root / "probe.log"
    log = log_path.open("a", encoding="utf-8")
    children: list[Any] = []
    xvfb: Any = None
    display = ""
    pid: int | None = None
    try:
        env = dict(
            os.environ, WINEPREFIX=str(prefix), WINEARCH="win32", WINEDEBUG="-all",
            LANG="ko_KR.UTF-8", LC_ALL="ko_KR.UTF-8", WINEDLLOVERRIDES="ddraw=b",
            SYW2_SUPPLY_PROBE="1",
        )
        xvfb, display = runtime_env._xvfb(log, "1600x1200x24")
        env["DISPLAY"] = display
        children.append(subprocess.Popen(
            ["wine", "explorer", "/desktop=Default,1600x1200"],
            cwd=game, env=env, stdout=log, stderr=log,
        ))
        time.sleep(1)
        game_proc = subprocess.Popen(
            ["wine", str(private_exe)], cwd=game, env=env, stdout=log, stderr=log,
        )
        children.append(game_proc)
        pid = game_proc.pid

        def state() -> dict[str, Any]:
            if pid is None:
                raise ProbeError("candidate PID is unavailable")
            return read_state(pid)

        def wait_for(predicate: Callable[[dict[str, Any]], bool], label: str, timeout: float = 45) -> dict[str, Any]:
            deadline = time.monotonic() + timeout
            last: dict[str, Any] = {}
            while time.monotonic() < deadline:
                try:
                    last = state()
                    if predicate(last):
                        result.setdefault("states", {})[label] = {"ps": last.get("ps"), "tick": last.get("tick")}
                        return last
                except (OSError, ValueError, ProbeError) as exc:
                    last = {"error": f"{type(exc).__name__}: {exc}"}
                time.sleep(0.25)
            raise ProbeError(f"{label} timeout; last={last}")

        wait_for(lambda item: item.get("ps") == 9, "ps9")
        tree = runtime_env._window_tree(display, 10)
        outer, content = runtime_env._game_window_ids(tree)
        if content is None:
            raise ProbeError("candidate game content window was not found")
        content_info = runtime_env._xwininfo_details(display, content, 10)
        crop = (int(content_info["x"]), int(content_info["y"]))

        def click(x: int, y: int, *, drag_to: tuple[int, int] | None = None, button: int = 1) -> None:
            argv = [sys.executable, str(REPO / "tools/x11_mouse_click.py"), "--display", display,
                    str(crop[0] + x), str(crop[1] + y), "--button", str(button)]
            if drag_to is not None:
                argv += ["--drag-to", str(crop[0] + drag_to[0]), str(crop[1] + drag_to[1])]
            subprocess.run(argv, env=env, stdout=log, stderr=log, timeout=10, check=True)
            result["inputs"].append({"x": x, "y": y, "drag_to": list(drag_to) if drag_to else None, "button": button})

        subprocess.run(["xdotool", "windowfocus", outer], env=env, stdout=log, stderr=log, timeout=10, check=True)
        click(184, 560)
        wait_for(lambda item: item.get("ps") == 7, "ps7")

        def read_selector() -> dict[str, Any]:
            if pid is None:
                raise ProbeError("candidate PID is unavailable")
            return runtime_env._read_lobby_selector(lambda address, size: read_memory(pid, address, size))

        selected = read_selector().get("selected")
        if selected == "solo":
            click(344, 169)
            time.sleep(0.5)
        click(462, 169)
        deadline = time.monotonic() + 10
        while read_selector().get("selected") != "solo" and time.monotonic() < deadline:
            time.sleep(0.2)
        if read_selector().get("selected") != "solo":
            raise ProbeError("solo selector did not settle")
        click(608, 564)
        wait_for(lambda item: item.get("ps") == 5, "ps5")
        ready_deadline = time.monotonic() + 12
        ready: dict[str, Any] = {}
        while time.monotonic() < ready_deadline:
            ready = runtime_env._read_local_ready_state(lambda address, size: read_memory(pid, address, size))
            if ready.get("ready_value") == 1:
                break
            time.sleep(0.2)
        if ready.get("ready_value") != 1:
            raise ProbeError(f"local lobby did not become ready: {ready}")
        click(608, 564)
        wait_for(lambda item: item.get("ps") == 3 and int(item.get("tick", 0)) > 0, "ps3")

        worker = unit_snapshot(pid, VISIBLE_WORKER_SLOT)
        if worker["owner"] != 0 or worker["unit_type"] in {0, SEED_TYPE}:
            raise ProbeError(f"slot1198 is not the expected pre-existing worker: {worker}")
        result["visible_worker_before_fixture"] = worker
        fixture_requests = dense_fixture_requests(worker)
        result["fixture"]["requests"] = fixture_requests
        receipts: list[dict[str, Any]] = []
        supply = SupplyProbe(prefix)
        for request in fixture_requests:
            receipt = supply.call(
                op=5, owner=0, unit_type=SEED_TYPE,
                x=request["x"], y=request["y"], count=request["count"],
            )
            receipts.append(receipt)
            if not receipt.get("ok") or receipt.get("fixture_added") != request["count"]:
                raise ProbeError(f"dense fixture batch failed: {receipt}")
        result["fixture_receipts"] = receipts
        if sum(int(receipt.get("fixture_added", 0)) for receipt in receipts) != SEED_COUNT:
            raise ProbeError(f"dense fixture total failed: {receipts}")
        time.sleep(1)
        result["fixture_units"] = fixture_units(pid)
        if attack_probe:
            # A real enemy unit is part of the paired fixture.  Type 2 is a
            # combat-capable stock unit, and owner 1 is intentionally distinct
            # from the selected owner 0; no unit fields are rewritten by the
            # probe.  The bridge's producer receipt is the authoritative slot
            # identity used for target matching below.
            target_world = (
                int(worker["x"]) + ATTACK_TARGET_OFFSET[0],
                int(worker["y"]) + ATTACK_TARGET_OFFSET[1],
            )
            if any(not 0 <= value < 180 for value in target_world):
                raise ProbeError(f"attack target falls outside the map: {target_world}")
            target_receipt = supply.call(
                op=5, owner=1, unit_type=SEED_TYPE,
                x=target_world[0], y=target_world[1], count=1,
            )
            if not target_receipt.get("ok") or target_receipt.get("fixture_added") != 1:
                raise ProbeError(f"attack target fixture failed: {target_receipt}")
            target_slot = int(target_receipt.get("producer", {}).get("slot", 0))
            if not 0 < target_slot < 1200:
                raise ProbeError(f"attack target slot missing: {target_receipt}")
            target_base = UNIT_BASE + target_slot * UNIT_STRIDE
            result["attack_fixture"] = {
                "owner": 1,
                "type": SEED_TYPE,
                "requested_world": list(target_world),
                "screen_input": list(ATTACK_TARGET_SCREEN),
                "receipt": target_receipt,
                "slot": target_slot,
                "handle": int.from_bytes(read_memory(pid, target_base + 0x29C, 4), "little"),
                "hp": int.from_bytes(read_memory(pid, target_base + UNIT_HP_OFFSET, 4), "little"),
                "owner_raw": int.from_bytes(read_memory(pid, target_base + UNIT_OWNER_OFFSET, 1), "little"),
                "type_raw": int.from_bytes(read_memory(pid, target_base + 0x8D, 1), "little"),
            }
        result["captures"] = [capture(display, artifact_root / "after-fixture.png", log)]
        click(235, 555)
        time.sleep(1)
        result["camera_after_minimap"] = list(
            int.from_bytes(read_memory(pid, 0x00B42D7C + offset, 4), "little", signed=True)
            for offset in (0, 4)
        )
        before = selection_snapshot(pid, base=selection_base, capacity=selection_capacity)
        result["selection_before"] = before
        result["captures"].append(capture(display, artifact_root / "before-drag.png", log))
        wait_for_selection_trace_gate(pid, artifact_root)
        # Cover the worker-centered grid while keeping the lower edge above
        # the command HUD (y >= 480).  The original and candidate use the
        # same rectangle so the selection-cap comparison remains paired.
        click(*DRAG_START, drag_to=DRAG_END)
        time.sleep(1)
        after = selection_snapshot(pid, base=selection_base, capacity=selection_capacity)
        result["selection_after"] = after
        result["captures"].append(capture(display, artifact_root / "after-drag.png", log))
        if after["count"] == 0:
            # A debugger attach/continue can consume the first synthetic mouse
            # gesture even after the tick gate has opened.  The lap649
            # operating instruction allows exactly one same-coordinate retry;
            # keep both snapshots so a zero result remains auditable.
            result["drag_retry"] = {"attempted": True, "same_rectangle": True}
            click(*DRAG_START, drag_to=DRAG_END)
            time.sleep(1)
            after = selection_snapshot(pid, base=selection_base, capacity=selection_capacity)
            result["selection_after_retry"] = after
            result["captures"].append(capture(display, artifact_root / "after-drag-retry.png", log))
            if after["count"] == 0:
                raise ProbeError("drag produced no selection after one retry")

        if attack_probe:
            target_slot = int(result["attack_fixture"]["slot"])
            attack_before = selected_unit_raw(pid, after)
            result["captures"].append(capture(display, artifact_root / "before-attack.png", log))
            # This is the product input under test: enter the stock attack
            # mode, then left-click the visible enemy target.  The earlier
            # right-click-only input was accepted as movement on the original
            # even when the target sprite was visible.
            send_key(display, "a", env=env, log=log)
            result["inputs"].append({"key": "a", "attack_mode": True})
            click(*ATTACK_TARGET_SCREEN, button=1)
            time.sleep(0.05)
            attack_immediate = selected_unit_raw(pid, after)
            time.sleep(0.25)
            attack_after = selected_unit_raw(pid, after)
            result["attack_probe"] = attack_observation(
                attack_before,
                attack_after,
                target_slot,
                immediate=attack_immediate,
                target_uid=int(result["attack_fixture"]["handle"]),
            )
            result["attack_probe"]["before"] = attack_before
            result["attack_probe"]["immediate"] = attack_immediate
            result["attack_probe"]["after"] = attack_after
            result["captures"].append(capture(display, artifact_root / "after-attack.png", log))

        if ui_roundtrip:
            result["ui_roundtrip"] = {}
            fixture_units_for_trace = cast(list[Mapping[str, Any]], result["fixture_units"])
            result["ui_roundtrip"]["selected"] = {
                "selection": after,
                "group": control_group_snapshot(pid),
            }
            result["captures"].append(capture(display, artifact_root / "ui-selected.png", log))

            wait_for_ui_trace_gate(pid, artifact_root)
            send_key(display, "1", ctrl=True, env=env, log=log)
            time.sleep(0.5)
            result["ui_roundtrip"]["stored"] = {
                "selection": selection_snapshot(pid, base=selection_base, capacity=selection_capacity),
                "group": control_group_snapshot(pid),
                "fixture_units": fixture_unit_group_snapshot(pid, fixture_units_for_trace),
            }
            result["captures"].append(capture(display, artifact_root / "ui-ctrl1-stored.png", log))

            click(*DESELECT_POINT)
            time.sleep(0.5)
            result["ui_roundtrip"]["deselected"] = {
                "selection": selection_snapshot(pid, base=selection_base, capacity=selection_capacity),
                "group": control_group_snapshot(pid),
                "fixture_units": fixture_unit_group_snapshot(pid, fixture_units_for_trace),
            }
            result["captures"].append(capture(display, artifact_root / "ui-deselected.png", log))

            send_key(display, "1", env=env, log=log)
            time.sleep(0.5)
            result["ui_roundtrip"]["recalled"] = {
                "selection": selection_snapshot(pid, base=selection_base, capacity=selection_capacity),
                "group": control_group_snapshot(pid),
                "fixture_units": fixture_unit_group_snapshot(pid, fixture_units_for_trace),
            }
            result["captures"].append(capture(display, artifact_root / "ui-recalled.png", log))

            send_key(display, "Escape", env=env, log=log)
            wait_for(lambda item: item.get("ps") == 23, "pause_for_save")
            click(*PAUSE_SAVE_POINT)
            time.sleep(0.5)
            click(*SAVE_SLOT_POINT)
            click(*SAVE_ACTION_POINT)
            time.sleep(0.8)
            save_path = game / "save" / "save001.dat"
            if not save_path.is_file():
                raise ProbeError(f"private save was not created: {save_path}")
            result["ui_roundtrip"]["save"] = {
                "path": str(save_path),
                "sha256": sha256(save_path),
                "size": save_path.stat().st_size,
            }
            result["captures"].append(capture(display, artifact_root / "ui-saved.png", log))

            click(*SAVE_MENU_RETURN_POINT)
            click(*RESUME_POINT)
            wait_for(lambda item: item.get("ps") == 3, "resume_after_save")
            click(*DESELECT_POINT)
            time.sleep(0.3)
            send_key(display, "Escape", env=env, log=log)
            wait_for(lambda item: item.get("ps") == 23, "pause_for_load")
            click(*PAUSE_LOAD_POINT)
            time.sleep(0.5)
            click(*SAVE_SLOT_POINT)
            click(*SAVE_ACTION_POINT)
            wait_for(lambda item: item.get("ps") == 3 and int(item.get("tick", 0)) > 0, "load_complete", 90)
            time.sleep(0.5)
            result["ui_roundtrip"]["loaded"] = {
                "selection": selection_snapshot(pid, base=selection_base, capacity=selection_capacity),
                "group": control_group_snapshot(pid),
            }
            result["captures"].append(capture(display, artifact_root / "ui-loaded.png", log))
            click(*DESELECT_POINT)
            time.sleep(0.3)
            send_key(display, "1", env=env, log=log)
            time.sleep(0.5)
            result["ui_roundtrip"]["recalled_after_load"] = {
                "selection": selection_snapshot(pid, base=selection_base, capacity=selection_capacity),
                "group": control_group_snapshot(pid),
            }
            result["captures"].append(capture(display, artifact_root / "ui-recalled-after-load.png", log))

            stored = result["ui_roundtrip"]["stored"]
            recalled = result["ui_roundtrip"]["recalled"]
            loaded = result["ui_roundtrip"]["loaded"]
            recalled_after_load = result["ui_roundtrip"]["recalled_after_load"]
            result["ui_roundtrip"]["checks"] = {
                "selected_50": after["count"] == 50 and after["unique_slots"] == 50,
                # The accepted v2 layout deliberately keeps the stock
                # PlayerStruct row at 20 and persists overflow members in
                # unit+0x344.  Together these represent the 50-member group
                # without corrupting adjacent group metadata.
                "group_stored_stock20_plus_overflow49": (
                    stored["group"]["group1_count"] == 20
                    and stored["fixture_units"]["group_counts"] == {"-1": 6, "1": 49}
                ),
                "deselected": result["ui_roundtrip"]["deselected"]["selection"]["count"] == 0,
                "recalled_50": recalled["selection"]["count"] == 50,
                "save_created": bool(result["ui_roundtrip"]["save"]["sha256"]),
                "group_retained_after_load": (
                    loaded["group"]["group1_count"] == 20
                    and loaded["group"]["group1_first_id"] == stored["group"]["group1_first_id"]
                ),
                "recalled_50_after_load": recalled_after_load["selection"]["count"] == 50,
            }
        click(*DRAG_END, button=3)
        time.sleep(1)
        result["move_selection"] = selection_snapshot(pid, base=selection_base, capacity=selection_capacity)
        result["selected_unit_raw"] = selected_unit_raw(pid, result["move_selection"])
        moved = [row for row in result["selected_unit_raw"] if isinstance(row.get("command"), int) and row["command"] != 0]
        result["movement_command_nonzero"] = len(moved)
        if variant == "candidate":
            drag_pass = after["count"] == 50 and after["unique_slots"] == 50
            ui_pass = not ui_roundtrip or all(result["ui_roundtrip"]["checks"].values())
            attack_pass = not attack_probe or result.get("attack_probe", {}).get("pass", False)
            if attack_probe:
                result["status"] = "PASS_ATTACK_TARGET" if drag_pass and attack_pass else "FAIL_ATTACK_TARGET"
            else:
                result["status"] = "PASS_UI_ROUNDTRIP" if drag_pass and ui_pass else (
                    "PASS" if drag_pass and not ui_roundtrip else "FAIL_UI_ROUNDTRIP" if ui_roundtrip else "FAIL_SELECTION_CAP"
                )
        else:
            attack_pass = not attack_probe or result.get("attack_probe", {}).get("pass", False)
            if attack_probe:
                result["status"] = "PASS_ORIGINAL_ATTACK" if after["count"] == 20 and after["unique_slots"] == 20 and attack_pass else "FAIL_ORIGINAL_ATTACK"
            else:
                result["status"] = (
                    "PASS_ORIGINAL_CAP20"
                    if after["count"] == 20 and after["unique_slots"] == 20
                    else "FAIL_ORIGINAL_SELECTION"
                )
    except (OSError, subprocess.SubprocessError, ProbeError, ValueError, KeyError) as exc:
        result["status"] = "FAIL"
        result["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        for child in children:
            if child.poll() is None:
                child.terminate()
        for child in children:
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait(timeout=5)
        cleanup_error: str | None = None
        env = locals().get("env", os.environ)
        try:
            subprocess.run(["wineserver", "-k"], env=env, stdout=log, stderr=log, timeout=10, check=False)
            subprocess.run(["wineserver", "-w"], env=env, stdout=log, stderr=log, timeout=10, check=False)
        except (OSError, subprocess.SubprocessError) as exc:
            cleanup_error = f"{type(exc).__name__}: {exc}"
        if xvfb is not None and xvfb.poll() is None:
            xvfb.terminate()
            try:
                xvfb.wait(timeout=5)
            except subprocess.TimeoutExpired:
                xvfb.kill()
                xvfb.wait(timeout=5)
        result["cleanup"] = {
            "error": cleanup_error,
            "owned_children_stopped": all(child.poll() is not None for child in children),
            "xvfb_stopped": xvfb is None or xvfb.poll() is not None,
            "prefix_processes_after": runtime_env._prefix_pids(prefix),
            "global_kill_used": False,
        }
        result["cleanup"]["ok"] = not result["cleanup"]["prefix_processes_after"] and cleanup_error is None
        result["source_sha_after"] = sha256(source_exe)
        result["source_unchanged"] = result["source_sha_after"] == ORIGINAL_SHA
        write_json(artifact_root / "probe-result.json", result)
        log.close()
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", choices=("original", "candidate"), default="candidate")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--runtime-root", type=Path, default=DEFAULT_RUNTIME_ROOT)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--ui-roundtrip", action="store_true",
                        help="exercise portrait/group/save/load inputs after the drag")
    parser.add_argument("--attack-probe", action="store_true",
                        help="seed one hostile type-2 unit and issue one real attack click")
    args = parser.parse_args(argv)
    result = run_probe(args.source, args.runtime_root, args.artifact_root,
                       variant=args.variant, ui_roundtrip=args.ui_roundtrip,
                       attack_probe=args.attack_probe)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status", "").startswith("PASS") and result.get("cleanup", {}).get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
