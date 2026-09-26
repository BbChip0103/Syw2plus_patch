/**
 * inmm_stub.c — _inmm.dll 래핑 stub DLL (C7 내부 계측 버전)
 *
 * 전략: EXE가 import하는 4개 함수를 가로채고, WINMM 직접 포워딩 + 내부 상태 계측.
 *       _inmm_orig.dll 프록시 방식은 LoadLibraryA로 인한 DllMain 이중 실행(DirectSound/COM
 *       초기화 충돌)으로 크래시 확인 → 제거. 순수 winmm/mci 직접 구현으로 변경.
 *
 * EXE import 함수:
 *   _ciSendCommandA  (ordinal 50)  → mciSendCommandA (WINMM)
 *   _imeBeginPeriod  (ordinal 101) → timeBeginPeriod (WINMM)
 *   _imeEndPeriod    (ordinal 102) → timeEndPeriod (WINMM)
 *   _imeGetTime      (ordinal 105) → timeGetTime (WINMM)
 *
 * 계측 대상:
 *   PROGRAM_STATE  0x4ED818  — 현재 게임 상태 (PS=9:타이틀, PS=3:인게임 등)
 *   GLOBAL_TICK    0x9B5210  — 누적 게임 틱
 *
 * 중요: Win32 전용 구현 — msvcrt.dll 의존성 없음.
 *       CRT 함수(fopen/fprintf/time) 대신 Win32 API(CreateFileA/WriteFile/GetLocalTime) 사용.
 */

#include <windows.h>
#include <mmsystem.h>
#include <stdarg.h>
#include "control_logging.h"
#include "control_protocol.h"
#include "control_executor.h"
#include "control_handler_bridge.h"
#include "asset_hook.h"
#include "sfx_hook.h"
#include "direct_draw_trace.h"
#include "final_d3d9_trace.h"
#include "ai_shadow.h"

/* ------------------------------------------------------------------ */
/* 정적 DLL 의존성 강제 — _inmm_orig.dll import table 매칭            */
/* ------------------------------------------------------------------ */
/* 원본 _inmm_orig.dll은 DSOUND/MSVFW32/MSACM32를 정적 import한다.
   이 DLL들이 EXE main() 전에 로드되어야 Wine의 DirectDraw가
   올바른 백엔드(GDI/팔레트 지원)를 선택한다. */
extern __declspec(dllimport) HRESULT WINAPI
    DirectSoundCreate(const GUID *lpGuid, void **ppDS, IUnknown *pUnkOuter);
extern __declspec(dllimport) BOOL WINAPI
    ICInfo(DWORD fccType, DWORD fccHandler, void *lpicinfo);
extern __declspec(dllimport) MMRESULT WINAPI
    acmDriverEnum(void *fnCallback, DWORD dwInstance, DWORD fdwEnum);

/* volatile: 옵티마이저가 참조를 제거하지 못하게 함 */
static void * volatile _dep_dsound  = (void *)DirectSoundCreate;
static void * volatile _dep_msvfw32 = (void *)ICInfo;
static void * volatile _dep_msacm32 = (void *)acmDriverEnum;

/* ------------------------------------------------------------------ */
/* 로그 경로                                                          */
/* ------------------------------------------------------------------ */
#define LOG_PATH    "C:\\inmm_stub.log"
#define STATE_JSONL "C:\\inmm_state_log.jsonl"
#define MCI_JSONL   "C:\\inmm_mci_log.jsonl"
#define WATCH_JSONL "C:\\inmm_watch_log.jsonl"

/* ------------------------------------------------------------------ */
/* 계측 대상 주소                                                     */
/* ------------------------------------------------------------------ */
#define PROGRAM_STATE_VA  0x004ED818u
#define GLOBAL_TICK_VA    0x009B5210u

/* ------------------------------------------------------------------ */
/* watch 항목 테이블                                                  */
/* ------------------------------------------------------------------ */
typedef struct {
    const char *name;
    DWORD       va;
    DWORD       last_val;
    BOOL        last_valid;
} WatchEntry;

static WatchEntry g_watch_table[] = {
    { "PROGRAM_STATE",   0x004ED818u, 0xFFFFFFFFu, FALSE },
    { "GLOBAL_TICK",     0x009B5210u, 0xFFFFFFFFu, FALSE },
    { "UNIT_TABLE_0",    0x009B5228u, 0xFFFFFFFFu, FALSE },
    { "UNIT0_QUEUE_CNT", 0x0066BB2Cu, 0xFFFFFFFFu, FALSE },
    /* #365 BUG-05: production-timing gate read by FUN_0043fdd0 as
     * ((byte)DAT_008924b8 & 7) == 0. Observing its live value vs GLOBAL_TICK
     * at PS=3 resolves whether it is a free-running tick counter (→ true
     * 8-tick cadence) or a small static enum (→ the 8-tick label is wrong).
     * Read-only watch; no code patch. */
    { "BUG05_PRODGATE_008924b8", 0x008924B8u, 0xFFFFFFFFu, FALSE },
};

#define WATCH_TABLE_SIZE ((int)(sizeof(g_watch_table) / sizeof(g_watch_table[0])))

/* ------------------------------------------------------------------ */
/* 파일 핸들 (Win32 — msvcrt FILE* 사용 금지)                        */
/* ------------------------------------------------------------------ */
static HANDLE g_log            = INVALID_HANDLE_VALUE;
static HANDLE g_state_log      = INVALID_HANDLE_VALUE;
static HANDLE g_mci_log        = INVALID_HANDLE_VALUE;
static HANDLE g_watch_log      = INVALID_HANDLE_VALUE;
static HANDLE g_unit_tick_log  = INVALID_HANDLE_VALUE;
static DWORD  g_last_dump_tick = 0xFFFFFFFFu;
#define UNIT_TICK_DUMP_INTERVAL 50u

/* ------------------------------------------------------------------ */
/* 기타 전역                                                          */
/* ------------------------------------------------------------------ */
static volatile LONG g_call_count     = 0;
static LONG          g_diag_dumped    = 0;
static volatile LONG g_initialized    = 0;
static volatile LONG g_worker_started = 0;
static HANDLE        g_worker_thread  = NULL;
static volatile LONG g_worker_stop    = 0;

/* ------------------------------------------------------------------ */
/* 안전 메모리 읽기 헬퍼                                              */
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

static BOOL write_u32_safe(DWORD va, DWORD val)
{
    MEMORY_BASIC_INFORMATION mbi;
    if (!VirtualQuery((LPCVOID)(uintptr_t)va, &mbi, sizeof(mbi))) return FALSE;
    if (mbi.State != MEM_COMMIT) return FALSE;
    if (mbi.Protect & (PAGE_NOACCESS | PAGE_GUARD | PAGE_READONLY)) return FALSE;
    *(volatile DWORD *)(uintptr_t)va = val;
    return TRUE;
}

/* CD-BGM 옵션 플래그 (FUN_004248f0/0041b560 등이 ==1 검사 후
 * FUN_00406500(트랙2 재생) 호출).  wine 환경 기본값 0이라 인게임 진입 시
 * MCI_PLAY가 영영 발화하지 않는다 — INMM_STUB_FORCE_MUSIC_ON=1 이면 워커가
 * 이 플래그를 1로 유지해 원본의 트랙 선택 로직을 그대로 발화시킨다. */
#define MUSIC_FLAG_VA 0x00669598u

static void log_msg(const char *fmt, ...);

static void force_music_flag_if_requested(void)
{
    static int s_enabled = -1;  /* -1 미확인 / 0 off / 1 on */
    if (s_enabled < 0) {
        char v[8];
        s_enabled =
            (GetEnvironmentVariableA("INMM_STUB_FORCE_MUSIC_ON", v, sizeof(v)) > 0)
                ? 1 : 0;
    }
    if (s_enabled != 1) return;
    DWORD cur = 0;
    if (read_u32_safe(MUSIC_FLAG_VA, &cur) && cur != 1) {
        if (write_u32_safe(MUSIC_FLAG_VA, 1)) {
            log_msg("[inmm_stub] FORCE_MUSIC_ON: 0x%08X %u -> 1\n",
                    MUSIC_FLAG_VA, (unsigned)cur);
        }
    }
}

/* ------------------------------------------------------------------ */
/* Win32 파일 열기 헬퍼 (append 모드)                                */
/* ------------------------------------------------------------------ */
static HANDLE open_append(const char *path)
{
    HANDLE h = CreateFileA(path, GENERIC_WRITE, FILE_SHARE_READ,
                           NULL, OPEN_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (h != INVALID_HANDLE_VALUE)
        SetFilePointer(h, 0, NULL, FILE_END);
    return h;
}

static void file_write(HANDLE h, const char *buf)
{
    if (h == INVALID_HANDLE_VALUE) return;
    DWORD written;
    WriteFile(h, buf, lstrlenA(buf), &written, NULL);
}

/* ------------------------------------------------------------------ */
/* 텍스트 로그 헬퍼                                                   */
/* ------------------------------------------------------------------ */
static void log_init(void)
{
    g_log = open_append(LOG_PATH);
    if (g_log == INVALID_HANDLE_VALUE) return;

    SYSTEMTIME st;
    GetLocalTime(&st);
    char buf[128];
    wsprintfA(buf, "\n[inmm_stub] === Session start: %04u-%02u-%02u %02u:%02u:%02u ===\n",
              st.wYear, st.wMonth, st.wDay,
              st.wHour, st.wMinute, st.wSecond);
    file_write(g_log, buf);
}

static void log_msg(const char *fmt, ...)
{
    if (g_log == INVALID_HANDLE_VALUE) return;
    char buf[1024];
    va_list args;
    va_start(args, fmt);
    wvsprintfA(buf, fmt, args);
    va_end(args);
    file_write(g_log, buf);
}

/* ------------------------------------------------------------------ */
/* JSONL 파일 초기화                                                  */
/* ------------------------------------------------------------------ */
static void jsonl_init(void)
{
    g_state_log = open_append(STATE_JSONL);
    g_mci_log   = open_append(MCI_JSONL);
    g_watch_log = open_append(WATCH_JSONL);
    /* control_log_init은 DLL_PROCESS_ATTACH에서 먼저 호출됨 — 여기선 생략 */
}

/* ------------------------------------------------------------------ */
/* watch_log JSONL 기록                                               */
/* ------------------------------------------------------------------ */
static void jsonl_write_watch(const char *name, DWORD va,
                               DWORD value, DWORD global_tick)
{
    if (g_watch_log == INVALID_HANDLE_VALUE) return;
    char buf[512];
    wsprintfA(buf,
              "{\"ts_ms\":%u,\"pid\":%u,\"event\":\"watch_change\","
              "\"name\":\"%s\",\"address\":\"0x%08X\","
              "\"value_u32\":%u,\"global_tick\":%u}\n",
              (unsigned)GetTickCount(),
              (unsigned)GetCurrentProcessId(),
              name, (unsigned)va, (unsigned)value, (unsigned)global_tick);
    file_write(g_watch_log, buf);
}

/* ------------------------------------------------------------------ */
/* state_log JSONL 기록                                               */
/* ------------------------------------------------------------------ */
static void jsonl_write_state(const char *event,
                               DWORD program_state, DWORD global_tick)
{
    if (g_state_log == INVALID_HANDLE_VALUE) return;
    char buf[512];
    wsprintfA(buf,
              "{\"ts_ms\":%u,\"pid\":%u,\"event\":\"%s\","
              "\"program_state\":%u,\"global_tick\":%u}\n",
              (unsigned)GetTickCount(),
              (unsigned)GetCurrentProcessId(),
              event, (unsigned)program_state, (unsigned)global_tick);
    file_write(g_state_log, buf);
}

/* ------------------------------------------------------------------ */
/* mci_log JSONL 기록                                                 */
/* ------------------------------------------------------------------ */
static void jsonl_write_mci(DWORD program_state, DWORD global_tick,
                              const char *command)
{
    if (g_mci_log == INVALID_HANDLE_VALUE) return;

    const char *cmd = (command && command[0]) ? command : "(null)";
    char safe_cmd[256];
    int si = 0, ci = 0;
    while (cmd[ci] && si < (int)sizeof(safe_cmd) - 3) {
        if (cmd[ci] == '"' || cmd[ci] == '\\') safe_cmd[si++] = '\\';
        safe_cmd[si++] = cmd[ci++];
    }
    safe_cmd[si] = '\0';

    char buf[512];
    wsprintfA(buf,
              "{\"ts_ms\":%u,\"pid\":%u,\"event\":\"mci_call\","
              "\"program_state\":%u,\"global_tick\":%u,"
              "\"command\":\"%s\"}\n",
              (unsigned)GetTickCount(),
              (unsigned)GetCurrentProcessId(),
              (unsigned)program_state, (unsigned)global_tick, safe_cmd);
    file_write(g_mci_log, buf);
}

/* ------------------------------------------------------------------ */
/* 프로세스 identity + image base 1회 기록                            */
/* ------------------------------------------------------------------ */
static void dump_process_identity_once(void)
{
    if (InterlockedCompareExchange(&g_diag_dumped, 1, 0) != 0) return;

    char path[MAX_PATH];
    DWORD pid = GetCurrentProcessId();
    DWORD n = GetModuleFileNameA(NULL, path, sizeof(path));
    if (n == 0 || n >= sizeof(path)) lstrcpyA(path, "(unknown)");

    HMODULE hbase = GetModuleHandleA(NULL);
    char buf[512];
    wsprintfA(buf, "[inmm_stub] process pid=%u image=%s image_base=0x%08X\n",
              (unsigned)pid, path, (unsigned)(uintptr_t)hbase);
    file_write(g_log, buf);

    DWORD ps = 0, tick = 0;
    BOOL ps_ok   = read_u32_safe(PROGRAM_STATE_VA, &ps);
    BOOL tick_ok = read_u32_safe(GLOBAL_TICK_VA,   &tick);
    wsprintfA(buf,
              "[inmm_stub] probe PROGRAM_STATE(0x%08X)=%u(%s) "
              "GLOBAL_TICK(0x%08X)=%u(%s)\n",
              PROGRAM_STATE_VA, (unsigned)ps,   ps_ok   ? "ok" : "FAIL",
              GLOBAL_TICK_VA,   (unsigned)tick, tick_ok ? "ok" : "FAIL");
    file_write(g_log, buf);
}

/* ------------------------------------------------------------------ */
/* lazy-init: 첫 export 호출 시 1회만 실행                            */
/* ------------------------------------------------------------------ */
static void ensure_initialized(void)
{
    if (InterlockedCompareExchange(&g_initialized, 1, 0) != 0) return;

    log_init();
    jsonl_init();
    file_write(g_log, "[inmm_stub] pure-winmm mode (no proxy)\n");
    dump_process_identity_once();
}

/* ------------------------------------------------------------------ */
/* ------------------------------------------------------------------ */
/* Per-tick unit dump (PS=3 전용)                                      */
/* compare_runs.py 호환: logic_tick, unit_id, x, y, hp               */
/* ------------------------------------------------------------------ */
#define UD_EXISTS_VA  0x008990C8u
#define UD_ARRAY_VA   0x0066B790u
#define UD_STRIDE     0x758u
#define UD_COUNT      1200

static void dump_units_at_tick(DWORD logic_tick)
{
    static char    line[256];
    static DWORD   g_dump_seq = 0;
    static DWORD   g_prev_tick = 0xFFFFFFFFu;
    /* sequential unit_id per snapshot (reset each tick) */
    int seq_uid = 0;
    if (g_unit_tick_log == INVALID_HANDLE_VALUE) {
        g_unit_tick_log = CreateFileA("C:\\inmm_unit_ticks.jsonl",
            GENERIC_WRITE, FILE_SHARE_READ, NULL,
            CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
        if (g_unit_tick_log == INVALID_HANDLE_VALUE) return;
        g_dump_seq = 0;
    }
    /* advance sequential dump tick each call */
    if (logic_tick != g_prev_tick) {
        if (g_prev_tick != 0xFFFFFFFFu) g_dump_seq++;
        g_prev_tick = logic_tick;
    }
    for (int i = 0; i < UD_COUNT; i++) {
        SHORT ex = *((volatile SHORT*)(uintptr_t)(UD_EXISTS_VA + (DWORD)i * 2));
        if (ex == 0) continue;
        DWORD base  = UD_ARRAY_VA + (DWORD)i * UD_STRIDE;
        WORD  x     = *((volatile WORD *)(uintptr_t)(base + 0x2A2));
        WORD  y     = *((volatile WORD *)(uintptr_t)(base + 0x2A4));
        DWORD hp    = *((volatile DWORD*)(uintptr_t)(base + 0x0B4));
        BYTE  utype = *((volatile BYTE *)(uintptr_t)(base + 0x08D));
        BYTE  owner = *((volatile BYTE *)(uintptr_t)(base + 0x08E));
        WORD  kind  = *((volatile WORD *)(uintptr_t)(base + 0x290));
        DWORD local_plr = 0xFFFFFFFFu;
        read_u32_safe(0x00B63FC4u, &local_plr);
        DWORD wr;
        int len = wsprintfA(line,
            "{\"logic_tick\":%u,\"unit_id\":%d,\"x\":%d,\"y\":%d,\"hp\":%d,\"unit_type\":%d,\"owner\":%d,\"local_plr\":%d,\"kind\":%d,\"command_kind\":0,\"ai_state\":\"\"}\n",
            (unsigned)g_dump_seq, seq_uid, (int)x, (int)y, (int)hp, (int)utype, (int)owner, (int)local_plr, (int)kind);
        WriteFile(g_unit_tick_log, line, (DWORD)len, &wr, NULL);
        seq_uid++;
    }
}

/* S2 polling worker                                                   */
/* ------------------------------------------------------------------ */
static DWORD WINAPI worker_proc(LPVOID param)
{
    (void)param;
    DWORD last_ps   = 0xFFFFFFFFu;
    DWORD last_tick = 0xFFFFFFFFu;

    while (!g_worker_stop) {
        Sleep(30);

        force_music_flag_if_requested();

        /* --- control protocol polling (B2 + R2) --- */
        {
            control_request_t req;
            BOOL parse_ok = FALSE;
            if (control_protocol_poll(&req, &parse_ok)) {
                control_result_t res;
                /* R2: zero-init로 확장 필드 초기값 보장 */
                {
                    char *zp = (char *)&res;
                    for (unsigned i = 0; i < sizeof(res); ++i) zp[i] = 0;
                    res.state_reached = 0xFFFFFFFFu;
                    res.start_state   = 0xFFFFFFFFu;
                    res.end_state     = 0xFFFFFFFFu;
                }

                if (!parse_ok) {
                    char detail[192];
                    const char *miss = req.missing_fields[0] ? req.missing_fields
                                                              : "unknown";
                    wsprintfA(detail, "missing=%s", miss);
                    lstrcpyA(res.request_id,
                             req.request_id[0] ? req.request_id : "-");
                    res.ok = FALSE;
                    lstrcpyA(res.reason,      "malformed_request");
                    lstrcpyA(res.reason_axis, CP_REASON_AXIS_LOGIC);
                    lstrcpyA(res.goal,        req.goal[0] ? req.goal : "-");
                    control_log_event(res.request_id, "parse_error",
                                      res.goal,
                                      0xFFFFFFFF, 0xFFFFFFFF, "-", detail);
                } else {
                    control_log_event(req.request_id, "parse_success",
                                      req.goal,
                                      0xFFFFFFFF, 0xFFFFFFFF, "-", "");
                    control_executor_run(&req, &res);
                }
                control_protocol_write_result(&res);
            }
        }

        DWORD ps = 0, tick = 0;
        BOOL ps_ok   = read_u32_safe(PROGRAM_STATE_VA, &ps);
        BOOL tick_ok = read_u32_safe(GLOBAL_TICK_VA,   &tick);

        if (!ps_ok && !tick_ok) continue;

        if (ps_ok && ps != last_ps) {
            jsonl_write_state("state_change", ps, tick_ok ? tick : last_tick);
            last_ps = ps;
        }
        if (tick_ok && tick != last_tick && tick > last_tick) {
            jsonl_write_state("tick_advance", ps_ok ? ps : last_ps, tick);
            last_tick = tick;
        }

        DWORD cur_tick = tick_ok ? tick : last_tick;
        for (int wi = 0; wi < WATCH_TABLE_SIZE; ++wi) {
            DWORD wval = 0;
            if (!read_u32_safe(g_watch_table[wi].va, &wval)) continue;
            if (!g_watch_table[wi].last_valid ||
                wval != g_watch_table[wi].last_val) {
                jsonl_write_watch(g_watch_table[wi].name,
                                  g_watch_table[wi].va,
                                  wval, cur_tick);
                g_watch_table[wi].last_val  = wval;
                g_watch_table[wi].last_valid = TRUE;
            }
        }

        /* #358 AC3: once in-game, probe the engine SFX resolver on live units'
         * real types to capture the authentic unit_type->YAV dispatch mapping
         * (synthetic trigger, authentic dispatch; logged with "trigger":"probe"). */
        if (ps_ok && ps == 3) {
            sfx_probe_live_units();
        }

        /* per-tick unit dump (PS=3 자동) */
        if (ps_ok && ps == 3 && tick_ok && tick != 0u) {
            if (g_last_dump_tick == 0xFFFFFFFFu ||
                (tick > g_last_dump_tick &&
                 tick - g_last_dump_tick >= UNIT_TICK_DUMP_INTERVAL)) {
                dump_units_at_tick(tick);
                g_last_dump_tick = tick;
            }
        } else if (g_unit_tick_log != INVALID_HANDLE_VALUE &&
                   !(ps_ok && ps == 3)) {
            CloseHandle(g_unit_tick_log);
            g_unit_tick_log  = INVALID_HANDLE_VALUE;
            g_last_dump_tick = 0xFFFFFFFFu;
        }
    }
    return 0;
}

/* MessageBoxA NOP stub — inline hook target. IDOK(1) 즉시 반환. */
static int WINAPI _nop_msgbox(HWND hWnd, LPCSTR lpText,
                               LPCSTR lpCaption, UINT uType)
{
    (void)hWnd; (void)uType;
    log_msg("[inmm_stub] MessageBoxA suppressed: %s — %s\n",
            lpCaption ? lpCaption : "(null)",
            lpText    ? lpText    : "(null)");
    return 1; /* IDOK */
}

/* ------------------------------------------------------------------ */
/* DllMain                                                             */
/* ------------------------------------------------------------------ */
BOOL WINAPI DllMain(HINSTANCE hInst, DWORD reason, LPVOID reserved)
{
    (void)reserved;

    if (reason == DLL_PROCESS_ATTACH) {
        DisableThreadLibraryCalls(hInst);

        /* Inline hook: MessageBoxA 함수 시작 5바이트를 JMP _nop_msgbox로 패치.
         * IAT patch는 delay-load/indirect call을 놓칠 수 있으므로 함수 자체를 패치.
         * 게임 내부 에러 핸들러(FUN_00465250)가 MessageBoxA로 모달 대화상자를 띄우는데,
         * headless(Xvfb) 환경에서는 OK 버튼을 누를 사람이 없어 main loop가 블로킹. */
        {
            FARPROC pMsgBox = GetProcAddress(GetModuleHandleA("user32.dll"),
                                             "MessageBoxA");
            if (pMsgBox) {
                DWORD old;
                if (VirtualProtect((LPVOID)pMsgBox, 8, PAGE_EXECUTE_READWRITE, &old)) {
                    /* E9 xx xx xx xx = JMP rel32 */
                    BYTE *p = (BYTE *)pMsgBox;
                    DWORD target = (DWORD)(ULONG_PTR)_nop_msgbox;
                    DWORD rel = target - ((DWORD)(ULONG_PTR)p + 5);
                    p[0] = 0xE9;
                    *(DWORD *)(p + 1) = rel;
                    VirtualProtect((LPVOID)pMsgBox, 8, old, &old);
                }
            }
        }

        control_log_init(); /* session_start 기록 — dll_attach보다 먼저 */
        /* _inmm_orig.dll 로드 없음 — 직접 winmm/mci 사용 */
        control_log_event(NULL, "dll_attach", NULL, 0xFFFFFFFF, 0xFFFFFFFF, NULL, "inmm_stub loaded");

        /* G1 presentation trace is opt-in and fail-closed inside its own
         * structured log.  Stock startup remains untouched when disabled. */
        /* Final D3D9 provenance trace is opt-in and pixel-write free. */
        if (!final_d3d9_trace_install()) {
            control_log_event(NULL, "final_d3d9_trace", NULL, 0xFFFFFFFF, 0xFFFFFFFF,
                              NULL, "requested final D3D9 trace installation failed");
        }

        if (!g1_direct_draw_trace_install()) {
            control_log_event(NULL, "g1_present_trace", NULL, 0xFFFFFFFF, 0xFFFFFFFF,
                              NULL, "requested trace installation failed");
        }

        /* G4 AI shadow is opt-in (INMM_AI_SHADOW=1) and fail-closed. */
        if (!ai_shadow_install()) {
            control_log_event(NULL, "ai_shadow", NULL, 0xFFFFFFFF, 0xFFFFFFFF,
                              NULL, "shadow installation failed or call-site signature mismatch");
        }

        /* Asset hook: IAT patch CreateFileA/W on EXE imports.
         * Logs all file opens to C:\inmm_asset_log.jsonl with PS state. */
        {
            int patched = asset_hook_install();
            char buf[64];
            wsprintfA(buf, "asset_hook %d slot(s) patched", patched);
            control_log_event(NULL, "asset_hook", NULL, 0xFFFFFFFF, 0xFFFFFFFF, NULL, buf);
        }

        /* SFX hook: inline trampoline at FUN_00445930 (SFX dispatch).
         * Captures original SFX events (unit_type, event_type, selected YAV)
         * to C:\inmm_sfx_log.jsonl. #358 AC3. */
        {
            int sfx_ok = sfx_hook_install();
            control_log_event(NULL, "sfx_hook", NULL, 0xFFFFFFFF, 0xFFFFFFFF, NULL,
                              sfx_ok ? "FUN_00445930 trampoline installed"
                                     : "sfx_hook install FAILED (prologue mismatch?)");
        }

    } else if (reason == DLL_PROCESS_DETACH) {
        ai_shadow_detach();
        final_d3d9_trace_detach();
        g1_direct_draw_trace_detach();
        if (g_worker_thread) {
            InterlockedExchange(&g_worker_stop, 1);
            WaitForSingleObject(g_worker_thread, 2000);
            CloseHandle(g_worker_thread);
            g_worker_thread = NULL;
        }

        char buf[128];
        wsprintfA(buf,
                  "[inmm_stub] DLL_PROCESS_DETACH — total calls intercepted: %u\n",
                  (unsigned)g_call_count);
        file_write(g_log, buf);

        control_log_close();
        if (g_watch_log != INVALID_HANDLE_VALUE) { CloseHandle(g_watch_log); g_watch_log = INVALID_HANDLE_VALUE; }
        if (g_mci_log   != INVALID_HANDLE_VALUE) { CloseHandle(g_mci_log);   g_mci_log   = INVALID_HANDLE_VALUE; }
        if (g_state_log != INVALID_HANDLE_VALUE) { CloseHandle(g_state_log); g_state_log = INVALID_HANDLE_VALUE; }
        if (g_log       != INVALID_HANDLE_VALUE) { CloseHandle(g_log);       g_log       = INVALID_HANDLE_VALUE; }
    }

    return TRUE;
}


/* ------------------------------------------------------------------ */
/* Export: _imeBeginPeriod  (ordinal 101)                             */
/* ------------------------------------------------------------------ */
__declspec(dllexport)
MMRESULT WINAPI _imeBeginPeriod(UINT uPeriod)
{
    ensure_initialized();
    InterlockedIncrement(&g_call_count);
    log_msg("[inmm_stub] _imeBeginPeriod(%u) [#%u]\n",
            uPeriod, (unsigned)g_call_count);
    return timeBeginPeriod(uPeriod);
}

/* ------------------------------------------------------------------ */
/* Export: _imeEndPeriod    (ordinal 102)                             */
/* ------------------------------------------------------------------ */
__declspec(dllexport)
MMRESULT WINAPI _imeEndPeriod(UINT uPeriod)
{
    ensure_initialized();
    InterlockedIncrement(&g_call_count);
    log_msg("[inmm_stub] _imeEndPeriod(%u) [#%u]\n",
            uPeriod, (unsigned)g_call_count);
    return timeEndPeriod(uPeriod);
}

/* ------------------------------------------------------------------ */
/* Export: _ciSendCommandA  (ordinal 50)                              */
/* 원본 _inmm_orig.dll: ret $0x10 = 4 params × 4 bytes               */
/* mciSendCommandA 와 동일한 4-arg 시그니처 (mciSendStringA 아님!)   */
/* ------------------------------------------------------------------ */
__declspec(dllexport)
MCIERROR WINAPI _ciSendCommandA(MCIDEVICEID mciId, UINT uMsg,
                                 DWORD_PTR dwParam1, DWORD_PTR dwParam2)
{
    ensure_initialized();
    InterlockedIncrement(&g_call_count);

    DWORD ps = 0, tick = 0;
    read_u32_safe(PROGRAM_STATE_VA, &ps);
    read_u32_safe(GLOBAL_TICK_VA,   &tick);

    log_msg("[inmm_stub] _ciSendCommandA(dev=%u msg=0x%X p1=0x%X p2=0x%X) ps=%u tick=%u [#%u]\n",
            (unsigned)mciId, (unsigned)uMsg,
            (unsigned)dwParam1, (unsigned)dwParam2,
            (unsigned)ps, (unsigned)tick, (unsigned)g_call_count);

    /* MCI 파라미터 구조체 필드 추출 (BGM 트랙 근거 캡처용).
     * 원본 EXE의 MCI 사용처 (analysis: FUN_00406350/440/520):
     *   0x803 MCI_OPEN   p2=MCI_OPEN_PARMS   {cb, wDeviceID, lpstrDeviceType..}
     *   0x80d MCI_SET    p2=MCI_SET_PARMS    {cb, dwTimeFormat(=10 TMSF)}
     *   0x814 MCI_STATUS p2=MCI_STATUS_PARMS {cb, dwReturn, dwItem, dwTrack}
     *   0x806 MCI_PLAY   p2=MCI_PLAY_PARMS   {cb, dwFrom, dwTo}
     *     → TMSF 포맷이므로 dwFrom 하위 바이트 = **트랙 번호** (FUN_00406520
     *       local_8 = track & 0xff). 이것이 free-battle BGM 트랙의 1차 근거. */
    DWORD *parms = (DWORD *)dwParam2;
    DWORD f2 = 0, f3 = 0;  /* struct dword[1], dword[2] */
    if (parms != NULL) {
        f2 = parms[1];
        f3 = parms[2];
    }

    char mci_buf[128];
    if (uMsg == 0x806 /* MCI_PLAY */) {
        wsprintfA(mci_buf,
                  "mciSendCmd dev=%u msg=0x%X p1=0x%X from=0x%X to=0x%X track=%u",
                  (unsigned)mciId, (unsigned)uMsg, (unsigned)dwParam1,
                  (unsigned)f2, (unsigned)f3, (unsigned)(f2 & 0xff));
    } else if (uMsg == 0x814 /* MCI_STATUS */) {
        wsprintfA(mci_buf,
                  "mciSendCmd dev=%u msg=0x%X p1=0x%X item=%u",
                  (unsigned)mciId, (unsigned)uMsg, (unsigned)dwParam1,
                  (unsigned)f3);
    } else {
        wsprintfA(mci_buf,
                  "mciSendCmd dev=%u msg=0x%X p1=0x%X p2v=0x%X",
                  (unsigned)mciId, (unsigned)uMsg, (unsigned)dwParam1,
                  (unsigned)f2);
    }
    jsonl_write_mci(ps, tick, mci_buf);

    char no_mci[8];
    if (GetEnvironmentVariableA("INMM_STUB_NO_MCI", no_mci, sizeof(no_mci)) > 0) {
        log_msg("[inmm_stub] _ciSendCommandA no-op by INMM_STUB_NO_MCI\n");
        return 0;
    }

    /* fake-CD 에뮬레이션 (INMM_STUB_FAKE_CD=1 일 때만):
     * wine 환경엔 CD가 없어 MCI_OPEN(cdaudio)이 실패 → 원본이 MCI_PLAY까지
     * 도달하지 못해 "어느 트랙을 트는가" 근거가 영영 안 나온다 (기존 로그가
     * 전부 0x803 반복인 이유).  성공을 가장해 게임의 트랙 선택 로직을 끝까지
     * 실행시키고, 위 JSONL 로깅으로 MCI_PLAY 트랙 번호를 채집한다.
     * 트랙 수는 99로 보고 — 게임측 가드(FUN_00406520: track <= count)를
     * 항상 통과시켜 요청 트랙이 그대로 MCI_PLAY에 드러나게 한다. */
    char fake_cd[8];
    if (GetEnvironmentVariableA("INMM_STUB_FAKE_CD", fake_cd, sizeof(fake_cd)) > 0) {
        switch (uMsg) {
        case 0x803: /* MCI_OPEN */
            if (parms != NULL) parms[1] = 0xCD;  /* wDeviceID */
            log_msg("[inmm_stub] FAKE_CD open → dev=0xCD\n");
            return 0;
        case 0x814: /* MCI_STATUS: dwItem(f3) 7=ready, 3=track count */
            if (parms != NULL) {
                if (f3 == 7)      parms[1] = 1;    /* ready */
                else if (f3 == 3) parms[1] = 99;   /* number of tracks */
                else              parms[1] = 1;    /* 기타 질의 generic */
            }
            return 0;
        case 0x806: /* MCI_PLAY — 트랙 근거는 위에서 이미 JSONL 기록됨 */
            log_msg("[inmm_stub] FAKE_CD play track=%u\n", (unsigned)(f2 & 0xff));
            return 0;
        case 0x804: /* MCI_CLOSE */
        case 0x808: /* MCI_STOP */
        case 0x809: /* MCI_PAUSE */
        case 0x807: /* MCI_SEEK */
        case 0x80d: /* MCI_SET */
            return 0;
        default:
            return 0;
        }
    }

    return mciSendCommandA(mciId, uMsg, dwParam1, dwParam2);
}

/* ------------------------------------------------------------------ */
/* Export: _imeGetTime      (ordinal 105)                             */
/* lazy-start polling worker thread                                    */
/* ------------------------------------------------------------------ */
__declspec(dllexport)
DWORD WINAPI _imeGetTime(void)
{
    ensure_initialized();
    InterlockedIncrement(&g_call_count);

    if (InterlockedCompareExchange(&g_worker_started, 1, 0) == 0) {
        DWORD ps_init = 0, tick_init = 0;
        read_u32_safe(PROGRAM_STATE_VA, &ps_init);
        read_u32_safe(GLOBAL_TICK_VA,   &tick_init);
        jsonl_write_state("ime_get_time_init", ps_init, tick_init);

        g_worker_thread = CreateThread(NULL, 0, worker_proc, NULL, 0, NULL);
        log_msg("[inmm_stub] polling worker %s\n",
                g_worker_thread ? "started" : "FAILED");
    }

    /* B6: main-loop slot drain. worker가 enqueue한 handler call을
     *      main thread(여기)에서 실행한다. 대기 중인 slot이 없으면 즉시 반환. */
    chb_drain_slot_mainthread();

    return timeGetTime();
}
