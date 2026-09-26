/*
 * final_d3d9_trace.c — bounded D3D9 factory/device provenance trace.
 *
 * This is deliberately observation-only: it never creates a D3D object, writes
 * pixels, changes presentation parameters, or wraps a dummy object. The hook
 * is opt-in and accepts only the pinned dxwrapper export stubs.
 */
#include "final_d3d9_trace.h"
#include <windows.h>
#include <d3d9.h>

#define TRACE_ENV "INMM_FINAL_D3D9_TRACE"
#define AUDIT_ENV "INMM_FINAL_D3D9_AUDIT_ONLY"
#define CACHE_CAS_ENV "INMM_FINAL_D3D9_CACHE_CAS"
#define WINE_REBASED_ENV "INMM_FINAL_D3D9_WINE_REBASED_HEADER"
#define WINE_REBASED_E_LFANEW 296u
#define TRACE_PATH "C:\\inmm_final_d3d9_trace.jsonl"
#define DXWRAPPER_NAME "dxwrapper.dll"
#define DXWRAPPER_SHA256 "96c443193bad8794ebf04738566e092f8b34ae4541cb2433fd0708d49edbe8fe"
#define DXWRAPPER_VERSION "1.0.6542.21"
#define DXWRAPPER_TIMESTAMP 0x60B2E3C1u
#define DXWRAPPER_IMAGE_SIZE 0x23C000u
#define D3D9_SOURCE_RVA 0x001F17F8u
#define D3D9_CACHE_RVA 0x001F23B4u
#define D3D9_FACTORY_RVA 0x001F22E0u
#define D3D9_DEVICE_RVA 0x001F22E4u
#define D3D9_INIT_GUARD_RVA 0x001F23B8u
#define D3D9_CALLSITE_RVA 0x000C18C3u
#define D3D9_CALLSITE_LEN 29u
#define D3D9_INNER_SOURCE_RVA 0x001BAC60u
#define D3D9_INNER_CACHE_RVA 0x001BACC0u
#define D3D9_INNER_GUARD_RVA 0x001BACC4u
#define D3D9_INNER_SOURCE_HEADER_RVA 0x0000A969u
#define D3D9_INNER_CACHE_HEADER_RVA 0x0000A992u
#define DXWRAPPER_IMAGE_BASE 0x10000000u
#define D3D9_SOURCE_ABS 0x101F17F8u
#define D3D9_INIT_GUARD_ABS 0x101F23B8u
#define D3D9_CACHE_ABS 0x101F23B4u
#define MAX_FACTORIES 4u
#define MAX_DEVICES 8u
#define MAX_BACKBUFFERS 16u

static const BYTE d3d9_callsite_shape[D3D9_CALLSITE_LEN] = {
    0xa1,0xf8,0x17,0x1f,0x10,0x68,0xb8,0x23,0x1f,0x10,
    0xa3,0xb4,0x23,0x1f,0x10,0xe8,0xb0,0x62,0x07,0x00,
    0x83,0xc4,0x04,0xe9,0xd4,0xfd,0xff,0xff,0xcc
};

typedef IDirect3D9 *(WINAPI *create9_fn)(UINT);
typedef HRESULT (WINAPI *factory_create_device_fn)(IDirect3D9 *, UINT, D3DDEVTYPE, HWND, DWORD, D3DPRESENT_PARAMETERS *, IDirect3DDevice9 **);
typedef ULONG (WINAPI *factory_release_fn)(IDirect3D9 *);
typedef ULONG (WINAPI *device_release_fn)(IDirect3DDevice9 *);
typedef HRESULT (WINAPI *device_present_fn)(IDirect3DDevice9 *, const RECT *, const RECT *, HWND, const RGNDATA *);
typedef HRESULT (WINAPI *device_reset_fn)(IDirect3DDevice9 *, D3DPRESENT_PARAMETERS *);
typedef HRESULT (WINAPI *device_get_viewport_fn)(IDirect3DDevice9 *, D3DVIEWPORT9 *);
typedef HRESULT (WINAPI *device_backbuffer_fn)(IDirect3DDevice9 *, UINT, UINT, D3DBACKBUFFER_TYPE, IDirect3DSurface9 **);
typedef ULONG (WINAPI *surface_release_fn)(IDirect3DSurface9 *);

typedef struct {
    IDirect3D9 *object;
    void **old_vtable;
    void **clone_vtable;
    DWORD vtable_count;
    factory_create_device_fn create_device;
    factory_release_fn release;
    BOOL active;
    BOOL allocated;
} FactoryRecord;

typedef struct {
    IDirect3DDevice9 *object;
    void **old_vtable;
    void **clone_vtable;
    DWORD vtable_count;
    device_present_fn present;
    device_reset_fn reset;
    device_backbuffer_fn get_backbuffer;
    device_get_viewport_fn get_viewport;
    device_release_fn release;
    DWORD generation;
    BOOL active;
    BOOL usable;
    BOOL allocated;
} DeviceRecord;

typedef struct {
    IDirect3DSurface9 *object;
    DWORD generation;
    DWORD width;
    DWORD height;
    DWORD format;
    BOOL active;
} BackbufferRecord;

static HANDLE g_log = INVALID_HANDLE_VALUE;
static HMODULE g_dxwrapper = NULL;
static volatile DWORD *g_d3d9_source_slot = NULL;
static create9_fn g_create9_original = NULL;
static HMODULE g_native_d3d9 = NULL;
static volatile LONG g_deferred_attempted = 0;
static FactoryRecord g_factories[MAX_FACTORIES];
static DeviceRecord g_devices[MAX_DEVICES];
static BackbufferRecord g_backbuffers[MAX_BACKBUFFERS];
static volatile LONG g_enabled = 0;
static volatile LONG g_installed = 0;
static DWORD g_serial = 0;
static DWORD g_generation = 1;
static HANDLE g_early_thread = NULL;
static volatile LONG g_early_stop = 0;

void final_d3d9_trace_on_direct_draw_create_ex(void);
static BOOL readable_address(const void *address, DWORD size);
static BOOL inner_header_matches(BYTE *base);
static void log_audit_slots(const char *phase);

static BOOL env_enabled(void)
{
    char value[8];
    DWORD n = GetEnvironmentVariableA(TRACE_ENV, value, sizeof(value));
    return n == 1u && value[0] == '1';
}

static BOOL audit_only_enabled(void)
{
    char value[8];
    DWORD n = GetEnvironmentVariableA(AUDIT_ENV, value, sizeof(value));
    return n == 1u && value[0] == '1';
}

static BOOL cache_cas_enabled(void)
{
    char value[8];
    DWORD n = GetEnvironmentVariableA(CACHE_CAS_ENV, value, sizeof(value));
    return n == 1u && value[0] == '1';
}

static BOOL early_cache_slots_ready(void)
{
    HMODULE module = GetModuleHandleA(DXWRAPPER_NAME); BYTE *base;
    volatile DWORD *source,*cache,*factory,*device;
    if(!module) return FALSE;
    base=(BYTE *)(ULONG_PTR)module;
    source=(volatile DWORD *)(base+D3D9_SOURCE_RVA); cache=(volatile DWORD *)(base+D3D9_CACHE_RVA);
    factory=(volatile DWORD *)(base+D3D9_FACTORY_RVA); device=(volatile DWORD *)(base+D3D9_DEVICE_RVA);
    if(!readable_address((const void *)source,4u) || !readable_address((const void *)cache,4u) || !readable_address((const void *)factory,4u) || !readable_address((const void *)device,4u)) return FALSE;
    return *source != 0u && *cache != 0u && *source == *cache && *factory == 0u && *device == 0u;
}

static BOOL early_audit_slots_ready(void)
{
    HMODULE module = GetModuleHandleA(DXWRAPPER_NAME); BYTE *base;
    volatile DWORD *factory,*device,*inner_source;
    if(!module) return FALSE;
    base=(BYTE *)(ULONG_PTR)module;
    factory=(volatile DWORD *)(base+D3D9_FACTORY_RVA); device=(volatile DWORD *)(base+D3D9_DEVICE_RVA);
    inner_source=(volatile DWORD *)(base+D3D9_INNER_SOURCE_RVA);
    if(!readable_address((const void *)factory,4u) || !readable_address((const void *)device,4u) ||
       !readable_address((const void *)inner_source,4u) || !inner_header_matches(base)) return FALSE;
    return *factory == 0u && *device == 0u && *inner_source != 0u;
}

static DWORD WINAPI early_cache_probe_thread(LPVOID unused)
{
    DWORD attempts;
    (void)unused;
    for(attempts=0u; attempts<6000u && !g_early_stop; ++attempts){
        if(audit_only_enabled()){
            if(early_audit_slots_ready()){ log_audit_slots("early"); return 0u; }
        } else if(early_cache_slots_ready()){
            final_d3d9_trace_on_direct_draw_create_ex(); return 0u;
        }
        Sleep(1u);
    }
    return 0u;
}

static BOOL wine_rebased_header_enabled(void)
{
    char value[8];
    DWORD n = GetEnvironmentVariableA(WINE_REBASED_ENV, value, sizeof(value));
    return n == 1u && value[0] == '1';
}

static void json_write(const char *line)
{
    DWORD len, wrote;
    if (g_log == INVALID_HANDLE_VALUE || !line) return;
    len = lstrlenA(line);
    if (!WriteFile(g_log, line, len, &wrote, NULL) || wrote != len) return;
    FlushFileBuffers(g_log);
}

static void log_install(const char *status, const char *reason, DWORD rva, void *target)
{
    char line[1600], path[260]; DWORD n, i;
    if (g_dxwrapper) {
        n=GetModuleFileNameA(g_dxwrapper,path,sizeof(path)-1u);
        if(!n || n>=sizeof(path)) lstrcpyA(path,"unknown");
        else { path[n]=0; for(i=0;i<n;++i) if(path[i]=='\\') path[i]='/'; }
    } else lstrcpyA(path,"not_loaded");
    wsprintfA(line, "{\"schema\":\"final-d3d9-trace-v2\",\"event\":\"install\",\"status\":\"%s\",\"reason\":\"%s\",\"module\":\"%s\",\"module_base\":\"0x%08X\",\"module_path\":\"%s\",\"module_sha256_external_pin\":\"%s\",\"module_sha256_verified\":\"external_manifest_required\",\"module_version_pin\":\"%s\",\"module_timestamp\":%u,\"module_image_size\":%u,\"rva\":\"0x%08X\",\"target\":\"0x%08X\"}\n", status, reason ? reason : "", DXWRAPPER_NAME, (unsigned)(ULONG_PTR)g_dxwrapper, path, DXWRAPPER_SHA256, DXWRAPPER_VERSION, (unsigned)DXWRAPPER_TIMESTAMP, (unsigned)DXWRAPPER_IMAGE_SIZE, (unsigned)rva, (unsigned)(ULONG_PTR)target);
    json_write(line);
}

static void log_skip(const char *kind, const char *reason, void *object, DWORD caller)
{
    char line[900];
    wsprintfA(line, "{\"schema\":\"final-d3d9-trace-v1\",\"event\":\"structured_skip\",\"kind\":\"%s\",\"reason\":\"%s\",\"object\":\"0x%08X\",\"caller\":\"0x%08X\"}\n", kind, reason, (unsigned)(ULONG_PTR)object, (unsigned)caller);
    json_write(line);
}

static void log_factory(const char *kind, void *factory, HRESULT hr, DWORD caller)
{
    char line[768];
    wsprintfA(line, "{\"schema\":\"final-d3d9-trace-v1\",\"event\":\"%s\",\"factory\":\"0x%08X\",\"hresult\":%ld,\"caller\":\"0x%08X\"}\n", kind, (unsigned)(ULONG_PTR)factory, (long)hr, (unsigned)caller);
    json_write(line);
}

static void log_device(const char *kind, void *device, HRESULT hr, const D3DPRESENT_PARAMETERS *pp, DWORD generation, DWORD caller)
{
    char line[1800];
    DWORD w = pp ? pp->BackBufferWidth : 0u, h = pp ? pp->BackBufferHeight : 0u;
    DWORD fmt = pp ? (DWORD)pp->BackBufferFormat : 0u;
    DWORD hwnd = pp ? (DWORD)(ULONG_PTR)pp->hDeviceWindow : 0u;
    DWORD flags = pp ? pp->Flags : 0u;
    DWORD count = pp ? pp->BackBufferCount : 0u;
    DWORD win = pp ? (DWORD)pp->Windowed : 0u;
    wsprintfA(line, "{\"schema\":\"final-d3d9-trace-v1\",\"event\":\"%s\",\"device\":\"0x%08X\",\"generation\":%u,\"hresult\":%ld,\"present_params\":{\"width\":%u,\"height\":%u,\"format\":%u,\"backbuffer_count\":%u,\"windowed\":%u,\"flags\":%u,\"hwnd\":\"0x%08X\"},\"caller\":\"0x%08X\"}\n", kind, (unsigned)(ULONG_PTR)device, (unsigned)generation, (long)hr, (unsigned)w, (unsigned)h, (unsigned)fmt, (unsigned)count, (unsigned)win, (unsigned)flags, (unsigned)hwnd, (unsigned)caller);
    json_write(line);
}

static void log_backbuffer(IDirect3DSurface9 *surface, HRESULT hr, HRESULT desc_hr, const D3DSURFACE_DESC *desc, DWORD generation, DWORD caller)
{
    char line[1400];
    DWORD w = desc ? desc->Width : 0u, h = desc ? desc->Height : 0u, fmt = desc ? (DWORD)desc->Format : 0u;
    DWORD usage = desc ? desc->Usage : 0u, pool = desc ? (DWORD)desc->Pool : 0u;
    wsprintfA(line, "{\"schema\":\"final-d3d9-trace-v1\",\"event\":\"get_back_buffer\",\"backbuffer\":\"0x%08X\",\"generation\":%u,\"hresult\":%ld,\"get_desc_hresult\":%ld,\"get_desc\":{\"width\":%u,\"height\":%u,\"format\":%u,\"usage\":%u,\"pool\":%u},\"caller\":\"0x%08X\"}\n", (unsigned)(ULONG_PTR)surface, (unsigned)generation, (long)hr, (long)desc_hr, (unsigned)w, (unsigned)h, (unsigned)fmt, (unsigned)usage, (unsigned)pool, (unsigned)caller);
    json_write(line);
}

static void log_present(IDirect3DDevice9 *device, HRESULT hr, DWORD generation, const D3DVIEWPORT9 *viewport, HRESULT viewport_hr, DWORD caller)
{
    char line[1200];
    DWORD serial = ++g_serial;
    DWORD x = viewport ? viewport->X : 0u, y = viewport ? viewport->Y : 0u;
    DWORD w = viewport ? viewport->Width : 0u, h = viewport ? viewport->Height : 0u;
    DWORD minz = viewport ? (DWORD)(viewport->MinZ * 1000000.0f) : 0u;
    DWORD maxz = viewport ? (DWORD)(viewport->MaxZ * 1000000.0f) : 0u;
    wsprintfA(line, "{\"schema\":\"final-d3d9-trace-v1\",\"event\":\"present\",\"serial\":%u,\"device\":\"0x%08X\",\"generation\":%u,\"present_hresult\":%ld,\"viewport_hresult\":%ld,\"viewport\":{\"x\":%u,\"y\":%u,\"width\":%u,\"height\":%u,\"minz_millionths\":%u,\"maxz_millionths\":%u},\"caller\":\"0x%08X\"}\n", (unsigned)serial, (unsigned)(ULONG_PTR)device, (unsigned)generation, (long)hr, (long)viewport_hr, (unsigned)x, (unsigned)y, (unsigned)w, (unsigned)h, (unsigned)minz, (unsigned)maxz, (unsigned)caller);
    json_write(line);
}

static FactoryRecord *find_factory(IDirect3D9 *object)
{
    DWORD i; for (i=0; i<MAX_FACTORIES; ++i) if (g_factories[i].active && g_factories[i].object == object) return &g_factories[i]; return NULL;
}
static DeviceRecord *find_device(IDirect3DDevice9 *object)
{
    DWORD i; for (i=0; i<MAX_DEVICES; ++i) if (g_devices[i].active && g_devices[i].object == object) return &g_devices[i]; return NULL;
}

static BOOL readable_address(const void *address, DWORD size)
{
    MEMORY_BASIC_INFORMATION mbi;
    if (!address || !VirtualQuery(address,&mbi,sizeof(mbi))) return FALSE;
    if (mbi.State != MEM_COMMIT || (mbi.Protect & (PAGE_NOACCESS|PAGE_GUARD))) return FALSE;
    return (BYTE *)address + size >= (BYTE *)address &&
           (BYTE *)address + size <= (BYTE *)mbi.BaseAddress + mbi.RegionSize;
}

static void log_header_observation(HMODULE module)
{
    char line[1500], path[260]; BYTE *base=(BYTE *)(ULONG_PTR)module; IMAGE_DOS_HEADER *dos; IMAGE_NT_HEADERS *nt; DWORD e_lfanew=0, image_base=0, timestamp=0, image_size=0, source=0, guard=0, cache=0, n, i;
    if(module){
        n=GetModuleFileNameA(module,path,sizeof(path)-1u);
        if(!n || n>=sizeof(path)) lstrcpyA(path,"unknown");
        else { path[n]=0; for(i=0;i<n;++i) if(path[i]=='\\') path[i]='/'; }
        if(readable_address(base,sizeof(IMAGE_DOS_HEADER))){
            dos=(IMAGE_DOS_HEADER *)base; e_lfanew=(DWORD)dos->e_lfanew;
            if(e_lfanew<=DXWRAPPER_IMAGE_SIZE-sizeof(IMAGE_NT_HEADERS) && readable_address(base+e_lfanew,sizeof(IMAGE_NT_HEADERS))){
                nt=(IMAGE_NT_HEADERS *)(base+e_lfanew); image_base=nt->OptionalHeader.ImageBase; timestamp=nt->FileHeader.TimeDateStamp; image_size=nt->OptionalHeader.SizeOfImage;
            }
        }
        if(readable_address(base+D3D9_CALLSITE_RVA+1u,4u)) source=*(DWORD *)(base+D3D9_CALLSITE_RVA+1u);
        if(readable_address(base+D3D9_CALLSITE_RVA+6u,4u)) guard=*(DWORD *)(base+D3D9_CALLSITE_RVA+6u);
        if(readable_address(base+D3D9_CALLSITE_RVA+11u,4u)) cache=*(DWORD *)(base+D3D9_CALLSITE_RVA+11u);
    } else lstrcpyA(path,"not_loaded");
    wsprintfA(line,"{\"schema\":\"final-d3d9-trace-v2\",\"event\":\"loaded_header_observation\",\"module_base\":\"0x%08X\",\"module_path\":\"%s\",\"e_lfanew\":%u,\"memory_image_base\":\"0x%08X\",\"memory_timestamp\":%u,\"memory_size_of_image\":%u,\"runtime_source_operand\":\"0x%08X\",\"runtime_guard_operand\":\"0x%08X\",\"runtime_cache_operand\":\"0x%08X\"}\n",(unsigned)(ULONG_PTR)module,path,(unsigned)e_lfanew,(unsigned)image_base,(unsigned)timestamp,(unsigned)image_size,(unsigned)source,(unsigned)guard,(unsigned)cache);
    json_write(line);
}

static void log_loader_slots(volatile DWORD *source, volatile DWORD *cache,
                              volatile DWORD *factory, volatile DWORD *device,
                              volatile DWORD *init)
{
    char line[1700];
    wsprintfA(line,
              "{\"schema\":\"final-d3d9-trace-v2\",\"event\":\"loader_slot_observation\",\"source_slot\":\"0x%08X\",\"source_value\":\"0x%08X\",\"cache_slot\":\"0x%08X\",\"cache_value\":\"0x%08X\",\"factory_slot\":\"0x%08X\",\"factory_value\":\"0x%08X\",\"device_slot\":\"0x%08X\",\"device_value\":\"0x%08X\",\"init_guard_slot\":\"0x%08X\",\"init_guard_value\":\"0x%08X\",\"cache_matches_source\":%u,\"factory_empty\":%u,\"device_empty\":%u}\n",
              (unsigned)(ULONG_PTR)source, (unsigned)*source,
              (unsigned)(ULONG_PTR)cache, (unsigned)*cache,
              (unsigned)(ULONG_PTR)factory, (unsigned)*factory,
              (unsigned)(ULONG_PTR)device, (unsigned)*device,
              (unsigned)(ULONG_PTR)init, (unsigned)*init,
              (unsigned)(*cache == *source), (unsigned)(*factory == 0u),
              (unsigned)(*device == 0u));
    json_write(line);
}

static void normalize_path(char *path, DWORD length)
{
    DWORD i;
    for(i=0u; i<length && path[i]; ++i) if(path[i]=='\\') path[i]='/';
}

static BOOL owner_for_value(DWORD value, HMODULE *owner, char *path, DWORD path_size)
{
    HMODULE module=NULL; DWORD n;
    if(!value || !GetModuleHandleExA(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
                                     (LPCSTR)(ULONG_PTR)value,&module) || !module) return FALSE;
    n=GetModuleFileNameA(module,path,path_size-1u);
    if(!n || n>=path_size) return FALSE;
    path[n]=0; normalize_path(path,n); *owner=module; return TRUE;
}

static BOOL inner_header_matches(BYTE *base)
{
    DWORD source_operand, cache_operand;
    if(!readable_address(base+D3D9_INNER_SOURCE_HEADER_RVA,6u) || !readable_address(base+D3D9_INNER_CACHE_HEADER_RVA,6u)) return FALSE;
    source_operand=*(DWORD *)(base+D3D9_INNER_SOURCE_HEADER_RVA+2u);
    cache_operand=*(DWORD *)(base+D3D9_INNER_CACHE_HEADER_RVA+2u);
    return base[D3D9_INNER_SOURCE_HEADER_RVA] == 0xffu && base[D3D9_INNER_SOURCE_HEADER_RVA+1u] == 0x35u &&
           source_operand == (DWORD)(ULONG_PTR)(base+D3D9_INNER_SOURCE_RVA) &&
           base[D3D9_INNER_CACHE_HEADER_RVA] == 0x89u && base[D3D9_INNER_CACHE_HEADER_RVA+1u] == 0x0du &&
           cache_operand == (DWORD)(ULONG_PTR)(base+D3D9_INNER_CACHE_RVA);
}

static void log_audit_slots(const char *phase)
{
    char line[4200], wrapper_path[260], source_path[260], cache_path[260], inner_source_path[260], inner_cache_path[260], factory_path[260], device_path[260], native_path[260];
    HMODULE native_module, owner; BYTE *base; volatile DWORD *source,*cache,*factory,*device,*init,*inner_source,*inner_cache,*inner_guard;
    DWORD source_value=0u,cache_value=0u,factory_value=0u,device_value=0u,init_value=0u,inner_source_value=0u,inner_cache_value=0u,inner_guard_value=0u;
    DWORD source_owner=0u,cache_owner=0u,inner_source_owner=0u,inner_cache_owner=0u,factory_owner=0u,device_owner=0u,native_export=0u,native_owner=0u,n;
    BOOL header_ok=FALSE, native_loaded=FALSE;
    lstrcpyA(wrapper_path,"not_loaded"); lstrcpyA(source_path,"null"); lstrcpyA(cache_path,"null"); lstrcpyA(inner_source_path,"null");
    lstrcpyA(inner_cache_path,"null"); lstrcpyA(factory_path,"null"); lstrcpyA(device_path,"null"); lstrcpyA(native_path,"d3d9_not_loaded");
    base=(BYTE *)(ULONG_PTR)GetModuleHandleA(DXWRAPPER_NAME);
    if(base){
        n=GetModuleFileNameA((HMODULE)(ULONG_PTR)base,wrapper_path,sizeof(wrapper_path)-1u);
        if(n && n<sizeof(wrapper_path)){wrapper_path[n]=0;normalize_path(wrapper_path,n);} else lstrcpyA(wrapper_path,"unknown");
        source=(volatile DWORD *)(base+D3D9_SOURCE_RVA); cache=(volatile DWORD *)(base+D3D9_CACHE_RVA);
        factory=(volatile DWORD *)(base+D3D9_FACTORY_RVA); device=(volatile DWORD *)(base+D3D9_DEVICE_RVA); init=(volatile DWORD *)(base+D3D9_INIT_GUARD_RVA);
        inner_source=(volatile DWORD *)(base+D3D9_INNER_SOURCE_RVA); inner_cache=(volatile DWORD *)(base+D3D9_INNER_CACHE_RVA); inner_guard=(volatile DWORD *)(base+D3D9_INNER_GUARD_RVA);
        if(readable_address((const void *)source,4u)) source_value=*source;
        if(readable_address((const void *)cache,4u)) cache_value=*cache;
        if(readable_address((const void *)factory,4u)) factory_value=*factory;
        if(readable_address((const void *)device,4u)) device_value=*device;
        if(readable_address((const void *)init,4u)) init_value=*init;
        header_ok=inner_header_matches(base);
        if(header_ok){
            if(readable_address((const void *)inner_source,4u)) inner_source_value=*inner_source;
            if(readable_address((const void *)inner_cache,4u)) inner_cache_value=*inner_cache;
            if(readable_address((const void *)inner_guard,4u)) inner_guard_value=*inner_guard;
        }
    }
    native_module=GetModuleHandleA("d3d9.dll");
    if(native_module){
        native_loaded=TRUE; native_export=(DWORD)(ULONG_PTR)GetProcAddress(native_module,"Direct3DCreate9"); native_owner=(DWORD)(ULONG_PTR)native_module;
        n=GetModuleFileNameA(native_module,native_path,sizeof(native_path)-1u);
        if(n && n<sizeof(native_path)){native_path[n]=0;normalize_path(native_path,n);} else lstrcpyA(native_path,"unknown");
    }
    if(owner_for_value(source_value,&owner,source_path,sizeof(source_path))) source_owner=(DWORD)(ULONG_PTR)owner;
    if(owner_for_value(cache_value,&owner,cache_path,sizeof(cache_path))) cache_owner=(DWORD)(ULONG_PTR)owner;
    if(owner_for_value(inner_source_value,&owner,inner_source_path,sizeof(inner_source_path))) inner_source_owner=(DWORD)(ULONG_PTR)owner;
    if(owner_for_value(inner_cache_value,&owner,inner_cache_path,sizeof(inner_cache_path))) inner_cache_owner=(DWORD)(ULONG_PTR)owner;
    if(owner_for_value(factory_value,&owner,factory_path,sizeof(factory_path))) factory_owner=(DWORD)(ULONG_PTR)owner;
    if(owner_for_value(device_value,&owner,device_path,sizeof(device_path))) device_owner=(DWORD)(ULONG_PTR)owner;
    wsprintfA(line,
        "{\"schema\":\"final-d3d9-trace-v3\",\"event\":\"inner_slot_audit\",\"phase\":\"%s\",\"dxwrapper_base\":\"0x%08X\",\"dxwrapper_path\":\"%s\",\"header_gate\":\"%s\",\"source_value\":\"0x%08X\",\"source_owner\":\"0x%08X\",\"source_path\":\"%s\",\"cache_value\":\"0x%08X\",\"cache_owner\":\"0x%08X\",\"cache_path\":\"%s\",\"factory_value\":\"0x%08X\",\"factory_owner\":\"0x%08X\",\"factory_path\":\"%s\",\"device_value\":\"0x%08X\",\"device_owner\":\"0x%08X\",\"device_path\":\"%s\",\"init_guard_value\":%u,\"inner_source_value\":\"0x%08X\",\"inner_source_owner\":\"0x%08X\",\"inner_source_path\":\"%s\",\"inner_cache_value\":\"0x%08X\",\"inner_cache_owner\":\"0x%08X\",\"inner_cache_path\":\"%s\",\"inner_guard_value\":%u,\"native_loaded\":%u,\"native_owner\":\"0x%08X\",\"native_path\":\"%s\",\"native_export\":\"0x%08X\"}\n",
        phase ? phase : "unknown", (unsigned)(ULONG_PTR)base, wrapper_path, header_ok ? "match" : "mismatch",
        (unsigned)source_value,(unsigned)source_owner,source_path,(unsigned)cache_value,(unsigned)cache_owner,cache_path,
        (unsigned)factory_value,(unsigned)factory_owner,factory_path,(unsigned)device_value,(unsigned)device_owner,device_path,
        (unsigned)init_value,(unsigned)inner_source_value,(unsigned)inner_source_owner,inner_source_path,(unsigned)inner_cache_value,(unsigned)inner_cache_owner,inner_cache_path,
        (unsigned)inner_guard_value,(unsigned)native_loaded,(unsigned)native_owner,native_path,(unsigned)native_export);
    json_write(line);
}

static BOOL writable_address(const void *address, DWORD size)
{
    MEMORY_BASIC_INFORMATION mbi; DWORD protect;
    if (!readable_address(address,size) || !VirtualQuery(address,&mbi,sizeof(mbi))) return FALSE;
    protect=mbi.Protect & 0xffu;
    return protect == PAGE_READWRITE || protect == PAGE_WRITECOPY ||
           protect == PAGE_EXECUTE_READWRITE || protect == PAGE_EXECUTE_WRITECOPY;
}

static BOOL has_highlow_reloc(const BYTE *base, const IMAGE_NT_HEADERS *nt, DWORD target_rva)
{
    IMAGE_DATA_DIRECTORY dir=nt->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_BASERELOC];
    BYTE *cursor, *end;
    if(!dir.VirtualAddress || dir.Size < 8u || dir.VirtualAddress >= DXWRAPPER_IMAGE_SIZE || dir.Size > DXWRAPPER_IMAGE_SIZE-dir.VirtualAddress) return FALSE;
    cursor=(BYTE *)base+dir.VirtualAddress; end=cursor+dir.Size;
    if(!readable_address(cursor,dir.Size)) return FALSE;
    while(cursor+8u<=end){
        DWORD page, block_size, count, i;
        WORD *entries;
        if(!readable_address(cursor,8u)) return FALSE;
        page=*(DWORD *)cursor; block_size=*(DWORD *)(cursor+4u);
        if(block_size<8u || block_size>DXWRAPPER_IMAGE_SIZE || cursor+block_size>end) return FALSE;
        if(!readable_address(cursor,block_size)) return FALSE;
        count=(block_size-8u)/2u; entries=(WORD *)(cursor+8u);
        for(i=0;i<count;++i) if((entries[i]>>12)==IMAGE_REL_BASED_HIGHLOW && page+(entries[i]&0x0fffu)==target_rva) return TRUE;
        cursor+=block_size;
    }
    return FALSE;
}

static BOOL h2_callsite_shape(const BYTE *base, const IMAGE_NT_HEADERS *nt)
{
    BYTE actual[D3D9_CALLSITE_LEN]; DWORD i, delta, source_abs, guard_abs, cache_abs;
    for(i=0;i<D3D9_CALLSITE_LEN;++i) actual[i]=base[D3D9_CALLSITE_RVA+i];
    source_abs=*(DWORD *)(actual+1u); guard_abs=*(DWORD *)(actual+6u); cache_abs=*(DWORD *)(actual+11u);
    delta=(DWORD)(ULONG_PTR)base-DXWRAPPER_IMAGE_BASE;
    /* Only the three verified HIGHLOW operands receive ASLR normalization. */
    if(source_abs-D3D9_SOURCE_ABS!=delta || guard_abs-D3D9_INIT_GUARD_ABS!=delta || cache_abs-D3D9_CACHE_ABS!=delta) return FALSE;
    if(!has_highlow_reloc(base,nt,D3D9_CALLSITE_RVA+1u) || !has_highlow_reloc(base,nt,D3D9_CALLSITE_RVA+6u) || !has_highlow_reloc(base,nt,D3D9_CALLSITE_RVA+11u)) return FALSE;
    for(i=0;i<D3D9_CALLSITE_LEN;++i) if((i<1u || i>4u) && (i<6u || i>9u) && (i<11u || i>14u) && actual[i]!=d3d9_callsite_shape[i]) return FALSE;
    return TRUE;
}

/* H2 waits until dxwrapper has run its native D3D9 loader. */
static BOOL module_pinned_h2(HMODULE module, const char **reason)
{
    IMAGE_DOS_HEADER *dos; IMAGE_NT_HEADERS *nt; BYTE *base;
    if (!module) { *reason="dxwrapper_not_loaded"; return FALSE; }
    base=(BYTE *)(ULONG_PTR)module; dos=(IMAGE_DOS_HEADER *)base;
    if (!readable_address(dos,sizeof(*dos)) || dos->e_magic != IMAGE_DOS_SIGNATURE) { *reason="bad_dos_header"; return FALSE; }
    if (dos->e_lfanew < 0 || (DWORD)dos->e_lfanew > DXWRAPPER_IMAGE_SIZE-sizeof(IMAGE_NT_HEADERS)) { *reason="bad_pe32_identity"; return FALSE; }
    nt=(IMAGE_NT_HEADERS *)(base+dos->e_lfanew);
    if (!readable_address(nt,sizeof(*nt)) || nt->Signature != IMAGE_NT_SIGNATURE || nt->FileHeader.Machine != IMAGE_FILE_MACHINE_I386 || nt->OptionalHeader.Magic != IMAGE_NT_OPTIONAL_HDR32_MAGIC) { *reason="bad_pe32_identity"; return FALSE; }
    if (wine_rebased_header_enabled()) {
        /* Wine may rewrite these header fields in memory; this opt-in branch
         * accepts only the observed loaded-base/e_lfanew pair, never the
         * native-preferred header as a fallback. */
        if (nt->OptionalHeader.ImageBase != (DWORD)(ULONG_PTR)module || dos->e_lfanew != WINE_REBASED_E_LFANEW) { *reason="wine_rebased_header_mismatch"; return FALSE; }
    } else if (nt->OptionalHeader.ImageBase != DXWRAPPER_IMAGE_BASE) {
        *reason="preferred_image_base_mismatch"; return FALSE;
    }
    if (nt->FileHeader.TimeDateStamp != DXWRAPPER_TIMESTAMP || nt->OptionalHeader.SizeOfImage != DXWRAPPER_IMAGE_SIZE) { *reason="timestamp_or_image_size_mismatch"; return FALSE; }
    if (!readable_address(base+D3D9_CALLSITE_RVA,D3D9_CALLSITE_LEN) || !h2_callsite_shape(base,nt)) { *reason="native_loader_callshape_or_relocation_mismatch"; return FALSE; }
    *reason=wine_rebased_header_enabled() ? "ok_wine_rebased_header" : "ok_native_preferred_header"; return TRUE;
}

static BOOL native_owner_for(void *function, HMODULE *owner, char *path, DWORD path_size)
{
    HMODULE module = NULL; DWORD n;
    if (!function || !GetModuleHandleExA(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,(LPCSTR)function,&module) || !module) return FALSE;
    if (module != GetModuleHandleA("d3d9.dll")) return FALSE;
    if ((void *)GetProcAddress(module,"Direct3DCreate9") != function) return FALSE;
    n=GetModuleFileNameA(module,path,path_size-1u);
    if (!n || n>=path_size) return FALSE;
    path[n]=0; *owner=module; return TRUE;
}

static ULONG WINAPI hook_factory_release(IDirect3D9 *object);
static HRESULT WINAPI hook_factory_create_device(IDirect3D9 *object, UINT adapter, D3DDEVTYPE type, HWND hwnd, DWORD flags, D3DPRESENT_PARAMETERS *pp, IDirect3DDevice9 **device);

static BOOL clone_factory(IDirect3D9 *object, FactoryRecord **out)
{
    FactoryRecord *r; DWORD i,count=17u; void **clone;
    if (!object || !object->lpVtbl || find_factory(object)) return FALSE;
    for (i=0;i<MAX_FACTORIES;++i)
        if (InterlockedCompareExchange((volatile LONG *)&g_factories[i].allocated,1,0)==0) break;
    if (i==MAX_FACTORIES) return FALSE;
    clone=(void **)HeapAlloc(GetProcessHeap(),HEAP_ZERO_MEMORY,count*sizeof(void *)); if (!clone) return FALSE;
    for (DWORD j=0;j<count;++j) clone[j]=((void **)object->lpVtbl)[j];
    r=&g_factories[i]; r->object=object; r->old_vtable=(void **)object->lpVtbl; r->clone_vtable=clone; r->vtable_count=count; r->active=TRUE;
    r->create_device=(factory_create_device_fn)clone[16]; r->release=(factory_release_fn)clone[2];
    /* Complete callback slots before publishing the cloned vtable. */
    clone[2]=(void *)hook_factory_release; clone[16]=(void *)hook_factory_create_device;
    object->lpVtbl=(IDirect3D9Vtbl *)clone;
    *out=r; return TRUE;
}

static void observe_backbuffer(DeviceRecord *r, DWORD caller)
{
    IDirect3DSurface9 *surface = NULL; D3DSURFACE_DESC desc; HRESULT get_hr, desc_hr = D3DERR_INVALIDCALL;
    if(!r || !r->active || !r->usable || !r->get_backbuffer || !r->object) return;
    ZeroMemory(&desc,sizeof(desc));
    get_hr=r->get_backbuffer(r->object,0u,0u,D3DBACKBUFFER_TYPE_MONO,&surface);
    if(SUCCEEDED(get_hr) && surface && surface->lpVtbl) {
        desc_hr=surface->lpVtbl->GetDesc(surface,&desc);
        /* Balance only this observer-owned extra GetBackBuffer reference. */
        surface->lpVtbl->Release(surface);
    }
    log_backbuffer(surface,get_hr,desc_hr,&desc,r->generation,caller);
}

static HRESULT WINAPI hook_device_present(IDirect3DDevice9 *device, const RECT *src, const RECT *dst, HWND window, const RGNDATA *dirty)
{
    DeviceRecord *r=find_device(device); HRESULT hr; DWORD caller=(DWORD)(ULONG_PTR)__builtin_return_address(0); D3DVIEWPORT9 viewport; HRESULT viewport_hr=D3DERR_INVALIDCALL;
    if(!r || !r->present) return D3DERR_INVALIDCALL;
    ZeroMemory(&viewport,sizeof(viewport));
    hr=r->present(device,src,dst,window,dirty);
    /* A lost/failed Present is not a usable-device observation boundary. */
    if(SUCCEEDED(hr) && r->usable) {
        if(r->get_viewport) viewport_hr=r->get_viewport(device,&viewport);
        observe_backbuffer(r, caller);
    }
    log_present(device,hr,r->generation,&viewport,viewport_hr,caller); return hr;
}
static HRESULT WINAPI hook_device_reset(IDirect3DDevice9 *device, D3DPRESENT_PARAMETERS *pp)
{
    DeviceRecord *r=find_device(device); HRESULT hr; DWORD caller=(DWORD)(ULONG_PTR)__builtin_return_address(0);
    if(!r || !r->reset) return D3DERR_INVALIDCALL;
    hr=r->reset(device,pp);
    if(SUCCEEDED(hr)){
        r->usable=TRUE;
        ++g_generation; r->generation=g_generation;
        for(DWORD i=0;i<MAX_BACKBUFFERS;++i) g_backbuffers[i].active=FALSE;
    } else {
        r->usable=FALSE;
    }
    log_device("reset",device,hr,pp,r->generation,caller); return hr;
}
static ULONG WINAPI hook_device_release(IDirect3DDevice9 *device);

static BOOL clone_device(IDirect3DDevice9 *object, DeviceRecord **out)
{
    DeviceRecord *r; DWORD i,count=119u; void **clone;
    if (!object || !object->lpVtbl || find_device(object)) return FALSE;
    for(i=0;i<MAX_DEVICES;++i)
        if (InterlockedCompareExchange((volatile LONG *)&g_devices[i].allocated,1,0)==0) break;
    if(i==MAX_DEVICES) return FALSE;
    clone=(void **)HeapAlloc(GetProcessHeap(),HEAP_ZERO_MEMORY,count*sizeof(void *)); if(!clone) return FALSE;
    for(DWORD j=0;j<count;++j) clone[j]=((void **)object->lpVtbl)[j];
    r=&g_devices[i]; r->object=object; r->old_vtable=(void **)object->lpVtbl; r->clone_vtable=clone; r->vtable_count=count; r->generation=g_generation; r->active=TRUE; r->usable=TRUE;
    r->present=(device_present_fn)clone[17]; r->reset=(device_reset_fn)clone[16]; r->get_backbuffer=(device_backbuffer_fn)clone[18]; r->get_viewport=(device_get_viewport_fn)clone[48]; r->release=(device_release_fn)clone[2];
    clone[16]=(void *)hook_device_reset; clone[17]=(void *)hook_device_present; clone[2]=(void *)hook_device_release;
    object->lpVtbl=(IDirect3DDevice9Vtbl *)clone; *out=r; return TRUE;
}

static ULONG WINAPI hook_factory_release(IDirect3D9 *object)
{
    FactoryRecord *r=find_factory(object); ULONG value;
    if(!r || !r->release) return 0u;
    value=r->release(object);
    if(value==0u){
        /* Final Release may have freed object: do not dereference or free callback storage. */
        r->active=FALSE; r->object=NULL;
    }
    return value;
}

static HRESULT WINAPI hook_factory_create_device(IDirect3D9 *object, UINT adapter, D3DDEVTYPE type, HWND hwnd, DWORD flags, D3DPRESENT_PARAMETERS *pp, IDirect3DDevice9 **device)
{
    FactoryRecord *r=find_factory(object); HRESULT hr; DeviceRecord *d; DWORD caller=(DWORD)(ULONG_PTR)__builtin_return_address(0);
    if(!r || !r->create_device) return E_FAIL;
    hr=r->create_device(object,adapter,type,hwnd,flags,pp,device); log_factory("factory_create_device",object,hr,caller);
    if(SUCCEEDED(hr) && device && *device && clone_device(*device,&d)) { log_device("create_device",*device,hr,pp,d->generation,caller); observe_backbuffer(d,caller); }
    else if(SUCCEEDED(hr) && device && *device) log_skip("create_device", "lifetime_or_vtable_capacity", *device, caller);
    return hr;
}

static ULONG WINAPI hook_device_release(IDirect3DDevice9 *device)
{
    DeviceRecord *r=find_device(device); ULONG value;
    if(!r || !r->release) return 0u;
    value=r->release(device);
    if(value==0u){
        /* Final Release may have freed object: do not dereference or free callback storage. */
        r->active=FALSE; r->object=NULL;
    }
    return value;
}

static IDirect3D9 *WINAPI hook_create9(UINT sdk)
{
    create9_fn original=g_create9_original; IDirect3D9 *object; FactoryRecord *r; DWORD caller=(DWORD)(ULONG_PTR)__builtin_return_address(0);
    if(!original) return NULL;
    object=original(sdk);
    if(object && clone_factory(object,&r)){ log_factory("factory_create9",object,S_OK,caller); }
    else if(object) log_skip("factory_create9", "com_alias_or_lifetime", object, caller);
    return object;
}

static void log_binding(volatile DWORD *source, volatile DWORD *cache, volatile DWORD *factory, volatile DWORD *device, volatile DWORD *init, void *native, HMODULE owner, const char *native_path, const char *hook_slot_kind, volatile DWORD *hook_slot)
{
    char line[1900], path[260]; DWORD n, i;
    n=GetModuleFileNameA(g_dxwrapper,path,sizeof(path)-1u);
    if(!n || n>=sizeof(path)) lstrcpyA(path,"unknown");
    else { path[n]=0; for(i=0;i<n;++i) if(path[i]=='\\') path[i]='/'; }
    wsprintfA(line,"{\"schema\":\"final-d3d9-trace-v2\",\"event\":\"native_binding\",\"status\":\"active\",\"header_policy\":\"%s\",\"dxwrapper_base\":\"0x%08X\",\"dxwrapper_path\":\"%s\",\"source_slot\":\"0x%08X\",\"cache_slot\":\"0x%08X\",\"factory_slot\":\"0x%08X\",\"device_slot\":\"0x%08X\",\"init_guard_slot\":\"0x%08X\",\"init_guard_value\":%u,\"hook_slot_kind\":\"%s\",\"hook_slot\":\"0x%08X\",\"native_owner\":\"0x%08X\",\"native_path\":\"%s\",\"native_export\":\"0x%08X\",\"forward_target\":\"0x%08X\"}\n",wine_rebased_header_enabled() ? "wine_rebased_loaded_base" : "native_preferred_image_base",(unsigned)(ULONG_PTR)g_dxwrapper,path,(unsigned)(ULONG_PTR)source,(unsigned)(ULONG_PTR)cache,(unsigned)(ULONG_PTR)factory,(unsigned)(ULONG_PTR)device,(unsigned)(ULONG_PTR)init,(unsigned)*init,hook_slot_kind ? hook_slot_kind : "unknown",(unsigned)(ULONG_PTR)hook_slot,(unsigned)(ULONG_PTR)owner,native_path ? native_path : "unknown",(unsigned)(ULONG_PTR)GetProcAddress(owner,"Direct3DCreate9"),(unsigned)(ULONG_PTR)native);
    json_write(line);
}

int final_d3d9_trace_install(void)
{
    if(!env_enabled()) return 1;
    InterlockedExchange(&g_enabled,1);
    g_log=CreateFileA(TRACE_PATH,GENERIC_WRITE,FILE_SHARE_READ|FILE_SHARE_WRITE,NULL,CREATE_ALWAYS,FILE_ATTRIBUTE_NORMAL,NULL);
    if(g_log==INVALID_HANDLE_VALUE) return 1;
    log_install("pending","deferred_native_d3d9_after_directdraw_create_ex",0u,NULL);
    if(cache_cas_enabled() || audit_only_enabled()){
        InterlockedExchange(&g_early_stop,0);
        g_early_thread=CreateThread(NULL,0,early_cache_probe_thread,NULL,0,NULL);
        if(g_early_thread) log_install("pending",audit_only_enabled() ? "early_inner_audit_probe_started" : "early_cache_cas_probe_started",D3D9_CACHE_RVA,NULL);
        else log_install("skip",audit_only_enabled() ? "early_inner_audit_probe_thread_create_failed" : "early_cache_cas_probe_thread_create_failed",D3D9_CACHE_RVA,NULL);
    }
    return 1;
}

void final_d3d9_trace_on_direct_draw_create_ex(void)
{
    const char *reason; BYTE *base; volatile DWORD *source,*cache,*factory,*device,*init; DWORD old; void *native;
    HMODULE owner; char path[260];
    if(!g_enabled || InterlockedCompareExchange(&g_deferred_attempted,1,0)!=0) return;
    g_dxwrapper=GetModuleHandleA(DXWRAPPER_NAME);
    log_header_observation(g_dxwrapper);
    if(audit_only_enabled()){
        base=(BYTE *)(ULONG_PTR)g_dxwrapper;
        source=(volatile DWORD *)(base+D3D9_SOURCE_RVA); cache=(volatile DWORD *)(base+D3D9_CACHE_RVA);
        factory=(volatile DWORD *)(base+D3D9_FACTORY_RVA); device=(volatile DWORD *)(base+D3D9_DEVICE_RVA); init=(volatile DWORD *)(base+D3D9_INIT_GUARD_RVA);
        if(readable_address((const void *)source,4u) && readable_address((const void *)cache,4u) && readable_address((const void *)factory,4u) && readable_address((const void *)device,4u) && readable_address((const void *)init,4u)) log_loader_slots(source,cache,factory,device,init);
        log_audit_slots("late");
        log_install("audit_only","header_observation_only_no_cas",0u,NULL);return;
    }
    if(!module_pinned_h2(g_dxwrapper,&reason)){log_install("skip",reason,D3D9_CALLSITE_RVA,NULL);return;}
    base=(BYTE *)(ULONG_PTR)g_dxwrapper;
    source=(volatile DWORD *)(base+D3D9_SOURCE_RVA); cache=(volatile DWORD *)(base+D3D9_CACHE_RVA);
    factory=(volatile DWORD *)(base+D3D9_FACTORY_RVA); device=(volatile DWORD *)(base+D3D9_DEVICE_RVA); init=(volatile DWORD *)(base+D3D9_INIT_GUARD_RVA);
    if(!readable_address((const void *)source,4u) || !readable_address((const void *)cache,4u) || !readable_address((const void *)factory,4u) || !readable_address((const void *)device,4u) || !readable_address((const void *)init,4u)){log_install("skip","loader_slots_unreadable",D3D9_SOURCE_RVA,NULL);return;}
    log_loader_slots(source,cache,factory,device,init);
    if(cache_cas_enabled()){
        if(*init == 0u){log_install("skip","cache_cas_requires_completed_initialization",D3D9_INIT_GUARD_RVA,(void *)(ULONG_PTR)*init);return;}
        if(*factory || *device){log_install("skip","cache_cas_loader_surface_already_created",D3D9_FACTORY_RVA,(void *)(ULONG_PTR)(*factory ? *factory : *device));return;}
        if(!*source || !*cache || *cache != *source){log_install("skip","cache_cas_source_cache_mismatch",D3D9_CACHE_RVA,(void *)(ULONG_PTR)*cache);return;}
        native=(void *)(ULONG_PTR)*cache;
        if(!native || !native_owner_for(native,&owner,path,sizeof(path)) || owner==g_dxwrapper){log_install("skip","cache_cas_native_d3d9_owner_or_export_mismatch",D3D9_CACHE_RVA,native);return;}
        for(old=0;old<sizeof(path);++old) if(path[old]=='\\') path[old]='/';
        if(!writable_address((const void *)cache,4u)){log_install("skip","cache_slot_not_writable",D3D9_CACHE_RVA,native);return;}
        g_native_d3d9=owner; g_create9_original=(create9_fn)native;
        old=(DWORD)(ULONG_PTR)InterlockedCompareExchangePointer((PVOID *)cache,(PVOID)hook_create9,native);
        if((void *)(ULONG_PTR)old != native){g_create9_original=NULL;log_install("skip","cache_cas_mismatch",D3D9_CACHE_RVA,native);return;}
        g_d3d9_source_slot=cache;
        log_binding(source,cache,factory,device,init,native,owner,path,"cache",cache);
        return;
    }
    /* _Init_thread_header leaves zero in the pristine state; -1 means initializing. */
    if(*init != 0u){log_install("skip","loader_initialization_guard_not_pristine",D3D9_INIT_GUARD_RVA,(void *)(ULONG_PTR)*init);return;}
    if(*cache || *factory || *device){log_install("skip","loader_slots_not_empty",D3D9_SOURCE_RVA,(void *)(ULONG_PTR)*source);return;}
    native=(void *)(ULONG_PTR)*source;
    if(!native || !native_owner_for(native,&owner,path,sizeof(path)) || owner==g_dxwrapper){log_install("skip","native_d3d9_owner_or_export_mismatch",D3D9_SOURCE_RVA,native);return;}
    for(old=0;old<sizeof(path);++old) if(path[old]=='\\') path[old]='/';
    if(!writable_address((const void *)source,4u)){log_install("skip","native_source_slot_not_writable",D3D9_SOURCE_RVA,native);return;}
    g_native_d3d9=owner; g_create9_original=(create9_fn)native;
    old=(DWORD)(ULONG_PTR)InterlockedCompareExchangePointer((PVOID *)source,(PVOID)hook_create9,native);
    if((void *)(ULONG_PTR)old != native){g_create9_original=NULL;log_install("skip","native_source_cas_mismatch",D3D9_SOURCE_RVA,native);return;}
    g_d3d9_source_slot=source;
    log_binding(source,cache,factory,device,init,native,owner,path,"source",source);
}

void final_d3d9_trace_detach(void)
{
    if(!g_enabled) return;
    /* Do not restore source slot or touch COM objects: native cache may retain our hook. */
    InterlockedExchange(&g_early_stop,1);
    if(g_early_thread){WaitForSingleObject(g_early_thread,2000u);CloseHandle(g_early_thread);g_early_thread=NULL;}
    if(g_log!=INVALID_HANDLE_VALUE){CloseHandle(g_log);g_log=INVALID_HANDLE_VALUE;}
    g_enabled=0;
}
