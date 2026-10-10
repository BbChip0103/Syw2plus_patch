"""Host-side contracts for the H-RS2 primary readback -> last logical frame repair."""

from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STUB = ROOT / "tools/inmm_stub"
MIRROR = STUB / "g1_mirror2x.c"
HEADER = STUB / "g1_mirror2x.h"
DIRECT_DRAW = STUB / "direct_draw_trace.c"
MAKEFILE = STUB / "Makefile"
PROBE = ROOT / "tools/g1_saved_scene_probe.py"


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


def test_primary_readback_helpers_apply_and_copy(tmp_path: Path) -> None:
    fixture = tmp_path / "primary_readback_contract.c"
    executable = tmp_path / "primary_readback_contract"
    fixture.write_text(
        r'''#include <assert.h>
#include <string.h>
#include "g1_primary_readback.h"

static uint8_t frame[800 * 600];
static uint8_t dst[1600 * 1200];

int main(void) {
    size_t sx, sy, w, h;
    int32_t rect[4];
    size_t i;
    /* only a non-primary destination reading a primary source is a readback */
    assert(g1_primary_readback_applies(0, 1));
    assert(!g1_primary_readback_applies(1, 1));
    assert(!g1_primary_readback_applies(0, 0));
    assert(!g1_primary_readback_applies(1, 0));

    /* NULL source rect = the whole logical 800x600 frame */
    assert(g1_primary_readback_rect(NULL, 0u, 0u, 1600u, 1200u, &sx, &sy, &w, &h));
    assert(sx == 0u && sy == 0u && w == 800u && h == 600u);
    /* explicit rect keeps logical coordinates */
    rect[0] = 10; rect[1] = 20; rect[2] = 110; rect[3] = 70;
    assert(g1_primary_readback_rect(rect, 5u, 6u, 800u, 600u, &sx, &sy, &w, &h));
    assert(sx == 10u && sy == 20u && w == 100u && h == 50u);
    /* rect outside the logical frame, empty, or inverted stays on the original path */
    rect[0] = -1; rect[1] = 0; rect[2] = 10; rect[3] = 10;
    assert(!g1_primary_readback_rect(rect, 0u, 0u, 800u, 600u, &sx, &sy, &w, &h));
    rect[0] = 0; rect[1] = 0; rect[2] = 801; rect[3] = 10;
    assert(!g1_primary_readback_rect(rect, 0u, 0u, 800u, 600u, &sx, &sy, &w, &h));
    rect[0] = 5; rect[1] = 5; rect[2] = 5; rect[3] = 10;
    assert(!g1_primary_readback_rect(rect, 0u, 0u, 800u, 600u, &sx, &sy, &w, &h));
    rect[0] = 9; rect[1] = 5; rect[2] = 5; rect[3] = 10;
    assert(!g1_primary_readback_rect(rect, 0u, 0u, 800u, 600u, &sx, &sy, &w, &h));
    /* destination smaller than the copy (BltFast would fail): original path */
    assert(!g1_primary_readback_rect(NULL, 0u, 0u, 799u, 600u, &sx, &sy, &w, &h));
    assert(!g1_primary_readback_rect(NULL, 0u, 1u, 800u, 600u, &sx, &sy, &w, &h));
    assert(!g1_primary_readback_rect(NULL, 1u, 0u, 800u, 600u, &sx, &sy, &w, &h));

    /* copy: logical rows land at (x, y) with the destination pitch, nothing else moves */
    for (i = 0; i < sizeof(frame); ++i) frame[i] = (uint8_t)(i % 251u + 1u);
    memset(dst, 0xEE, sizeof(dst));
    rect[0] = 3; rect[1] = 4; rect[2] = 13; rect[3] = 9;
    assert(g1_primary_readback_copy(frame, rect, 7u, 11u, dst, 1600u, 1600u, 1200u) == 50u);
    for (i = 0; i < 5u; ++i)
        assert(memcmp(dst + (11u + i) * 1600u + 7u, frame + (4u + i) * 800u + 3u, 10u) == 0);
    assert(dst[11u * 1600u + 6u] == 0xEE && dst[11u * 1600u + 17u] == 0xEE);
    assert(dst[10u * 1600u + 7u] == 0xEE && dst[16u * 1600u + 7u] == 0xEE);
    /* full-frame copy into a 1600x1200 surface touches only the top-left 800x600 */
    memset(dst, 0xEE, sizeof(dst));
    assert(g1_primary_readback_copy(frame, NULL, 0u, 0u, dst, 1600u, 1600u, 1200u) == 480000u);
    assert(memcmp(dst, frame, 800u) == 0);
    assert(memcmp(dst + 599u * 1600u, frame + 599u * 800u, 800u) == 0);
    assert(dst[800u] == 0xEE && dst[600u * 1600u] == 0xEE);
    /* rejected requests write nothing and return 0 */
    memset(dst, 0xEE, 64u);
    assert(g1_primary_readback_copy(frame, NULL, 0u, 0u, dst, 1600u, 700u, 600u) == 0u);
    assert(g1_primary_readback_copy(NULL, NULL, 0u, 0u, dst, 1600u, 1600u, 1200u) == 0u);
    assert(g1_primary_readback_copy(frame, NULL, 0u, 0u, NULL, 1600u, 1600u, 1200u) == 0u);
    assert(g1_primary_readback_copy(frame, NULL, 0u, 0u, dst, 799u, 1600u, 1200u) == 0u);
    assert(dst[0] == 0xEE);
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


def test_present_loop_keeps_the_last_logical_frame_for_readbacks() -> None:
    source = MIRROR.read_text(encoding="utf-8")
    makefile = MAKEFILE.read_text(encoding="utf-8")
    assert '#include "g1_primary_readback.h"' in source
    assert "g1_primary_readback.h" in makefile
    assert "SYW2_G1_PRIMARY_READBACK" in source
    # default on, only an explicit "0" turns the repair off
    env = source.index("G1_PRIMARY_READBACK_ENV, value")
    assert "!(size == 1u && value[0] == '0')" in source[env:env + 200]
    body = _function_body(source, "HRESULT g1_mirror2x_copy_present(")
    assert "g_last_frame" in body and "g_last_frame_valid" in body
    assert "g_last_frame_source_hash" in body
    # the snapshot is invalidated before the copy loop and revalidated after the hash
    assert body.index("g_last_frame_valid = FALSE") < body.index("g_last_frame_source_hash")
    install = _function_body(source, "BOOL g1_mirror2x_primitives_install(")
    assert "g_last_frame = " in install
    # buffer failure must not abort the hook install
    assert "!g_last_frame ||" not in install
    assert "g_primary_readback_enabled = FALSE" in install


def test_readback_entry_point_counts_converts_and_rejects() -> None:
    source = MIRROR.read_text(encoding="utf-8")
    header = HEADER.read_text(encoding="utf-8")
    assert "BOOL g1_mirror2x_primary_readback(" in header
    for name in ("calls", "converted", "rejects", "dest_hash", "source_hash", "return_address"):
        assert f"g1_mirror2x_primary_readback_{name}(void)" in header
    body = _function_body(source, "BOOL g1_mirror2x_primary_readback(")
    assert "g_primary_readback_calls" in body
    # counted even when the repair is off, converted only after a real copy
    assert body.index("++g_primary_readback_calls") < body.index("g_primary_readback_enabled")
    assert "g1_primary_readback_copy(" in body and "g1_primary_readback_rect(" in body
    assert "g_last_frame_valid" in body and "DDLOCK_READONLY" not in body
    assert "g_primary_readback_converted" in body and "g_primary_readback_rejects" in body
    assert "g_primary_readback_dest_hash" in body
    assert "g_primary_readback_source_hash" in body
    assert "dwRGBBitCount" in body


def test_primary_readback_call_site_is_hooked_not_the_surface_vtable() -> None:
    source = MIRROR.read_text(encoding="utf-8")
    trace = DIRECT_DRAW.read_text(encoding="utf-8")
    # the destination is a GetAttachedSurface flip-chain buffer: the DirectDraw
    # surface hooks never see it, so the repair hooks the game call site instead
    assert "g1_mirror2x_primary_readback(" not in trace
    assert "#define G1_PRIMARY_READBACK_SITE 0x004C7EE6u" in source
    assert "#define G1_RENDERER_BLIT 0x00469300u" in source
    assert "#define G1_PRIMARY_SURFACE_VA 0x00E5D434u" in source
    assert "#define G1_RENDERER_BACK_BUFFER 0x1520u" in source
    assert "{0xE8, 0x15, 0x14, 0xFA, 0xFF}" in source
    body = _function_body(source, "static DWORD __attribute__((thiscall)) mirror_primary_readback_site(")
    # only a selector-1 blit from the primary is taken over; all else is the original call
    assert "selector == 1u" in body and "G1_PRIMARY_SURFACE_VA" in body
    assert "G1_RENDERER_BACK_BUFFER" in body and "readable_bytes(" in body
    assert "g1_mirror2x_primary_readback(" in body
    assert "return blit(renderer, selector, x, y, source, rect, flags)" in body
    assert "(flags & 1u) != 0u" in body  # DDBLTFAST_SRCCOLORKEY stays on the original path
    install = _function_body(source, "BOOL g1_mirror2x_primitives_install(")
    assert "install_callsite(G1_PRIMARY_READBACK_SITE" in install
    detach = _function_body(source, "void g1_mirror2x_primitives_detach(")
    assert "restore_hook(&g_hook_primary_readback)" in detach
    assert "g_hook_primary_readback.installed" in _function_body(
        source, "BOOL g1_mirror2x_primitives_installed(")


def test_readback_counters_are_reported_on_every_present_row() -> None:
    trace = DIRECT_DRAW.read_text(encoding="utf-8")
    for name in ("calls", "converted", "rejects", "dest_hash", "source_hash", "return_address"):
        assert f"g1_mirror2x_primary_readback_{name}()" in trace
        assert f'\\"primary_readback_{name}\\"' in trace
