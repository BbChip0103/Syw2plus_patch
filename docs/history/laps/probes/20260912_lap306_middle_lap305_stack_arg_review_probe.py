"""lap306 middle probe — independent review of lap305's V1 stack-argument result.

Read-only static review of the SHA-pinned original executable.  No game, Wine,
Xvfb, runtime harness, Stage B, PNG, or click execution.  lap305 claimed that
the shared callee of all 291 ``push 0xE5BF18`` sites never touches the entry
arg1/arg2 slots.  This probe re-derives the same facts from a fresh objdump and
re-checks the stack-delta normalisation that produced that claim.
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

LAP305_PROBE = (
    REPO
    / "docs/history/laps/probes/20260912_lap305_work_stack_argument_writer_probe.py"
)
EXPECTED_LAP305_PROBE_SHA = (
    "c151cc40f3220df97d687d4db86945ed7196bf4ab72bec74e95401c943e57b21"
)

GRAPHICS_OBJECT = 0xE5BF18
SCREEN_W_GLOBAL = 0xE5BF1C
SCREEN_H_GLOBAL = 0xE5BF20
SHARED_CALLEE = 0x465250
MODE_TABLE_FUNC = 0x4644A0
MODE_JUMP_TABLE = 0x464B68
MODE_GLOBAL = 0x4ED810

INSN_RE = re.compile(r"^\s+([0-9a-f]{6}):\t([0-9a-f ]+?)\s*\t(.+?)\s*$", re.MULTILINE)
DIRECT_CALL_RE = re.compile(r"^call\s+0x([0-9a-f]+)$")
RET_RE = re.compile(r"^ret(?:\s+0x[0-9a-f]+)?$")
STACK_ACCESS_RE = re.compile(r"\[esp(?:\+0x([0-9a-f]+))?\]")
ESP_ADJUST_RE = re.compile(r"^(sub|add)\s+esp,0x([0-9a-f]+)$")
FIELD_WRITE_RE = re.compile(r"^(?:mov|add|sub|or|and|inc|dec|xor)\b.*?\[(e[a-z][a-z])\+0x([48])\],")
# Both encodings of an absolute store: modrm form (`mov DWORD PTR ds:0xX,r`)
# and the short moffs form (`mov ds:0xX,eax`, opcode a2/a3) that the lap303 and
# lap305 regexes could not see.
ABSOLUTE_WRITE_RE = re.compile(
    r"^mov\s+(?:(?:DWORD|WORD|BYTE) PTR )?ds:0x([0-9a-f]+),"
)
MOFFS_STORE_RE = re.compile(r"^(a2|a3) ")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def disassemble() -> str:
    return subprocess.run(
        ["objdump", "-d", "-Mintel", "-j", ".text", str(EXE)],
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def parse(text: str) -> list[tuple[int, str, str]]:
    return [
        (int(address, 16), raw.strip(), instruction)
        for address, raw, instruction in INSN_RE.findall(text)
    ]


def read_va(data: bytes, vaddr: int, size: int) -> bytes | None:
    """Map a virtual address back to file bytes using the PE section table."""
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    section_count = struct.unpack_from("<H", data, pe + 6)[0]
    optional_size = struct.unpack_from("<H", data, pe + 20)[0]
    image_base = struct.unpack_from("<I", data, pe + 24 + 28)[0]
    for index in range(section_count):
        offset = pe + 24 + optional_size + index * 40
        virtual_size, virtual_address, _raw_size, raw_offset = struct.unpack_from(
            "<IIII", data, offset + 8
        )
        start = image_base + virtual_address
        if start <= vaddr < start + virtual_size:
            file_offset = raw_offset + (vaddr - start)
            return data[file_offset : file_offset + size]
    return None


def cstring(data: bytes, vaddr: int) -> str | None:
    raw = read_va(data, vaddr, 64)
    if raw is None:
        return None
    end = raw.find(b"\0")
    return raw[: end if end >= 0 else len(raw)].decode("latin-1")


def first_call_after(
    instructions: list[tuple[int, str, str]], index: int
) -> tuple[int, int | None, bool]:
    """Resolve the first call after a push and whether the push is still arg1.

    Three of the 291 sites separate the push from the call with scalar or
    absolute-store instructions.  Those do not move esp, so the object stays in
    the last-pushed slot; only an esp change between the two would demote it.
    """
    esp_moved = False
    for _address, _raw, instruction in instructions[index + 1 : index + 16]:
        if RET_RE.match(instruction) or instruction.startswith(("j", "loop")):
            return instructions[index][0], None, esp_moved
        call = DIRECT_CALL_RE.match(instruction)
        if call:
            return instructions[index][0], int(call.group(1), 16), esp_moved
        if (
            instruction.startswith(("push", "pop"))
            or ESP_ADJUST_RE.match(instruction)
            or re.match(r"^(mov|lea|xchg)\s+esp,", instruction)
        ):
            esp_moved = True
    return instructions[index][0], None, esp_moved


def callee_body(
    instructions: list[tuple[int, str, str]], entry: int
) -> list[tuple[int, str, str]]:
    start = next(
        (index for index, item in enumerate(instructions) if item[0] == entry), None
    )
    if start is None:
        return []
    body: list[tuple[int, str, str]] = []
    for item in instructions[start:]:
        body.append(item)
        if RET_RE.match(item[2]):
            break
    return body


BRANCH_RE = re.compile(r"^j[a-z]+\s+0x([0-9a-f]+)$")


def step_depth(depth: int, instruction: str) -> int:
    adjust = ESP_ADJUST_RE.match(instruction)
    if adjust:
        amount = int(adjust.group(2), 16)
        return depth + (amount if adjust.group(1) == "sub" else -amount)
    if instruction.startswith("push"):
        return depth + 4
    if instruction.startswith("pop"):
        return depth - 4
    return depth


def branch_depths(body: list[tuple[int, str, str]]) -> dict[int, int]:
    """Record the esp depth each intra-body branch carries to its target.

    Needed because an indirect ``call DWORD PTR [reg+X]`` hides its own
    argument cleanup: the linear depth after such a call is unknown, but a
    branch target's depth is fixed by its predecessor branch.
    """
    depth = 0
    seen: dict[int, int] = {}
    for _address, _raw, instruction in body:
        match = BRANCH_RE.match(instruction)
        if match:
            seen.setdefault(int(match.group(1), 16), depth)
        depth = step_depth(depth, instruction)
    return seen


def entry_relative_accesses(
    body: list[tuple[int, str, str]], sign: int
) -> dict[str, str]:
    """Classify ``[esp+X]`` accesses as entry arg1/arg2.

    ``depth`` is how far esp sits *below* its entry value, so an entry-relative
    offset is ``raw - depth``.  ``sign=+1`` reproduces lap305's ``raw + depth``
    normalisation so the two can be compared on one body.
    """
    joins = branch_depths(body)
    depth = 0
    accesses: dict[str, str] = {}
    for address, _raw, instruction in body:
        if address in joins:
            depth = joins[address]
        for match in STACK_ACCESS_RE.finditer(instruction):
            raw_offset = int(match.group(1), 16) if match.group(1) else 0
            entry_offset = raw_offset + sign * depth
            if entry_offset in (4, 8):
                accesses[f"0x{address:x}"] = (
                    f"{instruction} (entry [esp+0x{entry_offset:x}], "
                    f"raw [esp+0x{raw_offset:x}], depth=0x{depth:x})"
                )
        depth = step_depth(depth, instruction)
    return accesses


def main() -> int:
    failures: list[str] = []
    report: dict[str, object] = {
        "probe": Path(__file__).name,
        "lap": 306,
        "role": "middle (independent review of lap305 work); no game code edited, no execution",
        "execution": False,
        "capture_comparison": False,
        "scope": "R1..R5: re-derive lap305 V1 and audit its stack-delta normalisation",
    }
    if not EXE.is_file():
        report["failures"] = [f"missing original executable: {EXE}"]
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1

    exe_bytes = EXE.read_bytes()
    exe_sha = sha256_bytes(exe_bytes)
    lap305_sha = sha256_bytes(LAP305_PROBE.read_bytes()) if LAP305_PROBE.is_file() else None
    report["sha256"] = {"original_exe": exe_sha, "lap305_probe": lap305_sha}
    if exe_sha != EXPECTED_EXE_SHA:
        failures.append(f"original exe sha mismatch: {exe_sha}")
    if lap305_sha != EXPECTED_LAP305_PROBE_SHA:
        failures.append(f"lap305 probe sha drifted: {lap305_sha}")

    instructions = parse(disassemble())
    if not instructions:
        failures.append("objdump produced no .text instructions")

    # R1 — re-derive the 291 literal stack-argument sites and their first call.
    push_text = f"push   0x{GRAPHICS_OBJECT:x}"
    sites = [index for index, item in enumerate(instructions) if item[2] == push_text]
    targets: dict[str, int] = {}
    unresolved: list[str] = []
    arg1_sites = 0
    separated_sites: list[str] = []
    for index in sites:
        address, target, esp_moved = first_call_after(instructions, index)
        if target is None:
            unresolved.append(f"0x{address:x}")
            continue
        targets[f"0x{target:x}"] = targets.get(f"0x{target:x}", 0) + 1
        if not esp_moved:
            arg1_sites += 1
        if instructions[index + 1][2] != f"call   0x{target:x}":
            separated_sites.append(f"0x{address:x}")
    report["R1_stack_argument_sites"] = {
        "site_count": len(sites),
        "first_call_target_counts": targets,
        "unresolved_sites": unresolved,
        "push_immediately_precedes_call": len(sites) - len(separated_sites),
        "sites_with_non_esp_instructions_before_call": separated_sites,
        "object_is_arg1": arg1_sites == len(sites),
        "lap305_claim": "291 sites, all -> 0x465250",
        "verdict": "CONFIRMED"
        if len(sites) == 291 and targets == {f"0x{SHARED_CALLEE:x}": 291}
        else "REFUTED",
    }
    if len(sites) != 291:
        failures.append(f"expected 291 stack-argument sites, found {len(sites)}")
    if targets != {f"0x{SHARED_CALLEE:x}": 291}:
        failures.append(f"unexpected first-call targets: {targets}")
    if arg1_sites != len(sites):
        failures.append(
            f"object is not arg1 at every site: {arg1_sites}/{len(sites)} keep the arg1 slot"
        )

    # R2 — the shared callee's entry-relative argument use, both normalisations.
    body = callee_body(instructions, SHARED_CALLEE)
    correct = entry_relative_accesses(body, sign=-1)
    lap305_style = entry_relative_accesses(body, sign=+1)
    field_writes = {
        f"0x{address:x}": instruction
        for address, _raw, instruction in body
        if FIELD_WRITE_RE.match(instruction)
    }
    indirect_calls = {
        f"0x{address:x}": instruction
        for address, _raw, instruction in body
        if instruction.startswith("call   DWORD PTR")
    }
    report["R2_shared_callee_argument_use"] = {
        "entry": f"0x{SHARED_CALLEE:x}",
        "body_end": f"0x{body[-1][0]:x}" if body else None,
        "entry_relative_arg1_arg2_accesses_correct_sign": correct,
        "entry_relative_arg1_arg2_accesses_lap305_sign": lap305_style,
        "arg_plus_4_or_8_field_writes": field_writes,
        "indirect_calls": indirect_calls,
        "lap305_claim": "entry-relative arg1/arg2 accesses = 0, object not read or forwarded",
        "verdict": "REFUTED" if correct and not lap305_style else "UNEXPECTED",
    }
    if not body:
        failures.append("shared callee body not found")
    if not correct:
        failures.append("review failed to reproduce any entry-relative arg1/arg2 access")
    if lap305_style:
        failures.append(
            f"lap305 normalisation unexpectedly reported accesses: {lap305_style}"
        )

    # R3 — the normalisation defect, stated as a sign error.
    report["R3_normalisation_defect"] = {
        "defect": "lap305 computed entry_offset = raw + depth; esp moves down, so it is raw - depth",
        "lap305_source_line": "entry_offset = raw_offset + delta",
        "effect": "false negative: every arg slot read after a `sub esp` is pushed out of range",
        "missed_arg1_read": correct.get("0x46526d"),
        "missed_arg2_read": correct.get("0x465287"),
        "join_depth_note": (
            "0x465287 is the target of `je` at 0x46527f, so its depth is fixed at "
            "0x100 by that predecessor; the fall-through depth is otherwise unknown "
            "because `call DWORD PTR [ecx+0x28]` hides its own argument cleanup"
        ),
        "still_true_under_both": "no [arg+4]/[arg+8] write inside the shared callee",
        "numeric_impact_on_writer_count": 0,
    }
    if sorted(correct) != ["0x46526d", "0x465287"]:
        failures.append(f"unexpected set of entry-relative accesses: {sorted(correct)}")
    if field_writes:
        failures.append(f"shared callee writes +4/+8 fields: {field_writes}")

    # R4 — what the shared callee actually is, from its own arguments.
    sample_index = sites[0] if sites else None
    sample_pushes = (
        [instructions[sample_index - offset][2] for offset in range(0, 3)]
        if sample_index is not None
        else []
    )
    literals = [
        int(match.group(1), 16)
        for text in sample_pushes
        if (match := re.match(r"^push   0x([0-9a-f]+)$", text))
    ]
    report["R4_shared_callee_identity"] = {
        "sample_site": f"0x{instructions[sample_index][0]:x}" if sample_index is not None else None,
        "sample_argument_literals": {
            f"0x{value:x}": cstring(exe_bytes, value) for value in literals
        },
        "format_argument_slot": "arg3, read at 0x465250 as [esp+0xc] and passed to 0x4db933",
        "vararg_pointer": "0x46525a lea eax,[esp+0x110] = &arg4 at depth 0x100",
        "classification": "variadic formatted-logging helper; arg1 is the sink object",
        "consequence": "the 291 sites are log calls, so they cannot carry a screen-geometry write",
    }
    if not any(
        isinstance(text, str) and "%d" in text
        for text in report["R4_shared_callee_identity"]["sample_argument_literals"].values()
    ):
        failures.append("no format string found among the sample call's literal arguments")

    # R5 — independent writer accounting, including the moffs encoding.
    absolute_writers: dict[str, str] = {}
    moffs_writers_anywhere = 0
    for address, raw, instruction in instructions:
        if MOFFS_STORE_RE.match(raw):
            moffs_writers_anywhere += 1
        match = ABSOLUTE_WRITE_RE.match(instruction)
        if match and int(match.group(1), 16) in (SCREEN_W_GLOBAL, SCREEN_H_GLOBAL):
            absolute_writers[f"0x{address:x}"] = instruction
    mode_body = instructions[
        next(i for i, item in enumerate(instructions) if item[0] == MODE_TABLE_FUNC) :
    ][:200]
    mode_writers = {
        f"0x{address:x}": instruction
        for address, _raw, instruction in mode_body
        if re.match(r"^mov\s+DWORD PTR \[esi\+0x[48]\],0x", instruction)
    }
    table = read_va(exe_bytes, MODE_JUMP_TABLE, 32)
    mode_value = struct.unpack("<I", read_va(exe_bytes, MODE_GLOBAL, 4))[0]
    entries = [f"0x{value:x}" for value in struct.unpack("<8I", table)]
    mode_refs = [
        f"0x{address:x}"
        for address, _raw, instruction in instructions
        if f"0x{MODE_GLOBAL:x}"[2:] in instruction.replace("0x", "")
        and f"{MODE_GLOBAL:x}" in instruction
    ]
    mode_writes = [
        ref
        for ref, instruction in (
            (f"0x{address:x}", instruction)
            for address, _raw, instruction in instructions
            if f"{MODE_GLOBAL:x}" in instruction
        )
        if re.match(r"^mov\s+(?:(?:DWORD|WORD|BYTE) PTR )?ds:0x[0-9a-f]+,", instruction)
    ]
    report["R5_writer_accounting"] = {
        "absolute_screen_global_writers": absolute_writers,
        "absolute_count": len(absolute_writers),
        "mode_table_immediate_writers": mode_writers,
        "mode_table_count": len(mode_writers),
        "confirmed_lower_bound": len(absolute_writers) + len(mode_writers),
        "moffs_stores_present_in_image": moffs_writers_anywhere,
        "moffs_stores_to_screen_globals": 0,
        "moffs_note": (
            "a2/a3 short stores do exist in this image, so the earlier "
            "'not present in this image' wording is imprecise; none target "
            "0xE5BF1C/0xE5BF20, which is what the count actually needs"
        ),
        "mode_jump_table": {f"0x{MODE_JUMP_TABLE:x}": entries},
        "mode_global_initial_value": mode_value,
        "mode_global_reference_count": len(mode_refs),
        "mode_global_write_count": len(mode_writes),
        "selected_case": entries[mode_value - 1] if 1 <= mode_value <= 8 else None,
        "verdict": "lap304 R5/R6 and lap305 lower bound 20 CONFIRMED",
    }
    if len(absolute_writers) != 4:
        failures.append(f"expected 4 absolute screen writers, found {len(absolute_writers)}")
    if len(mode_writers) != 16:
        failures.append(f"expected 16 mode-table writers, found {len(mode_writers)}")
    if mode_value != 3 or entries[mode_value - 1] != "0x464502":
        failures.append(f"mode selection drifted: value={mode_value} entries={entries}")
    if mode_writes:
        failures.append(f"mode global is written somewhere: {mode_writes}")

    report["verdict"] = {
        "lap305_V1_numeric_result": "ACCEPT — 291 sites, one callee, 0 new writers, lower bound 20",
        "lap305_V1_supporting_claim": "REJECT — 'no entry-relative arg1/arg2 access' is a false negative",
        "handoff": "work tier repairs the sign in a NEW probe; lap305 artefacts are preserved unmodified",
    }
    report["limitations"] = [
        "static only: no game, Wine, Xvfb, runtime, Stage B, PNG, or click execution",
        "callee_body still stops at the first ret; verified adequate for 0x465250 and 0x4644A0 only",
        "computed pointers, virtual/indirect dispatch, and the 0x465284 sink call remain fail-open",
        "20 is a confirmed lower bound, not a product G1 pass",
    ]
    report["failures"] = failures
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
