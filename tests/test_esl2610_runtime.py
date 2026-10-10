from __future__ import annotations

from pathlib import Path

from tools import esl2610_runtime as rt


def test_later_overlay_replaces_earlier_and_exe_xlsx_are_skipped(tmp_path: Path) -> None:
    a, b = tmp_path / "a", tmp_path / "b"
    (a / "Data").mkdir(parents=True)
    (b / "Data").mkdir(parents=True)
    (a / "Data" / "x.dat").write_bytes(b"old")
    (b / "Data" / "x.dat").write_bytes(b"new")
    (a / "keep.bin").write_bytes(b"k")
    (a / "game.EXE").write_bytes(b"MZ")
    (b / "notes.xlsx").write_bytes(b"x")
    pairs = {rel.as_posix(): src for src, rel in rt.overlay_files((a, b))}
    assert set(pairs) == {"Data/x.dat", "keep.bin"}
    assert pairs["Data/x.dat"] == b / "Data" / "x.dat"


def test_copy_overlays_writes_into_game_dir(tmp_path: Path) -> None:
    a = tmp_path / "a"
    (a / "d").mkdir(parents=True)
    (a / "d" / "f.bin").write_bytes(b"abc")
    game = tmp_path / "game"
    copied = rt.copy_overlays(game, (a,))
    assert (game / "d" / "f.bin").read_bytes() == b"abc"
    assert copied[0]["path"] == "d/f.bin" and copied[0]["bytes"] == 3


def test_selection_layout_constants() -> None:
    assert rt.SELECTION_ENTRIES_VA - rt.SELECTION_COUNT_VA == 0xD6AFE0
    assert rt.SELECTION_CAPACITY == 100


def test_runtime_uses_2613_exe_with_2612_data_overlay() -> None:
    assert rt.ESL2610_EXE.name == "[ESL]Syw2plus 2613.exe"
    assert rt.ESL2610_SHA256 == "818721a5e8539f9ed97090a6d64cfdba429d46ec9caaa5671528005b22f5b724"
    assert rt.OVERLAYS == (rt.ROOT / "patch_history" / "[ESL]Syw2plus 2612",)
