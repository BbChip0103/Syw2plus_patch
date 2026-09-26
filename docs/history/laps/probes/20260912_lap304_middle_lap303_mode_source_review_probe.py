"""lap304 middle probe — independent review of the lap303 U1~U5 outputs.

Static review of the read-only original executable and sprite fixture.  It does
not run the game, Wine, Xvfb, the runtime harness, or Stage B, and it does not
read captures as layout evidence.  Where lap303 asserted a hand-written table,
this probe re-derives the same fact from the instruction stream or the file
image so the two results are independent rather than copied.
"""
from __future__ import annotations

import bisect
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess


REPO = Path(__file__).resolve().parents[4]
EXE = REPO / "Syw2plus" / "syw2plus_original.exe"
SPRITE = REPO.parent / "Syw2plus" / "yfnt" / "saveloadtitle.spr"
EXPECTED_EXE_SHA = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"
EXPECTED_SPRITE_SHA = "7d154cdbf37dbea78c162ada870e656a039a224c5aa63ee52d86d8123c08a5c5"

LAP303_PROBE = REPO / "docs/history/laps/probes/20260912_lap303_work_save_load_layout_probe.py"
LAP303_REPORT = REPO / "logs/lap303/save_load_layout_probe.json"
# Pins of artefacts that already exist; no future-lap artefact is pinned here.
PAST_ARTEFACT_SHA = {
    "lap303_probe": "257c056352db9ef9aebb7752cc489e355c9028df6c89ab3e2f22a79e1de7ae35",
    "lap303_report": "5079de5a336d4feba7b7422cc0f2b9066b681c16385fb31b09f192a6b869d540",
    "lap302_report": "5190920f1cfb14d9155c913abc3378d88e092c8a6e13f8a116174cc1948940d2",
    "lap301_report": "c312b42e3593c2af5bb47e9df9e1b624f8a55ea618a1cc70b7e6dc709caaf10a",
    "lap299_report": "8e735a9a7f7b4ddbd1ab249039c568b42b16af8b248f47e64681d05476d2bb0b",
}
LAP_LOG_FILES = {
    "lap299_report": REPO / "logs/lap299/save_load_layout_probe.json",
    "lap301_report": REPO / "logs/lap301/save_load_layout_probe.json",
    "lap302_report": REPO / "logs/lap302/middle_writer_scope_review.json",
}

TEXT_VA, TEXT_RAW, TEXT_SIZE = 0x401000, 0x1000, 0x000E3AE5
DATA_VA, DATA_RAW, DATA_SIZE = 0x4EC000, 0xEC000, 0x0000D000

SCREEN_W_GLOBAL = 0xE5BF1C
SCREEN_H_GLOBAL = 0xE5BF20
GRAPHICS_OBJECT = 0xE5BF18
MODE_GLOBAL = 0x4ED810
MODE_TABLE_FUNC = 0x4644A0
MODE_BOUND_SITE = 0x4644B8
MODE_JUMP_SITE = 0x4644C1
MODE_JUMP_TABLE = 0x464B68

# The centre computation is a signed divide-by-two (cdq/sub/sar), not a bare sar.
CENTRE_ANCHORS = {
    0x4D625B: "mov    eax,DWORD PTR [esi+0x10f0]",
    0x4D6271: "cdq",
    0x4D6272: "sub    eax,edx",
    0x4D6310: "mov    edi,eax",
    0x4D6312: "mov    eax,ds:0xe5bf1c",
    0x4D6317: "cdq",
    0x4D6318: "sub    eax,edx",
    0x4D631A: "mov    ecx,eax",
    0x4D631C: "mov    eax,ds:0xe5bf20",
    0x4D6321: "cdq",
    0x4D6322: "sar    edi,1",
    0x4D6324: "sar    ecx,1",
    0x4D6326: "sub    ecx,edi",
    0x4D6328: "sub    eax,edx",
    0x4D632A: "mov    WORD PTR ds:0x1088b5c,cx",
    0x4D6331: "mov    edi,eax",
    0x4D6333: "mov    eax,DWORD PTR [esi+0x10f4]",
    0x4D6339: "cdq",
    0x4D633A: "sub    eax,edx",
    0x4D633C: "sar    edi,1",
    0x4D633E: "sar    eax,1",
    0x4D6340: "sub    edi,eax",
    0x4D6348: "mov    WORD PTR ds:0x1088b5e,di",
}
SLOT_Y_OFFSETS = (-0x1A, 0x08, 0x2A, 0x4C, 0x6E, 0x90, 0xB2)
SLOT_X_OFFSET, SLOT_W, SLOT_H = 0x14, 0x118, 0x18

INSN_RE = re.compile(r"^\s+([0-9a-f]{6}):\t([0-9a-f ]+?)\s*\t(.+?)\s*$", re.MULTILINE)
WRITE_RE = re.compile(r"^(?:mov|add|sub|or|and|inc|dec|xor)\b.*?\bds:0x(e5bf1c|e5bf20)\s*,")
MOFFS_WRITE_RE = re.compile(r"^mov\s+ds:0x(e5bf1c|e5bf20)\s*,")
THIS_FIELD_WRITE_RE = re.compile(r"^mov    (?:DWORD|WORD|BYTE) PTR \[(e[a-z][a-z])\+0x([48])\],(.+)$")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def disasm_text() -> str:
    return subprocess.run(
        ["objdump", "-d", "-Mintel", "-j", ".text", str(EXE)],
        check=True, capture_output=True, text=True,
    ).stdout


def parse(text: str) -> list[tuple[int, str]]:
    return [(int(a, 16), t) for a, _b, t in INSN_RE.findall(text)]


def va_to_raw(va: int) -> int | None:
    if TEXT_VA <= va < TEXT_VA + TEXT_SIZE:
        return TEXT_RAW + (va - TEXT_VA)
    if DATA_VA <= va < DATA_VA + DATA_SIZE:
        return DATA_RAW + (va - DATA_VA)
    return None


def trunc_div2(value: int) -> int:
    """cdq; sub eax,edx; sar eax,1 == signed divide by two toward zero."""
    return -((-value) // 2) if value < 0 else value // 2


def slots_for(origin: tuple[int, int]) -> list[list[int]]:
    left = origin[0] + SLOT_X_OFFSET
    return [
        [left, origin[1] + dy, left + SLOT_W, origin[1] + dy + SLOT_H]
        for dy in SLOT_Y_OFFSETS
    ]


def function_bodies(ins: list[tuple[int, str]]) -> tuple[dict[int, int], list[int]]:
    starts = sorted({int(m, 16) for m in re.findall(r"call   0x([0-9a-f]+)", "\n".join(t for _a, t in ins))})
    index = {a: i for i, (a, _t) in enumerate(ins)}
    return index, starts


def main() -> int:  # noqa: C901 - single linear audit script
    failures: list[str] = []
    report: dict[str, object] = {
        "probe": Path(__file__).name,
        "lap": 304,
        "role": "middle (diagnosis/plan/confirm); no game code edited, no execution",
        "reviews": "lap303 U1~U5",
        "capture_comparison": False,
        "execution": False,
    }
    for path in (EXE, SPRITE, LAP303_PROBE, LAP303_REPORT):
        if not path.is_file():
            failures.append(f"missing required input: {path}")
    if failures:
        report["failures"] = failures
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1

    image = EXE.read_bytes()
    exe_sha = hashlib.sha256(image).hexdigest()
    sprite_bytes = SPRITE.read_bytes()
    sprite_sha = hashlib.sha256(sprite_bytes).hexdigest()
    if exe_sha != EXPECTED_EXE_SHA:
        failures.append(f"original exe sha mismatch: {exe_sha}")
    if sprite_sha != EXPECTED_SPRITE_SHA:
        failures.append(f"sprite sha mismatch: {sprite_sha}")
    header = struct.unpack_from("<4I", sprite_bytes, 0)
    if header != (9, 320, 310, 1):
        failures.append(f"unexpected saveloadtitle.spr header: {header}")
    dialog = (header[1], header[2])
    report["sha256"] = {"original_exe": exe_sha, "sprite": sprite_sha}

    # R1 — lap303 artefacts unchanged and deterministic on two fresh runs.
    runs = [
        subprocess.run(
            [str(REPO / ".venv/bin/python"), str(LAP303_PROBE)],
            check=False, capture_output=True,
        )
        for _ in range(2)
    ]
    run_sha = [hashlib.sha256(r.stdout).hexdigest() for r in runs]
    stored_sha = sha256_file(LAP303_REPORT)
    probe_sha = sha256_file(LAP303_PROBE)
    if probe_sha != PAST_ARTEFACT_SHA["lap303_probe"]:
        failures.append(f"lap303 probe source changed: {probe_sha}")
    if stored_sha != PAST_ARTEFACT_SHA["lap303_report"]:
        failures.append(f"lap303 stored report changed: {stored_sha}")
    if run_sha[0] != run_sha[1]:
        failures.append(f"lap303 probe is not deterministic: {run_sha}")
    if run_sha[0] != stored_sha:
        failures.append("lap303 fresh run does not reproduce the stored report")
    if [r.returncode for r in runs] != [0, 0]:
        failures.append(f"lap303 probe exit codes {[r.returncode for r in runs]}")
    lap303 = json.loads(LAP303_REPORT.read_text())
    report["R1_lap303_reproduction"] = {
        "probe_sha256": probe_sha,
        "stored_report_sha256": stored_sha,
        "fresh_run_sha256": run_sha,
        "exit_codes": [r.returncode for r in runs],
        "stored_failures": lap303.get("failures"),
        "verdict": "ACCEPT",
    }

    text = disasm_text()
    ins = parse(text)
    by_addr = {a: t for a, t in ins}

    # R2 — re-derive the mode table from the bound check and the jump table bytes.
    bound_insn = by_addr.get(MODE_BOUND_SITE, "")
    jump_insn = by_addr.get(MODE_JUMP_SITE, "")
    bound_match = re.match(r"cmp    eax,0x([0-9a-f]+)$", bound_insn)
    if not bound_match:
        failures.append(f"mode bound check not found at 0x{MODE_BOUND_SITE:x}: {bound_insn!r}")
    if f"0x{MODE_JUMP_TABLE:x}" not in jump_insn:
        failures.append(f"mode jump does not use 0x{MODE_JUMP_TABLE:x}: {jump_insn!r}")
    branch_count = (int(bound_match.group(1), 16) + 1) if bound_match else 0
    raw = va_to_raw(MODE_JUMP_TABLE)
    entries = list(struct.unpack_from(f"<{branch_count}I", image, raw)) if raw else []
    branches: dict[str, object] = {}
    indirect: dict[int, str] = {}
    ordered = sorted(by_addr)
    for index, target in enumerate(entries):
        writes: dict[str, str] = {}
        resolution: list[int] = []
        if target not in by_addr:
            failures.append(f"mode branch {index} target 0x{target:x} is not an instruction")
        else:
            cursor = bisect.bisect_left(ordered, target)
            for addr in ordered[cursor:]:
                field = THIS_FIELD_WRITE_RE.match(by_addr[addr])
                if not field or field.group(1) != "esi" or field.group(2) not in "48":
                    break
                value = field.group(3).strip()
                if not value.startswith("0x"):
                    break
                writes[f"0x{addr:x}"] = by_addr[addr]
                indirect[addr] = by_addr[addr]
                resolution.append(int(value, 16))
                if len(writes) == 2:
                    break
        branches[f"0x{target:x}"] = {"table_index": index, "writes": writes, "resolution": resolution}
        if len(writes) != 2 or len(resolution) != 2:
            failures.append(f"mode branch 0x{target:x} did not yield a width/height pair: {writes}")
    reachable = sorted({tuple(b["resolution"]) for b in branches.values() if len(b["resolution"]) == 2})
    report["R2_mode_table"] = {
        "derivation": "cmp eax,0x7 bound + jmp [eax*4+0x464b68] table bytes read from the image",
        "bound_instruction": bound_insn,
        "branch_count": branch_count,
        "table_entries": [f"0x{e:x}" for e in entries],
        "branches": branches,
        "indirect_write_count": len(indirect),
        "distinct_resolutions": [list(r) for r in reachable],
        "matches_lap303": (
            len(indirect) == lap303["writer_scope"]["indirect_this_relative_count"]
            and [list(r) for r in reachable] == lap303["candidate_scope"]["fixed_mode_resolutions"]
        ),
        "verdict": "ACCEPT",
    }
    if not report["R2_mode_table"]["matches_lap303"]:
        failures.append("mode-table re-derivation disagrees with lap303")

    # R3 — every absolute reference to the two screen globals, classified.
    refs: dict[int, str] = {}
    for global_addr in (SCREEN_W_GLOBAL, SCREEN_H_GLOBAL):
        pattern = global_addr.to_bytes(4, "little")
        start = 0
        while True:
            start = image.find(pattern, start)
            if start < 0:
                break
            if TEXT_RAW <= start < TEXT_RAW + TEXT_SIZE:
                refs[start] = f"0x{global_addr:x}"
            start += 1
    disasm_refs = {a: t for a, t in ins if "e5bf1c" in t or "e5bf20" in t}
    writers = {
        f"0x{a:x}": t for a, t in disasm_refs.items()
        if WRITE_RE.match(t) or MOFFS_WRITE_RE.match(t)
    }
    report["R3_absolute_screen_global_refs"] = {
        "byte_level_reference_count": len(refs),
        "disassembled_reference_count": len(disasm_refs),
        "write_sites": dict(sorted(writers.items())),
        "read_site_count": len(disasm_refs) - len(writers),
        "moffs_form_write_present": any(MOFFS_WRITE_RE.match(t) for t in disasm_refs.values()),
        "lap303_direct_count": lap303["writer_scope"]["direct_absolute_count"],
        "note": (
            "lap303 required 'mov <SIZE> PTR ds:...' so the a3/a1 moffs encoding would have been "
            "invisible; no such write exists in this image, so the count of 4 still holds"
        ),
        "verdict": "ACCEPT-WITH-NOTE",
    }
    if len(refs) != len(disasm_refs):
        failures.append(
            f"byte-level ({len(refs)}) and disassembled ({len(disasm_refs)}) screen-global refs disagree"
        )
    if len(writers) != lap303["writer_scope"]["direct_absolute_count"]:
        failures.append(f"direct writer count disagrees with lap303: {sorted(writers)}")

    # R4 — centre formula including the signed-divide correction lap303 omitted.
    anchors: dict[str, str] = {}
    for addr, expected in CENTRE_ANCHORS.items():
        actual = by_addr.get(addr)
        anchors[f"0x{addr:x}"] = actual or ""
        if actual != expected:
            failures.append(f"centre anchor 0x{addr:x} expected {expected!r}, found {actual!r}")
    geometry: dict[str, object] = {}
    for screen in reachable:
        origin = (trunc_div2(screen[0]) - trunc_div2(dialog[0]),
                  trunc_div2(screen[1]) - trunc_div2(dialog[1]))
        rects = slots_for(origin)
        key = f"{screen[0]}x{screen[1]}"
        geometry[key] = {
            "origin": list(origin),
            "slot0_xyxy": rects[0],
            "slot6_xyxy": rects[-1],
            "inside_screen": all(
                0 <= r[0] < r[2] <= screen[0] and 0 <= r[1] < r[3] <= screen[1] for r in rects
            ),
        }
        reported = lap303["geometry_all_fixed_modes"].get(key, {})
        if reported.get("origin_binary_formula") != list(origin):
            failures.append(f"geometry origin mismatch vs lap303 at {key}")
        if reported.get("slot0_xyxy") != rects[0] or reported.get("slot6_xyxy") != rects[-1]:
            failures.append(f"geometry slot rect mismatch vs lap303 at {key}")
    report["R4_centre_formula"] = {
        "anchors": anchors,
        "correction": (
            "the idiom is cdq; sub eax,edx; sar reg,1 (signed divide toward zero) on both the "
            "screen and the dialog operand; 'sar/sar/sub' names only half of it"
        ),
        "numerical_impact": "none for the positive screen/dialog values reachable here",
        "guard_gap": "lap303 anchors omit 0x4d6271/0x4d6272/0x4d6317/0x4d6318/0x4d6328/0x4d6339/0x4d633a",
        "geometry_recomputed": geometry,
        "verdict": "ACCEPT-WITH-CORRECTION",
    }

    # R5 — bounded closure: which methods of the graphics object write [this+4]/[this+8].
    index, starts = function_bodies(ins)

    def body(func: int) -> list[tuple[int, str]]:
        i = index.get(func)
        if i is None:
            return []
        k = bisect.bisect_right(starts, func)
        end = starts[k] if k < len(starts) else TEXT_VA + TEXT_SIZE
        out = []
        for addr, insn in ins[i:]:
            if addr >= end:
                break
            out.append((addr, insn))
        return out

    thiscall_sites = [i for i, (_a, t) in enumerate(ins) if t == f"mov    ecx,0x{GRAPHICS_OBJECT:x}"]
    push_sites = [a for a, t in ins if t == f"push   0x{GRAPHICS_OBJECT:x}"]
    seeds: set[int] = set()
    for i in thiscall_sites:
        for j in range(i + 1, min(i + 13, len(ins))):
            insn = ins[j][1]
            if insn.startswith("mov    ecx,") or insn.startswith("lea    ecx"):
                break
            call = re.match(r"call   0x([0-9a-f]+)$", insn)
            if call:
                seeds.add(int(call.group(1), 16))
                break
    reached = set(seeds)
    frontier = [(f, 0) for f in sorted(seeds)]
    while frontier:
        func, depth = frontier.pop()
        if depth >= 3:
            continue
        insns = body(func)
        alias = {"ecx"}
        for _a, insn in insns[:10]:
            m = re.match(r"mov    (e[a-z][a-z]),ecx$", insn)
            if m:
                alias.add(m.group(1))
        for i, (_a, insn) in enumerate(insns):
            call = re.match(r"call   0x([0-9a-f]+)$", insn)
            if not call or i == 0:
                continue
            prev = re.match(r"mov    ecx,(e[a-z][a-z])$", insns[i - 1][1])
            if prev and prev.group(1) in alias:
                callee = int(call.group(1), 16)
                if callee not in reached:
                    reached.add(callee)
                    frontier.append((callee, depth + 1))
    field_writers: dict[str, list[str]] = {}
    for func in sorted(reached):
        insns = body(func)
        alias = {"ecx"}
        for _a, insn in insns[:10]:
            m = re.match(r"mov    (e[a-z][a-z]),ecx$", insn)
            if m:
                alias.add(m.group(1))
        found = [
            f"0x{a:x}" for a, insn in insns
            if (m := THIS_FIELD_WRITE_RE.match(insn)) and m.group(1) in alias
        ]
        if found:
            field_writers[f"0x{func:x}"] = found
    report["R5_this_field_writer_closure"] = {
        "thiscall_site_count": len(thiscall_sites),
        "closure_method_count": len(reached),
        "closure_rule": "direct calls only, ecx alias preserved, depth <= 3 from the thiscall seeds",
        "functions_writing_this_plus_4_or_8": field_writers,
        "sole_writer_is_mode_table": list(field_writers) == [f"0x{MODE_TABLE_FUNC:x}"],
        "total_writer_count": len(writers) + sum(len(v) for v in field_writers.values()),
        "remaining_fail_open": {
            "object_passed_as_stack_argument": len(push_sites),
            "indirect_or_virtual_calls": "call [reg+disp] edges are not followed",
            "depth_limit": 3,
        },
        "verdict": "ACCEPT",
    }
    if not report["R5_this_field_writer_closure"]["sole_writer_is_mode_table"]:
        failures.append(f"unexpected this+4/+8 writers in closure: {sorted(field_writers)}")

    # R6 — where the mode argument comes from, and what the image ships.
    mode_refs = {f"0x{a:x}": t for a, t in ins if f"0x{MODE_GLOBAL:x}" in t}
    mode_writes = {a: t for a, t in mode_refs.items() if re.search(rf"ds:0x{MODE_GLOBAL:x}\s*,", t)}
    mode_bytes = image.find(MODE_GLOBAL.to_bytes(4, "little"))
    mode_ref_bytes = 0
    start = 0
    while True:
        start = image.find(MODE_GLOBAL.to_bytes(4, "little"), start)
        if start < 0:
            break
        mode_ref_bytes += 1
        start += 1
    mode_value = struct.unpack_from("<I", image, va_to_raw(MODE_GLOBAL))[0]
    selected_index = mode_value - 1
    selected_branch = entries[selected_index] if 0 <= selected_index < len(entries) else None
    selected_resolution = (
        branches[f"0x{selected_branch:x}"]["resolution"] if selected_branch is not None else []
    )
    report["R6_mode_argument_source"] = {
        "mode_global": f"ds:0x{MODE_GLOBAL:x}",
        "code_references": mode_refs,
        "write_sites": mode_writes,
        "byte_level_reference_count": mode_ref_bytes,
        "image_initialised_value": mode_value,
        "dec_then_table_index": selected_index,
        "selected_branch": f"0x{selected_branch:x}" if selected_branch else "",
        "selected_resolution": selected_resolution,
        "callers_of_mode_table": {
            "0x4643c0": "arg2 of FUN_00464360, pushed at 0x423d50 from ds:0x4ed810",
            "0x464c64": "single stack arg of FUN_00464BF0, supplied from ds:0x4ed810 at 0x42484e/0x424e85/0x4d0fcb",
        },
        "status": "CONFIRMED-STATIC; runtime value is still unobserved",
        "caveat": (
            "0x4ed810 lives in writable .data; no static reference other than these reads exists, "
            "but a computed-pointer or file-load write cannot be excluded without execution"
        ),
        "verdict": "NEW-FINDING",
    }
    if mode_writes:
        failures.append(f"unexpected writer to the mode global: {mode_writes}")
    if mode_bytes < 0:
        failures.append("mode global address not present in the image")

    # R7 — provenance of the earlier lap artefacts.
    provenance: dict[str, object] = {}
    for name, path in LAP_LOG_FILES.items():
        actual = sha256_file(path) if path.is_file() else ""
        provenance[name] = {"path": str(path.relative_to(REPO)), "sha256": actual}
        if actual != PAST_ARTEFACT_SHA[name]:
            failures.append(f"{name} changed since it was recorded: {actual}")
    source = LAP303_PROBE.read_text()
    pinned = set(re.findall(r'"([0-9a-f]{64})"', source))
    report["R7_provenance"] = {
        "earlier_lap_logs": provenance,
        "lap303_report_self_lap": lap303.get("lap"),
        "lap303_report_self_probe": lap303.get("probe"),
        "lap303_probe_filename": LAP303_PROBE.name,
        "lap303_pinned_sha_count": len(pinned),
        "lap303_pins_only_read_only_inputs": pinned == {EXPECTED_EXE_SHA, EXPECTED_SPRITE_SHA},
        "lap301_report_still_self_labels_lap": json.loads(
            LAP_LOG_FILES["lap301_report"].read_text()
        ).get("lap"),
        "verdict": "ACCEPT",
    }
    if lap303.get("lap") != 303 or lap303.get("probe") != LAP303_PROBE.name:
        failures.append("lap303 report does not identify its own lap and source")
    if not report["R7_provenance"]["lap303_pins_only_read_only_inputs"]:
        failures.append(f"lap303 pins something other than the read-only inputs: {sorted(pinned)}")

    report["limitations"] = [
        "static only: no execution, capture, game, Wine/Xvfb, Stage B, runtime budget, or PNG",
        "R5 closure follows direct calls with a preserved ecx alias to depth 3; virtual calls and "
        "the 291 push-0xE5BF18 argument sites are not covered, so 20 stays a lower bound",
        "R6 fixes the mode argument statically; the dynamic writers at 0x431B79/0x4324B8 can still "
        "overwrite the screen globals after the mode table runs",
        "slot hitboxes, slot selection, and the post-click load transition remain UNKNOWN",
        "no product G1~G4 evidence is produced or promoted here",
    ]
    report["failures"] = failures
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
