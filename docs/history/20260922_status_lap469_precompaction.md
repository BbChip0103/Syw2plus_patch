# STATUS — 매 바퀴 갱신하는 기억
## 지금 상태
활성 G1/G2/G4 제품 미완료(0/3); G3 최대16인은 2026-09-17 사용자 지시로 중단. **G2 최우선·9/18 Claude Code 역할로 재개 승인**; **2026-09-21 00:20 지시로 G1/G4는 G2 성립 전까지 잠정 중단, G3는 계속 포기 범위로 고정**(G1/G4 표 항목은 과거 증거 보존일 뿐 현재 작업 대상 아님). M1/G1 요구 유지: 원본 구도·입력과 차후 고해상도 그림의 디테일 보존을 함께 만족하는1600×1200 화면. 제품 기준은 DESIGN, 사람 승인
원문은 feedback/APPROVALS·INBOX를 따르며 2026-09-12 01:03 bounded repair→fresh validation 허가는 제품/출시 승인이 아니다. DxWrapper 2× 화면·S1 입력쌍은 배치 프리뷰 근거만; 추가 디테일 보존 경로와 WM_CLOSE 결함은 남았다.
과거 G1/lap275~379 승인·반려·미결 계보는 전체 원문 `20260917_234449_status_pre_cutoff_compaction.md`(SHA 9400241176cce4bbe0047b358a887f09e269d9824a253654d6ff2718d352ddef,141줄)에 보존했으며 fresh 제품 PASS/출시 승인으로 승격하지 않는다. **lap462 압축(위 lap401~459의 개별 압축 각주 40건을 한 줄로 병합):** 그 압축 기록들이 가리키던 STATUS 스냅샷은 각 lap 번호의 `20260920_status_lap401_precompaction.md`~`20260921_status_lap459_precompaction.md` 파일에 그대로 남아 있으며(내용 삭제 없음), lap462 압축 직전 전체 원문은 `20260921_status_lap462_precompaction.md`(SHA 0b8d73aa3724c18a59e36368ee1b90fe972a73599be431564fbced5b75b1dc06, 128줄)에 보존했다. 개별 lap 상세는 `docs/history/laps/`에 그대로 있다.
| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | native PS3 PASS·원본구도 FAIL·제품 미완료 | stock UI 클릭 PS9→PS7→PS5→PS3 tick3, native `1600×1200×8bpp/pitch1600`/viewport 전역 PASS; 월드 시야 확대·스프라이트/HUD 원본 픽셀 크기라 G1 배치 FAIL, 고해상도 SPR·생산·종료 미검증; 이번최종acquisition은초기화guard8000001A에BLOCKED |
| G2 | **lap467(middle) 독립검수 = `STEP_C_INCONCLUSIVE` ⇒ lap466의 `RIDER_REPRO` REJECT.** 원시 3종만으로 비참조 재계산(`recheck467.py`): lap466이 고친 축은 확인됐다 — producer는 `ok:true`인 `op6 type46`(slot1182·id132254), 양성대조는 tick10 `reserved=0`→tick11 `10` 발화 후 417표본의 **유일한 전이**가 tick708 `(10,75,4)→(0,85,5)` 해소, cap 근접 주문도 **rice −800 과금**+`reserved`0→10이라 "주문이 큐에 안 들어갔을 가능성"(lap462 VOID 사유)은 배제됐고, 차량도 원본(pin 일치)에 `fixed_supply_5000.patched_bytes()`를 적용해 후보 SHA `0a1da226…` **재유도 일치**(바이트 차이 5개)로 stock1200+cap5000 확정. **그러나 판정은 성립하지 않는다:** 양성대조 해소지연 **L=698 tick**(주문10→해소708) 대비 cap 근접 관찰창은 **W=322 tick**(주문713→마지막1,035)뿐 = **W/L 0.461** ⇒ "전구간 `reserved=10`"은 고착과 정상 미완료를 **구분하지 못한다**(N96 확인, 697→**698** 정정). **N97(신규·결정적):** tick1,035의 producer는 **`command:15, progress:46, production_type:7`** — 같은 run에서 `progress`는 유휴0(tick8)·완료100(tick708)으로 의미가 고정돼 있으므로 **46은 창 끝에서 생산이 진행 중**이었다는 뜻이고, 속도도 양성대조와 같다(0.143266/tick×322=**46.13** 예측 vs **46** 실측, 완료 예정 tick1,411보다 **376 tick 일찍** 관측 종료) ⇒ 원시 증거는 `RIDER_REPRO`를 **지지하지 않으며** `RIDER_NO_REPRO`도 아니다. 무효인 것은 lap466의 절차가 아니라 **카드 §5-4의 `≥300 tick` 창 기준**(lap461이 L을 모른 채 쓴 값, N77과 같은 부류). ⇒ **Step C 2회 연속 무효 · W24 CLOSED 아님 · 144k 금지 유지 · lap404(가)는 번복도 확정도 없음**(이번 run은 (가)에 증거를 주지 않는다) · N93 미판별. lap467 게임실행0·source변경0·targeted11 passed·`SAFETY_PASS`·`CONTEXT_PASS`·커밋0. 전문 `20260922_lap467_middle_g2_w24_stepC_rerun_independent_review.md`·`ESCALATE_SOL`§41. **lap466(work) Step C 재실행 원문(보존):** `RIDER_REPRO` lap465가 VOID 처분한 Step C를 §40-2 두 필수조건으로 재실행: (a) **성공한 `op6 type46`**(cost20/w3/h3) 생산건물 producer(slot1182,id132254, `ok:true fixture_added:1`), (b) **양성 대조 선행** — owner0 저부하(`used=75`)에서 같은 producer에 `op1 type7`(cost10) 주문 → 417표본(0.05s)에서 `reserved`가 실제로 발화했다가 `used+10·reserved=0`으로 해소(producer 자체 `production_type:0→7,progress:0→100`으로 독립확증). 발화 확인 후 `op5 type5×142`로 `used=4985`까지 시딩(cap게이트 부분충족)하고 같은 producer(생존·소유 재확인)에 두 번째 `op1 type7` 주문 → tick714~1035 65표본 **전구간 `reserved=10`·`used=4985` 불변**, 해소 0건 ⇒ 카드 §5대로 **`RIDER_REPRO`**: lap412 기전이 stock 고유임이 이번엔 실제로 확증됐고 **lap404(가) 잠정채택이 유지**된다(lap462의 무효 Step C를 대체). Step A(`BUILDING_SEEDABLE`,대표t=46)·Step B(판정기 수리+음성대조 PASS)는 lap462 결과 재사용. Step D(`NO_ENGAGEMENT`, lap464 실행)는 lap465가 `ACCEPT`(불일치0, 역주입8건, 양성분기 `CYCLE_STABLE` 도달성 증명)했다 — 그때 무효였던 것은 Step C뿐이며 이번 lap466이 그 결손만 해소했다. 게임실행1(lap466)·source변경0(`runtime_bridge.c`/`control_executor.c` 실행전후 sha 동일)·원본 SHA 불변·targeted167 passed·`SAFETY_PASS`·`CONTEXT_PASS`·커밋0. **(그 "다음 middle 독립검수"가 위 lap467이며 결과는 REJECT다.)** N91~N95(C3전용 55슬롯 원본생산 오귀속 정정·type7→23 제자리전이17건·reserved10고정 아님·§7 사다리 비전역·P_max 계산차)는 유효한 채 보존. lap462~465 전문 계보는 `docs/history/20260922_status_lap466_precompaction.md`(SHA 54fe8841b378e7ff4b99d161d52b39c631217f2d64b0839816270c3bb3f2f7db, 130줄)와 개별 `docs/history/laps/20260921_lap462_*.md`~`20260922_lap465_*.md`에 그대로 보존. ·제품 미완료(부분 증거. W24는 A/B/D만 유효 판정, **C는 lap462·lap466 2회 연속 무효**라 CLOSED 아님) |
| G3 | 사용자 지시로 중단·활성 범위 제외 | 16 PlayerStruct가 bulk save112,036B 초과, self/opponent mask8bit라 owner8~15 표현 불가; 활성9~16/LAN 미완료 |
| G4 | 원본 issuer 국소 이동 PASS·제품 미완료 | 직접 command 기록은 정지; mainthread 원본 issuer는 같은 source 이동68좌표. current waypoint reinforcement 수리 후 AI2기 이동21/22좌표·목표gap2/1 PASS; one-shot2회 같은 이동 결과, 발행tick다름·지속 정책/품질 미검증; 이번정상AI512+load11 관측만PASS/정확postload미확정 |
## 다음 한 가지
**lap467(middle)이 N96 지시대로 lap466 Step C 원시 3종을 비참조 재계산해 `RIDER_REPRO`를 REJECT**했다(판정 `STEP_C_INCONCLUSIVE`, 근거·수치는 위 G2 표와 「검증 상태」). N96은 확인됐고(L=698 tick 대비 창 W=322, W/L 0.461), **N97로 결정적 보강** — 창 끝 producer가 `progress:46`(유휴0·완료100 사이)이라 **정상 생산 진행 중**이었고 속도도 양성대조와 동일. ⇒ **W24 CLOSED·144k 해제·lap404(가) 재심 종결은 전부 판정하지 않는다.**
**다음 한 가지: work 회차가 W24 §5 Step C를 3회차로 재실행**한다(새 카드 금지, §5 라벨 유지). 실행 **전에** 코드로 고정할 것: (i) **관찰창 ≥3×L**, L은 그 run의 양성대조로 **다시 측정**(2,094를 상수로 박지 않는다), (ii) **producer 주기 질의(op0)로 `(command,progress,production_type)` 시계열** — 장부만으로는 고착/진행 구분 불가가 이번에 확인됐다; 판별식은 `progress` 100 도달+`reserved` 해소 ⇒ `RIDER_NO_REPRO`, `progress`가 **≥L tick 정체**한 채 `reserved` 잔존 ⇒ `RIDER_REPRO`, 창 종료 시 **여전히 증가 중** ⇒ 판정 금지·창 부족 정직 보고, (iii) lap466의 (a)성공한 op6 type46·(b)양성대조 선행은 유지, 우회 패치·AI/생산 정책 변경 금지. **(ㄴ)·lap404(가)/(나)·F4(B)/(C)·3단 사용자 마일스톤 승인은 여전히 사용자 전권 대기**, 모델 착수 금지. 상세 `20260922_lap467_middle_g2_w24_stepC_rerun_independent_review.md`·`ESCALATE_SOL`§41(lap466 원문은 `20260922_lap466_work_g2_w24_stepC_rerun.md`·§40). lap462~465 계보(압축, 전문 보존)는 위 G2 표 항목과 `docs/history/20260922_status_lap466_precompaction.md`(SHA 54fe8841b378e7ff4b99d161d52b39c631217f2d64b0839816270c3bb3f2f7db, 130줄)를 참조.
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
**2026-09-22 lap467(middle) — lap466 Step C 독립검수 = `STEP_C_INCONCLUSIVE`(REJECT).** 판정 입력은
lap466 원시 3종뿐(`positive_control_samples.json` `afca96ca…272e0a06`·`step_c_samples.json`
`da39a97c…aad3ddc2`·`step_c_run_summary.json` `5beb90ed…192c9b81b`)이고 lap466 서술·STATUS/INBOX
요약은 제외했다. **확인된 것:** producer는 성공한 `op6 type46`, 양성대조는 tick10 발화→tick708 해소
(417표본의 유일한 전이), cap 근접 주문도 rice −800 과금되어 큐 진입 확정, 차량은 원본 pin에
`fixed_supply_5000.patched_bytes()`를 적용해 후보 SHA `0a1da226…` **재유도 일치**(5바이트 차이).
**무효 사유:** **L=698 tick vs W=322 tick(W/L 0.461)** ⇒ 미해소는 고착의 증거가 아니다(N96 확인,
697→698 정정). **N97:** tick1,035 producer `command:15,progress:46,production_type:7` ⇒ 창 끝에서
**생산 진행 중**이며 속도도 양성대조와 동일(0.143266/tick×322=46.13 예측 vs 46 실측, 완료 예정
tick1,411보다 376 tick 일찍 종료). 카드 §5-4 `≥300 tick` 기준 자체가 무판별(N77 부류)이며
lap466의 절차는 옳았다. ⇒ **W24 CLOSED 아님·144k 금지 유지·lap404(가) 번복도 확정도 없음·N93
미판별.** 게임실행0·source변경0·targeted11 passed·`SAFETY_PASS`·`CONTEXT_PASS`·원본 직접 재해시
`b56986e0…c9c08a8ac` 불변·커밋0. 재계산 산출물
`temp/Syw2plus_patch/g2_capacity/20260922_lap467_middle_stepC_recheck/`(`recheck467.py`·
`recheck467_output.json`). 전문 `20260922_lap467_middle_g2_w24_stepC_rerun_independent_review.md`.
**2026-09-22 lap466(work) — W24 Step C 재실행 `RIDER_REPRO`(위 lap467이 REJECT, 원문 보존).** 성공한 `op6 type46`(cost20/w3/h3)
producer(slot1182,id132254,`ok:true fixture_added:1`) 배치 후 owner0 저부하(`used=75`)에서 같은
producer에 `op1 type7`(cost10) 양성대조 주문 → 417표본(0.05s)에서 `reserved` 실제 발화 후
`used+10·reserved=0`으로 해소(producer `production_type:0→7,progress:0→100`으로 독립확증) →
`op5 type5×142`로 `used=4985`까지 시딩(cap게이트 부분충족) → 같은 producer(생존·소유 재확인)에
두 번째 `op1 type7` 주문 → tick714~1035 65표본 **전구간 `reserved=10`·`used=4985` 불변**, 해소
0건 ⇒ 카드 §5대로 **`RIDER_REPRO`**(lap404(가) 확정, lap462 Step C `VOID`를 대체). 게임실행1·
source변경0(`runtime_bridge.c`/`control_executor.c` 실행전후 sha 동일)·원본 SHA
`b56986e0…c9c08a8ac` 불변·targeted167 passed·`SAFETY_PASS`·`CONTEXT_PASS`·잔류 wine/Xvfb0·
커밋0. 상세 `20260922_lap466_work_g2_w24_stepC_rerun.md`+`w24_step_c_rerun.md`.
**lap462~465 계보(압축, 전문 보존):** lap462 Step A/B PASS(대표t=46, 판정기 수리)+Step C(당시)
`RIDER_NO_REPRO`(producer가 실패한 op6 잔여 type7이라 이후 VOID) → lap463 work가 allow-list
{5,7}→{5,7,46} 변경 후 게이트를 background로 띄우고 종료해 FAIL(INBOX 01:01 위반, N90) →
middle이 게이트만 회수(791 passed) → lap464가 N90 수리(796 passed)+Step D 실행 `NO_ENGAGEMENT`
자기판정 → lap465 middle이 원시 715표본+census 3종 재계산으로 Step D **ACCEPT**(역주입8건,
양성분기 `CYCLE_STABLE` 도달성 증명, D=12/R=0)하되 Step C만 **VOID** 처분(N91~N95: C3전용
55슬롯 원본생산 오귀속 정정·type7→23 제자리전이17건·reserved10고정 아님·§7 사다리 비전역·
P_max 계산차) → lap466(위)이 그 Step C 결손을 해소. 전문 각 `20260921_lap462_*.md`~
`20260922_lap465_*.md`, 압축 직전 STATUS 전문은 `docs/history/20260922_status_lap466_precompaction.md`
(SHA 54fe8841b378e7ff4b99d161d52b39c631217f2d64b0839816270c3bb3f2f7db, 130줄)에 보존.
**2026-09-21 lap461(middle) W24 발행 + 전투 축 실측 정정 N87~N89**(전문 `20260921_lap461_middle_g2_w24_issue_and_combat_axis_finding.md`·`ESCALATE_SOL`§39): lap460 §38이 인용한 수치를 서술이 아니라 원시 `recheck459_output.json` 직접 재독으로 대조해 **불일치0**(`U_min24`1,035/owner1/tick24,012·`U_min8`661/owner5·`r_late`0.008746719980007497·`r_need`0.033041666666666664·`DECAYED`·무결성 전부0·`min_rice`967,672). **N87(결정적, W24 설계를 바꿨다): "앵커를 붙이면 싸운다"는 레버는 이미 소진됐다** — lap451의 "앵커 8개 전부 disjoint"는 앵커 *좌표*가 다르다는 뜻이지 *배치 범위* 분리가 아니다. `runtime_bridge.c:200-205`가 앵커 셀부터 맵 전체를 선형 주사하므로 lap448 receipt의 `anchor`+`fixture_attempts`로 재계산한 주사 구간(0:202‥381·1:227‥573·2:252‥777·3:277‥934·4:5202‥5363·5:5227‥5604·6:5252‥5760·7:5277‥5930)은 **전 쌍에서 겹친다**(0-1 155·1-2 322·**2-3 501**·5-6 353·**6-7 484**셀). 적 유닛이 셀 단위로 뒤섞여 24,000tick 인접했는데도 owner `count` 감소 표본은 **단 2건**(tick10,587, owner0 152→150·owner1 154→152) = **소실 4기/1,166기/24k** ⇒ 전투/사망/재사용 축은 **기하로 만들 수 없고**, 남은 fixture 내 가설은 **구성(타입)** 뿐이며 그것도 실패하면 정답은 `NO_ENGAGEMENT`이고 **(ㄴ)이 유일한 진입로**라는 보고다(모델은 그 경우에도 AI 변경 착수 금지). **N88:** 타입표 `0x9B5238`은 `.data` raw끝 `0x4F9000` 바깥 BSS라 정적 목록 획득이 원리적으로 불가하고 `runtime_bridge.c:177`이 시딩 타입을 type5/type7로 하드코딩하나, 필드 오프셋은 소스로 확정(cost`+0x00`·width`+0x06`·height`+0x08`·flags`+0x14`)이고 샘플러가 게임 메모리를 직접 읽으므로 **PS3 진입 후 `0x9B5238+t*0x394`(t=0..199) 읽기만으로 전 타입 인벤토리 획득 가능**(DLL변경·새 op 불필요) ⇒ W24 Step A. `(flags&14)!=0`·width/height 1..8 가드는 의미 미상이므로 **완화 금지**, 건물이 걸리면 `BUILDING_BLOCKED` 보고. **N89:** lap404 rider 차량·수단은 이미 저장소에 있다 — `patches/population/fixed_supply_5000.py`(원본 2곳·길이불변 편집 ⇒ stock1200+cap5000; `0x3FFD4`는 `add eax,0x5DC`→`mov eax,0x1388`으로 **opcode도 바뀜**)와 **op1**(`:137-147`, 원본 `0x4AF5E0` Train, op4 아님) ⇒ 새 패치 모듈 금지. lap461 게임실행0·source변경0(N22)·targeted17 passed·`SAFETY_PASS`·`CONTEXT_PASS`·원본 직접 재해시 `b56986e0…c9c08a8ac` 불변·커밋0. **발행은 계획이며 제품 완료·마일스톤 승인이 아니다.**
**lap356~459 계보(압축, 이 절이 「바퀴 기록」 절과 중복이라 여기서 접는다 — 전문은 「바퀴 기록」의
같은 lap 번호 요약과 각 원 lap 기록, 그리고 이번 lap464 precompaction 스냅샷
`docs/history/20260922_status_lap464_precompaction.md`(SHA
`0e1a3301496540486180bad64cdbc6c9ef872fddb63e4ff56f3e8f946772c690`, 151줄)에 그대로 있다.
삭제·재해석 없음, 표시만 축소):** lap458(work) W23 A1 24k = `DECAYED` 등(전문 위 SHA 스냅샷·바퀴 기록 참조).
## 바퀴 기록
lap467(middle) lap466 Step C 독립검수 **REJECT = `STEP_C_INCONCLUSIVE`**(N96 확인 L698/W322,
신규 **N97** 창 끝 `progress:46` = 정상 생산 진행 중; W24 CLOSED 아님·144k 금지 유지, 위 검증
상태 참조). 게임실행0·제품코드0·커밋0. 전문
`20260922_lap467_middle_g2_w24_stepC_rerun_independent_review.md`·`ESCALATE_SOL`§41.
lap466(work) W24 Step C 재실행 **`RIDER_REPRO`**(성공한 op6 생산건물 producer + 양성대조 선행
발화·해소 확인 후 cap근접 65표본 전구간 reserved=10 불변, 위 검증 상태 참조). 게임실행1·
source변경0·커밋0. 전문 `20260922_lap466_work_g2_w24_stepC_rerun.md`.
lap465(middle) Step D 독립검수 **ACCEPT(불일치0)** + Step C **VOID**(lap466이 대체) + N91~N95
(위 검증 상태 참조). 게임실행0·제품코드0·커밋0. 전문
`20260922_lap465_middle_g2_w24_stepD_independent_review.md`·`ESCALATE_SOL`§40.
lap464(work) N90 핀테스트+Step D 실행 = `NO_ENGAGEMENT`(위 검증 상태 참조). 전문
`20260922_lap464_work_g2_w24_stepD_no_engagement.md`.
lap462(work) W24 Step A/B/C 실행(수치·판정 전문은 위 G2 표에 그대로 있다): Step A `BUILDING_SEEDABLE`(게임1회, 대표 t=46) → Step B `compute_verdict461.py` 신설(게임0, 음성대조2건 발화확인) → Step C `fixed_supply_5000.py` 차량으로 lap404 rider 실행(게임1회) = `RIDER_NO_REPRO`. Step D는 §9에 따라 다음 회차로 이월(재계획 아님). 게임실행2·source변경0·원본/`control_executor.c` 재해시 불변·커밋0. 전문 `20260921_lap462_work_g2_w24_stepABC.md`.
lap456~459(수치·판정 전문은 위 「검증 상태」 첫 단락과 G2 표에 그대로 있다): lap456 work가 W22
6 arm 실행해 `PARTIAL` 자기판정(게임실행6·source변경 N22 명시·`make check` 791 passed) → lap457
middle이 비참조 `recheck457.py`로 **ACCEPT(불일치0)**·**N77**(카드 `r_slow`는 baseline도 통과 ⇒
무판별)·N78~N80 발행 후 **W23 발행**(A1 1 arm 24k, 판정식을 후반증가율로 교체) → lap458 work가
W23 A1을 tick24,012까지 실행해 **`DECAYED`** 자기판정(게임실행1·source변경0) → lap459 middle이
lap458 서술/`compute_verdict458.py`/`run_summary.json`을 판정 입력에서 빼고 원시721표본+
`fingerprint.json`+실행 전 고정 판정식만으로 `recheck459.py` 재계산해 **ACCEPT(불일치0)**·
**N81~N86** 발행, 마일스톤 경계라 **카드 발행 없이** §37로 strategy/사용자 판정 요청.
전문 각 `20260921_lap45{6,7,8,9}_*.md`, `ESCALATE_SOL`§35~§37. → lap460 strategy(Fable5)가 §38로 5건 처분((ㄱ)채택·(ㄴ)사용자대기·lap404(가)잠정·F4(C)·W24 지시), 게임실행0·source변경0·targeted7·`SAFETY_PASS`·커밋0, 전문 `20260921_lap460_strategy_g2_evidence_axis_judgment.md`. → lap461 middle이 §38 인용 수치를 원시 재독으로 재확인(불일치0)하고 **W24 발행**(SHA `66441185…1171142`, 의무5건 반영) + **N87~N89**(전투 축은 기하로 불가·타입표 런타임 인벤토리 경로·rider 차량 기존 자산), 게임실행0·source변경0·targeted17 passed·`SAFETY_PASS`·원본불변·커밋0, 전문 `20260921_lap461_middle_g2_w24_issue_and_combat_axis_finding.md`·`ESCALATE_SOL`§39.
**lap452~455 W21 Step2·W22 발행 계보(lap465 압축 — 삭제·재해석 없이 표시만 축소, 전문은 위 SHA
`ae945859…641ec3b4` 스냅샷과 각 `20260921_lap45{2,3,4,5}_*.md`·`ESCALATE_SOL`§32-4/§34, 수치는
위 「검증 상태」 첫 단락과 G2 표에 그대로):** lap452 work가 저장/로드 왕복 실행해 (U5) 자기판정
PASS+N69/N70 정정+N65 수리+(U4) smaps_rollup 이행(게임실행1) → lap453 middle이 비참조
`recheck453.py`로 **(U5) ACCEPT(불일치0)**·**W21 카드 CLOSED 판정**((U0)~(U3) PASS·(U4) PARTIAL·
(U5) PASS, 전 Step이 실행자와 다른 middle에게 검수됨)+N71~N76, 마일스톤 경계라 카드 없이 §32로
strategy 판정 요청 → lap454 strategy가 W21 CLOSED 재확인(lap452 스팟체크 불일치0) → lap455 middle이
**W22 발행**하며 게임실행0으로 확정 4건 박음(난이도 레버 부재·자원 이미 포화·시드고정시 결정적·
baseline은 감속). lap452만 게임실행1, 나머지 0·source변경0(N22)·targeted passed·`SAFETY_PASS`·
원본 직접 재해시 불변·커밋0.
**lap441~451 W19~W21 계보(lap465 압축 — 삭제·재해석 없이 표시만 축소. 압축 직전 STATUS 전문은
`docs/history/20260922_status_lap465_precompaction.md` SHA
`ae9458593aa11119cd0109cc8381114158f4b6e91385d244910448ae641ec3b4`, 142줄에 보존했고, 각 전문은
`20260921_lap44{1,3,4,5,6,7,9}_*.md`·`20260921_lap45{0,1}_*.md`와 위 「검증 상태」 동일 lap 항목에
그대로 있다. lap442·448은 자체 lap기록 없음 — N64):** lap441 **ACCEPT((R1))**+W20발행 → lap442 work
실행 → lap443 비참조 **(T2) ACCEPT(불일치0)**(24k 도달이나 **전비5000 도달불가**, N55~N57+절차결함
N58로 strategy 판정요청) → lap444 strategy가 721표본 직접 재확인 후 **(나) 시딩 선행·(가) 합격경로**
확정(`G2_STRATEGY_FIXTURE_SCOPE_LAP444.md`) → lap445 **`recheck445.py` ACCEPT**+**W21 발행**(판정식
(U0)~(U5) 실행 전 고정, N56 소스 한 줄 귀속·N57 정정) → lap446 **(U0) PASS** → lap447 **ACCEPT**
+N59~N63 → lap448 Step1 24k soak `CAP_PROXIMITY_STABLE` → lap449 712표본 **ACCEPT**(U1~U3 PASS·
U4 PARTIAL)+N64~N68 → lap450 Step3 대조표 `lap413_stock_comparison.md` 발행 → lap451 **ACCEPT(15셀
중 14셀)**·**N66 CLOSED**·N69(도달 tick 23,997→**24,030**, 계측버그·판정불변)·N70·**N65 미수리
재확인**+Step2 착수조건 3건 handoff. 게임실행은 lap442·446·448뿐, 전 회차 제품코드/커밋0·source미변경(N22)·targeted passed·`SAFETY_PASS`·원본 직접 재해시 불변.
lap417~440 W10~W19 계보 + lap397~413 계보(압축, 위 「검증 상태」 항목들과 동일 — 전문 각
`20260921_lap4{17..40}_*.md`·`20260920_lap{397..413}_*.md`): 정적표면측정→FO closure→재배치구현→
커버리지REJECT/ACCEPT→W6/W7→P1→W8soak ACCEPT→P2원본생산FAIL→정적인벤토리→**H1기각**→P-D→
**H2 ACCEPT**→H5확정/H6기각→19,679유일해ACCEPT→W13 P-G→W14 CLOSED→P-J→(J2)확정·N40(J3)강등→
디스크로probe만→P-K/P-L→**ACCEPT**+(K2)N44강등→재확인ACCEPT+N46+판정식수리→(i)계속판정→
**(L3)정지**→ACCEPT+C1+N48→**(L2)확정**·W18허용→3차재확인ACCEPT+C2+N49·N50+W18발행→
(M1)ACCEPT+**N51로근본원인확정**((J2)/(J3)/(K2) REJECT)+W19발행→W19 Step1~4실행. 게임실행은
lap419·421·423·425·427·430·434·438·440, 전 회차 제품코드/커밋 전부0.
lap389~395 cap조사 계보(압축, 요약은 위 「검증 상태」 lap388~395 항목과 동일 — 개별 lap 판정/STOP 사유는 각 원문 파일 `20260919_lap389_*.md`/`20260920_lap39{0,1,3,4,5}_*.md`에 보존): lap389 NO_GO+F4발견→lap390 NOT_FEASIBLE(fixture한정)→lap391 ACCEPT+STOP(F4기준 판정대기)→lap392 Astra BLOCKED→lap393 cap≤4095 산출+STOP(목표숫자 변경권한없음)→lap394 Astra 반례제기→lap395 반례ACCEPT+**4095도 무효, 안전상한 UNKNOWN 확정**, W2 카드 인계(이후 우선순위변경으로 lap396 안전종료). `ESCALATE_SOL` §5~§10 전부 열려있음(닫힌 것 없음, 철회 없음).
**lap380~388 G2 레이아웃 카드 계보(압축, 전문 `docs/history/laps/20260918_lap38{0..8}_*.md`, 압축전 STATUS `20260920_status_lap391_precompaction.md` SHA `d168c947…eed7abb6`/135줄):** lap380계획→lap381 C1/H1 CLOSED→lap382work→lap383middle REJECT→lap384work수리→lap385middle ACCEPT→lap386~387work→lap388middle ACCEPT·**레이아웃 카드 종결**(재수리 없음). 전회차`make check`rc0+`SAFETY_PASS`, 원본/frozen불변, 게임실행/커밋0. `native_route_judgment`NO_GO 미변경. 종결리포트`docs/reports/20260918_G2_LAYOUT_CARD_CLOSURE.md`. 상위 통합blocker는 위「지금 막힌 것」에 그대로 살아있음.
lap377 Astra 방향 → lap378 middle ACCEPT → lap379 provenance BLOCKED 뒤 사용자 product-first 지시로 반복 중단. lap356~376 상세(import 해소·§3 RELEASE, REJECT/수리 반복, 게임/커밋 0회)는 각 lap 기록과 `20260912_status_lap361_entry.md`(SHA/124줄)에 보존.
