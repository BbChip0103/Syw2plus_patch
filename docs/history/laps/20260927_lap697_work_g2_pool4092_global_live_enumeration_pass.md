# 2026-09-27 | lap 697 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code Sonnet 5(claude-sonnet-5), 실무(work) 역할.
- 가설 / 사용자 관찰: STATUS/INBOX 2026-09-27 01:05 운영자 지시(lap696 후속, middle 전 마지막 1바퀴):
  전역 유닛 열거(`global_live_count`/active_slot_list 등)를 G2 pool4092 6-영역 재배치 주소로 고쳐,
  8인×10000 fixture에서 전역 live=1248(8×156), 슬롯 중복 0, owner별 count 합=전역 live, 저장/로드
  전후 동일을 raw로 확인한다. 근본 원인 가설: lap695/696의 `global_live_count`가
  `read_state(pid, detailed=True)`를 **profile 인자 없이(기본값 "original")** 호출하고 있었다 —
  `POOL_PROFILE_LAYOUTS.get(profile, STOCK_POOL)`이 등록되지 않은 profile에는 항상 STOCK_POOL
  (capacity1200, 옛 stock 주소 `0x0066B790`/`0x008990C8`)로 폴백하므로, 이 6-영역 재배치 후보에서는
  이미 다른 데이터로 재사용된 옛 주소를 읽어 항상 0을 반환한 것으로 추정했다.
- 예상 PASS / FAIL 조건: (a) `g2_supply10000_pool4092_owner500` profile을 `POOL_PROFILE_LAYOUTS`에
  올바른 주소로 등록하고 `detailed` 상태에 `active_slot_list`(6번째 영역, count+entries)를 디코드하면
  8인 fixture 라이브 실행에서 `exists_bitmap_count == active_slot_list_count == owner_count_sum == 1248`,
  `duplicate_count == 0`, `matches_existence_bitmap == true`가 나와야 PASS. 저장→로드 후에도 동일 값
  유지(`active_slots_unchanged_by_load == true`)면 전체 PASS. 가설이 틀렸다면(예: 진짜 원인이 다른
  주소 오류) 여전히 0이 나오거나 값이 어긋난다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 전부 uncommitted(LOOP_ALLOW_COMMITS=0).
  - `patches/population/runtime_driver.py`: `POOL_PROFILE_LAYOUTS`에 `g2_supply10000_pool4092_owner500`
    항목 추가(`(4093, 0x0108C000, 0x017E29F8)`, `full_tail_relocation_storage_layout_v1.layout(4093)`의
    unit_pool/unit_existence 출력과 동일함을 신규 테스트로 고정). 신규 `FULL_REGION_PROFILES` 매핑
    (profile → capacity)과 `state(detailed=True)`에 `active_slot_list` 디코드 블록 추가: 6번째 영역의
    trailing WORD 카운터 + entries를 읽어 `count`/`slots`/`duplicate_count`/`matches_existence_bitmap`을
    반환. 기존 `POOL_PROFILE_LAYOUTS`/`exists` 로직과 다른 profile들의 동작은 무변경(다른 profile은
    `FULL_REGION_PROFILES`에 없어 새 블록을 건너뜀).
  - `tools/g2_supply10000_pool4092_eight_owner_probe.py`: `global_live_count`가 profile 없이 호출하던
    버그를 고쳐 새 `PROFILE = "g2_supply10000_pool4092_owner500"` 상수로 `read_state(..., profile=PROFILE)`
    호출. `global_live_snapshot()` 신규(전 owner 합/active_slot_list/existence bitmap/중복 여부를 한
    번에 반환). fixture 완료 시점과 저장/로드 후 시점 각각에 `global_pool_integrity`/
    `loaded_global_pool_integrity` raw 판정 블록 추가, 무결성 실패 시 `FAIL_GLOBAL_POOL_INTEGRITY`/
    `FAIL_SAVE_LOAD_MISMATCH`로 상태를 낮춤(숨기지 않음).
  - 신규 `patches/population/test_runtime_driver_pool4092_global_live.py`(6 테스트, gdb/Wine 불필요):
    등록된 주소가 순수 기하 계산(`layout(4093)`)과 일치하는지, `state(detailed=True)`의
    `active_slot_list` 디코드가 중복/불일치를 raw로 잡아내는지 fake-memory로 검증.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 SHA
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
  (`[ESL]Syw2plus/[HQ]Syw2plus 2002.exe`, 실행 전후 불변, `source_unchanged: true`). 후보는 lap695/696과
  동일한 결정적 빌드(`g2_supply10000_pool4092_owner500.create_copy`, capacity 4093,
  candidate_sha256 `11aa9e796805d3e0c29b55de957d003c521e74f9aeddf4e3478bd743842e5b53`), 브리지
  `--unit-pool-capacity 4093`(bridge_sha256 `28980e42274f15eb56a81a5b201b0e66ca9dad2688d706d59610ee8fcbcca440`,
  lap695와 동일). **2026-09-27 lap699 정정(lap698 결함4 재조사):** 이 값은 `build_runtime_bridge.py`
  자체 매니페스트(`supply_bridge_build.json`)가 적는, 빌드에 쓴 `runtime_bridge.c` 원문 소스의 해시다
  — lap699가 lap695/697/699 세 lap의 보존 아티팩트 `.c` 파일을 직접 재해시해 전부 `28980e42…`로
  동일함을 재확인했다(소스 무변경이므로 당연히 안정적). lap698이 "불일치"로 지목했던
  `51168d40…`(695)/`bb3ae221…`(696)/`42d2eda1…`(697)/`0d848884…`(699)는 이 문서의 값과 **다른 대상을
  잰 값**이다 — 이 probe 스크립트의 `provenance.bridge_sha256`은 `sha256(bridge)`로 **컴파일된
  `_inmm.dll` 바이너리**를 해시하며, gcc/ld가 PE에 남기는 빌드시점 비결정적 바이트 때문에 소스가
  같아도 빌드마다 달라진다(lap699가 두 lap의 보존 `_inmm.dll`을 직접 재해시해 확인). 실제 결함은
  "브리지가 라운드마다 바뀌었다"가 아니라 코드베이스에 `bridge_sha256`이라는 같은 이름이 서로 다른
  두 대상(소스 vs 컴파일된 DLL)에 쓰이는 명명 충돌이다. fixture는 lap692/694/695/696과 완전히 동일(owner당 type103x153+type5x1, 156기,
  used=10000). 활성 8인(`_custom_game_chain_inject_g2_eight_seed42`), 지도 100x100.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `PYTHONPATH=. .venv/bin/python tools/g2_supply10000_pool4092_eight_owner_probe.py --runtime-root
  local/runtime/lap697_pool4092_global_live --artifact-root /home/dev_00/sharedfolder/260320_Syw2plus/
  temp/Syw2plus_patch/g2_capacity/20260927_lap697_pool4092_global_live --save-load`. 결과 JSON
  `<artifact-root>/probe-result.json`, wine/xvfb 로그 `<artifact-root>/probe.log`. `make check` 로그
  `logs/gates/20260927_lap697_make_check.log`. `checks/safety.sh check` 로그는 stdout(`SAFETY_PASS`)만.
  단위 테스트: `python3 -m pytest patches/population/test_runtime_driver_pool4092_global_live.py -q`
  (6 passed, gdb/Wine 불필요, 순수 fake-memory).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **PASS_ALL_EIGHT_SUPPLY10000_SAVE_LOAD.** raw 결과
  (`probe-result.json`): `pre_fixture_global_live=16`(HQ+worker x8), fixture 완료 후
  `final_global_live=1248`, `global_pool_integrity = {owner_count_sum: 1248, active_slot_list_count: 1248,
  exists_bitmap_count: 1248, duplicate_count: 0, matches_existence_bitmap: true,
  owner_sum_matches_active_count: true, owner_sum_matches_exists_count: true}` — **가설 확정**(profile
  누락이 원인이었고, 이번 수정 후 세 지표가 8×156=1248로 정확히 일치, 중복 0). 저장(`op=2`,
  `raw_return=1`)→로드(`op=3`, `raw_return=1`) 후 `loaded_global_pool_integrity`도 동일하게
  `{owner_count_sum: 1248, active_slot_list_count: 1248, exists_bitmap_count: 1248, duplicate_count: 0,
  matches_existence_bitmap: true, active_slots_unchanged_by_load: true}`, `owners_ok_after_load: 8`.
  원본 SHA 실행 전후 불변, cleanup ok(prefix 잔여 프로세스 0), 크래시 0, 게임 사본 자동 삭제(디스크 위생
  준수, 실행 후 여유 88GB). `make check` **1025 passed(755.05s)**, ruff/compileall/mypy/`CONTEXT_PASS`/
  shell -n 전부 PASS, `checks/safety.sh check` **SAFETY_PASS**. 신규 단위 테스트 6개 별도 PASS.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 이 수정은 `g2_supply10000_pool4092_owner500`
  profile에만 새 동작(active_slot_list 디코드)을 추가하며, 그 profile을 쓰지 않는 다른 모든 profile의
  `detailed` 동작은 무변경(if-분기가 `FULL_REGION_PROFILES.get(profile)` None일 때 건너뜀; 레거시
  n4001 계열 등은 등록돼 있지 않아 영향 없음). **남은 위험/미확인:** (1) `category_slot_list_a/b`(4번째,
  5번째 영역)는 이번 조사 범위 밖이라 디코드/검증하지 않았다 — 이 두 리스트가 무엇을 필터링하는지
  (문서 주석상 "semantics UNKNOWN"인 영역과 별개) 여전히 미상이며, 전역 풀 손상이 이 두 영역에서만
  발생하는 경우는 이번 검증으로 못 잡는다(unit_existence·active_slot_list 교차검증만 수행). (2) 24k/144k
  등 장시간 안정성, 멀티 동기화, 다른 저장 슬롯은 이번 lap 범위 밖. STATUS/INBOX가 요구한 "8인×10000
  fixture에서 전역 live=1248, 슬롯 중복 0, owner별 count 합=전역 live, 저장/로드 전후 동일"은 모두
  raw로 확인됐다 — **다음은 middle 독립 검수로 승격**할 조건을 충족했다고 판단한다(work tier 자체
  판단, middle 확정 아님).
- 다음 한 가지: G2 8인×10000 후보(v3: lap691~697 누적 — 전비10000, 4092-슬롯 풀, 개인500, 저장/로드,
  전역 유닛 열거 무결성)를 **middle 독립 검수로 승격**한다. middle은 필요하면 category_slot_list_a/b
  교차검증이나 다른 저장 슬롯 재현을 추가로 요구할 수 있다. middle PASS 후에는 사용자 3단 마일스톤
  판단(G2 8인×10000 안정성) 대기로 넘어간다.
