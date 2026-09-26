#!/usr/bin/env python3
"""Isolated runtime evidence for qhd_probe.py; no shared Wine sessions touched."""

import datetime
import json
import os
import pathlib
import struct
import subprocess
import time

ROOT = pathlib.Path("/home/dev_00/syw2plus-qhd-probe-0910")
PREFIX = pathlib.Path("/home/dev_00/.wine_syw2_qhd_probe_0910_r2")
OUT = pathlib.Path("/home/dev_00/sharedfolder/260320_Syw2plus/temp/20260910_qhd_probe")
OUT = OUT / os.environ.get("QHD_PROBE_RUN", "qhd_fullredraw_r1")
DISPLAY = ":193"


def main():
    if pathlib.Path("/tmp/.X193-lock").exists():
        raise RuntimeError("Display occupied; refusing reuse")
    OUT.mkdir(parents=True, exist_ok=True)
    env = dict(
        os.environ, DISPLAY=DISPLAY, WINEPREFIX=str(PREFIX), LANG="ko_KR.UTF-8", WINEDEBUG="-all"
    )
    for name in ("inmm_state_log.jsonl", "inmm_control_request.json", "inmm_control_result.json"):
        (PREFIX / "drive_c" / name).unlink(missing_ok=True)
    log = (OUT / "runtime.log").open("w")
    xvfb = subprocess.Popen(
        ["Xvfb", DISPLAY, "-screen", "0", "2560x1440x24"], stdout=log, stderr=log
    )
    time.sleep(2)
    game = None
    shell = None
    try:
        for key, value in [
            ("HKCU\\Software\\Wine\\Explorer", "Default"),
            ("HKCU\\Software\\Wine\\Explorer\\Desktops", "2560x1440"),
        ]:
            subprocess.run(
                [
                    "wine",
                    "reg",
                    "add",
                    key,
                    "/v",
                    "Desktop" if value == "Default" else "Default",
                    "/d",
                    value,
                    "/f",
                ],
                env=env,
                stdout=log,
                stderr=log,
                timeout=35,
            )
        shell = subprocess.Popen(
            ["wine", "explorer", "/desktop=Default,2560x1440"], env=env, stdout=log, stderr=log
        )
        time.sleep(5)
        game = subprocess.Popen(
            ["wine", str(ROOT / os.environ.get("QHD_PROBE_EXE", "qhd_probe.exe"))],
            cwd=ROOT,
            env=env,
            stdout=log,
            stderr=log,
        )
        print("pid", game.pid, flush=True)

        def memory(va, n):
            with open(f"/proc/{game.pid}/mem", "rb", buffering=0) as f:
                f.seek(va)
                return f.read(n)

        def state():
            try:
                return struct.unpack("<I", memory(0x4ED818, 4))[0]
            except (OSError, struct.error):
                return None

        def wait_ps(target, seconds):
            until = time.monotonic() + seconds
            while time.monotonic() < until:
                if state() == target:
                    return True
                if game.poll() is not None:
                    return False
                if "Unhandled page fault" in (OUT / "runtime.log").read_text(errors="replace"):
                    return False
                time.sleep(0.25)
            return False

        def shot(tag):
            p = OUT / (datetime.datetime.now().strftime("%Y%m%d_%H%M%S_") + tag + ".png")
            subprocess.run(["scrot", str(p)], env=env, check=True)
            print("screenshot", p, flush=True)

        def goal(name, timeout=45):
            rid = f"qhd-{time.time_ns()}"
            (PREFIX / "drive_c/inmm_control_request.json").write_text(
                json.dumps(dict(version="1", request_id=rid, goal=name, timeout_ms=timeout * 1000))
            )
            until = time.monotonic() + timeout + 3
            while time.monotonic() < until:
                try:
                    r = json.loads((PREFIX / "drive_c/inmm_control_result.json").read_text())
                    if r.get("request_id") == rid:
                        (OUT / (name + ".json")).write_text(json.dumps(r, indent=2))
                        return r
                except (OSError, ValueError):
                    pass
                time.sleep(0.3)
            return {}

        def snapshot(tag):
            m = json.loads(
                (
                    ROOT / (os.environ.get("QHD_PROBE_MANIFEST", "qhd_probe.exe.patch.json"))
                ).read_text()
            )
            rec = dict(tag=tag, pid=game.pid, state=state(), time=time.time())
            for name, va, size in [
                ("display", 0xE5BF18, 32),
                ("ddraw_fields", 0xE5BF18 + 0x1508, 32),
                ("clip", 0xB3AC80, 16),
                ("camera", 0xB42D7C, 8),
                ("mouse_xy", 0x4ED814, 4),
                ("selected_count", 0x899024, 4),
                ("selected_roster", 0x899028, 32),
                ("tick", 0x8924B8, 4),
                ("buffer_prefix", int(m["terrain_va"], 16), 64),
            ]:
                try:
                    rec[name] = memory(va, size).hex()
                except OSError as ex:
                    rec[name] = str(ex)
            (OUT / (tag + ".json")).write_text(json.dumps(rec, indent=2))
            print(rec, flush=True)
            # Exact indexed pixels, not scaled desktop capture; verify wider-render content.
            try:
                (OUT / (tag + "_terrain.bin")).write_bytes(
                    memory(int(m["terrain_va"], 16), 2560 * 1440)
                )
            except OSError:
                pass

        print("title", wait_ps(9, 60), "state", state(), flush=True)
        shot("title")
        if state() != 9:
            snapshot("startup_failure")
            return
        print("custom", goal("enter_custom_game", 20), flush=True)
        if os.environ.get("QHD_DEFER_DISPLAY") == "1":
            with open(f"/proc/{game.pid}/mem", "r+b", buffering=0) as f:
                f.seek(0x464505)
                f.write(struct.pack("<I", 2560))
                f.seek(0x46450C)
                f.write(struct.pack("<I", 1440))
            print("deferred display immediates installed after title", flush=True)
        print("chain", goal("_custom_game_chain_inject", 60), flush=True)
        print("ingame", wait_ps(3, 60), "state", state(), flush=True)
        snapshot("initial")
        shot("initial")
        if state() != 3:
            return
        time.sleep(8)
        snapshot("after8")
        shot("after8")
        subprocess.run(["xdotool", "mousemove", "1280", "730", "click", "1"], env=env)
        time.sleep(2)
        snapshot("hq_click_wide")
        shot("hq_click_wide")
        subprocess.run(["xdotool", "keydown", "Right"], env=env)
        time.sleep(2)
        subprocess.run(["xdotool", "keyup", "Right"], env=env)
        snapshot("camera_right")
        shot("camera_right")
        subprocess.run(["xdotool", "mousemove", "2400", "700"], env=env)
        time.sleep(4)
        snapshot("mouse_wide")
        shot("mouse_wide")
        time.sleep(20)
        snapshot("after32")
        shot("after32")
    finally:
        if game and game.poll() is None:
            game.terminate()
        if shell and shell.poll() is None:
            shell.terminate()
        subprocess.run(["wineserver", "-k"], env=env, stdout=log, stderr=log, timeout=10)
        xvfb.terminate()
        xvfb.wait(timeout=10)
        log.close()


if __name__ == "__main__":
    raise SystemExit(
        "Historical QHD launcher disabled: its fixed paths are not safe for new sessions. "
        "Use patches/population/runtime_driver.py with explicit private paths."
    )
