# STATUS — 매 바퀴 갱신하는 기억
## 지금 상태
활성 G1/G2/G4 제품 미완료(0/3); G3 최대16인은 2026-09-17 사용자 지시로 중단. **G2 최우선**; **2026-09-21 00:20 지시로 G1/G4는 G2 성립 전까지 잠정 중단, G3는 계속 포기 범위로 고정**. 제품 기준은 DESIGN, 사람 승인 원문은 feedback/APPROVALS·INBOX를 따른다.
과거 lap275~486 계보와 이번 압축 직전 STATUS 전문은 `docs/history/20260923_status_lap491_precompaction.md`(SHA `19d8a7af5b98becfdb46068d12654f7b77d62b172c2881971b9794872c3b0c9c`, 124줄)에 그대로 있다(그 안에 lap487 이전 precompaction 스냅샷 포인터도 연쇄 보존된다).
| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | native PS3 PASS·원본구도 FAIL·제품 미완료 | 위 precompaction 스냅샷에 상세(월드 시야 확대·HUD 원본 픽셀 크기 FAIL 등); G2 성립 전까지 잠정 중단 |
| G2 | **lap491(work, Sonnet5) W28 §4 게임 1회·동기·foreground 실행 완료**(전문 `docs/history/laps/20260923_lap491_work_g2_w28_settlement_blockage_preproof.md`). 차단을 먼저 `T_block=200tick` 이상 연속(t0=tick1414→tick1615, streak=201) 선입증한 뒤 op4 콜#2(counterfactual, `used=4980`) 발사, **+5tick 뒤(tick1620)** AND-3 전이(`reserved`10→0 ∧ `used`+10 ∧ `count`+1) 관측(귀속 강함) → tick2216까지 break 없이 관측 지속. work 산출 라벨은 **`SETTLEMENT_RESUMED_AFTER_HEADROOM`**(H-gate 지지, W27보다 강한 선입증). **lap492 middle 독립검수: 측정 ACCEPT(불일치 0)이나 라벨 확정 보류** — 콜#2 엔진tick은 **1618**이라(1615는 발사표본 tick) 완주가 **598 < 600**으로 2tick 부족, `resume_delay`는 **2tick**, tick1944 **사망 1건** 누락 오보, `used=4980`은 표본 부재(위 「검증 상태」 D1~D3). **lap493 strategy가 Q6-C 판정(§57): 라벨은 W28-R 재실행으로 재취득, 확정하지 않음. lap494 middle이
W28-R 발행(W28은 `SUPERSEDED_BY_W28R`, 재실행 금지) — D1~D3 3차 재현 ACCEPT·신규 N135.** PC predicate 히트 1건은 정상이며 판별량은 지속길이(대조군0tick vs 차단창201tick). targeted(runtime_env/eight_owner_setup/stock_stress/stock_lifecycle/official_creation) 186 passed·`SAFETY_PASS`·`CONTEXT_PASS`·op4 배제 핀 3종 현존·source변경0(원본exe·runtime_bridge.c·control_executor.c before/after SHA 일치; git은 unborn HEAD라 해당없음)·게임실행1·잔류0·커밋0. lap356~490 계보는 정확히 위 precompaction 스냅샷과 `docs/history/laps/`에. 제품 미완료(부분 증거) |
| G3 | 사용자 지시로 중단·활성 범위 제외 | 16 PlayerStruct가 bulk save112,036B 초과, self/opponent mask8bit라 owner8~15 표현 불가; 활성9~16/LAN 미완료 |
| G4 | 원본 issuer 국소 이동 PASS·제품 미완료 | 위 precompaction 스냅샷에 상세; G2 성립 전까지 잠정 중단 |
## 다음 한 가지
**work(Sonnet5/high)가 W28-R §4를 게임 1회·동기·foreground로 실행한다**
(카드 `docs/work/active/G2_SETTLEMENT_BLOCKAGE_PREPROOF_COUNTERFACTUAL_R_LAP494.md`, `READY_FOR_WORK`).
lap494 middle이 §57 R-1~R-6을 전부 문언화해 발행했다. 고치는 것은 **R-1**(완주 기준선 =
콜#2 `tick_after`, 발사표본 tick 금지, `+610` overshoot)·**R-2**(`READS`=표본∪콜 before/after 블록으로
AND-3 판정, 콜 ±10tick에서 `READS` 간격 ≤3tick 강제, `reads.jsonl` 1급 산출물)·**R-3**(분류기를
`order_open`과 분리해 창 끝까지, 정산 유닛 사후 생존 기록, `event_crosscheck`) **셋뿐**이고
파라미터·판정식·라벨은 W28과 동일(R-4, 완화 금지). **1회 한정 — 재미달 시 Q6-B 자동 종결(R-5).**
background 금지·재시도 없음·work는 라벨 확정 금지 → 다음 middle이 원시만으로 재계산해 확정.
**§8 W26(144k) 재개방은 W28-R ≥600tick 완주 + middle ACCEPT + 무결성 위반 0에 종속**(그 전 금지 유지).
**(ㄴ)·lap404(가)/(나)·F4(B)/(C)·3단 사용자 마일스톤 승인은 여전히 사용자 전권 대기**, 모델 착수 금지.
## 지금 막힌 것 (Blockers)
- **F4(lap395 확정): 안전상한 UNKNOWN — 어떤 uniform cap도 랩을 막지 못한다.** donor 이전+gate-legal 재생산 펌프로 cap 1500/4095/5000 전부에서 수신 used가 32,785 도달, cap≤4095 안전상한·즉치2개 카드 착수 근거 상실. 실제 게임 도달성은 여전히 UNKNOWN. 상세는 위 precompaction 스냅샷.
- **G2 구조통합 blocker(owner당1200 초과·저장호환 확장):** 저비용 다수 구성 확장에 필요한 Unit·보조 인덱스·bulk-relative alias·저장/LAN 일관 계약이 미구현. 현재 활성 work 경로(cap근접 시딩+장부 구성 fixture probe, W8~W28)와는 별도 축이며 그대로 남아 있다. 상세는 위 precompaction 스냅샷.
- G1/G4 개별 blocker(R1/S1 클릭·좌표 포렌식, AI runtime 실패 등)는 전문 그대로 위 precompaction 스냅샷과 `docs/history/laps/`에 보존되며 G2 성립 전까지 작업 대상이 아니다.
## 검증 상태
**2026-09-23 lap494(middle, Opus5) — D1~D3 3차 독립 재현 ACCEPT / W28-R 발행**(전문
`docs/history/laps/20260923_lap494_middle_w28r_issue.md`, 산출물
`temp/Syw2plus_patch/g2_capacity/20260923_lap494_middle_w28r_issue/`).
`run_summary`의 `verdict`/`reason`/`call2_tick`/`resume_delay_ticks`와 work 파생 보조 필드 8종을
배제하고 lap491 원시만으로 재계산: 선입증 `t0`1414→1615 201tick·75표본 전수 5중 신호·위반0,
op4 정확 2콜(콜#2 `id596`·`r7=4980`·`tick_before=tick_after=`**1618**), 마지막 표본 **2216**
⇒ 완주 **598<600**(D1), `used=4980` 표본 **0/550**·표본만 AND-3 **0건**·콜 after 블록 인정 시 1건
(지연 **2tick**)·표본 간격 min2/max**5**이고 >3tick 구간은 `1615→1620` **단 1건**(D2),
tick**1944** `count`6→5·`used`4990→4970 사망 1건 vs `death_events.json` `[]`(D3) — **전부 재현, 불일치 0.**
**결함 소재를 소스 줄까지 확정:** D1=lap491 스크립트 `:815 call2_tick = tick`(표본 tick 오용,
`:848`이 "engine tick"으로 오라벨), D2=콜이 엔진 tick 3개(1615→1618)를 소비해 **표본만으론 콜 구간
≤3tick이 물리적으로 불가능**(⇒요건을 낮추지 않고 `READS`로 검사 가능하게 정의), D3=`:694~696`의
`if order_open else "none"`이 정산 직후 R1′ 분류기 전체를 끔. **신규 N135:** 그 게이트는
`ledger_reverted_by_engine`까지 꺼서 재개 이후 **596tick 동안 무결성 채널이 무력**했다(표본 재계산이
덮어 결과는 무사하나, fail-closed 장치가 조용히 꺼진 것 자체가 결함 ⇒ W28-R R-3에서 수리).
게임실행0·source변경0·커밋0·표적**186 passed**·`SAFETY_PASS`·`CONTEXT_PASS`·op4 배제 핀 3종 현존.
**경고: 게임 실행 0이 lap492~494로 3연속** — §57이 이번 발행을 명시 허용했으나 **다음 work 회차의
게임 1회 실행은 의무**이고, 또 무실행이면 strategy가 이 목표의 계속/중단을 먼저 판정한다.
**2026-09-23 lap493(strategy, Fable5) — Q6 판정 = Q6-C 채택 / lap492 spot-check ACCEPT**(전문
`docs/history/laps/20260923_lap493_strategy_q6_disposition.md`, 판정 원문 `loop/ESCALATE_SOL` §57).
lap491 원시를 lap492 산출물 미경유로 직접 재확인: op4 정확 2콜·콜#2 `tick_before=tick_after=`**1618**
(used 4995→4980)·550표본 끝 tick2216 ⇒ 완주 **598<600**(D1), 표본 1615→1620 유일 5tick 간격·
`used=4980` 표본 부재(D2), tick1944 `count`6→5·`used`−20인데 `death_events.json` `[]`(D3) — 전부 재현.
**Q6-A 기각**(사후 완화 금지 + D2/D3 결함을 안고 144k 재개방 불가), **Q6-B 기각**(스크립트 기준선
오적용이 만든 2tick 미달로 답이 나온 실험을 영구 종결하는 비용 과대), **Q6-C 채택**(§54 "고칠 대상은
카드다" 선례). W28-R 경계 R-1~R-6은 §57에 고정: 엔진 tick 기준선 명문화 / after 블록=읽기 인정 +
콜 전후 ≤3tick 강제 / 사망 기록 수리 / 나머지 완화 금지 / 1회 한정·재미달 시 Q6-B 자동 종결 /
144k 재개방은 W28-R 완주+ACCEPT에 종속. 게임실행0·source변경0·커밋0. Fast 게이트는 회차 말 실행
(`/tmp/lap493_make_check.log`).
**2026-09-23 lap492(middle, Opus5) — W28 원시 독립 재계산: 측정 ACCEPT / 라벨 확정 보류**(전문
`docs/history/laps/20260923_lap492_middle_w28_independent_recheck.md`, 산출물
`temp/Syw2plus_patch/g2_capacity/20260923_lap492_middle_w28_independent_recheck/`).
`run_summary`의 `verdict`/`reason`/`exception`과 work 판정 로직은 물론 work가 파생한 보조 필드
(`streak_ticks`/`transition`/`order_a_finalized`/`headroom`/`phase`/`call2_fired`)까지 배제하고 원시
1차 필드+원시 콜 로그로만 재계산했다. **재현 불일치 0:** 차단 선입증 `t0`1414→1615 `streak`201tick·
75표본 전수 5중 신호·`used+reserved`는 오직 5005 / op4 정확히 2콜(히스토그램 `{7:1,6:2,1:2,0:809,4:2}`) /
AND-3 1건 `{4980,10,5}`(콜#2 after,tick1618)→`{4990,0,6}`(tick1620) / 무결성 위반 0(음수·wrap·R1′
미분류 이탈·비균형 종결 전부 0, 배열이 아니라 표본 재계산으로 확인) / PC `L`=702tick·지연3tick·분해능3tick.
**정정 3건:** **(D1, 라벨 뒤집음)** 콜#2 **엔진 tick은 1618**(원시 `tick_before=tick_after=1618`)이고
1615는 발사표본 tick일 뿐이다 ⇒ 카드 §3·§4-8이 고정한 엔진 tick 기준 완주는 2216−1618=**598 < 600**,
§5 문언상 기계 라벨은 `PRECONDITION_NOT_MET`(`observation_incomplete`), `resume_delay`는 **2tick**
(귀속 강함은 불변). **(D2)** `used=4980`은 **표본에 한 번도 없어** 표본만으로는 AND-3 0건이며,
콜#2 after 블록을 "읽기"로 포함해야 성립한다(문언 미확정). 재개가 일어난 1615→1620은 **≤3tick 표집을
위반한 유일한 5tick 구간**이다. **(D3)** tick**1944**에 `count`6→5·`used`4990→4970 **사망 1건**이
있는데 `death_events.json`이 `[]`라 lap491·STATUS·INBOX가 "사망0"으로 오보했다(§6 위반, 라벨 무영향;
`used`−20이라 죽은 개체는 정산 유닛이 아니며 정산 유닛의 사후 생존은 **미측정**).
**N132 정정:** 대조군 히트 1건은 정상이다 — 판별량은 히트 유무가 아니라 **연속 지속**이며
대조군 **0tick/1표본** vs 차단창 **201tick/75표본**으로 분리는 더 선명하다(N124 임계의 사후 정당화).
게임실행0·source변경0(`runtime_bridge.c` `2a3ad84b…`·`control_executor.c` `40003d06…`·
`runtime_env.py` `7418dcdf…`)·커밋0·표적**186 passed**·`SAFETY_PASS`·`CONTEXT_PASS`·op4 배제 핀 3종 현존.
**2026-09-23 lap491(work, Sonnet5) — W28 §4 게임 1회·동기·foreground 완주**(전문
`docs/history/laps/20260923_lap491_work_g2_w28_settlement_blockage_preproof.md`, 원시
`temp/Syw2plus_patch/g2_capacity/20260923_lap491_w28_settlement_blockage_preproof/`).
t0=producer A progress100 최초 관측 tick1414 → 5중 신호(alive∧progress100∧reserved==10∧command==15∧
미정산) 연속 스트릭이 끊기지 않고 tick1615까지 유지(streak_ticks=201 ≥ `T_block`200)되어 **차단
선입증 성립** → 그 직후 op4 콜#2(counterfactual, `used=4980`) 발사 → **+5tick 뒤 tick1620**에 AND-3
전이 관측(`reserved`10→0 ∧ `used`4980→4990(+10) ∧ `count`5→6(+1), 귀속구간 `T_attrib`50 이내 ⇒
귀속 **강함**) → 콜#2 엔진tick(1615) 기준 600tick 관측 **완주**(tick2216까지, 정산/사망에서 break
없음, N126·N130 해소 확인). work의 사전고정식(카드 §5) 기계 산출 라벨은
**`SETTLEMENT_RESUMED_AFTER_HEADROOM`**이나 **middle 원시 독립검수 전이므로 이 lap은 확정하지 않는다**
(카드 §7). PC 대조군: L=703tick, 표본tick 기준 progress100→정산 지연=3tick, 차단predicate 히트
**1건**(N132는 0건을 기대했음 — progress100 관측과 정산 사이 과도상태 1표본, 해석은 middle).
무결성: 음수·int16wrap 0, `ledger_reverted_by_engine` 0, 사망0, op4 정확히 2콜, 배제 핀 3종 실행
전/후 현존, source 변경0(원본exe·runtime_bridge.c·control_executor.c before/after SHA 각각 일치;
이 저장소는 git 커밋이 아직 없어(`unborn` HEAD) 3자 일치의 git 항목은 해당 없음). targeted
(`test_runtime_env`/`test_g2_eight_owner_setup`/`test_g2_stock_stress`/`test_g2_stock_lifecycle`/
`test_g2_official_creation`) **186 passed**(이번 회차 source 변경 0이므로 784 전체는 재실행하지
않음, 2026-09-20 21:58 지시+N22)·`SAFETY_PASS`·`CONTEXT_PASS`·잔류 프로세스0(`:199` lock 해제 확인)·
게임실행1·커밋0.
lap356~490 계보: `docs/history/20260923_status_lap491_precompaction.md`(SHA
`19d8a7af5b98becfdb46068d12654f7b77d62b172c2881971b9794872c3b0c9c`, 124줄)에 그대로 있고, 그 안에
lap480/485/487 등 이전 precompaction 스냅샷 포인터가 연쇄 보존된다.
## 바퀴 기록
lap494(middle, Opus5) §57 경계대로 **W28-R 발행 완료**(R-1~R-6 전부 문언화, W28은
`SUPERSEDED_BY_W28R`) + lap491 원시로 D1·D2·D3 3차 독립 재현(불일치 0)하고 결함 소재를 스크립트
줄까지 확정(`:815`/`:694~696`). 신규 **N135**(무결성 분류기가 정산 직후 조용히 꺼져 596tick 무력).
게임실행0·source변경0·커밋0·표적186 passed. 전문 `20260923_lap494_middle_w28r_issue.md`.
lap493(strategy, Fable5) `ESCALATE_SOL`§56 Q6 판정 = **Q6-C 채택**(W28-R 최소 재실행 1회, D1~D3 동반
수리, 경계 R-1~R-6은 §57)·Q6-A/Q6-B 기각. lap492 D1~D3를 원시 직접 spot-check로 전부 재현(ACCEPT).
1회 한정·재미달 시 Q6-B 자동 종결 선판정. 144k 재개방은 W28-R 완주+ACCEPT 종속. 사용자 전권 항목
불변. 게임실행0·source변경0·커밋0. 전문 `20260923_lap493_strategy_q6_disposition.md`.
lap492(middle, Opus5) W28 원시 독립 재계산: 측정 **ACCEPT**(재현 불일치 0) / 라벨 **확정 보류**.
정정 3건 D1(콜#2 엔진tick 1618 ⇒ 완주 598<600, 2tick 부족, `resume_delay` 2tick)·D2(`used=4980`
표본 부재 + 재개 구간만 5tick 표집)·D3(tick1944 사망 1건을 `death_events.json` `[]`로 오보).
N132 정정(판별량은 히트 유무가 아니라 지속: 대조군0tick vs 차단창201tick ⇒ 선입증 강화).
`ESCALATE_SOL`§56 **Q6(A/B/C)** strategy 회부, §8 W26 재개방 **미충족**으로 W26 미발행.
게임실행0·source변경0·커밋0·표적186 passed·`SAFETY_PASS`·`CONTEXT_PASS`. 전문
`20260923_lap492_middle_w28_independent_recheck.md`.
lap491(work, Sonnet5) W28 §4 게임 1회·동기·foreground 실행: 위 「검증 상태」와 동일 — 차단
`T_block=200tick` 선입증(tick1414→1615) 후 op4콜#2, +5tick 재개(강귀속), 600tick 완주, work 산출
라벨 `SETTLEMENT_RESUMED_AFTER_HEADROOM`(**middle 미확정**), PC predicate 히트1건(N132 상이).
게임실행1·source변경0·커밋0·targeted186 passed·`SAFETY_PASS`·`CONTEXT_PASS`. 전문
`20260923_lap491_work_g2_w28_settlement_blockage_preproof.md`.
lap356~490 계보(압축, 수치·판정 전문은 위 precompaction 스냅샷 연쇄와 각 원 lap 기록에 그대로):
lap490(middle) §54 경계대로 W28 발행 → lap489(strategy) Q4=승인·Q5=아니오 → lap488(middle) W27
원시 재검수(N127: 개입 전 체류 2tick«200, H-gate 확정 REJECT) → lap487(work) W27 실행(op4 2콜,
스크립트 버그로 자동verdict 오판) → lap486(middle) W27 발행 → lap356~485(W8~W25 soak/케이던스/
판정기 수리/fixture축 소거, Step A~D rider 계보 포함). 전 회차 제품코드/커밋 전부0(이번 lap491만
게임실행1, source변경0).
