#!/usr/bin/env python3
"""Read-only independent review of the lap606 W50B raw evidence."""

from __future__ import annotations

import hashlib
import json
import struct
from collections import Counter
from pathlib import Path

from PIL import Image


REPO = Path(__file__).resolve().parents[4]
RUN = REPO / "local/runtime/20260925_125736_3583920_0"
TRACE = RUN / "output/g1_presentation_trace/trace_raw.jsonl"
EVIDENCE = RUN / "output/g1_presentation_trace/evidence.json"
PROVENANCE = RUN / "output/g1_presentation_trace/provenance.json"
VERDICT = RUN / "output/g1_presentation_trace/verdict.json"
MANIFEST = RUN / "manifest.json"
ORIGINAL = Path(
    "/home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus_re/"
    "Syw2plus/syw2plus_original.exe"
)
CAPTURE = Path(
    "/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/captures/"
    "20260925_125818_20260925_125736_3583920_0-presentation_3586127_"
    "ps3_scene_1790308698176795886.png"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def read_trace(path: Path) -> list[dict[str, object]]:
    events = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        event = json.loads(line)
        if not isinstance(event, dict):
            raise ValueError(f"trace line {number} is not an object")
        events.append(event)
    return events


def pe_va_bytes(path: Path, va: int, size: int) -> str:
    data = path.read_bytes()
    pe_offset = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe_offset : pe_offset + 4] != b"PE\0\0":
        raise ValueError("not a PE image")
    coff = pe_offset + 4
    section_count = struct.unpack_from("<H", data, coff + 2)[0]
    optional_size = struct.unpack_from("<H", data, coff + 16)[0]
    optional = coff + 20
    if struct.unpack_from("<H", data, optional)[0] != 0x10B:
        raise ValueError("expected PE32 optional header")
    image_base = struct.unpack_from("<I", data, optional + 28)[0]
    rva = va - image_base
    sections = optional + optional_size
    for index in range(section_count):
        section = sections + index * 40
        virtual_size, virtual_address, raw_size, raw_offset = struct.unpack_from(
            "<IIII", data, section + 8
        )
        span = max(virtual_size, raw_size)
        if virtual_address <= rva and rva + size <= virtual_address + span:
            offset = raw_offset + (rva - virtual_address)
            return data[offset : offset + size].hex()
    raise ValueError(f"VA not mapped: 0x{va:08X}")


def capture_metrics(path: Path) -> dict[str, object]:
    image = Image.open(path).convert("RGB")
    width, height = image.size
    pixels = image.load()
    total_blocks = (width // 2) * (height // 2)
    equal_blocks = 0
    equal_anchor_pixels = 0
    for y in range(0, height, 2):
        for x in range(0, width, 2):
            block = [pixels[x, y], pixels[x + 1, y], pixels[x, y + 1], pixels[x + 1, y + 1]]
            equal_blocks += int(len(set(block)) == 1)
            equal_anchor_pixels += sum(pixel == block[0] for pixel in block)
    sampled = image.resize((width // 2, height // 2), Image.Resampling.NEAREST)
    expanded = sampled.resize((width, height), Image.Resampling.NEAREST)
    expanded_pixels = list(expanded.get_flattened_data())
    image_pixels = list(image.get_flattened_data())
    pixel_equality = sum(left == right for left, right in zip(image_pixels, expanded_pixels)) / (
        width * height
    )
    nonblack = [(x, y) for y in range(height) for x in range(width) if pixels[x, y] != (0, 0, 0)]
    bbox = None
    if nonblack:
        xs = [point[0] for point in nonblack]
        ys = [point[1] for point in nonblack]
        bbox = [min(xs), min(ys), max(xs) + 1, max(ys) + 1]
    quadrants = []
    for left, top, right, bottom in (
        (0, 0, 800, 600),
        (800, 0, 1600, 600),
        (0, 600, 800, 1200),
        (800, 600, 1600, 1200),
    ):
        quadrants.append(
            sum(
                pixels[x, y] != (0, 0, 0)
                for y in range(top, bottom)
                for x in range(left, right)
            )
        )
    return {
        "dimensions": [width, height],
        "nonblack_bbox": bbox,
        "nonblack_quadrants": quadrants,
        "block_all_equal_fraction": equal_blocks / total_blocks,
        "block_anchor_pixel_fraction": equal_anchor_pixels / (total_blocks * 4),
        "nearest_2x_pixel_equality": pixel_equality,
    }


def main() -> None:
    events = read_trace(TRACE)
    evidence = read_json(EVIDENCE)
    provenance = read_json(PROVENANCE)
    verdict = read_json(VERDICT)
    modes = [event for event in events if event.get("event") == "set_display_mode"]
    applied = [event for event in modes if event.get("native_2x_applied") == 1]
    skips = [event for event in events if event.get("event") == "structured_skip"]
    primary_creates = [
        event
        for event in events
        if event.get("event") == "create_surface"
        and isinstance(event.get("descriptor"), dict)
        and event["descriptor"].get("flags") == 33
        and event["descriptor"].get("backbuffer_count") == 1
    ]
    final_primary = primary_creates[-1]
    primary_surface = final_primary["returned_surface"]
    primary_descs = [
        event
        for event in events
        if event.get("event") == "get_surface_desc" and event.get("surface") == primary_surface
    ]
    ps3_offscreens = [
        event
        for event in events
        if event.get("event") == "create_surface"
        and event.get("program_state") == 2
        and isinstance(event.get("descriptor"), dict)
        and [event["descriptor"].get("width"), event["descriptor"].get("height")] == [832, 600]
    ]
    offscreen_surface = ps3_offscreens[-1]["returned_surface"]
    blts = [event for event in events if event.get("event") == "blt"]
    exact_final_blts = [event for event in blts if event.get("return_address") == "0x0041C3E4"]
    ps3_present_aggregates = [
        event
        for event in events
        if event.get("event") == "aggregate"
        and event.get("method") == "blt_fast"
        and event.get("program_state") == 3
        and event.get("object") == primary_surface
        and event.get("present_identity") == offscreen_surface
    ]
    summary = [event for event in events if event.get("event") == "summary"][-1]
    result = {
        "hashes": {
            "manifest": sha256(MANIFEST),
            "trace_raw": sha256(TRACE),
            "evidence": sha256(EVIDENCE),
            "provenance": sha256(PROVENANCE),
            "verdict": sha256(VERDICT),
            "capture": sha256(CAPTURE),
            "original": sha256(ORIGINAL),
            "private_exe": sha256(RUN / "game/syw2plus_original.exe"),
            "private_bridge": sha256(RUN / "game/_inmm.dll"),
        },
        "event_counts": dict(sorted(Counter(event.get("event") for event in events).items())),
        "native_modes": {
            "mode_count": len(modes),
            "applied_count": len(applied),
            "skip_count": len(skips),
            "exact_applied_contract": all(
                [event.get("requested_width"), event.get("requested_height"), event.get("requested_bpp")]
                == [800, 600, 8]
                and [event.get("forwarded_width"), event.get("forwarded_height"), event.get("forwarded_bpp")]
                == [1600, 1200, 8]
                and event.get("return_address") == "0x0046457D"
                and event.get("hresult") == 0
                for event in applied
            ),
        },
        "surfaces": {
            "final_primary_create_seq": final_primary.get("seq"),
            "final_primary_surface": primary_surface,
            "final_primary_desc": primary_descs[-1].get("actual_desc"),
            "ps3_offscreen_create_seq": ps3_offscreens[-1].get("seq"),
            "ps3_offscreen_surface": offscreen_surface,
            "ps3_offscreen_request": ps3_offscreens[-1].get("descriptor"),
        },
        "present_paths": {
            "blt_count": len(blts),
            "blt_callers": sorted(Counter(event.get("return_address") for event in blts).items()),
            "blt_sources": sorted(Counter(event.get("source") for event in blts).items()),
            "blt_flags": sorted(Counter(event.get("flags") for event in blts).items()),
            "exact_0041c3e4_count": len(exact_final_blts),
            "ps3_blt_fast_aggregate": ps3_present_aggregates,
        },
        "original_bytes": {
            "0041c3c4_0041c3e4": pe_va_bytes(ORIGINAL, 0x0041C3C4, 0x21),
            "0049272c_0049273f": pe_va_bytes(ORIGINAL, 0x0049272C, 0x14),
            "004d1050_004d1066": pe_va_bytes(ORIGINAL, 0x004D1050, 0x17),
        },
        "capture": capture_metrics(CAPTURE),
        "validator": evidence.get("validator"),
        "evidence_error": evidence.get("error"),
        "verdict_error": verdict.get("error"),
        "cleanup": evidence.get("cleanup"),
        "provenance": {
            "native_2x_environment": provenance.get("environment", {}).get("SYW2_G1_NATIVE_2X_BLIT"),
            "observational_only": provenance.get("observational_only"),
            "dxwrapper_enabled": provenance.get("dxwrapper_config", {}).get("enabled"),
        },
        "summary": {
            "event_count": summary.get("event_count"),
            "dropped_count": summary.get("dropped_count"),
            "detach": summary.get("detach"),
            "flush": summary.get("flush"),
        },
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
