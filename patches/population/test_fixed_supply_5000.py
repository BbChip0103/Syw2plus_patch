import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location(
    "fixed_supply_5000", Path(__file__).with_name("fixed_supply_5000.py")
)
patch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(patch)
SOURCE = Path(__file__).resolve().parents[2] / "Syw2plus/syw2plus_original.exe"


@pytest.fixture
def original():
    if not SOURCE.exists():
        pytest.skip("Local original game required")
    return SOURCE.read_bytes()


def test_only_documented_instruction_bytes_change(original):
    result = patch.patched_bytes(original)
    allowed = {i for off, before, _ in patch.EDITS for i in range(off, off + len(before))}
    assert len(result) == len(original)
    assert {i for i, (a, b) in enumerate(zip(original, result)) if a != b} <= allowed
    for off, _, after in patch.EDITS:
        assert result[off : off + len(after)] == after


def test_rejects_wrong_version():
    with pytest.raises(ValueError, match="SHA256"):
        patch.patched_bytes(b"not the original")


def test_copy_restore_preserves_input(original, tmp_path):
    source = tmp_path / "input.exe"
    source.write_bytes(original)
    target = tmp_path / "experiment.exe"
    patch.create_copy(source, target)
    assert source.read_bytes() == original
    assert target.read_bytes() == patch.patched_bytes(original)
    assert patch.restore(target) == patch.ORIGINAL_SHA256
    assert target.read_bytes() == original


def test_rejects_input_as_target(original, tmp_path):
    source = tmp_path / "input.exe"
    source.write_bytes(original)
    with pytest.raises(ValueError, match="input"):
        patch.create_copy(source, source)
    assert source.read_bytes() == original


def test_existing_destination_not_overwritten(original, tmp_path):
    source = tmp_path / "input.exe"
    source.write_bytes(original)
    target = tmp_path / "experiment.exe"
    target.write_bytes(b"keep")
    with pytest.raises(FileExistsError):
        patch.create_copy(source, target)
    assert target.read_bytes() == b"keep"
    assert not Path(str(target) + ".original").exists()


def test_restore_refuses_unknown_modification(original, tmp_path):
    source = tmp_path / "input.exe"
    source.write_bytes(original)
    target = tmp_path / "experiment.exe"
    patch.create_copy(source, target)
    target.write_bytes(b"changed externally")
    with pytest.raises(ValueError, match="exact experimental"):
        patch.restore(target)
    assert target.read_bytes() == b"changed externally"


EVIDENCE = Path(__file__).with_name("verification_0910")


def evidence_state(name):
    import json

    return json.loads((EVIDENCE / name).read_text())["state"]


def test_real_army_costs_and_pending_completion():
    import json

    costs = json.loads((EVIDENCE / "type_costs.json").read_text())["costs"]
    for name, count, used, reserved in [
        ("run3_real_army_fixture.json", 144, 4990, 0),
        ("run3_real_army_pending.json", 144, 4990, 10),
        ("run3_real_army_5000.json", 145, 5000, 0),
        ("run4_combined_loaded_army.json", 145, 5000, 0),
        ("run4_combined_pending_load.json", 144, 4990, 10),
        ("run4_combined_production_complete.json", 145, 5000, 0),
    ]:
        s = evidence_state(name)
        units = [u for u in s["units"] if u["owner"] == 0]
        assert s["ps"] == 3
        assert len(units) == len({u["internal_id"] for u in units}) == count
        assert sum(costs[str(u["type"])] for u in units) == used
        assert s["players"][0]["used"] == used
        assert s["players"][0]["reserved"] == reserved
        assert s["players"][0]["cap"] == 5000


def test_combined_runtime_dimensions_and_wide_selection():
    import json
    import struct

    renderer = json.loads((EVIDENCE / "run4_combined_renderer.json").read_text())
    values = struct.unpack("<10I", bytes.fromhex(renderer["hex"]))
    assert values[:6] == (3, 2560, 1440, 8, 2560, 1440)
    selected = json.loads((EVIDENCE / "run4_combined_selected.json").read_text())
    raw = bytes.fromhex(selected["hex"])
    assert struct.unpack_from("<I", raw)[0] == 1
    assert struct.unpack_from("<h", raw, 4)[0] == 1199


def test_current_build_reproduces_tested_combined_binary(original):
    import json
    from patches.resolution.qhd_probe import build

    qhd, _ = build(original)
    result = bytearray(qhd)
    for off, before, after in patch.EDITS:
        assert result[off : off + len(before)] == before
        result[off : off + len(before)] = after
    manifest = json.loads((EVIDENCE / "manifest.json").read_text())
    assert patch.digest(result) == manifest["combined_sha256"]


def test_combined_continuous_24k_after_last_load():
    import hashlib
    import json

    trace = (EVIDENCE / "run4_trace.jsonl").read_bytes()
    summary = json.loads((EVIDENCE / "run4_endurance_summary.json").read_text())
    assert hashlib.sha256(trace).hexdigest() == summary["trace_sha256"]
    rows = [json.loads(line) for line in trace.splitlines()]
    resets = [i for i in range(1, len(rows)) if rows[i]["tick"] < rows[i - 1]["tick"]]
    assert len(resets) == 1
    epoch = rows[resets[-1] :]
    events = [
        json.loads(line) for line in (EVIDENCE / "run4_bridge_log.jsonl").read_text().splitlines()
    ]
    load = [event for event in events if event["op"] == 3][-1]
    assert load["id"] == 21 and load["ok"]
    assert load["tick_after"] == summary["start_tick"] == 937
    assert 937 <= epoch[0]["tick"] <= 977
    assert epoch[-1]["tick"] - load["tick_after"] >= 24000
    assert len(epoch) == summary["samples"]
    assert all(row["ps"] == 3 for row in epoch)
    assert all(p["cap"] == 5000 for row in epoch for p in row["players"])
    assert all(0 <= b["tick"] - a["tick"] <= 40 for a, b in zip(epoch, epoch[1:]))
