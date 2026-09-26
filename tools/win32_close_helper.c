/*
 * win32_close_helper.c — fail-closed owned Win32 close transport.
 *
 * The helper is deliberately a small PE32 executable with no CRT dependency.
 * It accepts only a Win32 process id, enumerates top-level windows owned by
 * that process, and posts WM_CLOSE only when exactly one match exists.
 */
#include <windows.h>

typedef struct {
    DWORD requested_pid;
    DWORD match_count;
    HWND matched_hwnd;
    DWORD matched_thread;
} MatchContext;

static BOOL CALLBACK enum_owned_window(HWND hwnd, LPARAM raw_context)
{
    MatchContext *context = (MatchContext *)raw_context;
    DWORD pid = 0;
    DWORD thread = GetWindowThreadProcessId(hwnd, &pid);
    /* Wine may expose hidden per-process helper windows.  The close target
     * is the owned visible top-level client window, not those auxiliaries. */
    if (thread != 0 && pid == context->requested_pid && IsWindowVisible(hwnd)) {
        ++context->match_count;
        if (context->match_count == 1) {
            context->matched_hwnd = hwnd;
            context->matched_thread = thread;
        }
    }
    return TRUE;
}

static void write_stdout(const char *text)
{
    HANDLE output = GetStdHandle(STD_OUTPUT_HANDLE);
    DWORD written = 0;
    if (output != INVALID_HANDLE_VALUE && output != NULL)
        WriteFile(output, text, (DWORD)lstrlenA(text), &written, NULL);
}

static DWORD parse_pid(void)
{
    char *command = GetCommandLineA();
    char *cursor = command;
    DWORD value = 0;
    BOOL found = FALSE;
    while (*cursor != 0) {
        if (cursor[0] == '-' && cursor[1] == '-' &&
            cursor[2] == 'p' && cursor[3] == 'i' && cursor[4] == 'd' &&
            (cursor[5] == ' ' || cursor[5] == '\t')) {
            cursor += 5;
            while (*cursor == ' ' || *cursor == '\t') ++cursor;
            if (*cursor < '1' || *cursor > '9') return 0;
            while (*cursor >= '0' && *cursor <= '9') {
                DWORD digit = (DWORD)(*cursor - '0');
                if (value > (0xffffffffu - digit) / 10u) return 0;
                value = value * 10u + digit;
                ++cursor;
            }
            found = TRUE;
            break;
        }
        ++cursor;
    }
    return found ? value : 0;
}

int WINAPI WinMain(HINSTANCE instance, HINSTANCE previous, LPSTR command, int show)
{
    MatchContext context;
    char result[512];
    DWORD pid = parse_pid();
    BOOL posted = FALSE;
    DWORD post_error = ERROR_SUCCESS;
    (void)instance;
    (void)previous;
    (void)command;
    (void)show;

    context.requested_pid = pid;
    context.match_count = 0;
    context.matched_hwnd = NULL;
    context.matched_thread = 0;
    if (pid != 0)
        EnumWindows(enum_owned_window, (LPARAM)&context);

    if (pid != 0 && context.match_count == 1) {
        SetLastError(ERROR_SUCCESS);
        posted = PostMessageA(context.matched_hwnd, WM_CLOSE, 0, 0);
        if (!posted) post_error = GetLastError();
    } else {
        post_error = ERROR_INVALID_DATA;
    }

    wsprintfA(result,
        "{\"status\":\"%s\",\"requested_pid\":%u,"
        "\"matched_hwnd\":\"0x%08X\",\"matched_thread\":%u,"
        "\"match_count\":%u,\"post_result\":%s,\"post_error\":%u}\n",
        posted ? "PASS" : "FAIL", (unsigned)pid,
        (unsigned)(UINT_PTR)context.matched_hwnd,
        (unsigned)context.matched_thread, (unsigned)context.match_count,
        posted ? "true" : "false", (unsigned)post_error);
    write_stdout(result);
    return posted ? 0 : 2;
}
