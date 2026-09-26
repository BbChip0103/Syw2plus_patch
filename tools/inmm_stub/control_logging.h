/* control_logging.h — control plane 이벤트 로깅 (Win32 전용) */
#ifndef CONTROL_LOGGING_H
#define CONTROL_LOGGING_H

#include <windows.h>

#define CONTROL_EVENTS_JSONL "C:\\inmm_control_events.jsonl"

/* control_log_init: 세션 시작 시 1회 호출 (inmm_stub.c의 jsonl_init에서 호출) */
void control_log_init(void);

/* control_log_close: DLL detach 시 호출 */
void control_log_close(void);

/* control_log_event: control plane 이벤트 1개를 JSONL로 기록
 * - request_id: NULL이면 "-" 출력
 * - event_name: 필수 (예: "session_start", "executor_start", "state_write_attempt" 등)
 * - goal: NULL이면 "-" 출력
 * - state_before: 0xFFFFFFFF이면 -1로 기록
 * - state_after: 0xFFFFFFFF이면 -1로 기록
 * - bridge: NULL이면 "-" 출력
 * - detail: NULL이면 "" 출력
 */
void control_log_event(
    const char *request_id,
    const char *event_name,
    const char *goal,
    DWORD       state_before,
    DWORD       state_after,
    const char *bridge,
    const char *detail
);

#endif /* CONTROL_LOGGING_H */
