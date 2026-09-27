#!/usr/bin/env python3
"""Hash-guarded fixed-10000 supply cap. Create a new EXE copy; never patch the input.

2026-09-26 사용자 판단: G2 전비5000 단계는 달성으로 보고, 새 목표는 활성8인 각각
전비10000이다(docs/DESIGN.md G2). 이 모듈은 `fixed_supply_5000.py`와 정확히 같은
두 사이트에서 같은 명령 형태를 유지한 채 상수만 5000(0x1388)에서 10000(0x2710)으로
바꾼다. `+0x2012`(전비 상한)와 `+0x200c`(전비 사용)는 16-bit 필드이므로(analysis/
memory_maps/g2_capacity_boundaries.md) 10000은 65535 범위 안이며 이 두 자리 패치만으로
필드 자체의 폭 확장은 필요 없다.

이 패치는 전비 "상한" 값만 바꾼다. 원본 개인 개체 상한(+0x2010, 시작값250)과
전역 공유 슬롯(1200)은 바뀌지 않는다 -- 코스트35 유닛 250기의 합계는 8750으로
10000에 못 미치므로, 전비10000 도달 실측에는 더 비싼 유닛 구성 또는 개인 개체
상한 조정이 별도로 필요하다(docs/DESIGN.md G2, "전비는 개체 수가 아니다"). 이 모듈은
그 자체 수치 병목을 해소하지 않으며, 다음 회차가 실제 8인 fixture로 측정한다.

Evidence: analysis/memory_maps/population_5000_runtime_0910.md (5000 사이트 근거),
analysis/memory_maps/g2_supply10000_cap_bump_20260926.md (이 패치의 10000 파생 근거).
Restore only accepts our exact patched bytes and exact original backup.
"""

from __future__ import annotations
import argparse
import hashlib
from pathlib import Path

ORIGINAL_SHA256 = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"
# Exact-hash profile: these .text file offsets are VA - 0x400000.
# Same instruction bytes/lengths as fixed_supply_5000.py; only the trailing
# 16-bit/32-bit immediate differs (0x1388=5000 -> 0x2710=10000).
EDITS = (
    (0x1B576, bytes.fromhex("66c700dc05"), bytes.fromhex("66c7001027")),
    (0x3FFD4, bytes.fromhex("05dc050000"), bytes.fromhex("b810270000")),
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def patched_bytes(original: bytes) -> bytes:
    if digest(original) != ORIGINAL_SHA256:
        raise ValueError("Unsupported original EXE SHA256")
    result = bytearray(original)
    for offset, before, after in EDITS:
        if result[offset : offset + len(before)] != before or len(before) != len(after):
            raise ValueError("Unexpected instruction bytes/length")
        result[offset : offset + len(before)] = after
    return bytes(result)


def create_copy(source: Path, destination: Path) -> str:
    if source.resolve() == destination.resolve():
        raise ValueError("Refusing to modify the input EXE")
    original = source.read_bytes()
    patched = patched_bytes(original)
    backup = Path(str(destination) + ".original")
    # Exclusive creation prevents overwriting any existing game or backup.
    with backup.open("xb") as stream:
        stream.write(original)
    try:
        with destination.open("xb") as stream:
            stream.write(patched)
    except BaseException:
        backup.unlink()  # Only the new backup created by this invocation.
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
