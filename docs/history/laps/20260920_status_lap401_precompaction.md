# STATUS — 매 바퀴 갱신하는 기억
## 지금 상태
활성 G1/G2/G4 제품 미완료(0/3); G3 최대16인은 2026-09-17 사용자 지시로 중단. **G2 최우선·9/18 Claude Code 역할로 재개 승인**; G1/G4 후순위 유지. M1/G1 요구 유지: 원본 구도·입력과 차후 고해상도 그림의 디테일 보존을 함께 만족하는1600×1200 화면. 제품 기준은 DESIGN, 사람 승인
원문은 feedback/APPROVALS·INBOX를 따르며 2026-09-12 01:03 bounded repair→fresh validation 허가는 제품/출시 승인이 아니다. DxWrapper 2× 화면·S1 입력쌍은 배치 프리뷰 근거만; 추가 디테일 보존 경로와 WM_CLOSE 결함은 남았다.
과거 G1/lap275~379 승인·반려·미결 계보는 전체 원문 `20260917_234449_status_pre_cutoff_compaction.md`(SHA 9400241176cce4bbe0047b358a887f09e269d9824a253654d6ff2718d352ddef,141줄)에 보존했으며 fresh 제품 PASS/출시 승인으로 승격하지 않는다.
| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | native PS3 PASS·원본구도 FAIL·제품 미완료 | stock UI 클릭 PS9→PS7→PS5→PS3 tick3, native `1600×1200×8bpp/pitch1600`/viewport 전역 PASS; 월드 시야 확대·스프라이트/HUD 원본 픽셀 크기라 G1 배치 FAIL, 고해상도 SPR·생산·종료 미검증; 이번최종acquisition은초기화guard8000001A에BLOCKED |
| G2 | 8-slot고전비 초기USED/cap5000·실제24k baseline 관측/제품 미완료 | 1160HPpositive 초기군대→원본자연simulation Δ24124ticks/725sec 오류0/cleanup0잔류;25dead→gap→slotreuse 관측·owner4resrelease·원본풀peak1176. owner1USED5003은 lap389가 **정적 원인확정**(transfer `0x476ED0`→`0x43EE30`에 cap검사 없음=원본 허용)했고 사전거부는 NO_GO; **F4 장부랩 위험 신규**. 임의저전비대군/global1199·ordinaryowner242 확장/경제·확장save/LAN 미완료 |
| G3 | 사용자 지시로 중단·활성 범위 제외 | 16 PlayerStruct가 bulk save112,036B 초과, self/opponent mask8bit라 owner8~15 표현 불가; 활성9~16/LAN 미완료 |
| G4 | 원본 issuer 국소 이동 PASS·제품 미완료 | 직접 command 기록은 정지; mainthread 원본 issuer는 같은 source 이동68좌표. current waypoint reinforcement 수리 후 AI2기 이동21/22좌표·목표gap2/1 PASS; one-shot2회 같은 이동 결과, 발행tick다름·지속 정책/품질 미검증; 이번정상AI512+load11 관측만PASS/정확postload미확정 |
## 다음 한 가지
**W4 §5 실행을 다음 work 회차가 진행한다(승인 불필요).** lap401 work가 W4 §1의 B-1을 구현했다:
새 모듈 `tail_relocation_storage_layout_v1.py`가 pool/existence/age 세 배열을 `.rsrc` 아래
이미지 꼬리로 실제 재배치하며, N=1210 후보의 `b3_fixup_site_counts`가 카드 필수치
`{"unit_pool":1014,"unit_existence":34,"unit_age":4}`와 정확히 일치(이전 lap399는 `unit_pool:0`
미적용이 REJECT 사유였음). N=1200 항등·G-a(원본에 목적지 참조 1건뿐, 비주소로 기지)·G-b(bulk
blob 참조 3172→3132, 신규/변경 0건 — catA/catB/active 무손상 확인) 전부 PASS(정적, 기계 산출
`docs/history/laps/probes/out/20260920_lap401_work_g2_pool_tail_relocation.json`). 구현 중
`_patch_literal`의 고정16B 윈도우가 read-modify-write 리터럴 중복으로 오탐하는 결함을 발견·수리
(명령 자신의 길이로 재디코드). **아직 게임을 실행하지 않았다** — 다음 회차는 W4 §5 순서
(P-0 양성 대조군 → S-1 → S-2~S-5)를 그대로 따른다. 저장/LAN은 W4 §6대로 후속 필수 blocker.
## 지금 막힌 것 (Blockers)
- **F4(lap395 확정): 안전상한 UNKNOWN — 어떤 uniform cap도 랩을 막지 못한다.** lap394 반례 독립 재현 ACCEPT(12001/32761/40001 일치); lap393 P9의 assertion은 `32767//8` 상수 산술 2개뿐이라 불변식 산문을 인증하지 않는다. **신규:** 생산 gate `0x43EDA0`은 count cap `+0x2010`·supply cap `+0x2012`를 둘 다 강제하나 `roster_add 0x43EE30`은 `cmp ax,0x4B0`(배열1200)뿐이고 두 cap 참조 **0건** ⇒ 이전은 두 cap을 모두 우회. donor 이전+gate-legal 재생산 **펌프**로 수신 used가 cap 1500/4095/5000 **전부에서 32,785 도달**(차이는 재생산 799/87/7회뿐) ⇒ **cap≤4095 안전상한·§7.6 분기 A 전제 무효, 즉치2개 카드 착수 근거 상실**. cap5000은 펌프 없이 이전만으로도 1160기/40,000 집중 가능(1160≤1200). 남은 상한 `min(1200,풀)×최대비용`은 손익분기 평균 27.31 vs 실측 평균 31.66~34.42 ⇒ 37,988~41,309>32,767로 **구제 실패·cap 비의존**. 최대 단위비용은 비용표 `0x9B5238`/type표 `0x66B81D`가 `.data` raw끝 `0x4F9000` 바깥 BSS라 **정적 불가**(W2가 실측). P1~P4 바이트 사실·lap389 NO_GO·lap391 수치는 유지. 실제 게임 도달성 UNKNOWN.
- **현재 G2 구조통합 blocker:** 저비용 다수 구성의global1199/ordinaryowner242 확장에 필요한 Unit·보조 인덱스·bulk-relative alias·초기화/수명주기·저장/LAN의 일관 계약 미구현. 두 actual 진단은局所getter追加로 정상simulation에 도달하지 못함. 개별PC따라 패치 반복중단; 제품완료/전체불가능 선언없음. **lap381이 닫은 것은 layout 선행질문(C1 count폭·H1 matrix형태)뿐이며 이 통합 blocker는 그대로다.** **lap385 신규 실측(Astra 큐, 승인대기·작업은 계속함):** 핀된 save`0x440F02`(len`0xE397C`,src`0x892410`)/load`0x4412DC`가 정의하는 bulk blob `[0x892410,0x975D8C)`이 existence/age/catA/catB/active **5개 영역을 내부에 품는다**(unit_pool만 bulk 아래, 별도 roster). ⇒ 확장은 `0x892410`을 slot당1,880B 밀어올리는 **동시에** 고정길이 blob 내부를 slot당14B 불린다(N=4001→새 start`0xD97DE8`/필요 len`0xED2AA`); 둘 다 하드코딩 push 즉시값이라 **layout mapper만으로 저장호환 확장은 원리적으로 불가**하고 길이·주소 즉시값 fixup+저장포맷 변경이 필수다. lap379 Sol의 integration/broad-patcher/runtime NO-GO를 **뒤집지 않고 강화**한다. **새 불가능 증명 아님** — G2를 이 경로로 계속할지는 Astra 판정 사항. **lap388 종결:** 레이아웃 계산기 카드는 ACCEPT·계약5 CLOSED로 닫혔으나 이 통합 blocker는 **그대로다** — 오히려 "길이·주소 두 하드코딩 즉시값 fixup+저장포맷 변경 필수"를 수치로 굳혔다(`loop/ESCALATE_SOL` 판정 대기). **lap397 범위 정정(무효화 아님):** 이 통합 blocker는 owner당 1200기 초과와 저장호환에만 걸리며 **풀 확장 스파이크의 임계경로가 아니다** — `roster_add`의 `cmp ax,0x4B0`은 owner 유닛 **개수** 제한이고(`0xD4A+1200*4==0x200A` 검증), 유닛 1200기 미만 owner는 PlayerStruct 무변경으로 slot id≥1200을 담는다.
- **G4 persistent STOP:** 비지원 mode 제외와 post-load 첫 tick/중복 계약 미확정(`BLOCKED_MODE_EXCLUSION_AND_POSTLOAD_CONTRACT`); normalcall/owner/serializer·one-shot2회 이동과 이번shadow512+load11만 보존(정확load완료marker없음). **과거 lap379 provenance:** test pre-image SHA 충돌은 역사 검증 UNKNOWN으로 보존하되 fresh 현행 SHA의 제품 실행을 차단하지 않는다. 재핀·자가 baseline 승격은 계속 금지한다.
- **과거 G4 fresh AI runtime 실패(보존; 현재 chain 진입/180초 실행은 가능):** current bridge `592d03ec…0b3030`, old `f44090a3…adac4b`, ddraw override on/off 모두 PS40/tick0·동일 serious-error 이미지 `008e8465…6e3cd9`. 당시 bridge/renderer 두 가설 소진으로 반복 STOP한 기록; temp `Syw2plus_patch/g4_ai/`, residue0.
- **원본·후보 S1/화면·세 입력 PASS:** logical load-button `(316,372)` 1회로 PS35→PS3, 8 PlayerStruct 각각 save000과 일치. 원본800×600/후보1600×1200 PS35 실제 메뉴 캡처는 최근접 2배 뒤 **exact100%/MAE0**, PS3는 별도 쌍 exact99.213%/MAE0.470. 동일 source SHA fresh 미니맵 쌍 `(35,560)` camera `(39,53)→(49,159)`; 선택해제 쌍 `(400,220)` count `1→0`/first_slot `1174→0`; 드래그쌍 `(520,200)→(780,455)`은 clear0→count3/first_slot108 모두 동일. cleanup0잔류/후보 ini 원복. 첫 `(150,520)`은 원본 무효라 실패 보존. 생산·종료·장은 UNKNOWN.
- **lap332·lap334 probe가 rc1로 영구 실패(재pin 금지 → `loop/ESCALATE_SOL`):** 두 probe가 살아 있는
  `tools/runtime_env.py` SHA를 lap330 값 `997ff15b…cc46eed`로 단언하는데 봉투 §11이 허가한 lap335 편집이
  `922a267c…f8a2575`로 바꿨다. **W3와 같은 형태이자 lap334 N12 재발.** **분해(lap337·lap339 재현):** `failures`는
  살아 있는 SHA 단언이 **전부**(2건·1건)이고 나머지 단언은 지금도 통과 ⇒ 복구 불가는 lap331 run의 "검수
  SHA==실행 SHA" **동일성 재확인 하나**뿐(**영구 UNKNOWN**). 기준선 `922a267c…f8a2575`/`c04a6265…d769823`.
  **lap339 새 근거:** 필수 게이트 어느 것도 `docs/history/laps/probes`를 실행하지 않는다(pytest testpaths·ruff
  대상·mypy 명시 파일·safety.sh 전부 밖) ⇒ rc1이 게이트를 깨거나 가리지 않는다. lap338 §2.1 ACCEPT. W3는 미결.
- **N14(lap339, 승격 대기):** `checks/context_limits.py`의 STATUS cap은180이라 PROMPT의130줄을 강제하는 필수 게이트가 **없다**. lap323·lap333·lap338이 손수 쓴 길이 assert FAIL로 바퀴를
  소모했다(lap338의 131>130은 저장소 게이트가 아니었다). 게이트 조이기 제안은 승인 대기, R-a/R-b와 묶지 않는다.
- **후보 봉투(lap334) 확정 사항과 남은 사각:** 후보=동일 EXE+고정 ini(`918e7043…a5a2`→`f0ce9e64…6785`)+
  `ddraw=n,b`+private `game/ddraw.dll` 로드 단언. 좌표는 **무배율**이 판별됐다(lap148 ×2 클릭 PS9 FAIL vs
  lap154 unscaled `(184,560)` PS9→PS7→PS3 PASS, 둘 다 client 1600×1200·scale[2,2]). **N10:** 압축본 이름은
  `status_lapN_compaction`=lapN 종료 시점. **N11:** 하네스 `input_scale`은 기록용이며 클릭에 곱해지지 않는다.
- **정정 C1(lap332·lap334 재유도, 수치 영향 0):** 디스패처 `0x4233B8`은 테이블 전에 `cmp eax,0x28; jg 0x42351F;
  je 0x423515` 사다리를 갖는다(>40 arm 머리 `cmp eax,0x131`). lap326 §1이 빠뜨렸다. PS `40/150/180`은 찢김이 아니라
  **정당한 상태값**이고 35는 테이블 34번(`0x42341B`)이라 판정식 영향 0, 레지스터 store 33건 fail-open은 그대로다.
  **N8:** lap331 기록/STATUS가 이 3건을 미공개했다.
  **N9:** `manifest.runtime_config`는 prepare 스모크(`1024x768x24`, `(184,560)`)를 기술하며 R1 run을 기술하지 않는다.
- **R1 범위 밖 미검증:** fresh 원본/후보 동일상태 pair·PNG·WM_CLOSE·S1/F2-R2 결정성 없음. 배분 40/20/15/15는 가정.
- **exact-site 계측 불가(lap324 확정, lap326 유지):** 읽기 수단은 `process_vm_readv` 폴링뿐이고
  `process_vm_writev`/`ptrace`/`int3`/`winedbg`/`gdb` **0회**. 기구를 만드는 것 자체가 금지 위반이다.
  R1은 exact-site를 포기하고 **산출물(origin 전역)** 을 읽는다. 이 포기는 lap326에서도 유지된다.
- **lap324 §2.3 정정(lap326 기록):** E8-only 그래프가 `0x4A2FF5` 꼬리 `jmp`를 놓쳤다. 사슬 `0x423411→0x4248E0→
  0x4A2FF0→jmp 0x493C40→push 8→0x4D6A00→0x4D60B0→x·y·tag→ret→0x4248E5 PS:=35`는 전 간선 무조건 ⇒ PS==35는 세
  store 뒤이고 게이트된 1회 read에 찢김 없음(lap332 7지점 재유도). 수치 영향 0.
- **도달 판정식(lap326 확정, lap332 C1로 보정):** PS는 WORD@`0x4ED818`, 점프테이블 `0x423738` 35엔트리(인덱스 PS-1,
  PS9→`0x423407`/PS34→`0x423411`/PS35→`0x42341B`). PS 즉시 store 71건 중 값 35는 1건(`0x4248E5`), origin 미참조라
  순환 아님. **fail-open: 레지스터 store 33건 값 미상.**
- **저장/불러오기 절대 좌표 — 원본 baseline은 lap331/332가 실측했다.** 중심식이 sprite 크기로 origin을 만들어
  `ds:0x1088B5C/5E/60`에 16-bit 저장(직접 store 1/1/2, 전부 BSS 0). 예측 (P1) PS9 pre `(0,0,0)`·A `(240,145)`·
  `tag==8`이 **전부 실측과 일치**했고 B `(160,85)`와 R6(초기 모드 3→800×600)은 그대로다. **잔여 fail-open:**
  계산/간접 writer 미배제(N2), `0x4D60B0` 조기 반환 시 post==pre==0 → UNKNOWN. 원문은 lap326·lap332 기록.
- **좌표계는 해소(lap326).** 이미 PASS한 타이틀 입력이 변환을 고정한다(`root=content_crop+client`, 실증
  `(184,560)`→PS9→PS7, scale 1.0). `(296,505)`는 같은 좌표계·같은 변환이라 새 근거가 필요 없다.
- **map↔dialog 실제 event/thread 순서 UNKNOWN(lap308~316·lap322).** 정적 사실: 앵커 일치, `0x431AB0` 직접 caller
  `0x48F538` 1개, `0x4D60B0` caller 2개, 640×480 reset writer 2개가 성공 return **지배**, 실패 경로 runtime writer
  **0개**, lap310 절대 dword 리터럴 **0건**(계산 포인터 배제 불가).
- **R2 = 4회 독립 재유도(lap314·316·318·320) + lap324 재확인.** 창/entry **753**, 실패 arm **7**, 성공 arm **724**,
  unresolved **0**, 화면 전역 직접 store **4건** `{0x431B79,0x431B7F,0x4324B8,0x4324C2}`, gate `0x431AF2`=`750a`→
  `0x431AFE`. D1 공허성은 22-노드 증인 경로로 재확인. 원문은 lap314~320 기록.
- **F1 = 종결(lap319 수리 → lap320 ACCEPT).** 결함=objdump 접힘의 무징후 절단, 수리=명령 단위 길이 불변식; 접힘 27 전부 절단·초과 0. 원문은 lap319/lap320 기록.
- **N4·N5·N6·N7(수치 영향 0, 완화 아님, 원문은 lap320·lap322·lap330 기록):** (N4) lap319 KeyError 함정은 lap327이
  형태를 재사용하지 않아 미발동. (N5) gate 2B 교차검증으로 닫힘. (N6) `G1_R1_WAIT_PS_STATES=(9,35)`와 lap328 F4로
  해소. (N7) 클릭 후 `post` 대입 전 예외를 TIMEOUT으로 적는 삼항은 lap331 run 미발동(후보 경로도 같은 형태).
- **UNKNOWN 유지(F1 범위 밖):** (N1) 지도 창 간접 분기 0개라 lap315 E1 수리는 실제 대상에서 inert(합성 fixture만
  실행). (N2) 창 안 call 31개 fall-through → callee 쓰기·cross-function 순서·D5 under-claim·계산/간접 writer·실제
  실행 모두 UNKNOWN. (N3) 접힌 행의 `ds:0xB3AC88`=`0x33F`/`0xB3AC8C`=`0x1FF`는 화면 전역 아님, 의미 UNKNOWN.
- **lap312 강화 사실 유지:** 네 writer 전부 성공 경로 필수, `0x4324C2` 이후 도달 명령 4개에 화면 writer **0개** →
  성공 반환 시 마지막 직접 쓰기는 640×480 reset. **화면 전역 writer 하한 20(lap306):** 절대 4 + mode-table 16,
  `push 0xE5BF18` 291개 전부 `0x465250`; computed/indirect fail-open. lap310 정정(ii): `test_call_convention_
  cleanup_is_explicit`는 상수표 동어반복이라 독립 증거가 아니다.
- **provenance 회귀(전부 보존, 고쳐 쓰지 않음. 원문은 lap301·306·311·322·324 기록):** (a) lap299 report 재현 불가·
  lap301 `"lap": 299` 오기, (b) lap306 V2 자칭 lap 드리프트, (c) 손 전사 JSON의 SHA 무효, (d) lap311 `a33f216a…
  8fd4524`, (e) lap322 `7d04b9b2…35757ac`, (f) "테스트 수 불변 ⇒ 소스 무변경"은 증거가 아니다, (g) **정정 대기:**
  `player_offsets.md`의 `0x00B92CC0` 행은 **WORD·다음 상태 요청**(수치 영향 0, 별도 카드), (h) **N16(lap391 확정):**
  lap390 기록 본문의 `samples.jsonl` SHA `d7bf3e1f…`는 오기이고 "analysis `source.sha256`와 일치" 주장도 거짓이다
  (실제 `76903a8d…`, `d7bf3e1f…`는 같은 JSON의 `cost_evidence.sha256`). lap390의 기계 산출물 `output.json`은 올바른
  값을 담아 **수치 영향 0**이며 결함은 손 전사 1줄에 국한된다. (c)의 재발. 원문은 고쳐 쓰지 않고 lap391 기록이 정본.
  재발 방지(LAP_TEMPLATE에 "fixture SHA는 기계 산출물 필드 인용" 명시)는 승인 대기, N14와 묶지 않는다.
- comparator는 scene 4축과 선택 slot만 본다. nation/slot id/절대 selection·camera/tick은 기계 검사 밖이라 (B) 원시
  필드 대조로만 확인하고 overall PASS도 충분조건이 아니다. `scene.owners`=owner0~7 → owner8~15 미가시(G3 위험).
  R17 재결 미완료·R31 금지, R29 거부(lap266), R30 M11 생존, R6-B-R2 count 1→0 미결, lap274 M-d/M-e 드리프트 사각.
  offline 8건 주차: H=F2-R1/F3-R1/F6-R2, C=R23/R24·stage_budget_state, N=R20/R21/R22.
  **W2(lap296 §4.7.4):** `runtime_driver.py` 매직 리터럴 — `0x8990C8`·`0x66B790`/`0x758` 승격 가능, `0x8D` 가드 선행, `0x8E` 명명 금지.
- **W3(lap300 §4):** lap296 review probe의 `EXPECTED_SHA["target_probe"]`가 수리 전 SHA를 가리켜 영구 exit1. 재pin은
  자가 갱신이라 middle/work 단독 금지 — Astra/사용자 결정 대기. lap302~332 probe는 자기 산출물 SHA를 단언하지 않아 이
  함정을 피한다. **가드 잔여 사각:** `type`/`owner` 가드의 값 드리프트, lap301 `contains_all`, lap303 앵커의 중심식 4쌍.
- 후보 WM_CLOSE teardown 결함·후보 scene/input evidence·G2~G4 증거 미해결. lap279/280/284-middle probe는 아직 `0x440FF0` 창을 써 legacy window 오분류 위험. **lap292 사각:** 이름 결합 단언이 reader 이름을 안 봐 폭 드리프트 통과.
- **프로세스 사각:** 상수/앵커 승격 시 결합된 과거 probe 미재실행 → 잠복 결함 재발(lap294·lap296). **provenance:** lap287
  경고=lap290 부록, lap293/lap297/lap317 `ESCALATE_SOL`=각 lap294/298/318 부록 A, lap321=lap322 부록 A, lap323=lap324
  부록 A, **lap325=lap326 부록 A(소비)**, **lap380=lap381 부록 A(소비)**. lap300~325 STATUS 원문=각 압축본.
- map-layer serializer **28쌍** 모델은 lap286이 재현해 ACCEPT(`1,400,702`+`30.5`). 한계: 네 fixture가 정사각·짝수라
  오프셋 210/212 배정과 halving layer 구분 불가(lap322 §14.1 REJECT 사유), owner `+0x8E` 상속·save/load 동일성
  미검증, save000/save006 유지는 §7 카드 4항 미산출로 잠정.
- **G3 저장 포맷:** bulk `0x892410..0x975D8C`에 PlayerStruct 8개는 들어가나 16개는 `0x1B5A4` B 초과 → 9~16번 직렬화 공간 없음. G1 범위에서 수리하지 않는다.
- **실행 봉투(lap284 §5→lap322→lap326→lap331→lap334):** (a)~(e) 미제출 행은 R1 봉투가 대체한다. 네 실패 모드
  선언은 필수이고 lap326이 `pending_state`·`origin_tag`·`ps_word`/`ps_dword`를 추가했다(자동 연장·재시도 금지).
- **Plan C 함정(lap298 §10.3 봉인 유지):** 공유 temp `…_21_load_screen.png`(`5e95ed92…d17e5879`)는 원본 로드 대화상자가 **아니다**(Plan C `save_load_screen.cpp` 출처) → 좌표 출처 금지. **주소 실재≠좌표 출처 적격.**
- **lap301~336 probe의 제품 한계:** 앵커·pin·모드 테이블·CFG 지배·상태 전이 순서·하네스 분류/게이트는 정적/합성
  확인일 뿐 **구성 시점 전역값은 실행 없이 미관측**, hitbox·슬롯 선택·로드 전이는 UNKNOWN. tick 순환 의존은
  lap297~298에서 해소(연구 쌍 tick은 report-only, 제품 S1 (A)+(B) 불변).
## 검증 상태
**2026-09-20 lap401 work(Sonnet5/high) — W4 §1 B-1 재배치 구현(정적 PASS, 게임 미실행):**
신규 `tail_relocation_storage_layout_v1.py`(N=1200 항등, N>1200은 pool→existence→age 꼬리 packed)
+ `g2_unit_pool_expansion_v1.py` 재배선. N=1210 `b3_fixup_site_counts`가 카드 필수치와 정확 일치
(`unit_pool:1014` — lap399 REJECT 사유였던 0 적용이 해소됨). G-a(원본 목적지 참조 1건, 비주소 기지)
· G-b(bulk blob 참조 3172→3132, 신규/변경 0) PASS. 구현 중 `_patch_literal` 고정윈도우가
read-modify-write 리터럴 중복을 오탐하는 결함 발견·수리. 신규 pytest 11건(24건 중 신규분 포함).
`make check` rc0 **739 passed**(728→739) 225.45s+Ruff/compileall/mypy10 Success+`CONTEXT_PASS`,
**`SAFETY_PASS`**, 원본 2경로 재해시 불변. probe rc0 `failures=[]`
(SHA `73efeb2b…4e8ec8`, 산출물 `33f0c66e…298e2118`). 제품 게임실행 0, 메모리쓰기 0, 커밋 0.
상세 `20260920_lap401_work_g2_unit_pool_tail_relocation.md`.
**2026-09-20 lap400 middle(Opus5/high) — lap399 독립 검수: C1/C2/C3 ACCEPT, 후보 N=1210 REJECT(정적, 게임 미실행):** 신규 read-only probe rc0 `failures=[]`(`20260920_lap400_middle_g2_pool_overrun_probe.py` SHA `a52c36fc…a4f83476`, 산출물 `734eb0b2…2f06f287`). 재현 ACCEPT: N=1300 위험·사이트 카운트(pool 986/28)·후보 SHA `303c78f8…` 재생성·N=1200 항등·원본 불변. **REJECT 근거(신규):** 풀 delta 0·풀 fixup 0건 적용 ⇒ 제자리 성장이 live state/bulk blob 머리 18,800B를 침범(리터럴 1,311건 미수정). 부수: 재배치된 existence/age 목적지 `[0x89DA38,0x89ED20)`는 bulk blob **내부**라 save000 `fread`가 덮음. C4(`PS=40`)는 대조군 `trace.jsonl` 31표본 전부 `ps=40`로 **실재 ACCEPT**하나 같은 run의 원본 파일명 PS9 **양성 대조군이 없어** 파일명의존 vs 환경회귀 미구분(배제됨: driver profile 문자열·`dxwrapper.ini` Include/ExcludeProcess 공란). `make check` rc0 **728 passed** 207.74s+Ruff/compileall/mypy10 Success+`CONTEXT_PASS`, **`SAFETY_PASS`**, 원본 2경로 재해시 불변. 제품코드/바이너리/게임실행/메모리쓰기/커밋 **0**. 상세 `20260920_lap400_middle_g2_pool_overrun_reject.md`.
**2026-09-20 lap398 work(Sonnet5/high) — W3 §B-4 fail-open 3건 종결(정적 판정, 제품/런타임/마일스톤 승인 아님):** 신규 read-only probe **rc0 `failures=[]`**. FO-1 PASS(986건 균일delta 유효, slot0=type-indexed 정적테이블 점유 신규확인). FO-3 PASS(gap WORD1600개, 배타적). **FO-4 PASS+신규:** `cmp 0x00421349`/`0x0048f4b4`는 pool과 무관한 선행 정적테이블(`0x669c38..0x66b790`,50×140B)의 루프 종료조건 ⇒ **fixup 하드제외 필수**(포함시 무한/조기루프). `make check` rc0 715 passed 117.25s+Ruff/compileall/mypy10 Success+`CONTEXT_PASS`, **`SAFETY_PASS`**, 원본 재해시 불변. 제품코드/바이너리/게임실행/커밋 **0**. 상세 `20260920_lap398_work_g2_unit_pool_fo_closure.md`.
**2026-09-20 lap397 middle(Opus5/high) — 풀 확장 스파이크 정적 표면 측정:** slot색인은 pool/existence/age 3개뿐(active·catA·catB는 count색인), `0x892410` 별칭179건 전부 bulk base(수정불필요), 풀변위후보986건 전부 stride버킷0, 할당자 상수 3개+전멸루프1개, 제자리확장 NOT_FEASIBLE(재배치 필수), 새공간은 이미지 꼬리 확장 필요. `make check` rc0 715 passed+`SAFETY_PASS`, 원본 불변. 제품코드0. 상세 `20260920_lap397_middle_g2_unit_pool_expansion_surface.md`.
**lap388~395 G2 전비장부 cap 조사 계보(압축, lap398. 각 lap 기록 전문은 `docs/history/laps/20260919_lap389_*.md`~`20260920_lap395_*.md`에 보존):** lap389 owner-transfer 사전거부 NO_GO+신규F4(16bit장부/40,000합) 발견→lap390 W1 NOT_FEASIBLE(fixture한정)→lap391 ACCEPT+F4생존→lap392 Astra BLOCKED→lap393 cap≤4095 산출(이후 lap394 Astra 반례로 무효)→lap394 반례제기→lap395 반례ACCEPT+**4095도 무효, 안전상한 UNKNOWN 확정**(펌프로 세cap 전부 32,785 도달; cap5000은 펌프없이도 1160기/40,000으로 도달 가능). 전 회차 `make check` rc0 715 passed+`SAFETY_PASS`, 원본 불변, 제품코드/게임실행/커밋 **0**. `ESCALATE_SOL` §9로 열려있음(사용자 우선순위변경으로 후순위, 철회아님). lap397~398 풀확장 스파이크와는 독립 트랙.
**lap380~388 G2 레이아웃 카드 계보:** 개별 lap(380 C1/H1→381~383 REJECT/수리→384~387 수리/구현→388 ACCEPT
종결) 상세는 아래 「바퀴 기록」 압축 줄과 각 lap 원문(`docs/history/laps/20260918_lap38{0..8}_*.md`)에
보존. 전 회차 `make check` rc0+`SAFETY_PASS`, 원본/frozen 불변, 게임실행/커밋0.
**2026-09-15 product-first:** 원본·후보 실제 S1 load·PS35 메뉴 exact100%·PS3 이미지99.213%, 미니맵 camera·선택해제 count·드래그 count3 대칭 PASS; save000 8/8, cleanup/residue0, 후보 DxWrapper ini 원복·private ddraw module PASS. private G1 설정 draft SHA `f0ce9e64…6785` 산출(Windows native/출시 아님). targeted G1 62+profile6, G2 xref2; 통합 Fast442·Ruff/compileall/mypy/CONTEXT·safety2 PASS. G2 숫자패치만으로 전체8인 안정성 불가; 저장 save000/006 중 활성8인 fixture 없음, 원본 풀끝 `0x892410`은 live state 시작과 일치한다. G2 SHA-pinned 정적 xref inventory 후보 allocator18/spawn29/destruction13/save1/load1이나 경로 불완전/activation NO-GO. G4 원본 A* `[1]` PE 바이트 확인, 반복 비교 fixture 없음/제품 변경 NO-GO.
**2026-09-16 G4 path preflight/AI(압축, 전문 lap382 compaction+`20260916_g4_waypoint_*.md`):** pinned EXE/PE entry·UnitStruct reader PASS, original 2-run 결정론 BLOCKED. cooldown 후보 둘다 NO-GO. AI2기 waypoint reinforcement 수리 후 이동21/22좌표 국소 PASS; UI tail minimap FAIL 보존, 제품 AI/길찾기 완료 아님.
**lap356~370 검증 계보(REJECT/RELEASE 반복, 제품·게임 0회):** 각 lap 기록 및 `20260912_status_lap356_compaction.md`/`20260912_status_lap366_precompaction.md`/`20260918_status_lap382_compaction.md`(150줄 SHA `60a0d91d…d74659d5`)에 전문 보존.
## 바퀴 기록
lap401 work: W4 §1 B-1 재배치 layout 모듈 신규 구현+재배선, `unit_pool` fixup 0→1014 적용
해소, N=1200 항등·G-a·G-b 정적 PASS, `_patch_literal` 윈도우 버그 발견·수리, 신규 pytest 11건.
게임실행 0, 커밋 0. 다음: W4 §5 실행(P-0→S-1→S-2~S-5). 상세 `20260920_lap401_work_g2_unit_pool_tail_relocation.md`.
lap400 middle: lap399 후보 독립 검수. C1(N=1300 위험)/C2(사이트 카운트)/C3(후보 재현·항등·원본불변) **재현 ACCEPT**, C4는 부분 ACCEPT(양성 대조군 없음). **후보 N=1210 REJECT** — B-1을 base-preserving 계산기에 위임해 풀을 재배치하지 않았고(fixup 0/1014 적용), 제자리 성장이 live state 18,800B를 리터럴 1,311건 미수정인 채 침범. 올바른 목적지(이미지 꼬리)는 리터럴 1건뿐임을 같은 방법으로 측정. W3 SUPERSEDED 표기, 후속 카드 W4 발행, P-0 양성대조군을 실행 전 필수로 추가. 게임실행/제품바이트/커밋 0(컨펌 역할). 상세 `20260920_lap400_middle_g2_pool_overrun_reject.md`.
lap399 work: W3 §B-1~B-3 실구현. 신규 `g2_unit_pool_expansion_v1.py`가 N=1210 후보 생성(N=1200 항등 회귀 PASS, 사이트 카운트 2개 독립 probe와 일치). 신규발견1: N=1300은 catA/catB/FO-3-gap 물리침범 위험 → N=1210 채택(N<=1217 상한). 신규발견2: 후보 기동시 PS=40 정지는 패치 결함 아님을 대조군(파일명만 다른 원본)으로 확정 — 파일명 의존 실행 제약. S-1 BLOCKED(패치 무관, 다음 입력 명시). make check rc0 728 passed(715→728)+`SAFETY_PASS`, 원본 불변, 게임크래시0/커밋0. 상세 `20260920_lap399_work_g2_unit_pool_expansion_candidate_and_boot_probe.md`.
lap398 work: W3 §B-4 fail-open 3건(FO-1/FO-3/FO-4) 전부 바이트로 **PASS 종결**. FO-1은 원가설(전부 slot색인)을 정정 — slot0은 type-indexed 정적테이블이 점유하며, 통짜 블록 재배치 설계(§B-1)는 그대로 유효. FO-4는 신규 발견: `cmp 0x00421349`/`0x0048f4b4` 2건은 pool과 무관한 선행 정적테이블의 자기 루프 종료조건이라 **fixup에서 하드 제외해야 함**(포함 시 무한/조기루프 결함) — §B-3에 반영 필요. FO-3은 gap WORD배열(1600개)이 pool/existence/age와 배타적임을 재확인. 제품코드/게임실행/커밋 0(정적 재검증) — 다음 회차는 재조사 없이 즉시 구현(재배치+상수+fixup 적용, 위 제외목록 포함)과 격리 실행 착수. 상세 `20260920_lap398_work_g2_unit_pool_fo_closure.md`.
lap397 middle: 풀확장 정적표면 측정 — 재배치3영역+상수4개+fixup1,016건만 필요, 나머지(active/catA/catB/roster/별칭179건) 불필요를 바이트로 확정. 제자리확장 NOT_FEASIBLE, 재배치 **구조적 FEASIBLE**. lap385/388 통합blocker·lap389 NO_GO·`ESCALATE_SOL`§9 F4는 뒤집지 않고 후순위. work카드W3(fail-open4건 포함)로 인계. 상세 `20260920_lap397_middle_g2_unit_pool_expansion_surface.md`.
lap389~395 cap조사 계보(압축, 요약은 위 「검증 상태」 lap388~395 항목과 동일 — 개별 lap 판정/STOP 사유는 각 원문 파일 `20260919_lap389_*.md`/`20260920_lap39{0,1,3,4,5}_*.md`에 보존): lap389 NO_GO+F4발견→lap390 NOT_FEASIBLE(fixture한정)→lap391 ACCEPT+STOP(F4기준 판정대기)→lap392 Astra BLOCKED→lap393 cap≤4095 산출+STOP(목표숫자 변경권한없음)→lap394 Astra 반례제기→lap395 반례ACCEPT+**4095도 무효, 안전상한 UNKNOWN 확정**, W2 카드 인계(이후 우선순위변경으로 lap396 안전종료). `ESCALATE_SOL` §5~§10 전부 열려있음(닫힌 것 없음, 철회 없음).
**lap380~388 G2 레이아웃 카드 계보(압축, 전문 `docs/history/laps/20260918_lap38{0..8}_*.md`, 압축전 STATUS `20260920_status_lap391_precompaction.md` SHA `d168c947…eed7abb6`/135줄):** lap380계획→lap381 C1/H1 CLOSED→lap382work→lap383middle REJECT→lap384work수리→lap385middle ACCEPT→lap386~387work→lap388middle ACCEPT·**레이아웃 카드 종결**(재수리 없음). 전회차`make check`rc0+`SAFETY_PASS`, 원본/frozen불변, 게임실행/커밋0. `native_route_judgment`NO_GO 미변경. 종결리포트`docs/reports/20260918_G2_LAYOUT_CARD_CLOSURE.md`. 상위 통합blocker는 위「지금 막힌 것」에 그대로 살아있음.
lap377 Astra 방향 → lap378 middle ACCEPT → lap379 provenance BLOCKED 뒤 사용자 product-first 지시로 반복 중단.
lap356~376 상세(import 해소·§3 RELEASE, REJECT/수리 반복, 게임/커밋 0회)는 각 lap 기록과 `20260912_status_lap361_entry.md`(SHA/124줄)에 보존.
