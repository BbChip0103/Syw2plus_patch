"""lap306 work V2 — derive display-writer conditions and dialog ordering.

This is a read-only static probe of the SHA-pinned original executable.  It
does not run the game, Wine, Xvfb, the runtime harness, Stage B, or clicks.
It deliberately records the cross-function ordering as unresolved when the
direct call graph cannot prove it.
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
MAP_CALLSITE = 0x48F538
ALLOCATOR = 0x4DA96E
RUNTIME_WIDTH_WRITER = 0x431B79
RUNTIME_HEIGHT_WRITER = 0x431B7F
RESET_WIDTH_WRITER = 0x4324B8
RESET_HEIGHT_WRITER = 0x4324C2
MAP_SUCCESS_RET = 0x4324D5
MAP_FAILURE_RET = 0x431AFD
DIALOG_ENTRY = 0x4D60B0
DIALOG_CONFIG_X = 0x4D6312
DIALOG_CONFIG_Y = 0x4D631C
DIALOG_CALLS = (0x4D69E5, 0x4D6A05)
SCREEN_W_GLOBAL = 0xE5BF1C
SCREEN_H_GLOBAL = 0xE5BF20
STACK_CALLEE = 0x465250
STACK_JOIN = 0x465287

INSN_RE = re.compile(
    r"^\s+([0-9a-f]{6}):\t([0-9a-f ]+?)\s*\t(.+?)\s*$", re.MULTILINE
)
DIRECT_CALL_RE = re.compile(r"^call\s+0x([0-9a-f]+)$")
DIRECT_BRANCH_RE = re.compile(r"^(j(?:[a-z]+)|loop[a-z]*)\s+0x([0-9a-f]+)$")
RET_RE = re.compile(r"^ret(?:\s+0x[0-9a-f]+)?$")
STACK_ACCESS_RE = re.compile(r"\[esp(?:\+0x([0-9a-f]+))?\]")
ESP_ADJUST_RE = re.compile(r"^(sub|add)\s+esp,0x([0-9a-f]+)$")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def disassemble() -> str:
    return subprocess.run(
        ["objdump", "-d", "-Mintel", "-j", ".text", str(EXE)],
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def parse(text: str) -> list[tuple[int, str]]:
    return [(int(address, 16), instruction) for address, _bytes, instruction in INSN_RE.findall(text)]


def direct_calls(instructions: list[tuple[int, str]], target: int) -> list[int]:
    expected = f"0x{target:x}"
    return [address for address, instruction in instructions if instruction == f"call   {expected}"]


def successors(
    instructions: list[tuple[int, str]],
) -> tuple[dict[int, set[int]], list[str]]:
    by_address = {address: index for index, (address, _instruction) in enumerate(instructions)}
    graph: dict[int, set[int]] = {}
    unresolved: list[str] = []
    for index, (address, instruction) in enumerate(instructions):
        if RET_RE.match(instruction):
            graph[address] = set()
            continue
        fallthrough = instructions[index + 1][0] if index + 1 < len(instructions) else None
        match = DIRECT_BRANCH_RE.match(instruction)
        if match:
            mnemonic, target_text = match.groups()
            target = int(target_text, 16)
            edges = {target} if mnemonic == "jmp" else {target}
            if mnemonic != "jmp" and fallthrough is not None:
                edges.add(fallthrough)
            graph[address] = {edge for edge in edges if edge in by_address}
            continue
        if instruction.startswith("j") or instruction.startswith("loop"):
            unresolved.append(f"0x{address:x}: {instruction}")
        graph[address] = {fallthrough} if fallthrough in by_address else set()
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


def dominates(graph: dict[int, set[int]], start: int) -> dict[int, set[int]]:
    nodes = reachable(graph, start)
    predecessors = {node: set() for node in nodes}
    for source in nodes:
        for target in graph[source] & nodes:
            predecessors[target].add(source)
    dom = {node: set(nodes) for node in nodes}
    dom[start] = {start}
    changed = True
    while changed:
        changed = False
        for node in nodes - {start}:
            incoming = predecessors[node]
            new = {node} | set.intersection(*(dom[p] for p in incoming)) if incoming else {node}
            if new != dom[node]:
                dom[node] = new
                changed = True
    return dom


def stack_adjustment(instruction: str) -> int:
    match = ESP_ADJUST_RE.match(instruction)
    if match:
        amount = int(match.group(2), 16)
        return amount if match.group(1) == "sub" else -amount
    if instruction.startswith("push"):
        return 4
    if instruction.startswith("pop"):
        return -4
    return 0


def stack_depth_analysis(
    instructions: list[tuple[int, str]], start: int
) -> tuple[dict[int, set[int]], dict[int, dict[str, set[int]]], list[str]]:
    """Track entry-relative stack offsets with CFG joins, not linear text order."""
    graph, unresolved = successors(instructions)
    depths: dict[int, set[int]] = {start: {0}}
    pending = [start]
    accesses: dict[int, dict[str, set[int]]] = {}
    while pending:
        address = pending.pop()
        current = depths.get(address, set())
        instruction = dict(instructions)[address]
        for match in STACK_ACCESS_RE.finditer(instruction):
            raw = int(match.group(1), 16) if match.group(1) else 0
            accesses.setdefault(address, {}).setdefault("entry_offsets", set()).update(
                raw - depth for depth in current
            )
            accesses[address].setdefault("raw_offsets", set()).add(raw)
        outgoing_depths = {depth + stack_adjustment(instruction) for depth in current}
        for target in graph.get(address, set()):
            merged = depths.setdefault(target, set()) | outgoing_depths
            if merged != depths[target]:
                depths[target] = merged
                pending.append(target)
    return depths, accesses, unresolved


def fmt_addresses(values: set[int] | list[int] | tuple[int, ...]) -> list[str]:
    return [f"0x{value:x}" for value in sorted(values)]


def main() -> int:
    failures: list[str] = []
    report: dict[str, object] = {
        "probe": Path(__file__).name,
        "lap": 306,
        "role": "work (static research/probe); no game code edited, no execution",
        "execution": False,
        "capture_comparison": False,
        "scope": "V2: FUN_00431AB0 writer conditions and order against FUN_004D60B0",
    }
    if not EXE.is_file():
        report["failures"] = [f"missing original executable: {EXE}"]
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1

    exe_sha = sha256(EXE)
    report["sha256"] = {"original_exe": exe_sha}
    if exe_sha != EXPECTED_EXE_SHA:
        failures.append(f"original exe sha mismatch: {exe_sha}")

    instructions = parse(disassemble())
    by_address = dict(instructions)
    if not instructions:
        failures.append("objdump produced no .text instructions")

    map_instructions = [
        (address, instruction)
        for address, instruction in instructions
        if MAP_ENTRY <= address < MAP_END
    ]
    map_graph, map_unresolved = successors(map_instructions)
    map_reachable = reachable(map_graph, MAP_ENTRY)
    map_success_reachable = reachable(map_graph, 0x431AFE)
    map_success_dom = dominates(map_graph, 0x431AFE)
    map_returns = [address for address, instruction in map_instructions if RET_RE.match(instruction)]
    runtime_writers = {
        f"0x{RUNTIME_WIDTH_WRITER:x}": by_address.get(RUNTIME_WIDTH_WRITER, ""),
        f"0x{RUNTIME_HEIGHT_WRITER:x}": by_address.get(RUNTIME_HEIGHT_WRITER, ""),
    }
    reset_writers = {
        f"0x{RESET_WIDTH_WRITER:x}": by_address.get(RESET_WIDTH_WRITER, ""),
        f"0x{RESET_HEIGHT_WRITER:x}": by_address.get(RESET_HEIGHT_WRITER, ""),
    }
    expected_map_anchors = {
        0x431AE1: "call   0x4da96e",
        0x431AEB: "cmp    eax,ebx",
        0x431AF2: "jne    0x431afe",
        0x431AFD: "ret",
        0x431B79: "mov    DWORD PTR ds:0xe5bf1c,ebp",
        0x431B7F: "mov    DWORD PTR ds:0xe5bf20,edi",
        0x4324B8: "mov    DWORD PTR ds:0xe5bf1c,0x280",
        0x4324C2: "mov    DWORD PTR ds:0xe5bf20,0x1e0",
        0x4324CC: "mov    eax,0x1",
        0x4324D5: "ret",
    }
    anchor_matches = {
        f"0x{address:x}": by_address.get(address, "") == expected
        for address, expected in expected_map_anchors.items()
    }
    failures.extend(
        f"map anchor 0x{address:x}: expected {expected!r}, found {by_address.get(address)!r}"
        for address, expected in expected_map_anchors.items()
        if by_address.get(address) != expected
    )
    success_reset_dominates = all(
        writer in map_success_dom.get(MAP_SUCCESS_RET, set())
        for writer in (RESET_WIDTH_WRITER, RESET_HEIGHT_WRITER)
    )
    runtime_on_success = {address in map_success_reachable for address in (RUNTIME_WIDTH_WRITER, RUNTIME_HEIGHT_WRITER)}
    runtime_on_failure = any(
        writer in reachable(map_graph, MAP_FAILURE_RET)
        for writer in (RUNTIME_WIDTH_WRITER, RUNTIME_HEIGHT_WRITER)
    )
    report["map_function"] = {
        "entry": f"0x{MAP_ENTRY:x}",
        "range": f"0x{MAP_ENTRY:x}..0x{MAP_END - 1:x}",
        "direct_calls_to_entry": fmt_addresses(direct_calls(instructions, MAP_ENTRY)),
        "returns": fmt_addresses(map_returns),
        "cfg_unresolved_branches": map_unresolved,
        "cfg_reachable_instruction_count": len(map_reachable),
        "anchors_match": anchor_matches,
        "allocation_gate": {
            "allocator": f"0x{ALLOCATOR:x}",
            "failure_result": "eax == 0",
            "failure_branch": "0x431AF2 -> 0x431AFE is taken only when eax != 0; fall-through reaches 0x431AFD",
            "failure_return": f"0x{MAP_FAILURE_RET:x} returns 0",
        },
        "runtime_writer": {
            "writes": runtime_writers,
            "formula_width": "sign_extend(WORD [this+0x8c]) << 6",
            "formula_height": "(sign_extend(WORD [this+0x8e]) << 5) + 0xc8",
            "reachable_from_success_join": {
                f"0x{RUNTIME_WIDTH_WRITER:x}": RUNTIME_WIDTH_WRITER in map_success_reachable,
                f"0x{RUNTIME_HEIGHT_WRITER:x}": RUNTIME_HEIGHT_WRITER in map_success_reachable,
            },
            "absent_on_failure_path": not runtime_on_failure,
            "condition": "allocator 0x4DA96E returns nonzero; values are runtime map dimensions, not a fixed mode",
        },
        "success_reset": {
            "writes": reset_writers,
            "values": {"width": 640, "height": 480},
            "success_return": f"0x{MAP_SUCCESS_RET:x} returns 1",
            "both_writers_dominate_success_return": success_reset_dominates,
            "condition": "the nonzero-allocation path reaches the normal success return",
        },
    }
    if map_unresolved:
        failures.append(f"map CFG contains unresolved branch forms: {map_unresolved}")
    if map_returns != [MAP_FAILURE_RET, MAP_SUCCESS_RET]:
        failures.append(f"unexpected map return sites: {fmt_addresses(map_returns)}")
    if not all(runtime_on_success) or runtime_on_failure:
        failures.append("runtime writer reachability did not match the allocation-success gate")
    if not success_reset_dominates:
        failures.append("640x480 reset does not dominate the success return")

    # Dialog configuration reads the globals only inside FUN_004D60B0.
    dialog_anchors = {
        DIALOG_CONFIG_X: f"mov    eax,ds:0x{SCREEN_W_GLOBAL:x}",
        DIALOG_CONFIG_Y: f"mov    eax,ds:0x{SCREEN_H_GLOBAL:x}",
        0x4D632A: "mov    WORD PTR ds:0x1088b5c,cx",
        0x4D6348: "mov    WORD PTR ds:0x1088b5e,di",
    }
    dialog_anchor_matches = {
        f"0x{address:x}": by_address.get(address, "") == expected
        for address, expected in dialog_anchors.items()
    }
    failures.extend(
        f"dialog anchor 0x{address:x}: expected {expected!r}, found {by_address.get(address)!r}"
        for address, expected in dialog_anchors.items()
        if by_address.get(address) != expected
    )
    dialog_instructions = [
        (address, instruction)
        for address, instruction in instructions
        if DIALOG_ENTRY <= address < 0x4D6570
    ]
    dialog_graph, dialog_unresolved = successors(dialog_instructions)
    report["dialog_configuration"] = {
        "entry": f"0x{DIALOG_ENTRY:x}",
        "direct_calls_to_entry": fmt_addresses(direct_calls(instructions, DIALOG_ENTRY)),
        "global_reads_and_origin_stores": dialog_anchor_matches,
        "config_order": [
            f"0x{DIALOG_CONFIG_X:x} read screen width",
            f"0x{DIALOG_CONFIG_Y:x} read screen height",
            "0x4D632A/0x4D6348 store derived dialog origins",
        ],
        "unresolved_branches_in_inspected_range": dialog_unresolved,
        "callers": {
            f"0x{address:x}": "call FUN_004D60B0; caller then conditionally calls FUN_004D6930"
            for address in DIALOG_CALLS
        },
    }
    if sorted(direct_calls(instructions, DIALOG_ENTRY)) != sorted(DIALOG_CALLS):
        failures.append("dialog entry direct callsite set changed")
    if dialog_unresolved:
        failures.append(f"dialog CFG contains unresolved branch forms: {dialog_unresolved}")

    # Explicit R3 regression: the actual shared callee has a branch join with
    # two incoming stack depths.  Entry-relative offsets are raw - depth.
    callee_instructions = [
        (address, instruction)
        for address, instruction in instructions
        if STACK_CALLEE <= address < 0x4652AF
    ]
    depths, accesses, stack_unresolved = stack_depth_analysis(callee_instructions, STACK_CALLEE)
    callsite_accesses = {
        f"0x{address:x}": {
            "raw_offsets": sorted(values.get("raw_offsets", set())),
            "entry_relative_offsets": sorted(values.get("entry_offsets", set())),
        }
        for address, values in accesses.items()
        if address in (0x46526D, STACK_JOIN)
    }
    report["r3_stack_normalization_regression"] = {
        "callee": f"0x{STACK_CALLEE:x}",
        "rule": "entry_relative_offset = raw_offset - current_stack_depth",
        "branch_join": f"0x{STACK_JOIN:x}",
        "depths_at_branch_join": sorted(depths.get(STACK_JOIN, set())),
        "selected_accesses": callsite_accesses,
        "expected": {
            "0x46526d entry arg1": 4,
            "0x465287 joined entry offsets": [4, 8],
        },
        "unresolved_branches": stack_unresolved,
        "pass": (
            accesses.get(0x46526D, {}).get("entry_offsets") == {4}
            and accesses.get(STACK_JOIN, {}).get("entry_offsets") == {4, 8}
            and depths.get(STACK_JOIN) == {0x100, 0x104}
        ),
    }
    if stack_unresolved:
        failures.append(f"stack callee contains unresolved branch forms: {stack_unresolved}")
    if not report["r3_stack_normalization_regression"]["pass"]:
        failures.append("R3 stack normalization regression failed")

    report["ordering_conclusion"] = {
        "static_fact": (
            "FUN_00431AB0 writes runtime values before its success path, then unconditionally restores "
            "640x480 at 0x4324B8/0x4324C2 before ret=1"
        ),
        "dialog_fact": "FUN_004D60B0 reads the globals at 0x4D6312/0x4D631C while constructing the dialog",
        "cross_function_order": "UNKNOWN: no direct edge orders the 0x431AB0 caller and the 0x4D60B0 callers",
        "conditional_inference": (
            "under ordinary single-threaded sequential execution, a dialog configuration call after a "
            "successful FUN_00431AB0 return observes 640x480 from this function unless another writer intervenes; "
            "the actual runtime click-time mode remains unobserved"
        ),
        "product_verdict": "not a G1 product pass; static mode source only",
    }
    report["limitations"] = [
        "static only: no game, Wine, Xvfb, runtime, Stage B, PNG, or clicks",
        "the direct call graph cannot establish event/thread order between map creation and dialog construction",
        "indirect/virtual writers outside the inspected direct stores remain outside this V2 probe",
        "the 640x480 reset is proven for the normal success return, not for unknown asynchronous execution",
    ]
    report["failures"] = failures
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
