# STATUS 원문 보존 — lap302 압축 직전

- 원문 경로: `docs/STATUS.md`
- 원문 SHA256: `2361a54f829ac3b0b8504787ba82c22fb01ae61957776aa20672e1a762bce23f`
- 원문 줄 수: 124
- 보존 시각: 2026-09-12, lap302 middle(Claude Code claude-opus-5/high)
- 사유: lap302 검수 결과 추가로 130줄 상한을 넘기 때문. 삭제가 아니라 아래에 전문을 보존한다.

## 원문 전체

```markdown
# STATUS — 매 바퀴 갱신하는 기억

## 지금 상태

G1~G4 모두 제품 미완료. M1/G1 유지: 원본 800×600 구도와 입력을 유지한 1600×1200 출력. 제품 기준은
DESIGN, 사람 승인 원문은 feedback/APPROVALS·INBOX를 따르며 2026-09-12 01:03 bounded repair→fresh
validation 허가는 제품/출시 승인이 아니다. DxWrapper 출력/30초 렌더 과거 근거는 있으나 실제
scene/input 쌍과 WM_CLOSE 결함이 남았다. lap275 middle의 F3-R2-R1 선언 범위 승인, lap270 R30 선언
범위 PASS와 R17 계약 종결 FAIL은 함께 유효하며 M11 생존을 지우지 않는다.

G1-S1 계약 계보(상세 `…/G1_S1_MIDDLE_ACCEPTANCE_LAP277.md` §4.1~§4.7, 근거 lap276~296): 이 계보는
**S1 fixture의 정적 타당성**이며 두 run 값 동일성·제품 증거·Stage B 허가·마일스톤 종료가 아니다.

runtime/load 계보(상세 `docs/work/active/G1_RUNTIME_CONTRACT_MIDDLE_LAP284.md`, handoff §11): lap283
Astra → lap284 middle → lap290~296 하네스 ACCEPT → lap297 Astra → lap298 middle 타이틀 확정 →
lap299 work → lap300 middle(절대 좌표 REJECT) → **lap301 work T1~T4 정적 probe PASS**. runtime
예산 요청 없음, Stage B 0 유지. 제품 G1~G4 증거 0, S1 종결 REJECT 유지.

| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | 미완료 | S1/F2-R2 결정성, fresh pair, 실제 입력, WM_CLOSE |
| G2 | 미완료 | 활성8인 전비5000·풀/메모리·저장/지원동기화 증거 |
| G3 | 미완료 | 활성9~16번 실제 플레이/직렬화/지원 통신 |
| G4 | 미완료 | 원본 대비 반복 경로/전략 지표와 개선 |

## 다음 한 가지

**다음 한 가지: 다음 새 middle(Sol/Opus5/high)이 lap301의 수리 probe와 새 report를 독립 검수한다.**
`a6f682eb…a428c7a0` source와 `c312b42e…caaf10a` report의 원본 SHA·writer 4개·후보 A/B 전제와
geometry 결과를 대조한다. 게임/Wine/Xvfb/Stage B/runtime 예산/PNG/슬롯 클릭 실행은 계속 금지한다.

## 지금 막힌 것 (Blockers)

- S1/F2-R2 실제 결정성 미해결. Stage B·원본 재실행·Wine/Xvfb·R6-A/R6-C 금지. production 클릭 금지
  (정상 비활성은 BLOCKED로 남기고 후속 입력은 계속). 원본/제품 EXE·DLL/assets/baseline/golden 변경,
  evidence 재사용, blind retry, PASS 완화 금지.
- **저장/불러오기 절대 좌표 미확정(lap300 §3, REJECT):** 중심식은 `ds:0xE5BF1C/20`(그래픽 객체
  `0xE5BF18`의 +4/+8)에서 원점을 만들고, writer는 `0x431B79/7F`와 성공 exit의 무조건 640×480
  복원 `0x4324B8/C2`다. 800×600은 모드표의 한 값일 뿐이다. lap301은 후보 A title `(240,145)` /
  slots `[260,119,540,143]`…`[260,323,540,347]`, B title `(160,85)` / slots
  `[180,59,460,83]`…`[180,263,460,287]`를 출력했지만, 클릭 시 전역 관측은 실행이 필요하다.
- comparator는 scene 4축과 선택 slot만 본다. nation/전체 slot id/절대 selection·camera/tick은 기계 검사
  밖이며 (B) 원시 필드 대조로만 확인한다. overall PASS도 충분조건이 아니다. `scene.owners`는 owner0~7,
  offsets는 owner0/1만 본다 — owner8~15는 장면 서명에 안 보인다(G3 위험).
- R17 구조 재결 미완료·R31 금지, R29 범위 승인 거부(lap266), R30 M11 생존 유지, R6-B-R2의 count
  1→0 응답 판정 미결(규칙 변경 금지). lap274 추출기의 M-d/M-e 생존은 알려진 드리프트 사각으로 6종
  불일치로 해석·수리하지 않는다. 나머지 offline 8건 주차: H=F2-R1/F3-R1/F6-R2,
  C=R23/R24 및 stage_budget_state, N=R20/R21/R22. 삭제/PASS 전환 없음.
- **W2(lap296 §4.7.4):** `runtime_driver.py`는 아직 매직 리터럴을 읽는다. (a) line 84 `0x8990C8`·line 89
  `0x66B790`/`0x758`은 승격 가능, (b) line 100 `0x8D`는 probe 가드 선행, (c) line 101 `0x8E`는 상수
  부재·값 미재유도라 명명 **금지**.
- **W3(lap300 §4, 신규):** lap296 review probe의 `EXPECTED_SHA["target_probe"]`가 수리 전 SHA를 가리켜
  **영구 exit1**, 회귀 게이트 재사용 불가. 재pin은 자기 검수 대상 증거의 자가 갱신이라 middle/work
  단독 금지 — Astra/사용자 결정 대기. **가드 잔여 사각:** `type`/`owner` 가드는 리터럴 소멸·개명만
  잡고 **값 드리프트는 못 잡는다**(`0x8D`/`0x8E` 기대값 단언 없음, lap292 §4.5.4와 같은 부류).
- **lap301 work probe의 제품 한계:** T1 슬롯0 `-0x1A`·높이 `+0x18` 앵커와 T2 원본 fixture SHA pin은
  수리됐고, T3는 화면 전역 writer 4개와 후보 A/B를 출력한다. 그러나 클릭 시점의 전역값은 실행 없이는
  정할 수 없고, 버튼 hitbox·슬롯 선택·로드 전이는 UNKNOWN이다. 새 middle 독립 검수 전 승격 금지.
- 후보 WM_CLOSE teardown 결함, 실제 후보 scene/input evidence, G2~G4 증거 미해결. lap288/289:
  lap279/lap280/lap284-middle 세 probe는 아직 `0x440FF0` 창을 써 legacy window 오분류 위험이 남는다
  (수치 영향 0; lap289가 work probe만 `0x440F5B`로 좁혔다). **lap292 사각:** 이름 결합 단언이 reader
  이름을 안 봐 `x=i(G1_UNIT_X_OFFSET)`류 폭 드리프트는 통과(기록만, §4.5.4).
- **프로세스 사각:** 상수/앵커 승격 시 결합된 과거 probe를 재실행하지 않으면 잠복 결함이 재발한다
  (lap294·lap296). **provenance:** lap287 경고=lap290 부록, lap293 `ESCALATE_SOL`=lap294 부록 A,
  lap297 `ESCALATE_SOL`(`760a977e…4a8aa84c`)=lap298 부록 A, lap300 STATUS 원문=lap300 압축본.
- S1 여섯 행은 정적 CONFIRMED지만 **fixture 타당성**일 뿐. 두 run 값 동일성 미검증, Stage B/runtime
  pair는 상위 승인 전 금지.
- map-layer serializer **28쌍** 모델은 lap286이 재현해 ACCEPT(`1,400,702`+`30.5`). 한계: 네 fixture가
  전부 정사각·짝수 변이라 (a) 오프셋 210/212의 width/height 배정과 (b) halving layer `((w/2)*h)/2` 대
  `(w*h)//4` 구분 불가(홀수 변 fixture는 실행 필요). owner `+0x8E` 상속 미재유도, runtime layer
  의미·save/load 동일성 미검증.
- **G3 저장 포맷:** bulk 블록 `0x892410..0x975D8C`에 PlayerStruct 8개(`0x956770..0x973D50`)는 들어가지만
  16개는 `0x991330`까지 필요해 `0x1B5A4` B 넘친다. 현재 포맷에 9~16번 직렬화 공간이 구조적으로 없다.
  G1 범위에서 수리하지 않는다.
- **로드 경로 부재(lap284, lap298 재측정):** `tools/runtime_env.py`의 `save` 참조 **0**, PS35 참조 **0**,
  PS 대기값 **{3,5,7,9}**. 수정 대상 함수·기록 위치 미확정 → "연구 하네스" 행 **REJECT**.
- **실행 봉투 미성립(lap284 §5 (a)~(e)):** lap298이 (a)의 1차 클릭만 줄였고 (b) 3 MB save 로드의 90초
  상한, (c) save 선택 절차, (d) PS5 미도달 run의 수집/flush/종료, (e) wall-clock 예산은 전부 미제출
  → 봉투 행 **REJECT** 유지.
- **PS35→PS3 미도달 실패 모드(lap284 §6):** evidence 스키마에 보존 형태가 없어 실행 전 필드 선언 필요, 미선언 → "안전·회귀" 행 ACCEPT-WITH-CONDITION.
- **fixture 확정 근거 부재:** save000/save006 유지는 옳으나 선택 근거가 될 lap284 §7 카드 4항
  (nation/활성 구성/절대 유닛 수)이 lap286~289에서 미산출. 공통 사실은 "owner id ≥8 record 0개"뿐,
  save000 선호는 근거 없는 잠정이다.
- **Plan C 함정(lap298 §10.3 봉인):** 공유 temp의 800×600 `…_d1app2r3_21_load_screen.png`
  (`5e95ed92…d17e5879`)는 원본 로드 대화상자가 **아니다**. 슬롯 문자열은
  `Syw2plus_re/plan_c/src/ui/save_load_screen.cpp`(`f2232e91…90ff41ec`)가 만든다 → 좌표 출처 금지.
  그 모듈이 인용하는 `0x519A0C`/`0xB3AD74`/`0x1088B5C`는 원본 raw 크기 밖이라 섹션 virtual size 확인이
  선행돼야 하나, 셋 다 `FUN_004D60B0` 본문에 실재한다(lap300). 주소 실재≠좌표 출처 적격.
- **lap284 tick 순환 의존은 해소됐다(lap297 결정1 + lap298 ACCEPT).** 연구 쌍 tick은 허용오차 없는
  report-only이고 철회 범위는 연구 쌍 입력 요구뿐이며 제품 S1의 (A)+(B)는 그대로다. **`(296,505)`의
  한계:** 위치·라벨만 확정이고 **클릭 결과는 관측된 바 없으며** 슬롯 선택 UI·로드 후 전이는 UNKNOWN.

## 검증 상태

**lap301 work (probe `a6f682eb…a428c7a0`, report `c312b42e…caaf10a`, exit0):** 원본 EXE와
원본 입력 sprite SHA pin, T1/T2, writer 4개, 후보 A/B 전제·geometry 4항 PASS. report는
`logs/lap301/save_load_layout_probe.json`, 게임 실행 0.

**lap300 middle (review probe `718b1e4e…17ea63cf`, report `bcac0a41…764c67b2`, exit0):** lap299/lap280
report 결정성 및 `this+0x408`/stride16/count7/rect/버튼을 재유도하고, 로더 문자열과 280×24 bar를 확인.
lap296 가드는 fail-closed 확인, make check 292 passed, ruff/compileall/mypy/context 및 safety PASS, 게임 0.

lap296 middle이 lap295 수리를 ACCEPT(mutant 6종, 80 B 복원 SHA). lap286 middle이 save 레이아웃을 독립
재현(ACCEPT-WITH-CORRECTION): 경계 `0x440C20..0x440F5A`, fwrite 22/layer 28/helper 3/roster 1,
`1,400,702`·`30.5` 독립 유도, 네 fixture 모두 **owner id ≥8 record 0개**. 정정2로 `roster_records`
반증력은 **정수배 검사 4건**뿐이고 lap288은 경계 ACCEPT / 카드 종결 REJECT. lap284 middle:
fingerprint 9/9, 페이로드 50, 고정 22,978 B, map offset 70, 210/212. lap279~300 수치는
`docs/history/laps/`에 있고 실제 게임 검증으로 승격하지 않는다. G1 제품 증거 0.
이전 STATUS 원문은 `…_status_lap276/284/288/290/294/296/298/300_compaction.md`에 보존했다.

## 바퀴 기록

lap2~276 상세와 압축 원문은 `docs/history/laps/`.
lap277~283: 측정식 반려·대체 → 여섯 행 CONFIRMED, 유닛 오프셋 상수 3개 승격, objdump 독립 검수.
G3 저장 블로커 발견 후 lap283 Astra가 runtime/G3 결정. lap284~289: 여섯 입력 판정으로 runtime 예산
보류, 저장 레이아웃 카드 인계·lap286 독립 재현·경계 수리·`0x440F5B` 축소. 과거 PS3 run의 scene.tick은
폴링 산물. lap290~296: lap280 traceback을 상수 승격발 하네스 결합 결함으로 확정 → 수리 → 검수 →
승격 → 무방비 소비처 확정 → line 156·167 가드 → lap296 **ACCEPT**, §4.4.3 종결. lap297: Astra 세 결정
승격. lap298: middle이 그 결정을 판정하고 타이틀 `(296,505)`를 게임 실행 0으로 확정, Plan C 캡처 봉인.
lap299: work가 `FUN_004D60B0`+sprite header로 800×600 정적 레이아웃 재유도, geometry probe·check PASS.
lap300: middle이 lap299를 독립 검수해 결정성 ACCEPT, 상대 모델 ACCEPT-WITH-CORRECTION(앵커 구멍
`-0x1A`, fixture 미pin), **절대 800×600 좌표표 REJECT**(화면 전역 writer로 진입 경로 확정),
lap296 §4.7.6 가드 ACCEPT(+W3 신규) 및 work T1~T4 handoff.
lap301: work가 T1/T2를 수리하고 T3 후보 A/B·writer report를 생성, probe·make check·safety PASS.
```
