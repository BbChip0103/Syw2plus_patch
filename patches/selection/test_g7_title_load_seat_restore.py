from __future__ import annotations

import hashlib
from pathlib import Path
import struct

import capstone
import pefile
import pytest

from patches.selection import g6_shift_click_count_bound as g6
from patches.selection import g7_title_load_seat_restore as mod

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT.parent / "260921_temp"
PORT = {
    "normal": INPUT / "[ESL]Syw2plus 2608_AI상점개설_장수7명_전비1500-500-5000_G2_개인500_공용4092_G5_선택50_시험용.exe",
    "fixed_start": INPUT
    / "[ESL]Syw2plus 2608_AI상점개설_장수7명_전비1500-500-5000_시작자리고정_G2_개인500_공용4092_G5_선택50_시험용.exe",
}
PORT_SHA = {
    "normal": "0e28ef57f8eb1f674df544ef84889bd2c51224720a09d0a18122e55f8399d257",
    "fixed_start": "703deaf4c07b44975417f6835c569d65fa03adc2272ff6c75866da4723cd6ea0",
}


@pytest.fixture(scope="module")
def built() -> dict[str, tuple[bytes, bytes, dict]]:
    if not all(p.is_file() for p in PORT.values()):
        pytest.skip("pinned G5 port executables are required")
    out = {}
    for variant, path in PORT.items():
        base = path.read_bytes()
        candidate, report = mod.build_candidate(base)
        out[variant] = (base, candidate, report)
    return out


def _file_offset(data: bytes, va: int) -> int:
    pe = pefile.PE(data=data)
    for s in pe.sections:
        start = s.VirtualAddress + mod.IMAGE_BASE
        if start <= va < start + max(s.Misc_VirtualSize, s.SizeOfRawData):
            return va - start + s.PointerToRawData
    raise AssertionError(hex(va))


@pytest.mark.parametrize("variant", list(PORT))
def test_candidate_is_deterministic_and_pinned(variant: str, built: dict) -> None:
    base, candidate, report = built[variant]
    assert hashlib.sha256(base).hexdigest() == PORT_SHA[variant]
    assert report["base_sha256"] == PORT_SHA[variant]
    assert report["variant"] == variant
    assert report["stacked_on_g6"] is False
    assert report["candidate_sha256"] == hashlib.sha256(candidate).hexdigest()
    again, _ = mod.build_candidate(base)
    assert again == candidate


@pytest.mark.parametrize("variant", list(PORT))
def test_diff_is_hook_site_plus_cave_only(variant: str, built: dict) -> None:
    base, candidate, _report = built[variant]
    assert len(candidate) == len(base)
    hook = _file_offset(base, mod.HOOK_VA)
    cave = _file_offset(base, mod.CAVE_VA)
    allowed = set(range(hook, hook + 6)) | set(range(cave, cave + len(mod.CAVE_TEMPLATE)))
    changed = {i for i in range(len(base)) if base[i] != candidate[i]}
    assert changed and changed <= allowed
    assert base[hook : hook + 6] == bytes.fromhex("8b2d2caf b300".replace(" ", ""))
    assert candidate[hook : hook + 6] == b"\xe9" + struct.pack("<i", mod.CAVE_VA - (mod.HOOK_VA + 5)) + b"\x90"


@pytest.mark.parametrize("variant", list(PORT))
def test_cave_disassembly_matches_the_r4b_design(variant: str, built: dict) -> None:
    _base, candidate, _report = built[variant]
    cave = _file_offset(candidate, mod.CAVE_VA)
    body = candidate[cave : cave + len(mod.CAVE_TEMPLATE)]
    assert len(body) == 66
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    text = [f"{i.mnemonic} {i.op_str}" for i in md.disasm(body, mod.CAVE_VA)]
    assert text == [
        "pushal ",
        "pushfd ",
        "cmp word ptr [0x4ed848], 1",
        f"jne {hex(mod.CAVE_VA + 53)}",
        "mov esi, 0x632f7c",
        "mov edi, 0x632c9c",
        "mov ecx, 0x5c",
        "cld ",
        "rep movsd dword ptr es:[edi], dword ptr [esi]",
        "mov dword ptr [0xb63fc4], 0",
        "push 0xb63fc4",
        f"call {hex(mod.RESTORE_CALL_TARGET_VA)}",
        "add esp, 4",
        "popfd ",
        "popal ",
        "mov ebp, dword ptr [0xb3af2c]",
        f"jmp {hex(mod.RESUME_VA)}",
    ]
    assert mod.RESTORE_CALL_TARGET_VA == 0x43AF40 and mod.RESUME_VA == 0x441316


@pytest.mark.parametrize("variant", list(PORT))
def test_hook_jumps_to_cave_and_cave_resumes_after_the_replaced_instruction(variant: str, built: dict) -> None:
    _base, candidate, _report = built[variant]
    hook = _file_offset(candidate, mod.HOOK_VA)
    assert candidate[hook] == 0xE9
    assert mod.HOOK_VA + 5 + struct.unpack_from("<i", candidate, hook + 1)[0] == mod.CAVE_VA
    assert mod.HOOK_VA + 6 == mod.RESUME_VA


@pytest.mark.parametrize("variant", list(PORT))
def test_cave_lies_in_zero_tail_and_does_not_overlap_g6_cave(variant: str, built: dict) -> None:
    base, _candidate, _report = built[variant]
    section = _file_offset(base, mod.G5CODE_VA)
    tail = base[section + 0x900 : section + 0x1000]
    assert not any(tail), "port .g5code tail must be zero"
    assert mod.CAVE_VA + len(mod.CAVE_TEMPLATE) <= mod.G5CODE_VA + 0x1000
    g6_end = g6.CAVE_VA + len(g6.CAVE_TEMPLATE)
    assert mod.CAVE_VA >= g6_end or mod.CAVE_VA + len(mod.CAVE_TEMPLATE) <= g6.CAVE_VA
    assert mod.HOOK_VA not in range(g6.HOOK_VA, g6.HOOK_VA + 8)


@pytest.mark.parametrize("variant", list(PORT))
def test_stacks_on_the_g6_candidate_without_overlap(variant: str, built: dict) -> None:
    base, g7_only, _ = built[variant]
    g6_only, _ = g6.build_candidate(base)
    g67, report = mod.build_candidate(g6_only)
    assert report["stacked_on_g6"] is True
    assert report["base_sha256"] == hashlib.sha256(g6_only).hexdigest()
    assert report["variant"] == variant
    changed = {i for i in range(len(base)) if base[i] != g67[i]}
    g6_changed = {i for i in range(len(base)) if base[i] != g6_only[i]}
    g7_changed = {i for i in range(len(base)) if base[i] != g7_only[i]}
    assert changed == g6_changed | g7_changed
    assert not g6_changed & g7_changed
    assert mod.restore_candidate(g67, g6_only) == g6_only


@pytest.mark.parametrize("variant", list(PORT))
def test_rollback_is_byte_identical(variant: str, built: dict) -> None:
    base, candidate, _report = built[variant]
    assert mod.restore_candidate(candidate, base) == base


def test_rejects_unpinned_input_and_wrong_old_bytes() -> None:
    if not PORT["normal"].is_file():
        pytest.skip("pinned G5 port executables are required")
    base = PORT["normal"].read_bytes()
    with pytest.raises(ValueError):
        mod.build_candidate(base[:-1] + b"\x01")
    with pytest.raises(ValueError):
        mod.restore_candidate(base, base)  # base is not a candidate


def test_rejects_a_foreign_modification_in_the_cave_or_a_g6_lookalike() -> None:
    if not PORT["normal"].is_file():
        pytest.skip("pinned G5 port executables are required")
    base = bytearray(PORT["normal"].read_bytes())
    g6_only, _ = g6.build_candidate(bytes(base))
    tampered = bytearray(g6_only)
    tampered[_file_offset(bytes(base), g6.CAVE_VA) + 3] ^= 0xFF  # G6 cave no longer the pinned G6 build
    with pytest.raises(ValueError):
        mod.build_candidate(bytes(tampered))


def test_write_refuses_overwrite_of_input_and_existing_destination(tmp_path: Path) -> None:
    if not PORT["normal"].is_file():
        pytest.skip("pinned G5 port executables are required")
    with pytest.raises(ValueError):
        mod.write_candidate(PORT["normal"], PORT["normal"])
    destination = tmp_path / "out.exe"
    destination.write_bytes(b"keep")
    with pytest.raises(FileExistsError):
        mod.write_candidate(PORT["normal"], destination)
    assert destination.read_bytes() == b"keep"
