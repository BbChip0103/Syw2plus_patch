/**
 * asset_hook.c — kernel32!CreateFileA/W IAT hook for syw2plus_original.exe.
 *
 * Strategy: PE import table walk → find kernel32.dll descriptor →
 *           locate CreateFileA / CreateFileW slots in IAT →
 *           VirtualProtect + replace pointer with our wrappers.
 *
 * Wrapper logs (timestamp, PS, file_path) to C:\inmm_asset_log.jsonl, then
 * forwards the call to the real kernel32!CreateFileA via saved fn-pointers.
 *
 * Win32-only: no msvcrt deps. Same constraint as inmm_stub.c.
 */

#include "asset_hook.h"
#include "control_state_bridge.h"
#include <windows.h>

/* Saved real function pointers (resolved at install time). */
typedef HANDLE (WINAPI *CreateFileA_t)(LPCSTR, DWORD, DWORD,
                                       LPSECURITY_ATTRIBUTES, DWORD, DWORD,
                                       HANDLE);
typedef HANDLE (WINAPI *CreateFileW_t)(LPCWSTR, DWORD, DWORD,
                                       LPSECURITY_ATTRIBUTES, DWORD, DWORD,
                                       HANDLE);

static CreateFileA_t g_real_CreateFileA = NULL;
static CreateFileW_t g_real_CreateFileW = NULL;

static HANDLE        g_asset_log = INVALID_HANDLE_VALUE;
static volatile LONG g_in_hook   = 0; /* re-entrancy guard */

/* ------------------------------------------------------------------ */
/* Logging                                                             */
/* ------------------------------------------------------------------ */
static void asset_log_open(void)
{
    g_asset_log = CreateFileA("C:\\inmm_asset_log.jsonl",
                              GENERIC_WRITE,
                              FILE_SHARE_READ,
                              NULL, CREATE_ALWAYS,
                              FILE_ATTRIBUTE_NORMAL, NULL);
}

static void asset_log_write(const char *path_a, const wchar_t *path_w)
{
    if (g_asset_log == INVALID_HANDLE_VALUE) return;

    DWORD ps = 0xFFFFFFFFu;
    csb_read_state(&ps);

    char line[1024];
    int  n;
    if (path_a) {
        n = wsprintfA(line, "{\"ts\":%u,\"ps\":%u,\"api\":\"A\",\"path\":\"%s\"}\n",
                      (unsigned)GetTickCount(), (unsigned)ps, path_a);
    } else {
        /* UTF-16 → narrow conversion (best-effort, ASCII subset only) */
        char narrow[512];
        int  i = 0;
        while (path_w && path_w[i] && i < 511) {
            narrow[i] = (path_w[i] < 128) ? (char)path_w[i] : '?';
            ++i;
        }
        narrow[i] = 0;
        n = wsprintfA(line, "{\"ts\":%u,\"ps\":%u,\"api\":\"W\",\"path\":\"%s\"}\n",
                      (unsigned)GetTickCount(), (unsigned)ps, narrow);
    }
    DWORD written = 0;
    WriteFile(g_asset_log, line, n, &written, NULL);
    FlushFileBuffers(g_asset_log);
}

/* ------------------------------------------------------------------ */
/* Wrapper functions                                                   */
/* ------------------------------------------------------------------ */
static HANDLE WINAPI hook_CreateFileA(LPCSTR fileName, DWORD access,
                                      DWORD share, LPSECURITY_ATTRIBUTES sec,
                                      DWORD disp, DWORD flags, HANDLE templ)
{
    /* re-entrancy: skip logging when called from within asset_log_write */
    if (InterlockedExchange(&g_in_hook, 1) == 0) {
        if (fileName) asset_log_write(fileName, NULL);
        InterlockedExchange(&g_in_hook, 0);
    }
    return g_real_CreateFileA(fileName, access, share, sec, disp, flags, templ);
}

static HANDLE WINAPI hook_CreateFileW(LPCWSTR fileName, DWORD access,
                                      DWORD share, LPSECURITY_ATTRIBUTES sec,
                                      DWORD disp, DWORD flags, HANDLE templ)
{
    if (InterlockedExchange(&g_in_hook, 1) == 0) {
        if (fileName) asset_log_write(NULL, fileName);
        InterlockedExchange(&g_in_hook, 0);
    }
    return g_real_CreateFileW(fileName, access, share, sec, disp, flags, templ);
}

/* ------------------------------------------------------------------ */
/* IAT walking                                                         */
/* ------------------------------------------------------------------ */
static int patch_iat_for_module(HMODULE exe_base,
                                const char *target_dll,
                                const char *target_func,
                                FARPROC new_fn,
                                FARPROC *out_real_fn)
{
    BYTE *base = (BYTE *)exe_base;
    IMAGE_DOS_HEADER *dos = (IMAGE_DOS_HEADER *)base;
    if (dos->e_magic != IMAGE_DOS_SIGNATURE) return 0;

    IMAGE_NT_HEADERS *nt = (IMAGE_NT_HEADERS *)(base + dos->e_lfanew);
    if (nt->Signature != IMAGE_NT_SIGNATURE) return 0;

    DWORD imp_rva = nt->OptionalHeader
                       .DataDirectory[IMAGE_DIRECTORY_ENTRY_IMPORT].VirtualAddress;
    if (!imp_rva) return 0;

    IMAGE_IMPORT_DESCRIPTOR *imp = (IMAGE_IMPORT_DESCRIPTOR *)(base + imp_rva);

    for (; imp->Name; ++imp) {
        const char *dll_name = (const char *)(base + imp->Name);
        if (lstrcmpiA(dll_name, target_dll) != 0) continue;

        IMAGE_THUNK_DATA *oft =
            (IMAGE_THUNK_DATA *)(base + imp->OriginalFirstThunk);
        IMAGE_THUNK_DATA *ft =
            (IMAGE_THUNK_DATA *)(base + imp->FirstThunk);

        for (; oft->u1.AddressOfData; ++oft, ++ft) {
            /* Skip ordinal-only imports (high bit set) */
            if (oft->u1.Ordinal & IMAGE_ORDINAL_FLAG) continue;

            IMAGE_IMPORT_BY_NAME *imp_name =
                (IMAGE_IMPORT_BY_NAME *)(base + oft->u1.AddressOfData);
            if (lstrcmpA((const char *)imp_name->Name, target_func) != 0)
                continue;

            /* Found the slot. Save real fn-ptr, then patch. */
            *out_real_fn = (FARPROC)ft->u1.Function;

            DWORD old_protect = 0;
            if (!VirtualProtect(&ft->u1.Function, sizeof(FARPROC),
                                PAGE_READWRITE, &old_protect)) {
                return 0;
            }
            ft->u1.Function = (DWORD_PTR)new_fn;
            VirtualProtect(&ft->u1.Function, sizeof(FARPROC), old_protect,
                           &old_protect);
            return 1;
        }
    }
    return 0;
}

/* ------------------------------------------------------------------ */
/* Public install                                                      */
/* ------------------------------------------------------------------ */
int asset_hook_install(void)
{
    /* Resolve real fn pointers up-front (fallback if IAT missing) */
    HMODULE k32 = GetModuleHandleA("kernel32.dll");
    if (k32) {
        g_real_CreateFileA =
            (CreateFileA_t)GetProcAddress(k32, "CreateFileA");
        g_real_CreateFileW =
            (CreateFileW_t)GetProcAddress(k32, "CreateFileW");
    }
    if (!g_real_CreateFileA) return 0;

    asset_log_open();

    HMODULE exe = GetModuleHandleA(NULL);
    if (!exe) return 0;

    int patched = 0;
    FARPROC saved_a = NULL, saved_w = NULL;
    if (patch_iat_for_module(exe, "kernel32.dll", "CreateFileA",
                             (FARPROC)hook_CreateFileA, &saved_a)) {
        if (saved_a) g_real_CreateFileA = (CreateFileA_t)saved_a;
        ++patched;
    }
    if (patch_iat_for_module(exe, "kernel32.dll", "CreateFileW",
                             (FARPROC)hook_CreateFileW, &saved_w)) {
        if (saved_w) g_real_CreateFileW = (CreateFileW_t)saved_w;
        ++patched;
    }
    return patched;
}
