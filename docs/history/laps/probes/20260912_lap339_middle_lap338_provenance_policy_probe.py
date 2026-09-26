#!/usr/bin/env python3
"""lap339 middle — lap338 보존 정책 초안 검수와 결합 probe 영향표의 기계 근거.

설계 원칙(lap334 N12 / lap336 §4 / lap337 교훈 유지):
살아 있는 소스의 SHA256이나 "수리 전에만 참인 상태"를 **단언하지 않는다.**
R-a/R-b 수리 전후로 모두 참이어야 하는 계약만 단언하고, 전이 상태(현재 결함,
살아 있는 SHA, stale probe 실패 건수, 스냅샷 디렉터리 유무)는 `findings`로 보고만 한다.
불변 이력(압축본 body, 과거 probe 파일)은 정책상 편집 금지이므로 단언 대상이다.

실행: python3 docs/history/laps/probes/20260912_lap339_middle_lap338_provenance_policy_probe.py
rc0 = 계약 단언 전부 통과. 게임 실행/입력/메모리 접근/PNG/후보 artifact 0.
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

failures: list[str] = []

# 불변 이력: 정책상 편집 금지 대상만 SHA로 고정한다.
LAP337_COMPACTION_BODY_SHA = (
    "512abde1f83e4d8588c9c6aead9a70bebf9eb58444d447749fe401689b8cd5a6"
)
LAP337_COMPACTION_BODY_LINES = 130
STALE_PROBES = (
    "20260912_lap332_middle_lap331_r1_artifact_probe.py",
    "20260912_lap334_middle_candidate_r1_envelope_probe.py",
)
# 두 stale probe가 박아 둔 lap330 기대 SHA. 재pin 금지이므로 리터럴로 남긴다.
LAP330_HARNESS_SHA = "997ff15b13115ccebd9d8832b3b066add589b755d9cc6e8a77d987696cc46eed"
LAP330_TEST_SHA = "81acc11eab97cc04b797724360a81561a227c8454571290782f611aa936cac72"
CANDIDATE_NAMES = (
    "r1_load_origin_candidate.json",
    ".r1-load-origin-candidate.lock",
    "r1_load_origin_candidate.log",
)
SHA_DRIFT_VOCAB = ("SHA", "drift")
STATUS_HEADINGS = (
    "## 지금 상태",
    "## 다음 한 가지",
    "## 지금 막힌 것 (Blockers)",
    "## 검증 상태",
    "## 바퀴 기록",
)


def check(condition: bool, message: str) -> bool:
    if not condition:
        failures.append(message)
    return condition


def sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compaction_body(path: Path) -> tuple[str | None, int]:
    """압축본에서 fence 안 원문만 뽑아 SHA/줄 수를 독립 재계산한다."""
    if not path.is_file():
        return None, 0
    lines = path.read_text(encoding="utf-8").splitlines()
    try:
        start = lines.index("```markdown") + 1
    except ValueError:
        return None, 0
    end = len(lines) - 1
    while end > start and lines[end].strip() != "```":
        end -= 1
    body = lines[start:end]
    text = "\n".join(body) + "\n"
    return hashlib.sha256(text.encode("utf-8")).hexdigest(), len(body)


def declared_header(path: Path) -> dict[str, object]:
    if not path.is_file():
        return {}
    head = path.read_text(encoding="utf-8").splitlines()[:2]
    sha = re.search(r"([0-9a-f]{64})", head[0]) if head else None
    count = re.search(r"(\d+)", head[1]) if len(head) > 1 else None
    return {
        "declared_sha256": sha.group(1) if sha else None,
        "declared_lines": int(count.group(1)) if count else None,
    }


def ps9_stage_binding(func: object, stage: str) -> dict[str, object]:
    """`_wait_state(stage=...)` 호출의 stage_budget/stage_started 결합을 AST로 읽는다."""
    tree = ast.parse(inspect.cleandoc(inspect.getsource(func)))
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        kwargs = {kw.arg: kw.value for kw in node.keywords if kw.arg}
        target = kwargs.get("stage")
        if not (isinstance(target, ast.Constant) and target.value == stage):
            continue
        return {
            "stage": stage,
            "stage_budget": ast.unparse(kwargs["stage_budget"])
            if "stage_budget" in kwargs else None,
            "stage_started": ast.unparse(kwargs["stage_started"])
            if "stage_started" in kwargs else None,
        }
    return {"stage": stage, "stage_budget": None, "stage_started": None}


def gate_sources() -> dict[str, str]:
    return {
        name: (REPO / name).read_text(encoding="utf-8")
        for name in ("Makefile", "pyproject.toml", "checks/safety.sh", "checks/context_limits.py")
        if (REPO / name).is_file()
    }


def main() -> int:
    probes_dir = REPO / "docs/history/laps/probes"
    status = REPO / "docs/STATUS.md"
    status_lines = status.read_text(encoding="utf-8").splitlines()

    # (1) STATUS 계약 — 수리 전후 불변.
    check(len(status_lines) <= 130,
          f"STATUS.md is {len(status_lines)} lines; the PROMPT contract caps it at 130")
    for heading in STATUS_HEADINGS:
        check(status_lines.count(heading) == 1,
              f"STATUS.md must hold exactly one {heading}")

    # (2) 불변 이력 — lap337 압축본 원문 독립 재계산.
    compaction = REPO / "docs/history/laps/20260912_status_lap337_compaction.md"
    body_sha, body_lines = compaction_body(compaction)
    header = declared_header(compaction)
    check(body_sha == LAP337_COMPACTION_BODY_SHA,
          "lap337 compaction body SHA does not match the preserved value")
    check(body_lines == LAP337_COMPACTION_BODY_LINES,
          f"lap337 compaction body is {body_lines} lines, expected {LAP337_COMPACTION_BODY_LINES}")
    check(header.get("declared_sha256") == body_sha,
          "lap337 compaction header SHA disagrees with its own body")
    check(header.get("declared_lines") == body_lines,
          "lap337 compaction header line count disagrees with its own body")
    # STATUS는 "직전 원문을 담은 압축본"을 항상 가리켜야 한다. 특정 파일명을 박으면 다음 바퀴에
    # 영구 실패하므로(= 이 봉투가 금지한 전이 단언) 이름이 아니라 **연결 자체**를 단언한다.
    status_text = "\n".join(status_lines)
    named = sorted(set(re.findall(r"20260912_status_lap\d+_compaction\.md", status_text)))
    pointer_ok = False
    for name in named:
        target = REPO / "docs/history/laps" / name
        target_sha, target_lines = compaction_body(target)
        target_header = declared_header(target)
        if (target_sha is not None
                and target_header.get("declared_sha256") == target_sha
                and target_header.get("declared_lines") == target_lines):
            pointer_ok = True
    check(bool(named), "STATUS.md names no compaction holding its previous text")
    check(pointer_ok,
          "STATUS.md points at no compaction whose declared SHA/line count match its own body")

    # (3) 결합 probe 영향표 — stale probe는 존재하고 편집되지 않았다.
    stale: dict[str, object] = {}
    for name in STALE_PROBES:
        path = probes_dir / name
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        check(path.is_file(), f"stale probe {name} must be preserved, not deleted")
        pinned = [sha for sha in (LAP330_HARNESS_SHA, LAP330_TEST_SHA) if sha in text]
        stale[name] = {"exists": path.is_file(), "file_sha256": sha256_file(path),
                       "lap330_pins_present": pinned}
        check(pinned, f"{name} lost its lap330 pin; re-pinning/removal is forbidden")

    # (4) 현재 필수 게이트가 과거 probe에 의존하지 않는다 — 이것이 "역사적 검수 전용"
    #     분류를 안전하게 만드는 근거다.
    gates = gate_sources()
    for name, text in gates.items():
        check("history/laps/probes" not in text,
              f"{name} references docs/history/laps/probes; stale probes would break a required gate")
    pytest_paths = re.search(r"testpaths\s*=\s*\[([^\]]*)\]", gates.get("pyproject.toml", ""))
    collected = pytest_paths.group(1) if pytest_paths else ""
    check("history" not in collected,
          "pytest testpaths collect docs/history; historical probes would become required tests")

    # (5) 수리 후에도 참이어야 하는 후보/원본 PS9 계약.
    candidate_ps9 = ps9_stage_binding(runtime_env.g1_r1_candidate_load_origin, "candidate_ps9")
    origin_ps9 = ps9_stage_binding(runtime_env.g1_r1_load_origin, "r1_ps9")
    for binding in (candidate_ps9, origin_ps9):
        check(binding["stage_budget"] == "G1_R1_PS9_STAGE_BUDGET",
              f"{binding['stage']} must keep the shared PS9 stage budget symbol")
    check(runtime_env.G1_R1_PS9_STAGE_BUDGET == 40.0,
          "the PS9 stage budget must stay at the envelope's 40 seconds")

    # (6) 기록된 130줄 계약에 대응하는 기계 게이트가 없다는 사실(N14 근거).
    caps = re.search(r'"docs/STATUS\.md":\s*(\d+)', gates.get("checks/context_limits.py", ""))
    machine_cap = int(caps.group(1)) if caps else None
    prompt_text = (REPO / "loop/PROMPT.md").read_text(encoding="utf-8")
    check("130줄 이하로 유지한다" in prompt_text,
          "loop/PROMPT.md no longer states the 130-line STATUS contract")

    report = {
        "lap": 339,
        "role": "middle",
        "reviews": "lap338 provenance policy draft (no execution, no input, no memory write)",
        "status": {"lines": len(status_lines), "cap_contract": 130,
                   "machine_cap_in_context_limits": machine_cap},
        "compaction": {"lap337": {"name": compaction.name, "body_sha256": body_sha,
                                  "body_lines": body_lines, **header},
                       "named_by_status": named, "pointer_verified": pointer_ok},
        "stale_probes": stale,
        "gates_referencing_history_probes": [
            name for name, text in gates.items() if "history/laps/probes" in text
        ],
        "findings": {
            # 전이 상태: 단언하지 않고 보고만 한다.
            "R_a_candidate_names_in_tests": {
                name: sum(
                    path.read_text(encoding="utf-8").count(name)
                    for path in sorted((REPO / "tests").glob("*.py"))
                )
                for name in CANDIDATE_NAMES
            },
            "R_b_candidate_ps9": candidate_ps9,
            "R_b_origin_ps9": origin_ps9,
            "R_b_asymmetric": candidate_ps9["stage_started"] != origin_ps9["stage_started"],
            "snapshots_dir_exists": (REPO / "docs/history/laps/snapshots").is_dir(),
            "live_source_sha256": {
                "tools/runtime_env.py": sha256_file(REPO / "tools/runtime_env.py"),
                "tests/test_lap326_r1_load_origin.py":
                    sha256_file(REPO / "tests/test_lap326_r1_load_origin.py"),
            },
        },
        "failures": sorted(failures),
    }
    print(json.dumps(report, ensure_ascii=False, indent=1, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
