"""Host-side contracts for the H-PM2 PS23 pause-screen snapshot restore."""

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


def test_pause_snapshot_helpers_pick_and_transition(tmp_path: Path) -> None:
    fixture = tmp_path / "pause_snapshot_contract.c"
    executable = tmp_path / "pause_snapshot_contract"
    fixture.write_text(
        r'''#include <assert.h>
#include "g1_pause_snapshot.h"

int main(void) {
    /* existing HD (covered and expected == pixel) always wins, snapshot or not */
    assert(g1_pause_restore_pick(1, 5u, 5u, 0, 0u) == G1_PAUSE_PICK_EXISTING_HD);
    assert(g1_pause_restore_pick(1, 5u, 5u, 1, 9u) == G1_PAUSE_PICK_EXISTING_HD);
    /* panel overwrote expected, pixel is back to the world value: restore */
    assert(g1_pause_restore_pick(1, 77u, 5u, 1, 5u) == G1_PAUSE_PICK_RESTORE);
    /* already uncovered (stale cleared earlier) also restores when snapshot matches */
    assert(g1_pause_restore_pick(0, 0u, 5u, 1, 5u) == G1_PAUSE_PICK_RESTORE);
    /* snapshot disagrees with the pixel: stay nearest */
    assert(g1_pause_restore_pick(1, 77u, 5u, 1, 6u) == G1_PAUSE_PICK_NEAREST);
    assert(g1_pause_restore_pick(0, 0u, 5u, 1, 6u) == G1_PAUSE_PICK_NEAREST);
    /* invalid snapshot entry: stay nearest even if the byte happens to match */
    assert(g1_pause_restore_pick(1, 77u, 5u, 0, 5u) == G1_PAUSE_PICK_NEAREST);
    assert(g1_pause_restore_pick(0, 0u, 0u, 0, 0u) == G1_PAUSE_PICK_NEAREST);

    /* state transitions: capture on entering 23, invalidate on leaving it */
    assert(g1_pause_snapshot_action(3u, 23u) == G1_PAUSE_ACTION_CAPTURE);
    assert(g1_pause_snapshot_action(0u, 23u) == G1_PAUSE_ACTION_CAPTURE);
    assert(g1_pause_snapshot_action(23u, 23u) == G1_PAUSE_ACTION_NONE);
    assert(g1_pause_snapshot_action(23u, 3u) == G1_PAUSE_ACTION_INVALIDATE);
    assert(g1_pause_snapshot_action(23u, 9u) == G1_PAUSE_ACTION_INVALIDATE);
    assert(g1_pause_snapshot_action(3u, 3u) == G1_PAUSE_ACTION_NONE);
    assert(g1_pause_snapshot_action(3u, 9u) == G1_PAUSE_ACTION_NONE);

    /* restore only applies while the program state is the pause screen */
    assert(g1_pause_restore_active(23u, 1));
    assert(!g1_pause_restore_active(3u, 1));
    assert(!g1_pause_restore_active(23u, 0));
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


def test_present_loop_restores_pause_snapshot_before_nearest_fallback() -> None:
    source = MIRROR.read_text(encoding="utf-8")
    header = HEADER.read_text(encoding="utf-8")
    makefile = MAKEFILE.read_text(encoding="utf-8")
    assert '#include "g1_pause_snapshot.h"' in source
    assert "g1_pause_snapshot.h" in makefile
    assert 'SYW2_G1_PAUSE_SNAPSHOT' in source
    assert "pause_snapshot_pixels" in header and "pause_restore_pixels" in header
    assert "g1_mirror2x_pause_restore_total(void)" in header
    body = _function_body(source, "HRESULT g1_mirror2x_copy_present(")
    assert "g1_pause_snapshot_action(" in body
    assert "g1_pause_restore_pick(" in body
    # the snapshot buffers are optional: allocation failure keeps the old behaviour
    assert "g_pause_hd" in body and "g_pause_valid" in body and "g_pause_expected" in body
    # a restored pixel is covered again and never counted stale
    pick = body.index("g1_pause_restore_pick(")
    assert body.index("G1_PAUSE_PICK_RESTORE", pick) > pick
    assert "g_pause_restore_total" in source


def test_pause_snapshot_trace_fields_and_buffers_are_wired() -> None:
    source = MIRROR.read_text(encoding="utf-8")
    trace = DIRECT_DRAW.read_text(encoding="utf-8")
    assert "pause_snapshot_pixels" in trace and "pause_restore_pixels" in trace
    assert "pause_restore_total" in trace
    assert "g1_mirror2x_pause_restore_total()" in trace
    install = _function_body(source, "BOOL g1_mirror2x_primitives_install(")
    assert "g_pause_hd = " in install and "g_pause_valid = " in install
    assert "g_pause_expected = " in install
    # buffer failure must not abort the hook install
    assert "!g_pause_hd ||" not in install
    assert "g_pause_snapshot_enabled = FALSE" in install
