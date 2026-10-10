from __future__ import annotations

from pathlib import Path

import capstone
import pefile
import pytest

from patches.esl2610 import g2_combo_2610 as combo
from patches.esl2610 import g2_pool4093_2610, pe_extend

V8_SHA256 = "1e83466eab020818a6c0e9057508d71451af3ee1098af43ebefc20de8ab96e3d"
# Historical pre-G9 r8 output remains frozen as provenance, not the current V89 pin.
# Prior V89 pin retained in history; the G9 header-overlap fix intentionally
# changes the V89 bytes by moving its 15-byte hook into verified .g8code zero
# padding (same V8 input SHA, no section/header growth). Current candidate:
# ../temp/Syw2plus_patch/20261010_g9_windows_header_fix/artifactreport.json
V89_PRE_G9_R8_SHA256 = "39680ebbb202ba79cca4c47ac3eeb73b5cc9e8dbbf75c99ba679d07b1422db51"
V89_SHA256 = "b612109b8cd9e313927871a5a35f28cc09b9c95f80626c938f4d42192cb00556"


@pytest.fixture(scope="module")
def base() -> bytes:
    if not pe_extend.BASE_PATH.exists() or not g2_pool4093_2610.STOCK_ORACLE.exists():
        pytest.fail("pinned official 2613 EXE or stock oracle missing: V8/V89 not verifiable here")
    return pe_extend.BASE_PATH.read_bytes()


@pytest.fixture(scope="module")
def v8(base):
    return combo.build(base, "v8")


@pytest.fixture(scope="module")
def v89(base):
    return combo.build(base, "v89")


def test_combo_hashes_are_pinned(v8, v89):
    assert v8[1]["candidate_sha256"] == V8_SHA256
    assert v89[1]["candidate_sha256"] == V89_SHA256
    assert v8[1]["layers"] == ["G2", "G6", "G8"]
    assert v89[1]["layers"] == ["G2", "G6", "G8", "G9"]


def test_combo_uses_the_four_freed_section_slots(v8):
    image, report = v8
    assert report["sections"] == [".g2bss", ".g2code", ".g6code", ".g8code"]
    assert pe_extend.free_header_slots(image) == 0


def test_g9_stack_keeps_the_pinned_header_and_section_layout(v89):
    image, report = v89
    base_v8, _ = combo.build(pe_extend.BASE_PATH.read_bytes(), "v8")
    old = pefile.PE(data=base_v8)
    new = pefile.PE(data=image)
    assert report["candidate_sha256"] == V89_SHA256
    assert new.FILE_HEADER.NumberOfSections == old.FILE_HEADER.NumberOfSections == 94
    assert new.OPTIONAL_HEADER.SizeOfHeaders == old.OPTIONAL_HEADER.SizeOfHeaders == 0x1000
    assert new.OPTIONAL_HEADER.SizeOfImage == old.OPTIONAL_HEADER.SizeOfImage
    assert len(image) == len(base_v8)


def test_supply_is_g8_and_owner_cap_is_official(v8):
    image, _ = v8
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    def insn(va):
        off = pe_extend.va_to_offset(image, va)
        return next(md.disasm(image[off : off + 16], va))
    assert insn(0x0043FE9E).op_str == "ecx, 0x1f4"  # 500 per living hero (G8)
    assert insn(0x0043EDB0).op_str == "ax, 0x3f0"  # official per-player cap 1008


def test_official_2613_selection_100_and_g7_loader_hook_are_preserved(base, v8):
    image, report = v8
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)

    def insn(data: bytes, va: int):
        off = pe_extend.va_to_offset(data, va)
        return next(md.disasm(data[off : off + 16], va))

    for va, op in (
        (0x0041DC68, "eax, 0x64"),
        (0x0041DDE4, "edi, 0x64"),
        (0x0041DE55, "edi, 0x64"),
        (0x0043877A, "ax, 0x64"),
        (0x016016D9, "ecx, 0x64"),
    ):
        assert insn(image, va).op_str == op
    hook = pe_extend.va_to_offset(base, 0x00441310)
    assert image[pe_extend.va_to_offset(image, 0x00441310) :][:5] == base[hook : hook + 5]
    assert report["layers"] == ["G2", "G6", "G8"]


def test_2613_kills_unit_pool_reference_is_relocated(v8):
    image, report = v8
    insn = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    insn.detail = True
    off = pe_extend.va_to_offset(image, 0x0115BFAB)
    site = next(insn.disasm(image[off : off + 8], 0x0115BFAB))
    assert site.disp == int(report["detail"]["g2"]["layer2"]["new_pool"], 16) + 0x8D


def test_save_load_wrapper_jumps_stay_inside_the_wrapper(v8):
    image, report = v8
    code_va = int(report["detail"]["g2"]["layer4"]["g2code_va"], 16)
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    md.detail = True
    off = pe_extend.va_to_offset(image, code_va + 0x100)
    for ins in md.disasm(image[off : off + 0x100], code_va + 0x100):
        if ins.mnemonic in ("jne", "jmp"):
            target = ins.operands[0].imm
            assert code_va + 0x100 <= target < code_va + 0x800
        if ins.mnemonic == "ret":
            break


def test_write_candidate_is_copy_only(base, tmp_path: Path):
    source = tmp_path / "in.exe"
    source.write_bytes(base)
    with pytest.raises(ValueError, match="overwrite"):
        combo.write_candidate(source, source, "v8")
    dest = tmp_path / "v8.exe"
    report = combo.write_candidate(source, dest, "v8")
    assert report["candidate_sha256"] == V8_SHA256
    assert source.read_bytes() == base
    with pytest.raises(FileExistsError):
        combo.write_candidate(source, dest, "v8")
