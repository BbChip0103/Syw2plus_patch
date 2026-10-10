/* Bounded P2/P3 key-bound asset ledger.
 *
 * The source pointer is the exact frame pointer passed to the protected
 * original primitive. A key includes the writer and dimensions plus a
 * bounded digest of source bytes. The identity frame is the value produced
 * by the original primitive itself; this ledger only proves its provenance
 * and coverage so P3 can replace the source without changing the mask.
 */

#include <string.h>

#include "g1_hd_asset.h"
#include "g1_hd_pack.h"
#include "g1_perf_sections.h"
#include "g1_scale2x_core.h"
#include "g1_scratch_bounds.h"

#define G1_HD_SOURCE_ENV "SYW2_G1_HD_SOURCE"
#define G1_HD_SOURCE_IDENTITY "identity"
#define G1_HD_SOURCE_SCALE2X "scale2x"
#define G1_HD_PACK_ENV "SYW2_G1_HD_PACK"
#define G1_HD_PACK_TINTED_ENV "SYW2_G1_HD_PACK_TINTED"
#define G1_HD_PACK_FLIP_ENV "SYW2_G1_HD_PACK_FLIP"
#define G1_HD_PACK_BLEND_ENV "SYW2_G1_HD_PACK_BLEND"
#define G1_HD_PACK_EXT_ENV "SYW2_G1_HD_PACK_EXT"
#define G1_HD_BLEND_RLE 0x004672E0u
#define G1_HD_BLEND_WRLE 0x00467580u
#define G1_HD_BLEND_CLIP 0x00467B00u
#define G1_HD_BLEND_FLIP 0x00467FD0u
#define G1_HD_BLEND_SKIP 0x004685C0u
#define G1_HD_BLEND_CLIP7 0x004678C0u
#define G1_HD_BLEND_FLIP7 0x00468360u
#define G1_HD_FLIP_RLE 0x00466B50u
#define G1_HD_FLIP_CLIP 0x00466BE0u
#define G1_HD_TINTED_RLE 0x00466EA0u
#define G1_HD_TINTED_CLIP_RLE 0x00466540u
#define G1_HD_LUT_BYTES 256u
#define G1_HD_PACK_SHADE_ENV "SYW2_G1_HD_PACK_SHADE"
#define G1_HD_PACK_FULLSCREEN_ENV "SYW2_G1_HD_PACK_FULLSCREEN"
#define G1_HD_FULLSCREEN_MISS_SLOTS 8u
#define G1_HD_TERRAIN_SHADE 0x00468CC0u
#define G1_HD_TERRAIN_CLIP_SHADE 0x004690A0u
#define G1_HD_SHADE_LEVELS 64u
#define G1_HD_SHADE_MAP_LIMIT 65536u
#ifndef G1_HD_RENDERER_BASE
#define G1_HD_RENDERER_BASE ((const BYTE *)(ULONG_PTR)0x00E5BF18u)
#endif
#define G1_HD_RENDERER_INVERSE 0x19A0u
#define G1_HD_RENDERER_INVERSE_BYTES (64u * 64u * 64u)
#define G1_HD_RENDERER_PALETTE 0x419A0u
#define G1_HD_RENDERER_ENTRIES 0x15A0u
#define G1_HD_RENDERER_SHADE_TABLE 0x6BCA0u
#ifdef _WIN32
#define G1_HD_PATH_SEPARATOR '\\'
#else
#define G1_HD_PATH_SEPARATOR '/'      /* host-compiled unit tests */
#endif
#define G1_HD_KEY_LOG_ENV "SYW2_G1_HD_KEY_LOG"
#define G1_HD_KEY_LIMIT_ENV "SYW2_G1_HD_KEY_LIMIT"   /* diagnostic: lowers the key table size */
#ifndef G1_HD_KEY_LIMIT
#define G1_HD_KEY_LIMIT 4096u
#endif
#define G1_HD_PIXEL_LIMIT (800u * 600u)
#define G1_HD_DIGEST_BYTES 128u
#ifndef G1_HD_CACHE_BYTE_LIMIT
#define G1_HD_CACHE_BYTE_LIMIT (128u * 1024u * 1024u)
#endif

typedef struct {
    DWORD source;
    DWORD writer;
    DWORD auxiliary;
    DWORD auxiliary_digest;
    DWORD width;
    DWORD height;
    DWORD digest;
    DWORD pal;
    BYTE *identity_frame;
    BYTE *identity_written;
    DWORD identity_stride;
    DWORD identity_width;
    DWORD identity_height;
    DWORD identity_bytes;
    DWORD identity_mask_bytes;
    BYTE *hd_frame;
    DWORD hd_stride;
    DWORD hd_width;
    DWORD hd_height;
    DWORD hd_bytes;
    BYTE pack_state;
    BYTE pack_applied;
    BYTE lut_valid;
    BYTE lut[G1_HD_LUT_BYTES];
    /* Shaded terrain (0x468CC0/0x4690A0): shade_state 0 = not a shade key, 1 = copies
     * captured, 2 = rejected (shade_reason).  shade_lut holds one 256 B table per used level. */
    BYTE shade_state;
    BYTE shade_reason;
    BYTE shade_slot[G1_HD_SHADE_LEVELS];
    BYTE *shade_map;
    BYTE *shade_src;
    DWORD shade_src_bytes;
    BYTE *shade_lut;
    DWORD shade_lut_bytes;
    DWORD draws;
    DWORD last_draw;            /* g_draw_clock at the latest begin: LRU order for eviction */
} G1HdKey;

/* pack_state: first attempt for this key decided once; later identity
 * refreshes re-read the file only for a key that already hit. */
enum { PACK_UNTRIED = 0, PACK_HIT, PACK_MISS, PACK_REJECT, PACK_SKIP_AUX, PACK_NONE,
       PACK_LUT_REJECT, PACK_SHADE_REJECT };
enum { SHADE_REJECT_AUX = 0, SHADE_REJECT_TABLE, SHADE_REJECT_RANGE, SHADE_REJECT_SOURCE,
       SHADE_REJECT_SELFCHECK, SHADE_REJECT_REFRESH, SHADE_REJECT_REASONS };
static const char *const g_shade_reason_names[SHADE_REJECT_REASONS] = {
    "aux", "table", "range", "source", "selfcheck", "refresh" };

static G1HdKey g_keys[G1_HD_KEY_LIMIT];
static DWORD g_key_count = 0u;
static BYTE g_identity_mask[G1_HD_PIXEL_LIMIT];
static DWORD g_identity_pixels = 0u;
static DWORD g_invalid_sources = 0u;
static DWORD g_identity_events = 0u;
static DWORD g_identity_lookup_hits = 0u;
static DWORD g_identity_lookup_misses = 0u;
static DWORD g_identity_cache_bytes = 0u;
static DWORD g_draw_clock = 0u;
static DWORD g_identity_evictions = 0u;
static DWORD g_key_limit = G1_HD_KEY_LIMIT;
static DWORD g_identity_cache_inserts = 0u;
static DWORD g_identity_cache_hits = 0u;
static DWORD g_identity_cache_misses = 0u;
static DWORD g_identity_cache_refreshes = 0u;
static DWORD g_identity_negative_lookup_attempts = 0u;
static DWORD g_identity_negative_lookup_misses = 0u;
static DWORD g_identity_key_mismatches = 0u;
static DWORD g_scale2x_blocks = 0u;
static DWORD g_scale2x_subpixel_differences = 0u;
static DWORD g_scale2x_palette_violations = 0u;
static volatile LONG g_current_valid = 0;
static G1HdKey *g_current_key = NULL;
static LONG g_current_origin_x = 0;
static LONG g_current_origin_y = 0;
static DWORD g_full_frame_calls = 0u;
static DWORD g_bbox_calls = 0u;
static DWORD g_clipped_calls = 0u;
static DWORD g_identity_cache_hit_bytes = 0u;
static DWORD g_identity_cache_insert_bytes = 0u;
static DWORD g_identity_cache_refresh_bytes = 0u;
static DWORD g_clip_replay_mismatches = 0u;
static DWORD g_last_clip_mismatch_x = 0u;
static DWORD g_last_clip_mismatch_y = 0u;
static BYTE g_last_clip_screen_value = 0u;
static BYTE g_last_clip_replay_value = 0u;
static volatile LONG g_env_state = 0;
static DWORD g_hd_source_mode = 0u;
static char g_hd_pack_dir[MAX_PATH];
static char g_hd_key_log_path[MAX_PATH];
static HANDLE g_hd_key_log = INVALID_HANDLE_VALUE;
static DWORD g_pack_hits = 0u;
static DWORD g_pack_misses = 0u;
static DWORD g_pack_rejects = 0u;
static DWORD g_pack_skipped_aux = 0u;
static DWORD g_pack_lookup_blocks = 0u;
static DWORD g_pack_lut_hits = 0u;
static DWORD g_pack_lut_rejects = 0u;
static DWORD g_pack_lut_key_color = 0u;
static DWORD g_pack_lut_nonidentity = 0u;
static DWORD g_pack_flip_hits = 0u;
static DWORD g_pack_flip_misses = 0u;
static DWORD g_pack_flip_rejects = 0u;
static DWORD g_pack_blend_hits = 0u;
static DWORD g_pack_blend_misses = 0u;
static DWORD g_pack_blend_rejects = 0u;
static DWORD g_pack_ext_hits = 0u;
static DWORD g_pack_ext_misses = 0u;
static DWORD g_pack_ext_rejects = 0u;
/* H-HDN0: source pointer of the latest begin (the key keeps only 32 bits) and how the last pack read used the extended name */
static const BYTE *g_current_source = NULL;
static BYTE g_last_ext = 0u;
static BOOL g_hd_tinted_off = FALSE;
static BOOL g_hd_flip_off = FALSE;
static BOOL g_hd_blend_off = FALSE;
static BOOL g_hd_ext_off = FALSE;
static BOOL g_hd_shade_off = FALSE;
static BOOL g_hd_fullscreen_off = FALSE;
static BYTE *g_fullscreen_frame = NULL;
static DWORD g_fullscreen_hash = 0u;
static DWORD g_fullscreen_pal = 0u;
static DWORD g_fullscreen_width = 0u;
static DWORD g_fullscreen_height = 0u;
static DWORD g_fullscreen_missed_hash[G1_HD_FULLSCREEN_MISS_SLOTS];
static DWORD g_fullscreen_missed_pal[G1_HD_FULLSCREEN_MISS_SLOTS];
static BYTE g_fullscreen_missed_rejected[G1_HD_FULLSCREEN_MISS_SLOTS];
static DWORD g_fullscreen_missed_count = 0u;
static DWORD g_fullscreen_hits = 0u;
static DWORD g_fullscreen_misses = 0u;
static DWORD g_fullscreen_rejects = 0u;
static DWORD g_fullscreen_loads = 0u;
static DWORD g_pack_pal_misses = 0u;
static DWORD g_pal_digest = 0u;
static DWORD g_pal_tick = 0u;
static DWORD g_pal_changes = 0u;
static BOOL g_pal_valid = FALSE;
static BOOL g_pal_family = FALSE;
static DWORD g_pal_logged = 0u;
static DWORD g_pack_shade_hits = 0u;
static DWORD g_pack_shade_rejects[SHADE_REJECT_REASONS];
static DWORD g_pack_shade_selfcheck_pixels = 0u;
static DWORD g_pack_shade_multi_keys = 0u;
static DWORD g_pack_shade_key_color = 0u;
static DWORD g_pack_shade_lut_bytes = 0u;
/* Detail of the last shade key outcome, appended to its key-log line. */
static DWORD g_shade_slots = 0u;
static DWORD g_shade_checked = 0u;
static DWORD g_shade_mismatches = 0u;
static DWORD g_shade_first_x = 0u;
static DWORD g_shade_first_y = 0u;
static BYTE g_shade_last_reason = 0u;
/* Last silhouette-reject detail, appended to the key log's "reject" line. */
static DWORD g_reject_written = 0u;
static DWORD g_reject_pack_opaque = 0u;
static DWORD g_reject_written_keyed = 0u;
static DWORD g_reject_opaque_unwritten = 0u;
static DWORD g_reject_first_x = 0u;
static DWORD g_reject_first_y = 0u;
static DWORD g_reject_last_x = 0u;
static DWORD g_reject_last_y = 0u;

static void initialize_environment(void)
{
    char value[16];
    DWORD size;
    LONG state = InterlockedCompareExchange(&g_env_state, 1, 0);
    if (state == 0) {
        size = GetEnvironmentVariableA(G1_HD_SOURCE_ENV, value, sizeof(value));
        if (size == 8u && value[0] == 'i' && value[1] == 'd' &&
            value[2] == 'e' && value[3] == 'n' && value[4] == 't' &&
            value[5] == 'i' && value[6] == 't' && value[7] == 'y')
            g_hd_source_mode = 1u;
        else if (size == 7u && value[0] == 's' && value[1] == 'c' &&
                 value[2] == 'a' && value[3] == 'l' && value[4] == 'e' &&
                 value[5] == '2' && value[6] == 'x')
            g_hd_source_mode = 2u;
        size = GetEnvironmentVariableA(G1_HD_PACK_ENV, g_hd_pack_dir,
                                       sizeof(g_hd_pack_dir));
        if (size == 0u || size >= sizeof(g_hd_pack_dir)) g_hd_pack_dir[0] = '\0';
        size = GetEnvironmentVariableA(G1_HD_PACK_TINTED_ENV, value, sizeof(value));
        g_hd_tinted_off = size == 1u && value[0] == '0';
        size = GetEnvironmentVariableA(G1_HD_PACK_FLIP_ENV, value, sizeof(value));
        g_hd_flip_off = size == 1u && value[0] == '0';
        size = GetEnvironmentVariableA(G1_HD_PACK_BLEND_ENV, value, sizeof(value));
        g_hd_blend_off = size == 1u && value[0] == '0';
        size = GetEnvironmentVariableA(G1_HD_PACK_EXT_ENV, value, sizeof(value));
        g_hd_ext_off = size == 1u && value[0] == '0';
        size = GetEnvironmentVariableA(G1_HD_PACK_SHADE_ENV, value, sizeof(value));
        g_hd_shade_off = size == 1u && value[0] == '0';
        size = GetEnvironmentVariableA(G1_HD_PACK_FULLSCREEN_ENV, value, sizeof(value));
        g_hd_fullscreen_off = size == 1u && value[0] == '0';
        size = GetEnvironmentVariableA(G1_HD_KEY_LIMIT_ENV, value, sizeof(value));
        if (size > 0u && size < sizeof(value)) {
            DWORD limit = 0u, digit;
            for (digit = 0u; digit < size && value[digit] >= '0' && value[digit] <= '9' &&
                             limit <= G1_HD_KEY_LIMIT; ++digit)
                limit = limit * 10u + (DWORD)(value[digit] - '0');
            if (digit == size && limit >= 1u && limit <= G1_HD_KEY_LIMIT) g_key_limit = limit;
        }
        size = GetEnvironmentVariableA(G1_HD_KEY_LOG_ENV, g_hd_key_log_path,
                                       sizeof(g_hd_key_log_path));
        if (size == 0u || size >= sizeof(g_hd_key_log_path))
            g_hd_key_log_path[0] = '\0';
        InterlockedExchange(&g_env_state, 2);
    } else {
        while (InterlockedCompareExchange(&g_env_state, 2, 2) != 2) Sleep(0);
    }
}

static DWORD hash_source(const BYTE *source)
{
    DWORD hash = 2166136261u;
    DWORD index;
    if (!source) return 0u;
    for (index = 0u; index < G1_HD_DIGEST_BYTES; ++index) {
        hash ^= source[index];
        hash *= 16777619u;
    }
    return hash;
}

static BOOL readable_range(const BYTE *source, SIZE_T bytes)
{
    MEMORY_BASIC_INFORMATION info;
    SIZE_T remaining = bytes;
    const BYTE *cursor = source;
    if (!source) return FALSE;
    while (remaining != 0u) {
        SIZE_T available;
        if (!VirtualQuery(cursor, &info, sizeof(info)) ||
            info.State != MEM_COMMIT ||
            (info.Protect & (PAGE_NOACCESS | PAGE_GUARD)) != 0u) return FALSE;
        available = (SIZE_T)((BYTE *)info.BaseAddress + info.RegionSize - cursor);
        if (available == 0u) return FALSE;
        if (available > remaining) available = remaining;
        cursor += available;
        remaining -= available;
    }
    return TRUE;
}

static BOOL readable_source(const BYTE *source)
{
    return readable_range(source, G1_HD_DIGEST_BYTES);
}

/* Colour-substitution writers: output = lut[original index] (aux is the 256 B table). */
static BOOL is_tinted_pack_writer(DWORD writer)
{
    return writer == G1_HD_TINTED_RLE || writer == G1_HD_TINTED_CLIP_RLE;
}

/* 0x466B50 and its clip-box sibling 0x466BE0 draw the same RLE and remap table as the tinted writers,
 * right to left. */
static BOOL is_flip_pack_writer(DWORD writer)
{
    return writer == G1_HD_FLIP_RLE || writer == G1_HD_FLIP_CLIP;
}

/* H-HDB3: 0x467FD0 and 0x4685C0 blend the same stream as 0x467580 / 0x467B00 right to left.  They carry no remap table, so
 * only the pack file's rows are mirrored (the identity planes the caller binds are already in screen direction). */
static BOOL is_flip_blend_writer(DWORD writer)
{
    return writer == G1_HD_BLEND_FLIP || writer == G1_HD_BLEND_SKIP || writer == G1_HD_BLEND_FLIP7;
}

/* H-HDB4: 0x4678C0 and its left/right flipped sibling 0x468360 blend remap[token] (a 256 B table, the auxiliary
 * input like the tinted writers') with the destination.  The pack frame is in stream colours, so the captured table is
 * applied to it exactly like a tinted writer's; SYW2_G1_HD_PACK_TINTED=0 therefore also turns their pack off. */
static BOOL is_remap_blend_writer(DWORD writer)
{
    return writer == G1_HD_BLEND_CLIP7 || writer == G1_HD_BLEND_FLIP7;
}

/* Copy the table now (the game may rewrite it later) and accept it only if it still
 * hashes to the digest the primitive hook computed over the same 256 bytes. */
static BYTE capture_lut(G1HdKey *key, const BYTE *table, DWORD table_digest)
{
    DWORD hash = 2166136261u, index;
    if (!table || !readable_range(table, G1_HD_LUT_BYTES)) return 0u;
    for (index = 0u; index < G1_HD_LUT_BYTES; ++index) {
        key->lut[index] = table[index];
        hash ^= table[index];
        hash *= 16777619u;
    }
    return hash == table_digest;
}

/* Shaded terrain writers: dst = inverse[T[pal(c)][s]] with s = shade[y * w + x] (aux = w * h
 * shade bytes, source = row RLE <skip, count, count pixels>). */
static BOOL is_shade_pack_writer(DWORD writer)
{
    return writer == G1_HD_TERRAIN_SHADE || writer == G1_HD_TERRAIN_CLIP_SHADE;
}

static void shade_free_copies(G1HdKey *key)
{
    if (key->shade_map) HeapFree(GetProcessHeap(), 0, key->shade_map);
    if (key->shade_src) HeapFree(GetProcessHeap(), 0, key->shade_src);
    if (key->shade_lut) HeapFree(GetProcessHeap(), 0, key->shade_lut);
    key->shade_map = NULL;
    key->shade_src = NULL;
    key->shade_lut = NULL;
    key->shade_src_bytes = 0u;
    key->shade_lut_bytes = 0u;
}

/* Copies the shade bytes (accepted only if they still hash to the digest the primitive hook
 * computed) and the row-RLE source now: both belong to the game and change after this draw. */
static void capture_shade(G1HdKey *key, const BYTE *source, const BYTE *shade,
                          DWORD shade_digest)
{
    DWORD bytes = key->width * key->height, hash = 2166136261u, index, row;
    const BYTE *cursor = source;
    key->shade_state = 2u;
    key->shade_reason = SHADE_REJECT_AUX;
    if (!shade || bytes > G1_HD_SHADE_MAP_LIMIT || !readable_range(shade, bytes)) return;
    key->shade_map = (BYTE *)HeapAlloc(GetProcessHeap(), 0, bytes);
    if (!key->shade_map) return;
    for (index = 0u; index < bytes; ++index) {
        key->shade_map[index] = shade[index];
        hash ^= shade[index];
        hash *= 16777619u;
    }
    if (hash != shade_digest) { shade_free_copies(key); return; }
    key->shade_reason = SHADE_REJECT_SOURCE;
    for (row = 0u; row < key->height; ++row) {
        if (!readable_range(cursor, 2u) || (DWORD)cursor[0] + cursor[1] > key->width ||
            !readable_range(cursor + 2, cursor[1])) { shade_free_copies(key); return; }
        cursor += 2u + cursor[1];
    }
    key->shade_src_bytes = (DWORD)(cursor - source);
    key->shade_src = (BYTE *)HeapAlloc(GetProcessHeap(), 0, key->shade_src_bytes);
    if (!key->shade_src) { shade_free_copies(key); return; }
    for (index = 0u; index < key->shade_src_bytes; ++index) key->shade_src[index] = source[index];
    key->shade_state = 1u;
}

/* Builds LUT_s[c] = F(c, s) from the live renderer tables for every shade level the tile uses,
 * then replays the original row RLE and compares F against what the original actually wrote.
 * Returns 0 on success, otherwise a SHADE_REJECT_* reason + 1. */
static BYTE shade_prepare(G1HdKey *key)
{
    const BYTE *renderer = G1_HD_RENDERER_BASE;
    const BYTE *palette = renderer + G1_HD_RENDERER_PALETTE;
    const BYTE *table = renderer + G1_HD_RENDERER_SHADE_TABLE;
    const BYTE *inverse = renderer + G1_HD_RENDERER_INVERSE;
    DWORD width = key->identity_width, height = key->identity_height;
    BYTE used[G1_HD_SHADE_LEVELS];
    DWORD level, color, row, slots = 0u;
    const BYTE *cursor;
    g_shade_slots = g_shade_checked = g_shade_mismatches = g_shade_first_x = g_shade_first_y = 0u;
    if (!readable_range(palette, 768u) ||
        !readable_range(table, G1_HD_SHADE_LEVELS * 64u * 2u) ||
        !readable_range(inverse, G1_HD_RENDERER_INVERSE_BYTES)) return SHADE_REJECT_TABLE + 1u;
    for (level = 0u; level < G1_HD_SHADE_LEVELS; ++level) used[level] = 0u;
    cursor = key->shade_src;
    for (row = 0u; row < height; ++row) {
        DWORD skip = cursor[0], count = cursor[1], i;
        for (i = 0u; i < count; ++i) {
            BYTE shade = key->shade_map[row * width + skip + i];
            if (shade >= G1_HD_SHADE_LEVELS) return SHADE_REJECT_RANGE + 1u;
            used[shade] = 1u;
        }
        cursor += 2u + count;
    }
    for (level = 0u; level < G1_HD_SHADE_LEVELS; ++level)
        key->shade_slot[level] = used[level] ? (BYTE)slots++ : 0xFFu;
    g_shade_slots = slots;
    if (slots != 0u) {
        key->shade_lut = (BYTE *)HeapAlloc(GetProcessHeap(), 0, slots * G1_HD_LUT_BYTES);
        if (!key->shade_lut) return SHADE_REJECT_RANGE + 1u;
        key->shade_lut_bytes = slots * G1_HD_LUT_BYTES;
    }
    for (level = 0u; level < G1_HD_SHADE_LEVELS; ++level) {
        if (!used[level]) continue;
        for (color = 0u; color < 256u; ++color) {
            DWORD component[3], mapped[3], c;
            for (c = 0u; c < 3u; ++c) {
                component[c] = palette[color * 3u + c];
                if (component[c] >= G1_HD_SHADE_LEVELS) return SHADE_REJECT_RANGE + 1u;
                mapped[c] = (DWORD)table[((component[c] << 6) + level) * 2u] |
                            ((DWORD)table[((component[c] << 6) + level) * 2u + 1u] << 8);
                if (mapped[c] >= 64u) return SHADE_REJECT_RANGE + 1u;
            }
            key->shade_lut[key->shade_slot[level] * G1_HD_LUT_BYTES + color] =
                inverse[(mapped[0] << 12) + (mapped[1] << 6) + mapped[2]];
        }
    }
    cursor = key->shade_src;
    for (row = 0u; row < height; ++row) {
        DWORD skip = cursor[0], count = cursor[1], i;
        for (i = 0u; i < count; ++i) {
            DWORD pixel = row * width + skip + i;
            if (!key->identity_written[pixel]) continue;
            ++g_shade_checked;
            if (key->identity_frame[row * key->identity_stride + skip + i] !=
                key->shade_lut[key->shade_slot[key->shade_map[pixel]] * G1_HD_LUT_BYTES + cursor[2 + i]]) {
                if (g_shade_mismatches++ == 0u) { g_shade_first_x = skip + i; g_shade_first_y = row; }
            }
        }
        cursor += 2u + count;
    }
    if (g_shade_mismatches != 0u) return SHADE_REJECT_SELFCHECK + 1u;
    return 0u;
}

/* hd[i] = LUT_{shade of the 1x cell}[hd[i]]: the original shade is kept on its 2x2 block. */
static DWORD shade_apply(const G1HdKey *key, BYTE *hd, DWORD hd_width, DWORD hd_height)
{
    DWORD x, y, key_color = 0u;
    for (y = 0u; y < hd_height; ++y) {
        for (x = 0u; x < hd_width; ++x) {
            BYTE shade, slot;
            if (hd[y * hd_width + x] == G1_HD_PACK_KEY) continue;
            shade = key->shade_map[(y >> 1) * key->identity_width + (x >> 1)];
            if (shade >= G1_HD_SHADE_LEVELS) continue;
            slot = key->shade_slot[shade];
            if (slot == 0xFFu) continue;
            hd[y * hd_width + x] = key->shade_lut[slot * G1_HD_LUT_BYTES + hd[y * hd_width + x]];
            if (hd[y * hd_width + x] == G1_HD_PACK_KEY) ++key_color;
        }
    }
    return key_color;
}

BOOL g1_hd_asset_enabled(void)
{
    initialize_environment();
    return g_hd_source_mode != 0u;
}

const char *g1_hd_asset_source_name(void)
{
    initialize_environment();
    if (g_hd_source_mode == 2u) return G1_HD_SOURCE_SCALE2X;
    if (g_hd_source_mode == 1u) return G1_HD_SOURCE_IDENTITY;
    return "nearest";
}

/* H-HDPAL: the screen palette is the renderer's PALETTEENTRY array (renderer + 0x15A0, 256 x R,G,B,flags): the file
 * palette loader 0x465600 and the array loader 0x465840 both fill it before CreatePalette/SetEntries.  (+0x419A0 is a
 * 6-bit copy made once by the LUT initialiser 0x465300 and never changed: imjin2.pal, the in-game colour semantics.)
 * Pack frames are indices quantised to one palette, so the pack directory is that palette's pal8.  In-game the game
 * only darkens imjin2.pal (day/night, fades: no entry brighter than start*4), and a darkened screen shows the same
 * picture, so such a screen uses the directory of start*4; any other screen (title, lobby, protocol ...) has its own
 * colour semantics and uses the pal8 of the exact entries.  A few brighter entries (animated colours) are tolerated.
 * The id is cached per GetTickCount value (one draw call costs nothing) and reset by g1_hd_asset_reset. */
#define G1_HD_PAL_FAMILY_TOLERANCE 8u
/* Key-log line when the screen palette changes: the 256 R,G,B triples in hex (diagnostic only; 1.6 KB per change). */
static void write_palette_log_line(const BYTE *entries, DWORD hash)
{
    static const char hex[] = "0123456789abcdef";
    char line[3400], pal[9];
    DWORD index, length, written;
    if (!g_hd_key_log_path[0]) return;
    if (g_hd_key_log == INVALID_HANDLE_VALUE) {
        g_hd_key_log = CreateFileA(g_hd_key_log_path, GENERIC_WRITE, FILE_SHARE_READ, NULL, CREATE_ALWAYS,
                                   FILE_ATTRIBUTE_NORMAL, NULL);
        if (g_hd_key_log == INVALID_HANDLE_VALUE) return;
    }
    g1_hd_pack_format_pal(pal, sizeof(pal), hash);
    length = (DWORD)wsprintfA(line, "{\"pal_change\":\"%s\",\"rgb\":\"", pal);
    for (index = 0u; index < 256u; ++index) {
        BYTE component;
        for (component = 0u; component < 3u; ++component) {
            BYTE value = entries[index * 4u + component];
            line[length++] = hex[value >> 4];
            line[length++] = hex[value & 15u];
        }
    }
    line[length++] = '\"';
    length += (DWORD)wsprintfA(line + length, ",\"start\":\"");
    for (index = 0u; index < 256u; ++index) {
        BYTE component;
        for (component = 0u; component < 3u; ++component) {
            BYTE value = G1_HD_RENDERER_BASE[G1_HD_RENDERER_PALETTE + index * 3u + component];
            line[length++] = hex[value >> 4];
            line[length++] = hex[value & 15u];
        }
    }
    line[length++] = '\"'; line[length++] = '}'; line[length++] = '\n';
    WriteFile(g_hd_key_log, line, length, &written, NULL);
}

DWORD g1_hd_asset_palette_digest(void)
{
    DWORD tick = GetTickCount();
    if (!g_pal_valid || tick != g_pal_tick) {
        const BYTE *entries = G1_HD_RENDERER_BASE + G1_HD_RENDERER_ENTRIES;
        const BYTE *start = G1_HD_RENDERER_BASE + G1_HD_RENDERER_PALETTE;
        DWORD hash = 2166136261u, start_hash = 2166136261u, index, brighter = 0u, id;
        BOOL family;
        if (readable_range(entries, 1024u)) {
            BOOL have_start = readable_range(start, 768u);
            for (index = 0u; index < 256u; ++index) {
                BOOL over = FALSE;
                DWORD component;
                for (component = 0u; component < 3u; ++component) {
                    BYTE value = entries[index * 4u + component];
                    BYTE reference = have_start ? (BYTE)(start[index * 3u + component] << 2) : 0u;
                    hash ^= value; hash *= 16777619u;
                    start_hash ^= reference; start_hash *= 16777619u;
                    if (value > reference) over = TRUE;
                }
                if (over) ++brighter;
            }
            family = have_start && brighter <= G1_HD_PAL_FAMILY_TOLERANCE;
        } else {
            hash = 0u;
            family = FALSE;
        }
        id = family ? start_hash : hash;
        if (g_pal_valid && id != g_pal_digest) ++g_pal_changes;
        if (id && id != g_pal_logged) {
            write_palette_log_line(entries, id);
            g_pal_logged = id;
        }
        g_pal_digest = id;
        g_pal_family = family;
        g_pal_tick = tick;
        g_pal_valid = TRUE;
    }
    return g_pal_digest;
}
DWORD g1_hd_asset_palette_family(void) { return g_pal_family ? 1u : 0u; }
DWORD g1_hd_asset_palette_changes(void) { return g_pal_changes; }
DWORD g1_hd_asset_pack_pal_misses(void) { return g_pack_pal_misses; }

static G1HdKey *find_key_for_request(DWORD source, DWORD writer,
                                     DWORD auxiliary, DWORD auxiliary_digest,
                                     DWORD width, DWORD height, DWORD digest, DWORD pal)
{
    DWORD index;
    for (index = 0u; index < g_key_count; ++index) {
        G1HdKey *key = &g_keys[index];
        if (key->source == source && key->writer == writer &&
            key->auxiliary == auxiliary &&
            key->auxiliary_digest == auxiliary_digest &&
            key->width == width && key->height == height &&
            key->digest == digest && key->pal == pal)
            return key;
    }
    return NULL;
}

/* Diagnostic JSON-lines log (SYW2_G1_HD_KEY_LOG): one "first" line per key with
 * the pack outcome, then draw-count milestones. */
static void write_key_log_line(const G1HdKey *key, const char *result, DWORD draws)
{
    static const char hex[] = "0123456789abcdef";
    char line[400], digest[9], pal[9];
    DWORD index, length, written;
    if (!g_hd_key_log_path[0]) return;
    if (g_hd_key_log == INVALID_HANDLE_VALUE) {
        g_hd_key_log = CreateFileA(g_hd_key_log_path, GENERIC_WRITE,
                                   FILE_SHARE_READ, NULL, CREATE_ALWAYS,
                                   FILE_ATTRIBUTE_NORMAL, NULL);
        if (g_hd_key_log == INVALID_HANDLE_VALUE) return;
    }
    for (index = 0u; index < 8u; ++index)
        digest[index] = hex[(key->digest >> (28u - index * 4u)) & 15u];
    digest[8] = '\0';
    g1_hd_pack_format_pal(pal, sizeof(pal), key->pal);
    length = (DWORD)wsprintfA(line,
        "{\"writer\":\"0x%08X\",\"w\":%u,\"h\":%u,\"digest\":\"%s\",\"pal\":\"%s\",\"aux\":%u,\"result\":\"%s\",\"draws\":%u,\"src\":\"0x%08X\"",
        (unsigned)key->writer, (unsigned)key->width, (unsigned)key->height,
        digest, pal, (unsigned)(key->auxiliary != 0u), result, (unsigned)draws,
        (unsigned)key->source);
    if (result[0] == 'r' && result[1] == 'e')
        length += (DWORD)wsprintfA(line + length,
            ",\"written\":%u,\"pack_opaque\":%u,\"written_keyed\":%u,\"opaque_unwritten\":%u,\"first_xy\":[%u,%u],\"last_xy\":[%u,%u]",
            (unsigned)g_reject_written, (unsigned)g_reject_pack_opaque,
            (unsigned)g_reject_written_keyed, (unsigned)g_reject_opaque_unwritten,
            (unsigned)g_reject_first_x, (unsigned)g_reject_first_y,
            (unsigned)g_reject_last_x, (unsigned)g_reject_last_y);
    if (result[0] == 's' && result[1] == 'h' && result[6] == 'h')
        length += (DWORD)wsprintfA(line + length, ",\"slots\":%u,\"selfcheck\":%u",
                                   (unsigned)g_shade_slots, (unsigned)g_shade_checked);
    else if (result[0] == 's' && result[1] == 'h')
        length += (DWORD)wsprintfA(line + length,
            ",\"reason\":\"%s\",\"selfcheck\":%u,\"mismatches\":%u,\"first_xy\":[%u,%u]",
            g_shade_reason_names[g_shade_last_reason], (unsigned)g_shade_checked,
            (unsigned)g_shade_mismatches, (unsigned)g_shade_first_x, (unsigned)g_shade_first_y);
    line[length++] = '}';
    line[length++] = '\n';
    WriteFile(g_hd_key_log, line, length, &written, NULL);
}

/* Draw-count milestones (1, 2, 4, 8 ... then every 64th) keep the log small
 * while bounding each key's total draws to within 63 of its last line. */
static void note_key_draw(G1HdKey *key)
{
    DWORD draws = ++key->draws;
    if (!g_hd_key_log_path[0]) return;
    if (draws < 64u ? (draws & (draws - 1u)) == 0u : (draws & 63u) == 0u)
        write_key_log_line(key, "draws", draws);
}

/* Eviction (H-HDK0): the least recently begun key other than `exclude`.  With
 * need_frames only keys that still hold cached frames qualify.  Nothing outside
 * begin..end keeps a key pointer, so freeing a finished key's frames is safe. */
static G1HdKey *pick_lru_key(const G1HdKey *exclude, BOOL need_frames)
{
    G1HdKey *victim = NULL;
    DWORD index;
    for (index = 0u; index < g_key_count; ++index) {
        G1HdKey *key = &g_keys[index];
        if (key == exclude || (need_frames && !key->identity_frame && !key->hd_frame)) continue;
        if (!victim || key->last_draw < victim->last_draw) victim = key;
    }
    return victim;
}

/* with_shade: the key goes away; without it (byte pressure) the shaded terrain copies stay so the
 * next bind can rebuild the HD frame (the shade tables are built once at start). */
static void drop_key_frames(G1HdKey *key, BOOL with_shade)
{
    if (key->identity_frame) {
        HeapFree(GetProcessHeap(), 0, key->identity_frame);
        g_identity_cache_bytes -= key->identity_bytes + key->identity_mask_bytes;
    }
    if (key->identity_written) HeapFree(GetProcessHeap(), 0, key->identity_written);
    if (key->hd_frame) {
        HeapFree(GetProcessHeap(), 0, key->hd_frame);
        g_identity_cache_bytes -= key->hd_bytes;
    }
    if (with_shade) shade_free_copies(key);
    key->identity_frame = NULL;
    key->identity_written = NULL;
    key->hd_frame = NULL;
    key->identity_bytes = key->identity_mask_bytes = 0u;
    key->identity_stride = key->identity_width = key->identity_height = 0u;
    key->hd_stride = key->hd_width = key->hd_height = key->hd_bytes = 0u;
    key->pack_applied = 0u;
}

/* Cache bytes over budget: free the frames of the least recently begun other keys
 * (their identities stay, the next draw rebinds) until `needed` more bytes fit. */
static BOOL make_room_for(DWORD needed, const G1HdKey *exclude)
{
    while (g_identity_cache_bytes > G1_HD_CACHE_BYTE_LIMIT - needed) {
        G1HdKey *victim = pick_lru_key(exclude, TRUE);
        if (!victim) return FALSE;
        write_key_log_line(victim, "evict_bytes", victim->draws);
        drop_key_frames(victim, FALSE);
        ++g_identity_evictions;
    }
    return TRUE;
}

void g1_hd_asset_reset(void)
{
    DWORD index;
    g_pal_valid = FALSE;
    volatile BYTE *mask = g_identity_mask;
    for (index = 0u; index < g_key_count; ++index) {
        if (g_keys[index].identity_frame) {
            HeapFree(GetProcessHeap(), 0, g_keys[index].identity_frame);
            g_keys[index].identity_frame = NULL;
        }
        if (g_keys[index].identity_written) {
            HeapFree(GetProcessHeap(), 0, g_keys[index].identity_written);
            g_keys[index].identity_written = NULL;
        }
        if (g_keys[index].hd_frame) {
            HeapFree(GetProcessHeap(), 0, g_keys[index].hd_frame);
            g_keys[index].hd_frame = NULL;
        }
        shade_free_copies(&g_keys[index]);
    }
    g_key_count = 0u;
    g_identity_pixels = 0u;
    g_invalid_sources = 0u;
    g_identity_events = 0u;
    g_identity_lookup_hits = 0u;
    g_identity_lookup_misses = 0u;
    g_identity_cache_bytes = 0u;
    g_draw_clock = 0u;
    g_identity_evictions = 0u;
    g_identity_cache_inserts = 0u;
    g_identity_cache_hits = 0u;
    g_identity_cache_misses = 0u;
    g_identity_cache_refreshes = 0u;
    g_identity_negative_lookup_attempts = 0u;
    g_identity_negative_lookup_misses = 0u;
    g_identity_key_mismatches = 0u;
    g_scale2x_blocks = 0u;
    g_scale2x_subpixel_differences = 0u;
    g_scale2x_palette_violations = 0u;
    g_pack_hits = 0u;
    g_pack_misses = 0u;
    g_pack_rejects = 0u;
    g_pack_skipped_aux = 0u;
    g_pack_lookup_blocks = 0u;
    g_pack_lut_hits = 0u;
    g_pack_lut_rejects = 0u;
    g_pack_lut_key_color = 0u;
    g_pack_lut_nonidentity = 0u;
    g_pack_flip_hits = 0u;
    g_pack_flip_misses = 0u;
    g_pack_flip_rejects = 0u;
    g_pack_blend_hits = 0u;
    g_pack_blend_misses = 0u;
    g_pack_blend_rejects = 0u;
    g_pack_ext_hits = 0u;
    g_pack_ext_misses = 0u;
    g_pack_ext_rejects = 0u;
    g_pack_shade_hits = 0u;
    for (index = 0u; index < SHADE_REJECT_REASONS; ++index) g_pack_shade_rejects[index] = 0u;
    g_pack_shade_selfcheck_pixels = 0u;
    g_pack_shade_multi_keys = 0u;
    g_pack_shade_key_color = 0u;
    g_pack_shade_lut_bytes = 0u;
    g_pack_pal_misses = 0u;
    g_pal_changes = 0u;
    g_current_valid = 0;
    g_current_key = NULL;
    g_current_origin_x = 0u;
    g_current_origin_y = 0u;
    g_full_frame_calls = 0u;
    g_bbox_calls = 0u;
    g_clipped_calls = 0u;
    g_identity_cache_hit_bytes = 0u;
    g_identity_cache_insert_bytes = 0u;
    g_identity_cache_refresh_bytes = 0u;
    g_clip_replay_mismatches = 0u;
    g_last_clip_mismatch_x = 0u;
    g_last_clip_mismatch_y = 0u;
    g_last_clip_screen_value = 0u;
    g_last_clip_replay_value = 0u;
    g1_perf_sections_reset();
    for (index = 0u; index < G1_HD_PIXEL_LIMIT; ++index) mask[index] = 0u;
}

BOOL g1_hd_asset_begin(const BYTE *source, DWORD writer, DWORD width, DWORD height,
                       LONG origin_x, LONG origin_y)
{
    return g1_hd_asset_begin_with_aux(source, writer, NULL, 0u, width, height,
                                      origin_x, origin_y);
}

BOOL g1_hd_asset_begin_with_aux(const BYTE *source, DWORD writer,
                                const BYTE *auxiliary,
                                DWORD auxiliary_digest, DWORD width,
                                DWORD height, LONG origin_x, LONG origin_y)
{
    DWORD digest, pal;
    G1HdKey *key, *slot;
    BOOL clipped, appended = FALSE;
    ULONGLONG started = g1_perf_sections_start();
    if (!g1_hd_asset_enabled() || !source || width == 0u || height == 0u ||
        width > 800u || height > 600u || !readable_source(source)) {
        if (g1_hd_asset_enabled()) ++g_invalid_sources;
        g_current_valid = 0;
        g_current_key = NULL;
        return FALSE;
    }
    clipped = origin_x < 0 || origin_y < 0 ||
              origin_x > (LONG)(800u - width) ||
              origin_y > (LONG)(600u - height);
    digest = hash_source(source);
    pal = g1_hd_asset_palette_digest();
    key = find_key_for_request((DWORD)(ULONG_PTR)source, writer,
                               (DWORD)(ULONG_PTR)auxiliary, auxiliary_digest,
                               width, height, digest, pal);
    if (key) {
        key->last_draw = ++g_draw_clock;
        note_key_draw(key);
        ++g_bbox_calls;
        if (clipped) ++g_clipped_calls;
        g1_perf_sections_end(G1_PERF_HASH_LOOKUP, started, G1_HD_DIGEST_BYTES);
        ++g_identity_events;
        if (key->identity_frame) ++g_identity_cache_hits;
        else ++g_identity_cache_misses;
        g_current_key = key;
        g_current_source = source;
        g_current_origin_x = origin_x;
        g_current_origin_y = origin_y;
        g_current_valid = 1;
        return TRUE;
    }
    if (g_key_count >= g_key_limit) {
        slot = pick_lru_key(g_current_key, FALSE);
        if (!slot) {
            ++g_invalid_sources;
            g_current_valid = 0;
            g_current_key = NULL;
            return FALSE;
        }
        write_key_log_line(slot, "evict_key", slot->draws);
        drop_key_frames(slot, TRUE);
        ++g_identity_evictions;
    } else {
        slot = &g_keys[g_key_count];
        appended = TRUE;
    }
    memset(slot, 0, sizeof(*slot));
    slot->source = (DWORD)(ULONG_PTR)source;
    slot->writer = writer;
    slot->auxiliary = (DWORD)(ULONG_PTR)auxiliary;
    slot->auxiliary_digest = auxiliary_digest;
    slot->width = width;
    slot->height = height;
    slot->digest = digest;
    slot->pal = pal;
    slot->identity_frame = NULL;
    slot->identity_written = NULL;
    slot->identity_stride = 0u;
    slot->identity_width = 0u;
    slot->identity_height = 0u;
    slot->identity_bytes = 0u;
    slot->identity_mask_bytes = 0u;
    slot->hd_frame = NULL;
    slot->hd_stride = 0u;
    slot->hd_width = 0u;
    slot->hd_height = 0u;
    slot->hd_bytes = 0u;
    slot->pack_state = PACK_UNTRIED;
    slot->pack_applied = 0u;
    slot->lut_valid = 0u;
    if (auxiliary && g_hd_pack_dir[0] && g_hd_source_mode == 2u &&
        ((!g_hd_tinted_off && (is_tinted_pack_writer(writer) || is_remap_blend_writer(writer))) ||
         (!g_hd_flip_off && is_flip_pack_writer(writer))))
        slot->lut_valid = capture_lut(slot, auxiliary,
                                                    auxiliary_digest);
    slot->shade_state = 0u;
    slot->shade_reason = 0u;
    slot->shade_map = NULL;
    slot->shade_src = NULL;
    slot->shade_src_bytes = 0u;
    slot->shade_lut = NULL;
    slot->shade_lut_bytes = 0u;
    if (auxiliary && g_hd_pack_dir[0] && !g_hd_shade_off && g_hd_source_mode == 2u &&
        is_shade_pack_writer(writer))
        capture_shade(slot, source, auxiliary, auxiliary_digest);
    slot->draws = 0u;
    slot->last_draw = ++g_draw_clock;
    g_current_key = slot;
    g_current_source = source;
    note_key_draw(g_current_key);
    g_current_origin_x = origin_x;
    g_current_origin_y = origin_y;
    if (appended) ++g_key_count;
    ++g_bbox_calls;
    if (clipped) ++g_clipped_calls;
    ++g_identity_events;
    ++g_identity_cache_misses;
    g1_perf_sections_end(G1_PERF_HASH_LOOKUP, started, G1_HD_DIGEST_BYTES);
    g_current_valid = 1;
    return TRUE;
}

BOOL g1_hd_asset_needs_identity_frame(void)
{
    return g_current_valid != 0 && g_current_key &&
           !g_current_key->identity_frame;
}

BOOL g1_hd_asset_current_ready(void)
{
    return g_current_valid != 0 && g_current_key &&
           g_current_key->identity_frame != NULL;
}

BOOL g1_hd_asset_verify_unclipped_frame(const BYTE *screen_frame,
                                        const BYTE *unclipped_frame,
                                        DWORD frame_stride,
                                        DWORD unclipped_stride,
                                        DWORD width, DWORD height)
{
    return g1_hd_asset_verify_unclipped_frame_in_viewport(
        screen_frame, unclipped_frame, frame_stride, unclipped_stride,
        width, height, 0, 0, 799, 599);
}

BOOL g1_hd_asset_verify_unclipped_frame_in_viewport(
    const BYTE *screen_frame, const BYTE *unclipped_frame,
    DWORD frame_stride, DWORD unclipped_stride, DWORD width, DWORD height,
    LONG viewport_left, LONG viewport_top, LONG viewport_right,
    LONG viewport_bottom)
{
    ULONGLONG compare_started = g1_perf_sections_start();
    LONG visible_left, visible_top, visible_right, visible_bottom;
    DWORD y;
    if (g_current_valid == 0 || !g_current_key || !screen_frame ||
        !unclipped_frame || frame_stride < 800u ||
        unclipped_stride < width || width == 0u ||
        height == 0u || width > 800u || height > 600u ||
        viewport_right < viewport_left || viewport_bottom < viewport_top) {
        g_current_valid = 0;
        return FALSE;
    }
    visible_left = g_current_origin_x > viewport_left ? g_current_origin_x : viewport_left;
    visible_top = g_current_origin_y > viewport_top ? g_current_origin_y : viewport_top;
    visible_right = g_current_origin_x + (LONG)width;
    visible_bottom = g_current_origin_y + (LONG)height;
    if (visible_right > viewport_right + 1) visible_right = viewport_right + 1;
    if (visible_bottom > viewport_bottom + 1) visible_bottom = viewport_bottom + 1;
    if (visible_left < 0) visible_left = 0;
    if (visible_top < 0) visible_top = 0;
    if (visible_right > 800) visible_right = 800;
    if (visible_bottom > 600) visible_bottom = 600;
    if (visible_right <= visible_left || visible_bottom <= visible_top) {
        g1_perf_sections_end(G1_PERF_BIND_COMPARE, compare_started, 0u);
        return TRUE;
    }
    for (y = (DWORD)visible_top; y < (DWORD)visible_bottom; ++y) {
        DWORD x;
        DWORD local_y = (DWORD)((LONG)y - g_current_origin_y);
        for (x = (DWORD)visible_left; x < (DWORD)visible_right; ++x) {
            DWORD local_x = (DWORD)((LONG)x - g_current_origin_x);
            if (screen_frame[y * frame_stride + x] !=
                unclipped_frame[local_y * unclipped_stride + local_x]) {
                ++g_clip_replay_mismatches;
                g_last_clip_mismatch_x = x;
                g_last_clip_mismatch_y = y;
                g_last_clip_screen_value = screen_frame[y * frame_stride + x];
                g_last_clip_replay_value =
                    unclipped_frame[local_y * unclipped_stride + local_x];
                g_current_valid = 0;
                g1_perf_sections_end(G1_PERF_BIND_COMPARE, compare_started,
                                     (ULONGLONG)(visible_right - visible_left) *
                                     (visible_bottom - visible_top));
                return FALSE;
            }
        }
    }
    g1_perf_sections_end(G1_PERF_BIND_COMPARE, compare_started,
                         (ULONGLONG)(visible_right - visible_left) *
                         (visible_bottom - visible_top));
    return TRUE;
}

static BOOL build_scale2x(const BYTE *source, DWORD source_stride,
                          const BYTE *written, DWORD written_stride,
                          DWORD width, DWORD height, BYTE *destination,
                          DWORD destination_stride)
{
    ULONGLONG perf_started = g1_perf_sections_start();
    BYTE palette[256];
    DWORD x, y, i;
    if (!g1_scale2x_build_masked(source, source_stride, written, written_stride,
                                 width, height, destination, destination_stride)) {
        ++g_invalid_sources;
        g1_perf_sections_end(G1_PERF_SCALE2X_BUILD, perf_started, 0u);
        return FALSE;
    }
    for (i = 0u; i < 256u; ++i) palette[i] = 0u;
    for (y = 0u; y < height; ++y)
        for (x = 0u; x < width; ++x)
            if (written[y * written_stride + x])
                palette[source[y * source_stride + x]] = 1u;
    for (y = 0u; y < height; ++y) {
        for (x = 0u; x < width; ++x) {
            BYTE e, p0, p1, p2, p3;
            BYTE *row;
            if (!written[y * written_stride + x]) continue;
            e = source[y * source_stride + x];
            row = destination + (y * 2u) * destination_stride + x * 2u;
            p0 = row[0]; p1 = row[1];
            p2 = row[destination_stride]; p3 = row[destination_stride + 1u];
            ++g_scale2x_blocks;
            if (p0 != e) ++g_scale2x_subpixel_differences;
            if (p1 != e) ++g_scale2x_subpixel_differences;
            if (p2 != e) ++g_scale2x_subpixel_differences;
            if (p3 != e) ++g_scale2x_subpixel_differences;
            if (!palette[p0]) ++g_scale2x_palette_violations;
            if (!palette[p1]) ++g_scale2x_palette_violations;
            if (!palette[p2]) ++g_scale2x_palette_violations;
            if (!palette[p3]) ++g_scale2x_palette_violations;
        }
    }
    g1_perf_sections_end(G1_PERF_SCALE2X_BUILD, perf_started,
                          (ULONGLONG)width * height);
    return TRUE;
}

/* Counts written pixels against the pack's opaque 2x2 blocks for the key-log reject line. */
static void note_reject_detail(const G1HdKey *key, const BYTE *hd)
{
    DWORD x, y, width = key->identity_width, height = key->identity_height;
    g_reject_written = g_reject_pack_opaque = 0u;
    g_reject_written_keyed = g_reject_opaque_unwritten = 0u;
    for (y = 0u; y < height; ++y) {
        for (x = 0u; x < width; ++x) {
            const BYTE *top = hd + y * 2u * width * 2u + x * 2u;
            BOOL opaque = top[0] != G1_HD_PACK_KEY && top[1] != G1_HD_PACK_KEY &&
                          top[width * 2u] != G1_HD_PACK_KEY && top[width * 2u + 1u] != G1_HD_PACK_KEY;
            BOOL written = key->identity_written[y * width + x] != 0u;
            if (written) ++g_reject_written;
            if (opaque) ++g_reject_pack_opaque;
            if (written && !opaque) ++g_reject_written_keyed;
            if (opaque && !written) {
                if (g_reject_opaque_unwritten++ == 0u) { g_reject_first_x = x; g_reject_first_y = y; }
                g_reject_last_x = x;
                g_reject_last_y = y;
            }
        }
    }
}

/* <pack>\<pal8>\<name>; a missing pal directory (no frame was ever quantised to this screen palette) is counted. */
static BOOL pack_file_path(char *path, DWORD path_size, DWORD pal, const char *name)
{
    char pal8[9];
    DWORD directory_length = lstrlenA(g_hd_pack_dir), name_length = lstrlenA(name);
    if (!directory_length || !g1_hd_pack_format_pal(pal8, sizeof(pal8), pal) ||
        directory_length + 1u + 8u + 1u + name_length >= path_size) return FALSE;
    lstrcpyA(path, g_hd_pack_dir);
    if (path[directory_length - 1u] != '\\' && path[directory_length - 1u] != '/')
        path[directory_length++] = '\\';
    lstrcpyA(path + directory_length, pal8);
    directory_length += 8u;
    path[directory_length++] = G1_HD_PATH_SEPARATOR;
    lstrcpyA(path + directory_length, name);
    return TRUE;
}

static void note_missing_file(const char *path)
{
    char directory[MAX_PATH];
    DWORD length = lstrlenA(path);
    lstrcpyA(directory, path);
    while (length && directory[length - 1u] != G1_HD_PATH_SEPARATOR) --length;
    if (length) directory[length - 1u] = '\0';
    if (GetFileAttributesA(directory) == INVALID_FILE_ATTRIBUTES) ++g_pack_pal_misses;
}

/* Mirrors every pack row left to right (0x466B50 draws the unflipped frame's columns in reverse). */
static void flip_pack_rows(BYTE *hd, DWORD hd_width, DWORD hd_height)
{
    DWORD row, left;
    for (row = 0u; row < hd_height; ++row) {
        BYTE *line = hd + row * hd_width;
        for (left = 0u; left < hd_width / 2u; ++left) {
            BYTE swap = line[left];
            line[left] = line[hd_width - 1u - left];
            line[hd_width - 1u - left] = swap;
        }
    }
}

/* H-HDN0: the name of a picture whose first 128 source bytes collide with another one's.  <pack>\<pal8>\h<digest8>_<w>x<h>.amb
 * holds the prefix length L; the frame is h<digest8>_<w>x<h>_<L>_<p8>.idx8 with p8 = FNV-1a of the first L source bytes of
 * the stream being drawn.  Computed only for a key whose plain name has no file, once per key.  Sets g_last_ext:
 * 0 no marker (a plain miss), 1 the extended file was tried (outcome = the caller's state), 2 the marker was unusable. */
static HANDLE open_extended_pack_file(const G1HdKey *key)
{
    char name[64], path[MAX_PATH];
    BYTE marker[4];
    DWORD marker_high = 0u, marker_bytes = 0u, length, hash = 2166136261u, index;
    HANDLE file;
    const BYTE *source = g_current_source;
    g_last_ext = 0u;
    if (g_hd_ext_off || !g1_hd_pack_marker_name(name, sizeof(name), key->digest, key->width, key->height) ||
        !pack_file_path(path, sizeof(path), key->pal, name)) return INVALID_HANDLE_VALUE;
    file = CreateFileA(path, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (file == INVALID_HANDLE_VALUE) return INVALID_HANDLE_VALUE;
    g_last_ext = 2u;
    if (GetFileSize(file, &marker_high) != 4u || marker_high != 0u ||
        !ReadFile(file, marker, 4u, &marker_bytes, NULL) || marker_bytes != 4u) {
        CloseHandle(file);
        return INVALID_HANDLE_VALUE;
    }
    CloseHandle(file);
    length = (DWORD)marker[0] | ((DWORD)marker[1] << 8) | ((DWORD)marker[2] << 16) | ((DWORD)marker[3] << 24);
    if (length < G1_HD_PACK_EXT_MIN || length > G1_HD_PACK_EXT_MAX || !readable_range(source, length))
        return INVALID_HANDLE_VALUE;
    for (index = 0u; index < length; ++index) {
        hash ^= source[index];
        hash *= 16777619u;
    }
    if (!g1_hd_pack_ext_name(name, sizeof(name), key->digest, key->width, key->height, length, hash) ||
        !pack_file_path(path, sizeof(path), key->pal, name)) return INVALID_HANDLE_VALUE;
    g_last_ext = 1u;
    return CreateFileA(path, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
}

/* Reads <pack>\<pal8>\h<digest8>_<w>x<h>.idx8 (or its H-HDN0 extended name) over the Scale2x frame.  Returns the
 * state: HIT (hd filled), MISS (no file), REJECT (size or silhouette wrong).  A flip writer
 * mirrors the file's frame before the silhouette check: the identity mask is the flipped one. */
static BYTE read_pack_frame(const G1HdKey *key, BYTE *hd, DWORD hd_bytes)
{
    char name[40], path[MAX_PATH];
    DWORD file_high = 0u;
    DWORD file_bytes, bytes_read = 0u;
    HANDLE file;
    BYTE state = PACK_REJECT;
    g_last_ext = 0u;
    if (key->width != key->identity_width || key->height != key->identity_height ||
        !g1_hd_pack_name(name, sizeof(name), key->digest, key->width, key->height) ||
        !pack_file_path(path, sizeof(path), key->pal, name))
        return PACK_REJECT;
    file = CreateFileA(path, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING,
                       FILE_ATTRIBUTE_NORMAL, NULL);
    if (file == INVALID_HANDLE_VALUE) {
        note_missing_file(path);
        file = open_extended_pack_file(key);
        if (file == INVALID_HANDLE_VALUE) return PACK_MISS;
    }
    file_bytes = GetFileSize(file, &file_high);
    if (file_high == 0u && file_bytes == hd_bytes &&
        ReadFile(file, hd, hd_bytes, &bytes_read, NULL) && bytes_read == hd_bytes) {
        if (is_flip_pack_writer(key->writer) || is_flip_blend_writer(key->writer))
            flip_pack_rows(hd, key->width * 2u, key->height * 2u);
        if (g1_hd_pack_valid(key->identity_written, key->identity_width,
                             key->identity_width, key->identity_height, hd, hd_bytes))
            state = PACK_HIT;
        else
            note_reject_detail(key, hd);
    }
    CloseHandle(file);
    return state;
}

static BOOL build_hd_frame(G1HdKey *key)
{
    DWORD hd_width, hd_height, hd_bytes;
    BYTE *hd;
    if (!key || !key->identity_frame || !key->identity_written ||
        g_hd_source_mode != 2u) return TRUE;
    hd_width = key->identity_width * 2u;
    hd_height = key->identity_height * 2u;
    hd_bytes = hd_width * hd_height;
    if (hd_width == 0u || hd_height == 0u || hd_bytes < hd_width ||
        hd_bytes > G1_HD_CACHE_BYTE_LIMIT ||
        !make_room_for(hd_bytes, key)) return FALSE;
    hd = (BYTE *)HeapAlloc(GetProcessHeap(), 0, hd_bytes);
    if (!hd) return FALSE;
    key->pack_applied = 0u;
    if (key->pack_state == PACK_UNTRIED || key->pack_state == PACK_HIT) {
        BYTE state;
        BOOL lut_pack = FALSE, shade_pack = FALSE;
        g_last_ext = 0u;
        if (!g_hd_pack_dir[0]) state = PACK_NONE;
        else if (key->auxiliary != 0u) {
            if (((is_tinted_pack_writer(key->writer) || is_remap_blend_writer(key->writer)) && !g_hd_tinted_off) ||
                (is_flip_pack_writer(key->writer) && !g_hd_flip_off)) {
                if (!key->lut_valid) state = PACK_LUT_REJECT;
                else {
                    lut_pack = TRUE;
                    state = read_pack_frame(key, hd, hd_bytes);
                }
            } else if (is_shade_pack_writer(key->writer) && !g_hd_shade_off) {
                if (key->shade_state != 1u) {
                    g_shade_last_reason = key->shade_reason;
                    state = PACK_SHADE_REJECT;
                } else {
                    shade_pack = TRUE;
                    state = read_pack_frame(key, hd, hd_bytes);
                }
            } else state = PACK_SKIP_AUX;
        } else state = read_pack_frame(key, hd, hd_bytes);
        if (state == PACK_HIT && lut_pack) {
            DWORD index, key_color = 0u;
            for (index = 0u; index < hd_bytes; ++index) {
                if (hd[index] == G1_HD_PACK_KEY) continue;
                hd[index] = key->lut[hd[index]];
                if (hd[index] == G1_HD_PACK_KEY) ++key_color;
            }
            if (key->pack_state == PACK_UNTRIED) {
                BOOL identity = TRUE;
                for (index = 0u; index < G1_HD_LUT_BYTES; ++index)
                    if (key->lut[index] != (BYTE)index) identity = FALSE;
                ++g_pack_lut_hits;
                g_pack_lut_key_color += key_color;
                if (!identity) ++g_pack_lut_nonidentity;
            }
        }
        if (state == PACK_HIT && shade_pack) {
            DWORD key_color, level, distinct = 0u;
            if (key->pack_state == PACK_UNTRIED) {
                BYTE failed = shade_prepare(key);
                if (failed) {
                    g_shade_last_reason = (BYTE)(failed - 1u);
                    state = PACK_SHADE_REJECT;
                }
            }
            if (state == PACK_HIT) {
                key_color = shade_apply(key, hd, hd_width, hd_height);
                if (key->pack_state == PACK_UNTRIED) {
                    for (level = 0u; level < G1_HD_SHADE_LEVELS; ++level)
                        if (key->shade_slot[level] != 0xFFu) ++distinct;
                    ++g_pack_shade_hits;
                    g_pack_shade_selfcheck_pixels += g_shade_checked;
                    g_pack_shade_key_color += key_color;
                    g_pack_shade_lut_bytes += key->shade_lut_bytes;
                    if (distinct > 1u) ++g_pack_shade_multi_keys;
                }
            }
            if (key->shade_src) {
                HeapFree(GetProcessHeap(), 0, key->shade_src);
                key->shade_src = NULL;
                key->shade_src_bytes = 0u;
            }
        }
        if (key->pack_state == PACK_UNTRIED) {
            if (state == PACK_HIT) ++g_pack_hits;
            else if (state == PACK_MISS) ++g_pack_misses;
            else if (state == PACK_REJECT) ++g_pack_rejects;
            else if (state == PACK_SKIP_AUX) ++g_pack_skipped_aux;
            else if (state == PACK_LUT_REJECT) ++g_pack_lut_rejects;
            else if (state == PACK_SHADE_REJECT) ++g_pack_shade_rejects[g_shade_last_reason];
            if (g_last_ext == 2u) ++g_pack_ext_rejects;
            else if (g_last_ext == 1u) {
                if (state == PACK_HIT) ++g_pack_ext_hits;
                else if (state == PACK_MISS) ++g_pack_ext_misses;
                else if (state == PACK_REJECT) ++g_pack_ext_rejects;
            }
            if (key->writer == G1_HD_BLEND_RLE || key->writer == G1_HD_BLEND_WRLE || key->writer == G1_HD_BLEND_CLIP ||
                is_flip_blend_writer(key->writer) || is_remap_blend_writer(key->writer)) {
                if (state == PACK_HIT) ++g_pack_blend_hits;
                else if (state == PACK_MISS) ++g_pack_blend_misses;
                else if (state == PACK_REJECT || state == PACK_LUT_REJECT) ++g_pack_blend_rejects;
            }
            if (is_flip_pack_writer(key->writer)) {
                if (state == PACK_HIT) ++g_pack_flip_hits;
                else if (state == PACK_MISS) ++g_pack_flip_misses;
                else if (state == PACK_REJECT || state == PACK_LUT_REJECT) ++g_pack_flip_rejects;
            }
            write_key_log_line(key, state == PACK_HIT ? (lut_pack ? "lut_hit" : shade_pack ? "shade_hit" : "hit") :
                                    state == PACK_MISS ? "miss" :
                                    state == PACK_REJECT ? "reject" :
                                    state == PACK_SKIP_AUX ? "skip_aux" :
                                    state == PACK_LUT_REJECT ? "lut_reject" :
                                    state == PACK_SHADE_REJECT ? "shade_reject" : "nopack", 0u);
        }
        key->pack_state = state;
    }
    if (key->pack_state == PACK_HIT) {
        key->pack_applied = 1u;
    } else if (!build_scale2x(key->identity_frame, key->identity_stride,
                              key->identity_written, key->identity_width,
                              key->identity_width, key->identity_height, hd, hd_width)) {
        HeapFree(GetProcessHeap(), 0, hd);
        return FALSE;
    }
    key->hd_frame = hd;
    key->hd_stride = hd_width;
    key->hd_width = hd_width;
    key->hd_height = hd_height;
    key->hd_bytes = hd_bytes;
    g_identity_cache_bytes += hd_bytes;
    return TRUE;
}

BOOL g1_hd_asset_compare_visible_frame(const BYTE *frame, DWORD frame_stride,
                                       DWORD width, DWORD height)
{
    return g1_hd_asset_compare_visible_frame_in_viewport(
        frame, frame_stride, width, height, 0, 0, 799, 599);
}

/* The original writer clips to the renderer viewport, so pixels outside it are
 * never written to the live frame while the identity frame (full-viewport
 * replay) holds them.  Comparing them would evict a correct identity frame on
 * every hit; only the screen-and-viewport intersection is comparable. */
BOOL g1_hd_asset_compare_visible_frame_in_viewport(
    const BYTE *frame, DWORD frame_stride, DWORD width, DWORD height,
    LONG viewport_left, LONG viewport_top, LONG viewport_right,
    LONG viewport_bottom)
{
    ULONGLONG compare_started = g1_perf_sections_start();
    DWORD y;
    LONG left, top, right, bottom;
    G1ScratchBounds visible;
    if (g_current_valid == 0 || !g_current_key ||
        !g_current_key->identity_frame || !frame || frame_stride < width ||
        width == 0u || height == 0u || width > 800u || height > 600u ||
        g_current_key->identity_width != width ||
        g_current_key->identity_height != height ||
        g_current_key->identity_stride != width ||
        viewport_right < viewport_left || viewport_bottom < viewport_top)
        return FALSE;
    if (!g1_scratch_intersection(g_current_origin_x, g_current_origin_y,
                                 width, height, 800u, 600u, &visible) ||
        visible.width == 0u || visible.height == 0u) return FALSE;
    left = (LONG)visible.x > viewport_left ? (LONG)visible.x : viewport_left;
    top = (LONG)visible.y > viewport_top ? (LONG)visible.y : viewport_top;
    right = (LONG)(visible.x + visible.width);
    bottom = (LONG)(visible.y + visible.height);
    if (right > viewport_right + 1) right = viewport_right + 1;
    if (bottom > viewport_bottom + 1) bottom = viewport_bottom + 1;
    if (right <= left || bottom <= top) return FALSE;
    visible.x = (DWORD)left;
    visible.y = (DWORD)top;
    visible.width = (DWORD)(right - left);
    visible.height = (DWORD)(bottom - top);
    for (y = visible.y; y < visible.y + visible.height; ++y) {
        DWORD x;
        LONG local_y = (LONG)y - g_current_origin_y;
        const BYTE *source_row = frame + y * frame_stride;
        const BYTE *cached_row = g_current_key->identity_frame +
                                 (DWORD)local_y * width;
        for (x = visible.x; x < visible.x + visible.width; ++x) {
            LONG local_x = (LONG)x - g_current_origin_x;
            if (source_row[x] != cached_row[(DWORD)local_x]) {
                HeapFree(GetProcessHeap(), 0, g_current_key->identity_frame);
                g_current_key->identity_frame = NULL;
                if (g_current_key->identity_written) {
                    HeapFree(GetProcessHeap(), 0, g_current_key->identity_written);
                    g_current_key->identity_written = NULL;
                }
                if (g_current_key->hd_frame) {
                    HeapFree(GetProcessHeap(), 0, g_current_key->hd_frame);
                    g_current_key->hd_frame = NULL;
                }
                g_identity_cache_bytes -= g_current_key->identity_bytes;
                g_identity_cache_bytes -= g_current_key->identity_mask_bytes;
                g_identity_cache_bytes -= g_current_key->hd_bytes;
                g_current_key->identity_bytes = 0u;
                g_current_key->identity_mask_bytes = 0u;
                g_current_key->identity_stride = 0u;
                g_current_key->identity_width = 0u;
                g_current_key->identity_height = 0u;
                g_current_key->hd_stride = 0u;
                g_current_key->hd_width = 0u;
                g_current_key->hd_height = 0u;
                g_current_key->hd_bytes = 0u;
                g_current_key->pack_applied = 0u;
                if (g_current_key->pack_state == PACK_HIT &&
                    is_shade_pack_writer(g_current_key->writer)) {
                    /* The cached LUT belongs to the old 1x output; Scale2x for good (the tables never change). */
                    shade_free_copies(g_current_key);
                    g_current_key->pack_state = PACK_SHADE_REJECT;
                    g_shade_last_reason = SHADE_REJECT_REFRESH;
                    ++g_pack_shade_rejects[SHADE_REJECT_REFRESH];
                    write_key_log_line(g_current_key, "shade_reject", 0u);
                }
                ++g_identity_cache_refreshes;
                g_identity_cache_refresh_bytes += visible.width * visible.height * 2u;
                g1_perf_sections_end(G1_PERF_BIND_COMPARE, compare_started,
                                     (ULONGLONG)visible.width * visible.height);
                return FALSE;
            }
        }
    }
    g_identity_cache_hit_bytes += visible.width * visible.height;
    g1_perf_sections_end(G1_PERF_BIND_COMPARE, compare_started,
                         (ULONGLONG)visible.width * visible.height);
    return TRUE;
}

BOOL g1_hd_asset_bind_identity_frame(const BYTE *frame, DWORD frame_stride,
                                     const BYTE *written, DWORD written_stride,
                                     DWORD width, DWORD height)
{
    ULONGLONG alloc_started;
    DWORD y, bytes;
    BYTE *copy, *mask_copy;
    if (g_current_valid == 0 || !g_current_key || !frame || !written ||
        g_current_key->identity_frame || frame_stride < width ||
        written_stride < width ||
        width == 0u || height == 0u || width > 800u || height > 600u)
        return FALSE;
    bytes = width * height;
    if (bytes == 0u || bytes > G1_HD_CACHE_BYTE_LIMIT / 2u ||
        !make_room_for(bytes * 2u, g_current_key)) {
        ++g_invalid_sources;
        g_current_valid = 0;
        g_current_key = NULL;
        return FALSE;
    }
    alloc_started = g1_perf_sections_start();
    copy = (BYTE *)HeapAlloc(GetProcessHeap(), 0, bytes);
    mask_copy = (BYTE *)HeapAlloc(GetProcessHeap(), 0, bytes);
    if (copy) {
        for (y = 0u; y < height; ++y) {
            DWORD x;
            const BYTE *source_row = frame + y * frame_stride;
            const BYTE *written_row = written + y * written_stride;
            BYTE *cached_row = copy + y * width;
            BYTE *cached_mask_row = mask_copy ? mask_copy + y * width : NULL;
            for (x = 0u; x < width; ++x) {
                cached_row[x] = source_row[x];
                if (cached_mask_row) cached_mask_row[x] = written_row[x] != 0u;
            }
        }
    }
    g1_perf_sections_end(G1_PERF_BIND_COPY_ALLOC, alloc_started, bytes * 2u);
    if (!copy || !mask_copy) {
        if (copy) HeapFree(GetProcessHeap(), 0, copy);
        if (mask_copy) HeapFree(GetProcessHeap(), 0, mask_copy);
        ++g_invalid_sources;
        g_current_valid = 0;
        g_current_key = NULL;
        return FALSE;
    }
    g_current_key->identity_frame = copy;
    g_current_key->identity_written = mask_copy;
    g_current_key->identity_stride = width;
    g_current_key->identity_width = width;
    g_current_key->identity_height = height;
    g_current_key->identity_bytes = bytes;
    g_current_key->identity_mask_bytes = bytes;
    g_identity_cache_bytes += bytes * 2u;
    ++g_identity_cache_inserts;
    g_identity_cache_insert_bytes += bytes * 2u;
    if (!build_hd_frame(g_current_key)) {
        HeapFree(GetProcessHeap(), 0, g_current_key->identity_frame);
        g_current_key->identity_frame = NULL;
        HeapFree(GetProcessHeap(), 0, g_current_key->identity_written);
        g_current_key->identity_written = NULL;
        g_identity_cache_bytes -= bytes * 2u;
        g_current_key->identity_bytes = 0u;
        g_current_key->identity_mask_bytes = 0u;
        ++g_invalid_sources;
        g_current_valid = 0;
        g_current_key = NULL;
        return FALSE;
    }
    return TRUE;
}

static BOOL lookup_identity_block_at_for_key(const G1HdKey *key, DWORD x, DWORD y,
                                             BYTE *top_left, BYTE *top_right,
                                             BYTE *bottom_left, BYTE *bottom_right,
                                             BOOL count_normal_miss)
{
    DWORD local_x, local_y;
    BYTE pixel;
    if (!key || !key->identity_frame || !key->identity_written || !top_left || !top_right ||
        !bottom_left || !bottom_right) {
        if (count_normal_miss) ++g_identity_lookup_misses;
        return FALSE;
    }
    if ((LONG)x < g_current_origin_x || (LONG)y < g_current_origin_y ||
        (LONG)x - g_current_origin_x >= (LONG)key->identity_width ||
        (LONG)y - g_current_origin_y >= (LONG)key->identity_height) {
        if (count_normal_miss) ++g_identity_lookup_misses;
        return FALSE;
    }
    local_x = (DWORD)((LONG)x - g_current_origin_x);
    local_y = (DWORD)((LONG)y - g_current_origin_y);
    if (g_hd_source_mode == 2u) {
        if (!key->hd_frame) {
            if (count_normal_miss) ++g_identity_lookup_misses;
            return FALSE;
        }
        *top_left = key->hd_frame[(local_y * 2u) * key->hd_stride + local_x * 2u];
        *top_right = key->hd_frame[(local_y * 2u) * key->hd_stride + local_x * 2u + 1u];
        *bottom_left = key->hd_frame[(local_y * 2u + 1u) * key->hd_stride + local_x * 2u];
        *bottom_right = key->hd_frame[(local_y * 2u + 1u) * key->hd_stride + local_x * 2u + 1u];
        if (key->pack_applied) ++g_pack_lookup_blocks;
    } else {
        pixel = key->identity_frame[local_y * key->identity_stride + local_x];
        *top_left = pixel;
        *top_right = pixel;
        *bottom_left = pixel;
        *bottom_right = pixel;
    }
    ++g_identity_lookup_hits;
    return TRUE;
}

static BOOL lookup_identity_block_for_key(const G1HdKey *key, DWORD logical_pixel,
                                          BYTE *top_left, BYTE *top_right,
                                          BYTE *bottom_left, BYTE *bottom_right,
                                          BOOL count_normal_miss)
{
    if (logical_pixel >= 800u * 600u) {
        if (count_normal_miss) ++g_identity_lookup_misses;
        return FALSE;
    }
    return lookup_identity_block_at_for_key(key, logical_pixel % 800u,
                                            logical_pixel / 800u, top_left,
                                            top_right, bottom_left, bottom_right,
                                            count_normal_miss);
}

BOOL g1_hd_asset_lookup_identity_block(DWORD logical_pixel,
                                       BYTE *top_left, BYTE *top_right,
                                       BYTE *bottom_left, BYTE *bottom_right)
{
    if (g_current_valid == 0 || !g_current_key) {
        ++g_identity_lookup_misses;
        return FALSE;
    }
    return lookup_identity_block_for_key(g_current_key, logical_pixel,
                                         top_left, top_right, bottom_left,
                                         bottom_right, TRUE);
}

BOOL g1_hd_asset_lookup_identity_block_at(DWORD x, DWORD y,
                                          BYTE *top_left, BYTE *top_right,
                                          BYTE *bottom_left, BYTE *bottom_right)
{
    if (g_current_valid == 0 || !g_current_key) {
        ++g_identity_lookup_misses;
        return FALSE;
    }
    return lookup_identity_block_at_for_key(g_current_key, x, y, top_left,
                                            top_right, bottom_left, bottom_right,
                                            TRUE);
}

BOOL g1_hd_asset_probe_negative_key_mismatch(void)
{
    G1HdKey altered;
    G1HdKey *negative_key;
    BYTE top_left, top_right, bottom_left, bottom_right;
    if (!g1_hd_asset_enabled() || !g_current_key) return FALSE;
    altered = *g_current_key;
    altered.writer ^= 1u;
    ++g_identity_negative_lookup_attempts;
    negative_key = find_key_for_request(altered.source, altered.writer,
                                        altered.auxiliary,
                                        altered.auxiliary_digest,
                                        altered.width, altered.height,
                                        altered.digest, altered.pal);
    if (negative_key) {
        if (lookup_identity_block_for_key(negative_key, 0u, &top_left, &top_right,
                                          &bottom_left, &bottom_right, FALSE))
            return FALSE;
        return FALSE;
    }
    ++g_identity_negative_lookup_misses;
    ++g_identity_key_mismatches;
    return FALSE;
}

void g1_hd_asset_mark(DWORD logical_pixel)
{
    if (g_current_valid == 0 || logical_pixel >= G1_HD_PIXEL_LIMIT) return;
    if (g_identity_mask[logical_pixel] == 0u) {
        g_identity_mask[logical_pixel] = 1u;
        ++g_identity_pixels;
    }
}

void g1_hd_asset_end(void)
{
    g_current_valid = 0;
    g_current_key = NULL;
}

DWORD g1_hd_asset_identity_pixels(void) { return g_identity_pixels; }
DWORD g1_hd_asset_identity_keys(void) { return g_key_count; }
DWORD g1_hd_asset_identity_invalid_sources(void) { return g_invalid_sources; }
DWORD g1_hd_asset_identity_cache_bytes(void) { return g_identity_cache_bytes; }
DWORD g1_hd_asset_identity_evictions(void) { return g_identity_evictions; }
DWORD g1_hd_asset_identity_events(void) { return g_identity_events; }
DWORD g1_hd_asset_identity_lookup_hits(void) { return g_identity_lookup_hits; }
DWORD g1_hd_asset_identity_lookup_misses(void) { return g_identity_lookup_misses; }
DWORD g1_hd_asset_identity_cache_inserts(void) { return g_identity_cache_inserts; }
DWORD g1_hd_asset_identity_cache_hits(void) { return g_identity_cache_hits; }
DWORD g1_hd_asset_identity_cache_misses(void) { return g_identity_cache_misses; }
DWORD g1_hd_asset_identity_cache_refreshes(void) { return g_identity_cache_refreshes; }
DWORD g1_hd_asset_identity_negative_lookup_attempts(void) { return g_identity_negative_lookup_attempts; }
DWORD g1_hd_asset_identity_negative_lookup_misses(void) { return g_identity_negative_lookup_misses; }
DWORD g1_hd_asset_identity_key_mismatches(void) { return g_identity_key_mismatches; }
BOOL g1_hd_asset_pack_enabled(void)
{
    initialize_environment();
    return g_hd_pack_dir[0] != '\0';
}
/* The flip writers 0x466B50 / 0x466BE0 take the identity key path only when a Scale2x pack run is on and the
 * switch SYW2_G1_HD_PACK_FLIP is not 0; otherwise the caller keeps the plain diff mirror. */
BOOL g1_hd_asset_flip_key_path(void)
{
    initialize_environment();
    return g_hd_pack_dir[0] != '\0' && g_hd_source_mode == 2u && !g_hd_flip_off;
}
/* H-HDB0/H-HDB1/H-HDB2: the translucent writers 0x4672E0 (logo), 0x467580 (weighted) and 0x467B00 (weighted, clipped) take the identity key path only with a Scale2x pack run and the
 * switch SYW2_G1_HD_PACK_BLEND not 0; the pack frame it hits is blended with the HD destination by the caller. */
BOOL g1_hd_asset_blend_key_path(void)
{
    initialize_environment();
    return g_hd_pack_dir[0] != '\0' && g_hd_source_mode == 2u && !g_hd_blend_off;
}
/* H-HDB3: the left/right flipped translucent writers 0x467FD0 and 0x4685C0 additionally need SYW2_G1_HD_PACK_FLIP not 0. */
BOOL g1_hd_asset_blend_flip_key_path(void)
{
    initialize_environment();
    return g1_hd_asset_blend_key_path() && !g_hd_flip_off;
}
/* The current key's pack frame (2w x 2h index bytes, key 0xFE = transparent) when the pack file hit, else NULL. */
const BYTE *g1_hd_asset_current_pack_frame(DWORD *hd_width, DWORD *hd_height)
{
    const G1HdKey *key = g_current_key;
    if (g_current_valid == 0 || !key || !key->pack_applied || !key->hd_frame) return NULL;
    if (hd_width) *hd_width = key->hd_width;
    if (hd_height) *hd_height = key->hd_height;
    return key->hd_frame;
}
DWORD g1_hd_asset_pack_ext_hits(void) { return g_pack_ext_hits; }
DWORD g1_hd_asset_pack_ext_misses(void) { return g_pack_ext_misses; }
DWORD g1_hd_asset_pack_ext_rejects(void) { return g_pack_ext_rejects; }
DWORD g1_hd_asset_pack_blend_hits(void) { return g_pack_blend_hits; }
DWORD g1_hd_asset_pack_blend_misses(void) { return g_pack_blend_misses; }
DWORD g1_hd_asset_pack_blend_rejects(void) { return g_pack_blend_rejects; }
DWORD g1_hd_asset_pack_flip_hits(void) { return g_pack_flip_hits; }
DWORD g1_hd_asset_pack_flip_misses(void) { return g_pack_flip_misses; }
DWORD g1_hd_asset_pack_flip_rejects(void) { return g_pack_flip_rejects; }
/* Whole-screen raw picture (H-HDF0): <pack>\f<fnv1a of all w*h source bytes>_<w>x<h>.idx8, 2w x 2h bytes.  The
 * caller (the 0x466280 menu block copy) already hashes the packed 1x block, so the lookup key is that hash; the
 * picture is opaque, so the only check is the exact size and that the transparent key never occurs.  The last
 * hit stays cached (the title block copy runs every present); names that missed or were rejected are remembered
 * so a screen without a pack file does not touch the disk again. */
const BYTE *g1_hd_asset_fullscreen_frame(DWORD hash, DWORD width, DWORD height)
{
    char name[40], path[MAX_PATH];
    DWORD file_high = 0u, file_bytes, bytes_read = 0u, bytes, index, pal;
    HANDLE file;
    BYTE *frame;
    initialize_environment();
    if (!g_hd_pack_dir[0] || g_hd_fullscreen_off || g_hd_source_mode != 2u) return NULL;
    pal = g1_hd_asset_palette_digest();
    if (g_fullscreen_frame && g_fullscreen_hash == hash && g_fullscreen_width == width &&
        g_fullscreen_height == height && g_fullscreen_pal == pal) {
        ++g_fullscreen_hits;
        return g_fullscreen_frame;
    }
    for (index = 0u; index < g_fullscreen_missed_count; ++index)
        if (g_fullscreen_missed_hash[index] == hash && g_fullscreen_missed_pal[index] == pal) {
            if (g_fullscreen_missed_rejected[index]) ++g_fullscreen_rejects;
            else ++g_fullscreen_misses;
            return NULL;
        }
    if (!g1_hd_pack_fullscreen_name(name, sizeof(name), hash, width, height) ||
        !pack_file_path(path, sizeof(path), pal, name)) return NULL;
    bytes = width * 2u * height * 2u;
    file = CreateFileA(path, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING,
                       FILE_ATTRIBUTE_NORMAL, NULL);
    frame = NULL;
    if (file != INVALID_HANDLE_VALUE) {
        file_bytes = GetFileSize(file, &file_high);
        if (file_high == 0u && file_bytes == bytes &&
            (frame = (BYTE *)HeapAlloc(GetProcessHeap(), 0, bytes)) != NULL &&
            !(ReadFile(file, frame, bytes, &bytes_read, NULL) && bytes_read == bytes)) {
            HeapFree(GetProcessHeap(), 0, frame);
            frame = NULL;
        }
        CloseHandle(file);
        for (index = 0u; frame && index < bytes; ++index)
            if (frame[index] == G1_HD_PACK_KEY) {
                HeapFree(GetProcessHeap(), 0, frame);
                frame = NULL;
            }
    }
    if (!frame) {
        BOOL rejected = file != INVALID_HANDLE_VALUE;
        if (rejected) ++g_fullscreen_rejects;
        else {
            ++g_fullscreen_misses;
            note_missing_file(path);
        }
        if (g_fullscreen_missed_count < G1_HD_FULLSCREEN_MISS_SLOTS) {
            g_fullscreen_missed_hash[g_fullscreen_missed_count] = hash;
            g_fullscreen_missed_pal[g_fullscreen_missed_count] = pal;
            g_fullscreen_missed_rejected[g_fullscreen_missed_count++] = rejected ? 1u : 0u;
        }
        return NULL;
    }
    if (g_fullscreen_frame) HeapFree(GetProcessHeap(), 0, g_fullscreen_frame);
    g_fullscreen_frame = frame;
    g_fullscreen_hash = hash;
    g_fullscreen_pal = pal;
    g_fullscreen_width = width;
    g_fullscreen_height = height;
    ++g_fullscreen_loads;
    ++g_fullscreen_hits;
    return frame;
}
DWORD g1_hd_asset_fullscreen_hits(void) { return g_fullscreen_hits; }
DWORD g1_hd_asset_fullscreen_misses(void) { return g_fullscreen_misses; }
DWORD g1_hd_asset_fullscreen_rejects(void) { return g_fullscreen_rejects; }
DWORD g1_hd_asset_fullscreen_loads(void) { return g_fullscreen_loads; }
DWORD g1_hd_asset_pack_hits(void) { return g_pack_hits; }
DWORD g1_hd_asset_pack_misses(void) { return g_pack_misses; }
DWORD g1_hd_asset_pack_rejects(void) { return g_pack_rejects; }
DWORD g1_hd_asset_pack_skipped_aux(void) { return g_pack_skipped_aux; }
DWORD g1_hd_asset_pack_lookup_blocks(void) { return g_pack_lookup_blocks; }
DWORD g1_hd_asset_pack_lut_hits(void) { return g_pack_lut_hits; }
DWORD g1_hd_asset_pack_lut_rejects(void) { return g_pack_lut_rejects; }
DWORD g1_hd_asset_pack_lut_key_color(void) { return g_pack_lut_key_color; }
DWORD g1_hd_asset_pack_lut_nonidentity(void) { return g_pack_lut_nonidentity; }
DWORD g1_hd_asset_pack_shade_hits(void) { return g_pack_shade_hits; }
DWORD g1_hd_asset_pack_shade_rejects(void)
{
    DWORD index, total = 0u;
    for (index = 0u; index < SHADE_REJECT_REASONS; ++index) total += g_pack_shade_rejects[index];
    return total;
}
DWORD g1_hd_asset_pack_shade_rejects_by_reason(DWORD reason)
{
    return reason < SHADE_REJECT_REASONS ? g_pack_shade_rejects[reason] : 0u;
}
DWORD g1_hd_asset_pack_shade_selfcheck_pixels(void) { return g_pack_shade_selfcheck_pixels; }
DWORD g1_hd_asset_pack_shade_multi_keys(void) { return g_pack_shade_multi_keys; }
DWORD g1_hd_asset_pack_shade_key_color(void) { return g_pack_shade_key_color; }
DWORD g1_hd_asset_pack_shade_lut_bytes(void) { return g_pack_shade_lut_bytes; }
DWORD g1_hd_asset_scale2x_blocks(void) { return g_scale2x_blocks; }
DWORD g1_hd_asset_scale2x_subpixel_differences(void) { return g_scale2x_subpixel_differences; }
DWORD g1_hd_asset_scale2x_palette_violations(void) { return g_scale2x_palette_violations; }
DWORD g1_hd_asset_full_frame_calls(void) { return g_full_frame_calls; }
DWORD g1_hd_asset_bbox_calls(void) { return g_bbox_calls; }
DWORD g1_hd_asset_clipped_calls(void) { return g_clipped_calls; }
DWORD g1_hd_asset_cache_hit_bytes(void) { return g_identity_cache_hit_bytes; }
DWORD g1_hd_asset_cache_insert_bytes(void) { return g_identity_cache_insert_bytes; }
DWORD g1_hd_asset_cache_refresh_bytes(void) { return g_identity_cache_refresh_bytes; }
DWORD g1_hd_asset_clip_replay_mismatches(void) { return g_clip_replay_mismatches; }
void g1_hd_asset_last_clip_mismatch(DWORD *x, DWORD *y,
                                   BYTE *screen_value, BYTE *replay_value)
{
    if (x) *x = g_last_clip_mismatch_x;
    if (y) *y = g_last_clip_mismatch_y;
    if (screen_value) *screen_value = g_last_clip_screen_value;
    if (replay_value) *replay_value = g_last_clip_replay_value;
}
