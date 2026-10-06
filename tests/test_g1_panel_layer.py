"""Host-side contracts for the G1 HUD panel mirror layer."""

from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / "tools/inmm_stub/g1_panel_layer.h"


def test_panel_layer_header_compiles_and_preserves_fold_key_and_transfer_rules(
    tmp_path: Path,
) -> None:
    fixture = tmp_path / "panel_layer_contract.c"
    executable = tmp_path / "panel_layer_contract"
    fixture.write_text(
        r'''#include <assert.h>
#include <stdint.h>
#include <string.h>
#include "g1_panel_layer.h"

int main(void) {
    uint8_t raw_frame[831 * 2];
    uint8_t folded[800 * 2];
    uint8_t encoded_panel[831 * 2 + 4];
    uint8_t expected[4] = {0x21, 0x22, 0xFE, 0xFE};
    uint8_t covered[4] = {1, 1, 1, 1};
    uint8_t hd[16] = {0};
    uint8_t screen_expected[4] = {0x31, 0x32, 0x33, 0x34};
    uint8_t screen_covered[4] = {1, 1, 1, 1};
    uint8_t screen_hd[16];
    char digest[65];
    const uint8_t abc[] = {'a','b','c'};
    const uint8_t rle[] = {
        0x11, 0x12, 0xFE, 0x03,
        0x21, 0x22, 0x23, 0x24, 0x25
    };
    uint8_t decoded[2 * 800];
    size_t encoded_bytes = 0u;
    G1PanelTransferStats stats;
    memset(raw_frame, 0, sizeof(raw_frame));
    memset(folded, 0, sizeof(folded));
    memset(decoded, 0, sizeof(decoded));
    memset(screen_hd, 0xA5, sizeof(screen_hd));
    for (size_t row = 0u; row < 2u; ++row) {
        for (size_t column = 0u; column < 10u; ++column) encoded_panel[encoded_bytes++] = 0x11u;
        encoded_panel[encoded_bytes++] = 0xFEu;
        encoded_panel[encoded_bytes++] = 3u;
        for (size_t column = 13u; column < 831u; ++column)
            encoded_panel[encoded_bytes++] = (uint8_t)(0x40u + (column % 64u));
    }
    assert(g1_panel_decode_rows(encoded_panel, encoded_bytes, 831u, 2u,
                                831u, raw_frame));
    assert(raw_frame[10] == 0xFEu && raw_frame[11] == 0xFEu && raw_frame[12] == 0xFEu);
    assert(g1_panel_fold_frame(raw_frame, 831u, folded, 800u, 800u, 2u));
    assert(g1_panel_frame_equal(folded, 800u, raw_frame, 831u, 800u, 2u));
    assert(g1_panel_decode_rows(rle, sizeof(rle), 5u, 2u, 5u, decoded));
    assert(decoded[0] == 0x11u && decoded[1] == 0x12u && decoded[2] == 0xFEu);
    assert(decoded[5] == 0x21u && decoded[9] == 0x25u);
    assert(!g1_panel_decode_rows(rle, sizeof(rle) - 1u, 5u, 2u, 5u, decoded));
    memset(decoded, 0, sizeof(decoded));
    assert(g1_panel_decode_rows(rle, sizeof(rle), 5u, 2u, 5u, decoded));
    for (size_t i = 0; i < 831u * 2u; ++i) raw_frame[i] = (uint8_t)(i % 251u);
    assert(g1_panel_fold_frame(raw_frame, 831u, folded, 800u, 800u, 2u));
    assert(g1_panel_frame_equal(folded, 800u, raw_frame, 831u, 800u, 2u));
    assert(g1_panel_frame_equal(folded, 800u, folded, 800u, 800u, 2u));
    assert(g1_panel_sha256_rows(abc, 3u, 3u, 1u, digest));
    assert(strcmp(digest, "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad") == 0);
    assert(g1_panel_build_scale2x(expected, 2u, 2u, 2u, hd, 4u));
    assert(g1_panel_key_subpixels(expected, 2u, 2u, 2u, hd, 4u) == 0u);
    assert(g1_panel_apply_transfer(expected, covered, hd, 2u, 4u,
                                   (const uint8_t[]){0x21, 0x99, 0xFE, 0x22}, 2u,
                                   0u, 0u, 0u, 0u, 2u, 2u,
                                   screen_expected, screen_covered, screen_hd,
                                   2u, 4u, 2u, 2u, &stats));
    assert(stats.copied == 1u && stats.key_preserved == 1u &&
           stats.mismatch_cleared == 2u);
    assert(screen_expected[0] == 0x21 && screen_covered[0] == 1u);
    assert(screen_hd[0] == hd[0] && screen_hd[1] == hd[1]);
    assert(screen_expected[1] == 0x32 && screen_covered[1] == 0u);
    assert(screen_expected[2] == 0x33 && screen_covered[2] == 1u);
    assert(screen_hd[8] == 0xA5 && screen_hd[9] == 0xA5);
    assert(screen_covered[3] == 0u);
    return 0;
}
''',
        encoding="utf-8",
    )
    result = subprocess.run(
        ["gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-I",
         str(HEADER.parent), str(fixture), "-o", str(executable)],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    run = subprocess.run([str(executable)], capture_output=True, text=True, check=False)
    assert run.returncode == 0, run.stderr


def test_production_hook_pins_panel_writer_and_fails_closed_on_unbound_surface() -> None:
    mirror = (ROOT / "tools/inmm_stub/g1_mirror2x.c").read_text(encoding="utf-8")
    bridge = (ROOT / "tools/inmm_stub/direct_draw_trace.c").read_text(encoding="utf-8")
    assert "#define G1_PANEL_RLE 0x004663E0u" in mirror
    assert "expected_panel_rle[G1_PANEL_RLE_LEN]" in mirror
    assert "{0x51, 0x53, 0x8B, 0x5C, 0x24, 0x10}" in mirror
    for return_address in ("0x0041B78Cu", "0x0041C5A5u", "0x0042496Au", "0x00441538u"):
        assert return_address in (ROOT / "tools/inmm_stub/g1_panel_layer.h").read_text(encoding="utf-8")
    assert "source != panel_surface" in mirror
    assert "++g_panel_lock_failures" in mirror
    assert "(BYTE *)desc.lpSurface != g_panel_bound_buffer" in mirror
    assert "(DWORD)desc.lPitch != g_panel_bound_pitch" in mirror
    assert "desc.dwHeight != g_panel_bound_height" not in mirror
    assert "g1_mirror2x_panel_transfer(self, source, x, y, src, result" in bridge
    assert "char mirror_details[7200];" in bridge


def test_panel_asset_key_pack_and_binding_contracts(tmp_path: Path) -> None:
    fixture = tmp_path / "panel_pack_contract.c"
    executable = tmp_path / "panel_pack_contract"
    fixture.write_text(
        r'''#include <assert.h>
#include <stdint.h>
#include <string.h>
#include "g1_panel_layer.h"

int main(void) {
    uint8_t source[128], frame[4] = {0x20, 0xFE, 0x22, 0x23};
    uint8_t pack[16] = {
        0x31, 0x32, 0xFE, 0xFE,
        0x33, 0x34, 0xFE, 0xFE,
        0x35, 0x36, 0x37, 0x38,
        0x39, 0x3A, 0x3B, 0x3C
    };
    uint8_t screen_expected[4] = {0, 0, 0, 0};
    uint8_t screen_covered[4] = {0, 0, 0, 0};
    uint8_t screen_hd[16] = {0};
    char key[64], same_key[64], changed_key[64];
    G1PanelTransferStats stats;
    for (size_t i = 0; i < sizeof(source); ++i) source[i] = (uint8_t)i;
    uint32_t digest = g1_panel_source_digest(source, sizeof(source));
    assert(digest != 0u);
    assert(g1_panel_asset_key(key, sizeof(key), 0x004663E0u, 0x12345678u,
                              831u, 143u, digest));
    assert(g1_panel_asset_key(same_key, sizeof(same_key), 0x004663E0u,
                              0x12345678u, 831u, 143u, digest));
    assert(strcmp(key, same_key) == 0);
    assert(strstr(key, "w004663e0_s12345678_h") == key);
    assert(g1_panel_asset_key(changed_key, sizeof(changed_key), 0x004663E0u,
                              0x12345679u, 831u, 143u, digest));
    assert(strcmp(key, changed_key) != 0);
    assert(g1_panel_asset_key(changed_key, sizeof(changed_key), 0x004663E0u,
                              0x12345678u, 831u, 143u, digest + 1u));
    assert(strcmp(key, changed_key) != 0);
    assert(!g1_panel_asset_key(changed_key, sizeof(changed_key), 0x004663E0u,
                               0x12345678u, 800u, 143u, digest));
    assert(g1_panel_hd_pack_valid(frame, 2u, 2u, 2u, pack, sizeof(pack)));
    assert(!g1_panel_hd_pack_valid(frame, 2u, 2u, 2u, pack, sizeof(pack) - 1u));
    pack[2] = 0x44u;
    assert(!g1_panel_hd_pack_valid(frame, 2u, 2u, 2u, pack, sizeof(pack)));
    pack[2] = 0xFEu;
    assert(g1_panel_apply_transfer(frame, (const uint8_t[]){1,1,1,1}, pack,
                                   2u, 4u, frame, 2u, 0u, 0u, 0u, 0u,
                                   2u, 2u, screen_expected, screen_covered,
                                   screen_hd, 2u, 4u, 2u, 2u, &stats));
    assert(screen_hd[0] == 0x31u && screen_hd[1] == 0x32u);
    assert(screen_hd[4] == 0x33u && screen_hd[5] == 0x34u);
    assert(screen_covered[0] == 1u && screen_covered[1] == 0u);
    assert(g1_panel_writer_return(0x0041B78Cu));
    assert(g1_panel_writer_return(0x00441538u));
    assert(!g1_panel_writer_return(0x0045ED41u));
    assert(g1_panel_binding_matches(0x1000u, 800u, 0x1000u, 800u));
    assert(!g1_panel_binding_matches(0x1000u, 800u, 0x2000u, 800u));
    assert(!g1_panel_binding_matches(0x1000u, 800u, 0x1000u, 831u));
    return 0;
}
''',
        encoding="utf-8",
    )
    result = subprocess.run(
        ["gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-I",
         str(HEADER.parent), str(fixture), "-o", str(executable)],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    run = subprocess.run([str(executable)], capture_output=True, text=True, check=False)
    assert run.returncode == 0, run.stderr

    mirror = (ROOT / "tools/inmm_stub/g1_mirror2x.c").read_text(encoding="utf-8")
    assert "panel_load_hd_pack(source, height, g_panel_expected)" in mirror
    assert "g1_panel_build_scale2x(g_panel_expected" in mirror
    assert "expected_bytes = G1_PANEL_WIDTH * height * 4u;" in mirror
