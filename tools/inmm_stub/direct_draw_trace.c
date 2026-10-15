/*
 * direct_draw_trace.c — bounded DirectDraw7 provenance trace.
 *
 * This file is deliberately diagnostic-only.  It is enabled only when
 * SYW2_G1_PRESENT_TRACE=1 is present.  The executable and its surfaces are
 * never modified: the EXE import slot is redirected to this DLL and each
 * returned COM object receives a private vtable copy containing wrappers for
 * the documented methods only.
 *
 * The DLL is built with the same no-CRT rules as the existing diagnostic
 * bridge.  Do not use malloc, stdio, or compiler runtime helpers here.
 */

#include "direct_draw_trace.h"

#include <windows.h>
#include <ddraw.h>

#include "control_state_bridge.h"
#include "surface_reuse_contract.h"
#include "trace_record_serializer.h"
#include "final_d3d9_trace.h"
#include "g1_mirror2x.h"
#include "g1_screen_watch.h"
#include "g1_hd_asset.h"
#include "g1_census.h"
#include "g1_state_snapshot.h"
#include "g1_perf_sections.h"

#define TRACE_PATH "C:\\inmm_g1_present_trace.jsonl"
#define PERF_WINDOW_PATH "C:\\inmm_g1_perf_window.active"
#define INPUT_TRACE_PATH "C:\\inmm_g1_input_trace.jsonl"
#define SCROLL_TRACE_ARM_PATH "C:\\inmm_g1_scroll_trace.arm"
#define SCROLL_TRACE_READY_PATH "C:\\inmm_g1_scroll_trace.ready"
#define TRACE_ENV "SYW2_G1_PRESENT_TRACE"
#define TRACE_RUN_ENV "SYW2_G1_TRACE_RUN_ID"
#define TRACE_SCHEMA "g1-directdraw-trace-v1"
#define TRACE_MAX_METHOD 256u
#define TRACE_MAX_EVENTS 65536u
#define TRACE_MAX_DD 8u
#define TRACE_MAX_SURFACES 32u
#define TRACE_MAX_AGGREGATES 64u
#define TRACE_RESERVED_EVENTS 4u
#define TRACE_MAX_PRIMARY_PRESENT 2048u
#define PERF_WINDOW_MAX_SAMPLES 65536u
#define TRACE_DD_VTABLE_METHODS 30u
#define TRACE_SURFACE_VTABLE_METHODS 49u
#define TRACE_REQUIRED_PROGRAM_STATE_MASK 0x0Fu
#define TRACE_REQUIRED_DETAIL_RESERVE 4u
#define EXE_BASE_EXPECTED 0x00400000u
#define DIRECT_DRAW_IMPORT_THUNK 0x004D7938u
#define DIRECT_DRAW_IAT_SLOT 0x004E5018u
#define DIRECT_DRAW_IAT_THUNK_SIZE 6u
/* The renderer's only DirectDrawCreateEx call (E8 rel32 -> import thunk).  G1 hooks
 * this call instead of the IAT slot so an ASI renderer (hqcdd) can still claim the
 * IAT afterwards; the hook forwards through the thunk, i.e. whatever the IAT holds
 * at call time. */
#define DIRECT_DRAW_CALL_SITE 0x00464374u
#define DIRECT_DRAW_CALL_REL32_ORIGINAL 0x000735BFu
#define NATIVE_2X_SET_DISPLAY_RETURN 0x0046457Du
#define NATIVE_2X_PRESENT_RETURN 0x0049273Fu

typedef HRESULT (WINAPI *DirectDrawCreateExFn)(GUID *, LPVOID *, REFIID, IUnknown *);

/* Keep the hook prototype mechanically tied to MinGW's ddraw.h declaration.
 * A reordered output/IID pair must fail at compile time instead of producing
 * a callable, but ABI-incorrect, function pointer. */
#if defined(__GNUC__) || defined(__clang__)
typedef char direct_draw_create_ex_abi_must_match[
    __builtin_types_compatible_p(__typeof__(&DirectDrawCreateEx), DirectDrawCreateExFn)
        ? 1 : -1];
#endif
typedef struct {
    LPDIRECTDRAW7 object;
    IDirectDraw7Vtbl *original_vtable;
    IDirectDraw7Vtbl *clone_vtable;
    HRESULT (WINAPI *original_set_display_mode)(LPDIRECTDRAW7, DWORD, DWORD, DWORD, DWORD, DWORD);
    HRESULT (WINAPI *original_set_cooperative_level)(LPDIRECTDRAW7, HWND, DWORD);
    HRESULT (WINAPI *original_create_surface)(LPDIRECTDRAW7, LPDDSURFACEDESC2,
                                               LPDIRECTDRAWSURFACE7 *, IUnknown *);
    BOOL installed;
} DDRecord;

typedef struct {
    LPDIRECTDRAWSURFACE7 object;
    IDirectDrawSurface7Vtbl *original_vtable;
    IDirectDrawSurface7Vtbl *clone_vtable;
    HRESULT (WINAPI *original_get_surface_desc)(LPDIRECTDRAWSURFACE7, LPDDSURFACEDESC2);
    HRESULT (WINAPI *original_blt)(LPDIRECTDRAWSURFACE7, LPRECT, LPDIRECTDRAWSURFACE7,
                                   LPRECT, DWORD, LPDDBLTFX);
    HRESULT (WINAPI *original_blt_fast)(LPDIRECTDRAWSURFACE7, DWORD, DWORD,
                                        LPDIRECTDRAWSURFACE7, LPRECT, DWORD);
    HRESULT (WINAPI *original_flip)(LPDIRECTDRAWSURFACE7, LPDIRECTDRAWSURFACE7, DWORD);
    ULONG (WINAPI *original_release)(LPDIRECTDRAWSURFACE7);
    DWORD width;
    DWORD height;
    DWORD caps;
    BOOL descriptor_known;
    BOOL is_primary;
    BOOL installed;
} SurfaceRecord;

typedef struct {
    BOOL used;
    int method;
    DWORD object_identity;
    DWORD original_pointer;
    DWORD present_identity;
    DWORD program_state;
    DWORD count;
    DWORD first_call_seq;
    DWORD last_call_seq;
    DWORD first_tick;
    DWORD last_tick;
} TraceAggregate;

typedef struct {
    void **slot;
    void *loader_target;
    HMODULE ddraw_module;
    DWORD ddraw_start;
    DWORD ddraw_end;
} DirectDrawImport;

static HANDLE g_trace_log = INVALID_HANDLE_VALUE;
static HANDLE g_input_trace_log = INVALID_HANDLE_VALUE;
static volatile LONG g_trace_guard = 0;
static volatile LONG g_trace_enabled = 0;
static volatile LONG g_trace_installed = 0;
static volatile LONG g_trace_failed = 0;
static DWORD g_trace_seq = 0;
static DWORD g_source_seq = 0;
static DWORD g_event_count = 0;
static DWORD g_dropped_count = 0;
static DWORD g_method_call_counts[7];
static DWORD g_method_detailed_counts[7];
static DWORD g_method_aggregated_counts[7];
static DWORD g_method_dropped_counts[7];
static DWORD g_primary_present_count = 0;
static DWORD g_primary_present_dropped = 0;
static DWORD g_primary_elapsed_count = 0;
static DWORD g_primary_elapsed_histogram[256];
static DWORD g_primary_elapsed_max = 0;
static DWORD g_perf_window_count = 0;
static DWORD g_perf_window_dropped = 0;
static DWORD g_perf_window_histogram_ms[256];
static DWORD g_perf_window_first_tick_ms = 0;
static DWORD g_perf_window_last_tick_ms = 0;
static BOOL g_s3_pattern_trace_emitted = FALSE;
static DWORD g_primary_required_states_seen = 0;
static DWORD g_aggregate_output_dropped_count = 0;
static DWORD g_overflow_emitted = 0;
static DWORD g_last_mirror_program_state = 0xFFFFFFFFu;
static BOOL g_perf_window_was_active = FALSE;
static DWORD g_input_trace_seq = 0;
#define INPUT_TRACE_MAX_EVENTS 512u
static WNDPROC g_scroll_trace_original_wndproc = NULL;
static HWND g_scroll_trace_window = NULL;
static DWORD g_scroll_trace_seq = 0;
static LONG g_scroll_trace_window_area = 0;
static volatile LONG g_native_2x_split_applied = 0;
static char g_run_id[96] = "unknown";
static volatile LONG g_env_state = 0;
static BOOL g_trace_opt_in = FALSE;
static BOOL g_scroll_trace_opt_in = FALSE;
static BOOL g_native_2x_blit_opt_in = FALSE;
static BOOL g_native_2x_stretch_opt_in = FALSE;
static char g_perf_window_id[96] = "unset";
static DirectDrawCreateExFn g_original_create_ex = NULL;
static void **g_iat_slot = NULL;
static void *g_iat_original = NULL;
static LONG g_call_site_patched = 0;
static LONG g_deferred_input_installed = 0;
static DDRecord g_dd_records[TRACE_MAX_DD];
static SurfaceRecord g_surface_records[TRACE_MAX_SURFACES];
static TraceAggregate g_aggregates[TRACE_MAX_AGGREGATES];

static HRESULT WINAPI hook_get_surface_desc(LPDIRECTDRAWSURFACE7 self, LPDDSURFACEDESC2 desc);
static HRESULT WINAPI hook_blt(LPDIRECTDRAWSURFACE7 self, LPRECT dst,
                               LPDIRECTDRAWSURFACE7 source, LPRECT src,
                               DWORD flags, LPDDBLTFX fx);
static HRESULT WINAPI hook_blt_fast(LPDIRECTDRAWSURFACE7 self, DWORD x, DWORD y,
                                    LPDIRECTDRAWSURFACE7 source, LPRECT src, DWORD flags);
static HRESULT WINAPI hook_flip(LPDIRECTDRAWSURFACE7 self,
                                LPDIRECTDRAWSURFACE7 target, DWORD flags);
static ULONG WINAPI hook_surface_release(LPDIRECTDRAWSURFACE7 self);
static BOOL native_2x_blit_enabled(void);
static DWORD read_state(DWORD address);

static BOOL CALLBACK scroll_trace_find_window(HWND hwnd, LPARAM unused)
{
    RECT rect;
    DWORD pid = 0;
    (void)unused;
    if (!IsWindowVisible(hwnd)) return TRUE;
    GetWindowThreadProcessId(hwnd, &pid);
    if (pid != GetCurrentProcessId() || !GetWindowRect(hwnd, &rect)) return TRUE;
    if (!g_scroll_trace_window ||
        (rect.right - rect.left) * (rect.bottom - rect.top) > g_scroll_trace_window_area) {
        g_scroll_trace_window = hwnd;
        g_scroll_trace_window_area =
            (rect.right - rect.left) * (rect.bottom - rect.top);
    }
    return TRUE;
}

static LRESULT CALLBACK scroll_trace_wndproc(HWND hwnd, UINT message,
                                              WPARAM wparam, LPARAM lparam)
{
    if ((message == WM_KEYDOWN || message == WM_KEYUP) &&
        g_input_trace_log != INVALID_HANDLE_VALUE &&
        g_scroll_trace_seq < INPUT_TRACE_MAX_EVENTS) {
        char scroll_input_line[512];
        DWORD length;
        DWORD written = 0;
        BOOL write_ok;
        ++g_scroll_trace_seq;
        wsprintfA(scroll_input_line,
                  "{\"schema\":\"g1-scroll-input-v1\",\"seq\":%u,\"ts_ms\":%u,\"pid\":%u,\"hwnd\":\"0x%08X\",\"message\":%u,\"key\":%u,\"scan\":%u,\"repeat\":%u}\n",
                  (unsigned)g_scroll_trace_seq, (unsigned)GetTickCount(),
                  (unsigned)GetCurrentProcessId(), (unsigned)(ULONG_PTR)hwnd,
                  (unsigned)message, (unsigned)wparam,
                  (unsigned)((lparam >> 16) & 0xFF),
                  (unsigned)(lparam & 0xFFFF));
        length = (DWORD)lstrlenA(scroll_input_line);
        write_ok = length < sizeof(scroll_input_line) &&
                   WriteFile(g_input_trace_log, scroll_input_line, length,
                             &written, NULL) && written == length;
        if (write_ok) FlushFileBuffers(g_input_trace_log);
    }
    return g_scroll_trace_original_wndproc
        ? CallWindowProcA(g_scroll_trace_original_wndproc, hwnd, message, wparam, lparam)
        : DefWindowProcA(hwnd, message, wparam, lparam);
}

static DWORD WINAPI scroll_trace_arm_thread(LPVOID unused)
{
    DWORD attempt;
    (void)unused;
    for (attempt = 0; attempt < 18000u; ++attempt) {
        if (GetFileAttributesA(SCROLL_TRACE_ARM_PATH) != INVALID_FILE_ATTRIBUTES) break;
        Sleep(10u);
    }
    if (attempt == 18000u) return 0u;
    for (attempt = 0; attempt < 6000u && !g_scroll_trace_window; ++attempt) {
        EnumWindows(scroll_trace_find_window, 0);
        if (!g_scroll_trace_window) Sleep(1u);
    }
    if (g_scroll_trace_window) {
        LONG old = SetWindowLongA(g_scroll_trace_window, GWL_WNDPROC,
                                  (LONG)(ULONG_PTR)scroll_trace_wndproc);
        if (old != 0) g_scroll_trace_original_wndproc = (WNDPROC)(ULONG_PTR)old;
        else g_scroll_trace_window = NULL;
    }
    if (g_scroll_trace_window && g_scroll_trace_original_wndproc) {
        HANDLE ready = CreateFileA(SCROLL_TRACE_READY_PATH, GENERIC_WRITE,
                                   FILE_SHARE_READ, NULL, CREATE_ALWAYS,
                                   FILE_ATTRIBUTE_NORMAL, NULL);
        if (ready != INVALID_HANDLE_VALUE) {
            char ready_line[192];
            DWORD length = (DWORD)wsprintfA(
                ready_line,
                "{\"schema\":\"g1-scroll-receiver-ready-v1\",\"status\":\"PASS\",\"pid\":%u,\"hwnd\":\"0x%08X\",\"ts_ms\":%u}\n",
                (unsigned)GetCurrentProcessId(),
                (unsigned)(ULONG_PTR)g_scroll_trace_window,
                (unsigned)GetTickCount());
            DWORD written = 0;
            if (length < sizeof(ready_line)) {
                (void)WriteFile(ready, ready_line, length, &written, NULL);
                FlushFileBuffers(ready);
            }
            CloseHandle(ready);
        }
    }
    return 0u;
}

static BOOL read_scroll_camera(LONG *x, LONG *y)
{
    MEMORY_BASIC_INFORMATION mbi;
    volatile LONG *camera = (volatile LONG *)(ULONG_PTR)0x00B42D7Cu;
    if (!x || !y || !VirtualQuery((LPCVOID)camera, &mbi, sizeof(mbi)) ||
        mbi.State != MEM_COMMIT || (mbi.Protect & (PAGE_NOACCESS | PAGE_GUARD)))
        return FALSE;
    *x = camera[0];
    *y = camera[1];
    return TRUE;
}

static void record_primary_elapsed(DWORD elapsed_ms)
{
    if (g_primary_elapsed_count < TRACE_MAX_PRIMARY_PRESENT) {
        ++g_primary_elapsed_count;
        ++g_primary_elapsed_histogram[elapsed_ms < 255u ? elapsed_ms : 255u];
        if (elapsed_ms > g_primary_elapsed_max) g_primary_elapsed_max = elapsed_ms;
    }
    if (read_state(0x004ED818u) == 3u &&
        GetFileAttributesA(PERF_WINDOW_PATH) != INVALID_FILE_ATTRIBUTES) {
        DWORD now = GetTickCount();
        if (g_perf_window_count < PERF_WINDOW_MAX_SAMPLES) {
            if (g_perf_window_count == 0u) g_perf_window_first_tick_ms = now;
            ++g_perf_window_count;
            ++g_perf_window_histogram_ms[elapsed_ms < 255u ? elapsed_ms : 255u];
            g_perf_window_last_tick_ms = now;
        } else {
            ++g_perf_window_dropped;
        }
    }
}

static void primary_elapsed_summary(DWORD *p50, DWORD *p95, DWORD *maximum)
{
    DWORD i;
    DWORD cumulative = 0;
    DWORD p50_target;
    DWORD p95_target;
    BOOL p50_set = FALSE;
    BOOL p95_set = FALSE;
    *p50 = 0u;
    *p95 = 0u;
    if (g_primary_elapsed_count == 0) {
        *p50 = 0u;
        *p95 = 0u;
        *maximum = 0u;
        return;
    }
    p50_target = (g_primary_elapsed_count + 1u) / 2u;
    p95_target = (g_primary_elapsed_count * 95u + 99u) / 100u;
    for (i = 0; i < 256u; ++i) {
        cumulative += g_primary_elapsed_histogram[i];
        if (!p50_set && cumulative >= p50_target) {
            *p50 = i;
            p50_set = TRUE;
        }
        if (!p95_set && cumulative >= p95_target) {
            *p95 = i;
            p95_set = TRUE;
            break;
        }
    }
    *maximum = g_primary_elapsed_max;
}

static BOOL bytes_equal(const BYTE *left, const BYTE *right, DWORD size)
{
    DWORD i;
    for (i = 0; i < size; ++i) if (left[i] != right[i]) return FALSE;
    return TRUE;
}

static void initialize_environment(void)
{
    char value[8];
    DWORD size;
    LONG state = InterlockedCompareExchange(&g_env_state, 1, 0);
    if (state == 0) {
        size = GetEnvironmentVariableA(TRACE_ENV, value, sizeof(value));
        g_trace_opt_in = size == 1u && value[0] == '1';
        size = GetEnvironmentVariableA("SYW2_G1_SCROLL_TRACE", value, sizeof(value));
        g_scroll_trace_opt_in = size == 1u && value[0] == '1';
        size = GetEnvironmentVariableA("SYW2_G1_NATIVE_2X_BLIT", value, sizeof(value));
        g_native_2x_blit_opt_in = size == 1u && value[0] == '1';
        size = GetEnvironmentVariableA("SYW2_G1_NATIVE_2X_STRETCH", value, sizeof(value));
        g_native_2x_stretch_opt_in = size == 1u && value[0] == '1';
        size = GetEnvironmentVariableA(TRACE_RUN_ENV, g_run_id, sizeof(g_run_id));
        if (size == 0u || size >= sizeof(g_run_id)) lstrcpyA(g_run_id, "unknown");
        size = GetEnvironmentVariableA("SYW2_G1_PERF_WINDOW_ID", g_perf_window_id,
                                       sizeof(g_perf_window_id));
        if (size == 0u || size >= sizeof(g_perf_window_id))
            lstrcpyA(g_perf_window_id, "unset");
        InterlockedExchange(&g_env_state, 2);
    } else {
        while (InterlockedCompareExchange(&g_env_state, 2, 2) != 2) Sleep(0);
    }
}

static BOOL scroll_trace_enabled(void)
{
    initialize_environment();
    return g_scroll_trace_opt_in;
}

static BOOL env_enabled(void)
{
    initialize_environment();
    return g_trace_opt_in;
}

static BOOL mirror2x_trace_enabled(void)
{
    return g1_mirror2x_enabled() && native_2x_blit_enabled();
}

static BOOL native_2x_blit_enabled(void)
{
    initialize_environment();
    return g_native_2x_blit_opt_in;
}

static BOOL native_2x_stretch_enabled(void)
{
    initialize_environment();
    return g_native_2x_stretch_opt_in;
}

static BOOL primary_present_call(DWORD return_address)
{
    return return_address == NATIVE_2X_PRESENT_RETURN;
}

static void load_run_id(void)
{
    initialize_environment();
}

static void open_log(void)
{
    if (g_trace_log != INVALID_HANDLE_VALUE) return;
    g_trace_log = CreateFileA(TRACE_PATH, GENERIC_WRITE,
                              FILE_SHARE_READ | FILE_SHARE_WRITE, NULL,
                              CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
}

/* User build (no SYW2_G1_PRESENT_TRACE): an unwritable C:\ root must not
 * disable G1.  Fall back to %TEMP%; if that also fails, run without a log. */
static void open_log_fallback(void)
{
    char path[MAX_PATH + 32];
    DWORD length;
    if (g_trace_log != INVALID_HANDLE_VALUE || env_enabled()) return;
    length = GetTempPathA(MAX_PATH, path);
    if (length == 0u || length >= MAX_PATH) return;
    lstrcatA(path, "inmm_g1_present_trace.jsonl");
    g_trace_log = CreateFileA(path, GENERIC_WRITE,
                              FILE_SHARE_READ | FILE_SHARE_WRITE, NULL,
                              CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
}

static DWORD read_state(DWORD address)
{
    DWORD value = 0xFFFFFFFFu;
    csb_read_state(&value);
    if (address == 0x009B5210u) {
        MEMORY_BASIC_INFORMATION mbi;
        if (VirtualQuery((LPCVOID)(ULONG_PTR)address, &mbi, sizeof(mbi)) &&
            mbi.State == MEM_COMMIT && !(mbi.Protect & (PAGE_NOACCESS | PAGE_GUARD))) {
            value = *(volatile DWORD *)(ULONG_PTR)address;
        }
    }
    return value;
}

static BOOL write_line(const char *line, DWORD length)
{
    DWORD written = 0;
    if (g_trace_log == INVALID_HANDLE_VALUE || !line || length == 0u) return FALSE;
    if (!WriteFile(g_trace_log, line, length, &written, NULL) || written != length) return FALSE;
    return FlushFileBuffers(g_trace_log);
}

static void open_input_log(void)
{
    if (g_input_trace_log != INVALID_HANDLE_VALUE ||
        (!g1_mirror2x_enabled() && !scroll_trace_enabled())) return;
    g_input_trace_log = CreateFileA(INPUT_TRACE_PATH, GENERIC_WRITE,
                                    FILE_SHARE_READ | FILE_SHARE_WRITE, NULL,
                                    CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
}

void g1_mirror2x_input_trace(const char *kind, HWND hwnd, UINT message,
                             LONG physical_x, LONG physical_y,
                             LONG logical_x, LONG logical_y,
                             WPARAM wparam, BOOL transformed)
{
    char input_line[1400];
    int length;
    DWORD written = 0;
    if (g_input_trace_log == INVALID_HANDLE_VALUE || !kind ||
        g_input_trace_seq >= INPUT_TRACE_MAX_EVENTS) return;
    ++g_input_trace_seq;
    length = wsprintfA(input_line,
        "{\"schema\":\"g1-input-trace-v1\",\"run_id\":\"%s\",\"seq\":%u,"
        "\"ts_ms\":%u,\"pid\":%u,\"thread_id\":%u,\"kind\":\"%s\","
        "\"hwnd\":\"0x%08X\",\"message\":%u,\"wparam\":%u,"
        "\"physical\":[%d,%d],\"logical\":[%d,%d],\"transformed\":%u}\n",
        g_run_id, (unsigned)g_input_trace_seq, (unsigned)GetTickCount(),
        (unsigned)GetCurrentProcessId(), (unsigned)GetCurrentThreadId(), kind,
        (unsigned)(ULONG_PTR)hwnd, (unsigned)message, (unsigned)wparam,
        physical_x, physical_y, logical_x, logical_y, (unsigned)transformed);
    if (length <= 0 || (DWORD)length >= sizeof(input_line) ||
        !WriteFile(g_input_trace_log, input_line, (DWORD)length, &written, NULL) ||
        written != (DWORD)length) return;
    FlushFileBuffers(g_input_trace_log);
}

static int method_index(const char *event)
{
    if (lstrcmpA(event, "set_display_mode") == 0) return 0;
    if (lstrcmpA(event, "create_surface") == 0) return 1;
    if (lstrcmpA(event, "get_surface_desc") == 0) return 2;
    if (lstrcmpA(event, "blt") == 0) return 3;
    if (lstrcmpA(event, "blt_fast") == 0) return 4;
    if (lstrcmpA(event, "flip") == 0) return 5;
    if (lstrcmpA(event, "surface_release") == 0) return 6;
    return -1;
}

static const char *method_name(int index)
{
    static const char *names[7] = {
        "set_display_mode", "create_surface", "get_surface_desc", "blt",
        "blt_fast", "flip", "surface_release"
    };
    return index >= 0 && index < 7 ? names[index] : "unknown";
}

static const char *method_interface(int index)
{
    return index == 0 || index == 1 ? "IDirectDraw7" : "IDirectDrawSurface7";
}

static DWORD next_source_seq(void)
{
    return ++g_source_seq;
}

static BOOL trace_event_raw(const char *event, const char *install_status,
                            const char *details, DWORD call_seq,
                            DWORD program_state, DWORD game_tick)
{
    char prefix[1024];
    char line[16384];
    int prefix_length;
    DWORD length = 0u;
    if (!g_trace_enabled || g_trace_log == INVALID_HANDLE_VALUE) return FALSE;
    if (g_event_count >= TRACE_MAX_EVENTS) {
        return FALSE;
    }
    ++g_trace_seq;
    prefix_length = wsprintfA(prefix,
        "{\"schema\":\"%s\",\"run_id\":\"%s\",\"seq\":%u,"
        "\"call_seq\":%u,\"ts_ms\":%u,\"pid\":%u,\"thread_id\":%u,"
        "\"program_state\":%u,\"game_tick\":%u,\"event\":\"%s\","
        "\"install_status\":\"%s\"",
        TRACE_SCHEMA, g_run_id, (unsigned)g_trace_seq, (unsigned)call_seq,
        (unsigned)GetTickCount(),
        (unsigned)GetCurrentProcessId(), (unsigned)GetCurrentThreadId(),
        (unsigned)program_state, (unsigned)game_tick, event, install_status);
    if (prefix_length <= 0 || (DWORD)prefix_length >= sizeof(prefix)) return FALSE;
    if (!trace_record_serialize(line, sizeof(line), prefix, details, &length)) return FALSE;
    if (!write_line(line, length)) return FALSE;
    ++g_event_count;
    return TRUE;
}

static void trace_overflow(const char *scope)
{
    char details[220];
    DWORD call_seq;
    if (g_overflow_emitted >= 2u) return;
    /* Overflow markers are diagnostic detail; never consume the summary slot. */
    if (g_event_count >= TRACE_MAX_EVENTS - 1u) return;
    wsprintfA(details, ",\"scope\":\"%s\",\"dropped_count\":%u",
              scope, (unsigned)g_dropped_count);
    call_seq = next_source_seq();
    if (trace_event_raw("overflow", "active", details, call_seq,
                        read_state(0x004ED818u), read_state(0x009B5210u))) {
        ++g_overflow_emitted;
    }
}

static void trace_event(const char *event, const char *install_status, const char *details)
{
    DWORD call_seq = next_source_seq();
    BOOL reserved_diagnostic = lstrcmpA(event, "ret_range_diag") == 0 ||
                               lstrcmpA(event, "program_state_change") == 0;
    /* Keep slots for both overflow markers, opt-in/state diagnostics, and summary. */
    if (lstrcmpA(event, "summary") != 0 && !reserved_diagnostic &&
        g_event_count >= TRACE_MAX_EVENTS - TRACE_RESERVED_EVENTS) {
        ++g_dropped_count;
        g_trace_failed = 1;
        trace_overflow("event_limit");
        return;
    }
    /* Reserved diagnostics are rare and keep match-end state changes visible near the cap. */
    if (reserved_diagnostic && g_event_count >= TRACE_MAX_EVENTS - 1u) {
        ++g_dropped_count;
        g_trace_failed = 1;
        return;
    }
    if (!trace_event_raw(event, install_status, details, call_seq,
                         read_state(0x004ED818u), read_state(0x009B5210u))) {
        ++g_dropped_count;
        g_trace_failed = 1;
        /* Below the event cap the record failed to serialize or write (e.g. a line longer than the buffer). */
        if (g_event_count < TRACE_MAX_EVENTS) trace_overflow("serialize");
        else trace_overflow("event_limit");
    }
}

static BOOL trace_method_aggregate(int index, DWORD object_identity,
                                   DWORD original_pointer, DWORD present_identity,
                                   DWORD program_state, DWORD call_seq, DWORD tick)
{
    DWORD i;
    TraceAggregate *free_slot = NULL;
    for (i = 0; i < TRACE_MAX_AGGREGATES; ++i) {
        TraceAggregate *entry = &g_aggregates[i];
        if (!entry->used) {
            if (!free_slot) free_slot = entry;
            continue;
        }
        if (entry->method == index && entry->object_identity == object_identity &&
            entry->original_pointer == original_pointer &&
            entry->present_identity == present_identity &&
            entry->program_state == program_state) {
            ++entry->count;
            entry->last_call_seq = call_seq;
            entry->last_tick = tick;
            return TRUE;
        }
    }
    if (!free_slot) return FALSE;
    ZeroMemory(free_slot, sizeof(*free_slot));
    free_slot->used = TRUE;
    free_slot->method = index;
    free_slot->object_identity = object_identity;
    free_slot->original_pointer = original_pointer;
    free_slot->present_identity = present_identity;
    free_slot->program_state = program_state;
    free_slot->count = 1u;
    free_slot->first_call_seq = call_seq;
    free_slot->last_call_seq = call_seq;
    free_slot->first_tick = tick;
    free_slot->last_tick = tick;
    return TRUE;
}

static void trace_method_event(const char *event, const char *install_status,
                               const char *details, DWORD object_identity,
                               DWORD original_pointer, DWORD present_identity)
{
    int index = method_index(event);
    DWORD call_seq = next_source_seq();
    DWORD program_state = read_state(0x004ED818u);
    DWORD tick = read_state(0x009B5210u);
    if (index < 0) {
        trace_event(event, install_status, details);
        return;
    }
    ++g_method_call_counts[index];
    if (g_method_detailed_counts[index] < TRACE_MAX_METHOD &&
        g_event_count < TRACE_MAX_EVENTS - TRACE_RESERVED_EVENTS - TRACE_MAX_AGGREGATES &&
        trace_event_raw(event, install_status, details, call_seq, program_state, tick)) {
        ++g_method_detailed_counts[index];
        return;
    }
    if (trace_method_aggregate(index, object_identity, original_pointer,
                               present_identity, program_state, call_seq, tick)) {
        ++g_method_aggregated_counts[index];
        return;
    }
    ++g_method_dropped_counts[index];
    ++g_dropped_count;
    g_trace_failed = 1;
    trace_overflow(event);
}

static void trace_primary_method_event(const char *event, const char *install_status,
                                      const char *details, DWORD object_identity,
                                      DWORD original_pointer, DWORD present_identity,
                                      BOOL preserve_required_state)
{
    int index = method_index(event);
    DWORD call_seq = next_source_seq();
    DWORD program_state = read_state(0x004ED818u);
    DWORD tick = read_state(0x009B5210u);
    DWORD required_bit = 0u;
    BOOL required_state = FALSE;
    DWORD detail_limit = TRACE_MAX_METHOD;
    (void)object_identity;
    (void)original_pointer;
    (void)present_identity;
    if (preserve_required_state) {
        if (program_state == 3u) required_bit = 1u;
        else if (program_state == 5u) required_bit = 2u;
        else if (program_state == 7u) required_bit = 4u;
        else if (program_state == 9u) required_bit = 8u;
        required_state = required_bit != 0u &&
                         (g_primary_required_states_seen & required_bit) == 0u;
    }
    /* Keep four detailed slots available for the first converted primary
     * present in each required program state.  Without this reserve, PS3's
     * high call volume consumes the 256-detail cap before late state 3/5/7/9
     * records can be serialized, leaving only aggregate records that no
     * longer carry the converted primary evidence. */
    if ((g_primary_required_states_seen & TRACE_REQUIRED_PROGRAM_STATE_MASK) !=
            TRACE_REQUIRED_PROGRAM_STATE_MASK && !required_state) {
        detail_limit -= TRACE_REQUIRED_DETAIL_RESERVE;
    }
    ++g_primary_present_count;
    if (index >= 0) ++g_method_call_counts[index];
    if (index >= 0 && g_method_detailed_counts[index] < detail_limit &&
        g_event_count < TRACE_MAX_EVENTS - TRACE_RESERVED_EVENTS - TRACE_MAX_AGGREGATES &&
        trace_event_raw(event, install_status, details, call_seq, program_state, tick)) {
        ++g_method_detailed_counts[index];
        if (required_state) g_primary_required_states_seen |= required_bit;
        return;
    }
    if (index >= 0 && trace_method_aggregate(index, object_identity, original_pointer,
                                             present_identity, program_state, call_seq, tick)) {
        ++g_method_aggregated_counts[index];
        return;
    }
    {
        ++g_primary_present_dropped;
        ++g_method_dropped_counts[index >= 0 ? index : 0];
        ++g_dropped_count;
        g_trace_failed = 1;
        trace_overflow("primary_present");
    }
}

static void trace_emit_aggregates(void)
{
    DWORD i;
    for (i = 0; i < TRACE_MAX_AGGREGATES; ++i) {
        TraceAggregate *entry = &g_aggregates[i];
        char details[900];
        if (!entry->used) continue;
        /* Leave the final event slot for the summary, even when aggregates remain. */
        if (g_event_count >= TRACE_MAX_EVENTS - 1u) {
            ++g_aggregate_output_dropped_count;
            ++g_dropped_count;
            g_trace_failed = 1;
            continue;
        }
        wsprintfA(details,
                  ",\"method\":\"%s\",\"object\":\"0x%08X\",\"interface\":\"%s\",\"original_pointer\":\"0x%08X\",\"present_identity\":\"0x%08X\",\"program_state\":%u,\"count\":%u,\"first_call_seq\":%u,\"last_call_seq\":%u,\"first_tick\":%u,\"last_tick\":%u",
                  method_name(entry->method), (unsigned)entry->object_identity,
                  method_interface(entry->method), (unsigned)entry->original_pointer,
                  (unsigned)entry->present_identity, (unsigned)entry->program_state,
                  (unsigned)entry->count, (unsigned)entry->first_call_seq,
                  (unsigned)entry->last_call_seq, (unsigned)entry->first_tick,
                  (unsigned)entry->last_tick);
        if (!trace_event_raw("aggregate", "active", details, next_source_seq(),
                             read_state(0x004ED818u), read_state(0x009B5210u))) {
            ++g_aggregate_output_dropped_count;
            ++g_dropped_count;
            g_trace_failed = 1;
            trace_overflow("aggregate_output");
        }
    }
}

static DWORD aggregate_record_count(void)
{
    DWORD i, count = 0;
    for (i = 0; i < TRACE_MAX_AGGREGATES; ++i) if (g_aggregates[i].used) ++count;
    return count;
}

static void trace_emit_summary(void)
{
    char details[4096];
    DWORD primary_elapsed_p50;
    DWORD primary_elapsed_p95;
    DWORD primary_elapsed_max;
    primary_elapsed_summary(&primary_elapsed_p50, &primary_elapsed_p95,
                            &primary_elapsed_max);
    wsprintfA(details,
        ",\"event_count\":%u,\"dropped_count\":%u,\"source_call_count\":%u,\"aggregate_record_count\":%u,\"aggregate_output_dropped_count\":%u,\"method_counts\":{"
        "\"set_display_mode\":{\"detailed_count\":%u,\"aggregated_count\":%u,\"dropped_count\":%u,\"total_count\":%u},"
        "\"create_surface\":{\"detailed_count\":%u,\"aggregated_count\":%u,\"dropped_count\":%u,\"total_count\":%u},"
        "\"get_surface_desc\":{\"detailed_count\":%u,\"aggregated_count\":%u,\"dropped_count\":%u,\"total_count\":%u},"
        "\"blt\":{\"detailed_count\":%u,\"aggregated_count\":%u,\"dropped_count\":%u,\"total_count\":%u},"
        "\"blt_fast\":{\"detailed_count\":%u,\"aggregated_count\":%u,\"dropped_count\":%u,\"total_count\":%u},"
        "\"flip\":{\"detailed_count\":%u,\"aggregated_count\":%u,\"dropped_count\":%u,\"total_count\":%u},"
        "\"surface_release\":{\"detailed_count\":%u,\"aggregated_count\":%u,\"dropped_count\":%u,\"total_count\":%u}},"
        "\"primary_present_count\":%u,\"primary_present_dropped\":%u,"
        "\"primary_present_elapsed_ms\":{\"count\":%u,\"p50\":%u,\"p95\":%u,\"max\":%u},"
        "\"detach\":\"complete\",\"flush\":\"complete\"",
        (unsigned)g_event_count, (unsigned)g_dropped_count, (unsigned)g_source_seq,
        (unsigned)aggregate_record_count(),
        (unsigned)g_aggregate_output_dropped_count,
        (unsigned)g_method_detailed_counts[0], (unsigned)g_method_aggregated_counts[0], (unsigned)g_method_dropped_counts[0], (unsigned)g_method_call_counts[0],
        (unsigned)g_method_detailed_counts[1], (unsigned)g_method_aggregated_counts[1], (unsigned)g_method_dropped_counts[1], (unsigned)g_method_call_counts[1],
        (unsigned)g_method_detailed_counts[2], (unsigned)g_method_aggregated_counts[2], (unsigned)g_method_dropped_counts[2], (unsigned)g_method_call_counts[2],
        (unsigned)g_method_detailed_counts[3], (unsigned)g_method_aggregated_counts[3], (unsigned)g_method_dropped_counts[3], (unsigned)g_method_call_counts[3],
        (unsigned)g_method_detailed_counts[4], (unsigned)g_method_aggregated_counts[4], (unsigned)g_method_dropped_counts[4], (unsigned)g_method_call_counts[4],
        (unsigned)g_method_detailed_counts[5], (unsigned)g_method_aggregated_counts[5], (unsigned)g_method_dropped_counts[5], (unsigned)g_method_call_counts[5],
        (unsigned)g_method_detailed_counts[6], (unsigned)g_method_aggregated_counts[6], (unsigned)g_method_dropped_counts[6], (unsigned)g_method_call_counts[6],
        (unsigned)g_primary_present_count, (unsigned)g_primary_present_dropped,
        (unsigned)g_primary_elapsed_count, (unsigned)primary_elapsed_p50,
        (unsigned)primary_elapsed_p95, (unsigned)primary_elapsed_max);
    trace_event("summary", g_trace_failed ? "failed" : "detached", details);
}

static void trace_emit_perf_window_histogram(void)
{
    DWORD elapsed_ms;
    if (g_perf_window_count == 0u) return;
    {
        char details[192];
        wsprintfA(details,
            ",\"program_state\":3,\"count\":%u,\"dropped\":%u,\"first_tick_ms\":%u,\"last_tick_ms\":%u",
            (unsigned)g_perf_window_count, (unsigned)g_perf_window_dropped,
            (unsigned)g_perf_window_first_tick_ms, (unsigned)g_perf_window_last_tick_ms);
        trace_event("perf_window_meta", "complete", details);
    }
    for (elapsed_ms = 0u; elapsed_ms < 256u; ++elapsed_ms) {
        DWORD count = g_perf_window_histogram_ms[elapsed_ms];
        if (count == 0u) continue;
        {
            char details[128];
            wsprintfA(details,
                ",\"program_state\":3,\"elapsed_ms\":%u,\"count\":%u",
                (unsigned)elapsed_ms, (unsigned)count);
            trace_event("perf_window_histogram", "complete", details);
        }
    }
}

static DWORD module_end(HMODULE module)
{
    IMAGE_DOS_HEADER *dos;
    IMAGE_NT_HEADERS *nt;
    if (!module) return 0;
    dos = (IMAGE_DOS_HEADER *)module;
    if (dos->e_magic != IMAGE_DOS_SIGNATURE) return 0;
    nt = (IMAGE_NT_HEADERS *)((BYTE *)module + dos->e_lfanew);
    if (nt->Signature != IMAGE_NT_SIGNATURE) return 0;
    return (DWORD)(ULONG_PTR)module + nt->OptionalHeader.SizeOfImage;
}

static BOOL write_pointer(void **location, void *expected, void *value, void **old_out)
{
    DWORD old_protect = 0;
    DWORD restored = 0;
    void *old;
    if (!VirtualProtect(location, sizeof(void *), PAGE_READWRITE, &old_protect)) return FALSE;
    old = *location;
    if (expected && old != expected) {
        VirtualProtect(location, sizeof(void *), old_protect, &restored);
        return FALSE;
    }
    *location = value;
    if (!VirtualProtect(location, sizeof(void *), old_protect, &restored)) {
        /* The slot is still writable when protection restoration fails. */
        *location = old;
        VirtualProtect(location, sizeof(void *), old_protect, &restored);
        return FALSE;
    }
    if (old_out) *old_out = old;
    FlushInstructionCache(GetCurrentProcess(), location, sizeof(void *));
    return TRUE;
}

/* Code pages must stay executable while patched (unlike write_pointer's data slots). */
static BOOL write_code_dword(DWORD address, DWORD expected, DWORD value)
{
    DWORD *location = (DWORD *)(ULONG_PTR)address;
    DWORD old_protect = 0;
    DWORD restored = 0;
    if (!VirtualProtect(location, sizeof(DWORD), PAGE_EXECUTE_READWRITE, &old_protect)) return FALSE;
    if (*location != expected) {
        VirtualProtect(location, sizeof(DWORD), old_protect, &restored);
        return FALSE;
    }
    *location = value;
    VirtualProtect(location, sizeof(DWORD), old_protect, &restored);
    FlushInstructionCache(GetCurrentProcess(), location, sizeof(DWORD));
    return TRUE;
}

static BOOL replace_object_vtable(void *object, void **clone, void **old_out)
{
    return write_pointer((void **)object, NULL, clone, old_out);
}

static BOOL clone_dd_vtable(LPDIRECTDRAW7 object, IDirectDraw7Vtbl **clone_out,
                            IDirectDraw7Vtbl **old_out)
{
    IDirectDraw7Vtbl *old_vtable = object->lpVtbl;
    IDirectDraw7Vtbl *clone = (IDirectDraw7Vtbl *)HeapAlloc(
        GetProcessHeap(), HEAP_ZERO_MEMORY, sizeof(IDirectDraw7Vtbl));
    if (!clone) return FALSE;
    *clone = *old_vtable;
    if (!replace_object_vtable(object, (void **)clone, (void **)old_out)) {
        HeapFree(GetProcessHeap(), 0, clone);
        return FALSE;
    }
    *clone_out = clone;
    return TRUE;
}

static BOOL clone_surface_vtable(LPDIRECTDRAWSURFACE7 object,
                                 IDirectDrawSurface7Vtbl **clone_out,
                                 IDirectDrawSurface7Vtbl **old_out)
{
    IDirectDrawSurface7Vtbl *old_vtable = object->lpVtbl;
    IDirectDrawSurface7Vtbl *clone = (IDirectDrawSurface7Vtbl *)HeapAlloc(
        GetProcessHeap(), HEAP_ZERO_MEMORY, sizeof(IDirectDrawSurface7Vtbl));
    if (!clone) return FALSE;
    *clone = *old_vtable;
    if (!replace_object_vtable(object, (void **)clone, (void **)old_out)) {
        HeapFree(GetProcessHeap(), 0, clone);
        return FALSE;
    }
    *clone_out = clone;
    return TRUE;
}

static BOOL find_ddraw_iat(DirectDrawImport *import)
{
    BYTE *base = (BYTE *)(ULONG_PTR)EXE_BASE_EXPECTED;
    IMAGE_DOS_HEADER *dos = (IMAGE_DOS_HEADER *)base;
    IMAGE_NT_HEADERS *nt;
    IMAGE_IMPORT_DESCRIPTOR *imp;
    HMODULE ddraw;
    DWORD ddraw_start, ddraw_stop;
    if (!import) return FALSE;
    if (dos->e_magic != IMAGE_DOS_SIGNATURE) return FALSE;
    nt = (IMAGE_NT_HEADERS *)(base + dos->e_lfanew);
    if (nt->Signature != IMAGE_NT_SIGNATURE || nt->FileHeader.Machine != IMAGE_FILE_MACHINE_I386) return FALSE;
    imp = (IMAGE_IMPORT_DESCRIPTOR *)(base + nt->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IMPORT].VirtualAddress);
    ddraw = GetModuleHandleA("ddraw.dll");
    ddraw_start = (DWORD)(ULONG_PTR)ddraw;
    ddraw_stop = module_end(ddraw);
    if (!ddraw || !ddraw_stop || !imp) return FALSE;
    for (; imp->Name; ++imp) {
        const char *dll_name = (const char *)(base + imp->Name);
        IMAGE_THUNK_DATA *oft;
        IMAGE_THUNK_DATA *ft;
        if (lstrcmpiA(dll_name, "DDRAW.dll") != 0) continue;
        oft = (IMAGE_THUNK_DATA *)(base + imp->OriginalFirstThunk);
        ft = (IMAGE_THUNK_DATA *)(base + imp->FirstThunk);
        for (; oft->u1.AddressOfData; ++oft, ++ft) {
            IMAGE_IMPORT_BY_NAME *name;
            if (oft->u1.Ordinal & IMAGE_ORDINAL_FLAG) continue;
            name = (IMAGE_IMPORT_BY_NAME *)(base + oft->u1.AddressOfData);
            if (lstrcmpA((const char *)name->Name, "DirectDrawCreateEx") != 0) continue;
            if ((DWORD)(ULONG_PTR)&ft->u1.Function != DIRECT_DRAW_IAT_SLOT) return FALSE;
            /* The slot may already point at an ASI renderer; G1 no longer writes it. */
            if (!ft->u1.Function) return FALSE;
            import->slot = (void **)&ft->u1.Function;
            import->loader_target = (void *)(ULONG_PTR)ft->u1.Function;
            import->ddraw_module = ddraw;
            import->ddraw_start = ddraw_start;
            import->ddraw_end = ddraw_stop;
            return TRUE;
        }
    }
    return FALSE;
}

static DDRecord *dd_record(void *object)
{
    DWORD i;
    for (i = 0; i < TRACE_MAX_DD; ++i) if (g_dd_records[i].object == object) return &g_dd_records[i];
    return NULL;
}

static SurfaceRecord *surface_record(void *object)
{
    DWORD i;
    for (i = 0; i < TRACE_MAX_SURFACES; ++i) if (g_surface_records[i].object == object) return &g_surface_records[i];
    return NULL;
}

static G1SurfaceReuseDecision surface_record_reusable(const SurfaceRecord *record,
                                                      LPDIRECTDRAWSURFACE7 object)
{
    G1SurfaceReuseInput input;

    input.installed = record ? record->installed : 0;
    input.record_object = record ? record->object : NULL;
    input.object = object;
    input.object_vtable = object ? object->lpVtbl : NULL;
    input.original_vtable = record ? record->original_vtable : NULL;
    input.clone_vtable = record ? record->clone_vtable : NULL;
    input.clone_get_surface_desc = record && record->clone_vtable
        ? (G1SurfaceMethodPointer)record->clone_vtable->GetSurfaceDesc : NULL;
    input.clone_blt = record && record->clone_vtable
        ? (G1SurfaceMethodPointer)record->clone_vtable->Blt : NULL;
    input.clone_blt_fast = record && record->clone_vtable
        ? (G1SurfaceMethodPointer)record->clone_vtable->BltFast : NULL;
    input.clone_flip = record && record->clone_vtable
        ? (G1SurfaceMethodPointer)record->clone_vtable->Flip : NULL;
    input.clone_release = record && record->clone_vtable
        ? (G1SurfaceMethodPointer)record->clone_vtable->Release : NULL;
    input.hook_get_surface_desc = (G1SurfaceMethodPointer)hook_get_surface_desc;
    input.hook_blt = (G1SurfaceMethodPointer)hook_blt;
    input.hook_blt_fast = (G1SurfaceMethodPointer)hook_blt_fast;
    input.hook_flip = (G1SurfaceMethodPointer)hook_flip;
    input.hook_release = (G1SurfaceMethodPointer)hook_surface_release;
    input.original_get_surface_desc = record
        ? (G1SurfaceMethodPointer)record->original_get_surface_desc : NULL;
    input.original_blt = record ? (G1SurfaceMethodPointer)record->original_blt : NULL;
    input.original_blt_fast = record ? (G1SurfaceMethodPointer)record->original_blt_fast : NULL;
    input.original_flip = record ? (G1SurfaceMethodPointer)record->original_flip : NULL;
    input.original_release = record ? (G1SurfaceMethodPointer)record->original_release : NULL;
    return g1_surface_reuse_decide(&input);
}

static void trace_surface_reuse_failure(const SurfaceRecord *record,
                                         LPDIRECTDRAWSURFACE7 object,
                                         G1SurfaceReuseDecision decision)
{
    char details[900];
    wsprintfA(details,
              ",\"stage\":\"surface_vtable\",\"reason_code\":%u,\"reason\":\"%s\",\"actual_object\":\"0x%08X\",\"actual_vtable\":\"0x%08X\",\"stored_clone_vtable\":\"0x%08X\",\"stored_original_vtable\":\"0x%08X\",\"stored_release\":\"0x%08X\",\"hook_release\":\"0x%08X\",\"original_release\":\"0x%08X\"",
              (unsigned)decision.reason, g1_surface_reuse_reason_name(decision.reason),
              (unsigned)(ULONG_PTR)object,
              (unsigned)(ULONG_PTR)(object ? object->lpVtbl : NULL),
              (unsigned)(ULONG_PTR)(record ? record->clone_vtable : NULL),
              (unsigned)(ULONG_PTR)(record ? record->original_vtable : NULL),
              (unsigned)(ULONG_PTR)(record && record->clone_vtable ? record->clone_vtable->Release : NULL),
              (unsigned)(ULONG_PTR)hook_surface_release,
              (unsigned)(ULONG_PTR)(record ? record->original_release : NULL));
    trace_event("install", "failed", details);
}

static void format_rect(char *out, const RECT *rect)
{
    if (!rect) { lstrcpyA(out, "null"); return; }
    wsprintfA(out, "{\"left\":%d,\"top\":%d,\"right\":%d,\"bottom\":%d}",
              rect->left, rect->top, rect->right, rect->bottom);
}

static void format_desc(char *out, const DDSURFACEDESC2 *desc)
{
    if (!desc) { lstrcpyA(out, "null"); return; }
    wsprintfA(out, "{\"flags\":%u,\"width\":%u,\"height\":%u,\"backbuffer_count\":%u,\"caps\":%u,\"pitch\":%d,\"pixel_format_flags\":%u,\"rgb_bit_count\":%u}",
              (unsigned)desc->dwFlags, (unsigned)desc->dwWidth, (unsigned)desc->dwHeight,
              (unsigned)desc->dwBackBufferCount, (unsigned)desc->ddsCaps.dwCaps,
              (int)desc->lPitch, (unsigned)desc->ddpfPixelFormat.dwFlags,
              (unsigned)desc->ddpfPixelFormat.dwRGBBitCount);
}

/* G1's window subclass goes on before the renderer's SetCooperativeLevel
 * subclasses the same window, so the renderer's client->surface mapping runs
 * first and G1 halves its result (see g1_mirror2x_input_subclass). */
static HRESULT WINAPI hook_set_cooperative_level(LPDIRECTDRAW7 self, HWND window, DWORD flags)
{
    DDRecord *record = dd_record(self);
    if (!record || !record->original_set_cooperative_level) return DDERR_GENERIC;
    if (g1_mirror2x_enabled() && window && !g1_mirror2x_input_subclass(window)) {
        trace_event("install", "failed", ",\"stage\":\"mirror2x_input\",\"reason\":\"cooperative_window_subclass_failed\"");
        g_trace_failed = 1;
    }
    return record->original_set_cooperative_level(self, window, flags);
}

static HRESULT WINAPI hook_set_display_mode(LPDIRECTDRAW7 self, DWORD width, DWORD height,
                                             DWORD bpp, DWORD refresh, DWORD flags)
{
    DDRecord *record = dd_record(self);
    HRESULT result;
    char details[900];
    DWORD return_address = (DWORD)(ULONG_PTR)__builtin_return_address(0);
    DWORD forwarded_width = width;
    DWORD forwarded_height = height;
    BOOL native_2x_opt_in = native_2x_blit_enabled();
    BOOL native_2x_applied = native_2x_opt_in &&
        width == 800u && height == 600u && bpp == 8u &&
        return_address == NATIVE_2X_SET_DISPLAY_RETURN;
    const char *native_2x_skip_reason = "disabled";
    if (native_2x_applied) {
        forwarded_width = 1600u;
        forwarded_height = 1200u;
        native_2x_skip_reason = "none";
    } else if (native_2x_opt_in) {
        native_2x_skip_reason = "exact_800x600x8_call_gate_mismatch";
    }
    if (!record || !record->original_set_display_mode) return DDERR_GENERIC;
    result = record->original_set_display_mode(self, forwarded_width, forwarded_height,
                                                bpp, refresh, flags);
    if (native_2x_applied && SUCCEEDED(result)) InterlockedExchange(&g_native_2x_split_applied, 1);
    if (g1_mirror2x_enabled() && InterlockedCompareExchange(&g_deferred_input_installed, 1, 0) == 0 &&
        !g1_mirror2x_input_install()) {
        trace_event("install", "failed", ",\"stage\":\"mirror2x_input\",\"reason\":\"user32_iat_or_window_subclass_failed\"");
        g_trace_failed = 1;
    }
    wsprintfA(details, ",\"object\":\"0x%08X\",\"dd_vtable_methods\":%u,\"original_pointer\":\"0x%08X\",\"width\":%u,\"height\":%u,\"bpp\":%u,\"refresh\":%u,\"flags\":%u,\"requested_width\":%u,\"requested_height\":%u,\"requested_bpp\":%u,\"forwarded_width\":%u,\"forwarded_height\":%u,\"forwarded_bpp\":%u,\"native_2x_opt_in\":%u,\"native_2x_applied\":%u,\"native_2x_skip_reason\":\"%s\",\"caller\":\"0x%08X\",\"return_address\":\"0x%08X\",\"hresult\":%ld",
              (unsigned)(ULONG_PTR)self, (unsigned)TRACE_DD_VTABLE_METHODS,
              (unsigned)(ULONG_PTR)record->original_set_display_mode,
              (unsigned)width, (unsigned)height, (unsigned)bpp, (unsigned)refresh,
              (unsigned)flags, (unsigned)width, (unsigned)height, (unsigned)bpp,
              (unsigned)forwarded_width, (unsigned)forwarded_height, (unsigned)bpp,
              (unsigned)native_2x_opt_in, (unsigned)native_2x_applied,
              native_2x_skip_reason, (unsigned)return_address, (unsigned)return_address,
              (long)result);
    trace_method_event("set_display_mode", "active", details,
                       (DWORD)(ULONG_PTR)self,
                       (DWORD)(ULONG_PTR)record->original_set_display_mode,
                       (DWORD)(ULONG_PTR)self);
    if (native_2x_opt_in && !native_2x_applied) {
        char skip_details[420];
        wsprintfA(skip_details,
                  ",\"kind\":\"native_2x_blit\",\"reason\":\"%s\",\"return_address\":\"0x%08X\",\"requested_width\":%u,\"requested_height\":%u,\"requested_bpp\":%u",
                  native_2x_skip_reason, (unsigned)return_address,
                  (unsigned)width, (unsigned)height, (unsigned)bpp);
        trace_event("structured_skip", "active", skip_details);
    }
    return result;
}

static HRESULT WINAPI hook_create_surface(LPDIRECTDRAW7 self, LPDDSURFACEDESC2 request,
                                           LPDIRECTDRAWSURFACE7 *surface, IUnknown *outer)
{
    DDRecord *record = dd_record(self);
    HRESULT result;
    char request_json[640];
    char details[1800];
    DWORD surface_methods = 0;
    const char *install_status = "active";
    if (!record || !record->original_create_surface) return DDERR_GENERIC;
    result = record->original_create_surface(self, request, surface, outer);
    format_desc(request_json, request);
    if (SUCCEEDED(result) && surface && *surface) {
        SurfaceRecord *slot = surface_record(*surface);
        DWORD i;
        if (!slot) {
            for (i = 0; i < TRACE_MAX_SURFACES; ++i) if (!g_surface_records[i].object) { slot = &g_surface_records[i]; break; }
        }
        if (!slot) {
            ++g_dropped_count;
            g_trace_failed = 1;
            install_status = "failed";
            trace_overflow("surface_records");
            trace_event("install", "failed", ",\"stage\":\"surface_record\",\"reason\":\"record_capacity_exhausted\"");
        } else if (slot->installed || slot->object) {
            G1SurfaceReuseDecision decision = surface_record_reusable(slot, *surface);
            if (decision.reusable) {
                surface_methods = decision.method_count;
            } else {
                g_trace_failed = 1;
                install_status = "failed";
                trace_surface_reuse_failure(slot, *surface, decision);
            }
        } else {
            IDirectDrawSurface7Vtbl *old_vtable = NULL;
            IDirectDrawSurface7Vtbl *clone = NULL;
            if (!clone_surface_vtable(*surface, &clone, &old_vtable)) {
                g_trace_failed = 1;
                install_status = "failed";
                trace_event("install", "failed", ",\"stage\":\"surface_vtable\",\"reason\":\"clone_or_replace_failed\"");
            } else {
                slot->object = *surface;
                slot->original_vtable = old_vtable;
                slot->clone_vtable = clone;
                slot->original_get_surface_desc = old_vtable->GetSurfaceDesc;
                slot->original_blt = old_vtable->Blt;
                slot->original_blt_fast = old_vtable->BltFast;
                slot->original_flip = old_vtable->Flip;
                slot->original_release = old_vtable->Release;
                slot->descriptor_known = request != NULL;
                slot->width = request ? request->dwWidth : 0u;
                slot->height = request ? request->dwHeight : 0u;
                slot->caps = request ? request->ddsCaps.dwCaps : 0u;
                slot->is_primary = request &&
                    (request->ddsCaps.dwCaps & DDSCAPS_PRIMARYSURFACE) != 0;
                clone->GetSurfaceDesc = hook_get_surface_desc;
                clone->Blt = hook_blt;
                clone->BltFast = hook_blt_fast;
                clone->Flip = hook_flip;
                clone->Release = hook_surface_release;
                slot->installed = TRUE;
                surface_methods = TRACE_SURFACE_VTABLE_METHODS;
            }
        }
    }
    wsprintfA(details, ",\"dd_object\":\"0x%08X\",\"dd_vtable_methods\":%u,\"original_pointer\":\"0x%08X\",\"descriptor\":%s,\"returned_surface\":\"0x%08X\",\"surface_interface\":\"IDirectDrawSurface7\",\"surface_vtable_methods\":%u,\"caller\":\"0x%08X\",\"return_address\":\"0x%08X\",\"hresult\":%ld",
              (unsigned)(ULONG_PTR)self, (unsigned)TRACE_DD_VTABLE_METHODS,
              (unsigned)(ULONG_PTR)record->original_create_surface, request_json,
              (unsigned)(ULONG_PTR)(surface ? *surface : NULL), (unsigned)surface_methods,
              (unsigned)(ULONG_PTR)__builtin_return_address(0),
              (unsigned)(ULONG_PTR)__builtin_return_address(0), (long)result);
    trace_method_event("create_surface", install_status, details,
                       (DWORD)(ULONG_PTR)self,
                       (DWORD)(ULONG_PTR)record->original_create_surface,
                       (DWORD)(ULONG_PTR)(surface ? *surface : NULL));
    return result;
}

static HRESULT WINAPI hook_get_surface_desc(LPDIRECTDRAWSURFACE7 self, LPDDSURFACEDESC2 desc)
{
    SurfaceRecord *record = surface_record(self);
    HRESULT result;
    char desc_json[640];
    char details[1100];
    if (!record || !record->original_get_surface_desc) return DDERR_GENERIC;
    result = record->original_get_surface_desc(self, desc);
    if (SUCCEEDED(result) && desc) {
        record->descriptor_known = TRUE;
        record->width = desc->dwWidth;
        record->height = desc->dwHeight;
        record->caps = desc->ddsCaps.dwCaps;
        record->is_primary = (desc->ddsCaps.dwCaps & DDSCAPS_PRIMARYSURFACE) != 0 ||
            record->is_primary;
    }
    format_desc(desc_json, desc);
    wsprintfA(details, ",\"surface\":\"0x%08X\",\"surface_interface\":\"IDirectDrawSurface7\",\"surface_vtable_methods\":%u,\"original_pointer\":\"0x%08X\",\"actual_desc\":%s,\"caller\":\"0x%08X\",\"return_address\":\"0x%08X\",\"hresult\":%ld",
              (unsigned)(ULONG_PTR)self, (unsigned)TRACE_SURFACE_VTABLE_METHODS,
              (unsigned)(ULONG_PTR)record->original_get_surface_desc, desc_json,
              (unsigned)(ULONG_PTR)__builtin_return_address(0),
              (unsigned)(ULONG_PTR)__builtin_return_address(0), (long)result);
    trace_method_event("get_surface_desc", "active", details,
                       (DWORD)(ULONG_PTR)self,
                       (DWORD)(ULONG_PTR)record->original_get_surface_desc,
                       (DWORD)(ULONG_PTR)self);
    return result;
}

static BOOL census_surface_lock(LPDIRECTDRAWSURFACE7 surface, DDSURFACEDESC2 *desc)
{
    HRESULT result;
    if (!surface || !desc) return FALSE;
    ZeroMemory(desc, sizeof(*desc));
    desc->dwSize = sizeof(*desc);
    result = surface->lpVtbl->Lock(surface, NULL, desc,
                                   DDLOCK_WAIT | DDLOCK_READONLY, NULL);
    if (FAILED(result)) return FALSE;
    if (!desc->lpSurface || desc->lPitch <= 0 || desc->dwWidth == 0u ||
        desc->dwHeight == 0u) {
        surface->lpVtbl->Unlock(surface, desc->lpSurface);
        return FALSE;
    }
    return TRUE;
}

static void census_surface_unlock(LPDIRECTDRAWSURFACE7 surface,
                                  const DDSURFACEDESC2 *desc)
{
    if (surface && desc && desc->lpSurface)
        surface->lpVtbl->Unlock(surface, desc->lpSurface);
}

static void census_record_source_surface(LPDIRECTDRAWSURFACE7 source)
{
    DDSURFACEDESC2 desc;
    if (!source || !census_surface_lock(source, &desc)) return;
    g1_census_record_surface_buffer((DWORD)(ULONG_PTR)source,
        (DWORD)(ULONG_PTR)desc.lpSurface, (DWORD)desc.lPitch,
        desc.dwWidth, desc.dwHeight);
    census_surface_unlock(source, &desc);
}

static HRESULT WINAPI hook_blt(LPDIRECTDRAWSURFACE7 self, LPRECT dst,
                               LPDIRECTDRAWSURFACE7 source, LPRECT src,
                               DWORD flags, LPDDBLTFX fx)
{
    SurfaceRecord *record = surface_record(self);
    HRESULT result;
    char dst_json[160], src_json[160], base_details[850], details[1100];
    SurfaceRecord *source_surface = source ? surface_record(source) : NULL;
    RECT census_rect;
    DWORD census_left = 0u, census_top = 0u, census_right = 0u, census_bottom = 0u;
    BOOL census_blt_started = FALSE;
    BOOL census_window = g1_census_enabled() &&
        read_state(0x004ED818u) == g1_census_target_state();
    DDSURFACEDESC2 census_desc;
    G1OverlayBlt rect_blt;
    rect_blt.active = FALSE;
    if (!record || !record->original_blt) return DDERR_GENERIC;
    g1_screen_watch_on_surface_call(
        1u, (DWORD)(ULONG_PTR)__builtin_return_address(0), (DWORD)(ULONG_PTR)self,
        record->is_primary, (DWORD)(ULONG_PTR)source, (const LONG *)dst, (const LONG *)src,
        0u, 0u, flags);
    if (census_window && !record->is_primary) {
        g1_census_surface_blt_attempt(record->width, record->height);
        if (dst) census_rect = *dst;
        else {
            census_rect.left = 0; census_rect.top = 0;
            census_rect.right = (LONG)record->width;
            census_rect.bottom = (LONG)record->height;
        }
        if (census_rect.left >= 0 && census_rect.top >= 0 &&
            census_rect.right > census_rect.left && census_rect.bottom > census_rect.top) {
            census_left = (DWORD)census_rect.left;
            census_top = (DWORD)census_rect.top;
            census_right = (DWORD)census_rect.right;
            census_bottom = (DWORD)census_rect.bottom;
            if (census_surface_lock(self, &census_desc)) {
                census_blt_started = g1_census_surface_blt_begin(
                    (DWORD)(ULONG_PTR)census_desc.lpSurface, (DWORD)census_desc.lPitch,
                    census_desc.dwHeight, census_left, census_top, census_right,
                    census_bottom, (const BYTE *)census_desc.lpSurface);
                census_surface_unlock(self, &census_desc);
            } else {
                g1_census_surface_blt_skipped(3u);
            }
            census_record_source_surface(source);
        } else {
            g1_census_surface_blt_skipped(1u);
        }
    }
    if (g1_mirror2x_enabled() && read_state(0x004ED818u) == 3u && !record->is_primary)
        g1_mirror2x_overlay_rect_blt_begin(&rect_blt, self, dst, flags,
                                           record->width, record->height);
    result = record->original_blt(self, dst, source, src, flags, fx);
    g1_mirror2x_overlay_rect_blt_end(&rect_blt, self, result);
    if (census_blt_started && census_surface_lock(self, &census_desc)) {
        g1_census_surface_blt_end(
            (DWORD)(ULONG_PTR)census_desc.lpSurface, (DWORD)census_desc.lPitch,
            census_desc.dwHeight, census_left, census_top, census_right,
            census_bottom, (const BYTE *)census_desc.lpSurface);
        census_surface_unlock(self, &census_desc);
    }
    if (g1_census_enabled()) {
        g1_census_record_surface_write(
            "Blt", (DWORD)(ULONG_PTR)self, (DWORD)(ULONG_PTR)source,
            record->width, record->height,
            source_surface ? source_surface->width : 0u,
            source_surface ? source_surface->height : 0u,
            read_state(0x004ED818u), read_state(0x009B5210u),
            (DWORD)(ULONG_PTR)__builtin_return_address(0),
            record->is_primary, record->caps,
            source_surface ? source_surface->caps : 0u);
    }
    format_rect(dst_json, dst); format_rect(src_json, src);
    wsprintfA(base_details, ",\"destination_this\":\"0x%08X\",\"source\":\"0x%08X\",\"surface_interface\":\"IDirectDrawSurface7\",\"surface_vtable_methods\":%u,\"original_pointer\":\"0x%08X\",\"destination_rect\":%s,\"source_rect\":%s,\"flags\":%u,\"caller\":\"0x%08X\",\"return_address\":\"0x%08X\",\"present_tick\":%u,\"hresult\":%ld",
              (unsigned)(ULONG_PTR)self, (unsigned)(ULONG_PTR)source,
              (unsigned)TRACE_SURFACE_VTABLE_METHODS,
              (unsigned)(ULONG_PTR)record->original_blt, dst_json, src_json, (unsigned)flags,
              (unsigned)(ULONG_PTR)__builtin_return_address(0),
              (unsigned)(ULONG_PTR)__builtin_return_address(0), (unsigned)read_state(0x009B5210u), (long)result);
    if (record->is_primary) {
        wsprintfA(details, "%s,\"destination_is_primary\":1,\"source_desc_width\":%u,\"source_desc_height\":%u,\"converted\":0",
                  base_details, (unsigned)(source_surface ? source_surface->width : 0u),
                  (unsigned)(source_surface ? source_surface->height : 0u));
        trace_primary_method_event("blt", "active", details,
                                   (DWORD)(ULONG_PTR)self,
                                   (DWORD)(ULONG_PTR)record->original_blt,
                                   (DWORD)(ULONG_PTR)(source ? source : self),
                                   FALSE);
    } else {
        trace_method_event("blt", "active", base_details,
                           (DWORD)(ULONG_PTR)self,
                           (DWORD)(ULONG_PTR)record->original_blt,
                           (DWORD)(ULONG_PTR)(source ? source : self));
    }
    return result;
}

static HRESULT WINAPI hook_blt_fast(LPDIRECTDRAWSURFACE7 self, DWORD x, DWORD y,
                                    LPDIRECTDRAWSURFACE7 source, LPRECT src, DWORD flags)
{
    SurfaceRecord *record = surface_record(self);
    SurfaceRecord *source_record = source ? surface_record(source) : NULL;
    DWORD source_width = source_record ? source_record->width : 0u;
    DWORD source_height = source_record ? source_record->height : 0u;
    DWORD destination_width = record ? record->width : 0u;
    DWORD destination_height = record ? record->height : 0u;
    DDSURFACEDESC2 live_destination_desc;
    DDSURFACEDESC2 live_source_desc;
    BOOL live_destination_desc_known = FALSE;
    BOOL destination_is_primary = record ? record->is_primary : FALSE;
    BOOL live_source_desc_known = FALSE;
    DWORD destination_caps = record ? record->caps : 0u;
    DWORD source_caps = source_record ? source_record->caps : 0u;
    HRESULT result;
    char src_json[160], converted_dst_json[160], converted_src_json[160], details[7000];
    DWORD return_address = (DWORD)(ULONG_PTR)__builtin_return_address(0);
    BOOL stretch_opt_in = native_2x_stretch_enabled();
    BOOL converted = FALSE;
    BOOL mirror_attempted = FALSE;
    BOOL mirror_handled = FALSE;
    BOOL fallback_attempted = FALSE;
    BOOL fallback_succeeded = FALSE;
    BOOL mirror_gate_checked = FALSE;
    BOOL census_descriptor_probe = g1_census_enabled();
    DWORD present_started_ms;
    DWORD present_elapsed_ms;
    DWORD census_blt_left = 0u, census_blt_top = 0u;
    DWORD census_blt_right = 0u, census_blt_bottom = 0u;
    BOOL census_blt_started = FALSE;
    DDSURFACEDESC2 census_blt_desc;
    BOOL census_window = census_descriptor_probe &&
        read_state(0x004ED818u) == g1_census_target_state();
    G1PresentGateDecision gate_decision;
    G1MirrorPresentMetrics mirror_metrics;
    G1OverlayBlt overlay_blt;
    RECT effective_src;
    RECT destination_rect;
    DWORD blt_flags = 0u;
    ZeroMemory(&mirror_metrics, sizeof(mirror_metrics));
    overlay_blt.active = FALSE;
    if (!record || !record->original_blt_fast) return DDERR_GENERIC;
    g1_screen_watch_on_surface_call(
        2u, return_address, (DWORD)(ULONG_PTR)self, record->is_primary,
        (DWORD)(ULONG_PTR)source, NULL, (const LONG *)src, x, y, flags);
    present_started_ms = GetTickCount();
    if (census_descriptor_probe) {
        DDSURFACEDESC2 census_desc;
        ZeroMemory(&census_desc, sizeof(census_desc));
        census_desc.dwSize = sizeof(census_desc);
        if (SUCCEEDED(record->original_get_surface_desc(self, &census_desc))) {
            destination_width = census_desc.dwWidth;
            destination_height = census_desc.dwHeight;
            destination_caps = census_desc.ddsCaps.dwCaps;
            destination_is_primary = destination_is_primary ||
                (destination_caps & DDSCAPS_PRIMARYSURFACE) != 0;
        }
        if (source && source_record && source_record->original_get_surface_desc) {
            ZeroMemory(&census_desc, sizeof(census_desc));
            census_desc.dwSize = sizeof(census_desc);
            if (SUCCEEDED(source_record->original_get_surface_desc(source, &census_desc))) {
                source_width = census_desc.dwWidth;
                source_height = census_desc.dwHeight;
                source_caps = census_desc.ddsCaps.dwCaps;
            }
        }
    }
    if (mirror2x_trace_enabled()) {
        ZeroMemory(&live_destination_desc, sizeof(live_destination_desc));
        live_destination_desc.dwSize = sizeof(live_destination_desc);
        if (SUCCEEDED(self->lpVtbl->GetSurfaceDesc(self, &live_destination_desc))) {
            destination_width = live_destination_desc.dwWidth;
            destination_height = live_destination_desc.dwHeight;
            live_destination_desc_known = TRUE;
            destination_caps = live_destination_desc.ddsCaps.dwCaps;
            destination_is_primary = destination_is_primary ||
                (destination_caps & DDSCAPS_PRIMARYSURFACE) != 0;
        }
    }
    if (mirror2x_trace_enabled() && source) {
        ZeroMemory(&live_source_desc, sizeof(live_source_desc));
        live_source_desc.dwSize = sizeof(live_source_desc);
        if (SUCCEEDED(source->lpVtbl->GetSurfaceDesc(source, &live_source_desc))) {
            source_width = live_source_desc.dwWidth;
            source_height = live_source_desc.dwHeight;
            live_source_desc_known = TRUE;
            source_caps = live_source_desc.ddsCaps.dwCaps;
        }
    }
    ZeroMemory(&gate_decision, sizeof(gate_decision));
    if (mirror2x_trace_enabled()) {
        G1PresentGateInput gate_input;
        ZeroMemory(&gate_input, sizeof(gate_input));
        gate_input.destination_identity = (DWORD)(ULONG_PTR)self;
        gate_input.source_identity = (DWORD)(ULONG_PTR)source;
        gate_input.destination_caps = destination_caps;
        gate_input.source_caps = source_caps;
        gate_input.destination_width = destination_width;
        gate_input.destination_height = destination_height;
        gate_input.source_width = source_width;
        gate_input.source_height = source_height;
        gate_input.destination_descriptor_known = live_destination_desc_known;
        gate_input.source_descriptor_known = live_source_desc_known;
        gate_input.x = x;
        gate_input.y = y;
        gate_input.source_rect_present = src != NULL;
        if (src) {
            gate_input.source_left = src->left;
            gate_input.source_top = src->top;
            gate_input.source_right = src->right;
            gate_input.source_bottom = src->bottom;
        }
        gate_decision = g1_present_gate_decide(&gate_input);
        mirror_gate_checked = TRUE;
    }
    if (mirror_gate_checked && gate_decision.eligible) {
        effective_src.left = gate_decision.source_left;
        effective_src.top = gate_decision.source_top;
        effective_src.right = gate_decision.source_right;
        effective_src.bottom = gate_decision.source_bottom;
        destination_rect.left = gate_decision.destination_left;
        destination_rect.top = gate_decision.destination_top;
        destination_rect.right = gate_decision.destination_right;
        destination_rect.bottom = gate_decision.destination_bottom;
        mirror_attempted = TRUE;
        mirror_handled = TRUE;
        g1_mirror2x_scratch_bltfast_adopt(source, source_record != NULL);
        result = g1_mirror2x_copy_present(self, source, &effective_src,
                                          &destination_rect);
        if (FAILED(result)) {
            fallback_attempted = TRUE;
            blt_flags = DDBLT_WAIT;
            if (flags & DDBLTFAST_SRCCOLORKEY) blt_flags |= DDBLT_KEYSRC;
            result = record->original_blt(self, &destination_rect, source,
                                          &effective_src, blt_flags, NULL);
            fallback_succeeded = SUCCEEDED(result);
        } else {
            converted = TRUE;
        }
    } else if (stretch_opt_in && InterlockedCompareExchange(&g_native_2x_split_applied, 0, 0) &&
        record->is_primary && record->width == 1600u && record->height == 1200u &&
        source_record && source_record->descriptor_known && source_record->width >= 800u &&
        source_record->height == 600u && primary_present_call(return_address)) {
        effective_src = src ? *src : (RECT){0, 0, 800, 600};
        destination_rect.left = (LONG)(x * 2u);
        destination_rect.top = (LONG)(y * 2u);
        destination_rect.right = destination_rect.left +
            2 * (effective_src.right - effective_src.left);
        destination_rect.bottom = destination_rect.top +
            2 * (effective_src.bottom - effective_src.top);
        if (effective_src.left >= 0 && effective_src.top >= 0 &&
            effective_src.right > effective_src.left && effective_src.bottom > effective_src.top &&
            destination_rect.left >= 0 && destination_rect.top >= 0 &&
            destination_rect.right <= 1600 && destination_rect.bottom <= 1200) {
            blt_flags = DDBLT_WAIT;
            if (flags & DDBLTFAST_SRCCOLORKEY) blt_flags |= DDBLT_KEYSRC;
            result = record->original_blt(self, &destination_rect, source,
                                          &effective_src, blt_flags, NULL);
            converted = TRUE;
        }
    }
    if (!mirror_handled && !converted) {
        if (census_window && !destination_is_primary && source) {
            DWORD blt_width = src ? (src->right > src->left ? (DWORD)(src->right - src->left) : 0u)
                                  : source_width;
            DWORD blt_height = src ? (src->bottom > src->top ? (DWORD)(src->bottom - src->top) : 0u)
                                   : source_height;
            g1_census_surface_blt_attempt(destination_width, destination_height);
            if (blt_width && blt_height && blt_width <= 800u && blt_height <= 600u &&
                x <= 800u - blt_width && y <= 600u - blt_height &&
                census_surface_lock(self, &census_blt_desc)) {
                census_blt_left = x; census_blt_top = y;
                census_blt_right = x + blt_width;
                census_blt_bottom = y + blt_height;
                census_blt_started = g1_census_surface_blt_begin(
                    (DWORD)(ULONG_PTR)census_blt_desc.lpSurface,
                    (DWORD)census_blt_desc.lPitch, census_blt_desc.dwHeight,
                    census_blt_left, census_blt_top, census_blt_right,
                    census_blt_bottom, (const BYTE *)census_blt_desc.lpSurface);
                census_surface_unlock(self, &census_blt_desc);
                census_record_source_surface(source);
            } else {
                g1_census_surface_blt_skipped(2u);
            }
        }
        if (g1_mirror2x_enabled() && src && read_state(0x004ED818u) == 3u)
            g1_mirror2x_overlay_blt_begin(&overlay_blt, self, source, x, y, src,
                                          flags, destination_is_primary);
        result = record->original_blt_fast(self, x, y, source, src, flags);
        g1_mirror2x_overlay_blt_end(&overlay_blt, self, result);
        /* H-P35: the load-slot screen re-copies a whole 800x600 offscreen frame
         * (caller 0x00493CCB, NULL source rect, no colorkey) before the panel
         * writers run; the copy rewrites the same black, so the overlay diff
         * above never sees it. */
        if (g1_mirror2x_enabled() && SUCCEEDED(result) && !destination_is_primary &&
            return_address == 0x00493CCBu && !src && x == 0u && y == 0u &&
            !(flags & DDBLTFAST_SRCCOLORKEY) && source_width == 800u &&
            source_height == 600u && destination_width >= 800u &&
            destination_height == 600u && read_state(0x004ED818u) == 35u)
            g1_mirror2x_frame_blt_copy(self, source);
        if (census_blt_started && census_surface_lock(self, &census_blt_desc)) {
            g1_census_surface_blt_end(
                (DWORD)(ULONG_PTR)census_blt_desc.lpSurface,
                (DWORD)census_blt_desc.lPitch, census_blt_desc.dwHeight,
                census_blt_left, census_blt_top, census_blt_right,
                census_blt_bottom, (const BYTE *)census_blt_desc.lpSurface);
            census_surface_unlock(self, &census_blt_desc);
        }
    }
    g1_mirror2x_panel_transfer(self, source, x, y, src, result,
                               destination_is_primary);
    present_elapsed_ms = GetTickCount() - present_started_ms;
    if (destination_is_primary) record_primary_elapsed(present_elapsed_ms);
    if (g1_census_enabled()) {
        g1_census_record_surface_write(
            "BltFast", (DWORD)(ULONG_PTR)self, (DWORD)(ULONG_PTR)source,
            destination_width, destination_height, source_width, source_height,
            read_state(0x004ED818u), read_state(0x009B5210u),
            return_address, destination_is_primary, destination_caps, source_caps);
        if (destination_is_primary) {
            DDSURFACEDESC2 census_source_desc;
            DWORD census_source_buffer = 0u;
            DWORD census_source_pitch = 0u;
            BOOL census_source_locked = FALSE;
            HRESULT census_lock_result;
            ZeroMemory(&census_source_desc, sizeof(census_source_desc));
            census_source_desc.dwSize = sizeof(census_source_desc);
            census_lock_result = source ? source->lpVtbl->Lock(
                source, NULL, &census_source_desc,
                DDLOCK_WAIT | DDLOCK_READONLY, NULL) : DDERR_INVALIDOBJECT;
            if (SUCCEEDED(census_lock_result) && census_source_desc.lpSurface &&
                census_source_desc.lPitch > 0) {
                census_source_buffer = (DWORD)(ULONG_PTR)census_source_desc.lpSurface;
                census_source_pitch = (DWORD)census_source_desc.lPitch;
                census_source_locked = TRUE;
            }
            /* The boundary reads the unknown-pixel index histogram, so keep the
             * source locked until it returns. */
            g1_census_present_boundary(
                destination_width, destination_height, source_width, source_height,
                TRUE, read_state(0x004ED818u), read_state(0x009B5210u),
                (DWORD)(ULONG_PTR)source, census_source_buffer,
                census_source_pitch, census_source_locked);
            if (SUCCEEDED(census_lock_result))
                source->lpVtbl->Unlock(source, census_source_desc.lpSurface);
        }
    }
    format_rect(src_json, src);
    if (converted) {
        format_rect(converted_dst_json, &destination_rect);
        format_rect(converted_src_json, &effective_src);
    } else {
        lstrcpyA(converted_dst_json, "null");
        lstrcpyA(converted_src_json, "null");
    }
    wsprintfA(details, ",\"destination_this\":\"0x%08X\",\"source\":\"0x%08X\",\"surface_interface\":\"IDirectDrawSurface7\",\"surface_vtable_methods\":%u,\"original_pointer\":\"0x%08X\",\"x\":%u,\"y\":%u,\"source_rect\":%s,\"flags\":%u,\"caller\":\"0x%08X\",\"return_address\":\"0x%08X\",\"present_tick\":%u,\"hresult\":%ld,\"destination_is_primary\":%u,\"destination_desc_width\":%u,\"destination_desc_height\":%u,\"destination_caps\":%u,\"source_identity\":\"0x%08X\",\"source_caps\":%u,\"source_desc_known\":%u,\"source_desc_width\":%u,\"source_desc_height\":%u,\"converted\":%u,\"converted_destination_rect\":%s,\"converted_source_rect\":%s,\"converted_flags\":%u,\"original_method\":\"blt_fast\"",
              (unsigned)(ULONG_PTR)self, (unsigned)(ULONG_PTR)source,
              (unsigned)TRACE_SURFACE_VTABLE_METHODS,
              (unsigned)(ULONG_PTR)record->original_blt_fast, (unsigned)x, (unsigned)y,
              src_json, (unsigned)flags,
              (unsigned)return_address, (unsigned)return_address,
              (unsigned)read_state(0x009B5210u), (long)result,
              (unsigned)destination_is_primary,
              (unsigned)destination_width, (unsigned)destination_height,
              (unsigned)destination_caps, (unsigned)(ULONG_PTR)source,
              (unsigned)source_caps,
              (unsigned)live_source_desc_known,
              (unsigned)source_width, (unsigned)source_height,
              (unsigned)converted,
              converted_dst_json, converted_src_json,
              converted ? (unsigned)blt_flags : 0u);
    /* These fields make a rejected live surface-role decision observable even
     * when the legacy BltFast path is retained. */
    {
        char gate_details[256];
        wsprintfA(gate_details,
                  ",\"mirror_gate_checked\":%u,\"mirror_gate_eligible\":%u,\"mirror_gate_variant\":%u,\"mirror_gate_reject\":\"%s\",\"mirror_handled\":%u,\"fallback_attempted\":%u,\"fallback_succeeded\":%u",
                  (unsigned)mirror_gate_checked, (unsigned)gate_decision.eligible,
                  (unsigned)gate_decision.variant,
                  g1_present_reject_name(gate_decision.reject_reason),
                  (unsigned)mirror_handled, (unsigned)fallback_attempted,
                  (unsigned)fallback_succeeded);
        lstrcatA(details, gate_details);
    }
    {
        char timing_details[96];
        wsprintfA(timing_details, ",\"primary_present_elapsed_ms\":%u",
                  (unsigned)present_elapsed_ms);
        lstrcatA(details, timing_details);
    }
    if (mirror_attempted) {
        char mirror_details[7200];
        char scroll_details[96];
        LONG camera_x, camera_y;
        char mirror_destination_json[160];
        char mirror_source_json[160];
        char mirror_dump_details[260];
        char mirror_identity_details[980];
        char mirror_pack_details[1200];
        char mirror_cache_clip_details[260];
        LONG cache_clip_viewport[4];
        char mirror_perf_details[1100];
        char window_details[3200];
        DWORD window_attr = GetFileAttributesA(PERF_WINDOW_PATH);
        char window_id[96];
        g1_mirror2x_last_present_metrics(&mirror_metrics);
        format_rect(mirror_destination_json, &destination_rect);
        format_rect(mirror_source_json, &effective_src);
        wsprintfA(mirror_details,
                  ",\"destination_identity\":\"0x%08X\",\"source_identity\":\"0x%08X\",\"destination_caps\":%u,\"source_caps\":%u,\"source_rect\":%s,\"destination_rect\":%s,\"hresult\":%ld,\"fallback\":%u,\"success\":%u,\"source_width\":%u,\"source_height\":%u,\"source_stride\":%u,\"destination_width\":%u,\"destination_height\":%u,\"destination_stride\":%u,\"source_hash_fnv1a32\":\"0x%08X\",\"destination_hash_fnv1a32\":\"0x%08X\",\"nearest_matches\":%u,\"nearest_total\":%u,\"covered_pixels\":%u,\"stale_pixels\":%u",
                  (unsigned)(ULONG_PTR)self, (unsigned)(ULONG_PTR)source,
                  (unsigned)destination_caps,
                  (unsigned)source_caps,
                  mirror_source_json, mirror_destination_json, (long)result,
                  (unsigned)fallback_attempted, (unsigned)mirror_metrics.success,
                  (unsigned)mirror_metrics.source_width,
                  (unsigned)mirror_metrics.source_height,
                  (unsigned)mirror_metrics.source_stride,
                  (unsigned)mirror_metrics.destination_width,
                  (unsigned)mirror_metrics.destination_height,
                  (unsigned)mirror_metrics.destination_stride,
                  (unsigned)mirror_metrics.source_hash,
                  (unsigned)mirror_metrics.destination_hash,
                  (unsigned)mirror_metrics.nearest_matches,
                  (unsigned)mirror_metrics.nearest_total,
                  (unsigned)mirror_metrics.covered_pixels,
                  (unsigned)mirror_metrics.stale_pixels);
        wsprintfA(mirror_dump_details,
                  ",\"source_dump_hex\":\"%s\",\"destination_dump_hex\":\"%s\"",
                  mirror_metrics.source_dump, mirror_metrics.destination_dump);
        lstrcatA(mirror_details, mirror_dump_details);
        wsprintfA(mirror_identity_details,
                  ",\"identity_lookup_hits\":%u,\"identity_lookup_misses\":%u,\"identity_cache_inserts\":%u,\"identity_cache_hits\":%u,\"identity_cache_misses\":%u,\"identity_cache_refreshes\":%u,\"identity_negative_lookup_attempts\":%u,\"identity_negative_lookup_misses\":%u,\"identity_key_mismatches\":%u,\"hd_mask_inside_diff_subpixels\":%u,\"hd_mask_outside_diff_subpixels\":%u,\"full_frame_calls\":%u,\"bbox_calls\":%u,\"clipped_calls\":%u,\"cache_hit_compare_bytes\":%u,\"cache_insert_frame_bytes\":%u,\"cache_refresh_compare_bytes\":%u,\"clip_replay_mismatches\":%u,\"viewport_replays\":%u,\"viewport_field_mutations\":%u,\"viewport_restore_failures\":%u",
                  (unsigned)mirror_metrics.identity_lookup_hits,
                  (unsigned)mirror_metrics.identity_lookup_misses,
                  (unsigned)mirror_metrics.identity_cache_inserts,
                  (unsigned)mirror_metrics.identity_cache_hits,
                  (unsigned)mirror_metrics.identity_cache_misses,
                  (unsigned)mirror_metrics.identity_cache_refreshes,
                  (unsigned)mirror_metrics.identity_negative_lookup_attempts,
                  (unsigned)mirror_metrics.identity_negative_lookup_misses,
                  (unsigned)mirror_metrics.identity_key_mismatches,
                  (unsigned)mirror_metrics.hd_mask_inside_diff_subpixels,
                  (unsigned)mirror_metrics.hd_mask_outside_diff_subpixels,
                  (unsigned)g1_hd_asset_full_frame_calls(),
                  (unsigned)g1_hd_asset_bbox_calls(),
                  (unsigned)g1_hd_asset_clipped_calls(),
                  (unsigned)g1_hd_asset_cache_hit_bytes(),
                  (unsigned)g1_hd_asset_cache_insert_bytes(),
                  (unsigned)g1_hd_asset_cache_refresh_bytes(),
                  (unsigned)g1_hd_asset_clip_replay_mismatches(),
                  (unsigned)g1_mirror2x_viewport_replay_count(),
                  (unsigned)g1_mirror2x_viewport_field_mutations(),
                  (unsigned)g1_mirror2x_viewport_restore_failures());
        lstrcatA(mirror_details, mirror_identity_details);
        wsprintfA(mirror_pack_details,
                  ",\"hd_pack_enabled\":%u,\"hd_pack_sibling_duplicates\":%u,\"hd_source_guard_rejects\":%u,\"hd_pack_hits\":%u,\"hd_pack_misses\":%u,\"hd_pack_rejects\":%u,\"hd_pack_skipped_aux\":%u,\"hd_pack_lookup_blocks\":%u,\"hd_pack_lut_hits\":%u,\"hd_pack_lut_rejects\":%u,\"hd_pack_lut_key_color\":%u,\"hd_pack_lut_nonidentity\":%u,\"hd_pack_shade_hits\":%u,\"hd_pack_shade_rejects\":%u,\"hd_pack_shade_reject_aux\":%u,\"hd_pack_shade_reject_table\":%u,\"hd_pack_shade_reject_range\":%u,\"hd_pack_shade_reject_source\":%u,\"hd_pack_shade_reject_selfcheck\":%u,\"hd_pack_shade_reject_refresh\":%u,\"hd_pack_shade_selfcheck_pixels\":%u,\"hd_pack_shade_multi_keys\":%u,\"hd_pack_shade_key_color\":%u,\"hd_pack_shade_lut_bytes\":%u,\"hd_pack_fullscreen_hits\":%u,\"hd_pack_fullscreen_misses\":%u,\"hd_pack_fullscreen_rejects\":%u,\"hd_pack_fullscreen_loads\":%u",
                  (unsigned)g1_hd_asset_pack_enabled(),
                  (unsigned)g1_hd_asset_sibling_duplicates(),
                  (unsigned)g1_hd_asset_source_guard_rejects(),
                  (unsigned)g1_hd_asset_pack_hits(),
                  (unsigned)g1_hd_asset_pack_misses(),
                  (unsigned)g1_hd_asset_pack_rejects(),
                  (unsigned)g1_hd_asset_pack_skipped_aux(),
                  (unsigned)g1_hd_asset_pack_lookup_blocks(),
                  (unsigned)g1_hd_asset_pack_lut_hits(),
                  (unsigned)g1_hd_asset_pack_lut_rejects(),
                  (unsigned)g1_hd_asset_pack_lut_key_color(),
                  (unsigned)g1_hd_asset_pack_lut_nonidentity(),
                  (unsigned)g1_hd_asset_pack_shade_hits(),
                  (unsigned)g1_hd_asset_pack_shade_rejects(),
                  (unsigned)g1_hd_asset_pack_shade_rejects_by_reason(0u),
                  (unsigned)g1_hd_asset_pack_shade_rejects_by_reason(1u),
                  (unsigned)g1_hd_asset_pack_shade_rejects_by_reason(2u),
                  (unsigned)g1_hd_asset_pack_shade_rejects_by_reason(3u),
                  (unsigned)g1_hd_asset_pack_shade_rejects_by_reason(4u),
                  (unsigned)g1_hd_asset_pack_shade_rejects_by_reason(5u),
                  (unsigned)g1_hd_asset_pack_shade_selfcheck_pixels(),
                  (unsigned)g1_hd_asset_pack_shade_multi_keys(),
                  (unsigned)g1_hd_asset_pack_shade_key_color(),
                  (unsigned)g1_hd_asset_pack_shade_lut_bytes(),
                  (unsigned)g1_hd_asset_fullscreen_hits(),
                  (unsigned)g1_hd_asset_fullscreen_misses(),
                  (unsigned)g1_hd_asset_fullscreen_rejects(),
                  (unsigned)g1_hd_asset_fullscreen_loads());
        lstrcatA(mirror_details, mirror_pack_details);
        wsprintfA(mirror_pack_details,
                  ",\"hd_pack_pal_misses\":%u,\"hd_pal_digest\":%u,\"hd_pal_changes\":%u,\"hd_pal_family\":%u,\"hd_pack_flip_hits\":%u,\"hd_pack_flip_misses\":%u,\"hd_pack_flip_rejects\":%u,\"identity_cache_bytes\":%u,\"identity_evictions\":%u,\"hd_pack_ext_hits\":%u,\"hd_pack_ext_misses\":%u,\"hd_pack_ext_rejects\":%u",
                  (unsigned)g1_hd_asset_pack_pal_misses(),
                  (unsigned)g1_hd_asset_palette_digest(),
                  (unsigned)g1_hd_asset_palette_changes(),
                  (unsigned)g1_hd_asset_palette_family(),
                  (unsigned)g1_hd_asset_pack_flip_hits(),
                  (unsigned)g1_hd_asset_pack_flip_misses(),
                  (unsigned)g1_hd_asset_pack_flip_rejects(),
                  (unsigned)g1_hd_asset_identity_cache_bytes(),
                  (unsigned)g1_hd_asset_identity_evictions(),
                  (unsigned)g1_hd_asset_pack_ext_hits(),
                  (unsigned)g1_hd_asset_pack_ext_misses(),
                  (unsigned)g1_hd_asset_pack_ext_rejects());
        lstrcatA(mirror_details, mirror_pack_details);
        g1_mirror2x_cache_clip_first_viewport(cache_clip_viewport);
        wsprintfA(mirror_cache_clip_details,
                  ",\"cache_clip_attempts\":%u,\"cache_clip_verify_failures\":%u,\"cache_clip_first_viewport\":[%d,%d,%d,%d],\"cache_edge_unclipped_binds\":%u",
                  (unsigned)g1_mirror2x_cache_clip_attempts(),
                  (unsigned)g1_mirror2x_cache_clip_verify_failures(),
                  (int)cache_clip_viewport[0], (int)cache_clip_viewport[1],
                  (int)cache_clip_viewport[2], (int)cache_clip_viewport[3],
                  (unsigned)g1_mirror2x_cache_edge_unclipped_binds());
        lstrcatA(mirror_details, mirror_cache_clip_details);
        wsprintfA(mirror_perf_details,
                  ",\"elapsed_ms\":%u,\"primitive_reinvoke_elapsed_ms_total\":%u,\"primitive_reinvoke_elapsed_ms_max\":%u,\"primitive_reinvoke_count\":%u,\"primitive_install_success\":%u,\"primitive_call_count\":%u,\"primitive_covered_pixels_total\":%u,\"primitive_stale_pixels_total\":%u,\"hd_source\":\"%s\",\"identity_pixels\":%u,\"identity_keys\":%u,\"identity_invalid_sources\":%u,\"identity_events\":%u,\"scale2x_blocks\":%u,\"scale2x_subpixel_differences\":%u,\"scale2x_palette_violations\":%u,\"same_frame_oracle\":%u,\"terrain_rle_468c30_calls\":%u,\"terrain_shade_468cc0_calls\":%u,\"terrain_checker_468e10_calls\":%u,\"terrain_clip_468f00_calls\":%u,\"terrain_clip_shade_4690a0_calls\":%u,\"tinted_rle_466ea0_calls\":%u,\"tinted_rle_466ea0_covered\":%u,\"tinted_clip_rle_466540_calls\":%u,\"tinted_clip_rle_466540_covered\":%u",
                  (unsigned)mirror_metrics.elapsed_ms,
                  (unsigned)mirror_metrics.primitive_reinvoke_elapsed_ms_total,
                  (unsigned)mirror_metrics.primitive_reinvoke_elapsed_ms_max,
                  (unsigned)mirror_metrics.primitive_reinvoke_count,
                  (unsigned)g1_mirror2x_primitives_installed(),
                  (unsigned)g1_mirror2x_primitive_call_count(),
                  (unsigned)g1_mirror2x_primitive_covered_pixels(),
                  (unsigned)g1_mirror2x_stale_pixel_count(),
                  g1_hd_asset_source_name(),
                  (unsigned)mirror_metrics.identity_pixels,
                  (unsigned)mirror_metrics.identity_keys,
                  (unsigned)mirror_metrics.identity_invalid_sources,
                  (unsigned)mirror_metrics.identity_events,
                  (unsigned)mirror_metrics.scale2x_blocks,
                  (unsigned)mirror_metrics.scale2x_subpixel_differences,
                  (unsigned)mirror_metrics.scale2x_palette_violations,
                  (unsigned)(mirror_metrics.success &&
                             mirror_metrics.nearest_matches == mirror_metrics.nearest_total),
                  (unsigned)g1_mirror2x_terrain_writer_calls(0u),
                  (unsigned)g1_mirror2x_terrain_writer_calls(1u),
                  (unsigned)g1_mirror2x_terrain_writer_calls(2u),
                  (unsigned)g1_mirror2x_terrain_writer_calls(3u),
                  (unsigned)g1_mirror2x_terrain_writer_calls(4u),
                  (unsigned)g1_mirror2x_tinted_writer_calls(0u),
                  (unsigned)g1_mirror2x_tinted_writer_covered(0u),
                  (unsigned)g1_mirror2x_tinted_writer_calls(1u),
                  (unsigned)g1_mirror2x_tinted_writer_covered(1u));
        lstrcatA(mirror_details, mirror_perf_details);
        {
            char layer_details[640];
            wsprintfA(layer_details,
                      ",\"layer_compose_calls\":%u,\"layer_move_calls\":%u,\"layer_move_bytes\":%u,\"layer_move_unsupported\":%u,\"layer_transfer_calls\":%u,\"layer_covered_pixels\":%u,\"menu_copy_calls\":%u,\"menu_copy_pixels\":%u,\"menu_copy_hash_first\":%u,\"menu_copy_hash_last\":%u,\"menu_copy_hash_changes\":%u,\"partial_copy_calls\":%u,\"partial_copy_pixels\":%u,\"frame_copy_calls\":%u,\"frame_copy_pixels\":%u,\"frame_copy_rejects\":%u",
                      (unsigned)g1_mirror2x_layer_compose_calls(),
                      (unsigned)g1_mirror2x_layer_move_calls(),
                      (unsigned)g1_mirror2x_layer_move_bytes(),
                      (unsigned)g1_mirror2x_layer_move_unsupported(),
                      (unsigned)g1_mirror2x_layer_transfer_calls(),
                      (unsigned)g1_mirror2x_layer_covered_pixels(),
                      (unsigned)g1_mirror2x_menu_copy_calls(),
                      (unsigned)g1_mirror2x_menu_copy_pixels(),
                      (unsigned)g1_mirror2x_menu_copy_hash_first(),
                      (unsigned)g1_mirror2x_menu_copy_hash_last(),
                      (unsigned)g1_mirror2x_menu_copy_hash_changes(),
                      (unsigned)g1_mirror2x_partial_copy_calls(),
                      (unsigned)g1_mirror2x_partial_copy_pixels(),
                      (unsigned)g1_mirror2x_frame_copy_calls(),
                      (unsigned)g1_mirror2x_frame_copy_pixels(),
                      (unsigned)g1_mirror2x_frame_copy_rejects());
            lstrcatA(mirror_details, layer_details);
        }
        {
            char pause_details[160];
            wsprintfA(pause_details,
                      ",\"pause_snapshot_pixels\":%u,\"pause_restore_pixels\":%u,\"pause_restore_total\":%u",
                      (unsigned)mirror_metrics.pause_snapshot_pixels,
                      (unsigned)mirror_metrics.pause_restore_pixels,
                      (unsigned)g1_mirror2x_pause_restore_total());
            lstrcatA(mirror_details, pause_details);
        }
        {
            char readback_details[512];
            wsprintfA(readback_details,
                      ",\"primary_readback_calls\":%u,\"primary_readback_converted\":%u,\"primary_readback_rejects\":%u,\"primary_readback_dest_hash\":%u,\"primary_readback_source_hash\":%u,\"primary_readback_return_address\":%u",
                      (unsigned)g1_mirror2x_primary_readback_calls(),
                      (unsigned)g1_mirror2x_primary_readback_converted(),
                      (unsigned)g1_mirror2x_primary_readback_rejects(),
                      (unsigned)g1_mirror2x_primary_readback_dest_hash(),
                      (unsigned)g1_mirror2x_primary_readback_source_hash(),
                      (unsigned)g1_mirror2x_primary_readback_return_address());
            lstrcatA(mirror_details, readback_details);
        }
        {
            char bar_details[192];
            wsprintfA(bar_details,
                      ",\"bar_copy_468bb0_calls\":%u,\"bar_copy_468bb0_mirrored\":%u,\"bar_copy_468bb0_rejects\":%u,\"bar_copy_468bb0_pixels\":%u",
                      (unsigned)g1_mirror2x_bar_copy_calls(),
                      (unsigned)g1_mirror2x_bar_copy_mirrored(),
                      (unsigned)g1_mirror2x_bar_copy_rejects(),
                      (unsigned)g1_mirror2x_bar_copy_pixels());
            lstrcatA(mirror_details, bar_details);
        }
        {
            char compose_details[512];
            wsprintfA(compose_details,
                      ",\"briefing_compose_4d4620_calls\":%u,\"briefing_compose_4d4620_mirrored\":%u,\"briefing_compose_4d4620_rejects\":%u,\"briefing_compose_4d4620_pixels\":%u",
                      (unsigned)g1_mirror2x_briefing_compose_calls(),
                      (unsigned)g1_mirror2x_briefing_compose_mirrored(),
                      (unsigned)g1_mirror2x_briefing_compose_rejects(),
                      (unsigned)g1_mirror2x_briefing_compose_pixels());
            lstrcatA(mirror_details, compose_details);
            wsprintfA(compose_details,
                      ",\"briefing_compose_reject_gate\":%u,\"briefing_compose_reject_lock\":%u,\"briefing_compose_reject_surface\":%u,\"briefing_compose_last_dest\":%u,\"briefing_compose_last_geometry\":[%u,%u,%u,%u]",
                      (unsigned)g1_mirror2x_briefing_compose_reject_gate(),
                      (unsigned)g1_mirror2x_briefing_compose_reject_lock(),
                      (unsigned)g1_mirror2x_briefing_compose_reject_surface(),
                      (unsigned)g1_mirror2x_briefing_compose_last_dest(),
                      (unsigned)g1_mirror2x_briefing_compose_last_geometry(0u),
                      (unsigned)g1_mirror2x_briefing_compose_last_geometry(1u),
                      (unsigned)g1_mirror2x_briefing_compose_last_geometry(2u),
                      (unsigned)g1_mirror2x_briefing_compose_last_geometry(3u));
            lstrcatA(mirror_details, compose_details);
        }
        {
            char scratch_details[640];
            wsprintfA(scratch_details,
                      ",\"scratch_bltfast_calls\":%u,\"scratch_bltfast_recorded\":%u,\"scratch_bltfast_rejects\":%u,\"scratch_bltfast_flush_applied\":%u,\"scratch_bltfast_flush_pixels\":%u,\"scratch_bltfast_adopts\":%u,\"scratch_bltfast_adopt_skipped_record\":%u,\"scratch_bltfast_overflow\":%u,\"scratch_bltfast_other_site_calls\":%u",
                      (unsigned)g1_mirror2x_scratch_bltfast_calls(),
                      (unsigned)g1_mirror2x_scratch_bltfast_recorded(),
                      (unsigned)g1_mirror2x_scratch_bltfast_rejects(),
                      (unsigned)g1_mirror2x_scratch_bltfast_flush_applied(),
                      (unsigned)g1_mirror2x_scratch_bltfast_flush_pixels(),
                      (unsigned)g1_mirror2x_scratch_bltfast_adopts(),
                      (unsigned)g1_mirror2x_scratch_bltfast_adopt_skipped_record(),
                      (unsigned)g1_mirror2x_scratch_bltfast_overflow(),
                      (unsigned)g1_mirror2x_scratch_bltfast_other_site_calls());
            lstrcatA(mirror_details, scratch_details);
            wsprintfA(scratch_details,
                      ",\"scratch_bltfast_site_calls\":[%u,%u,%u,%u,%u,%u,%u]",
                      (unsigned)g1_mirror2x_scratch_bltfast_site_calls(0u),
                      (unsigned)g1_mirror2x_scratch_bltfast_site_calls(1u),
                      (unsigned)g1_mirror2x_scratch_bltfast_site_calls(2u),
                      (unsigned)g1_mirror2x_scratch_bltfast_site_calls(3u),
                      (unsigned)g1_mirror2x_scratch_bltfast_site_calls(4u),
                      (unsigned)g1_mirror2x_scratch_bltfast_site_calls(5u),
                      (unsigned)g1_mirror2x_scratch_bltfast_site_calls(6u));
            lstrcatA(mirror_details, scratch_details);
        }
        if (window_attr != INVALID_FILE_ATTRIBUTES && g1_perf_sections_enabled()) {
            G1PerfSectionStat stat[G1_PERF_SECTION_COUNT];
            char reinvoke_details[1400];
            if (!g_perf_window_was_active) g1_perf_sections_reset();
            g_perf_window_was_active = TRUE;
            g1_perf_sections_snapshot(stat);
            lstrcpyA(window_id, g_perf_window_id);
            wsprintfA(window_details,
                      ",\"perf_window_id\":\"%s\",\"perf_window_active\":true,\"perf_qpc_frequency\":%I64u,\"perf_sections\":{\"scratch_clear\":{\"count\":%I64u,\"total_qpc_ticks\":%I64u,\"max_qpc_ticks\":%I64u,\"bytes\":%I64u},\"original_call_a\":{\"count\":%I64u,\"total_qpc_ticks\":%I64u,\"max_qpc_ticks\":%I64u},\"original_call_b\":{\"count\":%I64u,\"total_qpc_ticks\":%I64u,\"max_qpc_ticks\":%I64u},\"hash_lookup\":{\"count\":%I64u,\"total_qpc_ticks\":%I64u,\"max_qpc_ticks\":%I64u,\"bytes\":%I64u},\"bind_compare\":{\"count\":%I64u,\"total_qpc_ticks\":%I64u,\"max_qpc_ticks\":%I64u,\"bytes\":%I64u},\"bind_copy_alloc\":{\"count\":%I64u,\"total_qpc_ticks\":%I64u,\"max_qpc_ticks\":%I64u,\"bytes\":%I64u},\"scale2x_build\":{\"count\":%I64u,\"total_qpc_ticks\":%I64u,\"max_qpc_ticks\":%I64u,\"bytes\":%I64u},\"compose\":{\"count\":%I64u,\"total_qpc_ticks\":%I64u,\"max_qpc_ticks\":%I64u,\"bytes\":%I64u},\"negative_probe\":{\"count\":%I64u,\"total_qpc_ticks\":%I64u,\"max_qpc_ticks\":%I64u}}",
                      window_id,
                      g1_perf_sections_frequency(),
                      stat[G1_PERF_SCRATCH_CLEAR].count,
                      stat[G1_PERF_SCRATCH_CLEAR].total_qpc_ticks,
                      stat[G1_PERF_SCRATCH_CLEAR].max_qpc_ticks,
                      stat[G1_PERF_SCRATCH_CLEAR].bytes,
                      stat[G1_PERF_ORIGINAL_A].count,
                      stat[G1_PERF_ORIGINAL_A].total_qpc_ticks,
                      stat[G1_PERF_ORIGINAL_A].max_qpc_ticks,
                      stat[G1_PERF_ORIGINAL_B].count,
                      stat[G1_PERF_ORIGINAL_B].total_qpc_ticks,
                      stat[G1_PERF_ORIGINAL_B].max_qpc_ticks,
                      stat[G1_PERF_HASH_LOOKUP].count,
                      stat[G1_PERF_HASH_LOOKUP].total_qpc_ticks,
                      stat[G1_PERF_HASH_LOOKUP].max_qpc_ticks,
                      stat[G1_PERF_HASH_LOOKUP].bytes,
                      stat[G1_PERF_BIND_COMPARE].count,
                      stat[G1_PERF_BIND_COMPARE].total_qpc_ticks,
                      stat[G1_PERF_BIND_COMPARE].max_qpc_ticks,
                      stat[G1_PERF_BIND_COMPARE].bytes,
                      stat[G1_PERF_BIND_COPY_ALLOC].count,
                      stat[G1_PERF_BIND_COPY_ALLOC].total_qpc_ticks,
                      stat[G1_PERF_BIND_COPY_ALLOC].max_qpc_ticks,
                      stat[G1_PERF_BIND_COPY_ALLOC].bytes,
                      stat[G1_PERF_SCALE2X_BUILD].count,
                      stat[G1_PERF_SCALE2X_BUILD].total_qpc_ticks,
                      stat[G1_PERF_SCALE2X_BUILD].max_qpc_ticks,
                      stat[G1_PERF_SCALE2X_BUILD].bytes,
                      stat[G1_PERF_COMPOSE].count,
                      stat[G1_PERF_COMPOSE].total_qpc_ticks,
                      stat[G1_PERF_COMPOSE].max_qpc_ticks,
                      stat[G1_PERF_COMPOSE].bytes,
                      stat[G1_PERF_NEGATIVE_PROBE].count,
                      stat[G1_PERF_NEGATIVE_PROBE].total_qpc_ticks,
                      stat[G1_PERF_NEGATIVE_PROBE].max_qpc_ticks);
            lstrcatA(mirror_details, window_details);
            wsprintfA(reinvoke_details,
                      ",\"perf_reinvoke_whole\":{\"tinted\":{\"count\":%I64u,\"total_qpc_ticks\":%I64u,\"max_qpc_ticks\":%I64u},\"tinted_clip\":{\"count\":%I64u,\"total_qpc_ticks\":%I64u,\"max_qpc_ticks\":%I64u},\"other\":{\"count\":%I64u,\"total_qpc_ticks\":%I64u,\"max_qpc_ticks\":%I64u}},\"perf_clip_prepare\":{\"count\":%I64u,\"total_qpc_ticks\":%I64u,\"max_qpc_ticks\":%I64u,\"bytes\":%I64u,\"temporary_alloc_free\":{\"count\":%I64u,\"total_qpc_ticks\":%I64u,\"max_qpc_ticks\":%I64u,\"requested_bytes\":%I64u},\"buffer_fill\":{\"count\":%I64u,\"total_qpc_ticks\":%I64u,\"max_qpc_ticks\":%I64u,\"bytes\":%I64u},\"mask_prepare\":{\"count\":%I64u,\"total_qpc_ticks\":%I64u,\"max_qpc_ticks\":%I64u,\"bytes\":%I64u}}",
                      stat[G1_PERF_WHOLE_TINTED].count,
                      stat[G1_PERF_WHOLE_TINTED].total_qpc_ticks,
                      stat[G1_PERF_WHOLE_TINTED].max_qpc_ticks,
                      stat[G1_PERF_WHOLE_TINTED_CLIP].count,
                      stat[G1_PERF_WHOLE_TINTED_CLIP].total_qpc_ticks,
                      stat[G1_PERF_WHOLE_TINTED_CLIP].max_qpc_ticks,
                      stat[G1_PERF_WHOLE_OTHER].count,
                      stat[G1_PERF_WHOLE_OTHER].total_qpc_ticks,
                      stat[G1_PERF_WHOLE_OTHER].max_qpc_ticks,
                      stat[G1_PERF_CLIP_PREPARE].count,
                      stat[G1_PERF_CLIP_PREPARE].total_qpc_ticks,
                      stat[G1_PERF_CLIP_PREPARE].max_qpc_ticks,
                      stat[G1_PERF_CLIP_PREPARE].bytes,
                      stat[G1_PERF_CLIP_TEMP_ALLOC_FREE].count,
                      stat[G1_PERF_CLIP_TEMP_ALLOC_FREE].total_qpc_ticks,
                      stat[G1_PERF_CLIP_TEMP_ALLOC_FREE].max_qpc_ticks,
                      stat[G1_PERF_CLIP_TEMP_ALLOC_FREE].bytes,
                      stat[G1_PERF_CLIP_BUFFER_FILL].count,
                      stat[G1_PERF_CLIP_BUFFER_FILL].total_qpc_ticks,
                      stat[G1_PERF_CLIP_BUFFER_FILL].max_qpc_ticks,
                      stat[G1_PERF_CLIP_BUFFER_FILL].bytes,
                      stat[G1_PERF_CLIP_MASK_PREPARE].count,
                      stat[G1_PERF_CLIP_MASK_PREPARE].total_qpc_ticks,
                      stat[G1_PERF_CLIP_MASK_PREPARE].max_qpc_ticks,
                      stat[G1_PERF_CLIP_MASK_PREPARE].bytes);
            lstrcatA(mirror_details, reinvoke_details);
        } else {
            g_perf_window_was_active = FALSE;
        }
        if (scroll_trace_enabled() && read_scroll_camera(&camera_x, &camera_y)) {
            DWORD sim_tick = *(volatile DWORD *)(ULONG_PTR)0x008924B8u;
            wsprintfA(scroll_details, ",\"camera\":[%d,%d],\"sim_tick\":%u",
                      camera_x, camera_y, (unsigned)sim_tick);
            lstrcatA(mirror_details, scroll_details);
        }
        {
            DWORD mirror_program_state = read_state(0x004ED818u);
            if (g_last_mirror_program_state == 0xFFFFFFFFu) {
                g_last_mirror_program_state = mirror_program_state;
            } else if (g_last_mirror_program_state != mirror_program_state) {
                char state_details[96];
                wsprintfA(state_details, ",\"from\":%u,\"to\":%u",
                          (unsigned)g_last_mirror_program_state,
                          (unsigned)mirror_program_state);
                trace_event("program_state_change", "active", state_details);
                g_last_mirror_program_state = mirror_program_state;
            }
            trace_event("mirror2x_present", mirror_metrics.success ? "active" : "failed",
                        mirror_details);
        }
        if (g1_mirror2x_s3_pattern_applied() && !g_s3_pattern_trace_emitted) {
            char s3_details[240];
            wsprintfA(s3_details,
                      ",\"sprite_id\":36,\"frame\":0,\"x\":10,\"y\":3,\"width\":20,\"height\":24,\"pattern_pixels\":%u",
                      (unsigned)g1_mirror2x_s3_pattern_pixel_count());
            trace_event("s3_pattern", "active", s3_details);
            g_s3_pattern_trace_emitted = TRUE;
        }
    }
    if (destination_is_primary) {
        trace_primary_method_event((converted || fallback_attempted) ? "blt" : "blt_fast", "active", details,
                                   (DWORD)(ULONG_PTR)self,
                                   (converted || fallback_attempted) ? (DWORD)(ULONG_PTR)record->original_blt
                                                                     : (DWORD)(ULONG_PTR)record->original_blt_fast,
                                   (DWORD)(ULONG_PTR)(source ? source : self),
                                   converted);
    } else {
        trace_method_event("blt_fast", "active", details,
                           (DWORD)(ULONG_PTR)self,
                           (DWORD)(ULONG_PTR)record->original_blt_fast,
                           (DWORD)(ULONG_PTR)(source ? source : self));
    }
    return result;
}

static HRESULT WINAPI hook_flip(LPDIRECTDRAWSURFACE7 self,
                                LPDIRECTDRAWSURFACE7 target, DWORD flags)
{
    SurfaceRecord *record = surface_record(self);
    HRESULT result;
    char details[650];
    if (!record || !record->original_flip) return DDERR_GENERIC;
    result = record->original_flip(self, target, flags);
    wsprintfA(details, ",\"destination_this\":\"0x%08X\",\"target\":\"0x%08X\",\"surface_interface\":\"IDirectDrawSurface7\",\"surface_vtable_methods\":%u,\"original_pointer\":\"0x%08X\",\"flags\":%u,\"caller\":\"0x%08X\",\"return_address\":\"0x%08X\",\"present_tick\":%u,\"hresult\":%ld",
              (unsigned)(ULONG_PTR)self, (unsigned)(ULONG_PTR)target,
              (unsigned)TRACE_SURFACE_VTABLE_METHODS,
              (unsigned)(ULONG_PTR)record->original_flip, (unsigned)flags,
              (unsigned)(ULONG_PTR)__builtin_return_address(0),
              (unsigned)(ULONG_PTR)__builtin_return_address(0), (unsigned)read_state(0x009B5210u), (long)result);
    trace_method_event("flip", "active", details,
                       (DWORD)(ULONG_PTR)self,
                       (DWORD)(ULONG_PTR)record->original_flip,
                       (DWORD)(ULONG_PTR)(target ? target : self));
    return result;
}

static ULONG WINAPI hook_surface_release(LPDIRECTDRAWSURFACE7 self)
{
    SurfaceRecord *record = surface_record(self);
    ULONG result;
    G1SurfaceReleaseInput input;
    G1SurfaceReleaseDecision decision;
    IDirectDrawSurface7Vtbl *clone;
    char details[900];
    const char *install_status = "active";

    if (!record || !record->original_release) return 0;
    result = record->original_release(self);
    input.clone_release = record->clone_vtable
        ? (G1SurfaceMethodPointer)record->clone_vtable->Release : NULL;
    input.hook_release = (G1SurfaceMethodPointer)hook_surface_release;
    input.original_release = (G1SurfaceMethodPointer)record->original_release;
    input.release_result = (unsigned)result;
    decision = g1_surface_release_decide(&input);
    if (decision.reason != G1_SURFACE_REUSE_RELEASE_KEEP &&
        decision.reason != G1_SURFACE_REUSE_RELEASE_RETIRE) {
        g_trace_failed = 1;
        install_status = "failed";
    }
    wsprintfA(details,
              ",\"surface\":\"0x%08X\",\"surface_interface\":\"IDirectDrawSurface7\",\"surface_vtable_methods\":%u,\"original_pointer\":\"0x%08X\",\"release_result\":%u,\"lifetime_action\":\"%s\",\"reason_code\":%u,\"reason\":\"%s\",\"stored_release\":\"0x%08X\",\"hook_release\":\"0x%08X\",\"original_release\":\"0x%08X\",\"caller\":\"0x%08X\",\"return_address\":\"0x%08X\",\"present_tick\":%u",
              (unsigned)(ULONG_PTR)self, (unsigned)TRACE_SURFACE_VTABLE_METHODS,
              (unsigned)(ULONG_PTR)record->original_release, (unsigned)result,
              decision.reason == G1_SURFACE_REUSE_RELEASE_RETIRE ? "retire" : "keep",
              (unsigned)decision.reason, g1_surface_reuse_reason_name(decision.reason),
              (unsigned)(ULONG_PTR)(record->clone_vtable ? record->clone_vtable->Release : NULL),
              (unsigned)(ULONG_PTR)hook_surface_release,
              (unsigned)(ULONG_PTR)record->original_release,
              (unsigned)(ULONG_PTR)__builtin_return_address(0),
              (unsigned)(ULONG_PTR)__builtin_return_address(0),
              (unsigned)read_state(0x009B5210u));
    trace_method_event("surface_release", install_status, details,
                       (DWORD)(ULONG_PTR)self,
                       (DWORD)(ULONG_PTR)record->original_release,
                       (DWORD)(ULONG_PTR)self);
    if (decision.reason == G1_SURFACE_REUSE_RELEASE_RETIRE) {
        clone = record->clone_vtable;
        ZeroMemory(record, sizeof(*record));
        if (clone) HeapFree(GetProcessHeap(), 0, clone);
    }
    return result;
}

static HRESULT WINAPI hook_direct_draw_create_ex(GUID *guid, LPVOID *out,
                                                  REFIID iid, IUnknown *outer)
{
    HRESULT result;
    char details[1200];
    DDRecord *slot = NULL;
    DWORD i;
    if (!g_original_create_ex) return DDERR_GENERIC;
    if (InterlockedCompareExchange(&g_trace_guard, 1, 0) != 0)
        return g_original_create_ex(guid, out, iid, outer);
    result = g_original_create_ex(guid, out, iid, outer);
    wsprintfA(details, ",\"caller\":\"0x%08X\",\"return_address\":\"0x%08X\",\"iid\":\"%08X-%04X-%04X-%02X%02X-%02X%02X%02X%02X%02X%02X\",\"original_pointer\":\"0x%08X\",\"module_start\":\"0x%08X\",\"module_end\":\"0x%08X\",\"dd_vtable_methods\":%u,\"hresult\":%ld,\"dd_object\":\"0x%08X\"",
              (unsigned)(ULONG_PTR)__builtin_return_address(0), (unsigned)(ULONG_PTR)__builtin_return_address(0),
              iid ? (unsigned)iid->Data1 : 0u, iid ? iid->Data2 : 0u, iid ? iid->Data3 : 0u,
              iid ? iid->Data4[0] : 0u, iid ? iid->Data4[1] : 0u, iid ? iid->Data4[2] : 0u,
              iid ? iid->Data4[3] : 0u, iid ? iid->Data4[4] : 0u, iid ? iid->Data4[5] : 0u,
              iid ? iid->Data4[6] : 0u, iid ? iid->Data4[7] : 0u,
              (unsigned)(ULONG_PTR)g_original_create_ex,
              (unsigned)(ULONG_PTR)GetModuleHandleA("ddraw.dll"),
              (unsigned)(ULONG_PTR)module_end(GetModuleHandleA("ddraw.dll")),
              (unsigned)TRACE_DD_VTABLE_METHODS, (long)result,
              (unsigned)(ULONG_PTR)(out ? *out : NULL));
    trace_event("direct_draw_create_ex", "active", details);
    if (FAILED(result) || !out || !*out) {
        InterlockedExchange(&g_trace_guard, 0);
        return result;
    }
    /* dxwrapper loads native D3D9 lazily; defer the typed source-slot hook until
     * the first successful original DirectDrawCreateEx boundary. */
    final_d3d9_trace_on_direct_draw_create_ex();
    for (i = 0; i < TRACE_MAX_DD; ++i) if (!g_dd_records[i].object) { slot = &g_dd_records[i]; break; }
    if (!slot) {
        ++g_dropped_count;
        trace_overflow("dd_records");
        InterlockedExchange(&g_trace_guard, 0);
        return result;
    }
    {
        IDirectDraw7Vtbl *old_vtable = NULL;
        IDirectDraw7Vtbl *clone = NULL;
        LPDIRECTDRAW7 dd = (LPDIRECTDRAW7)*out;
        if (!clone_dd_vtable(dd, &clone, &old_vtable)) {
            g_trace_failed = 1;
            trace_event("install", "failed", ",\"stage\":\"dd_vtable\",\"reason\":\"clone_or_replace_failed\"");
        } else {
            slot->object = dd;
            slot->original_vtable = old_vtable;
            slot->clone_vtable = clone;
            slot->original_create_surface = old_vtable->CreateSurface;
            slot->original_set_display_mode = old_vtable->SetDisplayMode;
            slot->original_set_cooperative_level = old_vtable->SetCooperativeLevel;
            clone->CreateSurface = hook_create_surface;
            clone->SetDisplayMode = hook_set_display_mode;
            clone->SetCooperativeLevel = hook_set_cooperative_level;
            slot->installed = TRUE;
        }
    }
    InterlockedExchange(&g_trace_guard, 0);
    return result;
}

static BOOL verify_runtime_contract(void)
{
    BYTE *base = (BYTE *)(ULONG_PTR)EXE_BASE_EXPECTED;
    static const BYTE import_thunk[DIRECT_DRAW_IAT_THUNK_SIZE] = {0xFF, 0x25, 0x18, 0x50, 0x4E, 0x00};
    static const BYTE caller_bytes[5] = {0xE8, 0xBF, 0x35, 0x07, 0x00};
    static const BYTE mode_width[7] = {0xC7, 0x46, 0x04, 0x20, 0x03, 0x00, 0x00};
    static const BYTE mode_height[7] = {0xC7, 0x46, 0x08, 0x58, 0x02, 0x00, 0x00};
    static const BYTE mode_call[3] = {0xFF, 0x51, 0x54};
    DirectDrawImport import;
    if (sizeof(IDirectDraw7Vtbl) != TRACE_DD_VTABLE_METHODS * sizeof(void *) ||
        sizeof(IDirectDrawSurface7Vtbl) != TRACE_SURFACE_VTABLE_METHODS * sizeof(void *)) return FALSE;
    if (!bytes_equal(base + DIRECT_DRAW_IMPORT_THUNK - EXE_BASE_EXPECTED,
                     import_thunk, sizeof(import_thunk))) return FALSE;
    if (!find_ddraw_iat(&import)) return FALSE;
    if (!bytes_equal(base + 0x00464374u - EXE_BASE_EXPECTED, caller_bytes, sizeof(caller_bytes))) return FALSE;
    if (!bytes_equal(base + 0x00464502u - EXE_BASE_EXPECTED, mode_width, sizeof(mode_width))) return FALSE;
    if (!bytes_equal(base + 0x00464509u - EXE_BASE_EXPECTED, mode_height, sizeof(mode_height))) return FALSE;
    if (!bytes_equal(base + 0x0046457Au - EXE_BASE_EXPECTED, mode_call, sizeof(mode_call))) return FALSE;
    g_iat_slot = import.slot;
    g_iat_original = import.loader_target;
    return TRUE;
}

int g1_direct_draw_trace_install(void)
{
    char details[700];
    if (!env_enabled() && !g1_mirror2x_enabled() && !g1_census_enabled() &&
        !g1_state_snapshot_enabled()) return 1;
    g_trace_enabled = 1;
    load_run_id();
    open_log();
    open_log_fallback();
    if (g_trace_log == INVALID_HANDLE_VALUE && env_enabled()) { g_trace_failed = 1; return 0; }
    trace_event("install", "starting", ",\"stage\":\"open\"");
    if (!verify_runtime_contract()) {
        g_trace_failed = 1;
        trace_event("install", "failed", ",\"stage\":\"runtime_contract\",\"reason\":\"SHA-pinned import/mode guard failed\"");
        return 0;
    }
    if (g1_state_snapshot_enabled() && !g1_state_snapshot_install()) {
        g_trace_failed = 1;
        trace_event("install", "failed", ",\"stage\":\"g1_state_snapshot\",\"reason\":\"old_bytes_or_runtime_install_failed\"");
        return 0;
    }
    g_original_create_ex = (DirectDrawCreateExFn)(ULONG_PTR)DIRECT_DRAW_IMPORT_THUNK;
    {
        DWORD rel = (DWORD)(ULONG_PTR)hook_direct_draw_create_ex - (DIRECT_DRAW_CALL_SITE + 5u);
        if (!write_code_dword(DIRECT_DRAW_CALL_SITE + 1u, DIRECT_DRAW_CALL_REL32_ORIGINAL, rel)) {
            g_trace_failed = 1;
            g_original_create_ex = NULL;
            trace_event("install", "failed", ",\"stage\":\"call_site\",\"reason\":\"call patch failed or old bytes changed\"");
            return 0;
        }
        g_call_site_patched = 1;
    }
    g_trace_installed = 1;
    wsprintfA(details, ",\"stage\":\"complete\",\"import_name\":\"DirectDrawCreateEx\",\"import_thunk\":\"0x004D7938\",\"iat_slot\":\"0x004E5018\",\"loader_target\":\"0x%08X\",\"original_pointer\":\"0x%08X\",\"module_start\":\"0x%08X\",\"module_end\":\"0x%08X\",\"dd_vtable_methods\":%u,\"surface_vtable_methods\":%u,\"event_limit\":%u,\"method_limit\":256,\"aggregate_limit\":64",
                (unsigned)(ULONG_PTR)g_iat_original, (unsigned)(ULONG_PTR)g_original_create_ex,
                (unsigned)(ULONG_PTR)GetModuleHandleA("ddraw.dll"),
                (unsigned)(ULONG_PTR)module_end(GetModuleHandleA("ddraw.dll")),
                (unsigned)TRACE_DD_VTABLE_METHODS, (unsigned)TRACE_SURFACE_VTABLE_METHODS,
                (unsigned)TRACE_MAX_EVENTS);
    trace_event("install", "active", details);
    open_input_log();
    if (scroll_trace_enabled() && !CreateThread(NULL, 0, scroll_trace_arm_thread,
                                                NULL, 0, NULL)) {
        trace_event("install", "failed",
                    ",\"stage\":\"scroll_receiver\",\"reason\":\"thread_create_failed\"");
        g_trace_failed = 1;
    }
    /* mirror2x input (GetCursorPos IAT + WndProc) is installed on the first
     * SetDisplayMode: an ASI renderer hooks GetCursorPos at SetCooperativeLevel,
     * and G1's /2 mapping must run on its already-mapped coordinates. */
    if (g1_mirror2x_enabled() && !g1_mirror2x_primitives_install()) {
        trace_event("install", "failed", ",\"stage\":\"mirror2x_primitives\",\"reason\":\"old_bytes_or_runtime_install_failed\"");
        g_trace_failed = 1;
    } else if (g1_mirror2x_enabled()) {
        trace_event("mirror2x_install", "active",
                    ",\"stage\":\"primitives\",\"primitive_install_success\":1,\"target_a\":\"0x00466D50\",\"target_b\":\"0x004664D0\",\"terrain_targets\":[\"0x00468C30\",\"0x00468CC0\",\"0x00468E10\",\"0x00468F00\",\"0x004690A0\"]");
    }
    if (g1_census_enabled() && !g1_census_install()) {
        trace_event("install", "failed",
                    ",\"stage\":\"g1_census\",\"reason\":\"old_bytes_or_runtime_install_failed\"");
    } else if (g1_census_enabled()) {
        trace_event("g1_census_install", "active",
                    ",\"stage\":\"writer_primitives\",\"measurement_only\":1");
    }
    return 1;
}

void g1_direct_draw_trace_detach(void)
{
    DWORD i;
    if (!g_trace_enabled) return;
    g1_state_snapshot_detach();
    if (g_call_site_patched && g_trace_installed) {
        DWORD rel = (DWORD)(ULONG_PTR)hook_direct_draw_create_ex - (DIRECT_DRAW_CALL_SITE + 5u);
        if (write_code_dword(DIRECT_DRAW_CALL_SITE + 1u, rel, DIRECT_DRAW_CALL_REL32_ORIGINAL))
            g_call_site_patched = 0;
    }
    for (i = 0; i < TRACE_MAX_SURFACES; ++i) {
        SurfaceRecord *record = &g_surface_records[i];
        if (record->object && record->clone_vtable) {
            if (IsBadReadPtr(record->object, sizeof(void *)) == 0) record->object->lpVtbl = record->original_vtable;
            HeapFree(GetProcessHeap(), 0, record->clone_vtable);
        }
    }
    for (i = 0; i < TRACE_MAX_DD; ++i) {
        DDRecord *record = &g_dd_records[i];
        if (record->object && record->clone_vtable) {
            if (IsBadReadPtr(record->object, sizeof(void *)) == 0) record->object->lpVtbl = record->original_vtable;
            HeapFree(GetProcessHeap(), 0, record->clone_vtable);
        }
    }
    if (g1_mirror2x_enabled()) {
        char mirror_details[14336];
        DWORD last_clip_writer, last_clip_origin_x, last_clip_origin_y;
        DWORD last_clip_width, last_clip_height, last_clip_x, last_clip_y;
        BYTE last_clip_screen_value, last_clip_replay_value;
        char mirror_count_details[512];
        char mirror_clip_details[640];
        g1_mirror2x_last_clip_mismatch(
            &last_clip_writer, &last_clip_origin_x, &last_clip_origin_y,
            &last_clip_width, &last_clip_height, &last_clip_x, &last_clip_y,
            &last_clip_screen_value, &last_clip_replay_value);
        wsprintfA(mirror_details,
                  ",\"primitive_install_success\":%u,\"primitive_call_count\":%u,\"covered_pixels\":%u,\"stale_pixels\":%u,\"present_count\":%u,\"panel_bound_transfers\":%u,\"panel_unbound_transfers\":%u,\"panel_lock_failures\":%u,\"panel_pointer_mismatches\":%u,\"panel_pitch_mismatches\":%u,\"panel_foreign_writer_calls\":%u,\"panel_frame_width\":%u,\"panel_frame_height\":%u,\"panel_frame_sha256\":\"%s\",\"panel_asset_key\":\"%s\",\"panel_hd_pack_loaded\":%u,\"panel_key_subpixels_emitted\":%u",
                  (unsigned)g1_mirror2x_primitives_installed(),
                  (unsigned)g1_mirror2x_primitive_call_count(),
                  (unsigned)g1_mirror2x_primitive_covered_pixels(),
                  (unsigned)g1_mirror2x_stale_pixel_count(),
                  (unsigned)g1_mirror2x_present_count(),
                  (unsigned)g1_mirror2x_panel_bound_transfers(),
                  (unsigned)g1_mirror2x_panel_unbound_transfers(),
                  (unsigned)g1_mirror2x_panel_lock_failures(),
                  (unsigned)g1_mirror2x_panel_pointer_mismatches(),
                  (unsigned)g1_mirror2x_panel_pitch_mismatches(),
                  (unsigned)g1_mirror2x_panel_foreign_writer_calls(),
                  (unsigned)g1_mirror2x_panel_frame_width(),
                  (unsigned)g1_mirror2x_panel_frame_height(),
                  g1_mirror2x_panel_frame_sha256(),
                  g1_mirror2x_panel_asset_key(),
                  (unsigned)g1_mirror2x_panel_hd_pack_loaded(),
                  (unsigned)g1_mirror2x_panel_key_subpixels_emitted());
        wsprintfA(mirror_count_details,
                  ",\"panel_transfer_copied\":%u,\"panel_transfer_key_preserved\":%u,\"panel_transfer_mismatch_cleared\":%u,\"tick\":%u,\"terrain_rle_468c30_calls\":%u,\"terrain_shade_468cc0_calls\":%u,\"terrain_checker_468e10_calls\":%u,\"terrain_clip_468f00_calls\":%u,\"terrain_clip_shade_4690a0_calls\":%u,\"tinted_rle_466ea0_calls\":%u,\"tinted_rle_466ea0_covered\":%u,\"tinted_clip_rle_466540_calls\":%u,\"tinted_clip_rle_466540_covered\":%u",
                  (unsigned)g1_mirror2x_panel_transfer_copied(),
                  (unsigned)g1_mirror2x_panel_transfer_key_preserved(),
                  (unsigned)g1_mirror2x_panel_transfer_mismatch_cleared(),
                  (unsigned)read_state(0x009B5210u),
                  (unsigned)g1_mirror2x_terrain_writer_calls(0u),
                  (unsigned)g1_mirror2x_terrain_writer_calls(1u),
                  (unsigned)g1_mirror2x_terrain_writer_calls(2u),
                  (unsigned)g1_mirror2x_terrain_writer_calls(3u),
                  (unsigned)g1_mirror2x_terrain_writer_calls(4u),
                  (unsigned)g1_mirror2x_tinted_writer_calls(0u),
                  (unsigned)g1_mirror2x_tinted_writer_covered(0u),
                  (unsigned)g1_mirror2x_tinted_writer_calls(1u),
                  (unsigned)g1_mirror2x_tinted_writer_covered(1u));
        wsprintfA(mirror_clip_details,
                  ",\"writer_a_clip_mismatches\":%u,\"writer_b_clip_mismatches\":%u,\"terrain_rle_clip_mismatches\":%u,\"terrain_shade_clip_mismatches\":%u,\"terrain_checker_clip_mismatches\":%u,\"terrain_clip_clip_mismatches\":%u,\"terrain_clip_shade_clip_mismatches\":%u,\"last_clip_mismatch_writer\":\"0x%08X\",\"last_clip_mismatch_origin\":[%u,%u],\"last_clip_mismatch_size\":[%u,%u],\"last_clip_mismatch_pixel\":[%u,%u],\"last_clip_mismatch_values\":[%u,%u]",
                  (unsigned)g1_mirror2x_writer_clip_mismatches(0u),
                  (unsigned)g1_mirror2x_writer_clip_mismatches(1u),
                  (unsigned)g1_mirror2x_writer_clip_mismatches(2u),
                  (unsigned)g1_mirror2x_writer_clip_mismatches(3u),
                  (unsigned)g1_mirror2x_writer_clip_mismatches(4u),
                  (unsigned)g1_mirror2x_writer_clip_mismatches(5u),
                  (unsigned)g1_mirror2x_writer_clip_mismatches(6u),
                  (unsigned)last_clip_writer,
                  (unsigned)last_clip_origin_x,
                  (unsigned)last_clip_origin_y,
                  (unsigned)last_clip_width,
                  (unsigned)last_clip_height,
                  (unsigned)last_clip_x,
                  (unsigned)last_clip_y,
                  (unsigned)last_clip_screen_value,
                  (unsigned)last_clip_replay_value);
        lstrcatA(mirror_details, mirror_count_details);
        lstrcatA(mirror_details, mirror_clip_details);
        {
            char layer_details[240];
            wsprintfA(layer_details,
                      ",\"layer_compose_calls\":%u,\"layer_move_calls\":%u,\"layer_move_bytes\":%u,\"layer_move_unsupported\":%u,\"layer_transfer_calls\":%u,\"layer_covered_pixels\":%u",
                      (unsigned)g1_mirror2x_layer_compose_calls(),
                      (unsigned)g1_mirror2x_layer_move_calls(),
                      (unsigned)g1_mirror2x_layer_move_bytes(),
                      (unsigned)g1_mirror2x_layer_move_unsupported(),
                      (unsigned)g1_mirror2x_layer_transfer_calls(),
                      (unsigned)g1_mirror2x_layer_covered_pixels());
            lstrcatA(mirror_details, layer_details);
        }
        {
            char overlay_details[160];
            wsprintfA(overlay_details,
                      ",\"overlay_blt_mirrored_calls\":%u,\"overlay_blt_mirrored_pixels\":%u,\"overlay_blt_rejects\":%u",
                      (unsigned)g1_mirror2x_overlay_blt_mirrored_calls(),
                      (unsigned)g1_mirror2x_overlay_blt_mirrored_pixels(),
                      (unsigned)g1_mirror2x_overlay_blt_rejects());
            lstrcatA(mirror_details, overlay_details);
        }
        {
            char rect_blt_details[960];
            wsprintfA(rect_blt_details,
                      ",\"overlay_rect_blt_invocations\":%u,\"overlay_rect_blt_mirrored_calls\":%u,\"overlay_rect_blt_mirrored_pixels\":%u,\"overlay_rect_blt_changed_calls\":%u,\"overlay_rect_blt_clipped_calls\":%u,\"overlay_rect_blt_keysrc_calls\":%u,\"overlay_rect_blt_colorfill_calls\":%u,\"overlay_rect_blt_reject_bounds\":%u,\"overlay_rect_blt_reject_size\":%u,\"overlay_rect_blt_reject_lock\":%u,\"overlay_rect_blt_reject_target\":%u,\"overlay_rect_blt_reject_result\":%u,\"overlay_rect_blt_heal_presents\":%u,\"overlay_rect_blt_heal_pixels\":%u,\"overlay_rect_blt_heal2_presents\":%u,\"overlay_rect_blt_heal2_pixels\":%u,\"overlay_rect_blt_heal2_skipped\":%u",
                      (unsigned)g1_mirror2x_overlay_rect_blt_invocations(),
                      (unsigned)g1_mirror2x_overlay_rect_blt_mirrored_calls(),
                      (unsigned)g1_mirror2x_overlay_rect_blt_mirrored_pixels(),
                      (unsigned)g1_mirror2x_overlay_rect_blt_changed_calls(),
                      (unsigned)g1_mirror2x_overlay_rect_blt_clipped_calls(),
                      (unsigned)g1_mirror2x_overlay_rect_blt_keysrc_calls(),
                      (unsigned)g1_mirror2x_overlay_rect_blt_colorfill_calls(),
                      (unsigned)g1_mirror2x_overlay_rect_blt_reject_bounds(),
                      (unsigned)g1_mirror2x_overlay_rect_blt_reject_size(),
                      (unsigned)g1_mirror2x_overlay_rect_blt_reject_lock(),
                      (unsigned)g1_mirror2x_overlay_rect_blt_reject_target(),
                      (unsigned)g1_mirror2x_overlay_rect_blt_reject_result(),
                      (unsigned)g1_mirror2x_overlay_rect_blt_heal_presents(),
                      (unsigned)g1_mirror2x_overlay_rect_blt_heal_pixels(),
                      (unsigned)g1_mirror2x_overlay_rect_blt_heal2_presents(),
                      (unsigned)g1_mirror2x_overlay_rect_blt_heal2_pixels(),
                      (unsigned)g1_mirror2x_overlay_rect_blt_heal2_skipped());
            lstrcatA(mirror_details, rect_blt_details);
        }
        {
            char rect_fill_details[320];
            wsprintfA(rect_fill_details,
                      ",\"rect_fill_466070_invocations\":%u,\"rect_fill_466070_mirrored_calls\":%u,\"rect_fill_466070_mirrored_pixels\":%u,\"rect_fill_466070_reject_target\":%u,\"rect_fill_466070_reject_size\":%u,\"rect_fill_466070_reject_guard\":%u",
                      (unsigned)g1_mirror2x_rect_fill_invocations(),
                      (unsigned)g1_mirror2x_rect_fill_mirrored_calls(),
                      (unsigned)g1_mirror2x_rect_fill_mirrored_pixels(),
                      (unsigned)g1_mirror2x_rect_fill_reject_target(),
                      (unsigned)g1_mirror2x_rect_fill_reject_size(),
                      (unsigned)g1_mirror2x_rect_fill_reject_guard());
            lstrcatA(mirror_details, rect_fill_details);
        }
        {
            char cache_fill_details[256];
            wsprintfA(cache_fill_details,
                      ",\"cache_fill_465FC0_invocations\":%u,\"cache_fill_465FC0_mirrored_calls\":%u,\"cache_fill_465FC0_mirrored_pixels\":%u,\"cache_fill_465FC0_reject_target\":%u,\"cache_fill_465FC0_unsupported\":%u",
                      (unsigned)g1_mirror2x_cache_fill_invocations(),
                      (unsigned)g1_mirror2x_cache_fill_mirrored_calls(),
                      (unsigned)g1_mirror2x_cache_fill_mirrored_pixels(),
                      (unsigned)g1_mirror2x_cache_fill_reject_target(),
                      (unsigned)g1_mirror2x_cache_fill_unsupported());
            lstrcatA(mirror_details, cache_fill_details);
        }
        {
            char rect_border_details[320];
            wsprintfA(rect_border_details,
                      ",\"rect_border_465B30_invocations\":%u,\"rect_border_465B30_mirrored_calls\":%u,\"rect_border_465B30_mirrored_pixels\":%u,\"rect_border_465B30_reject_target\":%u,\"rect_border_465B30_reject_size\":%u,\"rect_border_465B30_reject_guard\":%u",
                      (unsigned)g1_mirror2x_rect_border_invocations(),
                      (unsigned)g1_mirror2x_rect_border_mirrored_calls(),
                      (unsigned)g1_mirror2x_rect_border_mirrored_pixels(),
                      (unsigned)g1_mirror2x_rect_border_reject_target(),
                      (unsigned)g1_mirror2x_rect_border_reject_size(),
                      (unsigned)g1_mirror2x_rect_border_reject_guard());
            lstrcatA(mirror_details, rect_border_details);
        }
        {
            char rect_border7_details[320];
            wsprintfA(rect_border7_details,
                      ",\"rect_border7_465CA0_invocations\":%u,\"rect_border7_465CA0_mirrored_calls\":%u,\"rect_border7_465CA0_mirrored_pixels\":%u,\"rect_border7_465CA0_reject_target\":%u,\"rect_border7_465CA0_reject_size\":%u,\"rect_border7_465CA0_reject_guard\":%u",
                      (unsigned)g1_mirror2x_rect_border7_invocations(),
                      (unsigned)g1_mirror2x_rect_border7_mirrored_calls(),
                      (unsigned)g1_mirror2x_rect_border7_mirrored_pixels(),
                      (unsigned)g1_mirror2x_rect_border7_reject_target(),
                      (unsigned)g1_mirror2x_rect_border7_reject_size(),
                      (unsigned)g1_mirror2x_rect_border7_reject_guard());
            lstrcatA(mirror_details, rect_border7_details);
        }
        {
            char line_details[320];
            wsprintfA(line_details,
                      ",\"line_4659B0_invocations\":%u,\"line_4659B0_mirrored_calls\":%u,\"line_4659B0_mirrored_pixels\":%u,\"line_4659B0_reject_target\":%u,\"line_4659B0_reject_size\":%u,\"line_4659B0_reject_guard\":%u",
                      (unsigned)g1_mirror2x_line_invocations(),
                      (unsigned)g1_mirror2x_line_mirrored_calls(),
                      (unsigned)g1_mirror2x_line_mirrored_pixels(),
                      (unsigned)g1_mirror2x_line_reject_target(),
                      (unsigned)g1_mirror2x_line_reject_size(),
                      (unsigned)g1_mirror2x_line_reject_guard());
            lstrcatA(mirror_details, line_details);
        }
        {
            char rect_solid_details[420];
            wsprintfA(rect_solid_details,
                      ",\"rect_solid_465E80_invocations\":%u,\"rect_solid_465E80_mirrored_calls\":%u,\"rect_solid_465E80_mirrored_pixels\":%u,\"rect_solid_465E80_reject_target\":%u,\"rect_solid_465E80_reject_bounds\":%u,\"rect_solid_465E80_reject_size\":%u,\"rect_solid_465E80_reject_guard\":%u,\"rect_solid_465E80_ybound\":%u,\"rect_solid_465E80_wide_calls\":%u",
                      (unsigned)g1_mirror2x_rect_solid_invocations(),
                      (unsigned)g1_mirror2x_rect_solid_mirrored_calls(),
                      (unsigned)g1_mirror2x_rect_solid_mirrored_pixels(),
                      (unsigned)g1_mirror2x_rect_solid_reject_target(),
                      (unsigned)g1_mirror2x_rect_solid_reject_bounds(),
                      (unsigned)g1_mirror2x_rect_solid_reject_size(),
                      (unsigned)g1_mirror2x_rect_solid_reject_guard(),
                      (unsigned)g1_mirror2x_rect_solid_ybound(),
                      (unsigned)g1_mirror2x_rect_solid_wide_calls());
            lstrcatA(mirror_details, rect_solid_details);
        }
        {
            char flip_rle_details[520];
            wsprintfA(flip_rle_details,
                      ",\"flip_rle_466B50_invocations\":%u,\"flip_rle_466B50_mirrored_calls\":%u,\"flip_rle_466B50_mirrored_pixels\":%u,\"flip_rle_466B50_reject_target\":%u,\"flip_rle_466B50_reject_size\":%u,\"flip_rle_466B50_reject_guard\":%u,\"flip_rle_466B50_reject_bounds\":%u,\"flip_rle_466B50_clipped_calls\":%u,\"flip_rle_466B50_wrap_calls\":%u,\"flip_rle_466B50_keyed_calls\":%u,\"flip_rle_466B50_key_fallbacks\":%u",
                      (unsigned)g1_mirror2x_flip_rle_invocations(),
                      (unsigned)g1_mirror2x_flip_rle_mirrored_calls(),
                      (unsigned)g1_mirror2x_flip_rle_mirrored_pixels(),
                      (unsigned)g1_mirror2x_flip_rle_reject_target(),
                      (unsigned)g1_mirror2x_flip_rle_reject_size(),
                      (unsigned)g1_mirror2x_flip_rle_reject_guard(),
                      (unsigned)g1_mirror2x_flip_rle_reject_bounds(),
                      (unsigned)g1_mirror2x_flip_rle_clipped_calls(),
                      (unsigned)g1_mirror2x_flip_rle_wrap_calls(),
                      (unsigned)g1_mirror2x_flip_rle_keyed_calls(),
                      (unsigned)g1_mirror2x_flip_rle_key_fallbacks());
            lstrcatA(mirror_details, flip_rle_details);
        }
        {
            char keyed_copy_details[640];
            wsprintfA(keyed_copy_details,
                      ",\"keyed_copy_466480_invocations\":%u,\"keyed_copy_466480_mirrored_calls\":%u,\"keyed_copy_466480_mirrored_pixels\":%u,\"keyed_copy_466480_changed_calls\":%u,\"keyed_copy_466480_clipped_calls\":%u,\"keyed_copy_466480_reject_target\":%u,\"keyed_copy_466480_reject_bounds\":%u,\"keyed_copy_466480_reject_size\":%u,\"keyed_copy_466480_reject_guard\":%u",
                      (unsigned)g1_mirror2x_keyed_copy_invocations(),
                      (unsigned)g1_mirror2x_keyed_copy_mirrored_calls(),
                      (unsigned)g1_mirror2x_keyed_copy_mirrored_pixels(),
                      (unsigned)g1_mirror2x_keyed_copy_changed_calls(),
                      (unsigned)g1_mirror2x_keyed_copy_clipped_calls(),
                      (unsigned)g1_mirror2x_keyed_copy_reject_target(),
                      (unsigned)g1_mirror2x_keyed_copy_reject_bounds(),
                      (unsigned)g1_mirror2x_keyed_copy_reject_size(),
                      (unsigned)g1_mirror2x_keyed_copy_reject_guard());
            lstrcatA(mirror_details, keyed_copy_details);
        }
        {
            char blend_rle_details[360];
            wsprintfA(blend_rle_details,
                      ",\"blend_4672E0_invocations\":%u,\"blend_4672E0_mirrored_calls\":%u,\"blend_4672E0_mirrored_pixels\":%u,\"blend_4672E0_changed_calls\":%u,\"blend_4672E0_reject_target\":%u,\"blend_4672E0_reject_bounds\":%u,\"blend_4672E0_reject_size\":%u,\"blend_4672E0_reject_guard\":%u",
                      (unsigned)g1_mirror2x_blend_rle_invocations(),
                      (unsigned)g1_mirror2x_blend_rle_mirrored_calls(),
                      (unsigned)g1_mirror2x_blend_rle_mirrored_pixels(),
                      (unsigned)g1_mirror2x_blend_rle_changed_calls(),
                      (unsigned)g1_mirror2x_blend_rle_reject_target(),
                      (unsigned)g1_mirror2x_blend_rle_reject_bounds(),
                      (unsigned)g1_mirror2x_blend_rle_reject_size(),
                      (unsigned)g1_mirror2x_blend_rle_reject_guard());
            lstrcatA(mirror_details, blend_rle_details);
            char blend_key_details[360];
            wsprintfA(blend_key_details,
                      ",\"blend_4672E0_keyed_calls\":%u,\"blend_4672E0_keyed_pixels\":%u,\"blend_4672E0_key_fallbacks\":%u,\"blend_4672E0_selfcheck_mismatches\":%u,\"blend_4672E0_selfcheck_pixels\":%u,\"hd_pack_blend_hits\":%u,\"hd_pack_blend_misses\":%u,\"hd_pack_blend_rejects\":%u",
                      (unsigned)g1_mirror2x_blend_rle_keyed_calls(),
                      (unsigned)g1_mirror2x_blend_rle_keyed_pixels(),
                      (unsigned)g1_mirror2x_blend_rle_key_fallbacks(),
                      (unsigned)g1_mirror2x_blend_rle_selfcheck_mismatches(),
                      (unsigned)g1_mirror2x_blend_rle_selfcheck_pixels(),
                      (unsigned)g1_hd_asset_pack_blend_hits(),
                      (unsigned)g1_hd_asset_pack_blend_misses(),
                      (unsigned)g1_hd_asset_pack_blend_rejects());
            lstrcatA(mirror_details, blend_key_details);
        }
        {
            char blend_wrle_details[400];
            wsprintfA(blend_wrle_details,
                      ",\"blend_467580_invocations\":%u,\"blend_467580_mirrored_calls\":%u,\"blend_467580_mirrored_pixels\":%u,\"blend_467580_changed_calls\":%u,\"blend_467580_clipped_calls\":%u,\"blend_467580_reject_target\":%u,\"blend_467580_reject_bounds\":%u,\"blend_467580_reject_size\":%u,\"blend_467580_reject_guard\":%u",
                      (unsigned)g1_mirror2x_blend_wrle_invocations(),
                      (unsigned)g1_mirror2x_blend_wrle_mirrored_calls(),
                      (unsigned)g1_mirror2x_blend_wrle_mirrored_pixels(),
                      (unsigned)g1_mirror2x_blend_wrle_changed_calls(),
                      (unsigned)g1_mirror2x_blend_wrle_clipped_calls(),
                      (unsigned)g1_mirror2x_blend_wrle_reject_target(),
                      (unsigned)g1_mirror2x_blend_wrle_reject_bounds(),
                      (unsigned)g1_mirror2x_blend_wrle_reject_size(),
                      (unsigned)g1_mirror2x_blend_wrle_reject_guard());
            lstrcatA(mirror_details, blend_wrle_details);
            char blend_wrle_key_details[260];
            wsprintfA(blend_wrle_key_details,
                      ",\"blend_467580_keyed_calls\":%u,\"blend_467580_keyed_pixels\":%u,\"blend_467580_key_fallbacks\":%u,\"blend_467580_selfcheck_mismatches\":%u,\"blend_467580_selfcheck_pixels\":%u",
                      (unsigned)g1_mirror2x_blend_wrle_keyed_calls(),
                      (unsigned)g1_mirror2x_blend_wrle_keyed_pixels(),
                      (unsigned)g1_mirror2x_blend_wrle_key_fallbacks(),
                      (unsigned)g1_mirror2x_blend_wrle_selfcheck_mismatches(),
                      (unsigned)g1_mirror2x_blend_wrle_selfcheck_pixels());
            lstrcatA(mirror_details, blend_wrle_key_details);
            char blend_clip_details[480];
            wsprintfA(blend_clip_details,
                      ",\"blend_467B00_invocations\":%u,\"blend_467B00_mirrored_calls\":%u,\"blend_467B00_mirrored_pixels\":%u,\"blend_467B00_changed_calls\":%u,\"blend_467B00_clipped_calls\":%u,\"blend_467B00_reject_target\":%u,\"blend_467B00_reject_bounds\":%u,\"blend_467B00_reject_size\":%u,\"blend_467B00_reject_guard\":%u,\"blend_467B00_band_calls\":%u",
                      (unsigned)g1_mirror2x_blend_clip_invocations(),
                      (unsigned)g1_mirror2x_blend_clip_mirrored_calls(),
                      (unsigned)g1_mirror2x_blend_clip_mirrored_pixels(),
                      (unsigned)g1_mirror2x_blend_clip_changed_calls(),
                      (unsigned)g1_mirror2x_blend_clip_clipped_calls(),
                      (unsigned)g1_mirror2x_blend_clip_reject_target(),
                      (unsigned)g1_mirror2x_blend_clip_reject_bounds(),
                      (unsigned)g1_mirror2x_blend_clip_reject_size(),
                      (unsigned)g1_mirror2x_blend_clip_reject_guard(),
                      (unsigned)g1_mirror2x_blend_clip_band_calls());
            lstrcatA(mirror_details, blend_clip_details);
            char blend_clip_key_details[340];
            wsprintfA(blend_clip_key_details,
                      ",\"blend_467B00_keyed_calls\":%u,\"blend_467B00_keyed_pixels\":%u,\"blend_467B00_key_fallbacks\":%u,\"blend_467B00_selfcheck_mismatches\":%u,\"blend_467B00_selfcheck_pixels\":%u,\"blend_467B00_key_clip_cut\":%u,\"blend_467B00_key_clip_empty\":%u",
                      (unsigned)g1_mirror2x_blend_clip_keyed_calls(),
                      (unsigned)g1_mirror2x_blend_clip_keyed_pixels(),
                      (unsigned)g1_mirror2x_blend_clip_key_fallbacks(),
                      (unsigned)g1_mirror2x_blend_clip_selfcheck_mismatches(),
                      (unsigned)g1_mirror2x_blend_clip_selfcheck_pixels(),
                      (unsigned)g1_mirror2x_blend_clip_key_clip_cut(),
                      (unsigned)g1_mirror2x_blend_clip_key_clip_empty());
            lstrcatA(mirror_details, blend_clip_key_details);
            char blend_skip_details[480];
            wsprintfA(blend_skip_details,
                      ",\"blend_4685C0_invocations\":%u,\"blend_4685C0_mirrored_calls\":%u,\"blend_4685C0_mirrored_pixels\":%u,\"blend_4685C0_changed_calls\":%u,\"blend_4685C0_clipped_calls\":%u,\"blend_4685C0_reject_target\":%u,\"blend_4685C0_reject_bounds\":%u,\"blend_4685C0_reject_size\":%u,\"blend_4685C0_reject_guard\":%u,\"blend_4685C0_band_calls\":%u",
                      (unsigned)g1_mirror2x_blend_skip_invocations(),
                      (unsigned)g1_mirror2x_blend_skip_mirrored_calls(),
                      (unsigned)g1_mirror2x_blend_skip_mirrored_pixels(),
                      (unsigned)g1_mirror2x_blend_skip_changed_calls(),
                      (unsigned)g1_mirror2x_blend_skip_clipped_calls(),
                      (unsigned)g1_mirror2x_blend_skip_reject_target(),
                      (unsigned)g1_mirror2x_blend_skip_reject_bounds(),
                      (unsigned)g1_mirror2x_blend_skip_reject_size(),
                      (unsigned)g1_mirror2x_blend_skip_reject_guard(),
                      (unsigned)g1_mirror2x_blend_skip_band_calls());
            lstrcatA(mirror_details, blend_skip_details);
            char blend_skip_key_details[380];
            wsprintfA(blend_skip_key_details,
                      ",\"blend_4685C0_keyed_calls\":%u,\"blend_4685C0_keyed_pixels\":%u,\"blend_4685C0_key_fallbacks\":%u,\"blend_4685C0_selfcheck_mismatches\":%u,\"blend_4685C0_selfcheck_pixels\":%u,\"blend_4685C0_key_clip_cut\":%u,\"blend_4685C0_key_clip_empty\":%u",
                      (unsigned)g1_mirror2x_blend_skip_keyed_calls(),
                      (unsigned)g1_mirror2x_blend_skip_keyed_pixels(),
                      (unsigned)g1_mirror2x_blend_skip_key_fallbacks(),
                      (unsigned)g1_mirror2x_blend_skip_selfcheck_mismatches(),
                      (unsigned)g1_mirror2x_blend_skip_selfcheck_pixels(),
                      (unsigned)g1_mirror2x_blend_skip_key_clip_cut(),
                      (unsigned)g1_mirror2x_blend_skip_key_clip_empty());
            lstrcatA(mirror_details, blend_skip_key_details);
            char blend_clip7_details[400];
            wsprintfA(blend_clip7_details,
                      ",\"blend_4678C0_invocations\":%u,\"blend_4678C0_mirrored_calls\":%u,\"blend_4678C0_mirrored_pixels\":%u,\"blend_4678C0_changed_calls\":%u,\"blend_4678C0_clipped_calls\":%u,\"blend_4678C0_reject_target\":%u,\"blend_4678C0_reject_bounds\":%u,\"blend_4678C0_reject_size\":%u,\"blend_4678C0_reject_guard\":%u",
                      (unsigned)g1_mirror2x_blend_clip7_invocations(),
                      (unsigned)g1_mirror2x_blend_clip7_mirrored_calls(),
                      (unsigned)g1_mirror2x_blend_clip7_mirrored_pixels(),
                      (unsigned)g1_mirror2x_blend_clip7_changed_calls(),
                      (unsigned)g1_mirror2x_blend_clip7_clipped_calls(),
                      (unsigned)g1_mirror2x_blend_clip7_reject_target(),
                      (unsigned)g1_mirror2x_blend_clip7_reject_bounds(),
                      (unsigned)g1_mirror2x_blend_clip7_reject_size(),
                      (unsigned)g1_mirror2x_blend_clip7_reject_guard());
            lstrcatA(mirror_details, blend_clip7_details);
            char blend_4678C0_key_details[480];
            wsprintfA(blend_4678C0_key_details,
                      ",\"blend_4678C0_keyed_calls\":%u,\"blend_4678C0_keyed_pixels\":%u,\"blend_4678C0_key_fallbacks\":%u,\"blend_4678C0_selfcheck_mismatches\":%u,\"blend_4678C0_selfcheck_pixels\":%u,\"blend_4678C0_key_clip_cut\":%u,\"blend_4678C0_key_clip_empty\":%u,\"blend_4678C0_key_level_rejects\":%u",
                      (unsigned)g1_mirror2x_blend_clip7_keyed_calls(),
                      (unsigned)g1_mirror2x_blend_clip7_keyed_pixels(),
                      (unsigned)g1_mirror2x_blend_clip7_key_fallbacks(),
                      (unsigned)g1_mirror2x_blend_clip7_selfcheck_mismatches(),
                      (unsigned)g1_mirror2x_blend_clip7_selfcheck_pixels(),
                      (unsigned)g1_mirror2x_blend_clip7_key_clip_cut(),
                      (unsigned)g1_mirror2x_blend_clip7_key_clip_empty(),
                      (unsigned)g1_mirror2x_blend_clip7_key_level_rejects());
            lstrcatA(mirror_details, blend_4678C0_key_details);
            char flip_blend_details[520];
            wsprintfA(flip_blend_details,
                      ",\"blend_467FD0_invocations\":%u,\"blend_467FD0_mirrored_calls\":%u,\"blend_467FD0_mirrored_pixels\":%u,\"blend_467FD0_changed_calls\":%u,\"blend_467FD0_clipped_calls\":%u,\"blend_467FD0_reject_target\":%u,\"blend_467FD0_reject_bounds\":%u,\"blend_467FD0_reject_size\":%u,\"blend_467FD0_reject_guard\":%u,\"blend_467FD0_wrap_calls\":%u",
                      (unsigned)g1_mirror2x_flip_blend_invocations(),
                      (unsigned)g1_mirror2x_flip_blend_mirrored_calls(),
                      (unsigned)g1_mirror2x_flip_blend_mirrored_pixels(),
                      (unsigned)g1_mirror2x_flip_blend_changed_calls(),
                      (unsigned)g1_mirror2x_flip_blend_clipped_calls(),
                      (unsigned)g1_mirror2x_flip_blend_reject_target(),
                      (unsigned)g1_mirror2x_flip_blend_reject_bounds(),
                      (unsigned)g1_mirror2x_flip_blend_reject_size(),
                      (unsigned)g1_mirror2x_flip_blend_reject_guard(),
                      (unsigned)g1_mirror2x_flip_blend_wrap_calls());
            lstrcatA(mirror_details, flip_blend_details);
            char flip_blend_key_details[360];
            wsprintfA(flip_blend_key_details,
                      ",\"blend_467FD0_keyed_calls\":%u,\"blend_467FD0_keyed_pixels\":%u,\"blend_467FD0_key_fallbacks\":%u,\"blend_467FD0_selfcheck_mismatches\":%u,\"blend_467FD0_selfcheck_pixels\":%u,\"blend_467FD0_key_wrap_mismatches\":%u",
                      (unsigned)g1_mirror2x_flip_blend_keyed_calls(),
                      (unsigned)g1_mirror2x_flip_blend_keyed_pixels(),
                      (unsigned)g1_mirror2x_flip_blend_key_fallbacks(),
                      (unsigned)g1_mirror2x_flip_blend_selfcheck_mismatches(),
                      (unsigned)g1_mirror2x_flip_blend_selfcheck_pixels(),
                      (unsigned)g1_mirror2x_flip_blend_key_wrap_mismatches());
            lstrcatA(mirror_details, flip_blend_key_details);
            char blend_flip7_details[400];
            wsprintfA(blend_flip7_details,
                      ",\"blend_468360_invocations\":%u,\"blend_468360_mirrored_calls\":%u,\"blend_468360_mirrored_pixels\":%u,\"blend_468360_changed_calls\":%u,\"blend_468360_clipped_calls\":%u,\"blend_468360_reject_target\":%u,\"blend_468360_reject_bounds\":%u,\"blend_468360_reject_size\":%u,\"blend_468360_reject_guard\":%u",
                      (unsigned)g1_mirror2x_blend_flip7_invocations(),
                      (unsigned)g1_mirror2x_blend_flip7_mirrored_calls(),
                      (unsigned)g1_mirror2x_blend_flip7_mirrored_pixels(),
                      (unsigned)g1_mirror2x_blend_flip7_changed_calls(),
                      (unsigned)g1_mirror2x_blend_flip7_clipped_calls(),
                      (unsigned)g1_mirror2x_blend_flip7_reject_target(),
                      (unsigned)g1_mirror2x_blend_flip7_reject_bounds(),
                      (unsigned)g1_mirror2x_blend_flip7_reject_size(),
                      (unsigned)g1_mirror2x_blend_flip7_reject_guard());
            lstrcatA(mirror_details, blend_flip7_details);
            char blend_468360_key_details[480];
            wsprintfA(blend_468360_key_details,
                      ",\"blend_468360_keyed_calls\":%u,\"blend_468360_keyed_pixels\":%u,\"blend_468360_key_fallbacks\":%u,\"blend_468360_selfcheck_mismatches\":%u,\"blend_468360_selfcheck_pixels\":%u,\"blend_468360_key_clip_cut\":%u,\"blend_468360_key_clip_empty\":%u,\"blend_468360_key_level_rejects\":%u",
                      (unsigned)g1_mirror2x_blend_flip7_keyed_calls(),
                      (unsigned)g1_mirror2x_blend_flip7_keyed_pixels(),
                      (unsigned)g1_mirror2x_blend_flip7_key_fallbacks(),
                      (unsigned)g1_mirror2x_blend_flip7_selfcheck_mismatches(),
                      (unsigned)g1_mirror2x_blend_flip7_selfcheck_pixels(),
                      (unsigned)g1_mirror2x_blend_flip7_key_clip_cut(),
                      (unsigned)g1_mirror2x_blend_flip7_key_clip_empty(),
                      (unsigned)g1_mirror2x_blend_flip7_key_level_rejects());
            lstrcatA(mirror_details, blend_468360_key_details);
            char flip_blend7_details[400];
            wsprintfA(flip_blend7_details,
                      ",\"blend_467E60_invocations\":%u,\"blend_467E60_mirrored_calls\":%u,\"blend_467E60_mirrored_pixels\":%u,\"blend_467E60_changed_calls\":%u,\"blend_467E60_reject_target\":%u,\"blend_467E60_reject_bounds\":%u,\"blend_467E60_reject_size\":%u,\"blend_467E60_reject_guard\":%u",
                      (unsigned)g1_mirror2x_flip_blend7_invocations(),
                      (unsigned)g1_mirror2x_flip_blend7_mirrored_calls(),
                      (unsigned)g1_mirror2x_flip_blend7_mirrored_pixels(),
                      (unsigned)g1_mirror2x_flip_blend7_changed_calls(),
                      (unsigned)g1_mirror2x_flip_blend7_reject_target(),
                      (unsigned)g1_mirror2x_flip_blend7_reject_bounds(),
                      (unsigned)g1_mirror2x_flip_blend7_reject_size(),
                      (unsigned)g1_mirror2x_flip_blend7_reject_guard());
            lstrcatA(mirror_details, flip_blend7_details);
            char flip_clip_details[560];
            wsprintfA(flip_clip_details,
                      ",\"flip_clip_466BE0_invocations\":%u,\"flip_clip_466BE0_mirrored_calls\":%u,\"flip_clip_466BE0_mirrored_pixels\":%u,\"flip_clip_466BE0_changed_calls\":%u,\"flip_clip_466BE0_clipped_calls\":%u,\"flip_clip_466BE0_wrap_calls\":%u,\"flip_clip_466BE0_reject_target\":%u,\"flip_clip_466BE0_reject_bounds\":%u,\"flip_clip_466BE0_reject_size\":%u,\"flip_clip_466BE0_reject_guard\":%u,\"flip_clip_466BE0_keyed_calls\":%u,\"flip_clip_466BE0_key_fallbacks\":%u",
                      (unsigned)g1_mirror2x_flip_clip_invocations(),
                      (unsigned)g1_mirror2x_flip_clip_mirrored_calls(),
                      (unsigned)g1_mirror2x_flip_clip_mirrored_pixels(),
                      (unsigned)g1_mirror2x_flip_clip_changed_calls(),
                      (unsigned)g1_mirror2x_flip_clip_clipped_calls(),
                      (unsigned)g1_mirror2x_flip_clip_wrap_calls(),
                      (unsigned)g1_mirror2x_flip_clip_reject_target(),
                      (unsigned)g1_mirror2x_flip_clip_reject_bounds(),
                      (unsigned)g1_mirror2x_flip_clip_reject_size(),
                      (unsigned)g1_mirror2x_flip_clip_reject_guard(),
                      (unsigned)g1_mirror2x_flip_clip_keyed_calls(),
                      (unsigned)g1_mirror2x_flip_clip_key_fallbacks());
            lstrcatA(mirror_details, flip_clip_details);
            char shade_rle_details[480];
            wsprintfA(shade_rle_details,
                      ",\"shade_4687F0_invocations\":%u,\"shade_4687F0_mirrored_calls\":%u,\"shade_4687F0_mirrored_pixels\":%u,\"shade_4687F0_changed_calls\":%u,\"shade_4687F0_clipped_calls\":%u,\"shade_4687F0_wrap_calls\":%u,\"shade_4687F0_reject_target\":%u,\"shade_4687F0_reject_bounds\":%u,\"shade_4687F0_reject_size\":%u,\"shade_4687F0_reject_guard\":%u",
                      (unsigned)g1_mirror2x_shade_rle_invocations(),
                      (unsigned)g1_mirror2x_shade_rle_mirrored_calls(),
                      (unsigned)g1_mirror2x_shade_rle_mirrored_pixels(),
                      (unsigned)g1_mirror2x_shade_rle_changed_calls(),
                      (unsigned)g1_mirror2x_shade_rle_clipped_calls(),
                      (unsigned)g1_mirror2x_shade_rle_wrap_calls(),
                      (unsigned)g1_mirror2x_shade_rle_reject_target(),
                      (unsigned)g1_mirror2x_shade_rle_reject_bounds(),
                      (unsigned)g1_mirror2x_shade_rle_reject_size(),
                      (unsigned)g1_mirror2x_shade_rle_reject_guard());
            lstrcatA(mirror_details, shade_rle_details);
            char shade_flip_details[480];
            wsprintfA(shade_flip_details,
                      ",\"shade_4689C0_invocations\":%u,\"shade_4689C0_mirrored_calls\":%u,\"shade_4689C0_mirrored_pixels\":%u,\"shade_4689C0_changed_calls\":%u,\"shade_4689C0_clipped_calls\":%u,\"shade_4689C0_wrap_calls\":%u,\"shade_4689C0_reject_target\":%u,\"shade_4689C0_reject_bounds\":%u,\"shade_4689C0_reject_size\":%u,\"shade_4689C0_reject_guard\":%u",
                      (unsigned)g1_mirror2x_shade_flip_invocations(),
                      (unsigned)g1_mirror2x_shade_flip_mirrored_calls(),
                      (unsigned)g1_mirror2x_shade_flip_mirrored_pixels(),
                      (unsigned)g1_mirror2x_shade_flip_changed_calls(),
                      (unsigned)g1_mirror2x_shade_flip_clipped_calls(),
                      (unsigned)g1_mirror2x_shade_flip_wrap_calls(),
                      (unsigned)g1_mirror2x_shade_flip_reject_target(),
                      (unsigned)g1_mirror2x_shade_flip_reject_bounds(),
                      (unsigned)g1_mirror2x_shade_flip_reject_size(),
                      (unsigned)g1_mirror2x_shade_flip_reject_guard());
            lstrcatA(mirror_details, shade_flip_details);
            char shade_clip_details[480];
            wsprintfA(shade_clip_details,
                      ",\"shade_468870_invocations\":%u,\"shade_468870_mirrored_calls\":%u,\"shade_468870_mirrored_pixels\":%u,\"shade_468870_changed_calls\":%u,\"shade_468870_clipped_calls\":%u,\"shade_468870_wrap_calls\":%u,\"shade_468870_reject_target\":%u,\"shade_468870_reject_bounds\":%u,\"shade_468870_reject_size\":%u,\"shade_468870_reject_guard\":%u",
                      (unsigned)g1_mirror2x_shade_clip_invocations(),
                      (unsigned)g1_mirror2x_shade_clip_mirrored_calls(),
                      (unsigned)g1_mirror2x_shade_clip_mirrored_pixels(),
                      (unsigned)g1_mirror2x_shade_clip_changed_calls(),
                      (unsigned)g1_mirror2x_shade_clip_clipped_calls(),
                      (unsigned)g1_mirror2x_shade_clip_wrap_calls(),
                      (unsigned)g1_mirror2x_shade_clip_reject_target(),
                      (unsigned)g1_mirror2x_shade_clip_reject_bounds(),
                      (unsigned)g1_mirror2x_shade_clip_reject_size(),
                      (unsigned)g1_mirror2x_shade_clip_reject_guard());
            lstrcatA(mirror_details, shade_clip_details);
        }
        {
            char drift_hook_details[520];
            wsprintfA(drift_hook_details,
                      ",\"drift_467410_installed\":%u,\"drift_467410_invocations\":%u,\"drift_467410_changed_calls\":%u,\"drift_4676D0_installed\":%u,\"drift_4676D0_invocations\":%u,\"drift_4676D0_changed_calls\":%u,\"drift_w_records\":%u,\"drift_unattributed\":[%u,%u,%u],\"blend_467410_mirrored_calls\":%u,\"blend_467410_mirrored_pixels\":%u,\"blend_467410_reject_size\":%u,\"blend_467410_reject_other\":%u",
                      (unsigned)g1_mirror2x_drift_410_installed(),
                      (unsigned)g1_mirror2x_blend_410_invocations(),
                      (unsigned)g1_mirror2x_blend_410_changed_calls(),
                      (unsigned)g1_mirror2x_drift_6d0_installed(),
                      (unsigned)g1_mirror2x_blend_6d0_invocations(),
                      (unsigned)g1_mirror2x_blend_6d0_changed_calls(),
                      (unsigned)g1_mirror2x_drift_w_records(),
                      (unsigned)g1_mirror2x_drift_unattributed(0u),
                      (unsigned)g1_mirror2x_drift_unattributed(1u),
                      (unsigned)g1_mirror2x_drift_unattributed(2u),
                      (unsigned)g1_mirror2x_blend_410_mirrored_calls(),
                      (unsigned)g1_mirror2x_blend_410_mirrored_pixels(),
                      (unsigned)g1_mirror2x_blend_410_reject_size(),
                      (unsigned)(g1_mirror2x_blend_410_reject_target() +
                                 g1_mirror2x_blend_410_reject_bounds() +
                                 g1_mirror2x_blend_410_reject_guard()));
            lstrcatA(mirror_details, drift_hook_details);
        }
        lstrcatA(mirror_details, ",\"s3_pattern_enabled\":");
        lstrcatA(mirror_details, g1_mirror2x_s3_pattern_enabled() ? "1" : "0");
        lstrcatA(mirror_details, ",\"s3_pattern_applied\":");
        lstrcatA(mirror_details, g1_mirror2x_s3_pattern_applied() ? "1" : "0");
        {
            char s3_detail[96];
            wsprintfA(s3_detail, ",\"s3_pattern_pixels\":%u",
                      (unsigned)g1_mirror2x_s3_pattern_pixel_count());
            lstrcatA(mirror_details, s3_detail);
        }
        trace_event("mirror2x_metrics", "active", mirror_details);
        {
            char textout_details[800];
            wsprintfA(textout_details,
                      ",\"textout_iat_invocations\":%u,\"textout_iat_mirrored_calls\":%u,\"textout_iat_mirrored_pixels\":%u,\"textout_iat_changed_calls\":%u,\"textout_iat_reject_target\":%u,\"textout_iat_reject_size\":%u,\"textout_iat_reject_guard\":%u,\"textout_iat_reject_align\":%u,\"textout_iat_install_mismatch\":%u,\"textout_iat_slot_installed\":%u,\"textout_iat_slot_restored\":%u,\"textout_iat_reject_target_ps5\":%u,\"textout_iat_reject_target_ps7\":%u,\"textout_iat_reject_target_other\":%u,\"textout_iat_reject_target_dc_screen\":%u,\"textout_iat_reject_target_dc_buffer\":%u,\"textout_iat_reject_target_dc_other\":%u,\"textout_iat_screen_dc_calls\":%u",
                      (unsigned)g1_mirror2x_textout_invocations(),
                      (unsigned)g1_mirror2x_textout_mirrored_calls(),
                      (unsigned)g1_mirror2x_textout_mirrored_pixels(),
                      (unsigned)g1_mirror2x_textout_changed_calls(),
                      (unsigned)g1_mirror2x_textout_reject_target(),
                      (unsigned)g1_mirror2x_textout_reject_size(),
                      (unsigned)g1_mirror2x_textout_reject_guard(),
                      (unsigned)g1_mirror2x_textout_reject_align(),
                      (unsigned)g1_mirror2x_textout_install_mismatch(),
                      (unsigned)g1_mirror2x_textout_slot_installed(),
                      (unsigned)g1_mirror2x_textout_slot_restored(),
                      (unsigned)g1_mirror2x_textout_reject_target_ps5(),
                      (unsigned)g1_mirror2x_textout_reject_target_ps7(),
                      (unsigned)g1_mirror2x_textout_reject_target_other(),
                      (unsigned)g1_mirror2x_textout_reject_target_dc_screen(),
                      (unsigned)g1_mirror2x_textout_reject_target_dc_buffer(),
                      (unsigned)g1_mirror2x_textout_reject_target_dc_other(),
                      (unsigned)g1_mirror2x_textout_screen_dc_calls());
            trace_event("textout_iat_metrics", "active", textout_details);
        }
        if (g1_mirror2x_ret_range_diag_enabled()) {
            char ret_range_details[160];
            wsprintfA(ret_range_details,
                      ",\"b_kills\":%u,\"b_idle\":%u,\"textout_kills\":%u,\"textout_idle\":%u",
                      (unsigned)g1_mirror2x_ret_diag_b_kills(),
                      (unsigned)g1_mirror2x_ret_diag_b_idle(),
                      (unsigned)g1_mirror2x_ret_diag_textout_kills(),
                      (unsigned)g1_mirror2x_ret_diag_textout_idle());
            trace_event("ret_range_diag", "active", ret_range_details);
        }
    }
    g1_census_detach();
    trace_emit_aggregates();
    trace_emit_perf_window_histogram();
    trace_emit_summary();
    g1_mirror2x_primitives_detach();
    if (g1_mirror2x_enabled()) {
        char restore_details[96];
        wsprintfA(restore_details, ",\"textout_iat_slot_restored\":%u",
                  (unsigned)g1_mirror2x_textout_slot_restored());
        trace_event("textout_iat_restore", "active", restore_details);
    }
    if (g_trace_log != INVALID_HANDLE_VALUE) {
        CloseHandle(g_trace_log);
        g_trace_log = INVALID_HANDLE_VALUE;
    }
    if (g_input_trace_log != INVALID_HANDLE_VALUE) {
        CloseHandle(g_input_trace_log);
        g_input_trace_log = INVALID_HANDLE_VALUE;
    }
    g_trace_enabled = 0;
}
