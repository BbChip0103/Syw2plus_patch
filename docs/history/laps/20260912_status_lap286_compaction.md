# STATUS 원문 보존 — lap286 압축 직전

- 원문 SHA256: `e3017be144b133c6c004cc41b0666fcd5b964a8f53501e895b5c1c9eef3213de`
- 원문 줄 수: 119
- 보존 시각: 2026-09-12 11:25:59 KST
- 사유: lap286 갱신 후 137줄로 130줄 상한 초과. 아래가 갱신 전 전체 원문이다.

```markdown
# STATUS — 매 바퀴 갱신하는 기억

## 지금 상태

G1~G4 모두 제품 미완료. M1/G1 유지: 원본 800×600 구도와 입력을 유지한 1600×1200 출력.
제품 기준은 DESIGN, 사람 승인 원문은 feedback/APPROVALS와 INBOX를 따른다.
사용자의 2026-09-12 01:03 bounded repair→fresh validation 허가는 제품/출시 승인이 아니다.
DxWrapper 출력/30초 렌더 과거 근거는 있으나 실제 scene/input 쌍과 WM_CLOSE 결함이 남았다.

lap275 middle이 F3-R2-R1을 선언 범위 승인(offline 기계 증거, producer 6종·comparator 일치,
새 PASS 경로 0). lap270 R30 선언 범위 PASS와 R17 계약 종결 FAIL은 함께 유효하며 M11 생존을
지우지 않는다. 나머지 offline 8건은 lap271 H/C/N 분류로 주차됐고 Stage B 선행조건이 아니다.

G1-S1 계약 계보(상세는 `docs/work/active/G1_S1_MIDDLE_ACCEPTANCE_LAP277.md`):
lap276 Astra 방향 → lap277 middle이 lap271 §3 측정식을 반려하고 여섯 항목 표·tick delta
규칙으로 대체 → lap278 work 정적 조사 → lap279 middle이 다섯 행 UNKNOWN을 반려하고 여섯 행
전부 CONFIRMED로 교체(§4.2) → lap280 middle이 다른 추출 경로로 교차검증해 수용(§4.3),
정정 2건(포맷 "완전 열거" 과장 / 유닛 x·y는 이미 `+0x2A2`·`+0x2A4`로 고정) →
lap281 work가 상수 3개를 `tools/runtime_env.py`로 승격 → lap282 middle이 새 objdump로
독립 검수해 ACCEPT-WITH-CORRECTION(accessor 진입점 인용 정정 1건).
이 계보는 **S1 fixture의 정적 타당성**이며 두 run의 실제 값 동일성·제품 증거·Stage B
허가·마일스톤 종료가 아니다. comparator/producer/PASS 규칙은 전 구간 무변경이다.

lap283 Astra가 runtime 연구/Stage B 분리와 G3 저장 경계를 결정하고 실행 계약 누락으로
승격했다(`docs/work/active/G1_RUNTIME_G3_ASTRA_DECISION_LAP283.md`).
**lap284 middle이 그 여섯 필수 입력을 판정했다**
(`docs/work/active/G1_RUNTIME_CONTRACT_MIDDLE_LAP284.md`): 측정식 ACCEPT,
실패 보존 ACCEPT-WITH-CONDITION, fixture·하네스 연결·tick·실행 봉투 **REJECT**.
따라서 **runtime 예산 요청 없음, Stage B 0 유지**. 게임/Wine/Xvfb/실행은 0이다.

| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | 미완료 | S1/F2-R2 결정성, fresh pair, 실제 입력, WM_CLOSE |
| G2 | 미완료 | 활성8인 전비5000·풀/메모리·저장/지원동기화 증거 |
| G3 | 미완료 | 활성9~16번 실제 플레이/직렬화/지원 통신 |
| G4 | 미완료 | 원본 대비 반복 경로/전략 지표와 개선 |

## 다음 한 가지

**다음 한 가지: 새 middle 세션이 저장 파일 레이아웃 work 결과를 독립 검수한다.** work probe가
원본 `0x440C20`의 28 layer와 `0x403950/0x4441E0/0x4464B0` helper fwrite를 포함해 네 fixture
크기를 정확히 재구성했다. save000/006/011/012의 roster 해는 각각 375/558/147/149개이며,
save000/006의 nation·활성 구성·절대 unit record 수를 JSON에 보존했다.
카드 원문은 `docs/work/active/G1_RUNTIME_CONTRACT_MIDDLE_LAP284.md` §7, 상세는
`docs/history/laps/20260912_lap284_work_save_layout.md`다. 실행 예산 0; 하네스 수정·게임 실행·
PASS 규칙 변경은 금지. 다음 middle은 SHA/objdump/probe를 독립 재실행해 ACCEPT/REJECT한다.
상위(Astra) 큐 3건은 §8에 있다: tick report-only 제안, 로드 경로가 PS5→PS3 endpoint 규칙을
우회하는 구조 문제, fixture 열거에서 save011/012가 빠진 건.

## 지금 막힌 것 (Blockers)

- S1/F2-R2 실제 결정성은 미해결. Stage B, 원본 재실행, Wine/Xvfb, R6-A/R6-C 금지.
- comparator는 scene 4축과 선택 slot만 본다. nation/전체 slot id/절대 selection·camera/tick은
  기계 검사 밖이며 (B) 원시 필드 대조로만 확인한다. overall PASS도 충분조건이 아니다.
- `scene.owners`는 owner0~7, offsets는 owner0/1만 본다. owner8~15는 장면 서명에 안 보인다(G3 위험).
- 원본/제품 EXE·DLL/assets/baseline/golden 변경, evidence 재사용, blind retry, PASS 완화 금지.
- production 클릭 금지. 정상 비활성은 BLOCKED로 남기고 후속 입력은 계속한다.
- R17 구조 재결 미완료, R31 금지. R29 범위 승인 거부(lap266), R30 M11 생존 유지.
- lap274 추출기의 M-d(세 번째 함수), M-e(접두어 밖 분류) 생존은 알려진 미래 드리프트 사각.
  현재 6종 불일치로 해석하지 않으며 수리 계열은 열지 않는다.
- R6-B-R2의 count 1→0 응답 판정은 미결. 규칙 변경 금지.
- 나머지 offline 8건은 주차: H=F2-R1/F3-R1/F6-R2, C=R23/R24 및 stage_budget_state,
  N=R20/R21/R22. 삭제/PASS 전환 없음.
- `runtime_driver.py`는 `type=u[0x8D]`, `0x66B790`, `0x758`, `0x8990C8`을 여전히 매직
  리터럴로 읽는다. `runtime_env.py`에 동일 값 상수가 이미 있으므로 드리프트 사각이다(W2).
- 후보 WM_CLOSE teardown 결함, 실제 후보 scene/input evidence, G2~G4 증거 미해결.
- S1 여섯 행은 정적 CONFIRMED지만 **fixture 타당성**일 뿐이다. 두 run의 실제 값 동일성은
  미검증이며 Stage B/runtime pair는 상위 승인 전 금지.
- map-layer serializer **28쌍**(save `0x42A920`계열 / load `0x42A960`계열)은 이제 save 쪽
  element width/area factor와 세 helper의 고정 fwrite를 정적으로 대조해 네 fixture 크기를
  정확히 재구성했다. runtime layer 값의 의미·save/load 값 동일성은 여전히 미검증이다.
- **G3 저장 포맷:** save/load bulk 블록은 `0x892410..0x975D8C`다. PlayerStruct 8개
  (`0x956770..0x973D50`)는 들어가지만 16개는 `0x991330`까지 필요해 `0x1B5A4` 바이트 넘친다.
  현재 포맷에 9~16번 플레이어를 직렬화할 공간이 구조적으로 없다. G1 범위에서 수리하지 않는다.
- **lap284 신규:** 하네스에 저장 로드 경로가 0줄이고(`tools/runtime_env.py`의 save 참조 0,
  PS35 참조 0, 대기 PS는 3/5/7/9뿐) 타이틀의 불러오기 좌표가 저장소 어디에도 없다.
  좌표 확보는 게임 실행 또는 과거 스크린샷 분석을 요구하므로 offline 카드와 분리한다.
- **lap284 신규:** tick 순환 의존 — 계약은 tick 오차 근거 없이는 runtime 예산을 막는데
  로드 경로의 tick 근거는 로드 경로를 한 번 실행해야 나온다. 상위 결재 전 해소 불가.

## 검증 상태

lap284 middle: lap283 fingerprint **9/9 일치**, lap282 probe 출력과 lap283 recheck 출력이
바이트 동일. 신규 probe `…lap284_middle_runtime_contract_probe.py` exit0 failures=[]
(`logs/lap284/runtime_contract_probe.json`): save entry 페이로드 순서 50개(literal 17 → layer
28 → literal 3 → bulk → literal 1 → 로스터), map bounds가 layer보다 앞·bulk가 layer보다 뒤,
첫 layer 앞 고정 22,978 B, map block 파일 오프셋 70. 유도한 폭/높이 오프셋 210/212에서
save000·006=180×180, save011·012=100×100(가드 1..180 안). 같은 지도 쌍 크기 차이가 `0x758`의
정수배(183배 / 2배). 과거 PS3 run 8건의 scene.tick은 6이 7건·7이 1건이며 폴링 산물이다.
`make check` **292 passed(44.47s)**, Ruff/compileall/mypy 10 files, CONTEXT_PASS, SAFETY_PASS.
원본 EXE SHA `b56986e0…c9c08a8ac` 전후 동일. static-only; 게임/Wine/Xvfb/Stage B/PNG 0.
lap284 work probe `…lap284_work_save_layout_probe.py` exit0 failures=[]
(`logs/lap284/work_save_layout_probe.json`): 28 layer + helper fwrite 모델이 네 fixture를 정확히
재구성했고 roster `375/558/147/149`, save000/006 absolute unit records와 owner별 분포를 보존했다.
새 middle 독립 검수 전이며 제품 G1 증거로 승격하지 않는다.
최종 fresh `make check`는 **292 passed in 48.17s**, Ruff/compileall/mypy/CONTEXT_PASS,
probe/Ruff/py_compile/safety도 exit 0/`SAFETY_PASS`다. 실제 게임 실행은 0이다.
lap283 Astra: lap282 probe/출력 SHA 일치, 재실행 출력 동일·failures=[]. G3 초과 0x1B5A4 재확인.
make check 292 passed(45.47s), CONTEXT_PASS/SAFETY_PASS. 실제 실행 0, 계획 middle 미승인.
lap279~282 수치(291~292 passed, 각 probe failures=[], 기록 SHA 전수 일치)는
`docs/history/laps/`에 있다. 그 수치를 실제 게임 검증으로 승격하지 않는다. G1 신규 제품 증거 0.
이전 STATUS 원문은 `docs/history/laps/20260912_status_lap276_compaction.md`와
`…_status_lap284_compaction.md`에 SHA/줄 수와 함께 보존했다. 반려/승격 원문은 삭제하지 않는다.

## 바퀴 기록

lap2~276 상세와 압축 원문은 `docs/history/laps/`.
lap277: middle이 측정식 반려·대체 확정, work 조건부 승인. 게임 코드 변경 0.
lap278: work가 원본 저장/불러오기 정적 조사와 여섯 행 판정을 기록했다. 게임 코드 변경 0.
lap279: middle이 다섯 행 UNKNOWN을 반려하고 여섯 행 전부 CONFIRMED로 교체. G3 저장 포맷
블로커 발견. lap280: middle이 다른 추출 경로로 교차검증해 수용, 정정 2건.
lap281: work가 유닛 오프셋 상수 3개를 승격하고 정적 근거를 memory map에 기록했다.
lap282: middle이 새 objdump로 독립 검수해 수용, 폭 배타성·부호 근거 보강, 정정 1건.
lap283: Astra가 runtime 연구/Stage B 분리와 G3 저장 경계를 결정. 실행 계약 누락으로 승격.
lap284: middle이 그 여섯 필수 입력을 ACCEPT 1 / ACCEPT-WITH-CONDITION 1 / REJECT 4로 판정하고
runtime 예산 요청을 보류했다. 저장 파일 레이아웃 모델 offline 카드 한 장을 work에 인계.
lap284 work: serializer/helper static model이 네 fixture 크기와 정확히 일치. 게임 코드 변경 0,
새 middle 독립 검수 대기. 기록: `docs/history/laps/20260912_lap284_work_save_layout.md`.
(middle 기록: `docs/history/laps/20260912_lap284_middle_runtime_contract.md`)
```
