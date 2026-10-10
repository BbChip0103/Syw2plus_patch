from __future__ import annotations

from pathlib import Path

from tools import esl2613_runtime as rt


def test_runtime_pins_official_2613_and_uses_only_the_2612_bundle() -> None:
    assert rt.ESL2613_EXE.name == "[ESL]Syw2plus 2613.exe"
    assert rt.ESL2613_EXE.is_file()
    assert rt.sha256(rt.ESL2613_EXE) == rt.ESL2613_SHA256
    assert rt.ESL2613_EXE.stat().st_size == 2_000_896
    assert len(rt.OVERLAYS) == 1
    assert rt.OVERLAYS[0].name == "[ESL]Syw2plus 2612"
    assert rt.OVERLAYS[0].is_dir()


def test_overlay_merge_excludes_executables_and_keeps_later_override(tmp_path: Path) -> None:
    base, bundle = tmp_path / "base", tmp_path / "2612"
    (base / "Data").mkdir(parents=True)
    (bundle / "Data").mkdir(parents=True)
    (base / "Data" / "x.dat").write_bytes(b"base")
    (bundle / "Data" / "x.dat").write_bytes(b"2612")
    (bundle / "[ESL]Syw2plus 2612.exe").write_bytes(b"2612 exe")
    pairs = rt.overlay_files((base, bundle))
    assert pairs == [(bundle / "Data" / "x.dat", Path("Data/x.dat"))]


def test_prepare_copies_bundle_before_installing_pinned_executable(monkeypatch, tmp_path: Path) -> None:
    from tools import runtime_env

    game = tmp_path / "private-game"
    game.mkdir()
    overlay = tmp_path / "bundle"
    (overlay / "Data").mkdir(parents=True)
    (overlay / "Data" / "x.dat").write_bytes(b"bundle-data")
    exe = b"pinned-2613-exe"
    monkeypatch.setattr(rt, "OVERLAYS", (overlay,))
    monkeypatch.setattr(rt, "overlay_files", lambda _overlays: [(overlay / "Data" / "x.dat", Path("Data/x.dat"))])
    monkeypatch.setattr(runtime_env, "prepare", lambda *args, **kwargs: {"game": {"root": str(game)}})

    manifest, copied = rt.prepare(exe, tmp_path / "runtime")

    assert manifest["game"]["root"] == str(game)
    assert (game / "Data" / "x.dat").read_bytes() == b"bundle-data"
    assert (game / runtime_env.ORIGINAL_EXE).read_bytes() == exe
    assert copied[0]["path"] == "Data/x.dat"
