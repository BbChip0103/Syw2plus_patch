# STATUS — 매 바퀴 갱신하는 기억
## 지금 상태
활성 G1/G2/G4 제품 미완료(0/3); G3 최대16인은 2026-09-17 사용자 지시로 중단. **G2 최우선**; **2026-09-21 00:20 지시로 G1/G4는 G2 성립 전까지 잠정 중단, G3는 계속 포기 범위로 고정**. 제품 기준은 DESIGN, 사람 승인 원문은 feedback/APPROVALS·INBOX를 따른다.
과거 lap275~494 계보와 이번 압축 직전 STATUS 전문(lap491~494 상세 포함)은 `docs/history/20260923_status_lap495_precompaction.md`(SHA `2750b7fcdde9394a94d726ae06c6384c290311e7210ecf67ef159312c49022b8`, 126줄)에 그대로 있다(그 안에 이전 precompaction 스냅샷 포인터가 연쇄 보존됨).
| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | native PS3 PASS·원본구도 FAIL·제품 미완료 | 위 precompaction 스냅샷에 상세; G2 성립 전까지 잠정 중단 |
| G2 | **lap498(middle, Opus5)이 lap497 W26(144k soak)을 원시만으로 독립 재계산 = 측정 ACCEPT(불일치 0) ⇒ W26 `CLOSED`.** 종합 판정 `CAP_PROXIMITY_STABLE_144K`(부분 증거) 재현, U0~U3 전부 PASS. U4는 **UNKNOWN → (a) 호스트 페이지 회수**로 해소. **신규 N141(중대): 8 owner 전원 정지 — tick103,539 이후 40,484tick(28.1%) 동안 8인 장부·유닛 수 완전 불변, owner7은 tick2564부터 98.2% 동결. 엔진 tick은 정상 전진(리더 아티팩트 배제) ⇒ 이 soak이 잰 것은 "부하 지속"이 아니라 "정지 상태 생존"이다.** 긍정: 최종 tick144,023에 8/8 owner `used`∈[4995,5000](cap 5000의 99.9%+)을 72분51초 유지, fault·cap초과·장부불일치 0. N142: U6 3건 중 N68 동형은 owner4/7 **2건뿐**(owner2는 생산이 계속 돈 다른 현상). 제품 미완료 | lap356~495 계보는 아래 precompaction 스냅샷과 `docs/history/laps/`에. 상세는 아래 「검증 상태」 |
| G3 | 사용자 지시로 중단·활성 범위 제외 | 16 PlayerStruct가 bulk save112,036B 초과, self/opponent mask8bit라 owner8~15 표현 불가; 활성9~16/LAN 미완료 |
| G4 | 원본 issuer 국소 이동 PASS·제품 미완료 | 위 precompaction 스냅샷에 상세; G2 성립 전까지 잠정 중단 |
## 다음 한 가지
**middle 1회차 — lap448 24k 원시(712표본) 동일 재계산으로 N141 재현성 판정 + N142 owner2 분기
분류(rider).** 게임실행0·source변경0, 데이터 열기 전 판정식 사전 고정. lap499 strategy가 `ESCALATE_SOL`
§62로 Q7을 처분하며 허용한 결정-입력 분석 1회차다(그 후 사용자 응답 없으면 STOP ④6).
**Q7 처분(lap499, 사용자 번복 가능):** **Q7-B 잠정 채택** — W26 장부 상태 지속성(8/8 owner cap5000의
99.9%+/144k tick/무결성 위반0, lap498 독립 재계산 불일치0)을 **부분 증거** 라벨과 N141 한계(정지 상태
생존이지 실제 플레이 아님, 전투 축·건물 계층 미시험) 원문을 붙여 **3단 사용자 마일스톤 확인에 회부**.
**Q7-C 기각**(G2 최우선은 2026-09-17 사용자 지시라 모델이 접지 않음). **Q7-A는 모델 권한 밖** —
(ㄴ)은 사용자 전결. 단 strategy 권고: 사용자가 G2 "실제 플레이" 증거를 원하면 **(ㄴ) 승인이 유일하게
남은 기술적 진입로**다(W23 A1 + N87 + W26 §0-3 + N141).
**사용자에게 요청 중인 판정 2건:** ① Q7-A=(ㄴ) 승인 여부 ② Q7-B의 3단 마일스톤 판정(W26 부분 증거).
**(ㄴ)·lap404(가)/(나)·F4(B)/(C)·3단 사용자 마일스톤 승인은 여전히 사용자 전권 대기**, 모델 착수 금지.
## 지금 막힌 것 (Blockers)
- **F4(lap395 확정): 안전상한 UNKNOWN — 어떤 uniform cap도 랩을 막지 못한다.** donor 이전+gate-legal 재생산 펌프로 cap 1500/4095/5000 전부에서 수신 used가 32,785 도달, cap≤4095 안전상한·즉치2개 카드 착수 근거 상실. 실제 게임 도달성은 여전히 UNKNOWN. 상세는 위 precompaction 스냅샷.
- **N141(lap498 확정): fixture 내 G2 "실제 플레이" 경로가 소진됐다.** 자연도달 `NOT_FEASIBLE`(W23 A1)
  + 전투 축 기하로 생성 불가(N87) + 건물 계층 부재(W26 §0-3)에 더해, **시딩 축마저 8 owner 전원 정지로
  귀결**(tick103,539 이후 28.1% 완전 불변)됨이 실측됐다. 남은 유일한 기술적 진입로는 **(ㄴ) G2 한정
  최소 AI/설정 변경**이며 이는 2026-09-21 00:20 지시의 명시 예외 승인 사항이라 **모델이 착수할 수 없다.**
  lap499 strategy(§62)가 fixture 축 work 동결을 확정했고, 예외는 §61-끝 항1·항2의 원시 재계산
  middle 1회차뿐이다. (ㄴ) 자체는 사용자 전결 유지.
- **G2 구조통합 blocker(owner당1200 초과·저장호환 확장):** 저비용 다수 구성 확장에 필요한 Unit·보조 인덱스·bulk-relative alias·저장/LAN 일관 계약이 미구현. 현재 활성 work 경로(cap근접 시딩+장부 구성 fixture probe)와는 별도 축이며 그대로 남아 있다. 상세는 위 precompaction 스냅샷.
- G1/G4 개별 blocker(R1/S1 클릭·좌표 포렌식, AI runtime 실패 등)는 전문 그대로 위 precompaction 스냅샷과 `docs/history/laps/`에 보존되며 G2 성립 전까지 작업 대상이 아니다.
## 검증 상태
**2026-09-23 lap499(strategy, Fable5) — Q7 처분: Q7-B 잠정 채택(3단 회부)·Q7-C 기각·Q7-A 사용자 전결**
(전문 `docs/history/laps/20260923_lap499_strategy_q7_disposition.md`, 처분 원문 `loop/ESCALATE_SOL` §62).
fixture 축 G2 work 동결 확정, 예외로 §61-끝 항1(N141 재현성)·항2(N142 분류) middle 1회차만 허용.
문서 산출물만 — 게임실행0·제품 source 변경0·커밋0. INBOX는 350줄 한도라 이번 회차 무변경(Q7 원문은
STATUS·§61·§62 보유, 다음 압축 시 포인터 1줄 반영 권장).

**2026-09-23 lap498(middle, Opus5) — W26 원시 독립 재계산 = 측정 ACCEPT(불일치 0) ⇒ W26 `CLOSED`**
(전문 `docs/history/laps/20260923_lap498_middle_w26_independent_recheck.md`, 회부 `loop/ESCALATE_SOL` §61).
`run_summary.json`을 열지 않고 `samples.jsonl`(4,287행)·`events.jsonl`(6행)만으로 U0~U3·U6와 종합
판정식(N65 수리 반영)을 직접 재구현해 재계산했다. work 파생 `sum_count`는 입력으로 쓰지 않고 사후
대조만 했으며 4,287표본 전부 일치. **U0/U1/U2/U3 전부 PASS 재현**, U6 episode 3건의 enter tick·
`duration_ticks`가 `events.jsonl`과 정확 일치(누락·과잉 0), 표집 min1.0038559/max1.0755549/
mean1.0066226s 일치 ⇒ **`CAP_PROXIMITY_STABLE_144K` 재현**. 구조 무결성(owner8인 완비·필드결손0·
tick역행0·표본인덱스결손0·`cap` 전표본5000·`pid` 단일)과 F4 게이트(음수0·int16이탈0·
`count`>`count_cap`0) 전부 0 ⇒ F4는 (C) 유지.
**N141(중대):** owner별 마지막 상태변화 tick = owner7 **2,564**(98.2% 동결)·owner5 12,390·owner6
12,995·owner0 33,501·owner3 36,519·owner4 37,727·owner1 53,926·owner2 **103,539**. tick103,539 이후
40,484tick(28.1%) 동안 8인 장부·`live`(1,269) 전부 불변. **리더 아티팩트 배제** — 그 꼬리 1,208표본에서
엔진 tick 40,451 전진(표본당 mean33.5tick, N133과 정합)·`rss_kb` 470구별값 등 매 표본 갱신.
⇒ lap459 N81/N82의 owner별 완전 정지가 **시딩 축에서도 재현**. 라벨 의미는 "cap 근접 전비를 든 채
144k tick 생존"까지이며 "실제 플레이"는 보이지 않는다. **사후 재채점은 하지 않았다**(카드 §1).
**긍정:** 최종 tick144,023에 8/8 owner `used`∈[4995,5000](owner0/4/5=5000, owner2=4998, 나머지4,995)
— cap5000의 99.9%+를 72분51초 유지, fault·crash·장부불일치·cap초과 전부 0.
**N142:** U6 3건 중 N68 동형은 **owner4/owner7 2건뿐**(둘 다 `(4995,10)` 전표본·`count`154 고정).
owner2는 `(4980,23)→(4990,13)→(5000,13)×1,520`이고 `count`가 156→161 **증가** ⇒ 차단이 아니라 생산이
계속 돈 다른 현상. **N136 자연발생 입력은 2건으로 정정.** **N143(경미):** `duration_samples` 정의 2종
(exit는 배타 차, open_at_run_end는 포함 개수), 판정 무영향.
**U4 해소:** RSS 247,028KB(tick16,492)→29,828KB(tick132,770)→최종31,628KB. 급락은 임계별 −5MB **7건**/
−10MB **4건**/−20MB 2건(work "6건"은 임계 미명시). 귀속 = **(a) 호스트 페이지 회수** — ①`vm_size_kb`
4,287표본 전부 3,463,200KB 불변 ②`vm_swap_kb` 0→약130,320KB 단조증가 ③RSS ≥5MB 상승 **0건**
④최대 하강 3건이 `host_mem_available_kb` 급증(+852,508/+650,080/+2,098,696KB)과 동시.
**결정적 반증:** RSS 최소 시점 `live`=1,269 > RSS 최대 시점 `live`=1,247 ⇒ 게임측 해제로 설명 불가.
**환경 caveat:** 부하 호스트에서 돌았다(available 14.85GB→최소6.44GB).
무결성: 표적186 passed, `SAFETY_PASS`, `CONTEXT_PASS`, op4 배제 핀 3종 현존, orchestrator log의
fault/crash/error 0건, 잔류 프로세스 0, `:4977` 락 해제, 게임실행 **0**, source변경0, 커밋0.

**2026-09-23 lap497(work, Sonnet5) — W26 144k soak 완주, 종합 판정 `CAP_PROXIMITY_STABLE_144K`(부분 증거)**
(전문 `docs/history/laps/20260923_lap497_work_w26_144k_soak.md`). 실행 전 **N65 수리**(verdict 식에
`U3_pass` 추가, `PARTIAL_SOAK` 분기 신설, 예외 시에도 `run_summary.json` 항상 기록하도록 방어)를 W21
Step1 실행기 복사본에 적용한 새 실행기
(`temp/.../20260923_lap497_w26_seeded_cap_proximity_144k/w26_run.py`)로 실행.
**주요 수치:** 후보 `a10024de…`(핀 아님, 현재 source 재빌드로 확인 일치) · 원본 `b56986e0…` 실행 전/후
동일(`source_unchanged=true`) · PS3 진입 시 8인 `cap` 전부 5,000 확인 · 시딩 후 8/8 owner `used`∈[4900,4945]
(U1 PASS) · 144k soak 4,287표본, 표집간격 min1.0039s/max1.0756s/mean1.0066s · 최종 tick144,023 ·
fault/crash **0**, `used`>5000 표본 **0**(U2 PASS) · live==Σcount 4,287표본 전부 일치, 불일치**0**(U3 PASS,
N65가 이제 이 값을 종합판정에 반영) · owner0 tick283 자력 baseline 이탈 + 전run 활동 확인(U0 PASS,
"8_active") · 잔류 프로세스 **0**, 디스플레이 락 정상 해제, 커밋 **0**.
**U6(신규, 보고의무) — N136 간극에 자연발생 쪽 입력:** owner7이 `used+reserved>cap`(4995+10>5000)를
tick2564부터 **run 종료(144,023)까지 141,459tick(98.2%) 동안 자연 유지**(op4 미사용, gate-legal 시딩만),
owner4는 tick3405~30615(27,210tick, 자연 해소), owner2는 tick50743~102131(51,388tick, 자연 해소). 셋 다
`T_block`=200을 크게 초과. W28-R이 op4로 인위 재현한 차단과 동형 상태가 **인위 개입 없이도 장시간
지속됨**을 보인 1차 실측이나, 원인 기전(H-gate) 자체를 이 soak이 확인한 것은 아니다 — 다음 middle의
독립 재계산이 필요하다.
**U4(메모리 귀속)는 UNKNOWN으로 남김** — RSS가 tick16,492에서 최대247,028KB→tick132,770에서
최소29,828KB로 하강(급락 6건, 최대 −82,620KB @tick30,783), `smaps_rollup` Pss/Rss는 매 표본 기록됐으나
원인 (a)호스트 회수/(b)게임측 해제/(c)미해명 귀속 분석은 이번 lap에서 수행하지 않았다.
무결성: 표적186 passed, `SAFETY_PASS`, `CONTEXT_PASS`, op4 배제 핀 3종 현존, product source 변경0,
게임실행**1**(72분51초), 커밋0.
lap356~496 계보(lap496 middle W28-R 독립검수 = 측정ACCEPT+라벨확정`SETTLEMENT_RESUMED_AFTER_HEADROOM`
⇒ W28-R `CLOSED`, §8 3조건 충족으로 W26 카드 발행): 위 precompaction 스냅샷과 `docs/history/laps/`에.
## 바퀴 기록
lap499(strategy, Fable5) Q7 처분: **Q7-B 잠정 채택**(W26 장부 지속성을 부분 증거+N141 한계 원문으로
3단 사용자 마일스톤 회부), **Q7-C 기각**, **Q7-A=(ㄴ) 사용자 전결 유지+권고 첨부**. fixture 축 work
동결, 예외 middle 1회차(N141 재현성+N142 rider) 허용. 게임실행0·source변경0·커밋0·`SAFETY_PASS`·
`CONTEXT_PASS`. 전문 `20260923_lap499_strategy_q7_disposition.md`, 처분 `ESCALATE_SOL` §62.
lap498(middle, Opus5) W26 원시 독립검수: 측정 **ACCEPT**(불일치0) ⇒ **W26 `CLOSED`**. U0~U3 재현 PASS,
U6 3건 일치. **신규 N141(8 owner 전원 정지, 28.1% 구간 완전 불변 — 리더 아티팩트 배제)**·N142(N68
동형은 2건뿐)·N143. **U4 UNKNOWN → (a) 호스트 페이지 회수 해소.** 후속 work 카드 미발행,
`ESCALATE_SOL` §61 **Q7**으로 strategy/사용자 회부. 게임실행0·source변경0·커밋0·표적186 passed·
`SAFETY_PASS`·`CONTEXT_PASS`. 전문 `20260923_lap498_middle_w26_independent_recheck.md`.
lap497(work, Sonnet5) W26 144k soak 완주: 위 「검증 상태」와 동일 — `CAP_PROXIMITY_STABLE_144K`(부분 증거,
N65 수리 반영), U0~U3 전부 PASS, U6 신규 자연발생 관측(owner7 98.2% run 내내 미해소), U4 UNKNOWN.
게임실행1(72분51초)·source변경0·커밋0·표적186 passed·`SAFETY_PASS`·`CONTEXT_PASS`·잔류프로세스0.
전문 `20260923_lap497_work_w26_144k_soak.md`.
lap496(middle, Opus5) W28-R 독립검수: 원시만으로 측정 ACCEPT(불일치0), 라벨 확정
`SETTLEMENT_RESUMED_AFTER_HEADROOM`(strong/2tick), W28-R `CLOSED`, §8 3조건 충족으로 **W26(144k) 발행**
(`G2_SEEDED_CAP_PROXIMITY_144K_SOAK_LAP496.md`, N65 수리 의무 명기). 신규 N136~N140.
게임실행0·source변경0·커밋0·targeted186 passed·`SAFETY_PASS`·`CONTEXT_PASS`. 전문
`20260923_lap496_middle_w28r_independent_recheck.md`.
lap495(work, Sonnet5) W28-R §4 실행: R-1·R-2·R-3 반영 스크립트로 관측 610/610 완주,
resume_delay=2tick(강귀속), 정산 후 사망1건 포착(N135 회귀 확인), event_crosscheck 불일치0,
sampling_gap_violation없음, op4 정확히2콜, 무결성 위반0. work 산출 라벨은 미확정으로 남겼고
lap496이 확정했다. 게임실행1·source변경0·커밋0·targeted186 passed. 전문
`20260923_lap495_work_g2_w28r_settlement_blockage_preproof.md`.
lap356~494 계보(압축, 수치·판정 전문은 위 precompaction 스냅샷 연쇄와 각 원 lap 기록에 그대로):
lap494(middle) W28-R 발행(R-1~R-6 문언화, D1~D3 3차 재현, N135) → lap493(strategy) Q6-C 채택 →
lap492(middle) W28 원시 재계산: 측정ACCEPT·라벨확정보류(D1~D3 정정) → lap491(work) W28 §4 실행
(라벨 미확정 산출) → lap356~490(W8~W27 soak/케이던스/판정기 수리/fixture축 소거, Step A~D rider
계보 포함). 전 회차 제품코드/커밋 전부0(lap491·lap495·lap497만 게임실행1, source변경0).
