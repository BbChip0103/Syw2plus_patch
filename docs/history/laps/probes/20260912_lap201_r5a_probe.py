"""lap201 middle independent probe for R5-A (no game, no writes to repo)."""
import struct, sys, time, types
sys.path.insert(0, "/home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus_patch")
from tools import runtime_env as R

A = 0
def ok(cond, label):
    global A
    A += 1
    if not cond:
        raise AssertionError(f"PROBE FAIL: {label}")
    print(f"  ok {A:02d}: {label}")

# ---- reader fixture that logs every address touched -------------------------
def make_reader(count, slot, unit_type, active=1, fail_on=None):
    log = []
    def read(address, size):
        log.append((address, size))
        if fail_on is not None and address == fail_on:
            raise OSError(14, f"read fail at {address:#x}")
        if address == R.G1_SELECTION_COUNT_ADDRESS:
            return struct.pack("<i", count)
        if address == R.G1_SELECTION_FIRST_SLOT_ADDRESS:
            return struct.pack("<h", slot)
        if address == R.G1_UNIT_EXISTS_BASE_ADDRESS + slot * 2:
            return struct.pack("<h", active)
        if address == R.G1_UNIT_BASE_ADDRESS + slot * R.G1_UNIT_STRIDE + R.G1_UNIT_TYPE_OFFSET:
            return struct.pack("<B", unit_type)
        raise AssertionError(f"unexpected read {address:#x}+{size}")
    return read, log

print("\n[1] success fixture: approved slot/type evidence, no new offsets")
r, log = make_reader(1, 7, 58)
ev = R._read_g1_selection_evidence(r)
ok(ev["count"] == 1 and ev["first_slot"] == 7, "count/first_slot preserved from _read_selection")
ok(ev["selected_slot"] == 7, "selected_slot recorded")
ok(ev["selected_type"] == 58, "selected_type recorded")
ok("G1_UNIT_BASE_ADDRESS" in ev["selected_type_provenance"], "provenance names approved offsets")
allowed = {
    R.G1_SELECTION_COUNT_ADDRESS,
    R.G1_SELECTION_FIRST_SLOT_ADDRESS,
    R.G1_UNIT_EXISTS_BASE_ADDRESS + 7 * 2,
    R.G1_UNIT_BASE_ADDRESS + 7 * R.G1_UNIT_STRIDE + R.G1_UNIT_TYPE_OFFSET,
}
ok({a for a, _ in log} <= allowed, f"only pre-existing offsets read: {[hex(a) for a,_ in log]}")
ok(R.G1_UNIT_BASE_ADDRESS == 0x0066B790 and R.G1_UNIT_STRIDE == 0x758
   and R.G1_UNIT_TYPE_OFFSET == 0x8D, "offsets equal lap57/lap61 documented values")

print("\n[2] count==0: no unit read at all, UNKNOWN non-fatal")
r, log = make_reader(0, -1, 0)
ev = R._read_g1_selection_evidence(r)
ok(ev["selected_slot"] is None and ev["selected_type"] == "UNKNOWN", "empty selection -> UNKNOWN")
ok(all(a in (R.G1_SELECTION_COUNT_ADDRESS, R.G1_SELECTION_FIRST_SLOT_ADDRESS) for a, _ in log),
   "no selected-unit detail read when count==0")

print("\n[3] inactive slot (_CommandCellSnapshotError): non-fatal UNKNOWN + provenance")
r, _ = make_reader(1, 7, 58, active=0)
ev = R._read_g1_selection_evidence(r)
ok(ev["selected_type"] == "UNKNOWN", "inactive slot -> UNKNOWN, no raise")
ok(ev["selected_type_provenance"].startswith("_CommandCellSnapshotError:"), "provenance kept")
ok(ev["selected_slot"] == 7, "first_slot still preserved as selected_slot")

print("\n[4] unit_type==0 (normal 'unsupported type' branch): non-fatal")
r, _ = make_reader(1, 7, 0)
ev = R._read_g1_selection_evidence(r)
ok(ev["selected_type"] == "UNKNOWN", "type 0 -> UNKNOWN, no raise")

print("\n[5] HYPOTHESIS: OSError from the *extra* unit reads is FATAL (contract says non-fatal)")
type_addr = R.G1_UNIT_BASE_ADDRESS + 7 * R.G1_UNIT_STRIDE + R.G1_UNIT_TYPE_OFFSET
r, _ = make_reader(1, 7, 58, fail_on=type_addr)
raised = None
try:
    R._read_g1_selection_evidence(r)
except BaseException as exc:  # noqa: BLE001
    raised = exc
ok(isinstance(raised, OSError), f"OSError propagates out of the reader (got {raised!r})")
exists_addr = R.G1_UNIT_EXISTS_BASE_ADDRESS + 7 * 2
r, _ = make_reader(1, 7, 58, fail_on=exists_addr)
raised = None
try:
    R._read_g1_selection_evidence(r)
except BaseException as exc:  # noqa: BLE001
    raised = exc
ok(isinstance(raised, OSError), "OSError on unit-exists read also propagates")
# old reader is immune: it never touches those addresses
r, _ = make_reader(1, 7, 58, fail_on=type_addr)
old = R._read_selection(r)
ok(old["count"] == 1, "pre-R5-A _read_selection is unaffected by the same failure => blast radius grew")

print("\n[6] no absolute type predicate anywhere; budgets/timeouts unchanged")
src = open("/home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus_patch/tools/runtime_env.py").read()
ok(R.G1_INPUT_STAGE_BUDGETS == {"unit_select": 10.0, "drag_select": 10.0, "minimap": 10.0},
   "G1_INPUT_STAGE_BUDGETS unchanged (30.0 total)")
ok(R.G1_INPUT_PHASE_WALL_CLOCK_BUDGET == 31.5, "phase wall-clock budget 31.5 unchanged")
ok(sum(R.G1_INPUT_STAGE_BUDGETS.values()) == 30.0, "budget sum 30.0 <= 31.5")
ok('item.get("count", 0)) >= 1' in src and 'item.get("count", 0)) >= 2' in src,
   "wait predicates still count-only (>=1 / >=2)")
ok("selected_type\"] ==" not in src.replace('selection["selected_type"] == "UNKNOWN"', ""),
   "no verdict/predicate compares selected_type to a literal unit type")

print("\n[7] end-to-end: wired reader keeps drag/minimap running and carries evidence")
selection_state = {"count": 0, "slot": -1}
def live_read(address, size):
    if address == R.G1_SELECTION_COUNT_ADDRESS:
        return struct.pack("<i", selection_state["count"])
    if address == R.G1_SELECTION_FIRST_SLOT_ADDRESS:
        return struct.pack("<h", selection_state["slot"])
    slot = selection_state["slot"]
    if slot >= 0 and address == R.G1_UNIT_EXISTS_BASE_ADDRESS + slot * 2:
        return struct.pack("<h", 1)
    if slot >= 0 and address == R.G1_UNIT_BASE_ADDRESS + slot * R.G1_UNIT_STRIDE + R.G1_UNIT_TYPE_OFFSET:
        return struct.pack("<B", 58)
    raise AssertionError(f"unexpected read {address:#x}")

inputs, flushes, waits = [], [], []
camera = [7, 6]
tick = {"t": 10}
def wait(reader, predicate, message, **kw):
    waits.append(message)
    if "selection" in message and "drag" not in message:
        selection_state.update(count=1, slot=7)
    elif "drag" in message:
        selection_state.update(count=2, slot=7)
    else:
        camera[:] = [81, 0]
    result = reader(True)
    assert predicate(result), message
    return result
def rt_state():
    tick["t"] += 1
    return {"ps": 3, "tick": tick["t"]}
def prod_cell():
    raise R._CommandCellSnapshotError("probe: expected ineligible branch", [])
result = R._g1_run_input_sequence(
    inputs=inputs, content_crop=(37, 41, 1600, 1200), scale=(2.0, 2.0),
    capture=lambda tag: {"sha256": tag, "dimensions": [1600, 1200]},
    runtime_state=rt_state, game_state=lambda: {"ps": 3, "tick": tick["t"], "players": []},
    read_selection=lambda: R._read_g1_selection_evidence(live_read),
    read_camera=lambda: list(camera), wait=wait,
    click=lambda x, y: None, drag=lambda *a: None,
    read_production_cell=prod_cell,
    flush=lambda: flushes.append([str(i["tag"]) for i in inputs]),
    started=time.monotonic() - 1.0, timeout=90.0,
)
tags = [i["tag"] for i in inputs]
ok(tags == ["unit_select", "production", "drag_select", "minimap"],
   f"all four stages ran with the wired reader: {tags}")
ok(inputs[1]["result"] == "BLOCKED", "production still fail-closed BLOCKED")
ok(inputs[0]["after"]["selection"]["selected_type"] == 58, "unit_select after carries selected_type")
ok(inputs[0]["after"]["selection"]["selected_slot"] == 7, "unit_select after carries selected_slot")
ok(inputs[0]["before"]["selection"]["selected_type"] == "UNKNOWN",
   "unit_select before records UNKNOWN for empty selection")
ok(inputs[2]["after"]["selection"]["selected_type"] == 58, "drag_select after carries selected_type")
ok(result["camera_after_minimap"] == [81, 0], "minimap stage completed")

print("\n[8] overall/required_inputs laundering guard still holds")
blocked_inputs = [{"tag": t, "result": "BLOCKED" if t == "production" else "PASS"}
                  for t in R.G1_REQUIRED_INPUT_TAGS]
checks = R._g1_input_verdict(blocked_inputs, enabled=True)
base = R._g1_baseline_verdict(error=None, checks={"required_inputs": checks["required_inputs"]},
                              input_checks=checks, cleanup={"ok": True})
ok(checks["required_inputs"] is False, "required_inputs FAIL while production BLOCKED")
ok(base["overall"] != "PASS", "baseline overall cannot PASS while production BLOCKED")
cand = R._g1_presentation_verdict(error=None, cleanup={"ok": True}, validator={"status": "PASS"},
                                 inputs=blocked_inputs, input_sequence=True)
ok(cand["overall"] != "PASS", "candidate overall cannot PASS while production BLOCKED")

print(f"\nPROBE OK — {A} assertions")
