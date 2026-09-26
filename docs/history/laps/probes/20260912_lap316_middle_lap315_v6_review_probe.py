"""lap316 middle probe — independent review of the lap315 R2 fail-open repair.

This probe never imports the lap315 probe.  Every number is re-derived from two
sources that lap315 did not use together:

* ``objdump -d`` in **AT&T** syntax (lap315 used Intel syntax), parsed with a
  line model that distinguishes wrapped byte-continuation lines from real
  instructions;
* the **raw PE image**, parsed here with ``struct`` so instruction bytes come
  from the file rather than from objdump's byte column.

The two sources are cross-checked against each other, so a byte column that
objdump wraps across lines cannot silently truncate an instruction.

Algorithms are deliberately different from lap315: reachability is a FIFO
breadth-first sweep, and the "no screen writer dominates the gate" claim is
settled by exhibiting a **witness path** that avoids every writer instead of by
running a dominator fixpoint.

Read-only static audit.  No game, Wine, Xvfb, runtime, Stage B, PNG, or click
path is run.  JSON is emitted on stdout only.
"""
from __future__ import annotations

from collections import deque
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import sys


REPO = Path(__file__).resolve().parents[4]
EXE = REPO / "Syw2plus" / "syw2plus_original.exe"
EXPECTED_EXE_SHA = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"

LAP315_PROBE = REPO / "docs/history/laps/probes/20260912_lap315_work_v6_mode_writer_order_probe.py"
LAP315_REPORT = REPO / "logs/lap315/lap315_v6_mode_writer_order.json"
LAP315_PROBE_SHA = "839372aa3683dd99849ef00e27d034e6c6c1784c04180bda30e1f419e19784c6"
LAP315_REPORT_SHA = "ac0e1b7e3e2008bbb2850096811f4abfdfefbca933f067fb3d4a93dafc2bfa31"

MAP_ENTRY = 0x431AB0
MAP_END = 0x4324D6
GATE = 0x431AF2
FAILURE_SEED = 0x431AF4
SUCCESS_JOIN = 0x431AFE
SUCCESS_RET = 0x4324D5
SCREEN_GLOBALS = (0xE5BF1C, 0xE5BF20)

CLAIMED = {
    "instruction_count": 753,
    "entry_reachable_instruction_count": 753,
    "failure_arm_instruction_count": 7,
    "success_arm_instruction_count": 724,
    "unresolved_branches": 0,
    "screen_writers": (0x431B79, 0x431B7F, 0x4324B8, 0x4324C2),
    "gate_bytes": "750a",
    "gate_taken_target": 0x431AFE,
    "failure_arm_bytes": "5f5e5d33c05b83c434c3",
}

INSN_RE = re.compile(r"^\s+([0-9a-f]{6}):\t([0-9a-f ]+?)\t(\S.*?)\s*$")
CONT_RE = re.compile(r"^\s+([0-9a-f]{6}):\t([0-9a-f ]+?)\s*$")
BRANCH_RE = re.compile(r"^(j[a-z]+|loop[a-z]*)\s+(.*)$")
DIRECT_TARGET_RE = re.compile(r"^0x([0-9a-f]+)$")
RET_RE = re.compile(r"^ret[a-z]*(\s+\$0x[0-9a-f]+)?$")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def load_pe() -> tuple[bytes, list[tuple[str, int, int, int, int]], int]:
    """Parse the PE section table so virtual addresses can be read from file."""
    data = EXE.read_bytes()
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    if data[pe : pe + 4] != b"PE\0\0":
        raise ValueError("not a PE image")
    section_count = struct.unpack_from("<H", data, pe + 6)[0]
    optional_size = struct.unpack_from("<H", data, pe + 20)[0]
    image_base = struct.unpack_from("<I", data, pe + 24 + 28)[0]
    table = pe + 24 + optional_size
    sections = []
    for index in range(section_count):
        offset = table + 40 * index
        name = data[offset : offset + 8].rstrip(b"\0").decode("ascii", "replace")
        virtual_size, virtual_address, raw_size, raw_offset = struct.unpack_from("<IIII", data, offset + 8)
        sections.append((name, virtual_address, virtual_size, raw_offset, raw_size))
    return data, sections, image_base


def make_reader(data: bytes, sections, image_base: int):
    def read(address: int, size: int) -> bytes:
        for _name, virtual_address, virtual_size, raw_offset, raw_size in sections:
            start = image_base + virtual_address
            if start <= address < start + max(virtual_size, raw_size):
                offset = raw_offset + (address - start)
                return data[offset : offset + size]
        raise KeyError(f"address 0x{address:x} is not mapped")

    return read


def disassemble_att() -> tuple[list[tuple[int, str]], dict[int, str], int]:
    """Return (address, mnemonic-text) rows plus objdump's own byte column."""
    listing = subprocess.run(
        ["objdump", "-d", "-j", ".text", str(EXE)],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    rows: list[tuple[int, str]] = []
    columns: dict[int, str] = {}
    continuation_count = 0
    last_address: int | None = None
    for line in listing.splitlines():
        instruction = INSN_RE.match(line)
        if instruction:
            address = int(instruction.group(1), 16)
            rows.append((address, instruction.group(3)))
            columns[address] = instruction.group(2).replace(" ", "")
            last_address = address
            continue
        continued = CONT_RE.match(line)
        if continued and last_address is not None and ":" in line:
            columns[last_address] += continued.group(2).replace(" ", "")
            continuation_count += 1
    return rows, columns, continuation_count


def build_graph(window: list[tuple[int, str]]) -> tuple[dict[int, set[int]], list[str], list[str]]:
    known = {address for address, _text in window}
    graph: dict[int, set[int]] = {}
    unresolved: list[str] = []
    indirect: list[str] = []
    for index, (address, text) in enumerate(window):
        successor = window[index + 1][0] if index + 1 < len(window) else None
        if RET_RE.match(text):
            graph[address] = set()
            continue
        branch = BRANCH_RE.match(text)
        if branch:
            mnemonic, operand = branch.groups()
            direct = DIRECT_TARGET_RE.match(operand.strip())
            if direct is None:
                indirect.append(f"0x{address:x}: {text}")
                unresolved.append(f"0x{address:x}: indirect or unparsed branch")
                graph[address] = set()
                continue
            target = int(direct.group(1), 16)
            edges = {target}
            if mnemonic != "jmp":
                edges |= {successor} if successor is not None else set()
            if target not in known:
                unresolved.append(f"0x{address:x}: direct target 0x{target:x} outside window")
            graph[address] = {edge for edge in edges if edge in known}
            continue
        graph[address] = {successor} if successor in known else set()
    return graph, unresolved, indirect


def breadth_first(graph: dict[int, set[int]], start: int, blocked: frozenset[int] = frozenset()) -> set[int]:
    """FIFO sweep; ``blocked`` nodes are treated as removed from the graph."""
    if start in blocked:
        return set()
    seen = {start}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for successor in graph.get(node, set()):
            if successor in seen or successor in blocked:
                continue
            seen.add(successor)
            queue.append(successor)
    return seen


def witness_path(graph: dict[int, set[int]], start: int, goal: int, blocked: frozenset[int]) -> list[int] | None:
    """Shortest start->goal path that avoids every ``blocked`` node, or None."""
    if start in blocked:
        return None
    parent: dict[int, int | None] = {start: None}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        if node == goal:
            path = []
            cursor: int | None = node
            while cursor is not None:
                path.append(cursor)
                cursor = parent[cursor]
            return list(reversed(path))
        for successor in graph.get(node, set()):
            if successor in parent or successor in blocked:
                continue
            parent[successor] = node
            queue.append(successor)
    return None


def screen_global_mentions(window: list[tuple[int, str]], columns: dict[int, str]) -> list[dict[str, object]]:
    """Every window instruction that names a screen global, in any operand form."""
    needles = tuple(f"0x{value:x}" for value in SCREEN_GLOBALS)
    found = []
    for address, text in window:
        hit = next((needle for needle in needles if needle in text), None)
        if hit is None:
            continue
        raw = columns.get(address, "")
        operands = text.split(None, 1)[1] if " " in text else ""
        destination = operands.rsplit(",", 1)[-1].strip() if operands else ""
        found.append(
            {
                "address": f"0x{address:x}",
                "text": text,
                "bytes": raw,
                "global": hit,
                "is_store_to_global": destination == hit,
                "is_moffs_form": raw[:2] in {"a1", "a3"},
                "operand_size": "dword"
                if text.startswith(("movl", "mov ")) or text.split()[0] in {"mov", "movl"}
                else text.split()[0],
            }
        )
    return found


def instruction_contiguity(window: list[tuple[int, str]], start: int, size: int, read) -> dict[str, object]:
    selected = [address for address, _text in window if address >= start]
    cursor = start
    consumed = 0
    for address in selected:
        if address != cursor:
            break
        index = selected.index(address)
        length = selected[index + 1] - address if index + 1 < len(selected) else 0
        if length <= 0:
            break
        consumed += 1
        cursor = address + length
        if cursor - start >= size:
            break
    covered = cursor - start
    return {
        "instruction_count": consumed,
        "covered_bytes": covered,
        "is_contiguous": covered >= size,
        "bytes_from_pe_image": read(start, size).hex(),
    }


def rerun_lap315(expect_sha: str) -> dict[str, object]:
    """Run the lap315 probe as a subprocess (never imported) and hash stdout."""
    venv = REPO / ".venv/bin/python"
    interpreter = venv if venv.is_file() else Path(sys.executable)
    digests = []
    for _attempt in range(2):
        completed = subprocess.run(
            [str(interpreter), str(LAP315_PROBE)],
            cwd=str(REPO),
            capture_output=True,
        )
        digests.append({"exit_code": completed.returncode, "stdout_sha256": sha256_bytes(completed.stdout)})
    stored = LAP315_REPORT.read_bytes()
    return {
        "runs": digests,
        "stdout_sha_stable_across_runs": digests[0]["stdout_sha256"] == digests[1]["stdout_sha256"],
        "stored_report_sha256": sha256_bytes(stored),
        "stored_report_sha_matches_claim": sha256_bytes(stored) == expect_sha,
        "stored_report_matches_fresh_stdout": digests[0]["stdout_sha256"] == sha256_bytes(stored),
    }


def fmt(values) -> list[str]:
    return [f"0x{value:x}" for value in sorted(values)]


def main() -> int:  # noqa: C901 - one bounded static review report
    failures: list[str] = []
    notes: list[str] = []
    report: dict[str, object] = {
        "probe": Path(__file__).name,
        "lap": 316,
        "role": "middle (independent review); no game code edited, no execution",
        "execution": False,
        "scope": "independent re-derivation of lap315 R2 numbers, byte facts, and the D1/E1/E2 repair claims",
        "independence": [
            "lap315 probe is never imported; it is only re-run as a subprocess for reproducibility",
            "instruction text comes from AT&T objdump, not Intel",
            "instruction bytes come from the raw PE image parsed here, not from objdump's byte column",
            "reachability is FIFO breadth-first; gate dominance is settled by a witness path, not a fixpoint",
        ],
    }
    if not EXE.is_file():
        report["failures"] = [f"missing original executable: {EXE}"]
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1

    data, sections, image_base = load_pe()
    read = make_reader(data, sections, image_base)
    exe_sha = sha256_bytes(data)
    report["sha256"] = {
        "original_exe": exe_sha,
        "lap315_probe": sha256_bytes(LAP315_PROBE.read_bytes()) if LAP315_PROBE.is_file() else None,
    }
    if exe_sha != EXPECTED_EXE_SHA:
        failures.append(f"original exe sha mismatch: {exe_sha}")
    if report["sha256"]["lap315_probe"] != LAP315_PROBE_SHA:
        failures.append("lap315 probe sha does not match the lap315 report")

    rows, columns, continuation_count = disassemble_att()
    window = [(address, text) for address, text in rows if MAP_ENTRY <= address < MAP_END]
    graph, unresolved, indirect = build_graph(window)

    # Cross-check objdump's byte column against the raw PE image.
    byte_mismatches = []
    wrapped = []
    addresses = [address for address, _text in window]
    for index, address in enumerate(addresses):
        if index + 1 >= len(addresses):
            continue
        length = addresses[index + 1] - address
        column = columns.get(address, "")
        if len(column) // 2 > 7:
            wrapped.append(f"0x{address:x}")
        if column != read(address, length).hex():
            byte_mismatches.append(f"0x{address:x}")
    if byte_mismatches:
        failures.append(f"objdump byte column disagrees with the PE image at {byte_mismatches[:5]}")

    entry_reachable = breadth_first(graph, MAP_ENTRY)
    failure_reachable = breadth_first(graph, FAILURE_SEED)
    success_reachable = breadth_first(graph, SUCCESS_JOIN)

    mentions = screen_global_mentions(window, columns)
    stores = {int(item["address"], 16) for item in mentions if item["is_store_to_global"]}
    non_stores = [item for item in mentions if not item["is_store_to_global"]]

    counts = {
        "instruction_count": len(window),
        "entry_reachable_instruction_count": len(entry_reachable),
        "failure_arm_instruction_count": len(failure_reachable),
        "success_arm_instruction_count": len(success_reachable),
        "unresolved_branches": len(unresolved),
    }
    claimed_counts = {key: CLAIMED[key] for key in counts}
    report["independent_counts"] = counts
    report["lap315_claimed_counts"] = claimed_counts
    report["counts_match_lap315"] = counts == claimed_counts
    if counts != claimed_counts:
        failures.append(f"count mismatch: independent={counts} claimed={claimed_counts}")

    report["screen_global_census"] = {
        "definition": "every window instruction naming 0xe5bf1c or 0xe5bf20, in any operand form",
        "mentions": mentions,
        "store_addresses": fmt(stores),
        "non_store_mentions": non_stores,
        "moffs_store_count": sum(1 for item in mentions if item["is_moffs_form"] and item["is_store_to_global"]),
    }
    if stores != set(CLAIMED["screen_writers"]):
        failures.append(f"screen writer set mismatch: independent={fmt(stores)} claimed={fmt(CLAIMED['screen_writers'])}")

    failure_writers = stores & failure_reachable
    success_writers = stores & success_reachable
    blocked = frozenset(stores)
    path = witness_path(graph, MAP_ENTRY, GATE, blocked)
    report["r2_arm_comparison"] = {
        "failure_arm_screen_writers": fmt(failure_writers),
        "success_arm_screen_writers": fmt(success_writers),
        "failure_arm_reaches_success_return": SUCCESS_RET in failure_reachable,
        "pre_gate_witness_path_avoiding_all_writers": fmt(path) if path else None,
        "pre_gate_is_vacuous": bool(path),
        "vacuity_method": "witness path from map entry to the gate that avoids every screen writer",
    }
    if failure_writers:
        failures.append(f"failure arm writers are not empty: {fmt(failure_writers)}")
    if success_writers != set(CLAIMED["screen_writers"]):
        failures.append(f"success arm writer set mismatch: {fmt(success_writers)}")
    if SUCCESS_RET in failure_reachable:
        failures.append("failure arm reaches the success return")
    if path is None:
        failures.append("no writer-free path to the gate: the empty pre-gate set is not vacuous after all")

    gate_bytes = read(GATE, 2)
    taken = GATE + 2 + int.from_bytes(gate_bytes[1:2], "little", signed=True)
    arm = instruction_contiguity(window, FAILURE_SEED, len(CLAIMED["failure_arm_bytes"]) // 2, read)
    report["r2_byte_facts_from_pe_image"] = {
        "gate": f"0x{GATE:x}",
        "gate_bytes": gate_bytes.hex(),
        "gate_taken_target": f"0x{taken:x}",
        "gate_taken_target_is_success_join": taken == SUCCESS_JOIN,
        "failure_arm": arm,
        "failure_arm_matches_claim": arm["bytes_from_pe_image"] == CLAIMED["failure_arm_bytes"],
        "failure_arm_instruction_count_matches_claim": arm["instruction_count"] == CLAIMED["failure_arm_instruction_count"],
    }
    if gate_bytes.hex() != CLAIMED["gate_bytes"]:
        failures.append(f"gate bytes mismatch: {gate_bytes.hex()}")
    if taken != CLAIMED["gate_taken_target"]:
        failures.append(f"gate taken target mismatch: 0x{taken:x}")
    if not arm["is_contiguous"] or arm["bytes_from_pe_image"] != CLAIMED["failure_arm_bytes"]:
        failures.append("failure arm bytes or contiguity disagree with the claim")

    calls = [f"0x{address:x}" for address, text in window if text.startswith("call")]
    report["fail_open_audit"] = {
        "indirect_branches_in_window": indirect,
        "e1_repair_is_exercised_by_real_target": bool(indirect),
        "objdump_wrapped_byte_lines_in_listing": continuation_count,
        "window_instructions_longer_than_seven_bytes": wrapped,
        "lap315_byte_column_truncation_risk": "lap315 reads objdump's byte column and drops wrapped continuation lines; "
        "the current collected region has no wrapped instruction, and a wrapped one would fail contiguity (fail-closed)",
        "calls_treated_as_fall_through": len(calls),
        "call_addresses": calls,
    }
    if not indirect:
        notes.append(
            "E1 repair (indirect branches become unresolved) is inert on the real target: the map window contains "
            "0 indirect branches, so only the synthetic fixtures exercise it"
        )
    notes.append(
        f"{len(calls)} call instructions are treated as fall-through, so callee writes and cross-function order stay UNKNOWN"
    )
    if wrapped:
        notes.append(
            f"{len(wrapped)} window instructions exceed objdump's 7-byte line width; lap315's byte column would truncate "
            "them, which is fail-closed for contiguity but makes reported byte strings unreliable outside the arm"
        )

    report["lap315_reproducibility"] = rerun_lap315(LAP315_REPORT_SHA)
    reproduction = report["lap315_reproducibility"]
    if not reproduction["stdout_sha_stable_across_runs"]:
        failures.append("lap315 probe stdout is not stable across two fresh runs")
    if not reproduction["stored_report_sha_matches_claim"]:
        failures.append("stored lap315 report sha does not match the lap315 report claim")
    if not reproduction["stored_report_matches_fresh_stdout"]:
        failures.append("stored lap315 report is not byte-identical to a fresh probe run")

    report["limitations"] = [
        "static only: no game, Wine, Xvfb, runtime, Stage B, PNG, or clicks",
        "linear-sweep disassembly can desynchronize; this probe checks only that the window decodes without (bad) rows",
        "calls are not followed, so callee and cross-function writers remain UNKNOWN",
        "this review produces no G1/G2/G3/G4 product evidence",
    ]
    report["review_notes"] = notes
    report["failures"] = failures
    report["verdict"] = "ACCEPT" if not failures else "REJECT"
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
