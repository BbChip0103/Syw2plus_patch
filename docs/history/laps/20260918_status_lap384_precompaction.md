# STATUS — 매 바퀴 갱신하는 기억
## 지금 상태
활성 G1/G2/G4 제품 미완료(0/3); G3 최대16인은 2026-09-17 사용자 지시로 중단. **G2 최우선·9/18 Claude Code 역할로 재개 승인**; G1/G4 후순위 유지. M1/G1 요구 유지: 원본 구도·입력과 차후 고해상도 그림의 디테일 보존을 함께 만족하는1600×1200 화면. 제품 기준은 DESIGN, 사람 승인
원문은 feedback/APPROVALS·INBOX를 따르며 2026-09-12 01:03 bounded repair→fresh validation 허가는 제품/출시 승인이
아니다. DxWrapper 2× 화면·S1 입력쌍은 배치 프리뷰 근거만; 추가 디테일 보존 경로와 WM_CLOSE 결함은 남았다.
과거 G1/lap275~379 승인·반려·미결 계보는 전체 원문 `20260917_234449_status_pre_cutoff_compaction.md`(SHA 9400241176cce4bbe0047b358a887f09e269d9824a253654d6ff2718d352ddef,141줄)에 보존했으며 fresh 제품 PASS/출시 승인으로 승격하지 않는다.
| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | native PS3 PASS·원본구도 FAIL·제품 미완료 | stock UI 클릭 PS9→PS7→PS5→PS3 tick3, native `1600×1200×8bpp/pitch1600`/viewport 전역 PASS; 월드 시야 확대·스프라이트/HUD 원본 픽셀 크기라 G1 배치 FAIL, 고해상도 SPR·생산·종료 미검증; 이번최종acquisition은초기화guard8000001A에BLOCKED |
| G2 | 8-slot고전비 초기USED/cap5000·실제24k baseline 관측/제품 미완료 | 1160HPpositive 초기군대→원본자연simulation Δ24124ticks/725sec 오류0/cleanup0잔류;25dead→gap→slotreuse 관측·owner4resrelease·원본풀peak1176. owner1USED5003 기존foreignID ownertransfer 동반/원인UNKNOWN. 임의저전비대군/global1199·ordinaryowner242 확장/경제·확장save/LAN 미완료 |
| G3 | 사용자 지시로 중단·활성 범위 제외 | 16 PlayerStruct가 bulk save112,036B 초과, self/opponent mask8bit라 owner8~15 표현 불가; 활성9~16/LAN 미완료 |
| G4 | 원본 issuer 국소 이동 PASS·제품 미완료 | 직접 command 기록은 정지; mainthread 원본 issuer는 같은 source 이동68좌표. current waypoint reinforcement 수리 후 AI2기 이동21/22좌표·목표gap2/1 PASS; one-shot2회 같은 이동 결과, 발행tick다름·지속 정책/품질 미검증; 이번정상AI512+load11 관측만PASS/정확postload미확정 |
## 다음 한 가지
**다음 새 middle(Opus5/high)가 lap384 work 산출물(R1~R6 수리)을 독립 검수한다.**
- lap384 work(Sonnet5/high)가 `G2_STORAGE_LAYOUT_REPAIR_HANDOFF_LAP383.md`의 R1~R6을 전부 scoped 수리:
  R1 `layout(n<1200)` 거부, R2 `ForeignLayout.delta=new_start-old_start` 전면 수정, R3 VA가드
  `rsrc.new_end>=2**32`, R4 지정temp `.pelayout`+mapping JSON 실물 산출(SHA 기록됨), R5 launcher
  거부 테스트를 `runtime_env.validate_original_source` 실제 호출+zeroPopen 관측으로 교체, R6 blanket
  unmappable skip을 `0x0066B78F` 1개로 고정. 각 항목 신규 pytest 회귀 포함, `make check` 681 passed +
  `SAFETY_PASS`, 원본/frozen `offline_storage_v1` 불변. 상세 `20260918_lap384_work_g2_layout_r1_r6_repair.md`.
- 다음 middle이 확인할 것: (a) R1~R6 실측 독립 재유도, (b) 계획§3-5(`0x892410` 3중alias·PlayerStruct
  span 미노출)를 이 카드에 넣을지 별도 카드로 뺄지 **계획 문서에 명시**(work tier가 임의로 정하지 않음).
- 보호/원본/frozen pins갱신금지, 부산물은 지정temp/Syw2plus_patch 아래. 커밋·서비스·deps·게임실행·codefixup·주소추론generator없음. G2 priority8×5000/lifecycle/economy/save/LAN/24k144k는미완료. 매10분실제KST보고.

## 지금 막힌 것 (Blockers)
- **현재 G2 구조통합 blocker:** 저비용 다수 구성의global1199/ordinaryowner242 확장에 필요한 Unit·보조 인덱스·bulk-relative alias·초기화/수명주기·저장/LAN의 일관 계약 미구현. 두 actual 진단은局所getter追加로 정상simulation에 도달하지 못함. 개별PC따라 패치 반복중단; 제품완료/전체불가능 선언없음. **lap381이 닫은 것은 layout 선행질문(C1 count폭·H1 matrix형태)뿐이며 이 통합 blocker는 그대로다.**
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
  `player_offsets.md`의 `0x00B92CC0` 행은 **WORD·다음 상태 요청**(수치 영향 0, 별도 카드).
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
**2026-09-18 lap384 work(Sonnet5/high) — lap383 REJECT의 R1~R6 scoped 수리, 독립 검수 대기:**
6개 항목 전부 수리+회귀(신규 pytest 5건, 48 passed). `make check` **rc0 681 passed 117.37s**+
Ruff/compileall/mypy10+`CONTEXT_PASS`, `checks/safety.sh check` **`SAFETY_PASS`**. 원본
`b56986e0…c9c08a8ac` 불변, frozen `offline_storage_v1.py` 무수정(`e9d84513…9f8cc`). R4 산출물
지정temp `g2_capacity/20260918_lap383_layout_artifact/g2_layout_n4001.pelayout`
SHA `38a7148e…36cbc808`+mapping JSON SHA `fb7f9e83…d11605b18`. 독립 review probe 재실행: R1~R3
관련 FAIL 항목 전부 PASS로 반전, `module_sha_matches_lap382_record`는 모듈이 바뀌었으므로 예상된
FAIL, R1 옛 진단 스크립트는 새 `ValueError`로 의도대로 중단(회귀 아님, 실제 회귀는 pytest 신규
3건). 계획§3-5(0x892410 alias/PlayerStruct span)는 명시적으로 미착수(다음 middle 판정 대기).
게임실행·커밋·공유쓰기 0. 상세 `20260918_lap384_work_g2_layout_r1_r6_repair.md`.
**2026-09-18 lap383 middle(Opus5/high) — lap382 독립 검수 = REJECT(scoped 수리1회):** 독립 재유도로 **확인된 것**: `build_layout_artifact(원본,1200)` 바이트 완전동일; `.rsrc` 리소스 디렉터리 **직접 트리 walk**로 leaf 9개 재유도 → 모듈 `PAYLOAD_ENTRY_OFFSETS`와 정확일치(모듈상수 미사용); N=4001/9601/9904 artifact 변경바이트가 독립유도 허용범위의 부분집합(차집합0); 확장후 `.data` VirtualSize가 tail을 여전히 덮고 `.rsrc`와 비겹침·SizeOfImage가 rsrc끝 덮음(3N PASS, stock slack `0x5C8` 실측); N1200 항등 probe36개 중 파손0·unmappable은 `0x0066B78F` **1개뿐**이라 "±1 항등 vs unmappable 충돌"은 **충돌 아님**. **깨진 것**: R1 `layout(n<1200)` 미거부로 폐기slot이 외래블록 내부로 조용히 사상, R2 foreign delta=0(계약§3-2·lap381 정정 위반), R3 VA가드 `IMAGE_BASE+2**32`, R4 `.pelayout`/mapping 실물0, R5 launcher테스트 호출0건, R6 blanket skip. 게이트 재실측: `make check` **rc0 678 passed 124.02s**+ruff/compileall/mypy10/`CONTEXT_PASS`, `SAFETY_PASS`, lap380·lap381 probe 각 **rc0 `failures=[]`**, targeted45/dir90. 원본 `b56986e0…c9c08a8ac` 불변, `patches/**` SHA3종 불변, 게임실행·커밋·공유쓰기 0. 상세 `20260918_lap383_middle_g2_layout_independent_review.md`.
**2026-09-18 lap382 work(Sonnet5/high):** 신규 `base_preserving_storage_layout_v1.py`(순수 레이아웃 계산기+PE-layout artifact 빌더)와 테스트 45건 전부PASS: N=1200 layout이 §1 표와 바이트단위 일치+`build_layout_artifact(원본,1200)==원본`(강한 항등), N∈{4001,9601,9904} 확장에서 6영역/외래블록 겹침없음·순서·단조 보존·32bit overflow없음·`.rsrc` 정렬불변식, `.rsrc` 이동+9개 payload `OffsetToData` RVA+resource directory+SizeOfImage 일관 재기술(그 외 바이트 불변, 독립 diff로 확인), SHA불일치 거부, `write_layout_artifact`의 `.pelayout`/경로/원본파일명shadow 가드. `make check` **rc0 678 passed**(기존633+신규45)+Ruff/compileall/mypy10파일/`CONTEXT_PASS`, `checks/safety.sh check` **`SAFETY_PASS`**. 원본 `b56986e0…c9c08a8ac` 불변(빌드 전/후 동일), frozen `offline_storage_v1.py` 무수정, code operand fixup·후보EXE 생성·게임실행·커밋 0. 독립 검수 대기(§4).
**2026-09-18 lap381 middle(Opus5/high):** `make check` **rc0/633 passed 129.48s**+Ruff/compileall/mypy10파일/`CONTEXT_PASS`, `checks/safety.sh check` **`SAFETY_PASS`**, lap380 tail probe **rc0 `failures=[]`**(PE기하·3중alias `0x892410`·전영역BSS·basereloc부재 fresh 재유도), lap381 C1/H1 probe **rc0 `failures=[]`**. 원본 `b56986e0…c9c08a8ac` 불변, 원본/참고/공유 쓰기0·게임실행0·커밋0. 변경은 probe 2개뿐(`80dc357f…5095ab7c`, `0a66a29f…d4e1b0b4`). Fast일뿐 실제앱/24k/멀티 증거 아님.
**2026-09-15 product-first:** 원본·후보 실제 S1 load·PS35 메뉴 exact100%·PS3 이미지99.213%, 미니맵 camera·선택해제 count·드래그 count3 대칭 PASS; save000 8/8, cleanup/residue0, 후보 DxWrapper ini 원복·private ddraw module PASS. private G1 설정 draft SHA `f0ce9e64…6785` 산출(Windows native/출시 아님). targeted G1 62+profile6, G2 xref2; 통합 Fast442·Ruff/compileall/mypy/CONTEXT·safety2 PASS. G2 숫자패치만으로 전체8인 안정성 불가; 저장 save000/006 중 활성8인 fixture 없음, 원본 풀끝 `0x892410`은 live state 시작과 일치한다. G2 SHA-pinned 정적 xref inventory 후보 allocator18/spawn29/destruction13/save1/load1이나 경로 불완전/activation NO-GO. G4 원본 A* `[1]` PE 바이트 확인, 반복 비교 fixture 없음/제품 변경 NO-GO.
**2026-09-16 G4 path preflight/AI(압축, 전문은 lap382 compaction+`20260916_g4_waypoint_reinforcement_movement.md`/`20260916_g4_waypoint_probe_ack_failure.md`):** pinned EXE/PE entry·UnitStruct reader PASS, original 2-run 결정론 BLOCKED. cooldown 후보 둘다 NO-GO; 원본 mobile 다수기 300+tick 정지(`IDLE_COMMAND_ISSUANCE_GAP_OBSERVED`), 직접 command 기록 불충분. AI2기 waypoint reinforcement 수리 후 이동21/22좌표 국소 PASS; UI tail minimap FAIL 보존, 제품 AI/길찾기 완료 아님, 게임 실행·바이너리 변경0.
**lap356~370 검증 계보(REJECT/RELEASE 반복, 제품·게임 0회):** 각 lap 기록 및
`20260912_status_lap356_compaction.md`/`20260912_status_lap366_precompaction.md`/
`20260918_status_lap382_compaction.md`(이번 압축, 150줄 원문 SHA `60a0d91d…d74659d5`)에 전문 보존.
## 바퀴 기록
lap384 work: lap383 REJECT의 R1~R6 전부 scoped 수리, implementation-unchanged-streak **0으로 리셋**
(신규 pytest 5건, 제품코드 변경 2파일). 독립 middle 검수 대기. 상세 `20260918_lap384_work_g2_layout_r1_r6_repair.md`.
lap383 middle: lap382 산출물 **독립 검수 REJECT(scoped 수리1회)**. 독립 probe rc1 `failures=6`(의도된 판정, 필수게이트 밖). 제품코드/게임실행/커밋 0 — implementation-unchanged-streak **1**. 신규 handoff `G2_STORAGE_LAYOUT_REPAIR_HANDOFF_LAP383.md`, lap381 handoff는 소비됨. 상세 `20260918_lap383_middle_g2_layout_independent_review.md`.
lap382 work: streak 경고에 대응해 신규 2파일(`base_preserving_storage_layout_v1.py`+테스트)로 제품코드 산출, implementation-unchanged-streak **0으로 리셋**. C1/H1 재조사 없이 lap381 확정 사실만 사용. 상세 `20260918_lap382_work_g2_base_preserving_storage_layout_v1.md`.
lap381 middle: lap380 실행권한 blocker **해소**(make check rc0/633·`SAFETY_PASS`·tail probe rc0 실측). C1 **CLOSED**(count=WORD·겹침없음), H1 **CONFIRMED shape**(8×200 WORD matrix, 의미UNKNOWN), 계획 정정2건, Sonnet handoff 발행, `ESCALATE_SOL` 증거후 소비(원문은 기록 부록A). 제품코드/게임실행/커밋 0. 상세 `20260918_lap381_middle_g2_c1_h1_closed.md`.
lap380 middle: Opus 계획 산출·C1/H1 신규 기록, 게이트3종 실행불가로 `ESCALATE_SOL`; 제품코드/실행 0. 상세 `20260918_lap380_middle_g2_base_preserving_storage_plan.md`.
lap377 Astra 방향 → lap378 middle ACCEPT → lap379 provenance BLOCKED 뒤 사용자 product-first 지시로 반복 중단. fresh 원본 S1 실제 실행 PASS; 다음은 1600×1200 후보 S1/Stage B.
lap356~376 상세(import 해소·§3 RELEASE, REJECT/수리 반복, 게임/커밋 0회)는 각 lap 기록과
`20260912_status_lap361_entry.md`(SHA/124줄)에 보존.
