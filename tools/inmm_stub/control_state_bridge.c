/* control_state_bridge.c — PROGRAM_STATE 직접 읽기/쓰기 (Win32 전용, CRT 없음)
 *
 * R1 보정: PROGRAM_STATE(0x004ED818)는 WORD(2바이트).
 *   - 외부 API 시그니처는 DWORD 유지(executor/result 직렬화 호환).
 *   - 실제 메모리 접근은 USHORT(WORD) 2바이트로 수행.
 *   - 쓰기는 상위 바이트를 교란하지 않도록 2바이트만 기록.
 */

#include <windows.h>
#include "control_state_bridge.h"

/* ------------------------------------------------------------------ */
/* csb_read_state — WORD read → DWORD로 승격 반환                      */
/* ------------------------------------------------------------------ */
BOOL csb_read_state(DWORD *out)
{
    volatile USHORT *p = (volatile USHORT *)(uintptr_t)PROGRAM_STATE_VA;
    *out = (DWORD)(*p);
    return TRUE;
}

/* ------------------------------------------------------------------ */
/* csb_write_state — WORD write (상위 바이트 보존)                     */
/* ------------------------------------------------------------------ */
BOOL csb_write_state(DWORD val)
{
    USHORT *p = (USHORT *)(uintptr_t)PROGRAM_STATE_VA;
    if (IsBadWritePtr(p, sizeof(USHORT))) return FALSE;
    *p = (USHORT)(val & 0xFFFFu);
    return TRUE;
}

/* ------------------------------------------------------------------ */
/* csb_wait_steady                                                     */
/* ------------------------------------------------------------------ */
BOOL csb_wait_steady(DWORD expected, DWORD timeout_ms, DWORD *final_state)
{
    DWORD deadline = GetTickCount() + timeout_ms;
    DWORD cur = 0xFFFFFFFFu;

    for (;;) {
        if (csb_read_state(&cur)) {
            *final_state = cur;
            if (cur == expected) return TRUE;
        }
        if (GetTickCount() >= deadline) break;
        Sleep(30);
    }

    if (!csb_read_state(&cur)) cur = 0xFFFFFFFFu;
    *final_state = cur;
    return FALSE;
}
