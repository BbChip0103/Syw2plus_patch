#!/usr/bin/env python3
"""SHA-pinned, reversible dxwrapper profile for the G1 integer-2x probe.

This changes only a private ``dxwrapper.ini`` copy.  It deliberately does not
edit the game executable, DLLs, or any source/reference installation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil


REPO_ROOT = Path(__file__).resolve().parents[2]
PRIVATE_RUNTIME_ROOT = REPO_ROOT / "local" / "runtime"
SOURCE_SHA256 = "918e704346c20a0393a32501844b64536d7a233163c26305a332f8e56aeea5a2"
CANDIDATE_SHA256 = "f0ce9e649a48a79d427cb218f7952de50095091b8bba4e68ea7dfe8922566785"

# The profile leaves Dd7to9 and DdrawUseNativeResolution enabled as pinned in
# the supplied profile.  On a 1600x1200 display these two scaling guards make
# the 800x600 source an integer 2x 4:3 presentation and disable the QHD custom
# DLL path.
CHANGES: tuple[tuple[bytes, bytes, str], ...] = (
    (
        b"LoadCustomDllPath          = syw2x.dll",
        b"LoadCustomDllPath          =",
        "disable QHD custom syw2x.dll",
    ),
    (
        b"DdrawIntegerScalingClamp   = 0",
        b"DdrawIntegerScalingClamp   = 1",
        "enable integer scaling",
    ),
    (
        b"DdrawMaintainAspectRatio   = 0",
        b"DdrawMaintainAspectRatio   = 1",
        "preserve 4:3 aspect ratio",
    ),
)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build(data: bytes) -> tuple[bytes, dict[str, object]]:
    """Build the one approved profile and return bytes plus an audit manifest."""
    source_sha256 = _sha256(data)
    if source_sha256 != SOURCE_SHA256:
        raise ValueError(f"Unsupported dxwrapper.ini SHA256: {source_sha256}")

    output = data
    changes: list[dict[str, str]] = []
    for old, new, reason in CHANGES:
        if output.count(old) != 1:
            raise ValueError(f"expected exactly one old config line: {reason}")
        offset = output.index(old)
        output = output.replace(old, new, 1)
        changes.append({
            "offset": str(offset),
            "old": old.hex(),
            "new": new.hex(),
            "reason": reason,
        })

    candidate_sha256 = _sha256(output)
    if candidate_sha256 != CANDIDATE_SHA256:
        raise ValueError(
            f"approved dxwrapper.ini candidate SHA256 mismatch: {candidate_sha256}"
        )

    manifest: dict[str, object] = {
        "source_sha256": source_sha256,
        "patched_sha256": candidate_sha256,
        "changes": changes,
        "profile": {
            "Dd7to9": 1,
            "DdrawUseNativeResolution": 1,
            "DdrawIntegerScalingClamp": 1,
            "DdrawMaintainAspectRatio": 1,
            "target_display": "1600x1200",
            "source_composition": "800x600",
        },
    }
    return output, manifest


def _reject_path_links(path: Path) -> None:
    """Reject symlinked path components before resolving the private root."""
    current = Path(path.expanduser().absolute())
    for component in (current, *current.parents):
        if component.is_symlink():
            raise ValueError(f"symlink path component refused: {component}")


def _private_game_root(game_root: Path) -> Path:
    """Accept only a directly-created ``local/runtime/<run>/game`` root."""
    _reject_path_links(game_root)
    root = game_root.expanduser().resolve(strict=False)
    runtime_root = PRIVATE_RUNTIME_ROOT.expanduser().resolve(strict=False)
    try:
        relative = root.relative_to(runtime_root)
    except ValueError as exc:
        raise ValueError("game root must be under local/runtime/<run>/game") from exc
    if len(relative.parts) != 2 or relative.parts[1] != "game":
        raise ValueError("game root must be under local/runtime/<run>/game")
    if root.is_symlink() or not root.is_dir():
        raise ValueError(f"private game root is missing or linked: {root}")
    return root


def install_private(game_root: Path) -> dict[str, object]:
    """Install the pinned profile into one newly-created private game copy."""
    root = _private_game_root(game_root)
    target = root / "dxwrapper.ini"
    if target.is_symlink() or not target.is_file():
        raise ValueError(f"private dxwrapper.ini is missing or linked: {target}")
    data = target.read_bytes()
    if _sha256(data) != SOURCE_SHA256:
        raise ValueError("private dxwrapper.ini is not the pinned original")
    patched, manifest = build(data)
    if manifest["patched_sha256"] != CANDIDATE_SHA256:
        raise ValueError("approved dxwrapper.ini candidate pin did not match")
    backup = target.with_suffix(target.suffix + ".original-backup")
    manifest_path = target.with_suffix(target.suffix + ".patch.json")
    if backup.exists() or backup.is_symlink() or manifest_path.exists() or manifest_path.is_symlink():
        raise ValueError("private dxwrapper.ini install sidecar already exists")

    backup.write_bytes(data)
    try:
        target.write_bytes(patched)
        manifest["installation"] = {
            "game_root": str(root),
            "target": str(target),
            "backup": str(backup),
            "manifest": str(manifest_path),
                "installed_sha256": _sha256(target.read_bytes()),
        }
        if manifest["installation"]["installed_sha256"] != CANDIDATE_SHA256:  # type: ignore[index]
            raise ValueError("installed dxwrapper.ini candidate hash did not match")
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    except Exception:
        if target.is_file() and _sha256(target.read_bytes()) == CANDIDATE_SHA256:
            shutil.copyfile(backup, target)
        if manifest_path.exists() or manifest_path.is_symlink():
            manifest_path.unlink()
        if backup.exists() or backup.is_symlink():
            backup.unlink()
        raise
    return manifest


def uninstall_private(game_root: Path) -> dict[str, object]:
    """Restore and remove the sidecars for a previously installed private profile."""
    root = _private_game_root(game_root)
    target = root / "dxwrapper.ini"
    backup = target.with_suffix(target.suffix + ".original-backup")
    manifest_path = target.with_suffix(target.suffix + ".patch.json")
    restore(target)
    restored_sha256 = _sha256(target.read_bytes())
    if restored_sha256 != SOURCE_SHA256:
        raise ValueError("private dxwrapper.ini restore hash did not match")
    backup.unlink()
    manifest_path.unlink()
    return {"target": str(target), "restored_sha256": restored_sha256, "sidecars_removed": True}


def apply(source: Path, target: Path) -> dict[str, object]:
    """Write a new candidate and guarded backup; never overwrite a target."""
    source = source.expanduser().resolve()
    target = target.expanduser().resolve()
    if source == target or target.exists():
        raise ValueError("Output must be a new distinct file")
    data = source.read_bytes()
    patched, manifest = build(data)
    backup = target.with_suffix(target.suffix + ".original-backup")
    manifest_path = target.with_suffix(target.suffix + ".patch.json")
    if backup.exists() or manifest_path.exists():
        raise ValueError("Candidate sidecar already exists")
    backup.write_bytes(data)
    target.write_bytes(patched)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def restore(target: Path) -> None:
    """Restore only an untouched candidate from its guarded original backup."""
    target = target.expanduser().resolve()
    backup = target.with_suffix(target.suffix + ".original-backup")
    manifest_path = target.with_suffix(target.suffix + ".patch.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("source_sha256") != SOURCE_SHA256:
        raise ValueError("Restore refuses unsupported source pin")
    if manifest.get("patched_sha256") != CANDIDATE_SHA256:
        raise ValueError("Restore refuses unsupported candidate pin")
    if _sha256(backup.read_bytes()) != SOURCE_SHA256:
        raise ValueError("Restore refuses modified source backup")
    if _sha256(target.read_bytes()) != manifest["patched_sha256"]:
        raise ValueError("Restore refuses modified candidate")
    shutil.copyfile(backup, target)


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    apply_parser = subparsers.add_parser("apply")
    apply_parser.add_argument("source", type=Path)
    apply_parser.add_argument("target", type=Path)
    restore_parser = subparsers.add_parser("restore")
    restore_parser.add_argument("target", type=Path)
    args = parser.parse_args()
    if args.command == "apply":
        print(json.dumps(apply(args.source, args.target), indent=2))
    else:
        restore(args.target)


if __name__ == "__main__":
    main()
