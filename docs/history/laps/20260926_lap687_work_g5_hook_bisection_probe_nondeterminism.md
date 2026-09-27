# 2026-09-26 | lap 687 | 목표 G5

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5`(세션 보고 모델ID), 실무(work), high.
  이번 lap은 lap686 18:59 운영자 지시("H1/H2/H3를 하나씩 뺀 후보 3개로 dense-50 공격 1회씩 → 훅 1개
  특정")를 실행했다. 세션 도중(약 19:25) 운영자/중간 tier가 이미 이 lap의 1차 관측(같은 후보 재실행이
  0과 18로 갈린 것)을 반영해 `docs/STATUS.md`·`docs/feedback/INBOX.md`·`docs/feedback/APPROVALS.md`를
  커밋(`e0ab6a1`)했다 — 이 문서는 그 판정과 겹치지 않게, **이번 lap이 실제로 만든 것과 실측값**을
  근거로 남긴다.
- 가설 / 사용자 관찰: v2의 H1/H2/H3 훅 중 정확히 하나가 dense-50 공격 유지(`ever_command4_count`)를
  깨는지, v1 전체(훅 없음, lap686 기준 18/49)와 비교해 어느 훅을 제거하면 회복되는지 판별한다.
- 예상 PASS/FAIL 조건: 훅 3개 중 하나를 제거한 후보가 dense-50에서 V1_FULL 수준(약 18/49)으로
  회복되면 그 훅이 범인, 나머지 둘은 무해.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 전부 uncommitted
  (`LOOP_ALLOW_COMMITS=0`, 이번 세션은 커밋 권한 없음 — 세션 도중 다른 tier가 문서 파일만 별도로
  커밋했으나 아래 4개 신규 파일은 포함되지 않았다. `git status`가 모두 깨끗하게 나오는 것은 그
  문서 커밋 때문이며, 이 4개 파일은 여전히 uncommitted 상태로 디스크에 남아 있다):
  - `patches/selection/g5_selection_cap50_v2_partial.py`(신규): v1 전체 위에 H1/H2/H3 중 정확히
    2개만 적용하는 `build_candidate(original, skip="H1"|"H2"|"H3")` 빌더. 캐이브 3개는 항상 전부
    기록하되(레이아웃 동일성 유지), 사이트 훅만 선택적으로 설치.
  - `patches/selection/test_g5_selection_cap50_v2_partial.py`(신규, 5 케이스): 각 skip 변형이 정확히
    2개 훅만 설치하고, 세 변형과 v2 전체가 서로 다른 SHA를 갖는지 검증.
  - `tools/g5_worker_relative_move_attack_probe_v2_partial.py`(신규): `tools/g5_worker_relative_move_attack_probe.py`의
    dense-50 MOVE+ATTACK 수렴 하네스를 재사용하면서 `base.g5`/`base.TARGET_SHA`를 위 부분-훅 빌더로
    스왑. v1/v3 래퍼와 달리 SHA를 하드코딩하지 않고 매 호출마다 원본에서 새로 계산해, 이전에 본 적
    없는 조합도 안전하게 검증한다.
  - `tests/test_g5_worker_relative_move_attack_probe_v2_partial.py`(신규, 4 케이스): 알 수 없는 훅
    이름 거부, `variant=original`은 빌드하지 않음, `variant=candidate`는 신선한 SHA를 계산해 주입,
    예외 발생 시에도 `base.g5`/`base.TARGET_SHA`가 복원되는지 검증.
  - 제품 EXE/원본/바이너리 0 변경. 격리 실행 4회가 만든 `local/runtime/g5-lap687-v2-partial-convergence/*/*/game`
    사본(각 ~2.7GB)은 완료 직후 삭제(manifest/output/prefix/로그는 보존).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(4회 실행 전후 모두 재확인, 불변).
  후보 SHA(이번 lap에서 처음 계산, 매번 원본에서 재빌드):
  - skip=H1(H2+H3만 적용) `3f674b0287d5edc1…`
  - skip=H2(H1+H3만 적용) `06f978e0437fada4…`
  - skip=H3(H1+H2만 적용) `83b816a0b833a13b…`
  - (참고, v2 전체 = 모든 H1+H2+H3) `ae495fa5a1498597…`(lap665/685/686과 교차검증된 기존 값, 이번
    lap에서 재확인만 하고 재실행은 하지 않음)
  - 격리 Wine/Xvfb 1600×1200, PS3 solo owner0. lap682/685/686과 동일한 dense 7×8-1=55기 worker-relative
    fixture, 드래그50(worker+49).
- 실행 명령 / 로그 / 캡처 경로 및 해시(공유 `temp/Syw2plus_patch/20260926_lap687_g5_v2_partial_*/`):
  1. `PYTHONPATH=. .venv/bin/python -m tools.g5_worker_relative_move_attack_probe_v2_partial --variant candidate --skip-hook H1 --runtime-root local/runtime/g5-lap687-v2-partial-convergence/h1 --artifact-root .../20260926_lap687_g5_v2_partial_h1`
  2. 동일 `--skip-hook H2 ... .../h2 ... .../20260926_lap687_g5_v2_partial_h2`
  3. 동일 `--skip-hook H3 ... .../h3 ... .../20260926_lap687_g5_v2_partial_h3`
  4. skip=H1 **재실행**(재현성 확인) `... .../h1r2 ... .../20260926_lap687_g5_v2_partial_h1_r2`
  5. `PYTHONPATH=. .venv/bin/python -m pytest -q patches/selection/test_g5_selection_cap50_v2_partial.py tests/test_g5_worker_relative_move_attack_probe_v2_partial.py patches/selection/test_g5_selection_cap50_bisect.py tests/test_g5_bisect_attack_probe.py tests/test_g5_worker_relative_move_attack_probe_v1.py tests/test_g5_worker_relative_move_attack_probe_v2.py tests/test_g5_worker_relative_move_attack_probe.py` → **28 passed**.
  6. `make check`(foreground/nohup으로 세션 유지, 20분 타임아웃으로 폴링 대기, SIGTERM 없음) →
     **1003 passed(702.72s)**, ruff/compileall/mypy/`CONTEXT_PASS` 모두 PASS. 로그
     `logs/gates/20260926_lap687_make_check_run1.log`.
  7. `bash checks/safety.sh check` → `SAFETY_PASS`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **1차 3-way 결과(단발): skip=H1 → `ever_command4_count=0/49`. skip=H2 → `18/49`. skip=H3 →
    `18/49`(`max_pending_exact_count=1/49`).** 표면적으로는 "H2와 H3가 동시에 있어야 깨진다(H1 무관)"는
    깔끔한 패턴처럼 보였다(skip=H1일 때만 H2∧H3가 동시에 남아 있고, 그 경우만 유일하게 0으로 떨어짐).
  - **재현성 검사(결정적 반증): skip=H1을 동일 조건으로 재실행하니 `ever_command4_count=18/49`** —
    1차 결과(0/49)와 정면으로 모순된다. **같은 빌드, 같은 fixture, 같은 입력 순서에서 0과 18이 둘 다
    나온다** — 이는 dense-50 `ever_command4_count` 단발 측정이 **비결정적**이며, N=1 훅 이분 탐색으로
    "어느 묶음이 범인인지"를 가를 수 없다는 뜻이다. 1차 3-way 패턴은 우연의 일치였을 가능성이 높다.
  - **정적 교차검증(H1/H2/H3가 애초에 이 시나리오에서 실행되는지 자체가 의심스러움):** 원본 실행파일을
    직접 디스어셈블해 H1_SITE(`0x00445d4e`)·H2_SITE(`0x00445dcb`)가 속한 함수(그룹**지정**,
    `0x00445cd0`부터, `ret 8`은 아님 — 이 함수 자체는 `0x00445e22 ret 4`)와 H3_SITE(`0x00445ed1`)가
    속한 함수(그룹 **호출**, `0x00445e30`부터)의 코드 흐름을 끝까지 따라갔다. 두 함수 모두 Ctrl+숫자
    (지정)/숫자단독(호출) 키 입력에서만 진입하며, 이 두 함수로의 호출 지점을 `.text` 전체에서 바이트
    단위로 전수 스캔한 결과 **정확히 1곳**(지정, `0x0041d4f0`)과 **7곳**(호출,
    `0x0041d533/5a4/619/68e/70d/766/7fd`) — 모두 같은 키보드 폴링 디스패처 안에 있고, 각 호출은 해당
    숫자키가 실제로 눌렸을 때만 조건부로 실행된다. 게다가 이미 존재하는 lap677의 gdb 진입-카운트
    트레이스 산출물(`temp/Syw2plus_patch/20260926_lap677_g5_order_issuer_candidate_r9/gdb_control/{move,attack}/entry-summary.json`)을
    다시 읽어보니, 같은 종류의 MOVE/ATTACK 전용 probe 실행 동안 `group_assign_FUN_00445D30=0`,
    `order_consumer_FUN_0040F7D0=0`이 **이미 실측으로 기록되어 있었다** — 즉 group 지정/호출 키를
    누르지 않는 이 probe 시나리오에서는 H1/H2/H3가 들어 있는 두 함수가 **한 번도 진입되지 않는다**는
    독립 증거가 이미 존재한다. 이는 skip=H1/H2/H3 결과의 차이가 애초에 훅 코드의 "실행"에서 나올 수
    없다는 뜻이며, lap686이 "H1/H2/H3(G4) 훅이 지배적 원인"이라고 내린 귀속 자체도 재검토가 필요함을
    시사한다(같은 이유로 V1_FULL 18/49 대 V2_FULL 0/49 델타도 N=1~2 측정이라 노이즈일 가능성이 있다).
  - **종합 판정: NOT_FEASIBLE(이 방법으로는).** "훅 하나씩 제거해 dense-50 단발로 범인을 특정한다"는
    이번 lap의 접근은 측정 자체의 비결정성 때문에 판별력이 없다. 새로 만든 도구(부분-훅 빌더 +
    래퍼)는 재사용 가능한 인프라로 남기되, 이 결과만으로 어떤 훅도 "범인"으로 단정하지 않는다.
    (세션 도중 운영자가 19:25에 독립적으로 같은 결론 — "공격 probe가 비결정적" — 에 도달해 다음
    한 가지를 이미 갱신했다: 먼저 흔들림 원인 1개를 raw로 고정한 뒤 N=5 반복 측정으로 비율 분포
    판정.)
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 회귀 28 passed(신규 9 포함, 신규 2파일), `make check`
  1003 passed(702.72s), ruff/compileall/mypy/`CONTEXT_PASS`/`SAFETY_PASS` 모두 PASS. 제품 후보/원본
  EXE 0 변경. G5 2단 독립 검수·3단 사용자 milestone 승인은 여전히 없음(원래부터 없었음). 디스크:
  lap 시작 104~107GB → 4회 실행(각 ~2.7GB game 사본 즉시 정리) 후 104GB, 안전선(20GB) 위.
- 다음 한 가지: 19:25 운영자 판정(이미 STATUS/INBOX/APPROVALS에 기록됨)을 따른다 — middle 없이:
  ① 공격 probe 흔들림의 가장 유력한 원인 후보(적 스폰 위치/시점, 화면↔월드 목적지 변환, 공격 가능
  판정(P6) 시점, 선택 순서) 중 하나를 raw 비교 1회로 고정한다. ② 고정 후 v3 50기 N=5 / 원본 20기 N=5
  반복 측정으로 `ever_command4_count/attack_capable` 비율 분포를 비교해 판정한다(원본 중앙값 대비 후보
  중앙값). ③ 결과를 들고 middle 재검수. 이번 lap이 만든 부분-훅 빌더/래퍼는 ①②가 안정된 뒤, 필요하면
  "진짜 신호가 있는지" 재확인하는 데 재사용할 수 있다(지금은 사용하지 않는다 — 비결정성이 해소되기
  전에는 어떤 훅 조합 결과도 신뢰할 수 없다).
