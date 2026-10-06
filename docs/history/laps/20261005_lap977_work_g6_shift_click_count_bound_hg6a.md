# 2026-10-05 | lap 977 | 목표 G6 (H-G6a)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5` / high, 실무(work) 1 lap.
- 가설 / 사용자 관찰: 이식판의 Shift+클릭 두 번째 루프(`0x41DD82..0x41DDE7`)가 선택 개수가 아니라 칸 수 전체를 돌아 빈 칸(id 0)의 owner를 local과 비교한다 → local≠owner(id 0)이면 추가가 중단된다. 루프를 `edi < [esp+0x10]`으로 한정하면 풀린다(카드 `docs/work/active/G6_MIDDLE_LAP976_SHIFT_CLICK_COUNT_BOUND_HANDOFF.md`).
- 예상 PASS / FAIL 조건: 카드 §4(G6-1~G6-5). O·P에서 G6-1 결함(개수 1 유지) 재현 + C에서 G6-1~G6-5 충족.
- 변경 파일 / source fingerprint / 커밋: uncommitted — `patches/selection/g6_shift_click_count_bound.py`(신규), `patches/selection/test_g6_shift_click_count_bound.py`(신규, 14 테스트), `tools/g6_shift_click_probe.py`(신규), `tests/test_g6_shift_click_probe.py`(신규, 3 테스트), `analysis/memory_maps/g6_g7_local_player_slot_bugs_20261004.md`(추가). 제품 기존 파일·G1 uncommitted 변경 불변.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 `b56986e0…a8ac`(불변 재확인), 이식판 normal `0e28ef57…d257`·fixed_start `703deaf4…ea0`(입력 불변), 후보 C normal `b50af2a615354fc90d5438137a374c909850bf8d308761c9b5b4750b426b2f4f`·fixed_start `7c891658a58d3f837a47e7dc8fc74dbd0bb3739030182f04b7f13091f97f64b5`(테스트 pin). 혼자하기 2인(사람 1+컴퓨터 1) 기본 맵, 격리 사본/prefix/Xvfb 1600×1200. fixture = **합성** 엔진 op5 SEED_TYPE(2) owner=로비 자리(0), 화면 좌표에서 역산한 sparse 격자 23~29기 + 아래 dense 띠 46기 후 활성 78~96기(실행마다 시작 위치로 달라짐).
- 실행 명령 / 로그 / 캡처 경로 및 해시: `PYTHONPATH=. .venv/bin/python tools/g6_shift_click_probe.py --variant {orig|port|cand} --seat {0|1} --runtime-root local/runtime/lap977_g6_<v> --artifact-root ../temp/Syw2plus_patch/20261005_lap977_g6_hg6a/<run>`. 산출물 루트 `temp/Syw2plus_patch/20261005_lap977_g6_hg6a/`(각 run `probe-result.json`·`shots/*.png`·`probe.log`). 결과 JSON SHA256 앞 16자: orig@1 `3753d9adc370813d`·port@1 `371ba25ae43b9e1a`·cand@1(r3) `9c9900fb0404f80e`·port@0 `8a492c783d5027a1`·cand@0 `7721fdbc77f0993d`.
- 측정값 / 판정:
  - 정적: 테스트 17 passed(patch 14 + probe 3), RED(`ImportError`)→GREEN. diff 범위 = 지점 8바이트 + cave 23바이트, cave 비참조·rollback byte-identical·SHA/old bytes 거부·덮어쓰기 거부. `make lint`·`make typecheck` PASS.
  - **자리 이동 하네스: 대기실 방향키/번호·유형 클릭으로는 `[0xB63FC4]`가 바뀌지 않음 → 실제 자리 이동 BLOCKED**(로비는 ready 직후 ~1.5초에 자동 시작, 키 12회·클릭 5회 모두 local 0). 사전 §3 규칙대로 BLOCKED로 기록하되 그 뒤 **대체 재현(slot0 emulation)** 을 만들어 실행: local 0 유지, 미사용 풀 slot 0 owner byte를 1로 씀(원본 `0x66B81E`·이식판 `0x112E08E`) → `0x41DD93` 빈 칸 비교가 local=1과 동일하게 불일치. local DWORD 직접 쓰기는 부적합(local=3 → ps27 "게임을 떠나 나갔습니다", local=1 → 컴퓨터 자리라 AI가 fixture 조종).
  - G6-1(A 클릭 → B~F Shift+클릭 5회, owner 불일치 1): **O 원본 [1,1,1,1,1,1]·P 이식판 [1,1,1,1,1,1] = 결함 재현**, **C 후보 [1,2,3,4,5,6]**, 대조 1P(불일치 0): P [1..6]·C [1..6].
  - G6-2 Shift+드래그(2기, 외부 유닛 0): O 1→3·P 1→3·C 1→3(둘 다 합류). G6-3 선택된 유닛 Shift+클릭 제거: O/P/C 모두 3→2(제거 경로는 결함 영향 없음).
  - G6-4 상한: C@1 드래그 50 → 선택 안 된 격리 유닛 Shift+클릭 → 50 유지, 크래시 0. P@1도 50→50이지만 결함으로 막힌 것이라 변별력 없음(C만 의미). C@0·P@0 동일 50→50.
  - G6-5 안전: 5개 run 전부 크래시 0, 모든 스냅샷 개수 ≤ cap(최대 3/50/50/50/50), slot 중복 0, 게임 PS3 유지, 정리 후 prefix 프로세스 0·game 사본 제거.
  - 판정: 카드 §4 기준(O·P 결함 재현 + C G6-1~5 충족) **H-G6a PASS(partial)** — 단 입력은 "실제 자리 이동"이 아니라 slot0 emulation이고, 1회씩 실행(이상치 없음).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 실제 대기실 자리 이동 미재현(emulation은 `0x41DD93` 비교 한 곳만 동일하게 만듦; 실제 k≥1 자리에서 소유 유닛·AI·DPID가 달라 다른 경로가 추가로 막을 가능성은 미배제). 미실행: fixed_start lane 런타임·세이브/로드 후 선택·실제 사람 플레이. G2 풀·G5 50 상한·G5SC sidecar 비회귀는 P@0/C@0의 선택·상한 거동만 확인(저장/불러오기 미실행). 독립 검수·사용자 승인 없음(모델 컨펌 대기). G1 uncommitted 변경·H-F handoff 보존.
- 부작용 기록: 탐색 실행 약 19회가 prefix 약 582MB씩 남김(`local/runtime/lap977_g6_*`, 합 약 11GB) — 디스크 여유 19→7.2GiB. 종료됐으나 lossless archive·restore 검증 전이라 삭제하지 않음(game 사본만 runner가 정리).
- 다음 한 가지: middle(Opus) 독립 검수 — probe-result 5개 재계산(G6-1 스냅샷·slot0 poke readback·ps3 유지), emulation 타당성 판정(실제 자리 이동 재현 경로를 찾을지, 대안으로 수용할지)과 prefix archive 실행, 수용 시 H-G7o 정의.
