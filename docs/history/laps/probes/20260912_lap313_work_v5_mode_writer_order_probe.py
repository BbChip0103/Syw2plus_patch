"""lap313 work — repair the D1-D4 gaps in the lap311 R2 probe.

This remains a read-only probe of the SHA-pinned original executable.  The
failure-arm comparison now defines "pre-gate" by CFG dominance rather than
numeric address order, and the gate anchor is checked from instruction bytes:
the conditional branch must take the success join and its fall-through arm
must return zero.  The dead runtime-writer expectation from lap311 is removed;
the shared writer set is the single source of truth.

No game, Wine, Xvfb, runtime, Stage B, PNG, or click path is run here.  JSON is
emitted on stdout only; the caller redirects stdout without hand transcription.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess


REPO = Path(__file__).resolve().parents[4]
EXE = REPO / "Syw2plus" / "syw2plus_original.exe"
EXPECTED_EXE_SHA = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"

MAP_ENTRY = 0x431AB0
MAP_END = 0x4324D6
MAP_GATE_BRANCH = 0x431AF2
MAP_FAILURE_SEED = 0x431AF4
MAP_FAILURE_RET = 0x431AFD
MAP_SUCCESS_JOIN = 0x431AFE
MAP_SUCCESS_RET = 0x4324D5
SCREEN_GLOBALS = (0xE5BF1C, 0xE5BF20)
RUNTIME_WRITERS = (0x431B79, 0x431B7F)
RESET_WRITERS = (0x4324B8, 0x4324C2)
EXPECTED_SCREEN_WRITERS = set(RUNTIME_WRITERS + RESET_WRITERS)

GATE_BYTES = bytes.fromhex("750a")  # jne short +0xa
FAILURE_ARM_BYTES = bytes.fromhex("5f5e5d33c05b83c434c3")

INSN_RE = re.compile(r"^\s+([0-9a-f]{6}):\t([0-9a-f ]+?)\s*\t(.+?)\s*$", re.MULTILINE)
BRANCH_RE = re.compile(r"^(j[a-z]+|loop[a-z]*)\s+0x([0-9a-f]+)$")
RET_RE = re.compile(r"^ret(?:\s+0x[0-9a-f]+)?$")
SCREEN_WRITER_RE = re.compile(r"^mov\s+DWORD PTR ds:0x(e5bf1c|e5bf20),")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_listing() -> list[tuple[int, bytes, str]]:
    listing = subprocess.run(
        ["objdump", "-d", "-Mintel", "-j", ".text", str(EXE)],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return [(int(address, 16), bytes.fromhex(raw), instruction) for address, raw, instruction in INSN_RE.findall(listing)]


def parse_text() -> list[tuple[int, str]]:
    return [(address, instruction) for address, _raw, instruction in parse_listing()]


def build_cfg(window: list[tuple[int, str]]) -> tuple[dict[int, set[int]], list[str]]:
    known = {address for address, _instruction in window}
    graph: dict[int, set[int]] = {}
    unresolved: list[str] = []
    for index, (address, instruction) in enumerate(window):
        if RET_RE.match(instruction):
            graph[address] = set()
            continue
        fallthrough = window[index + 1][0] if index + 1 < len(window) else None
        match = BRANCH_RE.match(instruction)
        if match:
            mnemonic, target_text = match.groups()
            target = int(target_text, 16)
            edges = {target}
            if mnemonic != "jmp" and fallthrough is not None:
                edges.add(fallthrough)
            if target not in known:
                unresolved.append(f"0x{address:x}: target 0x{target:x} outside window")
            graph[address] = {edge for edge in edges if edge in known}
            continue
        graph[address] = {fallthrough} if fallthrough in known else set()
    return graph, unresolved


def reachable(graph: dict[int, set[int]], start: int) -> set[int]:
    seen: set[int] = set()
    pending = [start]
    while pending:
        address = pending.pop()
        if address in seen or address not in graph:
            continue
        seen.add(address)
        pending.extend(graph[address] - seen)
    return seen


def dominators(graph: dict[int, set[int]], start: int) -> dict[int, set[int]]:
    """Return CFG dominators for nodes reachable from ``start``."""
    nodes = reachable(graph, start)
    predecessors = {node: set() for node in nodes}
    for source in nodes:
        for target in graph[source] & nodes:
            predecessors[target].add(source)
    result = {node: set(nodes) for node in nodes}
    result[start] = {start}
    changed = True
    while changed:
        changed = False
        for node in sorted(nodes - {start}):
            incoming = predecessors[node]
            candidate = {node} if not incoming else {node} | set.intersection(*(result[p] for p in incoming))
            if candidate != result[node]:
                result[node] = candidate
                changed = True
    return result


def pre_gate_screen_writers(
    graph: dict[int, set[int]], entry: int, gate: int, writers: set[int]
) -> set[int]:
    """Select writers that CFG-dominate the gate on entry-reachable paths.

    Dominance is the control-flow meaning of "already written before reaching
    the gate".  It is deliberately independent of numeric address ordering,
    which is not sound when a function contains backward jumps.
    """
    return writers & dominators(graph, entry).get(gate, set())


def screen_writers(window: list[tuple[int, str]]) -> set[int]:
    return {address for address, instruction in window if SCREEN_WRITER_RE.match(instruction)}


def gate_byte_facts(rows: list[tuple[int, bytes, str]]) -> dict[str, object]:
    """Check the branch target and zero-return bytes at the pinned gate."""
    by_address = {address: raw for address, raw, _instruction in rows}
    gate_bytes = by_address.get(MAP_GATE_BRANCH, b"")
    taken_target = None
    if len(gate_bytes) >= 2 and gate_bytes[0] == 0x75:
        taken_target = MAP_GATE_BRANCH + 2 + int.from_bytes(gate_bytes[1:2], "little", signed=True)

    failure_bytes = b""
    for address, raw, _instruction in rows:
        if address < MAP_FAILURE_SEED:
            continue
        failure_bytes += raw
        if len(failure_bytes) >= len(FAILURE_ARM_BYTES):
            break

    return {
        "gate": f"0x{MAP_GATE_BRANCH:x}",
        "gate_bytes": gate_bytes.hex(),
        "gate_is_conditional_branch": gate_bytes[:2] == GATE_BYTES,
        "gate_taken_target": f"0x{taken_target:x}" if taken_target is not None else None,
        "gate_taken_target_is_success_join": taken_target == MAP_SUCCESS_JOIN,
        "fall_through": f"0x{MAP_FAILURE_SEED:x}",
        "failure_arm_bytes": failure_bytes[: len(FAILURE_ARM_BYTES)].hex(),
        "failure_arm_returns_zero": failure_bytes[: len(FAILURE_ARM_BYTES)] == FAILURE_ARM_BYTES,
    }


def fmt(values: set[int] | list[int] | tuple[int, ...]) -> list[str]:
    return [f"0x{value:x}" for value in sorted(values)]


def main() -> int:  # noqa: C901 - one bounded static audit report
    failures: list[str] = []
    report: dict[str, object] = {
        "probe": Path(__file__).name,
        "lap": 313,
        "role": "work (static research/probe); no game code edited, no execution",
        "execution": False,
        "scope": "R2 D1-D4 repair: CFG gate dominance and byte-pinned gate facts",
        "report_contract": "JSON is emitted on stdout; redirect stdout without hand transcription",
    }
    if not EXE.is_file():
        report["failures"] = [f"missing original executable: {EXE}"]
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1

    exe_sha = sha256_file(EXE)
    report["sha256"] = {"original_exe": exe_sha}
    if exe_sha != EXPECTED_EXE_SHA:
        failures.append(f"original exe sha mismatch: {exe_sha}")

    rows = parse_listing()
    instructions = [(address, instruction) for address, _raw, instruction in rows]
    map_window = [(address, instruction) for address, instruction in instructions if MAP_ENTRY <= address < MAP_END]
    map_rows = [(address, raw, instruction) for address, raw, instruction in rows if MAP_ENTRY <= address < MAP_END]
    graph, unresolved = build_cfg(map_window)
    if not map_window:
        failures.append("objdump produced no instructions in map window")

    all_writers = screen_writers(map_window)
    from_entry = reachable(graph, MAP_ENTRY)
    gate_dominators = dominators(graph, MAP_ENTRY).get(MAP_GATE_BRANCH, set())
    before_gate = pre_gate_screen_writers(graph, MAP_ENTRY, MAP_GATE_BRANCH, all_writers)
    failure_path = reachable(graph, MAP_FAILURE_SEED)
    success_path = reachable(graph, MAP_SUCCESS_JOIN)
    failure_writers = all_writers & failure_path
    success_writers = all_writers & success_path
    failure_preserves_screen_writer_set = failure_writers == before_gate
    r2 = {
        "gate": f"0x{MAP_GATE_BRANCH:x}",
        "failure_seed": f"0x{MAP_FAILURE_SEED:x}",
        "pre_gate_definition": "direct writers that CFG-dominate the gate from map entry",
        "gate_dominators": fmt(gate_dominators),
        "pre_gate_screen_writers": fmt(before_gate),
        "failure_arm_screen_writers": fmt(failure_writers),
        "success_arm_screen_writers": fmt(success_writers),
        "all_screen_writers_in_map_window": fmt(all_writers),
        "failure_preserves_pre_gate_screen_writer_set": failure_preserves_screen_writer_set,
        "failure_has_no_new_screen_global_writer": not (failure_writers - before_gate),
        "expected": {
            "all_screen_writers": fmt(EXPECTED_SCREEN_WRITERS),
            "failure_arm": [],
            "success_arm": fmt(EXPECTED_SCREEN_WRITERS),
        },
        "verdict": "PASS"
        if all_writers == EXPECTED_SCREEN_WRITERS
        and failure_preserves_screen_writer_set
        and success_writers == EXPECTED_SCREEN_WRITERS
        else "FAIL",
    }
    report["r2_failure_arm_writer_set_comparison"] = r2
    if all_writers != EXPECTED_SCREEN_WRITERS:
        failures.append(f"screen writer set changed: {fmt(all_writers)}")
    if not failure_preserves_screen_writer_set:
        failures.append(f"failure arm adds screen writers: {fmt(failure_writers - before_gate)}")
    if success_writers != EXPECTED_SCREEN_WRITERS:
        failures.append(f"success arm screen writer set changed: {fmt(success_writers)}")
    if MAP_SUCCESS_RET in failure_path:
        failures.append("failure arm reaches the success return")
    if MAP_GATE_BRANCH not in from_entry:
        failures.append("map entry cannot reach the gate")

    gate = gate_byte_facts(map_rows)
    gate["verdict"] = (
        "PASS"
        if gate["gate_is_conditional_branch"]
        and gate["gate_taken_target_is_success_join"]
        and gate["failure_arm_returns_zero"]
        else "FAIL"
    )
    report["r2_gate_byte_facts"] = gate
    for key in ("gate_is_conditional_branch", "gate_taken_target_is_success_join", "failure_arm_returns_zero"):
        if not gate[key]:
            failures.append(f"gate byte fact failed: {key}")

    report["map_cfg"] = {
        "instruction_count": len(map_window),
        "unresolved_branches": unresolved,
        "entry_reachable_instruction_count": len(from_entry),
        "failure_arm_instruction_count": len(failure_path),
        "success_arm_instruction_count": len(success_path),
        "success_return": f"0x{MAP_SUCCESS_RET:x}",
    }
    if unresolved:
        failures.append(f"map CFG has branch targets outside the inspected window: {unresolved}")

    report["limitations"] = [
        "static only: no game, Wine, Xvfb, runtime, Stage B, PNG, or clicks",
        "screen writer comparison covers direct instructions in this map function; indirect/computed writers remain UNKNOWN",
        "the CFG treats calls as fall-through and does not prove cross-function event/thread order",
        "this probe produces no G1/G2/G3/G4 product evidence",
    ]
    report["failures"] = failures
    report["verdict"] = "PASS" if not failures else "FAIL"
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
