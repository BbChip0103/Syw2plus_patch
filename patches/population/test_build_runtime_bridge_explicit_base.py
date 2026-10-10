"""The layout-agnostic explicit pool/existence base path of the bridge builder.

A pure-helper test of the argument semantics: the explicit pair must be used
verbatim (for relocation schemes other than ESL2608, e.g. the ESL2610 .g2bss
build) and must require --unit-pool-base, while existing callers that omit
--unit-existence-base are unaffected.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BUILDER = REPO / "patches" / "population" / "build_runtime_bridge.py"


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(BUILDER), *args],
        cwd=REPO, env={"PYTHONPATH": str(REPO), "PATH": ""},
        capture_output=True, text=True,
    )


def test_existence_base_requires_pool_base(tmp_path: Path) -> None:
    out = tmp_path / "out"  # never created: argparse errors before any build
    result = _run([
        "--out-dir", str(out),
        "--unit-pool-capacity", "4093",
        "--unit-existence-base", "0x220b9f8",
    ])
    assert result.returncode != 0
    assert "requires --unit-pool-base" in (result.stderr + result.stdout)
    assert not out.exists()


def test_help_lists_the_explicit_existence_base_option() -> None:
    result = _run(["--help"])
    assert result.returncode == 0
    assert "--unit-existence-base" in result.stdout
    assert "layout-agnostic" in result.stdout
