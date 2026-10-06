#!/usr/bin/env python3
"""R3 sparse-selection order-dispatch check (2026-09-28 01:30 user direction,
``docs/history/laps/20260927_lap721_middle_g5_v4_r1_confirmed_falsified_r3_sparse_gap.md``,
``loop/ESCALATE_SOL`` lap721 section).

lap721's independent review found v4's chunk-wrapper ``check_count`` looks
only at the live selection-array *count* field: if it is ``<= 20`` the order
falls straight through to the original, unchunked body, which always copies
a fixed ``entries[0:20]`` window. It also found (disasm) that the array's
removal routine zeroes a matching unit's slot **in place** with no
compaction. Put together: select 50, then let enough units at *low* array
indices die that the live count drops to <= 20 while the survivors are still
sitting at indices >= 20 -- the count-only gate takes the unchunked path,
which never reads past ``entries[19]``, so the survivors get nothing. This is
R3. ``patches/selection/g5_selection_cap50_v5.py`` is the fix (gate widened
to "count > 20 OR entries[20:50] has a live slot").

This probe creates that exact state with a REAL in-engine death (not a UI
deselect, which lap720 already showed clears/rebuilds the whole array
instead of leaving holes) via a new bridge diagnostic op (10): it calls the
original death handler ``FUN_00409C70`` directly on a chosen live unit,
which -- per lap721's disasm -- is the actual call chain that reaches the
selection-removal routine when the dying unit is selected. The bridge is a
private fork (``patches/population/g5_r3_death_bridge.c``); it is built via
``--bridge-source`` so the shared, G2-pinned ``runtime_bridge.c`` (and its
``G2_APPROVED_BRIDGE_SHA256`` gate) are never touched.

Protocol, all variants: solo lobby, the same worker-centered 55-unit dense
type-2 fixture as the other G5 probes (slot 1198's pre-existing worker makes
56 selectable units total), full-rectangle drag-select, full selection-array
buffer capture, then kill (via the death-handler bridge op) a chosen set of
array indices (``--scenario``, see below), leaving the rest alive. STOP is
then clicked once and every survivor slot is sampled for ``unit+0x384``
(pending order word); a validated ground right-click issues a plain MOVE the
same way.

PASS requires every surviving (post-kill) unit to receive both orders.
FAIL (R3 CONFIRMED for the ``v4``/``v3`` gate) is any survivor missing
either. The ``original`` variant is a sanity control: its capacity-20 body
is the same "always copy entries[0:20]" body v4/v5 fall through to, so with
survivors deliberately placed inside that same fixed window, the original
should always PASS -- confirming the death-and-measure method itself is
sound, independent of the gate under test.

``--scenario`` (2026-09-28 lap726, G5 completion checklist item (B) --
lap723 only exercised one kill pattern):

- ``front-death`` (default, byte-identical to lap723/lap721's original
  behaviour): kill array indices ``[0, K)``, survivors are the contiguous
  tail ``[K, count)``, ``K = max(cap/2, count - cap/2)``. Exercises v5's
  sparse-scan finding a survivor near the *start* of ``entries[20:50]``.
- ``middle-death``: kill a contiguous middle band, survivors are the front
  and rear bands (non-contiguous, split across the unchunked
  ``entries[0:20]`` window *and* the sparse-scanned ``entries[20:50]``
  region). Also drives the live count to exactly the ``<= 20`` boundary
  (count 20, not < 20), which ``front-death`` does not hit exactly.
- ``rear-death``: kill the contiguous tail, survivors are the front band
  entirely inside ``entries[0:20]``. A negative control on the sparse scan:
  with the tail genuinely empty the scan must find nothing and fall through
  to the unchunked body, which must still deliver both orders to the
  ``entries[0:20]``-resident survivors.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Mapping, cast

from tools import runtime_env
from tools.g5_candidate_drag_probe import (
    ProbeError, DRAG_START, DRAG_END, STOCK_SELECTION_BASE, STOCK_SELECTION_CAPACITY,
    SEED_TYPE, VISIBLE_WORKER_SLOT, UNIT_BASE, UNIT_STRIDE, UNIT_PENDING_COMMAND_OFFSET,
    selection_snapshot, unit_snapshot, dense_fixture_requests, sha256, write_json, capture,
)
from tools.g5_command_coverage_probe import BUTTONS
from tools.g5_attack_move_broadcast_probe import MINIMAP_CLICK
from patches.population.runtime_driver import read as read_memory
from patches.population.runtime_driver import state as read_state

REPO = Path(__file__).resolve().parents[1]
ORIGINAL_SHA = runtime_env.ORIGINAL_SHA256
DEFAULT_SOURCE = runtime_env.DEFAULT_SOURCE
STOP_PENDING = 0x1000002
MOVE_PENDING = 0x1000003
DEATH_BRIDGE_SOURCE = REPO / "patches/population/g5_r3_death_bridge.c"
DESTINATION_CANDIDATES = [
    (300, 420), (400, 300), (350, 250), (450, 350),
    (300, 350), (500, 300), (250, 300), (400, 420),
]

VARIANTS: dict[str, Any] = {}
SCENARIOS = ("front-death", "middle-death", "rear-death")


def _kill_survivor_indices(scenario: str, initial_count: int, *, is_candidate: bool) -> tuple[list[int], list[int]]:
    """Return (kill_indices, survivor_indices), both subsets of range(initial_count).

    ``cap`` (20) is the chunk/sparse-scan boundary for candidates; for the
    ``original`` variant (no chunking) it is only used as a proportional
    reference so the sanity control still splits the selection meaningfully.
    """
    cap = 20
    if scenario == "front-death":
        threshold = cap if is_candidate else initial_count // 2
        kill_count = max(threshold, initial_count - threshold)
        kill_count = min(kill_count, initial_count - 1)
        kill_indices = list(range(0, kill_count))
        survivor_indices = list(range(kill_count, initial_count))
    elif scenario == "middle-death":
        target_survivors = min(cap, initial_count - 2) if is_candidate else max(2, initial_count // 3)
        half = max(1, target_survivors // 2)
        front = list(range(0, half))
        rear = list(range(initial_count - half, initial_count))
        survivor_indices = sorted(set(front) | set(rear))
        kill_indices = [i for i in range(initial_count) if i not in survivor_indices]
    elif scenario == "rear-death":
        survive_count = cap if is_candidate else max(1, initial_count // 2)
        survive_count = min(survive_count, initial_count - 1)
        survivor_indices = list(range(0, survive_count))
        kill_indices = list(range(survive_count, initial_count))
    else:
        raise ProbeError(f"unknown scenario: {scenario}")
    if not kill_indices or not survivor_indices:
        raise ProbeError(f"bad kill/survivor split for scenario={scenario}: "
                          f"kill={kill_indices} survivors={survivor_indices}")
    return kill_indices, survivor_indices


def _variant_module(variant: str):
    if variant == "original":
        return None
    if variant == "candidate-v4":
        from patches.selection import g5_selection_cap50_v4 as g5
        return g5
    if variant == "candidate-v5":
        from patches.selection import g5_selection_cap50_v5 as g5
        return g5
    if variant == "candidate-v6":
        from patches.selection import g5_selection_cap50_v6 as g5
        return g5
    raise ProbeError(f"unsupported variant: {variant}")


class Bridge:
    """Generic ``id op owner slot type rice wood used`` request/result caller.

    Distinct from ``g5_candidate_drag_probe.SupplyProbe`` only in that it
    exposes ``slot`` (``SupplyProbe.call`` hardcodes it to 0, which is fine
    for the fixture-only ops it was built for but not for op 1/10 which
    address a specific unit slot). Shares one monotonic id counter across
    every call this probe makes -- the bridge rejects any request whose id
    is not strictly greater than the last one it served, regardless of which
    op produced it.
    """

    def __init__(self, prefix: Path) -> None:
        self.request = prefix / "drive_c" / "supply_probe_request.txt"
        self.result = prefix / "drive_c" / "supply_probe_result.json"
        self.next_id = 1

    def call(self, *, op: int, owner: int, slot: int = 0, type_: int = 0,
             rice: int = 0, wood: int = 0, used: int = 0) -> dict[str, Any]:
        request_id = self.next_id
        self.next_id += 1
        self.request.write_text(f"{request_id} {op} {owner} {slot} {type_} {rice} {wood} {used}\n",
                                 encoding="ascii")
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
        raise ProbeError(f"bridge request timed out: op={op} id={request_id}")


def read_full_buffer(pid: int, base: int, capacity: int) -> dict[str, Any]:
    raw = [
        int.from_bytes(read_memory(pid, base + 4 + i * 4, 4), "little", signed=False)
        for i in range(capacity)
    ]
    count = int.from_bytes(read_memory(pid, base, 4), "little", signed=True)
    return {"count_field": count, "raw_all": [hex(v) for v in raw], "slots_all": [v & 0xFFF for v in raw]}


def read_pending(pid: int, slot: int) -> int:
    base = UNIT_BASE + slot * UNIT_STRIDE
    return int.from_bytes(read_memory(pid, base + UNIT_PENDING_COMMAND_OFFSET, 4), "little")


def read_exists_hp(pid: int, slot: int) -> dict[str, int]:
    exists = int.from_bytes(read_memory(pid, 0x008990C8 + slot * 2, 2), "little")
    hp = int.from_bytes(read_memory(pid, UNIT_BASE + slot * UNIT_STRIDE + 0xB4, 4), "little", signed=True)
    return {"exists": exists, "hp": hp}


def sample_ever(pid: int, slots: list[int], act, window: float = 3.0, interval: float = 0.02) -> dict[str, Any]:
    before = {s: read_pending(pid, s) for s in slots}
    act()
    start = time.monotonic()
    ever: dict[int, set[int]] = {s: set() for s in slots}
    n_samples = 0
    while time.monotonic() - start < window:
        for s in slots:
            ever[s].add(read_pending(pid, s))
        n_samples += 1
        time.sleep(interval)
    return {
        "n_samples": n_samples,
        "before": {s: hex(v) for s, v in before.items()},
        "ever_raw": {s: sorted(vs) for s, vs in ever.items()},
    }


def run_probe(source: Path, runtime_root: Path, artifact_root: Path, *, variant: str,
              scenario: str = "front-death") -> dict[str, Any]:
    if artifact_root.exists():
        raise ProbeError(f"artifact root must be new: {artifact_root}")
    artifact_root.mkdir(parents=True)
    source, source_exe = runtime_env.validate_original_source(source)
    if sha256(source_exe) != ORIGINAL_SHA:
        raise ProbeError("protected source SHA mismatch")
    g5 = _variant_module(variant)
    candidate_bytes: bytes | None = None
    candidate_sha: str | None = None
    if g5 is not None:
        candidate_bytes, build_report = g5.build_candidate(source_exe.read_bytes())
        candidate_sha = build_report["candidate_sha256"]

    bridge_dir = artifact_root / "death_bridge"
    subprocess.run([sys.executable, str(REPO / "patches/population/build_runtime_bridge.py"),
                    "--out-dir", str(bridge_dir), "--unit-pool-capacity", "1200",
                    "--bridge-source", str(DEATH_BRIDGE_SOURCE)],
                   cwd=REPO, check=True, env=dict(os.environ, PYTHONPATH=str(REPO)))
    bridge_dll = bridge_dir / "_inmm.dll"
    manifest = runtime_env.prepare(source, runtime_root=runtime_root, bridge=bridge_dll, timeout=60)
    game = Path(cast(str, cast(Mapping, manifest["game"])["root"]))
    prefix = Path(cast(str, cast(Mapping, manifest["wine"])["prefix"]))
    private_exe = game / runtime_env.ORIGINAL_EXE
    if sha256(private_exe) != ORIGINAL_SHA:
        raise ProbeError("private copy pre-install check failed")
    if candidate_bytes is not None:
        private_exe.write_bytes(candidate_bytes)
    private_sha = sha256(private_exe)
    if g5 is not None and private_sha != candidate_sha:
        raise ProbeError(f"candidate SHA mismatch: {private_sha}")
    sel_base = g5.SELECTION_BASE if g5 is not None else STOCK_SELECTION_BASE
    sel_cap = g5.TARGET_CAPACITY if g5 is not None else STOCK_SELECTION_CAPACITY

    result: dict[str, Any] = {
        "schema": "syw2plus.g5-r3-sparse-selection-probe.v1", "variant": variant, "scenario": scenario,
        "status": "UNKNOWN",
        "provenance": {"source_sha256": sha256(source_exe), "private_exe_sha256": private_sha,
                       "candidate_sha256": candidate_sha},
        "captures": [], "inputs": [],
    }
    log = (artifact_root / "probe.log").open("a", encoding="utf-8")
    children: list[Any] = []
    xvfb: Any = None
    env = dict(os.environ, WINEPREFIX=str(prefix), WINEARCH="win32", WINEDEBUG="-all",
               LANG="ko_KR.UTF-8", LC_ALL="ko_KR.UTF-8", WINEDLLOVERRIDES="ddraw=b", SYW2_SUPPLY_PROBE="1")
    try:
        xvfb, display = runtime_env._xvfb(log, "1600x1200x24")
        env["DISPLAY"] = display
        children.append(subprocess.Popen(["wine", "explorer", "/desktop=Default,1600x1200"],
                                         cwd=game, env=env, stdout=log, stderr=log))
        time.sleep(1)
        game_proc = subprocess.Popen(["wine", str(private_exe)], cwd=game, env=env, stdout=log, stderr=log)
        children.append(game_proc)
        pid = game_proc.pid

        def alive() -> bool:
            if game_proc.poll() is not None:
                return False
            try:
                return int(read_state(pid).get("ps", -1)) == 3
            except (OSError, ValueError, ProbeError):
                return False

        def wait_for(pred, label: str, timeout: float = 45) -> dict[str, Any]:
            deadline = time.monotonic() + timeout
            last: dict[str, Any] = {}
            while time.monotonic() < deadline:
                try:
                    last = read_state(pid)
                    if pred(last):
                        return last
                except (OSError, ValueError, ProbeError) as exc:
                    last = {"error": str(exc)}
                time.sleep(0.25)
            raise ProbeError(f"{label} timeout; last={last}")

        wait_for(lambda s: s.get("ps") == 9, "ps9")
        tree = runtime_env._window_tree(display, 10)
        outer, content = runtime_env._game_window_ids(tree)
        if content is None:
            raise ProbeError("game content window not found")
        info = runtime_env._xwininfo_details(display, content, 10)
        crop = (int(info["x"]), int(info["y"]))

        def xdo(*args: str) -> None:
            subprocess.run(["xdotool", *args], env=env, stdout=log, stderr=log, timeout=10, check=True)

        def click(x: int, y: int, *, drag_to: tuple[int, int] | None = None, button: int = 1) -> None:
            argv = [sys.executable, str(REPO / "tools/x11_mouse_click.py"), "--display", display,
                    str(crop[0] + x), str(crop[1] + y), "--button", str(button)]
            if drag_to is not None:
                argv += ["--drag-to", str(crop[0] + drag_to[0]), str(crop[1] + drag_to[1])]
            subprocess.run(argv, env=env, stdout=log, stderr=log, timeout=10, check=True)
            result["inputs"].append({"x": x, "y": y, "drag_to": list(drag_to) if drag_to else None, "button": button})

        def snap(name: str) -> None:
            result["captures"].append(capture(display, artifact_root / f"{name}.png", log))

        def sel() -> dict[str, Any]:
            return selection_snapshot(pid, base=sel_base, capacity=sel_cap)

        xdo("windowfocus", outer)
        click(184, 560)
        wait_for(lambda s: s.get("ps") == 7, "ps7")

        def selector() -> Any:
            return runtime_env._read_lobby_selector(lambda a, n: read_memory(pid, a, n)).get("selected")

        if selector() == "solo":
            click(344, 169)
            time.sleep(0.5)
        click(462, 169)
        deadline = time.monotonic() + 10
        while selector() != "solo" and time.monotonic() < deadline:
            time.sleep(0.2)
        if selector() != "solo":
            raise ProbeError("solo selector did not settle")
        click(608, 564)
        wait_for(lambda s: s.get("ps") == 5, "ps5")
        deadline = time.monotonic() + 12
        while time.monotonic() < deadline:
            if runtime_env._read_local_ready_state(lambda a, n: read_memory(pid, a, n)).get("ready_value") == 1:
                break
            time.sleep(0.2)
        click(608, 564)
        wait_for(lambda s: s.get("ps") == 3 and int(s.get("tick", 0)) > 0, "ps3")

        worker = unit_snapshot(pid, VISIBLE_WORKER_SLOT)
        if worker["owner"] != 0 or worker["unit_type"] in {0, SEED_TYPE}:
            raise ProbeError(f"slot1198 is not the expected worker: {worker}")
        result["worker"] = worker
        bridge = Bridge(prefix)
        click(*MINIMAP_CLICK)
        time.sleep(1)
        snap("00-after-minimap")

        for req in dense_fixture_requests(worker):
            r = bridge.call(op=5, owner=0, type_=SEED_TYPE, rice=req["x"], wood=req["y"], used=req["count"])
            if not r.get("ok") or r.get("fixture_added") != req["count"]:
                raise ProbeError(f"fixture failed: {r}")
        time.sleep(1)
        snap("01-after-fixture")

        # --- establish the maximal live selection (50 candidate / 20 original)
        click(*DRAG_START, drag_to=DRAG_END)
        time.sleep(0.8)
        initial_sel = sel()
        initial_buffer = read_full_buffer(pid, sel_base, sel_cap)
        result["initial_selection"] = initial_sel
        result["initial_full_buffer"] = initial_buffer
        snap("02-after-full-drag")
        if not alive():
            raise ProbeError("game not alive after full drag")

        initial_count = initial_sel["count"]
        if initial_count < 4:
            raise ProbeError(f"drag selected too few units to run R3: {initial_count}")
        kill_indices, survivor_indices = _kill_survivor_indices(
            scenario, initial_count, is_candidate=g5 is not None
        )
        kill_slots = [initial_buffer["slots_all"][i] for i in kill_indices if initial_buffer["slots_all"][i] != 0]
        survivor_slots = [initial_buffer["slots_all"][i] for i in survivor_indices]
        if not kill_slots or not survivor_slots:
            raise ProbeError(f"bad kill/survivor split: kill={kill_slots} survivors={survivor_slots}")
        result["kill_plan"] = {
            "scenario": scenario, "kill_indices": kill_indices,
            "kill_slots": kill_slots, "survivor_indices": survivor_indices, "survivor_slots": survivor_slots,
        }

        kill_reports = []
        for slot in kill_slots:
            r = bridge.call(op=10, owner=0, slot=slot)
            kill_reports.append(r)
            if not r.get("ok"):
                raise ProbeError(f"kill failed for slot {slot}: {r}")
        result["kill_reports"] = kill_reports
        time.sleep(0.5)
        snap("03-after-kills")
        if not alive():
            raise ProbeError("game not alive after kills")

        after_buffer = read_full_buffer(pid, sel_base, sel_cap)
        result["after_kill_full_buffer"] = after_buffer
        result["after_kill_selection"] = sel()
        result["killed_exists_hp"] = {s: read_exists_hp(pid, s) for s in kill_slots}
        result["survivor_exists_hp"] = {s: read_exists_hp(pid, s) for s in survivor_slots}

        # The death handler (FUN_00409C70) sets a dead-flag and clears the
        # unit's own selected-flag; it does not itself zero HP or the
        # existence-table entry (those apparently follow on a later tick /
        # different code path a diagnostic op has no reason to chase) -- the
        # array evidence (count field + slot contents) is what this probe
        # actually needs, corroborated by each kill's own before/after report.
        structural_ok = (
            after_buffer["count_field"] == initial_count - len(kill_slots)
            and all(after_buffer["slots_all"][i] == 0 for i in kill_indices)
            and all(after_buffer["slots_all"][i] == initial_buffer["slots_all"][i] for i in survivor_indices)
            and all(r["op10"]["selected_before"] == 1 and r["op10"]["dead_flag_after"] == 1
                    and r["op10"]["selected_after"] == 0 for r in kill_reports)
            and all(v["hp"] > 0 for v in result["survivor_exists_hp"].values())
        )
        result["structural_ok"] = structural_ok
        if not structural_ok:
            result["status"] = "FAIL_KILL_SETUP"
            raise ProbeError(f"kill setup did not produce the intended sparse state: {result['kill_plan']}")

        stop_obs = sample_ever(pid, survivor_slots, lambda: click(*BUTTONS["stop"]), window=3.0)
        result["stop_observation"] = stop_obs
        snap("04-after-stop")
        if not alive():
            raise ProbeError("game not alive after stop click")
        stop_missed = [s for s in survivor_slots if STOP_PENDING not in stop_obs["ever_raw"][s]]
        result["stop_missed_slots"] = stop_missed

        def worker_order_at(screen: tuple[int, int], probe_slot: int) -> list[str]:
            base = UNIT_BASE + probe_slot * UNIT_STRIDE
            xdo("key", "s")
            time.sleep(0.4)
            got: set[int] = set()
            click(*screen, button=3)
            t0 = time.monotonic()
            while time.monotonic() - t0 < 0.5:
                got.add(int.from_bytes(read_memory(pid, base + UNIT_PENDING_COMMAND_OFFSET, 4), "little"))
                time.sleep(0.01)
            return sorted(hex(v) for v in got)

        probe_slot = survivor_slots[0]
        validation = []
        move_destination: tuple[int, int] | None = None
        for cand in DESTINATION_CANDIDATES:
            orders = worker_order_at(cand, probe_slot)
            ok = hex(MOVE_PENDING) in orders
            validation.append({"screen": list(cand), "pending_seen": orders, "move_ok": ok})
            if ok:
                move_destination = cand
                break
        result["move_destination_validation"] = validation
        move_missed: list[int] = list(survivor_slots)
        if move_destination is not None:
            # Issue the validated MOVE destination against the CURRENT
            # selection -- still the same sparse (post-kill) state the STOP
            # test just measured. A fresh drag here would rebuild the array
            # densely from index 0 (lap720) and stop exercising R3 entirely.
            current_buffer = read_full_buffer(pid, sel_base, sel_cap)
            live_survivors = [s for s in survivor_slots if s in current_buffer["slots_all"]]
            move_obs = sample_ever(pid, live_survivors, lambda: click(*move_destination, button=3), window=3.0)
            result["move_observation"] = move_obs
            snap("05-after-move")
            if not alive():
                raise ProbeError("game not alive after move click")
            move_missed = [s for s in live_survivors if MOVE_PENDING not in move_obs["ever_raw"][s]]
        result["move_missed_slots"] = move_missed

        if stop_missed or move_missed:
            result["status"] = "FAIL_R3_CONFIRMED"
        else:
            result["status"] = "PASS_NO_SPARSE_GAP"
    except (OSError, subprocess.SubprocessError, ProbeError, ValueError, KeyError, IndexError) as exc:
        if result["status"] == "UNKNOWN":
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
        subprocess.run(["wineserver", "-k"], env=env, stdout=log, stderr=log, timeout=10, check=False)
        subprocess.run(["wineserver", "-w"], env=env, stdout=log, stderr=log, timeout=10, check=False)
        if xvfb is not None and xvfb.poll() is None:
            xvfb.terminate()
            xvfb.wait(timeout=5)
        result["cleanup"] = {"prefix_processes_after": runtime_env._prefix_pids(prefix)}
        result["source_sha_after"] = sha256(source_exe)
        result["source_unchanged"] = result["source_sha_after"] == ORIGINAL_SHA
        write_json(artifact_root / "probe-result.json", result)
        log.close()
    return result


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", choices=("original", "candidate-v4", "candidate-v5", "candidate-v6"), required=True)
    ap.add_argument("--scenario", choices=SCENARIOS, default="front-death")
    ap.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    ap.add_argument("--runtime-root", type=Path, required=True)
    ap.add_argument("--artifact-root", type=Path, required=True)
    args = ap.parse_args(argv)
    res = run_probe(args.source, args.runtime_root, args.artifact_root, variant=args.variant,
                     scenario=args.scenario)
    print(json.dumps({k: res.get(k) for k in
                       ("status", "error", "variant", "scenario", "source_unchanged", "kill_plan",
                        "stop_missed_slots", "move_missed_slots", "structural_ok")}, ensure_ascii=False))
    return 0 if res.get("status") == "PASS_NO_SPARSE_GAP" else 2


if __name__ == "__main__":
    raise SystemExit(main())
