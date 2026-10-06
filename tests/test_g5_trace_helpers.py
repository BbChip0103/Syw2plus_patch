"""Behavior locks for selected G5 GDB helpers without executing a trace script."""

import ast
import json
import struct
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
TRACE_FILES = {
    "order": "tools/g5_order_record_builder_trace.py",
    "loop": "tools/g5_pending_broadcast_loop_entry_trace.py",
    "stack": "tools/g5_pending_broadcast_stack_builder_trace.py",
    "writer": "tools/g5_pending_broadcast_writer_trace.py",
    "upstream": "tools/g5_selection_upstream_trace.py",
    "watch": "tools/g5_selection_watch_trace.py",
    "v2": "tools/g5_v2_accessor_sanity_trace.py",
    "v3": "tools/g5_v3_chunk_dispatch_trace.py",
    "header": "tools/g5_v3_order_type_header_trace.py",
    "issuer": "tools/g5_order_issuer_entry_trace.py",
    "staging": "tools/g5_v3_staging_snapshot_trace.py",
}


class FakeInferior:
    def __init__(self, memory=None, error=None):
        self.memory = memory or {}
        self.error = error
        self.reads = []

    def read_memory(self, address, size):
        self.reads.append((address, size))
        if self.error is not None:
            raise self.error
        return self.memory[address][:size]


class FakeFrame:
    def __init__(self, registers=None, error_names=(), pc=0x12345678, pc_error=None):
        self.registers = registers or {}
        self.error_names = set(error_names)
        self.pc_value = pc
        self.pc_error = pc_error

    def read_register(self, name):
        if name in self.error_names:
            raise RuntimeError(name)
        return self.registers[name]

    def pc(self):
        if self.pc_error is not None:
            raise self.pc_error
        return self.pc_value


def extract(key, names, *, memory=None, read_error=None, frame=None):
    """Compile only named FunctionDef nodes into a small fake-GDB namespace."""
    source = (ROOT / TRACE_FILES[key]).read_text(encoding="utf-8")
    tree = ast.parse(source, filename=TRACE_FILES[key])
    wanted = set(names)
    funcs = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in wanted]
    assert {node.name for node in funcs} == wanted
    inferior = FakeInferior(memory, read_error)
    active_frame = frame or FakeFrame()

    class FakeGdb:
        @staticmethod
        def selected_inferior():
            return inferior

        @staticmethod
        def selected_frame():
            return active_frame

    namespace = {"gdb": FakeGdb, "struct": struct, "json": json}
    module = ast.Module(body=funcs, type_ignores=[])
    exec(compile(module, TRACE_FILES[key], "exec"), namespace)
    return namespace, inferior


READ_CASES = [
    ("order", "read_u16", "<H", 2),
    ("loop", "read_u32", "<I", 4),
    ("loop", "read_u16", "<H", 2),
    ("loop", "read_u8", None, 1),
    ("stack", "read_u32", "<I", 4),
    ("stack", "read_u16", "<H", 2),
    ("writer", "read_u32", "<I", 4),
    ("upstream", "read_bytes", None, 4),
    ("upstream", "read_u32", "<I", 4),
    ("watch", "read_bytes", None, 4),
    ("watch", "read_u32", "<I", 4),
    ("v2", "read_s16", "<h", 2),
    ("v3", "read_u16", "<H", 2),
    ("v3", "read_s16", "<h", 2),
    ("v3", "read_u32", "<I", 4),
]


@pytest.mark.parametrize("key,name,fmt,width", READ_CASES)
def test_memory_read_helpers_preserve_arguments_values_and_conversion(key, name, fmt, width):
    address = 0x10203040
    raw = bytes.fromhex("ff 80 34 12")
    dependencies = [name]
    if name == "read_u32" and key in {"upstream", "watch"}:
        dependencies.append("read_bytes")
    namespace, inferior = extract(key, dependencies, memory={address: raw})
    result = namespace[name](address) if name != "read_bytes" else namespace[name](address, width)
    assert inferior.reads == [(address, width)]
    expected = raw[:width] if fmt is None and name != "read_u8" else (
        raw[0] if name == "read_u8" else struct.unpack(fmt, raw[:width])[0]
    )
    assert result == expected


@pytest.mark.parametrize("key,name,fmt,width", READ_CASES)
def test_memory_read_helpers_preserve_underflow_and_gdb_errors(key, name, fmt, width):
    address = 0x10000
    dependencies = [name]
    if name == "read_u32" and key in {"upstream", "watch"}:
        dependencies.append("read_bytes")
    namespace, _ = extract(key, dependencies, memory={address: b"\x01"})
    def invoke():
        return namespace[name](address) if name != "read_bytes" else namespace[name](address, width)
    if name == "read_bytes":
        assert invoke() == b"\x01"
    elif name == "read_u8":
        assert invoke() == 1
    else:
        with pytest.raises(struct.error):
            invoke()
    failure = RuntimeError("fake GDB read failure")
    namespace, _ = extract(key, dependencies, read_error=failure)
    with pytest.raises(RuntimeError, match="fake GDB read failure"):
        namespace[name](address) if name != "read_bytes" else namespace[name](address, width)


@pytest.mark.parametrize("key", ["upstream", "watch"])
def test_bytes_helpers_convert_buffers_and_preserve_short_reads(key):
    address = 0x10000
    namespace, _ = extract(key, ["read_bytes"], memory={address: bytearray(b"\x01\x02")})
    result = namespace["read_bytes"](address, 4)
    assert result == b"\x01\x02"
    assert type(result) is bytes


def test_u8_helper_preserves_index_error_on_empty_buffer():
    namespace, _ = extract("loop", ["read_u8"], memory={0x10000: b""})
    with pytest.raises(IndexError):
        namespace["read_u8"](0x10000)


@pytest.mark.parametrize(
    "key,name,kwargs,expected",
    [
        ("order", "frame_registers", {}, {n: "0xffffffff" for n in ("eax", "ebx", "ecx", "edx", "esi", "edi", "esp", "ebp")}),
        ("stack", "frame_registers", {}, {n: "0xffffffff" for n in ("eax", "ebx", "ecx", "edx", "esi", "edi", "esp", "ebp")}),
        ("writer", "frame_registers", {}, {n: "0xffffffff" for n in ("eax", "ebx", "ecx", "edx", "esi", "edi", "esp", "ebp")}),
        ("watch", "frame_registers", {}, {n: "0xffffffff" for n in ("eax", "ebx", "ecx", "edx", "esi", "edi", "esp", "ebp")}),
        ("upstream", "frame_registers", {}, {n: 0xffffffff for n in ("eax", "ebx", "ecx", "edx", "esi", "edi", "esp", "ebp")}),
    ],
)
def test_frame_register_helpers_preserve_mask_format_and_per_register_failure(key, name, kwargs, expected):
    names = tuple(expected)
    frame = FakeFrame({n: -1 for n in names}, error_names={"ecx"})
    namespace, _ = extract(key, [name], frame=frame)
    result = namespace[name](**kwargs)
    expected["ecx"] = None
    assert result == expected


@pytest.mark.parametrize("key,name,expected", [
    ("order", "esp_word", "0x1234abcd"),
    ("stack", "esp_word", "0x1234abcd"),
    ("writer", "caller_return_address", "0x1234abcd"),
    ("v2", "return_address", "0x1234abcd"),
    ("v3", "return_address", "0x1234abcd"),
])
def test_stack_address_helpers_preserve_hex_and_none_fallback(key, name, expected):
    esp = 0x10000
    data = struct.pack("<I", 0x1234ABCD)
    frame = FakeFrame({"esp": esp})
    dependencies = [name]
    if key in {"stack", "writer"} and name in {"esp_word", "caller_return_address"}:
        dependencies.append("read_u32")
    if key == "v2" and name == "return_address":
        dependencies.append("reg")
    namespace, _ = extract(key, dependencies, memory={esp: data}, frame=frame)
    assert namespace[name]() == expected
    failing, _ = extract(key, dependencies, read_error=RuntimeError("unmapped"), frame=frame)
    assert failing[name]() is None


def test_frame_pc_formats_value_and_returns_none_on_failure():
    watch, _ = extract("watch", ["frame_pc"], frame=FakeFrame(pc=0x12345678))
    assert watch["frame_pc"]() == "0x12345678"
    failed_watch, _ = extract("watch", ["frame_pc"], frame=FakeFrame(pc_error=RuntimeError("pc unavailable")))
    assert failed_watch["frame_pc"]() is None


LOG_CASES = ["order", "stack", "v2", "v3"]


@pytest.mark.parametrize("key", LOG_CASES)
def test_stateless_log_preserves_json_record_order_precedence_and_newline(tmp_path, key):
    namespace, _ = extract(key, ["log"])
    namespace["time"] = type("Clock", (), {"time": staticmethod(lambda: 12.5)})
    path = tmp_path / "events.jsonl"
    namespace["events_path"] = str(path)
    namespace["log"]("before", z_field=7, a_field=3, wall_time=99, pid=42)
    expected = {"event": "before", "pid": 42, "wall_time": 99, "z_field": 7, "a_field": 3}
    encoded = json.dumps(expected, sort_keys=True) + "\n"
    assert path.read_text(encoding="utf-8") == encoded
    namespace["log"]("clock")
    clock_record = {"event": "clock", "wall_time": 12.5}
    assert path.read_text(encoding="utf-8").splitlines()[-1] == json.dumps(
        clock_record, sort_keys=True
    )
    with pytest.raises(TypeError, match="multiple values"):
        namespace["log"]("before", event="override")


@pytest.mark.parametrize("key", LOG_CASES)
def test_stateless_log_preserves_serialization_and_file_errors(tmp_path, key):
    namespace, _ = extract(key, ["log"])
    namespace["time"] = type("Clock", (), {"time": staticmethod(lambda: 1.0)})
    namespace["events_path"] = str(tmp_path / "events.jsonl")
    with pytest.raises(TypeError):
        namespace["log"]("x", unsupported=object())

    def fail_open(*args, **kwargs):
        raise OSError("cannot open trace file")

    namespace["open"] = fail_open
    with pytest.raises(OSError, match="cannot open trace file"):
        namespace["log"]("x")


@pytest.mark.parametrize("key", ["v2", "v3", "header"])
def test_reg_helpers_mask_values_and_return_none_for_register_errors(key):
    namespace, _ = extract(key, ["reg"], frame=FakeFrame({"eax": -1}))
    assert namespace["reg"]("eax") == 0xFFFFFFFF
    failed, _ = extract(key, ["reg"], frame=FakeFrame(error_names={"eax"}))
    assert failed["reg"]("eax") is None


def test_issuer_frame_registers_keeps_hex_values_and_per_register_none():
    namespace, _ = extract(
        "issuer", ["frame_registers"],
        frame=FakeFrame({"eax": -1, "ebx": 0x12, "edx": 0, "esi": 0, "edi": 0, "esp": 0, "ebp": 0}, error_names={"ecx"}),
    )
    values = namespace["frame_registers"]()
    assert values == {
        "eax": "0xffffffff", "ebx": "0x12", "ecx": None, "edx": "0x0",
        "esi": "0x0", "edi": "0x0", "esp": "0x0", "ebp": "0x0",
    }


def test_issuer_return_address_reads_exact_entry_word_and_falls_back_to_none():
    esp = 0x10203040
    namespace, inferior = extract(
        "issuer", ["return_address"], memory={esp: struct.pack("<I", 0x1234ABCD)},
        frame=FakeFrame({"esp": esp}),
    )
    assert namespace["return_address"]() == "0x1234abcd"
    assert inferior.reads == [(esp, 4)]

    missing_esp, no_read = extract("issuer", ["return_address"], frame=FakeFrame(error_names={"esp"}))
    assert missing_esp["return_address"]() is None
    assert no_read.reads == []
    read_failure, failed_inferior = extract(
        "issuer", ["return_address"], read_error=RuntimeError("unmapped"),
        frame=FakeFrame({"esp": esp}),
    )
    assert read_failure["return_address"]() is None
    assert failed_inferior.reads == [(esp, 4)]


def test_staging_region_hex_reads_exact_range_and_formats_or_reports_errors():
    address = 0x00893130
    namespace, inferior = extract(
        "staging", ["region_hex"], memory={address: bytes.fromhex("00 0a ff 42")},
    )
    assert namespace["region_hex"](address, 4) == "000aff42"
    assert inferior.reads == [(address, 4)]

    failed, failed_inferior = extract(
        "staging", ["region_hex"], read_error=RuntimeError("unmapped"),
    )
    assert failed["region_hex"](address, 4) == "error: RuntimeError('unmapped')"
    assert failed_inferior.reads == [(address, 4)]


def test_staging_log_sorts_keys_with_newline_and_propagates_errors(tmp_path):
    namespace, _ = extract("staging", ["log"])
    namespace["time"] = type("Clock", (), {"time": staticmethod(lambda: 12.5)})
    path = tmp_path / "staging.jsonl"
    namespace["events_path"] = str(path)
    namespace["log"]("stage", z_field=7, a_field=3, wall_time=99)
    expected = {"event": "stage", "wall_time": 99, "z_field": 7, "a_field": 3}
    assert path.read_text(encoding="utf-8") == json.dumps(expected, sort_keys=True) + "\n"
    with pytest.raises(TypeError):
        namespace["log"]("stage", unsupported=object())

    def fail_open(*args, **kwargs):
        raise OSError("cannot open staging trace")

    namespace["open"] = fail_open
    with pytest.raises(OSError, match="cannot open staging trace"):
        namespace["log"]("stage")
