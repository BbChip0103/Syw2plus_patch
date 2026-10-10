from __future__ import annotations

import pytest

from patches.esl2610 import g2_scan, pe_extend


@pytest.fixture(scope="module")
def base() -> bytes:
    if not pe_extend.BASE_PATH.exists():
        pytest.skip("local pinned ESL2610 executable required")
    return pe_extend.BASE_PATH.read_bytes()


@pytest.fixture(scope="module")
def inv(base):
    return g2_scan.build_inventory(base)


def test_rejects_unpinned_base():
    with pytest.raises(ValueError, match="SHA256"):
        g2_scan.build_inventory(b"\x00" * 4096)


def test_text_operand_classes_match_the_accepted_g2_relocation_set(inv):
    # Every .text operand into the six stock arrays, by class. These are the
    # same arrays/classes the accepted 2608/2606 G2 relocates; the counts are
    # pinned so a changed input or capstone build is caught.
    text = inv.by_section()[".text"]
    assert text["disp:pool"] == 983
    assert text["imm:pool"] == 30
    assert text["disp:exist"] == 32
    assert text["imm:exist"] == 2
    assert text["disp:age"] == 2
    assert text["imm:age"] == 3
    assert text["disp:cat_a"] == 19
    assert text["disp:cat_b"] == 2
    assert text["disp:active"] == 190
    assert text["imm:active"] == 72
    assert text["bound:N"] == 28


def test_new_sections_reference_the_stock_unit_arrays(inv):
    new_refs = [
        s for s in inv.sites if s.section not in (".text", ".rsrc") and s.op_kind != "bound"
    ]
    # 2610 new code genuinely addresses the stock pool/list arrays.
    assert len(new_refs) == 940
    sections = {s.section for s in new_refs}
    # The large compiled-C blob and several AI modules are all implicated.
    for name in (".a16code", ".n14code", ".r17code", ".kills", ".idle", ".hrcode", ".psncode"):
        assert name in sections


def test_2613_kills_pool_reference_is_in_inventory():
    official = pe_extend.REPO.parent / "patch_history"
    previous = official / "[ESL]Syw2plus 2612" / "[ESL]Syw2plus 2612.exe"
    image = (official / "[ESL]Syw2plus 2613.exe").read_bytes()
    inv2613 = g2_scan.build_inventory(image, require_pinned_base=False)
    inv2612 = g2_scan.build_inventory(previous.read_bytes(), require_pinned_base=False)
    site = next(s for s in inv2613.sites if s.va == 0x0115BFAB)
    assert (site.section, site.op_kind, site.region, site.value) == (
        ".kills", "disp", "pool", 0x0066B81D
    )
    assert len(inv2613.sites) == len(inv2612.sites) + 1
    assert inv2613.by_section()[".kills"]["disp:pool"] == inv2612.by_section()[".kills"]["disp:pool"] + 1
    assert inv2613.to_report()["unresolved_count"] == inv2612.to_report()["unresolved_count"] == 3
    unresolved_2612 = {x["kind"]: x["count"] for x in inv2612.to_report()["unresolved"]}
    unresolved_2613 = {x["kind"]: x["count"] for x in inv2613.to_report()["unresolved"]}
    assert unresolved_2613.keys() == unresolved_2612.keys()
    assert unresolved_2613 == {
        **unresolved_2612,
        "new_code_unit_capacity_refs": unresolved_2612["new_code_unit_capacity_refs"] + 1,
    }


def test_negative_pool_base_pointer_to_index_form_is_detected(inv):
    negs = [s for s in inv.sites if s.op_kind == "neg_pool_base"]
    # `lea reg,[unit - 0x66B790]` then divide-by-stride is how new modules turn
    # a UnitStruct pointer into a slot index; these must track pool relocation.
    assert negs, "expected pointer->index (-pool_base) sites in new code"
    assert all((-s.value) & 0xFFFFFFFF == g2_scan.POOL[0] for s in negs)


def test_capacity_bound_checks_are_enumerated(inv):
    bounds = [s for s in inv.sites if s.op_kind == "bound"]
    assert len(bounds) == 262
    # The pool byte-span bound 0x758*1200 is used as a pointer-range guard.
    assert any(s.value == 0x226C80 for s in bounds)
    assert any(s.region == "N" for s in bounds)  # plain 1200 slot bound


def test_new_perunit_bss_sized_to_1200_detected(inv):
    pu = {b["section"]: b for b in inv.new_perunit_bss if b["looks_per_unit"]}
    # These eight are clean header + stride*1200 per-unit arrays; each must grow
    # to 4093. (Composite/direct-indexed arrays such as .killdat are additionally
    # caught by their code references, not necessarily by this size heuristic.)
    for name, stride in (
        (".wecache", "0x10"),
        (".idldata", "0x8"),
        (".skstate", "0x18"),
        (".mvstate", "0x28"),
        (".hrstate", "0x44"),
        (".cpstate", "0x30"),
        (".healst", "0x28"),
        (".rsidle", "0x10"),
    ):
        assert name in pu, name
        assert pu[name]["stride_if_perunit"] == stride


def test_inventory_is_fail_closed_on_2610(inv):
    report = inv.to_report()
    assert report["release_status"] == "BLOCKED"
    kinds = {u["kind"] for u in report["unresolved"]}
    assert kinds == {
        "new_code_unit_capacity_refs",
        "capacity_bound_checks",
        "new_perunit_bss_sized_1200",
    }
