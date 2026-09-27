# 2026-09-27 | lap 696 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code Sonnet 5(claude-sonnet-5), 실무(work) 역할.
- 가설 / 사용자 관찰: STATUS/APPROVALS 2026-09-27 00:05 운영자 판정(lap694 승격 해소) 마지막 단계이자
  lap695 handoff ①: 8인 전원 `used=10000`(lap695, 전역풀4092)이 확정된 상태에서 **저장→로드 1회** 후에도
  8인 전원의 회계(`used/count/count_cap/cap`)가 유지되는지 raw로 확인한다. UI pause-menu 좌표 재사용은
  기각했다 — G5의 저장/로드 캘리브레이션(`PAUSE_SAVE_POINT` 등)은 1600×1200 데스크톱에서 나온 값이고
  이 G2 헤드리스 설정은 1024×768이라 좌표를 그대로 이식할 근거가 없다. 대신 브리지가 이미 노출한 원본
  save/load 함수 직접 호출 경로(`op=2`→`0x440c20`, `op=3`→`0x440ff0`, `runtime_env._g2_lifecycle_native_op`,
  기존 G2 24k 라이프사이클 코드에서 이미 검증된 경로)를 재사용해 UI 좌표 추측 없이 raw로 저장/로드한다.
- 예상 PASS / FAIL 조건: 로드 후 8인 전원이 `used==10000`이고 로드 전과 동일한 `count/count_cap/cap`이면
  PASS. 하나라도 어긋나면 FAIL_SAVE_LOAD_MISMATCH.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 전부 uncommitted(LOOP_ALLOW_COMMITS=0).
  기존 `tools/g2_supply10000_pool4092_eight_owner_probe.py`에 옵트인 `--save-load` 플래그를 추가한
  최소 diff만 — 기본값 `False`는 lap695의 정확히 같은 동작(신규 인자 없이 호출 시 바이트 단위로 동일)을
  보존한다. 추가 로직: 8/8 목표 도달 확인 뒤 `SAVE_LOAD_SLOT=1`로 `op=2` 저장(대상 슬롯이 이전에 없어야
  함을 사전 확인) → 저장 파일 존재/크기 확인 → `op=3` 로드 → `ps==3` 대기 → 8인 전원 `player_summary`
  재조회 후 저장 직전 값과 비교. 새 파일 없음(기존 헬퍼 재사용), 새 테스트 없음(이 저장소 관례상 probe
  오케스트레이션 스크립트 자체는 별도 pytest 대상이 아니며 `patches/population/test_*`가 바이트 패치만
  검증). 원본/참고 저장소 무변경.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 SHA
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(`[ESL]Syw2plus/[HQ]Syw2plus 2002.exe`,
  실행 전후 불변, `source_unchanged: true`). 후보는 lap695와 동일한 결정적 빌드
  (`g2_supply10000_pool4092_owner500.create_copy`, capacity 4093). fixture는 lap692/694/695와 완전히
  동일(owner당 type103x153+type5x1, 156기, used=10000). 활성 8인(`_custom_game_chain_inject_g2_eight_seed42`),
  지도 100x100.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `PYTHONPATH=. .venv/bin/python tools/g2_supply10000_pool4092_eight_owner_probe.py --runtime-root
  local/runtime/lap696_saveload --artifact-root /home/dev_00/sharedfolder/260320_Syw2plus/temp/
  Syw2plus_patch/g2_capacity/20260927_lap696_pool4092_eight_owner_saveload --save-load`.
  결과 JSON `<artifact-root>/probe-result.json`, wine/xvfb 로그 `<artifact-root>/probe.log`. 저장 파일
  자체는 격리 런타임 안(`local/runtime/lap696_saveload/20260927_004111_731380_0/game/save/save001.dat`,
  이후 게임 사본과 함께 삭제됨, SHA256은 결과 JSON에 보존:
  `14c5972363e041dc79ec2e3367da4eb49329f3c802a9a30d837a48b76e42d5f4`). `make check` 로그
  `logs/gates/20260927_lap696_make_check.log`. safety 로그는 stdout(`SAFETY_PASS`)만.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **PASS_ALL_EIGHT_SUPPLY10000_SAVE_LOAD.** 저장 직전
  owner0~7 전원 `used=10000, count=156, count_cap=500, cap=10000`(lap695와 동일). native `op=2`
  `raw_return=1`, `ok=true`, 저장 파일 생성 확인(0바이트 아님). native `op=3` `raw_return=1`, `ok=true`,
  로드 후 `ps==3` 도달, tick이 18→(로드 직후)18로 재설정(저장 시점 tick과 일치, fresh-state 정합).
  **로드 후 owner0~7 전원 `used=10000, count=156, count_cap=500, cap=10000` 유지**
  (`owners_ok_after_load: 8`). 원본 SHA 실행 전후 불변, cleanup ok(prefix 잔여 프로세스 0), 크래시 0.
  `make check` **1019 passed(828.01s)**(신규 테스트 없음, lap695와 카운트 동일 — 이 lap은 오케스트레이션
  스크립트만 수정), ruff/compileall/mypy/`CONTEXT_PASS` 전부 PASS, `checks/safety.sh check` **SAFETY_PASS**.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: `--save-load` 플래그는 옵트인이라 기존 lap695 무인자
  호출과 동작이 바이트 단위로 동일(회귀 없음). **남은 위험/미해결:** (1) lap695가 이미 밝힌 대로
  "detailed" 전역 유닛 열거(`global_live_count`)가 이번에도 저장 전/후 모두 `0`을 반환 — 이번 lap은
  PlayerStruct 회계만 확인했고 전역 풀 자체의 중복/손상 없음은 여전히 별도 도구 수리 없이는 확인
  불가(안전 규칙 요구사항 미해결, lap695와 동일 한계 지속). (2) 저장 슬롯은 1회(slot=1)만 확인했고
  24k/144k 등 장시간 안정성·멀티 동기화는 이번 lap 범위 밖. 이 결과는 아직 middle 독립 검수 전이다.
- 다음 한 가지: STATUS lap695가 남긴 두 과제 중 ①(저장→로드)은 이번 lap이 완료했다. 남은 것은
  ② `build_runtime_bridge.py`의 "detailed" 유닛 열거가 `active_slot_list` 등 6-영역 relocation의 나머지
  3영역 새 주소를 반영하도록 고쳐 전역 유닛 수/중복 여부를 raw로 검증하는 것(안전 규칙이 요구하는 "풀
  손상 아님" 증거) — 다음 work가 middle 회부 없이 바로 진행할 수 있다. ①②가 모두 끝나면 G2 8인×10000
  전체를 middle 독립 검수로 올린다.
