"""Host-side contracts for the G1 0x466070 clipped rect-fill diff mirror (H-F)."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STUB = ROOT / "tools/inmm_stub"


def install_reset(mirror: str) -> str:
    return mirror[mirror.index("g1_mirror2x_primitives_install"):]


def test_rect_fill_region_matches_original_pair_sort_and_clip(tmp_path: Path) -> None:
    fixture = tmp_path / "rect_fill_contract.c"
    executable = tmp_path / "rect_fill_contract"
    fixture.write_text(
        r'''#include <assert.h>
#include <stdint.h>
#include "g1_rect_fill.h"

int main(void) {
    const int32_t screen[4] = {0, 0, 799, 599};
    const int32_t inner[4] = {100, 50, 199, 149};
    G1RectFill r;
    /* plain rect, both ends inclusive */
    assert(g1_rect_fill_region(401, 153, 494, 159, screen, &r));
    assert(r.x == 401 && r.y == 153 && r.width == 94u && r.height == 7u);
    /* flipped pairs are swapped per axis */
    assert(g1_rect_fill_region(494, 159, 401, 153, screen, &r));
    assert(r.x == 401 && r.y == 153 && r.width == 94u && r.height == 7u);
    assert(g1_rect_fill_region(494, 153, 401, 159, screen, &r));
    assert(r.x == 401 && r.y == 153 && r.width == 94u && r.height == 7u);
    /* single point */
    assert(g1_rect_fill_region(5, 6, 5, 6, screen, &r));
    assert(r.x == 5 && r.y == 6 && r.width == 1u && r.height == 1u);
    /* partial clip on every side */
    assert(g1_rect_fill_region(90, 40, 210, 160, inner, &r));
    assert(r.x == 100 && r.y == 50 && r.width == 100u && r.height == 100u);
    /* clip edges are inclusive */
    assert(g1_rect_fill_region(199, 149, 300, 300, inner, &r));
    assert(r.x == 199 && r.y == 149 && r.width == 1u && r.height == 1u);
    assert(g1_rect_fill_region(0, 0, 100, 50, inner, &r));
    assert(r.x == 100 && r.y == 50 && r.width == 1u && r.height == 1u);
    /* completely outside, each side */
    assert(!g1_rect_fill_region(0, 60, 99, 70, inner, &r));
    assert(!g1_rect_fill_region(200, 60, 300, 70, inner, &r));
    assert(!g1_rect_fill_region(110, 0, 120, 49, inner, &r));
    assert(!g1_rect_fill_region(110, 150, 120, 200, inner, &r));
    /* negative / huge coordinates do not wrap */
    assert(g1_rect_fill_region(-50, -50, 5, 5, screen, &r));
    assert(r.x == 0 && r.y == 0 && r.width == 6u && r.height == 6u);
    assert(g1_rect_fill_region(INT32_MIN, INT32_MIN, INT32_MAX, INT32_MAX, screen, &r));
    assert(r.x == 0 && r.y == 0 && r.width == 800u && r.height == 600u);
    /* inverted clip (xmin > xmax) paints nothing */
    {
        const int32_t bad[4] = {10, 10, 5, 20};
        assert(!g1_rect_fill_region(0, 0, 50, 50, bad, &r));
    }
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


def test_rect_screen_region_intersects_clip_with_visible_screen(tmp_path: Path) -> None:
    """H-LB: the 0x465B30 box is the clipped rectangle limited to the visible screen."""
    fixture = tmp_path / "rect_screen_contract.c"
    executable = tmp_path / "rect_screen_contract"
    fixture.write_text(
        r'''#include <assert.h>
#include <stdint.h>
#include "g1_rect_fill.h"

int main(void) {
    const int32_t wide[4] = {0, 0, 831, 599};
    const int32_t screen[4] = {0, 0, 799, 599};
    G1RectFill r;
    /* clip opens into the stride padding: only the visible column x=799 remains */
    assert(g1_rect_screen_region(799, 48, 840, 50, wide, 800, 600, &r));
    assert(r.x == 799 && r.y == 48 && r.width == 1u && r.height == 3u);
    /* swapped corners behave like the fill */
    assert(g1_rect_screen_region(840, 50, 799, 48, wide, 800, 600, &r));
    assert(r.x == 799 && r.y == 48 && r.width == 1u && r.height == 3u);
    /* wholly inside the screen: same as g1_rect_fill_region */
    assert(g1_rect_screen_region(401, 153, 494, 159, wide, 800, 600, &r));
    assert(r.x == 401 && r.y == 153 && r.width == 94u && r.height == 7u);
    /* wholly in the padding: nothing visible */
    assert(!g1_rect_screen_region(800, 10, 831, 20, wide, 800, 600, &r));
    assert(!g1_rect_screen_region(0, 600, 10, 700, wide, 800, 600, &r));
    /* clip rejects first */
    assert(!g1_rect_screen_region(900, 0, 950, 10, screen, 800, 600, &r));
    /* the whole screen is a valid (large) region, taller than one overlay tile */
    assert(g1_rect_screen_region(INT32_MIN, INT32_MIN, INT32_MAX, INT32_MAX, wide, 800, 600, &r));
    assert(r.x == 0 && r.y == 0 && r.width == 800u && r.height == 600u);
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


def test_rect_fill_hook_table_and_wrapper_contract() -> None:
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    header = (STUB / "g1_mirror2x.h").read_text(encoding="utf-8")
    bridge = (STUB / "direct_draw_trace.c").read_text(encoding="utf-8")
    makefile = (STUB / "Makefile").read_text(encoding="utf-8")
    assert '#include "g1_rect_fill.h"' in mirror
    assert "g1_rect_fill.h" in makefile
    assert "#define G1_RECT_FILL 0x00466070u" in mirror
    assert "#define G1_RECT_FILL_LEN 5u" in mirror
    # prologue: mov eax,[esp+4]; push ebx (exact 5-byte instruction boundary)
    assert "expected_rect_fill[G1_RECT_FILL_LEN] =" in mirror
    assert "{0x8B, 0x44, 0x24, 0x04, 0x53}" in mirror
    assert "install_one(G1_RECT_FILL, expected_rect_fill, G1_RECT_FILL_LEN" in mirror
    assert "restore_hook(&g_hook_rect_fill)" in mirror
    assert "g_hook_rect_fill.installed" in mirror
    # original returns: 0x466070 ret 0x14 (5 stack args)
    start = mirror.index("mirror_rect_fill(void *renderer")
    body = mirror[start:mirror.index("BOOL g1_mirror2x_primitives_install(void)", start)]
    assert body.count("DWORD ") >= 5
    assert "g_original_rect_fill(renderer, x1, y1, x2, y2, color)" in body
    # before copy precedes the original call, apply follows it
    before = body.index("g_rect_fill_before")
    original = body.index("g_original_rect_fill(renderer")
    apply_at = body.index("g1_overlay_blt_apply(")
    assert before < original < apply_at
    assert "g1_rect_fill_region(" in body
    assert "g1_overlay_blt_accepts(" in body
    assert "G1_CACHE_BASE" in body and "g_panel_bound_buffer" in body
    assert "g_primitive_guard" in body
    for counter in ("g_rect_fill_invocations", "g_rect_fill_mirrored_calls",
                    "g_rect_fill_mirrored_pixels", "g_rect_fill_reject_target",
                    "g_rect_fill_reject_size", "g_rect_fill_reject_guard"):
        assert counter in mirror
        assert f"{counter} = 0u;" in mirror[mirror.index("g1_mirror2x_primitives_install"):]
    for key in ("rect_fill_466070_invocations", "rect_fill_466070_mirrored_calls",
                "rect_fill_466070_mirrored_pixels", "rect_fill_466070_reject_target",
                "rect_fill_466070_reject_size", "rect_fill_466070_reject_guard"):
        assert key in bridge
    for accessor in ("g1_mirror2x_rect_fill_invocations",
                     "g1_mirror2x_rect_fill_mirrored_calls",
                     "g1_mirror2x_rect_fill_mirrored_pixels",
                     "g1_mirror2x_rect_fill_reject_target",
                     "g1_mirror2x_rect_fill_reject_size",
                     "g1_mirror2x_rect_fill_reject_guard"):
        assert f"DWORD {accessor}(void);" in header


def test_rect_border_hook_table_and_wrapper_contract() -> None:
    """H-F2: 0x465B30 thiscall rectangle border (leaf, ret 0x14) diff mirror."""
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    header = (STUB / "g1_mirror2x.h").read_text(encoding="utf-8")
    bridge = (STUB / "direct_draw_trace.c").read_text(encoding="utf-8")
    assert "#define G1_RECT_BORDER 0x00465B30u" in mirror
    assert "#define G1_RECT_BORDER_LEN 8u" in mirror
    # prologue: sub esp,0x10; push ebx; mov ebx,[esp+0x18] (8 B, no relative branch)
    assert "expected_rect_border[G1_RECT_BORDER_LEN] =" in mirror
    assert "{0x83, 0xEC, 0x10, 0x53, 0x8B, 0x5C, 0x24, 0x18}" in mirror
    assert "install_one(G1_RECT_BORDER, expected_rect_border, G1_RECT_BORDER_LEN" in mirror
    assert "restore_hook(&g_hook_rect_border)" in mirror
    assert "g_hook_rect_border.installed" in mirror
    assert "g_original_rect_border = NULL;" in mirror
    # original returns: 0x465B30 ret 0x14 (5 stack args)
    start = mirror.index("mirror_rect_border(void *renderer")
    body = mirror[start:mirror.index("/* H-D2t:", start)]
    assert body.count("DWORD ") >= 5
    assert "g_original_rect_border(renderer, x1, y1, x2, y2, color)" in body
    before = body.index("g_rect_border_before")
    original = body.index("g_original_rect_border(renderer")
    apply_at = body.index("g1_overlay_blt_apply_tiled(")
    assert before < original < apply_at
    assert body.count("g_original_rect_border(") == 1
    # H-LB: every written pixel lies inside the sorted+clipped rectangle limited to the
    # visible screen (the renderer clip may open into the stride padding), diffed in tiles
    assert "g1_rect_screen_region(" in body
    assert "g1_rect_fill_region(" not in body
    assert "g1_overlay_blt_accepts(" not in body
    assert "g_rect_border_tile" in body
    assert ("static BYTE g_rect_border_before"
            "[G1_OVERLAY_SCREEN_WIDTH * G1_OVERLAY_SCREEN_HEIGHT];") in mirror
    assert "static BYTE g_rect_border_tile[G1_OVERLAY_MAX_WIDTH * G1_OVERLAY_MAX_HEIGHT];" in mirror
    # env-gated reject record (type g, capped), reset per run
    assert '\\"t\\":\\"g\\"' in mirror
    assert "g_rect_border_reject_logged = 0u;" in install_reset(mirror)
    assert "G1_CACHE_BASE" in body and "g_panel_bound_buffer" in body
    assert "g_primitive_guard" in body
    install = mirror[mirror.index("g1_mirror2x_primitives_install"):]
    for counter in ("g_rect_border_invocations", "g_rect_border_mirrored_calls",
                    "g_rect_border_mirrored_pixels", "g_rect_border_reject_target",
                    "g_rect_border_reject_size", "g_rect_border_reject_guard"):
        assert counter in mirror
        assert f"{counter} = 0u;" in install
    for suffix in ("invocations", "mirrored_calls", "mirrored_pixels",
                   "reject_target", "reject_size", "reject_guard"):
        assert f"rect_border_465B30_{suffix}" in bridge
        assert f"DWORD g1_mirror2x_rect_border_{suffix}(void);" in header


def test_rect_border7_hook_table_and_wrapper_contract() -> None:
    """H-D2t T-2: 0x465CA0 thiscall palette-LUT rectangle outline (ret 0x1c, 7 stack args:
    x0 y0 x1 y1 + 3 LUT indices) diff mirror.  The first 5 bytes are not an instruction
    boundary (83 EC 10 | 53 | B8 imm32), so 9 bytes are stolen and the hook state holds them."""
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    header = (STUB / "g1_mirror2x.h").read_text(encoding="utf-8")
    bridge = (STUB / "direct_draw_trace.c").read_text(encoding="utf-8")
    assert "#define G1_RECT_BORDER7 0x00465CA0u" in mirror
    assert "#define G1_RECT_BORDER7_LEN 9u" in mirror
    assert "BYTE original[16];" in mirror and "BYTE patched[16];" in mirror
    assert "expected_rect_border7[G1_RECT_BORDER7_LEN] =" in mirror
    assert re.search(
        r"expected_rect_border7\[G1_RECT_BORDER7_LEN\] =\s*"
        r"\{0x83, 0xEC, 0x10, 0x53, 0xB8, 0x01, 0x00, 0x00, 0x00\};", mirror)
    assert "install_one(G1_RECT_BORDER7, expected_rect_border7, G1_RECT_BORDER7_LEN" in mirror
    assert "restore_hook(&g_hook_rect_border7)" in mirror
    assert "g_hook_rect_border7.installed" in mirror
    assert "g_original_rect_border7 = NULL;" in mirror
    assert "static G1Primitive7Fn g_original_rect_border7" in mirror
    start = mirror.index("mirror_rect_border7(void *renderer")
    end = mirror.index("static DWORD __attribute__((thiscall))", start)
    body = mirror[start:end]
    assert "g_original_rect_border7(renderer, x1, y1, x2, y2, c1, c2, c3)" in body
    assert body.count("g_original_rect_border7(") == 1
    before = body.index("g_rect_border7_before")
    original = body.index("g_original_rect_border7(renderer")
    apply_at = body.index("g1_overlay_blt_apply_tiled(")
    assert before < original < apply_at
    assert "g1_overlay_blt_apply(" not in body
    # every written pixel lies inside the sorted rectangle clipped to the viewport
    assert "g1_rect_fill_region(" in body
    assert "G1_CACHE_BASE" in body and "g_panel_bound_buffer" in body
    assert "g_primitive_guard" in body
    assert ("static BYTE g_rect_border7_before"
            "[G1_OVERLAY_SCREEN_WIDTH * G1_OVERLAY_SCREEN_HEIGHT];") in mirror
    assert "static BYTE g_rect_border7_tile[G1_OVERLAY_MAX_WIDTH * G1_OVERLAY_MAX_HEIGHT];" in mirror
    install = mirror[mirror.index("g1_mirror2x_primitives_install"):]
    for counter in ("g_rect_border7_invocations", "g_rect_border7_mirrored_calls",
                    "g_rect_border7_mirrored_pixels", "g_rect_border7_reject_target",
                    "g_rect_border7_reject_size", "g_rect_border7_reject_guard"):
        assert counter in mirror
        assert f"{counter} = 0u;" in install
    for suffix in ("invocations", "mirrored_calls", "mirrored_pixels",
                   "reject_target", "reject_size", "reject_guard"):
        assert f"rect_border7_465CA0_{suffix}" in bridge
        assert f"DWORD g1_mirror2x_rect_border7_{suffix}(void);" in header
    assert "lstrcatA(mirror_details, rect_border7_details)" in bridge


def test_line_region_covers_every_plot_of_original_clipped_line(tmp_path: Path) -> None:
    """H-LN N-0: 0x4659B0 draws max(|dx|,|dy|)+2 plots through the 0x465900 clip.  The mirror
    region (end-point bbox grown by 1 px, clipped) must contain every plot the original writes."""
    fixture = tmp_path / "line_region_contract.c"
    executable = tmp_path / "line_region_contract"
    fixture.write_text(
        r'''#include <assert.h>
#include <stdint.h>
#include <stdlib.h>
#include "g1_rect_fill.h"

/* 0x4659B0 transcribed from objdump: signs from the differences, both error accumulators
 * start at 0, plot first, accumulate |dx|,|dy|, step an axis when its accumulator exceeds
 * the major span, subtract the span; max+2 iterations. */
static int plot_outside_region(int32_t x0, int32_t y0, int32_t x1, int32_t y1,
                               const int32_t clip[4], int *plots_in_clip, int *overshoot)
{
    int32_t dx = x1 - x0, dy = y1 - y0;
    int32_t sx = dx > 0 ? 1 : (dx == 0 ? 0 : -1);
    int32_t sy = dy > 0 ? 1 : (dy == 0 ? 0 : -1);
    int32_t adx = abs(dx), ady = abs(dy), major = adx > ady ? adx : ady;
    int32_t x = x0, y = y0, ex = 0, ey = 0, left = major + 2;
    int32_t lox = x0 < x1 ? x0 : x1, hix = x0 < x1 ? x1 : x0;
    int32_t loy = y0 < y1 ? y0 : y1, hiy = y0 < y1 ? y1 : y0;
    G1RectFill region;
    int have = g1_line_region(x0, y0, x1, y1, clip, &region);
    int outside = 0;
    while (left--) {
        int in_clip = x >= clip[0] && x <= clip[2] && y >= clip[1] && y <= clip[3];
        int ox = x < lox ? lox - x : (x > hix ? x - hix : 0);
        int oy = y < loy ? loy - y : (y > hiy ? y - hiy : 0);
        if (ox > *overshoot) *overshoot = ox;
        if (oy > *overshoot) *overshoot = oy;
        if (in_clip) {
            ++*plots_in_clip;
            if (!have || x < region.x || y < region.y ||
                x >= region.x + (int32_t)region.width ||
                y >= region.y + (int32_t)region.height)
                ++outside;
        }
        ex += adx;
        ey += ady;
        if (ex > major) { x += sx; ex -= major; }
        if (ey > major) { y += sy; ey -= major; }
    }
    return outside;
}

int main(void) {
    const int32_t clip[4] = {0, 0, 39, 29};
    int plots = 0, overshoot = 0, outside = 0;
    G1RectFill r;
    int32_t x0, y0, dx, dy;
    /* every direction, a point, axis-aligned and shallow/steep lines, inside and across the clip */
    for (x0 = -6; x0 <= 46; x0 += 4)
        for (y0 = -6; y0 <= 36; y0 += 5)
            for (dx = -14; dx <= 14; ++dx)
                for (dy = -14; dy <= 14; ++dy)
                    outside += plot_outside_region(x0, y0, x0 + dx, y0 + dy, clip, &plots,
                                                   &overshoot);
    assert(plots > 100000);
    assert(outside == 0);
    assert(overshoot <= 1);
    /* bbox grown by 1 px on every side, then clipped */
    assert(g1_line_region(10, 12, 20, 5, clip, &r));
    assert(r.x == 9 && r.y == 4 && r.width == 13u && r.height == 10u);
    assert(g1_line_region(20, 5, 10, 12, clip, &r));
    assert(r.x == 9 && r.y == 4 && r.width == 13u && r.height == 10u);
    /* one point */
    assert(g1_line_region(7, 8, 7, 8, clip, &r));
    assert(r.x == 6 && r.y == 7 && r.width == 3u && r.height == 3u);
    /* clip boundary: the grown box is cut at the clip rectangle */
    assert(g1_line_region(0, 0, 3, 3, clip, &r));
    assert(r.x == 0 && r.y == 0 && r.width == 5u && r.height == 5u);
    assert(g1_line_region(36, 26, 39, 29, clip, &r));
    assert(r.x == 35 && r.y == 25 && r.width == 5u && r.height == 5u);
    /* outside the clip: an empty grown box is rejected; a 1 px touch is kept (conservative) */
    assert(!g1_line_region(-10, 5, -2, 5, clip, &r));
    assert(g1_line_region(-10, 5, -1, 5, clip, &r) && r.x == 0 && r.width == 1u);
    assert(!g1_line_region(40, 40, 60, 60, clip, &r));
    /* int32 differences that overflow are not mirrored */
    assert(!g1_line_region(INT32_MIN, 0, INT32_MAX, 0, clip, &r));
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


def test_line_hook_table_and_wrapper_contract() -> None:
    """H-LN N-1: 0x4659B0 thiscall clipped line (ret 0x14, 5 stack args x0 y0 x1 y1 colour)
    diff mirror.  `83 EC 0C | 8B 44 24 18` is a 7-byte instruction boundary."""
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    header = (STUB / "g1_mirror2x.h").read_text(encoding="utf-8")
    bridge = (STUB / "direct_draw_trace.c").read_text(encoding="utf-8")
    assert "#define G1_LINE 0x004659B0u" in mirror
    assert "#define G1_LINE_LEN 7u" in mirror
    assert re.search(
        r"expected_line\[G1_LINE_LEN\] =\s*"
        r"\{0x83, 0xEC, 0x0C, 0x8B, 0x44, 0x24, 0x18\};", mirror)
    assert "install_one(G1_LINE, expected_line, G1_LINE_LEN" in mirror
    assert "restore_hook(&g_hook_line)" in mirror
    assert "g_hook_line.installed" in mirror
    assert "g_original_line = NULL;" in mirror
    assert "static G1PrimitiveFn g_original_line" in mirror
    start = mirror.index("mirror_line(void *renderer")
    end = mirror.index("static DWORD __attribute__((thiscall))", start)
    body = mirror[start:end]
    assert "g_original_line(renderer, x0, y0, x1, y1, color)" in body
    assert body.count("g_original_line(") == 1
    before = body.index("g_line_before")
    original = body.index("g_original_line(renderer")
    apply_at = body.index("g1_overlay_blt_apply_tiled(")
    assert before < original < apply_at
    assert "g1_overlay_blt_apply(" not in body
    assert "g1_line_region(" in body
    assert "G1_CACHE_BASE" in body and "g_panel_bound_buffer" in body
    assert "g_primitive_guard" in body
    assert ("static BYTE g_line_before"
            "[G1_OVERLAY_SCREEN_WIDTH * G1_OVERLAY_SCREEN_HEIGHT];") in mirror
    assert "static BYTE g_line_tile[G1_OVERLAY_MAX_WIDTH * G1_OVERLAY_MAX_HEIGHT];" in mirror
    install = mirror[mirror.index("g1_mirror2x_primitives_install"):]
    for counter in ("g_line_invocations", "g_line_mirrored_calls", "g_line_mirrored_pixels",
                    "g_line_reject_target", "g_line_reject_size", "g_line_reject_guard"):
        assert counter in mirror
        assert f"{counter} = 0u;" in install
    for suffix in ("invocations", "mirrored_calls", "mirrored_pixels",
                   "reject_target", "reject_size", "reject_guard"):
        assert f"line_4659B0_{suffix}" in bridge
        assert f"DWORD g1_mirror2x_line_{suffix}(void);" in header
    assert "lstrcatA(mirror_details, line_details)" in bridge


def test_flip_rle_hook_table_and_wrapper_contract() -> None:
    """H-F3: 0x466B50 thiscall flipped remap RLE (unclipped, ret 0x18) diff mirror."""
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    header = (STUB / "g1_mirror2x.h").read_text(encoding="utf-8")
    bridge = (STUB / "direct_draw_trace.c").read_text(encoding="utf-8")
    assert "#define G1_FLIP_RLE 0x00466B50u" in mirror
    assert "#define G1_FLIP_RLE_LEN 8u" in mirror
    # prologue: push ecx; push ebx; push esi; push edi; mov edi,[esp+0x18] (8 B)
    assert "expected_flip_rle[G1_FLIP_RLE_LEN] =" in mirror
    assert "{0x51, 0x53, 0x56, 0x57, 0x8B, 0x7C, 0x24, 0x18}" in mirror
    assert "install_one(G1_FLIP_RLE, expected_flip_rle, G1_FLIP_RLE_LEN" in mirror
    assert "restore_hook(&g_hook_flip_rle)" in mirror
    assert "g_hook_flip_rle.installed" in mirror
    assert "g_original_flip_rle = NULL;" in mirror
    # original returns: 0x466B50 ret 0x18 (6 stack args: x y w h rle lut)
    start = mirror.index("mirror_flip_rle(void *renderer")
    body = mirror[start:mirror.index("/* Original returns: 0x466BE0", start)]
    # H-R: all six original arguments are forwarded unchanged, exactly once
    assert "g_original_flip_rle(renderer, a_x, a_y, a_w, a_h, rle, lut)" in body
    assert body.count("g_original_flip_rle(") == 1
    before = body.index("g_flip_rle_before")
    original = body.index("g_original_flip_rle(renderer")
    apply_at = body.index("g1_overlay_blt_apply(")
    assert before < original < apply_at
    # unclipped primitive: int32 arguments, screen intersection (H-R), no viewport clip
    assert "g1_rect_fill_region(" not in body
    assert "g1_overlay_blt_accepts(" not in body
    assert "g1_flip_rle_region(" in body
    assert "(int32_t)a_x" in body and "(int32_t)a_h" in body
    assert "G1_CACHE_BASE" in body and "g_panel_bound_buffer" in body
    assert "g_primitive_guard" in body
    # rejected/clipped geometry stays visible in the drift "w" records
    assert "layer_drift_write_begin(&drift, renderer)" in body
    assert "layer_drift_write_end(&drift, G1_FLIP_RLE, why" in body
    install = mirror[mirror.index("g1_mirror2x_primitives_install"):]
    suffixes = ("invocations", "mirrored_calls", "mirrored_pixels", "reject_target",
                "reject_size", "reject_guard", "reject_bounds", "clipped_calls",
                "wrap_calls")
    for suffix in suffixes:
        counter = f"g_flip_rle_{suffix}"
        assert counter in mirror
        assert f"{counter} = 0u;" in install
    for suffix in suffixes:
        assert f"flip_rle_466B50_{suffix}" in bridge
        assert f"DWORD g1_mirror2x_flip_rle_{suffix}(void);" in header


def test_flip_rle_region_intersects_screen_like_unclipped_original(tmp_path: Path) -> None:
    """H-R: 0x466B50 has no clip; the mirror covers the screen intersection only."""
    fixture = tmp_path / "flip_rle_contract.c"
    executable = tmp_path / "flip_rle_contract"
    fixture.write_text(
        r'''#include <assert.h>
#include <stdint.h>
#include "g1_rect_fill.h"

int main(void) {
    G1FlipRleRegion r;
    const int32_t stride = 832;
    /* fully inside: unchanged, not clipped, no wrap */
    assert(g1_flip_rle_region(10, 20, 30, 40, stride, 800, 600, &r));
    assert(r.x == 10 && r.y == 20 && r.width == 30u && r.height == 40u);
    assert(!r.clipped && !r.wrap);
    /* x + w == 800 touches the right edge exactly: still inside */
    assert(g1_flip_rle_region(770, 0, 30, 10, stride, 800, 600, &r));
    assert(r.width == 30u && !r.clipped && !r.wrap);
    /* x + w == 801: cut to the screen; 832: empty but inside the stride; 833: wraps */
    assert(g1_flip_rle_region(771, 0, 30, 10, stride, 800, 600, &r));
    assert(r.x == 771 && r.width == 29u && r.clipped && !r.wrap);
    assert(!g1_flip_rle_region(802, 0, 30, 10, stride, 800, 600, &r));
    assert(!r.wrap);
    assert(!g1_flip_rle_region(803, 0, 30, 10, stride, 800, 600, &r));
    assert(r.wrap);
    assert(g1_flip_rle_region(790, 0, 43, 10, stride, 800, 600, &r));
    assert(r.x == 790 && r.width == 10u && r.clipped && r.wrap);
    /* x = -1 loses one column on the left and wraps into the previous row */
    assert(g1_flip_rle_region(-1, 5, 10, 10, stride, 800, 600, &r));
    assert(r.x == 0 && r.y == 5 && r.width == 9u && r.height == 10u);
    assert(r.clipped && r.wrap);
    /* y + h == 600 is inside; 601 is cut by one row and wraps below the screen */
    assert(g1_flip_rle_region(0, 590, 10, 10, stride, 800, 600, &r));
    assert(r.height == 10u && !r.clipped && !r.wrap);
    assert(g1_flip_rle_region(0, 590, 10, 11, stride, 800, 600, &r));
    assert(r.height == 10u && r.clipped && r.wrap);
    assert(g1_flip_rle_region(5, -3, 10, 10, stride, 800, 600, &r));
    assert(r.y == 0 && r.height == 7u && r.clipped && r.wrap);
    /* non-positive size: nothing is written, no wrap is reported */
    assert(!g1_flip_rle_region(0, 0, 0, 10, stride, 800, 600, &r) && !r.wrap);
    assert(!g1_flip_rle_region(0, 0, 10, -1, stride, 800, 600, &r) && !r.wrap);
    /* arguments are full int32 values, not 16-bit extended */
    assert(!g1_flip_rle_region((int32_t)0x00010010, 0, 32, 10, stride, 800, 600, &r));
    assert(r.wrap);
    assert(g1_flip_rle_region((int32_t)0xFFFFFFF0u, 0, 32, 10, stride, 800, 600, &r));
    assert(r.x == 0 && r.width == 16u && r.clipped && r.wrap);
    /* x + w must not overflow */
    assert(!g1_flip_rle_region(INT32_MAX, 0, INT32_MAX, 10, stride, 800, 600, &r));
    assert(r.wrap);
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


def test_rect_solid_region_matches_original_bounds_and_sort(tmp_path: Path) -> None:
    """H-N: 0x465E80 has no clip; it rejects out-of-range corners, never cuts them."""
    fixture = tmp_path / "rect_solid_contract.c"
    executable = tmp_path / "rect_solid_contract"
    fixture.write_text(
        r'''#include <assert.h>
#include <stdint.h>
#include "g1_rect_fill.h"

int main(void) {
    G1RectFill r;
    const int32_t stride = 832, ybound = 600;
    /* 4x6 floor fragment, both ends inclusive */
    assert(g1_rect_solid_region(480, 515, 483, 520, stride, ybound, 800, 600, &r));
    assert(r.x == 480 && r.y == 515 && r.width == 4u && r.height == 6u);
    /* flipped corners are sorted per axis */
    assert(g1_rect_solid_region(483, 520, 480, 515, stride, ybound, 800, 600, &r));
    assert(r.x == 480 && r.y == 515 && r.width == 4u && r.height == 6u);
    /* single pixel */
    assert(g1_rect_solid_region(5, 6, 5, 6, stride, ybound, 800, 600, &r));
    assert(r.width == 1u && r.height == 1u);
    /* any negative corner: original writes nothing (no clipping) */
    assert(!g1_rect_solid_region(-1, 0, 10, 10, stride, ybound, 800, 600, &r));
    assert(!g1_rect_solid_region(0, -1, 10, 10, stride, ybound, 800, 600, &r));
    assert(!g1_rect_solid_region(0, 0, -1, 10, stride, ybound, 800, 600, &r));
    assert(!g1_rect_solid_region(0, 0, 10, -1, stride, ybound, 800, 600, &r));
    /* x == stride / y == ybound is outside (jge), stride-1 / ybound-1 is inside */
    assert(!g1_rect_solid_region(0, 0, stride, 10, stride, ybound, 800, 600, &r));
    assert(!g1_rect_solid_region(stride, 0, 10, 10, stride, ybound, 800, 600, &r));
    assert(!g1_rect_solid_region(0, 0, 10, ybound, stride, ybound, 800, 600, &r));
    assert(!g1_rect_solid_region(0, ybound, 10, 10, stride, ybound, 800, 600, &r));
    assert(g1_rect_solid_region(0, 0, 10, ybound - 1, stride, ybound, 800, 600, &r));
    assert(r.height == 600u);
    /* x 800..831 is inside the stride but outside the screen: mirror only [0,800) */
    assert(g1_rect_solid_region(790, 0, 831, 3, stride, ybound, 800, 600, &r));
    assert(r.x == 790 && r.width == 10u && r.height == 4u);
    /* entirely in the stride padding: nothing to mirror */
    assert(!g1_rect_solid_region(800, 0, 831, 3, stride, ybound, 800, 600, &r));
    /* y beyond the screen but inside ybound is cut to the screen */
    assert(g1_rect_solid_region(0, 590, 3, 700, stride, 768, 800, 600, &r));
    assert(r.y == 590 && r.height == 10u);
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


def test_rect_solid_hook_table_and_wrapper_contract() -> None:
    """H-N: 0x465E80 thiscall solid rectangle (unclipped leaf, ret 0x14) diff mirror."""
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    header = (STUB / "g1_mirror2x.h").read_text(encoding="utf-8")
    bridge = (STUB / "direct_draw_trace.c").read_text(encoding="utf-8")
    assert "#define G1_RECT_SOLID 0x00465E80u" in mirror
    assert "#define G1_RECT_SOLID_LEN 5u" in mirror
    # prologue: mov eax,[ecx+0x10]; push ebx; push ebp (exact 5-byte instruction boundary)
    assert "expected_rect_solid[G1_RECT_SOLID_LEN] =" in mirror
    assert "{0x8B, 0x41, 0x10, 0x53, 0x55}" in mirror
    assert "install_one(G1_RECT_SOLID, expected_rect_solid, G1_RECT_SOLID_LEN" in mirror
    assert "restore_hook(&g_hook_rect_solid)" in mirror
    assert "g_hook_rect_solid.installed" in mirror
    assert "g_original_rect_solid = NULL;" in mirror
    # original returns: 0x465E80 ret 0x14 (5 stack args: x0 y0 x1 y1 color)
    start = mirror.index("mirror_rect_solid(void *renderer")
    body = mirror[start:mirror.index("BOOL g1_mirror2x_primitives_install(void)", start)]
    assert "g_original_rect_solid(renderer, x0, y0, x1, y1, color)" in body
    before = body.index("g_rect_solid_before")
    original = body.index("g_original_rect_solid(renderer")
    apply_at = body.index("g1_overlay_blt_apply(")
    assert before < original < apply_at
    # unclipped: original bounds check (stride / [renderer+0x14]) instead of the viewport
    assert "g1_rect_solid_region(" in body
    assert "g1_rect_fill_region(" not in body and "rect_fill_clip(" not in body
    assert "G1_RENDERER_YBOUND" in body
    assert "g1_overlay_blt_accepts(" in body
    assert "G1_CACHE_BASE" in body and "g_panel_bound_buffer" in body
    assert "g_primitive_guard" in body
    assert "#define G1_RENDERER_YBOUND 0x14u" in mirror
    install = mirror[mirror.index("g1_mirror2x_primitives_install"):]
    counters = ("invocations", "mirrored_calls", "mirrored_pixels", "reject_target",
                "reject_bounds", "reject_size", "reject_guard")
    for suffix in counters:
        assert f"g_rect_solid_{suffix}" in mirror
        assert f"g_rect_solid_{suffix} = 0u;" in install
        assert f"rect_solid_465E80_{suffix}" in bridge
        assert f"DWORD g1_mirror2x_rect_solid_{suffix}(void);" in header
    assert "rect_solid_465E80_ybound" in bridge
    assert "DWORD g1_mirror2x_rect_solid_ybound(void);" in header


def test_textout_iat_hook_and_wrapper_contract() -> None:
    """H-G: GDI TextOutA IAT slot 0x4E502C call diff mirror (slot-checked, restored)."""
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    header = (STUB / "g1_mirror2x.h").read_text(encoding="utf-8")
    bridge = (STUB / "direct_draw_trace.c").read_text(encoding="utf-8")
    assert "#define G1_TEXTOUT_SLOT 0x004E502Cu" in mirror
    # install only when the slot still holds gdi32!TextOutA, otherwise count the mismatch
    start = mirror.index("static BOOL textout_install(void)")
    install = mirror[start:mirror.index("static BOOL textout_restore(void)", start)]
    assert 'GetProcAddress(gdi, "TextOutA")' in install
    assert "*slot != (DWORD)(ULONG_PTR)real" in install
    assert "g_textout_install_mismatch" in install
    assert "VirtualProtect(slot" in install
    # restore only if the slot still holds our wrapper, and count the restore
    restore = mirror[mirror.index("static BOOL textout_restore(void)"):]
    restore = restore[:restore.index("BOOL g1_mirror2x_primitives_install(void)")]
    assert "*slot == (DWORD)(ULONG_PTR)mirror_textout" in restore
    assert "g_textout_slot_restored" in restore
    # wrapper: reject non TA_LEFT|TA_TOP, measure extent, shadow margin, before->real->flush->apply
    body = mirror[mirror.index("static BOOL WINAPI mirror_textout("):]
    body = body[:body.index("static BOOL textout_install(void)")]
    assert "g_textout_align(hdc)" in body and "g_textout_reject_align" in body
    assert "g_textout_extent(hdc, text, length, &extent)" in body
    assert "g_textout_before" in body and "g_textout_flush()" in body
    before = body.index("g_textout_before")
    original = body.index("g_real_textout(hdc, x, y, text, length)")
    flush = body.index("g_textout_flush()")
    apply_at = body.index("g1_overlay_blt_apply(")
    assert before < original < flush < apply_at
    assert "g1_overlay_blt_accepts(" in body
    assert "G1_CACHE_BASE" in body and "g_panel_bound_buffer" in body
    assert "g_primitive_guard" in body
    assert "G1_RENDERER_VA" in body
    install_all = mirror[mirror.index("BOOL g1_mirror2x_primitives_install(void)"):]
    for counter in ("g_textout_invocations", "g_textout_mirrored_calls",
                    "g_textout_mirrored_pixels", "g_textout_changed_calls",
                    "g_textout_reject_target", "g_textout_reject_size",
                    "g_textout_reject_guard", "g_textout_reject_align",
                    "g_textout_install_mismatch", "g_textout_slot_restored"):
        assert counter in mirror
        assert f"{counter} = 0u;" in install_all
    assert "textout_restore()" in install_all[install_all.index("primitives_detach"):]
    for suffix in ("invocations", "mirrored_calls", "mirrored_pixels", "changed_calls",
                   "reject_target", "reject_size", "reject_guard", "reject_align",
                   "install_mismatch", "slot_installed", "slot_restored"):
        assert f"textout_iat_{suffix}" in bridge
        assert f"DWORD g1_mirror2x_textout_{suffix}(void);" in header


def test_blend_rle_hook_table_and_wrapper_contract() -> None:
    """H-L: 0x4672E0 thiscall translucent logo RLE (unclipped, ret 0x14) diff mirror."""
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    header = (STUB / "g1_mirror2x.h").read_text(encoding="utf-8")
    bridge = (STUB / "direct_draw_trace.c").read_text(encoding="utf-8")
    assert "#define G1_BLEND_RLE 0x004672E0u" in mirror
    assert "#define G1_BLEND_RLE_LEN 6u" in mirror
    # prologue: push ecx; push ebx; push esi; mov esi,ecx; push edi (6 B)
    assert "{0x51, 0x53, 0x56, 0x8B, 0xF1, 0x57}" in mirror
    assert "install_one(G1_BLEND_RLE, expected_blend_rle, G1_BLEND_RLE_LEN" in mirror
    assert "restore_hook(&g_hook_blend_rle)" in mirror
    assert "g_hook_blend_rle.installed" in mirror
    assert "g_original_blend_rle = NULL;" in mirror
    # original returns: 0x4672E0 ret 0x14 (5 stack args: x y w h rle, low 16 bits each)
    start = mirror.index("mirror_blend_rle(void *renderer")
    body = mirror[start:mirror.index("BOOL g1_mirror2x_primitives_install(void)", start)]
    assert "g_original_blend_rle(renderer, a_x, a_y, a_w, a_h, rle)" in body
    # callers leave garbage in the upper words: arguments are sign-extended 16-bit
    assert body.count("(int16_t)") >= 4
    before = body.index("g_blend_rle_before")
    original = body.index("g_original_blend_rle(renderer")
    apply_at = body.index("g1_overlay_blt_apply(")
    assert before < original < apply_at
    # unclipped primitive: out-of-range rectangles are rejected, never cut
    assert "g_blend_rle_reject_bounds" in body
    assert "g1_rect_fill_region(" not in body
    assert "G1_CACHE_BASE" in body and "g_panel_bound_buffer" in body
    assert "g_primitive_guard" in body
    install = mirror[mirror.index("g1_mirror2x_primitives_install"):]
    counters = ("invocations", "mirrored_calls", "mirrored_pixels", "changed_calls",
                "reject_target", "reject_bounds", "reject_size", "reject_guard")
    for suffix in counters:
        assert f"g_blend_rle_{suffix} = 0u;" in install
        assert f"blend_4672E0_{suffix}" in bridge
        assert f"DWORD g1_mirror2x_blend_rle_{suffix}(void);" in header


def test_blend_weighted_rle_hook_table_and_wrapper_contract() -> None:
    """H-B: 0x467580 thiscall weighted translucent RLE (unclipped, ret 0x14) diff mirror."""
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    header = (STUB / "g1_mirror2x.h").read_text(encoding="utf-8")
    bridge = (STUB / "direct_draw_trace.c").read_text(encoding="utf-8")
    assert "#define G1_BLEND_WRLE 0x00467580u" in mirror
    assert "#define G1_BLEND_WRLE_LEN 6u" in mirror
    # prologue: push ecx; movsx edx,word [esp+0xC] (6 B, no relative operands)
    assert "{0x51, 0x0F, 0xBF, 0x54, 0x24, 0x0C}" in mirror
    assert "install_one(G1_BLEND_WRLE, expected_blend_wrle, G1_BLEND_WRLE_LEN" in mirror
    assert "restore_hook(&g_hook_blend_wrle)" in mirror
    assert "g_hook_blend_wrle.installed" in mirror
    assert "g_original_blend_wrle = NULL;" in mirror
    # original returns: 0x467580 ret 0x14 (5 stack args: x y w h rle, low 16 bits each)
    start = mirror.index("mirror_blend_wrle(void *renderer")
    body = mirror[start:mirror.index("static BOOL WINAPI mirror_textout", start)]
    assert "g_original_blend_wrle(renderer, a_x, a_y, a_w, a_h, rle)" in body
    assert body.count("(int16_t)") >= 4
    before = body.index("g_blend_wrle_before")
    original = body.index("g_original_blend_wrle(renderer")
    apply_at = body.index("g1_overlay_blt_apply_tiled(")
    assert before < original < apply_at
    # the H-L before buffer is a different hook's scratch: never shared
    assert "g_blend_rle_before" not in body
    # H-W330: width > 320 (lap1083 330x200) is tiled from a screen-sized before copy
    _assert_tiled_blend_wrapper("blend_wrle", "G1_BLEND_WRLE", mirror)
    assert "g_blend_wrle_reject_bounds" in body
    assert "g1_rect_fill_region(" not in body
    assert "G1_CACHE_BASE" in body and "g_panel_bound_buffer" in body
    assert "g_primitive_guard" in body
    # partially off-screen rectangles are mirrored over the screen intersection only
    # (the original is unclipped and is still called with its full rectangle)
    assert "g_blend_wrle_clipped_calls" in body
    assert "g_blend_wrle_reject_bounds" in body and "x0 >= x1" in body
    install = mirror[mirror.index("g1_mirror2x_primitives_install"):]
    counters = ("invocations", "mirrored_calls", "mirrored_pixels", "changed_calls",
                "clipped_calls", "reject_target", "reject_bounds", "reject_size",
                "reject_guard")
    for suffix in counters:
        assert f"g_blend_wrle_{suffix} = 0u;" in install
        assert f"blend_467580_{suffix}" in bridge
        assert f"DWORD g1_mirror2x_blend_wrle_{suffix}(void);" in header


def test_blend_clip_hook_table_and_wrapper_contract() -> None:
    """H-B4: 0x467B00 thiscall clipped dest-dependent blend RLE (ret 0x14) diff mirror."""
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    header = (STUB / "g1_mirror2x.h").read_text(encoding="utf-8")
    bridge = (STUB / "direct_draw_trace.c").read_text(encoding="utf-8")
    assert "#define G1_BLEND_CLIP 0x00467B00u" in mirror
    assert "#define G1_BLEND_CLIP_LEN 5u" in mirror
    # prologue: sub esp,0x14; xor eax,eax (5 B, same old bytes as 0x4676D0)
    assert "expected_blend_clip[G1_BLEND_CLIP_LEN]" in mirror
    assert "install_one(G1_BLEND_CLIP, expected_blend_clip, G1_BLEND_CLIP_LEN" in mirror
    assert "restore_hook(&g_hook_blend_clip)" in mirror
    assert "g_hook_blend_clip.installed" in mirror
    assert "g_original_blend_clip = NULL;" in mirror
    start = mirror.index("mirror_blend_clip(void *renderer")
    body = mirror[start:mirror.index("static DWORD __attribute__((thiscall)) observe_blend_410", start)]
    assert "g_original_blend_clip(renderer, a_x, a_y, a_w, a_h, rle)" in body
    assert body.count("(int16_t)") >= 4
    before = body.index("g_blend_clip_before")
    original = body.index("g_original_blend_clip(renderer")
    apply_at = body.index("g1_overlay_blt_apply_tiled(")
    assert before < original < apply_at
    # never share another hook's before buffer
    assert "g_blend_wrle_before" not in body and "g_blend_rle_before" not in body
    assert "g_blend_clip_reject_bounds" in body and "x0 >= x1" in body
    assert "g_blend_clip_clipped_calls" in body
    assert "g1_rect_fill_region(" not in body
    assert "G1_CACHE_BASE" in body and "g_panel_bound_buffer" in body
    assert "g_primitive_guard" in body
    assert "layer_drift_write_end(&drift, G1_BLEND_CLIP" in body
    install = mirror[mirror.index("g1_mirror2x_primitives_install"):]
    counters = ("invocations", "mirrored_calls", "mirrored_pixels", "changed_calls",
                "clipped_calls", "reject_target", "reject_bounds", "reject_size",
                "reject_guard", "band_calls")
    for suffix in counters:
        assert f"g_blend_clip_{suffix} = 0u;" in install
        assert f"blend_467B00_{suffix}" in bridge
        assert f"DWORD g1_mirror2x_blend_clip_{suffix}(void);" in header
    _assert_tiled_blend_wrapper("blend_clip", "G1_BLEND_CLIP", mirror)
    # band_calls keeps its name but now counts tiled calls with more than one tile (H-W330)
    assert "if (tiles > 1u) ++g_blend_clip_band_calls;" in body


def _assert_tiled_blend_wrapper(name: str, define: str, mirror: str) -> None:
    """H-W330 W-0: the wrapper copies the screen intersection into a screen-sized before buffer
    and applies it through g1_overlay_blt_apply_tiled with its own 320x160 tile buffer, so the
    old width/height size pre-check is gone and reject_size only means a failed apply."""
    assert (f"static BYTE g_{name}_before[G1_OVERLAY_SCREEN_WIDTH * G1_OVERLAY_SCREEN_HEIGHT];"
            in mirror)
    assert f"static BYTE g_{name}_tile[G1_OVERLAY_MAX_WIDTH * G1_OVERLAY_MAX_HEIGHT];" in mirror
    start = mirror.index(f"mirror_{name}(void *renderer")
    end = mirror.index("static DWORD __attribute__((thiscall))", start)
    body = mirror[start:end]
    assert body.count("g1_overlay_blt_apply_tiled(") == 1
    assert "g1_overlay_blt_apply(" not in body and "g1_overlay_blt_apply_banded(" not in body
    assert f"g_{name}_tile," in body
    assert "G1_OVERLAY_MAX_WIDTH" not in body and "G1_OVERLAY_MAX_HEIGHT" not in body
    assert body.count(f"g_original_{name}(") == 1
    assert f"g_{name}_before" in body and f"g_{name}_reject_size" in body
    assert body.count(f"++g_{name}_reject_size;") == 1  # failed apply only
    assert f"layer_drift_write_end(&drift, {define}, why" in body


def _assert_banded_blend_wrapper(name: str, define: str, mirror: str) -> None:
    """H-D2r R-1/R-2: the wrapper mirrors rects up to the screen height in row bands from its
    own 320x600 before buffer, uses the shared apply only through the banded helper, and
    reject_size now means width > 320 or a failed apply (never height)."""
    assert (f"static BYTE g_{name}_before[G1_OVERLAY_MAX_WIDTH * G1_OVERLAY_SCREEN_HEIGHT];"
            in mirror)
    start = mirror.index(f"mirror_{name}(void *renderer")
    end = mirror.index("static DWORD __attribute__((thiscall))", start)
    body = mirror[start:end]
    assert "g1_overlay_blt_apply_banded(" in body
    assert "g1_overlay_blt_apply(" not in body
    assert f"if (bands > 1u) ++g_{name}_band_calls;" in body
    assert "G1_OVERLAY_MAX_HEIGHT" not in body
    assert "(DWORD)(x1 - x0) > G1_OVERLAY_MAX_WIDTH)" in body
    assert f"g_{name}_before" in body and f"g_{name}_reject_size" in body
    assert f"layer_drift_write_end(&drift, {define}, why" in body


def test_blend_skip_hook_table_and_wrapper_contract() -> None:
    """H-D2r R-2: 0x4685C0 thiscall clipped dest-dependent blend RLE with 0xFE skips
    (ret 0x14, old bytes 83 EC 18 53 55) diff mirror, sibling of 0x467B00."""
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    header = (STUB / "g1_mirror2x.h").read_text(encoding="utf-8")
    bridge = (STUB / "direct_draw_trace.c").read_text(encoding="utf-8")
    assert "#define G1_BLEND_SKIP 0x004685C0u" in mirror
    assert "#define G1_BLEND_SKIP_LEN 5u" in mirror
    assert re.search(
        r"expected_blend_skip\[G1_BLEND_SKIP_LEN\] =\s*\{0x83, 0xEC, 0x18, 0x53, 0x55\};", mirror)
    assert "install_one(G1_BLEND_SKIP, expected_blend_skip, G1_BLEND_SKIP_LEN" in mirror
    assert "restore_hook(&g_hook_blend_skip)" in mirror
    assert "g_hook_blend_skip.installed" in mirror
    assert "g_original_blend_skip = NULL;" in mirror
    assert "static G1PrimitiveFn g_original_blend_skip" in mirror
    start = mirror.index("mirror_blend_skip(void *renderer")
    end = mirror.index("\n}\n", start)
    body = mirror[start:end]
    assert "g_original_blend_skip(renderer, a_x, a_y, a_w, a_h, rle)" in body
    assert body.count("g_original_blend_skip(") == 1
    assert body.count("(int16_t)") >= 4
    before = body.index("g_blend_skip_before")
    original = body.index("g_original_blend_skip(renderer")
    apply_at = body.index("g1_overlay_blt_apply_banded(")
    assert before < original < apply_at
    for other in ("g_blend_clip_before", "g_blend_wrle_before", "g_blend_rle_before",
                  "g_blend_clip7_before", "g_shade_flip_before"):
        assert other not in body
    assert "g_blend_skip_reject_bounds" in body and "x0 >= x1" in body
    assert "g_blend_skip_clipped_calls" in body
    assert "g1_rect_fill_region(" not in body
    assert "G1_CACHE_BASE" in body and "g_panel_bound_buffer" in body
    assert "g_primitive_guard" in body
    _assert_banded_blend_wrapper("blend_skip", "G1_BLEND_SKIP", mirror)
    # H-W330: 0x467B00 moved to the tiled path; 0x4685C0 intentionally stays banded
    assert "g1_overlay_blt_apply_tiled(" not in body
    install = mirror[mirror.index("g1_mirror2x_primitives_install"):]
    counters = ("invocations", "mirrored_calls", "mirrored_pixels", "changed_calls",
                "clipped_calls", "reject_target", "reject_bounds", "reject_size",
                "reject_guard", "band_calls")
    for suffix in counters:
        assert f"g_blend_skip_{suffix} = 0u;" in install
        assert f"blend_4685C0_{suffix}" in bridge
        assert f"DWORD g1_mirror2x_blend_skip_{suffix}(void);" in header
    assert "lstrcatA(mirror_details, blend_skip_details)" in bridge


def test_blend_clip7_hook_table_and_wrapper_contract() -> None:
    """H-P: 0x4678C0 thiscall clipped dest-dependent blend RLE (ret 0x1c, 7 args) diff mirror."""
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    header = (STUB / "g1_mirror2x.h").read_text(encoding="utf-8")
    bridge = (STUB / "direct_draw_trace.c").read_text(encoding="utf-8")
    assert "#define G1_BLEND_CLIP7 0x004678C0u" in mirror
    assert "#define G1_BLEND_CLIP7_LEN 5u" in mirror
    # prologue: sub esp,0x18; xor eax,eax (5 B)
    assert "expected_blend_clip7[G1_BLEND_CLIP7_LEN]" in mirror
    assert "{0x83, 0xEC, 0x18, 0x33, 0xC0}" in mirror
    assert "install_one(G1_BLEND_CLIP7, expected_blend_clip7, G1_BLEND_CLIP7_LEN" in mirror
    assert "restore_hook(&g_hook_blend_clip7)" in mirror
    assert "g_hook_blend_clip7.installed" in mirror
    assert "g_original_blend_clip7 = NULL;" in mirror
    assert "static G1Primitive7Fn g_original_blend_clip7" in mirror
    start = mirror.index("mirror_blend_clip7(void *renderer")
    body = mirror[start:mirror.index("static DWORD __attribute__((thiscall)) observe_blend_410", start)]
    # all 7 original args are forwarded unchanged, exactly once
    assert "g_original_blend_clip7(renderer, a_x, a_y, a_w, a_h, rle, remap, level)" in body
    assert body.count("g_original_blend_clip7(") == 1
    assert body.count("(int16_t)") >= 4
    before = body.index("g_blend_clip7_before")
    original = body.index("g_original_blend_clip7(renderer")
    apply_at = body.index("g1_overlay_blt_apply(")
    assert before < original < apply_at
    # never share another hook's before buffer
    for other in ("g_blend_clip_before", "g_blend_wrle_before", "g_blend_rle_before"):
        assert other not in body
    assert "g_blend_clip7_reject_bounds" in body and "x0 >= x1" in body
    assert "g_blend_clip7_clipped_calls" in body
    assert "G1_CACHE_BASE" in body and "g_panel_bound_buffer" in body
    assert "g_primitive_guard" in body
    assert "layer_drift_write_end(&drift, G1_BLEND_CLIP7" in body
    install = mirror[mirror.index("g1_mirror2x_primitives_install"):]
    counters = ("invocations", "mirrored_calls", "mirrored_pixels", "changed_calls",
                "clipped_calls", "reject_target", "reject_bounds", "reject_size",
                "reject_guard")
    for suffix in counters:
        assert f"g_blend_clip7_{suffix} = 0u;" in install
        assert f"blend_4678C0_{suffix}" in bridge
        assert f"DWORD g1_mirror2x_blend_clip7_{suffix}(void);" in header
    assert bridge.count("char mirror_details[7200];") == 1  # first builder; second is 9728 (H-L2, was 9216 H-D2r)
    assert "char mirror_details[5400];" not in bridge


def test_blend_clip_flip7_hook_table_and_wrapper_contract() -> None:
    """H-U: 0x468360 thiscall clipped left-right flipped blend RLE (ret 0x1c, 7 args) diff mirror."""
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    header = (STUB / "g1_mirror2x.h").read_text(encoding="utf-8")
    bridge = (STUB / "direct_draw_trace.c").read_text(encoding="utf-8")
    assert "#define G1_BLEND_FLIP7 0x00468360u" in mirror
    assert "#define G1_BLEND_FLIP7_LEN 5u" in mirror
    # prologue: sub esp,0x1c; push ebx; push ebp (5 B)
    assert "expected_blend_flip7[G1_BLEND_FLIP7_LEN]" in mirror
    assert "{0x83, 0xEC, 0x1C, 0x53, 0x55}" in mirror
    assert "install_one(G1_BLEND_FLIP7, expected_blend_flip7, G1_BLEND_FLIP7_LEN" in mirror
    assert "restore_hook(&g_hook_blend_flip7)" in mirror
    assert "g_hook_blend_flip7.installed" in mirror
    assert "g_original_blend_flip7 = NULL;" in mirror
    assert "static G1Primitive7Fn g_original_blend_flip7" in mirror
    start = mirror.index("mirror_blend_flip7(void *renderer")
    body = mirror[start:mirror.index("static DWORD __attribute__((thiscall))", start + 10)]
    # all 7 original args are forwarded unchanged, exactly once
    assert "g_original_blend_flip7(renderer, a_x, a_y, a_w, a_h, rle, remap, level)" in body
    assert body.count("g_original_blend_flip7(") == 1
    assert body.count("(int16_t)") >= 4
    before = body.index("g_blend_flip7_before")
    original = body.index("g_original_blend_flip7(renderer")
    apply_at = body.index("g1_overlay_blt_apply(")
    assert before < original < apply_at
    # never share another hook's before buffer
    for other in ("g_blend_clip_before", "g_blend_clip7_before", "g_flip_blend_before",
                  "g_blend_wrle_before", "g_blend_rle_before"):
        assert other not in body
    assert "g_blend_flip7_reject_bounds" in body and "x0 >= x1" in body
    assert "g_blend_flip7_clipped_calls" in body
    assert "G1_CACHE_BASE" in body and "g_panel_bound_buffer" in body
    assert "g_primitive_guard" in body
    assert "layer_drift_write_end(&drift, G1_BLEND_FLIP7" in body
    install = mirror[mirror.index("g1_mirror2x_primitives_install"):]
    counters = ("invocations", "mirrored_calls", "mirrored_pixels", "changed_calls",
                "clipped_calls", "reject_target", "reject_bounds", "reject_size",
                "reject_guard")
    for suffix in counters:
        assert f"g_blend_flip7_{suffix} = 0u;" in install
        assert f"blend_468360_{suffix}" in bridge
        assert f"DWORD g1_mirror2x_blend_flip7_{suffix}(void);" in header
    assert bridge.count("char mirror_details[7200];") == 1  # first builder; second is 9728 (H-L2, was 9216 H-D2r)
    assert "char mirror_details[6600];" not in bridge


def test_flip_clip_hook_table_and_wrapper_contract() -> None:
    """H-V: 0x466BE0 thiscall clipped left-right flipped remap RLE (ret 0x18, 6 args) diff mirror."""
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    header = (STUB / "g1_mirror2x.h").read_text(encoding="utf-8")
    bridge = (STUB / "direct_draw_trace.c").read_text(encoding="utf-8")
    assert "#define G1_FLIP_CLIP 0x00466BE0u" in mirror
    assert "#define G1_FLIP_CLIP_LEN 5u" in mirror
    # prologue: sub esp,0x18; xor eax,eax (5 B)
    assert "expected_flip_clip[G1_FLIP_CLIP_LEN]" in mirror
    assert "install_one(G1_FLIP_CLIP, expected_flip_clip, G1_FLIP_CLIP_LEN" in mirror
    assert "restore_hook(&g_hook_flip_clip)" in mirror
    assert "g_hook_flip_clip.installed" in mirror
    assert "g_original_flip_clip = NULL;" in mirror
    assert "static G1Primitive6Fn g_original_flip_clip" in mirror
    start = mirror.index("mirror_flip_clip(void *renderer")
    body = mirror[start:mirror.index("static DWORD __attribute__((thiscall))", start + 10)]
    # all 6 original args are forwarded unchanged, exactly once
    assert "g_original_flip_clip(renderer, a_x, a_y, a_w, a_h, rle, lut)" in body
    assert body.count("g_original_flip_clip(") == 1
    before = body.index("g_flip_clip_before")
    original = body.index("g_original_flip_clip(renderer")
    apply_at = body.index("g1_overlay_blt_apply(")
    assert before < original < apply_at
    # 32-bit arguments, screen intersection like H-R
    assert "(int32_t)a_x" in body and "(int32_t)a_h" in body
    assert "g1_flip_rle_region(" in body
    assert "(int16_t)" not in body
    # never share another hook's before buffer
    for other in ("g_flip_rle_before", "g_blend_clip7_before", "g_blend_flip7_before",
                  "g_flip_blend_before", "g_blend_clip_before"):
        assert other not in body
    assert "G1_CACHE_BASE" in body and "g_panel_bound_buffer" in body
    assert "g_primitive_guard" in body
    assert "layer_drift_write_begin(&drift, renderer)" in body
    assert "layer_drift_write_end(&drift, G1_FLIP_CLIP, why" in body
    install = mirror[mirror.index("g1_mirror2x_primitives_install"):]
    counters = ("invocations", "mirrored_calls", "mirrored_pixels", "changed_calls",
                "clipped_calls", "wrap_calls", "reject_target", "reject_bounds",
                "reject_size", "reject_guard")
    for suffix in counters:
        assert f"g_flip_clip_{suffix} = 0u;" in install
        assert f"flip_clip_466BE0_{suffix}" in bridge
        assert f"DWORD g1_mirror2x_flip_clip_{suffix}(void);" in header


_FORMAT_SPEC = re.compile(r"%([-+ #0]*)(\d*)(I64|l|h)?([udxXsc])")
# `%s` allowance for buffers that print string arguments: one value for every `%s`, or one
# value per `%s` in order (mirror_details prints panel_frame_sha256 [64] then panel_asset_key [63]).
_STRING_ALLOWANCE = {"mirror_perf_details": 64, "mirror_details": (64, 63)}


def _worst_format_length(fmt: str, string_allowance) -> int:
    literal = _FORMAT_SPEC.sub("", fmt.replace("%%", "%"))
    total = len(literal.encode("utf-8").decode("unicode_escape"))
    per_string = (list(string_allowance) if isinstance(string_allowance, (tuple, list))
                  else None)
    for flags, width, size, kind in _FORMAT_SPEC.findall(fmt):
        wide = size == "I64"
        if kind == "s":
            allowance = per_string.pop(0) if per_string else (
                0 if per_string is not None else string_allowance)
        else:
            allowance = 0
        digits = {"u": 20 if wide else 10, "d": 20 if wide else 11,
                  "x": 16 if wide else 8, "X": 16 if wide else 8, "c": 1,
                  "s": allowance}[kind]
        total += max(digits, int(width) if width else 0)
    return total


def test_trace_details_buffers_hold_worst_case_wsprintf_output() -> None:
    """V-S: wsprintfA cannot bound its output, so each fixed stack buffer must fit the
    worst-case length of its format (10 digits per %u, 11 per %d, 8 per %X)."""
    bridge = (STUB / "direct_draw_trace.c").read_text(encoding="utf-8")
    call = re.compile(
        r'wsprintfA\(\s*(\w+)\s*,\s*((?:"(?:[^"\\]|\\.)*"\s*)+)', re.S)
    checked = 0
    too_small = []
    for match in call.finditer(bridge):
        name = match.group(1)
        declared = None
        for decl in re.finditer(rf"char\s+{name}\s*\[(\d+)\]", bridge[: match.start()]):
            declared = int(decl.group(1))
        if declared is None:
            continue
        fmt = "".join(re.findall(r'"((?:[^"\\]|\\.)*)"', match.group(2)))
        worst = _worst_format_length(fmt, _STRING_ALLOWANCE.get(name, 0))
        checked += 1
        if worst + 1 > declared:
            line = bridge[: match.start()].count("\n") + 1
            too_small.append(f"{name}[{declared}] line {line}: worst {worst} + NUL")
    assert checked >= 40
    assert not too_small, too_small


def test_flip_blend_hook_table_and_wrapper_contract() -> None:
    """H-Q: 0x467FD0 thiscall unclipped flip dest-dependent blend RLE (ret 0x14, 5 args) diff mirror."""
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    header = (STUB / "g1_mirror2x.h").read_text(encoding="utf-8")
    bridge = (STUB / "direct_draw_trace.c").read_text(encoding="utf-8")
    assert "#define G1_FLIP_BLEND 0x00467FD0u" in mirror
    assert "#define G1_FLIP_BLEND_LEN 5u" in mirror
    # prologue: sub esp,8; push ebx; push esi (5 B)
    assert "expected_flip_blend[G1_FLIP_BLEND_LEN]" in mirror
    assert "{0x83, 0xEC, 0x08, 0x53, 0x56}" in mirror
    assert "install_one(G1_FLIP_BLEND, expected_flip_blend, G1_FLIP_BLEND_LEN" in mirror
    assert "restore_hook(&g_hook_flip_blend)" in mirror
    assert "g_hook_flip_blend.installed" in mirror
    assert "g_original_flip_blend = NULL;" in mirror
    assert "static G1PrimitiveFn g_original_flip_blend" in mirror
    start = mirror.index("mirror_flip_blend(void *renderer")
    body = mirror[start:mirror.index("static DWORD __attribute__((thiscall))", start + 10)]
    # all 5 original args are forwarded unchanged, exactly once
    assert "g_original_flip_blend(renderer, a_x, a_y, a_w, a_h, rle)" in body
    assert body.count("g_original_flip_blend(") == 1
    assert body.count("(int16_t)") >= 4
    before = body.index("g_flip_blend_before")
    original = body.index("g_original_flip_blend(renderer")
    apply_at = body.index("g1_overlay_blt_apply(")
    assert before < original < apply_at
    # never share another hook's before buffer
    for other in ("g_blend_clip_before", "g_blend_clip7_before", "g_blend_wrle_before",
                  "g_blend_rle_before"):
        assert other not in body
    assert "g_flip_blend_reject_bounds" in body and "x0 >= x1" in body
    assert "g_flip_blend_clipped_calls" in body
    assert "G1_CACHE_BASE" in body and "g_panel_bound_buffer" in body
    assert "g_primitive_guard" in body
    # no clip in the original: calls that wrap rows / leave the screen are counted
    assert "g_flip_blend_wrap_calls" in body and "stride" in body
    assert "layer_drift_write_end(&drift, G1_FLIP_BLEND" in body
    install = mirror[mirror.index("g1_mirror2x_primitives_install"):]
    counters = ("invocations", "mirrored_calls", "mirrored_pixels", "changed_calls",
                "clipped_calls", "reject_target", "reject_bounds", "reject_size",
                "reject_guard", "wrap_calls")
    assert len(counters) == 10
    for suffix in counters:
        assert f"g_flip_blend_{suffix} = 0u;" in install
        assert f"blend_467FD0_{suffix}" in bridge
        assert f"DWORD g1_mirror2x_flip_blend_{suffix}(void);" in header
    assert bridge.count("char mirror_details[7200];") == 1  # first builder; second is 9728 (H-L2, was 9216 H-D2r)
    assert "char mirror_details[6000];" not in bridge


def test_rect_blt_back_buffer_diff_mirror_contract() -> None:
    """H-A: back-buffer IDirectDrawSurface7::Blt (KEYSRC stretch) diff mirror."""
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    header = (STUB / "g1_mirror2x.h").read_text(encoding="utf-8")
    bridge = (STUB / "direct_draw_trace.c").read_text(encoding="utf-8")
    assert "g1_mirror2x_overlay_rect_blt_begin(" in header
    assert "g1_mirror2x_overlay_rect_blt_end(" in header
    start = mirror.index("BOOL g1_mirror2x_overlay_rect_blt_begin(")
    end_at = mirror.index("DWORD g1_mirror2x_overlay_blt_mirrored_calls", start)
    body = mirror[start:end_at]
    # dedicated before buffer, never the BltFast one
    assert "g_rect_blt_before" in body and "g_overlay_before" not in body
    assert "static BYTE g_rect_blt_before[G1_OVERLAY_MAX_WIDTH * G1_OVERLAY_MAX_HEIGHT]" in mirror
    # NULL dst, empty intersection, oversize, lock failure, wrong target are all counted
    for counter in ("reject_size", "reject_bounds", "reject_lock", "reject_target",
                    "reject_result", "keysrc_calls", "colorfill_calls", "clipped_calls"):
        assert f"g_rect_blt_{counter}" in body
    assert "DDBLT_KEYSRC" in body and "DDBLT_COLORFILL" in body
    assert "G1_CACHE_BASE" in body and "g_panel_bound_buffer" in body
    assert "DDLOCK_READONLY" in body
    # apply only after the original ran, via the shared diff routine
    assert "g1_overlay_blt_apply(g_rect_blt_before" in body
    assert body.index("g_rect_blt_before[") < body.index("g1_overlay_blt_apply(")
    # hook_blt: begin -> original -> end, PS3 + non-primary only
    blt_start = bridge.index("static HRESULT WINAPI hook_blt(")
    blt = bridge[blt_start:bridge.index("format_rect(dst_json, dst)", blt_start)]
    assert "g1_mirror2x_enabled()" in blt and "read_state(0x004ED818u) == 3u" in blt
    assert "!record->is_primary" in blt
    begin = blt.index("g1_mirror2x_overlay_rect_blt_begin(")
    original = blt.index("record->original_blt(self, dst, source, src, flags, fx)")
    end = blt.index("g1_mirror2x_overlay_rect_blt_end(")
    assert begin < original < end
    # H-A2: wined3d re-syncs the Blt'd region each present; re-diff it before the pixel loop
    heal = mirror[mirror.index("static void rect_blt_heal_at_present("):]
    heal = heal[:heal.index("\n}\n")]
    assert "g_rect_blt_before" in heal and "g1_overlay_blt_apply(g_rect_blt_before" in heal
    assert heal.index("g_expected_snapshot[") < heal.index("g1_overlay_blt_apply(")
    assert "g_rect_blt_heal_quiet >= 3u" in heal and "G1_PROGRAM_STATE_VA" in heal
    present = mirror[mirror.index("rect_blt_heal_at_present((const BYTE *)source_desc.lpSurface"):]
    assert present.index("rect_blt_heal_at_present(") < present.index("layer_drift_present(")
    assert present.index("rect_blt_heal_at_present(") < present.index("BOOL hd_asset =")
    # H-Z: while the first heal is active, a second heal re-diffs the stale bbox outside it
    assert "rect_blt_heal2_at_present(screen, pitch" in heal
    heal2 = mirror[mirror.index("static void rect_blt_heal2_at_present("):]
    heal2 = heal2[:heal2.index("\n}\n")]
    assert "g_covered[p]" in heal2 and "g_expected_snapshot[p]" in heal2
    assert "g_rect_blt_heal_x" in heal2 and "continue;" in heal2   # skips the first heal rect
    assert "bw <= G1_OVERLAY_MAX_WIDTH && bh <= G1_OVERLAY_MAX_HEIGHT" in heal2
    assert "g1_overlay_blt_apply(g_rect_blt_before" in heal2
    assert "++g_rect_blt_heal2_skipped" in heal2 and "layer_drift_on()" in heal2
    assert "\\\"t\\\":\\\"z\\\"" in heal2
    assert "rect_solid_reject_log(\"size\"" in mirror and "rect_solid_reject_log(\"target\"" in mirror
    install = mirror[mirror.index("g1_mirror2x_primitives_install"):]
    for suffix in ("heal_presents", "heal_pixels", "heal2_presents", "heal2_pixels", "heal2_skipped"):
        assert f"g_rect_blt_{suffix} = 0u;" in install
        assert f"overlay_rect_blt_{suffix}" in bridge
        assert f"DWORD g1_mirror2x_overlay_rect_blt_{suffix}(void);" in header
    counters = ("invocations", "mirrored_calls", "mirrored_pixels", "changed_calls",
                "clipped_calls", "keysrc_calls", "colorfill_calls", "reject_bounds",
                "reject_size", "reject_lock", "reject_target", "reject_result")
    for suffix in counters:
        assert f"g_rect_blt_{suffix} = 0u;" in install
        assert f"overlay_rect_blt_{suffix}" in bridge
        assert f"DWORD g1_mirror2x_overlay_rect_blt_{suffix}(void);" in header


def test_layer_drift_sibling_observe_hooks_and_write_attribution_contract() -> None:
    """H-B2: env-gated pass-through hooks 0x467410/0x4676D0 + per-call sample attribution."""
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    header = (STUB / "g1_mirror2x.h").read_text(encoding="utf-8")
    bridge = (STUB / "direct_draw_trace.c").read_text(encoding="utf-8")
    assert "#define G1_BLEND_410 0x00467410u" in mirror
    assert "#define G1_BLEND_6D0 0x004676D0u" in mirror
    # prologues: sub esp,8; push ebx; push esi / sub esp,0x14; xor eax,eax (5 B each)
    assert "{0x83, 0xEC, 0x08, 0x53, 0x56}" in mirror
    assert "{0x83, 0xEC, 0x14, 0x33, 0xC0}" in mirror
    # 0x467410 ret 0x1C = 7 stack args, 0x4676D0 ret 0x14 = 5 stack args
    assert "observe_blend_410(void *renderer, DWORD a_x," in mirror
    assert "DWORD remap, DWORD weight)" in mirror
    start = mirror.index("observe_blend_410(void *renderer")
    body = mirror[start:mirror.index("static BOOL WINAPI mirror_textout", start)]
    assert "g_original_blend_410(renderer, a_x, a_y, a_w, a_h, rle, remap, weight)" in body
    assert "g_original_blend_6d0(renderer, a_x, a_y, a_w, a_h, rle)" in body
    # observation only: no mirror/apply, no guard mutation
    assert "g1_overlay_blt_apply(" not in body
    assert "g_primitive_guard =" not in body and "++g_primitive_guard" not in body
    # installed only when the diagnostic is on; rolled back with the rest
    install = mirror[mirror.index("g1_mirror2x_primitives_install"):]
    assert "layer_drift_on() && !install_one(G1_BLEND_410" in install
    assert "layer_drift_on() && !install_one(G1_BLEND_6D0" in install
    assert "restore_hook(&g_hook_blend_410)" in mirror
    assert "restore_hook(&g_hook_blend_6d0)" in mirror
    assert "g_original_blend_410 = NULL;" in mirror
    assert "g_original_blend_6d0 = NULL;" in mirror
    # per-call write attribution: before/after screen samples around the original call
    wstart = mirror.index("mirror_blend_wrle(void *renderer")
    wbody = mirror[wstart:mirror.index("observe_blend_410(void *renderer", wstart)]
    begin = wbody.index("layer_drift_write_begin(")
    original = wbody.index("g_original_blend_wrle(renderer")
    end = wbody.index("layer_drift_write_end(")
    assert begin < original < end
    for why in ("guard", "reject_target", "reject_bounds", "reject_size", "clipped",
                "mirrored"):
        assert f'"{why}"' in wbody
    note = mirror[mirror.index("static void layer_drift_write_end("):]
    note = note[: note.index("\n}\n")]
    for key in ('\\"t\\":\\"w\\"', '\\"f\\":\\"%X\\"', '\\"why\\":\\"%s\\"',
                '\\"sb\\":[', '\\"sa\\":[', '\\"p\\":%u'):
        assert key in note
    # a sample change no hook explains is counted per present (record type "u")
    present = mirror[mirror.index("static void layer_drift_present("):]
    present = present[: present.index("\n}\n")]
    assert '\\"t\\":\\"u\\"' in present and "g_drift_unattributed" in present
    for name in ("blend_410_invocations", "blend_410_changed_calls",
                 "blend_6d0_invocations", "blend_6d0_changed_calls",
                 "drift_w_records"):
        assert f"DWORD g1_mirror2x_{name}(void);" in header
    for key in ("drift_467410_installed", "drift_4676D0_installed",
                "drift_w_records", "drift_unattributed"):
        assert key in bridge


def test_shade_rle_hook_table_and_wrapper_contract() -> None:
    """H-W: 0x4687F0 thiscall unclipped destination-remap RLE (ret 0x18, 6 args) diff mirror."""
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    header = (STUB / "g1_mirror2x.h").read_text(encoding="utf-8")
    bridge = (STUB / "direct_draw_trace.c").read_text(encoding="utf-8")
    assert "#define G1_SHADE_RLE 0x004687F0u" in mirror
    assert "#define G1_SHADE_RLE_LEN 5u" in mirror
    # prologue: push ecx; mov edx,[esp+0xC] (5 B, second instruction is esp-relative)
    assert "expected_shade_rle[G1_SHADE_RLE_LEN]" in mirror
    assert "{0x51, 0x8B, 0x54, 0x24, 0x0C}" in mirror
    assert "install_one(G1_SHADE_RLE, expected_shade_rle, G1_SHADE_RLE_LEN" in mirror
    assert "restore_hook(&g_hook_shade_rle)" in mirror
    assert "g_hook_shade_rle.installed" in mirror
    assert "g_original_shade_rle = NULL;" in mirror
    assert "static G1Primitive6Fn g_original_shade_rle" in mirror
    start = mirror.index("mirror_shade_rle(void *renderer")
    body = mirror[start:mirror.index("/* Original returns: 0x4672E0", start)]
    assert "g_original_shade_rle(renderer, a_x, a_y, a_w, a_h, rle, lut)" in body
    assert body.count("g_original_shade_rle(") == 1
    before = body.index("g_shade_rle_before")
    original = body.index("g_original_shade_rle(renderer")
    apply_at = body.index("g1_overlay_blt_apply(")
    assert before < original < apply_at
    # unclipped 32-bit rectangle: screen intersection like H-R
    assert "(int32_t)a_x" in body and "(int32_t)a_h" in body
    assert "g1_flip_rle_region(" in body
    assert "(int16_t)" not in body
    for other in ("g_flip_rle_before", "g_flip_clip_before", "g_blend_clip7_before",
                  "g_blend_flip7_before", "g_flip_blend_before"):
        assert other not in body
    assert "G1_CACHE_BASE" in body and "g_panel_bound_buffer" in body
    assert "g_primitive_guard" in body
    assert "layer_drift_write_begin(&drift, renderer)" in body
    assert "layer_drift_write_end(&drift, G1_SHADE_RLE, why" in body
    install = mirror[mirror.index("g1_mirror2x_primitives_install"):]
    counters = ("invocations", "mirrored_calls", "mirrored_pixels", "changed_calls",
                "clipped_calls", "wrap_calls", "reject_target", "reject_bounds",
                "reject_size", "reject_guard")
    for suffix in counters:
        assert f"g_shade_rle_{suffix} = 0u;" in install
        assert f"shade_4687F0_{suffix}" in bridge
        assert f"DWORD g1_mirror2x_shade_rle_{suffix}(void);" in header


def test_shade_flip_hook_table_and_wrapper_contract() -> None:
    """H-X: 0x4689C0 thiscall unclipped flipped destination-remap RLE (ret 0x18, 6 args) diff mirror."""
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    header = (STUB / "g1_mirror2x.h").read_text(encoding="utf-8")
    bridge = (STUB / "direct_draw_trace.c").read_text(encoding="utf-8")
    assert "#define G1_SHADE_FLIP 0x004689C0u" in mirror
    assert "#define G1_SHADE_FLIP_LEN 5u" in mirror
    # prologue: push ecx; push ebx; push ebp; push esi; push edi (5 x 1 B)
    assert "expected_shade_flip[G1_SHADE_FLIP_LEN]" in mirror
    assert "{0x51, 0x53, 0x55, 0x56, 0x57}" in mirror
    assert "install_one(G1_SHADE_FLIP, expected_shade_flip, G1_SHADE_FLIP_LEN" in mirror
    assert "restore_hook(&g_hook_shade_flip)" in mirror
    assert "g_hook_shade_flip.installed" in mirror
    assert "g_original_shade_flip = NULL;" in mirror
    assert "static G1Primitive6Fn g_original_shade_flip" in mirror
    start = mirror.index("mirror_shade_flip(void *renderer")
    body = mirror[start:mirror.index("/* Original returns: 0x4672E0", start)]
    assert "g_original_shade_flip(renderer, a_x, a_y, a_w, a_h, rle, lut)" in body
    assert body.count("g_original_shade_flip(") == 1
    before = body.index("g_shade_flip_before")
    original = body.index("g_original_shade_flip(renderer")
    apply_at = body.index("g1_overlay_blt_apply(")
    assert before < original < apply_at
    # unclipped 32-bit rectangle: screen intersection like H-R / H-W
    assert "(int32_t)a_x" in body and "(int32_t)a_h" in body
    assert "g1_flip_rle_region(" in body
    assert "(int16_t)" not in body
    for other in ("g_shade_rle_before", "g_flip_rle_before", "g_flip_clip_before",
                  "g_blend_clip7_before", "g_blend_flip7_before", "g_flip_blend_before"):
        assert other not in body
    assert "G1_CACHE_BASE" in body and "g_panel_bound_buffer" in body
    assert "g_primitive_guard" in body
    assert "layer_drift_write_begin(&drift, renderer)" in body
    assert "layer_drift_write_end(&drift, G1_SHADE_FLIP, why" in body
    install = mirror[mirror.index("g1_mirror2x_primitives_install"):]
    counters = ("invocations", "mirrored_calls", "mirrored_pixels", "changed_calls",
                "clipped_calls", "wrap_calls", "reject_target", "reject_bounds",
                "reject_size", "reject_guard")
    for suffix in counters:
        assert f"g_shade_flip_{suffix} = 0u;" in install
        assert f"shade_4689C0_{suffix}" in bridge
        assert f"DWORD g1_mirror2x_shade_flip_{suffix}(void);" in header
    assert "lstrcatA(mirror_details, shade_flip_details)" in bridge
    assert "char mirror_details[9728];" in bridge


def test_shade_clip_hook_table_and_wrapper_contract() -> None:
    """H-S3t: 0x468870 thiscall clipped destination-remap RLE (ret 0x18, 6 args) diff mirror."""
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    header = (STUB / "g1_mirror2x.h").read_text(encoding="utf-8")
    bridge = (STUB / "direct_draw_trace.c").read_text(encoding="utf-8")
    assert "#define G1_SHADE_CLIP 0x00468870u" in mirror
    assert "#define G1_SHADE_CLIP_LEN 7u" in mirror
    # prologue: sub esp,0x14 (3 B); mov edx,[esp+0x1c] (4 B) -> 7 B instruction boundary
    assert "expected_shade_clip[G1_SHADE_CLIP_LEN]" in mirror
    assert "{0x83, 0xEC, 0x14, 0x8B, 0x54, 0x24, 0x1C}" in mirror
    assert "install_one(G1_SHADE_CLIP, expected_shade_clip, G1_SHADE_CLIP_LEN" in mirror
    assert "restore_hook(&g_hook_shade_clip)" in mirror
    assert "g_hook_shade_clip.installed" in mirror
    assert "g_original_shade_clip = NULL;" in mirror
    assert "static G1Primitive6Fn g_original_shade_clip" in mirror
    start = mirror.index("mirror_shade_clip(void *renderer")
    body = mirror[start:mirror.index("/* Original returns: 0x4672E0", start)]
    assert "g_original_shade_clip(renderer, a_x, a_y, a_w, a_h, rle, lut)" in body
    assert body.count("g_original_shade_clip(") == 1
    before = body.index("g_shade_clip_before")
    original = body.index("g_original_shade_clip(renderer")
    apply_at = body.index("g1_overlay_blt_apply(")
    assert before < original < apply_at
    # 32-bit rectangle arguments, screen intersection (superset of the renderer-clipped writes)
    assert "(int32_t)a_x" in body and "(int32_t)a_h" in body
    assert "g1_flip_rle_region(" in body
    assert "(int16_t)" not in body
    for other in ("g_shade_rle_before", "g_shade_flip_before", "g_flip_rle_before",
                  "g_flip_clip_before", "g_blend_clip7_before", "g_blend_flip7_before",
                  "g_flip_blend_before"):
        assert other not in body
    assert "G1_CACHE_BASE" in body and "g_panel_bound_buffer" in body
    assert "g_primitive_guard" in body
    assert "layer_drift_write_begin(&drift, renderer)" in body
    assert "layer_drift_write_end(&drift, G1_SHADE_CLIP, why" in body
    install = mirror[mirror.index("g1_mirror2x_primitives_install"):]
    counters = ("invocations", "mirrored_calls", "mirrored_pixels", "changed_calls",
                "clipped_calls", "wrap_calls", "reject_target", "reject_bounds",
                "reject_size", "reject_guard")
    for suffix in counters:
        assert f"g_shade_clip_{suffix} = 0u;" in install
        assert f"shade_468870_{suffix}" in bridge
        assert f"DWORD g1_mirror2x_shade_clip_{suffix}(void);" in header
    assert "lstrcatA(mirror_details, shade_clip_details)" in bridge


def test_flip_blend7_original_write_model_stays_inside_screen_region(tmp_path: Path) -> None:
    """H-L2: C model transcribed from objdump 0x467E60 (no clip, 16-bit x y w h): the write
    column of an opaque byte is x+w-1-k, the destination is read at column x+k, an RLE
    0xFE n skip moves k by n (overflow allowed) and the RLE index carries across rows."""
    fixture = tmp_path / "flip_blend7_model.c"
    executable = tmp_path / "flip_blend7_model"
    fixture.write_text(
        r'''#include <assert.h>
#include <stdint.h>
#include <stdlib.h>
#include "g1_rect_fill.h"

#define STRIDE 832
#define SW 800
#define SH 600

static uint32_t seed = 12345u;
static uint32_t rnd(void) { seed = seed * 1664525u + 1013904223u; return seed >> 8; }

/* objdump 0x467E60: edi = rle index, ebp = k, eax = w - k, write [esi + eax - 1] */
static void model(int16_t x, int16_t y, int16_t w, int16_t h, const uint8_t *rle,
                  void (*hit)(int row, int wcol, int rcol, void *ctx), void *ctx)
{
    int row, k, p = 0;
    for (row = 0; row < h; ++row) {
        k = 0;
        while (k < w) {
            uint8_t b = rle[p];
            if (b == 0xFE) {
                p += 1;
                k += rle[p];
                p += 1;
            } else {
                hit(row, x + (w - k) - 1, x + k, ctx);
                ++k;
                ++p;
            }
        }
    }
    (void)y;
}

typedef struct { int16_t x, y, w, h; int bad, writes, visible; G1FlipRleRegion reg; int ok; } Ctx;

static void on_hit(int row, int wcol, int rcol, void *vctx)
{
    Ctx *c = (Ctx *)vctx;
    int ycol = c->y + row;
    ++c->writes;
    if (wcol < c->x || wcol >= c->x + c->w || rcol < c->x || rcol >= c->x + c->w) c->bad = 1;
    if (wcol >= 0 && wcol < SW && ycol >= 0 && ycol < SH) {
        ++c->visible;
        if (!c->ok || wcol < c->reg.x || wcol >= c->reg.x + (int)c->reg.width ||
            ycol < c->reg.y || ycol >= c->reg.y + (int)c->reg.height)
            c->bad = 1;
    }
}

int main(void) {
    int trial;
    for (trial = 0; trial < 20000; ++trial) {
        uint8_t rle[4096];
        Ctx c = {0};
        int p = 0, row, k;
        c.x = (int16_t)((int)(rnd() % 1100u) - 150);
        c.y = (int16_t)((int)(rnd() % 800u) - 100);
        c.w = (int16_t)(1 + rnd() % 60u);
        c.h = (int16_t)(1 + rnd() % 40u);
        /* a stream that fills every row exactly or overflows it with a trailing skip */
        for (row = 0; row < c.h; ++row) {
            k = 0;
            while (k < c.w) {
                if (rnd() % 4u == 0u) {
                    uint8_t n = (uint8_t)(1 + rnd() % 80u);
                    rle[p++] = 0xFE;
                    rle[p++] = n;
                    k += n;
                } else {
                    rle[p++] = (uint8_t)(rnd() % 0xFDu);
                    ++k;
                }
            }
        }
        c.ok = g1_flip_rle_region(c.x, c.y, c.w, c.h, STRIDE, SW, SH, &c.reg);
        model(c.x, c.y, c.w, c.h, rle, on_hit, &c);
        assert(!c.bad);
        if (!c.ok) assert(c.visible == 0);
    }
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


def test_flip_blend7_hook_table_and_wrapper_contract() -> None:
    """H-L2: 0x467E60 thiscall unclipped flip dest-dependent blend RLE (ret 0x1c, 7 args) diff mirror."""
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    header = (STUB / "g1_mirror2x.h").read_text(encoding="utf-8")
    bridge = (STUB / "direct_draw_trace.c").read_text(encoding="utf-8")
    assert "#define G1_FLIP_BLEND7 0x00467E60u" in mirror
    assert "#define G1_FLIP_BLEND7_LEN 5u" in mirror
    # prologue: sub esp,8; push ebp; push esi (5 B)
    assert "expected_flip_blend7[G1_FLIP_BLEND7_LEN]" in mirror
    assert "{0x83, 0xEC, 0x08, 0x55, 0x56}" in mirror
    assert "install_one(G1_FLIP_BLEND7, expected_flip_blend7, G1_FLIP_BLEND7_LEN" in mirror
    assert "restore_hook(&g_hook_flip_blend7)" in mirror
    assert "g_hook_flip_blend7.installed" in mirror
    assert "g_original_flip_blend7 = NULL;" in mirror
    assert "static G1Primitive7Fn g_original_flip_blend7" in mirror
    start = mirror.index("mirror_flip_blend7(void *renderer")
    body = mirror[start:mirror.index("static DWORD __attribute__((thiscall))", start + 10)]
    # all 7 original args are forwarded unchanged, exactly once (the row loop reads what it wrote)
    assert "g_original_flip_blend7(renderer, a_x, a_y, a_w, a_h, rle, remap, level)" in body
    assert body.count("g_original_flip_blend7(") == 1
    before = body.index("g_flip_blend7_before")
    original = body.index("g_original_flip_blend7(renderer")
    apply_at = body.index("g1_overlay_blt_apply_tiled(")
    assert before < original < apply_at
    # no clip in the original: 16-bit extended arguments, screen intersection only
    assert body.count("(int16_t)") >= 4
    assert "g1_flip_rle_region(" in body
    assert "g1_overlay_blt_accepts(" not in body
    assert "g_flip_blend7_tile" in body and "g_flip_blend7_reject_bounds" in body
    for other in ("g_flip_blend_before", "g_blend_flip7_before", "g_blend_clip7_before",
                  "g_flip_rle_before", "g_shade_clip_before"):
        assert other not in body
    assert "G1_CACHE_BASE" in body and "g_panel_bound_buffer" in body
    assert "g_primitive_guard" in body
    assert "layer_drift_write_begin(&drift, renderer)" in body
    assert "layer_drift_write_end(&drift, G1_FLIP_BLEND7, why" in body
    install = mirror[mirror.index("g1_mirror2x_primitives_install"):]
    counters = ("invocations", "mirrored_calls", "mirrored_pixels", "changed_calls",
                "reject_target", "reject_bounds", "reject_size", "reject_guard")
    for suffix in counters:
        assert f"g_flip_blend7_{suffix} = 0u;" in install
        assert f"blend_467E60_{suffix}" in bridge
        assert f"DWORD g1_mirror2x_flip_blend7_{suffix}(void);" in header
    assert "lstrcatA(mirror_details, flip_blend7_details)" in bridge


def test_mirror_details_builder_holds_worst_case_concatenation() -> None:
    """H-W/W-S2: the second mirror_details builder appends every block with lstrcatA, so the
    sum of the worst-case block lengths (plus literals) must fit the declared size."""
    bridge = (STUB / "direct_draw_trace.c").read_text(encoding="utf-8")
    start = bridge.index("char mirror_details[", bridge.index("char mirror_details[") + 10)
    end = bridge.index('trace_event("mirror2x_metrics", "active", mirror_details)', start)
    section = bridge[start:end]
    declared = int(re.match(r"char mirror_details\[(\d+)\]", section).group(1))
    call = re.compile(
        r'wsprintfA\(\s*(\w+)\s*,\s*((?:"(?:[^"\\]|\\.)*"\s*)+)', re.S)
    sizes: dict[str, int] = {}
    for decl in re.finditer(r"char\s+(\w+)\s*\[(\d+)\]", section):
        sizes[decl.group(1)] = int(decl.group(2))
    total = 0
    appended = 0
    for match in call.finditer(section):
        name = match.group(1)
        fmt = "".join(re.findall(r'"((?:[^"\\]|\\.)*)"', match.group(2)))
        worst = _worst_format_length(fmt, _STRING_ALLOWANCE.get(name, 0))
        if name == "mirror_details":
            total += worst
        elif f"lstrcatA(mirror_details, {name})" in section:
            total += worst
            appended += 1
    # string literals appended directly (flags "0"/"1" and key names), C escapes resolved
    for literal in re.findall(r'lstrcatA\(mirror_details,\s*"((?:[^"\\]|\\.)*)"', section):
        total += len(literal.encode("utf-8").decode("unicode_escape"))
    total += 1 * section.count('? "1" : "0"')
    assert appended >= 15
    assert total + 1 <= declared, (total, declared)
