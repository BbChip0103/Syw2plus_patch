# 2026-09-12 | lap 252 | 목표 G1 Stage B — R6-B-R14 독립 검수 (middle)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5`/high, middle tier
  (진단·계획·컨펌). 게임 코드 hands-on 수정 없음. SUT는 읽기 전용으로만 다뤘다.
- 가설 / 사용자 관찰: lap251은 production 직접 selection read 실패 시 nested
  `before/after.selection`에 `status="UNAVAILABLE"`, `count=null`, `read_failure=true`가
  남고 정상 read에는 표식이 없으며, production은 `BLOCKED`/click 미호출/effect wait 미진입,
  후속 drag/minimap 진행과 기존 `selection_read_failure` provenance가 보존된다고 주장했다.
  근거는 "targeted 4 passed" + Fast 274뿐이라 (a) 표식이 실제로 load-bearing인지, (b) production
  이외 단계로 새지 않는지, (c) failure-only 조건이 회귀로 고정됐는지는 증명되지 않았다.
- 예상 PASS / FAIL 조건: (C0) 출하된 R14 4건이 실제 저장소에서 통과. (C1) 독립 하네스로
  모든 selection read point(직접6 + poll2 + 무결1 = 9 case)를 구동해 계약에서 직접 쓴 기대 모델과
  0 불일치, 특히 production 지점에서만 표식이 나타나고 다른 지점에서는 전혀 나타나지 않을 것.
  (C2) 깊이 일치 미러의 무변이 M0 대조군이 실제 저장소 결과와 동일할 것(lap246 R20 교훈).
  (C3) 변이 5종이 각각 출하 테스트를 최소 1건 죽이고 R14 범위 밖은 0건일 것. 하나라도 어긋나면
  R14 middle **FAIL**로 기록한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): SUT 변경 0.
  검수 전후 동일: `tools/runtime_env.py` sha256
  `2819da727c11acf360c89dff8792abbb62a96f8d5a2a8b554aa9991c1e204bf3`,
  `tests/test_runtime_env.py` sha256
  `adac1297571a0b62ccd7d5c606a5855d386b15e25ad423e95208df018223f1f4`.
  신규 검수 산출물(uncommitted, `LOOP_ALLOW_COMMITS=0`):
  `docs/history/laps/probes/20260912_lap252_r14_review_probe.py` sha256
  `2e3f0728de82234f2864d493b2f77fb662e5c895c12ebee2c7d93b8e034bcdf9`,
  `docs/history/laps/probes/20260912_lap252_r14_review_report.json` sha256
  `80f12ff291f7248fbe3dd1e292fafdfdea8411cfba7f65da72bd48b06e627e87`.
  기록 문서: `docs/STATUS.md`, `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`,
  `loop/ESCALATE_SOL`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 EXE pin
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변; 제품 EXE/DLL/assets/
  baseline/golden 변경 0. Python 3.13.5/.venv, 순수 Python fake-clock 하네스.
  실제 게임/Wine/Xvfb/PNG 실행 **0회**, 플레이어·지도·군대 N/A.
  하네스 fixture는 lap251 테스트 헬퍼를 재사용하지 않고 새로 작성했다. 선택 상태를 **read 카운터가
  아니라 click/drag 스텁**이 전진시키므로 실패 주입 위치가 이후 관측값을 밀지 않는다(출하 헬퍼의
  `counts` 튜플 결합을 의도적으로 상속하지 않음).
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `.venv/bin/python docs/history/laps/probes/20260912_lap252_r14_review_probe.py --output
  docs/history/laps/probes/20260912_lap252_r14_review_report.json` → overall **PASS**.
  `.venv/bin/python -m pytest -q tests/test_runtime_env.py` = **139 passed**.
  `make check` = **274 passed**, Ruff/compileall/mypy 10 files, `CONTEXT_PASS`.
  `LOOP_DRY_RUN=0 bash checks/safety.sh check` = **SAFETY_PASS**. PNG/capture 경로 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): R14 middle 독립 검수 **PASS(범위 승인)**.
  - C0 baseline: 출하 R14 4건 = **4 passed / 135 deselected**.
  - C1 독립 행렬: 9 case(무결1, 직접 read point6, poll2) **불일치 0**.
    `production/before_production`에서만 before/after 양쪽에 `read_failure=true`,
    `status="UNAVAILABLE"`, `count=null`이 나타났고 `selection_read_failure.direct_read_point`
    = `before_production`, result=`BLOCKED`, waited=`False`, (670,490) 클릭 0회,
    tags=`[unit_select, production, drag_select, minimap]`, clicks=`[(410,270),(150,520)]`,
    drags=`[(350,180,550,350)]`였다. 나머지 8 case에서 표식은 **전 단계 0건**이며,
    poll 지점 읽기 실패는 wait가 흡수해 전체 run이 정상 완료됐다(표식 없음).
  - C1b 소비자 스캔: `tools/**`·`checks/**`에서 `read_failure`를 읽는 코드 **0개**(R23과 동종).
  - C2 미러 M0 대조군: 깊이 일치 미러 **139 passed**, 실제 저장소 **139 passed**로 동일.
  - C3 변이 5종: 각 1~2건 사살, **범위 밖 0건**.
    M1 표식 제거 → `..._mark_direct_read_failure_unavailable`;
    M2 무조건 표식 → `..._snapshot_has_no_failure_marker_on_success`;
    M3 `count`를 0으로 → `..._mark_direct_read_failure_unavailable`;
    M4 stage provenance 제거 → `..._stays_blocked_and_continues`;
    M5 실패 재-raise → 위 두 건 동시 사살.
  - probe 가드 실측: 기존 출력 경로 → exit 2, `/proc/nope/x.json`(부모 비디렉터리) → exit 2,
    dangling symlink 경로 → exit 2이며 symlink 대상 파일은 생성되지 않았다(R7/R10/R11).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 이번 판정은 1단 기계 검수의 **범위 승인**이며
  제품 G1 합격이나 사용자 마일스톤 승인이 아니다. 남은 위험:
  - **R24(신규 큐)**: `read_failure`를 읽는 소비자가 `tools/runtime_env.py` 밖에 0개다.
    `check_runtime_evidence.py`/`compare_g1_stage_b.py` 어느 쪽도 소비하지 않으므로 R14는 아직
    아무 게이트도 읽지 않는 증거를 쓴다. 더불어 record 최상위 `selection_count`는 실패/미관측
    양쪽 모두 `null`이라, 표식을 읽지 않는 소비자에게는 여전히 구별되지 않는다. R23과 동종이다.
  - M1/M3가 같은 단일 테스트에 걸리지만 두 변이 모두 같은 nested dict schema를 공격하므로
    R22와 달리 별개 성질이 한 테스트에 얹힌 경우로 보지 않는다. 기록만 남긴다.
  - S1/F2-R2, R6-B-R2, R15/R19~R23, WM_CLOSE teardown, 실제 후보 scene/input 증거, G2~G4는
    그대로 미해결이다. 이번 바퀴도 제품 G1 증거는 0이다.
- 다음 한 가지: work tier(Luna/Sonnet5, high)가 게임 없이 **R15**를 구현한다 — 직접 reader 실패가
  budget 소진보다 우선 분류되도록 고정. 이후 큐는 R19 → R20 → R21 → R22 → R23 → **R24** →
  F2-R1 → F3-R1 → F3-R2 → F6-R2다. S1/F2-R2 상위 재결 전 Stage B·게임/Wine/Xvfb 실행은 금지한다.
