#!/usr/bin/env python3
"""Offline-only PE32 storage candidate builder.

This module never patches the source image in place and never launches Wine/game
code.  It creates a private, explicitly incomplete 4001-slot storage section.
The 120 accessor records are frozen from the approved relocation include; no
runtime C/include parsing is performed.
"""

from __future__ import annotations
import argparse
import hashlib
import struct
from dataclasses import dataclass
from pathlib import Path

try:
    from patches.population.fixed_supply_5000 import (
        EDITS as FIXED_SUPPLY_EDITS,
        patched_bytes as fixed_supply_patched_bytes,
    )
except ModuleNotFoundError:  # direct absolute-path CLI invocation
    import importlib.util

    _fixed_spec = importlib.util.spec_from_file_location(
        "fixed_supply_5000", Path(__file__).with_name("fixed_supply_5000.py")
    )
    if _fixed_spec is None or _fixed_spec.loader is None:
        raise ImportError("fixed_supply_5000 utility is unavailable")
    _fixed_module = importlib.util.module_from_spec(_fixed_spec)
    _fixed_spec.loader.exec_module(_fixed_module)
    FIXED_SUPPLY_EDITS = _fixed_module.EDITS
    fixed_supply_patched_bytes = _fixed_module.patched_bytes

ORIGINAL_SHA256 = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"
PATCH_SOURCE_SHA256 = "e13195a4a88a35b944dc48dff3b8b584d8402dff9e33dfe3f6adb275edce5ace"
RECIPE_SHA256 = "0e5527ec1561d123b34fdc615bfa235f49a5348e1a14fbf35db6b836536c3ced"
CREATION_RECIPE_SHA256 = "0694c732b488fba4fba3e4fbbceede4b36692db71290cac67434946e1d707994"
OWNER_LIFECYCLE_RECIPE_SHA256 = "c334f04b329a550c981c307b4fa86511928a6f4686ee52c56d9712723e79afa3"
IMAGE_BASE = 0x400000
SECTION_NAME = b".g2stg"
CAPACITY = 4001
UNIT_SIZE = 0x758
ALLOCATOR_FILE_OFFSET = 0x42FA0
ALLOCATOR_VA = 0x00442FA0
ALLOCATOR_BYTES = bytes.fromhex(
    "53 56 57 33 db 33 c0 bf 01 00 00 00 b9 2a 9a 89 00 66 83 b9 a0 f6 ff ff 00 75 12 66 8b 31 0f bf d6 3b d3 7c 04 8b da 8b c7 46 66 89 31 83 c1 02 47 81 f9 88 a3 89 00 7c d8 5f 5e 5b c3"
)
INIT_CALL_VA = 0x0041B9C0
INIT_CALL_BYTES = bytes.fromhex("e8 9b 76 08 00")
ORIGINAL_INIT_VA = 0x004A3060
ORIGINAL_INIT_BYTES = bytes.fromhex("51 53 55 56 8b f1 57")
INIT_SOURCE_WORDS = {
    "sidecar_exists": 0x008990C8,
    "sidecar_age": 0x00899A28,
    "sidecar_active": 0x00974FA8,
}
INIT_SOURCE_DWORDS = {
    "sidecar_cata": 0x0089B008,
    "sidecar_catb": 0x0089C2CA,
}
INIT_SOURCE_COUNTERS = {
    "sidecar_active_count": 0x00975908,
    "sidecar_cata_count": 0x0089C2C8,
    "sidecar_catb_count": 0x0089D58A,
}
IMAGE_SCN_CNT_INITIALIZED_DATA = 0x00000040
IMAGE_SCN_MEM_READ = 0x40000000
IMAGE_SCN_MEM_WRITE = 0x80000000
IMAGE_SCN_MEM_EXECUTE = 0x20000000
IMAGE_SCN_CNT_CODE = 0x00000020


@dataclass(frozen=True)
class PatchRecord:
    va: int
    instruction_length: int
    operand_offset: int
    old_target: int
    region: str
    field_offset: int
    old_bytes: bytes

    @property
    def file_offset(self):
        return self.va - IMAGE_BASE


@dataclass(frozen=True)
class Section:
    name: bytes
    virtual_size: int
    virtual_address: int
    raw_size: int
    raw_pointer: int
    characteristics: int


@dataclass(frozen=True)
class PE:
    e_lfanew: int
    number_of_sections: int
    section_alignment: int
    file_alignment: int
    image_base: int
    size_of_image: int
    size_of_headers: int
    section_table: int
    sections: tuple[Section, ...]


@dataclass(frozen=True)
class StorageLayout:
    section_rva: int
    capacity: int
    unit_size: int
    unit_offset: int
    arena_offsets: dict[str, int]
    counter_offsets: dict[str, int]
    virtual_size: int


# Frozen from relocation_diag_patches.inc SHA above; 120 unique instruction records.
PATCHES = (
    PatchRecord(
        0x0043391A,
        7,
        3,
        0x00975908,
        "COUNTER_ACTIVE",
        0,
        bytes((0x66, 0x39, 0x1D, 0x08, 0x59, 0x97, 0x00)),
    ),
    PatchRecord(
        0x00433926,
        8,
        4,
        0x00974FA8,
        "ARENA_ACTIVE",
        0,
        bytes((0x0F, 0xBF, 0x0C, 0x45, 0xA8, 0x4F, 0x97, 0x00)),
    ),
    PatchRecord(
        0x0043392E,
        9,
        4,
        0x008990C8,
        "ARENA_EXISTS",
        0,
        bytes((0x66, 0x83, 0x3C, 0x4D, 0xC8, 0x90, 0x89, 0x00, 0x00)),
    ),
    PatchRecord(
        0x00433947,
        7,
        3,
        0x0066BA20,
        "ARENA_POOL",
        656,
        bytes((0x66, 0x8B, 0x88, 0x20, 0xBA, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0043395A, 6, 2, 0x0066B790, "ARENA_POOL", 0, bytes((0x8D, 0xB8, 0x90, 0xB7, 0x66, 0x00))
    ),
    PatchRecord(
        0x00433976,
        7,
        3,
        0x00975908,
        "COUNTER_ACTIVE",
        0,
        bytes((0x66, 0x3B, 0x1D, 0x08, 0x59, 0x97, 0x00)),
    ),
    PatchRecord(
        0x00433EC5,
        7,
        3,
        0x0089C2C8,
        "COUNTER_CATA",
        0,
        bytes((0x66, 0x39, 0x1D, 0xC8, 0xC2, 0x89, 0x00)),
    ),
    PatchRecord(
        0x00433ED1,
        8,
        4,
        0x0089B008,
        "ARENA_CATA",
        0,
        bytes((0x0F, 0xBF, 0x0C, 0x95, 0x08, 0xB0, 0x89, 0x00)),
    ),
    PatchRecord(
        0x00433ED9,
        9,
        4,
        0x008990C8,
        "ARENA_EXISTS",
        0,
        bytes((0x66, 0x83, 0x3C, 0x4D, 0xC8, 0x90, 0x89, 0x00, 0x00)),
    ),
    PatchRecord(
        0x00433EEF,
        7,
        3,
        0x0066B790,
        "ARENA_POOL",
        0,
        bytes((0x8D, 0x3C, 0xC5, 0x90, 0xB7, 0x66, 0x00)),
    ),
    PatchRecord(
        0x00433F0C,
        7,
        3,
        0x0089C2C8,
        "COUNTER_CATA",
        0,
        bytes((0x66, 0x3B, 0x1D, 0xC8, 0xC2, 0x89, 0x00)),
    ),
    PatchRecord(
        0x00416FD4,
        9,
        4,
        0x008990C8,
        "ARENA_EXISTS",
        0,
        bytes((0x66, 0x83, 0x3C, 0x4D, 0xC8, 0x90, 0x89, 0x00, 0x00)),
    ),
    PatchRecord(
        0x00416FF0, 6, 2, 0x0066B844, "ARENA_POOL", 180, bytes((0x8B, 0x88, 0x44, 0xB8, 0x66, 0x00))
    ),
    PatchRecord(
        0x00416FFD, 6, 2, 0x0066BAAC, "ARENA_POOL", 796, bytes((0x8A, 0x90, 0xAC, 0xBA, 0x66, 0x00))
    ),
    PatchRecord(
        0x0047B7C1, 6, 2, 0x0066B81E, "ARENA_POOL", 142, bytes((0x8A, 0x8E, 0x1E, 0xB8, 0x66, 0x00))
    ),
    PatchRecord(
        0x0047B7D5, 6, 2, 0x0066B968, "ARENA_POOL", 472, bytes((0x8B, 0x86, 0x68, 0xB9, 0x66, 0x00))
    ),
    PatchRecord(
        0x0047B7EB, 6, 2, 0x0066B81D, "ARENA_POOL", 141, bytes((0x8A, 0x86, 0x1D, 0xB8, 0x66, 0x00))
    ),
    PatchRecord(
        0x0047B825, 6, 2, 0x0066B8FC, "ARENA_POOL", 364, bytes((0x8B, 0x86, 0xFC, 0xB8, 0x66, 0x00))
    ),
    PatchRecord(
        0x0047B835, 6, 2, 0x0066B8FC, "ARENA_POOL", 364, bytes((0x89, 0x96, 0xFC, 0xB8, 0x66, 0x00))
    ),
    PatchRecord(
        0x0047B83B, 6, 2, 0x0066B904, "ARENA_POOL", 372, bytes((0x89, 0x9E, 0x04, 0xB9, 0x66, 0x00))
    ),
    PatchRecord(
        0x0047B84F,
        10,
        2,
        0x0066B968,
        "ARENA_POOL",
        472,
        bytes((0xF7, 0x86, 0x68, 0xB9, 0x66, 0x00, 0x02, 0x00, 0x10, 0x00)),
    ),
    PatchRecord(
        0x0047B85D, 6, 2, 0x0066B81D, "ARENA_POOL", 141, bytes((0x8A, 0x86, 0x1D, 0xB8, 0x66, 0x00))
    ),
    PatchRecord(
        0x0047B886, 6, 2, 0x0066B918, "ARENA_POOL", 392, bytes((0x8B, 0x86, 0x18, 0xB9, 0x66, 0x00))
    ),
    PatchRecord(
        0x0047B89A, 6, 2, 0x0066B918, "ARENA_POOL", 392, bytes((0x89, 0x96, 0x18, 0xB9, 0x66, 0x00))
    ),
    PatchRecord(
        0x0047B8A0, 6, 2, 0x0066B91C, "ARENA_POOL", 396, bytes((0x89, 0x9E, 0x1C, 0xB9, 0x66, 0x00))
    ),
    PatchRecord(
        0x0047B8B1,
        10,
        2,
        0x0066B968,
        "ARENA_POOL",
        472,
        bytes((0xF7, 0x86, 0x68, 0xB9, 0x66, 0x00, 0x02, 0x00, 0x10, 0x00)),
    ),
    PatchRecord(
        0x0047B8C1, 6, 2, 0x0066B974, "ARENA_POOL", 484, bytes((0x8B, 0x86, 0x74, 0xB9, 0x66, 0x00))
    ),
    PatchRecord(
        0x0047B8D7, 6, 2, 0x0066B81D, "ARENA_POOL", 141, bytes((0x8A, 0x86, 0x1D, 0xB8, 0x66, 0x00))
    ),
    PatchRecord(
        0x0047B919, 6, 2, 0x0066B81D, "ARENA_POOL", 141, bytes((0x8A, 0x86, 0x1D, 0xB8, 0x66, 0x00))
    ),
    PatchRecord(
        0x0047B944, 6, 2, 0x0066B8FC, "ARENA_POOL", 364, bytes((0x8B, 0x86, 0xFC, 0xB8, 0x66, 0x00))
    ),
    PatchRecord(
        0x0047B958, 6, 2, 0x0066B8FC, "ARENA_POOL", 364, bytes((0x89, 0xBE, 0xFC, 0xB8, 0x66, 0x00))
    ),
    PatchRecord(
        0x0047B95E, 6, 2, 0x0066B904, "ARENA_POOL", 372, bytes((0x89, 0x9E, 0x04, 0xB9, 0x66, 0x00))
    ),
    PatchRecord(
        0x0047B964, 6, 2, 0x0066B918, "ARENA_POOL", 392, bytes((0x39, 0x96, 0x18, 0xB9, 0x66, 0x00))
    ),
    PatchRecord(
        0x0047B96C, 6, 2, 0x0066B918, "ARENA_POOL", 392, bytes((0x89, 0x96, 0x18, 0xB9, 0x66, 0x00))
    ),
    PatchRecord(
        0x0047B972, 6, 2, 0x0066B91C, "ARENA_POOL", 396, bytes((0x89, 0x9E, 0x1C, 0xB9, 0x66, 0x00))
    ),
    PatchRecord(
        0x0047B983, 6, 2, 0x0066B968, "ARENA_POOL", 472, bytes((0x8B, 0x96, 0x68, 0xB9, 0x66, 0x00))
    ),
    PatchRecord(
        0x0047B9BC, 6, 2, 0x0066B844, "ARENA_POOL", 180, bytes((0x8B, 0x8E, 0x44, 0xB8, 0x66, 0x00))
    ),
    PatchRecord(
        0x0047B9C2, 6, 2, 0x0066B8B0, "ARENA_POOL", 288, bytes((0x8B, 0x86, 0xB0, 0xB8, 0x66, 0x00))
    ),
    PatchRecord(
        0x0047B9CE, 6, 2, 0x0066B790, "ARENA_POOL", 0, bytes((0x8D, 0x8E, 0x90, 0xB7, 0x66, 0x00))
    ),
    PatchRecord(
        0x0047B9DF, 6, 2, 0x0066B93C, "ARENA_POOL", 428, bytes((0x89, 0xBE, 0x3C, 0xB9, 0x66, 0x00))
    ),
    PatchRecord(
        0x0047B9E5, 6, 2, 0x0066B940, "ARENA_POOL", 432, bytes((0x89, 0x9E, 0x40, 0xB9, 0x66, 0x00))
    ),
    PatchRecord(
        0x0047B9F1,
        10,
        2,
        0x0066B968,
        "ARENA_POOL",
        472,
        bytes((0xF7, 0x86, 0x68, 0xB9, 0x66, 0x00, 0x02, 0x00, 0x10, 0x00)),
    ),
    PatchRecord(
        0x0047B9FD, 6, 2, 0x0066B930, "ARENA_POOL", 416, bytes((0x89, 0xBE, 0x30, 0xB9, 0x66, 0x00))
    ),
    PatchRecord(
        0x0047BA03, 6, 2, 0x0066B934, "ARENA_POOL", 420, bytes((0x89, 0x9E, 0x34, 0xB9, 0x66, 0x00))
    ),
    PatchRecord(
        0x0047BA0F,
        7,
        2,
        0x0066B968,
        "ARENA_POOL",
        472,
        bytes((0xF6, 0x86, 0x68, 0xB9, 0x66, 0x00, 0x02)),
    ),
    PatchRecord(
        0x0047BA18, 6, 2, 0x0066B9CC, "ARENA_POOL", 572, bytes((0x89, 0xBE, 0xCC, 0xB9, 0x66, 0x00))
    ),
    PatchRecord(
        0x0047BA1E, 6, 2, 0x0066B9D0, "ARENA_POOL", 576, bytes((0x89, 0x9E, 0xD0, 0xB9, 0x66, 0x00))
    ),
    PatchRecord(
        0x0040F550,
        7,
        3,
        0x0066BA2C,
        "ARENA_POOL",
        668,
        bytes((0x8B, 0x0C, 0xC5, 0x2C, 0xBA, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040F570,
        9,
        5,
        0x0066B81E,
        "ARENA_POOL",
        142,
        bytes((0x66, 0x0F, 0xBE, 0x04, 0xC5, 0x1E, 0xB8, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040F590,
        9,
        5,
        0x0066B81F,
        "ARENA_POOL",
        143,
        bytes((0x66, 0x0F, 0xBE, 0x04, 0xC5, 0x1F, 0xB8, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040F5B0,
        9,
        5,
        0x0066B81D,
        "ARENA_POOL",
        141,
        bytes((0x66, 0x0F, 0xB6, 0x04, 0xC5, 0x1D, 0xB8, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040F5D0,
        8,
        4,
        0x0066BA32,
        "ARENA_POOL",
        674,
        bytes((0x66, 0x8B, 0x04, 0xC5, 0x32, 0xBA, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040F5F0,
        8,
        4,
        0x0066BA34,
        "ARENA_POOL",
        676,
        bytes((0x66, 0x8B, 0x04, 0xC5, 0x34, 0xBA, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040F610,
        8,
        4,
        0x0066BA40,
        "ARENA_POOL",
        688,
        bytes((0x66, 0x8B, 0x04, 0xC5, 0x40, 0xBA, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040F630,
        8,
        4,
        0x0066BA42,
        "ARENA_POOL",
        690,
        bytes((0x66, 0x8B, 0x04, 0xC5, 0x42, 0xBA, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040F65A,
        7,
        3,
        0x0066B790,
        "ARENA_POOL",
        0,
        bytes((0x8D, 0x0C, 0xD5, 0x90, 0xB7, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040F684,
        7,
        3,
        0x0066B968,
        "ARENA_POOL",
        472,
        bytes((0x8B, 0x04, 0xC5, 0x68, 0xB9, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040F6B0,
        7,
        3,
        0x0066B790,
        "ARENA_POOL",
        0,
        bytes((0x8D, 0x0C, 0xC5, 0x90, 0xB7, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040F6D5,
        7,
        3,
        0x0066B790,
        "ARENA_POOL",
        0,
        bytes((0x8D, 0x0C, 0xCD, 0x90, 0xB7, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040F700,
        7,
        3,
        0x0066B7C8,
        "ARENA_POOL",
        56,
        bytes((0x8B, 0x04, 0xC5, 0xC8, 0xB7, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040F720,
        7,
        3,
        0x0066B790,
        "ARENA_POOL",
        0,
        bytes((0x8D, 0x0C, 0xC5, 0x90, 0xB7, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040F740,
        8,
        4,
        0x0066BAD4,
        "ARENA_POOL",
        836,
        bytes((0x66, 0x8B, 0x04, 0xC5, 0xD4, 0xBA, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040F765,
        7,
        3,
        0x0066BAD4,
        "ARENA_POOL",
        836,
        bytes((0x89, 0x14, 0xC5, 0xD4, 0xBA, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040F780,
        7,
        3,
        0x0066B790,
        "ARENA_POOL",
        0,
        bytes((0x8D, 0x0C, 0xC5, 0x90, 0xB7, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040F7A0,
        8,
        4,
        0x0066BAAC,
        "ARENA_POOL",
        796,
        bytes((0x0F, 0xBE, 0x04, 0xC5, 0xAC, 0xBA, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040F7C4,
        7,
        3,
        0x0066BAAC,
        "ARENA_POOL",
        796,
        bytes((0x88, 0x0C, 0xC5, 0xAC, 0xBA, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040F7EA,
        7,
        3,
        0x0066B790,
        "ARENA_POOL",
        0,
        bytes((0x8D, 0x0C, 0xD5, 0x90, 0xB7, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040F814,
        7,
        3,
        0x0066B808,
        "ARENA_POOL",
        120,
        bytes((0x89, 0x0C, 0xC5, 0x08, 0xB8, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040F830,
        7,
        3,
        0x0066B790,
        "ARENA_POOL",
        0,
        bytes((0x8D, 0x0C, 0xC5, 0x90, 0xB7, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040F855,
        8,
        4,
        0x0066BDD0,
        "ARENA_POOL",
        1600,
        bytes((0x66, 0x89, 0x0C, 0xC5, 0xD0, 0xBD, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040F87D,
        7,
        3,
        0x0066BDD2,
        "ARENA_POOL",
        1602,
        bytes((0x66, 0x89, 0x88, 0xD2, 0xBD, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040F884,
        7,
        3,
        0x0066BDD4,
        "ARENA_POOL",
        1604,
        bytes((0x66, 0x89, 0x90, 0xD4, 0xBD, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040F8A5,
        7,
        3,
        0x0066B790,
        "ARENA_POOL",
        0,
        bytes((0x8D, 0x0C, 0xCD, 0x90, 0xB7, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040F8D0,
        8,
        4,
        0x0066BA20,
        "ARENA_POOL",
        656,
        bytes((0x66, 0x8B, 0x04, 0xC5, 0x20, 0xBA, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040F8F0,
        7,
        3,
        0x0066B984,
        "ARENA_POOL",
        500,
        bytes((0x8A, 0x04, 0xC5, 0x84, 0xB9, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040F910,
        7,
        3,
        0x0066B790,
        "ARENA_POOL",
        0,
        bytes((0x8D, 0x0C, 0xC5, 0x90, 0xB7, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040F935,
        8,
        4,
        0x0066BAC8,
        "ARENA_POOL",
        824,
        bytes((0x66, 0x89, 0x0C, 0xC5, 0xC8, 0xBA, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040F950,
        8,
        4,
        0x0066BAC8,
        "ARENA_POOL",
        824,
        bytes((0x0F, 0xBF, 0x04, 0xC5, 0xC8, 0xBA, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040F975,
        8,
        4,
        0x0066B9A0,
        "ARENA_POOL",
        528,
        bytes((0x66, 0x3B, 0x0C, 0xC5, 0xA0, 0xB9, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040F97D,
        7,
        3,
        0x0066B9A0,
        "ARENA_POOL",
        528,
        bytes((0x8D, 0x04, 0xC5, 0xA0, 0xB9, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040F9B0,
        7,
        3,
        0x0066B9F4,
        "ARENA_POOL",
        612,
        bytes((0x8A, 0x04, 0xC5, 0xF4, 0xB9, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040F9D0,
        7,
        3,
        0x0066B978,
        "ARENA_POOL",
        488,
        bytes((0x8B, 0x04, 0xC5, 0x78, 0xB9, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040F9F5,
        7,
        3,
        0x0066B844,
        "ARENA_POOL",
        180,
        bytes((0x89, 0x14, 0xC5, 0x44, 0xB8, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040FA1A,
        7,
        3,
        0x0066B790,
        "ARENA_POOL",
        0,
        bytes((0x8D, 0x0C, 0xD5, 0x90, 0xB7, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040FA40,
        8,
        4,
        0x0066B94E,
        "ARENA_POOL",
        446,
        bytes((0x66, 0x8B, 0x04, 0xC5, 0x4E, 0xB9, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040FA60,
        8,
        4,
        0x0066B950,
        "ARENA_POOL",
        448,
        bytes((0x66, 0x8B, 0x04, 0xC5, 0x50, 0xB9, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040FA8A,
        7,
        3,
        0x0066B790,
        "ARENA_POOL",
        0,
        bytes((0x8D, 0x0C, 0xD5, 0x90, 0xB7, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040FAC9,
        7,
        3,
        0x0066B790,
        "ARENA_POOL",
        0,
        bytes((0x8D, 0x0C, 0xD5, 0x90, 0xB7, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040FB04,
        7,
        3,
        0x0066B790,
        "ARENA_POOL",
        0,
        bytes((0x8D, 0x0C, 0xCD, 0x90, 0xB7, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040FB35,
        7,
        3,
        0x0066B790,
        "ARENA_POOL",
        0,
        bytes((0x8D, 0x0C, 0xCD, 0x90, 0xB7, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040FB65,
        7,
        3,
        0x0066B790,
        "ARENA_POOL",
        0,
        bytes((0x8D, 0x0C, 0xCD, 0x90, 0xB7, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040FB95,
        7,
        3,
        0x0066B790,
        "ARENA_POOL",
        0,
        bytes((0x8D, 0x0C, 0xCD, 0x90, 0xB7, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040FBC0,
        7,
        3,
        0x0066B980,
        "ARENA_POOL",
        496,
        bytes((0x8B, 0x04, 0xC5, 0x80, 0xB9, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040FBE0,
        8,
        4,
        0x0066BAB0,
        "ARENA_POOL",
        800,
        bytes((0x66, 0x8B, 0x04, 0xC5, 0xB0, 0xBA, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040FC00,
        7,
        3,
        0x0066B988,
        "ARENA_POOL",
        504,
        bytes((0x8A, 0x04, 0xC5, 0x88, 0xB9, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040FC20,
        7,
        3,
        0x0066B790,
        "ARENA_POOL",
        0,
        bytes((0x8D, 0x0C, 0xC5, 0x90, 0xB7, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040FC40,
        8,
        4,
        0x0066B844,
        "ARENA_POOL",
        180,
        bytes((0x66, 0x8B, 0x04, 0xC5, 0x44, 0xB8, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040FC60,
        8,
        4,
        0x0066B848,
        "ARENA_POOL",
        184,
        bytes((0x66, 0x8B, 0x04, 0xC5, 0x48, 0xB8, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040FC80,
        7,
        3,
        0x0066B790,
        "ARENA_POOL",
        0,
        bytes((0x8D, 0x0C, 0xC5, 0x90, 0xB7, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040FCA0,
        7,
        3,
        0x0066B7C4,
        "ARENA_POOL",
        52,
        bytes((0x8A, 0x04, 0xC5, 0xC4, 0xB7, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040FCCF,
        7,
        3,
        0x0066B790,
        "ARENA_POOL",
        0,
        bytes((0x8D, 0x0C, 0xC5, 0x90, 0xB7, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040FD04,
        7,
        3,
        0x0066B790,
        "ARENA_POOL",
        0,
        bytes((0x8D, 0x0C, 0xCD, 0x90, 0xB7, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040FD30,
        7,
        3,
        0x0066BACC,
        "ARENA_POOL",
        828,
        bytes((0x8B, 0x04, 0xC5, 0xCC, 0xBA, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040FD50,
        7,
        3,
        0x0066B790,
        "ARENA_POOL",
        0,
        bytes((0x8D, 0x0C, 0xC5, 0x90, 0xB7, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040FD70,
        7,
        3,
        0x0066B790,
        "ARENA_POOL",
        0,
        bytes((0x8D, 0x0C, 0xC5, 0x90, 0xB7, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040FD94,
        7,
        3,
        0x0066B96C,
        "ARENA_POOL",
        476,
        bytes((0x8B, 0x04, 0xC5, 0x6C, 0xB9, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040FDC8,
        8,
        4,
        0x0066BCC2,
        "ARENA_POOL",
        1330,
        bytes((0x66, 0x8B, 0x04, 0x55, 0xC2, 0xBC, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040FDF0,
        7,
        3,
        0x0066B790,
        "ARENA_POOL",
        0,
        bytes((0x8D, 0x0C, 0xC5, 0x90, 0xB7, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040FE15,
        7,
        3,
        0x0066BBA8,
        "ARENA_POOL",
        1048,
        bytes((0x8D, 0x0C, 0xCD, 0xA8, 0xBB, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040FE48,
        8,
        4,
        0x0066BCDA,
        "ARENA_POOL",
        1354,
        bytes((0x66, 0x8B, 0x04, 0x55, 0xDA, 0xBC, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040FE78,
        8,
        4,
        0x0066BCF2,
        "ARENA_POOL",
        1378,
        bytes((0x66, 0x8B, 0x04, 0x55, 0xF2, 0xBC, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040FEA8,
        9,
        4,
        0x0066BE52,
        "ARENA_POOL",
        1730,
        bytes((0x66, 0x83, 0x3C, 0x95, 0x52, 0xBE, 0x66, 0x00, 0x00)),
    ),
    PatchRecord(
        0x0040FEB1,
        7,
        3,
        0x0066BE52,
        "ARENA_POOL",
        1730,
        bytes((0x8D, 0x04, 0x95, 0x52, 0xBE, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040FEE0,
        8,
        4,
        0x0066BD0A,
        "ARENA_POOL",
        1402,
        bytes((0x66, 0x8B, 0x04, 0xC5, 0x0A, 0xBD, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040FF05,
        7,
        3,
        0x0066B790,
        "ARENA_POOL",
        0,
        bytes((0x8D, 0x0C, 0xCD, 0x90, 0xB7, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040FF30,
        7,
        3,
        0x0066B790,
        "ARENA_POOL",
        0,
        bytes((0x8D, 0x0C, 0xC5, 0x90, 0xB7, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040FF50,
        7,
        3,
        0x0066B790,
        "ARENA_POOL",
        0,
        bytes((0x8D, 0x0C, 0xC5, 0x90, 0xB7, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040FF70,
        7,
        3,
        0x0066B94C,
        "ARENA_POOL",
        444,
        bytes((0x8A, 0x04, 0xC5, 0x4C, 0xB9, 0x66, 0x00)),
    ),
    PatchRecord(
        0x0040FFC3,
        7,
        3,
        0x0066B790,
        "ARENA_POOL",
        0,
        bytes((0x8D, 0x0C, 0xCD, 0x90, 0xB7, 0x66, 0x00)),
    ),
    PatchRecord(
        0x00410009,
        7,
        3,
        0x0066B790,
        "ARENA_POOL",
        0,
        bytes((0x8D, 0x0C, 0xD5, 0x90, 0xB7, 0x66, 0x00)),
    ),
)

# Separate, statically reviewed FUN_00443190/FUN_0048BC00 creation records.
# These are deliberately not folded into PATCHES: the frozen 120-record
# accessor family and its provenance remain independently testable.
CREATION_PATCHES = (
    PatchRecord(0x00443241, 7, 3, 0x0066B790, "ARENA_POOL", 0,
                bytes.fromhex("8d0cc590b76600")),
    PatchRecord(0x0048BC56, 8, 4, 0x008990C8, "ARENA_EXISTS", 0,
                bytes.fromhex("66891445c8908900")),
    PatchRecord(0x0048BC65, 10, 4, 0x00899A28, "ARENA_AGE", 0,
                bytes.fromhex("66c70455289a89000000")),
    PatchRecord(0x0048BC76, 7, 3, 0x00975908, "COUNTER_ACTIVE", 0,
                bytes.fromhex("0fbf0508599700")),
    PatchRecord(0x0048BC7D, 8, 4, 0x00974FA8, "ARENA_ACTIVE", 0,
                bytes.fromhex("66891445a84f9700")),
    PatchRecord(0x0048BC85, 6, 2, 0x00975908, "COUNTER_ACTIVE", 0,
                bytes.fromhex("66a108599700")),
    PatchRecord(0x0048BC92, 7, 3, 0x00975908, "COUNTER_ACTIVE", 0,
                bytes.fromhex("66ff0508599700")),
    PatchRecord(0x0048BCA1, 7, 3, 0x0089C2C8, "COUNTER_CATA", 0,
                bytes.fromhex("0fbf0dc8c28900")),
    PatchRecord(0x0048BCAE, 7, 3, 0x0089B008, "ARENA_CATA", 0,
                bytes.fromhex("89148d08b08900")),
    PatchRecord(0x0048BCB5, 7, 3, 0x0089C2C8, "COUNTER_CATA", 0,
                bytes.fromhex("66ff05c8c28900")),
    PatchRecord(0x0048BCBE, 7, 3, 0x0089D58A, "COUNTER_CATB", 0,
                bytes.fromhex("0fbf058ad58900")),
    PatchRecord(0x0048BCCB, 7, 3, 0x0089C2CA, "ARENA_CATB", 0,
                bytes.fromhex("890c85cac28900")),
    PatchRecord(0x0048BCD2, 7, 3, 0x0089D58A, "COUNTER_CATB", 0,
                bytes.fromhex("66ff058ad58900")),
)

# Separate owner add/remove lifecycle reads.  The owner roster, counters,
# type/cost operands, and low-word-ID behavior remain untouched.
OWNER_LIFECYCLE_PATCHES = (
    PatchRecord(0x0043EE80, 6, 2, 0x0066B81D, "ARENA_POOL", 0x8D,
                bytes.fromhex("8a901db86600")),
    PatchRecord(0x0043EEA2, 6, 2, 0x0066B968, "ARENA_POOL", 0x1D8,
                bytes.fromhex("8a9068b96600")),
    PatchRecord(0x0043EF71, 6, 2, 0x0066B81D, "ARENA_POOL", 0x8D,
                bytes.fromhex("8a901db86600")),
    PatchRecord(0x0043EF92, 6, 2, 0x0066B968, "ARENA_POOL", 0x1D8,
                bytes.fromhex("8a9068b96600")),
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def align(value: int, boundary: int) -> int:
    return (value + boundary - 1) // boundary * boundary


def parse_pe(data: bytes) -> PE:
    if len(data) < 0x100 or data[:2] != b"MZ":
        raise ValueError("not a PE32 image")
    e = struct.unpack_from("<I", data, 0x3C)[0]
    if data[e : e + 4] != b"PE\0\0":
        raise ValueError("bad PE signature")
    coff = e + 4
    n = struct.unpack_from("<H", data, coff + 2)[0]
    opt_size = struct.unpack_from("<H", data, coff + 16)[0]
    opt = coff + 20
    if struct.unpack_from("<H", data, opt)[0] != 0x10B:
        raise ValueError("not PE32")
    image_base, sec_align, file_align = struct.unpack_from("<III", data, opt + 28)
    size_image, size_headers = struct.unpack_from("<II", data, opt + 56)
    table = opt + opt_size
    sections = []
    for i in range(n):
        p = table + i * 40
        name = data[p : p + 8].rstrip(b"\0")
        vs, va, rs, rp = struct.unpack_from("<IIII", data, p + 8)
        chars = struct.unpack_from("<I", data, p + 36)[0]
        if rp + rs > len(data):
            raise ValueError("section exceeds file")
        sections.append(Section(name, vs, va, rs, rp, chars))
    return PE(
        e, n, sec_align, file_align, image_base, size_image, size_headers, table, tuple(sections)
    )


def storage_layout(section_rva: int, *, section_alignment: int = 0x1000) -> StorageLayout:
    if section_rva % section_alignment:
        raise ValueError("section RVA is not aligned")
    o = 0
    offsets = {}

    def arena(name, size):
        nonlocal o
        o = align(o, 4)
        offsets[name] = o
        o += size

    arena("unit", CAPACITY * UNIT_SIZE)
    arena("exists", CAPACITY * 2)
    arena("age", CAPACITY * 2)
    arena("active", CAPACITY * 2)
    arena("cata", CAPACITY * 4)
    arena("catb", CAPACITY * 4)
    counters = {}
    for name in ("active_count", "cata_count", "catb_count"):
        o = align(o, 4)
        counters[name] = o
        o += 2
    return StorageLayout(section_rva, CAPACITY, UNIT_SIZE, offsets["unit"], offsets, counters, o)


def _target(row: PatchRecord, layout: StorageLayout) -> int:
    if row.region == "ARENA_POOL":
        base = layout.section_rva + layout.arena_offsets["unit"] + row.field_offset
    elif row.region == "ARENA_EXISTS":
        base = layout.section_rva + layout.arena_offsets["exists"]
    elif row.region == "ARENA_AGE":
        base = layout.section_rva + layout.arena_offsets["age"]
    elif row.region == "ARENA_ACTIVE":
        base = layout.section_rva + layout.arena_offsets["active"]
    elif row.region == "ARENA_CATA":
        base = layout.section_rva + layout.arena_offsets["cata"]
    elif row.region == "ARENA_CATB":
        base = layout.section_rva + layout.arena_offsets["catb"]
    elif row.region == "COUNTER_ACTIVE":
        base = layout.section_rva + layout.counter_offsets["active_count"]
    elif row.region == "COUNTER_CATA":
        base = layout.section_rva + layout.counter_offsets["cata_count"]
    elif row.region == "COUNTER_CATB":
        base = layout.section_rva + layout.counter_offsets["catb_count"]
    else:
        raise ValueError(f"unknown patch region {row.region}")
    return IMAGE_BASE + base


def _validate_records(data: bytes, layout: StorageLayout) -> None:
    # Reserve the allocator slice before considering typed fixups.  A future
    # recipe must fail closed rather than letting a relocation overwrite it.
    seen = [
        (ALLOCATOR_FILE_OFFSET, ALLOCATOR_FILE_OFFSET + len(ALLOCATOR_BYTES)),
        (INIT_CALL_VA - IMAGE_BASE, INIT_CALL_VA - IMAGE_BASE + len(INIT_CALL_BYTES)),
    ]
    seen.extend((offset, offset + len(before)) for offset, before, _ in FIXED_SUPPLY_EDITS)
    for row in PATCHES:
        if len(row.old_bytes) != row.instruction_length:
            raise ValueError("patch instruction length mismatch")
        off = row.file_offset
        if off < 0 or off + row.instruction_length > len(data):
            raise ValueError("patch outside image")
        if data[off : off + row.instruction_length] != row.old_bytes:
            raise ValueError(f"unexpected bytes at {row.va:#x}")
        encoded = struct.unpack_from("<I", data, off + row.operand_offset)[0]
        if encoded != row.old_target:
            raise ValueError(f"unexpected operand at {row.va:#x}")
        if not (0 <= row.operand_offset <= row.instruction_length - 4):
            raise ValueError("invalid operand")
        seen.append((off, off + row.instruction_length))
    seen.sort()
    for (_, end), (start, _) in zip(seen, seen[1:]):
        if start < end:
            raise ValueError("overlapping patch records")


def _validate_additional_records(
    data: bytes,
    layout: StorageLayout,
    rows: tuple[PatchRecord, ...],
    prior_rows: tuple[PatchRecord, ...],
    family_name: str,
) -> None:
    """Validate an additional family against frozen and already-added records."""
    hard_reserved = [
        (ALLOCATOR_FILE_OFFSET, ALLOCATOR_FILE_OFFSET + len(ALLOCATOR_BYTES), "allocator"),
        (INIT_CALL_VA - IMAGE_BASE, INIT_CALL_VA - IMAGE_BASE + len(INIT_CALL_BYTES), "init call"),
    ]
    hard_reserved.extend(
        (offset, offset + len(before), "fixed-supply")
        for offset, before, _ in FIXED_SUPPLY_EDITS
    )
    typed_records = list(PATCHES) + list(prior_rows)
    for row in rows:
        if row.region not in {
            "ARENA_POOL", "ARENA_EXISTS", "ARENA_AGE", "ARENA_ACTIVE", "ARENA_CATA",
            "ARENA_CATB", "COUNTER_ACTIVE", "COUNTER_CATA", "COUNTER_CATB",
        }:
            raise ValueError(f"unknown {family_name} patch region {row.region}")
        if len(row.old_bytes) != row.instruction_length:
            raise ValueError(f"{family_name} instruction length mismatch")
        if not (0 <= row.operand_offset <= row.instruction_length - 4):
            raise ValueError(f"invalid {family_name} operand")
        off = row.file_offset
        if off < 0 or off + row.instruction_length > len(data):
            raise ValueError(f"{family_name} patch outside image")
        end = off + row.instruction_length
        for start, reserved_end, name in hard_reserved:
            if max(start, off) < min(reserved_end, end):
                raise ValueError(f"{family_name} record overlaps reserved {name} at {row.va:#x}")
        for prior in typed_records:
            start = prior.file_offset
            prior_end = start + prior.instruction_length
            if max(start, off) >= min(prior_end, end):
                continue
            exact = (
                off == start
                and end == prior_end
                and row == prior
                and _target(row, layout) == _target(prior, layout)
            )
            if not exact:
                raise ValueError(f"non-identical or partial typed overlap at {row.va:#x}")
        if data[off : off + row.instruction_length] != row.old_bytes:
            raise ValueError(f"unexpected {family_name} bytes at {row.va:#x}")
        encoded = struct.unpack_from("<I", data, off + row.operand_offset)[0]
        if encoded != row.old_target:
            raise ValueError(f"unexpected {family_name} operand at {row.va:#x}")
        typed_records.append(row)


def _validate_creation_records(data: bytes, layout: StorageLayout) -> None:
    _validate_additional_records(data, layout, CREATION_PATCHES, (), "creation")


def _validate_owner_lifecycle_records(data: bytes, layout: StorageLayout) -> None:
    _validate_additional_records(
        data, layout, OWNER_LIFECYCLE_PATCHES, CREATION_PATCHES, "owner lifecycle"
    )


def _allocator_after(layout: StorageLayout) -> bytes:
    # The selector's three proven address edits: age+2, paired existence delta,
    # and the age-array exclusive end.  Pool base is intentionally untouched.
    age_base = IMAGE_BASE + layout.section_rva + layout.arena_offsets["age"]
    exists_base = IMAGE_BASE + layout.section_rva + layout.arena_offsets["exists"]
    # The original selector starts at age_base+2, but its paired existence
    # displacement is measured from the unshifted age base.  Its exclusive
    # bound likewise ends at age_base + capacity*2.
    age = age_base + 2
    end = age_base + CAPACITY * 2
    out = bytearray(ALLOCATOR_BYTES)
    struct.pack_into("<I", out, 0x0D, age)
    struct.pack_into("<i", out, 0x14, exists_base - age_base)
    struct.pack_into("<I", out, 0x33, end)
    return bytes(out)


def _emit_mov_imm(reg: int, value: int) -> bytes:
    return bytes((0xB8 + reg,)) + struct.pack("<I", value)


def _build_init_stub(layout: StorageLayout, stub_va: int, original: bytes) -> bytes:
    """Build the x86 post-original-call prefix/tail copier without runtime deps."""
    call_off = INIT_CALL_VA - IMAGE_BASE
    if original[call_off : call_off + 5] != INIT_CALL_BYTES:
        raise ValueError("init call bytes mismatch")
    if (
        original[ORIGINAL_INIT_VA - IMAGE_BASE : ORIGINAL_INIT_VA - IMAGE_BASE + 7]
        != ORIGINAL_INIT_BYTES
    ):
        raise ValueError("original init bytes mismatch")
    code = bytearray(b"\xe8\0\0\0\0\x9c\x60\xfc")
    rel = ORIGINAL_INIT_VA - (stub_va + 5)
    struct.pack_into("<i", code, 1, rel)
    destination_arenas = {
        "sidecar_exists": "exists",
        "sidecar_age": "age",
        "sidecar_active": "active",
        "sidecar_cata": "cata",
        "sidecar_catb": "catb",
    }

    def copy_words(name: str) -> None:
        code.extend(_emit_mov_imm(6, INIT_SOURCE_WORDS[name]))  # mov esi, source
        code.extend(
            _emit_mov_imm(
                7, IMAGE_BASE + layout.section_rva + layout.arena_offsets[destination_arenas[name]]
            )
        )
        code.extend(_emit_mov_imm(1, 600))  # 1200 WORDs == 600 DWORDs
        code.extend(b"\xf3\xa5")
        code.extend(b"\x31\xc0")
        code.extend(_emit_mov_imm(1, 1400))  # exact 2800 WORD tail as DWORDs
        code.extend(b"\xf3\xab\x66\xab")  # plus exact final WORD

    def copy_dwords(name: str) -> None:
        code.extend(_emit_mov_imm(6, INIT_SOURCE_DWORDS[name]))
        code.extend(
            _emit_mov_imm(
                7, IMAGE_BASE + layout.section_rva + layout.arena_offsets[destination_arenas[name]]
            )
        )
        code.extend(_emit_mov_imm(1, 1200))
        code.extend(b"\xf3\xa5")
        code.extend(b"\x31\xc0")
        code.extend(_emit_mov_imm(1, 2801))
        code.extend(b"\xf3\xab")

    for name in ("sidecar_exists", "sidecar_age", "sidecar_active"):
        copy_words(name)
    for name in ("sidecar_cata", "sidecar_catb"):
        copy_dwords(name)
    for name, source in INIT_SOURCE_COUNTERS.items():
        code.extend(b"\x66\xa1" + struct.pack("<I", source))
        code.extend(
            b"\x66\xa3"
            + struct.pack(
                "<I",
                IMAGE_BASE
                + layout.section_rva
                + layout.counter_offsets[name.removeprefix("sidecar_")],
            )
        )
    code.extend(b"\x61\x9d\xc3")
    return bytes(code)


def build_candidate(original: bytes) -> bytes:
    if digest(original) != ORIGINAL_SHA256:
        raise ValueError("Unsupported original EXE SHA256")
    pe = parse_pe(original)
    if pe.image_base != IMAGE_BASE or pe.size_of_image != 0xC8F000:
        raise ValueError("unsupported PE layout")
    if original[ALLOCATOR_FILE_OFFSET : ALLOCATOR_FILE_OFFSET + 61] != ALLOCATOR_BYTES:
        raise ValueError("allocator bytes mismatch")
    layout = storage_layout(
        align(pe.size_of_image, pe.section_alignment), section_alignment=pe.section_alignment
    )
    _validate_records(original, layout)
    _validate_creation_records(original, layout)
    _validate_owner_lifecycle_records(original, layout)
    if len(pe.sections) > 0xFFFD:
        raise ValueError("section table full")
    section_raw = align(layout.virtual_size, pe.file_alignment)
    raw_pointer = align(
        max(len(original), *(s.raw_pointer + s.raw_size for s in pe.sections)), pe.file_alignment
    )
    stub_rva = align(layout.section_rva + layout.virtual_size, pe.section_alignment)
    stub = _build_init_stub(layout, IMAGE_BASE + stub_rva, original)
    stub_raw = align(len(stub), pe.file_alignment)
    out = bytearray(fixed_supply_patched_bytes(original))
    if raw_pointer < len(out):
        raise ValueError("raw section overlaps original")
    storage_raw_pointer = raw_pointer
    stub_raw_pointer = align(storage_raw_pointer + section_raw, pe.file_alignment)
    out.extend(b"\0" * (stub_raw_pointer + stub_raw - len(out)))
    # Header metadata is explicit and bounded to the existing header area.
    table = pe.section_table + pe.number_of_sections * 40
    if table + 80 > pe.size_of_headers:
        raise ValueError("no section-header room")
    storage_header = bytearray(40)
    storage_header[:8] = SECTION_NAME.ljust(8, b"\0")
    struct.pack_into(
        "<IIII",
        storage_header,
        8,
        layout.virtual_size,
        layout.section_rva,
        section_raw,
        storage_raw_pointer,
    )
    struct.pack_into(
        "<I",
        storage_header,
        36,
        IMAGE_SCN_CNT_INITIALIZED_DATA | IMAGE_SCN_MEM_READ | IMAGE_SCN_MEM_WRITE,
    )
    init_header = bytearray(40)
    init_header[:8] = b".g2ini\0\0"
    struct.pack_into("<IIII", init_header, 8, len(stub), stub_rva, stub_raw, stub_raw_pointer)
    struct.pack_into(
        "<I", init_header, 36, IMAGE_SCN_CNT_CODE | IMAGE_SCN_MEM_READ | IMAGE_SCN_MEM_EXECUTE
    )
    out[table : table + 40] = storage_header
    out[table + 40 : table + 80] = init_header
    nt = pe.e_lfanew
    coff = nt + 4
    opt = coff + 20
    struct.pack_into("<H", out, coff + 2, pe.number_of_sections + 2)
    struct.pack_into("<I", out, opt + 56, align(stub_rva + len(stub), pe.section_alignment))
    struct.pack_into("<I", out, opt + 4, struct.unpack_from("<I", original, opt + 4)[0] + stub_raw)
    struct.pack_into(
        "<I", out, opt + 8, struct.unpack_from("<I", original, opt + 8)[0] + section_raw
    )
    # Apply only encoded displacement fields, never other instruction bytes.
    for row in PATCHES:
        target = _target(row, layout)
        off = row.file_offset + row.operand_offset
        struct.pack_into("<I", out, off, target)
    for row in CREATION_PATCHES:
        target = _target(row, layout)
        off = row.file_offset + row.operand_offset
        struct.pack_into("<I", out, off, target)
    for row in OWNER_LIFECYCLE_PATCHES:
        target = _target(row, layout)
        off = row.file_offset + row.operand_offset
        struct.pack_into("<I", out, off, target)
    alloc = _allocator_after(layout)
    out[ALLOCATOR_FILE_OFFSET : ALLOCATOR_FILE_OFFSET + 61] = alloc
    call_off = INIT_CALL_VA - IMAGE_BASE
    struct.pack_into("<i", out, call_off + 1, IMAGE_BASE + stub_rva - (INIT_CALL_VA + 5))
    out[storage_raw_pointer : storage_raw_pointer + section_raw] = b"\0" * section_raw
    out[stub_raw_pointer : stub_raw_pointer + len(stub)] = stub
    return bytes(out)


def inspect_candidate(data: bytes) -> dict[str, object]:
    """Return informational metadata; callers must still enforce the SHA/pins."""
    pe = parse_pe(data)
    sec = next((s for s in pe.sections if s.name == SECTION_NAME), None)
    if sec is None:
        raise ValueError("storage section missing")
    return {
        "sha256": digest(data),
        "family_patch_count": len(PATCHES),
        "creation_patch_count": len(CREATION_PATCHES),
        "creation_recipe_sha256": CREATION_RECIPE_SHA256,
        "owner_lifecycle_patch_count": len(OWNER_LIFECYCLE_PATCHES),
        "owner_lifecycle_recipe_sha256": OWNER_LIFECYCLE_RECIPE_SHA256,
        "capacity": CAPACITY,
        "unit_size": UNIT_SIZE,
        "section_rva": sec.virtual_address,
        "section_raw_pointer": sec.raw_pointer,
        "section_raw_size": sec.raw_size,
        "section_virtual_size": sec.virtual_size,
        "section_characteristics": sec.characteristics,
        "allocator_edits": 3,
        "execution": "offline-only",
        "contracts": {
            "initialization": False,
            "consumer": False,
            "owner": False,
            "spatial": False,
            "save": False,
            "lan": False,
        },
    }


def create_copy(source: Path, destination: Path) -> str:
    if source.resolve() == destination.resolve():
        raise ValueError("Refusing to modify input EXE")
    original = source.read_bytes()
    patched = build_candidate(original)
    backup = Path(str(destination) + ".original")
    with backup.open("xb") as f:
        f.write(original)
    try:
        with destination.open("xb") as f:
            f.write(patched)
    except BaseException:
        backup.unlink()
        raise
    return digest(patched)


def restore(destination: Path) -> str:
    backup = Path(str(destination) + ".original")
    original = backup.read_bytes()
    if destination.read_bytes() != build_candidate(original):
        raise ValueError("Refusing restore: destination is not the exact experimental patch")
    destination.write_bytes(original)
    return digest(original)


def main() -> None:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("create-copy")
    c.add_argument("source", type=Path)
    c.add_argument("destination", type=Path)
    r = sub.add_parser("restore")
    r.add_argument("destination", type=Path)
    a = p.parse_args()
    print(
        create_copy(a.source, a.destination) if a.cmd == "create-copy" else restore(a.destination)
    )


if __name__ == "__main__":
    main()
