/**
 * control_logging.c — control plane 이벤트 로깅 (Win32 전용)
 *
 * Win32 API만 사용. CRT 함수(fopen/fprintf/sprintf 등) 금지.
 */

#include "control_logging.h"

/* ------------------------------------------------------------------ */
/* 모듈 내 파일 핸들                                                  */
/* ------------------------------------------------------------------ */
static HANDLE g_control_log = INVALID_HANDLE_VALUE;

/* ------------------------------------------------------------------ */
/* open_append 헬퍼 (control_logging 전용)                            */
/* ------------------------------------------------------------------ */
static HANDLE cl_open_append(const char *path)
{
    HANDLE h = CreateFileA(path, GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE,
                           NULL, OPEN_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (h != INVALID_HANDLE_VALUE)
        SetFilePointer(h, 0, NULL, FILE_END);
    return h;
}

static void cl_file_write(HANDLE h, const char *buf)
{
    if (h == INVALID_HANDLE_VALUE) return;
    DWORD written;
    WriteFile(h, buf, lstrlenA(buf), &written, NULL);
}

/* ------------------------------------------------------------------ */
/* 공개 API                                                            */
/* ------------------------------------------------------------------ */
void control_log_init(void)
{
    if (g_control_log != INVALID_HANDLE_VALUE) return; /* 중복 호출 방지 */
    g_control_log = cl_open_append(CONTROL_EVENTS_JSONL);

    /* session_start 이벤트 즉시 기록 */
    control_log_event(NULL, "session_start", NULL,
                      0xFFFFFFFF, 0xFFFFFFFF, NULL, "inmm_stub attached");
}

void control_log_close(void)
{
    if (g_control_log != INVALID_HANDLE_VALUE) {
        CloseHandle(g_control_log);
        g_control_log = INVALID_HANDLE_VALUE;
    }
}

void control_log_event(
    const char *request_id,
    const char *event_name,
    const char *goal,
    DWORD       state_before,
    DWORD       state_after,
    const char *bridge,
    const char *detail)
{
    if (g_control_log == INVALID_HANDLE_VALUE) return;

    /* NULL 인자 기본값 처리 */
    const char *rid    = (request_id && request_id[0]) ? request_id : "-";
    const char *ev     = (event_name && event_name[0]) ? event_name : "unknown";
    const char *gl     = (goal       && goal[0])       ? goal       : "-";
    const char *br     = (bridge     && bridge[0])     ? bridge     : "-";
    const char *det    = (detail     && detail[0])     ? detail     : "";

    /* state_before / state_after: 0xFFFFFFFF → -1 */
    char sb_str[12], sa_str[12];
    if (state_before == 0xFFFFFFFFu) {
        lstrcpyA(sb_str, "-1");
    } else {
        wsprintfA(sb_str, "%u", (unsigned)state_before);
    }
    if (state_after == 0xFFFFFFFFu) {
        lstrcpyA(sa_str, "-1");
    } else {
        wsprintfA(sa_str, "%u", (unsigned)state_after);
    }

    char buf[512];
    wsprintfA(buf,
              "{\"ts_ms\":%u,\"pid\":%u,\"request_id\":\"%s\","
              "\"event\":\"%s\",\"goal\":\"%s\","
              "\"state_before\":%s,\"state_after\":%s,"
              "\"bridge\":\"%s\",\"detail\":\"%s\"}\n",
              (unsigned)GetTickCount(),
              (unsigned)GetCurrentProcessId(),
              rid, ev, gl, sb_str, sa_str, br, det);

    cl_file_write(g_control_log, buf);
}
