# 2026-09-28 | lap 735 | 목표 G5 (체크리스트 C 특수능력 paired 측정 + 건설 재판정 착수)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5`, high effort (환경
  MODEL_ROUTING 계약상 work tier에 해당); 지정 역할 work — 승인된 범위의 실측/코드/실행만 수행,
  마일스톤 판정이나 v6 교체 승인 같은 상위 결정은 하지 않음.
- 가설 / 사용자 관찰: 2026-09-28 08:15/10:06 운영자 지시 — (C)는 lap731의 "특수능력 존재 확인"만으로
  PASS 처리할 수 없고, 존재하는 능력 버튼마다 원본20 대 후보(v6) 50의 실제 수신 수를 paired로 측정해야
  한다. 건설도 N/A 판정이 의심되어 재판정이 필요하다.
- 예상 PASS / FAIL 조건: 어떤 능력이 있든, 그 능력을 유발하는 입력(버튼 클릭 + 필요시 지면 후속
  클릭)이 선택된 슬롯 전원에 도달하면 PASS(원본 ≤20 전원, 후보 최대 50/51 전원 — 20에서 잘리지 않음).
  일부만 도달하면 FAIL(캡 관련 회귀).
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  - 신규 `tools/g5_worker_ability_broadcast_probe.py` (SHA256
    `556492a19078bb0a1cdfdd3478b9878ac08701faa15c67aa9eebfcee9c3d3a58`) — 조사용 도구,
    제품 코드(EXE 패치) 무변경. uncommitted(`LOOP_ALLOW_COMMITS=0`).
  - 방법: 능력 버튼(v/i/f 셀) 존재 여부는 **클릭 없이** 커맨드 그리드 캡처의 픽셀 표준편차로만
    판별(채워진 셀 std≈55~70, 빈 셀 std≈8 — 임계값 20). 클릭 기반 판별을 먼저 시도했다가(run1)
    같은 부팅의 유일한 기존 워커에 버튼을 미리 눌러 "소모"시켜 뒤이은 fixture-broadcast 측정에서
    거짓 FAIL(0/20)이 나오는 것을 발견해 픽셀 판별 방식으로 교체했다(같은 lap 안에서 자체 반증→수정,
    아래 실행 결과 run1/run2 비교로 근거 보존).
  - fixture 스폰(op=5/6)은 공유 `patches/population/runtime_bridge.c`의 fixture_type 화이트리스트가
    솔로 로비 랜덤 워커 타입(21/31/7 등)을 대부분 거부하므로, lap730이 이미 만든 화이트리스트 제거
    fork `patches/population/g5_c_repair_bridge.c`(무변경, 재사용)를 그대로 빌드에 사용했다 — 공유
    `runtime_bridge.c`도 `g5_r3_death_bridge.c`도 건드리지 않음(`git status`로 확인, 둘 다 무변경).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, 후보 v6
  `fdc913b5f42dc7cc2dcb258d3ecac43e2a2a79a24e4ce10ee362e8ded173805f`(`build_candidate` 재계산,
  `patches/selection/g5_selection_cap50_v6.py` 무변경). 격리 Wine prefix/Xvfb 1600x1200, 솔로
  로비(단일 활성 플레이어 owner0), worker-type 전용 7x8(-3..3 x -3..4) 밀집 fixture(55기)
  + 기존 워커 slot1198 = 56기 후보군. 이번 부팅 국가는 원본/후보 두 실행 모두 worker type=21로
  동일(솔로 로비 국가 배정이 이 세션 3회 부팅에서 21→21→31 순으로 관측 — 완전 균등 난수는 아닌
  것으로 보이나 확정 못함, run1은 type31).
- 실행 명령 / 로그 / 캡처 경로 및 해시: `PYTHONPATH=. .venv/bin/python -m
  tools.g5_worker_ability_broadcast_probe --variant {original,candidate} --runtime-root
  local/runtime/lap735_ability_{original2,candidate} --artifact-root
  /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260928_lap735_ability_{original2,candidate}`.
  run1(폐기, 방법 결함 확인용) 아티팩트는
  `.../20260928_lap735_ability_original/`(`probe-result.json`에 결함 재현 보존).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - 이번 부팅(원본·후보 모두 worker type=21)의 커맨드 그리드는 3칸(v/i/f) 전부 채워져 있었다
    (`cell_variance` v=69.9/i=59.5/f=70.1, 빈 셀 기준 8과 뚜렷이 구분).
  - **"f" 능력(그리드 4번째 칸, 아이콘 미상): 원본 20/20 전원 수신 PASS, 후보 50/50 전원 수신
    PASS.** `+0x290`/`+0x384` 필드가 20에서 잘리지 않고 선택된 전원(원본 20, 후보 50)에서 상태
    변화가 관측됨 — 이동/정지/공격/그룹지정/채집/수리에 이어 특수능력도 같은 브로드캐스트 게이트가
    적용됨을 처음으로 직접 확인.
  - **"v"/"i" 능력: 원본·후보 둘 다 0/20, 0/50 — 판정 UNKNOWN(캡 결함 아님).** 버튼 클릭 + 워커
    기준 (+4,-4) 지면 우클릭 입력으로는 어느 슬롯도 상태가 변하지 않았다(원본조차 0명). 20 중
    일부만 응답하는 "잘림" 패턴이 아니라 원본·후보 동일하게 전원 무반응이므로, v6 회귀가 아니라
    이 두 능력이 다른 대상(예: 특정 지형/건물, farmland 타일 등)을 요구하는 타겟 모드일 가능성이
    높다 — 근본 원인 미확정, v6 결함으로 볼 근거 없음(원본도 동일하게 실패).
  - 크래시 0(원본 2회+후보 1회 전부), `source_unchanged` 전부 true, `cleanup.prefix_processes_after=[]`
    전부. `make check` **1111 passed(789.17s)**, ruff/mypy/`CONTEXT_PASS` 전부 PASS,
    `checks/safety.sh check`: `SAFETY_PASS`(신규 pytest 0개, 조사용 도구 1개 추가).
  - **건설 재판정(08:15 지시 ①)은 이번 lap에서 별도 실측을 추가하지 못했다** — 이번 세션의 3회
    부팅(worker type 31→21→21)이 모두 lap730/731이 이미 조사한 2개국(type7/21/31) 범위 안에
    머물러 새 국가 표본을 얻지 못했고, 커맨드 그리드 캡처(`00-worker-selected-command-grid.png`,
    이번 lap 3장)에서도 "다음 페이지" 화살표나 추가 그리드 요소는 보이지 않았다(row1 4칸+row2
    8칸 고정 레이아웃, lap731 관측과 일치). 이는 lap731 N/A 판정을 약하게 보강하지만, 08:15 지시가
    요구한 "설명서/다른 국가/단축키" 전수 확인에는 미달한다 — **건설 = 아직 미확정(N/A 잠정 유지,
    확정 아님)**.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 특수능력 paired 측정은 이번에 확인된 "f" 능력
  1종에 한정된다 — 다른 부팅에서 나타날 수 있는 "v"/"i" 계열(또는 완전히 다른 국가의 다른 능력)이
  실제로 타겟을 만족했을 때도 동일하게 전원 수신하는지는 미검증(다음 work가 타겟 오프셋 탐색을
  gather 방식처럼 넓혀 확인 필요). 건설 재판정은 미완료. middle 독립 검수는 2026-09-28 03:36
  운영자 판정대로 체크리스트 전체(A~H) 완료 후 한 번에 진행하므로 이번 lap은 그 대상이 아니다.
- 다음 한 가지: ① 건설 재판정을 마저 진행 — 설명서(`../[ESL]Syw2plus/[필독] 임진록 설명서/`)에
  실제 조작법 텍스트가 있는지 재확인(이번 lap에서는 열어보지 않음), 부팅을 몇 차례 더 반복해 지금까지
  못 본 새 국가가 나오는지 확인. ② "v"/"i" 능력의 유효 타겟을 gather probe처럼 여러 지면 오프셋을
  순회 탐색해 실제로 발동시킨 뒤 같은 paired 측정을 반복(가능하면 같은 lap에서 여러 능력을 함께
  측정). 끝나면 (C) 완료 선언 → (E) UI 진행.
