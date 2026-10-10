"""Host-side contracts for the H-P35 load-slot screen frame/partial copy mirror."""

from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STUB = ROOT / "tools/inmm_stub"
MIRROR = STUB / "g1_mirror2x.c"
HEADER = STUB / "g1_mirror2x.h"
DIRECT_DRAW = STUB / "direct_draw_trace.c"


def _function_body(source: str, signature: str) -> str:
    start = source.rindex(signature)
    brace = source.index("{", start)
    depth = 0
    for index in range(brace, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[brace:index + 1]
    raise AssertionError(signature)


def test_frame_copy_header_covers_every_pixel_even_when_value_is_unchanged(
    tmp_path: Path,
) -> None:
    fixture = tmp_path / "frame_copy_contract.c"
    executable = tmp_path / "frame_copy_contract"
    fixture.write_text(
        r'''#include <assert.h>
#include <stdint.h>
#include <string.h>
#include "g1_frame_copy.h"

static uint8_t src[800u * 600u];
static uint8_t mask[800u * 600u];
static uint8_t hd[800u * 600u * 4u];
static uint8_t expected[800u * 600u];
static uint8_t covered[800u * 600u];
static uint8_t screen_hd[1600u * 1200u];

int main(void) {
    size_t i;
    memset(mask, 1, sizeof(mask));
    assert(g1_frame_copy_accepts(0u, 0u, 800u, 600u));
    assert(g1_frame_copy_accepts(240u, 100u, 320u, 425u));
    assert(!g1_frame_copy_accepts(0u, 0u, 0u, 600u));
    assert(!g1_frame_copy_accepts(0u, 0u, 800u, 0u));
    assert(!g1_frame_copy_accepts(1u, 0u, 800u, 600u));
    assert(!g1_frame_copy_accepts(0u, 1u, 800u, 600u));
    assert(!g1_frame_copy_accepts(700u, 0u, 101u, 10u));
    assert(!g1_frame_copy_accepts(0u, 590u, 10u, 11u));
    assert(g1_frame_copy_accepts(799u, 599u, 1u, 1u));

    /* a black full frame over an already-black screen: expected 0 is already
     * there, yet every pixel must become covered (the overlay diff would skip it) */
    memset(src, 0, sizeof(src));
    memset(expected, 0, sizeof(expected));
    memset(covered, 0, sizeof(covered));
    memset(screen_hd, 0xA5, sizeof(screen_hd));
    assert(g1_frame_copy_apply(src, 0u, 0u, 800u, 600u, 1, mask, hd, expected,
                               covered, screen_hd, 1600u));
    for (i = 0u; i < 800u * 600u; ++i) assert(covered[i] == 1u && expected[i] == 0u);
    for (i = 0u; i < 1600u * 1200u; ++i) assert(screen_hd[i] == 0u);

    /* partial rectangle: only it is covered; flat colour keeps all four subpixels */
    memset(covered, 0, sizeof(covered));
    memset(expected, 0, sizeof(expected));
    memset(screen_hd, 0x11, sizeof(screen_hd));
    memset(src, 7, 4u * 3u);
    assert(g1_frame_copy_apply(src, 10u, 20u, 4u, 3u, 1, mask, hd, expected,
                               covered, screen_hd, 1600u));
    assert(covered[20u * 800u + 10u] == 1u && covered[22u * 800u + 13u] == 1u);
    assert(covered[19u * 800u + 10u] == 0u && covered[20u * 800u + 9u] == 0u);
    assert(covered[20u * 800u + 14u] == 0u && covered[23u * 800u + 10u] == 0u);
    assert(expected[21u * 800u + 11u] == 7u);
    assert(screen_hd[40u * 1600u + 20u] == 7u && screen_hd[41u * 1600u + 21u] == 7u);
    assert(screen_hd[39u * 1600u + 20u] == 0x11u && screen_hd[40u * 1600u + 19u] == 0x11u);

    /* nearest keeps the source pixel in all four subpixels */
    memset(covered, 0, sizeof(covered));
    src[0] = 9u; src[1] = 3u;
    assert(g1_frame_copy_apply(src, 0u, 0u, 2u, 1u, 0, 0, 0, expected, covered,
                               screen_hd, 1600u));
    assert(screen_hd[0] == 9u && screen_hd[1] == 9u && screen_hd[1600u] == 9u &&
           screen_hd[1601u] == 9u && screen_hd[2] == 3u && screen_hd[1603u] == 3u);

    /* rejects: out-of-bounds, missing scratch, short destination stride */
    assert(!g1_frame_copy_apply(src, 700u, 0u, 101u, 10u, 0, 0, 0, expected, covered,
                                screen_hd, 1600u));
    assert(!g1_frame_copy_apply(src, 0u, 0u, 4u, 3u, 1, 0, hd, expected, covered,
                                screen_hd, 1600u));
    assert(!g1_frame_copy_apply(src, 0u, 0u, 4u, 3u, 0, 0, 0, expected, covered,
                                screen_hd, 1599u));
    return 0;
}
''',
        encoding="utf-8",
    )
    build = subprocess.run(
        ["gcc", "-std=c99", "-Wall", "-Wextra", "-Werror", f"-I{STUB}", str(fixture),
         "-o", str(executable)],
        capture_output=True, text=True, check=False,
    )
    assert build.returncode == 0, build.stderr
    run = subprocess.run([str(executable)], capture_output=True, text=True, check=False)
    assert run.returncode == 0, run.stderr


def test_block_copy_mirror_accepts_partial_rectangles_through_the_frame_copy_helper() -> None:
    source = MIRROR.read_text(encoding="utf-8")
    assert '#include "g1_frame_copy.h"' in source
    body = _function_body(source, "static void transfer_block_copy_to_screen(")
    assert "g1_frame_copy_accepts(x, y, width, height)" in body
    assert "x != 0u || y != 0u || width != 800u || height != 600u" not in body
    assert "G1_CACHE_BASE" in body and "g_panel_bound_buffer" in body
    assert "readable_bytes(src, width * height)" in body
    assert "g1_frame_copy_apply(" in body
    # Partial rectangles must not disturb the PS9 full-frame hash diagnostics.
    full = body.index("width == 800u && height == 600u")
    assert full < body.index("g_menu_copy_calls")
    assert "g_partial_copy_calls" in body and "g_partial_copy_pixels" in body


def test_offscreen_frame_blt_is_mirrored_after_the_original_call_for_the_load_screen() -> None:
    source = MIRROR.read_text(encoding="utf-8")
    header = HEADER.read_text(encoding="utf-8")
    trace = DIRECT_DRAW.read_text(encoding="utf-8")
    assert "BOOL g1_mirror2x_frame_blt_copy(" in header
    body = _function_body(source, "BOOL g1_mirror2x_frame_blt_copy(")
    assert "g1_frame_copy_accepts(0u, 0u, 800u, 600u)" in body
    assert "DDLOCK_READONLY" in body
    assert "g1_frame_copy_apply(" in body
    assert "g_frame_copy_calls" in body and "g_frame_copy_rejects" in body
    caller = _function_body(trace, "static HRESULT WINAPI hook_blt_fast(")
    after_original = caller.index("record->original_blt_fast(self, x, y, source, src, flags)")
    mirror_call = caller.index("g1_mirror2x_frame_blt_copy(")
    assert mirror_call > after_original
    gate = caller[mirror_call - 400:mirror_call]
    assert "0x00493CCBu" in gate and "!src" in gate and "read_state(0x004ED818u) == 35u" in gate
    assert "!destination_is_primary" in gate


def test_frame_copy_counters_are_reported_on_every_present_row() -> None:
    header = HEADER.read_text(encoding="utf-8")
    trace = DIRECT_DRAW.read_text(encoding="utf-8")
    for name in ("partial_copy_calls", "partial_copy_pixels", "frame_copy_calls",
                 "frame_copy_pixels", "frame_copy_rejects"):
        assert f"g1_mirror2x_{name}(void)" in header
        assert f'\\"{name}\\"' in trace
