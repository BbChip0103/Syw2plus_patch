#!/usr/bin/env python3
"""Assemble an isolated full-game copy from the pinned official ESL2614 input."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
from typing import Any

from tools import runtime_env


REPO = Path(__file__).resolve().parents[1]
ROOT = REPO.parent
ESL2614_SOURCE = ROOT / "[ESL]Syw2plus - ESL2614"
ESL2614_NESTED_SOURCE_NAME = "[ESL]Syw2plus"
ESL2614_EXE_NAME = "[ESL]Syw2plus 2614.exe"
ESL2614_SHA256 = "ac61a28f84f71d602c581a17c835ec4dbb99aad0341c6755e395549005cf88bf"
G1_WINMM = REPO / "tools" / "inmm_stub" / "winmm.dll"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_source() -> tuple[Path, Path]:
    source_input = ESL2614_SOURCE.expanduser()
    if source_input.is_symlink() or not source_input.is_dir():
        raise runtime_env.RuntimeSafetyError("ESL2614 input must be a real read-only directory")
    source = source_input.resolve(strict=True)
    runtime_env._reject_links(source)
    if not (source / ESL2614_EXE_NAME).is_file():
        nested = source / ESL2614_NESTED_SOURCE_NAME
        if nested.is_symlink() or not nested.is_dir():
            raise runtime_env.RuntimeSafetyError("ESL2614 nested input must be a real read-only directory")
        runtime_env._reject_links(nested)
        source = nested.resolve(strict=True)
    exe = source / ESL2614_EXE_NAME
    if not exe.is_file() or exe.is_symlink() or sha256(exe) != ESL2614_SHA256:
        raise runtime_env.RuntimeSafetyError("ESL2614 executable SHA-256 mismatch")
    return source, exe


def prepare(runtime_root: Path, *, g1_enabled: bool, timeout: float = 90) -> dict[str, Any]:
    """Use runtime_env for a fresh prefix, then populate its private game with 2614."""
    source, source_exe = verify_source()
    run_root = runtime_root.expanduser().resolve()
    if run_root == source or source in run_root.parents or run_root in source.parents:
        raise runtime_env.RuntimeSafetyError("source and runtime output must remain separate")

    # This creates a fresh owned Wine prefix and private output/manifest tree.
    manifest = runtime_env.prepare(runtime_env.DEFAULT_SOURCE, runtime_root=run_root,
                                   bridge=None, timeout=timeout)
    game = Path(str(manifest["game"]["root"]))
    for base, dirs, files in os.walk(source, followlinks=False):
        rel = Path(base).relative_to(source)
        destination = game / rel
        destination.mkdir(parents=True, exist_ok=True)
        for name in files:
            src = Path(base) / name
            if src.is_symlink() or not src.is_file():
                raise runtime_env.RuntimeSafetyError(f"unsafe ESL2614 input item: {src}")
            shutil.copy2(src, destination / name)
    copied_exe = game / ESL2614_EXE_NAME
    canonical_exe = game / runtime_env.ORIGINAL_EXE
    shutil.copy2(source_exe, canonical_exe)
    if sha256(copied_exe) != ESL2614_SHA256 or sha256(canonical_exe) != ESL2614_SHA256:
        raise runtime_env.RuntimeSafetyError("private ESL2614 executable copy failed SHA check")

    proxy_path = game / "winmm.dll"
    if g1_enabled:
        if proxy_path.exists() or proxy_path.is_symlink():
            raise runtime_env.RuntimeSafetyError("ESL2614 source already contains app-local winmm.dll")
        if not G1_WINMM.is_file():
            raise runtime_env.RuntimeSafetyError("G1 WINMM proxy has not been built")
        shutil.copy2(G1_WINMM, proxy_path)

    manifest["esl2614"] = {
        "source_root": str(source), "source_exe": str(source_exe),
        "source_exe_sha256": ESL2614_SHA256,
        "copied_exe_sha256": sha256(copied_exe),
        "canonical_exe_sha256": sha256(canonical_exe),
        "g1_winmm_enabled": g1_enabled,
        "g1_winmm_sha256": sha256(proxy_path) if g1_enabled else None,
    }
    run_dir = Path(str(manifest["output"]["run_dir"]))
    runtime_env._write_json(run_dir / "manifest.json", manifest)
    return manifest
