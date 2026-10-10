from __future__ import annotations

import hashlib
from pathlib import Path
import struct

import pefile
import pytest

from patches.selection import g6_shift_click_count_bound as mod

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT.parent / "260921_temp" / "archive"
PORT = {
    "normal": INPUT / "[ESL]Syw2plus 2608_AI상점개설_장수7명_전비1500-500-5000_G2_개인500_공용4092_G5_선택50_시험용.exe",
    "fixed_start": INPUT
    / "[ESL]Syw2plus 2608_AI상점개설_장수7명_전비1500-500-5000_시작자리고정_G2_개인500_공용4092_G5_선택50_시험용.exe",
}
PORT_SHA = {
    "normal": "0e28ef57f8eb1f674df544ef84889bd2c51224720a09d0a18122e55f8399d257",
    "fixed_start": "703deaf4c07b44975417f6835c569d65fa03adc2272ff6c75866da4723cd6ea0",
}
CANDIDATE_SHA = {
    "normal": "b50af2a615354fc90d5438137a374c909850bf8d308761c9b5b4750b426b2f4f",
    "fixed_start": "7c891658a58d3f837a47e7dc8fc74dbd0bb3739030182f04b7f13091f97f64b5",
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
    assert report["candidate_sha256"] == hashlib.sha256(candidate).hexdigest()
    assert report["candidate_sha256"] == CANDIDATE_SHA[variant]
    again, _ = mod.build_candidate(base)
    assert again == candidate


@pytest.mark.parametrize("variant", list(PORT))
def test_diff_is_hook_site_plus_cave_only(variant: str, built: dict) -> None:
    base, candidate, _report = built[variant]
    assert len(candidate) == len(base)
    hook = _file_offset(base, mod.HOOK_VA)
    cave = _file_offset(base, mod.CAVE_VA)
    allowed = set(range(hook, hook + 8)) | set(range(cave, cave + len(mod.CAVE_TEMPLATE)))
    changed = {i for i in range(len(base)) if base[i] != candidate[i]}
    assert changed and changed <= allowed
    assert candidate[hook : hook + 8] == b"\xe9" + struct.pack("<i", mod.CAVE_VA - (mod.HOOK_VA + 5)) + b"\x90\x90\x90"


@pytest.mark.parametrize("variant", list(PORT))
def test_cave_bounds_loop_by_count_and_resumes_original_flow(variant: str, built: dict) -> None:
    _base, candidate, _report = built[variant]
    cave = _file_offset(candidate, mod.CAVE_VA)
    body = candidate[cave : cave + len(mod.CAVE_TEMPLATE)]
    assert body[:4] == b"\x3b\x7c\x24\x10"  # cmp edi,[esp+0x10]
    assert body[4:6] == b"\x0f\x8d"
    assert mod.CAVE_VA + 10 + struct.unpack_from("<i", body, 6)[0] == mod.LOOP_EXIT_VA
    assert body[10:13] == b"\x66\x8b\x06"  # mov ax,[esi]
    assert body[13:18] == b"\xb9\x6c\xe3\x61\x00"  # mov ecx,0x61E36C
    assert body[18] == 0xE9
    assert mod.CAVE_VA + 23 + struct.unpack_from("<i", body, 19)[0] == mod.LOOP_RESUME_VA


@pytest.mark.parametrize("variant", list(PORT))
def test_cave_lies_in_zero_tail_of_g5code_and_overlaps_no_port_cave(variant: str, built: dict) -> None:
    base, _candidate, _report = built[variant]
    section = _file_offset(base, mod.G5CODE_VA)
    tail = base[section + 0x900 : section + 0x1000]
    assert not any(tail), "port .g5code tail must be zero"
    assert mod.G5CODE_VA + 0x900 <= mod.CAVE_VA
    assert mod.CAVE_VA + len(mod.CAVE_TEMPLATE) <= mod.G5CODE_VA + 0x1000
    pe = pefile.PE(data=base)
    names = [s.Name.rstrip(b"\0") for s in pe.sections]
    assert names[-1] == b".g5code"


@pytest.mark.parametrize("variant", list(PORT))
def test_no_other_instruction_branches_into_cave(variant: str, built: dict) -> None:
    _base, candidate, _report = built[variant]
    needle = struct.pack("<I", mod.CAVE_VA)
    # Absolute references: only zero allowed outside the hook's own rel32 (not an abs32).
    assert candidate.count(needle) == 0


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
