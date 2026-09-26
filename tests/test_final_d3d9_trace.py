"""Static contracts for the opt-in deferred native-D3D9 boundary tracer."""
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "tools" / "inmm_stub" / "final_d3d9_trace.c"
HEADER = ROOT / "tools" / "inmm_stub" / "final_d3d9_trace.h"
STUB = ROOT / "tools" / "inmm_stub" / "inmm_stub.c"
DDRAW = ROOT / "tools" / "inmm_stub" / "direct_draw_trace.c"
MAKEFILE = ROOT / "tools" / "inmm_stub" / "Makefile"


def source() -> str:
    return SRC.read_text(encoding="utf-8")


def function_body(text: str, name: str) -> str:
    prefix = r"(?m)^void\s+" if name.startswith("final_d3d9_trace_") else r"(?m)^static\s+"
    matches = list(re.finditer(prefix + r"[^\n{};]*\b" + re.escape(name) + r"\s*\([^;{}]*\)\s*\{", text))
    if not matches:
        raise AssertionError(f"function definition not found: {name}")
    opening = matches[-1].end() - 1
    depth = 0
    for index in range(opening, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[opening : index + 1]
    raise AssertionError(f"unterminated function: {name}")


def test_opt_in_and_exact_h2_loader_contract():
    text = source()
    assert '#define TRACE_ENV "INMM_FINAL_D3D9_TRACE"' in text
    assert '#define AUDIT_ENV "INMM_FINAL_D3D9_AUDIT_ONLY"' in text
    assert '#define CACHE_CAS_ENV "INMM_FINAL_D3D9_CACHE_CAS"' in text
    assert '#define WINE_REBASED_ENV "INMM_FINAL_D3D9_WINE_REBASED_HEADER"' in text
    assert "WINE_REBASED_E_LFANEW 296u" in text
    assert '#define DXWRAPPER_SHA256 "96c443193bad8794ebf04738566e092f8b34ae4541cb2433fd0708d49edbe8fe"' in text
    assert "DXWRAPPER_TIMESTAMP 0x60B2E3C1u" in text
    assert "DXWRAPPER_IMAGE_BASE 0x10000000u" in text
    assert "DXWRAPPER_IMAGE_SIZE 0x23C000u" in text
    assert "D3D9_SOURCE_RVA 0x001F17F8u" in text
    assert "D3D9_CACHE_RVA 0x001F23B4u" in text
    assert "D3D9_FACTORY_RVA 0x001F22E0u" in text
    assert "D3D9_DEVICE_RVA 0x001F22E4u" in text
    assert "D3D9_INIT_GUARD_RVA 0x001F23B8u" in text
    assert "D3D9_CALLSITE_RVA 0x000C18C3u" in text
    assert "0xa1,0xf8,0x17,0x1f,0x10" in text
    assert "0xa3,0xb4,0x23,0x1f,0x10" in text
    assert "0x83,0xc4,0x04,0xe9" in text
    assert "has_highlow_reloc" in text
    assert "D3D9_CALLSITE_RVA+1u" in text
    assert "D3D9_CALLSITE_RVA+6u" in text
    assert "D3D9_CALLSITE_RVA+11u" in text
    assert "D3D9_SOURCE_ABS 0x101F17F8u" in text
    assert "source_abs-D3D9_SOURCE_ABS!=delta" in text
    assert "guard_abs-D3D9_INIT_GUARD_ABS!=delta" in text
    assert "cache_abs-D3D9_CACHE_ABS!=delta" in text
    assert "module_sha256_verified" in text
    assert "external_manifest_required" in text
    assert "loaded_header_observation" in text
    assert "memory_image_base" in text and "memory_timestamp" in text
    assert "memory_size_of_image" in text and "e_lfanew" in text
    assert "e_lfanew<=DXWRAPPER_IMAGE_SIZE-sizeof(IMAGE_NT_HEADERS)" in text
    assert "wine_rebased_header_mismatch" in text
    assert "ok_wine_rebased_header" in text and "ok_native_preferred_header" in text
    assert "nt->OptionalHeader.ImageBase != (DWORD)(ULONG_PTR)module" in text
    assert "dos->e_lfanew != WINE_REBASED_E_LFANEW" in text
    assert "IMAGE_NT_OPTIONAL_HDR32_MAGIC" in text
    assert '\\"header_policy\\"' in text
    assert "runtime_source_operand" in text and "runtime_guard_operand" in text
    assert "runtime_cache_operand" in text
    assert "D3D9_INNER_SOURCE_RVA 0x001BAC60u" in text
    assert "D3D9_INNER_CACHE_RVA 0x001BACC0u" in text
    assert "D3D9_INNER_GUARD_RVA 0x001BACC4u" in text
    assert "D3D9_INNER_SOURCE_HEADER_RVA 0x0000A969u" in text
    assert "D3D9_INNER_CACHE_HEADER_RVA 0x0000A992u" in text


def test_no_startup_export_patch_and_deferred_original_success_integration():
    text = source()
    ddraw = DDRAW.read_text(encoding="utf-8")
    assert "patch_target" not in text
    assert "VirtualProtect" not in text
    assert "Direct3DCreate9Ex" not in text
    assert 'log_install("pending","deferred_native_d3d9_after_directdraw_create_ex"' in text
    assert "final_d3d9_trace_on_direct_draw_create_ex();" in ddraw
    success = ddraw.index("if (FAILED(result) || !out || !*out)")
    deferred = ddraw.index("final_d3d9_trace_on_direct_draw_create_ex();")
    assert success < deferred


def test_deferred_gate_is_fail_closed_and_validates_native_owner():
    text = source()
    body = function_body(text, "final_d3d9_trace_on_direct_draw_create_ex")
    assert "InterlockedCompareExchange(&g_deferred_attempted,1,0)" in body
    assert "module_pinned_h2" in body
    assert "WINE_REBASED_ENV" in text
    assert body.index("log_header_observation(g_dxwrapper)") < body.index("audit_only_enabled()") < body.index("module_pinned_h2")
    assert '"header_observation_only_no_cas"' in body
    assert body.index("audit_only_enabled()") < body.index("InterlockedCompareExchangePointer")
    assert "native_loader_callshape_or_relocation_mismatch" in text
    assert "*init != 0u" in body
    assert "loader_initialization_guard_not_pristine" in body
    assert "*cache || *factory || *device" in body
    assert 'GetModuleHandleExA(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS|GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT' in text
    assert 'GetProcAddress(module,"Direct3DCreate9")' in text
    assert "owner==g_dxwrapper" in body
    assert 'GetModuleHandleA("d3d9.dll")' in text
    assert '"loader_slots_not_empty"' in body


def test_a1_slots_are_observed_and_cache_cas_is_explicit_only():
    text = source()
    body = function_body(text, "final_d3d9_trace_on_direct_draw_create_ex")
    slots = function_body(text, "log_loader_slots")
    assert r'\"event\":\"loader_slot_observation\"' in slots
    for field in ("source_value", "cache_value", "factory_value", "device_value", "init_guard_value"):
        assert rf'\"{field}\"' in slots
    assert "cache_matches_source" in slots
    assert body.count("log_loader_slots(source,cache,factory,device,init)") == 2
    assert "cache_cas_enabled()" in body
    assert "cache_cas_requires_completed_initialization" in body
    assert "cache_cas_loader_surface_already_created" in body
    assert "InterlockedCompareExchangePointer((PVOID *)cache,(PVOID)hook_create9,native)" in body
    assert 'log_binding(source,cache,factory,device,init,native,owner,path,"cache",cache)' in body
    assert body.index("cache_cas_enabled()") < body.index("if(*init != 0u)")


def test_default_guard_skip_precedes_default_source_cas_and_cache_path_is_opt_in():
    text = source()
    body = function_body(text, "final_d3d9_trace_on_direct_draw_create_ex")
    default_guard = body.index('"loader_initialization_guard_not_pristine"')
    default_cas = body.index("InterlockedCompareExchangePointer((PVOID *)source,(PVOID)hook_create9,native)")
    cache_gate = body.index("if(cache_cas_enabled())")
    assert cache_gate < default_guard < default_cas
    assert "if(*init != 0u)" in body
    assert "loader_initialization_guard_not_pristine" in body


def test_cache_cas_early_probe_is_bounded_and_stopped_on_detach():
    text = source()
    install_start = text.index("int final_d3d9_trace_install(void)")
    install_end = text.index("\n}\n\nvoid final_d3d9_trace_on_direct_draw_create_ex", install_start) + 2
    install = text[install_start:install_end]
    detach = function_body(text, "final_d3d9_trace_detach")
    probe = function_body(text, "early_cache_probe_thread")
    ready = function_body(text, "early_cache_slots_ready")
    assert "source != 0u" in ready and "*cache != 0u" in ready
    assert "*source == *cache" in ready and "*factory == 0u" in ready and "*device == 0u" in ready
    assert "attempts<6000u" in probe and "Sleep(1u)" in probe
    assert "final_d3d9_trace_on_direct_draw_create_ex();" in probe
    assert "cache_cas_enabled() || audit_only_enabled()" in install
    assert "CreateThread(NULL,0,early_cache_probe_thread" in install
    assert '"early_cache_cas_probe_started"' in install
    assert "InterlockedExchange(&g_early_stop,1)" in detach
    assert "WaitForSingleObject(g_early_thread,2000u)" in detach


def test_inner_audit_has_early_and_late_read_only_boundaries():
    text = source()
    probe = function_body(text, "early_cache_probe_thread")
    audit = function_body(text, "log_audit_slots")
    install_start = text.index("int final_d3d9_trace_install(void)")
    install_end = text.index("\n}\n\nvoid final_d3d9_trace_on_direct_draw_create_ex", install_start) + 2
    install = text[install_start:install_end]
    deferred = function_body(text, "final_d3d9_trace_on_direct_draw_create_ex")
    assert 'log_audit_slots("early")' in probe
    assert 'log_audit_slots("late")' in deferred
    assert r'\"event\":\"inner_slot_audit\"' in audit
    for field in (
        "source_owner", "source_path", "cache_owner", "cache_path",
        "factory_owner", "factory_path", "device_owner", "device_path",
        "inner_source_value", "inner_source_owner", "inner_source_path",
        "inner_cache_value", "inner_cache_owner", "inner_cache_path",
        "inner_guard_value", "native_loaded", "native_path", "native_export",
    ):
        assert field in audit
    assert "inner_header_matches" in audit
    assert "header_gate" in audit
    assert "GetModuleHandleA(\"d3d9.dll\")" in audit
    assert "LoadLibrary" not in audit
    assert "InterlockedCompareExchangePointer" not in audit
    assert "early_inner_audit_probe_started" in install


def test_inner_header_gate_reads_only_pinned_rebased_operands():
    text = source()
    gate = function_body(text, "inner_header_matches")
    assert "base[D3D9_INNER_SOURCE_HEADER_RVA] == 0xffu" in gate
    assert "base[D3D9_INNER_SOURCE_HEADER_RVA+1u] == 0x35u" in gate
    assert "base[D3D9_INNER_CACHE_HEADER_RVA] == 0x89u" in gate
    assert "base[D3D9_INNER_CACHE_HEADER_RVA+1u] == 0x0du" in gate
    assert "source_operand == (DWORD)(ULONG_PTR)(base+D3D9_INNER_SOURCE_RVA)" in gate
    assert "cache_operand == (DWORD)(ULONG_PTR)(base+D3D9_INNER_CACHE_RVA)" in gate
    audit = function_body(text, "log_audit_slots")
    assert "header_ok=inner_header_matches(base)" in audit
    assert "if(header_ok)" in audit


def test_source_slot_cas_publishes_hook_only_for_expected_native_function():
    text = source()
    body = function_body(text, "final_d3d9_trace_on_direct_draw_create_ex")
    assert "g_create9_original=(create9_fn)native" in body
    assert "InterlockedCompareExchangePointer((PVOID *)source,(PVOID)hook_create9,native)" in body
    assert body.index("g_create9_original=(create9_fn)native") < body.index("InterlockedCompareExchangePointer")
    assert "native_source_slot_not_writable" in body
    assert "writable_address((const void *)source,4u)" in body
    assert "native_source_cas_mismatch" in body
    assert "g_create9_original=NULL" in body
    assert "Nativecache" not in text


def test_typed_factory_device_surface_observation_and_no_pixel_writes():
    text = source()
    assert "#include <d3d9.h>" in text
    assert "IDirect3D9Vtbl" in text and "IDirect3DDevice9Vtbl" in text
    assert "factory_create_device_fn" in text
    assert "device_present_fn" in text and "device_reset_fn" in text
    assert "device_backbuffer_fn" in text and "D3DSURFACE_DESC" in text
    assert "clone[16]" in text and "clone[17]" in text and "clone[48]" in text
    assert "CreateTexture" not in text and "LockRect" not in text
    assert "SetRenderTarget" not in text and "UpdateSurface" not in text
    assert "SetPixelShader" not in text
    assert "r->get_backbuffer(r->object,0u,0u,D3DBACKBUFFER_TYPE_MONO,&surface)" in text
    assert "surface->lpVtbl->GetDesc(surface,&desc)" in text
    assert "surface->lpVtbl->Release(surface)" in text
    assert "structured_skip" in text


def test_reset_and_release_lifetime_safety_remain_fail_closed():
    text = source()
    reset = function_body(text, "hook_device_reset")
    present = function_body(text, "hook_device_present")
    detach = function_body(text, "final_d3d9_trace_detach")
    factory_release = function_body(text, "hook_factory_release")
    device_release = function_body(text, "hook_device_release")
    assert "r->usable=FALSE" in reset and "r->usable=TRUE" in reset
    assert "SUCCEEDED(hr) && r->usable" in present
    assert present.index("ZeroMemory(&viewport") < present.index("hr=r->present")
    assert "->lpVtbl" not in detach
    assert "->lpVtbl" not in factory_release and "->lpVtbl" not in device_release
    assert "HeapFree" not in detach and "HeapFree" not in factory_release and "HeapFree" not in device_release
    assert "r->object=NULL" in factory_release and "r->object=NULL" in device_release


def test_process_lifetime_storage_and_atomic_object_slots():
    text = source()
    factory = function_body(text, "clone_factory")
    device = function_body(text, "clone_device")
    detach = function_body(text, "final_d3d9_trace_detach")
    assert "InterlockedCompareExchange" in factory and "InterlockedCompareExchange" in device
    assert factory.index("clone[2]=(void *)hook_factory_release") < factory.index("object->lpVtbl=")
    assert factory.index("clone[16]=(void *)hook_factory_create_device") < factory.index("object->lpVtbl=")
    assert "Keep trampoline storage" not in text
    assert "Do not restore source slot" in detach


def test_dll_header_makefile_integration_and_default_off():
    text = source()
    stub = STUB.read_text(encoding="utf-8")
    makefile = MAKEFILE.read_text(encoding="utf-8")
    header = HEADER.read_text(encoding="utf-8")
    assert "if(!env_enabled()) return 1;" in text
    assert "final_d3d9_trace.h" in stub and "final_d3d9_trace.c" in makefile
    assert "final_d3d9_trace_install" in header
    assert "final_d3d9_trace_on_direct_draw_create_ex" in header
    assert "final_d3d9_trace_detach()" in stub
    assert "FUN_004" not in text and "0x0043F250" not in text


def test_pinned_raw_loader_operands_and_opcode_mutations_are_rejected():
    """Exercise the exact pinned PE bytes/relocations, not only source spelling."""
    import hashlib
    import pytest
    import pefile

    dll = ROOT.parent / "Syw2plus_re" / "Syw2plus" / "dxwrapper.dll"
    if not dll.is_file():
        pytest.skip("pinned dxwrapper.dll asset is unavailable")
    assert hashlib.sha256(dll.read_bytes()).hexdigest() == "96c443193bad8794ebf04738566e092f8b34ae4541cb2433fd0708d49edbe8fe"
    pe = pefile.PE(str(dll))
    image = bytearray(pe.get_memory_mapped_image())
    site = 0xC18C3
    shape = bytes.fromhex(
        "a1 f8 17 1f 10 68 b8 23 1f 10 a3 b4 23 1f 10"
        "e8 b0 62 07 00 83 c4 04 e9 d4 fd ff ff cc"
    )
    assert pe.FILE_HEADER.TimeDateStamp == 0x60B2E3C1
    assert pe.OPTIONAL_HEADER.ImageBase == 0x10000000
    assert pe.OPTIONAL_HEADER.SizeOfImage == 0x23C000
    assert bytes(image[site : site + len(shape)]) == shape
    relocs = {
        entry.rva
        for block in pe.DIRECTORY_ENTRY_BASERELOC
        for entry in block.entries
        if entry.type == pefile.RELOCATION_TYPE["IMAGE_REL_BASED_HIGHLOW"]
    }
    assert {site + 1, site + 6, site + 11} <= relocs

    def accepts(buf: bytearray, loaded_base: int = 0x76FA0000) -> bool:
        actual = bytes(buf[site : site + len(shape)])
        if len(actual) != len(shape):
            return False
        delta = loaded_base - 0x10000000
        if int.from_bytes(actual[1:5], "little") - 0x101F17F8 != delta:
            return False
        if int.from_bytes(actual[6:10], "little") - 0x101F23B8 != delta:
            return False
        if int.from_bytes(actual[11:15], "little") - 0x101F23B4 != delta:
            return False
        return all(
            actual[i] == shape[i] for i in range(len(shape)) if i not in set(range(1, 5)) | set(range(6, 10)) | set(range(11, 15))
        )

    valid = bytearray(shape)
    valid[1:5] = (0x76FA0000 + 0x1F17F8).to_bytes(4, "little")
    valid[6:10] = (0x76FA0000 + 0x1F23B8).to_bytes(4, "little")
    valid[11:15] = (0x76FA0000 + 0x1F23B4).to_bytes(4, "little")
    loaded = bytearray(image)
    loaded[site : site + len(shape)] = valid
    assert accepts(image, 0x10000000)
    assert accepts(loaded)
    for offset in (1, 6, 11, 0, 15, 24):
        broken = bytearray(loaded)
        broken[site + offset] ^= 1
        assert not accepts(broken)


def test_host_gcc_executes_production_loader_verifiers_against_pinned_pe(tmp_path):
    """Compile the production verifier bodies and exercise real PE mutations."""
    import shutil
    import subprocess
    import textwrap

    import pefile
    import pytest

    dll = ROOT.parent / "Syw2plus_re" / "Syw2plus" / "dxwrapper.dll"
    if not dll.is_file() or not shutil.which("gcc"):
        pytest.skip("pinned DLL or host gcc unavailable")
    pe = pefile.PE(str(dll))
    mapped = pe.get_memory_mapped_image()
    harness = tmp_path / "h2_verifier.c"
    exe = tmp_path / "h2_verifier"
    define_names = {"DXWRAPPER_IMAGE_SIZE", "DXWRAPPER_IMAGE_BASE", "DXWRAPPER_TIMESTAMP", "D3D9_SOURCE_RVA", "D3D9_CACHE_RVA", "D3D9_INIT_GUARD_RVA", "D3D9_CALLSITE_RVA", "D3D9_CALLSITE_LEN", "D3D9_SOURCE_ABS", "D3D9_INIT_GUARD_ABS", "D3D9_CACHE_ABS", "WINE_REBASED_ENV", "WINE_REBASED_E_LFANEW"}
    h2_defines = "\n".join(line for line in source().splitlines() if line.startswith("#define ") and line.split()[1] in define_names)
    shape_start = source().index("static const BYTE d3d9_callsite_shape")
    shape_decl = source()[shape_start : source().index("};", shape_start) + 2]
    bodies = (
        "static BOOL wine_rebased_header_enabled(void) "
        + function_body(source(), "wine_rebased_header_enabled")
        + "\nstatic BOOL has_highlow_reloc(const BYTE *base, const IMAGE_NT_HEADERS *nt, DWORD target_rva) "
        + function_body(source(), "has_highlow_reloc")
        + "\nstatic BOOL h2_callsite_shape(const BYTE *base, const IMAGE_NT_HEADERS *nt) "
        + function_body(source(), "h2_callsite_shape")
        + "\nstatic BOOL module_pinned_h2(HMODULE module, const char **reason) "
        + function_body(source(), "module_pinned_h2")
    )
    harness.write_text(
        textwrap.dedent(
            f"""
            #include <stdint.h>
            #include <stdio.h>
            #include <stdlib.h>
            #include <string.h>
            #include <sys/mman.h>
            #include <unistd.h>
            typedef uint8_t BYTE; typedef uint16_t WORD; typedef uint32_t DWORD;
            typedef int BOOL; typedef void *HMODULE; typedef uintptr_t ULONG_PTR;
            #define TRUE 1
            #define FALSE 0
            #define IMAGE_DOS_SIGNATURE 0x5a4d
            #define IMAGE_NT_SIGNATURE 0x00004550
            #define IMAGE_FILE_MACHINE_I386 0x014c
            #define IMAGE_NT_OPTIONAL_HDR32_MAGIC 0x010b
            #define IMAGE_DIRECTORY_ENTRY_BASERELOC 5
            #define IMAGE_REL_BASED_HIGHLOW 3
            {h2_defines}
            #define IMAGE_DOS_SIGNATURE 0x5a4d
            #define IMAGE_NT_SIGNATURE 0x00004550
            #define IMAGE_FILE_MACHINE_I386 0x014c
            #define IMAGE_DIRECTORY_ENTRY_BASERELOC 5
            #define IMAGE_REL_BASED_HIGHLOW 3
            typedef struct {{ DWORD VirtualAddress, Size; }} IMAGE_DATA_DIRECTORY;
            typedef struct {{ WORD Machine, Sections; DWORD TimeDateStamp, a, b; WORD OptionalSize, Characteristics; }} IMAGE_FILE_HEADER;
            typedef struct {{ WORD Magic; BYTE pad1[26]; DWORD ImageBase; BYTE pad2[24]; DWORD SizeOfImage; BYTE pad3[36]; IMAGE_DATA_DIRECTORY DataDirectory[16]; }} IMAGE_OPTIONAL_HEADER;
            typedef struct {{ DWORD Signature; IMAGE_FILE_HEADER FileHeader; IMAGE_OPTIONAL_HEADER OptionalHeader; }} IMAGE_NT_HEADERS;
            typedef struct {{ WORD e_magic; BYTE pad[58]; int32_t e_lfanew; }} IMAGE_DOS_HEADER;
            static BYTE *g_base; static size_t g_size; static int g_wine_flag;
            static DWORD GetEnvironmentVariableA(const char *name, char *value, DWORD size) {{
                if(g_wine_flag && name[0]=='I') {{ if(size>1u) {{ value[0]='1'; value[1]=0; }} return 1u; }}
                return 0u;
            }}
            static BOOL readable_address(const void *address, DWORD size) {{
                uintptr_t p=(uintptr_t)address, b=(uintptr_t)g_base;
                return p>=b && size<=g_size && p-b<=g_size-size;
            }}
            {shape_decl}
            {bodies}
            int main(int argc, char **argv) {{
                FILE *f; size_t n; const char *reason=NULL; DWORD base, mode;
                if(argc!=4) return 2;
                mode=(DWORD)strtoul(argv[2],NULL,10);
                g_size=DXWRAPPER_IMAGE_SIZE;
                g_base=mmap((void *)(uintptr_t)strtoul(argv[3],NULL,16),g_size,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED_NOREPLACE,-1,0);
                if(g_base==MAP_FAILED) return 3;
                f=fopen(argv[1],"rb"); if(!f) return 4; n=fread(g_base,1,g_size,f); fclose(f); if(n<g_size) memset(g_base+n,0,g_size-n);
                base=(DWORD)(ULONG_PTR)g_base;
                *(DWORD *)(g_base+D3D9_CALLSITE_RVA+1u)=base+D3D9_SOURCE_RVA;
                *(DWORD *)(g_base+D3D9_CALLSITE_RVA+6u)=base+D3D9_INIT_GUARD_RVA;
                *(DWORD *)(g_base+D3D9_CALLSITE_RVA+11u)=base+D3D9_CACHE_RVA;
                if(mode==1) ((IMAGE_NT_HEADERS *)(g_base+((IMAGE_DOS_HEADER *)g_base)->e_lfanew))->FileHeader.TimeDateStamp=0x60b36251u;
                if(mode==2) *(DWORD *)(g_base+D3D9_CALLSITE_RVA+1u)^=1u;
                if(mode==3) *(BYTE *)(g_base+D3D9_CALLSITE_RVA)^=1u;
                if(mode==4) *(BYTE *)(g_base+D3D9_CALLSITE_RVA+16u)^=1u;
                if(mode==5) {{ IMAGE_NT_HEADERS *nt=(IMAGE_NT_HEADERS *)(g_base+((IMAGE_DOS_HEADER *)g_base)->e_lfanew); BYTE *q=g_base+nt->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_BASERELOC].VirtualAddress; nt->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_BASERELOC].Size=8u; *(DWORD *)(q+4)=8u; }}
                if(mode==6) {{ IMAGE_NT_HEADERS *nt=(IMAGE_NT_HEADERS *)(g_base+((IMAGE_DOS_HEADER *)g_base)->e_lfanew); BYTE *q=g_base+nt->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_BASERELOC].VirtualAddress; *(DWORD *)(q+4)=0xffffffffu; }}
                if(mode==8) {{ g_wine_flag=1; ((IMAGE_NT_HEADERS *)(g_base+((IMAGE_DOS_HEADER *)g_base)->e_lfanew))->OptionalHeader.ImageBase=base; }}
                if(mode==7) {{ IMAGE_NT_HEADERS *nt=(IMAGE_NT_HEADERS *)(g_base+((IMAGE_DOS_HEADER *)g_base)->e_lfanew); nt->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_BASERELOC].VirtualAddress=DXWRAPPER_IMAGE_SIZE-4u; nt->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_BASERELOC].Size=8u; }}
                if(mode==9) {{ g_wine_flag=1; ((IMAGE_NT_HEADERS *)(g_base+((IMAGE_DOS_HEADER *)g_base)->e_lfanew))->OptionalHeader.ImageBase=DXWRAPPER_IMAGE_BASE; }}
                if(mode==10) {{ ((IMAGE_DOS_HEADER *)g_base)->e_lfanew=297; }}
                if(mode==11) {{ ((IMAGE_NT_HEADERS *)(g_base+((IMAGE_DOS_HEADER *)g_base)->e_lfanew))->OptionalHeader.Magic=0x20b; }}
                return module_pinned_h2((HMODULE)g_base,&reason) ? 0 : 1;
            }}
            """
        ),
        encoding="utf-8",
    )
    subprocess.run(["gcc", "-std=c99", "-O0", "-Wall", str(harness), "-o", str(exe)], check=True)
    cases = {0: True, 1: False, 2: False, 3: False, 4: False, 5: False, 6: False, 7: False, 8: True, 9: False, 10: False, 11: False}
    image_path = tmp_path / "dxwrapper.dll"
    image_path.write_bytes(mapped)
    for loaded_base in (0x10000000, 0x20000000):
        for mode, accepted in cases.items():
            result = subprocess.run([str(exe), str(image_path), str(mode), f"{loaded_base:x}"], check=False)
            if result.returncode == 3:
                pytest.skip(f"host mapping unavailable at 0x{loaded_base:x}")
            assert result.returncode in (0, 1), (loaded_base, mode, result.returncode)
            expected = accepted
            # The Wine branch requires the loaded image base even when the
            # header still claims the native preferred base.
            if mode == 9 and loaded_base == 0x10000000:
                expected = True
            assert result.returncode == (0 if expected else 1), (loaded_base, mode)
