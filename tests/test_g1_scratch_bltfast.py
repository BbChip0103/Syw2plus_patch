"""Host-side contracts for the H-PS5W1 scratch BltFast (uncloned back buffer vtable) mirror."""

from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STUB = ROOT / "tools/inmm_stub"
MIRROR = STUB / "g1_mirror2x.c"
HEADER = STUB / "g1_mirror2x.h"
DIRECT_DRAW = STUB / "direct_draw_trace.c"
MAKEFILE = STUB / "Makefile"
SCRATCH = STUB / "g1_scratch_bltfast.h"

SITES = (0x4048D2, 0x405A06, 0x4B6D66, 0x4B7369, 0x4D1338, 0x4D1E27, 0x4D77EA)


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


def _compile_and_run(tmp_path: Path, name: str, body: str) -> None:
    fixture = tmp_path / f"{name}.c"
    executable = tmp_path / name
    fixture.write_text(body, encoding="utf-8")
    build = subprocess.run(
        ["gcc", "-std=c99", "-Wall", "-Wextra", "-Werror", f"-I{STUB}", str(fixture),
         "-o", str(executable)],
        capture_output=True, text=True, check=False,
    )
    assert build.returncode == 0, build.stderr
    run = subprocess.run([str(executable)], capture_output=True, text=True, check=False)
    assert run.returncode == 0, run.stderr


def test_scratch_bltfast_gate_states_and_rects(tmp_path: Path) -> None:
    sites = ", ".join(f"0x{site:X}u" for site in SITES)
    _compile_and_run(tmp_path, "scratch_bltfast_gate", rf'''#include <assert.h>
#include "g1_scratch_bltfast.h"

int main(void) {{
    static const uint32_t sites[7] = {{{sites}}};
    unsigned index;
    G1ScratchRect rect;
    /* menu list states only: 5 (single-player lobby) and 7; the in-game state keeps its own path */
    assert(g1_scratch_bltfast_state_accepts(5u));
    assert(g1_scratch_bltfast_state_accepts(7u));
    assert(!g1_scratch_bltfast_state_accepts(3u));
    assert(!g1_scratch_bltfast_state_accepts(20u));
    assert(!g1_scratch_bltfast_state_accepts(0u));
    assert(!g1_scratch_bltfast_state_accepts(0xFFFFFFFFu));
    /* the seven known screen-interface BltFast return addresses map to slots 0..6, else 7 */
    for (index = 0u; index < 7u; ++index)
        assert(g1_scratch_bltfast_site_index(sites[index]) == index);
    assert(g1_scratch_bltfast_site_index(0x49273Fu) == 7u);
    assert(g1_scratch_bltfast_site_index(0u) == 7u);
    /* a plain source rectangle lands at (x, y) with the source size */
    assert(g1_scratch_bltfast_rect(20u, 44u, 1, 0, 0, 100, 9, &rect));
    assert(rect.x == 20 && rect.y == 44 && rect.w == 100 && rect.h == 9);
    /* the source rectangle origin does not move the destination */
    assert(g1_scratch_bltfast_rect(20u, 44u, 1, 30, 40, 130, 49, &rect));
    assert(rect.x == 20 && rect.y == 44 && rect.w == 100 && rect.h == 9);
    /* the part past the 800x600 logical frame is clipped */
    assert(g1_scratch_bltfast_rect(750u, 590u, 1, 0, 0, 100, 30, &rect));
    assert(rect.x == 750 && rect.y == 590 && rect.w == 50 && rect.h == 10);
    /* a missing, empty or inverted source rectangle and an origin outside the frame are refused */
    assert(!g1_scratch_bltfast_rect(20u, 44u, 0, 0, 0, 100, 9, &rect));
    assert(!g1_scratch_bltfast_rect(20u, 44u, 1, 5, 5, 5, 9, &rect));
    assert(!g1_scratch_bltfast_rect(20u, 44u, 1, 5, 9, 50, 9, &rect));
    assert(!g1_scratch_bltfast_rect(20u, 44u, 1, 50, 5, 5, 9, &rect));
    assert(!g1_scratch_bltfast_rect(20u, 44u, 1, -1, 0, 10, 9, &rect));
    assert(!g1_scratch_bltfast_rect(800u, 44u, 1, 0, 0, 10, 9, &rect));
    assert(!g1_scratch_bltfast_rect(20u, 600u, 1, 0, 0, 10, 9, &rect));
    assert(!g1_scratch_bltfast_rect(20u, 44u, 1, 0, 0, 10, 9, 0));
    return 0;
}}
''')


def test_scratch_bltfast_queue_is_bounded_and_flushes_empty(tmp_path: Path) -> None:
    _compile_and_run(tmp_path, "scratch_bltfast_queue", r'''#include <assert.h>
#include "g1_scratch_bltfast.h"

int main(void) {
    G1ScratchQueue queue = {0};
    G1ScratchRect rect = {1, 2, 3, 4};
    unsigned index;
    g1_scratch_queue_reset(&queue);
    assert(queue.count == 0u && queue.overflow == 0u);
    for (index = 0u; index < G1_SCRATCH_BLTFAST_MAX_RECTS; ++index)
        assert(g1_scratch_queue_push(&queue, &rect));
    assert(queue.count == G1_SCRATCH_BLTFAST_MAX_RECTS);
    /* the next rectangle is dropped and counted, never written past the array */
    assert(!g1_scratch_queue_push(&queue, &rect));
    assert(queue.count == G1_SCRATCH_BLTFAST_MAX_RECTS && queue.overflow == 1u);
    assert(!g1_scratch_queue_push(&queue, &rect) && queue.overflow == 2u);
    assert(!g1_scratch_queue_push(0, &rect));
    assert(!g1_scratch_queue_push(&queue, 0));
    /* reset empties the queue but keeps the overflow total as a run-wide diagnostic */
    g1_scratch_queue_reset(&queue);
    assert(queue.count == 0u && queue.overflow == 2u);
    assert(g1_scratch_queue_push(&queue, &rect) && queue.count == 1u);
    return 0;
}
''')


def test_scratch_bltfast_wrapper_records_and_calls_the_original_once() -> None:
    source = MIRROR.read_text(encoding="utf-8")
    makefile = MAKEFILE.read_text(encoding="utf-8")
    assert '#include "g1_scratch_bltfast.h"' in source
    assert "g1_scratch_bltfast.h" in makefile
    # default on, only an explicit "0" turns the mirror off
    assert '"SYW2_G1_SCRATCH_BLTFAST_MIRROR"' in source
    env = source.index("G1_SCRATCH_BLTFAST_ENV, value")
    assert "!(size == 1u && value[0] == '0')" in source[env:env + 200]
    body = _function_body(source, "static HRESULT WINAPI mirror_scratch_blt_fast(")
    # the wrapper only records the rectangle: no Lock, the original runs exactly once
    assert body.count("g_scratch_original_blt_fast(") == 1
    assert "Lock(" not in body
    assert "g1_scratch_bltfast_rect(" in body
    assert "g1_scratch_queue_push(" in body
    assert "g1_scratch_bltfast_state_accepts(" in body
    assert "g1_scratch_bltfast_site_index(" in body
    assert "__builtin_return_address(0)" in body
    assert "g_primitive_guard" in body
    for counter in ("g_scratch_calls", "g_scratch_recorded", "g_scratch_rejects"):
        assert counter in body


def test_scratch_bltfast_adopts_an_uncloned_back_buffer_vtable() -> None:
    source = MIRROR.read_text(encoding="utf-8")
    adopt = _function_body(source, "void g1_mirror2x_scratch_bltfast_adopt(")
    assert "G1_BACK_BUFFER_VA" in adopt
    assert "HeapAlloc(" in adopt
    # the clone copies the original vtable and only replaces BltFast
    assert "*g_scratch_clone = *" in adopt
    assert "->BltFast = mirror_scratch_blt_fast" in adopt
    assert "lpVtbl = g_scratch_clone" in adopt
    # a surface the DirectDraw trace already cloned (record present) is never adopted twice
    assert "g_scratch_adopt_skipped_record" in adopt
    assert "g_scratch_adopts" in adopt
    # a record-bearing surface returns before anything is allocated or replaced (keeps the trace hook)
    record = adopt[adopt.index("if (has_record)"):adopt.index("back == g_scratch_surface")]
    assert "g_scratch_adopt_skipped_record" in record and "return;" in record
    assert "->lpVtbl" not in record and "HeapAlloc(" not in record
    assert adopt.index("if (has_record)") < adopt.index("HeapAlloc(")
    # an already adopted object whose vtable is still the clone is left alone (no clone chain)
    assert "back == g_scratch_surface && back->lpVtbl == g_scratch_clone" in adopt
    assert adopt.index("back->lpVtbl == g_scratch_clone") < adopt.index("HeapAlloc(")
    # the adoption runs from the primary present, only for a back buffer without a trace record
    trace = DIRECT_DRAW.read_text(encoding="utf-8")
    present = trace[trace.index("static HRESULT WINAPI hook_blt_fast"):]
    assert "g1_mirror2x_scratch_bltfast_adopt(" in present
    assert present.index("g1_mirror2x_scratch_bltfast_adopt(") < present.index(
        "g1_mirror2x_copy_present(")


def test_scratch_bltfast_flush_diffs_against_expected_before_the_present_loop() -> None:
    source = MIRROR.read_text(encoding="utf-8")
    flush = _function_body(source, "static void scratch_bltfast_at_present(")
    # expected snapshot is the "before", the locked back buffer the "after"
    assert "g_expected_snapshot" in flush
    assert "g1_overlay_blt_apply_tiled(" in flush
    assert "g_scratch_queue" in flush and "g1_scratch_queue_reset(" in flush
    assert "g1_scratch_bltfast_state_accepts(" in flush
    assert "g_scratch_flush_pixels" in flush and "g_scratch_flush_applied" in flush
    # the queue is emptied after the rectangles were processed, so the next present never replays them
    loop = flush.index("for (index = 0u; index < g_scratch_queue.count")
    assert flush.rindex("g1_scratch_queue_reset(&g_scratch_queue);") > loop
    assert flush[flush.rindex("g1_scratch_queue_reset(&g_scratch_queue);"):].replace(
        "g1_scratch_queue_reset(&g_scratch_queue);", "").strip() == "}"
    present = _function_body(source, "HRESULT g1_mirror2x_copy_present(")
    call = "scratch_bltfast_at_present((const BYTE *)source_desc.lpSurface"
    assert call in present
    # before the per-pixel stale test, so the repaired pixels count as covered
    assert present.index(call) < present.index("for (y = 0; y < height; ++y)")
    assert present.index("rect_blt_heal_at_present(") < present.index(call)


def test_scratch_bltfast_counters_are_reported_on_every_present_row() -> None:
    header = HEADER.read_text(encoding="utf-8")
    trace = DIRECT_DRAW.read_text(encoding="utf-8")
    for name in ("calls", "recorded", "rejects", "flush_applied", "flush_pixels", "adopts",
                 "adopt_skipped_record", "overflow", "other_site_calls"):
        assert f"g1_mirror2x_scratch_bltfast_{name}(void)" in header
        assert f"g1_mirror2x_scratch_bltfast_{name}()" in trace
        assert f'\\"scratch_bltfast_{name}\\"' in trace
    assert "g1_mirror2x_scratch_bltfast_site_calls(DWORD index)" in header
    assert "g1_mirror2x_scratch_bltfast_site_calls(" in trace
    assert '\\"scratch_bltfast_site_calls\\"' in trace
