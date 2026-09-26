"""lap300 middle review probe — independently re-derive the lap299 save/load layout.

Offline and read-only.  It reads the SHA-pinned original executable plus the two
read-only dialog sprites, and it re-runs the lap299 work probe to check byte
determinism.  It never runs the game, Wine, Xvfb, the runtime harness, or any
Stage B path, and it never reads a capture as layout evidence.

Unlike the lap299 probe this one does not assume the logical screen size.  It
enumerates every writer of the two globals that ``FUN_004D60B0`` actually reads
and emits one labelled candidate coordinate set per reachable screen value.
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
ASSETS = REPO.parent / "Syw2plus" / "yfnt"
TITLE_SPR = ASSETS / "saveloadtitle.spr"
BAR_SPR = ASSETS / "SaveLoadBar.spr"
LAP299 = Path(__file__).with_name("20260912_lap299_work_save_load_layout_probe.py")

EXPECTED_EXE_SHA = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"
EXPECTED_TITLE_SHA = "7d154cdbf37dbea78c162ada870e656a039a224c5aa63ee52d86d8123c08a5c5"
EXPECTED_LAP299_REPORT_SHA = (
    "8e735a9a7f7b4ddbd1ab249039c568b42b16af8b248f47e64681d05476d2bb0b"
)

# Screen globals read by the dialog's centering code.  They are fields +4/+8 of
# the graphics object whose "this" pointer the same function passes as 0xE5BF18.
SCREEN_W_GLOBAL = 0xE5BF1C
SCREEN_H_GLOBAL = 0xE5BF20
GRAPHICS_OBJECT = 0xE5BF18
# Centred dialog origin the function computes and then re-reads for every slot.
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
        ["objdump", "-d", "-Mintel", "-j", ".text",
         f"--start-address={start:#x}", f"--stop-address={stop:#x}", str(EXE)],
        check=True, capture_output=True, text=True,
    ).stdout


def spr_header(path: Path) -> tuple[int, int, int, int]:
    return struct.unpack("<4I", path.read_bytes()[:16])  # type: ignore[return-value]


def layout_for(screen: tuple[int, int], dialog: tuple[int, int]) -> dict[str, object]:
    origin_x = (screen[0] - dialog[0]) // 2
    origin_y = (screen[1] - dialog[1]) // 2
    left = origin_x + SLOT_X_OFFSET
    slots = [[left, origin_y + dy, left + SLOT_W, origin_y + dy + SLOT_H]
             for dy in SLOT_Y_OFFSETS]
    inside = all(0 <= r[0] < r[2] <= screen[0] and 0 <= r[1] < r[3] <= screen[1]
                 for r in slots)
    return {
        "screen": list(screen),
        "title_origin": [origin_x, origin_y],
        "slot_rects_xyxy": slots,
        "button_call_points_xy": {
            name: [origin_x + dx, origin_y + dy]
            for name, (dx, dy) in BUTTON_OFFSETS.items()
        },
        "all_slots_inside_screen": inside,
    }


def main() -> int:
    failures: list[str] = []
    report: dict[str, object] = {
        "probe": Path(__file__).name, "lap": 300, "role": "middle-review",
        "capture_comparison": False, "execution": False,
    }

    for path in (EXE, TITLE_SPR, BAR_SPR, LAP299):
        if not path.is_file():
            failures.append(f"required read-only input missing: {path}")
    if failures:
        report["failures"] = failures
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1

    shas = {"original_exe": sha256(EXE), "saveloadtitle_spr": sha256(TITLE_SPR),
            "saveloadbar_spr": sha256(BAR_SPR), "lap299_probe": sha256(LAP299)}
    report["sha256"] = shas
    if shas["original_exe"] != EXPECTED_EXE_SHA:
        failures.append(f"original exe sha mismatch: {shas['original_exe']}")
    if shas["saveloadtitle_spr"] != EXPECTED_TITLE_SHA:
        failures.append(f"saveloadtitle.spr sha mismatch: {shas['saveloadtitle_spr']}")

    # (1) lap299 determinism: the work probe must reproduce its recorded report.
    run = subprocess.run(["python3", str(LAP299)], capture_output=True, text=True)
    lap299_sha = hashlib.sha256(run.stdout.encode()).hexdigest()
    report["lap299_rerun"] = {"exit": run.returncode, "stdout_sha256": lap299_sha,
                              "matches_record": lap299_sha == EXPECTED_LAP299_REPORT_SHA}
    if run.returncode != 0 or lap299_sha != EXPECTED_LAP299_REPORT_SHA:
        failures.append(f"lap299 probe is not reproducible: exit={run.returncode} "
                        f"sha={lap299_sha}")

    # (2) The dialog sprites are named by the loader, not assumed.
    data = EXE.read_bytes()
    for needle in (b"yfnt\\saveloadtitle.spr\x00", b"yfnt\\saveloadbar.spr\x00"):
        if needle not in data:
            failures.append(f"dialog sprite path string absent: {needle!r}")
    title_hdr, bar_hdr = spr_header(TITLE_SPR), spr_header(BAR_SPR)
    report["sprite_headers"] = {"saveloadtitle": list(title_hdr),
                                "saveloadbar": list(bar_hdr)}
    if title_hdr[0:1] + title_hdr[3:] != (9, 1) or bar_hdr[0:1] + bar_hdr[3:] != (9, 1):
        failures.append(f"unexpected sprite header shape: {title_hdr} {bar_hdr}")
    # Independent corroboration of the hardcoded slot rect: the selection bar
    # sprite is exactly 0x118 x 0x18.
    if (bar_hdr[1], bar_hdr[2]) != (SLOT_W, SLOT_H):
        failures.append(f"SaveLoadBar.spr {bar_hdr[1]}x{bar_hdr[2]} does not match the "
                        f"hardcoded slot rect {SLOT_W}x{SLOT_H}")
    report["slot_rect_corroboration"] = {
        "hardcoded_rect": [SLOT_W, SLOT_H],
        "saveloadbar_spr_size": [bar_hdr[1], bar_hdr[2]],
        "agree": (bar_hdr[1], bar_hdr[2]) == (SLOT_W, SLOT_H),
    }

    # (3) Every layout constant, including the slot-0 offset the lap299 anchors miss.
    layout_text = disasm(0x4D60B0, 0x4D6570)
    anchors = (
        "lea    ebx,[esi+0x408]",
        "mov    WORD PTR [esi+0xf9c],0x7",
        "mov    WORD PTR [esi+0xfa4],0x118",
        "mov    WORD PTR [esi+0xfa6],0x18",
        "sub    ecx,0x1a",          # slot 0 y offset; absent from the lap299 anchors
        "add    edx,0x8", "add    eax,0x2a", "add    ecx,0x4c",
        "add    edx,0x6e", "add    eax,0x90", "add    ecx,0xb2",
        "add    ecx,0x14", "add    edx,0x14", "add    eax,0x14",
        "add    eax,0x24", "add    eax,0xba", "add    eax,0xd7",
        f"mov    WORD PTR ds:0x{ORIGIN_X_GLOBAL:x},cx",
        f"mov    WORD PTR ds:0x{ORIGIN_Y_GLOBAL:x},di",
    )
    for needle in anchors:
        if needle not in layout_text:
            failures.append(f"FUN_004D60B0 missing disassembly anchor: {needle}")
    if "add    eax,0x18" not in layout_text or "add    ecx,0x18" not in layout_text:
        failures.append("FUN_004D60B0 missing the slot height (+0x18) anchors")
    report["lap299_anchor_gap"] = {
        "constant": "slot0 y offset -0x1A",
        "instruction": "sub    ecx,0x1a @ 0x004D6358",
        "covered_by_lap299_anchors": "sub    ecx,0x1a" in LAP299.read_text(encoding="utf-8"),
    }

    # (4) Enumerate every writer of the screen globals across the whole .text.
    whole = disasm(0x401000, 0x4E4AE5)
    writers: list[dict[str, str]] = []
    pattern = re.compile(
        r"^  ([0-9a-f]{6}):\t[0-9a-f ]+\t(mov +DWORD PTR ds:0x(?:e5bf1c|e5bf20),.+)$",
        re.MULTILINE)
    for addr, text in pattern.findall(whole):
        writers.append({"address": f"0x{addr}", "instruction": text.strip()})
    report["screen_global_writers"] = writers
    if len(writers) < 4:
        failures.append(f"expected both globals written from >=2 sites, got {writers}")

    # The display-mode table proves 800x600 is a mode, not the only value.
    mode_text = disasm(0x4644A0, 0x464570)
    mode_pairs = {"320x200": ("[esi+0x4],0x140", "[esi+0x8],0xc8"),
                  "640x480": ("[esi+0x4],0x280", "[esi+0x8],0x1e0"),
                  "800x600": ("[esi+0x4],0x320", "[esi+0x8],0x258"),
                  "1024x768": ("[esi+0x4],0x400", "[esi+0x8],0x300"),
                  "1280x1024": ("[esi+0x4],0x500", "[esi+0x8],0x400")}
    modes = {name: all(part in mode_text for part in parts)
             for name, parts in mode_pairs.items()}
    report["display_mode_table"] = {"function": "0x004644A0", "modes_present": modes}
    for name, present in modes.items():
        if not present:
            failures.append(f"display mode {name} absent from FUN_004644A0 table")

    # The map-surface function's success exit overwrites the globals with 640x480.
    reset_text = disasm(0x4324B0, 0x4324D0)
    reset_640 = ("mov    DWORD PTR ds:0xe5bf1c,0x280" in reset_text
                 and "mov    DWORD PTR ds:0xe5bf20,0x1e0" in reset_text)
    report["post_map_reset"] = {
        "site": "0x004324B8 (success exit of FUN_00431AB0)",
        "sets_640x480": reset_640,
        "note": "no writer restores the display mode afterwards; FUN_004644A0 is the "
                "only other writer and is called from display init only",
    }
    if not reset_640:
        failures.append("expected the 640x480 store at 0x004324B8")

    # (5) One labelled candidate per reachable screen value.  Not a single answer.
    dialog = (title_hdr[1], title_hdr[2])
    report["candidates"] = {
        "A_title_screen_entry_800x600": layout_for((800, 600), dialog),
        "B_in_game_entry_after_map_surface_640x480": layout_for((640, 480), dialog),
    }
    report["candidates"]["A_title_screen_entry_800x600"]["precondition"] = (
        "FUN_00431AB0 has not run since display init; matches the lap298 800x600 title "
        "capture and reproduces the lap299 numbers")
    report["candidates"]["B_in_game_entry_after_map_surface_640x480"]["precondition"] = (
        "FUN_00431AB0 ran; corroborated by this function's own overwritten default "
        "table, whose x1=0xB4=180 equals origin_x(160)+0x14 for a 640-wide screen")

    report["limitations"] = [
        "which candidate holds at click time is not decided offline; it needs the "
        "observed value of 0xE5BF1C/0xE5BF20, which requires a run",
        "button callsites yield points, not hitbox extents",
        "slot selection and post-click load transition remain UNKNOWN",
    ]
    report["failures"] = failures
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
