# lap296 압축 전 docs/STATUS.md 원문 보존

- 보존 시각: 2026-09-12 (lap 296, middle)
- 원문 SHA256: `a49a60c8f6da388d6d1a7b870055920e6b443487a388c62ac4ccd8284bf0d378`
- 원문 줄 수: 125
- 사유: lap296 검수 결과를 넣으면 PROMPT.md의 130줄 상한을 넘는다. 원문을 먼저 보존하고 압축한다.

```markdown
# STATUS — 매 바퀴 갱신하는 기억

## 지금 상태

G1~G4 모두 제품 미완료. M1/G1 유지: 원본 800×600 구도와 입력을 유지한 1600×1200 출력.
제품 기준은 DESIGN, 사람 승인 원문은 feedback/APPROVALS와 INBOX를 따른다.
사용자의 2026-09-12 01:03 bounded repair→fresh validation 허가는 제품/출시 승인이 아니다.
DxWrapper 출력/30초 렌더 과거 근거는 있으나 실제 scene/input 쌍과 WM_CLOSE 결함이 남았다.

lap275 middle이 F3-R2-R1을 선언 범위 승인(offline 기계 증거, producer 6종·comparator 일치, 새 PASS
경로 0). lap270 R30 선언 범위 PASS와 R17 계약 종결 FAIL은 함께 유효하며 M11 생존을 지우지 않는다.
나머지 offline 8건은 lap271 H/C/N 분류로 주차됐고 Stage B 선행조건이 아니다.

G1-S1 계약 계보(상세 `docs/work/active/G1_S1_MIDDLE_ACCEPTANCE_LAP277.md` §4.1~§4.6, lap 근거는
`docs/history/laps/` lap276~294): Astra 방향 → 측정식 반려·대체 → work 정적 조사 → 여섯 행 전부
CONFIRMED → 다른 추출 경로 교차검증 수용(정정 2건) → 상수 3개를 `tools/runtime_env.py`로 승격 →
새 objdump 독립 검수 ACCEPT-WITH-CORRECTION(정정 1건). 이 계보는 **S1 fixture의 정적 타당성**이며
두 run의 값 동일성·제품 증거·Stage B 허가·마일스톤 종료가 아니다. comparator/producer/PASS 무변경.

lap283 Astra가 runtime 연구/Stage B 분리와 G3 저장 경계를 결정하고 실행 계약 누락으로 승격했다
(`docs/work/active/G1_RUNTIME_G3_ASTRA_DECISION_LAP283.md`). lap284 middle이 그 여섯 필수 입력을
판정했다(`…/G1_RUNTIME_CONTRACT_MIDDLE_LAP284.md`): 측정식 ACCEPT, 실패 보존
ACCEPT-WITH-CONDITION, fixture·하네스 연결·tick·실행 봉투 **REJECT**.
따라서 **runtime 예산 요청 없음, Stage B 0 유지**. 게임/Wine/Xvfb/실행은 0이다.

lap291 work 수리를 lap292 middle이 ACCEPT-WITH-CORRECTION(§4.5)했고, lap293 work는 그 정정을
수리하다 정의 누락 mutant가 `refs`에서 다시 `KeyError`로 죽어 승격했다. lap294 middle이
§4.6에서 무방비 소비처 두 곳(line 156·167)을 확정했다. lap295 work가 두 자리만 가드하고
정상 report·동행 4종·명명 failure를 fresh 확인했다. S1 카드 종결은 REJECT 유지.

| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | 미완료 | S1/F2-R2 결정성, fresh pair, 실제 입력, WM_CLOSE |
| G2 | 미완료 | 활성8인 전비5000·풀/메모리·저장/지원동기화 증거 |
| G3 | 미완료 | 활성9~16번 실제 플레이/직렬화/지원 통신 |
| G4 | 미완료 | 원본 대비 반복 경로/전략 지표와 개선 |

## 다음 한 가지

**다음 한 가지: 다음 새 middle 세션이 lap295 수리를 독립 검수한다.**
검수 범위는 target probe 정상 report 바이트 동일, 동행 4종 불변, 세 정의 삭제 mutant의
명명 failure/비제로 stdout, `make check` 결과다. 두 review probe의 `EXPECTED_SHA` 편집은 금지하며
수리 후 `target_probe sha mismatch` 한 줄은 예상 결과다(§4.6.4 5항).
게임/Wine/Stage B/runtime 예산/PASS 규칙 변경과 카드 종결은 금지한다.

## 지금 막힌 것 (Blockers)

- S1/F2-R2 실제 결정성은 미해결. Stage B, 원본 재실행, Wine/Xvfb, R6-A/R6-C 금지.
- comparator는 scene 4축과 선택 slot만 본다. nation/전체 slot id/절대 selection·camera/tick은
  기계 검사 밖이며 (B) 원시 필드 대조로만 확인한다. overall PASS도 충분조건이 아니다.
- `scene.owners`는 owner0~7, offsets는 owner0/1만 본다. owner8~15는 장면 서명에 안 보인다(G3 위험).
- 원본/제품 EXE·DLL/assets/baseline/golden 변경, evidence 재사용, blind retry, PASS 완화 금지.
- production 클릭 금지. 정상 비활성은 BLOCKED로 남기고 후속 입력은 계속한다.
- R17 구조 재결 미완료, R31 금지. R29 범위 승인 거부(lap266), R30 M11 생존 유지.
- lap274 추출기의 M-d(세 번째 함수)/M-e(접두어 밖 분류) 생존은 알려진 드리프트 사각. 현재 6종
  불일치로 해석하지 않으며 수리 계열은 열지 않는다.
- R6-B-R2의 count 1→0 응답 판정은 미결. 규칙 변경 금지.
- 나머지 offline 8건은 주차: H=F2-R1/F3-R1/F6-R2, C=R23/R24 및 stage_budget_state,
  N=R20/R21/R22. 삭제/PASS 전환 없음.
- `runtime_driver.py`는 `type=u[0x8D]`, `0x66B790`, `0x758`, `0x8990C8`을 여전히 매직
  리터럴로 읽는다. `runtime_env.py`에 동일 값 상수가 이미 있으므로 드리프트 사각이다(W2).
- 후보 WM_CLOSE teardown 결함, 실제 후보 scene/input evidence, G2~G4 증거 미해결.
- lap288/lap289: lap279/lap280/lap284-middle 세 probe는 아직 `0x440FF0` 창을 써서 legacy window
  오분류 위험이 남는다(수치 영향 0). lap289가 work probe만 `0x440F5B`로 좁혔다.
- **lap292 잔여 사각:** 이름 결합 단언이 reader 이름을 안 봐 `x=i(G1_UNIT_X_OFFSET)`류 폭
  드리프트는 통과한다(기록만, §4.5.4).
- **프로세스 사각:** 상수/앵커 승격 시 결합된 과거 probe를 재실행하지 않으면 잠복 결함이 재발한다.
  probe 52개 중 42개가 구현 모듈을 참조하나 `runtime_driver.py` 소스를 읽는 것은 lap280·lap282뿐이고
  lap290은 나머지를 실행 대조하지 않았다. lap294가 두 번째 사례(한 mutant는 한 상수만 대표한다)다.
- **provenance:** lap287이 middle probe를 편집해 편집 전 SHA가 없다는 경고는 lap290 기록 부록에,
  lap293 `ESCALATE_SOL` 원문(SHA `82d8ec12…6cf045f1`)은 lap294 기록 부록 A에 보존했다.
  lap289/lap290 변경 전후 SHA는 history에 있다.
- S1 여섯 행은 정적 CONFIRMED지만 **fixture 타당성**일 뿐이다. 두 run의 실제 값 동일성은
  미검증이며 Stage B/runtime pair는 상위 승인 전 금지.
- map-layer serializer **28쌍** save static 모델은 lap286이 재현해 ACCEPT(`1,400,702`+`30.5`).
  한계: 네 fixture가 전부 정사각·짝수 변이라 (a) 오프셋 210/212의 width/height 배정과 (b) halving
  layer `((w/2)*h)/2` 대 `(w*h)//4`를 구분 불가(홀수 변에서 갈라짐). owner `+0x8E`는 상속 가정
  미재유도, runtime layer 의미·save/load 동일성 미검증.
- **G3 저장 포맷:** save/load bulk 블록은 `0x892410..0x975D8C`다. PlayerStruct 8개
  (`0x956770..0x973D50`)는 들어가지만 16개는 `0x991330`까지 필요해 `0x1B5A4` 바이트 넘친다.
  현재 포맷에 9~16번 플레이어를 직렬화할 공간이 구조적으로 없다. G1 범위에서 수리하지 않는다.
- **lap284:** 하네스에 저장 로드 경로 0줄(`runtime_env.py` save 참조 0, PS35 참조 0, 대기 PS는
  3/5/7/9뿐)이고 타이틀 불러오기 좌표가 없다. 좌표 확보는 게임 실행을 요구해 offline과 분리한다.
- **lap284 tick 순환 의존:** 계약은 tick 오차 근거 없이 runtime 예산을 막는데 그 근거는 로드 경로를
  한 번 실행해야 나온다. 상위 결재 전 해소 불가.

## 검증 상태

**lap295 work (fresh, target probe `88d86281…2d9a18d`, target stdout/report
`3d4fe307…6a6d6a9126`):** 정상 exit0 및 `logs/lap280/s1_crossverify_probe.json` 바이트 동일.
lap292 review는 target SHA mismatch 1건만 stale 기대값으로 남겼고, 동행 4종은
`e848c940…`/`e0f07f3a…`/`28703830…`/`7381b5f7…` 불변, control·4 mutant는 명명 failure와
traceback 없음. lap294 scope harness의 현재 세 mutant도 `x/y` 1,083 B, `internal_id` 1,073 B
명명 failure로 바뀌었으며 `scope_verdict=sufficient`; harness 자체의 old-state assertion과
target SHA mismatch로 exit1인 것은 예상된 stale 결과다.
`make check` 292 passed(46.36s), ruff/compileall/mypy/CONTEXT_PASS, `SAFETY_PASS`.
게임·Wine·Xvfb·Stage B·runtime 예산·PNG 0. 원본 EXE `b56986e0…c9c08a8ac`, 구현 모듈
`dd2ad043…8500190`/`ae4ff939…4e4291b5` 불변.

lap292 middle(probe `2aaac7a0…33491335`, report `b2f7b217…0faa2cfc`)는 정상 report와 동행 4종
(`e848c940…`/`e0f07f3a…`/`28703830…`/`7381b5f7…`)을 재현했고 정의 삭제 mutant만 Traceback이었다.
lap286 middle이 save 레이아웃 모델을 독립 추출 경로로 재현(ACCEPT-WITH-CORRECTION): 경계
`0x440C20..0x440F5A`, 직접 fwrite 22 / layer 28 / helper 3 / roster 1, 상수항 `1,400,702`와
면적계수 `30.5` 독립 유도, 네 fixture 모두 **owner id ≥8 record 0개**. 정정2로 `roster_records`의
반증력은 **정수배 검사 4건**뿐이다. lap288은 경계·mutation 반증력 ACCEPT / 카드 종결 REJECT였다.
lap284 middle: lap283 fingerprint 9/9 일치, save 페이로드 50개, 첫 layer 앞 고정 22,978 B,
map block 오프셋 70, 폭/높이 210/212. 과거 PS3 run 8건의 scene.tick은 폴링 산물이다.
lap279~293 수치는 `docs/history/laps/`에 있다. 실제 게임 검증으로 승격하지 않는다. G1 제품 증거 0.
이전 STATUS 원문은 `…_status_lap276/284/288/290/294_compaction.md`에 보존했다.

## 바퀴 기록

lap2~276 상세와 압축 원문은 `docs/history/laps/`.
lap277~282: middle이 측정식을 반려·대체하고 여섯 행 CONFIRMED로 교체, 교차검증(정정 2건),
work가 유닛 오프셋 상수 3개 승격, middle이 새 objdump로 독립 검수(정정 1건). G3 저장 블로커 발견.
lap283: Astra가 runtime 연구/Stage B 분리와 G3 저장 경계를 결정. 실행 계약 누락으로 승격.
lap284: middle이 여섯 필수 입력을 ACCEPT1/조건부1/REJECT4로 판정해 runtime 예산을 보류하고
저장 레이아웃 카드를 work에 인계(모델 일치).
lap286: middle이 그 모델을 독립 재현해 ACCEPT-WITH-CORRECTION(정정 2건, 범위 한계 4건).
lap287~290: work가 경계 수리·`0x440F5B` 축소, middle이 lap280 traceback을 lap281 상수 승격발 하네스 결합 결함으로 확정해 §4.4.3 인계(카드 종결 REJECT 유지).
lap291: work가 지정 블록을 상수 정의/이름 결합 검사로 수리하고 fresh 검증 PASS. lap292: middle이
자체 mutant 5종으로 ACCEPT-WITH-CORRECTION(정정 1건, 잔여 사각 1건).
lap293: work가 튜플 가드를 수리했으나 `refs` 재인덱싱이 범위 밖이라 승격(`ESCALATE_SOL`).
lap294: middle이 소비처 두 곳을 확정해 §4.6으로 정정. lap295: work가 line 156·167만
수리하고 fresh probe·mutant·make check·safety를 통과시켰다. 게임·원본·구현 모듈 변경 0.
```
