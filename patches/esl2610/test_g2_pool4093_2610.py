from __future__ import annotations

from pathlib import Path

import pytest

from patches.esl2610 import g2_pool4093_2610 as mod
from patches.esl2610 import pe_extend

G2_SHA256 = "9d2179c4b4b91e8d3fe4d7aebfc152723f6c2025323ee784aaefd08008c18d90"


@pytest.fixture(scope="module")
def base() -> bytes:
    if not pe_extend.BASE_PATH.exists():
        pytest.fail("pinned official 2613 EXE missing: the G2 build cannot be verified here")
    return pe_extend.BASE_PATH.read_bytes()


def test_capacity_contract():
    assert mod.CAPACITY == 4093
    assert mod.USABLE_SLOTS == 4092
    assert mod.USABLE_SLOTS <= 0x0FFF  # 12-bit command-slot ceiling


def test_build_resolves_every_inventory_class(base):
    if not mod.STOCK_ORACLE.exists():
        pytest.fail("stock oracle EXE missing: the G2 build cannot be verified here")
    candidate, report = mod.build_candidate(base)
    assert set(report["inventory_resolved_by"]) == {
        "new_code_unit_capacity_refs", "capacity_bound_checks", "new_perunit_bss_sized_1200"}
    assert report["candidate_sha256"] == G2_SHA256
    assert pe_extend.section_names(candidate)[-2:] == [b".g2bss", b".g2code"]


def test_build_is_blocked_without_the_stock_oracle(base, monkeypatch, tmp_path):
    monkeypatch.setattr(mod, "STOCK_ORACLE", tmp_path / "missing.exe")
    with pytest.raises(mod.G2BuildBlocked) as excinfo:
        mod.build_candidate(base)
    assert any(u["kind"] == "stock_oracle_missing" for u in excinfo.value.report["unresolved"])


def test_rejects_unpinned_base():
    with pytest.raises(ValueError, match="SHA256"):
        mod.build_candidate(b"\x00" * 8192)


def test_create_copy_refuses_to_overwrite_input(base, tmp_path: Path):
    source = tmp_path / "in.exe"
    source.write_bytes(base)
    with pytest.raises(ValueError, match="overwrite"):
        mod.create_copy(source, source)
