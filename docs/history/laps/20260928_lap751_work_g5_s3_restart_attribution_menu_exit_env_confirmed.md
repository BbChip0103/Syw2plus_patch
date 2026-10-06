# 2026-09-28 | lap 751 | 목표 G5 ((F) S3 귀속·실측, lap750 middle 핸드오프)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5`, high / work tier(구현 실행).
  lap750 middle 핸드오프(`docs/history/laps/20260928_lap750_middle_g5_v8_final_review_hold_s3_s5_gap.md`)의
  "다음 한 가지" ①②③ 그대로 수행.
- 가설 / 사용자 관찰: lap750이 남긴 유일한 F 블로커는 S3(초기메뉴→새 게임 선택 이월)가 미측정이라는
  점. 핸드오프는 두 실험을 지정했다: ① v7(로드 래퍼가 20칸만 0 채움)로 "50 드래그→다시하기→50칸
  dump"만 실행해 재시작이 세이브 로드 경로(LOAD_WRAPPER, tail 잔존 예상)인지 유닛 해체 경로(dec, tail
  전부 0 예상)인지 귀속; ② 원본/후보로 순정 로비 시작 직후(fixture 이전) "초기메뉴"가 메인 메뉴로
  가는지 확인해, 과거 실패(lap747)가 fixture/선택 상태 때문인지 환경 자체의 제약인지 분리.
- 예상 PASS / FAIL 조건: ①에서 tail이 남으면(로드 경로) 또한 ②가 불가/FAIL이면 → v9 필요(새 게임
  초기화 지점에 새 배열 0 채움 추가). ①에서 tail이 전부 0이면(해체 경로) → S3도 같은 해체를 탈
  가능성이 높다는 핸드오프 자신의 사전 판정 기준 충족 → v9 불필요, 남은 것은 S3 자체가 여전히
  BLOCKED(env)라는 것만 재확인.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 전부 uncommitted(`LOOP_ALLOW_COMMITS=0`):
  - `tools/g5_stale_tail_probe.py` — 기존 파일에 두 개의 독립 게이트 분기만 추가(기존 S1~S5 흐름은
    변경 없음, 새 플래그가 꺼진 기본 동작은 100% 동일):
    - `--restart-dump-only`: 드래그 직후 S1 저장/로드를 건너뛰고 곧바로 재시작(`다시하기`) 후
      `full_dump`를 재시작 전/후로 비교(핸드오프 실험 ①).
    - `--menu-exit-fresh`: fixture/드래그를 만들기 전, 순정 솔로 로비 시작 직후 "초기메뉴" 시퀀스만
      시도하고 즉시 종료(핸드오프 실험 ②).
  - 제품 EXE/원본 바이트 변경 0. v9 빌드 없음(불필요 판정, 아래).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본
  `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` = `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
  (3회 실행 전후 전부 `source_unchanged=true`). v7 = `30efafa067b6cb524bd68594dedee4d0d4c68e1efef348e2f16c211dc8229bef`,
  v8 = `ef46d1acd55af2f6007824bb416b3c991ae4afb195fb369b3e86b5ee9182ff08`(둘 다 기존 기록과 재빌드 일치).
  솔로 로비, 1600×1200 Xvfb, 격리 prefix 3개(실험당 1개). ①은 worker(slot 1198) 앵커 dense fixture 55기
  + 50 드래그 선택. ②는 fixture/선택 없음(순정 로비 시작 직후).
- 실행 명령 / 로그 / 캡처 경로 및 해시: 3회 synchronous 격리 실행(`kill -0` 폴링, 세션 유지, 각 `game`
  사본은 직후 삭제·output/manifest/prefix/로그만 보존):
  1. `python3 tools/g5_stale_tail_probe.py --variant candidate --candidate-version v7 --runtime-root
     local/runtime/lap751_restart_dump_v7 --artifact-root
     .../20260928_lap751_restart_dump/v7 --restart-dump-only` → `RESTART_DUMP_TAIL_CLEARED`.
  2. `--variant original --runtime-root local/runtime/lap751_menu_fresh_original --artifact-root
     .../20260928_lap751_menu_fresh/original --menu-exit-fresh` → `MENU_EXIT_FRESH_BLOCKED_SAME_AS_FIXTURED`.
  3. `--variant candidate --candidate-version v8 --runtime-root local/runtime/lap751_menu_fresh_v8
     --artifact-root .../20260928_lap751_menu_fresh/v8 --menu-exit-fresh` →
     `MENU_EXIT_FRESH_BLOCKED_SAME_AS_FIXTURED`.
  전체 artifact·캡처·probe-result.json은
  `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260928_lap751_restart_dump/`,
  `.../20260928_lap751_menu_fresh/`에 보존. `make check` 로그 `/tmp/lap751_make_check.log`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **① `RESTART_DUMP_TAIL_CLEARED`(v7):** 재시작 전 `dump_before_restart` count=50·nonzero=50(정상
    드래그 결과). 재시작(`ps` 134→23→140→3, `tick` 134→2로 리셋) 후 `dump_after_restart`
    count=0·nonzero_count=0·`raw_entries` 50칸 전부 0(`tail_nonzero_indices_after_restart=[]`). v7의
    `LOAD_WRAPPER`는 20칸만 0 채우므로, 재시작이 그 경로를 탔다면 21~50칸이 남아야 했다 — **남지
    않았으므로 재시작은 세이브 로드 경로가 아니라 유닛 해체(dec, `0x412ed2`) 경로 50회 또는 그와
    동급의 전체 초기화로 비워진다**(핸드오프가 사전 등록한 두 해석 중 "해체 경로" 쪽 확정).
  - **② `MENU_EXIT_FRESH_BLOCKED_SAME_AS_FIXTURED`(원본·v8 동일):** fixture/선택이 전혀 없는 순정
    상태에서도 "초기메뉴" 확인 클릭 후 `ps`가 23→3으로 즉시 복귀(원본 `tick` 6→8, v8 `tick` 4→6,
    `ps_trace_after_confirm=[3]`, 메인 메뉴(`ps==9`) 도달 없음). lap747의 "원본도 동일 재현"이
    fixture/선택 상태와 무관하게 **환경/원본 고유의 메뉴 전환 제약**임을 fixture 없는 최소 조건에서도
    재확인했다 — 이 하네스에서는 어떤 상태에서도 "초기메뉴"로 메인 메뉴에 도달한 적이 없다.
  - **종합:** 핸드오프 branching(③)의 v9 트리거 조건 "①이 로드 경로이고 ②가 불가/FAIL"은 성립하지
    않는다 — ①은 로드 경로가 **아니다**(정반대: 좁은 LOAD_WRAPPER에 의존하지 않는 더 넓은 해체
    경로), ②는 여전히 불가하지만 이제 fixture와 무관함이 확인됐다. 핸드오프 자신이 사전에 명시한
    해석("재시작이 해체 경로로 비워지면 S3도 같은 해체를 탈 가능성이 높다")에 따라 **v9는 불필요하다는
    쪽으로 판정**하지만, 이것은 "S3가 같은 함수를 탄다"는 직접 증거가 아니라 유추(analogy)다 — 재시작과
    "새 게임 시작"이 동일한 매치-초기화 루틴을 호출하는지는 정적으로 확인하지 않았다. S3 자체는 여전히
    이 하네스에서 실측 불가능(`BLOCKED(env)`)하며, 이는 G(멀티)와 같은 급의 환경 제약으로 문서화한다.
  - `pytest patches/selection/test_g5_selection_cap50_v{7,8}.py` = 9 passed. `make check` = **1115
    passed, 5 skipped(783.17s)**, ruff/mypy/`CONTEXT_PASS` 전부 PASS. `checks/safety.sh check` =
    `SAFETY_PASS`. 3회 실행 전부 `source_unchanged=true`, `cleanup.ok=true`(고아 프로세스 0).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 제품 코드 0 변경(도구 파일 1개, 기존 분기 100% 보존
  — 새 플래그를 켜지 않으면 이전 lap들의 S1~S5 동작과 동일). 남은 위험: S3는 "재시작=해체 경로"라는
  유추로 위험이 낮아졌다고 판단하나, 새 게임 시작이 재시작과 동일한 초기화 함수를 타는지는 정적으로
  미확인 — 완전한 100% 확신은 아니다. lap748 S5(공허)는 그대로 남아 있다(정적 귀속 수용 유지, lap750
  판정 그대로). middle 재검수 대기.
- 다음 한 가지: **middle이 F를 최종 재검수**한다 — ①②의 새 증거(재시작=해체 경로 확정, 메뉴 전환
  제약=fixture 무관 환경 제약 확정)를 반영해 S3를 "미확정 실제 위험"에서 "BLOCKED(env) + 낮은 유추
  위험(재시작 해체 경로 analogy)"으로 재분류할지, 아니면 추가로 재시작 핸들러와 새 게임 초기화
  루틴이 같은 함수를 호출하는지 정적 대조(gdb 워치포인트 또는 xref)까지 요구할지 middle이 판단한다.
  PASS 처리 시 알려진 제한(멀티 BLOCKED, 부대 미지정 선택 로드 후 20기, 미니맵/능력 v UNKNOWN, 건설·
  승선 N/A, S3 BLOCKED(env)+analogy, S5 정적 귀속)을 명시해 사용자 milestone 재상정 여부를 정한다.
