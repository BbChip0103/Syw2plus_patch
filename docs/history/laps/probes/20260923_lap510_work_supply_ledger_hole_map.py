#!/usr/bin/env python3
"""lap510 work -- M-0 정적 구멍 맵 + M-b 원본 바이트 독립 재확인.

W30 카드(`docs/work/active/G2_F4B_SUPPLY_LEDGER_32BIT_LAP509.md`) M-0/M-b 를 lap509 와
독립적으로 재계산한다. lap509 는 필드별 고정 disp 목록에 대해서만 검사했다 -- 이 스크립트는
그와 달리 PlayerStruct 범위 [0, 0x3ABC) 안에서 등장하는 "모든" base+disp/절대주소 형태의
메모리 오퍼랜드를 오퍼랜드 크기(byte 단위)까지 포함해 수집하고, 그 합집합으로 덮이지 않는
4바이트 이상 연속 구간을 구멍 후보로 낸다. 읽기 전용. 원본/후보 바이트 변경 0, 메모리 쓰기 0,
게임 실행 0.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import struct
import sys

import capstone
from capstone.x86 import X86_OP_MEM

REPO_ROOT = pathlib.Path(__file__).resolve().parents[4]
ORIGINAL_EXE = REPO_ROOT / "Syw2plus" / "syw2plus_original.exe"
ORIGINAL_SHA256 = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"
ORIGINAL_SIZE = 1_032_192

IMAGE_BASE = 0x400000
PS_BASE = 0x956770
PS_STRIDE = 0x3ABC
PS_COUNT = 8

# W30 카드 §1 표 -- 독립 재확인 대상 9곳.
CARD_SITES = [
    (0x0043EDFC, "0f bf 91 0c 20 00 00"),
    (0x0043EE9B, "66 01 91 0c 20 00 00"),
    (0x0043EF8B, "66 29 91 0c 20 00 00"),
    (0x0043F0E9, "0f bf 86 0c 20 00 00"),
    (0x0043F3B3, "0f bf 85 0c 20 00 00"),
    (0x0040DD12, "0f bf 90 7c 87 95 00"),
    (0x0040E03B, "0f bf 90 7c 87 95 00"),
    (0x00499767, "0f bf 88 7c 87 95 00"),
    (0x00499A0E, "0f bf 88 7c 87 95 00"),
]

# lap509 §6 권고 인코딩이 필요로 하는 cost-load 동반 사이트 (writer 각각의 직전 로드).
CARD_COST_LOAD_SITES = [
    (0x0043EE93, "66 8b 14 95 38 52 9b 00"),
    (0x0043EF83, "66 8b 14 95 38 52 9b 00"),
]


def sha256_of(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_original() -> bytes:
    if not ORIGINAL_EXE.is_file():
        raise SystemExit(f"원본 EXE를 찾을 수 없다: {ORIGINAL_EXE}")
    data = ORIGINAL_EXE.read_bytes()
    actual = sha256_of(ORIGINAL_EXE)
    if actual != ORIGINAL_SHA256 or len(data) != ORIGINAL_SIZE:
        raise SystemExit(f"원본 fingerprint 불일치: sha256={actual} size={len(data)}")
    return data


def text_section(data: bytes) -> tuple[int, int, int]:
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    nsec = struct.unpack_from("<H", data, pe + 6)[0]
    opt_size = struct.unpack_from("<H", data, pe + 20)[0]
    for index in range(nsec):
        off = pe + 24 + opt_size + index * 40
        name = data[off : off + 8].rstrip(b"\0").decode("ascii", "replace")
        vsize, vaddr, _rsize, raw = struct.unpack_from("<IIII", data, off + 8)
        if name == ".text":
            return IMAGE_BASE + vaddr, raw, vsize
    raise SystemExit(".text 섹션을 찾지 못했다")


def sweep(code: bytes, base_va: int) -> dict[int, capstone.CsInsn]:
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    md.detail = True
    found: dict[int, capstone.CsInsn] = {}
    pos = 0
    size = len(code)
    while pos < size:
        advanced = False
        for insn in md.disasm(code[pos:], base_va + pos):
            found[insn.address] = insn
            advanced = True
            pos = insn.address - base_va + insn.size
        if not advanced:
            pos += 1
    covered = set()
    for addr, insn in found.items():
        covered.update(range(addr, addr + insn.size))
    for va in range(base_va, base_va + size):
        if va in covered:
            continue
        for insn in md.disasm(code[va - base_va : va - base_va + 16], va):
            found.setdefault(insn.address, insn)
            break
    return found


def operand_byte_size(op) -> int:
    # Capstone gives op.size in bytes for the memory operand width already.
    return op.size or 1


def touched_ranges(insns: dict[int, capstone.CsInsn]) -> list[tuple[int, int, int]]:
    """PlayerStruct[0] 절대주소(0x956770 base) 형태와 그 +0..PS_STRIDE 범위 base+disp 형태를
    모두 [byte_lo, byte_hi) 로 정규화해 낸다. 다른 base(스택 등)의 동일 disp 리터럴도
    보수적으로 포함한다 -- 안전한 방향의 과다 포함이다 (구멍을 놓치지 않되, 잘못 비우지 않는다)."""
    ps_end = PS_BASE + PS_STRIDE
    hits: list[tuple[int, int, int]] = []  # (byte_lo, byte_hi, va) va for provenance only
    for addr, insn in insns.items():
        for op in insn.operands:
            if op.type != X86_OP_MEM:
                continue
            disp = op.mem.disp
            size = operand_byte_size(op)
            # base+disp 형태: disp 자체가 PlayerStruct 필드 오프셋일 가능성 -- disp in [0, PS_STRIDE)
            if 0 <= disp < PS_STRIDE:
                hits.append((disp, disp + size, addr))
            # 절대주소 형태: disp 가 PlayerStruct[0] 안의 절대 VA
            unsigned = disp & 0xFFFFFFFF
            if PS_BASE <= unsigned < ps_end:
                off = unsigned - PS_BASE
                hits.append((off, off + size, addr))
    return hits


def find_holes(ranges: list[tuple[int, int, int]], span: int, min_len: int) -> list[dict]:
    touched = bytearray(span)
    for lo, hi, _addr in ranges:
        lo = max(0, lo)
        hi = min(span, hi)
        for i in range(lo, hi):
            touched[i] = 1
    holes = []
    i = 0
    while i < span:
        if touched[i]:
            i += 1
            continue
        j = i
        while j < span and not touched[j]:
            j += 1
        if j - i >= min_len:
            holes.append({"start": f"0x{i:04x}", "end": f"0x{j:04x}", "length": j - i})
        i = j
    return holes


def verify_card_sites(data: bytes) -> dict:
    out = {}
    for va, expected_hex in CARD_SITES + CARD_COST_LOAD_SITES:
        off = va - IMAGE_BASE
        expected = bytes.fromhex(expected_hex.replace(" ", ""))
        actual = data[off : off + len(expected)]
        out[f"0x{va:08x}"] = {
            "expected": expected_hex,
            "actual": actual.hex(" "),
            "match": actual == expected,
        }
    return out


def main() -> int:
    data = read_original()
    text_va, text_off, text_size = text_section(data)
    insns = sweep(data[text_off : text_off + text_size], text_va)

    site_check = verify_card_sites(data)
    site_mismatches = [va for va, v in site_check.items() if not v["match"]]

    ranges = touched_ranges(insns)
    holes = find_holes(ranges, PS_STRIDE, min_len=4)

    # 알려진 필드 블록(0x200a~0x2014, 2바이트씩 연속)과 겹치는 구멍은 애초에 없어야 한다 -- 자기검산.
    known_block_start, known_block_end = 0x200A, 0x2014
    holes_overlapping_known_block = [
        h for h in holes
        if int(h["start"], 16) < known_block_end and int(h["end"], 16) > known_block_start
    ]

    report = {
        "source": {
            "sha256": ORIGINAL_SHA256, "size": len(data),
            "text_va": f"0x{text_va:08x}", "text_size": text_size,
            "decoded_instructions": len(insns),
        },
        "player_struct": {"base": f"0x{PS_BASE:08x}", "stride": f"0x{PS_STRIDE:04x}", "count": PS_COUNT},
        "card_site_check": site_check,
        "card_site_mismatches": site_mismatches,
        "hole_candidates_min4B": holes,
        "hole_candidates_min4B_count": len(holes),
        "holes_overlapping_known_field_block_200a_2014": holes_overlapping_known_block,
        "touched_range_count": len(ranges),
    }

    print(json.dumps(report, indent=2, ensure_ascii=False))

    checks = {
        "M-b_all_9_card_sites_match": len(site_mismatches) == 0,
        "no_hole_overlaps_known_field_block": len(holes_overlapping_known_block) == 0,
        "at_least_one_4byte_hole_found": len(holes) >= 1,
    }
    failed = [name for name, ok in checks.items() if not ok]
    result = {"checks": checks, "failed": failed}
    (pathlib.Path(__file__).resolve().parents[0]).parent  # no-op, keep path use minimal
    print(json.dumps(result, indent=2, ensure_ascii=False), file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
