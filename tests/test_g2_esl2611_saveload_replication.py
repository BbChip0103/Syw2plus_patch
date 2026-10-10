"""Pure-helper contracts of the G2 2611 save/load replication wrapper."""

from tools import g2_esl2611_saveload_replication as sl


def test_remap_goal() -> None:
    assert sl.remap_goal(sl.SEED_GOAL_OLD) == sl.SEED_GOAL_NEW
    assert sl.remap_goal("other") == "other"


def test_unit_rows_decodes_fields() -> None:
    raw = bytearray(0x2A6)
    raw[0x8D], raw[0x8E] = 7, 3
    raw[0x29C:0x2A0] = (68268).to_bytes(4, "little")
    raw[0xB4:0xB8] = (400).to_bytes(4, "little", signed=True)
    raw[0x2A2:0x2A4] = (14).to_bytes(2, "little", signed=True)
    raw[0x2A4:0x2A6] = (20).to_bytes(2, "little", signed=True)
    assert sl.unit_rows(bytes(raw)) == (0, 7, 3, 68268, 400, 14, 20)


def test_diff_snapshots_classifies_changes() -> None:
    before = {1300: (1300, 7, 3, 9, 400, 14, 20), 1301: (1301, 7, 3, 10, 400, 5, 5), 1302: (1302, 7, 3, 11, 50, 1, 1)}
    after = {1300: (1300, 7, 3, 9, 390, 15, 21), 1301: (1301, 7, 3, 99, 400, 5, 5), 1303: (1303, 7, 3, 12, 1, 1, 1)}
    diff = sl.diff_snapshots(before, after, min_slot=1200)
    assert (diff["changed"], diff["changed_one_tick_drift"], diff["changed_other"]) == (2, 1, 1)
    assert (diff["missing_after"], diff["extra_after"], diff["exact"]) == (1, 1, False)
    assert sl.diff_snapshots(before, before)["exact"] is True
    assert sl.diff_snapshots(before, after, min_slot=1301)["compared"] == 2


def test_diff_ignores_slots_below_min_slot() -> None:
    assert sl.diff_snapshots({5: (5, 1, 1, 1, 1, 1, 1)}, {}, min_slot=1200)["exact"] is True


def test_ps_all_3_requires_nonempty_complete_rows() -> None:
    assert sl.ps_samples_all_3([]) is False
    assert sl.ps_samples_all_3([{"alive": True}]) is False
    assert sl.ps_samples_all_3([{"alive": True, "ps": 3}, {"alive": True, "ps": 3}]) is True
    assert sl.ps_samples_all_3([{"alive": True, "ps": 3, "error": "read failed"}]) is False
    assert sl.ps_samples_all_3([{"alive": True, "ps": 3}, {"alive": False, "ps": 3}]) is False
    assert sl.ps_samples_all_3([{"alive": True, "ps": 3}, {"alive": True, "ps": 2}]) is False


def test_frozen_candidate_validation_fails_closed_on_provenance_mismatch() -> None:
    meta = {"build": {"combo": {"schema": "syw2plus.esl2613.g2-combo.v1", "variant": "v8",
                                 "layers": ["G2", "G6", "G8"], "input_sha256": "base",
                                 "candidate_sha256": sl.EXPECTED_SHA["v8"]},
                      "spike": {"layer3": {"starts": {}}}}}
    assert sl.validate_frozen_candidate(meta, b"frozen candidate", "v8", expected_candidate_sha=sl.EXPECTED_SHA["v8"],
                                       expected_input_sha="base") is False
    matching = {"build": {"combo": {"schema": "syw2plus.esl2613.g2-combo.v1", "variant": "v8",
                                     "layers": ["G2", "G6", "G8"], "input_sha256": "base",
                                     "candidate_sha256": sl.EXPECTED_SHA["v8"]},
                              "spike": {"layer3": {"starts": {"g2bss": "0x1"}}}}}
    import hashlib
    candidate = b"frozen candidate"
    digest = hashlib.sha256(candidate).hexdigest()
    matching["build"]["combo"]["candidate_sha256"] = digest
    rebuilt_report = {"detail": {"g2": matching["build"]["spike"]}}
    assert sl.validate_frozen_candidate(matching, candidate, "v8", expected_candidate_sha=digest,
                                        expected_input_sha="base", rebuilt_candidate=candidate,
                                        rebuilt_report=rebuilt_report) is True
    matching["build"]["combo"]["input_sha256"] = "wrong-base"
    assert sl.validate_frozen_candidate(matching, candidate, "v8", expected_candidate_sha=digest,
                                        expected_input_sha="base", rebuilt_candidate=candidate,
                                        rebuilt_report=rebuilt_report) is False
    matching["build"]["combo"]["input_sha256"] = "base"
    matching["build"]["combo"]["variant"] = "v89"
    assert sl.validate_frozen_candidate(matching, candidate, "v8", expected_candidate_sha=digest,
                                        expected_input_sha="base", rebuilt_candidate=candidate,
                                        rebuilt_report=rebuilt_report) is False
    matching["build"]["combo"]["variant"] = "v8"
    assert sl.validate_frozen_candidate(matching, candidate, "v8", expected_candidate_sha=digest,
                                        expected_input_sha="base", rebuilt_candidate=b"other",
                                        rebuilt_report=rebuilt_report) is False
    tampered_report = {"detail": {"g2": {"layer3": {"starts": {"g2bss": "0x2"}}}}}
    assert sl.validate_frozen_candidate(matching, candidate, "v8", expected_candidate_sha=digest,
                                        expected_input_sha="base", rebuilt_candidate=candidate,
                                        rebuilt_report=tampered_report) is False
