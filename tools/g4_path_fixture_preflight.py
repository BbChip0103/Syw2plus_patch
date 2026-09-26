#!/usr/bin/env python3
"""Fail-closed preflight for an original-game pathfinding comparison fixture.

This tool does not launch or patch the game.  It records which prerequisites
are already grounded and which ones still prevent a repeatable before/after
pathfinding comparison.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct
from typing import Any


ORIGINAL_SHA256 = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"
WRAPPER_SHA256 = "681a88396967577c814257bb3211afda628f121e4a537534d68f5637ee22da87"
ASTAR_SHA256 = "8e5237e98934ef7ed230fba1e8509fb60a451cca52ddd5a4ccd304188e3270a9"
ASTAR_TABLE_ENTRY_VA = 0x004E5FF4
ASTAR_ENTRY_VA = 0x0046B840


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _pe_va_to_offset(data: bytes, va: int) -> int:
    if data[:2] != b"MZ":
        raise ValueError("not an MZ executable")
    pe_offset = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe_offset : pe_offset + 4] != b"PE\0\0":
        raise ValueError("missing PE signature")
    section_count = struct.unpack_from("<H", data, pe_offset + 6)[0]
    optional_size = struct.unpack_from("<H", data, pe_offset + 20)[0]
    optional = pe_offset + 24
    image_base = struct.unpack_from("<I", data, optional + 28)[0]
    rva = va - image_base
    section_table = optional + optional_size
    for index in range(section_count):
        section = section_table + index * 40
        virtual_size, virtual_address, raw_size, raw_offset = struct.unpack_from(
            "<IIII", data, section + 8
        )
        if virtual_address <= rva < virtual_address + max(virtual_size, raw_size):
            return raw_offset + (rva - virtual_address)
    raise ValueError(f"VA 0x{va:08X} is outside PE sections")


def _check(name: str, passed: bool, evidence: Any, blocker: str | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "name": name,
        "status": "PASS" if passed else "BLOCKED",
        "evidence": evidence,
    }
    if blocker is not None:
        result["blocker"] = blocker
    return result


def build_report(*, exe: Path, wrapper: Path, astar: Path, runtime_env: Path,
                 mouse_helper: Path) -> dict[str, Any]:
    exe_data = exe.read_bytes()
    exe_sha = _sha256(exe)
    wrapper_sha = _sha256(wrapper)
    astar_sha = _sha256(astar)
    table_offset = _pe_va_to_offset(exe_data, ASTAR_TABLE_ENTRY_VA)
    table_target = struct.unpack_from("<I", exe_data, table_offset)[0]
    runtime_text = runtime_env.read_text(encoding="utf-8")
    mouse_text = mouse_helper.read_text(encoding="utf-8")

    checks = [
        _check("pinned_original_executable", exe_sha == ORIGINAL_SHA256,
               {"path": str(exe), "sha256": exe_sha, "expected": ORIGINAL_SHA256}),
        _check("pinned_decompiler_inputs",
               wrapper_sha == WRAPPER_SHA256 and astar_sha == ASTAR_SHA256,
               {"wrapper_sha256": wrapper_sha, "astar_sha256": astar_sha}),
        _check("astar_table_entry", table_target == ASTAR_ENTRY_VA,
               {"entry_va": f"0x{ASTAR_TABLE_ENTRY_VA:08X}",
                "target_va": f"0x{table_target:08X}",
                "expected_target_va": f"0x{ASTAR_ENTRY_VA:08X}"}),
        _check("unit_coordinate_reader",
               all(token in runtime_text for token in (
                   "G1_UNIT_X_OFFSET = 0x2A2", "G1_UNIT_Y_OFFSET = 0x2A4",
                   '"x": unit.get("x")', '"y": unit.get("y")')),
               {"unit_x_offset": "0x2A2", "unit_y_offset": "0x2A4",
                "source": str(runtime_env)}),
        _check("right_click_injector",
               'ap.add_argument("--button"' in mouse_text and
               "XTestFakeButtonEvent" in mouse_text,
               {"source": str(mouse_helper), "required_button": 3}),
        _check("deterministic_scene_fixture", False,
               {"current_runtime_statement":
                "default two-player random game; map name/seed not exposed by approved read-only offsets"},
               "No pinned save/map plus observed replay seed currently guarantees the same pathfinding scene across runs."),
        _check("obstacle_occupancy_oracle", False, {},
               "No approved reader currently snapshots the exact passability/collision grid consumed by A*."),
        _check("movement_command_trace", False,
               {"available": "selection and generic XTest button injection",
                "missing": "integrated selected-slot right-click command plus per-tick x/y/result trace"},
               "A right-click helper exists, but no harness proves a deterministic move command and samples its route."),
        _check("repeatability_gate", False,
               {"required": ["same fixture hash", "same selected slot/type",
                              "same start/destination", "two original runs with identical route outcome"]},
               "No pair of original-game route traces exists."),
    ]
    blockers = [item["name"] for item in checks if item["status"] != "PASS"]
    return {
        "schema": "syw2plus.g4.path_fixture_preflight.v1",
        "observational_only": True,
        "activation_allowed": False,
        "verdict": "BLOCKED" if blockers else "READY",
        "checks": checks,
        "blockers": blockers,
        "conclusion": (
            "The original A* entry and low-level coordinate/input primitives are grounded, "
            "but a repeatable original-game comparison fixture is not yet available. "
            "Do not patch pathfinding constants or code from this evidence."
        ),
        "next_safe_fixture": {
            "kind": "diagnostic private-runtime fixture",
            "requirements": [
                "pin one save/map and verify its hash",
                "prove one movable selected unit and fixed start/destination",
                "snapshot the collision/passability inputs used by A*",
                "sample tick, slot, x, y and command state until arrival/failure",
                "require two byte-identical original trace outcomes before candidate comparison",
            ],
        },
    }


def main(argv: list[str] | None = None) -> int:
    root = Path(__file__).resolve().parents[1]
    original_root = root.parent / "Syw2plus_re"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path,
                        default=original_root / "Syw2plus" / "syw2plus_original.exe")
    parser.add_argument("--wrapper", type=Path,
                        default=original_root / "analysis/ghidra_output/FUN_0041af90.c")
    parser.add_argument("--astar", type=Path,
                        default=original_root / "analysis/ghidra_output/FUN_0046b840.c")
    parser.add_argument("--runtime-env", type=Path, default=root / "tools/runtime_env.py")
    parser.add_argument("--mouse-helper", type=Path, default=root / "tools/x11_mouse_click.py")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    report = build_report(exe=args.exe, wrapper=args.wrapper, astar=args.astar,
                          runtime_env=args.runtime_env, mouse_helper=args.mouse_helper)
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if report["verdict"] == "READY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
