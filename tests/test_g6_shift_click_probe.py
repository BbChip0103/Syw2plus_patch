from __future__ import annotations

import hashlib

from tools import g6_shift_click_probe as probe

UNIT_OWNER_OFFSET = 0x8E


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def test_slot0_owner_addresses_match_the_disassembled_owner_lookup() -> None:
    """0x40F560(id 0) reads the owner byte of pool slot 0: original 0x66B81E, G2 port 0x112E08E."""
    _sel, _cap, pool, _exists, _capacity = probe.LAYOUTS["orig"]
    assert pool + UNIT_OWNER_OFFSET == 0x0066B81E
    for variant in ("port", "cand"):
        _sel, _cap, pool, _exists, _capacity = probe.LAYOUTS[variant]
        assert pool + UNIT_OWNER_OFFSET == 0x0112E08E


def test_selection_layouts_follow_each_variant_storage() -> None:
    assert probe.LAYOUTS["orig"][:2] == (0x00899024, 20)
    assert probe.LAYOUTS["port"][:2] == (0x018A6000, 50)
    assert probe.LAYOUTS["cand"][:2] == probe.LAYOUTS["port"][:2]
    assert probe.LAYOUTS["cand67"] == probe.LAYOUTS["cand"]


def test_cand67_installs_the_g6_patch_stacked_with_the_g7_patch() -> None:
    from patches.selection import g6_shift_click_count_bound as g6
    from patches.selection import g7_title_load_seat_restore as g7

    if not probe.PORT_EXE.is_file():
        import pytest

        pytest.skip("pinned G5 port executable is required")
    port = probe.PORT_EXE.read_bytes()
    g6_only, _report = probe._install("cand")
    assert g6_only == g6.build_candidate(port)[0]
    stacked, report = probe._install("cand67")
    assert stacked == g7.build_candidate(g6.build_candidate(port)[0])[0] and stacked != g6_only
    assert report["stacked_on_g6"] is True


def test_fixture_screen_layout_stays_inside_the_viewport_above_the_hud() -> None:
    for x, y in [(x, y) for y in probe.SPARSE_ROWS for x in probe.SPARSE_COLS]:
        assert 5 <= x <= 795 and 45 <= y <= 470
    for x, y in [(x, y) for y in probe.DENSE_ROWS for x in probe.DENSE_COLS]:
        assert 5 <= x <= 795 and 45 <= y <= 470
    # Sparse neighbours are at least a sprite apart so a single click cannot hit two units.
    assert min(b - a for a, b in zip(probe.SPARSE_COLS, probe.SPARSE_COLS[1:])) >= 80
    assert min(b - a for a, b in zip(probe.SPARSE_ROWS, probe.SPARSE_ROWS[1:])) >= 60


def _solo_table(own: int = 0x1234) -> bytes:
    table = bytearray(probe.LOBBY_TABLE_SIZE)
    for i in range(probe.LOBBY_SLOTS):
        off = probe.LOBBY_ID_OFFSET + i * 4
        table[off:off + 4] = own.to_bytes(4, "little")
        row = (5 if i < 2 else 0, i, 0 if i == 0 else 1, 1 << i, 0, i)
        table[probe.LOBBY_ROW_OFFSET + i * 6:probe.LOBBY_ROW_OFFSET + i * 6 + 6] = bytes(row)
        table[probe.LOBBY_DWORD_OFFSET + i * 4:probe.LOBBY_DWORD_OFFSET + i * 4 + 4] = (100 + i).to_bytes(4, "little")
        table[probe.LOBBY_NAME_OFFSET + i * 15:probe.LOBBY_NAME_OFFSET + i * 15 + 15] = f"n{i}".encode().ljust(15, b"\0")
    return bytes(table)


def test_lobby_table_offsets_match_the_disassembled_arrays() -> None:
    assert probe.LOBBY_TABLE_VA + probe.LOBBY_ID_OFFSET == 0x632CA0
    assert probe.LOBBY_TABLE_VA + probe.LOBBY_ROW_OFFSET == 0x632CC0
    assert probe.LOBBY_TABLE_VA + probe.LOBBY_DWORD_OFFSET == 0x632CF0
    assert probe.LOBBY_TABLE_VA + probe.LOBBY_NAME_OFFSET == 0x632D94
    assert probe.LOBBY_TABLE_VA + probe.LOBBY_TABLE_SIZE == probe.LOBBY_SNAPSHOT_VA  # 0x4B7700 copies 0x5C dwords


def test_lobby_snapshot_makes_the_first_own_id_match_the_requested_seat() -> None:
    table = _solo_table()
    snapshot, ids = probe.build_lobby_snapshot(table, 2)
    assert len(snapshot) == probe.LOBBY_TABLE_SIZE and ids == {"own_id": 0x1234, "other_id": 0x1235}
    entries = [int.from_bytes(snapshot[4 + i * 4:8 + i * 4], "little") for i in range(probe.LOBBY_SLOTS)]
    assert entries.index(0x1234) == 2  # 0x43AF40 picks the first matching index
    row = probe.LOBBY_ROW_OFFSET
    # seat 0 (human) and seat 2 (none) trade type/flag bytes; index and mask bytes stay with their rows
    assert snapshot[row:row + 6] == bytes([0, 0, 1, 1, 0, 0])
    assert snapshot[row + 12:row + 18] == bytes([5, 2, 0, 4, 0, 2])
    name = probe.LOBBY_NAME_OFFSET
    assert snapshot[name + 30:name + 45] == table[name:name + 15] and snapshot[name:name + 15] == table[name + 30:name + 45]
    dword = probe.LOBBY_DWORD_OFFSET
    assert snapshot[dword + 8:dword + 12] == table[dword:dword + 4]


def test_lobby_snapshot_rejects_seat_zero_and_wrong_size() -> None:
    import pytest

    with pytest.raises(probe.ProbeError):
        probe.build_lobby_snapshot(_solo_table(), 0)
    with pytest.raises(probe.ProbeError):
        probe.build_lobby_snapshot(b"\0" * 4, 1)


def test_panel_diff_counts_only_the_seat_panel(tmp_path) -> None:
    from PIL import Image

    a, b = tmp_path / "a.png", tmp_path / "b.png"
    Image.new("RGB", (800, 600)).save(a)
    img = Image.new("RGB", (800, 600))
    img.putpixel((10, 10), (255, 0, 0))
    img.putpixel((300, 500), (255, 0, 0))  # outside the left seat panel
    img.save(b)
    assert probe.panel_changed_pixels(a, b) == 1


def test_lobby_snapshot_uses_the_runtime_own_id_when_it_differs_from_the_table() -> None:
    snapshot, ids = probe.build_lobby_snapshot(_solo_table(1), 3, own_id=0)
    entries = [int.from_bytes(snapshot[4 + i * 4:8 + i * 4], "little") for i in range(probe.LOBBY_SLOTS)]
    assert ids == {"own_id": 0, "other_id": 1} and entries[:4] == [1, 1, 1, 0]


def test_key_focus_constants_match_the_disassembled_key_state_and_queue() -> None:
    """0x421630 sets word [0x61E070+vk*2]; VK_UP 0x26 and VK_DOWN 0x28; 0x4216B0 counts the queue at 0x61E270."""
    assert probe.KEY_STATE_BASE_VA + 0x26 * 2 == 0x61E0BC
    assert probe.KEY_STATE_BASE_VA + 0x28 * 2 == 0x61E0C0
    assert probe.KEY_QUEUE_COUNT_VA == 0x61E270
    assert [name for name, _ in probe.KEY_FOCUS_VARIANTS] == ["f0", "f1", "f2", "f3", "f4", "f5", "f6"]


def _step(word: int, table_changed: bool = False, local: int = 0) -> dict:
    return {"key": "Down", "key_state": word, "queue_before": 0, "queue_during": word,
            "table_changed": table_changed, "local_index": local}


def test_key_focus_verdict_separates_delivery_from_seat_move() -> None:
    assert probe.key_focus_verdict([_step(0), _step(0)]) == {"k1_delivered": False, "k2_moved": False}
    assert probe.key_focus_verdict([_step(1), _step(0)]) == {"k1_delivered": True, "k2_moved": False}
    assert probe.key_focus_verdict([_step(1, True, 1)]) == {"k1_delivered": True, "k2_moved": True}
    # a table change without a new local, or a local without a table change, is not a seat move
    assert probe.key_focus_verdict([_step(1, True, 0)])["k2_moved"] is False
    assert probe.key_focus_verdict([_step(1, False, 2)])["k2_moved"] is False


def test_changed_pixels_accepts_the_chat_line_box(tmp_path) -> None:
    from PIL import Image

    a, b = tmp_path / "a.png", tmp_path / "b.png"
    Image.new("RGB", (800, 600)).save(a)
    img = Image.new("RGB", (800, 600))
    img.putpixel((300, 505), (255, 255, 255))  # inside the chat input line
    img.putpixel((10, 10), (255, 0, 0))  # seat panel only
    img.save(b)
    assert probe.panel_changed_pixels(a, b, probe.LOBBY_CHAT_BOX) == 1
    assert probe.panel_changed_pixels(a, b) == 1


def test_install_defaults_to_the_normal_port_and_rejects_unknown_ports() -> None:
    import pytest

    if not probe.PORT_EXE.is_file():
        pytest.skip("pinned G5 port executable is required")
    port_bytes, report = probe._install("port")
    assert _sha(port_bytes) == report["sha256"] == probe.g6_patch.PORT_SHA256["normal"]
    assert probe._install("port", "normal")[0] == port_bytes
    with pytest.raises(probe.ProbeError):
        probe._install("port", "bogus")


def test_install_fixed_start_port_builds_the_pinned_candidates() -> None:
    import pytest

    if not probe.PORT_EXES["fixed_start"].is_file():
        pytest.skip("pinned fixed-start G5 port executable is required")
    port_bytes, report = probe._install("port", "fixed_start")
    assert _sha(port_bytes).startswith("703deaf4") and report["sha256"].startswith("703deaf4")
    assert _sha(probe._install("cand", "fixed_start")[0]).startswith("7c891658a58d3f83")
    assert _sha(probe._install("cand67", "fixed_start")[0]).startswith("58b9b22a")
    assert probe._install("orig", "fixed_start")[0] is None  # the original ignores the port


def test_scroll_keys_parse_arrow_holds_and_reject_bad_specs() -> None:
    import pytest

    assert probe.parse_scroll_keys("") == []
    assert probe.parse_scroll_keys("Down:2.5, Right:1") == [("Down", 2.5), ("Right", 1.0)]
    for bad in ("Space:1", "Down", "Down:0", "Down:11"):
        with pytest.raises(probe.ProbeError):
            probe.parse_scroll_keys(bad)


def test_esl2610_variants_use_original_pool_and_moved_100_slot_selection() -> None:
    from tools import esl2610_runtime as rt

    assert probe.LAYOUTS["base2610"] == probe.LAYOUTS["cand2610"] == (0x00899024, 100, 0x0066B790, 0x008990C8, 1200)
    assert rt.SELECTION_ENTRIES_VA == 0x01604004


def test_esl2610_install_builds_candidate_from_the_pinned_exe() -> None:
    import pytest
    from patches.esl2610 import g6_shift_click_2610 as g6

    if not probe.esl2610_runtime.ESL2610_EXE.is_file():
        pytest.skip("pinned ESL2610 executable is required")
    base_bytes, base_report = probe._install("base2610")
    assert _sha(base_bytes) == probe.esl2610_runtime.ESL2610_SHA256 == base_report["sha256"]
    cand, _report = probe._install("cand2610")
    assert cand == g6.build_candidate(base_bytes)[0] and cand != base_bytes
