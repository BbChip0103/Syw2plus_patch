from pathlib import Path
import struct

import capstone
import pefile
import pytest

from patches.population import g2_full_capacity_persistence_v1 as mod
from patches.population.g2_full_capacity_supply5000_owner1200_v1 import (
    build_candidate as build_product_candidate,
)


ORIGINAL = Path(__file__).resolve().parents[2] / "Syw2plus" / "syw2plus_original.exe"


@pytest.fixture
def original() -> bytes:
    if not ORIGINAL.exists():
        pytest.skip("Local original game required")
    return ORIGINAL.read_bytes()


def _target(data: bytes, va: int) -> int:
    off = va - mod.IMAGE_BASE
    assert data[off] == 0xE8
    return va + 5 + struct.unpack_from("<i", data, off + 1)[0]


def test_n1200_adds_no_persistence_changes(original: bytes) -> None:
    candidate, report = mod.build_candidate(original, 1200)
    product, _product_report = build_product_candidate(original, 1200)
    assert candidate == product
    assert report["persistence_sidecar"] is False


def test_n4001_embeds_bounded_save_and_load_wrappers(original: bytes) -> None:
    candidate, report = mod.build_candidate(original, 4001)
    assert len(candidate) == len(original)
    assert _target(candidate, mod.SAVE_CALL_VA) == int(report["save_wrapper_va"], 16)
    assert _target(candidate, mod.LOAD_CALL_VA) == int(report["load_wrapper_va"], 16)
    assert struct.unpack_from("<H", candidate, mod.POSTLOAD_BOUND_VA - mod.IMAGE_BASE + 3)[0] == 4001
    assert [item["size"] for item in report["sidecars"]] == [8002, 8002, 16006, 16006, 8004]


def test_wrappers_call_original_stream_plus_five_sidecars(original: bytes) -> None:
    candidate, report = mod.build_candidate(original, 4001)
    pe = pefile.PE(data=candidate, fast_load=True)
    try:
        rsrc = next(s for s in pe.sections if s.Name.rstrip(b"\0") == b".rsrc")
        assert int(rsrc.Misc_VirtualSize) >= mod.RSRC_CODE_END_OFFSET
        assert int(rsrc.Characteristics) & mod.RSRC_EXECUTE_CODE_FLAGS == mod.RSRC_EXECUTE_CODE_FLAGS
        engine = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
        engine.detail = True
        for key, stream in (("save_wrapper_va", mod.SAVE_STREAM_FN), ("load_wrapper_va", mod.LOAD_STREAM_FN)):
            va = int(report[key], 16)
            off = int(rsrc.PointerToRawData) + va - (mod.IMAGE_BASE + int(rsrc.VirtualAddress))
            insns = list(engine.disasm(candidate[off : off + 0x100], va))
            calls = [insn.operands[0].imm for insn in insns if insn.mnemonic == "call"]
            assert calls[:6] == [stream] * 6
    finally:
        pe.close()


def test_rejects_wrong_original() -> None:
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        mod.build_candidate(b"not original", 4001)
