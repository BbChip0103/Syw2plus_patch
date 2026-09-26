/* control_state_bridge.h — PROGRAM_STATE 직접 읽기/쓰기 (Win32 전용) */
#ifndef CONTROL_STATE_BRIDGE_H
#define CONTROL_STATE_BRIDGE_H

#include <windows.h>

#define PROGRAM_STATE_VA 0x004ED818u

/* PROGRAM_STATE 를 읽어 *out 에 저장. 실패 시 FALSE. */
BOOL csb_read_state(DWORD *out);

/* PROGRAM_STATE 에 val 을 씀. 실패 시 FALSE. */
BOOL csb_write_state(DWORD val);

/* expected 상태가 될 때까지 최대 timeout_ms 동안 30ms 단위로 폴링.
 * 마지막으로 읽은 상태를 *final_state 에 기록.
 * expected 에 도달하면 TRUE, 타임아웃이면 FALSE. */
BOOL csb_wait_steady(DWORD expected, DWORD timeout_ms, DWORD *final_state);

#endif /* CONTROL_STATE_BRIDGE_H */
