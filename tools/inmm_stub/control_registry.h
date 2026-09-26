/* control_registry.h — goal → state 매핑 레지스트리 (Win32 전용)
 *
 * R4 확장:
 *  - goal 필수 범위 확대 (enter_briefing / enter_lobby / enter_load_game /
 *    enter_victory / enter_defeat / enter_battle_report)
 *  - 메타데이터 필드: handler_timeout_ms, bridge_priority, allowed_start_states
 *
 * 문자열/숫자 배열은 고정 크기로 선언 — CRT free 한계 안에서 유지한다.
 */
#ifndef CONTROL_REGISTRY_H
#define CONTROL_REGISTRY_H

#include <windows.h>

#define BRIDGE_UNKNOWN          0
#define BRIDGE_OK               1
#define BRIDGE_FAIL             2

#define BRIDGE_PRIO_STATE       0
#define BRIDGE_PRIO_INPUT       1
#define BRIDGE_PRIO_HANDLER     2

#define REGISTRY_MAX_STARTS     6   /* allowed_start_states 최대 개수 */

typedef struct {
    const char *goal;
    DWORD       preprocess_state;
    DWORD       steady_state;
    DWORD       default_timeout_ms;

    /* B5/R5: bridge metadata */
    BOOL        window_active_required;
    int         bridge_baseline_a;
    int         bridge_baseline_b;

    /* R4: 추가 메타데이터 */
    DWORD       handler_timeout_ms;   /* 0 이면 CHB_DEFAULT_TIMEOUT_MS 사용 */
    BOOL        handler_allowed;      /* handler bridge fallback 허용 여부 */
    int         bridge_priority[3];   /* {STATE, INPUT, HANDLER} 순서 */
    int         allowed_start_states[REGISTRY_MAX_STARTS]; /* -1=end marker */
    const char *bridge_downgrade_trigger;                  /* 예: "[0x66976C]==0" */
} goal_entry_t;

const goal_entry_t *control_registry_lookup(const char *goal);

#endif /* CONTROL_REGISTRY_H */
