"""Static-only guardrails for the private 1600x1200 research candidate."""

from __future__ import annotations

import hashlib
from pathlib import Path
import struct

import pefile
import pytest

from patches.resolution import native_1600_probe as probe
from patches.resolution import qhd_probe


SOURCE = Path(__file__).resolve().parents[2] / "Syw2plus_re" / "Syw2plus" / "syw2plus_original.exe"
HISTORICAL_QHD_SHA = "c4b912d96e623de91b7cc25de35c57395d8de1e01801e948f45b5b456b80f993"


def _original_bytes() -> bytes:
    if not SOURCE.is_file():
        pytest.skip("private game files are not installed")
    data = SOURCE.read_bytes()
    assert hashlib.sha256(data).hexdigest() == qhd_probe.SHA
    return data


def test_static_build_sets_native_dimensions_without_mutating_historical_qhd():
    original = _original_bytes()
    before = (qhd_probe.WIDTH, qhd_probe.HEIGHT, qhd_probe.RADIUS)
    patched, manifest = probe.build(original)
    assert (qhd_probe.WIDTH, qhd_probe.HEIGHT, qhd_probe.RADIUS) == before
    assert manifest["source_sha256"] == qhd_probe.SHA
    assert manifest["patched_sha256"] == hashlib.sha256(patched).hexdigest()
    assert (manifest["width"], manifest["height"]) == (1600, 1200)
    assert len(manifest["changes"]) == 74
    pe = pefile.PE(data=patched)
    for va, expected in ((0x464505, 1600), (0x46450C, 1200),
                         (0x432917, 1600), (0x432912, 1200)):
        assert struct.unpack("<I", pe.get_data(va - 0x400000, 4))[0] == expected
    qhd, _ = qhd_probe.build(original)
    assert hashlib.sha256(qhd).hexdigest() == HISTORICAL_QHD_SHA


def test_sha_rejection_restores_scoped_dimensions_and_writes_nothing(tmp_path: Path):
    before = (qhd_probe.WIDTH, qhd_probe.HEIGHT, qhd_probe.RADIUS)
    source = tmp_path / "wrong.exe"
    target = tmp_path / "candidate.exe"
    source.write_bytes(b"unsupported game version")
    with pytest.raises(ValueError, match="Unsupported binary SHA256"):
        probe.apply(source, target)
    assert (qhd_probe.WIDTH, qhd_probe.HEIGHT, qhd_probe.RADIUS) == before
    assert not target.exists()
    assert not target.with_suffix(".exe.original-backup").exists()
