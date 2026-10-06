/* Opt-in, read-only snapshots taken after the pinned simulation update call returns. */
#include "g1_state_snapshot.h"

#define SNAPSHOT_TICKS_ENV "SYW2_G1_STATE_SNAPSHOT_TICKS"
#define SNAPSHOT_DIR_ENV "SYW2_G1_STATE_SNAPSHOT_DIR"
#define SNAPSHOT_RUN_ENV "SYW2_G1_STATE_SNAPSHOT_RUN_ID"
#define SNAPSHOT_TRACE_PATH "C:\\g1_state_snapshot_trace.jsonl"
#define GAME_BASE 0x00400000u
#define TICK_ADDRESS 0x008924B8u
#define PLAYER_ADDRESS 0x00956770u
#define PLAYER_SIZE (8u * 0x3ABCu)
#define EXISTS_ADDRESS 0x008990C8u
#define EXISTS_SIZE (1200u * 2u)
#define UNIT_ADDRESS 0x0066B790u
#define UNIT_SIZE (1200u * 0x758u)
#define PS_ADDRESS 0x004ED818u
#define CAMERA_ADDRESS 0x00B42D7Cu
#define SNAPSHOT_MAX_TICKS 8u
#define THREAD_CONTEXTS 16u
#define SNAPSHOT_HEADER_SIZE 128u
#define SNAPSHOT_PAYLOAD_SIZE (4u + 4u + 8u + PLAYER_SIZE + EXISTS_SIZE + UNIT_SIZE)

void g1_state_snapshot_before(DWORD callsite);
void g1_state_snapshot_after(DWORD callsite);

typedef struct __attribute__((packed)) {
    char magic[8];
    DWORD version, header_size, pid, thread_id, callsite;
    DWORD tick_before, tick_after, sequence, flags;
    ULONGLONG qpc;
    char run_id[40];
    BYTE reserved[36];
} SnapshotHeader;

typedef struct {
    DWORD thread_id;
    DWORD tick_before;
    DWORD callsite;
    BOOL active;
} ThreadContext;

static const BYTE OLD_CALL_A[5] = {0xE8, 0x99, 0x81, 0xFF, 0xFF};
static const BYTE OLD_CALL_B[5] = {0xE8, 0x74, 0x76, 0xFF, 0xFF};
static const DWORD CALL_A = 0x004245D2u;
static const DWORD CALL_B = 0x004250F7u;
static DWORD g_ticks[SNAPSHOT_MAX_TICKS];
static DWORD g_tick_count;
static char g_output_dir[MAX_PATH];
static char g_run_id[40];
static BOOL g_enabled;
static BOOL g_installed;
static DWORD g_sequence;
static HANDLE g_trace = INVALID_HANDLE_VALUE;
static volatile LONG g_context_lock;
static volatile LONG g_snapshot_lock;
static ThreadContext g_contexts[THREAD_CONTEXTS];
static BYTE g_saved_calls[2][5];
static DWORD g_original_protect[2];
static BOOL g_call_installed[2];
static BYTE *g_snapshot_payload;
__attribute__((used)) DWORD g1_state_snapshot_update_target = 0x0041C770u;

static BOOL bytes_equal(const BYTE *a, const BYTE *b, DWORD length)
{
    DWORD i;
    for (i = 0; i < length; ++i) if (a[i] != b[i]) return FALSE;
    return TRUE;
}

static void copy_bytes(void *destination, const void *source, DWORD length)
{
    BYTE *out = (BYTE *)destination;
    const BYTE *in = (const BYTE *)source;
    DWORD i;
    for (i = 0; i < length; ++i) out[i] = in[i];
}

static BOOL readable(const void *address, DWORD length)
{
    MEMORY_BASIC_INFORMATION mbi;
    ULONG_PTR start = (ULONG_PTR)address;
    ULONG_PTR end = start + length;
    ULONG_PTR region_end;
    if (!address || !length || !VirtualQuery(address, &mbi, sizeof(mbi)) ||
        mbi.State != MEM_COMMIT || (mbi.Protect & (PAGE_NOACCESS | PAGE_GUARD))) return FALSE;
    region_end = (ULONG_PTR)mbi.BaseAddress + mbi.RegionSize;
    return end >= start && end <= region_end;
}

static void spin_lock(void)
{
    while (InterlockedCompareExchange(&g_context_lock, 1, 0) != 0) Sleep(0);
}

static void spin_unlock(void) { InterlockedExchange(&g_context_lock, 0); }

static BOOL target_tick(DWORD tick)
{
    DWORD i;
    for (i = 0; i < g_tick_count; ++i) if (g_ticks[i] == tick) return TRUE;
    return FALSE;
}

static void trace_event(const char *status, DWORD thread, DWORD callsite,
                        DWORD before, DWORD after, DWORD flags)
{
    char line[420];
    DWORD written = 0;
    int n;
    if (g_trace == INVALID_HANDLE_VALUE) return;
    n = wsprintfA(line,
        "{\"schema\":\"g1-inprocess-snapshot-v1\",\"event\":\"snapshot\","
        "\"status\":\"%s\",\"run_id\":\"%s\",\"pid\":%u,\"thread_id\":%u,"
        "\"callsite\":\"0x%08X\",\"tick_before\":%u,\"tick_after\":%u,"
        "\"tick_jump\":%u,\"sequence\":%u}\n",
        status, g_run_id, (unsigned)GetCurrentProcessId(), (unsigned)thread,
        (unsigned)callsite, (unsigned)before, (unsigned)after,
        (unsigned)(flags & 1u), (unsigned)g_sequence);
    if (n > 0) { WriteFile(g_trace, line, (DWORD)n, &written, NULL); FlushFileBuffers(g_trace); }
}

BOOL g1_state_snapshot_enabled(void)
{
    char ticks[128];
    DWORD size, value = 0;
    char *cursor;
    if (g_enabled) return TRUE;
    size = GetEnvironmentVariableA(SNAPSHOT_TICKS_ENV, ticks, sizeof(ticks));
    if (size == 0 || size >= sizeof(ticks)) return FALSE;
    size = GetEnvironmentVariableA(SNAPSHOT_DIR_ENV, g_output_dir, sizeof(g_output_dir));
    if (size == 0 || size >= sizeof(g_output_dir)) return FALSE;
    size = GetEnvironmentVariableA(SNAPSHOT_RUN_ENV, g_run_id, sizeof(g_run_id));
    if (size == 0 || size >= sizeof(g_run_id)) return FALSE;
    g_run_id[sizeof(g_run_id) - 1] = '\0';
    cursor = ticks;
    while (*cursor && g_tick_count < SNAPSHOT_MAX_TICKS) {
        char *end = cursor;
        value = 0;
        while (*end >= '0' && *end <= '9') {
            value = value * 10u + (DWORD)(*end - '0');
            ++end;
        }
        if (end == cursor || (*end && *end != ',')) { g_tick_count = 0; return FALSE; }
        g_ticks[g_tick_count++] = value;
        cursor = *end == ',' ? end + 1 : end;
    }
    if (*cursor || !g_tick_count) { g_tick_count = 0; return FALSE; }
    g_enabled = TRUE;
    return TRUE;
}

void g1_state_snapshot_before(DWORD callsite)
{
    DWORD i, thread = GetCurrentThreadId();
    DWORD tick = readable((void *)TICK_ADDRESS, 4) ? *(volatile DWORD *)TICK_ADDRESS : 0xFFFFFFFFu;
    spin_lock();
    for (i = 0; i < THREAD_CONTEXTS; ++i) {
        if (g_contexts[i].active && g_contexts[i].thread_id == thread) break;
        if (!g_contexts[i].active) break;
    }
    if (i < THREAD_CONTEXTS) {
        g_contexts[i].thread_id = thread;
        g_contexts[i].tick_before = tick;
        g_contexts[i].callsite = callsite;
        g_contexts[i].active = TRUE;
    }
    spin_unlock();
}

static BOOL write_all(HANDLE file, const BYTE *bytes, DWORD length)
{
    DWORD written = 0;
    return WriteFile(file, bytes, length, &written, NULL) && written == length;
}

static BOOL write_snapshot(DWORD callsite, DWORD thread, DWORD before, DWORD after)
{
    DWORD lengths[6] = {4u, 4u, 8u, PLAYER_SIZE, EXISTS_SIZE, UNIT_SIZE};
    DWORD addresses[6] = {PS_ADDRESS, TICK_ADDRESS, CAMERA_ADDRESS,
                          PLAYER_ADDRESS, EXISTS_ADDRESS, UNIT_ADDRESS};
    DWORD i, offset = 0, flags = after - before > 1u ? 1u : 0u;
    char path[MAX_PATH], temporary[MAX_PATH];
    HANDLE file;
    SnapshotHeader header;
    LARGE_INTEGER qpc;
    BOOL ok = TRUE;
    for (i = 0; i < 6u; ++i) {
        if (!readable((void *)(ULONG_PTR)addresses[i], lengths[i])) return FALSE;
    }
    if (!g_snapshot_payload) return FALSE;
    while (InterlockedCompareExchange(&g_snapshot_lock, 1, 0) != 0) Sleep(0);
    for (i = 0; i < 6u; ++i) {
        copy_bytes(g_snapshot_payload + offset, (void *)(ULONG_PTR)addresses[i], lengths[i]);
        offset += lengths[i];
    }
    ZeroMemory(&header, sizeof(header));
    copy_bytes(header.magic, "G1SNAP1", 7u);
    header.version = 1u; header.header_size = SNAPSHOT_HEADER_SIZE;
    header.pid = GetCurrentProcessId(); header.thread_id = thread;
    header.callsite = callsite; header.tick_before = before; header.tick_after = after;
    header.sequence = ++g_sequence; header.flags = flags;
    QueryPerformanceCounter(&qpc); header.qpc = (ULONGLONG)qpc.QuadPart;
    lstrcpynA(header.run_id, g_run_id, sizeof(header.run_id));
    wsprintfA(path, "%s\\state-%u.bin", g_output_dir, (unsigned)after);
    wsprintfA(temporary, "%s\\state-%u.bin.tmp", g_output_dir, (unsigned)after);
    file = CreateFileA(temporary, GENERIC_WRITE, 0, NULL, CREATE_ALWAYS,
                       FILE_ATTRIBUTE_NORMAL, NULL);
    if (file == INVALID_HANDLE_VALUE) ok = FALSE;
    else {
        ok = write_all(file, (const BYTE *)&header, sizeof(header));
        ok = ok && write_all(file, g_snapshot_payload, SNAPSHOT_PAYLOAD_SIZE);
        if (ok) FlushFileBuffers(file);
        CloseHandle(file);
        if (ok) ok = MoveFileExA(temporary, path, MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH);
        if (!ok) DeleteFileA(temporary);
    }
    if (ok) trace_event("written", thread, callsite, before, after, flags);
    else trace_event("write_failed", thread, callsite, before, after, flags);
    InterlockedExchange(&g_snapshot_lock, 0);
    return ok;
}

void g1_state_snapshot_after(DWORD callsite)
{
    DWORD i, thread = GetCurrentThreadId(), before = 0xFFFFFFFFu, saved_callsite = callsite;
    DWORD after = readable((void *)TICK_ADDRESS, 4) ? *(volatile DWORD *)TICK_ADDRESS : 0xFFFFFFFFu;
    spin_lock();
    for (i = 0; i < THREAD_CONTEXTS; ++i) {
        if (g_contexts[i].active && g_contexts[i].thread_id == thread) {
            before = g_contexts[i].tick_before; saved_callsite = g_contexts[i].callsite;
            g_contexts[i].active = FALSE;
            break;
        }
    }
    spin_unlock();
    if (before != after && target_tick(after)) write_snapshot(saved_callsite, thread, before, after);
}

__attribute__((naked)) static void snapshot_call_a(void)
{
    __asm__ __volatile__(
        "pushfl; pushal; pushl $0x004245D2; call _g1_state_snapshot_before; addl $4, %esp; popal; popfl;"
        "call *_g1_state_snapshot_update_target;"
        "pushfl; pushal; pushl $0x004245D2; call _g1_state_snapshot_after; addl $4, %esp; popal; popfl; ret");
}

__attribute__((naked)) static void snapshot_call_b(void)
{
    __asm__ __volatile__(
        "pushfl; pushal; pushl $0x004250F7; call _g1_state_snapshot_before; addl $4, %esp; popal; popfl;"
        "call *_g1_state_snapshot_update_target;"
        "pushfl; pushal; pushl $0x004250F7; call _g1_state_snapshot_after; addl $4, %esp; popal; popfl; ret");
}

static void make_hook(DWORD address, void *wrapper, BYTE hook[5])
{
    DWORD target = (DWORD)(ULONG_PTR)wrapper;
    DWORD relative = target - (address + 5u);
    hook[0] = 0xE8;
    copy_bytes(hook + 1, &relative, 4u);
}

static BOOL restore_call(DWORD address, const BYTE owned[5], const BYTE original[5])
{
    BYTE *site = (BYTE *)(ULONG_PTR)address;
    DWORD old = 0, ignored = 0;
    BOOL flush_ok, protect_ok;
    if (!bytes_equal(site, owned, 5u)) return FALSE;
    if (!VirtualProtect(site, 5u, PAGE_EXECUTE_READWRITE, &old)) return FALSE;
    if (!bytes_equal(site, owned, 5u)) {
        VirtualProtect(site, 5u, old, &ignored);
        return FALSE;
    }
    copy_bytes(site, original, 5u);
    flush_ok = FlushInstructionCache(GetCurrentProcess(), site, 5u);
    protect_ok = VirtualProtect(site, 5u, old, &ignored);
    if (flush_ok && protect_ok) return TRUE;
    /* If restoring page protection failed, the page should still be writable. Retry it. */
    if (!protect_ok && bytes_equal(site, original, 5u) &&
        VirtualProtect(site, 5u, old, &ignored)) protect_ok = TRUE;
    return flush_ok && protect_ok && bytes_equal(site, original, 5u);
}

static BOOL install_call(DWORD address, const BYTE expected[5], void *wrapper,
                         BYTE saved[5], DWORD *original_protect)
{
    BYTE *site = (BYTE *)(ULONG_PTR)address;
    BYTE hook[5];
    DWORD old = 0, ignored = 0;
    BOOL flush_ok, protect_ok;
    make_hook(address, wrapper, hook);
    if (!bytes_equal(site, expected, 5u) ||
        !VirtualProtect(site, 5u, PAGE_EXECUTE_READWRITE, &old)) return FALSE;
    if (!bytes_equal(site, expected, 5u)) {
        VirtualProtect(site, 5u, old, &ignored);
        return FALSE;
    }
    copy_bytes(saved, site, 5u);
    copy_bytes(site, hook, 5u);
    flush_ok = FlushInstructionCache(GetCurrentProcess(), site, 5u);
    protect_ok = VirtualProtect(site, 5u, old, &ignored);
    if (flush_ok && protect_ok) {
        *original_protect = old;
        return TRUE;
    }
    /* Undo only our complete hook; never overwrite a hook installed by another owner. */
    if (!protect_ok && bytes_equal(site, hook, 5u)) {
        copy_bytes(site, saved, 5u);
        flush_ok = FlushInstructionCache(GetCurrentProcess(), site, 5u) && flush_ok;
        protect_ok = VirtualProtect(site, 5u, old, &ignored);
    } else if (protect_ok && bytes_equal(site, hook, 5u) &&
               VirtualProtect(site, 5u, PAGE_EXECUTE_READWRITE, &ignored)) {
        if (bytes_equal(site, hook, 5u)) {
            copy_bytes(site, saved, 5u);
            flush_ok = FlushInstructionCache(GetCurrentProcess(), site, 5u) && flush_ok;
        }
        protect_ok = VirtualProtect(site, 5u, old, &ignored);
    }
    return FALSE;
}

BOOL g1_state_snapshot_install(void)
{
    char trace_path[MAX_PATH];
    BYTE hook_a[5], hook_b[5];
    if (!g1_state_snapshot_enabled()) return TRUE;
    if ((DWORD)(ULONG_PTR)GetModuleHandleA(NULL) != GAME_BASE || sizeof(SnapshotHeader) != SNAPSHOT_HEADER_SIZE) return FALSE;
    if (!CreateDirectoryA(g_output_dir, NULL) && GetLastError() != ERROR_ALREADY_EXISTS) return FALSE;
    wsprintfA(trace_path, "%s\\trace.jsonl", g_output_dir);
    g_trace = CreateFileA(trace_path, GENERIC_WRITE, FILE_SHARE_READ, NULL, CREATE_ALWAYS,
                          FILE_ATTRIBUTE_NORMAL, NULL);
    if (g_trace == INVALID_HANDLE_VALUE) return FALSE;
    g_snapshot_payload = (BYTE *)HeapAlloc(GetProcessHeap(), 0, SNAPSHOT_PAYLOAD_SIZE);
    if (!g_snapshot_payload) { CloseHandle(g_trace); g_trace = INVALID_HANDLE_VALUE; return FALSE; }
    make_hook(CALL_A, snapshot_call_a, hook_a);
    make_hook(CALL_B, snapshot_call_b, hook_b);
    if (!install_call(CALL_A, OLD_CALL_A, snapshot_call_a, g_saved_calls[0], &g_original_protect[0])) {
        if (bytes_equal((BYTE *)(ULONG_PTR)CALL_A, hook_a, 5u)) {
            copy_bytes(g_saved_calls[0], OLD_CALL_A, 5u);
            if (!restore_call(CALL_A, hook_a, g_saved_calls[0])) g_call_installed[0] = TRUE;
        }
        g_installed = g_call_installed[0];
        if (!g_installed) {
            HeapFree(GetProcessHeap(), 0, g_snapshot_payload); g_snapshot_payload = NULL;
            CloseHandle(g_trace); g_trace = INVALID_HANDLE_VALUE;
        }
        return FALSE;
    }
    g_call_installed[0] = TRUE;
    if (!install_call(CALL_B, OLD_CALL_B, snapshot_call_b, g_saved_calls[1], &g_original_protect[1])) {
        if (bytes_equal((BYTE *)(ULONG_PTR)CALL_B, hook_b, 5u)) {
            copy_bytes(g_saved_calls[1], OLD_CALL_B, 5u);
            if (!restore_call(CALL_B, hook_b, g_saved_calls[1])) g_call_installed[1] = TRUE;
        }
        if (g_call_installed[1])
            trace_event("rollback_failed", GetCurrentThreadId(), CALL_B, 0u, 0u, 0u);
        if (restore_call(CALL_A, hook_a, g_saved_calls[0])) g_call_installed[0] = FALSE;
        else trace_event("rollback_failed", GetCurrentThreadId(), CALL_A, 0u, 0u, 0u);
        g_installed = g_call_installed[0] || g_call_installed[1];
        if (!g_installed) {
            HeapFree(GetProcessHeap(), 0, g_snapshot_payload); g_snapshot_payload = NULL;
            CloseHandle(g_trace); g_trace = INVALID_HANDLE_VALUE;
        }
        return FALSE;
    }
    g_call_installed[1] = TRUE;
    g_installed = TRUE;
    return TRUE;
}

void g1_state_snapshot_detach(void)
{
    BYTE hook[5];
    if (g_installed) {
        make_hook(CALL_A, snapshot_call_a, hook);
        if (g_call_installed[0]) {
            if (restore_call(CALL_A, hook, g_saved_calls[0])) g_call_installed[0] = FALSE;
            else trace_event("detach_failed", GetCurrentThreadId(), CALL_A, 0u, 0u, 0u);
        }
        make_hook(CALL_B, snapshot_call_b, hook);
        if (g_call_installed[1]) {
            if (restore_call(CALL_B, hook, g_saved_calls[1])) g_call_installed[1] = FALSE;
            else trace_event("detach_failed", GetCurrentThreadId(), CALL_B, 0u, 0u, 0u);
        }
    }
    if (g_trace != INVALID_HANDLE_VALUE) { CloseHandle(g_trace); g_trace = INVALID_HANDLE_VALUE; }
}
