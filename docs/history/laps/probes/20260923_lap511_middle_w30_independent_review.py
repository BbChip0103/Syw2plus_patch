#!/usr/bin/env python3
"""lap511 middle — W30(lap510 work) 독립 검수 probe. 원본 읽기 전용, 게임 실행 없음.

lap510 의 hole_map.json / supply_ledger_32bit.EDITS 를 판정 입력으로 쓰지 않고
원본 EXE 와 원시 samples.jsonl 만으로 다시 계산한다.

A. 패치 재계산: 11곳 old-bytes, 후보 SHA, diff 범위, 패치 후 역디스어셈블, 원복.
B. 정적 위험: `.text` 전 메모리 오퍼랜드 중 PlayerStruct 상대 disp 가 새 구멍
   `[0x2100,0x2104)` 을 직접 덮거나, **인덱스 레지스터(SIB) 배열**의 시작 disp 가
   `[0x2014, 0x2104]` 에 있어 동적 인덱스로 구멍까지 닿을 수 있는 명령을 전부 나열한다.
C. 런타임 재계산: attempt1/attempt2 원시 window(+0x2000..+0x2110) 에서 바이트별 변화
   집합과 구멍 상수성을 재계산한다.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

import capstone
from capstone import x86

REPO = pathlib.Path(__file__).resolve().parents[4]
ORIGINAL_EXE = REPO / "Syw2plus" / "syw2plus_original.exe"
ORIGINAL_SHA = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"
CLAIMED_CANDIDATE_SHA = "7cb0faf3b71ca2ccfea82b4ff27e6dc6f979d2bb86ca411ae33835557eb809e0"
RUN_DIR = pathlib.Path(
    "/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/g2_capacity/"
    "20260923_lap510_work_f4b_ledger_32bit"
)
OUT = pathlib.Path("/tmp/lap511/w30_independent_review.json")

IMAGE_BASE = 0x400000
PS_BASE, PS_STRIDE, PS_COUNT = 0x956770, 0x3ABC, 8
HOLE = (0x2100, 0x2104)
ARRAY_WATCH = (0x2014, 0x2104)
# 카드 §1 + §6 (lap509 middle 원문) — lap510 코드가 아니라 카드에서 옮긴 기대값.
CARD_SITES = {
    0x43EDFC: "0fbf910c200000", 0x43EE9B: "6601910c200000", 0x43EF8B: "6629910c200000",
    0x43F0E9: "0fbf860c200000", 0x43F3B3: "0fbf850c200000",
    0x40DD12: "0fbf907c879500", 0x40E03B: "0fbf907c879500",
    0x499767: "0fbf887c879500", 0x499A0E: "0fbf887c879500",
    0x43EE93: "668b149538529b00", 0x43EF83: "668b149538529b00",
}


def sections(pe: bytes):
    e_lfanew = int.from_bytes(pe[0x3C:0x40], "little")
    nsec = int.from_bytes(pe[e_lfanew + 6:e_lfanew + 8], "little")
    opt = int.from_bytes(pe[e_lfanew + 20:e_lfanew + 22], "little")
    table = e_lfanew + 24 + opt
    for i in range(nsec):
        s = pe[table + 40 * i: table + 40 * (i + 1)]
        yield (s[:8].rstrip(b"\0").decode(), int.from_bytes(s[12:16], "little"),
               int.from_bytes(s[8:12], "little"), int.from_bytes(s[20:24], "little"),
               int.from_bytes(s[16:20], "little"))


def text_insns(pe: bytes):
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    md.detail = True
    md.skipdata = True
    for name, va, vsize, raw, rsize in sections(pe):
        if name == ".text":
            yield from md.disasm(pe[raw:raw + min(vsize, rsize)], IMAGE_BASE + va)


def ps_rel(op) -> tuple[int, str] | None:
    m = op.mem
    disp = m.disp & 0xFFFFFFFF
    # 절대주소 별칭은 base 레지스터(owner×stride)를 동반할 수 있다(예: [eax+0x95877c]).
    if PS_BASE <= disp < PS_BASE + PS_COUNT * PS_STRIDE:
        return (disp - PS_BASE) % PS_STRIDE, "abs"
    if m.base != 0 and 0 <= disp < PS_STRIDE:
        return disp, "rel"
    return None


def part_a(orig: bytes) -> dict:
    sys.path.insert(0, str(REPO / "patches" / "population"))
    import supply_ledger_32bit as p  # noqa: E402

    old_ok = {hex(va): orig[va - IMAGE_BASE: va - IMAGE_BASE + len(bytes.fromhex(h))].hex() == h
              for va, h in CARD_SITES.items()}
    edits_va = {va for va, _b, _a in p.EDITS}
    patched = p.patched_bytes(orig)
    diff = [i for i in range(len(orig)) if orig[i] != patched[i]]
    spans = [(va - IMAGE_BASE, va - IMAGE_BASE + len(b)) for va, b, _a in p.EDITS]
    outside = [hex(i) for i in diff if not any(s <= i < e for s, e in spans)]
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    dis = {}
    for va, before, _after in p.EDITS:
        off = va - IMAGE_BASE
        dis[hex(va)] = [f"{i.mnemonic} {i.op_str}".strip()
                        for i in md.disasm(patched[off:off + len(before)], va)]
    tmp = pathlib.Path("/tmp/lap511/restore_check")
    tmp.mkdir(parents=True, exist_ok=True)
    src, dst = tmp / "src.exe", tmp / "dst.exe"
    for f in (src, dst, pathlib.Path(str(dst) + ".original")):
        f.unlink(missing_ok=True)
    src.write_bytes(orig)
    created = p.create_copy(src, dst)
    restored = p.restore(dst)
    return {
        "card_old_bytes_match": old_ok,
        "edit_set_equals_card_set": edits_va == set(CARD_SITES),
        "candidate_sha": hashlib.sha256(patched).hexdigest(),
        "candidate_sha_matches_claim": hashlib.sha256(patched).hexdigest() == CLAIMED_CANDIDATE_SHA,
        "diff_bytes": len(diff), "diff_outside_sites": outside,
        "patched_disasm": dis,
        "create_copy_sha": created, "restore_sha_is_original": restored == ORIGINAL_SHA,
    }


def part_b(orig: bytes) -> dict:
    direct, arrays, old_field, pad_2016, bld_200e = [], [], [], [], []
    for insn in text_insns(orig):
        if insn.id == 0:
            continue
        for op in insn.operands:
            if op.type != x86.X86_OP_MEM:
                continue
            got = ps_rel(op)
            if got is None:
                continue
            rel, form = got
            rec = {"va": hex(insn.address), "insn": f"{insn.mnemonic} {insn.op_str}",
                   "rel": hex(rel), "form": form, "size": op.size,
                   "index": insn.reg_name(op.mem.index) if op.mem.index else None,
                   "scale": op.mem.scale}
            if rel < HOLE[1] and rel + op.size > HOLE[0]:
                direct.append(rec)
            if op.mem.index and ARRAY_WATCH[0] <= rel <= ARRAY_WATCH[1]:
                arrays.append(rec)
            if rel <= 0x200C < rel + op.size:
                old_field.append(rec)
            # 안 B 입력: +0x2016(리스트 count 워드와 dword 배열 사이 2B) 을 덮는 모든 접근,
            # +0x200e(building_count) 를 덮는 모든 접근.
            if rel < 0x2018 and rel + op.size > 0x2016:
                pad_2016.append(rec)
            if rel < 0x2010 and rel + op.size > 0x200E:
                bld_200e.append(rec)
    # +0x2014 리스트 추가 함수의 용량 상한(`cmp ax, 0x3e8`) 원본 바이트.
    bound = {hex(va): orig[va - IMAGE_BASE: va - IMAGE_BASE + 4].hex() for va in (0x43F4C7, 0x43F4F9)}
    list_end = 0x2018 + 0x3E8 * 4
    return {"direct_hole_overlap": direct, "indexed_arrays_starting_near_hole": arrays,
            "old_200c_touchers": old_field,
            "plan_b_pad_2016_touchers": pad_2016,
            "plan_b_building_200e_touchers": bld_200e,
            "list_2014_bound_bytes": bound,
            "list_2018_extent": [hex(0x2018), hex(list_end)],
            "hole_0x2100_inside_list": 0x2018 <= HOLE[0] and HOLE[1] <= list_end,
            "hole_0x2100_list_index": (HOLE[0] - 0x2018) // 4}


def part_c() -> dict:
    out = {}
    for arm, path in (("attempt1", RUN_DIR / "samples.jsonl"),
                      ("attempt2", RUN_DIR / "attempt2_hole2100" / "samples.jsonl")):
        rows = [json.loads(line) for line in path.open()]
        first = {o["owner"]: bytes.fromhex(o["window_hex"]) for o in rows[0]["owners"]}
        changed = set()
        hole_viol = pad_viol = 0
        list_count_max = 0
        n = 0
        covers_hole = len(first[0]) >= 0x104
        for r in rows:
            for o in r["owners"]:
                w = bytes.fromhex(o["window_hex"])
                n += 1
                changed |= {0x2000 + i for i in range(len(w)) if w[i] != first[o["owner"]][i]}
                if covers_hole and w[0x100:0x104] != first[o["owner"]][0x100:0x104]:
                    hole_viol += 1
                if w[0x16:0x18] != b"\0\0":
                    pad_viol += 1
                list_count_max = max(list_count_max, int.from_bytes(w[0x14:0x16], "little"))
        used = [max(o["used"] for r in rows for o in r["owners"] if o["owner"] == k) for k in range(8)]
        out[arm] = {
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "rows": len(rows), "owner_samples": n, "last_tick": rows[-1]["tick"],
            "window_covers_0x2100": covers_hole,
            "hole_0x2100_violations_vs_first": hole_viol if covers_hole else None,
            "pad_0x2016_nonzero_samples": pad_viol,
            "list_0x2014_count_max": list_count_max,
            "changed_offsets_min": hex(min(changed)) if changed else None,
            "changed_offsets_max": hex(max(changed)) if changed else None,
            "changed_offsets_ge_0x2014": sorted(hex(x) for x in changed if x >= 0x2014),
            "max_used_per_owner": used,
        }
    return out


def main() -> int:
    orig = ORIGINAL_EXE.read_bytes()
    if hashlib.sha256(orig).hexdigest() != ORIGINAL_SHA:
        raise SystemExit("원본 SHA 불일치 — STOP")
    result = {"original_sha": ORIGINAL_SHA, "A": part_a(orig), "B": part_b(orig), "C": part_c()}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=1, ensure_ascii=False))
    print(json.dumps(result, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
