# STATUS 원문 보존 — lap298 압축 직전

원문 SHA256 `260f0435adcfee02520433b3b55795f5134381482e602d2ea83b9f4858f75f83`, **130줄**.
lap298이 lap297 게이트 판정과 load UI 근거를 반영하며 130줄 상한을 지키기 위해 압축했다.
승인·반려·미결 근거는 삭제하지 않고 아래 원문과 현재 STATUS에 함께 보존한다.

---

# STATUS — 매 바퀴 갱신하는 기억

## 지금 상태

G1~G4 모두 제품 미완료. M1/G1 유지: 원본 800×600 구도와 입력을 유지한 1600×1200 출력.
제품 기준은 DESIGN, 사람 승인 원문은 feedback/APPROVALS와 INBOX를 따른다.
사용자의 2026-09-12 01:03 bounded repair→fresh validation 허가는 제품/출시 승인이 아니다.
DxWrapper 출력/30초 렌더 과거 근거는 있으나 실제 scene/input 쌍과 WM_CLOSE 결함이 남았다.

lap275 middle이 F3-R2-R1을 선언 범위 승인(offline 기계 증거, producer 6종·comparator 일치, 새 PASS
경로 0). lap270 R30 선언 범위 PASS와 R17 계약 종결 FAIL은 함께 유효하며 M11 생존을 지우지 않는다.
나머지 offline 8건은 lap271 H/C/N 분류로 주차됐고 Stage B 선행조건이 아니다.

G1-S1 계약 계보(상세 `docs/work/active/G1_S1_MIDDLE_ACCEPTANCE_LAP277.md` §4.1~§4.7, lap 근거는
`docs/history/laps/` lap276~296): Astra 방향 → 측정식 반려·대체 → work 정적 조사 → 여섯 행 전부
CONFIRMED → 다른 추출 경로 교차검증 수용(정정 2건) → 상수 3개를 `tools/runtime_env.py`로 승격 →
새 objdump 독립 검수 ACCEPT-WITH-CORRECTION(정정 1건). 이 계보는 **S1 fixture의 정적 타당성**이며
두 run의 값 동일성·제품 증거·Stage B 허가·마일스톤 종료가 아니다. comparator/producer/PASS 무변경.

lap283 Astra가 runtime 연구/Stage B 분리와 G3 저장 경계를 결정하고 실행 계약 누락으로 승격했다
(`docs/work/active/G1_RUNTIME_G3_ASTRA_DECISION_LAP283.md`). lap284 middle이 그 여섯 필수 입력을
판정했다(`…/G1_RUNTIME_CONTRACT_MIDDLE_LAP284.md`): 측정식 ACCEPT, 실패 보존
ACCEPT-WITH-CONDITION, fixture·하네스 연결·tick·실행 봉투 **REJECT**.
따라서 **runtime 예산 요청 없음, Stage B 0 유지**. 게임/Wine/Xvfb/실행은 0이다.

lap290~296 일곱 바퀴는 전부 lap280 static probe 하네스의 건전성이었다. lap296 middle이 lap295
수리를 **ACCEPT**하고 §4.4.3 계열을 종결했다(§4.7). 같은 기간 제품 G1~G4 증거는 0으로 정지해
있으며, 남은 상위 블로커(Stage B 허가, lap284 runtime 예산 REJECT와 tick 순환 의존, G3
`0x1B5A4` 초과)는 전부 이 tier 위의 결재를 기다린다. S1 카드 종결은 REJECT 유지.

| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | 미완료 | S1/F2-R2 결정성, fresh pair, 실제 입력, WM_CLOSE |
| G2 | 미완료 | 활성8인 전비5000·풀/메모리·저장/지원동기화 증거 |
| G3 | 미완료 | 활성9~16번 실제 플레이/직렬화/지원 통신 |
| G4 | 미완료 | 원본 대비 반복 경로/전략 지표와 개선 |

## 다음 한 가지

**다음 한 가지: 새 middle 세션이 `docs/work/active/G1_ASTRA_RESEARCH_GATE_LAP297.md`의
세 상위 결정과 handoff 표를 ACCEPT/REJECT로 판정하고 work 실행 범위 또는 구체 blocker를 확정한다.**
lap296 §4.7.6 두 scrape 가드 수리 인계는 유지하며 실제 work 때 먼저 수리·독립 검수한다.
Astra는 연구 tick report-only/별도 load evidence/fixture 두 후보 유지를 결정했다.
실행 예산은 여전히 0. load UI·명령·봉투 미확정으로 `loop/ESCALATE_SOL` 인계한다.

## 지금 막힌 것 (Blockers)

- S1/F2-R2 실제 결정성은 미해결. Stage B, 원본 재실행, Wine/Xvfb, R6-A/R6-C 금지.
- comparator는 scene 4축과 선택 slot만 본다. nation/전체 slot id/절대 selection·camera/tick은
  기계 검사 밖이며 (B) 원시 필드 대조로만 확인한다. overall PASS도 충분조건이 아니다.
- `scene.owners`는 owner0~7, offsets는 owner0/1만 본다. owner8~15는 장면 서명에 안 보인다(G3 위험).
- 원본/제품 EXE·DLL/assets/baseline/golden 변경, evidence 재사용, blind retry, PASS 완화 금지.
- production 클릭 금지. 정상 비활성은 BLOCKED로 남기고 후속 입력은 계속한다.
- R17 구조 재결 미완료, R31 금지. R29 범위 승인 거부(lap266), R30 M11 생존 유지.
- lap274 추출기의 M-d/M-e 생존은 알려진 드리프트 사각. 6종 불일치로 해석하지 않고 수리하지 않는다.
- R6-B-R2의 count 1→0 응답 판정은 미결. 규칙 변경 금지.
- 나머지 offline 8건은 주차: H=F2-R1/F3-R1/F6-R2, C=R23/R24 및 stage_budget_state,
  N=R20/R21/R22. 삭제/PASS 전환 없음.
- **W2(lap296이 세 부류로 분해, §4.7.4):** `runtime_driver.py`는 아직 매직 리터럴을 읽는다.
  (a) line 84 `0x8990C8`·line 89 `0x66B790`/`0x758`은 동일 값 상수가 이미 있고 원문을 긁는
  probe가 0개라 승격 가능. (b) line 100 `0x8D`는 probe 가드가 선행돼야 한다. (c) line 101
  `0x8E`는 `G1_UNIT_OWNER_OFFSET`이 없고 값이 미재유도라 이름 붙이기 **금지**.
- **lap296 측정:** lap280 probe line 129-130이 `pinned`를 만드는 무가드 scrape다. §4.6.3 불변식은
  인덱싱만 덮었으므로 lap290 결함 계열은 아직 열려 있다. 수리 인계는 §4.7.6에 보존하며 middle 패키지에 포함한다.
- **stale 기대값 주의:** 수리 후 lap294 probe의 `scope_verdict`는 `"refs guard alone is
  sufficient"`로 뒤집혀 보이지만 앵커 소멸 artifact다. §4.6.2의 불충분 판정은 유효하다(§4.7.5).
- 후보 WM_CLOSE teardown 결함, 실제 후보 scene/input evidence, G2~G4 증거 미해결.
- lap288/lap289: lap279/lap280/lap284-middle 세 probe는 아직 `0x440FF0` 창을 써서 legacy window
  오분류 위험이 남는다(수치 영향 0). lap289가 work probe만 `0x440F5B`로 좁혔다.
- **lap292 잔여 사각:** 이름 결합 단언이 reader 이름을 안 봐 `x=i(G1_UNIT_X_OFFSET)`류 폭
  드리프트는 통과한다(기록만, §4.5.4).
- **프로세스 사각:** 상수/앵커 승격 시 결합된 과거 probe를 재실행하지 않으면 잠복 결함이 재발한다.
  probe 52개 중 42개가 구현 모듈을 참조하나 소스를 읽는 것은 lap280·lap282뿐이다. lap294가 두 번째,
  lap296 §4.7.4가 세 번째 사례다.
- **provenance:** lap287 middle probe 편집 경고는 lap290 기록 부록, lap293 `ESCALATE_SOL` 원문
  (`82d8ec12…6cf045f1`)은 lap294 기록 부록 A에 보존했다. lap289/lap290 전후 SHA는 history에 있다.
- S1 여섯 행은 정적 CONFIRMED지만 **fixture 타당성**일 뿐이다. 두 run의 실제 값 동일성은
  미검증이며 Stage B/runtime pair는 상위 승인 전 금지.
- map-layer serializer **28쌍** save static 모델은 lap286이 재현해 ACCEPT(`1,400,702`+`30.5`).
  한계: 네 fixture가 전부 정사각·짝수 변이라 (a) 오프셋 210/212의 width/height 배정과 (b) halving
  layer `((w/2)*h)/2` 대 `(w*h)//4`를 구분 불가(홀수 변에서 갈라짐). 홀수 변 fixture는 게임 실행을
  요구한다. owner `+0x8E`는 상속 가정 미재유도, runtime layer 의미·save/load 동일성 미검증.
- **G3 저장 포맷:** save/load bulk 블록은 `0x892410..0x975D8C`다. PlayerStruct 8개
  (`0x956770..0x973D50`)는 들어가지만 16개는 `0x991330`까지 필요해 `0x1B5A4` 바이트 넘친다.
  현재 포맷에 9~16번 플레이어를 직렬화할 공간이 구조적으로 없다. G1 범위에서 수리하지 않는다.
- **lap284:** 하네스에 저장 로드 경로 0줄(`runtime_env.py` save 참조 0, PS35 참조 0, 대기 PS는
  3/5/7/9뿐)이고 타이틀 불러오기 좌표가 없다. 좌표 확보는 게임 실행을 요구해 offline과 분리한다.
- **lap284 tick 순환 의존:** 계약은 tick 오차 근거 없이 runtime 예산을 막는데 그 근거는 로드 경로를
  한 번 실행해야 나온다. lap297은 연구 tick report-only를 결정했으나 load 봉투는 미확정.

## 검증 상태

lap297 Astra: 문서만 변경. fresh make check 292 passed(48.81s), SAFETY_PASS; 상세는 lap297 이력.

**lap296 middle (fresh, probe `ba1f23b8…15babea2`, report `a690843f…7e0b584d`, exit0
`failures` 0):** lap295 수리 **ACCEPT**. §4.6.4 세 조건 전부 CONFIRMED — 정상 run exit0·1,139 B·
stderr 0 B이고 `logs/lap280/s1_crossverify_probe.json`과 `cmp` 바이트 동일(`3d4fe307…6a6d6a9126`),
동행 4종 `e848c940…`/`e0f07f3a…`/`28703830…`/`7381b5f7…` 불변, 자체 정의 삭제 mutant 3종이
1,083/1,083/1,073 B 명명 failure·`crash=null`·exit1. **범위 증명(새 증거):** 지시된 두 가드만
되돌린 80 B 복원본의 SHA가 수리 전 `edefa0e4…7b47f61d`와 바이트 일치 → 다른 곳 변경 0.
반증력 유지: 값 드리프트 mutant 3-failure, 리터럴 회귀 mutant 1-failure. lap292 review probe의
top-level failure는 `target_probe sha mismatch` **하나뿐**(§4.6.4 5항 예상대로), lap294 probe의
exit1 5건은 전부 stale 기대값. `make check` 292 passed(46.68s), ruff/compileall/mypy/CONTEXT_PASS,
`SAFETY_PASS`. 게임·Wine·Xvfb·Stage B·runtime 예산·PNG 0. 원본 EXE `b56986e0…c9c08a8ac`,
구현 모듈 `dd2ad043…8500190`/`ae4ff939…4e4291b5` 불변.

lap286 middle이 save 레이아웃 모델을 독립 추출 경로로 재현(ACCEPT-WITH-CORRECTION): 경계
`0x440C20..0x440F5A`, 직접 fwrite 22 / layer 28 / helper 3 / roster 1, 상수항 `1,400,702`와
면적계수 `30.5` 독립 유도, 네 fixture 모두 **owner id ≥8 record 0개**. 정정2로 `roster_records`의
반증력은 **정수배 검사 4건**뿐이다. lap288은 경계·mutation 반증력 ACCEPT / 카드 종결 REJECT였다.
lap284 middle: lap283 fingerprint 9/9 일치, save 페이로드 50개, 첫 layer 앞 고정 22,978 B,
map block 오프셋 70, 폭/높이 210/212. 과거 PS3 run 8건의 scene.tick은 폴링 산물이다.
lap279~295 수치는 `docs/history/laps/`에 있다. 실제 게임 검증으로 승격하지 않는다. G1 제품 증거 0.
이전 STATUS 원문은 `…_status_lap276/284/288/290/294/296_compaction.md`에 보존했다.

## 바퀴 기록

lap2~276 상세와 압축 원문은 `docs/history/laps/`.
lap277~282: middle이 측정식을 반려·대체하고 여섯 행 CONFIRMED로 교체, 교차검증(정정 2건),
work가 유닛 오프셋 상수 3개 승격, middle이 새 objdump로 독립 검수(정정 1건). G3 저장 블로커 발견.
lap283: Astra가 runtime 연구/Stage B 분리와 G3 저장 경계를 결정. 실행 계약 누락으로 승격.
lap284: middle이 여섯 필수 입력을 ACCEPT1/조건부1/REJECT4로 판정해 runtime 예산을 보류하고
저장 레이아웃 카드를 work에 인계(모델 일치). lap286: middle이 그 모델을 독립 재현해
ACCEPT-WITH-CORRECTION(정정 2건, 범위 한계 4건).
lap287~290: work가 경계 수리·`0x440F5B` 축소, middle이 lap280 traceback을 lap281 상수 승격발
하네스 결합 결함으로 확정해 §4.4.3 인계(카드 종결 REJECT 유지).
lap291~295: work 수리 → middle ACCEPT-WITH-CORRECTION(§4.5) → work가 범위 모순을 보고 승격
(`ESCALATE_SOL`) → middle이 무방비 소비처 두 곳을 확정(§4.6) → work가 line 156·167만 가드.
lap296: middle이 그 수리를 자체 mutant 6종으로 **ACCEPT**하고 80 B 복원 SHA로 범위까지 증명,
W2 승격이 지금은 probe를 0바이트로 죽인다는 새 사실을 §4.7.4에 남기고 §4.4.3 계열을 종결했다.
