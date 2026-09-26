# 2026-09-12 | lap 271 | 목표 G1 — offline 큐 Stage B 호출 경로 분류 (Astra 항목3)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high / **middle tier**
  (진단·계획·컨펌). 게임 코드 hands-on 수정 없음. 구현 없음. 자기 결과 최종 승인 없음.
- lap: `loop/.lap_counter` = **271**. runtime 안내는 lap=270이었으나 `loop/PROMPT.md`가
  카운터 파일을 권위로 정한다. lap270은 이미 middle 기록에 사용됐으므로 271을 쓴다.
- 가설 / 사용자 관찰: lap267 Astra 항목3은 "각 결함의 실제 Stage B producer/comparator 호출
  경로를 확인해 **필요한 항목만** 선행조건으로 분류하고, 역사 probe 전용 결함을 제품 게이트라고
  가정하지 말라"였다. 가설: offline 큐 9건 중 실제로 Stage B 판정을 바꾸는 것은 소수이며,
  나머지는 도달 불가 가드이거나 review 하네스 전용이다.
- 예상 PASS / FAIL 조건: 각 결함마다 (a) producer(`tools/runtime_env.py`) 또는
  comparator(`tools/compare_g1_stage_b.py`)의 실제 호출 경로에서 도달 가능한가, (b) 도달 시
  판정을 **PASS 쪽으로** 세탁하는가 아니면 FAIL/증거를 잃는가를 기계로 측정한다. 측정 없이
  기존 기록의 주장을 승격하지 않는다. 반대로 도달 가능성이 나오면 선행조건으로 승격한다.

## 변경 파일 / source fingerprint / 커밋

전부 uncommitted (`LOOP_ALLOW_COMMITS=0`, `git add`/push 없음). 신규 2 + 갱신 4.

| 파일 | sha256 |
|---|---|
| `docs/history/laps/probes/20260912_lap271_offline_queue_classification_probe.py` (신규) | `618d23dd8121c4b6dc09e8310e3ea2382fb706c0e5fcca99fea5f00c206e8c48` |
| `docs/history/laps/probes/20260912_lap271_offline_queue_classification_report.json` (신규) | `f1d7dc6b7daaa626172d67c65ae9da3324e8c8c302ab7028403b2f5479ffe969` |

갱신: 본 기록, `docs/work/active/G1_S1_DETERMINISM_RESEARCH_CONTRACT.md`(신규),
`docs/STATUS.md`, `loop/ESCALATE_SOL`. 제품/보호 자산은 하나도 건드리지 않았다.

검수 전후 불변을 확인한 지문(모두 lap270 기록과 바이트 일치):

| 파일 | sha256 |
|---|---|
| `tests/test_review_probe_output.py` | `862fd64a1e35eb14afe37dacefed6e1062b42a37bb622ea49c869de3129d3ea4` |
| `tools/runtime_env.py` | `e4f6a834f1ca591d2fe7acc1002beea4b343647d6ba47ff3b847f74e22455837` |
| `tools/compare_g1_stage_b.py` | `f57f5513b00262c0284a60be30b010575a81bc34be3f01eda89b3bc48f09b727` |
| `docs/history/laps/probes/20260912_lap228_r6b_r3_review_probe.py` | `16f74629aae8f823508762d719776547e1fd8365a07c7862bbf89a4d3ae06d12` |
| `docs/history/laps/probes/20260912_lap270_r30_review_probe.py` | `e7cd8593aa5f096eb67a782a37e99a9de1d720fd92f7676c395e79521eddfc89` |
| `docs/history/laps/probes/20260912_lap270_r30_review_report.json` | `aefd3d277d16368fbf31a69f39e01692264472858d03e7874ea77a3dd7a043a5` |

- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 EXE pin
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 무변경. **새 후보 SHA 없음.**
  게임/Wine/Xvfb/PNG **0회**, 활성 플레이어·지도·군대·fixture **없음**(문서/정적 분석 전용 바퀴).
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - `.venv/bin/python docs/history/laps/probes/20260912_lap271_offline_queue_classification_probe.py`
    → exit 0, 보고서 위 해시.
  - `make check` → `279 passed (43.72s)`, Ruff PASS, compileall PASS, mypy **10 source files** PASS,
    `CONTEXT_PASS`. 로그 `/tmp/lap271_check.log`(세션 임시, 수치는 본 기록이 권위).
  - `LOOP_DRY_RUN=0 bash checks/safety.sh check` → `SAFETY_PASS`.
  - 캡처 없음.

## 이전 바퀴(lap270) 독립 검수

lap270이 기록한 지문 5종을 재계산해 **전부 바이트 일치**했고(위 표), 이번 세션 전후로도 불변이다.
즉 lap270의 R30 검수 대상은 그 기록대로 보존돼 있다. 이번 바퀴는 lap270의 변이 행렬(M1~M11)을
재실행하지 않았다 — 상위 재결 대기 중인 R17 계열은 STATUS blocker가 착수를 금지하며, 이번
지정 작업이 아니다. **lap270의 "R30 범위 PASS / R17 계약 FAIL" 판정과 M11 생존은 그대로 유지**한다.

## 측정값 — 6축, 전부 이번 세션에서 독립 측정

**A1 (F2-R1 도달성).** `tools/compare_g1_stage_b.py`를 AST로 파싱해 `_stage_report` 호출을
전수 조사했다. **호출 1건**(`:357`), **위치 인자 5개** = `tag, baseline, candidate,
baseline_evidence, candidate_evidence`. 저장소 전체(.venv·docs/history 제외)에서 이 심볼을
참조하는 **외부 파일 0개**. 두 evidence 파라미터는 `None` 기본값을 가지지만 그 분기로 들어가는
경로가 없다. → **절대 slot/type 폴백은 현재 도달 불가 죽은 코드**다.

**A2 (F3-R1 도달성).** `tools/runtime_env.py`에서 `"last":` 키를 쓰는 지점은 **1곳**(`:2551`),
`record_timeout` 안이며 result로 `exc.classification`을 넘긴다. 즉 `after.last`를 가진 stage는
구조적으로 `result == "PASS"`가 될 수 없다. → **`after.last` 폴백도 현재 도달 불가**다.

**A3 (F3-R2 도달성) — 유일한 실측 도달 결함.** 실제 comparator에 합성 evidence 쌍을 넣었다.
후보의 minimap 카메라가 **실제로 움직이지 않은** 상태에서 producer가 실제로 flush 하는 결과
문자열을 넣으면:

| 후보 minimap `result` | stage | overall |
|---|---|---|
| `FAIL` (producer `runtime_env.py:2844`) | `UNKNOWN_DISPUTED_ORACLE` | `INCONCLUSIVE` |
| `BLOCKED`, `SKIP` | `UNKNOWN_DISPUTED_ORACLE` | `INCONCLUSIVE` |
| `FAIL_NO_EFFECT`, `UNKNOWN_BUDGET_EXHAUSTED`, `UNKNOWN_OBSERVATION_WINDOW_TRUNCATED`, `UNKNOWN_STATE_READ_FAILURE`, `UNKNOWN_SELECTION_OBSERVATION_CORRUPTED` | `UNKNOWN_DISPUTED_ORACLE` | `INCONCLUSIVE` |

선택 축도 같다: 후보 `unit_select.result == "FAIL"` → stage `UNKNOWN_DISPUTED_ORACLE` / overall
`INCONCLUSIVE`. 대조군(양쪽 PASS·일치)은 여전히 overall `PASS`이고, **새 PASS 경로는 0건**
(`new_pass_paths: []`)이다. 즉 F3-R2는 PASS 세탁이 아니라 **카드가 FAIL을 말할 능력의 상실**이다.
부수 발견: lap218 middle 재결이 열거한 disputed 3종은 **낡았다**. R12/R15/R25/R26/R27 이후
producer의 timeout classification은 최소 5종이며 `BLOCKED`/`SKIP`도 flush 된다. 수리 계약은
3종 리터럴이 아니라 현재 producer 집합에서 다시 유도해야 한다.

**A4 (R23/R24 소비자).** 두 게이트 도구(`compare_g1_stage_b.py`, `check_runtime_evidence.py`)에서
`read_coverage` **0/0**, `read_failure` **0/0**, `stage_budget_state` **0/0**. comparator의
`selection_count` 1건은 **자기가 details에 쓰는 키**이지 record 필드를 읽는 곳이 아니다
(`details["selection_count"] = {`, `"selection_count_delta": ...`). comparator가 실제로 읽는 것은
stage의 `before/after.selection.count`이며, 그 값이 없으면 stage/overall 모두 `INCONCLUSIVE`로
**fail-closed** 된다(실측). → R24의 "최상위 `selection_count`가 실패/미관측 모두 null"은 현재
어떤 판정도 PASS로 만들지 못한다.

**A5 (R21 제품 경로 여부).** producer의 `_write_json`은 `json.dumps(...)`로 **먼저 직렬화**한 뒤
`tmp.write_text(...)` → `tmp.replace(path)`로 원자 교체한다. `tools/` 전체에서 배타 생성
`open("x")`는 **0건**. → 절단 창은 제품 evidence 경로에 존재하지 않는다.

**A6 (하네스 국소성).** `open("x")` 27건, `M0_control` 24건이 모두 `docs/history/laps/probes/`
안에만 있고 `tools/` **0건**이다. (표의 tests 열 0은 문자열 검색 산물이며, R22는 정의상
`tests/` 안 취약성이다.)

## 판정 — offline 큐 분류 (Astra 항목3 답)

분류 기준(사전에 고정): **P**=실제 Stage B run의 판정을 잘못되게 하거나 판정 자체를 불가능하게
만든다 → 선행조건. **H**=Stage B 경로 위에 있으나 현재 producer 결합 때문에 도달 불가 → 가드
경화, 비차단. **C**=증거는 쓰이지만 어떤 게이트도 읽지 않는다 → 소비자 측 작업, 비차단.
**N**=review 하네스/테스트 전용 → **제품 게이트 아님**.

| 결함 | 분류 | 실측 근거 | Stage B 선행조건? |
|---|---|---|---|
| **F3-R2** | **P** | A3: 후보가 실제로 실패해도 카드가 `INCONCLUSIVE`만 낸다. `FAIL`/`BLOCKED`/`SKIP`+5종 전부 흡수 | **예 — 유일** |
| F2-R1 | H | A1: 호출 1건, 외부 참조 0, 폴백 분기 도달 불가 | 아니오 |
| F3-R1 | H | A2: `after.last` 기록 1곳, timeout 전용 → `PASS`와 공존 불가 | 아니오 |
| F6-R2 | H | flush 배선은 현재 두 producer(`:3397`, `:3867`) 모두 정상. 유실 시 `INCONCLUSIVE`로 닫힘 | 아니오 |
| R23 | C | A4: `read_coverage` 게이트 소비자 0 | 아니오 |
| R24 | C | A4: `read_failure` 소비자 0, 최상위 `selection_count`는 comparator가 읽지 않음, 결측은 fail-closed | 아니오 |
| R20 | N | A6: 미러 변이 하네스 전용, `tools/` 0건 | 아니오 |
| R21 | N | A5/A6: 제품 writer는 직렬화 선행 + 원자 교체. `open("x")`는 probe 규약에만 | 아니오 |
| R22 | N | `tests/` 내부 취약성. 제품 경로 없음 | 아니오 |

**결론: offline 큐 9건 중 Stage B 선행조건은 F3-R2 한 건뿐이다.** 나머지 8건은 주차하되
삭제하거나 PASS로 바꾸지 않는다(Astra 항목3 문구 그대로). H 3건은 "새 PASS 경로를 만들지
않는다"는 lap214 재결을 지키는 회귀 가드로서 가치가 있으나, Stage B 해금 전에 끝낼 필요는 없다.
C 2건은 해당 필드를 **판정에 쓰기로 결정한 뒤에만** 의미가 생긴다 — 그 결정은 상위 tier 소관이다.

이 판정은 **기계 1단 분류**이며, F3-R2 수리 자체의 범위 승인이 아니다(구현 전 work 계약 필요).
제품 G1 PASS도, 사용자 마일스톤 승인도 아니다. 프로세스 exit 0은 승인이 아니다.

## Astra 항목4 — S1 결정성 연구 계약

`docs/work/active/G1_S1_DETERMINISM_RESEARCH_CONTRACT.md`에 1쪽으로 초안했다. 요지: Stage B
fixture는 `tools/runtime_env.py:3548`이 스스로 기록하듯 *"default two-player random game; map
name/seed not exposed by approved read-only offsets"*이고 `replay_seed_observed=False`다(실측,
`:3551`/`:3919`). 계약은 work tier에게 **RNG 주소를 추측하지 말고**, 승인된 읽기 전용 오프셋과
기존 파일 근거만으로 "동일 초기 상태를 복원하는 지원 경로(저장/불러오기 또는 고정 시나리오)가
존재하는가"를 **존재 여부부터** 조사하게 한다. 없으면 정확한 누락 근거를 research blocker로
반환하는 것이 합격이다. 상세 성공/실패 측정식은 그 문서에 있다.

## 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태

- Fast/safety 회귀 없음(`279 passed`, `SAFETY_PASS`). 제품 증거 증가 **0**.
- 남은 위험 1: F3-R2 수리는 카드가 FAIL을 낼 수 있게 **판정력을 넓히는** 변경이다. 잘못 구현하면
  반대로 새 FAIL 오탐을 만들 수 있다. 그래서 구현 전에 범위 계약이 필요하고, lap218의 낡은 3종
  열거를 그대로 쓰면 안 된다(A3 부수 발견).
- 남은 위험 2: F3-R2를 고쳐도 **S1/F2-R2가 풀리지 않으면 Stage B는 여전히 실행 금지**다.
  이 분류는 "무엇이 선행조건인가"를 줄였을 뿐 Stage B를 해금하지 않는다.
- R17 계열(R19~R30, M11)과 S1/F2-R2/R6-B-R2는 **상위 재결 대기 그대로**다. 이번 바퀴는
  R31을 열지 않았고 어떤 미결도 닫지 않았다.
- 독립 검수 상태: 본 분류는 **다음 새 세션의 독립 검수 대상**이다. 자기 승인 없음.
  사용자 마일스톤 승인 없음.

## 다음 한 가지

**다음 work tier(Luna 또는 Sonnet5/high) — F3-R2 수리 1건.** 범위는
`docs/work/active/G1_S1_DETERMINISM_RESEARCH_CONTRACT.md`가 아니라 아래다:

1. `tools/compare_g1_stage_b.py:326`의 `disputed = any(result != "PASS")`를 **명시 열거**로 좁힌다.
   열거 집합은 lap218의 3종 리터럴이 아니라 **현재 producer가 실제로 flush 하는 timeout
   classification 집합**에서 유도하고, 그 유도 근거를 기록한다(오늘 실측: `FAIL_NO_EFFECT`,
   `UNKNOWN_BUDGET_EXHAUSTED`, `UNKNOWN_OBSERVATION_WINDOW_TRUNCATED`,
   `UNKNOWN_STATE_READ_FAILURE`, `UNKNOWN_SELECTION_OBSERVATION_CORRUPTED`).
2. 하드 `"FAIL"`은 카드 `FAIL`로 되돌린다. `"BLOCKED"`/`"SKIP"`/알 수 없는 문자열/`result` 키
   누락은 `INCONCLUSIVE`로 닫는다(기본값이 PASS가 되지 않게).
3. **새 PASS 경로를 0개 만든다.** 회귀는 (a) 각 분류마다 1건, (b) 하드 FAIL → 카드 FAIL,
   (c) 미지 문자열 → INCONCLUSIVE, (d) 기존 F1/F4/F5 fail-closed·scene gate·slot 강등 불변을
   고정하고 M0 대조군을 남긴다. 게임 실행 불필요.
4. F2-R1/F3-R1/F6-R2/R20~R24는 **건드리지 않는다**(H/C/N으로 주차). R31도 열지 않는다.

work가 끝나면 다음 새 middle 세션이 독립 검수한다. S1/F2-R2 상위 재결 전까지 Stage B·원본
재실행·Wine/Xvfb·R6-A/R6-C는 계속 금지다.
