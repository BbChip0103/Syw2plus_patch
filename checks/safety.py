#!/usr/bin/env python3
"""Fail-closed original/reference checks; pin is explicit and never overwrites trust."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from context_limits import check as context_errors

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL_SHA = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"
BANNED = {
    ".exe",
    ".dll",
    ".dat",
    ".bin",
    ".spr",
    ".yav",
    ".cof",
    ".pal",
    ".a",
    ".o",
    ".original",
    ".original-backup",
}


def protected(root: Path) -> dict[str, str]:
    result = {}
    for folder in ["docs/reference", "docs/baseline/golden"]:
        for path in sorted((root / folder).rglob("*")):
            if path.is_file():
                result[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def trust_path(root: Path) -> Path:
    common = subprocess.check_output(
        ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], cwd=root, text=True
    ).strip()
    return Path(common) / "syw2plus-patch-safety.json"


def check(root: Path, anchor: Path, require_game: bool = False) -> list[str]:
    errors = context_errors(root)
    try:
        expected = json.loads(anchor.read_text())["files"]
        if not expected or expected != protected(root):
            errors.append("Protected reference/golden changed or empty trust anchor")
    except (OSError, ValueError, KeyError):
        errors.append("Missing/invalid explicit safety pin; do not auto-adopt current files")
    original = root / "Syw2plus/syw2plus_original.exe"
    if original.is_file():
        if hashlib.sha256(original.read_bytes()).hexdigest() != ORIGINAL_SHA:
            errors.append("Original EXE SHA256 mismatch")
    elif require_game:
        errors.append("Original EXE required for real agent/runtime loop")
    # Check trackable and staged inputs, including force-added ignored binaries.
    names = (
        subprocess.check_output(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=root
        )
        .decode("utf-8", "surrogateescape")
        .split("\0")
    )
    for name in names:
        if not name:
            continue
        path = Path(name)
        if (
            path.suffix.lower() in BANNED
            or path.parts[0] in {"Syw2plus", "local", ".omx", ".omc", ".venv", "logs"}
            or path.name == ".env"
            or path.name == "env.local.sh"
            or name in {"loop/STOP", "loop/FULL_TEST", "loop/.lap_counter", "loop/ESCALATE_SOL"}
            or (path.name.startswith(".env.") and path.name != ".env.example")
        ):
            errors.append(f"Unsafe Git input: {name}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["pin", "check"], nargs="?", default="check")
    parser.add_argument("--require-game", action="store_true")
    args = parser.parse_args()
    anchor = trust_path(ROOT)
    if args.command == "pin":
        files = protected(ROOT)
        if not files:
            parser.error("No reference files to pin")
        with anchor.open("x") as stream:
            json.dump(
                {"files": files, "note": "Explicit setup pin, not worker self-approval"},
                stream,
                indent=2,
            )
        print(f"PINNED {anchor}")
        return 0
    errors = check(ROOT, anchor, args.require_game)
    print("\n".join(errors) if errors else "SAFETY_PASS")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
