from __future__ import annotations

import json
from pathlib import Path

import pytest

from patches.population import runtime_driver


def test_atomic_json_writes_unicode_json_to_tmp_then_replaces_target(tmp_path: Path):
    target = tmp_path / "state.json"
    target.write_text("old", encoding="utf-8")
    value = {"message": "한글 café", "items": (1, True, None)}

    runtime_driver.atomic_json(target, value)

    assert target.read_text(encoding="utf-8") == json.dumps(
        value, ensure_ascii=False, indent=2
    )
    assert not target.with_suffix(".tmp").exists()


def test_atomic_json_serialization_error_preserves_target_and_existing_tmp(tmp_path: Path):
    target = tmp_path / "state.json"
    temporary = target.with_suffix(".tmp")
    target.write_text("old target", encoding="utf-8")
    temporary.write_text("old temporary", encoding="utf-8")

    with pytest.raises(TypeError):
        runtime_driver.atomic_json(target, {"unsupported": object()})

    assert target.read_text(encoding="utf-8") == "old target"
    assert temporary.read_text(encoding="utf-8") == "old temporary"


def test_atomic_json_replace_error_preserves_target_and_written_tmp(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    target = tmp_path / "state.json"
    temporary = target.with_suffix(".tmp")
    target.write_text("old target", encoding="utf-8")

    def fail_replace(_self: Path, _target: Path) -> Path:
        raise OSError("replace failed")

    monkeypatch.setattr(Path, "replace", fail_replace)
    with pytest.raises(OSError, match="replace failed"):
        runtime_driver.atomic_json(target, {"message": "새 값"})

    assert target.read_text(encoding="utf-8") == "old target"
    assert temporary.read_text(encoding="utf-8") == json.dumps(
        {"message": "새 값"}, ensure_ascii=False, indent=2
    )
