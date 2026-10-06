from __future__ import annotations

import hashlib
from pathlib import Path
import struct

import capstone
import pefile
import pytest

from patches.selection import g6_shift_click_count_bound as g6
from patches.selection import g7_save_trailer_local_restore as mod
from patches.selection import g7_title_load_seat_restore as r4b

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


def _disasm(body: bytes, va: int) -> list[str]:
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    return [f"{i.mnemonic} {i.op_str}" for i in md.disasm(body, va)]


@pytest.mark.parametrize("variant", list(PORT))
def test_candidate_is_deterministic_and_pinned(variant: str, built: dict) -> None:
    base, candidate, report = built[variant]
    assert hashlib.sha256(base).hexdigest() == PORT_SHA[variant]
    assert report["base_sha256"] == PORT_SHA[variant]
    assert report["variant"] == variant
    assert report["stacked_on_g6"] is False
    assert report["candidate_sha256"] == hashlib.sha256(candidate).hexdigest()
    assert mod.build_candidate(base)[0] == candidate


@pytest.mark.parametrize("variant", list(PORT))
def test_diff_is_two_hook_sites_plus_two_caves_only(variant: str, built: dict) -> None:
    base, candidate, _report = built[variant]
    assert len(candidate) == len(base)
    allowed: set[int] = set()
    for hook_va, old in mod.HOOK_OLD.items():
        offset = _file_offset(base, hook_va)
        assert base[offset : offset + 5] == old
        assert candidate[offset : offset + 5] == b"\xe9" + struct.pack(
            "<i", mod.HOOK_TO_CAVE[hook_va] - (hook_va + 5)
        )
        allowed |= set(range(offset, offset + 5))
    for cave_va, body in mod.CAVES.items():
        offset = _file_offset(base, cave_va)
        allowed |= set(range(offset, offset + len(body)))
    changed = {i for i in range(len(base)) if base[i] != candidate[i]}
    assert changed and changed <= allowed


def test_old_hook_bytes_are_the_fclose_tail_jumps() -> None:
    for hook_va, old in mod.HOOK_OLD.items():
        assert old[0] == 0xE9
        assert hook_va + 5 + struct.unpack_from("<i", old, 1)[0] == mod.FCLOSE_VA


@pytest.mark.parametrize("variant", list(PORT))
def test_save_cave_writes_header_then_table_then_tail_jumps_to_fclose(variant: str, built: dict) -> None:
    _base, candidate, _report = built[variant]
    body = candidate[_file_offset(candidate, mod.SAVE_CAVE_VA) :][: len(mod.SAVE_CAVE)]
    buf = mod.SCRATCH_VA
    fwrite = hex(0x4DA39F)
    assert _disasm(body, mod.SAVE_CAVE_VA) == [
        "pushal ",
        "pushfd ",
        f"mov dword ptr [{hex(buf)}], 0x534c3747",
        f"mov dword ptr [{hex(buf + 4)}], 1",
        "mov eax, dword ptr [0xb63fc4]",
        f"mov dword ptr [{hex(buf + 8)}], eax",
        "movzx eax, word ptr [0x4ed848]",
        f"mov dword ptr [{hex(buf + 12)}], eax",
        "push dword ptr [esp + 0x28]",  # FILE*: 8 pushal + pushfd = 0x24, return address 4
        "push 1",
        "push 0x10",
        f"push {hex(buf)}",
        f"call {fwrite}",
        "add esp, 0x10",
        "push dword ptr [esp + 0x28]",
        "push 1",
        "push 0x170",
        "push 0x632c9c",
        f"call {fwrite}",
        "add esp, 0x10",
        "popfd ",
        "popal ",
        f"jmp {hex(mod.FCLOSE_VA)}",
    ]


@pytest.mark.parametrize("variant", list(PORT))
def test_load_cave_restores_only_when_trailer_is_complete_and_solo(variant: str, built: dict) -> None:
    _base, candidate, _report = built[variant]
    body = candidate[_file_offset(candidate, mod.LOAD_CAVE_VA) :][: len(mod.LOAD_CAVE)]
    text = _disasm(body, mod.LOAD_CAVE_VA)
    buf, tbl, fread = mod.SCRATCH_VA, mod.SCRATCH_VA + 0x10, hex(0x4DA4A9)
    skip = next(i.address for i in capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32).disasm(body, mod.LOAD_CAVE_VA)
                if i.mnemonic == "popfd")
    s = f"{skip:#x}"
    assert text == [
        "pushal ",
        "pushfd ",
        "cmp word ptr [0x4ed848], 1",
        f"jne {s}",
        "cmp dword ptr [0x18a68d0], 0x43533547",  # this file carried G5SC
        f"jne {s}",
        "push dword ptr [esp + 0x28]",
        "push 1",
        "push 0x10",
        f"push {hex(buf)}",
        f"call {fread}",
        "add esp, 0x10",
        "cmp eax, 1",
        f"jne {s}",
        f"cmp dword ptr [{hex(buf)}], 0x534c3747",
        f"jne {s}",
        f"cmp dword ptr [{hex(buf + 4)}], 1",
        f"jne {s}",
        f"cmp dword ptr [{hex(buf + 12)}], 1",  # saved game was solo
        f"jne {s}",
        f"cmp dword ptr [{hex(buf + 8)}], 8",
        f"jae {s}",
        "push dword ptr [esp + 0x28]",
        "push 1",
        "push 0x170",
        f"push {hex(tbl)}",
        f"call {fread}",
        "add esp, 0x10",
        "cmp eax, 1",
        f"jne {s}",
        f"mov esi, {hex(tbl)}",
        "mov edi, 0x632c9c",
        "mov ecx, 0x5c",
        "cld ",
        "rep movsd dword ptr es:[edi], dword ptr [esi]",
        f"mov eax, dword ptr [{hex(buf + 8)}]",
        "mov dword ptr [0xb63fc4], eax",
        "popfd ",
        "popal ",
        f"jmp {hex(mod.FCLOSE_VA)}",
    ]


@pytest.mark.parametrize("variant", list(PORT))
def test_caves_and_scratch_are_free_and_do_not_overlap_g6_or_each_other(variant: str, built: dict) -> None:
    base, _candidate, _report = built[variant]
    section = _file_offset(base, mod.G5CODE_VA)
    assert not any(base[section + 0x900 : section + 0x1000])
    spans = sorted((va, va + len(body)) for va, body in mod.CAVES.items())
    spans.append((g6.CAVE_VA, g6.CAVE_VA + len(g6.CAVE_TEMPLATE)))
    spans.sort()
    for (_s0, e0), (s1, _e1) in zip(spans, spans[1:]):
        assert e0 <= s1
    assert spans[-1][1] <= mod.G5CODE_VA + 0x1000
    # no port instruction or data dword names the .g5bss scratch range
    for i in range(len(base) - 4):
        value = int.from_bytes(base[i : i + 4], "little")
        assert not (mod.SCRATCH_VA <= value < mod.SCRATCH_VA + mod.SCRATCH_SIZE)


def test_scratch_header_size_matches_the_saved_header_and_table() -> None:
    assert mod.SCRATCH_SIZE == 0x10 + 0x170
    assert (r4b.HOOK_VA, mod.SAVE_HOOK_VA, mod.LOAD_HOOK_VA) == (0x441310, 0x18A7832, 0x18A78D6)


@pytest.mark.parametrize("variant", list(PORT))
def test_stacks_on_the_g6_candidate_without_overlap(variant: str, built: dict) -> None:
    base, r5_only, _ = built[variant]
    g6_only, _ = g6.build_candidate(base)
    stacked, report = mod.build_candidate(g6_only)
    assert report["stacked_on_g6"] is True
    assert report["variant"] == variant
    changed = {i for i in range(len(base)) if base[i] != stacked[i]}
    g6_changed = {i for i in range(len(base)) if base[i] != g6_only[i]}
    r5_changed = {i for i in range(len(base)) if base[i] != r5_only[i]}
    assert changed == g6_changed | r5_changed and not g6_changed & r5_changed
    assert mod.restore_candidate(stacked, g6_only) == g6_only


@pytest.mark.parametrize("variant", list(PORT))
def test_rollback_is_byte_identical_and_r4b_hook_is_untouched(variant: str, built: dict) -> None:
    base, candidate, _report = built[variant]
    assert mod.restore_candidate(candidate, base) == base
    offset = _file_offset(candidate, r4b.HOOK_VA)
    assert candidate[offset : offset + 6] == r4b.HOOK_OLD


def test_rejects_unpinned_input_r4b_stacking_and_foreign_cave_bytes() -> None:
    if not PORT["normal"].is_file():
        pytest.skip("pinned G5 port executables are required")
    base = PORT["normal"].read_bytes()
    with pytest.raises(ValueError):
        mod.build_candidate(base[:-1] + b"\x01")
    with pytest.raises(ValueError):
        mod.restore_candidate(base, base)
    with pytest.raises(ValueError):
        mod.build_candidate(r4b.build_candidate(base)[0])  # R4b is withdrawn: not a valid base
    tampered = bytearray(base)
    tampered[_file_offset(base, mod.LOAD_CAVE_VA) + 3] = 1
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
