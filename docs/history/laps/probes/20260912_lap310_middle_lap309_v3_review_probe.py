"""lap310 middle — independent review of the lap309 V3 repair (R2, R3, R5).

The review deliberately avoids the lap309 method: it parses the SHA-pinned
original PE image directly (headers, sections, import directory, raw bytes)
instead of re-parsing `objdump` text, and it *solves* for the two unknown
call-cleanup amounts instead of asserting them from a literal table.  Only the
original executable and the immutable lap309 artifacts are pinned; this probe
never pins its own output (the lap296/W3 self-pin trap).

Read-only static audit.  No game, Wine, Xvfb, runtime, Stage B, PNG, or click
execution.  The report is emitted on stdout only; the caller redirects stdout
to the lap report file so the report is exactly the generator output.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import struct


REPO = Path(__file__).resolve().parents[4]
EXE = REPO / "Syw2plus" / "syw2plus_original.exe"
EXPECTED_EXE_SHA = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"

# Immutable lap309 artifacts under review (already written, never regenerated here).
LAP309_ARTIFACTS = {
    "probe": (
        Path("docs/history/laps/probes/20260912_lap309_work_v3_mode_writer_order_probe.py"),
        "76e68c22402e627e3146b52f393f5600795fc0bf9946eb5d134216980bc1ac2c",
    ),
    "report": (
        Path("logs/lap309/lap309_v3_mode_writer_order.json"),
        "7f2a876fa64e973f7eea23f269f476f25f9b654a6b8f61be9a943ee2e0d34a79",
    ),
    "test": (
        Path("tests/test_lap309_mode_writer_probe.py"),
        "ba3f2b52da3c921961dad0a834d8eb27fc599ec66444e1bfa00327b8a55b35c0",
    ),
}

MAP_ENTRY = 0x431AB0
DIALOG_ENTRY = 0x4D60B0
MAP_GATE_BRANCH = 0x431AF2
MAP_FAILURE_SEED = 0x431AF4
MAP_FAILURE_RET = 0x431AFD
MAP_SUCCESS_JOIN = 0x431AFE
SCREEN_W = 0xE5BF1C
SCREEN_H = 0xE5BF20

# Byte-pinned instruction anchors: (address, raw bytes, meaning).
ANCHORS = (
    (MAP_GATE_BRANCH, "750a", "jne 0x431afe (success); fall-through 0x431af4 is the failure arm"),
    (MAP_FAILURE_SEED, "5f5e5d33c05b83c434c3", "failure epilogue: pops, xor eax,eax, add esp,0x34, ret"),
    (0x431B79, "892d1cbfe500", "runtime writer: mov ds:0xe5bf1c,ebp"),
    (0x431B7F, "893d20bfe500", "runtime writer: mov ds:0xe5bf20,edi"),
    (0x4324B8, "c7051cbfe50080020000", "reset writer: mov ds:0xe5bf1c,0x280"),
    (0x4324C2, "c70520bfe500e0010000", "reset writer: mov ds:0xe5bf20,0x1e0"),
    (0x4324CC, "b801000000", "mov eax,1 (success return value)"),
    (0x4324D5, "c3", "success ret"),
    (0x4D6312, "a11cbfe500", "dialog reader: mov eax,ds:0xe5bf1c"),
    (0x4D631C, "a120bfe500", "dialog reader: mov eax,ds:0xe5bf20"),
    (0x4D632A, "66890d5c8b0801", "dialog store: mov WORD PTR ds:0x1088b5c,cx"),
    (0x4D6348, "66893d5e8b0801", "dialog store: mov WORD PTR ds:0x1088b5e,di"),
)

# 32-bit stores into the screen globals, in every encoding the image uses.
SCREEN_STORE_PREFIXES = ("89", "c705", "a3")

CALLEE = 0x465250
CALLEE_RET = 0x4652AE
CALLEE_JOIN = 0x465287
CALLEE_ARG1_READ = 0x46526D
CALLEE_VCALL = 0x465284
CALLEE_IMPORT_CALL = 0x46529D
IMPORT_SLOT = 0x4E51CC

# Byte-pinned decode of 0x465250..0x4652ae.  `delta` is the esp change; the two
# unknown cleanups are symbolic ("V" = indirect callee cleanup at 0x465284,
# "I" = import callee cleanup at 0x46529d).  `esp_read` is the literal esp
# displacement of a [esp+disp] memory operand, when the instruction has one.
CALLEE_DECODE = (
    (0x465250, "8b4c240c", 0, 0x0C, "mov ecx,[esp+0xc]"),
    (0x465254, "81ec00010000", +0x100, None, "sub esp,0x100"),
    (0x46525A, "8d842410010000", 0, 0x110, "lea eax,[esp+0x110]"),
    (0x465261, "8d542400", 0, 0x00, "lea edx,[esp+0x0]"),
    (0x465265, "50", +4, None, "push eax"),
    (0x465266, "51", +4, None, "push ecx"),
    (0x465267, "52", +4, None, "push edx"),
    (0x465268, "e8c6660700", 0, None, "call 0x4db933 (cdecl, caller cleans below)"),
    (CALLEE_ARG1_READ, "8b84241001 0000", 0, 0x110, "mov eax,[esp+0x110]"),
    (0x465274, "83c40c", -0x0C, None, "add esp,0xc (cdecl cleanup of the 3 pushes)"),
    (0x465277, "8b801815 0000", 0, None, "mov eax,[eax+0x1518]"),
    (0x46527D, "85c0", 0, None, "test eax,eax"),
    (0x46527F, "7406", 0, None, "je 0x465287"),
    (0x465281, "8b08", 0, None, "mov ecx,[eax]"),
    (0x465283, "50", +4, None, "push eax"),
    (CALLEE_VCALL, "ff5128", "-V", None, "call [ecx+0x28] (unknown cleanup V)"),
    (CALLEE_JOIN, "8b942408010000", 0, 0x108, "mov edx,[esp+0x108]"),
    (0x46528E, "8b0dc0a4ec00", 0, None, "mov ecx,ds:0xeca4c0"),
    (0x465294, "6a00", +4, None, "push 0x0"),
    (0x465296, "8d442404", 0, 0x04, "lea eax,[esp+0x4]"),
    (0x46529A, "52", +4, None, "push edx"),
    (0x46529B, "50", +4, None, "push eax"),
    (0x46529C, "51", +4, None, "push ecx"),
    (CALLEE_IMPORT_CALL, "ff15cc514e00", "-I", None, f"call ds:0x{IMPORT_SLOT:x} (unknown cleanup I)"),
    (0x4652A3, "b801000000", 0, None, "mov eax,0x1"),
    (0x4652A8, "81c400010000", -0x100, None, "add esp,0x100"),
    (CALLEE_RET, "c3", 0, None, "ret (cdecl: esp must be back at entry depth)"),
)

# Path A skips the indirect call (je taken); path B goes through it.
PATH_A_SKIP = (0x465281, 0x465283, CALLEE_VCALL)
# Win32 stdcall arity is an API contract, not a fact in this image; only the
# names the probe actually resolves are listed.
STDCALL_ARITY = {"MessageBoxA": 4}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Image:
    """Minimal read-only PE view: sections, VA translation, import names."""

    def __init__(self, data: bytes) -> None:
        self.data = data
        pe = struct.unpack_from("<I", data, 0x3C)[0]
        if data[pe : pe + 4] != b"PE\0\0":
            raise ValueError("not a PE image")
        section_count = struct.unpack_from("<H", data, pe + 6)[0]
        optional_size = struct.unpack_from("<H", data, pe + 20)[0]
        optional = pe + 24
        self.base = struct.unpack_from("<I", data, optional + 28)[0]
        self.import_rva = struct.unpack_from("<I", data, optional + 104)[0]
        self.sections = []
        cursor = optional + optional_size
        for _ in range(section_count):
            name = data[cursor : cursor + 8].rstrip(b"\0").decode("ascii", "replace")
            virtual_size, virtual_address, raw_size, raw_pointer = struct.unpack_from("<IIII", data, cursor + 8)
            self.sections.append((name, virtual_address, virtual_size, raw_pointer, raw_size))
            cursor += 40

    def offset(self, va: int) -> int | None:
        rva = va - self.base
        for _name, virtual_address, virtual_size, raw_pointer, raw_size in self.sections:
            if virtual_address <= rva < virtual_address + min(max(virtual_size, 1), raw_size):
                return raw_pointer + (rva - virtual_address)
        return None

    def read(self, va: int, length: int) -> bytes:
        offset = self.offset(va)
        if offset is None:
            raise ValueError(f"unmapped va 0x{va:x}")
        return self.data[offset : offset + length]

    def section(self, name: str) -> tuple[int, bytes]:
        for entry_name, virtual_address, _virtual_size, raw_pointer, raw_size in self.sections:
            if entry_name == name:
                return self.base + virtual_address, self.data[raw_pointer : raw_pointer + raw_size]
        raise KeyError(name)

    def import_name_for_slot(self, slot_va: int) -> str | None:
        cursor = self.offset(self.base + self.import_rva)
        if cursor is None:
            return None
        while True:
            lookup, _stamp, _chain, name_rva, thunk_rva = struct.unpack_from("<IIIII", self.data, cursor)
            if not (lookup or name_rva or thunk_rva):
                return None
            cursor += 20
            slot = self.base + thunk_rva
            entry_offset = self.offset(slot)
            if entry_offset is None:
                continue
            while True:
                entry = struct.unpack_from("<I", self.data, self.offset(slot))[0]
                if entry == 0:
                    break
                if slot == slot_va:
                    if entry & 0x80000000:
                        return f"#ordinal{entry & 0xFFFF}"
                    hint_offset = self.offset(self.base + entry)
                    end = self.data.index(b"\0", hint_offset + 2)
                    return self.data[hint_offset + 2 : end].decode("ascii", "replace")
                slot += 4


def hex_bytes(text: str) -> bytes:
    return bytes.fromhex(text.replace(" ", ""))


def walk(decode, skip: set[int]) -> tuple[int, int, int, dict[int, int]]:
    """Return (const_depth, v_count, i_count, entry_relative_offsets) for one path."""
    const, v_count, i_count = 0, 0, 0
    offsets: dict[int, int] = {}
    for address, _raw, delta, esp_read, _text in decode:
        if address in skip:
            continue
        if esp_read is not None:
            offsets[address] = esp_read - const
        if delta == "-V":
            v_count += 1
        elif delta == "-I":
            i_count += 1
        else:
            const += delta
    return const, v_count, i_count, offsets


def scan_direct_calls(text_base: int, text: bytes, target: int) -> list[int]:
    hits = []
    for index in range(len(text) - 5):
        if text[index] == 0xE8:
            displacement = struct.unpack_from("<i", text, index + 1)[0]
            if text_base + index + 5 + displacement == target:
                hits.append(text_base + index)
    return hits


def scan_absolute_refs(image: Image, target: int) -> dict[str, list[str]]:
    needle = struct.pack("<I", target)
    found: dict[str, list[str]] = {}
    for name, virtual_address, _virtual_size, raw_pointer, raw_size in image.sections:
        blob = image.data[raw_pointer : raw_pointer + raw_size]
        start = 0
        while True:
            index = blob.find(needle, start)
            if index < 0:
                break
            found.setdefault(name, []).append(f"0x{image.base + virtual_address + index:x}")
            start = index + 1
    return found


def main() -> int:  # noqa: C901 - one bounded static audit report
    failures: list[str] = []
    report: dict[str, object] = {
        "probe": Path(__file__).name,
        "lap": 310,
        "role": "middle (independent review/confirm); no game code edited, no execution",
        "reviewing": "lap309 work V3 R2/R3/R5 repair",
        "method": "direct PE parse of the pinned image; no objdump, no lap309 code imported",
        "execution": False,
        "report_contract": "JSON on stdout; redirect stdout, never hand-transcribe",
    }
    if not EXE.is_file():
        report["failures"] = [f"missing original executable: {EXE}"]
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1

    data = EXE.read_bytes()
    exe_sha = sha256_bytes(data)
    artifact_sha = {}
    for key, (relative, expected) in LAP309_ARTIFACTS.items():
        path = REPO / relative
        actual = sha256_bytes(path.read_bytes()) if path.is_file() else None
        artifact_sha[key] = {"path": str(relative), "sha256": actual, "matches_pin": actual == expected}
        if actual != expected:
            failures.append(f"lap309 {key} sha drift: {actual}")
    report["sha256"] = {"original_exe": exe_sha, "lap309": artifact_sha}
    if exe_sha != EXPECTED_EXE_SHA:
        failures.append(f"original exe sha mismatch: {exe_sha}")

    image = Image(data)
    text_base, text = image.section(".text")

    # M1 — byte-level anchors (independent of any disassembler).
    anchors = {}
    for address, raw, meaning in ANCHORS:
        expected = hex_bytes(raw)
        actual = image.read(address, len(expected))
        anchors[f"0x{address:x}"] = {"matches": actual == expected, "meaning": meaning}
        if actual != expected:
            failures.append(f"anchor 0x{address:x}: expected {raw}, found {actual.hex()}")

    # M2 — R2 review: the failure arm is the fall-through of a 2-byte jne.
    jne_target = MAP_GATE_BRANCH + 2 + image.read(MAP_GATE_BRANCH + 1, 1)[0]
    failure_block = image.read(MAP_FAILURE_SEED, MAP_FAILURE_RET + 1 - MAP_FAILURE_SEED)
    failure_hex = failure_block.hex()
    screen_globals = (struct.pack("<I", SCREEN_W).hex(), struct.pack("<I", SCREEN_H).hex())
    stores_in_failure = [g for g in screen_globals if g in failure_hex]
    seed_is_fallthrough = MAP_FAILURE_SEED == MAP_GATE_BRANCH + 2
    report["m2_r2_failure_arm"] = {
        "gate": f"0x{MAP_GATE_BRANCH:x}",
        "branch_target": f"0x{jne_target:x}",
        "fall_through_seed": f"0x{MAP_FAILURE_SEED:x}",
        "seed_is_fall_through": seed_is_fallthrough,
        "seed_is_not_the_ret": MAP_FAILURE_SEED != MAP_FAILURE_RET,
        "failure_block_bytes": len(failure_block),
        "failure_block_hex": failure_hex,
        "screen_global_operands_in_failure_block": stores_in_failure,
        "verdict": "PASS" if seed_is_fallthrough and not stores_in_failure else "FAIL",
        "power_note": (
            "the repair is real (the lap308 seed was the ret itself), but the failure arm is a "
            f"{len(failure_block)}-byte epilogue with no memory operand at all, so the assertion "
            "'no runtime writer here' is low-power; the load-bearing R2 claim is the success-side "
            "dominator result, which this probe does not re-derive"
        ),
    }
    if not seed_is_fallthrough or jne_target != MAP_SUCCESS_JOIN:
        failures.append(f"R2 gate geometry changed: target=0x{jne_target:x}, seed=0x{MAP_FAILURE_SEED:x}")
    if stores_in_failure:
        failures.append(f"R2 failure arm references screen globals: {stores_in_failure}")

    # M3 — R3 review: verify the decode byte-for-byte, then solve for V and I.
    decode_mismatch = [
        f"0x{address:x}: expected {raw}, found {image.read(address, len(hex_bytes(raw))).hex()}"
        for address, raw, _delta, _read, _text in CALLEE_DECODE
        if image.read(address, len(hex_bytes(raw))) != hex_bytes(raw)
    ]
    failures.extend(decode_mismatch)
    decoded_span = sum(len(hex_bytes(raw)) for _a, raw, _d, _r, _t in CALLEE_DECODE)
    if CALLEE + decoded_span != CALLEE_RET + 1:
        failures.append(f"R3 decode is not contiguous over 0x{CALLEE:x}..0x{CALLEE_RET:x}")

    const_a, v_a, i_a, offsets_a = walk(CALLEE_DECODE, set(PATH_A_SKIP))
    const_b, v_b, i_b, offsets_b = walk(CALLEE_DECODE, set())
    join_a, _va, _ia, _oa = walk([e for e in CALLEE_DECODE if e[0] < CALLEE_JOIN], set(PATH_A_SKIP))
    join_b_const, join_b_v, _ib, _ob = walk([e for e in CALLEE_DECODE if e[0] < CALLEE_JOIN], set())
    # join equality: join_a == join_b_const - join_b_v * V  (path A never calls V)
    solved_v = (join_b_const - join_a) // join_b_v if join_b_v else None
    # ret depth must be 0 for any `ret`: const_b - v_b*V - i_b*I == 0
    solved_i = (const_b - v_b * (solved_v or 0)) // i_b if i_b else None
    import_name = image.import_name_for_slot(IMPORT_SLOT)
    import_arity = STDCALL_ARITY.get(import_name or "")
    report["m3_r3_solved_call_cleanup"] = {
        "callee": f"0x{CALLEE:x}..0x{CALLEE_RET:x}",
        "decoded_instructions": len(CALLEE_DECODE),
        "decode_matches_image": not decode_mismatch,
        "join_depth_path_a_no_vcall": f"0x{join_a:x}",
        "join_depth_path_b_symbolic": f"0x{join_b_const:x} - {join_b_v}*V",
        "solved_vcall_cleanup_bytes": solved_v,
        "ret_depth_symbolic": f"0x{const_b:x} - {v_b}*V - {i_b}*I",
        "solved_import_cleanup_bytes": solved_i,
        "entry_relative_offsets": {
            f"0x{CALLEE_ARG1_READ:x}": offsets_a.get(CALLEE_ARG1_READ),
            f"0x{CALLEE_JOIN:x}": offsets_a.get(CALLEE_JOIN),
        },
        "path_b_offsets_agree": offsets_a.get(CALLEE_JOIN) == offsets_b.get(CALLEE_JOIN) + (join_b_v * (solved_v or 0)),
        "import_slot": f"0x{IMPORT_SLOT:x}",
        "import_name": import_name,
        "import_stdcall_arity": import_arity,
        "import_arity_implies_cleanup": None if import_arity is None else import_arity * 4,
        "verdict": "PASS" if solved_v == 4 and solved_i == 16 else "FAIL",
        "derivation_note": (
            "V and I are not assumed: path A reaches the join without the indirect call, so the "
            "single join depth forces V, and `ret` requires depth 0 at 0x4652ae, which then forces "
            "I.  The independently resolved import name gives the same I, so lap309's literal "
            "{0, 4, 16} table is confirmed rather than merely restated."
        ),
    }
    if solved_v != 4:
        failures.append(f"R3 solved indirect-call cleanup is {solved_v}, expected 4")
    if solved_i != 16:
        failures.append(f"R3 solved import cleanup is {solved_i}, expected 16")
    if import_name != "MessageBoxA" or import_arity is None or import_arity * 4 != solved_i:
        failures.append(f"R3 import cross-check failed: slot resolves to {import_name!r}")
    if offsets_a.get(CALLEE_ARG1_READ) != 4 or offsets_a.get(CALLEE_JOIN) != 8:
        failures.append(f"R3 entry offsets changed: {offsets_a.get(CALLEE_ARG1_READ)}, {offsets_a.get(CALLEE_JOIN)}")
    if offsets_a.get(CALLEE_JOIN) != offsets_b.get(CALLEE_JOIN) + join_b_v * (solved_v or 0):
        failures.append("R3 join offset disagrees between the two paths once V is applied")

    # M5 — R5 review: direct callers from raw E8 encodings, plus an absolute-reference sweep.
    map_callers = scan_direct_calls(text_base, text, MAP_ENTRY)
    dialog_callers = scan_direct_calls(text_base, text, DIALOG_ENTRY)
    map_absolute = scan_absolute_refs(image, MAP_ENTRY)
    dialog_absolute = scan_absolute_refs(image, DIALOG_ENTRY)
    report["m5_r5_caller_assertion"] = {
        "map_entry": f"0x{MAP_ENTRY:x}",
        "map_direct_callers": [f"0x{a:x}" for a in map_callers],
        "dialog_entry": f"0x{DIALOG_ENTRY:x}",
        "dialog_direct_callers": [f"0x{a:x}" for a in dialog_callers],
        "map_absolute_dword_refs": map_absolute,
        "dialog_absolute_dword_refs": dialog_absolute,
        "verdict": "PASS" if map_callers == [0x48F538] and dialog_callers == [0x4D69E5, 0x4D6A05] else "FAIL",
        "method_note": (
            "raw E8 rel32 scan over .text plus a whole-image scan for the literal entry addresses; "
            "the second sweep is what lap309's disassembly-text match could not do"
        ),
    }
    if map_callers != [0x48F538]:
        failures.append(f"R5 map direct callers changed: {[hex(a) for a in map_callers]}")
    if dialog_callers != [0x4D69E5, 0x4D6A05]:
        failures.append(f"R5 dialog direct callers changed: {[hex(a) for a in dialog_callers]}")

    report["anchors"] = anchors
    report["limitations"] = [
        "static only: no game, Wine, Xvfb, runtime, Stage B, PNG, or clicks",
        "confirms lap309's static model; produces no G1/G2/G3/G4 product evidence",
        "the success-side dominator claim is re-checked only at byte level, not re-derived as a CFG",
        "computed pointers and virtual dispatch outside the inspected sites remain UNKNOWN",
        "click-time mode value, map/dialog event and thread order remain UNKNOWN",
    ]
    report["failures"] = failures
    report["verdict"] = "PASS" if not failures else "FAIL"
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
