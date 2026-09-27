#!/usr/bin/env python3
"""G4-P1 move-order local-step detour budget candidate v1. Never patch the input.

STATUS 2026-09-27 08:55 지시("상수 1~2개(예: 탐색 예산/우회 한도 상향)를 바꾼 후보 v1을
빌드")에 대한 최소 구현이다. 근거는
`analysis/memory_maps/g4_move_order_local_step_retry_20260927.md`.

원본 `FUN_0040C390`(파일 오프셋 `0xC390`)은 이동 상태(`Unit+0x290==3`) per-tick 핸들러의
유일 진입점이며(`.text` 전수 xref로 호출자 1곳만 확인, `0x48E706`), 여기서
`push 0x4; call 0x40B7E0`로 넘기는 상수 `4`가 `FUN_0040B810`(지상 이동 스텝) 내부에서
로컬 4방향 nudge 재시도 최대 횟수(`Unit+0x682` vs 이 인자)로 재사용된다. 이 모듈은 그 한
바이트만 `4`(0x04) -> `8`(0x08)로 올려, 장애물 앞에서 로컬 회피를 더 시도한 뒤에야
`FUN_0040B740`(원거리 목표로 리셋)로 넘어가게 한다.

이 상수는 `0x40B7E0`을 부르는 다른 29개 호출자(다른 mode 값, 전투/애니메이션 등)와 바이트를
공유하지 않는다(정적 xref로 유일 호출자 확인) -- 영향 범위는 플레이어/AI가 발행한 MOVE 주문의
로컬 회피 재시도 횟수뿐이다. 공격 상태(`Unit+0x290==4`)나 다른 상태 핸들러, 선택/부대/저장
경로는 이 바이트와 무관하다.

이 패치는 "우회 한도"만 올린다. `Unit+0x680` 쿨다운 리셋 상수(5)와 `FUN_0041AF90`의
bounding-box 마진(0x1E)은 건드리지 않는다(분석 문서 §4, 블라스트 반경/미조사 범위 이유).
품질 개선 여부는 이 모듈이 아니라 `tools/g4_path_baseline_probe.py`의 원본 대 후보 paired
실행이 raw로 확인한다.
"""

from __future__ import annotations
import argparse
import hashlib
from pathlib import Path

ORIGINAL_SHA256 = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"
# Exact-hash profile: file offset = VA - 0x400000 (.text rawptr == vaddr == 0x1000).
EDITS = (
    # FUN_0040C390: `push 0x4` -> `push 0x8` feeding FUN_0040B810's local-step
    # retry-count threshold (Unit+0x682 vs this value) for MOVE-order ticks.
    (0xC395, bytes.fromhex("6a04"), bytes.fromhex("6a08")),
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
