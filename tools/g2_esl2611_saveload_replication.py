#!/usr/bin/env python3
"""Independent save/load replication of the G2 combos (V8/V89) on top of ``tools.g2_esl2610_spike_probe.live_probe``.

The live lane (seed99 fixture, 8 AI, synthetic 160 units + 7 heroes per owner) is reused unchanged; only its save
step (``_save_roundtrip``) is replaced.  Modes (``--mode``):

* ``roundtrip`` -- save at >1200 live, play on, load, compare per-slot (slot,type,owner,uid,hp,x,y) for slots >= 1200,
  then play ``--after-seconds`` and sample combat/guard state; optional ``--legacy-save`` (made by the official EXE)
  is loaded afterwards and played the same way; optional ``--second-game`` leaves the game for the title and starts a
  new 8-AI game in the same process.
* ``official-save`` -- on the pure official 2611 EXE (G8 skipped) play the same fixture and keep a save for the
  legacy-load lane.
* ``explore`` -- command-file shell for finding UI click points (``<artifact>/cmd.txt`` lines ``click X Y``,
  ``key NAME``, ``shot NAME``, ``quit``).
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from typing import Any

from tools import g2_esl2610_spike_probe as spike
from tools import runtime_env
from tools.g5_candidate_drag_probe import capture

REPO = Path(__file__).resolve().parents[1]
SEED_GOAL_OLD = "_custom_game_chain_inject_g2_eight_ai_seed42"
SEED_GOAL_NEW = "_custom_game_chain_inject_g2_eight_ai_seed99"
EXPECTED_SHA = {"v8": "1e83466eab020818a6c0e9057508d71451af3ee1098af43ebefc20de8ab96e3d",
                "v89": "39680ebbb202ba79cca4c47ac3eeb73b5cc9e8dbbf75c99ba679d07b1422db51"}  # ESL 2613 combo pins
UNIT_STRIDE = 0x758
STOCK_CAPACITY = 1200
CTX: dict[str, Any] = {}


def ps_samples_all_3(rows: list[dict[str, Any]]) -> bool:
    """True only for a nonempty, complete sample set with every process in-game."""
    return bool(rows) and all(row.get("alive") is True and row.get("ps") == 3
                              and "error" not in row for row in rows)


def validate_frozen_candidate(meta: Any, candidate: bytes, variant: str, *,
                              expected_candidate_sha: str,
                              expected_input_sha: str,
                              rebuilt_candidate: bytes | None = None,
                              rebuilt_report: Any = None) -> bool:
    """Fail closed unless frozen metadata, actual candidate and fresh rebuild agree."""
    import hashlib

    if variant not in EXPECTED_SHA or rebuilt_candidate is None or not isinstance(rebuilt_report, dict):
        return False
    if hashlib.sha256(candidate).hexdigest() != expected_candidate_sha:
        return False
    if rebuilt_candidate != candidate:
        return False
    try:
        build = meta["build"]
        combo = build["combo"]
        spike = build["spike"]
        rebuilt_spike = rebuilt_report["detail"]["g2"]
        layers = ["G2", "G6", "G8"] + (["G9"] if variant == "v89" else [])
        return (combo["schema"] == "syw2plus.esl2613.g2-combo.v1"
                and combo["variant"] == variant
                and combo["layers"] == layers
                and combo["input_sha256"] == expected_input_sha
                and combo["candidate_sha256"] == expected_candidate_sha
                and spike == rebuilt_spike)
    except (KeyError, TypeError):
        return False


def remap_goal(goal: str) -> str:
    return SEED_GOAL_NEW if goal == SEED_GOAL_OLD else goal


def unit_rows(raw: bytes) -> tuple[int, int, int, int, int, int, int]:
    """(type, owner, uid, hp, x, y) of one unit record's first 0x2A6 bytes, prefixed by 0 (slot filled by caller)."""
    hp = int.from_bytes(raw[0xB4:0xB8], "little", signed=True)
    x = int.from_bytes(raw[0x2A2:0x2A4], "little", signed=True)
    y = int.from_bytes(raw[0x2A4:0x2A6], "little", signed=True)
    return (0, raw[0x8D], raw[0x8E], int.from_bytes(raw[0x29C:0x2A0], "little"), hp, x, y)


def snapshot(pid: int, pool_base: int, exist_base: int, capacity: int) -> dict[int, tuple[int, ...]]:
    """slot -> (slot,type,owner,uid,hp,x,y) of every live unit, read in one pass."""
    exist = spike.read_memory(pid, exist_base, capacity * 2)
    out: dict[int, tuple[int, ...]] = {}
    for slot in range(1, capacity):
        if exist[2 * slot] or exist[2 * slot + 1]:
            row = unit_rows(spike.read_memory(pid, pool_base + slot * UNIT_STRIDE, 0x2A6))
            out[slot] = (slot, *row[1:])
    return out


def is_one_tick_drift(before: tuple[int, ...], after: tuple[int, ...]) -> bool:
    """Same slot/type/owner/uid, position within one tile, hp not higher: what a single game tick of play can change."""
    return before[:4] == after[:4] and abs(before[5] - after[5]) <= 1 and abs(before[6] - after[6]) <= 1 and after[4] <= before[4]


def diff_snapshots(before: dict[int, tuple[int, ...]], after: dict[int, tuple[int, ...]], *, min_slot: int = 0) -> dict[str, Any]:
    keys = {s for s in (*before, *after) if s >= min_slot}
    missing = sorted(s for s in keys if s in before and s not in after)
    extra = sorted(s for s in keys if s in after and s not in before)
    changed = sorted(s for s in keys if s in before and s in after and before[s] != after[s])
    one_tick = [s for s in changed if is_one_tick_drift(before[s], after[s])]
    return {"compared": len([s for s in keys if s in before]), "missing_after": len(missing), "extra_after": len(extra),
            "changed": len(changed), "changed_one_tick_drift": len(one_tick), "changed_other": len(changed) - len(one_tick),
            "exact": not (missing or extra or changed),
            "examples": [{"slot": s, "before": before.get(s), "after": after.get(s)} for s in (missing + extra + changed)[:6]]}


class Ui:
    """Click/key/screenshot access to the private game window of the running probe."""

    def __init__(self, artifact_root: Path) -> None:
        self.display = CTX["display"]
        self.artifact_root = artifact_root
        self.env = dict(os.environ, DISPLAY=self.display)
        self.log = (artifact_root / "ui.log").open("a", encoding="utf-8")
        outer, content = runtime_env._game_window_ids(runtime_env._window_tree(self.display, 10))
        info = runtime_env._xwininfo_details(self.display, content or outer, 10)
        self.ox, self.oy, self.outer = int(info["x"]), int(info["y"]), outer

    def click(self, x: int, y: int) -> None:
        subprocess.run([sys.executable, str(REPO / "tools/x11_mouse_click.py"), "--display", self.display,
                        str(self.ox + x), str(self.oy + y), "--button", "1"], env=self.env, stdout=self.log,
                       stderr=self.log, timeout=10, check=True)

    def key(self, name: str) -> None:
        subprocess.run(["xdotool", "windowfocus", self.outer], env=self.env, stdout=self.log, stderr=self.log, timeout=10, check=False)
        subprocess.run(["xdotool", "key", name], env=self.env, stdout=self.log, stderr=self.log, timeout=10, check=True)

    def shot(self, name: str) -> None:
        capture(self.display, self.artifact_root / f"{name}.png", self.log)


RESTART_CLICK = (400, 308)  # pause menu "다시하기"
CONFIRM_CLICK = (409, 331)  # confirm button of the pause-menu dialogs
EXIT_CLICKS = ((400, 343), (409, 331))  # pause menu "초기메뉴" then the confirm button (found with --mode explore)


def wait_ps(pid: int, target: int, timeout: float) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            if spike.read_state(pid).get("ps") == target:
                return
        except (OSError, ValueError):
            pass
        time.sleep(0.4)
    raise RuntimeError(f"ps {target} timeout")


def leave_and_restart(ui: Ui, pid: int) -> dict[str, Any]:
    """Pause menu -> title -> new 8-AI game (seed99 goal) in the same process; returns the new game's first state."""
    for attempt in range(3):
        ui.key("Escape")
        try:
            wait_ps(pid, 23, 20)
            break
        except RuntimeError:
            ui.shot(f"escape_attempt{attempt}")
    else:
        raise RuntimeError("pause menu (ps 23) never appeared")
    for point in EXIT_CLICKS:
        ui.click(*point)
        time.sleep(1.0)
    wait_ps(pid, 9, 90)
    time.sleep(2)
    ui.click(184, 560)
    wait_ps(pid, 7, 45)
    chain = runtime_env._g4_send_control_goal(CTX["prefix"], SEED_GOAL_NEW, 30.0)
    if chain.get("ok") is not True:
        raise RuntimeError(f"second chain inject failed: {chain.get('reason')}")
    wait_ps(pid, 3, 90)
    time.sleep(6)
    return {"chain": {"ok": chain.get("ok"), "reason": chain.get("reason")}}


def guard_lines(prefix: Path) -> list[str]:
    path = prefix / "drive_c" / "g2_guard_fault.jsonl"
    return path.read_text(errors="replace").splitlines() if path.exists() else []


def markers(pid: int) -> dict[str, Any]:
    from tools import esl2610_runtime

    mod = spike._module_markers(pid, CTX.get("starts"))
    snap = spike._module_snapshot(pid, CTX.get("starts"))
    return {"modules": mod, "perunit_records": {k: v["records_used"] for k, v in snap.get("perunit", {}).items()},
            "module_used": {k: v["used"] for k, v in snap.get("module_arrays", {}).items()},
            "selection_count": int.from_bytes(spike.read_memory(pid, esl2610_runtime.SELECTION_COUNT_VA, 4), "little"),
            "tick": spike.read_state(pid).get("tick")}


def play_window(pid: int, layout: tuple[int, int, int], seconds: float, label: str, every: float = 15.0) -> dict[str, Any]:
    """Sample a played-on game: alive/ps/tick/live/hp of slots >= 1200, deaths since the first sample, guard lines."""
    pool_base, exist_base, capacity = layout
    prefix = CTX["prefix"]
    first = snapshot(pid, pool_base, exist_base, capacity)
    rows: list[dict[str, Any]] = []
    t0 = time.monotonic()
    while True:
        alive = Path(f"/proc/{pid}").exists()
        row: dict[str, Any] = {"t": round(time.monotonic() - t0, 1), "alive": alive}
        if alive:
            try:
                now = snapshot(pid, pool_base, exist_base, capacity)
                st = spike.read_state(pid)
                high = [r for r in now.values() if r[0] >= STOCK_CAPACITY]
                row.update({"ps": st.get("ps"), "tick": st.get("tick"), "live": len(now), "live_ge_1200": len(high),
                            "hp_sum_ge_1200": sum(r[4] for r in high), "dead_since_start": len([k for k in first if k not in now]),
                            "hp_changed": len([k for k in first if k in now and first[k][4] != now[k][4]]),
                            "kills_records": spike._module_markers(pid, CTX.get("starts")).get("kills_records"),
                            "guard_lines": len(guard_lines(prefix))})
            except (OSError, ValueError) as exc:
                row["error"] = str(exc)
        rows.append(row)
        if not alive or time.monotonic() - t0 >= seconds:
            break
        time.sleep(every)
    ticks = [r["tick"] for r in rows if r.get("tick") is not None]
    return {"label": label, "samples": rows, "alive_end": rows[-1]["alive"], "ps_all_3": ps_samples_all_3(rows),
            "tick_advanced": bool(ticks) and ticks[-1] > ticks[0], "combat": rows[-1].get("dead_since_start", 0) > 0 or rows[-1].get("hp_changed", 0) > 0,
            "guard_lines_end": len(guard_lines(prefix)), "guard_examples": guard_lines(prefix)[:5]}


def roundtrip(pid: int, supply: Any, game: Path, pool_base: int, exist_base: int, capacity: int,
              artifact_root: Path, slot: int = 5, legacy_save: Path | None = None,
              starts: dict[str, int] | None = None) -> dict[str, Any]:
    if starts is not None:
        CTX["starts"] = starts
    layout = (pool_base, exist_base, capacity)
    ui = Ui(artifact_root) if CTX.get("second_game") else None
    out: dict[str, Any] = {"guard_lines_before": len(guard_lines(CTX["prefix"]))}
    before = snapshot(pid, *layout[:2], capacity)
    out["tick_at_before_snapshot"] = spike.read_state(pid).get("tick")
    out["tick_before_save"] = spike.read_state(pid).get("tick")
    out["save_receipt"] = spike._bridge(supply, 2, 0, slot, timeout=60)
    files = sorted((game / "save").glob(f"*{slot:03d}*"))
    out["save_files"] = [p.name for p in files]
    if files:
        out["save_size"] = files[0].stat().st_size
        shutil.copy2(files[0], artifact_root / f"saved_{files[0].name}")
    time.sleep(15)
    drift = snapshot(pid, *layout[:2], capacity)
    out["tick_before_load"] = spike.read_state(pid).get("tick")
    out["load_receipt"] = spike._bridge(supply, 3, 0, slot, timeout=60)
    after = snapshot(pid, *layout[:2], capacity)
    out["tick_at_after_snapshot"] = spike.read_state(pid).get("tick")
    out["live"] = {"before": len(before), "drift": len(drift), "after": len(after)}
    out["slots_ge_1200_before"] = sum(1 for s in before if s >= STOCK_CAPACITY)
    out["slots_ge_1200_after"] = sum(1 for s in after if s >= STOCK_CAPACITY)
    out["drift_differs_ge_1200"] = not diff_snapshots(before, drift, min_slot=STOCK_CAPACITY)["exact"]
    out["compare_ge_1200"] = diff_snapshots(before, after, min_slot=STOCK_CAPACITY)
    out["compare_all"] = diff_snapshots(before, after)
    out["restored_exact"] = out["compare_all"]["exact"]
    ident = lambda d: {k: v[:4] for k, v in d.items()}  # noqa: E731
    out["compare_identity_slot_type_owner_uid"] = diff_snapshots(ident(before), ident(after), min_slot=STOCK_CAPACITY)["exact"]
    out["markers_after_load"] = markers(pid)
    out["post_load_play"] = play_window(pid, layout, CTX["after_seconds"], "post_load")
    if ui is not None:
        try:
            out["second_game"] = leave_and_restart(ui, pid)
            snap = snapshot(pid, *layout[:2], capacity)
            out["second_game"].update({"live": len(snap), "live_ge_1200": len([r for r in snap.values() if r[0] >= STOCK_CAPACITY]),
                                       "highest_slot": max(snap, default=0), "markers": markers(pid)})
            out["second_game"]["play"] = play_window(pid, layout, 30, "second_game", every=10)
        except Exception as exc:  # noqa: BLE001
            out["second_game"] = {"error": f"{type(exc).__name__}: {exc}"}
            ui.shot("second_game_failure")
    if legacy_save is not None:
        try:
            dest = game / "save" / f"save{slot + 1:03d}.dat"
            shutil.copy2(legacy_save, dest)
            out["legacy_save_sha256"] = spike._sha256(legacy_save.read_bytes())
            out["legacy_markers_before_load"] = markers(pid)
            out["legacy_state_before_load"] = spike._legacy_state(pid, CTX.get("starts"))
            out["legacy_load_receipt"] = spike._bridge(supply, 3, 0, slot + 1, timeout=60)
            time.sleep(2)
            out["legacy_live_after"] = len(snapshot(pid, *layout[:2], capacity))
            out["legacy_markers_after_load"] = markers(pid)
            out["legacy_state_after_load"] = spike._legacy_state(pid, CTX.get("starts"))
            out["legacy_ps"] = spike.read_state(pid).get("ps")
            out["legacy_play"] = play_window(pid, layout, CTX["after_seconds"], "legacy_load")
            out["legacy_tick_progress"] = [row["tick"] for row in out["legacy_play"]["samples"]
                                           if isinstance(row.get("tick"), int)]
            if ui is not None:
                out["legacy_restart"] = restart_game(ui, pid, layout)
        except Exception as exc:  # noqa: BLE001
            out["legacy_error"] = f"{type(exc).__name__}: {exc}"
            if ui is not None:
                ui.shot("legacy_failure")
    return out


def restart_game(ui: Ui, pid: int, layout: tuple[int, int, int]) -> dict[str, Any]:
    """Pause menu -> 다시하기 (restart) -> confirm; records whether the tick/unit set reset."""
    capacity = layout[2]
    before = {"tick": spike.read_state(pid).get("tick"), "live": len(snapshot(pid, layout[0], layout[1], capacity))}
    ui.key("Escape")
    wait_ps(pid, 23, 20)
    ui.click(*RESTART_CLICK)
    time.sleep(1.5)
    ui.shot("restart_after_click")
    ui.click(*CONFIRM_CLICK)
    deadline = time.monotonic() + 40
    after: dict[str, Any] = {}
    while time.monotonic() < deadline:
        st = spike.read_state(pid)
        after = {"ps": st.get("ps"), "tick": st.get("tick"), "live": len(snapshot(pid, layout[0], layout[1], capacity))}
        if st.get("ps") == 3 and st.get("tick") is not None and before["tick"] is not None and st["tick"] < before["tick"]:
            break
        time.sleep(1)
    ui.shot("restart_end")
    reset = after.get("ps") == 3 and after.get("tick") is not None and after["tick"] < (before["tick"] or 0)
    return {"before": before, "after": after, "restart_took_effect": reset}


def explore(pid: int, artifact_root: Path) -> dict[str, Any]:
    ui = Ui(artifact_root)
    cmd = artifact_root / "cmd.txt"
    done = 0
    while True:
        lines = cmd.read_text().splitlines() if cmd.exists() else []
        for line in lines[done:]:
            parts = line.split()
            done += 1
            if parts[0] == "quit":
                return {"explored": True}
            if parts[0] == "click":
                ui.click(int(parts[1]), int(parts[2]))
            elif parts[0] == "key":
                ui.key(parts[1])
            elif parts[0] == "shot":
                ui.shot(parts[1])
            elif parts[0] == "newgame":
                (artifact_root / "newgame.json").write_text(json.dumps(leave_and_restart(ui, pid)))
            elif parts[0] == "state":
                (artifact_root / "state.json").write_text(json.dumps(spike.read_state(pid)))
        time.sleep(1)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["roundtrip", "official-save", "explore"], required=True)
    parser.add_argument("--variant", choices=["base", "v8", "v89"], required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--tick-seconds", type=float, default=45.0)
    parser.add_argument("--accelerate", type=int, default=160)
    parser.add_argument("--heroes", type=int, default=7)
    parser.add_argument("--after-seconds", type=float, default=125.0)
    parser.add_argument("--exe", type=Path, help="use this prebuilt combo EXE (its SHA must equal the expected V8/V89 SHA)")
    parser.add_argument("--frozen-from", type=Path, help="live_result.json whose build.spike report matches --exe (layer3 starts)")
    parser.add_argument("--no-guard", action="store_true", help="do not arm PAGE_NOACCESS on the old storage")
    parser.add_argument("--second-game", action="store_true")
    parser.add_argument("--legacy-save", type=Path, default=None)
    args = parser.parse_args(argv)
    if args.frozen_from and not args.exe:
        parser.error("--frozen-from requires --exe so candidate bytes can be checked")
    if args.frozen_from and args.variant not in EXPECTED_SHA:
        parser.error("--frozen-from is only valid for V8/V89 candidates")
    original_goal = runtime_env._g4_send_control_goal
    original_xvfb = runtime_env._xvfb
    sent: list[str] = []

    def send(prefix: Path, goal: str, timeout: float) -> dict[str, Any]:
        sent.append(remap_goal(goal))
        CTX["prefix"] = prefix
        return original_goal(prefix, sent[-1], timeout)

    def xvfb(*a: Any, **k: Any) -> Any:
        proc, display = original_xvfb(*a, **k)
        if a[1:] == ("1600x1200x24",):  # the probe's game display (prepare() starts its own short-lived one)
            CTX["display"] = display
        return proc, display

    runtime_env._g4_send_control_goal = send  # type: ignore[assignment]
    runtime_env._xvfb = xvfb  # type: ignore[assignment]
    if args.exe and not args.frozen_from:
        from patches.esl2610 import g2_combo_2610

        want = args.exe.read_bytes()
        real_build = g2_combo_2610.build

        def checked(data: bytes, variant: str, stock: bytes | None = None) -> Any:
            image, report = real_build(data, variant, stock=stock)
            if image != want:
                raise SystemExit(f"live rebuild {spike._sha256(image)} != frozen {spike._sha256(want)}")
            return image, report

        g2_combo_2610.build = checked  # type: ignore[assignment]
    if args.frozen_from:
        from patches.esl2610 import g2_combo_2610
        from patches.esl2610 import g2_pool4093_2610, pe_extend

        exe_bytes = args.exe.read_bytes()
        digest = spike._sha256(exe_bytes)
        if digest != EXPECTED_SHA[args.variant]:
            raise SystemExit(f"frozen EXE sha {digest} != pinned ESL 2613 candidate {EXPECTED_SHA[args.variant]}")
        try:
            meta = json.loads(args.frozen_from.read_text())
            base_bytes = pe_extend.BASE_PATH.read_bytes()
            stock_bytes = g2_pool4093_2610.STOCK_ORACLE.read_bytes()
            rebuilt, rebuilt_report = g2_combo_2610.build(base_bytes, args.variant, stock=stock_bytes)
        except (OSError, ValueError, KeyError) as exc:
            raise SystemExit(f"cannot rebuild frozen candidate from pinned inputs: {exc}") from exc
        if not validate_frozen_candidate(meta, exe_bytes, args.variant,
                                         expected_candidate_sha=EXPECTED_SHA[args.variant],
                                         expected_input_sha=pe_extend.BASE_SHA256,
                                         rebuilt_candidate=rebuilt, rebuilt_report=rebuilt_report):
            raise SystemExit("frozen metadata/candidate does not match pinned-input independent rebuild")
        g2_combo_2610.build = lambda data, variant, stock=None: (rebuilt, rebuilt_report)  # type: ignore[assignment]
    CTX["after_seconds"], CTX["second_game"] = args.after_seconds, args.second_game
    for name in ("_module_markers", "_module_snapshot"):
        def remember(pid: int, starts: Any = None, _f: Any = getattr(spike, name)) -> Any:
            CTX["starts"] = starts
            return _f(pid, starts)
        setattr(spike, name, remember)
    if args.mode == "roundtrip":
        spike._save_roundtrip = roundtrip  # type: ignore[assignment]
    if args.mode == "explore":
        spike._save_roundtrip = lambda pid, supply, game, pb, eb, cap, art, **_k: explore(pid, art)  # type: ignore[assignment]
    save_test = args.mode != "official-save"
    if args.mode == "official-save":
        from patches.esl2610 import g8_supply_1500_500_5000 as g8

        g8.build_candidate = lambda data, **_k: (data, {"skipped": "official 2611 pure"})  # type: ignore[assignment]
        orig_rt = spike._save_roundtrip
        spike._save_roundtrip = lambda *a, **k: orig_rt(*a, **{**k, "legacy_save": None})  # type: ignore[assignment]
        save_test = True
    out = spike.live_probe(args.runtime_root, args.artifact_root, variant=args.variant,
                           tick_seconds=args.tick_seconds, accelerate=args.accelerate, heroes=args.heroes,
                           save_test=save_test, legacy_save=args.legacy_save,
                           guard=not args.no_guard)
    out["replication"] = {"sent_goals": sent, "mode": args.mode}
    (args.artifact_root / "replication.json").write_text(json.dumps({k: out.get(k) for k in ("status", "build", "replication", "save_test", "peak_live", "error", "guard_log")}, indent=1, default=str))
    print(json.dumps({k: out.get(k) for k in ("status", "variant", "peak_live", "error")}, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
