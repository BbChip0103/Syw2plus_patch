"""lap298 middle — can the load-path UI be established without running the game?

`G1_ASTRA_RESEARCH_GATE_LAP297.md` asks the middle tier to judge, from existing
local captures only, whether the load research envelope's UI inputs are
derivable or must stay UNKNOWN.  lap284 §2/§5 left the load menu and its click
sequence as the reason fixture selection and the execution envelope were both
REJECTed.  This probe answers three separate questions:

  1. Is the original title menu deterministic across the harness runs we already
     have, and where exactly are its buttons in the *click* coordinate frame?
     `_capture_screenshot` crops with ``scrot -a content_crop`` and every click
     is ``content_crop + (x, y)``, so a capture pixel and a click coordinate are
     the same number.  If the grid is regular and the harness's own verified
     random-game click lands in exactly one cell, the neighbouring cells are
     addressable by the same mechanism.
  2. Does the harness contain any load path today?  lap284 claimed zero.  This
     re-measures instead of citing.
  3. The shared capture directory contains an 800x600 `load_screen` PNG that
     looks like the answer to (1)'s follow-up dialog.  It is not: its strings
     come from the Plan C reimplementation's own UI module.  This probe pins
     that provenance so a later session cannot mistake it for original evidence.

Read-only: the original executable, the game data tree, the two implementation
modules, the shared capture directory and the Plan C reference tree are only
ever read.  No game, no Wine, no Xvfb, no Stage B, no runtime budget, no write
to any original or reference tree.

Usage: .venv/bin/python docs/history/laps/probes/20260912_lap298_middle_title_load_ui_probe.py
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import numpy as np
from PIL import Image

REPO = Path(__file__).resolve().parents[4]
SHARED = REPO.parent / "temp"
ENV_MOD = REPO / "tools" / "runtime_env.py"
DRIVER = REPO / "patches" / "population" / "runtime_driver.py"
EXE = REPO / "Syw2plus" / "syw2plus_original.exe"
SOURCE_TREE = REPO.parent / "Syw2plus_re" / "Syw2plus"
PLAN_C_UI = REPO.parent / "Syw2plus_re" / "plan_c" / "src" / "ui" / "save_load_screen.cpp"
PLAN_C_PNG = SHARED / "20260910_032210_d1app2r3_21_load_screen.png"

EXPECTED_SHA = {
    "original_exe": "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac",
    "runtime_env": "dd2ad0439111d6b1e098d0ea771db172847dfa42f04ed085c4567f2ac8500190",
    "runtime_driver": "ae4ff9393247ce31eab7c953b040f7d3c5aa8b0386af025046382c7d4e4291b5",
    "save000": "1c703551888f5c85a1fa2fb7b43d28309eb0b88e4bbf6e859f1a98b629e719da",
    "save006": "616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064",
}

# The harness's only title-menu click.  runtime_env.py:3416 issues it and
# runtime_env.py:606 names it "random-game".  Both are asserted below.
HARNESS_CLICK = (184, 560)
BUTTON_SIZE_RANGE = (90, 110, 30, 42)  # min_w, max_w, min_h, max_h
MENU_HALF_WIDTH = 500  # buttons live left of this; the rest is character art


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bands(vec: np.ndarray, threshold: int) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    start: int | None = None
    for index, value in enumerate(vec):
        if value > threshold and start is None:
            start = index
        elif value <= threshold and start is not None:
            out.append((start, index - 1))
            start = None
    if start is not None:
        out.append((start, len(vec) - 1))
    return out


def title_buttons(path: Path, failures: list[str]) -> list[dict[str, object]]:
    """Locate the title menu's button grid in the click coordinate frame."""
    image = Image.open(path).convert("RGB")
    if image.size != (800, 600):
        failures.append(f"title capture is not the 800x600 content crop: {image.size}")
        return []
    lit = (np.asarray(image).astype(int).sum(axis=2) / 3) > 25
    min_w, max_w, min_h, max_h = BUTTON_SIZE_RANGE
    buttons: list[dict[str, object]] = []
    # The right third of the title screen is lit character art with no buttons;
    # the row profile is taken over the menu half so the art cannot merge rows.
    row_profile = lit[:, :MENU_HALF_WIDTH].sum(axis=1)
    for row_index, (top, bottom) in enumerate(
        [band for band in bands(row_profile, 20) if min_h <= band[1] - band[0] + 1 <= max_h]
    ):
        columns = [
            band for band in bands(lit[top:bottom + 1, :MENU_HALF_WIDTH].sum(axis=0), 3)
            if min_w <= band[1] - band[0] + 1 <= max_w
        ]
        for col_index, (left, right) in enumerate(columns):
            buttons.append({
                "row": row_index + 1, "col": col_index + 1,
                "bbox": [left, top, right, bottom],
                "center": [(left + right) // 2, (top + bottom) // 2],
                "width": right - left + 1, "height": bottom - top + 1,
            })
    return buttons


def hit(buttons: list[dict[str, object]], point: tuple[int, int]) -> list[dict[str, object]]:
    x, y = point
    return [b for b in buttons if b["bbox"][0] <= x <= b["bbox"][2] and b["bbox"][1] <= y <= b["bbox"][3]]  # type: ignore[index]


def main() -> int:
    failures: list[str] = []
    report: dict[str, object] = {"probe": Path(__file__).name, "lap": 298}

    pinned = {
        "original_exe": EXE, "runtime_env": ENV_MOD, "runtime_driver": DRIVER,
        "save000": SOURCE_TREE / "save" / "save000.dat",
        "save006": SOURCE_TREE / "save" / "save006.dat",
    }
    measured: dict[str, str] = {}
    for name, path in pinned.items():
        if not path.is_file():
            failures.append(f"missing pinned artifact: {name} -> {path}")
            continue
        measured[name] = sha(path)
        if measured[name] != EXPECTED_SHA[name]:
            failures.append(f"{name} sha mismatch: {measured[name]}")
    report["pinned_sha256"] = measured

    # (1) determinism of the title screen across every harness capture we own.
    captures = sorted(SHARED.glob("*_title_before_menu_*.png"))
    capture_sha = {path.name: sha(path) for path in captures}
    distinct = sorted(set(capture_sha.values()))
    report["title_captures"] = {
        "count": len(captures), "distinct_sha256": distinct,
        "sha256": capture_sha,
    }
    if not captures:
        failures.append("no harness title captures found")
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1
    if len(distinct) != 1:
        failures.append(f"title screen is not byte-identical across runs: {len(distinct)} variants")

    buttons = title_buttons(captures[-1], failures)
    report["title_menu_grid"] = buttons
    if len(buttons) != 8:
        failures.append(f"title menu grid is not the expected 4x2: found {len(buttons)}")

    # The harness's verified click must land in exactly one cell, and that cell
    # is the one runtime_env.py calls the random-game entry.
    harness_hit = hit(buttons, HARNESS_CLICK)
    report["harness_click"] = {
        "point": list(HARNESS_CLICK),
        "cells_hit": [{"row": b["row"], "col": b["col"]} for b in harness_hit],
    }
    if len(harness_hit) != 1:
        failures.append(f"harness click {HARNESS_CLICK} hits {len(harness_hit)} cells, expected 1")
    elif (harness_hit[0]["row"], harness_hit[0]["col"]) != (2, 2):
        failures.append(f"harness click is not row2/col2: {harness_hit[0]['row']}/{harness_hit[0]['col']}")

    # Falsifying power: every cell centre must resolve to its own cell, and the
    # gap between two cells must resolve to none.  A detector that returned one
    # fat strip, or that swallowed the background, fails both.
    separation = {
        "centres_resolve_uniquely": all(
            len(hit(buttons, tuple(b["center"]))) == 1 for b in buttons  # type: ignore[arg-type]
        ),
        "gap_between_col1_and_col2_hits_nothing": (
            hit(buttons, (127, 560)) == [] if len(buttons) == 8 else None
        ),
        "point_above_grid_hits_nothing": hit(buttons, (184, 400)) == [],
    }
    report["detector_separation"] = separation
    for key, value in separation.items():
        if value is not True:
            failures.append(f"detector separation check failed: {key}={value}")

    # The load entry is the cell the harness has never clicked: row 1, col 3.
    load_cell = [b for b in buttons if (b["row"], b["col"]) == (1, 3)]
    report["load_cell_row1_col3"] = load_cell[0] if load_cell else None
    if not load_cell:
        failures.append("row1/col3 (load entry) was not located")

    # (2) does the harness have a load path at all?
    env_text = ENV_MOD.read_text()
    harness = {
        "save_word_occurrences": len(re.findall(r"save", env_text, re.IGNORECASE)),
        "ps35_occurrences": len(re.findall(r"\bps.{0,3}35\b", env_text, re.IGNORECASE)),
        "waited_player_states": sorted({int(m) for m in re.findall(r'item\.get\("ps"\) == (\d+)', env_text)}),
        "harness_click_literal_present": "content_crop[0] + 184, content_crop[1] + 560" in env_text,
        "random_game_label_present": "title random-game click (184,560)" in env_text,
        "content_crop_gate_800x600": 'raise RuntimeSafetyError("game content crop is not exactly 800x600")' in env_text,
        "capture_uses_crop": '"-a", ",".join(str(value) for value in crop)' in env_text,
    }
    report["harness_load_path"] = harness
    if harness["save_word_occurrences"] != 0:
        failures.append("runtime_env.py unexpectedly mentions save; lap284's zero-line claim is stale")
    for key in ("harness_click_literal_present", "random_game_label_present",
                "content_crop_gate_800x600", "capture_uses_crop"):
        if harness[key] is not True:
            failures.append(f"harness anchor missing: {key}")

    # (3) provenance of the 800x600 load dialog capture: Plan C, not the original.
    plan_c = {"png_exists": PLAN_C_PNG.is_file(), "ui_module_exists": PLAN_C_UI.is_file()}
    if plan_c["ui_module_exists"]:
        text = PLAN_C_UI.read_text(encoding="utf-8", errors="replace")
        plan_c["ui_module_sha256"] = sha(PLAN_C_UI)
        plan_c["emits_plnc_prefix"] = '"[PLNC] "' in text
        plan_c["emits_orig_prefix"] = '"[ORIG] "' in text
        plan_c["emits_empty_slot_label"] = "저장된 정보가 없습니다." in text
        plan_c["cites_original_function"] = "FUN_004D60B0" in text
        plan_c["load_mode_code"] = "0x3ED" if "0x3ED" in text else None
    if plan_c["png_exists"]:
        plan_c["png_sha256"] = sha(PLAN_C_PNG)
        plan_c["png_size"] = list(Image.open(PLAN_C_PNG).size)
    report["plan_c_load_dialog"] = plan_c
    report["plan_c_verdict"] = (
        "reject as original evidence: the dialog's slot labels are emitted by the "
        "Plan C reimplementation UI module, not by the original executable"
        if plan_c.get("emits_plnc_prefix") and plan_c.get("emits_empty_slot_label")
        else "provenance unresolved"
    )
    if plan_c["png_exists"] and not plan_c.get("emits_plnc_prefix"):
        failures.append("Plan C provenance could not be established for the load dialog capture")

    report["failures"] = failures
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
