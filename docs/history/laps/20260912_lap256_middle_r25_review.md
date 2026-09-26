# 2026-09-12 | lap 256 | 목표 G1 — R25 독립 검수와 R15 범위 재결

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high; middle tier(진단·계획·확인).
  hands-on 게임 구현 없음, SUT 무변경. lap counter 파일 값 256을 lap 번호로 사용했다(루프 헤더의
  `lap=255`와 불일치하나 `loop/PROMPT.md`는 counter 파일 값을 따르라고 규정한다. counter는 읽기만 했다).
- 가설 / 사용자 관찰: lap255(R25)는 테스트만 추가해 lap254가 남긴 R15 범위 결함(M4 상수 True 생존)을
  닫았다고 주장한다. 주장이 성립하려면 (a) 네 semantic case가 각각 실제로 하중을 받고,
  (b) M4가 죽고, (c) R15의 나머지 세 필드와 우선순위 회귀도 여전히 살아 있고,
  (d) 인접 범위 밖 사살이 0이어야 한다.
- 예상 PASS / FAIL 조건: 독립 기대 모델과 SUT 실측이 전 grid에서 불일치 0; 미러 M0 대조군이 실제
  저장소와 동일; M1~M9 변이 전부 최소 1건 사살(생존 0); `killed_other` 0건. 하나라도 어긋나면 재반려.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 신규 probe
  `docs/history/laps/probes/20260912_lap256_r25_review_probe.py`, 리포트
  `..._r25_review_report.json`, 본 기록, `docs/STATUS.md`,
  `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`, `loop/ESCALATE_SOL`.
  SUT `tools/runtime_env.py` 무변경 sha256 `0e3bf38220e8b762b2ba3b38d2151cfb51a6e8d4a6b85fd03fba6c41b89cb83c`,
  `tests/test_runtime_env.py` 무변경 sha256
  `40c91b76e59c9f23b7256a0cb7b591deb028d78c9bf8d67793566a44d292a7df` (검수 전후 동일).
  uncommitted, `LOOP_ALLOW_COMMITS=0`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 EXE pin
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변, 제품 EXE/DLL/assets/
  baseline/golden 변경 0. Python 3.13.5/.venv, fake monotonic clock + injected `OSError` direct-reader
  fixture, 깊이 일치 임시 미러(`/tmp/lap256_r25_*/sharedfolder/260320_Syw2plus/Syw2plus_patch`).
  실제 게임/Wine/Xvfb/PNG 0회, 플레이어·지도·군대 N/A.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - targeted `.venv/bin/python -m pytest -q tests/test_runtime_env.py -k '...stage_budget_exhaustion_is_semantic or ...precedes_exhausted_run_budget'` = `5 passed, 139 deselected`.
  - probe `--output docs/history/laps/probes/20260912_lap256_r25_review_report.json` exit 0:
    C0 `16 passed/128 deselected`; C1 독립 grid **105 case, 불일치 0**
    (stage 5종 × `stage_started` {None, 100.0, 104.25} × finish offset {0, 5, 9.999, 10.0, 10.001, 25, 40},
    `stage_budget`/`stage_started_elapsed`/`finished_elapsed`/`remaining_budget_after`/
    `stage_budget_exhausted`/`run_budget_exhausted`/classification 전부 대조);
    C2 미러 M0 `144 passed` = 실제 저장소 279 중 해당 파일 144와 일치;
    C3 변이 9종 **생존 0, `killed_other` 0**.
  - `make check` = `279 passed`, Ruff `All checks passed`, compileall, mypy `10 source files`, `CONTEXT_PASS`.
  - `LOOP_DRY_RUN=0 bash checks/safety.sh check` = `SAFETY_PASS`. 캡처 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **R25 독립 검수 PASS. R15 범위 승인(기계 1단).**
  변이별 사살(미러 144-test 전체 기준):

  | 변이 | 결과 | 사살한 R25 case | R15 테스트 | 범위 밖 |
  |---|---|---|---|---|
  | M1 우선순위 반전 | 4 failed | boundary, unknown-start, production | 사살 | 0 |
  | M2 timing 필드 제거 | 1 failed | – | 사살 | 0 |
  | M3 `run_budget_exhausted` False 고정 | 4 failed | boundary, unknown-start, production | 사살 | 0 |
  | **M4 `stage_budget_exhausted` True 고정** | **3 failed** | inside(9.999), unknown-start, production | – | 0 |
  | M5 예외 timing 0 | 1 failed | – | 사살 | 0 |
  | M6 `stage_budget_exhausted` False 고정 | 2 failed | boundary | 사살 | 0 |
  | M7 경계 `>=`→`>` | 2 failed | boundary | 사살 | 0 |
  | M8 `stage_started=None`→run start 대체 | 1 failed | unknown-start | – | 0 |
  | M9 `stage_budget=None`→0 대체 | 1 failed | production | – | 0 |

  네 case가 모두 개별 하중을 받는다: inside는 M4 단독, boundary는 M6/M7, unknown-start는 M8,
  unknown-budget은 M9가 각각 그 case만 사살한다. lap254 FAIL 사유(M4 생존)는 해소됐고
  M1/M2/M3/M5는 여전히 사살되므로 R15의 네 필드 + 우선순위가 전부 회귀로 덮인다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: SUT 로직·보호 자산 불변이므로 회귀 위험은 없다.
  이 승인은 **기계(1단) 범위 승인**이며 제품 G1 증거도 사용자 마일스톤 승인도 아니다.
  R26은 미해결이고 본 lap의 truth table이 그 근거를 재확인한다: `stage_budget_exhausted=false`가
  (i) 예산 내부(`unit_select`, stage_started=100.0, offset 9.999), (ii) `stage_started` 미상
  (`unit_select`, stage_started=None, offset 10.001), (iii) stage budget 없음(`production`,
  stage_started=100.0, offset 10.001) 세 상태에서 동일하게 false다. 구별하려면 소비자가
  `stage_budget`·`stage_started_elapsed`의 null 여부를 함께 읽어야 한다.
  S1/F2-R2, R6-B-R2, R19~R24, WM_CLOSE teardown, G2~G4는 여전히 미해결이다.
- 다음 한 가지: 다음 work tier(Luna 또는 Sonnet5/high)가 게임 없이 **R26**을 수리한다.
  `stage_budget_exhausted`가 위 세 상태를 구별할 수 있도록 provenance를 명시하고(예:
  `stage_budget_state` 같은 3-값 필드 또는 소비자 계약 문서화 + 회귀), 상수/축약 변이가 모두
  죽는 회귀를 함께 넣는다. 이후 큐는 R19 → R20 → R21 → R22 → R23 → R24 → F2-R1 → F3-R1 →
  F3-R2 → F6-R2. Stage B·게임/Wine/Xvfb는 S1/F2-R2 상위 재결 전까지 금지한다.

## 부록 — lap255가 남긴 `loop/ESCALATE_SOL` 원문 (본 lap에서 해소, 기록 보존)

```
lap=255 (counter file; agent only read it)
role=work (implementation) -> handoff to middle tier
reason=R25 work **PASS**; R15's prior coverage defect was repaired in tests, not SUT logic.
Four semantic cases now require `stage_budget_exhausted` to be false inside budget, true at the
exact boundary, and false when `stage_started` or the stage budget is unknown. The M4 constant-True
mutation now dies (3 tests), with no R15-adjacent range failures. No game/Wine/Xvfb/PNG, no Stage B;
machine (stage-1) work only, not a user milestone.

Evidence:
- targeted `.venv/bin/python -m pytest -q tests/test_runtime_env.py -k 'direct_selection_reader_stage_budget_exhaustion_is_semantic or direct_selection_reader_failure_precedes_exhausted_run_budget'` = 5 passed.
- transient constant-False stage-flag mirror = 2 failed/3 passed on the same targeted set; exact-boundary regression was killed.
- prior R15 probe, run against a fresh temporary mirror/output after R25: C0 12 passed/132 deselected,
  C1 PASS, C1b PASS, C2 M0 144 passed, M4 constant-True 3 failed/141 passed, killed adjacent `[]`.
- `make check` = 279 passed; Ruff/compileall/mypy 10 files; `CONTEXT_PASS`.
- `LOOP_DRY_RUN=0 bash checks/safety.sh check` = `SAFETY_PASS`.
- `tools/runtime_env.py` remains sha256
  `0e3bf38220e8b762b2ba3b38d2151cfb51a6e8d4a6b85fd03fba6c41b89cb83c`;
  original EXE pin remains `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.

What the promoted middle tier must verify next:
1. Re-run the R25 targeted cases and the mirror M0 control; confirm the semantic table above and
   that a constant-False stage flag dies on the exact-boundary case.
2. Re-run M4 (constant True) and confirm it dies while no R15-adjacent test fails; the work probe
   measured M4 as 3 failed/141 passed, killed-adjacent `[]`.
3. Decide whether the R15 range can be approved or must remain open. The work tier does not
   self-approve its own change. R26 remains queued after this confirmation.

Stage B, game, Wine and Xvfb stay forbidden until the S1/F2-R2 escalation is re-decided.
```

lap256 판정: 위 1·2·3 모두 독립 재측정으로 확인했다(1: M0 144 passed + M6 boundary 사살,
2: M4 3 failed/141 passed·범위 밖 0, 3: R15 범위 승인). 해당 escalation은 해소됐다.
