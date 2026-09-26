# 2026-09-21 | lap456 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5` / high, 실무(work) 역할.
  카드 발행자는 lap455 middle(Claude Code `claude-opus-5`/high).
- 가설 / 사용자 관찰: 카드 `docs/work/active/G2_NATURAL_ARRIVAL_FIXTURE_LEVER_PROBE_LAP455.md`(W22)의
  단일 질문 — 활성 owner의 `used`가 24k tick에서 600~1,698에 머무는 현 상태(gap → 5,000)를
  fixture/설정 레버만으로 메울 수 있는가? 6 arm(A0 baseline, A1 지도크기 d4a=1, A2 AI 8→4,
  A3 게임타입 d44=0, A4 시드 42→99, A5 지형 d46=1)을 tick 8,000 짧은 창으로 실행.
  게임 AI/바이너리 로직 변경 없음, op4/시딩 없음, op7(자원 공급)만 사용.
- 예상 PASS / FAIL 조건: 카드 §5 고정 판정식 — `FEASIBLE`은 어떤 arm이
  `U_min≥718(=2×359)` **그리고** `r_slow≥0.0341 used/tick`(tick 6,000→8,000 구간)을 동시 충족.
  전부 두 조건 다 미달이면 `NOT_FEASIBLE`, 유효 arm<4면 `BLOCKED`, 정확히 한 조건만 넘긴 arm이
  있으면 `PARTIAL`(+후속 1 arm 명시).
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  - `tools/inmm_stub/control_executor.c` — 추가적(additive)으로만 변경. 새 exact-match opt-in
    goal 리터럴 5개(`G2_EIGHT_AI_D4A1_GOAL`/`_AI4_GOAL`/`_D44_0_GOAL`/`_D46_1_GOAL`/
    `_SEED99_GOAL`) 추가, `is_g2_eight_goal()`이 두 리터럴 대신 7개를 받아들이도록 확장,
    `chain_inject_seed_from_goal()`에 `_seed99` suffix 추가, G2 lobby 설정 블록 내부에
    `owner0_ai`/`record[2]`/`d44`/`d46`/`d4a`를 goal-종속 표현식으로 일반화(레거시 두 goal에
    대해서는 수학적으로 동치 — 아래 검증 참조). 게임 EXE/DLL AI·경로·생산 로직 미변경.
  - `tests/test_g2_eight_owner_setup.py` — 위 소스 리터럴 변경에 맞춰 핀 테스트 갱신
    (기존 정확-문자열 핀 3건이 새 표현식과 불일치해 실패 → 갱신) + 신규 회귀 테스트
    `test_g2_legacy_goals_compute_identical_config_to_pre_w22_source` 추가(레거시 두 goal의
    `owner0_ai`/`record[2]`/`d44/d46/d4a`가 lap456 이전과 동일한 진리표를 내는지 Python으로
    재도출해 검증 — 문자열 핀이 아니라 동작 핀).
  - 커밋: uncommitted (`LOOP_ALLOW_COMMITS=0`, 사용자 명시 허용 없음). 경로/해시는 아래.
    - `control_executor.c` sha256(수정 후): `6d2ff139c4777ad8eac282699fa6c7649dfd0ddd5fb9d2c64f994c486ef41f1b`
      (첫 빌드 시점 기록값 — 이후 "roster/save"→"roster/persistence" 문구 수정으로 최종 파일은
      다르며, `make check` 최종 재실행이 최종 소스 기준 791 passed로 확인함).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  - 원본 `syw2plus_original.exe` SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
    — 실행 전/후 직접 재해시로 불변 확인.
  - 후보 `a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68` — arm마다
    현재 source로 재빌드해 SHA 일치 확인(핀 복사 아님, N53).
  - 브리지 DLL: arm마다 재빌드(각기 다른 SHA, `<arm>/fingerprint.json` 참고 — 이는 DLL 자체가
    아니라 빌드 타임스탬프/경로가 바뀌는 통상적 비결정 요소이며 소스는 동일).
  - 격리 실행: `runtime_env.prepare()`로 매 arm 전체 게임 사본 + 전용 Wine prefix + 전용 Xvfb
    display(`:3981`~`:3986`) 새로 생성. 자원: op7로 rice/wood 1,000,000 지급(8 owner 전원),
    시딩(op5/op6) 없음, op4 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - 스크립트: `temp/Syw2plus_patch/g2_capacity/20260921_lap456_w22_lever_probe/w22_arm_run.py`
    (lap442/446/448 스크립트를 본떠 작성, `runtime_env.py`의 `_g2_initial_creation_gate` 검증기는
    이 실행 경로에서 애초에 호출되지 않아 카드 §2-7이 지목한 파라미터화는 이번 스타일에는
    불필요 — `w22_lever_matrix.md` 노트에 스코프 결정으로 기록).
  - 실행: `python3 w22_arm_run.py --arm {A0..A5} --display :39{81..86}` 순차 동기 실행(모델
    세션이 직접 대기, background로 넘기고 세션 종료하지 않음 — INBOX 2026-09-21 01:01 준수).
  - 산출물: `temp/Syw2plus_patch/g2_capacity/20260921_lap456_w22_lever_probe/{A0..A5}/`
    각 `samples.jsonl`(초당 표본, rice/wood/owner별 필드 포함), `fingerprint.json`,
    `run_summary.json`, `resource_receipts.json`, `orchestrator.log`.
  - 필수 fail-closed 산출물: `.../w22_lever_matrix.md`(카드 §6 형식 그대로, 6 arm 전체 행 포함).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  | arm | 레버 | map | 활성 owner | 도달 tick | U_min | U_med | r_slow |
  |---|---|---|---|---|---|---|---|
  | A0 | baseline | 100×100 | 8 | 8021 | 334 | 655.0 | 0.0546 |
  | A1 | d4a=1 | 140×140(실측 확인) | 8 | 8019 | 676 | 789.0 | 0.1160 |
  | A2 | AI 8→4(owner4-7 ai=0) | 100×100 | 4 활성(+4 비활성 존재) | 8020 | 569 | 717.5 | 0.1067 |
  | A3 | d44=0 | 100×100 | 8 | 8021 | 531 | 665.0 | 0.0841 |
  | A4 | seed=99 | 100×100 | 8 | 8020 | 506 | 742.5 | 0.0865 |
  | A5 | d46=1 | 100×100 | 8 | 8015 | 462 | 574.0 | 0.0907 |

  전 arm `fault_or_crash=0`, `live==Σcount` 불일치 0, `used>5000` 관측 0.
  6 arm 전부 `U_min<718`이면서 `r_slow≥0.0341`(정확히 한 조건만 충족) ⇒ 카드 §5 정의상
  **`PARTIAL`**. A1(지도 확대)이 U_min·r_slow 둘 다 최고치로 가장 유망.
  `make check` **791 passed**(790+신규 테스트 1) + Ruff + compileall + mypy + `CONTEXT_PASS`,
  `checks/safety.sh check` → `SAFETY_PASS`, 원본 직접 재해시 불변. 이번 회차 source 변경함(N22
  명시): `control_executor.c` + `tests/test_g2_eight_owner_setup.py`.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - 이번 소스 변경은 **work 자기 판정**이며 다음 middle의 독립 검수가 아직 없다. 특히
    `test_g2_legacy_goals_compute_identical_config_to_pre_w22_source`가 레거시 동작 보존을
    Python 재도출로 검증했다는 주장은 재계산 검수 대상이다.
  - A2 해석 위험: "AI 8→4"는 owner4-7을 완전히 제거한 것이 아니라 `ai=0`으로만 만든 것 —
    4명은 여전히 시작 유닛/시작 위치를 점유한다(수동적 공간 소비자). `w22_lever_matrix.md`에
    명시했고, "4인 합격 주장 금지"(카드 §3) 준수.
  - 144k 카드 발행 금지 유지(카드 §1-5). 이번 회차는 실제 5,000 도달을 만들지 않았다.
  - `local/runtime`이 이번 6회 실행으로 82G/37개로 늘었다(255G 여유, 위기 아님) — 정리는
    이번 카드 범위 밖이라 수행하지 않았고, 다음 회차가 필요시 lap429 선례로 판단한다.
- 다음 한 가지: 카드 §5 PARTIAL 처리대로 **A1 하나만** 후속 — 동일 설정(d4a=1, 140×140,
  8-AI goal, seed42, op7 자원, 시딩 없음)으로 창을 tick 24,000까지 연장해 `U_min`이 718을
  넘어 계속 증가하는지, `r_slow`가 유지되는지 확인. 새 레버 값(예: d4a=2) 추가 금지 — 검증
  안 된 값이며 재계획 없이 이 카드 §7 되물음/144k 재논의로 넘어가지 않는다. 다음 middle이
  이번 회차의 소스 변경(control_executor.c 확장, 핀 테스트 갱신)과 6-arm 원시 수치를
  재계산 검수한 뒤 W23(A1 연장 soak) 카드를 발행한다.
