/* control_input_bridge.h — semantic input action bridge (Win32 전용)
 *
 * R5 확장:
 *  - choose_scenario_index / choose_custom_game_slot는 VK_DOWN×N + VK_RETURN
 *    key-navigation을 기본 경로로 사용 (input_action detail="key_nav")
 *  - 좌표 클릭은 cib_action_*_coordinate_fallback 로 분리, detail="coordinate_fallback"
 *  - 추가 semantic: menu_up / menu_down / advance_briefing
 */
#ifndef CONTROL_INPUT_BRIDGE_H
#define CONTROL_INPUT_BRIDGE_H

#include <windows.h>

#define WINDOW_ACTIVE_FLAG_VA  0x0066976Cu

HWND cib_get_hwnd(void);
BOOL cib_window_active(void);

/* 기존 semantic actions (path A) */
BOOL cib_action_confirm(const char *request_id);
BOOL cib_action_back(const char *request_id);

/* R5 확장 semantic actions */
BOOL cib_action_menu_up(const char *request_id);
BOOL cib_action_menu_down(const char *request_id);
BOOL cib_action_advance_briefing(const char *request_id);

/* choose_* — 기본 경로: key-nav, fallback: 좌표 클릭 */
BOOL cib_action_choose_scenario_index(const char *request_id, int index);
BOOL cib_action_choose_custom_game_slot(const char *request_id, int slot);

/* 명시적 좌표 fallback 경로 — 필요 시 executor/상위 로직이 직접 호출 */
BOOL cib_action_choose_scenario_index_coordinate_fallback(
    const char *request_id, int index);

#endif /* CONTROL_INPUT_BRIDGE_H */
