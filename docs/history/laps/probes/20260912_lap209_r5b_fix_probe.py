"""lap209 middle-tier independent probe of R5-B F1/F4 repair.
Fixtures are built here from scratch (not imported from tests/)."""
import importlib.util, json
from copy import deepcopy
from pathlib import Path

ROOT = Path("/home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus_patch")
spec = importlib.util.spec_from_file_location("cmp", ROOT / "tools/compare_g1_stage_b.py")
cmp = importlib.util.module_from_spec(spec); spec.loader.exec_module(cmp)

def mk_scene(dx=0, dy=0):
    return {"unit_slots": [
        {"slot": 500, "owner": 0, "type": 70, "world": {"x": 100+dx, "y": 100+dy}},
        {"slot": 501, "owner": 0, "type": 21, "world": {"x": 104+dx, "y": 101+dy}},
        {"slot": 700, "owner": 1, "type": 49, "world": {"x": 40+dx, "y": 30+dy}},
    ], "world_bounds": {"width": 256, "height": 256}}

def mk_inputs(cam_b=(10, 20), cam_a=(55, 60)):
    return [
        {"tag": "unit_select", "result": "PASS", "content": [400, 300],
         "before": {"selection": {"count": 0, "selected_slot": 500, "selected_type": 70}},
         "after":  {"selection": {"count": 1, "selected_slot": 500, "selected_type": 70}}},
        {"tag": "drag_select", "result": "PASS", "content": [300, 200],
         "before": {"selection": {"count": 1, "selected_slot": 500, "selected_type": 70},
                    "drag_to": {"content": [520, 360]}},
         "after":  {"selection": {"count": 1, "selected_slot": 500, "selected_type": 70}}},
        {"tag": "minimap", "result": "PASS", "content": [120, 500],
         "before": {"selection": {"count": 1}, "camera": list(cam_b)},
         "after":  {"selection": {"count": 1}, "camera": list(cam_a)}},
    ]

def ev(dx=0, dy=0, **kw):
    return {"scene": mk_scene(dx, dy), "inputs": mk_inputs(**kw)}

def run(name, base, cand, expect_not=("PASS",)):
    r = cmp.compare_evidence(base, cand)
    ok = r["status"] not in expect_not
    print(f"{name:52s} status={r['status']:24s} {'OK' if ok else '*** FAIL-OPEN ***'}")
    return r

print("--- control: identical/translated pair must be able to PASS ---")
r = cmp.compare_evidence(ev(), ev(dx=30, dy=-11))
print("P0 control translated pair                           status=", r["status"],
      "(expect PASS so later probes prove the fix, not a blanket block)")

print("\n--- F1 probes: missing / malformed minimap camera must never PASS ---")
for label, mutate in [
    ("P1a candidate before camera deleted", lambda e: e["inputs"][2]["before"].pop("camera")),
    ("P1b candidate after camera deleted",  lambda e: e["inputs"][2]["after"].pop("camera")),
    ("P1c baseline-side handled too (cand None)", lambda e: e["inputs"][2]["before"].__setitem__("camera", None)),
    ("P1d camera as float pair",            lambda e: e["inputs"][2]["after"].__setitem__("camera", [55.0, 60.0])),
    ("P1e camera as string 'UNKNOWN'",      lambda e: e["inputs"][2]["after"].__setitem__("camera", "UNKNOWN")),
    ("P1f camera as bool pair",             lambda e: e["inputs"][2]["after"].__setitem__("camera", [True, False])),
    ("P1g camera 3-tuple",                  lambda e: e["inputs"][2]["after"].__setitem__("camera", [55, 60, 0])),
    ("P1h camera as dict",                  lambda e: e["inputs"][2]["after"].__setitem__("camera", {"x": 55, "y": 60})),
]:
    c = ev(dx=30, dy=-11); mutate(c)
    rr = run(label, ev(), c)
    if label.startswith("P1a"):
        print("     missing=", rr["stages"]["minimap"].get("missing"))

c = ev(); c2 = ev(dx=30, dy=-11)
del c["inputs"][2]["before"]["camera"]
run("P1i baseline before camera deleted", c, c2)

print("\n--- F1 must not over-block: real camera divergence stays FAIL ---")
r = cmp.compare_evidence(ev(), ev(dx=30, dy=-11, cam_a=(99, 99)))
print("P2a different camera destination                     status=", r["status"],
      "stage=", r["stages"]["minimap"]["status"])
r = cmp.compare_evidence(ev(), ev(dx=30, dy=-11, cam_b=(55, 60), cam_a=(55, 60)))
print("P2b candidate camera did not move                    status=", r["status"],
      "stage=", r["stages"]["minimap"]["status"])

print("\n--- F4 probes: input record errors must never PASS ---")
c = ev(dx=30, dy=-11); c["inputs"].append(deepcopy(c["inputs"][0]))
run("P3a duplicate unit_select tag (candidate)", ev(), c)
b = ev(); b["inputs"].append(deepcopy(b["inputs"][2]))
run("P3b duplicate minimap tag (baseline)", b, ev(dx=30, dy=-11))
c = ev(dx=30, dy=-11); c["inputs"].append("not-an-object")
run("P3c non-object input record", ev(), c)
c = ev(dx=30, dy=-11); c["inputs"] = {"unit_select": c["inputs"][0]}
run("P3d inputs is not a list", ev(), c)

print("\n--- F4 residual probe: input record with non-string / missing tag ---")
c = ev(dx=30, dy=-11); c["inputs"].append({"result": "PASS", "content": [1, 2]})
run("P4a extra input with NO tag key", ev(), c)
c = ev(dx=30, dy=-11); c["inputs"].append({"tag": 7, "result": "PASS"})
run("P4b extra input with non-string tag", ev(), c)
c = ev(dx=30, dy=-11); c["inputs"][0] = dict(c["inputs"][0]); c["inputs"][0].pop("tag")
run("P4c required unit_select record lost its tag", ev(), c)

print("\n--- F2 / F3 are escalated, confirm they are UNCHANGED ---")
c = ev(dx=30, dy=-11)
for s in c["inputs"][:2]:
    s["before"]["selection"]["selected_slot"] = 1100
    s["after"]["selection"]["selected_slot"] = 1100
r = cmp.compare_evidence(ev(), c)
print("P5 F2 slot-id-only difference                        status=", r["status"],
      "(expected FAIL: unchanged escalated defect)")
c = ev(dx=30, dy=-11); c["inputs"][1]["result"] = "FAIL_NO_EFFECT"
r = cmp.compare_evidence(ev(), c)
print("P6 F3 disputed FAIL_NO_EFFECT inherited              status=", r["status"],
      "stage=", r["stages"]["drag_select"]["status"], "(expected FAIL: unchanged escalated defect)")
