"""Host-side contracts for the G1 0x465FC0 unclipped block-fill layer mirror (H-D2k-s0)."""

from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STUB = ROOT / "tools/inmm_stub"


def test_cache_fill_region_matches_original_dword_fill(tmp_path: Path) -> None:
    fixture = tmp_path / "cache_fill_contract.c"
    executable = tmp_path / "cache_fill_contract"
    fixture.write_text(
        r'''#include <assert.h>
#include <stdint.h>
#include "g1_cache_fill.h"

int main(void) {
    G1RectFill r;
    /* both corners inclusive, width floored to whole dwords (4 px) */
    assert(g1_cache_fill_region(100, 60, 199, 69, 8, 832, 512, &r) == 1);
    assert(r.x == 100 && r.y == 60 && r.width == 100u && r.height == 10u);
    assert(g1_cache_fill_region(100, 60, 202, 69, 8, 832, 512, &r) == 1);
    assert(r.x == 100 && r.y == 60 && r.width == 100u && r.height == 10u);
    /* swapped corners are sorted per axis */
    assert(g1_cache_fill_region(199, 69, 100, 60, 8, 832, 512, &r) == 1);
    assert(r.x == 100 && r.y == 60 && r.width == 100u && r.height == 10u);
    assert(g1_cache_fill_region(199, 60, 100, 69, 8, 832, 512, &r) == 1);
    assert(r.x == 100 && r.y == 60 && r.width == 100u && r.height == 10u);
    /* narrower than one dword writes nothing */
    assert(g1_cache_fill_region(10, 10, 12, 20, 8, 832, 512, &r) == 0);
    /* exactly one dword */
    assert(g1_cache_fill_region(10, 10, 13, 10, 8, 832, 512, &r) == 1);
    assert(r.x == 10 && r.y == 10 && r.width == 4u && r.height == 1u);
    /* full cache */
    assert(g1_cache_fill_region(0, 0, 831, 511, 8, 832, 512, &r) == 1);
    assert(r.x == 0 && r.y == 0 && r.width == 832u && r.height == 512u);
    /* the original never clips: anything leaving the cache is unsupported (-1) */
    assert(g1_cache_fill_region(-4, 0, 99, 9, 8, 832, 512, &r) == -1);
    assert(g1_cache_fill_region(0, -1, 99, 9, 8, 832, 512, &r) == -1);
    assert(g1_cache_fill_region(800, 0, 835, 9, 8, 832, 512, &r) == -1);
    assert(g1_cache_fill_region(0, 500, 99, 512, 8, 832, 512, &r) == -1);
    assert(g1_cache_fill_region(INT32_MIN, 0, INT32_MAX, 9, 8, 832, 512, &r) == -1);
    /* a floored width that still fits is mirrored even when the raw width would not */
    assert(g1_cache_fill_region(800, 0, 834, 9, 8, 832, 512, &r) == 1);
    assert(r.x == 800 && r.width == 32u);
    /* only 8-bit pixels (4 per dword) are modelled */
    assert(g1_cache_fill_region(0, 0, 99, 9, 16, 832, 512, &r) == -1);
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


def test_cache_fill_hook_table_and_wrapper_contract() -> None:
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    header = (STUB / "g1_mirror2x.h").read_text(encoding="utf-8")
    bridge = (STUB / "direct_draw_trace.c").read_text(encoding="utf-8")
    makefile = (STUB / "Makefile").read_text(encoding="utf-8")
    assert '#include "g1_cache_fill.h"' in mirror
    assert "g1_cache_fill.h" in makefile
    assert "#define G1_CACHE_FILL 0x00465FC0u" in mirror
    assert "#define G1_CACHE_FILL_LEN 5u" in mirror
    # prologue: mov edx,[esp+0xC]; push ebx (exact 5-byte instruction boundary)
    assert "expected_cache_fill[G1_CACHE_FILL_LEN] =" in mirror
    assert "{0x8B, 0x54, 0x24, 0x0C, 0x53}" in mirror
    assert "install_one(G1_CACHE_FILL, expected_cache_fill, G1_CACHE_FILL_LEN" in mirror
    assert "restore_hook(&g_hook_cache_fill)" in mirror
    assert "g_hook_cache_fill.installed" in mirror
    # the original runs first (pixels are only known after it), then the layer is updated
    start = mirror.index("mirror_cache_fill(void *renderer")
    body = mirror[start: mirror.index("\n}\n", start)]
    assert "g_original_cache_fill(renderer, x1, y1, x2, y2, color)" in body
    assert body.index("g_original_cache_fill(renderer") < body.index("cache_layer_fill(")
    assert "G1_CACHE_BASE" in body
    # the layer update writes expected + coverage + the flat HD block
    layer = mirror[mirror.index("static void cache_layer_fill("):]
    layer = layer[: layer.index("\n}\n")]
    assert "g_layer_expected[" in layer and "g_layer_covered[" in layer
    assert "g_layer_mirror" in layer
    for counter in ("g_cache_fill_invocations", "g_cache_fill_mirrored_calls",
                    "g_cache_fill_mirrored_pixels", "g_cache_fill_reject_target",
                    "g_cache_fill_unsupported"):
        assert f"static DWORD {counter} = 0u;" in mirror
        assert f"{counter} = 0u;" in mirror[mirror.index("g1_mirror2x_primitives_install"):]
    for accessor in ("g1_mirror2x_cache_fill_invocations",
                     "g1_mirror2x_cache_fill_mirrored_calls",
                     "g1_mirror2x_cache_fill_mirrored_pixels",
                     "g1_mirror2x_cache_fill_reject_target",
                     "g1_mirror2x_cache_fill_unsupported"):
        assert f"DWORD {accessor}(void);" in header
        assert f"DWORD {accessor}(void)" in mirror
        assert f"{accessor}()" in bridge
    assert "cache_fill_465FC0_invocations" in bridge
