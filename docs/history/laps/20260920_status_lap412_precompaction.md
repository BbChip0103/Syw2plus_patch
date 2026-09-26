# STATUS — 매 바퀴 갱신하는 기억
## 지금 상태
활성 G1/G2/G4 제품 미완료(0/3); G3 최대16인은 2026-09-17 사용자 지시로 중단. **G2 최우선·9/18 Claude Code 역할로 재개 승인**; G1/G4 후순위 유지. M1/G1 요구 유지: 원본 구도·입력과 차후 고해상도 그림의 디테일 보존을 함께 만족하는1600×1200 화면. 제품 기준은 DESIGN, 사람 승인
원문은 feedback/APPROVALS·INBOX를 따르며 2026-09-12 01:03 bounded repair→fresh validation 허가는 제품/출시 승인이 아니다. DxWrapper 2× 화면·S1 입력쌍은 배치 프리뷰 근거만; 추가 디테일 보존 경로와 WM_CLOSE 결함은 남았다.
과거 G1/lap275~379 승인·반려·미결 계보는 전체 원문 `20260917_234449_status_pre_cutoff_compaction.md`(SHA 9400241176cce4bbe0047b358a887f09e269d9824a253654d6ff2718d352ddef,141줄)에 보존했으며 fresh 제품 PASS/출시 승인으로 승격하지 않는다. lap401 자기 편집 전 142줄본은 `20260920_status_lap401_precompaction.md`(SHA 99e9c54e73dde10cdca20bb49525cfd74a0af372d209f700d0bf33491dd492e9)에 보존(내용 동일, 단락 줄바꿈만 압축).
| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | native PS3 PASS·원본구도 FAIL·제품 미완료 | stock UI 클릭 PS9→PS7→PS5→PS3 tick3, native `1600×1200×8bpp/pitch1600`/viewport 전역 PASS; 월드 시야 확대·스프라이트/HUD 원본 픽셀 크기라 G1 배치 FAIL, 고해상도 SPR·생산·종료 미검증; 이번최종acquisition은초기화guard8000001A에BLOCKED |
| G2 | **W8 24k 실제 soak PASS — lap412 middle 독립검수 ACCEPT**·P1 lap410 ACCEPT·제품 미완료 | lap411 marked compat(`4331d9cd…`)를 8owner cap5000/live3993~4000에서 **Δ24,180 tick** 실제 실행. lap412가 요약본을 믿지 않고 원시(trace 732행·snapshot10·save/load 응답·디스크 save파일)에서 **전 수치 재계산 → 불일치 0건**: used>5000 표본0/5,824, 슬롯·ID중복·owner손상0, slot≥1200 재사용8건(전건 final까지 생존), save/load 4,000슬롯 lost·id·type·owner·hp 전부0, RSS +8,776KiB/727s·후반기울기71.5%감속, 원본불변·SAFETY_PASS. **lap412 신규:** 처리율 33.2 tick/s가 첫1/3 33.3↔끝1/3 33.2로 평탄+표본 wall간격 최대1.10초 ⇒ **CPU정체 음성**; save/load는 좌표차165건이 전부 맨해튼1~2(10tick 이동과 정합)라 충실도 **강화**; trace 실제 tick역행은 12,273→12,269 1건(응답 자기보고 12,295→12,257과 구분). **strict-cap caveat 미해결이며 기전 확정** — 일시초과가 아니라 비용10 주문 1건이 큐에 걸려 `used`가 cap 아래로 내려가야 풀리는 상태(owner7은 유닛을 한 기도 잃지 않아 전 soak 99.45% 지속). 남은것=P2 원본 생산경로 대체·P3 strict cap(되물음 대기)·P4 반복/장기soak·LAN. 상세 `20260920_lap412_middle_g2_w8_soak_independent_review.md`. |
| G3 | 사용자 지시로 중단·활성 범위 제외 | 16 PlayerStruct가 bulk save112,036B 초과, self/opponent mask8bit라 owner8~15 표현 불가; 활성9~16/LAN 미완료 |
| G4 | 원본 issuer 국소 이동 PASS·제품 미완료 | 직접 command 기록은 정지; mainthread 원본 issuer는 같은 source 이동68좌표. current waypoint reinforcement 수리 후 AI2기 이동21/22좌표·목표gap2/1 PASS; one-shot2회 같은 이동 결과, 발행tick다름·지속 정책/품질 미검증; 이번정상AI512+load11 관측만PASS/정확postload미확정 |
## 다음 한 가지
**work(Sonnet5/high)가 P2를 실제 실행한다 — diagnostic op=6 시딩을 원본 생산/재생산 명령 경로로
대체해 8owner×used5000 near-cap에 원본 명령만으로 도달·유지한다.** lap412가 W8을 ACCEPT했고
strategy 큐(`G2_STRATEGY_DIRECTION_LAP404.md` D)와 lap411 지시가 모두 P2를 가리키므로 재계획 회차를
끼우지 않는다. AGENTS "원본 명령을 우회한 성공은 부족" 조항이 이 카드의 직접 근거다.
**같은 회차에** 값싼 귀속 probe를 곁들인다(별도 회차 금지): stock 원본을 cap5000으로 띄워 한 owner를
`used=5000`까지 채우고 생산 주문 1건을 건 뒤 `reserved`를 본다 — stock에서도 `5000+10`이면 되물음1
(가) 확정, 아니면 후보 고유 회귀로 P3를 앞당긴다. 전체 suite는 source 변경 시 통합 경계 1회만.
**lap412는 지정 역할대로 제품 증거 0회차다 ⇒ 다음 회차가 또 문서/계획이면 PROMPT③ 연속2회에 걸린다.**
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
**2026-09-20 lap412 middle(Opus5/high) — lap411 W8 독립 검수 ACCEPT(정정2·신규4건), 게임 미실행·제품코드 0:**
`soak_summary.json`을 근거로 쓰지 않고 원시(`trace.jsonl` 732행, snapshot 10개, save/load 응답,
디스크 `save092.dat`)만으로 전 수치를 재계산 → **불일치 0건**(`recompute_lap411.py`,
`temp/.../20260920_lap412_middle_review/`). W8 §2 (a)~(f) 전부 ACCEPT, (e)만 조건부.
독립 provenance: 실행된 exe가 핀 후보 `4331d9cd…`(동일 디렉터리 `game.exe`는 stock이나 미실행,
slot최대4000 관측이 stock1200 불가로 교차확인), 브리지 `bab1b72d…`/pool`0x0108C000`,
`save092.dat` 재해시 `9bfe52cf…`·9,281,722B·마커 `S2P1N4K1` **1회 @0x38**, 원본 2경로 불변, `SAFETY_PASS`,
display`:3128` 잔류0(남은 Xvfb는 전부 타 저장소 소유라 미개입).
**신규1:** 처리율 33.2 tick/s가 첫1/3 33.3↔끝1/3 33.2로 평탄, 표본 wall간격 최대1.10초 ⇒ AGENTS가 요구한
**CPU정체 축 음성**(lap411 미측정). **신규2:** save/load를 4,000슬롯 전 필드로 대조 — type/owner/hp/id
전부 0불일치, 좌표차 165건은 **전부 맨해튼 1~2**로 10tick 이동과 정합 ⇒ 충실도 강화.
**정정1:** "load 12,295→12,257 역행"은 제어 응답 자기보고이고, `trace.jsonl`의 실제 역행은 **12,273→12,269
1건**(표본간격 33tick 때문). 방향·시점 일치로 결론 유지, 수치 출처는 구분해 적을 것.
**정정2(되물음1 기전 확정):** `used+reserved=5010`은 일시 초과가 아니라 **해소되지 않는 예약** —
owner7은 `reserved=10`이 726/728 표본, tick158~24,298(**99.45%**) 고정이며 유닛을 한 기도 잃지 않아
`count`500 불변. owner3은 사망으로 `used`가 내려가면 해소(`reserved=0` 111표본). ⇒ 선택지 (가)는
"일시 초과 허용"이 아니라 "cap에 붙은 owner의 무기한 대기 주문 1건 허용"으로 다시 읽어야 한다.
**신규 N21:** W8 §4가 요구한 "stub 채널에 근거하지 않음" 명시 문장이 산출물에 없다(무해·문서 누락).
**신규 N22:** lap411이 스스로 `runtime_driver.py`+테스트1을 바꿨는데 "동일 source"를 근거로 전체 gate를
건너뛰었다 — INBOX 21:58 규칙의 **오적용**. lap412가 통합 경계 gate를 대신 실행(collected **785**=784+1).
하네스 수리 자체는 유효: `control_goal_payload`가 송신 경로(`runtime_driver.py:426`)에서 쓰이고,
`request_id`를 int로 역주입하면 신규 테스트가 FAIL(포착력 확인).
**신규 N23:** 시딩은 풀이 아니라 전비 cap에서 멈췄고(비용10×500기×8owner) live가 정확히 4,000 =
풀 가용 4,000칸 **여유 0**으로 운전됐다. 크래시는 없었으나 cap에 붙은 owner가 더 생산할 수 없어
**풀 고갈 경로는 실행되지 않았다**. `4001`은 lap381이 "공학 시험값·최종 용량 아님"으로 못박은 값이다.
**신규 N24:** `verify_g2_persistence_artifacts`는 이 번들 스키마를 모른다(다른 계보 전용) ⇒ W8 soak
산출물에 기계 게이트가 없다. P4에서 승격 권고, 단 P2를 미룰 사유 아님.
상세 `20260920_lap412_middle_g2_w8_soak_independent_review.md`.
**2026-09-20 lap411 work(Sonnet5/high+leader 회수) — W8 실제 Δ24,180tick soak PASS, lap412 ACCEPT:**
marked compat `4331d9cd…`, 8owner cap5000/live3993~4000, crash0, used>5000 0, 상세10 snapshot 무결성0,
slot≥1200 reuse8, 중간 marked save/load 4000→4000 lost/id mismatch/new0, RSS245,248→252,072→254,024KiB
(후반 slope71.5% 감속), rc0/residue0/원본불변/`SAFETY_PASS`. strict caveat `used+reserved=5010` 2,053표본.
첫 진입 실패는 PS9 이전 클릭+숫자 request_id 하네스 결함으로 확정·문자열ID 회귀테스트 수리. targeted6 passed,
Ruff/mypy PASS; 동일 source full784 반복 안 함. 상세 `20260920_lap411_work_g2_compat_long_soak.md`.
**2026-09-20 lap410 middle(Opus5/high) — lap409 P1 독립 검수 ACCEPT(정정2건), 게임 미실행·제품코드 0:**
INBOX 21:58 지시에 따라 전체 784 `make check`를 재실행하지 않고(동일 source, 직전 full gate PASS) **원시
산출물 재계산 + 표적 테스트 + 원본/안전검사**만 수행했다. 독립 확인: 원본 `b56986e0…08a8ac` 불변(후보 빌드
전후), `build_candidate(original,4001)` 재실행 → `4331d9cd…`가 `runtime_driver` 핀 및 실행 exe와 **바이트 동일**,
`save090.dat` 재해시 `814e7f05…a88460`/9,272,322B·마커 `S2P1N4K1` 파일 전체 **1회·오프셋 0x38**, presave/postload
스냅샷 직접 diff(소실0·internal_id불일치0·type/owner불일치0·신규5·slot≥1200이 2,801건 동수), `seed_receipts`
24건(executed23+`fixture_exceeds_unreserved_supply`1, producer슬롯 16/24가 ≥1200·최대3779, 시딩후 3,985가
trace tick687과 일치), `POOL_PROFILE_LAYOUTS[...compat]=(4001,0x0108C000,0x017B8658)`가 `layout(4001)`과 일치,
`/tmp/p1_bridge4001`의 `runtime_bridge.c`가 세 앵커 모두 치환된 진짜 4001 빌드이고 DLL `f642d033…`이 배포분과
동일(배포21:57:46 < 2차기동21:57:56), `pytest ...persistence_compat_v1.py -q` **5 passed**(W7 앵커 포함),
`SAFETY_PASS`, display`:300` 잔류0. **신규 근거:** `trace.jsonl` tick **2328→1567 역행** = 로드가 실제로 엔진
상태를 교체했다는 직접 증거(lap409 미제시; 없으면 "소실0"은 로드 무동작과 구분 불가). **정정1:** presave는
저장보다 ~535tick 앞섬 — 신규5 중 4기는 저장 이전 생산(세이브 포함), 로드후 생산은 1기. 카운트는 3,995→3,995
정확 일치, id검증 범위는 3,991/3,995. **정정2:** 배포 `_inmm.dll`의 stub 4모듈이 stock `0x008990C8`/1200
하드코딩 → 재배치 후보에서 유닛 0기 관측(`inmm_unit_ticks.jsonl` 0바이트 실증). 읽기전용·판정 무영향, 향후
오판 위험으로 W8 §4에 bounded 인계. 신규 카드 W8 `G2_COMPAT_LONG_SOAK_LAP410.md` 발행. 상세
`20260920_lap410_middle_g2_p1_independent_review.md`.
**2026-09-20 lap409 work(Sonnet5/high) — W7 앵커+P1 실제 게임 실행(첫 실제 실행 증거, lap410이 ACCEPT):**
W7: `test_compat_wrappers_are_contained_in_rsrc_cave_without_overlap` 신규(4 wrapper 실제 emit 산출물
길이로 컨테인먼트·비중첩·섹션매핑·실행속성 강제), 역주입 확인(`/tmp` in-memory, `RSRC_COMPAT_END_OFFSET`
1B 축소 시 FAIL 재현). P1: 격리 Wine(`local/runtime/20260920_215245_1236080_0`)에서 marked compat
(`4331d9cd…`) 후보를 title클릭(184,560)→PS7→goal `_custom_game_chain_inject_g2_eight_seed42`→PS3(8owner
cap5000)로 부팅, 진단브리지 재빌드 필요(최초 재사용분이 STOCK1200 주소라 op=6 전멸 발견→
`build_runtime_bridge --unit-pool-capacity 4001`로 재빌드), op=6 gate-legal 시딩으로 3,991 live 유닛
도달, op=2 슬롯90 저장(`save090.dat` 마커 `S2P1N4K1`이 파일 오프셋 `0x38`에서 실제 확인=신규 포맷),
op=3 재적재 후 독립 판독(`runtime_driver.py` snapshot)으로 슬롯 단위 대조: 소실0·id불일치0(생산계속 5기
순증만). 정리 후 잔류 프로세스0, 원본 2경로 `b56986e0…08a8ac` 불변, `make check` rc0 **784 passed**
(783+1)+`SAFETY_PASS`. **"compat는 382-unit만 통과" 갭이 near-4000에서 해소.** 게임코드/제품모듈 변경 0
(진단환경만 신규). 상세 `20260920_lap409_work_g2_p1_compat_near4000_live_execution.md`.
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
lap412 middle: lap411 W8 원시증거 전 수치 재계산 → **불일치 0건, ACCEPT**. 신규로 CPU정체 음성
(33.2 tick/s 평탄)·save/load 전필드 충실도 강화를 확인하고, 되물음1의 `5010`을 "해소되지 않는 예약"으로
기전 확정했다. N21(§4 문장 누락)·N22(전체 gate 오면제, 이번에 785로 대신 실행)·N23(풀 여유0·고갈경로
미시험)·N24(soak 번들 기계게이트 부재) 발행. 게임 미실행·제품코드/커밋 0. 다음은 P2 실제 실행.
상세 `20260920_lap412_middle_g2_w8_soak_independent_review.md`.
lap411 work: 하네스 PS9 대기+control request_id 문자열 수리 후 marked compat 실제 W8 완주 — Δ24,180tick,
live3993~4000, 중간 save/load 무손실, slot≥1200 reuse8, used>cap0, crash/residue0. strict used+reserved5010 caveat 유지.
상세 `20260920_lap411_work_g2_compat_long_soak.md`.
lap410 middle: lap409 P1 원시증거 독립 재계산 → **ACCEPT**. 로드 실재 증거(tick 2328→1567 역행) 신규 발굴,
정정1(대조 기준선이 저장보다 ~535tick 앞섬; 4기 id-미검증, 카운트는 정확 일치), 정정2(배포 DLL stub 4모듈의
stock 주소 잔존 → 재배치 후보에서 유닛 0기 관측, 읽기전용) 기록. 게임 미실행·제품코드/커밋 0. W8 발행.
상세 `20260920_lap410_middle_g2_p1_independent_review.md`.
lap409 work: W7 앵커(역주입확인PASS, `make check`784=783+1) 완료 후 즉시 P1 실제 실행 — marked compat
후보 near-4000(3,991 live)에서 gate-legal 시딩→마킹저장(마커 오프셋0x38 파일확인)→마킹로드 왕복 무손실.
STOCK1200 브리지/N=4001후보 주소불일치를 발견·재빌드로 수리. 원본불변·`SAFETY_PASS`. lap410 ACCEPT,
제품 완료 아님. 상세 `20260920_lap409_work_g2_p1_compat_near4000_live_execution.md`.
lap397~408: 위 「검증 상태」 압축 항목과 동일 계보(정적표면측정→FO closure→재배치구현→커버리지REJECT/
ACCEPT→W6/W7→미검수계보triage). 개별 lap 판정/수치는 각 `20260920_lap{397,398,400,401,402,404,406,408}_*.md`에 보존.
lap389~395 cap조사 계보(압축, 요약은 위 「검증 상태」 lap388~395 항목과 동일 — 개별 lap 판정/STOP 사유는 각 원문 파일 `20260919_lap389_*.md`/`20260920_lap39{0,1,3,4,5}_*.md`에 보존): lap389 NO_GO+F4발견→lap390 NOT_FEASIBLE(fixture한정)→lap391 ACCEPT+STOP(F4기준 판정대기)→lap392 Astra BLOCKED→lap393 cap≤4095 산출+STOP(목표숫자 변경권한없음)→lap394 Astra 반례제기→lap395 반례ACCEPT+**4095도 무효, 안전상한 UNKNOWN 확정**, W2 카드 인계(이후 우선순위변경으로 lap396 안전종료). `ESCALATE_SOL` §5~§10 전부 열려있음(닫힌 것 없음, 철회 없음).
**lap380~388 G2 레이아웃 카드 계보(압축, 전문 `docs/history/laps/20260918_lap38{0..8}_*.md`, 압축전 STATUS `20260920_status_lap391_precompaction.md` SHA `d168c947…eed7abb6`/135줄):** lap380계획→lap381 C1/H1 CLOSED→lap382work→lap383middle REJECT→lap384work수리→lap385middle ACCEPT→lap386~387work→lap388middle ACCEPT·**레이아웃 카드 종결**(재수리 없음). 전회차`make check`rc0+`SAFETY_PASS`, 원본/frozen불변, 게임실행/커밋0. `native_route_judgment`NO_GO 미변경. 종결리포트`docs/reports/20260918_G2_LAYOUT_CARD_CLOSURE.md`. 상위 통합blocker는 위「지금 막힌 것」에 그대로 살아있음.
lap377 Astra 방향 → lap378 middle ACCEPT → lap379 provenance BLOCKED 뒤 사용자 product-first 지시로 반복 중단.
lap356~376 상세(import 해소·§3 RELEASE, REJECT/수리 반복, 게임/커밋 0회)는 각 lap 기록과 `20260912_status_lap361_entry.md`(SHA/124줄)에 보존.
