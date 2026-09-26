# STATUS — 매 바퀴 갱신하는 기억
## 지금 상태
활성 G1/G2/G4 제품 미완료(0/3); G3 최대16인은 2026-09-17 사용자 지시로 중단. **G2 최우선·9/18 Claude Code 역할로 재개 승인**; **2026-09-21 00:20 지시로 G1/G4는 G2 성립 전까지 잠정 중단, G3는 계속 포기 범위로 고정**(G1/G4 표 항목은 과거 증거 보존일 뿐 현재 작업 대상 아님). M1/G1 요구 유지: 원본 구도·입력과 차후 고해상도 그림의 디테일 보존을 함께 만족하는1600×1200 화면. 제품 기준은 DESIGN, 사람 승인
원문은 feedback/APPROVALS·INBOX를 따르며 2026-09-12 01:03 bounded repair→fresh validation 허가는 제품/출시 승인이 아니다. DxWrapper 2× 화면·S1 입력쌍은 배치 프리뷰 근거만; 추가 디테일 보존 경로와 WM_CLOSE 결함은 남았다.
과거 G1/lap275~379 승인·반려·미결 계보는 전체 원문 `20260917_234449_status_pre_cutoff_compaction.md`(SHA 9400241176cce4bbe0047b358a887f09e269d9824a253654d6ff2718d352ddef,141줄)에 보존했으며 fresh 제품 PASS/출시 승인으로 승격하지 않는다. lap401 자기 편집 전 142줄본은 `20260920_status_lap401_precompaction.md`(SHA 99e9c54e73dde10cdca20bb49525cfd74a0af372d209f700d0bf33491dd492e9)에 보존(내용 동일, 단락 줄바꿈만 압축). lap412가 136줄에서 압축하기 직전 전체 원문은 `20260920_status_lap412_precompaction.md`(SHA fcfae74298ce8c62b820d0d6587516633380b54e1931116fd5f1c34ce670a07f, 136줄)에 보존했으며, 압축 대상은 lap409·lap410 두 항목뿐이고 각 lap 원문 파일에 전문이 그대로 남아 있다. lap414가 압축하기 직전 전체 원문은 `20260921_status_lap414_precompaction.md`(SHA 878f23ce08d1787ce06a4003b9a0dfda3e95fd3fd85cac9bfc4026073dc0f804, 125줄)에 보존했으며, 압축 대상은 lap411·lap412 두 항목뿐이고 각 lap 원문 파일에 전문이 그대로 남아 있다.
| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | native PS3 PASS·원본구도 FAIL·제품 미완료 | stock UI 클릭 PS9→PS7→PS5→PS3 tick3, native `1600×1200×8bpp/pitch1600`/viewport 전역 PASS; 월드 시야 확대·스프라이트/HUD 원본 픽셀 크기라 G1 배치 FAIL, 고해상도 SPR·생산·종료 미검증; 이번최종acquisition은초기화guard8000001A에BLOCKED |
| G2 | **P2 원본생산/AI 경로 FAIL(lap414 독립검수 ACCEPT)**·W8 lap412 ACCEPT·제품 미완료 | lap413에서 op=6 없이 원본 Train`0x4AF5E0`으로 owner0 worker가 slot3951에 생성(used20→30)되어 원본 생산·확장slot 소비는 성립. 그러나 resource-only fixture(원본 SetResource만, 장부/유닛 write0)로 7 AI를 돌린 N=4001 marked compat(`4331d9cd…`)가 **두 신규 prefix 모두 정확히 tick11,928/live468/owner5 used1208에서 `0x00414133` read page fault(`0x00338400`)**로 죽음. stock-layout supply5000 대조군(`0a1da…`)은 tick11,928을 통과해 13,116/live405까지 page fault 없이 진행 후 match 종료성 정지. 따라서 진단시딩 4,000기 W8 PASS를 일반 생산·전투 안정성으로 승격 불가. P2 FAIL, 다음은 fault 선행 손상 root-cause. W8 자체 ACCEPT·strict-cap caveat는 유지. 상세 `20260920_lap413_work_g2_original_production_failure.md`. |
| G3 | 사용자 지시로 중단·활성 범위 제외 | 16 PlayerStruct가 bulk save112,036B 초과, self/opponent mask8bit라 owner8~15 표현 불가; 활성9~16/LAN 미완료 |
| G4 | 원본 issuer 국소 이동 PASS·제품 미완료 | 직접 command 기록은 정지; mainthread 원본 issuer는 같은 source 이동68좌표. current waypoint reinforcement 수리 후 AI2기 이동21/22좌표·목표gap2/1 PASS; one-shot2회 같은 이동 결과, 발행tick다름·지속 정책/품질 미검증; 이번정상AI512+load11 관측만PASS/정확postload미확정 |
## 다음 한 가지
**work(Sonnet5/high)가 `0x00422dc0`(슬롯당 `FUN_0048aff0`→`FUN_004119f0`, 재배치된 풀에서 1200회만 순회)의
실제 호출 경로를 동적으로 확인한다** — 정적 스캔으로는 호출/주소참조 0건이라 실행 중 이 코드가 도달되는지,
얼마나 자주(틱마다인지) 도는지가 미확정이다. 방법 예: Wine 디버거 브레이크포인트나 계측 프로브로
`0x00422dc0` 진입 여부·빈도를 op7/7AI 동일 fixture에서 관측한다. 도달이 **확인되면** 그때 P-C로
`edi`(0x004183c7 근방, 즉치 0x4B0)를 이미 패치된 두 자매 site(`0x00441441`/`0x0044317d`)와 같은 방식으로
0xFA1로 최소 수리하고 동일 fixture로 재실행한다. **도달하지 않으면** H1의 이 경로는 기각하고 나머지 미해결
가설(포인터/stale 수명주기, H2)로 넘어간다 — 다른 두 후보(회전커서/선형커서)는 lap417이 이미 배제했다.
PASS는 tick11,928 통과 + page fault 0건이며 `used≥4900`은 이 카드 조건이 아니다(W9로 복귀할 다음 카드).
fault 명령(`0x00414133`) 자체는 원본과 바이트 동일하므로 패치 금지. **신규(lap417):** `+0x692` 이상은 매치
내내 0이다가 tick~11,900대에 **돌발** 발생하며(서서히 drift 아님), 이는 wild write/카운터 임계 통과형
사건에 더 부합하고 "느린 lifecycle 누락으로 인한 drift" 가설과는 덜 맞는다 — 다음 조사는 이 시간창을
좁히는 방향을 우선한다. P2 near-cap 조건은 FAIL이며 기준을 낮추지 않는다.
## 지금 막힌 것 (Blockers)
- **F4(lap395 확정): 안전상한 UNKNOWN — 어떤 uniform cap도 랩을 막지 못한다.** lap394 반례 독립 재현 ACCEPT(12001/32761/40001 일치); lap393 P9의 assertion은 `32767//8` 상수 산술 2개뿐이라 불변식 산문을 인증하지 않는다. **신규:** 생산 gate `0x43EDA0`은 count cap `+0x2010`·supply cap `+0x2012`를 둘 다 강제하나 `roster_add 0x43EE30`은 `cmp ax,0x4B0`(배열1200)뿐이고 두 cap 참조 **0건** ⇒ 이전은 두 cap을 모두 우회. donor 이전+gate-legal 재생산 **펌프**로 수신 used가 cap 1500/4095/5000 **전부에서 32,785 도달**(차이는 재생산 799/87/7회뿐) ⇒ **cap≤4095 안전상한·§7.6 분기 A 전제 무효, 즉치2개 카드 착수 근거 상실**. cap5000은 펌프 없이 이전만으로도 1160기/40,000 집중 가능(1160≤1200). 남은 상한 `min(1200,풀)×최대비용`은 손익분기 평균 27.31 vs 실측 평균 31.66~34.42 ⇒ 37,988~41,309>32,767로 **구제 실패·cap 비의존**. 최대 단위비용은 비용표 `0x9B5238`/type표 `0x66B81D`가 `.data` raw끝 `0x4F9000` 바깥 BSS라 **정적 불가**(W2가 실측). P1~P4 바이트 사실·lap389 NO_GO·lap391 수치는 유지. 실제 게임 도달성 UNKNOWN.
- **현재 G2 구조통합 blocker:** 저비용 다수 구성의global1199/ordinaryowner242 확장에 필요한 Unit·보조 인덱스·bulk-relative alias·초기화/수명주기·저장/LAN의 일관 계약 미구현. 두 actual 진단은局所getter追加로 정상simulation에 도달하지 못함. 개별PC따라 패치 반복중단; 제품완료/전체불가능 선언없음. **lap381이 닫은 것은 layout 선행질문(C1 count폭·H1 matrix형태)뿐이며 이 통합 blocker는 그대로다.** **lap385 신규 실측(Astra 큐, 승인대기·작업은 계속함):** 핀된 save`0x440F02`(len`0xE397C`,src`0x892410`)/load`0x4412DC`가 정의하는 bulk blob `[0x892410,0x975D8C)`이 existence/age/catA/catB/active **5개 영역을 내부에 품는다**(unit_pool만 bulk 아래, 별도 roster). ⇒ 확장은 `0x892410`을 slot당1,880B 밀어올리는 **동시에** 고정길이 blob 내부를 slot당14B 불린다(N=4001→새 start`0xD97DE8`/필요 len`0xED2AA`); 둘 다 하드코딩 push 즉시값이라 **layout mapper만으로 저장호환 확장은 원리적으로 불가**하고 길이·주소 즉시값 fixup+저장포맷 변경이 필수다. lap379 Sol의 integration/broad-patcher/runtime NO-GO를 **뒤집지 않고 강화**한다. **새 불가능 증명 아님** — G2를 이 경로로 계속할지는 Astra 판정 사항. **lap388 종결:** 레이아웃 계산기 카드는 ACCEPT·계약5 CLOSED로 닫혔으나 이 통합 blocker는 **그대로다** — 오히려 "길이·주소 두 하드코딩 즉시값 fixup+저장포맷 변경 필수"를 수치로 굳혔다(`loop/ESCALATE_SOL` 판정 대기). **lap397 범위 정정(무효화 아님):** 이 통합 blocker는 owner당 1200기 초과와 저장호환에만 걸리며 **풀 확장 스파이크의 임계경로가 아니다** — `roster_add`의 `cmp ax,0x4B0`은 owner 유닛 **개수** 제한이고(`0xD4A+1200*4==0x200A` 검증), 유닛 1200기 미만 owner는 PlayerStruct 무변경으로 slot id≥1200을 담는다.
- **G4 persistent STOP:** 비지원 mode 제외와 post-load 첫 tick/중복 계약 미확정(`BLOCKED_MODE_EXCLUSION_AND_POSTLOAD_CONTRACT`); normalcall/owner/serializer·one-shot2회 이동과 이번shadow512+load11만 보존(정확load완료marker없음). **과거 lap379 provenance:** test pre-image SHA 충돌은 역사 검증 UNKNOWN으로 보존하되 fresh 현행 SHA의 제품 실행을 차단하지 않는다. 재핀·자가 baseline 승격은 계속 금지한다.
- **과거 G4 fresh AI runtime 실패(보존; 현재 chain 진입/180초 실행은 가능):** current bridge `592d03ec…0b3030`, old `f44090a3…adac4b`, ddraw override on/off 모두 PS40/tick0·동일 serious-error 이미지 `008e8465…6e3cd9`. 당시 bridge/renderer 두 가설 소진으로 반복 STOP한 기록; temp `Syw2plus_patch/g4_ai/`, residue0.
- **원본·후보 S1/화면·세 입력 PASS:** logical load-button `(316,372)` 1회로 PS35→PS3, 8 PlayerStruct 각각 save000과 일치. 원본800×600/후보1600×1200 PS35 실제 메뉴 캡처는 최근접 2배 뒤 **exact100%/MAE0**, PS3는 별도 쌍 exact99.213%/MAE0.470. 동일 source SHA fresh 미니맵 쌍 `(35,560)` camera `(39,53)→(49,159)`; 선택해제 쌍 `(400,220)` count `1→0`/first_slot `1174→0`; 드래그쌍 `(520,200)→(780,455)`은 clear0→count3/first_slot108 모두 동일. cleanup0잔류/후보 ini 원복. 첫 `(150,520)`은 원본 무효라 실패 보존. 생산·종료·장은 UNKNOWN.
- **G1 R1/S1 클릭·좌표·PS전이 포렌식 계보(lap279~339, 압축, 전문 보존):** G1은 사용자 지시로 후순위이며
  이 블록의 모든 결론(좌표계 해소·도달판정식·F1/R1/R2 종결·provenance 회귀 a~h·N1~N16·W2/W3 미결·
  exact-site 계측 금지·G3 저장포맷 공간부족·Plan C 함정)은 **전문 그대로**
  `docs/history/laps/20260920_status_lap409_precompaction.md`(이번 압축 직전 전체 원문, SHA
  `d99533e1b1dfbb1df30e89dd77094e200ac29c92e2d72b37c356f52f8e33cd7f`, 130줄)와 각 원 lap 기록
  (`20260910~20260920_lap{279..339}_*.md`)에 보존된다. 삭제나 재해석 없이 STATUS 표시만 축소했다.
  재참조가 필요하면 압축본을 먼저 읽는다.
## 검증 상태
**2026-09-21 lap417 work(Sonnet5/high) — W10 P-B 정적 site 인벤토리, 게임 미실행·제품코드/커밋 0, source 변경 0:**
**선행 provenance 결함(N29):** lap415(00:51, PID 오추정 FAIL)·lap416(01:10, run2 H1지지)는 INBOX에만 기록되고
`docs/history/laps/`·STATUS 갱신이 없다(N20과 같은 계열 — 미기록 회차). 이번 lap이 lap416 run2의
`samples.jsonl`(709줄, `temp/.../20260921_lap416_fault_root_cause_pa_run2/`)을 원시 재확인해 INBOX 주장과
**일치**를 확인했다(slot3565/type76/owner4, tick11,921 move=-6599→tick11,928 move=19579, lo밴드 이상0).
**P-B 결과:** 원본/후보 `.text`를 capstone로 직접 재빌드·재디스어셈블(원본 SHA·후보 SHA `4331d9cd…` 둘 다
바이트 재확인) — decoded-operand 0x4B0(1200) 즉치는 **36곳**이며 N27의 54는 byte-pattern 오탐 포함 수치였다
(N27 스스로 밝힌 `0x0104b010` 오탐과 같은 계열). 36곳 전수 분류: 2곳 이미 0xFA1 패치, 1곳은 owner개수 상한
(변경 금지), 26곳은 UI 다이얼로그(`0x49baa0`)/서피스(`0x4a8100`) 생성자 인자(push-arg만, 주소무관), 1곳은
맵/월드 오브젝트의 `this`-상대 1200-word 버퍼, 1곳은 x100 상수표 — 모두 풀과 무관. **남는 풀-경계 미패치
site 3곳(N27과 매칭)의 호출자를 정적 추적**: `0x004183a0`(회전 커서 검색)은 매치-설정1회(`0x0043ff8d`)와
UI범위 2곳뿐, `0x00444ef0`(선형 커서 조회)은 8개 호출자 전부 UI/입력 범위(`0x4be000~0x4c2000`) — **둘 다
op7/AI 전용·무입력 fixture에서 재실행 안 됨(사실상 배제)**. `0x00422dc0`(슬롯당 `0x48aff0`→`0x004119f0`
호출, 재배치된 풀 기준 1200회만)만 직접 call/주소 참조가 파일 어디서도 0건 — 호출 경로 **미해결**,
유일하게 배제 안 된 후보. **신규(onset 재분석, 새 게임 실행 없이 기존 샘플 재집계):** `bands.hi.max_abs`가
tick15~11,904까지 전 구간 **정확히 0**이다가 11,921(6599)→11,928(19579)로 급변 — 매치 내내 서서히 drift한
것이 아니라 tick~11,900대의 **돌발 이벤트**다. **판정: H1/H2 미확정, 단일 원인 미지목 — P-C(수리) 미착수**
(카드 규칙상 추측 수리 금지). targeted 6 passed, `SAFETY_PASS`, 원본 2경로 재해시 불변, 잔류0. 상세
`20260921_lap417_work_g2_pb_static_inventory.md`, 산출물 `temp/.../20260921_lap417_pb_site_inventory/`.
**2026-09-21 lap414 middle(Opus5/high) — lap413 P2 FAIL 독립 검수 ACCEPT(불일치 0), 게임 미실행·제품코드/커밋 0:**
요약 JSON을 쓰지 않고 원시(trace.jsonl·samples·receipts·wine.log·manifest·실행파일 재해시)만으로 재계산 —
후보 두 run 모두 tick11,928/live468/owner5 used1208·동일 fault `read 0x00338400 @ 0x00414133`, stock 대조는
fault 0건으로 tick13,116까지 진행. 실행 exe SHA를 직접 재계산해 후보/stock 신원 확인(동일 디렉터리 `game.exe`는
stock·미실행). op7 영수증 7건·21필드 장부 변화 0 ⇒ resource-only 계약 성립. targeted **6 passed**, `SAFETY_PASS`,
원본 2경로 불변. **이번 회차 source 변경 0이라 전체 `make check` 미재실행**(직전 lap413이 통합 경계에서 786).
**N25:** 두 run은 신규 prefix/브리지인데도 **공유 tick 46개 전부에서 owner별 used/count/reserved 일치**(불일치 0)
⇒ 상태 수준 결정성, tick bisect 유효. **N26:** `0x00414000`은 Bresenham 경로점 생성+샘플러이고 호출자는
`0x0040be55` 하나, fault는 100칸 stack 배열을 `edx=((점수-1)×|unit+0x692|)/100`로 읽는 지점이며 `+0x692`는
`0x0040bc86~0x0040bcff`가 누적하는 타일 이동 진행도(50에서 다음 타일·-100)라 정상 `edx≤99`. fault 지점 ±0x180은
원본·후보 **완전 동일** ⇒ 명령 패치 금지. **N27:** 후보는 `.text`의 `0x4B0`(1200) 즉치 **54곳 중 2곳만** 0xFA1로
바꿨고, 풀을 실제 순회하는 잔존 site 최소 3개 — `0x00422dc0`(base는 `0x66b790→0x0108c000` 재배치·`mov edi,0x4B0`
루프는 그대로 ⇒ 0~1199만 슬롯당 `0x48aff0` 처리), `0x004183a0`(필드4곳 재배치·`idiv 0x4B0`2·`cmp bx,0x4B0` 잔존),
`0x00444efe`(주소 즉치 없이 매니저 `0x61e36c` 경유 ⇒ **주소기반 fixup이 못 보는 부류**). 오탐 분류도 기록
(`0x004a8843/48` 표면1200×1200, `0x004c470f` 표, `0x00491911`/`0x004922b9`는 실제로 주소 `0x0104b010`).
`roster_add 0x0043ee39`의 `cmp ax,0x4B0`은 lap397대로 owner당 개수 상한이므로 **유지**. **N28:** 원본 할당기는
풀을 **위에서 아래로** 채운다 — 시작 시 후보 slot3985~4000 / stock 1184~1199, crash tick의 후보 live 468기는
**전부 3533~4000**이고 0~1199에는 0기(owner별 수는 엔진 `count`와 8/8 일치) ⇒ N27의 1200-bound 순회는 후보에서
**생존 유닛 0기 구간만** 훑는다. **정정1(무해):** 요약 JSON의 `driver_exit:0`은 원시 `exit.json`(세 run 모두 null)과
다르고, run1의 `stalled:null`도 탐지 임계값 artifact다(run1도 tick11,928에 9샘플 고정). 판정 불변.
**한계 유지:** stock 대조는 다른 바이너리·다른 풀 크기라 "그 tick의 일반 엔진 버그 아님"까지만 경계 짓는다. 상세 `20260921_lap414_middle_g2_p2_fail_independent_review.md`, 산출물 `temp/.../20260921_lap414_middle_review/`.
**2026-09-20 lap413 work — P2 원본생산 실제 실행 FAIL(lap414 독립검수 ACCEPT):** resource-only op7 AI로
N=4001 후보가 신규 prefix/bridge 2회 모두 tick11,928/live468/owner5 used1208에서 `0x00414133` fault 재현;
stock-layout supply5000은 fault0·tick13,116까지 진행. `make check`rc0 786 passed. 상세
`20260920_lap413_work_g2_original_production_failure.md`.
**2026-09-20 lap409~412 P1/W8 계보(압축, 전문 각 `20260920_lap409_work_*.md`/`20260920_lap410_middle_*.md`/
`20260920_lap411_work_*.md`/`20260920_lap412_middle_*.md`):** lap409 work가 marked compat `4331d9cd…`로
near-4000(3,991 live) 첫 실제 실행(왕복 무손실, STOCK1200 브리지 오사용 발견·수리)→lap410 middle **ACCEPT**
(로드 실재 tick 2328→1567 역행 증거, 정정1 presave~535tick 선행/정정2 배포DLL stub 1200 하드코딩)→lap411
work가 marked compat로 Δ24,180tick W8 soak 완주(live3993~4000, crash0, slot≥1200 reuse8)→lap412 middle
**ACCEPT**(불일치0, CPU정체 음성, 되물음1의 `5010`을 "해소되지 않는 예약"으로 기전 확정, N21~N24 발행).
전 회차 게임실행 있음(work 두 회)/제품모듈 변경0/커밋0, `make check`rc0+`SAFETY_PASS`.
**2026-09-20 lap397~408 G2 재배치·커버리지·런타임계보(압축, 전문 각 `20260920_lap{397,398,400,401,402,404,406,408}_*.md`):**
lap397 정적표면측정(제자리확장NOT_FEASIBLE·재배치FEASIBLE)→lap398 FO 3건PASS(fixup제외목록 확정)→
lap399 W3구현N=1210(work, 압축줄 하단)→lap400 middle REJECT(제자리성장 D1)→lap401 work꼬리재배치 신규
구현(`tail_relocation_storage_layout_v1`)→lap402 middle ACCEPT+신규D1(N=4001 섹션커버리지 99.24% 밖,
수리값 산출)→lap404 strategy 미검수 자칭lap410/412 계보 triage(N18, 큐 `G2_STRATEGY_DIRECTION_LAP404.md`)
→lap406 middle 독립검수 항목1/2/4/5 ACCEPT·항목3 게이트지시(W6, N19 "한tick" 서술 정정)→**lap408 middle
W6 CLOSED**(783=779+4, 역주입포착확인, 원본불변)+신규W7(`.rsrc` wrapper 컨테인먼트 사각)+N20(미기록
회차). 전 회차 게임실행/제품코드/커밋0(work인 397·398·401 제외 컨펌·전략 역할), `make check`rc0+
`SAFETY_PASS`+원본불변 매회 확인.
**lap388~395 G2 전비장부 cap 조사 계보(압축, lap398. 각 lap 기록 전문은 `docs/history/laps/20260919_lap389_*.md`~`20260920_lap395_*.md`에 보존):** lap389 owner-transfer 사전거부 NO_GO+신규F4(16bit장부/40,000합) 발견→lap390 W1 NOT_FEASIBLE(fixture한정)→lap391 ACCEPT+F4생존→lap392 Astra BLOCKED→lap393 cap≤4095 산출(이후 lap394 Astra 반례로 무효)→lap394 반례제기→lap395 반례ACCEPT+**4095도 무효, 안전상한 UNKNOWN 확정**(펌프로 세cap 전부 32,785 도달; cap5000은 펌프없이도 1160기/40,000으로 도달 가능). 전 회차 `make check` rc0 715 passed+`SAFETY_PASS`, 원본 불변, 제품코드/게임실행/커밋 **0**. `ESCALATE_SOL` §9로 열려있음(사용자 우선순위변경으로 후순위, 철회아님). lap397~398 풀확장 스파이크와는 독립 트랙.
**lap380~388 G2 레이아웃 카드 계보:** 개별 lap(380 C1/H1→381~383 REJECT/수리→384~387 수리/구현→388 ACCEPT
종결) 상세는 아래 「바퀴 기록」 압축 줄과 각 lap 원문(`docs/history/laps/20260918_lap38{0..8}_*.md`)에
보존. 전 회차 `make check` rc0+`SAFETY_PASS`, 원본/frozen 불변, 게임실행/커밋0.
**2026-09-15 product-first:** 원본·후보 실제 S1 load·PS35 메뉴 exact100%·PS3 이미지99.213%, 미니맵 camera·선택해제 count·드래그 count3 대칭 PASS; save000 8/8, cleanup/residue0, 후보 DxWrapper ini 원복·private ddraw module PASS. private G1 설정 draft SHA `f0ce9e64…6785` 산출(Windows native/출시 아님). targeted G1 62+profile6, G2 xref2; 통합 Fast442·Ruff/compileall/mypy/CONTEXT·safety2 PASS. G2 숫자패치만으로 전체8인 안정성 불가; 저장 save000/006 중 활성8인 fixture 없음, 원본 풀끝 `0x892410`은 live state 시작과 일치한다. G2 SHA-pinned 정적 xref inventory 후보 allocator18/spawn29/destruction13/save1/load1이나 경로 불완전/activation NO-GO. G4 원본 A* `[1]` PE 바이트 확인, 반복 비교 fixture 없음/제품 변경 NO-GO.
**2026-09-16 G4 path preflight/AI(압축, 전문 lap382 compaction+`20260916_g4_waypoint_*.md`):** pinned EXE/PE entry·UnitStruct reader PASS, original 2-run 결정론 BLOCKED. cooldown 후보 둘다 NO-GO. AI2기 waypoint reinforcement 수리 후 이동21/22좌표 국소 PASS; UI tail minimap FAIL 보존, 제품 AI/길찾기 완료 아님.
**lap356~370 검증 계보(REJECT/RELEASE 반복, 제품·게임 0회):** 각 lap 기록 및 `20260912_status_lap356_compaction.md`/`20260912_status_lap366_precompaction.md`/`20260918_status_lap382_compaction.md`(150줄 SHA `60a0d91d…d74659d5`)에 전문 보존.
## 바퀴 기록
lap417 work: W10 P-B 정적 site 인벤토리 — decoded 0x4B0 즉치 36곳(N27의 54는 byte-pattern 오탐 포함) 전수
분류, 풀-경계 미패치 3곳 중 2곳(회전커서/선형커서)은 호출자 전부 매치설정·UI범위라 op7 AI fixture에서
배제, `0x00422dc0`만 호출경로 미해결 상태로 유일하게 남음. lap416 샘플 재분석으로 `+0x692` 이상이 매치
내내 0이다가 tick~11,900대에 돌발 발생함을 확인(서서히 drift 아님). 단일 원인 미확정 ⇒ P-C 미착수(추측
수리 금지). lap415/416 미기록(N29) 발견·INBOX 원시 재확인. 게임 미실행·제품코드/커밋 0.
상세 `20260921_lap417_work_g2_pb_static_inventory.md`.
lap414 middle: lap413 P2 FAIL 원시 재계산 → **ACCEPT(불일치 0)**. 신규로 두 run의 상태 수준 결정성(N25),
fault 기전(N26: `+0x692` 이동 진행도 → 100칸 stack 배열 인덱스, 명령 바이트 원본 동일), 잔존 1200-bound
풀 순회 site(N27)와 위→아래 슬롯 할당·live 전량 ≥3533(N28)을 확정. 정정1은 요약 JSON의 exit/stall 표기.
게임 미실행·제품코드/커밋 0. 수리 카드 W10 발행, 다음은 P-A 샘플러로 H1/H2 판별.
상세 `20260921_lap414_middle_g2_p2_fail_independent_review.md`.
lap409~413: 위 「검증 상태」 압축 항목과 동일 계보(P1 near-4000 실행→W8 soak 완주/ACCEPT→P2 원본생산 FAIL).
개별 lap 판정/수치는 각 `20260920_lap{409,410,411,412,413}_*.md`에 보존.
lap397~408: 위 「검증 상태」 압축 항목과 동일 계보(정적표면측정→FO closure→재배치구현→커버리지REJECT/
ACCEPT→W6/W7→미검수계보triage). 개별 lap 판정/수치는 각 `20260920_lap{397,398,400,401,402,404,406,408}_*.md`에 보존.
lap389~395 cap조사 계보(압축, 요약은 위 「검증 상태」 lap388~395 항목과 동일 — 개별 lap 판정/STOP 사유는 각 원문 파일 `20260919_lap389_*.md`/`20260920_lap39{0,1,3,4,5}_*.md`에 보존): lap389 NO_GO+F4발견→lap390 NOT_FEASIBLE(fixture한정)→lap391 ACCEPT+STOP(F4기준 판정대기)→lap392 Astra BLOCKED→lap393 cap≤4095 산출+STOP(목표숫자 변경권한없음)→lap394 Astra 반례제기→lap395 반례ACCEPT+**4095도 무효, 안전상한 UNKNOWN 확정**, W2 카드 인계(이후 우선순위변경으로 lap396 안전종료). `ESCALATE_SOL` §5~§10 전부 열려있음(닫힌 것 없음, 철회 없음).
**lap380~388 G2 레이아웃 카드 계보(압축, 전문 `docs/history/laps/20260918_lap38{0..8}_*.md`, 압축전 STATUS `20260920_status_lap391_precompaction.md` SHA `d168c947…eed7abb6`/135줄):** lap380계획→lap381 C1/H1 CLOSED→lap382work→lap383middle REJECT→lap384work수리→lap385middle ACCEPT→lap386~387work→lap388middle ACCEPT·**레이아웃 카드 종결**(재수리 없음). 전회차`make check`rc0+`SAFETY_PASS`, 원본/frozen불변, 게임실행/커밋0. `native_route_judgment`NO_GO 미변경. 종결리포트`docs/reports/20260918_G2_LAYOUT_CARD_CLOSURE.md`. 상위 통합blocker는 위「지금 막힌 것」에 그대로 살아있음.
lap377 Astra 방향 → lap378 middle ACCEPT → lap379 provenance BLOCKED 뒤 사용자 product-first 지시로 반복 중단.
lap356~376 상세(import 해소·§3 RELEASE, REJECT/수리 반복, 게임/커밋 0회)는 각 lap 기록과 `20260912_status_lap361_entry.md`(SHA/124줄)에 보존.
