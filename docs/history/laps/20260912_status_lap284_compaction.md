# STATUS 원문 보존 — lap284 압축 직전

PROMPT ⑤/`loop/PROMPT.md`의 130줄 규칙에 따라 lap284가 `docs/STATUS.md`의 서술을
압축하기 직전 원문을 그대로 보존한다. 반려/승격/미결 근거는 삭제하지 않았다.

- 원문 SHA256: `9087185915dcf8cebd962e79974da65c9e7995d43241cae0a6af920d2075063d`
- 원문 줄 수: 121
- 이 원문은 lap283 종료 시점의 STATUS이며 lap284 시작 시 해시가 동일했다(무변경 확인).

```markdown
# STATUS — 매 바퀴 갱신하는 기억

## 지금 상태

G1~G4 모두 제품 미완료. M1/G1 유지: 원본 800×600 구도와 입력을 유지한 1600×1200 출력.
제품 기준은 DESIGN, 사람 승인 원문은 feedback/APPROVALS와 INBOX를 따른다.
사용자의 2026-09-12 01:03 bounded repair→fresh validation 허가는 제품/출시 승인이 아니다.
DxWrapper 출력/30초 렌더 과거 근거는 있으나 실제 scene/input 쌍과 WM_CLOSE 결함이 남았다.

lap275 middle은 F3-R2-R1을 선언 범위 승인했다(offline 기계 증거).
현재 producer 6종과 comparator 일치, hard FAIL 우선·새 PASS 경로 0을 보고했다.
나머지 offline 8건은 lap271의 H/C/N 분류로 주차됐으며 Stage B 선행조건이 아니다.
lap270 R30 선언 범위 PASS와 R17 계약 종결 FAIL은 함께 유효하다. M11 생존을 지우지 않는다.

lap276 Astra는 S1 저장/불러오기 정적 조사로 방향을 결정했고 lap277 middle이
lap271 §3 요약 측정식을 **반려**하고 여섯 항목 표·tick 규칙으로 대체했다
(`docs/work/active/G1_S1_MIDDLE_ACCEPTANCE_LAP277.md`).
lap279 middle이 lap278 결과를 반려하고 여섯 행 전부를 **CONFIRMED**로 교체했고(§4.2),
lap280 middle이 다른 추출 경로로 독립 교차검증해 그 교체를 **수용(ACCEPT)**했다(§4.3).
정정 2건 동반: (1) "포맷이 정적으로 완전히 열거된다"는 과장 — literal 표 밖에 스택 블록
1개와 map-layer serializer 28쌍이 있다(개수·짝·읽기/쓰기 방향은 기계 확인, 레이어별
원소 수 동일성은 미검증). (2) 유닛 x/y 오프셋은 이미 `+0x2A2`/`+0x2A4`로 고정돼 있고
원본에서 교차확인됐다. 이는 S1 fixture의 **정적 타당성** 2단 판정일 뿐, 두 run의 실제 값
동일성·제품 증거·Stage B 허가·마일스톤 종료가 아니다. comparator/producer/PASS 규칙 무변경.

lap281 work는 위 확정 오프셋 3개를 `tools/runtime_env.py`의 이름 있는 상수로 승격하고
runtime driver가 이를 사용하도록 연결했다. lap282 middle이 이를 독립 검수해
**ACCEPT-WITH-CORRECTION** 했다: lap281 파일 SHA 5/5 일치, 새 objdump 재파싱으로
slot0 주소·폭·slot*0x758 스케일링·x/y 참조 115/115가 전부 재도출됐고, 추가로 필드 내부
바이트 참조 0개(폭 배타성)와 x/y movsx 41/41(부호 해석 근거)을 새로 확인했다.
정정 1건: memory map이 x/y accessor를 `0x40F5D0`/`0x40F5F0`으로 적었으나 그 둘은 읽기
명령 주소(call site 0)이고 실제 진입점은 `0x40F5C0`(caller 74)/`0x40F5E0`(caller 79)다.
오프셋 값은 영향받지 않아 lap281 판정을 뒤집지 않는다. 게임/Wine/Xvfb/Stage B는 0.

| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | 미완료 | S1/F2-R2 결정성, fresh pair, 실제 입력, WM_CLOSE |
| G2 | 미완료 | 활성8인 전비5000·풀/메모리·저장/지원동기화 증거 |
| G3 | 미완료 | 활성9~16번 실제 플레이/직렬화/지원 통신 |
| G4 | 미완료 | 원본 대비 반복 경로/전략 지표와 개선 |

## 다음 한 가지

**다음 한 가지: 새 middle이 lap283 실행 전 계약을 검수하고 저장 fixture 하네스 work 범위를 확정한다.**
상위 결정: `docs/work/active/G1_RUNTIME_G3_ASTRA_DECISION_LAP283.md`.
M1/G1 유지. 원본↔원본 저장 복원 연구 1쌍을 최소 예산 요청 단위로 정했으나 집행은 0이다.
실제 load 절차·하네스 변경안·tick 오차 근거·명령/시간/보존 봉투가 빠져 승격했다.
Stage B 예산도 0. 원본 연구의 새 middle 수용 후 별도 예산 재결 전까지 열지 않는다.
G3는 버전 식별 가능한 확장 저장 계약 방향으로 분리하고 현재 bulk 길이만 늘리는 수리는 금지한다.
W1/W2 정비는 주차 유지하며 S1 선행조건으로 삼지 않는다. 실행/검수 절차는 결정문서 참조.
`active_units` 집계와 PlayerStruct 장부는 다른 양이므로 동일성 전제 금지.

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
- lap279→lap280 검수로 S1 여섯 행은 정적 CONFIRMED가 됐지만 이는 **fixture 타당성**일
  뿐이다. 두 run의 실제 값 동일성은 여전히 미검증이며 Stage B/runtime pair는 상위 승인 전 금지.
- map-layer serializer **28쌍**(save `0x42A920`계열 / load `0x42A960`계열)은 literal 21블록
  표 밖의 가변 페이로드다. 개수·짝·fwrite/fread 방향은 확인했으나 **레이어별 원소 수
  동일성은 미검증**이다. "저장 포맷이 정적으로 완전히 열거됐다"고 쓰지 않는다.
- **신규 G3 저장 포맷 블로커:** save/load bulk 블록은 `0x892410..0x975D8C`다. PlayerStruct
  8개(`0x956770..0x973D50`)는 들어가지만 16개는 `0x991330`까지 필요해 `0x1B5A4` 바이트
  넘친다. 현재 포맷에 9~16번 플레이어를 직렬화할 공간이 구조적으로 없다. 기록만 하고
  G1 범위에서 수리하지 않는다.

## 검증 상태

lap283 Astra: lap282 probe/출력 SHA 일치, 새 재실행 출력 동일·failures=[].
G3 초과 0x1B5A4 재확인. make check 292 passed(45.47s), Ruff/compileall/mypy 10 files,
CONTEXT_PASS/SAFETY_PASS. 원본·구현 SHA 유지. 실제 실행 0, 계획 middle 미승인.

lap282: `make check` **292 passed(44.57s)**, Ruff/compileall/mypy 10 files, CONTEXT_PASS,
SAFETY_PASS, targeted `unit_record_offsets` 1 passed. 신규 objdump 306218행 재파싱 probe
exit0 failures=[] (`logs/lap282/unit_offset_review_probe.json`). lap281 기록 파일 SHA 5/5 일치,
원본 EXE SHA 검수 전후 동일. static-only; 게임/Wine/Xvfb/Stage B 실행 0.
lap281: targeted offset regression 1 passed; 원본 SHA 일치 및 objdump 재확인, driver `--help`
정상. `make check` **292 passed(44.06s)**, Ruff/compileall/mypy 10 files, CONTEXT_PASS,
SAFETY_PASS. static-only; 게임/Wine/Xvfb/Stage B 실행 0.
lap280: make check 291 passed(44.24s), Ruff/compileall/mypy 10 files, CONTEXT_PASS/SAFETY_PASS.
교차검증 probe exit0 failures=[] (`logs/lap280/s1_crossverify_probe.json`); lap279 probe 재실행
exit0 failures=[] 출력 동일. lap279 기록 SHA(원본 EXE/save000/006/runtime_env/comparator) 재계산 일치.
lap279: make check 291 passed(44.49s), Ruff/compileall/mypy 10 files, CONTEXT_PASS/SAFETY_PASS.
serializer probe exit0 failures=[] (`logs/lap279/s1_serializer_probe.json`); lap278 SHA 7종 전부 일치.
save/load 블록 표 21개가 주소·크기·순서까지 동일(block_table_identical=true). 게임 실행 0.
lap276~277 수치와 lap275 169칸 행렬은 `docs/history/laps/`에 있다.
그 수치를 실제 게임 검증으로 승격하지 않는다. G1 신규 제품 증거 0.
전체 이전 STATUS는 `docs/history/laps/20260912_status_lap276_compaction.md`에
원문 SHA/130줄과 함께 보존했다. 이전 반려/승격 원문은 history와 ESCALATE_SOL에 유지한다.

## 바퀴 기록

lap2~275 상세와 압축 원문은 `docs/history/laps/`.
lap276: Astra S1 방향 결정, 계약 모호성으로 middle 인계. 구현 변경 없음.
lap277: middle이 측정식 반려·대체 확정, work 조건부 승인. 게임 코드 변경 0.
lap278: work가 원본 저장/불러오기 정적 조사와 여섯 행 판정을 기록했다. 게임 코드 변경 0.
lap279: middle이 lap278을 독립 검수해 다섯 행 UNKNOWN을 반려하고 여섯 행 전부
CONFIRMED로 교체했다. 신규 G3 저장 포맷 블로커 발견. 게임 코드 변경 0.
lap280: middle이 lap279를 다른 추출 경로로 교차검증해 여섯 행 수용, 정정 2건.
게임 코드 변경 0.
lap281: work가 유닛 오프셋 상수 3개를 승격하고 원본 정적 근거를 memory map에 기록했다.
lap282: middle이 lap281을 새 objdump로 독립 검수해 수용하고, 폭 배타성·부호 근거를
보강했으며 accessor 인용 정정 1건과 work handoff 2건을 남겼다. 게임 코드 변경 0.
이번 기록: `docs/history/laps/20260912_lap282_middle_unit_offset_review.md`
(lap281 기록: `…_lap281_work_unit_offsets.md`).

lap283: Astra가 runtime 연구/Stage B 분리와 G3 저장 경계를 결정. 실행 계약 누락으로
ESCALATE_SOL 인계. 게임 구현·실행 0. 기록: `docs/history/laps/20260912_lap283_astra_runtime_g3.md`.
```
