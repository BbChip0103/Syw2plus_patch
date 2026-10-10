"""Host-side contracts for the H-RS3 result-table bar copy (0x468BB0) mirror."""

from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STUB = ROOT / "tools/inmm_stub"
MIRROR = STUB / "g1_mirror2x.c"
HEADER = STUB / "g1_mirror2x.h"
DIRECT_DRAW = STUB / "direct_draw_trace.c"
MAKEFILE = STUB / "Makefile"


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


def test_bar_copy_helpers_rect_span_and_pack(tmp_path: Path) -> None:
    fixture = tmp_path / "bar_copy_contract.c"
    executable = tmp_path / "bar_copy_contract"
    fixture.write_text(
        r'''#include <assert.h>
#include <string.h>
#include "g1_bar_copy.h"

static uint8_t src[300 * 40];
static uint8_t out[800 * 600];

int main(void) {
    size_t w, h, offset, span, i, row;
    /* the source rectangle is inclusive: width = sx1 - sx0 + 1, height = sy1 - sy0 + 1 */
    assert(g1_bar_copy_rect(0, 0, 99, 17, 10, 20, &w, &h));
    assert(w == 100u && h == 18u);
    assert(g1_bar_copy_rect(5, 3, 5, 3, 0, 0, &w, &h) && w == 1u && h == 1u);
    /* destination flush against the screen edge is fine, one past is not */
    assert(g1_bar_copy_rect(0, 0, 99, 17, 700, 582, &w, &h));
    assert(!g1_bar_copy_rect(0, 0, 99, 17, 701, 582, &w, &h));
    assert(!g1_bar_copy_rect(0, 0, 99, 17, 700, 583, &w, &h));
    /* inverted, negative or NULL requests are refused and leave the outputs alone */
    w = 7u; h = 9u;
    assert(!g1_bar_copy_rect(10, 0, 9, 17, 0, 0, &w, &h));
    assert(!g1_bar_copy_rect(0, 10, 99, 9, 0, 0, &w, &h));
    assert(!g1_bar_copy_rect(-1, 0, 99, 17, 0, 0, &w, &h));
    assert(!g1_bar_copy_rect(0, -1, 99, 17, 0, 0, &w, &h));
    assert(!g1_bar_copy_rect(0, 0, 99, 17, -1, 0, &w, &h));
    assert(!g1_bar_copy_rect(0, 0, 99, 17, 0, -1, &w, &h));
    assert(!g1_bar_copy_rect(0, 0, 99, 17, 0, 0, NULL, &h));
    assert(!g1_bar_copy_rect(0, 0, 99, 17, 0, 0, &w, NULL));
    assert(!g1_bar_copy_rect(0, 0, 0x7FFFFFFF, 17, 0, 0, &w, &h));
    assert(w == 7u && h == 9u);

    /* span: the last row only needs its own width, not the whole pitch */
    assert(g1_bar_copy_source_span(4u, 2u, 300u, 100u, 18u, &offset, &span));
    assert(offset == 2u * 300u + 4u && span == 17u * 300u + 100u);
    assert(!g1_bar_copy_source_span(250u, 0u, 300u, 100u, 18u, &offset, &span));
    assert(!g1_bar_copy_source_span(0u, 0u, 300u, 0u, 18u, &offset, &span));

    /* pack: strided rows end up packed with stride == width, nothing else is written */
    for (i = 0; i < sizeof(src); ++i) src[i] = (uint8_t)(i % 253u + 1u);
    memset(out, 0xEE, sizeof(out));
    assert(g1_bar_copy_pack(src, 300u, 4u, 2u, 100u, 18u, out) == 1800u);
    for (row = 0u; row < 18u; ++row)
        assert(memcmp(out + row * 100u, src + (2u + row) * 300u + 4u, 100u) == 0);
    assert(out[1800] == 0xEE);
    /* rejected requests write nothing */
    memset(out, 0xEE, 64u);
    assert(g1_bar_copy_pack(NULL, 300u, 4u, 2u, 100u, 18u, out) == 0u);
    assert(g1_bar_copy_pack(src, 300u, 4u, 2u, 100u, 18u, NULL) == 0u);
    assert(g1_bar_copy_pack(src, 90u, 4u, 2u, 100u, 18u, out) == 0u);
    assert(out[0] == 0xEE);
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


def test_bar_copy_call_site_is_hooked_with_the_original_called_first() -> None:
    source = MIRROR.read_text(encoding="utf-8")
    makefile = MAKEFILE.read_text(encoding="utf-8")
    assert '#include "g1_bar_copy.h"' in source
    assert "g1_bar_copy.h" in makefile
    assert "#define G1_BAR_COPY_SITE 0x004B5493u" in source
    assert "#define G1_BAR_COPY_FUNC 0x00468BB0u" in source
    assert "{0xE8, 0x18, 0x37, 0xFB, 0xFF}" in source
    # default on, only an explicit "0" turns the mirror off
    env = source.index("G1_BAR_COPY_ENV, value")
    assert "!(size == 1u && value[0] == '0')" in source[env:env + 200]
    body = _function_body(source, "static DWORD __attribute__((thiscall)) mirror_bar_copy_site(")
    # thiscall, ten stack arguments (ret 0x28); the original always runs first
    for name in ("dst", "dst_pitch", "src", "src_pitch", "sx0", "sy0", "sx1", "sy1", "dx", "dy"):
        assert name in body
    original = body.index("original(")
    assert original < body.index("g1_bar_copy_rect(") < body.index("transfer_block_copy_to_screen(")
    assert "G1_RENDERER_BUFFER" in body and "G1_RENDERER_STRIDE" in body
    assert "readable_bytes(" in body and "g1_bar_copy_pack(" in body
    assert "g_bar_copy_calls" in body and "g_bar_copy_mirrored" in body
    assert "g_bar_copy_rejects" in body and "g_bar_copy_pixels" in body
    install = _function_body(source, "BOOL g1_mirror2x_primitives_install(")
    assert "install_callsite(G1_BAR_COPY_SITE" in install
    detach = _function_body(source, "void g1_mirror2x_primitives_detach(")
    assert "restore_hook(&g_hook_bar_copy)" in detach
    assert "g_hook_bar_copy.installed" in _function_body(
        source, "BOOL g1_mirror2x_primitives_installed(")


def test_bar_copy_counters_are_reported_on_every_present_row() -> None:
    header = HEADER.read_text(encoding="utf-8")
    trace = DIRECT_DRAW.read_text(encoding="utf-8")
    for name in ("calls", "mirrored", "rejects", "pixels"):
        assert f"g1_mirror2x_bar_copy_{name}(void)" in header
        assert f"g1_mirror2x_bar_copy_{name}()" in trace
        assert f'\\"bar_copy_468bb0_{name}\\"' in trace
