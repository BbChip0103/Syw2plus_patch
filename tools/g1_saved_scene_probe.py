"""Run a deterministic G1 saved-scene comparison on private game copies.

The stock presentation probe starts a fresh random map, which is useful for
input plumbing but cannot support a same-scene visual comparison.  This probe
loads the pinned ``save006.dat`` in both lanes, then applies the same logical
selection/drag/minimap/production inputs.  The baseline is the original
800x600 presentation; the candidate enables the opt-in W60 1600x1200 mirror.
All writes are limited to the private game copy, its Wine prefix, and the
diagnostic bridge process.
"""

from __future__ import annotations

import argparse
import contextlib
from dataclasses import dataclass
import functools
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import statistics
import struct
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from typing import Any, Callable, Mapping, Sequence

from patches.population import runtime_driver
from tools import runtime_env
from tools.g1_mirror2x_probe import validate_trace
from tools.s1_load_evidence import SELECTED_INDEX_ADDRESS


REPO = Path(__file__).resolve().parents[1]
SOURCE = runtime_env.DEFAULT_SOURCE
FIXTURE_SOURCE = REPO.parent / "Syw2plus_re" / "Syw2plus"
SAVE_NAME = "save006.dat"
SAVE_SHA256 = "616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064"
SAVE_INDEX = 7
# Second in-game scene (H-S2).  Pin and 1-based list index come from the S1
# load-evidence fixture table (lap354/363), not from a guess.
SAVE000_NAME = "save000.dat"
SAVE000_SHA256 = "1c703551888f5c85a1fa2fb7b43d28309eb0b88e4bbf6e859f1a98b629e719da"
SAVE000_INDEX = 1
SAVE_FIXTURES = {
    "save006": (SAVE_NAME, SAVE_SHA256, SAVE_INDEX),
    "save000": (SAVE000_NAME, SAVE000_SHA256, SAVE000_INDEX),
}
LOAD_MENU = (296, 505)
LOAD_CONFIRM = (316, 372)
SELECTION_POINT = (270, 48)
DRAG_FROM = (100, 40)
DRAG_TO = (400, 220)
MINIMAP_POINT = (90, 553)
EMPTY_SELECTION_POINT = (600, 300)
# G2 Phase-C paired probing established this live worker-production cell for
# the same HQ command grid.  The previous (670, 490) point is the Stop cell.
PRODUCTION_POINT = (668, 540)
# Fresh lap943 capture after centering the owner0 slot1199 HQ at [165,87]
# places its clickable structure body around this logical screen point.
PRODUCTION_SELECTION_POINT = (450, 195)
PRODUCTION_SLOT = 1199
PRODUCTION_CONTROL_SECONDS = 1.0
PRODUCTION_BUILDING_TYPE = 58
PRODUCTION_UNIT_TYPE = 31
PRODUCTION_SPEC_ADDRESS = 0x009B5228 + PRODUCTION_UNIT_TYPE * 0x394 + 0x10
TERRAIN_SCROLL_KEYS = ("DOWN", "RIGHT", "LEFT", "UP")
SCROLL_PHASE_TICK_PLAN = {
    "down_input_tick": 24692,
    "down_observation_tick": 24728,
    "right_input_tick": 24788,
    "right_observation_tick": 24824,
    "final_observation_tick": 24860,
}
SNAPSHOT_HEADER = struct.Struct("<8s9IQ40s36x")
SNAPSHOT_CALLSITES = {0x004245D2, 0x004250F7}
PERFORMANCE_WINDOW_SECONDS = 20.0
PERFORMANCE_WINDOW_FILE = "inmm_g1_perf_window.active"
SELECTION_ARRAY_ADDRESS = 0x00899028
SELECTION_ARRAY_CAPACITY = 20
MINIMAP_GATE_ADDRESS = 0x0097597C
MINIMAP_WIDGET_ADDRESS = 0x00639350
MINIMAP_LUT_A_OFFSET = 0x13EEA
MINIMAP_LUT_WIDTH = 180
MINIMAP_LUT_HEIGHT = 90
MINIMAP_LUT_SIZE = MINIMAP_LUT_WIDTH * MINIMAP_LUT_HEIGHT * 2
SCENE_TIMEOUT = 90.0


class ProbeError(RuntimeError):
    """A saved-scene probe could not collect a complete observation."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _execution_source_hashes(build_manifest: Path) -> dict[str, str | None]:
    test_path = REPO / "tests" / "test_g1_saved_scene_probe.py"
    return {
        "host_probe_sha256": _sha256(Path(__file__).resolve()),
        "test_sha256": _sha256(test_path) if test_path.is_file() else None,
        "build_manifest_sha256": _sha256(build_manifest) if build_manifest.is_file() else None,
    }


def _wait_state(
    pid: int, predicate: Callable[[dict[str, Any]], bool], label: str,
    timeout: float = SCENE_TIMEOUT,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    last: dict[str, Any] = {}
    while time.monotonic() < deadline:
        try:
            last = runtime_driver.state(pid, False)
            if predicate(last):
                return last
        except (OSError, ValueError, KeyError) as exc:
            last = {"error": f"{type(exc).__name__}: {exc}"}
        time.sleep(0.15)
    raise ProbeError(f"{label} timeout; last={last}")


def _scaled_point(origin: tuple[int, int], logical: tuple[int, int], scale: int) -> tuple[int, int]:
    return origin[0] + logical[0] * scale, origin[1] + logical[1] * scale


def _inject(
    display: str, origin: tuple[int, int], logical: tuple[int, int], scale: int,
    env: Mapping[str, str], log: Any, *, button: int = 1,
    drag_to: tuple[int, int] | None = None,
) -> dict[str, Any]:
    x, y = _scaled_point(origin, logical, scale)
    argv = [
        sys.executable, str(REPO / "tools/x11_mouse_click.py"), "--display", display,
        str(x), str(y), "--button", str(button), "--hold-ms", "120", "--evidence",
    ]
    if drag_to is not None:
        to_x, to_y = _scaled_point(origin, drag_to, scale)
        argv.extend(["--drag-to", str(to_x), str(to_y), "--hold-ms", "150"])
    result = subprocess.run(argv, env=env, stdout=subprocess.PIPE, stderr=log,
                            text=True, timeout=10, check=False)
    if result.returncode:
        raise ProbeError(f"input injection failed ({result.returncode}): {argv}")
    records = []
    for line in result.stdout.splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            records.append(value)
    if not records:
        raise ProbeError(f"input injection emitted no evidence: {argv}")
    return {"logical": list(logical), "scale": scale, "argv": argv, **records[-1]}


def _send_down(display: str, env: Mapping[str, str], log: Any) -> None:
    subprocess.run(
        [sys.executable, str(REPO / "tools/x11_send_keys.py"), "--display", display, "DOWN"],
        env=env, stdout=log, stderr=log, timeout=10, check=True,
    )


def _send_key(
    display: str, env: Mapping[str, str], key: str, log: Any, *, repeat: int = 1,
    hold_ms: int | None = None,
) -> None:
    argv = [sys.executable, str(REPO / "tools/x11_send_keys.py"), "--display", display,
            "--repeat", str(repeat)]
    if hold_ms is not None:
        argv.extend(["--hold-ms", str(hold_ms)])
    subprocess.run(
        [*argv, key],
        env=env, stdout=log, stderr=log, timeout=10, check=True,
    )


def _send_key_edge(display: str, env: Mapping[str, str], key: str, *, down: bool) -> int:
    from tools import x11_send_keys

    connection = _SCROLL_X11_CONNECTIONS.get(display)
    if connection is None:
        connection = x11_send_keys.X11.XOpenDisplay(display.encode())
        if not connection:
            raise ProbeError(f"cannot open X11 display for scroll input: {display}")
        _SCROLL_X11_CONNECTIONS[display] = connection
    lookup = x11_send_keys.KEY_ALIASES.get(key.upper(), key)
    keysym = x11_send_keys.X11.XStringToKeysym(lookup.encode())
    keycode = x11_send_keys.X11.XKeysymToKeycode(connection, keysym)
    if not keysym or not keycode:
        raise ProbeError(f"cannot resolve scroll key: {key}")
    emitted_ns = time.monotonic_ns()
    if not x11_send_keys.Xtst.XTestFakeKeyEvent(connection, keycode, int(down), 0):
        raise ProbeError(f"XTest rejected scroll key edge: {key} down={down}")
    x11_send_keys.X11.XFlush(connection)
    return emitted_ns


_SCROLL_X11_CONNECTIONS: dict[str, Any] = {}


def _close_scroll_input(display: str | None) -> None:
    if display is None:
        return
    connection = _SCROLL_X11_CONNECTIONS.pop(display, None)
    if connection is not None:
        from tools import x11_send_keys

        x11_send_keys.X11.XCloseDisplay(connection)


_EDGE_DIAGONAL_SIGNS = {"UPLEFT": (False, False), "UPRIGHT": (True, False),
                        "DOWNLEFT": (False, True), "DOWNRIGHT": (True, True)}
_EDGE_SCROLL_KEYS = ("UP", "DOWN", "LEFT", "RIGHT", *_EDGE_DIAGONAL_SIGNS)


def _scroll_edge_point(
    origin: tuple[int, int], scale: int, key: str, *, down: bool,
) -> tuple[int, int]:
    """Root pointer target: window edge on press, window center on release."""
    if key not in _EDGE_SCROLL_KEYS:
        raise ValueError("edge scroll supports UP, DOWN, LEFT or RIGHT (or a UPLEFT, "
                         f"UPRIGHT, DOWNLEFT, DOWNRIGHT corner) only: {key!r}")
    center = origin[0] + 400 * scale, origin[1] + 300 * scale
    if not down:
        return center
    if key in _EDGE_DIAGONAL_SIGNS:
        right, lower = _EDGE_DIAGONAL_SIGNS[key]
        return (origin[0] + 800 * scale - 1 if right else origin[0],
                origin[1] + 600 * scale - 1 if lower else origin[1])
    if key in ("LEFT", "RIGHT"):
        return (origin[0] if key == "LEFT" else origin[0] + 800 * scale - 1), center[1]
    return center[0], origin[1] if key == "UP" else origin[1] + 600 * scale - 1


def _send_pointer_edge(
    display: str, env: Mapping[str, str], key: str, *, down: bool,
    origin: tuple[int, int], scale: int,
) -> int:
    """Edge-scroll counterpart of _send_key_edge: move the XTest pointer."""
    from tools import x11_mouse_click, x11_send_keys

    connection = _SCROLL_X11_CONNECTIONS.get(display)
    if connection is None:
        connection = x11_send_keys.X11.XOpenDisplay(display.encode())
        if not connection:
            raise ProbeError(f"cannot open X11 display for scroll input: {display}")
        _SCROLL_X11_CONNECTIONS[display] = connection
    x, y = _scroll_edge_point(origin, scale, key, down=down)
    emitted_ns = time.monotonic_ns()
    x11_mouse_click._move(connection, x, y)
    return emitted_ns


_EDGE_HORIZONTAL_KEYS = ("LEFT,RIGHT", "RIGHT,LEFT")
_EDGE_DIAGONAL_KEYS = ("UPLEFT,DOWNRIGHT", "DOWNRIGHT,UPLEFT", "UPRIGHT,DOWNLEFT", "DOWNLEFT,UPRIGHT")


def _scroll_edge_option_error(
    *, edge: bool, hold: bool, keys_spec: str, terrain_scroll: bool,
) -> str | None:
    if not edge:
        return None
    if not terrain_scroll:
        return "--terrain-scroll-edge requires --terrain-scroll"
    if hold:
        return "--terrain-scroll-edge is exclusive with --terrain-scroll-hold"
    if keys_spec != "DOWN,RIGHT" and keys_spec.replace(" ", "").upper() not in (
            *_EDGE_HORIZONTAL_KEYS, *_EDGE_DIAGONAL_KEYS):
        return ("--terrain-scroll-edge only accepts --terrain-scroll-keys LEFT,RIGHT, "
                "RIGHT,LEFT or a corner pair UPLEFT,DOWNRIGHT / UPRIGHT,DOWNLEFT "
                "(either order; default UP,DOWN)")
    return None


def _scroll_edge_keys(keys_spec: str) -> tuple[str, str]:
    """Edge-scroll key pair: UP,DOWN unless the horizontal round trip is requested."""
    if keys_spec == "DOWN,RIGHT":
        return "UP", "DOWN"
    keys = tuple(part.strip().upper() for part in keys_spec.split(","))
    if len(keys) == 2 and any(key in _EDGE_DIAGONAL_SIGNS for key in keys):
        if ",".join(keys) not in _EDGE_DIAGONAL_KEYS:
            raise ValueError(f"--terrain-scroll-keys corner pair must be opposite corners: {keys_spec!r}")
        return keys[0], keys[1]
    return _parse_scroll_keys(keys_spec)


_THROTTLE_MAX_STOP_MS = 1000
_THROTTLE_MAX_RUN_MS = 5000


def _parse_candidate_throttle(spec: str) -> tuple[int, int]:
    """``STOP_MS:RUN_MS`` duty for the H-LD candidate-only SIGSTOP/SIGCONT throttle."""
    parts = spec.split(":")
    if len(parts) != 2:
        raise ValueError("--candidate-throttle must be STOP_MS:RUN_MS")
    try:
        stop_ms, run_ms = (int(part.strip()) for part in parts)
    except ValueError as error:
        raise ValueError("--candidate-throttle must be STOP_MS:RUN_MS integers") from error
    if not (1 <= stop_ms <= _THROTTLE_MAX_STOP_MS and 1 <= run_ms <= _THROTTLE_MAX_RUN_MS):
        raise ValueError(
            f"--candidate-throttle STOP_MS in 1..{_THROTTLE_MAX_STOP_MS}, "
            f"RUN_MS in 1..{_THROTTLE_MAX_RUN_MS}")
    return stop_ms, run_ms


def _candidate_throttle_option_error(spec: str | None, *, terrain_scroll: bool) -> str | None:
    if spec is None:
        return None
    if not terrain_scroll:
        return "--candidate-throttle requires --terrain-scroll"
    try:
        _parse_candidate_throttle(spec)
    except ValueError as error:
        return str(error)
    return None


@dataclass(frozen=True)
class _ProcInfo:
    cwd: str
    maps: str
    comm: str
    cmdline: str
    state: str | None


def _read_proc_info(pid: int) -> _ProcInfo:
    proc = Path("/proc") / str(pid)
    stat = (proc / "stat").read_text(encoding="utf-8", errors="replace")
    return _ProcInfo(
        cwd=os.readlink(proc / "cwd"),
        maps=(proc / "maps").read_text(encoding="utf-8", errors="replace"),
        comm=(proc / "comm").read_text(encoding="utf-8", errors="replace").strip(),
        cmdline=(proc / "cmdline").read_bytes().replace(b"\0", b" ").decode("utf-8", "replace"),
        state=stat[stat.rindex(")") + 2:][:1] or None,
    )


def _read_proc_state(pid: int) -> str | None:
    try:
        stat = (Path("/proc") / str(pid) / "stat").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    return stat[stat.rindex(")") + 2:][:1] or None


def _throttle_target_error(
    *, pid: int, expected_pid: int, variant: str, game_dir: str, exe_name: str,
    info: _ProcInfo,
) -> str | None:
    """Reject any throttle target that is not this candidate lane's private-copy game process.

    ``/proc/<pid>/exe`` is the shared wine loader, so the private copy is bound through the
    working directory and the mapped private EXE image instead.
    """
    if variant != "candidate":
        return "throttle target must be the candidate lane"
    if pid != expected_pid:
        return f"throttle pid {pid} is not this lane's game process {expected_pid}"
    if "wineserver" in info.comm:
        return "throttle target must not be wineserver"
    if os.path.normpath(info.cwd) != os.path.normpath(game_dir):
        return f"throttle target cwd {info.cwd} is not the private game copy {game_dir}"
    private_image = os.path.join(game_dir, exe_name).lower()
    if private_image not in info.maps.lower():
        return "throttle target does not map the private game EXE image"
    return None


class _CandidateThrottle:
    """Periodically SIGSTOP/SIGCONT exactly one verified game PID (H-LD slow lane)."""

    def __init__(
        self, pid: int, stop_ms: int, run_ms: int, *,
        kill: Callable[[int, int], None] = os.kill,
        read_state: Callable[[int], str | None] = _read_proc_state,
    ) -> None:
        self.pid = pid
        self.stop_ms = stop_ms
        self.run_ms = run_ms
        self._kill = kill
        self._read_state = read_state
        self._done = threading.Event()
        self._thread: threading.Thread | None = None
        self._stop_count = 0
        self._stopped_s = 0.0
        self._process_gone = False
        self._summary: dict[str, Any] | None = None

    def start(self) -> None:
        self._thread = threading.Thread(target=self._loop, name="candidate-throttle", daemon=True)
        self._thread.start()

    def _loop(self) -> None:
        try:
            while not self._done.is_set():
                self._kill(self.pid, signal.SIGSTOP)
                self._stop_count += 1
                started = time.monotonic()
                interrupted = self._done.wait(self.stop_ms / 1000.0)
                self._kill(self.pid, signal.SIGCONT)
                self._stopped_s += time.monotonic() - started
                if interrupted or self._done.wait(self.run_ms / 1000.0):
                    return
        except ProcessLookupError:
            self._process_gone = True

    def stop(self) -> dict[str, Any]:
        if self._summary is not None:
            return self._summary
        self._done.set()
        if self._thread is not None:
            self._thread.join(timeout=5)
        try:
            self._kill(self.pid, signal.SIGCONT)
        except ProcessLookupError:
            self._process_gone = True
        state = self._read_state(self.pid)
        not_stopped = state != "T"
        self._summary = {
            "status": "PASS" if not_stopped else "FAIL",
            "pid": self.pid, "stop_ms": self.stop_ms, "run_ms": self.run_ms,
            "stop_count": self._stop_count,
            "stopped_ms": round(self._stopped_s * 1000.0, 1),
            "final_state": state, "final_state_not_stopped": not_stopped,
            "process_gone": self._process_gone,
        }
        return self._summary


def _wait_scroll_receiver_ready(ready_path: Path, *, timeout: float = 10.0) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    last_error = "ready acknowledgment not written"
    while time.monotonic() < deadline:
        try:
            row = json.loads(ready_path.read_text(encoding="utf-8"))
            if (isinstance(row, dict) and row.get("schema") == "g1-scroll-receiver-ready-v1"
                    and row.get("status") == "PASS" and row.get("hwnd")):
                return row
            last_error = "invalid receiver-ready acknowledgment"
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            last_error = f"{type(exc).__name__}: {exc}"
        time.sleep(0.05)
    raise ProbeError(f"scroll receiver did not become ready; {last_error}")


def _arm_and_wait_scroll_receiver(arm_path: Path, ready_path: Path) -> dict[str, Any]:
    arm_path.write_text("armed\n", encoding="ascii")
    return _wait_scroll_receiver_ready(ready_path)


def _wait_scroll_camera_stable(
    pid: int, read_memory: Callable[[int, int], bytes], *, timeout: float = 4.0,
) -> dict[str, Any]:
    """Require five stable PS3 camera samples while simulation ticks advance."""
    deadline = time.monotonic() + timeout
    previous_camera: list[int] | None = None
    previous_tick: int | None = None
    stable_samples = 0
    samples: list[dict[str, Any]] = []
    last_camera: list[int] | None = None
    while time.monotonic() < deadline:
        state = runtime_driver.state(pid, False)
        camera = runtime_env._read_camera(read_memory)
        tick = state.get("tick")
        samples.append({"monotonic_ns": time.monotonic_ns(), "camera": camera,
                        "tick": tick, "program_state": state.get("ps")})
        last_camera = camera
        if (state.get("ps") == 3 and camera == previous_camera
                and isinstance(tick, int) and isinstance(previous_tick, int)
                and tick > previous_tick):
            stable_samples += 1
            if stable_samples >= 5:
                return {"status": "PASS", "camera": camera,
                        "stable_samples": stable_samples, "samples": samples}
        else:
            stable_samples = 0
        previous_camera = camera
        previous_tick = tick if isinstance(tick, int) else None
        time.sleep(0.05)
    return {"status": "INCOMPLETE", "camera": last_camera,
            "stable_samples": stable_samples, "samples": samples}


def _wait_game_tick_delta(pid: int, start_tick: int, delta: int, *, timeout: float = 8.0) -> dict[str, Any]:
    target_tick = start_tick + delta
    deadline = time.monotonic() + timeout
    last: dict[str, Any] = {}
    while time.monotonic() < deadline:
        last = runtime_driver.state(pid, False)
        tick = last.get("tick")
        if last.get("ps") == 3 and isinstance(tick, int) and tick >= target_tick:
            return {"status": "PASS", "start_tick": start_tick, "target_tick": target_tick,
                    "end_tick": tick}
        time.sleep(0.02)
    return {"status": "INCOMPLETE", "start_tick": start_tick,
            "target_tick": target_tick, "last": last}


# Hold-scroll keyup lands this many ticks before the observation tick so the
# camera settles before the scene snapshot (H-D2h).
SCROLL_HOLD_RELEASE_LEAD_TICKS = 12


def _build_common_tick_plan(start_tick: int) -> dict[str, int]:
    """Freeze one absolute save-tick schedule before either lane scrolls."""
    return {
        "loaded_tick": start_tick,
        "down_input_tick": start_tick + 120,
        "down_observation_tick": start_tick + 156,
        "right_input_tick": start_tick + 216,
        "right_observation_tick": start_tick + 252,
        "final_observation_tick": start_tick + 288,
    }


def _read_sim_tick(pid: int) -> int:
    return struct.unpack("<i", runtime_driver.read(pid, 0x008924B8, 4))[0]


def _wait_for_exact_tick(pid: int, target_tick: int, *, timeout: float = 12.0) -> dict[str, Any]:
    """Wait for one preregistered tick; passing it makes the observation invalid."""
    deadline = time.monotonic() + timeout
    last_tick: int | None = None
    while time.monotonic() < deadline:
        last_tick = _read_sim_tick(pid)
        if last_tick == target_tick:
            return {"status": "PASS", "target_tick": target_tick, "observed_tick": last_tick}
        if last_tick > target_tick:
            return {"status": "INVALID", "target_tick": target_tick,
                    "observed_tick": last_tick, "reason": "target tick missed"}
        time.sleep(0.001)
    return {"status": "INVALID", "target_tick": target_tick,
            "observed_tick": last_tick, "reason": "target tick timeout"}


def _decode_batched_scene(
    ps_before: int, tick_before: int, camera_before: Sequence[int],
    player_bytes: bytes, exists_bytes: bytes, pool: bytes,
) -> dict[str, Any]:
    """Decode the six bounded scene ranges for both live and in-process samples."""
    player_stride = runtime_driver.PLAYER_STRUCT_SIZE
    capacity, _unit_base, _exists_base = runtime_driver.STOCK_POOL
    if len(player_bytes) != 8 * player_stride:
        raise ValueError("player snapshot has an invalid size")
    if len(exists_bytes) != capacity * 2 or len(pool) != capacity * 0x758:
        raise ValueError("unit snapshot has an invalid size")
    players = []
    for owner in range(8):
        data = player_bytes[owner * player_stride:(owner + 1) * player_stride]
        players.append({
            "owner": owner, "nation": data[0], "ai": data[2],
            "rice": struct.unpack_from("<i", data, 0x14)[0],
            "wood": struct.unpack_from("<i", data, 0x18)[0],
            "reserved": struct.unpack_from("<i", data, 0x1C)[0],
            "count": struct.unpack_from("<h", data, 0x200A)[0],
            "used": struct.unpack_from("<h", data, 0x200C)[0],
            "count_cap": struct.unpack_from("<h", data, 0x2010)[0],
            "cap": struct.unpack_from("<h", data, 0x2012)[0],
            "controller_opcode": struct.unpack_from(
                "<h", data, runtime_driver.G4_CONTROLLER_OPCODE_OFFSET)[0],
            "controller_argument": struct.unpack_from(
                "<h", data, runtime_driver.G4_CONTROLLER_ARGUMENT_OFFSET)[0],
            "ai_groups": runtime_driver.decode_g4_groups(data),
        })

    exists = struct.unpack(f"<{capacity}h", exists_bytes)
    units = []
    for slot, active in enumerate(exists):
        if not active:
            continue
        offset = slot * 0x758
        unit = pool[offset:offset + 0x758]
        units.append({
            "slot": slot, "type": unit[0x8D], "owner": unit[0x8E],
            "internal_id": struct.unpack_from(
                "<i", unit, runtime_driver.G1_UNIT_INTERNAL_ID_OFFSET)[0],
            "hp": struct.unpack_from("<i", unit, 0x0B4)[0],
            "command": struct.unpack_from("<h", unit, 0x290)[0],
            "production_type": struct.unpack_from("<i", unit, 0x320)[0],
            "progress": struct.unpack_from("<i", unit, 0x1F8)[0],
            "x": struct.unpack_from("<h", unit, runtime_driver.G1_UNIT_X_OFFSET)[0],
            "y": struct.unpack_from("<h", unit, runtime_driver.G1_UNIT_Y_OFFSET)[0],
        })
    return {"ps": ps_before, "tick": tick_before, "players": players, "units": units}


def _read_batched_scene(pid: int, read_memory: Callable[[int, int], bytes]) -> dict[str, Any]:
    """Read the bounded original pool in a few bulk reads, bracketed by sim state."""
    started = time.monotonic_ns()
    ps_before = struct.unpack("<i", read_memory(0x004ED818, 4))[0]
    tick_before = _read_sim_tick(pid)
    camera_before = runtime_env._read_camera(read_memory)
    capacity, unit_base, exists_base = runtime_driver.STOCK_POOL
    player_bytes = read_memory(0x00956770, 8 * runtime_driver.PLAYER_STRUCT_SIZE)
    exists_bytes = read_memory(exists_base, capacity * 2)
    pool = read_memory(unit_base, capacity * 0x758)
    state = _decode_batched_scene(ps_before, tick_before, camera_before,
                                  player_bytes, exists_bytes, pool)
    camera_after = runtime_env._read_camera(read_memory)
    tick_after = _read_sim_tick(pid)
    ps_after = struct.unpack("<i", read_memory(0x004ED818, 4))[0]
    finished = time.monotonic_ns()
    coherent = (ps_before == ps_after == 3 and tick_before == tick_after
                and camera_before == camera_after)
    return {
        "status": "PASS" if coherent else "INCOHERENT",
        "sim_tick_before": tick_before, "state_sim_tick": tick_before,
        "sim_tick_after": tick_after,
        "program_state_before": ps_before, "program_state_after": ps_after,
        "camera_before": camera_before, "camera_after": camera_after,
        "monotonic_before_ns": started, "monotonic_after_ns": finished,
        "read_duration_ms": (finished - started) / 1_000_000,
        "state": state,
    }


def _read_inprocess_scene_snapshot(
    path: Path, *, expected_tick: int, expected_run_id: str,
) -> dict[str, Any]:
    """Validate and decode one atomically published update-return snapshot."""
    capacity, _unit_base, _exists_base = runtime_driver.STOCK_POOL
    lengths = (4, 4, 8, 8 * runtime_driver.PLAYER_STRUCT_SIZE,
               capacity * 2, capacity * 0x758)
    expected_size = SNAPSHOT_HEADER.size + sum(lengths)
    try:
        raw = path.read_bytes()
    except OSError as exc:
        return {"status": "INVALID", "source": "in_process_update_return",
                "target_tick": expected_tick, "reason": f"snapshot unavailable: {exc}"}
    if len(raw) != expected_size:
        return {"status": "INVALID", "source": "in_process_update_return",
                "target_tick": expected_tick, "actual_size": len(raw),
                "expected_size": expected_size, "reason": "snapshot size mismatch"}
    (magic, version, header_size, pid, thread_id, callsite, tick_before,
     tick_after, sequence, flags, qpc, run_raw) = SNAPSHOT_HEADER.unpack_from(raw)
    run_id = run_raw.split(b"\0", 1)[0].decode("ascii", errors="replace")
    checks = {
        "magic_version": magic == b"G1SNAP1\0" and version == 1 and header_size == SNAPSHOT_HEADER.size,
        "run_id": run_id == expected_run_id,
        "pid_thread": pid > 0 and thread_id > 0,
        "callsite": callsite in SNAPSHOT_CALLSITES,
        "target_tick": tick_after == expected_tick,
        "tick_advanced": tick_after != tick_before,
        "no_tick_jump": (flags & 1) == 0 and tick_after - tick_before == 1,
    }
    if not all(checks.values()):
        return {"status": "INVALID", "source": "in_process_update_return",
                "target_tick": expected_tick, "header": {
                    "magic": magic.hex(), "version": version, "header_size": header_size,
                    "pid": pid, "thread_id": thread_id, "callsite": callsite,
                    "tick_before": tick_before, "tick_after": tick_after,
                    "sequence": sequence, "flags": flags, "qpc": qpc, "run_id": run_id,
                }, "checks": checks}
    ranges = []
    offset = SNAPSHOT_HEADER.size
    for length in lengths:
        ranges.append(raw[offset:offset + length])
        offset += length
    ps = struct.unpack("<i", ranges[0])[0]
    tick = struct.unpack("<i", ranges[1])[0]
    camera = struct.unpack("<2i", ranges[2])
    if ps != 3 or tick != expected_tick:
        return {"status": "INVALID", "source": "in_process_update_return",
                "target_tick": expected_tick, "reason": "snapshot body state disagrees with header",
                "program_state": ps, "body_tick": tick}
    try:
        state = _decode_batched_scene(ps, tick, camera, *ranges[3:])
    except (ValueError, struct.error) as exc:
        return {"status": "INVALID", "source": "in_process_update_return",
                "target_tick": expected_tick, "reason": str(exc)}
    return {"status": "PASS", "source": "in_process_update_return",
            "target_tick": expected_tick,
            "sim_tick_before": tick_before, "state_sim_tick": tick,
            "sim_tick_after": tick_after, "camera_before": list(camera),
            "camera_after": list(camera), "state": state,
            "snapshot_path": str(path), "snapshot_sha256": hashlib.sha256(raw).hexdigest(),
            "header": {"pid": pid, "thread_id": thread_id, "callsite": callsite,
                       "tick_before": tick_before, "tick_after": tick_after,
                       "sequence": sequence, "flags": flags, "qpc": qpc,
                       "run_id": run_id}, "checks": checks}


def _wait_inprocess_scene_snapshot(
    path: Path, *, expected_tick: int, expected_run_id: str,
    timeout: float = 20.0,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    last: dict[str, Any] = {"status": "INVALID", "reason": "snapshot not observed"}
    while time.monotonic() < deadline:
        if path.exists():
            last = _read_inprocess_scene_snapshot(
                path, expected_tick=expected_tick, expected_run_id=expected_run_id)
            if last.get("status") == "PASS" or "size mismatch" not in str(last.get("reason", "")):
                return last
        time.sleep(0.01)
    return last


def _scene_owner_count_invariant(state: Mapping[str, Any]) -> bool:
    players = state.get("players")
    units = state.get("units")
    if not isinstance(players, list) or len(players) != 8 or not isinstance(units, list):
        return False
    counts = {owner: 0 for owner in range(8)}
    for unit in units:
        if not isinstance(unit, Mapping) or unit.get("owner") not in counts:
            return False
        counts[unit["owner"]] += 1
    return all(isinstance(player, Mapping) and player.get("owner") == owner
               and player.get("count") == counts[owner]
               for owner, player in enumerate(players))


def _load_completed_state_reference(path: Path) -> dict[int, Mapping[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    lane = data.get("lane_results", {}).get("baselineA", {})
    checkpoints = lane.get("scroll_phase_diagnostic", {}).get("checkpoints", [])
    reference: dict[int, Mapping[str, Any]] = {}
    for checkpoint in checkpoints:
        tick = checkpoint.get("tick")
        snapshot = checkpoint.get("snapshot", {})
        state = snapshot.get("state")
        if isinstance(tick, int) and isinstance(state, Mapping):
            reference[tick] = state
    if set(reference) != set(SCROLL_PHASE_TICK_PLAN.values()):
        raise ValueError("completed-state reference does not contain all five fixed ticks")
    return reference


def _snapshot_with_live_read(
    pid: int, read_memory: Callable[[int, int], bytes], path: Path,
    *, target_tick: int, run_id: str,
) -> dict[str, Any]:
    snapshot = _wait_inprocess_scene_snapshot(
        path, expected_tick=target_tick, expected_run_id=run_id)
    if snapshot.get("status") != "PASS":
        return snapshot
    live = _read_batched_scene(pid, read_memory)
    snapshot = dict(snapshot)
    snapshot["live_scene_snapshot"] = live
    snapshot["live_vs_inprocess_diff"] = (
        _scene_diff(snapshot["state"], live["state"])
        if live.get("status") == "PASS" else None
    )
    return snapshot


def _rice_phase_observation(events: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Validate read-only rice-watch and player-phase events without inferring a boundary."""
    entries: dict[tuple[int, int], Mapping[str, Any]] = {}
    matched: list[dict[str, Any]] = []
    writers: list[Mapping[str, Any]] = []
    invalid: list[str] = []
    last_seq = 0
    for event in events:
        seq = event.get("seq")
        if not isinstance(seq, int) or seq <= last_seq:
            invalid.append("event sequence missing or non-monotonic")
        else:
            last_seq = seq
        kind = event.get("event")
        thread = event.get("thread_global_num")
        tick = event.get("tick")
        if kind in {"simulation_update_enter", "simulation_update_return"}:
            if not isinstance(thread, int) or not isinstance(tick, int):
                invalid.append(f"{kind} missing thread or tick")
                continue
            key = (thread, tick)
            if kind == "simulation_update_enter":
                if key in entries:
                    invalid.append("duplicate simulation update entry on same thread and tick")
                entries[key] = event
            elif key in entries:
                matched.append({"thread_global_num": thread, "tick": tick,
                                "phase_status": "VALID_OBSERVED",
                                "entry_seq": entries[key].get("seq"), "return_seq": seq,
                                "rice_at_return": event.get("rice")})
                del entries[key]
            else:
                invalid.append("simulation update return has no matching entry")
        elif kind == "rice_write":
            writers.append(event)

    if entries:
        invalid.append("simulation update entry has no return")
    ordered_phases = sorted(matched, key=lambda item: item["entry_seq"])
    missed_ticks = [
        {"previous_tick": previous["tick"], "next_tick": current["tick"]}
        for previous, current in zip(ordered_phases, ordered_phases[1:])
        if current["tick"] != previous["tick"] + 1
    ]
    if missed_ticks:
        invalid.append("simulation update tick sequence has a gap")
    if not writers:
        invalid.append("no rice writer observed in diagnostic window")
    for event in writers:
        if (not isinstance(event.get("thread_global_num"), int)
                or not isinstance(event.get("pc_after_write"), int)
                or not isinstance(event.get("writer_instruction_address"), int)
                or event.get("writer_instruction_bytes") != "894114"
                or not isinstance(event.get("old_rice"), int)
                or not isinstance(event.get("new_rice"), int)
                or event.get("old_rice") == event.get("new_rice")):
            invalid.append("rice writer event missing exact thread, store instruction, or old/new value")

    writer_threads = sorted({event["thread_global_num"] for event in writers
                             if isinstance(event.get("thread_global_num"), int)})
    return {
        "status": "PASS" if matched and not invalid else "INCONCLUSIVE",
        "phase_status": "VALID_OBSERVED" if matched and not invalid else "INVALID_OR_INCOMPLETE",
        "phase_criterion": "matching 0x41C8CE tick-published entry and 0x41C961 update return on same thread and tick",
        "completed_simulation_update_observations": matched,
        "missed_phase_ticks": missed_ticks,
        "rice_writer_event_count": len(writers),
        "rice_writer_threads": writer_threads,
        "rice_writer_thread_status": (
            "OBSERVED_SINGLE_THREAD" if len(writer_threads) == 1 else
            "OBSERVED_MULTIPLE_THREADS" if len(writer_threads) > 1 else "MISSING"
        ),
        "rice_writer_events": list(writers),
        "invalid_reasons": invalid,
        "stable_tick_is_completion_proof": False,
        "post_call_address_is_approved_boundary": False,
        "all_writer_quiescence_proven": False,
    }


def _rice_phase_target_tick(loaded_tick: int) -> int:
    """Choose an owner6 phase tick after a small fixed warmup."""
    minimum = loaded_tick + 64
    return minimum + ((6 - minimum % 8) % 8)


def _rice_trace_gdb_script(pid: int, control: Path, duration: float, target_tick: int) -> str:
    """Create a bounded GDB observer; it never writes target memory."""
    return f'''\
import gdb, json, os, struct, time
CONTROL = {str(control)!r}
EVENTS = os.path.join(CONTROL, "rice-writer-events.jsonl")
SUMMARY = os.path.join(CONTROL, "rice-writer-summary.json")
ARMED = os.path.join(CONTROL, "armed.json")
PAUSED = os.path.join(CONTROL, "paused.json")
RELEASE = os.path.join(CONTROL, "release.flag")
DEADLINE = time.time() + {float(duration)!r}
TARGET_TICK = {int(target_tick)}
RICE = 0x0096C7EC
TICK = 0x008924B8
events = []
seq = 0
last_rice = None
initial_rice = None
phase_open = {{}}
persisted = 0

def read_u32(address):
    return struct.unpack("<I", bytes(gdb.selected_inferior().read_memory(address, 4)))[0]

def read_i32(address):
    return struct.unpack("<i", bytes(gdb.selected_inferior().read_memory(address, 4)))[0]

def add(kind, **fields):
    global seq
    seq += 1
    thread = gdb.selected_thread()
    record = {{"seq": seq, "event": kind, "time_ns": time.monotonic_ns(),
              "thread_global_num": thread.global_num if thread else None,
              "thread_ptid": list(thread.ptid) if thread else None,
              "tick": read_u32(TICK)}}
    record.update(fields)
    events.append(record)
    if seq % 128 == 0:
        flush_events()

def flush_events():
    global persisted
    if persisted >= len(events):
        return
    with open(EVENTS, "a", encoding="utf-8") as handle:
        for record in events[persisted:]:
            handle.write(json.dumps(record, sort_keys=True) + "\\n")
        handle.flush()
    persisted = len(events)

class Phase(gdb.Breakpoint):
    def __init__(self, address, entering):
        super().__init__("*0x%x" % address, gdb.BP_HARDWARE_BREAKPOINT)
        self.entering = entering
    def stop(self):
        if time.time() >= DEADLINE:
            return True
        thread = gdb.selected_thread()
        key = thread.global_num if thread else -1
        if self.entering:
            phase_open[key] = read_u32(TICK)
            add("simulation_update_enter", address=hex(int(gdb.selected_frame().pc())),
                phase_tick=phase_open[key])
        else:
            tick = read_u32(TICK)
            if key in phase_open:
                add("simulation_update_return", address=hex(int(gdb.selected_frame().pc())),
                    phase_tick=phase_open.pop(key), rice=read_i32(RICE))
                if tick == TARGET_TICK:
                    with open(PAUSED, "w", encoding="utf-8") as handle:
                        json.dump({{"status": "PAUSED_AT_PHASE_RETURN", "tick": tick,
                                   "thread_global_num": key, "rice": read_i32(RICE),
                                   "all_stop_mode": not bool(gdb.parameter("non-stop"))}}, handle)
                    return True
            else:
                add("simulation_update_return_unmatched", address=hex(int(gdb.selected_frame().pc())),
                    rice=read_i32(RICE))
        return False

class PlayerPhase(gdb.Breakpoint):
    def __init__(self):
        super().__init__("*0x0041cb40", gdb.BP_HARDWARE_BREAKPOINT)
    def stop(self):
        if time.time() >= DEADLINE:
            return True
        add("player_phase_enter", address=hex(int(gdb.selected_frame().pc())),
            outer_phase_tick=phase_open.get(gdb.selected_thread().global_num))
        return False

class RiceWatch(gdb.Breakpoint):
    def __init__(self):
        super().__init__("*(int*)0x%x" % RICE, gdb.BP_WATCHPOINT, gdb.WP_WRITE)
    def stop(self):
        if time.time() >= DEADLINE:
            return True
        global last_rice
        new = read_i32(RICE)
        pc = int(gdb.selected_frame().pc()) & 0xffffffff
        try:
            instruction = gdb.execute("x/i $pc-8", to_string=True).strip()
        except Exception as exc:
            instruction = "unavailable: " + repr(exc)
        try:
            surrounding = bytes(gdb.selected_inferior().read_memory(pc - 8, 16)).hex()
        except Exception:
            surrounding = None
        try:
            store_bytes = bytes(gdb.selected_inferior().read_memory(pc - 3, 3)).hex()
        except Exception:
            store_bytes = None
        add("rice_write", pc_after_write=pc, instruction_near_pc=instruction,
            code_bytes_before_pc=surrounding,
            writer_instruction_address=pc - 3 if store_bytes == "894114" else None,
            writer_instruction_bytes=store_bytes, old_rice=last_rice, new_rice=new,
            phase_tick=phase_open.get(gdb.selected_thread().global_num))
        last_rice = new
        return False

try:
    last_rice = read_i32(RICE)
    initial_rice = last_rice
    entry = Phase(0x0041C8CE, True)
    player_phase = PlayerPhase()
    returned = Phase(0x0041C961, False)
    watch = RiceWatch()
    with open(ARMED, "w", encoding="utf-8") as handle:
        json.dump({{"armed": True, "pid": {pid}, "rice_address": hex(RICE),
                   "initial_rice": last_rice, "phase_entry": hex(0x0041C8CE),
                   "player_phase_entry": hex(0x0041CB40),
                   "observed_return_address": hex(0x0041C961),
                   "return_is_approved_boundary": False,
                   "all_stop_mode": not bool(gdb.parameter("non-stop")),
                   "software_breakpoints": False, "target_tick": TARGET_TICK}}, handle)
    while time.time() < DEADLINE:
        try:
            gdb.execute("continue")
        except gdb.error as exc:
            if "exited" in str(exc).lower():
                break
            raise
        if os.path.exists(PAUSED):
            while not os.path.exists(RELEASE):
                time.sleep(0.01)
            break
    summary = {{"schema": "syw2plus.g1-rice-writer-trace.v1", "status": "CAPTURED",
               "event_count": len(events), "unmatched_phase_threads": sorted(phase_open),
               "initial_rice": initial_rice, "return_is_approved_boundary": False}}
except Exception as exc:
    summary = {{"schema": "syw2plus.g1-rice-writer-trace.v1", "status": "ERROR",
               "error": repr(exc), "event_count": len(events)}}
finally:
    try:
        flush_events()
    except Exception:
        pass
    with open(SUMMARY, "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
    try:
        gdb.execute("detach")
    except Exception:
        pass
'''


def _scroll_raw_identity_errors(events: Sequence[Mapping[str, Any]], *,
                               expected_pid: int) -> list[str]:
    """Validate the run-local event envelope and exact pre-tick return identity."""
    invalid: list[str] = []
    branches: dict[int, Mapping[str, Any]] = {}
    last_seq = 0
    for event in events:
        if not isinstance(event, Mapping):
            invalid.append("raw event is not an object")
            continue
        seq = event.get("seq")
        if not isinstance(seq, int) or isinstance(seq, bool) or seq != last_seq + 1:
            invalid.append("raw event sequence missing, gapped, or non-monotonic")
        if isinstance(seq, int) and not isinstance(seq, bool):
            last_seq = seq
        ptid = event.get("thread_ptid")
        if (event.get("inferior_pid") != expected_pid
                or not isinstance(event.get("thread_global_num"), int)
                or isinstance(event.get("thread_global_num"), bool)
                or not isinstance(ptid, list) or len(ptid) != 3
                or any(not isinstance(part, int) or isinstance(part, bool) for part in ptid)
                or ptid[0] != expected_pid):
            invalid.append("raw event invocation identity missing or mismatched")
        kind = event.get("event")
        if kind == "pre_tick_branch":
            if (event.get("branch_taken") is True and isinstance(seq, int)
                    and not isinstance(seq, bool)):
                branches[seq] = event
        elif kind == "simulation_update_no_update_return":
            branch_seq = event.get("attributed_branch_seq")
            branch = branches.pop(branch_seq, None) if isinstance(branch_seq, int) else None
            identity = ("inferior_pid", "thread_global_num", "thread_ptid", "call_id", "tick")
            if (branch is None or event.get("branch_taken") is not True
                    or event.get("branch_address") != branch.get("address")
                    or any(event.get(field) != branch.get(field) for field in identity)):
                invalid.append("no-update return branch invocation identity mismatch")
    if branches:
        invalid.append("taken pre-tick branch has no exact no-update return")
    return invalid


def _scroll_phase_observation(events: Sequence[Mapping[str, Any]],
                              checkpoints: Sequence[Mapping[str, Any]], *,
                              expected_pid: int, expected_ticks: Sequence[int]) -> dict[str, Any]:
    """Validate exact same-thread entry/return and stopped-thread census per checkpoint."""
    invalid: list[str] = _scroll_raw_identity_errors(events, expected_pid=expected_pid)
    phases: dict[tuple[str, int], Mapping[str, Any]] = {}
    pre_tick_branches: dict[str, list[Mapping[str, Any]]] = {}
    matched: dict[int, dict[str, Any]] = {}
    last_seq = 0
    for event in events:
        seq = event.get("seq")
        if not isinstance(seq, int) or seq <= last_seq:
            invalid.append("event sequence missing or non-monotonic")
            continue
        last_seq = seq
        ptid = event.get("thread_ptid")
        if (event.get("inferior_pid") != expected_pid or not isinstance(thread := event.get("thread_global_num"), int)
                or not isinstance(ptid, list) or len(ptid) != 3
                or not all(isinstance(part, int) for part in ptid) or ptid[0] != expected_pid):
            invalid.append("event inferior identity mismatch")
        kind, tick = event.get("event"), event.get("tick")
        if kind in {"simulation_call_overlap", "simulation_update_entry_identity_missing",
                    "simulation_update_duplicate_entry", "pre_tick_branch_identity_missing"}:
            invalid.append(f"observer call lifecycle invalid: {kind}")
            continue
        if kind == "pre_tick_branch":
            call_id = event.get("call_id")
            if not isinstance(call_id, str) or event.get("branch_taken") not in {True, False}:
                invalid.append("pre-tick branch lacks call identity or branch outcome")
            elif event.get("branch_taken"):
                pre_tick_branches.setdefault(call_id, []).append(event)
            continue
        if kind == "simulation_update_no_update_return":
            call_id = event.get("call_id")
            branches = pre_tick_branches.get(call_id, []) if isinstance(call_id, str) else []
            branch_index = next((index for index, branch in enumerate(branches)
                                 if branch.get("seq") == event.get("attributed_branch_seq")
                                 and branch.get("address") == event.get("branch_address")
                                 and branch.get("tick") == tick
                                 and branch.get("thread_global_num") == thread), None)
            if branch_index is None:
                invalid.append("no-update return lacks observed taken pre-tick branch")
            else:
                branches.pop(branch_index)
            continue
        if kind not in {"simulation_update_enter", "simulation_update_return",
                        "simulation_update_return_unmatched"}:
            continue
        call_id = event.get("call_id")
        if not isinstance(thread, int) or not isinstance(tick, int) or not isinstance(call_id, str) or not call_id:
            invalid.append(f"{kind} missing thread, tick, or call identity")
            continue
        key = (call_id, tick)
        if kind == "simulation_update_enter":
            if key in phases:
                invalid.append("duplicate simulation update entry on same call and tick")
            phases[key] = event
        elif kind == "simulation_update_return_unmatched":
            invalid.append("simulation update return has no matching entry or pre-tick branch")
        elif key not in phases:
            invalid.append("simulation update return has no matching entry")
        else:
            entry = phases.pop(key)
            if any(entry.get(field) != event.get(field) for field in
                   ("inferior_pid", "thread_global_num", "thread_ptid")):
                invalid.append("simulation update entry/return identity mismatch")
            if event.get("phase_tick") != tick or entry.get("phase_tick") != tick:
                invalid.append("simulation update phase tick does not match checkpoint tick")
            if tick in matched:
                invalid.append("duplicate completed simulation phase at target tick")
            matched[tick] = {"thread_global_num": thread, "thread_ptid": ptid,
                             "inferior_pid": expected_pid, "call_id": call_id, "tick": tick,
                             "entry_seq": entry.get("seq"), "return_seq": seq,
                             "entry_before_return": entry.get("seq", 0) < seq}
    if phases:
        invalid.append("simulation update entry has no return")
    if any(pre_tick_branches.values()):
        invalid.append("taken pre-tick branch has no attributed no-update return")

    checkpoint_by_tick = {item.get("tick"): item for item in checkpoints
                          if isinstance(item.get("tick"), int)}
    if list(expected_ticks) != [item.get("tick") for item in checkpoints]:
        invalid.append("checkpoint order or schedule mismatch")
    for tick in expected_ticks:
        phase = matched.get(tick)
        checkpoint = checkpoint_by_tick.get(tick)
        if phase is None or checkpoint is None:
            invalid.append(f"missing completed phase checkpoint at tick {tick}")
            continue
        if phase["entry_before_return"] is not True:
            invalid.append(f"phase entry/return order invalid at tick {tick}")
        pause = checkpoint.get("pause", {})
        census = pause.get("threads")
        if (pause.get("status") != "PAUSED_AT_PHASE_RETURN"
                or pause.get("tick") != tick
                or pause.get("inferior_pid") != expected_pid
                or pause.get("thread_global_num") != phase["thread_global_num"]
                or pause.get("thread_ptid") != phase["thread_ptid"]
                or pause.get("call_id") != phase["call_id"]
                or not isinstance(pause.get("nonce"), str) or not pause.get("nonce")
                or not isinstance(pause.get("run_nonce"), str) or not pause.get("run_nonce")
                or pause.get("all_stop_mode") is not True):
            invalid.append(f"invalid or stale phase pause at tick {tick}")
        if pause.get("phase_context_quiescent") is not True or pause.get("unresolved_phase_calls") != []:
            invalid.append(f"unresolved simulation phase context at tick {tick}")
        if not isinstance(census, list) or not census:
            invalid.append(f"missing complete thread census at tick {tick}")
        elif (not pause.get("thread_census_complete") or any(
              not isinstance(row, Mapping) or row.get("is_running") is not False
              or row.get("inferior_pid") != expected_pid
              or not isinstance(row.get("global_num"), int)
              or not isinstance(row.get("ptid"), list) or len(row["ptid"]) != 3
              or row["ptid"][0] != expected_pid for row in census)
              or len({(row.get("inferior_pid"), row.get("global_num"), tuple(row.get("ptid", [])))
                      for row in census if isinstance(row, Mapping)}) != len(census)
              or not any(row.get("global_num") == phase["thread_global_num"]
                         and row.get("ptid") == phase["thread_ptid"] for row in census
                         if isinstance(row, Mapping))):
            invalid.append(f"running or incomplete thread census at tick {tick}")
        snap = checkpoint.get("snapshot", {})
        if (snap.get("status") != "PASS" or snap.get("sim_tick_before") != tick
                or snap.get("sim_tick_after") != tick):
            invalid.append(f"incoherent full-state snapshot at tick {tick}")
        release = checkpoint.get("release", {})
        ack = checkpoint.get("ack", {})
        if (release.get("nonce") != pause.get("nonce") or release.get("run_nonce") != pause.get("run_nonce")
                or release.get("tick") != tick
                or release.get("status") != "RELEASE"):
            invalid.append(f"stale or mismatched pause release at tick {tick}")
        if (ack.get("nonce") != pause.get("nonce") or ack.get("tick") != tick
                or ack.get("run_nonce") != pause.get("run_nonce")
                or ack.get("status") != "CONSUMED" or ack.get("tick_after") != tick
                or ack.get("census_stable") is not True
                or ack.get("all_threads_stopped") is not True
                or ack.get("phase_context_quiescent") is not True
                or ack.get("threads_after") != census):
            invalid.append(f"missing or mismatched consumed acknowledgment at tick {tick}")
    return {
        "status": "PASS" if not invalid else "INVALID",
        "completed_phases": [matched[tick] for tick in expected_ticks if tick in matched],
        "checkpoint_ticks": list(expected_ticks),
        "invalid_reasons": invalid,
        "all_stop_mode_alone_is_sufficient": False,
        "all_writer_quiescence_proven": not invalid,
    }


def _atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    """Publish a complete control record atomically in its destination directory."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(temporary)


def _scroll_pause_is_valid(pause: Mapping[str, Any], *, expected_pid: int,
                           expected_tick: int, run_nonce: str) -> tuple[bool, str]:
    """Validate pause identity and a complete stopped census before any read or input."""
    threads = pause.get("threads")
    required_identity = (isinstance(pause.get("nonce"), str) and bool(pause.get("nonce"))
                         and pause.get("run_nonce") == run_nonce
                         and pause.get("tick") == expected_tick
                         and pause.get("inferior_pid") == expected_pid
                         and isinstance(pause.get("thread_global_num"), int)
                         and isinstance(pause.get("thread_ptid"), list)
                         and isinstance(pause.get("call_id"), str))
    if not required_identity:
        return False, "pause nonce, tick, inferior, thread, or call identity mismatch"
    if (pause.get("status") != "PAUSED_AT_PHASE_RETURN" or pause.get("all_stop_mode") is not True
            or pause.get("thread_census_complete") is not True
            or not isinstance(threads, list) or not threads
            or any(not isinstance(row, Mapping) or row.get("inferior_pid") != expected_pid
                   or row.get("is_running") is not False
                   or not isinstance(row.get("global_num"), int)
                   or not isinstance(row.get("ptid"), list) or len(row["ptid"]) != 3
                   or row["ptid"][0] != expected_pid for row in threads)
            or len({(row.get("inferior_pid"), row.get("global_num"), tuple(row.get("ptid", [])))
                    for row in threads if isinstance(row, Mapping)}) != len(threads)
            or not any(row.get("global_num") == pause.get("thread_global_num")
                       and row.get("ptid") == pause.get("thread_ptid") for row in threads
                       if isinstance(row, Mapping))
            or pause.get("phase_context_quiescent") is not True
            or pause.get("unresolved_phase_calls") != []):
        return False, "pause lacks complete all-stopped census or phase quiescence"
    return True, "PASS"


def _scroll_pause_matches_completed_phase(path: Path, pause: Mapping[str, Any]) -> tuple[bool, str]:
    """Bind a live pause to exactly one completed raw phase before reading or input."""
    try:
        events = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    except (OSError, ValueError) as exc:
        return False, f"phase event stream unavailable: {exc}"
    expected_pid = pause.get("inferior_pid")
    if not isinstance(expected_pid, int) or isinstance(expected_pid, bool):
        return False, "pause has no valid inferior identity for raw phase stream"
    identity_errors = _scroll_raw_identity_errors(events, expected_pid=expected_pid)
    if identity_errors:
        return False, "; ".join(identity_errors)
    call_id, tick = pause.get("call_id"), pause.get("tick")
    matches = [event for event in events if isinstance(event, Mapping)
               and event.get("call_id") == call_id and event.get("phase_tick") == tick
               and event.get("event") in {"simulation_update_enter", "simulation_update_return"}]
    enters = [event for event in matches if event.get("event") == "simulation_update_enter"]
    returns = [event for event in matches if event.get("event") == "simulation_update_return"]
    if len(enters) != 1 or len(returns) != 1:
        return False, "pause has no unique completed phase entry/return"
    entry, returned = enters[0], returns[0]
    identity = ("inferior_pid", "thread_global_num", "thread_ptid")
    if (not isinstance(entry.get("seq"), int) or not isinstance(returned.get("seq"), int)
            or entry["seq"] >= returned["seq"]
            or any(entry.get(field) != returned.get(field) for field in identity)
            or any(returned.get(field) != pause.get(field) for field in identity)
            or returned.get("call_id") != pause.get("call_id")
            or returned.get("tick") != tick):
        return False, "pause identity does not match completed phase"
    return True, "PASS"


def _scroll_live_checkpoint_preflight(path: Path, pause: Mapping[str, Any], *,
                                     expected_pid: int, expected_tick: int,
                                     run_nonce: str) -> tuple[bool, str]:
    """Reject an invalid pause or raw prefix before the live consumer reads or sends input."""
    valid, reason = _scroll_pause_is_valid(
        pause, expected_pid=expected_pid, expected_tick=expected_tick, run_nonce=run_nonce,
    )
    if not valid:
        return False, reason
    return _scroll_pause_matches_completed_phase(path, pause)


def _scroll_wait_for_ack(path: Path, *, nonce: str, tick: int, run_nonce: str,
                         expected_threads: Sequence[Mapping[str, Any]],
                         timeout: float = 15.0) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if path.is_file():
            try:
                ack = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                time.sleep(0.01)
                continue
            if (ack.get("status") in {"CONSUMED", "CLEANUP_CONSUMED"}
                    and ack.get("nonce") == nonce and ack.get("tick") == tick
                    and ack.get("run_nonce") == run_nonce
                    and ack.get("tick_after") == tick
                    and ack.get("census_stable") is True
                    and ack.get("threads_after") == list(expected_threads)
                    and ack.get("all_threads_stopped") is True
                    and ack.get("phase_context_quiescent") is True):
                return ack
            raise ProbeError(f"stale or mismatched pause acknowledgment: {ack}")
        time.sleep(0.01)
    raise ProbeError(f"pause acknowledgment timeout for tick {tick} nonce {nonce}")


def _scroll_release_and_ack(release_path: Path, ack_path: Path, *, nonce: str, tick: int,
                            run_nonce: str, expected_threads: Sequence[Mapping[str, Any]],
                            status: str = "RELEASE",
                            timeout: float = 15.0) -> tuple[dict[str, Any], dict[str, Any]]:
    """Atomically release one exact pause and wait for its producer-consumed ack."""
    release = {"status": status, "nonce": nonce, "tick": tick, "run_nonce": run_nonce}
    _atomic_write_json(release_path, release)
    ack = _scroll_wait_for_ack(ack_path, nonce=nonce, tick=tick,
                               run_nonce=run_nonce, expected_threads=expected_threads,
                               timeout=timeout)
    return release, ack


def _scroll_checkpoint_state_diffs(
    reference: Sequence[Mapping[str, Any]], candidate: Sequence[Mapping[str, Any]],
    expected_ticks: Sequence[int],
) -> list[dict[str, Any]]:
    """Compare every captured player/unit field at each immutable checkpoint."""
    if len(reference) != len(candidate) or len(reference) != len(expected_ticks):
        return [{"status": "INVALID", "reason": "checkpoint count mismatch"}]
    diffs = []
    for left, right, tick in zip(reference, candidate, expected_ticks):
        if not isinstance(left, Mapping) or not isinstance(right, Mapping):
            diffs.append({"tick": tick, "invalid": True, "reason": "checkpoint record malformed"})
            continue
        left_snapshot = left.get("snapshot", {})
        right_snapshot = right.get("snapshot", {})
        left_snapshot = left_snapshot if isinstance(left_snapshot, Mapping) else {}
        right_snapshot = right_snapshot if isinstance(right_snapshot, Mapping) else {}
        if (left.get("tick") != tick or right.get("tick") != tick
                or left_snapshot.get("sim_tick_before") != tick
                or left_snapshot.get("sim_tick_after") != tick
                or right_snapshot.get("sim_tick_before") != tick
                or right_snapshot.get("sim_tick_after") != tick):
            diffs.append({"tick": tick, "invalid": True,
                          "reason": "checkpoint tick or snapshot tick mismatch"})
            continue
        diffs.append({"tick": tick, **_scene_diff(
            left_snapshot.get("state", {}), right_snapshot.get("state", {}))})
    return diffs


def _scroll_phase_lane_acceptance(
    lane: Mapping[str, Any], *, label: str, expected_ticks: Sequence[int],
    expected_inputs: Mapping[str, str],
) -> dict[str, Any]:
    """Require one complete, identity-safe baseline lane before staging a candidate."""
    diagnostic = lane.get("scroll_phase_diagnostic")
    diagnostic = diagnostic if isinstance(diagnostic, Mapping) else {}
    inputs = diagnostic.get("inputs")
    inputs = inputs if isinstance(inputs, list) else []
    checkpoints = diagnostic.get("checkpoints")
    checkpoints = checkpoints if isinstance(checkpoints, list) else []
    observed_ticks = [item.get("tick") for item in checkpoints if isinstance(item, Mapping)]
    input_keys = [item.get("key") for item in inputs if isinstance(item, Mapping)]
    expected_keys = ["DOWN", "RIGHT"]
    fixture = lane.get("fixture")
    fixture = fixture if isinstance(fixture, Mapping) else {}
    cleanup = lane.get("cleanup")
    cleanup = cleanup if isinstance(cleanup, Mapping) else {}
    snapshots = [item.get("snapshot") for item in checkpoints if isinstance(item, Mapping)]
    snapshot_states = [item.get("state") for item in snapshots if isinstance(item, Mapping)]
    observation = diagnostic.get("phase_observation")
    observation = observation if isinstance(observation, Mapping) else {}
    phases = observation.get("completed_phases")
    phases = phases if isinstance(phases, list) else []
    checkpoint_lifecycle_valid = len(checkpoints) == len(expected_ticks)
    pause_nonces: list[Any] = []
    run_nonces: list[Any] = []
    inferior_pids: list[Any] = []
    phase_by_tick = {phase.get("tick"): phase for phase in phases
                     if isinstance(phase, Mapping)}
    phase_call_ids = [phase.get("call_id") for phase in phases if isinstance(phase, Mapping)]
    if checkpoint_lifecycle_valid:
        for checkpoint, tick in zip(checkpoints, expected_ticks):
            if not isinstance(checkpoint, Mapping):
                checkpoint_lifecycle_valid = False
                break
            pause = checkpoint.get("pause")
            pause = pause if isinstance(pause, Mapping) else {}
            snapshot = checkpoint.get("snapshot")
            snapshot = snapshot if isinstance(snapshot, Mapping) else {}
            release = checkpoint.get("release")
            release = release if isinstance(release, Mapping) else {}
            ack = checkpoint.get("ack")
            ack = ack if isinstance(ack, Mapping) else {}
            census = pause.get("threads")
            phase = phase_by_tick.get(tick, {})
            phase_thread = phase.get("thread_global_num") if isinstance(phase, Mapping) else None
            if not (
                checkpoint.get("tick") == tick
                and pause.get("status") == "PAUSED_AT_PHASE_RETURN"
                and pause.get("tick") == tick
                and isinstance(pause.get("nonce"), str) and bool(pause.get("nonce"))
                and isinstance(pause.get("run_nonce"), str) and bool(pause.get("run_nonce"))
                and isinstance(pause.get("inferior_pid"), int)
                and isinstance(pause.get("thread_global_num"), int)
                and isinstance(pause.get("thread_ptid"), list)
                and pause.get("call_id") == phase.get("call_id")
                and pause.get("thread_global_num") == phase.get("thread_global_num")
                and pause.get("thread_ptid") == phase.get("thread_ptid")
                and pause.get("inferior_pid") == phase.get("inferior_pid")
                and isinstance(phase.get("call_id"), str) and bool(phase.get("call_id"))
                and phase.get("entry_before_return") is True
                and isinstance(phase.get("entry_seq"), int)
                and isinstance(phase.get("return_seq"), int)
                and phase.get("entry_seq") < phase.get("return_seq")
                and pause.get("all_stop_mode") is True
                and pause.get("phase_context_quiescent") is True
                and pause.get("unresolved_phase_calls") == []
                and pause.get("thread_census_complete") is True
                and isinstance(census, list) and bool(census)
                and all(isinstance(thread, Mapping) and thread.get("is_running") is False
                        and thread.get("inferior_pid") == pause.get("inferior_pid")
                        and isinstance(thread.get("global_num"), int)
                        and isinstance(thread.get("ptid"), list) and len(thread["ptid"]) == 3
                        and thread["ptid"][0] == pause.get("inferior_pid")
                        for thread in census)
                and len({(thread.get("inferior_pid"), thread.get("global_num"),
                          tuple(thread.get("ptid", []))) for thread in census
                         if isinstance(thread, Mapping)}) == len(census)
                and any(thread.get("global_num") == phase_thread
                        and thread.get("ptid") == phase.get("thread_ptid")
                        for thread in census if isinstance(thread, Mapping))
                and snapshot.get("status") == "PASS"
                and snapshot.get("sim_tick_before") == tick
                and snapshot.get("sim_tick_after") == tick
                and release.get("status") == "RELEASE"
                and release.get("tick") == tick
                and release.get("nonce") == pause.get("nonce")
                and release.get("run_nonce") == pause.get("run_nonce")
                and ack.get("status") == "CONSUMED"
                and ack.get("tick") == tick and ack.get("tick_after") == tick
                and ack.get("nonce") == pause.get("nonce")
                and ack.get("run_nonce") == pause.get("run_nonce")
                and ack.get("census_stable") is True
                and ack.get("all_threads_stopped") is True
                and ack.get("phase_context_quiescent") is True
                and ack.get("threads_after") == census
            ):
                checkpoint_lifecycle_valid = False
                break
            pause_nonces.append(pause["nonce"])
            run_nonces.append(pause["run_nonce"])
            inferior_pids.append(pause["inferior_pid"])
    checkpoint_lifecycle_valid = checkpoint_lifecycle_valid and (
        len(set(pause_nonces)) == len(expected_ticks)
        and len(set(run_nonces)) == 1 and len(set(inferior_pids)) == 1
    )
    helper_hash = diagnostic.get("close_helper_sha256")
    bridge_hash = diagnostic.get("bridge_sha256")
    checks = {
        "lane_completed": lane.get("status") == "DIAGNOSTIC_ONLY",
        "variant_matches": diagnostic.get("variant") == (
            "candidate" if label == "candidate" else "baseline"
        ),
        "phase_pass": diagnostic.get("phase_observation", {}).get("status") == "PASS"
        if isinstance(diagnostic.get("phase_observation"), Mapping) else False,
        "phase_schedule_complete": (
            observation.get("checkpoint_ticks") == list(expected_ticks)
            and [phase.get("tick") for phase in phases if isinstance(phase, Mapping)]
            == list(expected_ticks)
            and observation.get("invalid_reasons") == []
            and observation.get("all_writer_quiescence_proven") is True
            and len(phase_call_ids) == len(expected_ticks)
            and all(isinstance(call_id, str) and bool(call_id) for call_id in phase_call_ids)
            and len(set(phase_call_ids)) == len(expected_ticks)
        ),
        "exact_checkpoint_ticks": observed_ticks == list(expected_ticks),
        "checkpoint_lifecycle_valid": checkpoint_lifecycle_valid,
        "complete_captured_states": (
            len(snapshots) == len(expected_ticks)
            and all(isinstance(snapshot, Mapping) and snapshot.get("status") == "PASS"
                    and isinstance(snapshot.get("state"), Mapping)
                    and isinstance(snapshot["state"].get("players"), list)
                    and isinstance(snapshot["state"].get("units"), list)
                    and bool(snapshot["state"]["players"])
                    and bool(snapshot["state"]["units"])
                    for snapshot in snapshots)
            and all(isinstance(state, Mapping) for state in snapshot_states)
        ),
        "exact_input_sequence": input_keys == expected_keys and [
            item.get("target_input_tick") for item in inputs if isinstance(item, Mapping)
        ] == [SCROLL_PHASE_TICK_PLAN["down_input_tick"],
              SCROLL_PHASE_TICK_PLAN["right_input_tick"]],
        "inputs_valid": len(inputs) == len(expected_keys) and all(
            isinstance(item, Mapping) and item.get("valid") is True
            and item.get("input_tick_before") == item.get("target_input_tick")
            and item.get("input_tick_after") == item.get("target_input_tick")
            and isinstance(item.get("receiver_keydown"), Mapping)
            and isinstance(item.get("receiver_keyup"), Mapping)
            and bool(item["receiver_keydown"].get("message"))
            and bool(item["receiver_keyup"].get("message"))
            for item in inputs
        ),
        "no_target_memory_writes": diagnostic.get("target_memory_writes") == 0,
        "protected_source_unchanged": lane.get("source_unchanged") is True,
        "source_identity_matches": lane.get("source_exe_sha256") == runtime_env.ORIGINAL_SHA256,
        "private_executable_matches": lane.get("private_exe_sha256") == runtime_env.ORIGINAL_SHA256,
        "fixture_identity_matches": (
            fixture.get("name") == SAVE_NAME
            and fixture.get("sha256") == SAVE_SHA256
            and fixture.get("synthetic") is False
        ),
        "cleanup_complete": (
            cleanup.get("ok") is True and cleanup.get("game_removed") is True
            and cleanup.get("prefix_processes_after") == []
        ),
        "helper_and_bridge_identified": (
            helper_hash == expected_inputs.get("close_helper_sha256")
            and bridge_hash == expected_inputs.get("bridge_sha256")
        ),
    }
    return {"status": "PASS" if all(checks.values()) else "HOLD", "checks": checks}


def _scroll_input_delivery_signature(value: Any) -> list[tuple[Any, ...]] | None:
    if not isinstance(value, list) or not value or not all(isinstance(item, Mapping) for item in value):
        return None
    return [(
        item.get("key"), item.get("target_input_tick"),
        item.get("receiver_keydown", {}).get("message")
        if isinstance(item.get("receiver_keydown"), Mapping) else None,
        item.get("receiver_keyup", {}).get("message")
        if isinstance(item.get("receiver_keyup"), Mapping) else None,
    ) for item in value]


def _scroll_expected_file_identities(bridge: Path, close_helper: Path) -> dict[str, str]:
    """Freeze all protected and generated file identities before diagnostic lanes start."""
    _, original_exe = runtime_env.validate_original_source(SOURCE)
    fixture = FIXTURE_SOURCE / "save" / SAVE_NAME
    expected = {
        "probe_sha256": _sha256(Path(__file__).resolve()),
        "test_sha256": _sha256(REPO / "tests" / "test_g1_saved_scene_probe.py"),
        "original_exe_sha256": _sha256(original_exe),
        "save_sha256": _sha256(fixture),
        "bridge_sha256": _sha256(bridge),
        "close_helper_sha256": _sha256(close_helper),
    }
    if expected["original_exe_sha256"] != runtime_env.ORIGINAL_SHA256:
        raise ProbeError("protected original executable identity mismatch")
    if expected["save_sha256"] != SAVE_SHA256:
        raise ProbeError("protected save fixture identity mismatch")
    return expected


def _scroll_file_identities_unchanged(bridge: Path, close_helper: Path,
                                      expected: Mapping[str, str]) -> bool:
    try:
        current = _scroll_expected_file_identities(bridge, close_helper)
    except (OSError, ProbeError, runtime_env.RuntimeSafetyError):
        return False
    return dict(current) == dict(expected)


def _run_scroll_phase_orchestration(
    *, run_lane: Callable[..., dict[str, Any]], runtime_root: Path,
    artifact_root: Path, bridge: Path, close_helper: Path,
) -> tuple[dict[str, Any], int]:
    """Accept both baseline controls and persist that decision before candidate execution."""
    expected_ticks = [SCROLL_PHASE_TICK_PLAN[name] for name in (
        "down_input_tick", "down_observation_tick", "right_input_tick",
        "right_observation_tick", "final_observation_tick")]
    lanes: dict[str, dict[str, Any]] = {}
    try:
        expected_inputs = _scroll_expected_file_identities(bridge, close_helper)
    except (OSError, ProbeError, runtime_env.RuntimeSafetyError) as exc:
        acceptance = {"status": "HOLD", "reason": f"input identity unavailable: {exc}"}
        artifact_root.mkdir(parents=True, exist_ok=True)
        _atomic_write_json(artifact_root / "baseline-control-acceptance.json", acceptance)
        pair = {"schema": "syw2plus.g1-scroll-phase-diagnostic.v1", "status": "HOLD",
                "scope": "observation-only; exact file identity unavailable",
                "fixed_tick_plan": dict(SCROLL_PHASE_TICK_PLAN),
                "control_acceptance": acceptance, "lane_results": {
                    "baselineA": {"status": "SKIP", "reason": acceptance["reason"]},
                    "baselineB": {"status": "SKIP", "reason": acceptance["reason"]},
                    "candidate": {"status": "SKIP", "candidate_calls": 0}},
                "candidate_staged": False}
        _atomic_write_json(artifact_root / "scroll-phase-diagnostic-result.json", pair)
        return pair, 2

    def execute(label: str, variant: str) -> dict[str, Any]:
        try:
            lane = run_lane(
                variant=variant, bridge=bridge,
                runtime_root=runtime_root / label,
                artifact_root=artifact_root / label,
                close_helper=close_helper,
                hd_source="scale2x" if variant == "candidate" else None,
                scroll_phase_diagnostic=True, lane_label=label,
                common_tick_plan=SCROLL_PHASE_TICK_PLAN,
            )
            if not isinstance(lane, Mapping):
                return {"status": "INVALID_LANE_RESULT", "variant": variant,
                        "lane_label": label, "error": "lane result is not an object"}
            return dict(lane)
        except Exception as exc:  # The persisted HOLD is the handoff evidence.
            return {"status": "LANE_EXCEPTION", "variant": variant,
                    "lane_label": label, "error": f"{type(exc).__name__}: {exc}"}

    lanes["baselineA"] = execute("baselineA", "baseline")
    lanes["baselineB"] = execute("baselineB", "baseline")
    controls = {
        label: _scroll_phase_lane_acceptance(
            lanes[label], label=label, expected_ticks=expected_ticks,
            expected_inputs=expected_inputs,
        ) for label in ("baselineA", "baselineB")
    }
    first_diag = lanes["baselineA"].get("scroll_phase_diagnostic", {})
    second_diag = lanes["baselineB"].get("scroll_phase_diagnostic", {})
    first_diag = first_diag if isinstance(first_diag, Mapping) else {}
    second_diag = second_diag if isinstance(second_diag, Mapping) else {}
    diffs = _scroll_checkpoint_state_diffs(
        first_diag.get("checkpoints", []) if isinstance(first_diag, Mapping) else [],
        second_diag.get("checkpoints", []) if isinstance(second_diag, Mapping) else [],
        expected_ticks,
    )
    complete_records_equal = len(diffs) == len(expected_ticks) and all(
        diff.get("invalid") is not True
        and not any(value for key, value in diff.items() if key != "tick")
        for diff in diffs
    )
    first_inputs = first_diag.get("inputs", []) if isinstance(first_diag, Mapping) else []
    second_inputs = second_diag.get("inputs", []) if isinstance(second_diag, Mapping) else []
    first_input_signature = _scroll_input_delivery_signature(first_inputs)
    second_input_signature = _scroll_input_delivery_signature(second_inputs)
    input_delivery_equal = (
        first_input_signature is not None
        and first_input_signature == second_input_signature
    )
    inputs_unchanged = _scroll_file_identities_unchanged(bridge, close_helper, expected_inputs)
    control_accepted = inputs_unchanged and all(item["status"] == "PASS" for item in controls.values()) \
        and complete_records_equal and input_delivery_equal
    acceptance = {
        "status": "PASS" if control_accepted else "HOLD",
        "frozen_file_identities": dict(expected_inputs),
        "file_identities_unchanged_before_candidate": inputs_unchanged,
        "controls": controls,
        "baselineA_baselineB_complete_records_equal": complete_records_equal,
        "baselineA_baselineB_input_delivery_equal": input_delivery_equal,
        "baselineA_baselineB_checkpoint_diffs": diffs,
    }
    # This durable barrier must exist before any candidate process can be started.
    _atomic_write_json(artifact_root / "baseline-control-acceptance.json", acceptance)
    if not control_accepted:
        lanes["candidate"] = {
            "status": "SKIP", "reason": "baseline controls were not accepted",
            "candidate_calls": 0,
        }
        pair = {
            "schema": "syw2plus.g1-scroll-phase-diagnostic.v1",
            "status": "HOLD",
            "scope": "observation-only; no target memory writes; not B-prime acceptance",
            "fixed_tick_plan": dict(SCROLL_PHASE_TICK_PLAN),
            "control_acceptance": acceptance,
            "lane_results": lanes,
            "candidate_staged": False,
        }
        _atomic_write_json(artifact_root / "scroll-phase-diagnostic-result.json", pair)
        return pair, 2

    if not _scroll_file_identities_unchanged(bridge, close_helper, expected_inputs):
        acceptance["status"] = "HOLD"
        acceptance["file_identities_unchanged_before_candidate"] = False
        _atomic_write_json(artifact_root / "baseline-control-acceptance.json", acceptance)
        lanes["candidate"] = {"status": "SKIP", "reason": "frozen input identity drift",
                              "candidate_calls": 0}
        pair = {"schema": "syw2plus.g1-scroll-phase-diagnostic.v1", "status": "HOLD",
                "scope": "observation-only; frozen input identity drift",
                "fixed_tick_plan": dict(SCROLL_PHASE_TICK_PLAN),
                "control_acceptance": acceptance, "lane_results": lanes,
                "candidate_staged": False}
        _atomic_write_json(artifact_root / "scroll-phase-diagnostic-result.json", pair)
        return pair, 2

    lanes["candidate"] = execute("candidate", "candidate")
    candidate = lanes["candidate"]
    candidate_acceptance = _scroll_phase_lane_acceptance(
        candidate, label="candidate", expected_ticks=expected_ticks,
        expected_inputs=expected_inputs,
    )
    candidate_inputs_unchanged = _scroll_file_identities_unchanged(
        bridge, close_helper, expected_inputs,
    )
    candidate_acceptance["frozen_file_identities_unchanged_after_candidate"] = candidate_inputs_unchanged
    if not candidate_inputs_unchanged:
        candidate_acceptance["status"] = "HOLD"
    candidate_diag = candidate.get("scroll_phase_diagnostic", {})
    candidate_diag = candidate_diag if isinstance(candidate_diag, Mapping) else {}
    candidate_inputs = candidate_diag.get("inputs", []) if isinstance(candidate_diag, Mapping) else []
    candidate_vs_control = _scroll_checkpoint_state_diffs(
        first_diag.get("checkpoints", []),
        candidate_diag.get("checkpoints", []) if isinstance(candidate_diag, Mapping) else [],
        expected_ticks,
    )
    candidate_input_signature = _scroll_input_delivery_signature(candidate_inputs)
    candidate_inputs_equal = (
        first_input_signature is not None
        and first_input_signature == candidate_input_signature
    )
    candidate_equal = (
        candidate_acceptance["status"] == "PASS" and candidate_inputs_unchanged
        and candidate_inputs_equal
        and len(candidate_vs_control) == len(expected_ticks)
        and all(diff.get("invalid") is not True
                and not any(value for key, value in diff.items() if key != "tick")
                for diff in candidate_vs_control)
    )
    pair = {
        "schema": "syw2plus.g1-scroll-phase-diagnostic.v1",
        "status": "PASS_BOUNDED_SCROLL_DIAGNOSTIC" if candidate_equal else "HOLD",
        "scope": "observation-only; no target memory writes; not B-prime acceptance",
        "fixed_tick_plan": dict(SCROLL_PHASE_TICK_PLAN),
        "control_acceptance": acceptance,
        "candidate_acceptance": candidate_acceptance,
        "candidate_comparison": {
            "complete_records_equal": candidate_equal,
            "input_delivery_equal": candidate_inputs_equal,
            "checkpoint_full_state_diffs": candidate_vs_control,
        },
        "lane_results": lanes,
        "candidate_staged": True,
    }
    _atomic_write_json(artifact_root / "scroll-phase-diagnostic-result.json", pair)
    return pair, 0 if candidate_equal else 2


def _scroll_phase_trace_gdb_script(pid: int, control: Path, target_ticks: Sequence[int],
                                   timeout: float, run_nonce: str) -> str:
    """Observe only exact scroll checkpoints; no target memory writes or data watches."""
    return f'''\
import gdb, json, os, time, uuid
CONTROL = {str(control)!r}
EVENTS = os.path.join(CONTROL, "phase-events.jsonl")
SUMMARY = os.path.join(CONTROL, "summary.json")
ARMED = os.path.join(CONTROL, "armed.json")
PAUSED = os.path.join(CONTROL, "paused.json")
RELEASE = os.path.join(CONTROL, "release.json")
ACK = os.path.join(CONTROL, "ack.json")
DEADLINE = time.time() + {float(timeout)!r}
TARGET_PID = {int(pid)}
TARGET_TICKS = {list(target_ticks)!r}
RUN_NONCE = {run_nonce!r}
TICK = 0x008924B8
events = []
seq = 0
phase_open = {{}}
call_contexts = {{}}
call_seq = 0
persisted = 0
pending_pause = None

def read_tick():
    return int.from_bytes(bytes(gdb.selected_inferior().read_memory(TICK, 4)), "little", signed=True)

def add(kind, **fields):
    global seq
    seq += 1
    thread = gdb.selected_thread()
    inferior = thread.inferior if thread else gdb.selected_inferior()
    record = {{"seq": seq, "event": kind, "time_ns": time.monotonic_ns(),
              "thread_global_num": thread.global_num if thread else None,
              "thread_ptid": list(thread.ptid) if thread else None,
              "inferior_pid": inferior.pid if inferior else None, "tick": read_tick()}}
    record.update(fields)
    events.append(record)
    flush_events()
    return record

def flush_events():
    global persisted
    if persisted >= len(events):
        return
    with open(EVENTS, "a", encoding="utf-8") as handle:
        for record in events[persisted:]:
            handle.write(json.dumps(record, sort_keys=True) + "\\n")
        handle.flush()
        os.fsync(handle.fileno())
    persisted = len(events)

def atomic_json(path, payload):
    temporary = path + "." + uuid.uuid4().hex + ".tmp"
    with open(temporary, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, sort_keys=True)
        handle.write("\\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)

def thread_key(thread):
    if thread is None:
        return None
    return (thread.global_num, tuple(thread.ptid))

def begin_call_context(thread, origin):
    global call_seq
    key = thread_key(thread)
    if key is None:
        return None
    call_seq += 1
    call_id = "%s:%s:call%d" % (key[0], key[1], call_seq)
    context = {{"call_id": call_id, "thread_global_num": thread.global_num,
               "thread_ptid": list(thread.ptid), "origin": origin,
               "branch_events": [], "taken_branches": [], "entered": None}}
    call_contexts[key] = context
    return context

def thread_census():
    inferior = gdb.selected_inferior()
    rows = []
    for thread in inferior.threads():
        rows.append({{"global_num": thread.global_num, "ptid": list(thread.ptid),
                     "inferior_pid": thread.inferior.pid, "is_running": thread.is_running()}})
    return rows

class Phase(gdb.Breakpoint):
    def __init__(self, address, entering):
        super().__init__("*0x%x" % address, gdb.BP_HARDWARE_BREAKPOINT)
        self.entering = entering
    def stop(self):
        global pending_pause
        if time.time() >= DEADLINE:
            return True
        thread = gdb.selected_thread()
        key = thread.global_num if thread else -1
        tick = read_tick()
        thread_id = thread_key(thread)
        if self.entering:
            context = call_contexts.get(thread_id) or begin_call_context(thread, "phase-entry")
            if context is None:
                add("simulation_update_entry_identity_missing", address=hex(int(gdb.selected_frame().pc())))
                return False
            call_id = context["call_id"]
            if context["entered"] is not None:
                add("simulation_update_duplicate_entry", call_id=call_id,
                    address=hex(int(gdb.selected_frame().pc())), phase_tick=tick)
                return False
            context["entered"] = {{"tick": tick, "thread": key}}
            phase_open[call_id] = {{"tick": tick, "thread": key}}
            add("simulation_update_enter", call_id=call_id,
                address=hex(int(gdb.selected_frame().pc())), phase_tick=tick)
            return False
        context = call_contexts.pop(thread_id, None)
        if context is None:
            add("simulation_update_return_unmatched", address=hex(int(gdb.selected_frame().pc())))
            return False
        call_id = context["call_id"]
        entered = phase_open.pop(call_id, None)
        if entered is None:
            branches = context["taken_branches"]
            if branches:
                branch = branches.pop(0)
                add("simulation_update_no_update_return", call_id=call_id,
                    address=hex(int(gdb.selected_frame().pc())),
                    attributed_branch_seq=branch["seq"], branch_address=branch["address"],
                    branch_taken=True)
            else:
                add("simulation_update_return_unmatched", call_id=call_id,
                    address=hex(int(gdb.selected_frame().pc())))
            return False
        entered_tick = entered["tick"]
        context["entered"] = None
        add("simulation_update_return", call_id=call_id,
            address=hex(int(gdb.selected_frame().pc())),
            phase_tick=entered_tick, entered_thread_global_num=entered["thread"])
        if tick not in TARGET_TICKS or entered_tick != tick:
            return False
        nonce = uuid.uuid4().hex
        pending_pause = {{"tick": tick, "thread_global_num": key,
                          "thread_ptid": list(thread.ptid), "nonce": nonce,
                          "run_nonce": RUN_NONCE, "call_id": call_id,
                          "unresolved_phase_calls": sorted(
                              set(phase_open) | {{item["call_id"] for item in call_contexts.values()}}),
                          "phase_context_quiescent": not phase_open and not call_contexts}}
        return True

class PreTickBranch(gdb.Breakpoint):
    def __init__(self, address):
        super().__init__("*0x%x" % address, gdb.BP_HARDWARE_BREAKPOINT)
    def stop(self):
        if time.time() >= DEADLINE:
            return True
        flags = int(gdb.parse_and_eval("$eflags"))
        taken = bool(flags & 0x40)
        thread = gdb.selected_thread()
        thread_id = thread_key(thread)
        address = int(gdb.selected_frame().pc())
        context = call_contexts.get(thread_id)
        if address == 0x0041C873:
            if context is not None:
                add("simulation_call_overlap", call_id=context["call_id"],
                    address=hex(address), branch_taken=taken)
                return False
            context = begin_call_context(thread, "pre-tick-branch")
        elif context is None:
            context = begin_call_context(thread, "late-pre-tick-branch")
        if context is None:
            add("pre_tick_branch_identity_missing", address=hex(address), branch_taken=taken)
            return False
        event = add("pre_tick_branch", call_id=context["call_id"], address=hex(address),
                    branch_taken=taken, zero_flag=bool(flags & 0x40))
        context["branch_events"].append(event)
        if taken:
            context["taken_branches"].append(event)
        return False

try:
    inferior = gdb.selected_inferior()
    if inferior.pid != TARGET_PID:
        raise RuntimeError("attached inferior PID mismatch")
    if (os.path.exists(PAUSED) or os.path.exists(RELEASE) or os.path.exists(ACK)
            or os.path.exists(EVENTS) or os.path.exists(ARMED)):
        raise RuntimeError("stale observer control artifact")
    Phase(0x0041C8CE, True)
    Phase(0x0041C961, False)
    PreTickBranch(0x0041C873)
    PreTickBranch(0x0041C880)
    with open(ARMED, "w", encoding="utf-8") as handle:
        json.dump({{"status": "ARMED", "inferior_pid": inferior.pid,
                   "target_ticks": TARGET_TICKS, "hardware_breakpoints_only": True,
                   "run_nonce": RUN_NONCE, "target_memory_writes": 0}}, handle)
    observed = []
    while time.time() < DEADLINE and len(observed) < len(TARGET_TICKS):
        try:
            gdb.execute("continue")
        except gdb.error as exc:
            if "exited" in str(exc).lower():
                break
            raise
        if pending_pause is not None:
            inferior = gdb.selected_inferior()
            rows = thread_census()
            pause = {{"status": "PAUSED_AT_PHASE_RETURN", **pending_pause,
                     "inferior_pid": inferior.pid,
                     "all_stop_mode": not bool(gdb.parameter("non-stop")),
                     "threads": rows, "thread_census_complete": bool(rows) and all(
                         row["inferior_pid"] == TARGET_PID for row in rows)}}
            atomic_json(PAUSED, pause)
            pending_pause = None
        if os.path.exists(PAUSED):
            with open(PAUSED, encoding="utf-8") as handle:
                pause = json.load(handle)
            deadline = time.time() + 15
            while time.time() < deadline:
                if os.path.exists(RELEASE):
                    with open(RELEASE, encoding="utf-8") as handle:
                        release = json.load(handle)
                    if (release.get("nonce") == pause.get("nonce")
                            and release.get("tick") == pause.get("tick")
                            and release.get("run_nonce") == RUN_NONCE
                            and release.get("status") in {{"RELEASE", "INVALID_CLEANUP"}}):
                        break
                    raise RuntimeError("stale or mismatched pause release")
                time.sleep(0.01)
            else:
                raise RuntimeError("checkpoint release timeout")
            census_after = thread_census()
            tick_after = read_tick()
            census_stable = census_after == pause.get("threads")
            all_stopped = bool(census_after) and all(
                row.get("inferior_pid") == TARGET_PID and row.get("is_running") is False
                for row in census_after)
            phase_quiescent = not phase_open and not call_contexts
            ack_status = ("CONSUMED" if release.get("status") == "RELEASE" else
                          "CLEANUP_CONSUMED")
            if (tick_after != pause.get("tick") or not census_stable or not all_stopped
                    or not phase_quiescent):
                ack_status = "INVALIDATED"
            ack = {{"status": ack_status, "nonce": pause.get("nonce"),
                   "tick": pause.get("tick"), "tick_after": tick_after,
                   "run_nonce": RUN_NONCE, "release_status": release.get("status"),
                   "threads_after": census_after, "census_stable": census_stable,
                   "all_threads_stopped": all_stopped,
                   "phase_context_quiescent": phase_quiescent}}
            add("pause_release_ack", ack_status=ack_status, pause_tick=pause.get("tick"),
                tick_after=tick_after, census_stable=census_stable, all_threads_stopped=all_stopped)
            os.remove(PAUSED)
            os.remove(RELEASE)
            # The consumed ack is the publication barrier for the next checkpoint.
            atomic_json(ACK, ack)
            observed.append(pause.get("tick"))
    summary = {{"status": "CAPTURED" if observed == TARGET_TICKS else "INCOMPLETE",
               "observed_ticks": observed, "target_ticks": TARGET_TICKS,
               "unresolved_phase_calls": sorted(
                   set(phase_open) | {{item["call_id"] for item in call_contexts.values()}}),
               "run_nonce": RUN_NONCE}}
except Exception as exc:
    summary = {{"status": "ERROR", "error": repr(exc)}}
finally:
    flush_events()
    with open(SUMMARY, "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
    try:
        gdb.execute("detach")
    except Exception:
        pass
'''


class _RiceDiagnosticComplete(Exception):
    """Internal signal to skip the normal probe's later memory-writing checks."""


def _fixture_pin(fixture: str) -> tuple[str, str, int]:
    try:
        return SAVE_FIXTURES[fixture]
    except KeyError:
        raise ProbeError(f"unsupported fixture: {fixture}") from None


def _scene_option_error(
    *, fixture: str, scene_actions: str, terrain_scroll: bool, terrain_trace: bool,
    census_only: bool, rice_phase: bool, scroll_phase: bool,
) -> str | None:
    """save006-only scene work cannot run on a loaded-only scene or save000."""
    if fixture != "save006" and scene_actions != "none":
        return f"--fixture {fixture} requires --scene-actions none"
    if scene_actions == "none" and (terrain_trace or rice_phase or scroll_phase):
        return ("--scene-actions none cannot be combined with "
                "--terrain-trace, --rice-phase-diagnostic or "
                "--scroll-phase-diagnostic")
    return None


class _LoadedOnlyComplete(Exception):
    """Stop after the loaded capture (and optional performance window)."""


class _CensusStateComplete(Exception):
    """Internal signal: the selected non-PS3 census window is full, stop before loading."""


CENSUS_PRESENT_LIMIT = 64


def _census_loaded_wait_timeout(skip_presents: int) -> float:
    """Seconds to wait for the post-skip census window on a loaded-only PS3 scene."""
    return 60.0 + (skip_presents + CENSUS_PRESENT_LIMIT) / 10.0


def _census_watch_wait_timeout(watch_presents: int) -> float:
    """Extra seconds the loaded-only census run keeps the scene alive for a --census-watch-presents window."""
    return 60.0 + watch_presents / 5.0 if watch_presents else 0.0


def _wait_census_presents(census_path: Path, census_state: int, timeout: float) -> dict[str, Any]:
    """Wait until the DLL has logged a full present window for the selected program state."""
    deadline = time.monotonic() + timeout
    count = 0
    while True:
        try:
            lines = census_path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            lines = []
        count = 0
        for line in lines:
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue  # the DLL may be mid-write on the last line
            if row.get("event") == "present_boundary" and row.get("program_state") == census_state:
                count += 1
        if count >= CENSUS_PRESENT_LIMIT or time.monotonic() >= deadline:
            return {"census_state": census_state, "presents": count,
                    "status": "PASS" if count >= CENSUS_PRESENT_LIMIT else "TIMEOUT"}
        time.sleep(0.5)


def _wait_census_watch_summary(census_path: Path, timeout: float) -> dict[str, Any]:
    """Wait until the armed watch has published its summary (window end or arm failure)."""
    deadline = time.monotonic() + timeout
    while True:
        try:
            lines = census_path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            lines = []
        for line in lines:
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue  # the DLL may be mid-write on the last line
            if row.get("event") == "watch_summary":
                return {"status": "PASS", "reason": row.get("reason"),
                        "hits": row.get("hits"), "present_ticks": row.get("watch_present_ticks")}
        if time.monotonic() >= deadline:
            return {"status": "TIMEOUT"}
        time.sleep(0.5)


def _scene_diff(before: Mapping[str, Any], after: Mapping[str, Any]) -> dict[str, Any]:
    """Retain complete changed player/unit records for same-tick diagnosis."""
    def indexed(rows: Any, key: str) -> dict[Any, Any]:
        if not isinstance(rows, list):
            return {}
        return {row.get(key): row for row in rows if isinstance(row, Mapping)}

    before_players, after_players = indexed(before.get("players"), "owner"), indexed(after.get("players"), "owner")
    before_units, after_units = indexed(before.get("units"), "slot"), indexed(after.get("units"), "slot")
    return {
        "players_changed": [
            {"owner": key, "before": before_players.get(key), "after": after_players.get(key)}
            for key in sorted(before_players.keys() | after_players.keys())
            if before_players.get(key) != after_players.get(key)
        ],
        "units_created": [after_units[key] for key in sorted(after_units.keys() - before_units.keys())],
        "units_removed": [before_units[key] for key in sorted(before_units.keys() - after_units.keys())],
        "units_changed": [
            {"slot": key, "before": before_units.get(key), "after": after_units.get(key)}
            for key in sorted(before_units.keys() & after_units.keys())
            if before_units[key] != after_units[key]
        ],
    }


def _fixed_camera_coverage_summary(
    trace_path: Path, camera: list[int], *, after_line_count: int = 0,
) -> dict[str, Any]:
    try:
        lines = trace_path.read_text(encoding="utf-8").splitlines()[after_line_count:]
    except (OSError, UnicodeDecodeError):
        return {"status": "INCOMPLETE", "sample_count": 0}
    values: list[int] = []
    for line in lines:
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(row, dict) or row.get("event") != "mirror2x_present" or row.get("program_state") != 3:
            continue
        if row.get("camera") != camera:
            if values:
                break
            continue
        covered, stale = row.get("covered_pixels"), row.get("stale_pixels")
        if isinstance(covered, int) and isinstance(stale, int) and covered >= stale:
            values.append(covered - stale)
    if len(values) < 40:
        return {"status": "INCOMPLETE", "sample_count": len(values), "camera": camera}
    first20 = statistics.median(values[:20])
    last20 = statistics.median(values[-20:])
    return {"status": "PASS" if first20 >= 264_000 and last20 >= first20 * 0.9 else "FAIL",
            "sample_count": len(values), "camera": camera,
            "first20_p50": first20, "last20_p50": last20,
            "last20_at_least_90_percent": last20 >= first20 * 0.9}


def _wait_fixed_camera_coverage(
    trace_path: Path, camera: list[int], *, timeout: float = 8.0,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    result: dict[str, Any] = {"status": "INCOMPLETE", "sample_count": 0}
    while time.monotonic() < deadline:
        result = _fixed_camera_coverage_summary(trace_path, camera)
        if result["status"] != "INCOMPLETE":
            return result
        time.sleep(0.05)
    return result


SCROLL_CAMERA_SIGNS = {"DOWN": (1, 1), "RIGHT": (1, -1), "UP": (-1, -1), "LEFT": (-1, 1)}
# Corner edge scroll hypothesis (lap1082 5): the sum of both edge signs per step.
SCROLL_CAMERA_SIGNS_EDGE = {
    **SCROLL_CAMERA_SIGNS,
    "UPLEFT": (-2, 0), "DOWNRIGHT": (2, 0), "UPRIGHT": (0, -2), "DOWNLEFT": (0, 2),
}


def _expected_scroll_camera(before: list[int], key: str) -> list[int] | None:
    delta = SCROLL_CAMERA_SIGNS_EDGE.get(key)
    return [before[0] + delta[0], before[1] + delta[1]] if delta else None


def _parse_scroll_keys(spec: str) -> tuple[str, str]:
    """Two distinct scroll keys for the DOWN/RIGHT action slots (H-D2i)."""
    keys = tuple(part.strip().upper() for part in spec.split(","))
    if len(keys) != 2 or keys[0] == keys[1] or any(k not in SCROLL_CAMERA_SIGNS for k in keys):
        raise ValueError(f"--terrain-scroll-keys needs two distinct keys from "
                         f"{sorted(SCROLL_CAMERA_SIGNS)}: {spec!r}")
    return keys[0], keys[1]


def _scroll_clamp_free(before: list[int], after: list[int]) -> bool:
    """True when the camera moved diagonally with equal travel on both axes."""
    dx, dy = after[0] - before[0], after[1] - before[1]
    return dx != 0 and abs(dx) == abs(dy)


def _scroll_corner_clamp_free(before: list[int], after: list[int], key: str) -> bool:
    """True when a corner scroll moved along its hypothesized axis with no off-axis drift."""
    if key not in _EDGE_DIAGONAL_SIGNS or not _scroll_camera_steps(before, after, key):
        return False
    signs = SCROLL_CAMERA_SIGNS_EDGE[key]
    return all(d == 0 for d, sign in ((after[0] - before[0], signs[0]),
                                      (after[1] - before[1], signs[1])) if sign == 0)


def _scroll_camera_steps(before: list[int], after: list[int], key: str) -> int | None:
    """Camera travel along the key direction, or None for any other movement.

    A held key slides along a map edge once one axis clamps (H-D2h: DOWN went
    (158,101)->(179,128)), so the axes only need the key's sign, not equal steps.
    """
    signs = SCROLL_CAMERA_SIGNS_EDGE.get(key)
    if signs is None:
        return None
    dx, dy = after[0] - before[0], after[1] - before[1]
    if dx * signs[0] < 0 or dy * signs[1] < 0:
        return None
    return max(abs(d) // abs(sign) for d, sign in ((dx, signs[0]), (dy, signs[1])) if sign)


def _send_scroll_until_camera_change(
    display: str, env: Mapping[str, str], key: str, before: list[int],
    input_trace_path: Path, *, after_seq: int,
    read_camera: Callable[[], list[int]], timeout: float = 2.0,
    read_sim_tick: Callable[[], int] | None = None,
    release_at_tick: int | None = None,
    send_edge: Callable[..., int] | None = None,
) -> dict[str, Any]:
    """Release on the first camera transition; receipt polling is independent.

    With ``release_at_tick`` the key is held until the simulation reaches that
    tick instead (continuous scroll); only camera transitions are sampled.
    ``send_edge`` replaces the X11 key edge (edge-of-screen mouse scroll, H-D2e).
    """
    if release_at_tick is not None and read_sim_tick is None:
        raise ValueError("release_at_tick requires read_sim_tick")
    receiver_down = None
    after_camera = before
    camera_samples: list[dict[str, Any]] = []
    down_emitted_ns: int | None = None
    up_emitted_ns: int | None = None
    release_reason = "timeout"
    down_attempted = False
    input_tick_before: int | None = None
    input_tick_after: int | None = None
    deadline = time.monotonic() + timeout
    try:
        down_attempted = True
        if read_sim_tick is not None:
            input_tick_before = read_sim_tick()
        down_emitted_ns = (send_edge or _send_key_edge)(display, env, key, down=True)
        if read_sim_tick is not None:
            input_tick_after = read_sim_tick()
        while time.monotonic() < deadline:
            if release_at_tick is None or receiver_down is None:
                receiver_down = _latest_scroll_keydown(
                    input_trace_path, key, after_seq=after_seq,
                )
            after_camera = read_camera()
            if (release_at_tick is None or not camera_samples
                    or camera_samples[-1]["camera"] != after_camera):
                camera_samples.append({"monotonic_ns": time.monotonic_ns(),
                                       "camera": after_camera})
            if release_at_tick is None:
                if after_camera != before:
                    release_reason = "first_camera_change"
                    break
            elif read_sim_tick() >= release_at_tick:
                release_reason = "release_tick"
                break
            time.sleep(0.001)
    finally:
        if down_attempted:
            up_emitted_ns = (send_edge or _send_key_edge)(display, env, key, down=False)
    return {"receiver_down": receiver_down, "camera": after_camera,
            "camera_samples": camera_samples,
            "down_emitted_ns": down_emitted_ns, "up_emitted_ns": up_emitted_ns,
            "input_tick_before": input_tick_before, "input_tick_after": input_tick_after,
            "release_reason": release_reason}


def _capture(
    display: str, run_id: str, pid: int, tag: str, crop: tuple[int, int, int, int],
    output: Path, log: Any,
) -> dict[str, Any]:
    path, record = runtime_env._capture_screenshot(display, run_id, pid, tag, 20.0, crop)
    copied = output / f"{tag}.png"
    shutil.copy2(path, copied)
    return {**record, "path": str(copied), "source_path": str(path)}


def _latest_mirror_stale(trace_path: Path) -> int | None:
    """Read the last flushed cumulative stale counter without changing the game."""
    try:
        lines = trace_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return None
    for line in reversed(lines):
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if (row.get("event") == "mirror2x_present"
                and isinstance(row.get("primitive_stale_pixels_total"), int)):
            return row["primitive_stale_pixels_total"]
    return None


def _terrain_scroll_coverage(
    trace_path: Path, *, after_line_count: int, camera_before: list[int],
    expected_records: int = 30, observation_tick: int | None = None,
    observation_qpc: int | None = None,
) -> dict[str, Any]:
    """Measure scroll presents through the requested simulation-tick boundary."""
    try:
        lines = trace_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        lines = []
    samples: list[int] = []
    sample_seqs: list[int] = []
    sample_ticks: list[int] = []
    sample_ts_ms: list[int] = []
    last_metrics: dict[str, int] = {}
    transition_seq: int | None = None
    transition_camera: list[int] | None = None
    boundary_reached = False
    first_after_boundary: dict[str, int | None] | None = None
    epoch_comparable_samples = 0
    for line in lines[max(0, after_line_count):]:
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if (not isinstance(row, dict) or row.get("event") != "mirror2x_present"
                or row.get("program_state") != 3):
            continue
        camera = row.get("camera")
        if transition_seq is None:
            if (not isinstance(camera, list) or len(camera) != 2
                    or camera == camera_before):
                continue
            transition_seq = row.get("seq")
            transition_camera = camera
        if observation_tick is not None:
            sim_tick = row.get("sim_tick")
            if not isinstance(sim_tick, int):
                return {"status": "INVALID", "reason": "mirror2x_present missing integer sim_tick",
                        "sample_count": len(samples), "expected_records": expected_records,
                        "coverage_p50_pixels": None,
                        "transition_present_seq": transition_seq,
                        "transition_camera": transition_camera,
                        "boundary_reached": boundary_reached,
                        "sample_present_seqs": sample_seqs, "sample_sim_ticks": sample_ticks,
                        "sample_ts_ms": sample_ts_ms}
            if sim_tick > observation_tick:
                boundary_reached = True
                first_after_boundary = {"seq": row.get("seq"), "sim_tick": sim_tick}
                break
        covered = row.get("covered_pixels")
        stale = row.get("stale_pixels")
        if isinstance(covered, int) and isinstance(stale, int) and covered >= stale:
            samples.append(covered - stale)
            seq = row.get("seq")
            if isinstance(seq, int):
                sample_seqs.append(seq)
            tick = row.get("sim_tick")
            if observation_tick is not None and isinstance(tick, int):
                sample_ticks.append(tick)
            ts_ms = row.get("ts_ms")
            if isinstance(ts_ms, int):
                sample_ts_ms.append(ts_ms)
                if (observation_qpc is not None
                        and ts_ms <= observation_qpc // 10_000):
                    epoch_comparable_samples += 1
            for field in ("layer_compose_calls", "layer_move_calls", "layer_move_bytes",
                          "layer_move_unsupported", "layer_transfer_calls",
                          "layer_covered_pixels", "hd_mask_outside_diff_subpixels"):
                value = row.get(field)
                if isinstance(value, int):
                    last_metrics[field] = value
            if len(samples) == expected_records:
                break
    if len(samples) != expected_records:
        return {"status": "INCOMPLETE", "sample_count": len(samples),
                "expected_records": expected_records, "transition_present_seq": transition_seq,
                "coverage_p50_pixels": None,
                "transition_camera": transition_camera, "covered_minus_stale": samples,
                "observation_tick": observation_tick,
                "boundary_reached": boundary_reached,
                "last_in_boundary_seq": sample_seqs[-1] if sample_seqs else None,
                "first_after_boundary": first_after_boundary,
                "sample_present_seqs": sample_seqs, "sample_sim_ticks": sample_ticks,
                "sample_ts_ms": sample_ts_ms,
                "epoch_comparable_sample_count": (
                    epoch_comparable_samples if observation_qpc is not None else None)}
    p50 = sorted(samples)[(len(samples) - 1) // 2] if samples else None
    threshold = int(480_000 * 0.55)
    first_recovery = next((index + 1 for index, value in enumerate(samples)
                           if value >= threshold), None)
    return {"status": "PASS" if p50 is not None and p50 >= threshold else "FAIL",
            "sample_count": len(samples), "coverage_threshold_pixels": threshold,
            "coverage_p50_pixels": p50, "coverage_p50_ratio": p50 / 480_000 if p50 else None,
            "transition_present_seq": transition_seq, "transition_camera": transition_camera,
            "first_threshold_present": first_recovery,
            "covered_minus_stale": samples, "layer_metrics": last_metrics,
            "observation_tick": observation_tick, "boundary_reached": boundary_reached,
            "last_in_boundary_seq": sample_seqs[-1] if sample_seqs else None,
            "first_after_boundary": first_after_boundary,
            "sample_present_seqs": sample_seqs, "sample_sim_ticks": sample_ticks,
            "sample_ts_ms": sample_ts_ms,
            "epoch_comparable_sample_count": (
                epoch_comparable_samples if observation_qpc is not None else None)}


def _terrain_coverage_p50(trace_path: Path, *, before_line_count: int) -> int | None:
    try:
        lines = trace_path.read_text(encoding="utf-8").splitlines()[:before_line_count]
    except (OSError, UnicodeDecodeError):
        return None
    values: list[int] = []
    for line in lines:
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if (isinstance(row, dict) and row.get("event") == "mirror2x_present"
                and row.get("program_state") == 3
                and isinstance(row.get("covered_pixels"), int)
                and isinstance(row.get("stale_pixels"), int)
                and row["covered_pixels"] >= row["stale_pixels"]):
            values.append(row["covered_pixels"] - row["stale_pixels"])
    values = values[-30:]
    return sorted(values)[(len(values) - 1) // 2] if values else None


def _latest_layer_metrics(trace_path: Path) -> dict[str, int]:
    fields = ("layer_compose_calls", "layer_move_calls", "layer_move_bytes",
              "layer_move_unsupported", "layer_transfer_calls", "layer_covered_pixels",
              "hd_mask_outside_diff_subpixels")
    try:
        lines = trace_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return {}
    for line in reversed(lines):
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict) and row.get("event") == "mirror2x_present":
            return {field: row[field] for field in fields if isinstance(row.get(field), int)}
    return {}


def _trace_line_count(trace_path: Path) -> int:
    try:
        return len(trace_path.read_text(encoding="utf-8").splitlines())
    except (OSError, UnicodeDecodeError):
        return 0


def _latest_scroll_keydown(
    input_trace_path: Path, key: str, *, after_seq: int = 0,
) -> dict[str, Any] | None:
    """Return the latest game-window WM_KEYDOWN receipt for a virtual key."""
    virtual_key = {"DOWN": 0x28, "RIGHT": 0x27, "LEFT": 0x25, "UP": 0x26}.get(key)
    try:
        lines = input_trace_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return None
    for line in reversed(lines):
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if (isinstance(row, dict) and row.get("schema") == "g1-scroll-input-v1"
                and row.get("seq", 0) > after_seq
                and row.get("message") == 0x100 and row.get("key") == virtual_key):
            return row
    return None


def _latest_scroll_keyup(
    input_trace_path: Path, key: str, *, after_seq: int,
) -> dict[str, Any] | None:
    virtual_key = {"DOWN": 0x28, "RIGHT": 0x27, "LEFT": 0x25, "UP": 0x26}.get(key)
    try:
        lines = input_trace_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return None
    for line in reversed(lines):
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if (isinstance(row, dict) and row.get("schema") == "g1-scroll-input-v1"
                and row.get("seq", 0) > after_seq
                and row.get("message") == 0x101 and row.get("key") == virtual_key):
            return row
    return None


def _wait_for_terrain_scroll_coverage(
    trace_path: Path, *, after_line_count: int, camera_before: list[int],
    observation_tick: int | None = None, observation_qpc: int | None = None,
    timeout: float = 8.0,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    result: dict[str, Any] = {"status": "INCOMPLETE", "sample_count": 0}
    while time.monotonic() < deadline:
        result = _terrain_scroll_coverage(
            trace_path, after_line_count=after_line_count, camera_before=camera_before,
            observation_tick=observation_tick, observation_qpc=observation_qpc,
        )
        if result["status"] != "INCOMPLETE" or result.get("boundary_reached") is True:
            return result
        time.sleep(0.05)
    return result


def _wait_for_scroll_settled(
    pid: int, read_memory: Callable[[int, int], bytes], trace_path: Path, *,
    candidate: bool, timeout: float = 8.0,
) -> dict[str, Any]:
    """Wait for stable PS3 camera/ticks and, in the mirror lane, terrain calls."""
    deadline = time.monotonic() + timeout
    previous_camera: list[int] | None = None
    previous_tick: int | None = None
    stable = 0
    last_camera: list[int] | None = None
    while time.monotonic() < deadline:
        state = runtime_driver.state(pid, False)
        camera = runtime_env._read_camera(read_memory)
        tick = state.get("tick")
        if (state.get("ps") == 3 and camera == previous_camera
                and isinstance(tick, int) and isinstance(previous_tick, int)
                and tick > previous_tick):
            stable += 1
        else:
            stable = 0
        previous_camera, previous_tick = camera, tick if isinstance(tick, int) else None
        last_camera = camera
        if stable >= 5:
            writer_stable = None
            if candidate:
                try:
                    rows = [json.loads(line) for line in trace_path.read_text(
                        encoding="utf-8").splitlines() if line.strip()]
                    presents = [row for row in rows if isinstance(row, dict)
                                and row.get("event") == "mirror2x_present"
                                and row.get("program_state") == 3]
                    fields = ("terrain_rle_468c30_calls", "terrain_shade_468cc0_calls",
                              "terrain_checker_468e10_calls", "terrain_clip_468f00_calls",
                              "terrain_clip_shade_4690a0_calls")
                    tail = presents[-5:]
                    signatures = [tuple(row.get(field) for field in fields) for row in tail]
                    if len(tail) == 5 and all(value == signatures[0] for value in signatures):
                        writer_stable = signatures[0]
                except (OSError, UnicodeDecodeError, json.JSONDecodeError):
                    pass
            if not candidate or writer_stable is not None:
                return {"status": "PASS", "camera": camera, "stable_ticks": stable,
                        "terrain_writer_counts": writer_stable,
                        "terrain_writer_barrier": "PASS" if writer_stable is not None else "UNAVAILABLE"}
        time.sleep(0.05)
    return {"status": "INCOMPLETE", "camera": last_camera, "stable_ticks": stable,
            "terrain_writer_barrier": "INCOMPLETE" if candidate else "UNAVAILABLE"}


def _wait_for_mirror_present(
    trace_path: Path, *, program_state: int, minimum_records: int = 2,
    timeout: float = 5.0,
) -> dict[str, Any]:
    """Wait until the candidate has presented the requested live state.

    A Scale2x candidate can reach PS3 before its first converted primary
    present has reached the X server.  Capturing immediately after the state
    transition therefore records a valid but entirely black surface.  The
    trace is the same-run presentation witness, so use it as the capture
    barrier instead of an arbitrary sleep.
    """
    deadline = time.monotonic() + timeout
    last_count = 0
    while time.monotonic() < deadline:
        try:
            rows = [
                json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            matching = [
                row for row in rows
                if isinstance(row, dict)
                and row.get("event") == "mirror2x_present"
                and row.get("program_state") == program_state
            ]
            last_count = len(matching)
            if last_count >= minimum_records:
                return {"status": "PASS", "program_state": program_state,
                        "records": last_count, "elapsed": timeout - max(0.0, deadline - time.monotonic())}
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            pass
        time.sleep(0.05)
    raise ProbeError(
        f"candidate presentation barrier timed out for PS={program_state}; "
        f"matching_records={last_count}"
    )


def _primary_present_records(trace_path: Path, *, candidate: bool) -> list[dict[str, Any]]:
    """Read successful primary presentation witnesses from the live trace."""

    try:
        rows = [json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines()
                if line.strip()]
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return []
    event = "mirror2x_present" if candidate else "blt"
    return [row for row in rows if isinstance(row, dict)
            and row.get("event") == event and row.get("program_state") == 3
            and (candidate or row.get("caller") == "0x004D3ABC")
            and row.get("hresult") == 0
            and (not candidate or row.get("success") == 1)]


def _input_trace_records(trace_path: Path) -> list[dict[str, Any]]:
    try:
        rows = [json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines()
                if line.strip()]
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return []
    return [row for row in rows if isinstance(row, dict)
            and row.get("schema") == "g1-input-trace-v1"]


def _wait_for_post_release_presents(
    trace_path: Path, input_trace_path: Path, *, candidate: bool, input_seq_before: int,
    host_return_present_seq: int, drag_from: list[int], drag_to: list[int],
    minimum_records: int = 2, timeout: float = 5.0,
) -> dict[str, Any]:
    """Bind candidate presents to the game's received WM_LBUTTONUP boundary."""
    deadline = time.monotonic() + timeout
    release: dict[str, Any] | None = None
    last_presents: list[dict[str, Any]] = []
    invalid_reason: str | None = None
    while time.monotonic() < deadline:
        input_rows = [row for row in _input_trace_records(input_trace_path)
                      if isinstance(row.get("seq"), int) and row["seq"] > input_seq_before
                      and row.get("kind") == "WndProc"]
        downs = [row for row in input_rows if row.get("message") == 0x201]
        releases = [row for row in input_rows if row.get("message") == 0x202]
        if len(downs) > 1 or len(releases) > 1:
            invalid_reason = f"expected one drag down/up receipt, got down={len(downs)} up={len(releases)}"
            break
        if releases:
            if len(downs) != 1:
                invalid_reason = f"expected one drag down receipt before release, got {len(downs)}"
                break
            down, release = downs[0], releases[0]
            if (down.get("logical") != list(drag_from) or release.get("logical") != list(drag_to)
                    or down.get("seq", 0) >= release.get("seq", 0)
                    or not isinstance(release.get("ts_ms"), int)):
                invalid_reason = "received button coordinates/order do not match injected drag"
                break
            present_rows = _primary_present_records(trace_path, candidate=candidate)
            last_presents = [row for row in present_rows
                             if isinstance(row.get("seq"), int)
                             and isinstance(row.get("ts_ms"), int)
                             and row["seq"] > host_return_present_seq
                             and row["ts_ms"] > release.get("ts_ms", -1)]
            if len(last_presents) >= minimum_records:
                records = last_presents[:minimum_records]
                return {
                    "status": "PASS", "input_seq_before": input_seq_before,
                    "host_return_present_seq": host_return_present_seq,
                    "release": {key: release.get(key) for key in
                                ("seq", "ts_ms", "thread_id", "logical")},
                    "records": [{key: row.get(key) for key in
                                 ("seq", "ts_ms", "thread_id", "game_tick", "present_tick",
                                  "hresult", "success")} for row in records],
                    "first_release_delta_ms": records[0]["ts_ms"] - release["ts_ms"],
                    "elapsed": timeout - max(0.0, deadline - time.monotonic()),
                }
        time.sleep(0.05)
    if release is None and invalid_reason is None:
        invalid_reason = "game WndProc WM_LBUTTONUP receipt was not observed before timeout"
    return {
        "status": "UNKNOWN", "input_seq_before": input_seq_before,
        "host_return_present_seq": host_return_present_seq,
        "release": ({key: release.get(key) for key in
                     ("seq", "ts_ms", "thread_id", "logical")} if release else None),
        "records": [{key: row.get(key) for key in
                     ("seq", "ts_ms", "thread_id", "game_tick", "present_tick",
                      "hresult", "success")} for row in last_presents],
        "reason": invalid_reason or f"expected {minimum_records} fresh primary presents, got {len(last_presents)}",
    }


def _drag_capture_binding(
    *, candidate: bool, button_up_delivered: bool, post_input_presents: Mapping[str, Any],
    settled_status: str, stable_samples: int, settled_selection: Any,
    selection_before_capture: Any, selection_after_capture: Any,
) -> dict[str, Any]:
    selection_equal = (settled_selection == selection_before_capture == selection_after_capture)
    presents_bound = (not candidate or post_input_presents.get("status") == "PASS")
    accepted = (button_up_delivered and presents_bound and settled_status == "PASS"
                and stable_samples >= 2 and selection_equal)
    return {
        "status": ("PASS" if accepted and candidate else
                   "PASS_WITH_LIMITS" if accepted else "HOLD"),
        "button_up_delivered": button_up_delivered,
        "post_input_presents": post_input_presents,
        "settled_selection": {
            "status": settled_status, "stable_samples": stable_samples,
            "selected_slots": settled_selection,
        },
        "selection_before_capture": selection_before_capture,
        "selection_after_capture": selection_after_capture,
        "selection_stable_across_capture": selection_before_capture == selection_after_capture,
        "selection_bound_to_capture": selection_equal,
    }


def _wait_for_post_input_presents(
    trace_path: Path, *, candidate: bool, after_seq: int,
    minimum_records: int = 2, timeout: float = 5.0,
) -> dict[str, Any]:
    """Require fresh successful primary presents after the input was released."""

    deadline = time.monotonic() + timeout
    matching: list[dict[str, Any]] = []
    while time.monotonic() < deadline:
        matching = [row for row in _primary_present_records(trace_path, candidate=candidate)
                    if isinstance(row.get("seq"), int) and row["seq"] > after_seq]
        if len(matching) >= minimum_records:
            return {"status": "PASS", "after_seq": after_seq,
                    "records": [{key: row.get(key) for key in
                                 ("seq", "ts_ms", "game_tick", "present_tick", "hresult", "success")}
                                for row in matching[-minimum_records:]],
                    "elapsed": timeout - max(0.0, deadline - time.monotonic())}
        time.sleep(0.05)
    return {"status": "UNKNOWN", "after_seq": after_seq,
            "records": [{key: row.get(key) for key in
                         ("seq", "ts_ms", "game_tick", "present_tick", "hresult", "success")}
                        for row in matching],
            "reason": f"expected {minimum_records} fresh primary presents, got {len(matching)}"}


def _measure_performance_window(
    pid: int, prefix: Path, read_memory: Callable[[int, int], bytes], *,
    window_id: str, duration: float = PERFORMANCE_WINDOW_SECONDS,
) -> dict[str, Any]:
    """Measure one no-input PS3 interval and arm the DLL's matching present histogram."""

    marker = prefix / "drive_c" / PERFORMANCE_WINDOW_FILE
    if marker.exists():
        raise ProbeError(f"stale performance-window marker: {marker}")
    start_state = runtime_driver.state(pid, False)
    start_camera = runtime_env._read_camera(read_memory)
    if start_state.get("ps") != 3 or not isinstance(start_state.get("tick"), int):
        raise ProbeError(f"performance window requires loaded PS3: {start_state}")

    marker.write_text("active\\n", encoding="ascii")
    started = time.monotonic()
    samples = [start_state]
    ps3_stable = True
    monotonic_ticks = True
    previous_tick = start_state["tick"]
    last_raw_sample = started
    raw_samples: list[dict[str, Any]] = [{
        "monotonic": started, "ps": start_state.get("ps"),
        "sim_tick": start_state.get("tick"), "camera": start_camera,
    }]
    try:
        while time.monotonic() - started < duration:
            remaining = duration - (time.monotonic() - started)
            time.sleep(min(0.2, max(0.0, remaining)))
            state = runtime_driver.state(pid, False)
            samples.append(state)
            sampled_at = time.monotonic()
            if sampled_at - last_raw_sample >= 1.0:
                raw_samples.append({
                    "monotonic": sampled_at, "ps": state.get("ps"),
                    "sim_tick": state.get("tick"),
                    "camera": runtime_env._read_camera(read_memory),
                })
                last_raw_sample = sampled_at
            tick = state.get("tick")
            ps3_stable = ps3_stable and state.get("ps") == 3
            monotonic_ticks = monotonic_ticks and isinstance(tick, int) and tick >= previous_tick
            if isinstance(tick, int):
                previous_tick = tick
        end_state = runtime_driver.state(pid, False)
        end_camera = runtime_env._read_camera(read_memory)
        ended = time.monotonic()
    finally:
        marker.unlink(missing_ok=True)

    end_tick = end_state.get("tick")
    start_tick = start_state.get("tick")
    elapsed = ended - started
    tick_delta = end_tick - start_tick if isinstance(end_tick, int) and isinstance(start_tick, int) else None
    return {
        "status": "PASS" if (
            ps3_stable and monotonic_ticks and start_camera == end_camera
            and isinstance(tick_delta, int) and tick_delta > 0 and elapsed >= duration
        ) else "INVALID",
        "duration_target_seconds": duration,
        "monotonic_start": started,
        "monotonic_end": ended,
        "monotonic_seconds": elapsed,
        "sample_count": len(samples) + 1,
        "ps3_stable": ps3_stable,
        "tick_monotonic": monotonic_ticks,
        "camera_start": start_camera,
        "camera_end": end_camera,
        "tick_start": start_tick,
        "tick_end": end_tick,
        "tick_delta": tick_delta,
        "tick_rate_hz": tick_delta / elapsed if isinstance(tick_delta, int) and elapsed > 0 else None,
        "scene_start": _scene_identity(start_state),
        "scene_end": _scene_identity(end_state),
        "input": "none",
        "window_id": window_id,
        "state_samples": raw_samples,
        "marker_removed": not marker.exists(),
    }


def _arm_perf_sections_marker(prefix: Path) -> Path:
    """Enable opt-in DLL section snapshots for the bounded scroll diagnostic."""
    marker = prefix / "drive_c" / PERFORMANCE_WINDOW_FILE
    if marker.exists():
        raise ProbeError(f"stale performance-section marker: {marker}")
    marker.write_text("active\n", encoding="ascii")
    return marker


def _histogram_percentile(histogram: list[int], percentile: int) -> int | None:
    if len(histogram) != 256 or any(type(value) is not int or value < 0 for value in histogram):
        return None
    total = sum(histogram)
    if total == 0 or not 1 <= percentile <= 100:
        return None
    target = (total * percentile + 99) // 100
    cumulative = 0
    for value, count in enumerate(histogram):
        cumulative += count
        if cumulative >= target:
            return value
    return None


def _performance_present_metrics(trace_path: Path) -> dict[str, Any]:
    summaries: list[dict[str, Any]] = []
    histogram = [0] * 256
    seen_bins: set[int] = set()
    malformed_bins = False
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            if '"event":"perf_window_' in line:
                malformed_bins = True
            continue
        if isinstance(row, dict) and row.get("event") == "perf_window_meta":
            summaries.append(row)
        elif isinstance(row, dict) and row.get("event") == "perf_window_histogram":
            bucket = row.get("elapsed_ms")
            count = row.get("count")
            if (row.get("program_state") != 3 or type(bucket) is not int
                    or not 0 <= bucket < 256 or type(count) is not int or count <= 0
                    or bucket in seen_bins):
                malformed_bins = True
            else:
                histogram[bucket] = count
                seen_bins.add(bucket)
    if len(summaries) != 1:
        return {"status": "INVALID", "reason": f"expected one performance summary, got {len(summaries)}"}
    perf = summaries[0]
    count = perf.get("count")
    dropped = perf.get("dropped")
    if (type(count) is not int or type(dropped) is not int or dropped != 0
            or malformed_bins or sum(histogram) != count):
        return {"status": "INVALID", "reason": "sample count/drop/histogram mismatch", "raw": perf}
    p95 = _histogram_percentile(histogram, 95)
    first = perf.get("first_tick_ms")
    last = perf.get("last_tick_ms")
    span_ms = ((last - first) & 0xFFFFFFFF) if type(first) is int and type(last) is int else None
    if count == 0 or p95 is None or not isinstance(span_ms, int):
        return {"status": "INVALID", "reason": "empty or malformed PS3 present window", "raw": perf}
    return {"status": "PASS", "sample_count": count, "dropped": dropped,
            "p95_ms": p95, "sample_span_ms": span_ms, "histogram_ms": histogram}


def _scene_identity(state: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "players": [
            {key: player.get(key) for key in ("owner", "nation", "ai", "count_cap", "cap")}
            for player in state.get("players", []) if isinstance(player, Mapping)
        ],
        "units": sorted(
            (unit.get("slot"), unit.get("type"), unit.get("owner"), unit.get("internal_id"))
            for unit in state.get("units", []) if isinstance(unit, Mapping)
        ),
        "ps": state.get("ps"),
    }


def _selection_slots(read_memory: Callable[[int, int], bytes]) -> list[int]:
    """Read the bounded stock selection entries, not just count/first slot."""

    raw = read_memory(SELECTION_ARRAY_ADDRESS, SELECTION_ARRAY_CAPACITY * 4)
    if len(raw) != SELECTION_ARRAY_CAPACITY * 4:
        raise ProbeError("selection array read returned an unexpected size")
    # Each stock entry is a dword whose low word is the unit slot; the upper
    # word is auxiliary selection state and must not become part of the slot id.
    return [value & 0xFFFF for value in struct.unpack(f"<{SELECTION_ARRAY_CAPACITY}I", raw)]


def _selection_observation(read_memory: Callable[[int, int], bytes]) -> dict[str, Any]:
    evidence = runtime_env._read_g1_selection_evidence(read_memory)
    slots = _selection_slots(read_memory)
    count = evidence.get("count")
    if type(count) is int and 0 <= count <= SELECTION_ARRAY_CAPACITY:
        evidence["selected_slots"] = slots[:count]
    else:
        evidence["selected_slots"] = []
    evidence["selection_array_raw_hex"] = struct.pack(
        f"<{SELECTION_ARRAY_CAPACITY}I", *slots
    ).hex()
    return evidence


def _poll_observation(
    label: str, read: Callable[[], dict[str, Any]],
    predicate: Callable[[dict[str, Any]], bool], timeout: float = 10.0,
) -> dict[str, Any]:
    """Poll a semantic effect without converting a timeout into a lane crash."""

    started = time.monotonic()
    samples = 0
    last: dict[str, Any] = {}
    while time.monotonic() - started < timeout:
        try:
            last = read()
            samples += 1
            if predicate(last):
                return {"status": "PASS", "label": label, "samples": samples,
                        "elapsed": time.monotonic() - started, "final": last}
        except (OSError, ValueError, KeyError, struct.error) as exc:
            last = {"error": f"{type(exc).__name__}: {exc}"}
        time.sleep(0.15)
    return {"status": "UNKNOWN", "label": label, "samples": samples,
            "elapsed": time.monotonic() - started, "final": last}


def _poll_stable_observation(
    label: str, read: Callable[[], dict[str, Any]],
    predicate: Callable[[dict[str, Any]], bool], *, consecutive: int = 2,
    timeout: float = 10.0,
) -> dict[str, Any]:
    """Wait for repeated identical semantic reads after a delivered input."""

    started = time.monotonic()
    samples = 0
    stable_samples = 0
    previous: dict[str, Any] | None = None
    last: dict[str, Any] = {}
    while time.monotonic() - started < timeout:
        try:
            last = read()
            samples += 1
            if predicate(last):
                stable_samples = stable_samples + 1 if last == previous else 1
                previous = last
                if stable_samples >= consecutive:
                    return {"status": "PASS", "label": label, "samples": samples,
                            "stable_samples": stable_samples,
                            "elapsed": time.monotonic() - started, "final": last}
            else:
                stable_samples = 0
                previous = last
        except (OSError, ValueError, KeyError, struct.error) as exc:
            last = {"error": f"{type(exc).__name__}: {exc}"}
            stable_samples = 0
            previous = None
        time.sleep(0.15)
    return {"status": "UNKNOWN", "label": label, "samples": samples,
            "stable_samples": stable_samples,
            "elapsed": time.monotonic() - started, "final": last}


def _production_witness(state: Mapping[str, Any], selected_slot: int) -> dict[str, Any]:
    unit = next((item for item in state.get("units", [])
                 if isinstance(item, Mapping) and item.get("slot") == selected_slot), None)
    player = next((item for item in state.get("players", [])
                   if isinstance(item, Mapping) and item.get("owner") == 0), None)
    if not isinstance(unit, Mapping) or not isinstance(player, Mapping):
        return {"status": "UNKNOWN", "selected_slot": selected_slot}
    return {
        "status": "OBSERVED",
        "selected_slot": selected_slot,
        "slot": unit.get("slot"),
        "sim_tick": state.get("tick"),
        "owner": unit.get("owner"),
        "type": unit.get("type"),
        "command": unit.get("command"),
        "production_type": unit.get("production_type"),
        "progress": unit.get("progress"),
        "reserved": player.get("reserved"),
        "rice": player.get("rice"),
        "wood": player.get("wood"),
    }


def _production_spec(
    read_memory: Callable[[int, int], bytes], *, queue_type: int = PRODUCTION_UNIT_TYPE,
) -> dict[str, int]:
    address = 0x009B5228 + queue_type * 0x394 + 0x10
    raw = read_memory(address, 6)
    if len(raw) != 6:
        raise ProbeError("production spec read returned an unexpected size")
    population, rice, wood = struct.unpack("<hhh", raw)
    return {"population": population, "rice": rice, "wood": wood}


def _production_global_delta(before: Mapping[str, Any], after: Mapping[str, Any]) -> dict[str, int | None]:
    return {
        field: (after[field] - before[field]
                if isinstance(before.get(field), int) and isinstance(after.get(field), int)
                else None)
        for field in ("rice", "wood", "reserved")
    }


def _production_issue_acceptance(
    previous: Mapping[str, Any], issued: Mapping[str, Any], following: Mapping[str, Any], *,
    expected_slot: int, producer_type: int, queue_type: int,
    spec: Mapping[str, int],
) -> dict[str, Any]:
    """Validate the first command-15 sample and its adjacent exact issue cost."""
    identity_fields = ("selected_slot", "slot", "owner", "type")
    identity_ok = all(
        previous.get(field) == issued.get(field) == following.get(field)
        for field in identity_fields
    ) and (
        previous.get("selected_slot") == expected_slot
        and previous.get("slot") == expected_slot
        and previous.get("owner") == 0
        and previous.get("type") == producer_type
    )
    issue_transition = (
        previous.get("command") != 15
        and issued.get("command") == 15
        and issued.get("production_type") == queue_type
        and isinstance(previous.get("progress"), int)
        and isinstance(issued.get("progress"), int)
        and issued["progress"] < previous["progress"]
    )
    result: dict[str, Any] = {
        "status": "UNKNOWN", "cost_match": "INEXACT",
        "previous": dict(previous), "a": dict(issued), "b": dict(following),
        "expected_cost": {"rice": -spec.get("rice", 0), "wood": -spec.get("wood", 0),
                          "reserved": spec.get("population", 0)},
        "cost_vectors": {},
    }
    if not identity_ok or not issue_transition:
        return result
    expected = result["expected_cost"]
    for label, later in (("prev_to_a", issued), ("prev_to_b", following)):
        delta = _production_global_delta(previous, later)
        result["cost_vectors"][label] = delta
        if delta == expected:
            result["cost_match"] = label
            result["status"] = "PASS"
            result["issue_cost"] = delta
            return result
    return result


def _production_effect(
    before: Mapping[str, Any], after: Mapping[str, Any], *,
    producer_type: int = PRODUCTION_BUILDING_TYPE,
    queue_type: int = PRODUCTION_UNIT_TYPE,
    spec: Mapping[str, int] | None = None,
) -> bool:
    if spec is None:
        return False
    witness = {**after, "selected_slot": before.get("selected_slot", PRODUCTION_SLOT),
               "slot": after.get("slot", before.get("selected_slot", PRODUCTION_SLOT))}
    return _production_issue_acceptance(
        before, witness, witness, expected_slot=PRODUCTION_SLOT,
        producer_type=producer_type, queue_type=queue_type, spec=spec,
    )["status"] == "PASS"


def _poll_production_issue(
    read: Callable[[], dict[str, Any]], previous: Mapping[str, Any], *,
    expected_slot: int, producer_type: int, queue_type: int,
    spec: Mapping[str, int], timeout: float = 10.0,
) -> dict[str, Any]:
    """Capture the first command-15 sample plus the immediately adjacent reads."""
    started = time.monotonic()
    prior = dict(previous)
    samples = 0
    last: dict[str, Any] = {}
    while time.monotonic() - started < timeout:
        try:
            current = read()
            samples += 1
            last = current
            if current.get("command") == 15 and prior.get("command") != 15:
                following = read()
                samples += 1
                acceptance = _production_issue_acceptance(
                    prior, current, following, expected_slot=expected_slot,
                    producer_type=producer_type, queue_type=queue_type, spec=spec,
                )
                return {"status": acceptance["status"], "label": "production issue",
                        "samples": samples, "elapsed": time.monotonic() - started,
                        "acceptance": acceptance, "final": following}
            prior = current
        except (OSError, ValueError, KeyError, struct.error) as exc:
            last = {"error": f"{type(exc).__name__}: {exc}"}
        time.sleep(0.15)
    return {"status": "UNKNOWN", "label": "production issue", "samples": samples,
            "elapsed": time.monotonic() - started, "final": last,
            "acceptance": {"status": "UNKNOWN", "cost_match": "INEXACT"}}


def _production_completion(
    before_slots: set[int], before_count: int, state: Mapping[str, Any], *,
    selected_slot: int,
) -> dict[str, Any]:
    units = [item for item in state.get("units", []) if isinstance(item, Mapping)
             and item.get("owner") == 0 and item.get("type") == PRODUCTION_UNIT_TYPE]
    after_slots = {int(item["slot"]) for item in units if isinstance(item.get("slot"), int)}
    selected = next((item for item in state.get("units", []) if isinstance(item, Mapping)
                     and item.get("slot") == selected_slot), None)
    return {
        "status": "PASS" if (
            isinstance(selected, Mapping) and selected.get("command") != 15
            and len(units) == before_count + 1 and bool(after_slots - before_slots)
        ) else "UNKNOWN",
        "before_count": before_count, "after_count": len(units),
        "new_slots": sorted(after_slots - before_slots),
        "selected_command": selected.get("command") if isinstance(selected, Mapping) else None,
    }


def _valid_production_target(
    selection: Mapping[str, Any], unit: Mapping[str, Any] | None, *,
    expected_slot: int, expected_type: int = PRODUCTION_BUILDING_TYPE,
) -> bool:
    return (
        selection.get("count") == 1
        and selection.get("selected_slot") == expected_slot
        and isinstance(unit, Mapping)
        and unit.get("slot") == expected_slot
        and unit.get("owner") == 0
        and unit.get("type") == expected_type
    )


def _production_control_status(
    before: Mapping[str, Any], after: Mapping[str, Any], *,
    selected_slot: int, producer_type: int = PRODUCTION_BUILDING_TYPE,
) -> str:
    """Only a stable, fully observed live producer can authorize a click."""
    for witness in (before, after):
        if not (
            witness.get("status") == "OBSERVED"
            and witness.get("selected_slot") == selected_slot
            and witness.get("owner") == 0
            and witness.get("type") == producer_type == PRODUCTION_BUILDING_TYPE
            and all(isinstance(witness.get(field), int) for field in (
                "command", "production_type", "progress", "reserved", "rice", "wood",
            ))
        ):
            return "UNKNOWN"
    if before.get("command") == 15 or any(before.get(field) != after.get(field) for field in (
        "command", "production_type", "progress",
    )):
        return "UNKNOWN"
    return "PASS"


def _minimap_target_from_lut(
    widget_x: int, widget_y: int, lut: bytes,
    target_world: tuple[int, int] | None = None,
) -> dict[str, Any] | None:
    """Choose a baked LUT pixel for the target world point, never a guessed point."""
    if len(lut) != MINIMAP_LUT_SIZE:
        return None
    center_x = widget_x + MINIMAP_LUT_WIDTH // 2
    center_y = widget_y + MINIMAP_LUT_HEIGHT // 2
    baked: list[tuple[int, int, int, int]] = []
    for row in range(MINIMAP_LUT_HEIGHT):
        dy = row + 1
        screen_y = widget_y + dy
        if not widget_y < screen_y < widget_y + MINIMAP_LUT_HEIGHT:
            continue
        for col in range(MINIMAP_LUT_WIDTH + 1):
            screen_x = widget_x + col
            if not widget_x <= screen_x <= widget_x + MINIMAP_LUT_WIDTH:
                continue
            if not 0 <= screen_x < 800 or not 0 <= screen_y < 600:
                continue
            index = (row * MINIMAP_LUT_WIDTH + col) * 2
            if index + 1 >= len(lut):
                continue
            dx, dy_value = lut[index], lut[index + 1]
            if dx != 0xFF and dy_value != 0xFF:
                baked.append((screen_x, screen_y, dx, dy_value))
    if not baked:
        return None
    if target_world is None:
        x, y, dx, dy = min(
            baked, key=lambda item: (item[0] - center_x) ** 2 + (item[1] - center_y) ** 2,
        )
    else:
        target_x, target_y = target_world
        x, y, dx, dy = min(
            baked, key=lambda item: (
                (item[2] - target_x) ** 2 + (item[3] - target_y) ** 2,
                (item[0] - center_x) ** 2 + (item[1] - center_y) ** 2,
            ),
        )
    return {
        "screen_xy": [x, y], "lut_bytes": [dx, dy],
        "source": (
            "nearest_target_world" if target_world is not None else
            "widget_center" if (x, y) == (center_x, center_y) else "nearest_baked_pixel"
        ),
        "target_world": list(target_world) if target_world is not None else None,
        "widget_xy": [widget_x, widget_y],
        "baked_pixel_count": len(baked),
    }


def _unit_witness(
    state: Mapping[str, Any], slot: int | None,
    read_memory: Callable[[int, int], bytes] | None = None,
) -> dict[str, Any]:
    unit = next((item for item in state.get("units", [])
                 if isinstance(item, Mapping) and item.get("slot") == slot), None)
    if (not isinstance(slot, int) or slot <= 0
            or not isinstance(unit, Mapping)):
        return {"status": "UNKNOWN", "slot": slot}
    witness = {"status": "OBSERVED", "slot": slot,
               **{key: unit.get(key) for key in (
                   "owner", "type", "command", "production_type", "x", "y")}}
    if read_memory is not None:
        _capacity, unit_base, _exists_base = runtime_driver.STOCK_POOL
        address = unit_base + slot * 0x758
        witness["pending_command"] = int.from_bytes(
            read_memory(address + 0x384, 4), "little", signed=False,
        )
        witness["pending_xy"] = int.from_bytes(
            read_memory(address + 0x388, 4), "little", signed=False,
        )
    return witness


def _minimap_command_effect(
    before: Sequence[Mapping[str, Any]], after: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Require a non-empty, fully observed selection and changed order evidence."""
    after_by_slot = {row.get("slot"): row for row in after}
    rows = []
    for prior in before:
        current = after_by_slot.get(prior.get("slot"), {})
        observed = current.get("status") == "OBSERVED"
        xy_changed = observed and current.get("pending_xy") != prior.get("pending_xy")
        command_changed = observed and current.get("pending_command") != prior.get("pending_command")
        rows.append({
            "slot": prior.get("slot"), "owner": prior.get("owner"),
            "type": prior.get("type"), "pending_xy_before": prior.get("pending_xy"),
            "pending_xy_after": current.get("pending_xy"),
            "pending_xy_changed": xy_changed,
            "pending_command_before": prior.get("pending_command"),
            "pending_command_after": current.get("pending_command"),
            "pending_command_changed": command_changed,
            "observed": observed,
        })
    changed = sum(row["pending_xy_changed"] or row["pending_command_changed"] for row in rows)
    return {
        "selected_count": len(rows), "observed_count": sum(row["observed"] for row in rows),
        "changed_count": changed,
        "all_selected_changed": bool(rows) and len(rows) == len(before) and changed == len(rows),
        "rows": rows,
    }


def _minimap_command_settled(
    before: Sequence[Mapping[str, Any]], after: Sequence[Mapping[str, Any]],
) -> bool:
    """True once every selected unit consumed the order (its command id moved).

    The staged-but-unconsumed state already changes pending_xy, so the plain
    effect check can stop polling one tick early and make lanes disagree.
    """
    effect = _minimap_command_effect(before, after)
    if not effect["all_selected_changed"] or effect["observed_count"] != effect["selected_count"]:
        return False
    after_by_slot = {row.get("slot"): row for row in after}
    return all(after_by_slot[row.get("slot")].get("command") != row.get("command")
               for row in before)


def _run_lane(
    *, variant: str, bridge: Path, runtime_root: Path, artifact_root: Path,
    close_helper: Path, census: bool = False, census_state: int = 3,
    census_residual: bool = False,
    census_watch: str | None = None,
    census_watch_cache: bool = False,
    census_watch_presents: int = 0,
    census_skip_presents: int = 0,
    stale_mask: str | None = None,
    blend_size_reject_diag: bool = False,
    layer_drift: bool = False,
    screen_watch: bool = False,
    screen_watch_cache: bool = False,
    drift_samples: str | None = None,
    terrain_trace: bool = False,
    terrain_scroll: bool = False,
    terrain_scroll_hold: bool = False,
    terrain_scroll_keys: tuple[str, str] = ("DOWN", "RIGHT"),
    terrain_scroll_edge: bool = False,
    candidate_throttle: tuple[int, int] | None = None,
    hd_source: str | None = None, negative_mismatch: bool = False,
    performance_window: bool = False,
    perf_sections: bool = False,
    rice_phase_diagnostic: float | None = None,
    rice_phase_target_tick: int | None = None,
    common_tick_plan: Mapping[str, int] | None = None,
    scroll_phase_diagnostic: bool = False,
    inprocess_snapshot: bool = False,
    reference_states: Mapping[int, Mapping[str, Any]] | None = None,
    lane_label: str | None = None,
    fixture: str = "save006",
    scene_actions: str = "all",
) -> dict[str, Any]:
    if variant not in {"baseline", "candidate"}:
        raise ProbeError(f"unsupported variant: {variant}")
    if candidate_throttle is not None and variant != "candidate":
        raise ProbeError("candidate throttle is only allowed on the candidate lane")
    terrain_scroll_hold = terrain_scroll_hold or terrain_scroll_edge
    save_name, save_sha256, save_index = _fixture_pin(fixture)
    artifact_root.mkdir(parents=True, exist_ok=False)
    _, source_exe = runtime_env.validate_original_source(SOURCE)
    fixture_root = FIXTURE_SOURCE.resolve()
    manifest = runtime_env.prepare(SOURCE, runtime_root=runtime_root, bridge=bridge, timeout=90)
    run_dir = Path(manifest["output"]["run_dir"])
    game = Path(manifest["game"]["root"])
    prefix = Path(manifest["wine"]["prefix"])
    snapshot_dir = prefix / "drive_c" / "g1_state_snapshots"
    private_save = game / "save" / save_name
    shutil.copy2(fixture_root / "save" / save_name, private_save)
    if _sha256(private_save) != save_sha256:
        raise ProbeError("private save fixture hash mismatch")

    candidate = variant == "candidate"
    lane_label = lane_label or variant
    result: dict[str, Any] = {
        "schema": "syw2plus.g1-saved-scene-paired.v1",
        "variant": variant,
        "status": "UNKNOWN",
        "source_exe_sha256": _sha256(source_exe),
        "private_exe_sha256": _sha256(game / runtime_env.ORIGINAL_EXE),
        "fixture": {"name": save_name, "sha256": _sha256(private_save), "selected_index": save_index,
                    "synthetic": False, "source_root": str(fixture_root)},
        "manifest": str(run_dir / "manifest.json"),
        "private_game": str(game),
        "private_prefix": str(prefix),
        "variant_config": {"w60_mirror": candidate, "census": census,
                           "screen": "1600x1200x24", "hd_source": hd_source},
        "actions": [],
        "captures": {},
        "cleanup": {},
        "scroll_phase_attempts": [],
    }
    log_path = artifact_root / "probe.log"
    log = log_path.open("w", encoding="utf-8")
    children: list[subprocess.Popen[Any]] = []
    xvfb: subprocess.Popen[Any] | None = None
    display: str | None = None
    proc: subprocess.Popen[Any] | None = None
    gdb_proc: subprocess.Popen[Any] | None = None
    env: dict[str, str] | None = None
    terrain_control = artifact_root / "terrain-trace"
    trace_path = prefix / "drive_c" / "inmm_g1_present_trace.jsonl"
    input_trace_path = prefix / "drive_c" / "inmm_g1_input_trace.jsonl"
    scroll_arm_path = prefix / "drive_c" / "inmm_g1_scroll_trace.arm"
    perf_sections_marker: Path | None = None
    scroll_ready_path = prefix / "drive_c" / "inmm_g1_scroll_trace.ready"
    census_path = prefix / "drive_c" / "inmm_g1_census.jsonl"
    census_map_path = prefix / "drive_c" / "inmm_g1_census_map.bin"
    census_context_map_path = prefix / "drive_c" / "inmm_g1_census_context_map.bin"
    census_residual_map_path = prefix / "drive_c" / "inmm_g1_census_residual_map.bin"
    stale_mask_path = prefix / "drive_c" / "inmm_g1_stale_mask.bin"
    layer_drift_path = prefix / "drive_c" / "inmm_g1_layer_drift.jsonl"
    screen_watch_path = prefix / "drive_c" / "inmm_g1_screen_watch.jsonl"
    phase_control: Path | None = None
    receiver_ready: dict[str, Any] | None = None
    receiver_arm_tick: int | None = None
    actual_arm_tick: int | None = None
    phase_target_ticks: list[int] = []
    inprocess_snapshots: list[dict[str, Any]] = []
    throttle: _CandidateThrottle | None = None
    try:
        env = dict(os.environ)
        env.update({
            "WINEPREFIX": str(prefix), "WINEARCH": "win32", "WINEDEBUG": "-all",
            "LANG": "ko_KR.UTF-8", "LC_ALL": "ko_KR.UTF-8", "WINEDLLOVERRIDES": "ddraw=b",
            "SYW2_G1_PRESENT_TRACE": "1", "SYW2_G1_TRACE_RUN_ID": f"g1-saved-{lane_label}",
        })
        if terrain_trace or terrain_scroll or scroll_phase_diagnostic:
            env["SYW2_G1_SCROLL_TRACE"] = "1"
        if inprocess_snapshot:
            snapshot_run_id = f"{runtime_root.name}-{lane_label}"
            env.update({
                "SYW2_G1_STATE_SNAPSHOT_TICKS": ",".join(
                    str(tick) for tick in SCROLL_PHASE_TICK_PLAN.values()),
                "SYW2_G1_STATE_SNAPSHOT_DIR": r"C:\g1_state_snapshots",
                "SYW2_G1_STATE_SNAPSHOT_RUN_ID": snapshot_run_id,
            })
            result["inprocess_snapshot"] = {
                "enabled": True, "run_id": snapshot_run_id,
                "directory": str(snapshot_dir),
                "target_ticks": list(SCROLL_PHASE_TICK_PLAN.values()),
            }
        if perf_sections:
            env.update({
                "SYW2_G1_PERF_SECTIONS": "1",
                "SYW2_G1_PERF_WINDOW_ID": f"{runtime_root.name}-{variant}",
            })
        if census:
            env["SYW2_G1_CENSUS"] = "1"
            env["SYW2_G1_CENSUS_STATE"] = str(census_state)
            env["SYW2_G1_DEST_PROBE"] = "1"
            if census_residual:
                env["SYW2_G1_CENSUS_RESIDUAL"] = "1"
                if census_watch is not None:
                    env["SYW2_G1_CENSUS_WATCH"] = census_watch
                    if census_watch_cache:
                        env["SYW2_G1_CENSUS_WATCH_CACHE"] = "1"
                    if census_watch_presents:
                        env["SYW2_G1_CENSUS_WATCH_PRESENTS"] = str(census_watch_presents)
            if census_skip_presents:
                env["SYW2_G1_CENSUS_SKIP_PRESENTS"] = str(census_skip_presents)
        if candidate:
            env.update({"SYW2_G1_NATIVE_2X_BLIT": "1", "SYW2_G1_MIRROR2X": "1"})
            if hd_source is not None:
                env["SYW2_G1_HD_SOURCE"] = hd_source
            if negative_mismatch:
                env["SYW2_G1_HD_NEGATIVE_MISMATCH"] = "1"
            if stale_mask is not None:
                env["SYW2_G1_STALE_MASK"] = stale_mask
            if blend_size_reject_diag:
                env["SYW2_G1_BLEND_SIZE_REJECT_DIAG"] = "1"
            if layer_drift:
                env["SYW2_G1_LAYER_DRIFT"] = "1"
            if screen_watch:
                env["SYW2_G1_SCREEN_WATCH"] = "1"
                if screen_watch_cache:
                    env["SYW2_G1_SCREEN_WATCH_CACHE"] = "1"
            if drift_samples is not None:
                env["SYW2_G1_DRIFT_SAMPLES"] = drift_samples
        xvfb, display = runtime_env._xvfb(log, "1600x1200x24")
        env["DISPLAY"] = display
        children.append(subprocess.Popen(
            ["wine", "explorer", "/desktop=Default,1600x1200"], cwd=game,
            env=env, stdout=log, stderr=log,
        ))
        time.sleep(1)
        proc = subprocess.Popen(["wine", str(game / runtime_env.ORIGINAL_EXE)], cwd=game,
                                env=env, stdout=log, stderr=log)
        children.append(proc)
        pid = proc.pid
        wait9 = _wait_state(pid, lambda state: state.get("ps") == 9, "PS9")
        if terrain_trace:
            terrain_control.mkdir(parents=True, exist_ok=True)
            gdb_env = dict(os.environ, G1_TERRAIN_WRITER_TRACE_CONTROL=str(terrain_control))
            gdb_script = REPO / "tools" / "g1_terrain_writer_trace.py"
            gdb_log = (terrain_control / "gdb.log").open("w", encoding="utf-8")
            gdb_proc = subprocess.Popen(
                ["gdb", "-p", str(pid), "--batch", "-x", str(gdb_script)],
                env=gdb_env, stdout=gdb_log, stderr=gdb_log,
            )
            armed_deadline = time.monotonic() + 15.0
            while time.monotonic() < armed_deadline and not (terrain_control / "armed.json").exists():
                if gdb_proc.poll() is not None:
                    break
                time.sleep(0.1)
            result["terrain_trace_armed"] = (terrain_control / "armed.json").exists()
            if not result["terrain_trace_armed"]:
                raise ProbeError("terrain writer gdb trace did not arm")
        if scroll_phase_diagnostic:
            if common_tick_plan != SCROLL_PHASE_TICK_PLAN:
                raise ProbeError("scroll phase diagnostic requires the immutable r1 tick plan")
            phase_control = artifact_root / "scroll-phase-trace"
            phase_control.mkdir(parents=True, exist_ok=False)
            receiver_ready = _arm_and_wait_scroll_receiver(scroll_arm_path, scroll_ready_path)
            receiver_arm_tick = _read_sim_tick(pid)
            phase_target_ticks = [common_tick_plan[name] for name in (
                "down_input_tick", "down_observation_tick", "right_input_tick",
                "right_observation_tick", "final_observation_tick")]
            observer_script = phase_control / "observer.py"
            phase_run_nonce = uuid.uuid4().hex
            observer_script.write_text(
                _scroll_phase_trace_gdb_script(
                    pid, phase_control, phase_target_ticks, 300.0, phase_run_nonce,
                ),
                encoding="utf-8",
            )
            gdb_log = (phase_control / "gdb.log").open("w", encoding="utf-8")
            gdb_proc = subprocess.Popen(
                ["gdb", "-p", str(pid), "--batch", "-x", str(observer_script)],
                stdout=gdb_log, stderr=gdb_log,
            )
            armed_path = phase_control / "armed.json"
            armed_deadline = time.monotonic() + 30.0
            while time.monotonic() < armed_deadline and not armed_path.is_file():
                if gdb_proc.poll() is not None:
                    break
                time.sleep(0.1)
            if not armed_path.is_file():
                raise ProbeError("scroll phase GDB observer did not arm before save loading")
            armed = json.loads(armed_path.read_text(encoding="utf-8"))
            if (armed.get("inferior_pid") != pid or armed.get("hardware_breakpoints_only") is not True
                    or armed.get("run_nonce") != phase_run_nonce
                    or armed.get("target_ticks") != phase_target_ticks):
                raise ProbeError(f"scroll phase observer identity/scope mismatch: {armed}")
            actual_arm_tick = _read_sim_tick(pid)
            if actual_arm_tick >= SCROLL_PHASE_TICK_PLAN["down_input_tick"]:
                raise ProbeError(f"observer attached after first fixed input tick: {actual_arm_tick}")
        tree = runtime_env._window_tree(display, 20)
        allowed = ((1600, 1200),) if candidate else ((800, 600),)
        outer, content = runtime_env._game_window_ids(tree, allowed_sizes=allowed)
        if content is None:
            raise ProbeError(f"no content child with allowed size {allowed}")
        info = runtime_env._xwininfo_details(display, content, 20)
        size = (int(info["width"]), int(info["height"]))
        expected = (1600, 1200) if candidate else (800, 600)
        if size != expected:
            raise ProbeError(f"unexpected content size: {size}, expected {expected}")
        origin = (int(info["x"]), int(info["y"]))
        crop = (origin[0], origin[1], size[0], size[1])
        scale = 2 if candidate else 1
        result["window"] = {"origin": list(origin), "crop": list(crop), "size": list(size), "scale": scale}

        def runtime_read(address: int, amount: int) -> bytes:
            return runtime_driver.read(pid, address, amount)

        if candidate:
            result["capture_barriers"] = {"menu": _wait_for_mirror_present(
                trace_path, program_state=9,
            )}
        result["captures"]["menu"] = _capture(display, f"g1-saved-{variant}", pid, "menu", crop, artifact_root, log)
        if census and census_state == 9:
            # The PS9 menu is the measured scene: stay until its present window
            # is full, then stop before the save-load path changes the state.
            result["census_wait"] = _wait_census_presents(census_path, census_state, 120.0)
            if result["census_wait"]["status"] != "PASS":
                raise ProbeError(f"PS9 census window incomplete: {result['census_wait']}")
            # Same scene after the window: the first capture may predate the menu.
            result["captures"]["menu_after"] = _capture(
                display, f"g1-saved-{variant}", pid, "menu_after", crop, artifact_root, log)
            raise _CensusStateComplete()
        if candidate:
            # Let the first post-barrier frame finish its input dispatch before
            # sending the menu click; the 2x compositor is intentionally live
            # and can otherwise drop this transition on a busy Wine/Xvfb tick.
            time.sleep(0.5)
        load_clicks = [_inject(display, origin, LOAD_MENU, scale, env, log)]
        # XTest delivery can lose the first menu click while the live
        # presenter is still servicing a frame.  Retry only when the game is
        # observably still at PS9; never send a blind second click after the
        # state transition.
        time.sleep(1.0)
        if runtime_driver.state(pid, False).get("ps") == 9:
            load_clicks.append(_inject(display, origin, LOAD_MENU, scale, env, log))
        wait35 = _wait_state(pid, lambda state: state.get("ps") == 35, "PS35")
        result["actions"].append({"tag": "load_menu", "from": wait9, "to": wait35,
                                   "clicks": load_clicks, "result": "PASS"})

        navigation: list[int | None] = []
        navigation_delay = 0.30 if hd_source == "scale2x" else 0.12
        # The menu can coalesce a DOWN key while the 2x presenter is busy;
        # bound retries above the six steps needed for save006 rather than
        # mistaking delayed input delivery for a missing fixture.
        for _ in range(20):
            raw = runtime_read(SELECTED_INDEX_ADDRESS, 2)
            current = int.from_bytes(raw, "little") if len(raw) == 2 else None
            navigation.append(current)
            if current == save_index:
                break
            _send_down(display, env, log)
            time.sleep(navigation_delay)
        else:
            raise ProbeError(f"save slot navigation did not reach {save_index}: {navigation}")
        result["save_navigation"] = navigation
        result["navigation_delay_seconds"] = navigation_delay
        _inject(display, origin, LOAD_CONFIRM, scale, env, log)
        loaded = _wait_state(pid, lambda state: state.get("ps") == 3 and state.get("tick", 0) > 0, "loaded PS3")
        time.sleep(0.15)
        loaded_detailed = runtime_driver.state(pid, True)
        result["actions"].append({"tag": "load_fixture", "to": loaded, "result": "PASS"})
        result["scene"] = {"state": _scene_identity(loaded_detailed),
                            "snapshot": runtime_env._g1_scene_snapshot(loaded_detailed, runtime_read)}
        if rice_phase_diagnostic is not None:
            rice_control = artifact_root / "rice-phase-trace"
            rice_control.mkdir(parents=True, exist_ok=False)
            gdb_script = rice_control / "observer.py"
            loaded_tick = loaded_detailed.get("tick")
            target_tick = rice_phase_target_tick
            if target_tick is None:
                if not isinstance(loaded_tick, int):
                    raise ProbeError("rice phase diagnostic needs loaded sim tick")
                target_tick = _rice_phase_target_tick(loaded_tick)
            elif not isinstance(loaded_tick, int) or target_tick <= loaded_tick:
                raise ProbeError("rice phase target must be later than the loaded save tick")
            gdb_script.write_text(
                _rice_trace_gdb_script(pid, rice_control, rice_phase_diagnostic, target_tick),
                encoding="utf-8",
            )
            gdb_log = (rice_control / "gdb.log").open("w", encoding="utf-8")
            gdb_proc = subprocess.Popen(
                ["gdb", "-p", str(pid), "--batch", "-x", str(gdb_script)],
                stdout=gdb_log, stderr=gdb_log,
            )
            armed_deadline = time.monotonic() + 20.0
            armed_path = rice_control / "armed.json"
            while time.monotonic() < armed_deadline and not armed_path.is_file():
                if gdb_proc.poll() is not None:
                    break
                time.sleep(0.1)
            if not armed_path.is_file():
                raise ProbeError("rice writer GDB observer did not arm")
            result["rice_phase_diagnostic"] = {
                "status": "RUNNING", "armed": json.loads(armed_path.read_text(encoding="utf-8")),
                "duration_seconds": rice_phase_diagnostic,
                "target_tick": target_tick,
                "target_memory_writes": 0,
            }
            try:
                paused_path = rice_control / "paused.json"
                pause_deadline = time.monotonic() + min(rice_phase_diagnostic, 60.0)
                while time.monotonic() < pause_deadline and not paused_path.is_file():
                    if gdb_proc.poll() is not None:
                        break
                    time.sleep(0.05)
                if paused_path.is_file():
                    paused = json.loads(paused_path.read_text(encoding="utf-8"))
                    scene_at_pause = _read_batched_scene(pid, runtime_read)
                    result["rice_phase_diagnostic"].update({
                        "paused": paused,
                        "scene_snapshot_at_phase_return": scene_at_pause,
                        "all_writer_quiescence_proven_at_read": (
                            paused.get("all_stop_mode") is True
                            and paused.get("tick") == scene_at_pause.get("sim_tick_before")
                            == scene_at_pause.get("sim_tick_after")
                            and scene_at_pause.get("status") == "PASS"
                        ),
                    })
                    (rice_control / "release.flag").write_text(
                        "snapshot captured\n", encoding="utf-8"
                    )
                gdb_proc.wait(timeout=rice_phase_diagnostic * 3.0 + 60.0)
            except subprocess.TimeoutExpired as exc:
                gdb_proc.terminate()
                try:
                    gdb_proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    gdb_proc.kill()
                    gdb_proc.wait(timeout=5)
                raise ProbeError("rice writer GDB observer exceeded its bounded window") from exc
            summary_path = rice_control / "rice-writer-summary.json"
            events_path = rice_control / "rice-writer-events.jsonl"
            summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.is_file() else {}
            events = ([json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines()]
                      if events_path.is_file() else [])
            observation = _rice_phase_observation(events)
            result["rice_phase_diagnostic"].update({
                "status": observation["status"], "summary": summary,
                "observation": observation,
                "events_path": str(events_path),
                "events_sha256": _sha256(events_path) if events_path.is_file() else None,
                "summary_path": str(summary_path),
                "summary_sha256": _sha256(summary_path) if summary_path.is_file() else None,
                "gdb_exit": gdb_proc.returncode,
            })
            raise _RiceDiagnosticComplete()
        if terrain_scroll:
            loaded_tick = loaded_detailed.get("tick")
            if not isinstance(loaded_tick, int):
                raise ProbeError("common-tick schedule requires a loaded save sim_tick")
            if common_tick_plan is None:
                common_tick_plan = _build_common_tick_plan(loaded_tick)
            result["common_tick_plan"] = dict(common_tick_plan)
        if candidate:
            result.setdefault("capture_barriers", {})["loaded"] = _wait_for_mirror_present(
                trace_path, program_state=3,
            )
        result["captures"]["loaded"] = _capture(display, f"g1-saved-{variant}", pid, "loaded", crop, artifact_root, log)
        if performance_window:
            result["performance_window"] = _measure_performance_window(
                pid, prefix, runtime_read,
                window_id=f"{runtime_root.name}-{variant}",
            )
        if scene_actions == "none" and not terrain_scroll:
            if census:
                # Loaded-only census: fill the (post-skip) PS3 window before the
                # scene is torn down, otherwise the census log stays empty.
                result["census_wait"] = _wait_census_presents(
                    census_path, census_state, _census_loaded_wait_timeout(census_skip_presents))
                if result["census_wait"]["status"] != "PASS":
                    raise ProbeError(f"loaded-only census window incomplete: {result['census_wait']}")
                if census_watch_presents:
                    result["census_watch_wait"] = _wait_census_watch_summary(
                        census_path, _census_watch_wait_timeout(census_watch_presents))
            raise _LoadedOnlyComplete()

        if scroll_phase_diagnostic:
            if common_tick_plan != SCROLL_PHASE_TICK_PLAN:
                raise ProbeError("scroll phase diagnostic requires the immutable r1 tick plan")
            loaded_tick = loaded_detailed.get("tick")
            if not isinstance(loaded_tick, int) or loaded_tick >= common_tick_plan["down_input_tick"]:
                raise ProbeError(f"loaded tick is not before the fixed input schedule: {loaded_tick}")
            if phase_control is None or receiver_ready is None or receiver_arm_tick is None:
                raise ProbeError("scroll phase observer or receiver was not armed before load")
            (phase_control / "armed-tick.json").write_text(json.dumps({
                "loaded_tick": loaded_tick,
                "actual_arm_tick": actual_arm_tick,
                "receiver_arm_tick": receiver_arm_tick,
                "fixed_plan": dict(common_tick_plan),
            }, indent=2) + "\n", encoding="utf-8")
            checkpoints: list[dict[str, Any]] = []
            input_records: list[dict[str, Any]] = []
            input_specs = {
                common_tick_plan["down_input_tick"]: ("DOWN", common_tick_plan["down_observation_tick"]),
                common_tick_plan["right_input_tick"]: ("RIGHT", common_tick_plan["right_observation_tick"]),
            }
            ack_path = phase_control / "ack.json"
            for checkpoint_tick in phase_target_ticks:
                pause_path = phase_control / "paused.json"
                release_path = phase_control / "release.json"
                pause_deadline = time.monotonic() + 30.0
                while time.monotonic() < pause_deadline and not pause_path.is_file():
                    if gdb_proc.poll() is not None:
                        break
                    time.sleep(0.01)
                if not pause_path.is_file():
                    raise ProbeError(f"phase checkpoint {checkpoint_tick} was not reached")
                pause = json.loads(pause_path.read_text(encoding="utf-8"))
                checkpoint = {"tick": checkpoint_tick, "pause": pause, "snapshot": None,
                              "release": None, "ack": None}
                result["scroll_phase_attempts"].append(checkpoint)
                valid_pause, pause_reason = _scroll_live_checkpoint_preflight(
                    phase_control / "phase-events.jsonl", pause, expected_pid=pid,
                    expected_tick=checkpoint_tick, run_nonce=phase_run_nonce,
                )
                key_spec = input_specs.get(checkpoint_tick)
                key_attempted = False
                key: str | None = key_spec[0] if key_spec else None
                after_seq = 0
                before_camera: tuple[int, int] | None = None
                input_tick_before: int | None = None
                input_tick_after: int | None = None
                down_emitted_ns: int | None = None
                keyup_emitted_ns: int | None = None
                receiver_down = receiver_up = None
                camera_after: tuple[int, int] | None = None
                camera_samples: list[dict[str, Any]] = []
                snapshot: dict[str, Any] = {"status": "SKIP_INVALID_PAUSE", "reason": pause_reason}
                release: dict[str, Any] = {
                    "nonce": pause.get("nonce"), "run_nonce": phase_run_nonce,
                    "tick": checkpoint_tick,
                    "status": "INVALID_CLEANUP" if not valid_pause else "RELEASE",
                }
                try:
                    if valid_pause:
                        snapshot = _read_batched_scene(pid, runtime_read)
                        checkpoint["snapshot"] = snapshot
                        valid_pause, pause_reason = _scroll_live_checkpoint_preflight(
                            phase_control / "phase-events.jsonl", pause, expected_pid=pid,
                            expected_tick=checkpoint_tick, run_nonce=phase_run_nonce,
                        )
                        if (not valid_pause or snapshot.get("status") != "PASS"
                                or snapshot.get("sim_tick_before") != checkpoint_tick
                                or snapshot.get("sim_tick_after") != checkpoint_tick):
                            release["status"] = "INVALID_CLEANUP"
                            release["reason"] = pause_reason or "snapshot tick/census changed"
                        else:
                            if key is not None:
                                input_tick_before = _read_sim_tick(pid)
                                before_camera = runtime_env._read_camera(runtime_read)
                                prior = _latest_scroll_keydown(input_trace_path, key)
                                after_seq = prior["seq"] if prior is not None else 0
                                key_attempted = True
                                down_emitted_ns = _send_key_edge(display, env, key, down=True)
                                input_tick_after = _read_sim_tick(pid)
                                if (input_tick_before != checkpoint_tick
                                        or input_tick_after != checkpoint_tick):
                                    release["status"] = "INVALID_CLEANUP"
                                    release["reason"] = "input tick changed while checkpoint paused"
                    checkpoint["release"] = dict(release)
                    release, ack = _scroll_release_and_ack(
                        release_path, ack_path, nonce=str(pause.get("nonce")),
                        tick=checkpoint_tick, run_nonce=phase_run_nonce,
                        expected_threads=pause.get("threads", []),
                        status=release["status"],
                    )
                    checkpoint["release"] = release
                    checkpoint["ack"] = ack
                    with contextlib.suppress(FileNotFoundError):
                        ack_path.unlink()
                    if key is not None and key_attempted and release["status"] == "RELEASE":
                        drive_deadline = time.monotonic() + 2.0
                        camera_after = before_camera
                        while time.monotonic() < drive_deadline:
                            receiver_down = _latest_scroll_keydown(
                                input_trace_path, key, after_seq=after_seq,
                            )
                            camera_after = runtime_env._read_camera(runtime_read)
                            camera_samples.append({"monotonic_ns": time.monotonic_ns(),
                                                  "camera": camera_after})
                            if camera_after != before_camera:
                                break
                            time.sleep(0.001)
                        keyup_emitted_ns = _send_key_edge(display, env, key, down=False)
                        key_attempted = False
                        up_deadline = time.monotonic() + 3.0
                        while time.monotonic() < up_deadline:
                            receiver_down = _latest_scroll_keydown(
                                input_trace_path, key, after_seq=after_seq,
                            )
                            receiver_up = (_latest_scroll_keyup(
                                input_trace_path, key, after_seq=receiver_down["seq"])
                                if receiver_down is not None else None)
                            if receiver_up is not None:
                                break
                            time.sleep(0.01)
                        expected_camera = _expected_scroll_camera(before_camera, key)
                        input_record = {
                            "key": key, "target_input_tick": checkpoint_tick,
                            "target_observation_tick": key_spec[1],
                            "input_tick_before": input_tick_before,
                            "input_tick_after": input_tick_after,
                            "down_emitted_ns": down_emitted_ns,
                            "keyup_emitted_ns": keyup_emitted_ns,
                            "camera_before": before_camera, "camera_after": camera_after,
                            "expected_one_step_camera": expected_camera,
                            "camera_samples": camera_samples,
                            "receiver_keydown": receiver_down, "receiver_keyup": receiver_up,
                            "receiver_ready": receiver_ready,
                            "valid": (input_tick_before == checkpoint_tick
                                      and input_tick_after == checkpoint_tick
                                      and camera_after == expected_camera
                                      and receiver_down is not None and receiver_up is not None
                                      and receiver_down.get("message") == 0x100
                                      and receiver_up.get("message") == 0x101),
                        }
                        input_records.append(input_record)
                        if not input_record["valid"]:
                            raise ProbeError(f"fixed {key} receiver input evidence invalid: {input_record}")
                finally:
                    if key_attempted and key is not None:
                        try:
                            keyup_emitted_ns = _send_key_edge(display, env, key, down=False)
                        except Exception as keyup_exc:
                            checkpoint["keyup_error"] = f"{type(keyup_exc).__name__}: {keyup_exc}"
                            raise
                        finally:
                            checkpoint["keyup_emitted_ns"] = keyup_emitted_ns
                            checkpoint["keyup_attempted"] = True
                    if checkpoint["ack"] is None:
                        # Always release an invalid checkpoint so a failed consumer cannot strand GDB.
                        cleanup_release = {**release, "status": "INVALID_CLEANUP"}
                        checkpoint["release"] = cleanup_release
                        with contextlib.suppress(ProbeError):
                            _, checkpoint["ack"] = _scroll_release_and_ack(
                                release_path, ack_path,
                                nonce=str(pause.get("nonce")), tick=checkpoint_tick,
                                run_nonce=phase_run_nonce, expected_threads=pause.get("threads", []),
                                status="INVALID_CLEANUP", timeout=3.0,
                            )
                if checkpoint["release"].get("status") != "RELEASE":
                    raise ProbeError(
                        f"phase checkpoint rejected before input/snapshot acceptance: "
                        f"tick={checkpoint_tick} release={checkpoint['release']}"
                    )
                checkpoints.append(checkpoint)
            try:
                gdb_proc.wait(timeout=30)
            except subprocess.TimeoutExpired as exc:
                raise ProbeError("scroll phase observer did not finish after final release") from exc
            events_path = phase_control / "phase-events.jsonl"
            events = ([json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines()]
                      if events_path.is_file() else [])
            summary_path = phase_control / "summary.json"
            summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.is_file() else {}
            phase_observation = _scroll_phase_observation(
                events, checkpoints, expected_pid=pid, expected_ticks=phase_target_ticks,
            )
            result["scroll_phase_diagnostic"] = {
                "status": phase_observation["status"], "variant": variant,
                "lane_label": lane_label, "loaded_tick": loaded_tick,
                "actual_arm_tick": actual_arm_tick,
                "receiver_arm_tick": receiver_arm_tick,
                "tick_plan": dict(common_tick_plan), "inputs": input_records,
            "checkpoints": checkpoints, "phase_observation": phase_observation,
                "observer_summary": summary, "observer_exit": gdb_proc.returncode,
                "bridge_sha256": _sha256(bridge),
                "close_helper_sha256": _sha256(close_helper),
                "input_trace_sha256": _sha256(input_trace_path)
                if input_trace_path.is_file() else None,
                "events_path": str(events_path),
                "events_sha256": _sha256(events_path) if events_path.is_file() else None,
                "summary_path": str(summary_path),
                "summary_sha256": _sha256(summary_path) if summary_path.is_file() else None,
                "target_memory_writes": 0,
            }
            result["status"] = "DIAGNOSTIC_ONLY"
            raise _RiceDiagnosticComplete()

        if terrain_trace:
            # A real keyboard pan, after PS3/load, supplies the natural redraw
            # requested by the terrain attribution card.  Keep the input and
            # camera observation in the artifact; no game memory is written.
            camera_before_redraw = runtime_env._read_camera(runtime_read)
            stale_before_redraw = _latest_mirror_stale(trace_path)
            redraw_attempts: list[dict[str, Any]] = []
            camera_after_redraw = camera_before_redraw
            stale_before_scroll: int | None = None
            stale_after_scroll: int | None = None
            scroll_trace_start: int | None = None
            for key in TERRAIN_SCROLL_KEYS:
                before_key = runtime_env._read_camera(runtime_read)
                stale_before_key = _latest_mirror_stale(trace_path)
                trace_start = _trace_line_count(trace_path)
                scroll_arm_path.write_text("armed\n", encoding="ascii")
                _send_key(display, env, key, log, repeat=1, hold_ms=150)
                receiver_event = None
                receiver_keyup = None
                after_key = before_key
                receive_deadline = time.monotonic() + 2.0
                while time.monotonic() < receive_deadline:
                    receiver_event = _latest_scroll_keydown(
                        input_trace_path, key,
                        after_seq=(receiver_event or {}).get("seq", 0),
                    )
                    if receiver_event is not None:
                        receiver_keyup = _latest_scroll_keyup(
                            input_trace_path, key, after_seq=receiver_event["seq"],
                        )
                    after_key = runtime_env._read_camera(runtime_read)
                    if (receiver_event is not None and receiver_keyup is not None
                            and after_key != before_key):
                        break
                    time.sleep(0.05)
                stale_after_key = _latest_mirror_stale(trace_path)
                redraw_attempts.append({"input": key, "before": before_key,
                                        "after": after_key,
                                        "game_wm_keydown": receiver_event,
                                        "game_wm_keyup": receiver_keyup,
                                        "game_hold_ms": (
                                            receiver_keyup["ts_ms"] - receiver_event["ts_ms"]
                                            if receiver_event is not None and receiver_keyup is not None
                                            else None),
                                        "receiver_observed": receiver_event is not None,
                                        "stale_before": stale_before_key,
                                        "stale_after": stale_after_key,
                                        "stale_delta": (
                                            stale_after_key - stale_before_key
                                            if isinstance(stale_before_key, int)
                                            and isinstance(stale_after_key, int) else None),
                                        "changed": before_key != after_key})
                camera_after_redraw = after_key
                if before_key != after_key:
                    if receiver_event is not None:
                        stale_before_scroll = stale_before_key
                        stale_after_scroll = stale_after_key
                        scroll_trace_start = trace_start
                    break
            scroll_coverage = (
                _wait_for_terrain_scroll_coverage(
                    trace_path, after_line_count=scroll_trace_start,
                    camera_before=next(
                        item["before"] for item in redraw_attempts
                        if item["changed"]
                    ),
                ) if scroll_trace_start is not None else
                {"status": "SKIP", "reason": (
                    "camera changed without game WM_KEYDOWN receipt"
                    if camera_before_redraw != camera_after_redraw else "camera did not change"
                )}
            )
            result["terrain_redraw"] = {
                "attempts": redraw_attempts,
                "camera_before": camera_before_redraw,
                "camera_after": camera_after_redraw,
                "changed": camera_before_redraw != camera_after_redraw,
                "stale_before": stale_before_redraw,
                "stale_after": stale_after_scroll,
                "stale_delta": (
                    stale_after_scroll - stale_before_scroll
                    if isinstance(stale_before_scroll, int)
                    and isinstance(stale_after_scroll, int) else None),
                "coverage_within_30_presents": scroll_coverage,
            }

        if terrain_scroll:
            barrier = _wait_for_scroll_settled(
                pid, runtime_read, trace_path, candidate=candidate,
            )
            scroll_actions: list[dict[str, Any]] = []
            camera_before_sequence = runtime_env._read_camera(runtime_read)
            if barrier.get("status") != "PASS":
                raise ProbeError(f"PS3 terrain/camera settle barrier failed: {barrier}")
            receiver_ready = _arm_and_wait_scroll_receiver(scroll_arm_path, scroll_ready_path)
            fixed_camera_coverage = (
                _wait_fixed_camera_coverage(trace_path, camera_before_sequence)
                if candidate else {"status": "UNAVAILABLE"}
            )
            if candidate and perf_sections:
                perf_sections_marker = _arm_perf_sections_marker(prefix)
            if terrain_scroll_edge:
                _send_pointer_edge(display, env, "UP", down=False,
                                   origin=origin, scale=scale)
            for slot_name, key in zip(("down", "right"), terrain_scroll_keys):
                input_tick_name = f"{slot_name}_input_tick"
                observation_tick_name = f"{slot_name}_observation_tick"
                input_target = common_tick_plan.get(input_tick_name) if common_tick_plan else None
                observation_target = common_tick_plan.get(observation_tick_name) if common_tick_plan else None
                if not isinstance(input_target, int) or not isinstance(observation_target, int):
                    raise ProbeError(f"common tick plan missing {key} targets: {common_tick_plan}")
                # Finish file-backed diagnostics and arm the receiver before
                # the exact input tick. Reading the trace after the barrier can
                # consume the tick before the key edge is emitted.
                before_key = runtime_env._read_camera(runtime_read)
                trace_start = _trace_line_count(trace_path)
                key_before_coverage = _terrain_coverage_p50(
                    trace_path, before_line_count=trace_start,
                ) if candidate else None
                key_before_layer_metrics = _latest_layer_metrics(trace_path) if candidate else {}
                previous_down = _latest_scroll_keydown(input_trace_path, key)
                after_seq = previous_down["seq"] if previous_down is not None else 0
                keydown_seq = 0
                scroll_arm_path.write_text("armed\n", encoding="ascii")
                input_barrier = _wait_for_exact_tick(pid, input_target)
                if input_barrier.get("status") != "PASS":
                    scroll_actions.append({"key": key, "valid": False,
                                           "input_tick_barrier": input_barrier,
                                           "target_input_tick": input_target})
                    break
                input_camera = runtime_env._read_camera(runtime_read)
                if input_camera != before_key:
                    scroll_actions.append({"key": key, "valid": False,
                                           "input_tick_barrier": input_barrier,
                                           "target_input_tick": input_target,
                                           "camera_before": before_key,
                                           "camera_at_input_tick": input_camera,
                                           "reason": "camera changed before scheduled key edge"})
                    break
                if candidate_throttle is not None and throttle is None:
                    # H-LD: slow only this candidate game process from the first input tick on.
                    target_error = _throttle_target_error(
                        pid=pid, expected_pid=proc.pid, variant=variant,
                        game_dir=str(game), exe_name=runtime_env.ORIGINAL_EXE,
                        info=_read_proc_info(pid),
                    )
                    if target_error is not None:
                        raise ProbeError(target_error)
                    throttle = _CandidateThrottle(pid, *candidate_throttle)
                    throttle.start()
                receiver_up = None
                key_drive = _send_scroll_until_camera_change(
                    display, env, key, before_key, input_trace_path,
                    after_seq=after_seq,
                    read_camera=lambda: runtime_env._read_camera(runtime_read),
                    read_sim_tick=lambda: _read_sim_tick(pid),
                    release_at_tick=(
                        observation_target - SCROLL_HOLD_RELEASE_LEAD_TICKS
                        if terrain_scroll_hold else None),
                    **({"timeout": 10.0} if terrain_scroll_hold else {}),
                    **({"send_edge": functools.partial(
                        _send_pointer_edge, origin=origin, scale=scale)}
                       if terrain_scroll_edge else {}),
                )
                receiver_down = key_drive["receiver_down"]
                after_key = key_drive["camera"]
                keydown_seq = receiver_down["seq"] if receiver_down is not None else 0
                keyup_deadline = time.monotonic() + (0.0 if terrain_scroll_edge else 2.0)
                while time.monotonic() < keyup_deadline:
                    receiver_down = _latest_scroll_keydown(
                        input_trace_path, key, after_seq=after_seq,
                    )
                    if receiver_down is not None:
                        keydown_seq = receiver_down["seq"]
                    receiver_up = _latest_scroll_keyup(
                        input_trace_path, key, after_seq=keydown_seq,
                    ) if keydown_seq else None
                    if receiver_up is not None:
                        break
                    time.sleep(0.02)
                input_scene = (
                    _snapshot_with_live_read(
                        pid, runtime_read, snapshot_dir / f"state-{input_target}.bin",
                        target_tick=input_target, run_id=snapshot_run_id,
                    ) if inprocess_snapshot else None
                )
                if input_scene is not None:
                    inprocess_snapshots.append(input_scene)
                after_key = runtime_env._read_camera(runtime_read)
                camera_changed = before_key != after_key
                expected_camera = _expected_scroll_camera(before_key, key)
                exact_one_step = after_key == expected_camera
                scroll_steps = _scroll_camera_steps(before_key, after_key, key)
                scroll_motion_ok = (scroll_steps is not None and scroll_steps >= 1
                                    if terrain_scroll_hold else exact_one_step)
                if inprocess_snapshot:
                    scene_read = _snapshot_with_live_read(
                        pid, runtime_read, snapshot_dir / f"state-{observation_target}.bin",
                        target_tick=observation_target, run_id=snapshot_run_id,
                    )
                    observation_barrier = {
                        "status": scene_read.get("status"),
                        "target_tick": observation_target,
                        "observed_tick": scene_read.get("state_sim_tick"),
                        "source": scene_read.get("source"),
                    }
                    inprocess_snapshots.append(scene_read)
                else:
                    observation_barrier = _wait_for_exact_tick(pid, observation_target)
                    scene_read = (_read_batched_scene(pid, runtime_read)
                                  if observation_barrier.get("status") == "PASS" else
                                  {"status": "INVALID", "reason": "observation target missed",
                                   "target_tick": observation_target})
                if (inprocess_snapshot and scene_read.get("status") == "PASS"
                        and not _scene_owner_count_invariant(scene_read.get("state", {}))):
                    scene_read["status"] = "INVALID"
                    scene_read["owner_count_invariant"] = False
                coverage = (
                    _wait_for_terrain_scroll_coverage(
                        trace_path, after_line_count=trace_start,
                        camera_before=before_key,
                        observation_tick=observation_target,
                        observation_qpc=(scene_read.get("header", {}).get("qpc")
                                         if isinstance(scene_read.get("header"), Mapping)
                                         else None),
                    )
                    if candidate and scroll_motion_ok else
                    {"status": "UNAVAILABLE", "reason": "baseline lane has no mirror coverage trace"}
                )
                scene_after_action = (_scene_identity(scene_read["state"])
                                      if scene_read.get("status") == "PASS" else None)
                after_layer_metrics = coverage.get("layer_metrics", {})
                move_delta = (after_layer_metrics.get("layer_move_calls", 0)
                              - key_before_layer_metrics.get("layer_move_calls", 0))
                transfer_delta = (after_layer_metrics.get("layer_transfer_calls", 0)
                                  - key_before_layer_metrics.get("layer_transfer_calls", 0))
                coverage_p50 = coverage.get("coverage_p50_pixels")
                scroll_gate = {
                    "status": "PASS" if (
                        isinstance(coverage_p50, int) and coverage_p50 >= 264_000
                        and isinstance(key_before_coverage, int)
                        and coverage_p50 >= key_before_coverage * 0.9
                        and after_layer_metrics.get("layer_move_unsupported") == 0
                        and move_delta > 0 and transfer_delta > 0
                        and after_layer_metrics.get("hd_mask_outside_diff_subpixels") == 0
                    ) else "HOLD",
                    "p50_at_least_264000": isinstance(coverage_p50, int) and coverage_p50 >= 264_000,
                    "p50_at_least_90_percent_of_key_before": (
                        isinstance(coverage_p50, int) and isinstance(key_before_coverage, int)
                        and coverage_p50 >= key_before_coverage * 0.9
                    ),
                    "layer_move_delta": move_delta, "layer_transfer_delta": transfer_delta,
                    "unsupported": after_layer_metrics.get("layer_move_unsupported"),
                    "outside_diff": after_layer_metrics.get("hd_mask_outside_diff_subpixels"),
                } if candidate else {"status": "UNAVAILABLE"}
                scroll_actions.append({
                    "key": key, "before": before_key, "after": after_key,
                    "expected_one_step_camera": expected_camera,
                    "exact_one_step_camera": exact_one_step,
                    "scroll_hold": terrain_scroll_hold,
                    "scroll_edge": terrain_scroll_edge,
                    "scroll_steps": scroll_steps,
                    "scroll_clamp_free": _scroll_clamp_free(before_key, after_key),
                    "scroll_corner_clamp_free": (
                        _scroll_corner_clamp_free(before_key, after_key, key)
                        if key in _EDGE_DIAGONAL_SIGNS else None),
                    "release_at_tick": (observation_target - SCROLL_HOLD_RELEASE_LEAD_TICKS
                                        if terrain_scroll_hold else None),
                    "camera_changed": camera_changed,
                    "receiver_ready": receiver_ready,
                    "input_tick_barrier": input_barrier,
                    "target_input_tick": input_target,
                    "input_tick_before": key_drive["input_tick_before"],
                    "input_tick_after": key_drive["input_tick_after"],
                    "key_emission": {"down_monotonic_ns": key_drive["down_emitted_ns"],
                                     "up_monotonic_ns": key_drive["up_emitted_ns"],
                    "release_reason": key_drive["release_reason"]},
                    "camera_observations": key_drive["camera_samples"],
                    "target_observation_tick": observation_target,
                    "observation_tick_barrier": observation_barrier,
                    "input_scene_snapshot": input_scene,
                    "scene_snapshot": scene_read,
                    "scene_diff_from_previous": (
                        _scene_diff(scroll_actions[-1]["scene_snapshot"]["state"], scene_read["state"])
                        if scroll_actions and scroll_actions[-1].get("scene_snapshot", {}).get("status") == "PASS"
                        and scene_read.get("status") == "PASS" else None
                    ),
                    "scene_after_action": scene_after_action,
                    "game_wm_keydown": receiver_down, "game_wm_keyup": receiver_up,
                    "receiver_observed": receiver_down is not None and receiver_up is not None,
                    "receiver_waived_for_edge": terrain_scroll_edge,
                    "key_before_coverage_p50": key_before_coverage,
                    "key_before_layer_metrics": key_before_layer_metrics,
                    "scroll_gate": scroll_gate,
                    "hold_ms": (receiver_up["ts_ms"] - receiver_down["ts_ms"]
                                if receiver_down is not None and receiver_up is not None else None),
                    "coverage_30_present": coverage,
                    "valid": (input_barrier.get("status") == "PASS"
                              and key_drive["input_tick_before"] == input_target
                              and key_drive["input_tick_after"] == input_target
                              and (not inprocess_snapshot or (
                                  isinstance(input_scene, Mapping)
                                  and input_scene.get("status") == "PASS"
                                  and _scene_owner_count_invariant(input_scene.get("state", {}))))
                              and observation_barrier.get("status") == "PASS"
                              and scene_read.get("status") == "PASS"
                              and scroll_motion_ok
                              and (terrain_scroll_edge or (
                                  receiver_down is not None and receiver_up is not None))),
                })
                if not scroll_actions[-1]["valid"]:
                    break
            if perf_sections_marker is not None:
                perf_sections_marker.unlink(missing_ok=True)
                perf_sections_marker = None
            final_target = common_tick_plan.get("final_observation_tick") if common_tick_plan else None
            if inprocess_snapshot and isinstance(final_target, int):
                final_scene_read = _snapshot_with_live_read(
                    pid, runtime_read, snapshot_dir / f"state-{final_target}.bin",
                    target_tick=final_target, run_id=snapshot_run_id,
                )
                final_barrier = {"status": final_scene_read.get("status"),
                                 "target_tick": final_target,
                                 "observed_tick": final_scene_read.get("state_sim_tick"),
                                 "source": final_scene_read.get("source")}
                inprocess_snapshots.append(final_scene_read)
                if (final_scene_read.get("status") == "PASS"
                        and not _scene_owner_count_invariant(final_scene_read.get("state", {}))):
                    final_scene_read["status"] = "INVALID"
                    final_scene_read["owner_count_invariant"] = False
            else:
                final_barrier = (_wait_for_exact_tick(pid, final_target)
                                 if isinstance(final_target, int) else {"status": "INVALID"})
                if final_barrier.get("status") != "PASS":
                    final_scene_read = {"status": "INVALID", "reason": "final target tick missed",
                                        "target_tick": final_target}
                else:
                    final_scene_read = _read_batched_scene(pid, runtime_read)
            if throttle is not None:
                result["candidate_throttle"] = throttle.stop()
            snapshot_threads = [item.get("header", {}).get("thread_id")
                                for item in inprocess_snapshots]
            snapshot_reference_checks = []
            if inprocess_snapshot and reference_states is not None:
                for item in inprocess_snapshots:
                    tick = item.get("state_sim_tick")
                    expected = reference_states.get(tick)
                    equal = isinstance(expected, Mapping) and item.get("state") == expected
                    item["sampler_reference_check"] = {
                        "status": "PASS" if equal else "FAIL",
                        "tick": tick, "state_equal": equal,
                    }
                    snapshot_reference_checks.append(item["sampler_reference_check"])
            snapshot_gate = {
                "status": "PASS" if (
                    not inprocess_snapshot or (
                        len(inprocess_snapshots) == 5
                        and all(item.get("status") == "PASS" for item in inprocess_snapshots)
                        and len(set(snapshot_threads)) == 1 and snapshot_threads[0] is not None
                        and all(_scene_owner_count_invariant(item.get("state", {}))
                                for item in inprocess_snapshots)
                        and (reference_states is None or (
                            len(snapshot_reference_checks) == 5
                            and all(item.get("status") == "PASS"
                                    for item in snapshot_reference_checks)))
                    )
                ) else "HOLD",
                "snapshot_count": len(inprocess_snapshots),
                "target_ticks": [item.get("state_sim_tick") for item in inprocess_snapshots],
                "thread_ids": snapshot_threads,
                "owner_count_invariant_all": all(
                    _scene_owner_count_invariant(item.get("state", {}))
                    for item in inprocess_snapshots),
                "sampler_reference_checks": snapshot_reference_checks,
            }
            result["terrain_scroll"] = {
                "status": (
                    "INVALID" if len(scroll_actions) != 2 or
                    not all(action["valid"] for action in scroll_actions)
                    or final_scene_read.get("status") != "PASS"
                    or snapshot_gate.get("status") != "PASS" else
                    "PASS" if not candidate or all(
                        action["scroll_gate"]["status"] == "PASS" for action in scroll_actions
                    ) else "HOLD"
                ),
                "hold": terrain_scroll_hold,
                "edge": terrain_scroll_edge,
                "keys": list(terrain_scroll_keys),
                "barrier": barrier, "camera_before_sequence": camera_before_sequence,
                "fixed_camera_coverage": fixed_camera_coverage,
                "tick_plan": dict(common_tick_plan or {}),
                "final_observation_barrier": final_barrier,
                "final_scene_snapshot": final_scene_read,
                "inprocess_snapshot_gate": snapshot_gate,
                "camera_after_sequence": runtime_env._read_camera(runtime_read),
                "actions": scroll_actions,
            }
            result["terrain_scroll"]["scene_after"] = (
                _scene_identity(final_scene_read["state"])
                if final_scene_read.get("status") == "PASS" else None
            )
            result["terrain_scroll"]["final_scene_diff"] = (
                _scene_diff(scroll_actions[-1]["scene_snapshot"]["state"], final_scene_read["state"])
                if scroll_actions and scroll_actions[-1].get("scene_snapshot", {}).get("status") == "PASS"
                and final_scene_read.get("status") == "PASS" else None
            )
            # Diagnostic only (H-D2c): the screen after the last scroll observation.
            if candidate:
                result.setdefault("capture_barriers", {})["scroll_after"] = _wait_for_mirror_present(
                    trace_path, program_state=3,
                )
            result["captures"]["scroll_after"] = _capture(
                display, f"g1-saved-{variant}", pid, "scroll_after", crop, artifact_root, log,
            )
            if scene_actions == "none":
                # H-S3: the scroll window is scene independent; skip the save006-only work.
                raise _LoadedOnlyComplete()

        def selection() -> dict[str, Any]:
            return _selection_observation(runtime_read)

        before = selection()
        _inject(display, origin, SELECTION_POINT, scale, env, log)
        selected_wait = _poll_observation(
            "selection target slot 151", selection,
            lambda item: item.get("count") == 1 and item.get("selected_slot") == 151,
        )
        after = selected_wait["final"]
        result["actions"].append({"tag": "selection", "before": before, "after": after,
                                  "wait": selected_wait,
                                  "result": "PASS" if selected_wait["status"] == "PASS" else "UNKNOWN"})
        result["captures"]["selection"] = _capture(display, f"g1-saved-{variant}", pid, "selection", crop, artifact_root, log)

        empty_before = selection()
        _inject(display, origin, EMPTY_SELECTION_POINT, scale, env, log)
        empty_wait = _poll_observation("empty click clears selection", selection,
                                       lambda item: item.get("count") == 0)
        empty_after = empty_wait["final"]
        result["actions"].append({"tag": "empty_click", "before": empty_before,
                                  "after": empty_after, "wait": empty_wait,
                                  "result": "PASS" if empty_wait["status"] == "PASS" else "UNKNOWN"})

        drag_before = empty_after
        presents_before_drag = _primary_present_records(trace_path, candidate=candidate)
        present_seq_before_drag = max(
            (row.get("seq", 0) for row in presents_before_drag
             if isinstance(row.get("seq"), int)), default=0,
        )
        input_rows_before_drag = _input_trace_records(input_trace_path) if candidate else []
        input_seq_before_drag = max(
            (row.get("seq", 0) for row in input_rows_before_drag
             if isinstance(row.get("seq"), int)), default=0,
        )
        drag_input = _inject(display, origin, DRAG_FROM, scale, env, log, drag_to=DRAG_TO)
        post_input_presents = (
            _wait_for_post_release_presents(
                trace_path, input_trace_path, candidate=True,
                input_seq_before=input_seq_before_drag,
                host_return_present_seq=max(
                    (row.get("seq", 0) for row in _primary_present_records(trace_path, candidate=True)
                     if isinstance(row.get("seq"), int)), default=present_seq_before_drag,
                ),
                drag_from=DRAG_FROM, drag_to=DRAG_TO,
            )
            if candidate else {
                "status": "NOT_INSTRUMENTED",
                "reason": "baseline trace has no frame-level primary present event; the following X11 capture is retained",
                "last_primary_present_seq_before_input": present_seq_before_drag,
            }
        )
        drag_wait = _poll_stable_observation(
            "settled drag selection", selection,
            lambda item: item.get("count") != drag_before.get("count")
            or item.get("selected_slots") != drag_before.get("selected_slots"),
        )
        drag_after = drag_wait["final"]
        drag_capture_state_before = selection()
        drag_capture = _capture(display, f"g1-saved-{variant}", pid, "drag", crop, artifact_root, log)
        drag_capture_state_after = selection()
        settled_slots = drag_after.get("selected_slots")
        drag_capture_binding = _drag_capture_binding(
            candidate=candidate,
            button_up_delivered=drag_input.get("button_up") is True,
            post_input_presents=post_input_presents,
            settled_status=drag_wait.get("status", "UNKNOWN"),
            stable_samples=drag_wait.get("stable_samples", 0),
            settled_selection=settled_slots,
            selection_before_capture=drag_capture_state_before.get("selected_slots"),
            selection_after_capture=drag_capture_state_after.get("selected_slots"),
        )
        drag_capture_binding["settled_selection"]["samples"] = drag_wait.get("samples")
        drag_capture_binding["capture"] = drag_capture
        result["actions"].append({"tag": "drag", "before": drag_before, "after": drag_after,
                                  "wait": drag_wait,
                                  "input_injection": drag_input,
                                  "capture_binding": drag_capture_binding,
                                  "result": "PASS" if drag_wait["status"] == "PASS" else "UNKNOWN"})
        result["captures"]["drag"] = drag_capture

        # Test a known minimap command while the confirmed drag selection is
        # still active.  This is deliberately independent of the later HQ
        # production selection/re-centering path.
        minimap_selection_before = selection()
        minimap_slots = minimap_selection_before.get("selected_slots", [])
        minimap_count = minimap_selection_before.get("count")
        minimap_state_before = runtime_driver.state(pid, True)
        minimap_units_before = (
            [_unit_witness(minimap_state_before, slot, runtime_read)
             for slot in minimap_slots if isinstance(slot, int)]
            if isinstance(minimap_slots, list) else []
        )
        minimap_selection_valid = (
            isinstance(minimap_slots, list) and isinstance(minimap_count, int)
            and minimap_count > 0 and len(minimap_slots) == minimap_count
            and len(minimap_units_before) == len(minimap_slots)
            and all(unit.get("status") == "OBSERVED"
                    and isinstance(unit.get("owner"), int)
                    and isinstance(unit.get("type"), int) and unit.get("type") > 0
                    and isinstance(unit.get("pending_xy"), int)
                    and isinstance(unit.get("pending_command"), int)
                    for unit in minimap_units_before)
        )
        minimap_camera_before = runtime_env._read_camera(runtime_read)
        minimap_gate_before = runtime_driver.read(pid, MINIMAP_GATE_ADDRESS, 4)
        minimap_gate_record: dict[str, Any] = {
            "address": hex(MINIMAP_GATE_ADDRESS), "before_hex": minimap_gate_before.hex(),
            "written_hex": struct.pack("<I", 1).hex(),
        }
        minimap_steps: list[dict[str, Any]] = []
        minimap_final_units = minimap_units_before
        minimap_camera_after = minimap_camera_before
        minimap_result = "UNKNOWN"
        if minimap_selection_valid:
            runtime_driver.write(pid, MINIMAP_GATE_ADDRESS, struct.pack("<I", 1))
            minimap_gate_record["after_write_hex"] = runtime_driver.read(
                pid, MINIMAP_GATE_ADDRESS, 4).hex()
            try:
                # Preserve the historical plain right-click measurement first.
                right_click = _inject(
                    display, origin, MINIMAP_POINT, scale, env, log, button=3,
                )

                def minimap_observation() -> dict[str, Any]:
                    current_selection = selection()
                    current_state = runtime_driver.state(pid, True)
                    current_units = [
                        _unit_witness(current_state, slot, runtime_read)
                        for slot in minimap_slots
                    ]
                    return {
                        "camera": runtime_env._read_camera(runtime_read),
                        "selection": current_selection,
                        "units": current_units,
                    }

                def minimap_changed(item: Mapping[str, Any], prior_units: Sequence[Mapping[str, Any]]) -> bool:
                    if item.get("selection", {}).get("selected_slots") != minimap_slots:
                        return False
                    return (item.get("camera") != minimap_camera_before
                            or _minimap_command_settled(prior_units, item.get("units", [])))

                right_wait = _poll_observation(
                    "minimap right-click command or camera response", minimap_observation,
                    lambda item: minimap_changed(item, minimap_units_before), timeout=3.0,
                )
                right_final = right_wait.get("final", {})
                right_units_after = right_final.get("units", minimap_units_before)
                right_effect = _minimap_command_effect(minimap_units_before, right_units_after)
                right_camera_after = right_final.get("camera", minimap_camera_before)
                minimap_steps.append({
                    "mode": "plain_right_click", "point": list(MINIMAP_POINT),
                    "button": 3, "input": right_click,
                    "unit_effect": right_effect, "camera_after": right_camera_after,
                    "wait": right_wait,
                })
                minimap_camera_after = right_camera_after
                minimap_final_units = right_units_after
                right_pass = (right_effect["all_selected_changed"]
                              or right_camera_after != minimap_camera_before)
                if right_pass:
                    minimap_result = "PASS"
                else:
                    # Known lap768 path: select move mode, then left-click the
                    # baked, valid minimap center at (90,553).
                    move_mode = _inject(
                        display, origin, (703, 503), scale, env, log,
                    )
                    fallback_before = right_units_after
                    fallback_camera_before = right_camera_after
                    move_click = _inject(
                        display, origin, MINIMAP_POINT, scale, env, log, button=1,
                    )

                    def fallback_changed(item: Mapping[str, Any]) -> bool:
                        if item.get("selection", {}).get("selected_slots") != minimap_slots:
                            return False
                        return (item.get("camera") != fallback_camera_before
                                or _minimap_command_settled(fallback_before, item.get("units", [])))

                    fallback_wait = _poll_observation(
                        "move-mode minimap left-click command or camera response",
                        minimap_observation, fallback_changed, timeout=3.0,
                    )
                    fallback_final = fallback_wait.get("final", {})
                    minimap_final_units = fallback_final.get("units", fallback_before)
                    fallback_effect = _minimap_command_effect(
                        fallback_before, minimap_final_units,
                    )
                    fallback_total_effect = _minimap_command_effect(
                        minimap_units_before, minimap_final_units,
                    )
                    minimap_camera_after = fallback_final.get(
                        "camera", fallback_camera_before,
                    )
                    minimap_steps.append({
                        "mode": "move_then_left_click", "mode_button": [703, 503],
                        "mode_input": move_mode, "point": list(MINIMAP_POINT),
                        "button": 1, "input": move_click,
                        "unit_effect": fallback_effect,
                        "camera_before": fallback_camera_before,
                        "camera_after": minimap_camera_after, "wait": fallback_wait,
                    })
                    minimap_result = "PASS" if (
                        fallback_total_effect["all_selected_changed"]
                        or minimap_camera_after != fallback_camera_before
                    ) else "UNKNOWN"
            finally:
                runtime_driver.write(pid, MINIMAP_GATE_ADDRESS, minimap_gate_before)
                minimap_gate_record["restored_hex"] = runtime_driver.read(
                    pid, MINIMAP_GATE_ADDRESS, 4).hex()
        else:
            minimap_gate_record["restored_hex"] = minimap_gate_before.hex()
            minimap_gate_record["reason"] = "no non-empty fully observed drag selection"
        minimap_overall_effect = _minimap_command_effect(
            minimap_units_before, minimap_final_units,
        )
        result["actions"].append({
            "tag": "minimap", "input_source": "confirmed_drag_selection",
            "selection_before": minimap_selection_before,
            "selection_valid": minimap_selection_valid,
            "selected_slots": list(minimap_slots), "unit_before": minimap_units_before,
            "unit_after": minimap_final_units, "unit_effect": minimap_overall_effect,
            "camera_before": minimap_camera_before,
            "camera_after": minimap_camera_after, "steps": minimap_steps,
            "gate": minimap_gate_record,
            "result": minimap_result,
        })
        result["captures"]["minimap"] = _capture(
            display, f"g1-saved-{variant}", pid, "minimap", crop, artifact_root, log,
        )

        # Re-center the saved scene on the known owner0 HQ slot before selecting
        # it.  save006's HQ (slot1199/world 164,85) is outside the initial
        # camera used by the earlier slot151 input-parity checks.
        production_camera_before = runtime_env._read_camera(runtime_read)
        production_scene_before = runtime_driver.state(pid, True)
        production_hq_before = next(
            (item for item in production_scene_before.get("units", [])
             if isinstance(item, Mapping) and item.get("slot") == PRODUCTION_SLOT
             and item.get("owner") == 0
             and isinstance(item.get("type"), int) and item.get("type", 0) > 0),
            None,
        )
        production_target_world = (
            (production_hq_before.get("x"), production_hq_before.get("y"))
            if isinstance(production_hq_before, Mapping)
            and isinstance(production_hq_before.get("x"), int)
            and isinstance(production_hq_before.get("y"), int)
            else None
        )
        widget_x, widget_y = struct.unpack(
            "<ii", runtime_driver.read(pid, MINIMAP_WIDGET_ADDRESS, 8),
        )
        production_lut = runtime_driver.read(
            pid, MINIMAP_WIDGET_ADDRESS + MINIMAP_LUT_A_OFFSET, MINIMAP_LUT_SIZE,
        )
        production_minimap_target = _minimap_target_from_lut(
            widget_x, widget_y, production_lut,
            target_world=production_target_world,
        )
        production_gate_before = runtime_driver.read(pid, MINIMAP_GATE_ADDRESS, 4)
        production_reposition_click = None
        production_camera_after = production_camera_before
        production_gate_after_write = None
        production_gate_restored = None
        try:
            runtime_driver.write(pid, MINIMAP_GATE_ADDRESS, struct.pack("<I", 1))
            production_gate_after_write = runtime_driver.read(pid, MINIMAP_GATE_ADDRESS, 4)
            if production_gate_after_write != struct.pack("<I", 1):
                raise ProbeError("production minimap diagnostic gate did not enable")
            if production_minimap_target is not None:
                production_reposition_click = _inject(
                    display, origin, tuple(production_minimap_target["screen_xy"]),
                    scale, env, log,
                )
                time.sleep(0.5)
                production_camera_after = runtime_env._read_camera(runtime_read)
        finally:
            runtime_driver.write(pid, MINIMAP_GATE_ADDRESS, production_gate_before)
            production_gate_restored = runtime_driver.read(pid, MINIMAP_GATE_ADDRESS, 4)
        if production_gate_restored != production_gate_before:
            raise ProbeError("production minimap diagnostic gate did not restore exact bytes")
        production_reposition = {
            "camera_before": production_camera_before,
            "camera_after": production_camera_after,
            "hq_world_before": list(production_target_world)
            if production_target_world is not None else None,
            "minimap_target": production_minimap_target,
            "gate_before_hex": production_gate_before.hex(),
            "gate_after_write_hex": production_gate_after_write.hex()
            if production_gate_after_write is not None else None,
            "gate_restored_hex": production_gate_restored.hex()
            if production_gate_restored is not None else None,
            "click": production_reposition_click,
        }
        _inject(display, origin, PRODUCTION_SELECTION_POINT, scale, env, log)
        production_selection_wait = _poll_observation(
            "owner0 HQ selection", selection,
            lambda item: item.get("count") == 1 and item.get("selected_slot") == PRODUCTION_SLOT,
        )
        production_selection = production_selection_wait["final"]
        detailed_before = runtime_driver.state(pid, True)
        selected_slot = production_selection.get("selected_slot")
        selected_unit = next((item for item in detailed_before.get("units", [])
                              if isinstance(item, Mapping) and item.get("slot") == selected_slot), None)
        production_target = {
            "selection": production_selection,
            "wait": production_selection_wait,
            "unit": selected_unit,
            "expected_owner": 0,
            "expected_type": PRODUCTION_BUILDING_TYPE,
            "valid": _valid_production_target(
                production_selection,
                selected_unit if isinstance(selected_unit, Mapping) else None,
                expected_slot=PRODUCTION_SLOT,
                expected_type=PRODUCTION_BUILDING_TYPE,
            ),
        }
        producer_type = PRODUCTION_BUILDING_TYPE
        production_control_before = _production_witness(detailed_before, int(selected_slot)) \
            if isinstance(selected_slot, int) else {"status": "UNKNOWN"}
        # Establish a no-click control window in the same loaded scene.  This
        # separates natural tick/resource movement from the subsequent UI
        # command and prevents a pre-existing queue from being credited to it.
        control_started = time.monotonic()
        time.sleep(PRODUCTION_CONTROL_SECONDS)
        production_control_after = _production_witness(
            runtime_driver.state(pid, True), int(selected_slot)
        ) if isinstance(selected_slot, int) else {"status": "UNKNOWN"}
        production_control_result = (
            _production_control_status(
                production_control_before, production_control_after,
                selected_slot=PRODUCTION_SLOT, producer_type=producer_type,
            )
            if production_target["valid"]
            else "UNKNOWN"
        )
        production_before = runtime_driver.state(pid, True)
        issue_previous = _production_witness(production_before, int(selected_slot)) \
            if isinstance(selected_slot, int) else {"status": "UNKNOWN"}
        if production_control_result == "PASS" and _production_control_status(
            production_control_after, issue_previous, selected_slot=PRODUCTION_SLOT,
            producer_type=producer_type,
        ) != "PASS":
            production_control_result = "UNKNOWN"
        production_spec = _production_spec(
            lambda address, size: runtime_driver.read(pid, address, size),
        ) if production_target["valid"] else {}
        unit_slots_before = {
            int(item["slot"]) for item in production_before.get("units", [])
            if isinstance(item, Mapping) and item.get("owner") == 0
            and item.get("type") == PRODUCTION_UNIT_TYPE and isinstance(item.get("slot"), int)
        }
        unit_count_before = len(unit_slots_before)
        click_started = time.monotonic()
        production_click: dict[str, Any] | None = None
        if production_control_result == "PASS":
            production_click = _inject(display, origin, PRODUCTION_POINT, scale, env, log)

        def production_state() -> dict[str, Any]:
            current = runtime_driver.state(pid, True)
            return _production_witness(current, int(selected_slot)) \
                if isinstance(selected_slot, int) else {"status": "UNKNOWN"}

        production_wait = (
            _poll_production_issue(
                production_state, issue_previous, expected_slot=PRODUCTION_SLOT,
                producer_type=producer_type, queue_type=PRODUCTION_UNIT_TYPE,
                spec=production_spec,
            )
            if production_control_result == "PASS"
            else {"status": "UNKNOWN", "label": "owner0 production queue effect",
                  "samples": 0, "elapsed": time.monotonic() - control_started,
                  "final": issue_previous,
                  "acceptance": {"status": "UNKNOWN", "cost_match": "INEXACT"}}
        )
        production_after = production_wait["final"]
        result["actions"].append({"tag": "production", "before": production_before,
                                  "point": list(PRODUCTION_POINT),
                                  "reposition": production_reposition,
                                  "control_before": production_control_before,
                                  "control_after": production_control_after,
                                  "control_seconds": time.monotonic() - control_started,
                                  "control_global_delta": _production_global_delta(
                                      production_control_before, production_control_after,
                                  ),
                                  "control_result": production_control_result,
                                  "click": production_click,
                                  "target": production_target,
                                  "spec": production_spec,
                                  "unit_count_before": unit_count_before,
                                  "after_witness": production_after,
                                  "wait": production_wait,
                                  "result": "PASS" if (
                                      production_control_result == "PASS"
                                      and production_wait["status"] == "PASS"
                                  ) else "UNKNOWN",
                                  "issue_result": production_wait["status"],
                                  "issue_acceptance": production_wait.get("acceptance")})
        result["captures"]["production"] = _capture(display, f"g1-saved-{variant}", pid, "production", crop, artifact_root, log)
        completion_wait = (
            _poll_observation(
                "owner0 type31 production completion",
                lambda: runtime_driver.state(pid, True),
                lambda state: _production_completion(
                    unit_slots_before, unit_count_before, state,
                    selected_slot=PRODUCTION_SLOT,
                )["status"] == "PASS",
                timeout=max(0.0, 120.0 - (time.monotonic() - click_started)),
            ) if production_click is not None and production_wait["status"] == "PASS"
            else {"status": "UNKNOWN", "samples": 0, "elapsed": 0.0,
                  "final": production_before}
        )
        completion = _production_completion(
            unit_slots_before, unit_count_before, completion_wait["final"],
            selected_slot=PRODUCTION_SLOT,
        ) if isinstance(completion_wait.get("final"), Mapping) else {"status": "UNKNOWN"}
        for action in reversed(result["actions"]):
            if action.get("tag") == "production":
                action["completion_wait"] = completion_wait
                action["completion"] = completion
                break

        result["status"] = "PASS"
    except _RiceDiagnosticComplete:
        result["status"] = "DIAGNOSTIC_ONLY"
    except (_CensusStateComplete, _LoadedOnlyComplete):
        result["status"] = "PASS"
    except Exception as exc:
        result["status"] = "FAIL"
        result["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        if throttle is not None:
            result["candidate_throttle"] = throttle.stop()
        if perf_sections_marker is not None:
            perf_sections_marker.unlink(missing_ok=True)
        if scroll_phase_diagnostic and gdb_proc is not None and gdb_proc.poll() is None:
            stale_pause = artifact_root / "scroll-phase-trace" / "paused.json"
            if stale_pause.is_file():
                try:
                    pending = json.loads(stale_pause.read_text(encoding="utf-8"))
                    _atomic_write_json(stale_pause.parent / "release.json", {
                        "nonce": pending.get("nonce"), "tick": pending.get("tick"),
                        "run_nonce": pending.get("run_nonce"),
                        "status": "INVALID_CLEANUP",
                    })
                except (OSError, ValueError):
                    pass
            try:
                gdb_proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                gdb_proc.terminate()
                try:
                    gdb_proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    gdb_proc.kill()
                    gdb_proc.wait(timeout=5)
        if terrain_trace:
            (terrain_control / "stop.flag").write_text("stop\n", encoding="utf-8")
            if gdb_proc is not None:
                try:
                    gdb_proc.wait(timeout=60)
                except subprocess.TimeoutExpired:
                    gdb_proc.terminate()
                    gdb_proc.wait(timeout=5)
            summary_path = terrain_control / "writer-summary.json"
            if summary_path.is_file():
                result["terrain_trace"] = {
                    "summary": str(summary_path),
                    "events": str(terrain_control / "writer-events.jsonl"),
                    "summary_sha256": _sha256(summary_path),
                    "events_sha256": _sha256(terrain_control / "writer-events.jsonl")
                    if (terrain_control / "writer-events.jsonl").is_file() else None,
                }
        if (trace_path.is_file() and env is not None and display is not None
                and proc is not None and proc.poll() is None):
            try:
                owned = runtime_env._read_owned_win32_pid(trace_path, f"g1-saved-{lane_label}")
                close = runtime_env._request_owned_game_close(
                    display, int(owned["pid"]), close_helper, env,
                    time.monotonic() + 20.0, log,
                )
                result["trace_close"] = {"status": "PASS", "owned": owned, "request": close}
                proc.wait(timeout=20)
            except (OSError, subprocess.SubprocessError, runtime_env.RuntimeSafetyError, KeyError, ValueError) as exc:
                result["trace_close"] = {"status": "FAIL", "error": f"{type(exc).__name__}: {exc}"}
        for child in children:
            if child.poll() is None:
                child.terminate()
        for child in children:
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait(timeout=5)
        _close_scroll_input(display)
        try:
            subprocess.run(["wineserver", "-k"], env={"WINEPREFIX": str(prefix)},
                           stdout=log, stderr=log, timeout=10, check=False)
            subprocess.run(["wineserver", "-w"], env={"WINEPREFIX": str(prefix)},
                           stdout=log, stderr=log, timeout=10, check=False)
        except (OSError, subprocess.SubprocessError) as exc:
            result["cleanup_error"] = f"{type(exc).__name__}: {exc}"
        if xvfb is not None and xvfb.poll() is None:
            xvfb.terminate()
            try:
                xvfb.wait(timeout=5)
            except subprocess.TimeoutExpired:
                xvfb.kill()
                xvfb.wait(timeout=5)
        result["trace_exists_before_cleanup"] = trace_path.is_file()
        if trace_path.is_file():
            trace_copy = artifact_root / "trace_raw.jsonl"
            shutil.copy2(trace_path, trace_copy)
            result["trace"] = {"path": str(trace_copy), "sha256": _sha256(trace_copy)}
            if candidate:
                result["mirror_validator"] = validate_trace(trace_copy, required_states=(3, 9, 35))
                if hd_source == "identity":
                    from tools.g1_hd_identity_probe import validate_trace as validate_identity_trace

                    result["identity_validator"] = validate_identity_trace(trace_copy)
                elif hd_source == "scale2x":
                    from tools.g1_hd_scale2x_probe import validate_trace as validate_scale2x_trace

                    result["scale2x_validator"] = validate_scale2x_trace(trace_copy)
            if isinstance(result.get("performance_window"), dict):
                result["performance_window"]["primary_present"] = _performance_present_metrics(trace_copy)
        if candidate and input_trace_path.is_file():
            input_trace_copy = artifact_root / "input_trace_raw.jsonl"
            shutil.copy2(input_trace_path, input_trace_copy)
            result["input_trace"] = {
                "path": str(input_trace_copy), "sha256": _sha256(input_trace_copy),
            }
        if census_path.is_file():
            census_copy = artifact_root / "census_raw.jsonl"
            shutil.copy2(census_path, census_copy)
            result["census"] = {"path": str(census_copy), "sha256": _sha256(census_copy)}
        if census_map_path.is_file():
            census_map_copy = artifact_root / "census_map.bin"
            shutil.copy2(census_map_path, census_map_copy)
            result["census_map"] = {
                "path": str(census_map_copy), "sha256": _sha256(census_map_copy),
                "bytes": census_map_copy.stat().st_size,
            }
        if stale_mask_path.is_file():
            stale_mask_copy = artifact_root / "stale_mask.bin"
            shutil.copy2(stale_mask_path, stale_mask_copy)
            result["stale_mask"] = {
                "path": str(stale_mask_copy), "sha256": _sha256(stale_mask_copy),
                "bytes": stale_mask_copy.stat().st_size,
            }
        if layer_drift_path.is_file():
            layer_drift_copy = artifact_root / "layer_drift.jsonl"
            shutil.copy2(layer_drift_path, layer_drift_copy)
            result["layer_drift"] = {
                "path": str(layer_drift_copy), "sha256": _sha256(layer_drift_copy),
                "bytes": layer_drift_copy.stat().st_size,
            }
        if screen_watch_path.is_file():
            screen_watch_copy = artifact_root / "screen_watch.jsonl"
            shutil.copy2(screen_watch_path, screen_watch_copy)
            result["screen_watch"] = {
                "path": str(screen_watch_copy), "sha256": _sha256(screen_watch_copy),
                "bytes": screen_watch_copy.stat().st_size,
            }
        if census_residual_map_path.is_file():
            census_residual_map_copy = artifact_root / "census_residual_map.bin"
            shutil.copy2(census_residual_map_path, census_residual_map_copy)
            result["census_residual_map"] = {
                "path": str(census_residual_map_copy),
                "sha256": _sha256(census_residual_map_copy),
                "bytes": census_residual_map_copy.stat().st_size,
            }
        if census_context_map_path.is_file():
            census_context_map_copy = artifact_root / "census_context_map.bin"
            shutil.copy2(census_context_map_path, census_context_map_copy)
            result["census_context_map"] = {
                "path": str(census_context_map_copy),
                "sha256": _sha256(census_context_map_copy),
                "bytes": census_context_map_copy.stat().st_size,
            }
        if inprocess_snapshot and snapshot_dir.is_dir():
            snapshot_artifacts = artifact_root / "inprocess_snapshots"
            snapshot_artifacts.mkdir(exist_ok=True)
            copied = []
            for snapshot_file in sorted(snapshot_dir.glob("state-*.bin")):
                copied_file = snapshot_artifacts / snapshot_file.name
                shutil.copy2(snapshot_file, copied_file)
                copied.append({"path": str(copied_file), "name": copied_file.name,
                               "bytes": copied_file.stat().st_size,
                               "sha256": _sha256(copied_file)})
            trace_file = snapshot_dir / "trace.jsonl"
            if trace_file.is_file():
                copied_trace = snapshot_artifacts / "trace.jsonl"
                shutil.copy2(trace_file, copied_trace)
                result.setdefault("inprocess_snapshot", {})["trace"] = {
                    "path": str(copied_trace), "sha256": _sha256(copied_trace),
                }
            result.setdefault("inprocess_snapshot", {})["files"] = copied
        result["cleanup"]["prefix_processes_after"] = runtime_env._prefix_pids(prefix)
        if game.exists():
            shutil.rmtree(game)
        result["cleanup"]["game_removed"] = not game.exists()
        result["cleanup"]["ok"] = not result["cleanup"]["prefix_processes_after"] and result["cleanup"]["game_removed"]
        result["source_unchanged"] = _sha256(source_exe) == runtime_env.ORIGINAL_SHA256
        log.close()
        (artifact_root / "probe-result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    return result


def _validate_census_lane(lane: Mapping[str, Any], census_state: int = 3) -> dict[str, Any]:
    """Reject a census whose maps are not bound to the locked present source.

    ``census_state`` is the program state the DLL was asked to measure (PS3 by
    default); rows from another state are never accepted as that census.
    """
    census_info = lane.get("census")
    map_info = lane.get("census_map")
    context_info = lane.get("census_context_map")
    checks: dict[str, bool] = {}
    rows: list[dict[str, Any]] = []
    try:
        census_path = Path(census_info["path"])
        rows = [json.loads(line) for line in census_path.read_text(encoding="utf-8").splitlines()]
        checks["census_raw_readable"] = True
    except (KeyError, OSError, TypeError, json.JSONDecodeError):
        checks["census_raw_readable"] = False
    installs = [row for row in rows if row.get("event") == "install"]
    expected = {"terrain_context", "rle_clip", "rle_plain", "rect_fill", "block_copy",
                "rect_border", "rle_tinted_clip", "rle_tinted", "set_pixel"}
    checks["all_pinned_hooks_active"] = (
        {row.get("writer") for row in installs if row.get("status") == "active"} == expected
        and len(installs) == len(expected)
    )
    categories = [row for row in rows if row.get("event") == "writer_category"]
    checks["writer_categories_complete"] = (
        len(categories) == 10
        and {row.get("id") for row in categories} == set(range(1, 11))
        and any(row.get("writer") == "terrain_cache_transfer" for row in categories)
        and any(row.get("writer") == "dd_surface_blt" for row in categories)
    )
    presents = [row for row in rows if row.get("event") == "present_boundary"]
    checks["ps3_present_window"] = (
        0 < len(presents) <= 64
        and all(row.get("program_state") == census_state for row in presents)
        and all(row.get("census_state", 3 if census_state == 3 else None) == census_state
                for row in presents)
    )
    def _hex_value(value: Any) -> int | None:
        try:
            return int(value, 16) if isinstance(value, str) else int(value)
        except (TypeError, ValueError):
            return None

    checks["census_present_binding"] = (
        bool(presents) and all(
            row.get("binding") == "locked_source"
            and _hex_value(row.get("present_source_buffer")) not in (None, 0)
            and _hex_value(row.get("selected_buffer")) ==
                _hex_value(row.get("present_source_buffer"))
            and row.get("present_source_pitch", 0) > 0
            and row.get("map_generation_state") == census_state
            and row.get("map_write_calls", 0) > 0
            for row in presents
        )
    )
    expected_map_bytes = len(presents) * (32 + 800 * 600)
    expected_context_bytes = expected_map_bytes
    try:
        map_bytes = Path(map_info["path"]).read_bytes()
        context_bytes = Path(context_info["path"]).read_bytes()
        checks["writer_map_bytes_match"] = (
            len(map_bytes) == expected_map_bytes and expected_map_bytes > 0
        )
        checks["context_map_bytes_match"] = (
            len(context_bytes) == expected_context_bytes
            and expected_context_bytes == Path(map_info["path"]).stat().st_size
        )
        headers_match = bool(presents) and checks["writer_map_bytes_match"] and checks["context_map_bytes_match"]
        for index, row in enumerate(presents):
            expected_offset = index * (32 + 800 * 600)
            source_buffer = _hex_value(row.get("present_source_buffer"))
            source_pitch = row.get("present_source_pitch")
            selected_buffer = _hex_value(row.get("selected_buffer"))
            expected = (0x50314731, row.get("present"), 800, 600,
                        source_pitch, source_buffer, 800 * 600, census_state)
            if (row.get("map_offset") != expected_offset
                    or row.get("context_map_offset") != expected_offset
                    or row.get("map_bytes") != 800 * 600
                    or row.get("context_map_bytes") != 800 * 600
                    or source_buffer != selected_buffer):
                headers_match = False
            start = expected_offset
            end = start + 32
            try:
                writer_header = struct.unpack("<8I", map_bytes[start:end])
                context_header = struct.unpack("<8I", context_bytes[start:end])
            except struct.error:
                headers_match = False
                continue
            if writer_header != expected or context_header != expected:
                headers_match = False
                continue
            if any(value > 10 for value in map_bytes[end:end + 800 * 600]):
                headers_match = False
        checks["writer_map_headers_match"] = bool(headers_match)
        checks["buffer_context_capacity"] = any(
            row.get("event") == "buffer_context_summary"
            and row.get("buffer_context_dropped") == 0 for row in rows
        )
        surface_blt_summaries = [row for row in rows
                                 if row.get("event") == "surface_blt_summary"]
        checks["surface_blt_capture_complete"] = (
            len(surface_blt_summaries) == 1
            and surface_blt_summaries[0].get("capture_missed") == 0
            and surface_blt_summaries[0].get("calls_ps3") ==
                surface_blt_summaries[0].get("captured")
        )
    except (KeyError, OSError, TypeError):
        checks["writer_map_bytes_match"] = False
        checks["context_map_bytes_match"] = False
        checks["writer_map_headers_match"] = False
        checks["buffer_context_capacity"] = False
    return {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks,
            "present_count": len(presents), "install_count": len(installs)}


G1_CAPTURE_TAGS = ("loaded", "selection", "drag", "minimap", "production")
G1_WORLD_BLACK_EXCESS_LIMIT = 2_000
G1_SINGLE_BLACK_BLOCK_LIMIT = 2_000
G1_FOUR_BLACK_BLOCK_LIMIT = 2_000


def _single_black_blocks(baseline_image: Any, candidate_image: Any) -> int:
    """Count non-black source pixels with exactly one black candidate subpixel."""
    baseline_pixels = baseline_image.load()
    candidate_pixels = candidate_image.load()
    return sum(
        1
        for y in range(480)
        for x in range(800)
        if baseline_pixels[x, y] != (0, 0, 0)
        and sum(
            candidate_pixels[2 * x + dx, 2 * y + dy] == (0, 0, 0)
            for dy in range(2) for dx in range(2)
        ) == 1
    )


def _v2s_scale2x_reference(baseline_image: Any, candidate_image: Any) -> tuple[int, int]:
    """Split V2s against a perfect Scale2x of the 800x600 source.

    Returns ``(reference_blocks, unexplained_blocks)``. The reference applies the
    product EPX rule (`g1_scale2x_core.h`: edge clamp, all pixels written) to the
    whole source frame. ``reference_blocks`` counts non-black source pixels with
    exactly one black reference subpixel, which no full-coverage Scale2x can avoid.
    ``unexplained_blocks`` counts V2s-flagged candidate blocks whose black subpixel
    is not black at that position in the reference.
    """
    black = (0, 0, 0)
    width, height = baseline_image.size
    source = list(baseline_image.get_flattened_data())
    candidate_pixels = candidate_image.load()
    reference_blocks = unexplained_blocks = 0
    for y in range(480):
        row = y * width
        above = max(y - 1, 0) * width
        below = min(y + 1, height - 1) * width
        for x in range(width):
            e = source[row + x]
            if e == black:
                continue
            b, h = source[above + x], source[below + x]
            d, f = source[row + max(x - 1, 0)], source[row + min(x + 1, width - 1)]
            if b != h and d != f:
                reference = (d if d == b else e, f if b == f else e,
                             d if d == h else e, f if h == f else e)
            else:
                reference = (e, e, e, e)
            reference_black = tuple(pixel == black for pixel in reference)
            candidate_black = (
                candidate_pixels[2 * x, 2 * y] == black,
                candidate_pixels[2 * x + 1, 2 * y] == black,
                candidate_pixels[2 * x, 2 * y + 1] == black,
                candidate_pixels[2 * x + 1, 2 * y + 1] == black,
            )
            if sum(reference_black) == 1:
                reference_blocks += 1
            if sum(candidate_black) == 1 and not any(
                c and r for c, r in zip(candidate_black, reference_black)
            ):
                unexplained_blocks += 1
    return reference_blocks, unexplained_blocks


def _four_black_blocks(baseline_image: Any, candidate_image: Any) -> int:
    """Count non-black source pixels whose four candidate subpixels are black."""
    baseline_pixels = baseline_image.load()
    candidate_pixels = candidate_image.load()
    return sum(
        1
        for y in range(480)
        for x in range(800)
        if baseline_pixels[x, y] != (0, 0, 0)
        and candidate_pixels[2 * x, 2 * y] == (0, 0, 0)
        and candidate_pixels[2 * x + 1, 2 * y] == (0, 0, 0)
        and candidate_pixels[2 * x, 2 * y + 1] == (0, 0, 0)
        and candidate_pixels[2 * x + 1, 2 * y + 1] == (0, 0, 0)
    )


def _compare_images(
    baseline: Mapping[str, Any], candidate: Mapping[str, Any], tag: str = "loaded",
) -> dict[str, Any]:
    from PIL import Image, ImageChops

    try:
        base = Image.open(str(baseline["captures"][tag]["path"])).convert("RGB")
        cand = Image.open(str(candidate["captures"][tag]["path"])).convert("RGB")
    except (KeyError, OSError, TypeError) as exc:
        return {"status": "BLOCKED", "v2_status": "BLOCKED", "v2s_status": "BLOCKED",
                "v2s_raw_status": "BLOCKED", "v2q_status": "BLOCKED",
                "reason": f"{tag} capture unavailable: {exc}"}
    if base.size != (800, 600) or cand.size != (1600, 1200):
        return {"status": "BLOCKED", "v2_status": "BLOCKED", "v2s_status": "BLOCKED",
                "v2s_raw_status": "BLOCKED", "v2q_status": "BLOCKED",
                "reason": f"unexpected sizes: {base.size}, {cand.size}"}
    nearest = base.resize(cand.size, Image.Resampling.NEAREST)
    diff = ImageChops.difference(nearest, cand)
    differing = sum(1 for pixel in diff.get_flattened_data() if pixel != (0, 0, 0))
    baseline_black = sum(
        1 for y in range(480) for x in range(800)
        if base.getpixel((x, y)) == (0, 0, 0)
    )
    candidate_black = sum(
        1 for y in range(480) for x in range(800)
        if cand.getpixel((2 * x, 2 * y)) == (0, 0, 0)
    )
    black_excess = candidate_black - baseline_black
    single_black_blocks = _single_black_blocks(base, cand)
    reference_blocks, unexplained_blocks = _v2s_scale2x_reference(base, cand)
    four_black_blocks = _four_black_blocks(base, cand)
    return {
        "status": "PASS" if differing < nearest.width * nearest.height else "FAIL",
        "v2_status": "PASS" if black_excess <= G1_WORLD_BLACK_EXCESS_LIMIT else "FAIL",
        # W-1 (user decision 2026-10-06): the gate counts only single-black blocks
        # a perfect Scale2x of the source would not produce; raw stays a diagnostic.
        "v2s_status": "PASS" if unexplained_blocks <= G1_SINGLE_BLACK_BLOCK_LIMIT else "FAIL",
        "v2s_raw_status": "PASS" if single_black_blocks <= G1_SINGLE_BLACK_BLOCK_LIMIT else "FAIL",
        "baseline_size": list(base.size), "candidate_size": list(cand.size),
        "nearest_diff_pixels": differing, "total_pixels": nearest.width * nearest.height,
        "nearest_equal_ratio": 1.0 - differing / (nearest.width * nearest.height),
        "v2_world_black_samples": 800 * 480,
        "v2_baseline_world_black": baseline_black,
        "v2_candidate_world_black": candidate_black,
        "v2_candidate_minus_baseline_black": black_excess,
        "v2_maximum_excess": G1_WORLD_BLACK_EXCESS_LIMIT,
        "v2s_single_black_blocks": single_black_blocks,
        "v2s_scale2x_reference_blocks": reference_blocks,
        "v2s_unexplained_single_black_blocks": unexplained_blocks,
        "v2s_maximum_single_black_blocks": G1_SINGLE_BLACK_BLOCK_LIMIT,
        "v2q_status": "PASS" if four_black_blocks <= G1_FOUR_BLACK_BLOCK_LIMIT else "FAIL",
        "v2q_four_black_blocks": four_black_blocks,
        "v2q_maximum_four_black_blocks": G1_FOUR_BLACK_BLOCK_LIMIT,
    }


def _diagnostic_capture_comparisons(
    baseline: Mapping[str, Any], candidate: Mapping[str, Any], *, terrain_scroll: bool,
) -> dict[str, dict[str, Any]]:
    """Extra capture comparisons that are reported but never gate the pair."""
    if not terrain_scroll:
        return {}
    return {"scroll_after": _compare_images(baseline, candidate, "scroll_after")}


def _v2_capture_gate(comparisons: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    tag_status = {
        tag: comparisons.get(tag, {}).get("v2_status", "BLOCKED")
        for tag in G1_CAPTURE_TAGS
    }
    if all(status == "PASS" for status in tag_status.values()):
        status = "PASS"
    elif any(value == "FAIL" for value in tag_status.values()):
        status = "FAIL"
    else:
        status = "BLOCKED"
    return {"status": status, "required_tags": list(G1_CAPTURE_TAGS),
            "tag_status": tag_status}


def _v2s_capture_gate(comparisons: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    tag_status = {
        tag: comparisons.get(tag, {}).get("v2s_status", "BLOCKED")
        for tag in G1_CAPTURE_TAGS
    }
    if all(status == "PASS" for status in tag_status.values()):
        status = "PASS"
    elif any(value == "FAIL" for value in tag_status.values()):
        status = "FAIL"
    else:
        status = "BLOCKED"
    return {"status": status, "required_tags": list(G1_CAPTURE_TAGS),
            "tag_status": tag_status}


def _v2q_capture_gate(comparisons: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    tag_status = {
        tag: comparisons.get(tag, {}).get("v2q_status", "BLOCKED")
        for tag in G1_CAPTURE_TAGS
    }
    if all(status == "PASS" for status in tag_status.values()):
        status = "PASS"
    elif any(value == "FAIL" for value in tag_status.values()):
        status = "FAIL"
    else:
        status = "BLOCKED"
    return {"status": status, "required_tags": list(G1_CAPTURE_TAGS),
            "tag_status": tag_status}


def _pair_status(
    pair: Mapping[str, Any], *, performance_requested: bool,
    hd_source: str, scale2x_gate_status: str, terrain_scroll: bool,
) -> str:
    performance_comparison = pair.get("performance_comparison")
    performance_gate_pass = (
        not performance_requested
        or (isinstance(performance_comparison, Mapping)
            and performance_comparison.get("status") == "PASS")
    )
    return "PASS" if (
        pair.get("scene_state_equal") is True
        and pair.get("v2_capture_gate", {}).get("status") == "PASS"
        and pair.get("v2s_capture_gate", {}).get("status") == "PASS"
        and pair.get("v2q_capture_gate", {}).get("status") == "PASS"
        and (hd_source != "scale2x" or scale2x_gate_status == "PASS")
        and (not terrain_scroll
             or pair.get("terrain_scroll_parity", {}).get("status") == "PASS")
        and performance_gate_pass
    ) else "HOLD"


def _action(actions: list[Mapping[str, Any]], tag: str) -> Mapping[str, Any]:
    return next((item for item in actions if item.get("tag") == tag), {})


def _compare_input_effects(baseline: Mapping[str, Any], candidate: Mapping[str, Any]) -> dict[str, Any]:
    """Compare semantic input effects, keeping UNKNOWN distinct from parity."""

    base_actions = baseline.get("actions", [])
    candidate_actions = candidate.get("actions", [])
    if not isinstance(base_actions, list) or not isinstance(candidate_actions, list):
        return {"status": "UNKNOWN", "reason": "actions missing"}
    base_selection = _action(base_actions, "selection")
    cand_selection = _action(candidate_actions, "selection")
    base_empty = _action(base_actions, "empty_click")
    cand_empty = _action(candidate_actions, "empty_click")
    base_drag = _action(base_actions, "drag")
    cand_drag = _action(candidate_actions, "drag")
    base_minimap = _action(base_actions, "minimap")
    cand_minimap = _action(candidate_actions, "minimap")
    base_production = _action(base_actions, "production")
    cand_production = _action(candidate_actions, "production")
    checks = {
        "selection_target": (
            base_selection.get("result") == cand_selection.get("result") == "PASS"
            and base_selection.get("after", {}).get("selected_slots")
            == cand_selection.get("after", {}).get("selected_slots") == [151]
        ),
        "empty_click": (
            base_empty.get("result") == cand_empty.get("result") == "PASS"
            and base_empty.get("after", {}).get("count")
            == cand_empty.get("after", {}).get("count") == 0
        ),
        "drag_exact": (
            base_drag.get("result") == cand_drag.get("result") == "PASS"
            and base_drag.get("after", {}).get("selected_slots")
            == cand_drag.get("after", {}).get("selected_slots")
        ),
        "drag_capture_binding": (
            base_drag.get("capture_binding", {}).get("status")
            in ("PASS", "PASS_WITH_LIMITS")
            and cand_drag.get("capture_binding", {}).get("status") == "PASS"
        ),
        "minimap_gate_restore": (
            base_minimap.get("gate", {}).get("before_hex")
            == base_minimap.get("gate", {}).get("restored_hex")
            and cand_minimap.get("gate", {}).get("before_hex")
            == cand_minimap.get("gate", {}).get("restored_hex")
            and base_minimap.get("result") == cand_minimap.get("result") == "PASS"
            and base_minimap.get("camera_after") == cand_minimap.get("camera_after")
        ),
        "production_effect": (
            base_production.get("control_result")
            == cand_production.get("control_result") == "PASS"
            and base_production.get("issue_result")
            == cand_production.get("issue_result") == "PASS"
            and base_production.get("target", {}).get("selection", {}).get("selected_slot")
            == cand_production.get("target", {}).get("selection", {}).get("selected_slot")
            == PRODUCTION_SLOT
            and base_production.get("target", {}).get("expected_type")
            == cand_production.get("target", {}).get("expected_type")
            == PRODUCTION_BUILDING_TYPE
            and base_production.get("after_witness", {}).get("production_type")
            == cand_production.get("after_witness", {}).get("production_type")
            == PRODUCTION_UNIT_TYPE
            and base_production.get("spec") == cand_production.get("spec")
            and base_production.get("issue_acceptance", {}).get("issue_cost")
            == cand_production.get("issue_acceptance", {}).get("issue_cost")
        ),
        "production_completion": (
            base_production.get("completion", {}).get("status")
            == cand_production.get("completion", {}).get("status") == "PASS"
            and len(base_production.get("completion", {}).get("new_slots", [])) == 1
            and len(cand_production.get("completion", {}).get("new_slots", [])) == 1
        ),
    }
    return {"status": "PASS" if all(checks.values()) else "HOLD", "checks": checks}


def _compare_minimap_diagnostic_parity(
    baseline: Mapping[str, Any], candidate: Mapping[str, Any],
) -> dict[str, Any]:
    """Report original-parity when the diagnostic gate has no live effect.

    The normal input verdict must keep UNKNOWN distinct from PASS.  G1 also
    needs a separate answer for the narrower question: did the 2x path alter
    the original gated minimap behavior?  This check accepts equal UNKNOWN
    behavior only when the camera/unit observations and exact gate restore
    records match in both lanes.
    """
    base = _action(baseline.get("actions", []), "minimap")
    cand = _action(candidate.get("actions", []), "minimap")
    base_gate = base.get("gate", {})
    cand_gate = cand.get("gate", {})
    checks = {
        "same_result": base.get("result") == cand.get("result"),
        "same_camera_before_after": (
            base.get("camera_before") == cand.get("camera_before")
            and base.get("camera_after") == cand.get("camera_after")
        ),
        "same_unit_before_after": (
            base.get("unit_before") == cand.get("unit_before")
            and base.get("unit_after") == cand.get("unit_after")
        ),
        "exact_gate_restore": (
            base_gate.get("before_hex") == base_gate.get("restored_hex")
            and cand_gate.get("before_hex") == cand_gate.get("restored_hex")
            and base_gate.get("before_hex") == cand_gate.get("before_hex")
        ),
    }
    status = "PASS" if all(checks.values()) else "HOLD"
    effect = "ORIGINAL_PARITY_UNKNOWN" if status == "PASS" and base.get("result") == "UNKNOWN" else base.get("result")
    return {"status": status, "effect": effect, "checks": checks}


def _terrain_scroll_pair_parity(
    baseline: Mapping[str, Any], candidate: Mapping[str, Any], *, loaded_scene_equal: bool,
    candidate_fixed_coverage: Mapping[str, Any],
    scroll_keys: tuple[str, str] = ("DOWN", "RIGHT"),
) -> dict[str, Any]:
    base_actions = baseline.get("actions", [])
    candidate_actions = candidate.get("actions", [])
    common_plan = baseline.get("tick_plan")
    common_plan_match = isinstance(common_plan, Mapping) and common_plan == candidate.get("tick_plan")

    def snapshot_at_tick(snapshot: Mapping[str, Any], target: Any) -> bool:
        if snapshot.get("source") == "in_process_update_return":
            return (snapshot.get("state_sim_tick") == target
                    and snapshot.get("header", {}).get("tick_after") == target)
        return (snapshot.get("sim_tick_before") == target
                and snapshot.get("sim_tick_after") == target)

    action_scene_equal = (
        len(base_actions) == len(candidate_actions) == 2
        and all(base.get("scene_after_action") == cand.get("scene_after_action")
                and base.get("target_observation_tick") == cand.get("target_observation_tick")
                and base.get("scene_snapshot", {}).get("status") == "PASS"
                and cand.get("scene_snapshot", {}).get("status") == "PASS"
                and snapshot_at_tick(base.get("scene_snapshot", {}),
                                     base.get("target_observation_tick"))
                and snapshot_at_tick(cand.get("scene_snapshot", {}),
                                     cand.get("target_observation_tick"))
                for base, cand in zip(base_actions, candidate_actions))
    )
    end_state_equal = baseline.get("scene_after") == candidate.get("scene_after")
    final_snapshots_coherent = (
        baseline.get("final_scene_snapshot", {}).get("status") == "PASS"
        and candidate.get("final_scene_snapshot", {}).get("status") == "PASS"
        and snapshot_at_tick(baseline.get("final_scene_snapshot", {}),
                             common_plan.get("final_observation_tick"))
        and snapshot_at_tick(candidate.get("final_scene_snapshot", {}),
                             common_plan.get("final_observation_tick"))
    ) if isinstance(common_plan, Mapping) else False
    full_diffs = []
    if len(base_actions) == len(candidate_actions):
        for base, cand in zip(base_actions, candidate_actions):
            base_state = base.get("scene_snapshot", {}).get("state", {})
            candidate_state = cand.get("scene_snapshot", {}).get("state", {})
            full_diffs.append(_scene_diff(base_state, candidate_state))
    final_diff = _scene_diff(
        baseline.get("final_scene_snapshot", {}).get("state", {}),
        candidate.get("final_scene_snapshot", {}).get("state", {}),
    )
    complete_records_equal = all(not any(diff.values()) for diff in [*full_diffs, final_diff])
    baseline_inputs_on_target = all(
        item.get("input_tick_before") == item.get("target_input_tick")
        and item.get("input_tick_after") == item.get("target_input_tick")
        for item in base_actions
    )
    candidate_inputs_on_target = all(
        item.get("input_tick_before") == item.get("target_input_tick")
        and item.get("input_tick_after") == item.get("target_input_tick")
        for item in candidate_actions
    )
    same_order = ([item.get("key") for item in base_actions]
                  == [item.get("key") for item in candidate_actions] == list(scroll_keys))
    same_camera = ([item.get("after") for item in base_actions]
                   == [item.get("after") for item in candidate_actions])
    def snapshot_lane_ok(scroll: Mapping[str, Any]) -> bool:
        snapshots = []
        for action in scroll.get("actions", []):
            snapshots.extend((action.get("input_scene_snapshot"), action.get("scene_snapshot")))
        snapshots.append(scroll.get("final_scene_snapshot"))
        snapshots = [item for item in snapshots if isinstance(item, Mapping)]
        threads = [item.get("header", {}).get("thread_id") for item in snapshots]
        return (
            scroll.get("inprocess_snapshot_gate", {}).get("status") == "PASS"
            and len(snapshots) == 5
            and all(item.get("status") == "PASS"
                    and item.get("source") == "in_process_update_return"
                    and item.get("target_tick") == item.get("state_sim_tick")
                    and item.get("sim_tick_after") == item.get("state_sim_tick")
                    and _scene_owner_count_invariant(item.get("state", {}))
                    for item in snapshots)
            and len(set(threads)) == 1 and threads[0] is not None
        )
    snapshot_requested = any(
        scroll.get("inprocess_snapshot_gate", {}).get("status") != "PASS"
        or scroll.get("inprocess_snapshot_gate", {}).get("snapshot_count", 0) > 0
        for scroll in (baseline, candidate)
    )
    snapshot_source_valid = (
        snapshot_lane_ok(baseline) and snapshot_lane_ok(candidate)
        if snapshot_requested else True
    )
    return {
        "status": "PASS" if (
            baseline.get("status") == candidate.get("status") == "PASS"
            and same_order and same_camera and loaded_scene_equal
            and common_plan_match and action_scene_equal and end_state_equal
            and final_snapshots_coherent and complete_records_equal
            and baseline_inputs_on_target and candidate_inputs_on_target
            and snapshot_source_valid
            and candidate_fixed_coverage.get("status") == "PASS"
        ) else "HOLD",
        "same_order": same_order,
        "same_camera_after_each_key": same_camera,
        "loaded_scene_state_equal": loaded_scene_equal,
        "action_scene_state_equal": action_scene_equal,
        "common_tick_plan_match": common_plan_match,
        "baseline_inputs_on_target": baseline_inputs_on_target,
        "candidate_inputs_on_target": candidate_inputs_on_target,
        "final_snapshots_coherent": final_snapshots_coherent,
        "complete_records_equal": complete_records_equal,
        "action_full_state_diffs": full_diffs,
        "final_full_state_diff": final_diff,
        "candidate_fixed_camera_coverage": candidate_fixed_coverage,
        "end_game_state_equal": end_state_equal,
        "inprocess_snapshot_source_valid": snapshot_source_valid,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--census-only", action="store_true")
    parser.add_argument("--census-residual", action="store_true",
                        help="also record unhooked (shadow-compare) pixels per present; diagnostic opt-in")
    parser.add_argument("--census-watch", metavar="X,Y",
                        help="arm a hardware write watchpoint on this present-source pixel to find its writer EIP; diagnostic opt-in")
    parser.add_argument("--census-watch-cache", action="store_true",
                        help="watch the same X,Y in the 1x terrain cache (0xBA3D30, pitch 832) instead of the screen buffer; diagnostic opt-in")
    parser.add_argument("--census-watch-presents", type=int, default=0, metavar="N",
                        help="keep the watch armed for N target-state presents after arming (0-9999; 0 = until detach) and wait for its summary; diagnostic opt-in")
    parser.add_argument("--census-skip-presents", type=int, default=0, metavar="N",
                        help="skip the first N target-state presents before the 64-present census window starts (0-9999); diagnostic opt-in")
    parser.add_argument("--stale-mask", metavar="SPEC",
                        help="candidate lane: dump 800x600 covered/stale maps for these PS3 present ordinals (e.g. 6-12,300); diagnostic opt-in")
    parser.add_argument("--blend-size-reject-diag", action="store_true",
                        help="candidate lane: reproduce the lap1083 size reject of 0x467580/0x467B00 (H-ULc control run); diagnostic opt-in")
    parser.add_argument("--layer-drift", action="store_true",
                        help="candidate lane: record the 1x terrain-cache layer drift (sample points and rect counters per PS3 present, compose outcomes); diagnostic opt-in")
    parser.add_argument("--screen-watch", action="store_true",
                        help="candidate lane (needs --layer-drift): hardware write watch on the three screen sample points of every process thread (EIP/thread/value per hit); diagnostic opt-in")
    parser.add_argument("--screen-watch-cache", action="store_true",
                        help="candidate lane (needs --screen-watch): watch the sample points in the 1x terrain cache (0xBA3D30, pitch 832) instead of the screen buffer; diagnostic opt-in")
    parser.add_argument("--drift-samples", metavar="X,Y;X,Y;X,Y",
                        help="candidate lane (needs --layer-drift): move the three drift/screen-watch sample points to these 800x600 screen pixels; diagnostic opt-in")
    parser.add_argument("--census-state", type=int, choices=(3, 9), default=3,
                        help="program state the --census-only run measures (default PS3 save load; 9 = menu)")
    parser.add_argument("--terrain-trace", action="store_true")
    parser.add_argument("--terrain-scroll", action="store_true",
                        help="run same-key DOWN/RIGHT scroll input without gdb terrain tracing")
    parser.add_argument("--terrain-scroll-hold", action="store_true",
                        help="hold each scroll key until the simulation reaches the release tick (continuous scroll) instead of releasing on the first camera change")
    parser.add_argument("--terrain-scroll-edge", action="store_true",
                        help="edge-of-screen mouse scroll (XTest pointer at the top then bottom window edge, released to center) held until the release tick, instead of key hold; UP,DOWN round trip, or LEFT,RIGHT / RIGHT,LEFT via --terrain-scroll-keys")
    parser.add_argument("--terrain-scroll-keys", default="DOWN,RIGHT",
                        help="two distinct scroll keys for the first/second scroll action (default DOWN,RIGHT; UP,DOWN is the in-map round trip)")
    parser.add_argument("--candidate-throttle", metavar="STOP_MS:RUN_MS", default=None,
                        help="H-LD diagnostic: SIGSTOP/SIGCONT only the candidate lane's verified private-copy game process on this duty from the first scroll input tick to the end of the scroll window (needs --terrain-scroll)")
    parser.add_argument("--p4b-s-snapshot", action="store_true",
                        help="use update-return in-process snapshots as the terrain-scroll state gate")
    parser.add_argument("--reference-completed-states", type=Path,
                        help="lap888 completed-phase result JSON used to validate the snapshot sampler")
    parser.add_argument("--hd-source", choices=("identity", "scale2x"), default=None)
    parser.add_argument("--negative-mismatch", action="store_true")
    parser.add_argument("--performance-window", action="store_true",
                        help="measure a no-input PS3 tick/present window in both lanes")
    parser.add_argument("--perf-sections", action="store_true",
                        help="opt in to QPC cache/compositor section timing")
    parser.add_argument("--rice-phase-diagnostic", type=float, default=None,
                        help="observe owner6 rice writes and player-phase calls for N seconds")
    parser.add_argument("--rice-phase-variant", choices=("baseline", "candidate"), default="baseline",
                        help="lane for --rice-phase-diagnostic; candidate requires --hd-source scale2x")
    parser.add_argument("--rice-phase-target-tick", type=int, default=None,
                        help="pin the diagnostic to an absolute owner6 tick (tick & 7 == 6)")
    parser.add_argument("--scroll-phase-diagnostic", action="store_true",
                        help="run baselineA/baselineB/candidate on the immutable lap877 scroll schedule")
    parser.add_argument("--fixture", choices=tuple(SAVE_FIXTURES), default="save006",
                        help="pinned save to load (save000 is the H-S2 second scene; requires --scene-actions none)")
    parser.add_argument("--scene-actions", choices=("all", "none"), default="all",
                        help="none = stop after the loaded capture (+ --performance-window) without save006-only selection/drag/minimap/production work")
    args = parser.parse_args(argv)
    option_error = _scene_option_error(
        fixture=args.fixture, scene_actions=args.scene_actions,
        terrain_scroll=args.terrain_scroll, terrain_trace=args.terrain_trace,
        census_only=args.census_only,
        rice_phase=args.rice_phase_diagnostic is not None,
        scroll_phase=args.scroll_phase_diagnostic,
    )
    if option_error is not None:
        parser.error(option_error)
    fixture_name, fixture_sha256, _ = _fixture_pin(args.fixture)
    if args.terrain_scroll_hold and not args.terrain_scroll:
        parser.error("--terrain-scroll-hold requires --terrain-scroll")
    if args.terrain_scroll_keys != "DOWN,RIGHT" and not args.terrain_scroll:
        parser.error("--terrain-scroll-keys requires --terrain-scroll")
    edge_error = _scroll_edge_option_error(
        edge=args.terrain_scroll_edge, hold=args.terrain_scroll_hold,
        keys_spec=args.terrain_scroll_keys, terrain_scroll=args.terrain_scroll,
    )
    if edge_error is not None:
        parser.error(edge_error)
    try:
        scroll_keys = (_scroll_edge_keys(args.terrain_scroll_keys) if args.terrain_scroll_edge
                       else _parse_scroll_keys(args.terrain_scroll_keys))
    except ValueError as error:
        parser.error(str(error))
    throttle_error = _candidate_throttle_option_error(
        args.candidate_throttle, terrain_scroll=args.terrain_scroll)
    if throttle_error is not None:
        parser.error(throttle_error)
    candidate_throttle = (_parse_candidate_throttle(args.candidate_throttle)
                          if args.candidate_throttle is not None else None)
    if args.p4b_s_snapshot and not args.terrain_scroll:
        parser.error("--p4b-s-snapshot requires --terrain-scroll")
    if args.p4b_s_snapshot and args.fixture != "save006":
        parser.error("--p4b-s-snapshot requires --fixture save006 (lap888 reference is save006-only)")
    if args.p4b_s_snapshot and args.reference_completed_states is None:
        parser.error("--p4b-s-snapshot requires --reference-completed-states")
    if args.reference_completed_states is not None and not args.p4b_s_snapshot:
        parser.error("--reference-completed-states requires --p4b-s-snapshot")
    if args.rice_phase_diagnostic is not None and not (1.0 <= args.rice_phase_diagnostic <= 180.0):
        parser.error("--rice-phase-diagnostic must be between 1 and 180 seconds")
    if (args.rice_phase_diagnostic is not None and args.rice_phase_variant == "candidate"
            and args.hd_source != "scale2x"):
        parser.error("candidate rice phase diagnostics require --hd-source scale2x")
    if (args.rice_phase_target_tick is not None
            and (args.rice_phase_diagnostic is None or args.rice_phase_target_tick & 7 != 6)):
        parser.error("--rice-phase-target-tick requires diagnostic mode and an owner6 tick (tick & 7 == 6)")
    _, source_exe = runtime_env.validate_original_source(SOURCE)
    if _sha256(source_exe) != runtime_env.ORIGINAL_SHA256:
        raise SystemExit("protected source executable SHA mismatch")
    if _sha256(FIXTURE_SOURCE / "save" / fixture_name) != fixture_sha256:
        raise SystemExit("protected save fixture SHA mismatch")
    args.artifact_root.mkdir(parents=True, exist_ok=False)
    bridge_dir = args.artifact_root / "bridge"
    subprocess.run([
        sys.executable, str(REPO / "patches/population/build_runtime_bridge.py"),
        "--out-dir", str(bridge_dir), "--unit-pool-capacity", "1200",
    ], cwd=REPO, check=True, env={**os.environ, "PYTHONPATH": str(REPO)})
    bridge = bridge_dir / "_inmm.dll"
    close_dir = args.artifact_root / "close_helper"
    subprocess.run([
        sys.executable, str(REPO / "tools/win32_close_fixture.py"), "build",
        "--out-dir", str(close_dir),
    ], cwd=REPO, check=True, env={**os.environ, "PYTHONPATH": str(REPO)})
    close_helper = close_dir / "win32_close_helper.exe"
    if args.scroll_phase_diagnostic:
        if args.hd_source != "scale2x":
            parser.error("--scroll-phase-diagnostic requires --hd-source scale2x")
        pair, exit_code = _run_scroll_phase_orchestration(
            run_lane=_run_lane, runtime_root=args.runtime_root,
            artifact_root=args.artifact_root, bridge=bridge, close_helper=close_helper,
        )
        pair_path = args.artifact_root / "scroll-phase-diagnostic-result.json"
        print(json.dumps({"status": pair["status"], "result": str(pair_path),
                          "checks": pair.get("checks", pair.get("control_acceptance"))},
                         ensure_ascii=False))
        return exit_code
    if args.rice_phase_diagnostic is not None:
        diagnostic = _run_lane(
            variant=args.rice_phase_variant, bridge=bridge,
            runtime_root=args.runtime_root / "rice-phase", artifact_root=args.artifact_root / "rice-phase",
            close_helper=close_helper, rice_phase_diagnostic=args.rice_phase_diagnostic,
            rice_phase_target_tick=args.rice_phase_target_tick,
            hd_source=args.hd_source if args.rice_phase_variant == "candidate" else None,
        )
        detail = diagnostic.get("rice_phase_diagnostic", {})
        observation = detail.get("observation", {})
        snapshot = detail.get("scene_snapshot_at_phase_return", {})
        print(json.dumps({"status": diagnostic.get("status"),
                          "variant": args.rice_phase_variant,
                          "phase_diagnostic": detail.get("status"),
                          "phase_status": observation.get("phase_status"),
                          "target_tick": detail.get("target_tick"),
                          "phase_count": len(observation.get("completed_simulation_update_observations", [])),
                          "rice_writer_event_count": observation.get("rice_writer_event_count"),
                          "rice_writer_threads": observation.get("rice_writer_threads"),
                          "rice_writer_events": observation.get("rice_writer_events", [])[:3],
                          "all_writer_quiescence_proven_at_read": detail.get(
                              "all_writer_quiescence_proven_at_read"),
                          "snapshot_status": snapshot.get("status"),
                          "snapshot_tick": [snapshot.get("sim_tick_before"), snapshot.get("sim_tick_after")],
                          "snapshot_camera": snapshot.get("camera_before"),
                          "snapshot_player_count": len(snapshot.get("state", {}).get("players", [])),
                          "snapshot_unit_count": len(snapshot.get("state", {}).get("units", [])),
                          "event_sha256": detail.get("events_sha256"),
                          "summary_sha256": detail.get("summary_sha256"),
                          "cleanup": diagnostic.get("cleanup"),
                          "source_unchanged": diagnostic.get("source_unchanged")},
                         ensure_ascii=False))
        return 0 if diagnostic.get("status") == "DIAGNOSTIC_ONLY" else 2
    if args.census_state != 3 and not args.census_only:
        parser.error("--census-state requires --census-only")
    if args.census_residual and not args.census_only:
        parser.error("--census-residual requires --census-only")
    if args.census_watch is not None and not args.census_residual:
        parser.error("--census-watch requires --census-residual")
    if args.census_watch_cache and args.census_watch is None:
        parser.error("--census-watch-cache requires --census-watch")
    if args.census_watch_presents and args.census_watch is None:
        parser.error("--census-watch-presents requires --census-watch")
    if not 0 <= args.census_watch_presents <= 9999:
        parser.error("--census-watch-presents must be 0-9999")
    if args.census_skip_presents and not args.census_only:
        parser.error("--census-skip-presents requires --census-only")
    if not 0 <= args.census_skip_presents <= 9999:
        parser.error("--census-skip-presents must be 0-9999")
    if args.stale_mask is not None and (args.hd_source != "scale2x" or args.census_only):
        parser.error("--stale-mask requires --hd-source scale2x")
    if args.blend_size_reject_diag and (args.hd_source != "scale2x" or args.census_only):
        parser.error("--blend-size-reject-diag requires --hd-source scale2x")
    if args.layer_drift and (args.hd_source != "scale2x" or args.census_only):
        parser.error("--layer-drift requires --hd-source scale2x")
    if args.screen_watch and not args.layer_drift:
        parser.error("--screen-watch requires --layer-drift")
    if args.screen_watch_cache and not args.screen_watch:
        parser.error("--screen-watch-cache requires --screen-watch")
    if args.drift_samples is not None and not args.layer_drift:
        parser.error("--drift-samples requires --layer-drift")
    if args.census_only and args.hd_source is not None:
        parser.error("--census-only observes original pinned prologues and cannot be combined with --hd-source")
    if args.census_only:
        census = _run_lane(
            variant="baseline", bridge=bridge,
            runtime_root=args.runtime_root / "census",
            artifact_root=args.artifact_root / "census",
            close_helper=close_helper, census=True, census_state=args.census_state,
            census_residual=args.census_residual,
            census_watch=args.census_watch,
            census_watch_cache=args.census_watch_cache,
            census_watch_presents=args.census_watch_presents,
            census_skip_presents=args.census_skip_presents,
            terrain_trace=args.terrain_trace,
            terrain_scroll=args.terrain_scroll,
            fixture=args.fixture, scene_actions=args.scene_actions,
        )
        census_gate = _validate_census_lane(census, census_state=args.census_state)
        print(json.dumps({
            "status": "PASS" if census.get("status") == "PASS" and census_gate["status"] == "PASS" else "FAIL",
            "census_gate": census_gate,
            "census": census.get("census"),
            "trace": census.get("trace"),
            "cleanup": census.get("cleanup"),
        }, ensure_ascii=False))
        return 0 if census.get("status") == "PASS" and census_gate["status"] == "PASS" else 2
    reference_states = None
    if args.reference_completed_states is not None:
        reference_states = _load_completed_state_reference(args.reference_completed_states)
    execution_source_before = _execution_source_hashes(
        bridge_dir / "supply_bridge_build.json",
    )
    baseline = _run_lane(variant="baseline", bridge=bridge,
                         runtime_root=args.runtime_root / "baseline",
                         artifact_root=args.artifact_root / "baseline", close_helper=close_helper,
                         terrain_trace=args.terrain_trace,
                         terrain_scroll=args.terrain_scroll,
                         terrain_scroll_hold=args.terrain_scroll_hold,
                         terrain_scroll_keys=scroll_keys,
                         terrain_scroll_edge=args.terrain_scroll_edge,
                         fixture=args.fixture, scene_actions=args.scene_actions,
                         inprocess_snapshot=args.p4b_s_snapshot,
                         reference_states=reference_states,
                         common_tick_plan=(SCROLL_PHASE_TICK_PLAN if args.p4b_s_snapshot else None),
                         performance_window=args.performance_window,
                         perf_sections=args.perf_sections)
    candidate = _run_lane(variant="candidate", bridge=bridge,
                          runtime_root=args.runtime_root / "candidate",
                          artifact_root=args.artifact_root / "candidate", close_helper=close_helper,
                          hd_source=args.hd_source, terrain_trace=args.terrain_trace,
                          terrain_scroll=args.terrain_scroll,
                          terrain_scroll_hold=args.terrain_scroll_hold,
                          terrain_scroll_keys=scroll_keys,
                          terrain_scroll_edge=args.terrain_scroll_edge,
                          candidate_throttle=candidate_throttle,
                          fixture=args.fixture, scene_actions=args.scene_actions,
                          inprocess_snapshot=args.p4b_s_snapshot,
                          stale_mask=args.stale_mask,
                          blend_size_reject_diag=args.blend_size_reject_diag,
                          layer_drift=args.layer_drift,
                          screen_watch=args.screen_watch,
                          screen_watch_cache=args.screen_watch_cache,
                          drift_samples=args.drift_samples,
                          negative_mismatch=args.negative_mismatch,
                          performance_window=args.performance_window,
                          perf_sections=args.perf_sections,
                          common_tick_plan=(baseline.get("common_tick_plan")
                                            if args.terrain_scroll else None))
    execution_source_after = _execution_source_hashes(
        bridge_dir / "supply_bridge_build.json",
    )
    pair = {
        "schema": "syw2plus.g1-saved-scene-pair.v1",
        "fixture": {"name": fixture_name, "sha256": fixture_sha256, "synthetic": False},
        "execution_source": {
            "before": execution_source_before,
            "after": execution_source_after,
            "unchanged": execution_source_before == execution_source_after,
        },
        "baseline": baseline, "candidate": candidate,
        "scene_state_equal": baseline.get("scene", {}).get("state") == candidate.get("scene", {}).get("state"),
    }
    pair["input_effect_comparison"] = _compare_input_effects(baseline, candidate)
    pair["minimap_diagnostic_parity"] = _compare_minimap_diagnostic_parity(baseline, candidate)
    if args.terrain_scroll:
        base_scroll = baseline.get("terrain_scroll", {})
        candidate_scroll = candidate.get("terrain_scroll", {})
        pair["terrain_scroll_parity"] = _terrain_scroll_pair_parity(
            base_scroll, candidate_scroll,
            loaded_scene_equal=pair.get("scene_state_equal") is True,
            candidate_fixed_coverage=candidate_scroll.get("fixed_camera_coverage", {}),
            scroll_keys=scroll_keys,
        )
    if args.performance_window:
        base_perf = baseline.get("performance_window", {})
        cand_perf = candidate.get("performance_window", {})
        base_present = base_perf.get("primary_present", {})
        cand_present = cand_perf.get("primary_present", {})
        base_rate = base_perf.get("tick_rate_hz")
        cand_rate = cand_perf.get("tick_rate_hz")
        base_p95 = base_present.get("p95_ms")
        cand_p95 = cand_present.get("p95_ms")
        rate_ratio = cand_rate / base_rate if (
            isinstance(base_rate, (int, float)) and isinstance(cand_rate, (int, float)) and base_rate > 0
        ) else None
        p95_delta = cand_p95 - base_p95 if (
            isinstance(base_p95, int) and isinstance(cand_p95, int)
        ) else None
        perf_valid = (
            base_perf.get("status") == cand_perf.get("status") == "PASS"
            and base_present.get("status") == cand_present.get("status") == "PASS"
            and base_present.get("sample_span_ms", 0) >= 18_000
            and cand_present.get("sample_span_ms", 0) >= 18_000
        )
        pair["performance_comparison"] = {
            "status": "PASS" if (
                perf_valid and rate_ratio is not None and rate_ratio >= 0.95
                and p95_delta is not None and p95_delta <= 16
            ) else (
                "FAIL" if perf_valid else "INVALID"
            ),
            "baseline_tick_rate_hz": base_rate,
            "candidate_tick_rate_hz": cand_rate,
            "tick_rate_ratio": rate_ratio,
            "tick_rate_delta_percent": (rate_ratio - 1.0) * 100.0 if rate_ratio is not None else None,
            "baseline_present_p95_ms": base_p95,
            "candidate_present_p95_ms": cand_p95,
            "present_p95_delta_ms": p95_delta,
            "checks": {
                "tick_rate_at_least_95_percent": rate_ratio is not None and rate_ratio >= 0.95,
                "present_p95_within_16ms": p95_delta is not None and p95_delta <= 16,
                "matching_fixed_windows": perf_valid,
            },
        }
    if baseline.get("status") == "PASS" and candidate.get("status") == "PASS":
        pair["capture_visual_comparisons"] = {
            tag: _compare_images(baseline, candidate, tag)
            for tag in G1_CAPTURE_TAGS
        }
        pair["loaded_capture_comparison"] = pair["capture_visual_comparisons"]["loaded"]
        pair["scroll_after_comparison"] = _diagnostic_capture_comparisons(
            baseline, candidate, terrain_scroll=args.terrain_scroll,
        ).get("scroll_after")
    pair["v2_capture_gate"] = _v2_capture_gate(
        pair.get("capture_visual_comparisons", {})
    )
    pair["v2s_capture_gate"] = _v2s_capture_gate(
        pair.get("capture_visual_comparisons", {})
    )
    pair["v2q_capture_gate"] = _v2q_capture_gate(
        pair.get("capture_visual_comparisons", {})
    )
    scale2x_gate_status = candidate.get("scale2x_validator", {}).get("status", "BLOCKED")
    pair["scale2x_gate"] = {
        "status": scale2x_gate_status if args.hd_source == "scale2x" else "NOT_REQUIRED",
        "trace": candidate.get("scale2x_validator", {}),
    }
    pair_status = _pair_status(
        pair,
        performance_requested=args.performance_window,
        hd_source=args.hd_source,
        scale2x_gate_status=scale2x_gate_status,
        terrain_scroll=args.terrain_scroll,
    )
    pair["status"] = pair_status
    pair_path = args.artifact_root / "pair-result.json"
    pair_path.write_text(json.dumps(pair, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": pair_status,
                      "scene_state_equal": pair.get("scene_state_equal"),
                      "pair_result": str(pair_path)}, ensure_ascii=False))
    return 0 if (baseline.get("status") == "PASS" and candidate.get("status") == "PASS"
                 and pair_status == "PASS") else 2


if __name__ == "__main__":
    raise SystemExit(main())
