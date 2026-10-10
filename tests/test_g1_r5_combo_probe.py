from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools import g1_r5_combo_probe as probe


def test_input_sha_guard(tmp_path: Path) -> None:
    f = tmp_path / "x.bin"
    f.write_bytes(b"abc")
    good = probe.sha256_file(f)
    assert probe.check_input_sha(f, good, "x") == good
    with pytest.raises(probe.ProbeError, match="SHA mismatch"):
        probe.check_input_sha(f, "0" * 64, "x")


def test_pinned_constants_are_distinct_hex() -> None:
    values = [*probe.R5_SHA256.values(), *probe.G1_EXE_SHA256.values(), probe.G1MM_SHA256, probe.LAP1151_DLL_SHA256]
    assert len(set(values)) == len(values)
    assert all(len(v) == 64 and int(v, 16) >= 0 for v in values)


def test_paths_cannot_leave_private_root(tmp_path: Path) -> None:
    root = tmp_path / "runtime"
    (root / "a").mkdir(parents=True)
    assert probe.assert_under(root, root / "a") == (root / "a").resolve()
    with pytest.raises(probe.ProbeError):
        probe.assert_under(root, root / ".." / "other")
    link = root / "escape"
    link.symlink_to(tmp_path)
    with pytest.raises(probe.ProbeError):
        probe.assert_under(root, link / "x")


def test_capture_name_prefix() -> None:
    assert probe.capture_name("20261007_190000", "normal", "g1", "ps3_ingame") == \
        "20261007_190000_g1r5_normal_g1_ps3_ingame.png"


def _trace(*events: dict) -> str:
    return "\n".join(json.dumps(e) for e in events) + "\nnot json\n"


def test_parse_trace_active_and_failed() -> None:
    ok = probe.parse_trace(_trace(
        {"event": "install", "install_status": "active", "stage": "complete"},
        {"event": "mirror2x_install", "install_status": "active", "stage": "primitives"},
        {"event": "mirror2x_present", "program_state": 9}, {"event": "mirror2x_present", "program_state": 3}))
    assert ok["hook_install_active"] and ok["dd_install_active"] and not ok["install_failed"]
    assert ok["program_states"] == [3, 9] and ok["mirror2x_present_events"] == 2
    bad = probe.parse_trace(_trace(
        {"event": "install", "install_status": "failed", "stage": "mirror2x_primitives", "reason": "old_bytes"}))
    assert not bad["hook_install_active"] and bad["install_failed"][0]["stage"] == "mirror2x_primitives"
    assert probe.parse_trace("")["events"] == 0


def test_hooks_patched_requires_all_targets_to_be_jmp() -> None:
    assert probe.hooks_patched({a: 0xE9 for a in probe.HOOK_TARGETS})
    assert not probe.hooks_patched({a: 0x55 for a in probe.HOOK_TARGETS})
    assert not probe.hooks_patched({probe.HOOK_TARGETS[0]: 0xE9})


def test_stage_verdicts_g1_and_plain() -> None:
    g1 = {"window": {"size": [1600, 1200]},
          "install_log": {"hook_install_active": True, "dd_install_active": True, "install_failed": [],
                          "skipped_old_bytes_mismatch": 0, "hooks_patched": True, "events": 9},
          "to_ps3": {"reached_ps3": True, "alive_at_end": True}, "captures": {"a": {"returncode": 0}}}
    assert [probe.stage_verdict(n, g1, "g1") for n in ("window", "install_log", "to_ps3", "captures")] == ["PASS"] * 4
    assert probe.stage_verdict("window", {"window": {"size": [800, 600]}}, "g1") == "FAIL"
    plain = {"window": {"size": [800, 600]}, "install_log": {"events": 0, "hooks_patched": False}}
    assert probe.stage_verdict("window", plain, "plain") == "PASS"
    assert probe.stage_verdict("install_log", plain, "plain") == "PASS"
    assert probe.stage_verdict("install_log", {"install_log": {"events": 3}}, "plain") == "FAIL"
    assert probe.stage_verdict("to_ps3", {"to_ps3": {"reached_ps3": True, "alive_at_end": False}}, "g1") == "FAIL"
    assert probe.stage_verdict("input", {}, "g1") == "SKIP"


def test_validate_result_schema() -> None:
    good = {"schema": probe.SCHEMA, "mode": "g1", "lane": "normal", "status": "PASS", "provenance": {},
            "cleanup": {}, "verdicts": {name: "PASS" for name in probe.STAGES}}
    assert probe.validate_result(good) == []
    assert "mode" in probe.validate_result({**good, "mode": "x"})
    assert "verdicts" in probe.validate_result({**good, "verdicts": {"window": "PASS"}})
    assert "schema" in probe.validate_result({**good, "schema": "other"})


def test_find_game_window_prefers_content_child() -> None:
    tree = ("     0x400001 \"Syw\": (\"a.exe\" \"Wine\")  1600x1200+0+0  +0+0\n"
            "        0x400002 (has no name): ()  1600x1200+0+0  +0+0\n"
            "     0x400009 \"other\": ()  100x100+0+0  +0+0\n")
    assert probe.find_game_window(tree, ((1600, 1200), (800, 600))) == ("0x400001", "0x400002", (1600, 1200))
    with pytest.raises(probe.ProbeError):
        probe.find_game_window(tree, ((800, 600),))


# ---- relaunch (consecutive runs in one game copy / one prefix) -------------------------------------------------


def test_snapshot_and_diff_report_added_removed_changed(tmp_path: Path) -> None:
    (tmp_path / "keep.txt").write_text("a")
    (tmp_path / "gone.txt").write_text("a")
    (tmp_path / "grow.txt").write_text("a")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "n.bin").write_bytes(b"12")
    before = probe.snapshot_tree(tmp_path)
    assert set(before) == {"keep.txt", "gone.txt", "grow.txt", "sub/n.bin"}
    (tmp_path / "gone.txt").unlink()
    (tmp_path / "grow.txt").write_text("abc")
    (tmp_path / "new.log").write_text("x")
    diff = probe.diff_snapshots(before, probe.snapshot_tree(tmp_path))
    assert diff["added"] == ["new.log"] and diff["removed"] == ["gone.txt"]
    assert [c["path"] for c in diff["changed"]] == ["grow.txt"]
    assert diff["changed"][0]["size"] == [1, 3]


def test_diff_ignores_identical_snapshots(tmp_path: Path) -> None:
    (tmp_path / "a").write_text("a")
    snap = probe.snapshot_tree(tmp_path)
    assert probe.diff_snapshots(snap, dict(snap)) == {"added": [], "removed": [], "changed": []}


def test_reg_text_diff_lines_only() -> None:
    a = "[Software\\X]\n\"A\"=\"1\"\n"
    b = "[Software\\X]\n\"A\"=\"2\"\n\"B\"=\"3\"\n"
    out = probe.diff_reg_text(a, b)
    assert out["added"] == ['"A"="2"', '"B"="3"'] and out["removed"] == ['"A"="1"']


def test_environ_prefix_match() -> None:
    env = b"A=1\0WINEPREFIX=/x/prefix\0B=2\0"
    assert probe.environ_has_prefix(env, "/x/prefix")
    assert not probe.environ_has_prefix(env, "/x/prefix2")
    assert not probe.environ_has_prefix(b"A=1\0", "/x/prefix")


def test_relaunch_verdict() -> None:
    ok = {"reached_ps9": True, "exited_early": False}
    bad = {"reached_ps9": False, "exited_early": True}
    assert probe.relaunch_verdict([ok, ok]) == "NOT_REPRODUCED"
    assert probe.relaunch_verdict([ok, bad]) == "REPRODUCED_RUN2"
    assert probe.relaunch_verdict([ok, ok, bad]) == "REPRODUCED_RUN3"
    assert probe.relaunch_verdict([bad]) == "RUN1_FAILED"
    assert probe.relaunch_verdict([]) == "NO_RUNS"


def test_scan_crash_lines() -> None:
    text = "ok\nwine: Unhandled exception 0xc0000005 at 0x1\nerr:seh:foo bar\nfine\n"
    assert len(probe.scan_crash_lines(text)) == 2
    assert probe.scan_crash_lines("nothing\n") == []


def test_ddraw_override_choices() -> None:
    assert probe.DDRAW_OVERRIDES == {"builtin": "ddraw=b", "native": "ddraw=n,b"}
