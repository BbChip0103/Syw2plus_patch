"""H-HDL1: pointer-free HD pack name and silhouette check (host-compiled header)."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from test_g1_mirror2x import _WINDOWS_SHIM

ROOT = Path(__file__).resolve().parents[1]
STUB = ROOT / "tools/inmm_stub"


def _run(tmp_path: Path, body: str) -> None:
    fixture = tmp_path / "hd_pack_contract.c"
    executable = tmp_path / "hd_pack_contract"
    fixture.write_text(
        '#include <assert.h>\n#include <stdint.h>\n#include <string.h>\n#include "g1_hd_pack.h"\n'
        "int main(void) {\n" + body + "\n return 0; }\n",
        encoding="utf-8",
    )
    built = subprocess.run(
        ["gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-I", str(STUB), str(fixture), "-o", str(executable)],
        capture_output=True, text=True, check=False,
    )
    assert built.returncode == 0, built.stderr
    ran = subprocess.run([str(executable)], capture_output=True, text=True, check=False)
    assert ran.returncode == 0, ran.stderr


def test_name_is_lowercase_hex_digest_and_decimal_size(tmp_path: Path) -> None:
    _run(tmp_path, r"""
    char name[40];
    assert(g1_hd_pack_name(name, sizeof(name), 0xA3216FADu, 143u, 57u));
    assert(strcmp(name, "ha3216fad_143x57.idx8") == 0);
    assert(g1_hd_pack_name(name, sizeof(name), 0x0000000Fu, 1u, 600u));
    assert(strcmp(name, "h0000000f_1x600.idx8") == 0);
    assert(!g1_hd_pack_name(name, sizeof(name), 1u, 0u, 5u));
    assert(!g1_hd_pack_name(name, sizeof(name), 1u, 801u, 5u));
    assert(!g1_hd_pack_name(name, sizeof(name), 1u, 5u, 601u));
    assert(!g1_hd_pack_name(name, 8u, 1u, 5u, 5u));
    """)


def test_pack_valid_requires_exact_size_and_original_silhouette(tmp_path: Path) -> None:
    _run(tmp_path, r"""
    /* 2x1 pixels: pixel 0 written, pixel 1 not written -> 4x2 pack bytes. */
    const uint8_t written[2] = {1u, 0u};
    uint8_t pack[8] = {0x31u, 0x32u, 0xFEu, 0xFEu,
                       0x33u, 0x34u, 0xFEu, 0xFEu};
    assert(g1_hd_pack_valid(written, 2u, 2u, 1u, pack, sizeof(pack)));
    assert(!g1_hd_pack_valid(written, 2u, 2u, 1u, pack, sizeof(pack) - 1u));
    pack[2] = 0x40u;                       /* hole filled where original wrote nothing */
    assert(!g1_hd_pack_valid(written, 2u, 2u, 1u, pack, sizeof(pack)));
    pack[2] = 0xFEu;
    pack[5] = 0xFEu;                       /* key inside a pixel the original wrote */
    assert(!g1_hd_pack_valid(written, 2u, 2u, 1u, pack, sizeof(pack)));
    pack[5] = 0x34u;
    assert(g1_hd_pack_valid(written, 2u, 2u, 1u, pack, sizeof(pack)));
    assert(!g1_hd_pack_valid(written, 1u, 2u, 1u, pack, sizeof(pack)));  /* stride < width */
    assert(!g1_hd_pack_valid(NULL, 2u, 2u, 1u, pack, sizeof(pack)));
    """)


def test_loader_wiring_in_hd_asset() -> None:
    asset = (STUB / "g1_hd_asset.c").read_text(encoding="utf-8")
    assert '#define G1_HD_PACK_ENV "SYW2_G1_HD_PACK"' in asset
    assert "g1_hd_pack_name(name, sizeof(name), key->digest, key->width, key->height)" in asset
    assert "g1_hd_pack_valid(key->identity_written, key->identity_width" in asset
    assert "key->auxiliary != 0u" in asset                      # aux keys stay on Scale2x
    assert "build_scale2x(" in asset                              # fallback retained


def test_native_hd_sibling_pairs_are_indexed_with_the_original_parser() -> None:
    asset = (STUB / "g1_hd_asset.c").read_text(encoding="utf-8")
    assert "data.cFileName[i + 1u] == 'h'" in asset and "load_hd_single_file" in asset
    assert "native_add_source_frame" in asset and "native_decode_frame" in asset
    assert "hw != sw * 2u || hh != sh * 2u || hc != sc" in asset
    assert "g1_hd_pack_name(name, sizeof(name), digest, width, height)" in asset
    assert "g1_hd_asset_load_named_frame(key" in (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    assert "initialize_sidecars();" in asset and "build_scale2x(" in asset
    probe = (ROOT / "tools/g1_variant_display_probe.py").read_text(encoding="utf-8")
    assert "inmm_asset_log.jsonl" in probe and "hd_named_open_count" in probe


_LOADER_C = r"""#include <assert.h>
#include <stdlib.h>
#include <string.h>
#include "g1_hd_asset.h"
#include "g1_perf_sections.h"
ULONGLONG g1_perf_sections_start(void) { return 0u; }
void g1_perf_sections_end(G1PerfSection s, ULONGLONG t, ULONGLONG b) { (void)s; (void)t; (void)b; }
void g1_perf_sections_reset(void) {}
static BYTE source[256];
static DWORD writer_id = 7u;
/* 2x2 sprite at (10,10): pixel (1,1) not written; all written pixels are 5 */
static void draw(const BYTE *aux, DWORD aux_digest)
{
    BYTE frame[4] = {5u, 5u, 5u, 5u}, written[4] = {1u, 1u, 1u, 0u};
    g1_hd_asset_reset();
    assert(g1_hd_asset_begin_with_aux(source, writer_id, aux, aux_digest, 2u, 2u, 10, 10) == TRUE);
    assert(g1_hd_asset_bind_identity_frame(frame, 2u, written, 2u, 2u, 2u) == TRUE);
}
static BYTE block(DWORD x, DWORD y, int which)
{
    BYTE b[4];
    assert(g1_hd_asset_lookup_identity_block_at(x, y, &b[0], &b[1], &b[2], &b[3]) == TRUE);
    return b[which];
}
static DWORD fnv(const BYTE *bytes, DWORD count)
{
    DWORD hash = 2166136261u, index;
    for (index = 0u; index < count; ++index) { hash ^= bytes[index]; hash *= 16777619u; }
    return hash;
}
/* tinted draw: writer 0x466EA0/0x466540, aux = 256 B table lut[i] = i + 0x40 (0x31 -> key when keycolor) */
static void tinted(DWORD writer, int digest_ok, int keycolor)
{
    BYTE lut[256];
    DWORD index;
    for (index = 0u; index < 256u; ++index) lut[index] = (BYTE)(index + 0x40u);
    if (keycolor) lut[0x31] = 0xFEu;
    writer_id = writer;
    draw(lut, digest_ok ? fnv(lut, 256u) : fnv(lut, 256u) ^ 1u);
    lut[0x31] = 0u;            /* the game rewrites its table after the draw: the key keeps its own copy */
}
/* flip draw (0x466B50, or its clip-box sibling 0x466BE0): the original writes the frame right to left, so its
 * identity mask is the pack's silhouette mirrored: row 0 {1,1}, row 1 {0,1} (pixel (0,1) is the one left unwritten). */
static DWORD flip_writer = 0x00466B50u;
static void flip_draw(int digest_ok)
{
    BYTE lut[256], frame[4] = {5u, 5u, 0u, 5u}, written[4] = {1u, 1u, 0u, 1u};
    DWORD index;
    for (index = 0u; index < 256u; ++index) lut[index] = (BYTE)(index + 0x40u);
    g1_hd_asset_reset();
    assert(g1_hd_asset_begin_with_aux(source, flip_writer, lut, digest_ok ? fnv(lut, 256u) : fnv(lut, 256u) ^ 1u,
                                      2u, 2u, 10, 10) == TRUE);
    assert(g1_hd_asset_bind_identity_frame(frame, 2u, written, 2u, 2u, 2u) == TRUE);
    lut[0x31] = 0u;
}
/* H-HDB5: begin a key whose auxiliary table is `lut` (digest of its current bytes) without resetting the table of keys; bind the
 * identity frame only when the key is new.  `flipped` writers write right to left: their identity mask is the mirrored silhouette. */
static void aux_draw_keep_keys(DWORD writer, const BYTE *lut, int flipped)
{
    BYTE frame[4] = {5u, 5u, 5u, 5u}, written[4] = {1u, 1u, 1u, 0u};
    BYTE flipped_frame[4] = {5u, 5u, 0u, 5u}, flipped_written[4] = {1u, 1u, 0u, 1u};
    assert(g1_hd_asset_begin_with_aux(source, writer, lut, fnv(lut, 256u), 2u, 2u, 10, 10) == TRUE);
    if (g1_hd_asset_needs_identity_frame())
        assert(g1_hd_asset_bind_identity_frame(flipped ? flipped_frame : frame, 2u, flipped ? flipped_written : written, 2u, 2u, 2u) == TRUE);
}
/* shaded terrain: fake renderer tables (pal 3 B/colour, int16 T[(comp<<6)+s], inverse 64^3) */
BYTE g_fake_renderer[0x70000];
static void fake_tables(int bad_palette)
{
    DWORD c, comp, level, r, g, b;
    for (c = 0u; c < 256u; ++c) {
        g_fake_renderer[0x419A0u + c * 3u] = (BYTE)(c % 50u);
        g_fake_renderer[0x419A0u + c * 3u + 1u] = (BYTE)((c * 3u) % 64u);
        g_fake_renderer[0x419A0u + c * 3u + 2u] = (BYTE)((c * 5u + 1u) % 64u);
    }
    for (comp = 0u; comp < 64u; ++comp)
        for (level = 0u; level < 64u; ++level) {
            g_fake_renderer[0x6BCA0u + ((comp << 6) + level) * 2u] = (BYTE)((comp * 2u + level) % 64u);
            g_fake_renderer[0x6BCA0u + ((comp << 6) + level) * 2u + 1u] = 0u;
        }
    for (r = 0u; r < 64u; ++r) for (g = 0u; g < 64u; ++g) for (b = 0u; b < 64u; ++b)
        g_fake_renderer[0x19A0u + (r << 12) + (g << 6) + b] = (BYTE)((r * 7u + g * 3u + b + 5u) & 0xFFu);
    if (bad_palette) g_fake_renderer[0x419A0u] = 64u;
}
/* 10 entries brighter than the start palette (more than the family tolerance of 8): an exact-palette screen */
static void brighten_screen(BYTE value)
{
    DWORD index;
    for (index = 0u; index < 10u; ++index) g_fake_renderer[0x15A0u + index * 4u] = value;
}
static BYTE shade_f(DWORD c, DWORD level)
{
    DWORD r = g_fake_renderer[0x419A0u + c * 3u], g = g_fake_renderer[0x419A0u + c * 3u + 1u],
          b = g_fake_renderer[0x419A0u + c * 3u + 2u];
    DWORD tr = g_fake_renderer[0x6BCA0u + ((r << 6) + level) * 2u];
    DWORD tg = g_fake_renderer[0x6BCA0u + ((g << 6) + level) * 2u];
    DWORD tb = g_fake_renderer[0x6BCA0u + ((b << 6) + level) * 2u];
    return g_fake_renderer[0x19A0u + (tr << 12) + (tg << 6) + tb];
}
/* shade draw: row 0 = pixels 0x11 0x12, row 1 = pixel 0x13; shade map {3,5,3,9}; (1,1) unwritten */
static BYTE shade_map[4] = {3u, 5u, 3u, 9u};
static void shade_draw(DWORD writer, int digest_ok, int wrong_frame, int bad_source)
{
    static const BYTE rle[7] = {0u, 2u, 0x11u, 0x12u, 0u, 1u, 0x13u};
    BYTE frame[4], written[4] = {1u, 1u, 1u, 0u};
    memcpy(source, rle, sizeof(rle));
    if (bad_source) source[0] = 1u;                    /* skip 1 + count 2 > width 2 */
    frame[0] = shade_f(0x11u, shade_map[0]); frame[1] = shade_f(0x12u, shade_map[1]);
    frame[2] = shade_f(0x13u, shade_map[2]); frame[3] = 0u;
    if (wrong_frame) { frame[0] = frame[1] = frame[2] = 5u; }
    g1_hd_asset_reset();
    assert(g1_hd_asset_begin_with_aux(source, writer, shade_map,
                                      digest_ok ? fnv(shade_map, 4u) : fnv(shade_map, 4u) ^ 1u,
                                      2u, 2u, 10, 10) == TRUE);
    assert(g1_hd_asset_bind_identity_frame(frame, 2u, written, 2u, 2u, 2u) == TRUE);
}
/* The game's screen no longer matches the cached identity frame at (10,10): compare evicts it, then the
 * same key is drawn again with a new identity frame (7 everywhere it writes). */
static void refresh_key(const BYTE *aux, DWORD aux_digest, DWORD refreshes)
{
    static BYTE screen[800 * 600];
    BYTE fresh[4] = {7u, 7u, 7u, 7u}, written[4] = {1u, 1u, 1u, 0u};
    screen[10 * 800 + 10] = 0x77u;
    assert(g1_hd_asset_compare_visible_frame(screen, 800u, 2u, 2u) == FALSE);
    assert(g1_hd_asset_identity_cache_refreshes() == refreshes);
    assert(g1_hd_asset_begin_with_aux(source, writer_id, aux, aux_digest, 2u, 2u, 10, 10) == TRUE);
    assert(g1_hd_asset_bind_identity_frame(fresh, 2u, written, 2u, 2u, 2u) == TRUE);
}
int main(int argc, char **argv)
{
    int i;
    (void)argc;
    for (i = 0; i < 256; ++i) source[i] = (BYTE)i;
    setenv("SYW2_G1_HD_SOURCE", "scale2x", 1);
    setenv("SYW2_G1_HD_PACK", argv[2], 1);
    if (!strncmp(argv[1], "clip_flip_", 10)) {           /* the same flip scenarios through the clip-box writer 0x466BE0 */
        flip_writer = 0x00466BE0u;
        argv[1] += 5;
    }
    if (!strcmp(argv[1], "hit") || !strcmp(argv[1], "terrain")) {
        if (!strcmp(argv[1], "terrain")) writer_id = 0x00468C30u;   /* terrain writers 0x468C30/0x468F00 pass aux 0 */
        draw(NULL, 0u);
        assert(g1_hd_asset_pack_hits() == 1u && g1_hd_asset_pack_misses() == 0u && g1_hd_asset_pack_rejects() == 0u);
        assert(block(10u, 10u, 0) == 0x31u && block(11u, 10u, 3) == 0x38u);
        assert(block(10u, 11u, 2) == 0x3Bu && block(10u, 11u, 3) == 0x3Cu);
        assert(g1_hd_asset_pack_lookup_blocks() == 4u);
    } else if (!strcmp(argv[1], "miss") || !strcmp(argv[1], "reject")) {
        draw(NULL, 0u);
        if (!strcmp(argv[1], "miss")) assert(g1_hd_asset_pack_misses() == 1u && g1_hd_asset_pack_rejects() == 0u &&
                                             g1_hd_asset_pack_pal_misses() == 0u);   /* the pal directory exists, only the file is absent */
        else assert(g1_hd_asset_pack_rejects() == 1u && g1_hd_asset_pack_misses() == 0u);
        assert(g1_hd_asset_pack_hits() == 0u);
        assert(block(10u, 10u, 0) == 5u && block(11u, 11u, 3) == 5u);   /* Scale2x of a flat sprite */
        assert(g1_hd_asset_pack_lookup_blocks() == 0u);
    } else if (!strcmp(argv[1], "cbytes")) {
        BYTE frame[4] = {5u, 5u, 5u, 5u}, written[4] = {1u, 1u, 1u, 0u};
        g1_hd_asset_reset();
        assert(g1_hd_asset_identity_cache_bytes() == 0u);
        assert(g1_hd_asset_begin(source, writer_id, 2u, 2u, 10, 10) == TRUE);
        assert(g1_hd_asset_bind_identity_frame(frame, 2u, written, 2u, 2u, 2u) == TRUE);
        assert(g1_hd_asset_identity_cache_bytes() == 6u * 2u * 2u);          /* identity + mask (2wh) + HD frame (4wh) */
        assert(g1_hd_asset_begin(source + 16, writer_id, 2u, 2u, 10, 10) == TRUE);
        assert(g1_hd_asset_bind_identity_frame(frame, 2u, written, 2u, 2u, 2u) == TRUE);
        assert(g1_hd_asset_identity_keys() == 2u);
        assert(g1_hd_asset_identity_cache_bytes() == 2u * 6u * 2u * 2u);
        assert(g1_hd_asset_cache_insert_bytes() * 3u == g1_hd_asset_identity_cache_bytes() * 1u);   /* refresh 0: 3x the insert bytes */
        g1_hd_asset_reset();
        assert(g1_hd_asset_identity_cache_bytes() == 0u);
    } else if (!strcmp(argv[1], "env_limit")) {         /* SYW2_G1_HD_KEY_LIMIT=2 lowers the table; argv[3] = expected limit */
        BYTE frame[4] = {5u, 5u, 5u, 5u}, written[4] = {1u, 1u, 1u, 0u};
        DWORD limit = (DWORD)atoi(argv[3]), index;
        g1_hd_asset_reset();
        for (index = 0u; index < 3u; ++index) {
            assert(g1_hd_asset_begin(source + 16u * index, writer_id, 2u, 2u, 10, 10) == TRUE);
            assert(g1_hd_asset_bind_identity_frame(frame, 2u, written, 2u, 2u, 2u) == TRUE);
        }
        assert(g1_hd_asset_identity_keys() == (limit < 3u ? limit : 3u));
        assert(g1_hd_asset_identity_evictions() == (limit < 3u ? 3u - limit : 0u));
    } else if (!strcmp(argv[1], "evict_one")) {         /* one slot, held by the current key: it is spared, the request is invalid */
        BYTE frame[4] = {5u, 5u, 5u, 5u}, written[4] = {1u, 1u, 1u, 0u};
        g1_hd_asset_reset();
        assert(g1_hd_asset_begin(source, writer_id, 2u, 2u, 10, 10) == TRUE);
        assert(g1_hd_asset_bind_identity_frame(frame, 2u, written, 2u, 2u, 2u) == TRUE);
        assert(g1_hd_asset_begin(source + 16, writer_id, 2u, 2u, 10, 10) == FALSE);
        assert(g1_hd_asset_identity_evictions() == 0u && g1_hd_asset_identity_invalid_sources() == 1u);
        assert(g1_hd_asset_begin(source, writer_id, 2u, 2u, 10, 10) == TRUE && g1_hd_asset_needs_identity_frame() == FALSE);
    } else if (!strcmp(argv[1], "evict_keys") || !strcmp(argv[1], "evict_full") || !strcmp(argv[1], "evict_bytes")) {
        BYTE frame[4] = {5u, 5u, 5u, 5u}, written[4] = {1u, 1u, 1u, 0u};
        const BYTE *s0 = source, *s1 = source + 16, *s2 = source + 32, *s3 = source + 48;
#define BIND(src) do { assert(g1_hd_asset_begin(src, writer_id, 2u, 2u, 10, 10) == TRUE); \
                       assert(g1_hd_asset_bind_identity_frame(frame, 2u, written, 2u, 2u, 2u) == TRUE); } while (0)
        g1_hd_asset_reset();
        BIND(s0); BIND(s1); BIND(s2);
        if (strcmp(argv[1], "evict_bytes")) assert(g1_hd_asset_identity_keys() == 3u && g1_hd_asset_identity_evictions() == 0u);
        if (!strcmp(argv[1], "evict_bytes")) {          /* limit 60 B: two keys (24 B each) fit, the third needs room */
            assert(g1_hd_asset_identity_cache_bytes() <= 60u && g1_hd_asset_identity_evictions() == 1u);
            assert(g1_hd_asset_identity_invalid_sources() == 0u);
            assert(g1_hd_asset_begin(s0, writer_id, 2u, 2u, 10, 10) == TRUE);    /* the oldest key lost its frames, not its identity */
            assert(g1_hd_asset_needs_identity_frame() == TRUE && g1_hd_asset_identity_keys() == 3u);
            assert(g1_hd_asset_bind_identity_frame(frame, 2u, written, 2u, 2u, 2u) == TRUE);
            assert(g1_hd_asset_identity_cache_bytes() <= 60u && g1_hd_asset_identity_evictions() == 2u);
            assert(block(10u, 10u, 0) == 0x31u && g1_hd_asset_pack_rejects() == 0u);   /* s0 rebuilt from its pack file, not Scale2x */
        } else if (!strcmp(argv[1], "evict_full")) {    /* s2 is the current key: s0, the oldest of the others, goes */
            assert(g1_hd_asset_begin(s3, writer_id, 2u, 2u, 10, 10) == TRUE);
            assert(g1_hd_asset_identity_keys() == 3u && g1_hd_asset_identity_evictions() == 1u);
            assert(g1_hd_asset_begin(s2, writer_id, 2u, 2u, 10, 10) == TRUE);    /* the current key kept its frame */
            assert(g1_hd_asset_needs_identity_frame() == FALSE && g1_hd_asset_identity_evictions() == 1u);
        } else {
            assert(g1_hd_asset_begin(s0, writer_id, 2u, 2u, 10, 10) == TRUE);    /* touch s0: s1 is now the least recently begun */
            assert(g1_hd_asset_needs_identity_frame() == FALSE);
            BIND(s3);
            assert(g1_hd_asset_identity_keys() == 3u && g1_hd_asset_identity_evictions() == 1u);
            assert(g1_hd_asset_identity_invalid_sources() == 0u);
            assert(g1_hd_asset_identity_cache_bytes() == 3u * 24u);                /* 2wh + 4wh per resident key */
            assert(g1_hd_asset_begin(s0, writer_id, 2u, 2u, 10, 10) == TRUE);    /* survivor: still bound */
            assert(g1_hd_asset_needs_identity_frame() == FALSE);
            assert(g1_hd_asset_begin(s1, writer_id, 2u, 2u, 10, 10) == TRUE);    /* evicted key returns as a new key and rebinds */
            assert(g1_hd_asset_needs_identity_frame() == TRUE && g1_hd_asset_identity_evictions() == 2u);
            assert(g1_hd_asset_bind_identity_frame(frame, 2u, written, 2u, 2u, 2u) == TRUE);
            assert(g1_hd_asset_identity_cache_bytes() == 3u * 24u && g1_hd_asset_identity_invalid_sources() == 0u);
        }
#undef BIND
    } else if (!strcmp(argv[1], "lru_recency")) {       /* s0 is re-begun, then another key becomes current: s1 (not s0) is the victim */
        BYTE frame[4] = {5u, 5u, 5u, 5u}, written[4] = {1u, 1u, 1u, 0u};
        const BYTE *s0 = source, *s1 = source + 16, *s2 = source + 32, *s3 = source + 48;
#define BIND(src) do { assert(g1_hd_asset_begin(src, writer_id, 2u, 2u, 10, 10) == TRUE); \
                       assert(g1_hd_asset_bind_identity_frame(frame, 2u, written, 2u, 2u, 2u) == TRUE); } while (0)
        g1_hd_asset_reset();
        BIND(s0); BIND(s1); BIND(s2);
        assert(g1_hd_asset_begin(s0, writer_id, 2u, 2u, 10, 10) == TRUE && g1_hd_asset_needs_identity_frame() == FALSE);
        assert(g1_hd_asset_begin(s2, writer_id, 2u, 2u, 10, 10) == TRUE && g1_hd_asset_needs_identity_frame() == FALSE);
        BIND(s3);                                       /* current key s2 is spared; of s0 (re-begun) and s1, s1 is older */
        assert(g1_hd_asset_identity_keys() == 3u && g1_hd_asset_identity_evictions() == 1u);
        assert(g1_hd_asset_begin(s0, writer_id, 2u, 2u, 10, 10) == TRUE && g1_hd_asset_needs_identity_frame() == FALSE);
        assert(g1_hd_asset_identity_evictions() == 1u);
        assert(g1_hd_asset_begin(s1, writer_id, 2u, 2u, 10, 10) == TRUE && g1_hd_asset_needs_identity_frame() == TRUE);
        assert(g1_hd_asset_identity_evictions() == 2u);
#undef BIND
    } else if (!strcmp(argv[1], "build_self")) {        /* limit 20 B: the 8 B identity binds, its 16 B HD frame cannot fit beside it */
        BYTE frame[4] = {5u, 5u, 5u, 5u}, written[4] = {1u, 1u, 1u, 0u};
        g1_hd_asset_reset();
        assert(g1_hd_asset_begin(source, writer_id, 2u, 2u, 10, 10) == TRUE);
        assert(g1_hd_asset_bind_identity_frame(frame, 2u, written, 2u, 2u, 2u) == FALSE);   /* no other key to evict: fail, not evict itself */
        assert(g1_hd_asset_identity_invalid_sources() == 1u && g1_hd_asset_identity_cache_bytes() == 0u);
        assert(g1_hd_asset_identity_evictions() == 0u && g1_hd_asset_identity_keys() == 1u);
        assert(g1_hd_asset_begin(source, writer_id, 2u, 2u, 10, 10) == TRUE && g1_hd_asset_needs_identity_frame() == TRUE);
    } else if (!strcmp(argv[1], "aux")) {
        BYTE aux[4] = {1u, 2u, 3u, 4u};
        draw(aux, 99u);
        assert(g1_hd_asset_pack_skipped_aux() == 1u && g1_hd_asset_pack_hits() == 0u);
        assert(block(10u, 10u, 0) == 5u);
    } else if (!strcmp(argv[1], "tinted_hit") || !strcmp(argv[1], "tinted_clip_hit")) {
        tinted(!strcmp(argv[1], "tinted_hit") ? 0x00466EA0u : 0x00466540u, 1, 0);
        assert(g1_hd_asset_pack_hits() == 1u && g1_hd_asset_pack_lut_hits() == 1u);
        assert(g1_hd_asset_pack_skipped_aux() == 0u && g1_hd_asset_pack_lut_rejects() == 0u);
        assert(g1_hd_asset_pack_rejects() == 0u && g1_hd_asset_pack_lut_nonidentity() == 1u);
        assert(g1_hd_asset_pack_lut_key_color() == 0u);
        assert(block(10u, 10u, 0) == 0x71u && block(11u, 10u, 3) == 0x78u);       /* lut[pack index] */
        assert(block(10u, 11u, 2) == 0x7Bu && block(10u, 11u, 3) == 0x7Cu);
        assert(g1_hd_asset_pack_lookup_blocks() == 4u);
    } else if (!strcmp(argv[1], "flip_hit")) {
        assert(g1_hd_asset_flip_key_path() == TRUE);
        flip_draw(1);
        assert(g1_hd_asset_pack_hits() == 1u && g1_hd_asset_pack_lut_hits() == 1u && g1_hd_asset_pack_rejects() == 0u);
        assert(g1_hd_asset_pack_flip_hits() == 1u && g1_hd_asset_pack_flip_misses() == 0u && g1_hd_asset_pack_flip_rejects() == 0u);
        /* file rows 31 32 35 36 / 33 34 37 38 / 39 3A FE FE / 3B 3C FE FE, each mirrored, then lut[] = +0x40 */
        assert(block(10u, 10u, 0) == 0x76u && block(10u, 10u, 1) == 0x75u && block(11u, 10u, 0) == 0x72u && block(11u, 10u, 1) == 0x71u);
        assert(block(10u, 10u, 2) == 0x78u && block(10u, 10u, 3) == 0x77u && block(11u, 10u, 2) == 0x74u && block(11u, 10u, 3) == 0x73u);
        assert(block(10u, 11u, 0) == 0xFEu && block(10u, 11u, 3) == 0xFEu);                  /* the unwritten pixel stays key */
        assert(block(11u, 11u, 0) == 0x7Au && block(11u, 11u, 1) == 0x79u && block(11u, 11u, 2) == 0x7Cu && block(11u, 11u, 3) == 0x7Bu);
        assert(g1_hd_asset_pack_lookup_blocks() == 14u);               /* one per block() call above */
    } else if (!strncmp(argv[1], "ext_", 4)) {             /* H-HDN0: extended (prefix length) pack names; source[i] = i */
        const char *name = argv[1] + 4;
        draw(NULL, 0u);
        if (!strcmp(name, "hit")) {
            assert(g1_hd_asset_pack_hits() == 1u && g1_hd_asset_pack_misses() == 0u && g1_hd_asset_pack_rejects() == 0u);
            assert(g1_hd_asset_pack_ext_hits() == 1u && g1_hd_asset_pack_ext_misses() == 0u && g1_hd_asset_pack_ext_rejects() == 0u);
            assert(block(10u, 10u, 0) == 0x31u && block(11u, 10u, 3) == 0x38u && g1_hd_asset_pack_lookup_blocks() == 2u);
        } else if (!strcmp(name, "base_wins") || !strcmp(name, "off")) {
            assert(g1_hd_asset_pack_ext_hits() == 0u && g1_hd_asset_pack_ext_misses() == 0u && g1_hd_asset_pack_ext_rejects() == 0u);
            if (!strcmp(name, "off")) assert(g1_hd_asset_pack_misses() == 1u && g1_hd_asset_pack_hits() == 0u);
            else assert(g1_hd_asset_pack_hits() == 1u && block(10u, 10u, 0) == 0x31u);
        } else if (!strcmp(name, "no_marker")) {
            assert(g1_hd_asset_pack_misses() == 1u && g1_hd_asset_pack_hits() == 0u);
            assert(g1_hd_asset_pack_ext_hits() == 0u && g1_hd_asset_pack_ext_misses() == 0u && g1_hd_asset_pack_ext_rejects() == 0u);
            assert(block(10u, 10u, 0) == 5u);
        } else if (!strcmp(name, "no_file")) {
            assert(g1_hd_asset_pack_misses() == 1u && g1_hd_asset_pack_ext_misses() == 1u);
            assert(g1_hd_asset_pack_ext_hits() == 0u && g1_hd_asset_pack_ext_rejects() == 0u && block(10u, 10u, 0) == 5u);
        } else if (!strcmp(name, "bad_marker")) {                 /* unusable marker: a miss, counted as an ext reject */
            assert(g1_hd_asset_pack_misses() == 1u && g1_hd_asset_pack_hits() == 0u && g1_hd_asset_pack_ext_rejects() == 1u);
            assert(g1_hd_asset_pack_ext_hits() == 0u && g1_hd_asset_pack_ext_misses() == 0u && block(10u, 10u, 0) == 5u);
        } else if (!strcmp(name, "bad_frame")) {                  /* the extended file exists but its silhouette is wrong */
            assert(g1_hd_asset_pack_rejects() == 1u && g1_hd_asset_pack_hits() == 0u && g1_hd_asset_pack_ext_rejects() == 1u);
            assert(g1_hd_asset_pack_ext_hits() == 0u && g1_hd_asset_pack_ext_misses() == 0u && block(10u, 10u, 0) == 5u);
        } else {
            return 2;
        }
    } else if (!strcmp(argv[1], "extx_stale")) {           /* H-HDB2 B2-0 (lap1193 c4): a key that never reads a pack file does not reuse the last key's ext state */
        BYTE frame[4] = {5u, 5u, 5u, 5u}, written[4] = {1u, 1u, 1u, 0u}, aux[4] = {1u, 2u, 3u, 4u};
        g1_hd_asset_reset();
        assert(g1_hd_asset_begin(source, writer_id, 2u, 2u, 10, 10) == TRUE);
        assert(g1_hd_asset_bind_identity_frame(frame, 2u, written, 2u, 2u, 2u) == TRUE);
        assert(g1_hd_asset_pack_ext_rejects() == 1u && g1_hd_asset_pack_misses() == 1u);       /* the unusable marker */
        assert(g1_hd_asset_begin_with_aux(source + 16, writer_id, aux, 99u, 2u, 2u, 10, 10) == TRUE);
        assert(g1_hd_asset_bind_identity_frame(frame, 2u, written, 2u, 2u, 2u) == TRUE);
        assert(g1_hd_asset_pack_skipped_aux() == 1u);                                           /* no pack read for this key */
        assert(g1_hd_asset_pack_ext_rejects() == 1u && g1_hd_asset_pack_ext_hits() == 0u && g1_hd_asset_pack_ext_misses() == 0u);
    } else if (!strcmp(argv[1], "extx_refresh")) {         /* H-HDB2 B2-0 (lap1193 c9): a re-read of a HIT key counts nothing; argv[3] = its marker file */
        FILE *marker;
        draw(NULL, 0u);
        assert(g1_hd_asset_pack_ext_hits() == 1u && g1_hd_asset_pack_hits() == 1u && g1_hd_asset_pack_ext_rejects() == 0u);
        marker = fopen(argv[3], "wb");
        assert(marker != NULL && fwrite("\x01\x02\x03", 1u, 3u, marker) == 3u);                 /* now unusable: the refresh read ends in an ext reject */
        fclose(marker);
        refresh_key(NULL, 0u, 1u);
        assert(g1_hd_asset_pack_ext_hits() == 1u && g1_hd_asset_pack_ext_rejects() == 0u && g1_hd_asset_pack_ext_misses() == 0u);
        assert(g1_hd_asset_pack_hits() == 1u && g1_hd_asset_pack_misses() == 0u);              /* the first-try counters stay too */
    } else if (!strncmp(argv[1], "blendflip_", 10)) {      /* H-HDB3: 0x467FD0 / 0x4685C0, no aux, pack file mirrored, blend counters */
        BYTE frame[4] = {5u, 5u, 0u, 5u}, written[4] = {1u, 1u, 0u, 1u};   /* the flipped silhouette, as in flip_draw */
        DWORD pw = 0u, ph = 0u;
        const BYTE *pack;
        writer_id = !strcmp(argv[1], "blendflip_4685C0") ? 0x004685C0u : !strcmp(argv[1], "blendflip_plain") ? 0x00467580u : 0x00467FD0u;
        if (!strcmp(argv[1], "blendflip_flip_off")) {
            assert(g1_hd_asset_blend_key_path() == TRUE && g1_hd_asset_blend_flip_key_path() == FALSE);
            return 0;
        }
        if (!strcmp(argv[1], "blendflip_blend_off")) {
            assert(g1_hd_asset_blend_key_path() == FALSE && g1_hd_asset_blend_flip_key_path() == FALSE &&
                   g1_hd_asset_flip_key_path() == TRUE);
            return 0;
        }
        assert(g1_hd_asset_blend_flip_key_path() == TRUE);
        g1_hd_asset_reset();
        assert(g1_hd_asset_begin(source, writer_id, 2u, 2u, 10, 10) == TRUE);
        assert(g1_hd_asset_bind_identity_frame(frame, 2u, written, 2u, 2u, 2u) == TRUE);
        pack = g1_hd_asset_current_pack_frame(&pw, &ph);
        if (!strcmp(argv[1], "blendflip_plain")) {         /* a writer that does not mirror sees the flipped mask disagree with the file */
            assert(pack == NULL && g1_hd_asset_pack_blend_hits() == 0u && g1_hd_asset_pack_blend_rejects() == 1u && g1_hd_asset_pack_rejects() == 1u);
            return 0;
        }
        assert(pack != NULL && pw == 4u && ph == 4u);
        assert(pack[0] == 0x36u && pack[1] == 0x35u && pack[2] == 0x32u && pack[3] == 0x31u);   /* row 0 of _GOOD, mirrored */
        assert(pack[4] == 0x38u && pack[7] == 0x33u && pack[8] == 0xFEu && pack[11] == 0x39u);
        assert(g1_hd_asset_pack_blend_hits() == 1u && g1_hd_asset_pack_blend_misses() == 0u && g1_hd_asset_pack_blend_rejects() == 0u);
        assert(g1_hd_asset_pack_flip_hits() == 0u && g1_hd_asset_pack_lut_hits() == 0u);       /* the tinted/flip LUT path is not used */
    } else if (!strcmp(argv[1], "blendclip_hit")) {        /* H-HDB2: 0x467B00 counts its pack hit as a blend writer */
        DWORD pw = 0u, ph = 0u;
        writer_id = 0x00467B00u;
        draw(NULL, 0u);
        assert(g1_hd_asset_current_pack_frame(&pw, &ph) != NULL && pw == 4u && ph == 4u);
        assert(g1_hd_asset_pack_blend_hits() == 1u && g1_hd_asset_pack_blend_misses() == 0u && g1_hd_asset_pack_blend_rejects() == 0u);
    } else if (!strncmp(argv[1], "blend_", 6)) {           /* H-HDB0: 0x4672E0, no aux, plain pack file + blend counters */
        DWORD pw = 0u, ph = 0u;
        writer_id = 0x004672E0u;
        if (!strcmp(argv[1], "blend_off")) {
            assert(g1_hd_asset_blend_key_path() == FALSE && g1_hd_asset_flip_key_path() == TRUE);
        } else {
            assert(g1_hd_asset_blend_key_path() == TRUE);
            draw(NULL, 0u);
            if (!strcmp(argv[1], "blend_hit")) {
                const BYTE *frame = g1_hd_asset_current_pack_frame(&pw, &ph);
                assert(frame != NULL && pw == 4u && ph == 4u && frame[0] == 0x31u && frame[15] == 0xFEu);
                assert(g1_hd_asset_pack_blend_hits() == 1u && g1_hd_asset_pack_blend_misses() == 0u &&
                       g1_hd_asset_pack_blend_rejects() == 0u);
                g1_hd_asset_end();
                assert(g1_hd_asset_current_pack_frame(&pw, &ph) == NULL);   /* only while the key is current */
            } else {                                                       /* miss/reject: Scale2x frame is not a pack frame */
                assert(g1_hd_asset_current_pack_frame(&pw, &ph) == NULL);
                assert(g1_hd_asset_pack_blend_hits() == 0u);
                assert(g1_hd_asset_pack_blend_misses() == (strcmp(argv[1], "blend_miss") ? 0u : 1u));
                assert(g1_hd_asset_pack_blend_rejects() == (strcmp(argv[1], "blend_miss") ? 1u : 0u));
            }
            assert(g1_hd_asset_pack_flip_hits() == 0u && g1_hd_asset_pack_flip_misses() == 0u);   /* its own counters */
        }
    } else if (!strcmp(argv[1], "flip_miss")) {
        flip_draw(1);
        assert(g1_hd_asset_pack_misses() == 1u && g1_hd_asset_pack_flip_misses() == 1u && g1_hd_asset_pack_flip_hits() == 0u);
        assert(block(10u, 10u, 0) == 5u && block(10u, 11u, 0) != 5u);                           /* Scale2x of the mirrored mask */
    } else if (!strcmp(argv[1], "flip_bad_digest")) {
        flip_draw(0);
        assert(g1_hd_asset_pack_lut_rejects() == 1u && g1_hd_asset_pack_flip_rejects() == 1u && g1_hd_asset_pack_hits() == 0u);
        assert(g1_hd_asset_pack_lookup_blocks() == 0u && block(10u, 10u, 0) == 5u);
    } else if (!strcmp(argv[1], "flip_off")) {
        assert(g1_hd_asset_flip_key_path() == FALSE);
        flip_draw(1);
        assert(g1_hd_asset_pack_skipped_aux() == 1u && g1_hd_asset_pack_hits() == 0u && g1_hd_asset_pack_lut_hits() == 0u);
        assert(g1_hd_asset_pack_flip_hits() == 0u && g1_hd_asset_pack_flip_rejects() == 0u);
        assert(block(10u, 10u, 0) == 5u);
    } else if (!strcmp(argv[1], "flip_writers_apart")) {  /* same RLE and table through both flip writers: two keys, both hit */
        BYTE lut[256], frame[4] = {5u, 5u, 0u, 5u}, written[4] = {1u, 1u, 0u, 1u};
        DWORD index;
        for (index = 0u; index < 256u; ++index) lut[index] = (BYTE)(index + 0x40u);
        g1_hd_asset_reset();
        for (index = 0u; index < 2u; ++index) {
            assert(g1_hd_asset_begin_with_aux(source, index ? 0x00466BE0u : 0x00466B50u, lut, fnv(lut, 256u), 2u, 2u, 10, 10) == TRUE);
            assert(g1_hd_asset_bind_identity_frame(frame, 2u, written, 2u, 2u, 2u) == TRUE);
        }
        assert(g1_hd_asset_identity_keys() == 2u && g1_hd_asset_pack_flip_hits() == 2u && g1_hd_asset_pack_flip_rejects() == 0u);
    } else if (!strcmp(argv[1], "flip_tinted_independent")) {
        tinted(0x00466EA0u, 1, 0);
        assert(g1_hd_asset_pack_lut_hits() == 1u && g1_hd_asset_pack_flip_hits() == 0u && g1_hd_asset_flip_key_path() == FALSE);
        assert(block(10u, 10u, 0) == 0x71u && block(11u, 10u, 3) == 0x78u);                       /* tinted stays unflipped */
    } else if (!strcmp(argv[1], "lut_content_change")) {   /* argv[3] = writer; the same table pointer, rewritten between draws */
        DWORD writer = (DWORD)strtoul(argv[3], NULL, 16);
        int flipped = writer == 0x00468360u;
        BYTE table[256], at_a, at_b;
        DWORD index;
        g1_hd_asset_reset();
        for (index = 0u; index < 256u; ++index) table[index] = (BYTE)(index + 0x40u);
        aux_draw_keep_keys(writer, table, flipped);
        assert(g1_hd_asset_pack_hits() == 1u && g1_hd_asset_pack_lut_hits() == 1u && g1_hd_asset_identity_keys() == 1u);
        at_a = block(10u, 10u, 0);
        for (index = 0u; index < 256u; ++index) table[index] = (BYTE)(index + 0x50u);          /* the game rewrote the table in place */
        aux_draw_keep_keys(writer, table, flipped);
        assert(g1_hd_asset_identity_keys() == 2u && g1_hd_asset_pack_hits() == 2u && g1_hd_asset_pack_lut_rejects() == 0u);
        at_b = block(10u, 10u, 0);
        assert(at_b == (BYTE)(at_a + 0x10u));                                               /* the new table's colour, not the old key's */
        for (index = 0u; index < 256u; ++index) table[index] = (BYTE)(index + 0x40u);          /* back to the first table: its key returns */
        aux_draw_keep_keys(writer, table, flipped);
        assert(g1_hd_asset_identity_keys() == 2u && g1_hd_asset_pack_hits() == 2u && block(10u, 10u, 0) == at_a);
    } else if (!strcmp(argv[1], "tinted_keycolor")) {
        tinted(0x00466EA0u, 1, 1);
        assert(g1_hd_asset_pack_lut_hits() == 1u && g1_hd_asset_pack_lut_key_color() == 1u);
        assert(block(10u, 10u, 0) == 0xFEu);                  /* the original writes the table's key colour too */
    } else if (!strcmp(argv[1], "tinted_bad_digest")) {
        tinted(0x00466EA0u, 0, 0);
        assert(g1_hd_asset_pack_lut_rejects() == 1u && g1_hd_asset_pack_lut_hits() == 0u);
        assert(g1_hd_asset_pack_hits() == 0u && g1_hd_asset_pack_rejects() == 0u);
        assert(block(10u, 10u, 0) == 5u && g1_hd_asset_pack_lookup_blocks() == 0u);   /* Scale2x */
    } else if (!strcmp(argv[1], "tinted_off") || !strcmp(argv[1], "checker_writer")) {
        tinted(!strcmp(argv[1], "tinted_off") ? 0x00466EA0u : 0x00468E10u, 1, 0);
        assert(g1_hd_asset_pack_skipped_aux() == 1u && g1_hd_asset_pack_hits() == 0u);
        assert(g1_hd_asset_pack_lut_hits() == 0u && g1_hd_asset_pack_lut_rejects() == 0u);
        assert(block(10u, 10u, 0) == 5u);
    } else if (!strcmp(argv[1], "tinted_miss")) {
        tinted(0x00466EA0u, 1, 0);
        assert(g1_hd_asset_pack_misses() == 1u && g1_hd_asset_pack_lut_hits() == 0u);
        assert(block(10u, 10u, 0) == 5u);
    } else if (!strcmp(argv[1], "refresh_plain")) {
        draw(NULL, 0u);
        assert(g1_hd_asset_pack_hits() == 1u && block(10u, 10u, 0) == 0x31u);
        refresh_key(NULL, 0u, 1u);
        assert(g1_hd_asset_pack_hits() == 1u && g1_hd_asset_pack_rejects() == 0u);
        assert(block(10u, 10u, 0) == 0x31u && block(11u, 10u, 3) == 0x38u);   /* a plain key re-applies its pack */
    } else if (!strcmp(argv[1], "shade_evict_bytes")) {      /* byte pressure drops a shade key's frames, not its shade copies */
        BYTE frame[4] = {5u, 5u, 5u, 5u}, written[4] = {1u, 1u, 1u, 0u};
        fake_tables(0);
        shade_draw(0x00468CC0u, 1, 0, 0);
        assert(g1_hd_asset_pack_shade_hits() == 1u && block(10u, 10u, 0) == shade_f(0x31u, 3u));
        assert(g1_hd_asset_begin(source + 32, 7u, 2u, 2u, 10, 10) == TRUE);
        assert(g1_hd_asset_bind_identity_frame(frame, 2u, written, 2u, 2u, 2u) == TRUE);
        assert(g1_hd_asset_identity_evictions() == 1u);                                    /* the shade key's frames went */
        assert(g1_hd_asset_begin_with_aux(source, 0x00468CC0u, shade_map, fnv(shade_map, 4u), 2u, 2u, 10, 10) == TRUE);
        assert(g1_hd_asset_needs_identity_frame() == TRUE);
        {   BYTE shaded[4] = {shade_f(0x11u, shade_map[0]), shade_f(0x12u, shade_map[1]), shade_f(0x13u, shade_map[2]), 0u};
            assert(g1_hd_asset_bind_identity_frame(shaded, 2u, written, 2u, 2u, 2u) == TRUE); }
        assert(block(10u, 10u, 0) == shade_f(0x31u, 3u));                                  /* pack + shade LUT again */
        assert(g1_hd_asset_pack_shade_hits() == 1u && g1_hd_asset_pack_shade_rejects() == 0u);
    } else if (!strcmp(argv[1], "shade_refresh")) {
        DWORD pack_blocks;
        fake_tables(0);
        shade_draw(0x00468CC0u, 1, 0, 0);
        assert(g1_hd_asset_pack_shade_hits() == 1u && block(10u, 10u, 0) == shade_f(0x31u, 3u));
        pack_blocks = g1_hd_asset_pack_lookup_blocks();
        writer_id = 0x00468CC0u;
        refresh_key(shade_map, fnv(shade_map, 4u), 1u);
        assert(block(10u, 10u, 0) == 7u && block(11u, 10u, 3) == 7u);          /* new identity, Scale2x: no stale LUT */
        assert(g1_hd_asset_pack_shade_rejects() == 1u && g1_hd_asset_pack_shade_rejects_by_reason(5u) == 1u);
        assert(g1_hd_asset_pack_hits() == 1u && g1_hd_asset_pack_shade_hits() == 1u);
        assert(g1_hd_asset_pack_lookup_blocks() == pack_blocks);                /* the new build read no pack pixel */
        refresh_key(shade_map, fnv(shade_map, 4u), 2u);                           /* later refreshes stay on Scale2x and count once */
        assert(g1_hd_asset_pack_shade_rejects() == 1u && block(10u, 10u, 0) == 7u);
    } else if (!strncmp(argv[1], "shade_", 6)) {
        const char *name = argv[1] + 6;
        DWORD writer = !strcmp(name, "clip_hit") ? 0x004690A0u : !strcmp(name, "checker") ? 0x00468E10u : 0x00468CC0u;
        fake_tables(!strcmp(name, "bad_palette"));
        if (!strcmp(name, "bad_level")) shade_map[0] = 64u;
        shade_draw(writer, strcmp(name, "bad_digest") != 0, !strcmp(name, "selfcheck"), !strcmp(name, "bad_source"));
        if (!strcmp(name, "hit") || !strcmp(name, "clip_hit")) {
            static const BYTE pack[16] = {0x31, 0x32, 0x35, 0x36, 0x33, 0x34, 0x37, 0x38,
                                          0x39, 0x3A, 0xFE, 0xFE, 0x3B, 0x3C, 0xFE, 0xFE};
            DWORD px, cell;
            const DWORD level[3] = {3u, 5u, 3u};
            const DWORD at[3][2] = {{10u, 10u}, {11u, 10u}, {10u, 11u}};
            assert(g1_hd_asset_pack_hits() == 1u && g1_hd_asset_pack_shade_hits() == 1u);
            assert(g1_hd_asset_pack_shade_rejects() == 0u && g1_hd_asset_pack_rejects() == 0u);
            assert(g1_hd_asset_pack_skipped_aux() == 0u && g1_hd_asset_pack_lut_hits() == 0u);
            assert(g1_hd_asset_pack_shade_selfcheck_pixels() == 3u);
            assert(g1_hd_asset_pack_shade_multi_keys() == 1u);                 /* levels 3 and 5 */
            assert(g1_hd_asset_pack_shade_lut_bytes() == 2u * 256u);
            assert(g1_hd_asset_pack_shade_key_color() == 0u);
            for (px = 0u; px < 3u; ++px)
                for (cell = 0u; cell < 4u; ++cell) {
                    BYTE original = pack[(px == 1u ? 2u : 0u) + (px == 2u ? 8u : 0u) + (cell & 1u) + (cell >> 1) * 4u];
                    assert(block(at[px][0], at[px][1], (int)cell) == shade_f(original, level[px]));
                }
            assert(g1_hd_asset_pack_lookup_blocks() == 12u);
        } else if (!strcmp(name, "off") || !strcmp(name, "checker")) {
            assert(g1_hd_asset_pack_skipped_aux() == 1u && g1_hd_asset_pack_hits() == 0u);
            assert(g1_hd_asset_pack_shade_hits() == 0u && g1_hd_asset_pack_shade_rejects() == 0u);
            assert(block(10u, 10u, 0) != 0x31u);
        } else if (!strcmp(name, "miss")) {
            assert(g1_hd_asset_pack_misses() == 1u && g1_hd_asset_pack_shade_hits() == 0u);
            assert(g1_hd_asset_pack_shade_rejects() == 0u && block(10u, 10u, 0) != 0x31u);
        } else {
            DWORD reason = !strcmp(name, "bad_digest") ? 0u : !strcmp(name, "bad_palette") || !strcmp(name, "bad_level") ? 2u :
                           !strcmp(name, "bad_source") ? 3u : 4u;
            DWORD index;
            assert(g1_hd_asset_pack_shade_rejects() == 1u && g1_hd_asset_pack_shade_rejects_by_reason(reason) == 1u);
            for (index = 0u; index < 5u; ++index)
                if (index != reason) assert(g1_hd_asset_pack_shade_rejects_by_reason(index) == 0u);
            assert(g1_hd_asset_pack_shade_hits() == 0u && g1_hd_asset_pack_hits() == 0u);
            assert(block(10u, 10u, 0) != 0x31u && g1_hd_asset_pack_lookup_blocks() == 0u);   /* Scale2x */
        }
    } else if (!strncmp(argv[1], "pal_", 4)) {
        const char *name = argv[1] + 4;
        if (!strcmp(name, "other") || !strcmp(name, "root") || !strcmp(name, "absent")) {
            draw(NULL, 0u);          /* the screen palette (all zero) has no directory: a frame for another palette or in the root is never read */
            assert(g1_hd_asset_pack_misses() == 1u && g1_hd_asset_pack_hits() == 0u && g1_hd_asset_pack_rejects() == 0u);
            assert(g1_hd_asset_pack_pal_misses() == 1u);
            assert(block(10u, 10u, 0) == 5u && g1_hd_asset_pack_lookup_blocks() == 0u);   /* Scale2x */
        } else if (!strcmp(name, "two")) {
            draw(NULL, 0u);
            assert(g1_hd_asset_pack_hits() == 1u && block(10u, 10u, 0) == 0x31u);
            brighten_screen(9u);                                   /* a different palette: its own directory, its own picture */
            draw(NULL, 0u);
            assert(g1_hd_asset_pack_hits() == 1u && block(10u, 10u, 0) == 0x41u);
        } else if (!strcmp(name, "flags_ignored")) {
            g_fake_renderer[0x15A0u + 3u] = 4u;                  /* PALETTEENTRY.peFlags is not part of the palette */
            draw(NULL, 0u);
            assert(g1_hd_asset_pack_hits() == 1u && block(10u, 10u, 0) == 0x31u);
        } else if (!strncmp(name, "family", 6)) {
            DWORD index, over = !strcmp(name, "family_tolerance") ? 8u : !strcmp(name, "family_over") ? 9u : 0u;
            fake_tables(0);
            for (index = 0u; index < 256u; ++index) {          /* the game darkened start*4 by half, then by a quarter */
                DWORD component;
                for (component = 0u; component < 3u; ++component)
                    g_fake_renderer[0x15A0u + index * 4u + component] =
                        (BYTE)(((BYTE)(g_fake_renderer[0x419A0u + index * 3u + component] << 2)) >> 1);
            }
            for (index = 0u; index < over; ++index) g_fake_renderer[0x15A0u + (100u + index) * 4u + 1u] = 255u;
            draw(NULL, 0u);
            if (!strcmp(name, "family_over")) {
                assert(g1_hd_asset_palette_family() == 0u);   /* 9 brighter entries: the exact palette, which has no directory */
                assert(g1_hd_asset_pack_misses() == 1u && g1_hd_asset_pack_pal_misses() == 1u && g1_hd_asset_pack_hits() == 0u);
                return 0;
            }
            assert(g1_hd_asset_palette_family() == 1u);
            assert(g1_hd_asset_pack_hits() == 1u && g1_hd_asset_pack_pal_misses() == 0u && block(10u, 10u, 0) == 0x31u);
            if (!strcmp(name, "family")) {
                for (index = 0u; index < 256u * 4u; ++index)    /* darker again: same directory, same keys, no change */
                    if ((index & 3u) != 3u) g_fake_renderer[0x15A0u + index] >>= 1;
                draw(NULL, 0u);
                assert(g1_hd_asset_palette_family() == 1u && g1_hd_asset_pack_hits() == 1u);
                assert(g1_hd_asset_palette_changes() == 0u);
            }
        } else if (!strcmp(name, "keys")) {
            DWORD before;
            draw(NULL, 0u);
            before = g1_hd_asset_identity_keys();
            brighten_screen(1u);
            assert(g1_hd_asset_begin(source, writer_id, 2u, 2u, 10, 10) == TRUE);   /* same sprite, new palette: a new key */
            assert(g1_hd_asset_identity_keys() == before + 1u && g1_hd_asset_palette_changes() == 1u);
        } else {
            return 2;
        }
    } else if (!strncmp(argv[1], "fs_", 3)) {
        const char *name = argv[1] + 3;
        const BYTE *frame = g1_hd_asset_fullscreen_frame(0x12345678u, 800u, 600u);
        if (!strcmp(name, "hit")) {
            assert(frame != NULL && frame[0] == 0u && frame[1000] == (BYTE)(1000u % 251u) && frame[1919999] == (BYTE)(1919999u % 251u));
            assert(g1_hd_asset_fullscreen_frame(0x12345678u, 800u, 600u) == frame);       /* cached: one file read */
            assert(g1_hd_asset_fullscreen_hits() == 2u && g1_hd_asset_fullscreen_loads() == 1u);
            assert(g1_hd_asset_fullscreen_misses() == 0u && g1_hd_asset_fullscreen_rejects() == 0u);
            assert(g1_hd_asset_fullscreen_frame(0x12345679u, 800u, 600u) == NULL);       /* another picture: its own name */
            assert(g1_hd_asset_fullscreen_misses() == 1u);
            assert(g1_hd_asset_fullscreen_frame(0x12345678u, 800u, 600u) == frame);       /* a miss keeps the cached frame */
        } else if (!strcmp(name, "miss")) {
            assert(frame == NULL && g1_hd_asset_fullscreen_frame(0x12345678u, 800u, 600u) == NULL);
            assert(g1_hd_asset_fullscreen_misses() == 2u && g1_hd_asset_fullscreen_hits() == 0u);
            assert(g1_hd_asset_fullscreen_loads() == 0u && g1_hd_asset_fullscreen_rejects() == 0u);
        } else if (!strcmp(name, "reject")) {
            assert(frame == NULL);
            assert(g1_hd_asset_fullscreen_rejects() == 1u && g1_hd_asset_fullscreen_hits() == 0u);
            assert(g1_hd_asset_fullscreen_misses() == 0u && g1_hd_asset_fullscreen_loads() == 0u);
        } else if (!strcmp(name, "pal_other")) {
            assert(frame != NULL);
            brighten_screen(7u);
            assert(g1_hd_asset_fullscreen_frame(0x12345678u, 800u, 600u) == NULL);   /* same picture, foreign palette */
            assert(g1_hd_asset_fullscreen_misses() == 1u && g1_hd_asset_pack_pal_misses() == 1u);
            assert(g1_hd_asset_fullscreen_frame(0x12345678u, 800u, 600u) == NULL);   /* remembered miss, no new probe */
            assert(g1_hd_asset_pack_pal_misses() == 1u && g1_hd_asset_fullscreen_misses() == 2u);
            brighten_screen(0u);
            assert(g1_hd_asset_fullscreen_frame(0x12345678u, 800u, 600u) == frame);   /* back on the cached palette */
            assert(g1_hd_asset_fullscreen_loads() == 1u);
        } else if (!strcmp(name, "off")) {
            assert(frame == NULL);
            assert(g1_hd_asset_fullscreen_hits() == 0u && g1_hd_asset_fullscreen_misses() == 0u);
            assert(g1_hd_asset_fullscreen_rejects() == 0u && g1_hd_asset_fullscreen_loads() == 0u);
        } else {
            return 2;
        }
    } else {
        return 2;
    }
    return 0;
}
"""


def _loader(tmp_path: Path, scenario: str, pack: Path, env: dict[str, str] | None = None,
            defines: tuple[str, ...] = (), extra: tuple[str, ...] = ()) -> None:
    tmp_path.mkdir(exist_ok=True)
    (tmp_path / "windows.h").write_text(_WINDOWS_SHIM, encoding="utf-8")
    (tmp_path / "fake_renderer.h").write_text("#include <windows.h>\nextern BYTE g_fake_renderer[];\n", encoding="utf-8")
    fixture = tmp_path / "loader.c"
    executable = tmp_path / "loader"
    fixture.write_text(_LOADER_C, encoding="utf-8")
    built = subprocess.run(
        ["gcc", "-std=gnu11", "-Wall", "-Wextra", "-Werror", "-Wno-unused-function", "-I", str(tmp_path), "-I", str(STUB),
         "-include", str(tmp_path / "fake_renderer.h"), "-DG1_HD_RENDERER_BASE=g_fake_renderer", *defines,
         str(fixture), str(STUB / "g1_hd_asset.c"), "-o", str(executable)],
        capture_output=True, text=True, check=False,
    )
    assert built.returncode == 0, built.stderr
    ran = subprocess.run([str(executable), scenario, f"{pack}/", *extra], capture_output=True, text=True, check=False,
                         env={**os.environ, **(env or {})})  # "/" ends the dir: no "\\" join on the host
    assert ran.returncode == 0, ran.stderr


def _pal8(entries: bytes = bytes(1024)) -> str:
    """pal8 of the fake renderer's PALETTEENTRY array (default all zero): FNV-1a over the R,G,B bytes of 256 entries."""
    value = 2166136261
    for index in range(256):
        for byte in entries[index * 4:index * 4 + 3]:
            value = ((value ^ byte) * 16777619) & 0xFFFFFFFF
    return f"{value:08x}"


def _bright(value: int) -> bytes:
    """The fake screen after brighten_screen(): R of entries 0..9 raised above the (zero) start palette."""
    entries = bytearray(1024)
    for index in range(10):
        entries[index * 4] = value
    return bytes(entries)


def _start_pal8() -> str:
    """pal8 the loader uses for a darkened start palette: the fake start palette (fake_tables) times 4, R,G,B per colour."""
    rgb = bytearray()
    for colour in range(256):
        rgb += bytes(((colour % 50) * 4 & 255, (colour * 3 % 64) * 4 & 255, ((colour * 5 + 1) % 64) * 4 & 255, 0))
    return _pal8(bytes(rgb))


def _pal_dir(pack: Path, pal8: str | None = None) -> Path:
    directory = pack / (pal8 or _pal8())
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def _digest() -> int:
    value = 2166136261
    for byte in range(128):
        value = ((value ^ byte) * 16777619) & 0xFFFFFFFF
    return value


# pixels (0,0)(1,0)(0,1) written -> opaque 2x2 blocks; (1,1) not written -> key block
_GOOD = bytes([0x31, 0x32, 0x35, 0x36,
               0x33, 0x34, 0x37, 0x38,
               0x39, 0x3A, 0xFE, 0xFE,
               0x3B, 0x3C, 0xFE, 0xFE])


def test_loader_hit_uses_pack_pixels_instead_of_scale2x(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    pack.mkdir()
    (_pal_dir(pack) / f"h{_digest():08x}_2x2.idx8").write_bytes(_GOOD)
    _loader(tmp_path, "hit", pack)


def test_loader_hit_does_not_depend_on_the_writer(tmp_path: Path) -> None:
    """Terrain tiles (writer 0x468C30, no aux) take the same pack name as UI sprites: (digest, w, h) only."""
    pack = tmp_path / "pack"
    pack.mkdir()
    (_pal_dir(pack) / f"h{_digest():08x}_2x2.idx8").write_bytes(_GOOD)
    _loader(tmp_path, "terrain", pack)


def test_loader_miss_without_a_file_falls_back_to_scale2x(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    _pal_dir(pack)
    _loader(tmp_path, "miss", pack)


def test_loader_rejects_wrong_size_and_wrong_silhouette(tmp_path: Path) -> None:
    name = f"h{_digest():08x}_2x2.idx8"
    short = tmp_path / "short"
    short.mkdir()
    (_pal_dir(short) / name).write_bytes(_GOOD[:-1])
    _loader(tmp_path / "build_short", "reject", short)
    hole = bytearray(_GOOD)
    hole[0] = 0xFE                                   # key inside a pixel the original wrote
    shaped = tmp_path / "shaped"
    shaped.mkdir()
    (_pal_dir(shaped) / name).write_bytes(bytes(hole))
    _loader(tmp_path / "build_shaped", "reject", shaped)


def test_loader_leaves_aux_keys_on_scale2x(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    pack.mkdir()
    (_pal_dir(pack) / f"h{_digest():08x}_2x2.idx8").write_bytes(_GOOD)
    _loader(tmp_path, "aux", pack)


def test_loader_only_reads_the_directory_of_the_current_screen_palette(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    _pal_dir(pack, _pal8(_bright(7)))
    (_pal_dir(pack, _pal8(_bright(7))) / f"h{_digest():08x}_2x2.idx8").write_bytes(_GOOD)
    _loader(tmp_path, "pal_other", pack)               # frame exists, but for palette 07.. and the screen has another


def test_loader_ignores_frames_in_the_pack_root_and_counts_the_missing_pal_directory(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    pack.mkdir()
    (pack / f"h{_digest():08x}_2x2.idx8").write_bytes(_GOOD)       # the old flat layout: never read again
    _loader(tmp_path / "build_root", "pal_root", pack)
    _loader(tmp_path / "build_absent", "pal_absent", pack)


def test_each_screen_palette_has_its_own_picture_for_the_same_sprite(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    other = bytes([0x41 if b != 0xFE else b for b in _GOOD])
    changed = _bright(9)
    (_pal_dir(pack) / f"h{_digest():08x}_2x2.idx8").write_bytes(_GOOD)
    (_pal_dir(pack, _pal8(changed)) / f"h{_digest():08x}_2x2.idx8").write_bytes(
        bytes([b + 0x10 if b != 0xFE else b for b in _GOOD]))
    assert other  # documents the shift used above: 0x31 + 0x10 = 0x41
    _loader(tmp_path / "build", "pal_two", pack)


def test_palette_flags_byte_is_not_part_of_the_digest(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    (_pal_dir(pack) / f"h{_digest():08x}_2x2.idx8").write_bytes(_GOOD)
    _loader(tmp_path / "build", "pal_flags_ignored", pack)


def test_a_darkened_start_palette_uses_the_start_palette_directory_and_never_changes_keys(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    (_pal_dir(pack, _start_pal8()) / f"h{_digest():08x}_2x2.idx8").write_bytes(_GOOD)
    _loader(tmp_path / "build", "pal_family", pack)


def test_up_to_eight_brighter_entries_still_belong_to_the_start_palette_family(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    (_pal_dir(pack, _start_pal8()) / f"h{_digest():08x}_2x2.idx8").write_bytes(_GOOD)
    _loader(tmp_path / "build", "pal_family_tolerance", pack)


def test_nine_brighter_entries_leave_the_family_and_use_the_exact_palette(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    (_pal_dir(pack, _start_pal8()) / f"h{_digest():08x}_2x2.idx8").write_bytes(_GOOD)
    _loader(tmp_path / "build", "pal_family_over", pack)


def test_a_palette_change_makes_new_keys_for_the_same_sprite(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    pack.mkdir()
    _loader(tmp_path / "build", "pal_keys", pack)


def test_identity_cache_bytes_is_six_times_pixels_per_bound_key(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    pack.mkdir()
    _loader(tmp_path / "build", "cbytes", pack)
    trace = (STUB / "direct_draw_trace.c").read_text(encoding="utf-8")
    assert '\\"identity_cache_bytes\\":%u,\\"identity_evictions\\":%u' in trace


def _evict_pack(tmp_path: Path) -> Path:
    pack = tmp_path / "pack"
    pack.mkdir(parents=True)
    (_pal_dir(pack) / f"h{_digest():08x}_2x2.idx8").write_bytes(_GOOD)
    return pack


def test_key_table_full_evicts_the_least_recently_begun_key_and_the_evicted_key_returns(tmp_path: Path) -> None:
    _loader(tmp_path / "build", "evict_keys", _evict_pack(tmp_path), defines=("-DG1_HD_KEY_LIMIT=3u",))


def test_key_limit_env_lowers_the_table_and_ignores_bad_values(tmp_path: Path) -> None:
    pack = _evict_pack(tmp_path)
    for index, (value, expected) in enumerate((("2", "2"), ("0", "9999"), ("abc", "9999"), ("4097", "9999"), ("", "9999"))):
        _loader(tmp_path / f"build{index}", "env_limit", pack, env={"SYW2_G1_HD_KEY_LIMIT": value}, extra=(expected,))


def test_key_table_full_with_only_the_current_key_resident_refuses_the_request_instead_of_evicting_it(tmp_path: Path) -> None:
    _loader(tmp_path / "build", "evict_one", _evict_pack(tmp_path), defines=("-DG1_HD_KEY_LIMIT=1u",))


def test_key_table_full_spares_the_current_key_and_evicts_the_oldest_other(tmp_path: Path) -> None:
    _loader(tmp_path / "build", "evict_full", _evict_pack(tmp_path), defines=("-DG1_HD_KEY_LIMIT=3u",))


def test_key_table_full_keeps_a_key_that_was_begun_again_over_an_older_one(tmp_path: Path) -> None:
    """H-HDU1 U1-0: the victim is picked by the latest begin, not by insertion order (a hit refreshes the order)."""
    _loader(tmp_path / "build", "lru_recency", _evict_pack(tmp_path), defines=("-DG1_HD_KEY_LIMIT=3u",))


def test_cache_budget_too_small_for_the_hd_frame_fails_the_bind_instead_of_evicting_the_key_being_built(tmp_path: Path) -> None:
    """H-HDU1 U1-0: build may only evict other keys; evicting its own identity would free the frame it reads."""
    _loader(tmp_path / "build", "build_self", _evict_pack(tmp_path), defines=("-DG1_HD_CACHE_BYTE_LIMIT=20u",))


def test_cache_byte_budget_drops_the_oldest_frames_and_the_key_rebuilds_from_its_pack(tmp_path: Path) -> None:
    _loader(tmp_path / "build", "evict_bytes", _evict_pack(tmp_path), defines=("-DG1_HD_CACHE_BYTE_LIMIT=60u",))


def test_palette_trace_and_key_log_fields_are_emitted() -> None:
    trace = (STUB / "direct_draw_trace.c").read_text(encoding="utf-8")
    for field in ("hd_pack_pal_misses", "hd_pal_digest", "hd_pal_changes", "hd_pal_family"):
        assert f'\\"{field}\\":%u' in trace
    asset = (STUB / "g1_hd_asset.c").read_text(encoding="utf-8")
    assert '\\"pal\\":\\"%s\\"' in asset
    assert "G1_HD_RENDERER_ENTRIES 0x15A0u" in asset


def _tinted_pack(tmp_path: Path) -> Path:
    pack = tmp_path / "pack"
    pack.mkdir(parents=True)
    (_pal_dir(pack) / f"h{_digest():08x}_2x2.idx8").write_bytes(_GOOD)
    return pack


def test_tinted_writers_apply_the_colour_table_to_the_pack_indices(tmp_path: Path) -> None:
    """0x466EA0 and 0x466540 write dst = lut[source index]: the pack holds source indices, the loader applies lut[]."""
    _loader(tmp_path / "rle", "tinted_hit", _tinted_pack(tmp_path))
    _loader(tmp_path / "clip", "tinted_clip_hit", _tinted_pack(tmp_path / "c"))


def test_remap_table_content_change_makes_a_new_key_with_the_new_tables_colours_for_every_lut_writer(tmp_path: Path) -> None:
    """H-HDB5 B5-1: the table pointer is the same but its bytes change -> the key (auxiliary digest) differs and the pack frame takes the new table's colours.
    A key that ignored the digest would keep the first table's colours (m12b)."""
    for writer in ("466EA0", "466540", "4678C0", "468360"):
        _loader(tmp_path / writer, "lut_content_change", _tinted_pack(tmp_path / f"p{writer}"), extra=(writer,))


def test_tinted_lut_resulting_in_the_key_colour_is_written_and_counted(tmp_path: Path) -> None:
    _loader(tmp_path, "tinted_keycolor", _tinted_pack(tmp_path))


def test_tinted_table_whose_digest_differs_falls_back_to_scale2x(tmp_path: Path) -> None:
    _loader(tmp_path, "tinted_bad_digest", _tinted_pack(tmp_path))


def test_tinted_without_a_file_is_a_plain_miss(tmp_path: Path) -> None:
    pack = tmp_path / "empty"
    pack.mkdir()
    _loader(tmp_path, "tinted_miss", pack)


def test_tinted_env_off_and_other_aux_writers_stay_on_scale2x(tmp_path: Path) -> None:
    _loader(tmp_path / "off", "tinted_off", _tinted_pack(tmp_path), {"SYW2_G1_HD_PACK_TINTED": "0"})
    _loader(tmp_path / "checker", "checker_writer", _tinted_pack(tmp_path / "s"))


def test_tinted_trace_fields_are_emitted() -> None:
    trace = (STUB / "direct_draw_trace.c").read_text(encoding="utf-8")
    for field in ("hd_pack_lut_hits", "hd_pack_lut_rejects", "hd_pack_lut_key_color", "hd_pack_lut_nonidentity"):
        assert f'\\"{field}\\":%u' in trace


def test_key_log_reject_line_carries_the_silhouette_detail(tmp_path: Path) -> None:
    hole = bytearray(_GOOD)
    hole[0] = 0xFE                                   # pixel (0,0) written by the original but keyed in the pack
    pack = tmp_path / "pack"
    pack.mkdir()
    (_pal_dir(pack) / f"h{_digest():08x}_2x2.idx8").write_bytes(bytes(hole))
    log = tmp_path / "keys.jsonl"
    _loader(tmp_path / "build", "reject", pack, {"SYW2_G1_HD_KEY_LOG": str(log)})
    lines = [line for line in log.read_text(encoding="utf-8").splitlines() if '"result":"reject"' in line]
    assert len(lines) == 1
    assert '"written":3,"pack_opaque":2,"written_keyed":1,"opaque_unwritten":0,"first_xy":[0,0],"last_xy":[0,0]}' in lines[0]


def test_key_log_records_the_screen_and_start_palette_when_the_palette_id_changes(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    (_pal_dir(pack, _start_pal8()) / f"h{_digest():08x}_2x2.idx8").write_bytes(_GOOD)
    log = tmp_path / "keys.jsonl"
    _loader(tmp_path / "build", "pal_family", pack, {"SYW2_G1_HD_KEY_LOG": str(log)})
    lines = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines() if '"pal_change"' in line]
    assert [line["pal_change"] for line in lines] == [_start_pal8()]          # darkening inside the family is not a change
    assert len(lines[0]["rgb"]) == 1536 and len(lines[0]["start"]) == 1536


def _shade_digest() -> int:
    value = 2166136261
    for byte in [0, 2, 0x11, 0x12, 0, 1, 0x13] + list(range(7, 128)):
        value = ((value ^ byte) * 16777619) & 0xFFFFFFFF
    return value


def _shade_pack(tmp_path: Path, name: str = "pack") -> Path:
    pack = tmp_path / name
    pack.mkdir(parents=True)
    (_pal_dir(pack, _start_pal8()) / f"h{_shade_digest():08x}_2x2.idx8").write_bytes(_GOOD)   # fake_tables: screen = zero = darkened start
    return pack


def test_shaded_terrain_applies_the_renderer_chain_per_1x_cell_shade(tmp_path: Path) -> None:
    """0x468CC0 and 0x4690A0 write dst = inverse[T[pal(c)][s]]: each 1x cell's shade covers its 2x2 block."""
    _loader(tmp_path / "plain", "shade_hit", _shade_pack(tmp_path / "a"))
    _loader(tmp_path / "clip", "shade_clip_hit", _shade_pack(tmp_path / "b"))


def test_shaded_terrain_whose_identity_disagrees_with_the_tables_stays_on_scale2x(tmp_path: Path) -> None:
    _loader(tmp_path / "selfcheck", "shade_selfcheck", _shade_pack(tmp_path / "a"))


def test_shaded_terrain_rejects_bad_digest_source_level_and_palette(tmp_path: Path) -> None:
    for index, scenario in enumerate(("shade_bad_digest", "shade_bad_source", "shade_bad_level", "shade_bad_palette")):
        _loader(tmp_path / scenario, scenario, _shade_pack(tmp_path / f"p{index}"))


def test_byte_pressure_eviction_keeps_a_shaded_terrain_key_able_to_rebuild_its_pack_frame(tmp_path: Path) -> None:
    _loader(tmp_path / "shade", "shade_evict_bytes", _shade_pack(tmp_path / "a"), defines=("-DG1_HD_CACHE_BYTE_LIMIT=40u",))


def test_refreshed_shade_hit_key_drops_to_scale2x_but_plain_key_reapplies_its_pack(tmp_path: Path) -> None:
    """H-HDS1r: a shade HIT key whose identity is evicted must not paint its old LUT over the new frame."""
    _loader(tmp_path / "shade", "shade_refresh", _shade_pack(tmp_path / "a"))
    plain = tmp_path / "plain_pack"
    plain.mkdir()
    (_pal_dir(plain) / f"h{_digest():08x}_2x2.idx8").write_bytes(_GOOD)
    _loader(tmp_path / "plain", "refresh_plain", plain)


def test_shaded_terrain_env_off_checker_and_missing_file(tmp_path: Path) -> None:
    _loader(tmp_path / "off", "shade_off", _shade_pack(tmp_path / "a"), {"SYW2_G1_HD_PACK_SHADE": "0"})
    _loader(tmp_path / "checker", "shade_checker", _shade_pack(tmp_path / "b"))
    empty = tmp_path / "empty"
    empty.mkdir()
    _loader(tmp_path / "miss", "shade_miss", empty)


def test_shade_trace_fields_are_emitted() -> None:
    trace = (STUB / "direct_draw_trace.c").read_text(encoding="utf-8")
    for field in ("hd_pack_shade_hits", "hd_pack_shade_rejects", "hd_pack_shade_reject_aux",
                  "hd_pack_shade_reject_table", "hd_pack_shade_reject_range", "hd_pack_shade_reject_source",
                  "hd_pack_shade_reject_selfcheck", "hd_pack_shade_reject_refresh", "hd_pack_shade_selfcheck_pixels",
                  "hd_pack_shade_multi_keys", "hd_pack_shade_key_color", "hd_pack_shade_lut_bytes"):
        assert f'\\"{field}\\":%u' in trace


def _fullscreen_pack(tmp_path: Path, name: str = "pack", mutate: bytes | None = None) -> Path:
    """800x600 whole-screen pack file f<hash>_800x600.idx8: 1,920,000 bytes, byte i = i % 251 (never the key 0xFE)."""
    pack = tmp_path / name
    pack.mkdir(parents=True)
    body = bytes(i % 251 for i in range(1600 * 1200)) if mutate is None else mutate
    (_pal_dir(pack) / "f12345678_800x600.idx8").write_bytes(body)
    return pack


def test_fullscreen_name_uses_the_f_prefix_and_the_full_frame_digest(tmp_path: Path) -> None:
    _run(tmp_path, r"""
    char name[40];
    assert(g1_hd_pack_fullscreen_name(name, sizeof(name), 0x69EE1F1Cu, 800u, 600u));
    assert(strcmp(name, "f69ee1f1c_800x600.idx8") == 0);
    assert(g1_hd_pack_name(name, sizeof(name), 0x69EE1F1Cu, 800u, 600u));
    assert(strcmp(name, "h69ee1f1c_800x600.idx8") == 0);
    assert(!g1_hd_pack_fullscreen_name(name, sizeof(name), 1u, 801u, 600u));
    """)


def test_fullscreen_frame_hit_is_cached_and_a_miss_keeps_the_cached_frame(tmp_path: Path) -> None:
    _loader(tmp_path / "build", "fs_hit", _fullscreen_pack(tmp_path))


def test_fullscreen_frame_without_a_file_is_a_counted_miss(tmp_path: Path) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()
    _loader(tmp_path / "build", "fs_miss", empty)


def test_fullscreen_frame_rejects_wrong_size_and_the_key_colour(tmp_path: Path) -> None:
    body = bytearray(i % 251 for i in range(1600 * 1200))
    body[777] = 0xFE                                  # the transparent key can never appear in an opaque full screen
    _loader(tmp_path / "build_key", "fs_reject", _fullscreen_pack(tmp_path, "key", bytes(body)))
    _loader(tmp_path / "build_short", "fs_reject", _fullscreen_pack(tmp_path, "short", bytes(1600 * 1200 - 1)))


def test_fullscreen_frame_follows_the_screen_palette(tmp_path: Path) -> None:
    _loader(tmp_path / "build", "fs_pal_other", _fullscreen_pack(tmp_path))


def test_fullscreen_env_off_leaves_the_frame_on_scale2x(tmp_path: Path) -> None:
    _loader(tmp_path / "build", "fs_off", _fullscreen_pack(tmp_path), {"SYW2_G1_HD_PACK_FULLSCREEN": "0"})


def test_fullscreen_trace_fields_are_emitted() -> None:
    trace = (STUB / "direct_draw_trace.c").read_text(encoding="utf-8")
    for field in ("hd_source_guard_rejects", "hd_pack_fullscreen_hits", "hd_pack_fullscreen_misses", "hd_pack_fullscreen_rejects",
                  "hd_pack_fullscreen_loads"):
        assert f'\\"{field}\\":%u' in trace


def test_fullscreen_pack_frame_is_written_over_the_scale2x_copy_of_the_menu_block_copy() -> None:
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    body = mirror[mirror.index("static void transfer_block_copy_to_screen"):mirror.index("H-P35: the load-slot screen")]
    hashed = body.index("hash *= 16777619u;")
    lookup = body.index("g1_hd_asset_fullscreen_frame(hash, width, height)")
    assert hashed < lookup and "if (scale2x)" in body[hashed:lookup]
    assert body.index("g1_frame_copy_apply(") < lookup                    # Scale2x first: coverage maps stay as before
    assert "mirror_move_bytes(g_mirror + row * 1600u, pack + row * width * 2u, width * 2u)" in body[lookup:]


def test_flip_writer_applies_the_mirrored_pack_frame_and_the_colour_table(tmp_path: Path) -> None:
    """0x466B50 writes the same RLE right to left: the unflipped pack is mirrored, checked against the mirrored mask, then lut[]."""
    _loader(tmp_path, "flip_hit", _tinted_pack(tmp_path))


def test_flip_writer_checks_the_mirrored_silhouette_not_the_file_silhouette(tmp_path: Path) -> None:
    """Without the mirror the file's own silhouette (pixel (0,1) opaque) disagrees with the flipped identity mask: a hit proves the mirror."""
    pack = _tinted_pack(tmp_path)
    _loader(tmp_path / "hit", "flip_hit", pack)                    # the mirrored frame fits the mirrored mask
    _loader(tmp_path / "plain", "tinted_hit", pack)                # while a non-flip key keeps the file's silhouette


def test_flip_writer_without_a_file_is_a_counted_miss_and_bad_table_a_reject(tmp_path: Path) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()
    _loader(tmp_path / "miss", "flip_miss", empty)
    _loader(tmp_path / "digest", "flip_bad_digest", _tinted_pack(tmp_path / "p"))


def test_flip_env_off_keeps_the_diff_mirror_and_leaves_tinted_alone(tmp_path: Path) -> None:
    _loader(tmp_path / "off", "flip_off", _tinted_pack(tmp_path), {"SYW2_G1_HD_PACK_FLIP": "0"})
    _loader(tmp_path / "indep", "flip_tinted_independent", _tinted_pack(tmp_path / "t"), {"SYW2_G1_HD_PACK_FLIP": "0"})


def test_clip_flip_writer_applies_the_mirrored_pack_frame_and_the_colour_table(tmp_path: Path) -> None:
    """H-HDU1: 0x466BE0 is the clip-box sibling of 0x466B50: same mirrored pack frame, mirrored mask check and lut[]."""
    pack = _tinted_pack(tmp_path)
    _loader(tmp_path / "hit", "clip_flip_hit", pack)
    _loader(tmp_path / "apart", "flip_writers_apart", pack)        # the writer is part of the key identity


def test_clip_flip_writer_misses_rejects_and_follows_the_flip_switch(tmp_path: Path) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()
    _loader(tmp_path / "miss", "clip_flip_miss", empty)
    _loader(tmp_path / "digest", "clip_flip_bad_digest", _tinted_pack(tmp_path / "p"))
    _loader(tmp_path / "off", "clip_flip_off", _tinted_pack(tmp_path / "q"), {"SYW2_G1_HD_PACK_FLIP": "0"})


def test_clip_flip_wrapper_takes_the_key_path_with_the_viewport_replay_and_falls_back_to_the_diff_mirror() -> None:
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    start = mirror.index("static DWORD __attribute__((thiscall)) mirror_flip_clip(")
    wrapper = mirror[start:mirror.index("mirror_shade_rle(", start)]
    assert "active && g1_hd_asset_flip_key_path()" in wrapper     # edge sprites (region.wrap/clipped) are the point: viewport replay
    assert "!region.wrap" not in wrapper and "!region.clipped" not in wrapper    # neither edge case is excluded
    assert "G1_FLIP_CLIP, TRUE);" in wrapper                        # clipped: replay with the full viewport, like 0x466540
    assert "(DWORD)width, (DWORD)height" in wrapper                 # the whole sprite rectangle, not the on-screen part
    assert "x >= -32768 && x <= 32767" in wrapper and "width <= 800" in wrapper and "height <= 600" in wrapper
    assert "256u" in wrapper
    assert "if (g_reinvoke_composed)" in wrapper and "g_flip_clip_key_fallbacks" in wrapper and "g_flip_clip_keyed_calls" in wrapper
    assert wrapper.index("g_original_flip_clip(renderer") < wrapper.index("g1_hd_asset_flip_key_path()") < wrapper.index("g1_overlay_blt_apply(")
    assert "case G1_FLIP_CLIP:" in mirror and "g_original_flip_clip(renderer, x, y, args[2]" in mirror


def test_flip_wrapper_takes_the_key_path_only_for_a_whole_on_screen_rectangle() -> None:
    mirror = (STUB / "g1_mirror2x.c").read_text(encoding="utf-8")
    start = mirror.index("static DWORD __attribute__((thiscall)) mirror_flip_rle(")
    wrapper = mirror[start:mirror.index("mirror_keyed_copy(", start)]
    assert "active && !region.clipped && !region.wrap && g1_hd_asset_flip_key_path()" in wrapper
    assert "G1_FLIP_RLE, FALSE);" in wrapper                       # unclipped, tinted-style replay
    assert "256u" in wrapper                                        # aux = the 256 B remap table
    assert "if (g_reinvoke_composed)" in wrapper and "g_flip_rle_key_fallbacks" in wrapper   # not ready -> the diff mirror
    assert "case G1_FLIP_RLE:" in mirror
    assert 'g1_hd_asset_flip_key_path' in (STUB / "g1_hd_asset.h").read_text(encoding="utf-8")


def test_flip_trace_fields_are_emitted() -> None:
    trace = (STUB / "direct_draw_trace.c").read_text(encoding="utf-8")
    for field in ("hd_pack_flip_hits", "hd_pack_flip_misses", "hd_pack_flip_rejects",
                  "flip_rle_466B50_keyed_calls", "flip_rle_466B50_key_fallbacks",
                  "flip_clip_466BE0_keyed_calls", "flip_clip_466BE0_key_fallbacks"):
        assert f'\\"{field}\\":%u' in trace


def test_blend_writer_pack_hit_exposes_the_pack_frame_and_counts_its_own_hits(tmp_path: Path) -> None:
    """H-HDB0: 0x4672E0 has no aux table; its key hits the plain pack file and the caller blends that frame."""
    pack = tmp_path / "pack"
    pack.mkdir()
    (_pal_dir(pack) / f"h{_digest():08x}_2x2.idx8").write_bytes(_GOOD)
    _loader(tmp_path / "hit", "blend_hit", pack)


def test_blend_writer_miss_and_reject_leave_no_pack_frame(tmp_path: Path) -> None:
    empty = tmp_path / "empty"
    (empty / _pal8()).mkdir(parents=True)
    _loader(tmp_path / "miss", "blend_miss", empty)
    bad = tmp_path / "bad"
    (_pal_dir(bad) / f"h{_digest():08x}_2x2.idx8").write_bytes(bytes(16))        # no silhouette: every block opaque 0 -> reject
    _loader(tmp_path / "reject", "blend_reject", bad)


def test_blend_env_off_keeps_the_diff_mirror_and_leaves_flip_alone(tmp_path: Path) -> None:
    _loader(tmp_path / "off", "blend_off", tmp_path, {"SYW2_G1_HD_PACK_BLEND": "0"})


# --- H-HDN0: extended pack names --------------------------------------------------

def _prefix_hash(length: int) -> int:
    """FNV-1a of the first ``length`` bytes of the loader fixture's source (source[i] = i)."""
    value = 2166136261
    for byte in range(length):
        value = ((value ^ byte) * 16777619) & 0xFFFFFFFF
    return value


def _ext_files(directory: Path, length: int = 200, marker: bytes | None = None, frame: bytes | None = _GOOD,
               hash_length: int | None = None) -> None:
    """The plain name is absent; <name>.amb holds ``length``, the frame is named with FNV-1a over ``hash_length`` bytes."""
    stem = f"h{_digest():08x}_2x2"
    (directory / f"{stem}.amb").write_bytes(length.to_bytes(4, "little") if marker is None else marker)
    if frame is not None:
        (directory / f"{stem}_{length}_{_prefix_hash(hash_length or length):08x}.idx8").write_bytes(frame)


def test_extended_name_finds_the_frame_of_a_picture_whose_plain_name_collides(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    _ext_files(_pal_dir(pack))
    _loader(tmp_path / "build", "ext_hit", pack)


def test_extended_name_hashes_exactly_the_marker_length_of_source_bytes(tmp_path: Path) -> None:
    """A frame named with a hash over another length is not found: the file is a counted extended miss."""
    pack = tmp_path / "pack"
    _ext_files(_pal_dir(pack), length=200, hash_length=199)
    _loader(tmp_path / "build", "ext_no_file", pack)


def test_plain_name_wins_over_the_marker(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    directory = _pal_dir(pack)
    (directory / f"h{_digest():08x}_2x2.idx8").write_bytes(_GOOD)
    _ext_files(directory, frame=bytes(16))                         # a bad extended frame would reject if it were read
    _loader(tmp_path / "build", "ext_base_wins", pack)


def test_no_marker_is_a_plain_miss_and_leaves_the_extended_counters_alone(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    _pal_dir(pack)
    _loader(tmp_path / "build", "ext_no_marker", pack)


def test_marker_without_the_extended_file_is_a_counted_extended_miss(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    _ext_files(_pal_dir(pack), frame=None)
    _loader(tmp_path / "build", "ext_no_file", pack)


def test_unusable_markers_are_a_miss_counted_as_extended_rejects(tmp_path: Path) -> None:
    for number, marker in enumerate((
            (128).to_bytes(4, "little"),                  # not longer than the 128 digest bytes
            (65537).to_bytes(4, "little"),                # above the limit
            (200).to_bytes(3, "little"),                  # wrong size
            (200).to_bytes(4, "little") + b"\0")):        # wrong size
        pack = tmp_path / f"pack{number}"
        _ext_files(_pal_dir(pack), marker=marker)
        _loader(tmp_path / f"build{number}", "ext_bad_marker", pack)


def test_extended_frame_with_the_wrong_silhouette_is_rejected_and_counted(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    hole = bytearray(_GOOD)
    hole[0] = 0xFE
    _ext_files(_pal_dir(pack), frame=bytes(hole))
    _loader(tmp_path / "build", "ext_bad_frame", pack)


def test_extended_lookup_env_off_leaves_a_colliding_name_on_scale2x(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    _ext_files(_pal_dir(pack))
    _loader(tmp_path / "build", "ext_off", pack, {"SYW2_G1_HD_PACK_EXT": "0"})


def test_extended_lookup_is_wired_after_the_plain_miss_and_traced() -> None:
    asset = (STUB / "g1_hd_asset.c").read_text(encoding="utf-8")
    start = asset.index("static BYTE read_pack_frame(")
    body = asset[start:asset.index("static BOOL build_hd_frame(", start)]
    assert body.index("note_missing_file(path);") < body.index("open_extended_pack_file(key)")
    ext = asset[asset.index("static HANDLE open_extended_pack_file("):start]
    assert "readable_range(source, length)" in ext and "length < G1_HD_PACK_EXT_MIN || length > G1_HD_PACK_EXT_MAX" in ext
    assert "g_current_source = source;" in asset and '#define G1_HD_PACK_EXT_ENV "SYW2_G1_HD_PACK_EXT"' in asset
    trace = (STUB / "direct_draw_trace.c").read_text(encoding="utf-8")
    for field in ("hd_pack_ext_hits", "hd_pack_ext_misses", "hd_pack_ext_rejects"):
        assert f'\\"{field}\\":%u' in trace


# --- H-HDB2 B2-0: lap1193 surviving mutants c4 / c9 ---------------------------------

def test_a_key_that_reads_no_pack_file_does_not_inherit_the_previous_keys_extended_reject(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    _ext_files(_pal_dir(pack), marker=(128).to_bytes(4, "little"))
    _loader(tmp_path / "build", "extx_stale", pack)


def test_rereading_a_hit_key_leaves_every_extended_counter_alone(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    directory = _pal_dir(pack)
    _ext_files(directory)
    _loader(tmp_path / "build", "extx_refresh", pack, extra=(str(directory / f"h{_digest():08x}_2x2.amb"),))


def test_clipped_weighted_writer_pack_hit_counts_as_a_blend_hit(tmp_path: Path) -> None:
    pack = tmp_path / "pack"
    pack.mkdir()
    (_pal_dir(pack) / f"h{_digest():08x}_2x2.idx8").write_bytes(_GOOD)
    _loader(tmp_path / "build", "blendclip_hit", pack)


def test_flipped_translucent_writers_hit_the_mirrored_pack_frame_and_count_as_blend_writers(tmp_path: Path) -> None:
    """H-HDB3: 0x467FD0 and 0x4685C0 have no remap table: the identity mask is the mirrored silhouette, the file is mirrored."""
    pack = _tinted_pack(tmp_path)
    _loader(tmp_path / "fd0", "blendflip_467FD0", pack)
    _loader(tmp_path / "5c0", "blendflip_4685C0", pack)
    # a blend writer that does not draw right to left rejects the same mask: the mirror belongs to the two flipped writers only
    _loader(tmp_path / "plain", "blendflip_plain", pack)


def test_flipped_translucent_key_path_follows_both_the_blend_and_the_flip_switch(tmp_path: Path) -> None:
    pack = _tinted_pack(tmp_path)
    _loader(tmp_path / "flip", "blendflip_flip_off", pack, {"SYW2_G1_HD_PACK_FLIP": "0"})
    _loader(tmp_path / "blend", "blendflip_blend_off", pack, {"SYW2_G1_HD_PACK_BLEND": "0"})
