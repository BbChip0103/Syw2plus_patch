"""Static save-layout model for the lap284 work card.

This probe reads only the preserved original executable and four private fixture
files.  It does not start the game, Wine, Xvfb, or the runtime harness, and it
never writes to the original tree or to the fixture files.

The model follows the save call graph, including fixed fwrite blocks hidden
behind helper calls from the save entry.  It then solves the active roster
record count from the observed file size and uses that count only after the
static prefix model matches all four fixture sizes exactly.
"""
from __future__ import annotations

import hashlib
import json
import re
import struct
import subprocess
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
EXE = REPO / "Syw2plus" / "syw2plus_original.exe"
EXPECTED_EXE_SHA = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"

SAVE_ENTRY, SAVE_END = 0x440C20, 0x440F5B  # exclusive; save ret is at SAVE_END - 1
FWRITE = 0x4DA39F
FREAD = 0x4DA4A9  # neighbouring load routine; must not be in the save window
SAVE_ROSTER = 0x40F4B0
UNIT_STRIDE = 0x758
BULK_PTR, BULK_LEN = 0x892410, 0xE397C
PLAYER_BASE, PLAYER_STRIDE = 0x956770, 0x3ABC
MAP_WIDTH_FILE_OFFSET, MAP_HEIGHT_FILE_OFFSET = 210, 212
MAP_DIMENSION_GUARD = range(1, 181)

# The save entry calls 27 variable map writers and one fixed map-data writer.
# This is the observed call order, not a guessed contiguous address range.
LAYER_TARGETS = [
    0x42A920,
    0x42A9D0,
    0x42AA80,
    0x42AB30,
    0x42AC40,
    0x42ACF0,
    0x42ADA0,
    0x42AE50,
    0x42AF20,
    0x42AFD0,
    0x42B080,
    0x42B130,
    0x42B1E0,
    0x42B290,
    0x42B340,
    0x42B410,
    0x42B4E0,
    0x42B590,
    0x42B660,
    0x42B730,
    0x42B7E0,
    0x42B890,
    0x42B960,
    0x42BA30,
    0x42BAE0,
    0x42BB90,
    0x42BC40,
    0x42AB70,
]
LAYER_SET = set(LAYER_TARGETS)
LAYER_DISASM_STARTS = sorted(LAYER_SET)

# These helpers are called by the save entry and contain their own fwrite.
NESTED_SAVE_HELPERS = {
    0x403950: "secondary_header_0x430x64",
    0x4441E0: "secondary_header_0x48x96",
    0x4464B0: "secondary_tail_0x24x0a",
}
NESTED_SAVE_HELPER_ENDS = {
    0x403950: 0x403970,
    0x4441E0: 0x444200,
    0x4464B0: 0x4464D0,
}

FIXTURES = {
    "save000.dat": {
        "path": REPO.parent / "Syw2plus" / "save" / "save000.dat",
        "size": 3_093_902,
        "sha256": "1c703551888f5c85a1fa2fb7b43d28309eb0b88e4bbf6e859f1a98b629e719da",
    },
    "save006.dat": {
        "path": REPO.parent / "Syw2plus" / "save" / "save006.dat",
        "size": 3_437_942,
        "sha256": "616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064",
    },
    "save011.dat": {
        "path": REPO / "local" / "fixtures" / "20260910" / "save011.dat",
        "size": 1_982_062,
        "sha256": "23dd24d58555588e0ca09491559aed66ad3f2544ff3195c5af2ab9e2be14dfa4",
    },
    "save012.dat": {
        "path": REPO / "local" / "fixtures" / "20260910" / "save012.dat",
        "size": 1_985_822,
        "sha256": "5a6863c1eafaa8bd9a087238a41d45c45635dd66a208cf79a186e158819c28f1",
    },
}

LINE_RE = re.compile(r"^\s*([0-9a-f]+):\s+[0-9a-f ]+\s+(\S+)(?:\s+(.*))?$")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def disasm(start: int, stop: int) -> str:
    return subprocess.run(
        [
            "objdump",
            "-d",
            "-Mintel",
            "-j",
            ".text",
            f"--start-address={start:#x}",
            f"--stop-address={stop:#x}",
            str(EXE),
        ],
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def parsed_lines(text: str) -> list[tuple[int, str, str]]:
    out = []
    for line in text.splitlines():
        match = LINE_RE.match(line)
        if match:
            out.append((int(match.group(1), 16), match.group(2), (match.group(3) or "").strip()))
    return out


def immediate(value: str) -> int | None:
    return int(value, 16) if re.fullmatch(r"0x[0-9a-f]+", value) else None


def fwrite_records(text: str) -> list[dict[str, object]]:
    """Extract fwrite arguments from a small function or save-entry slice."""
    pushes: list[str] = []
    records: list[dict[str, object]] = []
    for address, op, args in parsed_lines(text):
        if op == "push":
            pushes.append(args)
            continue
        if op == "call" and args.split()[0:1] == [f"{FWRITE:#x}"]:
            if len(pushes) < 4:
                records.append({"site": f"{address:#010x}", "bytes": None})
            else:
                _file, count_raw, size_raw, ptr_raw = pushes[-4:]
                count = immediate(count_raw)
                size = immediate(size_raw)
                records.append(
                    {
                        "site": f"{address:#010x}",
                        "count": count,
                        "size": size,
                        "ptr": ptr_raw if immediate(ptr_raw) is not None else None,
                        "bytes": None if count is None or size is None else count * size,
                    }
                )
        if op == "call":
            pushes = []
    return records


def target_of(args: str) -> int | None:
    target = args.split()[0] if args.split() else ""
    return immediate(target)


def helper_record(target: int) -> dict[str, object]:
    records = fwrite_records(disasm(target, NESTED_SAVE_HELPER_ENDS[target]))
    if len(records) != 1 or records[0].get("bytes") is None:
        raise RuntimeError(f"helper {target:#x} did not yield one fixed fwrite: {records}")
    record = dict(records[0])
    record["helper"] = NESTED_SAVE_HELPERS[target]
    return record


def layer_model(target: int) -> dict[str, object]:
    index = LAYER_DISASM_STARTS.index(target)
    stop = LAYER_DISASM_STARTS[index + 1] if index + 1 < len(LAYER_DISASM_STARTS) else 0x42BD00
    text = disasm(target, stop)
    records = fwrite_records(text)
    if target == 0x42AB70:
        if len(records) != 1 or records[0].get("bytes") != 0x7E90:
            raise RuntimeError(f"fixed layer {target:#x} unexpected fwrite: {records}")
        return {
            "target": f"{target:#010x}",
            "writes": records,
            "mode": "fixed_count",
            "repeat": 1,
            "element_bytes": records[0]["size"],
            "bytes_for_map": records[0]["bytes"],
            "guarded_pointer": False,
        }
    if len(records) != 1 or records[0].get("size") not in (1, 2):
        raise RuntimeError(f"layer {target:#x} unexpected fwrite: {records}")
    repeat = 5 if "mov    ebx,0x5" in text else 1
    quarter = text.count("sar    ") >= 2
    mode = "quarter_area" if quarter else "full_area"
    return {
        "target": f"{target:#010x}",
        "writes": records,
        "mode": mode,
        "repeat": repeat,
        "element_bytes": records[0]["size"],
        "bytes_for_map": None,
        "guarded_pointer": "test   eax,eax" in text or "test   esi,esi" in text,
    }


def save_components() -> list[dict[str, object]]:
    """Build the complete save order, retaining nested helper fwrite blocks."""
    pushes: list[str] = []
    components: list[dict[str, object]] = []
    for address, op, args in parsed_lines(disasm(SAVE_ENTRY, SAVE_END)):
        if op == "push":
            pushes.append(args)
            continue
        if op != "call":
            continue
        target = target_of(args)
        if target == FWRITE:
            if len(pushes) < 4:
                raise RuntimeError(f"unparsed direct fwrite at {address:#x}")
            _file, count_raw, size_raw, ptr_raw = pushes[-4:]
            count, size, ptr = immediate(count_raw), immediate(size_raw), immediate(ptr_raw)
            # The first 0x40-byte block points at a stack buffer (ecx), while
            # every other direct block has an immediate data address.
            if count is None or size is None:
                raise RuntimeError(f"non-static direct fwrite at {address:#x}")
            components.append(
                {
                    "kind": "literal",
                    "site": f"{address:#010x}",
                    "ptr": None if ptr is None else f"{ptr:#010x}",
                    "bytes": count * size,
                    "count": count,
                    "size": size,
                }
            )
        elif target in LAYER_SET:
            components.append({"kind": "layer", "site": f"{address:#010x}", **layer_model(target)})
        elif target in NESTED_SAVE_HELPERS:
            components.append({**helper_record(target), "kind": "helper_call", "site": f"{address:#010x}"})
        elif target == SAVE_ROSTER:
            components.append({"kind": "roster", "site": f"{address:#010x}", "record_bytes": UNIT_STRIDE})
        pushes = []
    return components


def component_bytes(component: dict[str, object], area: int) -> int:
    kind = component["kind"]
    if kind in {"literal", "helper_call"}:
        return int(component["bytes"])
    if kind == "layer":
        mode = component["mode"]
        if mode == "fixed_count":
            return int(component["bytes_for_map"])
        factor = int(component["repeat"])
        if mode == "quarter_area":
            return factor * (area // 4) * int(component["element_bytes"])
        return factor * area * int(component["element_bytes"])
    if kind == "roster":
        return 0
    raise RuntimeError(f"unknown component kind: {kind}")


def fixture_report(components: list[dict[str, object]], failures: list[str]) -> dict[str, object]:
    report: dict[str, object] = {}
    layer_components = [c for c in components if c["kind"] == "layer"]
    if len(layer_components) != 28:
        failures.append(f"expected 28 layer calls, got {len(layer_components)}")
    roster_components = [c for c in components if c["kind"] == "roster"]
    if len(roster_components) != 1:
        failures.append(f"expected one roster call, got {len(roster_components)}")
    if any(c["kind"] == "helper_call" for c in components):
        helper_names = [str(c["helper"]) for c in components if c["kind"] == "helper_call"]
        if helper_names != list(NESTED_SAVE_HELPERS.values()):
            failures.append(f"nested save helper order changed: {helper_names}")

    for name, spec in FIXTURES.items():
        path = spec["path"]
        if not path.is_file():
            failures.append(f"missing fixture: {path}")
            continue
        actual_size = path.stat().st_size
        actual_sha = sha256(path)
        if actual_size != spec["size"]:
            failures.append(f"{name} size changed: {actual_size} != {spec['size']}")
        if actual_sha != spec["sha256"]:
            failures.append(f"{name} SHA changed: {actual_sha}")
        data = path.read_bytes()
        width, height = struct.unpack_from("<HH", data, MAP_WIDTH_FILE_OFFSET)
        if width not in MAP_DIMENSION_GUARD or height not in MAP_DIMENSION_GUARD:
            failures.append(f"{name} map dimensions outside guard: {width}x{height}")
        area = width * height
        static_prefix = sum(component_bytes(c, area) for c in components if c["kind"] != "roster")
        remainder = actual_size - static_prefix
        whole = remainder >= 0 and remainder % UNIT_STRIDE == 0
        roster_records = remainder // UNIT_STRIDE if whole else None
        reconstructed = static_prefix + roster_records * UNIT_STRIDE if roster_records is not None else None
        if not whole:
            failures.append(
                f"{name} static model leaves non-integral roster remainder: "
                f"size={actual_size} static={static_prefix} remainder={remainder}"
            )
        if reconstructed != actual_size:
            failures.append(f"{name} reconstruction mismatch: {reconstructed} != {actual_size}")
        report[name] = {
            "path": str(path),
            "sha256": actual_sha,
            "size": actual_size,
            "map_dimensions": {"width": width, "height": height, "area": area},
            "static_prefix_before_roster": static_prefix,
            "roster_remainder": remainder,
            "roster_records": roster_records,
            "reconstructed_size": reconstructed,
            "model_exact": reconstructed == actual_size,
        }
    return report


def player_report(components: list[dict[str, object]], fixture_data: dict[str, object], failures: list[str]) -> dict[str, object]:
    out: dict[str, object] = {}
    for name in ("save000.dat", "save006.dat"):
        facts = fixture_data[name]
        if not facts["model_exact"]:
            continue
        path = Path(str(facts["path"]))
        data = path.read_bytes()
        static_prefix = int(facts["static_prefix_before_roster"])
        roster_records = int(facts["roster_records"])
        # The bulk block is immediately followed by its 0x170 trailer and the
        # 0x24*0x0a helper block before the variable roster.
        tail_after_bulk = 0x170 + 0x24 * 0x0A
        roster_offset = static_prefix
        if roster_offset != len(data) - roster_records * UNIT_STRIDE:
            failures.append(f"{name} roster offset disagreement")
        bulk_offset = roster_offset - tail_after_bulk - BULK_LEN
        player_offset = bulk_offset + (PLAYER_BASE - BULK_PTR)
        counts = Counter()
        type_counts = Counter()
        for index in range(roster_records):
            record_offset = roster_offset + index * UNIT_STRIDE
            owner = data[record_offset + 0x8E]
            unit_type = data[record_offset + 0x8D]
            counts[owner] += 1
            type_counts[unit_type] += 1
        slots = []
        for owner in range(8):
            slot = player_offset + owner * PLAYER_STRIDE
            nation, player_num, is_cpu, alliance = struct.unpack_from("<BBBB", data, slot)
            unit_count = counts.get(owner, 0)
            slots.append(
                {
                    "owner": owner,
                    "nation": nation,
                    "player_num": player_num,
                    "is_cpu": is_cpu,
                    "alliance": alliance,
                    "unit_records": unit_count,
                    "configured": nation != 0,
                    "record_bearing_active": nation != 0 and unit_count > 0,
                }
            )
        out[name] = {
            "bulk_file_offset": bulk_offset,
            "player0_file_offset": player_offset,
            "roster_file_offset": roster_offset,
            "absolute_unit_count": roster_records,
            "unit_records_by_owner": {str(k): counts[k] for k in sorted(counts)},
            "unit_type_kinds": len(type_counts),
            "unit_owner_ids_outside_0_7": {str(k): counts[k] for k in sorted(counts) if k > 7},
            "player_slots": slots,
        }
    return out


def main() -> int:
    failures: list[str] = []
    exe_sha = sha256(EXE)
    if exe_sha != EXPECTED_EXE_SHA:
        failures.append(f"original executable SHA mismatch: {exe_sha}")
    save_code = parsed_lines(disasm(SAVE_ENTRY, SAVE_END))
    fread_calls = [
        f"{address:#010x}"
        for address, op, args in save_code
        if op == "call" and target_of(args) == FREAD
    ]
    if fread_calls:
        failures.append(f"{FREAD:#x} was included as a save fread target: {fread_calls}")
    components = save_components()
    layer_order = [int(str(c["target"]), 16) for c in components if c["kind"] == "layer"]
    if layer_order != LAYER_TARGETS:
        failures.append(f"layer call order changed: {[f'{x:#x}' for x in layer_order]}")
    fixture_data = fixture_report(components, failures)
    players = player_report(components, fixture_data, failures) if not failures else {}
    report = {
        "exe_sha256": exe_sha,
        "scope": {
            "game_started": False,
            "wine_started": False,
            "xvfb_started": False,
            "runtime_harness_started": False,
            "original_tree_written": False,
            "fixture_written": False,
        },
        "model": {
            "save_entry": f"{SAVE_ENTRY:#010x}",
            "layer_call_count": len(layer_order),
            "components": components,
            "unit_stride": UNIT_STRIDE,
            "bulk": {"address": f"{BULK_PTR:#010x}", "bytes": BULK_LEN},
            "player_struct": {"address": f"{PLAYER_BASE:#010x}", "stride": PLAYER_STRIDE},
            "map_dimension_file_offsets": {
                "width": MAP_WIDTH_FILE_OFFSET,
                "height": MAP_HEIGHT_FILE_OFFSET,
            },
        },
        "fixtures": fixture_data,
        "players_save000_save006": players,
        "failures": failures,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
