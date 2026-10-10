#!/usr/bin/env python3
"""Isolated runtime assembly for the official ESL 2613 executable.

The official 2613 release is installed over the 2612 data bundle. Build each
lane from the read-only original game tree, apply that bundle, then replace the
private original executable with the pinned 2613 executable.
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
OVERLAYS = (ROOT / "patch_history" / "[ESL]Syw2plus 2612",)
ESL2613_EXE = ROOT / "patch_history" / "[ESL]Syw2plus 2613.exe"
ESL2613_SHA256 = "818721a5e8539f9ed97090a6d64cfdba429d46ec9caaa5671528005b22f5b724"
SKIP_SUFFIXES = {".exe", ".xlsx"}

# The official 2613 release preserves the 2612 G1 address layout, including
# the 100-entry selection array.
SELECTION_COUNT_VA = 0x00899024
SELECTION_ENTRIES_VA = 0x01604004
SELECTION_CAPACITY = 100


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def overlay_files(overlays: tuple[Path, ...] = OVERLAYS) -> list[tuple[Path, Path]]:
    """Return sorted (source, relative path) pairs in overlay order."""
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
    """Prepare a private original + 2612 bundle + pinned 2613 executable lane."""
    manifest = runtime_env.prepare(BASE_SOURCE, runtime_root=runtime_root, bridge=bridge, timeout=timeout)
    game = Path(str(manifest["game"]["root"]))  # type: ignore[index]
    copied = copy_overlays(game)
    (game / runtime_env.ORIGINAL_EXE).write_bytes(exe_bytes)
    return manifest, copied
