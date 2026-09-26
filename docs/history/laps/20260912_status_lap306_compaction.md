# 보존: lap306 압축 이전 docs/STATUS.md 원문

- 원문 SHA256: 986bdc60f5089ec7cf3096e9c92d3539fa162f71a3b9998fe2a49718569a3466
- 원문 줄 수: 130
- 보존 시각: 2026-09-12 (lap306 middle)

---

# STATUS — 매 바퀴 갱신하는 기억
## 지금 상태
G1~G4 모두 제품 미완료. M1/G1 유지: 원본 800×600 구도와 입력을 유지한 1600×1200 출력. 제품 기준은
DESIGN, 사람 승인 원문은 feedback/APPROVALS·INBOX를 따르며 2026-09-12 01:03 bounded repair→fresh
validation 허가는 제품/출시 승인이 아니다. DxWrapper 출력/30초 렌더 근거는 있으나 실제 scene/input 쌍과
WM_CLOSE 결함이 남았다. lap275 F3-R2-R1 선언 범위 승인, lap270 R30 선언 범위 PASS와 R17 계약 종결 FAIL은
함께 유효하며 M11 생존을 지우지 않는다.

G1-S1 계약 계보(`…/G1_S1_MIDDLE_ACCEPTANCE_LAP277.md` §4.1~§4.7, 근거 lap276~296)는 **S1 fixture의 정적
타당성**일 뿐 두 run 값 동일성·제품 증거·Stage B 허가·마일스톤 종료가 아니다. runtime/load 계보
(`docs/work/active/G1_RUNTIME_CONTRACT_MIDDLE_LAP284.md` §11·§12): lap283 Astra → lap284 middle →
lap290~296 ACCEPT → lap297 Astra → lap298 타이틀 → lap299 work → lap300 middle(절대 좌표 REJECT) →
lap301 work → lap302 middle(T3 REVISE 2건) → lap303 work U1~U5 → **lap304 middle 독립 검수(U1~U5
ACCEPT, U3 정정, 모드 인자 출처 신규 확정)** → **lap305 work V1 ACCEPT(291 stack paths, 추가 writer 0)**. runtime 예산 0,
Stage B 0, 제품 증거 0, S1 종결 REJECT.
| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | 미완료 | S1/F2-R2 결정성, fresh pair, 실제 입력, WM_CLOSE |
| G2 | 미완료 | 활성8인 전비5000·풀/메모리·저장/지원동기화 증거 |
| G3 | 미완료 | 활성9~16번 실제 플레이/직렬화/지원 통신 |
| G4 | 미완료 | 원본 대비 반복 경로/전략 지표와 개선 |
## 다음 한 가지

**다음 한 가지: 다음 새 work(Luna/Sonnet5/high)가 V2를 새 파일에서 수행한다.** V1은 `push 0xE5BF18`
291개가 모두 `0x465250`으로 수렴하고 entry-relative `[arg+4]/[arg+8]` writer가 0이라 **20 하한 유지**.
V2=`FUN_00431AB0`의 `0x4324B8` 640×480 리셋·`0x431B79` 런타임 writer 실행 조건과 다이얼로그 구성
(`0x4D6312`) 대비 순서를 정적 유도한다. 이는 R6의 800×600을 뒤집을 수 있는 유일한 정적 경로다.
V3는 다음 별도 work에서 수행하며, 계속 게임/Wine/Xvfb/Stage B/runtime/PNG/클릭 실행과 기존 산출물 수정을 금지한다.

## 지금 막힌 것 (Blockers)

- S1/F2-R2 실제 결정성 미해결. Stage B·원본 재실행·Wine/Xvfb·R6-A/R6-C 금지. production 클릭 금지(정상
  비활성은 BLOCKED로 두고 후속 입력은 계속). 원본/제품 EXE·DLL/assets/baseline/golden 변경, evidence
  재사용, blind retry, PASS 완화 금지.
- **저장/불러오기 절대 좌표 — lap304가 정적으로 좁혔으나 미확정:** 중심식은 `cdq; sub eax,edx; sar`
  (0 방향 부호 나눗셈)을 화면·다이얼로그 양쪽에 적용해 `ds:0xE5BF1C/20`과 sprite 320×310에서 origin을
  만들고 `ds:0x1088B5C/5E`에 16-bit 고정 저장한다(읽는 시점은 클릭이 아니라 구성 `0x4D6312`).
  **lap304 R6:** `ds:0x4ED810`은 이미지 전체 참조 6개가 전부 읽기(쓰기 0), 초기값 **3** →
  `table[2]=0x464502` → **800×600**. `0x4644A0` 호출자 2개(`0x4643C0`/`0x464C64`)가 모두 이 전역에서
  모드를 받으므로 lap301 후보 **A `(240,145)` 정적 우세**, B `(160,85)`는 이 경로에서 선택 안 됨.
  미확정 이유: `0x4ED810`은 쓰기 가능 `.data`라 계산 포인터/파일 로드 변경을 실행 없이 못 배제하고,
  `0x4324B8`(640×480 고정)·`0x431B79`(런타임 값)가 이후 전역을 덮을 수 있다(→ V2).
- **화면 전역 writer 수: lap305 V1이 stack-argument 사각을 닫았다.** `push 0xE5BF18` **291개**가 모두
  `0x465250`으로 수렴하며 entry-relative arg1/arg2 접근·`+4/+8` writer·객체 forwarding이 0이다.
  따라서 lap304의 absolute 4 + mode-table 16 = **20 confirmed lower bound**는 유지된다. 다만 computed pointer,
  virtual/indirect dispatch와 V1 visible body 밖의 경로는 여전히 fail-open이며 제품 완료가 아니다.
- **provenance 회귀(lap302 §8, lap304 R7 재확인):** lap301이 probe를 덮어써 수리 전 lap299 소스가 트리에
  없다(커밋 0이라 복구 경로 없음) → lap299 report `8e735a9a…`는 재현 불가 과거 값. lap301 report는 아직
  `"lap": 299`로 자기 lap을 오기하며, lap304는 **고쳐 쓰지 않고 보존**했다. 수치 영향 0, 감사 추적 영향.
- comparator는 scene 4축과 선택 slot만 본다. nation/전체 slot id/절대 selection·camera/tick은 기계 검사
  밖이라 (B) 원시 필드 대조로만 확인하고 overall PASS도 충분조건이 아니다. `scene.owners`=owner0~7,
  offsets=owner0/1이라 owner8~15는 안 보인다(G3 위험).
- R17 구조 재결 미완료·R31 금지, R29 범위 승인 거부(lap266), R30 M11 생존 유지, R6-B-R2 count 1→0 응답
  판정 미결(규칙 변경 금지). lap274 추출기의 M-d/M-e 생존은 알려진 드리프트 사각. offline 8건 주차:
  H=F2-R1/F3-R1/F6-R2, C=R23/R24·stage_budget_state, N=R20/R21/R22. 삭제/PASS 전환 없음.
- **W2(lap296 §4.7.4):** `runtime_driver.py`는 아직 매직 리터럴을 읽는다 — (a) line 84 `0x8990C8`·line 89
  `0x66B790`/`0x758` 승격 가능, (b) line 100 `0x8D`는 probe 가드 선행, (c) line 101 `0x8E`는 상수 부재·값 미재유도라 명명 **금지**.
- **W3(lap300 §4):** lap296 review probe의 `EXPECTED_SHA["target_probe"]`가 수리 전 SHA를 가리켜
  **영구 exit1**, 회귀 게이트 재사용 불가. 재pin은 자가 갱신이라 middle/work 단독 금지 — Astra/사용자
  결정 대기. lap302~304 probe는 미래 산출물 SHA를 단언하지 않아 이 함정을 피한다(lap304 R7).
  **가드 잔여 사각:** `type`/`owner` 가드는 리터럴 소멸·개명만 잡고 **값 드리프트는 못 잡는다**.
  lap301 `contains_all`은 `add eax,0x18`(3회)·`add ecx,0x18`(2회)를 구별 못 하고, lap303 앵커는
  중심식 `cdq`/`sub eax,edx` 4쌍을 빼며(lap304 R4; 수치 영향 0), lap303 direct-writer 정규식은
  `a3` moffs 형태를 못 본다(이 이미지엔 없음) → V3.
- 후보 WM_CLOSE teardown 결함, 실제 후보 scene/input evidence, G2~G4 증거 미해결. lap279/lap280/
  lap284-middle 세 probe는 아직 `0x440FF0` 창을 써 legacy window 오분류 위험이 남는다(수치 영향 0;
  lap289가 work probe만 `0x440F5B`로 좁힘). **lap292 사각:** 이름 결합 단언이 reader 이름을 안 봐
  `x=i(G1_UNIT_X_OFFSET)`류 폭 드리프트는 통과(§4.5.4).
- **프로세스 사각:** 상수/앵커 승격 시 결합된 과거 probe를 재실행하지 않으면 잠복 결함이 재발한다
  (lap294·lap296). **provenance:** lap287 경고=lap290 부록, lap293 `ESCALATE_SOL`=lap294 부록 A, lap297
  `ESCALATE_SOL`(`760a977e…4a8aa84c`)=lap298 부록 A, lap300/302/304 STATUS 원문=각 압축본.
- S1 여섯 행은 정적 CONFIRMED지만 **fixture 타당성**일 뿐 — 두 run 값 동일성 미검증, Stage B/runtime pair는 상위 승인 전 금지.
- map-layer serializer **28쌍** 모델은 lap286이 재현해 ACCEPT(`1,400,702`+`30.5`). 한계: 네 fixture가
  전부 정사각·짝수 변이라 (a) 오프셋 210/212의 width/height 배정과 (b) halving layer `((w/2)*h)/2` 대
  `(w*h)//4` 구분 불가. owner `+0x8E` 상속·save/load 동일성 미검증.
- **G3 저장 포맷:** bulk `0x892410..0x975D8C`에 PlayerStruct 8개(`0x956770..0x973D50`)는 들어가지만 16개는
  `0x991330`까지 필요해 `0x1B5A4` B 넘친다 → 9~16번 직렬화 공간 없음. G1 범위에서 수리하지 않는다.
- **로드 경로 부재(lap284, lap298 재측정):** `tools/runtime_env.py`의 `save`/PS35 참조 **0**, PS 대기값
  **{3,5,7,9}**, 수정 대상 함수·기록 위치 미확정 → "연구 하네스" 행 **REJECT**.
- **실행 봉투 미성립(lap284 §5):** lap298이 (a) 1차 클릭만 줄였고 (b) 90초 상한 (c) save 선택 절차
  (d) PS5 미도달 run의 수집/flush/종료 (e) wall-clock 예산 미제출 → 봉투 행 **REJECT** 유지. PS35→PS3
  미도달 실패 모드(§6)는 evidence 스키마에 보존 형태가 없어 "안전·회귀" 행 ACCEPT-WITH-CONDITION.
- **fixture 확정 근거 부재:** save000/save006 유지는 옳으나 근거가 될 lap284 §7 카드 4항(nation/활성
  구성/절대 유닛 수)이 미산출. 공통 사실은 "owner id ≥8 record 0개"뿐이라 save000 선호는 잠정이다.
- **Plan C 함정(lap298 §10.3 봉인):** 공유 temp의 800×600 `…_d1app2r3_21_load_screen.png`
  (`5e95ed92…d17e5879`)는 원본 로드 대화상자가 **아니다**. 슬롯 문자열은
  `Syw2plus_re/plan_c/src/ui/save_load_screen.cpp`(`f2232e91…90ff41ec`)가 만든다 → 좌표 출처 금지.
  그 모듈의 `0x519A0C`/`0xB3AD74`/`0x1088B5C`가 `.data` virtual 안에 실재해도(lap302)
  **주소 실재≠좌표 출처 적격**이라 봉인은 그대로다.
- **lap301~304 probe의 제품 한계:** 앵커·fixture pin·모드 테이블은 정적으로 확인됐으나 구성 시점
  전역값은 실행 없이 관측되지 않고 버튼 hitbox·슬롯 선택·로드 전이는 UNKNOWN이다.
- **lap284 tick 순환 의존은 해소됐다(lap297 결정1 + lap298 ACCEPT).** 연구 쌍 tick은 report-only, 철회
  범위는 연구 쌍 입력 요구뿐이고 제품 S1의 (A)+(B)는 그대로다. **`(296,505)`:** 위치·라벨만 확정,
  **클릭 결과는 미관측**이며 슬롯 선택 UI·로드 후 전이는 UNKNOWN.

## 검증 상태

**lap305 work (`c151cc40…c943e57b21`/`b3a6e8bc…58c1ae36`, exit0, `failures=[]`):** V1 fresh objdump가
291/291 stack paths→`0x465250`, entry-relative arg1/arg2 접근 0, 추가 writer 0, lower bound 20을 확인했다.
두 report byte 동일. `make check` 292 passed, Ruff/compileall/mypy/CONTEXT, safety PASS, 게임/Wine/Xvfb 0.
**lap304 middle (`2047f839…218b1db2`/`d0ed2696…ae1d70b93`, exit0):** lap303 U1~U5 독립 재유도 ACCEPT,
U3 `cdq; sub; sar` 정정, R6 `ds:0x4ED810`=3 → 800×600 정적 신규 확정, 제품 증거 0.

**lap303 work (`257c0563…e1de7ae35`/`5079de5a…b869d540`, exit0, `failures=[]`):** U1 직접4+간접16=20 writer와
호출 사슬, U2 5해상도+동적 writer 후보, U3 중심식, U4 새 provenance, U5 no-future-SHA-pin; 두 fresh run
동일, 원본·lap299/lap301 SHA 불변. **lap302 middle (`b5343ec4…87ebd0a6`/`5190920f…8940d2`):** lap301 SHA
독립 확인, `sub ecx,0x1a`가 `0x4D6358`에 유일, `.text`=`0x401000..0x4E4AE5`, `.data` virtual
`0x4EC000..0x108BA38`. **lap301 work (`a6f682eb…a428c7a0`/`c312b42e…caaf10a`):** SHA pin·T1/T2·writer 4·후보
A/B geometry PASS(T3는 REVISE). **lap300 middle (`718b1e4e…17ea63cf`/`bcac0a41…764c67b2`):** 결정성·
`this+0x408`/stride16/count7/rect/버튼 재유도, 로더 문자열·280×24 bar, lap296 가드 fail-closed.

lap296이 lap295 수리를 ACCEPT(mutant 6종, 80 B 복원 SHA). lap286이 save 레이아웃을 독립 재현
(ACCEPT-WITH-CORRECTION): 경계 `0x440C20..0x440F5A`, fwrite 22/layer 28/helper 3/roster 1,
`1,400,702`·`30.5`, 네 fixture 모두 **owner id ≥8 record 0개**; 정정2로 `roster_records` 반증력은
**정수배 검사 4건**뿐이고 lap288은 경계 ACCEPT / 카드 종결 REJECT. lap284: fingerprint 9/9, 페이로드 50,
고정 22,978 B, map offset 70, 210/212. lap279~304 수치는 `docs/history/laps/`에 있고 게임 검증으로 승격하지
않는다. G1 제품 증거 0. 이전 STATUS 원문은 `…_status_lap276/284/288/290/294/296/298/300/302/304_compaction.md`에 보존.

## 바퀴 기록

lap2~276 상세와 압축 원문은 `docs/history/laps/`. lap277~283: 여섯 행 CONFIRMED, 유닛 오프셋 상수 3개
승격, G3 저장 블로커 발견 후 lap283 Astra가 runtime/G3 결정. lap284~289: runtime 예산 보류, 저장
레이아웃 인계·lap286 독립 재현·경계 수리. lap290~296: lap280 traceback을 상수 승격발 결합 결함으로
확정 → 수리 → 검수 → 가드 → **ACCEPT**. lap297: Astra 세 결정 승격. lap298: 타이틀 `(296,505)`,
Plan C 캡처 봉인. lap299: 800×600 정적 레이아웃 재유도. lap300: 결정성 ACCEPT, **절대 좌표표 REJECT**,
W3 신규, T1~T4 handoff. lap301: work T1/T2 수리. lap302: middle T1/T2/T4 ACCEPT, 중심식 정정,
**T3 REVISE 2건**. lap303: work U1~U5(writer 20·해상도 5·중심식·새 provenance). lap304: middle이 U1~U5를
독립 재유도해 **전부 ACCEPT**(U3 `cdq; sub; sar` 정정), writer 20을 닫힘 전수로 확정, **모드 인자
`ds:0x4ED810`=3 → 800×600·후보 A 정적 우세** 신규 확정, V1~V3 handoff. lap305: V1 stack path 291건
전수→`0x465250`, 추가 writer 0, **20 하한 유지**, 다음 V2.
