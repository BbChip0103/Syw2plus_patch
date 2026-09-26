# STATUS — 매 바퀴 갱신하는 기억
## 지금 상태
활성 G1/G2/G4 제품 미완료(0/3); G3 최대16인은 2026-09-17 사용자 지시로 중단. **G2 최우선·9/18 Claude Code 역할로 재개 승인**; **2026-09-21 00:20 지시로 G1/G4는 G2 성립 전까지 잠정 중단, G3는 계속 포기 범위로 고정**(G1/G4 표 항목은 과거 증거 보존일 뿐 현재 작업 대상 아님). M1/G1 요구 유지: 원본 구도·입력과 차후 고해상도 그림의 디테일 보존을 함께 만족하는1600×1200 화면. 제품 기준은 DESIGN, 사람 승인
원문은 feedback/APPROVALS·INBOX를 따르며 2026-09-12 01:03 bounded repair→fresh validation 허가는 제품/출시 승인이 아니다. DxWrapper 2× 화면·S1 입력쌍은 배치 프리뷰 근거만; 추가 디테일 보존 경로와 WM_CLOSE 결함은 남았다.
과거 G1/lap275~379 승인·반려·미결 계보는 전체 원문 `20260917_234449_status_pre_cutoff_compaction.md`(SHA 9400241176cce4bbe0047b358a887f09e269d9824a253654d6ff2718d352ddef,141줄)에 보존했으며 fresh 제품 PASS/출시 승인으로 승격하지 않는다. lap401 자기 편집 전 142줄본은 `20260920_status_lap401_precompaction.md`(SHA 99e9c54e73dde10cdca20bb49525cfd74a0af372d209f700d0bf33491dd492e9)에 보존(내용 동일, 단락 줄바꿈만 압축). lap412가 136줄에서 압축하기 직전 전체 원문은 `20260920_status_lap412_precompaction.md`(SHA fcfae74298ce8c62b820d0d6587516633380b54e1931116fd5f1c34ce670a07f, 136줄)에 보존했으며, 압축 대상은 lap409·lap410 두 항목뿐이고 각 lap 원문 파일에 전문이 그대로 남아 있다. lap414가 압축하기 직전 전체 원문은 `20260921_status_lap414_precompaction.md`(SHA 878f23ce08d1787ce06a4003b9a0dfda3e95fd3fd85cac9bfc4026073dc0f804, 125줄)에 보존했으며, 압축 대상은 lap411·lap412 두 항목뿐이고 각 lap 원문 파일에 전문이 그대로 남아 있다. lap418이 압축하기 직전 전체 원문은 `20260921_status_lap418_precompaction.md`(SHA 3754c8c92473e4b91dfdddff7ca0033841ef03f1238f177ade71f327beeb187f, 125줄)에 보존했으며, 압축 대상은 lap417 항목 하나뿐이고 그 전문은 `20260921_lap417_work_g2_pb_static_inventory.md`에 그대로 남아 있다. lap419가 압축하기 직전 전체 원문은 `20260921_status_lap419_precompaction.md`(SHA e3fafb76b674952a4578577e3df0dc340021989a7e07b7ad3391530697676067, 130줄)에 보존했으며, 압축 대상은 lap417 항목 하나뿐이고 그 전문은 `20260921_lap417_work_g2_pb_static_inventory.md`에 그대로 남아 있다. lap420이 압축하기 직전 전체 원문은 `20260921_status_lap420_precompaction.md`(SHA 744295ae3cca3f88851c5199333a64a35ad4c4d1a0b6a2b458e2486c629d8b5c, 120줄)에 보존했으며, 압축 대상은 lap418·lap419 두 항목뿐이고 각 전문은 `20260921_lap418_middle_g2_pb_independent_review.md`·`20260921_lap419_work_g2_h2_stale_vs_h1r_decision.md`에 그대로 남아 있다.
| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | native PS3 PASS·원본구도 FAIL·제품 미완료 | stock UI 클릭 PS9→PS7→PS5→PS3 tick3, native `1600×1200×8bpp/pitch1600`/viewport 전역 PASS; 월드 시야 확대·스프라이트/HUD 원본 픽셀 크기라 G1 배치 FAIL, 고해상도 SPR·생산·종료 미검증; 이번최종acquisition은초기화guard8000001A에BLOCKED |
| G2 | **P2 원본생산/AI 경로 FAIL(lap414 독립검수 ACCEPT)**·W8 lap412 ACCEPT·**H1 lap418에서 기전부재로 기각, H2 lap419·420 확정 기각, 남은 원인 주체는 lap420 검수로 미결 환원**·제품 미완료 | lap413에서 op=6 없이 원본 Train`0x4AF5E0`으로 owner0 worker가 slot3951에 생성(used20→30)되어 원본 생산·확장slot 소비는 성립. 그러나 resource-only fixture(원본 SetResource만, 장부/유닛 write0)로 7 AI를 돌린 N=4001 marked compat(`4331d9cd…`)가 **두 신규 prefix 모두 정확히 tick11,928/live468/owner5 used1208에서 `0x00414133` read page fault(`0x00338400`)**로 죽음. stock-layout supply5000 대조군(`0a1da…`)은 tick11,928을 통과해 13,116/live405까지 page fault 없이 진행 후 match 종료성 정지. 따라서 진단시딩 4,000기 W8 PASS를 일반 생산·전투 안정성으로 승격 불가. P2 FAIL, 다음은 fault 선행 손상 root-cause. W8 자체 ACCEPT·strict-cap caveat는 유지. 상세 `20260920_lap413_work_g2_original_production_failure.md`. |
| G3 | 사용자 지시로 중단·활성 범위 제외 | 16 PlayerStruct가 bulk save112,036B 초과, self/opponent mask8bit라 owner8~15 표현 불가; 활성9~16/LAN 미완료 |
| G4 | 원본 issuer 국소 이동 PASS·제품 미완료 | 직접 command 기록은 정지; mainthread 원본 issuer는 같은 source 이동68좌표. current waypoint reinforcement 수리 후 AI2기 이동21/22좌표·목표gap2/1 PASS; one-shot2회 같은 이동 결과, 발행tick다름·지속 정책/품질 미검증; 이번정상AI512+load11 관측만PASS/정확postload미확정 |
## 다음 한 가지
**work(Sonnet5/high)가 `docs/work/active/G2_POOL_FAULT_MOVE_FIELD_WRITER_LAP420.md`(W12)를 수행한다.**
lap420 middle이 lap419 P-D를 원시 `samples.jsonl`만으로 재계산해 **H2 기각은 ACCEPT(확정)**,
그러나 lap419의 H1r 해석은 **REJECT/정정**했다(N32/N33/N34). 정정된 사실: onset tick 11,915에
`+0x692` **혼자가 아니라 7개 필드가 동시에** 0→10 전후로 기동해 이후 함께 증가했고(단일 `0x758`
read 산출이라 아티팩트 아님), 3565 자신의 `move`는 그 전 163표본 **전부 0**이었다(±44~50은 hi밴드
2,801슬롯의 최댓값 오귀속), dense 구간 21개 tick은 표본이 없어 "매 tick"도 "tick마다 진동"도
성립하지 않는다. ⇒ 관측은 "**3565가 정상 활성화됐고 그 첫 tick부터 `+0x692`가 범위 밖**"까지이며
**원인 주체는 미결**이다. W12는 (P-E) 후보 `.text`에서 변위 `0x692`를 목적지로 쓰는 store 전수로
누산기 `0x0040bc86~0x0040bcff`(N26) 외 기록자 유무를 30분 상자로 가르고, 같은 회차에 (P-F) 스캔
범위를 줄여 **tick당 표본 2회 이상** + **slot<1200 저슬롯 활성화 대조군** + 활성화 시 경로점수를
함께 기록해 H5(자기 활성화 경로의 입력 결함) vs H6(외부 writer)을 가른다. `0x00414133`·
`roster_add 0x0043ee39`·`0x00422dc7`는 계속 패치 금지이고 lap418의 H1 기각도 되살리지 않는다.
P2 near-cap FAIL 기준은 낮추지 않는다. **lap419가 실행 회차라 PROMPT③ 카운터는 리셋됐고 lap420이
그 뒤 첫 제품0 회차다(연속 1회) — W12는 반드시 실행 증거를 만든다.**
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
**2026-09-21 lap420 middle(Opus5/high) — lap419 W11 P-D 독립 검수: 부분 ACCEPT/부분 REJECT. 게임
미실행·제품코드/커밋 0, 이번 회차 source 변경 0(01:00 이후 수정 파일 0건):** lap419 요약을 읽지 않고
원시 `samples.jsonl` 994줄만으로 W11 판정식을 재계산(`temp/.../20260921_lap420_middle_review/`,
`recompute_lap419.py`+`findings.json`). **ACCEPT:** fault tick11,928/sample994 재현; **H2 확정 기각** —
3565는 tick10,205~11,928 **406표본 전부** `alive=True/owner4/type76`이고 최초생존 뒤 `alive=False`
0표본이며 `alive`는 구조체가 아닌 **별도 존재배열 `0x017B8658`** 출처라 구조체 손상과 독립; lo밴드
994표본 `max_abs=0`; 이상슬롯 {3565}뿐(레코드241); VA산술 `0x016F0B0A` 일치; 원본2경로 불변·
`SAFETY_PASS`·targeted 6 passed. **REJECT/정정 3건:** **N32** "`+0x692`만 튄다"는 거짓 — onset
tick11,915에 `f674/f676/f2b8/f2bc/f2be 0→10`, `f2ba 0→9`, `f2a4 9→10`이 **동시에** 기동해 11,928까지
**함께 10→11→12→13 증가**한다(한 슬롯 전필드는 단일 `0x758` read 산출이라 아티팩트 아님). 흩어진
4클러스터가 같은 tick에 정합 카운터로 세팅되는 모양은 **이웃 오버런으로 설명되지 않는다**. **N33**
"±44~50 정상 드리프트"는 밴드통계 오귀속(N31 계열 반복) — 3565 자신의 `move`는 onset 이전 **163표본
전부 정확히 0**, 44~50은 hi밴드 2,801슬롯의 `max_abs` ⇒ 3565는 **정지(0)에서 활성화되며 첫 값부터
범위 밖(19,579)**. **N34** "매 tick 샘플/tick마다 진동" 불성립 — 정지tick 제외 시 dense 전 tick이
**표본 1개**(위상 비통제), 11,828~11,928 중 **21 tick 무표본**(11,916·11,922·11,927 포함; 표본1회가
4,000슬롯×`0x758`≈7.5MB로 ~0.037s). ⇒ 판정은 "**3565 정상 활성화 + 첫 tick부터 `+0x692` 범위 밖**"
까지이고 **원인 주체 미결**. 한계: 표본간격 1~2tick이라 "1tick 내 사망→동일 owner/type 재할당" 원리적
미배제(확률 낮음), HEAD unborn이라 source불변은 mtime 근거만, 2026-09-20 23:56 기동 `winedevice.exe`
2기(PID 2089059/2089068)는 **lap419 실행분 아님**이라 전역정리 금지로 관측만 기록. stub채널 비근거(N21).
`make check`(786) 미재실행(source 변경0, N22 명시). W12 발행. 상세 `20260921_lap420_middle_g2_pd_independent_review.md`.
**2026-09-21 lap419 work — W11 P-D 실제 실행(압축, 전문 `20260921_lap419_work_g2_h2_stale_vs_h1r_decision.md`;
해석부는 위 lap420이 정정):** lap416 하네스에 3565 전필드 기록·무조건 `max_abs`·크래시창 조밀샘플을 얹어
재실행, tick11,928 fault 재현(994표본). **H2 기각은 유효**(lap420 ACCEPT). "`+0x692`만/±44~50 드리프트/
tick마다 진동"과 그에 기댄 "H1r=외부 wild write 확정"은 lap420이 뒤집음. 제품코드/커밋0, source변경0.
**2026-09-21 lap418 middle — lap417 P-B 독립 검수, 부분 ACCEPT/부분 REJECT(압축, 전문
`20260921_lap418_middle_g2_pb_independent_review.md`). 게임 미실행·제품코드/커밋0:** 자체 resync
sweep(306,811 insn) 재계산. ACCEPT: 호출자 집합 2건(`FUN_004183a0`×3, `FUN_00444ef0`×8), onset 돌발성
709표본 재현. 정정: 후보기준 0x4B0은 즉치35+변위1(N30). **핵심 — `0x00422dc0`은 `.data` 초기화표
`0x004ec02c`→thunk `0x00422db0`→`_initterm 0x004de170`의 C++ 전역 정적생성자(main 이전 1회)이고
`FUN_004119f0`이 빈 생성자라 풀을 건드리지 않는다** ⇒ `0x00422dc7` 수리는 no-op, **착수 금지**,
**H1은 기전 부재로 기각**(UNKNOWN 아님). N31(조건부 `max_abs` 오독) 정정. targeted 6 passed,
`SAFETY_PASS`, 원본 불변. 연속 제품0 2회로 W11 발행 → lap419가 실행.
**2026-09-21 lap417 work(압축):** 0x4B0 전수 분류로 풀-경계 후보 3곳 좁힘, onset 돌발성 최초 지적.
`0x00422dc0` 미해결 판정만 lap418이 뒤집음. 게임 미실행·제품코드/커밋/source변경 0. 전문
`20260921_lap417_work_g2_pb_static_inventory.md`. N29(lap415/416 소급기록 없음) 유지.
**2026-09-21 lap414 middle — lap413 P2 FAIL 독립 검수 ACCEPT(불일치 0). 게임 미실행·제품코드/커밋 0.
압축, 전문 `20260921_lap414_middle_g2_p2_fail_independent_review.md`·산출물 `temp/.../20260921_lap414_middle_review/`:**
원시(trace.jsonl·samples·receipts·wine.log·manifest·재해시)만으로 후보 두 run의 tick11,928/live468/
owner5 used1208·동일 fault와 stock의 fault0/tick13,116을 재현, op7 resource-only 계약 성립(영수증7·
장부변화0). targeted 6 passed·`SAFETY_PASS`·원본불변, source 변경0이라 `make check` 미재실행.
**살아있는 신규 근거:** **N25** 두 run이 공유 tick 46개 전부 일치 ⇒ 상태 수준 결정성, tick bisect 유효.
**N26** `0x00414000`은 Bresenham 경로점 생성+샘플러, 호출자는 `0x0040be55` 하나, fault는 100칸 stack 배열을
`edx=((점수-1)×|unit+0x692|)/100`로 읽는 지점이고 `+0x692`는 `0x0040bc86~0x0040bcff`가 누적하는 타일 이동
진행도(정상 `edx≤99`) — fault 지점 ±0x180이 원본·후보 동일하므로 **명령 패치 금지**. **N28** 할당기는 풀을
위→아래로 채워 crash tick 후보 live 468기가 전부 3533~4000이고 0~1199에는 0기(엔진 `count`와 8/8 일치).
**N27은 lap418이 정정**(즉치 수·후보 고유 site 누락·`0x00422dc0` 성격). 정정1(요약 JSON의 exit/stall
표기)은 판정 불변. **한계 유지:** stock 대조는 다른 바이너리·다른 풀 크기라 "그 tick의 일반 엔진 버그
아님"까지만 경계 짓는다.
**2026-09-20 lap413 work — P2 원본생산 실제 실행 FAIL(lap414 독립검수 ACCEPT):** resource-only op7 AI로 N=4001
후보가 2회 모두 tick11,928/live468/owner5 used1208에서 `0x00414133` fault 재현, stock-layout supply5000은
fault0·tick13,116 진행. `make check`rc0 786. 상세 `20260920_lap413_work_g2_original_production_failure.md`.
**2026-09-20 lap409~412 P1/W8 계보(압축, 전문 각 `20260920_lap{409,410,411,412}_*.md`):** lap409 work가 marked
compat `4331d9cd…`로 near-4000(3,991 live) 첫 실제 실행(왕복 무손실, STOCK1200 브리지 오사용 수리)→lap410 middle
**ACCEPT**(로드 실재 tick 2328→1567 역행 증거; 정정1 presave~535tick 선행, 정정2 배포DLL stub 1200 하드코딩)→
lap411 work Δ24,180tick W8 soak 완주(live3993~4000, crash0, slot≥1200 reuse8)→lap412 middle **ACCEPT**(불일치0,
CPU정체 음성, 되물음1의 `5010`을 "해소되지 않는 예약"으로 기전 확정, N21~N24). 전 회차 게임실행 있음(work 두
회)/제품모듈 변경0/커밋0, `make check`rc0+`SAFETY_PASS`.
**2026-09-20 lap397~408 G2 재배치·커버리지·런타임계보(압축, 전문 각 `20260920_lap{397,398,400,401,402,404,406,408}_*.md`):**
lap397 정적표면측정(제자리확장NOT_FEASIBLE·재배치FEASIBLE)→lap398 FO 3건PASS→lap399 W3구현N=1210→lap400 middle
REJECT(제자리성장 D1)→lap401 work 꼬리재배치 구현(`tail_relocation_storage_layout_v1`)→lap402 middle ACCEPT+신규
D1(N=4001 섹션커버리지 99.24% 밖)→lap404 strategy triage(N18)→lap406 middle 항목1/2/4/5 ACCEPT·항목3 게이트지시
(W6, N19)→**lap408 middle W6 CLOSED**(783=779+4, 역주입포착확인)+W7(`.rsrc` wrapper 컨테인먼트 사각)+N20(미기록
회차). 전 회차 제품코드/커밋0, `make check`rc0+`SAFETY_PASS`+원본불변 확인.
**lap388~395 G2 전비장부 cap 조사 계보(압축, lap398. 각 lap 기록 전문은 `docs/history/laps/20260919_lap389_*.md`~`20260920_lap395_*.md`에 보존):** lap389 owner-transfer 사전거부 NO_GO+신규F4(16bit장부/40,000합) 발견→lap390 W1 NOT_FEASIBLE(fixture한정)→lap391 ACCEPT+F4생존→lap392 Astra BLOCKED→lap393 cap≤4095 산출(이후 lap394 Astra 반례로 무효)→lap394 반례제기→lap395 반례ACCEPT+**4095도 무효, 안전상한 UNKNOWN 확정**(펌프로 세cap 전부 32,785 도달; cap5000은 펌프없이도 1160기/40,000으로 도달 가능). 전 회차 `make check` rc0 715 passed+`SAFETY_PASS`, 원본 불변, 제품코드/게임실행/커밋 **0**. `ESCALATE_SOL` §9로 열려있음(사용자 우선순위변경으로 후순위, 철회아님). lap397~398 풀확장 스파이크와는 독립 트랙.
**lap380~388 G2 레이아웃 카드 계보:** 개별 lap(380 C1/H1→381~383 REJECT/수리→384~387 수리/구현→388 ACCEPT
종결) 상세는 아래 「바퀴 기록」 압축 줄과 각 lap 원문(`docs/history/laps/20260918_lap38{0..8}_*.md`)에
보존. 전 회차 `make check` rc0+`SAFETY_PASS`, 원본/frozen 불변, 게임실행/커밋0.
**2026-09-15 product-first:** 원본·후보 실제 S1 load·PS35 메뉴 exact100%·PS3 이미지99.213%, 미니맵 camera·선택해제 count·드래그 count3 대칭 PASS; save000 8/8, cleanup/residue0, 후보 DxWrapper ini 원복·private ddraw module PASS. private G1 설정 draft SHA `f0ce9e64…6785` 산출(Windows native/출시 아님). targeted G1 62+profile6, G2 xref2; 통합 Fast442·Ruff/compileall/mypy/CONTEXT·safety2 PASS. G2 숫자패치만으로 전체8인 안정성 불가; 저장 save000/006 중 활성8인 fixture 없음, 원본 풀끝 `0x892410`은 live state 시작과 일치한다. G2 SHA-pinned 정적 xref inventory 후보 allocator18/spawn29/destruction13/save1/load1이나 경로 불완전/activation NO-GO. G4 원본 A* `[1]` PE 바이트 확인, 반복 비교 fixture 없음/제품 변경 NO-GO.
**2026-09-16 G4 path preflight/AI(압축, 전문 lap382 compaction+`20260916_g4_waypoint_*.md`):** pinned EXE/PE entry·UnitStruct reader PASS, original 2-run 결정론 BLOCKED. cooldown 후보 둘다 NO-GO. AI2기 waypoint reinforcement 수리 후 이동21/22좌표 국소 PASS; UI tail minimap FAIL 보존, 제품 AI/길찾기 완료 아님.
**lap356~370 검증 계보(REJECT/RELEASE 반복, 제품·게임 0회):** 각 lap 기록 및 `20260912_status_lap356_compaction.md`/`20260912_status_lap366_precompaction.md`/`20260918_status_lap382_compaction.md`(150줄 SHA `60a0d91d…d74659d5`)에 전문 보존.
## 바퀴 기록
lap420 middle: lap419 P-D를 원시 `samples.jsonl`만으로 재계산 → **H2 확정 기각 ACCEPT**, lap419의 H1r
해석은 **REJECT/정정**(N32 `+0x692` 단독 아님·8필드 동시기동, N33 ±44~50은 밴드통계 오귀속·3565는
onset 전 163표본 전부 0, N34 21 tick 무표본이라 "매 tick/진동" 불성립) ⇒ 원인 주체 미결 환원. W12
`G2_POOL_FAULT_MOVE_FIELD_WRITER_LAP420.md` 발행. 게임 미실행·제품코드/커밋0·source변경0, targeted6
passed, `SAFETY_PASS`. 상세 `20260921_lap420_middle_g2_pd_independent_review.md`.
lap419 work: W11 P-D 실제 실행(fault tick11,928 재현, 994표본) → **H2 기각**(lap420 ACCEPT); "H1r=외부 wild write 확정"은 lap420이 정정. 제품코드/커밋0, source변경0.
lap417~418: W10 P-B 정적 인벤토리(풀-경계 후보 3곳, onset 돌발성) → lap418 독립 재계산이 부분 ACCEPT/부분
REJECT하고 `0x00422dc0`을 C++ 전역 정적생성자로 확정해 **H1 기각**·`0x00422dc7` 수리 금지. 둘 다 게임
미실행·제품코드/커밋0. 전문 `20260921_lap41{7,8}_*.md`.
lap414 middle: lap413 P2 FAIL 원시 재계산 → **ACCEPT(불일치 0)**. 신규로 결정성(N25)·fault 기전(N26)·위→아래
슬롯 할당과 live 전량 ≥3533(N28) 확정, N27은 lap418이 정정. 게임 미실행·제품코드/커밋 0. W10 발행.
상세 `20260921_lap414_middle_g2_p2_fail_independent_review.md`.
lap397~413: 위 「검증 상태」 압축 항목과 동일 계보(정적표면측정→FO closure→재배치구현→커버리지REJECT/
ACCEPT→W6/W7→P1 실행→W8 soak ACCEPT→P2 원본생산 FAIL). 개별 판정/수치는 각
`20260920_lap{397,398,400,401,402,404,406,408,409,410,411,412,413}_*.md`에 보존.
lap389~395 cap조사 계보(압축, 요약은 위 「검증 상태」 lap388~395 항목과 동일 — 개별 lap 판정/STOP 사유는 각 원문 파일 `20260919_lap389_*.md`/`20260920_lap39{0,1,3,4,5}_*.md`에 보존): lap389 NO_GO+F4발견→lap390 NOT_FEASIBLE(fixture한정)→lap391 ACCEPT+STOP(F4기준 판정대기)→lap392 Astra BLOCKED→lap393 cap≤4095 산출+STOP(목표숫자 변경권한없음)→lap394 Astra 반례제기→lap395 반례ACCEPT+**4095도 무효, 안전상한 UNKNOWN 확정**, W2 카드 인계(이후 우선순위변경으로 lap396 안전종료). `ESCALATE_SOL` §5~§10 전부 열려있음(닫힌 것 없음, 철회 없음).
**lap380~388 G2 레이아웃 카드 계보(압축, 전문 `docs/history/laps/20260918_lap38{0..8}_*.md`, 압축전 STATUS `20260920_status_lap391_precompaction.md` SHA `d168c947…eed7abb6`/135줄):** lap380계획→lap381 C1/H1 CLOSED→lap382work→lap383middle REJECT→lap384work수리→lap385middle ACCEPT→lap386~387work→lap388middle ACCEPT·**레이아웃 카드 종결**(재수리 없음). 전회차`make check`rc0+`SAFETY_PASS`, 원본/frozen불변, 게임실행/커밋0. `native_route_judgment`NO_GO 미변경. 종결리포트`docs/reports/20260918_G2_LAYOUT_CARD_CLOSURE.md`. 상위 통합blocker는 위「지금 막힌 것」에 그대로 살아있음.
lap377 Astra 방향 → lap378 middle ACCEPT → lap379 provenance BLOCKED 뒤 사용자 product-first 지시로 반복 중단.
lap356~376 상세(import 해소·§3 RELEASE, REJECT/수리 반복, 게임/커밋 0회)는 각 lap 기록과 `20260912_status_lap361_entry.md`(SHA/124줄)에 보존.
