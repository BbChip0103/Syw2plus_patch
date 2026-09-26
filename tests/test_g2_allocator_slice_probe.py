"""Focused, fail-closed checks for the isolated G2 allocator slice."""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from tools.g2_allocator_slice_probe import (
    ALLOCATOR_BYTES,
    ALLOCATOR_FILE_OFFSET,
    CAPACITIES,
    ORIGINAL_SHA256,
    RESULT_POLICY,
    compile_fixture,
    run_fixture,
    verify_original,
)

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / "Syw2plus" / "syw2plus_original.exe"


def test_original_is_pinned_and_exact_slice_is_not_reimplemented():
    if not ORIGINAL.is_file():
        pytest.skip("local original executable unavailable")
    report = verify_original(ORIGINAL)
    assert report["sha256"] == ORIGINAL_SHA256
    assert int(report["allocator_file_offset"], 16) == ALLOCATOR_FILE_OFFSET
    assert bytes.fromhex(str(report["allocator_bytes"])) == ALLOCATOR_BYTES
    assert len(ALLOCATOR_BYTES) == 0x3D


def test_capacity_geometry_and_capacity_aware_bias():
    assert CAPACITIES == (1200, 1201, 4001)
    assert 1200 * 2 == 0x960
    assert 1201 * 2 == 0x962
    assert 4001 * 2 == 0x1F42
    assert RESULT_POLICY["activation"] == "NO-GO"


def test_fixture_compiles_as_standalone_win32(tmp_path: Path):
    compiler = shutil.which("i686-w64-mingw32-gcc")
    if not compiler:
        pytest.skip("i686-w64-mingw32-gcc unavailable")
    executable = compile_fixture(tmp_path / "g2_allocator_slice_fixture.exe", compiler)
    assert executable.is_file()
    assert executable.stat().st_size > 0


def test_scope_does_not_claim_game_activation():
    assert RESULT_POLICY == {
        "activation": "NO-GO",
        "scope": "transplanted original allocator selector only; no spawn/save/LAN/ID proof",
        "execution": "dynamic transplanted original machine code in standalone Win32 process; never the game",
        "bulk_sentinel": "standalone only; not original-game bulk safety proof",
    }


def test_execution_admission_requires_explicit_owned_prefix(monkeypatch):
    if not ORIGINAL.is_file():
        pytest.skip("local original executable unavailable")
    monkeypatch.setenv("G2_ALLOCATOR_SLICE_ALLOW_WINE", "1")
    monkeypatch.delenv("WINEPREFIX", raising=False)
    with pytest.raises(RuntimeError, match="absolute WINEPREFIX"):
        run_fixture(ORIGINAL, Path("missing-fixture.exe"), allow_execution=True)
