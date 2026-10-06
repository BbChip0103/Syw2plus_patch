"""Static safety contracts for the bounded G1 live writer trace."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TRACE = (ROOT / "tools/g1_terrain_writer_trace.py").read_text(encoding="utf-8")
PROBE = (ROOT / "tools/g1_saved_scene_probe.py").read_text(encoding="utf-8")


def test_trace_is_read_only_and_bounded():
    assert "protected_read_only" in TRACE
    assert "G1_TERRAIN_WRITER_TRACE_CONTROL" in TRACE
    assert "gdb.BP_WATCHPOINT" in TRACE
    assert "TERRAIN_POINTS = ((64, 64), (416, 256), (768, 448))" in TRACE
    assert "process_vm_writev" not in TRACE
    assert "ptrace" not in TRACE
    assert "VirtualProtect" not in TRACE
    assert "self.enabled = False" in TRACE
    assert "Persist before detach" in TRACE
    assert "TERRAIN_BUFFER = 0x00BA3D30" in TRACE
    assert "TERRAIN_POINTS = ((64, 64), (416, 256), (768, 448))" in TRACE
    assert "terrain_buffer_write" in TRACE
    assert "MAX_ENTRY_SAMPLES = 16" in TRACE
    assert 'self.name != "terrain_draw_0x4324e0"' in TRACE


def test_trace_pins_context_and_all_renderer_targets():
    for address in ("0x00403B20", "0x00403C10", "0x00466D50",
                    "0x004664D0", "0x00465E80", "0x00466280",
                    "0x00465B30", "0x00466540", "0x00466EA0",
                    "0x004658E0"):
        assert address in TRACE
    assert "scene.get(\"program_state\") != 3" in TRACE
    assert "RENDERER + 0x1514" in TRACE
    for address in ("0x004324E0", "0x00433019", "0x004332F0"):
        assert address in TRACE
    assert '"terrain_draw_0x4324e0"' in TRACE
    assert '"terrain_cache_0x433019"' in TRACE
    assert '"terrain_overlay_0x4332f0"' in TRACE


def test_trace_records_runtime_asset_key_and_table_equality():
    for address in ("0x00435400", "0x00435593", "0x004355D7",
                    "0x0043561E", "0x00435662", "0x00435910",
                    "0x00435959"):
        assert address.lower() in TRACE.lower()
    assert "ASSET_BASE_TABLE = 0x00B65E8C" in TRACE
    assert "ASSET_OFFSET_TABLE = 0x00B65758" in TRACE
    assert "ASSET_FILE_STRIDE = 0xBF8" in TRACE
    assert "ASSET_FRAME_STRIDE = 0x2FE" in TRACE
    assert '"asset_key_entry"' in TRACE
    assert '"asset_blitter_call"' in TRACE
    assert "table_equality=equality" in TRACE
    assert "hashlib.sha256" in TRACE
    assert "source_stack_offset" in TRACE


def test_saved_scene_probe_exposes_opt_in_trace_only():
    assert 'parser.add_argument("--terrain-trace", action="store_true")' in PROBE
    assert "terrain_trace=args.terrain_trace" in PROBE
    assert '"LEFT"' in PROBE
    assert '"terrain_redraw"' in PROBE
