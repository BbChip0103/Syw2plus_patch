# STATUS — 매 바퀴 갱신하는 기억
## 지금 상태
활성 G1/G2/G4 제품 미완료(0/3); G3 최대16인은 2026-09-17 사용자 지시로 중단. **G2 최우선·9/18 Claude Code 역할로 재개 승인**; G1/G4 후순위 유지. M1/G1 요구 유지: 원본 구도·입력과 차후 고해상도 그림의 디테일 보존을 함께 만족하는1600×1200 화면. 제품 기준은 DESIGN, 사람 승인
원문은 feedback/APPROVALS·INBOX를 따르며 2026-09-12 01:03 bounded repair→fresh validation 허가는 제품/출시 승인이
아니다. DxWrapper 2× 화면·S1 입력쌍은 배치 프리뷰 근거만; 추가 디테일 보존 경로와 WM_CLOSE 결함은 남았다.
과거 G1/lap275~379 승인·반려·미결 계보는 전체 원문 `20260917_234449_status_pre_cutoff_compaction.md`(SHA 9400241176cce4bbe0047b358a887f09e269d9824a253654d6ff2718d352ddef,141줄)에 보존했으며 fresh 제품 PASS/출시 승인으로 승격하지 않는다.
| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | native PS3 PASS·원본구도 FAIL·제품 미완료 | stock UI 클릭 PS9→PS7→PS5→PS3 tick3, native `1600×1200×8bpp/pitch1600`/viewport 전역 PASS; 월드 시야 확대·스프라이트/HUD 원본 픽셀 크기라 G1 배치 FAIL, 고해상도 SPR·생산·종료 미검증; 이번최종acquisition은초기화guard8000001A에BLOCKED |
| G2 | 8-slot고전비 초기USED/cap5000·실제24k baseline 관측/제품 미완료 | 1160HPpositive 초기군대→원본자연simulation Δ24124ticks/725sec 오류0/cleanup0잔류;25dead→gap→slotreuse 관측·owner4resrelease·원본풀peak1176. owner1USED5003은 lap389가 **정적 원인확정**(transfer `0x476ED0`→`0x43EE30`에 cap검사 없음=원본 허용)했고 사전거부는 NO_GO; **F4 장부랩 위험 신규**. 임의저전비대군/global1199·ordinaryowner242 확장/경제·확장save/LAN 미완료 |
| G3 | 사용자 지시로 중단·활성 범위 제외 | 16 PlayerStruct가 bulk save112,036B 초과, self/opponent mask8bit라 owner8~15 표현 불가; 활성9~16/LAN 미완료 |
| G4 | 원본 issuer 국소 이동 PASS·제품 미완료 | 직접 command 기록은 정지; mainthread 원본 issuer는 같은 source 이동68좌표. current waypoint reinforcement 수리 후 AI2기 이동21/22좌표·목표gap2/1 PASS; one-shot2회 같은 이동 결과, 발행tick다름·지속 정책/품질 미검증; 이번정상AI512+load11 관측만PASS/정확postload미확정 |
## 다음 한 가지
**lap392 Astra: 근거 불명확으로 STOP·ESCALATE_SOL 유지. 승격 middle이 lap391 V2의 간격 내 패배/흡수 배제 불변식을 검수하고, 미입증이면 UNKNOWN으로 정정한 뒤 정상 명령 기반 bounded work probe를 인계한다.**
- 상위 판정/인계 기준: `docs/history/laps/20260919_lap392_astra_f4_evidence_boundary.md`. G2 우선·G1/G4 후순위·G3 중단, DESIGN 및 통합 NO_GO 유지. F4(b)는 추가 안전 검증 방향 권고일 뿐 제품기준 변경/승인 아님.
- W1은 소비 완료; 기존 trace 재분석 반복 금지. lap391 표본 수치는 보존하되 “gap-proof/이 fixture에서 불가능”은 불변식 미입증으로 UNKNOWN. 새 실행 승인 대기라는 종전 해석도 인계에서 재검토한다.
- 이전 STATUS 129줄 전문/SHA는 `20260919_lap392_status_before_escalation.md`와 lap392 기록에 보존. 과거 주장/반려/미결 삭제 아님.
## 지금 막힌 것 (Blockers)
- **lap392 우선 정정:** 아래와 과거 검증란의 V2 “패배0/gap 내 흡수 불가”는 표본만으로 증명되지 않음. 원본cap1500 전역12000 불변량 주장도 미입증. 수치와 추론을 분리하며 F4 도달성 UNKNOWN·제품0/3 유지.
- **F4 신규(lap389, `ESCALATE_SOL` 판정대기) — "8인 각5000" 숫자가 원본 장부 폭과 충돌한다:** 전비장부 `+0x200C`는 16-bit(`0043EE9B add word ptr [ecx+0x200C], dx`)이고 생산gate가 **부호있게** 읽는다(`0043EDFC`/`0043EE03 movsx`, `cmp/jle`@`0x43EE0F`) ⇒ 도달범위 `[-32768,32767]`. 9/19 run **실측** 전역used 합은 첫sample **40,000**(=8×5000), `32767-40000=-7233`. 한 owner에 집중되면 word가 음수로 랩→gate가 항상참→전비제한 사실상 해제→1199슬롯 고갈까지 생산가능. 원본cap1500은 8×1500=12,000/여유+20,767이라 **원리적 도달불가**였다. **산술·전역합40,000 확정, 랩 재현은 UNKNOWN**(관측 최대 단일owner used 5,003). 판정요청: G2 합격기준을 (a)`used<=cap` 무위반으로 둘지 (b)`생산gate 무결성+장부 랩 없음`으로 둘지, 그리고 cap5000이 16-bit signed 장부와 양립하는지. **middle 권고는 (b).** 장부 폭 확장이 필요하면 아래 통합 blocker와 같은 성격의 작업이다.
- **현재 G2 구조통합 blocker:** 저비용 다수 구성의global1199/ordinaryowner242 확장에 필요한 Unit·보조 인덱스·bulk-relative alias·초기화/수명주기·저장/LAN의 일관 계약 미구현. 두 actual 진단은局所getter追加로 정상simulation에 도달하지 못함. 개별PC따라 패치 반복중단; 제품완료/전체불가능 선언없음. **lap381이 닫은 것은 layout 선행질문(C1 count폭·H1 matrix형태)뿐이며 이 통합 blocker는 그대로다.** **lap385 신규 실측(Astra 큐, 승인대기·작업은 계속함):** 핀된 save`0x440F02`(len`0xE397C`,src`0x892410`)/load`0x4412DC`가 정의하는 bulk blob `[0x892410,0x975D8C)`이 existence/age/catA/catB/active **5개 영역을 내부에 품는다**(unit_pool만 bulk 아래, 별도 roster). ⇒ 확장은 `0x892410`을 slot당1,880B 밀어올리는 **동시에** 고정길이 blob 내부를 slot당14B 불린다(N=4001→새 start`0xD97DE8`/필요 len`0xED2AA`); 둘 다 하드코딩 push 즉시값이라 **layout mapper만으로 저장호환 확장은 원리적으로 불가**하고 길이·주소 즉시값 fixup+저장포맷 변경이 필수다. lap379 Sol의 integration/broad-patcher/runtime NO-GO를 **뒤집지 않고 강화**한다. **새 불가능 증명 아님** — G2를 이 경로로 계속할지는 Astra 판정 사항. **lap388 종결:** 레이아웃 계산기 카드는 ACCEPT·계약5 CLOSED로 닫혔으나 이 통합 blocker는 **그대로다** — 오히려 "길이·주소 두 하드코딩 즉시값 fixup+저장포맷 변경 필수"를 수치로 굳혔다(`loop/ESCALATE_SOL` 판정 대기).
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
**lap392 Astra:** 이전 probe의 D1/D3 소스 검수로 표본→연속 사건 배제의 근거 공백 확인. 수치 재계산·원본 재해시·게임실행 SKIP. Fast는 FULL_TEST 요청(미통과); 아래는 역사 결과이며 gap-proof 해석은 위 정정 우선.
**2026-09-20 lap391 middle(Opus5/high) — lap390 W1 독립 재계산 ACCEPT(관측 단위 승인일 뿐 제품/런타임/마일스톤 승인 아님):** lap390 스크립트를 import하지 않고 핀/주장값을 probe에 손으로 전사한 뒤 `samples.jsonl`(SHA `76903a8d…f0e7180`, 146samples, tick10020→34185, cap 전sample 균일5000) 원문에서 재계산 — sample수146/M1음수0/M2 `(5003,owner1,tick33185,sample140)` 4-튜플/M3 0/M4 40,000→35,427/`used>cap` 위반7건 sample140~146/per-owner 범위 8행, **전부 일치**. 신규 probe **rc0 `failures=[]`**. **신규 증거:** V1 샘플러가 이미 `used=i16(0x200C)`=`"<h"`이므로 lap390의 signed16 재해석은 항등이나 랩은 직접 음수로 가시(부호확장 40000→-25536까지 실증, fail-open 닫음); V2 per-owner roster count 최소 `{112,136,145,144,144,112,133,138}` ⇒ 패배owner 0건이라 gap 안 흡수도 불가(M3보다 강함); V3 여유27,764(5.5배)지만 전역합 peak40,000>32,767 유지 ⇒ **F4 산술 전제 생존**; V4 166~167tick 표본이라 gap 내 치유된 일시 랩은 원리적 비가시(V2가 실질 차단). **N16 provenance 정정 발행**(위 회귀 (h)). `make check` **rc0 715 passed 148.29s**+Ruff/compileall/mypy10 Success+`CONTEXT_PASS`, **`SAFETY_PASS`**, 원본 `b56986e0…c9c08a8ac` 재해시 불변. 제품코드/바이너리/게임실행/커밋 **0** — 변경은 probe1개+문서. 외부보존 `…/g2_capacity/20260919_owner_transfer_cap/lap391_middle_ledger_wrap_review/probe_output.json`(`2616be2a…75d71749`), probe `3121b5e1…4f3df93af9`. 상세 `20260920_lap391_middle_g2_ledger_wrap_review_acceptance.md`.
**2026-09-19 lap389 middle(Opus5/high) — 9/19 actual run 독립 재검수 ACCEPT + transfer 사전거부 NO_GO(정적 판정일 뿐 제품/마일스톤 승인 아님):** 보고서 텍스트를 믿지 않고 `samples.jsonl`에서 재계산 — 146samples, 위반 **7건**(sample140~146/tick33185~34185/owner1 `5003>5000`) 보고서와 **완전일치**, 전역used 합 첫40,000→끝35,427(보고서에 없던 신규수치, F4 근거). 신규 read-only probe **rc0 `failures=[]`**: 원본SHA `b56986e0…c9c08a8ac` 재확인, `0x476ED0` 본문 `[0x476ED0,0x477019)` 329B(바이트SHA `e39a1824…13cf197e`) 단일ret·조건분기1개(대상 본문내)·꼬리 `mov eax,1`; E8 rel32 전수로 caller 5개 산출 후 **각 call 직후2명령에서 반환값 소비0**; `0x43EE30` admission은 `cmp ax,0x4B0/jl` **roster<1200 하나뿐**이고 `+0x2012` 참조0, `+0x200C` 가산은 무조건; 생산gate `0x43EDA0`이 유일하게 `+0x2012`를 비교(caller7, transfer 본문내 **0**) ⇒ transfer는 gate를 **의도적 우회**; `0x43EE30`/`0x43EEC0` 각각 비-transfer caller `0x48BCFE`/`0x443156` 공유. caller 분류: capture(`FUN_004770D0` state0xF 대상+부속2기), 시간형점령(`FUN_004777E0`), 승선합류(`FUN_00407930` case0xC), wrapper `0x40F890`→**일괄흡수 `FUN_00444EF0`**/charm `FUN_00470A00`(type0x51). `checks/safety.sh check` **`SAFETY_PASS`**. 제품코드/바이너리/게임실행/커밋 **0** — 변경은 probe1개+문서. 외부보존 `…/g2_capacity/20260919_owner_transfer_cap/lap389_middle_static_judgment/`(probe_output `012033bf…08c5cdf7`, probe `eb5b3be1…b5a59b45`). 상세 `20260919_lap389_middle_g2_owner_transfer_cap_judgment.md`.
**2026-09-18 lap388 middle(Opus5/high) — lap386 Part A+lap387 Part B 독립 재유도 검수 ACCEPT(계산기 단위 승인일 뿐; 제품/런타임/마일스톤 승인 아님):** 핀을 probe에 따로 전사하고 자체 `cumulative_below()`로 기대값을 재계산(모듈은 답 읽기에만 import). 신규 probe **rc0 `failures=[]`**, N 스윕9종(1200~123457). **신규 증거 — 핀을 바이트로 승격:** 원본 EXE 섹션표를 재파싱해 `0xE397C`·`0x892410` 즉시값이 save`0x440F02`(파일`0x40F02`)·load`0x4412DC`(`0x412DC`) ±`0x40` 창에 **4/4 실재** 실측(단 **명령어 디코딩 미수행** = fail-open 1건). **핵심 교차검증 G3:** 모듈이 상수로 갖지 않는 old BULK end `0x975D8C`가 일반 `map_va`로 `bulk_end`와 전 N 일치, `0x892410`도 배타적끝/포함적첫바이트 두 해석이 같은 값으로 수렴 ⇒ blob 모형이 자기정합. **G5:** PlayerStruct 이동률 **1892**(=1880+2+2+4+4, active_slot_list는 위)를 독립 재유도해 전 N 일치, BULK start1880·end1894와 구별됨; span `8*0x3ABC` 불변. **G7:** `mapped_offset`이 naive 아님을 수치 고정(N=4001 보정 **33,612**=12×2801, `0xC4360`→`0xCC6AC`). **G9 반증력:** 틀린 구현2종(4-sidecar 길이`0xEBCC8`, PS 1880율 `0xE5C148`) 재현해 probe가 잡음 확인. `.pelayout` 원본에서 **재생성해 SHA 재현**(`38a7148e…36cbc808`), mapping JSON 기계값 전부 probe 독립산출과 일치. `make check` **rc0 715 passed 117.53s**+Ruff/compileall/mypy10+`CONTEXT_PASS`, **`SAFETY_PASS`**, 원본`b56986e0…c9c08a8ac` 불변/frozen`e9d84513…9f8cc` 무변경. 검수대상 SHA가 lap387 기록과 동일(모듈`1469752c…f0c1bd`/테스트`5c220a73…f0bd70c70`). 제품코드 변경0·게임실행0·커밋0. 상세 `20260918_lap388_middle_g2_layout_part_ab_acceptance.md`.
**lap386~387 work(Sonnet5/high, 압축):** lap386이 Part A(`bulk_state_base`를 `regions[0].new_end`에서 유도, 3중 이름+미모형화 blob 경고 docstring, pytest3), lap387이 Part B(`BULK_OLD_LENGTH`/`PLAYER_STRUCT_BASE`/`STRIDE`/`COUNT` 핀 상수 + `bulk_length`/`bulk_end`(**`regions[1:]`=sidecar 5개** delta 합; 이전 STATUS의 "regions[1:5]" 표기는 드리프트였고 4개 해석이면 `0xEBCC8`로 핀 불일치 — lap388 N15 정정) + `mapped_offset()` + `player_struct_layout()`, pytest15, collect82) 산출. 각 회차 `make check` rc0(689/715 passed)+`SAFETY_PASS`, 원본/frozen 불변, uncommitted. lap388이 ACCEPT. 전문 `20260918_lap386_work_g2_layout_part_a_alias_exposure.md`/`20260918_lap387_work_g2_layout_part_b_bulk_playerstruct.md`.
**2026-09-18 lap385 middle(Opus5/high) — lap384 R1~R6 독립 검수 ACCEPT(layout 계산기 단위 승인일 뿐 제품/런타임/마일스톤 승인 아님):** 핀된 표를 probe에 따로 전사하고 **수리 전 알고리즘을 국소 재구현**해 각 결함을 먼저 재현한 뒤 판정. 신규 probe 2개 **둘 다 rc0 `failures=[]`**. R1: 수리전 `map_va(0x66B790+0x758*1199,100)`가 `unit_pool`이라며 `0x891CB8`을 냈고 실제 새 주인은 `gap_after_active_slot_list`로 **lap383 주장 재현**, 현행은 전부 `ValueError`. R2: 외래delta를 모듈없이 재계산해 N=4001 `5,265,880/5,277,084/5,299,492/5,305,094`+rsrc`5,308,416` 전부 `.delta` 필드와 일치, 확장시 delta0 **0개**. R3: 독립 이분탐색으로 첫 초과 **N=2,259,703** 재유도 일치, `IMAGE_BASE+2**32` 형태 소멸. R4: `.pelayout`을 원본에서 **재생성해 SHA 재현**(`38a7148e…36cbc808`)+독립 PE파싱으로 길이불변·`.rsrc` RVA이동 `5,308,416`·SizeOfImage 커버 확인, 메인레포 `.pelayout` 0건. R6: 36 probe 중 unmappable 정확히1개=`0x0066B78F`. **R5 범위 정직화:** pytest는 `validate_original_source`를 직접 부를 뿐 `prepare()`/CLI를 부르지 **않는다**; lap385가 `runtime_main` 진입점 **11개 전수 도달성**으로 빠진 고리를 메움 — Popen 도달 가능한 8개 전부에서 게이트가 **엄격히 선행**(prepare 0 vs 26, smoke 0 vs 12, g1_baseline 0 vs 45 등), 나머지3개는 Popen 미도달 ⇒ 우회 불가. 라이브 거부(`SHA-256 mismatch`)+Popen0회, **대조군** N=1200 artifact는 같은 게이트 통과(내용 기반 증거). `make check` **rc0 681 passed 128.54s**+Ruff/compileall/mypy10+`CONTEXT_PASS`, **`SAFETY_PASS`**, 원본 `b56986e0…c9c08a8ac` 불변, frozen `e9d84513…9f8cc` 무변경. 제품코드 변경0·게임실행0·커밋0. 상세 `20260918_lap385_middle_g2_layout_r1_r6_acceptance.md`.
**lap384 work(Sonnet5/high, 압축):** lap383 REJECT의 R1~R6 전부 scoped 수리(신규 pytest 5건, 48 passed), `make check` rc0 681 passed+`SAFETY_PASS`, R4 산출물 지정temp에 실물 생성(mapping JSON SHA `fb7f9e83…d11605b18`). §3-5는 의도적 미착수로 남겨 middle 판정 대기 → lap385가 확정. 전문 `20260918_lap384_work_g2_layout_r1_r6_repair.md`.
**lap382~383(REJECT/scoped 수리 사이클, 압축):** lap382 work가 신규 `base_preserving_storage_layout_v1.py`+테스트45건 산출(N=1200 항등, 확장 겹침없음/단조/32bit, `.rsrc` 재기술 등 PASS). lap383 middle 독립검수가 핵심기하는 확인하되 R1~R6 계약위반 6건 REJECT. 게이트 매회 `make check` rc0 678 passed+`SAFETY_PASS`, 원본 불변. 전문은 `20260918_lap382_work_g2_base_preserving_storage_layout_v1.md`/`20260918_lap383_middle_g2_layout_independent_review.md`, 이번 압축 전문은 `20260918_status_lap384_precompaction.md`(SHA `6f11faa0…4661759f`,135줄)에 보존.
**2026-09-18 lap381 middle(Opus5/high):** `make check` **rc0/633 passed 129.48s**+Ruff/compileall/mypy10파일/`CONTEXT_PASS`, `checks/safety.sh check` **`SAFETY_PASS`**, lap380 tail probe **rc0 `failures=[]`**(PE기하·3중alias `0x892410`·전영역BSS·basereloc부재 fresh 재유도), lap381 C1/H1 probe **rc0 `failures=[]`**. 원본 `b56986e0…c9c08a8ac` 불변, 원본/참고/공유 쓰기0·게임실행0·커밋0. 변경은 probe 2개뿐(`80dc357f…5095ab7c`, `0a66a29f…d4e1b0b4`). Fast일뿐 실제앱/24k/멀티 증거 아님.
**2026-09-15 product-first:** 원본·후보 실제 S1 load·PS35 메뉴 exact100%·PS3 이미지99.213%, 미니맵 camera·선택해제 count·드래그 count3 대칭 PASS; save000 8/8, cleanup/residue0, 후보 DxWrapper ini 원복·private ddraw module PASS. private G1 설정 draft SHA `f0ce9e64…6785` 산출(Windows native/출시 아님). targeted G1 62+profile6, G2 xref2; 통합 Fast442·Ruff/compileall/mypy/CONTEXT·safety2 PASS. G2 숫자패치만으로 전체8인 안정성 불가; 저장 save000/006 중 활성8인 fixture 없음, 원본 풀끝 `0x892410`은 live state 시작과 일치한다. G2 SHA-pinned 정적 xref inventory 후보 allocator18/spawn29/destruction13/save1/load1이나 경로 불완전/activation NO-GO. G4 원본 A* `[1]` PE 바이트 확인, 반복 비교 fixture 없음/제품 변경 NO-GO.
**2026-09-16 G4 path preflight/AI(압축, 전문은 lap382 compaction+`20260916_g4_waypoint_reinforcement_movement.md`/`20260916_g4_waypoint_probe_ack_failure.md`):** pinned EXE/PE entry·UnitStruct reader PASS, original 2-run 결정론 BLOCKED. cooldown 후보 둘다 NO-GO; 원본 mobile 다수기 300+tick 정지(`IDLE_COMMAND_ISSUANCE_GAP_OBSERVED`), 직접 command 기록 불충분. AI2기 waypoint reinforcement 수리 후 이동21/22좌표 국소 PASS; UI tail minimap FAIL 보존, 제품 AI/길찾기 완료 아님, 게임 실행·바이너리 변경0.
**lap356~370 검증 계보(REJECT/RELEASE 반복, 제품·게임 0회):** 각 lap 기록 및
`20260912_status_lap356_compaction.md`/`20260912_status_lap366_precompaction.md`/
`20260918_status_lap382_compaction.md`(이번 압축, 150줄 원문 SHA `60a0d91d…d74659d5`)에 전문 보존.
## 바퀴 기록
lap392 Astra: 근거 공백으로 BLOCKED·승격 보존. 상위 방향/검증 조건만 문서화, 코드/바이너리/게임실행/커밋0. 상세 `20260919_lap392_astra_f4_evidence_boundary.md`.
lap391 middle: lap390 W1 **독립 재계산 ACCEPT**(probe rc0, 8지표 전부 일치) + 신규 V1~V4(패배owner0 gap-proof로 M3 보강, F4 산술 전제 생존 확인) + **N16 provenance 정정**. W1 **CLOSED**, 재수리 체인 없음. `ESCALATE_SOL` §5로 갱신(닫지 않음) — F4 합격기준 (a)/(b)와 "랩 트리거 fixture를 만들 것인가"(신규, 새 게임실행이라 승인 필요)가 승격 판정 대기. 제품코드/게임실행/커밋 0 — implementation-unchanged-streak **2**, 그러나 전제인 F4 기준이 판정 대기라 middle 단독으로 다음 제품 카드 개설 불가 ⇒ **STOP**. 상세 `20260920_lap391_middle_g2_ledger_wrap_review_acceptance.md`.
lap390 work(Sonnet5/high): handoff 카드W1 소비 — 9/19 samples.jsonl 재분석(재실행0)으로 F4 랩 도달성 **NOT_FEASIBLE**(이 fixture 한정) 산출. `make check` rc0 715 passed+`SAFETY_PASS`, 원본 불변, 제품코드/바이너리/게임실행/커밋 **0**(관측전용이라 streak 리셋 아님). lap391이 ACCEPT. 상세 `20260920_lap390_work_g2_ledger_wrap_reachability.md`.
lap389 middle: 9/19 actual run 독립 재검수 **ACCEPT**(위반7건/전역합40,000 재계산), transfer 사전거부 카드 **NO_GO로 종결**(반환값 미소비5/5·공유roster·semantics 파괴 3근거). **신규 F4**(16-bit signed 장부 vs 8×5000=40,000) 발견 → `loop/ESCALATE_SOL` 발행, 합격기준 재정의는 Astra/사용자 판정. 승인불필요 관측전용 work 카드W1 handoff 발행. 제품코드/게임실행/커밋 0 — implementation-unchanged-streak **2**(다음 회차는 측정 가능한 변화 또는 구체 blocker). 상세 `20260919_lap389_middle_g2_owner_transfer_cap_judgment.md`.
**lap380~388 G2 레이아웃 카드 계보(압축, lap391. 각 lap 기록 전문은 `docs/history/laps/20260918_lap38{0,1,2,3,4,5,6,7,8}_*.md`에 보존, 압축 전 STATUS 원문은 `20260920_status_lap391_precompaction.md` SHA `d168c947…eed7abb6`/135줄):** lap380 계획→lap381 C1 CLOSED·H1 shape CONFIRMED→lap382 work 산출(streak0 리셋)→lap383 middle REJECT(R1~R6)→lap384 work scoped 수리(streak0)→lap385 middle ACCEPT·§3-5를 PartA/PartB로 분할→lap386~387 work 구현(pytest3+15, streak0)→lap388 middle ACCEPT·**계약5 및 계산기단위 전체 CLOSED로 레이아웃 카드 종결**(재수리 체인 없음). 전 회차 `make check` rc0(633→715 passed)+`SAFETY_PASS`, 원본/frozen 불변, 제품코드 2파일 외 게임실행/커밋 **0**.
`native_route_judgment` **NO_GO는 미변경 — 뒤집지 않고 강화**. 종결 리포트 `docs/reports/20260918_G2_LAYOUT_CARD_CLOSURE.md`. handoff `…LAP381/LAP383/LAP385.md` 전부 **소비됨**(원문은 관례대로 `docs/work/active/`에 보존). 상위 통합 blocker는 위 「지금 막힌 것」에 그대로 살아 있다(이 종결이 해소하지 않음).
lap377 Astra 방향 → lap378 middle ACCEPT → lap379 provenance BLOCKED 뒤 사용자 product-first 지시로 반복 중단. fresh 원본 S1 실제 실행 PASS; 다음은 1600×1200 후보 S1/Stage B.
lap356~376 상세(import 해소·§3 RELEASE, REJECT/수리 반복, 게임/커밋 0회)는 각 lap 기록과
`20260912_status_lap361_entry.md`(SHA/124줄)에 보존.
