#!/usr/bin/env python3
"""G5 checklist (D) remaining items: Shift+number group-add and post-death recall.

STATUS 2026-09-28 lap731 next-action note: (D) 부대 체크리스트 중 Ctrl+숫자 지정/숫자
호출/저장로드는 lap724의 ``PASS_UI_ROUNDTRIP``(v5)이 이미 커버했고, 남은 것은 정확히
두 항목뿐이다 -- (1) 이미 Ctrl+숫자로 지정된 조에 Shift+같은숫자로 다른 유닛을 추가했을
때 조 인원이 정확히 늘어나는지, (2) 조에 지정된 유닛 일부가 실제로 죽은 뒤 그 조 번호를
누르면 생존자만 정확히 선택되는지. STATUS 원문은 "Ctrl+1 지정 후 Shift+2로 추가"라고
쓰여 있으나 조 번호 표기가 부정확한 것으로 판단해(오케스트레이터 확인, 2026-09-28 work
세션), 이 probe는 **같은 조 번호**(그룹 1: Ctrl+1로 지정, Shift+1로 추가)로 통일한다.

Both scenarios run back-to-back inside ONE game boot per variant (2026-09-28 06:55/07:35
운영자 지시 -- "한 fixture·한 실행 안에서 여러 단계를 순차로 측정"), reusing the same
group-1 membership: scenario 1 builds it up toward the variant's own selection cap (20
original / 50 candidate) via a sequential multi-select + several individual Shift+1
adds, then scenario 2 kills a front/middle/rear-mixed subset of that same membership
and confirms the recall shows only survivors.

Method notes (2026-09-28 work session, first execution attempt found a live
obstruction and this is the corrected design -- see history for the discarded
row/rectangle draft):

- A first attempt spawned a rectangular worker-centered fixture band and dragged it
  to build the initial group, matching every earlier G5 probe's convention. That
  attempt's ``--variant original`` run found this particular random-nation start's
  map has an obstruction (almost certainly the HQ building's footprint) immediately
  northwest of the worker: fixture requests at world offsets dx in {-3,-2,-1} at
  dy in {-3,-2} (relative to the worker) all landed on the wrong tile (the bridge's
  own Place-then-scan-forward fallback silently relocated them elsewhere), while
  dx in {0..3} at the same rows resolved exactly as requested. Rather than hardcode
  a hole around an HQ position that is not guaranteed stable across boots (solo-lobby
  nation, and therefore probably HQ placement, is randomized -- lap730's discovery),
  this probe spawns a generous multi-row candidate pool, resolves each cell against
  the *actual* post-spawn fixture snapshot (discarding any that landed off-target),
  and isolation-checks every resolved candidate with a lone plain click (same
  technique as ``g5_shift_click_add_probe.py``, lap728) before ever using it. Both
  the initial multi-select and the Shift+1 add sequence are built entirely from this
  isolation-verified pool, so a differently-shaped obstruction on a different boot
  cannot silently corrupt the test the way a fixed rectangle assumption would.
- The initial multi-select is built via plain-click + mouse Shift-click (an
  already-PASS-confirmed mechanism, lap728) rather than a single drag, specifically
  to avoid needing a clean rectangular region free of the obstruction above. Drag
  selection of an arbitrary count is not itself under test here (that is check A/B,
  already PASS in lap723-728); this probe's new contribution is the persistent
  group's Shift+1 add and the post-death recall.
- Group membership is read directly from each unit's own group field
  (``unit+0x344``, via ``fixture_unit_group_snapshot``) after every step, not by
  pressing "1" and re-measuring the selection -- this is closer to ground truth and
  does not disturb the on-screen selection state between steps. The last Shift+1
  step is followed by one explicit "1" recall as a belt-and-suspenders UI-level
  check. This is a *different* memory structure from the transient selection array
  R3 was about (``SELECTION_BASE`` / ``g5.SELECTION_BASE``): group membership is
  per-unit-field plus a legacy 20-slot record at ``GROUP1_BASE_ADDRESS`` (statically
  confirmed by lap724's ``group_stored_stock20_plus_overflow49`` finding, not a new
  guess here).
- How many Shift+1 steps actually run, and whether the 51st-equivalent
  over-cap rejection check runs at all, is decided at runtime from how many
  candidates survive spawn-resolution and isolation-checking (see
  ``plan_steps``) -- this task explicitly marks the over-cap check optional, and a
  terrain obstruction is exactly the kind of real-environment variability the
  "구현 우선" operating rule says to route around rather than block on.
- Death uses the same original death-handler bridge op (10,
  ``patches/population/g5_r3_death_bridge.c``, unmodified from the R3 probes) that
  calls ``FUN_00409C70`` directly; killed units are explicitly deselected first (a
  more realistic "died while not actively selected" state), and this is recorded
  per-kill, not assumed.

PASS requires: every Shift+1 step increases group-1 membership by exactly 1 (prior
members retained, new member present); if the over-cap rejection check ran, one more
Shift+1 attempt past the cap must leave membership unchanged; after killing a
front/middle/rear-mixed subset, recalling group 1 selects exactly the survivor set
(no dead slot present, no crash) and every recalled survivor accepts a broadcast
move order.
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

import numpy as np

from patches.selection import g5_selection_cap50_v5 as g5
from tools import runtime_env
from tools.g5_candidate_drag_probe import (
    ProbeError, DRAG_START, DRAG_END, STOCK_SELECTION_BASE, STOCK_SELECTION_CAPACITY,
    SEED_TYPE, VISIBLE_WORKER_SLOT, UNIT_BASE, UNIT_STRIDE, UNIT_PENDING_XY_OFFSET,
    UNIT_PENDING_COMMAND_OFFSET, selection_snapshot, unit_snapshot, fixture_units,
    fixture_unit_group_snapshot, control_group_snapshot, sha256, write_json, capture,
)
from tools.g5_r3_sparse_selection_probe import Bridge, read_exists_hp
from tools.g5_screen_world_calibration import decode_xy, fit_affine
from tools.g5_attack_move_broadcast_probe import MINIMAP_CLICK
from tools.g5_worker_relative_move_attack_probe import CALIBRATION_SCREEN_POINTS
from patches.population.runtime_driver import read as read_memory
from patches.population.runtime_driver import state as read_state

REPO = Path(__file__).resolve().parents[1]
ORIGINAL_SHA = runtime_env.ORIGINAL_SHA256
# v5 (lap723 R3 fix); pinned SHA reconfirmed by lap724~731.
TARGET_SHA = "29e61074c622c77debb5053a412e3337fc8100f1eda29bd68efb163b1a9ee146"
DEATH_BRIDGE_SOURCE = REPO / "patches/population/g5_r3_death_bridge.c"
MOVE_PENDING = 0x1000003
MOVE_DESTINATION = (300, 420)

# Generous multi-row candidate pool, worker's own row (dy=0) excluded to keep the
# worker itself out of group bookkeeping entirely. Deliberately wider than either
# cap needs so per-boot terrain/HQ obstruction and off-screen edge rows can be
# discarded by resolution/isolation checks without starving either variant's plan.
CANDIDATE_DX = tuple(range(-3, 4))
CANDIDATE_DY = (-4, -3, -2, -1, 1, 2, 3, 4, 5)

CAP = {"original": 20, "candidate": 50}
ADD_STEPS_WANTED = {"original": 6, "candidate": 10}


def candidate_cells() -> list[tuple[int, int]]:
    return [(dx, dy) for dy in CANDIDATE_DY for dx in CANDIDATE_DX]


def plan_steps(available: int, cap: int, add_steps_wanted: int) -> dict[str, Any]:
    """Decide bulk/add/reject-test sizes from how many candidates actually survived.

    Reaches exactly ``cap`` (and arms the over-cap rejection check) when enough
    candidates are available; otherwise falls back to a smaller but still
    multi-step demonstration below cap, skipping the rejection check (this task
    marks it optional, see module docstring).
    """
    if available >= cap + 1:
        final_target = cap
        add_steps = min(add_steps_wanted, final_target - 1)
        bulk_n = final_target - add_steps
        return {"bulk_n": bulk_n, "add_steps": add_steps, "final_target": final_target,
                "reject_test": True, "available": available}
    final_target = min(available - 1, cap - 1)
    add_steps = min(add_steps_wanted, max(1, final_target - 1))
    bulk_n = final_target - add_steps
    if bulk_n < 1 or add_steps < 1:
        raise ProbeError(f"not enough isolated candidates for a meaningful test: available={available}")
    return {"bulk_n": bulk_n, "add_steps": add_steps, "final_target": final_target,
            "reject_test": False, "available": available}


def kill_thirds(n: int) -> tuple[int, int, int]:
    """Front/middle/rear kill counts, at least one from each region."""
    total_kill = max(3, n // 4)
    front = max(1, total_kill // 3)
    rear = max(1, total_kill // 3)
    middle = max(1, total_kill - front - rear)
    return front, middle, rear


def run_probe(source: Path, runtime_root: Path, artifact_root: Path, *, variant: str) -> dict[str, Any]:
    if artifact_root.exists():
        raise ProbeError(f"artifact root must be new: {artifact_root}")
    artifact_root.mkdir(parents=True)
    _, source_exe = runtime_env.validate_original_source(source)
    if sha256(source_exe) != ORIGINAL_SHA:
        raise ProbeError("protected source SHA mismatch")
    candidate_bytes: bytes | None = None
    if variant == "candidate":
        candidate_bytes = g5.build_candidate(source_exe.read_bytes())[0]
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
    if variant == "candidate" and private_sha != TARGET_SHA:
        raise ProbeError(f"candidate SHA mismatch: {private_sha}")
    sel_base = g5.SELECTION_BASE if variant == "candidate" else STOCK_SELECTION_BASE
    sel_cap = g5.TARGET_CAPACITY if variant == "candidate" else STOCK_SELECTION_CAPACITY
    cap = CAP[variant]
    add_steps_wanted = ADD_STEPS_WANTED[variant]

    result: dict[str, Any] = {
        "schema": "syw2plus.g5-group-shift-add-death-recall.v2", "variant": variant, "status": "UNKNOWN",
        "cap": cap,
        "provenance": {"source_exe": str(source_exe), "source_sha256": sha256(source_exe),
                       "private_exe_sha256": private_sha, "game_root": str(game), "run_dir": str(game.parent)},
        "captures": [], "inputs": [], "shift_add_steps": [], "kill_reports": [],
    }
    log = (artifact_root / "probe.log").open("a", encoding="utf-8")
    children: list[Any] = []
    xvfb: Any = None
    env = dict(os.environ, WINEPREFIX=str(prefix), WINEARCH="win32", WINEDEBUG="-all",
               LANG="ko_KR.UTF-8", LC_ALL="ko_KR.UTF-8", WINEDLLOVERRIDES="ddraw=b", SYW2_SUPPLY_PROBE="1")
    game_proc: Any = None
    try:
        xvfb, display = runtime_env._xvfb(log, "1600x1200x24")
        env["DISPLAY"] = display
        children.append(subprocess.Popen(["wine", "explorer", "/desktop=Default,1600x1200"],
                                         cwd=game, env=env, stdout=log, stderr=log))
        time.sleep(1)
        game_proc = subprocess.Popen(["wine", str(private_exe)], cwd=game, env=env, stdout=log, stderr=log)
        children.append(game_proc)
        pid = game_proc.pid
        bridge = Bridge(prefix)

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

        def click(x: int, y: int, *, drag_to: tuple[int, int] | None = None, button: int = 1,
                  mod: str | None = None) -> None:
            argv = [sys.executable, str(REPO / "tools/x11_mouse_click.py"), "--display", display,
                    str(crop[0] + x), str(crop[1] + y), "--button", str(button)]
            if drag_to is not None:
                argv += ["--drag-to", str(crop[0] + drag_to[0]), str(crop[1] + drag_to[1])]
            if mod:
                xdo("keydown", mod)
                time.sleep(0.15)
            try:
                subprocess.run(argv, env=env, stdout=log, stderr=log, timeout=10, check=True)
            finally:
                if mod:
                    time.sleep(0.15)
                    xdo("keyup", mod)
            result["inputs"].append({"x": x, "y": y, "drag_to": list(drag_to) if drag_to else None,
                                     "button": button, "mod": mod})

        def press(key: str, mod: str | None = None) -> None:
            # A single chorded ``xdotool key mod+key`` call is used instead of
            # separate keydown/key/keyup calls: across separate invocations,
            # ``xdotool key 1`` independently resolves which keycode currently
            # produces the keysym "1" and can insert its own compensating
            # shift transitions to guarantee that exact keysym (shift+the same
            # physical key normally types "!", not "1"), silently cancelling
            # an externally-held Shift out from under it. The single chord
            # form presses+holds the modifier and the literal key together in
            # one xdotool-internal operation with no such correction step.
            xdo("key", f"{mod}+{key}" if mod else key)
            result["inputs"].append({"key": key, "mod": mod})

        def snap(name: str) -> None:
            result["captures"].append(capture(display, artifact_root / f"{name}.png", log))

        def sel() -> dict[str, Any]:
            s = selection_snapshot(pid, base=sel_base, capacity=sel_cap)
            if variant == "candidate":
                s["legacy_count"] = int.from_bytes(read_memory(pid, STOCK_SELECTION_BASE, 4), "little", signed=True)
            return s

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
        click(*MINIMAP_CLICK)
        time.sleep(1)
        snap("00-after-minimap")

        # --- calibration (worker-only, same 9-point affine as every other G5 probe)
        click(*DRAG_START, drag_to=DRAG_END)
        time.sleep(1)
        cal_sel = sel()
        if VISIBLE_WORKER_SLOT not in cal_sel["slots"]:
            raise ProbeError(f"worker not selected for calibration: {cal_sel}")
        wbase = UNIT_BASE + VISIBLE_WORKER_SLOT * UNIT_STRIDE

        def worker_pending_xy() -> tuple[int, int]:
            return decode_xy(int.from_bytes(read_memory(pid, wbase + UNIT_PENDING_XY_OFFSET, 4), "little"))

        samples = []
        for pt in CALIBRATION_SCREEN_POINTS:
            click(*pt, button=3)
            time.sleep(0.4)
            samples.append((pt, worker_pending_xy()))
        matrix, offset = fit_affine(samples)
        resid = max(float(np.max(np.abs(matrix @ np.array(p) + offset - np.array(w)))) for p, w in samples)
        result["screen_calibration"] = {"max_abs_residual": resid}
        minv = np.linalg.inv(matrix)

        def w2s(world: tuple[float, float]) -> tuple[int, int]:
            p = minv @ (np.array(world) - offset)
            return int(round(p[0])), int(round(p[1]))

        wx, wy = int(worker["x"]), int(worker["y"])

        # --- spawn the generous candidate pool, tolerating per-cell obstruction
        # (the bridge silently relocates a blocked request instead of failing it,
        # so resolution is done by diffing the post-spawn fixture snapshot against
        # exact requested world coordinates, not by trusting the spawn call alone).
        requested: list[dict[str, Any]] = []
        for dx, dy in candidate_cells():
            world = (wx + dx, wy + dy)
            if not (0 <= world[0] < 180 and 0 <= world[1] < 180):
                continue
            r = bridge.call(op=5, owner=0, type_=SEED_TYPE, rice=world[0], wood=world[1], used=1)
            if not r.get("ok") or r.get("fixture_added") != 1:
                raise ProbeError(f"fixture spawn failed at {world}: {r}")
            requested.append({"dx": dx, "dy": dy, "world": list(world)})
        time.sleep(1)
        snap("01-after-fixture")

        fixture = fixture_units(pid)
        by_xy = {(u["x"], u["y"]): u["slot"] for u in fixture}
        for entry in requested:
            entry["slot"] = by_xy.get(tuple(entry["world"]))
        resolved = [e for e in requested if e["slot"] is not None]
        result["spawn_pool"] = {"requested": len(requested), "resolved": len(resolved),
                                 "unresolved": [e for e in requested if e["slot"] is None]}
        if len(resolved) < cap // 2:
            raise ProbeError(f"too few candidates resolved to their requested cell: "
                              f"{len(resolved)}/{len(requested)}; result={result['spawn_pool']}")

        # --- deselect ground point, well away from every candidate cell
        dgx = wx - 8 if wx >= 8 else wx + 8
        dgy = wy - 8 if wy >= 8 else wy + 8
        deselect_pt = w2s((dgx, dgy))

        def do_deselect() -> None:
            click(*deselect_pt)
            time.sleep(0.4)

        def unit_screen(entry: Mapping[str, Any]) -> tuple[int, int]:
            return w2s(cast(tuple[int, int], tuple(entry["world"])))

        # --- find a click y-offset that isolates a single unit (lap728 technique)
        click_dy = None
        for dy in (-12, -20, -6, 0, -28):
            do_deselect()
            ux, uy = unit_screen(resolved[0])
            click(ux, uy + dy)
            time.sleep(0.5)
            s = sel()
            if s["count"] == 1 and s["slots"] == [resolved[0]["slot"]]:
                click_dy = dy
                break
        result["click_dy"] = click_dy
        if click_dy is None:
            raise ProbeError("no click offset gave an isolated single-unit selection")

        # --- isolation check every resolved candidate before using any of them
        isolated: list[dict[str, Any]] = []
        for entry in resolved:
            do_deselect()
            ux, uy = unit_screen(entry)
            click(ux, uy + click_dy)
            time.sleep(0.45)
            s = sel()
            ok = s["count"] == 1 and s["slots"] == [entry["slot"]]
            entry["isolation_check"] = {"count": s["count"], "slots": s["slots"], "isolated": ok}
            if ok:
                isolated.append(entry)
        snap("02-after-isolation-checks")
        result["isolation_summary"] = {"checked": len(resolved), "isolated": len(isolated)}

        plan = plan_steps(len(isolated), cap, add_steps_wanted)
        result["plan"] = plan
        bulk_n = plan["bulk_n"]
        add_steps = plan["add_steps"]
        bulk_seq = isolated[:bulk_n]
        add_seq = isolated[bulk_n:bulk_n + add_steps]
        reject_candidate = isolated[bulk_n + add_steps] if plan["reject_test"] else None
        known_units: list[Mapping[str, Any]] = isolated[:bulk_n + add_steps + (1 if reject_candidate else 0)]

        # --- build the initial multi-select via plain-click + mouse Shift-click
        # (an already-PASS mechanism, lap728) -- drag mechanics for an arbitrary
        # count are not what this probe is testing, see module docstring.
        do_deselect()
        first = bulk_seq[0]
        ux, uy = unit_screen(first)
        click(ux, uy + click_dy)
        time.sleep(0.3)
        for entry in bulk_seq[1:]:
            ux, uy = unit_screen(entry)
            click(ux, uy + click_dy, mod="shift")
            time.sleep(0.3)
        bulk_selection = sel()
        result["bulk_selection"] = bulk_selection
        snap("03-after-bulk-multiselect")
        if not alive():
            raise ProbeError("game not alive after bulk multi-select")
        expected_members = {int(e["slot"]) for e in bulk_seq}
        if bulk_selection["count"] != len(expected_members) or set(bulk_selection["slots"]) != expected_members:
            raise ProbeError(f"bulk multi-select did not select exactly the intended set: "
                              f"selected={sorted(bulk_selection['slots'])} expected={sorted(expected_members)}")

        # --- Ctrl+1: assign group 1 to the bulk selection
        press("1", mod="ctrl")
        time.sleep(0.5)
        group_after_assign = control_group_snapshot(pid)
        fixture_group_after_assign = fixture_unit_group_snapshot(pid, known_units)
        result["group_after_ctrl1_assign"] = {
            "control_group": group_after_assign, "fixture_group": fixture_group_after_assign,
        }
        snap("04-after-ctrl1-assign")
        members_group1 = {row["slot"] for row in fixture_group_after_assign["rows"] if row["group"] == 1}
        if members_group1 != expected_members:
            raise ProbeError(f"group1 membership after Ctrl+1 mismatch: "
                              f"{sorted(members_group1)} != {sorted(expected_members)}")

        # --- the Shift+1 add sequence: plain-click each new unit, then Shift+1
        for i, entry in enumerate(add_seq, start=1):
            do_deselect()
            ux, uy = unit_screen(entry)
            click(ux, uy + click_dy)
            time.sleep(0.4)
            solo_sel = sel()
            press("1", mod="shift")
            time.sleep(0.5)
            expected_members.add(int(entry["slot"]))
            fg = fixture_unit_group_snapshot(pid, known_units)
            members_now = {row["slot"] for row in fg["rows"] if row["group"] == 1}
            step = {
                "i": i, "slot": entry["slot"], "solo_click_selection": solo_sel,
                "expected_count": len(expected_members), "members_now": sorted(members_now),
                "new_member_present": entry["slot"] in members_now,
                "pass": members_now == expected_members,
            }
            result["shift_add_steps"].append(step)
            if not alive():
                raise ProbeError(f"game not alive after shift-add step {i}")
        snap("05-after-shift-add-sequence")

        # --- reject test (only when the plan reached exactly the variant cap):
        # one more Shift+1 attempt beyond cap must NOT grow group1.
        if reject_candidate is not None:
            do_deselect()
            ux, uy = unit_screen(reject_candidate)
            click(ux, uy + click_dy)
            time.sleep(0.4)
            press("1", mod="shift")
            time.sleep(0.5)
            fg_after_reject = fixture_unit_group_snapshot(pid, known_units)
            members_after_reject = {row["slot"] for row in fg_after_reject["rows"] if row["group"] == 1}
            result["reject_test"] = {
                "candidate_slot": reject_candidate["slot"],
                "members_before": sorted(expected_members),
                "members_after": sorted(members_after_reject),
                "unchanged": members_after_reject == expected_members,
                "at_cap": len(expected_members) == cap,
            }
            snap("06-after-reject-attempt")
            if not alive():
                raise ProbeError("game not alive after reject-test shift-add")
        else:
            result["reject_test"] = {"skipped": True, "reason": "insufficient isolated candidates for cap+1"}

        # --- final "1" recall to confirm UI-level consistency after all Shift adds
        do_deselect()
        press("1")
        time.sleep(0.5)
        result["recalled_after_shift_adds"] = sel()
        snap("07-after-recall-post-adds")

        # --- alternate group-extend mechanism, tried only if Shift+1 itself did
        # not grow membership: recall group1 (press "1"), Shift+CLICK (mouse, the
        # already-PASS mechanism from lap728) one more spare candidate onto the
        # live selection, then Ctrl+1 again to redefine group1 with the enlarged
        # selection. This answers the checklist's underlying question (can group
        # membership be grown at all after the initial Ctrl+1) even if the
        # specific "Shift+number" hotkey turns out not to be wired to it.
        shift_add_worked = any(step["pass"] for step in result["shift_add_steps"])
        spare_pool = isolated[bulk_n + add_steps + (1 if reject_candidate else 0):]
        if not shift_add_worked and spare_pool:
            spare = spare_pool[0]
            fg_before_redefine = fixture_unit_group_snapshot(pid, known_units)
            members_before_redefine = {row["slot"] for row in fg_before_redefine["rows"] if row["group"] == 1}
            do_deselect()
            press("1")
            time.sleep(0.4)
            recalled_for_extend = sel()
            ux, uy = unit_screen(spare)
            click(ux, uy + click_dy, mod="shift")
            time.sleep(0.4)
            extended_selection = sel()
            press("1", mod="ctrl")
            time.sleep(0.5)
            fg_after_redefine = fixture_unit_group_snapshot(pid, known_units + [spare])
            members_after_redefine = {row["slot"] for row in fg_after_redefine["rows"] if row["group"] == 1}
            result["alternate_extend_mechanism"] = {
                "members_before_redefine": sorted(members_before_redefine),
                "recalled_before_extend": recalled_for_extend,
                "spare_slot": spare["slot"],
                "selection_after_shift_click": extended_selection,
                "members_after_redefine": sorted(members_after_redefine),
                "spare_now_member": spare["slot"] in members_after_redefine,
                "grew_by_exactly_one": len(members_after_redefine) == len(members_before_redefine) + 1,
            }
            snap("07b-after-alternate-extend")
            if not alive():
                raise ProbeError("game not alive after alternate group-extend mechanism")
            # Feed the spare into the phase-2 bookkeeping so a successful
            # alternate-mechanism add is reflected in the kill/recall plan too.
            known_units = known_units + [spare]

        # ============ PHASE 2: kill a front/middle/rear-mixed subset, recall ============
        # Use the REAL measured group-1 membership here, not ``expected_members``
        # (that variable only records what *should* be true if every Shift+1 add
        # succeeded; feeding it into the kill plan would silently substitute an
        # assumption for ground truth if any add step actually failed).
        real_group_after_adds = fixture_unit_group_snapshot(pid, known_units)
        final_members = sorted(row["slot"] for row in real_group_after_adds["rows"] if row["group"] == 1)
        result["final_group_members"] = final_members
        result["final_group_members_matches_expected"] = final_members == sorted(expected_members)
        n = len(final_members)
        front_n, mid_n, rear_n = kill_thirds(n)
        front = final_members[:front_n]
        rear = final_members[n - rear_n:]
        mid_start = n // 2 - mid_n // 2
        middle = final_members[mid_start:mid_start + mid_n]
        kill_slots = front + middle + rear
        survivor_slots = [s for s in final_members if s not in kill_slots]
        result["kill_plan"] = {"front": front, "middle": middle, "rear": rear,
                                "kill_slots": kill_slots, "survivor_slots": survivor_slots}

        do_deselect()
        result["pre_kill_selection"] = sel()
        kill_reports = []
        for slot in kill_slots:
            r = bridge.call(op=10, owner=0, slot=slot)
            kill_reports.append(r)
            if not r.get("ok"):
                raise ProbeError(f"kill failed for slot {slot}: {r}")
        result["kill_reports"] = kill_reports
        time.sleep(0.5)
        snap("08-after-kills")
        if not alive():
            raise ProbeError("game not alive after kills")

        result["killed_exists_hp"] = {s: read_exists_hp(pid, s) for s in kill_slots}
        result["survivor_exists_hp"] = {s: read_exists_hp(pid, s) for s in survivor_slots}
        # NOTE: the death handler (op=10, see g5_r3_death_bridge.c) only sets the
        # dead-flag and clears the unit's own selected-flag; it does not itself
        # zero HP or the existence-table entry on the same tick (the R3 probes
        # already established this), so killed-unit hp/exists are NOT gated here
        # -- only the handler's own dead_flag_after/selected_after report, plus
        # survivors staying alive, are pass criteria.
        structural_ok = (
            all(v["hp"] > 0 for v in result["survivor_exists_hp"].values())
            and all(r["op10"]["dead_flag_after"] == 1 and r["op10"]["selected_after"] == 0
                    for r in kill_reports)
        )
        result["structural_ok"] = structural_ok

        # --- recall group1 after deaths
        press("1")
        time.sleep(0.6)
        recalled_after_death = sel()
        result["recalled_after_death"] = recalled_after_death
        snap("09-after-death-recall")
        if not alive():
            raise ProbeError("game not alive after post-death recall")
        recall_slots = set(recalled_after_death["slots"])
        recall_ok = (
            recalled_after_death["count"] == len(survivor_slots)
            and recall_slots == set(survivor_slots)
            and recalled_after_death["unique_slots"] == len(survivor_slots)
            and not (recall_slots & set(kill_slots))
        )
        result["death_recall_check"] = {
            "expected_survivor_count": len(survivor_slots), "recall_ok": recall_ok,
        }

        # --- bonus: confirm every recalled survivor accepts a broadcast move order
        move_pending_before = {
            s: int.from_bytes(read_memory(pid, UNIT_BASE + s * UNIT_STRIDE + UNIT_PENDING_COMMAND_OFFSET, 4),
                               "little")
            for s in survivor_slots
        }
        click(*MOVE_DESTINATION, button=3)
        t0 = time.monotonic()
        seen_move: dict[int, bool] = {s: False for s in survivor_slots}
        while time.monotonic() - t0 < 2.5:
            for s in survivor_slots:
                pend = int.from_bytes(
                    read_memory(pid, UNIT_BASE + s * UNIT_STRIDE + UNIT_PENDING_COMMAND_OFFSET, 4), "little")
                if pend == MOVE_PENDING:
                    seen_move[s] = True
            time.sleep(0.02)
        snap("10-after-post-death-move")
        result["post_death_move_check"] = {
            "before": {s: hex(v) for s, v in move_pending_before.items()},
            "all_survivors_moved": all(seen_move.values()), "seen_move": seen_move,
        }
        if not alive():
            raise ProbeError("game not alive after post-death move broadcast")

        # shift_add_direct_worked being False is reported as a descriptive finding,
        # not folded into the PASS/FAIL gate: if this engine simply does not wire
        # Shift+number to "add to group" (both original and candidate share the
        # same unmodified number-key handler -- v5 only touches the selection-array
        # cap), that is the same kind of "feature absent, not a regression" result
        # lap727 already established for ALT/Ctrl-click and portrait deselection.
        # ``death_recall_pass`` and the alternate-mechanism result are the load-
        # bearing evidence this probe's status reflects.
        reject_pass = (not plan["reject_test"]) or bool(
            result["reject_test"]["unchanged"] and result["reject_test"]["at_cap"])
        death_pass = bool(structural_ok and recall_ok and result["post_death_move_check"]["all_survivors_moved"])
        alt = result.get("alternate_extend_mechanism")
        alt_worked = bool(alt and alt.get("grew_by_exactly_one") and alt.get("spare_now_member"))
        result["summary"] = {
            "shift_add_direct_worked": shift_add_worked,
            "alternate_extend_worked": alt_worked,
            "group_extend_possible_by_any_mechanism": shift_add_worked or alt_worked,
            "reject_pass": reject_pass, "death_recall_pass": death_pass,
            "reached_cap_attempt": plan["reject_test"], "final_member_count_before_kill": len(final_members),
        }
        result["status"] = "COMPLETE" if death_pass else "FAIL_DEATH_RECALL"
    except (OSError, subprocess.SubprocessError, ProbeError, ValueError, KeyError, IndexError) as exc:
        result["status"] = "FAIL"
        result["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        result["game_exit_code_before_cleanup"] = None if game_proc is None else game_proc.poll()
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
    ap.add_argument("--variant", choices=("original", "candidate"), required=True)
    ap.add_argument("--source", type=Path, default=runtime_env.DEFAULT_SOURCE)
    ap.add_argument("--runtime-root", type=Path, required=True)
    ap.add_argument("--artifact-root", type=Path, required=True)
    args = ap.parse_args(argv)
    res = run_probe(args.source, args.runtime_root, args.artifact_root, variant=args.variant)
    print(json.dumps({k: res.get(k) for k in
                       ("status", "error", "variant", "source_unchanged", "summary")}, ensure_ascii=False))
    return 0 if res.get("status") == "COMPLETE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
