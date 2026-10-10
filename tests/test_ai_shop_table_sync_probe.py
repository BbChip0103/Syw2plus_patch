"""Pure-helper contracts for the shop-table-sync Wine probe (no Wine, no game)."""

from __future__ import annotations

import pytest

from tools import ai_shop_table_sync_probe as probe

ROW = probe.ROW
OLD_LEN = probe.sync_patch.COPY_LEN


def _fixture() -> tuple[bytes, bytes]:
    old = bytes((i * 7) % 251 for i in range(OLD_LEN))
    tail = b"\x0f\x00\x30\x00" + bytes(ROW * 3 - 4) + b"\xfe\xff"
    return old, tail


def _source() -> bytes:
    old, tail = _fixture()
    data = bytearray(probe.sync_patch.SHOPAI_FILE_OFFSET + probe.sync_patch.SHOPAI_RAW_SIZE)
    data[probe.sync_patch.OLD_TABLE_FILE_OFFSET : probe.sync_patch.OLD_TABLE_FILE_OFFSET + OLD_LEN] = old
    base = probe.sync_patch.SHOPAI_FILE_OFFSET
    data[base : base + OLD_LEN] = old
    data[base + OLD_LEN : base + OLD_LEN + len(tail)] = tail
    return bytes(data)


def test_marker_edit_changes_only_old_row_field() -> None:
    src = _source()
    out, info = probe.marker_edit(src, 3)
    diff = [i for i in range(len(src)) if src[i] != out[i]]
    start = probe.sync_patch.OLD_TABLE_FILE_OFFSET + 3 * ROW + probe.MARKER_FIELD
    assert diff and all(start <= i < start + 2 for i in diff)
    assert info["original"] != info["marker"]


def test_marker_edit_rejects_bad_row() -> None:
    with pytest.raises(ValueError):
        probe.marker_edit(_source(), probe.sync_patch.ROW_COUNT)


def test_marker_edit_rejects_noop() -> None:
    src = bytearray(_source())
    off = probe.sync_patch.OLD_TABLE_FILE_OFFSET + probe.MARKER_FIELD
    src[off : off + 2] = probe.MARKER_NEW_VALUE.to_bytes(2, "little")
    base = probe.sync_patch.SHOPAI_FILE_OFFSET + probe.MARKER_FIELD
    src[base : base + 2] = probe.MARKER_NEW_VALUE.to_bytes(2, "little")
    with pytest.raises(ValueError):
        probe.marker_edit(bytes(src), 0)


def _snapshots(synced: bool) -> tuple[bytes, bytes, bytes, bytes]:
    old, tail = _fixture()
    src, _ = probe.marker_edit(_source(), 0)
    new_old = src[probe.sync_patch.OLD_TABLE_FILE_OFFSET : probe.sync_patch.OLD_TABLE_FILE_OFFSET + OLD_LEN]
    original_row = old[:ROW]
    shopai = (new_old if synced else old) + tail
    return shopai, new_old, original_row, tail


def test_judge_sample_detects_sync_and_unsynced() -> None:
    shopai, new_old, original_row, tail = _snapshots(True)
    assert probe.judge_sample(shopai, new_old, 0, original_row, tail)["shopai_equals_old"]
    shopai, new_old, original_row, tail = _snapshots(False)
    judged = probe.judge_sample(shopai, new_old, 0, original_row, tail)
    assert judged["shopai_equals_original"] and not judged["shopai_equals_old"]
    assert judged["tail_unchanged"]


def test_judge_sample_flags_tail_change() -> None:
    shopai, new_old, original_row, tail = _snapshots(True)
    broken = shopai[:-2] + b"\x00\x00"
    assert not probe.judge_sample(broken, new_old, 0, original_row, tail)["tail_unchanged"]


def test_split_snapshot_rejects_wrong_length() -> None:
    with pytest.raises(ValueError):
        probe.split_snapshot(b"\0" * 10)


def _s(t: float, synced: bool, tail: bool = True) -> dict:
    return {"t": t, "shopai_equals_old": synced, "tail_unchanged": tail}


def test_verdict_candidate_cases() -> None:
    assert probe.verdict("candidate", [_s(1, False), _s(3, True)], True, False)["status"] == "PASS"
    assert probe.verdict("candidate", [_s(1, False)], True, False)["status"] == "INCONCLUSIVE"
    assert probe.verdict("candidate", [_s(1, True)], False, False)["status"] == "FAIL"
    assert probe.verdict("candidate", [_s(1, True)], True, True)["status"] == "FAIL"
    assert probe.verdict("candidate", [_s(1, True, tail=False)], True, False)["status"] == "FAIL"
    assert probe.verdict("candidate", [], True, False)["status"] == "FAIL"


def test_verdict_control_cases() -> None:
    assert probe.verdict("control", [_s(1, False)], True, False)["status"] == "PASS"
    assert probe.verdict("control", [_s(1, True)], True, False)["status"] == "FAIL"
