/* Private ESL2614 diagnostic proxy. It forwards the game's four WinMM imports
 * and polls the already pinned stock-layout bridge from the game tick caller. */
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <mmsystem.h>

extern void supply_probe_poll(void *caller);

static HMODULE real_winmm;

static FARPROC winmm_proc(const char *name)
{
    if (!real_winmm)
        real_winmm = LoadLibraryA("C:\\windows\\system32\\winmm.dll");
    return real_winmm ? GetProcAddress(real_winmm, name) : NULL;
}

HWND cib_get_hwnd(void)
{
    HWND window = GetForegroundWindow();
    DWORD pid = 0;
    if (window && GetWindowThreadProcessId(window, &pid) == GetCurrentThreadId() &&
        pid == GetCurrentProcessId())
        return window;
    return NULL;
}

MMRESULT WINAPI timeBeginPeriod(UINT period)
{
    typedef MMRESULT (WINAPI *fn_t)(UINT);
    fn_t fn = (fn_t)winmm_proc("timeBeginPeriod");
    return fn ? fn(period) : MMSYSERR_ERROR;
}

MMRESULT WINAPI timeEndPeriod(UINT period)
{
    typedef MMRESULT (WINAPI *fn_t)(UINT);
    fn_t fn = (fn_t)winmm_proc("timeEndPeriod");
    return fn ? fn(period) : MMSYSERR_ERROR;
}

MCIERROR WINAPI mciSendCommandA(MCIDEVICEID device, UINT command,
                                DWORD_PTR flags, DWORD_PTR parameters)
{
    typedef MCIERROR (WINAPI *fn_t)(MCIDEVICEID, UINT, DWORD_PTR, DWORD_PTR);
    fn_t fn = (fn_t)winmm_proc("mciSendCommandA");
    return fn ? fn(device, command, flags, parameters) : MCIERR_DEVICE_NOT_INSTALLED;
}

DWORD WINAPI timeGetTime(void)
{
    typedef DWORD (WINAPI *fn_t)(void);
    fn_t fn;
    /* Raw 2614 retains call 0x42334A and its WinMM timeGetTime IAT at 0x4E5294. */
    supply_probe_poll((void *)(ULONG_PTR)0x0042334Cu);
    fn = (fn_t)winmm_proc("timeGetTime");
    return fn ? fn() : 0;
}

BOOL WINAPI DllMain(HINSTANCE instance, DWORD reason, LPVOID reserved)
{
    (void)instance;
    (void)reason;
    (void)reserved;
    return TRUE;
}
