# 2026-09-28 | lap 753 | 목표 G5 (work: v9 빌드 + 게임 시작 경로 stale 주입 paired probe)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5`, high / work(실무 구현·probe·회귀).
  게임 코드 패치 1개 신설(v9), probe 도구 2개 수정.
- 가설 / 사용자 관찰: lap752 middle 핸드오프(`docs/history/laps/
  20260928_lap752_middle_g5_f_s3_newgame_init_gap_v9_handoff.md`) — 원본 새 게임 초기화 `0x4A3060`이
  레거시 선택 count/엔트리를 **직접** 0으로 만드는데, v8 새 배열(`0x0108C000`)은 이 보장에서 빠진다
  (H-NEWGAME-INIT, 정적 확정, 런타임 미검증). v9는 `0x4A3168`(`mov [esi+0x6c14],ebx`) 1지점을 hook해
  같은 자리에서 새 배열도 0으로 채운다.
- 예상 PASS / FAIL 조건: 유닛 자체의 "선택됨" 플래그(byte0)를 전혀 건드리지 않고 선택 배열에 직접
  가짜 stale 값(원본=레거시 20칸, 후보=새 배열 50칸)을 주입하면, 해체(dec, `0x412d90`) 경로가 그 슬롯들에
  대해 호출될 수 없다(어떤 유닛도 "선택됨"으로 플래그되지 않았으므로) — 이 상태에서 재시작 시 배열이
  비면 새 게임/재시작 초기화 자체가 원인, 남으면 v8처럼 초기화가 새 배열을 놓친다는 뜻. 기대: 원본
  CLEARED, v8 PERSISTED(갭 실증), v9 CLEARED(수정 확인).
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 신규
  `patches/selection/g5_selection_cap50_v9.py`,
  `patches/selection/test_g5_selection_cap50_v9.py`(pytest 7개). 수정
  `patches/population/runtime_driver.py`(`write()` 함수 추가, `process_vm_writev` — 기존 `read()`와
  같은 전용 격리 Wine 자식 프로세스 진단 전용 범위), `tools/g5_stale_tail_probe.py`(`--newgame-stale-probe`
  게이트 1개 추가, v9를 `CANDIDATE_MODULES`/`CANDIDATE_SHAS`에 등록 — 기존 S1~S5/restart-dump-only/
  menu-exit-fresh 분기 무변경). 커밋 없음(uncommitted, `LOOP_ALLOW_COMMITS=0` 기본).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본
  `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` = `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
  (4회 실행 전후 재확인, `source_unchanged=true` 4/4). v8 재빌드 =
  `ef46d1acd55af2f6007824bb416b3c991ae4afb195fb369b3e86b5ee9182ff08`(기록 일치). **v9 재빌드 =
  `18181cdef6c787a2be9a3cf78a2851eb4d764074c972e2b13690f27af0fd2017`**(결정적, 2회 빌드 동일 SHA).
  솔로 로비, 1600×1200 Xvfb, 격리 prefix. stale 주입 probe는 fixture/드래그 없이 순정 매치 시작 직후
  바로 메모리 주입(원본 20칸/후보 50칸, 값 1..capacity, 어떤 유닛도 byte0=1로 플래그하지 않음).
- 실행 명령 / 로그 / 캡처 경로 및 해시: 4회 synchronous 격리 실행(`kill -0` 폴링, 각 `game` 사본은 직후
  삭제·output/manifest/prefix/로그만 보존):
  1. `python3 tools/g5_stale_tail_probe.py --variant original --runtime-root
     local/runtime/lap752_newgame_stale_original --artifact-root
     .../20260928_lap752_newgame_stale/original --newgame-stale-probe` → 1차 시도는 Escape가 씹혀
     `NEWGAME_STALE_INCONCLUSIVE_ERROR`(pause 전환 타임아웃, injected 상태 자체는 정상 — count=20·
     nonzero=20·`injected_slots_have_no_selected_flag=true`); `windowfocus` 재포커스 + 3회 재시도
     로직 추가 후 재실행 → **`NEWGAME_STALE_CLEARED`**(1차 시도에서 성공).
  2. `--variant candidate --candidate-version v8 --runtime-root local/runtime/lap752_newgame_stale_v8
     --artifact-root .../20260928_lap752_newgame_stale/v8 --newgame-stale-probe` →
     **`NEWGAME_STALE_PERSISTED`**.
  3. `--variant candidate --candidate-version v9 --runtime-root local/runtime/lap752_newgame_stale_v9
     --artifact-root .../20260928_lap752_newgame_stale/v9 --newgame-stale-probe` →
     **`NEWGAME_STALE_CLEARED`**.
  4. `--variant candidate --candidate-version v9 --runtime-root local/runtime/lap752_v9_s124
     --artifact-root .../20260928_lap752_v9_s124 --attempt-restart` (S1/S2 기본 흐름 + S4) →
     `PASS_NO_STALE_TAIL_EFFECT`, `s4_restart.status=S4_PASS_SELECTION_CLEARED`, 크래시 0,
     `commanded_outside_legit_selection=[]`.
  전체 artifact·probe-result.json은
  `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260928_lap752_newgame_stale/`,
  `.../20260928_lap752_v9_s124/`에 보존. `make check` 로그 `/tmp/lap752work_make_check2.log`
  (1차 `/tmp/lap752work_make_check.log`는 ruff `F841` 미사용 변수 1건으로 FAIL, 수정 후 2차 PASS).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **falsifiable paired probe 결과 — 사전 등록한 세 갈래 그대로 확정:** 원본
    `NEWGAME_STALE_CLEARED`(count=20→0, nonzero=20→0), **v8 `NEWGAME_STALE_PERSISTED`(count=50→50,
    nonzero=50→50, 재시작 후에도 주입한 가짜 stale이 그대로 남음 — H-NEWGAME-INIT이 정적 확정을 넘어
    런타임에서 최초로 실증됨)**, **v9 `NEWGAME_STALE_CLEARED`(count=50→0, nonzero=50→0 — 새 hook이
    실제로 새 배열을 비움)**. 세 경우 모두 `pause_attempts=1`(재시도 로직 추가 후), `restarted=true`,
    `cleanup.ok=true`, `source_unchanged=true`.
  - v9 S1/S2/S4 회귀: `PASS_NO_STALE_TAIL_EFFECT` — v8이 lap746/748에서 확립한 save/load stale-tail
    수정과 재시작 클린업이 v9에서도 그대로 유지됨(v9는 v8 위에 1지점만 추가하므로 기대대로).
  - `make check` **1122 passed, 5 skipped(774.79s)**, ruff/mypy(10 source files, 0 issue)/
    `CONTEXT_PASS` 전부 PASS. `checks/safety.sh check` = `SAFETY_PASS`.
  - v9 pytest 7개(결정적 재빌드, hook old-byte 고정, diff 범위가 hook+cave+section-header로만 한정,
    cave가 원 명령 재현 후 51-dword 0 채움 후 점프 복귀함을 디스어셈블로 확인) 전부 PASS.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 제품 코드는 v9 하나(선택 관련 20파일째, v1~v9
  체인)만 추가, 기존 v1~v8 어떤 바이트도 변경 없음(pytest로 diff 범위 고정: hook 6바이트 중 5바이트 변경
  지점 + 새 cave(`.rsrc` 0x2200~0x2240, 기존 v7/v8 cave 0x2100~0x2200과 겹치지 않음, 원본에서 0x3000까지
  0으로 확인됨) + section header VirtualSize 필드 1바이트). **다음 middle이 (F)/S3를 이 새 runtime
  증거로 재검수할 차례.** 남은 미결: (A) 표에 this-상대 초기화 행(이번 lap 미착수, 다음 항목),
  G 멀티는 `BLOCKED(env)` 그대로, S3 자체(초기메뉴 UI)는 여전히 env로 미실측이지만 "게임 시작/재시작
  초기화가 새 배열을 비우는가"라는 실질 질문은 이번 falsification으로 직접 커버됨.
  **② 호출자 귀속(gdb, lap752 핸드오프 항목)은 의도적으로 미실행** — work 판단(묻지 말고 결정):
  `0x41b9c0`/`0x41bc4f`/`0x4c3e59` 세 호출자 전부 동일한 `0x4a3060`을 호출하고 v9는 그 함수 내부의
  단일 명령(`0x4a3168`)을 hook하므로, 어느 호출자가 실제로 불렸는지는 hook의 정확성과 무관하다(핸드오프
  자신이 "귀속은 증거용"이라고 명시). 대신 이번 lap의 실제 재시작 실행(`restarted=true`, tick 리셋
  4회 관측)이 그 중 최소 하나(다시하기 경로, `0x41bc4f` 추정)가 실제로 이 hook을 통과했다는 실행 증거를
  대체 제공한다고 판단해 별도 gdb 브레이크포인트 세션은 생략했다 — middle이 이 판단에 동의하지 않으면
  다음 lap에서 gdb 귀속을 추가한다.
- 다음 한 가지: middle이 이 lap의 runtime falsification(원본 CLEARED/v8 PERSISTED/v9 CLEARED)과 S1/S2/S4
  v9 회귀를 근거로 G5 (F)/S3을 재검수. PASS 판정이면 (A) 표에 this-상대 초기화 행을 추가하고 사용자
  milestone 재상정(알려진 제한: G 멀티 BLOCKED(env), 부대 미지정 선택 로드 후 20기, 미니맵/능력 v
  UNKNOWN, 건설·승선 N/A, S3 초기메뉴 UI 자체는 env 미실측이나 새 게임/재시작 초기화는 v9로 실측 커버,
  S5 정적 귀속).
