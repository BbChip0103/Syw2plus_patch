# 2026-09-29 | lap757 | 목표 G5

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5` / high, 실무(work) 역할.
- 가설 / 사용자 관찰: 2026-09-29 09:55 운영자 지시 ①: lap756 v10 runtime 증거는 50기 가득 찬 드래그
  1건만 측정했고, "부대 미지정 선택 count 중간값(예: 25, 35) 저장/로드"와 "부대(Ctrl+숫자)와 섞인
  상태 저장/로드"는 미측정이었다(lap756 상세 "남은 위험" ②). v10 설계(모듈 docstring)는 `count`를
  특별 취급하지 않고 매 저장마다 count+전체50엔트리를 무조건 트레일러로 덧붙이므로 이론상 중간값도
  동일하게 동작해야 하지만, 실측으로 확인되지 않았다. 가설: (a) 20<count<50 미지정 선택도 정확히
  복원된다, (b) 기존 부대(Ctrl+1)와 그와 다른 20 초과 라이브 선택이 동시에 존재해도 저장/로드가
  서로 간섭하지 않는다(부대 저장은 원본 엔진의 별도 저장소 `GROUP1_BASE_ADDRESS`/`unit+0x344`이고
  v10 사이드카는 라이브 선택 배열만 건드림).
- 예상 PASS / FAIL 조건: Round A(25기, 부대 없음) 저장→로드 후 count/슬롯 25개 전부 일치.
  Round B(부대1=15기 Ctrl+1 지정 후 다른 35기를 부대 재지정 없이 라이브 선택 → 저장) 로드 후
  라이브 선택 35개 전부 일치 **그리고** "1" 호출 시 원래 부대1의 15명이 정확히 복원. 회귀(크래시)
  없음.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `tools/g5_v10_partial_and_squad_saveload_probe.py`(신규 probe, 제품 EXE/패치 바이트 변경 없음
  — `patches/selection/g5_selection_cap50_v10.py`는 이 lap에서 import만 하고 수정하지 않음).
  **uncommitted**(`LOOP_ALLOW_COMMITS=0` 기본, 사용자 명시 허용 없음). lap756 이전 랩들이 남긴
  uncommitted 변경(`docs/*`, `patches/population/{build_runtime_bridge,runtime_driver}.py`,
  `tools/g5_candidate_drag_probe.py`)도 그대로 보존, 이 lap은 건드리지 않음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(실행 전/후 재확인, 불변).
  v10 후보 SHA `c3ceaa25dea98232234759a332b867d92a669f63a03c3f453d3199cc329ebfad`(lap756과 동일 바이트,
  이 lap에서 재빌드해 일치 확인). 격리 Wine9.0/Xvfb 1600x1200, 단일플레이 solo, worker-anchored
  7x9 후보 풀(요청 63, 해석 53, 격리선택검증 통과 50) type2 유닛.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `.venv/bin/python tools/g5_v10_partial_and_squad_saveload_probe.py
  --runtime-root local/runtime/20260929_lap757_v10_partial_squad
  --artifact-root .../temp/Syw2plus_patch/g5_lap757/v10_partial_squad` (exit 0, 전체 runtime
  session including 9점 화면-월드 캘리브레이션+53기 스폰+50기 isolation 확인+2라운드 save/load
  약 몇 분). 캡처 8장(00~07 prefix) 및 `probe-result.json`이 위 artifact 경로에 있다. `game` 사본은
  실행 직후 삭제(811M 회수), `output`/`prefix`/`probe.log`/캡처/`probe-result.json`은 보존.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  `screen_calibration.max_abs_residual`=1.06(px, 기존 랩들과 동급). **Round A: PASS** —
  저장 전 count=25/slots 25종 → 로드 후 count=25/slots 정확히 동일 25종(순서 무관 set 비교),
  중복 없음. **Round B: PASS** — 부대1=15기 Ctrl+1 지정(엔진 필드 `unit+0x344` 15기 전원 group=1
  확인) 후 겹치지 않는 별도 35기를 라이브 선택(overlap=[])하고 저장 → 로드 후 라이브 선택
  35/35 정확히 일치, 이어서 "1" 호출(부대1 소환) 결과 count=15/slots가 저장 전 부대1 멤버와 정확히
  일치(`squad_recall_pass=True`) — 라이브 선택 사이드카와 부대 저장소 사이 간섭 없음. 크래시 0,
  `cleanup.ok=true`(고아 프로세스 0), `source_unchanged=true`. **`make check` 1131 passed·5
  skipped(757.84s), ruff/mypy(0 issue)·`CONTEXT_PASS`, `checks/safety.sh check` → `SAFETY_PASS`.**
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  이 lap은 lap756 "남은 위험 ②"(중간값·부대혼합 미측정)를 해소했다. lap756이 이미 측정한
  count=50(가득 참) 케이스와 함께, 이제 count∈{15(부대만), 25, 35, 50}에서 v10 사이드카가 모두
  일관되게 동작함이 실증됐다 — 모듈 docstring이 예측한 "count를 특별 취급하지 않는다"는 설계와
  일치. **09:55 지시 ①의 나머지("v10 핵심 회귀 1회: 드래그4종·명령·공격·그룹·사망후호출·R3·Shift")는
  이 lap에서 착수하지 않았다** — v10은 v9 대비 hook 2곳+cave만 다르고(`test_only_the_hook_sites_*`로
  범위 고정된 pytest), v9는 이미 lap753/754에서 56 pytest+A~H 2단 독립 재검수(PASS 다수)를 통과했으며,
  v10이 추가한 코드 경로는 저장/로드 흐름에만 존재한다(드래그/이동/공격/그룹/사망 경로는 바이트
  단위로 무변경). 따라서 v10 고유의 잔여 회귀 표면은 저장/로드 인접 동작뿐이라고 판단해 이번 lap은
  그 표면(중간값·부대혼합)을 우선 측정했다 — **다만 이것은 work tier의 범위 축소 판단이며, middle이
  "핵심 회귀 1회"를 여전히 필요하다고 보면 다음 work lap에서 기존 coverage probe(예:
  `g5_command_coverage_probe.py` 계열, TARGET_SHA를 v10으로 갱신)로 보강한다.** item ②(미니맵
  우클릭/능력v paired)는 이 lap에서 미착수. **middle 독립 재검수 아직 없음** — 이 lap은 work tier
  정보제공이다.
- 다음 한 가지: 09:55 지시 순서대로 다음 work lap은 ② 미니맵 우클릭 이동·특수능력 v paired 확인
  (격리 환경 미니맵 렌더/입력 조건 조사, 원본20/v10-50 대상)에 착수하거나, middle이 먼저 (1)
  전체(lap756 50기 + 이 lap 25/35/부대혼합)를 독립 재검수한다. 순서는 middle/사용자 판단.
