"""Host-side contracts for the H-SC2 briefing compose (0x4B23B5 -> 0x4D4620) mirror."""

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


def test_briefing_compose_gate_accepts_only_the_ps20_back_buffer(tmp_path: Path) -> None:
    fixture = tmp_path / "briefing_compose_contract.c"
    executable = tmp_path / "briefing_compose_contract"
    fixture.write_text(
        r'''#include <assert.h>
#include "g1_briefing_compose.h"

int main(void) {
    /* state 20, dest == back buffer, 8-bit 800x600 surface */
    assert(g1_briefing_compose_accepts(20u, 0x1000u, 0x1000u, 800u, 600u, 800u, 8u));
    assert(g1_briefing_compose_accepts(20u, 0x1000u, 0x1000u, 800u, 600u, 1600u, 8u));
    assert(g1_briefing_compose_accepts(20u, 0x1000u, 0x1000u, 1600u, 600u, 2048u, 8u));
    /* menu-state flip-chain back buffer: 1600x1200 whose top-left 800x600 is the logical frame */
    assert(g1_briefing_compose_accepts(20u, 0x1000u, 0x1000u, 1600u, 1200u, 1600u, 8u));
    /* other program states never mirror */
    assert(!g1_briefing_compose_accepts(3u, 0x1000u, 0x1000u, 800u, 600u, 800u, 8u));
    assert(!g1_briefing_compose_accepts(19u, 0x1000u, 0x1000u, 800u, 600u, 800u, 8u));
    assert(!g1_briefing_compose_accepts(21u, 0x1000u, 0x1000u, 800u, 600u, 800u, 8u));
    /* destination must be the back buffer and non-null (the 0x41C362 caller uses another) */
    assert(!g1_briefing_compose_accepts(20u, 0x2000u, 0x1000u, 800u, 600u, 800u, 8u));
    assert(!g1_briefing_compose_accepts(20u, 0u, 0u, 800u, 600u, 800u, 8u));
    /* geometry/format mismatches are refused */
    assert(!g1_briefing_compose_accepts(20u, 0x1000u, 0x1000u, 799u, 600u, 800u, 8u));
    assert(!g1_briefing_compose_accepts(20u, 0x1000u, 0x1000u, 800u, 1200u, 800u, 8u));
    assert(!g1_briefing_compose_accepts(20u, 0x1000u, 0x1000u, 1600u, 1199u, 1600u, 8u));
    assert(!g1_briefing_compose_accepts(20u, 0x1000u, 0x1000u, 1599u, 1200u, 1600u, 8u));
    assert(!g1_briefing_compose_accepts(20u, 0x1000u, 0x1000u, 800u, 600u, 799u, 8u));
    assert(!g1_briefing_compose_accepts(20u, 0x1000u, 0x1000u, 800u, 600u, 2049u, 8u));
    assert(!g1_briefing_compose_accepts(20u, 0x1000u, 0x1000u, 800u, 600u, 1600u, 16u));
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


def test_briefing_compose_call_site_is_hooked_around_the_original() -> None:
    source = MIRROR.read_text(encoding="utf-8")
    makefile = MAKEFILE.read_text(encoding="utf-8")
    assert '#include "g1_briefing_compose.h"' in source
    assert "g1_briefing_compose.h" in makefile
    assert "#define G1_BRIEFING_COMPOSE_SITE 0x004B23B5u" in source
    assert "#define G1_BRIEFING_COMPOSE_FUNC 0x004D4620u" in source
    assert "#define G1_BACK_BUFFER_VA 0x00E5D438u" in source
    assert '"SYW2_G1_BRIEFING_COMPOSE"' in source
    # old bytes: call 0x4D4620 from 0x4B23B5 (rel32 0x22266)
    assert "{0xE8, 0x66, 0x22, 0x02, 0x00}" in source
    # default on, only an explicit "0" turns the mirror off
    env = source.index("G1_BRIEFING_COMPOSE_ENV, value")
    assert "!(size == 1u && value[0] == '0')" in source[env:env + 200]
    body = _function_body(source, "static DWORD __attribute__((thiscall)) mirror_briefing_compose_site(")
    # thiscall with one stack argument (ret 4): the before copy is taken, the original runs
    # once, then the surface is locked again and the changed pixels are mirrored
    assert body.index("Lock(") < body.index("original(") < body.rindex("Lock(")
    assert "g1_briefing_compose_accepts(" in body
    assert "G1_PROGRAM_STATE_VA" in body and "G1_BACK_BUFFER_VA" in body
    assert "g1_overlay_blt_apply_tiled(" in body
    # both Lock phases validate the surface with the same gate
    assert body.count("g1_briefing_compose_accepts(") == 2
    assert "DDLOCK_WAIT" in body
    for counter in ("g_briefing_compose_calls", "g_briefing_compose_mirrored",
                    "g_briefing_compose_changed_pixels", "g_briefing_compose_rejects"):
        assert counter in body
    install = _function_body(source, "BOOL g1_mirror2x_primitives_install(")
    assert "install_callsite(G1_BRIEFING_COMPOSE_SITE" in install
    detach = _function_body(source, "void g1_mirror2x_primitives_detach(")
    assert "restore_hook(&g_hook_briefing_compose)" in detach
    assert "g_hook_briefing_compose.installed" in _function_body(
        source, "BOOL g1_mirror2x_primitives_installed(")


def test_briefing_compose_counters_are_reported_on_every_present_row() -> None:
    header = HEADER.read_text(encoding="utf-8")
    trace = DIRECT_DRAW.read_text(encoding="utf-8")
    for name in ("calls", "mirrored", "pixels", "rejects"):
        assert f"g1_mirror2x_briefing_compose_{name}(void)" in header
        assert f"g1_mirror2x_briefing_compose_{name}()" in trace
        assert f'\\"briefing_compose_4d4620_{name}\\"' in trace
