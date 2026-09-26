"""lap203 middle independent probe for R5-A + R5-C.

Written fresh for this lap.  It does not import or reuse any body from
tests/test_runtime_env.py, does not run the game, and writes only to a
caller-supplied temporary directory.

Scope: D1 (raw read failures are non-fatal, enumerated only) and
D2 (the real injected reader reaches disk evidence through the shared
input sequence), plus the lap199/lap201 invariants that must not regress.
"""
import ast
import json
import struct
import sys
import tempfile
from pathlib import Path

REPO = Path("/home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus_patch")
sys.path.insert(0, str(REPO))
from tools import runtime_env as R  # noqa: E402

COUNT = 0
def ok(cond, label):
    global COUNT
    COUNT += 1
    if not cond:
        raise AssertionError(f"PROBE FAIL #{COUNT}: {label}")
    print(f"  ok {COUNT:02d}: {label}")


SOURCE = (REPO / "tools" / "runtime_env.py").read_text(encoding="utf-8")
TREE = ast.parse(SOURCE)
FUNCS = {n.name: n for n in ast.walk(TREE) if isinstance(n, ast.FunctionDef)}


# --------------------------------------------------------------------------
print("\n[A] D1 source contract: only the enumerated failure classes are caught")
ev_fn = FUNCS["_read_g1_selection_evidence"]
handlers = [h for h in ast.walk(ev_fn) if isinstance(h, ast.ExceptHandler)]
ok(len(handlers) == 1, f"_read_g1_selection_evidence has exactly one except handler ({len(handlers)})")
caught = handlers[0].type
names = sorted(n.attr if isinstance(n, ast.Attribute) else n.id
               for n in (caught.elts if isinstance(caught, ast.Tuple) else [caught]))
ok(names == ["OSError", "_CommandCellSnapshotError", "error"],
   f"caught classes are exactly _CommandCellSnapshotError/OSError/struct.error ({names})")
ok(all(not (isinstance(n, ast.Name) and n.id in {"Exception", "BaseException"})
       for n in ast.walk(caught)), "handler does not widen to Exception/BaseException")
ok(handlers[0].type is not None, "no bare except")

# the pre-existing exception contracts named in the card must be untouched
for fname in ("_read_selection", "_read_g1_command_selection_identity"):
    fn = FUNCS[fname]
    ok(not [h for h in ast.walk(fn) if isinstance(h, ast.ExceptHandler)],
       f"{fname} still contains no except handler (contract unchanged)")

print("\n[B] no new memory offsets; documented lap57/lap61 values intact")
ok(R.G1_SELECTION_COUNT_ADDRESS == 0x00899024, "selection count address 0x00899024")
ok(R.G1_SELECTION_FIRST_SLOT_ADDRESS == 0x00899028, "first slot address 0x00899028")
ok(R.G1_UNIT_EXISTS_BASE_ADDRESS == 0x008990C8, "unit exists base 0x008990C8")
ok(R.G1_UNIT_BASE_ADDRESS == 0x0066B790 and R.G1_UNIT_STRIDE == 0x758
   and R.G1_UNIT_TYPE_OFFSET == 0x8D, "unit base/stride/type offset unchanged")

print("\n[C] wait predicates and budgets are unchanged")
ok(R.G1_INPUT_STAGE_BUDGETS == {"unit_select": 10.0, "drag_select": 10.0, "minimap": 10.0},
   "stage budgets are 10/10/10")
ok(R.G1_INPUT_STAGE_BUDGET_TOTAL == 30.0, "stage budget total is 30.0")
ok(R.G1_INPUT_PHASE_WALL_CLOCK_BUDGET == 31.5 and R.G1_INPUT_STAGE_BUDGET_TOTAL <= 31.5,
   "phase wall-clock budget is 31.5 and covers the stage total")
seq_src = ast.get_source_segment(SOURCE, FUNCS["_g1_run_input_sequence"])
ok(seq_src.count('int(item.get("count", 0)) >= 1') == 1, "unit_select predicate is count >= 1")
ok(seq_src.count('int(item.get("count", 0)) >= 2') == 1, "drag_select predicate is count >= 2")
ok("selected_type" not in seq_src and "selected_slot" not in seq_src,
   "no absolute slot/type predicate inside the input sequence")

print("\n[D] baseline and candidate inject the same reader")
injections = [ln.strip() for ln in SOURCE.splitlines()
              if "read_selection=" in ln and "def " not in ln]
ok(len(injections) == 2, f"exactly two read_selection injection sites ({len(injections)})")
ok(all(ln == "read_selection=lambda: _read_g1_selection_evidence(read_for_process)," for ln in injections),
   "both sites inject _read_g1_selection_evidence(read_for_process)")

# verdict must not consume the new evidence fields
verdict_src = ast.get_source_segment(SOURCE, FUNCS["_g1_input_verdict"])
ok("selected_type" not in verdict_src and "selected_slot" not in verdict_src,
   "_g1_input_verdict ignores slot/type evidence")


# --------------------------------------------------------------------------
def reader(count, slot=7, unit_type=58, active=1, fail=None):
    """fail = (address, exception) injected at that address."""
    touched = []
    def read(address, size):
        touched.append(address)
        if fail is not None and address == fail[0]:
            raise fail[1]
        if address == R.G1_SELECTION_COUNT_ADDRESS:
            return struct.pack("<i", count())
        if address == R.G1_SELECTION_FIRST_SLOT_ADDRESS:
            return struct.pack("<h", slot)
        if address == R.G1_UNIT_EXISTS_BASE_ADDRESS + slot * 2:
            return struct.pack("<h", active)
        if address == R.G1_UNIT_BASE_ADDRESS + slot * R.G1_UNIT_STRIDE + R.G1_UNIT_TYPE_OFFSET:
            return struct.pack("<B", unit_type)
        raise AssertionError(f"probe: unexpected read at {address:#x}")
    return read, touched


TYPE_ADDR = R.G1_UNIT_BASE_ADDRESS + 7 * R.G1_UNIT_STRIDE + R.G1_UNIT_TYPE_OFFSET
EXISTS_ADDR = R.G1_UNIT_EXISTS_BASE_ADDRESS + 7 * 2

print("\n[E] reader behaviour: success, empty, and every failure class")
read, touched = reader(lambda: 1)
ev = R._read_g1_selection_evidence(read)
ok(ev["count"] == 1 and ev["first_slot"] == 7, "count/first_slot preserved")
ok(ev["selected_slot"] == 7 and ev["selected_type"] == 58, "approved slot/type recorded")
ok(set(touched) == {R.G1_SELECTION_COUNT_ADDRESS, R.G1_SELECTION_FIRST_SLOT_ADDRESS,
                    EXISTS_ADDR, TYPE_ADDR}, "only the four approved addresses were read")

read, touched = reader(lambda: 0)
ev = R._read_g1_selection_evidence(read)
ok(ev["selected_slot"] is None and ev["selected_type"] == "UNKNOWN", "count==0 -> UNKNOWN")
ok(EXISTS_ADDR not in touched and TYPE_ADDR not in touched,
   "count==0 reads no selected-unit detail")

read, _ = reader(lambda: 1, active=0)
ev = R._read_g1_selection_evidence(read)
ok(ev["selected_type"] == "UNKNOWN" and ev["selected_slot"] == 7,
   "inactive slot stays non-fatal (lap201 behaviour preserved)")
ok(ev["selected_type_provenance"].startswith("_CommandCellSnapshotError: "),
   "snapshot provenance wording unchanged")

for label, addr, exc in (
    ("OSError at the exists read", EXISTS_ADDR, OSError(5, "probe io")),
    ("OSError at the type read", TYPE_ADDR, OSError(5, "probe io")),
    ("struct.error at the exists read", EXISTS_ADDR, struct.error("probe unpack")),
    ("struct.error at the type read", TYPE_ADDR, struct.error("probe unpack")),
):
    read, _ = reader(lambda: 1, fail=(addr, exc))
    ev = R._read_g1_selection_evidence(read)
    ok(ev["selected_type"] == "UNKNOWN" and ev["selected_slot"] == 7,
       f"{label} is non-fatal and keeps first_slot")
    ok(ev["selected_type_provenance"].startswith(f"{type(exc).__name__}: "),
       f"{label} records provenance {type(exc).__name__}")

read, _ = reader(lambda: 1, fail=(TYPE_ADDR, TypeError("probe programming error")))
raised = None
try:
    R._read_g1_selection_evidence(read)
except BaseException as exc:  # noqa: BLE001
    raised = exc
ok(isinstance(raised, TypeError), "a genuine programming error still propagates (no blanket catch)")

read, _ = reader(lambda: 1, fail=(R.G1_SELECTION_COUNT_ADDRESS, OSError(5, "probe io")))
raised = None
try:
    R._read_g1_selection_evidence(read)
except BaseException as exc:  # noqa: BLE001
    raised = exc
ok(isinstance(raised, OSError), "pre-R5-A count read keeps its original fatal contract")

read, _ = reader(lambda: 1, active=0)
raised = None
try:
    R._read_g1_command_selection_identity(read, selection_count=1)
except BaseException as exc:  # noqa: BLE001
    raised = exc
ok(isinstance(raised, R._CommandCellSnapshotError),
   "_read_g1_command_selection_identity still raises for an inactive slot")


# --------------------------------------------------------------------------
print("\n[F] end-to-end: real reader injected into the shared input sequence")

def run_sequence(tmpdir, name, *, active=1, fail_at=None, fail_exc=None):
    """Drive the real _g1_run_input_sequence with the real evidence reader."""
    box = {"count": 0, "tick": 0, "camera": [100, 100]}
    inputs: list[dict] = []
    out = Path(tmpdir) / f"{name}.json"

    def read(address, size):
        if address == R.G1_SELECTION_COUNT_ADDRESS:
            return struct.pack("<i", box["count"])
        if address == R.G1_SELECTION_FIRST_SLOT_ADDRESS:
            return struct.pack("<h", 7)
        if fail_at is not None and address == fail_at:
            raise fail_exc
        if address == EXISTS_ADDR:
            return struct.pack("<h", active)
        if address == TYPE_ADDR:
            return struct.pack("<B", 58)
        raise AssertionError(f"probe: unexpected read {address:#x}")

    def flush():
        out.write_text(json.dumps(inputs, default=str), encoding="utf-8")

    def wait(reader_fn, predicate, message, **kwargs):
        for _ in range(50):
            item = reader_fn(False)
            if predicate(item):
                return item
        raise AssertionError(f"probe wait never satisfied: {message}")

    def click(x, y):
        box["tick"] += 1
        if (x, y) == (410, 270):
            box["count"] = 1
        if (x, y) == (150, 520):
            box["camera"] = [220, 260]

    def drag(x0, y0, x1, y1):
        box["tick"] += 1
        box["count"] = 2

    result = R._g1_run_input_sequence(
        inputs=inputs, content_crop=(0, 0, 800, 600), scale=(2.0, 2.0),
        capture=lambda t: {"tag": t, "path": f"probe://{t}.png"},
        runtime_state=lambda: {"ps": 3, "tick": box["tick"]},
        game_state=lambda: {"ps": 3, "tick": box["tick"]},
        read_selection=lambda: R._read_g1_selection_evidence(read),
        read_camera=lambda: list(box["camera"]),
        wait=wait, click=click, drag=drag,
        read_production_cell=lambda: {"status": "UNAVAILABLE"},
        flush=flush, started=R.time.monotonic(), timeout=120.0,
    )
    return inputs, json.loads(out.read_text(encoding="utf-8")), result


def stage(inputs, tag):
    return [item for item in inputs if item.get("tag") == tag][0]


ORDER = ["unit_select", "production", "drag_select", "minimap"]

with tempfile.TemporaryDirectory() as tmpdir:
    inputs, on_disk, result = run_sequence(tmpdir, "success")
    ok([i.get("tag") for i in inputs] == ORDER, "success: all four stages ran in order")
    unit = stage(inputs, "unit_select")
    ok(unit["before"]["selection"]["selected_type"] == "UNKNOWN"
       and unit["before"]["selection"]["selected_slot"] is None,
       "success: unit_select.before is UNKNOWN (empty selection)")
    ok(unit["after"]["selection"]["selected_slot"] == 7
       and unit["after"]["selection"]["selected_type"] == 58,
       "success: unit_select.after carries the approved slot/type")
    drag_entry = stage(inputs, "drag_select")
    ok(drag_entry["after"]["selection"]["selected_slot"] == 7
       and drag_entry["after"]["selection"]["selected_type"] == 58,
       "success: drag_select.after carries the approved slot/type")
    disk_unit = [i for i in on_disk if i.get("tag") == "unit_select"][0]
    ok(disk_unit["after"]["selection"]["selected_type"] == 58,
       "success: slot/type evidence reached the flushed disk file")
    ok(stage(inputs, "production")["result"] == "BLOCKED", "success: production stayed BLOCKED")
    ok(stage(inputs, "minimap")["result"] == "PASS"
       and result["camera_after_minimap"] == [220, 260],
       "success: minimap ran after production and observed the camera change")
    verdict = R._g1_input_verdict(inputs, enabled=True)
    ok(verdict["required_inputs"] is False and verdict["production_blocked"] is True,
       "success: slot/type evidence does not launder required_inputs")

    failures = (
        ("oserror", dict(fail_at=TYPE_ADDR, fail_exc=OSError(5, "probe io")), "OSError: "),
        # struct.error.__name__ is "error"; the card fixed the provenance format
        # as f"{type(exc).__name__}: {exc}", so this is the expected rendering.
        ("structerror", dict(fail_at=EXISTS_ADDR, fail_exc=struct.error("probe unpack")),
         "error: "),
        ("snapshot", dict(active=0), "_CommandCellSnapshotError: "),
    )
    for name, kwargs, expected in failures:
        inputs, on_disk, _ = run_sequence(tmpdir, name, **kwargs)
        tags = [i.get("tag") for i in inputs]
        ok(tags == ORDER, f"{name}: all four stages still ran ({tags})")
        after = stage(inputs, "unit_select")["after"]["selection"]
        ok(after["selected_type"] == "UNKNOWN"
           and after["selected_type_provenance"].startswith(expected),
           f"{name}: unit_select.after is UNKNOWN with {expected.strip(': ')} provenance")
        ok(stage(inputs, "drag_select")["after"]["selection"]["selected_type"] == "UNKNOWN",
           f"{name}: drag_select.after is UNKNOWN, not fatal")
        ok(stage(inputs, "minimap")["result"] == "PASS", f"{name}: minimap still executed")
        ok([i.get("tag") for i in on_disk] == tags, f"{name}: the failure run is preserved on disk")
        ok(R._g1_input_verdict(inputs, enabled=True)["required_inputs"] is False,
           f"{name}: overall stays fail-closed")

print(f"\nPROBE PASS — {COUNT} assertions")
