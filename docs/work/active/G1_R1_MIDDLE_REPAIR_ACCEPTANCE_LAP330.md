# lap330 middle — lap329 R1 수리(D1·D1b·D2·D3)의 독립 재검수

2026-09-12 / Claude Code claude-opus-5 / high / 중간계획·컨펌. 게임 구현·게임 실행 0, 게임 코드 수정 0.
이 문서는 middle 기술 판정이며 사용자 마일스톤 승인도 제품 증거도 아니다. 현재 큐는 docs/STATUS.md만 따른다.

입력: `G1_R1_MIDDLE_IMPLEMENTATION_REVIEW_LAP328.md` §수리 계약(다른 middle 세션이 발행),
`G1_R1_MIDDLE_ENVELOPE_LAP326.md` §4·§5·§6, lap329 work 기록, 현물
`tools/runtime_env.py`/`tests/test_lap326_r1_load_origin.py`, AGENTS/PROMPT 안전 규칙, APPROVALS 2026-09-12 01:03.
증거: 본 lap 신규 probe `docs/history/laps/probes/20260912_lap330_middle_lap329_r1_repair_probe.py`
(`37be75bfe077662b6a26d9a7cc4906d7cc35771f8b142a464579a035ec62d680`),
stdout SHA256 `d2caedd75fa7cb3b3be339ed3a4f3b8bb1b3092352bd79ecddb0664f57507850`
(연속 2회 byte-identical, rc0, `failures=[]`). probe는 이전 lap probe를 **import하지 않고**
현물 AST와 하네스 자체를 합성 reader로 실행해 재유도한다. 검수 대상 현물 SHA는 lap329 기록과 일치한다:
`tools/runtime_env.py`=`997ff15b…cc46eed`, `tests/test_lap326_r1_load_origin.py`=`81acc11e…cac72`.
독립 재현: `make check` **368 passed**·Ruff·compileall·mypy·CONTEXT_PASS·rc0,
`bash checks/safety.sh check` **SAFETY_PASS**, 원본 EXE SHA `b56986e0…c08a8ac` **불변**.

## 판정: **ACCEPT**. lap328의 D1·D1b·D2·D3는 모두 해소됐고 제한 1 run을 **발효**한다

lap328 §R-e가 지정한 "또 다른 새 middle의 독립 확인"이 본 lap이다. 세 결함은 전부 닫혔고,
F1~F8·P1과 공유 코드 불변은 유지된다. 남는 것은 한 건의 **잠복 함정(N7)**뿐이며 수치 영향 0이다.

| 수리 조항 | 판정 | 근거(probe 필드) |
|---|---|---|
| (R-a) D1 — post 수집 실패가 COLLECTION_ERROR | **ACCEPT** | `D1_routing`: 두 origin read 모두 `_g1_r1_read_origin_checked`, 핸들러 순서 `_G1WaitTimeout` → `_G1R1CollectionError` → 일반 튜플. 일반 핸들러는 더 이상 read 실패를 받지 않는다 |
| (R-a) D1b — errno·요청/실제 길이·site 필드 분해 | **ACCEPT** | `C_collection_error`: **실제** `process_vm_readv` 실패(자기 프로세스 pid0/addr0, `[Errno 3] read 0:0, got -1/6`)를 통과시켜 pre/post 모두 `errno=3`·`requested_size=6`·`actual_size=-1`·`site={address,function,phase}` 보존 |
| (R-b) D2 — stage budget 명시 전달 | **ACCEPT** | `B_wait_call_sites`: PS9 `stage_budget=G1_R1_PS9_STAGE_BUDGET, stage_started=started`, PS35 `=G1_R1_PS35_STAGE_BUDGET, stage_started=ps35_stage_started`. 상수 실측 40.0/20.0 |
| (R-b) 공유 코드 불변 | **ACCEPT** | `B_shared_invariants`: `_wait_state` 본문에 R1 이름 **0개**, `G1_INPUT_STAGE_BUDGETS` 키 = 제품 3개(`drag_select,minimap,unit_select`)·합 30.0 |
| (R-c) D3 — 분류기 경유 | **ACCEPT** | `D3_test_adequacy`: 테스트 6개, `_g1_r1_failure_record` 직접 주입 **0건**, 분류기 미경유 테스트 **0건**, skip/xfail/TODO 마커 **0** |
| (R-d) F1~F8·P1 | **ACCEPT** | `E_structural`: 제품 5개 서브커맨드 유지, 금지 토큰 5종 `tools/**` 히트 0, origin read site 1, 예측 람다가 `G1_R1_WAIT_PS_STATES[0]/[1]`만 사용(리터럴 9/35 0), R1 내부 클릭 주입 1·스크린샷 0, `BLOCKED_PRECONDITION` 게이트 존재 |
| §4 네 실패 모드 구분 | **ACCEPT** | `B_mode_separation`: 서로 다른 4값 |

## 1. 네 모드는 실제 분류기를 돌려 네 값으로 갈라진다 (lap328 D2의 역재현 포함)

probe가 `_wait_state`를 **가짜 시계로 실제 호출**해 얻은 값(합성 reader, 게임 0):

| 시나리오 | stage_budget | wait classification | R1 mode | remaining |
|---|---|---|---|---|
| PS9 스테이지 내 미도달 | 40.0 | `FAIL_NO_EFFECT` | **UNREACHED** ① | 50.0 |
| PS35 스테이지 내 미도달(클릭 t=45) | 20.0 | `FAIL_NO_EFFECT` | **UNREACHED** ① | 25.0 |
| PS35 run deadline 소진(클릭 t=85) | 20.0 | `UNKNOWN_BUDGET_EXHAUSTED` | **TIMEOUT** ③ | 0.0 (`run_deadline_clamped=true`) |
| PS35 폴링 read 전부 실패 | 20.0 | `UNKNOWN_STATE_READ_FAILURE` | **COLLECTION_ERROR** ④ | 25.0 (`read_error_count=80`) |
| PS35 도달 | 20.0 | — | 반환 `ps=35` | — |
| **대조군** stage_budget 없음 | `null` | `UNKNOWN_BUDGET_EXHAUSTED` | TIMEOUT | 0.0 |

마지막 행이 lap328 D2의 붕괴 형태이며, 같은 reader·같은 시계에서 **호출부의 `stage_budget` 유무만으로**
①과 ③이 갈린다. 즉 수리의 인과가 호출부 변경에 있음이 재유도된다. 모드 ②는 대기가 아니라 비교기가 낸다:
`_g1_r1_compare_origin((0,0,0),(0,0,0))` → `REACHED_UNCHANGED`/`UNKNOWN`, 변화 표본은 `OBSERVED`.

## 2. D1b는 손으로 옮긴 문자열이 아니라 실제 커널 실패로 확인했다

lap329 테스트는 `OSError(5, "read 123:1088b5c, got -1/6")`를 직접 만든다(형태는 맞으나 자기 선언이다).
본 probe는 대신 `patches/population/runtime_driver.read(0, 0, 6)`를 **실제로** 호출해 커널이 만든
`ProcessLookupError: [Errno 3] read 0:0, got -1/6`을 얻고, 그 예외를 `_g1_r1_read_origin_checked`에
그대로 통과시켰다. 진단 정규식 `(?:got|returned)\s+(-?\d+)/(\d+)`가 **현물 메시지 형태에 맞는다**는
것이 이로써 독립 확인된다(이 형태는 `runtime_driver.py:50`이 만드는 유일한 read 실패 형태다).
쓰기·ptrace·게임 프로세스 접근은 없다. 대상은 자기 프로세스의 주소 0이다.

## 3. 잔여 — N7 (수치 영향 0, 완화 아님)

일반 핸들러의 `COLLECTION_ERROR if evidence.get('post') is not None else TIMEOUT` 삼항은
lap328이 "제거하거나 상태 변수로 대체"를 제안했는데 **그대로 남아 있다**. 다만 오분류는 사라졌다:
클릭 이후 그 핸들러에 도달할 수 있는 예외원이 없기 때문이다 — post origin read는
`_G1R1CollectionError`(앞 핸들러), PS35 대기는 `_G1WaitTimeout`(더 앞 핸들러)으로 가고,
`_wait_state`의 폴링 루프는 reader의 `OSError/ValueError/struct.error`를 스스로 삼킨다.
따라서 **N7 = 죽은 분기의 잠복 함정**: 클릭 이후·`evidence['post']` 대입 이전에 예외를 낼 수 있는
문장이 앞으로 하나라도 추가되면 그 실패는 다시 `TIMEOUT`(모드 ③)으로 기록된다. 지금 수리하지 **않는다**
— 검수한 SHA와 실행할 SHA를 같게 유지하는 것이 1 run의 exact-once 규칙보다 우선한다. 기록으로만 남긴다.

## 4. 발효 조건 — work tier가 정확히 1 run

- 실행 주체는 **work tier(Luna 또는 Sonnet5/high)**다. 본 middle은 실행하지 않는다.
- 실행 아티팩트는 **본 lap이 검수한 SHA 그대로**여야 한다(`997ff15b…cc46eed`/`81acc11e…cac72`).
  실행 전 어떤 수정도 금지하며, 수정하면 그 순간 본 ACCEPT는 소멸하고 새 middle 검수가 필요하다.
- **정확히 1회**, `--timeout` ≤ 90초, 고정 `1600x1200x24`, 새 private prefix/output(하네스가 강제).
  실패해도 **무변경 blind 재시도 금지**. 실패 레코드·로그·`r1_load_origin.json`을 전부 보존한다.
- 배분 40/20/15/15는 여전히 **가정**이다. 첫 run이 실측해 기록하고 재평가 대상으로 남긴다.
- 미도달(①)은 **정당한 결과**다. 도달 실패를 근거로 클릭 좌표·예산·판정식을 그 자리에서 바꾸지 않는다.
- 산출물은 연구 레인 전용이다. 제품 G1 evidence·Stage B·PNG 비교·W3 재pin·baseline/golden 갱신·
  INT3/원본 이미지 변경·재클릭은 **여전히 금지**다.
- run 뒤에는 다시 새 middle이 결과(네 모드 중 어느 것인지, `pending_state` 시계열, `origin_tag`,
  `ps_word`/`ps_dword`, cleanup·elapsed)를 독립 검수한다. `exit 0`은 판정이 아니다.

## 이 판정이 아닌 것

제품 G1 합격, Stage B 허가, 마일스톤 종료/이동, 사용자 승인이 **아니다**. `(296,505)` 클릭 결과는
여전히 미관측이고 후보 A `(240,145)`/B `(160,85)`는 정적 후보다. S1 종결 REJECT, R17/R31 금지,
R29 범위 승인 거부, R30 M11 생존, R6-B-R2 미결, WM_CLOSE 결함, offline 8건 주차, G3 저장 포맷 블로커,
N1~N6·W2·W3, (W) `player_offsets.md` 정정 대기는 전부 유효하다. G2~G4 증거는 0이다.
`make check` 368 passed와 probe rc0은 계획 승인도 제품 검증도 아니다.
