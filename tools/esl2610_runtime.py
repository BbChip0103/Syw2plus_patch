#!/usr/bin/env python3
"""ESL 2610 lane for the isolated runtime harness.

The official 2610 folder holds only the files that changed against the full 2608
game folder, which in turn holds only what changed against ``[ESL]Syw2plus``
(the folder that ships ``_inmm.dll``, ``_inmmserv.exe``, ``ddraw.dll`` and DxWnd).
A runnable 2610 game is therefore ``[ESL]Syw2plus`` + 2608 overlay + 2610 overlay
with the pinned (or candidate) 2610 EXE written over the private original name.
Everything is copied into the private run directory made by ``runtime_env.prepare``.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import shutil
from typing import Any

from tools import runtime_env

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO.parent
BASE_SOURCE = ROOT / "[ESL]Syw2plus"
# The base distribution is complete; official 2613 is 2612 data + the 2613 EXE.
OVERLAYS = (ROOT / "patch_history" / "[ESL]Syw2plus 2612",)
# Official 2613 EXE over the 2612 data overlay (no new data bundle was supplied).
ESL2610_EXE = ROOT / "patch_history" / "[ESL]Syw2plus 2613.exe"
ESL2610_SHA256 = "818721a5e8539f9ed97090a6d64cfdba429d46ec9caaa5671528005b22f5b724"
SKIP_SUFFIXES = {".exe", ".xlsx"}
# 2610 selection: count unchanged, entries moved, 100 slots.
SELECTION_COUNT_VA = 0x00899024
SELECTION_ENTRIES_VA = 0x01604004
SELECTION_CAPACITY = 100


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def overlay_files(overlays: tuple[Path, ...] = OVERLAYS) -> list[tuple[Path, Path]]:
    """(source, relative) pairs in overlay order; later overlays replace earlier ones."""
    merged: dict[Path, Path] = {}
    for root in overlays:
        for item in sorted(root.rglob("*")):
            if item.is_symlink() or not item.is_file() or item.suffix.lower() in SKIP_SUFFIXES:
                continue
            merged[item.relative_to(root)] = item
    return [(source, relative) for relative, source in sorted(merged.items())]


def copy_overlays(game: Path, overlays: tuple[Path, ...] = OVERLAYS) -> list[dict[str, Any]]:
    copied: list[dict[str, Any]] = []
    for source, relative in overlay_files(overlays):
        target = game / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied.append({"path": str(relative), "sha256": sha256(target), "bytes": target.stat().st_size})
    return copied


def prepare(exe_bytes: bytes, runtime_root: Path, *, bridge: Path | None = None,
            timeout: float = 90) -> tuple[dict[str, object], list[dict[str, Any]]]:
    """Private game copy + new Wine prefix with the 2610 overlays and ``exe_bytes`` installed."""
    manifest = runtime_env.prepare(BASE_SOURCE, runtime_root=runtime_root, bridge=bridge, timeout=timeout)
    game = Path(str(manifest["game"]["root"]))  # type: ignore[index]
    copied = copy_overlays(game)
    (game / runtime_env.ORIGINAL_EXE).write_bytes(exe_bytes)
    return manifest, copied
