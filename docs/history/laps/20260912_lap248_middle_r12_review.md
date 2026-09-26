# 2026-09-12 | lap 248 | 목표 G1 Stage B — R6-B-R12 독립 검수

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5`/high; middle tier
  (진단·계획·확인). 게임 코드 hands-on 수정 없음. `loop/.lap_counter`=248을 lap 번호로 쓴다
  (루프 런타임 evidence 블록은 `lap=247`로 표시되어 한 칸 차이가 있으나 PROMPT.md ⑤에 따라
  카운터 파일 값을 사용한다. 카운터는 읽기만 했다).
- 가설 / 사용자 관찰: lap247 work가 `_wait_state`에서 selection `CORRUPTED`를 read-error
  tail/coverage 부족의 `UNAVAILABLE` 표기로부터 보호했다고 주장한다. 제시된 증거는 "targeted
  4 passed"와 Fast 전체뿐이라 (a) 가드가 실제로 load-bearing인지, (b) 과하게 강해 기존 SOUND
  경로의 `UNAVAILABLE`까지 막지는 않는지, (c) 겹침 조합 전체에서 계약이 성립하는지를
  보여주지 못한다. 이 세 가지를 독립 하네스로 따로 측정한다.
- 예상 PASS / FAIL 조건: **PASS**는 (C0) 출하 회귀가 실제 저장소에서 통과하고, (C1) 독자적으로
  작성한 기대 모델과 81-case 전수 행렬이 불일치 0이며, (C2) 변이 없는 깊이 일치 미러가 실제
  저장소와 같은 결과를 내고(M0 대조군), (C3) 가드 삭제 변이가 **R12 케이스만**, 가드
  무조건-보존 변이가 **기존 UNAVAILABLE 케이스만**, 역전 변이가 **양쪽 모두**를 죽일 때다.
  하나라도 어긋나면 FAIL로 적고 범위 승인을 하지 않는다.
- 변경 파일 / source fingerprint / 커밋: SUT 무변경. 이번 lap 신규 파일은
  `docs/history/laps/probes/20260912_lap248_r12_review_probe.py` sha256
  `6ab1e5b2a67626578983326e722edb2630ee2d9df6420af872ab3d4eba5816e5`,
  `...20260912_lap248_r12_review_report.json` sha256
  `48faf1d307dab213ece2170879240c0f48263be0c7e3f69dda697ba907884c64`,
  `...20260912_lap248_r12_review_report.attempt1.json`(41바이트 절단),
  `...20260912_lap248_r12_review_report.PROVENANCE.md`, 그리고 STATUS/handoff/ESCALATE_SOL.
  모두 uncommitted, `LOOP_ALLOW_COMMITS=0`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 검수 시점
  `tools/runtime_env.py` sha256 `2f59bbbd14c177119117a9435df0426a66142d4ed1d8cb1b19105a4b3a8025c4`,
  `tests/test_runtime_env.py` sha256
  `d75c75b43a0e32d72882361a2ac80a700825895ecb9cbae24a63a42732f5f842` — lap247 기록과 일치.
  lap247의 pre-change 지문 `bb10cd84…d2bab`는 lap246 middle이 독립적으로 "불변"으로 기록한
  값과 같아, lap246 이후의 유일한 델타가 이번 R12 변경임이 교차 확인된다. 원본 EXE pin
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변, 제품 EXE/DLL/
  assets/baseline/golden 변경 0. Python 3.13.5/.venv, fake-clock + fake-reader fixture;
  실제 게임/Wine/Xvfb/PNG 실행 0, 플레이어·지도·군대 N/A.
- 실행 명령 / 로그: `python docs/history/laps/probes/20260912_lap248_r12_review_probe.py
  --output docs/history/laps/probes/20260912_lap248_r12_review_report.json` → `exit 0`,
  verdict 전부 PASS. `make check` = **271 passed**, Ruff/compileall/mypy 10 files,
  `CONTEXT_PASS`. `LOOP_DRY_RUN=0 bash checks/safety.sh check` = **SAFETY_PASS**.
- 측정값 / 판정:
  - **C0 BASELINE PASS** — 실제 저장소에서 R12 2-param + 기존 UNAVAILABLE 2건 + 경계
    FAIL_NO_EFFECT + corruption provenance 2건 = **7 passed, 129 deselected**.
  - **C1 MATRIX PASS** — `{SOUND, CORRUPTED, ERROR}^4` = **81 케이스 전수**, 구현을 보지 않고
    계약에서 직접 쓴 기대 모델과 **불일치 0**. 최종 selection status, classification,
    `corrupted_poll_count`, `read_error_count`, `poll_count`를 모두 대조했다. read error가
    있으면서 `CORRUPTED`가 보존된 경우 **32건**이며 그 32건 전부에서
    `first_corruption_provenance`가 살아 있다. SOUND가 `UNAVAILABLE`로 내려간 경우 **20건**.
    분류 우선순위(read failure > coverage > selection corrupted > no effect)도 81/81 일치.
  - **C2 MIRROR CONTROL (M0) PASS** — 깊이를 맞춘 무변이 미러에서 `tests/test_runtime_env.py`
    **136 passed**, 실제 저장소와 동일. lap246 R20 교훈대로 대조군을 먼저 세웠다.
  - **C3 MUTATIONS PASS** — 같은 미러에서 M1 `가드 삭제` → **2 failed**, 죽은 것은 R12
    케이스(2 param)뿐이고 기존 UNAVAILABLE 0건·기타 0건. M2 `가드 무조건 보존(if False)` →
    **2 failed**, 죽은 것은 기존 UNAVAILABLE 2건뿐이고 R12 0건. M3 `가드 역전` → **4 failed**,
    양쪽 모두. 즉 가드는 load-bearing이면서(**M1**) 과하게 강하지 않다(**M2**).
  - 판정: R6-B-R12 **PASS / 범위 승인**. 승인 범위는 `_wait_state`의 최종 selection 표기
    한 곳뿐이며, R6-B-R2 semantics·분류 우선순위·제품 G1 증거는 승인 대상이 아니다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: Fast/safety 회귀 없음. 이번 검수는 기계
  1단이며 사용자 마일스톤 승인이 아니다. 남은 위험 두 가지를 기록한다.
  1) 보존된 `CORRUPTED`는 **마지막 성공 poll**의 상태이므로, read-error tail이 겹치면 그
     관측은 stale일 수 있다. 이번 계약에서 그 불확실성은 `selection_observation.status`가
     아니라 timeout `classification`(READ_FAILURE/READ_COVERAGE)과 상위 관측 필드가 담는다.
     `CORRUPTED` 문자열만 보고 판단하는 소비자가 생기면 다시 결함이 된다. 현재 저장소에는
     `tools/runtime_env.py` 밖에서 이 status를 읽는 코드가 **0개**임을 grep으로 확인했다.
  2) **신규 R21(하네스 규약 결함, 제품 영향 없음)**: 공용 probe 출력 규약이 payload
     직렬화 가능 여부를 확인하기 전에 `open("x")`로 증거 파일을 먼저 만든다. 이번 attempt1이
     `json.dump` `TypeError`로 죽으면서 41바이트 절단 파일을 남겼고, R6-B-R7의 "기존 증거
     덮어쓰기 거부" 때문에 같은 경로 재시도까지 막혔다. 직렬화 후 배타 생성(또는 sibling
     temp + link/rename)으로 창을 없애면 R7/R10/R11을 약화시키지 않고 해결된다. 상세는
     `...20260912_lap248_r12_review_report.PROVENANCE.md`.
  S1/F2-R2, R6-B-R2, R13~R15, R19/R20 및 제품 G1~G4는 그대로 미해결이다.
- 다음 한 가지: work tier(Luna/Sonnet5, high)가 게임 없이 **R13**(PASS 경로의 read coverage
  미노출)을 구현한다. Stage B·게임/Wine/Xvfb 실행은 S1/F2-R2 상위 재결 전까지 계속 금지.
