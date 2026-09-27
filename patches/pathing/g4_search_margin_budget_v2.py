#!/usr/bin/env python3
"""G4-P1 real pathfinder bounding-box margin candidate v2. Never patch the input.

STATUS 2026-09-27 lap708 handoff("§3이 미조사로 남긴 FUN_0041AF90 ... 정적으로 이어서
특정하고 그 마진/탐색 본체 상수로 후보 v2를 만들어 같은 obstacle_row paired 절차로
재측정한다")에 대한 최소 구현이다. 근거는
`analysis/memory_maps/g4_move_order_local_step_retry_20260927.md` §7(lap709 추가).

이번 lap709 정적 조사로 `FUN_0041AF90`(로컬 nudge가 실패했을 때 §2 `FUN_0040B810`이
호출하는 "진짜" 경로 스텝 진입점, `.text` 전수 xref 유일 호출자 `0x40b95d`)의 내부를
끝까지 따라갔다:

- `FUN_0041AF90`은 전역 per-tick 스로틀(`0x892FF8` vs `0x1770`=6000)을 통과하면 시작/목표
  좌표를 각각 **`±0x1E`(30타일) 마진**으로 클램프(맵 경계로 추가 클램프)한 bounding box를
  만들어 전역 싱글턴 경로탐색 엔진 객체(`ds:0xb92cbc`, 생성자 `FUN_0041AE70(this,200,200)`
  at `0x424ca6`)의 vtable 두 번째 슬롯(`[eax+4]`, vtable 베이스 `0x4e57e0`, 엔트리[1]=
  `0x46b840`)을 직접 호출한다(정적 확인: `.rdata` 파일 오프셋 `0xe57e4`의 raw DWORD가
  `0x46b840`).
- `FUN_0046B840`은 실제 그리드 탐색 본체다: per-search 스텝 카운터(엔진 객체 필드
  `+0x3c`, 루프 진입마다 재초기화·증가)가 있고, 8방향(모드 인자 `0x8`, 대안 `0x4`=4방향)
  이웃 확장 헬퍼 `FUN_0046BBF0`을 최대 8회 호출하는 open-list 기반 탐색 루프(`0x46b912`
  ~`0x46bac6`)를 돈다. 이 함수 자체는 이번 조사 범위 밖 유지(471+줄, 우선순위
  큐/실수 비교/좌표 델타가 컴파일러 재적재 패턴으로 얽혀 있어 스택 슬롯 하나를
  "스텝 예산 상수"로 단정하기엔 이번 lap의 정적 근거가 불충분 — 과다 확신 금지, §7에
  한계로 명시).
- 반대로 **마진 `0x1E`(30타일)는 4개의 정확한 바이트 위치**(아래 EDITS)로 완전히 확정됐고,
  독립 두 좌표(x/y) 클램프에 각각 대칭으로 쓰이며 다른 코드 경로와 바이트를 공유하지 않는다
  (`FUN_0041AF90` 유일 호출자 확인, §7). 이번 v2는 여기만 60타일(0x3C)로 두 배 넓혀
  bounding box를 121x121타일로 키운다 — obstacle_row(8타일 폭)에는 이미 30타일 마진도
  충분히 넓어 보여 개선이 없을 수 있다는 반대 가설도 §7에 명시(실패 시 예상된 결과).

이 상수는 시작/목표 좌표 클램프 전용이며(§7), `Unit+0x680`/`0x682`(로컬 nudge, v1이 이미
건드림) 및 8/4-방향 모드 플래그와는 바이트를 공유하지 않는다. 품질 개선 여부는 이 모듈이
아니라 `tools/g4_path_baseline_probe.py --variant candidate_v2`의 원본 대 후보 paired
실행이 raw로 확인한다.
"""

from __future__ import annotations
import argparse
import hashlib
from pathlib import Path

ORIGINAL_SHA256 = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"
# Exact-hash profile: file offset = VA - 0x400000 (.text rawptr == vaddr == 0x1000).
EDITS = (
    # FUN_0041AF90: min-x clamp `lea esi,[eax-0x1e]` -> `[eax-0x3c]` (disp8 -30 -> -60).
    (0x1AFC1, bytes.fromhex("8d70e2"), bytes.fromhex("8d70c4")),
    # FUN_0041AF90: max-x clamp `add eax,0x1e` -> `add eax,0x3c` (+30 -> +60).
    (0x1AFCB, bytes.fromhex("83c01e"), bytes.fromhex("83c03c")),
    # FUN_0041AF90: min-y clamp `lea esi,[eax-0x1e]` -> `[eax-0x3c]` (disp8 -30 -> -60).
    (0x1AFED, bytes.fromhex("8d70e2"), bytes.fromhex("8d70c4")),
    # FUN_0041AF90: max-y clamp `add eax,0x1e` -> `add eax,0x3c` (+30 -> +60).
    (0x1AFF6, bytes.fromhex("83c01e"), bytes.fromhex("83c03c")),
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
