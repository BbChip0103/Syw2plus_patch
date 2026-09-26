# lap325 STATUS 원문 보존 (lap326 압축 전)

보존 시점: 2026-09-12 / lap326 middle.
원문 경로: `docs/STATUS.md`
원문 SHA256: `0c64d66207bf2ea4d10232fb403ee3c0c5804e521cdd1a5284789353b46988c1`
원문 줄 수: 126

아래는 압축 전 전체 원문이다. 미결/반려/provenance를 삭제하지 않고 그대로 보존한다.

```markdown
# STATUS — 매 바퀴 갱신하는 기억
## 지금 상태
G1~G4 모두 제품 미완료. M1/G1 유지: 원본 800×600 구도와 입력을 유지한 1600×1200 출력. 제품 기준은 DESIGN, 사람 승인
원문은 feedback/APPROVALS·INBOX를 따르며 2026-09-12 01:03 bounded repair→fresh validation 허가는 제품/출시 승인이
아니다. DxWrapper 출력 근거는 있으나 실제 scene/input 쌍과 WM_CLOSE 결함이 남았다.
lap275 F3-R2-R1 선언 범위 승인, lap270 R30 PASS와 R17 계약 종결 FAIL은 함께 유효하며 M11 생존을 지우지 않는다.
G1-S1 계약 계보(`…/G1_S1_MIDDLE_ACCEPTANCE_LAP277.md` §4.1~§4.7)는 **S1 fixture 정적 타당성**일 뿐 두 run 동일성·제품
증거·Stage B 허가·마일스톤 종료가 아니다. runtime/load 계보(`…/G1_RUNTIME_CONTRACT_MIDDLE_LAP284.md` §11~§14)는
lap283→lap324까지 `docs/history/laps/`에 보존된다. lap318→lap320 ACCEPT로 F1 종결, lap322가 §13 여섯 행을 §14로 판정
(fixture·§5(c)·하네스 경계·§5(b)(e) REJECT, §5(a) 부분, §5(d)/§6 조건부, 패키지 REJECT), lap323 Astra가 §14.7 봉투
REJECT, **lap325 Astra가 R1 연구 범위를 조건부 허용, 도달·표본 기준은 middle로 반환**. runtime 예산 0·Stage B 0·제품 증거 0·
S1 종결 REJECT는 그대로다.
| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | 미완료 | S1/F2-R2 결정성, fresh pair, 실제 입력, WM_CLOSE |
| G2 | 미완료 | 활성8인 전비5000·풀/메모리·저장/지원동기화 증거 |
| G3 | 미완료 | 활성9~16번 실제 플레이/직렬화/지원 통신 |
| G4 | 미완료 | 원본 대비 반복 경로/전략 지표와 개선 |
## 다음 한 가지
**새 middle(Sol 승격 요청)이 lap325 R1 봉투의 도달·표본 일관성 기준을 검증하고 수용/반려한다.**
`docs/work/active/G1_R1_SCOPE_DIRECTION_LAP325.md`가 세 변경의 조건부 상한을 확정했다.
즉시 실행 예산 0·work 카드 0. 봉투 수용→work 구현/검사→새 middle 실행 전 검수 후에만 1회 실행 가능.
## 지금 막힌 것 (Blockers)
- **R1(lap325):** runtime 1 run≤90초·연구 하네스·클릭 1회는 상위 조건부 허용. 즉시 발효 아님.
  lap324의 '구성 확인' 판정식과 별도 x/y store의 표본 일관성은 미정 → ESCALATE_SOL.
  Stage B·쌍·PNG 비교·W3 재pin·baseline/golden·INT3 금지 유지. 기존 원문은 lap324 압축본 보존.
- **exact-site 계측 불가(lap324 확정):** 읽기 수단은 `process_vm_readv` 폴링뿐이고 `process_vm_writev`/`ptrace`/
  `PTRACE`/`int3`/`0xCC`/`winedbg`/`gdb` **0회**. 따라서 "0x4D6312가 읽는 순간"은 증명 수단이 없고, 만들면 그것이
  하네스 수정 위반이다 → §14.7 제출 형태는 자기모순. 대신 R1은 관측 대상을 산출물로 바꾼다.
- **도달은 입력 0과 충돌(lap324):** 하네스 대기 가능 상태는 형태 무관 AST로 `ps ∈ {3,4,5,6,7,9}`뿐, `35` 리터럴 0,
  `save` 토큰 0, `0x1088B5C/5E` 참조 0. PS9(타이틀)는 입력 0으로 도달하지만 다이얼로그가 아니고 `FUN_004D60B0`
  직접 caller는 `0x4D69E5`/`0x4D6A05` 2개뿐이라 구성은 최소 1클릭을 요구한다. 타이틀 시점 값 대체는 금지 유지.
- **저장/불러오기 절대 좌표 — 관측 대상만 좁혀졌고 값은 미확정.** 중심식 `cdq; sub eax,edx; sar`이
  `ds:0xE5BF1C/20`과 sprite 크기로 origin을 만들어 `ds:0x1088B5C/5E`에 16-bit 저장(계산 시점 `0x4D6312`).
  **lap324 신규:** `.text`(0x401000–0x4E4AE5) 절대 operand 전수 스캔 — `0x1088B5C` 출현 10 중 **직접 store 1**
  (`0x4D632A`), `0x1088B5E` 출현 11 중 **직접 store 1**(`0x4D6348`), 나머지는 전부 `movsx` 읽기, 미분류 0.
  직접 writer가 각각 하나라 폴링 1회로 A/B를 가릴 수 있다. **잔여 fail-open:** 계산/간접 writer는 배제 불가(N2 계열).
  **lap322 §14.3:** `yfnt/saveloadtitle.spr` 102,260 B `7d154cdb…c08a5c5` 헤더 `[9,320,310,1]`에 같은 식을 대입하면
  **A(240,145)**(800×600)와 **B(160,85)**(640×480) — A/B는 두 가설이 아니라 하나의 식을 두 전역값에 대입한 결과다.
  **R6:** `ds:0x4ED810` 참조 6개 전부 읽기, 초기값 **3**, `table[2]=0x464502` → 800×600 → A 정적 우세(쓰기 가능
  `.data`라 계산 포인터/파일 로드 미배제). **정적 지렛대 소진(lap322)** 판정은 유지한다.
- **map↔dialog 실제 event/thread 순서 UNKNOWN(lap308~316·lap322).** 정적 사실: 앵커 일치, `0x431AB0` 직접 caller
  `0x48F538` 1개, `0x4D60B0` caller 2개, 640×480 reset writer 2개가 성공 return **지배**, 실패 경로 runtime writer
  **0개**, lap310 절대 dword 스캔 리터럴 **0건**(계산 포인터는 배제 불가).
- **R2 = 4회 독립 재유도(lap314·316·318·320) + lap324 재확인.** 창/entry **753**, 실패 arm **7**, 성공 arm **724**,
  unresolved **0**, 화면 전역 직접 store **4건** `{0x431B79,0x431B7F,0x4324B8(0x280),0x4324C2(0x1E0)}`(moffs 0·실패 arm
  writer 0), gate `0x431AF2`=`750a`→`0x431AFE`. D1 공허성은 22-노드 증인 경로로 재확인. 원문은 lap314~320 기록.
- **F1 = 종결(lap319 수리 → lap320 ACCEPT).** 결함은 objdump 접힘의 무징후 절단, 수리는 명령 단위 길이 불변식.
  접힘 27 전부 절단·초과 0, 두 reset이 파일·델타·열 세 출처 일치. 원문은 lap319/lap320 기록과 압축본.
- **N4·N5·N6·표기 정정(수치 영향 0, 완화 아님, 원문은 lap320·lap322 기록):** (N4) lap319 `main()`의 `checks` 선평가가
  reset 행 부재 시 KeyError로 FAIL JSON을 못 남긴다. (N5) 남은 직접 행 조회는 gate 2B 교차검증으로 닫힘. (N6) lap284
  probe의 `ps_states_waited`·`ps35_references` 정규식이 집합 소속 형태에 **fail-open**(실제 비교 집합 `{3,4,5,6,7,9}`);
  결론 "PS35 참조 0"은 형태 무관 스캔으로 재성립하고 lap324가 독립 재유도했다. `_g1_flush_input_stage`는 호출 9곳의
  **레코드 단위**라 필요한 것은 새 필드지 새 주기가 아니다. 예산 기구 `G1_INPUT_STAGE_BUDGETS`·4값 `stage_budget_state`·
  `G1_INPUT_MAX_TRUNCATION_RATIO=0.25`는 이미 있고 `runtime_env.py:2202-2205`가 그 25%를 스스로 "측정이 아닌 가정"이라
  선언한다. §5(b) 3 MB 로드 소요 측정치는 **0**, 과거 8.4~19.1초는 **새 게임** run이라 대체 금지. lap322는 lap319/320
  probe를 실행 게이트로 채택하지 않아 N4를 선행 조건으로 지정하지 않았다(§14.8). **lap324 단서:** R1 evidence 스키마가
  그 `main()` 형태를 재사용하면 발동한다.
- **UNKNOWN 유지(F1 범위 밖):** (N1) 지도 창 간접 분기 0개라 lap315 E1 수리는 실제 대상에서 inert(합성 fixture만
  실행). (N2) 창 안 call 31개 fall-through → callee 쓰기·cross-function 순서·D5 under-claim·계산/간접 writer·실제
  실행 모두 UNKNOWN. (N3) 접힌 행의 `ds:0xB3AC88`=`0x33F`/`0xB3AC8C`=`0x1FF`는 화면 전역 아님, 의미 UNKNOWN.
- **lap312 강화 사실 유지:** 네 writer 전부 성공 경로 필수, `0x4324C2` 이후 도달 명령 4개에 화면 writer **0개** →
  성공 반환 시 마지막 직접 쓰기는 640×480 reset. **화면 전역 writer 하한 20(lap306):** 절대 4 + mode-table 16,
  `push 0xE5BF18` 291개 전부 `0x465250`(lap310 정정); computed/indirect는 fail-open, 화면 전역 moffs 저장 0건.
  lap310 정정(ii): `test_call_convention_cleanup_is_explicit`는 상수표 동어반복이라 `4`/`16`의 독립 증거가 아니다.
- **provenance 회귀(전부 보존, 고쳐 쓰지 않음):** (a) lap301이 probe를 덮어써 lap299 report `8e735a9a…`는 재현 불가,
  lap301의 `"lap": 299` 오기도 그대로 둔다. (b) lap306 V2의 자칭 `lap 306`은 실제 러너 lap 307, 드리프트는 lap308부터
  닫혔다. (c) `lap306_v2_mode_writer_order.json`은 손 전사 요약이라 SHA가 생성기 출력을 고정하지 못한다.
  (d) lap311 probe 약칭은 `a33f216a…8fd4524`가 실제. (e) lap322 §14 서두 `bcf4…`는 계약 추가 전 보고서, 최종은
  `7d04b9b2…35757ac`(lap323). (f) "테스트 수 불변 ⇒ 소스 무변경"은 증거가 아니다 → lap324부터 해시 장부.
- comparator는 scene 4축과 선택 slot만 본다. nation/slot id/절대 selection·camera/tick은 기계 검사 밖이라 (B) 원시 필드
  대조로만 확인하고 overall PASS도 충분조건이 아니다. `scene.owners`=owner0~7 → owner8~15 미가시(G3 위험).
  R17 구조 재결 미완료·R31 금지, R29 범위 승인 거부(lap266), R30 M11 생존, R6-B-R2 count 1→0 미결(규칙 변경 금지).
  lap274 추출기 M-d/M-e 생존은 드리프트 사각. offline 8건 주차: H=F2-R1/F3-R1/F6-R2, C=R23/R24·stage_budget_state,
  N=R20/R21/R22. 삭제/PASS 전환 없음. **W2(lap296 §4.7.4):** `runtime_driver.py` 매직 리터럴 — (a) `0x8990C8`·
  `0x66B790`/`0x758` 승격 가능, (b) `0x8D`는 probe 가드 선행, (c) `0x8E`는 상수 부재·값 미재유도라 명명 **금지**.
- **W3(lap300 §4):** lap296 review probe의 `EXPECTED_SHA["target_probe"]`가 수리 전 SHA를 가리켜 영구 exit1, 회귀 게이트
  재사용 불가. 재pin은 자가 갱신이라 middle/work 단독 금지 — Astra/사용자 결정 대기. lap302~324 probe는 자기 산출물 SHA를
  단언하지 않아 이 함정을 피한다. **가드 잔여 사각:** `type`/`owner` 가드는 값 드리프트를, lap301 `contains_all`은
  `add eax/ecx,0x18`을 구별 못 하고 lap303 앵커는 중심식 4쌍을 뺀다. lap306 `callee_body` 절단과 N6도 같은 종류다.
- 후보 WM_CLOSE teardown 결함, 실제 후보 scene/input evidence, G2~G4 증거 미해결. lap279/lap280/lap284-middle 세 probe는
  아직 `0x440FF0` 창을 써 legacy window 오분류 위험. **lap292 사각:** 이름 결합 단언이 reader 이름을 안 봐 폭 드리프트 통과.
- **프로세스 사각:** 상수/앵커 승격 시 결합된 과거 probe 미재실행 → 잠복 결함 재발(lap294·lap296). **provenance:** lap287
  경고=lap290 부록, lap293/lap297/lap317 `ESCALATE_SOL`=각 lap294/298/318 부록 A, lap321=lap322 부록 A,
  lap323(`a1026fce…56217008`)=lap324 부록 A(소비). lap300~323 STATUS 원문=각 압축본.
- map-layer serializer **28쌍** 모델은 lap286이 재현해 ACCEPT(`1,400,702`+`30.5`). 한계: 네 fixture가 전부 정사각·짝수
  변이라 오프셋 210/212 배정과 halving layer를 구분 못 한다 → lap322 §14.1이 fixture 행을 REJECT한 직접 이유.
  owner `+0x8E` 상속·save/load 동일성도 미검증. save000(`1c703551…`)/save006(`616b7997…`) 유지는 옳으나 §7 카드 4항
  미산출이라 잠정("owner id ≥8 record 0개"만 공통).
- **G3 저장 포맷:** bulk `0x892410..0x975D8C`에 PlayerStruct 8개는 들어가지만 16개는 `0x1B5A4` B 넘친다 → 9~16번 직렬화
  공간 없음. G1 범위에서 수리하지 않는다.
- **실행 봉투 미성립(lap284 §5 → lap322 §14.5·§14.6 → lap324):** (a)~(e) 미제출로 봉투 행 REJECT 유지. §6은 기구 충분·
  필드 선언 미완이라 ACCEPT-WITH-CONDITION — 네 실패 모드(도달 실패/전역 미변화/timeout/수집 실패)에 원시 PS·tick·경과·
  run ID·소유 PID·입력·오류·flush 경로·종료 방식을 실행 전 선언한다. lap324 제안 배분(준비40/클릭20/관측15/종료15초, 합
  90초 이내)은 전부 **가정**이며 첫 run이 실측해 재평가한다. 자동 연장·blind 재시도 금지.
- **Plan C 함정(lap298 §10.3 봉인 유지):** 공유 temp 800×600 `…_21_load_screen.png`(`5e95ed92…d17e5879`)는 원본 로드
  대화상자가 **아니다**(출처는 Plan C `save_load_screen.cpp`) → 좌표 출처 금지. **주소 실재≠좌표 출처 적격.**
- **lap301~324 probe의 제품 한계:** 앵커·pin·모드 테이블·CFG 지배는 정적 확인이나 **구성 시점 전역값은 실행 없이 미관측**,
  hitbox·슬롯 선택·로드 전이는 UNKNOWN, call fall-through로 cross-function 순서 미증명. tick 순환 의존은 해소
  (lap297 결정1+lap298): 연구 쌍 tick은 report-only, 제품 S1 (A)+(B) 불변. **`(296,505)`:** 위치·라벨만 확정,
  **클릭 결과 미관측**, 하네스에 0회 등장(문서 전용). R1이 허가되면 이 클릭이 첫 실관측이 된다.
## 검증 상태
**lap325 Astra:** lap324 probe 1회 재현, failures=[], SHA `c00eed09…59fbb1e21cf` 동일.
새 독립 알고리즘/실행 증거 아님. make check 361 passed·Ruff/compileall/mypy/CONTEXT_PASS, SAFETY_PASS.
보호 트리 127파일 pre/post SHA 동일·원본 SHA 불변. STATUS 126줄/Blockers 1개, 게임 코드/실행 0.
**lap324 middle:** 제출 봉투 BLOCKED, R1 상위 반환. 당시 make check 361 passed·SAFETY_PASS,
보호 90파일 SHA 불변. 이번 실행 결과로 승격하지 않는다. 상세/해시는 lap324 기록과 압축본.

**lap323 Astra:** §14.7 봉투 REJECT(새 격리 시작·입력 없는 exact-site 도달 근거 누락/금지 충돌), middle 인계 6행 지정.
STATUS 초안 길이 검사 131>130 FAIL 후 재시도 없이 중단, Fast SKIP. lap322 probe 재실행은 최종 report `7d04b9b2…35757ac`와
byte-identical(재현성 확인이며 새 독립 알고리즘/실행 증거 아님). 상세는 lap323 기록·`logs/lap323/`.

**lap322 middle (`14dd9768…94b051a3`, exit0):** §13 여섯 행 심사 완료(§14), 361 passed, SAFETY_PASS. **lap320 middle
(`68cbfb4b…5a85226c7`, report `3d0022b8…a24f60da`):** lap319 F1 **ACCEPT**(수치는 위 R2 항목), targeted 11 passed.
**lap286~318(판정·SHA 원문은 각 lap 기록과 압축본):** lap318이 lap317 ACCEPT-WITH-REVISION(342), lap317 Astra는
lap316 fresh report 동일·failures=[](328), lap316이 lap315 ACCEPT-WITH-NOTES, lap314가 lap313, lap312가 lap311,
lap310이 lap309 V3, lap308 V2 ACCEPT 계열. lap306 하한 20·cross-function UNKNOWN, lap305 291 stack paths, lap304 R6
800×600, lap303 직접4+간접16=20, lap302 `.text`/`.data` 범위, lap301 writer 4·후보 A/B PASS, lap296이 lap295 수리
ACCEPT, lap286 save 레이아웃 재현했으나 카드 종결 REJECT. 원본 SHA 전 구간 불변. lap279~324 수치는 게임 검증으로
승격하지 않는다. G1 제품 증거 0.

## 바퀴 기록
lap2~324 상세·미결·압축 원문은 `docs/history/laps/`에 보존.
직전 STATUS 원문/SHA/줄 수는 `20260912_status_lap324_compaction.md`에 보존했다.
lap325: R1 조건부 연구 범위 결정, 도달·표본 기준 불명확으로 ESCALATE_SOL 갱신. 게임 코드/실행 0.
lap324 ESCALATE_SOL 원문은 lap325 기록 부록 A에 보존. 마일스톤 종료/이동·제품 승인 없음.
```
