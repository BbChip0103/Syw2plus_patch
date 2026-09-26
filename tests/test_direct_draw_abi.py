"""Native compile regressions for the DirectDrawCreateEx ABI contract."""

from __future__ import annotations

from pathlib import Path
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools/inmm_stub/direct_draw_trace.c"
COMPILER = "i686-w64-mingw32-gcc"


def _syntax_check(source: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            COMPILER,
            "-m32",
            "-Wall",
            "-Wextra",
            "-I",
            str(SOURCE.parent),
            "-fsyntax-only",
            str(source),
        ],
        cwd=source.parent,
        capture_output=True,
        text=True,
        check=False,
    )


def test_directdraw_source_compiles_with_header_abi_contract():
    assert shutil.which(COMPILER), f"required native compiler is unavailable: {COMPILER}"
    result = _syntax_check(SOURCE)
    assert result.returncode == 0, result.stderr


def test_reversed_output_and_iid_order_is_rejected(tmp_path: Path):
    assert shutil.which(COMPILER), f"required native compiler is unavailable: {COMPILER}"
    altered = tmp_path / SOURCE.name
    original = SOURCE.read_text(encoding="utf-8")
    corrected = "typedef HRESULT (WINAPI *DirectDrawCreateExFn)(GUID *, LPVOID *, REFIID, IUnknown *);"
    reversed_order = "typedef HRESULT (WINAPI *DirectDrawCreateExFn)(GUID *, REFIID, LPVOID *, IUnknown *);"
    assert original.count(corrected) == 1
    altered.write_text(original.replace(corrected, reversed_order), encoding="utf-8")

    result = _syntax_check(altered)

    assert result.returncode != 0
    assert "negative width" in result.stderr or "size of array" in result.stderr


def test_hook_forwards_output_and_iid_in_header_order():
    source = SOURCE.read_text(encoding="utf-8")
    signature = "static HRESULT WINAPI hook_direct_draw_create_ex(GUID *guid, LPVOID *out,\n                                                  REFIID iid, IUnknown *outer)"
    assert signature in source
    assert source.count("g_original_create_ex(guid, out, iid, outer)") == 2
    assert "iid ? (unsigned)iid->Data1" in source
    assert "(out ? *out : NULL)" in source


def test_native_2x_blit_is_exact_call_gated_and_default_off():
    source = SOURCE.read_text(encoding="utf-8")
    assert '#define NATIVE_2X_SET_DISPLAY_RETURN 0x0046457Du' in source
    assert 'GetEnvironmentVariableA("SYW2_G1_NATIVE_2X_BLIT"' in source
    assert 'static const BYTE mode_call[3] = {0xFF, 0x51, 0x54};' in source
    assert 'return_address == NATIVE_2X_SET_DISPLAY_RETURN' in source
    assert 'forwarded_width = 1600u;' in source
    assert 'forwarded_height = 1200u;' in source
    assert 'native_2x_skip_reason' in source
    assert source.count(
        'record->original_set_display_mode(self, forwarded_width, forwarded_height,'
    ) == 1


SURFACE_CONTRACT_HARNESS = r'''
#include <stdio.h>
#include <string.h>

#include "surface_reuse_contract.h"

static int record_marker;
static int other_marker;
static int original_vtable_marker;
static int clone_vtable_marker;

static void method_a(void) {}
static void method_b(void) {}

static int expect_failure(G1SurfaceReuseInput input, unsigned reason, const char *name)
{
    G1SurfaceReuseDecision decision = g1_surface_reuse_decide(&input);
    if (decision.reusable || decision.method_count != 0u || decision.reason != reason) {
        fprintf(stderr, "%s: reusable=%d methods=%u reason=%u expected=%u\n",
                name, decision.reusable, decision.method_count, decision.reason, reason);
        return 1;
    }
    return 0;
}

int main(void)
{
    G1SurfaceReuseInput input = {0};
    G1SurfaceReuseDecision decision;

    input.installed = 1;
    input.record_object = &record_marker;
    input.object = &record_marker;
    input.object_vtable = &clone_vtable_marker;
    input.original_vtable = &original_vtable_marker;
    input.clone_vtable = &clone_vtable_marker;
    input.clone_get_surface_desc = method_a;
    input.clone_blt = method_a;
    input.clone_blt_fast = method_a;
    input.clone_flip = method_a;
    input.hook_get_surface_desc = method_a;
    input.hook_blt = method_a;
    input.hook_blt_fast = method_a;
    input.hook_flip = method_a;
    input.original_get_surface_desc = method_a;
    input.original_blt = method_a;
    input.original_blt_fast = method_a;
    input.original_flip = method_a;
    input.clone_release = method_a;
    input.hook_release = method_a;
    input.original_release = method_a;

    decision = g1_surface_reuse_decide(&input);
    if (!decision.reusable || decision.method_count != 49u ||
        decision.reason != G1_SURFACE_REUSE_OK ||
        strcmp(g1_surface_reuse_reason_name(decision.reason), "ok") != 0) return 10;

    input.installed = 0;
    if (expect_failure(input, G1_SURFACE_REUSE_STALE_UNINSTALLED, "stale") != 0) return 11;
    input.installed = 1;
    input.record_object = NULL;
    if (expect_failure(input, G1_SURFACE_REUSE_RECORD_OBJECT_MISSING, "record-object") != 0) return 12;
    input.record_object = &other_marker;
    if (expect_failure(input, G1_SURFACE_REUSE_RECORD_OBJECT_MISMATCH, "identity") != 0) return 13;
    input.record_object = &record_marker;
    input.object = NULL;
    if (expect_failure(input, G1_SURFACE_REUSE_OBJECT_MISSING, "object") != 0) return 14;
    input.object = &record_marker;
    input.object_vtable = NULL;
    if (expect_failure(input, G1_SURFACE_REUSE_OBJECT_VTABLE_MISSING, "object-vtable") != 0) return 15;
    input.object_vtable = &clone_vtable_marker;
    input.original_vtable = NULL;
    if (expect_failure(input, G1_SURFACE_REUSE_ORIGINAL_VTABLE_MISSING, "original-vtable") != 0) return 16;
    input.original_vtable = &original_vtable_marker;
    input.clone_vtable = NULL;
    if (expect_failure(input, G1_SURFACE_REUSE_CLONE_VTABLE_MISSING, "clone-vtable") != 0) return 17;
    input.clone_vtable = &other_marker;
    if (expect_failure(input, G1_SURFACE_REUSE_CLONE_VTABLE_MISMATCH, "clone-identity") != 0) return 18;
    input.clone_vtable = &clone_vtable_marker;

    input.clone_get_surface_desc = method_b;
    if (expect_failure(input, G1_SURFACE_REUSE_GET_DESC_WRAPPER_MISMATCH, "get-desc-wrapper") != 0) return 19;
    input.clone_get_surface_desc = method_a;
    input.clone_blt = method_b;
    if (expect_failure(input, G1_SURFACE_REUSE_BLT_WRAPPER_MISMATCH, "blt-wrapper") != 0) return 20;
    input.clone_blt = method_a;
    input.clone_blt_fast = method_b;
    if (expect_failure(input, G1_SURFACE_REUSE_BLT_FAST_WRAPPER_MISMATCH, "blt-fast-wrapper") != 0) return 21;
    input.clone_blt_fast = method_a;
    input.clone_flip = method_b;
    if (expect_failure(input, G1_SURFACE_REUSE_FLIP_WRAPPER_MISMATCH, "flip-wrapper") != 0) return 22;
    input.clone_flip = method_a;

    input.original_get_surface_desc = NULL;
    if (expect_failure(input, G1_SURFACE_REUSE_GET_DESC_ORIGINAL_MISSING, "get-desc-original") != 0) return 23;
    input.original_get_surface_desc = method_a;
    input.original_blt = NULL;
    if (expect_failure(input, G1_SURFACE_REUSE_BLT_ORIGINAL_MISSING, "blt-original") != 0) return 24;
    input.original_blt = method_a;
    input.original_blt_fast = NULL;
    if (expect_failure(input, G1_SURFACE_REUSE_BLT_FAST_ORIGINAL_MISSING, "blt-fast-original") != 0) return 25;
    input.original_blt_fast = method_a;
    input.original_flip = NULL;
    if (expect_failure(input, G1_SURFACE_REUSE_FLIP_ORIGINAL_MISSING, "flip-original") != 0) return 26;
    input.original_flip = method_a;

    input.clone_release = NULL;
    if (expect_failure(input, G1_SURFACE_REUSE_RELEASE_WRAPPER_MISSING, "release-wrapper") != 0) return 27;
    input.clone_release = method_a;
    input.hook_release = NULL;
    if (expect_failure(input, G1_SURFACE_REUSE_RELEASE_HOOK_MISSING, "release-hook") != 0) return 28;
    input.hook_release = method_a;
    input.clone_release = method_b;
    if (expect_failure(input, G1_SURFACE_REUSE_RELEASE_WRAPPER_MISMATCH, "release-mismatch") != 0) return 29;
    input.clone_release = method_a;
    input.original_release = NULL;
    if (expect_failure(input, G1_SURFACE_REUSE_RELEASE_ORIGINAL_MISSING, "release-original") != 0) return 30;
    input.original_release = method_a;

    {
        G1SurfaceReleaseInput release = {method_a, method_a, method_a, 1u};
        G1SurfaceReleaseDecision lifetime = g1_surface_release_decide(&release);
        if (lifetime.retire || lifetime.reason != G1_SURFACE_REUSE_RELEASE_KEEP ||
            strcmp(g1_surface_reuse_reason_name(lifetime.reason), "release_keep") != 0) return 31;
        release.release_result = 0u;
        lifetime = g1_surface_release_decide(&release);
        if (!lifetime.retire || lifetime.reason != G1_SURFACE_REUSE_RELEASE_RETIRE ||
            strcmp(g1_surface_reuse_reason_name(lifetime.reason), "release_retire") != 0) return 32;
        release.clone_release = method_b;
        lifetime = g1_surface_release_decide(&release);
        if (lifetime.retire || lifetime.reason != G1_SURFACE_REUSE_RELEASE_WRAPPER_MISMATCH) return 33;
    }

    {
        unsigned cycle;
        unsigned failed = 0u;
        int slot_live = 1;
        G1SurfaceReleaseInput release = {method_a, method_a, method_a, 1u};
        for (cycle = 0u; cycle < 9u; ++cycle) {
            G1SurfaceReleaseDecision lifetime = g1_surface_release_decide(&release);
            if (lifetime.retire || lifetime.reason != G1_SURFACE_REUSE_RELEASE_KEEP) ++failed;
            release.release_result = 0u;
            lifetime = g1_surface_release_decide(&release);
            if (!lifetime.retire || lifetime.reason != G1_SURFACE_REUSE_RELEASE_RETIRE) ++failed;
            slot_live = 0;
            if (slot_live) ++failed;
            slot_live = 1; /* empty slot gets a fresh clone before reuse is checked */
            decision = g1_surface_reuse_decide(&input);
            if (!slot_live || !decision.reusable || decision.method_count != 49u) ++failed;
            release.release_result = 1u;
        }
        if (failed != 0u) return 34;
    }

    puts("surface_contract_pass");
    return 0;
}
'''


def _run_surface_contract_harness(header: Path, tmp_path: Path) -> subprocess.CompletedProcess[str]:
    source = tmp_path / "surface_contract_harness.c"
    executable = tmp_path / "surface_contract_harness"
    source.write_text(SURFACE_CONTRACT_HARNESS, encoding="utf-8")
    compile_result = subprocess.run(
        ["gcc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-I", str(header.parent),
         str(source), "-o", str(executable)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert compile_result.returncode == 0, compile_result.stderr
    return subprocess.run([str(executable)], capture_output=True, text=True, check=False)


def test_surface_reuse_uses_shared_native_decision_and_checks_all_branches(tmp_path: Path):
    source = SOURCE.read_text(encoding="utf-8")
    header = SOURCE.parent / "surface_reuse_contract.h"
    assert '#include "surface_reuse_contract.h"' in source
    assert "return g1_surface_reuse_decide(&input);" in source
    assert "surface_methods = decision.method_count;" in source
    assert "trace_surface_reuse_failure" in source
    assert "reason_code" in source
    assert "actual_vtable" in source
    assert "stored_clone_vtable" in source
    assert "stored_original_vtable" in source
    assert "clone->Release = hook_surface_release;" in source
    assert "g1_surface_release_decide(&input)" in source
    assert "ZeroMemory(record, sizeof(*record));" in source

    result = _run_surface_contract_harness(header, tmp_path)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "surface_contract_pass"


def test_surface_reuse_native_regression_rejects_reusable_mutation(tmp_path: Path):
    header = SOURCE.parent / "surface_reuse_contract.h"
    altered_header = tmp_path / header.name
    altered_header.write_text(
        header.read_text(encoding="utf-8").replace(
            "decision.reusable = 1;", "decision.reusable = 0;", 1,
        ),
        encoding="utf-8",
    )
    result = _run_surface_contract_harness(altered_header, tmp_path)
    assert result.returncode != 0


def test_surface_lifetime_native_regression_rejects_zero_retire_mutation(tmp_path: Path):
    header = SOURCE.parent / "surface_reuse_contract.h"
    altered_header = tmp_path / header.name
    altered_header.write_text(
        header.read_text(encoding="utf-8").replace(
            "decision.retire = 1;", "decision.retire = 0;", 1,
        ),
        encoding="utf-8",
    )
    result = _run_surface_contract_harness(altered_header, tmp_path)
    assert result.returncode != 0
