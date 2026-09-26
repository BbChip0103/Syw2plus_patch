#!/usr/bin/env python3
"""lap337 middle — lap336 검수 재현과 R-a/R-b 수리 범위 근거.

설계 원칙(lap334 N12 / lap336 §4 교훈 적용):
살아 있는 파일의 SHA256이나 "수리 전에만 참인 결함 상태"를 **단언하지 않는다.**
그런 단언은 정당한 편집 한 번으로 영구 실패가 되고(W3, lap332/lap334 probe), 그것을
통과시키려 재pin하는 것은 금지다. 수리 전후로 모두 참이어야 하는 계약만 단언하고,
전이 상태(현재 결함, 살아 있는 SHA, artifact 건수)는 `findings` 데이터로 **보고만** 한다.

실행: python3 docs/history/laps/probes/20260912_lap337_middle_lap336_repair_scope_probe.py
rc0 = 계약 단언 전부 통과. 게임 실행/입력/메모리 접근/PNG 0.
"""

from __future__ import annotations

import ast
import hashlib
import inspect
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))

from tools import runtime_env  # noqa: E402

ORIGIN_NAMES = ("r1_load_origin.json", ".r1-load-origin.lock", "r1_load_origin.log")
CANDIDATE_NAMES = (
    "r1_load_origin_candidate.json",
    ".r1-load-origin-candidate.lock",
    "r1_load_origin_candidate.log",
)
LAP335_COMPACTION_BODY_SHA = (
    "bba77d09fa70de0c80c67510819b528b19e02caadc6c1e558b85cefbc0fc1954"
)


def sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def function_ast(func: object) -> ast.AST:
    return ast.parse(inspect.cleandoc(inspect.getsource(func)))


def string_literals(tree: ast.AST) -> list[str]:
    return [n.value for n in ast.walk(tree)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)]


def artifact_names(func: object) -> dict[str, str | None]:
    """함수 본문이 실제로 쓰는 artifact/lock/log 이름을 뽑는다."""
    literals = set(string_literals(function_ast(func)))
    found: dict[str, str | None] = {"json": None, "lock": None, "log": None}
    for text in sorted(literals):
        if text.endswith(".json") and "r1_load_origin" in text:
            found["json"] = text
        elif text.endswith(".lock") and "r1-load-origin" in text:
            found["lock"] = text
        elif text.endswith(".log") and "r1_load_origin" in text:
            found["log"] = text
    return found


def ps9_wait_binding(func: object, stage: str) -> dict[str, object]:
    """`_wait_state(stage=...)` 호출의 stage_budget/stage_started 결합을 읽는다."""
    for node in ast.walk(function_ast(func)):
        if not isinstance(node, ast.Call):
            continue
        kw = {k.arg: k.value for k in node.keywords if k.arg}
        stage_kw = kw.get("stage")
        if not (isinstance(stage_kw, ast.Constant) and stage_kw.value == stage):
            continue
        return {
            "stage": stage,
            "stage_budget": ast.unparse(kw["stage_budget"]) if "stage_budget" in kw else None,
            "stage_started": ast.unparse(kw["stage_started"]) if "stage_started" in kw else None,
        }
    return {"stage": stage, "stage_budget": None, "stage_started": None}


def compaction_body_sha(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"```markdown\n(.*)\n```\s*$", text, re.S)
    if match is None:
        return {"found": False, "body_sha256": None, "line_count": None}
    body = match.group(1) + "\n"
    return {
        "found": True,
        "body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
        "line_count": len(body.splitlines()),
    }


def main() -> int:
    failures: list[str] = []
    findings: dict[str, object] = {}

    def check(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    # --- 계약 단언 1: artifact 이름 분리 (봉투 lap334 §10, 수리 전후 불변) ---
    origin = artifact_names(runtime_env.g1_r1_load_origin)
    candidate = artifact_names(runtime_env.g1_r1_candidate_load_origin)
    findings["artifact_names"] = {"origin": origin, "candidate": candidate}
    check(tuple(origin[k] for k in ("json", "lock", "log")) == ORIGIN_NAMES,
          "origin R1 artifact/lock/log names drifted from the lap326 contract")
    check(tuple(candidate[k] for k in ("json", "lock", "log")) == CANDIDATE_NAMES,
          "candidate R1 artifact/lock/log names drifted from envelope lap334 section 10")
    check(not (set(ORIGIN_NAMES) & set(CANDIDATE_NAMES)),
          "origin and candidate artifact names are not disjoint")

    # --- 계약 단언 2: 시간 배분 상한과 좌표/상태 상수 (봉투 §8·§5, 확대 금지) ---
    budgets = {
        "ps9_stage_budget": runtime_env.G1_R1_PS9_STAGE_BUDGET,
        "ps35_stage_budget": runtime_env.G1_R1_PS35_STAGE_BUDGET,
        "click_point": list(runtime_env.G1_R1_CLICK_POINT),
        "wait_ps_states": list(runtime_env.G1_R1_WAIT_PS_STATES),
    }
    findings["constants"] = budgets
    check(budgets["ps9_stage_budget"] == 40.0, "PS9 stage budget is no longer 40s")
    check(budgets["ps35_stage_budget"] == 20.0, "PS35 stage budget is no longer 20s")
    check(budgets["click_point"] == [296, 505], "candidate click point drifted")
    check(budgets["wait_ps_states"] == [9, 35], "wait PS states drifted")

    # --- 계약 단언 3: 불변 이력(압축본)의 본문 SHA는 재현 가능해야 한다 ---
    lap335_compaction = REPO / "docs/history/laps/20260912_status_lap335_compaction.md"
    body = compaction_body_sha(lap335_compaction)
    findings["lap335_compaction"] = body
    check(body["body_sha256"] == LAP335_COMPACTION_BODY_SHA,
          "lap335 compaction body SHA does not reproduce the lap336 record")
    check(body["line_count"] == 130, "lap335 compaction body is not 130 lines")

    # --- 보고만: R-b 근거 (수리되면 값이 바뀐다 → 단언하지 않는다) ---
    findings["ps9_wait_binding"] = {
        "origin": ps9_wait_binding(runtime_env.g1_r1_load_origin, "r1_ps9"),
        "candidate": ps9_wait_binding(
            runtime_env.g1_r1_candidate_load_origin, "candidate_ps9"),
    }

    # --- 보고만: R-a 근거 (수리되면 값이 바뀐다) ---
    test_path = REPO / "tests/test_lap326_r1_load_origin.py"
    test_text = test_path.read_text(encoding="utf-8")
    findings["r_a_name_assertions_present"] = {
        name: (name in test_text) for name in CANDIDATE_NAMES
    }

    # --- 보고만: 살아 있는 SHA와 artifact 건수 (검수 기준선 기록용) ---
    findings["live_sha256"] = {
        rel: sha256_file(REPO / rel)
        for rel in (
            "tools/runtime_env.py",
            "tests/test_lap326_r1_load_origin.py",
            "docs/work/active/G1_CANDIDATE_R1_MIDDLE_ENVELOPE_LAP334.md",
            "docs/work/active/G1_CANDIDATE_R1_MIDDLE_IMPLEMENTATION_REVIEW_LAP336.md",
            "docs/history/laps/probes/"
            "20260912_lap336_middle_lap335_candidate_implementation_probe.py",
        )
    }
    findings["artifact_counts"] = {
        "origin_r1_load_origin_json": len(sorted(REPO.glob(
            "local/runtime/*/output/r1_load_origin.json"))),
        "candidate_r1_load_origin_candidate_json": len(sorted(REPO.glob(
            "local/runtime/*/output/r1_load_origin_candidate.json"))),
    }

    print(json.dumps({"failures": failures, "findings": findings},
                     ensure_ascii=False, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
