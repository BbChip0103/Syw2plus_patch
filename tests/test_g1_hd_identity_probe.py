"""Static and raw-contract tests for G1 P2 identity provenance."""

import json
from pathlib import Path

from tools.g1_hd_identity_probe import validate_trace


ROOT = Path(__file__).resolve().parents[1]


def test_identity_module_is_opt_in_and_bounded() -> None:
    source = (ROOT / "tools/inmm_stub/g1_hd_asset.c").read_text(encoding="utf-8")
    header = (ROOT / "tools/inmm_stub/g1_hd_asset.h").read_text(encoding="utf-8")
    assert '#define G1_HD_SOURCE_ENV "SYW2_G1_HD_SOURCE"' in source
    assert '#define G1_HD_KEY_LIMIT 4096u' in source
    assert '#define G1_HD_DIGEST_BYTES 128u' in source
    assert "VirtualQuery" in source
    assert "g1_hd_asset_mark" in header
    assert "g1_hd_asset_end" in header
    assert "g1_hd_asset_bind_identity_frame" in header
    assert "g1_hd_asset_lookup_identity_block" in header
    assert "g1_hd_asset_probe_negative_key_mismatch" in header


def test_identity_output_is_key_bound_before_composition() -> None:
    asset = (ROOT / "tools/inmm_stub/g1_hd_asset.c").read_text(encoding="utf-8")
    mirror = (ROOT / "tools/inmm_stub/g1_mirror2x.c").read_text(encoding="utf-8")
    assert "identity_frame" in asset
    assert "g_current_key" in asset
    assert "G1_HD_CACHE_BYTE_LIMIT" in asset
    assert "HeapAlloc" in asset and "HeapFree" in asset
    assert "g_identity_cache_inserts" in asset
    assert "g_identity_cache_hits" in asset
    assert "g_identity_cache_misses" in asset
    assert "g_identity_cache_refreshes" in asset
    assert "g_identity_negative_lookup_attempts" in asset
    assert "g_identity_negative_lookup_misses" in asset
    assert "lookup_identity_block_for_key" in asset
    assert "find_key_for_request" in asset
    assert "altered.writer ^= 1u" in asset
    negative = asset.split("BOOL g1_hd_asset_probe_negative_key_mismatch", 1)[1].split(
        "void g1_hd_asset_mark", 1
    )[0]
    assert "find_key_for_request(altered.source" in negative
    assert "altered.identity_frame = NULL" not in negative
    assert "g_current_origin_x" in asset
    assert "g_current_origin_y" in asset
    assert "g1_hd_asset_lookup_identity_block" in mirror
    compose = mirror.split("DWORD g1_mirror2x_compose_sentinel", 1)[1].split(
        "HRESULT g1_mirror2x_copy_present", 1
    )[0]
    assert "g1_hd_asset_lookup_identity_block" in compose
    assert "BYTE pixel = (a != 0x00u) ? a : b" not in compose


def test_validator_accepts_identity_and_preserves_stale_measurement(tmp_path: Path) -> None:
    trace = tmp_path / "trace.jsonl"
    rows = [
        {
            "event": "mirror2x_present",
            "hd_source": "identity",
            "nearest_matches": 480000,
            "nearest_total": 480000,
            "identity_pixels": 12000,
            "identity_keys": 4,
            "identity_invalid_sources": 0,
            "identity_events": 12,
            "identity_lookup_hits": 12000,
            "identity_lookup_misses": 0,
            "identity_cache_inserts": 4,
            "identity_cache_hits": 8,
            "identity_cache_misses": 4,
            "identity_cache_refreshes": 2,
            "identity_negative_lookup_attempts": 1,
            "identity_negative_lookup_misses": 1,
            "identity_key_mismatches": 1,
            "stale_pixels": 3,
        },
        {"event": "summary"},
    ]
    trace.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
    result = validate_trace(trace)
    assert result["status"] == "PASS"
    assert result["identity_pixels_max"] == 12000
    assert result["stale_pixels_total"] == 3


def test_validator_rejects_missing_identity_key(tmp_path: Path) -> None:
    trace = tmp_path / "trace.jsonl"
    rows = [{
        "event": "mirror2x_present", "hd_source": "identity",
        "nearest_matches": 480000, "nearest_total": 480000,
        "identity_pixels": 0, "identity_keys": 0,
        "identity_invalid_sources": 1, "identity_events": 0,
        "identity_lookup_hits": 0, "identity_lookup_misses": 0,
        "identity_cache_inserts": 0, "identity_cache_hits": 0,
        "identity_cache_misses": 0, "identity_key_mismatches": 0,
        "identity_cache_refreshes": 0, "identity_negative_lookup_attempts": 0,
        "identity_negative_lookup_misses": 0,
        "stale_pixels": 0,
    }, {"event": "summary"}]
    trace.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
    assert validate_trace(trace)["status"] == "BLOCKED"
