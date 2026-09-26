# lap323 갱신 전 STATUS 원문 보존

SHA256: dfa364a35e8932b1896382112ad933f342d5c1a18d425857c00778b80289f21b
줄 수: 130

```markdown
# STATUS — 매 바퀴 갱신하는 기억
## 지금 상태
G1~G4 모두 제품 미완료. M1/G1 유지: 원본 800×600 구도와 입력을 유지한 1600×1200 출력. 제품 기준은 DESIGN, 사람 승인
원문은 feedback/APPROVALS·INBOX를 따르며 2026-09-12 01:03 bounded repair→fresh validation 허가는 제품/출시 승인이
아니다. DxWrapper 출력 근거는 있으나 실제 scene/input 쌍과 WM_CLOSE 결함이 남았다.
lap275 F3-R2-R1 선언 범위 승인, lap270 R30 PASS와 R17 계약 종결 FAIL은 함께 유효하며 M11 생존을 지우지 않는다.
G1-S1 계약 계보(`…/G1_S1_MIDDLE_ACCEPTANCE_LAP277.md` §4.1~§4.7)는 **S1 fixture 정적 타당성**일 뿐 두 run 동일성·제품
증거·Stage B 허가·마일스톤 종료가 아니다. runtime/load 계보(`…/G1_RUNTIME_CONTRACT_MIDDLE_LAP284.md` §11~§14)는
lap283→lap322까지 `docs/history/laps/`에 보존된다. lap318→lap319→**lap320 ACCEPT**로 F1 종결. **lap322 middle이 §13
여섯 행을 §14로 판정**: fixture·§5(c)·하네스 경계·§5(b)(e) 예산 REJECT, §5(a) 위치·라벨만 부분 ACCEPT, §5(d)/§6
ACCEPT-WITH-CONDITION, 패키지 REJECT. runtime 예산 0·Stage B 0·제품 증거 0·S1 종결 REJECT는 그대로다.
| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | 미완료 | S1/F2-R2 결정성, fresh pair, 실제 입력, WM_CLOSE |
| G2 | 미완료 | 활성8인 전비5000·풀/메모리·저장/지원동기화 증거 |
| G3 | 미완료 | 활성9~16번 실제 플레이/직렬화/지원 통신 |
| G4 | 미완료 | 원본 대비 반복 경로/전략 지표와 개선 |
## 다음 한 가지
**다음 한 가지: 상위(Astra/사용자)가 §14.7 최소 관측 봉투 1건의 허가 여부를 판정한다.** 대상=구성 시점 `0x4D6312`가
읽는 `ds:0xE5BF1C/20` 값 1회 관측(입력 0, 클릭 0, 쌍 0). 800×600→후보A, 640×480→후보B, 그 외→두 후보 폐기·blocker.
변경 요청은 "runtime 예산 0" 한 줄뿐. 거부 시 유일한 독립 진행분은 §14.1 fixture 모델 반증(실행 예산 0)이며 정적 CFG
재개는 요청하지 않는다. N4 수리·W3 재pin 보류 유지. work 실행 카드 0. `loop/ESCALATE_SOL`로 인계.
## 지금 막힌 것 (Blockers)
- **N6(lap322 신규, 수치 영향 0, 판정 불변, 완화 아님):** lap284 probe의 두 가드가 **fail-open**이다.
  `ps_states_waited`의 `get("ps") == N` 정규식이 **집합 소속 대기**를 못 봐, 하네스가 line **3466·3902**에서 실제 대기하는
  `item.get("ps") in {4,5,6}`을 놓친다 → "PS 대기값 {3,5,7,9}뿐"은 **불완전**(형태 무관 AST 집합은 **{3,4,5,6,7,9}**).
  같은 이유로 `ps35_references`는 `in {35,...}` 형태를 **미탐지**한다. **결론은 생존:** "PS35 참조 0"을 lap322가 형태 무관
  스캔 `bare_35_occurrences=0`으로 재성립(값은 옳았고 근거가 약했다). 원문 불변, 로드 경로는 PS 대기 **형태**를 선언해야 한다.
- **표기 정정(lap322, 수치 영향 0):** §5(d)의 "flush는 stage 단위"는 과소 표기다 — `_g1_flush_input_stage` 호출 지점 **9개**로
  매 입력 기록마다 불려 주기는 **레코드 단위**이므로 필요한 것은 새 flush 주기가 아니라 **새 필드**다. **예산 기구도 이미
  있다:** `G1_INPUT_STAGE_BUDGETS={unit_select,drag_select,minimap:10.0}`·4값 `stage_budget_state`·
  `G1_INPUT_MAX_TRUNCATION_RATIO=0.25`이고 `runtime_env.py:2202-2205`가 그 25%를 **측정이 아닌 설계 가정**이라 스스로 선언
  → §5(e)는 예산 발명이 아니라 로드 단계 키 추가+가정 선언 문제다. §5(b) 3 MB 로드 소요는 측정치 **0**이고 과거
  8.4~19.1초는 **새 게임** run이라 대체 금지.
- S1/F2-R2 실제 결정성 미해결(S1 여섯 행은 정적 CONFIRMED지만 **fixture 타당성**일 뿐 — 두 run 값 동일성 미검증).
  Stage B·원본 재실행·Wine/Xvfb·R6-A/R6-C·production 클릭 금지. 원본/제품 EXE·DLL/assets/baseline/golden 변경,
  evidence 재사용, blind retry, PASS 완화 금지.
- **저장/불러오기 절대 좌표 — 정적으로 좁혀졌으나 미확정.** 중심식 `cdq; sub eax,edx; sar`을 화면·다이얼로그에 적용해
  `ds:0xE5BF1C/20`과 sprite에서 origin을 만들고 `ds:0x1088B5C/5E`에 16-bit 저장(읽는 시점은 구성 `0x4D6312`). **R6:**
  `ds:0x4ED810` 참조 6개 전부 읽기, 초기값 **3**, `table[2]=0x464502` → **800×600** → 후보 **A 정적 우세**. 미확정 이유:
  `0x4ED810`은 쓰기 가능 `.data`라 계산 포인터/파일 로드를 실행 없이 못 배제하고 dialog 시점 다른 writer도 미확정.
  **lap322 §14.3 신규:** `yfnt/saveloadtitle.spr` 102,260 B `7d154cdb…c08a5c5` 헤더 `[9,320,310,1]`에 같은 식을 대입하면
  `((800-320)//2,(600-310)//2)`=**A(240,145)**, `((640-320)//2,(480-310)//2)`=**B(160,85)** — 즉 **A/B는 두 가설이 아니라
  하나의 식을 두 전역값에 대입한 결과**이고 선택은 구성 시점 `ds:0xE5BF1C/20` 값과 동치다. **정적 지렛대 소진:** 더
  좁힐 정적 수단을 middle이 특정하지 못했다 → 정적 CFG 재개 사유로 쓰지 않고 §14.7로 반환.
- **map↔dialog 실제 event/thread 순서 UNKNOWN(lap308~316·lap322 모두 못 좁힘).** 정적 사실: 앵커 일치, `0x431AB0` 직접
  caller `0x48F538` 1개, `0x4D60B0` caller `0x4D69E5/0x4D6A05`, 640×480 reset writer 2개가 성공 return **지배**, 실패 경로
  runtime writer **0개**, lap310 절대 dword 스캔 리터럴 **0건**(계산 포인터는 배제 불가).
- **R2 = 4회 독립 재유도(lap314·316·318·320).** 창/entry **753**, 실패 arm **7**, 성공 arm **724**, unresolved **0**,
  화면 전역 census **4건 전부 직접 dword store** `{0x431B79, 0x431B7F, 0x4324B8(0x280), 0x4324C2(0x1E0)}`(moffs 0·실패
  arm writer 0), gate `0x431AF2`=`750a`→`0x431AFE`. D1 공허성은 **22-노드 증인 경로**로 재확인. 원문은 lap314~320 기록.
- **F1 = 종결(lap319 수리 → lap320 ACCEPT).** 결함은 objdump 접힘의 **무징후 절단**, 수리는 **명령 단위 길이 불변식**.
  접힘 27 전부 절단·초과 0, 두 reset `0x4324B8`(`0xE5BF1C`=640)·`0x4324C2`(`0xE5BF20`=480)이 파일·델타·열 **세 출처
  일치**. lap318의 "7B 초과"는 **길이 기준** 표현(표기 정정, 수치 영향 0). 원문은 lap319/lap320 기록과 압축본.
- **N4·N5(lap320, 수치 영향 0, 완화 아님):** (N4) lap319 `main()`의 `checks` 선평가가 reset 행 부재 시 **KeyError로 죽어
  FAIL JSON을 못 남긴다**(값 누출 0). (N5) 남은 직접 행 조회는 gate 파일 2B 교차검증·`is_contiguous=False`로 닫힌다.
  **lap322(§14.8):** 그 probe를 실행 게이트로 채택하지 않아 N4 수리를 선행 조건으로 **지정하지 않는다**. W3 재pin도 미승인.
- **UNKNOWN 유지(F1 범위 밖):** (N1) 지도 창 간접 분기 **0개**라 lap315 E1 수리는 실제 대상에서 **inert**(합성 fixture만
  실행 — "간접 분기 확인"으로 승격 금지). (N2) 창 안 **call 31개** fall-through → callee 쓰기·cross-function 순서·**D5**
  under-claim·계산/간접 writer·실제 실행 모두 UNKNOWN. (N3) 접힌 행의 `ds:0xB3AC88`=`0x33F`/`0xB3AC8C`=`0x1FF`는
  화면 전역 아님, 의미 UNKNOWN.
- **lap312 강화 사실 유지:** 네 writer 전부 성공 경로 필수, `0x4324C2` 이후 도달 명령 4개에 화면 writer **0개** → 성공
  반환 시 **마지막 직접 쓰기는 640×480 reset**. **화면 전역 writer 하한 20(lap306):** 절대 4 + mode-table 16, `push
  0xE5BF18` 291개 전부 `0x465250`(=`vsprintf`+`MessageBoxA` 헬퍼, lap310 정정); computed pointer·indirect dispatch는
  fail-open. **moffs 종결:** 화면 전역 대상 moffs 저장 **0건**. lap310 정정(ii): `test_call_convention_cleanup_is_explicit`는
  상수표 **동어반복**이라 `4`/`16`의 독립 증거가 아니다.
- **provenance 회귀(전부 보존, 고쳐 쓰지 않음):** (a) lap301이 probe를 덮어써 lap299 report `8e735a9a…`는 재현 불가,
  lap301의 `"lap": 299` 오기도 그대로 둔다. (b) lap306 V2의 자칭 `lap 306`은 **실제 러너 lap 307**, 드리프트는 lap308부터
  **닫혔다**(`loop-progress.result`의 `lap=`은 직전 완료 lap이라 1 차이가 정상). (c) `lap306_v2_mode_writer_order.json`은
  **손 전사 요약**이라 SHA가 생성기 출력을 고정하지 못한다. (d) lap311 probe 약칭은 `a33f216a…8fd4524`가 실제이며
  과거 압축본의 틀린 꼬리는 고치지 않는다. 상세는 각 lap 기록.
- comparator는 scene 4축과 선택 slot만 본다. nation/slot id/절대 selection·camera/tick은 기계 검사 밖이라 (B) 원시 필드 대조로만 확인하고 overall PASS도 충분조건이 아니다. `scene.owners`=owner0~7 → owner8~15 미가시(G3 위험).
- R17 구조 재결 미완료·R31 금지, R29 범위 승인 거부(lap266), R30 M11 생존, R6-B-R2 count 1→0 미결(규칙 변경 금지).
  lap274 추출기 M-d/M-e 생존은 드리프트 사각. offline 8건 주차: H=F2-R1/F3-R1/F6-R2, C=R23/R24·stage_budget_state,
  N=R20/R21/R22. 삭제/PASS 전환 없음. **W2(lap296 §4.7.4):** `runtime_driver.py`의 매직 리터럴 — (a) `0x8990C8`·
  `0x66B790`/`0x758` 승격 가능, (b) `0x8D`는 probe 가드 선행, (c) `0x8E`는 상수 부재·값 미재유도라 명명 **금지**.
- **W3(lap300 §4):** lap296 review probe의 `EXPECTED_SHA["target_probe"]`가 수리 전 SHA를 가리켜 **영구 exit1**, 회귀 게이트
  재사용 불가. 재pin은 자가 갱신이라 middle/work 단독 금지 — Astra/사용자 결정 대기. lap302~322 probe는 자기 산출물 SHA를
  단언하지 않아 이 함정을 피한다. **가드 잔여 사각:** `type`/`owner` 가드는 값 드리프트를, lap301 `contains_all`은
  `add eax/ecx,0x18`을 구별 못 하고 lap303 앵커는 중심식 4쌍을 뺀다. lap306 `callee_body` 절단과 **N6의 두 정규식**도
  같은 종류의 구조적 fail-open이다(수치 영향 0).
- 후보 WM_CLOSE teardown 결함, 실제 후보 scene/input evidence, G2~G4 증거 미해결. lap279/lap280/lap284-middle 세 probe는
  아직 `0x440FF0` 창을 써 legacy window 오분류 위험. **lap292 사각:** 이름 결합 단언이 reader 이름을 안 봐 폭 드리프트 통과.
- **프로세스 사각:** 상수/앵커 승격 시 결합된 과거 probe 미재실행 → 잠복 결함 재발(lap294·lap296). **provenance:** lap287
  경고=lap290 부록, lap293/lap297/lap317 `ESCALATE_SOL`=각 lap294/298/318 부록 A(소비),
  lap321 `ESCALATE_SOL`(`761275fb…f01297dd`)=lap322 부록 A(소비), lap300~321 STATUS 원문=각 압축본.
- map-layer serializer **28쌍** 모델은 lap286이 재현해 ACCEPT(`1,400,702`+`30.5`). 한계: 네 fixture가 전부 정사각·짝수
  변이라 오프셋 210/212 배정과 halving layer `((w/2)*h)/2` 대 `(w*h)//4`를 구분 못 한다 → **lap322 §14.1이 fixture 행을
  REJECT한 직접 이유**(§7 카드 4항 nation/활성 구성 미산출). owner `+0x8E` 상속·save/load 동일성도 미검증.
- **G3 저장 포맷:** bulk `0x892410..0x975D8C`에 PlayerStruct 8개는 들어가지만 16개는 `0x1B5A4` B 넘친다 → 9~16번 직렬화 공간 없음. G1 범위에서 수리하지 않는다.
- **로드 경로 부재(lap284·lap298 → lap322 §14.4 재측정):** `runtime_env.py`의 `save` 참조 **0**, 리터럴 `35` **0회**(형태 무관
  스캔) → 수정 대상 함수·기록 위치 미확정으로 "연구 하네스" 행 **REJECT 유지**(PS 대기값 서술은 N6로 정정). save000
  (`1c703551…`)/save006(`616b7997…`) 유지는 옳으나 §7 카드 4항 미산출이라 잠정("owner id ≥8 record 0개"만 공통).
- **실행 봉투 미성립(lap284 §5 → lap322 §14.5·§14.6):** (a)~(e) 미제출로 봉투 행 **REJECT 유지**. §6은 기구 충분·필드 선언
  미완이라 **ACCEPT-WITH-CONDITION** — 네 실패 모드(PS35 미도달/PS35 도달·PS3 미도달/timeout/수집 실패)에 원시 PS·tick·
  경과·run ID·소유 PID·입력·오류·flush 경로·종료 방식을 실행 전 선언해야 한다.
- **Plan C 함정(lap298 §10.3 봉인 유지):** 공유 temp 800×600 `…_21_load_screen.png`(`5e95ed92…d17e5879`)는 원본 로드 대화상자가 **아니다**(출처는 Plan C `save_load_screen.cpp`) → 좌표 출처 금지. **주소 실재≠좌표 출처 적격**.
- **lap301~322 probe의 제품 한계:** 앵커·pin·모드 테이블·CFG 지배는 정적 확인이나 **구성 시점 전역값은 실행 없이 미관측**,
  hitbox·슬롯 선택·로드 전이는 UNKNOWN, call fall-through로 cross-function 순서 미증명. **tick 순환 의존은 해소**
  (lap297 결정1+lap298): 연구 쌍 tick은 report-only, 제품 S1 (A)+(B) 불변. **`(296,505)`:** 위치·라벨만 확정,
  **클릭 결과 미관측**, 하네스에 **0회** 등장(문서 전용).
## 검증 상태
**lap322 middle (probe `14dd9768…94b051a3`, report `bcf4f0a9…6f7f3c3674`, exit0, failures=[], 연속 2회 stdout 동일):**
§13 여섯 행 심사 완료(§14). 이전 lap probe를 import하지 않고 fixture SHA·타이틀 14장 단일 SHA `277a0b23…9ce5b252`·전부
800×600·sprite 헤더·하네스 사실을 재유도했고, lap320 report 재실행이 `3d0022b8…a24f60da` byte-identical(재현성 확인이며
새 독립 알고리즘 검수 아님). `make check` **361 passed**, Ruff/compileall/mypy/CONTEXT_PASS, **SAFETY_PASS**, 원본 SHA 불변.
tools/tests/probe/pin/baseline/golden 무변경(테스트 수 361 불변이 기계 증거). 게임/Wine/Xvfb/StageB/PNG/click 0.
**기술 컨펌이며 사용자 마일스톤 승인도 제품 증거도 아니다.**

**lap321 Astra:** lap320 fresh report byte-identical·failures=[]; 361 passed·SAFETY_PASS·원본 SHA 일치. §13 방향
RECORDED·middle PENDING. 실행 근거 미확정으로 ESCALATE_SOL 인계. 상세는 lap321 기록/logs.

**lap320 middle (probe `68cbfb4b…5a85226c7`, report `3d0022b8…a24f60da`, exit0, 연속 2회 stdout 동일):** lap319 F1
**ACCEPT** — lap315/316/319 probe를 import하지 않고 753/7/724·unresolved 0·writer 4/0·gate·접힘 27·두 reset을 전부 재유도
일치(화면 writer는 **바이트 디코드**), targeted 11 passed, 361 passed, SAFETY_PASS, 원본 SHA 불변. **lap319 work:** F1
수리 PASS, targeted 8 passed, 350 passed, SAFETY_PASS. 상세·SHA는 lap319·lap320 기록.
**lap313~318 (SHA·수치 원문은 각 lap 기록과 압축본):** lap318 `020f3fab…2a3d29b9`가 lap317 ACCEPT-WITH-REVISION(342
passed), lap317 Astra는 lap316 fresh report 동일·failures=[](328), lap316 `6bc0923a…6aedcb80`가 lap315
ACCEPT-WITH-NOTES, lap314 `44a115e6…a7b75e49`가 lap313 ACCEPT-WITH-CORRECTION, lap312가 lap311
ACCEPT-WITH-STRENGTHENING, lap310 `cb4e6c51…869f5d933`이 lap309 V3 ACCEPT. 원본 SHA 전 구간 불변.
**lap286~308 (원문은 `docs/history/laps/` 및 각 압축본):** lap308 V2 ACCEPT-WITH-CORRECTION, lap306 하한 20·
cross-function UNKNOWN, lap305 291 stack paths, lap304 R6 800×600, lap303 직접4+간접16=20, lap302 `.text`/`.data` 범위,
lap301 writer 4·후보 A/B PASS, lap296이 lap295 수리 ACCEPT, lap286 save 레이아웃 재현했으나 카드 종결 REJECT.
lap279~320 수치는 게임 검증으로 승격하지 않는다. G1 제품 증거 0.

## 바퀴 기록
lap2~321 상세·미결·압축 원문은 `docs/history/laps/`에 보존. 직전 STATUS 127줄은
`20260912_status_lap321_compaction.md`에 원문 SHA `ac82284c…a618f6bd6`와 함께 보존했다.
lap322 middle: §13 여섯 행을 §14로 판정, N6·flush 표기 정정 2건 추가, 최소 관측 봉투 1건만 상위 반환, work 카드 0.
lap321 ESCALATE_SOL(`761275fb…f01297dd`)은 lap322 기록 부록 A로 **소비**. 상위 허가 PENDING, 제품 미완료 유지.
```
