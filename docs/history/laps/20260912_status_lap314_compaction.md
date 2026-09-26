# STATUS — 매 바퀴 갱신하는 기억
## 지금 상태
G1~G4 모두 제품 미완료. M1/G1 유지: 원본 800×600 구도와 입력을 유지한 1600×1200 출력. 제품 기준은 DESIGN,
사람 승인 원문은 feedback/APPROVALS·INBOX를 따르며 2026-09-12 01:03 bounded repair→fresh validation 허가는
제품/출시 승인이 아니다. DxWrapper 출력/30초 렌더 근거는 있으나 실제 scene/input 쌍과 WM_CLOSE 결함이 남았다.
lap275 F3-R2-R1 선언 범위 승인, lap270 R30 선언 범위 PASS와 R17 계약 종결 FAIL은 함께 유효하며 M11 생존을
지우지 않는다. G1-S1 계약 계보(`…/G1_S1_MIDDLE_ACCEPTANCE_LAP277.md` §4.1~§4.7, 근거 lap276~296)는 **S1
fixture 정적 타당성**일 뿐 두 run 동일성·제품 증거·Stage B 허가·마일스톤 종료가 아니다. runtime/load
계보(`docs/work/active/G1_RUNTIME_CONTRACT_MIDDLE_LAP284.md` §11·§12)는 lap283 Astra→lap312 middle까지
`docs/history/laps/`에 보존된다. **lap312가 lap311 V4를 lap311 코드를 쓰지 않는 두 방법(원시 PE 바이트
census + cut 판정)으로 ACCEPT-WITH-STRENGTHENING**했고, lap313 work가 D1~D4를 새 probe에서 수리해
정적 PASS했다. runtime 예산 0, Stage B 0, 제품 증거 0, S1 종결 REJECT는 그대로다.
| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | 미완료 | S1/F2-R2 결정성, fresh pair, 실제 입력, WM_CLOSE |
| G2 | 미완료 | 활성8인 전비5000·풀/메모리·저장/지원동기화 증거 |
| G3 | 미완료 | 활성9~16번 실제 플레이/직렬화/지원 통신 |
| G4 | 미완료 | 원본 대비 반복 경로/전략 지표와 개선 |
## 다음 한 가지
**다음 한 가지: 다음 middle(Sol/Opus5/high)이 lap313 새 probe와 원본 SHA를 독립 검수한다.**
lap313은 `pre_gate`를 CFG 지배 관계로 계산하고, gate target/실패 arm 0 반환을 원시 바이트로 가드하며,
`EXPECTED_RUNTIME_WRITERS`를 제거했다. lap311 파일을 덮어쓰지 않았고 lap305~313 산출물과 원본은 SHA 불변이다.
게임/Wine/Xvfb/Stage B/runtime/PNG/클릭 실행은 계속 금지.
## 지금 막힌 것 (Blockers)

- S1/F2-R2 실제 결정성 미해결(S1 여섯 행은 정적 CONFIRMED지만 **fixture 타당성**일 뿐 — 두 run 값 동일성 미검증, Stage B/runtime
  pair는 상위 승인 전 금지). Stage B·원본 재실행·Wine/Xvfb·R6-A/R6-C 금지. production 클릭 금지(정상 비활성은 BLOCKED로 두고 후속
  입력은 계속). 원본/제품 EXE·DLL/assets/baseline/golden 변경, evidence 재사용, blind retry, PASS 완화 금지.
- **저장/불러오기 절대 좌표 — 정적으로 좁혀졌으나 미확정:** 중심식 `cdq; sub eax,edx; sar`을 화면·다이얼로그 양쪽에 적용해
  `ds:0xE5BF1C/20`과 sprite 320×310에서 origin을 만들고 `ds:0x1088B5C/5E`에 16-bit 고정 저장(읽는 시점은 클릭이 아니라 구성
  `0x4D6312`). **R6(lap304, lap306 재현):** `ds:0x4ED810` 참조 6개 전부 읽기(쓰기 0), 초기값 **3**, jump table `0x464B68`의
  `table[2]=0x464502` → **800×600** → lap301 후보 **A `(240,145)` 정적 우세**, B `(160,85)` 미선택. 미확정 이유: `0x4ED810`은
  쓰기 가능 `.data`라 계산 포인터/파일 로드를 실행 없이 못 배제하고, dialog 시점의 다른 writer 개입도 미확정이다.
- **map↔dialog 실제 event/thread 순서 UNKNOWN(lap308·lap310·lap312 모두 못 좁힘).** 정적 사실 유지: 앵커 일치, `0x431AB0`
  직접 caller `0x48F538` 1개, `0x4D60B0` caller `0x4D69E5/0x4D6A05`, map ret 2개, 640×480 reset writer 2개가 성공 return
  **지배**, 실패 경로 runtime writer **0개**. **lap310:** 전 섹션 절대 dword 스캔에서 두 진입점 리터럴 **0건** → 포인터
  테이블 경유 근거 없음(계산 포인터는 배제 불가).
- **R2 검수 결과(lap313 work, 1단 정적 PASS):** `.text` 절대 참조 111건과 직접 writer 4개는 유지되고,
  `pre_gate`는 CFG 지배 기반으로 `[]`, failure `[]`, success 4개다. gate `0x431AF2`=`75 0a` → `0x431AFE`,
  실패 arm 바이트는 `eax=0` 반환이다. D1~D4 수리의 독립 middle 검수와 제품 증거는 아직 0이다.
  **lap312 수치:** lap311 수치는 독립 재현됐다 — `.text` 절대 참조 111건
  = load 107 + **store 4**, store 4개 전부 map window 안, **moffs store 0**; gate `0x431AF2`=`75 0a` →
  taken `0x431AFE`, fall-through arm 바이트가 eax=0 반환; window 753, 실패 arm 정확히 7개이며 성공 ret 미도달
  (lap311의 746=753−7과 일치); cut 판정으로 reset writer 2개가 entry·join→성공 ret를 단절하고 **반증 대조군
  `0x431AFD`는 단절하지 않는다**. **강화 신규:** runtime writer 2개도 성공 경로 필수이고, reset은 `0x431B79`
  이후에도 필수이며, `0x4324C2` 이후 도달 명령 4개(`0x4324CC/D1/D2/D5`)에 화면 writer **0개** → 성공 반환 시
  **마지막 직접 쓰기는 640×480 reset**이다. **lap312의 D1~D4는 lap313 새 probe에서 수리됐고, D5**
  under-claim과 계산/간접 writer 및 실제 실행은 여전히 UNKNOWN이다. 기존 lap311의 D1 `pre_gate` 집합이 구조적으로 공허
  (네 writer 모두 gate 주소 위) → lap310의 "공허 게이트" 지적은 부분 수리, D2 "gate 이전"을 주소 순서로 근사해
  backward jump에 불건전, D3 anchor 가드가 taken target·반환값 미확인(fail-open), D4 `EXPECTED_RUNTIME_WRITERS`
  죽은 상수였음이 lap312에서 확인됐다. 또한 lap311 테스트는 검증 대상 함수를 import해 알고리즘 결함을 못 잡는다(드리프트는 잡음).
- **lap309 테스트 성격 표기(lap310, 수치 영향 0):** `test_lap309_mode_writer_probe.py::test_call_convention_cleanup_is_explicit`는
  상수표를 자기 자신과 대조하는 **동어반복**이라 `4`/`16`의 독립 증거가 아니다(실질 증거는 같은 파일 불변식 테스트와 lap310 solver). 규칙 완화 아님.
- **`0x465250` 의미 정정(lap310, 수치 영향 0):** lap305/306의 "가변인자 **로깅** 헬퍼"는 부정확하다. 실제로는
  `vsprintf`(`0x4DB933`, arg3=포맷) 후 import slot `0x4E51CC`=**`MessageBoxA`**(USER32 4인자 stdcall)를 부르는
  **메시지박스 헬퍼**다 → lap306 R4(291 push site가 기하 writer 미운반) 강화. lap305 근거 결함(line 104
  `raw + delta` 부호 오류, 수치 영향 0)과 산출물 SHA 보존은 유효하다.
- **화면 전역 writer 수 = 확인된 하한 20 (lap306 독립 재현):** 절대 4 + mode-table 16, `push 0xE5BF18`
  291개 전부 `0x465250`. computed pointer·virtual/indirect dispatch(특히 `0x465284`)·visible body 밖은
  fail-open. **moffs 종결(lap306 R5, lap312 재확인):** 화면 전역 대상 moffs 저장 **0건**.
- **provenance 회귀(전부 보존, 고쳐 쓰지 않음):** (a) lap301이 probe를 덮어써 수리 전 lap299 소스가 트리에
  없다(커밋 0) → lap299 report `8e735a9a…`는 재현 불가; lap301 report의 `"lap": 299` 오기도 그대로 둔다.
  (b) lap306 V2의 자칭 `lap 306`은 **실제 러너 lap 307**이다. lap308~310은 러너 로그와 `loop/.lap_counter`가 일치해
  드리프트는 lap308부터 **닫혔다**(`logs/loop-progress.result`의 `lap=`은 **직전 완료 lap**이라 1 차이가 정상).
  (c) `logs/lap306/lap306_v2_mode_writer_order.json`은 probe stdout이 아닌 **손 전사 요약**이라 SHA가 생성기 출력을
  고정하지 못한다(전사값은 독립 재유도와 일치, 수치 영향 0).
- comparator는 scene 4축과 선택 slot만 본다. nation/전체 slot id/절대 selection·camera/tick은 기계 검사 밖이라 (B) 원시 필드
  대조로만 확인하고 overall PASS도 충분조건이 아니다. `scene.owners`=owner0~7, offsets=owner0/1 → owner8~15 미가시(G3 위험).
- R17 구조 재결 미완료·R31 금지, R29 범위 승인 거부(lap266), R30 M11 생존 유지, R6-B-R2 count 1→0 판정 미결(규칙 변경 금지).
  lap274 추출기의 M-d/M-e 생존은 드리프트 사각. offline 8건 주차: H=F2-R1/F3-R1/F6-R2, C=R23/R24·stage_budget_state,
  N=R20/R21/R22. 삭제/PASS 전환 없음.
- **W2(lap296 §4.7.4):** `runtime_driver.py`는 아직 매직 리터럴을 읽는다 — (a) line 84 `0x8990C8`·line 89 `0x66B790`/`0x758` 승격 가능, (b) line 100 `0x8D`는 probe 가드 선행, (c) line 101 `0x8E`는 상수 부재·값 미재유도라 명명 **금지**.
- **W3(lap300 §4):** lap296 review probe의 `EXPECTED_SHA["target_probe"]`가 수리 전 SHA를 가리켜 **영구 exit1**, 회귀 게이트
  재사용 불가. 재pin은 자가 갱신이라 middle/work 단독 금지 — Astra/사용자 결정 대기. lap302~312 probe는 미래/자기 산출물 SHA를
  단언하지 않아 이 함정을 피한다. **가드 잔여 사각:** `type`/`owner` 가드는 값 드리프트를, lap301 `contains_all`은
  `add eax/ecx,0x18`을 구별 못 하고 lap303 앵커는 중심식 4쌍을 뺀다(lap304 R4). lap306 `callee_body` first-`ret` 절단도
  구조적 fail-open(수치 영향 0).
- 후보 WM_CLOSE teardown 결함, 실제 후보 scene/input evidence, G2~G4 증거 미해결. lap279/lap280/lap284-middle 세 probe는
  아직 `0x440FF0` 창을 써 legacy window 오분류 위험(lap289가 work probe만 `0x440F5B`로 좁힘). **lap292 사각:** 이름 결합
  단언이 reader 이름을 안 봐 폭 드리프트는 통과(수치 영향 0).
- **프로세스 사각:** 상수/앵커 승격 시 결합된 과거 probe 미재실행 → 잠복 결함 재발(lap294·lap296). **provenance:** lap287
  경고=lap290 부록, lap293 `ESCALATE_SOL`=lap294 부록 A, lap297 `ESCALATE_SOL`(`760a977e…4a8aa84c`)=lap298 부록 A,
  lap300/302/304/306/308/310/312 STATUS 원문=각 압축본.
- map-layer serializer **28쌍** 모델은 lap286이 재현해 ACCEPT(`1,400,702`+`30.5`). 한계: 네 fixture가 전부 정사각·짝수
  변이라 오프셋 210/212 배정과 halving layer `((w/2)*h)/2` 대 `(w*h)//4`를 구분 못 하고, owner `+0x8E` 상속·save/load 동일성 미검증.
- **G3 저장 포맷:** bulk `0x892410..0x975D8C`에 PlayerStruct 8개(`0x956770..0x973D50`)는 들어가지만 16개는 `0x991330`까지
  필요해 `0x1B5A4` B 넘친다 → 9~16번 직렬화 공간 없음. G1 범위에서 수리하지 않는다.
- **로드 경로 부재(lap284, lap298 재측정):** `tools/runtime_env.py`의 `save`/PS35 참조 **0**, PS 대기값 **{3,5,7,9}**,
  수정 대상 함수·기록 위치 미확정 → "연구 하네스" 행 **REJECT**. save000/save006 유지는 옳으나 lap284 §7 카드 4항 미산출이라
  잠정(공통 사실은 "owner id ≥8 record 0개").
- **실행 봉투 미성립(lap284 §5):** lap298이 (a)~(e)(1차 클릭·90초 상한·save 선택 절차·PS5 미도달 run 처리·wall-clock 예산)
  미제출 → 봉투 행 **REJECT** 유지. PS35→PS3 미도달 실패 모드(§6)는 evidence 스키마 부재로 "안전·회귀" 행 ACCEPT-WITH-CONDITION.
- **Plan C 함정(lap298 §10.3 봉인 유지):** 공유 temp의 800×600 `…_d1app2r3_21_load_screen.png`
  (`5e95ed92…d17e5879`)는 원본 로드 대화상자가 **아니다**(슬롯 문자열 출처는 Plan C
  `save_load_screen.cpp` `f2232e91…90ff41ec`) → 좌표 출처 금지. **주소 실재≠좌표 출처 적격**(lap302).
- **lap301~312 probe의 제품 한계:** 앵커·fixture pin·모드 테이블·호출 규약·CFG 지배는 정적 확인이나 구성 시점
  전역값은 실행 없이 미관측이고 버튼 hitbox·슬롯 선택·로드 전이는 UNKNOWN이다.
- **lap284 tick 순환 의존은 해소됐다(lap297 결정1 + lap298 ACCEPT).** 연구 쌍 tick은 report-only이고 제품 S1의
  (A)+(B)는 그대로다. **`(296,505)`:** 위치·라벨만 확정, **클릭 결과 미관측**, 슬롯 선택 UI·로드 후 전이 UNKNOWN.

## 검증 상태

**lap313 work (`4d3a01a8…066eef`, test `9ed8eec4…58aae2`, report `74976804…3ef9c3f`, exit0, fresh 2회
stdout byte-identical):** D1~D4 수리 R2 정적 PASS. 원본 SHA `b56986e0…c9c08a8ac`와 lap311 산출물 SHA 불변.
targeted **4 passed**, `make check` **307 passed**, Ruff/compileall/mypy/CONTEXT_PASS, safety **SAFETY_PASS**;
게임/Wine/Xvfb/Stage B/PNG/click 0. 다음 middle 독립 검수 필요, 제품 증거 0.
lap312 middle은 원시 PE census/cut 판정으로 lap311을 **ACCEPT-WITH-STRENGTHENING**했으며 수치는 history에 보존.
**lap311 work (`a33f216a…c9c08a8`, test `dc3ac0f2…b69f699`, report `efa4d84e…72c6dbc`, exit0, fresh 2회 byte-identical)**는 R2 실패 arm writer 집합 비교와 reverse post-dominator를 남겼고 `make check` 299 passed였다.
**lap310 middle (`cb4e6c51…869f5d933`)**은 lap309 V3 독립 ACCEPT, **lap309 work V3 (`76e68c22…980bc1ac2`)**는 R2/R3/R5 수리. 원문 기록 보존.
**lap300~308 (SHA·수치 원문은 `docs/history/laps/` 및 각 압축본):** lap308 middle V2 ACCEPT-WITH-CORRECTION,
lap306 work V2 정적 PASS·cross-function UNKNOWN, lap306 middle V1 ACCEPT-WITH-CORRECTION·하한 20, lap305 V1 291
stack paths, lap304 U1~U5 ACCEPT·R6 800×600, lap303 직접4+간접16=20·중심식, lap302 `.text`=`0x401000..0x4E4AE5`·
`.data` `0x4EC000..0x108BA38`, lap301 writer 4·후보 A/B PASS, lap300 결정성·280×24 bar.
lap296이 lap295 수리를 ACCEPT(mutant 6종, 80 B 복원 SHA). lap286 save 레이아웃은 경계 `0x440C20..0x440F5A`,
`1,400,702`·`30.5`, owner id ≥8 record 0개를 독립 재현했으나 카드 종결 REJECT. lap279~312 수치는
`docs/history/laps/`에 보존하며 게임 검증으로 승격하지 않는다. G1 제품 증거 0.

## 바퀴 기록

lap2~299 상세와 압축 원문은 `docs/history/laps/`(여섯 행 CONFIRMED·G3 저장 블로커·lap286 저장 레이아웃 재현·
lap290~296 결합 결함 수리 ACCEPT·lap297 Astra 세 결정·lap298 `(296,505)`와 Plan C 봉인·lap299 800×600
재유도). lap300 결정성 ACCEPT·**절대 좌표표 REJECT**·W3 신규, lap301 work T1/T2 수리, lap302 middle
T1/T2/T4 ACCEPT·**T3 REVISE 2건**, lap303 work U1~U5, lap304 middle 전부 ACCEPT·**`ds:0x4ED810`=3 →
800×600·후보 A 우세**, lap305 work V1 291건 전수, lap306 middle V1 ACCEPT-WITH-CORRECTION 후 work V2가
gate·reset·dialog reader 정적 확인, lap308 middle V2 ACCEPT-WITH-CORRECTION·결함 3건 handoff, lap309 work
V3 수리 PASS, lap310 middle이 PE 직접 파싱으로 R2·R3·R5 독립 재유도 ACCEPT, lap311 work가 새 CFG 방식으로
R2 저출력 수리. **lap312 middle은 원시 PE 바이트 census와 cut 판정(반증 대조군 포함)으로 lap311을
ACCEPT-WITH-STRENGTHENING — 성공 반환 시 마지막 직접 쓰기가 640×480 reset임을 신규 확정하고, lap311 결함
D1~D4를 다음 work로 handoff했다.** STATUS 원문은 `20260912_status_lap312_compaction.md`
(`ca9b8cb9…3257c48f`, 129줄)에 보존.
