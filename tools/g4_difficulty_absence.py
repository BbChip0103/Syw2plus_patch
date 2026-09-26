#!/usr/bin/env python3
"""Verify that original free battle has no AI difficulty selector."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from pathlib import Path
from typing import Any

EXPECTED_EXE_SHA256 = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"
TEXT_NAMES = ("Text_kor.dat", "TexJ_kor.dat", "TexR_kor.dat", "TeJM_kor.dat")
REQUIRED_LABELS = (
    "전장지도", "자동생성", "많은 자원", "큰 지도", "복잡 지형", "기본 배경",
    "보통 게임", "깃발뺏기", "시간제한", "느리게", "보통", "빠르게",
)
FORBIDDEN_LABELS = ("난이도", "쉬움", "어려움")
LOBBY_WORD_TARGETS = [
    0x00632D54, 0x00632D46, 0x00632D44, 0x00632D4A,
    0x00632D48, 0x00632D4C, 0x00632D42,
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _va_to_offset(image: bytes, va: int) -> int:
    pe = struct.unpack_from("<I", image, 0x3C)[0]
    section_count = struct.unpack_from("<H", image, pe + 6)[0]
    optional_size = struct.unpack_from("<H", image, pe + 20)[0]
    image_base = struct.unpack_from("<I", image, pe + 24 + 28)[0]
    rva = va - image_base
    section = pe + 24 + optional_size
    for index in range(section_count):
        entry = section + index * 40
        virtual_size, virtual_address, raw_size, raw_offset = struct.unpack_from(
            "<IIII", image, entry + 8
        )
        if virtual_address <= rva < virtual_address + max(virtual_size, raw_size):
            return raw_offset + rva - virtual_address
    raise ValueError(f"VA not mapped: {va:#x}")


def _slice(image: bytes, start_va: int, end_va: int) -> bytes:
    start = _va_to_offset(image, start_va)
    return image[start : start + end_va - start_va]


def build_report(exe: Path, texts: tuple[Path, ...]) -> dict[str, Any]:
    image = exe.read_bytes()
    speed = _slice(image, 0x004165C0, 0x00416622)
    lobby = _slice(image, 0x004B763C, 0x004B76AE)
    speed_globals = (0x00975B2C, 0x00B93960, 0x00B93964, 0x006695A4, 0x004ED80C)
    speed_pass = (
        all(struct.pack("<I", address) in speed for address in speed_globals)
        and b"\xB8\x3C\x00\x00\x00\xC3" in speed
        and b"\xFF\x24\x85\x24\x66\x41\x00" in speed
    )
    word_targets = [
        struct.unpack("<I", match)[0]
        for match in re.findall(rb"\x66\xA3(.{4})", lobby, flags=re.DOTALL)
    ]
    lobby_pass = (
        word_targets == LOBBY_WORD_TARGETS
        and b"\x89\x15" + struct.pack("<I", 0x00632D38) in lobby
    )
    registries: list[dict[str, Any]] = []
    for path in texts:
        text = path.read_bytes().decode("cp949")
        missing = [label for label in REQUIRED_LABELS if label not in text]
        forbidden = [label for label in FORBIDDEN_LABELS if label in text]
        registries.append({
            "path": str(path), "sha256": _sha256(path),
            "missing_required": missing, "forbidden_present": forbidden,
            "pass": not missing and not forbidden,
        })
    exe_sha = _sha256(exe)
    passed = (
        exe_sha == EXPECTED_EXE_SHA256 and speed_pass and lobby_pass
        and len(registries) == 4 and all(item["pass"] for item in registries)
    )
    return {
        "schema": "syw2plus.g4.free_battle_difficulty_absence.v1",
        "classification": "NO_FREE_BATTLE_DIFFICULTY_SELECTOR" if passed else "EVIDENCE_INVALID",
        "activation_allowed": False,
        "exe": {"path": str(exe), "sha256": exe_sha, "pinned": exe_sha == EXPECTED_EXE_SHA256},
        "game_speed_function": {"va": "0x004165C0", "pass": speed_pass},
        "lobby_commit": {
            "va_range": ["0x004B763C", "0x004B76AE"],
            "word_targets": [f"0x{address:08X}" for address in word_targets],
            "pass": lobby_pass,
        },
        "registries": registries,
        "conclusion": (
            "Original free battle has game-speed and seven lobby settings, but no AI difficulty field. "
            "Do not invent or search for an Easy/Normal/Hard runtime value."
        ),
    }


def main(argv: list[str] | None = None) -> int:
    root = Path(__file__).resolve().parents[1]
    default_game = root.parent / "Syw2plus_re" / "Syw2plus"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-root", type=Path, default=default_game)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    report = build_report(
        args.game_root / "syw2plus_original.exe",
        tuple(args.game_root / name for name in TEXT_NAMES),
    )
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if report["classification"] == "NO_FREE_BATTLE_DIFFICULTY_SELECTOR" else 2


if __name__ == "__main__":
    raise SystemExit(main())
