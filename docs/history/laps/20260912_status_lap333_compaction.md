# lap334 편집 전 STATUS 원문 보존

원문 SHA256: `b2d2c230c907d0e34629cdd2e188013ee41d49d680aa2be2b45597f617ee1e5d`
원문 줄 수: 130
보존 방법: 편집 전 파일 bytes를 UTF-8로 그대로 아래에 수록.

```markdown
# STATUS — 매 바퀴 갱신하는 기억
## 지금 상태
G1~G4 모두 제품 미완료. M1/G1 유지: 원본 800×600 구도와 입력을 유지한 1600×1200 출력. 제품 기준은 DESIGN, 사람 승인
원문은 feedback/APPROVALS·INBOX를 따르며 2026-09-12 01:03 bounded repair→fresh validation 허가는 제품/출시 승인이
아니다. DxWrapper 출력 근거는 있으나 실제 scene/input 쌍과 WM_CLOSE 결함이 남았다.
lap275 F3-R2-R1 선언 범위 승인, lap270 R30 PASS와 R17 계약 종결 FAIL은 함께 유효하며 M11 생존을 지우지 않는다.
G1-S1 계약 계보(`…/G1_S1_MIDDLE_ACCEPTANCE_LAP277.md` §4.1~§4.7)는 **S1 fixture 정적 타당성**일 뿐 두 run 동일성·제품
증거·Stage B 허가·마일스톤 종료가 아니다. runtime/load 계보(`…/G1_RUNTIME_CONTRACT_MIDDLE_LAP284.md` §11~§14)는
lap283→lap325에 보존된다. lap320 ACCEPT로 F1 종결, lap322가 §13을 §14로 판정, lap323이 §14.7 봉투 REJECT,
lap324가 R1 개정안 반환, lap325가 조건부 허용, lap326 middle이 R1 봉투 ACCEPT, lap327 work가 §5 구현,
lap328 middle이 REJECT, lap329 work가 수리, lap330 middle이 제한 1 run을 발효, lap331 work가 정확히 1회 실행해
`OBSERVED/REACHED_CHANGED`를 얻었고, **lap332 middle이 그 artifact를 재실행 없이 독립 검수해 ACCEPT, R1 연구 레인을
종결했다.** Stage B 0·제품 증거 0·S1 REJECT는 그대로다.
| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | 미완료 | S1/F2-R2 결정성, fresh 원본/후보 pair, WM_CLOSE |
| G2 | 미완료 | 활성8인 전비5000·풀/메모리·저장/지원동기화 증거 |
| G3 | 미완료 | 활성9~16번 실제 플레이/직렬화/지원 통신 |
| G4 | 미완료 | 원본 대비 반복 경로/전략 지표와 개선 |
## 다음 한 가지
**middle이 lap333 ESCALATE_SOL의 STATUS 편집안 길이 실패(131>130)와 후보 R1 방향을 검수한다.**
방향 문서: `docs/work/active/G1_CANDIDATE_R1_DIRECTION_LAP333.md`. 후보 봉투 미확정; 실행0회.
실패 편집안은 쓰기 전 중단되었고 기존 원문은 `20260912_status_lap332_compaction.md`에 보존했다.
W3 재pin·원본 n>1·예산 확대·Stage B·PNG·baseline/golden 변경 불허. 후보 근거/봉투는 middle/work로 분리.
## 지금 막힌 것 (Blockers)
- **R1 ACCEPT(lap332); lap333 후보 R1 방향 결정, 봉투·문서 실패 검수 대기:** artifact 3종 SHA 일치, `r1_load_origin.json` 전 저장소 **1건**,
  PNG 0, 봉투·네 모드·시계열·cleanup 전부 PASS. post origin `(240,145)`는 run 자신의 스프라이트 헤더 `[9,320,310,1]`로
  재계산한 후보 **A**와 일치하고 `tag==8`이 `push 8` 경로를 지목해 형제 경로(`push 0x3E8`)를 배제한다.
  **그러나 이는 content 800×600 원본 baseline이지 1600×1200 후보 증거가 아니다.** n=1이라 결정성은 미측정, 재클릭 금지.
- **정정 C1(lap332, 수치 영향 0):** 디스패처 `0x4233B8`은 테이블 진입 전에 `cmp eax,0x28; jg 0x42351F; je 0x423515`
  사다리를 갖는다(>40 arm 머리 `cmp eax,0x131`). lap326 §1 서술이 이를 빠뜨렸다. 관측된 PS `40/150/180`은 찢김이
  아니라 **정당한 상태값**이다. 35는 그대로 테이블 34번(`0x42341B`)로 가므로 판정식 영향 0이고, PS 레지스터 store
  33건 fail-open도 닫히지 않는다(명제는 계속 "PS==35를 관측했다"). **N8:** lap331 기록/STATUS가 이 3건을 미공개했다.
  **N9:** `manifest.runtime_config`는 prepare 스모크(`1024x768x24`, `(184,560)`)를 기술하며 R1 run을 기술하지 않는다.
- **R1 범위 밖은 그대로 미검증:** fresh 원본/후보 동일상태 pair·PNG·WM_CLOSE·S1/F2-R2 결정성은 아직 없다.
  배분 40/20/15/15는 단일 표본 elapsed 4.278초와 대조해도 재평가가 필요한 설계 가정이다.
- **exact-site 계측 불가(lap324 확정, lap326 유지):** 읽기 수단은 `process_vm_readv` 폴링뿐이고
  `process_vm_writev`/`ptrace`/`int3`/`winedbg`/`gdb` **0회**. 기구를 만드는 것 자체가 금지 위반이다.
  R1은 exact-site를 포기하고 **산출물(origin 전역)** 을 읽는다. 이 포기는 lap326에서도 유지된다.
- **lap324 §2.3 정정(lap326, 원문은 lap326 기록):** E8-only 그래프가 `0x4A2FF5` 꼬리 `jmp`를 놓쳤다. 실제 사슬
  `0x423411→0x4248E0→0x4A2FF0→jmp 0x493C40→push 8→0x4D6A00→0x4D60B0→x·y·tag→ret→0x4248E5 PS:=35`는 전 간선
  무조건 ⇒ PS==35는 세 store 뒤, 게이트된 1회 read에 찢김 없음(lap332가 7지점 바이트·rel32 3건 재유도). 수치 영향 0.
- **도달 판정식(lap326 확정, lap332 C1로 보정):** PS는 WORD@`0x4ED818`, 점프테이블 `0x423738` 35엔트리(인덱스 PS-1,
  PS9→`0x423407`/PS34→`0x423411`/PS35→`0x42341B`). PS 즉시 store 71건 중 값 35는 1건(`0x4248E5`), origin 미참조라
  순환 아님. **fail-open: 레지스터 store 33건 값 미상.**
- **저장/불러오기 절대 좌표 — 원본 baseline은 lap331/332가 실측했다.** 중심식이 sprite 크기로 origin을 만들어
  `ds:0x1088B5C/5E/60`에 16-bit 저장(직접 store 1/1/2, 전부 BSS 0). 예측 (P1) PS9 pre `(0,0,0)`·A `(240,145)`·
  `tag==8`이 **전부 실측과 일치**했고 B `(160,85)`와 R6(초기 모드 3→800×600)은 그대로다. **잔여 fail-open:**
  계산/간접 writer 미배제(N2), `0x4D60B0` 조기 반환 시 post==pre==0 → UNKNOWN. 원문은 lap326·lap332 기록.
- **좌표계는 해소(lap326).** `runtime_env.py:3413-3421`의 **이미 PASS한** 타이틀 입력이 변환을 고정한다
  (`root=content_crop+client`, 실증 `(184,560)`→PS9→PS7, content 800×600·root 1600×1200 강제, scale 1.0).
  `(296,505)`는 같은 좌표계·같은 변환이라 새 근거가 필요 없다.
- **map↔dialog 실제 event/thread 순서 UNKNOWN(lap308~316·lap322).** 정적 사실: 앵커 일치, `0x431AB0` 직접 caller
  `0x48F538` 1개, `0x4D60B0` caller 2개(lap326 재확인), 640×480 reset writer 2개가 성공 return **지배**,
  실패 경로 runtime writer **0개**, lap310 절대 dword 스캔 리터럴 **0건**(계산 포인터는 배제 불가).
- **R2 = 4회 독립 재유도(lap314·316·318·320) + lap324 재확인.** 창/entry **753**, 실패 arm **7**, 성공 arm **724**,
  unresolved **0**, 화면 전역 직접 store **4건** `{0x431B79,0x431B7F,0x4324B8,0x4324C2}`(moffs 0·실패 arm writer 0),
  gate `0x431AF2`=`750a`→`0x431AFE`. D1 공허성은 22-노드 증인 경로로 재확인. 원문은 lap314~320 기록.
- **F1 = 종결(lap319 수리 → lap320 ACCEPT).** 결함은 objdump 접힘의 무징후 절단, 수리는 명령 단위 길이 불변식.
  접힘 27 전부 절단·초과 0, 두 reset이 파일·델타·열 세 출처 일치. 원문은 lap319/lap320 기록과 압축본.
- **N4·N5·N6·N7(수치 영향 0, 완화 아님, 원문은 lap320·lap322·lap330 기록):** (N4) lap319 KeyError 함정은 lap327
  구현이 형태를 재사용하지 않아 미발동. (N5) gate 2B 교차검증으로 닫힘. (N6) `G1_R1_WAIT_PS_STATES=(9,35)` 선언과
  lap328 F4 ACCEPT로 해소. (N7) 클릭 후 `post` 대입 전 예외를 TIMEOUT으로 적는 삼항은 lap331 run에서 미발동.
- **UNKNOWN 유지(F1 범위 밖):** (N1) 지도 창 간접 분기 0개라 lap315 E1 수리는 실제 대상에서 inert(합성 fixture만
  실행). (N2) 창 안 call 31개 fall-through → callee 쓰기·cross-function 순서·D5 under-claim·계산/간접 writer·실제
  실행 모두 UNKNOWN. (N3) 접힌 행의 `ds:0xB3AC88`=`0x33F`/`0xB3AC8C`=`0x1FF`는 화면 전역 아님, 의미 UNKNOWN.
- **lap312 강화 사실 유지:** 네 writer 전부 성공 경로 필수, `0x4324C2` 이후 도달 명령 4개에 화면 writer **0개** →
  성공 반환 시 마지막 직접 쓰기는 640×480 reset. **화면 전역 writer 하한 20(lap306):** 절대 4 + mode-table 16,
  `push 0xE5BF18` 291개 전부 `0x465250`(lap310 정정); computed/indirect fail-open, moffs 저장 0건. lap310 정정(ii):
  `test_call_convention_cleanup_is_explicit`는 상수표 동어반복이라 독립 증거가 아니다.
- **provenance 회귀(전부 보존, 고쳐 쓰지 않음. 원문은 lap301·306·311·322·324 기록):** (a) lap299 report 재현 불가와
  lap301 `"lap": 299` 오기, (b) lap306 V2 자칭 lap 드리프트, (c) 손 전사 요약 JSON의 SHA 무효, (d) lap311 약칭
  `a33f216a…8fd4524`, (e) lap322 최종 `7d04b9b2…35757ac`, (f) "테스트 수 불변 ⇒ 소스 무변경"은 증거가 아니다.
  (g) **문서 정정 대기:** `player_offsets.md`의 `0x00B92CC0` 행은 실제로 **WORD·다음 상태 요청**. 수치 영향 0, 별도 카드.
- comparator는 scene 4축과 선택 slot만 본다. nation/slot id/절대 selection·camera/tick은 기계 검사 밖이라 (B) 원시 필드
  대조로만 확인하고 overall PASS도 충분조건이 아니다. `scene.owners`=owner0~7 → owner8~15 미가시(G3 위험).
  R17 구조 재결 미완료·R31 금지, R29 범위 승인 거부(lap266), R30 M11 생존, R6-B-R2 count 1→0 미결. lap274 추출기
  M-d/M-e 생존은 드리프트 사각. offline 8건 주차: H=F2-R1/F3-R1/F6-R2, C=R23/R24·stage_budget_state, N=R20/R21/R22.
  **W2(lap296 §4.7.4):** `runtime_driver.py` 매직 리터럴 — `0x8990C8`·`0x66B790`/`0x758` 승격 가능, `0x8D` 가드 선행, `0x8E` 명명 금지.
- **W3(lap300 §4):** lap296 review probe의 `EXPECTED_SHA["target_probe"]`가 수리 전 SHA를 가리켜 영구 exit1. 재pin은
  자가 갱신이라 middle/work 단독 금지 — Astra/사용자 결정 대기. lap302~332 probe는 자기 산출물 SHA를 단언하지 않아 이
  함정을 피한다. **가드 잔여 사각:** `type`/`owner` 가드의 값 드리프트, lap301 `contains_all`, lap303 앵커의 중심식 4쌍.
- 후보 WM_CLOSE teardown 결함, 실제 후보 scene/input evidence, G2~G4 증거 미해결. lap279/lap280/lap284-middle 세 probe는
  아직 `0x440FF0` 창을 써 legacy window 오분류 위험. **lap292 사각:** 이름 결합 단언이 reader 이름을 안 봐 폭 드리프트 통과.
- **프로세스 사각:** 상수/앵커 승격 시 결합된 과거 probe 미재실행 → 잠복 결함 재발(lap294·lap296). **provenance:** lap287
  경고=lap290 부록, lap293/lap297/lap317 `ESCALATE_SOL`=각 lap294/298/318 부록 A, lap321=lap322 부록 A, lap323=lap324
  부록 A, **lap325=lap326 부록 A(소비)**. lap300~325 STATUS 원문=각 압축본.
- map-layer serializer **28쌍** 모델은 lap286이 재현해 ACCEPT(`1,400,702`+`30.5`). 한계: 네 fixture가 전부 정사각·짝수
  변이라 오프셋 210/212 배정과 halving layer 구분 불가(lap322 §14.1 REJECT 사유), owner `+0x8E` 상속·save/load
  동일성 미검증, save000/save006 유지는 §7 카드 4항 미산출로 잠정.
- **G3 저장 포맷:** bulk `0x892410..0x975D8C`에 PlayerStruct 8개는 들어가나 16개는 `0x1B5A4` B 초과 → 9~16번 직렬화 공간 없음. G1 범위에서 수리하지 않는다.
- **실행 봉투(lap284 §5 → lap322 §14 → lap324 → lap326 → lap328 → lap331):** (a)~(e) 미제출 행은 R1 봉투가 대체한다. 네 실패
  모드(미도달/전역 미변화/timeout/수집 실패) 선언은 필수이고 lap326이 `pending_state`·`origin_tag`·`ps_word`/`ps_dword`
  를 추가했다. 배분(준비40/클릭20/관측15/종료15초, 합 ≤90초)은 **가정**이며 lap331 run elapsed는 4.278초였다(자동 연장·재시도 금지).
- **Plan C 함정(lap298 §10.3 봉인 유지):** 공유 temp `…_21_load_screen.png`(`5e95ed92…d17e5879`)는 원본 로드 대화상자가 **아니다**(Plan C `save_load_screen.cpp` 출처) → 좌표 출처 금지. **주소 실재≠좌표 출처 적격.**
- **lap301~328 probe의 제품 한계:** 앵커·pin·모드 테이블·CFG 지배·상태 전이 순서·하네스 분류 동작은 정적/합성 확인일
  뿐 **구성 시점 전역값은 실행 없이 미관측**, hitbox·슬롯 선택·로드 전이는 UNKNOWN. tick 순환 의존은 lap297~298에서
  해소(연구 쌍 tick은 report-only, 제품 S1 (A)+(B) 불변).
## 검증 상태
**lap332 middle:** lap331 artifact **ACCEPT**(재실행·입력·쓰기·PNG 0). 신규 probe
`…20260912_lap332_middle_lap331_r1_artifact_probe.py`(`e8dc8c75…a1f9c367`) rc0·`failures=[]`·stdout
`5efe92a0…6cc31afc`(연속 2회 byte-identical). 1차 출처만 사용: 보존 artifact·run 자신의 PE 바이트·스프라이트 헤더.
검수 SHA == 실행 SHA(`997ff15b…cc46eed`/`81acc11e…cac72`), 원본 EXE `b56986e0…c08a8ac` 불변. 표본 12건 전부
WORD==DWORD·단조·`pending` 0→34 단일 전이, 사슬 7지점 바이트·rel32 3건 재유도 일치. 정정 C1·N8·N9는 블로커에.
make check **368 passed**(60.31s)·Ruff/compileall/mypy/CONTEXT_PASS·rc0, SAFETY_PASS. 게임 코드/하네스 변경 0, 실행 0, 커밋 0.
**lap331 work:** 새 private run `20260912_172722_2210599_0`에서 R1을 정확히 1회 실행, `OBSERVED/REACHED_CHANGED`, elapsed 4.278s.
실제 클릭 1회·PS 9→35·pending 0→34·origin `(0,0,0)`→`(240,145,8)`, root 1600×1200/content 800×600, cleanup OK.
`r1_load_origin.json` SHA `76ce7788…bfa442cf`, manifest `4109704a…d18096a2`, 원본/하네스 SHA 불변; 제품 G1/Stage B 승격 아님.
**lap330 middle:** lap329 수리 **ACCEPT**, 제한 1 run 발효. 신규 probe
`…20260912_lap330_middle_lap329_r1_repair_probe.py`(`37be75bf…5ec62d680`) rc0·failures=[]·stdout
`d2caedd7…f57507850`(연속 2회 byte-identical). 현물 SHA는 lap329 기록과 일치(`997ff15b…cc46eed`/`81acc11e…cac72`);
D1b는 커널이 만든 실제 실패 `[Errno 3] read 0:0, got -1/6`(자기 프로세스 pid0/addr0)를 통과시켜 errno·6·-1·site
분해를 확인했고, D3는 테스트 6개 전부 분류기 경유·자기주입 0·skip 0. 독립 재현: make check **368 passed**·
Ruff/compileall/mypy/CONTEXT_PASS·exit0, SAFETY_PASS, 원본 EXE SHA 실측 불변. 게임 코드/하네스 변경 0, 실행 0, 커밋 0.
**lap329 work:** (R-a)(R-b)(R-c) 수리, R1 테스트 7 passed, 368 passed, SAFETY_PASS, 실행 0.
**lap328 middle:** lap327 구현 ACCEPT-WITH-REQUIRED-REPAIR, probe `29b6ca76…737a3e9c` rc0·stdout `99900d58…0ace88eb`,
D1·D2 재유도, 367 passed, 실행 0. **lap327 work:** 연구 전용 `g1-r1-load-origin` 경로 추가(§5 구현), 367 passed, 실행 0.
**lap326 middle:** R1 봉투 ACCEPT, probe `70c9cc17…5f17bd8` rc0·stdout `1bff28d4…10cf0785`, 361 passed, 실행 0.
**lap325 Astra:** lap324 probe 1회 재현, failures=[], SHA `c00eed09…59fbb1e21cf` 동일(새 독립 알고리즘/실행 증거 아님),
361 passed, SAFETY_PASS, 보호 트리 127파일 SHA 동일. **lap324 middle:** 제출 봉투 BLOCKED, R1 상위 반환.
**lap323 Astra:** §14.7 봉투 REJECT, STATUS 길이 131>130 FAIL 후 중단, Fast SKIP. **lap322 middle
(`14dd9768…94b051a3`):** §13 여섯 행 심사(§14), 361 passed. **lap320 (`68cbfb4b…`):** lap319 F1 **ACCEPT**, 11 passed.
**lap286~318(판정·SHA 원문은 각 lap 기록과 압축본):** lap318=lap317 ACCEPT-WITH-REVISION(342), lap317 Astra=lap316
동일(328), lap316=lap315 ACCEPT-WITH-NOTES, lap314/312/310/308 ACCEPT 계열. lap306 하한 20, lap305 291 stack paths,
lap304 R6 800×600, lap303 직접4+간접16=20, lap301 writer 4·A/B PASS, lap296 ACCEPT, lap286 REJECT. 원본 SHA 불변.
lap279~332 수치는 게임 검증으로 승격하지 않는다. G1 제품 증거 0.

## 바퀴 기록
lap333: 문서 방향/ESCALATE 보존, 길이 검사 실패 후 중단(상세 `20260912_lap333_astra_candidate_r1_direction.md`). lap2~330 상세·미결·압축 원문은 `docs/history/laps/`에 보존. 직전 STATUS 원문(126줄)/SHA(`a8820ae7…d25315b1`)은 `20260912_status_lap331_compaction.md`에, 그 이전(127줄, `16e7ef82…a918bdaa`, 편집 역적용 복원본)은 `20260912_status_lap329_compaction.md`에 보존했다.
lap326: R1 봉투 ACCEPT. lap327: R1 work 구현. lap328: 실행 전 독립 검수 — 구조 ACCEPT, D1/D1b/D2/D3 수리 요구. lap329: 그 수리. lap330: 수리 독립 재검수 ACCEPT — 제한 1 run 발효. lap331: R1 정확히 1회 실측 `OBSERVED/REACHED_CHANGED`. **lap332: 그 artifact 독립 검수 ACCEPT, R1 연구 레인 종결, 정정 C1·N8·N9 기록, 상위 방향을 `loop/ESCALATE_SOL`로 이관.** 게임 코드/실행 하네스 변경 0, 마일스톤 종료/이동·제품 승인 없음.
```
