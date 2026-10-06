# 2026-09-28 | lap 728 | 목표 G5

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5`, 실무(work, 구현·실행).
- 가설 / 사용자 관찰: 2026-09-28 05:36 운영자 판정 — lap727 raw에서 원본 `shift_click_unit`=2→
  `shift_click_second_unit`=3, v5는 1→2로 v5 첫 추가가 미반영됐을 가능성(사용자가 G2 빌드에서 본 증상과
  동일 우려). 원본의 시작값 2 자체가 lap726/727이 문서화한 조밀 55기/1타일 간격 fixture의 화면상 스프라이트
  겹침 아티팩트일 가능성이 큰데, 그 겹침을 논증이 아니라 **애초에 겹치지 않는 배치**로 제거하고 유닛 1기
  선택 → 선택 안 된 유닛 5기를 차례로 Shift+클릭하며 매 단계 count·슬롯 포함 여부를 원본/v5 paired로
  raw 측정하라는 지시(다음 work 최우선).
- 예상 PASS / FAIL 조건: PASS = Shift+클릭마다 count가 정확히 1씩 늘고, 이전에 선택된 슬롯이 전부 유지되며,
  새로 클릭한 슬롯이 그 단계에 나타난다(6단계: 최초 plain 클릭 1 + Shift 5회 → 1,2,3,4,5,6). 사전 조건으로
  각 후보 유닛이 **단독 plain 클릭 시 정확히 count=1·그 슬롯만** 선택되어야(격리 확인) 다음 Shift 단계가
  유효하다. FAIL = 어떤 단계에서 count가 안 늘거나, 이전 슬롯이 빠지거나, 새 슬롯이 없거나, 격리 확인
  자체가 실패(겹침 재현).
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  - 신규 `tools/g5_shift_click_add_probe.py`(SHA256
    `760d2935278017c52f99bcd3d0ecdff3c5087b2d2282e7eb0697a34bc4a891e2`). `g5_command_coverage_probe.py`/
    `g5_worker_relative_move_attack_probe.py`와 같은 solo-lobby 부트스트랩·9점 화면↔월드 아핀 보정을 재사용하되,
    55기 밀집 격자 대신 **worker 기준 맨해튼거리 ≥3인 희소 오프셋 10개**(`CANDIDATE_OFFSETS`)에서 화면에 보이는
    것만(최대 10개) 1기씩 스폰하고, 이번 lap이 새로 추가한 **격리 확인 단계**(각 후보를 단독 plain 클릭했을 때
    `count==1`이고 그 슬롯만 나오는지)를 통과한 것 중 6개를 순서대로 사용한다. 이 파일을 참조하는 pytest 없음
    (`grep -rl g5_shift_click_add_probe tests/` 결과 없음, 기존 G5 probe 도구들과 동일 패턴).
  - `patches/selection/g5_selection_cap50_v5.py`/원본 EXE 무변경(읽기만). 커밋 없음(uncommitted,
    `LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(양 실행 전후 `source_unchanged=true`).
  v5 후보 `29e61074c622c77debb5053a412e3337fc8100f1eda29bd68efb163b1a9ee146`(lap723~727과 동일). 격리
  Wine/Xvfb 1600×1200, PS3 solo, owner0. fixture는 이번 lap 전용 희소 배치 — worker(slot1198) 주변
  `(-3,-3),(3,-3),(-3,4),(3,4),(0,-3),(0,4),(-3,0),(3,0),(-3,1),(3,1)` 오프셋 SEED_TYPE=2 각 1기(화면 밖으로
  걸러진 것 제외, 원본·v5 둘 다 9개가 화면 안). 소스 `[ESL]Syw2plus`(SHA 위와 동일).
- 실행 명령 / 로그 / 캡처 경로 및 해시: 전체 artifact
  `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260928_lap728_shift_click_add/`
  {shift-original, shift-candidate-v5}/.
  1. `PYTHONPATH=. .venv/bin/python tools/g5_shift_click_add_probe.py --variant original
     --runtime-root local/runtime/lap728_shift_orig --artifact-root .../shift-original` → `COMPLETE None`.
     결과 JSON SHA256 `f401134fa198b5abe3406028ccb88aac95d9702f968917c0fbce9b860011b06d`.
  2. 같은 명령 `--variant candidate --runtime-root local/runtime/lap728_shift_v5
     --artifact-root .../shift-candidate-v5` → `COMPLETE None`. 결과 JSON SHA256
     `5f7f988ac81146653e22b59d3cfb0819118f7fc2369727812b0c53a91658d33b`.
  3. `make check`(foreground nohup + poll, 로그 `logs/gates/20260928_lap728_make_check.log`),
     `bash checks/safety.sh check`.
  4. 각 run 뒤 `local/runtime/lap728_shift_*/*/game`(약 800MB씩) 삭제, output/manifest/prefix/log는 보존
     (디스크 위생). `cleanup.prefix_processes_after=[]` 2/2로 고아 프로세스 없음 확인.
  - 첫 시도(현재 우선 재실행분에는 없음, 근접 삭제됨)는 화면 캘리브레이션 드래그 전 미니맵 좌클릭
    warm-up 스텝을 빠뜨려 `worker not selected for calibration`(count=0)으로 FAIL — 기존 coverage
    probe와 동일한 `click(MINIMAP_CLICK); sleep(1)` 스텝을 추가해 통과(도구 자체 버그 수정, 제품 코드
    무관).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  1. **격리 확인 = 원본·v5 둘 다 9/9 PASS**(`isolation_summary={'checked': 9, 'isolated': 9}` 양쪽 동일).
     희소 배치(맨해튼거리≥3)에서는 단독 plain 클릭이 매번 정확히 그 유닛 1기만 선택했다 — lap726/727의
     조밀 fixture 겹침 아티팩트가 **배치 밀도 문제였음을 직접 재현으로 확인**(추측이 아니라 반증).
  2. **Shift+클릭 개별 추가 6단계 전부 PASS(원본·v5 둘 다, raw)**:
     - 원본: 순서 슬롯 `[1194,1193,1192,1191,1190,1189]`, count 1→2→3→4→5→6, 매 단계
       `new_slot_present=True`·`all_prior_present=True`.
     - v5: 순서 슬롯 `[1194,1193,1192,1195,1190,1189]`(스폰 슬롯 배정만 다름, 개수 무관), count도
       동일하게 1→2→3→4→5→6, 매 단계 `new_slot_present=True`·`all_prior_present=True`.
     - **lap727 05:15 관찰(원본 2→3, v5 1→2)은 결함이 아니라 조밀 fixture 스프라이트 겹침 아티팩트였다는
       잠정 판단이 이번 격리 재실행으로 확정(CONFIRMED)됐다** — 겹침을 제거하면 원본·v5 둘 다 매 Shift+클릭이
       정확히 +1이고 시작값도 둘 다 1(정상)이다.
  3. **보너스 확인(6기 전체 이동 명령 수신) = PASS(원본·v5 둘 다)**: 최종 6기 선택 상태에서 우클릭 이동을
     내리자 `seen_move`가 6슬롯 전부 `True`(2초 창 안에 `command==3` 관측) — Shift로 추가된 유닛도 이후
     명령을 정상 수신.
  4. 크래시 0(2/2), `source_unchanged=true`(2/2), `cleanup.prefix_processes_after=[]`(2/2, 고아 없음).
  5. `make check` **1106 passed(764.94s)**, ruff/compileall/mypy/`CONTEXT_PASS` 전부 PASS, `SAFETY_PASS`.
     신규 pytest 0개(제품 코드 무변경, probe 도구만 신규).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - 이번 lap은 6개 슬롯까지만 확인했다 — 21~50번째 구간(부대필드 `+0x344` 경로, lap661~667에서
    별도로 검증된 영역)에서의 Shift 개별 추가는 범위 밖(체크리스트 (D) 부대 항목에서 다룰 사안).
  - 격리 확인 자체가 이번 lap의 신규 방법론(기존 도구는 anchor1/anchor2를 겹침 여부 검증 없이 사용)이므로,
    (A) 정적 전수 표에 "격리 검증 방법"으로 한 줄 추가할 가치는 있으나 이번 lap에서는 하지 않음(범위 밖,
    필요 시 다음 (A) 갱신 때 참고).
  - 독립 검수: 아직 없음(work tier 산출, 2026-09-28 03:36 운영자 판정에 따라 middle은 체크리스트 전체가
    채워진 뒤 한 번에 진행).
  - 사용자 승인: 없음(G5 확정은 체크리스트 A~H 완료 후).
- 다음 한 가지: 이번 lap으로 **(B) Shift+클릭 개별 추가 격리 재확인 = PASS로 확정**, 따라서 **(B) 전체
  완료**(드래그/Shift 추가·제거/ALT·Ctrl/더블클릭 선택/포트레이트 해제(미지원)/51번째 거부/R3 사망 3위치/
  이번 격리 재확인 — 전부 PASS 또는 원본과 동일 동작). 다음은 **(C) 명령 전부**: 일꾼 채집/건설/수리 등
  특수 명령, 특수능력/변신, 승선/하선 등 툴바 전체 버튼과 단축키, 명령 직후 대기열·목적지 좌표 일치. 이어서
  (D) 부대(Ctrl+숫자 지정·호출·Shift+숫자 추가·부대원 사망 후 호출, 특히 21~50번째 구간)~(H) 순서.
