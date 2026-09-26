# 2026-09-12 | lap 270 | 목표 G1 (R17 커버리지 계약) — R30 독립 검수

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high, middle tier
  (진단·계획·컨펌). 게임 코드 hands-on 수정 없음. SUT·보호 자산 불변.
- 가설 / 사용자 관찰: lap269 work가 구현한 R30(변이 B = named review result 대입의 합집합)이
  lap266/lap268이 정한 ship 조건을 실제로 충족하는지, 그리고 R17 커버리지 단언이 비공허하게
  하중을 지는지를 새 세션에서 독립 확인한다.
- 예상 PASS / FAIL 조건: (1) mirror M0 = 실저장소 결과, (2) 생존자 정확히 `[M1_rename_only]`,
  (3) M2/M3/M6/M7/M8 사살 이유 전부 `r17_coverage_assert`, M9/M10은 `completeness_assert`,
  (4) R17 단언 제거 시 M2/M3/M6/M7/M8 전부 부활(=R17 단독 사살자),
  (5) 정상 run에서 body 줄이 실제 실행됨(비공허), 거부 run에서 0줄, (6) Fast 게이트 전부 PASS.
- 변경 파일 / source fingerprint / 커밋: 신규 `docs/history/laps/probes/20260912_lap270_r30_review_probe.py`
  SHA256 `e7cd8593aa5f096eb67a782a37e99a9de1d720fd92f7676c395e79521eddfc89`, 신규
  `..._lap270_r30_review_report.json` SHA256
  `aefd3d277d16368fbf31a69f39e01692264472858d03e7874ea77a3dd7a043a5`, 그리고 `docs/STATUS.md`,
  `loop/ESCALATE_SOL`, 본 기록. 검수 대상은 변경하지 않았다:
  `tests/test_review_probe_output.py` = `862fd64a...29d3ea4` (lap269 기록값과 동일),
  `tools/runtime_env.py` = `e4f6a834...4f22455837`, SUT probe
  `20260912_lap228_r6b_r3_review_probe.py` = `16f74629...bbf89a4d3ae06d12`. uncommitted, 커밋 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 EXE pin
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` (조회만). 후보 SHA 없음.
  Linux/.venv, 게임·Wine·Xvfb·PNG 0회, 플레이어·지도·군대 없음. 모든 변이는 throwaway `/tmp` 미러.
- 실행 명령 / 로그:
  - C0 `.venv/bin/python -m pytest -q tests/test_review_probe_output.py` → `8 passed`.
  - C1 저장소 helper를 직접 import해 body/trace 측정.
  - C2~C5 `.venv/bin/python docs/history/laps/probes/20260912_lap270_r30_review_probe.py`.
  - `make check` → `279 passed (45.47s)`, Ruff `All checks passed!`, compileall,
    mypy `10 source files` Success, `CONTEXT_PASS`.
  - `LOOP_DRY_RUN=0 bash checks/safety.sh check` → `SAFETY_PASS`.
- 측정값 / 판정:
  - **C1 비공허성(신규 측정, lap269가 기록하지 않은 값).** body = **81줄**
    (137~148, 197~204, 217~227, 261, 283~292, 365~385, 393~409, 412).
    정상 run: 268줄 실행, 그중 **body 58줄 실행**. 거부 run: 48줄 실행, **body 0줄**, 최대 실행 줄 128.
    → `assert not (body & seen)`는 baseline에서 실질 하중 58줄을 진다. R29(276줄 구간 중 5줄로 붕괴)
    대비 구조적으로 개선됐다.
  - **C2** mirror `M0_control` `8 passed` = 실저장소 `8 passed`. 미러 충실.
  - **C3 변이 행렬(저장소 테스트 파일 그대로, helper swap 없음)**: M0 `8 passed`;
    생존자 `[M1_rename_only, M11_...]`; M2/M3/M6/M7/M8 각 `1 failed / 7 passed`이며
    사살 이유 5종 모두 `r17_coverage_assert`; M9/M10 각 `1 failed / 7 passed`,
    이유 `completeness_assert`. **M1~M10 범위에서 lap269 선언값과 완전히 일치**.
  - **C4 귀속**: 테스트에서 `assert not (_review_body_lines() & seen)` 한 줄만 삭제하면
    M2/M3/M6/M7/M8이 전부 `8 passed`로 부활한다(M0도 `8 passed`).
    → R17이 **단독** 사살자이고, R7/R10/R11/R15/R25/R26/R27은 약화되지 않았다.
  - **C5 신규 반례 M11 — 승인 범위 밖, 생존.** M8은 review result *한 개*만 별칭으로 돌렸다.
    M11은 7개 전부를 `_SRC_<name>`으로 계산하고, preflight 거부 블록을 report write 바로 위로
    옮긴 뒤 그 아래에서 canonical 이름 7개를 재바인딩한다. 결과 `8 passed` **생존**.
    거부 run 측정: 반환코드 2·거부 메시지 정상이지만 **260줄이 거부 전에 실행**된다
    (baseline 48줄, 최대 실행 줄 407). 이때 R30 body는 81줄 → **8줄**(재바인딩 7 + report write)로
    줄고 그 8줄은 전부 거부 아래에 있어 교집합이 다시 공허해진다.
    즉 R17이 막으려는 late-refusal 결함이 실제로 성립하는데 테스트는 통과한다.
  - **근본 원인(R19→R28→R29→R30 공통)**: body 집합을 *변이 대상 파일 자신의 구문*에서 유도한다.
    R30의 합집합은 "이동 가능한 첫 앵커" 결함은 닫았으나 "앵커가 공격자 제어" 결함은 닫지 못한다.
    앵커를 몇 개로 늘리든 같은 형태의 다음 반례가 존재한다(고정점 없음).
  - **판정: R30 = 선언 범위 PASS / R17 계약 종결 FAIL.**
    lap266이 명시한 ship 조건(정확한 수치, R17 단독 사살자, `make check` 279 passed,
    SUT·보호 자산 불변)은 **전부 충족**하므로 lap269 work의 납품은 승인한다(기계 1단 범위 승인).
    그러나 M11 때문에 "출력 preflight 거부가 review 본문보다 먼저"라는 R17 계약이 보장된다고는
    승인하지 않는다. 이것은 work tier의 이행 실패가 아니라 접근법 자체의 한계다.
  - 나는 R31을 열지 않는다. lap261~270 10바퀴 연속 제품 증거 0이며, 같은 계열의 11번째 바퀴를
    이 tier가 독단으로 시작하는 것은 STATUS의 상위 재결 대기 blocker를 우회하는 것이다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 기존 R7/R10/R11/R15/R25/R26/R27 회귀는 C4로
  무손상 확인. M9/M10 개명 fail-closed는 lap268이 수용한 위험으로 유지(완화 금지).
  R29 범위 승인 거부(lap266)는 계속 유효하다. 제품 G1 승인도 사용자 마일스톤 승인도 아니다.
  S1/F2-R2, R6-B-R2, WM_CLOSE teardown, Stage B는 미해결/금지 상태 그대로다.
- 상위 재결에 올리는 제안(이 tier가 결정하지 않음): SUT는 SHA가 고정된 **불변 역사 증거 파일**이다
  (`16f74629...`). 따라서 계약을 파일 내용에서 유도하지 말고 (a) SUT SHA를 단언한 뒤
  **절대 줄 번호를 하드코딩**하거나, (b) 줄 커버리지 대신 관측 가능한 부작용
  (거부 전 `observe_raw`/`rt._g1_selection_responded` 호출 0회 등)을 단언하도록 계열 전체를
  바꾸는 선택지가 있다. (a)는 파일이 불변이므로 공격자 제어 앵커 문제를 원천 제거한다.
  어느 쪽이든 R19~R30 계열을 1회로 종결하는 구조 변경이라 Astra/사용자 재결이 필요하다.
- 다음 한 가지: 다음 middle 세션은 R31을 열지 말고 **Astra 항목3/4**(offline 큐 결함을 실제
  Stage B producer/comparator 호출 경로로 분류 + S1 결정성 연구 계약 1쪽 초안)를 먼저 수행한다.
  R17 계열의 구조 변경은 위 제안에 대한 상위 재결 이후에만 착수한다.

## 최종 문서 provenance (lap270 종료 시점)

- `docs/STATUS.md` SHA256 `c37944cbf13b5068d4e2aa2ea524f5f4183bc94f903d5ac1d13d6bfa8d61d4a1`, 127줄.
- `loop/ESCALATE_SOL` SHA256 `d31954d4094bfb39a3650c73cba0460269e8d96874c72cfbadf621eadf12b633`
  (lap270 블록을 앞에 덧붙였고 lap268 이하 원문은 그대로 보존).
- 검수 대상은 검수 전후 불변: test `862fd64a…`, SUT probe `16f74629…`, runtime_env `e4f6a834…`.
- 문서 편집 후 재실행: `make check` 279 passed, Ruff/compileall/mypy 10 files, `CONTEXT_PASS`,
  `SAFETY_PASS`. `LOOP_ALLOW_COMMITS` 미설정이므로 커밋 없음(uncommitted 보존).
