/**
 * sfx_hook.c — inline trampoline hook for the original SFX dispatch function.
 *
 * Target: FUN_00445930 @ 0x00445930 (syw2plus_original.exe, base 0x00400000).
 *   int __stdcall FUN_00445930(short unit_type, short event_type,
 *                              char *out_path, char *out2);
 *
 * Prologue (objdump, confirmed):
 *   00445930: 53                push ebx
 *   00445931: 66 8b 5c 24 08    mov  bx,[esp+8]      ; param_1 (unit_type)
 *   00445936: 56                push esi             ; <- continue here
 * First two instructions = 6 bytes; relocated into the trampoline so a 5-byte
 * JMP can be planted at the entry without splitting an instruction.
 *
 * The hook runs the original (filling out_path with the selected YAV variant),
 * then logs the SFX *event* to C:\inmm_sfx_log.jsonl:
 *   {ts, pid, event:"sfx_dispatch", program_state, global_tick,
 *    unit_type, event_type, ret, path}
 *
 * Win32-only (no msvcrt), matching inmm_stub.c / asset_hook.c constraints.
 */

#include "sfx_hook.h"
#include "control_state_bridge.h"
#include <windows.h>

#define SFX_VA          0x00445930u
#define PROLOGUE_LEN    6u            /* push ebx + mov bx,[esp+8] */
#define JMP_LEN         5u
#define GLOBAL_TICK_VA  0x009B5210u

typedef int (__stdcall *sfx_fn_t)(short, short, char *, char *);

static sfx_fn_t      g_sfx_orig    = NULL;  /* trampoline → original body */
static HANDLE        g_sfx_log     = INVALID_HANDLE_VALUE;
static volatile LONG g_in_sfx      = 0;     /* re-entrancy guard */
static volatile LONG g_probe_active = 0;    /* 1 while sfx_probe_live_units runs */

/* ------------------------------------------------------------------ */
static BOOL read_u32_safe(DWORD va, DWORD *out)
{
    MEMORY_BASIC_INFORMATION mbi;
    if (!VirtualQuery((LPCVOID)(uintptr_t)va, &mbi, sizeof(mbi))) return FALSE;
    if (mbi.State != MEM_COMMIT) return FALSE;
    if (mbi.Protect & (PAGE_NOACCESS | PAGE_GUARD)) return FALSE;
    *out = *(volatile DWORD *)(uintptr_t)va;
    return TRUE;
}

/* Copy src into dst as a JSON-safe string (escape backslash + quote). */
static void json_escape(const char *src, char *dst, int dst_cap)
{
    int di = 0;
    if (!src) { dst[0] = 0; return; }
    for (int si = 0; src[si] && di < dst_cap - 2; ++si) {
        char c = src[si];
        if (c == '\\' || c == '"') dst[di++] = '\\';
        dst[di++] = c;
    }
    dst[di] = 0;
}

static void sfx_log_write(short unit_type, short event_type,
                          int ret, const char *path)
{
    if (g_sfx_log == INVALID_HANDLE_VALUE) return;

    DWORD ps = 0xFFFFFFFFu;
    csb_read_state(&ps);
    DWORD tick = 0;
    read_u32_safe(GLOBAL_TICK_VA, &tick);

    char safe_path[512];
    json_escape(path, safe_path, (int)sizeof(safe_path));

    const char *trigger = g_probe_active ? "probe" : "natural";
    char line[768];
    int n = wsprintfA(line,
        "{\"ts\":%u,\"pid\":%u,\"event\":\"sfx_dispatch\",\"trigger\":\"%s\","
        "\"program_state\":%u,\"global_tick\":%u,"
        "\"unit_type\":%d,\"event_type\":%d,\"ret\":%d,\"path\":\"%s\"}\n",
        (unsigned)GetTickCount(), (unsigned)GetCurrentProcessId(), trigger,
        (unsigned)ps, (unsigned)tick,
        (int)unit_type, (int)event_type, ret, safe_path);

    DWORD written = 0;
    WriteFile(g_sfx_log, line, n, &written, NULL);
    FlushFileBuffers(g_sfx_log);
}

/* ------------------------------------------------------------------ */
/* The hook: run original first so out_path is populated, then log.    */
/* ------------------------------------------------------------------ */
static int __stdcall sfx_hook(short unit_type, short event_type,
                              char *out_path, char *out2)
{
    int ret = g_sfx_orig(unit_type, event_type, out_path, out2);
    if (InterlockedExchange(&g_in_sfx, 1) == 0) {
        sfx_log_write(unit_type, event_type, ret,
                      (ret && out_path) ? out_path : "");
        InterlockedExchange(&g_in_sfx, 0);
    }
    return ret;
}

/* ------------------------------------------------------------------ */
int sfx_hook_install(void)
{
    BYTE *target = (BYTE *)(uintptr_t)SFX_VA;

    /* Sanity: the entry must still be the known prologue (53 66 8b 5c 24 08).
     * Guards against a mismatched EXE build silently corrupting code. */
    static const BYTE expect[PROLOGUE_LEN] = { 0x53, 0x66, 0x8b, 0x5c, 0x24, 0x08 };
    {
        MEMORY_BASIC_INFORMATION mbi;
        if (!VirtualQuery(target, &mbi, sizeof(mbi))) return 0;
        if (mbi.State != MEM_COMMIT) return 0;
        for (unsigned i = 0; i < PROLOGUE_LEN; ++i)
            if (target[i] != expect[i]) return 0;
    }

    /* Allocate executable trampoline: [6 original bytes][JMP to SFX_VA+6]. */
    BYTE *tramp = (BYTE *)VirtualAlloc(NULL, PROLOGUE_LEN + JMP_LEN,
                                       MEM_COMMIT | MEM_RESERVE,
                                       PAGE_EXECUTE_READWRITE);
    if (!tramp) return 0;
    for (unsigned i = 0; i < PROLOGUE_LEN; ++i) tramp[i] = target[i];
    tramp[PROLOGUE_LEN] = 0xE9; /* JMP rel32 */
    *(DWORD *)(tramp + PROLOGUE_LEN + 1) =
        (DWORD)(SFX_VA + PROLOGUE_LEN) - ((DWORD)(uintptr_t)tramp + PROLOGUE_LEN + JMP_LEN);
    g_sfx_orig = (sfx_fn_t)tramp;

    /* Open the event log before planting the hook (avoids logging from hook). */
    g_sfx_log = CreateFileA("C:\\inmm_sfx_log.jsonl",
                            GENERIC_WRITE, FILE_SHARE_READ,
                            NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);

    /* Plant JMP sfx_hook at the entry (5 bytes), NOP the 6th leftover byte. */
    DWORD old = 0;
    if (!VirtualProtect(target, PROLOGUE_LEN, PAGE_EXECUTE_READWRITE, &old)) {
        VirtualFree(tramp, 0, MEM_RELEASE);
        g_sfx_orig = NULL;
        return 0;
    }
    target[0] = 0xE9; /* JMP rel32 */
    *(DWORD *)(target + 1) = (DWORD)(uintptr_t)sfx_hook - (SFX_VA + JMP_LEN);
    target[5] = 0x90; /* NOP — leftover byte of the relocated mov */
    VirtualProtect(target, PROLOGUE_LEN, old, &old);
    FlushInstructionCache(GetCurrentProcess(), target, PROLOGUE_LEN);

    return 1;
}

/* ------------------------------------------------------------------ */
/* Live-unit SFX resolver probe (#358 AC3).                            */
/* ------------------------------------------------------------------ */
#define PROBE_PROGRAM_STATE_VA 0x004ED818u
#define PROBE_UD_EXISTS_VA     0x008990C8u
#define PROBE_UD_ARRAY_VA      0x0066B790u
#define PROBE_UD_STRIDE        0x758u
#define PROBE_UD_COUNT         1200
#define PROBE_OFF_UNIT_TYPE    0x08Du   /* byte */
#define SFX_TABLE_LOADER_VA    0x00445110u  /* FUN_00445110: builds DAT_00c19358 */
#define SFX_TABLE_COUNT_VA     0x00C19678u  /* DAT_00c19678: entry count */

static volatile LONG g_probe_done = 0;

int sfx_probe_live_units(void)
{
    /* require the hook (so calls are logged) and in-game state */
    if (g_sfx_orig == NULL) return 0;
    DWORD ps = 0;
    if (!read_u32_safe(PROBE_PROGRAM_STATE_VA, &ps) || ps != 3) return 0;
    if (InterlockedExchange(&g_probe_done, 1) != 0) return 0; /* once */

    /* Ensure the engine's SFX table is populated. Depending on how far the
     * chain-inject init progressed, DAT_00c19358 may or may not already be
     * loaded (observed count: 0 early, 94 once init completed). If empty, call
     * the engine's OWN table loader (FUN_00445110) to load the authentic gamejvi
     * mapping; the call is idempotent (a no-op when already populated). */
    DWORD tbl_before = 0, tbl_after = 0;
    read_u32_safe(SFX_TABLE_COUNT_VA, &tbl_before);
    if (tbl_before == 0) {
        ((void (*)(void))(uintptr_t)SFX_TABLE_LOADER_VA)();
    }
    read_u32_safe(SFX_TABLE_COUNT_VA, &tbl_after);
    /* diagnostic line so we can see whether the loader populated the table */
    if (g_sfx_log != INVALID_HANDLE_VALUE) {
        char diag[160];
        int dn = wsprintfA(diag,
            "{\"event\":\"sfx_table_probe\",\"count_before\":%u,\"count_after\":%u}\n",
            (unsigned)tbl_before, (unsigned)tbl_after);
        DWORD w = 0; WriteFile(g_sfx_log, diag, dn, &w, NULL);
    }

    typedef int (__stdcall *sfx_call_t)(short, short, char *, char *);
    sfx_call_t resolve = (sfx_call_t)(uintptr_t)SFX_VA; /* hooked entry → logged */

    /* event types from FUN_00445110 table loader: 4=die, 5=recover, 6, 0xb=train */
    static const short EVENTS[] = { 4, 5, 6, 0xb };
    char buf_a[160];
    char buf_b[160];
    int calls = 0;

    InterlockedExchange(&g_probe_active, 1);

    /* (1) probe the REAL unit_type of each live in-game unit (proves the
     *     dispatch works for units actually on the map). */
    for (int i = 0; i < PROBE_UD_COUNT; ++i) {
        SHORT ex = *((volatile SHORT *)(uintptr_t)(PROBE_UD_EXISTS_VA + (DWORD)i * 2));
        if (ex == 0) continue;
        DWORD base = PROBE_UD_ARRAY_VA + (DWORD)i * PROBE_UD_STRIDE;
        BYTE unit_type = *((volatile BYTE *)(uintptr_t)(base + PROBE_OFF_UNIT_TYPE));
        for (unsigned e = 0; e < sizeof(EVENTS) / sizeof(EVENTS[0]); ++e) {
            buf_a[0] = 0; buf_b[0] = 0;
            resolve((short)unit_type, EVENTS[e], buf_a, buf_b);
            ++calls;
        }
    }

    /* (2) sweep the full unit_type space so the engine's complete authentic
     *     (unit_type,event_type)->YAV dispatch mapping is captured. Entries that
     *     exist (e.g. general units 0x4c..0x65) return a resolved YAV path;
     *     others return ret=0 (no SFX) — both are authentic engine answers. */
    for (short ut = 0; ut < 200; ++ut) {
        for (unsigned e = 0; e < sizeof(EVENTS) / sizeof(EVENTS[0]); ++e) {
            buf_a[0] = 0; buf_b[0] = 0;
            resolve(ut, EVENTS[e], buf_a, buf_b);
            ++calls;
        }
    }

    InterlockedExchange(&g_probe_active, 0);
    return calls;
}
