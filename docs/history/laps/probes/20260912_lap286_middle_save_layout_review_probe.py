"""Independent middle review of the lap284 work save-layout model.

This probe re-derives the original save serializer model from objdump output
without reusing the work probe's hard-coded layer list, helper list, window
boundaries, or classification heuristics.  It reads only the preserved original
executable and the four private fixture files.  It never starts the game, Wine,
Xvfb, or the runtime harness, and never writes to the original tree or fixtures.

Differences from the lap284 work probe, on purpose:
  * the save function range is cut at its own terminating `ret` and the
    exclusive `SAVE_END` contract, not at the neighbouring load entry;
  * every layer body is bounded by its own padding run instead of by the next
    layer address, so a neighbouring load routine cannot contaminate the
    classification;
  * layer element width and repeat count are read from the decoded fwrite
    argument pushes and the decremented loop register, not from substring
    matches on the whole window;
  * every non-modelled callee of the save function is transitively scanned for
    reachable fwrite sites.
"""
from __future__ import annotations

import hashlib
import json
import re
import struct
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
EXE = REPO / "Syw2plus" / "syw2plus_original.exe"
EXPECTED_EXE_SHA = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"

SAVE_ENTRY, SAVE_END = 0x440C20, 0x440F5B  # exclusive; ret is at SAVE_END - 1
FWRITE = 0x4DA39F
FREAD = 0x4DA4A9  # neighbouring load routine; never a save fwrite target
SAVE_ROSTER = 0x40F4B0
UNIT_STRIDE = 0x758
BULK_PTR = 0x892410
PLAYER_BASE, PLAYER_STRIDE = 0x956770, 0x3ABC
MAP_WIDTH_FILE_OFFSET, MAP_HEIGHT_FILE_OFFSET = 210, 212
MAP_DIMENSION_GUARD = range(1, 181)
PAD_RUN = 4  # consecutive nops that mark the end of a function body

WORK_PROBE_OUTPUT = REPO / "logs" / "lap284" / "work_save_layout_probe.json"

FIXTURES = {
    "save000.dat": (REPO.parent / "Syw2plus" / "save" / "save000.dat", 3_093_902,
                    "1c703551888f5c85a1fa2fb7b43d28309eb0b88e4bbf6e859f1a98b629e719da"),
    "save006.dat": (REPO.parent / "Syw2plus" / "save" / "save006.dat", 3_437_942,
                    "616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064"),
    "save011.dat": (REPO / "local" / "fixtures" / "20260910" / "save011.dat", 1_982_062,
                    "23dd24d58555588e0ca09491559aed66ad3f2544ff3195c5af2ab9e2be14dfa4"),
    "save012.dat": (REPO / "local" / "fixtures" / "20260910" / "save012.dat", 1_985_822,
                    "5a6863c1eafaa8bd9a087238a41d45c45635dd66a208cf79a186e158819c28f1"),
}

LINE_RE = re.compile(r"^\s*([0-9a-f]+):\s+((?:[0-9a-f]{2} )+)\s*(\S+)(?:\s+(.*))?$")
HEX_RE = re.compile(r"0x[0-9a-f]+")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def disasm(start: int, stop: int) -> list[tuple[int, str, str]]:
    text = subprocess.run(
        ["objdump", "-d", "-Mintel", "-j", ".text",
         f"--start-address={start:#x}", f"--stop-address={stop:#x}", str(EXE)],
        check=True, capture_output=True, text=True,
    ).stdout
    out: list[tuple[int, str, str]] = []
    for line in text.splitlines():
        m = LINE_RE.match(line)
        if m:
            out.append((int(m.group(1), 16), m.group(3), (m.group(4) or "").strip()))
    return out


def body(start: int, limit: int = 0x600) -> list[tuple[int, str, str]]:
    """Instructions of one function.

    The body ends at the first `ret` that no earlier branch jumps past, which
    also terminates functions that are not followed by nop padding (0x440AC0
    runs straight into the save entry at 0x440C20).  A padding run ends the body
    too, for the tail-call shapes that never reach a `ret`.
    """
    lines = disasm(start, start + limit)
    out: list[tuple[int, str, str]] = []
    run = 0
    furthest_target = start
    for address, op, args in lines:
        if op == "nop":
            run += 1
            if run >= PAD_RUN:
                return out
            continue
        if run:
            out.extend([(0, "nop", "")] * run)
            run = 0
        out.append((address, op, args))
        if op.startswith("j"):
            target = imm(args.split()[0]) if args.split() else None
            if target is not None and target > furthest_target:
                furthest_target = target
        if op == "ret" and address >= furthest_target:
            return out
    return out


def imm(token: str) -> int | None:
    return int(token, 16) if re.fullmatch(r"0x[0-9a-f]+", token) else None


def call_target(args: str) -> int | None:
    head = args.split()[0] if args.split() else ""
    return imm(head)


def fwrite_sites(code: list[tuple[int, str, str]]) -> list[dict[str, object]]:
    """Decode (ptr, size, count) from the four pushes preceding each fwrite."""
    pushes: list[str] = []
    sites: list[dict[str, object]] = []
    for address, op, args in code:
        if op == "push":
            pushes.append(args)
            continue
        if op == "call":
            if call_target(args) == FWRITE and len(pushes) >= 4:
                _file, count_raw, size_raw, ptr_raw = pushes[-4:]
                sites.append({
                    "site": f"{address:#010x}",
                    "count_token": count_raw,
                    "count": imm(count_raw),
                    "size": imm(size_raw),
                    "ptr": imm(ptr_raw),
                })
            pushes = []
    return sites


def classify_layer(start: int) -> dict[str, object]:
    """Re-derive one layer's byte formula from its own function body only."""
    code = body(start)
    sites = fwrite_sites(code)
    if len(sites) != 1:
        return {"target": f"{start:#010x}", "error": f"{len(sites)} fwrite sites"}
    site = sites[0]
    element = site["size"]
    text = " | ".join(f"{op} {args}" for _a, op, args in code)
    # A halving layer applies the signed div-by-2 idiom (cdq; sub; sar 1) twice.
    halvings = len(re.findall(r"sar +e[a-z]x,1", text))
    # A repeated layer loads a literal loop counter and decrements it.
    repeat = 1
    m = re.search(r"mov +(e[a-z]x),0x([0-9a-f]+)", text)
    if m and f"dec {m.group(1)}" in text:
        repeat = int(m.group(2), 16)
    if site["count"] is not None:
        return {"target": f"{start:#010x}", "mode": "fixed_count", "repeat": repeat,
                "element_bytes": element, "fixed_bytes": site["count"] * element,
                "area_coefficient": 0.0, "halvings": halvings, "fwrite": site}
    if halvings == 2:
        mode, coefficient = "quarter_area", 0.25
    elif halvings == 0:
        mode, coefficient = "full_area", 1.0
    else:
        return {"target": f"{start:#010x}", "error": f"unexpected halving count {halvings}"}
    return {"target": f"{start:#010x}", "mode": mode, "repeat": repeat,
            "element_bytes": element, "fixed_bytes": 0,
            "area_coefficient": coefficient * repeat * element,
            "halvings": halvings, "fwrite": site}


def reaches_fwrite(start: int, max_depth: int = 3) -> list[str]:
    """Bounded transitive scan for fwrite sites reachable from `start`."""
    found: list[str] = []
    seen: set[int] = set()

    def walk(target: int, depth: int) -> None:
        if depth > max_depth or target in seen:
            return
        seen.add(target)
        for address, op, args in body(target):
            if op != "call":
                continue
            callee = call_target(args)
            if callee == FWRITE:
                found.append(f"{address:#010x}->fwrite")
            elif callee is not None and 0x401000 <= callee < 0x4D0000:
                walk(callee, depth + 1)

    walk(start, 0)
    return found


def main() -> int:
    failures: list[str] = []
    notes: list[str] = []

    exe_sha = sha256(EXE)
    if exe_sha != EXPECTED_EXE_SHA:
        failures.append(f"original executable SHA mismatch: {exe_sha}")

    save_code = body(SAVE_ENTRY, limit=SAVE_END - SAVE_ENTRY)
    save_end = save_code[-1][0] if save_code else 0
    if save_code[-1][1] != "ret":
        failures.append(f"save body does not end in ret: {save_code[-1]}")
    if save_end != SAVE_END - 1:
        failures.append(
            f"save body end changed: expected {SAVE_END - 1:#x}, got {save_end:#x}"
        )

    fread_calls = [
        f"{address:#010x}"
        for address, op, args in save_code
        if op == "call" and call_target(args) == FREAD
    ]
    if fread_calls:
        failures.append(f"{FREAD:#x} was included as a save fwrite target: {fread_calls}")

    direct_fwrite = fwrite_sites(save_code)
    layers: list[int] = []
    helpers: list[int] = []
    roster: list[int] = []
    others: list[int] = []
    for address, op, args in save_code:
        if op != "call":
            continue
        target = call_target(args)
        if target is None or target == FWRITE:
            continue
        if 0x42A000 <= target < 0x42C000:
            layers.append(target)
        elif target == SAVE_ROSTER:
            roster.append(target)
        elif target in (0x403950, 0x4441E0, 0x4464B0):
            helpers.append(target)
        else:
            others.append(target)

    if len(layers) != 28:
        failures.append(f"expected 28 layer calls, got {len(layers)}")
    if len(set(layers)) != len(layers):
        failures.append("a layer target is called more than once")
    if len(roster) != 1:
        failures.append(f"expected one roster call, got {len(roster)}")
    if len(helpers) != 3:
        failures.append(f"expected three nested helper calls, got {len(helpers)}")

    # Completeness: every callee that the size model ignores must write no bytes.
    hidden: dict[str, list[str]] = {}
    for target in sorted(set(others)):
        reached = reaches_fwrite(target)
        if reached:
            hidden[f"{target:#010x}"] = reached
            failures.append(f"ignored callee {target:#010x} reaches fwrite: {reached}")

    helper_bytes = 0
    helper_detail = []
    for target in helpers:
        sites = fwrite_sites(body(target))
        if len(sites) != 1 or sites[0]["count"] is None or sites[0]["size"] is None:
            failures.append(f"helper {target:#010x} is not a single fixed fwrite: {sites}")
            continue
        block = int(sites[0]["count"]) * int(sites[0]["size"])
        helper_bytes += block
        helper_detail.append({"helper": f"{target:#010x}", "bytes": block, "fwrite": sites[0]})

    literal_bytes = 0
    for site in direct_fwrite:
        if site["count"] is None or site["size"] is None:
            failures.append(f"non-static direct fwrite at {site['site']}")
            continue
        literal_bytes += int(site["count"]) * int(site["size"])

    layer_models = [classify_layer(target) for target in layers]
    for model in layer_models:
        if "error" in model:
            failures.append(f"layer {model['target']}: {model['error']}")
    fixed_layer_bytes = sum(int(m.get("fixed_bytes", 0)) for m in layer_models if "error" not in m)
    area_coefficient = sum(float(m["area_coefficient"]) for m in layer_models if "error" not in m)

    constant = literal_bytes + helper_bytes + fixed_layer_bytes

    fixture_report: dict[str, object] = {}
    for name, (path, expected_size, expected_sha) in FIXTURES.items():
        if not path.is_file():
            failures.append(f"missing fixture: {path}")
            continue
        actual_size = path.stat().st_size
        actual_sha = sha256(path)
        if actual_size != expected_size:
            failures.append(f"{name} size changed: {actual_size}")
        if actual_sha != expected_sha:
            failures.append(f"{name} SHA changed: {actual_sha}")
        data = path.read_bytes()
        width, height = struct.unpack_from("<HH", data, MAP_WIDTH_FILE_OFFSET)
        if width not in MAP_DIMENSION_GUARD or height not in MAP_DIMENSION_GUARD:
            failures.append(f"{name} map dimensions outside guard: {width}x{height}")
        area = width * height
        scaled = area_coefficient * area
        if scaled != int(scaled):
            failures.append(f"{name} area coefficient is not integral for area {area}")
        prefix = constant + int(scaled)
        remainder = actual_size - prefix
        integral = remainder >= 0 and remainder % UNIT_STRIDE == 0
        if not integral:
            failures.append(f"{name} remainder {remainder} is not a multiple of {UNIT_STRIDE}")
        fixture_report[name] = {
            "sha256": actual_sha,
            "size": actual_size,
            "width": width,
            "height": height,
            "square": width == height,
            "even_dimensions": width % 2 == 0 and height % 2 == 0,
            "static_prefix_before_roster": prefix,
            "roster_remainder": remainder,
            "roster_records": remainder // UNIT_STRIDE if integral else None,
        }

    # Rebuild the payload in call order so the bulk block's file offset, and the
    # PlayerStruct offsets the work card derives from it, are checked and not assumed.
    ordered: list[tuple[str, object]] = []
    pushes: list[str] = []
    layer_by_target = {m["target"]: m for m in layer_models}
    helper_by_target = {h["helper"]: h for h in helper_detail}
    for address, op, args in save_code:
        if op == "push":
            pushes.append(args)
            continue
        if op != "call":
            continue
        target = call_target(args)
        if target == FWRITE and len(pushes) >= 4:
            _file, count_raw, size_raw, ptr_raw = pushes[-4:]
            ordered.append(("literal", {
                "bytes": int(imm(count_raw)) * int(imm(size_raw)),
                "ptr": imm(ptr_raw),
            }))
        elif target is not None and f"{target:#010x}" in layer_by_target:
            ordered.append(("layer", layer_by_target[f"{target:#010x}"]))
        elif target is not None and f"{target:#010x}" in helper_by_target:
            ordered.append(("helper", helper_by_target[f"{target:#010x}"]))
        elif target == SAVE_ROSTER:
            ordered.append(("roster", {}))
        pushes = []

    players: dict[str, object] = {}
    for name, facts in fixture_report.items():
        if facts["roster_records"] is None:
            continue
        area = facts["width"] * facts["height"]
        cursor = 0
        bulk_offset = None
        for kind, item in ordered:
            if kind == "literal":
                if item["ptr"] == BULK_PTR:
                    bulk_offset = cursor
                cursor += int(item["bytes"])
            elif kind == "helper":
                cursor += int(item["bytes"])
            elif kind == "layer":
                cursor += int(item["fixed_bytes"]) + int(float(item["area_coefficient"]) * area)
            else:
                break
        if cursor != facts["static_prefix_before_roster"]:
            failures.append(f"{name} ordered walk disagrees with summed prefix: {cursor}")
        if bulk_offset is None:
            failures.append(f"{name} bulk block {BULK_PTR:#x} not found in call order")
            continue
        data = Path(FIXTURES[name][0]).read_bytes()
        player_offset = bulk_offset + (PLAYER_BASE - BULK_PTR)
        roster_offset = cursor
        histogram: dict[int, int] = {}
        for index in range(int(facts["roster_records"])):
            owner = data[roster_offset + index * UNIT_STRIDE + 0x8E]
            histogram[owner] = histogram.get(owner, 0) + 1
        slots = []
        for owner in range(8):
            nation, player_num, is_cpu, alliance = struct.unpack_from(
                "<BBBB", data, player_offset + owner * PLAYER_STRIDE)
            slots.append({"owner": owner, "nation": nation, "player_num": player_num,
                          "is_cpu": is_cpu, "alliance": alliance,
                          "unit_records": histogram.get(owner, 0)})
        if sum(histogram.values()) != facts["roster_records"]:
            failures.append(f"{name} owner histogram does not sum to the record count")
        players[name] = {
            "bulk_file_offset": bulk_offset,
            "player0_file_offset": player_offset,
            "roster_file_offset": roster_offset,
            "unit_records_by_owner": {str(k): histogram[k] for k in sorted(histogram)},
            "owner_ids_outside_0_7": {str(k): histogram[k] for k in sorted(histogram) if k > 7},
            "player_slots": slots,
        }

    # Cross-check against the lap284 work probe's recorded numbers.
    cross: dict[str, object] = {}
    if WORK_PROBE_OUTPUT.is_file():
        work = json.loads(WORK_PROBE_OUTPUT.read_text())
        for name, facts in fixture_report.items():
            recorded = work["fixtures"].get(name, {})
            same_prefix = recorded.get("static_prefix_before_roster") == facts["static_prefix_before_roster"]
            same_records = recorded.get("roster_records") == facts["roster_records"]
            cross[name] = {"same_static_prefix": same_prefix, "same_roster_records": same_records}
            if not (same_prefix and same_records):
                failures.append(f"{name} disagrees with lap284 work probe: {recorded}")
        for name, facts in players.items():
            recorded = work.get("players_save000_save006", {}).get(name)
            if recorded is None:
                continue
            agree = (recorded["bulk_file_offset"] == facts["bulk_file_offset"]
                     and recorded["player0_file_offset"] == facts["player0_file_offset"]
                     and recorded["roster_file_offset"] == facts["roster_file_offset"]
                     and recorded["unit_records_by_owner"] == facts["unit_records_by_owner"])
            cross.setdefault("players", {})[name] = {"same_offsets_and_histogram": agree}
            if not agree:
                failures.append(f"{name} player/roster facts disagree with lap284 work probe")
    else:
        failures.append(f"missing work probe output: {WORK_PROBE_OUTPUT}")

    # Limits this probe cannot close; recorded so they are not read as verified.
    if all(f["square"] for f in fixture_report.values()):
        notes.append("all four fixtures are square, so the width/height file-offset "
                     "assignment (210 vs 212) is not distinguished by this evidence")
    if all(f["even_dimensions"] for f in fixture_report.values()):
        notes.append("all four fixtures have even dimensions, so the halving layers' "
                     "((w/2)*h)/2 truncation cannot be told apart from (w*h)/4 here")
    notes.append("per-layer full/quarter assignment is not uniquely determined by file "
                 "size: swapping one full layer with one quarter layer preserves the total")
    notes.append("roster record count is solved from the remainder, so 'exact "
                 "reconstruction' is the integrality test, not a second independent test")

    report = {
        "exe_sha256": exe_sha,
        "scope": {"game_started": False, "wine_started": False, "xvfb_started": False,
                  "runtime_harness_started": False, "original_tree_written": False,
                  "fixture_written": False},
        "save_function": {
            "entry": f"{SAVE_ENTRY:#010x}",
            "exclusive_end": f"{SAVE_END:#010x}",
            "last_instruction": f"{save_end:#010x}",
            "direct_fwrite_calls": len(direct_fwrite),
            "fread_calls_in_save": fread_calls,
            "layer_calls": len(layers),
            "helper_calls": len(helpers),
            "roster_calls": len(roster),
            "ignored_callees": [f"{t:#010x}" for t in sorted(set(others))],
            "ignored_callees_reaching_fwrite": hidden,
        },
        "model": {
            "literal_bytes": literal_bytes,
            "helper_bytes": helper_bytes,
            "helper_detail": helper_detail,
            "fixed_layer_bytes": fixed_layer_bytes,
            "constant_bytes": constant,
            "area_coefficient": area_coefficient,
            "layers": layer_models,
            "unit_stride": UNIT_STRIDE,
        },
        "fixtures": fixture_report,
        "players": players,
        "cross_check_vs_lap284_work": cross,
        "limits": notes,
        "failures": failures,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
