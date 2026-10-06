from __future__ import annotations

from tools import g7_save_load_probe as probe


def test_first_match_index_is_the_first_slot_holding_the_own_id() -> None:
    assert probe.first_match_index([5, 5, 7, 7], 7) == 2
    assert probe.first_match_index([1, 1, 1], 9) is None


def test_repair_class_is_r1_only_when_the_table_still_yields_the_saved_seat() -> None:
    assert probe.classify_repair([5, 5, 7, 7, 7, 7, 7, 7], 7, 2) == "R1"
    assert probe.classify_repair([7] * 8, 7, 2) == "R2"  # first match 0, saved seat 2
    assert probe.classify_repair([1] * 8, 7, 2) == "R2"  # no match at all


def test_save_slot_index_follows_the_title_list_numbering() -> None:
    assert probe.title_list_index("save001.dat") == 2
    assert probe.title_list_index("save006.dat") == 7


def test_owner_tally_counts_live_units_per_owner() -> None:
    rows = [{"owner": 2, "hp": 10}, {"owner": 2, "hp": 5}, {"owner": 0, "hp": 1}, {"owner": 3, "hp": 0}]
    assert probe.owner_tally(rows) == {0: 1, 2: 2}


def test_defect_needs_local_zero_with_a_nonzero_saved_seat_and_a_visible_symptom() -> None:
    kw = {"ps_seen": [3], "selected_owners": [2], "owner_units": 9}
    assert not probe.defect_reproduced(local=2, seat=2, **kw)
    assert not probe.defect_reproduced(local=0, seat=2, **kw)  # local 0 but no symptom, owner 2 still selectable
    assert probe.defect_reproduced(local=0, seat=2, **{**kw, "ps_seen": [3, 27]})
    assert probe.defect_reproduced(local=0, seat=2, **{**kw, "selected_owners": [0, 0]})
    assert probe.defect_reproduced(local=0, seat=2, **{**kw, "selected_owners": []})
    assert not probe.defect_reproduced(local=0, seat=2, **{**kw, "selected_owners": [], "owner_units": 0})


def test_repair_verdict_requires_seat_local_clean_ps_and_only_own_units_selected() -> None:
    ok = probe.repair_verdict(local=2, seat=2, ps_seen=[3], selected_owners=[2, 2, 2])
    assert ok == {"local_is_seat": True, "ps_clean": True, "selection_owned": True, "repaired": True}
    assert not probe.repair_verdict(local=0, seat=2, ps_seen=[3], selected_owners=[2])["repaired"]
    assert not probe.repair_verdict(local=2, seat=2, ps_seen=[3, 27, 29], selected_owners=[2])["ps_clean"]
    assert not probe.repair_verdict(local=2, seat=2, ps_seen=[3], selected_owners=[2, 0])["selection_owned"]
    assert not probe.repair_verdict(local=2, seat=2, ps_seen=[3], selected_owners=[])["selection_owned"]  # nothing selected


def test_repair_verdict_covers_the_solo_seat_zero_regression() -> None:
    assert probe.repair_verdict(local=0, seat=0, ps_seen=[3], selected_owners=[0, 0])["repaired"]


def test_candidate_variants_install_the_g7_patch_with_or_without_g6() -> None:
    from patches.selection import g6_shift_click_count_bound as g6
    from patches.selection import g7_title_load_seat_restore as g7

    if not probe.PORT_EXE.is_file():
        import pytest

        pytest.skip("pinned G5 port executable is required")
    port = probe.PORT_EXE.read_bytes()
    g7_only, report7 = probe._install("cand")
    assert g7_only == g7.build_candidate(port)[0] and report7["stacked_on_g6"] is False
    g67, report67 = probe._install("cand67")
    assert g67 == g7.build_candidate(g6.build_candidate(port)[0])[0] and report67["stacked_on_g6"] is True
    assert probe._install("port")[0] == port
    assert probe.layout_key("cand67") == "port" and probe.layout_key("orig") == "orig"


def test_fixed_start_port_installs_the_pinned_fixed_start_stack() -> None:
    import pytest

    from patches.selection import g6_shift_click_count_bound as g6
    from patches.selection import g7_title_load_seat_restore as g7

    exe = probe.PORT_EXES["fixed_start"]
    assert probe.PORT_EXES["normal"] == probe.PORT_EXE
    with pytest.raises(probe.ProbeError):
        probe._install("cand67", port="bogus")
    if not exe.is_file():
        pytest.skip("pinned fixed_start G5 port executable is required")
    assert probe.sha256(exe) == g6.PORT_SHA256["fixed_start"]
    base = exe.read_bytes()
    stacked, report = probe._install("cand67", port="fixed_start")
    assert stacked == g7.build_candidate(g6.build_candidate(base)[0])[0] and report["stacked_on_g6"] is True
    assert probe._install("port", port="fixed_start")[0] == base


def test_parse_actions_accepts_known_kinds_and_fixture_names_only() -> None:
    import pytest

    assert probe.parse_actions("ingame:S0, title:S2 ,pause-shot") == ["ingame:S0", "title:S2", "pause-shot"]
    assert probe.parse_actions("") == []
    for bad in ("ingame:S9", "load:S0", "title", "pause-shot:S0"):
        with pytest.raises(probe.ProbeError):
            probe.parse_actions(bad)


def test_parse_clicks_reads_semicolon_separated_points() -> None:
    assert probe.parse_clicks("400,306;400,300") == [(400, 306), (400, 300)]
    assert probe.parse_clicks("") == []


def test_cross_scenario_rejects_missing_actions_and_missing_fixtures(tmp_path) -> None:
    import pytest

    with pytest.raises(probe.ProbeError):
        probe.run_probe("port", 2, tmp_path / "rt", tmp_path / "art", scenario="x")
    with pytest.raises(probe.ProbeError):
        probe.run_probe("port", 2, tmp_path / "rt", tmp_path / "art", scenario="x", actions=["ingame:S0"],
                        saves={"S0": tmp_path / "missing.dat"})
    assert not (tmp_path / "art").exists()


def test_expected_seat_names_the_fixture_seats() -> None:
    assert probe.EXPECTED_SEAT == {"S0": 0, "S2": 2}


def test_cand_r5_variant_installs_g6_plus_the_save_trailer_without_r4b() -> None:
    import pytest

    from patches.selection import g6_shift_click_count_bound as g6
    from patches.selection import g7_save_trailer_local_restore as r5
    from patches.selection import g7_title_load_seat_restore as r4b

    if not probe.PORT_EXE.is_file():
        pytest.skip("pinned G5 port executable is required")
    port = probe.PORT_EXE.read_bytes()
    exe, report = probe._install("cand-r5")
    assert exe == r5.build_candidate(g6.build_candidate(port)[0])[0] and report["stacked_on_g6"] is True
    assert exe != r4b.build_candidate(g6.build_candidate(port)[0])[0]
    assert "cand-r5" in probe.VARIANTS and probe.layout_key("cand-r5") == "port"


def test_overwrite_snapshot_is_only_for_the_observe_scenario_without_an_existing_save(tmp_path) -> None:
    import pytest

    with pytest.raises(probe.ProbeError):
        probe.run_probe("cand-r5", 2, tmp_path / "rt", tmp_path / "art", scenario="x", actions=["ingame:S0"],
                        overwrite_snapshot=True)
    save = tmp_path / "s.dat"
    save.write_bytes(b"x")
    with pytest.raises(probe.ProbeError):
        probe.run_probe("cand-r5", 2, tmp_path / "rt", tmp_path / "art", existing_save=save, overwrite_snapshot=True)
    assert not (tmp_path / "art").exists()
