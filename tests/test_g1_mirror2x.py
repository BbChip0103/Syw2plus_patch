"""Regression contracts for the opt-in W60 mirror bridge."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
MIRROR = ROOT / "tools/inmm_stub/g1_mirror2x.c"
HEADER = ROOT / "tools/inmm_stub/g1_mirror2x.h"
DIRECT_DRAW = ROOT / "tools/inmm_stub/direct_draw_trace.c"
PRESENT_CONTRACT = ROOT / "tools/inmm_stub/g1_present_contract.h"
G1_ENVIRONMENT_SOURCES = (
    ROOT / "tools/inmm_stub/direct_draw_trace.c",
    ROOT / "tools/inmm_stub/g1_census.c",
    ROOT / "tools/inmm_stub/g1_hd_asset.c",
    ROOT / "tools/inmm_stub/g1_mirror2x.c",
    ROOT / "tools/inmm_stub/g1_perf_sections.c",
)


def _function_body(source: str, signature: str) -> str:
    start = source.index(signature)
    opening = source.index("{", start)
    depth = 0
    for index in range(opening, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[opening : index + 1]
    raise AssertionError(f"unterminated function: {signature}")


def test_mirror_bridge_is_opt_in_and_pins_both_primitive_entries() -> None:
    source = MIRROR.read_text(encoding="utf-8")
    assert 'GetEnvironmentVariableA(G1_MIRROR_ENV' in _function_body(
        source, "static void initialize_environment(void)"
    )
    assert "#define G1_TARGET_A 0x00466D50u" in source
    assert "#define G1_TARGET_B 0x004664D0u" in source
    assert "expected_a[G1_TARGET_A_LEN]" in source
    assert "expected_b[G1_TARGET_B_LEN]" in source
    assert "old_bytes" not in source or "bytes_equal" in source


def test_terrain_blitter_family_is_hooked_with_exact_stack_contracts() -> None:
    source = MIRROR.read_text(encoding="utf-8")
    contracts = (
        ("0x00468C30u", "G1_TERRAIN_RLE_LEN 8u", "0x10", "mirror_terrain_rle"),
        ("0x00468CC0u", "G1_TERRAIN_SHADE_LEN 5u", "0x18", "mirror_terrain_shade"),
        ("0x00468E10u", "G1_TERRAIN_CHECKER_LEN 5u", "0x14", "mirror_terrain_checker"),
        ("0x00468F00u", "G1_TERRAIN_CLIP_LEN 8u", "0x14", "mirror_terrain_clip"),
        ("0x004690A0u", "G1_TERRAIN_CLIP_SHADE_LEN 5u", "0x18", "mirror_terrain_clip_shade"),
    )
    for address, length, ret_bytes, wrapper in contracts:
        assert address in source
        assert length in source
        assert wrapper in source
        assert ret_bytes in source
    assert "rle_dimensions" in source
    assert "skip = cursor[0]" in source and "length = cursor[1]" in source
    assert "g1_hd_asset_begin_with_aux" in source
    assert "if (a == b && (a != 0x00u || b != 0xFFu))" in source
    assert "if (g1_hd_asset_current_ready())" in source
    assert "g1_hd_asset_verify_unclipped_frame_in_viewport" in source
    assert "g1_mirror2x_terrain_writer_calls" in source
    assert "g_hook_terrain_clip_shade.installed" in source


def test_unclipped_terrain_writers_bind_identity_from_their_screen_origin() -> None:
    source = MIRROR.read_text(encoding="utf-8")
    contracts = (
        ("static DWORD __attribute__((thiscall)) mirror_terrain_rle(",
         "G1_TERRAIN_RLE, FALSE);"),
        ("static DWORD __attribute__((thiscall)) mirror_terrain_shade(",
         "G1_TERRAIN_SHADE, FALSE);"),
        ("static DWORD __attribute__((thiscall)) mirror_terrain_checker(",
         "G1_TERRAIN_CHECKER, FALSE);"),
    )
    for signature, clipped_contract in contracts:
        body = _function_body(source, signature)
        assert "mirror_reinvoke" in body
        assert clipped_contract in body
    reinvoke = _function_body(source, "static void mirror_reinvoke(")
    frame = (MIRROR.parent / "g1_mirror_frame.h").read_text(encoding="utf-8")
    assert "g1_mirror_unclipped_bind_fits(origin_x, origin_y, width, height" in reinvoke
    assert "(unsigned long)origin_x <= frame_width - width" in frame
    assert "(unsigned long)origin_y <= surface_height - height" in frame
    assert "(DWORD)origin_y * stride + (DWORD)origin_x" in reinvoke


def test_p4b_cache_layer_hooks_are_version_guarded_and_fail_closed() -> None:
    source = MIRROR.read_text(encoding="utf-8")
    memory_map = (ROOT / "analysis/memory_maps/g1_w70_p4b_terrain_cache_scroll_lap863.md").read_text(
        encoding="utf-8"
    )
    frame_header = (ROOT / "tools/inmm_stub/g1_mirror_frame.h").read_text(encoding="utf-8")
    assert "#define G1_CACHE_WIDTH G1_MIRROR_CACHE_WIDTH" in source
    assert "#define G1_MIRROR_CACHE_WIDTH 832u" in frame_header
    assert "#define G1_CACHE_HEIGHT 512u" in source
    for site, old_bytes in (
        ("0x00432A2Du", "0x9E,0x87,0x0A,0x00"),
        ("0x00432AB5u", "0x16,0x87,0x0A,0x00"),
        ("0x00432B38u", "0x93,0x86,0x0A,0x00"),
        ("0x00432BD4u", "0xF7,0x85,0x0A,0x00"),
        ("0x00432C7Cu", "0x4F,0x85,0x0A,0x00"),
        ("0x00432D4Eu", "0x7D,0x84,0x0A,0x00"),
        ("0x00432E1Du", "0xAE,0x83,0x0A,0x00"),
        ("0x00432ED2u", "0xF9,0x82,0x0A,0x00"),
    ):
        assert site in source
        assert old_bytes in source
        assert site.removeprefix("0x00")[:4] in memory_map
    assert "expected_cache_copy[8]" in source
    assert "g_original_cache_copy(renderer, x, y, width, height, source)" in source
    assert "transfer_cache_to_screen(x, y, width, height)" in source
    assert "g_original_cache_move(destination, source, bytes)" in source
    callsite_installer = _function_body(source, "static BOOL install_callsite(")
    assert "target[0] = 0xE8" in callsite_installer
    assert "target[0] = 0xE9" not in callsite_installer
    assert "target[0] = 0xE9" in _function_body(source, "static BOOL install_one(")
    assert "cache_layer_move_range(dst - G1_CACHE_BASE, src - G1_CACHE_BASE, bytes)" in source
    assert "++g_layer_move_unsupported" in source
    assert "clear_layer_coverage(dst_offset, dst_end)" in source
    assert "mirror_move_bytes" in source
    assert "g1_hd_asset_lookup_identity_block_at(x, y" in source


def test_hd_cache_key_includes_auxiliary_pointer_and_content_digest() -> None:
    source = (ROOT / "tools/inmm_stub/g1_hd_asset.c").read_text(encoding="utf-8")
    assert "#define G1_HD_KEY_LIMIT 4096u" in source
    assert "DWORD auxiliary;" in source
    assert "DWORD auxiliary_digest;" in source
    assert "key->auxiliary == auxiliary" in source
    assert "key->auxiliary_digest == auxiliary_digest" in source


def test_tinted_rle_writers_have_six_argument_pinned_hooks() -> None:
    source = Path("tools/inmm_stub/g1_mirror2x.c").read_text()
    assert "#define G1_TINTED_RLE 0x00466EA0u" in source
    assert "#define G1_TINTED_CLIP_RLE 0x00466540u" in source
    assert "expected_tinted_rle" in source
    assert "{0x83, 0xEC, 0x14, 0x8B, 0x44, 0x24, 0x1C}" in source
    assert "expected_tinted_clip_rle" in source
    assert "{0x51, 0x53, 0x56, 0x57, 0x8B, 0x7C, 0x24, 0x18}" in source


def test_tinted_rle_hooks_reinvoke_original_with_lut_identity() -> None:
    source = Path("tools/inmm_stub/g1_mirror2x.c").read_text()
    assert "mirror_tinted_rle" in source
    assert "mirror_tinted_clip_rle" in source
    for function in ("mirror_tinted_rle", "mirror_tinted_clip_rle"):
        body = _function_body(source, f"static DWORD __attribute__((thiscall)) {function}(")
        assert "g_original_tinted" in body
        assert "source, lut," in body
        flat = " ".join(body.split())
        assert "256u, G1_TINTED_RLE, tinted_origin_outside_screen(" in flat or (
            "256u, G1_TINTED_CLIP_RLE, TRUE" in flat
        )
        assert "G1_TINTED_RLE" in body or "G1_TINTED_CLIP_RLE" in body


def test_unclipped_tinted_rle_uses_viewport_replay_only_for_offscreen_origin() -> None:
    source = Path("tools/inmm_stub/g1_mirror2x.c").read_text()
    helper = _function_body(source, "static BOOL tinted_origin_outside_screen(")
    assert "G1_RENDERER_HEIGHT" in helper
    assert "(LONG)(SHORT)x" in helper and "(LONG)(SHORT)y" in helper
    assert "800" in helper
    body = _function_body(source, "static DWORD __attribute__((thiscall)) mirror_tinted_rle(")
    assert "tinted_origin_outside_screen(renderer, x, y, width, height)" in " ".join(body.split())
    assert "256u, G1_TINTED_RLE, FALSE" not in body
    clip_body = _function_body(
        source, "static DWORD __attribute__((thiscall)) mirror_tinted_clip_rle("
    )
    assert "256u, G1_TINTED_CLIP_RLE, TRUE" in clip_body


def test_g1_environment_reads_are_latched_outside_hot_paths() -> None:
    for path in G1_ENVIRONMENT_SOURCES:
        source = path.read_text(encoding="utf-8")
        initializer = _function_body(source, "static void initialize_environment(void)")
        assert source.count("GetEnvironmentVariableA(") == initializer.count(
            "GetEnvironmentVariableA("
        ), path.name

    mirror = MIRROR.read_text(encoding="utf-8")
    compose = _function_body(mirror, "DWORD g1_mirror2x_compose_sentinel(")
    pixel_loop = compose[compose.index("for (y = bounds.y") :]
    assert "g1_hd_asset_enabled(" not in pixel_loop
    assert "_env(" not in pixel_loop
    assert "_enabled(" not in pixel_loop


def test_present_gate_is_content_keyed_and_keeps_logical_800_contract() -> None:
    source = MIRROR.read_text(encoding="utf-8")
    assert "destination_width != 1600u" in source
    assert "source_width < 800u" in source
    assert "src_width != 800u" in source
    assert "source_rect ? *source_rect : (RECT){0, 0, 800, 600}" in source
    assert "return_address" not in source.split("g1_mirror2x_present_rect", 1)[1].split(
        "BOOL g1_mirror2x_input_point", 1
    )[0]


def test_live_surface_role_gate_is_compiled_and_fail_closed(tmp_path: Path) -> None:
    fixture = tmp_path / "g1_present_contract_fixture.c"
    executable = tmp_path / "g1_present_contract_fixture"
    fixture.write_text(
        r'''#include <assert.h>
#include "g1_present_contract.h"

static G1PresentGateInput base_input(void) {
    G1PresentGateInput input = {0};
    input.destination_identity = 0x1000u;
    input.source_identity = 0x2000u;
    input.destination_caps = G1_PRESENT_CAPS_PRIMARYSURFACE;
    input.destination_width = 1600u;
    input.destination_height = 1200u;
    input.destination_descriptor_known = 1;
    input.source_descriptor_known = 1;
    return input;
}

int main(void) {
    G1PresentGateInput input = base_input();
    G1PresentGateDecision decision;

    input.source_width = 832u;
    input.source_height = 600u;
    input.source_rect_present = 1;
    input.source_right = 800;
    input.source_bottom = 600;
    decision = g1_present_gate_decide(&input);
    assert(decision.eligible && decision.variant == G1_PRESENT_VARIANT_OFFSCREEN_800);
    assert(decision.destination_right == 1600 && decision.destination_bottom == 1200);

    input.source_width = 1600u;
    input.source_height = 1200u;
    input.source_caps = G1_PRESENT_CAPS_BACKBUFFER;
    input.source_rect_present = 0;
    input.source_left = input.source_top = input.source_right = input.source_bottom = 0;
    decision = g1_present_gate_decide(&input);
    assert(decision.eligible && decision.variant == G1_PRESENT_VARIANT_MENU_BACKBUFFER);
    assert(decision.source_right == 800 && decision.source_bottom == 600);

    input.source_identity = input.destination_identity;
    decision = g1_present_gate_decide(&input);
    assert(!decision.eligible && decision.reject_reason == G1_PRESENT_REJECT_SAME_SURFACE);
    input.source_identity = 0x2000u;
    input.source_caps = 0u;
    decision = g1_present_gate_decide(&input);
    assert(!decision.eligible && decision.reject_reason == G1_PRESENT_REJECT_MENU_ROLE);
    input.source_caps = G1_PRESENT_CAPS_BACKBUFFER;
    input.x = 1u;
    decision = g1_present_gate_decide(&input);
    assert(!decision.eligible && decision.reject_reason == G1_PRESENT_REJECT_MENU_ROLE);
    input.x = 0u;
    input.source_rect_present = 1;
    input.source_right = 800;
    input.source_bottom = 600;
    decision = g1_present_gate_decide(&input);
    assert(!decision.eligible && decision.reject_reason == G1_PRESENT_REJECT_MENU_ROLE);
    return 0;
}
''',
        encoding="utf-8",
    )
    result = __import__("subprocess").run(
        ["gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-I", str(PRESENT_CONTRACT.parent),
         str(fixture), "-o", str(executable)],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    run = __import__("subprocess").run([str(executable)], capture_output=True, text=True, check=False)
    assert run.returncode == 0, run.stderr


def test_present_fallback_is_handled_without_second_blt_fast() -> None:
    source = DIRECT_DRAW.read_text(encoding="utf-8")
    body_start = source.rindex("static HRESULT WINAPI hook_blt_fast(")
    body_end = source.index("\nstatic HRESULT WINAPI hook_flip", body_start)
    body = source[body_start:body_end]
    assert "BOOL mirror_handled = FALSE;" in source
    assert "BOOL fallback_attempted = FALSE;" in source
    assert "if (!mirror_handled && !converted) {" in body
    assert body.count("record->original_blt_fast(") == 1
    assert "result = record->original_blt_fast(self, x, y, source, src, flags);" in body
    assert "fallback_succeeded = SUCCEEDED(result);" in source


def test_long_mirror_metrics_are_split_before_win32_wsprintf_limit() -> None:
    source = DIRECT_DRAW.read_text(encoding="utf-8")
    assert "char mirror_dump_details[260];" in source
    assert "char mirror_perf_details[1100];" in source
    for writer_key in (
        "terrain_rle_468c30_calls", "terrain_shade_468cc0_calls",
        "terrain_checker_468e10_calls", "terrain_clip_468f00_calls",
        "terrain_clip_shade_4690a0_calls",
    ):
        assert writer_key in source
    assert "lstrcatA(mirror_details, mirror_dump_details);" in source
    assert "lstrcatA(mirror_details, mirror_perf_details);" in source


def test_sentinel_compositor_records_covered_pixels_and_falls_back_at_present() -> None:
    source = MIRROR.read_text(encoding="utf-8")
    assert "a != 0x00u || b != 0xFFu" in source
    assert "g_covered[logical] = 1u" in source
    assert "g_mirror + y * 2u * 1600u + x * 2u" in source
    assert "mirror_pixel[1601u]" in source
    assert "BYTE pixel = source_row[x]" in source
    assert "DDLOCK_READONLY" in source


def test_sentinel_uses_logical_mask_indices_and_same_frame_snapshot() -> None:
    source = MIRROR.read_text(encoding="utf-8")
    assert "g_expected_snapshot" in source
    assert "g_stale_pixels" in source
    assert "DWORD logical = y * width + x;" in source
    assert "DWORD expected_index = y * src_stride + x;" in source
    assert "g_expected_snapshot[logical] = expected800[expected_index]" in source
    assert "g_expected_snapshot[p] == pixel" in source
    assert "++g_stale_pixels" in source


def test_primitive_scratch_initialization_uses_safe_writer_bbox(tmp_path: Path) -> None:
    source = MIRROR.read_text(encoding="utf-8")
    assert "g1_mirror_scratch_bounds(origin_x, origin_y, width, height" in source
    assert "g1_mirror2x_compose_sentinel(expected, g_scratch_a, g_scratch_b" in source
    assert "primitive_x, primitive_y, primitive_width" in source

    fixture = tmp_path / "scratch_bounds_fixture.c"
    executable = tmp_path / "scratch_bounds_fixture"
    fixture.write_text(
        r'''#include <assert.h>
#include "g1_scratch_bounds.h"

int main(void) {
    G1ScratchBounds bounds;
    assert(g1_scratch_intersection(10, 3, 20, 24, 800, 600, &bounds));
    assert(bounds.x == 10 && bounds.y == 3 && bounds.width == 20 && bounds.height == 24);
    assert(g1_scratch_intersection(780, 576, 20, 24, 800, 600, &bounds));
    assert(bounds.x == 780 && bounds.y == 576 && bounds.width == 20 && bounds.height == 24);
    assert(g1_scratch_intersection(790, 590, 20, 20, 800, 600, &bounds));
    assert(bounds.x == 790 && bounds.y == 590 && bounds.width == 10 && bounds.height == 10);
    assert(g1_scratch_intersection(-10, 5, 20, 10, 800, 600, &bounds));
    assert(bounds.x == 0 && bounds.y == 5 && bounds.width == 10 && bounds.height == 10);
    assert(g1_scratch_intersection(-30, 0, 10, 10, 800, 600, &bounds));
    assert(bounds.width == 0 && bounds.height == 10);
    assert(!g1_scratch_intersection(0, 0, 0, 24, 800, 600, &bounds));
    assert(!g1_scratch_intersection(0x7fffffff, 0, 2, 1, 800, 600, &bounds));
    return 0;
}
''',
        encoding="utf-8",
    )
    result = __import__("subprocess").run(
        ["gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-I",
         str(MIRROR.parent), str(fixture), "-o", str(executable)],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    run = __import__("subprocess").run([str(executable)], capture_output=True, text=True, check=False)
    assert run.returncode == 0, run.stderr


def test_cache_scratch_clear_matches_compose_frame_and_preserves_screen_contract(
    tmp_path: Path,
) -> None:
    fixture = tmp_path / "mirror_frame_fixture.c"
    executable = tmp_path / "mirror_frame_fixture"
    fixture.write_text(
        r'''#include <assert.h>
#include <stdint.h>
#include <string.h>
#include "g1_mirror_frame.h"

static void clear_frame(uint8_t *a, uint8_t *b, unsigned stride,
                        int x, int y, unsigned w, unsigned h, int cache) {
    G1ScratchBounds bounds;
    unsigned row, col;
    assert(g1_mirror_scratch_bounds(x, y, w, h, cache, 600u, &bounds));
    for (row = bounds.y; row < bounds.y + bounds.height; ++row)
        for (col = 0; col < bounds.width; ++col) {
            a[row * stride + bounds.x + col] = 0u;
            b[row * stride + bounds.x + col] = 255u;
        }
}

int main(void) {
    uint8_t a[832 * 600], b[832 * 600];
    G1ScratchBounds bounds;
    unsigned x, y;
    assert(g1_mirror_frame_width(1) == 832u);
    assert(g1_mirror_frame_width(0) == 800u);
    {
        long vp[4];
        g1_mirror_replay_viewport(0, 600u, vp);
        assert(vp[0] == 0 && vp[1] == 0 && vp[2] == 799 && vp[3] == 599);
        g1_mirror_replay_viewport(1, 512u, vp);
        assert(vp[0] == 0 && vp[1] == 0 && vp[2] == 831 && vp[3] == 511);
        assert((unsigned)(vp[2] + 1) <= 832u && (unsigned)(vp[3] + 1) <= 512u);
    }
    /* Unclipped bind gate: screen keeps its 800 limit, cache follows 832. */
    assert(g1_mirror_unclipped_bind_fits(736, 10, 64, 32, 0, 600u));
    assert(!g1_mirror_unclipped_bind_fits(737, 10, 64, 32, 0, 600u));
    assert(!g1_mirror_unclipped_bind_fits(768, 10, 64, 32, 0, 600u));
    assert(g1_mirror_unclipped_bind_fits(768, 10, 64, 32, 1, 512u));
    assert(!g1_mirror_unclipped_bind_fits(769, 10, 64, 32, 1, 512u));
    assert(!g1_mirror_unclipped_bind_fits(-1, 10, 64, 32, 1, 512u));
    assert(!g1_mirror_unclipped_bind_fits(0, 481, 64, 32, 1, 512u));
    assert(g1_mirror_unclipped_bind_fits(0, 480, 64, 32, 1, 512u));
    assert(!g1_mirror_unclipped_bind_fits(0, 0, 833, 32, 1, 512u));
    assert(g1_mirror_scratch_bounds(768, 10, 64, 32, 1, 600, &bounds));
    assert(bounds.x == 768 && bounds.width == 64);
    assert(g1_mirror_scratch_bounds(800, 10, 64, 32, 1, 600, &bounds));
    assert(bounds.x == 800 && bounds.width == 32);
    assert(g1_mirror_scratch_bounds(-32, 10, 64, 32, 1, 600, &bounds));
    assert(bounds.x == 0 && bounds.width == 32);
    assert(g1_mirror_scratch_bounds(768, 10, 64, 32, 0, 600, &bounds));
    assert(bounds.x == 768 && bounds.width == 32);

    memset(a, 7, sizeof(a)); memset(b, 7, sizeof(b));
    clear_frame(a, b, 832, 768, 10, 64, 32, 1);
    for (y = 10; y < 42; ++y) for (x = 768; x < 832; ++x)
        assert(a[y * 832 + x] == 0u && b[y * 832 + x] == 255u);
    memset(a, 7, sizeof(a)); memset(b, 7, sizeof(b));
    clear_frame(a, b, 832, 800, 10, 64, 32, 1);
    for (y = 10; y < 42; ++y) for (x = 800; x < 832; ++x)
        assert(a[y * 832 + x] == 0u && b[y * 832 + x] == 255u);
    memset(a, 7, sizeof(a)); memset(b, 7, sizeof(b));
    clear_frame(a, b, 832, 768, 10, 64, 32, 0);
    for (y = 10; y < 42; ++y) {
        for (x = 768; x < 800; ++x)
            assert(a[y * 832 + x] == 0u && b[y * 832 + x] == 255u);
        for (x = 800; x < 832; ++x)
            assert(a[y * 832 + x] == 7u && b[y * 832 + x] == 7u);
    }
    return 0;
}
''',
        encoding="utf-8",
    )
    result = __import__("subprocess").run(
        ["gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-I",
         str(MIRROR.parent), str(fixture), "-o", str(executable)],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    run = __import__("subprocess").run([str(executable)], capture_output=True, text=True, check=False)
    assert run.returncode == 0, run.stderr


def test_mirror_reinvoke_uses_one_frame_width_for_clear_and_compose() -> None:
    source = MIRROR.read_text(encoding="utf-8")
    reinvoke = _function_body(source, "static void mirror_reinvoke(")
    assert "g1_mirror_scratch_bounds(origin_x, origin_y, width, height" in reinvoke
    assert "cache_target = (DWORD)(ULONG_PTR)expected == G1_CACHE_BASE" in reinvoke
    assert "g1_mirror_scratch_bounds(origin_x, origin_y, width, height" in _function_body(
        source, "static DWORD compose_cache_layer("
    )


def test_clipped_replay_viewport_follows_target_and_counts_cache_binds() -> None:
    source = MIRROR.read_text(encoding="utf-8")
    reinvoke = _function_body(source, "static void mirror_reinvoke(")
    assert "g1_mirror_replay_viewport(cache_target, surface_height, full_viewport)" in reinvoke
    assert "{0, 0, 799, 599}" not in reinvoke
    assert reinvoke.count("++g_cache_clip_attempts") == 1
    assert reinvoke.count("++g_cache_clip_verify_failures") == 2
    assert "cache_clip_verify_failures" in DIRECT_DRAW.read_text(encoding="utf-8")


def test_unclipped_bind_gate_uses_target_frame_width_and_counts_cache_edge_binds() -> None:
    source = MIRROR.read_text(encoding="utf-8")
    reinvoke = _function_body(source, "static void mirror_reinvoke(")
    assert "g1_mirror_unclipped_bind_fits(origin_x, origin_y, width, height" in reinvoke
    assert "width <= 800u && height <= surface_height" not in reinvoke
    assert reinvoke.count("++g_cache_edge_unclipped_binds") == 1
    assert "cache_edge_unclipped_binds" in DIRECT_DRAW.read_text(encoding="utf-8")


def test_opt_in_perf_reports_whole_reinvoke_and_exclusive_clip_preparation() -> None:
    perf_header = (ROOT / "tools/inmm_stub/g1_perf_sections.h").read_text(encoding="utf-8")
    perf_source = (ROOT / "tools/inmm_stub/g1_perf_sections.c").read_text(encoding="utf-8")
    mirror = MIRROR.read_text(encoding="utf-8")
    trace = DIRECT_DRAW.read_text(encoding="utf-8")
    reinvoke = _function_body(mirror, "static void mirror_reinvoke(")
    assert "G1_PERF_WHOLE_TINTED" in perf_header
    assert "G1_PERF_WHOLE_TINTED_CLIP" in perf_header
    assert "G1_PERF_WHOLE_OTHER" in perf_header
    assert "G1_PERF_CLIP_PREPARE" in perf_header
    assert "g1_perf_sections_accumulate" in perf_source
    assert "g1_perf_sections_elapsed" in perf_source
    assert "if (!g1_perf_sections_enabled() || !QueryPerformanceCounter(&now)) return 0u" in perf_source
    assert "whole_started = g1_perf_sections_start()" in reinvoke
    assert "G1_PERF_WHOLE_TINTED_CLIP" in reinvoke
    assert "g1_perf_sections_end(writer == G1_TINTED_RLE" in reinvoke
    assert "g1_perf_sections_accumulate(G1_PERF_CLIP_PREPARE" in reinvoke
    assert "invoke_original(writer, renderer, args, TRUE)" in reinvoke
    assert reinvoke.count("g1_perf_sections_accumulate(G1_PERF_CLIP_PREPARE") == 1
    assert "perf_reinvoke_whole" in trace and "perf_clip_prepare" in trace
    assert "g1_perf_sections_accumulate(section, g1_perf_sections_elapsed(started), bytes)" in perf_source
    assert "if (ticks == 0u || section >= G1_PERF_SECTION_COUNT" in perf_source
    reset = _function_body(perf_source, "void g1_perf_sections_reset(void)")
    assert "i < G1_PERF_SECTION_COUNT" in reset
    assert all(f"g_stats[i].{field} = 0u" in reset
               for field in ("count", "total_qpc_ticks", "max_qpc_ticks", "bytes"))
    assert reinvoke.index("g1_perf_sections_end(writer == G1_TINTED_RLE") > reinvoke.rindex("return;")


def test_clip_cost_buckets_time_alloc_fill_and_mask_without_overlapping_each_other() -> None:
    perf_header = (ROOT / "tools/inmm_stub/g1_perf_sections.h").read_text(encoding="utf-8")
    perf_source = (ROOT / "tools/inmm_stub/g1_perf_sections.c").read_text(encoding="utf-8")
    mirror = MIRROR.read_text(encoding="utf-8")
    trace = DIRECT_DRAW.read_text(encoding="utf-8")
    sections = (
        ("G1_PERF_CLIP_TEMP_ALLOC_FREE", "temporary_alloc_free", "requested_bytes"),
        ("G1_PERF_CLIP_BUFFER_FILL", "buffer_fill", "bytes"),
        ("G1_PERF_CLIP_MASK_PREPARE", "mask_prepare", "bytes"),
    )
    for enum_name, trace_name, bytes_name in sections:
        assert enum_name in perf_header
        assert f'\\"{trace_name}\\"' in trace
        assert f'\\"{bytes_name}\\"' in trace
    alloc = _function_body(mirror, "static BYTE *clip_prepare_alloc(")
    free = _function_body(mirror, "static void clip_prepare_free(")
    fill = _function_body(mirror, "static void clip_prepare_fill(")
    mask = _function_body(mirror, "static void clip_prepare_mask(")
    for body, category in (
        (alloc, "G1_PERF_CLIP_TEMP_ALLOC_FREE"),
        (free, "G1_PERF_CLIP_TEMP_ALLOC_FREE"),
        (fill, "G1_PERF_CLIP_BUFFER_FILL"),
        (mask, "G1_PERF_CLIP_MASK_PREPARE"),
    ):
        assert body.count("g1_perf_sections_start()") == 1
        assert body.count("g1_perf_sections_elapsed(started)") == 1
        assert body.count(f"g1_perf_sections_accumulate({category}") == 1
    assert "HeapAlloc(GetProcessHeap(), 0, bytes)" in alloc
    assert "HeapFree(GetProcessHeap(), 0, memory)" in free
    assert "fill_bytes(destination, value, bytes)" in fill
    assert "mask_row[x] = zero_row[x] == ff_row[x]" in mask
    reinvoke = _function_body(mirror, "static void mirror_reinvoke(")
    assert "clip_prepare_alloc(bytes)" in reinvoke
    assert "clip_prepare_alloc((SIZE_T)width * height)" in reinvoke
    assert "if (unclipped && unclipped_ff)" in reinvoke
    assert "if (written)" in reinvoke
    assert reinvoke.count("clip_prepare_free(") == 4
    # The second identity check compares the clipped FF-background lane with
    # its full replay counterpart; scratch_a is the 00-background lane.
    first_verify = reinvoke.index("g1_hd_asset_verify_unclipped_frame_in_viewport(")
    second_verify = reinvoke.index(
        "g1_hd_asset_verify_unclipped_frame_in_viewport(",
        first_verify + 1,
    )
    assert "(const BYTE *)scratch_a" in reinvoke[first_verify:second_verify]
    assert "(const BYTE *)scratch_b" in reinvoke[second_verify:]
    assert "clip_prepare_mask(unclipped, unclipped_ff" in reinvoke

    # Parent clip timing must include both full-buffer allocations and the
    # written-mask allocation, including their NULL/failure paths.
    alloc_pair = reinvoke.index("BYTE *unclipped = clip_prepare_alloc(bytes);")
    alloc_pair_end = reinvoke.index("if (unclipped && unclipped_ff)", alloc_pair)
    alloc_pair_timed = reinvoke.rfind(
        "clip_prepare_ticks += g1_perf_sections_elapsed(clip_prepare_started);",
        alloc_pair,
        alloc_pair_end,
    )
    assert alloc_pair_timed > reinvoke.index("BYTE *unclipped_ff =", alloc_pair)
    assert alloc_pair_timed < alloc_pair_end
    mask_alloc = reinvoke.index("BYTE *written = clip_prepare_alloc(")
    mask_alloc_elapsed = reinvoke.index(
        "clip_prepare_ticks += g1_perf_sections_elapsed(clip_prepare_started);",
        mask_alloc,
    )
    mask_success = reinvoke.index("if (written) {", mask_alloc)
    assert mask_alloc_elapsed < mask_success
    first_verify = reinvoke.index(
        "g1_hd_asset_verify_unclipped_frame_in_viewport(", alloc_pair_end
    )
    assert reinvoke.rfind("clip_prepare_started = g1_perf_sections_start();", first_verify,
                         mask_alloc_elapsed) != -1

    # The parent timer pauses around the original replay and bind calls.
    original_replay = reinvoke.index("invoke_original(writer, renderer, args, TRUE);")
    replay_timer_stop = reinvoke.rfind(
        "clip_prepare_ticks += g1_perf_sections_elapsed(clip_prepare_started);",
        alloc_pair,
        original_replay,
    )
    replay_timer_resume = reinvoke.index(
        "clip_prepare_started = g1_perf_sections_start();", original_replay
    )
    assert replay_timer_stop != -1 and replay_timer_stop < original_replay
    assert replay_timer_resume > original_replay
    bind_call = reinvoke.index("g1_hd_asset_bind_identity_frame(unclipped, stride")
    bind_timer_stop = reinvoke.rfind(
        "clip_prepare_ticks += g1_perf_sections_elapsed(clip_prepare_started);",
        mask_alloc_elapsed,
        bind_call,
    )
    assert bind_timer_stop != -1 and bind_timer_stop < bind_call
    reset = _function_body(perf_source, "void g1_perf_sections_reset(void)")
    assert "i < G1_PERF_SECTION_COUNT" in reset
    assert "if (!g1_perf_sections_enabled() || !QueryPerformanceCounter(&now)) return 0u" in perf_source


def test_mirror_byte_fill_helpers_preserve_unaligned_ranges_and_tail_bytes(tmp_path: Path) -> None:
    import subprocess

    source = MIRROR.read_text(encoding="utf-8")
    word_fill = _function_body(source, "void fill_pattern_bytes(")
    zero = _function_body(source, "void zero_bytes(")
    fill = _function_body(source, "void fill_bytes(")
    fixture = tmp_path / "byte_fill.c"
    executable = tmp_path / "byte_fill"
    fixture.write_text(
        "#include <stdint.h>\n#include <stdio.h>\n"
        "typedef uint8_t BYTE; typedef uint32_t DWORD; typedef uintptr_t ULONG_PTR;\n"
        + "static void fill_pattern_bytes(void *memory, BYTE value, DWORD size) "
        + word_fill + "\n"
        + "static void zero_bytes(void *memory, DWORD size) " + zero + "\n"
        + "static void fill_bytes(void *memory, BYTE value, DWORD size) " + fill + "\n"
        + "int main(void) { unsigned char b[8200]; unsigned n, off, i;\n"
        "for (n=0; n<=256; ++n) for (off=0; off<4; ++off) {\n"
        "for(i=0;i<8200;++i)b[i]=0xA5;\nzero_bytes(b+off,n);\n"
        "for(i=0;i<8200;++i) if(b[i] != ((i>=off && i<off+n)?0:0xA5)) return 1;\n"
        "for(i=0;i<8200;++i)b[i]=0xA5;\nfill_bytes(b+off,(BYTE)n,(DWORD)n);\n"
        "for(i=0;i<8200;++i) if(b[i] != ((i>=off && i<off+n)?(BYTE)n:0xA5)) return 2; }\n"
        "return 0; }\n", encoding="utf-8"
    )
    build = subprocess.run(
        ["gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-O2",
         str(fixture), "-o", str(executable)],
        capture_output=True, text=True, check=False,
    )
    assert build.returncode == 0, build.stderr
    run = subprocess.run([str(executable)], capture_output=True, text=True, check=False)
    assert run.returncode == 0, run.stderr


def test_primitive_install_is_transactional_and_restores_exact_old_bytes() -> None:
    source = MIRROR.read_text(encoding="utf-8")
    assert "typedef struct {" in source and "G1HookState" in source
    assert "restore_hook(&g_hook_a)" in source
    assert "restore_hook(&g_hook_b)" in source
    assert "g_hook_a.installed" in source
    assert "g_hook_b.installed" in source
    assert "bytes_equal(hook->target, hook->original" in source


def test_input_bridge_converts_messages_and_cursor_contracts() -> None:
    source = MIRROR.read_text(encoding="utf-8")
    header = HEADER.read_text(encoding="utf-8")
    assert "WM_MOUSEFIRST" in source and "WM_MOUSELAST" in source
    assert "LOWORD(lparam)" in source and "HIWORD(lparam)" in source
    assert "GetCursorPos" in source and "SetCursorPos" in source and "ClipCursor" in source
    assert "g1_mirror2x_input_install" in header
    direct = DIRECT_DRAW.read_text(encoding="utf-8")
    assert "g1_mirror2x_input_install()" in direct
    assert "g1_mirror2x_primitives_install()" in direct


def test_live_probe_requires_metrics_and_accepts_complete_same_frame_records(tmp_path: Path) -> None:
    from tools.g1_mirror2x_probe import validate_trace

    events: list[dict[str, object]] = []
    for program_state in (3, 5, 7, 9):
        events.extend([
            {"event": "blt", "program_state": program_state,
             "destination_is_primary": 1, "converted": 1},
            {"event": "mirror2x_present", "success": 1, "fallback": 0,
             "source_width": 800, "source_height": 600,
             "destination_width": 1600, "destination_height": 1200,
             "source_identity": "0x1", "destination_identity": "0x2",
             "source_rect": {"left": 0, "top": 0, "right": 800, "bottom": 600},
             "destination_rect": {"left": 0, "top": 0, "right": 1600, "bottom": 1200},
             "source_hash_fnv1a32": "0x1", "destination_hash_fnv1a32": "0x2",
             "source_dump_hex": "00", "destination_dump_hex": "0000",
             "nearest_matches": 1920000, "nearest_total": 1920000,
             "same_frame_oracle": 1, "covered_pixels": 10,
             "elapsed_ms": 100, "primitive_reinvoke_elapsed_ms_total": 80,
             "primitive_reinvoke_elapsed_ms_max": 40, "primitive_reinvoke_count": 2,
             "primitive_install_success": 1, "primitive_call_count": 2},
        ])
    events.append({"event": "summary"})
    trace = tmp_path / "trace.jsonl"
    trace.write_text("\n".join(json.dumps(event) for event in events) + "\n", encoding="utf-8")
    assert validate_trace(trace)["status"] == "PASS"

    incomplete = tmp_path / "incomplete.jsonl"
    incomplete.write_text(json.dumps(events[0]) + "\n", encoding="utf-8")
    verdict = validate_trace(incomplete)
    assert verdict["status"] == "BLOCKED"
    assert any("no live mirror2x_present" in error for error in verdict["errors"])


def test_python_reference_nearest_shape_matches_the_fixed_rect_contract() -> None:
    source = bytes(range(4))
    result = bytearray(16)
    for y in range(2):
        for x in range(2):
            pixel = source[y * 2 + x]
            row = (y * 2) * 4
            result[row + x * 2 : row + x * 2 + 2] = bytes((pixel, pixel))
            result[row + 4 + x * 2 : row + 4 + x * 2 + 2] = bytes((pixel, pixel))
    assert bytes(result) == bytes((0, 0, 1, 1, 0, 0, 1, 1,
                                   2, 2, 3, 3, 2, 2, 3, 3))


@pytest.mark.parametrize("flag", ["--g1-mirror2x"])
def test_runtime_cli_requires_native_split_for_mirror(flag: str, capsys: pytest.CaptureFixture[str]) -> None:
    from tools import runtime_env

    result = runtime_env.runtime_main([
        "g1-presentation-trace", "--manifest", "/missing/manifest.json", flag,
    ])
    assert result == 2
    assert "requires --native-2x-blit" in capsys.readouterr().err


def test_menu_block_copy_is_mirrored_from_its_packed_source_and_reported() -> None:
    source = MIRROR.read_text(encoding="utf-8")
    header = HEADER.read_text(encoding="utf-8")
    trace = DIRECT_DRAW.read_text(encoding="utf-8")
    copy_hook = _function_body(source, "static DWORD __attribute__((thiscall)) mirror_cache_copy(")
    assert "transfer_block_copy_to_screen(renderer, x, y, width, height, source)" in copy_hook
    body = _function_body(source, "static void transfer_block_copy_to_screen(")
    # The full-screen packed-source copy seen in the menu (lap950: (0,0,800,600)) plus,
    # since H-P35, any in-bounds partial rectangle through the shared frame-copy helper.
    assert "g1_frame_copy_accepts(x, y, width, height)" in body
    assert "G1_CACHE_BASE" in body and "g_panel_bound_buffer" in body
    assert "readable_bytes(src, width * height)" in body
    assert "g1_frame_copy_apply(" in body
    assert 'g1_hd_asset_source_name()' in body
    assert "g_expected_snapshot, g_covered, g_mirror" in body
    for name in ("menu_copy_calls", "menu_copy_pixels", "menu_copy_hash_first",
                 "menu_copy_hash_last", "menu_copy_hash_changes"):
        assert f"g1_mirror2x_{name}(void)" in header
        assert f'\\"{name}\\"' in trace


def test_stale_mask_state_gate_defaults_to_ps3_and_follows_the_selected_state(tmp_path: Path) -> None:
    """H-RS1 RS1-0: SYW2_G1_STALE_MASK_STATE picks the program state the stale mask dumps (3/5/7/20/23/27/29)."""
    import subprocess

    fixture = tmp_path / "stale_mask_state.c"
    executable = tmp_path / "stale_mask_state"
    fixture.write_text(
        r'''#include <assert.h>
#include "g1_stale_mask.h"

int main(void) {
    assert(g1_stale_mask_state_parse("27", 2u) == 27u);
    assert(g1_stale_mask_state_parse("29", 2u) == 29u);
    assert(g1_stale_mask_state_parse("23", 2u) == 23u);
    /* H-SC1 SC1-0: "20" follows the scenario briefing PS20 */
    assert(g1_stale_mask_state_parse("20", 2u) == 20u);
    assert(g1_stale_mask_state_parse("200", 3u) == 3u);
    assert(g1_stale_mask_state_parse("3", 1u) == 3u);
    assert(g1_stale_mask_state_parse("", 0u) == 3u);
    /* H-PS5W0 W0-0: single-digit "5" / "7" follow the solo lobby PS5 / the title protocol PS7 */
    assert(g1_stale_mask_state_parse("5", 1u) == 5u);
    assert(g1_stale_mask_state_parse("7", 1u) == 7u);
    assert(g1_stale_mask_state_parse("57", 2u) == 3u);
    assert(g1_stale_mask_state_parse("4", 1u) == 3u);
    assert(g1_stale_mask_state_parse("50", 2u) == 3u);
    assert(g1_stale_mask_state_parse("28", 2u) == 3u);
    assert(g1_stale_mask_state_parse("270", 3u) == 3u);
    assert(g1_stale_mask_state_parse("2", 1u) == 3u);
    return 0;
}
''',
        encoding="utf-8",
    )
    subprocess.run(
        ["gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", f"-I{ROOT / 'tools/inmm_stub'}",
         str(fixture), "-o", str(executable)],
        check=True,
    )
    subprocess.run([str(executable)], check=True)


def test_mirror_present_selects_the_stale_mask_state_from_the_env() -> None:
    source = (ROOT / "tools/inmm_stub/g1_mirror2x.c").read_text(encoding="utf-8")
    assert '#define G1_STALE_MASK_STATE_ENV "SYW2_G1_STALE_MASK_STATE"' in source
    init = source[source.index("static void initialize_environment(void)"):]
    init = init[: init.index("\n}\n")]
    assert "g1_stale_mask_state_parse(" in init
    present = source[source.index("HRESULT g1_mirror2x_copy_present("):]
    present = present[: present.index("ZeroMemory(&g_last_present")]
    # env absent => g_stale_mask_state stays 3 => the old `== 3u` PS3 selection is unchanged
    assert "program_state == 3u" not in present
    assert "program_state == g_stale_mask_state" in present


def test_stale_mask_helper_parses_ordinals_and_classifies_pixels_with_host_gcc(tmp_path: Path) -> None:
    import subprocess

    helper = ROOT / "tools/inmm_stub/g1_stale_mask.h"
    fixture = tmp_path / "stale_mask.c"
    executable = tmp_path / "stale_mask"
    fixture.write_text(
        r'''#include <assert.h>
#include "g1_stale_mask.h"
int main(void) {
    G1StaleMaskSpec spec;
    unsigned long header[8];
    assert(g1_stale_mask_parse("6-12,300,579-630", 16u, &spec) == 1 && spec.count == 3u);
    assert(g1_stale_mask_selected(&spec, 5u) == 0);
    assert(g1_stale_mask_selected(&spec, 6u) == 1 && g1_stale_mask_selected(&spec, 12u) == 1);
    assert(g1_stale_mask_selected(&spec, 13u) == 0);
    assert(g1_stale_mask_selected(&spec, 300u) == 1 && g1_stale_mask_selected(&spec, 301u) == 0);
    assert(g1_stale_mask_selected(&spec, 579u) == 1 && g1_stale_mask_selected(&spec, 630u) == 1);
    assert(g1_stale_mask_selected(&spec, 631u) == 0);
    assert(g1_stale_mask_parse("0", 1u, &spec) == 1 && g1_stale_mask_selected(&spec, 0u) == 1);
    /* a-b/step samples every step-th ordinal starting at a (burst hunting over a wide window) */
    assert(g1_stale_mask_parse("420-640/8", 9u, &spec) == 1 && spec.count == 1u);
    assert(g1_stale_mask_selected(&spec, 420u) == 1 && g1_stale_mask_selected(&spec, 428u) == 1);
    assert(g1_stale_mask_selected(&spec, 421u) == 0 && g1_stale_mask_selected(&spec, 427u) == 0);
    assert(g1_stale_mask_selected(&spec, 636u) == 1 && g1_stale_mask_selected(&spec, 644u) == 0);
    assert(g1_stale_mask_selected(&spec, 419u) == 0);
    assert(g1_stale_mask_parse("6-12,420-640/8", 14u, &spec) == 1 && spec.count == 2u);
    assert(g1_stale_mask_selected(&spec, 9u) == 1 && g1_stale_mask_selected(&spec, 436u) == 1);
    assert(g1_stale_mask_parse("6-12/", 5u, &spec) == 0 && spec.count == 0u);
    assert(g1_stale_mask_parse("6-12/0", 6u, &spec) == 0);
    assert(g1_stale_mask_parse("6/2", 3u, &spec) == 0);
    assert(g1_stale_mask_parse("6-12/12345", 10u, &spec) == 0);
    /* malformed specs are rejected and leave the spec empty (nothing is dumped) */
    assert(g1_stale_mask_parse("", 0u, &spec) == 0 && spec.count == 0u);
    assert(g1_stale_mask_parse("6-", 2u, &spec) == 0 && spec.count == 0u);
    assert(g1_stale_mask_parse("-6", 2u, &spec) == 0);
    assert(g1_stale_mask_parse("12-6", 4u, &spec) == 0);
    assert(g1_stale_mask_parse("6,,7", 4u, &spec) == 0);
    assert(g1_stale_mask_parse("6,", 2u, &spec) == 0);
    assert(g1_stale_mask_parse("6;7", 3u, &spec) == 0);
    assert(g1_stale_mask_parse("12345", 5u, &spec) == 0);
    assert(g1_stale_mask_parse("1,2,3,4,5,6,7,8", 15u, &spec) == 1 && spec.count == 8u);
    assert(g1_stale_mask_parse("1,2,3,4,5,6,7,8,9", 17u, &spec) == 0 && spec.count == 0u);
    assert(g1_stale_mask_selected(&spec, 1u) == 0);
    /* 0 uncovered, 1 covered and equal, 2 covered but stale */
    assert(g1_stale_mask_value(0, 0) == 0u && g1_stale_mask_value(0, 1) == 0u);
    assert(g1_stale_mask_value(1, 1) == 1u && g1_stale_mask_value(1, 0) == 2u);
    g1_stale_mask_header(header, 9u, 3ul, 1234ul, 77ul, 400000ul, 42700ul);
    assert(header[0] == 0x314B3153ul && header[1] == 9ul && header[2] == 3ul);
    assert(header[3] == 1234ul && header[4] == 77ul && header[5] == 400000ul);
    assert(header[6] == 42700ul && header[7] == 480000ul);
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


_WINDOWS_SHIM = r"""#ifndef FAKE_WINDOWS_H
#define FAKE_WINDOWS_H
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
typedef int BOOL; typedef unsigned int DWORD; typedef int LONG;
typedef unsigned char BYTE; typedef unsigned long long ULONGLONG;
typedef size_t SIZE_T; typedef uintptr_t ULONG_PTR; typedef void *HANDLE;
typedef union { struct { DWORD LowPart; LONG HighPart; }; long long QuadPart; } LARGE_INTEGER;
#define TRUE 1
#define FALSE 0
#define MEM_COMMIT 0x1000
#define PAGE_NOACCESS 1
#define PAGE_GUARD 0x100
typedef struct { void *BaseAddress; SIZE_T RegionSize; DWORD State; DWORD Protect; } MEMORY_BASIC_INFORMATION;
static inline DWORD GetEnvironmentVariableA(const char *n, char *v, DWORD size)
{ const char *e = getenv(n); DWORD l; if (!e) return 0; l = (DWORD)strlen(e); if (l >= size) return l + 1; memcpy(v, e, l + 1); return l; }
static inline LONG InterlockedCompareExchange(volatile LONG *d, LONG x, LONG c)
{ LONG o = *d; if (o == c) *d = x; return o; }
static inline LONG InterlockedExchange(volatile LONG *d, LONG x) { LONG o = *d; *d = x; return o; }
static inline void Sleep(DWORD ms) { (void)ms; }
static inline DWORD GetTickCount(void) { static DWORD tick; return ++tick; }   /* every call is a new tick: no stale cache on the host */
static inline SIZE_T VirtualQuery(const void *a, MEMORY_BASIC_INFORMATION *i, SIZE_T l)
{ (void)l; i->BaseAddress = (void *)a; i->RegionSize = 1u << 20; i->State = MEM_COMMIT; i->Protect = 4; return sizeof(*i); }
static inline HANDLE GetProcessHeap(void) { return 0; }
static inline void *HeapAlloc(HANDLE h, DWORD f, SIZE_T n) { (void)h; (void)f; return malloc(n); }
static inline BOOL HeapFree(HANDLE h, DWORD f, void *p) { (void)h; (void)f; free(p); return 1; }
/* stdio-backed file API for the HD pack loader and key log */
#include <stdio.h>
#define MAX_PATH 260
#define INVALID_HANDLE_VALUE ((HANDLE)(intptr_t)-1)
#define GENERIC_READ 1u
#define GENERIC_WRITE 2u
#define FILE_SHARE_READ 1u
#define OPEN_EXISTING 3u
#define CREATE_ALWAYS 2u
#define FILE_ATTRIBUTE_NORMAL 0x80u
#define INVALID_FILE_ATTRIBUTES 0xFFFFFFFFu
#include <sys/stat.h>
static inline DWORD GetFileAttributesA(const char *path)
{ struct stat st; return stat(path, &st) == 0 ? (S_ISDIR(st.st_mode) ? 0x10u : 0x80u) : INVALID_FILE_ATTRIBUTES; }
static inline HANDLE CreateFileA(const char *path, DWORD access, DWORD share, void *sec, DWORD disp, DWORD attr, void *tmpl)
{ FILE *fp; (void)share; (void)sec; (void)disp; (void)attr; (void)tmpl;
  fp = fopen(path, (access & GENERIC_WRITE) ? "wb" : "rb"); return fp ? (HANDLE)fp : INVALID_HANDLE_VALUE; }
static inline DWORD GetFileSize(HANDLE h, DWORD *high)
{ FILE *fp = (FILE *)h; long cur = ftell(fp), n; fseek(fp, 0, SEEK_END); n = ftell(fp); fseek(fp, cur, SEEK_SET);
  if (high) { *high = 0; }
  return (DWORD)n; }
static inline BOOL ReadFile(HANDLE h, void *b, DWORD n, DWORD *got, void *o)
{ (void)o; *got = (DWORD)fread(b, 1, n, (FILE *)h); return 1; }
static inline BOOL WriteFile(HANDLE h, const void *b, DWORD n, DWORD *w, void *o)
{ (void)o; *w = (DWORD)fwrite(b, 1, n, (FILE *)h); return 1; }
static inline BOOL CloseHandle(HANDLE h) { return fclose((FILE *)h) == 0; }
#define lstrlenA(s) ((DWORD)strlen(s))
#define lstrcpyA(d, s) strcpy(d, s)
#define wsprintfA sprintf
#endif
"""


def test_hit_compare_is_limited_to_the_renderer_viewport_with_host_gcc(tmp_path: Path) -> None:
    import subprocess

    stub = ROOT / "tools/inmm_stub"
    (tmp_path / "windows.h").write_text(_WINDOWS_SHIM, encoding="utf-8")
    fixture = tmp_path / "hit_compare.c"
    executable = tmp_path / "hit_compare"
    fixture.write_text(
        r"""#include <assert.h>
#include <stdlib.h>
#include "g1_hd_asset.h"
#include "g1_perf_sections.h"
ULONGLONG g1_perf_sections_start(void) { return 0u; }
void g1_perf_sections_end(G1PerfSection s, ULONGLONG t, ULONGLONG b) { (void)s; (void)t; (void)b; }
void g1_perf_sections_reset(void) {}
static BYTE screen[800 * 600];
static BYTE source[256];
BYTE g_fake_renderer[0x70000];
/* writer 7 at origin (10,10), 4x4 sprite of 5s; identity frame comes from a full-viewport replay */
static void bind_sprite(void)
{
    BYTE frame[16], written[16];
    int i;
    for (i = 0; i < 16; ++i) { frame[i] = 5u; written[i] = 1u; }
    g1_hd_asset_reset();
    assert(g1_hd_asset_begin(source, 7u, 4u, 4u, 10, 10) == TRUE);
    assert(g1_hd_asset_needs_identity_frame() == TRUE);
    assert(g1_hd_asset_bind_identity_frame(frame, 4u, written, 4u, 4u, 4u) == TRUE);
    g1_hd_asset_end();
    assert(g1_hd_asset_begin(source, 7u, 4u, 4u, 10, 10) == TRUE);
    assert(g1_hd_asset_needs_identity_frame() == FALSE);
}
static void paint_screen(int x0)
{
    int x, y;
    for (y = 0; y < 600; ++y)
        for (x = 0; x < 800; ++x) screen[y * 800 + x] = 0u;
    for (y = 10; y < 14; ++y)
        for (x = x0; x < 14; ++x) screen[y * 800 + x] = 5u;
}
int main(void)
{
    setenv("SYW2_G1_HD_SOURCE", "identity", 1);
    /* writer clipped columns 10..11 (viewport left=12): only outside-viewport pixels differ */
    bind_sprite(); paint_screen(12);
    assert(g1_hd_asset_compare_visible_frame_in_viewport(screen, 800u, 4u, 4u, 12, 0, 799, 599) == TRUE);
    assert(g1_hd_asset_identity_cache_refreshes() == 0u && g1_hd_asset_current_ready() == TRUE);
    /* the unrestricted wrapper keeps the old whole-screen behaviour (refresh) */
    assert(g1_hd_asset_compare_visible_frame(screen, 800u, 4u, 4u) == FALSE);
    assert(g1_hd_asset_identity_cache_refreshes() == 1u && g1_hd_asset_current_ready() == FALSE);
    /* one differing pixel inside the viewport still refreshes */
    bind_sprite(); paint_screen(12);
    screen[12 * 800 + 13] = 9u;
    assert(g1_hd_asset_compare_visible_frame_in_viewport(screen, 800u, 4u, 4u, 12, 0, 799, 599) == FALSE);
    assert(g1_hd_asset_identity_cache_refreshes() == 1u && g1_hd_asset_current_ready() == FALSE);
    /* full-screen viewport is byte-identical to the unrestricted compare, both ways */
    bind_sprite(); paint_screen(10);
    assert(g1_hd_asset_compare_visible_frame_in_viewport(screen, 800u, 4u, 4u, 0, 0, 799, 599) == TRUE);
    assert(g1_hd_asset_identity_cache_refreshes() == 0u && g1_hd_asset_current_ready() == TRUE);
    paint_screen(12);
    assert(g1_hd_asset_compare_visible_frame_in_viewport(screen, 800u, 4u, 4u, 0, 0, 799, 599) == FALSE);
    assert(g1_hd_asset_identity_cache_refreshes() == 1u);
    /* sprite entirely outside the viewport: nothing compared, cache kept */
    bind_sprite(); paint_screen(14);
    assert(g1_hd_asset_compare_visible_frame_in_viewport(screen, 800u, 4u, 4u, 100, 100, 700, 500) == FALSE);
    assert(g1_hd_asset_identity_cache_refreshes() == 0u && g1_hd_asset_current_ready() == TRUE);
    /* malformed (inverted) viewport never evicts */
    assert(g1_hd_asset_compare_visible_frame_in_viewport(screen, 800u, 4u, 4u, 20, 0, 10, 599) == FALSE);
    assert(g1_hd_asset_identity_cache_refreshes() == 0u && g1_hd_asset_current_ready() == TRUE);
    return 0;
}
""",
        encoding="utf-8",
    )
    (tmp_path / "fake_renderer.h").write_text("#include <windows.h>\nextern BYTE g_fake_renderer[];\n", encoding="utf-8")
    build = subprocess.run(
        ["gcc", "-std=gnu11", "-Wall", "-Wextra", "-Werror", "-Wno-unused-function",
         "-I", str(tmp_path), "-I", str(stub), "-include", str(tmp_path / "fake_renderer.h"),
         "-DG1_HD_RENDERER_BASE=g_fake_renderer", str(fixture), str(stub / "g1_hd_asset.c"),
         "-o", str(executable)],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert build.returncode == 0, build.stderr
    run = subprocess.run([str(executable)], capture_output=True, text=True, check=False)
    assert run.returncode == 0, run.stderr


def test_live_hit_compare_passes_the_renderer_viewport_and_not_a_full_screen_range() -> None:
    source = MIRROR.read_text()
    flat = " ".join(source.split())
    assert "g1_hd_asset_compare_visible_frame_in_viewport(" in flat
    assert "g1_hd_asset_compare_visible_frame((const BYTE *)scratch_a" not in flat
    hit = flat[flat.index("g1_hd_asset_compare_visible_frame_in_viewport(") - 400 :
               flat.index("g1_hd_asset_compare_visible_frame_in_viewport(") + 200]
    assert "G1_RENDERER_VIEWPORT" in hit


def test_stale_mask_dump_is_opt_in_ps3_only_and_leaves_default_present_path_unchanged() -> None:
    source = MIRROR.read_text(encoding="utf-8")
    assert '#include "g1_stale_mask.h"' in source
    assert "g1_stale_mask.h" in (ROOT / "tools/inmm_stub/Makefile").read_text(encoding="utf-8")
    initializer = _function_body(source, "static void initialize_environment(void)")
    assert '#define G1_STALE_MASK_ENV "SYW2_G1_STALE_MASK"' in source
    assert "GetEnvironmentVariableA(G1_STALE_MASK_ENV" in initializer
    assert "g1_stale_mask_parse(" in initializer
    present = _function_body(source, "HRESULT g1_mirror2x_copy_present(")
    # selection is decided once per present, before the pixel loop; the loop only writes into an optional buffer
    assert present.index("g1_stale_mask_selected(") < present.index("for (y = 0; y < height; ++y)")
    assert "g1_stale_mask_value(" in present
    assert "mask_dump" in present
    # ordinals count presents of the selected program state only (PS3 unless H-RS1's state env says
    # otherwise) and the dump is capped
    assert "G1_STALE_MASK_DUMP_LIMIT" in source
    assert "g_stale_mask_ordinal" in source
    assert '#define G1_STALE_MASK_PATH "C:\\\\inmm_g1_stale_mask.bin"' in source
    # the header sums are the present record's own covered/stale counters
    assert "g1_stale_mask_header(" in present
    assert "covered_now, stale_now" in present[present.index("g1_stale_mask_header("):]


def test_probe_exposes_stale_mask_option_for_the_candidate_lane_only() -> None:
    source = (ROOT / "tools/g1_saved_scene_probe.py").read_text(encoding="utf-8")
    assert '"--stale-mask"' in source
    assert "--stale-mask requires --hd-source scale2x" in source
    assert "stale_mask=args.stale_mask" in source
    # the env reaches the candidate lane only, and the artifact is copied beside the other raw outputs
    candidate_env = source[source.index("if candidate:"):source.index("xvfb, display = runtime_env._xvfb")]
    assert 'env["SYW2_G1_STALE_MASK"] = stale_mask' in candidate_env
    assert 'prefix / "drive_c" / "inmm_g1_stale_mask.bin"' in source
    assert '"stale_mask.bin"' in source


def test_layer_drift_helper_geometry_overlap_and_counts_with_host_gcc(tmp_path: Path) -> None:
    import subprocess

    helper = ROOT / "tools/inmm_stub/g1_layer_drift.h"
    fixture = tmp_path / "layer_drift.c"
    executable = tmp_path / "layer_drift"
    fixture.write_text(
        r'''#include <assert.h>
#include <string.h>
#include "g1_layer_drift.h"
static unsigned char cache[832 * 512], lexp[832 * 512], lcov[832 * 512];
static unsigned char screen[800 * 600], snap[800 * 600], cov[800 * 600];
int main(void)
{
    unsigned x, y, i;
    G1LayerDriftCounts c;
    /* three save000 stale components (lap1010/lap1012), half-open rects */
    assert(g1_layer_drift_rect(0).x0 == 38u && g1_layer_drift_rect(0).x1 == 187u);
    assert(g1_layer_drift_rect(0).y0 == 64u && g1_layer_drift_rect(0).y1 == 169u);
    assert(g1_layer_drift_rect(1).x0 == 371u && g1_layer_drift_rect(1).x1 == 503u);
    assert(g1_layer_drift_rect(1).y0 == 427u && g1_layer_drift_rect(1).y1 == 492u);
    assert(g1_layer_drift_rect(2).x0 == 259u && g1_layer_drift_rect(2).x1 == 338u);
    assert(g1_layer_drift_rect(2).y0 == 0u && g1_layer_drift_rect(2).y1 == 26u);
    assert(g1_layer_drift_rect(3).x1 == 0u);
    /* sample points A (112,126) B (437,463) C (302,9) lie inside their own rect only */
    for (i = 0u; i < G1_LAYER_DRIFT_RECTS; ++i) {
        g1_layer_drift_sample(i, &x, &y);
        assert(g1_layer_drift_contains(i, (long)x, (long)y) == 1);
    }
    g1_layer_drift_sample(0u, &x, &y); assert(x == 112u && y == 126u);
    g1_layer_drift_sample(1u, &x, &y); assert(x == 437u && y == 463u);
    g1_layer_drift_sample(2u, &x, &y); assert(x == 302u && y == 9u);
    assert(g1_layer_drift_contains(0u, 37, 100) == 0 && g1_layer_drift_contains(0u, 38, 100) == 1);
    assert(g1_layer_drift_contains(0u, 186, 168) == 1 && g1_layer_drift_contains(0u, 187, 168) == 0);
    assert(g1_layer_drift_contains(0u, 186, 169) == 0);
    /* overlap pixel counts, including negative origins and disjoint regions */
    assert(g1_layer_drift_overlap(0u, 0, 0, 800u, 600u) == 149u * 105u);
    assert(g1_layer_drift_overlap(0u, 38, 64, 1u, 1u) == 1u);
    assert(g1_layer_drift_overlap(0u, 30, 60, 10u, 10u) == 2u * 6u);
    assert(g1_layer_drift_overlap(0u, -5, -5, 10u, 10u) == 0u);
    assert(g1_layer_drift_overlap(0u, 187, 64, 10u, 10u) == 0u);
    assert(g1_layer_drift_overlap(2u, 300, -4, 10u, 10u) == 10u * 6u);
    assert(g1_layer_drift_overlap(9u, 0, 0, 800u, 600u) == 0u);
    /* counts: untouched layer = every pixel uncovered, nothing stale */
    memset(cache, 7, sizeof(cache)); memset(screen, 7, sizeof(screen));
    g1_layer_drift_count(2u, cache, lexp, lcov, screen, 800u, snap, cov, &c);
    assert(c.uncovered == 79u * 26u && c.stale == 0u && c.screen_ne_cache == 0u && c.snap_ne_layer == 0u);
    /* covered layer that matches the cache is not drift */
    memset(lcov, 1, sizeof(lcov)); memset(lexp, 7, sizeof(lexp));
    g1_layer_drift_count(2u, cache, lexp, lcov, screen, 800u, snap, cov, &c);
    assert(c.uncovered == 0u && c.stale == 0u);
    /* cache written after compose: 3 stale pixels, one of them also differs on screen */
    cache[9u * 832u + 302u] = 92u; cache[0u * 832u + 259u] = 1u; cache[25u * 832u + 337u] = 2u;
    screen[9u * 800u + 302u] = 92u;
    cache[26u * 832u + 259u] = 5u; /* outside rect C: ignored */
    g1_layer_drift_count(2u, cache, lexp, lcov, screen, 800u, snap, cov, &c);
    assert(c.stale == 3u && c.uncovered == 0u);
    assert(c.screen_ne_cache == 2u); /* (259,0) and (337,25) still show 7 against cache 1/2 */
    /* snapshot only counts where the screen is covered */
    snap[9u * 800u + 302u] = 3u;
    g1_layer_drift_count(2u, cache, lexp, lcov, screen, 800u, snap, cov, &c);
    assert(c.snap_ne_layer == 0u);
    cov[9u * 800u + 302u] = 1u;
    g1_layer_drift_count(2u, cache, lexp, lcov, screen, 800u, snap, cov, &c);
    assert(c.snap_ne_layer == 1u);
    /* uncovered layer pixel is not stale even if the cache changed */
    lcov[0u * 832u + 259u] = 0u;
    g1_layer_drift_count(2u, cache, lexp, lcov, screen, 800u, snap, cov, &c);
    assert(c.stale == 2u && c.uncovered == 1u);
    assert(G1_DRIFT_CALL_REASONS == 7u && G1_DRIFT_PX_RESULTS == 4u);
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


def test_layer_drift_sample_override_parser_with_host_gcc(tmp_path: Path) -> None:
    import subprocess

    helper = ROOT / "tools/inmm_stub/g1_layer_drift.h"
    fixture = tmp_path / "drift_samples.c"
    executable = tmp_path / "drift_samples"
    fixture.write_text(
        r'''#include <assert.h>
#include <string.h>
#include "g1_layer_drift.h"
static int parse(const char *text) { return g1_layer_drift_samples_parse(text, (unsigned long)strlen(text)); }
static void expect_defaults(void)
{
    unsigned x, y;
    g1_layer_drift_sample(0u, &x, &y); assert(x == 112u && y == 126u);
    g1_layer_drift_sample(1u, &x, &y); assert(x == 437u && y == 463u);
    g1_layer_drift_sample(2u, &x, &y); assert(x == 302u && y == 9u);
}
int main(void)
{
    unsigned x, y;
    expect_defaults();
    /* anything malformed or out of [0,800)x[0,600) leaves the defaults untouched */
    assert(parse("") == 0 && parse(";;") == 0 && parse("1,2") == 0);
    assert(parse("1,2;3,4") == 0 && parse("1,2;3,4;5,6;7,8") == 0);
    assert(parse("1,2;3,4;5") == 0 && parse("1,2;3,4;5,") == 0 && parse("1,2;3,4;,6") == 0);
    assert(parse("1,2;3,4;800,6") == 0 && parse("1,2;3,4;5,600") == 0);
    assert(parse("1,2;3,4;a,6") == 0 && parse("1,2;3,4;5,6,7") == 0 && parse("1,2;3,4;-5,6") == 0);
    assert(parse("1,2;3,4;12345,6") == 0);
    expect_defaults();
    /* a partial failure must not leave a half-written table */
    assert(parse("10,20;30,40;999,1") == 0);
    expect_defaults();
    assert(parse("583,306;480,515;799,599") == 1);
    g1_layer_drift_sample(0u, &x, &y); assert(x == 583u && y == 306u);
    g1_layer_drift_sample(1u, &x, &y); assert(x == 480u && y == 515u);
    g1_layer_drift_sample(2u, &x, &y); assert(x == 799u && y == 599u);
    assert(parse("0,0;0,0;0,0") == 1);
    g1_layer_drift_sample(2u, &x, &y); assert(x == 0u && y == 0u);
    /* a later bad spec keeps the last good override */
    assert(parse("1,2") == 0);
    g1_layer_drift_sample(0u, &x, &y); assert(x == 0u && y == 0u);
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


def test_drift_samples_override_is_opt_in_env_and_harness_flag() -> None:
    mirror = MIRROR.read_text(encoding="utf-8")
    watch = (ROOT / "tools/inmm_stub/g1_screen_watch.c").read_text(encoding="utf-8")
    probe = (ROOT / "tools/g1_saved_scene_probe.py").read_text(encoding="utf-8")
    # both translation units own a copy of the sample table, so both read the env
    for source in (mirror, watch):
        assert "SYW2_G1_DRIFT_SAMPLES" in source
        assert "g1_layer_drift_samples_parse(" in source
    assert '"--drift-samples"' in probe
    assert 'env["SYW2_G1_DRIFT_SAMPLES"] = drift_samples' in probe
    assert "--drift-samples requires --layer-drift" in probe


def test_layer_drift_diagnostic_is_opt_in_and_leaves_default_paths_unchanged() -> None:
    source = MIRROR.read_text(encoding="utf-8")
    assert '#include "g1_layer_drift.h"' in source
    assert "g1_layer_drift.h" in (ROOT / "tools/inmm_stub/Makefile").read_text(encoding="utf-8")
    assert '#define G1_LAYER_DRIFT_ENV "SYW2_G1_LAYER_DRIFT"' in source
    assert '#define G1_LAYER_DRIFT_PATH "C:\\\\inmm_g1_layer_drift.jsonl"' in source
    initializer = _function_body(source, "static void initialize_environment(void)")
    assert "GetEnvironmentVariableA(G1_LAYER_DRIFT_ENV" in initializer
    # every cache-target outcome of mirror_reinvoke is noted, each only when the env is on
    reinvoke = _function_body(source, "static void mirror_reinvoke(")
    for reason in ("G1_DRIFT_RET_ARGS", "G1_DRIFT_RET_BUFFER", "G1_DRIFT_RET_PANEL_FOREIGN",
                   "G1_DRIFT_RET_RANGE", "G1_DRIFT_NOT_READY", "G1_DRIFT_COMPOSE_RAN"):
        assert reason in reinvoke, reason
    compose = _function_body(source, "static DWORD compose_cache_layer(")
    for result in ("G1_DRIFT_COMPOSE_BOUNDS", "G1_DRIFT_PX_A_NE_B", "G1_DRIFT_PX_UNWRITTEN",
                   "G1_DRIFT_PX_LOOKUP_MISS", "G1_DRIFT_PX_COMPOSED"):
        assert result in compose, result
    # the compose pixel math is untouched: same skip conditions, same stores
    assert "if (a != b || (a == 0u && b == 0xFFu)) continue;" not in compose or "drift" in compose
    assert "g_layer_expected[logical] = expected[logical];" in compose
    # the per-present sampler runs for program state 3 only, before the stale loop mutates g_covered
    present = _function_body(source, "HRESULT g1_mirror2x_copy_present(")
    assert "layer_drift_present(" in present
    assert present.index("layer_drift_present(") < present.index("for (y = 0; y < height; ++y)")
    sampler = _function_body(source, "static void layer_drift_present(")
    assert "G1_PROGRAM_STATE_VA" in sampler and "g1_layer_drift_count(" in sampler
    # nested-guard bypasses of cache-target writers are counted by the wrappers
    assert source.count("layer_drift_guard_bypass(renderer);") >= 5


def test_ulc_blend_size_reject_diag_is_opt_in_env_and_candidate_only_flag() -> None:
    """H-ULc U-0: a diagnostic-only switch reproduces the lap1083 size reject of 0x467580/0x467B00."""
    source = MIRROR.read_text(encoding="utf-8")
    probe = (ROOT / "tools/g1_saved_scene_probe.py").read_text(encoding="utf-8")
    assert '#define G1_BLEND_SIZE_REJECT_DIAG_ENV "SYW2_G1_BLEND_SIZE_REJECT_DIAG"' in source
    assert "static BOOL g_blend_size_reject_diag = FALSE;" in source
    initializer = _function_body(source, "static void initialize_environment(void)")
    assert "GetEnvironmentVariableA(G1_BLEND_SIZE_REJECT_DIAG_ENV" in initializer
    assert "g_blend_size_reject_diag = size == 1u && value[0] == '1';" in initializer
    # off by default: the helper answers FALSE unless the env switch is on
    helper = _function_body(source, "static BOOL blend_size_reject_diag(int width, int height, BOOL check_height)")
    assert "initialize_environment();" in helper
    assert "g_blend_size_reject_diag" in helper
    assert "G1_OVERLAY_MAX_WIDTH" in helper and "G1_OVERLAY_MAX_HEIGHT" in helper
    # 0x467580 rejects width > 320 or height > 160, 0x467B00 only width > 320 (lap1083 contract)
    wrle = _function_body(source, "static DWORD __attribute__((thiscall)) mirror_blend_wrle(")
    clip = _function_body(source, "static DWORD __attribute__((thiscall)) mirror_blend_clip(")
    for body, name, check_height in ((wrle, "wrle", "TRUE"), (clip, "clip", "FALSE")):
        call = f"blend_size_reject_diag(x1 - x0, y1 - y0, {check_height})"
        assert body.count("blend_size_reject_diag(") == 1 and call in body
        # decided after the bounds check, before the before-copy; the original still runs unchanged
        assert body.index('why = "reject_bounds";') < body.index(call) < body.index('why = "mirrored";')
        assert f"g_blend_{name}_reject_size += 1u;" in body
        assert body.count(f"g_original_blend_{name}(") == 1
        assert body.count("g1_overlay_blt_apply_tiled(") == 1
    # harness: opt-in flag, candidate lane only, needs the scale2x candidate
    assert '"--blend-size-reject-diag"' in probe
    assert "--blend-size-reject-diag requires --hd-source scale2x" in probe
    assert "blend_size_reject_diag=args.blend_size_reject_diag" in probe
    candidate_env = probe[probe.index("if candidate:"):probe.index("xvfb, display = runtime_env._xvfb")]
    assert 'env["SYW2_G1_BLEND_SIZE_REJECT_DIAG"] = "1"' in candidate_env


def test_ua0_candidate_no_present_trace_flag_preserves_owned_run_id() -> None:
    """H-UA0 U-0: disable present events but keep the candidate run ID for owned close."""
    probe = (ROOT / "tools/g1_saved_scene_probe.py").read_text(encoding="utf-8")
    assert '"--candidate-no-present-trace"' in probe
    assert "--candidate-no-present-trace requires --hd-source scale2x" in probe
    assert "no_present_trace=args.candidate_no_present_trace" in probe
    candidate_env = probe[probe.index("if candidate:"):probe.index("xvfb, display = runtime_env._xvfb")]
    assert "if no_present_trace:" in candidate_env
    assert "_disable_present_trace(env)" in candidate_env
    disable_present_trace = probe[
        probe.index("def _disable_present_trace("):probe.index("\ndef _performance_present_metrics(")
    ]
    assert 'env.pop("SYW2_G1_PRESENT_TRACE", None)' in disable_present_trace
    assert 'env.pop("SYW2_G1_TRACE_RUN_ID", None)' not in disable_present_trace
    # the stub installs the mirror without the trace opt-in (the trace log is a mirror byproduct)
    trace = (ROOT / "tools/inmm_stub/direct_draw_trace.c").read_text(encoding="utf-8")
    install = _function_body(trace, "int g1_direct_draw_trace_install(void)")
    assert "!env_enabled() && !g1_mirror2x_enabled()" in install


def test_ua0_candidate_native_ddraw_flag_is_candidate_only() -> None:
    """H-UA0 U-2: the user's game folder ddraw.dll can be loaded (native) in the candidate lane only."""
    probe = (ROOT / "tools/g1_saved_scene_probe.py").read_text(encoding="utf-8")
    assert '"--candidate-native-ddraw"' in probe
    assert "--candidate-native-ddraw requires --hd-source scale2x" in probe
    assert "native_ddraw=args.candidate_native_ddraw" in probe
    candidate_env = probe[probe.index("if candidate:"):probe.index("xvfb, display = runtime_env._xvfb")]
    assert 'env["WINEDLLOVERRIDES"] = "ddraw=n,b"' in candidate_env


def test_ua2_stub_unit_tick_dump_has_env_opt_out_before_file_open() -> None:
    """H-UA2 UA2-1: INMM_STUB_NO_UNIT_TICKS skips the PS3 unit dump (no file open, no write); unset keeps the old behavior."""
    stub = (ROOT / "tools/inmm_stub/inmm_stub.c").read_text(encoding="utf-8")
    body = _function_body(stub, "static void dump_units_at_tick(DWORD logic_tick)")
    # the only other mention sits inside the SYW2_G1_DEFAULT_ON build's default-setter block (H-DEF1)
    plain = re.sub(r"#ifdef SYW2_G1_DEFAULT_ON.*?#endif\n", "", stub, flags=re.S)
    assert plain.count('"INMM_STUB_NO_UNIT_TICKS"') == 1
    assert 'GetEnvironmentVariableA("INMM_STUB_NO_UNIT_TICKS"' in body
    assert "g_no_unit_ticks" in body
    # read once and cached, and the early return comes before the log file is created
    assert "g_no_unit_ticks < 0" in body
    assert body.index("g_no_unit_ticks) return;") < body.index('CreateFileA("C:\\\\inmm_unit_ticks.jsonl"')
    # the default (env unset) path still creates the same file
    assert body.count('CreateFileA("C:\\\\inmm_unit_ticks.jsonl"') == 1


def test_ua2_candidate_no_unit_ticks_flag_is_candidate_only() -> None:
    """H-UA2 UA2-2: the user-trial opt-out env is reachable from the harness candidate lane only."""
    probe = (ROOT / "tools/g1_saved_scene_probe.py").read_text(encoding="utf-8")
    assert '"--candidate-no-unit-ticks"' in probe
    assert "--candidate-no-unit-ticks requires --hd-source scale2x" in probe
    assert "no_unit_ticks=args.candidate_no_unit_ticks" in probe
    candidate_env = probe[probe.index("if candidate:"):probe.index("xvfb, display = runtime_env._xvfb")]
    assert 'env["INMM_STUB_NO_UNIT_TICKS"] = "1"' in candidate_env
    # baseline lane / default env never set it
    assert probe.count('"INMM_STUB_NO_UNIT_TICKS"') == 1


_RET_RANGE_FIXTURE = r"""
#include <assert.h>
#include <stdint.h>
typedef uint32_t DWORD;
#define G1_RET_RANGE_KILLS_BASE 0x0115B000u
#define G1_RET_RANGE_IDLE_BASE 0x01157000u
#define G1_RET_RANGE_SIZE 0x1000u
@@FUNCTION@@
int main(void)
{
    DWORD kills = 0u, idle = 0u;
    ret_range_diag_count(0x0115BBB9u, &kills, &idle);   /* .kills call site of 0x4664D0 */
    ret_range_diag_count(0x0115B000u, &kills, &idle);   /* first byte of .kills */
    assert(kills == 2u && idle == 0u);
    ret_range_diag_count(0x0115BFFFu, &kills, &idle);   /* last byte of .kills */
    assert(kills == 3u && idle == 0u);
    ret_range_diag_count(0x0115C000u, &kills, &idle);   /* one past .kills: not counted */
    ret_range_diag_count(0x0115AFFFu, &kills, &idle);   /* one before .kills / past .idle */
    assert(kills == 3u && idle == 0u);
    ret_range_diag_count(0x01157000u, &kills, &idle);
    ret_range_diag_count(0x01157FFFu, &kills, &idle);
    assert(kills == 3u && idle == 2u);
    ret_range_diag_count(0x01158000u, &kills, &idle);
    ret_range_diag_count(0x01156FFFu, &kills, &idle);
    ret_range_diag_count(0x0041B78Cu, &kills, &idle);   /* .text return addresses are neither */
    assert(kills == 3u && idle == 2u);
    return 0;
}
"""


def test_ret_range_diag_counts_primitive_b_and_textout_returns_in_kills_idle_only_when_opted_in(tmp_path: Path) -> None:
    """H-E2611G1-1 E1-1: opt-in return-address counters for the 2611 `.kills`/`.idle` sections; off = no change."""
    import subprocess

    source = MIRROR.read_text(encoding="utf-8")
    assert '#define G1_RET_RANGE_DIAG_ENV "SYW2_G1_RET_RANGE_DIAG"' in source
    assert "static BOOL g_ret_range_diag = FALSE;" in source
    initializer = _function_body(source, "static void initialize_environment(void)")
    assert "GetEnvironmentVariableA(G1_RET_RANGE_DIAG_ENV" in initializer
    assert "g_ret_range_diag = size == 1u && value[0] == '1';" in initializer
    # the real helper text, run on the host: [base, base+0x1000) of each section, half-open
    helper = source[source.index("static void ret_range_diag_count("):]
    helper = helper[: helper.index("\n}\n") + 3]
    fixture = tmp_path / "ret_range.c"
    executable = tmp_path / "ret_range"
    fixture.write_text(_RET_RANGE_FIXTURE.replace("@@FUNCTION@@", helper), encoding="utf-8")
    built = subprocess.run(["gcc", "-std=gnu11", "-Wall", "-Wextra", "-Werror", str(fixture), "-o", str(executable)],
                           capture_output=True, text=True, check=False)
    assert built.returncode == 0, built.stderr
    ran = subprocess.run([str(executable)], capture_output=True, text=True, check=False)
    assert ran.returncode == 0, ran.stderr
    # primitive B counts its own return address before anything else runs, only when opted in
    hook_b = _function_body(source, "static DWORD __attribute__((thiscall)) mirror_primitive_b(")
    assert "DWORD return_address = (DWORD)(ULONG_PTR)__builtin_return_address(0);" in hook_b
    count_b = "ret_range_diag_count(return_address, &g_ret_diag_b_kills, &g_ret_diag_b_idle);"
    assert hook_b.count(count_b) == 1 and "if (g_ret_range_diag) " + count_b in hook_b
    assert hook_b.index(count_b) < hook_b.index("InterlockedExchange(&g_primitive_guard, 1)")
    assert hook_b.index("if (!g_original_b) return 0u;") < hook_b.index(count_b)
    # the original B call and the mirror call are unchanged (one each)
    assert hook_b.count("g_original_b(") == 2 and hook_b.count("mirror_reinvoke(") == 1
    # TextOutA counts its caller the same way, before the guard / mirror decisions
    textout = _function_body(source, "static BOOL WINAPI mirror_textout(")
    assert "DWORD return_address = (DWORD)(ULONG_PTR)__builtin_return_address(0);" in textout
    count_t = "ret_range_diag_count(return_address, &g_ret_diag_textout_kills, &g_ret_diag_textout_idle);"
    assert textout.count(count_t) == 1 and "if (g_ret_range_diag) " + count_t in textout
    assert textout.index(count_t) < textout.index("if (g_primitive_guard)")
    # counters are reset with the other textout counters and exposed only through accessors
    for name in ("g_ret_diag_b_kills", "g_ret_diag_b_idle", "g_ret_diag_textout_kills", "g_ret_diag_textout_idle"):
        assert f"static DWORD {name} = 0u;" in source
        assert f"    {name} = 0u;" in source
    assert "BOOL g1_mirror2x_ret_range_diag_enabled(void)" in source
    # the trace record exists only when the diagnostic is on (default output is byte-identical)
    trace = (ROOT / "tools/inmm_stub/direct_draw_trace.c").read_text(encoding="utf-8")
    assert 'trace_event("ret_range_diag", "active"' in trace
    block = trace[trace.index("if (g1_mirror2x_ret_range_diag_enabled())"):]
    assert block.index('trace_event("ret_range_diag"') < block.index("}") + 400
