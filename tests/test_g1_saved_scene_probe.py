from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import threading
import time
from types import ModuleType

import pytest
from PIL import Image

from tools.g1_saved_scene_probe import (
    SAVE_NAME,
    SAVE_SHA256,
    _compare_input_effects,
    _compare_minimap_diagnostic_parity,
    _disable_present_trace,
    _histogram_percentile,
    _performance_present_metrics,
    _pair_status,
    _trace_close_summary,
    _production_effect,
    _poll_stable_observation,
    _scene_identity,
)


def test_candidate_capture_barrier_requires_multiple_matching_presents(tmp_path: Path) -> None:
    from tools.g1_saved_scene_probe import _wait_for_mirror_present

    trace = tmp_path / "trace.jsonl"
    trace.write_text(
        '{"event":"mirror2x_present","program_state":9}\n'
        '{"event":"mirror2x_present","program_state":3}\n'
        '{"event":"mirror2x_present","program_state":3}\n',
        encoding="utf-8",
    )
    result = _wait_for_mirror_present(trace, program_state=3, timeout=0.2)
    assert result["status"] == "PASS", result["invalid_reasons"]
    assert result["records"] == 2


@pytest.mark.parametrize(
    ("candidate", "records"),
    [
        (False, [
            {"event": "blt", "program_state": 3, "caller": "0x004D3ABC",
             "hresult": 0, "seq": 11, "ts_ms": 20, "present_tick": 19},
            {"event": "blt", "program_state": 3, "caller": "0x004D3ABC",
             "hresult": 0, "seq": 12, "ts_ms": 40, "present_tick": 39},
        ]),
        (True, [
            {"event": "mirror2x_present", "program_state": 3, "success": 1,
             "hresult": 0, "seq": 11, "ts_ms": 20, "game_tick": 19},
            {"event": "mirror2x_present", "program_state": 3, "success": 1,
             "hresult": 0, "seq": 12, "ts_ms": 40, "game_tick": 39},
        ]),
    ],
)
def test_post_input_capture_barrier_requires_fresh_primary_presents(
    tmp_path: Path, candidate: bool, records: list[dict[str, object]],
) -> None:
    from tools.g1_saved_scene_probe import _wait_for_post_input_presents

    trace = tmp_path / "trace.jsonl"
    trace.write_text("".join(json.dumps(row) + "\n" for row in records), encoding="utf-8")
    result = _wait_for_post_input_presents(trace, candidate=candidate, after_seq=10, timeout=0.2)
    assert result["status"] == "PASS", result
    assert [row["seq"] for row in result["records"]] == [11, 12]


def test_post_release_barrier_uses_first_present_after_received_button_up(tmp_path: Path) -> None:
    from tools.g1_saved_scene_probe import _wait_for_post_release_presents

    present_trace = tmp_path / "present.jsonl"
    input_trace = tmp_path / "input.jsonl"
    presents = [
        {"event": "mirror2x_present", "program_state": 3, "success": 1,
         "hresult": 0, "seq": seq, "ts_ms": ts}
        for seq, ts in ((1032, 854185), (1036, 854248), (1040, 854285),
                        (1044, 854348), (1048, 854382), (1052, 854450),
                        (1056, 854499), (1060, 854559), (1064, 854603))
    ]
    input_rows = [
        {"schema": "g1-input-trace-v1", "seq": 40, "kind": "WndProc",
         "message": 0x201, "logical": [100, 40], "ts_ms": 854263, "thread_id": 280},
        {"schema": "g1-input-trace-v1", "seq": 41, "kind": "WndProc",
         "message": 0x202, "logical": [400, 220], "ts_ms": 854538, "thread_id": 280},
    ]
    present_trace.write_text("".join(json.dumps(row) + "\n" for row in presents), encoding="utf-8")
    input_trace.write_text("".join(json.dumps(row) + "\n" for row in input_rows), encoding="utf-8")

    result = _wait_for_post_release_presents(
        present_trace, input_trace, candidate=True, input_seq_before=39,
        host_return_present_seq=1056, drag_from=(100, 40), drag_to=(400, 220), timeout=0.2,
    )

    assert result["status"] == "PASS", result
    assert [row["seq"] for row in result["records"]] == [1060, 1064]
    assert result["release"]["seq"] == 41
    assert result["first_release_delta_ms"] == 21


@pytest.mark.parametrize("input_rows", [
    [],
    [{"seq": 41, "kind": "WndProc", "message": 0x202, "logical": [400, 220]}],
    [{"seq": 40, "kind": "WndProc", "message": 0x201, "logical": [100, 40]},
     {"seq": 41, "kind": "WndProc", "message": 0x202, "logical": [400, 220]},
     {"seq": 42, "kind": "WndProc", "message": 0x202, "logical": [400, 220]}],
    [{"seq": 40, "kind": "WndProc", "message": 0x201, "logical": [99, 40]},
     {"seq": 41, "kind": "WndProc", "message": 0x202, "logical": [400, 220]}],
    [{"seq": 40, "kind": "WndProc", "message": 0x201, "logical": [100, 40]},
     {"seq": 41, "kind": "WndProc", "message": 0x202, "logical": [399, 220]}],
])
def test_post_release_barrier_rejects_missing_ambiguous_or_mismatched_release(
    tmp_path: Path, input_rows: list[dict[str, object]],
) -> None:
    from tools.g1_saved_scene_probe import _wait_for_post_release_presents

    present_trace = tmp_path / "present.jsonl"
    input_trace = tmp_path / "input.jsonl"
    present_trace.write_text("", encoding="utf-8")
    input_trace.write_text("".join(json.dumps({"schema": "g1-input-trace-v1", **row}) + "\n"
                                         for row in input_rows), encoding="utf-8")
    result = _wait_for_post_release_presents(
        present_trace, input_trace, candidate=True, input_seq_before=39,
        host_return_present_seq=1056, drag_from=[100, 40], drag_to=[400, 220], timeout=0.01,
    )
    assert result["status"] == "UNKNOWN"


def test_post_release_barrier_excludes_equal_timestamp_and_old_sequence(tmp_path: Path) -> None:
    from tools.g1_saved_scene_probe import _wait_for_post_release_presents

    present_trace = tmp_path / "present.jsonl"
    input_trace = tmp_path / "input.jsonl"
    input_trace.write_text(
        json.dumps({"schema": "g1-input-trace-v1", "seq": 40, "kind": "WndProc",
                    "message": 0x201, "logical": [100, 40]}) + "\n"
        + json.dumps({"schema": "g1-input-trace-v1", "seq": 41, "kind": "WndProc",
                     "message": 0x202, "logical": [400, 220], "ts_ms": 100}) + "\n",
        encoding="utf-8",
    )
    rows = [
        {"event": "mirror2x_present", "program_state": 3, "success": 1, "hresult": 0,
         "seq": 1057, "ts_ms": 100},
        {"event": "mirror2x_present", "program_state": 3, "success": 1, "hresult": 0,
         "seq": 1056, "ts_ms": 101},
    ]
    present_trace.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    result = _wait_for_post_release_presents(
        present_trace, input_trace, candidate=True, input_seq_before=39,
        host_return_present_seq=1056, drag_from=[100, 40], drag_to=[400, 220], timeout=0.01,
    )
    assert result["status"] == "UNKNOWN"


def test_drag_capture_binding_requires_gate_and_stable_capture_selection() -> None:
    from tools.g1_saved_scene_probe import _drag_capture_binding

    def lane(*, candidate: bool, gate: str = "PASS", settled: list[int] | None = None,
             before: list[int] | None = None, after: list[int] | None = None) -> dict[str, object]:
        return _drag_capture_binding(
            candidate=candidate, button_up_delivered=True,
            post_input_presents={"status": gate}, settled_status="PASS", stable_samples=2,
            settled_selection=settled or [124, 140, 151, 170],
            selection_before_capture=before or [124, 140, 151, 170],
            selection_after_capture=after or [124, 140, 151, 170],
        )

    assert lane(candidate=True)["status"] == "PASS"
    assert lane(candidate=True, gate="UNKNOWN")["status"] == "HOLD"
    assert lane(candidate=True, before=[151])["status"] == "HOLD"
    assert lane(candidate=True, after=[151])["status"] == "HOLD"
    assert lane(candidate=False)["status"] == "PASS_WITH_LIMITS"
    assert lane(candidate=False, before=[151])["status"] == "HOLD"


def test_input_comparison_gates_capture_binding_independently_of_drag_semantics() -> None:
    def lane(binding: str) -> dict[str, object]:
        return {"actions": [
            {"tag": "selection", "result": "PASS", "after": {"selected_slots": [151]}},
            {"tag": "empty_click", "result": "PASS", "after": {"count": 0}},
            {"tag": "drag", "result": "PASS", "after": {"selected_slots": [124, 140, 151, 170]},
             "capture_binding": {"status": binding}},
            {"tag": "minimap", "result": "UNKNOWN", "camera_after": [1, 2],
             "gate": {"before_hex": "00", "restored_hex": "00"}},
            {"tag": "production", "control_result": "UNKNOWN", "result": "UNKNOWN"},
        ]}

    result = _compare_input_effects(lane("PASS_WITH_LIMITS"), lane("HOLD"))
    assert result["status"] == "HOLD"
    assert result["checks"]["drag_exact"] is True
    assert result["checks"]["drag_capture_binding"] is False


def test_stable_observation_requires_two_identical_matching_reads() -> None:
    reads = iter(({"count": 1, "selected_slots": [151]},
                  {"count": 4, "selected_slots": [124, 140, 151, 170]},
                  {"count": 4, "selected_slots": [124, 140, 151, 170]}))
    result = _poll_stable_observation(
        "settled drag", lambda: next(reads),
        lambda item: item.get("count") == 4,
    )
    assert result["status"] == "PASS"
    assert result["samples"] == 3
    assert result["stable_samples"] == 2


@pytest.mark.parametrize(("black_count", "expected"), [(2_000, "PASS"), (2_001, "FAIL")])
def test_capture_visual_gate_v2_black_world_excess_boundary(
    tmp_path: Path, black_count: int, expected: str,
) -> None:
    from tools.g1_saved_scene_probe import _compare_images

    baseline_path = tmp_path / "baseline.png"
    candidate_path = tmp_path / "candidate.png"
    Image.new("RGB", (800, 600), (255, 255, 255)).save(baseline_path)
    candidate_image = Image.new("RGB", (1600, 1200), (255, 255, 255))
    for index in range(black_count):
        x, y = index % 800, index // 800
        candidate_image.putpixel((2 * x, 2 * y), (0, 0, 0))
    candidate_image.save(candidate_path)
    baseline = {"captures": {"loaded": {"path": str(baseline_path)}}}
    candidate = {"captures": {"loaded": {"path": str(candidate_path)}}}

    result = _compare_images(baseline, candidate)

    assert result["v2_status"] == expected
    assert result["v2s_status"] == expected
    assert result["v2_candidate_minus_baseline_black"] == black_count
    assert result["v2_maximum_excess"] == 2_000
    assert result["v2s_single_black_blocks"] == black_count


def _naive_scale2x(pixels: list[tuple[int, int, int]], width: int, height: int) -> list[
    tuple[int, int, int]
]:
    """Independent EPX reference (edge clamp), row-major 2x output."""
    out = [(0, 0, 0)] * (4 * width * height)
    for y in range(height):
        for x in range(width):
            e = pixels[y * width + x]
            b = pixels[max(y - 1, 0) * width + x]
            h = pixels[min(y + 1, height - 1) * width + x]
            d = pixels[y * width + max(x - 1, 0)]
            f = pixels[y * width + min(x + 1, width - 1)]
            p0 = p1 = p2 = p3 = e
            if b != h and d != f:
                p0 = d if d == b else e
                p1 = f if b == f else e
                p2 = d if d == h else e
                p3 = f if h == f else e
            top = (2 * y) * 2 * width + 2 * x
            out[top], out[top + 1] = p0, p1
            out[top + 2 * width], out[top + 2 * width + 1] = p2, p3
    return out


def _staircase_baseline(tmp_path: Path) -> tuple[Path, list[tuple[int, int, int]]]:
    """White 800x600 with black diagonal staircases in the top half of the world."""
    white, black = (255, 255, 255), (0, 0, 0)
    pixels = [white] * (800 * 600)
    for j in range(60):
        for i in range(200):
            pixels[(4 * j + 1) * 800 + 4 * i + 2] = black
            pixels[(4 * j + 2) * 800 + 4 * i + 1] = black
    from PIL import Image

    path = tmp_path / "baseline.png"
    image = Image.new("RGB", (800, 600))
    image.putdata(pixels)
    image.save(path)
    return path, pixels


def _write_candidate(tmp_path: Path, pixels: list[tuple[int, int, int]],
                     injected: int) -> Path:
    from PIL import Image

    scaled = _naive_scale2x(pixels, 800, 600)
    for index in range(injected):  # plain white world rows, below the staircases
        x, y = index % 800, 240 + index // 800
        assert pixels[y * 800 + x] == (255, 255, 255)
        scaled[(2 * y) * 1600 + 2 * x] = (0, 0, 0)
    path = tmp_path / "candidate.png"
    image = Image.new("RGB", (1600, 1200))
    image.putdata(scaled)
    image.save(path)
    return path


def test_v2s_exact_scale2x_candidate_has_no_unexplained_black_blocks(tmp_path: Path) -> None:
    from tools.g1_saved_scene_probe import _compare_images

    baseline_path, pixels = _staircase_baseline(tmp_path)
    candidate_path = _write_candidate(tmp_path, pixels, 0)
    result = _compare_images({"captures": {"loaded": {"path": str(baseline_path)}}},
                             {"captures": {"loaded": {"path": str(candidate_path)}}})

    # A perfect Scale2x necessarily has single-black blocks; they are not defects.
    assert result["v2s_single_black_blocks"] > 2_000
    assert result["v2s_raw_status"] == "FAIL"
    assert result["v2s_scale2x_reference_blocks"] == result["v2s_single_black_blocks"]
    assert result["v2s_unexplained_single_black_blocks"] == 0
    assert result["v2s_status"] == "PASS"


@pytest.mark.parametrize(("injected", "expected"), [(2_000, "PASS"), (2_001, "FAIL")])
def test_v2s_gate_counts_only_unexplained_single_black_blocks(
    tmp_path: Path, injected: int, expected: str,
) -> None:
    from tools.g1_saved_scene_probe import _compare_images

    baseline_path, pixels = _staircase_baseline(tmp_path)
    candidate_path = _write_candidate(tmp_path, pixels, injected)
    result = _compare_images({"captures": {"loaded": {"path": str(baseline_path)}}},
                             {"captures": {"loaded": {"path": str(candidate_path)}}})

    assert result["v2s_unexplained_single_black_blocks"] == injected
    assert result["v2s_single_black_blocks"] == (
        result["v2s_scale2x_reference_blocks"] + injected)
    assert result["v2s_status"] == expected
    assert result["v2s_maximum_single_black_blocks"] == 2_000


def test_v2s_capture_gate_ignores_raw_diagnostic_status() -> None:
    from tools.g1_saved_scene_probe import G1_CAPTURE_TAGS, _v2s_capture_gate

    comparisons = {tag: {"v2s_status": "PASS", "v2s_raw_status": "FAIL"}
                   for tag in G1_CAPTURE_TAGS}
    assert _v2s_capture_gate(comparisons)["status"] == "PASS"


@pytest.mark.parametrize(("statuses", "expected"), [
    ({tag: "PASS" for tag in ("loaded", "selection", "drag", "minimap", "production")}, "PASS"),
    ({"loaded": "FAIL"}, "FAIL"),
    ({"loaded": "PASS"}, "BLOCKED"),
])
def test_capture_visual_gate_v2_preserves_fail_and_missing_states(
    statuses: dict[str, str], expected: str,
) -> None:
    from tools.g1_saved_scene_probe import _v2_capture_gate

    comparisons = {tag: {"v2_status": status} for tag, status in statuses.items()}
    result = _v2_capture_gate(comparisons)

    assert result["status"] == expected
    assert json.loads(json.dumps(result))["status"] == expected


@pytest.mark.parametrize(("statuses", "expected"), [
    ({tag: "PASS" for tag in ("loaded", "selection", "drag", "minimap", "production")}, "PASS"),
    ({"loaded": "FAIL"}, "FAIL"),
    ({"loaded": "PASS"}, "BLOCKED"),
])
def test_capture_visual_gate_v2s_preserves_fail_and_missing_states(
    statuses: dict[str, str], expected: str,
) -> None:
    from tools.g1_saved_scene_probe import _v2s_capture_gate

    comparisons = {tag: {"v2s_status": status} for tag, status in statuses.items()}
    result = _v2s_capture_gate(comparisons)

    assert json.loads(json.dumps(result))["status"] == expected


@pytest.mark.parametrize(("black_blocks", "expected"), [(2_000, "PASS"), (2_001, "FAIL")])
def test_capture_visual_gate_v2q_four_black_blocks_boundary(
    tmp_path: Path, black_blocks: int, expected: str,
) -> None:
    from tools.g1_saved_scene_probe import _compare_images

    baseline_path = tmp_path / "baseline.png"
    candidate_path = tmp_path / "candidate.png"
    Image.new("RGB", (800, 600), (255, 255, 255)).save(baseline_path)
    candidate_image = Image.new("RGB", (1600, 1200), (255, 255, 255))
    for index in range(black_blocks):
        x, y = index % 800, index // 800
        for dy in range(2):
            for dx in range(2):
                candidate_image.putpixel((2 * x + dx, 2 * y + dy), (0, 0, 0))
    candidate_image.save(candidate_path)
    baseline = {"captures": {"loaded": {"path": str(baseline_path)}}}
    candidate = {"captures": {"loaded": {"path": str(candidate_path)}}}

    result = _compare_images(baseline, candidate)

    assert result["v2q_status"] == expected
    assert result["v2q_four_black_blocks"] == black_blocks
    assert result["v2q_maximum_four_black_blocks"] == 2_000


@pytest.mark.parametrize("expected", ["PASS", "FAIL", "BLOCKED"])
def test_capture_visual_gate_v2q_preserves_aggregate_and_json_state(expected: str) -> None:
    from tools.g1_saved_scene_probe import _v2q_capture_gate

    tags = ("loaded", "selection", "drag", "minimap", "production")
    comparisons = {tag: {"v2q_status": "PASS"} for tag in tags}
    if expected == "FAIL":
        comparisons["drag"]["v2q_status"] = "FAIL"
    elif expected == "BLOCKED":
        del comparisons["production"]

    result = _v2q_capture_gate(comparisons)

    assert result["status"] == expected
    assert json.loads(json.dumps(result))["status"] == expected


def test_scroll_coverage_starts_at_camera_transition_present(tmp_path: Path) -> None:
    from tools.g1_saved_scene_probe import _terrain_scroll_coverage

    trace = tmp_path / "trace.jsonl"
    before = {"event": "mirror2x_present", "program_state": 3, "seq": 1,
              "camera": [158, 101], "covered_pixels": 10, "stale_pixels": 0}
    rows = [before]
    rows.extend({"event": "mirror2x_present", "program_state": 3,
                 "seq": seq, "camera": [158, 101],
                 "sim_tick": 100 + seq,
                 "covered_pixels": 10, "stale_pixels": 0}
                for seq in range(2, 5))
    rows.extend({"event": "mirror2x_present", "program_state": 3,
                 "seq": seq, "camera": [159, 102],
                 "sim_tick": 100 + seq,
                 "covered_pixels": 300_000, "stale_pixels": 0}
                for seq in range(5, 35))
    trace.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")

    result = _terrain_scroll_coverage(
        trace, after_line_count=1, camera_before=[158, 101],
        observation_tick=136,
    )

    assert result["status"] == "PASS"
    assert result["sample_count"] == 30
    assert result["coverage_p50_pixels"] == 300_000
    assert result["transition_present_seq"] == 5
    assert result["first_threshold_present"] == 1


def test_scroll_coverage_does_not_accept_without_camera_transition(tmp_path: Path) -> None:
    from tools.g1_saved_scene_probe import _terrain_scroll_coverage

    trace = tmp_path / "trace.jsonl"
    rows = [{"event": "mirror2x_present", "program_state": 3, "seq": seq,
             "sim_tick": 100 + seq, "camera": [158, 101],
             "covered_pixels": 300_000, "stale_pixels": 0}
            for seq in range(1, 31)]
    trace.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")

    result = _terrain_scroll_coverage(
        trace, after_line_count=0, camera_before=[158, 101],
        observation_tick=136,
    )
    assert result["status"] == "INCOMPLETE"
    assert result["sample_count"] == 0
    assert result["transition_present_seq"] is None


def test_scroll_coverage_rejects_samples_after_observation_tick(tmp_path: Path) -> None:
    from tools.g1_saved_scene_probe import _terrain_scroll_coverage

    trace = tmp_path / "trace.jsonl"
    rows = [{"event": "mirror2x_present", "program_state": 3, "seq": seq,
             "sim_tick": 101 + seq, "camera": [159, 102],
             "covered_pixels": 300_000, "stale_pixels": 0}
            for seq in range(1, 27)]
    rows += [{"event": "mirror2x_present", "program_state": 3, "seq": seq,
              "sim_tick": 137 + seq, "camera": [159, 102],
              "covered_pixels": 300_000, "stale_pixels": 0}
             for seq in range(27, 31)]
    trace.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")

    result = _terrain_scroll_coverage(
        trace, after_line_count=0, camera_before=[158, 101], observation_tick=136,
    )

    assert result["status"] == "INCOMPLETE"
    assert result["sample_count"] == 26
    assert result["boundary_reached"] is True
    assert result["last_in_boundary_seq"] == 26
    assert result["first_after_boundary"] == {"seq": 27, "sim_tick": 164}
    assert result["coverage_p50_pixels"] is None


def test_scroll_coverage_waits_for_delayed_boundary_rows(tmp_path: Path, monkeypatch) -> None:
    import tools.g1_saved_scene_probe as probe

    trace = tmp_path / "trace.jsonl"
    prefix = [{"event": "mirror2x_present", "program_state": 3, "seq": seq,
               "sim_tick": 101 + seq, "camera": [159, 102],
               "covered_pixels": 300_000, "stale_pixels": 0}
              for seq in range(1, 21)]
    trace.write_text("".join(json.dumps(row) + "\n" for row in prefix), encoding="utf-8")
    appended = False

    def append_boundary(_delay: float) -> None:
        nonlocal appended
        if not appended:
            suffix = [{"event": "mirror2x_present", "program_state": 3, "seq": seq,
                       "sim_tick": 101 + seq, "camera": [159, 102],
                       "covered_pixels": 300_000, "stale_pixels": 0}
                      for seq in range(21, 31)]
            suffix.append({"event": "mirror2x_present", "program_state": 3, "seq": 31,
                           "sim_tick": 137, "camera": [159, 102],
                           "covered_pixels": 300_000, "stale_pixels": 0})
            with trace.open("a", encoding="utf-8") as stream:
                stream.write("".join(json.dumps(row) + "\n" for row in suffix))
            appended = True

    monkeypatch.setattr(probe.time, "sleep", append_boundary)
    result = probe._wait_for_terrain_scroll_coverage(
        trace, after_line_count=0, camera_before=[158, 101], observation_tick=136,
        timeout=1.0,
    )

    assert result["status"] == "PASS"
    assert result["sample_count"] == 30
    assert result["boundary_reached"] is False
    assert all(tick <= 136 for tick in result["sample_sim_ticks"])


def test_scroll_coverage_returns_incomplete_immediately_at_boundary(tmp_path: Path,
                                                                    monkeypatch) -> None:
    import tools.g1_saved_scene_probe as probe

    trace = tmp_path / "trace.jsonl"
    rows = [{"event": "mirror2x_present", "program_state": 3, "seq": seq,
             "sim_tick": 101 + seq, "camera": [159, 102],
             "covered_pixels": 300_000, "stale_pixels": 0}
            for seq in range(1, 27)]
    rows.append({"event": "mirror2x_present", "program_state": 3, "seq": 27,
                 "sim_tick": 137, "camera": [159, 102],
                 "covered_pixels": 300_000, "stale_pixels": 0})
    trace.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")

    def unexpected_wait(_delay: float) -> None:
        raise AssertionError("coverage wait continued after observation boundary")

    monkeypatch.setattr(probe.time, "sleep", unexpected_wait)
    result = probe._wait_for_terrain_scroll_coverage(
        trace, after_line_count=0, camera_before=[158, 101], observation_tick=136,
        timeout=1.0,
    )
    assert result["status"] == "INCOMPLETE"
    assert result["sample_count"] == 26
    assert result["boundary_reached"] is True


def test_scroll_coverage_invalidates_missing_sim_tick(tmp_path: Path) -> None:
    from tools.g1_saved_scene_probe import _terrain_scroll_coverage

    trace = tmp_path / "trace.jsonl"
    rows = [{"event": "mirror2x_present", "program_state": 3, "seq": seq,
             "camera": [159, 102], "covered_pixels": 300_000, "stale_pixels": 0}
            for seq in range(1, 31)]
    trace.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")

    result = _terrain_scroll_coverage(
        trace, after_line_count=0, camera_before=[158, 101], observation_tick=136,
    )
    assert result["status"] == "INVALID"
    assert result["sample_count"] == 0
    assert result["reason"] == "mirror2x_present missing integer sim_tick"


def test_scroll_coverage_uses_only_first_30_in_boundary_samples(tmp_path: Path) -> None:
    from tools.g1_saved_scene_probe import _terrain_scroll_coverage

    trace = tmp_path / "trace.jsonl"
    rows = [{"event": "mirror2x_present", "program_state": 3, "seq": seq,
             "sim_tick": 100 + seq, "camera": [159, 102],
             "covered_pixels": 300_000 + seq, "stale_pixels": 0}
            for seq in range(1, 32)]
    rows.append({"event": "mirror2x_present", "program_state": 3, "seq": 32,
                 "sim_tick": 137, "camera": [159, 102],
                 "covered_pixels": 999_999, "stale_pixels": 0})
    trace.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")

    result = _terrain_scroll_coverage(
        trace, after_line_count=0, camera_before=[158, 101], observation_tick=131,
    )
    assert result["status"] == "PASS"
    assert result["sample_count"] == 30
    assert result["sample_present_seqs"] == list(range(1, 31))
    assert result["boundary_reached"] is False


def test_scroll_trace_adds_sim_tick_only_with_camera_field() -> None:
    source = (Path(__file__).parents[1] / "tools/inmm_stub/direct_draw_trace.c").read_text(
        encoding="utf-8"
    )
    assert '\\"sim_tick\\"' in source
    assert "0x008924B8" in source


def test_opt_in_perf_sections_marker_is_bounded_and_rejects_stale_marker(tmp_path: Path) -> None:
    import tools.g1_saved_scene_probe as probe

    prefix = tmp_path / "prefix"
    drive_c = prefix / "drive_c"
    drive_c.mkdir(parents=True)
    marker = probe._arm_perf_sections_marker(prefix)
    assert marker == drive_c / probe.PERFORMANCE_WINDOW_FILE
    assert marker.read_text(encoding="ascii") == "active\n"
    with pytest.raises(probe.ProbeError, match="stale performance-section marker"):
        probe._arm_perf_sections_marker(prefix)
    marker.unlink()


def test_opt_in_perf_sections_marker_wraps_candidate_scroll_inputs() -> None:
    source = (Path(__file__).parents[1] / "tools/g1_saved_scene_probe.py").read_text(
        encoding="utf-8"
    )
    marker_start = source.index("perf_sections_marker = _arm_perf_sections_marker(prefix)")
    scroll_start = source.index("for slot_name, key in zip(", marker_start)
    marker_end = source.index("perf_sections_marker.unlink(missing_ok=True)", scroll_start)
    final_snapshot = source.index("final_target = common_tick_plan", marker_end)
    assert marker_start < scroll_start < marker_end < final_snapshot
    assert "if candidate and perf_sections:" in source[marker_start - 100:marker_start]


def test_scroll_receiver_requires_game_window_wm_keydown(tmp_path: Path) -> None:
    from tools.g1_saved_scene_probe import _latest_scroll_keydown, _latest_scroll_keyup

    trace = tmp_path / "input.jsonl"
    rows = [
        {"schema": "g1-scroll-input-v1", "seq": 1, "message": 0x101, "key": 0x28},
        {"schema": "g1-scroll-input-v1", "seq": 2, "message": 0x100, "key": 0x27},
        {"schema": "g1-scroll-input-v1", "seq": 3, "message": 0x100, "key": 0x28},
        {"schema": "g1-scroll-input-v1", "seq": 4, "message": 0x101, "key": 0x28},
    ]
    trace.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")

    down = _latest_scroll_keydown(trace, "DOWN")
    assert down is not None and down["seq"] == 3
    up = _latest_scroll_keyup(trace, "DOWN", after_seq=down["seq"])
    assert up is not None and up["seq"] == 4
    assert _latest_scroll_keydown(trace, "LEFT") is None


def test_scroll_probe_uses_card_down_path_first() -> None:
    from tools.g1_saved_scene_probe import TERRAIN_SCROLL_KEYS

    assert TERRAIN_SCROLL_KEYS[0] == "DOWN"


def test_scroll_receiver_ready_ack_is_required(tmp_path: Path) -> None:
    from tools.g1_saved_scene_probe import ProbeError, _wait_scroll_receiver_ready

    ready = tmp_path / "receiver.ready"
    ready.write_text(json.dumps({
        "schema": "g1-scroll-receiver-ready-v1", "status": "PASS", "hwnd": "0x1234",
    }), encoding="utf-8")
    assert _wait_scroll_receiver_ready(ready, timeout=0.01)["hwnd"] == "0x1234"
    ready.write_text('{"schema":"wrong"}', encoding="utf-8")
    with pytest.raises(ProbeError, match="did not become ready"):
        _wait_scroll_receiver_ready(ready, timeout=0.01)


def test_scroll_receiver_is_armed_before_waiting_for_ready_ack(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    import tools.g1_saved_scene_probe as probe

    arm = tmp_path / "receiver.arm"
    ready = tmp_path / "receiver.ready"

    def acknowledge_after_arm(path: Path) -> dict[str, str]:
        assert arm.read_text(encoding="ascii") == "armed\n"
        return {"status": "PASS", "hwnd": "0x1234"}

    monkeypatch.setattr(probe, "_wait_scroll_receiver_ready", acknowledge_after_arm)
    assert probe._arm_and_wait_scroll_receiver(arm, ready)["status"] == "PASS"


def test_scroll_releases_on_first_camera_change_while_receipt_is_delayed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    import tools.g1_saved_scene_probe as probe

    edge_events: list[tuple[str, bool]] = []
    camera_values = iter(([158, 101], [159, 102]))
    monkeypatch.setattr(probe, "_send_key_edge",
                        lambda display, env, key, *, down: (edge_events.append((key, down)) or 10))
    monkeypatch.setattr(probe, "_latest_scroll_keydown", lambda *args, **kwargs: None)
    result = probe._send_scroll_until_camera_change(
        ":91", {}, "DOWN", [158, 101], tmp_path / "input.jsonl",
        after_seq=0, read_camera=lambda: next(camera_values), timeout=0.1,
    )
    assert edge_events == [("DOWN", True), ("DOWN", False)]
    assert result["release_reason"] == "first_camera_change"
    assert result["camera"] == [159, 102]
    assert result["receiver_down"] is None


def test_scroll_keyup_is_attempted_when_camera_read_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    import tools.g1_saved_scene_probe as probe

    edge_events: list[tuple[str, bool]] = []
    monkeypatch.setattr(probe, "_send_key_edge",
                        lambda display, env, key, *, down: (edge_events.append((key, down)) or 10))
    monkeypatch.setattr(probe, "_latest_scroll_keydown", lambda *args, **kwargs: None)

    def fail_read() -> list[int]:
        raise RuntimeError("camera read failed")

    with pytest.raises(RuntimeError, match="camera read failed"):
        probe._send_scroll_until_camera_change(
            ":91", {}, "DOWN", [158, 101], tmp_path / "input.jsonl",
            after_seq=0, read_camera=fail_read, timeout=0.1,
        )
    assert edge_events == [("DOWN", True), ("DOWN", False)]


def test_scroll_exact_one_step_rejects_overshoot() -> None:
    from tools.g1_saved_scene_probe import _expected_scroll_camera

    assert [159, 102] == _expected_scroll_camera([158, 101], "DOWN")
    assert [171, 114] != _expected_scroll_camera([158, 101], "DOWN")
    assert [159, 100] == _expected_scroll_camera([158, 101], "RIGHT")


def test_scroll_camera_steps_counts_travel_in_key_direction_with_edge_slide() -> None:
    from tools.g1_saved_scene_probe import _scroll_camera_steps

    assert 0 == _scroll_camera_steps([158, 101], [158, 101], "DOWN")
    assert 1 == _scroll_camera_steps([158, 101], [159, 102], "DOWN")
    assert 5 == _scroll_camera_steps([158, 101], [163, 106], "DOWN")
    assert 4 == _scroll_camera_steps([158, 101], [162, 97], "RIGHT")
    # Edge slide: x clamps at 179 while y keeps moving (observed lap1006).
    assert 27 == _scroll_camera_steps([158, 101], [179, 128], "DOWN")
    assert 6 == _scroll_camera_steps([179, 128], [179, 122], "RIGHT")
    assert _scroll_camera_steps([158, 101], [157, 100], "DOWN") is None
    assert _scroll_camera_steps([158, 101], [159, 100], "DOWN") is None
    assert _scroll_camera_steps([158, 101], [159, 102], "RIGHT") is None
    assert _scroll_camera_steps([158, 101], [159, 100], "LEFT") is None


def test_scroll_hold_keeps_key_down_until_release_tick_not_first_camera_change(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    import tools.g1_saved_scene_probe as probe

    edge_events: list[tuple[str, bool]] = []
    camera_values = iter(([158, 101], [159, 102], [159, 102], [160, 103], [161, 104]))
    tick_values = iter((100, 100, 101, 102, 103, 104, 105))
    monkeypatch.setattr(probe, "_send_key_edge",
                        lambda display, env, key, *, down: (edge_events.append((key, down)) or 10))
    monkeypatch.setattr(probe, "_latest_scroll_keydown", lambda *args, **kwargs: None)
    result = probe._send_scroll_until_camera_change(
        ":91", {}, "DOWN", [158, 101], tmp_path / "input.jsonl",
        after_seq=0, read_camera=lambda: next(camera_values), timeout=5.0,
        read_sim_tick=lambda: next(tick_values), release_at_tick=105,
    )
    assert edge_events == [("DOWN", True), ("DOWN", False)]
    assert result["release_reason"] == "release_tick"
    assert result["camera"] == [161, 104]
    assert result["input_tick_before"] == 100 and result["input_tick_after"] == 100
    # Only camera transitions are sampled in hold mode.
    assert [item["camera"] for item in result["camera_samples"]] == [
        [158, 101], [159, 102], [160, 103], [161, 104]]


def test_scroll_hold_times_out_with_keyup_when_release_tick_never_arrives(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    import tools.g1_saved_scene_probe as probe

    edge_events: list[tuple[str, bool]] = []
    monkeypatch.setattr(probe, "_send_key_edge",
                        lambda display, env, key, *, down: (edge_events.append((key, down)) or 10))
    monkeypatch.setattr(probe, "_latest_scroll_keydown", lambda *args, **kwargs: None)
    result = probe._send_scroll_until_camera_change(
        ":91", {}, "RIGHT", [158, 101], tmp_path / "input.jsonl",
        after_seq=0, read_camera=lambda: [158, 101], timeout=0.05,
        read_sim_tick=lambda: 100, release_at_tick=200,
    )
    assert edge_events == [("RIGHT", True), ("RIGHT", False)]
    assert result["release_reason"] == "timeout"


def test_scroll_hold_requires_sim_tick_reader(tmp_path: Path) -> None:
    import tools.g1_saved_scene_probe as probe

    with pytest.raises(ValueError, match="read_sim_tick"):
        probe._send_scroll_until_camera_change(
            ":91", {}, "DOWN", [158, 101], tmp_path / "input.jsonl",
            after_seq=0, read_camera=lambda: [158, 101], release_at_tick=104,
        )


def test_terrain_scroll_hold_flag_is_opt_in_and_requires_terrain_scroll() -> None:
    source = (Path(__file__).parents[1] / "tools/g1_saved_scene_probe.py").read_text(
        encoding="utf-8"
    )
    assert 'parser.add_argument("--terrain-scroll-hold"' in source
    assert "--terrain-scroll-hold requires --terrain-scroll" in source
    assert "terrain_scroll_hold: bool = False" in source
    assert source.count("terrain_scroll_hold=args.terrain_scroll_hold") == 2
    scroll_loop = source[source.index("for slot_name, key in zip(", source.index('def _run_lane')):
                         source.index("        def selection()", source.index('def _run_lane'))]
    # Default 1-step path stays: hold only adds a release tick, never replaces the helper call.
    assert "release_at_tick=(" in scroll_loop
    assert "if terrain_scroll_hold else None" in scroll_loop


def test_scroll_camera_signs_cover_up_and_left_for_round_trip_hold() -> None:
    from tools.g1_saved_scene_probe import _expected_scroll_camera, _scroll_camera_steps

    assert [157, 100] == _expected_scroll_camera([158, 101], "UP")
    assert [157, 102] == _expected_scroll_camera([158, 101], "LEFT")
    assert 24 == _scroll_camera_steps([158, 101], [134, 77], "UP")
    assert 24 == _scroll_camera_steps([134, 77], [158, 101], "DOWN")
    assert 3 == _scroll_camera_steps([158, 101], [155, 104], "LEFT")
    assert _scroll_camera_steps([158, 101], [159, 102], "UP") is None
    assert _scroll_camera_steps([158, 101], [157, 100], "LEFT") is None


def test_parse_scroll_keys_defaults_to_down_right_and_accepts_up_down() -> None:
    import pytest as _pytest
    from tools.g1_saved_scene_probe import _parse_scroll_keys

    assert ("DOWN", "RIGHT") == _parse_scroll_keys("DOWN,RIGHT")
    assert ("UP", "DOWN") == _parse_scroll_keys("up,down")
    for bad in ("UP", "UP,DOWN,LEFT", "UP,UP", "UP,SPACE", ""):
        with _pytest.raises(ValueError):
            _parse_scroll_keys(bad)


def test_scroll_clamp_free_requires_equal_axis_travel() -> None:
    from tools.g1_saved_scene_probe import _scroll_clamp_free

    assert _scroll_clamp_free([158, 101], [134, 77]) is True
    assert _scroll_clamp_free([158, 101], [179, 128]) is False
    assert _scroll_clamp_free([158, 101], [158, 101]) is False


def test_terrain_scroll_keys_flag_is_opt_in_and_threaded_to_lanes() -> None:
    source = (Path(__file__).parents[1] / "tools/g1_saved_scene_probe.py").read_text(
        encoding="utf-8"
    )
    assert 'parser.add_argument("--terrain-scroll-keys"' in source
    assert "--terrain-scroll-keys requires --terrain-scroll" in source
    assert 'default="DOWN,RIGHT"' in source
    assert "terrain_scroll_keys: tuple[str, str] = (\"DOWN\", \"RIGHT\")" in source
    assert source.count("terrain_scroll_keys=scroll_keys") == 2


def test_scroll_pair_parity_accepts_configured_key_order() -> None:
    import inspect
    from tools.g1_saved_scene_probe import _terrain_scroll_pair_parity

    params = inspect.signature(_terrain_scroll_pair_parity).parameters
    assert params["scroll_keys"].default == ("DOWN", "RIGHT")


def test_scroll_pair_parity_holds_on_post_input_scene_mismatch() -> None:
    from tools.g1_saved_scene_probe import _terrain_scroll_pair_parity

    tick_plan = {"down_input_tick": 100, "down_observation_tick": 136,
                 "right_input_tick": 196, "right_observation_tick": 232,
                 "final_observation_tick": 268}

    def snapshot(tick: int, cap: int) -> dict[str, object]:
        state = {"players": [{"owner": 2, "cap": cap}], "units": []}
        return {"status": "PASS", "sim_tick_before": tick, "sim_tick_after": tick,
                "state": state}

    def lane(cap: int) -> dict[str, object]:
        return {
            "status": "PASS", "scene_after": {"owner2_cap": cap},
            "tick_plan": tick_plan,
            "actions": [
                {"key": "DOWN", "after": [159, 102],
                 "scene_after_action": {"tick": 136}, "target_observation_tick": 136,
                 "target_input_tick": 100, "input_tick_before": 100, "input_tick_after": 100,
                 "scene_snapshot": snapshot(136, cap)},
                {"key": "RIGHT", "after": [160, 101],
                 "scene_after_action": {"tick": 232}, "target_observation_tick": 232,
                 "target_input_tick": 196, "input_tick_before": 196, "input_tick_after": 196,
                 "scene_snapshot": snapshot(232, cap)},
            ],
            "final_scene_snapshot": snapshot(268, cap),
        }

    result = _terrain_scroll_pair_parity(
        lane(2100), lane(2300), loaded_scene_equal=True,
        candidate_fixed_coverage={"status": "PASS"},
    )
    assert result["same_camera_after_each_key"] is True
    assert result["end_game_state_equal"] is False
    assert result["complete_records_equal"] is False
    assert result["status"] == "HOLD"


def test_scroll_pair_rejects_lane_local_equal_deltas_at_different_ticks() -> None:
    from tools.g1_saved_scene_probe import _terrain_scroll_pair_parity

    def lane(start: int) -> dict[str, object]:
        plan = {"down_input_tick": start + 100, "down_observation_tick": start + 136,
                "right_input_tick": start + 196, "right_observation_tick": start + 232,
                "final_observation_tick": start + 268}
        return {"status": "PASS", "tick_plan": plan, "scene_after": {"same": True},
                "actions": [{"key": key, "after": camera, "scene_after_action": {"same": True},
                             "target_input_tick": plan[f"{key.lower()}_input_tick"],
                             "input_tick_before": plan[f"{key.lower()}_input_tick"],
                             "input_tick_after": plan[f"{key.lower()}_input_tick"],
                             "target_observation_tick": plan[f"{key.lower()}_observation_tick"],
                             "scene_snapshot": {"status": "PASS",
                                                "sim_tick_before": plan[f"{key.lower()}_observation_tick"],
                                                "sim_tick_after": plan[f"{key.lower()}_observation_tick"],
                                                "state": {"players": [], "units": []}}}
                            for key, camera in (("DOWN", [159, 102]), ("RIGHT", [160, 101]))],
                "final_scene_snapshot": {"status": "PASS",
                                         "sim_tick_before": plan["final_observation_tick"],
                                         "sim_tick_after": plan["final_observation_tick"],
                                         "state": {"players": [], "units": []}}}

    result = _terrain_scroll_pair_parity(
        lane(1000), lane(2000), loaded_scene_equal=True,
        candidate_fixed_coverage={"status": "PASS"},
    )
    assert result["common_tick_plan_match"] is False
    assert result["status"] == "HOLD"


def test_scroll_pair_accepts_complete_inprocess_snapshot_lanes() -> None:
    from tools.g1_saved_scene_probe import _terrain_scroll_pair_parity

    tick_plan = {"down_input_tick": 100, "down_observation_tick": 136,
                 "right_input_tick": 196, "right_observation_tick": 232,
                 "final_observation_tick": 268}

    def snapshot(tick: int) -> dict[str, object]:
        return {
            "status": "PASS", "source": "in_process_update_return",
            "target_tick": tick, "state_sim_tick": tick, "sim_tick_after": tick,
            "header": {"tick_after": tick, "thread_id": 7},
            "state": {"players": [{"owner": owner, "count": 0}
                                    for owner in range(8)], "units": []},
        }

    def lane() -> dict[str, object]:
        return {
            "status": "PASS", "scene_after": {"same": True}, "tick_plan": tick_plan,
            "inprocess_snapshot_gate": {"status": "PASS", "snapshot_count": 5},
            "actions": [
                {"key": "DOWN", "after": [159, 102], "scene_after_action": {"same": True},
                 "target_input_tick": 100, "input_tick_before": 100, "input_tick_after": 100,
                 "target_observation_tick": 136,
                 "input_scene_snapshot": snapshot(100), "scene_snapshot": snapshot(136)},
                {"key": "RIGHT", "after": [160, 101], "scene_after_action": {"same": True},
                 "target_input_tick": 196, "input_tick_before": 196, "input_tick_after": 196,
                 "target_observation_tick": 232,
                 "input_scene_snapshot": snapshot(196), "scene_snapshot": snapshot(232)},
            ],
            "final_scene_snapshot": snapshot(268),
        }

    result = _terrain_scroll_pair_parity(
        lane(), lane(), loaded_scene_equal=True,
        candidate_fixed_coverage={"status": "PASS"},
    )
    assert result["inprocess_snapshot_source_valid"] is True
    assert result["complete_records_equal"] is True
    assert result["status"] == "PASS"


def test_scene_diff_retains_full_player_and_unit_records() -> None:
    from tools.g1_saved_scene_probe import _scene_diff

    result = _scene_diff(
        {"players": [{"owner": 1, "rice": 10}],
         "units": [{"slot": 4, "owner": 1, "hp": 90}]},
        {"players": [{"owner": 1, "rice": 11}],
         "units": [{"slot": 4, "owner": 1, "hp": 80}, {"slot": 7, "owner": 1}]},
    )
    assert result["players_changed"] == [
        {"owner": 1, "before": {"owner": 1, "rice": 10}, "after": {"owner": 1, "rice": 11}}
    ]
    assert result["units_changed"][0]["before"]["hp"] == 90
    assert result["units_changed"][0]["after"]["hp"] == 80
    assert result["units_created"] == [{"slot": 7, "owner": 1}]


def test_inprocess_snapshot_uses_same_decoder_and_rejects_bad_identity(tmp_path: Path) -> None:
    import struct

    import tools.g1_saved_scene_probe as probe
    from patches.population import runtime_driver

    capacity, _unit_base, _exists_base = runtime_driver.STOCK_POOL
    player_bytes = bytes(8 * runtime_driver.PLAYER_STRUCT_SIZE)
    exists_bytes = bytes(capacity * 2)
    pool_bytes = bytes(capacity * 0x758)
    camera_bytes = struct.pack("<2i", 158, 101)
    payload = (struct.pack("<i", 3) + struct.pack("<i", 24692) + camera_bytes
               + player_bytes + exists_bytes + pool_bytes)
    header = probe.SNAPSHOT_HEADER.pack(
        b"G1SNAP1\0", 1, probe.SNAPSHOT_HEADER.size, 4321, 7,
        0x004245D2, 24691, 24692, 1, 0, 123456789,
        b"run-baseline\0".ljust(40, b"\0"),
    )
    snapshot = tmp_path / "state-24692.bin"
    snapshot.write_bytes(header + payload)

    decoded = probe._read_inprocess_scene_snapshot(
        snapshot, expected_tick=24692, expected_run_id="run-baseline",
    )
    expected = probe._decode_batched_scene(
        3, 24692, [158, 101], player_bytes, exists_bytes, pool_bytes,
    )
    assert decoded["status"] == "PASS"
    assert decoded["source"] == "in_process_update_return"
    assert decoded["state"] == expected
    assert decoded["header"]["thread_id"] == 7
    assert probe._scene_owner_count_invariant(decoded["state"])

    wrong_run = probe._read_inprocess_scene_snapshot(
        snapshot, expected_tick=24692, expected_run_id="other-run",
    )
    assert wrong_run["status"] == "INVALID"
    assert wrong_run["checks"]["run_id"] is False
    snapshot.write_bytes(header + payload[:-1])
    truncated = probe._read_inprocess_scene_snapshot(
        snapshot, expected_tick=24692, expected_run_id="run-baseline",
    )
    assert truncated["status"] == "INVALID"
    assert truncated["reason"] == "snapshot size mismatch"


def test_snapshot_call_patch_source_guards_ownership_and_rollback() -> None:
    source = (Path(__file__).parents[1] / "tools/inmm_stub/g1_state_snapshot.c").read_text()

    def function_body(name: str) -> str:
        start = source.index(name + "(")
        opening = source.index("{", start)
        depth = 0
        for index in range(opening, len(source)):
            if source[index] == "{":
                depth += 1
            elif source[index] == "}":
                depth -= 1
                if depth == 0:
                    return source[opening:index + 1]
        raise AssertionError(f"unterminated C function: {name}")

    install = function_body("install_call")
    restore = function_body("restore_call")
    detach = function_body("g1_state_snapshot_detach")
    assert install.index("bytes_equal(site, expected, 5u)") < install.index("VirtualProtect(")
    assert install.index("bytes_equal(site, expected, 5u)", install.index("VirtualProtect(")) < install.index("copy_bytes(site, hook, 5u)")
    assert "FlushInstructionCache(GetCurrentProcess(), site, 5u)" in install
    assert "bytes_equal(site, hook, 5u)" in install
    assert "VirtualProtect(site, 5u, old, &ignored)" in install
    assert restore.index("bytes_equal(site, owned, 5u)") < restore.index("VirtualProtect(")
    assert restore.index("bytes_equal(site, owned, 5u)", restore.index("VirtualProtect(")) < restore.index("copy_bytes(site, original, 5u)")
    assert "FlushInstructionCache(GetCurrentProcess(), site, 5u)" in restore
    assert "make_hook(CALL_A, snapshot_call_a, hook)" in detach
    assert "make_hook(CALL_B, snapshot_call_b, hook)" in detach
    assert "site[0] == 0xE8" not in detach


def test_snapshot_wrappers_call_update_without_compiler_thunk() -> None:
    source = (Path(__file__).parents[1] / "tools/inmm_stub/g1_state_snapshot.c").read_text()
    for callsite, wrapper in (("0x004245D2", "snapshot_call_a"),
                              ("0x004250F7", "snapshot_call_b")):
        body = source[source.index("static void " + wrapper):]
        body = body[:body.index("\n}") + 2]
        assert f"pushl ${callsite}; call _g1_state_snapshot_before" in body
        assert "call *_g1_state_snapshot_update_target" in body
        assert f"pushl ${callsite}; call _g1_state_snapshot_after" in body
        assert "popal; popfl; ret" in body
    assert "call_update" not in source


def test_snapshot_hooks_install_only_after_runtime_contract_guard() -> None:
    source = (Path(__file__).parents[1] / "tools/inmm_stub/direct_draw_trace.c").read_text()
    start = source.index("int g1_direct_draw_trace_install(void)")
    body = source[start:source.index("\nvoid g1_direct_draw_trace_detach", start)]
    assert body.index("if (!verify_runtime_contract())") < body.index(
        "if (g1_state_snapshot_enabled() && !g1_state_snapshot_install())")


def test_rice_phase_observation_requires_matching_entry_and_return() -> None:
    from tools.g1_saved_scene_probe import _rice_phase_observation

    result = _rice_phase_observation([
        {"seq": 1, "event": "simulation_update_enter", "thread_global_num": 2, "tick": 24862},
        {"seq": 2, "event": "rice_write", "thread_global_num": 2, "pc_after_write": 0x43ED67,
         "writer_instruction_address": 0x43ED64, "writer_instruction_bytes": "894114",
         "old_rice": 230206, "new_rice": 230207},
        {"seq": 3, "event": "simulation_update_return", "thread_global_num": 2, "tick": 24862,
         "rice": 230207},
    ])
    assert result["status"] == "PASS"
    assert result["phase_status"] == "VALID_OBSERVED"
    assert result["missed_phase_ticks"] == []
    assert result["completed_simulation_update_observations"][0]["tick"] == 24862
    assert result["rice_writer_thread_status"] == "OBSERVED_SINGLE_THREAD"
    assert result["stable_tick_is_completion_proof"] is False
    assert result["post_call_address_is_approved_boundary"] is False
    assert result["all_writer_quiescence_proven"] is False


def test_rice_phase_observation_rejects_stable_tick_without_phase_return() -> None:
    from tools.g1_saved_scene_probe import _rice_phase_observation

    result = _rice_phase_observation([
        {"seq": 1, "event": "tick_sample", "tick": 24862},
        {"seq": 2, "event": "simulation_update_enter", "thread_global_num": 2, "tick": 24862},
    ])
    assert result["status"] == "INCONCLUSIVE"
    assert result["phase_status"] == "INVALID_OR_INCOMPLETE"
    assert "simulation update entry has no return" in result["invalid_reasons"]


def test_rice_phase_observation_rejects_a_missed_tick() -> None:
    from tools.g1_saved_scene_probe import _rice_phase_observation

    result = _rice_phase_observation([
        {"seq": 1, "event": "simulation_update_enter", "thread_global_num": 2, "tick": 24862},
        {"seq": 2, "event": "simulation_update_return", "thread_global_num": 2, "tick": 24862},
        {"seq": 3, "event": "simulation_update_enter", "thread_global_num": 2, "tick": 24864},
        {"seq": 4, "event": "simulation_update_return", "thread_global_num": 2, "tick": 24864},
    ])
    assert result["status"] == "INCONCLUSIVE"
    assert result["missed_phase_ticks"] == [{"previous_tick": 24862, "next_tick": 24864}]


def test_rice_phase_observation_rejects_missing_writer_evidence() -> None:
    from tools.g1_saved_scene_probe import _rice_phase_observation

    result = _rice_phase_observation([
        {"seq": 1, "event": "simulation_update_enter", "thread_global_num": 2, "tick": 24862},
        {"seq": 2, "event": "simulation_update_return", "thread_global_num": 2, "tick": 24862},
    ])
    assert result["status"] == "INCONCLUSIVE"
    assert result["rice_writer_thread_status"] == "MISSING"
    assert "no rice writer observed in diagnostic window" in result["invalid_reasons"]


def test_rice_phase_observation_rejects_writer_missing_thread_or_old_new() -> None:
    from tools.g1_saved_scene_probe import _rice_phase_observation

    result = _rice_phase_observation([
        {"seq": 1, "event": "simulation_update_enter", "thread_global_num": 2, "tick": 24862},
        {"seq": 2, "event": "rice_write", "pc_after_write": 0x43ED67,
         "old_rice": 230207, "new_rice": 231007},
        {"seq": 3, "event": "simulation_update_return", "thread_global_num": 2, "tick": 24862,
         "rice": 231007},
    ])
    assert result["status"] == "INCONCLUSIVE"
    assert "rice writer event missing exact thread, store instruction, or old/new value" in result["invalid_reasons"]


def test_rice_phase_observation_retains_writer_thread_and_value_transition() -> None:
    from tools.g1_saved_scene_probe import _rice_phase_observation

    result = _rice_phase_observation([
        {"seq": 1, "event": "simulation_update_enter", "thread_global_num": 2, "tick": 24862},
        {"seq": 2, "event": "rice_write", "thread_global_num": 2, "pc_after_write": 0x43ED67,
         "writer_instruction_address": 0x43ED64, "writer_instruction_bytes": "894114",
         "old_rice": 230207, "new_rice": 231007},
        {"seq": 3, "event": "simulation_update_return", "thread_global_num": 2, "tick": 24862,
         "rice": 231007},
    ])
    assert result["status"] == "PASS"
    assert result["rice_writer_threads"] == [2]
    assert result["rice_writer_events"][0]["old_rice"] == 230207
    assert result["rice_writer_events"][0]["new_rice"] == 231007
    assert result["rice_writer_events"][0]["writer_instruction_address"] == 0x43ED64
    assert result["all_writer_quiescence_proven"] is False


def test_rice_gdb_observer_script_is_valid_python_and_declares_read_only_scope(
    tmp_path: Path,
) -> None:
    from tools.g1_saved_scene_probe import _rice_trace_gdb_script

    source = _rice_trace_gdb_script(123, tmp_path, 4.0, 24862)
    compile(source, "rice_writer_observer.py", "exec")
    assert "gdb.BP_WATCHPOINT, gdb.WP_WRITE" in source
    assert "gdb.BP_HARDWARE_BREAKPOINT" in source
    assert 'gdb.parameter("non-stop")' in source
    assert '"simulation_update_enter"' in source
    assert '"simulation_update_return"' in source
    assert '"player_phase_enter"' in source
    assert "return_is_approved_boundary" in source
    assert "gdb.selected_inferior().write_memory" not in source
    assert source.count("if time.time() >= DEADLINE:") == 3


def test_rice_phase_target_tick_selects_owner6_after_warmup() -> None:
    from tools.g1_saved_scene_probe import _rice_phase_target_tick

    target = _rice_phase_target_tick(24577)
    assert target >= 24577 + 64
    assert target & 7 == 6


def test_scroll_phase_observation_accepts_exact_phases_and_quiescent_census() -> None:
    from tools.g1_saved_scene_probe import _scroll_phase_observation

    ticks = [24728, 24824, 24860]
    events = []
    checkpoints = []
    seq = 0
    for tick in ticks:
        call_id = f"4:(1, 2, 3):0:{tick - 1}"
        seq += 1
        events.append({"seq": seq, "event": "simulation_update_enter", "tick": tick,
                       "phase_tick": tick, "thread_global_num": 4, "inferior_pid": 99,
                       "thread_ptid": [99, 4, 0],
                       "call_id": call_id})
        seq += 1
        events.append({"seq": seq, "event": "simulation_update_return", "tick": tick,
                       "phase_tick": tick, "thread_global_num": 4, "inferior_pid": 99,
                       "thread_ptid": [99, 4, 0],
                       "call_id": call_id})
        checkpoints.append({
            "tick": tick,
            "pause": {"status": "PAUSED_AT_PHASE_RETURN", "tick": tick,
                      "inferior_pid": 99, "all_stop_mode": True,
                      "thread_global_num": 4, "thread_ptid": [99, 4, 0],
                      "call_id": call_id, "run_nonce": "run1",
                      "threads": [{"global_num": 4, "ptid": [99, 4, 0],
                                   "inferior_pid": 99, "is_running": False}],
                      "thread_census_complete": True, "phase_context_quiescent": True,
                      "unresolved_phase_calls": [], "nonce": f"n{tick}"},
            "snapshot": {"status": "PASS", "sim_tick_before": tick, "sim_tick_after": tick,
                         "state": {"players": [], "units": []}},
            "release": {"status": "RELEASE", "tick": tick, "nonce": f"n{tick}",
                        "run_nonce": "run1"},
            "ack": {"status": "CONSUMED", "tick": tick, "nonce": f"n{tick}",
                    "run_nonce": "run1", "tick_after": tick, "census_stable": True,
                    "all_threads_stopped": True, "phase_context_quiescent": True,
                    "threads_after": [{"global_num": 4, "ptid": [99, 4, 0],
                                       "inferior_pid": 99, "is_running": False}]},
        })

    result = _scroll_phase_observation(events, checkpoints, expected_pid=99, expected_ticks=ticks)
    assert result["status"] == "PASS"
    assert result["all_writer_quiescence_proven"] is True


@pytest.mark.parametrize("mutation,reason", [
    ("missing_return", "simulation update entry has no return"),
    ("shifted_schedule", "checkpoint order or schedule mismatch"),
    ("running_thread", "running or incomplete thread census"),
    ("stale_pause", "stale or mismatched pause release"),
    ("unresolved_context", "unresolved simulation phase context"),
])
def test_scroll_phase_observation_rejects_incomplete_or_unstable_checkpoint(
    mutation: str, reason: str,
) -> None:
    from tools.g1_saved_scene_probe import _scroll_phase_observation

    ticks = [24728, 24824, 24860]
    events = []
    checkpoints = []
    seq = 0
    for tick in ticks:
        call_id = f"4:(1, 2, 3):0:{tick - 1}"
        seq += 1
        events.append({"seq": seq, "event": "simulation_update_enter", "tick": tick,
                       "phase_tick": tick, "thread_global_num": 4, "inferior_pid": 99,
                       "thread_ptid": [99, 4, 0],
                       "call_id": call_id})
        if mutation != "missing_return" or tick != ticks[1]:
            seq += 1
            events.append({"seq": seq, "event": "simulation_update_return", "tick": tick,
                           "phase_tick": tick, "thread_global_num": 4, "inferior_pid": 99,
                           "thread_ptid": [99, 4, 0],
                           "call_id": call_id})
        checkpoint_tick = tick + 2 if mutation == "shifted_schedule" and tick == ticks[1] else tick
        pause = {"status": "PAUSED_AT_PHASE_RETURN", "tick": checkpoint_tick,
                 "inferior_pid": 99, "all_stop_mode": True,
                 "thread_global_num": 4, "thread_ptid": [99, 4, 0],
                 "call_id": call_id, "run_nonce": "run1",
                 "threads": [{"global_num": 4, "ptid": [99, 4, 0], "inferior_pid": 99,
                              "is_running": mutation == "running_thread" and tick == ticks[0]}],
                 "thread_census_complete": True, "phase_context_quiescent": True,
                 "unresolved_phase_calls": [], "nonce": f"n{tick}"}
        if mutation == "stale_pause" and tick == ticks[0]:
            pause["nonce"] = "old"
        if mutation == "unresolved_context" and tick == ticks[0]:
            pause["phase_context_quiescent"] = False
            pause["unresolved_phase_calls"] = ["other"]
        snapshot = {"status": "PASS", "sim_tick_before": tick, "sim_tick_after": tick,
                    "state": {"players": [], "units": []}}
        checkpoints.append({"tick": checkpoint_tick, "pause": pause, "snapshot": snapshot,
                            "release": {"status": "RELEASE", "tick": tick, "nonce": f"n{tick}",
                                        "run_nonce": "run1"},
                            "ack": {"status": "CONSUMED", "tick": tick, "nonce": f"n{tick}",
                                    "run_nonce": "run1", "tick_after": tick,
                                    "census_stable": True, "all_threads_stopped": True,
                                    "phase_context_quiescent": True,
                                    "threads_after": pause["threads"]}})

    result = _scroll_phase_observation(events, checkpoints, expected_pid=99, expected_ticks=ticks)
    assert result["status"] == "INVALID"
    if reason:
        assert any(reason in item for item in result["invalid_reasons"])


def test_scroll_pause_consumer_waits_for_exact_producer_consumed_ack(tmp_path: Path) -> None:
    from tools.g1_saved_scene_probe import (
        _atomic_write_json,
        _scroll_pause_is_valid,
        _scroll_release_and_ack,
    )

    pause = {
        "status": "PAUSED_AT_PHASE_RETURN", "nonce": "pause-1", "run_nonce": "run-1",
        "tick": 24728, "inferior_pid": 321, "thread_global_num": 5,
        "thread_ptid": [321, 5, 0], "call_id": "5:(321, 5, 0):0:0x401000",
        "all_stop_mode": True, "thread_census_complete": True,
        "phase_context_quiescent": True, "unresolved_phase_calls": [],
        "threads": [{"global_num": 5, "ptid": [321, 5, 0],
                     "inferior_pid": 321, "is_running": False}],
    }
    valid, reason = _scroll_pause_is_valid(
        pause, expected_pid=321, expected_tick=24728, run_nonce="run-1",
    )
    assert valid, reason

    release_path = tmp_path / "release.json"
    ack_path = tmp_path / "ack.json"
    producer_seen: list[dict[str, object]] = []

    def producer() -> None:
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline and not release_path.is_file():
            time.sleep(0.005)
        release = json.loads(release_path.read_text(encoding="utf-8"))
        producer_seen.append(release)
        _atomic_write_json(ack_path, {
            "status": "CONSUMED", "nonce": release["nonce"], "tick": release["tick"],
            "run_nonce": release["run_nonce"], "tick_after": release["tick"],
            "census_stable": True, "all_threads_stopped": True,
            "phase_context_quiescent": True,
            "threads_after": pause["threads"],
        })

    producer_thread = threading.Thread(target=producer)
    producer_thread.start()
    snapshot_calls: list[int] = []
    if valid:
        snapshot_calls.append(24728)
    release, ack = _scroll_release_and_ack(
        release_path, ack_path, nonce=pause["nonce"], tick=24728, run_nonce="run-1",
        expected_threads=pause["threads"],
        timeout=2,
    )
    producer_thread.join(timeout=2)

    assert snapshot_calls == [24728]
    assert producer_seen == [release]
    assert release["status"] == "RELEASE"
    assert ack == {"status": "CONSUMED", "nonce": "pause-1", "tick": 24728,
                   "run_nonce": "run-1", "tick_after": 24728,
                   "census_stable": True, "all_threads_stopped": True,
                   "phase_context_quiescent": True, "threads_after": pause["threads"]}


def test_scroll_pause_consumer_rejects_stale_or_partial_pause_before_snapshot() -> None:
    from tools.g1_saved_scene_probe import _scroll_pause_is_valid

    pause = {"status": "PAUSED_AT_PHASE_RETURN", "nonce": "old", "run_nonce": "prior",
             "tick": 24728, "inferior_pid": 321, "all_stop_mode": True}
    valid, reason = _scroll_pause_is_valid(
        pause, expected_pid=321, expected_tick=24788, run_nonce="current",
    )
    snapshot_calls: list[int] = []
    if valid:
        snapshot_calls.append(24788)
    assert valid is False
    assert "identity mismatch" in reason
    assert snapshot_calls == []


def test_scroll_phase_observation_attributes_pre_tick_return_to_taken_branch() -> None:
    from tools.g1_saved_scene_probe import _scroll_phase_observation

    ticks = [24728]
    call_id = "5:(321, 5, 0):0:0x401000"
    events = [
        {"seq": 1, "event": "pre_tick_branch", "tick": 24727, "thread_global_num": 5,
         "thread_ptid": [321, 5, 0], "inferior_pid": 321, "call_id": call_id,
         "address": "0x41c873", "branch_taken": True},
        {"seq": 2, "event": "simulation_update_no_update_return", "tick": 24727,
         "thread_global_num": 5, "thread_ptid": [321, 5, 0],
         "inferior_pid": 321, "call_id": call_id,
         "attributed_branch_seq": 1, "branch_address": "0x41c873", "branch_taken": True},
        {"seq": 3, "event": "simulation_update_enter", "tick": 24728,
         "phase_tick": 24728, "thread_global_num": 5, "inferior_pid": 321,
         "thread_ptid": [321, 5, 0],
         "call_id": "next-call"},
        {"seq": 4, "event": "simulation_update_return", "tick": 24728,
         "phase_tick": 24728, "thread_global_num": 5, "inferior_pid": 321,
         "thread_ptid": [321, 5, 0],
         "call_id": "next-call"},
    ]
    checkpoint = {
        "tick": 24728,
        "pause": {"status": "PAUSED_AT_PHASE_RETURN", "tick": 24728,
                  "inferior_pid": 321, "all_stop_mode": True, "thread_global_num": 5,
                  "thread_ptid": [321, 5, 0], "call_id": "next-call", "run_nonce": "run",
                  "threads": [{"global_num": 5, "ptid": [321, 5, 0],
                               "inferior_pid": 321, "is_running": False}],
                  "thread_census_complete": True, "phase_context_quiescent": True,
                  "unresolved_phase_calls": [], "nonce": "n1"},
        "snapshot": {"status": "PASS", "sim_tick_before": 24728, "sim_tick_after": 24728},
        "release": {"status": "RELEASE", "tick": 24728, "nonce": "n1", "run_nonce": "run"},
        "ack": {"status": "CONSUMED", "tick": 24728, "nonce": "n1", "run_nonce": "run",
                "tick_after": 24728, "census_stable": True, "all_threads_stopped": True,
                "phase_context_quiescent": True,
                "threads_after": [{"global_num": 5, "ptid": [321, 5, 0],
                                   "inferior_pid": 321, "is_running": False}]},
    }
    result = _scroll_phase_observation(events, [checkpoint], expected_pid=321, expected_ticks=ticks)
    assert result["status"] == "PASS", result["invalid_reasons"]

    events[1] = {**events[1], "call_id": "wrong-call"}
    result = _scroll_phase_observation(events, [checkpoint], expected_pid=321, expected_ticks=ticks)
    assert result["status"] == "INVALID"
    assert any("no-update return lacks" in reason for reason in result["invalid_reasons"])


def test_scroll_phase_observation_rejects_raw_sequence_gap() -> None:
    from tools.g1_saved_scene_probe import _scroll_phase_observation

    events = [
        {"seq": 1, "event": "simulation_update_enter", "tick": 24728,
         "phase_tick": 24728, "call_id": "call-a", "inferior_pid": 321,
         "thread_global_num": 5, "thread_ptid": [321, 5, 0]},
        {"seq": 3, "event": "simulation_update_return", "tick": 24728,
         "phase_tick": 24728, "call_id": "call-a", "inferior_pid": 321,
         "thread_global_num": 5, "thread_ptid": [321, 5, 0]},
    ]
    result = _scroll_phase_observation(events, [], expected_pid=321, expected_ticks=[])

    assert result["status"] == "INVALID"
    assert any("sequence" in reason for reason in result["invalid_reasons"])


def test_scroll_phase_observation_rejects_no_update_return_ptid_substitution() -> None:
    from tools.g1_saved_scene_probe import _scroll_phase_observation

    events = [
        {"seq": 1, "event": "pre_tick_branch", "tick": 24727,
         "thread_global_num": 5, "thread_ptid": [321, 5, 0], "inferior_pid": 321,
         "call_id": "call-a", "address": "0x41c873", "branch_taken": True},
        {"seq": 2, "event": "simulation_update_no_update_return", "tick": 24727,
         "thread_global_num": 5, "thread_ptid": [321, 6, 0], "inferior_pid": 321,
         "call_id": "call-a", "attributed_branch_seq": 1,
         "branch_address": "0x41c873", "branch_taken": True},
    ]
    result = _scroll_phase_observation(events, [], expected_pid=321, expected_ticks=[])

    assert result["status"] == "INVALID"
    assert any("no-update return" in reason for reason in result["invalid_reasons"])


@pytest.mark.parametrize("field", ["thread_global_num", "thread_ptid", "inferior_pid"])
def test_scroll_phase_observation_rejects_entry_return_identity_substitution(field: str) -> None:
    from tools.g1_saved_scene_probe import _scroll_phase_observation

    tick = 24728
    identity: dict[str, object] = {
        "thread_global_num": 5, "thread_ptid": [321, 5, 0], "inferior_pid": 321,
    }
    events = [
        {"seq": 1, "event": "simulation_update_enter", "tick": tick,
         "phase_tick": tick, "call_id": "call-a", **identity},
        {"seq": 2, "event": "simulation_update_return", "tick": tick,
         "phase_tick": tick, "call_id": "call-a", **identity},
    ]
    events[1][field] = ([321, 8, 0] if field == "thread_ptid" else
                        (6 if field == "thread_global_num" else 999))
    ptid = [321, 5, 0]
    census = [{"global_num": 5, "ptid": ptid, "inferior_pid": 321,
               "is_running": False}]
    checkpoint = {
        "tick": tick,
        "pause": {"status": "PAUSED_AT_PHASE_RETURN", "tick": tick, "nonce": "n1",
                  "run_nonce": "r1", "inferior_pid": 321, "thread_global_num": 5,
                  "thread_ptid": ptid, "call_id": "call-a", "all_stop_mode": True,
                  "thread_census_complete": True, "threads": census,
                  "phase_context_quiescent": True, "unresolved_phase_calls": []},
        "snapshot": {"status": "PASS", "sim_tick_before": tick, "sim_tick_after": tick},
        "release": {"status": "RELEASE", "tick": tick, "nonce": "n1", "run_nonce": "r1"},
        "ack": {"status": "CONSUMED", "tick": tick, "tick_after": tick, "nonce": "n1",
                "run_nonce": "r1", "census_stable": True, "all_threads_stopped": True,
                "phase_context_quiescent": True, "threads_after": census},
    }
    result = _scroll_phase_observation(events, [checkpoint], expected_pid=321,
                                       expected_ticks=[tick])
    assert result["status"] == "INVALID"
    assert any("identity mismatch" in item for item in result["invalid_reasons"])


def test_scroll_live_pause_must_match_the_completed_raw_phase(tmp_path: Path) -> None:
    from tools.g1_saved_scene_probe import _scroll_pause_matches_completed_phase

    path = tmp_path / "phase-events.jsonl"
    pause = {"call_id": "call-1", "tick": 24728, "inferior_pid": 321,
             "thread_global_num": 5, "thread_ptid": [321, 5, 0]}
    events = [
        {"seq": 1, "event": "simulation_update_enter", "call_id": "call-1",
         "tick": 24728, "phase_tick": 24728, "inferior_pid": 321,
         "thread_global_num": 5, "thread_ptid": [321, 5, 0]},
        {"seq": 2, "event": "simulation_update_return", "call_id": "call-1",
         "tick": 24728, "phase_tick": 24728, "inferior_pid": 321,
         "thread_global_num": 5, "thread_ptid": [321, 5, 0]},
    ]
    path.write_text("".join(json.dumps(event) + "\n" for event in events))
    assert _scroll_pause_matches_completed_phase(path, pause) == (True, "PASS")
    events[1]["thread_ptid"] = [321, 6, 0]
    path.write_text("".join(json.dumps(event) + "\n" for event in events))
    valid, reason = _scroll_pause_matches_completed_phase(path, pause)
    assert valid is False
    assert "does not match" in reason


@pytest.mark.parametrize("defect", ["sequence_gap", "no_update_ptid"])
def test_scroll_live_preflight_rejects_invalid_raw_before_snapshot_or_input(
    tmp_path: Path, defect: str,
) -> None:
    from tools.g1_saved_scene_probe import _scroll_live_checkpoint_preflight

    path = tmp_path / "phase-events.jsonl"
    events = [
        {"seq": 1, "event": "pre_tick_branch", "tick": 24727,
         "inferior_pid": 321, "thread_global_num": 5, "thread_ptid": [321, 5, 0],
         "call_id": "call-0", "address": "0x41c873", "branch_taken": True},
        {"seq": 2, "event": "simulation_update_no_update_return", "tick": 24727,
         "inferior_pid": 321, "thread_global_num": 5, "thread_ptid": [321, 5, 0],
         "call_id": "call-0", "attributed_branch_seq": 1,
         "branch_address": "0x41c873", "branch_taken": True},
        {"seq": 3, "event": "simulation_update_enter", "tick": 24728,
         "phase_tick": 24728, "inferior_pid": 321, "thread_global_num": 5,
         "thread_ptid": [321, 5, 0], "call_id": "call-1"},
        {"seq": 4, "event": "simulation_update_return", "tick": 24728,
         "phase_tick": 24728, "inferior_pid": 321, "thread_global_num": 5,
         "thread_ptid": [321, 5, 0], "call_id": "call-1"},
    ]
    if defect == "sequence_gap":
        events[1]["seq"] = 3
    else:
        events[1]["thread_ptid"] = [321, 6, 0]
    path.write_text("".join(json.dumps(event) + "\n" for event in events))
    pause = {
        "status": "PAUSED_AT_PHASE_RETURN", "nonce": "n1", "run_nonce": "r1",
        "tick": 24728, "inferior_pid": 321, "thread_global_num": 5,
        "thread_ptid": [321, 5, 0], "call_id": "call-1", "all_stop_mode": True,
        "thread_census_complete": True, "phase_context_quiescent": True,
        "unresolved_phase_calls": [],
        "threads": [{"inferior_pid": 321, "global_num": 5, "ptid": [321, 5, 0],
                     "is_running": False}],
    }
    snapshot_calls: list[str] = []
    input_calls: list[str] = []
    valid, reason = _scroll_live_checkpoint_preflight(
        path, pause, expected_pid=321, expected_tick=24728, run_nonce="r1",
    )
    if valid:
        snapshot_calls.append("snapshot")
        input_calls.append("input")

    assert valid is False, reason
    assert snapshot_calls == []
    assert input_calls == []


def test_scroll_gdb_producer_and_host_consumer_complete_real_file_handshake(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    from tools.g1_saved_scene_probe import (
        _scroll_pause_is_valid,
        _scroll_phase_observation,
        _scroll_release_and_ack,
        _scroll_phase_trace_gdb_script,
    )

    ticks = [24728, 24824, 24860]
    control = tmp_path / "control"
    control.mkdir()

    class FakeFrame:
        def __init__(self, pc: int, caller: bool = False) -> None:
            self._pc = pc
            self._caller = caller

        def older(self):
            if self._caller:
                return None
            unwind_pc = 0x45880000 if memory["pc"] == 0x41C8CE else 0x4243D7
            return FakeFrame(unwind_pc, caller=True)

        def pc(self) -> int:
            return self._pc

        def level(self) -> int:
            return 1 if self._caller else 0

    class FakeInferior:
        pid = 321

        def read_memory(self, address: int, size: int) -> bytes:
            assert address == 0x008924B8 and size == 4
            return memory["tick"].to_bytes(4, "little", signed=True)

        def threads(self):
            return [fake_thread]

    class FakeThread:
        global_num = 5
        ptid = (321, 5, 0)
        inferior = FakeInferior()

        def is_running(self) -> bool:
            return False

    memory = {"tick": 24727, "pc": 0, "schedule_index": 0}
    fake_thread = FakeThread()
    breakpoints = []

    class FakeBreakpoint:
        def __init__(self, location: str, kind: int) -> None:
            self.location = int(location.removeprefix("*"), 16)
            breakpoints.append(self)

    class FakeGdb(ModuleType):
        BP_HARDWARE_BREAKPOINT = 1
        BP_WATCHPOINT = 2
        WP_WRITE = 3
        Breakpoint = FakeBreakpoint

        def selected_inferior(self):
            return fake_thread.inferior

        def selected_thread(self):
            return fake_thread

        def selected_frame(self):
            return FakeFrame(memory["pc"])

        def parameter(self, name: str):
            assert name == "non-stop"
            return False

        def parse_and_eval(self, expression: str):
            assert expression == "$eflags"
            return 0x40

        def execute(self, command: str):
            if command == "detach":
                return
            assert command == "continue"
            callbacks = {item.location: item for item in breakpoints}
            schedule = [(24727, (0x41C873, 0x41C961))]
            for tick in ticks:
                schedule.append((tick, (0x41C8CE, 0x41C961)))
            while memory["schedule_index"] < len(schedule):
                tick, pcs = schedule[memory["schedule_index"]]
                memory["schedule_index"] += 1
                memory["tick"] = tick
                for pc in pcs:
                    memory["pc"] = pc
                    if callbacks[pc].stop():
                        return
            raise AssertionError("GDB producer did not stop at a target checkpoint")

    fake_gdb = FakeGdb("gdb")
    monkeypatch.setitem(sys.modules, "gdb", fake_gdb)
    source = _scroll_phase_trace_gdb_script(321, control, ticks, 10.0, "run-321")
    producer_error: list[BaseException] = []

    def run_producer() -> None:
        try:
            exec(compile(source, "generated_scroll_observer.py", "exec"), {})
        except BaseException as exc:  # preserve thread failures for the test assertion
            producer_error.append(exc)

    producer = threading.Thread(target=run_producer)
    producer.start()
    checkpoints = []
    for tick in ticks:
        pause_path = control / "paused.json"
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline and not pause_path.is_file():
            time.sleep(0.005)
        if not pause_path.is_file():
            producer.join(timeout=1)
            assert producer_error == [], repr(producer_error)
            pytest.fail(f"observer did not publish pause; files={list(control.iterdir())}")
        pause = json.loads(pause_path.read_text(encoding="utf-8"))
        valid, reason = _scroll_pause_is_valid(
            pause, expected_pid=321, expected_tick=tick, run_nonce="run-321",
        )
        assert valid, reason
        snapshot = {"status": "PASS", "sim_tick_before": tick, "sim_tick_after": tick,
                    "state": {"players": [], "units": []}}
        release, ack = _scroll_release_and_ack(
            control / "release.json", control / "ack.json", nonce=pause["nonce"],
            tick=tick, run_nonce="run-321", expected_threads=pause["threads"], timeout=2,
        )
        checkpoints.append({"tick": tick, "pause": pause, "snapshot": snapshot,
                            "release": release, "ack": ack})
        (control / "ack.json").unlink()
    producer.join(timeout=2)
    assert not producer.is_alive()
    assert producer_error == []
    events = [json.loads(line) for line in (control / "phase-events.jsonl").read_text().splitlines()]
    summary = json.loads((control / "summary.json").read_text())
    assert summary["status"] == "CAPTURED"
    assert any(row["event"] == "simulation_update_no_update_return" for row in events)
    assert _scroll_phase_observation(
        events, checkpoints, expected_pid=321, expected_ticks=ticks,
    )["status"] == "PASS"


def test_scroll_checkpoint_state_comparison_keeps_all_player_and_unit_fields() -> None:
    from tools.g1_saved_scene_probe import _scroll_checkpoint_state_diffs

    ticks = [24728]
    before = [{"tick": 24728, "snapshot": {
        "sim_tick_before": 24728, "sim_tick_after": 24728,
        "state": {"players": [{"owner": 0, "rice": 10}],
                  "units": [{"slot": 4, "x": 10, "hp": 100}]},
    }}]
    after = [{"tick": 24728, "snapshot": {
        "sim_tick_before": 24728, "sim_tick_after": 24728,
        "state": {"players": [{"owner": 0, "rice": 11}],
                  "units": [{"slot": 4, "x": 10, "hp": 90}]},
    }}]
    diff = _scroll_checkpoint_state_diffs(before, after, ticks)[0]
    assert diff["players_changed"][0]["before"]["rice"] == 10
    assert diff["players_changed"][0]["after"]["rice"] == 11
    assert diff["units_changed"][0]["before"]["hp"] == 100
    assert diff["units_changed"][0]["after"]["hp"] == 90


def test_scroll_phase_gdb_script_is_syntactically_valid_and_read_only(tmp_path: Path) -> None:
    from tools.g1_saved_scene_probe import _scroll_phase_trace_gdb_script

    source = _scroll_phase_trace_gdb_script(123, tmp_path, [24728, 24824, 24860], 240, "run-nonce")
    compile(source, "scroll_phase_observer.py", "exec")
    assert "gdb.BP_HARDWARE_BREAKPOINT" in source
    assert "gdb.BP_WATCHPOINT" not in source
    assert "selected_inferior().write_memory" not in source
    assert "thread_census_complete" in source
    assert "unresolved_phase_calls" in source
    assert "pre_tick_branch" in source
    assert "simulation_update_no_update_return" in source
    assert "os.replace(temporary, path)" in source
    assert "return_is_approved_boundary" not in source


def test_fixed_camera_coverage_requires_40_samples_and_tracks_first_last_windows(
    tmp_path: Path,
) -> None:
    from tools.g1_saved_scene_probe import _fixed_camera_coverage_summary

    trace = tmp_path / "fixed.jsonl"
    rows = [{"event": "mirror2x_present", "program_state": 3, "camera": [158, 101],
             "covered_pixels": 300_000, "stale_pixels": 0} for _ in range(40)]
    trace.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    result = _fixed_camera_coverage_summary(trace, [158, 101])
    assert result["status"] == "PASS"
    assert result["sample_count"] == 40
    assert result["first20_p50"] == result["last20_p50"] == 300_000

    trace.write_text("".join(json.dumps(row) + "\n" for row in rows[:39]), encoding="utf-8")
    assert _fixed_camera_coverage_summary(trace, [158, 101])["status"] == "INCOMPLETE"


def test_gdb_free_scroll_lane_uses_same_closed_loop_keys_and_layer_metrics() -> None:
    source = (Path(__file__).parents[1] / "tools/g1_saved_scene_probe.py").read_text(
        encoding="utf-8"
    )
    assert 'parser.add_argument("--terrain-scroll"' in source
    assert 'for slot_name, key in zip(("down", "right"), terrain_scroll_keys)' in source
    assert "_send_key_edge(display, env, key, down=True)" in source
    assert "_send_key_edge(display, env, key, down=False)" in source
    assert "_close_scroll_input(display)" in source
    assert "XCloseDisplay(connection)" in source
    assert "_wait_for_scroll_settled(" in source
    assert '"layer_move_unsupported"' in source
    assert '"layer_transfer_calls"' in source
    assert '"hd_mask_outside_diff_subpixels"' in source
    assert "_arm_and_wait_scroll_receiver(scroll_arm_path, scroll_ready_path)" in source
    assert "_send_scroll_until_camera_change(" in source
    assert "_wait_for_exact_tick(pid, input_target)" in source
    assert "_wait_for_exact_tick(pid, observation_target)" in source
    assert "_read_batched_scene(pid, runtime_read)" in source
    assert '"sim_tick_before"' in source and '"sim_tick_after"' in source
    assert '"monotonic_before_ns"' in source and '"monotonic_after_ns"' in source
    assert "_wait_for_terrain_scroll_coverage(" in source
    scroll_loop = source[source.index("for slot_name, key in zip(", source.index('def _run_lane')):
                         source.index("        def selection()", source.index('def _run_lane'))]
    assert scroll_loop.index("_trace_line_count(trace_path)") < scroll_loop.index(
        "_wait_for_exact_tick(pid, input_target)"
    )
    assert scroll_loop.index('scroll_arm_path.write_text("armed\\n"') < scroll_loop.index(
        "_wait_for_exact_tick(pid, input_target)"
    )
    assert "_wait_for_exact_tick(pid, observation_target)" in scroll_loop
    assert "_wait_for_terrain_scroll_coverage(" in scroll_loop
    assert '"exact_one_step_camera": exact_one_step' in source
    assert "_terrain_scroll_pair_parity(" in source
    assert "_wait_fixed_camera_coverage(trace_path, camera_before_sequence)" in source


def test_exact_common_tick_wait_rejects_missed_target(monkeypatch: pytest.MonkeyPatch) -> None:
    import tools.g1_saved_scene_probe as probe

    ticks = iter((41, 43))
    monkeypatch.setattr(probe, "_read_sim_tick", lambda _pid: next(ticks))
    assert probe._wait_for_exact_tick(1, 41)["status"] == "PASS"

    ticks = iter((41, 43))
    monkeypatch.setattr(probe, "_read_sim_tick", lambda _pid: next(ticks))
    missed = probe._wait_for_exact_tick(1, 42)
    assert missed["status"] == "INVALID"
    assert missed["reason"] == "target tick missed"


def test_live_scene_sampler_accepts_only_coherent_target_tick(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import tools.g1_saved_scene_probe as probe

    monkeypatch.setattr(probe, "_wait_for_exact_tick", lambda _pid, tick: {
        "status": "PASS", "target_tick": tick, "observed_tick": tick,
    })
    monkeypatch.setattr(probe, "_read_batched_scene", lambda _pid, _read: {
        "status": "PASS", "program_state_before": 3, "program_state_after": 3,
        "sim_tick_before": 24600, "sim_tick_after": 24600,
        "state": {"tick": 24600, "units": []},
    })

    result = probe._read_scene_at_exact_tick(1, 24600, lambda _address, _size: b"")

    assert result["status"] == "PASS"
    assert result["source"] == "live_common_tick"
    assert result["target_tick"] == 24600
    assert result["state"]["tick"] == 24600


@pytest.mark.parametrize("snapshot", [
    {"status": "PASS", "program_state_before": 3, "program_state_after": 3,
     "sim_tick_before": 24599, "sim_tick_after": 24600, "state": {"units": []}},
    {"status": "PASS", "program_state_before": 3, "program_state_after": 3,
     "sim_tick_before": 24601, "sim_tick_after": 24601, "state": {"units": []}},
    {"status": "PASS", "program_state_before": 3, "program_state_after": 27,
     "sim_tick_before": 24600, "sim_tick_after": 24600, "state": {"units": []}},
])
def test_live_scene_sampler_holds_tick_cross_or_non_ps3_snapshot(
    monkeypatch: pytest.MonkeyPatch, snapshot: dict[str, object],
) -> None:
    import tools.g1_saved_scene_probe as probe

    monkeypatch.setattr(probe, "_wait_for_exact_tick", lambda _pid, tick: {
        "status": "PASS", "target_tick": tick, "observed_tick": tick,
    })
    monkeypatch.setattr(probe, "_read_batched_scene", lambda _pid, _read: snapshot)

    result = probe._read_scene_at_exact_tick(1, 24600, lambda _address, _size: b"")

    assert result["status"] == "INVALID"
    assert result["target_tick"] == 24600
    assert result["reason"] == "target tick not coherently bracketed"


def test_live_scene_sampler_does_not_read_after_missed_target(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import tools.g1_saved_scene_probe as probe

    monkeypatch.setattr(probe, "_wait_for_exact_tick", lambda _pid, tick: {
        "status": "INVALID", "target_tick": tick,
        "observed_tick": tick + 1, "reason": "target tick missed",
    })
    monkeypatch.setattr(
        probe, "_read_batched_scene",
        lambda *_args: pytest.fail("must not sample after the target tick was missed"),
    )

    result = probe._read_scene_at_exact_tick(1, 24600, lambda _address, _size: b"")

    assert result["status"] == "INVALID"
    assert result["barrier"]["reason"] == "target tick missed"


def test_save006_initial_scene_uses_pinned_common_tick_sampler() -> None:
    source = (Path(__file__).parents[1] / "tools/g1_saved_scene_probe.py").read_text(
        encoding="utf-8"
    )
    load_scene = source[source.index('if fixture == "save006":', source.index('def _run_lane')):]
    load_scene = load_scene[:load_scene.index("if rice_phase_diagnostic is not None:")]
    save006_branch = load_scene[:load_scene.index("        else:")]

    assert "SAVE006_INITIAL_SCENE_TICK = 24600" in source
    assert "_read_scene_at_exact_tick(\n                pid, SAVE006_INITIAL_SCENE_TICK, runtime_read," in load_scene
    assert '"sim_tick_before", "sim_tick_after"' in load_scene
    assert 'raise ProbeError(f"initial save006 scene sample invalid:' in load_scene
    assert "_g1_scene_snapshot(loaded_detailed, runtime_read)" not in save006_branch


def test_saved_scene_fixture_contract_is_pinned() -> None:
    assert SAVE_NAME == "save006.dat"
    assert len(SAVE_SHA256) == 64
    assert all(char in "0123456789abcdef" for char in SAVE_SHA256)


def test_present_p95_recomputes_from_unclipped_window_histogram(tmp_path: Path) -> None:
    trace = tmp_path / "trace.jsonl"
    rows = [{
        "event": "perf_window_meta", "program_state": 3,
        "count": 100, "dropped": 0, "first_tick_ms": 1000,
        "last_tick_ms": 21000,
    }, {"event": "perf_window_histogram", "program_state": 3,
        "elapsed_ms": 1, "count": 94},
        {"event": "perf_window_histogram", "program_state": 3,
         "elapsed_ms": 9, "count": 6}]
    trace.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    result = _performance_present_metrics(trace)
    assert result["status"] == "PASS"
    assert result["sample_count"] == 100
    assert result["sample_span_ms"] == 20000
    assert result["p95_ms"] == 9
    assert _histogram_percentile(result["histogram_ms"], 50) == 1


def test_present_histogram_rejects_drops_and_count_mismatch(tmp_path: Path) -> None:
    trace = tmp_path / "trace.jsonl"
    rows = [{
        "event": "perf_window_meta", "program_state": 3,
        "count": 2, "dropped": 1, "first_tick_ms": 100,
        "last_tick_ms": 200,
    }, {"event": "perf_window_histogram", "program_state": 3,
        "elapsed_ms": 1, "count": 2}]
    trace.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    assert _performance_present_metrics(trace)["status"] == "INVALID"


def test_performance_window_is_opt_in_and_fixed_length() -> None:
    from tools.g1_saved_scene_probe import PERFORMANCE_WINDOW_SECONDS

    assert PERFORMANCE_WINDOW_SECONDS == 20.0
    assert "PERF_WINDOW_PATH" in (Path(__file__).parents[1]
                                   / "tools/inmm_stub/direct_draw_trace.c").read_text()


@pytest.mark.parametrize("performance_status", ["FAIL", "INVALID", None])
def test_requested_performance_gate_blocks_pair_pass(performance_status: str | None) -> None:
    pair: dict[str, object] = {
        "scene_state_equal": True,
        "v2_capture_gate": {"status": "PASS"},
        "v2s_capture_gate": {"status": "PASS"},
        "v2q_capture_gate": {"status": "PASS"},
    }
    if performance_status is not None:
        pair["performance_comparison"] = {"status": performance_status}

    assert _pair_status(
        pair, performance_requested=True, hd_source="none",
        scale2x_gate_status="PASS", terrain_scroll=False,
    ) == "HOLD"


def test_requested_performance_pass_allows_pair_pass() -> None:
    pair: dict[str, object] = {
        "scene_state_equal": True,
        "candidate": {
            "trace_close": {"status": "PASS"},
            "trace_summary": {"status": "PASS", "summary_count": 1,
                              "dropped_count": 0, "detach": "complete", "flush": "complete"},
        },
        "v2_capture_gate": {"status": "PASS"},
        "v2s_capture_gate": {"status": "PASS"},
        "v2q_capture_gate": {"status": "PASS"},
        "input_effect_comparison": {"status": "PASS"},
        "performance_comparison": {"status": "PASS"},
    }

    assert _pair_status(
        pair, performance_requested=True, hd_source="none",
        scale2x_gate_status="PASS", terrain_scroll=False,
    ) == "PASS"


def test_unrequested_performance_gate_remains_optional() -> None:
    pair: dict[str, object] = {
        "scene_state_equal": True,
        "candidate": {
            "trace_close": {"status": "PASS"},
            "trace_summary": {"status": "PASS", "summary_count": 1,
                              "dropped_count": 0, "detach": "complete", "flush": "complete"},
        },
        "v2_capture_gate": {"status": "PASS"},
        "v2s_capture_gate": {"status": "PASS"},
        "v2q_capture_gate": {"status": "PASS"},
        "input_effect_comparison": {"status": "PASS"},
    }

    assert _pair_status(
        pair, performance_requested=False, hd_source="none",
        scale2x_gate_status="PASS", terrain_scroll=False,
    ) == "PASS"


@pytest.mark.parametrize("input_verdict", [None, "UNKNOWN", "HOLD", "FAIL"])
def test_standard_pair_requires_registered_input_effect_pass(
    input_verdict: str | None,
) -> None:
    pair: dict[str, object] = {
        "scene_state_equal": True,
        "candidate": {
            "trace_close": {"status": "PASS"},
            "trace_summary": {"status": "PASS", "summary_count": 1,
                              "dropped_count": 0, "detach": "complete", "flush": "complete"},
        },
        "v2_capture_gate": {"status": "PASS"},
        "v2s_capture_gate": {"status": "PASS"},
        "v2q_capture_gate": {"status": "PASS"},
    }
    if input_verdict is not None:
        pair["input_effect_comparison"] = {"status": input_verdict}

    assert _pair_status(
        pair, performance_requested=False, hd_source="none",
        scale2x_gate_status="PASS", terrain_scroll=False,
    ) == "HOLD"


def test_diagnostic_pair_can_skip_semantic_input_gate() -> None:
    pair: dict[str, object] = {
        "scene_state_equal": True,
        "candidate": {
            "trace_close": {"status": "PASS"},
            "trace_summary": {"status": "PASS", "summary_count": 1,
                              "dropped_count": 0, "detach": "complete", "flush": "complete"},
        },
        "v2_capture_gate": {"status": "PASS"},
        "v2s_capture_gate": {"status": "PASS"},
        "v2q_capture_gate": {"status": "PASS"},
    }

    assert _pair_status(
        pair, performance_requested=False, hd_source="none",
        scale2x_gate_status="PASS", terrain_scroll=False,
        input_effects_required=False,
    ) == "PASS"


@pytest.mark.parametrize(
    ("trace_close", "trace_summary"),
    [
        ({"status": "FAIL"}, {"status": "PASS", "summary_count": 1,
                                "dropped_count": 0, "detach": "complete", "flush": "complete"}),
        ({"status": "PASS"}, {"status": "FAIL", "summary_count": 0}),
        ({"status": "PASS"}, {"status": "PASS", "summary_count": 1,
                                "dropped_count": 1, "detach": "complete", "flush": "complete"}),
        ({"status": "PASS"}, {"status": "PASS", "summary_count": 1,
                                "dropped_count": 0, "detach": "complete", "flush": "pending"}),
    ],
)
def test_pair_status_requires_candidate_owned_close_and_complete_summary(
    trace_close: dict[str, str], trace_summary: dict[str, object],
) -> None:
    pair: dict[str, object] = {
        "scene_state_equal": True,
        "candidate": {"trace_close": trace_close, "trace_summary": trace_summary},
        "v2_capture_gate": {"status": "PASS"},
        "v2s_capture_gate": {"status": "PASS"},
        "v2q_capture_gate": {"status": "PASS"},
    }

    assert _pair_status(
        pair, performance_requested=False, hd_source="none",
        scale2x_gate_status="PASS", terrain_scroll=False,
    ) == "HOLD"


def test_trace_close_summary_checks_run_binding_and_flush(tmp_path: Path) -> None:
    trace = tmp_path / "trace.jsonl"
    trace.write_text("\n".join(json.dumps(row) for row in [
        {"event": "install", "run_id": "g1-saved-candidate"},
        {"event": "summary", "run_id": "g1-saved-candidate", "install_status": "detached",
         "dropped_count": 0, "detach": "complete", "flush": "complete"},
        {"event": "textout_iat_restore", "run_id": "g1-saved-candidate"},
    ]) + "\n", encoding="utf-8")

    assert _trace_close_summary(trace, "g1-saved-candidate")["status"] == "PASS"
    assert _trace_close_summary(trace, "g1-saved-baseline")["status"] == "FAIL"


def test_user_trial_disables_present_trace_but_keeps_owned_run_id() -> None:
    env = {
        "SYW2_G1_PRESENT_TRACE": "1",
        "SYW2_G1_TRACE_RUN_ID": "g1-saved-candidate",
    }

    _disable_present_trace(env)

    assert "SYW2_G1_PRESENT_TRACE" not in env
    assert env["SYW2_G1_TRACE_RUN_ID"] == "g1-saved-candidate"


def test_scene_identity_excludes_tick_but_keeps_state() -> None:
    before = {"ps": 3, "tick": 12, "players": [{"owner": 0, "nation": 1, "rice": 1}],
              "units": [{"slot": 2, "type": 3, "owner": 0, "internal_id": 7, "x": 1}]}
    after = {"ps": 3, "tick": 99, "players": [{"owner": 0, "nation": 1, "rice": 999}],
             "units": [{"slot": 2, "type": 3, "owner": 0, "internal_id": 7, "x": 99}]}
    assert _scene_identity(before) == _scene_identity(after)


def test_probe_source_has_no_binary_write_path() -> None:
    source = Path(__file__).parents[1] / "tools" / "g1_saved_scene_probe.py"
    text = source.read_text(encoding="utf-8")
    assert "private_save" in text
    assert "shutil.copy2(fixture_file, private_save)" in text
    assert "write_bytes" not in text


def test_production_effect_requires_owner0_type58_and_type31_native_queue() -> None:
    from tools.g1_saved_scene_probe import _production_issue_acceptance

    before = {"status": "OBSERVED", "selected_slot": 1199, "slot": 1199,
              "owner": 0, "type": 58, "command": 1,
              "production_type": 31, "progress": 100, "reserved": 423,
              "rice": 1000, "wood": 500}
    issue = {**before, "command": 15, "progress": 13,
             "reserved": 433, "rice": 200, "wood": 200}
    spec = {"population": 10, "rice": 800, "wood": 300}
    accepted = _production_issue_acceptance(before, issue, issue, expected_slot=1199,
                                            producer_type=58, queue_type=31, spec=spec)
    assert accepted["status"] == "PASS"
    assert accepted["issue_transition_observed"] is True
    assert not _production_effect(before, {**issue, "production_type": 7},
                                  producer_type=58, queue_type=31, spec=spec)
    assert not _production_effect({**before, "owner": 1}, issue,
                                  producer_type=58, queue_type=31, spec=spec)
    assert not _production_effect(before, {**issue, "rice": 840},
                                  producer_type=58, queue_type=31, spec=spec)
    assert not _production_effect(before, {**issue, "progress": 100},
                                  producer_type=58, queue_type=31, spec=spec)
    assert not _production_effect(before, {**issue, "command": 1},
                                  producer_type=58, queue_type=31, spec=spec)


def test_production_control_keeps_natural_resource_delta_but_blocks_unit_change() -> None:
    from tools.g1_saved_scene_probe import _production_control_status, _production_global_delta

    before = {"status": "OBSERVED", "selected_slot": 1199, "owner": 0, "type": 58,
              "command": 1, "production_type": 31, "progress": 100,
              "reserved": 423, "rice": 1000, "wood": 500}
    after = {**before, "rice": 1640}
    assert _production_control_status(before, after, selected_slot=1199,
                                      producer_type=58) == "PASS"
    assert _production_global_delta(before, after) == {
        "rice": 640, "wood": 0, "reserved": 0,
    }
    assert _production_control_status(before, {**after, "progress": 99},
                                      selected_slot=1199, producer_type=58) == "UNKNOWN"
    assert _production_control_status(before, {**after, "command": 15},
                                      selected_slot=1199, producer_type=58) == "UNKNOWN"


def test_production_issue_cost_accepts_only_exact_adjacent_sample_delta() -> None:
    from tools.g1_saved_scene_probe import _production_issue_acceptance

    previous = {"status": "OBSERVED", "selected_slot": 1199, "slot": 1199,
                "owner": 0, "type": 58, "command": 1, "production_type": 31,
                "progress": 100, "reserved": 423, "rice": 1000, "wood": 500}
    issued = {**previous, "command": 15, "progress": 10, "reserved": 433,
              "rice": 200, "wood": 200}
    spec = {"population": 10, "rice": 800, "wood": 300}
    assert _production_issue_acceptance(previous, issued, issued, expected_slot=1199,
                                        producer_type=58, queue_type=31,
                                        spec=spec)["cost_match"] == "prev_to_a"
    inexact = _production_issue_acceptance(previous, {**issued, "rice": 840},
                                           {**issued, "rice": 840}, expected_slot=1199,
                                           producer_type=58, queue_type=31, spec=spec)
    assert inexact["status"] == "UNKNOWN"
    assert inexact["issue_transition_observed"] is True


def test_inexact_issue_cost_still_authorizes_native_completion_observation() -> None:
    from tools.g1_saved_scene_probe import _should_observe_production_completion

    click = {"logical": [668, 540]}
    target = {"valid": True}
    inexact_transition = {"status": "UNKNOWN", "cost_match": "INEXACT",
                         "issue_transition_observed": True}
    no_transition = {"status": "UNKNOWN", "issue_transition_observed": False}

    assert _should_observe_production_completion(click, target, inexact_transition)
    assert not _should_observe_production_completion(None, target, inexact_transition)
    assert not _should_observe_production_completion(click, {"valid": False}, inexact_transition)
    assert not _should_observe_production_completion(click, target, no_transition)


def test_production_spec_reads_three_signed_words() -> None:
    from tools.g1_saved_scene_probe import PRODUCTION_SPEC_ADDRESS, _production_spec

    raw = (-2).to_bytes(2, "little", signed=True) + (800).to_bytes(2, "little") + (300).to_bytes(2, "little")
    def read_memory(address: int, size: int) -> bytes:
        assert address == PRODUCTION_SPEC_ADDRESS and size == 6
        return raw

    assert _production_spec(read_memory) == {"population": -2, "rice": 800, "wood": 300}


def test_minimap_command_settled_requires_every_unit_to_consume_the_order() -> None:
    from tools.g1_saved_scene_probe import _minimap_command_settled

    # lap966/969 raw: idle before, intermediate (xy staged, command not yet
    # consumed), then consumed (command 1 -> 3).
    before = [
        {"status": "OBSERVED", "slot": 124, "command": 1,
         "pending_command": 0x01000001, "pending_xy": 6553741},
        {"status": "OBSERVED", "slot": 140, "command": 1,
         "pending_command": 0x00010001, "pending_xy": 0},
    ]
    intermediate = [
        {**before[0], "pending_command": 0x01000003, "pending_xy": 5767258},
        {**before[1], "pending_command": 0x01000003, "pending_xy": 5767259},
    ]
    consumed = [
        {**intermediate[0], "command": 3, "pending_command": 0x01000001},
        {**intermediate[1], "command": 3, "pending_command": 0x01000001},
    ]
    assert _minimap_command_settled(before, intermediate) is False
    assert _minimap_command_settled(before, consumed) is True
    assert _minimap_command_settled(before, before) is False
    assert _minimap_command_settled(before, [consumed[0], intermediate[1]]) is False
    assert _minimap_command_settled(before, [consumed[0]]) is False
    assert _minimap_command_settled(before, [
        consumed[0], {"status": "UNKNOWN", "slot": 140},
    ]) is False
    assert _minimap_command_settled([], []) is False


def test_minimap_effect_requires_valid_selected_unit_witnesses() -> None:
    from patches.population import runtime_driver
    from tools.g1_saved_scene_probe import _minimap_command_effect, _unit_witness

    before = [
        {"status": "OBSERVED", "slot": 151, "owner": 0, "type": 12,
         "pending_command": 0, "pending_xy": 0x00010002},
        {"status": "OBSERVED", "slot": 170, "owner": 0, "type": 13,
         "pending_command": 0, "pending_xy": 0x00030004},
    ]
    after = [
        {**before[0], "pending_command": 3, "pending_xy": 0x00050006},
        {**before[1], "pending_command": 3, "pending_xy": 0x00070008},
    ]
    result = _minimap_command_effect(before, after)
    assert result["all_selected_changed"] is True
    assert result["selected_count"] == result["observed_count"] == 2

    assert _minimap_command_effect([], [])["all_selected_changed"] is False
    assert _minimap_command_effect(before, [after[0]])["all_selected_changed"] is False
    assert _unit_witness({"units": []}, None) == {"status": "UNKNOWN", "slot": None}

    address = runtime_driver.STOCK_POOL[1] + 151 * 0x758
    def read_memory(at: int, size: int) -> bytes:
        assert size == 4
        if at == address + 0x384:
            return (0x01000003).to_bytes(4, "little")
        if at == address + 0x388:
            return (0x000A000B).to_bytes(4, "little")
        raise AssertionError(f"unexpected unit witness read {at:#x}")

    witness = _unit_witness(
        {"units": [{"slot": 151, "owner": 0, "type": 12}]}, 151, read_memory,
    )
    assert witness["pending_command"] == 0x01000003
    assert witness["pending_xy"] == 0x000A000B


def test_input_comparison_does_not_promote_unknown_or_gate_zero() -> None:
    def lane(minimap_result: str = "PASS", *, queue_type: int = 31,
             cost: tuple[int, int, int] = (-800, -300, 10)) -> dict[str, object]:
        return {"actions": [
            {"tag": "selection", "result": "PASS", "after": {"selected_slots": [151]}},
            {"tag": "empty_click", "result": "PASS", "after": {"count": 0}},
            {"tag": "drag", "result": "PASS", "after": {"selected_slots": [151, 152]},
             "capture_binding": {"status": "PASS"}},
            {"tag": "minimap", "result": minimap_result, "camera_after": [12, 34],
             "gate": {"before_hex": "00000000", "restored_hex": "00000000"}},
            {"tag": "production", "control_result": "PASS", "result": "PASS",
             "issue_result": "PASS", "spec": {"population": 10, "rice": 800, "wood": 300},
             "issue_acceptance": {"issue_cost": {"rice": cost[0], "wood": cost[1],
                                                   "reserved": cost[2]}},
             "target": {"selection": {"selected_slot": 1199}, "expected_type": 58},
             "after_witness": {"type": 58, "production_type": queue_type},
             "completion": {"status": "PASS", "new_slots": [1200]}},
        ]}
    assert _compare_input_effects(lane(), lane())["status"] == "PASS"
    assert _compare_input_effects(lane("UNKNOWN"), lane())["status"] == "HOLD"
    assert _compare_input_effects(lane(), lane(queue_type=7))["checks"]["production_effect"] is False
    assert _compare_input_effects(lane(), lane(cost=(-160, -300, 10)))["checks"]["production_effect"] is False


def test_production_control_requires_observed_owner0_producer_without_effect() -> None:
    from tools.g1_saved_scene_probe import _production_control_status

    before = {
        "status": "OBSERVED", "selected_slot": 1199, "slot": 1199,
        "owner": 0, "type": 58,
        "command": 1, "production_type": 31, "progress": 100,
        "reserved": 0, "rice": 100, "wood": 50,
    }
    after = dict(before)
    assert _production_control_status(before, after, selected_slot=1199,
                                      producer_type=58) == "PASS"
    assert _production_control_status({"status": "UNKNOWN"}, after, selected_slot=1199,
                                      producer_type=58) == "UNKNOWN"
    assert _production_control_status(before, {**after, "owner": 1}, selected_slot=1199,
                                      producer_type=58) == "UNKNOWN"
    assert _production_control_status(before, {**after, "type": None}, selected_slot=1199,
                                      producer_type=58) == "UNKNOWN"
    assert _production_control_status(before, {**after, "progress": 99}, selected_slot=1199,
                                      producer_type=58) == "UNKNOWN"


def test_production_selection_requires_a_real_nonempty_owner0_producer() -> None:
    from tools.g1_saved_scene_probe import _valid_production_target

    selection = {"count": 1, "selected_slot": 1199}
    unit = {"slot": 1199, "owner": 0, "type": 58}
    assert _valid_production_target(selection, unit, expected_slot=1199)
    assert _valid_production_target(selection, {**unit, "type": 58}, expected_slot=1199)
    assert not _valid_production_target({"count": 0, "selected_slot": None}, None,
                                        expected_slot=1199)
    assert not _valid_production_target(selection, {**unit, "owner": 1}, expected_slot=1199)
    assert not _valid_production_target(selection, {**unit, "type": 0}, expected_slot=1199)


def test_live_minimap_target_uses_widget_bounds_and_non_ff_lut() -> None:
    from tools.g1_saved_scene_probe import _minimap_target_from_lut

    raw = bytearray(b"\xff" * (180 * 90 * 2))
    # One baked pixel at widget-relative (89, 1); the geometric center is empty.
    offset = (89) * 2
    raw[offset:offset + 2] = bytes((4, 7))
    target = _minimap_target_from_lut(0, 509, bytes(raw))
    assert target["screen_xy"] == [89, 510]
    assert target["lut_bytes"] == [4, 7]
    assert target["source"] == "nearest_baked_pixel"
    assert _minimap_target_from_lut(0, 509, b"\xff" * len(raw)) is None


def test_live_minimap_target_rejects_out_of_widget_or_sentinel_points() -> None:
    from tools.g1_saved_scene_probe import _minimap_target_from_lut

    raw = bytearray(b"\xff" * (180 * 90 * 2))
    # Center is baked; no out-of-bounds fallback point is accepted.
    offset = ((44 * 180) + 90) * 2
    raw[offset:offset + 2] = bytes((3, 5))
    target = _minimap_target_from_lut(0, 509, bytes(raw))
    assert target is not None
    assert 0 <= target["screen_xy"][0] <= 180
    assert 509 < target["screen_xy"][1] < 599


def test_live_minimap_target_matches_hq_world_position_through_baked_lut() -> None:
    from tools.g1_saved_scene_probe import _minimap_target_from_lut

    raw = bytearray(b"\xff" * (180 * 90 * 2))
    raw[(10 * 180 + 20) * 2:(10 * 180 + 20) * 2 + 2] = bytes((89, 89))
    raw[(20 * 180 + 30) * 2:(20 * 180 + 30) * 2 + 2] = bytes((164, 85))
    target = _minimap_target_from_lut(0, 509, bytes(raw), target_world=(164, 85))
    assert target is not None
    assert target["screen_xy"] == [30, 530]
    assert target["lut_bytes"] == [164, 85]
    assert target["target_world"] == [164, 85]
    assert target["source"] == "nearest_target_world"


def test_minimap_diagnostic_parity_accepts_equal_original_unknown() -> None:
    def lane() -> dict[str, object]:
        return {"actions": [{
            "tag": "minimap", "result": "UNKNOWN",
            "camera_before": [158, 101], "camera_after": [158, 101],
            "unit_before": {"status": "UNKNOWN", "slot": None},
            "unit_after": {"status": "UNKNOWN", "slot": None},
            "gate": {"before_hex": "00000000", "restored_hex": "00000000"},
        }]}

    result = _compare_minimap_diagnostic_parity(lane(), lane())
    assert result == {
        "status": "PASS", "effect": "ORIGINAL_PARITY_UNKNOWN",
        "checks": {
            "same_result": True, "same_camera_before_after": True,
            "same_unit_before_after": True, "exact_gate_restore": True,
        },
    }


def _scroll_orchestration_lane(label: str) -> dict[str, object]:
    from tools.g1_saved_scene_probe import SCROLL_PHASE_TICK_PLAN
    from tools.runtime_env import ORIGINAL_SHA256

    ticks = [SCROLL_PHASE_TICK_PLAN[name] for name in (
        "down_input_tick", "down_observation_tick", "right_input_tick",
        "right_observation_tick", "final_observation_tick")]
    state = {
        "players": [{"owner": 0, "rice": 100, "wood": 20}],
        "units": [{"slot": 1, "type": 3, "owner": 0, "x": 10, "y": 20}],
    }
    inputs = []
    for key, tick in (("DOWN", ticks[0]), ("RIGHT", ticks[2])):
        inputs.append({
            "key": key, "valid": True, "target_input_tick": tick,
            "input_tick_before": tick, "input_tick_after": tick,
            "receiver_keydown": {"message": f"{key}-down"},
            "receiver_keyup": {"message": f"{key}-up"},
        })
    checkpoints = []
    pid = 4321 + (1 if label == "baselineB" else 0)
    ptid = [pid, 7, 0]
    call_ids = [f"{label}-call-{index}" for index, _ in enumerate(ticks)]
    for index, tick in enumerate(ticks):
        nonce = f"{label}-pause-{index}"
        run_nonce = f"{label}-run"
        checkpoints.append({
            "tick": tick,
            "pause": {
                "status": "PAUSED_AT_PHASE_RETURN", "tick": tick,
                "nonce": nonce, "run_nonce": run_nonce, "inferior_pid": pid,
                "thread_global_num": 7, "thread_ptid": ptid,
                "call_id": call_ids[index],
                "all_stop_mode": True, "phase_context_quiescent": True,
                "unresolved_phase_calls": [], "thread_census_complete": True,
                "threads": [{"global_num": 7, "ptid": ptid,
                             "inferior_pid": pid, "is_running": False}],
            },
            "snapshot": {
                "status": "PASS", "sim_tick_before": tick,
                "sim_tick_after": tick, "state": state,
            },
            "release": {"status": "RELEASE", "tick": tick, "nonce": nonce,
                        "run_nonce": run_nonce},
            "ack": {
                "status": "CONSUMED", "tick": tick, "tick_after": tick,
                "nonce": nonce, "run_nonce": run_nonce, "census_stable": True,
                "all_threads_stopped": True, "phase_context_quiescent": True,
                "threads_after": [{"global_num": 7, "ptid": ptid,
                                   "inferior_pid": pid, "is_running": False}],
            },
        })
    return {
        "status": "DIAGNOSTIC_ONLY", "variant": "baseline", "lane_label": label,
        "source_exe_sha256": ORIGINAL_SHA256,
        "private_exe_sha256": ORIGINAL_SHA256,
        "source_unchanged": True,
        "fixture": {"name": "save006.dat", "sha256": SAVE_SHA256, "synthetic": False},
        "cleanup": {"ok": True, "game_removed": True, "prefix_processes_after": []},
        "scroll_phase_diagnostic": {
            "status": "PASS", "variant": "baseline", "phase_observation": {
                "status": "PASS", "checkpoint_ticks": ticks,
                "completed_phases": [{"tick": tick, "thread_global_num": 7,
                                      "thread_ptid": ptid, "inferior_pid": pid,
                                      "call_id": call_ids[index],
                                      "entry_seq": index * 2 + 1,
                                      "return_seq": index * 2 + 2,
                                      "entry_before_return": True}
                                     for index, tick in enumerate(ticks)],
                "invalid_reasons": [], "all_writer_quiescence_proven": True,
            },
            "target_memory_writes": 0, "close_helper_sha256": "b" * 64,
            "bridge_sha256": "c" * 64, "inputs": inputs, "checkpoints": checkpoints,
        },
    }


def test_scroll_orchestration_persists_control_acceptance_before_candidate(
    tmp_path: Path,
) -> None:
    from tools.g1_saved_scene_probe import _run_scroll_phase_orchestration

    calls: list[str] = []
    artifacts = tmp_path / "artifacts"
    bridge = tmp_path / "bridge.dll"
    close_helper = tmp_path / "helper.exe"
    bridge.write_bytes(b"bridge-fixture")
    close_helper.write_bytes(b"helper-fixture")

    def run_lane(**kwargs: object) -> dict[str, object]:
        label = str(kwargs["lane_label"])
        calls.append(label)
        if label == "candidate":
            acceptance = json.loads(
                (artifacts / "baseline-control-acceptance.json").read_text()
            )
            assert acceptance["status"] == "PASS"
            assert calls == ["baselineA", "baselineB", "candidate"]
        lane = _scroll_orchestration_lane(label)
        lane["variant"] = str(kwargs["variant"])
        lane["scroll_phase_diagnostic"]["variant"] = str(kwargs["variant"])
        lane["scroll_phase_diagnostic"]["bridge_sha256"] = hashlib.sha256(
            Path(kwargs["bridge"]).read_bytes()).hexdigest()
        lane["scroll_phase_diagnostic"]["close_helper_sha256"] = hashlib.sha256(
            Path(kwargs["close_helper"]).read_bytes()).hexdigest()
        return lane

    pair, exit_code = _run_scroll_phase_orchestration(
        run_lane=run_lane, runtime_root=tmp_path / "runtime", artifact_root=artifacts,
        bridge=bridge, close_helper=close_helper,
    )
    assert exit_code == 0
    assert calls == ["baselineA", "baselineB", "candidate"]
    assert pair["status"] == "PASS_BOUNDED_SCROLL_DIAGNOSTIC"
    assert pair["control_acceptance"]["status"] == "PASS"


def test_scroll_orchestration_skips_candidate_if_frozen_file_changes(tmp_path: Path) -> None:
    from tools.g1_saved_scene_probe import _run_scroll_phase_orchestration

    bridge = tmp_path / "bridge.dll"
    helper = tmp_path / "helper.exe"
    bridge.write_bytes(b"bridge-before")
    helper.write_bytes(b"helper")
    calls: list[str] = []

    def run_lane(**kwargs: object) -> dict[str, object]:
        label = str(kwargs["lane_label"])
        calls.append(label)
        lane = _scroll_orchestration_lane(label)
        diagnostic = lane["scroll_phase_diagnostic"]
        diagnostic["variant"] = str(kwargs["variant"])
        diagnostic["bridge_sha256"] = hashlib.sha256(bridge.read_bytes()).hexdigest()
        diagnostic["close_helper_sha256"] = hashlib.sha256(helper.read_bytes()).hexdigest()
        if label == "baselineB":
            bridge.write_bytes(b"bridge-after")
        return lane

    pair, exit_code = _run_scroll_phase_orchestration(
        run_lane=run_lane, runtime_root=tmp_path / "runtime", artifact_root=tmp_path / "artifacts",
        bridge=bridge, close_helper=helper,
    )
    assert exit_code == 2
    assert calls == ["baselineA", "baselineB"]
    assert pair["status"] == "HOLD"
    assert pair["lane_results"]["candidate"]["candidate_calls"] == 0
    assert pair["control_acceptance"]["file_identities_unchanged_before_candidate"] is False


@pytest.mark.parametrize("bad_lane", ["baselineA", "baselineB"])
@pytest.mark.parametrize("defect", [
    "phase", "missing_checkpoint", "wrong_checkpoint", "duplicate_checkpoint",
    "missing_ack", "wrong_ack", "duplicate_ack", "partial_census", "stale_pause",
    "identity_mismatch", "nonquiescent_phase",
    "phase_call_mismatch", "phase_thread_mismatch", "census_pid_mismatch",
    "release_run_nonce_mismatch", "missing_pause_identity", "bridge_hash_mismatch",
    "helper_hash_mismatch", "census_ptid_mismatch", "census_running",
    "ack_census_mismatch", "pause_run_nonce_mismatch",
    "raw_sequence_gap", "raw_no_update_ptid",
    "empty_input", "wrong_input", "invalid_input", "state_mismatch",
    "source_identity", "fixture_identity", "cleanup", "partial_record",
    "lane_exception", "lane_nonobject",
])
def test_scroll_orchestration_holds_and_skips_candidate_on_rejected_control(
    tmp_path: Path, bad_lane: str, defect: str,
) -> None:
    from tools.g1_saved_scene_probe import _run_scroll_phase_orchestration

    calls: list[str] = []
    artifacts = tmp_path / "artifacts"
    bridge = tmp_path / "bridge.dll"
    close_helper = tmp_path / "helper.exe"
    bridge.write_bytes(b"bridge-fixture")
    close_helper.write_bytes(b"helper-fixture")

    def run_lane(**kwargs: object) -> dict[str, object]:
        label = str(kwargs["lane_label"])
        calls.append(label)
        if label != bad_lane:
            lane = _scroll_orchestration_lane(label)
            lane["variant"] = str(kwargs["variant"])
            lane["scroll_phase_diagnostic"]["variant"] = str(kwargs["variant"])
            lane["scroll_phase_diagnostic"]["bridge_sha256"] = hashlib.sha256(
                Path(kwargs["bridge"]).read_bytes()).hexdigest()
            lane["scroll_phase_diagnostic"]["close_helper_sha256"] = hashlib.sha256(
                Path(kwargs["close_helper"]).read_bytes()).hexdigest()
            return lane
        if defect == "lane_exception":
            raise RuntimeError("fixture lane failure")
        if defect == "lane_nonobject":
            return None  # type: ignore[return-value]
        lane = _scroll_orchestration_lane(label)
        diagnostic = lane["scroll_phase_diagnostic"]
        if defect == "phase":
            diagnostic["phase_observation"]["status"] = "INVALID"
        elif defect in {"raw_sequence_gap", "raw_no_update_ptid"}:
            diagnostic["phase_observation"]["status"] = "INVALID"
            diagnostic["phase_observation"]["invalid_reasons"] = [defect]
        elif defect == "missing_checkpoint":
            diagnostic["checkpoints"].pop()
        elif defect == "partial_record":
            diagnostic["checkpoints"][2] = None
        elif defect == "wrong_checkpoint":
            diagnostic["checkpoints"][1]["tick"] += 1
        elif defect == "duplicate_checkpoint":
            diagnostic["checkpoints"][1] = dict(diagnostic["checkpoints"][0])
        elif defect == "missing_ack":
            diagnostic["checkpoints"][2]["ack"] = None
        elif defect == "wrong_ack":
            diagnostic["checkpoints"][2]["ack"]["nonce"] = "stale"
        elif defect == "duplicate_ack":
            diagnostic["checkpoints"][2]["ack"] = dict(diagnostic["checkpoints"][1]["ack"])
        elif defect == "partial_census":
            diagnostic["checkpoints"][2]["pause"]["thread_census_complete"] = False
        elif defect == "stale_pause":
            diagnostic["checkpoints"][2]["pause"]["tick"] += 1
        elif defect == "identity_mismatch":
            diagnostic["checkpoints"][2]["pause"]["inferior_pid"] += 1
        elif defect == "phase_call_mismatch":
            diagnostic["checkpoints"][2]["pause"]["call_id"] = "other-call"
        elif defect == "phase_thread_mismatch":
            diagnostic["checkpoints"][2]["pause"]["thread_ptid"] = [4321, 99, 0]
        elif defect == "census_pid_mismatch":
            diagnostic["checkpoints"][2]["pause"]["threads"][0]["inferior_pid"] = 9999
        elif defect == "census_ptid_mismatch":
            diagnostic["checkpoints"][2]["pause"]["threads"][0]["ptid"] = [4321, 99, 0]
        elif defect == "census_running":
            diagnostic["checkpoints"][2]["pause"]["threads"][0]["is_running"] = True
        elif defect == "ack_census_mismatch":
            diagnostic["checkpoints"][2]["ack"]["threads_after"] = []
        elif defect == "pause_run_nonce_mismatch":
            diagnostic["checkpoints"][2]["pause"]["run_nonce"] = "other-run"
        elif defect == "release_run_nonce_mismatch":
            diagnostic["checkpoints"][2]["release"]["run_nonce"] = "other-run"
        elif defect == "missing_pause_identity":
            del diagnostic["checkpoints"][2]["pause"]["call_id"]
        elif defect == "bridge_hash_mismatch":
            diagnostic["bridge_sha256"] = "d" * 64
        elif defect == "helper_hash_mismatch":
            diagnostic["close_helper_sha256"] = "e" * 64
        elif defect == "nonquiescent_phase":
            diagnostic["phase_observation"]["all_writer_quiescence_proven"] = False
        elif defect == "empty_input":
            diagnostic["inputs"] = []
        elif defect == "wrong_input":
            diagnostic["inputs"][0]["key"] = "UP"
        elif defect == "invalid_input":
            diagnostic["inputs"][1]["valid"] = False
        elif defect == "state_mismatch":
            diagnostic["checkpoints"][2]["snapshot"]["state"]["players"][0]["rice"] += 1
        elif defect == "source_identity":
            lane["source_unchanged"] = False
        elif defect == "fixture_identity":
            lane["fixture"]["synthetic"] = True
        elif defect == "cleanup":
            lane["cleanup"]["ok"] = False
        lane["variant"] = str(kwargs["variant"])
        diagnostic["variant"] = str(kwargs["variant"])
        if defect != "bridge_hash_mismatch":
            diagnostic["bridge_sha256"] = hashlib.sha256(
                Path(kwargs["bridge"]).read_bytes()).hexdigest()
        if defect != "helper_hash_mismatch":
            diagnostic["close_helper_sha256"] = hashlib.sha256(
                Path(kwargs["close_helper"]).read_bytes()).hexdigest()
        return lane

    pair, exit_code = _run_scroll_phase_orchestration(
        run_lane=run_lane, runtime_root=tmp_path / "runtime", artifact_root=artifacts,
        bridge=bridge, close_helper=close_helper,
    )
    assert exit_code == 2
    assert calls == ["baselineA", "baselineB"]
    assert pair["status"] == "HOLD"
    assert pair["lane_results"]["candidate"]["status"] == "SKIP"
    assert pair["lane_results"]["candidate"]["candidate_calls"] == 0
    stored = json.loads((artifacts / "baseline-control-acceptance.json").read_text())
    assert stored["status"] == "HOLD"


def _write_capture_pair(tmp_path: Path, tag: str) -> tuple[dict, dict]:
    baseline_path = tmp_path / f"baseline-{tag}.png"
    candidate_path = tmp_path / f"candidate-{tag}.png"
    Image.new("RGB", (800, 600), (255, 255, 255)).save(baseline_path)
    Image.new("RGB", (1600, 1200), (255, 255, 255)).save(candidate_path)
    return (
        {"captures": {tag: {"path": str(baseline_path)}}},
        {"captures": {tag: {"path": str(candidate_path)}}},
    )


def test_scroll_after_diagnostic_comparison_is_scroll_only_and_not_a_gate_tag(
    tmp_path: Path,
) -> None:
    from tools.g1_saved_scene_probe import (
        G1_CAPTURE_TAGS,
        _diagnostic_capture_comparisons,
        _v2_capture_gate,
        _v2q_capture_gate,
        _v2s_capture_gate,
    )

    baseline, candidate = _write_capture_pair(tmp_path, "scroll_after")

    assert _diagnostic_capture_comparisons(baseline, candidate, terrain_scroll=False) == {}
    result = _diagnostic_capture_comparisons(baseline, candidate, terrain_scroll=True)
    assert set(result) == {"scroll_after"}
    assert result["scroll_after"]["status"] == "PASS"
    assert result["scroll_after"]["v2q_status"] == "PASS"
    assert "scroll_after" not in G1_CAPTURE_TAGS
    # A diagnostic FAIL must not leak into the required-tag gates.
    comparisons = {tag: {"v2_status": "PASS", "v2s_status": "PASS", "v2q_status": "PASS"}
                   for tag in G1_CAPTURE_TAGS}
    comparisons["scroll_after"] = {"v2_status": "FAIL", "v2s_status": "FAIL", "v2q_status": "FAIL"}
    for gate in (_v2_capture_gate, _v2s_capture_gate, _v2q_capture_gate):
        gated = gate(comparisons)
        assert gated["status"] == "PASS"
        assert gated["required_tags"] == list(G1_CAPTURE_TAGS)


def test_scroll_after_diagnostic_comparison_blocks_when_capture_missing(tmp_path: Path) -> None:
    from tools.g1_saved_scene_probe import _diagnostic_capture_comparisons

    result = _diagnostic_capture_comparisons({"captures": {}}, {"captures": {}}, terrain_scroll=True)

    assert result["scroll_after"]["status"] == "BLOCKED"


def test_scroll_after_capture_is_taken_after_final_scroll_observation() -> None:
    source = Path("tools/g1_saved_scene_probe.py").read_text(encoding="utf-8")
    lane = source[source.index("def _run_lane"):]
    final_diff = lane.index('result["terrain_scroll"]["final_scene_diff"]')
    capture = lane.index('"scroll_after"')
    assert final_diff < capture < lane.index("def selection()")
    block = lane[final_diff:lane.index("def selection()")]
    assert 'result["captures"]["scroll_after"] = _capture(' in block
    assert '_wait_for_mirror_present(' in block  # candidate waits for a settled present
    assert "_diagnostic_capture_comparisons(" in source
    assert 'pair["scroll_after_comparison"]' in source


def test_fixture_pins_default_to_save006_and_save000_matches_s1_evidence() -> None:
    from tools.g1_saved_scene_probe import SAVE_FIXTURES, SAVE_INDEX, _fixture_pin
    from tools.s1_load_evidence import FIXTURES as S1_FIXTURES

    assert SAVE_FIXTURES["save006"] == (SAVE_NAME, SAVE_SHA256, SAVE_INDEX)
    name, sha256, index = _fixture_pin("save000")
    spec = S1_FIXTURES["save000.dat"]
    assert (name, sha256, index) == ("save000.dat", spec.expected_sha256, spec.selected_index)
    assert index == 1
    with pytest.raises(Exception, match="unsupported fixture"):
        _fixture_pin("save001")


def test_fixture_and_scene_actions_options_reject_save006_only_modes() -> None:
    from tools.g1_saved_scene_probe import _scene_option_error

    base = dict(fixture="save006", scene_actions="all", terrain_scroll=False,
                terrain_trace=False, census_only=False, rice_phase=False,
                scroll_phase=False)
    assert _scene_option_error(**base) is None
    assert _scene_option_error(**{**base, "scene_actions": "none"}) is None
    assert _scene_option_error(**{**base, "fixture": "save000", "scene_actions": "none"}) is None
    assert "--fixture save000 requires --scene-actions none" in _scene_option_error(
        **{**base, "fixture": "save000"})
    for flag in ("terrain_trace", "rice_phase", "scroll_phase"):
        assert "--scene-actions none cannot be combined" in _scene_option_error(
            **{**base, "scene_actions": "none", flag: True})
    # H-S3: a key/edge scroll is scene independent, so none + terrain_scroll is allowed.
    assert _scene_option_error(**{**base, "scene_actions": "none", "terrain_scroll": True}) is None
    assert _scene_option_error(**{**base, "fixture": "save000", "scene_actions": "none",
                                  "terrain_scroll": True}) is None
    assert "--fixture save000 requires --scene-actions none" in _scene_option_error(
        **{**base, "fixture": "save000", "terrain_scroll": True})


def test_census_only_combines_with_scene_actions_none_for_save000() -> None:
    from tools.g1_saved_scene_probe import _scene_option_error

    base = dict(fixture="save000", scene_actions="none", terrain_scroll=False,
                terrain_trace=False, census_only=True, rice_phase=False,
                scroll_phase=False)
    assert _scene_option_error(**base) is None
    assert _scene_option_error(**{**base, "fixture": "save006"}) is None
    # save000 census still needs the loaded-only scene; the other modes stay rejected.
    assert "--fixture save000 requires --scene-actions none" in _scene_option_error(
        **{**base, "scene_actions": "all"})
    assert "--scene-actions none cannot be combined" in _scene_option_error(
        **{**base, "terrain_trace": True})


def test_census_branch_threads_fixture_and_loaded_only_waits_for_census_window() -> None:
    from tools.g1_saved_scene_probe import CENSUS_PRESENT_LIMIT, _census_loaded_wait_timeout

    source = (Path(__file__).parents[1] / "tools/g1_saved_scene_probe.py").read_text(
        encoding="utf-8"
    )
    census_branch = source[source.index("    if args.census_only:\n        census = _run_lane("):]
    census_branch = census_branch[:census_branch.index("census_gate = _validate_census_lane")]
    assert "fixture=args.fixture" in census_branch and "scene_actions=args.scene_actions" in census_branch
    # Window wait sits between the performance window and the loaded-only stop.
    perf = source.index('result["performance_window"] = _measure_performance_window(')
    wait = source.index("_census_loaded_wait_timeout(census_skip_presents)")
    stop = source.index("raise _LoadedOnlyComplete()")
    assert perf < wait < stop
    # skip + 64 presents at >=10/s plus 60 s of load/capture slack.
    assert _census_loaded_wait_timeout(0) == 60.0 + CENSUS_PRESENT_LIMIT / 10.0
    assert _census_loaded_wait_timeout(250) == 60.0 + (250 + CENSUS_PRESENT_LIMIT) / 10.0


def test_scene_actions_none_stops_after_loaded_capture_and_threads_fixture() -> None:
    source = (Path(__file__).parents[1] / "tools/g1_saved_scene_probe.py").read_text(
        encoding="utf-8"
    )
    assert 'parser.add_argument("--fixture"' in source
    assert 'parser.add_argument("--scene-actions"' in source
    assert 'default="save006"' in source and 'default="all"' in source
    # option check + census lane + new-game-path lanes + result-screen lanes + baseline lane + candidate lane
    assert source.count("fixture=args.fixture, scene_actions=args.scene_actions") == 6
    loaded = source.index('result["captures"]["loaded"] = _capture(')
    stop = source.index("raise _LoadedOnlyComplete()")
    selection = source.index("def selection() -> dict[str, Any]:")
    assert loaded < stop < selection
    assert "_LoadedOnlyComplete):" in source


def test_probe_exposes_layer_drift_option_for_the_candidate_lane_only() -> None:
    source = (Path(__file__).parents[1] / "tools/g1_saved_scene_probe.py").read_text(encoding="utf-8")
    assert '"--layer-drift"' in source
    assert "--layer-drift requires --hd-source scale2x" in source
    assert "layer_drift=args.layer_drift" in source
    candidate_env = source[source.index("if candidate:"):source.index("xvfb, display = runtime_env._xvfb")]
    assert 'env["SYW2_G1_LAYER_DRIFT"] = "1"' in candidate_env
    baseline_env = source[source.index("def _run_lane("):source.index("if candidate:")]
    assert "SYW2_G1_LAYER_DRIFT" not in baseline_env
    assert 'prefix / "drive_c" / "inmm_g1_layer_drift.jsonl"' in source
    assert '"layer_drift.jsonl"' in source


def test_scroll_edge_point_maps_up_down_edges_and_center_for_both_lane_scales() -> None:
    from tools.g1_saved_scene_probe import _scroll_edge_point

    assert (500, 100) == _scroll_edge_point((100, 100), 1, "UP", down=True)
    assert (500, 699) == _scroll_edge_point((100, 100), 1, "DOWN", down=True)
    assert (500, 400) == _scroll_edge_point((100, 100), 1, "UP", down=False)
    assert (900, 100) == _scroll_edge_point((100, 100), 2, "UP", down=True)
    assert (900, 1299) == _scroll_edge_point((100, 100), 2, "DOWN", down=True)
    assert (900, 700) == _scroll_edge_point((100, 100), 2, "DOWN", down=False)
    assert (100, 400) == _scroll_edge_point((100, 100), 1, "LEFT", down=True)
    assert (899, 400) == _scroll_edge_point((100, 100), 1, "RIGHT", down=True)
    assert (500, 400) == _scroll_edge_point((100, 100), 1, "LEFT", down=False)
    assert (100, 700) == _scroll_edge_point((100, 100), 2, "LEFT", down=True)
    assert (1699, 700) == _scroll_edge_point((100, 100), 2, "RIGHT", down=True)
    assert (900, 700) == _scroll_edge_point((100, 100), 2, "RIGHT", down=False)
    with pytest.raises(ValueError, match="UP, DOWN, LEFT or RIGHT"):
        _scroll_edge_point((100, 100), 1, "FOO", down=True)


def test_scroll_until_camera_change_uses_injected_edge_sender_instead_of_key_edge(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    import tools.g1_saved_scene_probe as probe

    key_events: list[tuple[str, bool]] = []
    edge_events: list[tuple[str, bool]] = []
    monkeypatch.setattr(probe, "_send_key_edge",
                        lambda display, env, key, *, down: (key_events.append((key, down)) or 10))
    monkeypatch.setattr(probe, "_latest_scroll_keydown", lambda *args, **kwargs: None)
    camera_values = iter(([158, 101], [157, 100], [156, 99]))
    tick_values = iter((100, 100, 101, 105))
    result = probe._send_scroll_until_camera_change(
        ":91", {}, "UP", [158, 101], tmp_path / "input.jsonl",
        after_seq=0, read_camera=lambda: next(camera_values), timeout=5.0,
        read_sim_tick=lambda: next(tick_values), release_at_tick=105,
        send_edge=lambda display, env, key, *, down: (edge_events.append((key, down)) or 7),
    )
    assert key_events == []
    assert edge_events == [("UP", True), ("UP", False)]
    assert result["down_emitted_ns"] == 7 and result["up_emitted_ns"] == 7
    assert result["release_reason"] == "release_tick"


def test_scroll_edge_option_error_is_exclusive_with_hold_and_keys_and_needs_terrain_scroll() -> None:
    from tools.g1_saved_scene_probe import _scroll_edge_option_error

    assert _scroll_edge_option_error(edge=False, hold=True, keys_spec="DOWN,RIGHT",
                                     terrain_scroll=True) is None
    assert _scroll_edge_option_error(edge=True, hold=False, keys_spec="DOWN,RIGHT",
                                     terrain_scroll=True) is None
    assert "requires --terrain-scroll" in _scroll_edge_option_error(
        edge=True, hold=False, keys_spec="DOWN,RIGHT", terrain_scroll=False)
    assert "--terrain-scroll-hold" in _scroll_edge_option_error(
        edge=True, hold=True, keys_spec="DOWN,RIGHT", terrain_scroll=True)
    assert "--terrain-scroll-keys" in _scroll_edge_option_error(
        edge=True, hold=False, keys_spec="UP,DOWN", terrain_scroll=True)
    for spec in ("LEFT,RIGHT", "RIGHT,LEFT"):
        assert _scroll_edge_option_error(edge=True, hold=False, keys_spec=spec,
                                         terrain_scroll=True) is None
    assert "--terrain-scroll-keys" in _scroll_edge_option_error(
        edge=True, hold=False, keys_spec="LEFT,DOWN", terrain_scroll=True)


def test_scroll_edge_point_maps_diagonal_corners_and_center_for_both_lane_scales() -> None:
    from tools.g1_saved_scene_probe import _scroll_edge_point

    assert (100, 100) == _scroll_edge_point((100, 100), 1, "UPLEFT", down=True)
    assert (899, 100) == _scroll_edge_point((100, 100), 1, "UPRIGHT", down=True)
    assert (100, 699) == _scroll_edge_point((100, 100), 1, "DOWNLEFT", down=True)
    assert (899, 699) == _scroll_edge_point((100, 100), 1, "DOWNRIGHT", down=True)
    assert (1699, 1299) == _scroll_edge_point((100, 100), 2, "DOWNRIGHT", down=True)
    assert (100, 100) == _scroll_edge_point((100, 100), 2, "UPLEFT", down=True)
    assert (500, 400) == _scroll_edge_point((100, 100), 1, "UPLEFT", down=False)
    assert (900, 700) == _scroll_edge_point((100, 100), 2, "DOWNRIGHT", down=False)


def test_scroll_edge_diagonal_keys_are_edge_only_and_validated() -> None:
    import pytest as _pytest
    from tools.g1_saved_scene_probe import (
        _parse_scroll_keys, _scroll_edge_keys, _scroll_edge_option_error,
    )

    assert ("UPLEFT", "DOWNRIGHT") == _scroll_edge_keys("UPLEFT,DOWNRIGHT")
    assert ("DOWNLEFT", "UPRIGHT") == _scroll_edge_keys("downleft, upright")
    for spec in ("UPLEFT,DOWNRIGHT", "DOWNRIGHT,UPLEFT", "UPRIGHT,DOWNLEFT", "DOWNLEFT,UPRIGHT"):
        assert _scroll_edge_option_error(edge=True, hold=False, keys_spec=spec,
                                         terrain_scroll=True) is None
    for bad in ("UPLEFT,UPRIGHT", "UPLEFT,UP", "UPLEFT,UPLEFT"):
        assert "--terrain-scroll-keys" in _scroll_edge_option_error(
            edge=True, hold=False, keys_spec=bad, terrain_scroll=True)
        with _pytest.raises(ValueError):
            _scroll_edge_keys(bad)
    # Diagonals are mouse-corner scrolls only: no X11 key exists for the key-hold path.
    with _pytest.raises(ValueError):
        _parse_scroll_keys("UPLEFT,DOWNRIGHT")


def test_scroll_camera_steps_diagonal_corner_hypothesis_sums_both_edge_signs() -> None:
    from tools.g1_saved_scene_probe import _scroll_camera_steps

    # Hypothesis (lap1082 5): UPLEFT = UP(-1,-1)+LEFT(-1,+1) = (-2,0) per step.
    assert 3 == _scroll_camera_steps([158, 101], [152, 101], "UPLEFT")
    assert 3 == _scroll_camera_steps([158, 101], [164, 101], "DOWNRIGHT")
    assert 2 == _scroll_camera_steps([158, 101], [158, 97], "UPRIGHT")
    assert 2 == _scroll_camera_steps([158, 101], [158, 105], "DOWNLEFT")
    assert 0 == _scroll_camera_steps([158, 101], [158, 101], "UPLEFT")
    assert _scroll_camera_steps([158, 101], [164, 101], "UPLEFT") is None
    assert _scroll_camera_steps([158, 101], [158, 105], "UPRIGHT") is None


def test_scroll_corner_clamp_free_needs_hypothesized_axis_motion_without_off_axis_drift() -> None:
    from tools.g1_saved_scene_probe import _scroll_corner_clamp_free

    assert _scroll_corner_clamp_free([158, 101], [134, 101], "UPLEFT") is True
    assert _scroll_corner_clamp_free([158, 101], [158, 125], "DOWNLEFT") is True
    assert _scroll_corner_clamp_free([158, 101], [158, 101], "UPLEFT") is False
    assert _scroll_corner_clamp_free([158, 101], [134, 103], "UPLEFT") is False
    assert _scroll_corner_clamp_free([158, 101], [182, 101], "UPLEFT") is False
    assert _scroll_corner_clamp_free([158, 101], [134, 77], "UP") is False


def test_scroll_edge_keys_default_up_down_and_horizontal_only_on_request() -> None:
    from tools.g1_saved_scene_probe import _scroll_edge_keys

    assert _scroll_edge_keys("DOWN,RIGHT") == ("UP", "DOWN")
    assert _scroll_edge_keys("LEFT,RIGHT") == ("LEFT", "RIGHT")
    assert _scroll_edge_keys("right, left") == ("RIGHT", "LEFT")


def test_terrain_scroll_edge_flag_wiring_waives_key_receiver_and_forces_up_down() -> None:
    source = (Path(__file__).parents[1] / "tools/g1_saved_scene_probe.py").read_text(
        encoding="utf-8"
    )
    assert 'parser.add_argument("--terrain-scroll-edge"' in source
    assert source.count("terrain_scroll_edge=args.terrain_scroll_edge") == 2
    assert "_scroll_edge_keys(args.terrain_scroll_keys)" in source
    scroll_loop = source[source.index("for slot_name, key in zip(", source.index('def _run_lane')):
                         source.index("        def selection()", source.index('def _run_lane'))]
    assert "\"send_edge\": functools.partial(" in scroll_loop
    assert "terrain_scroll_edge or" in scroll_loop
    assert '"scroll_edge": terrain_scroll_edge' in scroll_loop


def test_scene_actions_none_with_terrain_scroll_stops_after_scroll_block() -> None:
    source = (Path(__file__).parents[1] / "tools/g1_saved_scene_probe.py").read_text(
        encoding="utf-8"
    )
    # The loaded-only stop must not fire before the scroll block when scrolling is requested.
    assert 'if scene_actions == "none" and not terrain_scroll:' in source
    scroll = source.index('result["captures"]["scroll_after"] = _capture(')
    selection = source.index("        def selection() -> dict[str, Any]:")
    stop = source.index('if scene_actions == "none":', scroll)
    assert scroll < stop < selection
    assert "--p4b-s-snapshot requires --fixture save006" in source


def test_parse_candidate_throttle_accepts_stop_run_ms_and_rejects_bad_specs() -> None:
    from tools.g1_saved_scene_probe import _parse_candidate_throttle

    assert _parse_candidate_throttle("20:30") == (20, 30)
    assert _parse_candidate_throttle(" 40 : 30 ") == (40, 30)
    for bad in ("", "20", "20:", ":30", "0:30", "20:0", "a:b", "20:30:1", "-1:5", "1.5:3",
                "1001:30", "20:5001"):
        with pytest.raises(ValueError):
            _parse_candidate_throttle(bad)


def test_candidate_throttle_option_error_needs_terrain_scroll_and_valid_spec() -> None:
    from tools.g1_saved_scene_probe import _candidate_throttle_option_error

    assert _candidate_throttle_option_error(None, terrain_scroll=False) is None
    assert _candidate_throttle_option_error("20:30", terrain_scroll=True) is None
    assert "requires --terrain-scroll" in _candidate_throttle_option_error(
        "20:30", terrain_scroll=False)
    assert "STOP_MS:RUN_MS" in _candidate_throttle_option_error("20", terrain_scroll=True)


def _proc_reader(*, cwd: str, maps: str, comm: str = "wine-preloader",
                 cmdline: str = "Z:\\game\\Syw2plus.exe"):
    from tools.g1_saved_scene_probe import _ProcInfo

    return _ProcInfo(cwd=cwd, maps=maps, comm=comm, cmdline=cmdline, state="S")


def test_throttle_target_error_accepts_only_the_candidate_private_copy_process() -> None:
    from tools.g1_saved_scene_probe import _throttle_target_error

    game = "/runtime/candidate/game"
    exe = "Syw2plus.exe"
    good = _proc_reader(cwd=game, maps=f"7f00 r-xp {game}/{exe}\n")
    assert _throttle_target_error(
        pid=42, expected_pid=42, variant="candidate", game_dir=game, exe_name=exe,
        info=good) is None
    # PID is not the Popen of this lane.
    assert "pid" in _throttle_target_error(
        pid=43, expected_pid=42, variant="candidate", game_dir=game, exe_name=exe, info=good)
    # baseline is never throttled.
    assert "candidate" in _throttle_target_error(
        pid=42, expected_pid=42, variant="baseline", game_dir=game, exe_name=exe, info=good)
    # another game copy (cwd mismatch) and the shared loader without the private image.
    other = _proc_reader(cwd="/runtime/baseline/game", maps=f"7f00 r-xp {game}/{exe}\n")
    assert "cwd" in _throttle_target_error(
        pid=42, expected_pid=42, variant="candidate", game_dir=game, exe_name=exe, info=other)
    no_image = _proc_reader(cwd=game, maps="7f00 r-xp /usr/lib/wine/wine-preloader\n",
                            cmdline="wine")
    assert "image" in _throttle_target_error(
        pid=42, expected_pid=42, variant="candidate", game_dir=game, exe_name=exe, info=no_image)
    # wineserver is never a target.
    server = _proc_reader(cwd=game, maps=f"{game}/{exe}", comm="wineserver")
    assert "wineserver" in _throttle_target_error(
        pid=42, expected_pid=42, variant="candidate", game_dir=game, exe_name=exe, info=server)


class _FakeSignals:
    def __init__(self, *, state_after: str = "S", gone: bool = False) -> None:
        import signal

        self.signal = signal
        self.calls: list[tuple[int, int]] = []
        self.state_after = state_after
        self.gone = gone
        self.stopped = False

    def kill(self, pid: int, sig: int) -> None:
        if self.gone:
            raise ProcessLookupError(pid)
        self.calls.append((pid, sig))
        if sig == self.signal.SIGSTOP:
            self.stopped = True
        elif sig == self.signal.SIGCONT:
            self.stopped = False

    def state(self, pid: int) -> str | None:
        if self.gone:
            return None
        return "T" if self.stopped else self.state_after


def test_candidate_throttle_alternates_stop_cont_and_always_ends_with_cont() -> None:
    import signal
    from tools.g1_saved_scene_probe import _CandidateThrottle

    fake = _FakeSignals()
    throttle = _CandidateThrottle(4242, 5, 5, kill=fake.kill, read_state=fake.state)
    throttle.start()
    deadline = time.monotonic() + 3.0
    while sum(1 for _, sig in fake.calls if sig == signal.SIGSTOP) < 3 and time.monotonic() < deadline:
        time.sleep(0.005)
    summary = throttle.stop()
    assert {pid for pid, _ in fake.calls} == {4242}
    sigs = [sig for _, sig in fake.calls]
    assert set(sigs) == {signal.SIGSTOP, signal.SIGCONT}
    assert sigs[0] == signal.SIGSTOP and sigs[-1] == signal.SIGCONT
    assert summary["status"] == "PASS"
    assert summary["stop_count"] >= 3
    assert summary["stopped_ms"] > 0
    assert summary["final_state_not_stopped"] is True
    assert summary["pid"] == 4242 and summary["stop_ms"] == 5 and summary["run_ms"] == 5
    assert throttle.stop() == summary  # idempotent: no second signal burst
    assert [sig for _, sig in fake.calls][-1] == signal.SIGCONT


def test_candidate_throttle_stop_while_stopped_resumes_and_fails_if_still_stopped() -> None:
    import signal
    from tools.g1_saved_scene_probe import _CandidateThrottle

    fake = _FakeSignals()
    throttle = _CandidateThrottle(7, 60_000 // 60, 5000, kill=fake.kill, read_state=fake.state)
    throttle.start()
    deadline = time.monotonic() + 3.0
    while not fake.calls and time.monotonic() < deadline:
        time.sleep(0.001)
    assert fake.calls[0][1] == signal.SIGSTOP
    summary = throttle.stop()
    assert fake.calls[-1][1] == signal.SIGCONT and not fake.stopped
    assert summary["status"] == "PASS"

    class StuckSignals(_FakeSignals):
        def kill(self, pid: int, sig: int) -> None:
            if sig == self.signal.SIGCONT:
                self.calls.append((pid, sig))
                return  # resume did not take effect
            super().kill(pid, sig)

    stuck = StuckSignals()
    throttle = _CandidateThrottle(7, 20, 5000, kill=stuck.kill, read_state=stuck.state)
    throttle.start()
    deadline = time.monotonic() + 3.0
    while not stuck.calls and time.monotonic() < deadline:
        time.sleep(0.001)
    summary = throttle.stop()
    assert summary["status"] == "FAIL"
    assert summary["final_state_not_stopped"] is False


def test_candidate_throttle_tolerates_exited_process() -> None:
    from tools.g1_saved_scene_probe import _CandidateThrottle

    fake = _FakeSignals(gone=True)
    throttle = _CandidateThrottle(9, 5, 5, kill=fake.kill, read_state=fake.state)
    throttle.start()
    summary = throttle.stop()
    assert summary["status"] == "PASS"
    assert summary["process_gone"] is True


def test_run_lane_rejects_throttle_on_baseline_before_touching_anything(tmp_path: Path) -> None:
    from tools.g1_saved_scene_probe import ProbeError, _run_lane

    artifact = tmp_path / "artifact"
    with pytest.raises(ProbeError, match="candidate"):
        _run_lane(variant="baseline", bridge=tmp_path / "b.dll", runtime_root=tmp_path / "rt",
                  artifact_root=artifact, close_helper=tmp_path / "c.exe",
                  candidate_throttle=(20, 30))
    assert not artifact.exists()


def test_candidate_throttle_flag_wiring_is_candidate_only_and_stopped_in_finally() -> None:
    import inspect
    from tools import g1_saved_scene_probe as probe

    source = (Path(__file__).parents[1] / "tools/g1_saved_scene_probe.py").read_text(
        encoding="utf-8"
    )
    assert inspect.signature(probe._run_lane).parameters["candidate_throttle"].default is None
    assert 'parser.add_argument("--candidate-throttle"' in source
    assert source.count("candidate_throttle=") >= 1
    main_src = source[source.index("def main("):]
    baseline_call = main_src[main_src.index('baseline = _run_lane('):main_src.index('candidate = _run_lane(')]
    candidate_call = main_src[main_src.index('candidate = _run_lane('):main_src.index("execution_source_after")]
    assert "candidate_throttle" not in baseline_call
    assert "candidate_throttle=" in candidate_call
    lane = source[source.index("def _run_lane("):source.index("def _validate_census_lane(")]
    # started after the first input tick barrier, stopped in the cleanup path, reported.
    assert lane.index("input_barrier = _wait_for_exact_tick(pid, input_target)") < lane.index(
        "throttle.start()")
    assert "throttle.stop()" in lane[lane.index("    finally:"):]
    assert 'result["candidate_throttle"]' in lane


def test_esl2613_flag_switches_game_preparation_and_selection_array(monkeypatch, tmp_path: Path) -> None:
    from tools import esl2613_runtime, g1_saved_scene_probe as probe, runtime_env

    calls: list[str] = []
    monkeypatch.setattr(runtime_env, "prepare",
                        lambda source, **kw: calls.append("hq2002") or {"lane": "hq2002"})
    exe = b"2610-exe"
    monkeypatch.setattr(esl2613_runtime, "ESL2613_EXE", tmp_path / "2613.exe")
    (tmp_path / "2613.exe").write_bytes(exe)
    monkeypatch.setattr(esl2613_runtime, "ESL2613_SHA256", hashlib.sha256(exe).hexdigest())
    seen: dict[str, object] = {}

    def fake_prepare(exe_bytes, runtime_root, *, bridge=None, timeout=90):
        seen.update(exe=exe_bytes, root=runtime_root, bridge=bridge)
        calls.append("esl2613")
        return {"lane": "esl2613"}, [{"path": "x"}]

    monkeypatch.setattr(esl2613_runtime, "prepare", fake_prepare)
    assert probe._prepare_lane_game(tmp_path / "rt", None, esl2613=False) == {"lane": "hq2002"}
    manifest = probe._prepare_lane_game(tmp_path / "rt", None, esl2613=True)
    assert manifest["lane"] == "esl2613" and manifest["esl2613_overlays"] == [{"path": "x"}]
    assert seen["exe"] == exe and calls == ["hq2002", "esl2613"]

    reads: list[tuple[int, int]] = []

    def read(address: int, size: int) -> bytes:
        reads.append((address, size))
        return bytes(size)

    probe._selection_slots(read, esl2613=False)
    probe._selection_slots(read, esl2613=True)
    assert reads == [(0x00899028, 20 * 4), (esl2613_runtime.SELECTION_ENTRIES_VA, 100 * 4)]


def test_esl2613_flag_refuses_a_wrong_executable(monkeypatch, tmp_path: Path) -> None:
    from tools import esl2613_runtime, g1_saved_scene_probe as probe

    monkeypatch.setattr(esl2613_runtime, "ESL2613_EXE", tmp_path / "2613.exe")
    (tmp_path / "2613.exe").write_bytes(b"not the official exe")
    with pytest.raises(probe.ProbeError, match="2613"):
        probe._prepare_lane_game(tmp_path / "rt", None, esl2613=True)


def test_esl2613_flag_is_off_by_default_and_also_serves_the_saved_scene_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """--esl2613 needs no new-game-only mode and can run the save006 lanes."""
    from tools import g1_saved_scene_probe as probe

    class _Reached(Exception):
        pass

    def reached(source):
        raise _Reached

    assert probe.ESL2613 is False
    monkeypatch.setattr(probe, "ESL2613", False)
    monkeypatch.setattr(probe.runtime_env, "validate_original_source", reached)
    with pytest.raises(_Reached):
        probe.main(["--runtime-root", str(tmp_path / "r"), "--artifact-root", str(tmp_path / "a"),
                    "--esl2613"])
    assert probe.ESL2613 is True  # parsed, past every option check, no --new-game-path
    assert not (tmp_path / "a").exists()
    with pytest.raises(_Reached):
        probe.main(["--runtime-root", str(tmp_path / "r"), "--artifact-root", str(tmp_path / "a")])
    assert probe.ESL2613 is False


def test_esl2613_selection_memory_redirects_only_the_stock_entries() -> None:
    from tools import esl2613_runtime, g1_saved_scene_probe as probe

    reads: list[tuple[int, int]] = []

    def read(address: int, size: int) -> bytes:
        reads.append((address, size))
        return bytes(size)

    assert probe._selection_memory(read, esl2613=False) is read
    view = probe._selection_memory(read, esl2613=True)
    view(0x00899024, 4)                      # selection count stays
    view(0x00899028, 2)                      # first slot -> first 2610 entry
    view(0x00899028 + 8, 4)                  # entry 2 keeps its offset
    view(0x00899028 + 20 * 4 - 2, 4)         # crosses the stock array end: not redirected
    base = esl2613_runtime.SELECTION_ENTRIES_VA
    assert reads == [(0x00899024, 4), (base, 2), (base + 8, 4), (0x00899028 + 78, 4)]


def test_ret_range_diag_flag_is_candidate_only_opt_in_and_needs_scale2x() -> None:
    """H-E2611G1-1 E1-1: --ret-range-diag sets SYW2_G1_RET_RANGE_DIAG for the candidate lane only."""
    probe = (Path(__file__).parents[1] / "tools/g1_saved_scene_probe.py").read_text(encoding="utf-8")
    assert '"--ret-range-diag"' in probe
    assert "--ret-range-diag requires --hd-source scale2x" in probe
    assert "ret_range_diag=args.ret_range_diag" in probe
    candidate_env = probe[probe.index("if candidate:"):probe.index("xvfb, display = runtime_env._xvfb")]
    assert 'env["SYW2_G1_RET_RANGE_DIAG"] = "1"' in candidate_env
    assert probe.count('"SYW2_G1_RET_RANGE_DIAG"') == 1


def test_new_game_path_summary_names_the_real_private_exe_of_every_lane() -> None:
    """H-E2611G1-1 E1-0: the on-disk runtime manifest keeps the pre-overwrite EXE SHA, so the summary must carry the lane's measured one."""
    probe = (Path(__file__).parents[1] / "tools/g1_saved_scene_probe.py").read_text(encoding="utf-8")
    start = probe.index('"schema": "syw2plus.g1-new-game-path.v1"')
    keys = probe[start:probe.index('"victory_poke", "screen_watch")', start)]
    assert '"private_exe_sha256"' in keys and '"source_exe_sha256"' in keys


def test_new_game_play_dwell_captures_split_the_dwell_into_equal_timed_captures(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """H-E2611G1-1 E1-2: --new-game-play-dwell-captures N captures N times inside one unchanged dwell window; 0 = old behaviour."""
    import tools.g1_saved_scene_probe as probe

    slept: list[float] = []
    captured: list[str] = []
    monkeypatch.setattr(probe, "_send_key_edge", lambda display, env, key, *, down: 1)
    monkeypatch.setattr(probe.time, "sleep", lambda seconds: slept.append(seconds))
    monkeypatch.setattr(probe, "_trace_line_count", lambda path: 7)
    camera = iter(([1, 1], [2, 1]))

    def run(dwell_captures: int) -> dict:
        slept.clear()
        captured.clear()
        return probe._new_game_play_window(
            display=":91", env={}, read_camera=lambda: next(camera, [2, 1]), trace_path=tmp_path / "t.jsonl",
            keys=("RIGHT",), hold=0.0, gap=0.0, dwell=60.0,
            capture=captured.append, dwell_captures=dwell_captures)

    result = run(0)
    assert captured == [] and slept == [0.0, 0.0, 60.0]
    camera = iter(([1, 1], [2, 1]))
    result = run(1)  # N=1 boundary: one capture after the full dwell, not the old uncaptured sleep
    assert captured == ["ps3_dwell_1"] and slept == [0.0, 0.0, 60.0]
    assert result["dwell_captures"] == ["ps3_dwell_1"]
    camera = iter(([1, 1], [2, 1]))
    result = run(0)
    assert [w["name"] for w in result["windows"]] == ["scroll_RIGHT", "dwell"]
    camera = iter(([1, 1], [2, 1]))
    result = run(3)
    assert captured == ["ps3_dwell_1", "ps3_dwell_2", "ps3_dwell_3"]
    assert slept == [0.0, 0.0, 20.0, 20.0, 20.0]
    assert [w["name"] for w in result["windows"]] == ["scroll_RIGHT", "dwell"]
    assert result["dwell_captures"] == ["ps3_dwell_1", "ps3_dwell_2", "ps3_dwell_3"]
    source = (Path(__file__).parents[1] / "tools/g1_saved_scene_probe.py").read_text(encoding="utf-8")
    assert '"--new-game-play-dwell-captures"' in source
    assert "--new-game-play-dwell-captures requires --new-game-play" in source


def test_new_game_play_keys_none_skips_scrolling_and_keeps_the_start_camera(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """H-E2611G1-1 E1-2: the random start can sit at a map edge, so --new-game-play-keys none dwells at the start camera."""
    import tools.g1_saved_scene_probe as probe

    edges: list[tuple[str, bool]] = []
    monkeypatch.setattr(probe, "_send_key_edge", lambda display, env, key, *, down: edges.append((key, down)) or 1)
    monkeypatch.setattr(probe.time, "sleep", lambda seconds: None)
    monkeypatch.setattr(probe, "_trace_line_count", lambda path: 3)
    monkeypatch.setitem(probe.NEW_GAME_PLAY_OVERRIDE, "keys", ())
    result = probe._new_game_play_window(
        display=":91", env={}, read_camera=lambda: [91, 54], trace_path=tmp_path / "t.jsonl",
        hold=0.0, gap=0.0, dwell=1.0)
    assert edges == [] and result["segments"] == []
    assert result["status"] == "PASS" and [w["name"] for w in result["windows"]] == ["dwell"]
    source = (Path(__file__).parents[1] / "tools/g1_saved_scene_probe.py").read_text(encoding="utf-8")
    assert 'args.new_game_play_keys.strip().lower() == "none"' in source
    assert 'NEW_GAME_PLAY_OVERRIDE["keys"] = ()' in source  # none -> no keys, not the default sequence
