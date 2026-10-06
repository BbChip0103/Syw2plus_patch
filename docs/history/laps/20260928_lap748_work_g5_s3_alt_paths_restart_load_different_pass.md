# 2026-09-28 | lap 748 | 목표 G5 (18:35 지시 ① S3 대체 경로: 다시하기/불러오기)

- 실제 provider/model/effort / 지정 역할: Claude Code Sonnet 5 / high / work tier(구현 실행). lap747의
  17:45/18:05/18:35 운영자 지시 중 아직 미착수였던 ①(S3 대체 경로)을 그대로 수행. ②(홀드버튼
  원본/후보 각 3회)는 lap747이 이미 완료했으므로 이번 lap은 손대지 않았다.
- 가설 / 사용자 관찰: lap747이 확정한 사실 — "초기메뉴" 확인 대화상자를 정확히 클릭해도 메인
  메뉴로 가지 않고 즉시 같은 게임으로 복귀하는 현상이 원본(무패치)에서도 동일하게 재현되므로
  v8/G5 패치 결함이 아니라 probe 환경 또는 원본 고유 제약이다. 18:35 지시는 이 결론을 "환경 제약
  종결"로 받아들이지 않고, 사용자가 실제로 우려하는 것("50기 선택 상태가 새 판/다른 판에 이월되지
  않는지")을 다른 두 경로로 다시 확인하라고 요구했다: 일시정지 메뉴의 "다시하기"(재시작)와
  "불러오기"(다른 세이브 로드). 두 경로 모두 lap746이 발견하고 v8로 고친 H-STALE-TAIL 버그
  (`LOAD_WRAPPER`가 entries[20:50]을 비우지 않는 결함)와 같은 코드 경로(로드/초기화)를 밟을 가능성이
  있으므로, v7이었다면 FAIL했을 것이고 v8이 PASS해야 lap746 수정이 이 두 경로에도 일반화됨을
  보인다.
- 예상 PASS / FAIL 조건: S4(재시작) — 재시작이 실제로 일어났음을 tick이 재시작 클릭 직전 값보다
  낮아짐으로 확인한 뒤, 선택 배열 전체(50칸, `range(count)`가 아니라 전 버퍼)가 count=0·비0칸=0이면
  PASS, 아니면 FAIL(선택 이월). S5(불러오기 다른 판) — fixture 생성 전에 만든 baseline 세이브(이
  probe 자신의 S1 세이브가 아니라 완전히 다른 게임 상태)를 로드한 뒤 같은 기준으로 PASS/FAIL, 추가로
  entries[20:50] 잔존 칸(stale tail)이 실제로 명령을 받는지 우클릭 이동 diff로 확인.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 전부 uncommitted(`LOOP_ALLOW_COMMITS=0`):
  - `tools/g5_stale_tail_probe.py`: (1) `PAUSE_RESTART_POINT = (400, 307)` 상수 추가(일시정지 메뉴
    6번째 행 "다시하기", 기존 확정된 35px 행 간격으로 계산: `132 + (6-1)*35`). (2) ps3 도달 직후,
    dense fixture 생성 **전**에 `attempt_load_different` 플래그 아래 baseline 세이브를 만들고
    `shutil.copy2`로 host-side `baseline_backup.dat`에 보존하는 블록 추가(S1이 나중에 같은 슬롯을
    덮어써도 살아남도록). (3) 기존 S1/S2 redrag+resave 직후, S3(초기메뉴) 시도 **전**에 S4(재시작)와
    S5(불러오기 다른 판) 블록을 새로 추가 — 둘 다 `--attempt-restart`/`--attempt-load-different`로
    개별 게이트, `not crashed`일 때만 실행, 실패해도 `S4_INCONCLUSIVE_*`/`S5_INCONCLUSIVE_*`로
    기록하고 계속 진행(S3와 같은 best-effort 패턴). S5는 두 번째 세이브 슬롯 UI 없이, host 파일시스템
    복사(`baseline_backup.dat` → `save001.dat`)로 "다른 판"을 준비한 뒤 기존 `PAUSE_LOAD_POINT`/
    `SAVE_SLOT_POINT`/`SAVE_ACTION_POINT` 클릭 시퀀스를 그대로 재사용. `run()`/`main()` 시그니처에
    `attempt_restart`/`attempt_load_different` 매개변수와 `--attempt-restart`/`--attempt-load-different`
    CLI 플래그 추가. 신규 파일 0개, 제품 EXE/원본 0 변경.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(`[ESL]Syw2plus/[HQ]Syw2plus
  2002.exe`, 3회 실행 전후 재해시 불변). 후보 v8
  `ef46d1acd55af2f6007824bb416b3c991ae4afb195fb369b3e86b5ee9182ff08`(lap746/747 기록과 일치). 솔로
  로비, worker(slot 1198) 앵커 7×8 dense fixture(55기 SEED_TYPE=2), 기존 G5 stale-tail probe와 동일
  protocol.
- 실행 명령 / 로그 / 캡처 경로 및 해시: 3회 synchronous 격리 실행(각 `kill -0` 폴링, 세션 유지, `game`
  사본은 실행 직후 삭제 — output/manifest/prefix/로그만 보존):
  1. `PYTHONPATH=. .venv/bin/python tools/g5_stale_tail_probe.py --variant original --runtime-root
     local/runtime/20260928_lap748_g5_s4s5_original --artifact-root
     .../temp/Syw2plus_patch/20260928_lap748_g5_s4s5_original --attempt-restart
     --attempt-load-different` → 성공. 로그 `/tmp/lap748_s4s5_original.log`.
  2. 같은 명령을 `--variant candidate --candidate-version v8`로 1차 실행
     (`local/runtime/20260928_lap748_g5_s4s5_v8`) → `pause_for_baseline_save` 타임아웃으로 `FAIL`
     (baseline 세이브 직전 Escape 키가 등록되지 않음, tick은 계속 진행 중이었음 — 원본에서는 동일
     코드 경로가 1회차에 성공했으므로 candidate 결함이 아니라 환경 플레이크로 판단, 재시도).
     로그 `/tmp/lap748_s4s5_v8.log`.
  3. 동일 명령 재시도(`local/runtime/20260928_lap748_g5_s4s5_v8_retry`) → 성공. 로그
     `/tmp/lap748_s4s5_v8_retry.log`.
  이후 `make check`(`/tmp/lap748_make_check.log`), `bash checks/safety.sh check`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **원본 (run 1):** 전체 `status=PASS_NO_STALE_TAIL_EFFECT`(기존 S1/S2 불변식 그대로 유지).
    `s4_restart`: `pre_restart_tick=235` → 확인 클릭 후 `ps_trace_after_confirm=[150,2,2,3]` →
    `state_after_confirm={ps:3, tick:5}`(tick이 235→5로 실제 감소, `restarted=true`),
    `selection_after_restart`는 20칸 전부 0(`count=0, nonzero_count=0, count_matches_nonzero=true`),
    `fixture_slots_after_restart=[]`(재시작으로 이전 fixture 사라짐) → **`S4_PASS_SELECTION_CLEARED`**.
    `s5_load_different`: `baseline_save_pre_fixture.selection.count=0`(fixture 이전이므로 당연),
    로드 후 `selection_after_load`도 20칸 전부 0, `fixture_units_vanished=[]`(baseline 시점엔 애초에
    fixture가 없었음), `stale_tail_slots_after_load=[]`, `stale_tail_commanded_after_move=[]` →
    **`S5_PASS_NO_CARRYOVER`**.
  - **후보 v8 (run 3, run 2는 환경 플레이크로 재시도):** 전체 `status=PASS_NO_STALE_TAIL_EFFECT`.
    `s4_restart`: `pre_restart_tick=224` → `state_after_confirm={ps:3, tick:2}`(224→2, `restarted=
    true`), `selection_after_restart`는 **50칸**(`base=0x108c000, capacity=50`) 전부 0
    (`count=0, nonzero_count=0, count_matches_nonzero=true`) → **`S4_PASS_SELECTION_CLEARED`**.
    `s5_load_different`: `selection_after_load`도 50칸 전부 0, `stale_tail_slots_after_load=[]`,
    `stale_tail_commanded_after_move=[]`, `fixture_units_vanished=[]` → **`S5_PASS_NO_CARRYOVER`**.
    두 결과 모두 원본과 패턴 일치(20칸 vs 50칸이라는 용량 차이만 있고, 둘 다 완전히 클린).
  - 3회 실행 모두 `source_unchanged=true`, `cleanup.ok=true`, 크래시 0(`process_alive` 유지 또는
    정상 종료). `make check` **1115 passed, 5 skipped(785.44s)**, ruff/compileall/mypy 전부 PASS,
    `checks/context_limits.py` `CONTEXT_PASS`, `checks/safety.sh check` `SAFETY_PASS`. 디스크: 게임
    사본(각 1.4GB) 3개 실행 직후 삭제(prefix/output/manifest/로그 보존), 종료 시 116G 여유.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 이번 lap은 S3(초기메뉴)의 환경 제약을 우회해,
  사용자가 실제로 우려하는 "50선택이 새 판에 이월되는가"라는 질문을 두 개의 독립 경로(재시작,
  다른 세이브 로드)로 직접 답했다 — 둘 다 원본·v8 모두 클린, v8의 H-STALE-TAIL 수정이 일반화됨을
  실측으로 확인. **fixture-free 순정 로비에서 "초기메뉴"를 재시도하는 항목은 이번 lap에서 착수하지
  않았다** — S4/S5가 이미 "선택 이월" 우려를 실질적으로 해소했고, 18:35 지시가 이를 "가능하면"으로
  낮은 우선순위로 표현했으므로, 남은 시간 예산을 (F) 판정의 마지막 실질 블로커인 홀드버튼 편차
  조사로 돌리는 것이 더 가치가 크다고 판단했다(다음 한 가지 참고). middle 독립 검수는 아직
  받지 않았다(work tier 정보제공). 사용자 milestone 여전히 없음.
- 다음 한 가지: 홀드버튼 편차(원본 3회 20/20 고정 대 v8 3회 0/50→50/50→3/50 요동, 단축키는 v8도
  50/50 안정)의 근본 원인을 좁힌다. 우선 `tools/g5_command_coverage_probe.py`의 `hold_button` 관측
  윈도우(현재 `window=3.0`)를 stop/hold/patrol 대비 넓혀 v8로 2~3회 재측정 — 매번 50/50에 도달하면
  "표본/타이밍 아티팩트"로 결론(회귀 아님), 여전히 요동하면 gdb로 청크 분할 발행 코드 경로를 직접
  추적해 즉시 수정한다. 해소되면(또는 회귀 아님으로 확정되면) middle이 G5 (F)를 v8 기준(S1/S2/S4/S5
  전부 PASS, S3는 원본도 동일한 환경 제약으로 명시)으로 최종 재검수한다.
