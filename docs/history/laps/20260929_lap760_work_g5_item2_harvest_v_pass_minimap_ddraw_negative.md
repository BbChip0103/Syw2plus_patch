# 2026-09-29 | lap 760 | 목표 G5 (사용자 항목(2))

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5`/high, work(실무).
- 가설 / 사용자 관찰: 2026-09-29 11:25 운영자 지시 ①②. ① 일꾼 선택→V(수확)→자원 좌클릭이
  원본20/v10 50 모두에서 채집 pending(`0x1000008`)을 낸다(원본 먼저 성공 조건 확보). ② 원본 폴더의
  `ddraw.dll`(네이티브)을 격리 사본에 로드하면(`WINEDLLOVERRIDES=ddraw=n,b`) 격리 환경에서 검게
  그려지는 미니맵이 실제로 렌더된다.
- 예상 PASS / FAIL 조건: ① 선택 전원이 V+클릭으로 채집 pending을 수신하면 PASS(원본20/후보50 각각).
  ② 미니맵 다이아몬드 영역이 native override에서 builtin 대비 시각적으로 달라지면(렌더 신호) PASS,
  동일하면 UNKNOWN 유지.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): uncommitted(`LOOP_ALLOW_COMMITS=0`).
  - `tools/g5_worker_harvest_v_command_probe.py`(신규, 이 lap이 `BRIDGE_SOURCE`를 기존
    `patches/population/g5_c_repair_bridge.c`(lap730에서 이미 검증된, 고정 allow-list 없이 구조적
    게이트만 쓰는 private fork)로 바꿔 랜덤 국가 일꾼 unit_type 문제를 해소).
  - `tools/g5_minimap_ddraw_native_override_probe.py`(신규, 이전 세션 구간에서 이미 실행 완료).
  - `tools/g5_worker_gather_command_probe.py`, `tools/g5_ability_target_search_probe.py`(신규,
    이전 세션 구간 산출물, 이 lap에서 변경 없음).
  - `patches/population/build_runtime_bridge.py`(`--bridge-source` 오버라이드 옵션 추가, 기존
    G2-pinned 공유 `runtime_bridge.c` 경로는 무변경 시 그대로 기본값).
  - `patches/population/runtime_driver.py`(`write()` 헬퍼 추가, lap753에서 이미 도입된 진단 전용
    기능 — 이 lap은 사용하지 않음, 무변경 유지).
  - `tools/g5_candidate_drag_probe.py`(원본 EXE 파일명을 SHA-first로 해석하도록 수정, lap 이전 구간).
  - 제품 코드(`patches/population/runtime_bridge.c`, `patches/selection/g5_selection_cap50_v10.py`)
    무변경.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`([ESL]Syw2plus, 보호 원본),
  후보 v10 `c3ceaa25dea98232234759a332b867d92a669f63a03c3f453d3199cc329ebfad`(patches/selection/
  g5_selection_cap50_v10.py). 격리 Wine/Xvfb 1600×1200, PS3 solo, owner0. 일꾼 unit_type은 로비
  국가 랜덤(이 lap 관측: 21/31, lap730 기존 관측 7과 합쳐 {7,21,23,31}이 W24 Step A 정적 인벤토리
  기준 동일 스펙(cost10/width1/height1/flags0=gate-legal)). 채집 fixture는 일�원 중심 격자에
  `g5_c_repair_bridge.c`의 op=5(구조적 게이트만, 고정 allow-list 없음)로 스폰.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - ① `python3 -m tools.g5_worker_harvest_v_command_probe --variant original --runtime-root
    local/runtime/lap760-harvest-v-original --artifact-root
    .../20260929_lap760_harvest_v/original-r8` → `probe-result.json`
    (`private_exe_sha256=b56986e0…`, `source_unchanged=true`).
  - 같은 명령 `--variant candidate --runtime-root local/runtime/lap760-harvest-v-candidate
    --artifact-root .../20260929_lap760_harvest_v/candidate-r1` →
    (`private_exe_sha256=c3ceaa25…`, `source_unchanged=true`).
  - (참고, 이전 세션 구간) ② `tools/g5_minimap_ddraw_native_override_probe.py` 3변형
    (`builtin_control` ddraw=b, `native_test` ddraw=n,b, native+explicit LoadLibrary) →
    `local/runtime/lap760-minimap-ddraw-{builtin,native,native-loaddll}-out/probe-result.json`.
  - 이 lap 전에 원인 진단으로 실패한 시도 5회(원본 fixture `unsupported_army_fixture_type`,
    worker_type 21/31/21/21/31 — 로비 국가 랜덤 재확인, 새 가설 아님, 근본 원인은 브리지
    소스 교체로 해소)는 `original-r1..r7`(일부 삭제됨, r8이 최종 성공)에 로그가 남아 있다.
  - `make check` 동치 게이트를 개별 실행: `pytest -ra` 1131 passed·5 skipped(662.41s,
    `logs/gates/lap760_pytest_20260929*.log`), `ruff check`·`mypy --follow-imports=skip`·
    `compileall`·`checks/context_limits.py`(`CONTEXT_PASS`)·`checks/safety.sh check`
    (`SAFETY_PASS`) 전부 개별 PASS(제품 코드 무변경이므로 lap758/759와 동일하게 전체 `make check`
    자동화 러너 대신 구성 체크를 그대로 실행).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - ① **PASS**: 원본 `selected_count=20, harvested_count=20, all_selected_harvested=true`;
    후보(v10) `selected_count=50, harvested_count=50, all_selected_harvested=true`. 두 변형 모두
    `all_pending_values_seen=["0x1","0x1000001","0x1000008"]`(이동 없이 곧장 채집 pending으로
    전이, 중간 이동 pending 없음). 명시적 V-버튼 경로가 우클릭 암묵 채집(lap729, 이미 PASS)과
    동일하게 선택 전원에 도달함을 실측 확인.
  - ② **UNKNOWN 유지(부정 결과, 실행 증거 확보)**: `builtin_control`/`native_test`/
    `native+LoadLibrary` 3변형 모두 `minimap_render_signal=false`, `minimap_click_signal=false`.
    다이아몬드 영역 전/후 픽셀 diff는 있으나(내부 60×30 상자 unique_colors 1→71, 클릭 시 UI 패널
    갱신으로 추정) 3변형 사이에 차이가 없어 native ddraw.dll override가 미니맵 렌더 활성화의
    원인이 아님을 실측 반증. 미니맵 클릭 입력 핸들러(좌표→월드 변환) 자체는 이 lap에서 미착수.
  - 크래시 0(전 실행), `source_unchanged` 전부 true, `cleanup.prefix_processes_after=[]` 전부.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 제품 코드(런타임 브리지·선택 패치) 무변경이므로
  회귀 위험 없음. `BRIDGE_SOURCE`를 `g5_c_repair_bridge.c`로 바꾼 것은 진단 전용 private fork 재사용
  (이미 lap730에서 검증됨)이며 G2-pinned 공유 `runtime_bridge.c`/`G2_APPROVED_BRIDGE_SHA256`은
  손대지 않음. middle 독립 검수 없음(정보 제공용). 남은 것: 미니맵 클릭 입력 핸들러 브레이크포인트
  조사(②), "V" 정확 대상 특정(lap758 잔여, ①과 무관), "I" 다른 국가 확인(lap758 잔여).
- 다음 한 가지: work가 미니맵 클릭 입력 핸들러(미니맵 영역 좌표→월드 변환→이동 명령)를
  브레이크포인트로 확인하거나(② 계속), lap758 잔여 항목(V 정확 대상, I 국가)으로 진행. 그 다음
  middle이 사용자 항목(1)(lap756/757)+(2)(이 lap) 전체를 독립 재검수 → 사용자 3단 milestone 재상정.
  G1 재개 금지, 멀티/초기메뉴 경로는 알려진 제한 유지.
