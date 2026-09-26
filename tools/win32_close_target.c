/* A self-contained PE32 target used only by the owned-close fixture. */
#include <windows.h>

static HANDLE log_handle = INVALID_HANDLE_VALUE;
static DWORD window_count;
static DWORD destroyed_count;
static DWORD close_count;

static void log_line(const char *line)
{
    DWORD written = 0;
    if (log_handle == INVALID_HANDLE_VALUE) return;
    SetFilePointer(log_handle, 0, NULL, FILE_END);
    WriteFile(log_handle, line, (DWORD)lstrlenA(line), &written, NULL);
    FlushFileBuffers(log_handle);
}

static void log_event(const char *event, HWND hwnd)
{
    char line[384];
    wsprintfA(line,
        "{\"event\":\"%s\",\"pid\":%u,\"hwnd\":\"0x%08X\","
        "\"window_count\":%u,\"destroyed_count\":%u,\"close_count\":%u}\n",
        event, (unsigned)GetCurrentProcessId(), (unsigned)(UINT_PTR)hwnd,
        (unsigned)window_count, (unsigned)destroyed_count, (unsigned)close_count);
    log_line(line);
}

static BOOL has_word(const char *command, const char *word)
{
    const char *cursor = command;
    DWORD length = lstrlenA(word);
    while (*cursor != 0) {
        DWORD index = 0;
        while (index < length && cursor[index] == word[index]) ++index;
        if (index == length) return TRUE;
        ++cursor;
    }
    return FALSE;
}

static LRESULT CALLBACK fixture_window_proc(HWND hwnd, UINT message,
                                            WPARAM wparam, LPARAM lparam)
{
    (void)lparam;
    if (message == WM_CLOSE) {
        ++close_count;
        log_event("wm_close", hwnd);
        DestroyWindow(hwnd);
        return 0;
    }
    if (message == WM_TIMER) {
        log_event("timeout_destroy", hwnd);
        DestroyWindow(hwnd);
        return 0;
    }
    if (message == WM_DESTROY) {
        ++destroyed_count;
        if (destroyed_count >= window_count) {
            log_event("quit", hwnd);
            PostQuitMessage(0);
        }
        return 0;
    }
    return DefWindowProcA(hwnd, message, wparam, lparam);
}

int WINAPI WinMain(HINSTANCE instance, HINSTANCE previous, LPSTR command, int show)
{
    WNDCLASSA klass;
    MSG message;
    HWND first = NULL;
    HWND second = NULL;
    BOOL no_window = has_word(GetCommandLineA(), "--mode none");
    BOOL multiple = has_word(GetCommandLineA(), "--mode multiple");
    (void)previous;
    (void)command;
    (void)show;

    log_handle = CreateFileA("C:\\win32_close_fixture.jsonl", GENERIC_WRITE,
                             FILE_SHARE_READ | FILE_SHARE_WRITE, NULL,
                             CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (log_handle == INVALID_HANDLE_VALUE) return 3;
    log_event("start", NULL);
    if (no_window) {
        log_event("ready", NULL);
        Sleep(1000);
        log_event("exit", NULL);
        CloseHandle(log_handle);
        return 0;
    }

    klass.style = CS_HREDRAW | CS_VREDRAW;
    klass.lpfnWndProc = fixture_window_proc;
    klass.cbClsExtra = 0;
    klass.cbWndExtra = 0;
    klass.hInstance = instance;
    klass.hIcon = NULL;
    klass.hCursor = NULL;
    klass.hbrBackground = (HBRUSH)(COLOR_WINDOW + 1);
    klass.lpszMenuName = NULL;
    klass.lpszClassName = "Syw2OwnedCloseFixture";
    if (!RegisterClassA(&klass)) return 4;

    first = CreateWindowExA(0, klass.lpszClassName, "owned-close-fixture-1",
                            WS_OVERLAPPEDWINDOW, 20, 20, 320, 200,
                            NULL, NULL, instance, NULL);
    if (!first) return 5;
    ++window_count;
    ShowWindow(first, SW_SHOW);
    if (multiple) {
        second = CreateWindowExA(0, klass.lpszClassName, "owned-close-fixture-2",
                                 WS_OVERLAPPEDWINDOW, 360, 20, 320, 200,
                                 NULL, NULL, instance, NULL);
        if (!second) return 6;
        ++window_count;
        ShowWindow(second, SW_SHOW);
    }
    log_event("ready", first);
    SetTimer(first, 1, 1500, NULL);
    if (second) SetTimer(second, 2, 1500, NULL);
    while (GetMessageA(&message, NULL, 0, 0) > 0) {
        TranslateMessage(&message);
        DispatchMessageA(&message);
    }
    log_event("exit", NULL);
    CloseHandle(log_handle);
    return 0;
}
