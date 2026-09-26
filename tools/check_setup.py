#!/usr/bin/env python3
"""Read-only setup diagnostics. No Wine process, installation or patch side effects."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SHA = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"

# ``python tools/check_setup.py`` puts ``tools/`` (not the repository root)
# on sys.path, while package/type-check invocations start at the root.
if __package__ in {None, ""}:
    sys.path.insert(0, str(ROOT / "tools"))
from runtime_env import (  # noqa: E402
    DEFAULT_RUNTIME_ROOT,
    RuntimeSafetyError,
    check_runtime,
    probe_libraries,
    probe_model_clis,
    probe_tools,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-game", action="store_true")
    parser.add_argument(
        "--require-runtime",
        action="store_true",
        help="fail unless all Wine/X11/MinGW tools and the validated local manifest exist",
    )
    parser.add_argument(
        "--runtime-manifest",
        type=Path,
        default=ROOT / DEFAULT_RUNTIME_ROOT / "manifest.json",
        help="dedicated manifest emitted by tools/runtime_env.py prepare",
    )
    args = parser.parse_args()
    versions: dict[str, str | None] = {}
    for name in ["pefile", "capstone", "pytest", "ruff", "mypy"]:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    original = ROOT / "Syw2plus/syw2plus_original.exe"
    digest = hashlib.sha256(original.read_bytes()).hexdigest() if original.is_file() else None
    tools = probe_tools()
    libraries = probe_libraries()
    missing_tools = [name for name, status in tools.items() if not status.present]
    missing_libraries = [name for name, status in libraries.items() if not status.present]
    manifest: dict[str, object] = {
        "path": str(args.runtime_manifest),
        "present": args.runtime_manifest.is_file(),
        "valid": False,
    }
    try:
        evidence = check_runtime(args.runtime_manifest)
        manifest.update({"valid": True, "message": "runtime_env.check_runtime accepted", "evidence": evidence})
    except (OSError, RuntimeSafetyError, ValueError, KeyError, TypeError) as exc:
        manifest["message"] = f"runtime_env.check_runtime rejected: {type(exc).__name__}"
    runtime = {
        "ok": not missing_tools and not missing_libraries and bool(manifest["valid"]),
        "tools": {
            name: {"name": name, "path": status.path, "present": status.present}
            for name, status in tools.items()
        },
        "libraries": {
            name: {"name": name, "path": status.path, "present": status.present}
            for name, status in libraries.items()
        },
        "missing_tools": missing_tools,
        "missing_libraries": missing_libraries,
        "manifest": manifest,
        "side_effects": False,
    }
    ok = all(versions.values()) and (digest == SHA if digest else not args.require_game)
    if args.require_runtime:
        ok = ok and bool(runtime["ok"])
    report = {
        "ok": ok,
        "python": sys.version,
        "repo": str(ROOT),
        "packages": versions,
        "original_sha256": digest,
        "original_status": "verified" if digest == SHA else ("missing" if not digest else "WRONG"),
        # Kept as a compatibility view for existing setup logs.  It is
        # informational unless --require-runtime is explicitly requested.
        "runtime_tools_optional": {
            name: status.path for name, status in tools.items()
        },
        "runtime": runtime,
        "model_clis": probe_model_clis(),
        "note": "Missing original means binary tests SKIP, not fresh runtime verification.",
    }
    print(json.dumps(report, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
