"""H-HDX2 HD picture checker/converter: synthetic reference frames, no game folder needed."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from tools import g1_hd_convert as hc
from tools import g1_hd_extract as hx

ROOT = Path(__file__).resolve().parents[1]
GAME = Path("/nonexistent/game")


def _palette() -> np.ndarray:
    pal = np.zeros((256, 3), dtype=np.uint8)
    for i in range(256):
        pal[i] = (i, (i * 7) % 256, (i * 13) % 256)
    pal[182] = pal[16]                       # equal-RGB pair like the real palette
    return pal


def _ref_idx() -> np.ndarray:
    idx = np.full((3, 4), 254, dtype=np.uint8)
    idx[0, 1], idx[0, 2] = 20, 237           # plain + team
    idx[1, 0:4] = (30, 40, 238, 50)
    idx[2, 1] = 60
    return idx


def _write_ref(ref_dir: Path, rel: str, frame: str, idx: np.ndarray, pal: np.ndarray) -> hc.RefFrame:
    opq = idx != 254
    base = ref_dir / rel / frame
    hx.save_index_png(Path(f"{base}.png"), idx, pal)
    hx.save_mask_png(Path(f"{base}_mask.png"), opq)
    hx.save_index_png(Path(f"{base}_2x.png"), hx.scale2x_masked(idx, opq), pal)
    return hc.load_ref_png(Path(f"{base}.png"))


def _rgb(idx: np.ndarray, pal: np.ndarray) -> np.ndarray:
    return pal[idx]


@pytest.fixture()
def ref(tmp_path: Path) -> hc.RefFrame:
    return _write_ref(tmp_path / "ref", "char/u.spr", "0000", _ref_idx(), _palette())


def test_reference_silhouette_and_footprint(ref: hc.RefFrame) -> None:
    assert ref.silhouette2x.shape == (6, 8) and int(ref.silhouette2x.sum()) == 7 * 4
    assert int(ref.footprint.sum()) == 8                      # two team pixels x 4
    assert ref.footprint[0:2, 4:6].all()


def test_quantize_exact_colours_round_trip_the_draft(ref: hc.RefFrame) -> None:
    pal = _palette()
    out, stats = hc.quantize(_rgb(ref.draft, pal), ref, pal)
    assert np.array_equal(out, ref.draft)
    assert stats["pixels"] == 28


def test_quantize_forces_silhouette_even_when_colour_is_254(ref: hc.RefFrame) -> None:
    pal = _palette()
    rgb = _rgb(ref.draft, pal).copy()
    rgb[ref.silhouette2x] = pal[254]                            # opaque area painted in the key colour
    rgb[~ref.silhouette2x] = pal[20]                            # transparent area painted opaque
    out, _ = hc.quantize(rgb, ref, pal)
    assert np.array_equal(out == 254, ~ref.silhouette2x)


def test_quantize_team_candidates_only_inside_footprint(ref: hc.RefFrame) -> None:
    pal = _palette()
    rgb = _rgb(ref.draft, pal).copy()
    rgb[ref.footprint] = pal[20]                                # plain colour in team footprint
    outside = ref.silhouette2x & ~ref.footprint
    rgb[outside] = pal[237]                                     # team colour outside the footprint
    out, _ = hc.quantize(rgb, ref, pal)
    assert ((out[ref.footprint] >= 236) & (out[ref.footprint] <= 239)).all()
    assert not ((out[outside] >= 236) & (out[outside] <= 239)).any()
    assert not (out[outside] == 254).any()


def test_quantize_tie_rule_prefers_draft_then_smallest(ref: hc.RefFrame) -> None:
    pal = _palette()
    ref_a = ref
    rgb = _rgb(ref_a.draft, pal).copy()
    rgb[ref_a.silhouette2x & ~ref_a.footprint] = pal[16]       # equal to idx 16 and 182
    draft = ref_a.draft.copy()
    sel = ref_a.silhouette2x & ~ref_a.footprint
    draft[sel] = 182
    out, stats = hc.quantize(rgb, hc.RefFrame(ref_a.idx, ref_a.opaque, draft), pal)
    assert (out[sel] == 182).all() and stats["tie_pixels"] == int(sel.sum())
    assert stats["tie_resolved_by_draft"] == int(sel.sum())
    draft[sel] = 40                                              # not among the nearest
    out2, stats2 = hc.quantize(rgb, hc.RefFrame(ref_a.idx, ref_a.opaque, draft), pal)
    assert (out2[sel] == 16).all() and stats2["tie_resolved_by_draft"] == 0


def _team_heavy_ref(tmp_path: Path) -> hc.RefFrame:
    rng = np.random.default_rng(7)
    idx = rng.choice(np.array([20, 30, 236, 237, 238, 239, 254], dtype=np.uint8), size=(12, 14))
    return _write_ref(tmp_path / "ref", "char/t.spr", "0000", idx, _palette())


def test_team_safe_draft_fixes_plain_scale2x_team_footprint(tmp_path: Path) -> None:
    pal = _palette()
    r = _team_heavy_ref(tmp_path)
    plain = _save(tmp_path / "plain.png", r.draft, pal, transparency=254)
    assert hc.check_image(plain, r, pal)["team_leak"] + hc.check_image(plain, r, pal)["team_missing"] > 0
    safe = _save(tmp_path / "safe.png", r.team_safe_draft, pal, transparency=254)
    assert not any(hc.check_image(safe, r, pal)[k] for k in hc.VIOLATION_KINDS)
    assert np.array_equal(r.team_safe_draft != 254, r.silhouette2x)
    # only team-related sub-pixels changed
    changed = r.team_safe_draft != r.draft
    assert not (changed & ~(r.footprint | ((r.draft >= 236) & (r.draft <= 239)))).any()


def test_quantize_round_trips_team_safe_draft_on_team_heavy_frame(tmp_path: Path) -> None:
    pal = _palette()
    r = _team_heavy_ref(tmp_path)
    out, _ = hc.quantize(_rgb(r.team_safe_draft, pal), r, pal)
    assert np.array_equal(out, r.team_safe_draft)


def test_draft_dir_writes_conforming_tree(tmp_path: Path) -> None:
    pal = _palette()
    r = _team_heavy_ref(tmp_path)
    report = hc.draft_dir(tmp_path / "ref", tmp_path / "hd", pal, GAME)
    assert report["frames"] == 1
    checked = hc.check_dir(tmp_path / "hd", tmp_path / "ref", pal)
    assert checked["pass"] and checked["violations"] == 0
    assert np.array_equal(np.array(Image.open(tmp_path / "hd/char/t.spr/0000.png")), r.team_safe_draft)


def test_quantize_rejects_wrong_size_without_resize(ref: hc.RefFrame) -> None:
    pal = _palette()
    with pytest.raises(hc.ConvertError):
        hc.quantize(np.zeros((7, 8, 3), dtype=np.uint8), ref, pal)
    with pytest.raises(hc.ConvertError):
        hc.quantize(np.zeros((6, 9, 3), dtype=np.uint8), ref, pal)


def _save(path: Path, idx: np.ndarray, pal: np.ndarray, **kw: object) -> Image.Image:
    img = Image.fromarray(idx, mode="P")
    img.putpalette(pal.ravel().tolist())
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="PNG", **kw)
    return Image.open(path)


def test_check_accepts_the_draft_and_flags_each_defect(ref: hc.RefFrame, tmp_path: Path) -> None:
    pal = _palette()
    good = _save(tmp_path / "g.png", ref.draft, pal, transparency=254)
    assert not any(hc.check_image(good, ref, pal)[k] for k in ("needs_convert", *hc.VIOLATION_KINDS))

    def counts(arr: np.ndarray, p: np.ndarray = pal, **kw: object) -> dict[str, int]:
        return hc.check_image(_save(tmp_path / "d.png", arr, p, **kw), ref, pal)

    assert counts(np.pad(ref.draft, ((0, 1), (0, 0)), constant_values=254), transparency=254)["size"] == 1
    assert counts(ref.draft[:, :-1], transparency=254)["size"] == 1
    other = pal.copy()
    other[5] = (1, 2, 3)
    assert counts(ref.draft, other, transparency=254)["palette"] == 1
    assert counts(ref.draft)["transparency"] == 1                    # no tRNS: 254 would be opaque
    shifted = ref.draft.copy()
    ys, xs = np.nonzero(ref.silhouette2x)
    shifted[ys[0], xs[0]] = 254                                       # one silhouette pixel punched out
    assert counts(shifted, transparency=254)["silhouette"] == 1
    leak = ref.draft.copy()
    ly, lx = np.nonzero(ref.silhouette2x & ~ref.footprint)
    leak[ly[0], lx[0]] = 236
    c = counts(leak, transparency=254)
    assert c["team_leak"] == 1
    miss = ref.draft.copy()
    fy, fx = np.nonzero(ref.footprint)
    miss[fy[0], fx[0]] = 20
    assert counts(miss, transparency=254)["team_missing"] == 1
    rgb = Image.fromarray(_rgb(ref.draft, pal), mode="RGB")
    assert hc.check_image(rgb, ref, pal)["needs_convert"] == 1


def test_convert_dir_writes_conforming_mirror_tree(tmp_path: Path) -> None:
    pal = _palette()
    ref_dir, rgb_dir, out = tmp_path / "ref", tmp_path / "rgb", tmp_path / "out"
    r = _write_ref(ref_dir, "char/u.spr", "0000", _ref_idx(), pal)
    (rgb_dir / "char/u.spr").mkdir(parents=True)
    Image.fromarray(_rgb(r.draft, pal), mode="RGB").save(rgb_dir / "char/u.spr/0000.png")
    _write_ref(ref_dir, "char/u.spr", "0001", _ref_idx(), pal)
    Image.fromarray(np.zeros((5, 5, 3), dtype=np.uint8), mode="RGB").save(rgb_dir / "char/u.spr/0001.png")   # wrong size
    Image.fromarray(np.zeros((6, 8, 3), dtype=np.uint8), mode="RGB").save(rgb_dir / "char/u.spr/0002.png")   # no reference
    report = hc.convert_dir(rgb_dir, ref_dir, out, pal, GAME)
    assert report["converted"] == 1 and len(report["errors"]) == 2 and not report["pass"]
    assert (out / "char/u.spr/0000.png").exists() and not list(out.rglob("000[12].png"))
    checked = hc.check_dir(out, ref_dir, pal)
    assert checked["pass"] and checked["frames"] == 1 and checked["violations"] == 0
    assert np.array_equal(np.array(Image.open(out / "char/u.spr/0000.png")), r.draft)


def test_convert_is_deterministic(tmp_path: Path) -> None:
    pal = _palette()
    ref_dir, rgb_dir = tmp_path / "ref", tmp_path / "rgb"
    r = _write_ref(ref_dir, "t/a.ytl", "0000", _ref_idx(), pal)
    (rgb_dir / "t/a.ytl").mkdir(parents=True)
    noisy = np.clip(_rgb(r.draft, pal).astype(int) + np.random.default_rng(1).integers(-8, 9, (6, 8, 3)), 0, 255)
    Image.fromarray(noisy.astype(np.uint8), mode="RGB").save(rgb_dir / "t/a.ytl/0000.png")
    reports = [json.dumps(hc.convert_dir(rgb_dir, ref_dir, tmp_path / f"o{i}", pal, GAME), sort_keys=True) for i in (1, 2)]
    assert reports[0] == reports[1]
    assert (tmp_path / "o1/t/a.ytl/0000.png").read_bytes() == (tmp_path / "o2/t/a.ytl/0000.png").read_bytes()


def test_outputs_inside_repo_game_or_inputs_are_refused(tmp_path: Path) -> None:
    pal = _palette()
    game = tmp_path / "game"
    game.mkdir()
    rgb_dir, ref_dir = tmp_path / "rgb", tmp_path / "ref"
    rgb_dir.mkdir()
    ref_dir.mkdir()
    for bad in (game / "hd", ROOT / "local" / "hd", rgb_dir / "o", ref_dir / "o", rgb_dir):
        with pytest.raises(SystemExit):
            hc.convert_dir(rgb_dir, ref_dir, bad, pal, game)


def test_panel_idx8_is_headerless_2x_bytes_and_refuses_defects(ref: hc.RefFrame, tmp_path: Path) -> None:
    pal = _palette()
    hd = tmp_path / "hd.png"
    _save(hd, ref.draft, pal, transparency=254).close()
    ref_png = tmp_path / "ref" / "char/u.spr" / "0000.png"
    out = tmp_path / "panel.idx8"
    report = hc.panel_idx8(hd, ref_png, out, pal, GAME)
    assert report["bytes"] == 8 * 6 == out.stat().st_size and report["width"] == 8 and report["height"] == 6
    assert out.read_bytes() == ref.draft.tobytes()
    bad = tmp_path / "bad.png"
    _save(bad, ref.draft[:, :-1], pal, transparency=254).close()
    with pytest.raises(SystemExit):
        hc.panel_idx8(bad, ref_png, tmp_path / "x.idx8", pal, GAME)


def test_panel_idx8_keeps_only_the_engine_panel_width(tmp_path: Path) -> None:
    """The engine reads 800 of the 831 source columns (g1_panel_fold_frame), so the pack is 1600 wide."""
    pal = _palette()
    idx = np.full((2, hc.PANEL_ENGINE_WIDTH + 5), 20, dtype=np.uint8)
    idx[0, 0] = 254
    ref = _write_ref(tmp_path / "ref", "fnt/p.spr", "0000", idx, pal)
    hd = tmp_path / "hd.png"
    _save(hd, ref.draft, pal, transparency=254).close()
    out = tmp_path / "panel.idx8"
    report = hc.panel_idx8(hd, tmp_path / "ref" / "fnt/p.spr" / "0000.png", out, pal, GAME)
    assert report["width"] == 2 * hc.PANEL_ENGINE_WIDTH and report["source_width"] == idx.shape[1]
    assert report["bytes"] == 2 * hc.PANEL_ENGINE_WIDTH * 4 == out.stat().st_size
    assert out.read_bytes() == ref.draft[:, : 2 * hc.PANEL_ENGINE_WIDTH].tobytes()


def test_cli_check_exit_codes_and_report(tmp_path: Path) -> None:
    pal_file = tmp_path / "imjin2.pal"
    pal_file.write_bytes(bytes(((i * 3) % 64, (i * 5) % 64, (i * 7) % 64)[c] for i in range(256) for c in range(3)))
    pal = hx.load_palette(pal_file)
    ref_dir, hd_dir = tmp_path / "ref", tmp_path / "hd"
    r = _write_ref(ref_dir, "char/u.spr", "0000", _ref_idx(), pal)
    _save(hd_dir / "char/u.spr/0000.png", r.draft, pal, transparency=254).close()
    cmd = ["python3", str(ROOT / "tools/g1_hd_convert.py"), "check", str(hd_dir), "--ref", str(ref_dir), "--pal", str(pal_file)]
    good = subprocess.run(cmd, capture_output=True, text=True, check=False)
    assert good.returncode == 0 and json.loads(good.stdout)["pass"] is True
    _save(hd_dir / "char/u.spr/0000.png", r.draft, pal).close()      # drop tRNS
    bad = subprocess.run(cmd, capture_output=True, text=True, check=False)
    assert bad.returncode == 1 and json.loads(bad.stdout)["violation_totals"]["transparency"] == 1


def test_check_reports_frames_without_reference(tmp_path: Path) -> None:
    pal = _palette()
    hd_dir = tmp_path / "hd"
    _save(hd_dir / "x/0000.png", np.full((2, 2), 254, dtype=np.uint8), pal, transparency=254).close()
    report = hc.check_dir(hd_dir, tmp_path / "ref", pal)
    assert report["violation_totals"]["no_reference"] == 1 and not report["pass"]


# --- pack (H-HDL1) --------------------------------------------------------------

import struct  # noqa: E402


def _rle_spr(fw: int, fh: int, frames: list[bytes]) -> bytes:
    data = bytearray(hx.SPR_FIXED_HEADER)
    struct.pack_into("<4I", data, 0, 9, fw, fh, len(frames))
    cursor = 0
    for i, frame in enumerate(frames):
        cursor += len(frame)
        if i + 1 < len(frames):
            struct.pack_into("<I", data, hx.SPR_OFFSET_TABLE + 4 * i, cursor)
    struct.pack_into("<3I", data, hx.SPR_SHEET_RECORD, cursor, 0, 0)
    return bytes(data) + b"".join(frames)


def _literal_frame(seed: int, count: int = 160, tweak_at: int | None = None) -> bytes:
    """A fully opaque literal RLE stream of ``count`` pixels (no 0xFE values)."""
    body = bytearray(((seed * 7 + i) % 200) + 1 for i in range(count))
    if tweak_at is not None:
        body[tweak_at] ^= 0x55
    return bytes(body)


def _fnv(window: bytes) -> int:
    value = 2166136261
    for byte in window[:128]:
        value = ((value ^ byte) * 16777619) & 0xFFFFFFFF
    return value


def _pack_game(tmp_path: Path) -> Path:
    game = tmp_path / "game"
    (game / "char").mkdir(parents=True)
    tail = _literal_frame(9, count=160)
    # a.spr: f0 unique, f1 same 128-byte window as f2 but a different tail (conflict), f2 last
    (game / "char" / "a.spr").write_bytes(_rle_spr(16, 10, [_literal_frame(1), _literal_frame(2), _literal_frame(2, tweak_at=150)]))
    # b.spr: repeats a.spr's f0 byte for byte -> same name, same content, two references
    (game / "char" / "b.spr").write_bytes(_rle_spr(16, 10, [_literal_frame(1), tail]))
    # c.spr: a 4x4 frame (16 bytes) as the last frame cannot give a 128-byte digest
    (game / "char" / "c.spr").write_bytes(_rle_spr(4, 4, [_literal_frame(4, count=16)]))
    return game


def _ytl_file(fw: int, fh: int, frames: list[bytes]) -> bytes:
    data = bytearray(hx.SPR_FIXED_HEADER)
    struct.pack_into("<4I", data, 0, 9, fw, fh, len(frames))
    cursor = 0
    for i, frame in enumerate(frames):
        struct.pack_into("<I", data, hx.YTL_OFFSET_TABLE + 4 * i, cursor)
        cursor += len(frame)
    struct.pack_into("<3I", data, hx.SPR_SHEET_RECORD, cursor, 0, 0)
    return bytes(data) + b"".join(frames)


def _ytl_frame(seed: int, fw: int = 16, fh: int = 8) -> bytes:
    """fh full-width scanline records (skip 0, count fw): 8 x 18 = 144 bytes >= the 128 B digest window."""
    return b"".join(bytes((0, fw)) + bytes(((seed * 11 + r * 3 + i) % 200) + 1 for i in range(fw)) for r in range(fh))


def test_pack_dry_run_names_ytl_frames_at_their_stream_start(tmp_path: Path) -> None:
    """Terrain writers 0x468C30/0x468F00 get the .ytl frame stream start (0xBF4 + 0x4C0 table entry) as source."""
    game = tmp_path / "game"
    (game / "tile" / "bright").mkdir(parents=True)
    f0, f1 = _ytl_frame(1), _ytl_frame(2)
    blob = _ytl_file(16, 8, [f0, f1])
    (game / "tile" / "bright" / "t.ytl").write_bytes(blob)
    (game / "tile" / "dark").mkdir()
    (game / "tile" / "dark" / "t.ytl").write_bytes(blob)                # same picture in a second theme: one name
    out = tmp_path / "out"
    report = hc.pack_dir(game, out, ("tile",), None, None, _palette(), dry_run=True)
    index = json.loads((out / "digest_index.json").read_text(encoding="utf-8"))["index"]
    n0, n1 = hc.pack_name(_fnv(f0), 16, 8), hc.pack_name(_fnv(f1), 16, 8)
    assert index[n0] == [["tile/bright/t.ytl", 0], ["tile/dark/t.ytl", 0]]
    assert index[n1] == [["tile/bright/t.ytl", 1], ["tile/dark/t.ytl", 1]]
    assert report["named"] == 4 and report["unique_names"] == 2 and report["conflict_names"] == 0


def test_pack_writes_ytl_hd_frames_from_the_written_pixels(tmp_path: Path) -> None:
    pal = _palette()
    game = tmp_path / "game"
    (game / "tile").mkdir(parents=True)
    # frame 0 leaves the last four pixels of every row unwritten (skip 0, count 12)
    rows = b"".join(bytes((0, 12)) + bytes(range(1, 13)) for _ in range(12))
    (game / "tile" / "t.ytl").write_bytes(_ytl_file(16, 12, [rows]))
    dec = hx.decode_ytl((game / "tile" / "t.ytl").read_bytes())
    ref_dir, hd_dir = tmp_path / "ref", tmp_path / "hd"
    stem = ref_dir / "tile/t.ytl" / "0000"
    base, doubled, _ = hx.make_products(dec.idx[0], dec.opaque[0], 0)
    hx.save_index_png(Path(f"{stem}.png"), base, pal)
    hx.save_mask_png(Path(f"{stem}_mask.png"), dec.opaque[0])
    hx.save_index_png(Path(f"{stem}_2x.png"), doubled, pal)
    _hd_for(ref_dir, hd_dir, "tile/t.ytl", "0000", pal, 41)
    out = tmp_path / "pack"
    report = hc.pack_dir(game, out, ("tile",), hd_dir, ref_dir, pal, dry_run=False)
    body = (out / hc.pack_name(_fnv(rows), 16, 12)).read_bytes()
    assert report["pack_files"] == 1 and len(body) == 4 * 16 * 12
    hd = np.frombuffer(body, dtype=np.uint8).reshape(24, 32)
    assert set(hd[:, :24].ravel()) == {41} and set(hd[:, 24:].ravel()) == {254}   # unwritten columns stay transparent


def test_pack_name_and_digest_match_the_engine_text() -> None:
    assert hc.pack_name(0xA3216FAD, 143, 57) == "ha3216fad_143x57.idx8"
    assert hc.pack_name(0xF, 1, 600) == "h0000000f_1x600.idx8"
    assert hc.pack_name(0x2AA149C7, 831, 160) == "w004663e0_h2aa149c7_831x160.idx8"   # g1_panel_asset_key text
    data = bytes(range(200))
    assert hc.fnv1a_128(data, 10) == _fnv(data[10:138])
    assert hc.fnv1a_128(data, 100) is None            # window runs past the end of the file


def test_pack_dry_run_names_frames_and_excludes_conflicts(tmp_path: Path) -> None:
    game = _pack_game(tmp_path)
    out = tmp_path / "out"
    report = hc.pack_dir(game, out, ("char",), None, None, _palette(), dry_run=True)
    index = json.loads((out / "digest_index.json").read_text(encoding="utf-8"))
    f0 = hc.pack_name(_fnv(_literal_frame(1)), 16, 10)
    f1 = hc.pack_name(_fnv(_literal_frame(2)), 16, 10)
    assert index["index"][f0] == [["char/a.spr", 0], ["char/b.spr", 0]]
    # H-HDN0: f1 and f2 share the 128-byte window but differ after it; the 160-byte streams tell them apart
    assert f1 not in index["index"] and f1 not in index["conflicts"]
    ext = index["extended"][f1]
    assert ext["length"] == 160 and sorted(ext["pictures"].values()) == [[["char/a.spr", 1]], [["char/a.spr", 2]]]
    assert {f"{hc.fnv1a_prefixes(stream, 0, [160])[160]:08x}" for stream in (_literal_frame(2), _literal_frame(2, tweak_at=150))} \
        == set(ext["pictures"])
    assert report["conflict_names"] == 0 and report["extended_names"] == 1 and report["extended_frames"] == 2
    assert report["extended_lengths"] == {"160": 1}
    assert report["tail_short"] == 1 and report["unique_names"] == 3     # c.spr's only frame is short
    assert not any(p.suffix in (".idx8", ".amb") for p in out.iterdir())


def _hd_for(ref_dir: Path, hd_dir: Path, rel: str, frame: str, pal: np.ndarray, value: int) -> None:
    ref = hc.load_ref_png(ref_dir / rel / f"{frame}.png")
    idx = np.where(ref.silhouette2x, value, 254).astype(np.uint8)
    hx.save_index_png(hd_dir / rel / f"{frame}.png", idx, pal)


def test_pack_writes_conflict_free_hd_frames_byte_for_byte(tmp_path: Path) -> None:
    pal = _palette()
    game = _pack_game(tmp_path)
    ref_dir = tmp_path / "ref"
    for rel, i in (("char/a.spr", 0), ("char/b.spr", 0)):
        dec = hx.decode_spr((game / rel).read_bytes())
        base, doubled, _ = hx.make_products(dec.idx[i], dec.opaque[i], 0)
        stem = ref_dir / rel / f"{i:04d}"
        hx.save_index_png(Path(f"{stem}.png"), base, pal)
        hx.save_mask_png(Path(f"{stem}_mask.png"), dec.opaque[i])
        hx.save_index_png(Path(f"{stem}_2x.png"), doubled, pal)
    hd_dir = tmp_path / "hd"
    _hd_for(ref_dir, hd_dir, "char/a.spr", "0000", pal, 77)
    _hd_for(ref_dir, hd_dir, "char/b.spr", "0000", pal, 77)
    hx.save_index_png(hd_dir / "char/a.spr" / "0001.png", np.full((20, 32), 5, dtype=np.uint8), pal)  # no reference
    out = tmp_path / "pack"
    report = hc.pack_dir(game, out, ("char",), hd_dir, ref_dir, pal, dry_run=False)
    name = hc.pack_name(_fnv(_literal_frame(1)), 16, 10)
    body = (out / name).read_bytes()
    assert len(body) == 4 * 16 * 10 and set(body) == {77}
    assert report["pack_files"] == 1 and report["conflict_names"] == 0 and report["no_hd"] >= 1
    assert report["extended_names"] == 1 and report["extended_files"] == 0     # f1/f2 have no HD picture: no marker, no file
    assert not list(out.glob("*.amb"))


def test_pack_rejects_output_inside_the_game(tmp_path: Path) -> None:
    game = _pack_game(tmp_path)
    with pytest.raises(SystemExit):
        hc.pack_dir(game, game / "pack", ("char",), None, None, _palette(), dry_run=True)


def test_pack_hd_for_one_picture_of_a_prefix_conflict_is_written_under_the_extended_name(tmp_path: Path) -> None:
    """a.spr f1/f2 share a name but differ in 1x picture; f1's HD goes to the marker's extended name, never the plain one."""
    pal = _palette()
    game = _pack_game(tmp_path)
    ref_dir = tmp_path / "ref"
    dec = hx.decode_spr((game / "char/a.spr").read_bytes())
    stem = ref_dir / "char/a.spr" / "0001"
    base, doubled, _ = hx.make_products(dec.idx[1], dec.opaque[1], 0)
    hx.save_index_png(Path(f"{stem}.png"), base, pal)
    hx.save_mask_png(Path(f"{stem}_mask.png"), dec.opaque[1])
    hx.save_index_png(Path(f"{stem}_2x.png"), doubled, pal)
    hd_dir = tmp_path / "hd"
    _hd_for(ref_dir, hd_dir, "char/a.spr", "0001", pal, 90)
    out = tmp_path / "pack"
    report = hc.pack_dir(game, out, ("char",), hd_dir, ref_dir, pal, dry_run=False)
    plain = hc.pack_name(_fnv(_literal_frame(2)), 16, 10)
    ext_name = hc.ext_pack_name(_fnv(_literal_frame(2)), 16, 10, 160, hc.fnv1a_prefixes(_literal_frame(2), 0, [160])[160])
    assert report["pack_files"] == 0 and report["conflict_names"] == 0 and report["extended_files"] == 1
    assert sorted(p.name for p in out.iterdir() if p.suffix != ".json") == sorted([plain[:-5] + ".amb", ext_name])
    assert (out / (plain[:-5] + ".amb")).read_bytes() == struct.pack("<I", 160)
    assert len((out / ext_name).read_bytes()) == 4 * 16 * 10 and set((out / ext_name).read_bytes()) == {90}


def test_pack_hd_pictures_that_disagree_for_one_name_are_a_conflict(tmp_path: Path) -> None:
    """Two identical 1x frames (a.spr f0, b.spr f0) given different HD pictures: no file for that name."""
    pal = _palette()
    game = _pack_game(tmp_path)
    ref_dir = tmp_path / "ref"
    hd_dir = tmp_path / "hd"
    for rel, value in (("char/a.spr", 11), ("char/b.spr", 12)):
        dec = hx.decode_spr((game / rel).read_bytes())
        stem = ref_dir / rel / "0000"
        base, doubled, _ = hx.make_products(dec.idx[0], dec.opaque[0], 0)
        hx.save_index_png(Path(f"{stem}.png"), base, pal)
        hx.save_mask_png(Path(f"{stem}_mask.png"), dec.opaque[0])
        hx.save_index_png(Path(f"{stem}_2x.png"), doubled, pal)
        _hd_for(ref_dir, hd_dir, rel, "0000", pal, value)
    out = tmp_path / "pack"
    report = hc.pack_dir(game, out, ("char",), hd_dir, ref_dir, pal, dry_run=False)
    assert report["pack_files"] == 0 and report["conflict_names"] == 1 and report["extended_names"] == 1   # f0 name; f1/f2 extended
    assert not list(out.glob("*.amb"))                                  # no HD picture for f1/f2: no marker


def test_pack_panel_frame_uses_the_panel_name_and_keeps_800_source_columns(tmp_path: Path) -> None:
    pal = _palette()
    game = tmp_path / "game"
    (game / "fnt").mkdir(parents=True)
    fw, fh = 831, 2
    frame = bytes(((i * 3) % 200) + 1 for i in range(fw * fh))   # >= 128 literal bytes, no 0xFE
    (game / "fnt" / "pannelx.spr").write_bytes(_rle_spr(fw, fh, [frame]))
    dec = hx.decode_spr((game / "fnt/pannelx.spr").read_bytes())
    ref_dir, hd_dir = tmp_path / "ref", tmp_path / "hd"
    stem = ref_dir / "fnt/pannelx.spr" / "0000"
    base, doubled, _ = hx.make_products(dec.idx[0], dec.opaque[0], 0)
    hx.save_index_png(Path(f"{stem}.png"), base, pal)
    hx.save_mask_png(Path(f"{stem}_mask.png"), dec.opaque[0])
    hx.save_index_png(Path(f"{stem}_2x.png"), doubled, pal)
    _hd_for(ref_dir, hd_dir, "fnt/pannelx.spr", "0000", pal, 33)
    out = tmp_path / "pack"
    report = hc.pack_dir(game, out, ("fnt",), hd_dir, ref_dir, pal, dry_run=False)
    name = f"w004663e0_h{_fnv(frame):08x}_831x2.idx8"
    assert report["pack_files"] == 1 and len((out / name).read_bytes()) == 800 * 2 * 4   # 1600 x 4 HD pixels


# --- whole-screen raw pictures (H-HDF0) ------------------------------------------

def _raw_spr(fw: int, fh: int, frames: list[bytes], extra: int = 0) -> bytes:
    header = struct.pack("<4I", 9, fw, fh, len(frames)).ljust(hx.SPR_FIXED_HEADER, b"\0")
    return header + b"".join(frames) + b"\0" * extra


def _screen_pal() -> np.ndarray:
    pal = np.zeros((256, 3), dtype=np.uint8)
    for i in range(256):
        pal[i] = (i, 255 - i, (i * 3) % 256)
    return pal


def test_fullscreen_name_and_digest_match_the_engine_menu_hash(tmp_path: Path) -> None:
    pixels = bytes((i * 5 + 1) % 200 for i in range(8 * 6))
    spr = tmp_path / "in" / "title.spr"
    spr.parent.mkdir()
    spr.write_bytes(_raw_spr(8, 6, [pixels]))
    report = hc.fullscreen_pack(spr, None, tmp_path / "out", _screen_pal(), GAME)
    value = 2166136261
    for byte in pixels:                      # transfer_block_copy_to_screen: hash ^= src[i]; hash *= 16777619u
        value = ((value ^ byte) * 16777619) & 0xFFFFFFFF
    name = f"f{value:08x}_8x6.idx8"
    assert report["frames"][0]["name"] == name == hc.fullscreen_name(value, 8, 6)
    assert (tmp_path / "out" / name).stat().st_size == 16 * 12 == report["frames"][0]["bytes"]


def test_fullscreen_rgb_input_quantizes_exactly_and_never_writes_the_key(tmp_path: Path) -> None:
    pal = _screen_pal()
    pal[254] = (7, 7, 7)                     # the key's colour is a perfect match for these pixels; it must still lose
    idx = np.full((6, 8), 254, dtype=np.uint8)
    idx[:3] = 20
    idx[3:] = 21
    spr = tmp_path / "in" / "s.spr"
    spr.parent.mkdir()
    spr.write_bytes(_raw_spr(8, 6, [idx.tobytes()]))
    hd = np.repeat(np.repeat(pal[idx], 2, axis=0), 2, axis=1)
    hd[0:2, 0:2] = (7, 7, 7)                 # an upscaled pixel exactly the key's colour
    png = tmp_path / "hd.png"
    Image.fromarray(hd, "RGB").save(png)
    report = hc.fullscreen_pack(spr, png, tmp_path / "out", pal, GAME)
    body = (tmp_path / "out" / report["frames"][0]["name"]).read_bytes()
    assert 254 not in body and report["frames"][0]["source"] == "rgb"
    others = [i for i in range(256) if i != 254]
    nearest = others[int(((pal[others].astype(int) - (7, 7, 7)) ** 2).sum(axis=1).argmin())]
    assert body[0] == nearest and set(body) == {20, 21, nearest}
    assert body[-1] == 21 and body[2 * 8 + 5] == 20


def test_fullscreen_bicubic_stand_in_of_a_flat_frame_is_the_flat_index(tmp_path: Path) -> None:
    pal = _screen_pal()
    spr = tmp_path / "in" / "s.spr"
    spr.parent.mkdir()
    spr.write_bytes(_raw_spr(8, 6, [bytes([33]) * 48]))
    report = hc.fullscreen_pack(spr, None, tmp_path / "out", pal, GAME)
    assert (tmp_path / "out" / report["frames"][0]["name"]).read_bytes() == bytes([33]) * (16 * 12)


def test_fullscreen_refuses_rle_sized_files_wrong_rgb_size_and_outputs_in_the_game(tmp_path: Path) -> None:
    pal = _screen_pal()
    spr = tmp_path / "in" / "s.spr"
    spr.parent.mkdir()
    spr.write_bytes(_raw_spr(8, 6, [bytes([33]) * 48], extra=3))      # trailing bytes: not a plain raw picture
    with pytest.raises(SystemExit):
        hc.fullscreen_pack(spr, None, tmp_path / "out", pal, GAME)
    spr.write_bytes(_raw_spr(8, 6, [bytes([33]) * 48]))
    small = tmp_path / "small.png"
    Image.fromarray(np.zeros((6, 8, 3), dtype=np.uint8), "RGB").save(small)
    with pytest.raises(SystemExit):
        hc.fullscreen_pack(spr, small, tmp_path / "out", pal, GAME)
    with pytest.raises(SystemExit):
        hc.fullscreen_pack(spr, None, ROOT / "x_out", pal, GAME)


# --- unframed single-picture RLE (H-HDB0: the HUD logo fnt/imjin2plus.spr, frame count 0) ----------------------

def _unframed_spr(fw: int, fh: int, stream: bytes, frames: int = 0) -> bytes:
    return struct.pack("<4I", 9, fw, fh, frames).ljust(hx.SPR_FIXED_HEADER, b"\0") + stream


def _logo_stream() -> bytes:
    """20x8: row 0 skip 20 (a full row), row 1 skip 3 + 17 pixels, row 2 FE 0 (skip 0) + 20 pixels, rows 3..7 plain."""
    stream = bytes([hx.RLE_MARKER, 20]) + bytes([hx.RLE_MARKER, 3]) + bytes(range(30, 47))
    stream += bytes([hx.RLE_MARKER, 0]) + bytes(range(50, 70))
    for row in range(5):
        stream += bytes(60 + row for _ in range(20))
    return stream


def test_logo_reads_the_stream_like_the_engine_and_names_it_by_the_first_128_bytes(tmp_path: Path) -> None:
    stream = _logo_stream()
    spr = tmp_path / "in" / "logo.spr"
    spr.parent.mkdir()
    spr.write_bytes(_unframed_spr(20, 8, stream))
    fw, fh, idx, opaque = hc.decode_unframed_rle(spr.read_bytes())
    assert (fw, fh) == (20, 8) and not opaque[0].any() and not opaque[1, :3].any() and opaque[1, 3:].all()
    assert idx[1, 3] == 30 and idx[2, 0] == 50 and opaque[2].all()        # FE 0 skips zero columns, it is not a pixel
    report = hc.logo_pack(spr, None, tmp_path / "out", _screen_pal(), GAME)
    value = 2166136261
    for byte in stream[:128]:
        value = ((value ^ byte) * 16777619) & 0xFFFFFFFF
    assert report["name"] == f"h{value:08x}_20x8.idx8" and report["opaque_pixels"] == int(opaque.sum())
    body = (tmp_path / "out" / report["name"]).read_bytes()
    assert len(body) == 40 * 16 and body[:40] == bytes([hc.TRANSPARENT]) * 40   # silhouette: row 0 is all key
    assert body[2 * 40 + 6] != hc.TRANSPARENT and body[2 * 40 + 5] == hc.TRANSPARENT


def test_logo_refuses_framed_files_unconsumed_streams_and_short_streams(tmp_path: Path) -> None:
    pal = _screen_pal()
    spr = tmp_path / "in" / "logo.spr"
    spr.parent.mkdir()
    for blob in (_unframed_spr(20, 8, _logo_stream(), frames=1),                      # a framed file is the ordinary path
                 _unframed_spr(20, 8, _logo_stream() + b"\0"),                          # bytes left after the last row
                 _unframed_spr(20, 8, _logo_stream()[:-3]),                            # ends inside the last row
                 _unframed_spr(4, 2, bytes(8))):                                      # shorter than the 128 digest bytes
        spr.write_bytes(blob)
        with pytest.raises(SystemExit):
            hc.logo_pack(spr, None, tmp_path / "out", pal, GAME)


# --- screen palette directory (H-HDPAL) ---------------------------------------------

def _pal_file(tmp_path: Path, seed: int) -> tuple[Path, str]:
    """6-bit .pal file plus the pal8 the engine computes: FNV-1a over the R,G,B bytes of 256 PALETTEENTRYs (value << 2)."""
    raw = bytes((i * seed + i // 3) % 64 for i in range(768))
    path = tmp_path / f"p{seed}.pal"
    path.write_bytes(raw)
    value = 2166136261
    for entry in range(256):
        for channel in range(3):
            value = ((value ^ (raw[entry * 3 + channel] << 2)) * 16777619) & 0xFFFFFFFF
    return path, f"{value:08x}"


def test_fullscreen_output_goes_into_the_directory_of_the_given_palette(tmp_path: Path) -> None:
    spr = tmp_path / "in" / "title.spr"
    spr.parent.mkdir()
    spr.write_bytes(_raw_spr(8, 6, [bytes((i * 5 + 1) % 200 for i in range(48))]))
    out = tmp_path / "pack"
    for seed in (5, 7):
        pal, pal8 = _pal_file(tmp_path, seed)
        assert hc.main(["fullscreen", "--pal", str(pal), "--game", str(GAME), "--out", str(out), str(spr)]) == 0
        assert len(list((out / pal8).glob("f*_8x6.idx8"))) == 1
    assert len(list(out.iterdir())) == 2 and not list(out.glob("*.idx8"))     # no frame in the pack root


def test_pack_and_fullscreen_require_the_palette_and_the_pal8_depends_on_it(tmp_path: Path) -> None:
    for argv in (["pack", "--out", str(tmp_path / "o"), "--dry-run"],
                 ["fullscreen", "--out", str(tmp_path / "o"), str(tmp_path / "x.spr")]):
        with pytest.raises(SystemExit) as error:
            hc.main(argv)
        assert error.value.code == 2
    (first, a), (second, b) = _pal_file(tmp_path, 5), _pal_file(tmp_path, 7)
    assert a != b and hc.palette_pal8(hx.load_palette(first)) == a and hc.palette_pal8(hx.load_palette(second)) == b


# --- extended pack names (H-HDN0) --------------------------------------------------

def test_extended_candidates_start_at_256_double_and_end_at_the_shortest_stream() -> None:
    assert hc.ext_candidates(128) == [] and hc.ext_candidates(129) == [129] and hc.ext_candidates(160) == [160]
    assert hc.ext_candidates(256) == [256] and hc.ext_candidates(300) == [256, 300]
    assert hc.ext_candidates(1024) == [256, 512, 1024] and hc.ext_candidates(1500) == [256, 512, 1024, 1500]
    assert hc.ext_candidates(70000)[-1] == 65536 and hc.ext_candidates(70000)[:2] == [256, 512]


def test_stream_ranges_run_to_the_next_distinct_start_or_the_end_of_the_file() -> None:
    assert hc.stream_ranges([300, 100, 100, 200], 450) == {100: 100, 200: 100, 300: 150}


def test_prefix_hash_is_fnv1a_of_exactly_the_requested_bytes() -> None:
    data = bytes(range(256)) * 2
    got = hc.fnv1a_prefixes(data, 10, [129, 200, 300])
    for length, value in got.items():
        assert value == hc.fnv1a_all(data[10:10 + length])
    assert sorted(got) == [129, 200, 300]


def test_extended_names_match_the_engine_header_text(tmp_path: Path) -> None:
    program = tmp_path / "names.c"
    program.write_text(r"""#include <stdio.h>
#include "g1_hd_pack.h"
int main(void)
{
    char name[64];
    if (!g1_hd_pack_marker_name(name, sizeof(name), 0xA3216FADu, 143u, 57u)) return 1;
    puts(name);
    if (!g1_hd_pack_ext_name(name, sizeof(name), 0xA3216FADu, 143u, 57u, 1024u, 0x0000BEEFu)) return 2;
    puts(name);
    if (!g1_hd_pack_ext_name(name, sizeof(name), 0x0000000Fu, 800u, 600u, 65536u, 0xFFFFFFFFu)) return 3;
    puts(name);
    if (g1_hd_pack_ext_name(name, sizeof(name), 1u, 5u, 5u, 128u, 0u)) return 4;
    if (g1_hd_pack_ext_name(name, sizeof(name), 1u, 5u, 5u, 65537u, 0u)) return 5;
    return 0;
}
""", encoding="utf-8")
    exe = tmp_path / "names"
    built = subprocess.run(["gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-I", str(ROOT / "tools/inmm_stub"), str(program), "-o", str(exe)],
                           capture_output=True, text=True, check=False)
    assert built.returncode == 0, built.stderr
    ran = subprocess.run([str(exe)], capture_output=True, text=True, check=False)
    assert ran.returncode == 0, ran.returncode
    assert ran.stdout.split() == [hc.marker_name(0xA3216FAD, 143, 57), hc.ext_pack_name(0xA3216FAD, 143, 57, 1024, 0xBEEF),
                                  hc.ext_pack_name(0xF, 800, 600, 65536, 0xFFFFFFFF)]
    assert hc.marker_name(0xA3216FAD, 143, 57) == "ha3216fad_143x57.amb"
    assert hc.ext_pack_name(0xA3216FAD, 143, 57, 1024, 0xBEEF) == "ha3216fad_143x57_1024_0000beef.idx8"


def _same_window_game(tmp_path: Path, tweak_at: int, count: int = 500) -> Path:
    """Two 25x20 frames (500 B each) in one file whose first ``tweak_at`` bytes agree: the digest window (128 B) always does."""
    game = tmp_path / "game"
    (game / "char").mkdir(parents=True)
    frames = [_literal_frame(5, count=count), _literal_frame(5, count=count, tweak_at=tweak_at)]
    (game / "char" / "w.spr").write_bytes(_rle_spr(25, 20, frames))
    return game


def test_extended_length_is_the_smallest_candidate_that_separates_every_picture(tmp_path: Path) -> None:
    out = tmp_path / "out"
    for tweak_at, expected in ((130, 256), (300, 500), (480, 500)):         # 256 sees byte 130 only; 300/480 need the whole 500
        game = _same_window_game(tmp_path / f"g{tweak_at}", tweak_at)
        report = hc.pack_dir(game, out / str(tweak_at), ("char",), None, None, _palette(), dry_run=True)
        index = json.loads((out / str(tweak_at) / "digest_index.json").read_text(encoding="utf-8"))
        ((name, ext),) = index["extended"].items()
        assert ext["length"] == expected and len(ext["pictures"]) == 2 and not index["conflicts"], tweak_at
        assert name == hc.pack_name(_fnv(_literal_frame(5, count=500)), 25, 20) and report["extended_lengths"] == {str(expected): 1}


def test_a_prefix_shorter_than_the_digest_window_leaves_the_conflict(tmp_path: Path) -> None:
    """Frames at most 128 bytes apart have no usable prefix: the names keep their old conflict handling."""
    names = {"hAAAAAAAA_4x4.idx8": {"sources": {"p1": [["x.spr", 0]], "p2": [["x.spr", 1]]}, "hd": {}, "refs": []}}
    members = {"hAAAAAAAA_4x4.idx8": [("x.spr", 0, 0, 100, "p1"), ("x.spr", 1, 100, 400, "p2")]}
    assert hc._split_by_prefix(tmp_path, names, members) == {}


def test_pictures_that_no_candidate_length_tells_apart_stay_a_conflict(tmp_path: Path) -> None:
    (tmp_path / "x.spr").write_bytes(bytes(1200))                                 # identical bytes under two picture labels
    names = {"hAAAAAAAA_4x4.idx8": {"sources": {"p1": [["x.spr", 0]], "p2": [["x.spr", 1]]}, "hd": {}, "refs": []}}
    members = {"hAAAAAAAA_4x4.idx8": [("x.spr", 0, 0, 300, "p1"), ("x.spr", 1, 0, 300, "p2")]}
    assert hc._split_by_prefix(tmp_path, names, members) == {}


def _three_streams(tmp_path: Path, tweak_b: int, tweak_c: int) -> tuple[dict, dict]:
    """Three 600 B streams that agree on their first 255 bytes; A differs from B and C at byte 255, B and C at ``tweak_b``/``tweak_c``."""
    base = bytes((i * 7 + 3) % 251 for i in range(600))
    a, b, c = bytearray(base), bytearray(base), bytearray(base)
    a[255] ^= 0x55
    b[tweak_b] ^= 0x11
    c[tweak_c] ^= 0x22
    (tmp_path / "x.spr").write_bytes(bytes(a) + bytes(b) + bytes(c))
    name = "hAAAAAAAA_4x4.idx8"
    names = {name: {"sources": {"p1": [["x.spr", 0]], "p2": [["x.spr", 1]], "p3": [["x.spr", 2]]}, "hd": {}, "refs": []}}
    members = {name: [("x.spr", 0, 0, 600, "p1"), ("x.spr", 1, 600, 600, "p2"), ("x.spr", 2, 1200, 600, "p3")]}
    return names, members


def test_a_prefix_that_tells_only_some_pictures_apart_is_skipped_for_the_one_that_tells_all(tmp_path: Path) -> None:
    """H-HDB2 B2-0 (lap1193 survivor p2): at 256 A is alone but B and C share a hash; 512 separates all three."""
    names, members = _three_streams(tmp_path, tweak_b=300, tweak_c=400)
    ((name, (length, groups)),) = hc._split_by_prefix(tmp_path, names, members).items()
    assert length == 512 and sorted(picture for picture, _ in groups.values()) == ["p1", "p2", "p3"]
    assert all(len(frames) == 1 for _, frames in groups.values())


def test_a_name_that_every_prefix_leaves_ambiguous_for_two_pictures_stays_a_conflict(tmp_path: Path) -> None:
    """H-HDB2 B2-0 (lap1193 survivor p2): B and C agree through the whole 600 B range, so even a lone A is no split."""
    names, members = _three_streams(tmp_path, tweak_b=599, tweak_c=599)
    (tmp_path / "x.spr").write_bytes(
        (tmp_path / "x.spr").read_bytes()[:1200] + (tmp_path / "x.spr").read_bytes()[600:1200])    # C = a copy of B
    assert hc._split_by_prefix(tmp_path, names, members) == {}


def test_panel_names_are_never_extended(tmp_path: Path) -> None:
    (tmp_path / "x.spr").write_bytes(bytes(range(256)) * 8)
    names = {"w004663e0_hAAAAAAAA_831x4.idx8": {"sources": {"p1": [["x.spr", 0]], "p2": [["x.spr", 1]]}, "hd": {}, "refs": []}}
    members = {"w004663e0_hAAAAAAAA_831x4.idx8": [("x.spr", 0, 0, 500, "p1"), ("x.spr", 1, 500, 500, "p2")]}
    assert hc._split_by_prefix(tmp_path, names, members) == {}


def test_extended_pictures_with_different_hd_for_one_prefix_are_not_written(tmp_path: Path) -> None:
    """The same 1x frame twice (a.spr f0 and a copy in b.spr) given different HD pictures: listed in hd_conflicts, no file, no marker."""
    pal = _palette()
    game = tmp_path / "game"
    (game / "char").mkdir(parents=True)
    f1, f2 = _literal_frame(2), _literal_frame(2, tweak_at=150)
    (game / "char" / "a.spr").write_bytes(_rle_spr(16, 10, [f1, f2]))
    (game / "char" / "b.spr").write_bytes(_rle_spr(16, 10, [f2, f1]))
    ref_dir, hd_dir = tmp_path / "ref", tmp_path / "hd"
    for rel, value in (("char/a.spr", 31), ("char/b.spr", 32)):
        dec = hx.decode_spr((game / rel).read_bytes())
        for i in (0, 1):
            stem = ref_dir / rel / f"{i:04d}"
            base, doubled, _ = hx.make_products(dec.idx[i], dec.opaque[i], 0)
            hx.save_index_png(Path(f"{stem}.png"), base, pal)
            hx.save_mask_png(Path(f"{stem}_mask.png"), dec.opaque[i])
            hx.save_index_png(Path(f"{stem}_2x.png"), doubled, pal)
            _hd_for(ref_dir, hd_dir, rel, f"{i:04d}", pal, value)
    out = tmp_path / "pack"
    report = hc.pack_dir(game, out, ("char",), hd_dir, ref_dir, pal, dry_run=False)
    index = json.loads((out / "digest_index.json").read_text(encoding="utf-8"))
    ((_, ext),) = index["extended"].items()
    assert len(ext["hd_conflicts"]) == 2 and report["extended_files"] == 0 and not list(out.glob("*.amb"))
    assert not any(p.suffix == ".idx8" for p in out.iterdir())
