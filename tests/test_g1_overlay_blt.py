"""Host-side contracts for the G1 colorkey BltFast overlay mirror (H-T)."""

from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STUB = ROOT / "tools/inmm_stub"


def test_overlay_blt_header_mirrors_only_changed_pixels_and_gates_inputs(
    tmp_path: Path,
) -> None:
    fixture = tmp_path / "overlay_blt_contract.c"
    executable = tmp_path / "overlay_blt_contract"
    fixture.write_text(
        r'''#include <assert.h>
#include <stdint.h>
#include <string.h>
#include "g1_overlay_blt.h"

static uint8_t after[832u * 600u];
static uint8_t expected[800u * 600u];
static uint8_t covered[800u * 600u];
static uint8_t hd[1600u * 1200u];
static uint8_t scratch[G1_OVERLAY_SCRATCH_BYTES];

int main(void) {
    G1OverlayStats stats;
    uint8_t before[4u * 3u];
    size_t i;
    /* gates: primary, panel source, no colorkey, size cap, bounds */
    assert(g1_overlay_blt_accepts(0, 0, 1, 1, 832u, 600u, 618u, 500u, 101u, 40u));
    assert(!g1_overlay_blt_accepts(1, 0, 1, 1, 832u, 600u, 618u, 500u, 101u, 40u));
    assert(!g1_overlay_blt_accepts(0, 1, 1, 1, 832u, 600u, 618u, 500u, 101u, 40u));
    assert(!g1_overlay_blt_accepts(0, 0, 0, 1, 832u, 600u, 618u, 500u, 101u, 40u));
    assert(!g1_overlay_blt_accepts(0, 0, 1, 0, 832u, 600u, 618u, 500u, 101u, 40u));
    assert(!g1_overlay_blt_accepts(0, 0, 1, 1, 832u, 600u, 618u, 500u, 321u, 40u));
    /* save000 lump (lap1028 H-M): 0x467580 call 130x130 at (511,267) was rejected by the old 128 cap */
    assert(g1_overlay_blt_accepts(0, 0, 1, 1, 832u, 600u, 511u, 267u, 130u, 130u));
    assert(g1_overlay_blt_accepts(0, 0, 1, 1, 832u, 600u, 618u, 440u, 101u, 160u));
    assert(!g1_overlay_blt_accepts(0, 0, 1, 1, 832u, 600u, 618u, 400u, 101u, 161u));
    assert(!g1_overlay_blt_accepts(0, 0, 1, 1, 832u, 600u, 700u, 500u, 101u, 40u));
    assert(!g1_overlay_blt_accepts(0, 0, 1, 1, 832u, 600u, 618u, 580u, 101u, 40u));
    assert(!g1_overlay_blt_accepts(0, 0, 1, 1, 640u, 480u, 10u, 10u, 10u, 10u));
    assert(g1_overlay_blt_accepts(0, 0, 1, 1, 800u, 600u, 700u, 560u, 100u, 40u));

    /* background 5 everywhere; blit rect (10,20) 4x3: row0 colorkey (same
     * value, unchanged), the rest changes to 9 except one unchanged pixel */
    memset(after, 5, sizeof(after));
    memset(before, 5, sizeof(before));
    memset(covered, 0, sizeof(covered));
    memset(expected, 0, sizeof(expected));
    memset(hd, 0xA5, sizeof(hd));
    covered[20u * 800u + 10u] = 1u;      /* pre-existing coverage, unchanged pixel */
    expected[20u * 800u + 10u] = 5u;
    hd[20u * 2u * 1600u + 20u] = 0x77u;
    for (i = 4u; i < 12u; ++i) after[(20u + i / 4u) * 832u + 10u + i % 4u] = 9u;
    after[22u * 832u + 13u] = 5u;        /* back to background: unchanged */
    assert(g1_overlay_blt_apply(before, after, 832u, 10u, 20u, 4u, 3u, 1,
                                scratch, expected, covered, hd, 1600u, &stats));
    assert(stats.changed == 7u && stats.unchanged == 5u);
    assert(covered[20u * 800u + 10u] == 1u && expected[20u * 800u + 10u] == 5u);
    assert(hd[20u * 2u * 1600u + 20u] == 0x77u);
    assert(covered[21u * 800u + 10u] == 1u && expected[21u * 800u + 10u] == 9u);
    assert(covered[22u * 800u + 13u] == 0u);
    assert(covered[19u * 800u + 10u] == 0u && covered[20u * 800u + 14u] == 0u);
    /* (11,21): d==f==9 so Scale2x keeps all four subpixels at 9; (10,21) has
     * b=5,d=5,f=9,h=9 so its top-left subpixel takes the 5 neighbour */
    assert(hd[21u * 2u * 1600u + 22u] == 9u && hd[21u * 2u * 1600u + 23u] == 9u);
    assert(hd[(21u * 2u + 1u) * 1600u + 22u] == 9u &&
           hd[(21u * 2u + 1u) * 1600u + 23u] == 9u);
    assert(hd[21u * 2u * 1600u + 20u] == 5u);
    /* border/untouched hd stays as before */
    assert(hd[19u * 2u * 1600u + 20u] == 0xA5u);

    /* nearest mode replicates the post value */
    memset(covered, 0, sizeof(covered));
    memset(hd, 0, sizeof(hd));
    assert(g1_overlay_blt_apply(before, after, 832u, 10u, 20u, 4u, 3u, 0,
                                scratch, expected, covered, hd, 1600u, &stats));
    assert(hd[21u * 2u * 1600u + 20u] == 9u && hd[21u * 2u * 1600u + 21u] == 9u);
    assert(hd[(21u * 2u + 1u) * 1600u + 20u] == 9u &&
           hd[(21u * 2u + 1u) * 1600u + 21u] == 9u);

    /* screen-edge clamp: rect flush with the bottom-right corner */
    memset(after, 5, sizeof(after));
    after[599u * 832u + 799u] = 8u;
    {
        uint8_t edge_before[4] = {5u, 5u, 5u, 5u};
        assert(g1_overlay_blt_apply(edge_before, after, 832u, 798u, 598u, 2u, 2u, 1,
                                    scratch, expected, covered, hd, 1600u, &stats));
        assert(stats.changed == 1u && covered[599u * 800u + 799u] == 1u);
        assert(expected[599u * 800u + 799u] == 8u);
    }

    /* rejected geometry leaves the mirror untouched */
    memset(covered, 0, sizeof(covered));
    assert(!g1_overlay_blt_apply(before, after, 832u, 790u, 20u, 20u, 3u, 1,
                                 scratch, expected, covered, hd, 1600u, &stats));
    assert(covered[20u * 800u + 795u] == 0u);
    assert(!g1_overlay_blt_apply(before, after, 799u, 10u, 20u, 4u, 3u, 1,
                                 scratch, expected, covered, hd, 1600u, &stats));
    return 0;
}
''',
        encoding="utf-8",
    )
    result = subprocess.run(
        ["gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-I", str(STUB),
         str(fixture), "-o", str(executable)],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    run = subprocess.run([str(executable)], capture_output=True, text=True, check=False)
    assert run.returncode == 0, run.stderr


def test_production_hook_wires_overlay_mirror_around_ps3_blt_fast() -> None:
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    bridge = (STUB / "direct_draw_trace.c").read_text(encoding="utf-8")
    assert "source == panel_surface" in mirror
    assert mirror.count("++g_overlay_blt_mirrored_calls") == 1
    begin = bridge.index("g1_mirror2x_overlay_blt_begin(&overlay_blt")
    original = bridge.index("record->original_blt_fast(self, x, y, source, src, flags)", begin)
    end = bridge.index("g1_mirror2x_overlay_blt_end(&overlay_blt", original)
    assert begin < original < end
    assert "read_state(0x004ED818u) == 3u" in bridge[begin - 120:begin]
    for key in ("overlay_blt_mirrored_calls", "overlay_blt_mirrored_pixels",
                "overlay_blt_rejects"):
        assert key in bridge


def test_overlay_blt_banded_apply_equals_whole_frame_scale2x(tmp_path: Path) -> None:
    """H-D2r R-0: rects taller than G1_OVERLAY_MAX_HEIGHT are applied in row bands whose
    result must equal a single whole-frame Scale2x of the post frame (the apply halo reads
    the real post frame, so band seams are invisible); <=160 rows stays one band."""
    fixture = tmp_path / "overlay_blt_banded.c"
    executable = tmp_path / "overlay_blt_banded"
    fixture.write_text(
        r'''#include <assert.h>
#include <stdint.h>
#include <string.h>
#include "g1_overlay_blt.h"

#define W 800u
#define H 600u
static uint8_t after[832u * H];
static uint8_t before[G1_OVERLAY_MAX_WIDTH * G1_OVERLAY_SCREEN_HEIGHT];
static uint8_t expected[W * H];
static uint8_t covered[W * H];
static uint8_t hd[W * 2u * H * 2u];
static uint8_t ref_hd[W * 2u * H * 2u];
static uint8_t full_mask[W * H];
static uint8_t scratch[G1_OVERLAY_SCRATCH_BYTES];
static uint32_t rng = 12345u;
static uint32_t next(void) { rng = rng * 1664525u + 1013904223u; return rng >> 16; }

static void run_case(size_t x, size_t y, size_t w, size_t h, int scale2x,
                     size_t want_bands) {
    G1OverlayStats stats;
    size_t bands = 99u, row, col, changed = 0u;
    memset(covered, 0, sizeof(covered));
    memset(expected, 0, sizeof(expected));
    memset(hd, 0xA5, sizeof(hd));
    for (row = 0u; row < h; ++row)
        for (col = 0u; col < w; ++col) {
            uint8_t v = after[(y + row) * 832u + x + col];
            before[row * w + col] = (next() & 1u) ? v : (uint8_t)(v ^ 1u);
            if (before[row * w + col] != v) ++changed;
        }
    memset(full_mask, 1, sizeof(full_mask));
    if (scale2x)
        assert(g1_scale2x_build_masked(after, 832u, full_mask, W, W, H, ref_hd, W * 2u));
    assert(g1_overlay_blt_apply_banded(before, after, 832u, x, y, w, h, scale2x, scratch,
                                       expected, covered, hd, W * 2u, &stats, &bands));
    assert(bands == want_bands);
    assert(stats.changed == changed && stats.changed + stats.unchanged == w * h);
    for (row = 0u; row < h; ++row)
        for (col = 0u; col < w; ++col) {
            size_t sx = x + col, sy = y + row;
            uint8_t v = after[sy * 832u + sx];
            uint8_t *out = hd + sy * 2u * (W * 2u) + sx * 2u;
            if (before[row * w + col] == v) {
                assert(!covered[sy * W + sx] && out[0] == 0xA5u);
                continue;
            }
            assert(covered[sy * W + sx] == 1u && expected[sy * W + sx] == v);
            if (scale2x) {
                const uint8_t *r = ref_hd + sy * 2u * (W * 2u) + sx * 2u;
                assert(out[0] == r[0] && out[1] == r[1]);
                assert(out[W * 2u] == r[W * 2u] && out[W * 2u + 1u] == r[W * 2u + 1u]);
            } else {
                assert(out[0] == v && out[1] == v && out[W * 2u] == v && out[W * 2u + 1u] == v);
            }
        }
}

int main(void) {
    size_t i, s;
    G1OverlayStats stats;
    size_t bands = 0u;
    for (i = 0u; i < sizeof(after); ++i) after[i] = (uint8_t)(2u + (next() % 3u));
    for (s = 0u; s < 2u; ++s) {
        run_case(0u, 30u, 163u, 200u, (int)s, 2u);    /* lap1061 0x467B00 reject: 330x200 clipped */
        run_case(0u, 30u, 320u, 570u, (int)s, 4u);    /* tallest: 570 rows = 4 bands */
        run_case(10u, 0u, 320u, 600u, (int)s, 4u);    /* full screen height */
        run_case(5u, 400u, 100u, 200u, (int)s, 2u);   /* flush with the bottom edge */
        run_case(20u, 20u, 100u, 160u, (int)s, 1u);   /* <=160 rows: single band */
        run_case(20u, 20u, 100u, 161u, (int)s, 2u);   /* boundary: 161 rows */
        run_case(20u, 20u, 50u, 1u, (int)s, 1u);
    }
    /* single band equals plain apply byte for byte */
    {
        static uint8_t hd2[W * 2u * H * 2u];
        static uint8_t cov2[W * H], exp2[W * H];
        size_t row, col;
        for (row = 0u; row < 40u; ++row)
            for (col = 0u; col < 90u; ++col) before[row * 90u + col] = (uint8_t)(after[(50u + row) * 832u + 33u + col] ^ ((row + col) & 1u));
        memset(hd, 0, sizeof(hd)); memset(hd2, 0, sizeof(hd2));
        memset(covered, 0, sizeof(covered)); memset(cov2, 0, sizeof(cov2));
        memset(expected, 0, sizeof(expected)); memset(exp2, 0, sizeof(exp2));
        assert(g1_overlay_blt_apply(before, after, 832u, 33u, 50u, 90u, 40u, 1, scratch, exp2, cov2, hd2, W * 2u, &stats));
        assert(g1_overlay_blt_apply_banded(before, after, 832u, 33u, 50u, 90u, 40u, 1, scratch, expected, covered, hd, W * 2u, &stats, &bands));
        assert(bands == 1u);
        assert(!memcmp(hd, hd2, sizeof(hd)) && !memcmp(covered, cov2, sizeof(covered)) && !memcmp(expected, exp2, sizeof(expected)));
    }
    /* rejects leave the mirror untouched and report no bands */
    memset(covered, 0, sizeof(covered));
    bands = 7u;
    assert(!g1_overlay_blt_apply_banded(before, after, 832u, 0u, 0u, 321u, 200u, 1, scratch, expected, covered, hd, W * 2u, &stats, &bands));
    assert(!g1_overlay_blt_apply_banded(before, after, 832u, 0u, 500u, 100u, 101u, 1, scratch, expected, covered, hd, W * 2u, &stats, &bands));
    assert(!g1_overlay_blt_apply_banded(before, after, 832u, 0u, 0u, 100u, 0u, 1, scratch, expected, covered, hd, W * 2u, &stats, &bands));
    assert(bands == 0u);
    for (i = 0u; i < sizeof(covered); ++i) assert(!covered[i]);
    return 0;
}
''',
        encoding="utf-8",
    )
    result = subprocess.run(
        ["gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-I", str(STUB),
         str(fixture), "-o", str(executable)],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    run = subprocess.run([str(executable)], capture_output=True, text=True, check=False)
    assert run.returncode == 0, run.stderr


def test_overlay_blt_tiled_apply_equals_whole_frame_scale2x(tmp_path: Path) -> None:
    """H-D2t T-2: rects wider than G1_OVERLAY_MAX_WIDTH (selection outlines up to the whole
    screen) are applied in <=320x160 tiles from one full-size before copy; the tiles together
    must equal a single whole-frame Scale2x of the post frame (halo reads the real post
    frame, so tile seams are invisible)."""
    fixture = tmp_path / "overlay_blt_tiled.c"
    executable = tmp_path / "overlay_blt_tiled"
    fixture.write_text(
        r'''#include <assert.h>
#include <stdint.h>
#include <string.h>
#include "g1_overlay_blt.h"

#define W 800u
#define H 600u
static uint8_t after[832u * H];
static uint8_t before[W * H];
static uint8_t tile[G1_OVERLAY_MAX_WIDTH * G1_OVERLAY_MAX_HEIGHT];
static uint8_t expected[W * H];
static uint8_t covered[W * H];
static uint8_t hd[W * 2u * H * 2u];
static uint8_t ref_hd[W * 2u * H * 2u];
static uint8_t full_mask[W * H];
static uint8_t scratch[G1_OVERLAY_SCRATCH_BYTES];
static uint32_t rng = 777u;
static uint32_t next(void) { rng = rng * 1664525u + 1013904223u; return rng >> 16; }

static void run_case(size_t x, size_t y, size_t w, size_t h, int scale2x,
                     size_t want_tiles) {
    G1OverlayStats stats;
    size_t tiles = 99u, row, col, changed = 0u;
    memset(covered, 0, sizeof(covered));
    memset(expected, 0, sizeof(expected));
    memset(hd, 0xA5, sizeof(hd));
    for (row = 0u; row < h; ++row)
        for (col = 0u; col < w; ++col) {
            uint8_t v = after[(y + row) * 832u + x + col];
            before[row * w + col] = (next() & 1u) ? v : (uint8_t)(v ^ 1u);
            if (before[row * w + col] != v) ++changed;
        }
    memset(full_mask, 1, sizeof(full_mask));
    if (scale2x)
        assert(g1_scale2x_build_masked(after, 832u, full_mask, W, W, H, ref_hd, W * 2u));
    assert(g1_overlay_blt_apply_tiled(before, after, 832u, x, y, w, h, scale2x, scratch, tile,
                                      expected, covered, hd, W * 2u, &stats, &tiles));
    assert(tiles == want_tiles);
    assert(stats.changed == changed && stats.changed + stats.unchanged == w * h);
    for (row = 0u; row < h; ++row)
        for (col = 0u; col < w; ++col) {
            size_t sx = x + col, sy = y + row;
            uint8_t v = after[sy * 832u + sx];
            uint8_t *out = hd + sy * 2u * (W * 2u) + sx * 2u;
            if (before[row * w + col] == v) {
                assert(!covered[sy * W + sx] && out[0] == 0xA5u);
                continue;
            }
            assert(covered[sy * W + sx] == 1u && expected[sy * W + sx] == v);
            if (scale2x) {
                const uint8_t *r = ref_hd + sy * 2u * (W * 2u) + sx * 2u;
                assert(out[0] == r[0] && out[1] == r[1]);
                assert(out[W * 2u] == r[W * 2u] && out[W * 2u + 1u] == r[W * 2u + 1u]);
            } else {
                assert(out[0] == v && out[1] == v && out[W * 2u] == v && out[W * 2u + 1u] == v);
            }
        }
}

int main(void) {
    size_t i, s;
    G1OverlayStats stats;
    size_t tiles = 0u;
    for (i = 0u; i < sizeof(after); ++i) after[i] = (uint8_t)(2u + (next() % 3u));
    for (s = 0u; s < 2u; ++s) {
        run_case(100u, 40u, 226u, 136u, (int)s, 1u);   /* lap1065 p314 drag box: one tile */
        run_case(0u, 0u, 320u, 160u, (int)s, 1u);      /* exactly one tile */
        run_case(0u, 0u, 321u, 160u, (int)s, 2u);      /* boundary: 321 columns */
        run_case(0u, 0u, 320u, 161u, (int)s, 2u);      /* boundary: 161 rows */
        run_case(33u, 21u, 641u, 330u, (int)s, 9u);    /* 3 x 3 tiles */
        run_case(0u, 0u, 800u, 600u, (int)s, 12u);     /* whole screen: 3 x 4 tiles */
        run_case(799u, 599u, 1u, 1u, (int)s, 1u);      /* last pixel */
        run_case(34u, 0u, 330u, 74u, (int)s, 2u);      /* lap1083 330x200 at (34,-126), screen part */
        run_case(473u, 98u, 327u, 200u, (int)s, 4u);   /* 330x200 at (473,98) clipped at x=800 */
        run_case(9u, 294u, 330u, 200u, (int)s, 4u);    /* 330x200 at (9,294) */
    }
    /* rejects leave the mirror untouched and report no tiles */
    memset(covered, 0, sizeof(covered));
    tiles = 7u;
    assert(!g1_overlay_blt_apply_tiled(before, after, 832u, 0u, 0u, 801u, 100u, 1, scratch, tile, expected, covered, hd, W * 2u, &stats, &tiles));
    assert(!g1_overlay_blt_apply_tiled(before, after, 832u, 0u, 0u, 100u, 601u, 1, scratch, tile, expected, covered, hd, W * 2u, &stats, &tiles));
    assert(!g1_overlay_blt_apply_tiled(before, after, 832u, 700u, 0u, 101u, 100u, 1, scratch, tile, expected, covered, hd, W * 2u, &stats, &tiles));
    assert(!g1_overlay_blt_apply_tiled(before, after, 832u, 0u, 500u, 100u, 101u, 1, scratch, tile, expected, covered, hd, W * 2u, &stats, &tiles));
    assert(!g1_overlay_blt_apply_tiled(before, after, 832u, 0u, 0u, 0u, 10u, 1, scratch, tile, expected, covered, hd, W * 2u, &stats, &tiles));
    assert(!g1_overlay_blt_apply_tiled(before, after, 832u, 0u, 0u, 10u, 0u, 1, scratch, tile, expected, covered, hd, W * 2u, &stats, &tiles));
    assert(!g1_overlay_blt_apply_tiled(before, after, 832u, 0u, 0u, 10u, 10u, 1, scratch, NULL, expected, covered, hd, W * 2u, &stats, &tiles));
    assert(tiles == 0u);
    for (i = 0u; i < sizeof(covered); ++i) assert(!covered[i]);
    return 0;
}
''',
        encoding="utf-8",
    )
    result = subprocess.run(
        ["gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-I", str(STUB),
         str(fixture), "-o", str(executable)],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    run = subprocess.run([str(executable)], capture_output=True, text=True, check=False)
    assert run.returncode == 0, run.stderr
