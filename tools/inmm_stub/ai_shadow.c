/*
 * ai_shadow.c — read-only shadow of the reviewed normal AI dispatch edge.
 *
 * Only CALL rel32 at 0x0041CBE5 (FUN_0041CB40 normal branch) is replaced. The wrapper records raw state,
 * calls 0x0043F5D0 exactly once, and returns its result unchanged. It never
 * calls an order issuer or writes game-owned fields. This is an ECX-only raw
 * ABI, not a C thiscall/fastcall declaration.
 *
 * Win32/no-CRT. Default OFF; set INMM_AI_SHADOW=1 to opt in. Evidence only.
 */
#include "ai_shadow.h"
#include <windows.h>

#define SHADOW_CALL_SITE       0x0041CBE5u
#define SHADOW_ORIGINAL_TARGET 0x0043F5D0u
#define SHADOW_CALL_LEN        5u
#define SHADOW_MAX_EVENTS      512u
#define SHADOW_POSTLOAD_EVENTS 17u
#define SHADOW_PATH            "C:\\inmm_ai_shadow.jsonl"
#define SHADOW_ENV             "INMM_AI_SHADOW"
#define G4_RUN_ID_ENV          "INMM_G4_RUN_ID"

#define LOAD_CALL_SITE         0x004D6B98u
#define LOAD_ORIGINAL_TARGET   0x00440FF0u

#define PROGRAM_STATE_VA       0x004ED818u
#define COMMITTED_LOCAL_VA     0x004ED848u
#define SCENARIO_SELECTOR_VA   0x009E1DD8u
#define NETWORK_MODE_VA        0x00B93960u
#define NETWORK_MODAL_VA       0x00B93964u
#define RAW_GATE_A_VA          0x00B93982u
#define RAW_GATE_B_VA          0x00B93988u
#define GLOBAL_TICK_VA         0x008924B8u

#define UNIT_EXISTS_VA         0x008990C8u
#define UNIT_ARRAY_VA          0x0066B790u
#define UNIT_STRIDE            0x758u
#define UNIT_COUNT             1200u
#define UNIT_OWNER_OFF         0x08Eu
#define UNIT_HP_OFF            0x0B4u
#define UNIT_COMMAND_OFF       0x290u
#define UNIT_ID_OFF            0x29Cu
#define UNIT_X_OFF             0x2A2u
#define UNIT_Y_OFF             0x2A4u
#define UNIT_PENDING_OFF       0x384u
#define UNIT_PENDING_XY_OFF    0x388u
#define PLAYER_BASE_VA         0x00956770u
#define PLAYER_STRIDE          0x3ABCu
#define PLAYER_AI_OFF          0x002u

typedef struct {
    DWORD edi;
    DWORD esi;
    DWORD ebp;
    DWORD entry_esp;
    DWORD ebx;
    DWORD edx;
    DWORD ecx;
    DWORD eax;
    DWORD entry_flags;
} ai_shadow_frame_t;

static HANDLE g_shadow_log = INVALID_HANDLE_VALUE;
static volatile LONG g_shadow_enabled = 0;
static volatile LONG g_shadow_installed = 0;
static volatile LONG g_shadow_guard = 0;
static volatile LONG g_shadow_events = 0;
static volatile LONG g_postload_events = 0;
static volatile LONG g_postload_active = 0;
static volatile LONG g_sequence = 0;
volatile DWORD g_original_target __attribute__((used, externally_visible)) = SHADOW_ORIGINAL_TARGET;
volatile DWORD g_load_original_target __attribute__((used, externally_visible)) = LOAD_ORIGINAL_TARGET;
static DWORD g_last_tick = 0;
static BOOL g_have_last_tick = FALSE;
static BYTE g_saved_call[SHADOW_CALL_LEN];
static BYTE g_saved_load_call[SHADOW_CALL_LEN];
static DWORD g_load_tpre = 0;
static DWORD g_load_marker_seq = 0;
static char g_run_id[96];

static BOOL read_bytes(DWORD address, void *out, DWORD length)
{
    BYTE *dst = (BYTE *)out;
    DWORD remaining = length;
    DWORD current = address;
    if (length == 0) return TRUE;
    while (remaining != 0) {
        MEMORY_BASIC_INFORMATION mbi;
        DWORD region_end, available, chunk, i;
        const volatile BYTE *src;
        if (!VirtualQuery((LPCVOID)(uintptr_t)current, &mbi, sizeof(mbi))) return FALSE;
        if (mbi.State != MEM_COMMIT ||
            (mbi.Protect & (PAGE_NOACCESS | PAGE_GUARD))) return FALSE;
        region_end = (DWORD)(uintptr_t)mbi.BaseAddress + (DWORD)mbi.RegionSize;
        if (region_end <= current) return FALSE;
        available = region_end - current;
        chunk = available < remaining ? available : remaining;
        src = (const volatile BYTE *)(uintptr_t)current;
        for (i = 0; i < chunk; ++i) dst[i] = src[i];
        dst += chunk;
        current += chunk;
        remaining -= chunk;
    }
    return TRUE;
}

static BOOL read_u16(DWORD address, WORD *out)
{
    return read_bytes(address, out, sizeof(*out));
}

static BOOL read_u32(DWORD address, DWORD *out)
{
    return read_bytes(address, out, sizeof(*out));
}

static BOOL shadow_env_enabled(void)
{
    char value[16];
    DWORD n = GetEnvironmentVariableA(SHADOW_ENV, value, sizeof(value));
    return n == 1 && value[0] == '1';
}

static void shadow_run_id(void)
{
    DWORD n = GetEnvironmentVariableA(G4_RUN_ID_ENV, g_run_id, sizeof(g_run_id));
    if (n == 0 || n >= sizeof(g_run_id)) g_run_id[0] = '\0';
}

static int append_text(char *dst, int pos, int cap, const char *text)
{
    if (pos < 0) pos = 0;
    while (text && *text && pos < cap - 1) dst[pos++] = *text++;
    if (pos < cap) dst[pos] = '\0';
    return pos;
}

static int append_u32(char *dst, int pos, int cap, DWORD value)
{
    char reversed[10];
    int n = 0;
    if (value == 0) return append_text(dst, pos, cap, "0");
    while (value && n < (int)sizeof(reversed)) {
        reversed[n++] = (char)('0' + (value % 10));
        value /= 10;
    }
    while (n > 0 && pos < cap - 1) dst[pos++] = reversed[--n];
    dst[pos] = '\0';
    return pos;
}

static int append_bool(char *dst, int pos, int cap, BOOL value)
{
    return append_text(dst, pos, cap, value ? "true" : "false");
}

static void shadow_write(const char *line, int length)
{
    DWORD written;
    if (g_shadow_log == INVALID_HANDLE_VALUE || length <= 0) return;
    WriteFile(g_shadow_log, line, (DWORD)length, &written, NULL);
    FlushFileBuffers(g_shadow_log);
}

static DWORD next_sequence(void)
{
    return (DWORD)InterlockedIncrement(&g_sequence);
}

static int append_source(char *dst, int pos, int cap, DWORD source_id,
                         DWORD slot, DWORD owner, DWORD command,
                         DWORD pending, DWORD pending_xy)
{
    pos = append_text(dst, pos, cap, "{\"full_id\":");
    pos = append_u32(dst, pos, cap, source_id);
    pos = append_text(dst, pos, cap, ",\"slot\":");
    pos = append_u32(dst, pos, cap, slot);
    pos = append_text(dst, pos, cap, ",\"owner\":");
    pos = append_u32(dst, pos, cap, owner);
    pos = append_text(dst, pos, cap, ",\"command\":");
    pos = append_u32(dst, pos, cap, command);
    pos = append_text(dst, pos, cap, ",\"pending\":");
    pos = append_u32(dst, pos, cap, pending);
    pos = append_text(dst, pos, cap, ",\"pending_xy\":");
    pos = append_u32(dst, pos, cap, pending_xy);
    return append_text(dst, pos, cap, "}");
}

static BOOL raw_mode_ok(DWORD *ps, WORD *local, WORD *scenario,
                        DWORD *network, DWORD *modal, WORD *gate_a, WORD *gate_b,
                        const char **reject)
{
    if (!read_u32(PROGRAM_STATE_VA, ps) || !read_u16(COMMITTED_LOCAL_VA, local) ||
        !read_u16(SCENARIO_SELECTOR_VA, scenario) ||
        !read_u32(NETWORK_MODE_VA, network) ||
        !read_u32(NETWORK_MODAL_VA, modal) ||
        !read_u16(RAW_GATE_A_VA, gate_a) ||
        !read_u16(RAW_GATE_B_VA, gate_b)) {
        *reject = "raw_mode_read_failed";
        return FALSE;
    }
    if (*ps != 3u) { *reject = "program_state_not_3"; return FALSE; }
    if (*local != 1u) { *reject = "committed_local_not_1"; return FALSE; }
    if (*scenario != 0u) { *reject = "scenario_selector_nonzero"; return FALSE; }
    if (*network != 0u) { *reject = "network_mode_nonzero"; return FALSE; }
    if (*modal != 0u) { *reject = "network_modal_nonzero"; return FALSE; }
    if (*gate_a != 0u) { *reject = "raw_gate_a_nonzero"; return FALSE; }
    if (*gate_b != 0u) { *reject = "raw_gate_b_nonzero"; return FALSE; }
    return TRUE;
}

static void find_source(BYTE owner, DWORD *source_id, DWORD *slot,
                        DWORD *hp, DWORD *command, DWORD *pending,
                        DWORD *pending_xy, DWORD *x, DWORD *y, BOOL *live)
{
    DWORD i;
    *source_id = *slot = *hp = *command = *pending = *pending_xy = *x = *y = 0;
    *live = FALSE;
    for (i = 1; i < UNIT_COUNT; ++i) {
        WORD exists, command_word, pending_word, sx, sy;
        DWORD base;
        BYTE unit_owner;
        if (!read_u16(UNIT_EXISTS_VA + i * 2u, &exists) || exists == 0) continue;
        base = UNIT_ARRAY_VA + i * UNIT_STRIDE;
        if (!read_bytes(base + UNIT_OWNER_OFF, &unit_owner, sizeof(unit_owner)) ||
            unit_owner != owner || !read_u32(base + UNIT_HP_OFF, hp) || *hp == 0 ||
            !read_u32(base + UNIT_ID_OFF, source_id) ||
            (*source_id & 0xffffu) != i) continue;
        *slot = i;
        if (!read_u16(base + UNIT_COMMAND_OFF, &command_word)) command_word = 0;
        if (!read_u16(base + UNIT_PENDING_OFF, &pending_word)) pending_word = 0;
        *command = command_word;
        *pending = pending_word;
        read_u32(base + UNIT_PENDING_XY_OFF, pending_xy);
        if (!read_u16(base + UNIT_X_OFF, &sx)) sx = 0;
        if (!read_u16(base + UNIT_Y_OFF, &sy)) sy = 0;
        *x = sx;
        *y = sy;
        *live = TRUE;
        return;
    }
}

/* JSON fields: same_tick_reentry, tick_rewind, postload, entry_ecx,
 * raw_mode, source/full_id/command/pending/pending_xy, decision, original_call. */
static void __attribute__((used)) __cdecl ai_shadow_capture(const ai_shadow_frame_t *frame)
{
    DWORD tick = 0, ps = 0, network = 0, modal = 0;
    WORD local = 0, scenario = 0, gate_a = 0, gate_b = 0;
    DWORD source_id, slot, hp, command, pending, pending_xy, x, y;
    DWORD owner, player;
    BYTE player_ai = 0;
    BOOL live, tick_rewind = FALSE, same_tick = FALSE, mode_ok;
    BOOL ecx_owner_match = FALSE, source_guard = FALSE;
    const char *reject = "";
    DWORD sequence, marker_sequence = 0;
    DWORD pid = GetCurrentProcessId(), tid = GetCurrentThreadId();
    BOOL postload_window;
    char line[1800];
    int p = 0;

    if (g_shadow_enabled == 0 ||
        InterlockedCompareExchange(&g_shadow_guard, 1, 0) != 0) return;
    postload_window = g_postload_active != 0 &&
                      (DWORD)g_postload_events < SHADOW_POSTLOAD_EVENTS;
    if (!postload_window && (DWORD)g_shadow_events >= SHADOW_MAX_EVENTS) {
        InterlockedExchange(&g_shadow_guard, 0);
        return;
    }
    if (postload_window) {
        InterlockedIncrement(&g_postload_events);
        marker_sequence = g_load_marker_seq;
        if ((DWORD)g_postload_events >= SHADOW_POSTLOAD_EVENTS)
            InterlockedExchange(&g_postload_active, 0);
    } else {
        InterlockedIncrement(&g_shadow_events);
    }
    sequence = next_sequence();
    if (!read_u32(GLOBAL_TICK_VA, &tick)) reject = "tick_read_failed";
    owner = tick & 7u;
    if (g_have_last_tick) {
        same_tick = tick == g_last_tick;
        tick_rewind = tick < g_last_tick;
    }
    g_last_tick = tick;
    g_have_last_tick = TRUE;
    mode_ok = reject[0] == '\0' &&
              raw_mode_ok(&ps, &local, &scenario, &network, &modal,
                          &gate_a, &gate_b, &reject);
    player = PLAYER_BASE_VA + owner * PLAYER_STRIDE;
    read_bytes(player + PLAYER_AI_OFF, &player_ai, sizeof(player_ai));
    ecx_owner_match = frame->ecx == player;
    find_source((BYTE)owner, &source_id, &slot, &hp, &command, &pending,
                &pending_xy, &x, &y, &live);
    source_guard = live && player_ai == 1 && ecx_owner_match &&
                   command == 1 && pending == 1;

    p = append_text(line, p, sizeof(line),
                    "{\"schema_version\":2,\"event\":\"ai_shadow\",\"run_id\":\"");
    p = append_text(line, p, sizeof(line), g_run_id);
    p = append_text(line, p, sizeof(line), "\",\"pid\":");
    p = append_u32(line, p, sizeof(line), pid);
    p = append_text(line, p, sizeof(line), ",\"tid\":");
    p = append_u32(line, p, sizeof(line), tid);
    p = append_text(line, p, sizeof(line), ",\"seq\":");
    p = append_u32(line, p, sizeof(line), sequence);
    p = append_text(line, p, sizeof(line), ",\"load_marker_seq\":");
    p = append_u32(line, p, sizeof(line), marker_sequence);
    p = append_text(line, p, sizeof(line), ",\"tick\":");
    p = append_u32(line, p, sizeof(line), tick);
    p = append_text(line, p, sizeof(line), ",\"owner\":");
    p = append_u32(line, p, sizeof(line), owner);
    p = append_text(line, p, sizeof(line), ",\"entry_ecx\":");
    p = append_u32(line, p, sizeof(line), frame->ecx);
    p = append_text(line, p, sizeof(line), ",\"player_ai\":");
    p = append_u32(line, p, sizeof(line), player_ai);
    p = append_text(line, p, sizeof(line), ",\"ecx_owner_match\":");
    p = append_bool(line, p, sizeof(line), ecx_owner_match);
    p = append_text(line, p, sizeof(line), ",\"source_guard\":");
    p = append_bool(line, p, sizeof(line), source_guard);
    p = append_text(line, p, sizeof(line), ",\"same_tick_reentry\":");
    p = append_bool(line, p, sizeof(line), same_tick);
    p = append_text(line, p, sizeof(line), ",\"tick_rewind\":");
    p = append_bool(line, p, sizeof(line), tick_rewind);
    p = append_text(line, p, sizeof(line), ",\"postload\":\"");
    p = append_text(line, p, sizeof(line),
                    tick_rewind ? "INFERRED_TICK_REWIND" : "UNOBSERVED");
    p = append_text(line, p, sizeof(line), "\",\"raw_mode\":{");
    p = append_text(line, p, sizeof(line), "\"program_state\":");
    p = append_u32(line, p, sizeof(line), ps);
    p = append_text(line, p, sizeof(line), ",\"committed_local\":");
    p = append_u32(line, p, sizeof(line), local);
    p = append_text(line, p, sizeof(line), ",\"scenario_selector\":");
    p = append_u32(line, p, sizeof(line), scenario);
    p = append_text(line, p, sizeof(line), ",\"network_mode\":");
    p = append_u32(line, p, sizeof(line), network);
    p = append_text(line, p, sizeof(line), ",\"network_modal\":");
    p = append_u32(line, p, sizeof(line), modal);
    p = append_text(line, p, sizeof(line), ",\"gate_a\":");
    p = append_u32(line, p, sizeof(line), gate_a);
    p = append_text(line, p, sizeof(line), ",\"gate_b\":");
    p = append_u32(line, p, sizeof(line), gate_b);
    p = append_text(line, p, sizeof(line), "},\"source\":{");
    p = append_text(line, p, sizeof(line), "\"full_id\":");
    p = append_u32(line, p, sizeof(line), source_id);
    p = append_text(line, p, sizeof(line), ",\"slot\":");
    p = append_u32(line, p, sizeof(line), slot);
    p = append_text(line, p, sizeof(line), ",\"live\":");
    p = append_bool(line, p, sizeof(line), live);
    p = append_text(line, p, sizeof(line), ",\"hp\":");
    p = append_u32(line, p, sizeof(line), hp);
    p = append_text(line, p, sizeof(line), ",\"command\":");
    p = append_u32(line, p, sizeof(line), command);
    p = append_text(line, p, sizeof(line), ",\"pending\":");
    p = append_u32(line, p, sizeof(line), pending);
    p = append_text(line, p, sizeof(line), ",\"pending_xy\":");
    p = append_u32(line, p, sizeof(line), pending_xy);
    p = append_text(line, p, sizeof(line), ",\"x\":");
    p = append_u32(line, p, sizeof(line), x);
    p = append_text(line, p, sizeof(line), ",\"y\":");
    p = append_u32(line, p, sizeof(line), y);
    p = append_text(line, p, sizeof(line), "},\"decision\":\"");
    p = append_text(line, p, sizeof(line),
                    mode_ok && live ? "SHADOW_POLICY_UNTESTED" : "concrete_rejection");
    p = append_text(line, p, sizeof(line), "\",\"rejection\":\"");
    p = append_text(line, p, sizeof(line),
                    mode_ok && live ? "shadow_policy_not_replayed"
                    : (reject[0] ? reject : "no_live_source"));
    p = append_text(line, p, sizeof(line),
                    "\",\"original_call\":\"forwarded_once\",\"candidate_present\":false,\"candidate_issue_count\":0}\n");
    shadow_write(line, p);
    InterlockedExchange(&g_shadow_guard, 0);
}

/* Exact wrapper: no guessed C convention for FUN_0043F5D0. */
static void __attribute__((naked, noinline)) ai_shadow_call_wrapper(void)
{
    __asm__ __volatile__(
        "pushfl\n\t"
        "pushal\n\t"
        "movl %%esp, %%eax\n\t"
        "pushl %%eax\n\t"
        "call _ai_shadow_capture\n\t"
        "addl $4, %%esp\n\t"
        "popal\n\t"
        "popfl\n\t"
        /* Tail-jump: the original CALL return address and exit EAX/FLAGS
         * are exactly the ones seen by the caller. */
        "jmp *_g_original_target\n\t"
        ::: "memory", "eax"
    );
}

static void __attribute__((used)) __cdecl g4_load_before(DWORD slot)
{
    (void)slot;
    if (g_shadow_enabled == 0) return;
    if (!read_u32(GLOBAL_TICK_VA, &g_load_tpre)) g_load_tpre = 0;
}

static void __attribute__((used)) __cdecl g4_load_complete(DWORD slot, DWORD result)
{
    DWORD tload = 0, owner, source_id, found_slot, hp, command, pending, pending_xy, x, y;
    BOOL live;
    DWORD sequence, pid, tid;
    char line[1200];
    int p = 0;

    if (g_shadow_enabled == 0 || result != 1u ||
        !read_u32(GLOBAL_TICK_VA, &tload)) return;
    owner = (tload + 1u) & 7u;
    find_source((BYTE)owner, &source_id, &found_slot, &hp, &command, &pending,
                &pending_xy, &x, &y, &live);
    sequence = next_sequence();
    pid = GetCurrentProcessId();
    tid = GetCurrentThreadId();
    p = append_text(line, p, sizeof(line),
                    "{\"schema_version\":2,\"event\":\"load_complete\",\"run_id\":\"");
    p = append_text(line, p, sizeof(line), g_run_id);
    p = append_text(line, p, sizeof(line), "\",\"pid\":");
    p = append_u32(line, p, sizeof(line), pid);
    p = append_text(line, p, sizeof(line), ",\"tid\":");
    p = append_u32(line, p, sizeof(line), tid);
    p = append_text(line, p, sizeof(line), ",\"seq\":");
    p = append_u32(line, p, sizeof(line), sequence);
    p = append_text(line, p, sizeof(line), ",\"slot\":");
    p = append_u32(line, p, sizeof(line), slot);
    p = append_text(line, p, sizeof(line), ",\"result\":1,\"tpre\":");
    p = append_u32(line, p, sizeof(line), g_load_tpre);
    p = append_text(line, p, sizeof(line), ",\"tload\":");
    p = append_u32(line, p, sizeof(line), tload);
    p = append_text(line, p, sizeof(line), ",\"next_owner\":");
    p = append_u32(line, p, sizeof(line), owner);
    p = append_text(line, p, sizeof(line), ",\"source\":");
    p = append_source(line, p, sizeof(line), source_id, found_slot, owner,
                      command, pending, pending_xy);
    p = append_text(line, p, sizeof(line),
                    ",\"candidate_present\":false,\"candidate_issue_count\":0}\n");
    shadow_write(line, p);
    g_load_marker_seq = sequence;
    InterlockedExchange(&g_postload_events, 0);
    InterlockedExchange(&g_postload_active, 1);
    (void)live;
}

static void __attribute__((naked, noinline)) g4_load_call_wrapper(void)
{
    __asm__ __volatile__(
        "pushl 4(%%esp)\n\t"
        "call _g4_load_before\n\t"
        "addl $4, %%esp\n\t"
        "pushl 4(%%esp)\n\t"
        "call *_g_load_original_target\n\t"
        "addl $4, %%esp\n\t"
        "pushl %%eax\n\t"
        "pushl 8(%%esp)\n\t"
        "call _g4_load_complete\n\t"
        "addl $4, %%esp\n\t"
        "popl %%eax\n\t"
        "ret\n\t"
        ::: "memory", "eax"
    );
}

static BOOL verify_call_site(DWORD address, const BYTE *expected, BYTE *saved)
{
    if (!read_bytes(address, saved, SHADOW_CALL_LEN)) return FALSE;
    for (unsigned i = 0; i < SHADOW_CALL_LEN; ++i)
        if (saved[i] != expected[i]) return FALSE;
    return TRUE;
}

static BOOL write_call_site(DWORD address, void *wrapper)
{
    BYTE *site = (BYTE *)(uintptr_t)address;
    DWORD old, rel;
    if (!VirtualProtect(site, SHADOW_CALL_LEN, PAGE_EXECUTE_READWRITE, &old)) return FALSE;
    rel = (DWORD)(uintptr_t)wrapper - (address + SHADOW_CALL_LEN);
    site[0] = 0xE8;
    *(DWORD *)(site + 1) = rel;
    VirtualProtect(site, SHADOW_CALL_LEN, old, &old);
    FlushInstructionCache(GetCurrentProcess(), site, SHADOW_CALL_LEN);
    return TRUE;
}

static void rollback_call_site(DWORD address, const BYTE *saved)
{
    BYTE *site = (BYTE *)(uintptr_t)address;
    DWORD old;
    if (!VirtualProtect(site, SHADOW_CALL_LEN, PAGE_EXECUTE_READWRITE, &old)) return;
    for (unsigned i = 0; i < SHADOW_CALL_LEN; ++i) site[i] = saved[i];
    VirtualProtect(site, SHADOW_CALL_LEN, old, &old);
    FlushInstructionCache(GetCurrentProcess(), site, SHADOW_CALL_LEN);
}

int ai_shadow_install(void)
{
    if (!shadow_env_enabled()) return 1;
    if (InterlockedCompareExchange(&g_shadow_installed, 1, 0) != 0) return 1;
    shadow_run_id();
    g_shadow_log = CreateFileA(SHADOW_PATH, GENERIC_WRITE, FILE_SHARE_READ,
                               NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    static const BYTE expected_shadow[SHADOW_CALL_LEN] = { 0xE8, 0xE6, 0x29, 0x02, 0x00 };
    static const BYTE expected_load[SHADOW_CALL_LEN] = { 0xE8, 0x53, 0xA4, 0xF6, 0xFF };
    if (g_shadow_log == INVALID_HANDLE_VALUE ||
        !verify_call_site(SHADOW_CALL_SITE, expected_shadow, g_saved_call) ||
        !verify_call_site(LOAD_CALL_SITE, expected_load, g_saved_load_call) ||
        !write_call_site(SHADOW_CALL_SITE, ai_shadow_call_wrapper) ||
        !write_call_site(LOAD_CALL_SITE, g4_load_call_wrapper)) {
        if (g_saved_call[0] == expected_shadow[0])
            rollback_call_site(SHADOW_CALL_SITE, g_saved_call);
        if (g_saved_load_call[0] == expected_load[0])
            rollback_call_site(LOAD_CALL_SITE, g_saved_load_call);
        if (g_shadow_log != INVALID_HANDLE_VALUE) CloseHandle(g_shadow_log);
        g_shadow_log = INVALID_HANDLE_VALUE;
        InterlockedExchange(&g_shadow_installed, 0);
        return 0;
    }
    InterlockedExchange(&g_shadow_enabled, 1);
    return 1;
}

void ai_shadow_detach(void)
{
    /* Process-lifetime hook: do not rewrite the EXE call site during detach.
     * Any late edge reaches the wrapper, which observes disabled state and
     * tail-jumps to the original target without logging. */
    InterlockedExchange(&g_shadow_enabled, 0);
    if (g_shadow_log != INVALID_HANDLE_VALUE) CloseHandle(g_shadow_log);
    g_shadow_log = INVALID_HANDLE_VALUE;
    InterlockedExchange(&g_shadow_installed, 0);
}
