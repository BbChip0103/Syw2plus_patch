#!/usr/bin/env python3
"""Compose the protected-original G2 candidate: 4092-slot pool + owner500 + supply10000.

2026-09-27 00:05 운영자 판정(lap694 승격 해소, strategy 대행): lap694가 실측한 전역
1200-슬롯 풀 병목은 (a) 더 비싼 gate-legal 타입 재탐색이 아니라 (b) 전역 풀 확장으로
해소한다. 이미 실전 검증된 ESL 계열 4092-슬롯/개인500 풀 재배치
(`g2_esl2606_pool4092_owner500.py`/`g2_esl2608_pool4092_owner500.py`)를 그 기술 그대로
**보호 원본(b56986e0) 기준**에 적용한다. ESL 모듈과 달리 이 체인은 별도 ESL 참조
바이너리와 diff할 필요가 없다 -- `g2_full_capacity_persistence_compat_v1.build_candidate`가
이미 보호 원본 위에서 직접 풀 재배치(구조체 6개 영역 tail relocation, save/load 호환
헤더 포함)를 만든다. 이 모듈은 그 체인 출력 위에 세 가지만 겹쳐 적용한다:

1. 전비 상한 5000 -> 10000 (`fixed_supply_10000`과 동일한 두 자리, 같은 명령 형태).
2. 개인 로스터 상한 1200 -> 500 (`fixed_owner_count_1200`과 같은 자리; 8*500=4000<=4092
   유지, ESL 500-owner 변형과 동일 정책).
3. 유휴 영웅 초상화 producer 탐색 상한 1200 -> 4093
   (`g2_esl2606_pool4092_owner500.PRODUCER_LOOKUP_EDITS`와 정확히 같은 3개 명령 자리;
   이 코드는 ESL 델타와 무관한 보호 원본 .text 그대로이므로 그대로 재사용 가능하다).

Evidence: docs/history/laps/20260926_lap694_work_g2_supply10000_eight_owner_global_pool_bottleneck.md,
analysis/memory_maps/g2_esl2606_idle_portrait_producer_scan_20260925.md.
Hash-guarded at every stage; refuses to touch any byte outside these three edits plus
the underlying pool-relocation chain's own pinned edits. Never modifies the input EXE.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from typing import Any

from patches.population.fixed_owner_count_1200 import OWNER_COUNT_FILE_OFFSET
from patches.population.fixed_supply_5000 import EDITS as SUPPLY_5000_EDITS
from patches.population.fixed_supply_10000 import EDITS as SUPPLY_10000_EDITS
from patches.population.full_tail_relocation_storage_layout_v1 import ORIGINAL_SHA256
from patches.population.g2_esl2606_pool4092_owner500 import PRODUCER_LOOKUP_EDITS
from patches.population.g2_full_capacity_persistence_compat_v1 import (
    build_candidate as build_compat_candidate,
)

CAPACITY = 4093  # slot zero is reserved: 4092 usable slots (<= 4095, 12-bit command-safe)
USABLE_SLOTS = CAPACITY - 1
OWNER_COUNT_BEFORE_1200 = bytes.fromhex("b0040000")
OWNER_COUNT_AFTER_500 = bytes.fromhex("f4010000")
OWNER_COUNT_POLICY = 500


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _apply_supply_10000(out: bytearray) -> list[dict[str, str]]:
    applied = []
    for (offset, _before5000, after_5000), (offset10k, _before10k, after_10000) in zip(
        SUPPLY_5000_EDITS, SUPPLY_10000_EDITS
    ):
        if offset != offset10k:
            raise ValueError("supply-5000/10000 edit sites diverged")
        current = bytes(out[offset : offset + len(after_5000)])
        if current != after_5000:
            raise ValueError(f"supply-5000 preimage mismatch at 0x{offset:X}: {current.hex()}")
        out[offset : offset + len(after_10000)] = after_10000
        applied.append({"offset": f"0x{offset:X}", "before": after_5000.hex(), "after": after_10000.hex()})
    return applied


def _apply_owner_cap_500(out: bytearray) -> dict[str, str]:
    start = OWNER_COUNT_FILE_OFFSET
    end = start + len(OWNER_COUNT_BEFORE_1200)
    current = bytes(out[start:end])
    if current != OWNER_COUNT_BEFORE_1200:
        raise ValueError(f"owner-count-1200 preimage mismatch at 0x{start:X}: {current.hex()}")
    out[start:end] = OWNER_COUNT_AFTER_500
    return {"offset": f"0x{start:X}", "before": OWNER_COUNT_BEFORE_1200.hex(), "after": OWNER_COUNT_AFTER_500.hex()}


def _apply_producer_lookup_fixups(out: bytearray) -> dict[str, str]:
    patched: dict[str, str] = {}
    for va, old, new in PRODUCER_LOOKUP_EDITS:
        offset = va - 0x00400000
        current = bytes(out[offset : offset + len(old)])
        if current != old:
            raise ValueError(f"producer-lookup preimage mismatch at 0x{va:08x}: {current.hex()}")
        out[offset : offset + len(new)] = new
        patched[f"0x{va:08x}"] = new.hex()
    return patched


def build_candidate(original: bytes) -> tuple[bytes, dict[str, Any]]:
    if digest(original) != ORIGINAL_SHA256:
        raise ValueError("unsupported protected original EXE SHA256")
    compat_candidate, compat_report = build_compat_candidate(original, CAPACITY)
    out = bytearray(compat_candidate)
    supply_edits = _apply_supply_10000(out)
    owner_edit = _apply_owner_cap_500(out)
    producer_lookup = _apply_producer_lookup_fixups(out)
    candidate = bytes(out)
    return candidate, {
        "capacity_slots": CAPACITY,
        "usable_slots": USABLE_SLOTS,
        "owner_count_cap": OWNER_COUNT_POLICY,
        "supply_cap": 10000,
        "supply_edits": supply_edits,
        "owner_count_edit": owner_edit,
        "producer_lookup_edits": producer_lookup,
        "candidate_sha256": digest(candidate),
        "compat_report": compat_report,
    }


def create_copy(source: Path, destination: Path) -> dict[str, Any]:
    if source.resolve() == destination.resolve():
        raise ValueError("refusing to modify the input EXE")
    original = source.read_bytes()
    candidate, report = build_candidate(original)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb") as stream:
        stream.write(candidate)
    if digest(destination.read_bytes()) != report["candidate_sha256"]:
        raise ValueError("candidate write verification failed")
    return report


def restore_copy(destination: Path, source: Path) -> str:
    original = source.read_bytes()
    candidate, _report = build_candidate(original)
    if destination.read_bytes() != candidate:
        raise ValueError("refusing restore: destination is not this exact candidate")
    temporary = Path(str(destination) + ".restore.tmp")
    with temporary.open("xb") as stream:
        stream.write(original)
    temporary.replace(destination)
    return digest(original)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("create-copy")
    create.add_argument("source", type=Path)
    create.add_argument("destination", type=Path)
    restore = sub.add_parser("restore")
    restore.add_argument("destination", type=Path)
    restore.add_argument("source", type=Path)
    args = parser.parse_args()
    if args.command == "create-copy":
        print(create_copy(args.source, args.destination))
    else:
        print(restore_copy(args.destination, args.source))


if __name__ == "__main__":
    main()
