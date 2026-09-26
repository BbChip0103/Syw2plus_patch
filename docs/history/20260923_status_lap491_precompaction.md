# STATUS — 매 바퀴 갱신하는 기억
## 지금 상태
활성 G1/G2/G4 제품 미완료(0/3); G3 최대16인은 2026-09-17 사용자 지시로 중단. **G2 최우선·9/18 Claude Code 역할로 재개 승인**; **2026-09-21 00:20 지시로 G1/G4는 G2 성립 전까지 잠정 중단, G3는 계속 포기 범위로 고정**(G1/G4 표 항목은 과거 증거 보존일 뿐 현재 작업 대상 아님). M1/G1 요구 유지: 원본 구도·입력과 차후 고해상도 그림의 디테일 보존을 함께 만족하는1600×1200 화면. 제품 기준은 DESIGN, 사람 승인
원문은 feedback/APPROVALS·INBOX를 따르며 2026-09-12 01:03 bounded repair→fresh validation 허가는 제품/출시 승인이 아니다. DxWrapper 2× 화면·S1 입력쌍은 배치 프리뷰 근거만; 추가 디테일 보존 경로와 WM_CLOSE 결함은 남았다.
과거 G1/lap275~379 승인·반려·미결 계보와 lap401~475의 개별 STATUS 스냅샷은 `docs/history/`의 각 `*_precompaction.md`(내용 삭제 없음)에 그대로 있다. **이번 lap487 압축 직전 STATUS 전문**은 `20260922_status_lap487_precompaction.md`(SHA `bead7bb0f95b0a09f62cdf9a3ee77170b4c8ba9e79f9979973e06a1270223d12`, 127줄)에 보존했다(그 이전 lap485/480 등 precompaction 스냅샷 포인터는 그 파일 안에 그대로 있다). 개별 lap 상세는 `docs/history/laps/`에 그대로 있다.
| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | native PS3 PASS·원본구도 FAIL·제품 미완료 | stock UI 클릭 PS9→PS7→PS5→PS3 tick3, native `1600×1200×8bpp/pitch1600`/viewport 전역 PASS; 월드 시야 확대·스프라이트/HUD 원본 픽셀 크기라 G1 배치 FAIL, 고해상도 SPR·생산·종료 미검증; 이번최종acquisition은초기화guard8000001A에BLOCKED |
| G2 | **lap478(middle) Round 2 독립검수 = 측정 ACCEPT(불일치0) / 해석 REJECT(`ROUND2_PRECONDITION_NOT_MET`). rider 라인은 `RIDER_STOCK_REPRO_UNDECIDABLE_BY_FIXTURE`로 종료(§44 하드캡 소진), H-serial은 승격 반대, W24 CLOSED·144k는 strategy 회부.** 5중 신호는 원시 669표본으로 전부 재현(`reserved`{0,10}·`producer_b_command`{1}·`producer_b_progress`{0}·B rice 미징수·finalization 1건). 그러나 **(N111)** 주문 B의 엔진 read `before`가 `{used 4990, reserved 10}`이라 **실효 headroom=cap−used−reserved=0<비용10** ⇒ work의 "headroom 충분" 전제가 원시와 어긋나 H-serial 미지지. **(N112)** `used+reserved+비용≤cap`일 때만 수락 규칙이 lap471/474/476A/476B **4/4를 경계(등호)까지 설명** ⇒ H-headroom을 "미결 예약 포함"으로 정정·강화, H-serial은 lap471을 설명 못해 단독 대체 불가. **(N113)** 밴드 `[10,20)`이 두 번째 수락을 수학적으로 불가능하게 만들어 §45 요건①②가 성립한 적 없다 ⇒ "재현 실패"가 아니라 **"미시험"**. **(N114)** 판정식 잠재 위양성(정산 끝난 A가 stuck 증인이 될 수 있었다). **(N115)** 사망 이벤트15=유닛16기, cost-20 사망 1건(producer 건물 파괴 가능성, UNKNOWN). 이번 회차 게임실행0·제품코드0·source변경0(3자일치)·targeted167 passed·`SAFETY_PASS`·`CONTEXT_PASS`·커밋0. 전문 `20260922_lap478_middle_g2_w24_stepC_round2_independent_review.md`·`ESCALATE_SOL`§46. **lap479 strategy 처분(§47): W24 CLOSED(`UNDECIDABLE_BY_FIXTURE`)·144k 조건부 해제·W25 허용·H-serial 제외. lap480(middle): W25 발행하되 §47(ii) 구성 절차가 브리지 가드로 실행 전 도달 불가(N117)·목표 상태는 핀으로 배제된 op4로만 구성 가능(N118) ⇒ 카드 `BLOCKED_PENDING_STRATEGY`·§48 Q1 회부. lap481(strategy): **Q1=D2 채택**(§49, R1·R2 경계)·카드 `READY_FOR_WORK`.** **lap483(work): §4+§8 게임 1회 실행 완료. lap484(middle) 독립검수 = 측정 ACCEPT(불일치0) / 해석 REJECT.** 라벨 `PRECONDITION_NOT_MET` 유지하되 사유는 `order_terminated_without_production_at_tick1943`으로 정정(N122: 주문은 tick1943 종결, 그때 A는 hp3600 만전, 사망은 1,109tick 뒤). **(N119)** 수락은 `used`를 올리지 않고 `reserved`만 올린다(op1 before/after 동일); 정산=`reserved−cost`·`used+cost`·`count+1`, 사망=`used−cost`·`count−1` ⇒ 두 계정 독립, N112 이중계상 아님·N68의 5,010은 실제 약정. **(N121)** 대조군은 progress100과 정산이 같은 표본(≤3tick)인데 표적 arm은 progress100으로 **529tick 체류**(≥176×) 뒤 미생산 종결, 생산속도는 정상(695 vs 701tick) ⇒ 이상은 **정산 단계 국소**. 단 카드 임계 `5L=3510`은 "주문→해소" 지연 기준이라 과대 ⇒ **임계 교정 결함**으로 176배 신호가 null 라벨로 떨어짐. **(N120)** 그 종결은 수락이 올린 적 없는 비용을 `used`에서 빼는 **비균형 차감**(자연 발생 UNKNOWN). **(N123)** 이 run은 **N68 미재현**(N68=24k 무기한 vs 여기 529tick 종결) ⇒ H-gate(정산 cap 재검사 후 포기)·H-place(배치/스폰 실패 타임아웃) 2가설 병존. 카드 CLOSED, strategy 회부 Q2(144k 개방)·Q3(op4 2콜) = §50. **lap485(strategy, Fable5) §50 판정(§51): Q2=E2(144k 계속 닫음, 재개방=W27 실행+측정 ACCEPT+무결성 위반0, `used`수치 부분증거 라벨 강제)·Q3=F1(op4 2콜 counterfactual W27 허용, R2′/R3/임계 재교정 의무). lap486(middle) lap485 spot-check 독립 재현 ACCEPT(불일치0)·W27 발행(`READY_FOR_WORK`)·임계 `T_block=200tick` 확정(N124)·N125로 N121 확증(W25 null은 임계 과대의 산물, 79표본 전구간 stall 522tick=임계 2.6배) ⇒ Q2=E2 근거 강화. **lap487(work, Sonnet5) W27 §4 게임1회 동기 실행(op4 2콜: 구성4995→counterfactual4980, +0tick). lap488(middle, Opus5) 원시 독립 재계산 = 측정 ACCEPT(불일치1건·판정무영향) / 라벨 `SETTLEMENT_RESUMED_AFTER_HEADROOM` 확정 / 귀결 "⇒H-gate 확정"은 REJECT. W27 `CLOSED`.** AND 3조건(`reserved`10→0 ∧ `used`4980→4990(+비용10) ∧ `count`5→6)은 원시로 전부 충족된다. 그러나 **(N127 결정적)** A가 `progress==100`으로 관측된 표본은 **1건(tick1408)**뿐이고 op4콜#2는 tick1410 ⇒ **개입 전 체류 2tick = `T_block=200`의 1/100**이며, 대조군 지연은 `run_summary`의 1이 아니라 **0tick**(원시 표본207이 progress100·`reserved`10→0·`used`40→50·`count`3→4를 **같은 표본**에 담음; 스크립트가 표본tick 대신 루프종료 재읽기tick에서 뺀 정의결함 `:454`)이고 대조군 표집 평균3.35/최대4tick이라 **~4tick 미만 지연은 분해 불가** ⇒ A의 2tick 미정산은 그 맹점 안 ⇒ **"개입 전에 막혀 있었다"는 측정이 없어 H-gate와 "애초에 안 막힘"이 구분되지 않는다. §1 질문 OPEN, 귀결은 "H-gate 지지·확정 아님".** 결함은 lap487 실행이 아니라 **lap486 카드**(+50tick 발사창이 차단 노출 전 개입을 강제). **(N126)** "동일 트랜잭션 창" 서술 철회 — 엔진 자체 사후블록(tick1410)은 `{4980,res10,count5}`로 **아직 재개 전**이고 재개는 **tick 미기록** 재읽기에서만 보임 ⇒ 재개 지연 UNKNOWN. **(N128)** §5 R1 승계는 재개신호(`used`+비용)를 그 자체로 위반으로 만들어 **재개 라벨을 문언상 도달불가**로 했다 ⇒ "스크립트 버그"는 절반만 맞고 뿌리는 카드. **(N129)** 세 이벤트 배열 `[]`는 예외가 기록경로를 건너뛴 결과라 **"사건0건"이 아니다**(§6 N120 의무 post-call2 미이행). **(N130)** `call2_fired=true` 표본 **0건** ⇒ §4-7의 ≥600tick 관측 미실행, 개입후 주장은 **단일 재읽기 1건**에 의존, `NO_RESUME_WITHIN_WINDOW` 평가 불가, §4는 1~6단계만 실행. 무결성 위반0·R2′(op4 정확히2콜)·R3 5종·A 260표본 전부 생존·source3자불변·핀3종·targeted16 passed·`SAFETY_PASS`·`CONTEXT_PASS`·커밋0. **lap489(strategy, Fable5) §53 판정(§54): Q4=승인(W28 재발행, 차단 선입증·R1 정정·관측 완주+증분 기록·지연 정의 수리 의무, 미재현 시 1회 종결)·Q5=아니오(144k 계속 닫음, 재개방=W28 완결 1회 종결+측정 ACCEPT+무결성0으로 대체). spot-check로 N126/N127/N129/N130 원시 재현(불일치0). **lap490(middle, Opus5) §54 경계대로 W28 발행 완료(`G2_SETTLEMENT_BLOCKAGE_PREPROOF_COUNTERFACTUAL_LAP490.md`, `READY_FOR_WORK`) + lap483/487 원시 독립 재현 = 측정 ACCEPT(정정 1건·판정 무영향).** 교정 5건 문언화: 발사 전건을 **"progress100·5중 신호 연속 체류 ≥`T_block`200tick 선입증 직후"**로 교체(+50tick 창 폐기)·**R1′**(`used`+비용10 ∧ `reserved`10→0 ∧ `count`+1은 재개 신호이고 위반 아님, N128 해소)·모든 재읽기 tick 기록+콜#2 엔진 tick 기준 ≥600tick 관측 완주(정산·종결·사망에서 break 금지, N126·N130 해소)·표본마다 append+flush 증분 기록(N129 해소)·대조군 지연을 표본 tick 기준으로 정의하고 표집 ≤3tick 상향. **(N131 정정)** §54 서술의 "콜#2 엔진 사후블록 `{4995,10,5}`"는 원시의 **before** 블록이고 **after는 `{4980,10,5}`**(둘 다 재개 전 ⇒ 판정 무영향). **(N132)** lap487 대조군에 차단 predicate 표본 **0/208**이고 정산 표본에서 `command`15→1 동반 ⇒ 건강한 정산은 predicate를 만들지 않는다(특이도 지지, lap483의 79표본 연속은 이례). **(N133)** 실측 **33tick/s** ⇒ 선입증 200tick≈6초·관측 600tick≈18초로 완주 비용 사실상 0, lap483 종결은 발사 예정 시점보다 ~329tick 뒤. **(N134)** lap483의 `progress==100`은 종결 이후 tick3052까지 총 246건 ⇒ 단독으로는 계류 신호 아님, 5중 신호 연접만 쓴다. 게임실행0·제품코드0·source변경0·커밋0·표적16 passed·핀3종 현존. ·제품 미완료(부분 증거) |
| G3 | 사용자 지시로 중단·활성 범위 제외 | 16 PlayerStruct가 bulk save112,036B 초과, self/opponent mask8bit라 owner8~15 표현 불가; 활성9~16/LAN 미완료 |
| G4 | 원본 issuer 국소 이동 PASS·제품 미완료 | 직접 command 기록은 정지; mainthread 원본 issuer는 같은 source 이동68좌표. current waypoint reinforcement 수리 후 AI2기 이동21/22좌표·목표gap2/1 PASS; one-shot2회 같은 이동 결과, 발행tick다름·지속 정책/품질 미검증; 이번정상AI512+load11 관측만PASS/정확postload미확정 |
## 다음 한 가지
**work(Sonnet5/high)가 W28 `docs/work/active/G2_SETTLEMENT_BLOCKAGE_PREPROOF_COUNTERFACTUAL_LAP490.md`
§4를 게임 1회·동기·foreground로 완주한다(background 금지, 재시도 없음).**
핵심 순서: PS3·cap5000 확인 → op7 자원 → **대조군(≤3tick 표집, 지연을 표본 tick으로 계산·분해능
공개·차단 predicate 표본 수 기대 0)** → 주문 A 5중 신호 수락 → **op4 콜#1 `used=4995`** →
≤3tick 표집으로 **progress100·5중 신호 연속 체류 ≥200tick 선입증** → 그 직후 **op4 콜#2 `used=4980`**
(직후 재읽기는 tick과 함께 표본으로 기록하고 예외를 던지지 않는다) → **콜#2 엔진 tick 기준
≥600tick 관측 완주**(정산·비균형 종결·사망에서 break 금지). op4는 **정확히 2콜**, 표본마다
append+flush 증분 기록, 라벨 3종·사유 사전 표만 사용, 라벨 확정은 work가 하지 않는다.
차단이 `t0+700tick` 안에 200tick에 도달하지 못하면 `PRECONDITION_NOT_MET`
(사유 `no_blockage_ge_t_block_observed`) **1회 종결·재시도 없음**(§54).
lap488·489·490이 연속 무실행이므로 **이번 work 회차의 게임 1회 실행은 의무**다.
**(ㄴ)·lap404(가)/(나)·F4(B)/(C)·3단 사용자 마일스톤 승인은 여전히 사용자 전권 대기**, 모델 착수 금지.
## 지금 막힌 것 (Blockers)
- **F4(lap395 확정): 안전상한 UNKNOWN — 어떤 uniform cap도 랩을 막지 못한다.** lap394 반례 독립 재현 ACCEPT(12001/32761/40001 일치); lap393 P9의 assertion은 `32767//8` 상수 산술 2개뿐이라 불변식 산문을 인증하지 않는다. **신규:** 생산 gate `0x43EDA0`은 count cap `+0x2010`·supply cap `+0x2012`를 둘 다 강제하나 `roster_add 0x43EE30`은 `cmp ax,0x4B0`(배열1200)뿐이고 두 cap 참조 **0건** ⇒ 이전은 두 cap을 모두 우회. donor 이전+gate-legal 재생산 **펌프**로 수신 used가 cap 1500/4095/5000 **전부에서 32,785 도달**(차이는 재생산 799/87/7회뿐) ⇒ **cap≤4095 안전상한·§7.6 분기 A 전제 무효, 즉치2개 카드 착수 근거 상실**. cap5000은 펌프 없이 이전만으로도 1160기/40,000 집중 가능(1160≤1200). 남은 상한 `min(1200,풀)×최대비용`은 손익분기 평균 27.31 vs 실측 평균 31.66~34.42 ⇒ 37,988~41,309>32,767로 **구제 실패·cap 비의존**. 최대 단위비용은 비용표 `0x9B5238`/type표 `0x66B81D`가 `.data` raw끝 `0x4F9000` 바깥 BSS라 **정적 불가**(W2가 실측). P1~P4 바이트 사실·lap389 NO_GO·lap391 수치는 유지. 실제 게임 도달성 UNKNOWN.
- **현재 G2 구조통합 blocker:** 저비용 다수 구성의global1199/ordinaryowner242 확장에 필요한 Unit·보조 인덱스·bulk-relative alias·초기화/수명주기·저장/LAN의 일관 계약 미구현. 두 actual 진단은局所getter追加로 정상simulation에 도달하지 못함. 개별PC따라 패치 반복중단; 제품완료/전체불가능 선언없음. **lap381이 닫은 것은 layout 선행질문(C1 count폭·H1 matrix형태)뿐이며 이 통합 blocker는 그대로다.** **lap385 신규 실측(Astra 큐, 승인대기·작업은 계속함):** 핀된 save`0x440F02`(len`0xE397C`,src`0x892410`)/load`0x4412DC`가 정의하는 bulk blob `[0x892410,0x975D8C)`이 existence/age/catA/catB/active **5개 영역을 내부에 품는다**(unit_pool만 bulk 아래, 별도 roster). ⇒ 확장은 `0x892410`을 slot당1,880B 밀어올리는 **동시에** 고정길이 blob 내부를 slot당14B 불린다(N=4001→새 start`0xD97DE8`/필요 len`0xED2AA`); 둘 다 하드코딩 push 즉시값이라 **layout mapper만으로 저장호환 확장은 원리적으로 불가**하고 길이·주소 즉시값 fixup+저장포맷 변경이 필수다. lap379 Sol의 integration/broad-patcher/runtime NO-GO를 **뒤집지 않고 강화**한다. **새 불가능 증명 아님** — G2를 이 경로로 계속할지는 Astra 판정 사항. **lap388 종결:** 레이아웃 계산기 카드는 ACCEPT·계약5 CLOSED로 닫혔으나 이 통합 blocker는 **그대로다** — 오히려 "길이·주소 두 하드코딩 즉시값 fixup+저장포맷 변경 필수"를 수치로 굳혔다(`loop/ESCALATE_SOL` 판정 대기). **lap397 범위 정정(무효화 아님):** 이 통합 blocker는 owner당 1200기 초과와 저장호환에만 걸리며 **풀 확장 스파이크의 임계경로가 아니다** — `roster_add`의 `cmp ax,0x4B0`은 owner 유닛 **개수** 제한이고(`0xD4A+1200*4==0x200A` 검증), 유닛 1200기 미만 owner는 PlayerStruct 무변경으로 slot id≥1200을 담는다.
- **G4 persistent STOP:** 비지원 mode 제외와 post-load 첫 tick/중복 계약 미확정(`BLOCKED_MODE_EXCLUSION_AND_POSTLOAD_CONTRACT`); normalcall/owner/serializer·one-shot2회 이동과 이번shadow512+load11만 보존(정확load완료marker없음). **과거 lap379 provenance:** test pre-image SHA 충돌은 역사 검증 UNKNOWN으로 보존하되 fresh 현행 SHA의 제품 실행을 차단하지 않는다. 재핀·자가 baseline 승격은 계속 금지한다.
- **과거 G4 fresh AI runtime 실패(보존; 현재 chain 진입/180초 실행은 가능):** current bridge `592d03ec…0b3030`, old `f44090a3…adac4b`, ddraw override on/off 모두 PS40/tick0·동일 serious-error 이미지 `008e8465…6e3cd9`. 당시 bridge/renderer 두 가설 소진으로 반복 STOP한 기록; temp `Syw2plus_patch/g4_ai/`, residue0.
- **원본·후보 S1/화면·세 입력 PASS:** logical load-button `(316,372)` 1회로 PS35→PS3, 8 PlayerStruct 각각 save000과 일치. 원본800×600/후보1600×1200 PS35 실제 메뉴 캡처는 최근접 2배 뒤 **exact100%/MAE0**, PS3는 별도 쌍 exact99.213%/MAE0.470. 동일 source SHA fresh 미니맵 쌍 `(35,560)` camera `(39,53)→(49,159)`; 선택해제 쌍 `(400,220)` count `1→0`/first_slot `1174→0`; 드래그쌍 `(520,200)→(780,455)`은 clear0→count3/first_slot108 모두 동일. cleanup0잔류/후보 ini 원복. 첫 `(150,520)`은 원본 무효라 실패 보존. 생산·종료·장은 UNKNOWN.
- **G1 R1/S1 클릭·좌표·PS전이 포렌식 계보(lap279~339, 압축, 전문 보존):** G1은 사용자 지시로
  후순위이며 이 블록의 모든 결론(좌표계 해소·도달판정식·F1/R1/R2 종결·provenance 회귀 a~h·
  N1~N16·W2/W3 미결·exact-site 계측 금지·G3 저장포맷 공간부족·Plan C 함정)은 **전문 그대로**
  `docs/history/laps/20260920_status_lap409_precompaction.md`(SHA
  `d99533e1b1dfbb1df30e89dd77094e200ac29c92e2d72b37c356f52f8e33cd7f`, 130줄)와 각 원 lap 기록
  (`20260910~20260920_lap{279..339}_*.md`)에 보존된다. 삭제·재해석 없이 STATUS 표시만 축소했다.
## 검증 상태
**2026-09-23 lap490(middle, Opus5) — §54 경계대로 W28 발행 + lap483/487 원시 독립 재현(전문
`docs/history/laps/20260923_lap490_middle_g2_w28_issue.md`·`ESCALATE_SOL`§55, 재계산
`temp/Syw2plus_patch/g2_capacity/20260922_lap490_middle_w28_issue/`).**
`run_summary`의 `verdict`/`reason`/`exception`과 lap487~489 서술을 **참조하지 않고** 원시만 재계산:
lap483 = 전이 정확히 2건·progress100 tick1414→종결 tick1943 체류 **529tick**·그 구간 79표본 전부
5중 신호 / lap487 = `progress==100` 정확히 1건(tick1408)·`call2_fired` 0건·op4 정확히 2콜·콜#2 엔진
after `{4980,10,5}`(재개 전)·재개는 tick 없는 재읽기뿐·대조군 표본 tick 기준 지연 **0**
⇒ **측정 ACCEPT**(정정 1건 = N131, §54 서술이 before 블록을 사후블록으로 적음, **판정 무영향**).
**W28 발행 완료**(`READY_FOR_WORK`, §54 교정 5건 전부 문언화 + 지평 `t0+700tick`·`T_attrib=50tick`·
사유 사전 표 고정). 신규 N132(대조군 predicate 0/208 = 특이도)·N133(33tick/s, 완주 비용 ~0,
종결은 발사 +329tick 뒤)·N134(`progress==100` 단독은 계류 신호 아님).
게임실행0·제품코드0·source변경0·커밋0·표적16 passed·`SAFETY_PASS`·`CONTEXT_PASS`·잔류0·새 카드 1장.
**2026-09-22 lap489(strategy, Fable5) — §53 Q4·Q5 판정(전문 `ESCALATE_SOL`§54·lap 기록
`20260922_lap489_strategy_g2_q4_q5_disposition.md`).** 판정 전 spot-check: lap487 원시 직접
재계산으로 lap488의 결정적 사실 전부 재현(불일치 0) — A progress100 window 표본 정확히 1건
(tick1408)·`call2_fired=true` 0건·A 생존 260/260·477콜 중 op4 정확히 2콜·콜#2 엔진 사후블록
tick1410 `{4995,10,5}`(재개 전)·재개는 tick 미상 재읽기 `{4990,0,6}`뿐·대조군 표본207(tick702)
progress100+정산 동시(지연 0, run_summary `1`은 정의 결함). **Q4=승인·Q5=아니오**(내용은 위
「다음 한 가지」와 §54). 게임실행0·제품코드0·source변경0·커밋0·`SAFETY_PASS`·`CONTEXT_PASS`.
**2026-09-22 lap488(middle, Opus5) — lap487 W27 원시 독립 재검수(전문
`20260922_lap488_middle_w27_independent_review.md`, 재계산
`temp/Syw2plus_patch/g2_capacity/20260922_lap488_middle_w27_review/`).**
`run_summary`의 `verdict`/`reason`/`exception`과 work의 `verify_lap487.py`를 **읽지 않고**
원시만으로 재계산: 카드 §5 AND 3조건 전부 충족 ⇒ **측정 ACCEPT**, 라벨
`SETTLEMENT_RESUMED_AFTER_HEADROOM` **확정**, W27 `CLOSED`. R2′(477콜 중 op4 정확히 2콜)·
R3 전제 5종(tick1408)·무결성 위반 **0**(음수·wrap 0, `reserved∈{0,10}`, 라이브 `used` 최대
4995≤cap, `used+reserved` 최대 5005=의도된 fixture)·producer A 260표본 전부 생존·
source 3자 불변·op4 배제 핀 3종 현존·표적 **16 passed**·`SAFETY_PASS`·`CONTEXT_PASS`·잔류 0.
**그러나 라벨에 붙은 귀결 "⇒H-gate 확정"은 채택하지 않는다(N127)** — 개입 전 체류가 2tick뿐이고
대조군 분해능이 ~4tick이라 **차단 자체가 측정되지 않았다**. §1 OPEN. 재계산 불일치는 1건
(대조군 지연 1→**0**, 스크립트 `:454` 정의 결함)이며 `32×지연<200`이라 `T_block=200`(N124)은
그대로 지배해 **판정 무영향**이다. 부수 정정 N126·N128·N129·N130은 위 G2 표와 §53에 있다.
게임실행0·제품코드0·source변경0·커밋0·새 카드 0.
**2026-09-22 lap487(work, Sonnet5) — W27 §4 게임 1회 동기 실행(전문
`20260922_lap487_work_g2_w27_settlement_resume_counterfactual.md`, 원시
`temp/Syw2plus_patch/g2_capacity/20260922_lap487_w27_settlement_resume_counterfactual/`).**
op4 정확히 2콜: 구성(tick710, `used=4995`) → R3 전제 5종이 progress100 최초 표본(tick1408)에서
즉시 충족 → counterfactual(+0tick, `used=4980`). **스크립트 자체 사후검증 버그**(콜#2 직후 값이
즉시 정산-재개로 바뀔 수 있다는 카드의 핵심 가설을 검증 코드가 배제한 설계 결함)로
`run_summary.json` 자동 `verdict`는 **잘못** `PRECONDITION_NOT_MET`(신뢰 금지, 사유
`"op4 call #2 wrote used=4990, expected 4980"`). 예외 이전 동기 기록된 원시 필드만으로
(`verify_lap487.py`, run_summary verdict/reason 미참조) AND-판정 재계산:
`reserved`10→0 ∧ `used`4980→4990(+10=비용) ∧ `count`5→6(+1) 동일 트랜잭션 창 전부 충족
⇒ **원시는 `SETTLEMENT_RESUMED_AFTER_HEADROOM`(H-gate 지지)을 시사, work는 라벨 미확정**.
스크립트 버그로 `finalization_events.json`은 빈 배열(정상 append 경로 미도달) — middle이 원시
필드로 직접 보완 확인해야 한다. targeted16 passed·`SAFETY_PASS`·`CONTEXT_PASS`·게임실행1·
source변경0(3자일치)·op4배제핀3종 유지·커밋0.
**lap356~486 계보(전문 전량 보존, 삭제 없음):** `20260922_status_lap487_precompaction.md`
(SHA `bead7bb0f95b0a09f62cdf9a3ee77170b4c8ba9e79f9979973e06a1270223d12`, 127줄)에 이 압축 직전
STATUS 전문이 그대로 있고, 그 안에 lap480/485 등 이전 precompaction 스냅샷 포인터가 연쇄
보존된다. 핵심 요지: lap486(middle) lap485 spot-check 원시 재현 ACCEPT+**T_block=200tick 확정
(N124)**+N125(Q2=E2 근거 강화)+W27 발행 → lap484~485(W25 REJECT+Q2=E2/Q3=F1 채택) →
lap479~481(W24 CLOSED+W25 발행+Q1=D2) → lap475~478(Round1 ACCEPT→Round2→Round2 REJECT,
N111~N116) → lap462~474(Step A~D 7회차, rider 계보) → lap356~461(W8~W23, soak/케이던스/
판정기 수리/fixture축 소거). 개별 lap 전문은 전부 `docs/history/laps/`에 있다.
## 바퀴 기록
lap490(middle, Opus5) §54 경계대로 **W28 발행 1회**(`G2_SETTLEMENT_BLOCKAGE_PREPROOF_COUNTERFACTUAL_LAP490.md`,
`READY_FOR_WORK`) + lap483/487 **원시 독립 재현 = 측정 ACCEPT**(정정 N131, 판정 무영향).
교정 5건 문언화(선입증 발사·R1′·tick 기록+600tick 완주·증분 기록·대조군 지연 정의) + N132·N133·N134.
게임실행0·제품코드0·source변경0·커밋0·표적16 passed. 다음은 **work의 W28 게임 1회 실행(의무)**.
전문 `20260923_lap490_middle_g2_w28_issue.md`·§55.
lap489(strategy, Fable5) §53 Q4·Q5 판정 → **Q4=승인(W28 재발행, §53 교정 3건+증분 이벤트 기록+
지연 정의 수리 의무, `no_blockage_ge_t_block_observed` 1회 종결) · Q5=아니오(144k 계속 닫음,
재개방 조건을 "W28 완결 1회 종결+측정 ACCEPT+무결성 위반0"으로 대체)**. spot-check 불일치0.
다음은 middle W28 발행 1회 → work 게임 1회 실행. 게임실행0·source변경0·커밋0. 전문 §54.
lap488(middle, Opus5) lap487 W27 원시 독립 재검수 → **측정 ACCEPT · 라벨
`SETTLEMENT_RESUMED_AFTER_HEADROOM` 확정 · 귀결 "⇒H-gate 확정" REJECT · W27 `CLOSED`**:
N127(개입 전 체류 2tick « `T_block`200, 대조군 지연 재계산 0tick·분해능 ~4tick ⇒ 차단 미측정,
§1 OPEN)·N126(동일 트랜잭션 창 서술 철회, 재개 지연 UNKNOWN)·N128(R1↔재개라벨 자기모순,
"스크립트 버그"는 절반만 맞음)·N129(빈 이벤트 배열은 사건0건이 아님)·N130(≥600tick 관측 미실행,
§4는 1~6단계만). strategy 회부 §53 Q4·Q5. 게임실행0·제품코드0·source변경0·커밋0·새 카드 0·
targeted16 passed·`SAFETY_PASS`·`CONTEXT_PASS`. 전문
`20260922_lap488_middle_w27_independent_review.md`.
lap487(work, Sonnet5) W27 §4 게임 1회 동기 실행(재시도 없음, background 미사용, 완주): 위
「검증 상태」와 동일 — op4 2콜(4995→4980)·스크립트 사후검증 버그로 자동verdict 오판(신뢰금지)·
원시 재계산(`verify_lap487.py`)은 `SETTLEMENT_RESUMED_AFTER_HEADROOM` 시사·라벨 미확정.
게임실행1·source변경0·targeted16 passed·`SAFETY_PASS`·`CONTEXT_PASS`·커밋0. 전문
`20260922_lap487_work_g2_w27_settlement_resume_counterfactual.md`.
lap486(middle, Opus5) lap485 spot-check를 lap483 원시로 독립 재현 **ACCEPT(불일치0)** + **W27 발행**
(`G2_SETTLEMENT_RESUME_COUNTERFACTUAL_LAP486.md`, `READY_FOR_WORK`): §51 R2′/R3/라벨3종 승계,
**임계 `T_block=200tick` 확정(N124)**, **N125로 N121·Q2=E2 확증**. 새 strategy 회부 없음.
게임실행0·제품코드0·source변경0·커밋0. 전문 `20260922_lap486_middle_g2_w27_issue.md`·`ESCALATE_SOL`§52.
lap356~485 계보(압축, 수치·판정 전문은 위 precompaction 스냅샷 연쇄와 각 원 lap 기록에 그대로):
lap484~485(W25 REJECT→Q2=E2/Q3=F1) → lap479~481(W24 CLOSED→W25→Q1=D2) → lap475~478(Round1
ACCEPT→Round2→REJECT) → lap462~474(Step A~D 7회차) → lap456~461(W22 6arm→W23 DECAYED→W24 발행) →
lap356~455(W8~W23 soak/케이던스/판정기/fixture축 소거). 전 회차 제품코드/커밋
전부0, source변경은 N22 명시 회차만.
