#!/usr/bin/env python3
"""Fail-closed validator for one diagnostic DirectDraw presentation trace."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, cast


SCHEMA = "g1-directdraw-trace-v1"
EXPECTED_DD_IID = "15E65EC0-3B9C-11D2-B92F-00609797EA5B"
EXPECTED_SURFACE_INTERFACE = "IDirectDrawSurface7"
DD_VTABLE_METHODS = 30
SURFACE_VTABLE_METHODS = 49
MAX_EVENTS = 2048
MAX_METHOD_EVENTS = 256
MAX_AGGREGATES = 64
SUPPORTED_CLIENT_SIZES = {(800, 600), (1600, 1200)}
REQUIRED = {
    "schema", "run_id", "seq", "ts_ms", "pid", "thread_id", "program_state",
    "game_tick", "event", "install_status",
}
METHOD_EVENTS = {"set_display_mode", "create_surface", "get_surface_desc", "blt", "blt_fast", "flip",
                 "surface_release"}
PRESENT_EVENTS = {"blt", "blt_fast", "flip"}
NATIVE_SPLIT_RETURN = "0x0046457D"
NATIVE_PRESENT_RETURNS = {"0x0049273F"}


def _object(value: object) -> str | None:
    if not isinstance(value, str) or not value.startswith("0x"):
        return None
    return value.upper()


def _address(value: object) -> str | None:
    return _object(value)


def _int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _required_fields(item: Mapping[str, Any], fields: set[str], label: str,
                     errors: list[str]) -> None:
    missing = sorted(field for field in fields if field not in item)
    if missing:
        errors.append(f"{label} missing fields: {','.join(missing)}")


def _valid_address_range(item: Mapping[str, Any], label: str, errors: list[str]) -> None:
    start = _address(item.get("module_start"))
    end = _address(item.get("module_end"))
    original = _address(item.get("original_pointer"))
    if not start or not end or not original:
        errors.append(f"{label} module/original pointer provenance is missing")
        return
    try:
        if not (int(start, 16) <= int(original, 16) < int(end, 16)):
            errors.append(f"{label} original pointer is outside the DDRAW module range")
    except ValueError:
        errors.append(f"{label} module/original pointer is not hexadecimal")


def _read_jsonl(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    events: list[dict[str, Any]] = []
    errors: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return [], [f"trace read failed: {exc}"]
    for line_number, line in enumerate(lines, 1):
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"line {line_number}: invalid JSON: {exc.msg}")
            continue
        if not isinstance(item, dict):
            errors.append(f"line {line_number}: event is not an object")
            continue
        missing = sorted(REQUIRED - set(item))
        if missing:
            errors.append(f"line {line_number}: missing fields: {','.join(missing)}")
        if item.get("schema") != SCHEMA:
            errors.append(f"line {line_number}: unexpected schema")
        for field in ("seq", "ts_ms", "pid", "thread_id", "program_state", "game_tick"):
            if not _int(item.get(field)):
                errors.append(f"line {line_number}: {field} must be an integer")
        for field in ("run_id", "event", "install_status"):
            if not isinstance(item.get(field), str) or not item.get(field):
                errors.append(f"line {line_number}: {field} must be a non-empty string")
        events.append(item)
    return events, errors


def validate(trace: Path, *, capture: Mapping[str, Any] | None = None) -> dict[str, Any]:
    events, schema_errors = _read_jsonl(trace)
    errors = list(schema_errors)
    run_ids = {item.get("run_id") for item in events}
    if len(run_ids) != 1 or None in run_ids:
        errors.append("trace must contain exactly one non-null run_id")
    sequences = [item.get("seq") for item in events if isinstance(item.get("seq"), int)]
    if sequences != list(range(1, len(sequences) + 1)):
        errors.append("event seq must be contiguous starting at 1")
    pids = {item.get("pid") for item in events if _int(item.get("pid"))}
    if len(pids) != 1:
        errors.append("trace must contain exactly one process pid")
    if len(events) > MAX_EVENTS:
        errors.append(f"trace exceeds the {MAX_EVENTS} event limit")
    counts: dict[str, int] = {}
    for item in events:
        event = item.get("event")
        if isinstance(event, str):
            counts[event] = counts.get(event, 0) + 1
            if event in METHOD_EVENTS and counts[event] > MAX_METHOD_EVENTS:
                errors.append(f"method event limit exceeded: {event}")
        if item.get("install_status") == "failed":
            errors.append(f"instrumentation failure event: {event}")
        if event in METHOD_EVENTS and item.get("install_status") != "active":
            errors.append(f"method event is not active: {event}")

    install = [item for item in events if item.get("event") == "install"]
    direct = [item for item in events if item.get("event") == "direct_draw_create_ex"]
    creates = [item for item in events if item.get("event") == "create_surface"]
    descs = [item for item in events if item.get("event") == "get_surface_desc"]
    releases = [item for item in events if item.get("event") == "surface_release"]
    presents = [item for item in events if item.get("event") in PRESENT_EVENTS]
    overflows = [item for item in events if item.get("event") == "overflow"]
    aggregates = [item for item in events if item.get("event") == "aggregate"]
    complete_install = [item for item in install
                        if item.get("install_status") == "active" and item.get("stage") == "complete"]
    if not complete_install:
        errors.append("complete active install event is missing")
    else:
        item = complete_install[0]
        _required_fields(item, {"import_name", "import_thunk", "iat_slot", "loader_target",
                                 "original_pointer", "module_start", "module_end",
                                 "dd_vtable_methods", "surface_vtable_methods", "event_limit",
                                 "method_limit", "aggregate_limit"}, "install", errors)
        if item.get("import_name") != "DirectDrawCreateEx":
            errors.append("install import name is not DirectDrawCreateEx")
        if item.get("import_thunk") != "0x004D7938":
            errors.append("install import thunk does not match the pinned code thunk")
        if item.get("iat_slot") != "0x004E5018":
            errors.append("install IAT slot does not match the pinned runtime slot")
        if item.get("dd_vtable_methods") != DD_VTABLE_METHODS:
            errors.append("install DD7 vtable method count is invalid")
        if item.get("surface_vtable_methods") != SURFACE_VTABLE_METHODS:
            errors.append("install Surface7 vtable method count is invalid")
        if (item.get("event_limit") != MAX_EVENTS or
                item.get("method_limit") != MAX_METHOD_EVENTS or
                item.get("aggregate_limit") != MAX_AGGREGATES):
            errors.append("install trace limits are invalid")
        _valid_address_range(item, "install", errors)
    if overflows:
        errors.append("trace contains overflow")
    if not direct:
        errors.append("DirectDrawCreateEx event is missing")
    if not creates:
        errors.append("CreateSurface event is missing")
    if not descs:
        errors.append("GetSurfaceDesc event is missing")
    if not presents:
        errors.append("Blt/BltFast/Flip presentation event is missing")

    for item in direct:
        _required_fields(item, {"dd_object", "iid", "caller", "return_address", "original_pointer",
                                 "module_start", "module_end", "dd_vtable_methods"},
                         "DirectDrawCreateEx", errors)
        if item.get("iid") != EXPECTED_DD_IID:
            errors.append("DirectDrawCreateEx IID is not IID_IDirectDraw7")
        if item.get("dd_vtable_methods") != DD_VTABLE_METHODS:
            errors.append("DirectDrawCreateEx DD7 vtable method count is invalid")
        _valid_address_range(item, "DirectDrawCreateEx", errors)
    for item in (item for item in events if item.get("event") == "set_display_mode"):
        _required_fields(item, {"object", "dd_vtable_methods", "original_pointer", "caller",
                                 "return_address", "width", "height"}, "SetDisplayMode", errors)
        if item.get("dd_vtable_methods") != DD_VTABLE_METHODS:
            errors.append("SetDisplayMode DD7 vtable method count is invalid")
    for item in creates:
        _required_fields(item, {"dd_object", "returned_surface", "descriptor", "surface_interface",
                                 "surface_vtable_methods", "caller", "return_address"},
                         "CreateSurface", errors)
        if item.get("surface_interface") != EXPECTED_SURFACE_INTERFACE:
            errors.append("CreateSurface interface is not IDirectDrawSurface7")
        if item.get("surface_vtable_methods") != SURFACE_VTABLE_METHODS:
            errors.append("CreateSurface Surface7 vtable method count is invalid")
        if not isinstance(item.get("descriptor"), dict):
            errors.append("CreateSurface descriptor is not an object")
    for item in descs:
        _required_fields(item, {"surface", "surface_interface", "surface_vtable_methods", "caller",
                                 "return_address", "actual_desc"}, "GetSurfaceDesc", errors)
        if item.get("surface_interface") != EXPECTED_SURFACE_INTERFACE:
            errors.append("GetSurfaceDesc interface is not IDirectDrawSurface7")
        if item.get("surface_vtable_methods") != SURFACE_VTABLE_METHODS:
            errors.append("GetSurfaceDesc Surface7 vtable method count is invalid")
        desc = item.get("actual_desc")
        if not isinstance(desc, dict) or not _int(desc.get("width")) or not _int(desc.get("height")):
            errors.append("GetSurfaceDesc actual descriptor is incomplete")
    for item in presents:
        _required_fields(item, {"destination_this", "surface_interface", "surface_vtable_methods",
                                 "caller", "return_address", "present_tick"}, "present", errors)
        if item.get("surface_interface") != EXPECTED_SURFACE_INTERFACE:
            errors.append("present interface is not IDirectDrawSurface7")
        if item.get("surface_vtable_methods") != SURFACE_VTABLE_METHODS:
            errors.append("present Surface7 vtable method count is invalid")
        if not _int(item.get("present_tick")) or item.get("present_tick") != item.get("game_tick"):
            errors.append("present tick is missing or does not match event game_tick")
    for item in releases:
        _required_fields(item, {"surface", "surface_interface", "surface_vtable_methods",
                                "original_pointer", "release_result", "lifetime_action",
                                "reason_code", "reason", "caller", "return_address"},
                        "SurfaceRelease", errors)
        if item.get("surface_interface") != EXPECTED_SURFACE_INTERFACE:
            errors.append("SurfaceRelease interface is not IDirectDrawSurface7")
        if item.get("surface_vtable_methods") != SURFACE_VTABLE_METHODS:
            errors.append("SurfaceRelease Surface7 vtable method count is invalid")
        for field in ("surface", "original_pointer", "caller", "return_address"):
            if not _address(item.get(field)):
                errors.append(f"SurfaceRelease {field} pointer is invalid")
        if not _int(item.get("release_result")):
            errors.append("SurfaceRelease refcount result is not an integer")
        if item.get("lifetime_action") not in {"keep", "retire"}:
            errors.append("SurfaceRelease lifetime action is invalid")
        if not _int(item.get("reason_code")) or not isinstance(item.get("reason"), str):
            errors.append("SurfaceRelease reason evidence is incomplete")
        if item.get("lifetime_action") == "retire" and item.get("release_result") != 0:
            errors.append("SurfaceRelease retire action requires a zero refcount")
        if item.get("lifetime_action") == "keep" and item.get("release_result") == 0:
            errors.append("SurfaceRelease keep action requires a non-zero refcount")

    aggregate_counts: dict[str, int] = {}
    aggregate_keys: set[tuple[object, ...]] = set()
    previous_first_seq = 0
    if len(aggregates) > MAX_AGGREGATES:
        errors.append(f"trace exceeds the {MAX_AGGREGATES} aggregate record limit")
    for item in aggregates:
        _required_fields(item, {"method", "object", "interface", "original_pointer",
                                 "present_identity", "program_state", "count",
                                 "first_call_seq", "last_call_seq", "first_tick",
                                 "last_tick"}, "aggregate", errors)
        method = item.get("method")
        if method not in METHOD_EVENTS:
            errors.append("aggregate method is not a known method event")
            continue
        if item.get("install_status") != "active":
            errors.append(f"aggregate is not active: {method}")
        expected_interface = "IDirectDraw7" if method in {"set_display_mode", "create_surface"} else EXPECTED_SURFACE_INTERFACE
        if item.get("interface") != expected_interface:
            errors.append(f"aggregate interface is invalid: {method}")
        for field in ("object", "original_pointer", "present_identity"):
            if not _address(item.get(field)):
                errors.append(f"aggregate {field} identity is invalid: {method}")
        integer_fields = ("program_state", "count", "first_call_seq", "last_call_seq",
                          "first_tick", "last_tick")
        raw_numeric_values = {field: item.get(field) for field in integer_fields}
        if any(not isinstance(value, int) or isinstance(value, bool) or value < 0
               for value in raw_numeric_values.values()):
            errors.append(f"aggregate numeric provenance is invalid: {method}")
            continue
        numeric_values: dict[str, int] = {
            field: cast(int, value) for field, value in raw_numeric_values.items()
        }
        if numeric_values["count"] <= 0:
            errors.append(f"aggregate count must be positive: {method}")
        if numeric_values["first_call_seq"] > numeric_values["last_call_seq"]:
            errors.append(f"aggregate call sequence is not monotonic: {method}")
        if numeric_values["first_tick"] > numeric_values["last_tick"]:
            errors.append(f"aggregate tick range is not monotonic: {method}")
        if numeric_values["first_call_seq"] < previous_first_seq:
            errors.append("aggregate first_call_seq is not ordered")
        previous_first_seq = max(previous_first_seq, numeric_values["first_call_seq"])
        aggregate_key = (method, item.get("object"), item.get("interface"),
                         item.get("original_pointer"), item.get("present_identity"),
                         item.get("program_state"))
        if aggregate_key in aggregate_keys:
            errors.append("aggregate stable key is emitted more than once")
        aggregate_keys.add(aggregate_key)
        aggregate_counts[method] = aggregate_counts.get(method, 0) + numeric_values["count"]

    dd_objects = {_object(item.get("dd_object")) for item in direct}
    dd_objects.discard(None)
    surface_objects = {
        _object(item.get("returned_surface")) for item in creates
    }
    surface_objects.discard(None)
    desc_objects = {_object(item.get("surface")) for item in descs}
    desc_objects.discard(None)
    present_objects: set[str] = set()
    for item in presents:
        for field in ("destination_this", "source", "target"):
            value = _object(item.get(field))
            if value:
                present_objects.add(value)
    if not dd_objects:
        errors.append("DirectDraw object identity is missing")
    if not surface_objects:
        errors.append("returned surface identity is missing")
    if not surface_objects.intersection(desc_objects):
        errors.append("surface CreateSurface -> GetSurfaceDesc identity is not connected")
    if not surface_objects.intersection(present_objects):
        errors.append("surface identity is not connected to a present method")

    capture_ok = False
    capture_details: dict[str, Any] = {}
    if capture is None:
        errors.append("PS9/PS3 capture evidence is missing")
    else:
        capture_details = dict(capture)
        client_size = capture.get("client_size")
        client_size_tuple = tuple(client_size) if isinstance(client_size, list) else None
        logical_content_size = capture.get("logical_content_size", [800, 600])
        capture_ok = (
            capture.get("run_id") in run_ids
            and capture.get("ps_before") == 9
            and capture.get("ps_after") == 3
            and isinstance(capture.get("tick_after"), int)
            and int(capture["tick_after"]) > 0
            and client_size_tuple in SUPPORTED_CLIENT_SIZES
            and logical_content_size == [800, 600]
            and isinstance(capture.get("screenshot"), Mapping)
        )
        screenshot = capture.get("screenshot")
        if capture_ok and isinstance(screenshot, Mapping):
            capture_ok = (isinstance(screenshot.get("sha256"), str)
                          and screenshot.get("dimensions") == list(client_size_tuple or ()))
        if not capture_ok:
            errors.append("capture does not prove same-run PS9 -> PS3 with supported client/logical sizes")

    summaries = [item for item in events if item.get("event") == "summary"]
    if len(summaries) != 1 or not events or events[-1].get("event") != "summary":
        errors.append("exactly one final summary event is required")
    else:
        summary = summaries[0]
        summary_dropped_count = summary.get("dropped_count")
        if summary_dropped_count != 0:
            errors.append("summary reports dropped events")
        if summary.get("event_count") != len(events) - 1:
            errors.append("summary event_count does not match emitted events")
        source_call_count = summary.get("source_call_count")
        aggregate_record_count = summary.get("aggregate_record_count")
        for field, value in (("source_call_count", source_call_count),
                             ("aggregate_record_count", aggregate_record_count)):
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                errors.append(f"summary {field} is missing or invalid")
        if (isinstance(aggregate_record_count, int) and
                aggregate_record_count == len(aggregates)):
            pass
        else:
            errors.append("summary aggregate_record_count does not match aggregate events")
        method_summary = summary.get("method_counts")
        if not isinstance(method_summary, Mapping):
            errors.append("summary method_counts is missing")
        else:
            method_dropped_total = 0
            for method in METHOD_EVENTS:
                summary_item = method_summary.get(method)
                if not isinstance(summary_item, Mapping):
                    errors.append(f"summary method count is missing: {method}")
                    continue
                values: dict[str, Any] = {
                    field: summary_item.get(field) for field in
                    ("detailed_count", "aggregated_count", "dropped_count", "total_count")
                }
                if any(not _int(value) or value < 0 for value in values.values()):
                    errors.append(f"summary method count is invalid: {method}")
                    continue
                if values["detailed_count"] != counts.get(method, 0):
                    errors.append(f"summary detailed_count does not match events: {method}")
                if values["aggregated_count"] != aggregate_counts.get(method, 0):
                    errors.append(f"summary aggregated_count does not match aggregates: {method}")
                if values["total_count"] != (values["detailed_count"] +
                                               values["aggregated_count"] +
                                               values["dropped_count"]):
                    errors.append(f"summary method arithmetic is inconsistent: {method}")
                method_dropped_total += cast(int, values["dropped_count"])
            if (isinstance(summary_dropped_count, int) and
                    method_dropped_total > summary_dropped_count):
                errors.append("summary dropped_count is lower than method dropped counts")

    status = "PASS" if not errors else "BLOCKED"
    return {
        "status": status,
        "schema": {"errors": schema_errors, "event_count": len(events), "counts": counts},
        "identity": {
            "dd_objects": sorted(dd_objects),
            "surface_objects": sorted(surface_objects),
            "described_surfaces": sorted(desc_objects),
            "present_objects": sorted(present_objects),
        },
        "capture": {"ok": capture_ok, **capture_details},
        "errors": errors,
        "trace_sha256": hashlib.sha256(trace.read_bytes()).hexdigest() if trace.is_file() else None,
    }


def validate_native_split(trace: Path, *, capture: Mapping[str, Any] | None = None,
                          provenance: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Validate the opt-in W50C contract without weakening the legacy validator."""
    report = validate(trace, capture=capture)
    errors = list(report.get("errors", []))
    try:
        events = [json.loads(line) for line in trace.read_text(encoding="utf-8").splitlines()
                  if line.strip()]
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"native split trace read failed: {exc}")
        events = []

    modes = [event for event in events if isinstance(event, dict)
             and event.get("event") == "set_display_mode"]
    exact_modes = [event for event in modes
                   if event.get("requested_width") == 800
                   and event.get("requested_height") == 600
                   and event.get("requested_bpp") == 8
                   and event.get("forwarded_width") == 1600
                   and event.get("forwarded_height") == 1200
                   and event.get("forwarded_bpp") == 8
                   and event.get("return_address") == NATIVE_SPLIT_RETURN
                   and event.get("hresult") == 0]
    if not exact_modes:
        errors.append("native split requires one exact successful 800x600x8 -> 1600x1200x8 mode event")

    creates = [event for event in events if isinstance(event, dict)
               and event.get("event") == "create_surface"]
    primary_creates = [event for event in creates
                       if isinstance(event.get("descriptor"), dict)
                       and isinstance(event["descriptor"].get("caps"), int)
                       and (event["descriptor"]["caps"] & 0x200)]
    if not primary_creates:
        errors.append("native split primary surface creation evidence is missing")
    primary_ids = {_object(event.get("returned_surface")) for event in primary_creates}
    primary_ids.discard(None)
    descriptors = [event for event in events if isinstance(event, dict)
                   and event.get("event") == "get_surface_desc"]
    primary_descs = [event for event in descriptors if _object(event.get("surface")) in primary_ids]
    if not any(isinstance(event.get("actual_desc"), dict)
               and event["actual_desc"].get("width") == 1600
               and event["actual_desc"].get("height") == 1200
               for event in primary_descs):
        errors.append("native split primary descriptor is not 1600x1200")
    if not any(isinstance(event.get("actual_desc"), dict)
               and event["actual_desc"].get("width") == 800
               and event["actual_desc"].get("height") == 600
               for event in descriptors if _object(event.get("surface")) not in primary_ids):
        errors.append("native split renderer 800x600 descriptor evidence is missing")

    primary_present = [event for event in events if isinstance(event, dict)
                       and event.get("event") in {"blt", "blt_fast"}
                       and event.get("destination_is_primary") == 1]
    converted = [event for event in primary_present if event.get("converted") == 1]
    if not converted:
        errors.append("native split has no converted primary BltFast present call")
    for event in converted:
        if event.get("return_address") not in NATIVE_PRESENT_RETURNS:
            errors.append("converted primary present caller is outside the pinned set")
        if event.get("converted_destination_rect") != {"left": 0, "top": 0,
                                                        "right": 1600, "bottom": 1200}:
            errors.append("converted primary present destination rect is not 1600x1200")
        if event.get("converted_source_rect") != {"left": 0, "top": 0,
                                                   "right": 800, "bottom": 600}:
            errors.append("converted primary present source rect is not 800x600")
        if event.get("hresult") != 0:
            errors.append("converted primary Blt returned a failure HRESULT")
    if any(event.get("converted") != 1 and event.get("source_desc_width", 0) >= 800
           and event.get("source_desc_height") == 600 for event in primary_present):
        errors.append("an eligible primary logical present remained unconverted")
    if provenance is not None:
        if provenance.get("observational_only") is not False:
            errors.append("native split provenance must set observational_only=false")
        scope = provenance.get("intervention_scope")
        if scope != ["set_display_mode_exact_800x600x8_to_1600x1200x8",
                     "ps3_present_bltfast_to_blt_2x"]:
            errors.append("native split provenance intervention scope is incomplete")

    report["status"] = "PASS" if not errors else "BLOCKED"
    report["errors"] = errors
    report["native_split"] = {
        "mode_exact": bool(exact_modes), "primary_present_events": len(primary_present),
        "converted_events": len(converted), "pinned_returns": sorted(NATIVE_PRESENT_RETURNS),
    }
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--capture", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        capture = json.loads(args.capture.read_text(encoding="utf-8"))
        report = validate(args.trace, capture=capture)
    except (OSError, ValueError, TypeError) as exc:
        report = {"status": "BLOCKED", "errors": [f"validator input failed: {exc}"]}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("status") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
