"""lap299 work probe — statically re-derive the original save/load layout.

The probe reads the SHA-pinned original executable and the read-only sprite
fixture.  It does not run the game, Wine, Xvfb, the runtime harness, or any
Stage B path, and it never reads a capture as layout evidence.

The layout constants are extracted from the original ``FUN_004D60B0``
disassembly.  The screen globals that feed the center formula are enumerated
from the original ``.text``; both reachable static coordinate candidates are
reported with their preconditions.  They are not observed click behavior.
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
SCREEN_W_GLOBAL = 0xE5BF1C
SCREEN_H_GLOBAL = 0xE5BF20
GRAPHICS_OBJECT = 0xE5BF18
ORIGIN_X_GLOBAL = 0x1088B5C
ORIGIN_Y_GLOBAL = 0x1088B5E
SLOT_Y_OFFSETS = (-0x1A, 0x08, 0x2A, 0x4C, 0x6E, 0x90, 0xB2)
SLOT_X_OFFSET = 0x14
SLOT_W = 0x118
SLOT_H = 0x18
BUTTON_OFFSETS = {"ok_call_point": (0x24, 0xD7), "cancel_call_point": (0xBA, 0xD7)}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def contains_all(text: str, needles: tuple[str, ...], failures: list[str], label: str) -> None:
    for needle in needles:
        if needle not in text:
            failures.append(f"{label} missing disassembly anchor: {needle}")


def overlaps(left: tuple[int, int, int, int], right: tuple[int, int, int, int]) -> bool:
    return not (
        left[2] <= right[0]
        or right[2] <= left[0]
        or left[3] <= right[1]
        or right[3] <= left[1]
    )


def layout_for(screen: tuple[int, int], dialog: tuple[int, int]) -> dict[str, object]:
    origin_x = (screen[0] - dialog[0]) // 2
    origin_y = (screen[1] - dialog[1]) // 2
    left = origin_x + SLOT_X_OFFSET
    slots = [
        [left, origin_y + offset, left + SLOT_W, origin_y + offset + SLOT_H]
        for offset in SLOT_Y_OFFSETS
    ]
    return {
        "screen": list(screen),
        "title_origin": [origin_x, origin_y],
        "slot_record_start_this_offset": "0x408",
        "slot_record_stride": 16,
        "slot_count": len(slots),
        "slot_rects_xyxy": slots,
        "button_call_points_xy": {
            name: [origin_x + dx, origin_y + dy]
            for name, (dx, dy) in BUTTON_OFFSETS.items()
        },
    }


def screen_checks(
    layout: dict[str, object], screen: tuple[int, int]
) -> dict[str, bool]:
    slots = layout["slot_rects_xyxy"]
    buttons = layout["button_call_points_xy"]
    assert isinstance(slots, list)
    assert isinstance(buttons, dict)
    rects = [tuple(rect) for rect in slots]
    points = [tuple(point) for point in buttons.values()]
    return {
        "slot_rects_non_overlapping": not any(
            overlaps(left, right)
            for index, left in enumerate(rects)
            for right in rects[index + 1 :]
        ),
        "slot_rects_inside_screen": all(
            0 <= rect[0] < rect[2] <= screen[0]
            and 0 <= rect[1] < rect[3] <= screen[1]
            for rect in rects
        ),
        "buttons_inside_screen": all(
            0 <= point[0] < screen[0] and 0 <= point[1] < screen[1]
            for point in points
        ),
        "buttons_outside_slot_rects": all(
            not any(rect[0] <= point[0] < rect[2] and rect[1] <= point[1] < rect[3]
                    for rect in rects)
            for point in points
        ),
    }


def main() -> int:
    failures: list[str] = []
    report: dict[str, object] = {
        "probe": Path(__file__).name,
        "lap": 299,
        "capture_comparison": False,
        "execution": False,
    }

    if not EXE.is_file() or not SPRITE.is_file():
        failures.append("required read-only original or sprite fixture is missing")
        report["failures"] = failures
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1

    exe_sha = sha256(EXE)
    sprite_sha = sha256(SPRITE)
    report["sha256"] = {"original_exe": exe_sha, "sprite": sprite_sha}
    if exe_sha != EXPECTED_EXE_SHA:
        failures.append(f"original exe sha mismatch: {exe_sha}")
    if sprite_sha != EXPECTED_SPRITE_SHA:
        failures.append(f"sprite sha mismatch: {sprite_sha}")

    header = struct.unpack("<4I", SPRITE.read_bytes()[:16])
    report["sprite_header"] = {
        "first_four_u32": list(header),
        "interpretation": "frame_count,width,height,format_marker",
        "file_size": SPRITE.stat().st_size,
    }
    if header != (9, 320, 310, 1):
        failures.append(f"unexpected saveloadtitle.spr header: {header}")
    sprite_width, sprite_height = header[1], header[2]

    layout_text = disasm(0x4D60B0, 0x4D6570)
    mode_text = disasm(0x4D6930, 0x4D6A40)
    screen_text = disasm(0x4324B8, 0x4324CC)
    contains_all(
        layout_text,
        (
            "mov    WORD PTR [esi+0xf9c],0x7",
            "lea    ebx,[esi+0x408]",
            "mov    WORD PTR [esi+0xfa4],0x118",
            "mov    WORD PTR [esi+0xfa6],0x18",
            "sub    ecx,0x1a",
            "add    ecx,0x14",
            "add    edx,0x8",
            "add    eax,0x2a",
            "add    ecx,0x4c",
            "add    edx,0x6e",
            "add    eax,0x90",
            "add    ecx,0xb2",
            "add    eax,0xd7",
            "add    eax,0x24",
            "add    eax,0xba",
            "add    eax,0x18",
            "add    ecx,0x18",
        ),
        failures,
        "FUN_004D60B0",
    )
    contains_all(
        mode_text,
        (
            "cmp    ax,0x3ed",
            "cmp    ax,0x3eb",
            "call   0x4d60b0",
        ),
        failures,
        "save/load mode dispatch",
    )
    contains_all(
        screen_text,
        (
            "mov    DWORD PTR ds:0xe5bf1c,0x280",
            "mov    DWORD PTR ds:0xe5bf20,0x1e0",
        ),
        failures,
        "original logical-screen initialization",
    )
    whole_text = disasm(0x401000, 0x4E4AE5)
    writer_pattern = re.compile(
        r"^  ([0-9a-f]{6}):\t[0-9a-f ]+\t"
        r"(mov +DWORD PTR ds:0x(?:e5bf1c|e5bf20),.+)$",
        re.MULTILINE,
    )
    screen_writers = [
        {"address": f"0x{address}", "instruction": instruction.strip()}
        for address, instruction in writer_pattern.findall(whole_text)
    ]
    expected_writer_text = {
        "0x431b79": "mov    DWORD PTR ds:0xe5bf1c,ebp",
        "0x431b7f": "mov    DWORD PTR ds:0xe5bf20,edi",
        "0x4324b8": "mov    DWORD PTR ds:0xe5bf1c,0x280",
        "0x4324c2": "mov    DWORD PTR ds:0xe5bf20,0x1e0",
    }
    actual_writer_text = {entry["address"].lower(): entry["instruction"]
                          for entry in screen_writers}
    for address, instruction in expected_writer_text.items():
        if actual_writer_text.get(address) != instruction:
            failures.append(f"screen global writer mismatch at {address}: "
                            f"{actual_writer_text.get(address)!r}")
    if len(screen_writers) != len(expected_writer_text):
        failures.append(f"unexpected screen global writer count: {screen_writers}")

    mode_text = disasm(0x4644A0, 0x464570)
    mode_pairs = {
        "320x200": ("[esi+0x4],0x140", "[esi+0x8],0xc8"),
        "640x480": ("[esi+0x4],0x280", "[esi+0x8],0x1e0"),
        "800x600": ("[esi+0x4],0x320", "[esi+0x8],0x258"),
        "1024x768": ("[esi+0x4],0x400", "[esi+0x8],0x300"),
        "1280x1024": ("[esi+0x4],0x500", "[esi+0x8],0x400"),
    }
    modes_present = {
        name: all(part in mode_text for part in parts)
        for name, parts in mode_pairs.items()
    }
    for name, present in modes_present.items():
        if not present:
            failures.append(f"display mode {name} absent from mode table")

    reset_text = disasm(0x4324B0, 0x4324D0)
    reset_640 = (
        "mov    DWORD PTR ds:0xe5bf1c,0x280" in reset_text
        and "mov    DWORD PTR ds:0xe5bf20,0x1e0" in reset_text
    )
    if not reset_640:
        failures.append("expected the 640x480 post-map screen reset")

    report["disassembly"] = {
        "layout_range": "0x004D60B0..0x004D656F",
        "mode_range": "0x004D6930..0x004D6A3F",
        "layout_constants_source": "original EXE objdump; no Plan C values used",
        "screen_globals_read": {
            "screen_width": f"ds:0x{SCREEN_W_GLOBAL:x}",
            "screen_height": f"ds:0x{SCREEN_H_GLOBAL:x}",
            "graphics_object": f"ds:0x{GRAPHICS_OBJECT:x} (+4/+8)",
            "origin_x": f"ds:0x{ORIGIN_X_GLOBAL:x}",
            "origin_y": f"ds:0x{ORIGIN_Y_GLOBAL:x}",
        },
        "screen_global_writers": screen_writers,
        "display_mode_table": {
            "function": "0x004644A0",
            "modes_present": modes_present,
        },
        "post_map_reset": {
            "site": "0x004324B8 (success exit of FUN_00431AB0)",
            "sets_640x480": reset_640,
        },
    }

    dialog_size = (sprite_width, sprite_height)
    candidate_specs = {
        "A_title_screen_entry_800x600": {
            "screen": (800, 600),
            "precondition": (
                "FUN_00431AB0 has not run since display init; the mode value at "
                "click time is 800x600"
            ),
        },
        "B_in_game_entry_after_map_surface_640x480": {
            "screen": (640, 480),
            "precondition": (
                "FUN_00431AB0 ran before the click; its success exit restored "
                "the screen globals to 640x480"
            ),
        },
    }
    candidates: dict[str, object] = {}
    for name, spec in candidate_specs.items():
        screen = spec["screen"]
        assert isinstance(screen, tuple)
        candidate = layout_for(screen, dialog_size)
        candidate["precondition"] = spec["precondition"]
        candidate["checks"] = screen_checks(candidate, screen)
        candidates[name] = candidate
        if not all(candidate["checks"].values()):
            failures.append(f"candidate {name} failed geometry checks: {candidate['checks']}")
    report["candidates"] = candidates
    report["limitations"] = [
        "which candidate holds at click time is not decided offline; it needs the "
        "observed values of ds:0xE5BF1C/ds:0xE5BF20, which requires a run",
        "button callsites yield points, not button hitbox extents",
        "no original capture was used for coordinate confirmation",
        "slot selection and post-click load transition remain UNKNOWN",
    ]
    report["failures"] = failures
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
