# 2026-09-23 | lap 507 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5`/high, work(실무). 카드
  `docs/work/active/G2_Q8_USED_CEILING_QUANTIFICATION_LAP505.md`(W29, lap505 strategy 발행).
- 가설 / 사용자 관찰: lap504 N150이 owner5 `used` 구조적 천장을 평균 보급비 기반으로 **추정**
  (≈2,030)했다. Q8 = "8인 각각 전비 5,000 자연 도달이 stock 표 아래서 산술적으로 불가한가"를
  실측(추정 아님)으로 닫는다.
- 예상 PASS / FAIL 조건: 8 owner 각각의 `used` 천장을 `Σ(typemax_eff × 실측 보급비)`로 계산해
  k(천장<5,000인 owner 수)를 구한다. k=8 ⇒ `NATURAL_ARRIVAL_ARITH_INFEASIBLE`, 1≤k≤7 ⇒
  `PARTIAL`, k=0 ⇒ N150 반증 재회부(사전 고정, 카드 §3).
- **직전 회차(lap506) 경과:** 동일 카드로 동일 스크립트(`w29_ceiling_run.py`)를 작성해 실행했으나
  background로 띄운 뒤 회차를 종료해 loop cleanup이 죽였다(표본 116/24,000에서 절단, 잔류
  프로세스 0, lap 기록 없음 — lap463·482·502에 이은 4번째 반복, `loop/PROMPT.md`③에 규칙
  명문화됨). 이번 lap507은 **그 스크립트를 새로 쓰지 않고 그대로**(바이트 비교: 파일 수정 없음)
  실행했다. 차이점: (1) lap506의 부분 산출물(`bridge_build/`, `samples.jsonl` 등)을
  `lap506_partial_attempt/`로 이동 보존 후 클린 상태에서 재실행(스크립트가 `samples.jsonl`을
  append 모드로 열어 이전 잔여물과 섞이는 것을 방지, `bridge_build/`는 `exist_ok=False`라
  남아있으면 즉시 예외) — 이것은 스크립트 코드 변경이 아니라 스크립트가 기대하는 빈 출력
  디렉터리 상태 복원이다. (2) Monitor 도구로 `orchestrator.log`를 `tail --pid=<PID> -f`로 지켜보며
  **세션을 종료하지 않고 완주까지 대기**(PROMPT③의 명시 지시 그대로).
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 제품 source **0건** 변경. 이 lap이
  쓴 파일: `analysis/memory_maps/g2_kind_supply_cost_table_lap507_20260923.md`(신규),
  `docs/history/laps/20260923_lap507_work_w29_used_ceiling_probe.md`(이 문서),
  `loop/ESCALATE_SOL` §68 추가, `docs/STATUS.md`/`docs/feedback/INBOX.md` 갱신. uncommitted
  (`LOOP_ALLOW_COMMITS` 미설정/0).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(실행 전후 동일 확인),
  후보(N=4001 persistence-compat) `a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68`,
  bridge dll `b4a8bad16a1156d70c6cc8e3593df45defd46608cce3df0b6f248bf7582be1b6`. 격리 Wine prefix,
  Xvfb `:4001`, 지도 140×140(seed 42), 8인 AI 전원 활성(`active_owners=[0..7]`), goal
  `_custom_game_chain_inject_g2_eight_ai_d4a1_seed42`(op7 자원만 지급, 시딩 없음, lap458/502와
  동일 결정적 궤적).
- 실행 명령 / 로그 / 캡처 경로 및 해시: `python3 w29_ceiling_run.py --display :4001`(REPO 기준
  상대 경로 없이 절대경로 실행). 산출물
  `temp/Syw2plus_patch/g2_capacity/20260923_lap506_w29_used_ceiling/`(디렉터리명은 lap506이
  만든 것을 유지 — 카드 §4가 "20260923_lap50X" 패턴을 허용): `run_summary.json`,
  `ceiling_table.json`, `type_specs.json`, `production_table.json`, `partial_evidence_check.json`,
  `samples.jsonl`(721줄), `orchestrator.log`, `fingerprint.json`, `resource_receipts.json`.
  lap506의 부분 산출물은 `lap506_partial_attempt/` 하위에 원문 그대로 보존(삭제 없음).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - 실행: `stop_reason=stop_tick_reached`, `final_tick=24029`, `sample_count=721`,
    `fault_or_crash=False`, `U3_live_count_mismatch_samples=0`(`U3_pass=True`),
    `any_owner_used_over_5000=False`, `max_live=775`, `max_slot_index_seen=4000`.
    `source_unchanged=True`, `control_executor_c_unchanged=True`. **`verdict=PROBE_OK`.**
  - 카드 §1(보급비 주소) 채택 조건 재확인: `cost[27]+cost[76]=20`(일치), `cost[80]=0`(일치).
  - 카드 §2(crowd 채널): `TYPESPEC_BASE+kind*0x394+0x4C` 재해석 시 65개 생산 kind 전부
    비퇴화값(0 아님) — flat-array 가정(N147, 전부 0)과 다른 결과라 **주소 정정은 지지**되나,
    이 dword가 G-7 크라우드 게이트와 어떻게 연결되는지는 **디코딩하지 못했다** ⇒ **H-CROWD는
    카드 지시대로 UNKNOWN 유지**(상세 근거 `analysis/memory_maps/g2_kind_supply_cost_table_lap507_20260923.md` §3).
  - 카드 §3(8 owner 천장): owner별 천장 [2445, 1070, 2445, 2050, 2445, 1190, 2050, 2445],
    전부 5,000 미만 ⇒ **k=8**. 전체 65종 이론 최대(모든 생산건물을 다 지었을 때) = **8,077**
    (> 5,000, Σtypemax=568).
  - **사전 고정 판정식 적용 결과: `NATURAL_ARRIVAL_ARITH_INFEASIBLE`**(카드 §3, 현 종단 건물
    구성 기준). 단서: 이론 최대 8,077 > 5,000이므로 "표 값이 절대적으로 불가능하게 만든다"가
    아니라 "이 fixture에서 AI가 실제로 지은 건물 구성(27종 중 6~8종)이 5,000 미만 천장을
    만든다"는 **구성 종속** 결론이다. 건물을 더 지을 수 있는지는 이 lap이 조사하지 않았다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - 회귀: 없음(제품 source 무변경, `SAFETY_PASS`).
  - 남은 위험: H-CROWD 채널 의미 미해독(위 그대로 UNKNOWN). owner별 건물 종 수가 27종 중
    6~8종에 그친 이유(건설 AI 판단/길찾기/자원/시간 부족)는 미조사 — "이론 최대 8,077"과
    "실측 천장 1,070~2,445"의 격차를 설명하지 않는다.
  - **독립 검수 없음(work 자기 결과)** — 카드 §5·§67 예산대로 다음 middle 1회가
    `samples.jsonl`+`ceiling_table.json` 원시에서 재계산해야 2단이 선다. 예산 소진: W29는
    **work 1회 + middle 1회**로 한정(§67), 이 lap이 그 work 1회다.
  - 사용자 승인: 해당 없음(읽기 전용, (ㄴ) 승인 대상 아님, 04:14 지시와 동일 범위).
    (ㄴ) 착수·Q7-B 3단 마일스톤·(ㄱ)/(ㄷ)·Q8 자체의 (ㄱ)/(ㄴ)/(ㄷ) 선택은 전부 사용자 전권 —
    이 lap은 판정식을 적용해 `k=8`을 보고할 뿐 선택하지 않는다.
- 다음 한 가지: middle(Opus5/high) 1회가 이 집계를 원시에서 독립 재계산(불일치 0 확인 목표)하고,
  H-CROWD UNKNOWN 유지가 타당한지, "건물 구성이 왜 6~8종에 그쳤는지" 후속 조사가 필요한지
  판단한다. §67 예산(work+middle 각 1회)이 이것으로 소진되므로, 그 뒤 사용자 Q8/(ㄱ)/(ㄴ)/(ㄷ)
  응답이 없으면 `loop/PROMPT.md`④6에 따라 STOP.
