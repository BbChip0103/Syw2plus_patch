# 2026-09-28 | lap 734 | 목표 G5 (v6 핵심 회귀 재확인, 10:06 지시 ①)

- 실제 provider/model/effort / 지정 역할: Claude Code Sonnet 5 / high / work tier(구현 실행).
- 가설 / 사용자 관찰: 2026-09-28 10:06 운영자 지시(lap733 v6 수용) — "다음 work는 한 lap에: ①
  v6 핵심 회귀 1회(기존 coverage probe로 드래그 4종·이동·정지/홀드/순찰·공격·그룹 roundtrip·R3·
  Shift+클릭 추가/제거, 원본 1회 대조), ② 08:15 보류분(건설 재판정·특수능력 paired). 끝나면 (E)
  UI." lap733은 v6(H4 사망-후-호출 훅)를 (D) 항목만 검증했고 "byte-diff 스코프 인자에만 의존"해
  드래그/이동/공격/정지·홀드·순찰/그룹저장로드/R3 핵심 회귀를 v6로 실측 재확인하지 않았다고
  명시적으로 남겼다 — 이번 lap의 목적은 그 실측 공백을 메우는 것.
- 예상 PASS / FAIL 조건: H4 훅은 `0x00409CB8` 콜사이트 5바이트 + 새 캐이브만 추가하고 v5의 기존
  선택/이동/공격/그룹/R3 경로 바이트를 전혀 건드리지 않으므로(lap733 disasm 확인), 핵심 회귀는
  v5(lap723~729)와 동일한 PASS 패턴이 나와야 한다. 새로운 FAIL이 나오면 H4 훅이 예상 밖의 부작용을
  낸 것으로 v7 필요.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 제품 EXE/원본 무변경.
  `tools/g5_r3_sparse_selection_probe.py`에 `candidate-v6` variant 추가(2줄, `_variant_module`
  분기 + `--variant` choices, v4→v5 추가 때와 동일한 논-인베이시브 패턴). 그 외 신규 파일 없음
  (`/tmp/lap734_v6_*_driver.py` 3개는 세션 임시 monkeypatch 드라이버, 저장소에 없음 — lap682/717/
  723/724 선례와 동일하게 모듈 전역 `g5`/`TARGET_SHA`만 교체). 전부 uncommitted
  (`LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(두 소스 경로
  `[ESL]Syw2plus`와 `Syw2plus_re/Syw2plus/syw2plus_original.exe` 둘 다 실행 전/후 재확인).
  후보 v6 `fdc913b5f42dc7cc2dcb258d3ecac43e2a2a79a24e4ce10ee362e8ded173805f`(원본에서
  `g5_selection_cap50_v6.build_candidate`로 재빌드, 모든 실행에서 `private_exe_sha256` 일치
  확인). 솔로 로비, worker(slot 1198) 앵커 7×8 dense fixture(55기 SEED_TYPE=2, +worker=56),
  기존 G5 probe들과 동일 protocol.
- 실행 명령 / 로그 / 캡처 경로 및 해시: 4개 probe × (original 1회 + candidate-v6 1회, R3는
  candidate-v6 3 시나리오)를 순차 synchronous 실행(백그라운드로 띄우고 세션 종료하지 않음, PID
  `kill -0` 폴링으로 완주까지 대기):
  1. `tools/g5_command_coverage_probe.py`(monkeypatch `/tmp/lap734_v6_coverage_driver.py`) —
     `local/runtime/lap734_v6_cov_{original,candidate}/`,
     `../../temp/Syw2plus_patch/20260928_lap734_v6_coverage/{original,candidate}/probe-result.json`.
  2. `tools/g5_worker_relative_move_attack_probe.py`(monkeypatch `/tmp/lap734_v6_attack_driver.py`,
     `--source Syw2plus_re/Syw2plus`) — `local/runtime/lap734_v6_attack_{original,candidate}/`,
     `../../temp/Syw2plus_patch/20260928_lap734_v6_attack/{original,candidate}/probe-result.json`.
  3. `tools/g5_candidate_drag_probe.py --ui-roundtrip`(monkeypatch
     `/tmp/lap734_v6_roundtrip_driver.py`, `--source Syw2plus_re/Syw2plus`) —
     `local/runtime/lap734_v6_roundtrip_{original,candidate}/`,
     `../../temp/Syw2plus_patch/20260928_lap734_v6_roundtrip/{original,candidate}/probe-result.json`.
  4. `tools/g5_r3_sparse_selection_probe.py --variant candidate-v6 --scenario
     {front,middle,rear}-death` — `local/runtime/lap734_v6_r3_{front,middle,rear}/`,
     `../../temp/Syw2plus_patch/20260928_lap734_v6_r3/{front,middle,rear}/probe-result.json`.
  이후 `make check`(`/tmp/lap734_make_check.log`), `checks/safety.sh check`. 각 `game`
  사본(~800MB~1.2GB)은 실행 직후 삭제(디스크 위생), output/manifest/log는 보존.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **coverage(①-a): PASS.** 원본 20/20 vs 후보 50/50 — 지면 이동(버튼+우클릭), 정지(버튼+`S`),
    홀드(버튼+`H`), 순찰(버튼+`P`) 전부 `command_changed_to`/`pending_changed_to` 50/50 일치(원본
    20/20 baseline과 같은 패턴). 드래그 4종(plain/ALT/Ctrl/Shift) `_fulldrag`/`_fulldrag_again`
    전부 count=50·unique=50. 더블클릭 같은종류선택 `doubleclick_unit` count=50. Shift 토글:
    `shift_toggle_before_remove`=2 → `shift_toggle_after_remove`=1(정확히 1개 제거)·
    `shift_second_smalldrag` `kept_from_first`=8(추가 유지 확인). `fifty_first_rejection`:
    `fixture_total`=55, `pool_total_with_worker`=56, `selected_count`=50=`capacity`,
    `matches_capacity=true`(51번째 정확히 거부). `source_unchanged` true(양쪽),
    `cleanup.prefix_processes_after=[]`(양쪽).
  - **attack(①-b): PASS(회귀 신호 없음, 단일측정).** 원본: `attack_capable_count`=19,
    `move_convergence.ever_matched_count`=20/20, `attack_window.max_pending_exact_count`=17/19
    (89%), `ever_command4_count`=6/19(원시 `command==4` 지표, lap689가 자동교전 오염으로 신뢰도
    낮다고 정정한 지표). 후보 v6: `attack_capable_count`=49, move `ever_matched_count`=50/50,
    `max_pending_exact_count`=22/49(45%), `ever_command4_count`=27/49(55%). pending-word 기준
    비율(원본 89% vs 후보 45%)과 `ever_command4` 기준(원본 32% vs 후보 55%)이 서로 다른 방향으로
    갈리는 것은 lap688 N=5(원본 4~100%, 후보 54~100%)에서 이미 확인된 큰 표본 변동폭 안이며, 이번
    N=1 측정만으로 v6 고유 회귀라고 결론 낼 근거는 없다(과거에도 항상 N=1은 변동이 컸음). `observed
    _target_uids`가 후보에서 2개(394410, 984177) 나온 것은 lap683이 지적한 자동교전 오염과 같은
    종류(측정 노이즈, v6 원인 아님). move 자체는 20/20→50/50으로 명확히 PASS.
  - **group roundtrip(①-c): PASS.** 원본 `movement_command_nonzero`=20. 후보 v6: `status=
    PASS_UI_ROUNDTRIP`, `movement_command_nonzero`=50, `checks` 7/7 전부 true(`selected_50`,
    `group_stored_stock20_plus_overflow49`, `deselected`, `recalled_50`, `save_created`,
    `group_retained_after_load`, `recalled_50_after_load`) — lap724의 v5 결과와 동일 패턴.
  - **R3(①-d): PASS(3 시나리오 전부).** `candidate-v6`, front/middle/rear-death 각 1회:
    셋 다 `status=PASS_NO_SPARSE_GAP`, `structural_ok=true`, `stop_missed_slots=[]`,
    `move_missed_slots=[]`. front(kill 0~29, survivor 30~49), middle(kill 10~39, survivor
    0~9+40~49, count 정확히 20 경계), rear(kill 20~49, survivor 0~19, entries[0:20] 전용 대조군)
    — lap721이 정의한 세 경계 조건 전부 생존자 누락 없음. v6가 v5의 R3 수정(sparse-scan 게이트)을
    깨지 않았음을 확인.
  - **make check / lint / safety:** `1111 passed`(772.33s), `ruff check` All checks passed,
    `compileall` PASS, `mypy`(지정 10개 파일) Success, `checks/context_limits.py` → `CONTEXT_PASS`,
    `checks/safety.sh check` → `SAFETY_PASS`. 크래시 0(8개 probe 실행 전부), `source_unchanged`
    true 전부(두 원본 경로 SHA 실행 전/후 재확인), `cleanup.prefix_processes_after=[]` 전부.
    디스크: 회차 시작 152G 여유 → 종료 146G(게임 사본 정리 후), 사전 존재하던 타 세션 Xvfb 고아
    프로세스(1024x768 해상도, 내 실행은 전부 1600x1200)는 "자기 실행분만 정리" 규칙에 따라
    손대지 않음.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: v6 핵심 회귀는 전부 PASS로 lap733의 "byte-diff
  스코프 인자에만 의존" 공백을 실측으로 메웠다. **10:06 지시 ②(건설 재판정 + 특수능력 paired)는
  이번 lap에서 착수하지 못했다** — 08:15 지시가 이미 지적했듯 이 항목은 마일스톤 경계에 닿는
  까다로운 재판정(설명서 확인, 다른 국가 재부팅, 커맨드 그리드 하위 페이지, 단축키 전수)이라
  얕은 조사로 성급히 결론 내리면 lap731처럼 다시 뒤집힐 위험이 있어 시간 예산 안에 안전하게 끝내지
  못했다. middle 독립 검수는 여전히 체크리스트 전체(A~H) 완료 후 한 번에 진행(2026-09-28 03:36
  운영자 판정 유지). 사용자 milestone 승인 없음.
- 다음 한 가지: work tier가 10:06 지시 ②를 착수 — 설명서(`[필독] 임진록 설명서`)에서 건설 관련
  문구 확인, 최소 2개 다른 국가로 재부팅해 커맨드 그리드 전 페이지·단축키(숫자/문자 전수)를
  스캔해 "건설" 기능이 실제로 존재하는지 재판정하고, 존재하는 모든 특수능력/변신 버튼마다 원본
  20/v6 50 paired 수신 수를 측정. 끝나면 (E) UI(50기 초상화/정보패널/HUD/체력바 표시)로 진행.
