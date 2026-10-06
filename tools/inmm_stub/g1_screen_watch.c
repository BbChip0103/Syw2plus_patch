/* H-B3 diagnostic: who writes the three save000 screen sample points?
 *
 * Opt-in SYW2_G1_SCREEN_WATCH=1 (mirror candidate lane with the layer-drift
 * diagnostic).  At the first valid PS3 present it arms DR0..DR2 as one-byte
 * write breakpoints on the renderer's screen buffer (A/B/C sample points) on
 * every thread of the process and logs each hit (EIP, thread, value, module,
 * mirror guard, .text return addresses).  Data breakpoints trap after the
 * writing instruction, so EIP is the instruction following the write.  The game
 * buffer is only read.  Win32/no-CRT like the rest of the DLL. */

#include <windows.h>
#include <tlhelp32.h>

#include "g1_mirror2x.h"
#include "g1_screen_watch.h"

#define G1_SCREEN_WATCH_ENV "SYW2_G1_SCREEN_WATCH"
#define G1_SCREEN_WATCH_CACHE_ENV "SYW2_G1_SCREEN_WATCH_CACHE"
#define G1_DRIFT_SAMPLES_ENV "SYW2_G1_DRIFT_SAMPLES"
#define G1_SCREEN_WATCH_PATH "C:\\inmm_g1_screen_watch.jsonl"
#define SW_PROGRAM_STATE_VA 0x004ED818u
#define SW_RENDERER_VA 0x00E5BF18u
#define SW_RENDERER_HEIGHT 0x08u
#define SW_RENDERER_STRIDE 0x10u
#define SW_RENDERER_BUFFER 0x1514u
#define SW_RAW_LIMIT 20000u
#define SW_EIP_TABLE 48u
#define SW_STACK_SCAN 96u
#define SW_STACK_KEEP 4u
#define SW_REARM_INTERVAL 8u
#define SW_HEARTBEAT 50u

typedef struct {
    DWORD slot, eip, base, hits, first_present, last_present, present_thread_hits;
} SwEipEntry;

static volatile LONG g_sw_state = 0;
static BOOL g_sw_enabled = FALSE;
static HANDLE g_sw_file = INVALID_HANDLE_VALUE;
static PVOID g_sw_veh = NULL;
static volatile LONG g_sw_lock = 0;
static volatile LONG g_sw_armed = 0;
static BOOL g_sw_cache = FALSE;
static volatile LONG g_sw_selftest_active = 0;
static volatile BYTE g_sw_selftest_byte = 0u;
static volatile DWORD g_sw_selftest_hits = 0u;
static volatile DWORD g_sw_next_present = 0u;
static volatile DWORD g_sw_present_tid = 0u;
static DWORD g_sw_addr[G1_SCREEN_WATCH_SAMPLES];
static DWORD g_sw_exe_base = 0u, g_sw_dll_base = 0u;
static DWORD g_sw_arm_ok = 0u, g_sw_arm_fail = 0u, g_sw_arm_rounds = 0u;
static DWORD g_sw_threads_armed = 0u, g_sw_present_thread_armed = 0u;
static DWORD g_sw_presents_seen = 0u;
static DWORD g_sw_match_last = 0xFFu;
static DWORD g_sw_hits = 0u, g_sw_raw = 0u, g_sw_raw_dropped = 0u;
static DWORD g_sw_hits_slot[G1_SCREEN_WATCH_SAMPLES + 1u];
static DWORD g_sw_eip_distinct = 0u, g_sw_eip_overflow = 0u;
static SwEipEntry g_sw_eip[SW_EIP_TABLE];

static BOOL screen_watch_on(void)
{
    char value[8];
    char drift_samples[64];
    DWORD size;
    LONG state = InterlockedCompareExchange(&g_sw_state, 1, 0);
    if (state == 0) {
        size = GetEnvironmentVariableA(G1_SCREEN_WATCH_ENV, value, sizeof(value));
        g_sw_enabled = size == 1u && value[0] == '1';
        size = GetEnvironmentVariableA(G1_SCREEN_WATCH_CACHE_ENV, value, sizeof(value));
        g_sw_cache = size == 1u && value[0] == '1';
        size = GetEnvironmentVariableA(G1_DRIFT_SAMPLES_ENV, drift_samples, sizeof(drift_samples));
        if (size > 0u && size < sizeof(drift_samples))
            g1_layer_drift_samples_parse(drift_samples, size);
        InterlockedExchange(&g_sw_state, 2);
    } else {
        while (g_sw_state != 2) Sleep(0);
    }
    return g_sw_enabled;
}

static void sw_emit(const char *line, int length)
{
    DWORD written;
    if (length <= 0) return;
    if (g_sw_file == INVALID_HANDLE_VALUE) return;
    WriteFile(g_sw_file, line, (DWORD)length, &written, NULL);
}

static void sw_lock(void)
{
    while (InterlockedExchange(&g_sw_lock, 1) != 0) Sleep(0);
}

static void sw_unlock(void)
{
    InterlockedExchange(&g_sw_lock, 0);
}

static BOOL sw_readable(const void *address, DWORD bytes)
{
    MEMORY_BASIC_INFORMATION info;
    DWORD_PTR end = (DWORD_PTR)address + bytes;
    if (VirtualQuery(address, &info, sizeof(info)) != sizeof(info)) return FALSE;
    if (info.State != MEM_COMMIT || (info.Protect & (PAGE_NOACCESS | PAGE_GUARD)) != 0u)
        return FALSE;
    return end <= (DWORD_PTR)info.BaseAddress + info.RegionSize;
}

static DWORD sw_allocation_base(DWORD address)
{
    MEMORY_BASIC_INFORMATION info;
    if (VirtualQuery((const void *)(ULONG_PTR)address, &info, sizeof(info)) != sizeof(info) ||
        info.State != MEM_COMMIT) return 0u;
    return (DWORD)(ULONG_PTR)info.AllocationBase;
}

/* Set (dr7 != 0) or clear (dr7 == 0) the debug registers of one thread. */
static BOOL sw_apply_thread(DWORD tid, const DWORD *addr, DWORD dr7)
{
    CONTEXT context;
    BOOL self = tid == GetCurrentThreadId();
    HANDLE thread = self ? GetCurrentThread()
                         : OpenThread(THREAD_GET_CONTEXT | THREAD_SET_CONTEXT |
                                      THREAD_SUSPEND_RESUME, FALSE, tid);
    BOOL ok = FALSE;
    if (!thread) return FALSE;
    if (!self && SuspendThread(thread) == (DWORD)-1) {
        CloseHandle(thread);
        return FALSE;
    }
    context.ContextFlags = CONTEXT_DEBUG_REGISTERS;
    if (GetThreadContext(thread, &context)) {
        context.Dr0 = addr ? addr[0] : 0u;
        context.Dr1 = addr ? addr[1] : 0u;
        context.Dr2 = addr ? addr[2] : 0u;
        context.Dr6 = 0u;
        context.Dr7 = dr7;
        ok = SetThreadContext(thread, &context);
    }
    if (!self) {
        ResumeThread(thread);
        CloseHandle(thread);
    }
    return ok;
}

/* Arm (or clear) every thread of this process; counts successes and failures. */
static void sw_apply_all(const DWORD *addr, DWORD dr7, BOOL count)
{
    HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0u);
    THREADENTRY32 entry;
    DWORD pid = GetCurrentProcessId(), present_tid = g_sw_present_tid;
    DWORD armed = 0u;
    if (snapshot == INVALID_HANDLE_VALUE) {
        if (count) ++g_sw_arm_fail;
        return;
    }
    entry.dwSize = sizeof(entry);
    if (Thread32First(snapshot, &entry)) {
        do {
            if (entry.th32OwnerProcessID != pid) continue;
            if (sw_apply_thread(entry.th32ThreadID, addr, dr7)) {
                ++armed;
                if (count) {
                    ++g_sw_arm_ok;
                    if (entry.th32ThreadID == present_tid) g_sw_present_thread_armed = 1u;
                }
            } else if (count) {
                ++g_sw_arm_fail;
            }
        } while (Thread32Next(snapshot, &entry));
    }
    CloseHandle(snapshot);
    if (count) g_sw_threads_armed = armed;
}

static void sw_note_eip(DWORD slot, DWORD eip, DWORD base, DWORD present, BOOL present_thread)
{
    DWORD i;
    for (i = 0u; i < g_sw_eip_distinct; ++i) {
        if (g_sw_eip[i].eip == eip && g_sw_eip[i].slot == slot) {
            ++g_sw_eip[i].hits;
            g_sw_eip[i].last_present = present;
            if (present_thread) ++g_sw_eip[i].present_thread_hits;
            return;
        }
    }
    if (g_sw_eip_distinct < SW_EIP_TABLE) {
        SwEipEntry *entry = &g_sw_eip[g_sw_eip_distinct++];
        entry->slot = slot;
        entry->eip = eip;
        entry->base = base;
        entry->hits = 1u;
        entry->first_present = entry->last_present = present;
        entry->present_thread_hits = present_thread ? 1u : 0u;
    } else {
        ++g_sw_eip_overflow;
    }
}

static LONG CALLBACK sw_veh(EXCEPTION_POINTERS *info)
{
    CONTEXT *c;
    DWORD slot, tid, present, base, i, found = 0u, scan = SW_STACK_SCAN;
    DWORD stack[SW_STACK_KEEP] = {0u, 0u, 0u, 0u};
    const DWORD *sp;
    BOOL present_thread;
    char line[512];
    if (info->ExceptionRecord->ExceptionCode != EXCEPTION_SINGLE_STEP)
        return EXCEPTION_CONTINUE_SEARCH;
    c = info->ContextRecord;
    if (g_sw_selftest_active) {
        ++g_sw_selftest_hits;
        c->Dr6 = 0u;
        return EXCEPTION_CONTINUE_EXECUTION;
    }
    if (!g_sw_armed) return EXCEPTION_CONTINUE_SEARCH;
    slot = g1_screen_watch_slot(c->Dr6);
    tid = GetCurrentThreadId();
    present_thread = tid == g_sw_present_tid;
    present = g_sw_next_present;
    base = sw_allocation_base(c->Eip);
    sp = (const DWORD *)(ULONG_PTR)c->Esp;
    if (!sw_readable(sp, scan * sizeof(DWORD))) scan = 16u;
    if (sw_readable(sp, scan * sizeof(DWORD)))
        for (i = 0u; i < scan && found < SW_STACK_KEEP; ++i)
            if (g1_screen_watch_in_exe_text(sp[i])) stack[found++] = sp[i];
    sw_lock();
    ++g_sw_hits;
    if (slot < G1_SCREEN_WATCH_SAMPLES + 1u) ++g_sw_hits_slot[slot];
    sw_note_eip(slot, c->Eip, base, present, present_thread);
    if (g_sw_raw < SW_RAW_LIMIT) {
        DWORD v[G1_SCREEN_WATCH_SAMPLES];
        for (i = 0u; i < G1_SCREEN_WATCH_SAMPLES; ++i)
            v[i] = (DWORD)*(volatile BYTE *)(ULONG_PTR)g_sw_addr[i];
        ++g_sw_raw;
        sw_emit(line, wsprintfA(line,
            "{\"t\":\"x\",\"p\":%u,\"i\":%u,\"dr6\":%u,\"eip\":\"0x%08X\",\"tid\":%u,"
            "\"pt\":%u,\"val\":%u,\"v\":[%u,%u,%u],\"mod\":%u,\"base\":\"0x%08X\","
            "\"guard\":%u,\"st\":[\"0x%08X\",\"0x%08X\",\"0x%08X\",\"0x%08X\"]}\n",
            present, slot, (unsigned)(c->Dr6 & 0xFu), (unsigned)c->Eip, tid,
            (unsigned)present_thread,
            slot < G1_SCREEN_WATCH_SAMPLES ? v[slot] : 256u, v[0], v[1], v[2],
            g1_screen_watch_module_class(base, g_sw_exe_base, g_sw_dll_base), base,
            g1_mirror2x_primitive_guard(),
            stack[0], stack[1], stack[2], stack[3]));
    } else {
        ++g_sw_raw_dropped;
    }
    sw_unlock();
    c->Dr6 = 0u;
    return EXCEPTION_CONTINUE_EXECUTION;
}

/* One real write to a private byte through slot 3 proves traps reach the handler. */
static void sw_selftest(void)
{
    DWORD before = g_sw_selftest_hits;
    BOOL armed;
    char line[200];
    g_sw_selftest_active = 1;
    /* the private byte rides slot 3 through Dr3, which sw_apply_thread leaves alone */
    {
        CONTEXT context;
        context.ContextFlags = CONTEXT_DEBUG_REGISTERS;
        armed = GetThreadContext(GetCurrentThread(), &context);
        if (armed) {
            context.Dr3 = (DWORD)(ULONG_PTR)&g_sw_selftest_byte;
            context.Dr6 = 0u;
            context.Dr7 = (DWORD)g1_screen_watch_dr7(0u, 1);
            armed = SetThreadContext(GetCurrentThread(), &context);
        }
        if (armed) {
            g_sw_selftest_byte = 0x5Au;
            context.ContextFlags = CONTEXT_DEBUG_REGISTERS;
            if (GetThreadContext(GetCurrentThread(), &context)) {
                context.Dr3 = 0u;
                context.Dr6 = 0u;
                context.Dr7 = 0u;
                (void)SetThreadContext(GetCurrentThread(), &context);
            }
        }
    }
    g_sw_selftest_active = 0;
    sw_emit(line, wsprintfA(line,
        "{\"t\":\"s\",\"armed\":%u,\"hits\":%u,\"status\":\"%s\"}\n",
        (unsigned)armed, (unsigned)(g_sw_selftest_hits - before),
        g_sw_selftest_hits == before + 1u ? "PASS" : (armed ? "no_hit" : "set_context_failed")));
}

/* Published every heartbeat: totals plus the (slot, EIP) table with module names. */
static void sw_summary(DWORD present)
{
    char line[1000], name[260];
    const char *file;
    SwEipEntry table[SW_EIP_TABLE];
    DWORD i, count;
    int length;
    sw_lock();
    count = g_sw_eip_distinct;
    /* field-wise: a struct assignment would pull in memcpy (no CRT) */
    for (i = 0u; i < count; ++i) {
        table[i].slot = g_sw_eip[i].slot;
        table[i].eip = g_sw_eip[i].eip;
        table[i].base = g_sw_eip[i].base;
        table[i].hits = g_sw_eip[i].hits;
        table[i].first_present = g_sw_eip[i].first_present;
        table[i].last_present = g_sw_eip[i].last_present;
        table[i].present_thread_hits = g_sw_eip[i].present_thread_hits;
    }
    length = wsprintfA(line,
        "{\"t\":\"k\",\"p\":%u,\"hits\":%u,\"raw\":%u,\"dropped\":%u,\"slot_hits\":[%u,%u,%u,%u],"
        "\"distinct\":%u,\"overflow\":%u,\"arm_rounds\":%u,\"arm_ok\":%u,\"arm_fail\":%u,"
        "\"threads\":%u,\"present_thread_armed\":%u,\"selftest_hits\":%u}\n",
        present, g_sw_hits, g_sw_raw, g_sw_raw_dropped, g_sw_hits_slot[0], g_sw_hits_slot[1],
        g_sw_hits_slot[2], g_sw_hits_slot[3], g_sw_eip_distinct, g_sw_eip_overflow,
        g_sw_arm_rounds, g_sw_arm_ok, g_sw_arm_fail, g_sw_threads_armed,
        g_sw_present_thread_armed, g_sw_selftest_hits);
    sw_emit(line, length);
    sw_unlock();
    /* module names are resolved outside the hit lock (loader state) */
    for (i = 0u; i < count; ++i) {
        const SwEipEntry *entry = &table[i];
        DWORD n = 0u, j;
        name[0] = '\0';
        if (entry->base != 0u)
            n = GetModuleFileNameA((HMODULE)(ULONG_PTR)entry->base, name, sizeof(name));
        name[sizeof(name) - 1u] = '\0'; /* truncation does not NUL-terminate */
        file = name;
        for (j = 0u; j < n && j < sizeof(name) - 1u; ++j)
            if (name[j] == '\\' || name[j] == '/') file = name + j + 1u;
        for (j = 0u; j < sizeof(name) - 1u && name[j] != '\0'; ++j)
            if (name[j] == '"' || (unsigned char)name[j] < 0x20u) name[j] = '_';
        length = wsprintfA(line,
            "{\"t\":\"e\",\"p\":%u,\"i\":%u,\"eip\":\"0x%08X\",\"base\":\"0x%08X\","
            "\"hits\":%u,\"first\":%u,\"last\":%u,\"pt_hits\":%u,\"module\":\"%s\"}\n",
            present, entry->slot, entry->eip, entry->base, entry->hits,
            entry->first_present, entry->last_present, entry->present_thread_hits,
            file);
        sw_lock();
        sw_emit(line, length);
        sw_unlock();
    }
}

static BOOL sw_buffer_valid(DWORD *buffer, DWORD *stride)
{
    const BYTE *renderer = (const BYTE *)(ULONG_PTR)SW_RENDERER_VA;
    if (!sw_readable(renderer, SW_RENDERER_BUFFER + sizeof(DWORD))) return FALSE;
    *stride = *(const volatile DWORD *)(renderer + SW_RENDERER_STRIDE);
    *buffer = *(const volatile DWORD *)(renderer + SW_RENDERER_BUFFER);
    return *buffer != 0u && *stride >= 800u && *stride <= 4096u &&
           *(const volatile DWORD *)(renderer + SW_RENDERER_HEIGHT) == 600u;
}

void g1_screen_watch_on_present(const unsigned char *surface, unsigned long pitch,
                                unsigned long next_present)
{
    DWORD addr[G1_SCREEN_WATCH_SAMPLES], buffer, stride, i, match = 0u;
    BOOL rearm;
    unsigned px, py;
    char line[300];
    if (!screen_watch_on()) return;
    if (*(const volatile DWORD *)(ULONG_PTR)SW_PROGRAM_STATE_VA != 3u) return;
    g_sw_next_present = (DWORD)next_present;
    g_sw_present_tid = GetCurrentThreadId();
    if (!sw_buffer_valid(&buffer, &stride)) return;
    if (g_sw_file == INVALID_HANDLE_VALUE) {
        g_sw_file = CreateFileA(G1_SCREEN_WATCH_PATH, GENERIC_WRITE, FILE_SHARE_READ, NULL,
                                OPEN_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
        if (g_sw_file == INVALID_HANDLE_VALUE) return;
        SetFilePointer(g_sw_file, 0, NULL, FILE_END);
        g_sw_exe_base = (DWORD)(ULONG_PTR)GetModuleHandleA(NULL);
        g_sw_dll_base = sw_allocation_base((DWORD)(ULONG_PTR)&g_sw_selftest_byte);
        sw_emit(line, wsprintfA(line,
            "{\"t\":\"h\",\"schema\":\"syw2plus.g1-screen-watch.v1\",\"exe_base\":\"0x%08X\","
            "\"dll_base\":\"0x%08X\",\"pid\":%u}\n",
            g_sw_exe_base, g_sw_dll_base, (unsigned)GetCurrentProcessId()));
    }
    ++g_sw_presents_seen;
    for (i = 0u; i < G1_SCREEN_WATCH_SAMPLES; ++i) {
        g1_layer_drift_sample(i, &px, &py);
        addr[i] = g_sw_cache
            ? (DWORD)g1_screen_watch_address(G1_SCREEN_WATCH_CACHE_BASE,
                                             G1_SCREEN_WATCH_CACHE_PITCH, px, py)
            : (DWORD)g1_screen_watch_address(buffer, stride, px, py);
        if (!g_sw_cache && surface && addr[i] == (DWORD)(ULONG_PTR)(surface + py * pitch + px))
            match |= 1u << i;
    }
    if (match != g_sw_match_last) {
        g_sw_match_last = match;
        sw_emit(line, wsprintfA(line,
            "{\"t\":\"m\",\"p\":%u,\"match\":%u,\"buffer\":\"0x%08X\",\"stride\":%u,"
            "\"surface\":\"0x%08X\",\"pitch\":%u}\n",
            (unsigned)next_present, match, buffer, stride,
            (unsigned)(ULONG_PTR)surface, (unsigned)pitch));
    }
    rearm = !g_sw_armed || addr[0] != g_sw_addr[0] || addr[1] != g_sw_addr[1] ||
            addr[2] != g_sw_addr[2] || g_sw_presents_seen % SW_REARM_INTERVAL == 0u;
    if (rearm) {
        if (!g_sw_veh) {
            g_sw_veh = AddVectoredExceptionHandler(1u, sw_veh);
            if (!g_sw_veh) return;
            sw_selftest();
        }
        sw_lock();
        for (i = 0u; i < G1_SCREEN_WATCH_SAMPLES; ++i) g_sw_addr[i] = addr[i];
        sw_unlock();
        g_sw_armed = 1;
        ++g_sw_arm_rounds;
        sw_apply_all(addr, (DWORD)g1_screen_watch_dr7(G1_SCREEN_WATCH_SAMPLES, 0), TRUE);
        sw_emit(line, wsprintfA(line,
            "{\"t\":\"a\",\"p\":%u,\"round\":%u,\"threads\":%u,\"ok\":%u,\"fail\":%u,"
            "\"present_thread_armed\":%u,\"addr\":[\"0x%08X\",\"0x%08X\",\"0x%08X\"]}\n",
            (unsigned)next_present, g_sw_arm_rounds, g_sw_threads_armed, g_sw_arm_ok,
            g_sw_arm_fail, g_sw_present_thread_armed, addr[0], addr[1], addr[2]));
    }
    if (g_sw_presents_seen % SW_HEARTBEAT == 0u) sw_summary((DWORD)next_present);
}
