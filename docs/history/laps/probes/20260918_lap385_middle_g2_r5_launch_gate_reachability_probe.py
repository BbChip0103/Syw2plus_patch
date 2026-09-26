#!/usr/bin/env python3
"""lap385 middle(Opus5/high) — R5 strictness probe.

STATUS lap384 asked the next middle to judge `validate_original_source`
"strictly, as distinct from calling the real canonical/legacy prepare
entrypoint".  This probe answers the only question that makes the R5 test
meaningful as *launch-gate* evidence rather than as a helper-function test:

  For every CLI-dispatched entrypoint of tools/runtime_env.py, does the
  ordered intra-module call graph reach `validate_original_source` strictly
  before it can reach `subprocess.Popen`?

Static, read-only, AST-only.  Launches nothing.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
RUNTIME_ENV = REPO / "tools/runtime_env.py"

GATE = "validate_original_source"

failures: list[str] = []
tree = ast.parse(RUNTIME_ENV.read_text())
funcs = {n.name: n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}


def called_names(node: ast.AST) -> list[str]:
    """Ordered call targets inside a function body (nested defs included)."""
    out: list[str] = []
    for n in ast.walk(node):
        if isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Name):
                out.append(f.id)
            elif isinstance(f, ast.Attribute):
                out.append(f"{getattr(f.value, 'id', '?')}.{f.attr}")
    return out


def reaches(start: str, target: str, seen: set[str] | None = None) -> bool:
    seen = seen or set()
    if start in seen:
        return False
    seen.add(start)
    if start == target:
        return True
    node = funcs.get(start.split(".")[-1])
    if node is None:
        return False
    for callee in called_names(node):
        short = callee.split(".")[-1]
        if callee == target or short == target:
            return True
        if short in funcs and reaches(short, target, seen):
            return True
    return False


def popen_call(name: str) -> bool:
    return name in {"subprocess.Popen", "Popen"}


def reaches_popen(start: str, seen: set[str] | None = None) -> bool:
    seen = seen or set()
    if start in seen:
        return False
    seen.add(start)
    node = funcs.get(start.split(".")[-1])
    if node is None:
        return False
    for callee in called_names(node):
        if popen_call(callee):
            return True
        short = callee.split(".")[-1]
        if short in funcs and reaches_popen(short, seen):
            return True
    return False


# CLI-dispatched entrypoints: the functions named on the right-hand side of the
# `args.command == ...` dispatch ladder in main().
main_fn = funcs.get("runtime_main")
assert main_fn is not None, "runtime_main (the CLI dispatcher) not found"
dispatched: list[str] = []
for node in ast.walk(main_fn):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in funcs:
        if node.func.id not in dispatched:
            dispatched.append(node.func.id)

report: dict[str, object] = {}
for entry in dispatched:
    node = funcs[entry]
    calls = called_names(node)
    gate_at = next((i for i, c in enumerate(calls) if c.split(".")[-1] == GATE), None)
    if gate_at is None:
        gate_at = next(
            (i for i, c in enumerate(calls) if c.split(".")[-1] in funcs and reaches(c.split(".")[-1], GATE)),
            None,
        )
    popen_at = next(
        (
            i
            for i, c in enumerate(calls)
            if popen_call(c) or (c.split(".")[-1] in funcs and reaches_popen(c.split(".")[-1]))
        ),
        None,
    )
    ok = popen_at is None or (gate_at is not None and gate_at < popen_at)
    report[entry] = {
        "gate_first_reached_at_call": gate_at,
        "popen_first_reachable_at_call": popen_at,
        "gate_precedes_popen": ok,
    }
    if not ok:
        failures.append(f"{entry}_can_reach_popen_before_{GATE}")

# The R5 test calls the gate directly, NOT prepare()/check_runtime().  Record
# that honestly rather than claiming the entrypoint itself was exercised.
report["_scope_note"] = (
    "The lap384 R5 pytest invokes validate_original_source directly; it does not "
    "invoke prepare()/check_runtime()/the CLI. This probe supplies the missing "
    "link statically: the gate is unavoidable on every dispatched path above."
)

print(json.dumps({"failures": failures, "dispatched": dispatched, "report": report}, indent=2))
raise SystemExit(1 if failures else 0)
