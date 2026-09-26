"""Offline guards for the opt-in G2 relocation fail-stop diagnostic."""

import json
import struct
from pathlib import Path
from typing import Any
import pytest

from tools import runtime_env


def _raw(*, magic: int = runtime_env.G2_RELOCATION_DIAG_MAGIC,
         version: int = runtime_env.G2_RELOCATION_DIAG_VERSION,
         armed: int = 1, applied: int = 47, copied: int = 6,
         fixups: int = 47, request_id: int = 223456) -> bytes:
    fields = [0] * 49
    fields[:8] = [magic, version, 512, 1201, 47, copied, request_id, 0x0042334C]
    fields[20:24] = [47, applied, 100, 101]
    fields[27:35] = [request_id, 6, 0, 0, 0, 0, 0, 0]
    fields[26] = 0x47424631
    fields[35:39] = [3, 1, 321, 321]
    fields[39:46] = [0x0066C000, 0x00892000, 1, 1, 5, 640, fixups]
    fields[46:49] = [3, 0, 0]
    if not armed:
        fields[43] = 4
    raw = bytearray(runtime_env.G2_RELOCATION_DIAG_RAW_SIZE)
    raw[:runtime_env.G2_RELOCATION_DIAG_MANIFEST.size] = runtime_env.G2_RELOCATION_DIAG_MANIFEST.pack(*fields)
    patch = []
    for index in range(fixups):
        patch.extend([0x004AF5E0 + index * 4, 0x11110000 + index, 0x22220000 + index, 5, 1])
    raw[640:640 + len(patch) * 4] = struct.pack(f"<{len(patch)}I", *patch)
    fault = [runtime_env.G2_RELOCATION_DIAG_MAGIC, runtime_env.G2_RELOCATION_DIAG_VERSION,
             0xC0000005, 0, 2, 0, 0, 0x401000, 321, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0x401000, 0]
    raw[512:512 + runtime_env.G2_RELOCATION_DIAG_FAULT.size] = runtime_env.G2_RELOCATION_DIAG_FAULT.pack(*fault)
    return bytes(raw)


def _family_raw(*, status: int = runtime_env.G2_FAMILY_PROGRESS_COMPLETE,
                family_patch_count: int = 73, bad_identity: bool = False,
                request_id: int = 334455, with_fault: bool = False,
                end_tick: int = 1256, bad_hp: int | None = None) -> bytes:
    fields = [0] * 49
    fields[:8] = [runtime_env.G2_RELOCATION_DIAG_MAGIC, 1, 512, 1201, 120, 6,
                  request_id, 0x0042334C]
    fields[20:24] = [120, 120, 100, 101]
    fields[24] = 0
    fields[26] = 0x47424631
    fields[27:35] = [request_id, 6, 0, 0, 0, 0, 0, 0]
    fields[35:46] = [3, 1, 321, 321, 0x0066C000, 0x00892000, 1, 1, 5, 640, 120]
    fields[46:49] = [3, 0, 0]
    raw = bytearray(runtime_env.G2_RELOCATION_DIAG_RAW_SIZE)
    raw[:runtime_env.G2_RELOCATION_DIAG_MANIFEST.size] = runtime_env.G2_RELOCATION_DIAG_MANIFEST.pack(*fields)
    records: list[int] = []
    for index in range(120):
        records.extend([0x004AF5E0 + index * 4, index + 1, 0x30000000 + index, 5, 1])
    raw[640:640 + len(records) * 4] = struct.pack(f"<{len(records)}I", *records)
    progress = [runtime_env.G2_FAMILY_PROGRESS_MAGIC, 1, status, 0, 1000, end_tick, end_tick,
                256, 256, 256, 20000, 321, 321, 1201, 6, 47, family_patch_count,
                120, 16, 16, 16, 16, 0, 0]
    identities: list[int] = []
    slot = 1
    for owner in range(8):
        for unit_type in (49, 7):
            identities.extend([slot, (owner + 1) * 0x10000 + slot, owner, unit_type,
                               100, 1, 0, 1])
            slot += 1
    if bad_identity:
        identities[3] = 5
    if bad_hp is not None:
        identities[4] = bad_hp
    raw[runtime_env.G2_FAMILY_PROGRESS_OFFSET:
        runtime_env.G2_FAMILY_PROGRESS_OFFSET + runtime_env.G2_FAMILY_PROGRESS.size] = struct.pack(
        "<152I", *(progress + identities)
    )
    if with_fault:
        fault = [runtime_env.G2_RELOCATION_DIAG_MAGIC, 1, 0xC0000005, 0, 2, 0,
                 0, 0x401000, 777, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x401000, 0]
        raw[512:512 + runtime_env.G2_RELOCATION_DIAG_FAULT.size] = struct.pack(
            "<20I", *fault
        )
    return bytes(raw)


def test_relocation_bridge_hash_is_fail_closed_until_separate_review(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(runtime_env, "G2_RELOCATION_DIAG_BRIDGE_SHA256", None)
    monkeypatch.setattr(runtime_env, "G2_FAMILY_ACCESSOR_BRIDGE_SHA256", None)
    manifest = tmp_path / "build.json"
    manifest.write_text("{}", encoding="utf-8")
    with pytest.raises(runtime_env.RuntimeSafetyError, match="not separately reviewed"):
        runtime_env._g2_relocation_diag_build_manifest(manifest, game=tmp_path)


def test_relocation_build_manifest_requires_original_mode_capacity_and_actual_dll(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(runtime_env, "G2_ARTIFACT_ROOT", tmp_path)
    digest = "a" * 64
    dll = tmp_path / "private_inmm.dll"
    dll.write_bytes(b"reviewed-private-dll")
    dll_sha = runtime_env._sha256(dll)
    monkeypatch.setattr(runtime_env, "G2_RELOCATION_DIAG_BRIDGE_SHA256", dll_sha)
    manifest = tmp_path / "build.json"
    manifest.write_text(json.dumps({
        "diagnostic_mode": "g2_six_arena_failstop_v1", "diagnostic_only": True,
        "original_stub_inputs": {"relocation_diag.c": digest},
        "capacity": 1201,
        "patch_count": 47,
        "dll": str(dll), "dll_sha256": dll_sha,
    }), encoding="utf-8")
    evidence = runtime_env._g2_relocation_diag_build_manifest(manifest, game=tmp_path)
    assert evidence["mode"] == runtime_env.G2_RELOCATION_DIAG_MODE
    assert evidence["patch_count"] == 47
    assert evidence["capacity"] == 1201


def test_relocation_native_op_uses_exact_one_eight_dword_request_and_valid_raw(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    prefix = tmp_path / "prefix"
    drive_c = prefix / "drive_c"
    drive_c.mkdir(parents=True)
    monkeypatch.setattr(runtime_env.time, "monotonic_ns", lambda: 123456)
    request_id = 223456
    (drive_c / "supply_probe_result.json").write_text(
        json.dumps({"id": request_id, "op": 6, "ps": 3, "ok": True}),
        encoding="utf-8",
    )
    (drive_c / "g2_relocation_fault.bin").write_bytes(_raw())
    evidence = runtime_env._g2_relocation_diag_native_op(prefix, timeout=1)
    assert evidence["request"]["fields"] == [request_id, 6, 0, 0, 0, 0, 0, 0]
    assert evidence["status"] == "OBSERVED_RELOCATION_DIAGNOSTIC_FAULT"
    assert evidence["raw"]["status"] == "PASS"
    assert evidence["raw"]["classification"] == "OBSERVED_RELOCATION_DIAGNOSTIC_FAULT"
    assert evidence["raw"]["stage"] == 5
    assert evidence["raw"]["request_words"] == [request_id, 6, 0, 0, 0, 0, 0, 0]
    assert len(evidence["raw"]["patch_records"]) == 47
    assert evidence["raw"]["fault_address"] == 0
    assert (drive_c / "supply_probe_request.txt").read_text(encoding="ascii").split() == [
        str(request_id), "6", "0", "0", "0", "0", "0", "0",
    ]


@pytest.mark.parametrize("kwargs", [
    {"magic": 0x44414221}, {"version": 2}, {"applied": 46}, {"copied": 5},
])
def test_relocation_raw_invalid_or_partial_is_blocked(tmp_path: Path, kwargs: dict[str, Any]) -> None:
    path = tmp_path / "g2_relocation_fault.bin"
    path.write_bytes(_raw(**kwargs))
    result = runtime_env._g2_relocation_diag_raw(path)
    assert result["status"] == "BLOCKED"


@pytest.mark.parametrize("manifest_index,bad_value", [
    (36, 0),  # profile_check_ok
    (41, 0),  # copied arena comparison
    (43, 4),  # armed only at stage 5
    (44, 512),  # patch manifest must be at the fixed offset
    (39, 0x0066B000),  # guard must begin at the page-aligned interior
])
def test_relocation_raw_requires_final_native_manifest_contract(
    tmp_path: Path, manifest_index: int, bad_value: int,
) -> None:
    payload = bytearray(_raw())
    struct.pack_into("<I", payload, manifest_index * 4, bad_value)
    path = tmp_path / "g2_relocation_fault.bin"
    path.write_bytes(payload)
    result = runtime_env._g2_relocation_diag_raw(path)
    assert result["status"] == "BLOCKED"


def test_relocation_native_op_does_not_accept_precreated_zero_mapping(tmp_path: Path,
                                                                       monkeypatch: pytest.MonkeyPatch) -> None:
    prefix = tmp_path / "prefix"
    drive_c = prefix / "drive_c"
    drive_c.mkdir(parents=True)
    monkeypatch.setattr(runtime_env.time, "monotonic_ns", lambda: 123456)
    (drive_c / "g2_relocation_fault.bin").write_bytes(bytes(runtime_env.G2_RELOCATION_DIAG_RAW_SIZE))
    result = runtime_env._g2_relocation_diag_native_op(prefix, timeout=0.05)
    assert result["status"] == "BLOCKED_RELOCATION_DIAGNOSTIC_BOUNDARY"
    assert result["raw"]["status"] == "BLOCKED"


def test_relocation_mode_is_exact_g2_and_does_not_mix_stock_or_sampling(tmp_path: Path) -> None:
    build = tmp_path / "build.json"
    with pytest.raises(runtime_env.RuntimeSafetyError, match="exact G2"):
        runtime_env.g1_baseline(tmp_path / "missing.json", timeout=5,
                                g2_relocation_diag_build=build)
    with pytest.raises(runtime_env.RuntimeSafetyError, match="stock stress/lifecycle"):
        runtime_env.g1_baseline(tmp_path / "missing.json", timeout=5,
                                g4_chain_goal=runtime_env.G2_CREATION_GOAL,
                                g4_candidate_exe=runtime_env.G2_CREATION_CANDIDATE,
                                g2_artifact_output=tmp_path / "out",
                                g2_stock_stress=True, g2_relocation_diag_build=build)
    with pytest.raises(runtime_env.RuntimeSafetyError, match="suppresses normal sampling"):
        runtime_env.g1_baseline(tmp_path / "missing.json", timeout=5,
                                g4_chain_goal=runtime_env.G2_CREATION_GOAL,
                                g4_candidate_exe=runtime_env.G2_CREATION_CANDIDATE,
                                g2_artifact_output=tmp_path / "out",
                                g4_sample_seconds=10, g2_relocation_diag_build=build)


def test_relocation_source_keeps_default_off_and_suppresses_old_tail() -> None:
    source = Path(runtime_env.__file__).read_text(encoding="utf-8")
    assert "g2_relocation_diag_build: Path | None = None" in source
    assert 'env["SYW2_G2_RELOCATION_DIAG"] = "1"' in source
    assert '"fields": [request_id, 6, 0, 0, 0, 0, 0, 0]' in source
    assert "normal G1 tail suppressed" in source
    assert "OBSERVED_RELOCATION_DIAGNOSTIC_FAULT" in source


def test_family_accessor_manifest_and_complete_progress_witness(tmp_path: Path,
                                                                monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(runtime_env, "G2_ARTIFACT_ROOT", tmp_path)
    dll = tmp_path / "family.dll"
    dll.write_bytes(b"family-reviewed-dll")
    digest = runtime_env._sha256(dll)
    monkeypatch.setattr(runtime_env, "G2_FAMILY_ACCESSOR_BRIDGE_SHA256", digest)
    manifest = tmp_path / "family.json"
    manifest.write_text(json.dumps({
        "diagnostic_only": True,
        "diagnostic_mode": runtime_env.G2_FAMILY_ACCESSOR_MODE,
        "capacity": 1201, "patch_count": 120,
        "dll": str(dll), "dll_sha256": digest,
        "original_stub_inputs": {"family_accessor.c": "a" * 64},
        "progress_schema": {"offset": 3328, "fixed_size": 608,
                             "expected_ticks": 256, "deadline_ms": 20000,
                             "identity_records": 16, "completion_status": 2},
    }), encoding="utf-8")
    evidence = runtime_env._g2_relocation_diag_build_manifest(manifest, game=tmp_path)
    assert evidence["mode"] == runtime_env.G2_FAMILY_ACCESSOR_MODE
    raw_path = tmp_path / "family.bin"
    raw_path.write_bytes(_family_raw())
    raw = runtime_env._g2_family_accessor_raw(raw_path)
    assert raw["status"] == "PASS"
    assert raw["classification"] == "BOUNDED256TICK_NEW_ARENA_WITNESS"
    assert raw["progress"]["family_patch_count"] == 73
    assert len(raw["progress"]["identities"]) == 16


def test_family_accessor_rejects_identity_or_progress_contract_mismatch(tmp_path: Path) -> None:
    raw_path = tmp_path / "family.bin"
    raw_path.write_bytes(_family_raw(bad_identity=True))
    assert runtime_env._g2_family_accessor_raw(raw_path)["status"] == "BLOCKED"
    raw_path.write_bytes(_family_raw(family_patch_count=84))
    assert runtime_env._g2_family_accessor_raw(raw_path)["status"] == "BLOCKED"
    raw_path.write_bytes(_family_raw(bad_hp=0x80000000))
    assert runtime_env._g2_family_accessor_raw(raw_path)["status"] == "BLOCKED"


def test_family_accessor_preserves_first_av_as_blocked_context(tmp_path: Path) -> None:
    path = tmp_path / "family.bin"
    path.write_bytes(_family_raw(with_fault=True))
    result = runtime_env._g2_family_accessor_raw(path)
    assert result["status"] == "BLOCKED"
    assert result["fault"]["present"] is True
    assert result["request_id"] == 334455


def test_family_initial_identity_snapshot_requires_exact_sixteen_units() -> None:
    units = [{"slot": slot, "internal_id": (owner + 1) * 0x10000 + slot,
              "owner": owner, "type": unit_type}
             for owner in range(8) for slot, unit_type in ((owner + 1, 49), (owner + 17, 7))]
    identities = runtime_env._g2_family_initial_identities({"units": units})
    assert len(identities) == 16
    assert {(item["owner"], item["type"]) for item in identities} >= {
        (owner, unit_type) for owner in range(8) for unit_type in (49, 7)
    }
    with pytest.raises(runtime_env.RuntimeSafetyError, match="exactly 16"):
        runtime_env._g2_family_initial_identities({"units": units[:15]})


def test_family_accessor_native_op_rejects_mismatched_raw_request_id(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    prefix = tmp_path / "prefix"
    drive_c = prefix / "drive_c"
    drive_c.mkdir(parents=True)
    # Generated request is 334456; the fixed raw witness carries 334455.
    monkeypatch.setattr(runtime_env.time, "monotonic_ns", lambda: 234356)
    (drive_c / "g2_relocation_fault.bin").write_bytes(_family_raw())
    result = runtime_env._g2_family_accessor_native_op(prefix, timeout=0.05)
    assert result["status"] == "BLOCKED_RELOCATION_DIAGNOSTIC_BOUNDARY"
    assert result["raw"]["reason"].startswith("family raw request id")
