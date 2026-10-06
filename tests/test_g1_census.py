"""Static contracts for the opt-in W70 writer census."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CENSUS = ROOT / "tools/inmm_stub/g1_census.c"
HEADER = ROOT / "tools/inmm_stub/g1_census.h"
MAKEFILE = ROOT / "tools/inmm_stub/Makefile"


def test_census_is_opt_in_measurement_only_and_separate_from_mirror() -> None:
    source = CENSUS.read_text(encoding="utf-8")
    assert '#define CENSUS_ENV "SYW2_G1_CENSUS"' in source
    assert '#define CENSUS_PATH "C:\\\\inmm_g1_census.jsonl"' in source
    assert '#define CENSUS_MAP_PATH "C:\\\\inmm_g1_census_map.bin"' in source
    assert '#define CENSUS_CONTEXT_MAP_PATH "C:\\\\inmm_g1_census_context_map.bin"' in source
    assert "#define CENSUS_SURFACE_LIMIT 256u" in source
    assert '"event\\\":\\\"present_boundary' in source
    assert '"event\\\":\\\"dest_probe' in source
    assert 'SYW2_G1_DEST_PROBE' in source
    assert '\\"measurement_only\\":1' in source
    assert '\\"dest_read\\":\\"unknown\\"' in source
    assert "VirtualAlloc" in source and "VirtualProtect" in source
    assert "g1_census_detach" in HEADER.read_text(encoding="utf-8")
    assert "g1_census.c" in MAKEFILE.read_text(encoding="utf-8")


def test_census_pins_all_p1_targets_and_uses_arity_specific_wrappers() -> None:
    source = CENSUS.read_text(encoding="utf-8")
    for address in ("00466D50", "004664D0", "00465E80", "00466280",
                    "00465B30", "00466540", "00466EA0", "004658E0"):
        assert f"0x{address}u" in source
    assert "CensusFn3" in source
    assert "CensusFn5" in source
    assert "CensusFn6" in source
    assert "CensusFn7" in source
    assert "census_rle_tinted_clip" in source
    assert "census_set_pixel" in source
    assert '"set_pixel", 0x004658E0u, 9u' in source


def test_census_attribution_persists_across_present_boundaries() -> None:
    source = CENSUS.read_text(encoding="utf-8")
    assert "Preserve the map" in source
    assert "semantic_write" in source
    assert "target->address == 0x00466280u" in source
    assert "e == 0x00BA3D30u" in source
    assert '"terrain_cache_transfer"' in source
    assert "CENSUS_WRITER_COUNT 10u" in source
    assert "state != g_census_target_state" in source
    assert "writer_pixels[8]" in source
    assert "terrain_cache_transfer_calls" in source
    assert "terrain_cache_transfer_summary" in source
    assert '"terrain_context", 0x00403B20u' in source
    assert "terrain_0x403B20" in source
    assert "writer_context" in source
    assert "context_map" in source
    assert "g1_census_present_boundary" in HEADER.read_text(encoding="utf-8")
    assert "g1_census_generation_changed" in source
    assert "context->map[index] = 0u;" in source
    assert "g1_census_surface_blt_begin" in source
    assert "g1_census_surface_blt_end" in source


def test_runtime_cli_exposes_census_opt_in() -> None:
    source = (ROOT / "tools/runtime_env.py").read_text(encoding="utf-8")
    assert "g1_census: bool = False" in source
    assert 't.add_argument("--g1-census", action="store_true")' in source
    assert "g1_census=args.g1_census" in source
    probe_source = (ROOT / "tools/g1_saved_scene_probe.py").read_text(encoding="utf-8")
    assert "census_context_map.bin" in probe_source
    assert "_validate_census_lane(census, census_state=args.census_state)" in probe_source
    assert "cannot be combined with --hd-source" in probe_source


def test_census_validation_requires_active_pins_and_ps3_maps(tmp_path: Path) -> None:
    import json
    import struct

    from tools.g1_saved_scene_probe import _validate_census_lane

    names = ("terrain_context", "rle_clip", "rle_plain", "rect_fill", "block_copy",
             "rect_border", "rle_tinted_clip", "rle_tinted", "set_pixel")
    rows = [
        {"event": "install", "writer": name, "status": "active"} for name in names
    ]
    rows.extend({"event": "writer_category", "id": index, "writer": writer}
                for index, writer in enumerate(("rle_clip", "rle_plain", "rect_fill",
                    "block_copy", "rect_border", "rle_tinted_clip", "rle_tinted",
                    "set_pixel", "terrain_cache_transfer", "dd_surface_blt"), start=1))
    rows.append({"event": "present_boundary", "present": 1, "program_state": 3,
                 "binding": "locked_source", "present_source_buffer": "0xB000",
                 "present_source_pitch": 832, "selected_buffer": "0xB000",
                 "map_generation_state": 3, "map_write_calls": 1,
                 "map_offset": 0, "map_bytes": 480000,
                 "context_map_offset": 0, "context_map_bytes": 480000})
    rows.append({"event": "buffer_context_summary", "buffer_context_dropped": 0})
    rows.append({"event": "surface_blt_summary", "writer": "dd_surface_blt",
                 "calls_ps3": 0, "captured": 0, "capture_missed": 0})
    raw_path = tmp_path / "census.jsonl"
    raw_path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
    binary = struct.pack("<8I", 0x50314731, 1, 800, 600, 832, 0xB000, 480000, 3) + bytes(480000)
    map_path = tmp_path / "map.bin"
    context_path = tmp_path / "context.bin"
    map_path.write_bytes(binary)
    context_path.write_bytes(binary)
    lane = {"census": {"path": str(raw_path)}, "census_map": {"path": str(map_path)},
            "census_context_map": {"path": str(context_path)}}
    assert _validate_census_lane(lane)["status"] == "PASS"

    rows[-3]["program_state"] = 9
    raw_path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
    assert _validate_census_lane(lane)["checks"]["ps3_present_window"] is False


def test_census_present_binding_and_generation_contract_with_host_gcc(tmp_path: Path) -> None:
    import subprocess

    helper = ROOT / "tools/inmm_stub/g1_census_contract.h"
    fixture = tmp_path / "census_contract.c"
    executable = tmp_path / "census_contract"
    fixture.write_text(
        r'''#include <assert.h>
#include "g1_census_contract.h"
int main(void) {
    G1CensusBufferKey buffers[] = {{0xA000u, 832u}, {0xB000u, 832u}};
    unsigned long generation = 1u;
    /* A's larger coverage must not override the present source B. */
    assert(g1_census_find_source_buffer(buffers, 2u, 0xB000u, 832u) == 1);
    assert(g1_census_find_source_buffer(buffers, 2u, 0xDEADBEEFu, 832u) == -1);
    assert(g1_census_find_source_buffer(buffers, 2u, 0xB000u, 800u) == -1);
    assert(g1_census_buffer_key_matches(0xB000u, 832u, 0xB000u, 832u));
    assert(!g1_census_buffer_key_matches(0xB000u, 800u, 0xB000u, 832u));
    assert(!g1_census_generation_changed(9u, 9u, &generation));
    assert(generation == 1u);
    assert(g1_census_generation_changed(9u, 3u, &generation));
    assert(generation == 2u);
    return 0;
}
''',
        encoding="utf-8",
    )
    result = subprocess.run(
        ["gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-I", str(helper.parent),
         str(fixture), "-o", str(executable)],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    run = subprocess.run([str(executable)], capture_output=True, text=True, check=False)
    assert run.returncode == 0, run.stderr


def test_census_gate_binds_json_present_to_binary_map_header(tmp_path: Path) -> None:
    import json
    import struct

    from tools.g1_saved_scene_probe import _validate_census_lane

    names = ("terrain_context", "rle_clip", "rle_plain", "rect_fill", "block_copy",
             "rect_border", "rle_tinted_clip", "rle_tinted", "set_pixel")
    rows = [{"event": "install", "writer": name, "status": "active"} for name in names]
    rows.extend({"event": "writer_category", "id": index, "writer": writer}
                for index, writer in enumerate(("rle_clip", "rle_plain", "rect_fill",
                    "block_copy", "rect_border", "rle_tinted_clip", "rle_tinted",
                    "set_pixel", "terrain_cache_transfer", "dd_surface_blt"), start=1))
    rows.append({"event": "present_boundary", "present": 1, "program_state": 3,
                 "binding": "locked_source", "present_source_buffer": "0xB000",
                 "present_source_pitch": 832, "selected_buffer": "0xB000",
                 "map_generation_state": 3, "map_write_calls": 1,
                 "map_offset": 0, "map_bytes": 480000,
                 "context_map_offset": 0, "context_map_bytes": 480000})
    rows.append({"event": "buffer_context_summary", "buffer_context_dropped": 0})
    rows.append({"event": "surface_blt_summary", "writer": "dd_surface_blt",
                 "calls_ps3": 0, "captured": 0, "capture_missed": 0})
    header = struct.pack("<8I", 0x50314731, 1, 800, 600, 832, 0xB000, 480000, 3)
    raw = tmp_path / "raw.jsonl"
    raw.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
    maps = tmp_path / "maps.bin"
    contexts = tmp_path / "contexts.bin"
    maps.write_bytes(header + bytes(480000))
    contexts.write_bytes(header + bytes(480000))
    lane = {"census": {"path": str(raw)}, "census_map": {"path": str(maps)},
            "census_context_map": {"path": str(contexts)}}
    assert _validate_census_lane(lane)["status"] == "PASS"

    # JSON claims one selected surface while both binary files identify another.
    valid_header = (0x50314731, 1, 800, 600, 832, 0xB000, 480000, 3)
    for field_index, bad_value in ((1, 2), (4, 800), (5, 0xA000), (7, 9)):
        mutated = list(valid_header)
        mutated[field_index] = bad_value
        maps.write_bytes(struct.pack("<8I", *mutated) + bytes(480000))
        assert _validate_census_lane(lane)["checks"]["writer_map_headers_match"] is False
        maps.write_bytes(header + bytes(480000))
        contexts.write_bytes(struct.pack("<8I", *mutated) + bytes(480000))
        assert _validate_census_lane(lane)["checks"]["writer_map_headers_match"] is False
        contexts.write_bytes(header + bytes(480000))
    maps.write_bytes(header + bytes(480000))
    rows[-3]["selected_buffer"] = "0xA000"
    raw.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
    assert _validate_census_lane(lane)["checks"]["census_present_binding"] is False


def _function_body(source: str, signature: str) -> str:
    start = source.index(signature)
    brace = source.index("{", start)
    depth = 0
    for index in range(brace, len(source)):
        depth += {"{": 1, "}": -1}.get(source[index], 0)
        if depth == 0:
            return source[brace:index + 1]
    raise AssertionError(f"unterminated body for {signature}")


def test_present_boundary_serializes_surface_pointer_not_backing_buffer() -> None:
    source = CENSUS.read_text(encoding="utf-8")
    header = HEADER.read_text(encoding="utf-8")
    emit = _function_body(source, "static void emit_present_boundary(")
    assert "DWORD source_surface" in source[source.index("static void emit_present_boundary("):
                                            source.index("static void emit_present_boundary(") + 400]
    assert "DWORD source_surface" in header
    assert "(unsigned)(source_locked ? source_surface : 0u),\n" \
           "        (unsigned)(source_locked ? source_buffer : 0u),\n" \
           "        (unsigned)(source_locked ? source_pitch : 0u)," in emit
    caller = (ROOT / "tools/inmm_stub/direct_draw_trace.c").read_text(encoding="utf-8")
    call = caller[caller.index("g1_census_present_boundary("):]
    call = call[:call.index(");") + 2]
    assert "(DWORD)(ULONG_PTR)source" in call


def test_surface_blt_captured_counts_completed_captures_only() -> None:
    source = CENSUS.read_text(encoding="utf-8")
    begin = _function_body(source, "BOOL g1_census_surface_blt_begin(")
    end = _function_body(source, "void g1_census_surface_blt_end(")
    assert "++g_surface_blt_captured" not in begin
    assert end.count("++g_surface_blt_captured") == 1
    # Counted only after the post-Blt comparison loop, never on an early return.
    assert end.index("++g_surface_blt_captured") > end.index("for (row = 0;")


def test_census_target_state_defaults_to_ps3_and_env_selects_another() -> None:
    import subprocess
    import tempfile

    helper = ROOT / "tools/inmm_stub/g1_census_contract.h"
    with tempfile.TemporaryDirectory() as directory:
        fixture = Path(directory) / "target_state.c"
        executable = Path(directory) / "target_state"
        fixture.write_text(
            r'''#include <assert.h>
#include "g1_census_contract.h"
int main(void) {
    assert(g1_census_parse_target_state(0, 0u) == 3u);      /* unset -> PS3 */
    assert(g1_census_parse_target_state("", 0u) == 3u);
    assert(g1_census_parse_target_state("9", 1u) == 9u);
    assert(g1_census_parse_target_state("35", 2u) == 35u);
    assert(g1_census_parse_target_state("3", 1u) == 3u);
    assert(g1_census_parse_target_state("x", 1u) == 3u);    /* invalid -> PS3 */
    assert(g1_census_parse_target_state("9x", 2u) == 3u);
    assert(g1_census_parse_target_state("123", 3u) == 3u);  /* too long */
    return 0;
}
''',
            encoding="utf-8",
        )
        build = subprocess.run(
            ["gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-Wno-unused-function", "-I", str(helper.parent),
             str(fixture), "-o", str(executable)],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        assert build.returncode == 0, build.stderr
        run = subprocess.run([str(executable)], capture_output=True, text=True, check=False)
        assert run.returncode == 0, run.stderr


def test_census_state_gates_use_selectable_state_not_literal_ps3() -> None:
    source = CENSUS.read_text(encoding="utf-8")
    assert "SYW2_G1_CENSUS_STATE" in source
    assert "g1_census_parse_target_state" in source
    assert "census_program_state() == 3u" not in source
    assert "census_program_state() != 3u" not in source
    assert "state != 3u" not in source
    assert '\\"program_state\\":3,' not in source
    assert '\\"census_state\\":%u' in source
    assert "unknown_index_top" in source
    assert "g1_census_target_state" in HEADER.read_text(encoding="utf-8")
    caller = (ROOT / "tools/inmm_stub/direct_draw_trace.c").read_text(encoding="utf-8")
    assert "g1_census_target_state()" in caller
    assert "census_descriptor_probe && read_state(0x004ED818u) == 3u" not in caller
    assert "g1_census_enabled() && read_state(0x004ED818u) == 3u" not in caller


def test_census_index_top_reports_four_largest_unknown_indices(tmp_path: Path) -> None:
    import subprocess

    helper = ROOT / "tools/inmm_stub/g1_census_contract.h"
    fixture = tmp_path / "index_top.c"
    executable = tmp_path / "index_top"
    fixture.write_text(
        r'''#include <assert.h>
#include "g1_census_contract.h"
int main(void) {
    unsigned long hist[256] = {0};
    G1CensusIndexCount top[4];
    hist[7] = 100u; hist[0] = 100u; hist[200] = 5u; hist[3] = 50u; hist[9] = 1u;
    g1_census_index_top(hist, top);
    assert(top[0].index == 0u && top[0].count == 100u);   /* tie -> lower index */
    assert(top[1].index == 7u && top[1].count == 100u);
    assert(top[2].index == 3u && top[2].count == 50u);
    assert(top[3].index == 200u && top[3].count == 5u);
    hist[7] = hist[0] = hist[3] = hist[200] = 0u;
    g1_census_index_top(hist, top);
    assert(top[0].index == 9u && top[0].count == 1u);
    assert(top[1].count == 0u && top[2].count == 0u && top[3].count == 0u);
    return 0;
}
''',
        encoding="utf-8",
    )
    build = subprocess.run(
        ["gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-Wno-unused-function", "-I", str(helper.parent),
         str(fixture), "-o", str(executable)],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert build.returncode == 0, build.stderr
    run = subprocess.run([str(executable)], capture_output=True, text=True, check=False)
    assert run.returncode == 0, run.stderr


def _ps9_census_fixture(tmp_path: Path, state: int):
    import json
    import struct

    names = ("terrain_context", "rle_clip", "rle_plain", "rect_fill", "block_copy",
             "rect_border", "rle_tinted_clip", "rle_tinted", "set_pixel")
    rows = [{"event": "install", "writer": name, "status": "active"} for name in names]
    rows.extend({"event": "writer_category", "id": index, "writer": writer}
                for index, writer in enumerate(("rle_clip", "rle_plain", "rect_fill",
                    "block_copy", "rect_border", "rle_tinted_clip", "rle_tinted",
                    "set_pixel", "terrain_cache_transfer", "dd_surface_blt"), start=1))
    rows.append({"event": "present_boundary", "present": 1, "program_state": state,
                 "census_state": state, "binding": "locked_source",
                 "present_source_buffer": "0xB000", "present_source_pitch": 832,
                 "selected_buffer": "0xB000", "map_generation_state": state,
                 "map_write_calls": 1, "map_offset": 0, "map_bytes": 480000,
                 "context_map_offset": 0, "context_map_bytes": 480000})
    rows.append({"event": "buffer_context_summary", "buffer_context_dropped": 0})
    rows.append({"event": "surface_blt_summary", "writer": "dd_surface_blt",
                 "calls_ps3": 0, "captured": 0, "capture_missed": 0})
    header = struct.pack("<8I", 0x50314731, 1, 800, 600, 832, 0xB000, 480000, state)
    raw = tmp_path / "raw.jsonl"
    raw.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
    maps = tmp_path / "maps.bin"
    contexts = tmp_path / "contexts.bin"
    maps.write_bytes(header + bytes(480000))
    contexts.write_bytes(header + bytes(480000))
    return {"census": {"path": str(raw)}, "census_map": {"path": str(maps)},
            "census_context_map": {"path": str(contexts)}}


def test_census_validation_accepts_selected_state_and_rejects_mismatch(tmp_path: Path) -> None:
    from tools.g1_saved_scene_probe import _validate_census_lane

    lane = _ps9_census_fixture(tmp_path, 9)
    assert _validate_census_lane(lane, census_state=9)["status"] == "PASS"
    # The default stays PS3: a PS9 capture must not be accepted as the PS3 census.
    assert _validate_census_lane(lane)["status"] == "FAIL"
    assert _validate_census_lane(lane, census_state=3)["checks"]["ps3_present_window"] is False


def test_probe_exposes_census_state_option_and_passes_env() -> None:
    source = (ROOT / "tools/g1_saved_scene_probe.py").read_text(encoding="utf-8")
    assert '"--census-state"' in source
    assert 'env["SYW2_G1_CENSUS_STATE"] = str(census_state)' in source
    assert "census_state=args.census_state" in source
    assert "_validate_census_lane(census, census_state=args.census_state)" in source


def test_residual_shadow_compare_counts_only_post_hook_changes_with_host_gcc(tmp_path: Path) -> None:
    import subprocess

    helper = ROOT / "tools/inmm_stub/g1_census_residual.h"
    fixture = tmp_path / "residual.c"
    executable = tmp_path / "residual"
    fixture.write_text(
        r'''#include <assert.h>
#include <string.h>
#include "g1_census_contract.h"
#include "g1_census_residual.h"
static unsigned char buffer[600u * 832u];
static unsigned char shadow[800u * 600u];
static unsigned char mask[800u * 600u];
int main(void) {
    G1CensusResidual r;
    unsigned i;
    for (i = 0; i < sizeof(buffer); ++i) buffer[i] = (unsigned char)(i * 7u);
    /* init: shadow = buffer contents, so nothing is unhooked */
    assert(g1_census_residual_sync(shadow, buffer, 832u, 0u, 0u, 800u, 600u) == 1);
    memset(mask, 0, sizeof(mask));
    g1_census_residual_compare(shadow, buffer, 832u, &r, mask);
    assert(r.pixels == 0u && r.min_x == -1 && r.max_y == -1);
    /* a write outside any hook: 3x2 block at (10,20) set to index 5 */
    for (i = 0; i < 3u; ++i) { buffer[20u * 832u + 10u + i] = 5u; buffer[21u * 832u + 10u + i] = 5u; }
    /* pitch padding changes are not screen pixels */
    buffer[20u * 832u + 805u] ^= 0xFFu;
    memset(mask, 0, sizeof(mask));
    g1_census_residual_compare(shadow, buffer, 832u, &r, mask);
    assert(r.pixels == 6u);
    assert(r.min_x == 10 && r.min_y == 20 && r.max_x == 12 && r.max_y == 21);
    assert(r.histogram[5] == 6u);
    assert(mask[20u * 800u + 10u] == 1u && mask[21u * 800u + 12u] == 1u && mask[0] == 0u);
    /* a hook result for the 2x2 sub-rectangle at (10,20) syncs shadow, leaving 2 pixels */
    assert(g1_census_residual_sync(shadow, buffer, 832u, 10u, 20u, 2u, 2u) == 1);
    memset(mask, 0, sizeof(mask));
    g1_census_residual_compare(shadow, buffer, 832u, &r, mask);
    assert(r.pixels == 2u && r.min_x == 12 && r.max_x == 12 && r.min_y == 20 && r.max_y == 21);
    /* rejects out-of-range rectangles and short pitch without touching shadow */
    assert(g1_census_residual_sync(shadow, buffer, 832u, 700u, 0u, 101u, 1u) == 0);
    assert(g1_census_residual_sync(shadow, buffer, 832u, 0u, 599u, 1u, 2u) == 0);
    assert(g1_census_residual_sync(shadow, buffer, 799u, 0u, 0u, 1u, 1u) == 0);
    /* the compare's top-4 index summary reuses the contract helper */
    {
        G1CensusIndexCount top[4];
        g1_census_index_top(r.histogram, top);
        assert(top[0].index == 5u && top[0].count == 2u);
    }
    return 0;
}
''',
        encoding="utf-8",
    )
    build = subprocess.run(
        ["gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-Wno-unused-function", "-I", str(helper.parent),
         str(fixture), "-o", str(executable)],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert build.returncode == 0, build.stderr
    run = subprocess.run([str(executable)], capture_output=True, text=True, check=False)
    assert run.returncode == 0, run.stderr


def test_residual_is_opt_in_and_leaves_default_census_output_unchanged() -> None:
    source = CENSUS.read_text(encoding="utf-8")
    assert '"SYW2_G1_CENSUS_RESIDUAL"' in source
    assert "g1_census_residual.h" in source
    assert '#define CENSUS_RESIDUAL_MAP_PATH "C:\\\\inmm_g1_census_residual_map.bin"' in source
    assert '"event\\":\\"residual_boundary' in source
    assert '\\"unhooked_pixels\\"' in source and '\\"unhooked_index_top\\"' in source
    # every residual path is gated by the opt-in flag so default raw/map output is untouched
    assert source.count("g_residual_enabled") >= 5
    assert "if (g_residual_enabled && selected" in source
    assert "residual_sync_context(context, x, y, width, height)" in source
    assert "residual_sync_context(context, g_surface_blt_left" in source


def test_probe_exposes_census_residual_option_and_collects_residual_map() -> None:
    source = (ROOT / "tools/g1_saved_scene_probe.py").read_text(encoding="utf-8")
    assert '"--census-residual"' in source
    assert 'env["SYW2_G1_CENSUS_RESIDUAL"] = "1"' in source
    assert "inmm_g1_census_residual_map.bin" in source
    assert "census_residual_map" in source
    assert "--census-residual requires --census-only" in source


def test_residual_textout_iat_is_opt_in_pinned_and_restored() -> None:
    source = CENSUS.read_text(encoding="utf-8")
    assert "#define CENSUS_TEXTOUT_SLOT 0x004E502Cu" in source
    # old value must equal gdi32!TextOutA before the slot is replaced, and the slot is put back
    assert 'GetProcAddress(gdi, "TextOutA")' in source
    assert "*slot == (DWORD)(ULONG_PTR)real" in source
    assert "*slot == (DWORD)(ULONG_PTR)census_textout" in source
    assert "*slot = (DWORD)(ULONG_PTR)g_real_textout;" in source
    assert "if (g_residual_enabled) install_textout_slot();" in source
    assert "restore_textout_slot();" in source
    # the real function runs first so the original drawing is unchanged
    assert source.index("g_real_textout(hdc, x, y, text, length)") < source.index('"event\\":\\"textout_call')
    # no gdi32 link dependency is added for the opt-in measurement
    assert "gdi32" not in MAKEFILE.read_text(encoding="utf-8")
    assert '\\"textout_calls\\"' in source


def test_residual_mode_counts_non_screen_blt_apart_and_default_counts_every_blt() -> None:
    source = CENSUS.read_text(encoding="utf-8")
    header = HEADER.read_text(encoding="utf-8")
    assert "g1_census_surface_blt_attempt(DWORD destination_width, DWORD destination_height)" in header
    start = source.index("void g1_census_surface_blt_attempt(")
    body = source[start:source.index("void g1_census_surface_blt_skipped(")]
    # the exclusion only exists behind the residual opt-in, so the default census still counts every Blt
    assert "if (g_residual_enabled &&" in body
    assert "destination_width < CENSUS_MAP_WIDTH || destination_height < CENSUS_MAP_HEIGHT" in body
    assert body.index("g_residual_enabled") < body.index("++g_surface_blt_attempts")
    caller = (ROOT / "tools/inmm_stub/direct_draw_trace.c").read_text(encoding="utf-8")
    assert "g1_census_surface_blt_attempt(record->width, record->height);" in caller
    assert "g1_census_surface_blt_attempt(destination_width, destination_height);" in caller
    assert '\\"non_screen_surface_blt\\"' in source


def test_watch_helper_parses_pixel_and_builds_write_watch_with_host_gcc(tmp_path: Path) -> None:
    import subprocess

    helper = ROOT / "tools/inmm_stub/g1_census_watch.h"
    fixture = tmp_path / "watch.c"
    executable = tmp_path / "watch"
    fixture.write_text(
        r'''#include <assert.h>
#include "g1_census_watch.h"
int main(void) {
    unsigned x = 0u, y = 0u;
    assert(g1_census_watch_parse("782,380", 7u, &x, &y) == 1 && x == 782u && y == 380u);
    assert(g1_census_watch_parse("0,0", 3u, &x, &y) == 1 && x == 0u && y == 0u);
    assert(g1_census_watch_parse("799,599", 7u, &x, &y) == 1 && x == 799u && y == 599u);
    /* out of the 800x600 screen, malformed, empty and too long values are rejected */
    assert(g1_census_watch_parse("800,0", 5u, &x, &y) == 0);
    assert(g1_census_watch_parse("0,600", 5u, &x, &y) == 0);
    assert(g1_census_watch_parse("782;380", 7u, &x, &y) == 0);
    assert(g1_census_watch_parse("782,", 4u, &x, &y) == 0);
    assert(g1_census_watch_parse(",380", 4u, &x, &y) == 0);
    assert(g1_census_watch_parse("7 82,380", 8u, &x, &y) == 0);
    assert(g1_census_watch_parse("", 0u, &x, &y) == 0);
    assert(g1_census_watch_parse("1234567890,1", 12u, &x, &y) == 0);
    assert(g1_census_watch_pixel_address(0x233C7B0ul, 832ul, 782u, 380u) ==
           0x233C7B0ul + 380ul * 832ul + 782ul);
    /* DR7: local enable slot 0, break on data writes (RW0=01), 1-byte length (LEN0=00) */
    assert(G1_CENSUS_WATCH_DR7 == 0x00010001ul);
    /* lap1014 H-S2w: the 1x terrain cache (0xBA3D30, pitch 832) is watched instead of the screen */
    assert(G1_CENSUS_WATCH_CACHE_BASE == 0x00BA3D30ul && G1_CENSUS_WATCH_CACHE_PITCH == 832ul);
    assert(g1_census_watch_cache_address(112u, 126u) == 0x00BBD720ul);
    assert(g1_census_watch_cache_address(437u, 463u) == 0x00C01FA5ul);
    assert(g1_census_watch_cache_address(302u, 9u) == 0x00BA5B9Eul);
    assert(g1_census_watch_is_exe_text(0x00401000ul) == 1);
    assert(g1_census_watch_is_exe_text(0x004E4AE5ul) == 1);
    assert(g1_census_watch_is_exe_text(0x004E4AE6ul) == 0);
    assert(g1_census_watch_is_exe_text(0x00400FFFul) == 0);
    assert(g1_census_watch_is_exe_text(0x7B000000ul) == 0);
    return 0;
}
''',
        encoding="utf-8",
    )
    build = subprocess.run(
        ["gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-Wno-unused-function", "-I", str(helper.parent),
         str(fixture), "-o", str(executable)],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert build.returncode == 0, build.stderr
    run = subprocess.run([str(executable)], capture_output=True, text=True, check=False)
    assert run.returncode == 0, run.stderr


def test_watch_is_opt_in_residual_only_self_tested_and_released() -> None:
    source = CENSUS.read_text(encoding="utf-8")
    assert '"SYW2_G1_CENSUS_WATCH"' in source
    assert '#include "g1_census_watch.h"' in source
    assert "g1_census_watch.h" in MAKEFILE.read_text(encoding="utf-8")
    # armed only when residual mode is on and the value parses; default census never installs it
    assert "g_watch_enabled = g_residual_enabled && " in source
    assert "AddVectoredExceptionHandler(1, census_watch_veh)" in source
    assert "RemoveVectoredExceptionHandler" in source
    # the self test uses a private variable, never the game's buffer
    assert "g_watch_selftest_byte" in source
    # the handler bumps this asynchronously; a non-volatile counter let the compiler cache it (lap953 r1 no_hit)
    assert "static volatile DWORD g_watch_hits_selftest" in source
    assert '\\"event\\":\\"watch_selftest' in source
    assert source.index("watch_selftest(") < source.index("watch_arm_address(g_watch_address)")
    # one record per hit with instruction bytes before EIP, plus a summary and a release
    assert '\\"event\\":\\"watch_hit' in source
    assert '\\"event\\":\\"watch_summary' in source
    assert "g1_census_watch_is_exe_text" in source
    assert "watch_finish(\"detach\")" in source
    assert "watch_apply(0u, 0u)" in source
    assert "CONTEXT_DEBUG_REGISTERS" in source
    assert "G1_CENSUS_WATCH_DR7" in source


def test_probe_exposes_census_watch_option_and_passes_env() -> None:
    source = (ROOT / "tools/g1_saved_scene_probe.py").read_text(encoding="utf-8")
    assert '"--census-watch"' in source
    assert 'env["SYW2_G1_CENSUS_WATCH"] = census_watch' in source
    assert "--census-watch requires --census-residual" in source
    assert "census_watch=args.census_watch" in source


def test_probe_exposes_census_watch_cache_and_presents_options() -> None:
    from tools.g1_saved_scene_probe import _census_watch_wait_timeout

    source = (ROOT / "tools/g1_saved_scene_probe.py").read_text(encoding="utf-8")
    assert '"--census-watch-cache"' in source
    assert '"--census-watch-presents"' in source
    assert 'env["SYW2_G1_CENSUS_WATCH_CACHE"] = "1"' in source
    assert 'env["SYW2_G1_CENSUS_WATCH_PRESENTS"] = str(census_watch_presents)' in source
    assert "--census-watch-cache requires --census-watch" in source
    assert "--census-watch-presents requires --census-watch" in source
    assert "--census-watch-presents must be 0-9999" in source
    assert "census_watch_cache=args.census_watch_cache" in source
    assert "census_watch_presents=args.census_watch_presents" in source
    # the loaded-only wait must outlast the watch window, not only the 64-present census window
    assert "_census_watch_wait_timeout(census_watch_presents)" in source
    assert _census_watch_wait_timeout(0) == 0.0
    assert _census_watch_wait_timeout(700) == 60.0 + 700 / 5.0


def test_watch_cache_and_presents_are_opt_in_watch_only_options() -> None:
    source = CENSUS.read_text(encoding="utf-8")
    # both need an armed watch (residual + parsed pixel) and default to the existing behaviour
    assert '"SYW2_G1_CENSUS_WATCH_CACHE"' in source
    assert '"SYW2_G1_CENSUS_WATCH_PRESENTS"' in source
    assert "g_watch_cache = g_watch_enabled && " in source
    assert "g1_census_watch_cache_address(g_watch_x, g_watch_y)" in source
    assert "g1_census_parse_skip_presents(" in source[source.index("SYW2_G1_CENSUS_WATCH_PRESENTS"):]
    # the watch keeps its own present count (g_present_count stops at CENSUS_PRESENT_LIMIT)
    assert "g_watch_present_ticks" in source
    assert 'watch_finish("watch_window_end")' in source
    # without N the old 64-present window_end stays; with N it must not cut the watch short (lap1014 wa: 0 hits)
    assert "if (!g_watch_presents && g_present_count >= CENSUS_PRESENT_LIMIT)" in source
    assert '\\"watch_present\\":%u' in source
    assert '\\"cache\\":%u' in source
    # measurement only: the census still never writes the game's buffers
    assert "g_watch_selftest_byte" in source


def test_blend_writer_targets_are_pinned_residual_only_and_leave_default_table_alone() -> None:
    source = CENSUS.read_text(encoding="utf-8")
    # lap953 watchpoints: pixel (782,380) was written inside 0x4672E0 (EIP 0x4673D3) and
    # pixel (223,279) inside 0x467580 (EIP 0x467692); both end in `mov [dest], lut[...]`
    assert ('{"rle_blend_4672E0", 0x004672E0u, 6u, {0x51,0x53,0x56,0x8B,0xF1,0x57}, 5u, '
            'NULL, NULL, 0,0,0,0,FALSE}') in source
    assert ('{"rle_blend_467580", 0x00467580u, 6u, {0x51,0x0F,0xBF,0x54,0x24,0x0C}, 5u, '
            'NULL, NULL, 0,0,0,0,FALSE}') in source
    assert "#define CENSUS_BLEND_COUNT 2u" in source
    # default census: eight writer targets, ten categories, no extra install/summary rows
    assert "#define CENSUS_TARGET_COUNT 8u" in source
    assert "#define CENSUS_WRITER_COUNT 10u" in source
    assert "if (g_residual_enabled && !install_blend_targets())" in source
    assert "restore_one(target)" in source
    for event in ("blend_install", "blend_call", "blend_boundary", "blend_summary"):
        assert f'\\"event\\":\\"{event}' in source
    start = source.index("static DWORD call_blend(")
    body = source[start:source.index("static DWORD __attribute__((thiscall)) census_rle_blend_0")]
    # the original blend runs between the before-snapshot and the shadow sync, so the shadow
    # holds the blend result and the pixels leave the unhooked residual
    assert body.index("snapshot_before(") < body.index("result = target_result(") < body.index(
        "residual_sync_context(context, x, y, width, height)")
    assert "InterlockedExchange(&g_guard, 1)" in body
    assert "census_program_state() == g_census_target_state" in body
    # the writers read 16-bit words; raw DWORD args had garbage upper halves and a 223-row bbox
    assert "(DWORD)(int)(short)c, (DWORD)(int)(short)d" in body


def test_census_skip_presents_parse_defaults_to_zero_and_rejects_garbage(tmp_path: Path) -> None:
    import subprocess

    helper = ROOT / "tools/inmm_stub/g1_census_contract.h"
    fixture = tmp_path / "skip_presents.c"
    executable = tmp_path / "skip_presents"
    fixture.write_text(
        r'''#include <assert.h>
#include "g1_census_contract.h"
int main(void) {
    assert(g1_census_parse_skip_presents(0, 0u) == 0u);      /* unset -> no skip */
    assert(g1_census_parse_skip_presents("", 0u) == 0u);
    assert(g1_census_parse_skip_presents("0", 1u) == 0u);
    assert(g1_census_parse_skip_presents("300", 3u) == 300u);
    assert(g1_census_parse_skip_presents("9999", 4u) == 9999u);
    assert(g1_census_parse_skip_presents("12345", 5u) == 0u); /* too long */
    assert(g1_census_parse_skip_presents("30x", 3u) == 0u);   /* invalid -> no skip */
    assert(g1_census_parse_skip_presents("-5", 2u) == 0u);
    return 0;
}
''',
        encoding="utf-8",
    )
    build = subprocess.run(
        ["gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-Wno-unused-function", "-I",
         str(helper.parent), str(fixture), "-o", str(executable)],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert build.returncode == 0, build.stderr
    run = subprocess.run([str(executable)], capture_output=True, text=True, check=False)
    assert run.returncode == 0, run.stderr


def test_census_skip_presents_defers_recording_without_changing_default_window() -> None:
    source = CENSUS.read_text(encoding="utf-8")
    assert "SYW2_G1_CENSUS_SKIP_PRESENTS" in source
    assert "g1_census_parse_skip_presents" in source
    assert "#define CENSUS_PRESENT_LIMIT 64u" in source  # window length is unchanged
    start = source.index("static void emit_present_boundary(")
    body = source[start:source.index("void g1_census_present_boundary(")]
    gate = body.index("g_present_count >= CENSUS_PRESENT_LIMIT) return;")
    skip = body.index("g_skip_presents_seen < g_skip_presents")
    count = body.index("++g_present_count;")
    # skipped presents still advance the real PS3 ordinal but never the 64-present window
    assert gate < skip < count
    skipped = body[skip:count]
    assert "++g_present_sequence" in skipped and "++g_present_count" not in skipped
    assert "return;" in skipped
    # the opt-in is parsed with the other env switches and defaults to 0 (byte-same path)
    assert "static DWORD g_skip_presents = 0u;" in source


def test_probe_cli_exposes_census_skip_presents_requiring_census_only() -> None:
    source = (ROOT / "tools/g1_saved_scene_probe.py").read_text(encoding="utf-8")
    assert '"--census-skip-presents"' in source
    assert "--census-skip-presents requires --census-only" in source
    assert "census_skip_presents=args.census_skip_presents" in source
    assert 'env["SYW2_G1_CENSUS_SKIP_PRESENTS"] = str(census_skip_presents)' in source


def test_probe_rejects_census_skip_presents_without_census_only(tmp_path: Path) -> None:
    import pytest

    from tools.g1_saved_scene_probe import main

    with pytest.raises(SystemExit) as raised:
        main(["--runtime-root", str(tmp_path / "r"), "--artifact-root", str(tmp_path / "a"),
              "--census-skip-presents", "300"])
    assert raised.value.code == 2
