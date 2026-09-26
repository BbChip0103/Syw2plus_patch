from pathlib import Path

import pytest

from patches.ai import gather_cooldown_probe as probe


def fake_original() -> bytes:
    data = bytearray(probe.EDIT_OFFSET + len(probe.BEFORE) + 4)
    data[probe.EDIT_OFFSET : probe.EDIT_OFFSET + len(probe.BEFORE)] = probe.BEFORE
    return bytes(data)


def test_patch_is_single_reversible_instruction(tmp_path: Path, monkeypatch) -> None:
    original = fake_original()
    monkeypatch.setattr(probe, "ORIGINAL_SHA256", probe.digest(original))
    patched = probe.patched_bytes(original)
    assert patched[probe.EDIT_OFFSET : probe.EDIT_OFFSET + len(probe.AFTER)] == probe.AFTER
    assert sum(a != b for a, b in zip(original, patched, strict=True)) == 1
    source = tmp_path / "source.exe"
    destination = tmp_path / "candidate.exe"
    source.write_bytes(original)
    probe.create_copy(source, destination)
    assert probe.restore(destination) == probe.digest(original)
    assert destination.read_bytes() == original


def test_patch_rejects_wrong_hash_and_in_place(tmp_path: Path, monkeypatch) -> None:
    original = fake_original()
    source = tmp_path / "source.exe"
    source.write_bytes(original)
    with pytest.raises(ValueError, match="SHA256"):
        probe.patched_bytes(original)
    monkeypatch.setattr(probe, "ORIGINAL_SHA256", probe.digest(original))
    with pytest.raises(ValueError, match="input"):
        probe.create_copy(source, source)
