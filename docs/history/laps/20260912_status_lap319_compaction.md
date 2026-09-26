# lap320 진입 시 STATUS 원문 보존

원문 SHA256: `2b697659169af4bfa3e74e1e5c607d2acb50ac3a532754147558f081f388d3e3`
원문 줄 수: 127

```markdown
# STATUS — 매 바퀴 갱신하는 기억
## 지금 상태
G1~G4 모두 제품 미완료. M1/G1 유지: 원본 800×600 구도와 입력을 유지한 1600×1200 출력. 제품 기준은 DESIGN,
사람 승인 원문은 feedback/APPROVALS·INBOX를 따르며 2026-09-12 01:03 bounded repair→fresh validation 허가는
제품/출시 승인이 아니다. DxWrapper 출력/30초 렌더 근거는 있으나 실제 scene/input 쌍과 WM_CLOSE 결함이 남았다.
lap275 F3-R2-R1 선언 범위 승인, lap270 R30 선언 범위 PASS와 R17 계약 종결 FAIL은 함께 유효하며 M11 생존을
지우지 않는다. G1-S1 계약 계보(`…/G1_S1_MIDDLE_ACCEPTANCE_LAP277.md` §4.1~§4.7, 근거 lap276~296)는 **S1 fixture
정적 타당성**일 뿐 두 run 동일성·제품 증거·Stage B 허가·마일스톤 종료가 아니다. runtime/load 계보
(`docs/work/active/G1_RUNTIME_CONTRACT_MIDDLE_LAP284.md` §11·§12)는 lap283 Astra→lap316 middle까지
`docs/history/laps/`에 보존된다. **lap318 middle이 lap317 Astra의 F1 범위를 독립 검수해 ACCEPT-WITH-REVISION**했고
**lap319 work가 F1 수리를 PASS**했다. runtime 예산 0·Stage B 0·제품 증거 0·S1 종결 REJECT는 그대로다.
| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | 미완료 | S1/F2-R2 결정성, fresh pair, 실제 입력, WM_CLOSE |
| G2 | 미완료 | 활성8인 전비5000·풀/메모리·저장/지원동기화 증거 |
| G3 | 미완료 | 활성9~16번 실제 플레이/직렬화/지원 통신 |
| G4 | 미완료 | 원본 대비 반복 경로/전략 지표와 개선 |
## 다음 한 가지
**다음 한 가지: 다음 새 middle이 lap319 F1 work를 독립 검수한다** — 새 probe/test/report의 바이트·경계 재유도만 수행한다.
lap319는 reset store 두 곳을 **값=원본 PE, 경계=주소 델타**로 검증하고 정상 접힘·부정 fixture 5종을 통과시켰다.
runtime/Stage B/제품 증거 예산 0, 기존 pin·lap313~316·`tools/`·`patches/` 무변경.
## 지금 막힌 것 (Blockers)
- S1/F2-R2 실제 결정성 미해결(S1 여섯 행은 정적 CONFIRMED지만 **fixture 타당성**일 뿐 — 두 run 값 동일성 미검증, Stage B/runtime
  pair는 상위 승인 전 금지). Stage B·원본 재실행·Wine/Xvfb·R6-A/R6-C 금지. production 클릭 금지(정상 비활성은 BLOCKED로 두고 후속
  입력은 계속). 원본/제품 EXE·DLL/assets/baseline/golden 변경, evidence 재사용, blind retry, PASS 완화 금지.
- **저장/불러오기 절대 좌표 — 정적으로 좁혀졌으나 미확정:** 중심식 `cdq; sub eax,edx; sar`을 화면·다이얼로그 양쪽에 적용해
  `ds:0xE5BF1C/20`과 sprite 320×310에서 origin을 만들고 `ds:0x1088B5C/5E`에 16-bit 고정 저장(읽는 시점은 클릭이 아니라 구성
  `0x4D6312`). **R6(lap304, lap306 재현):** `ds:0x4ED810` 참조 6개 전부 읽기(쓰기 0), 초기값 **3**, jump table `0x464B68`의
  `table[2]=0x464502` → **800×600** → lap301 후보 **A `(240,145)` 정적 우세**, B `(160,85)` 미선택. 미확정 이유: `0x4ED810`은
  쓰기 가능 `.data`라 계산 포인터/파일 로드를 실행 없이 못 배제하고, dialog 시점의 다른 writer 개입도 미확정이다.
- **map↔dialog 실제 event/thread 순서 UNKNOWN(lap308~lap316 모두 못 좁힘).** 정적 사실 유지: 앵커 일치, `0x431AB0`
  직접 caller `0x48F538` 1개, `0x4D60B0` caller `0x4D69E5/0x4D6A05`, map ret 2개, 640×480 reset writer 2개가 성공 return
  **지배**, 실패 경로 runtime writer **0개**. **lap310:** 전 섹션 절대 dword 스캔에서 두 진입점 리터럴 **0건** → 포인터 테이블 경유 근거 없음(계산 포인터는 배제 불가).
- **R2 = 3회 독립 재유도(lap314·lap316 middle ACCEPT, lap318 세 번째 재확인). lap319 F1 수리 PASS이나 middle 독립 검수 전이다.**
  창/entry **753**, 실패 arm **7**(`0x431AF4..0x431AFD`, 성공 ret `0x4324D5` 미도달), 성공 arm **724**, unresolved **0**,
  화면 전역 census **4건 전부 직접 dword store** `{0x431B79, 0x431B7F, 0x4324B8(0x280), 0x4324C2(0x1E0)}`(moffs 0·
  실패 arm writer 0). gate `0x431AF2`=`750a` → taken `0x431AFE`, 실패 arm 연속 10B `5f5e5d33c05b83c434c3`(eax=0),
  성공 ret `c3`. D1 공허성은 writer 4개를 모두 제거해도 남는 **22-노드 증인 경로**로 재확인. 원문은 lap311~316 기록.
- **F1(lap319 work PASS):** objdump가 7바이트 초과 명령 바이트를 다음 줄로 접고 lap315 `INSN_RE`가
  그 연속줄을 버린다. 창 안 **27개**가 해당하며 `0x4324B8`·`0x4324C2`(10B reset writer) 포함. **lap318 신규 사실:** 접힌 27행의
  열 바이트는 전부 파일 바이트의 **정확한 접두사**(손상 0)이고 연속줄 27개는 전부 접힌 명령 **내부 주소**라 명령 행으로
  파싱되지 않는다(phantom 0) → 결함은 행 발명이 아니라 **무징후 절단**이다. 다중 명령 수집만 gap으로 FAIL하고 직접
  `by_address` 조회는 **fail-open**이므로, 수리의 필요조건은 **명령 단위 길이 불변식**이다. 현재 유일한 바이트 수집(실패 arm)은
  접힌 명령을 건드리지 않아 기존 수치는 그대로다. 새 probe는 두 reset의 PE 10B/주소 델타 10/재구성 열 10을 확인하고
  누락·무경계·gap·overlap·범위 밖을 FAIL로 닫았다(새 middle 독립 검수 대기).
- **UNKNOWN 유지(F1 범위 밖):** (N1) 지도 창 간접 분기 **0개**라 lap315 E1 수리는 실제 대상에서 **inert**이고 합성 fixture만
  이를 실행한다("간접 분기를 확인했다"로 승격 금지). (N2) 창 안 **call 31개**를 fall-through로 두어 callee 쓰기·cross-function
  순서·**D5** under-claim·계산/간접 writer·실제 실행 모두 UNKNOWN. (N3, lap318) 접힌 27행 중 `0x432497`·`0x4324A6`이
  `ds:0xB3AC88`=`0x33F`, `ds:0xB3AC8C`=`0x1FF`를 쓴다 — 화면 전역 아님, 의미 UNKNOWN.
- **lap312 강화 사실 유지:** 네 writer 전부 성공 경로 필수, reset은 `0x431B79` 이후에도 필수, `0x4324C2` 이후 도달 명령
  4개에 화면 writer **0개** → 성공 반환 시 **마지막 직접 쓰기는 640×480 reset**. **테스트 품질:** lap313 backward-jump,
  lap316 witness-path/BFS/indirect-jump, lap318 접힘·gap·overlap·범위밖 fixture는 손으로 답을 유도할 수 있는 **진짜
  알고리즘 테스트**다(바이너리 사실 테스트는 드리프트만 잡는다).
- **표기 정정 2건(lap310, 수치 영향 0, 규칙 완화 아님):** (i) `test_lap309_mode_writer_probe.py::test_call_convention_cleanup_is_explicit`는
  상수표 **동어반복**이라 `4`/`16`의 독립 증거가 아니다(실질 증거는 같은 파일 불변식 테스트와 lap310 solver). (ii) `0x465250`은
  `vsprintf`(`0x4DB933`) 후 import slot `0x4E51CC`=**`MessageBoxA`**를 부르는 **메시지박스 헬퍼**다(로깅 헬퍼 아님) → lap306 R4
  강화. lap305 근거 결함(line 104 `raw + delta` 부호 오류)과 산출물 SHA 보존은 유효하다.
- **화면 전역 writer 수 = 확인된 하한 20 (lap306 독립 재현):** 절대 4 + mode-table 16, `push 0xE5BF18` 291개 전부
  `0x465250`. computed pointer·virtual/indirect dispatch(특히 `0x465284`)·visible body 밖은 fail-open.
  **moffs 종결(lap306 R5, lap312·lap316 재확인):** 화면 전역 대상 moffs 저장 **0건**.
- **provenance 회귀(전부 보존, 고쳐 쓰지 않음):** (a) lap301이 probe를 덮어써 수리 전 lap299 소스가 트리에
  없다(커밋 0) → lap299 report `8e735a9a…`는 재현 불가; lap301 report의 `"lap": 299` 오기도 그대로 둔다.
  (b) lap306 V2의 자칭 `lap 306`은 **실제 러너 lap 307**이고 lap308~318은 러너 로그와 `loop/.lap_counter`가 일치해 드리프트는
  lap308부터 **닫혔다**(`logs/loop-progress.result`의 `lap=`은 **직전 완료 lap**이라 1 차이가 정상). (c)
  `logs/lap306/lap306_v2_mode_writer_order.json`은 probe stdout이 아닌 **손 전사 요약**이라 SHA가 생성기 출력을 고정하지
  못한다(전사값은 독립 재유도와 일치). (d) **lap314 정정:** 이전 STATUS/lap312 압축본의 lap311 probe 약칭
  `a33f216a…c9c08a8`은 **꼬리가 틀렸다**(원본 EXE SHA 꼬리). 실제 `a33f216a…8fd4524`, 정본은
  `20260912_lap311_work_v4_mode_writer_order.md`. 과거 압축본은 고치지 않는다.
- comparator는 scene 4축과 선택 slot만 본다. nation/전체 slot id/절대 selection·camera/tick은 기계 검사 밖이라 (B) 원시 필드
  대조로만 확인하고 overall PASS도 충분조건이 아니다. `scene.owners`=owner0~7, offsets=owner0/1 → owner8~15 미가시(G3 위험).
- R17 구조 재결 미완료·R31 금지, R29 범위 승인 거부(lap266), R30 M11 생존 유지, R6-B-R2 count 1→0 판정 미결(규칙 변경 금지).
  lap274 추출기의 M-d/M-e 생존은 드리프트 사각. offline 8건 주차: H=F2-R1/F3-R1/F6-R2, C=R23/R24·stage_budget_state, N=R20/R21/R22. 삭제/PASS 전환 없음.
- **W2(lap296 §4.7.4):** `runtime_driver.py`는 아직 매직 리터럴을 읽는다 — (a) line 84 `0x8990C8`·line 89 `0x66B790`/`0x758` 승격 가능, (b) line 100 `0x8D`는 probe 가드 선행, (c) line 101 `0x8E`는 상수 부재·값 미재유도라 명명 **금지**.
- **W3(lap300 §4):** lap296 review probe의 `EXPECTED_SHA["target_probe"]`가 수리 전 SHA를 가리켜 **영구 exit1**, 회귀 게이트
  재사용 불가. 재pin은 자가 갱신이라 middle/work 단독 금지 — Astra/사용자 결정 대기. lap302~318 probe는 미래/자기 산출물 SHA를
  단언하지 않아 이 함정을 피한다. **가드 잔여 사각:** `type`/`owner` 가드는 값 드리프트를, lap301 `contains_all`은
  `add eax/ecx,0x18`을 구별 못 하고 lap303 앵커는 중심식 4쌍을 뺀다(lap304 R4). lap306 `callee_body` first-`ret` 절단도 구조적 fail-open(수치 영향 0).
- 후보 WM_CLOSE teardown 결함, 실제 후보 scene/input evidence, G2~G4 증거 미해결. lap279/lap280/lap284-middle 세 probe는 아직
  `0x440FF0` 창을 써 legacy window 오분류 위험(lap289가 work probe만 `0x440F5B`로 좁힘). **lap292 사각:** 이름 결합 단언이 reader 이름을 안 봐 폭 드리프트 통과.
- **프로세스 사각:** 상수/앵커 승격 시 결합된 과거 probe 미재실행 → 잠복 결함 재발(lap294·lap296). **provenance:** lap287
  경고=lap290 부록, lap293 `ESCALATE_SOL`=lap294 부록 A, lap297 `ESCALATE_SOL`(`760a977e…4a8aa84c`)=lap298 부록 A,
  lap317 `ESCALATE_SOL`(`37cb58d7…a3a7e6e4`)=lap318 부록 A(소비), lap300~317 STATUS 원문=각 압축본.
- map-layer serializer **28쌍** 모델은 lap286이 재현해 ACCEPT(`1,400,702`+`30.5`). 한계: 네 fixture가 전부 정사각·짝수 변이라 오프셋 210/212 배정과 halving layer `((w/2)*h)/2` 대 `(w*h)//4`를 구분 못 하고, owner `+0x8E` 상속·save/load 동일성 미검증.
- **G3 저장 포맷:** bulk `0x892410..0x975D8C`에 PlayerStruct 8개(`0x956770..0x973D50`)는 들어가지만 16개는 `0x991330`까지
  필요해 `0x1B5A4` B 넘친다 → 9~16번 직렬화 공간 없음. G1 범위에서 수리하지 않는다.
- **로드 경로 부재(lap284, lap298 재측정):** `tools/runtime_env.py`의 `save`/PS35 참조 **0**, PS 대기값 **{3,5,7,9}**, 수정 대상 함수·기록 위치 미확정 → "연구 하네스" 행 **REJECT**. save000/save006 유지는 옳으나 lap284 §7 카드 4항 미산출이라 잠정(공통 사실은 "owner id ≥8 record 0개").
- **실행 봉투 미성립(lap284 §5):** lap298이 (a)~(e)(1차 클릭·90초 상한·save 선택 절차·PS5 미도달 run 처리·wall-clock 예산)
  미제출 → 봉투 행 **REJECT** 유지. PS35→PS3 미도달 실패 모드(§6)는 evidence 스키마 부재로 "안전·회귀" 행 ACCEPT-WITH-CONDITION.
- **Plan C 함정(lap298 §10.3 봉인 유지):** 공유 temp의 800×600 `…_d1app2r3_21_load_screen.png`
  (`5e95ed92…d17e5879`)는 원본 로드 대화상자가 **아니다**(슬롯 문자열 출처는 Plan C
  `save_load_screen.cpp` `f2232e91…90ff41ec`) → 좌표 출처 금지. **주소 실재≠좌표 출처 적격**(lap302).
- **lap301~318 probe의 제품 한계:** 앵커·fixture pin·모드 테이블·호출 규약·CFG 지배는 정적 확인이나 구성 시점 전역값은
  실행 없이 미관측이고 버튼 hitbox·슬롯 선택·로드 전이는 UNKNOWN. call을 fall-through로 취급해 callee 쓰기와 cross-function 순서를 증명하지 못한다.
- **lap284 tick 순환 의존은 해소됐다(lap297 결정1 + lap298 ACCEPT).** 연구 쌍 tick은 report-only이고 제품 S1의
  (A)+(B)는 그대로다. **`(296,505)`:** 위치·라벨만 확정, **클릭 결과 미관측**, 슬롯 선택 UI·로드 후 전이 UNKNOWN.
## 검증 상태

**lap319 work (probe `eeed0913…1671e6d3`, test `4a246d15…2248522b`, report `09e012dc…f4161def`, exit0, 연속 2회
stdout 동일·저장 report와 일치):** F1 수리 **PASS** — 두 reset PE 값/주소 델타/재구성 열 모두 10B, window/entry/failure/success
753/753/7/724, unresolved 0, writer 4/0, gate·실패 arm 유지. targeted **8 passed**, `make check` **350 passed**,
Ruff/compileall/mypy/CONTEXT_PASS, safety **SAFETY_PASS**, 원본 SHA `b56986e0…c9c08a8ac` 불변. 게임/Wine/Xvfb/Stage B/PNG/click 0.
최종 기술 컨펌과 제품 증거는 없다.

lap317 Astra: lap316 fresh report 동일·failures=[]; Fast 328 passed·lint/type/context/safety PASS. 계획은 lap318이 수용.
**lap316 middle (`6bc0923a…6aedcb80`, report `c91a238b…141f3af5`)**: lap315 ACCEPT-WITH-NOTES, 328 passed. **lap315 work
(`839372aa…e19784c6`, report `ac0e1b7e…fc2bfa31`)**: 새 probe 정적 PASS, 319 passed.
**lap314 middle (`44a115e6…a7b75e49`)**: lap313 ACCEPT-WITH-CORRECTION, 원본 SHA 불변, 313 passed. **lap313 work
(`4d3a01a8…066eef`)**: D2/D3/D4만 확인, D1 PARTIAL. **lap311 work (`a33f216a…8fd4524`)**: 299 passed, lap312가
ACCEPT-WITH-STRENGTHENING. **lap310 middle (`cb4e6c51…869f5d933`)**은 lap309 V3 독립 ACCEPT.
**lap286~308 (SHA·수치 원문은 `docs/history/laps/` 및 각 압축본):** lap308 V2 ACCEPT-WITH-CORRECTION, lap306 work V2
정적 PASS·cross-function UNKNOWN, lap306 middle V1 하한 20, lap305 V1 291 stack paths, lap304 U1~U5 ACCEPT·R6
800×600, lap303 직접4+간접16=20·중심식, lap302 `.text`=`0x401000..0x4E4AE5`·`.data` `0x4EC000..0x108BA38`, lap301
writer 4·후보 A/B PASS, lap300 결정성·280×24 bar, lap296이 lap295 수리 ACCEPT(mutant 6종), lap286 save 레이아웃
(`0x440C20..0x440F5A`, `1,400,702`·`30.5`, owner id ≥8 record 0개) 독립 재현했으나 카드 종결 REJECT.
lap279~319 수치는 게임 검증으로 승격하지 않는다. G1 제품 증거 0.

## 바퀴 기록

lap2~299 상세와 압축 원문은 `docs/history/laps/`(여섯 행 CONFIRMED·G3 저장 블로커·lap286 저장 레이아웃 재현·lap290~296 결합 결함 수리 ACCEPT·lap297 Astra 세 결정·lap298 `(296,505)`와 Plan C 봉인·lap299 800×600 재유도).
lap300 결정성 ACCEPT·**절대 좌표표 REJECT**·W3 신규, lap301 T1/T2 수리, lap302 T1/T2/T4 ACCEPT·**T3 REVISE 2건**,
lap303 U1~U5, lap304 전부 ACCEPT·**`ds:0x4ED810`=3 → 800×600·후보 A 우세**, lap305 291건 전수, lap306 V1→V2 gate·
reset·dialog reader 정적 확인, lap308 V2 ACCEPT-WITH-CORRECTION·결함 3건, lap309 V3 수리 PASS, lap310 PE 직접 파싱
재유도 ACCEPT, lap311 새 CFG로 R2 저출력 수리, lap312 원시 PE census·cut으로 ACCEPT-WITH-STRENGTHENING·D1~D5
handoff, lap313 D1~D4 정적 PASS, lap314 node-cut ACCEPT-WITH-CORRECTION, lap315 D1 잔여·E1·E2 수리, lap316 세 번째
독립 방법 ACCEPT-WITH-NOTES·N1/F1/N2, lap317 Astra가 F1 한정 범위·검증 해석을 상위 기록.
**lap318 middle이 그 범위를 독립 검수해 ACCEPT-WITH-REVISION하고, lap319 work가 범위·부정 fixture 5종을 구현했다.**
직전 STATUS는 `20260912_status_lap317_compaction.md`에 SHA/130줄 원문 보존.
```
