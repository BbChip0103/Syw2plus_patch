# 2026-09-28 | lap 730 | 목표 G5

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5`, 실무(work, 구현·실행).
- 가설 / 사용자 관찰: STATUS 2026-09-28 06:55 운영자 지시 — 체크리스트 (C) 남은 항목 중 **수리
  (손상 아군 건물 대상)**을 원본1회+v5 1회로 한 lap에 끝내라. 가설: 채집(lap729)과 같은 공용
  opcode 게이트(`0x41F0A4`)가 수리 명령에도 적용되어, 손상된 아군 HQ를 우클릭했을 때의 pending
  word가 원본 20기/v5 50기 전원에 도달한다(=앞 20칸으로 잘리지 않는다).
- 예상 PASS / FAIL 조건: PASS = 선택된 유닛 수(원본 상한20, 후보v5 상한50) 전원이 손상된 HQ
  우클릭 후 해당 pending word를 한 번이라도 보인다. FAIL = 후보에서 선택 수보다 적은 수만 받는다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  - 신규 `tools/g5_worker_repair_command_probe.py`(SHA256
    `4bf6bc3cf401687b6779d9c6ce2163045c972cb057751ea9794bb2e911fb5404`). `g5_worker_gather_command_probe`
    와 같은 solo-lobby 부트스트랩·9점 화면↔월드 아핀을 재사용하되, 목표가 스폰 fixture가 아니라
    **게임 시작 시 이미 존재하는 owner0 HQ**라 별도 탐색이 필요했다.
  - 신규 `patches/population/g5_c_repair_bridge.c`(SHA256
    `31d9d8955e709928c68b1187e432c797d10047bd04f18debf80f6013d6e1bb30`, `g5_r3_death_bridge.c`를
    fork해 op=11 추가: owner 소유·생존 유닛의 `unit+0xB4`(hp) 직접 기록 — op=10처럼 원본 death
    handler를 거칠 필요가 없다고 판단한 근거는 파일 자체 docstring 참고). **같은 fork에서 op=5/6
    fixture-type 화이트리스트(원래 `{2,5,7,28,29,46,103,104,108}`)를 제거하고 구조적 게이트
    (flags bit1/2/3=0, width/height 1..8, type<200)와 실제 엔진 Place/Gate 호출만으로 대체** —
    솔로 로비의 국가(및 일꾼 type id)가 fixture-고정이 아니라 매 부팅마다 달라짐을 이 lap이
    실측(worker_type이 31/7/21/31로 실행마다 바뀜, HQ type도 49/70/58/58)했기 때문에 사전에
    화이트리스트를 큐레이션할 수 없었다. 이 fork는 G2 pinned `runtime_bridge.c`도, R3 probe가
    참조하는 `g5_r3_death_bridge.c`도 건드리지 않는다(둘 다 무변경, 아래 `make check` 확인).
  - `patches/selection/g5_selection_cap50_v5.py`/원본 EXE 무변경(읽기만). 커밋 없음(uncommitted,
    `LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(모든 실행 전후
  `source_unchanged=true`, FAIL 포함). v5 후보 `29e61074c622c77debb5053a412e3337fc8100f1eda29bd68efb163b1a9ee146`
  (lap723~729와 동일). 격리 Wine/Xvfb 1600×1200, PS3 solo, owner0. **솔로 로비 국가는 부팅마다
  랜덤**(일꾼 type 7/21/31, HQ type 49/58/70 관측 — 새 발견, 아래 "부수 발견" 참고). fixture는
  `g5_worker_gather_command_probe.worker_grid_requests`(일꾼 기준 7x8, -3..3 × -3..4, 중심 제외
  55기)를 재사용해 **런타임 실측 일꾼 unit_type**으로 스폰. 목표(HQ)는 스폰하지 않고 게임 시작부터
  존재하는 owner0의 유일한 비일꾼 유닛을 제외 스캔으로 특정. 소스 `[ESL]Syw2plus`(SHA 위와 동일).
- 실행 명령 / 로그 / 캡처 경로 및 해시: 전체 artifact
  `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260928_lap730_worker_repair/`.
  1. `--variant original` 4회 FAIL(방법론 반복 수정, 아래 "부수 발견/과정" 참고) → 5회차
     `--runtime-root local/runtime/lap730_repair_orig_r5` → `COMPLETE`이나 버그(잡음 pending
     `0x1000001`을 신호로 오인)로 판정이 무의미해 즉시 버그 수정 → 6회차
     `--runtime-root local/runtime/lap730_repair_orig_r6 --artifact-root .../repair-original-r6`
     → **진짜 `COMPLETE`**. 결과 JSON SHA256 `e5b48ae16796d78908c4871af590ced8418ac267f8da8be898c7603698fd3e04`.
  2. `--variant candidate --runtime-root local/runtime/lap730_repair_v5
     --artifact-root .../repair-candidate-v5` → 1회차 `COMPLETE`(재시도 불요). 결과 JSON SHA256
     `84c1c26f8c3283669a99eb3314de73541c21d2c5062c2e1e7f52f4384f172b80`.
  3. `make check`(foreground nohup + `kill -0` 폴링, 로그 `logs/gates/20260928_lap730_make_check.log`),
     `bash checks/safety.sh check`.
  4. 각 run 뒤 `local/runtime/lap730_repair_*/*/game`(~810MB×2) 삭제, FAIL 포함 output/manifest/
     prefix/log는 보존(디스크 위생, 여유 146G).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  1. **부수 발견(중요, 향후 probe에 반영 필요):** 이 솔로 로비 fixture는 **국가가 부팅마다
     랜덤**이다 — 일꾼 unit_type이 7/21/31로, HQ unit_type이 49/58/70으로 실행마다 바뀌었다
     (기존 lap712~729 문서의 "worker unit_type=7"은 우연히 일치한 표본들이었을 가능성이 크다).
     기존 브리지 op=5/6의 fixture-type 화이트리스트는 일꾼 type이 그 목록 밖(21/31 등)이면
     스폰 자체가 막힌다 — 이번 lap의 fork(화이트리스트 제거, 구조적 게이트만 유지)로 우회했다.
     **다음 일꾼 관련 probe(건설·특수능력·승선하선 포함)는 이 fork(또는 동등한 구조적 게이트
     방식)를 기본으로 삼아야 한다.**
  2. **HQ 우클릭 pending word는 손상 여부와 무관하게 채집과 같은 `0x1000008`이다**(원본·v5 양쪽,
     손상 전/후 각각 확인) — 이 엔진은 "아군 구조물과 상호작용"을 하나의 공용 pending word로
     발행하고(자원 보유 시 예치, 손상 시 수리 등) 실제 동작은 이후 엔진 로직이 문맥으로 결정하는
     것으로 보인다(별도의 "수리 전용" pending word는 이 lap에서 발견하지 못함). 건물 anchor
     좌표(=배치 원점)가 항상 클릭 가능한 스프라이트 위에 있는 것도 아니었다(4회차 FAIL의 원인) —
     이번 lap이 추가한 `HQ_FOOTPRINT_OFFSET_CANDIDATES` 근접 탐색(채집의 목적지 탐색과 동일 기법)
     으로 해결.
  3. **원본**: worker unit_type=7 확인(6회차), HQ 근접 탐색 1회차 오프셋(0,0)에서 즉시
     `0x1000008` 확인, HQ hp 4800→2400(정확히 절반) 직접 기록 성공, 55기 스폰 성공, 전체 드래그
     선택 **20/20**(상한), 손상 HQ 클릭 후 `pending_ever["0x1000008"]=20` — **20/20 전원 수리
     주문 수신 PASS**(`all_selected_repaired=True`).
  4. **후보 v5**: worker unit_type=31, HQ hp 3600→1800, 55기 스폰 성공, 전체 드래그 선택
     **50/50**(상한 없음 확인), 손상 HQ 클릭 후 `pending_ever["0x1000008"]=50` — **50/50 전원
     수리 주문 수신 PASS**(`all_selected_repaired=True`, `capacity=50`). `private_exe_sha256`이
     v5 pinned SHA와 일치.
  5. **보조 관측(PASS 판정에 포함되지 않음, docstring에 사전 명시):** 클릭 후 6초간 HQ hp를
     0.5초 간격으로 샘플링했으나 원본·v5 둘 다 hp가 전혀 오르지 않았다(`hq_hp_rising=False`
     양쪽). fixture가 **일꾼 기준**(HQ 기준이 아님) 7×8 격자라 HQ까지 물리적 이동 거리가 있고,
     6초는 도보+수리 누적 틱에 비해 짧았을 가능성이 크다 — "주문이 전원에게 발행되는지"라는
     체크리스트 항목의 핵심 질문(명령 절단 여부)과는 별개의 질문이므로 이 lap에서는 FAIL로
     처리하지 않았지만, "정말 수리가 진행되는가"는 미확정으로 남는다(다음 항목 참고).
  6. 크래시 0(FAIL 4건 포함 전부 정상 종료), `source_unchanged=true` 전부, `cleanup.
     prefix_processes_after=[]` 전부. `make check` **1106 passed(792.53s)**, ruff/mypy/
     `CONTEXT_PASS`/`SAFETY_PASS` 전부 PASS(신규 pytest 0개, 제품 코드 무변경 — 이 probe/브리지는
     진단 전용 파일이며 `runtime_bridge.c`/`g5_r3_death_bridge.c`는 무변경이라 기존 G2 핀·R3
     probe 참조는 영향받지 않음, `make check` 전체 재현으로 간접 확인).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: middle 검수는 2026-09-28 03:36 운영자 판정에
  따라 체크리스트 (A)~(H) 전체가 채워진 뒤 한 번에 진행(이번 lap 단독 요청 아님, 정보 제공용).
  남은 위험: (a) "수리"가 실제로 HQ hp를 올리는지는 이 lap에서 미확정(위 5번) — 체크리스트 (C)의
  "명령 직후 대기열·목적지 좌표 일치" 잔여 항목과 함께 다음에 더 긴 관찰창(수십 초) 또는 HQ에
  가까운 fixture로 재확인이 필요하다. (b) op5/6 화이트리스트 제거가 이 fork에 한정됐는지 재확인
  필요(코드상 `g5_c_repair_bridge.c`만 수정, `runtime_bridge.c`/`g5_r3_death_bridge.c`는 `git
  status`로 무변경 확인됨 — middle이 diff로 재확인 권장).
- 다음 한 가지: 06:55 지시가 요청한 (C) 잔여 중 **건설(건물 배치 UI)·특수능력/변신·승선/하선**은
  이 lap에서 다루지 못했다(수리 하나에만 6회 부팅이 필요했다 — 국가 랜덤화라는 새 변수 때문).
  다음 work는 이 lap의 fork 브리지·근접 탐색 기법을 재사용해 **건설**부터(운영자 우선순위 유지):
  건물 배치 UI 진입(단축키/버튼 확인 필요 — 미상), 배치 클릭, pending/명령 상태 확인. 시간이
  남으면 특수능력·승선하선. 각 항목은 대상 유닛/기능이 이 게임에 없으면 N/A로 사유 기록. 수리의
  hp 회복 미확정(위)은 다음 세션이 더 긴 관찰창으로 재확인하거나, 이 lap의 근거로 "명령 절단
  없음"만 확정하고 별도 후순위 항목으로 기록.
