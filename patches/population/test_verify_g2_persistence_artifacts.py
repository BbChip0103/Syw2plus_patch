import json
from pathlib import Path
import struct

from patches.population.verify_g2_persistence_artifacts import verify_bundle


def _bundle(tmp_path: Path, *, duplicate: bool = False) -> Path:
    capacity = 4
    existence = (0, 1, 2, 3)
    age = (0, 11, 12, 13)
    category_a = (*([0] * (capacity * 2)), 0)
    category_b = (1, 2, 3, *([0] * (capacity * 2 - 3)), 3)
    active = (1, 2, 3, 0, 3)
    sidecar = struct.pack(
        f"<{capacity * 7 + 3}H",
        *existence,
        *age,
        *category_a,
        *category_b,
        *active,
    )
    (tmp_path / "frozen4000_sidecars.bin").write_bytes(sidecar)
    (tmp_path / "save097.dat").write_bytes(
        b"prefix" + sidecar + (sidecar if duplicate else b"") + b"suffix"
    )
    (tmp_path / "frozen4000_snapshot.json").write_text(
        json.dumps({"state": {"units": [{"slot": slot} for slot in (1, 2, 3)]}})
    )
    return tmp_path


def test_exact_bundle_passes(tmp_path: Path) -> None:
    report = verify_bundle(_bundle(tmp_path), capacity=4)
    assert report["ok"] is True
    assert report["save_offsets"] == [6]
    assert report["live"] == report["active_count"] == 3


def test_duplicate_serialized_sidecar_fails_closed(tmp_path: Path) -> None:
    report = verify_bundle(_bundle(tmp_path, duplicate=True), capacity=4)
    assert report["ok"] is False
    assert report["checks"]["serialized_once"] is False
