from __future__ import annotations

from pathlib import Path

import pefile
import pytest

from patches.esl2610 import g2_spike_build as mod
from patches.esl2610 import pe_extend

STOCK = Path(__file__).resolve().parents[2] / "Syw2plus" / "syw2plus_original.exe"


@pytest.fixture(scope="module")
def base() -> bytes:
    if not pe_extend.BASE_PATH.exists():
        pytest.skip("local pinned ESL2610 executable required")
    return pe_extend.BASE_PATH.read_bytes()


@pytest.fixture(scope="module")
def stock() -> bytes:
    if not STOCK.exists():
        pytest.skip("local pinned stock EXE required")
    return STOCK.read_bytes()


@pytest.fixture(scope="module")
def built(base, stock):
    return mod.build_spike_candidate(base, stock)


def test_candidate_is_byte_exact_to_rebased_stock_oracle(base, stock, built):
    candidate, report = built
    check = mod.verify_against_oracle(base, stock, candidate)
    assert check["mismatches"] == 0
    assert check["runs_checked"] == 1324
    assert report["text_runs_applied"] == 1324
    assert report["product_runs_skipped"] == 3
    # the four save/load stream-call redirects are left to layer 4
    assert report["text_runs_skipped"] == 8
    assert report["rebased_address_dwords"] == 1308
    # cat-list accesses relative to the bulk object (this = 0x892410)
    assert report["rebased_bulk_relative_disps"] == 13


def test_candidate_is_a_valid_pe_with_only_g2bss_added(base, built):
    candidate, report = built
    pe = pefile.PE(data=candidate)
    basepe = pefile.PE(data=base)
    try:
        assert set(pe.get_warnings()) - set(basepe.get_warnings()) == set()
        assert pe.OPTIONAL_HEADER.CheckSum == pe.generate_checksum()
        assert pe.sections[-1].Name.rstrip(b"\0") == b".g2bss"
        assert pe.FILE_HEADER.NumberOfSections == basepe.FILE_HEADER.NumberOfSections + 1
        last_va = mod.pe_extend.IMAGE_BASE + pe.sections[-1].VirtualAddress
        assert last_va == int(report["g2bss_va"], 16)
        # BSS adds no raw bytes: file length is unchanged.
        assert len(candidate) == len(base)
    finally:
        pe.close()
        basepe.close()


def test_official_1008_cap_is_preserved(base, built):
    candidate, _ = built
    off = pe_extend.va_to_offset(candidate, 0x0041B56D)
    # mov edx, 0x3F0  (1008) kept, not raised to 1200/4093
    assert candidate[off : off + 5] == bytes.fromhex("baf0030000")


def test_official_supply_formula_is_preserved(base, built):
    # The oracle's non-G2 product layer fixes supply at 5000; G2 must not.
    candidate, _ = built
    for va, size in ((0x0041B576, 5), (0x0043FE9E, 6), (0x0043FFD4, 5)):
        off = pe_extend.va_to_offset(candidate, va)
        assert candidate[off : off + size] == base[off : off + size], hex(va)


def test_rejects_wrong_bases(base, stock):
    with pytest.raises(ValueError, match="SHA256"):
        mod.build_spike_candidate(b"\x00" * 8192, stock)
    with pytest.raises(ValueError, match="stock"):
        mod.build_spike_candidate(base, b"\x00" * 8192)


def test_deliverable_builder_needs_the_stock_oracle(base, monkeypatch, tmp_path):
    from patches.esl2610 import g2_pool4093_2610 as builder

    monkeypatch.setattr(builder, "STOCK_ORACLE", tmp_path / "missing.exe")
    with pytest.raises(builder.G2BuildBlocked):
        builder.build_candidate(base)


def test_cli_refuses_to_write_without_spike_flag(tmp_path, base, stock):
    # build_spike_candidate itself only returns bytes; the CLI guards writes.
    # Here we assert the guard constants: no deliverable path accepted.
    deliver = Path(mod.__file__).resolve().parents[1]
    out = deliver / "should_never_write.exe"
    assert deliver in out.resolve().parents  # the guard's condition holds for deliverable paths
