#!/usr/bin/env python3
"""Private Wine diagnostic session. Never attaches to an existing game process.

Addresses and scope: analysis/memory_maps/population_5000_runtime_0910.md.
Commands are read from the private output directory; only this spawned process is read.
"""

from __future__ import annotations
import argparse
import ctypes
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import time
from typing import TypeAlias, cast

REPO = Path(__file__).resolve().parents[2]
SCREENSHOTS = Path("/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/captures")
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from tools.runtime_env import (  # noqa: E402
    G1_UNIT_INTERNAL_ID_OFFSET,
    G1_UNIT_X_OFFSET,
    G1_UNIT_Y_OFFSET,
)
from patches.population.fixed_supply_5000 import (  # noqa: E402
    ORIGINAL_SHA256,
    digest as _digest,
)
from patches.population.full_tail_relocation_storage_layout_v1 import (  # noqa: E402
    layout as _tail_region_layout,
)

ExecutableProfile: TypeAlias = tuple[str, str]
ExecutableProfiles: TypeAlias = ExecutableProfile | tuple[ExecutableProfile, ...]

SUPPORTED_EXECUTABLES: dict[str, ExecutableProfiles] = {
    # The relocated pool probe must retain the original filename: the engine
    # has already shown filename-sensitive startup behaviour.  Keep the gate
    # fail-closed by accepting only the explicitly listed byte identities.
    "syw2plus_original.exe": (
        ("original", ORIGINAL_SHA256),
        (
            "fixed_supply_5000_original_filename",
            "0a1da2263ff099b9fc35d8c63bb82bbefec6dffbae0dcc7458e32887f3f34ad3",
        ),
        # W19 (lap439/440, docs/work/active/
        # G2_IMM_FIXUP_FALSE_POSITIVE_REPAIR_LAP439.md): the unit_pool imm
        # scanner false-positive repair changes every one of these
        # candidates' bytes (25 fewer bogus relocations applied). Per card
        # §6, old pins are kept (not erased, they still identify the
        # known-faulty pre-repair byte identity for comparison) and the
        # freshly rebuilt bytes are accepted under the *same* profile name
        # via a second tuple with the new SHA256.
        (
            "g2_unit_pool_expansion_v1_n1210_tail_relocated",
            "a3fd29340fa4d0fbd39b77127ef2d7f1b4993fe9453d0f2d32f981296aa73b41",
        ),
        (
            "g2_unit_pool_expansion_v1_n1210_tail_relocated",
            "fc607bec5f7c11664b2ba0a698fb411bf60b58300bfc6fa66e98d92443620573",
        ),
        (
            "g2_unit_pool_expansion_v1_n1210_supply5000",
            "90ed0bad35821c86553a0a0e163b93c892ff254fe4c1cdaba5a0deb0a31f6b91",
        ),
        (
            "g2_unit_pool_expansion_v1_n1210_supply5000",
            "55c8fb1109067a8aae08572a5bea6360c7a504ada2d0e1e534a6dc5bd39ab753",
        ),
        (
            "g2_unit_pool_expansion_v1_n1250_supply5000",
            "2420eb54493b6240c992969ff683f46231897046225c604a030ef55d10041312",
        ),
        (
            "g2_unit_pool_expansion_v1_n1250_supply5000",
            "c8f7e015e4f6b4791996285e9b0325b5b33a694795a2b478c33c380dac1d87ff",
        ),
        (
            "g2_full_unit_capacity_v1_n1250_supply5000",
            "c3bd799fefd31ffb8d02ed7e1d08bb734890c7e637c7eb3ffe4dc236004df5d3",
        ),
        (
            "g2_full_unit_capacity_v1_n1250_supply5000",
            "3cc91ef82fb660a6113a6307779ae98bfd7284e3eae804f19e841c1819453977",
        ),
        (
            "g2_full_unit_capacity_v1_n1250_supply5000_legacy",
            "66adee3f341b1cd96a80a76ddfac205c9264ae878db07ba08e3f2dc2eb47cf65",
        ),
        (
            "g2_full_capacity_v1_n4001_supply5000_owner1200",
            "20b95a94711590e1bd41559ce76a9de6e40c155948f8d559b1090909fc342794",
        ),
        (
            "g2_full_capacity_v1_n4001_supply5000_owner1200",
            "d13189bb9839b6cc9818624df792e1f465b820448c3f09b7ebc1e5b81f3c26c5",
        ),
        (
            "g2_full_capacity_v1_n4001_supply5000_owner1200_persistence",
            "1e90f62fdcecb49d47d85af54bef17744bb7ae9d895a43b1923fd59405a30093",
        ),
        (
            "g2_full_capacity_v1_n4001_supply5000_owner1200_persistence",
            "47087c194a6d55dea87d86146e39639e0eeffdeeea1a58c6b17b9c6987bf5a2c",
        ),
        (
            "g2_full_capacity_v1_n4001_persistence_compat",
            "4331d9cd646c03a0102394727894beaf893e5b9aa3505c4ddb41eb26a4ef9bbe",
        ),
        (
            "g2_full_capacity_v1_n4001_persistence_compat",
            "a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68",
        ),
    ),
    # Exact pure-transform outputs; external filenames/manifests are not trusted.
    "supply5000.exe": (
        "fixed_supply_5000",
        "0a1da2263ff099b9fc35d8c63bb82bbefec6dffbae0dcc7458e32887f3f34ad3",
    ),
    "g2_supply_5000.exe": (
        "fixed_supply_5000",
        "0a1da2263ff099b9fc35d8c63bb82bbefec6dffbae0dcc7458e32887f3f34ad3",
    ),
    # 2026-09-26: G2 새 목표(활성8인 각각 전비10000, docs/DESIGN.md). Same two-site
    # cap patch as fixed_supply_5000, immediate only (5000 -> 10000).
    "supply10000.exe": (
        "fixed_supply_10000",
        "039a358ca3e8031ce316bd57e8a66df0358babeba3a544d3e850f740cebc6a1d",
    ),
    "g2_supply_10000.exe": (
        "fixed_supply_10000",
        "039a358ca3e8031ce316bd57e8a66df0358babeba3a544d3e850f740cebc6a1d",
    ),
    "g2_unit_pool_n1210.exe": (
        "g2_unit_pool_expansion_v1_n1210",
        "303c78f81f816ed82e495fa4545cc23af3fa7200344eb029b4e9f31cabe96522",
    ),
    # lap399 control: byte-identical original under a different filename, to
    # separate "PS stuck at 40" caused by the candidate's own patch from a
    # filename-dependent engine behavior.  Same SHA256 as syw2plus_original.exe.
    "control_renamed_original.exe": ("control_renamed_original", ORIGINAL_SHA256),
    "supply5000_qhd.exe": (
        "combined_qhd_fixed_supply_5000",
        "d22904639adf03ddf2b6b3122a64a59131770e5ad85107290229e6932b319abc",
    ),
}

POOL_PROFILE_LAYOUTS = {
    "g2_unit_pool_expansion_v1_n1210_tail_relocated": (1210, 0x0108C000, 0x012B75F0),
    "g2_unit_pool_expansion_v1_n1210_supply5000": (1210, 0x0108C000, 0x012B75F0),
    "g2_unit_pool_expansion_v1_n1250_supply5000": (1250, 0x0108C000, 0x012C9BB0),
    "g2_full_unit_capacity_v1_n1250_supply5000": (1250, 0x0108C000, 0x012C9BB0),
    "g2_full_capacity_v1_n4001_supply5000_owner1200": (4001, 0x0108C000, 0x017B8658),
    "g2_full_capacity_v1_n4001_supply5000_owner1200_persistence": (
        4001,
        0x0108C000,
        0x017B8658,
    ),
    "g2_full_capacity_v1_n4001_persistence_compat": (4001, 0x0108C000, 0x017B8658),
    # lap695 (STATUS 2026-09-27): protected-original G2 candidate, 4093-slot
    # (4092 usable) tail relocation + owner500 + supply10000. unit_pool base
    # 0x0108C000 and unit_existence base 0x017E29F8 are the base-preserving
    # `full_tail_relocation_storage_layout_v1.layout(4093)` outputs for the
    # first two of the six relocated regions (see FULL_REGION_PROFILES for
    # the other four -- unit_age/category_slot_list_a/b/active_slot_list --
    # used by the lap697 global-live cross-check below).
    "g2_supply10000_pool4092_owner500": (4093, 0x0108C000, 0x017E29F8),
}
STOCK_POOL = (1200, 0x0066B790, 0x008990C8)

# Profiles whose "detailed" state should also decode the fourth-through-sixth
# relocated regions (unit_age, category_slot_list_a/b, active_slot_list) via
# the full six-region tail-relocation map, so callers can cross-check the
# authoritative active_slot_list against the unit_existence bitmap (dup/
# owner-sum verification) instead of trusting a single region in isolation.
# Value is the capacity passed to `full_tail_relocation_storage_layout_v1.
# layout()` -- the same capacity registered above in POOL_PROFILE_LAYOUTS.
FULL_REGION_PROFILES: dict[str, int] = {
    "g2_supply10000_pool4092_owner500": 4093,
}

G4_CONTROLLER_OPCODE_OFFSET = 0x0D32
G4_CONTROLLER_ARGUMENT_OFFSET = 0x0D34
G4_GROUP_COUNT_OFFSET = 0x348A
G4_GROUP_BASE_OFFSET = 0x3490
G4_GROUP_STRIDE = 0x02E0
G4_GROUP_LIMIT = 2
G4_ROUTE_MEMBER_COUNT_OFFSET = 0x0CBA
G4_ROUTE_MEMBER_IDS_OFFSET = 0x099A
G4_ROUTE_LIMIT = 10
G4_ROUTE_MEMBER_LIMIT = 20
PLAYER_STRUCT_SIZE = 0x3ABC


class IOV(ctypes.Structure):
    _fields_ = [("base", ctypes.c_void_p), ("size", ctypes.c_size_t)]


LIBC = ctypes.CDLL(None, use_errno=True)
LIBC.process_vm_readv.restype = ctypes.c_ssize_t


def read(pid, address, size):
    buf = ctypes.create_string_buffer(size)
    n = LIBC.process_vm_readv(
        pid,
        ctypes.byref(IOV(ctypes.cast(buf, ctypes.c_void_p), size)),
        1,
        ctypes.byref(IOV(address, size)),
        1,
        0,
    )
    if n != size:
        raise OSError(ctypes.get_errno(), f"read {pid}:{address:x}, got {n}/{size}")
    return buf.raw


def decode_g4_groups(data: bytes) -> dict[str, object]:
    """Decode the bounded AI-group targets already selected by the original engine."""

    if len(data) < PLAYER_STRUCT_SIZE:
        raise ValueError(f"PlayerStruct returned {len(data)}/{PLAYER_STRUCT_SIZE} bytes")

    def i16(off: int) -> int:
        return struct.unpack_from("<h", data, off)[0]

    count = i16(G4_GROUP_COUNT_OFFSET)
    if not 0 <= count <= G4_GROUP_LIMIT:
        return {"status": "UNSUPPORTED_COUNT", "count": count, "groups": []}
    groups: list[dict[str, object]] = []
    for index in range(count):
        base = G4_GROUP_BASE_OFFSET + index * G4_GROUP_STRIDE
        route_id = i16(base + 4)
        member_offset = G4_ROUTE_MEMBER_COUNT_OFFSET + route_id * 2
        valid_route = 0 <= route_id < G4_ROUTE_LIMIT
        member_count = i16(member_offset) if valid_route else None
        member_ids: list[int] = []
        if member_count is not None and 0 <= member_count <= G4_ROUTE_MEMBER_LIMIT:
            ids_offset = G4_ROUTE_MEMBER_IDS_OFFSET + route_id * G4_ROUTE_MEMBER_LIMIT * 4
            member_ids = list(struct.unpack_from(f"<{member_count}I", data, ids_offset))
        groups.append({
            "index": index,
            "target_x": i16(base),
            "target_y": i16(base + 2),
            "route_id": route_id,
            "state": i16(base + 6),
            "member_count": member_count,
            "member_ids": member_ids,
            "waypoint_count": i16(base + 0x2D8),
            "waypoint_index": i16(base + 0x2DA),
            "last_update_tick": struct.unpack_from("<i", data, base + 0x2DC)[0],
        })
    return {"status": "OK", "count": count, "groups": groups}


def state(pid, detailed=False, profile="original"):
    def integer(a):
        return struct.unpack("<i", read(pid, a, 4))[0]

    result = {"pid": pid, "time": time.time(), "ps": integer(0x4ED818), "tick": integer(0x8924B8)}
    result["players"] = []
    for owner in range(8):
        data = read(pid, 0x956770 + owner * 0x3ABC, PLAYER_STRUCT_SIZE)

        def i16(off):
            return struct.unpack_from("<h", data, off)[0]

        def i32(off):
            return struct.unpack_from("<i", data, off)[0]

        result["players"].append(
            dict(
                owner=owner,
                nation=data[0],
                ai=data[2],
                rice=i32(0x14),
                wood=i32(0x18),
                reserved=i32(0x1C),
                count=i16(0x200A),
                used=i16(0x200C),
                count_cap=i16(0x2010),
                cap=i16(0x2012),
                controller_opcode=i16(G4_CONTROLLER_OPCODE_OFFSET),
                controller_argument=i16(G4_CONTROLLER_ARGUMENT_OFFSET),
                ai_groups=decode_g4_groups(data),
            )
        )
    if detailed:
        capacity, unit_base, exists_base = POOL_PROFILE_LAYOUTS.get(profile, STOCK_POOL)
        exists = struct.unpack(f"<{capacity}h", read(pid, exists_base, capacity * 2))
        units = []
        for slot, active in enumerate(exists):
            if not active:
                continue
            u = read(pid, unit_base + slot * 0x758, 0x758)

            def h(off):
                return struct.unpack_from("<h", u, off)[0]

            def i(off):
                return struct.unpack_from("<i", u, off)[0]

            units.append(
                dict(
                    slot=slot,
                    type=u[0x8D],
                    owner=u[0x8E],
                    internal_id=i(G1_UNIT_INTERNAL_ID_OFFSET),
                    hp=i(0x0B4),
                    command=h(0x290),
                    production_type=i(0x320),
                    progress=i(0x1F8),
                    x=h(G1_UNIT_X_OFFSET),
                    y=h(G1_UNIT_Y_OFFSET),
                )
            )
        result["units"] = units

        full_capacity = FULL_REGION_PROFILES.get(profile)
        if full_capacity is not None:
            regions_by_name = {r.name: r for r in _tail_region_layout(full_capacity).regions}
            active_region = regions_by_name["active_slot_list"]
            count_addr = active_region.new_start + active_region.array_new_span
            active_count = struct.unpack("<H", read(pid, count_addr, 2))[0]
            active_slots: list[int] = []
            if 0 <= active_count <= full_capacity:
                active_slots = list(
                    struct.unpack(
                        f"<{active_count}H",
                        read(pid, active_region.new_start, active_count * 2),
                    )
                )
            exists_slots = {u["slot"] for u in units}
            result["active_slot_list"] = {
                "count": active_count,
                "slots": active_slots,
                "duplicate_count": len(active_slots) - len(set(active_slots)),
                "matches_existence_bitmap": set(active_slots) == exists_slots,
            }
    return result


def atomic_json(path, data):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    tmp.replace(path)


def control_goal_payload(request_id: object, goal: str, timeout_ms: int) -> dict[str, object]:
    """Build the string-ID request required by the inmm control protocol."""
    return {
        "version": "1",
        "request_id": str(request_id),
        "goal": goal,
        "timeout_ms": timeout_ms,
    }


def validate_game_root(path: Path) -> Path:
    """Reject this repo's inputs and the known sibling/original installations."""
    root = path.resolve()
    originals = (
        REPO / "Syw2plus",
        REPO.parent / "Syw2plus_re" / "Syw2plus",
        REPO.parent / "Syw2plus",
        # 2026-09-26 사용자 결정: 원본 게임 기준 경로 전환.
        REPO.parent / "[ESL]Syw2plus",
    )
    if any(root == p.resolve() or p.resolve() in root.parents for p in originals):
        raise ValueError("Refusing original game directory; use a private complete copy")
    return root


def validate_runtime_executable(root: Path, executable: str) -> dict[str, str]:
    """Fail closed on arbitrary ``--exe`` before Wine/Xvfb/process launch."""
    candidate_name = Path(executable)
    if candidate_name.name != executable or executable not in SUPPORTED_EXECUTABLES:
        raise ValueError("unsupported executable profile; exact original/fixed/combined bytes required")
    path = root / executable
    if path.is_symlink() or not path.is_file():
        raise ValueError("supported executable is missing or linked")
    actual = _digest(path.read_bytes())
    configured = SUPPORTED_EXECUTABLES[executable]
    profiles = (
        cast(tuple[ExecutableProfile, ...], configured)
        if isinstance(configured[0], tuple)
        else (cast(ExecutableProfile, configured),)
    )
    for profile, expected in profiles:
        if actual == expected:
            return {"name": executable, "profile": profile, "sha256": actual}
    profile_names = "/".join(profile for profile, _expected in profiles)
    raise ValueError(f"{profile_names} executable SHA256 mismatch")


def build_runtime_env(prefix: Path, display: str) -> dict[str, str]:
    """Match the known-good isolated Wine launch contract."""
    return dict(
        os.environ,
        DISPLAY=display,
        WINEPREFIX=str(prefix),
        WINEARCH="win32",
        LANG="ko_KR.UTF-8",
        LC_ALL="ko_KR.UTF-8",
        WINEDEBUG="-all",
        WINEDLLOVERRIDES="ddraw=b",
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game-root", type=Path, required=True)
    ap.add_argument("--prefix", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--display", required=True)
    ap.add_argument("--exe", default="supply5000.exe")
    ap.add_argument(
        "--screen", choices=("1024x768", "1600x1200", "2560x1440"), default="1024x768"
    )
    args = ap.parse_args()
    root = validate_game_root(args.game_root)
    executable = validate_runtime_executable(root, args.exe)
    prefix = args.prefix.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    num = args.display.lstrip(":")
    if Path(f"/tmp/.X{num}-lock").exists() or Path(f"/tmp/.X11-unix/X{num}").exists():
        raise SystemExit("Display already used")
    for p in Path("/proc").iterdir():
        if not p.name.isdigit():
            continue
        try:
            if f"WINEPREFIX={prefix}".encode() in (p / "environ").read_bytes().split(b"\0"):
                raise SystemExit("Prefix already in use")
        except (OSError, PermissionError):
            pass
    env = build_runtime_env(prefix, args.display)
    if executable["profile"] in {
        "original",
        "fixed_supply_5000",
        "fixed_supply_5000_original_filename",
        "fixed_supply_10000",
        "g2_unit_pool_expansion_v1_n1210_supply5000",
        "g2_unit_pool_expansion_v1_n1250_supply5000",
        "g2_full_unit_capacity_v1_n1250_supply5000",
        "g2_full_unit_capacity_v1_n1250_supply5000_legacy",
        "g2_full_capacity_v1_n4001_supply5000_owner1200",
        "g2_full_capacity_v1_n4001_supply5000_owner1200_persistence",
        "g2_full_capacity_v1_n4001_persistence_compat",
    }:
        env["SYW2_SUPPLY_PROBE"] = "1"
    log = (out / "wine.log").open("wb")
    xvfb = None
    desktop = None
    game = None
    try:
        xvfb = subprocess.Popen(
            ["Xvfb", args.display, "-screen", "0", f"{args.screen}x24"], stdout=log, stderr=log
        )
        time.sleep(1)
        desktop = subprocess.Popen(
            ["wine", "explorer", "/desktop=Default,1600x1200"],
            cwd=root,
            env=env,
            stdout=log,
            stderr=log,
        )
        # Match tools.runtime_env.g1_baseline's verified launch envelope.
        time.sleep(1)
        game = subprocess.Popen(
            ["wine", str(root / args.exe)], cwd=root, env=env, stdout=log, stderr=log
        )
        atomic_json(
            out / "session.json",
            dict(
                game_pid=game.pid,
                display=args.display,
                prefix=str(prefix),
                root=str(root),
                exe=executable["name"],
                exe_profile=executable["profile"],
                exe_sha256=executable["sha256"],
            ),
        )
        last_id = None
        last_sample = 0
        trace = (out / "trace.jsonl").open("a", buffering=1)
        while game.poll() is None:
            now = time.time()
            if now - last_sample >= 1:
                try:
                    s = state(game.pid, profile=executable["profile"])
                    trace.write(json.dumps(s) + "\n")
                    atomic_json(out / "latest.json", s)
                except OSError as error:
                    atomic_json(out / "latest.json", dict(error=str(error), pid=game.pid))
                last_sample = now
            try:
                req = json.loads((out / "request.json").read_text())
            except (OSError, ValueError):
                time.sleep(0.1)
                continue
            if req["id"] == last_id:
                time.sleep(0.1)
                continue
            last_id = req["id"]
            response = {"id": last_id, "op": req["op"]}
            try:
                if req["op"] == "snapshot":
                    response["state"] = state(game.pid, True, profile=executable["profile"])
                elif req["op"] == "read":
                    response["hex"] = read(game.pid, int(req["va"], 0), int(req["size"])).hex()
                    response.update(pid=game.pid, va=req["va"], size=req["size"])
                elif req["op"] == "goal":
                    r = control_goal_payload(
                        last_id,
                        req["goal"],
                        req.get("timeout_ms", 60000),
                    )
                    atomic_json(prefix / "drive_c/inmm_control_request.json", r)
                    deadline = time.time() + r["timeout_ms"] / 1000 + 5
                    while time.time() < deadline:
                        try:
                            result = json.loads(
                                (prefix / "drive_c/inmm_control_result.json").read_text()
                            )
                            if result.get("request_id") == r["request_id"]:
                                response["result"] = result
                                break
                        except (OSError, ValueError):
                            pass
                        time.sleep(0.1)
                    else:
                        raise TimeoutError("control goal")
                elif req["op"] == "click":
                    subprocess.run(
                        [
                            sys.executable,
                            str(REPO / "tools/x11_mouse_click.py"),
                            "--display",
                            args.display,
                            str(req["x"]),
                            str(req["y"]),
                        ],
                        check=True,
                        stdout=log,
                        stderr=log,
                    )
                elif req["op"] == "key":
                    subprocess.run(
                        [
                            sys.executable,
                            str(REPO / "tools/x11_send_keys.py"),
                            req["key"],
                            "--display",
                            args.display,
                        ],
                        check=True,
                        stdout=log,
                        stderr=log,
                    )
                elif req["op"] == "shot":
                    SCREENSHOTS.mkdir(parents=True, exist_ok=True)
                    shot = SCREENSHOTS / (
                        time.strftime("%Y%m%d_%H%M%S") + "_supply5000_" + str(last_id) + ".png"
                    )
                    subprocess.run(["scrot", str(shot)], env=env, check=True)
                    response["path"] = str(shot)
                elif req["op"] == "stop":
                    atomic_json(out / "response.json", response)
                    break
                else:
                    raise ValueError("Unknown op")
            except Exception as error:
                response["error"] = repr(error)
            atomic_json(out / "response.json", response)
        atomic_json(out / "exit.json", dict(returncode=game.poll()))
    finally:
        # Unique prefix only; never kill another wineserver/display.
        if game and game.poll() is None:
            game.terminate()
        subprocess.run(["wineserver", "-k"], env=env, stdout=log, stderr=log)
        if desktop and desktop.poll() is None:
            desktop.terminate()
        if xvfb and xvfb.poll() is None:
            xvfb.terminate()
            xvfb.wait(timeout=10)
        log.close()


if __name__ == "__main__":
    main()
