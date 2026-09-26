/* control_handler_bridge.c — main-loop slot 대기 패턴 (Win32 전용, CRT 없음) */

#include <windows.h>
#include "control_handler_bridge.h"
#include "control_logging.h"

/* ------------------------------------------------------------------ */
/* 단일 슬롯 상태                                                     */
/* ------------------------------------------------------------------ */
static volatile LONG    s_slot_state   = CHB_SLOT_EMPTY;
static DWORD            s_handler_va   = 0;
static DWORD            s_deadline_tick= 0;
static char             s_request_id[32];
static char             s_label[32];

/* ------------------------------------------------------------------ */
/* chb_call_handler — worker thread enqueue + bounded wait            */
/* ------------------------------------------------------------------ */
BOOL chb_call_handler(const char *request_id,
                      const char *label,
                      DWORD handler_va,
                      DWORD timeout_ms)
{
    DWORD effective = (timeout_ms > 0) ? timeout_ms : CHB_DEFAULT_TIMEOUT_MS;

    /* 1. 재진입 방지: slot이 EMPTY일 때만 PENDING으로 CAS */
    LONG prev = InterlockedCompareExchange(&s_slot_state,
                                           CHB_SLOT_CLAIMED,
                                           CHB_SLOT_EMPTY);
    if (prev != CHB_SLOT_EMPTY) {
        control_log_event(request_id, "slot_busy", label,
                          0xFFFFFFFF, 0xFFFFFFFF, "handler",
                          "slot already in use");
        return FALSE;
    }

    /* 2. slot payload 설정 (단일 writer: claim한 worker만 쓴다) */
    s_handler_va = handler_va;
    lstrcpynA(s_request_id, request_id ? request_id : "-", 32);
    lstrcpynA(s_label,      label      ? label      : "-", 32);
    s_deadline_tick = GetTickCount() + effective;

    /* Publish only after every shared payload field is complete.  The main
     * loop drains PENDING exclusively, so it cannot observe a half-written
     * handler address/label/request. */
    InterlockedExchange(&s_slot_state, CHB_SLOT_PENDING);

    {
        char detail[80];
        wsprintfA(detail, "timeout_ms=%u handler_va=0x%08X",
                  (unsigned)effective, (unsigned)handler_va);
        control_log_event(request_id, "slot_wait_start", label,
                          0xFFFFFFFF, 0xFFFFFFFF, "handler", detail);
    }

    /* 3. bounded poll: main thread가 DONE으로 전환할 때까지 */
    for (;;) {
        LONG st = InterlockedCompareExchange(&s_slot_state,
                                             CHB_SLOT_EMPTY,
                                             CHB_SLOT_DONE);
        if (st == CHB_SLOT_DONE) {
            /* main thread가 drain 완료 → EMPTY로 리셋했음 */
            control_log_event(request_id, "slot_wait_success", label,
                              0xFFFFFFFF, 0xFFFFFFFF, "handler", "");
            return TRUE;
        }

        if (GetTickCount() >= s_deadline_tick) {
            /* timeout — slot을 강제로 EMPTY로 전환.
             * main thread가 그 사이 PENDING을 읽고 handler를 실행하려 해도
             * state_write의 revert 경로에서 보호됨 (B3 state_bridge 호출자 책임). */
            InterlockedExchange(&s_slot_state, CHB_SLOT_EMPTY);
            control_log_event(request_id, "slot_wait_expired", label,
                              0xFFFFFFFF, 0xFFFFFFFF, "handler",
                              "timeout — main-loop slot not drained");
            return FALSE;
        }

        Sleep(5); /* 5ms poll — worker는 이 동안 다른 작업 없음 */
    }
}

/* ------------------------------------------------------------------ */
/* chb_drain_slot_mainthread — _imeGetTime 안에서 호출                 */
/* ------------------------------------------------------------------ */
void chb_drain_slot_mainthread(void)
{
    LONG st = InterlockedCompareExchange(&s_slot_state,
                                         CHB_SLOT_PENDING,
                                         CHB_SLOT_PENDING);
    if (st != CHB_SLOT_PENDING) {
        return; /* 빠른 경로: 대기 중인 slot 없음 */
    }

    /* Test hook: label이 "_skip_"로 시작하면 drain하지 않는다.
     * worker timeout 경로 재현 + state_bridge revert 증거 확보용. */
    if (s_label[0] == '_' && s_label[1] == 's' && s_label[2] == 'k' &&
        s_label[3] == 'i' && s_label[4] == 'p' && s_label[5] == '_') {
        return;
    }

    /* PENDING 확인됨 — main thread 유일 실행자로서 handler 호출.
     * s_handler_va == 0 이면 no-op 시뮬레이션(B6 minimal). */
    if (s_handler_va != 0) {
        if (!IsBadCodePtr((FARPROC)s_handler_va)) {
            chb_handler_fn_t fn = (chb_handler_fn_t)(ULONG_PTR)s_handler_va;
            fn();
        } else {
            control_log_event(s_request_id, "slot_error", s_label,
                              0xFFFFFFFF, 0xFFFFFFFF, "handler",
                              "handler_va unreadable");
        }
    }

    /* DONE으로 전환 — worker가 다음 poll에서 관찰 */
    InterlockedExchange(&s_slot_state, CHB_SLOT_DONE);
}
