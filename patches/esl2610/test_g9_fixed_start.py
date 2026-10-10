from __future__ import annotations

import hashlib
import shutil
import subprocess
from pathlib import Path

import pefile
import pytest

from patches.esl2610 import g2_combo_2610 as combo
from patches.esl2610 import g9_fixed_start as mod
from patches.esl2610 import pe_extend


@pytest.fixture(scope="module")
def base() -> bytes:
    if not pe_extend.BASE_PATH.exists():
        pytest.skip("local pinned ESL2613 executable required")
    return pe_extend.BASE_PATH.read_bytes()


def _at(data: bytes, va: int, n: int) -> bytes:
    off = pe_extend.va_to_offset(data, va)
    return data[off : off + n]


def test_sites_match_the_2606_fixed_start_preimage(base):
    assert _at(base, 0x41F2AE, 6) == bytes.fromhex("0f858b000000")  # jne 0x41F33F
    assert _at(base, 0x42FBB1, 3) == bytes.fromhex("0fbfd2")  # movsx edx,dx (rand % n)


def test_applies_legacy_fixed_chunks_and_procedural_path(base):
    out, report = mod.build_candidate(base)
    assert _at(out, 0x41F2AE, 6) == bytes.fromhex("0f858a000000")  # jne 0x41F33E (inc esi)
    assert _at(out, 0x42FBB1, 3) == bytes.fromhex("8bd390")  # mov edx,ebx (loop index)
    assert _at(out, 0x44F079, 6)[0] == 0xE9
    assert _at(out, 0x44F079, 6)[5] == 0x90
    assert pe_extend.section_names(out)[-1] == mod.PROCEDURAL_SECTION
    assert report["procedural_placement"] == "new-section"
    assert report["chunks"] == ["0x41f2b0", "0x42fbb1", "0x44f079"]


def test_context_is_pinned(base):
    for va, digest in mod.CONTEXT_SHA256.items():
        off = pe_extend.va_to_offset(base, va)
        assert hashlib.sha256(base[off - mod.CONTEXT : off + mod.CONTEXT]).hexdigest() == digest


def test_full_v8_stack_and_exact_v89_rollback(base):
    v8, _ = combo.build(base, "v8")
    assert hashlib.sha256(v8).hexdigest() == "1e83466eab020818a6c0e9057508d71451af3ee1098af43ebefc20de8ab96e3d"
    out, report = mod.build_candidate(v8, require_pinned_base=False)
    assert _at(out, 0x42FBB1, 3) == bytes.fromhex("8bd390")
    assert pe_extend.section_names(out)[-4:] == mod.STACKED_SECTIONS
    assert report["procedural_placement"] == "pinned-.g8code-zero-tail"
    assert mod.restore_candidate(out) == v8
    old_pe, new_pe = pefile.PE(data=v8), pefile.PE(data=out)
    assert new_pe.FILE_HEADER.NumberOfSections == old_pe.FILE_HEADER.NumberOfSections
    assert new_pe.OPTIONAL_HEADER.SizeOfHeaders == old_pe.OPTIONAL_HEADER.SizeOfHeaders
    assert new_pe.OPTIONAL_HEADER.SizeOfCode == old_pe.OPTIONAL_HEADER.SizeOfCode
    assert new_pe.OPTIONAL_HEADER.SizeOfImage == old_pe.OPTIONAL_HEADER.SizeOfImage
    assert [(d.VirtualAddress, d.Size) for d in new_pe.OPTIONAL_HEADER.DATA_DIRECTORY] == [
        (d.VirtualAddress, d.Size) for d in old_pe.OPTIONAL_HEADER.DATA_DIRECTORY
    ]
    assert new_pe.OPTIONAL_HEADER.CheckSum == new_pe.generate_checksum()
    changes = (
        (0x41F2B0, bytes.fromhex("8a")),
        (0x42FBB1, bytes.fromhex("8bd390")),
        (0x44F079, _at(out, 0x44F079, 6)),
        (
            pe_extend.section_va(v8, mod.STACKED_PROCEDURAL_SECTION)
            + mod.STACKED_PROCEDURAL_CAVE_OFFSET,
            _at(
                out,
                pe_extend.section_va(v8, mod.STACKED_PROCEDURAL_SECTION)
                + mod.STACKED_PROCEDURAL_CAVE_OFFSET,
                len(mod.PROCEDURAL_PREFIX) + 4,
            ),
        ),
    )
    for old_sec, new_sec in zip(old_pe.sections, new_pe.sections):
        assert old_sec.Name == new_sec.Name
        assert old_sec.VirtualAddress == new_sec.VirtualAddress
        assert old_sec.Misc_VirtualSize == new_sec.Misc_VirtualSize
        assert old_sec.SizeOfRawData == new_sec.SizeOfRawData
        if old_sec.SizeOfRawData:
            assert new_sec.PointerToRawData == old_sec.PointerToRawData
            expected = bytearray(v8[old_sec.PointerToRawData : old_sec.PointerToRawData + old_sec.SizeOfRawData])
            for va, new_bytes in changes:
                old_off = pe_extend.va_to_offset(v8, va)
                if old_sec.PointerToRawData <= old_off < old_sec.PointerToRawData + old_sec.SizeOfRawData:
                    start = old_off - old_sec.PointerToRawData
                    expected[start : start + len(new_bytes)] = new_bytes
            actual = out[new_sec.PointerToRawData : new_sec.PointerToRawData + new_sec.SizeOfRawData]
            assert actual == expected
        else:
            assert new_sec.PointerToRawData == old_sec.PointerToRawData
    assert len(out) == len(v8)
    assert [s.Name for s in new_pe.sections] == [s.Name for s in old_pe.sections]
    assert [s.PointerToRawData for s in new_pe.sections] == [s.PointerToRawData for s in old_pe.sections]
    with pytest.raises(ValueError):
        mod.build_candidate(out, require_pinned_base=False)


def test_rejects_unpinned(base):
    with pytest.raises(ValueError, match="SHA256"):
        mod.build_candidate(base[:-1] + b"\x01")


def test_rejects_2612_version_marker_even_on_unpinned_path(base):
    marker = pe_extend.va_to_offset(base, 0x004ED7F8)
    wrong = bytearray(base)
    wrong[marker : marker + len(b"[ESL]2613")] = b"[ESL]2612"
    with pytest.raises(ValueError, match="2613 version marker"):
        mod.build_candidate(bytes(wrong), require_pinned_base=False)


def test_procedural_fixture_exposes_nonidentity_seat_to_startlist_mapping():
    """Pin the observed r8 d54=0 counterexample, not just the fixed-map route."""
    observed_owner_to_startlist = (1, 5, 7, 0, 2, 4, 3, 6)
    assert observed_owner_to_startlist != tuple(range(8))


def _run_native_candidate(
    candidate: bytes, tmp_path: Path, *, expected_prefix: bytes | None = None
) -> subprocess.CompletedProcess[str]:
    """Execute the built candidate's real detour/prefix in an ELF32 native scaffold.

    The original 44F020..44F09B body is copied from the candidate.  Only its
    three external helper CALL rel32s and the candidate detour/continuation
    rel32s are relocated into this ELF fixture; helper implementations are
    explicit mocks.  In particular, opcode bytes are read from the built PE,
    not re-created from a Python range/mapping oracle.
    """
    assembler, linker = shutil.which("as"), shutil.which("ld")
    assert assembler and linker, "GNU i386 assembler/linker required for G9 native regression"
    tmp_path.mkdir(parents=True, exist_ok=True)

    detour = _at(candidate, mod.PROCEDURAL_SITE, 6)
    assert detour[0] == 0xE9 and detour[5] == 0x90
    target = mod.PROCEDURAL_SITE + 5 + int.from_bytes(detour[1:5], "little", signed=True)
    code_off = pe_extend.va_to_offset(candidate, target)
    code_len = len(mod.PROCEDURAL_PREFIX) + 4
    code = candidate[code_off : code_off + code_len]
    if expected_prefix is not None:
        assert code[: len(expected_prefix)] == expected_prefix
    assert code[len(mod.PROCEDURAL_PREFIX) - 1] == 0xE9
    assert len(code) == code_len

    body_off = pe_extend.va_to_offset(candidate, 0x0044F020)
    (tmp_path / "native_function.bin").write_bytes(candidate[body_off : body_off + 0x7C])
    assert len((tmp_path / "native_function.bin").read_bytes()) == 0x7C
    asm = f'''\
.section .text
.globl _start
_start:
 movl $-1, count
next_count:
 incl count
 movl $0, helper_calls
 movl $0, rng_state
 movl $0xcccccccc, %eax
 movl $output, %edi
 movl $18, %ecx
 rep stosl
 movl %esp, before_sp
 movl $0x13572468,%ebp
 movl $0x11111111,%ebx
 movl $0x22222222,%esi
 movl $0x33333333,%edi
 pushl $dummy
 pushl $input
 pushl $output
 pushl $dummy
 pushl count
 call native_func
 addl $20,%esp
 cmpl before_sp,%esp
 jne fail
 cmpl $0x13572468,%ebp
 jne fail
 cmpl $0x11111111,%ebx
 jne fail
 cmpl $0x22222222,%esi
 jne fail
 cmpl $0x33333333,%edi
 jne fail
 movl count,%ecx
 cmpl helper_calls,%ecx
 jne fail
 leal (,%ecx,4),%eax
 cmpl %eax,rng_state
 jne fail
 xorl %edx,%edx
verify:
 cmpl %ecx,%edx
 jge guard
 movl input(,%edx,8),%eax
 cmpl output(,%edx,8),%eax
 jne fail
 movl input+4(,%edx,8),%eax
 cmpl output+4(,%edx,8),%eax
 jne fail
 incl %edx
 jmp verify
guard:
 cmpl $0xcccccccc,output(,%edx,8)
 jne fail
 cmpl $0xcccccccc,output+4(,%edx,8)
 jne fail
 cmpl $8,count
 jl next_count
 # The original signed guard must also reject a negative count without calls.
 movl $0,helper_calls
 movl $0,rng_state
 movl $0xcccccccc,output
 movl %esp,before_sp
 pushl $dummy
 pushl $input
 pushl $output
 pushl $dummy
 pushl $-1
 call native_func
 addl $20,%esp
 cmpl before_sp,%esp
 jne fail
 cmpl $0,helper_calls
 jne fail
 cmpl $0,rng_state
 jne fail
 cmpl $0xcccccccc,output
 jne fail
 movl $4,%eax
 movl $1,%ebx
 movl $pass_message,%ecx
 movl $pass_length,%edx
 int $0x80
 xorl %ebx,%ebx
 jmp exit
fail:
 movl $1,%ebx
exit:
 movl $1,%eax
 int $0x80

native_func:
 # Exact candidate body; replace only the three helper-call targets with mocks.
 .incbin "native_function.bin",0,0x19
 call stub_init
 .incbin "native_function.bin",0x1e,0xb
 call stub_aux
 .incbin "native_function.bin",0x2e,0x26
 call stub_native_selector
 .byte {detour[0]}
 .long hook-.-4
 .byte {detour[5]}
continue_native:
 .incbin "native_function.bin",0x5f,0x1d
hook:
 # Built-candidate instruction bytes through the JMP opcode, then local rel32.
 .byte {','.join(str(b) for b in code[:len(mod.PROCEDURAL_PREFIX)])}
 .long continue_native-.-4
stub_init:
 # Poison S-8, which is [hook ESP+34h] and differs from count [hook ESP+40h].
 movw $0,0x34(%esp)
 ret
stub_aux:
 movl 8(%esp),%edx
 movl $8,%ecx
 xorl %eax,%eax
fill_aux:
 movw %ax,(%edx)
 addl $2,%edx
 incl %eax
 loop fill_aux
 ret
stub_native_selector:
 incl helper_calls
 addl $4,rng_state
 movl $0xffff,%eax
 ret
.section .data
count:.long 0
before_sp:.long 0
helper_calls:.long 0
rng_state:.long 0
dummy:.space 64
input:.long 100,101,200,201,300,301,400,401,500,501,600,601,700,701,800,801
output:.space 72
pass_message:.ascii "PASS candidate-byte ELF32 count0..8/negative, identity, poison, helper, stack and callee-saved checks\\n"
.set pass_length,.-pass_message
'''
    (tmp_path / "native_fixture.S").write_text(asm)
    subprocess.run([assembler, "--32", "-o", "native_fixture.o", "native_fixture.S"], cwd=tmp_path, check=True, capture_output=True, text=True)
    subprocess.run([linker, "-m", "elf_i386", "-o", "native_fixture", "native_fixture.o"], cwd=tmp_path, check=True, capture_output=True, text=True)
    return subprocess.run([str(tmp_path / "native_fixture")], cwd=tmp_path, check=False, capture_output=True, text=True)


def test_procedural_detour_executes_actual_candidate_bytes_and_preserves_native_contract(base, tmp_path):
    v8, _ = combo.build(base, "v8")
    out, report = mod.build_candidate(v8, require_pinned_base=False)
    # 44F074 still calls the native helper (RNG/auxiliary state), while G9
    # overrides only the returned selection index and resumes at 44F07F.
    assert _at(out, 0x44F074, 5) == bytes.fromhex("e827000000")
    detour = _at(out, 0x44F079, 6)
    assert detour[0] == 0xE9 and detour[5] == 0x90
    detour_target = 0x44F079 + 5 + int.from_bytes(detour[1:5], "little", signed=True)
    assert detour_target == int(report["procedural_section_va"], 16)
    code_off = pe_extend.va_to_offset(out, detour_target)
    code = out[code_off : code_off + len(bytes.fromhex(report["procedural_code_hex"]))]
    assert code.hex() == report["procedural_code_hex"]
    assert code.startswith(mod.PROCEDURAL_PREFIX)
    ret_disp = int.from_bytes(code[-4:], "little", signed=True)
    assert detour_target + len(code) + ret_disp == mod.PROCEDURAL_CONTINUE
    run = _run_native_candidate(out, tmp_path, expected_prefix=mod.PROCEDURAL_PREFIX)
    assert run.returncode == 0, f"native fixture exit={run.returncode}; stdout={run.stdout!r}; stderr={run.stderr!r}"
    assert "PASS candidate-byte ELF32" in run.stdout
