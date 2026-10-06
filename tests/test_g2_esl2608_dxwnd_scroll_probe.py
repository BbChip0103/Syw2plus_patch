from pathlib import Path

from tools import g2_esl2608_dxwnd_scroll_probe as probe


def test_profile_uses_c_drive_target_and_private_game_startfolder(tmp_path: Path) -> None:
    bundle = tmp_path / "dxwnd"
    bundle.mkdir()
    game = tmp_path / "game"
    game.mkdir()
    target = game / "candidate.exe"
    target.write_bytes(b"fixture")
    profile = probe._profile(
        bundle, game, target, title="fixture",
        bundle_win_path="C:\\dxwnd\\",
        target_win_path="C:\\dxwnd\\candidate.exe",
    )
    text = profile.read_text(encoding="latin-1")
    assert "path0=C:\\dxwnd\\candidate.exe" in text
    assert "launchpath0=C:\\dxwnd\\candidate.exe" in text
    assert f"startfolder0={probe._win_path(game)}" in text
    assert "sizx0=800" in text and "sizy0=600" in text


def test_delivered_filename_and_sha_are_pinned() -> None:
    for lane, name in probe.TARGET_FILENAMES.items():
        candidate = probe.INPUT_ROOT / name
        assert candidate.is_file()
        assert probe._digest(candidate) == probe.TARGET_SHA[lane]
