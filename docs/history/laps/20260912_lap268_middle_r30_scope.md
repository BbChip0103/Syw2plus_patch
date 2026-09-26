# 2026-09-12 | lap 268 | G1 (R17 커버리지 계열) — R30 수리 범위·종료 기준 확정

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high / middle
  (진단·계획·확인). 구현 없음. 자기 계획 독립 승인 없음. 게임/Wine/Xvfb/PNG 0회.
- lap: 읽기 전용 `loop/.lap_counter` = **268**(runtime 안내 267과 다름). PROMPT 규칙대로 파일 값 사용.
- 목표: lap267 Astra 결정 계약을 검토해 **R30 한정 수리의 범위와 종료 기준을 확정**하고 work
  (Luna/high 또는 Sonnet5/high)에 인계한다. STATUS "다음 한 가지" 그대로.
- 가설: lap266이 미러에서 선측정한 변이 B(named review result 대입의 **합집합**)가 재현 가능하고,
  사살이 **R17 커버리지 단언**에 귀속되면 R30 범위를 승인할 수 있다.
- 예상 PASS / FAIL 조건: PASS = M0 `8 passed`, 생존자 정확히 `[M1]`, M2/M3/M6/M7/M8 사살이 모두
  R17 커버리지 단언 때문. FAIL = 어느 하나라도 재현 실패하거나 사살자가 완전성 self-check이면
  범위 승인 거부하고 상위 반환.

## 이전 바퀴(lap267 Astra) 독립 검수 — PASS

lap267은 문서 전용이었고 "파일·계약 대조, 변이 재실행 없음"이라고 스스로 적었다. 이번 세션이
재측정한 지문 6개가 기록과 **모두 일치**한다(무단 편집 없음):

- `tests/test_review_probe_output.py` `59538c0e1778b9c09ff6e83207123a89229f3001d351a873af2b194e72ec8957`
- SUT `docs/history/laps/probes/20260912_lap228_r6b_r3_review_probe.py`
  `16f74629aae8f823508762d719776547e1fd8365a07c7862bbf89a4d3ae06d12`
- `tools/runtime_env.py` `e4f6a834f1ca591d2fe7acc1002beea4b343647d6ba47ff3b847f74e22455837`
- lap266 증거 JSON 3개 `df45e459…`(R29 검수) / `21d4eaca…`(R30 변이 A) / `3b69345a…`(R30B)
- STATUS 117줄(상한 130), `## 지금 막힌 것` 정확히 1개, 카운터 파일 무변경(읽기만).

## 이번 세션의 독립 재측정 — lap266 R30B 행렬 재현 + 사살 귀속

`docs/history/laps/probes/20260912_lap268_r30_scope_probe.py`
(SHA256 `c983fdcf9f22477aabf63a37bcd7d85b8368327d236045bb8fd291afb47b7cd9`),
보고서 `..._lap268_r30_scope_report.json`
(SHA256 `a29ce69b925753e0a92980a3880bef5d771a19be3c7fe40b9400c538774a2c32`).
모든 변이는 /tmp 폐기 미러에서만 실행했고 저장소 파일은 변경하지 않았다.

lap266 대비 추가한 것은 **사살 이유 분류(`kill_reason`)**와 **변이 M9/M10**이다. lap266 보고서는
pass/fail 카운트만 남겨, 사살이 진짜 탐지(R17 커버리지 단언)인지 계약 self-check 실패인지
구분할 수 없었다. Astra lap267 항목1이 요구한 구분이 이것이다.

| 변이 | 결과 | kill_reason | 판정 |
|---|---|---|---|
| M0 대조군 | 8 passed | none | 재현 (오탐 0) |
| M1 개명-only(`drive_wait`) | 8 passed | none | 의도된 생존 재현 |
| M2 late refusal | 1 failed / 7 passed | **r17_coverage_assert** | 사살, 귀속 확인 |
| M3 late refusal + 개명 | 1 failed / 7 passed | **r17_coverage_assert** | 사살, 귀속 확인 |
| M6 전처리 tail 이동 + late refusal | 1 failed / 7 passed | **r17_coverage_assert** | 사살, 귀속 확인 |
| M7 전처리를 report write 위로 | 1 failed / 7 passed | **r17_coverage_assert** | 사살, 귀속 확인 |
| M8 decoy anchor(lap266 생존자) | 1 failed / 7 passed | **r17_coverage_assert** | **사살**, 귀속 확인 |
| **M9**(신규) review result 개명 `synthetic`→`synthetic_grid`, 결함 없음 | 1 failed / 7 passed | completeness_assert | **오탐(fail-closed)** |
| **M10**(신규) M9 ∘ late refusal | 1 failed / 7 passed | completeness_assert | 사살되나 **진단 이름이 틀림** |

생존자 = `[M1_rename_only]`로 lap266과 동일. 즉 변이 B는 재현되며, 다섯 결함 변이의 사살은 모두
실제 커버리지 단언이 한 것이고 완전성 self-check가 우연히 대신 죽인 것이 아니다.

**M9/M10이 새로 드러낸 비용.** 이름 튜플이 하드코딩이라 SUT의 review result 이름을 무해하게 바꾸면
테스트가 `missing review results`로 빨갛게 된다(M9). 실제 late refusal과 겹치면(M10) 테스트는
여전히 실패하지만 메시지는 원인을 잘못 지목한다. SUT는 SHA로 고정된 역사 증거라 정당한 개명은
발생할 수 없으므로 **fail-closed 오탐은 수용 가능하며 사실상 변조 탐지로도 동작한다**. 다만
work는 이 결합을 테스트 안에 명시해야 하고, 이름 부분집합만 확인하는 "best-effort" 형태로
완화하면 공허성이 되살아나므로 금지한다.

`_review_body_lines()` 소비자는 `tests/test_review_probe_output.py:227` **1개뿐**(정적 grep)이라
R17 단독 하중은 구조적으로 유지된다.

## 판정 — R30(변이 B) **범위 승인**, 구현은 work tier

middle은 구현하지 않는다. 아래 계약을 `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`
lap268 절에 인계했다. 승인 대상은 **수리 범위와 종료 기준**이며 R30 구현·제품 G1 증거·사용자
마일스톤 승인이 아니다. lap266의 R29 반려는 그대로 유지한다(되돌리지 않음).

- 허용 파일: `tests/test_review_probe_output.py` **단 하나**. SUT probe/보호 자산/다른 테스트 금지.
- 기각 확정: 변이 A(top-level 문 차집합). M0 대조군 `1 failed` 오탐 — 다시 시도 금지.
- 출하 조건: M0 `8 passed`; 생존자 정확히 `[M1]`; M2/M3/M6/M7/M8 각 `1 failed / 7 passed`이고
  **사살 이유가 R17 커버리지 단언으로 기록될 것**(카운트만으로 마감 금지); M9/M10은
  `completeness_assert`로 실패하는 것이 정상이며 그 사실을 테스트 주석과 기록에 남길 것;
  R17 제거 시 전 변이 생존; `make check` `279 passed` + ruff/compileall/mypy/CONTEXT/SAFETY PASS.
- 중단 조건(재시도 금지, 보존 후 ESCALATE): 위 수치가 재현되지 않음 / 사살자가 완전성 단언으로
  바뀜 / 수리에 SUT probe 변경이 필요하다는 결론 / 기존 R7/R10/R11/R15/R25/R26/R27 약화.
- 예산: 1바퀴, 게임·Wine·Xvfb·PNG 0, 커밋 0. 결과는 **다음 새 middle 세션이 독립 검수**한다.
- R30 승인 뒤 큐: offline(R20~R24/F2-R1/F3-R1/F3-R2/F6-R2) **자동 소진 금지**. 다음 middle의
  한 가지는 Astra 항목3(각 결함의 실제 Stage B producer/comparator 호출 경로 확인 후 선행조건
  분류)과 항목4(S1 결정성 조사 계약 1장) 설계다.

## 미결 보존 (상위 재결 대기, 이번 세션이 바꾸지 않음)

- **R6-B-R2** count 1→0 계약 충돌, **S1/F2-R2** 장면·slot 결정성, 후보 WM_CLOSE teardown.
- 제품 증거 증가 0. lap261~268 8바퀴 연속으로 역사 probe의 *테스트의 테스트*에 소비됐다는
  STATUS 경고는 유효하며 Astra 항목3/4가 그 출구다.

## 검증 / 기록

- 실행: `make check` → **279 passed (45.93s)**, Ruff PASS, compileall PASS, mypy 10 files PASS,
  `CONTEXT_PASS`; `LOOP_DRY_RUN=0 bash checks/safety.sh check` → **SAFETY_PASS**.
  로그 `/tmp/lap268_make_check.log`. 변이 행렬은 위 probe/report.
- 원본 EXE pin `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`. 새 후보 SHA 없음.
  게임/활성 인원/지도/군대/fixture/PNG 없음. Stage B 실행 없음. 패치 생성/원복 SKIP(문서·테스트 전용).
- 변경 파일(모두 uncommitted, `LOOP_ALLOW_COMMITS` 미설정): 본 기록,
  `docs/history/laps/probes/20260912_lap268_r30_scope_probe.py`, `..._lap268_r30_scope_report.json`,
  `docs/STATUS.md`, `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`, `loop/ESCALATE_SOL`.
- 다음 한 가지: **work tier가 R30(변이 B)을 위 계약대로 구현**하고, 그 결과를 다음 새 middle이
  독립 검수한다. 프로세스 exit 0은 승인도 제품 PASS도 아니다.
