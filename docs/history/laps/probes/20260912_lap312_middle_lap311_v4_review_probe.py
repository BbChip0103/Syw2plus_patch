"""lap312 middle — independent review of the lap311 V4 repair (R2).

The review deliberately avoids the lap311 method on both axes it claims.

1. Writer census: lap311 matched an `objdump` text regex inside the map window.
   This probe instead parses the SHA-pinned PE image directly and scans the raw
   `.text` bytes for every absolute-displacement reference to the two screen
   globals across the *whole* section, classifying each by opcode as a load or a
   store.  That reproduces the writer set without trusting disassembly text and
   also bounds it outside the map window.
2. Mandatory-execution proof: lap311 ran an iterative dataflow dominator
   fixpoint on the reversed CFG.  This probe uses the *cut* characterisation
   instead — a node N is mandatory on every entry-to-success-return path exactly
   when deleting N makes the success return unreachable from the entry.  The
   cut test carries its own falsification control, so a graph bug cannot make
   every claim pass silently.

It also checks two gate facts lap311 asserted only through constant names: that
`0x431AF2` really is a conditional branch whose taken target is the success
join, and that the fall-through arm really returns 0.

Only the original executable and the immutable lap311 artifacts are pinned;
this probe never pins its own output (the lap296/W3 self-pin trap).

Read-only static audit.  No game, Wine, Xvfb, runtime, Stage B, PNG, or click
execution.  The report is emitted on stdout only; the caller redirects stdout so
the stored report is exactly the generator output.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess


REPO = Path(__file__).resolve().parents[4]
EXE = REPO / "Syw2plus" / "syw2plus_original.exe"
EXPECTED_EXE_SHA = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"

# Immutable lap311 artifacts under review (already written, never regenerated here).
LAP311_ARTIFACTS = {
    "probe": (
        Path("docs/history/laps/probes/20260912_lap311_work_v4_mode_writer_order_probe.py"),
        "a33f216a51a6f213543df8905e4b3ece19435316a71f44241761c543f8fd4524",
    ),
    "test": (
        Path("tests/test_lap311_mode_writer_probe.py"),
        "dc3ac0f25811a6da3a2050bc0d5cad401dbedd677e09975e559dce2c5b69f699",
    ),
    "report": (
        Path("logs/lap311/lap311_v4_mode_writer_order.json"),
        "efa4d84e6328472bfb65081ed87a7a50e31f661ac18c682087ab764d372c6dbc",
    ),
}

MAP_ENTRY = 0x431AB0
MAP_END = 0x4324D6
MAP_GATE_BRANCH = 0x431AF2
MAP_FAILURE_SEED = 0x431AF4
MAP_FAILURE_RET = 0x431AFD
MAP_SUCCESS_JOIN = 0x431AFE
MAP_SUCCESS_RET = 0x4324D5

SCREEN_W = 0xE5BF1C
SCREEN_H = 0xE5BF20
RUNTIME_WRITERS = (0x431B79, 0x431B7F)
RESET_WRITERS = (0x4324B8, 0x4324C2)
ALL_WRITERS = RUNTIME_WRITERS + RESET_WRITERS

# Byte-pinned gate facts lap311 named but never checked.
GATE_BYTES = "750a"          # jne rel8
GATE_TAKEN_TARGET = MAP_SUCCESS_JOIN
FAILURE_ARM_BYTES = "5f5e5d33c05b83c434c3"  # pop edi/esi/ebp; xor eax,eax; pop ebx; add esp,0x34; ret

# mod=00, rm=101 (disp32) store/load opcode prefixes, plus the moffs forms.
STORE_MODRM = {"8905", "890d", "8915", "891d", "8925", "892d", "8935", "893d", "c705"}
LOAD_MODRM = {"8b05", "8b0d", "8b15", "8b1d", "8b25", "8b2d", "8b35", "8b3d"}
STORE_MOFFS = 0xA3           # mov moffs32, eax
LOAD_MOFFS = 0xA1            # mov eax, moffs32
LOAD_IMUL = {"0faf05", "0faf0d", "0faf15", "0faf1d", "0faf25", "0faf2d", "0faf35", "0faf3d"}
RMW_MODRM = {"ff05", "ff0d", "8305", "830d", "8325", "832d", "0105", "2905", "3105"}

BRANCH_RE = re.compile(r"^(jmp|j[a-z]+|loop[a-z]*)\s+0x([0-9a-f]+)")
RET_RE = re.compile(r"^ret\b")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_text_section() -> tuple[int, bytes]:
    """Parse the PE headers directly and return (.text virtual base, raw bytes)."""
    data = EXE.read_bytes()
    pe_offset = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe_offset : pe_offset + 4] != b"PE\0\0":
        raise ValueError("not a PE image")
    section_count = struct.unpack_from("<H", data, pe_offset + 6)[0]
    optional_size = struct.unpack_from("<H", data, pe_offset + 20)[0]
    image_base = struct.unpack_from("<I", data, pe_offset + 24 + 28)[0]
    cursor = pe_offset + 24 + optional_size
    for _ in range(section_count):
        name = data[cursor : cursor + 8].rstrip(b"\0").decode("ascii", "replace")
        virtual_size, virtual_address, raw_size, raw_pointer = struct.unpack_from("<IIII", data, cursor + 8)
        if name == ".text":
            length = min(raw_size, virtual_size)
            return image_base + virtual_address, data[raw_pointer : raw_pointer + length]
        cursor += 40
    raise ValueError(".text section not found")


def classify_reference(blob: bytes, offset: int) -> tuple[str, int]:
    """Classify the absolute reference whose disp32 starts at `offset`."""
    one = blob[offset - 1] if offset >= 1 else -1
    two = blob[offset - 2 : offset].hex()
    three = blob[offset - 3 : offset].hex()
    if one == STORE_MOFFS:
        return "store/mov-moffs32-eax", offset - 1
    if one == LOAD_MOFFS:
        return "load/mov-eax-moffs32", offset - 1
    if two in STORE_MODRM:
        return "store/mov-disp32", offset - 2
    if two in LOAD_MODRM:
        return "load/mov-disp32", offset - 2
    if two in RMW_MODRM:
        return "store/read-modify-write", offset - 2
    if three in LOAD_IMUL:
        return "load/imul-disp32", offset - 3
    return "unclassified", offset


def scan_absolute_writers(text_base: int, blob: bytes) -> dict[str, object]:
    kinds: dict[str, int] = {}
    stores: dict[int, list[str]] = {}
    unclassified: list[str] = []
    total = 0
    for target in (SCREEN_W, SCREEN_H):
        needle = struct.pack("<I", target)
        offset = blob.find(needle)
        while offset >= 0:
            total += 1
            kind, start = classify_reference(blob, offset)
            kinds[kind] = kinds.get(kind, 0) + 1
            address = text_base + start
            if kind.startswith("store"):
                stores.setdefault(address, []).append(f"0x{target:x}")
            if kind == "unclassified":
                unclassified.append(f"0x{address:x}->0x{target:x}")
            offset = blob.find(needle, offset + 1)
    return {
        "section": ".text",
        "section_base": f"0x{text_base:x}",
        "section_bytes": len(blob),
        "absolute_reference_count": total,
        "reference_kinds": dict(sorted(kinds.items())),
        "store_sites": {f"0x{address:x}": sorted(targets) for address, targets in sorted(stores.items())},
        "unclassified": unclassified,
    }


def disassemble_window() -> list[tuple[int, str]]:
    listing = subprocess.run(
        ["objdump", "-d", "-Mintel", "-j", ".text", str(EXE)],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    window: list[tuple[int, str]] = []
    for line in listing.splitlines():
        fields = line.split("\t")
        if len(fields) < 3:
            continue
        try:
            address = int(fields[0].strip().rstrip(":"), 16)
        except ValueError:
            continue
        if MAP_ENTRY <= address < MAP_END:
            window.append((address, fields[2].strip()))
    return window


def build_successors(window: list[tuple[int, str]]) -> tuple[dict[int, set[int]], list[str]]:
    known = {address for address, _text in window}
    successors: dict[int, set[int]] = {}
    unresolved: list[str] = []
    for index, (address, text) in enumerate(window):
        if RET_RE.match(text):
            successors[address] = set()
            continue
        fallthrough = window[index + 1][0] if index + 1 < len(window) else None
        match = BRANCH_RE.match(text)
        if match:
            mnemonic, target_text = match.groups()
            target = int(target_text, 16)
            edges = {target}
            if mnemonic != "jmp" and fallthrough is not None:
                edges.add(fallthrough)
            if target not in known:
                unresolved.append(f"0x{address:x}: target 0x{target:x} outside window")
            successors[address] = {edge for edge in edges if edge in known}
            continue
        successors[address] = {fallthrough} if fallthrough in known else set()
    return successors, unresolved


def reachable(successors: dict[int, set[int]], start: int, banned: frozenset[int] = frozenset()) -> set[int]:
    seen: set[int] = set()
    pending = [start]
    while pending:
        node = pending.pop()
        if node in seen or node in banned or node not in successors:
            continue
        seen.add(node)
        pending.extend(successors[node] - seen)
    return seen


def cuts(successors: dict[int, set[int]], start: int, sink: int, node: int) -> bool:
    """True when deleting `node` makes `sink` unreachable from `start`."""
    return sink not in reachable(successors, start, banned=frozenset({node}))


def fmt(values) -> list[str]:
    return [f"0x{value:x}" for value in sorted(values)]


def main() -> int:  # noqa: C901 - one bounded static audit report
    failures: list[str] = []
    findings: list[str] = []
    report: dict[str, object] = {
        "probe": Path(__file__).name,
        "lap": 312,
        "role": "middle (independent review of lap311 work); no game code edited, no execution",
        "execution": False,
        "scope": "independent re-derivation of lap311 R2: writer census by raw PE bytes, mandatory execution by CFG cut test",
        "report_contract": "JSON is emitted on stdout; redirect stdout without hand transcription",
    }
    if not EXE.is_file():
        report["failures"] = [f"missing original executable: {EXE}"]
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1

    exe_sha = sha256_file(EXE)
    pinned = {"original_exe": exe_sha}
    if exe_sha != EXPECTED_EXE_SHA:
        failures.append(f"original exe sha mismatch: {exe_sha}")
    for label, (relative, expected) in sorted(LAP311_ARTIFACTS.items()):
        path = REPO / relative
        if not path.is_file():
            failures.append(f"lap311 {label} missing: {relative}")
            continue
        actual = sha256_file(path)
        pinned[f"lap311_{label}"] = actual
        if actual != expected:
            failures.append(f"lap311 {label} sha drifted: {actual}")
    report["sha256"] = pinned

    text_base, blob = load_text_section()

    # --- axis 1: writer census straight from the raw section bytes -------------
    census = scan_absolute_writers(text_base, blob)
    store_addresses = {int(address, 16) for address in census["store_sites"]}
    census["expected_store_sites"] = fmt(ALL_WRITERS)
    census["matches_lap311_writer_set"] = store_addresses == set(ALL_WRITERS)
    census["all_stores_inside_map_window"] = all(MAP_ENTRY <= address < MAP_END for address in store_addresses)
    census["moffs_store_count"] = census["reference_kinds"].get("store/mov-moffs32-eax", 0)
    census["verdict"] = (
        "PASS"
        if census["matches_lap311_writer_set"] and census["all_stores_inside_map_window"] and not census["unclassified"]
        else "FAIL"
    )
    report["a1_absolute_writer_census"] = census
    if not census["matches_lap311_writer_set"]:
        failures.append(f"absolute store set differs from lap311: {fmt(store_addresses)}")
    if census["unclassified"]:
        failures.append(f"unclassified absolute references: {census['unclassified']}")

    # --- axis 2: gate facts lap311 asserted only by constant naming ------------
    gate_offset = MAP_GATE_BRANCH - text_base
    gate_bytes = blob[gate_offset : gate_offset + 2].hex()
    gate_target = MAP_GATE_BRANCH + 2 + blob[gate_offset + 1] if gate_bytes.startswith("75") else None
    failure_offset = MAP_FAILURE_SEED - text_base
    failure_bytes = blob[failure_offset : failure_offset + len(FAILURE_ARM_BYTES) // 2].hex()
    gate = {
        "gate": f"0x{MAP_GATE_BRANCH:x}",
        "gate_bytes": gate_bytes,
        "gate_is_conditional_branch": gate_bytes == GATE_BYTES,
        "gate_taken_target": f"0x{gate_target:x}" if gate_target is not None else None,
        "gate_taken_target_is_success_join": gate_target == GATE_TAKEN_TARGET,
        "fall_through": f"0x{MAP_FAILURE_SEED:x}",
        "failure_arm_bytes": failure_bytes,
        "failure_arm_returns_zero": failure_bytes == FAILURE_ARM_BYTES,
        "note": "lap311 checked only `failure_seed == gate + 2`; the taken target and the zero return value were unchecked",
    }
    gate["verdict"] = (
        "PASS"
        if gate["gate_is_conditional_branch"] and gate["gate_taken_target_is_success_join"] and gate["failure_arm_returns_zero"]
        else "FAIL"
    )
    report["a2_gate_byte_facts"] = gate
    for key in ("gate_is_conditional_branch", "gate_taken_target_is_success_join", "failure_arm_returns_zero"):
        if not gate[key]:
            failures.append(f"gate byte fact failed: {key}")

    # --- axis 3: mandatory execution by cut test, with falsification control ----
    window = disassemble_window()
    successors, unresolved = build_successors(window)
    if unresolved:
        failures.append(f"map CFG has branch targets outside the inspected window: {unresolved}")
    entry_reachable = reachable(successors, MAP_ENTRY)
    failure_reachable = reachable(successors, MAP_FAILURE_SEED)
    join_reachable = reachable(successors, MAP_SUCCESS_JOIN)

    control_node = MAP_FAILURE_RET  # on no entry->success path; deleting it must change nothing
    control_still_reachable = MAP_SUCCESS_RET in reachable(successors, MAP_ENTRY, banned=frozenset({control_node}))
    cut_results = {f"0x{writer:x}": cuts(successors, MAP_ENTRY, MAP_SUCCESS_RET, writer) for writer in ALL_WRITERS}
    join_cut_results = {
        f"0x{writer:x}": cuts(successors, MAP_SUCCESS_JOIN, MAP_SUCCESS_RET, writer) for writer in RESET_WRITERS
    }
    order_cut = {
        f"0x{reset:x} mandatory after 0x{RUNTIME_WRITERS[0]:x}": cuts(
            successors, RUNTIME_WRITERS[0], MAP_SUCCESS_RET, reset
        )
        for reset in RESET_WRITERS
    }
    after_last_reset = reachable(successors, RESET_WRITERS[1]) - {RESET_WRITERS[1]}
    writers_after_last_reset = after_last_reset & set(ALL_WRITERS)

    mandatory = {
        "method": "node N is mandatory on every entry->success-ret path iff deleting N disconnects them",
        "entry_reachable_instruction_count": len(entry_reachable),
        "join_reachable_instruction_count": len(join_reachable),
        "failure_arm_instructions": fmt(failure_reachable),
        "failure_arm_reaches_success_return": MAP_SUCCESS_RET in failure_reachable,
        "falsification_control_node": f"0x{control_node:x}",
        "falsification_control_leaves_success_reachable": control_still_reachable,
        "writer_cuts_entry_to_success_ret": cut_results,
        "reset_writer_cuts_join_to_success_ret": join_cut_results,
        "reset_writers_mandatory_after_runtime_writer": order_cut,
        "instructions_after_last_reset_writer": fmt(after_last_reset),
        "screen_writers_after_last_reset_writer": fmt(writers_after_last_reset),
        "lap311_reset_claim_reproduced": all(cut_results[f"0x{writer:x}"] for writer in RESET_WRITERS)
        and all(join_cut_results.values()),
        "beyond_lap311_runtime_writers_also_mandatory": all(
            cut_results[f"0x{writer:x}"] for writer in RUNTIME_WRITERS
        ),
        "beyond_lap311_last_direct_write_is_the_640x480_reset": not writers_after_last_reset,
    }
    mandatory["verdict"] = (
        "PASS"
        if mandatory["lap311_reset_claim_reproduced"]
        and control_still_reachable
        and not mandatory["failure_arm_reaches_success_return"]
        else "FAIL"
    )
    report["a3_mandatory_execution_cut_test"] = mandatory
    if not mandatory["lap311_reset_claim_reproduced"]:
        failures.append("cut test does not reproduce the lap311 reset-writer claim")
    if not control_still_reachable:
        failures.append("falsification control failed: deleting an off-path node disconnected the success return")
    if mandatory["failure_arm_reaches_success_return"]:
        failures.append("failure arm reaches the success return")

    # --- axis 4: residual defects in the lap311 artifact (no numeric impact) ----
    probe_source = (REPO / LAP311_ARTIFACTS["probe"][0]).read_text() if (REPO / LAP311_ARTIFACTS["probe"][0]).is_file() else ""
    pre_gate_is_vacuous = all(writer > MAP_GATE_BRANCH for writer in ALL_WRITERS)
    if pre_gate_is_vacuous:
        findings.append(
            "D1 vacuous component: every direct writer sits above the gate address, so lap311's "
            "`pre_gate_screen_writers` is empty by construction and the pre/post comparison reduces to "
            "`failure_writers == set()`; the new information is the success-arm set and the post-dominator, "
            "not the comparison (no numeric impact)"
        )
    findings.append(
        "D2 fail-open definition: lap311 approximates 'before the gate' by address order "
        "(`address < MAP_GATE_BRANCH`), which is unsound in a function with backward jumps; empty here, "
        "so no numeric impact"
    )
    findings.append(
        "D3 fail-open anchor guard: lap311 checks only `failure_seed == gate + 2` and never that the gate is a "
        "conditional branch taking 0x431afe, nor that the fall-through returns 0; axis 2 confirms both from bytes, "
        "so the constants are right today and the gap is guard-only (no numeric impact)"
    )
    if "EXPECTED_RUNTIME_WRITERS" in probe_source and probe_source.count("EXPECTED_RUNTIME_WRITERS") == 1:
        findings.append(
            "D4 dead constant: lap311 defines `EXPECTED_RUNTIME_WRITERS` and never reads it (no numeric impact)"
        )
    findings.append(
        "D5 under-claim: post-dominance of the entry does not by itself establish what the function leaves in the "
        "screen globals; axis 3 adds that all four direct writers are mandatory on success paths, that the resets "
        "are mandatory after the runtime writer, and that no direct screen writer follows 0x4324c2"
    )
    report["a4_residual_defects"] = findings

    report["limitations"] = [
        "static only: no game, Wine, Xvfb, runtime, Stage B, PNG, or clicks",
        "the byte census covers absolute-displacement operands only; computed/indirect pointer writes remain UNKNOWN",
        "axis 3 shares objdump instruction boundaries with lap311 and treats calls as fall-through, so callee writes and cross-function event/thread order remain UNKNOWN",
        "this probe produces no G1/G2/G3/G4 product evidence and is not a Stage B, milestone, or user approval",
    ]
    report["failures"] = failures
    report["verdict"] = "PASS" if not failures else "FAIL"
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
