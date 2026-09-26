# 2026-09-11 | lap 185 | 목표 G1 (카드2 Stage A / A-14 독립 검수)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high /
  middle tier(진단·계획·확인). 게임 코드 hands-on 수정 0건, Stage B/P6 실행 0회.
- 가설 / 사용자 관찰: lap184가 주장한 A-14(주석·기록 provenance 정정, 9자리
  `truncation_ratio` evidence, 2.4999/2.5001 경계 회귀, 값·필드·분류 순서 불변)가
  독립적으로 재현되는가.
- 예상 PASS / FAIL 조건: source SHA 3/3 일치, 전체 게이트 재현, 주석이 synthetic probe를
  실측으로 부르지 않음, 3자리 evidence로는 구분 불가한 경계를 9자리 ratio가 구분,
  엄격 부등호 유지, `UNKNOWN_BUDGET_EXHAUSTED` 우선순위 유지.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `docs/STATUS.md`, `loop/ESCALATE_SOL`, 본 기록. 제품/도구 코드 무변경.
  커밋 없음(`LOOP_ALLOW_COMMITS` 미설정).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본 EXE SHA
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변
  (`checks/safety.sh check` → `SAFETY_PASS`). 실제 게임/Wine/Xvfb/prefix/display 0회;
  독립 probe는 synthetic monotonic clock만 사용; 플레이어/지도/군대 N/A.

## 실행 명령 / 수치

- `sha256sum tools/runtime_env.py tests/test_runtime_env.py
  docs/history/laps/20260911_lap182_luna_a13_threshold.md` → lap184 기록과 **3/3 MATCH**
  (`c2adaa2e…5850`, `a674892c…4c16`, `88c12cff…a489`).
- `make check` → **207 passed** (35.83s); Ruff `All checks passed!`; compileall;
  mypy `Success: no issues found in 9 source files`; `CONTEXT_PASS`; EXIT=0.
- `.venv/bin/python -m pytest -q tests/test_runtime_env.py` → **94 passed**.
- `… -k 'wait_state or input_verdict'` → **10 passed, 84 deselected**.
- `bash checks/safety.sh check` → `SAFETY_PASS`; `git diff --check` → PASS.
- 독립 경계 probe `/tmp/lap185_probe.py`(lap184 테스트를 쓰지 않고 `_wait_state`를 직접 호출):

  | pre-poll | classification | truncation_seconds | truncation_ratio | exceeds |
  |---|---|---|---|---|
  | 0.0 | FAIL_NO_EFFECT | 0.0 | 0.0 | False |
  | 0.30 | FAIL_NO_EFFECT | 0.3 | 0.03 | False |
  | 2.4999 | FAIL_NO_EFFECT | **2.5** | 0.24999 | False |
  | 2.5000 | FAIL_NO_EFFECT | **2.5** | 0.25 | False |
  | 2.50004 | UNKNOWN_OBSERVATION_WINDOW_TRUNCATED | **2.5** | 0.250004 | True |
  | 2.5001 | UNKNOWN_OBSERVATION_WINDOW_TRUNCATED | **2.5** | 0.25001 | True |
  | 8.0 | UNKNOWN_OBSERVATION_WINDOW_TRUNCATED | 8.0 | 0.8 | True |

  `stage_budget<=0`은 0.0/-1.0 모두 `RuntimeSafetyError`로 거부된다.

## 판정 — A-14 승인

- **provenance**: `tools/runtime_env.py:1987-1991` 주석은 이제 "design assumption based on
  retaining at least 75% of a stage's observation window, not a measurement of pre-poll work"이며
  실제 분포 미측정과 Stage B 재평가 의무를 명시한다. lap182 기록에도 정정 절이 추가됐고
  원래 수치·판정은 provenance 보존을 위해 남아 있다. A-14 요구 충족.
- **evidence 정밀도**: 위 표가 A-14의 핵심 주장을 독립 확인한다. 기존 3자리
  `truncation_seconds`는 2.4999/2.5000/2.50004/2.5001을 **모두 2.5로 접어** 구분하지 못하는데,
  9자리 `truncation_ratio`는 0.24999 / 0.25 / 0.250004 / 0.25001로 분리한다.
  `truncation_threshold_ratio`=0.25가 함께 기록되어 비교를 재구성할 수 있다.
- **경계**: 2.5000초 정확값이 `FAIL_NO_EFFECT`로 남아 엄격 부등호가 유지되고, 전환은 단조롭다.
  `UNKNOWN_BUDGET_EXHAUSTED` 우선순위, 임계값 `0.25`, 기존 필드는 모두 불변이다.
- 따라서 **A-14는 모델 기술 컨펌으로 승인**한다. 이는 사용자 마일스톤 승인이 아니다.

## 동반 발부 카드 A-15 (work tier) — 잘림 evidence 원인 혼동

`stage_deadline = min(run_deadline, stage_started + stage_budget)`에서 **run_deadline이
잡히는 경우** `truncation_seconds`가 사전작업이 아니라 전체 run 예산 소진을 재는데,
같은 이름으로 기록된다. 독립 probe(pre-poll=2.0초, timeout=5.0초, budget=10.0초):

- `truncation_seconds` = **7.0**, `truncation_ratio` = **0.7**,
  `truncation_threshold_ratio` = 0.25, 그런데 `truncation_exceeds_threshold` = **False**.
- 즉 같은 evidence 레코드 안에서 ratio(0.7)가 threshold(0.25)를 넘는데 "exceeds" 필드는 거짓이다.

분류 자체는 틀리지 않는다. 이 경로는 항상 `remaining=0`이 되어 우선순위가 높은
`UNKNOWN_BUDGET_EXHAUSTED`로 귀결된다. 문제는 **evidence의 자기모순과 오염**이다:

- STATUS blocker가 요구하는 "Stage B 첫 run에서 실제 잘림 분포를 기록해 2.5초 임계값을
  재평가"를 수행할 때, 예산 소진 run의 7.0초짜리 가짜 잘림값이 분포에 섞이면
  임계값 재평가가 그대로 오염된다. 이는 A-14가 아니라 A-12/A-13부터 있던 계산이지만,
  A-14가 `truncation_exceeds_threshold`라는 이름을 새로 부여하면서 모순이 드러났다.
- 입력 phase는 run 후반부라 실제 run에서 도달 가능한 경로다(stage 진입 시 잔여 예산<10초).

A-15 요구(구현은 work tier):
1. 사전작업으로 인한 잘림과 run 예산 clamp로 인한 축소를 **분리된 필드**로 기록한다.
   기존 필드명을 재사용해 의미를 바꾸지 말고, clamp 여부를 명시적 boolean으로 남긴다.
2. `truncation_exceeds_threshold`는 함께 기록된 `truncation_ratio`/`truncation_threshold_ratio`
   비교와 항상 일치해야 한다. 일치가 불가능하면 필드명을 의미에 맞게 바꾼다.
3. clamp 경로 회귀를 고정한다(예: pre-poll=2.0/timeout=5.0/budget=10.0 →
   `UNKNOWN_BUDGET_EXHAUSTED` 유지 + 사전작업 잘림은 2.0초로 보고).
4. 임계값 `0.25`, 분류 우선순위, 기존 PASS/FAIL 판정은 변경 금지.

- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: A-14 독립 검수 완료(승인).
  Stage B와 P6는 `docs/feedback/APPROVALS.md`에 사용자 승인이 없어 계속 금지다.
  실제 원본/후보 나란히 입력 비교, WM_CLOSE 종료 결함, G2~G4 제품 증거는 여전히 미검증이다.
- 다음 한 가지: work tier가 A-15를 구현한다. Stage B/P6는 사용자 승인 전까지 금지.
