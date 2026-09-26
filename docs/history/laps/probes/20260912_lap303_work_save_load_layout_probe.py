"""lap303 work probe — repair the lap302 writer/candidate handoff.

This is a static probe of the read-only original executable and sprite fixture.
It does not run the game, Wine, Xvfb, the runtime harness, or Stage B, and it
does not read captures as layout evidence.  It is a new lap-named source so
the repaired probe does not overwrite earlier provenance.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess


REPO = Path(__file__).resolve().parents[4]
EXE = REPO / "Syw2plus" / "syw2plus_original.exe"
SPRITE = REPO.parent / "Syw2plus" / "yfnt" / "saveloadtitle.spr"
EXPECTED_EXE_SHA = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"
EXPECTED_SPRITE_SHA = "7d154cdbf37dbea78c162ada870e656a039a224c5aa63ee52d86d8123c08a5c5"

GRAPHICS_OBJECT = 0xE5BF18
SCREEN_W_GLOBAL = 0xE5BF1C
SCREEN_H_GLOBAL = 0xE5BF20
ORIGIN_X_GLOBAL = 0x1088B5C
ORIGIN_Y_GLOBAL = 0x1088B5E

CENTRE_FORMULA_ANCHORS = {
    0x4D625B: "mov    eax,DWORD PTR [esi+0x10f0]",
    0x4D6310: "mov    edi,eax",
    0x4D6312: "mov    eax,ds:0xe5bf1c",
    0x4D631C: "mov    eax,ds:0xe5bf20",
    0x4D6322: "sar    edi,1",
    0x4D6324: "sar    ecx,1",
    0x4D6326: "sub    ecx,edi",
    0x4D632A: "mov    WORD PTR ds:0x1088b5c,cx",
    0x4D6333: "mov    eax,DWORD PTR [esi+0x10f4]",
    0x4D633C: "sar    edi,1",
    0x4D633E: "sar    eax,1",
    0x4D6340: "sub    edi,eax",
    0x4D6345: "add    eax,0x14",
    0x4D6348: "mov    WORD PTR ds:0x1088b5e,di",
    0x4D6351: "movsx  ecx,WORD PTR ds:0x1088b5e",
    0x4D6358: "sub    ecx,0x1a",
    0x4D635B: "mov    DWORD PTR [esi+0x40c],ecx",
    0x4D6363: "add    edx,0x118",
    0x4D6371: "add    eax,0x18",
}

INDIRECT_CHAIN_ANCHORS = {
    0x423D52: "mov    ecx,0xe5bf18",
    0x423D63: "call   0x464360",
    0x4643BE: "mov    ecx,esi",
    0x4643C0: "call   0x4644a0",
    0x4644AD: "mov    esi,ecx",
    0x4644B5: "mov    DWORD PTR [esi],eax",
    0x4644C1: "jmp    DWORD PTR [eax*4+0x464b68]",
}

# Each entry is the pair of writes emitted by one reachable mode-table branch.
MODE_BRANCH_WRITES = {
    0x4644C8: {
        "resolution": (320, 200),
        "writes": {
            0x4644C8: "mov    DWORD PTR [esi+0x4],0x140",
            0x4644CF: "mov    DWORD PTR [esi+0x8],0xc8",
        },
    },
    0x4644DB: {
        "resolution": (640, 480),
        "writes": {
            0x4644DB: "mov    DWORD PTR [esi+0x4],0x280",
            0x4644E2: "mov    DWORD PTR [esi+0x8],0x1e0",
        },
    },
    0x4644EB: {
        "resolution": (640, 480),
        "writes": {
            0x4644EB: "mov    DWORD PTR [esi+0x4],0x280",
            0x4644F2: "mov    DWORD PTR [esi+0x8],0x1e0",
        },
    },
    0x464502: {
        "resolution": (800, 600),
        "writes": {
            0x464502: "mov    DWORD PTR [esi+0x4],0x320",
            0x464509: "mov    DWORD PTR [esi+0x8],0x258",
        },
    },
    0x464512: {
        "resolution": (800, 600),
        "writes": {
            0x464512: "mov    DWORD PTR [esi+0x4],0x320",
            0x464519: "mov    DWORD PTR [esi+0x8],0x258",
        },
    },
    0x464529: {
        "resolution": (1024, 768),
        "writes": {
            0x464529: "mov    DWORD PTR [esi+0x4],0x400",
            0x464530: "mov    DWORD PTR [esi+0x8],0x300",
        },
    },
    0x464539: {
        "resolution": (1024, 768),
        "writes": {
            0x464539: "mov    DWORD PTR [esi+0x4],0x400",
            0x464540: "mov    DWORD PTR [esi+0x8],0x300",
        },
    },
    0x464550: {
        "resolution": (1280, 1024),
        "writes": {
            0x464550: "mov    DWORD PTR [esi+0x4],0x500",
            0x464557: "mov    DWORD PTR [esi+0x8],0x400",
        },
    },
}

DIRECT_WRITERS = {
    0x431B79: "mov    DWORD PTR ds:0xe5bf1c,ebp",
    0x431B7F: "mov    DWORD PTR ds:0xe5bf20,edi",
    0x4324B8: "mov    DWORD PTR ds:0xe5bf1c,0x280",
    0x4324C2: "mov    DWORD PTR ds:0xe5bf20,0x1e0",
}

SLOT_Y_OFFSETS = (-0x1A, 0x08, 0x2A, 0x4C, 0x6E, 0x90, 0xB2)
SLOT_X_OFFSET = 0x14
SLOT_W = 0x118
SLOT_H = 0x18
INSN_RE = re.compile(
    r"^\s+([0-9a-f]{6}):\t(?:[0-9a-f]{2} )+\s*\t(.+?)\s*$",
    re.MULTILINE,
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def disasm(start: int, stop: int) -> str:
    return subprocess.run(
        [
            "objdump",
            "-d",
            "-Mintel",
            "-j",
            ".text",
            f"--start-address={start:#x}",
            f"--stop-address={stop:#x}",
            str(EXE),
        ],
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def instructions(text: str) -> dict[int, str]:
    return {int(address, 16): instruction for address, instruction in INSN_RE.findall(text)}


def check_anchors(
    found: dict[int, str], expected: dict[int, str], label: str, failures: list[str]
) -> dict[str, str]:
    resolved: dict[str, str] = {}
    for address, instruction in expected.items():
        actual = found.get(address)
        resolved[f"0x{address:x}"] = actual or ""
        if actual != instruction:
            failures.append(
                f"{label}: 0x{address:x} expected {instruction!r}, found {actual!r}"
            )
    return resolved


def halve_toward_zero(value: int) -> int:
    return -((-value) // 2) if value < 0 else value // 2


def origin_from_binary(screen: tuple[int, int], dialog: tuple[int, int]) -> tuple[int, int]:
    """Reproduce ``sar(screen,1) - sar(dialog,1)`` from the command stream."""
    return (
        halve_toward_zero(screen[0]) - halve_toward_zero(dialog[0]),
        halve_toward_zero(screen[1]) - halve_toward_zero(dialog[1]),
    )


def slots_for(origin: tuple[int, int]) -> list[tuple[int, int, int, int]]:
    left = origin[0] + SLOT_X_OFFSET
    return [
        (left, origin[1] + offset, left + SLOT_W, origin[1] + offset + SLOT_H)
        for offset in SLOT_Y_OFFSETS
    ]


def geometry_for(screen: tuple[int, int], dialog: tuple[int, int]) -> dict[str, object]:
    binary_origin = origin_from_binary(screen, dialog)
    arithmetic_origin = ((screen[0] - dialog[0]) // 2, (screen[1] - dialog[1]) // 2)
    rects = slots_for(binary_origin)
    inside = all(
        0 <= rect[0] < rect[2] <= screen[0]
        and 0 <= rect[1] < rect[3] <= screen[1]
        for rect in rects
    )
    return {
        "screen": list(screen),
        "dialog": list(dialog),
        "origin_binary_formula": list(binary_origin),
        "origin_screen_minus_dialog_divided": list(arithmetic_origin),
        "formulas_agree": binary_origin == arithmetic_origin,
        "slot_count": len(rects),
        "slot_record_start_this_offset": "0x408",
        "slot_record_stride": 16,
        "slot0_xyxy": list(rects[0]),
        "slot6_xyxy": list(rects[-1]),
        "slot_rects_inside_screen": inside,
    }


def main() -> int:
    failures: list[str] = []
    report: dict[str, object] = {
        "probe": Path(__file__).name,
        "lap": 303,
        "role": "work (static implementation); no game code, no execution",
        "capture_comparison": False,
        "execution": False,
    }
    if not EXE.is_file() or not SPRITE.is_file():
        failures.append("required read-only original or sprite fixture is missing")
        report["failures"] = failures
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1

    exe_bytes = EXE.read_bytes()
    sprite_bytes = SPRITE.read_bytes()
    exe_sha = sha256_bytes(exe_bytes)
    sprite_sha = sha256_bytes(sprite_bytes)
    report["sha256"] = {"original_exe": exe_sha, "sprite": sprite_sha}
    if exe_sha != EXPECTED_EXE_SHA:
        failures.append(f"original exe sha mismatch: {exe_sha}")
    if sprite_sha != EXPECTED_SPRITE_SHA:
        failures.append(f"sprite sha mismatch: {sprite_sha}")

    header = struct.unpack_from("<4I", sprite_bytes, 0)
    report["sprite_header"] = {
        "first_four_u32": list(header),
        "interpretation": "frame_count,width,height,format_marker",
        "file_size": len(sprite_bytes),
    }
    if header != (9, 320, 310, 1):
        failures.append(f"unexpected saveloadtitle.spr header: {header}")
    dialog = (header[1], header[2])

    whole = disasm(0x401000, 0x4E4AE5)
    found = instructions(whole)
    check_anchors(found, CENTRE_FORMULA_ANCHORS, "centre formula", failures)
    check_anchors(found, INDIRECT_CHAIN_ANCHORS, "indirect chain", failures)

    layout_text = disasm(0x4D60B0, 0x4D6570)
    for anchor in (
        "mov    WORD PTR [esi+0xf9c],0x7",
        "lea    ebx,[esi+0x408]",
        "mov    WORD PTR [esi+0xfa4],0x118",
        "mov    WORD PTR [esi+0xfa6],0x18",
        "sub    ecx,0x1a",
        "add    ecx,0x14",
        "add    eax,0x18",
        "add    ecx,0x18",
    ):
        if anchor not in layout_text:
            failures.append(f"FUN_004D60B0 missing disassembly anchor: {anchor}")

    direct_pattern = re.compile(
        r"^\s+([0-9a-f]{6}):\t(?:[0-9a-f]{2} )+\s*\t"
        r"(mov +(?:DWORD|WORD|BYTE) PTR ds:0x(?:e5bf1c|e5bf20),.+?)\s*$",
        re.MULTILINE,
    )
    direct = {int(address, 16): instruction for address, instruction in direct_pattern.findall(whole)}
    if direct != DIRECT_WRITERS:
        failures.append(f"direct absolute writer set changed: {sorted(map(hex, direct))}")

    indirect: dict[int, str] = {}
    mode_branches: dict[str, object] = {}
    for branch, spec in MODE_BRANCH_WRITES.items():
        branch_writes: dict[str, str] = {}
        for address, expected in spec["writes"].items():
            actual = found.get(address)
            branch_writes[f"0x{address:x}"] = actual or ""
            if actual != expected:
                failures.append(
                    f"mode writer 0x{address:x} expected {expected!r}, found {actual!r}"
                )
            indirect[address] = actual or ""
        mode_branches[f"0x{branch:x}"] = {
            "resolution": list(spec["resolution"]),
            "writes": branch_writes,
        }

    report["disassembly"] = {
        "layout_range": "0x004D60B0..0x004D656F",
        "layout_constants_source": "original EXE objdump; no Plan C values used",
        "screen_globals_read": {
            "screen_width": f"ds:0x{SCREEN_W_GLOBAL:x}",
            "screen_height": f"ds:0x{SCREEN_H_GLOBAL:x}",
            "graphics_object": f"ds:0x{GRAPHICS_OBJECT:x} (+4/+8)",
            "origin_x": f"ds:0x{ORIGIN_X_GLOBAL:x}",
            "origin_y": f"ds:0x{ORIGIN_Y_GLOBAL:x}",
        },
        "direct_absolute_writers": {
            f"0x{address:x}": instruction
            for address, instruction in sorted(direct.items())
        },
        "indirect_this_relative_writers": {
            f"0x{address:x}": instruction
            for address, instruction in sorted(indirect.items())
        },
        "mode_table": {
            "function": "0x004644A0",
            "this_value": "0xE5BF18",
            "mode_branches": mode_branches,
        },
    }
    report["writer_scope"] = {
        "direct_absolute_count": len(direct),
        "indirect_this_relative_count": len(indirect),
        "minimum_total_writer_count": len(direct) + len(indirect),
        "this_relative_fields": {
            "[this+0x4]": "ds:0xE5BF1C when this=0xE5BF18",
            "[this+0x8]": "ds:0xE5BF20 when this=0xE5BF18",
        },
        "absolute_only_count_gate": {
            "previous_expected_count": 4,
            "indirect_path": "fail-open",
            "reason": "absolute-address regex cannot observe [this+0x4]/[this+0x8]",
        },
    }

    reachable = sorted({spec["resolution"] for spec in MODE_BRANCH_WRITES.values()})
    geometries = {
        f"{screen[0]}x{screen[1]}": geometry_for(screen, dialog)
        for screen in reachable
    }
    for name, geometry in geometries.items():
        if not geometry["formulas_agree"]:
            failures.append(f"centre formula mismatch at {name}")
    report["candidate_scope"] = {
        "candidate_count": 7,
        "fixed_mode_resolutions": [list(screen) for screen in reachable],
        "additional_dynamic_writers": [
            {
                "name": "post_map_reset_640x480",
                "writer_sites": ["0x4324B8", "0x4324C2"],
                "precondition": "successful FUN_00431AB0 exit executes the unconditional 640x480 reset",
            },
            {
                "name": "map_surface_dynamic",
                "writer_sites": ["0x431B79", "0x431B7F"],
                "precondition": "FUN_00431AB0 map-surface path writes runtime ebp/edi values",
                "screen": "runtime values; not statically reduced to one resolution",
            },
        ],
        "candidate_exclusivity": "REJECTED offline; runtime mode/global observation is still required",
    }
    report["geometry_all_fixed_modes"] = geometries
    report["modes_where_dialog_leaves_screen"] = [
        name for name, geometry in geometries.items() if not geometry["slot_rects_inside_screen"]
    ]

    report["provenance"] = {
        "lap": 303,
        "probe_source": Path(__file__).name,
        "new_source_instead_of_overwrite": True,
        "historical_lap299_and_lap301_logs_modified": False,
        "future_artifact_sha_pinned": False,
        "determinism_assertion_policy": (
            "compare two fresh executions of this probe in the same session; "
            "do not assert a future lap report SHA"
        ),
    }
    report["limitations"] = [
        "static only: the live resolution when FUN_004D60B0 builds the dialog is not observed",
        "map-surface ebp/edi values and the mode argument source remain runtime/undetermined",
        "button callsites yield points, not hitbox extents; slot selection and post-click load remain UNKNOWN",
        "no capture, game, Wine/Xvfb, Stage B, runtime budget, or product G1 PASS",
    ]
    report["failures"] = failures
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
