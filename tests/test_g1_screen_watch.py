"""Host-side contracts for the G1 screen-sample write watch (H-B3, diagnostic only)."""

from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STUB = ROOT / "tools/inmm_stub"


def test_screen_watch_helpers_build_dr7_addresses_and_slots(tmp_path: Path) -> None:
    fixture = tmp_path / "screen_watch_contract.c"
    executable = tmp_path / "screen_watch_contract"
    fixture.write_text(
        r'''#include <assert.h>
#include "g1_screen_watch.h"

int main(void) {
    /* three sample slots: local enable bits 0/2/4, RW=01 (write) at 16/20/24, LEN=00 */
    assert(g1_screen_watch_dr7(3u, 0) == 0x01110015ul);
    /* selftest adds slot 3 (enable bit 6, RW3=01 at bit 28) */
    assert(g1_screen_watch_dr7(3u, 1) == 0x11110055ul);
    assert(g1_screen_watch_dr7(0u, 0) == 0ul);
    assert(g1_screen_watch_dr7(1u, 0) == 0x00010001ul);
    /* buffer + y*stride + x */
    assert(g1_screen_watch_address(0x1000ul, 832ul, 112u, 126u) == 0x1000ul + 126ul * 832ul + 112u);
    /* lowest set Dr6 bit among slots 0..3, 4 = none */
    assert(G1_SCREEN_WATCH_CACHE_BASE == 0x00BA3D30ul && G1_SCREEN_WATCH_CACHE_PITCH == 832ul);
    assert(g1_screen_watch_address(G1_SCREEN_WATCH_CACHE_BASE, G1_SCREEN_WATCH_CACHE_PITCH, 100u, 60u) == 0x00BA3D30ul + 60ul * 832ul + 100u);
    assert(g1_screen_watch_slot(0x1ul) == 0u);
    assert(g1_screen_watch_slot(0x4ul) == 2u);
    assert(g1_screen_watch_slot(0x6ul) == 1u);
    assert(g1_screen_watch_slot(0x8ul) == 3u);
    assert(g1_screen_watch_slot(0x0ul) == 4u);
    assert(g1_screen_watch_slot(0xFFFF0FF0ul) == 4u);
    /* pinned-EXE .text only */
    assert(g1_screen_watch_in_exe_text(0x00467692ul));
    assert(!g1_screen_watch_in_exe_text(0x00400FFFul));
    assert(!g1_screen_watch_in_exe_text(0x004E4AE6ul));
    /* module class: exe image base / our dll base / other */
    assert(g1_screen_watch_module_class(0x400000ul, 0x400000ul, 0x10000000ul) == 0u);
    assert(g1_screen_watch_module_class(0x10000000ul, 0x400000ul, 0x10000000ul) == 1u);
    assert(g1_screen_watch_module_class(0x7B000000ul, 0x400000ul, 0x10000000ul) == 2u);
    assert(g1_screen_watch_module_class(0ul, 0x400000ul, 0x10000000ul) == 3u);
    return 0;
}
''',
        encoding="utf-8",
    )
    subprocess.run(
        ["gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", f"-I{STUB}", str(fixture),
         "-o", str(executable)],
        check=True,
    )
    subprocess.run([str(executable)], check=True)


def test_screen_watch_module_contract() -> None:
    """The VEH-based all-thread DR watch is env-gated and never writes the game buffer."""
    source = (STUB / "g1_screen_watch.c").read_text(encoding="utf-8")
    header = (STUB / "g1_screen_watch.h").read_text(encoding="utf-8")
    makefile = (STUB / "Makefile").read_text(encoding="utf-8")
    assert "g1_screen_watch.c" in makefile and "g1_screen_watch.h" in makefile
    assert '#define G1_SCREEN_WATCH_ENV "SYW2_G1_SCREEN_WATCH"' in source
    assert 'C:\\\\inmm_g1_screen_watch.jsonl' in source
    # env off => first statement of the present hook returns before anything is installed
    present = source[source.index("void g1_screen_watch_on_present("):]
    present = present[: present.index("\n}\n")]
    gate = present.index("if (!screen_watch_on()) return;")
    assert gate < present.index("CreateFileA") < present.index("AddVectoredExceptionHandler")
    assert "AddVectoredExceptionHandler" in source
    assert source.index("screen_watch_on()") < source.index("AddVectoredExceptionHandler")
    # every thread of the process is armed (Toolhelp32), failures are counted
    assert "CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD" in source
    assert "th32OwnerProcessID" in source
    assert "SuspendThread" in source and "SetThreadContext" in source
    assert "g_sw_arm_fail" in source and "g_sw_arm_ok" in source
    # selftest on the private byte through slot 3 before the real arm
    assert "g_sw_selftest_byte" in source and '\\"t\\":\\"s\\"' in source
    # hit record carries who/where/what
    handler = source[source.index("sw_veh("):]
    handler = handler[: handler.index("\n}\n")]
    for key in ('\\"t\\":\\"x\\"', '\\"eip\\"', '\\"tid\\"', '\\"pt\\"', '\\"val\\"',
                '\\"mod\\"', '\\"guard\\"', '\\"st\\"'):
        assert key in handler
    assert "SW_RAW_LIMIT" in source and "20000u" in source
    assert "g1_mirror2x_primitive_guard()" in handler
    # arming and match records
    assert '\\"t\\":\\"a\\"' in source and '\\"t\\":\\"m\\"' in source
    assert '\\"t\\":\\"k\\"' in source
    # the game buffer is only ever read (no store through the watched pointers)
    assert "*(BYTE *)g_sw_addr" not in source
    assert "g1_screen_watch_on_present(" in header


def test_mirror_present_calls_screen_watch_and_exposes_guard() -> None:
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    header = (STUB / "g1_mirror2x.h").read_text(encoding="utf-8")
    assert '#include "g1_screen_watch.h"' in mirror
    assert "DWORD g1_mirror2x_primitive_guard(void);" in header
    assert "DWORD g1_mirror2x_primitive_guard(void) { return (DWORD)g_primitive_guard; }" in mirror
    call = mirror.index("g1_screen_watch_on_present(")
    drift = mirror.index("layer_drift_present((const BYTE *)source_desc.lpSurface")
    assert drift < call < mirror.index("s3_overlay_at_present((const BYTE *)source_desc.lpSurface")
    assert "g_drift_present" in mirror[call: call + 200]


def test_probe_exposes_screen_watch_option_for_the_candidate_lane_only() -> None:
    source = (ROOT / "tools/g1_saved_scene_probe.py").read_text(encoding="utf-8")
    assert '"--screen-watch"' in source
    assert "--screen-watch requires --layer-drift" in source
    assert "screen_watch=args.screen_watch" in source
    candidate_env = source[source.index("if candidate:"):source.index("xvfb, display = runtime_env._xvfb")]
    assert 'env["SYW2_G1_SCREEN_WATCH"] = "1"' in candidate_env
    baseline_env = source[source.index("def _run_lane("):source.index("if candidate:")]
    assert "SYW2_G1_SCREEN_WATCH" not in baseline_env
    assert 'prefix / "drive_c" / "inmm_g1_screen_watch.jsonl"' in source
    assert '"screen_watch.jsonl"' in source


def test_screen_watch_cache_option_watches_the_terrain_cache_for_the_candidate_lane_only() -> None:
    watch = (STUB / "g1_screen_watch.c").read_text(encoding="utf-8")
    assert '#define G1_SCREEN_WATCH_CACHE_ENV "SYW2_G1_SCREEN_WATCH_CACHE"' in watch
    present = watch[watch.index("void g1_screen_watch_on_present("):]
    assert "g_sw_cache" in present and "G1_SCREEN_WATCH_CACHE_BASE" in present
    source = (ROOT / "tools/g1_saved_scene_probe.py").read_text(encoding="utf-8")
    assert '"--screen-watch-cache"' in source
    assert "--screen-watch-cache requires --screen-watch" in source
    assert "screen_watch_cache=args.screen_watch_cache" in source
    candidate_env = source[source.index("if candidate:"):source.index("xvfb, display = runtime_env._xvfb")]
    assert 'env["SYW2_G1_SCREEN_WATCH_CACHE"] = "1"' in candidate_env
    baseline_env = source[source.index("def _run_lane("):source.index("if candidate:")]
    assert "SYW2_G1_SCREEN_WATCH_CACHE" not in baseline_env
