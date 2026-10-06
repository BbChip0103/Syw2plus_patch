/* Bounded P2/P3 key-bound asset ledger.
 *
 * The source pointer is the exact frame pointer passed to the protected
 * original primitive. A key includes the writer and dimensions plus a
 * bounded digest of source bytes. The identity frame is the value produced
 * by the original primitive itself; this ledger only proves its provenance
 * and coverage so P3 can replace the source without changing the mask.
 */

#include "g1_hd_asset.h"
#include "g1_perf_sections.h"
#include "g1_scale2x_core.h"
#include "g1_scratch_bounds.h"

#define G1_HD_SOURCE_ENV "SYW2_G1_HD_SOURCE"
#define G1_HD_SOURCE_IDENTITY "identity"
#define G1_HD_SOURCE_SCALE2X "scale2x"
#define G1_HD_KEY_LIMIT 4096u
#define G1_HD_PIXEL_LIMIT (800u * 600u)
#define G1_HD_DIGEST_BYTES 128u
#define G1_HD_CACHE_BYTE_LIMIT (128u * 1024u * 1024u)

typedef struct {
    DWORD source;
    DWORD writer;
    DWORD auxiliary;
    DWORD auxiliary_digest;
    DWORD width;
    DWORD height;
    DWORD digest;
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
} G1HdKey;

static G1HdKey g_keys[G1_HD_KEY_LIMIT];
static DWORD g_key_count = 0u;
static BYTE g_identity_mask[G1_HD_PIXEL_LIMIT];
static DWORD g_identity_pixels = 0u;
static DWORD g_invalid_sources = 0u;
static DWORD g_identity_events = 0u;
static DWORD g_identity_lookup_hits = 0u;
static DWORD g_identity_lookup_misses = 0u;
static DWORD g_identity_cache_bytes = 0u;
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

static BOOL readable_source(const BYTE *source)
{
    MEMORY_BASIC_INFORMATION info;
    SIZE_T remaining = G1_HD_DIGEST_BYTES;
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

static G1HdKey *find_key_for_request(DWORD source, DWORD writer,
                                     DWORD auxiliary, DWORD auxiliary_digest,
                                     DWORD width, DWORD height, DWORD digest)
{
    DWORD index;
    for (index = 0u; index < g_key_count; ++index) {
        G1HdKey *key = &g_keys[index];
        if (key->source == source && key->writer == writer &&
            key->auxiliary == auxiliary &&
            key->auxiliary_digest == auxiliary_digest &&
            key->width == width && key->height == height &&
            key->digest == digest)
            return key;
    }
    return NULL;
}

void g1_hd_asset_reset(void)
{
    DWORD index;
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
    }
    g_key_count = 0u;
    g_identity_pixels = 0u;
    g_invalid_sources = 0u;
    g_identity_events = 0u;
    g_identity_lookup_hits = 0u;
    g_identity_lookup_misses = 0u;
    g_identity_cache_bytes = 0u;
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
    DWORD digest;
    G1HdKey *key;
    BOOL clipped;
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
    key = find_key_for_request((DWORD)(ULONG_PTR)source, writer,
                               (DWORD)(ULONG_PTR)auxiliary, auxiliary_digest,
                               width, height, digest);
    if (key) {
        ++g_bbox_calls;
        if (clipped) ++g_clipped_calls;
        g1_perf_sections_end(G1_PERF_HASH_LOOKUP, started, G1_HD_DIGEST_BYTES);
        ++g_identity_events;
        if (key->identity_frame) ++g_identity_cache_hits;
        else ++g_identity_cache_misses;
        g_current_key = key;
        g_current_origin_x = origin_x;
        g_current_origin_y = origin_y;
        g_current_valid = 1;
        return TRUE;
    }
    if (g_key_count >= G1_HD_KEY_LIMIT) {
        ++g_invalid_sources;
        g_current_valid = 0;
        g_current_key = NULL;
        return FALSE;
    }
    g_keys[g_key_count].source = (DWORD)(ULONG_PTR)source;
    g_keys[g_key_count].writer = writer;
    g_keys[g_key_count].auxiliary = (DWORD)(ULONG_PTR)auxiliary;
    g_keys[g_key_count].auxiliary_digest = auxiliary_digest;
    g_keys[g_key_count].width = width;
    g_keys[g_key_count].height = height;
    g_keys[g_key_count].digest = digest;
    g_keys[g_key_count].identity_frame = NULL;
    g_keys[g_key_count].identity_written = NULL;
    g_keys[g_key_count].identity_stride = 0u;
    g_keys[g_key_count].identity_width = 0u;
    g_keys[g_key_count].identity_height = 0u;
    g_keys[g_key_count].identity_bytes = 0u;
    g_keys[g_key_count].identity_mask_bytes = 0u;
    g_keys[g_key_count].hd_frame = NULL;
    g_keys[g_key_count].hd_stride = 0u;
    g_keys[g_key_count].hd_width = 0u;
    g_keys[g_key_count].hd_height = 0u;
    g_keys[g_key_count].hd_bytes = 0u;
    g_current_key = &g_keys[g_key_count];
    g_current_origin_x = origin_x;
    g_current_origin_y = origin_y;
    ++g_key_count;
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
        g_identity_cache_bytes > G1_HD_CACHE_BYTE_LIMIT - hd_bytes) return FALSE;
    hd = (BYTE *)HeapAlloc(GetProcessHeap(), 0, hd_bytes);
    if (!hd) return FALSE;
    if (!build_scale2x(key->identity_frame, key->identity_stride,
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
        g_identity_cache_bytes > G1_HD_CACHE_BYTE_LIMIT - bytes * 2u) {
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
                                        altered.digest);
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
