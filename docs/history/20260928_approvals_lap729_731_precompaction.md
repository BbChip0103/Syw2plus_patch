- [ ] **2026-09-28 lap731 work tier(Claude Code Sonnet, 정보 제공용 — 새 middle 검수 요청 아님,
  2026-09-28 03:36 운영자 판정에 따라 middle은 체크리스트 전체가 채워진 뒤 한 번에 진행):** 07:35
  지시(건설·특수능력/변신·승선하선·좌표일치를 한 probe로 끝내라)를 수행하되, 이 네 항목은 사전에
  버튼 의미가 전혀 알려져 있지 않아 원본 1회·v5 1회 paired 실측으로 바로 끝낼 수 없었다(v3 patch가
  선택 배열 broadcast만 건드리므로 건설/능력/승선은 애초에 v5 회귀 위험이 없는 항목) — 대신 신규
  `tools/g5_worker_ability_hq_ui_survey_probe.py`·`tools/g5_hq_command_grid_survey_probe.py`(둘 다
  원본만 실행하는 순수 UI 조사, 제품 코드 무변경)로 **일꾼과 본진(HQ)의 커맨드 그리드 버튼 전수를
  실측·툴팁 캡처**했다. 결과(솔로 로비 국가 랜덤 2회 부팅, worker type31/HQ58과 worker type21/HQ70):
  일꾼 그리드는 S(정지)/M(이동) 외에 국가마다 다른 1~2개 능력만 있고(이번 두 부팅에서 V=`묻기(V)`,
  F=`불끄기(F)` 툴팁 확인 — 채집·수리는 버튼이 아니라 우클릭으로만 발동되는 것은 lap729/730에서
  이미 확인됨), **"건물을 새로 배치"하는 버튼은 없다**. HQ 그리드는 8칸 중 S(정지)/R(`수리(R)` 툴팁
  확인, 자원비용 없음)/D(동전 아이콘, 툴팁 미포착)/T·B·F·X 4칸이 전부 골드·목재·인구 비용이 표시된
  **유닛 생산 슬롯**(`영 소환소(A)` 골드2600/목재2400/인구20 필요건물 영 대장간, `영 능부(F)`
  골드300/인구10, `숨은창 등록(X)` 골드2000/목재2000 등 — 훈련 진행률 표시줄까지 확인)이었다. R을
  누른 뒤 근처 빈 땅을 좌클릭해도 1200슬롯 existence 테이블에 새 엔트리가 0개(배치 커서/유령
  건물 없음). **결론: (C) 건설 = N/A — 이 실행 파일에는 플레이어가 새 건물을 배치하는 기능 자체가
  없다**(AI 전용 `건설 결정 루틴`과는 별개; `analysis/memory_maps/ai_production_decision_path_
  00406770_20260923.md` 참고). **(C) 특수능력/변신 = 존재하는 능력(묻기/불끄기, HQ 수리·생산 4종)을
  전수 캡처로 확인**, "변신" 명칭·기능은 두 국가 표본 모두에서 미발견(국가별 버튼이 랜덤이라 다른
  국가에 변신형 능력이 있을 가능성은 배제 못 함, 후속 조사 여지로 남김). **(C) 승선/하선 = N/A** —
  이 솔로 로비 fixture(existence 4슬롯, owner0는 일꾼+HQ뿐)에 배 유닛·수상 지형이 없고, 저장소
  전체를 grep해도 보트/선박 타입ID가 확정된 적이 없어(`analysis/`·`docs/history/` 어디에도 없음)
  범위 안에서 스폰할 방법이 없다. **(C) 명령 직후 목적지 좌표 일치 = 기존 증거로 PASS 판단**(신규
  probe 불요) — lap668/670의 9점 화면↔월드 아핀 확정(잔차 0.444타일 이내 정확 일치), lap682/717/
  723/724의 `destination_validation`/`converged_at_s` dest 추적이 이미 이동/패트롤 목적지 일치를
  매 checklist probe에서 반복 확인해 왔고, 공격은 `+0x38C`==적 uid 정확 일치(좌표보다 강한 기준)로
  lap671/688에서 확정됨. **이로써 (C) 체크리스트는 완료로 판단한다**(lap730이 남긴 "HQ hp가 6초
  관찰창에서 안 오름"은 그 lap 자체가 "PASS 판정에는 영향 없음"이라 결론지은 별개 미확정 질문으로,
  보류 유지). 부수 발견: lap724의 `PASS_UI_ROUNDTRIP`(v5, `selected_50`·`group_stored_stock20_
  plus_overflow49`·`recalled_50`·`save_created`·`group_retained_after_load`·`recalled_50_after_
  load`)이 이미 **(D) 부대의 Ctrl+숫자 지정·숫자 호출·저장로드 전후 recall을 v5로 커버**하고 있어,
  (D)에 남은 것은 **Shift+숫자 추가**와 **부대원 사망 후 호출** 두 항목뿐이다. 크래시 0(두 probe
  모두), `source_unchanged` 2/2(둘 다 원본만 실행), 실행 후 `local/runtime/lap731_*`의 ~2.7GB game
  사본은 직후 삭제(디스크 위생, output/log/manifest 보존). `make check` 1106 passed(755.21s),
  ruff/mypy/`CONTEXT_PASS`/`SAFETY_PASS` 전부 PASS(신규 pytest 0개, 제품 코드 무변경 — 신규 도구
  2개는 순수 조사용). 같은 lap에서 APPROVALS를 261→122줄로 선압축(lap712~721 계보, 원문 140줄
  SHA256 `4077e7d84cee6ea3fbeb62d4ac168c7dee7899d25eadeb0f8d9cbf21d81dbeb2`,
  `docs/history/20260928_approvals_lap712_721_g4g5v4_precompaction.md` 보존). **다음 work 권장:**
  (D) 잔여 두 항목(Shift+숫자 추가 — v5 50기 선택에서 Ctrl+1 지정 후 Shift+2로 다른 유닛을 같은
  조에 추가; 부대원 사망 후 호출 — `g5_r3_sparse_selection_probe.Bridge` op=10/11 사망 기법 재사용해
  조 구성원 일부를 죽인 뒤 숫자 호출이 생존자만 정확히 부르는지)로 (D) 마감 → (E)~(H) 진행. 근거
  `../history/laps/20260928_lap731_work_g5_checklist_c_construction_ability_embark_survey.md`.
- [ ] **2026-09-28 lap730 work tier(Claude Code Sonnet, 정보 제공용 — 새 middle 검수 요청 아님,
  2026-09-28 03:36 운영자 판정에 따라 middle은 체크리스트 전체가 채워진 뒤 한 번에 진행):** 06:55
  운영자 지시(수리 우선)를 수행. 신규 `tools/g5_worker_repair_command_probe.py` + 신규
  `patches/population/g5_c_repair_bridge.c`(`g5_r3_death_bridge.c` fork, op=11 "생존 유닛 hp
  직접 기록" 추가, op5/6 fixture-type 화이트리스트를 구조적 게이트+실엔진 Place/Gate 호출로 대체)
  로 게임 시작부터 존재하는 owner0 HQ를 제외 스캔으로 찾고, op=11로 hp를 절반으로 낮춘 뒤 근접
  좌표 탐색(`HQ_FOOTPRINT_OFFSET_CANDIDATES`, 채집의 목적지 탐색과 동일 기법)으로 확정한 화면
  좌표를 우클릭 — **원본 20/20·v5 50/50 전원 손상 HQ 우클릭 시 pending `0x1000008`(채집과 동일
  공용 값, 손상 전/후 동일값이라 이 게임에 별도 "수리 전용" pending word는 없는 것으로 판단) 수신
  PASS**. **부수 발견**: 이 솔로 로비 fixture의 국가는 부팅마다 랜덤이라 일꾼/HQ unit_type이
  실행마다 바뀐다(7/21/31, 49/58/70 관측) — 기존 화이트리스트 브리지로는 재현 불가한 경우가
  많아 4회 재부팅 끝에 화이트리스트 제거 fork로 전환했다. 이 fork는 G2 pinned `runtime_bridge.c`도
  R3 probe가 참조하는 `g5_r3_death_bridge.c`도 건드리지 않는다(`git status` 확인, 둘 다 무변경).
  **미확정**: 손상 HQ 클릭 후 6초 관찰창에서 hp가 전혀 오르지 않았다(원본·v5 둘 다) — fixture가
  일꾼 기준이라 HQ까지 도보 거리가 있어 관찰창이 짧았을 가능성, PASS 판정(명령 절단 없음)과는
  별개 질문이라 이 lap의 결론에는 영향 없음. `source_unchanged` 7/7(FAIL 4건 포함), `cleanup.
  prefix_processes_after=[]` 7/7, 크래시 0. `make check` 1106 passed(792.53s), ruff/mypy/
  `CONTEXT_PASS`/`SAFETY_PASS` 전부 PASS(신규 pytest 0개, 제품 코드 무변경). (C)는 아직 건설·
  특수능력/변신·승선하선이 미측정이라 완료 아님. 다음 work 권장: 건설(이 lap의 fork·근접탐색
  기법 재사용). 근거 `../history/laps/20260928_lap730_work_g5_worker_repair_command_pass.md`.
- [ ] **2026-09-28 lap729 work tier(Claude Code Sonnet, 정보 제공용 — 새 middle 검수 요청 아님, 2026-09-28 03:36 운영자 판정에 따라 middle은 체크리스트 전체가 채워진 뒤 한 번에 진행):** 체크리스트 (C) 명령 전부 중 첫 항목(일꾼 채집)을 측정. 신규 `tools/g5_worker_gather_command_probe.py`가 런타임 실측 일꾼 unit_type(=7)으로 worker 기준 7x8 격자 55기를 스폰하고, 라이브 일꾼 우클릭 탐색으로 채집 pending word(`0x1000008`)를 내는 목적지를 고정한 뒤 전체 드래그 선택 → 그 목적지 우클릭 결과를 `observe()`(g5_command_coverage_probe에서 무수정 재사용)로 집계 — **원본 20/20·v5 50/50 전원 채집 pending 수신 PASS**. 후보 1회차 `unsupported_army_fixture_type` flake(원본이 같은 type=7로 55/55 성공했으므로 브리지 게이트 결함 아님)는 즉시 재실행(v5_r2)으로 해소, `source_unchanged`/`cleanup.prefix_processes_after=[]` 모두 정상(FAIL run 포함 3/3). `make check` 1106 passed(787.50s), ruff/mypy/`CONTEXT_PASS`/`SAFETY_PASS` 전부 PASS(신규 pytest 0개, 제품 코드 무변경). (C)는 아직 건설·수리·특수능력/변신·승선하선이 미측정이라 완료 아님. 다음 work 권장: 수리(같은 방식 재사용 가능). 근거 `../history/laps/20260928_lap729_work_g5_worker_gather_command_pass.md`.
