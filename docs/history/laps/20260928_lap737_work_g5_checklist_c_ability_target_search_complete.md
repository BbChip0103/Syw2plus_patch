# 2026-09-28 | lap 737 | 목표 G5 (체크리스트 C 잔여 "v"/"i" 특수능력 유효 타겟 탐색 → C 완료 선언)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5`, high effort (환경
  MODEL_ROUTING 계약상 work tier에 해당); 지정 역할 work — 승인된 범위의 실측/코드/실행만 수행,
  마일스톤 판정이나 (C) 완료를 넘는 상위 결정(G5 종료 여부)은 하지 않음.
- 가설 / 사용자 관찰: 2026-09-28 lap736 "다음 work" 권고(STATUS) — lap735가 "v"/"i" 셀을
  버튼+고정 지면점(worker+(4,-4)) 1곳으로만 시도해 전원 무반응(0/20, 0/50)이었던 것을, gather
  probe(lap729)가 목적지를 몰라 여러 오프셋을 탐색했던 것과 같은 방법으로 재시도하면 유효 타겟을
  찾을 수 있을 것이라는 가설. 겸해서 세 번째 국가(worker7)의 특수능력도 아직 미측정이었다(lap736
  보너스 항목).
- 예상 PASS / FAIL 조건: 오프셋 탐색으로 lone worker가 실제로 발동(`+0x290`/`+0x384` 변화)하는
  레시피를 찾으면, 그 레시피를 미사용 fixture에 적용해 원본 ≤20/후보 ≤50 전원이 반응하면 PASS
  (선택상한 무관), 일부만 반응하면 FAIL(캡 회귀), 전원 무반응이면 근본원인을 추가로 좁혀 UNKNOWN.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  - 신규 `tools/g5_ability_target_search_probe.py` (SHA256
    `24a352ab378bcf6f3a76471dacf0e9388c11f5b4e6d079cc8f8da457da81df4a`) — 조사용 도구, 제품 코드
    (EXE 패치) 무변경. uncommitted(`LOOP_ALLOW_COMMITS=0`).
  - 방법: (1) lone worker에서 "s" 리셋 후 버튼만 클릭(자가발동 가설), 변화 없으면 (2)
    `g5_worker_gather_command_probe.GATHER_OFFSET_CANDIDATES`와 동일한 worker 기준 지면 오프셋을
    최대 8개까지 순서대로 우클릭(버튼+지면)하며 시도. 각 시도 전 baseline은 `wait_settle()`로
    command/pending이 0.6초간 무변화일 때까지 대기한 뒤 포착 — **run1(변경 전 코드)에서 baseline을
    "s" 키 후 고정 0.4초 sleep만으로 잡았다가, stop 명령이 자연히 정착되는 중(`command` 3→1)이던
    것을 "능력이 발동했다"는 거짓 양성으로 오판한 것을 자체 발견·수정**(같은 lap 안에서 반증→수정,
    아래 run1/run2 비교로 근거 보존). 확인된 레시피는 그 즉시 미사용 fixture(worker-type 전용 7x8
    격자, `g5_worker_gather_command_probe.worker_grid_requests` 재사용) 전체 드래그 선택에 적용,
    응답은 `g5_worker_ability_broadcast_probe.responded_slots`(변경 없이 재사용)로 측정. 추가로
    fixture 스폰 직후, 전체 드래그 전에 worker 기준 -1..1 타일 박스(2~4기)만 선택한 "duo-check"를
    끼워 넣어 선택 크기 자체가 발동 여부를 가르는지 별도로 관측.
  - fixture 스폰(op=5)은 lap730/735가 이미 검증한 화이트리스트 제거 fork
    `patches/population/g5_c_repair_bridge.c`(무변경, 재사용) — 공유 `runtime_bridge.c`도 R3
    probe의 `g5_r3_death_bridge.c`도 건드리지 않음(`git status`로 확인, 둘 다 무변경).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, 후보 v6
  `fdc913b5f42dc7cc2dcb258d3ecac43e2a2a79a24e4ce10ee362e8ded173805f`(`build_candidate` 재계산,
  `patches/selection/g5_selection_cap50_v6.py` 무변경). 격리 Wine prefix/Xvfb 1600x1200, 솔로
  로비(단일 활성 플레이어 owner0), worker-type 전용 7x8(-3..3 x -3..4) 밀집 fixture(55기) + 기존
  워커 slot1198 = 56기 후보군. 부팅별 국가: 원본 run1/run2 = worker7(HQ49), 후보 run1 =
  worker31(HQ58), 후보 run2 = worker21(HQ70) — 이번 세션 4회 부팅으로 3개국 전부(worker7/21/31)를
  다뤘다(lap736이 미측정으로 남긴 worker7 특수능력이 이번에 처음 측정됨).
- 실행 명령 / 로그 / 캡처 경로 및 해시: `PYTHONPATH=. .venv/bin/python -m
  tools.g5_ability_target_search_probe --variant {original,candidate} --runtime-root
  local/runtime/lap737_ability_target_{original,original_r2,original_r3,candidate,candidate_r2}
  --artifact-root /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/
  20260928_lap737_ability_target_{...} --max-attempts 4`. run1(`..._original/`, 폐기, baseline
  결함 재현 보존)은 "v" 능력에서 거짓 양성(`command` 3→1이 stop 자연정착이었음)을 보였다;
  `wait_settle` 수정 후 `..._original_r2/`·`..._original_r3/`(둘 다 worker7 재현)·
  `..._candidate/`(worker31)·`..._candidate_r2/`(worker21) 4회가 실제 결과다. 각 `attempt_01/
  probe-result.json`에 `target_search`/`ability_probes`/`duo_check` 원자료 보존. 게임 사본(~580MB
  ×5)은 직후 삭제(디스크 위생, output/manifest/prefix/log 보존).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **"i" 셀 (원본 worker7 / 후보v6 worker21, 두 국가 모두 활성):** 지면 오프셋 (0,6) 우클릭이
    lone worker에서 `command` 1→8로 실제 발동(원본·후보 둘 다 동일 좌표·동일 레시피로 재현) — 이는
    `wait_settle` 적용 후에도 살아남은 진짜 양성. 그러나 **같은 레시피를 fixture로 확대하면 원본
    20/20·후보 50/50 전원 무반응**(0 responded, `not_responded_slots`에 lone worker 자신의 슬롯도
    포함). 원인 규명을 위해 끼워 넣은 **duo-check(원본: worker7 기준 2기 선택, 후보: worker21
    기준 3기 선택)도 둘 다 무반응** — 선택 인원이 1명에서 2명으로 늘어나는 순간 이미 발동하지
    않는다. **판정: 이 능력은 "정확히 1기 선택" 상태에서만 발동하는 솔로 전용 커맨드로 설계된 것으로
    보이며(원본도 그룹에서 발동 안 함), G5 선택상한(20→50) 확장과 무관한 원본 엔진 동작이다 — N/A,
    선택상한 결함 아님.**
  - **"v" 셀 (원본 worker7·후보v6 worker31, 두 국가에서 활성 — worker21 부팅에서도 활성이었으나
    이번 lap에서 원본측은 worker7만 시도):** button-only 1회 + 지면 오프셋 최대 8개(그 중 1개는
    화면 밖이라 실제 시도 7개) 전부 lone worker에서 무변화. **유효 발동 레시피를 찾지 못해
    `NO_FIRING_TARGET_FOUND`로 fixture 측정 자체를 하지 않음.** 3개국(worker7/21/31, lap735
    포함) 전부에서 원본·후보 동일하게 무반응이었으므로 v6 회귀로 볼 근거는 없으나, 유효 타겟이
    무엇인지는 여전히 미상 — **UNKNOWN 유지**(실패 가설 2회: (1) 고정 지면점 1곳 - lap735, (2)
    button-only+8오프셋 탐색 - 본 lap; 추가 탐색은 다른 접근이 필요해 이번 lap에서 중단).
  - 크래시 0(원본 3회+후보 2회 전부 완주), `source_unchanged` 전부 true, `cleanup.
    prefix_processes_after=[]` 전부. `make check` **1111 passed(818.64s)**, ruff/mypy/
    `CONTEXT_PASS` 전부 PASS, `checks/safety.sh check`: `SAFETY_PASS`(신규 pytest 0개, 조사용
    도구 1개 추가, 제품 코드 무변경).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: v6 자체의 결함이 아님(원본도 동일 동작) —
  "i"는 설계상 솔로 전용, "v"는 근본원인 미상이나 원본·후보 대칭이라 회귀 신호 없음. **(C) 체크리스트
  전체(이동·미니맵 우클릭·공격·정지·홀드·순찰·채집/건설/수리·특수능력/변신·승선하선·좌표일치)를 이
  lap으로 완료 선언한다** — 미니맵 우클릭(격리 환경 무반응, lap682/717/723 UNKNOWN)과 "v" 능력
  UNKNOWN 2건은 잔존하되, 둘 다 원본에서도 동일하게 확인 불가/무반응이라 v6 특유의 회귀가 아니라는
  근거를 갖췄다. middle 독립 검수는 2026-09-28 03:36 운영자 판정에 따라 체크리스트 A~H 전체가
  채워진 뒤 한 번에 진행하므로 이번 lap에서 별도 요청하지 않는다(work tier, 정보 제공용).
- 다음 한 가지: (E) UI — 50기 선택 시 초상화/정보 패널 표시·클릭·스크롤, HUD 깨짐, 선택 표시(체력바)
  50기 확인. 끝나면 (F) 저장/로드 → (G) 멀티 → (H) 장시간 순서로 진행.
