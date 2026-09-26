# 2026-09-12 | lap 273 | 목표 G1 — lap272 F3-R2 수리 독립 검수 (middle)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5`/high / middle
  (진단·계획·컨펌). 게임 코드/도구 hands-on 수정 없음. 게임 실행 예산 0.
- 가설 / 사용자 관찰: lap272가 `_DISPUTED_SOURCE_RESULTS`를 **현재 producer 집합에서 유도**
  했는지 검증한다. `loop/ESCALATE_SOL`(lap271) 항목3의 side finding은 lap218의 3개 리터럴을
  베끼지 말고 현재 producer가 실제로 flush하는 분류에서 유도하라고 명시했다.
- 예상 PASS / FAIL 조건:
  - PASS-1 새 PASS 경로 0개 (source result 교차곱 전수 탐색).
  - PASS-2 하드 `FAIL` → stage/overall `FAIL`, disputed 동석 시에도 `FAIL` 우선.
  - PASS-3 `BLOCKED`/`SKIP`/미지 문자열/`result` 결측 → `INCONCLUSIVE`.
  - PASS-4 M0 정상 pair PASS, scene gate/slot 강등/production NOT_COMPARED 불변.
  - PASS-5 comparator의 disputed 집합 == producer가 실제로 내는 timeout 분류 집합.
  - 하나라도 어긋나면 해당 항목 FAIL.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  제품/도구 파일 **무변경**. 검수 후 재측정한 지문이 lap272 선언과 바이트 일치:
  `tools/compare_g1_stage_b.py` `68994909d59be1c00fa7eef0b1b209b479d63404b9749cb8a766381b3522e525`,
  `tests/test_compare_g1_stage_b.py` `9e80626253921f6739a1f015a3deaadc0631092a5e0f9844b0d7d38c3358cfd5`,
  `tools/runtime_env.py` `e4f6a834f1ca591d2fe7acc1002beea4b343647d6ba47ff3b847f74e22455837`.
  신규(기록 전용): probe `docs/history/laps/probes/20260912_lap273_middle_f3_r2_review_probe.py`
  SHA256 `9140aea261468e9b2cc038a93578e2e8bd613c17ea81feffe1862a4e8a821757`,
  report `..._review_report.json` SHA256
  `d2ef89a527494b7d63353ae43e601e31a03237ef9795c00c313064b5d8f57d9b`.
  STATUS 압축 원문 `docs/history/laps/20260912_status_lap273_compaction.md`
  SHA256 `8b6aff3867c3f5a8e436f39277ccd0f81542c950be60d8d54f4e7c78e4fca547`
  (원문 SHA256 `355219b9804302d607ab449c1b2989f6dd2fbe6f3779c635fb7fd205e7cbbee3`, 130줄).
  커밋 없음(`LOOP_ALLOW_COMMITS=0`), uncommitted 보존.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 EXE pin
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 조회값 유지, 후보 없음.
  Linux/.venv offline synthetic evidence fixture만 사용(probe 안에서 직접 구성, lap272 테스트
  fixture를 import하지 않음). 게임/Wine/Xvfb/PNG/캡처 **0회**, 활성 플레이어·지도·군대 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - `.venv/bin/python docs/history/laps/probes/20260912_lap273_middle_f3_r2_review_probe.py`
    → exit 0, 위 report JSON.
  - `.venv/bin/python -m pytest -q tests/test_compare_g1_stage_b.py` → `24 passed`
    (lap272 선언값과 일치).
  - `make check` → `289 passed (43.98s)`, Ruff PASS, compileall PASS, mypy 10 files PASS,
    `CONTEXT_PASS`, `MAKE_EXIT=0`.
  - `LOOP_DRY_RUN=0 bash checks/safety.sh check` → `SAFETY_PASS`, `SAFETY_EXIT=0`. 캡처 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **A1 어휘 유도 (FAIL).** probe가 `tools/runtime_env.py`를 AST로 읽어 `^(FAIL|UNKNOWN)_[A-Z0-9_]+$`
    형태의 분류 리터럴을 독립 추출했다. producer는 **6종**을 낸다:
    `UNKNOWN_BUDGET_EXHAUSTED`(:3259), `UNKNOWN_OBSERVATION_WINDOW_TRUNCATED`(:3260),
    `UNKNOWN_STATE_READ_FAILURE`(:3261, :2183), **`UNKNOWN_STATE_READ_COVERAGE`(:3262)**,
    `UNKNOWN_SELECTION_OBSERVATION_CORRUPTED`(:3263), `FAIL_NO_EFFECT`(:3264).
    comparator의 `_DISPUTED_SOURCE_RESULTS`는 **5종**이고 `UNKNOWN_STATE_READ_COVERAGE`가 빠졌다.
    `declared_but_not_in_producer`는 0건이다. comparator 주석이 근거로 적은
    `runtime_env.py:3258-3264` 범위가 바로 6종을 담은 삼항식이라 주석과 집합이 서로 모순된다.
    이 분류는 실재하며 `tests/test_runtime_env.py:2551`이 직접 단언한다(R8 계열, lap237/238).
  - **A2 행렬 (선언 5종 PASS / 6번째 FAIL).** 3개 stage × 11개 result 값 = 33칸을 측정했다.
    timeout 5종은 전부 stage `UNKNOWN_DISPUTED_ORACLE`/overall `INCONCLUSIVE`,
    하드 `FAIL`은 stage/overall `FAIL`, `BLOCKED`/`SKIP`/`WAT_UNRECOGNIZED`/`result` 결측은
    stage/overall `INCONCLUSIVE`. **`UNKNOWN_STATE_READ_COVERAGE`만 stage `INCONCLUSIVE`**이며
    reason은 `"source input stage result is missing or unrecognized"`다. 즉 측정·회귀된 실제
    timeout을 "미지/결측"으로 오분류한다.
  - **A3 새 PASS 경로 0 (PASS).** 어휘 10종을 baseline×candidate 교차곱(100) × 3 stage = 300칸
    전수 탐색. overall PASS는 **3건뿐이고 전부 baseline=candidate=`PASS`**다.
    `pass_with_any_non_PASS_source: []`. PASS 세탁은 없다.
  - **A4 FAIL 우선순위 (PASS).** baseline=`UNKNOWN_BUDGET_EXHAUSTED`, candidate=`FAIL`을
    같은 stage에 넣어도 stage/overall `FAIL`. 하드 FAIL이 disputed에 흡수되지 않는다.
  - **A5 실제로 깨진 후보 (PASS, 단 disputed 우선 규칙 확인).** 후보 미니맵 카메라가 움직이지
    않은 pair에서 source `PASS`→`FAIL`/`FAIL`, source `FAIL`→`FAIL`/`FAIL`,
    source `FAIL_NO_EFFECT`→`UNKNOWN_DISPUTED_ORACLE`/`INCONCLUSIVE`. 마지막은 설계상
    의도(관측 자체가 분쟁 중)이며 새 결함이 아니다. 판정 순서는 hard FAIL > disputed > 미지 >
    checks로 코드 :335-:367과 일치한다.
  - **A6 불변 (PASS).** scene 불일치 → overall/stage `UNKNOWN_SCENE_MISMATCH`,
    slot 강등 → overall `INCONCLUSIVE`/stage `UNKNOWN_SLOT_CORRESPONDENCE`,
    production `NOT_COMPARED`. F1/F4/F5·M0 정상 pair PASS 유지.
  - **최종 판정: 선언 범위 PASS / F3-R2 계약 종결 FAIL.** lap272가 스스로 적은 "timeout 5종"
    범위 안에서는 모든 항목이 성립한다. 그러나 `loop/ESCALATE_SOL`이 못 박은 "현재 producer
    집합에서 유도"는 충족하지 못했다(6종 중 1종 누락). 이는 lap218의 3개 리터럴을 베낀 것과
    **같은 계열의 오류가 한 단계 위에서 반복된 것**이다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - 심각도는 **판정값이 아니라 진단 라벨**에 있다. `UNKNOWN_STATE_READ_COVERAGE`가 빠져도
    카드 overall은 양쪽 다 `INCONCLUSIVE`라 PASS 세탁도 FAIL 상실도 아니다(A2/A3 실측).
    그러나 사람과 다음 세션은 stage status/reason을 읽고 "관측 분쟁 → bounded repair"인지
    "증거 형식 오류 → producer 수리"인지를 가른다. 지금은 R8이 낸 실제 읽기 커버리지 부족이
    "unrecognized"로 보고되어 잘못된 수리 대상으로 라우팅된다.
  - 회귀 테스트도 같은 5종만 덮는다. 6번째 분류에 대한 단언이 없어 이 누락은 `make check`로
    영영 잡히지 않는다. 수리 시 회귀와 **유도 근거 기록**을 같이 요구한다.
  - middle 자기 승인 아님, 사용자 마일스톤 승인 아님, 제품 G1 증거 아님.
  - S1/F2-R2 미해결이므로 Stage B fresh run은 계속 금지. R17 계열/R31, R6-B-R2,
    F2-R1/F3-R1/F6-R2, R20~R24는 이 바퀴에서 건드리지 않았다.
- 다음 한 가지: **work(Luna 또는 Sonnet5/high)** — F3-R2-R1 수리 1건, 게임 실행 0.
  `_DISPUTED_SOURCE_RESULTS`에 `UNKNOWN_STATE_READ_COVERAGE`를 넣되, **리터럴을 베끼지 말고**
  producer에서 유도한 근거(파일·줄·유도 방법)를 주석과 lap 기록에 남긴다. 6종 각각과 하드
  `FAIL`·`BLOCKED`·`SKIP`·미지·결측에 대한 회귀를 추가하고, 새 PASS 경로 0을 재확인한다.
  집합이 producer와 어긋나면 깨지는 형태의 회귀(예: producer에서 유도한 집합과의 대조)를
  권장하되 SHA 고정 SUT 결합은 금지한다(R29/R30 교훈). 그 뒤 다음 새 middle이 독립 검수한다.
