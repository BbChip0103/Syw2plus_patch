/* G1 W70 P1 writer census.
 *
 * This module is deliberately measurement-only.  It is opt-in through
 * SYW2_G1_CENSUS=1, checks every pinned prologue before installing, calls the
 * original function unchanged, and writes bounded argument samples to a
 * separate JSONL file.  It never writes the renderer buffer or an EXE on disk.
 */

#include "g1_census.h"
#include "g1_census_contract.h"
#include "g1_census_residual.h"
#include "g1_census_watch.h"

#define CENSUS_ENV "SYW2_G1_CENSUS"
#define CENSUS_PATH "C:\\inmm_g1_census.jsonl"
#define CENSUS_MAP_PATH "C:\\inmm_g1_census_map.bin"
#define CENSUS_CONTEXT_MAP_PATH "C:\\inmm_g1_census_context_map.bin"
#define CENSUS_RESIDUAL_MAP_PATH "C:\\inmm_g1_census_residual_map.bin"
#define CENSUS_SAMPLE_LIMIT 32u
#define CENSUS_SURFACE_LIMIT 256u
#define CENSUS_TARGET_COUNT 8u
#define CENSUS_WRITER_COUNT 10u
#define CENSUS_MAX_PROLOGUE 12u
#define CENSUS_MAP_WIDTH 800u
#define CENSUS_MAP_HEIGHT 600u
#define CENSUS_MAP_PIXELS (CENSUS_MAP_WIDTH * CENSUS_MAP_HEIGHT)
#define CENSUS_MAX_BUFFERS 16u
#define CENSUS_PRESENT_LIMIT 64u
#define CENSUS_TEXTOUT_SLOT 0x004E502Cu
#define CENSUS_TEXTOUT_SAMPLE_LIMIT 1024u
#define CENSUS_WATCH_SAMPLE_LIMIT 512u
#define CENSUS_WATCH_EIP_TABLE 24u
#define CENSUS_WATCH_STACK_WORDS 8u
#define CENSUS_WATCH_STACK_SCAN 256u
#define CENSUS_WATCH_CODE_BYTES 24u

typedef DWORD (__attribute__((thiscall)) *CensusFn3)(void *, DWORD, DWORD, DWORD);
typedef DWORD (__attribute__((thiscall)) *CensusFn5)(void *, DWORD, DWORD, DWORD, DWORD, DWORD);
typedef DWORD (__attribute__((thiscall)) *CensusFn6)(void *, DWORD, DWORD, DWORD, DWORD, DWORD, DWORD);
typedef DWORD (__attribute__((thiscall)) *CensusFn7)(void *, DWORD, DWORD, DWORD, DWORD, DWORD, DWORD, DWORD);
typedef void (*CensusWrapper)(void);
typedef BOOL (WINAPI *CensusTextOutA)(HDC, int, int, LPCSTR, int);
typedef BOOL (WINAPI *CensusTextExtentA)(HDC, LPCSTR, int, SIZE *);

typedef struct {
    const char *name;
    DWORD address;
    DWORD length;
    BYTE expected[CENSUS_MAX_PROLOGUE];
    DWORD arity;
    CensusWrapper wrapper;
    BYTE *trampoline;
    DWORD call_count;
    DWORD sample_count;
    DWORD calls_ps3;
    DWORD install_ok;
    BOOL installed;
} CensusTarget;

typedef struct {
    BOOL used;
    DWORD buffer;
    DWORD stride;
    DWORD height;
    DWORD generation;
    DWORD generation_state;
    BYTE *map;
    BYTE *context_map;
    BYTE *shadow;
    DWORD changed_pixels;
    DWORD assigned_pixels;
    DWORD writer_pixels[CENSUS_WRITER_COUNT];
    DWORD writer_calls[CENSUS_WRITER_COUNT];
    DWORD min_x;
    DWORD min_y;
    DWORD max_x;
    DWORD max_y;
} CensusBuffer;

typedef struct {
    DWORD surface;
    DWORD buffer;
    DWORD pitch;
    DWORD width;
    DWORD height;
    BOOL used;
} CensusSurface;

static HANDLE g_log = INVALID_HANDLE_VALUE;
static HANDLE g_map_log = INVALID_HANDLE_VALUE;
static HANDLE g_context_map_log = INVALID_HANDLE_VALUE;
static HANDLE g_residual_map_log = INVALID_HANDLE_VALUE;
static volatile LONG g_guard = 0;
static volatile LONG g_installed = 0;
static DWORD g_sequence = 0;
static DWORD g_surface_events = 0;
static DWORD g_present_sequence = 0;
static DWORD g_map_offset = 0;
static DWORD g_context_map_offset = 0;
static DWORD g_present_count = 0;
static DWORD g_skip_presents = 0u;
static DWORD g_skip_presents_seen = 0u;
static DWORD g_buffer_context_dropped = 0;
static DWORD g_surface_blt_attempts = 0u;
static DWORD g_surface_blt_captured = 0u;
static DWORD g_surface_blt_skip[8];
static volatile LONG g_cache_transfer_calls = 0;
static volatile LONG g_ps3_cache_transfer_calls = 0;
static volatile LONG g_ps3_cache_transfer_window_calls = 0;
static volatile LONG g_terrain_depth = 0;
static DWORD g_terrain_calls = 0;
static BOOL g_dest_probe_enabled = FALSE;
static volatile LONG g_env_state = 0;
static BOOL g_census_enabled = FALSE;
static DWORD g_census_target_state = 3u;
static BOOL g_dest_probe_opt_in = FALSE;
static BOOL g_residual_enabled = FALSE;
static CensusTextOutA g_real_textout = NULL;
static CensusTextExtentA g_text_extent = NULL;  /* resolved at runtime: the DLL does not link gdi32 */
static BOOL g_textout_installed = FALSE;
static DWORD g_textout_calls = 0u;
static DWORD g_textout_window_calls = 0u;
static DWORD g_textout_samples = 0u;
/* Opt-in (residual mode) translucent RLE writers found by the watchpoint. */
#define CENSUS_BLEND_COUNT 2u
#define CENSUS_BLEND_SAMPLE_LIMIT 256u
static DWORD g_blend_window_calls[CENSUS_BLEND_COUNT];
static DWORD g_blend_window_changed[CENSUS_BLEND_COUNT];
static DWORD g_blend_total_changed[CENSUS_BLEND_COUNT];
static DWORD g_blend_samples = 0u;
static DWORD g_blend_window_any = 0u;
static DWORD g_blend_min_x = 0u, g_blend_min_y = 0u, g_blend_max_x = 0u, g_blend_max_y = 0u;
static void emit_blend_boundary(void);
static BOOL g_watch_enabled = FALSE;
static unsigned g_watch_x = 0u;
static unsigned g_watch_y = 0u;
static PVOID g_watch_veh = NULL;
static HANDLE g_watch_thread = NULL;
static DWORD g_watch_thread_id = 0u;
static DWORD g_watch_address = 0u;
static BOOL g_watch_armed = FALSE;
static BOOL g_watch_cache = FALSE;
static DWORD g_watch_presents = 0u;
static DWORD g_watch_present_ticks = 0u;
static BOOL g_watch_done = FALSE;
static volatile LONG g_watch_selftest_active = 0;
static volatile BYTE g_watch_selftest_byte = 0u;
static volatile DWORD g_watch_hits_selftest = 0u;
static DWORD g_watch_hits = 0u;
static DWORD g_watch_hits_in_hook = 0u;
static DWORD g_watch_hits_in_terrain = 0u;
static DWORD g_watch_hits_exe_text = 0u;
static DWORD g_watch_samples = 0u;
static DWORD g_watch_eip_distinct = 0u;
static DWORD g_watch_eip_overflow = 0u;
static DWORD g_watch_eip[CENSUS_WATCH_EIP_TABLE];
static DWORD g_watch_eip_hits[CENSUS_WATCH_EIP_TABLE];
static BOOL g_dest_probe_done[CENSUS_TARGET_COUNT];
static DWORD g_dest_probe_status[CENSUS_TARGET_COUNT];
static CensusBuffer g_buffers[CENSUS_MAX_BUFFERS];
static BYTE g_last_writer_maps[CENSUS_MAX_BUFFERS][CENSUS_MAP_PIXELS];
static BYTE g_last_context_maps[CENSUS_MAX_BUFFERS][CENSUS_MAP_PIXELS];
static BYTE g_residual_shadows[CENSUS_MAX_BUFFERS][CENSUS_MAP_PIXELS];
static BYTE g_residual_mask[CENSUS_MAP_PIXELS];
static BYTE g_before[CENSUS_MAP_PIXELS];
static BYTE g_surface_before[CENSUS_MAP_PIXELS];
static BYTE g_probe_output[CENSUS_MAP_PIXELS];
static CensusSurface g_surfaces[CENSUS_SURFACE_LIMIT];
static CensusBuffer *g_surface_blt_context = NULL;
static DWORD g_surface_blt_buffer = 0u;
static DWORD g_surface_blt_pitch = 0u;
static DWORD g_surface_blt_height = 0u;
static DWORD g_surface_blt_left = 0u;
static DWORD g_surface_blt_top = 0u;
static DWORD g_surface_blt_width = 0u;
static DWORD g_surface_blt_height_rect = 0u;

static DWORD target_result(CensusTarget *target, void *renderer,
                           DWORD a, DWORD b, DWORD c, DWORD d, DWORD e, DWORD f);

static DWORD target_index(const CensusTarget *target)
{
    if (!target) return 0u;
    if (target->address == 0x004664D0u) return 1u;
    if (target->address == 0x00465E80u) return 2u;
    if (target->address == 0x00466280u) return 3u;
    if (target->address == 0x00465B30u) return 4u;
    if (target->address == 0x00466540u) return 5u;
    if (target->address == 0x00466EA0u) return 6u;
    if (target->address == 0x004658E0u) return 7u;
    return 0u;
}

static DWORD fnv1a(const BYTE *bytes, DWORD length)
{
    DWORD hash = 2166136261u;
    DWORD i;
    if (!bytes) return 0u;
    for (i = 0; i < length; ++i) {
        hash ^= bytes[i];
        hash *= 16777619u;
    }
    return hash;
}

static void census_copy_bytes(BYTE *destination, const BYTE *source, DWORD length)
{
    volatile BYTE *out = (volatile BYTE *)destination;
    const volatile BYTE *in = (const volatile BYTE *)source;
    DWORD i;
    for (i = 0; i < length; ++i) out[i] = in[i];
}

static void initialize_environment(void)
{
    char value[8];
    char watch[16];
    DWORD size;
    LONG state = InterlockedCompareExchange(&g_env_state, 1, 0);
    if (state == 0) {
        size = GetEnvironmentVariableA(CENSUS_ENV, value, sizeof(value));
        g_census_enabled = size == 1u && value[0] == '1';
        size = GetEnvironmentVariableA("SYW2_G1_DEST_PROBE", value, sizeof(value));
        g_dest_probe_opt_in = size == 1u && value[0] == '1';
        size = GetEnvironmentVariableA("SYW2_G1_CENSUS_RESIDUAL", value, sizeof(value));
        g_residual_enabled = size == 1u && value[0] == '1';
        size = GetEnvironmentVariableA("SYW2_G1_CENSUS_WATCH", watch, sizeof(watch));
        g_watch_enabled = g_residual_enabled && size > 0u && size < sizeof(watch) &&
                          g1_census_watch_parse(watch, size, &g_watch_x, &g_watch_y);
        size = GetEnvironmentVariableA("SYW2_G1_CENSUS_WATCH_CACHE", value, sizeof(value));
        g_watch_cache = g_watch_enabled && size == 1u && value[0] == '1';
        size = GetEnvironmentVariableA("SYW2_G1_CENSUS_WATCH_PRESENTS", value, sizeof(value));
        g_watch_presents = g_watch_enabled && size < sizeof(value)
            ? g1_census_parse_skip_presents(value, size) : 0u;
        size = GetEnvironmentVariableA("SYW2_G1_CENSUS_SKIP_PRESENTS", value, sizeof(value));
        g_skip_presents = size < sizeof(value)
            ? g1_census_parse_skip_presents(value, size) : 0u;
        size = GetEnvironmentVariableA("SYW2_G1_CENSUS_STATE", value, sizeof(value));
        g_census_target_state = size < sizeof(value)
            ? g1_census_parse_target_state(value, size) : 3u;
        InterlockedExchange(&g_env_state, 2);
    } else {
        while (InterlockedCompareExchange(&g_env_state, 2, 2) != 2) Sleep(0);
    }
}

BOOL g1_census_enabled(void)
{
    initialize_environment();
    return g_census_enabled;
}

DWORD g1_census_target_state(void)
{
    initialize_environment();
    return g_census_target_state;
}

static void write_line(const char *line, DWORD length)
{
    DWORD written = 0u;
    if (g_log == INVALID_HANDLE_VALUE || !line || length == 0u) return;
    WriteFile(g_log, line, length, &written, NULL);
    FlushFileBuffers(g_log);
}

static void open_log(void)
{
    if (g_log != INVALID_HANDLE_VALUE) return;
    g_log = CreateFileA(CENSUS_PATH, GENERIC_WRITE,
                        FILE_SHARE_READ | FILE_SHARE_WRITE, NULL,
                        CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
}

static BOOL readable_range(const void *address, DWORD length)
{
    MEMORY_BASIC_INFORMATION mbi;
    ULONG_PTR start = (ULONG_PTR)address;
    ULONG_PTR end;
    ULONG_PTR region_end;
    if (!address || length == 0u) return FALSE;
    if (!VirtualQuery(address, &mbi, sizeof(mbi)) || mbi.State != MEM_COMMIT ||
        (mbi.Protect & (PAGE_NOACCESS | PAGE_GUARD))) return FALSE;
    end = start + (ULONG_PTR)length;
    region_end = (ULONG_PTR)mbi.BaseAddress + mbi.RegionSize;
    return end >= start && end <= region_end;
}

static BOOL writable_range(void *address, DWORD length)
{
    MEMORY_BASIC_INFORMATION mbi;
    if (!readable_range(address, length)) return FALSE;
    if (!VirtualQuery(address, &mbi, sizeof(mbi))) return FALSE;
    return !(mbi.Protect & (PAGE_READONLY | PAGE_EXECUTE | PAGE_EXECUTE_READ));
}

static DWORD census_program_state(void)
{
    MEMORY_BASIC_INFORMATION mbi;
    if (!VirtualQuery((LPCVOID)0x004ED818u, &mbi, sizeof(mbi)) ||
        mbi.State != MEM_COMMIT || (mbi.Protect & (PAGE_NOACCESS | PAGE_GUARD)))
        return 0xFFFFFFFFu;
    return *(volatile DWORD *)0x004ED818u;
}

/* Opt-in: the shadow starts as the buffer's current content (nothing unhooked
 * yet) and is refreshed after every hooked write. */
static void residual_sync_context(CensusBuffer *context, DWORD x, DWORD y,
                                  DWORD width, DWORD height)
{
    DWORD span;
    if (!g_residual_enabled || !context || !context->shadow || context->stride == 0u)
        return;
    span = (y + height > 0u ? y + height - 1u : 0u) * context->stride + x + width;
    if (!readable_range((const void *)(ULONG_PTR)context->buffer, span)) return;
    (void)g1_census_residual_sync(context->shadow, (const BYTE *)(ULONG_PTR)context->buffer,
                                  context->stride, x, y, width, height);
}

static CensusBuffer *buffer_context(DWORD buffer, DWORD stride, DWORD height)
{
    DWORD i;
    DWORD state = census_program_state();
    if (!buffer || stride < CENSUS_MAP_WIDTH || height == 0u) return NULL;
    for (i = 0; i < CENSUS_MAX_BUFFERS; ++i) {
        CensusBuffer *context = &g_buffers[i];
        DWORD index;
        if (!context->used || !g1_census_buffer_key_matches(
                context->buffer, context->stride, buffer, stride)) continue;
        if (height > context->height) context->height = height;
        if (g1_census_generation_changed(context->generation_state, state,
                                         &context->generation)) {
            for (index = 0; index < CENSUS_MAP_PIXELS; ++index) {
                context->map[index] = 0u;
                context->context_map[index] = 0u;
            }
            context->changed_pixels = 0u;
            context->assigned_pixels = 0u;
            context->generation_state = state;
            context->min_x = CENSUS_MAP_WIDTH;
            context->min_y = CENSUS_MAP_HEIGHT;
            context->max_x = 0u;
            context->max_y = 0u;
            for (index = 0; index < CENSUS_WRITER_COUNT; ++index) {
                context->writer_pixels[index] = 0u;
                context->writer_calls[index] = 0u;
            }
            if (height >= CENSUS_MAP_HEIGHT)
                residual_sync_context(context, 0u, 0u, CENSUS_MAP_WIDTH, CENSUS_MAP_HEIGHT);
        }
        return context;
    }
    for (i = 0; i < CENSUS_MAX_BUFFERS; ++i) {
        if (!g_buffers[i].used) {
            g_buffers[i].used = TRUE;
            g_buffers[i].buffer = buffer;
            g_buffers[i].stride = stride;
            g_buffers[i].height = height;
            g_buffers[i].generation = 1u;
            g_buffers[i].generation_state = state;
            g_buffers[i].map = g_last_writer_maps[i];
            g_buffers[i].context_map = g_last_context_maps[i];
            g_buffers[i].shadow = g_residual_shadows[i];
            g_buffers[i].min_x = CENSUS_MAP_WIDTH;
            g_buffers[i].min_y = CENSUS_MAP_HEIGHT;
            g_buffers[i].max_x = 0u;
            g_buffers[i].max_y = 0u;
            if (height >= CENSUS_MAP_HEIGHT)
                residual_sync_context(&g_buffers[i], 0u, 0u, CENSUS_MAP_WIDTH, CENSUS_MAP_HEIGHT);
            return &g_buffers[i];
        }
    }
    return NULL;
}

static BOOL renderer_buffer(void *renderer, DWORD *buffer, DWORD *stride, DWORD *height)
{
    MEMORY_BASIC_INFORMATION mbi;
    if (!renderer || !buffer || !stride || !height) return FALSE;
    if (!VirtualQuery((LPCVOID)((BYTE *)renderer + 0x1514u), &mbi, sizeof(mbi)) ||
        mbi.State != MEM_COMMIT || (mbi.Protect & (PAGE_NOACCESS | PAGE_GUARD))) return FALSE;
    *buffer = *(volatile DWORD *)((BYTE *)renderer + 0x1514u);
    *stride = *(volatile DWORD *)((BYTE *)renderer + 0x10u);
    *height = *(volatile DWORD *)((BYTE *)renderer + 0x08u);
    return *buffer != 0u && *stride >= CENSUS_MAP_WIDTH && *height >= CENSUS_MAP_HEIGHT;
}

static BOOL call_bbox(const CensusTarget *target, DWORD a, DWORD b, DWORD c, DWORD d,
                      DWORD stride, DWORD height, DWORD *x, DWORD *y,
                      DWORD *width, DWORD *box_height)
{
    DWORD right;
    DWORD bottom;
    if (!target || !x || !y || !width || !box_height) return FALSE;
    *x = a; *y = b;
    if (target->arity == 3u) {
        *width = 1u; *box_height = 1u;
    } else if (target->address == 0x00465E80u || target->address == 0x00465B30u) {
        if (c <= a || d <= b) return FALSE;
        *width = c - a; *box_height = d - b;
    } else {
        *width = c; *box_height = d;
    }
    if (*x >= CENSUS_MAP_WIDTH || *y >= CENSUS_MAP_HEIGHT || *width == 0u ||
        *box_height == 0u || *x + *width < *x || *y + *box_height < *y) return FALSE;
    right = *x + *width; bottom = *y + *box_height;
    if (right > CENSUS_MAP_WIDTH) *width = CENSUS_MAP_WIDTH - *x;
    if (bottom > CENSUS_MAP_HEIGHT) *box_height = CENSUS_MAP_HEIGHT - *y;
    if (*width == 0u || *box_height == 0u || stride < CENSUS_MAP_WIDTH ||
        height < CENSUS_MAP_HEIGHT) return FALSE;
    return TRUE;
}

static BOOL snapshot_before(CensusBuffer *context, DWORD x, DWORD y,
                            DWORD width, DWORD height)
{
    DWORD row;
    BYTE *buffer;
    if (!context || width > CENSUS_MAP_WIDTH || height > CENSUS_MAP_HEIGHT) return FALSE;
    buffer = (BYTE *)(ULONG_PTR)context->buffer;
    if (!readable_range(buffer, context->height * context->stride))
        return FALSE;
    for (row = 0; row < height; ++row)
        for (DWORD col = 0; col < width; ++col)
            g_before[row * width + col] = buffer[(y + row) * context->stride + x + col];
    return TRUE;
}

static void map_changes(CensusBuffer *context, DWORD writer, DWORD x, DWORD y,
                        DWORD width, DWORD height, BOOL semantic_write)
{
    DWORD row, col;
    BYTE context_id = InterlockedCompareExchange(&g_terrain_depth, 0, 0) > 0 ? 1u : 0u;
    BYTE *buffer;
    if (!context || !context->map || !context->context_map || writer == 0u) return;
    buffer = (BYTE *)(ULONG_PTR)context->buffer;
    for (row = 0; row < height; ++row) {
        for (col = 0; col < width; ++col) {
            DWORD map_index = (y + row) * CENSUS_MAP_WIDTH + x + col;
            BYTE before = g_before[row * width + col];
            BYTE after = buffer[(y + row) * context->stride + x + col];
            BYTE previous;
            if (!semantic_write && before == after) continue;
            previous = context->map[map_index];
            if (previous == writer) {
                context->context_map[map_index] = context_id;
                continue;
            }
            if (previous > 0u && previous <= CENSUS_WRITER_COUNT &&
                context->writer_pixels[previous - 1u] > 0u)
                --context->writer_pixels[previous - 1u];
            if (previous == 0u) ++context->assigned_pixels;
            context->map[map_index] = (BYTE)writer;
            context->context_map[map_index] = context_id;
            ++context->writer_pixels[writer - 1u];
            ++context->changed_pixels;
            if (x + col < context->min_x) context->min_x = x + col;
            if (y + row < context->min_y) context->min_y = y + row;
            if (x + col > context->max_x) context->max_x = x + col;
            if (y + row > context->max_y) context->max_y = y + row;
        }
    }
}

static void restore_snapshot(CensusBuffer *context, DWORD x, DWORD y,
                             DWORD width, DWORD height, const BYTE *source)
{
    DWORD row, col;
    BYTE *buffer;
    if (!context || !source) return;
    buffer = (BYTE *)(ULONG_PTR)context->buffer;
    if (!writable_range(buffer, context->height * context->stride)) return;
    for (row = 0; row < height; ++row)
        for (col = 0; col < width; ++col)
            buffer[(y + row) * context->stride + x + col] = source[row * width + col];
}

static void emit_dest_probe(const CensusTarget *target, DWORD status)
{
    char line[600];
    int length;
    const char *name = status == 1u ? "dest_read" :
                       status == 2u ? "no_dest_read" : "inconclusive";
    length = wsprintfA(line,
        "{\"schema\":\"g1-writer-census-v1\",\"event\":\"dest_probe\","
        "\"writer\":\"%s\",\"status\":\"%s\",\"restored\":1,"
        "\"measurement_only\":1}\n", target->name, name);
    if (length > 0) write_line(line, (DWORD)length);
}

static void probe_destination_read(CensusTarget *target, CensusBuffer *context,
                                   void *renderer,
                                   DWORD a, DWORD b, DWORD c, DWORD d, DWORD e, DWORD f,
                                   DWORD x, DWORD y, DWORD width, DWORD height)
{
    DWORD row, col;
    BOOL differs = FALSE;
    BOOL output_changed = FALSE;
    BYTE *buffer;
    if (!g_dest_probe_enabled || !target || !context || target->call_count != 1u ||
        g_dest_probe_done[target_index(target)] || width * height > CENSUS_MAP_PIXELS)
        return;
    g_dest_probe_done[target_index(target)] = TRUE;
    buffer = (BYTE *)(ULONG_PTR)context->buffer;
    for (row = 0; row < height; ++row)
        for (col = 0; col < width; ++col) {
            g_probe_output[row * width + col] = buffer[(y + row) * context->stride + x + col];
            if (g_probe_output[row * width + col] != g_before[row * width + col]) output_changed = TRUE;
        }
    restore_snapshot(context, x, y, width, height, g_before);
    if (writable_range(buffer, context->height * context->stride)) {
        DWORD perturb = y * context->stride + x + (height / 2u) * context->stride + width / 2u;
        ((BYTE *)(ULONG_PTR)context->buffer)[perturb] ^= 0x5Au;
        (void)target_result(target, renderer, a, b, c, d, e, f);
        for (row = 0; row < height; ++row)
            for (col = 0; col < width; ++col)
                if (buffer[(y + row) * context->stride + x + col] !=
                    g_probe_output[row * width + col]) differs = TRUE;
        restore_snapshot(context, x, y, width, height, g_probe_output);
    }
    g_dest_probe_status[target_index(target)] = !output_changed ? 3u : (differs ? 1u : 2u);
    emit_dest_probe(target, g_dest_probe_status[target_index(target)]);
}

static void emit_install(const CensusTarget *target, BOOL ok)
{
    char line[720];
    int length;
    if (!target) return;
    length = wsprintfA(line,
        "{\"schema\":\"g1-writer-census-v1\",\"event\":\"install\","
        "\"writer\":\"%s\",\"target\":\"0x%08X\",\"arity\":%u,"
        "\"prologue_len\":%u,\"old_bytes_fnv1a32\":\"0x%08X\","
        "\"status\":\"%s\",\"measurement_only\":1}\n",
        target->name, (unsigned)target->address, (unsigned)target->arity,
        (unsigned)target->length, (unsigned)fnv1a(target->expected, target->length),
        ok ? "active" : "skipped_old_bytes_mismatch");
    if (length > 0) write_line(line, (DWORD)length);
}

static void emit_call(CensusTarget *target, void *renderer,
                      DWORD a, DWORD b, DWORD c, DWORD d, DWORD e, DWORD f,
                      DWORD result)
{
    char line[1300];
    int length;
    DWORD state = 0xFFFFFFFFu;
    DWORD tick = 0xFFFFFFFFu;
    DWORD stride = 0xFFFFFFFFu;
    DWORD height = 0xFFFFFFFFu;
    DWORD buffer = 0u;
    DWORD terrain_context = InterlockedCompareExchange(&g_terrain_depth, 0, 0) > 0 ? 1u : 0u;
    const char *writer_name = target && target->address == 0x00466280u &&
        e == 0x00BA3D30u ? "terrain_cache_transfer" : target->name;
    if (!target || target->sample_count >= CENSUS_SAMPLE_LIMIT) return;
    ++target->sample_count;
    ++g_sequence;
    if (renderer) {
        MEMORY_BASIC_INFORMATION mbi;
        if (VirtualQuery((LPCVOID)((BYTE *)renderer + 0x10u), &mbi,
                         sizeof(mbi)) && mbi.State == MEM_COMMIT &&
            !(mbi.Protect & (PAGE_NOACCESS | PAGE_GUARD))) {
            stride = *(volatile DWORD *)((BYTE *)renderer + 0x10u);
            height = *(volatile DWORD *)((BYTE *)renderer + 0x08u);
            buffer = *(volatile DWORD *)((BYTE *)renderer + 0x1514u);
        }
    }
    /* PROGRAM_STATE/GLOBAL_TICK are read only when mapped. */
    {
        MEMORY_BASIC_INFORMATION mbi;
        if (VirtualQuery((LPCVOID)0x004ED818u, &mbi, sizeof(mbi)) &&
            mbi.State == MEM_COMMIT && !(mbi.Protect & (PAGE_NOACCESS | PAGE_GUARD)))
            state = *(volatile DWORD *)0x004ED818u;
        if (VirtualQuery((LPCVOID)0x009B5210u, &mbi, sizeof(mbi)) &&
            mbi.State == MEM_COMMIT && !(mbi.Protect & (PAGE_NOACCESS | PAGE_GUARD)))
            tick = *(volatile DWORD *)0x009B5210u;
    }
    length = wsprintfA(line,
        "{\"schema\":\"g1-writer-census-v1\",\"event\":\"primitive_call\","
        "\"seq\":%u,\"writer\":\"%s\",\"target\":\"0x%08X\","
        "\"this\":\"0x%08X\",\"args\":[%u,%u,%u,%u,%u,%u],\"result\":%u,"
        "\"renderer_stride\":%u,\"renderer_height\":%u,\"renderer_buffer\":\"0x%08X\","
        "\"program_state\":%u,\"game_tick\":%u,\"writer_context\":\"%s\","
        "\"context_address\":\"0x%08X\",\"dest_read\":\"unknown\","
        "\"sample\":%u,\"measurement_only\":1}\n",
        (unsigned)g_sequence, writer_name, (unsigned)target->address,
        (unsigned)(ULONG_PTR)renderer, (unsigned)a, (unsigned)b, (unsigned)c,
        (unsigned)d, (unsigned)e, (unsigned)f, (unsigned)result,
        (unsigned)stride, (unsigned)height, (unsigned)buffer, (unsigned)state,
        (unsigned)tick, terrain_context ? "terrain_0x403B20" : "direct_primitive",
        terrain_context ? 0x00403B20u : 0u, (unsigned)target->sample_count);
    if (length > 0) write_line(line, (DWORD)length);
}

static void emit_surface_summary(const char *method, DWORD self, DWORD source,
                                 DWORD dw, DWORD dh, DWORD sw, DWORD sh,
                                 DWORD state, DWORD tick, DWORD caller,
                                 BOOL destination_is_primary,
                                 DWORD destination_caps, DWORD source_caps)
{
    char line[1200];
    int length;
    if (g_surface_events >= CENSUS_SURFACE_LIMIT) return;
    ++g_surface_events;
    ++g_sequence;
    length = wsprintfA(line,
        "{\"schema\":\"g1-writer-census-v1\",\"event\":\"surface_write\","
        "\"seq\":%u,\"writer\":\"DirectDraw.%s\",\"this\":\"0x%08X\","
        "\"source\":\"0x%08X\",\"destination_width\":%u,\"destination_height\":%u,"
        "\"source_width\":%u,\"source_height\":%u,\"program_state\":%u,"
        "\"game_tick\":%u,\"caller\":\"0x%08X\",\"return_address\":\"0x%08X\","
        "\"destination_is_primary\":%u,\"destination_caps\":%u,\"source_caps\":%u,"
        "\"pixel_provenance\":\"%s\",\"dest_read\":\"unknown\",\"measurement_only\":1}\n",
        (unsigned)g_sequence, method ? method : "unknown", (unsigned)self,
        (unsigned)source, (unsigned)dw, (unsigned)dh, (unsigned)sw, (unsigned)sh,
        (unsigned)state, (unsigned)tick, (unsigned)caller, (unsigned)caller,
        (unsigned)destination_is_primary, (unsigned)destination_caps,
        (unsigned)source_caps, destination_is_primary ? "primary_present" : "offscreen_blt");
    if (length > 0) write_line(line, (DWORD)length);
}

static void emit_terrain_context_call(void *renderer,
                                      DWORD a, DWORD b, DWORD c, DWORD d,
                                      DWORD e, DWORD f, DWORD g)
{
    DWORD vtable = 0u;
    DWORD method = 0u;
    DWORD state = 0xFFFFFFFFu;
    DWORD tick = 0xFFFFFFFFu;
    char line[1100];
    int length;
    MEMORY_BASIC_INFORMATION mbi;
    if (g_terrain_calls > CENSUS_SAMPLE_LIMIT) return;
    if (readable_range(renderer, sizeof(DWORD))) {
        vtable = *(volatile DWORD *)renderer;
        if (readable_range((void *)(ULONG_PTR)(vtable + 0x30u), sizeof(DWORD)))
            method = *(volatile DWORD *)(ULONG_PTR)(vtable + 0x30u);
    }
    if (VirtualQuery((LPCVOID)0x004ED818u, &mbi, sizeof(mbi)) &&
        mbi.State == MEM_COMMIT && !(mbi.Protect & (PAGE_NOACCESS | PAGE_GUARD)))
        state = *(volatile DWORD *)0x004ED818u;
    if (VirtualQuery((LPCVOID)0x009B5210u, &mbi, sizeof(mbi)) &&
        mbi.State == MEM_COMMIT && !(mbi.Protect & (PAGE_NOACCESS | PAGE_GUARD)))
        tick = *(volatile DWORD *)0x009B5210u;
    length = wsprintfA(line,
        "{\"schema\":\"g1-writer-census-v1\",\"event\":\"terrain_context_call\","
        "\"context_address\":\"0x00403B20\",\"renderer\":\"0x%08X\","
        "\"vtable\":\"0x%08X\",\"method_0x30\":\"0x%08X\","
        "\"args\":[%u,%u,%u,%u,%u,%u,%u],\"program_state\":%u,"
        "\"game_tick\":%u,\"measurement_only\":1}\n",
        (unsigned)(ULONG_PTR)renderer, (unsigned)vtable, (unsigned)method,
        (unsigned)a, (unsigned)b, (unsigned)c, (unsigned)d, (unsigned)e,
        (unsigned)f, (unsigned)g, (unsigned)state, (unsigned)tick);
    if (length > 0) write_line(line, (DWORD)length);
}

void g1_census_record_surface_write(const char *method, DWORD self,
                                    DWORD source, DWORD destination_width,
                                    DWORD destination_height, DWORD source_width,
                                    DWORD source_height, DWORD program_state,
                                    DWORD game_tick, DWORD caller,
                                    BOOL destination_is_primary,
                                    DWORD destination_caps, DWORD source_caps)
{
    if (!g1_census_enabled() || g_log == INVALID_HANDLE_VALUE) return;
    emit_surface_summary(method, self, source, destination_width,
                         destination_height, source_width, source_height,
                         program_state, game_tick, caller, destination_is_primary,
                         destination_caps, source_caps);
}

static CensusBuffer *present_source_buffer(DWORD buffer, DWORD pitch)
{
    DWORD i;
    G1CensusBufferKey keys[CENSUS_MAX_BUFFERS];
    int match;
    for (i = 0; i < CENSUS_MAX_BUFFERS; ++i) {
        keys[i].buffer = g_buffers[i].used ? g_buffers[i].buffer : 0u;
        keys[i].stride = g_buffers[i].used ? g_buffers[i].stride : 0u;
    }
    match = g1_census_find_source_buffer(keys, CENSUS_MAX_BUFFERS, buffer, pitch);
    return match >= 0 ? &g_buffers[(DWORD)match] : NULL;
}

static void unknown_index_top(const CensusBuffer *selected, DWORD source_buffer,
                              DWORD source_pitch, G1CensusIndexCount top[4])
{
    unsigned long histogram[256];
    const volatile BYTE *pixels = (const volatile BYTE *)(ULONG_PTR)source_buffer;
    DWORD x, y;
    for (x = 0; x < 256u; ++x) histogram[x] = 0u;
    if (selected && source_pitch >= CENSUS_MAP_WIDTH &&
        readable_range((const void *)(ULONG_PTR)source_buffer,
                       (CENSUS_MAP_HEIGHT - 1u) * source_pitch + CENSUS_MAP_WIDTH)) {
        for (y = 0; y < CENSUS_MAP_HEIGHT; ++y)
            for (x = 0; x < CENSUS_MAP_WIDTH; ++x)
                if (selected->map[y * CENSUS_MAP_WIDTH + x] == 0u)
                    ++histogram[pixels[y * source_pitch + x]];
    }
    g1_census_index_top(histogram, top);
}

/* Opt-in watchpoint (SYW2_G1_CENSUS_WATCH=x,y, residual mode only): one hardware
 * write breakpoint on a present-source pixel that every present left unhooked.
 * A vectored handler logs who wrote it (EIP, registers, the bytes just before
 * EIP, .text return addresses on the stack) and whether a census hook was
 * active.  The game's buffer is never written; the self test uses a private
 * byte.  Data breakpoints trap after the writing instruction, so EIP is the
 * instruction following the write. */
static BOOL watch_apply(DWORD address, DWORD dr7)
{
    CONTEXT context;
    BOOL self = g_watch_thread_id == GetCurrentThreadId();
    HANDLE thread = self ? GetCurrentThread() : g_watch_thread;
    BOOL ok = FALSE;
    if (!thread || (!self && SuspendThread(thread) == (DWORD)-1)) return FALSE;
    context.ContextFlags = CONTEXT_DEBUG_REGISTERS;
    if (GetThreadContext(thread, &context)) {
        context.Dr0 = address;
        context.Dr6 = 0u;
        context.Dr7 = dr7;
        ok = SetThreadContext(thread, &context);
    }
    if (!self) ResumeThread(thread);
    return ok;
}

static BOOL watch_arm_address(DWORD address)
{
    return watch_apply(address, G1_CENSUS_WATCH_DR7);
}

static void watch_note_eip(DWORD eip)
{
    DWORD i;
    for (i = 0u; i < g_watch_eip_distinct; ++i)
        if (g_watch_eip[i] == eip) { ++g_watch_eip_hits[i]; return; }
    if (g_watch_eip_distinct < CENSUS_WATCH_EIP_TABLE) {
        g_watch_eip[g_watch_eip_distinct] = eip;
        g_watch_eip_hits[g_watch_eip_distinct++] = 1u;
    } else {
        ++g_watch_eip_overflow;
    }
}

static void watch_log_hit(const CONTEXT *c)
{
    static const char hex[] = "0123456789ABCDEF";
    char code[CENSUS_WATCH_CODE_BYTES * 2u + 1u];
    DWORD stack[CENSUS_WATCH_STACK_WORDS];
    DWORD found = 0u, i;
    const BYTE *bytes = (const BYTE *)(ULONG_PTR)(c->Eip - CENSUS_WATCH_CODE_BYTES);
    const DWORD *sp = (const DWORD *)(ULONG_PTR)c->Esp;
    DWORD scan = CENSUS_WATCH_STACK_SCAN;
    char line[1200];
    int length;
    for (i = 0u; i < CENSUS_WATCH_STACK_WORDS; ++i) stack[i] = 0u;
    if (!readable_range(sp, scan * sizeof(DWORD))) scan = 32u;
    if (readable_range(sp, scan * sizeof(DWORD)))
        for (i = 0u; i < scan && found < CENSUS_WATCH_STACK_WORDS; ++i)
            if (g1_census_watch_is_exe_text(sp[i])) stack[found++] = sp[i];
    if (readable_range(bytes, CENSUS_WATCH_CODE_BYTES)) {
        for (i = 0u; i < CENSUS_WATCH_CODE_BYTES; ++i) {
            code[i * 2u] = hex[bytes[i] >> 4];
            code[i * 2u + 1u] = hex[bytes[i] & 15u];
        }
        code[CENSUS_WATCH_CODE_BYTES * 2u] = 0;
    } else {
        code[0] = 0;
    }
    length = wsprintfA(line,
        "{\"schema\":\"g1-writer-census-v1\",\"event\":\"watch_hit\","
        "\"seq\":%u,\"present\":%u,\"watch_present\":%u,\"eip\":\"0x%08X\",\"eip_in_exe_text\":%u,"
        "\"in_hook\":%u,\"in_terrain\":%u,\"dr6\":\"0x%08X\","
        "\"eax\":\"0x%08X\",\"ebx\":\"0x%08X\",\"ecx\":\"0x%08X\",\"edx\":\"0x%08X\","
        "\"esi\":\"0x%08X\",\"edi\":\"0x%08X\",\"ebp\":\"0x%08X\",\"esp\":\"0x%08X\","
        "\"value\":%u,\"code_before_eip\":\"%s\","
        "\"stack_text\":[\"0x%08X\",\"0x%08X\",\"0x%08X\",\"0x%08X\","
        "\"0x%08X\",\"0x%08X\",\"0x%08X\",\"0x%08X\"],\"measurement_only\":1}\n",
        (unsigned)g_watch_hits, (unsigned)(g_present_sequence + 1u),
        (unsigned)g_watch_present_ticks, (unsigned)c->Eip,
        (unsigned)g1_census_watch_is_exe_text(c->Eip),
        (unsigned)(g_guard != 0), (unsigned)(g_terrain_depth > 0), (unsigned)c->Dr6,
        (unsigned)c->Eax, (unsigned)c->Ebx, (unsigned)c->Ecx, (unsigned)c->Edx,
        (unsigned)c->Esi, (unsigned)c->Edi, (unsigned)c->Ebp, (unsigned)c->Esp,
        (unsigned)*(volatile BYTE *)(ULONG_PTR)g_watch_address, code,
        (unsigned)stack[0], (unsigned)stack[1], (unsigned)stack[2], (unsigned)stack[3],
        (unsigned)stack[4], (unsigned)stack[5], (unsigned)stack[6], (unsigned)stack[7]);
    if (length > 0) write_line(line, (DWORD)length);
}

static LONG CALLBACK census_watch_veh(EXCEPTION_POINTERS *info)
{
    CONTEXT *c;
    if (info->ExceptionRecord->ExceptionCode != EXCEPTION_SINGLE_STEP ||
        g_watch_thread_id == 0u || GetCurrentThreadId() != g_watch_thread_id)
        return EXCEPTION_CONTINUE_SEARCH;
    c = info->ContextRecord;
    if (g_watch_selftest_active) {
        ++g_watch_hits_selftest;
        c->Dr6 = 0u;
        return EXCEPTION_CONTINUE_EXECUTION;
    }
    if (!g_watch_armed) return EXCEPTION_CONTINUE_SEARCH;
    ++g_watch_hits;
    if (g_guard != 0) ++g_watch_hits_in_hook;
    if (g_terrain_depth > 0) ++g_watch_hits_in_terrain;
    if (g1_census_watch_is_exe_text(c->Eip)) ++g_watch_hits_exe_text;
    watch_note_eip(c->Eip);
    if (g_watch_samples < CENSUS_WATCH_SAMPLE_LIMIT) {
        ++g_watch_samples;
        watch_log_hit(c);
    }
    c->Dr6 = 0u;
    return EXCEPTION_CONTINUE_EXECUTION;
}

static BOOL watch_selftest(void)
{
    DWORD before = g_watch_hits_selftest;
    BOOL armed, hit = FALSE;
    char line[260];
    int length;
    g_watch_selftest_active = 1;
    armed = watch_arm_address((DWORD)(ULONG_PTR)&g_watch_selftest_byte);
    if (armed) {
        g_watch_selftest_byte = 0x5Au;
        hit = g_watch_hits_selftest == before + 1u;
        (void)watch_apply(0u, 0u);
    }
    g_watch_selftest_active = 0;
    length = wsprintfA(line,
        "{\"schema\":\"g1-writer-census-v1\",\"event\":\"watch_selftest\","
        "\"armed\":%u,\"hits\":%u,\"status\":\"%s\",\"measurement_only\":1}\n",
        (unsigned)armed, (unsigned)(g_watch_hits_selftest - before),
        hit ? "PASS" : (armed ? "no_hit" : "set_context_failed"));
    if (length > 0) write_line(line, (DWORD)length);
    return hit;
}

/* Release the debug register, drop the handler and publish the tally once. */
static void watch_finish(const char *reason)
{
    char line[1400];
    int length, n;
    DWORD i;
    if (!g_watch_enabled || g_watch_done) return;
    g_watch_done = TRUE;
    if (g_watch_armed) {
        g_watch_armed = FALSE;
        (void)watch_apply(0u, 0u);
    }
    if (g_watch_veh) {
        RemoveVectoredExceptionHandler(g_watch_veh);
        g_watch_veh = NULL;
    }
    if (g_watch_thread) {
        CloseHandle(g_watch_thread);
        g_watch_thread = NULL;
    }
    length = wsprintfA(line,
        "{\"schema\":\"g1-writer-census-v1\",\"event\":\"watch_summary\","
        "\"reason\":\"%s\",\"pixel\":[%u,%u],\"address\":\"0x%08X\","
        "\"cache\":%u,\"watch_presents\":%u,\"watch_present_ticks\":%u,"
        "\"hits\":%u,\"hits_in_hook\":%u,\"hits_in_terrain\":%u,"
        "\"hits_eip_in_exe_text\":%u,\"samples\":%u,\"distinct_eip\":%u,"
        "\"eip_overflow\":%u,\"selftest_hits\":%u,\"eips\":[",
        reason, g_watch_x, g_watch_y, (unsigned)g_watch_address,
        (unsigned)g_watch_cache, (unsigned)g_watch_presents,
        (unsigned)g_watch_present_ticks, (unsigned)g_watch_hits, (unsigned)g_watch_hits_in_hook,
        (unsigned)g_watch_hits_in_terrain, (unsigned)g_watch_hits_exe_text,
        (unsigned)g_watch_samples, (unsigned)g_watch_eip_distinct,
        (unsigned)g_watch_eip_overflow, (unsigned)g_watch_hits_selftest);
    for (i = 0u; i < g_watch_eip_distinct && length > 0 && length < 1200; ++i) {
        n = wsprintfA(line + length, "%s[\"0x%08X\",%u]", i ? "," : "",
                      (unsigned)g_watch_eip[i], (unsigned)g_watch_eip_hits[i]);
        if (n > 0) length += n;
    }
    n = wsprintfA(line + length, "],\"measurement_only\":1}\n");
    if (length > 0 && n > 0) write_line(line, (DWORD)(length + n));
}

/* Called at each PS3 present boundary with the locked, census-selected source. */
static void watch_on_present(BOOL selected_source, DWORD source_buffer, DWORD source_pitch)
{
    char line[300];
    int length;
    if (!g_watch_enabled || g_watch_done) return;
    if (g_watch_armed) {
        /* an explicit watch window (H-S2w) outlives the 64-present census window */
        if (!g_watch_presents && g_present_count >= CENSUS_PRESENT_LIMIT)
            watch_finish("window_end");
        return;
    }
    if (!selected_source || source_pitch < CENSUS_MAP_WIDTH) return;
    g_watch_address = g_watch_cache
        ? (DWORD)g1_census_watch_cache_address(g_watch_x, g_watch_y)
        : (DWORD)g1_census_watch_pixel_address(
              source_buffer, source_pitch, g_watch_x, g_watch_y);
    if (!readable_range((const void *)(ULONG_PTR)g_watch_address, 1u)) return;
    g_watch_thread_id = GetCurrentThreadId();
    if (!DuplicateHandle(GetCurrentProcess(), GetCurrentThread(), GetCurrentProcess(),
                         &g_watch_thread, 0u, FALSE, DUPLICATE_SAME_ACCESS))
        g_watch_thread = NULL;
    g_watch_veh = AddVectoredExceptionHandler(1, census_watch_veh);
    if (!g_watch_veh || !watch_selftest() ||
        !watch_arm_address(g_watch_address)) {
        watch_finish("arm_failed");
        return;
    }
    g_watch_armed = TRUE;
    length = wsprintfA(line,
        "{\"schema\":\"g1-writer-census-v1\",\"event\":\"watch_armed\","
        "\"present\":%u,\"pixel\":[%u,%u],\"address\":\"0x%08X\","
        "\"cache\":%u,\"watch_presents\":%u,"
        "\"thread_id\":%u,\"selftest_hits\":%u,\"measurement_only\":1}\n",
        (unsigned)g_present_sequence, g_watch_x, g_watch_y,
        (unsigned)g_watch_address, (unsigned)g_watch_cache,
        (unsigned)g_watch_presents, (unsigned)g_watch_thread_id,
        (unsigned)g_watch_hits_selftest);
    if (length > 0) write_line(line, (DWORD)length);
}

/* Opt-in residual: compare the locked present source with the shadow of the
 * last hooked result.  Separate event/file; the default census is unchanged. */
static void emit_residual_boundary(const CensusBuffer *selected, DWORD source_buffer,
                                   DWORD source_pitch, DWORD state, const DWORD header[8])
{
    G1CensusResidual residual;
    G1CensusIndexCount top[4];
    DWORD written;
    DWORD i;
    char line[700];
    int length;
    if (!readable_range((const void *)(ULONG_PTR)source_buffer,
                        (CENSUS_MAP_HEIGHT - 1u) * source_pitch + CENSUS_MAP_WIDTH)) return;
    {   /* volatile: keep the CRT-less DLL from linking a compiler-made memset */
        volatile BYTE *mask = (volatile BYTE *)g_residual_mask;
        for (i = 0; i < CENSUS_MAP_PIXELS; ++i) mask[i] = 0u;
    }
    g1_census_residual_compare(selected->shadow, (const BYTE *)(ULONG_PTR)source_buffer,
                               source_pitch, &residual, g_residual_mask);
    g1_census_index_top(residual.histogram, top);
    if (g_residual_map_log != INVALID_HANDLE_VALUE && header[0] == 0x50314731u) {
        DWORD map_header[8];
        for (i = 0; i < 8u; ++i) map_header[i] = header[i];
        map_header[6] = CENSUS_MAP_PIXELS;
        if (WriteFile(g_residual_map_log, map_header, sizeof(map_header), &written, NULL) &&
            written == sizeof(map_header))
            WriteFile(g_residual_map_log, g_residual_mask, CENSUS_MAP_PIXELS, &written, NULL);
    }
    length = wsprintfA(line,
        "{\"schema\":\"g1-writer-census-v1\",\"event\":\"residual_boundary\","
        "\"present\":%u,\"program_state\":%u,\"unhooked_pixels\":%u,"
        "\"unhooked_bbox\":[%d,%d,%d,%d],"
        "\"unhooked_index_top\":[[%u,%u],[%u,%u],[%u,%u],[%u,%u]],"
        "\"textout_calls\":%u,\"measurement_only\":1}\n",
        (unsigned)g_present_sequence, (unsigned)state, (unsigned)residual.pixels,
        residual.min_x, residual.min_y, residual.max_x, residual.max_y,
        (unsigned)top[0].index, (unsigned)top[0].count,
        (unsigned)top[1].index, (unsigned)top[1].count,
        (unsigned)top[2].index, (unsigned)top[2].count,
        (unsigned)top[3].index, (unsigned)top[3].count,
        (unsigned)g_textout_window_calls);
    g_textout_window_calls = 0u;
    if (length > 0) write_line(line, (DWORD)length);
}

static void emit_present_boundary(DWORD destination_width, DWORD destination_height,
                                  DWORD source_width, DWORD source_height,
                                  BOOL destination_is_primary, DWORD state, DWORD tick,
                                  DWORD source_surface, DWORD source_buffer,
                                  DWORD source_pitch, BOOL source_locked)
{
    CensusBuffer *selected;
    DWORD total = CENSUS_MAP_PIXELS;
    DWORD assigned = 0u;
    DWORD map_start = g_map_offset;
    DWORD context_map_start = g_context_map_offset;
    DWORD cache_transfer_calls;
    DWORD header[8];
    DWORD written;
    G1CensusIndexCount unknown_top[4];
    char line[2400];
    const char *binding = source_locked && source_buffer && source_pitch
        ? "locked_source" : "unbound";
    int length;
    if (!destination_is_primary || state != g_census_target_state ||
        g_present_count >= CENSUS_PRESENT_LIMIT) return;
    cache_transfer_calls = (DWORD)InterlockedExchange(
        &g_ps3_cache_transfer_window_calls, 0);
    if (g_skip_presents_seen < g_skip_presents) {
        /* Opt-in delayed window: hooks keep attributing writers, but nothing is
         * recorded.  The real PS3 ordinal still advances for stale-mask matching. */
        ++g_skip_presents_seen;
        ++g_present_sequence;
        if (g_skip_presents_seen == g_skip_presents) {
            char skip_line[200];
            int skip_length = wsprintfA(skip_line,
                "{\"schema\":\"g1-writer-census-v1\",\"event\":\"present_skip\","
                "\"skipped\":%u,\"next_present\":%u,\"measurement_only\":1}\n",
                (unsigned)g_skip_presents_seen, (unsigned)(g_present_sequence + 1u));
            if (skip_length > 0) write_line(skip_line, (DWORD)skip_length);
        }
        return;
    }
    ++g_present_count;
    ++g_present_sequence;
    header[0] = 0u;
    selected = source_locked ? present_source_buffer(source_buffer, source_pitch) : NULL;
    if (selected) assigned = selected->assigned_pixels;
    /* Direct unknown measurement: 8bpp index histogram of the pixels no writer
     * changed, read from the still-locked present source. */
    unknown_index_top(selected, source_buffer, source_pitch, unknown_top);
    if (g_map_log != INVALID_HANDLE_VALUE && selected) {
        header[0] = 0x50314731u; /* G1P1 */
        header[1] = g_present_sequence;
        header[2] = CENSUS_MAP_WIDTH;
        header[3] = CENSUS_MAP_HEIGHT;
        header[4] = selected->stride;
        header[5] = selected->buffer;
        header[6] = CENSUS_MAP_PIXELS;
        header[7] = state;
        if (WriteFile(g_map_log, header, sizeof(header), &written, NULL) &&
            written == sizeof(header) &&
            WriteFile(g_map_log, selected->map, CENSUS_MAP_PIXELS, &written, NULL) &&
            written == CENSUS_MAP_PIXELS)
            g_map_offset += sizeof(header) + CENSUS_MAP_PIXELS;
    }
    if (g_residual_enabled && selected && source_locked && selected->shadow) {
        emit_residual_boundary(selected, source_buffer, source_pitch, state, header);
        emit_blend_boundary();
    }
    if (g_context_map_log != INVALID_HANDLE_VALUE && selected) {
        if (WriteFile(g_context_map_log, header, sizeof(header), &written, NULL) &&
            written == sizeof(header) &&
            WriteFile(g_context_map_log, selected->context_map, CENSUS_MAP_PIXELS,
                      &written, NULL) && written == CENSUS_MAP_PIXELS)
            g_context_map_offset += sizeof(header) + CENSUS_MAP_PIXELS;
    }
    length = wsprintfA(line,
        "{\"schema\":\"g1-writer-census-v1\",\"event\":\"present_boundary\","
        "\"present\":%u,\"destination_width\":%u,\"destination_height\":%u,"
        "\"source_width\":%u,\"source_height\":%u,\"selected_buffer\":\"0x%08X\","
        "\"binding\":\"%s\",\"present_source_surface\":\"0x%08X\","
        "\"present_source_buffer\":\"0x%08X\",\"present_source_pitch\":%u,"
        "\"map_generation\":%u,\"map_generation_state\":%u,\"map_write_calls\":%u,"
        "\"map_offset\":%u,\"map_bytes\":%u,\"context_map_offset\":%u,"
        "\"context_map_bytes\":%u,\"assigned_pixels\":%u,"
        "\"unknown_pixels\":%u,\"unknown_index_top\":[[%u,%u],[%u,%u],[%u,%u],[%u,%u]],"
        "\"attribution_ratio\":%u,\"bbox\":[%d,%d,%d,%d],"
        "\"writer_pixels\":[%u,%u,%u,%u,%u,%u,%u,%u,%u,%u],"
        "\"terrain_cache_transfer_calls\":%u,\"program_state\":%u,"
        "\"census_state\":%u,\"game_tick\":%u,\"measurement_only\":1}\n",
        (unsigned)g_present_sequence, (unsigned)destination_width,
        (unsigned)destination_height, (unsigned)source_width, (unsigned)source_height,
        (unsigned)(selected ? selected->buffer : 0u), binding,
        (unsigned)(source_locked ? source_surface : 0u),
        (unsigned)(source_locked ? source_buffer : 0u),
        (unsigned)(source_locked ? source_pitch : 0u),
        (unsigned)(selected ? selected->generation : 0u),
        (unsigned)(selected ? selected->generation_state : 0xFFFFFFFFu),
        (unsigned)(selected ? selected->writer_calls[0] + selected->writer_calls[1] +
            selected->writer_calls[2] + selected->writer_calls[3] +
            selected->writer_calls[4] + selected->writer_calls[5] +
            selected->writer_calls[6] + selected->writer_calls[7] +
            selected->writer_calls[8] + selected->writer_calls[9] : 0u),
        (unsigned)map_start,
        (unsigned)(selected ? CENSUS_MAP_PIXELS : 0u), (unsigned)context_map_start,
        (unsigned)(selected ? CENSUS_MAP_PIXELS : 0u), (unsigned)assigned,
        (unsigned)(total - assigned),
        (unsigned)unknown_top[0].index, (unsigned)unknown_top[0].count,
        (unsigned)unknown_top[1].index, (unsigned)unknown_top[1].count,
        (unsigned)unknown_top[2].index, (unsigned)unknown_top[2].count,
        (unsigned)unknown_top[3].index, (unsigned)unknown_top[3].count,
        (unsigned)((assigned * 100u) / total),
        selected ? (int)selected->min_x : -1, selected ? (int)selected->min_y : -1,
        selected ? (int)selected->max_x : -1, selected ? (int)selected->max_y : -1,
        (unsigned)(selected ? selected->writer_pixels[0] : 0u),
        (unsigned)(selected ? selected->writer_pixels[1] : 0u),
        (unsigned)(selected ? selected->writer_pixels[2] : 0u),
        (unsigned)(selected ? selected->writer_pixels[3] : 0u),
        (unsigned)(selected ? selected->writer_pixels[4] : 0u),
        (unsigned)(selected ? selected->writer_pixels[5] : 0u),
        (unsigned)(selected ? selected->writer_pixels[6] : 0u),
        (unsigned)(selected ? selected->writer_pixels[7] : 0u),
        (unsigned)(selected ? selected->writer_pixels[8] : 0u),
        (unsigned)(selected ? selected->writer_pixels[9] : 0u),
        (unsigned)cache_transfer_calls,
        (unsigned)state, (unsigned)g_census_target_state, (unsigned)tick);
    if (length > 0) write_line(line, (DWORD)length);
    watch_on_present(selected != NULL && source_locked, source_buffer, source_pitch);
    /* The logical back buffer is reused between presents.  Preserve the map
     * so unchanged pixels retain their last writer; a present is a boundary
     * for aggregation, not evidence that the renderer cleared the buffer. */
}

void g1_census_present_boundary(DWORD destination_width, DWORD destination_height,
                                DWORD source_width, DWORD source_height,
                                BOOL destination_is_primary, DWORD state, DWORD tick,
                                DWORD source_surface, DWORD source_buffer,
                                DWORD source_pitch, BOOL source_locked)
{
    if (!g1_census_enabled() || g_log == INVALID_HANDLE_VALUE) return;
    /* H-S2w: g_present_count stops at CENSUS_PRESENT_LIMIT, so an armed watch counts
     * target-state primary presents itself and (opt-in N) ends after N of them. */
    if (g_watch_armed && destination_is_primary && state == g_census_target_state) {
        ++g_watch_present_ticks;
        if (g_watch_presents && g_watch_present_ticks >= g_watch_presents)
            watch_finish("watch_window_end");
    }
    emit_present_boundary(destination_width, destination_height, source_width,
                          source_height, destination_is_primary, state, tick,
                          source_surface, source_buffer, source_pitch,
                          source_locked);
}

void g1_census_record_surface_buffer(DWORD surface, DWORD buffer, DWORD pitch,
                                    DWORD width, DWORD height)
{
    DWORD i;
    if (!g1_census_enabled() || g_log == INVALID_HANDLE_VALUE ||
        census_program_state() != g_census_target_state || g_present_count >= CENSUS_PRESENT_LIMIT ||
        !surface || !buffer || !pitch || !width || !height) return;
    for (i = 0; i < CENSUS_SURFACE_LIMIT; ++i) {
        CensusSurface *known = &g_surfaces[i];
        char line[500];
        int length;
        if (known->used && known->surface != surface) continue;
        if (known->used && known->buffer == buffer && known->pitch == pitch &&
            known->width == width && known->height == height) return;
        if (!known->used) known->used = TRUE;
        known->surface = surface;
        known->buffer = buffer;
        known->pitch = pitch;
        known->width = width;
        known->height = height;
        length = wsprintfA(line,
            "{\"schema\":\"g1-writer-census-v1\",\"event\":\"surface_buffer\","
            "\"surface\":\"0x%08X\",\"buffer\":\"0x%08X\","
            "\"pitch\":%u,\"width\":%u,\"height\":%u,\"program_state\":%u,"
            "\"measurement_only\":1}\n",
            (unsigned)surface, (unsigned)buffer, (unsigned)pitch,
            (unsigned)width, (unsigned)height, (unsigned)g_census_target_state);
        if (length > 0) write_line(line, (DWORD)length);
        return;
    }
}

void g1_census_surface_blt_attempt(DWORD destination_width, DWORD destination_height)
{
    if (g1_census_enabled() && g_log != INVALID_HANDLE_VALUE &&
        census_program_state() == g_census_target_state && g_present_count < CENSUS_PRESENT_LIMIT) {
        if (g_residual_enabled &&
            (destination_width < CENSUS_MAP_WIDTH || destination_height < CENSUS_MAP_HEIGHT)) {
            g1_census_surface_blt_skipped(7u);
            return;
        }
        ++g_surface_blt_attempts;
    }
}

void g1_census_surface_blt_skipped(DWORD reason)
{
    if (g_residual_enabled && reason < 8u) ++g_surface_blt_skip[reason];
}

BOOL g1_census_surface_blt_begin(DWORD buffer, DWORD pitch, DWORD height,
                                 DWORD left, DWORD top, DWORD right, DWORD bottom,
                                 const BYTE *pixels)
{
    DWORD row, width, rect_height;
    CensusBuffer *context;
    g_surface_blt_context = NULL;
    if (!g1_census_enabled() || g_log == INVALID_HANDLE_VALUE ||
        census_program_state() != g_census_target_state || g_present_count >= CENSUS_PRESENT_LIMIT) {
        g1_census_surface_blt_skipped(4u);
        return FALSE;
    }
    if (!buffer || pitch < CENSUS_MAP_WIDTH || !pixels || right <= left ||
        bottom <= top || right > CENSUS_MAP_WIDTH || bottom > CENSUS_MAP_HEIGHT ||
        bottom > height) {
        g1_census_surface_blt_skipped(5u);
        if (g_residual_enabled && g_surface_blt_skip[5] <= 8u) {
            char line[300];
            int length = wsprintfA(line,
                "{\"schema\":\"g1-writer-census-v1\",\"event\":\"surface_blt_rect_sample\","
                "\"buffer\":\"0x%08X\",\"pitch\":%u,\"height\":%u,\"rect\":[%u,%u,%u,%u],"
                "\"measurement_only\":1}\n",
                (unsigned)buffer, (unsigned)pitch, (unsigned)height,
                (unsigned)left, (unsigned)top, (unsigned)right, (unsigned)bottom);
            if (length > 0) write_line(line, (DWORD)length);
        }
        return FALSE;
    }
    width = right - left;
    rect_height = bottom - top;
    if (width * rect_height > CENSUS_MAP_PIXELS ||
        !readable_range(pixels, height * pitch)) {
        g1_census_surface_blt_skipped(6u);
        return FALSE;
    }
    context = buffer_context(buffer, pitch, height);
    if (!context) {
        ++g_buffer_context_dropped;
        return FALSE;
    }
    for (row = 0; row < rect_height; ++row) {
        census_copy_bytes(g_surface_before + row * width,
                          pixels + (top + row) * pitch + left, width);
    }
    g_surface_blt_context = context;
    g_surface_blt_buffer = buffer;
    g_surface_blt_pitch = pitch;
    g_surface_blt_height = height;
    g_surface_blt_left = left;
    g_surface_blt_top = top;
    g_surface_blt_width = width;
    g_surface_blt_height_rect = rect_height;
    return TRUE;
}

void g1_census_surface_blt_end(DWORD buffer, DWORD pitch, DWORD height,
                               DWORD left, DWORD top, DWORD right, DWORD bottom,
                               const BYTE *pixels)
{
    DWORD row, col;
    BOOL changed = FALSE;
    CensusBuffer *context = g_surface_blt_context;
    if (!context) return;
    g_surface_blt_context = NULL;
    if (buffer != g_surface_blt_buffer || pitch != g_surface_blt_pitch ||
        height != g_surface_blt_height || left != g_surface_blt_left ||
        top != g_surface_blt_top || right - left != g_surface_blt_width ||
        bottom - top != g_surface_blt_height_rect || !pixels ||
        !readable_range(pixels, height * pitch)) return;
    for (row = 0; row < g_surface_blt_height_rect; ++row) {
        for (col = 0; col < g_surface_blt_width; ++col) {
            DWORD local = row * g_surface_blt_width + col;
            DWORD map_index = (top + row) * CENSUS_MAP_WIDTH + left + col;
            BYTE after = pixels[(top + row) * pitch + left + col];
            BYTE previous;
            if (g_surface_before[local] == after) continue;
            changed = TRUE;
            previous = context->map[map_index];
            if (previous == CENSUS_WRITER_COUNT) continue;
            if (previous > 0u && previous <= CENSUS_WRITER_COUNT &&
                context->writer_pixels[previous - 1u] > 0u)
                --context->writer_pixels[previous - 1u];
            if (previous == 0u) ++context->assigned_pixels;
            context->map[map_index] = CENSUS_WRITER_COUNT;
            context->context_map[map_index] = 0u;
            ++context->writer_pixels[CENSUS_WRITER_COUNT - 1u];
            ++context->changed_pixels;
            if (left + col < context->min_x) context->min_x = left + col;
            if (top + row < context->min_y) context->min_y = top + row;
            if (left + col > context->max_x) context->max_x = left + col;
            if (top + row > context->max_y) context->max_y = top + row;
        }
    }
    if (changed) ++context->writer_calls[CENSUS_WRITER_COUNT - 1u];
    residual_sync_context(context, g_surface_blt_left, g_surface_blt_top,
                          g_surface_blt_width, g_surface_blt_height_rect);
    /* Count only a capture whose post-Blt compare ran to completion. */
    ++g_surface_blt_captured;
}

static BOOL bytes_equal(const BYTE *address, const BYTE *expected, DWORD length)
{
    DWORD i;
    for (i = 0; i < length; ++i) if (address[i] != expected[i]) return FALSE;
    return TRUE;
}

static BOOL install_one(CensusTarget *target)
{
    BYTE *address;
    BYTE *trampoline;
    DWORD old_protect, restored, relative;
    DWORD i;
    if (!target) return FALSE;
    address = (BYTE *)(ULONG_PTR)target->address;
    if (!bytes_equal(address, target->expected, target->length)) return FALSE;
    trampoline = (BYTE *)VirtualAlloc(NULL, target->length + 5u,
                                      MEM_COMMIT | MEM_RESERVE,
                                      PAGE_EXECUTE_READWRITE);
    if (!trampoline) return FALSE;
    for (i = 0; i < target->length; ++i) trampoline[i] = address[i];
    trampoline[target->length] = 0xE9;
    *(DWORD *)(trampoline + target->length + 1u) =
        (target->address + target->length) -
        ((DWORD)(ULONG_PTR)trampoline + target->length + 5u);
    if (!VirtualProtect(address, target->length, PAGE_EXECUTE_READWRITE,
                        &old_protect)) {
        VirtualFree(trampoline, 0, MEM_RELEASE);
        return FALSE;
    }
    address[0] = 0xE9;
    relative = (DWORD)(ULONG_PTR)target->wrapper - (target->address + 5u);
    *(DWORD *)(address + 1u) = relative;
    for (i = 5u; i < target->length; ++i) address[i] = 0x90;
    VirtualProtect(address, target->length, old_protect, &restored);
    FlushInstructionCache(GetCurrentProcess(), address, target->length);
    target->trampoline = trampoline;
    target->installed = TRUE;
    target->install_ok = 1u;
    return TRUE;
}

static BOOL restore_one(CensusTarget *target)
{
    BYTE *address;
    DWORD old_protect, restored, i;
    if (!target || !target->installed) return TRUE;
    address = (BYTE *)(ULONG_PTR)target->address;
    if (!VirtualProtect(address, target->length, PAGE_EXECUTE_READWRITE,
                        &old_protect)) return FALSE;
    for (i = 0; i < target->length; ++i) address[i] = target->expected[i];
    VirtualProtect(address, target->length, old_protect, &restored);
    FlushInstructionCache(GetCurrentProcess(), address, target->length);
    target->installed = FALSE;
    if (target->trampoline) VirtualFree(target->trampoline, 0, MEM_RELEASE);
    target->trampoline = NULL;
    return bytes_equal(address, target->expected, target->length);
}

static CensusTarget g_targets[CENSUS_TARGET_COUNT] = {
    {"rle_clip", 0x00466D50u, 7u, {0x83,0xEC,0x14,0x8B,0x54,0x24,0x1C}, 5u, NULL, NULL, 0,0,0,0,FALSE},
    {"rle_plain", 0x004664D0u, 8u, {0x55,0x56,0x8B,0x74,0x24,0x10,0x8B,0xE9}, 5u, NULL, NULL, 0,0,0,0,FALSE},
    {"rect_fill", 0x00465E80u, 9u, {0x8B,0x41,0x10,0x53,0x55,0x8B,0x6C,0x24,0x0C}, 5u, NULL, NULL, 0,0,0,0,FALSE},
    {"block_copy", 0x00466280u, 8u, {0x8B,0x41,0x0C,0x53,0x99,0x83,0xE2,0x07}, 5u, NULL, NULL, 0,0,0,0,FALSE},
    {"rect_border", 0x00465B30u, 8u, {0x83,0xEC,0x10,0x53,0x8B,0x5C,0x24,0x18}, 5u, NULL, NULL, 0,0,0,0,FALSE},
    {"rle_tinted_clip", 0x00466540u, 8u, {0x51,0x53,0x56,0x57,0x8B,0x7C,0x24,0x18}, 6u, NULL, NULL, 0,0,0,0,FALSE},
    {"rle_tinted", 0x00466EA0u, 7u, {0x83,0xEC,0x14,0x8B,0x44,0x24,0x1C}, 6u, NULL, NULL, 0,0,0,0,FALSE},
    {"set_pixel", 0x004658E0u, 9u, {0x8B,0x41,0x10,0x8B,0x91,0x14,0x15,0x00,0x00}, 3u, NULL, NULL, 0,0,0,0,FALSE},
};

/* 0x403B20 is a context boundary, not a pixel writer.  Its detour only
 * brackets the original call so nested primitive writes can carry the
 * terrain provenance without changing the renderer arguments or result. */
static CensusTarget g_terrain_target = {
    "terrain_context", 0x00403B20u, 7u,
    {0x53,0x66,0x8B,0x5C,0x24,0x1C,0x56}, 7u,
    NULL, NULL, 0,0,0,0,FALSE
};

static DWORD target_result(CensusTarget *target, void *renderer,
                           DWORD a, DWORD b, DWORD c, DWORD d, DWORD e, DWORD f)
{
    if (target->arity == 3u)
        return ((CensusFn3)(ULONG_PTR)target->trampoline)(renderer, a, b, c);
    if (target->arity == 5u)
        return ((CensusFn5)(ULONG_PTR)target->trampoline)(renderer, a, b, c, d, e);
    if (target->arity == 7u)
        return ((CensusFn7)(ULONG_PTR)target->trampoline)(renderer, a, b, c, d, e, f, 0u);
    return ((CensusFn6)(ULONG_PTR)target->trampoline)(renderer, a, b, c, d, e, f);
}

static DWORD __attribute__((thiscall)) census_terrain_context(
    void *renderer, DWORD a, DWORD b, DWORD c, DWORD d, DWORD e, DWORD f, DWORD g)
{
    DWORD result;
    ++g_terrain_calls;
    emit_terrain_context_call(renderer, a, b, c, d, e, f, g);
    InterlockedIncrement(&g_terrain_depth);
    result = ((CensusFn7)(ULONG_PTR)g_terrain_target.trampoline)(
        renderer, a, b, c, d, e, f, g);
    InterlockedDecrement(&g_terrain_depth);
    return result;
}

static DWORD call_target(CensusTarget *target, void *renderer,
                         DWORD a, DWORD b, DWORD c, DWORD d, DWORD e, DWORD f)
{
    DWORD result;
    DWORD buffer = 0u, stride = 0u, renderer_height = 0u;
    DWORD x = 0u, y = 0u, width = 0u, height = 0u;
    DWORD writer_id;
    CensusBuffer *context = NULL;
    BOOL snapshot = FALSE;
    ++target->call_count;
    if (census_program_state() == g_census_target_state) ++target->calls_ps3;
    if (target->address == 0x00466280u && e == 0x00BA3D30u) {
        InterlockedIncrement(&g_cache_transfer_calls);
        if (census_program_state() == g_census_target_state) {
            InterlockedIncrement(&g_ps3_cache_transfer_calls);
            InterlockedIncrement(&g_ps3_cache_transfer_window_calls);
        }
    }
    if (InterlockedExchange(&g_guard, 1) != 0) {
        result = target_result(target, renderer, a, b, c, d, e, f);
        InterlockedExchange(&g_guard, 0);
        return result;
    }
    if (renderer_buffer(renderer, &buffer, &stride, &renderer_height)) {
        context = buffer_context(buffer, stride, renderer_height);
        if (!context) ++g_buffer_context_dropped;
        if (context && !call_bbox(target, a, b, c, d, stride, renderer_height,
                                  &x, &y, &width, &height)) {
            x = 0u; y = 0u; width = CENSUS_MAP_WIDTH; height = CENSUS_MAP_HEIGHT;
        }
        if (context) snapshot = snapshot_before(context, x, y, width, height);
    }
    result = target_result(target, renderer, a, b, c, d, e, f);
    if (snapshot) {
        /* 0x466280 normally denotes a block copy.  When its source is the
         * pinned terrain cache, keep that transfer distinct in the
         * last-writer map so it cannot be double-counted as a terrain
         * blitter's source writes. */
        writer_id = target->address == 0x00466280u && e == 0x00BA3D30u
            ? CENSUS_WRITER_COUNT - 1u : target_index(target) + 1u;
        if (writer_id > 0u && writer_id <= CENSUS_WRITER_COUNT)
            ++context->writer_calls[writer_id - 1u];
        map_changes(context, writer_id, x, y, width, height,
                    target->address == 0x00466280u || target->address == 0x00465E80u);
        residual_sync_context(context, x, y, width, height);
        probe_destination_read(target, context, renderer, a, b, c, d, e, f,
                               x, y, width, height);
    }
    emit_call(target, renderer, a, b, c, d, e, f, result);
    InterlockedExchange(&g_guard, 0);
    return result;
}

static DWORD __attribute__((thiscall)) census_rle_clip(void *r, DWORD a,DWORD b,DWORD c,DWORD d,DWORD e)
{ return call_target(&g_targets[0],r,a,b,c,d,e,0u); }
static DWORD __attribute__((thiscall)) census_rle_plain(void *r, DWORD a,DWORD b,DWORD c,DWORD d,DWORD e)
{ return call_target(&g_targets[1],r,a,b,c,d,e,0u); }
static DWORD __attribute__((thiscall)) census_rect_fill(void *r, DWORD a,DWORD b,DWORD c,DWORD d,DWORD e)
{ return call_target(&g_targets[2],r,a,b,c,d,e,0u); }
static DWORD __attribute__((thiscall)) census_block_copy(void *r, DWORD a,DWORD b,DWORD c,DWORD d,DWORD e)
{ return call_target(&g_targets[3],r,a,b,c,d,e,0u); }
static DWORD __attribute__((thiscall)) census_rect_border(void *r, DWORD a,DWORD b,DWORD c,DWORD d,DWORD e)
{ return call_target(&g_targets[4],r,a,b,c,d,e,0u); }
static DWORD __attribute__((thiscall)) census_rle_tinted_clip(void *r, DWORD a,DWORD b,DWORD c,DWORD d,DWORD e,DWORD f)
{ return call_target(&g_targets[5],r,a,b,c,d,e,f); }
static DWORD __attribute__((thiscall)) census_rle_tinted(void *r, DWORD a,DWORD b,DWORD c,DWORD d,DWORD e,DWORD f)
{ return call_target(&g_targets[6],r,a,b,c,d,e,f); }
static DWORD __attribute__((thiscall)) census_set_pixel(void *r, DWORD a,DWORD b,DWORD c)
{ return call_target(&g_targets[7],r,a,b,c,0u,0u,0u); }

static void emit_summary(CensusTarget *target)
{
    char line[760];
    int length;
    if (!target) return;
    length = wsprintfA(line,
        "{\"schema\":\"g1-writer-census-v1\",\"event\":\"summary\","
        "\"writer\":\"%s\",\"target\":\"0x%08X\",\"arity\":%u,"
        "\"installed\":%u,\"calls\":%u,\"calls_ps3\":%u,\"samples\":%u,"
        "\"dest_read\":\"unknown\",\"dest_probe\":%u,\"measurement_only\":1}\n",
        target->name, (unsigned)target->address, (unsigned)target->arity,
        (unsigned)target->install_ok, (unsigned)target->call_count,
        (unsigned)target->calls_ps3, (unsigned)target->sample_count,
        (unsigned)g_dest_probe_status[target_index(target)]);
    if (length > 0) write_line(line, (DWORD)length);
}

static void emit_buffer_summaries(void)
{
    DWORD i;
    for (i = 0; i < CENSUS_MAX_BUFFERS; ++i) {
        CensusBuffer *buffer = &g_buffers[i];
        char line[900];
        int length;
        if (!buffer->used) continue;
        length = wsprintfA(line,
            "{\"schema\":\"g1-writer-census-v1\",\"event\":\"buffer_summary\","
            "\"buffer\":\"0x%08X\",\"stride\":%u,\"generation\":%u,"
            "\"generation_state\":%u,\"assigned_pixels\":%u,"
            "\"writer_pixels\":[%u,%u,%u,%u,%u,%u,%u,%u,%u,%u],"
            "\"bbox\":[%d,%d,%d,%d],\"writer_calls\":[%u,%u,%u,%u,%u,%u,%u,%u,%u,%u],"
            "\"measurement_only\":1}\n",
            (unsigned)buffer->buffer, (unsigned)buffer->stride,
            (unsigned)buffer->generation, (unsigned)buffer->generation_state,
            (unsigned)buffer->assigned_pixels,
            (unsigned)buffer->writer_pixels[0], (unsigned)buffer->writer_pixels[1],
            (unsigned)buffer->writer_pixels[2], (unsigned)buffer->writer_pixels[3],
            (unsigned)buffer->writer_pixels[4], (unsigned)buffer->writer_pixels[5],
            (unsigned)buffer->writer_pixels[6], (unsigned)buffer->writer_pixels[7],
            (unsigned)buffer->writer_pixels[8], (unsigned)buffer->writer_pixels[9],
            buffer->assigned_pixels ? (int)buffer->min_x : -1,
            buffer->assigned_pixels ? (int)buffer->min_y : -1,
            buffer->assigned_pixels ? (int)buffer->max_x : -1,
            buffer->assigned_pixels ? (int)buffer->max_y : -1,
            (unsigned)buffer->writer_calls[0], (unsigned)buffer->writer_calls[1],
            (unsigned)buffer->writer_calls[2], (unsigned)buffer->writer_calls[3],
            (unsigned)buffer->writer_calls[4], (unsigned)buffer->writer_calls[5],
            (unsigned)buffer->writer_calls[6], (unsigned)buffer->writer_calls[7],
            (unsigned)buffer->writer_calls[8], (unsigned)buffer->writer_calls[9]);
        if (length > 0) write_line(line, (DWORD)length);
    }
    {
        char line[220];
        int length = wsprintfA(line,
            "{\"schema\":\"g1-writer-census-v1\",\"event\":\"buffer_context_summary\","
            "\"buffer_context_dropped\":%u,\"measurement_only\":1}\n",
            (unsigned)g_buffer_context_dropped);
        if (length > 0) write_line(line, (DWORD)length);
    }
    {
        char line[260];
        int length = wsprintfA(line,
            "{\"schema\":\"g1-writer-census-v1\",\"event\":\"surface_blt_summary\","
            "\"writer\":\"dd_surface_blt\",\"calls_ps3\":%u,"
            "\"captured\":%u,\"capture_missed\":%u,\"measurement_only\":1}\n",
            (unsigned)g_surface_blt_attempts, (unsigned)g_surface_blt_captured,
            (unsigned)(g_surface_blt_attempts - g_surface_blt_captured));
        if (length > 0) write_line(line, (DWORD)length);
        if (g_residual_enabled) {
            length = wsprintfA(line,
                "{\"schema\":\"g1-writer-census-v1\",\"event\":\"surface_blt_skip_reasons\","
                "\"blt_rect_invalid\":%u,\"bltfast_skipped\":%u,\"blt_lock_failed\":%u,"
                "\"begin_gate\":%u,\"begin_rect\":%u,\"begin_unreadable\":%u,"
                "\"non_screen_surface_blt\":%u,\"measurement_only\":1}\n",
                (unsigned)g_surface_blt_skip[1], (unsigned)g_surface_blt_skip[2],
                (unsigned)g_surface_blt_skip[3], (unsigned)g_surface_blt_skip[4],
                (unsigned)g_surface_blt_skip[5], (unsigned)g_surface_blt_skip[6],
                (unsigned)g_surface_blt_skip[7]);
            if (length > 0) write_line(line, (DWORD)length);
        }
    }
}

static void emit_writer_table(void)
{
    static const char *names[CENSUS_WRITER_COUNT] = {
        "rle_clip", "rle_plain", "rect_fill", "block_copy",
        "rect_border", "rle_tinted_clip", "rle_tinted", "set_pixel",
        "terrain_cache_transfer", "dd_surface_blt"
    };
    DWORD i;
    for (i = 0; i < CENSUS_WRITER_COUNT; ++i) {
        char line[240];
        int length = wsprintfA(line,
            "{\"schema\":\"g1-writer-census-v1\",\"event\":\"writer_category\","
            "\"id\":%u,\"writer\":\"%s\",\"area_scope\":\"PS3_last_writer_map\","
            "\"measurement_only\":1}\n",
            (unsigned)(i + 1u), names[i]);
        if (length > 0) write_line(line, (DWORD)length);
    }
}

static void emit_cache_transfer_summary(void)
{
    char line[300];
    int length = wsprintfA(line,
        "{\"schema\":\"g1-writer-census-v1\",\"event\":\"terrain_cache_transfer_summary\","
        "\"target\":\"0x00466280\",\"source\":\"0x00BA3D30\","
        "\"calls_all_states\":%u,\"calls_ps3\":%u,\"measurement_only\":1}\n",
        (unsigned)InterlockedCompareExchange(&g_cache_transfer_calls, 0, 0),
        (unsigned)InterlockedCompareExchange(&g_ps3_cache_transfer_calls, 0, 0));
    if (length > 0) write_line(line, (DWORD)length);
}

static void emit_terrain_summary(void)
{
    char line[420];
    int length = wsprintfA(line,
        "{\"schema\":\"g1-writer-census-v1\",\"event\":\"context_summary\","
        "\"context\":\"terrain_0x403B20\",\"installed\":%u,\"calls\":%u,"
        "\"measurement_only\":1}\n",
        (unsigned)g_terrain_target.install_ok, (unsigned)g_terrain_calls);
    if (length > 0) write_line(line, (DWORD)length);
}

/* Opt-in GDI attribution: the game calls TextOutA through IAT slot 0x4E502C.
 * The detour calls the real function first, then records where it drew so the
 * coordinates can be compared with the unhooked-pixel mask.  The EXE file is
 * never touched; the slot is restored at detach. */
static BOOL WINAPI census_textout(HDC hdc, int x, int y, LPCSTR text, int length)
{
    BOOL result = g_real_textout(hdc, x, y, text, length);
    if (g_residual_enabled && census_program_state() == g_census_target_state &&
        g_present_count < CENSUS_PRESENT_LIMIT) {
        ++g_textout_calls;
        ++g_textout_window_calls;
        if (g_textout_samples < CENSUS_TEXTOUT_SAMPLE_LIMIT) {
            SIZE extent;
            char sample[17];
            char line[420];
            int n, i;
            extent.cx = 0;
            extent.cy = 0;
            ++g_textout_samples;
            if (g_text_extent && text && length > 0) g_text_extent(hdc, text, length, &extent);
            n = text && length > 0 ? (length < 16 ? length : 16) : 0;
            for (i = 0; i < n; ++i)
                sample[i] = (text[i] >= 0x20 && text[i] < 0x7F && text[i] != '"' &&
                             text[i] != '\\') ? text[i] : '.';
            sample[n] = 0;
            n = wsprintfA(line,
                "{\"schema\":\"g1-writer-census-v1\",\"event\":\"textout_call\","
                "\"seq\":%u,\"present\":%u,\"hdc\":\"0x%08X\",\"x\":%d,\"y\":%d,"
                "\"length\":%d,\"extent\":[%d,%d],\"text_ascii\":\"%s\","
                "\"measurement_only\":1}\n",
                (unsigned)g_textout_calls, (unsigned)(g_present_sequence + 1u),
                (unsigned)(ULONG_PTR)hdc, x, y, length, (int)extent.cx, (int)extent.cy, sample);
            if (n > 0) write_line(line, (DWORD)n);
        }
    }
    return result;
}

static void install_textout_slot(void)
{
    DWORD *slot = (DWORD *)(ULONG_PTR)CENSUS_TEXTOUT_SLOT;
    HMODULE gdi = GetModuleHandleA("gdi32.dll");
    FARPROC real = gdi ? GetProcAddress(gdi, "TextOutA") : NULL;
    DWORD old_protect, restored;
    BOOL ok = FALSE;
    char line[320];
    int length;
    if (real && readable_range(slot, sizeof(DWORD)) && *slot == (DWORD)(ULONG_PTR)real &&
        VirtualProtect(slot, sizeof(DWORD), PAGE_READWRITE, &old_protect)) {
        g_real_textout = (CensusTextOutA)(ULONG_PTR)real;
        g_text_extent = (CensusTextExtentA)(ULONG_PTR)GetProcAddress(gdi, "GetTextExtentPoint32A");
        *slot = (DWORD)(ULONG_PTR)census_textout;
        VirtualProtect(slot, sizeof(DWORD), old_protect, &restored);
        g_textout_installed = TRUE;
        ok = TRUE;
    }
    length = wsprintfA(line,
        "{\"schema\":\"g1-writer-census-v1\",\"event\":\"textout_iat\","
        "\"slot\":\"0x%08X\",\"status\":\"%s\",\"gdi32_textouta\":\"0x%08X\","
        "\"slot_value\":\"0x%08X\",\"measurement_only\":1}\n",
        (unsigned)CENSUS_TEXTOUT_SLOT, ok ? "active" : "skipped_slot_mismatch",
        (unsigned)(ULONG_PTR)real,
        readable_range(slot, sizeof(DWORD)) ? (unsigned)*slot : 0u);
    if (length > 0) write_line(line, (DWORD)length);
}

static void restore_textout_slot(void)
{
    DWORD *slot = (DWORD *)(ULONG_PTR)CENSUS_TEXTOUT_SLOT;
    DWORD old_protect, restored;
    char line[260];
    int length;
    BOOL restored_ok = FALSE;
    if (!g_textout_installed) return;
    if (*slot == (DWORD)(ULONG_PTR)census_textout &&
        VirtualProtect(slot, sizeof(DWORD), PAGE_READWRITE, &old_protect)) {
        *slot = (DWORD)(ULONG_PTR)g_real_textout;
        VirtualProtect(slot, sizeof(DWORD), old_protect, &restored);
        restored_ok = *slot == (DWORD)(ULONG_PTR)g_real_textout;
    }
    g_textout_installed = FALSE;
    length = wsprintfA(line,
        "{\"schema\":\"g1-writer-census-v1\",\"event\":\"textout_summary\","
        "\"calls_in_state\":%u,\"samples\":%u,\"slot_restored\":%u,"
        "\"measurement_only\":1}\n",
        (unsigned)g_textout_calls, (unsigned)g_textout_samples, (unsigned)restored_ok);
    if (length > 0) write_line(line, (DWORD)length);
}

/* Opt-in (residual mode): the watchpoint caught two unhooked translucent RLE
 * writers drawing present pixels: 0x4672E0 (the logo, pixel 782,380) and 0x467580
 * (the opening effect, pixel 223,279).  Both are thiscall(x, y, width, height,
 * RLE data) and mix the destination pixel through the renderer's colour tables.
 * Measurement only: the original runs unchanged; the shadow is synced afterwards,
 * so what a writer drew leaves the unhooked residual. */
static CensusTarget g_blend_targets[CENSUS_BLEND_COUNT] = {
    {"rle_blend_4672E0", 0x004672E0u, 6u, {0x51,0x53,0x56,0x8B,0xF1,0x57}, 5u, NULL, NULL, 0,0,0,0,FALSE},
    {"rle_blend_467580", 0x00467580u, 6u, {0x51,0x0F,0xBF,0x54,0x24,0x0C}, 5u, NULL, NULL, 0,0,0,0,FALSE},
};

static DWORD call_blend(DWORD index, void *renderer, DWORD a, DWORD b, DWORD c, DWORD d, DWORD e)
{
    CensusTarget *target = &g_blend_targets[index];
    DWORD result;
    DWORD buffer = 0u, stride = 0u, renderer_height = 0u;
    DWORD x = 0u, y = 0u, width = 0u, height = 0u;
    DWORD row, col, changed = 0u;
    CensusBuffer *context = NULL;
    BOOL snapshot = FALSE;
    BOOL in_window = census_program_state() == g_census_target_state &&
                     g_present_count < CENSUS_PRESENT_LIMIT;
    ++target->call_count;
    if (in_window) ++target->calls_ps3;
    if (InterlockedExchange(&g_guard, 1) != 0)
        return target_result(target, renderer, a, b, c, d, e, 0u);
    if (renderer_buffer(renderer, &buffer, &stride, &renderer_height)) {
        context = buffer_context(buffer, stride, renderer_height);
        /* the functions read x, y, width, height as 16-bit words; the caller's
         * upper halves are not zero (lap953 sample: width 589924 = 0x90064) */
        if (context && !call_bbox(target, (DWORD)(int)(short)a, (DWORD)(int)(short)b,
                                  (DWORD)(int)(short)c, (DWORD)(int)(short)d,
                                  stride, renderer_height, &x, &y, &width, &height)) {
            x = 0u; y = 0u; width = CENSUS_MAP_WIDTH; height = CENSUS_MAP_HEIGHT;
        }
        if (context) snapshot = snapshot_before(context, x, y, width, height);
    }
    result = target_result(target, renderer, a, b, c, d, e, 0u);
    if (snapshot) {
        const BYTE *pixels = (const BYTE *)(ULONG_PTR)context->buffer;
        for (row = 0u; row < height; ++row)
            for (col = 0u; col < width; ++col)
                if (g_before[row * width + col] != pixels[(y + row) * context->stride + x + col])
                    ++changed;
        residual_sync_context(context, x, y, width, height);
    }
    if (in_window) {
        if (g_blend_window_any == 0u) {
            g_blend_min_x = x; g_blend_min_y = y;
            g_blend_max_x = x + width; g_blend_max_y = y + height;
        } else {
            if (x < g_blend_min_x) g_blend_min_x = x;
            if (y < g_blend_min_y) g_blend_min_y = y;
            if (x + width > g_blend_max_x) g_blend_max_x = x + width;
            if (y + height > g_blend_max_y) g_blend_max_y = y + height;
        }
        ++g_blend_window_any;
        ++g_blend_window_calls[index];
        g_blend_window_changed[index] += changed;
        g_blend_total_changed[index] += changed;
        if (g_blend_samples < CENSUS_BLEND_SAMPLE_LIMIT) {
            char line[400];
            int length;
            ++g_blend_samples;
            length = wsprintfA(line,
                "{\"schema\":\"g1-writer-census-v1\",\"event\":\"blend_call\","
                "\"seq\":%u,\"writer\":\"%s\",\"present\":%u,"
                "\"args\":[%d,%d,%d,%d,\"0x%08X\"],"
                "\"bbox\":[%u,%u,%u,%u],\"changed\":%u,\"snapshot\":%u,"
                "\"measurement_only\":1}\n",
                (unsigned)g_blend_samples, target->name, (unsigned)(g_present_sequence + 1u),
                (int)a, (int)b, (int)c, (int)d, (unsigned)e,
                (unsigned)x, (unsigned)y, (unsigned)width, (unsigned)height,
                (unsigned)changed, (unsigned)snapshot);
            if (length > 0) write_line(line, (DWORD)length);
        }
    }
    InterlockedExchange(&g_guard, 0);
    return result;
}

static DWORD __attribute__((thiscall)) census_rle_blend_0(void *r, DWORD a,DWORD b,DWORD c,DWORD d,DWORD e)
{ return call_blend(0u,r,a,b,c,d,e); }
static DWORD __attribute__((thiscall)) census_rle_blend_1(void *r, DWORD a,DWORD b,DWORD c,DWORD d,DWORD e)
{ return call_blend(1u,r,a,b,c,d,e); }

static BOOL install_blend_targets(void)
{
    CensusWrapper wrappers[CENSUS_BLEND_COUNT] = {
        (CensusWrapper)census_rle_blend_0, (CensusWrapper)census_rle_blend_1};
    DWORD i;
    for (i = 0u; i < CENSUS_BLEND_COUNT; ++i) {
        CensusTarget *target = &g_blend_targets[i];
        char line[420];
        int length;
        BOOL ok;
        target->wrapper = wrappers[i];
        ok = install_one(target);
        length = wsprintfA(line,
            "{\"schema\":\"g1-writer-census-v1\",\"event\":\"blend_install\","
            "\"writer\":\"%s\",\"target\":\"0x%08X\",\"arity\":%u,\"prologue_len\":%u,"
            "\"old_bytes_fnv1a32\":\"0x%08X\",\"status\":\"%s\",\"measurement_only\":1}\n",
            target->name, (unsigned)target->address, (unsigned)target->arity,
            (unsigned)target->length, (unsigned)fnv1a(target->expected, target->length),
            ok ? "active" : "skipped_old_bytes_mismatch");
        if (length > 0) write_line(line, (DWORD)length);
        if (!ok) return FALSE;
    }
    return TRUE;
}

/* One line per present window: each blend writer's calls and changed pixels, plus the bbox union. */
static void emit_blend_boundary(void)
{
    char line[360];
    int length = wsprintfA(line,
        "{\"schema\":\"g1-writer-census-v1\",\"event\":\"blend_boundary\","
        "\"present\":%u,\"calls\":[%u,%u],\"changed_pixels\":[%u,%u],"
        "\"bbox\":[%u,%u,%u,%u],\"measurement_only\":1}\n",
        (unsigned)g_present_sequence,
        (unsigned)g_blend_window_calls[0], (unsigned)g_blend_window_calls[1],
        (unsigned)g_blend_window_changed[0], (unsigned)g_blend_window_changed[1],
        (unsigned)g_blend_min_x, (unsigned)g_blend_min_y,
        (unsigned)g_blend_max_x, (unsigned)g_blend_max_y);
    g_blend_window_any = 0u;
    g_blend_window_calls[0] = g_blend_window_calls[1] = 0u;
    g_blend_window_changed[0] = g_blend_window_changed[1] = 0u;
    if (length > 0) write_line(line, (DWORD)length);
}

static void blend_finish(void)
{
    DWORD i;
    for (i = 0u; i < CENSUS_BLEND_COUNT; ++i) {
        CensusTarget *target = &g_blend_targets[i];
        char line[380];
        int length;
        BOOL restored;
        if (!target->installed) continue;
        restored = restore_one(target);
        length = wsprintfA(line,
            "{\"schema\":\"g1-writer-census-v1\",\"event\":\"blend_summary\","
            "\"writer\":\"%s\",\"calls_all_states\":%u,\"calls_in_state\":%u,"
            "\"changed_pixels_in_state\":%u,\"samples\":%u,\"restored\":%u,"
            "\"measurement_only\":1}\n",
            target->name, (unsigned)target->call_count, (unsigned)target->calls_ps3,
            (unsigned)g_blend_total_changed[i], (unsigned)g_blend_samples, (unsigned)restored);
        if (length > 0) write_line(line, (DWORD)length);
    }
}

BOOL g1_census_install(void)
{
    DWORD i;
    CensusWrapper wrappers[CENSUS_TARGET_COUNT] = {
        (CensusWrapper)census_rle_clip, (CensusWrapper)census_rle_plain,
        (CensusWrapper)census_rect_fill, (CensusWrapper)census_block_copy,
        (CensusWrapper)census_rect_border, (CensusWrapper)census_rle_tinted_clip,
        (CensusWrapper)census_rle_tinted, (CensusWrapper)census_set_pixel};
    if (!g1_census_enabled()) return TRUE;
    if (InterlockedCompareExchange(&g_installed, 1, 0) != 0) return TRUE;
    initialize_environment();
    g_dest_probe_enabled = g_dest_probe_opt_in;
    open_log();
    if (g_log == INVALID_HANDLE_VALUE) return FALSE;
    g_map_log = CreateFileA(CENSUS_MAP_PATH, GENERIC_WRITE,
                            FILE_SHARE_READ | FILE_SHARE_WRITE, NULL,
                            CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (g_map_log == INVALID_HANDLE_VALUE) {
        CloseHandle(g_log);
        g_log = INVALID_HANDLE_VALUE;
        return FALSE;
    }
    g_context_map_log = CreateFileA(CENSUS_CONTEXT_MAP_PATH, GENERIC_WRITE,
                                    FILE_SHARE_READ | FILE_SHARE_WRITE, NULL,
                                    CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (g_context_map_log == INVALID_HANDLE_VALUE) {
        CloseHandle(g_map_log);
        g_map_log = INVALID_HANDLE_VALUE;
        CloseHandle(g_log);
        g_log = INVALID_HANDLE_VALUE;
        return FALSE;
    }
    if (g_residual_enabled) {
        g_residual_map_log = CreateFileA(CENSUS_RESIDUAL_MAP_PATH, GENERIC_WRITE,
                                         FILE_SHARE_READ | FILE_SHARE_WRITE, NULL,
                                         CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
        if (g_residual_map_log == INVALID_HANDLE_VALUE) {
            CloseHandle(g_context_map_log);
            g_context_map_log = INVALID_HANDLE_VALUE;
            CloseHandle(g_map_log);
            g_map_log = INVALID_HANDLE_VALUE;
            CloseHandle(g_log);
            g_log = INVALID_HANDLE_VALUE;
            return FALSE;
        }
    }
    g_terrain_target.wrapper = (CensusWrapper)census_terrain_context;
    if (!install_one(&g_terrain_target)) {
        emit_install(&g_terrain_target, FALSE);
        g1_census_detach();
        return FALSE;
    }
    emit_install(&g_terrain_target, TRUE);
    if (g_residual_enabled) install_textout_slot();
    emit_writer_table();
    for (i = 0; i < CENSUS_TARGET_COUNT; ++i) {
        g_targets[i].wrapper = wrappers[i];
        if (!install_one(&g_targets[i])) {
            emit_install(&g_targets[i], FALSE);
            g1_census_detach();
            return FALSE;
        }
        emit_install(&g_targets[i], TRUE);
    }
    if (g_residual_enabled && !install_blend_targets()) {
        g1_census_detach();
        return FALSE;
    }
    return TRUE;
}

void g1_census_detach(void)
{
    DWORD i;
    if (g_log == INVALID_HANDLE_VALUE) return;
    for (i = 0; i < CENSUS_TARGET_COUNT; ++i) {
        emit_summary(&g_targets[i]);
        restore_one(&g_targets[i]);
    }
    blend_finish();
    emit_buffer_summaries();
    emit_terrain_summary();
    emit_cache_transfer_summary();
    watch_finish("detach");
    restore_textout_slot();
    restore_one(&g_terrain_target);
    CloseHandle(g_log);
    g_log = INVALID_HANDLE_VALUE;
    if (g_map_log != INVALID_HANDLE_VALUE) {
        CloseHandle(g_map_log);
        g_map_log = INVALID_HANDLE_VALUE;
    }
    if (g_context_map_log != INVALID_HANDLE_VALUE) {
        CloseHandle(g_context_map_log);
        g_context_map_log = INVALID_HANDLE_VALUE;
    }
    if (g_residual_map_log != INVALID_HANDLE_VALUE) {
        CloseHandle(g_residual_map_log);
        g_residual_map_log = INVALID_HANDLE_VALUE;
    }
    InterlockedExchange(&g_installed, 0);
}
