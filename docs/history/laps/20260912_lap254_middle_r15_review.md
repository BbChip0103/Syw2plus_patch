# 2026-09-12 | lap 254 | 목표 G1 — R6-B-R15 독립 검수 (middle tier)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5`/high; middle tier
  (진단·계획·확인). 게임 코드 hands-on 수정 없음, SUT 무변경.
- 가설 / 사용자 관찰: lap253은 직접 selection reader 실패가 run/stage budget 소진보다 우선
  `UNKNOWN_STATE_READ_FAILURE`로 분류되고 `finished_elapsed`/`remaining_budget_after`/
  `stage_budget_exhausted`/`run_budget_exhausted` provenance가 남는다고 주장했다. 근거는
  "targeted 11 passed"와 Fast뿐이며, (a) 단일 fixture 밖에서 timing 필드가 맞는지, (b) 우선순위
  주장이 공허하지 않은지(두 경로가 우연히 같을 수 있음), (c) 새 성질이 실제로 테스트에 걸려
  있는지를 보이지 않는다.
- 예상 PASS / FAIL 조건: C0 출하 케이스 통과, C1 독립 기대 모델 대비 불일치 0, C1b poll 경로가
  같은 조건에서 실제로 `UNKNOWN_BUDGET_EXHAUSTED`를 답해 비대칭이 실재함, C2 깊이 일치 미러
  M0가 실제 저장소와 동일, C3 변이 5종이 각각 출하 테스트를 1건 이상 사살. 하나라도 실패하면
  범위 승인하지 않는다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): SUT 무변경 —
  `tools/runtime_env.py` sha256
  `0e3bf38220e8b762b2ba3b38d2151cfb51a6e8d4a6b85fd03fba6c41b89cb83c`,
  `tests/test_runtime_env.py` sha256
  `d7778430c156f0c4493891e0cd8adc2d21166602c594f5537dee2a84359606e3` (검수 전후 동일, lap253
  기록과 일치). 신규 산출물은 probe/report와 문서뿐이며 모두 uncommitted, `LOOP_ALLOW_COMMITS=0`:
  - `docs/history/laps/probes/20260912_lap254_r15_review_probe.py` sha256=`d6cfc68a9a41d0b7d0ced1c464ab9cc2ac306db80ac39a87ff5c4f4b49a1d6ea`
  - `docs/history/laps/probes/20260912_lap254_r15_review_report.json` sha256=`8ef611a33bcbef7af19790b66138ec9873a79aea38c24ca4e9afae34cb1fd8dc`
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 EXE pin
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변; 제품 EXE/DLL/assets/
  baseline/golden 변경 0. Python 3.13.5/.venv, fake monotonic clock + 주입 예외 fixture.
  실제 게임/Wine/Xvfb/PNG 0회, 플레이어·지도·군대 N/A. Stage B 실행 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `.venv/bin/python docs/history/laps/probes/20260912_lap254_r15_review_probe.py --output
  docs/history/laps/probes/20260912_lap254_r15_review_report.json`;
  `.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_runtime_env.py` = **140 passed**;
  `make check` = **275 passed** (Ruff/compileall/mypy 10 files, `CONTEXT_PASS`);
  `LOOP_DRY_RUN=0 bash checks/safety.sh check` = **SAFETY_PASS**. 캡처 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): R15 **구현은 검증됨, 범위 승인은 FAIL(커버리지)**.
  - **C0 PASS** — 출하 직접-reader 케이스 12 passed / 128 deselected.
  - **C1 PASS** — 독립 행렬 74 case(stage 6종 × 종료시각 4종 × 예외 3종 + 성공 대조 N0 +
    미포획 예외 대조 N1). 72개 실패 case 전부 `UNKNOWN_STATE_READ_FAILURE`, 다른 분류 0건.
    기대 모델(여기서 계약만 보고 작성, stage budget 표도 재기술)과 **불일치 0**. 종료시각
    2.5/9.999/10.0/12.5s에서 `finished_elapsed`/`remaining_budget_after` 반올림값,
    `run_budget_exhausted`(10.0·12.5에서만 true), `stage_budget_exhausted`(`stage_started`가
    None이거나 production처럼 budget이 없으면 항상 false), 예외 객체의 **비반올림** 값,
    메시지의 read point, poll 계수 0, provenance 문자열이 모두 일치했다. N0에서 성공 read는
    그대로 반환되고 N1에서 `RuntimeError`는 재분류 없이 통과했다.
  - **C1b PASS** — 같은 소진 조건(timeout=1.0, stage_budget=10.0, 모든 read 실패)에서 `_wait_state`
    는 실제로 `UNKNOWN_BUDGET_EXHAUSTED`(read_error_count=4)를 답했고 직접 경로는
    `UNKNOWN_STATE_READ_FAILURE`였다. 비대칭은 실재하며 R15 주장은 공허하지 않다.
  - **C2 PASS** — 깊이 일치 미러 M0 대조군 **140 passed** = 실제 저장소 140 passed (lap246 R20 교훈).
  - **C3 FAIL** — 변이 5종 중 **M4가 생존**했다. `stage_budget_exhausted`를 무조건 `True`로
    고정해도 미러 전체가 **140 passed**로 통과한다. M1(우선순위 반전)/M2(timing 필드 제거)/
    M3(`run_budget_exhausted` false 고정)/M5(예외 timing 0)는 각각 R15 테스트 1건만 사살하고
    범위 밖 0건이었다. 즉 R15의 네 필드 중 `stage_budget_exhausted`만 회귀가 없다.
  - 게임 기반 Stage B는 S1/F2-R2 재결 전 금지로 **SKIP/N/A**.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 구현 자체는 74-case 독립 행렬에서 정확하므로
  제품 동작 결함은 관측되지 않았다. 결함은 **증거 강도**다. `stage_budget_exhausted`를 읽는
  출하 테스트는 `tests/test_runtime_env.py:1412` 한 줄뿐이고 그 fixture의 기대값이 True라서,
  상수 True 구현과 실제 구현을 구별하지 못한다. 음성 case(예산 내부, production처럼 budget None,
  `stage_started=None`)가 하나도 없다. R22와 같은 단일-테스트 결합 문제의 재발이다.
  사용자 마일스톤 승인 없음. G1 제품 증거, S1/F2-R2, R6-B-R2, R19~R24, WM_CLOSE, G2~G4 미해결.
  신규 큐:
  - **R25**: `stage_budget_exhausted`에 음성 회귀가 없다(M4 생존, lap254 실측). 값이 뒤집혀도
    Fast가 초록이다.
  - **R26**: `stage_budget_exhausted=false`는 "예산 내부"와 "이 stage에 budget이 없음"
    (production) / "`stage_started` 미상"을 구별하지 못한다. 같은 record의 `stage_budget`·
    `stage_started_elapsed`가 null인지 함께 읽어야만 구별된다. R23/R24와 동종이며 제품 영향 없음.
  - 확인: `run_budget_exhausted`/`stage_budget_exhausted`를 읽는 소비자는 `tools/runtime_env.py`
    밖에 **0개**다(테스트·문서·본 probe 제외). R23/R24와 같은 상태다.
- 다음 한 가지: work tier(Luna 또는 Sonnet5/high)가 게임 없이 **R25**를 수리한다 —
  `stage_budget_exhausted`에 음성/경계 회귀를 추가해 상수 True·상수 False 구현이 모두 죽게 한다
  (예산 내부 false, 경계 `finished == stage_started + stage_budget` true, `stage_started=None`
  false, production처럼 `stage_budget=None` false). SUT 로직 변경은 불필요하며 관측상 정확하다.
  Stage B·게임/Wine/Xvfb는 S1/F2-R2 상위 재결 전까지 금지한다.
