/* control_handler_bridge.h — main-loop slot 대기 패턴 (Win32 전용, CRT 없음)
 *
 * 목적: 게임 내부 handler VA를 안전하게 호출하기 위한 단일-슬롯 브리지.
 *       worker thread는 slot에 요청을 enqueue하고 bounded wait 수행,
 *       main-loop thread는 _imeGetTime 안에서 slot을 drain(실행/완료)한다.
 *
 * 동시성 계약:
 *   - 슬롯은 1개(single slot)뿐이며 InterlockedCompareExchange로 claim.
 *   - 동시에 2개의 요청이 들어오면 두 번째는 즉시 slot_busy로 거부.
 *   - worker에서 handler VA를 직접 호출하는 경로 없음.
 *
 * 이벤트:
 *   slot_wait_start    — worker가 slot 요청 등록
 *   slot_wait_success  — main thread가 slot drain 완료
 *   slot_wait_expired  — timeout 도달, worker 복귀
 *   slot_busy          — 재진입/동시 호출 거부
 */
#ifndef CONTROL_HANDLER_BRIDGE_H
#define CONTROL_HANDLER_BRIDGE_H

#include <windows.h>

#define CHB_SLOT_EMPTY      0
#define CHB_SLOT_PENDING    1
#define CHB_SLOT_DONE       2
/* Claimed by a worker while its static slot payload is being published.
 * Main-loop drain must never execute this intermediate state. */
#define CHB_SLOT_CLAIMED    3

#define CHB_DEFAULT_TIMEOUT_MS  500u

/* 기본 handler type — no args, no return (B6 최소형).
 * 실제 게임 handler는 복잡한 인자를 받지만, B6에서는 "slot 메커니즘"만 검증한다.
 * 차기 스토리에서 인자/반환값 확장 가능. */
typedef void (WINAPI *chb_handler_fn_t)(void);

/* worker thread에서 호출.
 *   request_id: 로그용
 *   label     : handler 식별용 (예: "preproc_title")
 *   handler_va: 실행할 함수 VA (0이면 no-op 시뮬레이션)
 *   timeout_ms: 0이면 CHB_DEFAULT_TIMEOUT_MS 사용
 * 반환: TRUE=main thread가 drain했음, FALSE=timeout/busy */
BOOL chb_call_handler(const char *request_id,
                      const char *label,
                      DWORD handler_va,
                      DWORD timeout_ms);

/* main-loop thread(_imeGetTime)에서 호출.
 * pending slot이 있으면 handler를 실행하고 상태를 DONE으로 전환. */
void chb_drain_slot_mainthread(void);

#endif /* CONTROL_HANDLER_BRIDGE_H */
