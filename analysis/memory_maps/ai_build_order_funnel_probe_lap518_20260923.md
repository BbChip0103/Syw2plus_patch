# W32 — AI 건설 오더 깔때기(점유→시작→발부→완공) 실행 결과 (lap518 work)

카드 `docs/work/active/G2_BUILD_ORDER_FUNNEL_PROBE_LAP517.md`(lap517 middle 발행, `ESCALATE_SOL`§75).
스크립트 `temp/Syw2plus_patch/g2_capacity/20260923_lap518_work_w32_build_funnel/w32_build_funnel_run.py`
(lap516 `w31_build_pace_run.py` 복사, SHA256 `5054f3250981a198302a254aa055fd78daed9cb97283f9466920c7618b9c2b9f`).
역할: work(Sonnet5) 1회, 포그라운드 동기 실행(PROMPT③).

## 0. 실행 요약

- fixture: W29/W31과 동일(`_custom_game_chain_inject_g2_eight_ai_d4a1_seed42`, 8 owner 전원 조선(nation 1),
  자원 각 1,000,000 op7, `+0x2010`=1,200, N=4001 후보). 후보 SHA `a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68`
  (W29/W31과 byte-identical). 브리지 DLL SHA `244c13265c925d7467d778cb9e8723995709ec08b941c3054507743663cdcc9a`.
  원본 SHA 전후 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변,
  `control_executor.c` SHA 불변(`40003d06…`).
- 게임 실행 1회, tick 24,005 도달(`stop_tick_reached`), 표본 1,438개(0.5s 간격), 벽시계 ≈13분.
  `U3_pass=True`(live/count 불일치 0/1,438), `any_owner_used_over_5000=False`, `fault_or_crash=False`.
  AI/건설 로직 변경 0, 메모리 쓰기는 기존 op7 자원 fixture뿐, 원본/후보 신규 패치 0, 커밋 0.
- **N144 결정성 대조: `pass=True`, 불일치 0/8** — max_used_by_owner
  `[1708, 1035, 1583, 1536, 1513, 1070, 1406, 1376]`과 owner별 최종 건물 수
  `[17, 14, 16, 15, 15, 10, 15, 19]`가 lap516(W31)과 정확히 일치. 같은 시드/fixture/후보에서
  두 회차가 동일 궤적을 재현함을 직접 확인했다(엔진 결정성, 시딩/난수 재현성 문제 아님).

## 1. M-1 신규 필드 (기존 W31 필드는 그대로 유지)

- `+0xD32`(word, `order_kind`): 기존 0x2014B 버퍼 안, 신규 읽기 없음.
- `+0x33AC`(dword, `build_order_start_tick`): 기존 `+0x2FB8..+0x3478` EXT 버퍼 안, 신규 읽기 없음.
- `+0x3A70`(dword, `build_issue`): 버퍼 밖, owner당 4B 신규 읽기(이번 lap 유일한 신규 메모리 read).

## 2. M-2 집계 (owner 0~7, 8/8)

| owner | f_idle | S | S_exp | S/S_exp | C | C/S | B | D | B/C | 반증표본 |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.896 | 102 | 81.49 | 1.25 | 23 | 0.225 | 16 | 0 | 0.696 | 26 |
| 1 | 0.902 | 97 | 82.00 | 1.18 | 18 | 0.186 | 13 | 0 | 0.722 | 43 |
| 2 | 0.898 | 87 | 81.68 | 1.07 | 24 | 0.276 | 15 | 0 | 0.625 | 31 |
| 3 | 0.915 | 89 | 83.20 | 1.07 | 20 | 0.225 | 14 | 0 | 0.700 | 36 |
| 4 | 0.887 | 88 | 80.67 | 1.09 | 27 | 0.307 | 14 | 0 | 0.519 | 23 |
| 5 | 0.900 | 88 | 81.81 | 1.08 | 11 | 0.125 | 9 | 0 | 0.818 | 41 |
| 6 | 0.895 | 83 | 81.36 | 1.02 | 20 | 0.241 | 14 | 0 | 0.700 | 35 |
| 7 | 0.896 | 86 | 81.49 | 1.06 | 23 | 0.267 | 18 | 0 | 0.783 | 32 |

- `S`(건설 오더 시작, `+0x33AC` 값 변화): 83~102/24k. `S_exp`(카드식 `3,000×f_idle/33`) 81~83.
  `S/S_exp` 1.02~1.25 — **모두 1.3배 미만**(반증조건①은 8/8 불성립).
- `S_short_gap_defects`(연속 시작 간격 <100 tick): **8/8 owner 전원 0건** — 쿨다운 100 tick 위반 없음,
  표본 간격(≤20 tick, 실측 최대 갭 여유 확인)에서 시작 이벤트 누락 없다는 카드 전제와 정합.
- `C`(건설 명령 발부, `+0x3A70` 값 변화, 초기값 −10000 제외): 11~27/24k. `C/S` = 0.125~0.307
  (전원 <0.5 ⇒ `EXEC_FAIL_BOUND` 조건 자체는 성립).
- `B`(`+0x200E` 건물 수 순증가 합) 9~18, `D`(감소) 전원 0 — lap516 net_buildings_built와 owner별 정확히 일치.
  `B/C` = 0.519~0.818(전원 ≥0.5 ⇒ `COMPLETION_BOUND` 불성립: 발부된 명령은 대부분 건물로 이어진다).
- `f_idle` 0.887~0.915(전원 ≥0.5 ⇒ `OCCUPANCY_BOUND` 불성립: 다른 오더 점유가 병목이 아니다).

## 3. 반증조건②가 8/8 owner에서 성립 ⇒ `MODEL_REFUTED`(라벨 미부여, 원시 보고)

카드 §3 반증조건: "`+0xD32==1`이 아닌 표본에서 `+0x33AC`가 바뀌면 ... 라벨을 붙이지 말고 `MODEL_REFUTED`로
원시를 보고한다." **owner 8/8 전원에서 이 조건이 실측됐다**(위 표 "반증표본" 열, 23~43건/83~102건 시작 =
전체 시작의 **26.6%~44.3%**). 예시(owner0, tick 4639): `+0x33AC`가 4384→4624로 변했는데(새 시작), 그
표본에서 `order_kind=0`·`build_state=0`(둘 다 유휴)이 동시 관측됐다. `S_short_gap_defects=0`이므로 표본이
다음 시작을 놓친 것은 아니다 — **시작 직후 매우 짧게(다음 0.5s/≤20tick 표본 이전) 유휴로 복귀**했다는 뜻이다.

**원인은 이 카드의 범위로 미판별(재해석 금지, 카드 지시대로 라벨 미부여):**
- 가설(A) 부지/일꾼 실패로 상태1이 스케줄러 호출 내에서(≤8 tick) 즉시 종료 — SCH §2의 상태1~4
  디스패처가 동일 tick 내 여러 상태를 통과할 수 있다면 우리 표본 해상도(≤20 tick)로는 원천적으로
  포착 불가능하다.
- 가설(B) `+0xD32`/`build_state`가 이 경로에서 카드 가정과 다르게 갱신된다(SCH §2 모델 자체 결함).
- 두 가설을 가르려면 카드 범위를 넘는 고빈도 샘플링(스케줄러 주기 8 tick 이하) 또는 별도 계측이 필요하며,
  이는 이 카드가 승인한 범위가 아니다(§5 "이 카드가 허가하지 않는 것").

## 4. M-3 정적 확인 (실행 전, lap517 probe 재실행으로 대체)

`docs/history/laps/probes/20260923_lap517_middle_w31_independent_review.py` 재실행: **exit 0, 단언 16/16
PASS**, 산출 SHA `8802218b69d9a88cc7bc832e61b097e6ad8f949307b85687dd2d7bd10b54602c`(lap517 기록과 동일,
결정적). 교차 확인: `analysis/memory_maps/ai_build_order_scheduler_0043f5d0_lap517_20260923.md`가
`+0x3A70` 쓰기 정확히 3곳(초기화 `0x43ECD5`, 상태3 성공 `0x43E56C`, 상태4 성공 `0x43E78E`)과 `+0x33AC`
쓰기 정확히 2곳(초기화 `0x43ECC3`, 스케줄러 `0x43F88E`)을 이미 바이트로 확정해 두었다 — 카드 §2 M-3가
요구한 정적 재확인과 일치, 신규 정적 probe 불필요.

## 5. 승격 조건 판단

**부분 해당 — 카드가 사전 등록한 반증조건이 8/8 owner에서 실측되어 `MODEL_REFUTED`가 됐다(실패 가설
1회, 카드 상한 이내).** 이는 "예상 밖 실패"가 아니라 카드가 명시적으로 예비한 결과이므로 STOP 사유는
아니지만, **§3 EXEC_FAIL_BOUND 가설(C/S 0.125~0.307, 전원 <0.5)이 반증으로 인해 정식 라벨로 확정되지
못한다** — 즉 병목이 "실행 실패" 단계에 있다는 방향성 증거(C/S 낮음 + 반증표본 26.6~44.3%가 같은 방향을
가리킴)는 있으나 카드의 사전 판정식으로는 닫히지 않는다. 다음 middle 독립 검수가:
1. 원시 `samples.jsonl`/`build_funnel_summary.json` 비참조 재집계로 반증표본·S/C/B 수치 재현.
2. §3의 두 가설(스케줄러 8-tick 이하 초고속 실패 vs SCH 모델 결함)을 원본 바이트로 가를지, 아니면
   이 결과를 "손실 단계는 여전히 UNKNOWN, 방향성은 EXEC_FAIL"로 마감하고 카드를 닫을지 판정한다.
3. Q9(F4 실행검증 제외 범위)·Q8((ㄱ)/(ㄴ)/(ㄷ))·Q7-B는 이 lap이 고르지 않고 그대로 유지.

## 6. 산출물

- 스크립트: `temp/Syw2plus_patch/g2_capacity/20260923_lap518_work_w32_build_funnel/w32_build_funnel_run.py`
  (SHA256 `5054f3250981a198302a254aa055fd78daed9cb97283f9466920c7618b9c2b9f`)
- 원시: 같은 디렉터리의 `samples.jsonl`(SHA256 `b695365cd4416ec6a5256000327ada285bea46eef2f003a0a9bf9935f7c1a94f`,
  1,438줄), `build_funnel_summary.json`(SHA256 `e473cc4f01df0c64e7969385b1c3464bd32ca51f04d73395ec2e38b48e5c7eb9`),
  `build_pace_summary.json`(W31 필드 그대로, SHA256 `747f79ae6b6f5fb2b77711f33715f951a1818824b23f05c064914a024a982474`),
  `run_summary.json`(SHA256 `13b4ccc280a80ca7515a8e60e1c0e3cff5c9f4c9e56cb879ce3240af29778b24`), `orchestrator.log`.
- 안전 게이트: `checks/safety.sh check` → `SAFETY_PASS`. 제품 source 변경 0(동일 source, PROMPT
  2026-09-20 21:58 지시대로 784+ 전체 `make check` 재실행 면제, 직전 819 passed 유지).
