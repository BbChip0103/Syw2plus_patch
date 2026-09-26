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

#define TRACE_PATH "C:\\inmm_g1_present_trace.jsonl"
#define TRACE_ENV "SYW2_G1_PRESENT_TRACE"
#define TRACE_RUN_ENV "SYW2_G1_TRACE_RUN_ID"
#define TRACE_SCHEMA "g1-directdraw-trace-v1"
#define TRACE_MAX_METHOD 256u
#define TRACE_MAX_EVENTS 2048u
#define TRACE_MAX_DD 8u
#define TRACE_MAX_SURFACES 32u
#define TRACE_MAX_AGGREGATES 64u
#define TRACE_RESERVED_EVENTS 2u
#define TRACE_MAX_PRIMARY_PRESENT 2048u
#define TRACE_DD_VTABLE_METHODS 30u
#define TRACE_SURFACE_VTABLE_METHODS 49u
#define EXE_BASE_EXPECTED 0x00400000u
#define DIRECT_DRAW_IMPORT_THUNK 0x004D7938u
#define DIRECT_DRAW_IAT_SLOT 0x004E5018u
#define DIRECT_DRAW_IAT_THUNK_SIZE 6u
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
static DWORD g_overflow_emitted = 0;
static volatile LONG g_native_2x_split_applied = 0;
static char g_run_id[96] = "unknown";
static DirectDrawCreateExFn g_original_create_ex = NULL;
static void **g_iat_slot = NULL;
static void *g_iat_original = NULL;
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

static BOOL bytes_equal(const BYTE *left, const BYTE *right, DWORD size)
{
    DWORD i;
    for (i = 0; i < size; ++i) if (left[i] != right[i]) return FALSE;
    return TRUE;
}

static BOOL env_enabled(void)
{
    char value[8];
    DWORD size = GetEnvironmentVariableA(TRACE_ENV, value, sizeof(value));
    return size == 1 && value[0] == '1';
}

static BOOL native_2x_blit_enabled(void)
{
    char value[8];
    DWORD size = GetEnvironmentVariableA("SYW2_G1_NATIVE_2X_BLIT", value, sizeof(value));
    return size == 1 && value[0] == '1';
}

static BOOL native_2x_stretch_enabled(void)
{
    char value[8];
    DWORD size = GetEnvironmentVariableA("SYW2_G1_NATIVE_2X_STRETCH", value, sizeof(value));
    return size == 1 && value[0] == '1';
}

static BOOL primary_present_call(DWORD return_address)
{
    return return_address == NATIVE_2X_PRESENT_RETURN;
}

static void load_run_id(void)
{
    DWORD size = GetEnvironmentVariableA(TRACE_RUN_ENV, g_run_id, sizeof(g_run_id));
    if (size == 0 || size >= sizeof(g_run_id)) lstrcpyA(g_run_id, "unknown");
}

static void open_log(void)
{
    if (g_trace_log != INVALID_HANDLE_VALUE) return;
    g_trace_log = CreateFileA(TRACE_PATH, GENERIC_WRITE,
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
    char line[4096];
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
    /* Keep one event for the first overflow marker and one for summary. */
    if (lstrcmpA(event, "summary") != 0 &&
        g_event_count >= TRACE_MAX_EVENTS - TRACE_RESERVED_EVENTS) {
        ++g_dropped_count;
        g_trace_failed = 1;
        trace_overflow("event_limit");
        return;
    }
    if (!trace_event_raw(event, install_status, details, call_seq,
                         read_state(0x004ED818u), read_state(0x009B5210u))) {
        ++g_dropped_count;
        g_trace_failed = 1;
        trace_overflow("event_limit");
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
                                      DWORD original_pointer, DWORD present_identity)
{
    int index = method_index(event);
    DWORD call_seq = next_source_seq();
    DWORD program_state = read_state(0x004ED818u);
    DWORD tick = read_state(0x009B5210u);
    (void)object_identity;
    (void)original_pointer;
    (void)present_identity;
    ++g_primary_present_count;
    if (index >= 0) ++g_method_call_counts[index];
    if (index < 0 || g_event_count >= TRACE_MAX_EVENTS - TRACE_RESERVED_EVENTS ||
        !trace_event_raw(event, install_status, details, call_seq, program_state, tick)) {
        ++g_primary_present_dropped;
        ++g_method_dropped_counts[index >= 0 ? index : 0];
        ++g_dropped_count;
        g_trace_failed = 1;
        trace_overflow("primary_present");
        return;
    }
    ++g_method_detailed_counts[index];
}

static void trace_emit_aggregates(void)
{
    DWORD i;
    for (i = 0; i < TRACE_MAX_AGGREGATES; ++i) {
        TraceAggregate *entry = &g_aggregates[i];
        char details[900];
        if (!entry->used) continue;
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
    wsprintfA(details,
        ",\"event_count\":%u,\"dropped_count\":%u,\"source_call_count\":%u,\"aggregate_record_count\":%u,\"method_counts\":{"
        "\"set_display_mode\":{\"detailed_count\":%u,\"aggregated_count\":%u,\"dropped_count\":%u,\"total_count\":%u},"
        "\"create_surface\":{\"detailed_count\":%u,\"aggregated_count\":%u,\"dropped_count\":%u,\"total_count\":%u},"
        "\"get_surface_desc\":{\"detailed_count\":%u,\"aggregated_count\":%u,\"dropped_count\":%u,\"total_count\":%u},"
        "\"blt\":{\"detailed_count\":%u,\"aggregated_count\":%u,\"dropped_count\":%u,\"total_count\":%u},"
        "\"blt_fast\":{\"detailed_count\":%u,\"aggregated_count\":%u,\"dropped_count\":%u,\"total_count\":%u},"
        "\"flip\":{\"detailed_count\":%u,\"aggregated_count\":%u,\"dropped_count\":%u,\"total_count\":%u},"
        "\"surface_release\":{\"detailed_count\":%u,\"aggregated_count\":%u,\"dropped_count\":%u,\"total_count\":%u}},"
        "\"primary_present_count\":%u,\"primary_present_dropped\":%u,"
        "\"detach\":\"complete\",\"flush\":\"complete\"",
        (unsigned)g_event_count, (unsigned)g_dropped_count, (unsigned)g_source_seq,
        (unsigned)aggregate_record_count(),
        (unsigned)g_method_detailed_counts[0], (unsigned)g_method_aggregated_counts[0], (unsigned)g_method_dropped_counts[0], (unsigned)g_method_call_counts[0],
        (unsigned)g_method_detailed_counts[1], (unsigned)g_method_aggregated_counts[1], (unsigned)g_method_dropped_counts[1], (unsigned)g_method_call_counts[1],
        (unsigned)g_method_detailed_counts[2], (unsigned)g_method_aggregated_counts[2], (unsigned)g_method_dropped_counts[2], (unsigned)g_method_call_counts[2],
        (unsigned)g_method_detailed_counts[3], (unsigned)g_method_aggregated_counts[3], (unsigned)g_method_dropped_counts[3], (unsigned)g_method_call_counts[3],
        (unsigned)g_method_detailed_counts[4], (unsigned)g_method_aggregated_counts[4], (unsigned)g_method_dropped_counts[4], (unsigned)g_method_call_counts[4],
        (unsigned)g_method_detailed_counts[5], (unsigned)g_method_aggregated_counts[5], (unsigned)g_method_dropped_counts[5], (unsigned)g_method_call_counts[5],
        (unsigned)g_method_detailed_counts[6], (unsigned)g_method_aggregated_counts[6], (unsigned)g_method_dropped_counts[6], (unsigned)g_method_call_counts[6],
        (unsigned)g_primary_present_count, (unsigned)g_primary_present_dropped);
    trace_event("summary", g_trace_failed ? "failed" : "detached", details);
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
            if ((DWORD)(ULONG_PTR)ft->u1.Function < ddraw_start ||
                (DWORD)(ULONG_PTR)ft->u1.Function >= ddraw_stop) return FALSE;
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

static HRESULT WINAPI hook_blt(LPDIRECTDRAWSURFACE7 self, LPRECT dst,
                               LPDIRECTDRAWSURFACE7 source, LPRECT src,
                               DWORD flags, LPDDBLTFX fx)
{
    SurfaceRecord *record = surface_record(self);
    HRESULT result;
    char dst_json[160], src_json[160], base_details[850], details[1100];
    SurfaceRecord *source_surface = source ? surface_record(source) : NULL;
    if (!record || !record->original_blt) return DDERR_GENERIC;
    result = record->original_blt(self, dst, source, src, flags, fx);
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
                                   (DWORD)(ULONG_PTR)(source ? source : self));
    } else {
        trace_method_event("blt", "active", details,
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
    HRESULT result;
    char src_json[160], converted_dst_json[160], converted_src_json[160], details[1500];
    DWORD return_address = (DWORD)(ULONG_PTR)__builtin_return_address(0);
    BOOL stretch_opt_in = native_2x_stretch_enabled();
    BOOL converted = FALSE;
    RECT effective_src;
    RECT destination_rect;
    DWORD blt_flags;
    if (!record || !record->original_blt_fast) return DDERR_GENERIC;
    if (stretch_opt_in && InterlockedCompareExchange(&g_native_2x_split_applied, 0, 0) &&
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
    if (!converted) result = record->original_blt_fast(self, x, y, source, src, flags);
    format_rect(src_json, src);
    if (converted) {
        format_rect(converted_dst_json, &destination_rect);
        format_rect(converted_src_json, &effective_src);
    } else {
        lstrcpyA(converted_dst_json, "null");
        lstrcpyA(converted_src_json, "null");
    }
    wsprintfA(details, ",\"destination_this\":\"0x%08X\",\"source\":\"0x%08X\",\"surface_interface\":\"IDirectDrawSurface7\",\"surface_vtable_methods\":%u,\"original_pointer\":\"0x%08X\",\"x\":%u,\"y\":%u,\"source_rect\":%s,\"flags\":%u,\"caller\":\"0x%08X\",\"return_address\":\"0x%08X\",\"present_tick\":%u,\"hresult\":%ld,\"destination_is_primary\":%u,\"source_desc_width\":%u,\"source_desc_height\":%u,\"converted\":%u,\"converted_destination_rect\":%s,\"converted_source_rect\":%s,\"converted_flags\":%u,\"original_method\":\"blt_fast\"",
              (unsigned)(ULONG_PTR)self, (unsigned)(ULONG_PTR)source,
              (unsigned)TRACE_SURFACE_VTABLE_METHODS,
              (unsigned)(ULONG_PTR)record->original_blt_fast, (unsigned)x, (unsigned)y,
              src_json, (unsigned)flags,
              (unsigned)return_address, (unsigned)return_address,
              (unsigned)read_state(0x009B5210u), (long)result,
              (unsigned)record->is_primary,
              (unsigned)(source_record ? source_record->width : 0u),
              (unsigned)(source_record ? source_record->height : 0u),
              (unsigned)converted,
              converted_dst_json, converted_src_json,
              converted ? (unsigned)blt_flags : 0u);
    if (record->is_primary) {
        trace_primary_method_event(converted ? "blt" : "blt_fast", "active", details,
                                   (DWORD)(ULONG_PTR)self,
                                   converted ? (DWORD)(ULONG_PTR)record->original_blt
                                             : (DWORD)(ULONG_PTR)record->original_blt_fast,
                                   (DWORD)(ULONG_PTR)(source ? source : self));
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
            clone->CreateSurface = hook_create_surface;
            clone->SetDisplayMode = hook_set_display_mode;
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
    if (!env_enabled()) return 1;
    g_trace_enabled = 1;
    load_run_id();
    open_log();
    if (g_trace_log == INVALID_HANDLE_VALUE) { g_trace_failed = 1; return 0; }
    trace_event("install", "starting", ",\"stage\":\"open\"");
    if (!verify_runtime_contract()) {
        g_trace_failed = 1;
        trace_event("install", "failed", ",\"stage\":\"runtime_contract\",\"reason\":\"SHA-pinned import/mode guard failed\"");
        return 0;
    }
    g_original_create_ex = (DirectDrawCreateExFn)g_iat_original;
    {
        void *old = NULL;
        if (!write_pointer(g_iat_slot, g_iat_original, (void *)hook_direct_draw_create_ex, &old) || old != g_iat_original) {
            g_trace_failed = 1;
            g_original_create_ex = NULL;
            trace_event("install", "failed", ",\"stage\":\"iat\",\"reason\":\"slot patch failed or target changed; rollback attempted\"");
            return 0;
        }
    }
    g_trace_installed = 1;
    wsprintfA(details, ",\"stage\":\"complete\",\"import_name\":\"DirectDrawCreateEx\",\"import_thunk\":\"0x004D7938\",\"iat_slot\":\"0x004E5018\",\"loader_target\":\"0x%08X\",\"original_pointer\":\"0x%08X\",\"module_start\":\"0x%08X\",\"module_end\":\"0x%08X\",\"dd_vtable_methods\":%u,\"surface_vtable_methods\":%u,\"event_limit\":2048,\"method_limit\":256,\"aggregate_limit\":64",
                (unsigned)(ULONG_PTR)g_iat_original, (unsigned)(ULONG_PTR)g_original_create_ex,
                (unsigned)(ULONG_PTR)GetModuleHandleA("ddraw.dll"),
                (unsigned)(ULONG_PTR)module_end(GetModuleHandleA("ddraw.dll")),
                (unsigned)TRACE_DD_VTABLE_METHODS, (unsigned)TRACE_SURFACE_VTABLE_METHODS);
    trace_event("install", "active", details);
    return 1;
}

void g1_direct_draw_trace_detach(void)
{
    DWORD i;
    if (!g_trace_enabled) return;
    if (g_iat_slot && g_trace_installed) {
        DWORD old_protect = 0, restored = 0;
        if (VirtualProtect(g_iat_slot, sizeof(void *), PAGE_READWRITE, &old_protect)) {
            *g_iat_slot = g_iat_original;
            VirtualProtect(g_iat_slot, sizeof(void *), old_protect, &restored);
            FlushInstructionCache(GetCurrentProcess(), g_iat_slot, sizeof(void *));
        }
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
    trace_emit_aggregates();
    trace_emit_summary();
    if (g_trace_log != INVALID_HANDLE_VALUE) {
        CloseHandle(g_trace_log);
        g_trace_log = INVALID_HANDLE_VALUE;
    }
    g_trace_enabled = 0;
}
