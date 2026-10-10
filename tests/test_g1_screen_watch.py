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


def test_screen_watch_state_gate_helpers_default_to_ps3(tmp_path: Path) -> None:
    """H-PM1 PM1-0: SYW2_G1_SCREEN_WATCH_STATE=23 watches PS23; anything else keeps PS3."""
    fixture = tmp_path / "screen_watch_state.c"
    executable = tmp_path / "screen_watch_state"
    fixture.write_text(
        r'''#include <assert.h>
#include "g1_screen_watch.h"

int main(void) {
    assert(g1_screen_watch_state_parse("23", 2u) == 23u);
    assert(g1_screen_watch_state_parse("27", 2u) == 27u);
    assert(g1_screen_watch_state_parse("29", 2u) == 29u);
    /* H-TM1 TM1-0: the one-digit "9" follows the title-menu PS9 (user-registration popup) */
    assert(g1_screen_watch_state_parse("9", 1u) == 9u);
    /* H-SC1 SC1-0: "20" follows the scenario briefing PS20 */
    assert(g1_screen_watch_state_parse("20", 2u) == 20u);
    assert(g1_screen_watch_state_parse("200", 3u) == 3u);
    assert(g1_screen_watch_state_parse("02", 2u) == 3u);
    assert(g1_screen_watch_state_parse("90", 2u) == 3u);
    assert(g1_screen_watch_state_parse("09", 2u) == 3u);
    assert(g1_screen_watch_state_parse("28", 2u) == 3u);
    assert(g1_screen_watch_state_parse("270", 3u) == 3u);
    assert(g1_screen_watch_state_parse("3", 1u) == 3u);
    assert(g1_screen_watch_state_parse("", 0u) == 3u);
    /* H-OS1 OS1-0: "5" / "7" follow the solo lobby PS5 / connection-method PS7 */
    assert(g1_screen_watch_state_parse("5", 1u) == 5u);
    assert(g1_screen_watch_state_parse("7", 1u) == 7u);
    assert(g1_screen_watch_state_parse("4", 1u) == 3u);
    assert(g1_screen_watch_state_parse("57", 2u) == 3u);
    assert(g1_screen_watch_state_parse("05", 2u) == 3u);
    assert(g1_screen_watch_state_parse("230", 3u) == 3u);
    assert(g1_screen_watch_state_parse("2", 1u) == 3u);
    /* PS3 keeps the drift present counter; other states have no drift counter, use the watch's own */
    assert(g1_screen_watch_present_ordinal(3u, 77ul, 5ul) == 77ul);
    assert(g1_screen_watch_present_ordinal(20u, 77ul, 5ul) == 5ul);
    assert(g1_screen_watch_present_ordinal(23u, 77ul, 5ul) == 5ul);
    assert(g1_screen_watch_present_ordinal(27u, 77ul, 5ul) == 5ul);
    assert(g1_screen_watch_present_ordinal(29u, 77ul, 5ul) == 5ul);
    assert(g1_screen_watch_present_ordinal(9u, 77ul, 5ul) == 5ul);
    assert(g1_screen_watch_present_ordinal(5u, 77ul, 5ul) == 5ul);
    assert(g1_screen_watch_present_ordinal(7u, 77ul, 5ul) == 5ul);
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


def test_screen_watch_present_hook_uses_the_state_gate() -> None:
    source = (STUB / "g1_screen_watch.c").read_text(encoding="utf-8")
    assert '#define G1_SCREEN_WATCH_STATE_ENV "SYW2_G1_SCREEN_WATCH_STATE"' in source
    present = source[source.index("void g1_screen_watch_on_present("):]
    present = present[: present.index("\n}\n")]
    # env absent => g_sw_watch_state stays 3 => the old `!= 3u` early return is unchanged
    assert "!= 3u) return;" not in present
    assert "!= g_sw_watch_state) return;" in present
    assert "g1_screen_watch_present_ordinal(" in present
    assert "g1_screen_watch_state_parse(" in source[: source.index("void g1_screen_watch_on_present(")]


def test_probe_screen_watch_state_option_and_new_game_path_wiring() -> None:
    source = (ROOT / "tools/g1_saved_scene_probe.py").read_text(encoding="utf-8")
    assert '"--screen-watch-state"' in source
    assert "choices=(3, 5, 7, 9, 20, 23, 27, 29)" in source
    assert "--screen-watch-state requires --screen-watch" in source
    assert "screen_watch_state=args.screen_watch_state" in source
    candidate_env = source[source.index("if candidate:"):source.index("xvfb, display = runtime_env._xvfb")]
    assert 'env["SYW2_G1_SCREEN_WATCH_STATE"] = str(screen_watch_state)' in candidate_env
    # the new-game-path branch hands the drift/watch options to the candidate lane only
    branch = source[source.index("    if args.new_game_path:\n        lanes = {"):]
    branch = branch[: branch.index("passed = all(")]
    for needle in ("layer_drift=args.layer_drift if name == \"candidate\" else False",
                   "screen_watch=args.screen_watch if name == \"candidate\" else False",
                   "screen_watch_state=args.screen_watch_state",
                   "screen_watch_cache=args.screen_watch_cache if name == \"candidate\" else False",
                   "drift_samples=args.drift_samples if name == \"candidate\" else None"):
        assert needle in branch
    summary = source[source.index('"schema": "syw2plus.g1-new-game-path.v1"'):]
    summary = summary[: summary.index("new-game-path-result.json")]
    assert '"screen_watch"' in summary


def test_screen_watch_surface_call_table_names_the_game_side_caller_in_ps23() -> None:
    """H-PM1 PM1-1b: the DR watch only sees wined3d's memcpy thread; the issuing
    ddraw Blt/BltFast (caller EIP, rects, surfaces) is tabled per present range."""
    header = (STUB / "g1_screen_watch.h").read_text(encoding="utf-8")
    source = (STUB / "g1_screen_watch.c").read_text(encoding="utf-8")
    trace = (STUB / "direct_draw_trace.c").read_text(encoding="utf-8")
    assert "g1_screen_watch_on_surface_call(" in header
    assert '#include "g1_screen_watch.h"' in trace
    # cheap early-out when the diagnostic is off or the watched state is not PS23
    call = source[source.index("void g1_screen_watch_on_surface_call("):]
    call = call[: call.index("\n}\n")]
    # H-RS1: the table follows any non-PS3 watched state, only while the game is in that state
    assert "g_sw_state != 2" in call and "g_sw_watch_state == G1_SCREEN_WATCH_STATE_PS3" in call
    assert "!= g_sw_watch_state" in call
    assert "SW_PROGRAM_STATE_VA" in call and "SW_CALL_TABLE" in source
    assert "first_present" in call and "last_present" in call
    # published with the heartbeat as {"t":"q"} rows
    summary = source[source.index("static void sw_summary("):source.index("static BOOL sw_buffer_valid(")]
    assert '\\"t\\":\\"q\\"' in summary and "caller" in summary
    # both hooks report their caller; the game buffer is not touched
    blt = trace[trace.rindex("static HRESULT WINAPI hook_blt(LPDIRECTDRAWSURFACE7 self, LPRECT dst,\n"):]
    blt = blt[: blt.index("\n}\n")]
    assert "g1_screen_watch_on_surface_call(" in blt and "__builtin_return_address(0)" in blt
    fast = trace[trace.rindex("static HRESULT WINAPI hook_blt_fast(LPDIRECTDRAWSURFACE7 self, DWORD x, DWORD y,\n"):]
    fast = fast[: fast.index("present_started_ms = GetTickCount();")]
    assert "g1_screen_watch_on_surface_call(" in fast


def test_probe_title_button_branch_hands_screen_watch_options_to_the_candidate_lane() -> None:
    """H-TM1 TM1-0: --title-button user can run the PS9 write watch on the candidate lane only."""
    source = (ROOT / "tools/g1_saved_scene_probe.py").read_text(encoding="utf-8")
    branch = source[source.index("    if args.title_button:\n        lanes = {"):]
    branch = branch[: branch.index("windows = {name:")]
    for needle in ("layer_drift=args.layer_drift if name == \"candidate\" else False",
                   "screen_watch=args.screen_watch if name == \"candidate\" else False",
                   "screen_watch_state=args.screen_watch_state",
                   "screen_watch_cache=args.screen_watch_cache if name == \"candidate\" else False",
                   "drift_samples=args.drift_samples if name == \"candidate\" else None"):
        assert needle in branch
    summary = source[source.index('"schema": "syw2plus.g1-title-button.v1"'):]
    summary = summary[: summary.index("title-button-result.json")]
    assert '"screen_watch"' in summary and '"layer_drift"' in summary


def test_probe_title_button_branch_hands_stale_mask_options_to_the_candidate_lane() -> None:
    """H-SC1 SC1-0: --title-button scenario can dump PS20 stale masks from the candidate lane only."""
    source = (ROOT / "tools/g1_saved_scene_probe.py").read_text(encoding="utf-8")
    branch = source[source.index("    if args.title_button:\n        lanes = {"):]
    branch = branch[: branch.index("windows = {name:")]
    assert "stale_mask=args.stale_mask if name == \"candidate\" else None" in branch
    assert "stale_mask_state=args.stale_mask_state" in branch
    summary = source[source.index('"schema": "syw2plus.g1-title-button.v1"'):]
    summary = summary[: summary.index("title-button-result.json")]
    assert '"stale_mask"' in summary


def test_probe_new_game_path_branch_hands_stale_mask_options_to_the_candidate_lane() -> None:
    """H-PS5W0 W0-0: --new-game-path used to drop --stale-mask, so the lap1210 runs wrote no mask dump."""
    source = (ROOT / "tools/g1_saved_scene_probe.py").read_text(encoding="utf-8")
    branch = source[source.index("    if args.new_game_path:\n        lanes = {"):]
    branch = branch[: branch.index("passed = all(")]
    assert "stale_mask=args.stale_mask if name == \"candidate\" else None" in branch
    assert "stale_mask_state=args.stale_mask_state" in branch


def test_screen_watch_call_from_parse_and_gate(tmp_path: Path) -> None:
    """H-SC1 SC1-2: SYW2_G1_SCREEN_WATCH_CALL_FROM=<present> skips ddraw call-table rows before that watch present."""
    fixture = tmp_path / "screen_watch_call_from.c"
    executable = tmp_path / "screen_watch_call_from"
    fixture.write_text(
        r'''#include <assert.h>
#include "g1_screen_watch.h"

int main(void) {
    assert(g1_screen_watch_call_from_parse("2800", 4ul) == 2800ul);
    assert(g1_screen_watch_call_from_parse("0", 1ul) == 0ul);
    assert(g1_screen_watch_call_from_parse("99999", 5ul) == 99999ul);
    assert(g1_screen_watch_call_from_parse("", 0ul) == 0ul);
    assert(g1_screen_watch_call_from_parse("123456", 6ul) == 0ul);
    assert(g1_screen_watch_call_from_parse("28x0", 4ul) == 0ul);
    assert(g1_screen_watch_call_from_parse("-5", 2ul) == 0ul);
    return 0;
}
''',
        encoding="utf-8",
    )
    subprocess.run(["cc", "-I", str(STUB), str(fixture), "-o", str(executable)], check=True)
    subprocess.run([str(executable)], check=True)
    source = (STUB / "g1_screen_watch.c").read_text(encoding="utf-8")
    assert '#define G1_SCREEN_WATCH_CALL_FROM_ENV "SYW2_G1_SCREEN_WATCH_CALL_FROM"' in source
    call = source[source.index("void g1_screen_watch_on_surface_call("):]
    call = call[: call.index("\n}\n")]
    assert "present < g_sw_call_from" in call


def test_probe_screen_watch_call_from_option_wiring() -> None:
    source = (ROOT / "tools/g1_saved_scene_probe.py").read_text(encoding="utf-8")
    assert '"--screen-watch-call-from"' in source
    assert "--screen-watch-call-from requires --screen-watch" in source
    candidate_env = source[source.index("if candidate:"):source.index("xvfb, display = runtime_env._xvfb")]
    assert 'env["SYW2_G1_SCREEN_WATCH_CALL_FROM"] = str(screen_watch_call_from)' in candidate_env
    branch = source[source.index("    if args.title_button:\n        lanes = {"):]
    branch = branch[: branch.index("windows = {name:")]
    assert "screen_watch_call_from=args.screen_watch_call_from" in branch
