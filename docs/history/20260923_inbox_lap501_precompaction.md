# INBOX lap471~498 W24~W28-R 계보 원문 보존 (lap501 압축, 2026-09-23)

원문 SHA256 `771f32491e8f179ef5f576df469d5c8fb4926f8d0c5143834616b0a6c3c09201` · 65줄. 삭제·재해석 없이 그대로 옮겼다.
이전 precompaction 스냅샷 포인터는 이 본문 안에 연쇄 보존돼 있다.

---

- [ ] 2026-09-22~23 lap471~496 W24~W28-R settlement-blockage 계보 **1차 종결**
  (lap496 압축 — 원문 전량 보존, 삭제 없음): lap471~495 전문은
  `docs/history/20260923_inbox_lap496_precompaction.md`(SHA
  `230e0f1b81963a46cc9a6f5cf1fb48d8b8db5bc14cf9205055ce8afcb2010a85`, 362줄, 이전 precompaction
  스냅샷 포인터는 그 안에 연쇄 보존)와 각 `docs/history/laps/20260923_lap49{1,2,3,4,5,6}_*.md`에
  그대로 있다. 요지: lap471~489 rider 종료·W25/W27 계보 → lap490 W28 발행 → lap491(work) 실행
  (라벨 미확정) → lap492(middle) 측정 ACCEPT·라벨 보류(D1~D3 정정) → lap493(strategy) Q6-C 채택 →
  lap494(middle) W28-R 발행(R-1~R-6 문언화, 신규 N135).
  **2026-09-23 lap495(work, Sonnet5):** R-1·R-2·R-3만 반영한 lap491 사본으로 게임 1회 재실행
  (source 미변경). op4 정확히 2콜, **관측 610/610 완주**, AND-3 재개 `resume_delay`=2tick(강귀속),
  정산 이후 사망 1건 포착(tick1943, N135 회귀 확인), `event_crosscheck` 불일치 0, 표집 위반 없음.
  work 산출 라벨은 **미확정**으로 남겼다(카드 §7).
  **2026-09-23 lap496(middle, Opus5) — 이 계보를 닫았다(전문
  `docs/history/laps/20260923_lap496_middle_w28r_independent_recheck.md`, 판정 `loop/ESCALATE_SOL` §59):**
  `run_summary`를 한 번도 읽지 않고 work 파생 보조 필드를 전부 제거한 뒤 원시(`reads.jsonl`/
  `window_samples.jsonl`/`events.jsonl`/`supply_probe_call_log.json`)만으로 재계산 ⇒ **측정 ACCEPT
  (재현 불일치 0)** 및 **라벨 확정 `SETTLEMENT_RESUMED_AFTER_HEADROOM`**(attribution=strong,
  `resume_delay_ticks`=2). `CALL2_ENGINE_TICK`=1610, 완주 610≥600, AND-3 1건, `t0`=1406·74표본 전수
  5중 신호, 표집 위반 0, R1′ `ledger_reverted_by_engine` 0건, `event_crosscheck` 4종 전부 일치,
  무결성(음수·wrap·라이브 `used`>cap) 전부 0. `reads.jsonl` 546건은 표본542+콜4블록의 독립 재조립과
  완전 일치. **W28-R = `CLOSED`**, §1 기전 질문의 답은 **H-gate 지지**(정산 단계가 장부 `used`를 cap에
  재검사한다). 신규 **N136**(그 기전이 N68을 그대로 설명한다 — 단 op4 desync 기반이라 자연 발생까지는
  미증명, N123 병존) · **N137**(`firing_sample_tick` 정의 2종, 판정 무영향) · **N138**(대조군 predicate
  히트 0건 ⇒ 특이도 분리가 N132보다 선명) · **N139**(정산 유닛 slot1148은 창 끝까지 생존, tick1943
  사망은 다른 유닛) · **N140**(R1′를 `READS`에 돌리면 op4 자신의 write가 위반으로 잡히는 문언 결함).
  **§8 재개방 3조건(완주 610 + middle ACCEPT + 무결성 위반 0) 전부 충족** ⇒ §57-6 위임 범위대로
  lap496이 **W26 발행**: `docs/work/active/G2_SEEDED_CAP_PROXIMITY_144K_SOAK_LAP496.md`
  (`READY_FOR_WORK`, W21 Step1과 같은 gate-legal 시딩 축, `STOP_TICK`=144,000, **op4 전면 금지**,
  N120·N121·N123·N124·N125·N126~N134·N135 미결 위험 명시 기재, `used`/`reserved` "부분 증거" 라벨 강제,
  N65 verdict 식 수리 의무, 신규 (U6) 정산 게이트 관측 의무).
  게임실행0·source변경0·커밋0·표적186 passed·`SAFETY_PASS`·`CONTEXT_PASS`.
  다음: **work(Sonnet5)가 W26을 게임 1회·foreground·동기로 실행**(벽시계 70~90분 규모, 세션 시간이
  부족하면 시작하지 않고 기록) → 다음 middle이 원시 독립검수.
  **이것은 제품 완료가 아니다** — W26도 "전투 축 미시험·시딩 fixture" 한정의 부분 증거이며,
  (ㄴ)·lap404(가)/(나)·F4(B)/(C)·3단 사용자 마일스톤 승인은 전부 사용자 전권 대기다.
  **2026-09-23 lap497(work, Sonnet5) — W26 144k soak 1회 완주(전문
  `docs/history/laps/20260923_lap497_work_w26_144k_soak.md`):** 실행 전 **N65 수리**(verdict 식에
  `U3_pass` 추가, `PARTIAL_SOAK` 분기 신설)를 적용한 새 실행기로 실행. 8/8 owner `used`∈[4900,4945]
  (U1) · 4,287표본 fault0·`used`>5000표본0·완주(U2) · live==Σcount 4,287표본 불일치0(U3) · owner0
  전run 활동 확인(U0) ⇒ **종합 판정 `CAP_PROXIMITY_STABLE_144K`**(부분 증거). **신규 (U6) 관측 —
  N136 자연발생 간극에 입력:** owner7이 `used+reserved>cap`를 op4 없이 tick2564~144023(run 끝까지
  98.2%) 자연 유지, owner4/owner2도 각 27,210/51,388tick 뒤 자연 해소 — W28-R이 인위로 만든 차단과
  동형 상태가 **개입 없이도 장시간 지속됨**을 보인 1차 실측(원인 기전까지 확인한 것은 아님).
  U4(메모리 귀속)는 원시(smaps_rollup)만 확보하고 UNKNOWN으로 남겼다. 잔류프로세스0·source변경0·
  커밋0·표적186 passed·`SAFETY_PASS`·`CONTEXT_PASS`. **독립 검수 없음** — 다음 middle이
  `run_summary.json`을 읽지 않고 `samples.jsonl`/`events.jsonl` 원시로 재계산해야 카드 §4 `CLOSED`.
  (ㄴ)·lap404(가)/(나)·F4(B)/(C)·3단 승인은 여전히 사용자 전권 대기, 이 lap이 대신 고르지 않았다.
  **2026-09-23 lap498(middle, Opus5) — W26 독립검수로 이 계보를 닫았다(전문
  `docs/history/laps/20260923_lap498_middle_w26_independent_recheck.md`, 회부 `loop/ESCALATE_SOL` §61):**
  `run_summary.json`을 열지 않고 `samples.jsonl`(4,287행)·`events.jsonl`(6행)만으로 U0~U3·U6와 종합
  판정식을 재구현해 재계산 ⇒ **측정 ACCEPT(불일치 0)**, `CAP_PROXIMITY_STABLE_144K` 재현 ⇒ **W26 `CLOSED`**.
  **U4는 `UNKNOWN` → (a) 호스트 페이지 회수로 해소**(`vm_size_kb` 전표본 불변+`vm_swap_kb` 단조증가+RSS 상승0건+host available 급증 동시; 결정적 반증=RSS 최소 시점 `live`1,269>최대 시점 1,247).
  **신규 N141(중대):** owner별 마지막 상태변화가 owner7 tick2,564 ~ owner2 tick103,539이고, **tick103,539
  이후 40,484tick(전체 28.1%) 동안 8인 장부·유닛 수가 전부 완전 불변**이었다. 그 구간에서도 엔진 tick은
  40,451 전진하고 메모리 필드는 매 표본 갱신돼 **리더 아티팩트는 배제**됐다 ⇒ 이 soak이 실측한 것은
  "부하 지속"이 아니라 **"정지 상태 생존"**이며, lap459 N81/N82의 owner별 완전 정지가 **시딩 축에서도
  재현**됐다. 다만 최종 tick144,023에 **8/8 owner가 `used`∈[4995,5000](cap5000의 99.9%+)을 72분51초 유지**
  하고 fault·cap초과·장부불일치가 전부 0인 것도 사실이다(장부 상태 지속성은 실측 지지).
  **N142:** U6 3건 중 N68 동형은 **owner4/owner7 2건뿐**(owner2는 episode 중 `count`가 156→161 증가한 다른 현상) ⇒ **N136 자연발생 입력을 3건에서 2건으로 정정**. **N143**(경미, 정의 2종).
  게임실행0·source변경0·커밋0·표적186 passed·`SAFETY_PASS`·`CONTEXT_PASS`. **lap498은 후속 work 카드를
  발행하지 않았다** — N141로 fixture 내 G2 경로가 소진돼(자연도달 `NOT_FEASIBLE`+전투 축 기하 불가 N87
  +건물 계층 부재+시딩 축 정지) 남은 진입로가 **(ㄴ)뿐인데 이는 사용자 전권**이기 때문이다.
  §61에 **Q7**(A=(ㄴ) 승인 / B=장부 지속성을 기술 충족 근거로 인정해 3단 마일스톤 확인으로 승격 /
  C=G2 현 범위 중단·우선순위 재판정)로 회부했고 **모델은 고르지 않는다.** (ㄴ)·lap404(가)/(나)·
  F4(B)/(C)·3단 승인 전부 사용자 전권 대기 불변.
