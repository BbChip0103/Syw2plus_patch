# 2026-09-12 | lap 275 | 목표 G1 — F3-R2-R1 독립 검수 (middle)

- 실제 provider/model/effort / 지정 역할: middle — Claude Code `claude-opus-5`/high.
  진단·계획·확인만 수행했고 게임 코드/comparator/producer/테스트를 수정하지 않았다.
- 가설 / 검수 대상: lap274 work가 comparator `_DISPUTED_SOURCE_RESULTS`에
  `UNKNOWN_STATE_READ_COVERAGE`를 보완해 producer 6종과 일치시켰고, AST 드리프트 회귀를
  추가했다고 주장했다. 이 주장을 lap274 테스트를 **재사용하지 않고** 독립 유도로 확인한다.
- 예상 PASS / FAIL 조건: (A) 자체 AST 유도 집합 == comparator 선언, 양방향 차 0, 6종.
  (B) classification이 comparator가 읽는 `inputs[i]["result"]`에 실제로 도달.
  (C) 확장 어휘 전수 행렬에서 hard `FAIL` 우선 > disputed > PASS/INCONCLUSIVE 계약 성립.
  (D) 새 PASS 경로 0. (E) scene gate·slot 강등·production `NOT_COMPARED`·결측 키 불변.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  신규 `docs/history/laps/probes/20260912_lap275_middle_f3_r2_r1_review_probe.py`
  SHA256 `3f2d886a93c12133a6ac264be45d899ecbecc5b8bcc342192daa4eca78220f97`.
  검수 대상은 불변 확인만 했다: producer `tools/runtime_env.py`
  `e4f6a834f1ca591d2fe7acc1002beea4b343647d6ba47ff3b847f74e22455837`,
  comparator `tools/compare_g1_stage_b.py`
  `9b684cec7b9fd284aed88e9c063e903c6fcd7322946bee6644541f32e426efdb`,
  tests `tests/test_compare_g1_stage_b.py`
  `74b7d337d1aae6ab11d12528b012ffb31a1a94f2840108066bb806de2a3d2991`.
  세 해시 모두 lap274 기록값과 일치한다. `LOOP_ALLOW_COMMITS=0`, 커밋 없음, 미커밋 보존.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 EXE pin
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변.
  Linux/.venv offline synthetic fixture만 사용. 게임/Wine/Xvfb/PNG/실제 플레이어·지도·군대 0회.
  변이 실험은 `/tmp/lap275_mut/` 사본에서만 했고 저장소 파일은 손대지 않았다(사후 해시 재확인).
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - `.venv/bin/python docs/history/laps/probes/20260912_lap275_middle_f3_r2_r1_review_probe.py`
    → exit 0, `verdict=PASS`, failures 0. 출력 `/tmp/lap275_review.json`.
  - `.venv/bin/python -m pytest -q tests/test_compare_g1_stage_b.py` → `26 passed`.
  - `make check` → `291 passed (44.66s)`, Ruff/compileall/mypy 10 files, `CONTEXT_PASS`.
  - `LOOP_DRY_RUN=0 bash checks/safety.sh check` → `SAFETY_PASS`. 캡처 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **F3-R2-R1 선언 범위 PASS — 범위 승인.**
  - A. 이 세션이 새로 쓴 추출기는 lap274 테스트와 **스코프 규칙이 다르다**(lap274=함수
    화이트리스트 `{_g1_read_selection_stage,_wait_state}` + `^(FAIL|UNKNOWN)_[A-Z0-9_]+$` 정규식,
    lap275=파일 전체에서 `classification=` 키워드 인자와 `classification = <IfExp>` 대입의
    리터럴). 두 독립 유도가 같은 6종을 낸다: `FAIL_NO_EFFECT`, `UNKNOWN_BUDGET_EXHAUSTED`,
    `UNKNOWN_OBSERVATION_WINDOW_TRUNCATED`, `UNKNOWN_SELECTION_OBSERVATION_CORRUPTED`,
    `UNKNOWN_STATE_READ_COVERAGE`, `UNKNOWN_STATE_READ_FAILURE`. producer_only 0, comparator_only 0.
  - B. **신규 확인(이전 바퀴가 명시 검증하지 않은 연결고리).** `record_timeout`이
    `exc.classification`을 `record(...)`의 9번째 위치인자 `result`로 넘기고
    `_g1_record_input`이 그것을 `entry["result"]`에 넣는다. comparator가 읽는
    `baseline.get("result")`와 동일 필드다. 어휘 일치가 공회전이 아님을 확인했다.
  - C. 확장 어휘 13종(6종 + `PASS`/`FAIL`/`BLOCKED`/`SKIP`/미지 문자열/`None`/비문자열)
    × 13종 = **169칸 전수**에서 stage 상태가 계약과 100% 일치. hard `FAIL`이 disputed보다
    우선(25칸), disputed 잔여(120칸), (PASS,PASS) 1칸, 나머지 23칸 `INCONCLUSIVE`.
  - D. stage `PASS`는 `[("PASS","PASS")]` 단 1쌍. overall `PASS`도 같은 1칸뿐. 새 PASS 경로 0.
  - E. 결측 `result` 키 3종 모두 stage/overall `INCONCLUSIVE`. scene mismatch는 hard FAIL
    입력에서도 stage/overall을 `UNKNOWN_SCENE_MISMATCH`로 덮는다. slot만 다른 all-PASS 쌍은
    `UNKNOWN_SLOT_CORRESPONDENCE`/overall `INCONCLUSIVE`로 강등된다. production은 169칸
    전부 `NOT_COMPARED`. M0 동일 증거 대조는 `PASS`.
  - 변이 귀속(`/tmp/lap275_mut/` 사본): **M-a** producer에 7번째 분류 추가 → `1 failed/25 passed`
    (드리프트 회귀만 사살). **M-b** comparator에서 `UNKNOWN_STATE_READ_COVERAGE` 제거
    (= lap273 수리 전 상태) → `1 failed/25 passed`. **M-c** 직접 raise의
    `UNKNOWN_STATE_READ_FAILURE` 개명 → `1 failed/25 passed`. 회귀는 SHA 비고정이며 실제
    사살자다. 복원 후 `26 passed`, 사본 해시가 원본과 일치.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  **알려진 사각 2건(블로커 아님, 신규 계열 착수 금지).** lap274 회귀의 추출기는 선언 범위
  밖에서 다음을 놓친다. 사본 변이로 확인:
  - **M-d** `_G1WaitTimeout`을 **세 번째 함수**에서 새 분류로 raise → `26 passed`로 생존.
    원인은 하드코딩된 함수 화이트리스트다.
  - **M-e** `_wait_state` 안이라도 `FAIL_`/`UNKNOWN_` 접두어가 아닌 분류명(`TIMEOUT_...`)
    → `26 passed`로 생존. 원인은 정규식 접두어 가정이다.
  둘 다 **미래 드리프트** 위험이며 현재 producer 상태의 결함은 아니다. 현재 producer는
  두 경로·6종이 전부이고 그 집합은 일치한다. 알려진 1줄급 수정 방향은 추출기를
  `classification=` 키워드 인자 기준(함수/접두어 비의존)으로 바꾸는 것이며, 이는 lap270이
  상위로 올린 R17 계열 *테스트의 테스트* 구조 문제와 같은 모양이다. **재결 전 착수 금지**
  규칙을 지켜 이 바퀴는 기록만 하고 R31/신규 수리를 열지 않았다.
  원본·보호 자산·producer 바이트 불변. 사용자 마일스톤 승인 없음. 제품 G1 증거 아님.
- 다음 한 가지: offline 큐의 유일한 Stage B 선행조건이던 F3-R2가 닫혔다. 남은 8건은 lap271
  분류대로 도달 불가 가드/소비자 0/하네스 전용이라 Stage B를 열지 못한다. 따라서 **다음 실무
  작업 후보가 없고** 상위 재결(S1/F2-R2 결정성, R17 구조 3안, S1 연구 계약 실행 예산)이
  유일한 경로다. `loop/ESCALATE_SOL`에 lap275 항목으로 승격했다.
