from __future__ import annotations

import struct

import pytest

from patches.esl2610 import g6_shift_click_2610 as g6
from patches.esl2610 import pe_extend
from patches.esl2610 import g8_supply_1500_500_5000 as mod


@pytest.fixture(scope="module")
def base() -> bytes:
    if not pe_extend.BASE_PATH.exists():
        pytest.skip("local pinned ESL2611 executable required")
    return pe_extend.BASE_PATH.read_bytes()


def _at(data: bytes, va: int, n: int) -> bytes:
    off = pe_extend.va_to_offset(data, va)
    return data[off : off + n]


def test_official_formula_is_1500_plus_200_per_hero(base):
    assert _at(base, 0x43FE9E, 6) == bytes.fromhex("81c1c8000000")  # add ecx,200
    assert _at(base, 0x43FFD4, 12) == bytes.fromhex("05dc050000" "668985 12200000")


def test_per_hero_becomes_500_and_cap_cave_clamps_to_5000(base):
    out, report = mod.build_candidate(base)
    assert _at(out, 0x43FE9E, 6) == bytes.fromhex("81c1f4010000")  # add ecx,500
    hook = _at(out, 0x43FFD4, 5)
    cave = pe_extend.section_va(out, mod.SECTION_NAME)
    assert hook[0] == 0xE9 and 0x43FFD9 + struct.unpack_from("<i", hook, 1)[0] == cave
    body = _at(out, cave, 22)
    assert body[:5] == bytes.fromhex("05dc050000")  # add eax,1500
    assert body[5:10] == bytes.fromhex("3d88130000")  # cmp eax,5000
    assert body[10:12] == bytes.fromhex("7e05")  # jle +5
    assert body[12:17] == bytes.fromhex("b888130000")  # mov eax,5000
    assert body[17] == 0xE9 and cave + 22 + struct.unpack_from("<i", body, 18)[0] == 0x43FFD9
    assert _at(out, 0x43FFD9, 7) == bytes.fromhex("66898512200000")  # store untouched
    assert report["formula"] == "min(1500 + 500*living_heroes, 5000)"


def test_stacks_with_g6_in_either_order(base):
    a, _ = mod.build_candidate(g6.build_candidate(base)[0], require_pinned_base=False)
    b, _ = g6.build_candidate(mod.build_candidate(base)[0], require_pinned_base=False)
    for out in (a, b):
        names = pe_extend.section_names(out)
        assert {mod.SECTION_NAME, g6.SECTION_NAME} <= set(names)
        assert _at(out, 0x43FE9E, 6) == bytes.fromhex("81c1f4010000")


def test_rejects_double_apply_and_unpinned(base):
    out, _ = mod.build_candidate(base)
    with pytest.raises(ValueError):
        mod.build_candidate(out, require_pinned_base=False)
    with pytest.raises(ValueError, match="SHA256"):
        mod.build_candidate(base[:-1] + b"\x01")
