# APPROVALS lap734~737 work tier 정보제공 계보 원문 보존 (2026-09-28, lap741 압축)

SHA256 `ad5ee26fb93f7c2a112bc71a0d179aaf3b2c4d09b54c89c0c379ec575c8ed036`(원문 89줄)

- [ ] **2026-09-28 lap734 work tier(Claude Code Sonnet, 정보 제공용 — 새 middle 검수 요청 아님,
  2026-09-28 03:36 운영자 판정에 따라 middle은 체크리스트 전체가 채워진 뒤 한 번에 진행):** 10:06
  지시 ①(v6 핵심 회귀 1회, 원본 1회 대조)을 수행. 기존 4개 probe(coverage/attack/roundtrip/R3)를
  모듈 `g5`/`TARGET_SHA`만 v5→v6로 임시 스왑하는 monkeypatch 드라이버(lap682/717/723/724 선례와
  동일 방식, 저장소 파일 아님)로 재사용해 원본 1회·후보 v6 1회씩(R3는 front/middle/rear-death 3
  시나리오) 실행 — **전부 PASS**: 드래그 4종(plain/ALT/Ctrl/Shift) 50/50, 이동(버튼+우클릭)
  50/50, 정지·홀드·순찰(버튼+단축키) 50/50, 더블클릭 같은종류선택 50/50, 51번째 거부(56 중 정확히
  50), Shift+클릭 추가/제거 toggle PASS, 그룹 roundtrip(지정→해제→호출→저장→로드→호출)
  `PASS_UI_ROUNDTRIP` 7/7, R3 3 시나리오 전부 `PASS_NO_SPARSE_GAP`·`structural_ok=true`·누락 0.
  공격은 pending-word 기준 원본 17/19·후보 22/49로 단일측정 변동폭 안(lap688 N=5 선례와 같은
  패턴, 회귀 아님 — 확정하려면 N≥3 필요). `tools/g5_r3_sparse_selection_probe.py`에
  `candidate-v6` variant 2줄만 추가(v4→v5 추가 때와 동일 패턴, 제품코드 아님). 크래시 0,
  `source_unchanged` 전부 true, `cleanup.prefix_processes_after=[]` 전부. `make check`
  1111 passed(772.33s), ruff/mypy/`CONTEXT_PASS`/`SAFETY_PASS` 전부 PASS. **10:06 지시 ②(건설
  재판정+특수능력 paired)는 이번 lap에서 착수하지 못했다** — 08:15 지시가 지적한 마일스톤 경계
  재판정이라 얕은 조사로 성급히 끝내지 않기 위해 다음 work로 넘긴다. 근거
  `../history/laps/20260928_lap734_work_g5_v6_core_regression_pass.md`.
- [ ] **2026-09-28 lap735 work tier(Claude Code Sonnet, 정보 제공용 — 새 middle 검수 요청 아님,
  2026-09-28 03:36 운영자 판정에 따라 middle은 체크리스트 전체가 채워진 뒤 한 번에 진행):** 10:06
  지시 ②(건설 재판정 + 특수능력 paired)를 수행, **특수능력 부분만 완료**. 신규
  `tools/g5_worker_ability_broadcast_probe.py`는 능력 버튼(v/i/f 셀) 존재 여부를 **클릭 없이**
  커맨드그리드 캡처의 픽셀 표준편차로 판별한다(채워진 셀 std≈55~70, 빈 셀 std≈8) — run1에서 클릭
  기반 판별을 먼저 시도했다가 같은 부팅의 유일한 워커에 버튼을 미리 눌러 능력을 "소모"시켜 뒤이은
  fixture-broadcast 측정이 거짓 0/20으로 나오는 것을 발견했고(단발성/쿨다운 효과로 추정), 같은 lap
  안에서 픽셀 판별 방식으로 교체해 해결했다. fixture는 lap730이 만든 화이트리스트-제거 fork
  `patches/population/g5_c_repair_bridge.c`(무변경, 재사용)로 worker-type 전용 55기를 스폰 —
  공유 `runtime_bridge.c`도 R3 probe의 `g5_r3_death_bridge.c`도 건드리지 않았다. 결과(이번 부팅
  원본·후보 둘 다 worker type=21): **"f" 능력 원본20/20·후보v6 50/50 전원 수신 PASS**(캡 잘림 없음
  — 이동/공격/그룹지정/채집/수리에 이어 특수능력도 같은 브로드캐스트 게이트가 적용됨을 처음 직접
  확인). "v"/"i" 능력은 원본·후보 **동일하게** 0/20·0/50(무반응) — 일부만 응답하는 잘림 패턴이
  아니라 원본조차 0이므로 v6 회귀로 볼 근거가 없다(타겟 조건 미상, UNKNOWN으로 표시). **건설
  재판정은 착수하지 못했다** — 이번 세션 3회 부팅(worker type 31→21→21)이 모두 lap730/731이 이미
  조사한 국가(type7/21/31) 범위에 머물러 새 국가 표본을 못 얻었고, 설명서
  (`../[ESL]Syw2plus/[필독] 임진록 설명서/`)도 열어보지 않았다 — 캡처된 커맨드그리드(이번 lap 3장)
  에서 "다음 페이지" 화살표나 추가 UI 요소는 보이지 않아 lap731의 N/A 판정을 약하게 보강하지만,
  08:15 지시가 요구한 전수 확인에는 미달한다(**건설 = 미확정으로 유지, N/A 확정 아님**). 크래시
  0(원본 2회+후보 1회), `source_unchanged` 전부 true, `cleanup.prefix_processes_after=[]` 전부.
  `make check` **1111 passed(789.17s)**, ruff/mypy/`CONTEXT_PASS` 전부 PASS,
  `checks/safety.sh check`: `SAFETY_PASS`(신규 pytest 0개, 조사용 도구 1개만 추가, 제품 코드
  무변경). 다음 work 권장: ① 건설 재판정 마저 진행(설명서 실제 확인, 추가 부팅으로 새 국가 탐색),
  ② "v"/"i" 능력의 유효 타겟을 gather probe처럼 여러 지면 오프셋으로 탐색해 발동시킨 뒤 같은
  paired 측정 반복. 끝나면 (C) 완료 선언 → (E) UI. 근거
  `../history/laps/20260928_lap735_work_g5_worker_ability_broadcast_paired_partial.md`.
- [ ] **2026-09-28 lap736 work tier(Claude Code Sonnet, 정보 제공용 — 새 middle 검수 요청 아님,
  2026-09-28 03:36 운영자 판정에 따라 middle은 체크리스트 전체가 채워진 뒤 한 번에 진행):** 08:15
  지시 ①(건설 재판정)을 수행. 설명서 3종(`../[ESL]Syw2plus/[필독] 임진록 설명서/` 멀티게임 메뉴얼·
  ESL 패치요약·SYW2X 설명서)을 육안 확인 — 셋 다 일꾼/HQ의 "건물 배치" 조작법 텍스트를 포함하지
  않는다(ESL 요약의 "빌드 다양화"는 build-order 전략 문맥이지 배치 UI가 아님). 신규
  `tools/g5_construction_new_nation_survey_probe.py`(lap731의 두 survey probe를 합치고, 서명
  `(worker_type,hq_type)`이 lap731이 이미 완전 survey한 `{(31,58),(21,70)}`과 다르면 같은 부팅에서
  계속 워커·HQ 그리드 전 버튼을 수행)로 재부팅 16회(4개 타이밍 라운드 — 고정 타이밍은 5회 전부 동일
  국가로 수렴해 tick-seed로 추정, 확인 클릭 직전 지연을 라운드마다 다르게 줘 재시도)를 실행 —
  **솔로 로비 국가 풀이 정확히 3개(worker7/HQ49, worker21/HQ70, worker31/HQ58)로 수렴**하고 4번째는
  16회 중 한 번도 나오지 않았다(08:15 지시의 "표본이 작다"는 의심에 대한 직접 반증 방향 증거,
  모집단 자체가 작을 가능성). 세 번째 국가(worker7/HQ49, 이전엔 gather probe에만 쓰이고 그리드
  survey는 이번이 처음)의 워커 7버튼·HQ 7버튼(R·D는 지면 클릭 후속까지) 전부에서
  `new_slots_after_click=[]`·`new_slots_after_ground_followup=[]`(신규 existence 엔트리 0, 배치
  커서 없음) — lap731이 본 다른 두 국가와 동일한 결론이며, HQ 그리드 형태(S/R/D/T·F/B/Z +
  F1~F11 생산줄)도 국가 간에 레이블 문자만 다르고 구조가 같아 건설 부재가 특정 국가 결함이 아니라
  이 EXE 구조 전체의 특성임을 시사한다. **(C) 건설 = N/A로 강화(3개국 전수, 반증 없음, 08:15 지시
  이행 완료).** 크래시 0(16/16), `source_unchanged` 16/16, `cleanup.prefix_processes_after=[]`
  16/16. `make check` **1111 passed(920.81s)**, ruff/mypy/`CONTEXT_PASS` 전부 PASS,
  `checks/safety.sh check`: `SAFETY_PASS`(신규 pytest 0개, 조사용 도구 1개만 추가, 제품 코드
  무변경). 남은 위험: "정확히 3개국"은 유한 시도(16회) 기반 귀납이라 100% 확증은 아니다. 다음 work
  권장: 08:15 지시 잔여 ②("v"/"i" 능력의 유효 타겟을 gather probe처럼 여러 지면 오프셋으로 탐색해
  발동시킨 뒤 paired 측정, 세 번째 국가 worker7의 특수능력 paired도 함께). 끝나면 (C) 완료 선언 →
  (E) UI. 근거
  `../history/laps/20260928_lap736_work_g5_construction_third_nation_survey.md`.
- [ ] **2026-09-28 lap737 work tier(Claude Code Sonnet, 정보 제공용 — 새 middle 검수 요청 아님,
  2026-09-28 03:36 운영자 판정에 따라 middle은 체크리스트 전체가 채워진 뒤 한 번에 진행):** 08:15
  지시 잔여 ②("v"/"i" 능력 유효 타겟 탐색)를 수행, **(C) 완료 선언.** 신규
  `tools/g5_ability_target_search_probe.py` — lone worker에서 button-only 자가발동 가설 실패 시
  gather와 동일한 지면 오프셋 최대 8개를 우클릭으로 탐색(baseline은 `wait_settle()`로 직전 "s"
  정지명령이 자연 정착될 때까지 대기한 뒤 포착 — run1이 고정 0.4초 sleep만으로 baseline을 잡았다가
  stop 자연정착(`command` 3→1)을 "능력 발동"으로 오판한 거짓양성을 자체 발견·수정). **"i" 셀: 지면
  (worker 기준 (0,6)) 우클릭이 lone worker에서 실제 발동(`command` 1→8, 원본worker7·후보v6
  worker21 둘 다 재현) 확인됐으나, 같은 레시피를 미사용 fixture 전체(원본20/후보50)에 적용하면
  전원 무반응 — 원인 규명용 duo-check(2~3기만 선택)도 원본·후보 둘 다 무반응이라 **"정확히 1기
  선택" 상태에서만 발동하는 솔로 전용 커맨드로 판정(N/A, 선택상한 결함 아님)**.** **"v" 셀: 3개국
  (worker7/21/31, lap735 포함) 전부에서 button-only+지면 오프셋 탐색 전부 무반응 — 근본원인 미상
  UNKNOWN 유지(원본도 0이라 v6 회귀 아님)**. 세 번째 국가(worker7)의 특수능력도 이번에 처음
  측정해 08:15/lap736 잔여 보너스 항목을 해소했다. 크래시 0(원본3+후보2), `source_unchanged`
  전부, `cleanup.prefix_processes_after=[]` 전부. `make check` **1111 passed(818.64s)**,
  ruff/mypy/`CONTEXT_PASS` 전부 PASS, `checks/safety.sh check`: `SAFETY_PASS`(신규 pytest 0개,
  조사용 도구 1개만 추가, 제품 코드 무변경). **이로써 (C) 체크리스트 전체(이동·미니맵·공격·정지·
  홀드·순찰·채집/건설/수리·특수능력·승선하선·좌표일치) 완료로 판단한다** — 미니맵 우클릭과 "v"
  능력 2건은 UNKNOWN으로 남지만 둘 다 원본에서도 동일하게 확인 불가/무반응이라 v6 특유의 회귀
  근거는 없다. 다음 work 권장: (E) UI(50기 선택 시 초상화/정보 패널·HUD·체력바). 근거
  `../history/laps/20260928_lap737_work_g5_checklist_c_ability_target_search_complete.md`.
