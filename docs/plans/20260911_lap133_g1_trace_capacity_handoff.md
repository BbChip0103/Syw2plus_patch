# 2026-09-11 lap133 — G1 lossless bounded trace capacity handoff

## 중간 판정

lap132의 owned Win32 close transport는 lap133 Sol/high 독립 검수에서 **MIDDLE CONFIRM PASS**다.
이 판정은 fresh PE32 fixture의 종료 전달 경계만 확인하며 실제 게임 process exit/DLL detach,
overflow 없는 trace, G1 1600×1200 결과나 M1 승인이 아니다.

lap128의 보존된 live trace SHA256
`b105fc3452dc1650aab58cd7c66aa79e97656964a121ab18d80713f6469d8539`는 617행이며,
`surface_release=256`, `blt_fast=256`, overflow 2개가 seq453/454의 PS7에서 발생했다.
이는 method별 256 상한이 PS3 전에 실제 관측을 잘랐다는 실패 증거다. 이 과거 artifact는 입력
fixture일 뿐 새 runtime 성공 증거가 아니다.

## 다음 Luna/high work 한 가지

`tools/inmm_stub/direct_draw_trace.c`의 반복 method event를 bounded하게 집계하되 실제 호출 수와
identity/state/tick provenance를 잃지 않는 계약을 구현하고, validator와 synthetic 회귀로 고정한다.
이번 바퀴에는 게임 runtime을 실행하지 않는다.

### 허용 범위

- `tools/inmm_stub/direct_draw_trace.c`, `tools/check_g1_presentation_trace.py`와 직접 관련된 테스트/
  build fixture만 최소 수정한다. 필요하면 기존 bridge build helper를 그대로 사용한다.
- 원본/참고 EXE·DLL·assets, private game copy, close helper/runner, product resolution bytes,
  baseline/golden, 좌표/timeout은 변경하지 않는다. 새 dependency를 추가하지 않는다.
- 단순 상한 증가, overflow event/validator 억제, dropped count 0 위조, summary 합성은 금지한다.

### 필수 계약과 측정식

1. 고빈도 `surface_release`/`blt_fast` 등 method 호출은 고정 크기 메모리 안에서 연속 구간 또는
   검증 가능한 stable key로 집계한다. key에는 validator가 요구하는 object/interface/original pointer/
   present identity와 `program_state`, first/last tick·sequence 범위를 판별할 정보가 남아야 한다.
2. method별 total call count는 `detailed_count + aggregated_count + dropped_count`로 검산 가능해야 한다.
   정상 synthetic stress와 이후 fresh runtime의 PASS 조건은 `dropped_count=0`이며, 실제 용량 고갈은
   계속 명시적 overflow/BLOCKED다.
3. aggregation record는 count>0, 단조 first/last sequence·tick, 동일 run/PID와 허용된 key를 요구한다.
   key가 바뀐 호출을 한 묶음으로 합치거나 PS7 호출을 PS3 present로 재분류하면 FAIL이다.
4. summary는 method별 detailed/aggregated/total/dropped 수치와 전체 emitter 수치를 남긴다. validator는
   산술 불일치, 누락 identity, overflow, dropped>0, PS3 capture와 연결되지 않은 present를 BLOCKED한다.
5. synthetic 회귀는 정확히 256 경계와 그 이상, key/state/tick 전환, malformed aggregate, 실제 capacity
   exhaustion을 포함한다. 617행 historical shape는 fixture 출처/SHA를 명시해 회귀 입력으로만 사용한다.
6. 기존 install/typed-vtable/original-call/lifetime/close-finalization 계약은 바꾸지 않고 모두 회귀 PASS해야 한다.

### 검증 순서와 중단 조건

1. 변경 전 617행 artifact 수치와 현재 emitter/validator SHA를 다시 대조한다.
2. targeted synthetic tests를 먼저 추가하고 저장소 밖 새 `mktemp -d`에서 PE32 bridge를 build한다.
3. targeted tests, `make check`, `make doctor`, `bash checks/safety.sh check`를 실행한다.
4. 모두 PASS해도 이번 work lap에서는 게임 runtime을 실행하지 않고 새 Sol/high 독립 검수로 넘긴다.
5. lossless aggregation key를 현재 schema로 검증할 수 없거나 필수 gate가 예상 밖 실패하면 재시도하거나
   상한만 바꾸지 말고 변경·근거를 보존해 `loop/ESCALATE_SOL`을 만든다.

