/* control_executor.c — control plane 실행기 (Win32 전용, CRT 없음)
 *
 * R2~R6 확장:
 *  - result 확장 필드 (goal, start_state, end_state, bridge_used, fallback_chain,
 *    rollback_*, reason_axis, elapsed_ms) 채움
 *  - state 실패 시 input bridge, 그 다음 handler bridge fallback 시도
 *  - handler timeout 시 state_bridge revert + rollback_* 이벤트/결과 기록
 *  - executor_start / executor_finish / bridge_exhausted 이벤트
 */

#include <windows.h>
#include "control_executor.h"
#include "control_registry.h"
#include "control_state_bridge.h"
#include "control_logging.h"
#include "control_input_bridge.h"
#include "control_handler_bridge.h"

/* ------------------------------------------------------------------ */
/* 결과 초기화 / 보조자                                                 */
/* ------------------------------------------------------------------ */
static void res_init(control_result_t *res, const control_request_t *req)
{
    lstrcpyA(res->request_id, req->request_id);
    res->ok            = FALSE;
    res->reason[0]     = '\0';
    res->state_reached = 0xFFFFFFFFu;
    res->event_count   = 0;
    lstrcpynA(res->goal, req->goal, sizeof(res->goal));
    res->reason_axis[0]           = '\0';
    res->start_state              = 0xFFFFFFFFu;
    res->end_state                = 0xFFFFFFFFu;
    res->bridge_used[0]           = '\0';
    res->bridge_downgraded_from[0]= '\0';
    res->fallback_chain[0]        = '\0';
    res->fallback_count           = 0;
    res->elapsed_ms               = 0;
    res->rollback_attempted       = FALSE;
    res->rollback_ok              = FALSE;
}

static void fc_append(control_result_t *res, const char *tag)
{
    int len = lstrlenA(res->fallback_chain);
    int add = lstrlenA(tag);
    if (len + add + 2 >= (int)sizeof(res->fallback_chain)) return;
    if (len > 0) {
        res->fallback_chain[len++] = ',';
        res->fallback_chain[len]   = '\0';
    }
    lstrcatA(res->fallback_chain, tag);
    res->fallback_count++;
}

static void set_reason(control_result_t *res, const char *axis, const char *reason)
{
    lstrcpynA(res->reason_axis, axis,   sizeof(res->reason_axis));
    lstrcpynA(res->reason,      reason, sizeof(res->reason));
}

/* ------------------------------------------------------------------ */
/* C1 cheat path — "_cheat_start_custom_game" test goal                */
/*                                                                     */
/* 게임의 FUN_004b8d60 내부 디버그 경로 활용:                            */
/*   if (DAT_0107c960 == 10 && FUN_00404c20(DAT_0106a5f8)==1)           */
/*     sVar4 = 0x1f8 (임의게임 강제 시작 트리거)                         */
/* worker에서 DAT_0107c960에 10을 쓴 뒤 PS 전이 체인을 polling 관측.     */
/* ------------------------------------------------------------------ */
#define CHEAT_DBG_FLAG_VA  0x0107C960u   /* DAT_0107c960 */
#define CHEAT_COND_VA      0x00C0CB60u   /* DAT_00c0cb60 — DAT_0106a5f8 source */
#define CHEAT_BOOL_VA      0x0106A5F8u   /* DAT_0106a5f8 — forced to 1 */

static BOOL is_cheat_start_goal(const char *goal)
{
    return (lstrcmpA(goal, "_cheat_start_custom_game") == 0);
}

static void run_cheat_start(const control_request_t *req,
                            control_result_t *res)
{
    DWORD state_before = 0xFFFFFFFFu, cur = 0xFFFFFFFFu;
    DWORD t0 = GetTickCount();

    csb_read_state(&state_before);
    res->start_state = state_before;
    lstrcpyA(res->bridge_used, "cheat");

    if (state_before != 7) {
        control_log_event(req->request_id, "cheat_abort", req->goal,
                          state_before, 0xFFFFFFFF, "cheat",
                          "not_in_custom_game_ps7");
        res->ok = FALSE;
        res->state_reached = state_before;
        res->end_state     = state_before;
        set_reason(res, CP_REASON_AXIS_LOGIC, "not_in_custom_game");
        res->elapsed_ms = GetTickCount() - t0;
        return;
    }

    /* 치트 조건: DAT_0107c960=10 AND FUN_00404c20(DAT_0106a5f8)==1.
     * 후자는 DAT_0106a5f8이 1 또는 유효 포인터일 때 발생. DAT_0106a5f8은
     * 매 프레임 DAT_00c0cb60 != 0 여부로 재설정되므로 DAT_00c0cb60=1도 같이 쓴다. */
    {
        volatile DWORD *dbg  = (DWORD *)(uintptr_t)CHEAT_DBG_FLAG_VA;
        volatile DWORD *cond = (DWORD *)(uintptr_t)CHEAT_COND_VA;
        volatile DWORD *b    = (DWORD *)(uintptr_t)CHEAT_BOOL_VA;
        if (IsBadWritePtr((LPVOID)dbg, sizeof(DWORD)) ||
            IsBadWritePtr((LPVOID)cond, sizeof(DWORD)) ||
            IsBadWritePtr((LPVOID)b,    sizeof(DWORD))) {
            control_log_event(req->request_id, "cheat_abort", req->goal,
                              state_before, 0xFFFFFFFF, "cheat",
                              "flag addrs unwritable");
            res->ok = FALSE;
            res->state_reached = state_before;
            res->end_state     = state_before;
            set_reason(res, CP_REASON_AXIS_ENV, "flag_unwritable");
            res->elapsed_ms = GetTickCount() - t0;
            return;
        }
        *dbg  = 10;
        *cond = 1;
        *b    = 1;
    }

    control_log_event(req->request_id, "cheat_flag_set", req->goal,
                      state_before, state_before, "cheat",
                      "DAT_0107c960=10 DAT_00c0cb60=1 DAT_0106a5f8=1");

    /* PS chain polling up to effective timeout (default 6s) */
    DWORD timeout_ms = (req->timeout_ms > 0) ? req->timeout_ms : 6000;
    DWORD deadline   = GetTickCount() + timeout_ms;
    DWORD path[32];
    int   plen = 1;
    path[0] = state_before;

    while (GetTickCount() < deadline) {
        if (csb_read_state(&cur)) {
            if (cur != path[plen - 1] && plen < 32) {
                path[plen++] = cur;
                char evdetail[64];
                wsprintfA(evdetail, "cheat transition PS=%u", (unsigned)cur);
                control_log_event(req->request_id, "state_change_observed",
                                  req->goal, path[plen - 2], cur,
                                  "cheat", evdetail);
                if (cur == 3) break;
            }
        }
        Sleep(30);
    }

    /* path 직렬화: "7,140,150,..." */
    char detail[192];
    detail[0] = '\0';
    for (int i = 0; i < plen; ++i) {
        char tmp[16];
        wsprintfA(tmp, i ? ",%u" : "%u", (unsigned)path[i]);
        if (lstrlenA(detail) + lstrlenA(tmp) + 1 < (int)sizeof(detail))
            lstrcatA(detail, tmp);
    }
    control_log_event(req->request_id, "cheat_probe_done", req->goal,
                      state_before, cur, "cheat", detail);

    res->state_reached = cur;
    res->end_state     = cur;
    res->ok            = (cur == 3);
    if (cur == 3)
        set_reason(res, "", "cheat_reached_ingame");
    else if (cur != state_before)
        set_reason(res, CP_REASON_AXIS_LOGIC, "cheat_partial_chain");
    else
        set_reason(res, CP_REASON_AXIS_LOGIC, "cheat_no_effect");
    lstrcpynA(res->fallback_chain, detail, sizeof(res->fallback_chain));
    res->fallback_count = (DWORD)plen;
    res->elapsed_ms     = GetTickCount() - t0;
}

/* ------------------------------------------------------------------ */
/* C2 input probe — "_custom_game_probe" test goal                     */
/*                                                                     */
/* PS=7(임의게임)에서 시작 트리거를 찾기 위해 VK 시퀀스를 순차 주입한다.  */
/* 각 시도 후 PS를 관측해 전이 유발한 입력을 기록한다.                    */
/* ------------------------------------------------------------------ */
static BOOL is_custom_probe_goal(const char *goal)
{
    return (lstrcmpA(goal, "_custom_game_probe") == 0);
}

typedef struct {
    const char *label;
    UINT        vk;
    DWORD       scan;
    int         repeat;
} probe_step_t;

static void probe_post(HWND h, UINT vk, DWORD scan)
{
    DWORD down = (scan << 16) | 0x00000001u;
    DWORD up   = (scan << 16) | 0xC0000001u;
    PostMessageA(h, WM_KEYDOWN, vk, down);
    PostMessageA(h, WM_KEYUP,   vk, up);
}

static void run_custom_probe(const control_request_t *req,
                             control_result_t *res)
{
    DWORD state_before = 0xFFFFFFFFu, cur = 0;
    DWORD t0 = GetTickCount();
    HWND  hwnd = cib_get_hwnd();

    csb_read_state(&state_before);
    res->start_state = state_before;
    lstrcpyA(res->bridge_used, "input_probe");

    if (state_before != 7 || !hwnd) {
        control_log_event(req->request_id, "probe_abort", req->goal,
                          state_before, 0xFFFFFFFF, "input_probe",
                          hwnd ? "not_in_ps7" : "no_hwnd");
        set_reason(res, CP_REASON_AXIS_LOGIC,
                   hwnd ? "not_in_custom_game" : "no_hwnd");
        res->end_state = res->state_reached = state_before;
        res->elapsed_ms = GetTickCount() - t0;
        return;
    }

    /* probe 시퀀스 — 각 step 후 500ms 대기하면서 PS 관측 */
    probe_step_t steps[] = {
        { "Enter",        VK_RETURN, 0x001C, 1 },
        { "Space",        VK_SPACE,  0x0039, 1 },
        { "Tab+Enter",    VK_TAB,    0x000F, 1 }, /* Tab first */
        { "Enter2",       VK_RETURN, 0x001C, 1 },
        { "Tab+Tab+Enter",VK_TAB,    0x000F, 2 },
        { "Enter3",       VK_RETURN, 0x001C, 1 },
        { "Tab*3+Enter",  VK_TAB,    0x000F, 3 },
        { "Enter4",       VK_RETURN, 0x001C, 1 },
        { "F10",          VK_F10,    0x0044, 1 },
        { "Alt+S",        0x53,      0x001F, 1 }, /* S key */
    };
    int nsteps = (int)(sizeof(steps)/sizeof(steps[0]));

    char detail[256];
    detail[0] = '\0';

    for (int i = 0; i < nsteps; ++i) {
        /* 키 주입 */
        for (int r = 0; r < steps[i].repeat; ++r) {
            probe_post(hwnd, steps[i].vk, steps[i].scan);
            Sleep(50);
        }
        /* step 기록 */
        char tmp[48];
        wsprintfA(tmp, " %s", steps[i].label);
        if (lstrlenA(detail) + lstrlenA(tmp) + 1 < (int)sizeof(detail))
            lstrcatA(detail, tmp);

        /* 관찰 window (500ms) */
        DWORD wait_end = GetTickCount() + 500;
        DWORD prev = state_before;
        while (GetTickCount() < wait_end) {
            csb_read_state(&cur);
            if (cur != prev) {
                char evdetail[64];
                wsprintfA(evdetail, "after=%s PS=%u",
                          steps[i].label, (unsigned)cur);
                control_log_event(req->request_id,
                                  "probe_transition", req->goal,
                                  prev, cur, "input_probe", evdetail);
                prev = cur;
                if (cur == 3 || cur != state_before) goto FOUND;
            }
            Sleep(30);
        }
    }

FOUND:
    lstrcpynA(res->fallback_chain, detail, sizeof(res->fallback_chain));
    res->fallback_count = (DWORD)nsteps;
    res->state_reached = cur;
    res->end_state     = cur;
    res->ok            = (cur != state_before && cur != 0xFFFFFFFFu);
    res->elapsed_ms    = GetTickCount() - t0;
    if (cur == 3)
        set_reason(res, "", "probe_reached_ingame");
    else if (cur != state_before)
        set_reason(res, "", "probe_state_changed");
    else
        set_reason(res, CP_REASON_AXIS_LOGIC, "probe_no_effect");

    control_log_event(req->request_id, "probe_done", req->goal,
                      state_before, cur, "input_probe", detail);
}

/* ------------------------------------------------------------------ */
/* C2 mouse probe — "_custom_game_mouse_probe"                         */
/*                                                                     */
/* 800x600 게임 창의 버튼 위치 후보에 마우스 클릭 주입 + PS 관찰.         */
/* ------------------------------------------------------------------ */
static BOOL is_mouse_probe_goal(const char *goal)
{
    return (lstrcmpA(goal, "_custom_game_mouse_probe") == 0);
}

/* SendInput 기반 hardware-level 마우스 클릭 — DirectInput 게임 대응.
 * (x,y)는 게임 창의 client 좌표. screen 좌표로 변환 후 SetCursorPos + SendInput. */
static void mouse_click(HWND h, int x, int y)
{
    POINT p = { x, y };
    ClientToScreen(h, &p);

    /* 화면 크기 정규화 (SendInput 의 MOUSEEVENTF_ABSOLUTE 요구) */
    int sw = GetSystemMetrics(SM_CXSCREEN);
    int sh = GetSystemMetrics(SM_CYSCREEN);
    if (sw <= 0) sw = 1;
    if (sh <= 0) sh = 1;

    INPUT inp[3] = {0};
    inp[0].type = INPUT_MOUSE;
    inp[0].mi.dx = (p.x * 65535) / sw;
    inp[0].mi.dy = (p.y * 65535) / sh;
    inp[0].mi.dwFlags = MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_MOVE;

    inp[1].type = INPUT_MOUSE;
    inp[1].mi.dwFlags = MOUSEEVENTF_LEFTDOWN;

    inp[2].type = INPUT_MOUSE;
    inp[2].mi.dwFlags = MOUSEEVENTF_LEFTUP;

    SendInput(1, &inp[0], sizeof(INPUT));
    Sleep(10);
    SendInput(1, &inp[1], sizeof(INPUT));
    Sleep(20);
    SendInput(1, &inp[2], sizeof(INPUT));

    /* fallback: PostMessageA도 같이 쏴둔다 — 어느 쪽이든 먹히는 경로 커버 */
    PostMessageA(h, WM_LBUTTONDOWN, MK_LBUTTON, MAKELPARAM(x, y));
    Sleep(10);
    PostMessageA(h, WM_LBUTTONUP, 0, MAKELPARAM(x, y));
}

static void run_mouse_probe(const control_request_t *req,
                            control_result_t *res)
{
    DWORD state_before = 0xFFFFFFFFu, cur = 0;
    DWORD t0 = GetTickCount();
    HWND  hwnd = cib_get_hwnd();

    csb_read_state(&state_before);
    res->start_state = state_before;
    lstrcpyA(res->bridge_used, "mouse_probe");

    if (state_before != 7 || !hwnd) {
        control_log_event(req->request_id, "mprobe_abort", req->goal,
                          state_before, 0xFFFFFFFF, "mouse_probe",
                          hwnd ? "not_in_ps7" : "no_hwnd");
        set_reason(res, CP_REASON_AXIS_LOGIC,
                   hwnd ? "not_in_custom_game" : "no_hwnd");
        res->end_state = res->state_reached = state_before;
        res->elapsed_ms = GetTickCount() - t0;
        return;
    }

    /* 800x600 기준 버튼 후보 그리드.
     * 구 RTS UI에서 "시작" 은 보통 우측 하단 또는 하단 중앙 */
    int points[][2] = {
        /* 우측 하단 (가장 유력) */
        {720, 560}, {680, 560}, {720, 540}, {680, 540},
        /* 좌측 하단 (취소류) */
        { 80, 560}, { 40, 560},
        /* 하단 중앙 */
        {400, 560}, {400, 540}, {400, 520},
        /* 좌측 버튼 그룹 (2nd 컬럼, 보통 "시나리오 선택", "진영", 등) */
        {120, 400}, {120, 450}, {120, 500},
        /* 우측 중간 ("시작" 버튼이 옆에 있을 수도) */
        {720, 460}, {720, 500}, {720, 420},
        /* 센터 라인 */
        {400, 460}, {400, 400},
    };
    int npoints = (int)(sizeof(points)/sizeof(points[0]));

    char detail[256];
    detail[0] = '\0';
    int transitions = 0;

    for (int i = 0; i < npoints; ++i) {
        int x = points[i][0], y = points[i][1];
        mouse_click(hwnd, x, y);

        /* 관찰 window 400ms */
        DWORD wait_end = GetTickCount() + 400;
        DWORD prev = state_before;
        while (GetTickCount() < wait_end) {
            csb_read_state(&cur);
            if (cur != prev) {
                char evdetail[80];
                wsprintfA(evdetail, "x=%d y=%d prev=%u new=%u",
                          x, y, (unsigned)prev, (unsigned)cur);
                control_log_event(req->request_id,
                                  "mprobe_transition", req->goal,
                                  prev, cur, "mouse_probe", evdetail);
                prev = cur;
                transitions++;
                if (cur != state_before) {
                    char tmp[48];
                    wsprintfA(tmp, " HIT@(%d,%d)->PS%u",
                              x, y, (unsigned)cur);
                    if (lstrlenA(detail) + lstrlenA(tmp) + 1 <
                        (int)sizeof(detail))
                        lstrcatA(detail, tmp);
                    if (cur == 3) goto FOUND;
                    goto FOUND; /* 첫 번째 hit에서 중단 — 좌표 확정 */
                }
            }
            Sleep(30);
        }
    }

FOUND:
    lstrcpynA(res->fallback_chain, detail[0] ? detail : "no_hit",
              sizeof(res->fallback_chain));
    res->fallback_count = (DWORD)transitions;
    res->state_reached = cur;
    res->end_state     = cur;
    res->ok            = (cur != state_before && cur != 0xFFFFFFFFu);
    res->elapsed_ms    = GetTickCount() - t0;
    if (cur == 3)
        set_reason(res, "", "mprobe_reached_ingame");
    else if (cur != state_before)
        set_reason(res, "", "mprobe_state_changed");
    else
        set_reason(res, CP_REASON_AXIS_LOGIC, "mprobe_no_effect");

    control_log_event(req->request_id, "mprobe_done", req->goal,
                      state_before, cur, "mouse_probe",
                      detail[0] ? detail : "no_transition");
}

/* ------------------------------------------------------------------ */
/* C3 state-chain inject — "_custom_game_chain_inject"                 */
/*                                                                     */
/* Custom Game UI의 시작 버튼을 거치지 않고 원본 state chain을          */
/* 직접 주입: DAT_00b92cc0=2 + PS=140                                  */
/*                                                                     */
/* 원본 분석 (analysis/ghidra_output/):                                  */
/*   custom_game_tick(7)이 FUN_004b8d60 반환값 sVar1을 받아             */
/*     DAT_004ed818 = 0x8c (140)                                       */
/*     DAT_00b92cc0 = sVar1                                            */
/*   state 140 (FUN_00425160) → PS=150 (0x96)                          */
/*   state 150 (FUN_00425170) → FUN_004933e0()==1 시 PS=DAT_00b92cc0   */
/*   state 2   (FUN_00424d50) → 무조건 PS=3 (ingame)                   */
/*                                                                     */
/* 우리가 DAT_00b92cc0=2 + PS=140 쓰면 게임이 자동으로                  */
/* 140→150→2→3 체인을 탄다.                                             */
/* ------------------------------------------------------------------ */
#define CG_CHAIN_VALUE_VA  0x00B92CC0u  /* DAT_00b92cc0 — custom_game sVar1 저장소 */
#define SCENARIO_INDEX_VA  0x009E1DD8u  /* DAT_009e1dd8 — 시나리오 인덱스 (WORD) */
#define SCENARIO_FLAG_VA   0x009E1DDAu  /* DAT_009e1dda — 시나리오 선택 완료 플래그 (WORD) */
#define G2_EIGHT_GOAL      "_custom_game_chain_inject_g2_eight_seed42"
#define G2_EIGHT_AI_GOAL   "_custom_game_chain_inject_g2_eight_ai_seed42"
/* W22 (lap456 work) fixture-lever arms: exact-match opt-ins, additive only.
 * Each shares every G2_EIGHT_AI_GOAL precondition/gate and differs from it
 * by exactly one lobby field (see run_chain_inject overrides below). None
 * of these change legacy goal behavior -- is_g2_eight_goal only grows the
 * accepted literal set, chain_inject_seed_from_goal only grows accepted
 * seed suffixes. */
#define G2_EIGHT_AI_D4A1_GOAL "_custom_game_chain_inject_g2_eight_ai_d4a1_seed42"
#define G2_EIGHT_AI_AI4_GOAL  "_custom_game_chain_inject_g2_eight_ai4_seed42"
#define G2_EIGHT_AI_D44_0_GOAL "_custom_game_chain_inject_g2_eight_ai_d44_0_seed42"
#define G2_EIGHT_AI_D46_1_GOAL "_custom_game_chain_inject_g2_eight_ai_d46_1_seed42"
#define G2_EIGHT_AI_SEED99_GOAL "_custom_game_chain_inject_g2_eight_ai_seed99"
#define G2_LOBBY_VA        0x00632CC0u
#define G2_LOBBY_RECORDS   8
#define G2_LOBBY_STRIDE    6
#define G2_RAW_GATE_B_VA   0x00B93988u

static BOOL is_g2_eight_goal(const char *goal)
{
    /* Deliberately exact: this diagnostic must not alter legacy chain goals.
     * G2_EIGHT_AI_GOAL is a separate opt-in that only changes record[2] for
     * owner 0 (see run_chain_inject); it shares every other precondition and
     * gate with G2_EIGHT_GOAL so it must match here too. The W22 arm goals
     * below are the same kind of opt-in, one lobby field each. */
    return lstrcmpA(goal, G2_EIGHT_GOAL) == 0 ||
           lstrcmpA(goal, G2_EIGHT_AI_GOAL) == 0 ||
           lstrcmpA(goal, G2_EIGHT_AI_D4A1_GOAL) == 0 ||
           lstrcmpA(goal, G2_EIGHT_AI_AI4_GOAL) == 0 ||
           lstrcmpA(goal, G2_EIGHT_AI_D44_0_GOAL) == 0 ||
           lstrcmpA(goal, G2_EIGHT_AI_D46_1_GOAL) == 0 ||
           lstrcmpA(goal, G2_EIGHT_AI_SEED99_GOAL) == 0;
}

static BOOL g2_setup_preflight(void)
{
    volatile BYTE *lobby = (BYTE *)(uintptr_t)G2_LOBBY_VA;
    volatile USHORT *game_mode = (USHORT *)(uintptr_t)0x00632D42u;
    volatile USHORT *game_type = (USHORT *)(uintptr_t)0x00632D44u;
    volatile USHORT *terrain = (USHORT *)(uintptr_t)0x00632D46u;
    volatile USHORT *map_selector = (USHORT *)(uintptr_t)0x00632D48u;
    volatile USHORT *map_size = (USHORT *)(uintptr_t)0x00632D4Au;
    volatile USHORT *tile = (USHORT *)(uintptr_t)0x00632D4Cu;
    volatile USHORT *session = (USHORT *)(uintptr_t)0x00632D54u;
    volatile USHORT *seed = (USHORT *)(uintptr_t)0x00632D92u;
    volatile SHORT *chain = (SHORT *)(uintptr_t)CG_CHAIN_VALUE_VA;
    volatile USHORT *program_state = (USHORT *)(uintptr_t)PROGRAM_STATE_VA;
    volatile USHORT *raw_gate_b = (USHORT *)(uintptr_t)G2_RAW_GATE_B_VA;
    return !IsBadWritePtr((LPVOID)lobby, G2_LOBBY_RECORDS * G2_LOBBY_STRIDE) &&
           !IsBadWritePtr((LPVOID)game_mode, sizeof(USHORT)) &&
           !IsBadWritePtr((LPVOID)game_type, sizeof(USHORT)) &&
           !IsBadWritePtr((LPVOID)terrain, sizeof(USHORT)) &&
           !IsBadWritePtr((LPVOID)map_selector, sizeof(USHORT)) &&
           !IsBadWritePtr((LPVOID)map_size, sizeof(USHORT)) &&
           !IsBadWritePtr((LPVOID)tile, sizeof(USHORT)) &&
           !IsBadWritePtr((LPVOID)session, sizeof(USHORT)) &&
           !IsBadWritePtr((LPVOID)seed, sizeof(USHORT)) &&
           !IsBadWritePtr((LPVOID)chain, sizeof(SHORT)) &&
           !IsBadWritePtr((LPVOID)program_state, sizeof(USHORT)) &&
           !IsBadReadPtr((LPCVOID)raw_gate_b, sizeof(USHORT));
}

static BOOL plus_map_name_from_goal(const char *goal, char *out, int out_len, BOOL *custom_map)
{
    static const char prefix[] = "_custom_game_chain_inject_plus";
    static const char suffix_name[] = "_name";
    static const char suffix_custom[] = "_custom_name";
    static const char suffix_custom_parent[] = "_custom_parent_name";
    int prefix_len = lstrlenA(prefix);
    int goal_len = lstrlenA(goal);
    int suffix_len = 0;
    int digit_len;
    int i;
    if (out_len > 0) out[0] = '\0';
    if (custom_map) *custom_map = FALSE;
    if (goal_len <= prefix_len) return FALSE;
    for (i = 0; i < prefix_len; ++i) {
        if (goal[i] != prefix[i]) return FALSE;
    }
    if (goal_len > lstrlenA(suffix_custom_parent) &&
        lstrcmpA(goal + goal_len - lstrlenA(suffix_custom_parent), suffix_custom_parent) == 0) {
        suffix_len = lstrlenA(suffix_custom_parent);
        if (custom_map) *custom_map = TRUE;
    } else if (goal_len > lstrlenA(suffix_custom) &&
        lstrcmpA(goal + goal_len - lstrlenA(suffix_custom), suffix_custom) == 0) {
        suffix_len = lstrlenA(suffix_custom);
        if (custom_map) *custom_map = TRUE;
    } else if (goal_len > lstrlenA(suffix_name) &&
               lstrcmpA(goal + goal_len - lstrlenA(suffix_name), suffix_name) == 0) {
        suffix_len = lstrlenA(suffix_name);
    } else {
        return FALSE;
    }
    digit_len = goal_len - prefix_len - suffix_len;
    if (digit_len < 2 || digit_len > 2) return FALSE;
    for (i = 0; i < digit_len; ++i) {
        char c = goal[prefix_len + i];
        if (c < '0' || c > '9') return FALSE;
    }
    if (suffix_len == lstrlenA(suffix_custom_parent)) {
        if (out_len < 24) return FALSE;
        wsprintfA(out, "..\\stagemap\\plus%c%c.map", goal[prefix_len], goal[prefix_len + 1]);
    } else {
        if (out_len < 11) return FALSE;
        wsprintfA(out, "plus%c%c.map", goal[prefix_len], goal[prefix_len + 1]);
    }
    return TRUE;
}

static BOOL chain_inject_seed_from_goal(const char *goal, USHORT *seed_out)
{
    static const char seed1[] = "_seed1";
    static const char seed7[] = "_seed7";
    static const char seed42[] = "_seed42";
    static const char seed99[] = "_seed99"; /* W22 arm A4 */
    const int goal_len = lstrlenA(goal);
    const int seed1_len = lstrlenA(seed1);
    const int seed7_len = lstrlenA(seed7);
    const int seed42_len = lstrlenA(seed42);
    const int seed99_len = lstrlenA(seed99);
    if (seed_out) *seed_out = 0;
    if (goal_len > seed1_len &&
        lstrcmpA(goal + goal_len - seed1_len, seed1) == 0) {
        if (seed_out) *seed_out = 1;
        return TRUE;
    }
    if (goal_len > seed7_len &&
        lstrcmpA(goal + goal_len - seed7_len, seed7) == 0) {
        if (seed_out) *seed_out = 7;
        return TRUE;
    }
    if (goal_len > seed99_len &&
        lstrcmpA(goal + goal_len - seed99_len, seed99) == 0) {
        if (seed_out) *seed_out = 99;
        return TRUE;
    }
    if (goal_len > seed42_len &&
        lstrcmpA(goal + goal_len - seed42_len, seed42) == 0) {
        if (seed_out) *seed_out = 42;
        return TRUE;
    }
    return FALSE;
}

static BOOL chain_inject_goal_matches(const char *goal, const char *base)
{
    char with_seed1[96];
    char with_seed7[96];
    char with_seed42[96];
    if (lstrcmpA(goal, base) == 0) return TRUE;
    wsprintfA(with_seed1, "%s_seed1", base);
    if (lstrcmpA(goal, with_seed1) == 0) return TRUE;
    wsprintfA(with_seed7, "%s_seed7", base);
    if (lstrcmpA(goal, with_seed7) == 0) return TRUE;
    wsprintfA(with_seed42, "%s_seed42", base);
    return lstrcmpA(goal, with_seed42) == 0;
}

static BOOL is_set_seed_goal(const char *goal)
{
    return lstrcmpA(goal, "_set_seed1") == 0 ||
           lstrcmpA(goal, "_set_seed7") == 0 ||
           lstrcmpA(goal, "_set_seed42") == 0;
}

static BOOL is_scenario1_select_goal(const char *goal)
{
    return lstrcmpA(goal, "_scenario1_select_first") == 0;
}

static void run_scenario1_select(const control_request_t *req,
                                 control_result_t *res)
{
    volatile USHORT *pIdx  = (USHORT *)(uintptr_t)SCENARIO_INDEX_VA;
    volatile USHORT *pFlag = (USHORT *)(uintptr_t)SCENARIO_FLAG_VA;
    DWORD state_before = 0xFFFFFFFFu;
    csb_read_state(&state_before);
    res->start_state = res->end_state = res->state_reached = state_before;
    lstrcpyA(res->bridge_used, "scenario1_select");

    if (state_before != 15) {
        char reason[48];
        wsprintfA(reason, "not_in_scenario_select_ps=%u", (unsigned)state_before);
        set_reason(res, CP_REASON_AXIS_LOGIC, reason);
        control_log_event(req->request_id, "scenario1_select_abort",
                          req->goal, state_before, state_before,
                          "scenario1_select", reason);
        return;
    }
    if (IsBadWritePtr((LPVOID)pIdx, sizeof(USHORT)) ||
        IsBadWritePtr((LPVOID)pFlag, sizeof(USHORT))) {
        set_reason(res, CP_REASON_AXIS_ENV, "scenario_select_unwritable");
        return;
    }
    *pIdx = 1;   /* capture_scenario1_phase1.py verified 1-based id. */
    *pFlag = 1;  /* selection complete before enter_briefing. */
    res->ok = TRUE;
    set_reason(res, "", "ok");
    control_log_event(req->request_id, "scenario1_select_first",
                      req->goal, state_before, state_before,
                      "scenario1_select", "DAT_009E1DD8=1 DAT_009E1DDA=1");
}

static void run_set_seed(const control_request_t *req, control_result_t *res)
{
    volatile USHORT *pSeedSupplier = (USHORT *)(uintptr_t)0x00632D92u;
    USHORT seed_value = 0;
    DWORD state_before = 0xFFFFFFFFu;
    csb_read_state(&state_before);
    res->start_state = res->end_state = res->state_reached = state_before;
    lstrcpyA(res->bridge_used, "set_seed");
    if (!chain_inject_seed_from_goal(req->goal, &seed_value)) {
        set_reason(res, CP_REASON_AXIS_LOGIC, "unknown_seed_goal");
        return;
    }
    if (IsBadWritePtr((LPVOID)pSeedSupplier, sizeof(USHORT))) {
        set_reason(res, CP_REASON_AXIS_ENV, "seed_unwritable");
        return;
    }
    *pSeedSupplier = seed_value;
    res->ok = TRUE;
    {
        char detail[32];
        wsprintfA(detail, "DAT_00632D92=%u", (unsigned)seed_value);
        control_log_event(req->request_id, "set_seed", req->goal,
                          state_before, state_before, "set_seed",
                          detail);
    }
    set_reason(res, "", "ok");
}

static BOOL is_chain_inject_goal(const char *goal)
{
    char map_name[64];
    return (is_g2_eight_goal(goal) ||
            chain_inject_goal_matches(goal, "_custom_game_chain_inject") ||
            lstrcmpA(goal, "_scenario1_chain_ingame") == 0 ||
            lstrcmpA(goal, "_scenario1_direct_ingame") == 0 ||
            chain_inject_goal_matches(goal, "_custom_game_chain_inject_joseon_ming") ||
            chain_inject_goal_matches(goal, "_custom_game_chain_inject_ming_joseon") ||
            chain_inject_goal_matches(goal, "_custom_game_chain_inject_ming_japan") ||
            chain_inject_goal_matches(goal, "_custom_game_chain_inject_map2") ||
            plus_map_name_from_goal(goal, map_name, sizeof(map_name), NULL) ||
            chain_inject_goal_matches(goal, "_custom_game_chain_inject_d44_0") ||
            chain_inject_goal_matches(goal, "_custom_game_chain_inject_d44_0_d46_1") ||
            chain_inject_goal_matches(goal, "_custom_game_chain_inject_d44_0_d46_2") ||
            chain_inject_goal_matches(goal, "_custom_game_chain_inject_d44_1") ||
            chain_inject_goal_matches(goal, "_custom_game_chain_inject_d44_1_d46_1") ||
            chain_inject_goal_matches(goal, "_custom_game_chain_inject_d44_1_d46_2") ||
            chain_inject_goal_matches(goal, "_custom_game_chain_inject_d46_1") ||
            chain_inject_goal_matches(goal, "_custom_game_chain_inject_d46_2"));
}

static void chain_inject_nations_for_goal(const char *goal, BYTE *p0, BYTE *p1)
{
    /* Binary nation ids: 1=Joseon, 2=Japan, 3=Ming.
     * Default preserves the historical control capture setup (Joseon vs Japan).
     * The explicit Ming variants are for TODO-PARITY-ALL-0102 fixed-nation matrix
     * capture; they still only pre-seed the original lobby blob before PS=140.
     */
    *p0 = 1;
    *p1 = 2;
    if (chain_inject_goal_matches(goal, "_custom_game_chain_inject_joseon_ming")) {
        *p0 = 1;
        *p1 = 3;
    } else if (chain_inject_goal_matches(goal, "_custom_game_chain_inject_ming_joseon")) {
        *p0 = 3;
        *p1 = 1;
    } else if (chain_inject_goal_matches(goal, "_custom_game_chain_inject_ming_japan")) {
        *p0 = 3;
        *p1 = 2;
    }
}

static void run_chain_inject(const control_request_t *req,
                             control_result_t *res)
{
    DWORD state_before = 0xFFFFFFFFu, cur = 0;
    DWORD t0 = GetTickCount();

    csb_read_state(&state_before);
    res->start_state = state_before;
    lstrcpyA(res->bridge_used, "chain_inject");

    if (lstrcmpA(req->goal, "_scenario1_direct_ingame") == 0 && state_before != 9) {
        DWORD wait_timeout = (req->timeout_ms > 0) ? req->timeout_ms : 15000;
        DWORD wait_deadline = GetTickCount() + wait_timeout;
        DWORD observed = state_before;
        while (GetTickCount() < wait_deadline) {
            if (csb_read_state(&observed) && observed == 9) {
                state_before = observed;
                res->start_state = state_before;
                control_log_event(req->request_id, "direct_ingame_wait_ps9",
                                  req->goal, 0xFFFFFFFF, 9,
                                  "chain_inject", "observed PS=9");
                break;
            }
            Sleep(10);
        }
        if (state_before != 9) {
            char reason[64];
            wsprintfA(reason, "direct_ingame_no_ps9_last=%u", (unsigned)observed);
            control_log_event(req->request_id, "chain_abort", req->goal,
                              observed, 0xFFFFFFFF, "chain_inject", reason);
            set_reason(res, CP_REASON_AXIS_LOGIC, reason);
            res->end_state = res->state_reached = observed;
            res->elapsed_ms = GetTickCount() - t0;
            return;
        }
    }

    /* PS=7 (임의게임) 또는 PS=20 (시나리오 브리핑) 허용 */
    if (state_before != 7 && state_before != 20 && state_before != 15 &&
        !(lstrcmpA(req->goal, "_scenario1_direct_ingame") == 0 && state_before == 9)) {
        char reason[48];
        wsprintfA(reason, "unexpected_ps_%u", (unsigned)state_before);
        control_log_event(req->request_id, "chain_abort", req->goal,
                          state_before, 0xFFFFFFFF, "chain_inject",
                          reason);
        set_reason(res, CP_REASON_AXIS_LOGIC, reason);
        res->end_state = res->state_reached = state_before;
        res->elapsed_ms = GetTickCount() - t0;
        return;
    }

    /* G2's eight-owner creation is an ordinary custom-game PS=7 probe only.
     * Do not reinterpret a briefing/scenario transition as this fixture. */
    if (is_g2_eight_goal(req->goal) && state_before != 7) {
        char reason[64];
        wsprintfA(reason, "g2_eight_requires_ps7_got_%u", (unsigned)state_before);
        control_log_event(req->request_id, "chain_abort", req->goal,
                          state_before, 0xFFFFFFFF, "chain_inject", reason);
        set_reason(res, CP_REASON_AXIS_LOGIC, reason);
        res->end_state = res->state_reached = state_before;
        res->elapsed_ms = GetTickCount() - t0;
        return;
    }

    /* chain 값: PS=7 → 2(임의게임 인게임 전처리), PS=20 → 1(시나리오 인게임 전처리),
     *           PS=15 → 16(브리핑 전처리) */
    int target;
    if (lstrcmpA(req->goal, "_scenario1_chain_ingame") == 0 ||
        lstrcmpA(req->goal, "_scenario1_direct_ingame") == 0) target = 1;
    else if (state_before == 7) target = 2;
    else if (state_before == 15) target = 16; /* briefing preprocess */
    else target = 1; /* PS=20 → scenario ingame preprocess */

    if (req->params.scenario_index != CP_PARAM_UNSET &&
        req->params.scenario_index > 0)
        target = req->params.scenario_index;

    if (is_g2_eight_goal(req->goal) && target != 2) {
        control_log_event(req->request_id, "chain_abort", req->goal,
                          state_before, 0xFFFFFFFF, "chain_inject",
                          "g2_eight_rejects_scenario_index_override");
        set_reason(res, CP_REASON_AXIS_LOGIC,
                   "g2_eight_rejects_scenario_index_override");
        res->end_state = res->state_reached = state_before;
        res->elapsed_ms = GetTickCount() - t0;
        return;
    }

    if (is_g2_eight_goal(req->goal) && !g2_setup_preflight()) {
        control_log_event(req->request_id, "chain_abort", req->goal,
                          state_before, 0xFFFFFFFF, "chain_inject",
                          "g2_setup_preflight_failed");
        set_reason(res, CP_REASON_AXIS_ENV, "g2_setup_preflight_failed");
        res->end_state = res->state_reached = state_before;
        res->elapsed_ms = GetTickCount() - t0;
        return;
    }

    /* PS=15/20에서 chain 시작 시: 시나리오 인덱스 + 선택 완료 플래그를 미리 세팅.
     * FUN_004b21c0(briefing init)이 DAT_009e1dd8으로 SPR 경로를 구성하므로
     * 유효한 인덱스가 없으면 hang.  capture_scenario1_phase1.py 검증상
     * DAT_009e1dd8은 1-based scenario id여야 하며 0은 SCRIPT001 오류 경로다. */
    if (state_before == 15 || state_before == 20 ||
        lstrcmpA(req->goal, "_scenario1_direct_ingame") == 0) {
        volatile USHORT *pIdx  = (USHORT *)(uintptr_t)SCENARIO_INDEX_VA;
        volatile USHORT *pFlag = (USHORT *)(uintptr_t)SCENARIO_FLAG_VA;
        if (!IsBadWritePtr((LPVOID)pIdx,  sizeof(USHORT)) &&
            !IsBadWritePtr((LPVOID)pFlag, sizeof(USHORT))) {
            if (*pIdx == 0 && *pFlag == 0) {
                *pIdx  = 1; /* 첫 번째 시나리오 (제 1장 노량해전) */
                *pFlag = 1; /* 선택 완료 */
                control_log_event(req->request_id, "scenario_index_set",
                                  req->goal, 0xFFFFFFFF, 0,
                                  "chain_inject", "idx=1 flag=1");
            }
            if (lstrcmpA(req->goal, "_scenario1_chain_ingame") == 0 ||
                lstrcmpA(req->goal, "_scenario1_direct_ingame") == 0) {
                *pIdx = 1;
                *pFlag = 1;
                control_log_event(req->request_id, "scenario_index_forced",
                                  req->goal, 0xFFFFFFFF, 0,
                                  "chain_inject", "idx=1 flag=1 direct_ingame");
            }
        }
    }

    /* Custom game path (target==2): pre-initialize 0x632c9c setup area so
     * FUN_0041b9b0 (PS=2 handler) runs cleanly.
     *
     * FUN_004464f0 uses (player_or_gametype * 3 + FUN_0044ffe0()) as a byte
     * offset into a local stack table to get sVar10 (NPC/player count).
     * With all-zero BSS:
     *   - DAT_00632cc0 entries all 0 → iVar9=0 (no active players)
     *   - index = 0 → hits uninitialized local_b0 → sVar10=-26649 → YMAP crash
     *
     * Fix both potential sources of the index:
     *   1. Player table: set 2 active entries in DAT_00632cc0 (first byte
     *      of each 6-byte entry != 0 and != 6 counts as active).
     *      With iVar9=2: index=6 → local_98=4 → sVar10=4 (valid).
     *   2. Game type: set DAT_00632d44=2 (if param_1 = game_type):
     *      index=6 → same result.
     *   3. Map size: DAT_00632d4a=0 → FUN_0042dff0(100,100,0) → 100x100 map
     *      → FUN_0044ffe0()=0 (small) → index offset = 0.
     *
     * NOTE: Do NOT call FUN_004b93d0(-1) from this worker thread.
     * Calling it while the game main thread runs PS=7 causes a threading
     * race that stalls PS=140 dispatch forever. */
    if (target == 2) {
        /* player table: 8 entries × 6 bytes at 0x632cc0.
         * byte[0] of entry: 0=inactive, 6=inactive, else=active. */
        volatile BYTE *pLobby = (BYTE *)(uintptr_t)G2_LOBBY_VA;
        volatile BYTE *pPlr0 = (BYTE *)(uintptr_t)0x00632CC0u; /* entry 0 flag */
        volatile BYTE *pPlr1 = (BYTE *)(uintptr_t)0x00632CC6u; /* entry 1 flag */
        volatile USHORT *pGameMode    = (USHORT *)(uintptr_t)0x00632D42u;
        volatile USHORT *pGameType    = (USHORT *)(uintptr_t)0x00632D44u;
        volatile USHORT *pTerrainB    = (USHORT *)(uintptr_t)0x00632D46u;
        volatile USHORT *pMapSelector = (USHORT *)(uintptr_t)0x00632D48u;
            volatile USHORT *pMapSizeFlag = (USHORT *)(uintptr_t)0x00632D4Au;
            volatile USHORT *pTileTheme   = (USHORT *)(uintptr_t)0x00632D4Cu;
            volatile USHORT *pSessionKind = (USHORT *)(uintptr_t)0x00632D54u;
            volatile USHORT *pSeedSupplier = (USHORT *)(uintptr_t)0x00632D92u;
        volatile USHORT *pRawGateB = (USHORT *)(uintptr_t)G2_RAW_GATE_B_VA;
        if (!IsBadWritePtr((LPVOID)pPlr0,      sizeof(BYTE))  &&
            !IsBadWritePtr((LPVOID)pPlr1,      sizeof(BYTE))  &&
            !IsBadWritePtr((LPVOID)pGameMode,  sizeof(USHORT)) &&
            !IsBadWritePtr((LPVOID)pGameType,  sizeof(USHORT)) &&
            !IsBadWritePtr((LPVOID)pTerrainB,  sizeof(USHORT)) &&
            !IsBadWritePtr((LPVOID)pMapSelector,sizeof(USHORT)) &&
            !IsBadWritePtr((LPVOID)pMapSizeFlag,sizeof(USHORT)) &&
            !IsBadWritePtr((LPVOID)pTileTheme, sizeof(USHORT)) &&
            !IsBadWritePtr((LPVOID)pSessionKind, sizeof(USHORT))) {
            BYTE nation0 = 1, nation1 = 2;
            USHORT game_mode = *pGameMode;
            USHORT d44 = 2;
            USHORT d46 = *pTerrainB;
            USHORT d48 = *pMapSelector;
            USHORT d4a = 0;
            USHORT d4c = *pTileTheme;
            char detail[160];
            char map_name_buf[64];
            BOOL custom_map_name = FALSE;
            USHORT seed_value = 0;
            BOOL has_seed = chain_inject_seed_from_goal(req->goal, &seed_value);
            (void)plus_map_name_from_goal(req->goal, map_name_buf, sizeof(map_name_buf), &custom_map_name);
            if (is_g2_eight_goal(req->goal)) {
                /* FUN_0041B9B0 consumes the complete lobby blob and creates
                 * PlayerStructs. Populate only that source blob: never write
                 * the PlayerStruct arena directly. All preconditions above are checked
                 * before the first roster byte is changed. */
                int owner;
                /* record[2] is owner0's is_cpu/AI-controller flag (W21 Step0,
                 * N56): G2_EIGHT_GOAL leaves owner0 as a human slot (=0) so
                 * existing lap419~442 evidence is unchanged; G2_EIGHT_AI_GOAL
                 * is the only goal that flips owner0 to =1 as well. */
                BOOL owner0_ai = (lstrcmpA(req->goal, G2_EIGHT_GOAL) != 0);
                /* W22 (lap456 work) fixture-lever arms: each below is an
                 * exact-goal override of exactly one lobby field, no effect
                 * on any other goal string (card boundary §1-3). */
                BOOL want_d4a1 = (lstrcmpA(req->goal, G2_EIGHT_AI_D4A1_GOAL) == 0);
                BOOL want_d44_0 = (lstrcmpA(req->goal, G2_EIGHT_AI_D44_0_GOAL) == 0);
                BOOL want_d46_1 = (lstrcmpA(req->goal, G2_EIGHT_AI_D46_1_GOAL) == 0);
                BOOL want_ai4 = (lstrcmpA(req->goal, G2_EIGHT_AI_AI4_GOAL) == 0);
                if (*pRawGateB != 0) {
                    control_log_event(req->request_id, "game_setup_abort",
                                      req->goal, state_before, state_before,
                                      "chain_inject",
                                      "g2_requires_B93988_zero");
                    set_reason(res, CP_REASON_AXIS_LOGIC,
                               "g2_requires_B93988_zero");
                    res->end_state = res->state_reached = state_before;
                    res->elapsed_ms = GetTickCount() - t0;
                    return;
                }
                nation0 = 1;
                nation1 = 1;
                game_mode = 0; /* requested ordinary-mode diagnostic; UI label unverified */
                d44 = want_d44_0 ? 0 : 2; /* verified small-map game type unless W22 A3 override */
                d46 = want_d46_1 ? 1 : 0; /* W22 A5 terrain override */
                d48 = 0;
                d4a = want_d4a1 ? 1 : 0;  /* original 100x100 small-map unless W22 A1 override */
                d4c = 0;
                for (owner = 0; owner < G2_LOBBY_RECORDS; ++owner) {
                    volatile BYTE *record = pLobby + owner * G2_LOBBY_STRIDE;
                    BOOL owner_ai = (owner == 0) ? owner0_ai : TRUE;
                    /* W22 A2: owners 4..7 stay present (roster/persistence
                     * layout unchanged) but are marked non-AI so they do not
                     * self-play, leaving 4 active AI competitors instead of
                     * 8 (card section 3 A2 note: diagnostic, not "4-player
                     * pass"). */
                    if (want_ai4 && owner >= 4) {
                        owner_ai = FALSE;
                    }
                    record[0] = 1; /* Joseon */
                    record[1] = (BYTE)owner;
                    record[2] = (BYTE)(owner_ai ? 1 : 0);
                    record[3] = (BYTE)(1u << owner);
                    record[4] = 0; /* FUN_0041B9B0 derives enemy mask */
                    record[5] = (BYTE)owner;
                }
            } else {
            chain_inject_nations_for_goal(req->goal, &nation0, &nation1);
            if (lstrcmpA(req->goal, "_custom_game_chain_inject_map2") == 0) {
                game_mode = 3;
                d44 = 2;
                d46 = 0;
                d48 = 2;
                d4a = 0;
                d4c = 0;
            } else if (plus_map_name_from_goal(req->goal, detail, sizeof(detail), NULL)) {
                game_mode = 3;
                d44 = 2;
                d46 = 0;
                d48 = 0;
                d4a = 0;
                d4c = 0;
            } else if (chain_inject_goal_matches(req->goal, "_custom_game_chain_inject_d44_0")) {
                game_mode = 3;
                d44 = 0;
                d46 = 0;
                d48 = 0;
                d4a = 0;
                d4c = 0;
            } else if (lstrcmpA(req->goal, "_custom_game_chain_inject_d44_1") == 0) {
                game_mode = 3;
                d44 = 1;
                d46 = 0;
                d48 = 0;
                d4a = 0;
                d4c = 0;
            } else if (lstrcmpA(req->goal, "_custom_game_chain_inject_d44_0_d46_1") == 0) {
                game_mode = 3;
                d44 = 0;
                d46 = 1;
                d48 = 0;
                d4a = 0;
                d4c = 0;
            } else if (lstrcmpA(req->goal, "_custom_game_chain_inject_d44_0_d46_2") == 0) {
                game_mode = 3;
                d44 = 0;
                d46 = 2;
                d48 = 0;
                d4a = 0;
                d4c = 0;
            } else if (lstrcmpA(req->goal, "_custom_game_chain_inject_d44_1_d46_1") == 0) {
                game_mode = 3;
                d44 = 1;
                d46 = 1;
                d48 = 0;
                d4a = 0;
                d4c = 0;
            } else if (lstrcmpA(req->goal, "_custom_game_chain_inject_d44_1_d46_2") == 0) {
                game_mode = 3;
                d44 = 1;
                d46 = 2;
                d48 = 0;
                d4a = 0;
                d4c = 0;
            } else if (lstrcmpA(req->goal, "_custom_game_chain_inject_d46_1") == 0) {
                game_mode = 3;
                d44 = 2;
                d46 = 1;
                d48 = 0;
                d4a = 0;
                d4c = 0;
            } else if (lstrcmpA(req->goal, "_custom_game_chain_inject_d46_2") == 0) {
                game_mode = 3;
                d44 = 2;
                d46 = 2;
                d48 = 0;
                d4a = 0;
                d4c = 0;
            }
            }
            *pPlr0        = nation0;  /* player 0: active nation */
            *pPlr1        = nation1;  /* player 1: active AI nation */
            *pGameMode    = game_mode;
            *pGameType    = d44;  /* DAT_00632d44=2 DAT_00632d4a=0: game type 2, small map → sVar10=4 */
            *pTerrainB    = d46;
            *pMapSelector = d48;
            *pMapSizeFlag = d4a;  /* map size 0 → FUN_0042dff0(100,100,0) */
            *pTileTheme   = d4c;
            *pSessionKind = custom_map_name ? 1 : 0;
            if (has_seed && !IsBadWritePtr((LPVOID)pSeedSupplier, sizeof(USHORT))) {
                *pSeedSupplier = seed_value;
            }
            const char *map_name = "";
            if (plus_map_name_from_goal(req->goal, map_name_buf, sizeof(map_name_buf), &custom_map_name)) {
                map_name = map_name_buf;
            }
            if (map_name[0] != '\0') {
                volatile char *pMapName = (char *)(uintptr_t)0x00632D56u;
                /* DAT_00632D56 sits before DAT_00632D92; keep writes below
                 * that 0x3c-byte gap so long parent paths do not clobber the
                 * seed word. */
                if (!IsBadWritePtr((LPVOID)pMapName, 60)) {
                    ZeroMemory((LPVOID)pMapName, 60);
                    lstrcpynA((LPSTR)pMapName, map_name, 60);
                }
            }
            wsprintfA(detail,
                      "plr0=%u plr1=%u d42=%u d44=%u d46=%u d48=%u d4a=%u d4c=%u d54=%u seed=%u map=%s",
                      (unsigned)nation0, (unsigned)nation1,
                      (unsigned)game_mode, (unsigned)d44, (unsigned)d46,
                      (unsigned)d48, (unsigned)d4a, (unsigned)d4c,
                      (unsigned)(custom_map_name ? 1 : 0),
                      (unsigned)(has_seed ? seed_value : 0), map_name);
            control_log_event(req->request_id, "game_setup_preinit", req->goal,
                              state_before, state_before, "chain_inject",
                              detail);
        }
    }

    /* DAT_00b92cc0 = target, DAT_004ed818 = 140 (chain start) */
    {
        volatile SHORT *pChain = (SHORT *)(uintptr_t)CG_CHAIN_VALUE_VA;
        volatile USHORT *pPS   = (USHORT *)(uintptr_t)PROGRAM_STATE_VA;
        if (IsBadWritePtr((LPVOID)pChain, sizeof(SHORT)) ||
            IsBadWritePtr((LPVOID)pPS,    sizeof(USHORT))) {
            control_log_event(req->request_id, "chain_abort", req->goal,
                              state_before, 0xFFFFFFFF, "chain_inject",
                              "addrs unwritable");
            set_reason(res, CP_REASON_AXIS_ENV, "flag_unwritable");
            res->end_state = res->state_reached = state_before;
            res->elapsed_ms = GetTickCount() - t0;
            return;
        }
        *pChain = (SHORT)target;
        *pPS    = 140; /* 0x8C */
    }
    {
        char detail[64];
        wsprintfA(detail, "DAT_00b92cc0=%d PS=140", target);
        control_log_event(req->request_id, "chain_inject_set", req->goal,
                          state_before, 140, "chain_inject", detail);
    }

    /* chain polling up to timeout */
    DWORD timeout = (req->timeout_ms > 0) ? req->timeout_ms : 10000;
    DWORD deadline = GetTickCount() + timeout;
    DWORD path[32];
    int   plen = 1;
    path[0] = state_before;
    cur = 140;

    while (GetTickCount() < deadline) {
        if (csb_read_state(&cur)) {
            if (plen < 32 && cur != path[plen - 1]) {
                path[plen++] = cur;
                char ev[48];
                wsprintfA(ev, "chain PS=%u", (unsigned)cur);
                control_log_event(req->request_id,
                                  "state_change_observed",
                                  req->goal, path[plen - 2], cur,
                                  "chain_inject", ev);
                if (cur == 3) break;
            }
        }
        Sleep(30);
    }

    char detail[256];
    detail[0] = '\0';
    for (int i = 0; i < plen; ++i) {
        char tmp[16];
        wsprintfA(tmp, i ? ",%u" : "%u", (unsigned)path[i]);
        if (lstrlenA(detail) + lstrlenA(tmp) + 1 < (int)sizeof(detail))
            lstrcatA(detail, tmp);
    }
    control_log_event(req->request_id, "chain_probe_done", req->goal,
                      state_before, cur, "chain_inject", detail);

    lstrcpynA(res->fallback_chain, detail, sizeof(res->fallback_chain));
    res->fallback_count = (DWORD)plen;
    res->state_reached = cur;
    res->end_state     = cur;
    res->ok            = (cur == 3);
    res->elapsed_ms    = GetTickCount() - t0;
    if (cur == 3)
        set_reason(res, "", "chain_reached_ingame");
    else if (cur != state_before)
        set_reason(res, CP_REASON_AXIS_LOGIC, "chain_partial");
    else
        set_reason(res, CP_REASON_AXIS_LOGIC, "chain_no_effect");
}


/* ------------------------------------------------------------------ */
/* 0206/0204 map widget probe — "_custom_game_map_widget_probe"         */
/*                                                                     */
/* Clicks conservative PS=7 client-coordinate candidates and records     */
/* raw setup globals after each click to C:\inmm_map_widget_probe.json. */
/* This is evidence collection only: it must not be used as parity pass. */
/* ------------------------------------------------------------------ */
static BOOL is_map_widget_probe_goal(const char *goal)
{
    return (lstrcmpA(goal, "_custom_game_map_widget_probe") == 0);
}

static USHORT read_u16_va(DWORD va)
{
    volatile USHORT *p = (volatile USHORT *)(uintptr_t)va;
    if (IsBadReadPtr((LPCVOID)p, sizeof(USHORT))) return 0xFFFFu;
    return *p;
}

static void run_map_widget_probe(const control_request_t *req,
                                 control_result_t *res)
{
    DWORD state_before = 0xFFFFFFFFu, cur = 0;
    DWORD t0 = GetTickCount();
    HWND hwnd = cib_get_hwnd();
    int changed_count = 0;
    int clicked_count = 0;

    csb_read_state(&state_before);
    res->start_state = state_before;
    lstrcpyA(res->bridge_used, "map_widget");

    if (state_before != 7 || !hwnd) {
        control_log_event(req->request_id, "map_widget_abort", req->goal,
                          state_before, 0xFFFFFFFF, "map_widget",
                          hwnd ? "not_in_ps7" : "no_hwnd");
        set_reason(res, CP_REASON_AXIS_LOGIC,
                   hwnd ? "not_in_custom_game" : "no_hwnd");
        res->end_state = res->state_reached = state_before;
        res->elapsed_ms = GetTickCount() - t0;
        return;
    }

    const USHORT base_d42 = read_u16_va(0x00632D42u);
    const USHORT base_d44 = read_u16_va(0x00632D44u);
    const USHORT base_d46 = read_u16_va(0x00632D46u);
    const USHORT base_d48 = read_u16_va(0x00632D48u);
    const USHORT base_d4a = read_u16_va(0x00632D4Au);
    const USHORT base_d4c = read_u16_va(0x00632D4Cu);

    /* Broad but conservative: avoid very bottom start/back areas. */
    const int points[][2] = {
        {180,180},{240,180},{300,180},{360,180},{420,180},{480,180},{540,180},{600,180},
        {180,220},{240,220},{300,220},{360,220},{420,220},{480,220},{540,220},{600,220},
        {180,260},{240,260},{300,260},{360,260},{420,260},{480,260},{540,260},{600,260},
        {180,300},{240,300},{300,300},{360,300},{420,300},{480,300},{540,300},{600,300},
        {180,340},{240,340},{300,340},{360,340},{420,340},{480,340},{540,340},{600,340},
        {180,380},{240,380},{300,380},{360,380},{420,380},{480,380},{540,380},{600,380},
        {180,420},{240,420},{300,420},{360,420},{420,420},{480,420},{540,420},{600,420},
        {180,460},{240,460},{300,460},{360,460},{420,460},{480,460},{540,460},{600,460}
    };
    const int npoints = (int)(sizeof(points) / sizeof(points[0]));

    static char json[8192];
    int pos = 0;
    pos += wsprintfA(json + pos,
        "{\"schema_version\":1,\"todo\":\"TODO-PARITY-ALL-0206\","
        "\"status\":\"ps7-map-widget-probe\",\"start_state\":%u,"
        "\"baseline\":{\"d42\":%u,\"d44\":%u,\"d46\":%u,\"d48\":%u,\"d4a\":%u,\"d4c\":%u},"
        "\"samples\":[",
        (unsigned)state_before,
        (unsigned)base_d42,(unsigned)base_d44,(unsigned)base_d46,
        (unsigned)base_d48,(unsigned)base_d4a,(unsigned)base_d4c);

    for (int i = 0; i < npoints; ++i) {
        int x = points[i][0], y = points[i][1];
        mouse_click(hwnd, x, y);
        Sleep(120);
        csb_read_state(&cur);
        const USHORT d42 = read_u16_va(0x00632D42u);
        const USHORT d44 = read_u16_va(0x00632D44u);
        const USHORT d46 = read_u16_va(0x00632D46u);
        const USHORT d48 = read_u16_va(0x00632D48u);
        const USHORT d4a = read_u16_va(0x00632D4Au);
        const USHORT d4c = read_u16_va(0x00632D4Cu);
        const int changed = (d42 != base_d42 || d44 != base_d44 || d46 != base_d46 ||
                             d48 != base_d48 || d4a != base_d4a || d4c != base_d4c);
        if (changed) changed_count++;
        if (pos < (int)sizeof(json) - 256) {
            pos += wsprintfA(json + pos,
                "%s{\"i\":%d,\"x\":%d,\"y\":%d,\"ps\":%u,\"changed\":%s,"
                "\"d42\":%u,\"d44\":%u,\"d46\":%u,\"d48\":%u,\"d4a\":%u,\"d4c\":%u}",
                clicked_count ? "," : "", i, x, y, (unsigned)cur,
                changed ? "true" : "false",
                (unsigned)d42,(unsigned)d44,(unsigned)d46,
                (unsigned)d48,(unsigned)d4a,(unsigned)d4c);
        }
        clicked_count++;
        if (cur != state_before) break;
    }
    pos += wsprintfA(json + pos,
        "],\"clicked_count\":%d,\"changed_count\":%d,\"end_state\":%u}",
        clicked_count, changed_count, (unsigned)cur);

    HANDLE hf = CreateFileA("C:\\inmm_map_widget_probe.json",
                            GENERIC_WRITE, 0, NULL, CREATE_ALWAYS,
                            FILE_ATTRIBUTE_NORMAL, NULL);
    if (hf != INVALID_HANDLE_VALUE) {
        DWORD written;
        WriteFile(hf, json, (DWORD)pos, &written, NULL);
        CloseHandle(hf);
    }

    res->state_reached = cur;
    res->end_state = cur;
    res->ok = TRUE;
    res->fallback_count = (DWORD)changed_count;
    res->elapsed_ms = GetTickCount() - t0;
    wsprintfA(res->fallback_chain, "clicked=%d changed=%d", clicked_count, changed_count);
    set_reason(res, "", changed_count ? "map_widget_changed" : "map_widget_no_change");
    control_log_event(req->request_id, "map_widget_done", req->goal,
                      state_before, cur, "map_widget", res->fallback_chain);
}

/* ------------------------------------------------------------------ */
/* 0206 child-control probe — "_custom_game_child_control_probe"       */
/*                                                                     */
/* Blind client-coordinate clicking did not hit a map selector.  The    */
/* next non-circular step is to ask Win32 what child/dialog controls     */
/* actually exist while PS=7 is displayed, especially the controls seen */
/* in FUN_004A6470 (0x40f, 0x421, 0x422, 0x425, ...).  This goal only   */
/* dumps control metadata to C:\inmm_child_controls.json.               */
/* ------------------------------------------------------------------ */
static BOOL is_child_control_probe_goal(const char *goal)
{
    return (lstrcmpA(goal, "_custom_game_child_control_probe") == 0);
}

typedef struct {
    HWND main_hwnd;
    char *json;
    int pos;
    int cap;
    int count;
    int interesting_count;
} child_probe_ctx_t;

static void json_append_ascii_string(char *dst, int *pos, int cap, const char *src)
{
    int p = *pos;
    if (p < cap) dst[p++] = '"';
    if (src) {
        for (int i = 0; src[i] && p < cap - 3; ++i) {
            unsigned char c = (unsigned char)src[i];
            if (c == '"' || c == '\\') {
                dst[p++] = '\\';
                dst[p++] = (char)c;
            } else if (c >= 0x20 && c < 0x7f) {
                dst[p++] = (char)c;
            } else {
                dst[p++] = '?';
            }
        }
    }
    if (p < cap) dst[p++] = '"';
    *pos = p;
    if (p < cap) dst[p] = '\0';
}

static int is_interesting_control_id(int id)
{
    return (id == 0x40e || id == 0x40f || id == 0x410 ||
            id == 0x41e || id == 0x420 || id == 0x421 ||
            id == 0x422 || id == 0x425 ||
            (id >= 0x44c && id <= 0x450) ||
            (id >= 0x514 && id <= 0x517));
}

static BOOL CALLBACK enum_child_probe_cb(HWND hwnd, LPARAM lparam)
{
    child_probe_ctx_t *ctx = (child_probe_ctx_t *)lparam;
    RECT r;
    POINT tl, br;
    char cls[64];
    char text[96];
    int id;
    int interesting;

    if (!ctx || ctx->count >= 512 || ctx->pos >= ctx->cap - 512)
        return TRUE;

    cls[0] = '\0';
    text[0] = '\0';
    GetClassNameA(hwnd, cls, sizeof(cls));
    GetWindowTextA(hwnd, text, sizeof(text));
    id = GetDlgCtrlID(hwnd);
    interesting = is_interesting_control_id(id);
    if (interesting) ctx->interesting_count++;

    GetWindowRect(hwnd, &r);
    tl.x = r.left; tl.y = r.top;
    br.x = r.right; br.y = r.bottom;
    if (ctx->main_hwnd) {
        ScreenToClient(ctx->main_hwnd, &tl);
        ScreenToClient(ctx->main_hwnd, &br);
    }

    ctx->pos += wsprintfA(ctx->json + ctx->pos,
        "%s{\"i\":%d,\"hwnd\":\"0x%08X\",\"parent\":\"0x%08X\","
        "\"id\":%d,\"id_hex\":\"0x%03X\",\"interesting\":%s,"
        "\"visible\":%s,\"enabled\":%s,\"rect_client\":[%d,%d,%d,%d],"
        "\"class\":",
        ctx->count ? "," : "",
        ctx->count,
        (unsigned)(UINT_PTR)hwnd,
        (unsigned)(UINT_PTR)GetParent(hwnd),
        id,
        (unsigned)(id & 0xFFFF),
        interesting ? "true" : "false",
        IsWindowVisible(hwnd) ? "true" : "false",
        IsWindowEnabled(hwnd) ? "true" : "false",
        tl.x, tl.y, br.x, br.y);
    json_append_ascii_string(ctx->json, &ctx->pos, ctx->cap, cls);
    if (ctx->pos < ctx->cap - 128) {
        ctx->pos += wsprintfA(ctx->json + ctx->pos, ",\"text\":");
        json_append_ascii_string(ctx->json, &ctx->pos, ctx->cap, text);
        ctx->pos += wsprintfA(ctx->json + ctx->pos, "}");
    }
    ctx->count++;
    return TRUE;
}

static BOOL CALLBACK enum_top_probe_cb(HWND hwnd, LPARAM lparam)
{
    enum_child_probe_cb(hwnd, lparam);
    EnumChildWindows(hwnd, enum_child_probe_cb, lparam);
    return TRUE;
}

static void run_child_control_probe(const control_request_t *req,
                                    control_result_t *res)
{
    DWORD state_before = 0xFFFFFFFFu, cur = 0;
    DWORD t0 = GetTickCount();
    HWND hwnd = cib_get_hwnd();
    static char json[65536];
    child_probe_ctx_t ctx;

    csb_read_state(&state_before);
    res->start_state = state_before;
    lstrcpyA(res->bridge_used, "child_controls");

    if (!hwnd) {
        control_log_event(req->request_id, "child_control_abort", req->goal,
                          state_before, 0xFFFFFFFF, "child_controls",
                          "no_hwnd");
        set_reason(res, CP_REASON_AXIS_LOGIC, "no_hwnd");
        res->end_state = res->state_reached = state_before;
        res->elapsed_ms = GetTickCount() - t0;
        return;
    }

    ctx.main_hwnd = hwnd;
    ctx.json = json;
    ctx.pos = 0;
    ctx.cap = (int)sizeof(json);
    ctx.count = 0;
    ctx.interesting_count = 0;

    ctx.pos += wsprintfA(json + ctx.pos,
        "{\"schema_version\":1,\"todo\":\"TODO-PARITY-ALL-0206\","
        "\"status\":\"ps7-child-control-probe\",\"start_state\":%u,"
        "\"main_hwnd\":\"0x%08X\","
        "\"raw_globals\":{\"d42\":%u,\"d44\":%u,\"d46\":%u,\"d48\":%u,"
        "\"d4a\":%u,\"d4c\":%u},\"controls\":[",
        (unsigned)state_before,
        (unsigned)(UINT_PTR)hwnd,
        (unsigned)read_u16_va(0x00632D42u),
        (unsigned)read_u16_va(0x00632D44u),
        (unsigned)read_u16_va(0x00632D46u),
        (unsigned)read_u16_va(0x00632D48u),
        (unsigned)read_u16_va(0x00632D4Au),
        (unsigned)read_u16_va(0x00632D4Cu));

    EnumWindows(enum_top_probe_cb, (LPARAM)&ctx);
    csb_read_state(&cur);

    if (ctx.pos < ctx.cap - 128) {
        ctx.pos += wsprintfA(json + ctx.pos,
            "],\"control_count\":%d,\"interesting_control_count\":%d,"
            "\"end_state\":%u}",
            ctx.count, ctx.interesting_count, (unsigned)cur);
    }

    HANDLE hf = CreateFileA("C:\\inmm_child_controls.json",
                            GENERIC_WRITE, 0, NULL, CREATE_ALWAYS,
                            FILE_ATTRIBUTE_NORMAL, NULL);
    if (hf != INVALID_HANDLE_VALUE) {
        DWORD written;
        WriteFile(hf, json, (DWORD)ctx.pos, &written, NULL);
        CloseHandle(hf);
    }

    res->state_reached = cur;
    res->end_state = cur;
    res->ok = TRUE;
    res->fallback_count = (DWORD)ctx.interesting_count;
    res->elapsed_ms = GetTickCount() - t0;
    wsprintfA(res->fallback_chain, "controls=%d interesting=%d",
              ctx.count, ctx.interesting_count);
    set_reason(res, "", ctx.interesting_count ? "child_controls_found" : "child_controls_no_interesting_ids");
    control_log_event(req->request_id, "child_control_done", req->goal,
                      state_before, cur, "child_controls", res->fallback_chain);
}

/* ------------------------------------------------------------------ */
/* 0204/0206 lobby map probe — "_custom_game_lobby_map_probe"          */
/*                                                                     */
/* PS=5 is the actual game lobby screen with the visible map list.      */
/* Probe the visible list row coordinates from the captured lobby shot  */
/* and record whether DAT_00632D56 / setup globals change.              */
/* ------------------------------------------------------------------ */
static BOOL is_lobby_map_probe_goal(const char *goal)
{
    return (lstrcmpA(goal, "_custom_game_lobby_map_probe") == 0);
}

static void read_ascii_va(DWORD va, char *out, int out_cap)
{
    int i;
    if (out_cap <= 0) return;
    out[0] = '\0';
    for (i = 0; i < out_cap - 1; ++i) {
        volatile char *p = (volatile char *)(uintptr_t)(va + (DWORD)i);
        char c;
        if (IsBadReadPtr((LPCVOID)p, 1)) break;
        c = *p;
        if (!c) break;
        out[i] = c;
    }
    out[i] = '\0';
}

static void run_lobby_map_probe(const control_request_t *req,
                                control_result_t *res)
{
    DWORD state_before = 0xFFFFFFFFu, cur = 0;
    DWORD t0 = GetTickCount();
    HWND hwnd = cib_get_hwnd();
    int changed_count = 0;
    int clicked_count = 0;
    char base_map[96];
    static char json[8192];
    int pos = 0;

    csb_read_state(&state_before);
    res->start_state = state_before;
    lstrcpyA(res->bridge_used, "lobby_map");

    if (state_before != 5 || !hwnd) {
        control_log_event(req->request_id, "lobby_map_abort", req->goal,
                          state_before, 0xFFFFFFFF, "lobby_map",
                          hwnd ? "not_in_ps5" : "no_hwnd");
        set_reason(res, CP_REASON_AXIS_LOGIC,
                   hwnd ? "not_in_lobby" : "no_hwnd");
        res->end_state = res->state_reached = state_before;
        res->elapsed_ms = GetTickCount() - t0;
        return;
    }

    read_ascii_va(0x00632D56u, base_map, sizeof(base_map));

    /* Visible PS=5 map list rows from original lobby screenshot:
     * x around 500, y around 122/143/164/184/204/224. */
    const int points[][2] = {
        {500,122}, {500,143}, {500,164}, {500,184}, {500,204}, {500,224},
        {620,122}, {620,143}, {620,164}, {620,184}, {620,204}, {620,224}
    };
    const int npoints = (int)(sizeof(points) / sizeof(points[0]));

    pos += wsprintfA(json + pos,
        "{\"schema_version\":1,\"todo\":\"TODO-PARITY-ALL-0204\","
        "\"status\":\"ps5-lobby-map-probe\",\"start_state\":%u,"
        "\"baseline\":{\"d42\":%u,\"d44\":%u,\"d46\":%u,\"d48\":%u,"
        "\"d4a\":%u,\"d4c\":%u,\"map_name\":",
        (unsigned)state_before,
        (unsigned)read_u16_va(0x00632D42u),
        (unsigned)read_u16_va(0x00632D44u),
        (unsigned)read_u16_va(0x00632D46u),
        (unsigned)read_u16_va(0x00632D48u),
        (unsigned)read_u16_va(0x00632D4Au),
        (unsigned)read_u16_va(0x00632D4Cu));
    json_append_ascii_string(json, &pos, sizeof(json), base_map);
    pos += wsprintfA(json + pos, "},\"samples\":[");

    for (int i = 0; i < npoints; ++i) {
        int x = points[i][0], y = points[i][1];
        char map_name[96];
        int changed;
        mouse_click(hwnd, x, y);
        Sleep(300);
        csb_read_state(&cur);
        read_ascii_va(0x00632D56u, map_name, sizeof(map_name));
        changed = (lstrcmpA(map_name, base_map) != 0 ||
                   read_u16_va(0x00632D42u) != read_u16_va(0x00632D42u));
        if (lstrcmpA(map_name, base_map) != 0) changed_count++;
        if (pos < (int)sizeof(json) - 384) {
            pos += wsprintfA(json + pos,
                "%s{\"i\":%d,\"x\":%d,\"y\":%d,\"ps\":%u,"
                "\"changed\":%s,\"d42\":%u,\"d44\":%u,\"d46\":%u,"
                "\"d48\":%u,\"d4a\":%u,\"d4c\":%u,\"map_name\":",
                clicked_count ? "," : "", i, x, y, (unsigned)cur,
                changed ? "true" : "false",
                (unsigned)read_u16_va(0x00632D42u),
                (unsigned)read_u16_va(0x00632D44u),
                (unsigned)read_u16_va(0x00632D46u),
                (unsigned)read_u16_va(0x00632D48u),
                (unsigned)read_u16_va(0x00632D4Au),
                (unsigned)read_u16_va(0x00632D4Cu));
            json_append_ascii_string(json, &pos, sizeof(json), map_name);
            pos += wsprintfA(json + pos, "}");
        }
        clicked_count++;
        if (cur != state_before) break;
    }

    pos += wsprintfA(json + pos,
        "],\"clicked_count\":%d,\"changed_count\":%d,\"end_state\":%u}",
        clicked_count, changed_count, (unsigned)cur);

    HANDLE hf = CreateFileA("C:\\inmm_lobby_map_probe.json",
                            GENERIC_WRITE, 0, NULL, CREATE_ALWAYS,
                            FILE_ATTRIBUTE_NORMAL, NULL);
    if (hf != INVALID_HANDLE_VALUE) {
        DWORD written;
        WriteFile(hf, json, (DWORD)pos, &written, NULL);
        CloseHandle(hf);
    }

    res->state_reached = cur;
    res->end_state = cur;
    res->ok = TRUE;
    res->fallback_count = (DWORD)changed_count;
    res->elapsed_ms = GetTickCount() - t0;
    wsprintfA(res->fallback_chain, "clicked=%d changed=%d", clicked_count, changed_count);
    set_reason(res, "", changed_count ? "lobby_map_changed" : "lobby_map_no_change");
    control_log_event(req->request_id, "lobby_map_done", req->goal,
                      state_before, cur, "lobby_map", res->fallback_chain);
}

/* ------------------------------------------------------------------ */
/* NOW-0701 step 2 — "_combat_melee_adjacent"                          */
/*                                                                     */
/* race-AI free_battle 시나리오는 양 진영을 맵의 반대편(체비셰프 거리 65+)*/
/* 에 스폰해 1200틱 캡처 창에서 교전이 발생하지 않는다 (combat_oracle_  */
/* 0701_report blocker 참조). 이 sub-goal은 chain_inject 완료 후 (PS=3)*/
/* 호출되어 다음을 수행한다:                                            */
/*                                                                     */
/*   1. unit array를 스캔해 owner 0/1 각각의 첫 전투형(체력>0, ATK>0,   */
/*      worker/builder 제외) 유닛을 1개씩 선택.                         */
/*   2. 두 유닛을 인접 타일((10,10)/(11,10))로 강제 재배치 — +0x2A2/    */
/*      +0x2A4 직접 기입.                                               */
/*   3. 각 유닛의 target_unit_id(+0x64A)에 상대 unit_id를, command_kind */
/*      (+0x290) 0x04 (move-to-attack)을 설정.                         */
/*                                                                     */
/* 본 sub-goal은 race-AI의 동일한 결정 경로를 우회하지 않는다 — 단순히   */
/* 두 유닛의 시작 좌표/타겟을 인접하게 만들어 race-AI 자체 SM이 즉시     */
/* 교전 명령을 내릴 수 있는 상태로 만든다. 데미지 계산/HP 감소/사망     */
/* 판정은 모두 원본 코드 (FUN_00413CE0/FUN_00470600 등)가 수행한다.       */
/* ------------------------------------------------------------------ */
#define UA_EXISTS_VA  0x008990C8u
#define UA_ARRAY_VA   0x0066B790u
#define UA_STRIDE     0x758u
#define UA_COUNT      1200
#define UA_OFF_TYPE   0x08D
#define UA_OFF_OWNER  0x08E
#define UA_OFF_HP     0x0B4
#define UA_OFF_ATK_TIMER 0x07C
#define UA_OFF_AI     0x1F0
#define UA_OFF_CMD    0x290
#define UA_OFF_UID    0x29C
#define UA_OFF_X      0x2A2
#define UA_OFF_Y      0x2A4
#define UA_OFF_TGT    0x64A

static BOOL is_combat_melee_adjacent_goal(const char *goal)
{
    return (lstrcmpA(goal, "_combat_melee_adjacent") == 0 ||
            lstrcmpA(goal, "_combat_scenario1_melee_adjacent") == 0 ||
            lstrcmpA(goal, "_combat_scenario1_melee_isolated") == 0);
}

/* 첫 번째 살아있는 유닛 후보 — owner 일치 + HP>0. race-AI free_battle 시나리오
 * 는 1200~3268 tick 캡처 창에서 buildings/builders만 스폰하므로(전체
 * production_racei_long_0601 캡처 검증) 전투형 unit_type 필터 없이 owner별
 * 첫 단위를 반환한다. 후속 단계가 unit_type 필드를 melee로 재기입한다. */
static int find_any_owned_unit(BYTE want_owner)
{
    int i;
    for (i = 0; i < UA_COUNT; i++) {
        SHORT ex = *((volatile SHORT *)(uintptr_t)(UA_EXISTS_VA + (DWORD)i * 2));
        if (ex == 0) continue;
        DWORD base = UA_ARRAY_VA + (DWORD)i * UA_STRIDE;
        BYTE  own  = *((volatile BYTE *)(uintptr_t)(base + UA_OFF_OWNER));
        DWORD hp   = *((volatile DWORD *)(uintptr_t)(base + UA_OFF_HP));
        if (own != want_owner) continue;
        if (hp == 0) continue;
        return i;
    }
    return -1;
}

/* Scenario-1 combat-capable pair finder.  This is deliberately narrower than
 * the free-battle fallback above: scenario 1 loads genuine combat units through
 * the original scenario initializer, so we select existing owner0 type2
 * (Joseon spear) and owner1 type3 (Japan spear) instances and never rewrite
 * +0x08D. */
static int find_owned_unit_of_type(BYTE want_owner, BYTE want_type)
{
    int i;
    for (i = 0; i < UA_COUNT; i++) {
        SHORT ex = *((volatile SHORT *)(uintptr_t)(UA_EXISTS_VA + (DWORD)i * 2));
        if (ex == 0) continue;
        DWORD base = UA_ARRAY_VA + (DWORD)i * UA_STRIDE;
        BYTE  own  = *((volatile BYTE *)(uintptr_t)(base + UA_OFF_OWNER));
        BYTE  type = *((volatile BYTE *)(uintptr_t)(base + UA_OFF_TYPE));
        DWORD hp   = *((volatile DWORD *)(uintptr_t)(base + UA_OFF_HP));
        if (own != want_owner) continue;
        if (type != want_type) continue;
        if (hp == 0) continue;
        return i;
    }
    return -1;
}

static int neutralize_other_owner1_units_for_isolated_duel(int keep_slot)
{
    int i;
    int moved = 0;
    for (i = 0; i < UA_COUNT; i++) {
        SHORT ex = *((volatile SHORT *)(uintptr_t)(UA_EXISTS_VA + (DWORD)i * 2));
        if (ex == 0) continue;
        if (i == keep_slot) continue;
        DWORD base = UA_ARRAY_VA + (DWORD)i * UA_STRIDE;
        BYTE  own  = *((volatile BYTE *)(uintptr_t)(base + UA_OFF_OWNER));
        DWORD hp   = *((volatile DWORD *)(uintptr_t)(base + UA_OFF_HP));
        if (own != 1) continue;
        if (hp == 0) continue;

        /* Controlled isolation for the oracle capture: keep the selected
         * owner1 type3 attacker intact, but move every other living owner1
         * scenario unit away from the target and clear immediate combat order
         * fields.  Damage/dispatch code remains original; this only prevents
         * the multi-attacker contamination observed in the 2026-06-04
         * FUN_00470600 dispatch capture. */
        *((volatile WORD  *)(uintptr_t)(base + UA_OFF_X)) = (WORD)(40 + (moved % 10));
        *((volatile WORD  *)(uintptr_t)(base + UA_OFF_Y)) = (WORD)(40 + (moved / 10));
        *((volatile WORD  *)(uintptr_t)(base + UA_OFF_TGT)) = 0;
        *((volatile WORD  *)(uintptr_t)(base + UA_OFF_CMD)) = 0;
        *((volatile DWORD *)(uintptr_t)(base + UA_OFF_AI)) = 0;
        *((volatile WORD  *)(uintptr_t)(base + UA_OFF_ATK_TIMER)) = 0;
        moved++;
    }
    return moved;
}

static void run_combat_scenario1_melee_adjacent(const control_request_t *req,
                                                control_result_t *res)
{
    DWORD state_before = 0xFFFFFFFFu;
    DWORD t0 = GetTickCount();
    BOOL isolated = (lstrcmpA(req->goal, "_combat_scenario1_melee_isolated") == 0);
    const char *bridge = isolated
        ? "cs1_isolated"
        : "cs1_adjacent";

    csb_read_state(&state_before);
    res->start_state = state_before;
    lstrcpyA(res->bridge_used, bridge);

    if (state_before != 3) {
        char reason[48];
        wsprintfA(reason, "not_in_ingame_ps=%u", (unsigned)state_before);
        control_log_event(req->request_id, "cs1_abort", req->goal,
                          state_before, 0xFFFFFFFF, bridge, reason);
        set_reason(res, CP_REASON_AXIS_LOGIC, reason);
        res->end_state = res->state_reached = state_before;
        res->elapsed_ms = GetTickCount() - t0;
        return;
    }

    int slot0 = find_owned_unit_of_type(0, 2); /* scenario1 owner0 spearman */
    int slot1 = find_owned_unit_of_type(1, 3); /* scenario1 owner1 spearman */
    if (slot0 < 0 || slot1 < 0) {
        char detail[64];
        wsprintfA(detail, "owner0_type2_slot=%d owner1_type3_slot=%d",
                  slot0, slot1);
        control_log_event(req->request_id, "cs1_no_spearmen", req->goal,
                          state_before, state_before, bridge, detail);
        set_reason(res, CP_REASON_AXIS_LOGIC, "scenario1_spearmen_missing");
        res->end_state = res->state_reached = state_before;
        res->elapsed_ms = GetTickCount() - t0;
        return;
    }

    DWORD base0 = UA_ARRAY_VA + (DWORD)slot0 * UA_STRIDE;
    DWORD base1 = UA_ARRAY_VA + (DWORD)slot1 * UA_STRIDE;
    DWORD uid0 = *((volatile DWORD *)(uintptr_t)(base0 + UA_OFF_UID));
    DWORD uid1 = *((volatile DWORD *)(uintptr_t)(base1 + UA_OFF_UID));
    int neutralized = isolated
        ? neutralize_other_owner1_units_for_isolated_duel(slot1)
        : 0;

    /* Safe combat setup: keep original scenario-spawned unit_type/sprite state,
     * only move both units into adjacent tiles and seed the attack order.  This
     * avoids the documented post-spawn +0x08D retype crash in FUN_00466540. */
    *((volatile WORD *)(uintptr_t)(base0 + UA_OFF_X)) = 10;
    *((volatile WORD *)(uintptr_t)(base0 + UA_OFF_Y)) = 10;
    *((volatile WORD *)(uintptr_t)(base1 + UA_OFF_X)) = 11;
    *((volatile WORD *)(uintptr_t)(base1 + UA_OFF_Y)) = 10;
    *((volatile WORD *)(uintptr_t)(base0 + UA_OFF_TGT)) = (WORD)(uid1 & 0xFFFF);
    *((volatile WORD *)(uintptr_t)(base1 + UA_OFF_TGT)) = (WORD)(uid0 & 0xFFFF);
    *((volatile WORD *)(uintptr_t)(base0 + UA_OFF_CMD)) = 4; /* move-to-attack */
    *((volatile WORD *)(uintptr_t)(base1 + UA_OFF_CMD)) = 4;

    {
        char detail[224];
        wsprintfA(detail,
                  "slot0=%d uid0=%u ut0=2 @(10,10) | slot1=%d uid1=%u ut1=3 @(11,10) cmd=4 neutralized_owner1=%d (scenario-spawned; no retype%s)",
                  slot0, (unsigned)uid0, slot1, (unsigned)uid1,
                  neutralized, isolated ? "; isolated" : "");
        control_log_event(req->request_id, "cs1_placed", req->goal,
                          state_before, state_before, bridge, detail);
        lstrcpynA(res->fallback_chain, detail, sizeof(res->fallback_chain));
    }

    res->ok = TRUE;
    res->state_reached = res->end_state = state_before;
    set_reason(res, "", "cs1_placed_ok");
    res->elapsed_ms = GetTickCount() - t0;
}

static void run_combat_melee_adjacent(const control_request_t *req,
                                      control_result_t *res)
{
    DWORD state_before = 0xFFFFFFFFu;
    DWORD t0 = GetTickCount();

    csb_read_state(&state_before);
    res->start_state = state_before;
    lstrcpyA(res->bridge_used, "combat_adjacent");

    if (state_before != 3) {
        char reason[48];
        wsprintfA(reason, "not_in_ingame_ps=%u", (unsigned)state_before);
        control_log_event(req->request_id, "cma_abort", req->goal,
                          state_before, 0xFFFFFFFF, "combat_melee_adjacent",
                          reason);
        set_reason(res, CP_REASON_AXIS_LOGIC, reason);
        res->end_state = res->state_reached = state_before;
        res->elapsed_ms = GetTickCount() - t0;
        return;
    }

    int slot0 = find_any_owned_unit(0);
    int slot1 = find_any_owned_unit(1);
    if (slot0 < 0 || slot1 < 0) {
        char detail[64];
        wsprintfA(detail, "slot0=%d slot1=%d", slot0, slot1);
        control_log_event(req->request_id, "cma_no_combat_units", req->goal,
                          state_before, state_before, "combat_melee_adjacent",
                          detail);
        set_reason(res, CP_REASON_AXIS_LOGIC, "no_combat_units");
        res->end_state = res->state_reached = state_before;
        res->elapsed_ms = GetTickCount() - t0;
        return;
    }

    DWORD base0 = UA_ARRAY_VA + (DWORD)slot0 * UA_STRIDE;
    DWORD base1 = UA_ARRAY_VA + (DWORD)slot1 * UA_STRIDE;

    /* unit_id (used as target) */
    DWORD uid0 = *((volatile DWORD *)(uintptr_t)(base0 + UA_OFF_UID));
    DWORD uid1 = *((volatile DWORD *)(uintptr_t)(base1 + UA_OFF_UID));
    BYTE  ut0_before = *((volatile BYTE *)(uintptr_t)(base0 + UA_OFF_TYPE));
    BYTE  ut1_before = *((volatile BYTE *)(uintptr_t)(base1 + UA_OFF_TYPE));

    /* NOTE: 시도 #1에서 unit_type 재기입 (+0x08D = 2/3 melee) 직후 sprite
     * blit 경로 FUN_00466540 (RLE blit) 에서 page-fault on read NULL
     * @ 0x0046657F 가 발생해 wine 자체가 즉시 디버거를 띄우고 inferior가
     * exit code 05 로 종료된다. 이는 unit 슬롯에 보관된 sprite_loaded
     * 캐시가 원래 unit_type (7/31) 용으로 잡혀 있고, type 2/3 sprite가
     * 로드되지 않은 상태로 그리기 함수가 즉시 진입하기 때문이다.
     * 결과: post-spawn retype 은 sprite 경로 invariant 를 깨고 즉시 SEGV.
     *
     * 본 sub-goal 은 따라서 position+target 만 기입하고 unit_type 은
     * 유지한다. race-AI free_battle 시나리오의 spawn 유닛은 ATK=0 building/
     * builder뿐이므로 (1200/3268 tick 캡처 모두 동일하게 검증) 본 사후-배치
     * 만으로는 데미지가 발생하지 않는다. 이 사실 자체가 NOW-0701 step-2
     * 두 번째 블로커 (post-spawn retype unsafe) 를 캡처-증거로 확정한다. */

    /* Place adjacent: (10,10) / (11,10) — middle of the 100x100 map. */
    *((volatile WORD *)(uintptr_t)(base0 + UA_OFF_X)) = 10;
    *((volatile WORD *)(uintptr_t)(base0 + UA_OFF_Y)) = 10;
    *((volatile WORD *)(uintptr_t)(base1 + UA_OFF_X)) = 11;
    *((volatile WORD *)(uintptr_t)(base1 + UA_OFF_Y)) = 10;

    /* target each other + move-to-attack command. */
    *((volatile WORD *)(uintptr_t)(base0 + UA_OFF_TGT)) = (WORD)(uid1 & 0xFFFF);
    *((volatile WORD *)(uintptr_t)(base1 + UA_OFF_TGT)) = (WORD)(uid0 & 0xFFFF);
    *((volatile WORD *)(uintptr_t)(base0 + UA_OFF_CMD)) = 4; /* move-to-attack */
    *((volatile WORD *)(uintptr_t)(base1 + UA_OFF_CMD)) = 4;

    {
        char detail[224];
        wsprintfA(detail,
                  "slot0=%d uid0=%u ut0=%u @(10,10) | slot1=%d uid1=%u ut1=%u @(11,10) cmd=4 (position-only; retype unsafe)",
                  slot0, (unsigned)uid0, (unsigned)ut0_before,
                  slot1, (unsigned)uid1, (unsigned)ut1_before);
        control_log_event(req->request_id, "cma_placed", req->goal,
                          state_before, state_before,
                          "combat_melee_adjacent", detail);
        lstrcpynA(res->fallback_chain, detail, sizeof(res->fallback_chain));
    }

    res->ok = TRUE;
    res->state_reached = res->end_state = state_before;
    set_reason(res, "", "cma_placed_ok");
    res->elapsed_ms = GetTickCount() - t0;
}

/* G4 diagnostic only: reinforce one original AI-selected waypoint per AI
 * owner.  The worker only queues this no-argument callback; all game memory
 * reads and the cdecl issuer call happen on the _imeGetTime/main-loop thread.
 * Do not turn this into a persistent tick hook: the static payload/latch is
 * deliberately one-shot so a timed-out worker can never leave stack pointers
 * for a later callback. */
#define G4_PLAYER_BASE_VA       0x00956770u
#define G4_PLAYER_STRIDE        0x3ABCu
#define G4_PLAYER_COUNT         8
#define G4_MAP_WIDTH_VA         0x00B3DE34u
#define G4_MAP_HEIGHT_VA        0x00B3DE36u
#define G4_GLOBAL_TICK_VA       0x008924B8u
#define G4_GROUP_COUNT_OFF      0x348Au
#define G4_GROUP_RECORD_OFF     0x3490u
#define G4_GROUP_STRIDE         0x2E0u
#define G4_ROUTE_COUNT_OFF      0xCBAu
#define G4_ROUTE_MEMBERS_OFF    0x99Au
#define G4_ROUTE_COUNT           10
#define G4_ROUTE_MEMBER_LIMIT    20
#define G4_SOURCE_PENDING_OFF   0x384u
#define G4_SOURCE_PENDING_XY_OFF 0x388u
#define G4_SOURCE_COMMAND_OFF   0x290u

static BOOL is_g4_waypoint_probe_goal(const char *goal)
{
    return lstrcmpA(goal, "_g4_idle_waypoint_reinforcement_probe") == 0;
}

/* FUN_004AEDE0 — pinned original void cdecl movement issuer. */
typedef void (__attribute__((cdecl)) *g4_waypoint_issue_fn)(
    DWORD source_full_id, DWORD target_x, DWORD target_y, DWORD mode);

/* Existing G4 mobile/combat discriminator; keep the waypoint probe on the
 * same approved type table as the idle-order probe below. */
static BOOL g4_mobile_combat_type(BYTE type);

static BOOL g4_waypoint_issuer_signature_ok(void)
{
    static const BYTE expected[] = {
        0x8B, 0x44, 0x24, 0x10, 0x8B, 0x0D, 0x78, 0x5C,
        0x9E, 0x00, 0x8B, 0x54, 0x24, 0x0C, 0x6A, 0x00,
    };
    const volatile BYTE *actual = (const volatile BYTE *)(uintptr_t)0x004AEDE0u;
    DWORD i;
    if (IsBadReadPtr((const void *)actual, sizeof(expected))) return FALSE;
    for (i = 0; i < sizeof(expected); ++i) {
        if (actual[i] != expected[i]) return FALSE;
    }
    return TRUE;
}

static BOOL g4_waypoint_in_map(SHORT x, SHORT y, SHORT width, SHORT height)
{
    /* World tiles are zero based; dimensions themselves are separately
     * bounded to the observed 1..180 range before this helper is used. */
    return x >= 0 && y >= 0 && x < width && y < height;
}

static BOOL g4_waypoint_member_contains(DWORD player, DWORD source_full_id)
{
    int route, member;
    for (route = 0; route < G4_ROUTE_COUNT; ++route) {
        DWORD members = player + G4_ROUTE_MEMBERS_OFF +
                        (DWORD)route * G4_ROUTE_MEMBER_LIMIT * sizeof(DWORD);
        for (member = 0; member < G4_ROUTE_MEMBER_LIMIT; ++member) {
            DWORD id = *((volatile DWORD *)(uintptr_t)(members +
                                 (DWORD)member * sizeof(DWORD)));
            if (id == source_full_id) return TRUE;
        }
    }
    return FALSE;
}

static BOOL g4_waypoint_group_has_live_member(DWORD player, BYTE owner,
                                              int route)
{
    int member, slot;
    DWORD members = player + G4_ROUTE_MEMBERS_OFF +
                    (DWORD)route * G4_ROUTE_MEMBER_LIMIT * sizeof(DWORD);
    for (member = 0; member < G4_ROUTE_MEMBER_LIMIT; ++member) {
        DWORD wanted = *((volatile DWORD *)(uintptr_t)(members +
                                     (DWORD)member * sizeof(DWORD)));
        if (wanted == 0) continue;
        for (slot = 1; slot < UA_COUNT; ++slot) {
            SHORT exists = *((volatile SHORT *)(uintptr_t)(UA_EXISTS_VA +
                                      (DWORD)slot * sizeof(SHORT)));
            DWORD base;
            if (exists == 0) continue;
            base = UA_ARRAY_VA + (DWORD)slot * UA_STRIDE;
            if (*((volatile BYTE *)(uintptr_t)(base + UA_OFF_OWNER)) != owner ||
                *((volatile DWORD *)(uintptr_t)(base + UA_OFF_HP)) == 0) continue;
            if (*((volatile DWORD *)(uintptr_t)(base + UA_OFF_UID)) == wanted)
                return TRUE;
        }
    }
    return FALSE;
}

static void g4_waypoint_json_append(char *json, int *pos, int cap,
                                    const char *text)
{
    int p = *pos;
    if (p < 0) p = 0;
    if (p >= cap) {
        *pos = cap;
        return;
    }
    while (text && *text && p < cap - 1) json[p++] = *text++;
    json[p] = '\0';
    *pos = p;
}

static void g4_waypoint_json_record(char *json, int *pos, int cap,
                                    int owner, DWORD tick, DWORD source_id,
                                    int source_slot, int group, SHORT x,
                                    SHORT y, DWORD pending_before,
                                    DWORD pending_after, DWORD after_pending_xy,
                                    DWORD expected_xy, BOOL admitted,
                                    const char *skip_reason)
{
    char line[512];
    wsprintfA(line,
              "%s{\"owner\":%d,\"tick\":%lu,\"source_full_id\":%lu,"
              "\"slot\":%d,\"group\":%d,\"target\":[%d,%d],"
              "\"before_pending\":%lu,\"after_pending\":%lu,"
              "\"after_pending_xy\":\"0x%08lX\","
              "\"expected_xy\":\"0x%08lX\","
              "\"admitted\":%s,\"skip_reason\":\"",
              *pos > 0 && json[*pos - 1] != '[' ? "," : "", owner,
              (unsigned long)tick, (unsigned long)source_id, source_slot,
              group, (int)x, (int)y, (unsigned long)pending_before,
              (unsigned long)pending_after, (unsigned long)after_pending_xy,
              (unsigned long)expected_xy, admitted ? "true" : "false");
    g4_waypoint_json_append(json, pos, cap, line);
    g4_waypoint_json_append(json, pos, cap, skip_reason);
    g4_waypoint_json_append(json, pos, cap, "\"}");
}

static void g4_waypoint_execute(const control_request_t *req,
                                control_result_t *res)
{
    static char g4_waypoint_json[8192];
    DWORD tick = 0;
    DWORD started = GetTickCount();
    DWORD state_before = 0xFFFFFFFFu;
    SHORT map_width = 0, map_height = 0;
    int json_pos = 0, calls = 0, admitted_count = 0, owner;
    BOOL artifact_ok = FALSE;
    g4_waypoint_json[0] = '\0';
    g4_waypoint_json_append(g4_waypoint_json, &json_pos,
                            sizeof(g4_waypoint_json),
                            "{\"schema_version\":1,\"goal\":\"waypoint_reinforcement\",\"owners\":[");

    csb_read_state(&state_before);
    res->state_reached = res->end_state = res->start_state = state_before;
    lstrcpynA(res->bridge_used, "g4_waypoint", sizeof(res->bridge_used));
    if (state_before != 3) {
        set_reason(res, CP_REASON_AXIS_LOGIC, "requires_ingame_ps3");
        g4_waypoint_json_append(g4_waypoint_json, &json_pos,
                                sizeof(g4_waypoint_json),
                                "],\"tick\":0,\"status\":\"requires_ingame_ps3\"}");
        goto write_json;
    }
    tick = *((volatile DWORD *)(uintptr_t)G4_GLOBAL_TICK_VA);
    map_width = *((volatile SHORT *)(uintptr_t)G4_MAP_WIDTH_VA);
    map_height = *((volatile SHORT *)(uintptr_t)G4_MAP_HEIGHT_VA);
    if (!g4_waypoint_issuer_signature_ok()) {
        set_reason(res, CP_REASON_AXIS_ENV, "waypoint_issuer_signature_mismatch");
        g4_waypoint_json_append(g4_waypoint_json, &json_pos,
                                sizeof(g4_waypoint_json),
                                "],\"tick\":0,\"status\":\"issuer_signature_mismatch\"}");
        goto write_json;
    }
    if (map_width < 1 || map_width > 180 || map_height < 1 || map_height > 180) {
        set_reason(res, CP_REASON_AXIS_ENV, "unsupported_map_bounds");
        g4_waypoint_json_append(g4_waypoint_json, &json_pos,
                                sizeof(g4_waypoint_json),
                                "],\"tick\":0,\"status\":\"unsupported_map_bounds\"}");
        goto write_json;
    }

    for (owner = 0; owner < G4_PLAYER_COUNT; ++owner) {
        DWORD player = G4_PLAYER_BASE_VA + (DWORD)owner * G4_PLAYER_STRIDE;
        BYTE nation = *((volatile BYTE *)(uintptr_t)(player + 0));
        BYTE ai = *((volatile BYTE *)(uintptr_t)(player + 2));
        DWORD source_id = 0;
        DWORD pending_before = 0, pending_after = 0;
        DWORD after_pending_xy = 0, expected_xy = 0;
        SHORT target_x = -1, target_y = -1;
        int source_slot = -1, chosen_group = -1;
        const char *skip = "";
        BOOL did_admit = FALSE;

        if (nation == 0 || nation == 6) skip = "inactive_or_observer_nation";
        else if (ai != 1) skip = "human_owner";
        else {
            SHORT group_count = *((volatile SHORT *)(uintptr_t)(player + G4_GROUP_COUNT_OFF));
            int group;
            if (group_count < 0 || group_count > 2) skip = "unsupported_group_count";
            else {
                for (group = 0; group < group_count && chosen_group < 0; ++group) {
                    DWORD record = player + G4_GROUP_RECORD_OFF +
                                   (DWORD)group * G4_GROUP_STRIDE;
                    SHORT gx = *((volatile SHORT *)(uintptr_t)(record + 0));
                    SHORT gy = *((volatile SHORT *)(uintptr_t)(record + 2));
                    SHORT gr = *((volatile SHORT *)(uintptr_t)(record + 4));
                    SHORT gs = *((volatile SHORT *)(uintptr_t)(record + 6));
                    SHORT members = gr >= 0 && gr < G4_ROUTE_COUNT
                        ? *((volatile SHORT *)(uintptr_t)(player + G4_ROUTE_COUNT_OFF +
                                                          (DWORD)gr * sizeof(SHORT))) : 0;
                    if (gr < 0 || gr >= G4_ROUTE_COUNT || gs != 1 ||
                        members < 1 || members > G4_ROUTE_MEMBER_LIMIT ||
                        !g4_waypoint_in_map(gx, gy, map_width, map_height) ||
                        !g4_waypoint_group_has_live_member(player, (BYTE)owner, gr))
                        continue;
                    chosen_group = group;
                    target_x = gx;
                    target_y = gy;
                }
                if (chosen_group < 0) skip = "no_valid_ai_group_waypoint";
                else {
                    int slot;
                    for (slot = 1; slot < UA_COUNT; ++slot) {
                        SHORT exists = *((volatile SHORT *)(uintptr_t)(UA_EXISTS_VA +
                                                  (DWORD)slot * sizeof(SHORT)));
                        DWORD base;
                        BYTE type;
                        DWORD hp;
                        SHORT command;
                        SHORT pending_word;
                        SHORT sx, sy;
                        DWORD dx, dy;
                        if (exists == 0) continue;
                        base = UA_ARRAY_VA + (DWORD)slot * UA_STRIDE;
                        if (*((volatile BYTE *)(uintptr_t)(base + UA_OFF_OWNER)) != (BYTE)owner)
                            continue;
                        hp = *((volatile DWORD *)(uintptr_t)(base + UA_OFF_HP));
                        if (hp == 0) continue;
                        DWORD candidate_id = *((volatile DWORD *)(uintptr_t)(base + UA_OFF_UID));
                        if ((candidate_id & 0xFFFFu) != (DWORD)slot ||
                            g4_waypoint_member_contains(player, candidate_id)) continue;
                        type = *((volatile BYTE *)(uintptr_t)(base + UA_OFF_TYPE));
                        command = *((volatile SHORT *)(uintptr_t)(base + UA_OFF_CMD));
                        pending_word = *((volatile SHORT *)(uintptr_t)(base + G4_SOURCE_PENDING_OFF));
                        if (!g4_mobile_combat_type(type) || command != 1 || pending_word != 1)
                            continue;
                        sx = *((volatile SHORT *)(uintptr_t)(base + UA_OFF_X));
                        sy = *((volatile SHORT *)(uintptr_t)(base + UA_OFF_Y));
                        dx = sx > target_x ? (DWORD)(sx - target_x) : (DWORD)(target_x - sx);
                        dy = sy > target_y ? (DWORD)(sy - target_y) : (DWORD)(target_y - sy);
                        if ((dx > dy ? dx : dy) <= 5) continue;
                        source_id = candidate_id;
                        source_slot = slot;
                        pending_before = *((volatile DWORD *)(uintptr_t)(base + G4_SOURCE_PENDING_OFF));
                        /* Identity/owner/live/pending are revalidated immediately before call. */
                        if (*((volatile SHORT *)(uintptr_t)(UA_EXISTS_VA +
                                              (DWORD)source_slot * sizeof(SHORT))) == 0 ||
                            *((volatile DWORD *)(uintptr_t)(base + UA_OFF_UID)) != source_id ||
                            *((volatile BYTE *)(uintptr_t)(base + UA_OFF_OWNER)) != (BYTE)owner ||
                            *((volatile DWORD *)(uintptr_t)(base + UA_OFF_HP)) == 0 ||
                            *((volatile SHORT *)(uintptr_t)(base + G4_SOURCE_PENDING_OFF)) != 1) {
                            skip = "source_revalidation_failed";
                            break;
                        }
                        ((g4_waypoint_issue_fn)(uintptr_t)0x004AEDE0u)(
                            source_id, (DWORD)(USHORT)target_x,
                            (DWORD)(USHORT)target_y, 1u);
                        pending_after = *((volatile DWORD *)(uintptr_t)(base + G4_SOURCE_PENDING_OFF));
                        {
                            after_pending_xy = *((volatile DWORD *)(uintptr_t)(base + G4_SOURCE_PENDING_XY_OFF));
                            expected_xy = ((DWORD)(USHORT)target_y << 16) |
                                          (DWORD)(USHORT)target_x;
                            did_admit = pending_after == 0x00010003u &&
                                        after_pending_xy == expected_xy;
                        }
                        calls++;
                        admitted_count += did_admit ? 1 : 0;
                        skip = did_admit ? "" : "pending_admission_failed";
                        break; /* no alternate source/retry after one selection */
                    }
                    if (source_slot < 0 && skip[0] == '\0') skip = "no_eligible_source";
                }
            }
        }
        g4_waypoint_json_record(g4_waypoint_json, &json_pos,
                                sizeof(g4_waypoint_json), owner, tick, source_id,
                                source_slot, chosen_group, target_x, target_y,
                                pending_before, pending_after, after_pending_xy,
                                expected_xy, did_admit, skip);
    }
    g4_waypoint_json_append(g4_waypoint_json, &json_pos,
                            sizeof(g4_waypoint_json), "],\"tick\":");
    {
        char tick_text[24];
        wsprintfA(tick_text, "%lu", (unsigned long)tick);
        g4_waypoint_json_append(g4_waypoint_json, &json_pos,
                                sizeof(g4_waypoint_json), tick_text);
    }
    g4_waypoint_json_append(g4_waypoint_json, &json_pos,
                            sizeof(g4_waypoint_json), "}");

write_json:
    {
        HANDLE hf = CreateFileA("C:\\inmm_g4_waypoint_probe.json",
                                GENERIC_WRITE, 0, NULL, CREATE_ALWAYS,
                                FILE_ATTRIBUTE_NORMAL, NULL);
        if (hf != INVALID_HANDLE_VALUE) {
            DWORD written = 0;
            artifact_ok = WriteFile(hf, g4_waypoint_json, (DWORD)json_pos,
                                    &written, NULL) && written == (DWORD)json_pos;
            CloseHandle(hf);
        }
    }
    res->fallback_count = (DWORD)calls;
    res->ok = artifact_ok && admitted_count > 0;
    {
        char summary[96];
        wsprintfA(summary, "calls=%d admitted=%d artifact=waypoint_json",
                  calls, admitted_count);
        lstrcpynA(res->fallback_chain, summary, sizeof(res->fallback_chain));
    }
    if (!artifact_ok)
        set_reason(res, CP_REASON_AXIS_ENV, "waypoint_json_write_failed");
    else if (admitted_count > 0)
        set_reason(res, "", "waypoint_order_admitted");
    else if (calls > 0)
        set_reason(res, CP_REASON_AXIS_LOGIC, "waypoint_order_not_admitted");
    else if (res->reason[0] == '\0')
        set_reason(res, CP_REASON_AXIS_LOGIC, "waypoint_no_eligible_source");
    res->elapsed_ms = GetTickCount() - started;
    control_log_event(req->request_id, "g4_waypoint_probe", req->goal,
                      res->start_state, res->end_state, res->bridge_used,
                      res->fallback_chain);
}

static volatile LONG s_g4_waypoint_once = 0;
static control_request_t s_g4_waypoint_req;
static control_result_t s_g4_waypoint_res;

static void WINAPI g4_waypoint_mainthread(void)
{
    g4_waypoint_execute(&s_g4_waypoint_req, &s_g4_waypoint_res);
}

static void run_g4_waypoint_probe(const control_request_t *req,
                                  control_result_t *res)
{
    DWORD i;
    DWORD started = GetTickCount();
    BYTE *dst;
    const BYTE *src;
    if (InterlockedCompareExchange(&s_g4_waypoint_once, 1, 0) != 0) {
        set_reason(res, CP_REASON_AXIS_LOGIC, "one_shot_already_used");
        return;
    }
    dst = (BYTE *)&s_g4_waypoint_req;
    src = (const BYTE *)req;
    for (i = 0; i < sizeof(s_g4_waypoint_req); ++i) dst[i] = src[i];
    dst = (BYTE *)&s_g4_waypoint_res;
    src = (const BYTE *)res;
    for (i = 0; i < sizeof(s_g4_waypoint_res); ++i) dst[i] = src[i];
    if (!chb_call_handler(req->request_id, "g4_waypoint_probe",
                          (DWORD)(uintptr_t)g4_waypoint_mainthread, 1000u)) {
        set_reason(res, CP_REASON_AXIS_ENV, "mainthread_waypoint_timeout");
        res->elapsed_ms = GetTickCount() - started;
        return;
    }
    dst = (BYTE *)res;
    src = (const BYTE *)&s_g4_waypoint_res;
    for (i = 0; i < sizeof(s_g4_waypoint_res); ++i) dst[i] = src[i];
    res->elapsed_ms = GetTickCount() - started;
}

/* G4 diagnostic only: submit one target order through the original high-level
 * issuer FUN_00415480.  This does not spawn/retype units or alter pathfinding;
 * it tests whether the observed stationary population admits and consumes an
 * original pending order. */
static BOOL is_g4_idle_attack_probe_goal(const char *goal)
{
    return lstrcmpA(goal, "_g4_issue_idle_attack_probe") == 0;
}

static BOOL g4_mobile_combat_type(BYTE type)
{
    DWORD row = 0x009B5228u + (DWORD)type * 0x394u;
    DWORD flags = *((volatile DWORD *)(uintptr_t)(row + 0x4Cu));
    SHORT attack_kind = *((volatile SHORT *)(uintptr_t)(row + 0x5Cu));
    return (flags & 1u) != 0 && attack_kind > 0;
}

typedef int (__attribute__((thiscall)) *g4_issue_target_fn)(
    void *unit, DWORD target_x, DWORD target_y, DWORD target_id);

static BOOL g4_issue_target_signature_ok(void)
{
    static const BYTE expected[] = {
        0x53, 0x56, 0x8B, 0xF1, 0x57, 0x8A,
        0x86, 0x1C, 0x03, 0x00, 0x00, 0x84,
    };
    const volatile BYTE *actual = (const volatile BYTE *)(uintptr_t)0x00415480u;
    DWORD i;
    if (IsBadReadPtr((const void *)actual, sizeof(expected))) return FALSE;
    for (i = 0; i < sizeof(expected); ++i) {
        if (actual[i] != expected[i]) return FALSE;
    }
    return TRUE;
}

static int g4_nearest_enemy_slot(WORD x, WORD y)
{
    int i;
    int best = -1;
    DWORD best_distance = 0xFFFFFFFFu;
    for (i = 0; i < UA_COUNT; ++i) {
        SHORT ex = *((volatile SHORT *)(uintptr_t)(UA_EXISTS_VA + (DWORD)i * 2));
        DWORD base;
        BYTE owner;
        DWORD hp;
        WORD enemy_x, enemy_y;
        DWORD dx, dy, distance;
        if (ex == 0) continue;
        base = UA_ARRAY_VA + (DWORD)i * UA_STRIDE;
        owner = *((volatile BYTE *)(uintptr_t)(base + UA_OFF_OWNER));
        hp = *((volatile DWORD *)(uintptr_t)(base + UA_OFF_HP));
        if (owner != 1 || hp == 0) continue;
        enemy_x = *((volatile WORD *)(uintptr_t)(base + UA_OFF_X));
        enemy_y = *((volatile WORD *)(uintptr_t)(base + UA_OFF_Y));
        dx = enemy_x > x ? enemy_x - x : x - enemy_x;
        dy = enemy_y > y ? enemy_y - y : y - enemy_y;
        distance = dx > dy ? dx : dy;
        if (distance < best_distance) {
            best = i;
            best_distance = distance;
        }
    }
    return best;
}

static void g4_idle_attack_execute(const control_request_t *req,
                                  control_result_t *res)
{
    DWORD state_before = 0xFFFFFFFFu;
    DWORD t0 = GetTickCount();
    int i;
    int issued = 0;
    csb_read_state(&state_before);
    res->start_state = res->end_state = res->state_reached = state_before;
    lstrcpynA(res->bridge_used, "g4_order_probe", sizeof(res->bridge_used));
    if (state_before != 3) {
        set_reason(res, CP_REASON_AXIS_LOGIC, "requires_ingame_ps3");
        return;
    }
    if (!g4_issue_target_signature_ok()) {
        set_reason(res, CP_REASON_AXIS_ENV, "issuer_signature_mismatch");
        return;
    }
    for (i = 0; i < UA_COUNT && issued < 1; ++i) {
        SHORT ex = *((volatile SHORT *)(uintptr_t)(UA_EXISTS_VA + (DWORD)i * 2));
        DWORD base;
        BYTE owner, type;
        DWORD hp, target_base, target_uid;
        DWORD pending_before, pending_after;
        DWORD pending_xy, pending_target;
        WORD command, x, y;
        WORD target_x, target_y;
        int admitted;
        int target_slot;
        if (ex == 0) continue;
        base = UA_ARRAY_VA + (DWORD)i * UA_STRIDE;
        owner = *((volatile BYTE *)(uintptr_t)(base + UA_OFF_OWNER));
        type = *((volatile BYTE *)(uintptr_t)(base + UA_OFF_TYPE));
        hp = *((volatile DWORD *)(uintptr_t)(base + UA_OFF_HP));
        command = *((volatile WORD *)(uintptr_t)(base + UA_OFF_CMD));
        if (owner != 0 || hp == 0 || command != 1 || !g4_mobile_combat_type(type)) continue;
        x = *((volatile WORD *)(uintptr_t)(base + UA_OFF_X));
        y = *((volatile WORD *)(uintptr_t)(base + UA_OFF_Y));
        target_slot = g4_nearest_enemy_slot(x, y);
        if (target_slot < 0) continue;
        target_base = UA_ARRAY_VA + (DWORD)target_slot * UA_STRIDE;
        target_uid = *((volatile DWORD *)(uintptr_t)(target_base + UA_OFF_UID));
        target_x = *((volatile WORD *)(uintptr_t)(target_base + UA_OFF_X));
        target_y = *((volatile WORD *)(uintptr_t)(target_base + UA_OFF_Y));
        pending_before = *((volatile DWORD *)(uintptr_t)(base + 0x384u));
        admitted = ((g4_issue_target_fn)(uintptr_t)0x00415480u)(
            (void *)(uintptr_t)base, (DWORD)target_x, (DWORD)target_y, target_uid);
        pending_after = *((volatile DWORD *)(uintptr_t)(base + 0x384u));
        pending_xy = *((volatile DWORD *)(uintptr_t)(base + 0x388u));
        pending_target = *((volatile DWORD *)(uintptr_t)(base + 0x38Cu));
        {
            char detail[160];
            wsprintfA(detail,
                      "slot=%d target=%d ret=%d cmd=%u pending=%08lX>%08lX xy=%08lX tgt=%08lX",
                      i, target_slot, admitted, (unsigned)command,
                      (unsigned long)pending_before, (unsigned long)pending_after,
                      (unsigned long)pending_xy, (unsigned long)pending_target);
            lstrcpynA(res->fallback_chain, detail, sizeof(res->fallback_chain));
        }
        if (admitted == 1) issued = 1;
    }
    res->fallback_count = (DWORD)issued;
    res->ok = issued > 0;
    set_reason(res, issued > 0 ? "" : CP_REASON_AXIS_LOGIC,
               issued > 0 ? "original_target_order_admitted" : "target_order_not_admitted");
    res->elapsed_ms = GetTickCount() - t0;
    control_log_event(req->request_id, "g4_idle_attack_probe", req->goal,
                      state_before, state_before, "g4_idle_attack_probe",
                      res->fallback_chain);
}

/* One-shot static payload: a timed-out callback never retains worker stack
 * pointers, and a second request cannot overwrite a still-running payload. */
static volatile LONG s_g4_order_once = 0;
static control_request_t s_g4_order_req;
static control_result_t s_g4_order_res;

static void WINAPI g4_idle_attack_mainthread(void)
{
    g4_idle_attack_execute(&s_g4_order_req, &s_g4_order_res);
}

static void run_g4_idle_attack_probe(const control_request_t *req,
                                    control_result_t *res)
{
    DWORD i;
    DWORD started = GetTickCount();
    BYTE *dst;
    const BYTE *src;
    if (InterlockedCompareExchange(&s_g4_order_once, 1, 0) != 0) {
        set_reason(res, CP_REASON_AXIS_LOGIC, "one_shot_already_used");
        return;
    }
    dst = (BYTE *)&s_g4_order_req;
    src = (const BYTE *)req;
    for (i = 0; i < sizeof(s_g4_order_req); ++i) dst[i] = src[i];
    dst = (BYTE *)&s_g4_order_res;
    src = (const BYTE *)res;
    for (i = 0; i < sizeof(s_g4_order_res); ++i) dst[i] = src[i];
    if (!chb_call_handler(req->request_id, "g4_order_probe",
                          (DWORD)(uintptr_t)g4_idle_attack_mainthread, 1000u)) {
        set_reason(res, CP_REASON_AXIS_ENV, "mainthread_order_timeout");
        res->elapsed_ms = GetTickCount() - started;
        return;
    }
    dst = (BYTE *)res;
    src = (const BYTE *)&s_g4_order_res;
    for (i = 0; i < sizeof(s_g4_order_res); ++i) dst[i] = src[i];
    res->elapsed_ms = GetTickCount() - started;
}

/* ------------------------------------------------------------------ */
/* B6 test path — "_test_handler_slot" goal 전용                       */
/* ------------------------------------------------------------------ */
static BOOL is_test_handler_goal(const char *goal)
{
    return (lstrcmpA(goal, "_test_handler_slot") == 0);
}

static void run_test_handler_slot(const control_request_t *req,
                                  control_result_t *res)
{
    DWORD state_before = 0xFFFFFFFFu;
    BOOL  ok_normal, ok_timeout;
    DWORD t0 = GetTickCount();

    csb_read_state(&state_before);
    res->start_state = state_before;

    ok_normal = chb_call_handler(req->request_id, "test_ok",
                                 0, CHB_DEFAULT_TIMEOUT_MS);
    fc_append(res, "handler");

    ok_timeout = chb_call_handler(req->request_id, "_skip_expire",
                                  0, 100);
    fc_append(res, "handler_skip");

    if (!ok_timeout && state_before != 0xFFFFFFFFu) {
        control_log_event(req->request_id, "rollback_attempt", req->goal,
                          0xFFFFFFFF, state_before, "state",
                          "handler skip → state revert");
        res->rollback_attempted = TRUE;
        BOOL wr = csb_write_state(state_before);
        res->rollback_ok = wr;
        control_log_event(req->request_id,
                          wr ? "rollback_success" : "rollback_failed",
                          req->goal, 0xFFFFFFFF, state_before, "state", "");
    }

    res->ok            = ok_normal;
    res->state_reached = state_before;
    res->end_state     = state_before;
    lstrcpyA(res->bridge_used, "handler");
    if (ok_normal) {
        set_reason(res, "", "handler_slot_ok");
    } else {
        set_reason(res, CP_REASON_AXIS_LOGIC, "handler_slot_failed");
    }
    res->elapsed_ms = GetTickCount() - t0;
    (void)ok_timeout;
}

/* ------------------------------------------------------------------ */
/* state bridge 진행 (성공=TRUE, 실패=FALSE)                            */
/* ------------------------------------------------------------------ */
static BOOL try_state_bridge(const control_request_t *req,
                             const goal_entry_t *entry,
                             control_result_t *res,
                             DWORD effective_timeout,
                             DWORD *final_state)
{
    control_log_event(req->request_id, "state_write_attempt", req->goal,
                      res->start_state, entry->preprocess_state, "state", "");
    csb_write_state(entry->preprocess_state);

    fc_append(res, "state");
    lstrcpyA(res->bridge_used, "state");

    if (csb_wait_steady(entry->steady_state, effective_timeout, final_state)) {
        control_log_event(req->request_id, "state_wait_success", req->goal,
                          entry->preprocess_state, *final_state, "state", "");
        return TRUE;
    }
    control_log_event(req->request_id, "state_wait_timeout", req->goal,
                      entry->preprocess_state, *final_state, "state", "");
    return FALSE;
}

/* ------------------------------------------------------------------ */
/* input bridge 진행 (성공 판정은 후속 state 대기로 확인)              */
/* ------------------------------------------------------------------ */
static void try_input_bridge(const control_request_t *req,
                             const goal_entry_t *entry,
                             control_result_t *res)
{
    control_log_event(req->request_id, "fallback_to_input_bridge", req->goal,
                      0xFFFFFFFF, 0xFFFFFFFF, "input_A", "");

    if (entry->window_active_required && !cib_window_active()) {
        control_log_event(req->request_id, "bridge_downgrade", req->goal,
                          0xFFFFFFFF, 0xFFFFFFFF, "input_A",
                          "[0x66976C]==0 window-active false");
        lstrcpyA(res->bridge_downgraded_from, "A");
        fc_append(res, "input_A_skipped");
        lstrcpyA(res->bridge_used, "input_B");
    } else {
        cib_action_confirm(req->request_id);
        fc_append(res, "input_A");
        lstrcpyA(res->bridge_used, "input_A");
    }
}

/* ------------------------------------------------------------------ */
/* handler bridge fallback (실 goal과 연결) — R6                        */
/* ------------------------------------------------------------------ */
static BOOL try_handler_bridge(const control_request_t *req,
                               const goal_entry_t *entry,
                               control_result_t *res,
                               DWORD effective_timeout,
                               DWORD *final_state)
{
    DWORD handler_timeout = (entry->handler_timeout_ms > 0)
                            ? entry->handler_timeout_ms
                            : CHB_DEFAULT_TIMEOUT_MS;

    control_log_event(req->request_id, "fallback_to_handler_bridge", req->goal,
                      0xFFFFFFFF, 0xFFFFFFFF, "handler", "");

    lstrcpyA(res->bridge_used, "handler"); /* 실패 경로에서도 유지 */

    /* 현재 registry에는 handler_va 직접 지정이 없으므로 no-op(0) 슬롯 호출.
     * slot drain이 되면 '핸들러 진입 가능 상태'임을 확인한다. drain 실패 시
     * revert 경로를 시도한다. */
    BOOL ok = chb_call_handler(req->request_id, req->goal, 0, handler_timeout);
    fc_append(res, "handler");

    if (ok) {
        if (csb_wait_steady(entry->steady_state, effective_timeout, final_state)) {
            return TRUE;
        }
    }

    /* 실패 — revert */
    control_log_event(req->request_id, "rollback_attempt", req->goal,
                      0xFFFFFFFF, res->start_state, "state",
                      "handler fallback failed → state revert");
    res->rollback_attempted = TRUE;
    BOOL wr = csb_write_state(res->start_state);
    res->rollback_ok = wr;
    control_log_event(req->request_id,
                      wr ? "rollback_success" : "rollback_failed",
                      req->goal, 0xFFFFFFFF, res->start_state, "state", "");
    return FALSE;
}

/* ------------------------------------------------------------------ */
/* Dx read_unit_state — 인게임 유닛 배열 덤프 (C:\inmm_unit_state.json) */
/* ------------------------------------------------------------------ */
static BOOL is_read_unit_state_goal(const char *goal)
{
    return (lstrcmpA(goal, "read_unit_state") == 0);
}

#define US_EXISTS_VA  0x008990C8u
#define US_ARRAY_VA   0x0066B790u
#define US_STRIDE     0x758u
#define US_COUNT      1200

static void run_read_unit_state(const control_request_t *req,
                                control_result_t *res)
{
    static char buf[131072];
    int pos = 0, i, count = 0;
    BOOL first = TRUE;

    pos += wsprintfA(buf + pos, "{\"units\":[");

    for (i = 0; i < US_COUNT; i++) {
        SHORT ex = *((volatile SHORT*)(uintptr_t)(US_EXISTS_VA + (DWORD)i * 2));
        if (ex == 0) continue;

        DWORD base  = US_ARRAY_VA + (DWORD)i * US_STRIDE;
        WORD  x     = *((volatile WORD *)(uintptr_t)(base + 0x2A2));
        WORD  y     = *((volatile WORD *)(uintptr_t)(base + 0x2A4));
        BYTE  utype = *((volatile BYTE *)(uintptr_t)(base + 0x08D));
        BYTE  own   = *((volatile BYTE *)(uintptr_t)(base + 0x08E));
        DWORD hp    = *((volatile DWORD*)(uintptr_t)(base + 0x0B4));
        WORD  kind  = *((volatile WORD *)(uintptr_t)(base + 0x290));

        if (!first) buf[pos++] = ',';
        first = FALSE;
        pos += wsprintfA(buf + pos,
            "{\"slot\":%d,\"utype\":%d,\"owner\":%d,\"hp\":%d,\"x\":%d,\"y\":%d,\"kind\":%d}",
            i, (int)utype, (int)own, (int)hp, (int)x, (int)y, (int)kind);
        count++;
        if (pos > 120000) break;
    }

    pos += wsprintfA(buf + pos, "],\"count\":%d}", count);

    HANDLE hf = CreateFileA("C:\\inmm_unit_state.json",
                            GENERIC_WRITE, 0, NULL,
                            CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (hf != INVALID_HANDLE_VALUE) {
        DWORD wr;
        WriteFile(hf, buf, (DWORD)pos, &wr, NULL);
        CloseHandle(hf);
        res->ok = TRUE;
        set_reason(res, "", "ok");
    } else {
        set_reason(res, CP_REASON_AXIS_ENV, "file_create_failed");
    }
    res->start_state = res->end_state = res->state_reached = 3;
}

/* ------------------------------------------------------------------ */
/* Dx raw_dump — 유닛 슬롯 기준 또는 절대 VA 기준 메모리 덤프           */
/*                                                                     */
/* 모드 A (unit_offset): 유닛 배열 슬롯의 base + offset 에서 size 바이트 */
/* 모드 B (absolute_va): 지정한 VA 에서 size 바이트 직접 덤프             */
/* ------------------------------------------------------------------ */
static BOOL is_raw_dump_goal(const char *goal)
{
    return (lstrcmpA(goal, "raw_dump") == 0);
}

/* 로컬 JSON 헬퍼 — raw_json 버퍼에서 문자열 값 추출 */
static int rd_find_str(const char *json, const char *key,
                       char *out, int maxout)
{
    char pat[80];
    int ki = 0;
    pat[ki++] = '"';
    {
        const char *k = key;
        while (*k && ki < 76) pat[ki++] = *k++;
    }
    pat[ki++] = '"';
    pat[ki++] = ':';
    pat[ki]   = '\0';

    int plen = ki;
    const char *p = json;
    while (*p) {
        int match = 1, i;
        for (i = 0; i < plen; i++) {
            if (p[i] == '\0' || p[i] != pat[i]) { match = 0; break; }
        }
        if (match) {
            const char *v = p + plen;
            while (*v == ' ' || *v == '\t') v++;
            if (*v != '"') { p++; continue; }
            v++;
            int n = 0;
            while (*v && *v != '"' && n < maxout - 1)
                out[n++] = *v++;
            out[n] = '\0';
            return 1;
        }
        p++;
    }
    return 0;
}

/* 로컬 JSON 헬퍼 — raw_json 버퍼에서 DWORD(unsigned int) 값 추출 */
static int rd_find_u32(const char *json, const char *key, DWORD *out)
{
    char pat[80];
    int ki = 0;
    pat[ki++] = '"';
    {
        const char *k = key;
        while (*k && ki < 76) pat[ki++] = *k++;
    }
    pat[ki++] = '"';
    pat[ki++] = ':';
    pat[ki]   = '\0';

    int plen = ki;
    const char *p = json;
    while (*p) {
        int match = 1, i;
        for (i = 0; i < plen; i++) {
            if (p[i] == '\0' || p[i] != pat[i]) { match = 0; break; }
        }
        if (match) {
            const char *v = p + plen;
            while (*v == ' ' || *v == '\t') v++;
            if (*v >= '0' && *v <= '9') {
                DWORD val = 0;
                while (*v >= '0' && *v <= '9') {
                    val = val * 10 + (DWORD)(*v - '0');
                    v++;
                }
                *out = val;
                return 1;
            }
            return 0;
        }
        p++;
    }
    return 0;
}

#define RD_MAX_SIZE    512u   /* 덤프 최대 크기 (바이트) */
#define RD_HEX_BUFSIZE 2048  /* "XX " * 512 + null */

static void run_raw_dump(const control_request_t *req,
                         control_result_t *res)
{
    const char *json = req->raw_json;
    char   mode[32];
    DWORD  size = 0;
    DWORD  target_va = 0;

    res->start_state = res->end_state = res->state_reached = 3;
    lstrcpyA(res->bridge_used, "raw_dump");

    /* mode 파싱 */
    if (!rd_find_str(json, "mode", mode, sizeof(mode))) {
        set_reason(res, CP_REASON_AXIS_LOGIC, "missing_mode");
        return;
    }

    /* size 파싱 + 범위 검사 */
    if (!rd_find_u32(json, "size", &size) || size == 0) {
        set_reason(res, CP_REASON_AXIS_LOGIC, "missing_size");
        return;
    }
    if (size > RD_MAX_SIZE) {
        set_reason(res, CP_REASON_AXIS_LOGIC, "out_of_bounds");
        return;
    }

    if (lstrcmpA(mode, "unit_offset") == 0) {
        /* 모드 A: 유닛 슬롯 기준 */
        DWORD unit_slot = 0xFFFFFFFFu;
        DWORD offset    = 0;

        if (!rd_find_u32(json, "unit_slot", &unit_slot)) {
            set_reason(res, CP_REASON_AXIS_LOGIC, "missing_unit_slot");
            return;
        }
        rd_find_u32(json, "offset", &offset); /* 0이면 base 그대로 */

        /* 슬롯 범위 검사 */
        if (unit_slot >= (DWORD)US_COUNT) {
            set_reason(res, CP_REASON_AXIS_LOGIC, "invalid_slot");
            return;
        }

        /* 슬롯 활성 여부 검사 */
        SHORT ex = *((volatile SHORT*)(uintptr_t)
                     (US_EXISTS_VA + unit_slot * 2));
        if (ex == 0) {
            set_reason(res, CP_REASON_AXIS_LOGIC, "invalid_slot");
            return;
        }

        DWORD base = US_ARRAY_VA + unit_slot * (DWORD)US_STRIDE;
        if (base == 0) {
            set_reason(res, CP_REASON_AXIS_LOGIC, "null_ptr");
            return;
        }

        /* offset + size 범위 검사 (stride 내부) */
        if (offset + size > (DWORD)US_STRIDE) {
            set_reason(res, CP_REASON_AXIS_LOGIC, "out_of_bounds");
            return;
        }

        target_va = base + offset;

    } else if (lstrcmpA(mode, "absolute_va") == 0) {
        /* 모드 B: 절대 VA 직접 */
        char va_str[32];
        if (!rd_find_str(json, "va", va_str, sizeof(va_str))) {
            set_reason(res, CP_REASON_AXIS_LOGIC, "bad_va");
            return;
        }

        /* "0x..." 또는 순수 16진 파싱 (strtoul 사용) */
        const char *vp = va_str;
        if (vp[0] == '0' && (vp[1] == 'x' || vp[1] == 'X')) vp += 2;
        if (*vp == '\0') {
            set_reason(res, CP_REASON_AXIS_LOGIC, "bad_va");
            return;
        }
        DWORD parsed = 0;
        while (*vp) {
            char c = *vp++;
            DWORD digit;
            if (c >= '0' && c <= '9')      digit = (DWORD)(c - '0');
            else if (c >= 'a' && c <= 'f') digit = (DWORD)(c - 'a' + 10);
            else if (c >= 'A' && c <= 'F') digit = (DWORD)(c - 'A' + 10);
            else { parsed = 0; break; }
            parsed = parsed * 16 + digit;
        }
        if (parsed == 0) {
            set_reason(res, CP_REASON_AXIS_LOGIC, "bad_va");
            return;
        }
        target_va = parsed;

    } else {
        set_reason(res, CP_REASON_AXIS_LOGIC, "bad_va");
        return;
    }

    /* 읽기 가능 여부 확인 */
    if (IsBadReadPtr((LPCVOID)(uintptr_t)target_va, (UINT_PTR)size)) {
        set_reason(res, CP_REASON_AXIS_ENV, "null_ptr");
        return;
    }

    /* hex 문자열 빌드 — "XX " 형식 */
    static char hex_buf[RD_HEX_BUFSIZE];
    int hpos = 0;
    DWORD i;
    for (i = 0; i < size; i++) {
        BYTE b = *((volatile BYTE *)(uintptr_t)(target_va + i));
        char tmp[8];
        wsprintfA(tmp, "%02X ", (unsigned)b);
        if (hpos + 3 < RD_HEX_BUFSIZE - 1) {
            hex_buf[hpos++] = tmp[0];
            hex_buf[hpos++] = tmp[1];
            hex_buf[hpos++] = tmp[2];
        }
    }
    /* 마지막 공백 제거 */
    if (hpos > 0 && hex_buf[hpos - 1] == ' ') hpos--;
    hex_buf[hpos] = '\0';

    /* 결과 JSON 작성 — C:\inmm_raw_dump.json */
    {
        static char out_buf[RD_HEX_BUFSIZE + 128];
        int opos = 0;
        char va_fmt[20];
        wsprintfA(va_fmt, "0x%08X", (unsigned)target_va);
        opos += wsprintfA(out_buf + opos,
            "{\"ok\":true,\"hex\":\"%s\",\"va\":\"%s\",\"len\":%u}",
            hex_buf, va_fmt, (unsigned)size);

        HANDLE hf = CreateFileA("C:\\inmm_raw_dump.json",
                                GENERIC_WRITE, 0, NULL,
                                CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
        if (hf != INVALID_HANDLE_VALUE) {
            DWORD written;
            WriteFile(hf, out_buf, (DWORD)opos, &written, NULL);
            CloseHandle(hf);
            res->ok = TRUE;
            set_reason(res, "", "ok");
        } else {
            set_reason(res, CP_REASON_AXIS_ENV, "file_create_failed");
        }
    }
}

/* ------------------------------------------------------------------ */
/* control_executor_run                                                */
/* ------------------------------------------------------------------ */
void control_executor_run(const control_request_t *req, control_result_t *res)
{
    DWORD state_before  = 0xFFFFFFFFu;
    DWORD final_state   = 0xFFFFFFFFu;
    DWORD effective_timeout;
    DWORD t0 = GetTickCount();

    res_init(res, req);

    if (is_cheat_start_goal(req->goal)) {
        run_cheat_start(req, res);
        control_log_event(req->request_id, "executor_finish", req->goal,
                          res->start_state, res->end_state,
                          res->bridge_used, res->reason);
        return;
    }

    if (is_chain_inject_goal(req->goal)) {
        run_chain_inject(req, res);
        control_log_event(req->request_id, "executor_finish", req->goal,
                          res->start_state, res->end_state,
                          res->bridge_used, res->reason);
        return;
    }

    if (is_set_seed_goal(req->goal)) {
        run_set_seed(req, res);
        control_log_event(req->request_id, "executor_finish", req->goal,
                          res->start_state, res->end_state,
                          res->bridge_used, res->reason);
        return;
    }

    if (is_scenario1_select_goal(req->goal)) {
        run_scenario1_select(req, res);
        control_log_event(req->request_id, "executor_finish", req->goal,
                          res->start_state, res->end_state,
                          res->bridge_used, res->reason);
        return;
    }

    if (is_map_widget_probe_goal(req->goal)) {
        run_map_widget_probe(req, res);
        control_log_event(req->request_id, "executor_finish", req->goal,
                          res->start_state, res->end_state,
                          res->bridge_used, res->reason);
        return;
    }

    if (is_child_control_probe_goal(req->goal)) {
        run_child_control_probe(req, res);
        control_log_event(req->request_id, "executor_finish", req->goal,
                          res->start_state, res->end_state,
                          res->bridge_used, res->reason);
        return;
    }

    if (is_lobby_map_probe_goal(req->goal)) {
        run_lobby_map_probe(req, res);
        control_log_event(req->request_id, "executor_finish", req->goal,
                          res->start_state, res->end_state,
                          res->bridge_used, res->reason);
        return;
    }

    if (is_combat_melee_adjacent_goal(req->goal)) {
        if (lstrcmpA(req->goal, "_combat_scenario1_melee_adjacent") == 0 ||
            lstrcmpA(req->goal, "_combat_scenario1_melee_isolated") == 0)
            run_combat_scenario1_melee_adjacent(req, res);
        else
            run_combat_melee_adjacent(req, res);
        control_log_event(req->request_id, "executor_finish", req->goal,
                          res->start_state, res->end_state,
                          res->bridge_used, res->reason);
        return;
    }

    if (is_g4_idle_attack_probe_goal(req->goal)) {
        run_g4_idle_attack_probe(req, res);
        control_log_event(req->request_id, "executor_finish", req->goal,
                          res->start_state, res->end_state,
                          res->bridge_used, res->reason);
        return;
    }

    if (is_g4_waypoint_probe_goal(req->goal)) {
        run_g4_waypoint_probe(req, res);
        control_log_event(req->request_id, "executor_finish", req->goal,
                          res->start_state, res->end_state,
                          res->bridge_used, res->reason);
        return;
    }

    if (is_mouse_probe_goal(req->goal)) {
        run_mouse_probe(req, res);
        control_log_event(req->request_id, "executor_finish", req->goal,
                          res->start_state, res->end_state,
                          res->bridge_used, res->reason);
        return;
    }

    if (is_custom_probe_goal(req->goal)) {
        run_custom_probe(req, res);
        control_log_event(req->request_id, "executor_finish", req->goal,
                          res->start_state, res->end_state,
                          res->bridge_used, res->reason);
        return;
    }

    if (is_test_handler_goal(req->goal)) {
        run_test_handler_slot(req, res);
        control_log_event(req->request_id, "executor_finish", req->goal,
                          res->start_state, res->end_state,
                          res->bridge_used, res->reason);
        return;
    }

    if (is_read_unit_state_goal(req->goal)) {
        run_read_unit_state(req, res);
        control_log_event(req->request_id, "executor_finish", req->goal,
                          res->start_state, res->end_state,
                          res->bridge_used, res->reason);
        return;
    }

    if (is_raw_dump_goal(req->goal)) {
        run_raw_dump(req, res);
        control_log_event(req->request_id, "executor_finish", req->goal,
                          res->start_state, res->end_state,
                          res->bridge_used, res->reason);
        return;
    }

    /* 1. goal 조회 */
    const goal_entry_t *entry = control_registry_lookup(req->goal);
    if (!entry) {
        set_reason(res, CP_REASON_AXIS_LOGIC, "unknown_goal");
        control_log_event(req->request_id, "executor_finish", req->goal,
                          0xFFFFFFFF, 0xFFFFFFFF, "", "unknown_goal");
        return;
    }

    /* 2. 현재 상태 읽기 */
    csb_read_state(&state_before);
    res->start_state = state_before;

    /* 3. executor_start */
    control_log_event(req->request_id, "executor_start", req->goal,
                      state_before, entry->preprocess_state, "state", "");

    effective_timeout = (req->timeout_ms > 0)
                        ? req->timeout_ms
                        : entry->default_timeout_ms;

    /* 4. state bridge 시도 */
    BOOL success = try_state_bridge(req, entry, res, effective_timeout, &final_state);

    /* 5. state 실패 + input bridge 허용 시에만 input fallback */
    if (!success && entry->window_active_required && req->params.allow_input_bridge) {
        try_input_bridge(req, entry, res);
        success = csb_wait_steady(entry->steady_state,
                                  effective_timeout / 2, &final_state);
        if (success) {
            control_log_event(req->request_id, "state_wait_success", req->goal,
                              entry->preprocess_state, final_state,
                              res->bridge_used, "");
        }
    }

    /* 6. handler bridge fallback (allow_handler_bridge 허용 시) */
    if (!success && req->params.allow_handler_bridge) {
        success = try_handler_bridge(req, entry, res,
                                     effective_timeout, &final_state);
    }

    res->end_state     = final_state;
    res->state_reached = final_state;
    res->elapsed_ms    = GetTickCount() - t0;

    if (success) {
        res->ok = TRUE;
        set_reason(res, "", "ok");
    } else {
        res->ok = FALSE;
        if (res->rollback_attempted && !res->rollback_ok) {
            set_reason(res, CP_REASON_AXIS_ENV, "rollback_failed");
        } else if (lstrcmpA(res->bridge_used, "handler") == 0) {
            set_reason(res, CP_REASON_AXIS_LOGIC, "handler_slot_timeout");
        } else {
            set_reason(res, CP_REASON_AXIS_LOGIC, "state_wait_timeout");
        }
        control_log_event(req->request_id, "bridge_exhausted", req->goal,
                          entry->preprocess_state, final_state,
                          res->bridge_used, res->fallback_chain);
    }

    control_log_event(req->request_id, "executor_finish", req->goal,
                      state_before, final_state,
                      res->bridge_used, res->reason);
}
