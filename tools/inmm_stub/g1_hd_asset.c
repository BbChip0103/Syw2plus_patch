/* Bounded P2/P3 key-bound asset ledger.
 *
 * The source pointer is the exact frame pointer passed to the protected
 * original primitive. A key includes the writer and dimensions plus a
 * bounded digest of source bytes. The identity frame is the value produced
 * by the original primitive itself; this ledger only proves its provenance
 * and coverage so P3 can replace the source without changing the mask.
 */

#include <string.h>
#ifdef _WIN32
#include <stdlib.h>
#endif

#include "g1_hd_asset.h"
#include "g1_hd_pack.h"
#include "g1_perf_sections.h"
#include "g1_scale2x_core.h"
#include "g1_scratch_bounds.h"
#include "g1_sha256.h"

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
#ifdef _WIN32
#define G1_HD_SIDECAR_LIMIT 524288u
#define G1_HD_SIDECAR_DIR_LIMIT 4096u
#define G1_HD_SIDECAR_HASH_SIZE 1048576u
#define G1_HD_SOURCE_GUARD_LIMIT 4096u
typedef struct { char name[64]; char pal8[9]; DWORD frame; DWORD directory; DWORD length; DWORD p8; DWORD width; DWORD height; BYTE native; BYTE ambiguous; } G1HdSidecarEntry;
typedef struct { char path[MAX_PATH]; BYTE sha256[32]; } G1HdSourceGuardEntry;
static G1HdSidecarEntry *g_sidecar_entries;
static DWORD g_sidecar_count;
static DWORD *g_sidecar_hash;
static char (*g_sidecar_dirs)[MAX_PATH];
static DWORD g_sidecar_dir_count;
static char (*g_hd_single_files)[MAX_PATH];
static DWORD g_hd_single_file_count;
static DWORD g_sidecar_duplicates;
static BOOL g_sidecar_enabled;
static char g_sidecar_root[MAX_PATH];
static G1HdSourceGuardEntry *g_source_guard_entries;
static DWORD g_source_guard_count;
static BOOL g_source_guard_active;
static BOOL g_source_guard_invalid;
static DWORD g_source_guard_rejects;
#endif
static void initialize_environment(void);
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
static BOOL readable_range(const BYTE *source, SIZE_T bytes);

#ifdef _WIN32
static DWORD sidecar_hash_key(const char *name, const char *pal8)
{
    DWORD hash = 2166136261u;
    const unsigned char *p;
    for (p = (const unsigned char *)name; *p; ++p) { hash ^= *p; hash *= 16777619u; }
    for (p = (const unsigned char *)pal8; *p; ++p) { hash ^= *p; hash *= 16777619u; }
    return hash & (G1_HD_SIDECAR_HASH_SIZE - 1u);
}

static char *sidecar_find_text(char *text, const char *wanted)
{
    DWORD length = (DWORD)lstrlenA(wanted);
    char *p;
    DWORD i;
    for (p = text; *p; ++p) {
        for (i = 0u; i < length && p[i] && p[i] == wanted[i]; ++i) { }
        if (i == length) return p;
    }
    return NULL;
}

static BOOL sidecar_prefix(const char *text, const char *wanted, DWORD length)
{
    DWORD i;
    for (i = 0u; i < length; ++i) if (text[i] != wanted[i]) return FALSE;
    return TRUE;
}

static DWORD sidecar_hex(const char *text)
{
    DWORD value = 0u;
    while (*text) {
        BYTE c = (BYTE)*text++;
        DWORD digit;
        if (c >= '0' && c <= '9') digit = c - '0';
        else if (c >= 'a' && c <= 'f') digit = c - 'a' + 10u;
        else if (c >= 'A' && c <= 'F') digit = c - 'A' + 10u;
        else break;
        value = (value << 4) | digit;
    }
    return value;
}

static DWORD parse_json_uint(const char **cursor, DWORD *value)
{
    DWORD n = 0u;
    const char *p = *cursor;
    if (*p < '0' || *p > '9') return 0u;
    while (*p >= '0' && *p <= '9') { n = n * 10u + (DWORD)(*p - '0'); ++p; }
    *cursor = p; *value = n; return 1u;
}

static DWORD parse_json_string(const char **cursor, char *out, DWORD capacity)
{
    DWORD n = 0u;
    const char *p = *cursor;
    if (*p++ != '"') return 0u;
    while (*p && *p != '"') {
        if (*p == '\\' || n + 1u >= capacity) return 0u;
        out[n++] = *p++;
    }
    if (*p != '"') return 0u;
    out[n] = '\0'; *cursor = p + 1; return 1u;
}

static DWORD sidecar_find(const char *name, const char *pal8)
{
    DWORD slot = sidecar_hash_key(name, pal8), probes;
    for (probes = 0u; probes < G1_HD_SIDECAR_HASH_SIZE; ++probes) {
        DWORD ref = g_sidecar_hash ? g_sidecar_hash[slot] : 0u;
        if (!ref) return 0u;
        if (!lstrcmpA(g_sidecar_entries[ref - 1u].name, name) &&
            !lstrcmpA(g_sidecar_entries[ref - 1u].pal8, pal8)) return ref;
        slot = (slot + 1u) & (G1_HD_SIDECAR_HASH_SIZE - 1u);
    }
    return 0u;
}

static DWORD read_le32(const BYTE *p)
{
    return (DWORD)p[0] | ((DWORD)p[1] << 8) | ((DWORD)p[2] << 16) | ((DWORD)p[3] << 24);
}

static void native_copy(BYTE *destination, const BYTE *source, DWORD bytes)
{
    DWORD index;
    for (index = 0u; index < bytes; ++index) destination[index] = source[index];
}

static BOOL native_equal(const BYTE *left, const BYTE *right, DWORD bytes)
{
    DWORD index;
    for (index = 0u; index < bytes; ++index) if (left[index] != right[index]) return FALSE;
    return TRUE;
}

static char *native_last_dot(char *text)
{
    char *last = NULL;
    while (*text) { if (*text == '.') last = text; ++text; }
    return last;
}

static DWORD native_hash_bytes(const BYTE *bytes, DWORD count)
{
    DWORD value = 2166136261u, index;
    for (index = 0u; index < count; ++index) { value ^= bytes[index]; value *= 16777619u; }
    return value;
}

static void native_add_kind(const char *name, DWORD file_id, DWORD frame, DWORD width, DWORD height, BYTE kind)
{
    DWORD found = sidecar_find(name, ""), slot;
    G1HdSidecarEntry *entry;
    if (found) { g_sidecar_entries[found - 1u].ambiguous = 1u; ++g_sidecar_duplicates; return; }
    if (g_sidecar_count >= G1_HD_SIDECAR_LIMIT || file_id >= g_hd_single_file_count) return;
    entry = &g_sidecar_entries[g_sidecar_count];
    lstrcpyA(entry->name, name); entry->pal8[0] = '\0';
    entry->frame = frame; entry->directory = file_id;
    entry->length = 0xFFFFFFFFu; entry->p8 = 0u;
    entry->width = width; entry->height = height; entry->native = kind; entry->ambiguous = 0u;
    slot = sidecar_hash_key(name, "");
    while (g_sidecar_hash[slot]) slot = (slot + 1u) & (G1_HD_SIDECAR_HASH_SIZE - 1u);
    g_sidecar_hash[slot] = ++g_sidecar_count;
}

static void native_add(const char *name, DWORD file_id, DWORD frame, DWORD width, DWORD height)
{
    native_add_kind(name, file_id, frame, width, height, 1u);
}

static BOOL native_bmp_read(const char *path, BYTE *pixels, DWORD capacity, DWORD *width_out,
                            DWORD *height_out, BYTE palette_out[1024])
{
    BYTE header[54], palette[1024];
    HANDLE file;
    DWORD high = 0u, size, got = 0u, offset, dib, width, height, row, stride, colors;
    LONG signed_width, signed_height;
    WORD planes, bpp;
    DWORD compression;
    if (!path) return FALSE;
    file = CreateFileA(path, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (file == INVALID_HANDLE_VALUE) return FALSE;
    size = GetFileSize(file, &high);
    if (high || size == INVALID_FILE_SIZE || size < sizeof(header) ||
        !ReadFile(file, header, sizeof(header), &got, NULL) || got != sizeof(header) ||
        header[0] != 'B' || header[1] != 'M') { CloseHandle(file); return FALSE; }
    offset = read_le32(header + 10); dib = read_le32(header + 14);
    signed_width = (LONG)read_le32(header + 18); signed_height = (LONG)read_le32(header + 22);
    planes = (WORD)(header[26] | ((WORD)header[27] << 8));
    bpp = (WORD)(header[28] | ((WORD)header[29] << 8)); compression = read_le32(header + 30);
    colors = read_le32(header + 46); if (!colors) colors = 256u;
    if (dib < 40u || signed_width <= 0 || signed_height == 0 || signed_height == (-2147483647L - 1L) ||
        planes != 1u || bpp != 8u || compression != 0u || colors != 256u || offset < 14u + dib + 1024u) {
        CloseHandle(file); return FALSE;
    }
    width = (DWORD)signed_width; height = (DWORD)(signed_height < 0 ? -signed_height : signed_height);
    if (!width || !height || width > 32768u || height > 32768u || width > 0xFFFFFFFFu / height) {
        CloseHandle(file); return FALSE;
    }
    stride = (width + 3u) & ~3u;
    if (stride > 0xFFFFFFFFu / height || offset > size || size - offset < stride * height ||
        (pixels && capacity < width * height) ||
        SetFilePointer(file, 14u + dib, NULL, FILE_BEGIN) == INVALID_SET_FILE_POINTER ||
        !ReadFile(file, palette, sizeof(palette), &got, NULL) || got != sizeof(palette)) {
        CloseHandle(file); return FALSE;
    }
    if (palette_out) native_copy(palette_out, palette, sizeof(palette));
    if (pixels) {
        BYTE *line = (BYTE *)HeapAlloc(GetProcessHeap(), 0, stride);
        if (!line) { CloseHandle(file); return FALSE; }
        for (row = 0u; row < height; ++row) {
            DWORD source_row = signed_height < 0 ? row : height - 1u - row;
            if (SetFilePointer(file, offset + source_row * stride, NULL, FILE_BEGIN) == INVALID_SET_FILE_POINTER ||
                !ReadFile(file, line, stride, &got, NULL) || got != stride) {
                HeapFree(GetProcessHeap(), 0, line); CloseHandle(file); return FALSE;
            }
            native_copy(pixels + row * width, line, width);
        }
        HeapFree(GetProcessHeap(), 0, line);
    }
    if (width_out) *width_out = width;
    if (height_out) *height_out = height;
    CloseHandle(file);
    return TRUE;
}

static BOOL native_decode_rle(HANDLE file, DWORD file_size, DWORD offset, DWORD encoded_bytes,
                              BYTE *pixels, DWORD pixel_count)
{
    DWORD pos = 0u, emitted = 0u, got = 0u;
    BYTE value, run;
    if (!pixels || offset > file_size || encoded_bytes > file_size - offset ||
        SetFilePointer(file, offset, NULL, FILE_BEGIN) == INVALID_SET_FILE_POINTER) return FALSE;
    while (pos < encoded_bytes && emitted < pixel_count) {
        if (!ReadFile(file, &value, 1u, &got, NULL) || got != 1u) return FALSE;
        ++pos;
        if (value == 0xFEu) {
            if (pos >= encoded_bytes || !ReadFile(file, &run, 1u, &got, NULL) || got != 1u) return FALSE;
            ++pos;
            if (!run) pixels[emitted++] = 0xFEu;
            else if (run <= pixel_count - emitted) { memset(pixels + emitted, 0xFE, run); emitted += run; }
            else return FALSE;
        } else pixels[emitted++] = value;
    }
    return pos == encoded_bytes && emitted == pixel_count;
}

static void native_add_sheet_cells(HANDLE source_file, DWORD source_size, DWORD file_id,
                                   DWORD frame_width, DWORD frame_height, DWORD sheet_width,
                                   DWORD sheet_height, DWORD encoded_bytes)
{
    DWORD cells_x, cells_y, cell, x, y, row, cell_bytes;
    BYTE *sheet, *cell_pixels;
    if (!frame_width || !frame_height || frame_width > 0xFFFFFFFFu / frame_height ||
        sheet_width % frame_width || sheet_height % frame_height ||
        sheet_width <= frame_width || sheet_height < frame_height || sheet_width > 32768u || sheet_height > 32768u ||
        sheet_width > 0xFFFFFFFFu / sheet_height || sheet_width * sheet_height > 64u * 1024u * 1024u) return;
    sheet = (BYTE *)HeapAlloc(GetProcessHeap(), 0, sheet_width * sheet_height);
    cell_bytes = frame_width * frame_height;
    cell_pixels = (BYTE *)HeapAlloc(GetProcessHeap(), 0, cell_bytes);
    if (!sheet || !cell_pixels) { if (sheet) HeapFree(GetProcessHeap(), 0, sheet); if (cell_pixels) HeapFree(GetProcessHeap(), 0, cell_pixels); return; }
    if (!native_decode_rle(source_file, source_size, 0xBF4u, encoded_bytes, sheet, sheet_width * sheet_height)) goto done;
    cells_x = sheet_width / frame_width; cells_y = sheet_height / frame_height;
    for (cell = 0u; cell < cells_x * cells_y; ++cell) {
        DWORD digest;
        char name[64];
        x = (cell % cells_x) * frame_width; y = (cell / cells_x) * frame_height;
        for (row = 0u; row < frame_height; ++row)
            native_copy(cell_pixels + row * frame_width, sheet + (y + row) * sheet_width + x, frame_width);
        digest = native_hash_bytes(cell_pixels, cell_bytes);
        if (g1_hd_pack_name(name, sizeof(name), digest, frame_width, frame_height))
            native_add(name, file_id, cell, frame_width, frame_height);
    }
done:
    HeapFree(GetProcessHeap(), 0, cell_pixels); HeapFree(GetProcessHeap(), 0, sheet);
}

static DWORD native_ytl_width(HANDLE file, DWORD offset, DWORD rows)
{
    DWORD row, width = 0u, got, end;
    BYTE record[2];
    for (row = 0u; row < rows; ++row) {
        if (SetFilePointer(file, offset, NULL, FILE_BEGIN) == INVALID_SET_FILE_POINTER ||
            !ReadFile(file, record, 2u, &got, NULL) || got != 2u) return 0u;
        end = (DWORD)record[0] + (DWORD)record[1];
        if (end > width) width = end;
        offset += 2u + (DWORD)record[1];
    }
    return width;
}

static void native_add_source_frame(HANDLE source_file, DWORD source_size, DWORD file_id,
                                    DWORD frame, DWORD offset, DWORD range_bytes, DWORD width, DWORD height)
{
    BYTE prefix[G1_HD_PACK_EXT_MAX];
    DWORD available, want, digest, length, hash;
    DWORD got = 0u;
    char name[64], extended[64];
    if (offset > source_size || source_size - offset < G1_HD_DIGEST_BYTES || width == 0u || height == 0u ||
        SetFilePointer(source_file, offset, NULL, FILE_BEGIN) == INVALID_SET_FILE_POINTER) return;
    available = source_size - offset;
    if (range_bytes && available > range_bytes) available = range_bytes;
    want = available < sizeof(prefix) ? available : (DWORD)sizeof(prefix);
    if (!ReadFile(source_file, prefix, want, &got, NULL) || got != want) return;
    digest = native_hash_bytes(prefix, G1_HD_DIGEST_BYTES);
    if (g1_hd_pack_name(name, sizeof(name), digest, width, height)) native_add(name, file_id, frame, width, height);
    if (width == 831u) {
        wsprintfA(name, "w004663e0_h%08lx_831x%lu.idx8", (unsigned long)digest, (unsigned long)height);
        native_add(name, file_id, frame, width, height);
    }
    for (length = 256u; length <= G1_HD_PACK_EXT_MAX && length <= want; length *= 2u) {
        hash = native_hash_bytes(prefix, length);
        if (g1_hd_pack_ext_name(extended, sizeof(extended), digest, width, height, length, hash))
            native_add(extended, file_id, frame, width, height);
        if (length > G1_HD_PACK_EXT_MAX / 2u) break;
    }
}

static int source_guard_hex(char value)
{
    if (value >= '0' && value <= '9') return value - '0';
    if (value >= 'a' && value <= 'f') return value - 'a' + 10;
    if (value >= 'A' && value <= 'F') return value - 'A' + 10;
    return -1;
}

static BOOL source_guard_prefix_equal(const char *value, const char *prefix, DWORD length)
{
    DWORD i;
    for (i = 0u; i < length; ++i) {
        char a = value[i], b = prefix[i];
        if (a >= 'A' && a <= 'Z') a = (char)(a + ('a' - 'A'));
        if (b >= 'A' && b <= 'Z') b = (char)(b + ('a' - 'A'));
        if (a != b) return FALSE;
    }
    return TRUE;
}

static BOOL load_source_guard(const char *root)
{
    char path[MAX_PATH];
    HANDLE file;
    DWORD high = 0u, size, got = 0u, start = 0u, i;
    char *data;
    g_source_guard_active = TRUE;
    if (lstrlenA(root) + 24u >= MAX_PATH) { g_source_guard_invalid = TRUE; return FALSE; }
    wsprintfA(path, "%s\\g1_hd_sources.sha256", root);
    /* Native HD siblings fail closed unless the sidecar records their source identities. */
    file = CreateFileA(path, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (file == INVALID_HANDLE_VALUE) { g_source_guard_invalid = TRUE; return FALSE; }
    size = GetFileSize(file, &high);
    if (high || size == INVALID_FILE_SIZE || size > 4u * 1024u * 1024u) {
        g_source_guard_invalid = TRUE; CloseHandle(file); return TRUE;
    }
    data = (char *)HeapAlloc(GetProcessHeap(), 0, size + 1u);
    g_source_guard_entries = (G1HdSourceGuardEntry *)HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY,
        sizeof(G1HdSourceGuardEntry) * G1_HD_SOURCE_GUARD_LIMIT);
    if (!data || !g_source_guard_entries || !ReadFile(file, data, size, &got, NULL) || got != size) {
        if (data) HeapFree(GetProcessHeap(), 0, data);
        g_source_guard_invalid = TRUE; CloseHandle(file); return TRUE;
    }
    CloseHandle(file); data[size] = '\0';
    for (i = 0u; i <= size; ++i) {
        if (data[i] == '\n' || data[i] == '\0') {
            char *line = data + start, *relative;
            DWORD line_length = i - start, path_length, j;
            G1HdSourceGuardEntry *entry;
            start = i + 1u;
            if (line_length && line[line_length - 1u] == '\r') --line_length;
            if (!line_length) continue;
            if (line_length < 67u || line[64] != ' ' || line[65] != ' ') { g_source_guard_invalid = TRUE; break; }
            path_length = line_length - 66u;
            if (!path_length || path_length >= MAX_PATH || g_source_guard_count >= G1_HD_SOURCE_GUARD_LIMIT) {
                g_source_guard_invalid = TRUE; break;
            }
            line[64] = '\0'; relative = line + 66;
            entry = &g_source_guard_entries[g_source_guard_count];
            for (j = 0u; j < 32u; ++j) {
                int high_nibble = source_guard_hex(line[j * 2u]), low_nibble = source_guard_hex(line[j * 2u + 1u]);
                if (high_nibble < 0 || low_nibble < 0) { g_source_guard_invalid = TRUE; break; }
                entry->sha256[j] = (BYTE)((high_nibble << 4) | low_nibble);
            }
            if (g_source_guard_invalid) break;
            for (j = 0u; j < path_length; ++j) {
                if (relative[j] == '\\') relative[j] = '/';
                if ((BYTE)relative[j] < 0x20u) { g_source_guard_invalid = TRUE; break; }
                entry->path[j] = relative[j];
            }
            entry->path[path_length] = '\0';
            if (g_source_guard_invalid) break;
            for (j = 0u; j < g_source_guard_count; ++j) {
                if (!lstrcmpiA(entry->path, g_source_guard_entries[j].path)) { g_source_guard_invalid = TRUE; break; }
            }
            if (g_source_guard_invalid) break;
            ++g_source_guard_count;
        }
    }
    if (!g_source_guard_count) g_source_guard_invalid = TRUE;
    HeapFree(GetProcessHeap(), 0, data);
    return TRUE;
}

static BOOL source_guard_matches(const char *hd_path, HANDLE source_file)
{
    char relative[MAX_PATH];
    DWORD root_length = lstrlenA(g_sidecar_root), path_length = lstrlenA(hd_path), i, got;
    G1Sha256 sha;
    BYTE digest[32], buffer[16384];
    G1HdSourceGuardEntry *expected = NULL;
    if (!g_source_guard_active) return TRUE;
    if (g_source_guard_invalid || path_length <= root_length || !source_guard_prefix_equal(hd_path, g_sidecar_root, root_length) ||
        (hd_path[root_length] != '\\' && hd_path[root_length] != '/')) goto reject;
    if (path_length - root_length - 1u >= sizeof(relative)) goto reject;
    lstrcpyA(relative, hd_path + root_length + 1u);
    for (i = 0u; relative[i]; ++i) if (relative[i] == '\\') relative[i] = '/';
    for (i = 0u; i < g_source_guard_count; ++i) {
        if (!lstrcmpiA(relative, g_source_guard_entries[i].path)) { expected = &g_source_guard_entries[i]; break; }
    }
    if (!expected || SetFilePointer(source_file, 0, NULL, FILE_BEGIN) == INVALID_SET_FILE_POINTER) goto reject;
    g1_sha256_init(&sha);
    for (;;) {
        if (!ReadFile(source_file, buffer, sizeof(buffer), &got, NULL)) goto reject;
        if (!got) break;
        g1_sha256_update(&sha, buffer, got);
    }
    g1_sha256_final(&sha, digest);
    if (SetFilePointer(source_file, 0, NULL, FILE_BEGIN) == INVALID_SET_FILE_POINTER) goto reject;
    for (i = 0u; i < sizeof(digest); ++i) if (digest[i] != expected->sha256[i]) goto reject;
    return TRUE;
reject:
    ++g_source_guard_rejects;
    return FALSE;
}

static void load_hd_single_file(const char *path)
{
    BYTE source_header[0xBF4], hd_header[0xBF4];
    char source_path[MAX_PATH], *mark, *dot;
    HANDLE source_file, hd_file;
    DWORD source_high = 0u, hd_high = 0u, source_size, hd_size, got = 0u;
    DWORD sw, sh, sc, hw, hh, hc, i, j, width, source_offset, hd_offset, next_offset, range_bytes;
    DWORD hd_table, source_sheet, hd_sheet, source_sheet_width, source_sheet_height, hd_sheet_width, hd_sheet_height;
    DWORD file_id;
    BOOL ytl = FALSE, raw = FALSE;
    if (!g_sidecar_entries) {
        g_sidecar_entries = (G1HdSidecarEntry *)HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, sizeof(G1HdSidecarEntry) * G1_HD_SIDECAR_LIMIT);
        g_sidecar_hash = (DWORD *)HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, sizeof(DWORD) * G1_HD_SIDECAR_HASH_SIZE);
        g_sidecar_dirs = (char (*)[MAX_PATH])HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, MAX_PATH * G1_HD_SIDECAR_DIR_LIMIT);
        g_hd_single_files = (char (*)[MAX_PATH])HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, MAX_PATH * G1_HD_SIDECAR_DIR_LIMIT);
        if (!g_sidecar_entries || !g_sidecar_hash || !g_sidecar_dirs || !g_hd_single_files) return;
    }
    if (lstrlenA(path) >= MAX_PATH || g_hd_single_file_count >= G1_HD_SIDECAR_DIR_LIMIT) return;
    lstrcpyA(source_path, path);
    dot = native_last_dot(source_path);
    if (!dot) return;
    mark = dot - 3;
    if (mark < source_path || mark[0] != '_' || mark[1] != 'h' || mark[2] != 'd') return;
    { DWORD n; for (n = 0u; dot[n]; ++n) mark[n] = dot[n]; mark[n] = '\0'; }
    hd_file = CreateFileA(path, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    source_file = CreateFileA(source_path, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (hd_file == INVALID_HANDLE_VALUE || source_file == INVALID_HANDLE_VALUE) { if (hd_file != INVALID_HANDLE_VALUE) CloseHandle(hd_file); if (source_file != INVALID_HANDLE_VALUE) CloseHandle(source_file); return; }
    if (!source_guard_matches(path, source_file)) goto done;
    source_size = GetFileSize(source_file, &source_high); hd_size = GetFileSize(hd_file, &hd_high);
    dot = native_last_dot(source_path);
    if (dot && !lstrcmpiA(dot, ".bmp")) {
        DWORD source_width = 0u, source_height = 0u, hd_width = 0u, hd_height = 0u;
        DWORD area, digest;
        BYTE source_palette[1024], hd_palette[1024], *pixels;
        char name[64];
        if (source_high || hd_high || source_size == INVALID_FILE_SIZE || hd_size == INVALID_FILE_SIZE ||
            !native_bmp_read(source_path, NULL, 0u, &source_width, &source_height, source_palette) ||
            !native_bmp_read(path, NULL, 0u, &hd_width, &hd_height, hd_palette) ||
            hd_width != source_width * 2u || hd_height != source_height * 2u ||
            !native_equal(source_palette, hd_palette, sizeof(source_palette)) ||
            source_width > 0xFFFFFFFFu / source_height || source_width * source_height < G1_HD_DIGEST_BYTES ||
            source_width * source_height > 64u * 1024u * 1024u || g_hd_single_file_count >= G1_HD_SIDECAR_DIR_LIMIT) goto done;
        area = source_width * source_height;
        pixels = (BYTE *)HeapAlloc(GetProcessHeap(), 0, area);
        if (!pixels) goto done;
        if (native_bmp_read(source_path, pixels, area, &source_width, &source_height, NULL)) {
            digest = native_hash_bytes(pixels, G1_HD_DIGEST_BYTES);
            if (g1_hd_pack_name(name, sizeof(name), digest, source_width, source_height)) {
                file_id = g_hd_single_file_count;
                lstrcpyA(g_hd_single_files[g_hd_single_file_count++], path);
                native_add_kind(name, file_id, 0u, source_width, source_height, 2u);
            }
        }
        HeapFree(GetProcessHeap(), 0, pixels);
        goto done;
    }
    if (source_high || hd_high || source_size == INVALID_FILE_SIZE || hd_size == INVALID_FILE_SIZE ||
        source_size < sizeof(source_header) || hd_size < sizeof(hd_header) ||
        !ReadFile(source_file, source_header, sizeof(source_header), &got, NULL) || got != sizeof(source_header)) goto done;
    if (SetFilePointer(hd_file, 0, NULL, FILE_BEGIN) == INVALID_SET_FILE_POINTER ||
        !ReadFile(hd_file, hd_header, sizeof(hd_header), &got, NULL) || got != sizeof(hd_header)) goto done;
    sw = read_le32(source_header + 4); sh = read_le32(source_header + 8); sc = read_le32(source_header + 12);
    hw = read_le32(hd_header + 4); hh = read_le32(hd_header + 8); hc = read_le32(hd_header + 12);
    if (read_le32(source_header) != 9u || read_le32(hd_header) != 9u || !sw || !sh || !sc || sc > 300u ||
        hw != sw * 2u || hh != sh * 2u || hc != sc) goto done;
    source_sheet = read_le32(source_header + 0xBC8);
    hd_sheet = read_le32(hd_header + 0xBC8); hd_table = read_le32(hd_header + 0x4C4);
    source_sheet_width = read_le32(source_header + 0xBCC); source_sheet_height = read_le32(source_header + 0xBD0);
    hd_sheet_width = read_le32(hd_header + 0xBCC); hd_sheet_height = read_le32(hd_header + 0xBD0);
    dot = native_last_dot(source_path); if (!dot) goto done;
    ytl = !lstrcmpiA(dot, ".ytl");
    if (!ytl) raw = read_le32(source_header + 0xBCC) != 0u &&
                       source_sheet == read_le32(source_header + 0xBCC) * read_le32(source_header + 0xBD0);
    file_id = g_hd_single_file_count;
    lstrcpyA(g_hd_single_files[g_hd_single_file_count++], path);
    if (!ytl && !raw && source_sheet_width >= sw && source_sheet_height >= sh &&
        source_sheet_width % sw == 0u && source_sheet_height % sh == 0u &&
        (source_sheet_width > sw || source_sheet_height > sh) &&
        source_sheet_width * source_sheet_height > sw * sh * sc &&
        hd_sheet_width == source_sheet_width * 2u && hd_sheet_height == source_sheet_height * 2u) {
        native_add_sheet_cells(source_file, source_size, file_id, sw, sh,
                               source_sheet_width, source_sheet_height, source_sheet);
        goto done;
    }
    if (raw) {
        DWORD frame_bytes = sw * sh;
        BYTE *pixels = (BYTE *)HeapAlloc(GetProcessHeap(), 0, frame_bytes);
        if (!pixels) goto done;
        for (i = 0u; i < sc; ++i) {
            char name[64];
            source_offset = 0xBF4u + i * frame_bytes;
            if (source_offset > source_size || source_size - source_offset < frame_bytes ||
                SetFilePointer(source_file, source_offset, NULL, FILE_BEGIN) == INVALID_SET_FILE_POINTER ||
                !ReadFile(source_file, pixels, frame_bytes, &got, NULL) || got != frame_bytes) continue;
            wsprintfA(name, "f%08lx_%lux%lu.idx8", (unsigned long)native_hash_bytes(pixels, frame_bytes),
                      (unsigned long)sw, (unsigned long)sh);
            native_add(name, file_id, i, sw, sh);
        }
        HeapFree(GetProcessHeap(), 0, pixels);
        goto done;
    }
    for (i = 0u; i < sc; ++i) {
        if (ytl) {
            source_offset = 0xBF4u + read_le32(source_header + 0x4C0u + 4u * i);
            hd_offset = 0xBF4u + read_le32(hd_header + 0x4C0u + 4u * i);
            width = native_ytl_width(source_file, source_offset, sh);
        } else {
            source_offset = 0xBF4u + (i ? read_le32(source_header + 0x4C4u + 4u * (i - 1u)) : 0u);
            hd_offset = 0xBF4u + (i ? read_le32(hd_header + 0x4C4u + 4u * (i - 1u)) : 0u);
            width = sw;
        }
        next_offset = source_size;
        for (j = i + 1u; j < sc; ++j) {
            DWORD candidate = ytl ? 0xBF4u + read_le32(source_header + 0x4C0u + 4u * j)
                                 : 0xBF4u + read_le32(source_header + 0x4C4u + 4u * (j - 1u));
            if (candidate > source_offset && candidate < next_offset) next_offset = candidate;
        }
        range_bytes = next_offset > source_offset ? next_offset - source_offset : 0u;
        (void)hd_offset; (void)hd_sheet; (void)hd_table;
        native_add_source_frame(source_file, source_size, file_id, i, source_offset, range_bytes, width, sh);
    }
done:
    CloseHandle(source_file); CloseHandle(hd_file);
}

static DWORD native_find(const char *name)
{
    DWORD found = sidecar_find(name, "");
    if (!found || !g_sidecar_entries[found - 1u].native || g_sidecar_entries[found - 1u].ambiguous) return 0u;
    return found;
}

static BOOL native_decode_bitmap(const char *path, DWORD source_width, DWORD source_height,
                                 BYTE *output, DWORD output_bytes)
{
    DWORD width = 0u, height = 0u;
    if (!source_width || !source_height || source_width > 0xFFFFFFFFu / source_height ||
        source_width * source_height > 0xFFFFFFFFu / 4u ||
        output_bytes != source_width * source_height * 4u ||
        !native_bmp_read(path, output, output_bytes, &width, &height, NULL)) return FALSE;
    return width == source_width * 2u && height == source_height * 2u;
}

static BOOL native_decode_frame(const char *path, DWORD frame, DWORD source_width, DWORD source_height,
                                BYTE *output, DWORD output_bytes)
{
    BYTE header[0xBF4], pair[2], signature[2];
    HANDLE file;
    DWORD got = 0u, high = 0u, size, width, height, count, row, out_width, out_height;
    DWORD offset, sheet, sheet_width, sheet_height, pixel_count, emitted, run;
    BOOL ytl, raw;
    if (!path || !output || !source_width || !source_height ||
        output_bytes != source_width * source_height * 4u) return FALSE;
    file = CreateFileA(path, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (file == INVALID_HANDLE_VALUE) return FALSE;
    size = GetFileSize(file, &high);
    if (high || size == INVALID_FILE_SIZE || size < 2u ||
        SetFilePointer(file, 0u, NULL, FILE_BEGIN) == INVALID_SET_FILE_POINTER ||
        !ReadFile(file, signature, 2u, &got, NULL) || got != 2u) { CloseHandle(file); return FALSE; }
    if (signature[0] == 'B' && signature[1] == 'M') { CloseHandle(file); return native_decode_bitmap(path, source_width, source_height, output, output_bytes); }
    if (size < sizeof(header) ||
        SetFilePointer(file, 0u, NULL, FILE_BEGIN) == INVALID_SET_FILE_POINTER ||
        !ReadFile(file, header, sizeof(header), &got, NULL) || got != sizeof(header) || read_le32(header) != 9u) {
        CloseHandle(file); return FALSE;
    }
    width = read_le32(header + 4); height = read_le32(header + 8); count = read_le32(header + 12);
    out_width = source_width * 2u; out_height = source_height * 2u; pixel_count = out_width * out_height;
    if (width < out_width || height != out_height || width > 32768u || height > 32768u ||
        width > 0xFFFFFFFFu / height || count > 300u) { CloseHandle(file); return FALSE; }
    { volatile BYTE *fill = output; DWORD i; for (i = 0u; i < output_bytes; ++i) fill[i] = 0xFEu; }
    sheet = read_le32(header + 0xBC8); sheet_width = read_le32(header + 0xBCC); sheet_height = read_le32(header + 0xBD0);
    { DWORD path_length = lstrlenA(path); ytl = path_length >= 4u && !lstrcmpiA(path + path_length - 4u, ".ytl"); }
    if (!ytl && sheet_width >= width && sheet_height >= height && sheet_width <= 32768u && sheet_height <= 32768u &&
        sheet_width <= 0xFFFFFFFFu / sheet_height && sheet_width % width == 0u &&
        sheet_height % height == 0u && sheet_width * sheet_height > width * height * count) {
        DWORD cells_x = sheet_width / width, cells_y = sheet_height / height;
        DWORD cell_x, cell_y, sheet_area = sheet_width * sheet_height;
        BYTE *pixels;
        if (frame >= cells_x * cells_y || sheet_area > 64u * 1024u * 1024u) { CloseHandle(file); return FALSE; }
        pixels = (BYTE *)HeapAlloc(GetProcessHeap(), 0, sheet_area);
        if (!pixels) { CloseHandle(file); return FALSE; }
        if (!native_decode_rle(file, size, 0xBF4u, sheet, pixels, sheet_area)) {
            HeapFree(GetProcessHeap(), 0, pixels); CloseHandle(file); return FALSE;
        }
        cell_x = (frame % cells_x) * width; cell_y = (frame / cells_x) * height;
        for (row = 0u; row < height; ++row)
            native_copy(output + row * out_width, pixels + (cell_y + row) * sheet_width + cell_x, out_width);
        HeapFree(GetProcessHeap(), 0, pixels); CloseHandle(file); return TRUE;
    }
    if (frame >= count) { CloseHandle(file); return FALSE; }
    raw = !ytl && sheet_width && sheet == sheet_width * sheet_height;
    if (raw) {
        offset = 0xBF4u + frame * width * height;
        if (offset > size || size - offset < width * height) { CloseHandle(file); return FALSE; }
        for (row = 0u; row < out_height; ++row) {
            if (SetFilePointer(file, offset + row * width, NULL, FILE_BEGIN) == INVALID_SET_FILE_POINTER ||
                !ReadFile(file, output + row * out_width, out_width, &got, NULL) || got != out_width) { CloseHandle(file); return FALSE; }
        }
        CloseHandle(file); return TRUE;
    }
    if (ytl) {
        offset = 0xBF4u + read_le32(header + 0x4C0u + 4u * frame);
        for (row = 0u; row < out_height; ++row) {
            BYTE skip, count_bytes;
            if (SetFilePointer(file, offset, NULL, FILE_BEGIN) == INVALID_SET_FILE_POINTER ||
                !ReadFile(file, pair, 2u, &got, NULL) || got != 2u) { CloseHandle(file); return FALSE; }
            skip = pair[0]; count_bytes = pair[1]; offset += 2u;
            if ((DWORD)skip + count_bytes > width || offset > size || size - offset < count_bytes) { CloseHandle(file); return FALSE; }
            if (count_bytes && skip < out_width) {
                DWORD take = count_bytes;
                if ((DWORD)skip + take > out_width) take = out_width - skip;
                if (SetFilePointer(file, offset, NULL, FILE_BEGIN) == INVALID_SET_FILE_POINTER ||
                    !ReadFile(file, output + row * out_width + skip, take, &got, NULL) || got != take) { CloseHandle(file); return FALSE; }
            }
            offset += count_bytes;
        }
        CloseHandle(file); return TRUE;
    }
    offset = 0xBF4u + (frame ? read_le32(header + 0x4C4u + 4u * (frame - 1u)) : 0u);
    if (offset >= size || SetFilePointer(file, offset, NULL, FILE_BEGIN) == INVALID_SET_FILE_POINTER) { CloseHandle(file); return FALSE; }
    emitted = 0u;
    while (emitted < pixel_count) {
        BYTE value;
        if (!ReadFile(file, &value, 1u, &got, NULL) || got != 1u) { CloseHandle(file); return FALSE; }
        if (value == 0xFEu) {
            if (!ReadFile(file, pair + 1, 1u, &got, NULL) || got != 1u) { CloseHandle(file); return FALSE; }
            run = pair[1];
            if (!run) output[emitted++] = 0xFEu;
            else if (run <= pixel_count - emitted) emitted += run;
            else { CloseHandle(file); return FALSE; }
        } else output[emitted++] = value;
    }
    CloseHandle(file); return TRUE;
}

static BOOL native_load_key(const char *name, DWORD width, DWORD height, BYTE *output, DWORD bytes)
{
    DWORD found = native_find(name), file_id;
    G1HdSidecarEntry *entry;
    if (!found) return FALSE;
    entry = &g_sidecar_entries[found - 1u];
    file_id = entry->directory;
    if (file_id >= g_hd_single_file_count || entry->height != height) return FALSE;
    if (entry->width == 831u && width == 800u) { /* panel writer consumes 800 of 831 columns */ }
    else if (entry->width != width) return FALSE;
    return native_decode_frame(g_hd_single_files[file_id], entry->frame, width, height, output, bytes);
}

static void load_sidecar_index(const char *directory)
{
    char path[MAX_PATH], name[64], pal8[9];
    HANDLE file;
    DWORD high = 0u, size, read = 0u, directory_id, slot;
    char *json, *scan;
    if (!g_sidecar_entries) {
        g_sidecar_entries = (G1HdSidecarEntry *)HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, sizeof(G1HdSidecarEntry) * G1_HD_SIDECAR_LIMIT);
        g_sidecar_hash = (DWORD *)HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, sizeof(DWORD) * G1_HD_SIDECAR_HASH_SIZE);
        g_sidecar_dirs = (char (*)[MAX_PATH])HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, MAX_PATH * G1_HD_SIDECAR_DIR_LIMIT);
        if (!g_sidecar_entries || !g_sidecar_hash || !g_sidecar_dirs) return;
    }
    if (g_sidecar_dir_count >= G1_HD_SIDECAR_DIR_LIMIT ||
        lstrlenA(directory) + 12u >= MAX_PATH) return;
    lstrcpyA(g_sidecar_dirs[g_sidecar_dir_count], directory);
    directory_id = g_sidecar_dir_count++;
    wsprintfA(path, "%s\\index.json", directory);
    file = CreateFileA(path, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (file == INVALID_HANDLE_VALUE) return;
    size = GetFileSize(file, &high);
    if (high || size == INVALID_FILE_SIZE || size > 16u * 1024u * 1024u) { CloseHandle(file); return; }
    json = (char *)HeapAlloc(GetProcessHeap(), 0, size + 1u);
    if (!json) { CloseHandle(file); return; }
    if (!ReadFile(file, json, size, &read, NULL) || read != size) { HeapFree(GetProcessHeap(), 0, json); CloseHandle(file); return; }
    CloseHandle(file); json[size] = '\0';
    scan = sidecar_find_text(json, "\"frames\":[");
    if (!scan) { HeapFree(GetProcessHeap(), 0, json); return; }
    scan += 10;
    while ((scan = sidecar_find_text(scan, "\"frame\":")) != NULL) {
        const char *p = scan + 8;
        DWORD frame, length, p8_value = 0u;
        char p8_text[9];
        G1HdSidecarEntry *entry;
        if (!parse_json_uint(&p, &frame) || !sidecar_prefix(p, ",\"digest\":", 10u)) break;
        p += 10;
        if (!parse_json_string(&p, name, sizeof(name)) || !sidecar_prefix(p, ",\"pal8\":", 8u)) break;
        p += 8;
        if (!parse_json_string(&p, pal8, sizeof(pal8)) || !sidecar_prefix(p, ",\"length\":", 10u)) break;
        p += 10;
        if (!parse_json_uint(&p, &length) || !sidecar_prefix(p, ",\"p8\":", 6u)) break;
        p += 6;
        if (!parse_json_string(&p, p8_text, sizeof(p8_text))) break;
        p8_value = sidecar_hex(p8_text);
        if (!pal8[0] || lstrlenA(pal8) != 8 || frame > 9999u || (DWORD)lstrlenA(name) >= sizeof(name)) break;
        slot = sidecar_find(name, pal8);
        if (slot) { ++g_sidecar_duplicates; scan = (char *)p; continue; }
        if (g_sidecar_count >= G1_HD_SIDECAR_LIMIT) break;
        entry = &g_sidecar_entries[g_sidecar_count];
        lstrcpyA(entry->name, name); lstrcpyA(entry->pal8, pal8);
        entry->frame = frame; entry->directory = directory_id; entry->length = length; entry->p8 = p8_value;
        slot = sidecar_hash_key(name, pal8);
        while (g_sidecar_hash[slot]) slot = (slot + 1u) & (G1_HD_SIDECAR_HASH_SIZE - 1u);
        g_sidecar_hash[slot] = ++g_sidecar_count;
        scan = (char *)p;
    }
    HeapFree(GetProcessHeap(), 0, json);
}

static void scan_sidecar_tree(const char *directory, DWORD depth)
{
    char pattern[MAX_PATH], child[MAX_PATH];
    WIN32_FIND_DATAA data;
    HANDLE find;
    DWORD length;
    if (depth > 12u || lstrlenA(directory) + 4u >= MAX_PATH) return;
    length = lstrlenA(directory);
    wsprintfA(pattern, "%s\\*", directory);
    find = FindFirstFileA(pattern, &data);
    if (find == INVALID_HANDLE_VALUE) return;
    do {
        if (data.dwFileAttributes & FILE_ATTRIBUTE_REPARSE_POINT ||
            !lstrcmpA(data.cFileName, ".") || !lstrcmpA(data.cFileName, "..")) continue;
        if (length + 1u + lstrlenA(data.cFileName) >= MAX_PATH) continue;
        lstrcpyA(child, directory); child[length] = '\\'; lstrcpyA(child + length + 1u, data.cFileName);
        if (data.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) {
            if (lstrlenA(data.cFileName) >= 3 && !lstrcmpiA(data.cFileName + lstrlenA(data.cFileName) - 3, ".hd"))
                load_sidecar_index(child);
            else
                scan_sidecar_tree(child, depth + 1u);
        } else {
            DWORD n = lstrlenA(data.cFileName), i;
            for (i = 0u; i + 4u < n; ++i) if (data.cFileName[i] == '_' && data.cFileName[i + 1u] == 'h' &&
                data.cFileName[i + 2u] == 'd' && data.cFileName[i + 3u] == '.') {
                load_hd_single_file(child);
                break;
            }
        }
    } while (FindNextFileA(find, &data));
    FindClose(find);
}

static void initialize_sidecars(void)
{
    char root[MAX_PATH];
    DWORD size = GetModuleFileNameA(NULL, root, MAX_PATH);
    if (!size || size >= MAX_PATH) return;
    while (size && root[size - 1u] != '\\' && root[size - 1u] != '/') --size;
    if (!size) return;
    root[size - 1u] = '\0';
    lstrcpynA(g_sidecar_root, root, sizeof(g_sidecar_root));
    (void)load_source_guard(root);
    scan_sidecar_tree(root, 0u);
    g_sidecar_enabled = g_sidecar_count != 0u;
}

static BOOL sidecar_path(char *path, DWORD capacity, const char *name, const char *pal8, DWORD length, DWORD p8, DWORD *offset)
{
    char extended[64];
    DWORD ref = sidecar_find(name, pal8), i;
    if (!ref && length) {
        char base[64];
        lstrcpyA(base, name);
        i = 0u;
        while (base[i] && base[i] != '.') ++i;
        if (base[i] == '.') base[i] = '\0';
        wsprintfA(extended, "%s_%lu_%08lx.idx8", base, (unsigned long)length, (unsigned long)p8);
        ref = sidecar_find(extended, pal8);
    }
    if (!ref) return FALSE;
    if (offset) *offset = 0u;
    if (g_sidecar_entries[ref - 1u].frame > 9999u) {
        DWORD file_id = g_sidecar_entries[ref - 1u].directory;
        if (file_id >= g_hd_single_file_count) return FALSE;
        lstrcpynA(path, g_hd_single_files[file_id], capacity);
        if ((DWORD)lstrlenA(path) >= capacity) return FALSE;
        if (offset) *offset = g_sidecar_entries[ref - 1u].frame;
        return TRUE;
    }
    if (wsprintfA(path, "%s\\%04lu.idx8", g_sidecar_dirs[g_sidecar_entries[ref - 1u].directory],
                  (unsigned long)g_sidecar_entries[ref - 1u].frame) >= (int)capacity) return FALSE;
    return TRUE;
}

BOOL g1_hd_asset_load_named_frame(const char *name, DWORD palette, BYTE *output, DWORD bytes)
{
    char path[MAX_PATH], pal8[9];
    DWORD offset = 0u, high = 0u, size, read = 0u;
    HANDLE file;
    if (!name || !output || !bytes || !g1_hd_pack_format_pal(pal8, sizeof(pal8), palette)) return FALSE;
    initialize_environment();
#ifdef _WIN32
    {
        DWORD found = native_find(name);
        if (found) {
            G1HdSidecarEntry *entry = &g_sidecar_entries[found - 1u];
            DWORD width = entry->width == 831u && bytes == 800u * entry->height * 4u ? 800u : entry->width;
            if (entry->height == 0u || bytes != width * entry->height * 4u ||
                entry->directory >= g_hd_single_file_count) return FALSE;
            return native_decode_frame(g_hd_single_files[entry->directory], entry->frame,
                                       width, entry->height, output, bytes);
        }
    }
#endif
    if (!sidecar_path(path, sizeof(path), name, pal8, 0u, 0u, &offset)) return FALSE;
    file = CreateFileA(path, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (file == INVALID_HANDLE_VALUE) return FALSE;
    size = GetFileSize(file, &high);
    if (high == 0u && size != INVALID_FILE_SIZE &&
        ((!offset && size == bytes) || (offset && size >= offset && size - offset >= bytes)) &&
        (!offset || SetFilePointer(file, offset, NULL, FILE_BEGIN) != INVALID_SET_FILE_POINTER) &&
        ReadFile(file, output, bytes, &read, NULL) && read == bytes) {
        CloseHandle(file);
        return TRUE;
    }
    CloseHandle(file);
    return FALSE;
}

static BOOL sibling_pack_path(const G1HdKey *key, char *path, DWORD path_size, DWORD *offset)
{
    char name[40], pal8[9];
    DWORD length, hash, i;
    const BYTE *source = g_current_source;
    if (!g_sidecar_enabled || !g1_hd_pack_name(name, sizeof(name), key->digest, key->width, key->height) ||
        !g1_hd_pack_format_pal(pal8, sizeof(pal8), key->pal)) return FALSE;
    if (sidecar_path(path, path_size, name, pal8, 0u, 0u, offset)) return TRUE;
    if (g_hd_ext_off || !source) return FALSE;
    for (length = 256u; length <= G1_HD_PACK_EXT_MAX; length *= 2u) {
        if (!readable_range(source, length)) break;
        hash = 2166136261u;
        for (i = 0u; i < length; ++i) { hash ^= source[i]; hash *= 16777619u; }
        if (sidecar_path(path, path_size, name, pal8, length, hash, offset)) return TRUE;
        if (length > G1_HD_PACK_EXT_MAX / 2u) break;
    }
    return FALSE;
}

static BOOL sibling_native_load(const G1HdKey *key, BYTE *output, DWORD bytes)
{
    char name[40], extended[64];
    DWORD length, hash, index;
    const BYTE *source = g_current_source;
    if (!key || !source || !g1_hd_pack_name(name, sizeof(name), key->digest, key->width, key->height)) return FALSE;
    if (native_load_key(name, key->width, key->height, output, bytes)) return TRUE;
    if (g_hd_ext_off) return FALSE;
    for (length = 256u; length <= G1_HD_PACK_EXT_MAX; length *= 2u) {
        if (!readable_range(source, length)) break;
        hash = 2166136261u;
        for (index = 0u; index < length; ++index) { hash ^= source[index]; hash *= 16777619u; }
        if (g1_hd_pack_ext_name(extended, sizeof(extended), key->digest, key->width, key->height, length, hash) &&
            native_load_key(extended, key->width, key->height, output, bytes)) return TRUE;
        if (length > G1_HD_PACK_EXT_MAX / 2u) break;
    }
    return FALSE;
}

static BOOL has_pack_assets(void)
{
    return g_hd_pack_dir[0] != '\0' || g_sidecar_enabled;
}
#endif
#ifdef _WIN32
#define G1_HD_PACK_AVAILABLE() has_pack_assets()
#else
#define G1_HD_PACK_AVAILABLE() (g_hd_pack_dir[0] != '\0')
#endif

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
#ifdef _WIN32
        if (!g_hd_pack_dir[0]) initialize_sidecars();
#endif
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
    { BYTE *bytes = (BYTE *)slot; DWORD i; for (i = 0u; i < sizeof(*slot); ++i) bytes[i] = 0u; }
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
    if (auxiliary && G1_HD_PACK_AVAILABLE() && g_hd_source_mode == 2u &&
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
    if (auxiliary && G1_HD_PACK_AVAILABLE() && !g_hd_shade_off && g_hd_source_mode == 2u &&
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
    DWORD sibling_offset = 0u;
    HANDLE file;
    BYTE state = PACK_REJECT;
    BOOL sibling = FALSE;
    g_last_ext = 0u;
    if (key->width != key->identity_width || key->height != key->identity_height ||
        !g1_hd_pack_name(name, sizeof(name), key->digest, key->width, key->height))
        return PACK_REJECT;
    if (!g_hd_pack_dir[0]) {
#ifdef _WIN32
        if (sibling_native_load(key, hd, hd_bytes)) {
            if (is_flip_pack_writer(key->writer) || is_flip_blend_writer(key->writer))
                flip_pack_rows(hd, key->width * 2u, key->height * 2u);
            if (g1_hd_pack_valid(key->identity_written, key->identity_width,
                                 key->identity_width, key->identity_height, hd, hd_bytes)) return PACK_HIT;
            note_reject_detail(key, hd);
            return PACK_REJECT;
        }
        if (!sibling_pack_path(key, path, sizeof(path), &sibling_offset)) return PACK_MISS;
        sibling = TRUE;
        file = CreateFileA(path, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING,
                           FILE_ATTRIBUTE_NORMAL, NULL);
#else
        return PACK_MISS;
#endif
    } else {
        if (!pack_file_path(path, sizeof(path), key->pal, name)) return PACK_REJECT;
        file = CreateFileA(path, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING,
                           FILE_ATTRIBUTE_NORMAL, NULL);
    }
    if (file == INVALID_HANDLE_VALUE) {
        if (sibling) return PACK_MISS;
        note_missing_file(path);
        file = open_extended_pack_file(key);
        if (file == INVALID_HANDLE_VALUE) return PACK_MISS;
    }
    file_bytes = GetFileSize(file, &file_high);
    if (sibling && sibling_offset && (file_high != 0u || file_bytes < sibling_offset || file_bytes - sibling_offset < hd_bytes)) {
        CloseHandle(file);
        return PACK_REJECT;
    }
    if ((!sibling_offset && file_high == 0u && file_bytes == hd_bytes) ||
        (sibling_offset && SetFilePointer(file, sibling_offset, NULL, FILE_BEGIN) != INVALID_SET_FILE_POINTER)) {
      if ((sibling_offset || (file_high == 0u && file_bytes == hd_bytes)) &&
        ReadFile(file, hd, hd_bytes, &bytes_read, NULL) && bytes_read == hd_bytes) {
        if (is_flip_pack_writer(key->writer) || is_flip_blend_writer(key->writer))
            flip_pack_rows(hd, key->width * 2u, key->height * 2u);
        if (g1_hd_pack_valid(key->identity_written, key->identity_width,
                             key->identity_width, key->identity_height, hd, hd_bytes))
            state = PACK_HIT;
        else
            note_reject_detail(key, hd);
      }
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
        if (!G1_HD_PACK_AVAILABLE()) state = PACK_NONE;
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
    return G1_HD_PACK_AVAILABLE();
}

DWORD g1_hd_asset_sibling_duplicates(void)
{
#ifdef _WIN32
    initialize_environment();
    return g_sidecar_duplicates;
#else
    return 0u;
#endif
}
DWORD g1_hd_asset_source_guard_rejects(void)
{
#ifdef _WIN32
    initialize_environment();
    return g_source_guard_rejects;
#else
    return 0u;
#endif
}
/* The flip writers 0x466B50 / 0x466BE0 take the identity key path only when a Scale2x pack run is on and the
 * switch SYW2_G1_HD_PACK_FLIP is not 0; otherwise the caller keeps the plain diff mirror. */
BOOL g1_hd_asset_flip_key_path(void)
{
    initialize_environment();
    return G1_HD_PACK_AVAILABLE() && g_hd_source_mode == 2u && !g_hd_flip_off;
}
/* H-HDB0/H-HDB1/H-HDB2: the translucent writers 0x4672E0 (logo), 0x467580 (weighted) and 0x467B00 (weighted, clipped) take the identity key path only with a Scale2x pack run and the
 * switch SYW2_G1_HD_PACK_BLEND not 0; the pack frame it hits is blended with the HD destination by the caller. */
BOOL g1_hd_asset_blend_key_path(void)
{
    initialize_environment();
    return G1_HD_PACK_AVAILABLE() && g_hd_source_mode == 2u && !g_hd_blend_off;
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
    if (!G1_HD_PACK_AVAILABLE() || g_hd_fullscreen_off || g_hd_source_mode != 2u) return NULL;
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
    if (!g1_hd_pack_fullscreen_name(name, sizeof(name), hash, width, height)) return NULL;
    bytes = width * 2u * height * 2u;
    frame = NULL;
#ifdef _WIN32
    if (!g_hd_pack_dir[0]) {
        frame = (BYTE *)HeapAlloc(GetProcessHeap(), 0, bytes);
        if (!frame || !native_load_key(name, width, height, frame, bytes)) {
            if (frame) HeapFree(GetProcessHeap(), 0, frame);
            frame = NULL;
        } else {
            for (index = 0u; index < bytes; ++index) if (frame[index] == G1_HD_PACK_KEY) {
                HeapFree(GetProcessHeap(), 0, frame);
                frame = NULL;
                break;
            }
        }
        file = INVALID_HANDLE_VALUE;
    } else {
#endif
        if (!pack_file_path(path, sizeof(path), pal, name)) return NULL;
        file = CreateFileA(path, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING,
                           FILE_ATTRIBUTE_NORMAL, NULL);
#ifdef _WIN32
    }
#endif
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
