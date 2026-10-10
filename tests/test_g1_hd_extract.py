"""H-HDX1 original picture extractor: synthetic format vectors plus pinned real-file checks."""

from __future__ import annotations

import json
import struct
import subprocess
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from tools import g1_hd_extract as hx

ROOT = Path(__file__).resolve().parents[1]
GAME = hx.DEFAULT_GAME


def _palette_bytes() -> bytes:
    return bytes(((i * 3) % 64, (i * 5) % 64, (i * 7) % 64)[c] for i in range(256) for c in range(3))


def _spr(fw: int, fh: int, frames: list[bytes], *, raw: bool = False, sheet: tuple[int, int] | None = None) -> bytes:
    """Build a .spr: header, offset table (0x4C4), sheet record (0xBC8), pixel data (0xBF4)."""
    data = bytearray(hx.SPR_FIXED_HEADER)
    struct.pack_into("<4I", data, 0, 9, fw, fh, len(frames))
    cursor = 0
    for i, frame in enumerate(frames):
        cursor += len(frame)
        if i + 1 < len(frames):
            struct.pack_into("<I", data, hx.SPR_OFFSET_TABLE + 4 * i, cursor)
    sw, sh = sheet if sheet else ((fw * len(frames), fh) if raw else (0, 0))
    struct.pack_into("<3I", data, hx.SPR_SHEET_RECORD, cursor, sw, sh)
    return bytes(data) + b"".join(frames)


def _ytl(fw: int, fh: int, frames: list[bytes]) -> bytes:
    data = bytearray(hx.SPR_FIXED_HEADER)
    struct.pack_into("<4I", data, 0, 9, fw, fh, len(frames))
    cursor = 0
    for i, frame in enumerate(frames):
        struct.pack_into("<I", data, hx.YTL_OFFSET_TABLE + 4 * i, cursor)
        cursor += len(frame)
    struct.pack_into("<3I", data, hx.SPR_SHEET_RECORD, cursor, 0, 0)
    return bytes(data) + b"".join(frames)


def test_rle_runs_literals_and_escaped_fe() -> None:
    # 4x2 frame: [T T 7 8] [FE-literal 9 T T]
    frame = bytes([0xFE, 2, 7, 8, 0xFE, 0, 9, 0xFE, 2])
    dec = hx.decode_spr(_spr(4, 2, [frame]))
    assert dec.kind == "rle" and dec.exact == [True] and dec.mask_source == "rle_runs"
    assert dec.opaque[0].tolist() == [[0, 0, 1, 1], [1, 1, 0, 0]]
    assert dec.idx[0][0, 2:].tolist() == [7, 8]
    assert dec.idx[0][1, :2].tolist() == [0xFE, 9]
    assert dec.sheet_record == "zero_or_undersized:0x0"


def test_rle_frames_are_independent_streams_not_a_sheet_grid() -> None:
    f0 = bytes([1, 2, 3, 4])           # 2x2 all literal
    f1 = bytes([0xFE, 4])              # 2x2 fully transparent
    dec = hx.decode_spr(_spr(2, 2, [f0, f1], sheet=(4, 2)))
    assert dec.idx[0].tolist() == [[1, 2], [3, 4]]
    assert not dec.opaque[1].any() and dec.exact == [True, True]


def test_rle_frame_not_exactly_consumed_is_flagged() -> None:
    dec = hx.decode_spr(_spr(2, 2, [bytes([1, 2, 3])]))   # one pixel short
    assert dec.exact == [False]
    assert any("not exactly consumed" in w for w in dec.warnings)


def test_raw_spr_uses_consecutive_blocks_and_all_opaque() -> None:
    f0, f1 = bytes([1, 2, 3, 0xFE]), bytes([5, 6, 7, 8])
    dec = hx.decode_spr(_spr(2, 2, [f0, f1], raw=True))
    assert dec.kind == "raw" and dec.mask_source == "raw_all_opaque"
    assert dec.idx[1].tolist() == [[5, 6], [7, 8]]
    assert dec.opaque[0].all() and dec.idx[0][1, 1] == 0xFE
    assert any("all opaque" in w for w in dec.warnings)


def test_ytl_scanline_records_and_chain_exactness() -> None:
    f0 = bytes([1, 2, 5, 6]) + bytes([4, 0]) + bytes([3, 1, 9])
    f1 = bytes([0, 4, 1, 2, 3, 4]) * 3
    dec = hx.decode_ytl(_ytl(4, 3, [f0, f1]))
    assert dec.kind == "ytl" and dec.exact == [True, True]
    assert dec.opaque[0].tolist() == [[0, 1, 1, 0], [0, 0, 0, 0], [0, 0, 0, 1]]
    assert dec.idx[0][2, 3] == 9 and dec.opaque[1].all()


def test_ytl_overlong_record_marks_frame_inexact() -> None:
    dec = hx.decode_ytl(_ytl(2, 1, [bytes([1, 5, 1, 2, 3, 4, 5])]))
    assert dec.exact == [False]


def test_ytl_rle_encoders_round_trip_exact_bytes() -> None:
    f0 = bytes([1, 2, 5, 6]) + bytes([4, 0]) + bytes([3, 1, 9])
    dec = hx.decode_ytl(_ytl(4, 3, [f0]))
    assert hx.ytl_encode_frame(dec.idx[0], dec.opaque[0]) == f0
    rle = bytes([0xFE, 2, 7, 8, 0xFE, 0, 9, 0xFE, 2])
    dec2 = hx.decode_spr(_spr(4, 2, [rle]))
    assert hx.rle_encode(dec2.idx[0], dec2.opaque[0]) == rle


def test_rle_long_transparent_run_is_split_at_255() -> None:
    idx = np.zeros((1, 300), dtype=np.uint8)
    opq = np.zeros((1, 300), dtype=bool)
    assert hx.rle_encode(idx, opq) == bytes([0xFE, 255, 0xFE, 45])


def test_bmp_8bit_bottom_up_rows_and_stride_padding() -> None:
    w, h = 3, 2
    rows = [bytes([1, 2, 3, 0]), bytes([4, 5, 6, 0])]   # stride 4; bottom row first
    palette = bytes(range(256)) * 4
    hdr = struct.pack("<IiiHHIIiiII", 40, w, h, 1, 8, 0, 8, 2834, 2834, 256, 0)
    pixel_off = 14 + 40 + 1024
    data = b"BM" + struct.pack("<IHHI", pixel_off + 8, 0, 0, pixel_off) + hdr + palette + b"".join(rows)
    dec, pal = hx.decode_bmp(data)
    assert dec.idx[0].tolist() == [[4, 5, 6], [1, 2, 3]] and len(pal) == 1024
    assert dec.opaque[0].all() and dec.mask_source == "bmp_colorkey_fe"     # no 254 in this image
    with pytest.raises(hx.AssetError):
        hx.decode_bmp(data[:28] + struct.pack("<H", 24) + data[30:])


def test_bad_headers_are_classified_not_raised_as_other_errors() -> None:
    with pytest.raises(hx.AssetError):
        hx.decode_spr(b"\x00" * 100)
    bad = bytearray(_spr(2, 2, [bytes([1, 2, 3, 4])]))
    struct.pack_into("<I", bad, 12, 0)
    with pytest.raises(hx.AssetError):
        hx.decode_spr(bytes(bad))
    with pytest.raises(hx.AssetError):
        hx.decode_ytl(_ytl(2, 2, [b"\x00\x00\x00\x00"] * 2)[:100])


def test_palette_6bit_x4_and_fe_replacement_excludes_254(tmp_path: Path) -> None:
    path = tmp_path / "imjin2.pal"
    path.write_bytes(_palette_bytes())
    pal = hx.load_palette(path)
    assert pal[1].tolist() == [12, 20, 28] and pal.dtype == np.uint8
    repl = hx.fe_replacement(pal)
    assert repl != hx.TRANSPARENT
    path.write_bytes(bytes([64]) + bytes(767))
    with pytest.raises(hx.AssetError):
        hx.load_palette(path)


def test_scale2x_matches_engine_c_kernel(tmp_path: Path) -> None:
    driver = tmp_path / "driver.c"
    driver.write_text(
        r'''#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include "g1_scale2x_core.h"
int main(void) {
    unsigned w, h; if (scanf("%u %u", &w, &h) != 2) return 2;
    uint8_t *s = malloc(w*h), *m = malloc(w*h), *d = malloc(w*h*4);
    for (unsigned i = 0; i < w*h; ++i) { unsigned v; scanf("%u", &v); s[i] = (uint8_t)v; }
    for (unsigned i = 0; i < w*h; ++i) { unsigned v; scanf("%u", &v); m[i] = (uint8_t)v; }
    if (!g1_scale2x_build_masked(s, w, m, w, w, h, d, w*2)) return 3;
    for (unsigned i = 0; i < w*h*4; ++i) printf("%u ", d[i]);
    return 0;
}
''',
        encoding="utf-8",
    )
    binary = tmp_path / "driver"
    built = subprocess.run(
        ["gcc", "-std=c11", "-Wall", "-Werror", "-I", str(ROOT / "tools/inmm_stub"), str(driver), "-o", str(binary)],
        capture_output=True, text=True, check=False,
    )
    assert built.returncode == 0, built.stderr
    rng = np.random.default_rng(1157)
    for trial in range(40):
        h, w = int(rng.integers(1, 9)), int(rng.integers(1, 9))
        src = rng.integers(0, 4, size=(h, w), dtype=np.uint8)
        wr = (rng.random((h, w)) < (0.3 + 0.6 * (trial % 3) / 2)).astype(bool)
        text = f"{w} {h} " + " ".join(map(str, src.ravel())) + " " + " ".join(str(int(v)) for v in wr.ravel())
        run = subprocess.run([str(binary)], input=text, capture_output=True, text=True, check=True)
        expected = np.array(run.stdout.split(), dtype=np.uint8).reshape(h * 2, w * 2)
        assert np.array_equal(hx.scale2x_masked(src, wr), expected)


def test_products_silhouette_2x2_and_no_opaque_254() -> None:
    idx = np.array([[0xFE, 5, 5], [7, 0xFE, 5], [7, 7, 0]], dtype=np.uint8)
    opq = np.array([[1, 1, 0], [1, 1, 1], [0, 1, 1]], dtype=bool)
    base, doubled, remapped = hx.make_products(idx, opq, 33)
    assert remapped == 2 and base[0, 0] == 33 and base[0, 2] == 254
    assert doubled.shape == (6, 6)
    mask2 = np.repeat(np.repeat(opq, 2, axis=0), 2, axis=1)
    assert np.array_equal(doubled != 254, mask2)


def test_png_outputs_have_exact_size_palette_and_transparency(tmp_path: Path) -> None:
    pal_path = tmp_path / "p.pal"
    pal_path.write_bytes(_palette_bytes())
    pal = hx.load_palette(pal_path)
    arr = np.full((3, 4), 254, dtype=np.uint8)
    arr[1, 1] = 9
    hx.save_index_png(tmp_path / "a.png", arr, pal)
    hx.save_mask_png(tmp_path / "a_mask.png", arr != 254)
    img = Image.open(tmp_path / "a.png")
    assert img.mode == "P" and img.size == (4, 3)
    assert img.getpalette()[:768] == pal.ravel().tolist()
    assert np.array_equal(np.array(img), arr) and img.info["transparency"] is not None
    mask = Image.open(tmp_path / "a_mask.png")
    assert mask.mode == "1" and int(np.array(mask).sum()) == 1


def _make_game(tmp_path: Path) -> Path:
    game = tmp_path / "game"
    (game / "pal").mkdir(parents=True)
    (game / "pal" / "imjin2.pal").write_bytes(_palette_bytes())
    (game / "char").mkdir()
    (game / "char" / "unit.spr").write_bytes(
        _spr(4, 2, [bytes([0xFE, 2, 7, 8, 0xFE, 0, 9, 0xFE, 2]), bytes([1, 2, 3, 4, 5, 6, 7, 8])]))
    (game / "tile").mkdir()
    (game / "tile" / "t.ytl").write_bytes(_ytl(4, 3, [bytes([1, 2, 5, 6, 0, 0, 3, 1, 9])]))
    (game / "other").mkdir()
    (game / "other" / "bad.spr").write_bytes(b"short")
    (game / "other" / "keep.spr").write_bytes(_spr(2, 2, [bytes([1, 2, 3, 4])]))
    return game


def test_extract_writes_triplets_manifest_and_leaves_source_untouched(tmp_path: Path) -> None:
    game = _make_game(tmp_path)
    out = tmp_path / "out"
    manifest = hx.extract(game, out, ("char", "tile"), (), False, ROOT)
    assert manifest["source_unchanged"] and manifest["summary"] == {"rle": 2, "ytl": 1, "unsupported": 1}
    assert manifest["unclassified"] == [{"path": "other/bad.spr", "reason": "shorter than the 0xBF4 header"}]
    for stem in ("0000", "0001"):
        base = out / "char" / "unit.spr" / stem
        assert (base.with_suffix(".png")).exists() and Path(f"{base}_mask.png").exists()
        assert Image.open(f"{base}_2x.png").size == (8, 4)
    assert not (out / "other").exists()                       # not an image dir: census only
    per_file = json.loads((out / "char" / "unit.spr" / "manifest.json").read_text(encoding="utf-8"))
    assert per_file["frames"][0]["literal_fe"] == 1 and per_file["frames"][0]["exact"] is True


def test_extract_is_deterministic(tmp_path: Path) -> None:
    game = _make_game(tmp_path)
    hx.extract(game, tmp_path / "o1", ("char", "tile"), (), False, ROOT)
    hx.extract(game, tmp_path / "o2", ("char", "tile"), (), False, ROOT)
    first = sorted(p.relative_to(tmp_path / "o1") for p in (tmp_path / "o1").rglob("*") if p.is_file())
    second = sorted(p.relative_to(tmp_path / "o2") for p in (tmp_path / "o2").rglob("*") if p.is_file())
    assert first == second and first
    for rel in first:
        assert (tmp_path / "o1" / rel).read_bytes() == (tmp_path / "o2" / rel).read_bytes()


def test_extract_rejects_output_inside_game_or_repo(tmp_path: Path) -> None:
    game = _make_game(tmp_path)
    with pytest.raises(SystemExit):
        hx.extract(game, game / "hd", ("char",), (), False, ROOT)
    with pytest.raises(SystemExit):
        hx.extract(game, ROOT / "local" / "hd_out", ("char",), (), False, ROOT)


def test_census_only_writes_no_pngs(tmp_path: Path) -> None:
    game = _make_game(tmp_path)
    hx.extract(game, tmp_path / "o", ("char",), (), True, ROOT)
    assert not list((tmp_path / "o").rglob("*.png"))


_needs_game = pytest.mark.skipif(not (GAME / "pal" / "imjin2.pal").exists(), reason="local game folder unavailable")


@_needs_game
def test_real_files_decode_exactly() -> None:
    for rel, kind, fw, fh, fc in (("char/archerk.spr", "rle", 56, 46, 184),
                                  ("char/ad1.SPR", "rle", 66, 60, 50),
                                  ("BattleSpr/ICON.Spr", "raw", 32, 16, 3),
                                  ("tile/bright/grss1.ypr.ytl", "ytl", 32, 16, 450)):
        dec, _ = hx.decode_file(GAME / rel)
        assert (dec.kind, dec.fw, dec.fh, len(dec.idx)) == (kind, fw, fh, fc)
        assert all(dec.exact), rel


@_needs_game
def test_real_roundtrip_is_byte_identical() -> None:
    result = hx.roundtrip(GAME, 6, 1157)
    assert result["frames"] > 0
    assert result["identical"] == result["frames"], result["different"][:3]


def test_bmp_254_is_color_key_transparent_not_remapped() -> None:
    """Y-0: portrait BMP index 254 is the engine colour key (SetColorKey 0xFE)."""
    w, h = 3, 2
    rows = [bytes([254, 2, 3, 0]), bytes([4, 254, 254, 0])]
    hdr = struct.pack("<IiiHHIIiiII", 40, w, h, 1, 8, 0, 8, 2834, 2834, 256, 0)
    pixel_off = 14 + 40 + 1024
    data = b"BM" + struct.pack("<IHHI", pixel_off + 8, 0, 0, pixel_off) + hdr + bytes(range(256)) * 4 + b"".join(rows)
    dec, _ = hx.decode_bmp(data)
    assert dec.opaque[0].tolist() == [[1, 0, 0], [0, 1, 1]]     # bottom-up file: top row is the last stored
    base, doubled, remapped = hx.make_products(dec.idx[0], dec.opaque[0], 33)
    assert remapped == 0 and not (base[dec.opaque[0]] == 254).any()
    assert np.array_equal(doubled != 254, np.repeat(np.repeat(dec.opaque[0], 2, axis=0), 2, axis=1))
