from __future__ import annotations

import hashlib
from pathlib import Path
import struct

from tools.g4_path_fixture_preflight import build_report


def _write_pe(path: Path, *, table_target: int) -> None:
    data = bytearray(0x600)
    data[:2] = b"MZ"
    struct.pack_into("<I", data, 0x3C, 0x80)
    data[0x80:0x84] = b"PE\0\0"
    struct.pack_into("<H", data, 0x86, 1)
    struct.pack_into("<H", data, 0x94, 0xE0)
    optional = 0x98
    struct.pack_into("<H", data, optional, 0x10B)
    struct.pack_into("<I", data, optional + 28, 0x00400000)
    section = optional + 0xE0
    data[section:section + 8] = b".data\0\0\0"
    struct.pack_into("<IIII", data, section + 8, 0x1000, 0xE0000, 0x200, 0x400)
    struct.pack_into("<I", data, 0x400 + 0x5FF4, table_target)
    path.write_bytes(data)


def test_preflight_fails_closed_without_comparison_fixture(tmp_path: Path, monkeypatch) -> None:
    exe = tmp_path / "game.exe"
    # Use a larger synthetic section so the target VA maps into the file.
    data = bytearray(0x7000)
    data[:2] = b"MZ"
    struct.pack_into("<I", data, 0x3C, 0x80)
    data[0x80:0x84] = b"PE\0\0"
    struct.pack_into("<H", data, 0x86, 1)
    struct.pack_into("<H", data, 0x94, 0xE0)
    optional = 0x98
    struct.pack_into("<I", data, optional + 28, 0x00400000)
    section = optional + 0xE0
    struct.pack_into("<IIII", data, section + 8, 0x10000, 0xE0000, 0x10000, 0x400)
    struct.pack_into("<I", data, 0x400 + 0x5FF4, 0x0046B840)
    exe.write_bytes(data)
    wrapper = tmp_path / "wrapper.c"
    astar = tmp_path / "astar.c"
    wrapper.write_text("wrapper", encoding="utf-8")
    astar.write_text("astar", encoding="utf-8")
    runtime = tmp_path / "runtime.py"
    runtime.write_text(
        'G1_UNIT_X_OFFSET = 0x2A2\nG1_UNIT_Y_OFFSET = 0x2A4\n'
        'x={"x": unit.get("x"), "y": unit.get("y")}\n', encoding="utf-8"
    )
    mouse = tmp_path / "mouse.py"
    mouse.write_text('XTestFakeButtonEvent\nap.add_argument("--button")\n', encoding="utf-8")
    hashes = {
        exe: "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac",
        wrapper: "681a88396967577c814257bb3211afda628f121e4a537534d68f5637ee22da87",
        astar: "8e5237e98934ef7ed230fba1e8509fb60a451cca52ddd5a4ccd304188e3270a9",
    }
    monkeypatch.setattr(hashlib, "sha256", hashlib.sha256)
    import tools.g4_path_fixture_preflight as module
    monkeypatch.setattr(module, "_sha256", lambda path: hashes.get(path, hashlib.sha256(path.read_bytes()).hexdigest()))

    report = build_report(exe=exe, wrapper=wrapper, astar=astar,
                          runtime_env=runtime, mouse_helper=mouse)

    assert report["verdict"] == "BLOCKED"
    assert report["activation_allowed"] is False
    assert report["blockers"] == [
        "deterministic_scene_fixture", "obstacle_occupancy_oracle",
        "movement_command_trace", "repeatability_gate",
    ]


def test_preflight_rejects_wrong_table_target(tmp_path: Path, monkeypatch) -> None:
    exe = tmp_path / "game.exe"
    data = bytearray(0x7000)
    data[:2] = b"MZ"
    struct.pack_into("<I", data, 0x3C, 0x80)
    data[0x80:0x84] = b"PE\0\0"
    struct.pack_into("<H", data, 0x86, 1)
    struct.pack_into("<H", data, 0x94, 0xE0)
    optional = 0x98
    struct.pack_into("<I", data, optional + 28, 0x00400000)
    section = optional + 0xE0
    struct.pack_into("<IIII", data, section + 8, 0x10000, 0xE0000, 0x10000, 0x400)
    struct.pack_into("<I", data, 0x400 + 0x5FF4, 0xDEADBEEF)
    exe.write_bytes(data)
    wrapper = tmp_path / "wrapper.c"
    astar = tmp_path / "astar.c"
    runtime = tmp_path / "runtime.py"
    mouse = tmp_path / "mouse.py"
    for path in (wrapper, astar, runtime, mouse):
        path.write_text("x", encoding="utf-8")
    import tools.g4_path_fixture_preflight as module
    monkeypatch.setattr(module, "_sha256", lambda _path: "wrong")

    report = build_report(exe=exe, wrapper=wrapper, astar=astar,
                          runtime_env=runtime, mouse_helper=mouse)

    entry = next(item for item in report["checks"] if item["name"] == "astar_table_entry")
    assert entry["status"] == "BLOCKED"
    assert entry["evidence"]["target_va"] == "0xDEADBEEF"
