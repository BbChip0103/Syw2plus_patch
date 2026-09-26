"""Static and source-only regression checks for the opt-in G4 AI shadow."""
from pathlib import Path

ROOT = Path(__file__).parents[1]
SOURCE = ROOT / "tools/inmm_stub/ai_shadow.c"
HEADER = ROOT / "tools/inmm_stub/ai_shadow.h"
STUB = ROOT / "tools/inmm_stub/inmm_stub.c"
MAKEFILE = ROOT / "tools/inmm_stub/Makefile"


def test_shadow_is_opt_in_and_has_no_issuer_or_game_writes():
    source = SOURCE.read_text()
    assert 'GetEnvironmentVariableA(SHADOW_ENV' in source
    assert "return n == 1 && value[0] == '1';" in source
    assert "SHADOW_PATH            \"C:\\\\inmm_ai_shadow.jsonl\"" in source
    assert "FUN_0041CB40" in source
    assert "SHADOW_ORIGINAL_TARGET 0x0043F5D0u" in source
    assert "g4_waypoint_issue_fn" not in source
    assert "0x004AEDE0" not in source
    assert "InterlockedCompareExchange(&g_shadow_guard, 1, 0)" in source


def test_call_site_signature_and_exact_once_forwarding_are_pinned():
    source = SOURCE.read_text()
    assert "{ 0xE8, 0xE6, 0x29, 0x02, 0x00 }" in source
    asm_start = source.index("ai_shadow_call_wrapper")
    asm = source[asm_start : source.index("g4_load_before", asm_start)]
    assert '"pushfl\\n\\t"' in asm
    assert '"pushal\\n\\t"' in asm
    assert '"popal\\n\\t"' in asm
    assert '"popfl\\n\\t"' in asm
    assert asm.count('"jmp *_g_original_target\\n\\t"') == 1
    assert 'Tail-jump' in asm
    assert "site[0] = 0xE8;" in source


def test_exact_postload_hook_pins_load_site_marker_sequence_and_rollback():
    source = SOURCE.read_text()
    assert "LOAD_CALL_SITE         0x004D6B98u" in source
    assert "LOAD_ORIGINAL_TARGET   0x00440FF0u" in source
    assert "{ 0xE8, 0x53, 0xA4, 0xF6, 0xFF }" in source
    assert "g4_load_call_wrapper" in source
    wrapper_start = source.index("g4_load_call_wrapper")
    wrapper = source[wrapper_start : source.index("static BOOL verify_call_site", wrapper_start)]
    assert '"pushl 4(%%esp)\\n\\t"' in wrapper
    assert '"call *_g_load_original_target\\n\\t"' in wrapper
    assert '"addl $4, %%esp\\n\\t"' in wrapper
    assert '"pushl %%eax\\n\\t"' in wrapper
    assert '"pushl 8(%%esp)\\n\\t"' in wrapper
    assert '"call _g4_load_complete\\n\\t"' in wrapper
    assert '"addl $8, %%esp\\n\\t"' in wrapper
    assert '"popl %%eax\\n\\t"' in wrapper
    assert "call *g_load_original_target" not in wrapper
    assert wrapper.index('"pushl 4(%%esp)\\n\\t"') < wrapper.index('"call *_g_load_original_target\\n\\t"')
    assert wrapper.index('"call *_g_load_original_target\\n\\t"') < wrapper.index('"pushl %%eax\\n\\t"')
    assert wrapper.index('"call _g4_load_complete\\n\\t"') < wrapper.index('"popl %%eax\\n\\t"')
    assert "result != 1u" in source
    assert '"event\\\":\\\"load_complete' in source
    assert '"load_marker_seq\\\":' in source
    assert "verify_call_site(SHADOW_CALL_SITE" in source
    assert "verify_call_site(LOAD_CALL_SITE" in source
    assert "rollback_call_site(SHADOW_CALL_SITE" in source
    assert "rollback_call_site(LOAD_CALL_SITE" in source


def test_postload_window_is_bounded_and_candidate_is_not_implemented():
    source = SOURCE.read_text()
    assert "#define SHADOW_POSTLOAD_EVENTS 17u" in source
    assert "g_postload_active" in source
    assert '"candidate_present\\\":false' in source
    assert '"candidate_issue_count\\\":0' in source


def test_raw_mode_and_shadow_evidence_fields_are_present():
    source = SOURCE.read_text()
    for address in (
        "PROGRAM_STATE_VA       0x004ED818u",
        "COMMITTED_LOCAL_VA     0x004ED848u",
        "SCENARIO_SELECTOR_VA   0x009E1DD8u",
        "NETWORK_MODE_VA        0x00B93960u",
        "NETWORK_MODAL_VA       0x00B93964u",
        "RAW_GATE_A_VA          0x00B93982u",
        "RAW_GATE_B_VA          0x00B93988u",
        "GLOBAL_TICK_VA         0x008924B8u",
    ):
        assert address in source
    for field in (
        '"same_tick_reentry"', '"tick_rewind"', '"postload"',
        '"entry_ecx"', '"raw_mode"', '"source"', '"full_id"',
        '"command"', '"pending"', '"pending_xy"', '"decision"',
        '"original_call"', '"forwarded_once"',
    ):
        assert field in source or field.replace('"', '') in source
    assert '"INFERRED_TICK_REWIND"' in source
    assert '"UNOBSERVED"' in source
    assert 'SHADOW_POLICY_UNTESTED' in source
    assert 'would_issue_candidate_raw_guards' not in source
    assert '"concrete_rejection"' in source


def test_minimal_integration_is_wired_and_default_remains_safe():
    assert '#include "ai_shadow.h"' in STUB.read_text()
    stub = STUB.read_text()
    assert "if (!ai_shadow_install())" in stub
    assert "ai_shadow_detach();" in stub
    assert "ai_shadow.c" in MAKEFILE.read_text()
    assert "int ai_shadow_install(void);" in HEADER.read_text()
