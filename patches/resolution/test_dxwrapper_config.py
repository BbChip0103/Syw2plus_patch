"""Config-profile safety tests; no Wine sessions launched."""

from pathlib import Path

import pytest

from patches.resolution import dxwrapper_config as config


SOURCE = Path("/home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus_re/Syw2plus/dxwrapper.ini")


@pytest.fixture
def source(tmp_path: Path) -> tuple[Path, bytes]:
    if not SOURCE.is_file():
        pytest.skip("Pinned dxwrapper.ini reference unavailable")
    path = tmp_path / "dxwrapper.ini"
    data = SOURCE.read_bytes()
    path.write_bytes(data)
    return path, data


def test_identity_rejected() -> None:
    with pytest.raises(ValueError, match="Unsupported dxwrapper.ini SHA256"):
        config.build(b"not the pinned profile")


def test_exact_profile_roundtrip_and_manifest(source: tuple[Path, bytes], tmp_path: Path) -> None:
    source_path, before = source
    target = tmp_path / "candidate.ini"
    manifest = config.apply(source_path, target)
    assert target.read_bytes() != before
    assert len(manifest["changes"]) == 3
    assert manifest["patched_sha256"] == config.CANDIDATE_SHA256
    assert all(set(change) == {"offset", "old", "new", "reason"} for change in manifest["changes"])
    candidate = target.read_text(encoding="utf-8")
    assert "LoadCustomDllPath          = syw2x.dll" not in candidate
    assert "LoadCustomDllPath          =\r\n" in candidate or "LoadCustomDllPath          =\n" in candidate
    assert "DdrawIntegerScalingClamp   = 1" in candidate
    assert "DdrawMaintainAspectRatio   = 1" in candidate
    config.restore(target)
    assert target.read_bytes() == before


def test_refuse_in_place_and_overwrite(source: tuple[Path, bytes], tmp_path: Path) -> None:
    source_path, _ = source
    with pytest.raises(ValueError, match="new distinct"):
        config.apply(source_path, source_path)
    target = tmp_path / "existing.ini"
    target.write_text("keep", encoding="utf-8")
    with pytest.raises(ValueError, match="new distinct"):
        config.apply(source_path, target)
    assert target.read_text(encoding="utf-8") == "keep"


def test_restore_refuses_candidate_tampering(source: tuple[Path, bytes], tmp_path: Path) -> None:
    source_path, _ = source
    target = tmp_path / "candidate.ini"
    config.apply(source_path, target)
    target.write_bytes(target.read_bytes() + b"tampered")
    with pytest.raises(ValueError, match="modified candidate"):
        config.restore(target)


def test_private_install_is_pinned_and_uninstall_is_byte_exact(
    source: tuple[Path, bytes], tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_path, before = source
    repo = tmp_path / "repo"
    game = repo / "local" / "runtime" / "run-1" / "game"
    game.mkdir(parents=True)
    target = game / "dxwrapper.ini"
    target.write_bytes(source_path.read_bytes())
    monkeypatch.setattr(config, "REPO_ROOT", repo)
    monkeypatch.setattr(config, "PRIVATE_RUNTIME_ROOT", repo / "local" / "runtime")

    manifest = config.install_private(game)
    assert manifest["source_sha256"] == config.SOURCE_SHA256
    assert manifest["patched_sha256"] == config.CANDIDATE_SHA256
    assert config._sha256(target.read_bytes()) == config.CANDIDATE_SHA256
    result = config.uninstall_private(game)
    assert result["restored_sha256"] == config.SOURCE_SHA256
    assert target.read_bytes() == before
    assert not target.with_suffix(target.suffix + ".original-backup").exists()
    assert not target.with_suffix(target.suffix + ".patch.json").exists()


def test_private_install_rejects_non_private_and_linked_roots(
    source: tuple[Path, bytes], tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_path, _ = source
    repo = tmp_path / "repo"
    private_root = repo / "local" / "runtime"
    monkeypatch.setattr(config, "REPO_ROOT", repo)
    monkeypatch.setattr(config, "PRIVATE_RUNTIME_ROOT", private_root)
    foreign = tmp_path / "foreign-game"
    foreign.mkdir()
    with pytest.raises(ValueError, match="under local/runtime"):
        config.install_private(foreign)

    game = private_root / "run-1" / "game"
    game.mkdir(parents=True)
    link = game / "dxwrapper.ini"
    link.symlink_to(source_path)
    with pytest.raises(ValueError, match="missing or linked"):
        config.install_private(game)
