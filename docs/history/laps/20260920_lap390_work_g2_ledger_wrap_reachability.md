# 2026-09-20 | lap 390 | 목표 G2 (F4 handoff W1)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5` / high, 실무(work) tier.
  loop/.lap_counter=390. handoff 발행자는 lap389 middle(`claude-opus-5`/high).
- 가설 / 사용자 관찰: 카드 W1(`docs/work/active/G2_OWNER_TRANSFER_CAP_MIDDLE_JUDGMENT_LAP389.md` §C) —
  전비 장부 `+0x200C`가 16-bit이고 생산 gate가 부호있게 읽는다(F4). 9/19 실측 전역 used 합 40,000이
  signed16 상한 32,767을 넘으므로 산술상 랩이 가능하다. 질문: **같은 fixture에서 실제로 한 owner의
  `used`가 32,767을 넘어(음수로 랩) 관측되는가?**
- 예상 PASS / FAIL 조건(핸드오프 §C 판정식, 실행 전 고정):
  - M1: 매 sample 8인의 `used`를 signed16으로 재해석해 1회라도 음수 → **FEASIBLE**(랩 CONFIRMED), 즉시 중단.
  - M1 음수 0 & M2(단일owner used 최대치)가 32,767에 크게 못 미치고 & M3(roster 0-전환+타owner used 점프,
    FUN_00444EF0 간접증거) 0건 → **NOT_FEASIBLE**로 기록.
  - 측정 수단 자체가 부족하면 **BLOCKED**.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 제품코드/바이너리 변경 **0**.
  신규 read-only 분석 스크립트 1개(외부 temp, 메인 레포 밖):
  `…/temp/Syw2plus_patch/g2_capacity/20260919_owner_transfer_cap/lap390_work_ledger_wrap_reachability/ledger_wrap_reachability_v1.py`
  (SHA256 `2d91952c97d97945ae2187e435933a030942b17b424fbc0dc81c1bf9897c903c`) +
  `output.json`(SHA256 `12e9663ab09b3be80fb9134e90b6a11ef1a6b11992bf3d340832e2442bc1f967`).
  이번 lap이 새로 실행한 게임/바이너리 명령 **0건** — 기존 9/19 관측 하네스가 이미 만든
  `samples.jsonl`을 다시 읽었을 뿐이다. uncommitted(LOOP_ALLOW_COMMITS=0, 사용자 커밋 허용 없음).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  9/19와 **동일** fixture 재사용(신규 실행 없음, 핀 재해시로 동일성 확인) —
  `…/g2_capacity/20260919_eight_owner_5000_stability_actual_v1/official_run1/g2_stock_24k_observation/samples.jsonl`
  SHA256 `d7bf3e1f73892b5d3ab4065dec5dd821bc2d43d71f4daadb9105a9bc2bdafdfe`(스크립트가 실행마다 재계산,
  independent_analysis_v1의 `source.sha256`와 일치 확인). 원본 EXE `b56986e0…c9c08a8ac`(불변, 손대지 않음).
  8-owner/cap5000 로드, 146 samples, tick 10020→34185.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `python3 ledger_wrap_reachability_v1.py > output.json`(rc0, exit0). 로그/출력은 위 output.json 경로.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - M1 음수 이벤트 **0건**.
  - M2 단일owner used 최대치 **5,003**(owner1, tick33185, sample140) — 32,767까지 여유 **27,764**.
  - M3(roster count→0 & 타owner used 점프) **0건** — 이 fixture 구간(24k tick)에서
    `FUN_00444EF0` 일괄흡수의 간접 신호 없음.
  - M4 전역 used 합: 첫 sample(tick10020) **40,000** → 끝 sample(tick34185) **35,427**
    (최소35,427/최대40,000) — lap389 middle 재계산과 완전 일치.
  - per-owner used 범위(signed16 재해석해도 전부 양수, 원값과 동일): owner0 3845~5000,
    owner1 4685~5003, owner2 4920~5000, owner3 4691~5000, owner4 4730~5000, owner5 3895~5000,
    owner6 3938~5000, owner7 4360~5000.
  - **판정: NOT_FEASIBLE**(현재 fixture 한정). F4의 산술 가능성(lap389)은 그대로 유효하나,
    이 자연 시뮬레이션 24k tick 구간에서는 랩 재현이 관측되지 않았다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - 이 판정은 **이 fixture 한정**이다. 랩을 실제로 트리거하려면 한 owner의 used를 5,000대의
    6~7배 수준(32,767 근접)까지 몰아야 하고, 그러려면 `FUN_00444EF0`(패배 owner 일괄흡수)를
    반복 유도하는 별도 fixture가 필요하다 — 이번 lap은 그런 fixture를 만들지 않았다(관측전용
    카드 범위 밖, 새 게임 실행/생성 fixture 금지 규칙 준수).
  - F4 자체(합격기준 재정의 판정)는 여전히 `loop/ESCALATE_SOL`에 열려 있다. 이번 lap은 그
    승격판정을 대체하지 않는다 — 단지 W1 관측 카드를 닫을 뿐이다.
  - `checks/safety.sh check` → `SAFETY_PASS`. `make check` **rc0 715 passed 153.68s**
    +Ruff/compileall/mypy10파일 Success+`CONTEXT_PASS`. 이 lap이 만든 신규 파일은 메인 레포
    밖(temp)이라 이 게이트 대상에 포함되지 않는다 — 게이트는 무변경 회귀만 확인한다.
  - 독립 검수: 다음 middle 회차가 `output.json`과 `samples.jsonl` 재계산으로 확인.
- 다음 한 가지: W1 **CLOSED**(NOT_FEASIBLE, 관측전용, 바이너리 변경 0).
  F4 판정(합격기준 (a) vs (b), 장부폭 확장 필요 여부)은 여전히 Astra/사용자 대기 —
  `loop/ESCALATE_SOL` 유지. 랩 트리거 fixture(FUN_00444EF0 반복 유도)는 별도 카드로
  제안하되 착수는 다음 middle/Astra 판정 이후.
