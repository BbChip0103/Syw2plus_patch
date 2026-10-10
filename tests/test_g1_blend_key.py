"""H-HDB0: 0x4672E0 (50% translucent logo RLE) HD key path: host-compiled header + source wiring contracts."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUB = ROOT / "tools/inmm_stub"

_PRELUDE = r"""#include <assert.h>
#include <stdint.h>
#include <string.h>
#include "g1_blend_key.h"
/* 6-bit palette: colour c = (c % 50, c * 3 % 64, (c * 5 + 1) % 64); inverse LUT = a hash of the 18-bit offset */
static uint8_t palette[256 * 3];
static uint8_t inverse[G1_BLEND_INVERSE_BYTES];
static void tables(void)
{
    uint32_t c, i;
    for (c = 0u; c < 256u; ++c) {
        palette[c * 3u] = (uint8_t)(c % 50u);
        palette[c * 3u + 1u] = (uint8_t)((c * 3u) % 64u);
        palette[c * 3u + 2u] = (uint8_t)((c * 5u + 1u) % 64u);
    }
    for (i = 0u; i < G1_BLEND_INVERSE_BYTES; ++i) inverse[i] = (uint8_t)((i * 2654435761u) >> 24);
}
/* the original's arithmetic, written independently of the header */
/* H-HDB1: 0x467580 weight table, signed (some entries negative) */
static int16_t weights[G1_BLEND_WEIGHT_ENTRIES];
static void weight_table(void)
{
    uint32_t i;
    for (i = 0u; i < G1_BLEND_WEIGHT_ENTRIES; ++i) weights[i] = (int16_t)((int32_t)((i * 37u) % 61u) - 5);
}
/* 0x467580's arithmetic written from the disassembly: movsx T[(dest channel << 6) + source channel] per channel, then
 * inverse[(((t0 << 6) + t1) << 6) + t2]; returns 0 when the offset is outside the LUT */
__attribute__((unused)) static int original_weighted(uint8_t d, uint8_t s, uint8_t *out)
{
    int32_t t0 = weights[(palette[d * 3] << 6) + palette[s * 3]];
    int32_t t1 = weights[(palette[d * 3 + 1] << 6) + palette[s * 3 + 1]];
    int32_t t2 = weights[(palette[d * 3 + 2] << 6) + palette[s * 3 + 2]];
    int32_t offset = ((t0 * 64 + t1) * 64) + t2;
    if (offset < 0 || offset >= (int32_t)G1_BLEND_INVERSE_BYTES) return 0;
    *out = inverse[offset];
    return 1;
}
__attribute__((unused)) static uint8_t original_pixel(uint8_t d, uint8_t s)
{
    uint32_t ebx = ((uint32_t)(palette[d * 3] >> 1) + (palette[s * 3] >> 1)) << 6;
    ebx += (uint32_t)(palette[s * 3 + 1] >> 1) + (palette[d * 3 + 1] >> 1);
    ebx <<= 6;
    return inverse[ebx + (palette[d * 3 + 2] >> 1) + (palette[s * 3 + 2] >> 1)];
}
"""


def _run(tmp_path: Path, body: str) -> None:
    fixture = tmp_path / "blend_key.c"
    executable = tmp_path / "blend_key"
    fixture.write_text(_PRELUDE + "int main(void) {\n tables();\n weight_table();\n" + body + "\n return 0; }\n", encoding="utf-8")
    built = subprocess.run(
        ["gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-I", str(STUB), str(fixture), "-o", str(executable)],
        capture_output=True, text=True, check=False,
    )
    assert built.returncode == 0, built.stderr
    ran = subprocess.run([str(executable)], capture_output=True, text=True, check=False)
    assert ran.returncode == 0, ran.stderr


def test_decode_ends_a_row_by_width_and_a_skip_may_pass_the_width(tmp_path: Path) -> None:
    """3 wide, 3 rows.  Row 0: skip 1, pixels 7 8.  Row 1: pixel 9, skip 5 (past the width ends the row).  Row 2: skip 0, 4 4 4."""
    _run(tmp_path, r"""
    static const uint8_t rle[] = {0xFE, 1, 7, 8, 9, 0xFE, 5, 0xFE, 0, 4, 4, 4};
    uint8_t idx[9] = {0}, mask[9] = {0};
    size_t used = g1_blend_decode_rle(rle, sizeof(rle), 3u, 3u, idx, mask);
    assert(used == sizeof(rle));
    assert(!mask[0] && mask[1] && mask[2] && idx[1] == 7 && idx[2] == 8);
    assert(mask[3] && idx[3] == 9 && !mask[4] && !mask[5]);
    assert(mask[6] && mask[7] && mask[8] && idx[6] == 4 && idx[8] == 4);
""")


def test_decode_fails_on_a_stream_longer_than_the_limit(tmp_path: Path) -> None:
    _run(tmp_path, r"""
    static const uint8_t rle[] = {1, 2, 3, 4};
    uint8_t idx[4], mask[4];
    assert(g1_blend_decode_rle(rle, 3u, 2u, 2u, idx, mask) == 0u);    /* needs 4 bytes */
    assert(g1_blend_decode_rle(rle, 4u, 2u, 2u, idx, mask) == 4u);
    static const uint8_t cut[] = {0xFE};
    assert(g1_blend_decode_rle(cut, 1u, 2u, 1u, idx, mask) == 0u);    /* skip marker without its count */
""")


def test_blend_pixel_matches_the_originals_arithmetic_for_every_pair(tmp_path: Path) -> None:
    _run(tmp_path, r"""
    unsigned d, s;
    for (d = 0u; d < 256u; ++d) for (s = 0u; s < 256u; ++s) {
        uint8_t out = 0u;
        assert(g1_blend_pixel(palette, inverse, NULL, (uint8_t)d, (uint8_t)s, &out) == 1 && out == original_pixel((uint8_t)d, (uint8_t)s));
    }
    palette[3] = 200u;                       /* an 8-bit entry: the offset leaves the table, the pixel is refused */
    { uint8_t out = 0u; assert(g1_blend_pixel(palette, inverse, NULL, 1u, 0u, &out) == 0); }
""")


def test_selfcheck_accepts_the_originals_output_and_rejects_any_difference(tmp_path: Path) -> None:
    _run(tmp_path, r"""
    uint8_t before[6] = {10, 20, 30, 40, 50, 60}, idx[6] = {0, 1, 0, 0, 2, 0}, mask[6] = {0, 1, 0, 0, 1, 0};
    uint8_t screen[8 * 4]; size_t checked = 0u, i;
    memset(screen, 99, sizeof(screen));
    for (i = 0u; i < 6u; ++i) screen[(i / 3u) * 8u + 2u + i % 3u] = before[i];
    screen[0 * 8 + 2 + 1] = original_pixel(20, 1);
    screen[1 * 8 + 2 + 1] = original_pixel(50, 2);
    assert(g1_blend_selfcheck(palette, inverse, NULL, before, idx, mask, 3u, 2u, screen + 2u, 8u, &checked) == 1 && checked == 2u);
    screen[1 * 8 + 2 + 1] ^= 1u;             /* a blended pixel differs */
    assert(g1_blend_selfcheck(palette, inverse, NULL, before, idx, mask, 3u, 2u, screen + 2u, 8u, &checked) == 0);
    screen[1 * 8 + 2 + 1] ^= 1u;
    screen[0 * 8 + 2] ^= 1u;                 /* an unwritten pixel was touched */
    assert(g1_blend_selfcheck(palette, inverse, NULL, before, idx, mask, 3u, 2u, screen + 2u, 8u, &checked) == 0);
""")


def test_apply_hd_blends_the_hd_destination_with_the_pack_for_covered_opaque_pixels_only(tmp_path: Path) -> None:
    _run(tmp_path, r"""
    /* 2x1 logo at (1, 1): pixel 0 opaque+covered, pixel 1 opaque but not covered */
    uint8_t mask[2] = {1, 1}, covered[2] = {1, 0};
    uint8_t hd_before[8] = {10, 11, 12, 13, 14, 15, 16, 17};      /* 4 wide x 2 high destination copy */
    uint8_t pack[8] = {21, 0xFE, 23, 24, 25, 26, 27, 28};         /* subpixel (1,0) of logo pixel 0 is transparent -> the whole pixel is kept */
    uint8_t screen[16 * 8]; size_t written, i;
    memset(screen, 77, sizeof(screen));
    written = g1_blend_apply_hd(palette, inverse, NULL, mask, covered, 2u, 1u, hd_before, pack, 4u, screen, 16u, 1u, 1u, 0xFEu);
    assert(written == 0u);                                         /* pixel 0 has a transparent subpixel, pixel 1 is not covered */
    for (i = 0u; i < sizeof(screen); ++i) assert(screen[i] == 77);
    pack[1] = 22u;
    written = g1_blend_apply_hd(palette, inverse, NULL, mask, covered, 2u, 1u, hd_before, pack, 4u, screen, 16u, 1u, 1u, 0xFEu);
    assert(written == 1u);
    assert(screen[2 * 16 + 2] == original_pixel(10, 21) && screen[2 * 16 + 3] == original_pixel(11, 22));
    assert(screen[3 * 16 + 2] == original_pixel(14, 25) && screen[3 * 16 + 3] == original_pixel(15, 26));
    assert(screen[2 * 16 + 4] == 77 && screen[3 * 16 + 5] == 77 && screen[2 * 16 + 1] == 77);   /* the uncovered pixel stays */
""")


def test_weighted_pixel_matches_the_originals_table_arithmetic_for_every_pair_including_refusals(tmp_path: Path) -> None:
    _run(tmp_path, r"""
    unsigned d, s, refused = 0u, drawn = 0u;
    for (d = 0u; d < 256u; ++d) for (s = 0u; s < 256u; ++s) {
        uint8_t out = 0u, expected = 0u;
        int ok = g1_blend_pixel(palette, inverse, weights, (uint8_t)d, (uint8_t)s, &out);
        assert(ok == original_weighted((uint8_t)d, (uint8_t)s, &expected));
        if (ok) { assert(out == expected); ++drawn; } else ++refused;
    }
    assert(refused > 0u && drawn > 0u);      /* negative and out-of-LUT offsets exist in this table and are refused */
    palette[3] = 64u;                        /* a channel value that indexes past the 64 x 64 table is refused */
    { uint8_t out = 0u; assert(g1_blend_pixel(palette, inverse, weights, 1u, 0u, &out) == 0); }
""")


def test_weighted_pixel_is_not_the_average(tmp_path: Path) -> None:
    _run(tmp_path, r"""
    unsigned d, s, differ = 0u;
    for (d = 0u; d < 64u; ++d) for (s = 0u; s < 64u; ++s) {
        uint8_t a = 0u, w = 0u;
        if (g1_blend_pixel(palette, inverse, NULL, (uint8_t)d, (uint8_t)s, &a) &&
            g1_blend_pixel(palette, inverse, weights, (uint8_t)d, (uint8_t)s, &w) && a != w) ++differ;
    }
    assert(differ > 100u);
""")


def test_weighted_selfcheck_and_apply_follow_the_table_and_the_crop_window(tmp_path: Path) -> None:
    _run(tmp_path, r"""
    /* a 4x2 stream, window = columns 1..2 of both rows */
    uint8_t idx[8] = {5, 6, 7, 8, 9, 10, 11, 12}, mask[8] = {1, 1, 1, 0, 1, 1, 1, 1};
    uint8_t vidx[4], vmask[4], before[4] = {40, 41, 42, 43}, screen[8 * 3], out = 0u;
    size_t checked = 0u, i, written;
    g1_blend_crop(idx, 4u, 1u, 0u, 2u, 2u, vidx);
    g1_blend_crop(mask, 4u, 1u, 0u, 2u, 2u, vmask);
    assert(vidx[0] == 6 && vidx[1] == 7 && vidx[2] == 10 && vidx[3] == 11);
    assert(vmask[0] && vmask[1] && vmask[2] && vmask[3]);
    memset(screen, 99, sizeof(screen));
    for (i = 0u; i < 4u; ++i) {
        assert(original_weighted(before[i], vidx[i], &out) == 1);
        screen[(i / 2u) * 8u + 3u + i % 2u] = out;
    }
    assert(g1_blend_selfcheck(palette, inverse, weights, before, vidx, vmask, 2u, 2u, screen + 3u, 8u, &checked) == 1 && checked == 4u);
    assert(g1_blend_selfcheck(palette, inverse, NULL, before, vidx, vmask, 2u, 2u, screen + 3u, 8u, &checked) == 0);   /* the average formula does not explain the output */
    screen[3] ^= 1u;
    assert(g1_blend_selfcheck(palette, inverse, weights, before, vidx, vmask, 2u, 2u, screen + 3u, 8u, &checked) == 0);
    {
        /* HD: the pack frame is 8x4; the window starts at stream column 1, so the pack is read from subpixel column 2 */
        uint8_t covered[4] = {1, 1, 1, 1}, hd_before[4 * 4], pack[8 * 4], hd_screen[16 * 8];
        for (i = 0u; i < sizeof(hd_before); ++i) hd_before[i] = (uint8_t)(20u + i);
        for (i = 0u; i < sizeof(pack); ++i) pack[i] = (uint8_t)(1u + i % 9u);
        memset(hd_screen, 77, sizeof(hd_screen));
        written = g1_blend_apply_hd(palette, inverse, weights, vmask, covered, 2u, 2u, hd_before, pack + 2u, 8u, hd_screen, 16u, 1u, 1u, 0xFEu);
        size_t expected_written = 0u;
        for (i = 0u; i < 4u; ++i) {
            size_t row = i / 2u, col = i % 2u, sub;
            uint8_t expect[4];
            int whole = 1;
            for (sub = 0u; sub < 4u; ++sub) {
                size_t hx = col * 2u + (sub & 1u), hy = row * 2u + (sub >> 1);
                if (!original_weighted(hd_before[hy * 4u + hx], pack[hy * 8u + 2u + hx], &expect[sub])) whole = 0;
            }
            expected_written += whole ? 1u : 0u;
            for (sub = 0u; sub < 4u; ++sub) {
                size_t hx = col * 2u + (sub & 1u), hy = row * 2u + (sub >> 1);
                assert(hd_screen[(2u + hy) * 16u + 2u + hx] == (whole ? expect[sub] : 77));
            }
        }
        assert(written == expected_written && written > 0u);
    }
""")


def test_clip_flip_wrapper_skips_the_diff_mirror_after_a_keyed_draw() -> None:
    """B-0 (lap1187 mutation v3): a keyed 0x466BE0 draw must not run the Scale2x diff mirror over the key's HD pixels."""
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    start = mirror.index("static DWORD __attribute__((thiscall)) mirror_flip_clip(")
    wrapper = mirror[start:mirror.index("mirror_shade_rle(", start)]
    keyed = wrapper[wrapper.index("if (g_reinvoke_composed) {"):wrapper.index("} else {", wrapper.index("if (g_reinvoke_composed) {"))]
    assert "++g_flip_clip_keyed_calls;" in keyed and "active = FALSE;" in keyed


def test_blend_wrapper_runs_the_key_after_the_diff_mirror_with_pre_draw_copies_and_counts_fallbacks() -> None:
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    start = mirror.index("static DWORD __attribute__((thiscall)) mirror_blend_rle(")
    wrapper = mirror[start:mirror.index("Original returns: 0x467580", start)]
    assert "key_try = g1_hd_asset_blend_key_path();" in wrapper
    # covered flags and the HD destination are copied before the original draws, the key overlay runs after the diff mirror
    assert (wrapper.index("blend_key_snapshot(") < wrapper.index("g_original_blend_rle(renderer") <
            wrapper.index("g1_overlay_blt_apply(") < wrapper.index("blend_key_apply(renderer"))
    assert "++g_blend_rle_key.keyed_calls;" in wrapper and "++g_blend_rle_key.key_fallbacks;" in wrapper
    # the diff mirror is never skipped: a fallback and a miss keep its Scale2x blocks
    assert "active = FALSE;" not in wrapper


def test_blend_key_apply_checks_the_originals_output_before_it_touches_the_mirror() -> None:
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    start = mirror.index("static BOOL blend_key_apply(")
    body = mirror[start:mirror.index("Original returns: 0x4672E0", start)]
    assert (body.index("g1_blend_decode_rle(") < body.index("g1_blend_selfcheck(") < body.index("g1_hd_asset_begin(") <
            body.index("g1_hd_asset_bind_identity_frame(") < body.index("g1_hd_asset_current_pack_frame(") <
            body.index("g1_blend_apply_hd("))
    assert "if (!g1_blend_selfcheck(" in body and "if (!g1_blend_decode_rle(" in body
    assert "++stats->selfcheck_mismatches;" in body and "stats->selfcheck_pixels += " in body
    assert "hd_width == (DWORD)width * 2u && hd_height == (DWORD)height * 2u" in body
    assert "G1_HD_PACK_KEY" in body and "g_blend_key_hd_before" in body and "g_blend_key_covered" in body
    # the selfcheck is a gate: a mismatch ends the function before the key is bound or drawn
    gate = body[body.index("if (!g1_blend_selfcheck("):body.index("stats->selfcheck_pixels += ")]
    assert "return FALSE;" in gate
    assert "g1_hd_asset_end();" in body


def test_blend_trace_fields_and_switch_are_wired() -> None:
    trace = (STUB / "direct_draw_trace.c").read_text(encoding="utf-8")
    for field in ("blend_4672E0_keyed_calls", "blend_4672E0_keyed_pixels", "blend_4672E0_key_fallbacks",
                  "blend_4672E0_selfcheck_mismatches", "blend_4672E0_selfcheck_pixels",
                  "hd_pack_blend_hits", "hd_pack_blend_misses", "hd_pack_blend_rejects"):
        assert f'\\"{field}\\":%u' in trace
    asset = (STUB / "g1_hd_asset.c").read_text(encoding="utf-8")
    assert '#define G1_HD_PACK_BLEND_ENV "SYW2_G1_HD_PACK_BLEND"' in asset
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    reset = mirror[mirror.index("g_blend_rle_key.keyed_calls = 0u;"):]
    for stats in ("g_blend_rle_key", "g_blend_wrle_key"):
        for counter in ("keyed_calls", "keyed_pixels", "key_fallbacks", "selfcheck_mismatches", "selfcheck_pixels"):
            assert f"{stats}.{counter} = 0u;" in reset


def test_blend_wrappers_call_the_key_only_inside_a_key_try_block_after_the_diff_mirror() -> None:
    """B1-0 (lap1189 survivors x1/x3): removing the key call or letting a failed self check continue must turn this RED."""
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    for name, end, call, stats in (("mirror_blend_rle", "Original returns: 0x467580", "blend_key_apply(renderer, G1_BLEND_RLE, FALSE,", "g_blend_rle_key"),
                                   ("mirror_blend_wrle", "H-D2r: taller blends", "blend_key_apply(renderer, G1_BLEND_WRLE, TRUE,", "g_blend_wrle_key")):
        start = mirror.index(f"static DWORD __attribute__((thiscall)) {name}(")
        wrapper = mirror[start:mirror.index(end, start)]
        block = wrapper[wrapper.index("if (key_try) {"):]
        assert call in block and f"++{stats}.keyed_calls;" in block and f"++{stats}.key_fallbacks;" in block
        diff = wrapper.index("g1_overlay_blt_apply") if name == "mirror_blend_rle" else wrapper.index("g1_overlay_blt_apply_tiled")
        assert wrapper.index("g_original_blend_") < diff < wrapper.index("if (key_try) {", diff)
    core = mirror[mirror.index("static BOOL blend_key_apply("):mirror.index("Original returns: 0x4672E0")]
    mismatch = core[core.index("if (!g1_blend_selfcheck("):core.index("stats->selfcheck_pixels += ")]
    assert mismatch.rstrip().endswith("}") and "++stats->selfcheck_mismatches;" in mismatch and "return FALSE;" in mismatch


def test_weighted_wrapper_keys_the_screen_window_with_the_weight_table() -> None:
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    start = mirror.index("static DWORD __attribute__((thiscall)) mirror_blend_wrle(")
    wrapper = mirror[start:mirror.index("H-D2r: taller blends", start)]
    assert "key_try = g1_hd_asset_blend_key_path();" in wrapper
    assert "G1_BLEND_KEY_MAX_PIXELS" in wrapper and "++g_blend_wrle_key.key_fallbacks;" in wrapper
    # the window copy happens before the original draws; the key sees the stream rectangle and the screen window
    assert wrapper.index("blend_key_snapshot(x0, y0, x1 - x0, y1 - y0);") < wrapper.index("g_original_blend_wrle(renderer")
    assert "x, y, width, height, x0, y0, x1 - x0," in wrapper and "g_blend_wrle_before" in wrapper
    core = mirror[mirror.index("static BOOL blend_key_apply("):mirror.index("Original returns: 0x4672E0")]
    assert "weighted ? (const int16_t *)((const BYTE *)renderer + 0x41CA0u) : NULL" in core
    assert "g1_hd_asset_begin((const BYTE *)(ULONG_PTR)rle, writer, (DWORD)width, (DWORD)height, x, y)" in core
    assert "g1_blend_crop(g_blend_key_idx" in core and "g1_blend_crop(g_blend_key_mask" in core
    assert "frame + offset_y * 2u * hd_width + offset_x * 2u" in core


def test_weighted_trace_fields_and_pack_counters_cover_the_second_writer() -> None:
    trace = (STUB / "direct_draw_trace.c").read_text(encoding="utf-8")
    for field in ("keyed_calls", "keyed_pixels", "key_fallbacks", "selfcheck_mismatches", "selfcheck_pixels"):
        assert f'\\"blend_467580_{field}\\":%u' in trace
        assert f"g1_mirror2x_blend_wrle_{field}()" in trace
    asset = (STUB / "g1_hd_asset.c").read_text(encoding="utf-8")
    assert "key->writer == G1_HD_BLEND_RLE || key->writer == G1_HD_BLEND_WRLE" in asset


def test_blend_key_apply_pins_the_crop_offsets_the_decode_limit_and_the_pixel_counter() -> None:
    """N-0 (lap1191 survivors n3/n11/n13): the cropped window offsets, the decode limit and keyed_pixels are pinned by text."""
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    core = mirror[mirror.index("static BOOL blend_key_apply("):mirror.index("Original returns: 0x4672E0")]
    assert "g1_blend_crop(g_blend_key_idx, (size_t)width, offset_x, offset_y, (size_t)visible_width," in core        # n3
    assert "g1_blend_crop(g_blend_key_mask, (size_t)width, offset_x, offset_y, (size_t)visible_width," in core
    assert "size_t offset_x = (size_t)(x0 - x), offset_y = (size_t)(y0 - y);" in core
    assert "pixels * 2u + (size_t)height * 2u" in core                                                               # n13
    assert "stats->keyed_pixels += (DWORD)written;" in core                                                          # n11


def test_weighted_wrapper_refuses_a_stream_larger_than_the_static_buffers() -> None:
    """N-0 (lap1191 survivor n12): the stream rectangle may not exceed the 800 x 600 key buffers."""
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    assert "#define G1_BLEND_KEY_MAX_PIXELS (G1_OVERLAY_SCREEN_WIDTH * G1_OVERLAY_SCREEN_HEIGHT)" in mirror
    assert "if (key_try && (size_t)width * (size_t)height > G1_BLEND_KEY_MAX_PIXELS) {" in mirror
    start = mirror.index("if (key_try && (size_t)width * (size_t)height > G1_BLEND_KEY_MAX_PIXELS) {")
    assert "key_try = FALSE;" in mirror[start:start + 160]


# --- H-HDB2: 0x467B00 = 0x467580 + the renderer clip rectangle -------------------------------------------------------

def test_clip_window_is_the_screen_intersection_cut_by_an_inclusive_clip_rectangle(tmp_path: Path) -> None:
    _run(tmp_path, r"""
    int wx0 = -1, wy0 = -1, wx1 = -1, wy1 = -1;
    /* stream rectangle on the screen: [10, 50) x [20, 60) */
    assert(g1_blend_clip_window(10, 20, 50, 60, 0, 0, 799, 599, &wx0, &wy0, &wx1, &wy1) == 1);
    assert(wx0 == 10 && wy0 == 20 && wx1 == 50 && wy1 == 60);                 /* a wide clip cuts nothing */
    assert(g1_blend_clip_window(10, 20, 50, 60, 15, 0, 799, 599, &wx0, &wy0, &wx1, &wy1) == 1 && wx0 == 15 && wy0 == 20 && wx1 == 50 && wy1 == 60);
    assert(g1_blend_clip_window(10, 20, 50, 60, 0, 25, 799, 599, &wx0, &wy0, &wx1, &wy1) == 1 && wx0 == 10 && wy0 == 25 && wx1 == 50 && wy1 == 60);
    /* right and bottom are inclusive: right = 44 keeps column 44, so the window ends at 45 */
    assert(g1_blend_clip_window(10, 20, 50, 60, 0, 0, 44, 599, &wx0, &wy0, &wx1, &wy1) == 1 && wx0 == 10 && wx1 == 45 && wy1 == 60);
    assert(g1_blend_clip_window(10, 20, 50, 60, 0, 0, 799, 54, &wx0, &wy0, &wx1, &wy1) == 1 && wy0 == 20 && wy1 == 55 && wx1 == 50);
    /* a one-pixel-wide / one-pixel-high clip at the first column and row */
    assert(g1_blend_clip_window(10, 20, 50, 60, 10, 20, 10, 20, &wx0, &wy0, &wx1, &wy1) == 1 && wx0 == 10 && wx1 == 11 && wy0 == 20 && wy1 == 21);
    /* ... and at the last column and row of the rectangle */
    assert(g1_blend_clip_window(10, 20, 50, 60, 49, 59, 800, 600, &wx0, &wy0, &wx1, &wy1) == 1 && wx0 == 49 && wx1 == 50 && wy0 == 59 && wy1 == 60);
    /* all four sides at once */
    assert(g1_blend_clip_window(10, 20, 50, 60, 15, 25, 44, 54, &wx0, &wy0, &wx1, &wy1) == 1 && wx0 == 15 && wy0 == 25 && wx1 == 45 && wy1 == 55);
    /* a clip rectangle that is not inside the screen cannot widen the intersection */
    assert(g1_blend_clip_window(10, 20, 50, 60, -100, -100, 5000, 5000, &wx0, &wy0, &wx1, &wy1) == 1 && wx0 == 10 && wy0 == 20 && wx1 == 50 && wy1 == 60);
    assert(g1_blend_clip_window(10, 20, 50, 60, INT32_MIN, INT32_MIN, INT32_MAX, INT32_MAX, &wx0, &wy0, &wx1, &wy1) == 1 && wx1 == 50 && wy1 == 60);
""")


def test_clip_window_is_empty_when_the_clip_rectangle_misses_the_stream_rectangle(tmp_path: Path) -> None:
    _run(tmp_path, r"""
    int wx0 = 7, wy0 = 7, wx1 = 7, wy1 = 7;
    assert(g1_blend_clip_window(10, 20, 50, 60, 0, 0, 9, 599, &wx0, &wy0, &wx1, &wy1) == 0);       /* right edge just left of the rectangle */
    assert(g1_blend_clip_window(10, 20, 50, 60, 0, 0, 799, 19, &wx0, &wy0, &wx1, &wy1) == 0);      /* bottom edge just above */
    assert(g1_blend_clip_window(10, 20, 50, 60, 50, 0, 799, 599, &wx0, &wy0, &wx1, &wy1) == 0);     /* left edge at the exclusive end */
    assert(g1_blend_clip_window(10, 20, 50, 60, 0, 60, 799, 599, &wx0, &wy0, &wx1, &wy1) == 0);     /* top edge at the exclusive end */
    assert(g1_blend_clip_window(10, 20, 50, 60, 30, 30, 20, 40, &wx0, &wy0, &wx1, &wy1) == 0);      /* inverted clip */
    assert(g1_blend_clip_window(10, 20, 50, 60, INT32_MAX, 0, INT32_MAX, 599, &wx0, &wy0, &wx1, &wy1) == 0);
    assert(wx0 == 7 && wy0 == 7 && wx1 == 7 && wy1 == 7);                                           /* nothing is written on a miss */
""")


def test_rows_above_the_clip_are_parsed_but_the_window_keeps_the_streams_own_row_order(tmp_path: Path) -> None:
    """A 3 x 4 stream whose rows have different shapes; the clip starts at row 2, so the window is rows 2 and 3 of the stream."""
    _run(tmp_path, r"""
    /* row 0: 1 2 3 | row 1: FE 1 4 FE 1 | row 2: 5 FE 2 | row 3: FE 0 6 7 8 */
    uint8_t rle[] = {1, 2, 3, 0xFE, 1, 4, 0xFE, 1, 5, 0xFE, 2, 0xFE, 0, 6, 7, 8};
    uint8_t idx[12] = {0}, mask[12] = {0}, vidx[6], vmask[6];
    int wx0, wy0, wx1, wy1;
    assert(g1_blend_decode_rle(rle, sizeof(rle), 3u, 4u, idx, mask) == sizeof(rle));
    assert(g1_blend_clip_window(0, 0, 3, 4, 0, 2, 799, 599, &wx0, &wy0, &wx1, &wy1) == 1 && wy0 == 2 && wy1 == 4);
    g1_blend_crop(idx, 3u, (size_t)(wx0 - 0), (size_t)(wy0 - 0), (size_t)(wx1 - wx0), (size_t)(wy1 - wy0), vidx);
    g1_blend_crop(mask, 3u, (size_t)(wx0 - 0), (size_t)(wy0 - 0), (size_t)(wx1 - wx0), (size_t)(wy1 - wy0), vmask);
    assert(vidx[0] == 5 && vidx[1] == 0 && vidx[2] == 0 && vidx[3] == 6 && vidx[4] == 7 && vidx[5] == 8);
    assert(vmask[0] == 1 && vmask[1] == 0 && vmask[2] == 0 && vmask[3] == 1 && vmask[4] == 1 && vmask[5] == 1);
""")


def _clip_wrapper() -> str:
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    start = mirror.index("static DWORD __attribute__((thiscall)) mirror_blend_clip(")
    return mirror[start:mirror.index("H-D2r: 0x4685C0", start)]


def test_clip_wrapper_reads_the_renderer_clip_before_the_original_runs_and_keys_after_the_diff_mirror() -> None:
    wrapper = _clip_wrapper()
    assert "key_try = g1_hd_asset_blend_key_path();" in wrapper
    # left, top, right, bottom in renderer + 0x4D0 / 0x4D4 / 0x4D8 / 0x4DC order, read before the original draws
    reads = [wrapper.index(f"G1_RENDERER_VIEWPORT + {offset}u)") for offset in (4, 8, 12)]
    assert wrapper.index("*(const volatile int32_t *)((BYTE *)renderer + G1_RENDERER_VIEWPORT),") < reads[0] < reads[1] < reads[2]
    assert reads[2] < wrapper.index("blend_key_snapshot(kx0, ky0, kx1 - kx0, ky1 - ky0);") < wrapper.index("g_original_blend_clip(renderer")
    assert "g1_blend_clip_window(x0, y0, x1, y1," in wrapper and "&kx0, &ky0, &kx1, &ky1" in wrapper
    # the key window's pre-draw copy is cropped out of the screen intersection's copy, at the key window's offset
    assert ("g1_blend_crop(g_blend_clip_before, (size_t)(x1 - x0), (size_t)(kx0 - x0), (size_t)(ky0 - y0)," in wrapper and
            "(size_t)(kx1 - kx0), (size_t)(ky1 - ky0), g_blend_clip_key_before);" in wrapper)
    assert wrapper.index("g_original_blend_clip(renderer") < wrapper.index("g1_overlay_blt_apply_tiled") < wrapper.index("if (key_try) {", wrapper.index("g1_overlay_blt_apply_tiled"))
    block = wrapper[wrapper.index("if (key_try) {", wrapper.index("g1_overlay_blt_apply_tiled")):]
    assert ("blend_key_apply(renderer, G1_BLEND_CLIP, TRUE, rle, x, y, width, height, kx0, ky0, kx1 - kx0," in block and
            "ky1 - ky0, buffer, stride, g_blend_clip_key_before, &g_blend_clip_key)" in block)
    assert "++g_blend_clip_key.keyed_calls;" in block and "++g_blend_clip_key.key_fallbacks;" in block
    # the cut counter only counts a keyed call, and only when the window really is narrower than the screen intersection
    assert "if (key_cut) ++g_blend_clip_key.key_clip_cut;" in block
    assert "key_cut = kx0 != x0 || ky0 != y0 || kx1 != x1 || ky1 != y1;" in wrapper
    assert "active = FALSE;" not in wrapper                                    # the diff mirror always runs; a miss keeps it


def test_clip_wrapper_skips_the_key_for_an_empty_clip_window_and_a_stream_larger_than_the_buffers() -> None:
    wrapper = _clip_wrapper()
    empty = wrapper[wrapper.index("!g1_blend_clip_window("):wrapper.index("if (key_try) {")]
    assert "key_try = FALSE;" in empty and "++g_blend_clip_key.key_clip_empty;" in empty
    big = wrapper[wrapper.index("if (key_try && (size_t)width * (size_t)height > G1_BLEND_KEY_MAX_PIXELS) {"):]
    assert "++g_blend_clip_key.key_fallbacks;" in big[:160] and "key_try = FALSE;" in big[:200]
    assert wrapper.index("G1_BLEND_KEY_MAX_PIXELS") < wrapper.index("!g1_blend_clip_window(")


def test_clip_key_trace_fields_counters_and_writer_are_wired() -> None:
    trace = (STUB / "direct_draw_trace.c").read_text(encoding="utf-8")
    for field in ("keyed_calls", "keyed_pixels", "key_fallbacks", "selfcheck_mismatches", "selfcheck_pixels", "key_clip_cut", "key_clip_empty"):
        assert f'\\"blend_467B00_{field}\\":%u' in trace
        assert f"g1_mirror2x_blend_clip_{field}()" in trace
        assert f"DWORD g1_mirror2x_blend_clip_{field}(void);" in (STUB / "g1_mirror2x.h").read_text(encoding="utf-8")
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    reset = mirror[mirror.index("g_blend_rle_key.keyed_calls = 0u;"):]
    for counter in ("keyed_calls", "keyed_pixels", "key_fallbacks", "selfcheck_mismatches", "selfcheck_pixels", "key_clip_cut", "key_clip_empty"):
        assert f"g_blend_clip_key.{counter} = 0u;" in reset
    asset = (STUB / "g1_hd_asset.c").read_text(encoding="utf-8")
    assert "#define G1_HD_BLEND_CLIP 0x00467B00u" in asset
    assert "key->writer == G1_HD_BLEND_RLE || key->writer == G1_HD_BLEND_WRLE || key->writer == G1_HD_BLEND_CLIP" in asset


# --- H-HDB3: 0x467FD0 and 0x4685C0 = 0x467580 and 0x467B00 drawn right to left --------------------------------------

def test_flip_rows_reverses_every_row_for_odd_and_even_widths(tmp_path: Path) -> None:
    _run(tmp_path, r"""
    uint8_t odd[6] = {1, 2, 3, 4, 5, 6}, even[8] = {1, 2, 3, 4, 5, 6, 7, 8}, one[2] = {9, 8};
    g1_blend_flip_rows(odd, 3u, 2u);
    assert(odd[0] == 3 && odd[1] == 2 && odd[2] == 1 && odd[3] == 6 && odd[4] == 5 && odd[5] == 4);
    g1_blend_flip_rows(even, 4u, 2u);
    assert(even[0] == 4 && even[1] == 3 && even[2] == 2 && even[3] == 1 && even[4] == 8 && even[5] == 7 && even[6] == 6 && even[7] == 5);
    g1_blend_flip_rows(one, 1u, 2u);                                  /* a one-wide plane is its own mirror */
    assert(one[0] == 9 && one[1] == 8);
    g1_blend_flip_rows(even, 4u, 0u);                                 /* no rows, nothing touched */
    assert(even[0] == 4);
""")


# The reference writes the stream the way the disassembly of 0x467FD0 / 0x4685C0 does: the token at stream column c lands on
# screen column x + (w - c - 1); 0x4685C0 additionally writes only columns in [left, right] and rows >= top, parses the
# rows above the clip, and stops at the first row below it.  The blend is the original's weighted arithmetic.
_FLIP_REFERENCE = r"""
#define SW 40
#define SH 20
static uint8_t before_screen[SW * SH], after_screen[SW * SH], touched[SW * SH], good[16];
static void flip_screens(void)
{
    uint32_t i, found = 0u, s;
    for (s = 1u; s < 256u && found < 16u; ++s) {
        int ok = 1;
        uint8_t out;
        for (i = 40u; i < 44u; ++i) if (!original_weighted((uint8_t)i, (uint8_t)s, &out)) ok = 0;
        if (ok) good[found++] = (uint8_t)s;
    }
    assert(found == 16u);
    for (i = 0u; i < SW * SH; ++i) before_screen[i] = (uint8_t)(40u + (i * 7u) % 4u);
}
static void reference_draw(const uint8_t *rle, int x, int y, int w, int h, int clipped, int left, int top, int right, int bottom)
{
    size_t pos = 0u;
    int row, col;
    memcpy(after_screen, before_screen, sizeof(after_screen));
    memset(touched, 0, sizeof(touched));
    for (row = 0; row < h; ++row) {
        if (clipped && y + row > bottom) return;                      /* rows below the clip are not parsed */
        col = 0;
        while (col < w) {
            if (rle[pos] == 0xFE) { col += rle[pos + 1u]; pos += 2u; continue; }
            {
                int sx = x + (w - col - 1), sy = y + row;
                if (!clipped || (sy >= top && sx >= left && sx <= right)) {
                    uint8_t out = 0u;
                    assert(original_weighted(after_screen[sy * SW + sx], rle[pos], &out));
                    after_screen[sy * SW + sx] = out;
                    touched[sy * SW + sx] = 1u;
                }
            }
            ++col;
            ++pos;
        }
    }
}
/* the key path: decode, (flip,) window, crop, self check against the reference's output.  -2 = decode failed, -1 = empty
 * window (the reference then wrote nothing); a touched cell outside the window, or a window cell whose mask disagrees with
 * the reference's writes, aborts. */
static int keyed_check(const uint8_t *rle, size_t used, int x, int y, int w, int h, int clipped, int left, int top, int right,
                       int bottom, int flip, size_t *checked)
{
    static uint8_t idx[SW * SH], mask[SW * SH], vidx[SW * SH], vmask[SW * SH], bw[SW * SH];
    int kx0 = x, ky0 = y, kx1 = x + w, ky1 = y + h, r, c;
    memset(idx, 0, sizeof(idx));
    memset(mask, 0, sizeof(mask));
    reference_draw(rle, x, y, w, h, clipped, left, top, right, bottom);
    if (g1_blend_decode_rle(rle, used, (size_t)w, (size_t)h, idx, mask) == 0u) return -2;
    if (flip) {
        g1_blend_flip_rows(idx, (size_t)w, (size_t)h);
        g1_blend_flip_rows(mask, (size_t)w, (size_t)h);
    }
    if (clipped && !g1_blend_clip_window(x, y, x + w, y + h, left, top, right, bottom, &kx0, &ky0, &kx1, &ky1)) {
        for (r = 0; r < SW * SH; ++r) assert(!touched[r]);
        return -1;
    }
    g1_blend_crop(idx, (size_t)w, (size_t)(kx0 - x), (size_t)(ky0 - y), (size_t)(kx1 - kx0), (size_t)(ky1 - ky0), vidx);
    g1_blend_crop(mask, (size_t)w, (size_t)(kx0 - x), (size_t)(ky0 - y), (size_t)(kx1 - kx0), (size_t)(ky1 - ky0), vmask);
    for (r = 0; r < SH; ++r)
        for (c = 0; c < SW; ++c)
            if (touched[r * SW + c]) assert(c >= kx0 && c < kx1 && r >= ky0 && r < ky1);
    for (r = 0; r < ky1 - ky0; ++r)
        for (c = 0; c < kx1 - kx0; ++c)
            bw[r * (kx1 - kx0) + c] = before_screen[(ky0 + r) * SW + kx0 + c];
    if (flip)                                                         /* with the right planes the mask is exactly the writes */
        for (r = 0; r < ky1 - ky0; ++r)
            for (c = 0; c < kx1 - kx0; ++c) assert(touched[(ky0 + r) * SW + kx0 + c] == vmask[r * (kx1 - kx0) + c]);
    return g1_blend_selfcheck(palette, inverse, weights, bw, vidx, vmask, (size_t)(kx1 - kx0), (size_t)(ky1 - ky0),
                              after_screen + ky0 * SW + kx0, SW, checked);
}
"""

# 6 x 4 stream (no row is the mirror of another), tokens drawn from verified sources good[]:
#   row 0: skip 1, tokens at columns 1-5 | row 1: columns 0 1, skip 3, column 5 | row 2: skip 2, columns 2 3, skip 0, columns 4 5
#   | row 3: column 0, skip 4, skip 1
_FLIP_STREAM = r"""
    uint8_t rle[64];
    size_t n = 0u, i;
    const int program[] = {-1, 1, 0, 1, 2, 3, 4,   5, 6, -1, 3, 7,   -1, 2, 8, 9, -1, 0, 10, 11,   12, -1, 4, -1, 1};
    flip_screens();
    for (i = 0u; i < sizeof(program) / sizeof(program[0]); ++i) {
        if (program[i] == -1) { rle[n++] = 0xFE; rle[n++] = (uint8_t)program[++i]; }
        else rle[n++] = good[program[i]];
    }
"""


def _run_flip(tmp_path: Path, tail: str) -> None:
    fixture = tmp_path / "flip_key.c"
    executable = tmp_path / "flip_key"
    fixture.write_text(_PRELUDE + _FLIP_REFERENCE + "int main(void) {\n tables();\n weight_table();\n" + _FLIP_STREAM + tail
                       + "\n return 0; }\n", encoding="utf-8")
    built = subprocess.run(
        ["gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-I", str(STUB), str(fixture), "-o", str(executable)],
        capture_output=True, text=True, check=False,
    )
    assert built.returncode == 0, built.stderr
    ran = subprocess.run([str(executable)], capture_output=True, text=True, check=False)
    assert ran.returncode == 0, ran.stderr


def test_flipped_planes_match_the_reference_draw_of_the_unclipped_writer_and_unflipped_planes_do_not(tmp_path: Path) -> None:
    """0x467FD0: the token at stream column c lands on screen column x + w - c - 1, so only the reversed planes explain the output."""
    _run_flip(tmp_path, r"""
    size_t checked = 0u;
    assert(keyed_check(rle, n, 8, 5, 6, 4, 0, 0, 0, 0, 0, 1, &checked) == 1 && checked == 13u);
    assert(keyed_check(rle, n, 8, 5, 6, 4, 0, 0, 0, 0, 0, 0, &checked) == 0);            /* stream direction: wrong cells */
    assert(keyed_check(rle, n, 0, 0, 6, 4, 0, 0, 0, 0, 0, 1, &checked) == 1);            /* flush with the screen corner */
    assert(keyed_check(rle, n, 34, 16, 6, 4, 0, 0, 0, 0, 0, 1, &checked) == 1);          /* flush with the far corner */
""")


def test_flipped_clipped_writer_keys_exactly_the_cells_the_reference_writes(tmp_path: Path) -> None:
    """0x4685C0: left/right/top/bottom clip in screen coordinates; the stream is cropped in screen direction at (kx0 - x, ky0 - y)."""
    _run_flip(tmp_path, r"""
    size_t checked = 0u;
    /* stream at x=8..13, y=5..8; screen column 8 is the stream's LAST column */
    assert(keyed_check(rle, n, 8, 5, 6, 4, 1, 10, 0, 799, 599, 1, &checked) == 1);        /* left clip cuts the stream's right end */
    assert(keyed_check(rle, n, 8, 5, 6, 4, 1, 10, 0, 799, 599, 0, &checked) == 0);        /* the stream-direction planes are wrong */
    assert(keyed_check(rle, n, 8, 5, 6, 4, 1, 0, 0, 11, 599, 1, &checked) == 1);          /* right is inclusive: column 11 is drawn */
    assert(keyed_check(rle, n, 8, 5, 6, 4, 1, 0, 0, 12, 599, 1, &checked) == 1);
    assert(keyed_check(rle, n, 8, 5, 6, 4, 1, 0, 7, 799, 599, 1, &checked) == 1);         /* rows 0 and 1 parsed, not written */
    assert(keyed_check(rle, n, 8, 5, 6, 4, 1, 0, 0, 799, 6, 1, &checked) == 1);           /* bottom inclusive: rows 0 and 1 only */
    assert(keyed_check(rle, n, 8, 5, 6, 4, 1, 9, 6, 12, 7, 1, &checked) == 1);            /* all four sides */
    assert(keyed_check(rle, n, 8, 5, 6, 4, 1, 13, 5, 13, 8, 1, &checked) == 1);           /* a one-column window: the stream's first column */
    assert(keyed_check(rle, n, 8, 5, 6, 4, 1, 8, 8, 8, 8, 1, &checked) == 1);             /* one pixel: stream column 5 of the last row */
    assert(keyed_check(rle, n, 8, 5, 6, 4, 1, 14, 0, 799, 599, 1, &checked) == -1);       /* clip right of the rectangle: empty */
    assert(keyed_check(rle, n, 8, 5, 6, 4, 1, 0, 0, 7, 599, 1, &checked) == -1);          /* clip left of the rectangle: empty */
    assert(keyed_check(rle, n, 8, 5, 6, 4, 1, 0, 9, 799, 599, 1, &checked) == -1);        /* clip below the rectangle: empty */
""")


def _wrapper(name: str, end: str) -> str:
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    start = mirror.index(f"static DWORD __attribute__((thiscall)) {name}(")
    return mirror[start:mirror.index(end, start)]


_KEY_WRAPPERS = (("mirror_blend_rle", "Original returns: 0x467580", "g1_overlay_blt_apply("),
                 ("mirror_blend_wrle", "H-D2r: taller blends", "g1_overlay_blt_apply_tiled("),
                 ("mirror_blend_clip", "H-D2r: 0x4685C0", "g1_overlay_blt_apply_tiled("),
                 ("mirror_blend_skip", "H-P: 0x4678C0", "g1_overlay_blt_apply_banded("),
                 ("mirror_flip_blend", "H-L2: 0x467E60", "g1_overlay_blt_apply("),
                 ("mirror_blend_clip7", "H-U: 0x468360", "g1_overlay_blt_apply("),      # H-HDB4
                 ("mirror_blend_flip7", "H-Q: 0x467FD0", "g1_overlay_blt_apply("))


def test_every_blend_wrapper_keys_only_inside_the_diff_mirror_success_branch() -> None:
    """B3-0 (lap1195 survivor n11): the key block sits before the diff mirror's reject_size else branch, never after it."""
    for name, end, diff in _KEY_WRAPPERS:
        wrapper = _wrapper(name, end)
        applied = wrapper.index(diff, wrapper.index("g_original_"))
        reject = wrapper.index("reject_size", applied)
        key = wrapper.index("if (key_try) {", applied)
        assert key < reject, name
        assert wrapper.count("blend_key_apply(") == 1, name
        assert wrapper.index("blend_key_apply(") > applied, name


def test_flipped_writers_derive_the_flip_from_the_writer_and_reverse_the_planes_before_the_crop() -> None:
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    core = mirror[mirror.index("static BOOL blend_key_apply("):mirror.index("Original returns: 0x4672E0")]
    assert "const BOOL flip = writer == G1_FLIP_BLEND || writer == G1_BLEND_SKIP || writer == G1_BLEND_FLIP7;" in core   # H-HDB4: 0x468360 too
    assert (core.index("g1_blend_decode_rle(") < core.index("if (flip) {") < core.index("g1_blend_crop(g_blend_key_idx") <
            core.index("g1_blend_selfcheck(") < core.index("g1_hd_asset_bind_identity_frame("))
    reverse = core[core.index("if (flip) {"):core.index("g1_blend_crop(g_blend_key_idx")]
    assert "g1_blend_flip_rows(g_blend_key_idx, (size_t)width, (size_t)height);" in reverse
    assert "g1_blend_flip_rows(g_blend_key_mask, (size_t)width, (size_t)height);" in reverse
    assert "#define G1_BLEND_SKIP 0x004685C0u" in mirror and "#define G1_FLIP_BLEND 0x00467FD0u" in mirror


def test_flipped_clip_wrapper_reads_the_renderer_clip_before_the_original_and_keys_after_the_diff_mirror() -> None:
    wrapper = _wrapper("mirror_blend_skip", "H-P: 0x4678C0")
    assert "key_try = g1_hd_asset_blend_flip_key_path();" in wrapper
    reads = [wrapper.index(f"G1_RENDERER_VIEWPORT + {offset}u)") for offset in (4, 8, 12)]
    assert wrapper.index("*(const volatile int32_t *)((BYTE *)renderer + G1_RENDERER_VIEWPORT),") < reads[0] < reads[1] < reads[2]
    assert reads[2] < wrapper.index("blend_key_snapshot(kx0, ky0, kx1 - kx0, ky1 - ky0);") < wrapper.index("g_original_blend_skip(renderer")
    assert "g1_blend_clip_window(x0, y0, x1, y1," in wrapper and "&kx0, &ky0, &kx1, &ky1" in wrapper
    assert ("g1_blend_crop(g_blend_skip_before, (size_t)(x1 - x0), (size_t)(kx0 - x0), (size_t)(ky0 - y0)," in wrapper and
            "(size_t)(kx1 - kx0), (size_t)(ky1 - ky0), g_blend_clip_key_before);" in wrapper)
    block = wrapper[wrapper.index("if (key_try) {", wrapper.index("g1_overlay_blt_apply_banded(")):]
    assert ("blend_key_apply(renderer, G1_BLEND_SKIP, TRUE, rle, x, y, width, height, kx0, ky0, kx1 - kx0," in block and
            "ky1 - ky0, buffer, stride, g_blend_clip_key_before, &g_blend_skip_key)" in block)
    assert "++g_blend_skip_key.keyed_calls;" in block and "++g_blend_skip_key.key_fallbacks;" in block
    assert "if (key_cut) ++g_blend_skip_key.key_clip_cut;" in block
    assert block.count("key_clip_cut") == 1 and block.index("key_clip_cut") < block.index("++g_blend_skip_key.key_fallbacks;")   # only a keyed call counts a cut
    assert "key_cut = kx0 != x0 || ky0 != y0 || kx1 != x1 || ky1 != y1;" in wrapper
    empty = wrapper[wrapper.index("!g1_blend_clip_window("):wrapper.index("if (key_try) {")]
    assert "key_try = FALSE;" in empty and "++g_blend_skip_key.key_clip_empty;" in empty
    big = wrapper[wrapper.index("if (key_try && (size_t)width * (size_t)height > G1_BLEND_KEY_MAX_PIXELS) {"):]
    assert "++g_blend_skip_key.key_fallbacks;" in big[:160] and "key_try = FALSE;" in big[:200]
    assert wrapper.index("G1_BLEND_KEY_MAX_PIXELS") < wrapper.index("!g1_blend_clip_window(")
    assert "active = FALSE;" not in wrapper


def test_flipped_unclipped_wrapper_keys_the_screen_window_and_counts_wrap_mismatches() -> None:
    wrapper = _wrapper("mirror_flip_blend", "H-L2: 0x467E60")
    assert "key_try = g1_hd_asset_blend_flip_key_path();" in wrapper
    assert "G1_BLEND_KEY_MAX_PIXELS" in wrapper and "++g_flip_blend_key.key_fallbacks;" in wrapper
    assert wrapper.index("blend_key_snapshot(x0, y0, x1 - x0, y1 - y0);") < wrapper.index("g_original_flip_blend(renderer")
    block = wrapper[wrapper.index("if (key_try) {", wrapper.index("g1_overlay_blt_apply(")):]
    assert ("blend_key_apply(renderer, G1_FLIP_BLEND, TRUE, rle, x, y, width, height, x0, y0, x1 - x0," in block and
            "y1 - y0, buffer, stride, g_flip_blend_before, &g_flip_blend_key)" in block)
    assert "++g_flip_blend_key.keyed_calls;" in block and "++g_flip_blend_key.key_fallbacks;" in block
    # a mismatch is a wrap mismatch only for a call whose rectangle leaves the stride or the screen
    assert "wrapped = x < 0 || x + width > (int)stride || y < 0 || y + height > (int)G1_OVERLAY_SCREEN_HEIGHT;" in wrapper
    assert ("if (wrapped && g_flip_blend_key.selfcheck_mismatches != mismatches)" in block and
            "++g_flip_blend_key.key_wrap_mismatches;" in block)
    assert "active = FALSE;" not in wrapper


def test_flipped_key_trace_fields_counters_resets_and_asset_writers_are_wired() -> None:
    trace = (STUB / "direct_draw_trace.c").read_text(encoding="utf-8")
    header = (STUB / "g1_mirror2x.h").read_text(encoding="utf-8")
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    reset = mirror[mirror.index("g_blend_rle_key.keyed_calls = 0u;"):]
    for tag, prefix, stats, counters in (
            ("4685C0", "blend_skip", "g_blend_skip_key", ("keyed_calls", "keyed_pixels", "key_fallbacks", "selfcheck_mismatches",
                                                         "selfcheck_pixels", "key_clip_cut", "key_clip_empty")),
            ("467FD0", "flip_blend", "g_flip_blend_key", ("keyed_calls", "keyed_pixels", "key_fallbacks", "selfcheck_mismatches",
                                                         "selfcheck_pixels", "key_wrap_mismatches"))):
        for counter in counters:
            assert f'\\"blend_{tag}_{counter}\\":%u' in trace
            assert f"g1_mirror2x_{prefix}_{counter}()" in trace
            assert f"DWORD g1_mirror2x_{prefix}_{counter}(void);" in header
            assert f"{stats}.{counter} = 0u;" in reset
    asset = (STUB / "g1_hd_asset.c").read_text(encoding="utf-8")
    assert "#define G1_HD_BLEND_FLIP 0x00467FD0u" in asset and "#define G1_HD_BLEND_SKIP 0x004685C0u" in asset
    assert "return writer == G1_HD_BLEND_FLIP || writer == G1_HD_BLEND_SKIP || writer == G1_HD_BLEND_FLIP7;" in asset   # H-HDB4: 0x468360 too
    assert "if (is_flip_pack_writer(key->writer) || is_flip_blend_writer(key->writer))" in asset
    assert "is_flip_blend_writer(key->writer) || is_remap_blend_writer(key->writer)) {" in asset   # counted as a blend writer
    assert "return g1_hd_asset_blend_key_path() && !g_hd_flip_off;" in asset


# ---- H-HDB4: 0x4678C0 / 0x468360 (7 stack args: x y width height rle remap level) -------------------------------------
# The reference below is written from the disassembly (orig_4678C0 / orig_468360 / 0x4654D0), not from the header: the
# table builder fills slice `level` (outer loop v = 0, 10 .. 90) with max(d, max(0, s - floor(v * s / 100))), the writer
# indexes it as T[((level << 6) + palette[d][c]) << 6) + palette[remap[token]][c]] per channel, then
# inverse[(((t0 << 6) + t1) << 6) + t2].  0x4678C0 writes x + col; 0x468360 x + (w - col - 1); both clip like 0x467B00.
_LEVEL_REFERENCE = r"""
#define SW 40
#define SH 20
#define SLICES 10
static uint32_t level_table[SLICES * 4096];
static uint8_t remap[256], identity[256], before_screen[SW * SH], after_screen[SW * SH], touched[SW * SH];
static const uint8_t tokens[] = {3, 17, 29, 41, 57, 71, 83, 97, 101, 113, 127, 131, 149};
/* 0x4654D0 literally: edx = max(d, c), ebx = min(d, c), eax = (64 - edx + ((64 - edx) >> 31 & 63)) >> 6, entry = max(d, c) + eax * ebx */
static uint32_t builder_entry(int level, int d, int s)
{
    int v = level * 10, c = s - (v * s) / 100, hi, lo, eax;
    if (c <= 0) c = 0;
    hi = d > c ? d : c;
    lo = d < c ? d : c;
    eax = (64 - hi) >> 6;
    return (uint32_t)(hi + eax * lo);
}
static void level_tables(void)
{
    int level, d, s, i;
    for (level = 0; level < SLICES; ++level)
        for (d = 0; d < 64; ++d)
            for (s = 0; s < 64; ++s) level_table[(level * 64 + d) * 64 + s] = builder_entry(level, d, s);
    for (i = 0; i < 256; ++i) { remap[i] = (uint8_t)((i * 37 + 11) & 255); identity[i] = (uint8_t)i; }
}
static int original_level(int level, uint8_t d, uint8_t token, uint8_t *out)
{
    uint8_t s = remap[token];
    uint32_t t0 = level_table[(((level << 6) + palette[d * 3]) << 6) + palette[s * 3]];
    uint32_t t1 = level_table[(((level << 6) + palette[d * 3 + 1]) << 6) + palette[s * 3 + 1]];
    uint32_t t2 = level_table[(((level << 6) + palette[d * 3 + 2]) << 6) + palette[s * 3 + 2]];
    uint32_t offset = (((t0 << 6) + t1) << 6) + t2;
    if (offset >= G1_BLEND_INVERSE_BYTES) return 0;
    *out = inverse[offset];
    return 1;
}
static void reference_draw(const uint8_t *rle, int x, int y, int w, int h, int flip, int level, int left, int top, int right, int bottom)
{
    size_t pos = 0u;
    int row, col;
    int i;
    for (i = 0; i < SW * SH; ++i) before_screen[i] = (uint8_t)(40 + (i * 7) % 4);
    memcpy(after_screen, before_screen, sizeof(after_screen));
    memset(touched, 0, sizeof(touched));
    for (row = 0; row < h; ++row) {
        if (y + row > bottom) return;                                  /* rows below the clip are not parsed */
        col = 0;
        while (col < w) {
            if (rle[pos] == 0xFE) { col += rle[pos + 1u]; pos += 2u; continue; }
            {
                int sx = flip ? x + (w - col - 1) : x + col, sy = y + row;
                if (sy >= top && sx >= left && sx <= right) {
                    uint8_t out = 0u;
                    assert(original_level(level, after_screen[sy * SW + sx], rle[pos], &out));
                    after_screen[sy * SW + sx] = out;
                    touched[sy * SW + sx] = 1u;
                }
            }
            ++col;
            ++pos;
        }
    }
}
/* the key path of blend_key_apply for a remapped writer: level slice -> int16 weights, decode, (flip,) window, crop,
 * remap plane, self check.  -3 = level refused, -2 = decode failed, -1 = empty window. */
__attribute__((unused)) static int keyed_check7(const uint8_t *rle, size_t used, int x, int y, int w, int h, int flip, int ref_level, int key_level,
                        const uint8_t *key_remap, int left, int top, int right, int bottom, size_t *checked)
{
    static uint8_t idx[SW * SH], mask[SW * SH], vidx[SW * SH], vmask[SW * SH], vsrc[SW * SH], bw[SW * SH];
    static int16_t lw[G1_BLEND_WEIGHT_ENTRIES];
    int kx0, ky0, kx1, ky1, r, c;
    reference_draw(rle, x, y, w, h, flip, ref_level, left, top, right, bottom);
    if (!g1_blend_level_weights(level_table, key_level, lw)) return -3;
    memset(idx, 0, sizeof(idx));
    memset(mask, 0, sizeof(mask));
    if (g1_blend_decode_rle(rle, used, (size_t)w, (size_t)h, idx, mask) == 0u) return -2;
    if (flip) {
        g1_blend_flip_rows(idx, (size_t)w, (size_t)h);
        g1_blend_flip_rows(mask, (size_t)w, (size_t)h);
    }
    if (!g1_blend_clip_window(x, y, x + w, y + h, left, top, right, bottom, &kx0, &ky0, &kx1, &ky1)) {
        for (r = 0; r < SW * SH; ++r) assert(!touched[r]);
        return -1;
    }
    g1_blend_crop(idx, (size_t)w, (size_t)(kx0 - x), (size_t)(ky0 - y), (size_t)(kx1 - kx0), (size_t)(ky1 - ky0), vidx);
    g1_blend_crop(mask, (size_t)w, (size_t)(kx0 - x), (size_t)(ky0 - y), (size_t)(kx1 - kx0), (size_t)(ky1 - ky0), vmask);
    g1_blend_remap_plane(key_remap, vidx, vmask, (size_t)(kx1 - kx0) * (size_t)(ky1 - ky0), vsrc);
    for (r = 0; r < SH; ++r)
        for (c = 0; c < SW; ++c)
            if (touched[r * SW + c]) assert(c >= kx0 && c < kx1 && r >= ky0 && r < ky1);
    for (r = 0; r < ky1 - ky0; ++r)
        for (c = 0; c < kx1 - kx0; ++c) {
            bw[r * (kx1 - kx0) + c] = before_screen[(ky0 + r) * SW + kx0 + c];
            assert(touched[(ky0 + r) * SW + kx0 + c] == vmask[r * (kx1 - kx0) + c]);   /* the mask is exactly the writes */
        }
    return g1_blend_selfcheck(palette, inverse, lw, bw, vsrc, vmask, (size_t)(kx1 - kx0), (size_t)(ky1 - ky0),
                              after_screen + ky0 * SW + kx0, SW, checked);
}
"""

# 6 x 4 stream: row 0: skip 1, tokens 1-5 | row 1: columns 0 1, skip 3, column 5 | row 2: skip 2, columns 2 3, skip 0, 4 5 | row 3: column 0, skip 4, skip 1
_LEVEL_STREAM = r"""
    uint8_t rle[64];
    size_t n = 0u, i;
    const int program[] = {-1, 1, 0, 1, 2, 3, 4,   5, 6, -1, 3, 7,   -1, 2, 8, 9, -1, 0, 10, 11,   12, -1, 4, -1, 1};
    level_tables();
    for (i = 0u; i < sizeof(program) / sizeof(program[0]); ++i) {
        if (program[i] == -1) { rle[n++] = 0xFE; rle[n++] = (uint8_t)program[++i]; }
        else rle[n++] = tokens[program[i]];
    }
    (void)rle;
    (void)n;
"""


def _run_level(tmp_path: Path, tail: str) -> None:
    fixture = tmp_path / "level_key.c"
    executable = tmp_path / "level_key"
    fixture.write_text(_PRELUDE + _LEVEL_REFERENCE + "int main(void) {\n tables();\n weight_table();\n" + _LEVEL_STREAM + tail
                       + "\n return 0; }\n", encoding="utf-8")
    built = subprocess.run(
        ["gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-I", str(STUB), str(fixture), "-o", str(executable)],
        capture_output=True, text=True, check=False,
    )
    assert built.returncode == 0, built.stderr
    ran = subprocess.run([str(executable)], capture_output=True, text=True, check=False)
    assert ran.returncode == 0, ran.stderr


def test_level_slices_are_the_table_builders_ten_and_anything_else_is_refused(tmp_path: Path) -> None:
    """B4-0 (2): 0x4654D0 fills 10 slices of 64 x 64 DWORDs; a level outside 0..9 or an entry beyond int16 is refused, never guessed."""
    _run_level(tmp_path, r"""
    static int16_t out[G1_BLEND_WEIGHT_ENTRIES];
    int level;
    uint32_t entry;
    assert(G1_BLEND_LEVEL_SLICES == 10u && SLICES == 10);
    for (level = 0; level < SLICES; ++level) {
        assert(g1_blend_level_weights(level_table, level, out) == 1);
        for (entry = 0u; entry < G1_BLEND_WEIGHT_ENTRIES; ++entry) assert((uint32_t)(int32_t)out[entry] == level_table[level * 4096 + entry]);
    }
    assert(level_table[0 * 4096 + (5 << 6) + 9] == 9u && level_table[0 * 4096 + (9 << 6) + 5] == 9u);     /* level 0: max(d, s) */
    assert(level_table[9 * 4096 + (0 << 6) + 40] == 4u);                                                  /* level 9: 40 - floor(90 * 40 / 100) */
    assert(g1_blend_level_weights(level_table, -1, out) == 0);
    assert(g1_blend_level_weights(level_table, 10, out) == 0);
    assert(g1_blend_level_weights(level_table, 32767, out) == 0);
    assert(g1_blend_level_weights(level_table, 3, NULL) == 0 && g1_blend_level_weights(NULL, 3, out) == 0);
    level_table[3 * 4096 + 77] = 40000u;                                                                 /* beyond int16: no guess */
    assert(g1_blend_level_weights(level_table, 3, out) == 0);
    assert(g1_blend_level_weights(level_table, 2, out) == 1 && g1_blend_level_weights(level_table, 4, out) == 1);
    level_table[3 * 4096 + 77] = 0xFFFFFFFBu;                                                            /* -5 survives the round trip, sign kept */
    assert(g1_blend_level_weights(level_table, 3, out) == 1 && out[77] == -5);
    level_table[3 * 4096 + 77] = 0x00008000u;                                                            /* 32768 does not */
    assert(g1_blend_level_weights(level_table, 3, out) == 0);
""")


def test_every_destination_and_token_blends_like_the_original_for_every_level(tmp_path: Path) -> None:
    """B4-2: remap (S), level (L), DWORD table (W) and the shared weighted core give the original's pixel for all 10 x 256 x 256 cases."""
    _run_level(tmp_path, r"""
    static int16_t lw[G1_BLEND_WEIGHT_ENTRIES];
    int level, d, token;
    unsigned differ = 0u;
    for (level = 0; level < SLICES; ++level) {
        assert(g1_blend_level_weights(level_table, level, lw) == 1);
        for (d = 0; d < 256; ++d)
            for (token = 0; token < 256; ++token) {
                uint8_t want = 0u, got = 0u, other = 0u;
                int ok = original_level(level, (uint8_t)d, (uint8_t)token, &want);
                assert(ok == g1_blend_pixel(palette, inverse, lw, (uint8_t)d, remap[token], &got));
                if (ok) assert(want == got);
                /* S: the identity remap, L: the neighbouring level and W: the 0x467580 table all change some result */
                if (ok && g1_blend_pixel(palette, inverse, lw, (uint8_t)d, (uint8_t)token, &other) && other != got) ++differ;
            }
    }
    assert(differ > 10000u);
    { /* L: levels 0 and 9 disagree on enough pairs that a level ignored (pinned to 0) cannot pass the stream checks below */
        static int16_t lw0[G1_BLEND_WEIGHT_ENTRIES], lw9[G1_BLEND_WEIGHT_ENTRIES];
        unsigned level_differ = 0u;
        assert(g1_blend_level_weights(level_table, 0, lw0) && g1_blend_level_weights(level_table, 9, lw9));
        for (d = 0; d < 256; ++d)
            for (token = 0; token < 256; ++token) {
                uint8_t a, b;
                if (g1_blend_pixel(palette, inverse, lw0, (uint8_t)d, remap[token], &a) &&
                    g1_blend_pixel(palette, inverse, lw9, (uint8_t)d, remap[token], &b) && a != b) ++level_differ;
            }
        assert(level_differ > 10000u);
    }
""")


def test_remapped_writers_key_exactly_the_cells_the_reference_writes_and_every_input_matters(tmp_path: Path) -> None:
    """B4-2 mutants: remap omitted, level ignored/changed, flip omitted, clip window omitted, wrong flip direction -> self check fails."""
    _run_level(tmp_path, r"""
    size_t checked = 0u;
    int level;
    /* 0x4678C0 (no flip), unclipped within the screen: the stream has 13 opaque pixels */
    for (level = 0; level < SLICES; ++level)
        assert(keyed_check7(rle, n, 8, 5, 6, 4, 0, level, level, remap, -1000, -1000, 1000, 1000, &checked) == 1 && checked == 13u);
    assert(keyed_check7(rle, n, 8, 5, 6, 4, 0, 3, 4, remap, -1000, -1000, 1000, 1000, &checked) == 0);       /* level changed */
    assert(keyed_check7(rle, n, 8, 5, 6, 4, 0, 3, 0, remap, -1000, -1000, 1000, 1000, &checked) == 0);       /* level ignored (0) */
    assert(keyed_check7(rle, n, 8, 5, 6, 4, 0, 9, 8, remap, -1000, -1000, 1000, 1000, &checked) == 0);
    assert(keyed_check7(rle, n, 8, 5, 6, 4, 0, 3, 3, identity, -1000, -1000, 1000, 1000, &checked) == 0);    /* remap omitted */
    assert(keyed_check7(rle, n, 8, 5, 6, 4, 0, 3, 10, remap, -1000, -1000, 1000, 1000, &checked) == -3);     /* level outside the table */
    assert(keyed_check7(rle, n, 8, 5, 6, 4, 0, 3, -1, remap, -1000, -1000, 1000, 1000, &checked) == -3);
    /* 0x468360 (flip): the token at stream column c lands on x + w - c - 1 */
    for (level = 0; level < SLICES; ++level)
        assert(keyed_check7(rle, n, 8, 5, 6, 4, 1, level, level, remap, -1000, -1000, 1000, 1000, &checked) == 1 && checked == 13u);
    assert(keyed_check7(rle, n, 0, 0, 6, 4, 1, 5, 5, remap, -1000, -1000, 1000, 1000, &checked) == 1);        /* screen corner */
    assert(keyed_check7(rle, n, 34, 16, 6, 4, 1, 5, 5, remap, -1000, -1000, 1000, 1000, &checked) == 1);      /* far corner */
    assert(keyed_check7(rle, n, 8, 5, 6, 4, 1, 5, 6, remap, -1000, -1000, 1000, 1000, &checked) == 0);
    assert(keyed_check7(rle, n, 8, 5, 6, 4, 1, 5, 5, identity, -1000, -1000, 1000, 1000, &checked) == 0);
    /* the clip window (renderer + 0x4D0..0x4DC, right and bottom inclusive), both directions */
    for (level = 2; level < 10; level += 7) {
        int flip;
        for (flip = 0; flip < 2; ++flip) {
            assert(keyed_check7(rle, n, 8, 5, 6, 4, flip, level, level, remap, 10, 0, 799, 599, &checked) == 1);     /* left clip */
            assert(keyed_check7(rle, n, 8, 5, 6, 4, flip, level, level, remap, 0, 0, 11, 599, &checked) == 1);       /* right inclusive */
            assert(keyed_check7(rle, n, 8, 5, 6, 4, flip, level, level, remap, 0, 7, 799, 599, &checked) == 1);      /* rows above parsed, not written */
            assert(keyed_check7(rle, n, 8, 5, 6, 4, flip, level, level, remap, 0, 0, 799, 6, &checked) == 1);        /* bottom inclusive */
            assert(keyed_check7(rle, n, 8, 5, 6, 4, flip, level, level, remap, 9, 6, 12, 7, &checked) == 1);         /* all four sides */
            assert(keyed_check7(rle, n, 8, 5, 6, 4, flip, level, level, remap, 8, 8, 8, 8, &checked) == 1);          /* one pixel */
            assert(keyed_check7(rle, n, 8, 5, 6, 4, flip, level, level, remap, 14, 0, 799, 599, &checked) == -1);    /* empty windows */
            assert(keyed_check7(rle, n, 8, 5, 6, 4, flip, level, level, remap, 0, 0, 7, 599, &checked) == -1);
            assert(keyed_check7(rle, n, 8, 5, 6, 4, flip, level, level, remap, 0, 9, 799, 599, &checked) == -1);
        }
    }
""")


def test_wrong_flip_direction_is_caught_by_the_self_check(tmp_path: Path) -> None:
    """B4-2 mutant 'flip omitted': the planes of 0x468360 left in stream direction must not pass (and the reverse for 0x4678C0)."""
    _run_level(tmp_path, r"""
    static uint8_t idx[SW * SH], mask[SW * SH], vsrc[SW * SH], bw[SW * SH];
    static int16_t lw[G1_BLEND_WEIGHT_ENTRIES];
    size_t checked = 0u;
    int flip, r, c;
    assert(g1_blend_level_weights(level_table, 4, lw) == 1);
    for (flip = 0; flip < 2; ++flip) {
        reference_draw(rle, 8, 5, 6, 4, flip, 4, -1000, -1000, 1000, 1000);
        memset(idx, 0, sizeof(idx));
        memset(mask, 0, sizeof(mask));
        assert(g1_blend_decode_rle(rle, n, 6u, 4u, idx, mask) == n);
        if (!flip) g1_blend_flip_rows(idx, 6u, 4u), g1_blend_flip_rows(mask, 6u, 4u);                  /* the WRONG direction for each writer */
        g1_blend_remap_plane(remap, idx, mask, 24u, vsrc);
        for (r = 0; r < 4; ++r) for (c = 0; c < 6; ++c) bw[r * 6 + c] = before_screen[(5 + r) * SW + 8 + c];
        assert(g1_blend_selfcheck(palette, inverse, lw, bw, vsrc, mask, 6u, 4u, after_screen + 5 * SW + 8, SW, &checked) == 0);
    }
""")


def test_both_remapped_blend_wrappers_key_after_the_diff_mirror_with_remap_level_and_clip_window() -> None:
    """B4-1 wrappers: source contract for 0x4678C0 (plain switch) and 0x468360 (flip switch)."""
    for name, end, switch, writer, stats, before, original in (
            ("mirror_blend_clip7", "H-U: 0x468360", "g1_hd_asset_blend_key_path", "G1_BLEND_CLIP7", "g_blend_clip7_key",
             "g_blend_clip7_before", "g_original_blend_clip7"),
            ("mirror_blend_flip7", "H-Q: 0x467FD0", "g1_hd_asset_blend_flip_key_path", "G1_BLEND_FLIP7", "g_blend_flip7_key",
             "g_blend_flip7_before", "g_original_blend_flip7")):
        wrapper = _wrapper(name, end)
        assert f"key_try = {switch}();" in wrapper, name
        assert ("if (key_try && (size_t)width * (size_t)height > G1_BLEND_KEY_MAX_PIXELS) {\n"
                f"                ++{stats}.key_fallbacks;\n                key_try = FALSE;") in wrapper, name
        window = wrapper[wrapper.index("!g1_blend_clip_window("):wrapper.index("if (key_try) {")]
        assert f"++{stats}.key_clip_empty;" in window and "key_try = FALSE;" in window, name
        snapshot = wrapper.index("blend_key_snapshot(kx0, ky0, kx1 - kx0, ky1 - ky0);")
        assert wrapper.index("!g1_blend_clip_window(") < snapshot < wrapper.index(f"{original}(renderer"), name
        assert (f"g1_blend_crop({before}, (size_t)(x1 - x0), (size_t)(kx0 - x0), (size_t)(ky0 - y0)," in wrapper and
                "(size_t)(kx1 - kx0), (size_t)(ky1 - ky0), g_blend_clip_key_before);" in wrapper), name
        assert "key_cut = kx0 != x0 || ky0 != y0 || kx1 != x1 || ky1 != y1;" in wrapper, name
        block = wrapper[wrapper.index("if (key_try) {", wrapper.index("g1_overlay_blt_apply(")):]
        # the remap table and level are set right before the shared core and dropped right after it
        assert block.index("blend_key_set_remap(remap, level);") < block.index("blend_key_apply(") < block.index("g_blend_key_remap = NULL;"), name
        assert (f"blend_key_apply(renderer, {writer}, TRUE, rle, x, y, width, height, kx0, ky0, kx1 - kx0," in block and
                f"ky1 - ky0, buffer, stride, g_blend_clip_key_before, &{stats})" in block), name
        assert f"++{stats}.keyed_calls;" in block and f"++{stats}.key_fallbacks;" in block, name
        assert f"if (key_cut) ++{stats}.key_clip_cut;" in block, name
        assert block.count("key_clip_cut") == 1 and block.index("key_clip_cut") < block.index(f"++{stats}.key_fallbacks;"), name
        assert "active = FALSE;" not in wrapper, name
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    setter = mirror[mirror.index("static void blend_key_set_remap("):mirror.index("/* H-P: 0x4678C0")]
    assert "g_blend_key_remap_digest = auxiliary_digest((const BYTE *)(ULONG_PTR)remap, 256u, &valid);" in setter
    assert "g_blend_key_remap = valid && remap != 0u ? (const BYTE *)(ULONG_PTR)remap : NULL;" in setter
    assert "g_blend_key_level = (int16_t)level;" in setter                                  # movsx of the low 16 bits, like the original


def test_every_clip_wrapper_reads_exactly_the_four_renderer_clip_fields() -> None:
    """B4-0 (3) (lap1197 survivor a4): a key window built from anything but the renderer clip (constants, a second call) must turn this RED."""
    reads = ("*(const volatile int32_t *)((BYTE *)renderer + G1_RENDERER_VIEWPORT),\n"
             "                                      *(const volatile int32_t *)((BYTE *)renderer + G1_RENDERER_VIEWPORT + 4u),\n"
             "                                      *(const volatile int32_t *)((BYTE *)renderer + G1_RENDERER_VIEWPORT + 8u),\n"
             "                                      *(const volatile int32_t *)((BYTE *)renderer + G1_RENDERER_VIEWPORT + 12u),\n"
             "                                      &kx0, &ky0, &kx1, &ky1)")
    for name, end in (("mirror_blend_clip", "H-D2r: 0x4685C0"), ("mirror_blend_skip", "H-P: 0x4678C0"),
                      ("mirror_blend_clip7", "H-U: 0x468360"), ("mirror_blend_flip7", "H-Q: 0x467FD0")):
        wrapper = _wrapper(name, end)
        assert wrapper.count("g1_blend_clip_window(") == 1, name
        call = wrapper[wrapper.index("g1_blend_clip_window("):]
        assert call.startswith("g1_blend_clip_window(x0, y0, x1, y1,\n"), name
        assert reads in call[:call.index("&kx0") + 40 + len("&kx0, &ky0, &kx1, &ky1)")], name
        assert wrapper.count("blend_key_snapshot(kx0, ky0, kx1 - kx0, ky1 - ky0);") == 1, name
        assert "kx0, ky0, kx1 - kx0," in wrapper[wrapper.index("blend_key_apply("):], name   # the core gets the cut window, never x0/y0


def test_blend_key_apply_refuses_before_decoding_and_feeds_remap_through_the_selfcheck_and_the_asset_key() -> None:
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    core = mirror[mirror.index("static BOOL blend_key_apply("):mirror.index("Original returns: 0x4672E0")]
    assert "const BOOL remapped = writer == G1_BLEND_CLIP7 || writer == G1_BLEND_FLIP7;" in core
    gate = core[core.index("if (remapped) {"):core.index("fill_bytes(g_blend_key_idx")]
    assert "!g_blend_key_remap" in gate and "g1_blend_level_weights((const uint32_t *)((const BYTE *)renderer + 0x43CA0u), g_blend_key_level," in gate
    assert "++stats->key_level_rejects;" in gate and "return FALSE;" in gate and "weights = g_blend_key_level_weights;" in gate
    plane = core[core.index("g1_blend_remap_plane("):core.index("if (!g1_blend_selfcheck(")]
    assert "g_blend_key_remap, g_blend_key_vidx, g_blend_key_vmask," in plane and "source_plane = g_blend_key_vsrc;" in plane
    assert "g1_blend_selfcheck(palette, inverse, weights, before, source_plane, g_blend_key_vmask," in core
    assert (core.index("if (remapped) {") < core.index("g1_blend_decode_rle(") < core.index("g1_blend_remap_plane(") <
            core.index("g1_blend_selfcheck(") < core.index("g1_hd_asset_begin_with_aux(") < core.index("g1_hd_asset_bind_identity_frame("))
    assert ("if (remapped ? !g1_hd_asset_begin_with_aux((const BYTE *)(ULONG_PTR)rle, writer, g_blend_key_remap,\n"
            "                                               g_blend_key_remap_digest, (DWORD)width, (DWORD)height, x, y)\n"
            "                 : !g1_hd_asset_begin((const BYTE *)(ULONG_PTR)rle, writer, (DWORD)width, (DWORD)height, x, y))") in core
    # the identity key and the pack frame stay in stream colours: the bound plane is the decoded stream, not the remapped one
    assert "bind_identity_frame(g_blend_key_idx, (DWORD)width, g_blend_key_mask," in core
    assert "g_blend_key_vsrc" not in core[core.index("g1_hd_asset_bind_identity_frame("):]
    # the weighted draw uses the same per-level weights as the self check
    assert "g1_blend_apply_hd(palette, inverse, weights, g_blend_key_vmask," in core


def test_remapped_blend_writers_share_the_tinted_lut_path_in_the_asset_layer() -> None:
    asset = (STUB / "g1_hd_asset.c").read_text(encoding="utf-8")
    assert "#define G1_HD_BLEND_CLIP7 0x004678C0u" in asset and "#define G1_HD_BLEND_FLIP7 0x00468360u" in asset
    assert "return writer == G1_HD_BLEND_CLIP7 || writer == G1_HD_BLEND_FLIP7;" in asset
    # the table is captured (and digest-checked) at begin, applied to the pack frame at build; PACK_TINTED=0 turns it off with them
    assert "((!g_hd_tinted_off && (is_tinted_pack_writer(writer) || is_remap_blend_writer(writer))) ||" in asset
    assert "if (((is_tinted_pack_writer(key->writer) || is_remap_blend_writer(key->writer)) && !g_hd_tinted_off) ||" in asset
    assert "else if (state == PACK_REJECT || state == PACK_LUT_REJECT) ++g_pack_blend_rejects;" in asset
    # 0x468360 is also a flipped writer (pack rows mirrored); 0x4678C0 is not
    assert "return writer == G1_HD_BLEND_FLIP || writer == G1_HD_BLEND_SKIP || writer == G1_HD_BLEND_FLIP7;" in asset
    assert "G1_HD_BLEND_CLIP7" not in asset[asset.index("static BOOL is_flip_blend_writer("):asset.index("static BOOL is_remap_blend_writer(")]


def test_remapped_key_trace_fields_counters_resets_and_header_are_wired() -> None:
    trace = (STUB / "direct_draw_trace.c").read_text(encoding="utf-8")
    header = (STUB / "g1_mirror2x.h").read_text(encoding="utf-8")
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    reset = mirror[mirror.index("g_blend_rle_key.keyed_calls = 0u;"):]
    counters = ("keyed_calls", "keyed_pixels", "key_fallbacks", "selfcheck_mismatches", "selfcheck_pixels", "key_clip_cut",
                "key_clip_empty", "key_level_rejects")
    for tag, prefix, stats in (("4678C0", "blend_clip7", "g_blend_clip7_key"), ("468360", "blend_flip7", "g_blend_flip7_key")):
        for counter in counters:
            assert f'\\"blend_{tag}_{counter}\\":%u' in trace, (tag, counter)
            assert f"g1_mirror2x_{prefix}_{counter}()" in trace, (tag, counter)
            assert f"DWORD g1_mirror2x_{prefix}_{counter}(void);" in header, (tag, counter)
            assert f"DWORD g1_mirror2x_{prefix}_{counter}(void) {{ return {stats}.{counter}; }}" in mirror, (tag, counter)
            assert f"{stats}.{counter} = 0u;" in reset, (tag, counter)


def test_trace_line_buffer_holds_the_longest_metrics_record() -> None:
    """lap1198 run S1: the metrics event (mirror_details + prefix) exceeded the 10,240 B line and was dropped silently (event_limit overflow)."""
    import re
    trace = (STUB / "direct_draw_trace.c").read_text(encoding="utf-8")
    line = int(re.search(r"char prefix\[1024\];\n    char line\[(\d+)\];", trace).group(1))
    details = max(int(m) for m in re.findall(r"char mirror_details\[(\d+)\];", trace))
    assert line >= details + 1024 + 2                                   # prefix, closing "}\n"


def test_level_ten_is_refused_even_when_eleven_slices_hold_valid_values(tmp_path: Path) -> None:
    """H-HDB5 B5-2: the 11th slice is whatever follows the table in renderer memory; even with int16-sized values there it must not be read."""
    _run_level(tmp_path, r"""
    static uint32_t eleven[(SLICES + 1) * 4096];
    static int16_t out[G1_BLEND_WEIGHT_ENTRIES];
    size_t entry;
    for (entry = 0u; entry < sizeof(eleven) / sizeof(eleven[0]); ++entry) eleven[entry] = (uint32_t)(entry % 61u);
    assert(g1_blend_level_weights(eleven, 9, out) == 1);
    assert(g1_blend_level_weights(eleven, 10, out) == 0);
    assert(g1_blend_level_weights(eleven, 11, out) == 0);
""")


_SET_REMAP_FIXTURE = r"""#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>
#include "g1_blend_key.h"
typedef uint32_t DWORD;
typedef uint8_t BYTE;
typedef int BOOL;
typedef uintptr_t ULONG_PTR;
#define TRUE 1
#define FALSE 0
#define NULL ((void *)0)
static int g_readable = 1;
static BOOL readable_bytes(const BYTE *source, DWORD bytes) { (void)source; (void)bytes; return g_readable; }
static const BYTE *g_blend_key_remap = NULL;
static DWORD g_blend_key_remap_digest = 0u;
static int32_t g_blend_key_level = 0;
@@FUNCTIONS@@
/* DWORD addresses: the originals are 32-bit pointers */
static BYTE *low_page(void)
{
    BYTE *page = mmap(NULL, 4096, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS | MAP_32BIT, -1, 0);
    assert(page != MAP_FAILED);
    return page;
}
"""


def _function_text(source: str, signature: str) -> str:
    start = source.index(signature)
    return source[start:source.index("\n}\n", start) + 3]


def _run_set_remap(tmp_path: Path, body: str) -> None:
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    functions = _function_text(mirror, "static DWORD auxiliary_digest(") + "\n" + _function_text(mirror, "static void blend_key_set_remap(")
    fixture = tmp_path / "set_remap.c"
    executable = tmp_path / "set_remap"
    fixture.write_text(_SET_REMAP_FIXTURE.replace("@@FUNCTIONS@@", functions) + "int main(void) {\n" + body + "\n return 0; }\n",
                       encoding="utf-8")
    built = subprocess.run(["gcc", "-std=gnu11", "-Wall", "-Wextra", "-Werror", "-I", str(STUB), str(fixture), "-o", str(executable)],
                           capture_output=True, text=True, check=False)
    assert built.returncode == 0, built.stderr
    ran = subprocess.run([str(executable)], capture_output=True, text=True, check=False)
    assert ran.returncode == 0, ran.stderr


def test_set_remap_takes_the_level_of_every_call_and_the_slice_follows_it(tmp_path: Path) -> None:
    """H-HDB5 B5-3: the real blend_key_set_remap text, run on the host: two levels in turn each select their own slice (a level kept from the first call would not)."""
    _run_set_remap(tmp_path, r"""
    static uint32_t table[G1_BLEND_LEVEL_SLICES * G1_BLEND_WEIGHT_ENTRIES];
    static int16_t out[G1_BLEND_WEIGHT_ENTRIES];
    BYTE *page = low_page();
    DWORD remap = (DWORD)(uintptr_t)page;
    size_t slice, entry;
    int round;
    for (slice = 0u; slice < G1_BLEND_LEVEL_SLICES; ++slice)
        for (entry = 0u; entry < G1_BLEND_WEIGHT_ENTRIES; ++entry) table[slice * G1_BLEND_WEIGHT_ENTRIES + entry] = (uint32_t)(slice * 5u + 1u);
    for (round = 0; round < 3; ++round) {
        blend_key_set_remap(remap, 2u);
        assert(g_blend_key_level == 2 && g_blend_key_remap == page);
        assert(g1_blend_level_weights(table, g_blend_key_level, out) == 1 && out[0] == 11 && out[G1_BLEND_WEIGHT_ENTRIES - 1u] == 11);
        blend_key_set_remap(remap, 7u);
        assert(g_blend_key_level == 7);
        assert(g1_blend_level_weights(table, g_blend_key_level, out) == 1 && out[0] == 36);
    }
    blend_key_set_remap(remap, 0xFFFF0003u);                                         /* only the low 16 bits are the level argument */
    assert(g_blend_key_level == 3);
    blend_key_set_remap(remap, 0x8000u);                                             /* a negative int16 is refused by the slice check */
    assert(g_blend_key_level == -32768 && g1_blend_level_weights(table, g_blend_key_level, out) == 0);
""")


def test_set_remap_digests_the_256_byte_table_and_refuses_an_unreadable_or_missing_one(tmp_path: Path) -> None:
    _run_set_remap(tmp_path, r"""
    BYTE *page = low_page();
    DWORD remap = (DWORD)(uintptr_t)page, first;
    unsigned i;
    for (i = 0u; i < 256u; ++i) page[i] = (BYTE)i;
    blend_key_set_remap(remap, 1u);
    first = g_blend_key_remap_digest;
    assert(g_blend_key_remap == page && first != 0u);
    page[255] ^= 1u;                                                                 /* the last byte is part of the digest */
    blend_key_set_remap(remap, 1u);
    assert(g_blend_key_remap == page && g_blend_key_remap_digest != first);
    g_readable = 0;
    blend_key_set_remap(remap, 4u);
    assert(g_blend_key_remap == NULL && g_blend_key_level == 4);                    /* an unreadable table: no remap, blend_key_apply refuses */
    g_readable = 1;
    blend_key_set_remap(0u, 5u);
    assert(g_blend_key_remap == NULL && g_blend_key_level == 5);
""")


def test_each_writers_trace_field_reads_its_own_writers_accessor() -> None:
    """H-HDB5 B5-4: field blend_<addr>_<name> pairs, in format order, with g1_mirror2x_blend_<clip7|flip7>_<name>() — a swapped pair of accessors passes the presence-only checks above."""
    import re
    trace = (STUB / "direct_draw_trace.c").read_text(encoding="utf-8")
    owners = {"4678C0": "clip7", "468360": "flip7"}
    paired = {tag: 0 for tag in owners}
    for call in re.finditer(r'wsprintfA\(\w+,\s*((?:"(?:[^"\\]|\\.)*"\s*)+),(.*?)\);', trace, re.DOTALL):
        fields = re.findall(r'\\"blend_(4678C0|468360)_(\w+)\\":%u', call.group(1))
        if not fields:
            continue
        accessors = re.findall(r"\(unsigned\)(g1_mirror2x_\w+)\(\)", call.group(2))
        assert len(fields) == len(accessors), call.group(1)[:80]
        for (tag, name), accessor in zip(fields, accessors):
            assert accessor == f"g1_mirror2x_blend_{owners[tag]}_{name}", (tag, name, accessor)
            paired[tag] += 1
    assert paired == {"4678C0": 17, "468360": 17}, paired
