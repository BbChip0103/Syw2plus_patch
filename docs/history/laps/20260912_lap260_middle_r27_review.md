# 2026-09-12 | lap 260 | 목표 G1 — R27 독립 검수 (middle)

- lap 번호 근거: `loop/.lap_counter`=**260**(읽기만 함). 루프 헤더는 lap=259라고 표시했으나
  `loop/PROMPT.md`가 counter 파일을 권위로 정하므로 이 바퀴는 260이다. lap258은 middle(R26)과
  work(R27)가 같은 번호를 쓴 기록이 이미 있어 259는 비어 있다.
- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5`/high / middle(진단·계획·확인).
  게임 코드 hands-on 수정 없음. 검수 probe만 새로 작성했다.
- 가설: lap258 work의 R27(production 실제 호출 shape `(stage_budget=None, stage_started=None)`을
  `STAGE_BUDGET_UNAVAILABLE`로 고정하는 회귀)이 lap258 middle의 생존 변이 M5(우선순위 역전)를
  실제로 사살하고, R26/R25/R15 회귀를 약화하지 않았는가.
- 예상 PASS / FAIL 조건: PASS = 독립 행렬 불일치 0, M0 대조군 일치, 적용 가능한 변이 생존 0,
  범위 밖 사살 0, 그리고 R27만 제거했을 때 M5가 되살아나 R27이 하중을 받는 것이 증명될 때.
  FAIL = 생존 변이가 남거나 R27이 어떤 변이에도 단독 하중을 갖지 않을 때.
- 변경 파일 / 커밋: `docs/history/laps/probes/20260912_lap260_r27_review_probe.py`,
  `..._report.json`, 본 기록, `docs/STATUS.md`, `loop/ESCALATE_SOL`,
  `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`. SUT/테스트는 검수 중 변경하지 않았다.
  uncommitted, `LOOP_ALLOW_COMMITS=0`.
- 원본 SHA / 환경 / fixture: 원본 EXE pin
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변; 제품 EXE/DLL/assets/
  baseline/golden 변경 0. Python 3.13.5/.venv, fake monotonic + injected direct selection reader
  `OSError`, `_g1_run_input_sequence` production 시퀀스 fixture, /tmp depth-matched mirror.
  실제 게임/Wine/Xvfb/PNG **0회**; 플레이어·지도·군대 N/A.
- 실행 명령 / 로그:
  - probe `.venv/bin/python docs/history/laps/probes/20260912_lap260_r27_review_probe.py`,
    exit 0, 리포트 `docs/history/laps/probes/20260912_lap260_r27_review_report.json`.
  - `make check` = `279 passed`; Ruff/compileall/mypy 10 source files; `CONTEXT_PASS`.
  - `LOOP_DRY_RUN=0 bash checks/safety.sh check` = `SAFETY_PASS`. 캡처 없음.

## 측정값

- **C0** targeted+인접 선택: `14 passed / 130 deselected`, returncode 0.
- **C1** 독립 행렬 **160-case**(stage 5종 × `stage_started` {None,0.0,4.25,100.0} × offset 8종),
  기대 모델은 계약에서 작성. **불일치 0**, 네 상태 모두 관측
  (UNAVAILABLE 64 / EXHAUSTED 36 / WITHIN 36 / START_UNKNOWN 24), 160건 모두
  `UNKNOWN_STATE_READ_FAILURE`.
  production 기본 호출(= `stage_started` 생략)의 실측 shape는
  `stage_budget=None`, `stage_started_elapsed=None`, `stage_budget_state=STAGE_BUDGET_UNAVAILABLE`.
  호출부 정적 확인: production 호출은 `stage_started`를 넘기지 않고 `G1_INPUT_STAGE_BUDGETS`에
  production 항목이 없다 → lap258이 지목한 도달 가능 shape가 실재함을 재확인.
- **C2** depth-matched mirror M0 = `144 passed` = 실저장소 `144 passed` (일치).
- **C3** 변이 **12종**: 적용 가능한 11종 **전부 사살, 생존 0, 범위 밖 사살 0**.
  - **M5 우선순위 역전(lap258 생존자)** → 이제 `1 failed`, 사살자는 R27 회귀 단 하나.
  - M1 WITHIN 고정 4건 / M2 EXHAUSTED 고정 4건 / M3 UNAVAILABLE 고정 3건 /
    M4 UNAVAILABLE→START_UNKNOWN 2건 / M6 START_UNKNOWN→WITHIN 1건(R27) /
    M7 `>=`→`>` 1건 / M8 EXHAUSTED→WITHIN 1건 / M9 legacy boolean True 고정 3건 /
    M10 `stage_started_elapsed` None→0.0 1건(R27) /
    M11 production 호출부가 `stage_started=started`를 넘기도록 shape 변경 1건(R27).
  - M12(production에 budget 10.0 추가)는 **비가용 변이**다. `G1_INPUT_STAGE_BUDGET_TOTAL`
    31.5초 상한 가드가 import 시 `RuntimeSafetyError`로 거부해 수집 자체가 실패한다
    (`1 error`). 상한 안에 들어오는 동등 변이 M12b(`"production": 1.5`)를 별도로 실행해
    `3 failed / 141 passed`(R27 + R26 production case + budget pin 테스트)로 사살을 확인했다.
- **C4** 하중 확인: R27 회귀 **하나만** 제거하면(`143 passed` 기준선) **M5·M6·M10·M11이 전부
  되살아난다**. 반대로 M1/M2/M3/M4/M7/M8/M9는 R27 없이도 R26 회귀가 계속 사살한다 →
  R27은 새로 하중을 받고 있고 R26/R25/R15 커버리지는 약화되지 않았다.
- 검수 전후 지문 동일: `tools/runtime_env.py`
  `e4f6a834f1ca591d2fe7acc1002beea4b343647d6ba47ff3b847f74e22455837`,
  `tests/test_runtime_env.py`
  `eaa50b919e42dd051044d4551cb2df923dd455035214200e741745e9bc15eae3`
  (lap258 work 기록값과 일치).

## 판정

**R27 범위 승인 PASS — 기계(1단)만.** lap258의 유일한 생존 변이가 죽었고, 그 사살이 R27
회귀에 단독으로 귀속됨을 제거 실험으로 증명했다. 범위 밖 사살 0으로 과잉 결합도 없다.

이것은 제품 G1 증거가 아니며 사용자 마일스톤 승인이 아니다. Stage B, 실제 게임/Wine/Xvfb는
S1/F2-R2 상위 재결 전까지 계속 금지다.

## 남은 위험 / 다음 행동

- `stage_budget_state` 소비자는 여전히 `tools/runtime_env.py` 밖에 0개다(R23/R24와 같은 형태의
  미소비 provenance 위험). 이는 R27 범위 밖이며 R23/R24 큐 항목으로 남긴다.
- 다음 한 가지: offline 큐 **R19**(R17 회귀가 함수명 `drive_wait` 하나에만 걸려 있어 개명 시
  조기-거부 삭제를 놓친다 — lap244)를 work tier가 구현하고, 다음 새 middle이 독립 검수한다.
- 상위 재결 대기(변동 없음): S1/F2-R2 scene·slot 결정성, R6-B-R2.
