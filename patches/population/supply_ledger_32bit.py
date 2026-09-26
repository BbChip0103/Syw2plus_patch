#!/usr/bin/env python3
"""F4(B) 전비 장부 `used`(원본 +0x200c, 16-bit) 를 32-bit 로 확장.

카드: docs/work/active/G2_F4B_SUPPLY_LEDGER_32BIT_LAP509.md (W30) §8 안 B.
근거: analysis/memory_maps/g2_supply_ledger_200c_site_inventory_lap509_20260923.md,
      analysis/memory_maps/g2_supply_ledger_hole_rejection_lap511_20260923.md
      (lap511 middle 이 안 A `+0x2100` 을 REJECT -- 실제로는 `+0x2018` 용량 1,000칸
      dword 리스트의 58번 칸이었다).

안 B 채택: `used`(+0x200c) 는 **제자리에서** 4바이트로 확장한다(disp 불변, opcode 만
word->dword). 이것이 덮는 `+0x200e` building_count(2B) 는 `+0x2016`(리스트 count 워드
`+0x2014` 와 dword 원소 배열 `+0x2018` 사이 2바이트 정렬 패딩, 정적 유일 접근자
`0x43F57F` 는 esi>=1 이라 비도달, lap510 원시 2,896 owner-표본 전부 0)으로 옮긴다.
stride `0x3ABC`/저장 span 길이는 불변이다(M-g) -- 이 패치는 15곳 모두 같은 길이로
치환하므로 다른 명령의 주소/점프 타깃은 전혀 바뀌지 않는다(재배치 fixup 불필요).

3 묶음, 총 15곳:
  - building_count 이사 4곳: disp `0x200e` -> `0x2016` (다른 바이트 불변, 길이 불변).
  - `used` 제자리 dword 9곳: opcode 만 word->dword, disp 불변(`0x200c`/`0x95877c` 별칭),
    1바이트 짧아지는 만큼 `nop` 1개로 길이 보존.
  - cost-load 2곳: `mov dx,...`(66 8b) -> `movzx edx,...`(0f b7), 동일 길이. writer 의
    `edx` 상위 16비트를 0으로 보장해야 뒤따르는 dword add/sub 가 쓰레기를 더하지 않는다.

원본은 읽기 전용. 새 복사본에만 패치하고 정확한 원복을 함께 제공한다(M-c).

구세이브 호환: `[0x200c,0x2010)` 은 구 blob 에서 `used(16)|building(16)<<16` 이므로,
로드 후 로스터 재계산 훅이 없으면 구 세이브의 `used`/`building_count` 는 쓰레기가 된다.
그 훅은 이 카드 범위 밖이다 -- 후보는 **신규 게임 전용**이며 구세이브 로드는 미지원이다.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

ORIGINAL_SHA256 = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"
IMAGE_BASE = 0x400000

PS_BASE = 0x956770
PS_STRIDE = 0x3ABC
PS_COUNT = 8

USED_OFFSET = 0x200C  # 원본 2B -> 이 패치로 제자리 4B(dword)가 된다. disp 는 안 바뀐다.
OLD_BUILDING_OFFSET = 0x200E  # 원본 building_count 자리(2B) -- USED_OFFSET 확장이 덮는다.
NEW_BUILDING_OFFSET = 0x2016  # count 워드(+0x2014)/dword 배열(+0x2018) 사이 정렬 패딩.
LIST_COUNT_OFFSET = 0x2014
LIST_ELEMENTS_OFFSET = 0x2018
LIST_CAPACITY = 1000  # `0x43F4C7 cmp ax,0x3e8` -- 원소 영역 [0x2018,0x2018+1000*4)=[0x2018,0x2FB8)

# (VA, old_bytes_hex, new_bytes_hex) -- 길이는 항상 old == new (짧아지는 만큼 0x90 nop로 채움).
EDITS: tuple[tuple[int, bytes, bytes], ...] = (
    # --- building_count 이사 4곳: disp 0x200e(`0e200000`) -> 0x2016(`16200000`), 길이 불변.
    (0x0043DB24, bytes.fromhex("0fbf8e0e200000"), bytes.fromhex("0fbf8e16200000")),
    (0x0043E204, bytes.fromhex("6683bf0e20000005"), bytes.fromhex("6683bf1620000005")),
    (0x0043EEAD, bytes.fromhex("66ff810e200000"), bytes.fromhex("66ff8116200000")),
    (0x0043EF9D, bytes.fromhex("66ff890e200000"), bytes.fromhex("66ff8916200000")),
    # --- used 제자리 dword 9곳: opcode word->dword, disp 불변, 1B 남는 만큼 nop.
    # base+disp 5곳: movsx r32, word[reg+0x200c] (7B) -> mov r32, dword[reg+0x200c] (6B)+nop
    (0x0043EDFC, bytes.fromhex("0fbf910c200000"), bytes.fromhex("8b910c20000090")),
    (0x0043F0E9, bytes.fromhex("0fbf860c200000"), bytes.fromhex("8b860c20000090")),
    (0x0043F3B3, bytes.fromhex("0fbf850c200000"), bytes.fromhex("8b850c20000090")),
    # writer(+) 0x43EE9B: add word[ecx+0x200c],dx (7B) -> add dword[ecx+0x200c],edx (6B)+nop
    (0x0043EE9B, bytes.fromhex("6601910c200000"), bytes.fromhex("01910c20000090")),
    # writer(-) 0x43EF8B: sub word[ecx+0x200c],dx (7B) -> sub dword[ecx+0x200c],edx (6B)+nop
    (0x0043EF8B, bytes.fromhex("6629910c200000"), bytes.fromhex("29910c20000090")),
    # 절대주소 별칭 4곳: movsx r32, word[eax+0x95877c] (7B) -> mov r32, dword[eax+0x95877c] (6B)+nop
    (0x0040DD12, bytes.fromhex("0fbf907c879500"), bytes.fromhex("8b907c87950090")),
    (0x0040E03B, bytes.fromhex("0fbf907c879500"), bytes.fromhex("8b907c87950090")),
    (0x00499767, bytes.fromhex("0fbf887c879500"), bytes.fromhex("8b887c87950090")),
    (0x00499A0E, bytes.fromhex("0fbf887c879500"), bytes.fromhex("8b887c87950090")),
    # --- writer 직전 cost-load 2곳: mov dx, word[edx*4+0x9b5238] (8B, 66 8b)
    #     -> movzx edx, word[edx*4+0x9b5238] (8B, 0f b7) -- edx 상위 16bit를 0으로 보장해야
    #     뒤따르는 dword add/sub 가 쓰레기 상위비트를 더하지 않는다(카드 §6 마지막 행).
    (0x0043EE93, bytes.fromhex("668b149538529b00"), bytes.fromhex("0fb7149538529b00")),
    (0x0043EF83, bytes.fromhex("668b149538529b00"), bytes.fromhex("0fb7149538529b00")),
)

assert all(len(before) == len(after) for _va, before, after in EDITS)
assert len(EDITS) == 15


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def patched_bytes(original: bytes) -> bytes:
    if digest(original) != ORIGINAL_SHA256:
        raise ValueError("Unsupported original EXE SHA256")
    result = bytearray(original)
    for va, before, after in EDITS:
        offset = va - IMAGE_BASE
        if result[offset : offset + len(before)] != before:
            raise ValueError(f"Unexpected instruction bytes at 0x{va:08x}")
        if len(before) != len(after):
            raise ValueError(f"Edit at 0x{va:08x} changes length")
        result[offset : offset + len(after)] = after
    return bytes(result)


def create_copy(source: Path, destination: Path) -> str:
    if source.resolve() == destination.resolve():
        raise ValueError("Refusing to modify the input EXE")
    original = source.read_bytes()
    patched = patched_bytes(original)
    backup = Path(str(destination) + ".original")
    with backup.open("xb") as stream:
        stream.write(original)
    try:
        with destination.open("xb") as stream:
            stream.write(patched)
    except BaseException:
        backup.unlink()
        raise
    return digest(patched)


def restore(destination: Path) -> str:
    backup = Path(str(destination) + ".original")
    original = backup.read_bytes()
    expected = patched_bytes(original)
    if destination.read_bytes() != expected:
        raise ValueError("Refusing restore: destination is not the exact experimental patch")
    destination.write_bytes(original)
    return digest(original)


def used_va(owner: int) -> int:
    if not 0 <= owner < PS_COUNT:
        raise ValueError("owner must be 0..7")
    return PS_BASE + owner * PS_STRIDE + USED_OFFSET


def building_va(owner: int) -> int:
    if not 0 <= owner < PS_COUNT:
        raise ValueError("owner must be 0..7")
    return PS_BASE + owner * PS_STRIDE + NEW_BUILDING_OFFSET


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create-copy")
    create.add_argument("source", type=Path)
    create.add_argument("destination", type=Path)
    undo = commands.add_parser("restore")
    undo.add_argument("destination", type=Path)
    args = parser.parse_args()
    print(
        create_copy(args.source, args.destination)
        if args.command == "create-copy"
        else restore(args.destination)
    )


if __name__ == "__main__":
    main()
