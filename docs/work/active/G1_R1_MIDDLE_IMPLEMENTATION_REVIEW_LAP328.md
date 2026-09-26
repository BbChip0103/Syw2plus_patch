# lap328 middle — lap327 R1 구현 실행 전 독립 검수

2026-09-12 / Claude Code claude-opus-5 / high / 중간계획·컨펌. 게임 실행 0, 게임 코드 수정 0.
이 문서는 middle 기술 판정이며 사용자 마일스톤 승인도 제품 증거도 아니다. 현재 큐는 docs/STATUS.md만 따른다.

입력: `G1_R1_MIDDLE_ENVELOPE_LAP326.md` §4·§5·§6(다른 middle 세션이 발행), lap327 work 기록,
`tools/runtime_env.py`/`tests/test_lap326_r1_load_origin.py` 현물, AGENTS/PROMPT 안전 규칙.
증거: 본 lap 신규 probe `docs/history/laps/probes/20260912_lap328_middle_lap327_r1_review_probe.py`
(`29b6ca762e6d73befce70fd7fe044c3cd53d78790fc6e11cedae5ade737a3e9c`), stdout SHA
`99900d589365fd09be6e2365712076fe7189977a64c18f3118a4ad2a0ace88eb`(연속 2회 byte-identical, rc0, failures=[]).
probe는 이전 lap probe를 import하지 않고 현물 AST와 하네스 자체를 합성 reader로 실행해 재유도한다.
독립 재현: `make check` 367 passed·Ruff·compileall·mypy·CONTEXT_PASS, `checks/safety.sh check` SAFETY_PASS,
원본 EXE SHA `b56986e0…c08a8ac` 불변. lap327이 기록한 두 구현 파일 SHA는 현물과 일치한다.

## 판정: **ACCEPT-WITH-REQUIRED-REPAIR**. 1 run은 아직 발효하지 않는다

§5의 구조 조항(F1~F8, P1)은 **전부 충족**한다. 그러나 §4가 요구한 **네 실패 모드의 구분 가능성**이
현물에서 성립하지 않는다(D1·D2). R1은 재시도 금지의 **1회성 측정**이고 그 산출물의 본체가 실패 모드
레코드이므로, 분류가 틀린 채로 그 1회를 소모하는 것은 되돌릴 수 없다. 수리는 R1 레인 안에서 끝나며
공유 `_wait_state`를 건드리지 않는다. 수리 후 **다시 새 middle 검수**를 받고 나서 실행한다.

| 조항 | 판정 | 근거(probe 필드) |
|---|---|---|
| F1 연구 전용 서브커맨드 1개, 제품 경로 무간섭 | **ACCEPT** | `F1_F5_isolation`: 제품 5개 서브커맨드 전부 디스패치 유지, `_g1_flush_input_stage`·`_capture_screenshot` 호출 0 |
| F2 `runtime_driver.read`만, writev/ptrace/int3/winedbg 0 | **ACCEPT** | `F2_forbidden_tokens` 5종 전부 `tools/**` 히트 0, raw reader import 1건 |
| F3 origin 단일 6바이트 read, PS `<h`+비교 dword | **ACCEPT** | `F3_read_shapes`: origin 호출 `[(0x1088B5C,6)]` 1건, `{x:240,y:145,tag:8}`, ps/ps_word/ps_dword 일치 |
| F4 `G1_R1_WAIT_PS_STATES=(9,35)` 선언 상수만 참조 | **ACCEPT** | `wait_predicates` 두 람다가 `[0]`/`[1]` 첨자만 사용, 리터럴 9/35 없음 |
| F5 evidence 분리 | **ACCEPT** | 산출물은 `r1_load_origin.json`/`.log` 둘뿐, 저장소 내 소비자 0(테스트 제외) |
| F6 N4 선행조건 | **미발동** | lap319/320 `main()` 선평가 형태를 재사용하지 않음 |
| F7 합성 4종 | **부분 — D3** | `F7_test_adequacy`: 4종 중 3종이 동어반복 |
| F8 Stage B/쌍/PNG/재pin/재클릭 금지 | **ACCEPT** | 클릭 주입 지점 정확히 1개, 스크린샷 0, golden/baseline 갱신 0 |
| P1 pre≠(0,0,0) → blocker | **ACCEPT** | `P1_precondition` 3항 전부 참, 실패 시 클릭 자체를 건너뜀 |
| §4 네 실패 모드 구분 | **REJECT — 수리 필요** | D1·D2 |

## D1. 클릭 이후의 수집 실패가 `TIMEOUT`으로 기록된다 (모드 ④ → ③ 오분류)

현물(`tools/runtime_env.py` 일반 except 핸들러):

```python
if evidence.get('input', {}).get('count') == 1:
    mode = 'COLLECTION_ERROR' if evidence.get('post') is not None else 'TIMEOUT'
else:
    mode = 'COLLECTION_ERROR'
```

probe가 이 문장을 그대로 실행한 결과: `before_click → COLLECTION_ERROR`,
`after_click_post_missing → TIMEOUT`, `after_click_post_present → COLLECTION_ERROR`.

도달 가능성: 클릭으로 `count=1`이 된 뒤 `evidence['post']` 대입 전까지 이 핸들러가 잡는 예외를 낼 수
있는 문장은 **`post = _g1_r1_read_origin(read_for_process)` 하나뿐**이다(PS35 대기는 `_G1WaitTimeout`
으로 앞 핸들러가 잡는다). 그리고 `_g1_r1_compare_origin`은 리스트 비교뿐이라 예외를 내지 않는다.
⇒ **`post is not None` 가지는 사실상 도달 불가**이고, 실제로 발생하는 post read 실패(모드 ④)는 전부
`TIMEOUT`(모드 ③)으로 남는다. `runtime_driver.read`는 짧은 read에서 값을 돌려주지 않고 `OSError`를
던지므로(`n != size` → `raise OSError(errno, …)`), 현실의 모드 ④는 정확히 이 경로로만 온다.

부수 결함 **D1b:** §4 ④는 `errno·요청 길이·실제 길이·site`를 요구하는데 현물은 `error` 문자열
(`"read {pid}:{addr:x}, got {n}/{size}"`)만 남긴다. 필드로 분해되지 않는다.

## D2. stage budget이 없어 모든 미도달이 `UNKNOWN_BUDGET_EXHAUSTED`로 붕괴한다 (모드 ① 소멸)

R1의 두 대기는 `_wait_state(..., stage="r1_ps9"/"r1_ps35")`를 **`stage_budget` 없이** 호출한다.
이때 `stage_deadline == run_deadline`이므로 폴링 루프는 **run deadline에서만** 빠져나오고
`remaining = max(0.0, run_deadline - finished)`는 **항상 0**이다. 분류 우선순위의 첫 항이
`"UNKNOWN_BUDGET_EXHAUSTED" if remaining <= 0.0`이므로 그 아래 항은 전부 가려진다.

probe가 하네스를 합성 reader로 직접 돌린 결과(`D2_wait_classification.observed`):
`no_stage_budget_never_reached → UNKNOWN_BUDGET_EXHAUSTED`,
`no_stage_budget_all_reads_failed → UNKNOWN_BUDGET_EXHAUSTED`(읽기 전부 실패해도 같은 값),
대조군 `stage_budget_never_reached → FAIL_NO_EFFECT`.

⇒ (i) 모드 ①(예산 내 PS35 미도달)은 **관측 불가능**하고, (ii) 폴링 중 read 실패
(`UNKNOWN_STATE_READ_FAILURE`/`…_COVERAGE`, 모드 ④)도 `classification`에서는 가려진다.
완화: `observation`의 `read_error_count`/`first|last_read_error_provenance`/`poll_count`와
`pending_state` 시계열은 살아남으므로 **원자료는 손실되지 않는다.** 손상되는 것은 분류다.
그러나 §4가 ①과 ③을 구분하라고 한 이유(=클릭이 맞았는데 느린가, 예산이 애초에 모자랐나)는
분류가 상수가 되는 순간 1회 run의 판독에서 사라진다.

## D3. 합성 4종 중 3종이 동어반복이라 D1·D2를 잡지 못한다

`F7_test_adequacy`: `test_r1_synthetic_unreached_is_preserved_as_unknown`,
`…_timeout_preserves_wait_diagnostics`, `…_short_read_is_collection_error_and_not_pass` 세 개는
자기가 `_g1_r1_failure_record(mode=…)`에 **넣은 문자열을** 다시 단언한다. 실제 분류기
(위 D1의 분기, D2의 `_wait_state` 분류)를 통과시키지 않는다. 분류기를 실제로 거치는 검사는
`…_reached_unchanged_is_not_a_pass` 하나뿐이고, CLI 검사는 진짜 진입점을 monkeypatch로 치환한다.
이는 STATUS에 이미 기록된 lap310 정정(ii) “상수표 동어반복은 독립 증거가 아니다”와 같은 종류다.
또한 짧은 read 검사의 fixture(크기-1 바이트 반환)는 `runtime_driver.read`가 만들 수 없는 형태다.

## 수리 계약 — work tier (Luna 또는 Sonnet5 / high). 최소 변경, R1 레인 안에서만

- **(R-a) D1:** post origin read를 자체 `try/except`로 감싸 `COLLECTION_ERROR`로 분류하고
  `errno`·`requested_size`·`actual_size`·`site`(주소와 함수)를 **필드로** 남긴다(D1b). 일반 핸들러의
  `post is not None` 삼항은 도달 불가이므로 제거하거나, 실제로 무엇이 실패했는지 표시하는 상태
  변수로 대체한다. pre origin read에도 같은 필드 분해를 적용한다.
- **(R-b) D2:** 두 대기 호출에 §4의 선언된 배분을 `stage_budget`/`stage_started`로 **명시 전달**한다
  (PS9 준비 40s, 클릭→PS35 20s). `G1_INPUT_STAGE_BUDGETS`에 항목을 추가하지 **않는다** — 그 dict는
  제품 입력 단계 소유이고 모듈 상한 단언에 묶여 있다. `_wait_state` 본문은 **수정 금지**(제품
  `g1-baseline`/`g1-presentation-trace`와 공유). 배분은 여전히 가정이며 첫 run이 실측해 재평가한다.
- **(R-c) D3:** 합성 검사를 분류기 경유로 바꾼다. 최소한 (i) post read가 `OSError`를 던질 때 레코드가
  `COLLECTION_ERROR`이고 errno 필드가 살아있는지, (ii) `stage_budget`을 받은 미도달 대기가
  `FAIL_NO_EFFECT`(→모드 ①)로, 예산 소진이 `UNKNOWN_BUDGET_EXHAUSTED`(→모드 ③)로 갈라지는지를
  **하네스를 실제로 호출해서** 본다. `test.skip`/`.only`/스텁 금지.
- **(R-d) 불변:** F1~F8·P1은 그대로 유지한다. 게임/Wine/Xvfb/클릭 예산은 수리 중에도 **0**이다.
  `make check`와 `checks/safety.sh check`를 통과시키고 파일 SHA를 기록한다.
- **(R-e) 재검수:** 수리 후 **또 다른 새 middle 세션**이 D1·D2·D3의 해소를 독립 확인해야 1 run이
  발효한다. 본 probe를 재실행하면 `files` SHA 단언이 의도적으로 실패한다 — 그것이 “현물이 바뀌었다”는
  신호이며, 재검수 세션은 새 probe로 분류기 동작을 다시 유도해야 한다(과거 rc0 승격 금지).

## 이 판정이 아닌 것

제품 G1 합격, Stage B 허가, runtime 예산 승인, 클릭 결과 승인, 마일스톤 종료/이동이 **아니다**.
`(296,505)` 클릭 결과는 여전히 미관측이고 후보 A `(240,145)`/B `(160,85)`는 정적 후보다.
S1 종결 REJECT, R17/R31 금지, R29 범위 승인 거부, R30 M11 생존, R6-B-R2 미결, WM_CLOSE 결함,
offline 8건 주차, G3 저장 포맷 블로커, N1~N3·N5·W2·W3, (W) `player_offsets.md` 정정 대기는 전부 유효하다.
`make check` 367 passed와 probe rc0은 계획 승인도 제품 검증도 아니다.
