# STATUS — 매 바퀴 갱신하는 기억
## 지금 상태
활성 G1/G2/G4 제품 미완료(0/3); G3 최대16인은 2026-09-17 사용자 지시로 중단. **G2 최우선 루프 재개(9/17 15:20KST)**; G1/G4 후순위 유지. M1/G1 요구 유지: 원본 구도·입력과 차후 고해상도 그림의 디테일 보존을 함께 만족하는1600×1200 화면. 제품 기준은 DESIGN, 사람 승인
원문은 feedback/APPROVALS·INBOX를 따르며 2026-09-12 01:03 bounded repair→fresh validation 허가는 제품/출시 승인이
아니다. DxWrapper 2× 화면·S1 입력쌍은 배치 프리뷰 근거만; 추가 디테일 보존 경로와 WM_CLOSE 결함은 남았다.
lap275 F3-R2-R1 선언 범위 승인, lap270 R30 PASS와 R17 계약 종결 FAIL은 함께 유효하며 M11 생존을 지우지 않는다.
G1-S1 계약 계보(`…/G1_S1_MIDDLE_ACCEPTANCE_LAP277.md` §4.1~§4.7)는 **S1 fixture 정적 타당성**일 뿐 두 run 동일성·제품
증거·Stage B 허가·마일스톤 종료가 아니다. runtime/load 계보(`…/G1_RUNTIME_CONTRACT_MIDDLE_LAP284.md` §11~§14)는
lap283→lap325에 보존된다. lap320 F1 종결 → lap322~325 §14 심사/반환/조건부 → lap326 R1 봉투 ACCEPT →
lap327 구현 → lap328 REJECT → lap329 수리 → lap330 제한 1 run 발효 → lap331 1회 실행 → lap332 ACCEPT로 R1
연구 레인 종결 → lap333 후보 선택 → lap334 봉투 ACCEPT → lap335 §11 구현 → lap336·lap337이 그 구현을
ACCEPT-WITH-REQUIRED-REPAIR로 판정하고 R-a·R-b 범위 확정 → lap338 Astra 보존 정책 초안 → lap339 middle 봉투
ACCEPT → lap340 work 수리 → **lap344 middle 전체 fresh 검수 ACCEPT** → lap345 후보 R1 관측 → lap346·347 probe 결함 →
**lap348 fresh 독립 검수 ACCEPT로 후보 R1 연구 레인 종결** → lap349~355 S1 load 근거 수립·reader 수리 → **lap356
middle이 lap354 F1~F4 수리를 ACCEPT** → lap357 adapter 구현 → lap358 SHA STOP → lap359 erratum → **lap360
fresh middle이 event-boundary adapter 구현 범위를 ACCEPT** → lap362 middle이 원본 pre slot1의 정적 구성 가능성과
work 봉투 초안 수립 → lap363 RELEASE·work 구현 → **lap365 REJECT → lap366 RELEASE → lap367~373 수리/검수 반복 → lap374~379 provenance 반복 중단 → 2026-09-15 제품우선 원본·1600×1200 후보 S1 PASS, 실제 PS3 이미지 비교.** 제품 입력/WM_CLOSE·장기 안정성은 UNKNOWN이다.
| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | native PS3 PASS·원본구도 FAIL·제품 미완료 | stock UI 클릭 PS9→PS7→PS5→PS3 tick3, native `1600×1200×8bpp/pitch1600`/viewport 전역 PASS; 월드 시야 확대·스프라이트/HUD 원본 픽셀 크기라 G1 배치 FAIL, 고해상도 SPR·생산·종료 미검증; 이번최종acquisition은초기화guard8000001A에BLOCKED |
| G2 | 8-slot고전비 초기USED/cap5000·실제24k baseline 관측/제품 미완료 | 1160HPpositive 초기군대→원본자연simulation Δ24124ticks/725sec 오류0/cleanup0잔류;25dead→gap→slotreuse 관측·owner4resrelease·원본풀peak1176. owner1USED5003 기존foreignID ownertransfer 동반/원인UNKNOWN. 임의저전비대군/global1199·ordinaryowner242 확장/경제·확장save/LAN 미완료 |
| G3 | 사용자 지시로 중단·활성 범위 제외 | 16 PlayerStruct가 bulk save112,036B 초과, self/opponent mask8bit라 owner8~15 표현 불가; 활성9~16/LAN 미완료 |
| G4 | 원본 issuer 국소 이동 PASS·제품 미완료 | 직접 command 기록은 정지; mainthread 원본 issuer는 같은 source 이동68좌표. current waypoint reinforcement 수리 후 AI2기 이동21/22좌표·목표gap2/1 PASS; one-shot2회 같은 이동 결과, 발행tick다름·지속 정책/품질 미검증; 이번정상AI512+load11 관측만PASS/정확postload미확정 |
## 다음 한 가지
**G2: 현재 안전분기 종료·전체목표 미완료. CLI STOP 확인, 00KST 종료시각 대기.**
- 실제 원본 1,200슬롯의 보조 고전비 구성: 초기 8명 각각 USED/cap5000, 총1160기 → 자연 시뮬레이션 Δ24124틱/725초/146샘플. 오류0·게임 프로세스 정리0잔류. 사망 표본→부재→같은 슬롯 새ID 25건, owner4 TYPE7 새ID 11건/예약해제 5회; 최대점유1176(동시1199·할당거절 미검증). 독립 분석0e8d를 Root가 11개 절 재현했다.
- 모든146×8 진영의 점유 개체 전비합=USED(1168회 일치); 생존개체만 계산한50회 차이는 사망 후 제거대기 개체 비용이다. owner1 USED5003>cap5000 7샘플은 동일ID394322의 owner3→1 이전 동반(새 전역ID 생성 아님). 호출 원인은 UNKNOWN; 독립 감사7f12, 강제 보정/제품안정성 주장 없음.
- 정상생산 COUNT243 실험 동결4a14/testb62는 절대23:40 종료시각·보수적 시간예측·명령owner/상한/pending 선행조건·생산행동 회귀 부족으로 Astra/medium STOP, Sol 동일 동결본 REJECT. 부모 연결은 정상이며 '기존cap250 생성게이트 충돌' 가설은 기각했다. 게임/prefix 준비0, 게임 불가능/OOM 증거 아님. 실패 코드는 외부 보존, 추가 수리/실행/예산리셋 없음.
- Luna가 active source6efd/test722로 정확 원복(영수증1a4f/target12·Ruff·mypy·compile PASS). Root 전체633 Fast(149.68초)+Ruff/compile/mypy10/context/shell/추가mypy2·전후SHA PASS, PTY63605 rc0. 보호8pins PASS/ownedprefix 잔류0, 최종영수증7ed9. 원본·공유DLL·native C·driver 불변, owner1200 후보6074는 미실행 오프라인 산출물이다.
- **전체 G2 미완료:** 임의 저전비 구성·global1199 확장·저장/LAN·메모리/성능144k 미검증. 실제 고전비 baseline을 제품완료로 승격하지 않는다. 사용자 상한00 KST, 현재결과를22:24에 정리보고. 기존 증거대조는 끝났으며 자정까지 시간을 채우는 재실험 없이 보고서20260917_g2_cutoff_result_report.md에 성과/가능성을 기록했다. 활성 OMX 실행모드없음·종료카드 추가실행/수리 없음; 아래 목표연속 요청에 따른 새로운 읽기전용 카드만 수행. G1/G4 후순위, G3 중단, 목표는 미완료 유지.
- 22:26 읽기전용3카드의 selected facts는 Sol/high 독립 RAW 검수1057로 조건부 채택: bulk16명령/3함수/3호출 및 Root9구간401명령 일치. matrix89A388, load441441 bound1200, exists/age init alias 및serialized8player 확인. 산출물의 generic Bcount/Player-relative roster/stream cdecl(실제RET4) 등 잘못된 annotation은 불채택, 전체참조 폐쇄·구현GO 없음. 상세20260917_g2_storage_lifecycle_contract_review.md. 보호 소스/DLL/C 핀 불변.
- 마지막 zero-cost TYPE94 질문 종료(22:48 Sol/high 검수d950). 기존cost0@9CA290/producer49→94행은 확인했으나 flags11808 bit8의positive indexed counter 거절이 존재하며 정상HQ 생산완료→반복동시생존은 미폐쇄. '반복 경로가 닫혔다/uniqueness 제한없음' author주장은 불채택. 다른TYPE·추가reader·새코드·게임·STOP 재개 없음, 4001/9601/9904 용량 모두 미승인. Astra의 이후 탐색마무리 지침에 따라 오늘 안전분기 종료·성과/속도/가능성 보고. **G2 완성품 없음, 원천불가능 판정도 없음.**
- 22:49~22:51 종료검증: 보호8pins 일치/known ownedWinePID3804916 소멸/새runtime0. priorfinally ownedprefix remaining[]와 readable /proc exactprefix0 확인; unreadable environments 일부 동일UID 서비스3·zombie3는 별도 한계 기록, systemwide모든프로세스 귀속단정/kill 없음. 영수증989f4c32…a0de. 새 변경은 문서/외부읽기전용 산출물뿐, source6efd/test722 및 마지막fresh633Fast 유지. active child6 모두completed·배포/커밋 없음. 사용자상한00KST 이후 자동실행 금지, 목표 미완료를 완료로표시하지 않는다.
- 실제2026-09-17T22:52:32.703350+09:00 runner확인: systemdunit미설치/CLI process없음, LOOP_ENABLE_AGENT=1이지만loop/STOP생성. stop_preflight가agent/lock/counter전에rc0종료하고runner/config/counter 전후SHA일치. 별도Nativegoal은아직active/미완료이며CLI STOP이이를중지한다고주장하지않는다. 종료시각대기만위해ownedtimerPID124104/session43513 READY확인(00KST자연종료), 새G2작업아님. 이후추가실험없음, 다음실제시각10분보고.


## 지금 막힌 것 (Blockers)
- **현재 G2 구조통합 blocker:** 저비용 다수 구성의global1199/ordinaryowner242 확장에 필요한 Unit·보조 인덱스·bulk-relative alias·초기화/수명주기·저장/LAN의 일관 계약 미구현. 두 actual 진단은局所getter追加로 정상simulation에 도달하지 못함. 개별PC따라 패치 반복중단; 제품완료/전체불가능 선언없음.
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
  부록 A, **lap325=lap326 부록 A(소비)**. lap300~325 STATUS 원문=각 압축본.
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
**2026-09-15 product-first:** 원본·후보 실제 S1 load·PS35 메뉴 exact100%·PS3 이미지99.213%, 미니맵 camera·선택해제 count·드래그 count3 대칭 PASS; save000 8/8, cleanup/residue0, 후보 DxWrapper ini 원복·private ddraw module PASS. private G1 설정 draft SHA `f0ce9e64…6785` 산출(Windows native/출시 아님). targeted G1 62+profile6, G2 xref2; 통합 Fast442·Ruff/compileall/mypy/CONTEXT·safety2 PASS. G2 숫자패치만으로 전체8인 안정성 불가; 저장 save000/006 중 활성8인 fixture 없음, 원본 풀끝 `0x892410`은 live state 시작과 일치한다. G2 SHA-pinned 정적 xref inventory 후보 allocator18/spawn29/destruction13/save1/load1이나 경로 불완전/activation NO-GO. G4 원본 A* `[1]` PE 바이트 확인, 반복 비교 fixture 없음/제품 변경 NO-GO.
**2026-09-16 G4 path preflight:** pinned EXE/Ghidra/PE entry·UnitStruct x/y reader·button3 PASS; deterministic scene, collision oracle, integrated move trace, original 2-run equality BLOCKED. JSON `c655ebf0…890a3`; targeted2/Ruff/mypy PASS. 게임 실행·바이너리 변경0.
**2026-09-16 G4 AI:** 건설/채집 cooldown 후보는 matchup 비대칭으로 둘 다 NO-GO. 원본 seed1 240초 mobile 추적은 owner0 26기 중 9기, owner1 23기 중 1기가 300+tick 완전 정지하며 전부 command1만 유지(`ef6193f4…3aba`) → `IDLE_COMMAND_ISSUANCE_GAP_OBSERVED`. 4기 target+command 직접 기록은 전부 좌표 불변(`02ac73db…0163`)이라 `DIRECT_COMMAND_FIELDS_INSUFFICIENT`. 원본 issuer `0x415480` 호출은 좌표69개 이동을 만들었고, mainthread slot 재현에서도 같은 source328848가 좌표68개 이동(`fdb3d294…c717`) → 국소 `ORIGINAL_ORDER_PATH_MOVEMENT_PASS`; wall-clock 두 run endpoint는 달라 결정론 증거 아님. 원본 AI current waypoint가 seed1 154/160초에 populated됨(`096f3f18…4af9`). 전역 적 조회 없이 AI/nonmember 한 기를 한 waypoint로 이동시키는 private reinforcement 첫 실행은 pending2건 접수했으나 ack JSON escape/tick 주소/partial trace 유실로 `BLOCKED_EVIDENCE`(`20260916_g4_waypoint_probe_ack_failure.md`). 3건 수리 후 새 실행은 ack 정상·718samples·AI2기 command3 이동21/22좌표, waypoint gap2/1로 국소 PASS(`20260916_g4_waypoint_reinforcement_movement.md`). UI tail minimap FAIL 보존, 최종 targeted171·Fast504/Ruff/compileall/mypy/CONTEXT/safety PASS, 제품 AI/길찾기 완료 아님.
**lap370 middle:** 세 SHA 일치·targeted **44 passed**지만 cleanup `UNKNOWN/CLEANUP_FAILURE` CLI **rc0** 재현 및 여섯 cap의 안/밖
회귀·실제 diff 부재로 **REJECT/STOP**; lap354/Fast/safety SKIP, 구현·게임 0회. **lap369 work:** 44/Fast422/safety PASS는 과거 기계 결과로 보존.
**lap368 middle:** fake clock 151s returned/artifact PASS·stage 경계 누락으로 **REJECT/STOP**. **lap367 work:** 36/Fast414/safety PASS는 과거 결과.
**lap366 middle:** 세 현행 SHA 일치; lap365 F1~F3 CONFIRM, timing/cleanup 충돌 해소·work repair RELEASE. targeted 24;
lap354 exact-once `failures=[]`; Fast 402·Ruff/compileall/mypy/CONTEXT, safety 2종 PASS; 수정·실행 0회. 제품/S1/Stage B UNKNOWN.
**lap365 middle:** lap363 세 SHA 일치; cleanup fail-closed·post/artifact deadline·§3.4 회귀 누락으로 **REJECT/STOP**.
**lap363 middle:** repo-root provenance=`tools/runtime_env.py`; lap354 exact-once rc0/`failures=[]`; doctor, targeted 21, Fast 399, Ruff/compileall/mypy/CONTEXT_PASS, safety PASS; 실행 0회, §3 RELEASE.
**lap360 middle:** 세 현행 SHA 일치, adapter 순서/fail-closed 재유도 ACCEPT; targeted 21, lap354 probe rc0/`failures=[]`,
Fast 399·Ruff/compileall/mypy/CONTEXT_PASS, safety PASS, binary contract 13 PASS, 원본 verified. 실제 실행 0회.
**lap357 work:** event-boundary adapter와 trigger/order/timeout/read-error 회귀를 추가했다. SHA는
`runtime_env.py=ba0a7beb…272b7372`, `s1_load_evidence.py=fffc6444…8ad90fa65`, test=`7508e5c1…ad6cb8c7`; targeted 21,
lap354 rc0/`failures=[]`, Fast 399·Ruff/compileall/mypy/CONTEXT_PASS, safety `SAFETY_PASS`; 실행 0회.
**lap356 middle:** lap355 reader wiring F1~F4 **ACCEPT**. N15 event boundary는 lap357에서 수리됐고 실제 실행·제품 증거는 UNKNOWN.
이전 상세 검증 계보와 lap355는 각 lap 기록/`20260912_status_lap356_compaction.md`, lap366 132줄 원문은 `20260912_status_lap366_precompaction.md`에 보존했다.
## 바퀴 기록
lap377 Astra 방향 → lap378 middle ACCEPT → lap379 provenance BLOCKED 뒤 사용자 product-first 지시로 반복 중단. fresh 원본 S1 실제 실행 PASS; 다음은 1600×1200 후보 S1/Stage B.
lap356~360 상세 및 진입 STATUS 원문은 `docs/history/laps/20260912_status_lap361_entry.md`에 SHA/124줄과 함께 보존.
lap363 middle: import 해소·§3 RELEASE; lap365 REJECT, lap366 RELEASE, lap367 PASS, lap368 REJECT, lap369 수리, lap370 REJECT, lap371 수리, lap372 REJECT, lap373 수리, lap374 provenance REJECT, lap375 BLOCKER, lap376 log 기반 exact 복원 가능 PASS; 게임/커밋 0.
상세는 각 lap 기록과 `20260914_lap373_luna_s1_trigger_wait_boundary_repair.md`, `20260914_lap374_middle_lap373_provenance_review.md`, `20260914_lap375_luna_provenance_repair_blocked.md`, `20260915_lap376_middle_lap372_provenance_recovery_review.md`.
