# 2026-09-27 | lap 695 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code Sonnet 5(claude-sonnet-5), 실무(work) 역할.
- 가설 / 사용자 관찰: APPROVALS/STATUS 2026-09-27 00:05 운영자 판정(lap694 승격 해소, strategy 대행) —
  lap694가 확정한 전역 1200-슬롯 풀 병목을 (a) 고비용 타입 재탐색이 아니라 (b) 전역 풀 확장으로
  해소한다. 이미 실전 검증된 ESL 계열 4092-슬롯 풀 재배치(`g2_esl2606_pool4092_owner500.py`/
  `g2_esl2608_pool4092_owner500.py`, 개인500·공용4092)를 보호 원본(b56986e0) 기준 전비10000
  후보에 이식하고, lap694의 8인 probe를 재실행해 owner0~7 전원 `used=10000` 도달을 raw로 확인한다.
- 예상 PASS / FAIL 조건: 8인 전원이 `used>=10000`에 도달하면 병목 해소 확인
  (PASS_ALL_EIGHT_SUPPLY10000). 일부만 도달하면 여전히 병목(추가 조사 필요). 크래시/계정 불일치면 FAIL.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 전부 uncommitted(LOOP_ALLOW_COMMITS=0).
  신규 `patches/population/g2_supply10000_pool4092_owner500.py`
  (SHA256 `1c301c71b4bd6d385ec41a744d88a30a3d363c56191ce9c341bae1c6faf14a99`) — 보호 원본 위에서
  `g2_full_capacity_persistence_compat_v1.build_candidate(original, 4093)`(기존 검증된 6-영역 tail
  relocation + save/load 호환 헤더 체인, ESL 참조 바이너리 불필요, stock에 직접 적용)를 호출한 뒤
  전비10000(2자리 명령 치환), 개인로스터500(1자리 명령 치환), 유휴영웅 초상화 producer 탐색
  1200→4093(`g2_esl2606_pool4092_owner500.PRODUCER_LOOKUP_EDITS` 그대로 재사용, ESL 델타와 무관한
  보호 원본 .text 자리라 이식 가능) 세 가지만 겹쳐 적용. 신규 테스트
  `patches/population/test_g2_supply10000_pool4092_owner500.py`(9개, 전부 hash-guard/preimage
  검증, `Syw2plus/syw2plus_original.exe` 로컬 참조 fixture로 실행). 신규
  `tools/g2_supply10000_pool4092_eight_owner_probe.py`
  (SHA256 `aa240c334fc75b6d8b71b4f40d788bf84cbf426254508c3d0db630eaf41b82cf`) —
  lap694 probe를 새 후보/새 풀 용량(4093)으로만 교체한 것, fixture 구성·8인 활성화 로직은 lap694와
  동일. 기존 `patches/population/runtime_bridge.c`(lap692 allow-list, 무변경 그대로 사용),
  `patches/population/runtime_driver.py`, `tools/runtime_env.py`(lap693 경로 전환)는 이번 lap에서
  읽기만 함. 원본/참고 저장소 무변경.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 SHA
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(새 경로
  `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe`, 실행 전후 불변). 후보 SHA는 매 빌드 결정적으로 재계산됨
  (동일 원본 입력이면 항상 동일 바이트; `create_copy` 호출부에서 `candidate_sha256`로 자체 검증).
  브리지 SHA `28980e42274f15eb56a81a5b201b0e66ca9dad2688d706d59610ee8fcbcca440`
  (`--unit-pool-capacity 4093`로 빌드, `unit_pool_base=0x0108C000`, `unit_existence_base=0x017E29F8`).
  **2026-09-27 lap699 정정(lap698 결함4 재조사):** 이 값은 `build_runtime_bridge.py`가 자체
  `supply_bridge_build.json` 매니페스트에 적는 `bridge_sha256`(빌드에 쓴 `runtime_bridge.c`
  **원문 소스**의 해시)과 일치하며, 소스가 안 바뀌는 한 lap695/696/697/699 전부 동일하다(lap699가
  네 lap의 실제 보존 아티팩트 `.c` 파일을 재해시해 확인: 전부 `28980e42…`). lap698이 "불일치"로 지목한
  `51168d40…`/`bb3ae221…`/`42d2eda1…`(lap695/696/697)와 이번 lap699의 `0d848884…`는 **다른 것을
  잰 값**이다 — `g2_supply10000_pool4092_eight_owner_probe.py`의 `provenance.bridge_sha256`은
  `sha256(bridge)`로 컴파일된 **`_inmm.dll` 바이너리**를 해시하며(소스가 아님), gcc/ld가 PE에 남기는
  빌드시점 비결정적 바이트(타임스탬프 등) 때문에 소스가 동일해도 빌드마다 값이 달라진다(lap699가
  두 lap의 보존 `_inmm.dll`을 직접 재해시해 확인). 즉 실제 결함은 "브리지가 라운드마다 바뀌었다"가
  아니라 **코드베이스에 `bridge_sha256`이라는 같은 이름이 서로 다른 두 대상(소스 vs 컴파일된 DLL)에
  쓰이는 명명 충돌**이다. 위 문서 값은 전자(소스 해시, 안정적)를 정확히 인용한 것이었다.
  활성 8인(`_custom_game_chain_inject_g2_eight_seed42`, lap694와 동일 컨트롤 목표), 지도 100x100.
  owner별 fixture: type103(cost65) x153 + type5(cost35) x1(개인 154기 요청, 기존 HQ+worker 포함 총
  156기/owner) — lap692/694와 완전히 동일한 fixture 구성, 이번 lap의 유일한 변수는 전역 풀
  1200→4092(usable) 하나뿐.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `PYTHONPATH=. .venv/bin/python tools/g2_supply10000_pool4092_eight_owner_probe.py --runtime-root
  local/runtime --artifact-root /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/
  g2_capacity/20260927_lap695_pool4092_eight_owner_supply10000`.
  결과 JSON `<artifact-root>/probe-result.json`(schema
  `syw2plus.g2-supply10000-pool4092-eight-owner-probe.v1`). wine/xvfb 로그 `<artifact-root>/probe.log`.
  `make check` 로그 `logs/gates/20260927_lap695_make_check.log`. safety 로그는 stdout(SAFETY_PASS)만.
  단위 테스트: `PYTHONPATH=. .venv/bin/python -m pytest -q
  patches/population/test_g2_supply10000_pool4092_owner500.py` → 9 passed.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  **PASS_ALL_EIGHT_SUPPLY10000.** 8인 전원 chain-inject 생성 성공(PS7→PS3, 8인 모두 nonzero
  nation/ai role 확인). owner0~7 **전원 `used=10000, count=156, count_cap=500, cap=10000` 도달**
  (lap694에서 owner7만 `used=6845, count=107`로 거부됐던 것과 대조). `fixture_locked_after_
  accounting_failure` 잠금 0회, 크래시 0, cleanup ok(prefix 잔여 프로세스 0), 원본 SHA 실행 전후
  불변(`source_unchanged: true`). `make check` **1019 passed(769.54s)**(신규 테스트 9개 포함,
  lap694 대비 +9), ruff/compileall/mypy/`CONTEXT_PASS` 전부 PASS, `checks/safety.sh check`
  **SAFETY_PASS**. 이 결과는 2026-09-27 00:05 운영자 판정(전역 풀 확장 채택)이 예측한 대로
  8*156=1248 <= 4092(usable)이 실측으로 병목을 해소함을 확인한다.
  **미해결/알려진 한계:** `global_live_count()`(`read_state(pid, detailed=True)["units"]`)가
  이번 실행 전 구간에서 `0`을 반환했다(pre-fixture 16기가 있어야 할 시점 포함) — `player_summary()`
  가 읽는 PlayerStruct 필드(`used/count/cap`, 원본 게임의 전비 회계 그 자체)는 정상이지만, "detailed"
  전체 유닛 열거는 이번 6-영역 전체 relocation(카테고리 A/B·active_slot_list 포함) 후보에서
  깨져 있다. `build_runtime_bridge.py --unit-pool-capacity`는 `tail_relocation_storage_layout_v1`
  (pool+existence+age 3영역)만 반영해 브리지에 전달하며, active_slot_list 등 나머지 3영역의 새
  주소를 모른다 — "detailed" 열거가 그 리스트를 옛 주소에서 읽어 0을 얻는 것으로 추정(미검증 가설).
  즉 이번 PASS는 **PlayerStruct 회계 기준**으로 8/8 확인이며, **전역 유닛 풀 자체의 중복/손상 없음
  은 이 도구로 아직 별도 확인하지 못했다**(안전 규칙 "개체 제한/풀 손상... 실제 증거로 구분"에 따라
  명시). 저장/로드 1회(운영자 지시 마지막 단계)도 이번 lap 범위 밖(미실행).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 신규 파일 3개 추가, 기존 코드 무변경. `make check`
  카운트가 lap694(1010) 대비 +9(신규 유닛 테스트)로 정합적으로 증가했고 실패 0. 이 결과는 아직 middle
  독립 검수 전이다. 저장/로드, 24k/144k, 멀티 동기화, 전역 유닛 열거 도구 수리는 모두 미실측.
- 다음 한 가지: middle/strategy 판정 없이 바로 두 가지를 work가 진행할 수 있다 — ① 운영자 지시의
  마지막 단계인 **저장→로드 1회**(8인 fixture 상태에서 게임 자체 저장/로드 UI 또는 이미 검증된
  offline_storage/persistence 경로로, 로드 후 8인 전원 `used=10000` 유지 확인), ② `build_runtime_
  bridge.py`의 detailed 유닛 열거가 `active_slot_list`(6-영역 전체 relocation의 나머지 3영역) 새
  주소를 반영하도록 고쳐 전역 유닛 수/중복 여부를 raw로 검증(안전 규칙이 요구하는 "풀 손상 아님"
  증거). 둘 다 끝나면 middle 독립 검수로 G2 8인×10000을 올린다.
