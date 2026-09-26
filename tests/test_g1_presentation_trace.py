"""Synthetic trace fixtures for the fail-closed DirectDraw provenance validator."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

import pytest

from tools.check_g1_presentation_trace import validate, validate_native_split
from tools.runtime_env import RuntimeSafetyError, _presentation_trace_install_gate


ROOT = Path(__file__).resolve().parents[1]
COMPILER = "i686-w64-mingw32-gcc"


def _build_serializer_fixture(tmp_path: Path, serializer_source: Path) -> Path:
    executable = tmp_path / "trace_serializer_fixture.exe"
    result = subprocess.run(
        [COMPILER, "-m32", "-Wall", "-Wextra", "-Werror", "-O2",
         "-fno-stack-protector", "-mno-stack-arg-probe", "-nostartfiles",
         "-nodefaultlibs", "-Wl,-e,_WinMain@16", "-o", str(executable),
         "-I", str(ROOT / "tools/inmm_stub"),
         str(ROOT / "tools/inmm_stub/trace_serializer_fixture.c"),
         str(serializer_source), "-lkernel32", "-luser32"],
        cwd=ROOT / "tools/inmm_stub", capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    return executable


def _run_serializer_fixture(
    executable: Path, tmp_path: Path,
) -> tuple[subprocess.CompletedProcess[str], bytes]:
    prefix = Path(tempfile.mkdtemp(prefix="syw2-trace-serializer-", dir=tmp_path))
    env = dict(os.environ, WINEPREFIX=str(prefix), WINEARCH="win32", WINEDEBUG="-all")
    # This fixture is a console-only serializer check. Inheriting a stale or
    # unrelated desktop DISPLAY can leave Wine child processes holding the
    # captured pipes after wineboot has already returned successfully.
    env.pop("DISPLAY", None)
    try:
        boot = subprocess.run(["wineboot", "-u"], env=env, capture_output=True, text=True, timeout=30)
        assert boot.returncode == 0, boot.stderr
        result = subprocess.run(["wine", str(executable)], env=env, capture_output=True,
                                text=True, timeout=30)
        output_path = prefix / "drive_c/trace_serializer_fixture.jsonl"
        output = output_path.read_bytes() if output_path.is_file() else b""
        return result, output
    finally:
        subprocess.run(["wineserver", "-k"], env=env, capture_output=True, check=False)
        subprocess.run(["wineserver", "-w"], env=env, capture_output=True, check=False)
        shutil.rmtree(prefix, ignore_errors=True)


def test_native_serializer_preserves_lap136_shape_and_fail_closed_capacity(tmp_path: Path):
    assert shutil.which(COMPILER), f"required native compiler is unavailable: {COMPILER}"
    assert shutil.which("wine"), "required native runner is unavailable: wine"
    executable = _build_serializer_fixture(tmp_path, ROOT / "tools/inmm_stub/trace_record_serializer.c")
    result, output = _run_serializer_fixture(executable, tmp_path)
    assert result.returncode == 0, result.stderr
    assert len(output) == 1103
    assert b"\x00" not in output
    assert output.endswith(b"}\n")
    assert output.count(b"\n") == 1
    record = json.loads(output.decode("ascii"))
    assert record["run_id"] == (
        "20260911_172631_3142585_0-"
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_abcde"
    )
    assert len(record["run_id"]) == 95
    assert record["method_counts"]["blt_fast"]["total_count"] == 2798
    assert record["detach"] == "complete"
    assert record["flush"] == "complete"


def _assert_production_trace_writer_contract(source: str) -> None:
    raw_start = source.index("static BOOL trace_event_raw(")
    raw_end = source.index("\n}\n\nstatic void trace_overflow", raw_start)
    raw = source[raw_start:raw_end]
    event_start = source.index("static void trace_event(")
    event_end = source.index("\n}\n\nstatic BOOL trace_method_aggregate", event_start)
    event = source[event_start:event_end]

    assert '#include "trace_record_serializer.h"' in source
    assert "trace_record_serialize(line, sizeof(line), prefix, details, &length)" in raw
    assert "written != length" in source
    assert "wsprintfA(line," not in source
    write_index = raw.index("if (!write_line(line, length)) return FALSE;")
    count_index = raw.index("++g_event_count;")
    assert write_index < count_index
    failure_start = event.index(
        "if (!trace_event_raw(event, install_status, details, call_seq,"
    )
    failure = event[failure_start:]
    dropped_index = failure.index("++g_dropped_count;")
    failed_index = failure.index("g_trace_failed = 1;")
    overflow_index = failure.index('trace_overflow("event_limit");')
    assert dropped_index < failed_index < overflow_index


def test_production_trace_writer_uses_bounded_serializer_and_exact_write():
    source = (ROOT / "tools/inmm_stub/direct_draw_trace.c").read_text(encoding="utf-8")
    _assert_production_trace_writer_contract(source)


def test_production_trace_writer_regression_rejects_failure_order_mutations():
    source = (ROOT / "tools/inmm_stub/direct_draw_trace.c").read_text(encoding="utf-8")
    write_marker = "if (!write_line(line, length)) return FALSE;\n    ++g_event_count;"
    write_mutation = "++g_event_count;\n    if (!write_line(line, length)) return FALSE;"
    assert write_marker in source
    with pytest.raises(AssertionError):
        _assert_production_trace_writer_contract(source.replace(write_marker, write_mutation, 1))

    failure_start = source.index(
        "    if (!trace_event_raw(event, install_status, details, call_seq,"
    )
    failure_source = source[failure_start:]
    failure_marker = "++g_dropped_count;\n        g_trace_failed = 1;"
    failure_mutation = "g_trace_failed = 1;\n        ++g_dropped_count;"
    assert failure_marker in failure_source
    with pytest.raises(AssertionError):
        _assert_production_trace_writer_contract(
            source[:failure_start] + failure_source.replace(failure_marker, failure_mutation, 1)
        )


def test_native_serializer_regression_rejects_old_1024_byte_mutation(tmp_path: Path):
    assert shutil.which(COMPILER), f"required native compiler is unavailable: {COMPILER}"
    assert shutil.which("wine"), "required native runner is unavailable: wine"
    serializer = ROOT / "tools/inmm_stub/trace_record_serializer.c"
    mutated = tmp_path / serializer.name
    mutated.write_text(
        serializer.read_text(encoding="utf-8").replace(
            "if ((DWORD)fragment_length > available) return FALSE;",
            "if ((DWORD)fragment_length > available || *used + (DWORD)fragment_length > 1023u) return FALSE;",
            1,
        ),
        encoding="utf-8",
    )
    executable = _build_serializer_fixture(tmp_path, mutated)
    result, _ = _run_serializer_fixture(executable, tmp_path)
    assert result.returncode != 0


def _event(seq: int, event: str, **extra: object) -> dict[str, object]:
    return {
        "schema": "g1-directdraw-trace-v1", "run_id": "fixture-1", "seq": seq,
        "ts_ms": seq, "pid": 7, "thread_id": 8, "program_state": 3,
        "game_tick": seq, "event": event, "install_status": "active", **extra,
    }


def _capture(client_size: list[int] | None = None) -> dict[str, object]:
    size = client_size or [800, 600]
    return {"run_id": "fixture-1", "ps_before": 9, "ps_after": 3,
            "tick_after": 42, "client_size": size, "logical_content_size": [800, 600],
            "screenshot": {"sha256": "a" * 64, "dimensions": size}}


def _method_counts(*, blt_fast_detailed: int = 0, blt_fast_aggregated: int = 0,
                   blt_fast_dropped: int = 0) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    for method in ("set_display_mode", "create_surface", "get_surface_desc", "blt", "flip",
                   "surface_release"):
        result[method] = {"detailed_count": 0, "aggregated_count": 0,
                          "dropped_count": 0, "total_count": 0}
    result["blt_fast"] = {
        "detailed_count": blt_fast_detailed,
        "aggregated_count": blt_fast_aggregated,
        "dropped_count": blt_fast_dropped,
        "total_count": blt_fast_detailed + blt_fast_aggregated + blt_fast_dropped,
    }
    return result


def _aggregate(seq: int, *, program_state: int = 3, count: int = 1,
               first_call_seq: int | None = None) -> dict[str, object]:
    first = seq if first_call_seq is None else first_call_seq
    return _event(
        seq, "aggregate", method="blt_fast", object="0x2000",
        interface="IDirectDrawSurface7", original_pointer="0x70004000",
        present_identity="0x2001", program_state=program_state, count=count,
        first_call_seq=first, last_call_seq=first + count - 1,
        first_tick=first, last_tick=first + count - 1,
    )


def test_valid_identity_chain_passes(tmp_path: Path):
    events = [
        _event(1, "install", stage="complete", import_name="DirectDrawCreateEx",
               import_thunk="0x004D7938", iat_slot="0x004E5018", loader_target="0x70001000",
               original_pointer="0x70001000", module_start="0x70000000", module_end="0x70100000",
               dd_vtable_methods=30, surface_vtable_methods=49, event_limit=2048, method_limit=256,
               aggregate_limit=64),
        _event(2, "direct_draw_create_ex", dd_object="0x1000",
               iid="15E65EC0-3B9C-11D2-B92F-00609797EA5B", caller="0x400100",
               return_address="0x400100", original_pointer="0x70001000",
               module_start="0x70000000", module_end="0x70100000", dd_vtable_methods=30),
        _event(3, "set_display_mode", object="0x1000", width=800, height=600,
               dd_vtable_methods=30, original_pointer="0x70002000", caller="0x400200",
               return_address="0x400200"),
        _event(4, "create_surface", dd_object="0x1000", returned_surface="0x2000",
               descriptor={"width": 800, "height": 600}, surface_interface="IDirectDrawSurface7",
               surface_vtable_methods=49, caller="0x400300", return_address="0x400300"),
        _event(5, "get_surface_desc", surface="0x2000", actual_desc={"width": 800, "height": 600},
               surface_interface="IDirectDrawSurface7", surface_vtable_methods=49,
               caller="0x400400", return_address="0x400400"),
        _event(6, "flip", destination_this="0x2000", target="0x2001",
               surface_interface="IDirectDrawSurface7", surface_vtable_methods=49,
               caller="0x400500", return_address="0x400500", present_tick=6),
        _event(7, "surface_release", surface="0x2000",
               surface_interface="IDirectDrawSurface7", surface_vtable_methods=49,
               original_pointer="0x70003000", release_result=0, lifetime_action="retire",
               reason_code=23, reason="release_retire", caller="0x400600",
               return_address="0x400600"),
        _event(8, "summary", event_count=7, dropped_count=0, source_call_count=8,
               aggregate_record_count=0, method_counts={
                   "set_display_mode": {"detailed_count": 1, "aggregated_count": 0,
                                         "dropped_count": 0, "total_count": 1},
                   "create_surface": {"detailed_count": 1, "aggregated_count": 0,
                                       "dropped_count": 0, "total_count": 1},
                   "get_surface_desc": {"detailed_count": 1, "aggregated_count": 0,
                                         "dropped_count": 0, "total_count": 1},
                   "blt": {"detailed_count": 0, "aggregated_count": 0,
                           "dropped_count": 0, "total_count": 0},
                   "blt_fast": {"detailed_count": 0, "aggregated_count": 0,
                                "dropped_count": 0, "total_count": 0},
                   "flip": {"detailed_count": 1, "aggregated_count": 0,
                            "dropped_count": 0, "total_count": 1},
                   "surface_release": {"detailed_count": 1, "aggregated_count": 0,
                                       "dropped_count": 0, "total_count": 1},
               }),
    ]
    path = tmp_path / "trace.jsonl"
    path.write_text("\n".join(json.dumps(item) for item in events) + "\n")
    report = validate(path, capture=_capture())
    assert report["status"] == "PASS"
    report_2x = validate(path, capture=_capture([1600, 1200]))
    assert report_2x["status"] == "PASS"


def test_native_split_validator_requires_converted_pinned_present(tmp_path: Path):
    events = [
        _event(1, "install", stage="complete", import_name="DirectDrawCreateEx",
               import_thunk="0x004D7938", iat_slot="0x004E5018", loader_target="0x70001000",
               original_pointer="0x70001000", module_start="0x70000000", module_end="0x70100000",
               dd_vtable_methods=30, surface_vtable_methods=49, event_limit=2048, method_limit=256,
               aggregate_limit=64),
        _event(2, "direct_draw_create_ex", dd_object="0x1000",
               iid="15E65EC0-3B9C-11D2-B92F-00609797EA5B",
               caller="0x400100", return_address="0x400100", original_pointer="0x70001000",
               module_start="0x70000000", module_end="0x70100000", dd_vtable_methods=30),
        _event(3, "set_display_mode", object="0x1000", width=800, height=600, bpp=8,
               requested_width=800, requested_height=600, requested_bpp=8,
               forwarded_width=1600, forwarded_height=1200, forwarded_bpp=8,
               hresult=0, return_address="0x0046457D", dd_vtable_methods=30,
               original_pointer="0x70002000", caller="0x400200"),
        _event(4, "create_surface", dd_object="0x1000", returned_surface="0x2000",
               descriptor={"flags": 33, "width": 1600, "height": 1200,
                           "backbuffer_count": 1, "caps": 0x200},
               surface_interface="IDirectDrawSurface7", surface_vtable_methods=49,
               caller="0x400300", return_address="0x400300"),
        _event(5, "create_surface", dd_object="0x1000", returned_surface="0x2001",
               descriptor={"flags": 33, "width": 832, "height": 600,
                           "backbuffer_count": 0, "caps": 0},
               surface_interface="IDirectDrawSurface7", surface_vtable_methods=49,
               caller="0x400301", return_address="0x400301"),
        _event(6, "get_surface_desc", surface="0x2000", actual_desc={"width": 1600, "height": 1200},
               surface_interface="IDirectDrawSurface7", surface_vtable_methods=49,
               caller="0x400400", return_address="0x400400"),
        _event(7, "get_surface_desc", surface="0x2001", actual_desc={"width": 800, "height": 600},
               surface_interface="IDirectDrawSurface7", surface_vtable_methods=49,
               caller="0x400401", return_address="0x400401"),
        _event(8, "blt", destination_this="0x2000", source="0x2001", destination_is_primary=1,
               source_desc_width=832, source_desc_height=600, converted=1,
               converted_destination_rect={"left": 0, "top": 0, "right": 1600, "bottom": 1200},
               converted_source_rect={"left": 0, "top": 0, "right": 800, "bottom": 600},
                   caller="0x0049273F", return_address="0x0049273F", present_tick=42,
                   game_tick=42, hresult=0,
               original_pointer="0x70003000", surface_interface="IDirectDrawSurface7",
               surface_vtable_methods=49),
    ]
    counts = {method: {"detailed_count": 0, "aggregated_count": 0,
                       "dropped_count": 0, "total_count": 0}
              for method in ("set_display_mode", "create_surface", "get_surface_desc",
                             "blt", "blt_fast", "flip", "surface_release")}
    counts["set_display_mode"] = {"detailed_count": 1, "aggregated_count": 0,
                                   "dropped_count": 0, "total_count": 1}
    counts["create_surface"] = {"detailed_count": 2, "aggregated_count": 0,
                                 "dropped_count": 0, "total_count": 2}
    counts["get_surface_desc"] = {"detailed_count": 2, "aggregated_count": 0,
                                   "dropped_count": 0, "total_count": 2}
    counts["blt"] = {"detailed_count": 1, "aggregated_count": 0,
                      "dropped_count": 0, "total_count": 1}
    events.append(_event(9, "summary", event_count=8, dropped_count=0, source_call_count=9,
                         aggregate_record_count=0, method_counts=counts))
    path = tmp_path / "native-trace.jsonl"
    path.write_text("\n".join(json.dumps(item) for item in events) + "\n")
    report = validate_native_split(path, capture=_capture(), provenance={
        "observational_only": False,
        "intervention_scope": ["set_display_mode_exact_800x600x8_to_1600x1200x8",
                                "ps3_present_bltfast_to_blt_2x"],
    })
    assert report["status"] == "PASS", report["errors"]


def test_missing_present_identity_is_blocked(tmp_path: Path):
    events = [
        _event(1, "install", stage="complete"),
        _event(2, "direct_draw_create_ex", dd_object="0x1000"),
        _event(3, "create_surface", dd_object="0x1000", returned_surface="0x2000"),
        _event(4, "get_surface_desc", surface="0x2000"),
        _event(5, "flip", destination_this="0x9999"),
    ]
    path = tmp_path / "trace.jsonl"
    path.write_text("\n".join(json.dumps(item) for item in events) + "\n")
    report = validate(path, capture=_capture())
    assert report["status"] == "BLOCKED"
    assert any("not connected to a present" in error for error in report["errors"])


def test_overflow_is_never_pass(tmp_path: Path):
    events = [
        _event(1, "install", stage="complete"),
        _event(2, "overflow", scope="surface_records"),
    ]
    path = tmp_path / "trace.jsonl"
    path.write_text("\n".join(json.dumps(item) for item in events) + "\n")
    report = validate(path, capture=_capture())
    assert report["status"] == "BLOCKED"
    assert "trace contains overflow" in report["errors"]


def test_exact_method_boundary_and_state_transition_aggregate_passes(tmp_path: Path):
    events = [
        _event(1, "install", stage="complete", import_name="DirectDrawCreateEx",
               import_thunk="0x004D7938", iat_slot="0x004E5018", loader_target="0x70001000",
               original_pointer="0x70001000", module_start="0x70000000", module_end="0x70100000",
               dd_vtable_methods=30, surface_vtable_methods=49, event_limit=2048,
               method_limit=256, aggregate_limit=64),
        _event(2, "direct_draw_create_ex", dd_object="0x1000",
               iid="15E65EC0-3B9C-11D2-B92F-00609797EA5B", caller="0x400100",
               return_address="0x400100", original_pointer="0x70001000",
               module_start="0x70000000", module_end="0x70100000", dd_vtable_methods=30),
        _event(3, "create_surface", dd_object="0x1000", returned_surface="0x2000",
               descriptor={"width": 800, "height": 600}, surface_interface="IDirectDrawSurface7",
               surface_vtable_methods=49, caller="0x400300", return_address="0x400300"),
        _event(4, "get_surface_desc", surface="0x2000", actual_desc={"width": 800, "height": 600},
               surface_interface="IDirectDrawSurface7", surface_vtable_methods=49,
               caller="0x400400", return_address="0x400400"),
    ]
    for seq in range(5, 261):
        events.append(_event(
            seq, "blt_fast", destination_this="0x2000", source="0x2001",
            surface_interface="IDirectDrawSurface7", surface_vtable_methods=49,
            caller="0x400500", return_address="0x400500", present_tick=seq,
        ))
    events.extend([_aggregate(261, first_call_seq=261),
                   _aggregate(262, program_state=7, first_call_seq=262)])
    method_counts = _method_counts(blt_fast_detailed=256, blt_fast_aggregated=2)
    for method in ("create_surface", "get_surface_desc"):
        method_counts[method] = {"detailed_count": 1, "aggregated_count": 0,
                                 "dropped_count": 0, "total_count": 1}
    events.append(_event(
        263, "summary", event_count=262, dropped_count=0, source_call_count=263,
        aggregate_record_count=2,
        method_counts=method_counts,
    ))
    path = tmp_path / "trace.jsonl"
    path.write_text("\n".join(json.dumps(item) for item in events) + "\n")
    report = validate(path, capture=_capture())
    assert report["status"] == "PASS", report["errors"]


def test_malformed_aggregate_key_is_blocked(tmp_path: Path):
    events = [_aggregate(1), _aggregate(2)]
    path = tmp_path / "trace.jsonl"
    path.write_text("\n".join(json.dumps(item) for item in events) + "\n")
    report = validate(path, capture=_capture())
    assert report["status"] == "BLOCKED"
    assert "aggregate stable key is emitted more than once" in report["errors"]


def test_aggregate_capacity_exhaustion_is_blocked(tmp_path: Path):
    events = [_aggregate(seq, program_state=seq, first_call_seq=seq)
              for seq in range(1, 66)]
    events.append(_event(66, "summary", event_count=65, dropped_count=0,
                         source_call_count=66, aggregate_record_count=65,
                         method_counts=_method_counts(blt_fast_aggregated=65)))
    path = tmp_path / "trace.jsonl"
    path.write_text("\n".join(json.dumps(item) for item in events) + "\n")
    report = validate(path, capture=_capture())
    assert report["status"] == "BLOCKED"
    assert "trace exceeds the 64 aggregate record limit" in report["errors"]


def test_install_gate_is_before_input_and_preserves_failed_raw_trace(tmp_path: Path):
    source = tmp_path / "inmm_trace.jsonl"
    raw_copy = tmp_path / "output" / "trace_raw.jsonl"
    source.write_text(json.dumps({"run_id": "run-1", "event": "install",
                                  "install_status": "failed", "stage": "runtime_contract"}) + "\n",
                       encoding="utf-8")

    with pytest.raises(RuntimeSafetyError, match="failed before first input"):
        _presentation_trace_install_gate(source, raw_copy, "run-1")
    assert raw_copy.read_text(encoding="utf-8") == source.read_text(encoding="utf-8")


def test_install_gate_rejects_malformed_or_missing_trace(tmp_path: Path):
    raw_copy = tmp_path / "trace_raw.jsonl"
    malformed = tmp_path / "malformed.jsonl"
    malformed.write_text("{not-json}\n", encoding="utf-8")
    with pytest.raises(RuntimeSafetyError, match="malformed"):
        _presentation_trace_install_gate(malformed, raw_copy, "run-1")
    assert raw_copy.read_text(encoding="utf-8") == "{not-json}\n"

    missing = tmp_path / "missing.jsonl"
    with pytest.raises(RuntimeSafetyError, match="missing"):
        _presentation_trace_install_gate(missing, raw_copy, "run-1")
    assert raw_copy.read_text(encoding="utf-8") == "{not-json}\n"
