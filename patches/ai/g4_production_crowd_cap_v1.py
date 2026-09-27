#!/usr/bin/env python3
"""G4 free-for-all AI production candidate v1 — raise the H-CROWD density cap.

STATUS 2026-09-27 13:05 운영자 판정("AI 자원 소비(생산 결정) 개선: 원본 AI 생산 결정
루틴에서 생산을 막는 조건... 상수 1~2개를 바꾼 후보 v1")에 대한 최소 구현이다. 근거는
`analysis/memory_maps/ai_production_decision_path_00406770_20260923.md` §3 G-7(H-CROWD).

lap712 baseline: owner1(nation2)이 owner0(nation1)보다 자원을 훨씬 덜 쓰며 쌓는다
(income_per_min owner1 +1734 대 owner0 -1119, production_count_proxy 12 대 21,
army_unit_count 10 대 16). §1 문서는 AI 생산 결정 경로(`FUN_00406770`→`FUN_00406B00`→
`FUN_0043E7F0`)에 자원 게이트가 하나도 없고, 대신 영구화 가능한 게이트 셋 중 하나가
**H-CROWD**(생산 건물 중심 11×11=121칸 안에 같은 kind·같은 owner 유닛이 7기 이상이면
그 kind 발주를 하지 않음, `FUN_00406B00` @ `0x406c44`)임을 원본 바이트로 확정했다.
H-TYPEMAX/H-RATIO(§4 `FUN_0043E7F0`)는 런타임/Data 파일에서만 채워지는 표를 참조해
EXE 정적 바이트로 값이 없다(문서 §5 "파일에 초기값이 없다") — 정적으로 상수를 바꿀 수
있는 유일한 생산 억제 게이트가 H-CROWD다.

이 후보는 `cmp word ptr [esp+0x10], 7`(밀집 계수 임계값)의 즉치값 하나만 `7`→`14`로
올린다 — 생산 건물 근처에 쌓일 수 있는 동종 유닛 수 상한을 두 배로 늘려, 밀집도 게이트가
너무 일찍 발주를 막는 owner(가설: owner1류)가 더 오래/더 많이 생산을 계속하게 한다.
다른 게이트(G-1~G-6, G-8)와 다른 kind/owner 조합, 다른 명령 경로는 바이트를 공유하지
않는다(§3, 유일 호출자 `FUN_00406B00`).

품질 개선 여부는 이 모듈이 아니라 `tools/g4_ai_behavior_probe.py`의 원본 대 후보
paired 실행(같은 `_custom_game_chain_inject_seed1` fixture)이 raw로 확인한다:
지표 = owner1 `resource_stock`(쌓인 자원, ↓ 기대) · `production_count_proxy`(↑ 기대) ·
`army_unit_count`(↑ 기대) · crash 0. `idle_worker_count`는 보조 지표로만 기록한다.
"""

from __future__ import annotations
import argparse
import hashlib
from pathlib import Path

ORIGINAL_SHA256 = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"
# Exact-hash profile: file offset = VA - 0x400000 (.text rawptr == vaddr == 0x1000).
EDITS = (
    # FUN_00406B00 G-7 H-CROWD: `cmp word ptr [esp+0x10],7` -> `,14` (density cap 7 -> 14).
    (0x6C44, bytes.fromhex("66837c241007"), bytes.fromhex("66837c24100e")),
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
