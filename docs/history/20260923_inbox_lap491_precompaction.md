# INBOX — 사용자 지시 원문과 처리 상태

체크는 문서 반영 여부이며 제품 구현 완료가 아니다. 체크된 상시 요구도 계속 유효하다.

## 처리 대기

- [ ] 2026-09-22 lap471~483 W24/W25 rider-settlement 계보 **진행 중** (lap483 압축 — 원문 전량 보존,
  삭제 없음): lap471~478은 W24 Step C rider 라인을 `RIDER_STOCK_REPRO_UNDECIDABLE_BY_FIXTURE`로
  종료(§44 하드캡 소진, H-serial 승격 반대, N111~N116). 전문은
  `docs/history/20260922_inbox_lap478_precompaction.md`(SHA
  `aaefe20d09e6555274c71f87fb75fc65d8f965287db7c007aadd5fe9ca256de2`, 384줄)와 개별
  `docs/history/laps/20260922_lap47{1,2,3,4,5,6}_*.md`·`20260922_lap478_middle_*.md`,
  `loop/ESCALATE_SOL`§43~§46에 그대로 있다.
  **lap479~481(§47~§49, lap485 압축 — 전문은 `docs/history/20260922_inbox_lap485_precompaction.md`
  SHA `1a5033eed7814239c37e482e2f1791b3c906ca0aaf06a03bc2de31212438b408` 400줄과 각 원 lap 기록에
  그대로):** lap479 strategy §46 처분(W24 CLOSED·144k 조건부 해제·W25 허용·H-serial 제외) →
  lap480 middle W25 발행+N117(§47(ii) 실행 전 도달 불가)·N118(op4만이 구성 수단) ⇒ Q1 회부 →
  lap481 strategy Q1=**D2 채택**(op4 1콜 기전 probe 한정)·카드 `READY_FOR_WORK`.
  **lap482(work) FAIL(원문 보존):** 브리지 빌드만 하고 probe를 background로 띄운 뒤 회차 종료 —
  INBOX 2026-09-21 01:01 규칙 2회째 위반(lap463과 동일 패턴). 게임 미실행·표본0. 스크립트
  (`w25_settlement_gate_probe.py`, 41,491B)는 완성 상태로 보존됨.
  **2026-09-22 lap483(work) 추기(전문 `docs/history/laps/20260922_lap483_work_*.md`):** lap482 스크립트를
  무수정 1회 실행해 §4+§8 완결(PC L=702·Order A 5중신호·op4단일콜 `used+reserved=5005>cap`), 사전고정
  판정 `PRECONDITION_NOT_MET`, tick1943 제4패턴을 재해석 없이 인계. 게임실행1·source변경0·커밋0·잔류0.
  **2026-09-22 lap484(middle) 추기:** 원시 5종 전수 재계산 ⇒ **측정 ACCEPT(불일치 0) / 해석 REJECT**.
  라벨 `PRECONDITION_NOT_MET` 유지·사유만 오귀속 정정(**N122**
  `order_terminated_without_production_at_tick1943`; 주문은 tick1943 종결, 그때 A는 hp3600 만전, 사망은
  1,109tick 뒤). **N119** 수락은 `reserved`만 올리고 `used`는 불변 ⇒ 두 계정 독립·N112 이중계상 아님.
  **N121** 대조군은 progress100과 정산이 같은 표본(≤3tick)인데 표적 arm은 529tick 체류(≥176×) 뒤
  미생산 종결·생산속도는 정상 ⇒ 이상은 **정산 단계 국소**이나 카드 임계 `5L=3510`이 과대해 신호가
  null 라벨로 떨어진 **임계 교정 결함**. **N120** 그 종결은 수락이 올린 적 없는 비용을 `used`에서 빼는
  **비균형 차감**(자연 발생 UNKNOWN). **N123 N68 미재현** ⇒ H-gate·H-place 2가설 병존. 카드 CLOSED.
  게임실행0·제품코드0·source변경0·커밋0. 전문 `docs/history/laps/20260922_lap484_middle_*.md`·§50.
  **2026-09-22 lap485(strategy, Fable5) 추기(`ESCALATE_SOL`§51):** **Q2=E2** — 144k(W26) 계속 닫음.
  조건 문언 충족은 임계 교정 결함(N121)의 산물이고 N120 미결이면 `used≤cap` 해석이 오염된다.
  재개방 조건(§47 대체)=W27 실행+middle 측정 ACCEPT+새 무결성 위반 0(발행 시 N120/N121/N123 명시·
  `used` 수치 부분증거 라벨 강제). **Q3=F1** — op4 2콜(구성+counterfactual) 기전 probe 한정 허용,
  middle이 W27 발행. 경계 R2′(정확히 2콜·핀 3종 유지·재사용 금지)·R3(counterfactual은 pending 확인
  후 progress100 +50tick 이내, 종결 시 `PRECONDITION_NOT_MET` 1회 종결)·임계 재교정(대조군
  progress100→정산 지연 기준)·사전 고정 라벨 3종. 판정 전 spot-check로 lap484 원시 7종 SHA·전이
  2건·체류 529tick·대조군 지연 0 재확인. 게임실행0·source변경0·커밋0.
  **2026-09-22 lap486(middle, Opus5) 추기(`ESCALATE_SOL`§52):** lap485 spot-check를 lap483 **원시만으로
  독립 재현 = ACCEPT(불일치0)**(원시 6종 SHA·전이 정확히 2건·op4 `{70,10}→{4995,10}`·체류 529tick·
  대조군 지연0). **W27 발행 완료**(`docs/work/active/G2_SETTLEMENT_RESUME_COUNTERFACTUAL_LAP486.md`,
  `READY_FOR_WORK`). **N124**: 대조군 지연 "0"은 표집 해상도(3~4tick) 한계값이라 §51 곱셈항이 퇴화
  ⇒ **확정 임계 `T_block=200tick`**. **N125**: 그 임계를 W25에 소급하면 tick1414~1936 79표본 전부
  stall 조건 유지·체류 522tick=임계 **2.6배** ⇒ W25 null은 정산 차단 부재가 아니라 **임계 과대의
  산물**임이 확증되어 **Q2=E2 근거 강화**. 둘 다 §51 위임 범위라 새 strategy 회부 없음.
  게임실행0·제품코드0·source변경0·커밋0·표적16 passed. 전문 `docs/history/laps/20260922_lap486_middle_*.md`.
  **2026-09-22 lap487(work, Sonnet5) 추기(전문 `docs/history/laps/20260922_lap487_work_g2_w27_settlement_resume_counterfactual.md`):**
  W27 §4를 게임 1회·동기·foreground로 완주(background 미사용). op4 정확히 2콜: 구성(`used=4995`,
  tick710) → R3 전제 5종이 progress100 최초 도달 표본(tick1408)에서 즉시 충족 → counterfactual
  (`used=4980`, **+0tick**, 50tick 창 이내). **스크립트 자체의 사후검증 코드가 버그**로 콜#2 직후
  즉시 정산 재개 가능성을 예견 못해 `RuntimeError`를 던졌고, 그 결과 `run_summary.json` 자동
  `verdict`는 **잘못** `PRECONDITION_NOT_MET`으로 기록됐다(신뢰 금지). 그러나 예외 이전 원시 필드
  (엔진 자체 `op4_call2_result` before/after + 독립 재읽기 `owner0_after_op4_call2`)만으로 카드
  AND-판정을 기계적으로 재계산(`verify_lap487.py`, run_summary의 verdict/reason 미참조)하면:
  `reserved`10→0 **그리고** `used`4980→4990(+10=주문비용) **그리고** `count`5→6(+1) — 동일
  트랜잭션 창 안에서 3조건 전부 충족 ⇒ **원시 증거는 `SETTLEMENT_RESUMED_AFTER_HEADROOM`을
  가리킨다(H-gate 지지, 정산은 headroom 회복 즉시 재개)**. targeted16 passed·`SAFETY_PASS`·
  `CONTEXT_PASS`, 게임실행1·source변경0(3자일치)·op4배제핀3종 그대로·커밋0. **이 라벨은 work가
  확정하지 않는다** — 카드 §7대로 middle 독립검수(원시만 재계산) 필요, finalization_events.json이
  같은 버그로 공백이라 middle이 원시 필드로 직접 보완 확인해야 한다.
  **2026-09-22 lap488(middle, Opus5) 추기(전문 `laps/20260922_lap488_middle_w27_independent_review.md`·§53):**
  `run_summary`의 `verdict`/`reason`/`exception`과 work의 `verify_lap487.py`를
  **읽지 않고** 원시만으로 재계산 ⇒ **측정 ACCEPT · 라벨 `SETTLEMENT_RESUMED_AFTER_HEADROOM` 확정 ·
  W27 `CLOSED`**. 단 **§5가 그 라벨에 붙인 귀결 "⇒H-gate 확정"은 채택하지 않는다.**
  **(N127)** 주문 A가 `progress==100`으로 관측된 표본은 **1건(tick1408)**뿐이고 op4 콜#2는
  tick**1410** ⇒ **개입 전 체류 2tick**으로, 카드가 스스로 확정한 임계 `T_block=200tick`(N124)의
  **1/100**이다. 게다가 대조군 progress100→정산 지연은 `run_summary`의 `1`이 아니라 **0tick**이며
  (원시 표본207 tick702가 `progress==100`·`reserved`10→0·`used`40→50·`count`3→4를 **같은 표본**에
  담는다; 스크립트가 표본tick 대신 루프 종료 후 재읽기tick 703에서 뺀 정의 결함 `w27_…py:454`),
  대조군 표집이 평균3.35/최대4tick이라 **~4tick 미만 지연은 분해 불가** ⇒ A의 2tick 미정산은 그
  맹점 안이다. **즉 "개입 전에 막혀 있었다"를 입증하는 측정이 없고 정산 재개는 H-gate와 "애초에
  안 막힘"을 구분하지 못한다. §1은 OPEN, 귀결은 "H-gate 지지(약~중)·확정 아님".** **lap487의 잘못이
  아니다** — work는 §4-6("+50tick 이내 발사")을 정확히 지켰고 결함은 **lap486이 발행한 카드 자체**다
  (+50tick 창이 정상 지연 0~4tick 앞에서 차단이 드러나기 전 개입을 강제한다).
  부수 정정: **(N126)** "동일 트랜잭션 창" 서술 **철회** — 엔진이 op4 콜#2 안에서 스스로 읽은 사후
  블록(tick1410)은 `{used4980, reserved10, count5}`로 **아직 재개 전**이고 재개는 그 뒤 별도
  `read_owner()`에서만 보이며 **그 tick은 미기록** ⇒ 재개 지연 **UNKNOWN**. **(N128)** §5 R1 승계는
  `used`의 엔진 측 이탈을 위반으로 종결시키는데 재개 라벨은 `used`가 비용만큼 **증가**하는 것이므로
  **문언상 재개 라벨이 도달 불가능**했다 ⇒ lap487의 "스크립트 버그" 서술은 **절반만 맞고** 뿌리는 카드다. **(N129)** 세 이벤트 배열 `[]`는 예외가 기록 경로를 건너뛴 결과라 **"사건 0건"이
  아니다**(§6 N120 의무 post-call2 미이행). **(N130)** `call2_fired=true` 표본 **0건** ⇒ §4-7의
  ≥600tick 관측 미실행, 개입 후 주장은 **tick 미상의 단일 재읽기 1건**에 의존, `NO_RESUME_WITHIN_WINDOW`
  평가 불가 ⇒ **§4는 1~6단계까지만 실행됐다.** 무결성 위반 **0**·R2′(477콜 중 op4 정확히 2콜)·
  R3 전제 5종·A 260표본 전부 생존·source 3자 불변·핀 3종 현존·표적 16 passed·`SAFETY_PASS`·
  `CONTEXT_PASS`·잔류0·게임실행0·제품코드0·source변경0·커밋0·새 카드 발행 0.
  다음: **strategy(Astra/Fable5)가 §53 Q4(교정 counterfactual W28 재승인 — 발사 조건을 "차단
  ≥`T_block` 선입증 직후"로 교체·R1 정정·재읽기 tick 기록+≥600tick 관측 완주)와 Q5(§8의 "W27
  실행"이 7단계 미실행으로도 충족되는가 ⇒ 예면 middle이 즉시 W26/144k 발행)를 판정한다.**
  **2026-09-22 lap489(strategy, Fable5) 추기(`ESCALATE_SOL`§54):** 판정 전 spot-check로 lap488의
  결정적 원시 사실을 lap487 원시에서 독립 재현(불일치 0 — progress100 window 표본 1건 tick1408·
  `call2_fired=true` 0건·op4 정확히 2콜·콜#2 사후블록 tick1410 재개 전·재개는 tick 미상 재읽기뿐·
  대조군 표본207 지연 0). **Q4=승인** — middle이 **W28** 1장 발행(op4 정확히 2콜 재허용). §53 교정
  3건 의무(차단 `T_block=200tick` 선입증 후 발사·R1을 "비용+10 이외 이탈만"으로 정정·재읽기 tick
  기록+발사 시 ≥600tick 관측 완주) + 추가 2건(이벤트 증분 기록으로 N129 해소·대조군 지연 정의를
  표본 tick 기준으로 수리). 차단 미재현이면 `no_blockage_ge_t_block_observed` 1회 종결·재시도 없음.
  **Q5=아니오** — "W27 실행"은 §4 1~6단계뿐(N130)이라 §8 미충족, 144k 계속 닫음. **재개방 조건을
  대체**: W28 완결 1회 종결(발사 시 7단계 완주 포함) + middle 측정 ACCEPT + 무결성 위반 0이면
  라벨 무관 W26 발행 가능(N120~N130 명시·`used` "부분 증거" 라벨 강제 유지). lap488·489 연속
  무실행이므로 다음 회차는 middle W28 발행 1회만, 그 다음 work는 게임 1회 실행 필수. 게임실행0·
  source변경0·커밋0. 전문 `docs/history/laps/20260922_lap489_strategy_g2_q4_q5_disposition.md`.
  **2026-09-23 lap490(middle, Opus5) 추기(`ESCALATE_SOL`§55, 전문
  `docs/history/laps/20260923_lap490_middle_g2_w28_issue.md`):** §54 경계대로 **W28 발행 1회 완료**
  (`docs/work/active/G2_SETTLEMENT_BLOCKAGE_PREPROOF_COUNTERFACTUAL_LAP490.md`, `READY_FOR_WORK`).
  발행 전 lap483/487 **원시만으로 독립 재현 = 측정 ACCEPT** (lap483 전이 정확히 2건·체류 529tick·
  79표본 5중 신호 / lap487 progress100 1건·`call2_fired` 0건·op4 정확히 2콜·대조군 표본 tick 기준
  지연 0). **정정 N131(판정 무영향)**: §54의 "콜#2 엔진 사후블록 `{4995,10,5}`"는 원시 **before**이고
  after는 `{4980,10,5}`(둘 다 재개 전). 교정 5건 문언화(선입증 발사·**R1′**로 재개 신호를 위반에서
  제외·모든 재읽기 tick 기록+콜#2 엔진 tick 기준 ≥600tick 관측 완주·표본마다 append+flush 증분
  기록·대조군 지연 표본 tick 정의+≤3tick 표집) + 지평 `t0+700tick`·`T_attrib=50tick`·사유 사전 표.
  신규 **N132**(대조군 차단 predicate 0/208 = 특이도 지지)·**N133**(33tick/s ⇒ 완주 비용 ~0, lap483
  종결은 발사 +329tick 뒤라 break 금지)·**N134**(`progress==100` 단독은 계류 신호 아님).
  게임실행0·제품코드0·source변경0·커밋0·표적16 passed·핀3종 현존. **lap488·489·490 연속 무실행이므로
  다음 work 회차의 게임 1회 실행은 의무**이며, 또 무실행이면 strategy가 계속/중단을 먼저 판정한다.
  **압축 직전 INBOX 전체 원문**은 `docs/history/20260922_inbox_lap483_precompaction.md`(SHA
  `e1b394e68e51a14e2bb76e7c5ae2d86c0ad894164b3cb75a5f9e490e4b7e1e11`, 400줄, 이전 precompaction
  스냅샷 포인터는 그 안에 그대로 있다)에 보존했다.
  **기록/런타임 lap 번호 주의:** `.lap_counter`·러너 로그 기준 lap476은 runtime lap477(기록 계열이
  1 뒤처져 lap477 파일은 없다). 과거 명칭은 고치지 않는다.

- [ ] lap469~471 계보 (lap472 압축·lap486 재압축 — 원문 전량 보존, 삭제 없음): lap469(work) Step C
  3회차 `RIDER_NO_REPRO` → lap470(middle) **REJECT(`STEP_C_PRECONDITION_NOT_MET`)**(N98~N104) →
  lap471(work) 4회차는 §42-6의 4가지를 구현해 전제를 처음 성립시켰으나 주문이 창 2,106tick 내내
  `reserved=0`이라 4번째 상태 **`RIDER_ORDER_NOT_ACCEPTED`**로 종료(1차 discriminator 결함은 work가
  직접 정정, 원문 `attempt1_stale_progress_false_positive/`) → lap472 독립검수.
  전문은 `docs/history/20260922_inbox_lap472_precompaction.md`(SHA `87ac134e…`, 390줄)·
  `20260922_inbox_lap486_precompaction.md`(SHA `f1054f35…`, 404줄)와 각
  `docs/history/laps/20260922_lap4{69,70,71}_*.md`(`ESCALATE_SOL`§42·§43)에 그대로 있다.
  **lap465~467 원문**은 `docs/history/20260922_inbox_lap469_precompaction.md`
  (SHA `02fa663c…`, 393줄)와 각 `docs/history/laps/20260922_lap46{5,6,7}_*.md`에 그대로 있다.

- [ ] lap462~465 계보 (lap466 압축·lap485 재압축 — 원문 전량 보존, 삭제 없음): Step A
  `BUILDING_SEEDABLE`+Step B 수리 → lap463 background 방치 FAIL(01:01 규칙 위반)+N90 →
  lap464 N90 수리+Step D `NO_ENGAGEMENT` → lap465(middle) Step D **ACCEPT**·Step C **VOID**
  (N91~N95) → lap466이 Step C 결손 해소. 전문은
  `docs/history/20260922_inbox_lap466_precompaction.md`(SHA `5b92adeea252861e1ffbe7314475c4de6d2c7619d72e775256154f2a8c1a9f68`, 396줄)·
  `docs/history/20260922_inbox_lap485_precompaction.md`(400줄)와
  `docs/history/laps/20260921_lap462_*.md`·`20260922_lap46{3,4,5}_*.md`에 그대로 있다.

- [ ] 2026-09-21 01:10 KST 운영 회수 — W10 P-A 실제 완료. lap415 입력의 PID 원인 서술은
  **정정**한다: PID는 맞았고 최초 PE mapping 전 일시 `EFAULT`를 retry하지 않은 것이 원인이었다.
  lap416 probe 수정본을 root 소유 동기 세션에서 새 run2로 실행해 709표본/동일 tick11,928 정지를
  재현했다. fault 직전 생존 high-slot **3565/type76/owner4**의 `+0x692`가 tick11,921에서 -6599,
  tick11,928에서 19579로 폭증했고 low band 이상은 0이다. 따라서 카드 P-A의 **H1 지지** 조건을
  충족한다. 증거 `temp/Syw2plus_patch/g2_capacity/20260921_lap416_fault_root_cause_pa_run2/`;
  후보 SHA `4331d9cd…`, 원본 전후 `b56986e0…`, 709 lines, `SAFETY_PASS`, 잔류0. 다음 work는
  W10 P-B의 1200-bound 전수 인벤토리와 이 손상을 만드는 단일 site를 좁힌 뒤 P-C 최소 수리한다.

- [ ] 2026-09-21 01:01 KST 운영 규칙: loop agent가 장시간 Wine probe를 셸 background로 띄운 뒤
  회차를 종료하면 loop cleanup이 자식도 정리해 실행이 지속되지 않는다. 장기 probe는 모델 세션이
  직접 기다리거나 root가 소유한 exec 세션으로 실행·회수한다. “background 실행 중” 문구만으로
  활성 프로세스를 주장하지 않고 PID/산출물 갱신을 확인한다.

- [ ] 2026-09-21 00:51 KST 운영 회수: lap415 W10 P-A probe는 실제 샘플링에 진입하지 못했다.
  `movement_state_probe.py`가 `subprocess.Popen(["wine", ...]).pid`인 Wine 런처 PID 2435667을
  게임 내부 PID로 사용해 PS 주소 `0x4ED818` read가 `EFAULT`로 종료됐고 `samples.jsonl`은 0B다.
  게임 후보 실패나 H1/H2 판정으로 세지 않는다. 산출물은
  `temp/Syw2plus_patch/g2_capacity/20260921_lap415_fault_root_cause_pa/`에 보존됐다. 다음 work는
  기존 `tools.runtime_env`/`runtime_driver`의 검증된 Windows game PID 발견 방식을 재사용해 같은
  P-A를 재실행한다. 새 독자 PID 추측을 추가하지 않는다.

- [ ] 2026-09-21 00:20 KST: 사용자 목표 우선순위 확정. **G2(8인 각각 전비 5000 안정 플레이)가
  성립하기 전까지 G1(1600×1200 원본 구성)과 G4(AI/길찾기 개선)는 잠정 중단**한다. G3(최대
  16인)는 잠정 중단이 아니라 **계속 포기한 범위**로 고정한다. 현재 lap414의 G2 독립 검수는
  이 지시와 일치하므로 중단하지 않으며, 이후 루프도 G2의 직접 조사·수리·실행검증 외 목표로
  전환하지 않는다.

- [ ] 2026-09-20 21:58 KST: 사용자 “아니 뭐 이렇게 굼떠”. 같은 소스에 대해 784개 전체
  `make check`를 회차마다 반복해 실제 게임 실행을 늦추지 않는다. 직전 동일 source의 full gate가
  PASS이면 다음 독립 검수는 원시 산출물·표적 테스트·원본/안전검사만 수행하고 제품 런타임으로
  즉시 이동한다. 전체 gate는 소스 변경 뒤 통합 경계에서 한 번만 실행한다.
  **2026-09-20 lap410 적용(상시 규칙이라 체크는 두지 않음):** 이 지시를 처음 적용했다. lap410은 동일
  source·직전 full gate PASS이므로 784 `make check`를 재실행하지 않고 원시 산출물 재계산 + 표적 테스트
  (`test_g2_full_capacity_persistence_compat_v1.py` 5 passed) + 원본 해시 + `checks/safety.sh check`만
  수행했다. 발행한 다음 카드 W8에도 §6으로 같은 규칙을 박아 두었다.
  **2026-09-20 lap412 오적용 정정(N22):** 이 규칙은 "동일 source일 때 면제"이지 "항상 면제"가 아니다.
  lap411은 스스로 `patches/population/runtime_driver.py`(`control_goal_payload`)와 신규 테스트
  `tests/test_runtime_env.py::test_runtime_driver_control_goal_uses_protocol_string_request_id`를
  추가해 **source를 바꿨는데도** "동일 source"를 근거로 전체 gate를 건너뛰었다. 규칙 후단
  "전체 gate는 소스 변경 뒤 통합 경계에서 한 번만 실행한다"가 걸리는 경우였다. lap412 middle이
  그 통합 경계 gate를 대신 실행했다(collected **785** = 784+신규1). **규칙 자체는 유효하며 변경 없다** —
  앞으로 면제를 주장하는 회차는 "이번 회차에 source를 바꾸지 않았다"를 함께 적는다.

- [ ] 2026-09-20 00:33 KST: 사용자 "그래 그 1200을 늘릴 수는 없냐고" 이후 "ㄱㄱ".
  G2의 즉시 최우선 작업을 전비 장부 단독 조사에서 **전역 UnitStruct 풀 1,200칸 확장 실행
  스파이크**로 전환한다. 첫 성공 기준은 격리된 실제 게임에서 slot index **1,200 이상** 개체를
  정상 생성하고, 기존 reader로 관측한 뒤 사망·슬롯 재사용까지 증명하는 것이다. 단순 `0x4B0`
  상수 변경이나 다음 상태영역 덮어쓰기는 금지한다. 새 풀/보조배열 주소 재배치와 참조 fixup을
  최소 범위로 구현하고, 실패 가설 2회 또는 60분 안에 `FEASIBLE`/`NOT_FEASIBLE`/`BLOCKED`로
  판정한다. 저장/LAN은 이 첫 스파이크의 PASS 조건이 아니지만 후속 필수 blocker로 명시한다.
  2026-09-20 lap396 전비 probe는 이 최신 우선순위에 따라 안전 종료(exit143, safety ok)했다.
  2026-09-20 lap397 middle이 정적 표면을 측정해 최소 변경 범위를 확정하고 즉시 실행 가능한
  work 카드 `docs/work/active/G2_UNIT_POOL_EXPANSION_SPIKE_LAP397.md`(W3)로 인계했다.
  건드릴 것은 재배치3영역(pool/existence/age)+상수4개+fixup1,016건뿐이며 active/catA/catB·
  PlayerStruct roster·`0x892410` 별칭179건은 불필요함을 바이트로 확인했다. 제자리 확장은
  `NOT_FEASIBLE`(풀이 bulk에 밀착·age뒤 구멍 참조9건), 재배치 경로는 구조적으로 `FEASIBLE`.
  lap399 후보는 lap400이 REJECT(제자리 성장), lap401 work가 꼬리 재배치를 구현, lap402 middle이
  독립 검수해 **재배치·fixup·패처 수리는 ACCEPT**하되 **후보 기동은 REJECT**했다 — 재배치 블록의
  99.24%가 어떤 PE 섹션에도 매핑되지 않는 신규 결함(D1, `.data` VirtualSize 산출 한 줄). 수리 카드는
  `docs/work/active/G2_POOL_SECTION_COVERAGE_REPAIR_LAP402.md`(W5).
  lap406 middle이 자칭 lap410/412 런타임 계보를 2단 검수해 항목1/2/4/5 ACCEPT·항목3(커버리지
  앵커)만 게이트 추가 지시(W6)했고, lap408 middle이 그 W6 게이트 2건을 독립 검수해 **CLOSED**
  했다(`make check` 783 passed=779+4, 역주입으로 D1 계열 포착 확인, 원본·pin 불변). lap408은
  같은 계열의 남은 사각 하나를 W7 `G2_RSRC_WRAPPER_CONTAINMENT_GATE_LAP408.md`로 발행했다
  (`.rsrc` cave wrapper 4건에 컨테인먼트 앵커 없음, 마지막 `LEGACY_COPY` 여유 49B).
  **아직 실제 게임 실행 증거가 없으므로 제품 구현 완료가 아니다** — 체크는 그대로 둔다.
  다음 회차는 W7 뒤 **즉시 P1(near-4000 live 실제 실행)** 이며, 이 첫 성공 기준(slot≥1200
  생성→관측→사망→재사용)의 독립 재현은 여전히 미검증이다.
  **2026-09-20 lap409 work 추기(원문 위는 보존):** W7 앵커 완료 뒤 P1을 착수해 marked compat
  (`4331d9cd…`) 후보로 격리 Wine에서 near-4000(3,991 live, 8owner) 규모 gate-legal 시딩→마킹저장
  (마커 `S2P1N4K1` 파일 오프셋 `0x38` 확인)→마킹로드 왕복을 슬롯 단위로 무손실 확인(소실0·id불일치0).
  slot≥1200 생성→관측→재사용 자체는 이 lap 이전에 이미 실측됐고(seed 시 slot 3977 등 관측),
  이번 lap이 새로 더한 것은 **marked compat 저장/로드가 near-4000에서 실제로 무손실**이라는 증거다.
  **이번 lap은 work 역할의 자기 결과이며 독립(다음 middle) 검수는 아직 없다.** 상세
  `docs/history/laps/20260920_lap409_work_g2_p1_compat_near4000_live_execution.md`.
  **2026-09-20 lap410 middle 추기(위 원문 보존):** lap409 P1을 원시 산출물 재계산으로 독립 검수해
  **ACCEPT**했다(후보 재현·save 해시/마커·스냅샷 diff·receipts·브리지 4001 소스·표적 5 passed·
  `SAFETY_PASS`·원본 불변). 위 21:58 지시에 따라 전체 784 게이트는 재실행하지 않았다(동일 source).
  **신규 근거:** `trace.jsonl`의 tick **2328→1567 역행**이 로드가 실제로 엔진 상태를 교체했음을 직접
  증명한다 — 이것이 없으면 "소실0"은 로드가 아무 일도 안 한 경우와 구분되지 않는다.
  **정정1:** presave 스냅샷이 저장 시점보다 ~535 tick 앞서므로 "5기는 로드 후 생산"은 사실과 다르다.
  4기는 저장 이전 생산(세이브에 포함), 로드 후 생산은 1기. 카운트는 저장 3,995→로드 3,995로 정확
  일치하나 id 단위 검증 범위는 3,995 중 3,991기다.
  **정정2(신규 결함):** 배포 진단 DLL의 `inmm_stub.c`/`ai_shadow.c`/`sfx_hook.c`/`control_executor.c`가
  stock 유닛 존재배열 `0x008990C8`과 1200 경계를 하드코딩해, 재배치 후보에서 유닛을 0기로 관측한다
  (`C:\inmm_unit_ticks.jsonl`이 3,991기 생존 중 0바이트로 실증). 전부 읽기 전용이라 손상 위험은 없고
  P1 판정에도 영향이 없으나, 향후 lap이 이 채널을 근거로 "전멸"을 오판할 위험이 있다.
  **여전히 제품 구현 완료가 아니다** — 단발 왕복 1회이며 장시간 안정성·원본 생산 경로·LAN 미검증.
  다음 회차는 work 카드 `docs/work/active/G2_COMPAT_LONG_SOAK_LAP410.md`(W8, compat 장시간 soak)다.
  상세 `docs/history/laps/20260920_lap410_middle_g2_p1_independent_review.md`.
  **2026-09-21 lap413~414 추기(위 원문 보존):** W8은 lap411 실행·lap412 ACCEPT로 닫혔고, lap413이 W9(P2,
  원본 생산 명령으로 near-cap 도달)를 실행해 **FAIL**했다 — 자원만 공급(op7)한 8인 AI 대전에서 N=4001
  후보가 **두 번 모두 tick 11,928에서 `read 0x00338400 @ 0x00414133` page fault**로 죽었고, stock-layout
  대조군은 같은 tick을 fault 없이 통과했다. lap414 middle이 요약본을 쓰지 않고 원시 산출물만으로
  재계산해 그 FAIL을 **ACCEPT**하고, fault 기전을 바이트로 확정했다(100칸 stack 배열을
  `((경로점수-1)×|유닛 이동진행도 +0x692|)/100`로 인덱싱하며, 그 명령 바이트는 원본과 동일).
  또 후보가 `.text`의 1200 즉치 54곳 중 **2곳만** 4001로 바꿨고 풀을 순회하는 잔존 1200-bound site가
  최소 3곳 남아 있음을 확인했다. **이 첫 성공 기준(slot≥1200 생성→관측→사망→재사용)은 진단 시딩으로는
  충족됐지만 원본 생산·AI 전투 경로의 안정성은 여전히 미충족이므로 체크는 그대로 둔다.**
  다음 회차는 `docs/work/active/G2_POOL_SCOPE_1200_FAULT_ROOT_CAUSE_LAP414.md`(W10)다.

- [x] 2026-09-17 12:23 KST: "일단 그 세 부분 가능 여부를 더 확실하게 알아봐". G1/G2/G4 핵심 blocker를 구별하는 제한 실행 조사; G3 재개 없음. 계측 실패를 전체 목표 불가능으로 치환하지 않는다. 세 bounded 실행카드 종료·Sol검수 리포트 `docs/reports/20260917_THREE_GOAL_FEASIBILITY_UPDATE.md` 작성; 목표완료 아님.

- [ ] 2026-09-15 11:46 KST: "조금 조사한 뒤 안 될 것 같으면 빠르게 불가능하다고 보고하고,
  될 것 같으면 빠르게 작업에 착수"한다. 조사와 문서 자체를 목표로 삼지 않는다. 각 핵심 분기는
  짧은 feasibility 판정(`FEASIBLE`/`NOT_FEASIBLE`/`BLOCKED`)으로 끝내고, `FEASIBLE`이면 다음 work
  회차부터 구현·실행 증거를 만든다. `NOT_FEASIBLE`/`BLOCKED`이면 추측성 반복 대신 근거·대안·영향을
  사용자에게 즉시 보고한다.

- [ ] 2026-09-15 11:35 KST: "대목표 4개 중 완료 0개인데 왜 진행 속도가 이렇게 느린가".
  제품 구현보다 해시·스냅샷·시간경계 등 증거 하네스 자체 보수에 과도하게 머문 운영을 교정한다.
  Astra가 큰 방향을 재판단해 G1의 남은 실제 제품 판정을 최단 경로로 닫고, 독립 파일의 G2 구조
  조사를 함께 활성화한다. 이미 충분한 안전 근거가 있는 항목을 반복 검수하지 말고, 새 제품 증거를
  만드는 작업을 우선한다. 정확성·원본 보호·저장/메모리 안전은 계속 타협하지 않는다.

- [ ] 2026-09-10 23:06 KST: 실제 루프 시작. 10분마다 한국 시간과 함께 진행상황 보고.
  Astra/high 상위 전략 → Sol/high 중간 계획·컨펌 → Luna/high 실무 순으로 명시적 1바퀴씩 진행한다.
  자동 서비스/무한 실행/자동 커밋·푸시는 사용하지 않는다.

## 처리 완료

- [x] **2026-09-22 lap487 압축:** 이 섹션의 체크 완료 항목 전량(목표1~4 원문, 모델 역할, 환경세팅, 구조 이관, G3 중단 리포트, astra→fable 전환 2건)은 `docs/history/20260922_inbox_completed_section_lap487_archive.md`(SHA256 `ce6f8daeeda7f235d199dec62350614d2f2458b7ff2a8bd7b678b1eb7e1f8b90`, 34줄)에 **원문 그대로** 보존했다. 삭제 없음. 체크된 상시 요구는 계속 유효하며, 재참조가 필요하면 그 파일을 읽는다.

## 되물음

- [ ] 2026-09-20 lap404 strategy — **일시적 전비 초과 표시 허용 여부.** 8인 5000 144k 실측에서
  라이브 유닛 전비는 5000을 넘지 않았으나, 생산 완료 직전 한 tick 창에서 `used+reserved=5010`
  같은 일시 pending 초과가 원본 1200-slot 대조군에서도 동일하게 관측됐다(원본 고유 동작).
  (가) 이 일시 초과를 허용하고 "라이브 used ≤5000"만 강제, (나) pending 포함 strict 5000 강제
  (원본 생산/예약 순서 변경 필요, 위험). 권고는 (가).
  - **2026-09-20 lap406 middle 정정 N19(위 원문은 고치지 않고 보존):** 144k 원시 로그를
    owner별로 재계산하니 **"한 tick 창"이 아니다.** 초과 owner-표본 216건이고 값은 전부
    정확히 `used=5000, reserved=10`이며, owner6은 tick **33917→50130**(16,213 tick·97표본),
    owner5는 tick **101643→121547**(19,904 tick·119표본) 동안 **지속**됐다. 즉 (가)를 고르면
    총합 5010 표시를 owner당 **수 분(약 490초·600초)** 허용하게 된다. 라이브 `used`가 cap을
    넘은 표본은 전 soak 통틀어 0건이라는 부분만 원문대로 참이다.
  - **미증명 귀속:** "원본 1200-slot 대조군에서도 동일하게 관측됐다"를 뒷받침하는 산출물은
    이 계보에 없다 — 같은 계보 stock 대조군은 cap 1500에 max used 40, 초과 표본 0건이라
    cap 근처에 가지 않았다. 파일로 남은 유일한 stock 초과 증거는 2026-09-17
    `stock_cap_overshoot_audit_v1`의 **라이브 `used`=5003(owner1, 7표본, 원인 UNKNOWN)** 으로
    pending reservation과 **다른 현상**이다. 근거는
    `docs/history/laps/20260920_lap406_middle_g2_full_capacity_runtime_review.md`.
  - **2026-09-20 lap412 middle 기전 확정(위 원문 보존, 선택지 문구 정정 필요):** lap411 24k soak의
    owner별 시계열을 재계산하니 **"일시 초과"도 "수 분 지속"도 아니다 — 해소되지 않는 예약이다.**
    owner7은 728 PS3 표본 중 726에서 `reserved=10`이고, tick 158~24,298(전 soak의 **99.45%**)
    동안 `used=5000, reserved=10`으로 고정됐다. owner7은 24k tick 내내 유닛을 한 기도 잃지 않아
    `count`가 500에서 불변이었다. 반대로 owner3은 사망으로 `used`가 내려가면 예약이 해소됐고
    (`reserved=0` 111표본), `used<5000`일 때의 `reserved=10`은 합이 cap 이하라 초과가 아니었다.
    ⇒ 실체는 **비용 10짜리 생산 주문 1건이 큐에 걸린 상태이며 `used`가 cap 아래로 내려가야만
    해소된다.** 따라서 선택지 (가)는 "일시 초과 허용"이 아니라 **"cap에 붙은 owner가 대기 주문
    1건을 무기한 보유하는 것을 허용"** 으로 다시 읽어야 한다. 관측 범위에서 해악은 0이다
    (크래시·풀 손상·라이브 `used` cap 초과 전부 0건 / 5,824 owner-표본).
    **귀속은 여전히 미증명**이고, 다음 work 회차가 P2와 **같은 회차에** 값싼 결판 probe를 넣는다:
    stock 원본을 cap 5000으로 띄워 한 owner를 `used=5000`까지 채우고 생산 주문 1건을 건 뒤
    `reserved`를 본다. stock에서도 `5000+10`이 나오면 (가) 확정, 안 나오면 후보 고유 회귀로
    승격해 P3를 앞당긴다. 근거 `docs/history/laps/20260920_lap412_middle_g2_w8_soak_independent_review.md`.
  - **2026-09-21 lap449 middle 신규 증거 N68(위 원문 전부 보존, 선택지 미변경):** lap412가 확정한
    기전이 **수리된 신후보(`a10024de…`)·cap 근접·24k soak에서도 그대로 재현**됐다. lap448 Step1
    원시 712표본 재계산 결과 `used+reserved>5000`인 owner-표본이 **1,263건**이고 값은 **전부
    정확히 `(used 4995, reserved 10)`**, 해당 owner는 **owner4(619표본)와 owner7(644표본)
    둘뿐**이며 **마지막 표본까지 해소되지 않았다**. 라이브 `used`가 5000을 넘은 표본은
    **0건**(8 owner × 712표본 전부). ⇒ 8인 중 **2인**이 24k 내내 대기 주문 1건을 보유했고,
    나머지 6인 중 3인(owner0/2/5)은 `used`가 정확히 5000에 도달했다.
    관측 범위에서 해악은 여전히 0(크래시·풀 손상·라이브 cap 초과 전부 0).
    **여전히 사용자 판단 대기 항목이며 모델이 대신 고르지 않는다.**
    근거 `docs/history/laps/20260921_lap449_middle_g2_w21_step1_independent_review.md`.
- [ ] 2026-09-20 lap404 strategy — **전비 장부 16-bit 랩 위험의 마감 방식.** 이전(transfer)으로
  한 owner에 전역 전비를 집중시키면 signed16 장부가 랩될 수 있음이 산술로 남아 있다(게임 내
  도달성은 미실측). (B) 장부 32-bit 확장(저장포맷 동반, 큰 작업), (C) 도달성 실측 후 실제 불가면
  5000 유지(작은 작업, 단 실측로 랩이 재현되면 B로 회귀). 권고는 (C) 선행.
- [ ] 2026-09-21 lap458 work — **W23 A1 24k 연장 결과 `DECAYED` ⇒ (가) 자연 도달은 fixture/config
  축에서 NOT_FEASIBLE 확정.** 카드 `G2_A1_MAP_LEVER_LONG_WINDOW_LAP457.md` §4 고정 판정식대로
  W22 최유망 레버 A1(지도140×140)을 tick24,000까지 연장 실행한 결과, `r_late`(owner1,
  16k→24k)=0.008747 < `r_need`=0.033042(=(5000−U_min24 1,035)/120,000) ⇒ `DECAYED`.
  `U_min8`=661(owner5)로 W22 결정성 재확인, 무결성 위반 전부 0, 게임실행1회·source변경0·
  targeted7 passed·`SAFETY_PASS`. 카드가 예약한 대로 **모델은 AI/경로/생산 로직 변경에
  착수하지 않았고** 아래 되물음을 그대로 승격한다(고르지 않음, `G2_NATURAL_ARRIVAL_FIXTURE_LEVER_PROBE_LAP455.md`
  §7 · `loop/ESCALATE_SOL` §36):
  - **(ㄱ)** 시딩 기반 cap 근접 + 왕복 증거(W21)를 G2 안정성 증거 축으로 인정하고 (가)를 재정의할지.
  - **(ㄴ)** G2 한정 최소 AI/설정 변경 허용 — 2026-09-21 00:20 G4 잠정 중단의 명시 예외 승인 여부.
  - **(ㄷ)** 현재 기준(자연 도달 요구) 유지, (가) 보류.
  이 3건은 바로 위 lap404 되물음(전비 장부 16-bit 랩 마감 방식)과 함께 사용자/strategy 판정
  대기 상태다. 상세 `docs/history/laps/20260921_lap458_work_g2_w23_a1_long_window_decayed.md`.
  - **2026-09-21 lap459 middle 독립검수 = ACCEPT(재계산 불일치 0)**, 위 원문 유지·선택지 미변경.
    원시 721표본만으로 비참조 재계산해 `U_min24`=1,035(owner1, tick24,012)·`r_late`=0.008747·
    `r_need`=0.033042·`DECAYED` 전부 일치, `U_min8`=661/owner5로 W22 결정성 정확 재현, 실행 **전**
    고정 기대 band 1,050~1,073 대비 실측 1,035(−1.4%).
    **판정 방향에 영향을 줄 신규 실측:** **(N81)** 정체 원인은 자원·cap·풀이 전부 아니다 — 최소
    rice 967,672/wood 969,464(지급 1,000,000의 **96.8%가 최악 시점에도 잔존**), `count` 최대
    108/1,200, `used` 최대 1,708/5,000 ⇒ **AI가 자원을 거의 손대지 않은 채 스스로 생산을 멈춘다.**
    **(N82)** 부드러운 감쇠가 아니라 owner별 **완전 정지** — owner5는 tick14,641 이후 런의 39.0%
    동안 `used` 불변(`r_late` 정확히 0.0), owner7 31.8%, owner6 15.4%.
    ⇒ 두 실측은 **(ㄴ)이 유일하게 남은 기술적 진입로**임을 시사하나, 이는 사용자 지시
    (2026-09-21 00:20)의 명시 예외 승인이므로 **모델은 착수하지 않고 승인을 기다린다.**
    **(N83) 경고:** 이 run은 바로 위 lap404 되물음에 **새 증거를 주지 않는다** —
    `used+reserved>5000` 0건(아무도 cap 근처에 못 감)이라 N68 현상이 발생할 수 없다.
    **(N84) 표현 정정:** "전 owner 감쇠"는 과장 — owner0(0.04498)·owner2(0.03749)는 `r_need`를
    후반에도 넘는다. 판정이 유지되는 이유는 G2가 "8인 **각각** 5,000"이라 최저 owner가 구속
    조건이기 때문이다. 정확한 서술은 "8인 합계가 24k에서 11,207 = 8×5,000의 **28.0%**".
    상세 `docs/history/laps/20260921_lap459_middle_g2_w23_a1_independent_review.md`.
  - **2026-09-21 lap460 strategy(Fable5) 처분(`ESCALATE_SOL`§38, 원문 보존·사용자 번복 가능):**
    **(ㄱ) 채택·(ㄷ) 기각** — G2 원문 계약은 "cap5000 플레이 안정"이므로 gate-legal 시딩
    cap근접+soak+왕복을 증거 축으로 인정(마일스톤 승인 대체 아님, 자연 도달 계속 요구 시 번복).
    **(ㄴ)은 모델이 고르지 않고 사용자 승인 대기 유지**(승인 전 AI/설정 변경 착수 금지).
    lap404는 **(가) 잠정 채택**(stock cap5000 `reserved` rider probe를 W24에 의무화, 미재현 시
    회귀 승격·재심). F4는 **(C) 채택**(soak에서 랩/음수 관측 시 즉시 STOP 후 (B) 재심). 다음은
    middle이 **W24**(혼합 구성+전투/사망/재사용 순환 24k) 1장 발행, **144k 금지는 W24 ACCEPT까지 유지**.
  - **2026-09-21 lap461 middle 신규 실측 N87 — (ㄴ)의 무게가 커졌다(선택지 미변경, 모델은 고르지 않음):** lap448에서 8 owner의 배치 주사 구간은 전 쌍에서 겹쳐(2-3 501셀·6-7 484셀 등) 적 유닛이 24,000tick 내내 셀 단위로 인접했는데도 소실은 **4기/1,166기**뿐이었다 ⇒ "전투/사망/슬롯 재사용" 축도 **기하(fixture)로는 만들 수 없음**이 실측됐고, 남은 fixture 내 가설은 구성(타입) 하나뿐이다. 그것마저 실패하면 자연 도달에 이어 **전투 축까지 (ㄴ) 승인 없이는 닫히지 않는다.** W24는 그 결과를 `NO_ENGAGEMENT`로 정직하게 보고하도록 실행 전에 고정했고 **승인 전 AI/생산 정책 변경에는 착수하지 않는다.** 근거 `docs/history/laps/20260921_lap461_middle_g2_w24_issue_and_combat_axis_finding.md`·`ESCALATE_SOL`§39.

실제 구현 선택이 목표·안전·배포 범위를 바꿀 때만 새 질문을 추가한다.

## 2026-09-17 15:20 KST — G2 최우선 루프 재개
- [x] 사용자: "8인 각각 전비 5000 안정 플레이 이걸 최우선 목표로 좀 파보자. 루프 ㄱㄱ". 큐/우선순위 반영(제품완료 아님). G1/G4 후순위, G3중단 유지.

## 2026-09-17 21:16 KST — 사용자 루프 시간 상한
- 사용자: “한국시간 기준12시까지만 루프 돌릴거야. 이후는 진행속도나 가능성 생각해서 볼테니까 그거 생각해서 진행해봐”.
- 현재21:16이므로 Root는 **오늘밤자정2026-09-18 00:00KST**를 보수상한으로 잡았다고 사용자에게 명시했다. 정오를 뜻한 경우 정정 대기; 답변전에는 더짧은상한 유지.
- 10분마다KST보고, 상한에서신규작업중단/ownedcleanup/성과·가능성정리. 기존 STOP 예산리셋·목표축소·제품승인 아님.

## 2026-09-18T17:56:55.515225+09:00 — Claude Code 전환 및 루프 재개
- 사용자: “ㅇㅇ 그렇게 가보고 루프 다시 돌려”. 중간계획/검수ClaudeCode Opus5/high, 실무ClaudeCode Sonnet5/high, 큰분기Astra medium(필요high) 유지. 새명시재개는어제00상한종료이후재개허가이며원제품목표/원본안전/실패보존유지. 이전STOP기술카드예산자동리셋/제품승인아님. 10분KST보고 유지,서비스/커밋/자동push안함.

## 2026-09-21 lap423·429·438·440·442 운영 회수 계보 (lap462 압축 — 원문 전량 보존, 삭제 없음)
- 이 5건(lap423 P-H 동기복구·lap429 디스크blocker해소·lap438 W18 동기복구·lap440 W19 동기검증회수·
  lap442 W20 background회수+lap441 middle W19 ACCEPT(R1) 독립검수)은 **모델/Root가 쓴 운영 회수
  기록**이며(사용자 지시 아님), 400줄 상한 때문에 lap462가 포인터로 줄였다. **원문 전량 보존**:
  `docs/history/20260921_inbox_lap462_precompaction.md`(SHA `d67aed38…f83113b03d`, 415줄).
  핵심 결론은 STATUS G2 표/검증상태(lap441~443)에 남아 있고, 개별 전문은
  `docs/history/laps/20260921_lap429_work_g2_w16_disk_blocker.md`·
  `20260921_lap441_middle_g2_w19_independent_review.md`(§8에 lap440 산출물)·
  `20260921_lap443_middle_g2_w20_t2_independent_review.md`(lap442 실행분)에 있다.
  lap423/438은 개별 lap 파일이 없어 위 스냅샷이 유일한 원문이다.

## 2026-09-21 lap425·427·428 계보 (lap449 압축 — 원문 전량 보존, 삭제 없음)

- 이 세 항목은 **모델이 쓴 회차 기록**이며(사용자 지시 아님), INBOX 400줄 상한(`checks/context_limits.py`)에
  걸려 lap449가 포인터로, **lap488이 한 번 더** 포인터로 줄였다. **원문 전량 보존, 삭제 없음** —
  `docs/history/20260921_inbox_lap449_precompaction.md`(SHA `ebf58faa…4288086`, 411줄)와
  `docs/history/20260922_inbox_lap488_precompaction.md`(SHA
  `4ab21ca1ec058bbc04c71ce5a36e1e62d282e37985b7b0e99eebb282025f82c7`, 419줄)에 그대로 있고,
  각 lap 전문은 `docs/history/laps/20260921_lap42{5,7,8}_*.md`에 있다.
  요지: lap425(W14 P-I) 판정 **(B) `+0x700` 자체가 표적** 확정 → lap427(W15 P-J) 당시
  (J2) 외부write·(J3) 블록write 보고 → lap428 middle 측정 ACCEPT·해석 2건 정정(N40으로 (J3) 강등,
  N41로 (J2) 근거 교체, 신규 N42·**N43**)·W16 발행.
- **⚠ 이후 뒤집힌 부분(요지는 남긴다):** **lap439 N51이 (J2)·(J3)·(K2)를 전부 REJECT**했다 — 진범은
  외부 write가 아니라 후보 빌드의 **immediate 재배치 오탐**(`0x0040F053` 종료 즉치)이고 세 store는
  원본과 바이트 동일했다. **(L2)·N43은 유지.** 현재 유효한 결론은 STATUS G2 표와 `ESCALATE_SOL`§25.


## 2026-09-21 Root 회수 — lap448 W21 Step1 24k cap-proximity soak (lap489 압축 — 원문 전량 보존, 삭제 없음)
- 이 블록(Root 동기 회수 + lap449 middle ACCEPT 검수)은 **모델/Root가 쓴 운영·검수 기록**이며
  (사용자 지시 아님), 400줄 상한 때문에 lap489가 포인터로 줄였다. **원문 전량 보존**:
  `docs/history/20260922_inbox_lap489_precompaction.md`(SHA
  `d9ec8ac257d353370346c5ee20ceddf5fb423db4459e977e91d2a8df8e437ebd`, 400줄).
  요지: lap448 background 방치를 Root가 동기 회수, 신후보 `a10024de…` N=4001 24k soak
  `CAP_PROXIMITY_STABLE`(부분 증거) → lap449 middle 원시 712표본 재계산 ACCEPT(U1~U3 PASS,
  U4 메모리 절반 귀속, N64~N68). 핵심 결론은 STATUS G2 표와
  `docs/history/laps/20260921_lap449_middle_g2_w21_step1_independent_review.md`에 있다.
