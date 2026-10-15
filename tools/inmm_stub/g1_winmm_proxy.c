/* App-local WINMM proxy for ESL2614. G1 hooks run for the game's four imports;
 * every other WINMM export is resolved from the system directory at call time. */
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <mmsystem.h>

MMRESULT WINAPI _imeBeginPeriod(UINT period);
MMRESULT WINAPI _imeEndPeriod(UINT period);
MCIERROR WINAPI _ciSendCommandA(MCIDEVICEID device, UINT command,
                                 DWORD_PTR flags, DWORD_PTR params);
DWORD WINAPI _imeGetTime(void);

static HMODULE g_system_winmm;

FARPROC __cdecl g1_winmm_resolve(const char *name)
{
    char path[MAX_PATH];
    UINT n;
    if (!g_system_winmm) {
        n = GetSystemDirectoryA(path, MAX_PATH);
        if (!n || n >= MAX_PATH - 11)
            return NULL;
        path[n++] = '\\';
        lstrcpyA(path + n, "winmm.dll");
        g_system_winmm = LoadLibraryA(path);
    }
    return g_system_winmm ? GetProcAddress(g_system_winmm, name) : NULL;
}

FARPROC __cdecl g1_winmm_resolve_ordinal(DWORD ordinal)
{
    char path[MAX_PATH];
    UINT n;
    if (!g_system_winmm) {
        n = GetSystemDirectoryA(path, MAX_PATH);
        if (!n || n >= MAX_PATH - 11)
            return NULL;
        path[n++] = '\\';
        lstrcpyA(path + n, "winmm.dll");
        g_system_winmm = LoadLibraryA(path);
    }
    return g_system_winmm ? GetProcAddress(g_system_winmm, (LPCSTR)(ULONG_PTR)ordinal) : NULL;
}

MMRESULT WINAPI g1_winmm_time_begin_period(UINT period)
{
    typedef MMRESULT (WINAPI *fn_t)(UINT);
    fn_t fn = (fn_t)g1_winmm_resolve("timeBeginPeriod");
    return fn ? fn(period) : MMSYSERR_ERROR;
}

MMRESULT WINAPI g1_winmm_time_end_period(UINT period)
{
    typedef MMRESULT (WINAPI *fn_t)(UINT);
    fn_t fn = (fn_t)g1_winmm_resolve("timeEndPeriod");
    return fn ? fn(period) : MMSYSERR_ERROR;
}

MCIERROR WINAPI g1_winmm_mci_send_command_a(MCIDEVICEID device, UINT command,
                                             DWORD_PTR flags, DWORD_PTR params)
{
    typedef MCIERROR (WINAPI *fn_t)(MCIDEVICEID, UINT, DWORD_PTR, DWORD_PTR);
    fn_t fn = (fn_t)g1_winmm_resolve("mciSendCommandA");
    return fn ? fn(device, command, flags, params) : MCIERR_DEVICE_NOT_INSTALLED;
}

DWORD WINAPI g1_winmm_time_get_time(void)
{
    typedef DWORD (WINAPI *fn_t)(void);
    fn_t fn = (fn_t)g1_winmm_resolve("timeGetTime");
    return fn ? fn() : 0;
}

/* Entry points in the export definition route through the existing G1 hooks. */

MMRESULT WINAPI g1_proxy_timeBeginPeriod(UINT period)
{
    return _imeBeginPeriod(period);
}

MMRESULT WINAPI g1_proxy_timeEndPeriod(UINT period)
{
    return _imeEndPeriod(period);
}

MCIERROR WINAPI g1_proxy_mciSendCommandA(MCIDEVICEID device, UINT command,
                                          DWORD_PTR flags, DWORD_PTR params)
{
    return _ciSendCommandA(device, command, flags, params);
}

DWORD WINAPI g1_proxy_timeGetTime(void)
{
    return _imeGetTime();
}

