#!/usr/bin/env python3
"""lap326 middle probe — R1 reach predicate and store/PS ordering, re-derived from the original PE.

Read-only. No game execution, no harness change, no patching. Emits one JSON report on stdout.

Question this probe answers (lap325 Astra handoff items 1 and 2):
  1. Is there a non-circular, byte-grounded predicate for "the load dialog was constructed"?
  2. Are the two origin stores (x at 0x1088B5C, y at 0x1088B5E) sampleable without a torn pair?

Method: parse PE sections, scan .text for absolute operands and rel32 control transfers,
and check exact instruction bytes at the sites the answer depends on. Every check appends to
`failures` as it runs; the report is built from whatever ran, so a missing site cannot raise
before the JSON is emitted (this is the N4 pre-evaluation trap, avoided deliberately).
"""

from __future__ import annotations

import hashlib
import json
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
ORIGINAL = REPO / "Syw2plus" / "syw2plus_original.exe"
ORIGINAL_SHA = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"

PS_ADDR = 0x4ED818
ORIGIN_X = 0x1088B5C
ORIGIN_Y = 0x1088B5E
ORIGIN_TAG = 0x1088B60
SCREEN_W_GLOBAL = 0xE5BF1C
SCREEN_H_GLOBAL = 0xE5BF20

DISPATCH_READ = 0x4233B8
DISPATCH_TABLE = 0x423738
PS34_ARM = 0x423411
PS34_HANDLER = 0x4248E0
PS35_WRITE = 0x4248E5
PS35_HANDLER = 0x4248F0
PREPROCESS = 0x4A2FF0
CONSTRUCT = 0x493C40
DIALOG_WRAPPER = 0x4D6A00
DIALOG_BODY = 0x4D60B0
STORE_X = 0x4D632A
STORE_Y = 0x4D6348


def load_sections(data: bytes) -> dict[str, tuple[int, int, int]]:
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    nsec = struct.unpack_from("<H", data, pe + 6)[0]
    optsz = struct.unpack_from("<H", data, pe + 20)[0]
    imgbase = struct.unpack_from("<I", data, pe + 24 + 28)[0]
    out: dict[str, tuple[int, int, int]] = {}
    base = pe + 24 + optsz
    for i in range(nsec):
        raw = data[base + i * 40:base + (i + 1) * 40]
        name = raw[:8].rstrip(b"\0").decode("ascii", "replace")
        _vsz, va, rsz, ra = struct.unpack_from("<IIII", raw, 8)
        out[name] = (va + imgbase, ra, rsz)
    return out


def main() -> int:
    failures: list[str] = []
    report: dict[str, object] = {"lap": 326, "probe": Path(__file__).name}

    data = ORIGINAL.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    report["original_sha256"] = sha
    if sha != ORIGINAL_SHA:
        failures.append(f"original SHA mismatch: {sha}")
        print(json.dumps({**report, "failures": failures}, indent=2, sort_keys=True))
        return 1

    secs = load_sections(data)
    text_va, text_ra, text_rsz = secs[".text"]
    text = data[text_ra:text_ra + text_rsz]
    text_end = text_va + text_rsz
    report["text_range"] = [hex(text_va), hex(text_end)]

    def at(va: int, n: int) -> bytes:
        return text[va - text_va:va - text_va + n]

    def expect(va: int, hexbytes: str, label: str) -> None:
        want = bytes.fromhex(hexbytes)
        got = at(va, len(want))
        if got != want:
            failures.append(f"{label} @{va:#x}: want {want.hex()} got {got.hex()}")

    # --- 1. dispatcher reads PS as a sign-extended WORD -------------------------------
    expect(DISPATCH_READ, "0fbf0518d84e00", "dispatcher movsx WORD [PS]")
    report["dispatcher_read"] = {"va": hex(DISPATCH_READ), "form": "movsx eax, WORD PTR ds:0x4ED818"}

    # --- 2. jump table arm for PS=34 -------------------------------------------------
    table = [struct.unpack_from("<I", text, DISPATCH_TABLE - text_va + i * 4)[0] for i in range(35)]
    report["dispatch_table"] = {"va": hex(DISPATCH_TABLE), "entries": 35,
                                "ps34": hex(table[33]), "ps35": hex(table[34]),
                                "ps9": hex(table[8])}
    if table[33] != PS34_ARM:
        failures.append(f"PS=34 table entry is {table[33]:#x}, expected {PS34_ARM:#x}")
    expect(PS34_ARM, "e8ca140000", "PS=34 arm call 0x4248E0")

    # --- 3. PS=34 handler: construct first, PS:=35 after -----------------------------
    expect(PS34_HANDLER, "e80be70700", "PS34 handler call 0x4A2FF0")
    expect(PS35_WRITE, "66c70518d84e002300", "PS34 handler store WORD [PS],35")
    expect(PS35_WRITE + 9, "c3", "PS34 handler ret")

    # --- 4. PS immediate writers: 35 must be singular; register stores are fail-open ---
    ps_pat = struct.pack("<I", PS_ADDR)
    imm35: list[str] = []
    imm_total = reg_stores = 0
    for i in range(len(text) - 3):
        if text[i:i + 4] != ps_pat:
            continue
        pre3 = text[i - 3:i]
        pre2 = text[i - 2:i]
        if pre3 == b"\x66\xc7\x05":
            imm_total += 1
            if struct.unpack_from("<H", text, i + 4)[0] == 35:
                imm35.append(hex(text_va + i - 3))
        elif pre2 == b"\x66\xa3" or (pre3[:1] == b"\x66" and len(pre3) == 3 and pre3[1] == 0x89):
            reg_stores += 1
    report["ps_writers"] = {"immediate_total": imm_total, "immediate_value_35": imm35,
                            "register_stores_fail_open": reg_stores}
    if imm35 != [hex(PS35_WRITE)]:
        failures.append(f"PS=35 immediate writers {imm35} != [{hex(PS35_WRITE)}]")

    # --- 5. rel32 call/jmp graph for the construct chain ------------------------------
    def refs(target: int) -> list[tuple[str, str]]:
        out = []
        for i in range(len(text) - 4):
            op = text[i]
            if op in (0xE8, 0xE9):
                rel = struct.unpack_from("<i", text, i + 1)[0]
                if text_va + i + 5 + rel == target:
                    out.append((hex(text_va + i), "call" if op == 0xE8 else "jmp"))
        return out

    chain = {hex(t): refs(t) for t in (PREPROCESS, CONSTRUCT, DIALOG_WRAPPER, DIALOG_BODY,
                                       0x4A3000)}
    report["chain_callers"] = chain
    if chain[hex(PREPROCESS)] != [(hex(PS34_HANDLER), "call")]:
        failures.append(f"0x4A2FF0 callers {chain[hex(PREPROCESS)]} are not exactly the PS34 handler")
    if chain[hex(CONSTRUCT)] != [(hex(PREPROCESS + 5), "jmp")]:
        failures.append(f"0x493C40 refs {chain[hex(CONSTRUCT)]} are not exactly the 0x4A2FF0 tail jmp")
    if chain[hex(DIALOG_BODY)] != [("0x4d69e5", "call"), ("0x4d6a05", "call")]:
        failures.append(f"0x4D60B0 callers changed: {chain[hex(DIALOG_BODY)]}")
    if chain["0x4a3000"] != [(hex(PS35_HANDLER + 1), "call")]:
        failures.append(f"0x4A3000 callers {chain['0x4a3000']} are not exactly the PS35 handler")

    expect(PREPROCESS, "e81b21ffff", "0x4A2FF0 call 0x495110")
    expect(PREPROCESS + 5, "e9460cffff", "0x4A2FF0 tail jmp 0x493C40")
    expect(CONSTRUCT, "6a08", "0x493C40 push 8")
    expect(CONSTRUCT + 2, "e8b92d0400", "0x493C40 call 0x4D6A00")
    expect(DIALOG_WRAPPER, "b978620801", "0x4D6A00 mov ecx,0x1086278")
    expect(DIALOG_WRAPPER + 5, "e8a6f6ffff", "0x4D6A00 call 0x4D60B0")

    # second direct caller of the wrapper must push a different tag
    expect(0x493D66, "68e8030000", "0x493D66 push 0x3E8 (other 0x4D6A00 caller)")

    # --- 6. origin stores inside 0x4D60B0 ---------------------------------------------
    expect(0x4D6312, "a11cbfe500", "read screen width global")
    expect(0x4D631C, "a120bfe500", "read screen height global")
    expect(STORE_X, "66890d5c8b0801", "store WORD [0x1088B5C],cx")
    expect(STORE_Y, "66893d5e8b0801", "store WORD [0x1088B5E],di")
    gap = at(STORE_X + 7, STORE_Y - STORE_X - 7)
    if len(gap) != 23:
        failures.append(f"x->y store gap is {len(gap)} bytes, expected 23")
    report["origin_stores"] = {"x": hex(STORE_X), "y": hex(STORE_Y),
                               "gap_bytes": len(gap), "gap_hex": gap.hex(),
                               "width_global": hex(SCREEN_W_GLOBAL),
                               "height_global": hex(SCREEN_H_GLOBAL)}

    # --- 7. direct-store census for the three adjacent globals ------------------------
    census: dict[str, dict[str, object]] = {}
    for target in (ORIGIN_X, ORIGIN_Y, ORIGIN_TAG):
        pat = struct.pack("<I", target)
        occ = 0
        stores: list[str] = []
        for i in range(len(text) - 3):
            if text[i:i + 4] != pat:
                continue
            occ += 1
            pre3 = text[i - 3:i]
            pre2 = text[i - 2:i]
            if pre3[:1] == b"\x66" and pre3[1] == 0x89:
                stores.append(hex(text_va + i - 3))
            elif pre2 == b"\x66\xa3":
                stores.append(hex(text_va + i - 2))
            elif pre3 == b"\x66\xc7\x05":
                stores.append(hex(text_va + i - 3))
        census[hex(target)] = {"operand_occurrences": occ, "direct_stores": stores}
    report["adjacent_global_census"] = census
    if census[hex(ORIGIN_X)]["direct_stores"] != [hex(STORE_X)]:
        failures.append(f"origin x direct stores changed: {census[hex(ORIGIN_X)]}")
    if census[hex(ORIGIN_Y)]["direct_stores"] != [hex(STORE_Y)]:
        failures.append(f"origin y direct stores changed: {census[hex(ORIGIN_Y)]}")
    if census[hex(ORIGIN_TAG)]["direct_stores"] != ["0x4d6a23", "0x4d6a2f"]:
        failures.append(f"origin tag direct stores changed: {census[hex(ORIGIN_TAG)]}")

    # --- 8. initial values: PS from raw .data, origins are BSS -------------------------
    data_va, data_ra, data_rsz = secs[".data"]
    ps_off = data_ra + (PS_ADDR - data_va)
    ps_initial_word = struct.unpack_from("<H", data, ps_off)[0]
    ps_initial_high = struct.unpack_from("<H", data, ps_off + 2)[0]
    report["initial_values"] = {
        "ps_word": ps_initial_word, "ps_high_word": ps_initial_high,
        "data_raw_last_va": hex(data_va + data_rsz),
        "origins_are_bss": ORIGIN_X >= data_va + data_rsz,
    }
    if not (ORIGIN_X >= data_va + data_rsz and ORIGIN_TAG >= data_va + data_rsz):
        failures.append("origin globals are inside raw .data; BSS zero-init assumption fails")
    if ps_initial_high != 0:
        failures.append(f"PS high word is {ps_initial_high}, a 4-byte PS read is not equivalent")

    # --- 9. A/B arithmetic from the decoded centering form -----------------------------
    spr_w, spr_h = 320, 310
    ab = {"A_800x600": [(800 - spr_w) // 2, (600 - spr_h) // 2],
          "B_640x480": [(640 - spr_w) // 2, (480 - spr_h) // 2]}
    report["candidates"] = ab
    if ab["A_800x600"] != [240, 145] or ab["B_640x480"] != [160, 85]:
        failures.append(f"A/B arithmetic changed: {ab}")

    report["ordering_claim"] = (
        "PS34 arm 0x423411 -> 0x4248E0 -> call 0x4A2FF0 -> tail jmp 0x493C40 -> push 8; "
        "call 0x4D6A00 -> call 0x4D60B0 (origin x then y) -> return -> 0x4248E5 sets PS=35. "
        "Every edge on this chain is unconditional, so an observer that sees PS==35 is "
        "strictly after both origin stores of this entry path."
    )
    report["fail_open"] = [
        "computed/indirect writers to the three globals are not excluded by an absolute-operand scan",
        f"{reg_stores} register stores to PS could carry value 35 at runtime",
        "the click at (296,505) is not statically proven to select the load button",
        "0x4D60B0 may early-return before the stores; that yields pre==post, not a candidate",
    ]

    report["failures"] = failures
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
