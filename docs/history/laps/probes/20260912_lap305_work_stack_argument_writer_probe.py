"""lap305 work probe — close the ``push 0xE5BF18`` writer gap.

This is a read-only static probe of the SHA-pinned original executable.  It
does not run the game, Wine, Xvfb, the runtime harness, or Stage B.  The
previous lap's 20-writer result followed only ``mov ecx,0xE5BF18`` calls.  V1
checks every literal stack-argument site, resolves its first call target, and
audits the shared callee's argument slots and field writes.
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

GRAPHICS_OBJECT = 0xE5BF18
SCREEN_W_GLOBAL = 0xE5BF1C
SCREEN_H_GLOBAL = 0xE5BF20
STACK_ARGUMENT_CALLEE = 0x465250
MODE_TABLE = 0x4644A0

INSN_RE = re.compile(
    r"^\s+([0-9a-f]{6}):\t([0-9a-f ]+?)\s*\t(.+?)\s*$", re.MULTILINE
)
DIRECT_CALL_RE = re.compile(r"^call\s+0x([0-9a-f]+)$")
RET_RE = re.compile(r"^ret(?:\s+0x[0-9a-f]+)?$")
STACK_ACCESS_RE = re.compile(r"\[esp(?:\+0x([0-9a-f]+))?\]")
ESP_ADJUST_RE = re.compile(r"^(sub|add)\s+esp,0x([0-9a-f]+)$")
FIELD_WRITE_RE = re.compile(
    r"^(?:mov|add|sub|or|and|inc|dec|xor)\b.*?"
    r"\[(e[a-z][a-z])\+0x([48])\],"
)
ABSOLUTE_SCREEN_WRITE_RE = re.compile(
    r"^mov\s+(?:DWORD|WORD|BYTE) PTR ds:0x(?:e5bf1c|e5bf20),"
)


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


def first_call_after(
    instructions: list[tuple[int, str]], index: int
) -> tuple[int, int | None, list[str]]:
    """Return the first call after a push, stopping at an unsafe control edge."""
    push_address = instructions[index][0]
    between: list[str] = []
    for address, instruction in instructions[index + 1 : index + 16]:
        if RET_RE.match(instruction) or instruction.startswith(("j", "loop")):
            return push_address, None, between
        call = DIRECT_CALL_RE.match(instruction)
        if call:
            return push_address, int(call.group(1), 16), between
        between.append(f"0x{address:x}: {instruction}")
    return push_address, None, between


def callee_body(
    instructions: list[tuple[int, str]], entry: int
) -> list[tuple[int, str]]:
    start = next((index for index, (address, _instruction) in enumerate(instructions) if address == entry), None)
    if start is None:
        return []
    body: list[tuple[int, str]] = []
    for item in instructions[start:]:
        body.append(item)
        if RET_RE.match(item[1]):
            break
    return body


def entry_relative_stack_accesses(body: list[tuple[int, str]]) -> dict[str, str]:
    """Classify original arg1/arg2 slots after stack-frame adjustments.

    The callee subtracts 0x100 before using a local ``[esp+4]`` buffer.  A
    raw textual match would misclassify that local as the entry arg1, so this
    tracks the current stack delta and reports only entry-relative offsets 4
    and 8.
    """
    delta = 0
    accesses: dict[str, str] = {}
    for address, instruction in body:
        for match in STACK_ACCESS_RE.finditer(instruction):
            raw_offset = int(match.group(1), 16) if match.group(1) else 0
            entry_offset = raw_offset + delta
            if entry_offset in (4, 8):
                accesses[f"0x{address:x}"] = (
                    f"{instruction} (entry [esp+0x{entry_offset:x}], "
                    f"raw [esp+0x{raw_offset:x}], stack_delta=0x{delta:x})"
                )
        adjust = ESP_ADJUST_RE.match(instruction)
        if adjust:
            amount = int(adjust.group(2), 16)
            delta += amount if adjust.group(1) == "sub" else -amount
        elif instruction.startswith("push"):
            delta += 4
        elif instruction.startswith("pop"):
            delta -= 4
    return accesses


def main() -> int:
    failures: list[str] = []
    report: dict[str, object] = {
        "probe": Path(__file__).name,
        "lap": 305,
        "role": "work (static research/probe); no game code edited, no execution",
        "execution": False,
        "capture_comparison": False,
        "scope": "V1: every push 0xE5BF18 argument path",
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

    # V1-A: enumerate all literal object pushes and resolve the first call.
    push_rows: list[dict[str, object]] = []
    for index, (address, instruction) in enumerate(instructions):
        if instruction != f"push   0x{GRAPHICS_OBJECT:x}":
            continue
        push_address, target, between = first_call_after(instructions, index)
        push_rows.append(
            {
                "push": f"0x{push_address:x}",
                "first_call": f"0x{target:x}" if target is not None else None,
                "instructions_between": between,
            }
        )

    targets: dict[str, int] = {}
    unsafe_rows: list[str] = []
    for row in push_rows:
        target = row["first_call"]
        if target is None:
            unsafe_rows.append(str(row["push"]))
            continue
        targets[str(target)] = targets.get(str(target), 0) + 1
    report["V1_stack_argument_sites"] = {
        "literal": f"0x{GRAPHICS_OBJECT:x}",
        "site_count": len(push_rows),
        "expected_site_count": 291,
        "first_call_target_counts": targets,
        "unsafe_control_edge_sites": unsafe_rows,
        "all_sites_resolve_to_shared_callee": (
            len(push_rows) == 291
            and not unsafe_rows
            and targets == {f"0x{STACK_ARGUMENT_CALLEE:x}": 291}
        ),
        "sites": push_rows,
    }
    if len(push_rows) != 291:
        failures.append(f"expected 291 stack-argument sites, found {len(push_rows)}")
    if unsafe_rows:
        failures.append(f"stack-argument sites without a safe first call: {unsafe_rows}")
    if targets != {f"0x{STACK_ARGUMENT_CALLEE:x}": 291}:
        failures.append(f"unexpected stack-argument call targets: {targets}")

    # V1-B: audit the shared callee as the function receiving arg1=E5BF18.
    body = callee_body(instructions, STACK_ARGUMENT_CALLEE)
    stack_arg_accesses = entry_relative_stack_accesses(body)
    field_writes = {
        f"0x{address:x}": instruction
        for address, instruction in body
        if FIELD_WRITE_RE.match(instruction)
    }
    direct_callees = sorted(
        int(match.group(1), 16)
        for _address, instruction in body
        if (match := DIRECT_CALL_RE.match(instruction))
    )
    indirect_callees = {
        f"0x{address:x}": instruction
        for address, instruction in body
        if instruction.startswith("call   DWORD PTR")
    }
    object_literal_refs = {
        f"0x{address:x}": instruction
        for address, instruction in body
        if f"{GRAPHICS_OBJECT:x}" in instruction
    }
    ret_instruction = next(
        (instruction for _address, instruction in reversed(body) if RET_RE.match(instruction)),
        None,
    )
    report["V1_shared_callee_audit"] = {
        "entry": f"0x{STACK_ARGUMENT_CALLEE:x}",
        "body_end": f"0x{body[-1][0]:x}" if body else None,
        "entry_instruction": by_address.get(STACK_ARGUMENT_CALLEE, ""),
        "ret_instruction": ret_instruction,
        "entry_relative_arg_4_or_8_accesses": stack_arg_accesses,
        "arg_plus_4_or_8_field_writes": field_writes,
        "direct_callees": [f"0x{target:x}" for target in direct_callees],
        "indirect_callees": indirect_callees,
        "object_literal_references": object_literal_refs,
        "object_arg1_is_consumed_by_shared_callee": bool(stack_arg_accesses or object_literal_refs),
        "writer_found_in_shared_callee": bool(field_writes),
        "interpretation": (
            "all 291 sites pass the object as the first stack argument to 0x465250; "
            "the callee reads [esp+0xc] instead, has no entry-relative arg1/arg2 access, "
            "does not mention 0xE5BF18, and contains no [arg+4]/[arg+8] write"
        ),
    }
    if not body:
        failures.append("shared stack-argument callee body was not found")
    if stack_arg_accesses:
        failures.append(f"shared callee accesses entry arg1/arg2 stack slots: {stack_arg_accesses}")
    if field_writes:
        failures.append(f"shared callee writes +4/+8 fields: {field_writes}")
    if object_literal_refs:
        failures.append(f"shared callee unexpectedly references object literal: {object_literal_refs}")

    # V1-C: fresh lower-bound accounting for the already confirmed paths.
    absolute_writers = {
        f"0x{address:x}": instruction
        for address, instruction in instructions
        if ABSOLUTE_SCREEN_WRITE_RE.match(instruction)
    }
    mode_body = callee_body(instructions, MODE_TABLE)
    mode_field_writers = {
        f"0x{address:x}": instruction
        for address, instruction in mode_body
        if FIELD_WRITE_RE.match(instruction)
        and re.search(r"\[esi\+0x(?:4|8)\],", instruction)
    }
    lower_bound = len(absolute_writers) + len(mode_field_writers)
    report["confirmed_writer_accounting"] = {
        "absolute_screen_global_writers": absolute_writers,
        "mode_table_this_plus_4_or_8_writers": mode_field_writers,
        "absolute_count": len(absolute_writers),
        "indirect_mode_table_count": len(mode_field_writers),
        "confirmed_lower_bound": lower_bound,
        "stack_argument_new_writers": len(field_writes),
        "updated_lower_bound": lower_bound + len(field_writes),
        "verdict": "20 remains the confirmed lower bound; V1 adds no writer",
    }
    if len(absolute_writers) != 4:
        failures.append(f"expected 4 absolute screen writers, found {len(absolute_writers)}")
    if len(mode_field_writers) != 16:
        failures.append(f"expected 16 mode-table field writers, found {len(mode_field_writers)}")
    if lower_bound != 20:
        failures.append(f"confirmed writer lower bound changed unexpectedly: {lower_bound}")

    report["limitations"] = [
        "static only: no game, Wine, Xvfb, runtime, Stage B, PNG, or click execution",
        "V1 closes literal push-to-direct-callee paths only; computed pointers, virtual dispatch, "
        "and unrelated callers remain outside this probe",
        "the shared callee has unresolved indirect calls, but the pushed object is not read or "
        "forwarded by its visible body",
        "20 is a confirmed lower bound, not a product G1 pass",
    ]
    report["failures"] = failures
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
