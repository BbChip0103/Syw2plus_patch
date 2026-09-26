/* control_input_bridge.c — semantic input action bridge (Win32 전용, CRT 없음)
 *
 * R5: key-navigation 기본 + coordinate_fallback 분리.
 */

#include <windows.h>
#include "control_input_bridge.h"
#include "control_logging.h"

/* ------------------------------------------------------------------ */
/* cib_get_hwnd — EnumWindows로 현재 프로세스의 첫 번째 visible window */
/* ------------------------------------------------------------------ */

static HWND  s_found_hwnd;
static LONG  s_found_area;

/* current process 소속 top-level visible window 중 최대 면적 선택.
 * 게임은 보통 800x600 등 큰 창이고 부수적으로 1x1 IME/hidden 창들이 공존. */
static BOOL CALLBACK enum_windows_proc(HWND hwnd, LPARAM lParam)
{
    DWORD pid = 0;
    (void)lParam;
    if (!IsWindowVisible(hwnd))
        return TRUE;
    GetWindowThreadProcessId(hwnd, &pid);
    if (pid != GetCurrentProcessId())
        return TRUE;

    RECT r;
    if (!GetWindowRect(hwnd, &r)) return TRUE;
    LONG area = (r.right - r.left) * (r.bottom - r.top);
    if (area > s_found_area) {
        s_found_area = area;
        s_found_hwnd = hwnd;
    }
    return TRUE;
}

HWND cib_get_hwnd(void)
{
    s_found_hwnd = NULL;
    s_found_area = 0;
    EnumWindows(enum_windows_proc, 0);
    return s_found_hwnd;
}

/* ------------------------------------------------------------------ */
/* cib_window_active — [0x66976C] != 0 이면 TRUE                      */
/* ------------------------------------------------------------------ */

BOOL cib_window_active(void)
{
    DWORD *ptr = (DWORD *)WINDOW_ACTIVE_FLAG_VA;
    if (IsBadReadPtr(ptr, sizeof(DWORD)))
        return TRUE;
    return (*ptr != 0) ? TRUE : FALSE;
}

/* ------------------------------------------------------------------ */
/* 공통 키 입력 헬퍼                                                    */
/* ------------------------------------------------------------------ */

static BOOL ensure_ready(const char *request_id, const char *label, HWND *out)
{
    HWND h = cib_get_hwnd();
    if (!h) {
        control_log_event(request_id, "bridge_error", label,
                          0xFFFFFFFF, 0xFFFFFFFF, "input_A", "hwnd=NULL");
        return FALSE;
    }
    if (!cib_window_active()) {
        control_log_event(request_id, "bridge_downgrade", label,
                          0xFFFFFFFF, 0xFFFFFFFF, "input_A", "[0x66976C]==0");
        return FALSE;
    }
    *out = h;
    return TRUE;
}

static void post_vkey(HWND h, UINT vk, DWORD scan_prefix)
{
    DWORD down = (scan_prefix << 16) | 0x00000001u;
    DWORD up   = (scan_prefix << 16) | 0xC0000001u;
    PostMessageA(h, WM_KEYDOWN, vk, down);
    PostMessageA(h, WM_KEYUP,   vk, up);
}

/* ------------------------------------------------------------------ */
/* 기존 actions                                                         */
/* ------------------------------------------------------------------ */

BOOL cib_action_confirm(const char *request_id)
{
    HWND h;
    if (!ensure_ready(request_id, "confirm", &h)) return FALSE;
    post_vkey(h, VK_RETURN, 0x001C);
    control_log_event(request_id, "input_action", "confirm",
                      0xFFFFFFFF, 0xFFFFFFFF, "input_A", "key_nav");
    return TRUE;
}

BOOL cib_action_back(const char *request_id)
{
    HWND h;
    if (!ensure_ready(request_id, "back", &h)) return FALSE;
    post_vkey(h, VK_ESCAPE, 0x0001);
    control_log_event(request_id, "input_action", "back",
                      0xFFFFFFFF, 0xFFFFFFFF, "input_A", "key_nav");
    return TRUE;
}

/* ------------------------------------------------------------------ */
/* R5 semantic actions                                                  */
/* ------------------------------------------------------------------ */

BOOL cib_action_menu_up(const char *request_id)
{
    HWND h;
    if (!ensure_ready(request_id, "menu_up", &h)) return FALSE;
    post_vkey(h, VK_UP, 0x0048);
    control_log_event(request_id, "input_action", "menu_up",
                      0xFFFFFFFF, 0xFFFFFFFF, "input_A", "key_nav");
    return TRUE;
}

BOOL cib_action_menu_down(const char *request_id)
{
    HWND h;
    if (!ensure_ready(request_id, "menu_down", &h)) return FALSE;
    post_vkey(h, VK_DOWN, 0x0050);
    control_log_event(request_id, "input_action", "menu_down",
                      0xFFFFFFFF, 0xFFFFFFFF, "input_A", "key_nav");
    return TRUE;
}

BOOL cib_action_advance_briefing(const char *request_id)
{
    HWND h;
    if (!ensure_ready(request_id, "advance_briefing", &h)) return FALSE;
    post_vkey(h, VK_RETURN, 0x001C);
    control_log_event(request_id, "input_action", "advance_briefing",
                      0xFFFFFFFF, 0xFFFFFFFF, "input_A", "key_nav");
    return TRUE;
}

/* ------------------------------------------------------------------ */
/* choose_* — key-navigation 기본                                        */
/* ------------------------------------------------------------------ */

static void key_nav_select(HWND h, int n, UINT vk_step, DWORD scan_step)
{
    for (int i = 0; i < n; ++i) {
        post_vkey(h, vk_step, scan_step);
        Sleep(30);
    }
    post_vkey(h, VK_RETURN, 0x001C);
}

BOOL cib_action_choose_scenario_index(const char *request_id, int index)
{
    HWND h;
    if (!ensure_ready(request_id, "choose_scenario_index", &h)) return FALSE;
    if (index < 0) index = 0;
    if (index > 63) index = 63;
    key_nav_select(h, index, VK_DOWN, 0x0050);
    char detail[48];
    wsprintfA(detail, "key_nav index=%d", index);
    control_log_event(request_id, "input_action", "choose_scenario_index",
                      0xFFFFFFFF, 0xFFFFFFFF, "input_A", detail);
    return TRUE;
}

BOOL cib_action_choose_custom_game_slot(const char *request_id, int slot)
{
    HWND h;
    if (!ensure_ready(request_id, "choose_custom_game_slot", &h)) return FALSE;
    if (slot < 0) slot = 0;
    if (slot > 63) slot = 63;
    key_nav_select(h, slot, VK_DOWN, 0x0050);
    char detail[48];
    wsprintfA(detail, "key_nav slot=%d", slot);
    control_log_event(request_id, "input_action", "choose_custom_game_slot",
                      0xFFFFFFFF, 0xFFFFFFFF, "input_A", detail);
    return TRUE;
}

/* ------------------------------------------------------------------ */
/* coordinate fallback — 명시적 분리 경로                                */
/* ------------------------------------------------------------------ */

BOOL cib_action_choose_scenario_index_coordinate_fallback(
    const char *request_id, int index)
{
    HWND h;
    if (!ensure_ready(request_id, "choose_scenario_index_coord", &h))
        return FALSE;
    int x = 512;
    int y = 200 + index * 40;
    PostMessageA(h, WM_LBUTTONDOWN, MK_LBUTTON, MAKELPARAM(x, y));
    PostMessageA(h, WM_LBUTTONUP,   0,          MAKELPARAM(x, y));
    char detail[64];
    wsprintfA(detail, "coordinate_fallback index=%d x=%d y=%d", index, x, y);
    control_log_event(request_id, "input_action",
                      "choose_scenario_index",
                      0xFFFFFFFF, 0xFFFFFFFF, "input_A", detail);
    return TRUE;
}
