# APPROVALS — 검수/마일스톤 판정

## 현재 판정

제품 마일스톤 확정 적용 기록은 아직 없음. G5 v10은 18:4x 조건부 사전 승인 상태이며 lap769 기술 조건을
충족했지만, 호출 지시상 마일스톤 경계라 승격 작업자가 적용한다. **G1 카드2 Stage B 실제 원본/후보 비교 실행은 승인됨.**
목표 문서 반영과 Stage B 실행 승인은 기능 승인/출시 승인이 아니다.
1단 자동 테스트 →2단 다음 새 세션 독립 검수 →3단 사용자 마일스톤 확인으로 운영한다.

## 미해결·반려·판정 불명 색인

- [ ] **2026-09-29 lap769 middle 2단 판정 — G5 v10 `PASS_WITH_LIMITS`, 18:4x 사전 승인 적용 경계.** lap768 원본20/v10 50 미니맵 이동·공격·순찰 raw에서 `pending_xy` 전원 변화와 명령 parity 확인: 이동 command3 20/20·50/50, 공격 command3 19/20·49/50+pending4 각1, 순찰 지연 command35 20/20·50/50.
  v10 SHA/원복·거부·범위, Fast 1136 passed·5 skipped, `SAFETY_PASS`; A/B/C/D/F/H PASS, E 조건부, G `BLOCKED(env)` 수용. 최신 사용자 사전 승인 조건은 충족했으나 호출 지시상 마일스톤 경계이므로 승격 작업자가 재질문 없이 G5 3단 승인·종료와 G1 전환을 기록한다.
  상세 `../history/laps/20260929_lap769_middle_g5_v10_minimap_modes_review_pass_escalate.md`.
- [ ] **lap767 middle Shift 재검수:** 원본20/v10 50 모두 추가 `1→2`, 제거 `2→1`, anchor 명령 배제 parity; lap765 이상치는 재현되지 않은 실행 이상치로 해소. v10 `PASS_WITH_LIMITS`, 사용자 판단 전 종료 금지. 상세
  `../history/laps/20260929_lap767_middle_g5_v10_shift_recheck_pass_escalate.md`.
- [ ] **2026-09-29 lap762 work tier 정보제공(middle 독립 검수 아님): G5 사용자 항목(2) 미니맵
  "마지막 1 lap" — 클릭 라우팅 체인 신규 특정, `UNKNOWN` 확정(근거 대폭 갱신).** 12:37 지시 처리.
  objdump 전수 xref로 실제 클릭 경로를 찾았다: WM_L/RBUTTON 핸들러 → `FUN_004216B0`(마우스 이벤트
  enqueue) → 매 틱 클릭 라우터(`FUN_004217B0`로 dequeue) → 필터 통과 시 `FUN_004516A0`(this=미니맵
  위젯 `0x639350`, 히트테스트+좌표변환, 판정범위 화면 x∈[0,180]·y∈(509,599] — lap710이 이미
  클릭-테스트한 다이아몬드 영역과 거의 일치) → 실패 시만 메인뷰포트 히트테스트로 폴백. **신규 반증:
  위젯 생성자 `FUN_00451130`가 좌표 LUT을 0xFF(sentinel)로 먼저 채우지만 같은 함수의 후속 루프가
  실제 맵 타일 데이터로 일부를 굽는다 — 원본 실행 중 LUT-A 32400바이트를 직접 읽어 16200/32400
  (50%)이 0xFF가 아님을 실측 확인했다.** 즉 "미니맵 렌더/좌표 서브시스템이 완전히 죽어있다"던
  lap677/710/758/760의 반복 negative 결론은 이 지점(좌표 LUT)에서는 반증된다 — 실제 지형 데이터가
  살아서 구워져 있다. **gdb 5-breakpoint 실측(원본, 2회 격리 실행, lap710 다이아몬드 5지점+
  `MINIMAP_CLICK`+`MINIMAP_CENTER`+LUT 비-FF 픽셀 좌표까지 8지점 우클릭): `FUN_004216B0`(enqueue)
  24회, 라우터 dequeue 호출 19086회(매 틱)는 확인되지만 미니맵 히트테스트 `FUN_004516A0`는 0회,
  성공/실패 리턴도 둘 다 0회.** 병목은 "렌더/좌표계산 죽음"이 아니라 라우터 내부 필터 체인(버튼타입
  검사 `0x41e332`, 좌표 sentinel 검사 `0x41e365`, 게이트 호출 `0x41e43d call 0x41c450`) 중 하나로
  코드 위치가 좁혀졌으며, 어느 분기인지는 이 lap 예산 밖(추가 브레이크포인트 3개 필요). **12:37
  지시의 명시 조항("도달하지 않으면 근거를 남기고 UNKNOWN 확정")을 충족해 `UNKNOWN`으로 확정하되,
  근거는 이전 세션들의 "렌더 진입점을 못 찾음"보다 훨씬 구체적이다(정확한 함수 주소·바운딩박스·LUT
  베이킹 상태·라우터 필터 체인 위치까지 실측).** 크래시0, `source_unchanged` 2/2, `cleanup.ok` 2/2.
  `ruff`/`compileall`(신규 파일 2개) PASS, `checks/safety.sh check` → `SAFETY_PASS`, `checks/
  context_limits.py` → `CONTEXT_PASS`(제품 코드 무변경이므로 lap758~760과 동일 판단으로 전체
  `make check` 자동화 러너는 생략). **다음 work가 라우터 필터 체인 3곳(위 각주)에 추가
  브레이크포인트로 정확한 차단 분기를 좁히거나, middle이 이 lap762 근거(렌더-완전죽음 가설 부분
  반증 포함)를 사용자 항목(1)+(2)와 v10 전체 재검수에 반영한다.** 상세
  `../history/laps/20260929_lap762_work_g5_minimap_click_router_hittest_blocked_upstream.md`,
  `../../analysis/memory_maps/g5_minimap_click_router_lap762.md`.
- [ ] **2026-09-29 lap763 work tier 정보제공(middle 독립 검수 아님): G5 사용자 항목(2) 미니맵 —
  lap762 "3-필터 브레이크포인트" 지시 처리, 게이트 확정 + 강제-플래그로 히트테스트 도달 실증.**
  12:57 지시 처리. 세 필터 지점(`0x41e332`/`0x41e365`/`0x41e43d call 0x41c450`)에 개별
  브레이크포인트+레지스터 캡처를 걸어 **`0x41e332`·`0x41e365`는 무해한 커서-아이콘 분기(둘 다
  무조건 다음 코드로 수렴, `FUN_004516A0` 호출과 무관)이고 유일한 실제 게이트는 `call 0x41c450`
  뿐**임을 확정. 관측된 9430회 호출 전부에서 반환값 `eax=0x0`. 게이트 함수 자체를 분해해
  `0x97597c`(세 OR 조건 중 하나)가 `WORD PTR ds:0x975914==3`일 때만 새 게임 초기화 코드가 1로
  쓴다는 것, `0x975914`는 로비 UI 접근자(`call 0x4ced40`, `this=0x1065d10`)의 반환값 `0x632d42`를
  그대로 복사한 "게임 타입" 계열 로비 선택값이라는 것까지 정적으로 추적. **실측(핵심): `0x97597c`를
  격리 사본 안에서 진단 전용 write(기존 stale-tail fixture와 같은 범위, `runtime_driver.write()`)로
  1로 강제하자 `FUN_004516A0` 호출 수가 0 → 6232회(성공 4195/실패 2037)로 뛰었다** — 미니맵
  렌더/좌표 서브시스템이 죽은 게 아니라 이 게이트 플래그 하나가 잠가놓고 있었을 뿐임을 직접
  실증(12:37 지시의 "성립하면 강제로 열어 원본 미니맵 우클릭 이동을 성립시켜라" 조항 충족).
  아직 fixture 유닛으로 실제 명령효과(`pending_xy`)까지는 측정하지 않았다(다음 work 과제).
  크래시0, `source_unchanged` 2/2, `cleanup.ok` 2/2. `ruff`/`compileall`(변경 파일 2개) PASS,
  `SAFETY_PASS`/`CONTEXT_PASS`(제품 코드 무변경, lap758~762와 동일 판단으로 전체 `make check`
  생략). **12:37 지시의 "성립하지 않으면 UNKNOWN 확정" 조항은 적용되지 않는다 — 성립했으므로
  UNKNOWN을 그대로 재확정하지 않고, 다음 work가 fixture로 명령효과 paired를 측정하거나 middle이
  이 근거로 항목(1)+(2)+v10 전체 재검수를 진행할지 운영자가 정한다.** 상세
  `../history/laps/20260929_lap763_work_g5_minimap_router_gate_flag_confirmed.md`,
  `../../analysis/memory_maps/g5_minimap_router_gate_lap763.md`.
- **[압축 포인터] lap756~760 work tier 정보제공 계보(원문 72줄, SHA256
  `7d693378630c3b7d14d10e1a1ad6bd036cf60f0acd57eae909b763c2ebd6e864`)** — 전문
  `docs/history/20260929_approvals_lap756_760_precompaction.md`. v10 항목(1) 50기 save/load
  구현+3-way PASS(lap756), 중간값/부대혼합 보완측정 PASS(lap757), 능력v/미니맵 provenance
  확정(lap758), 미니맵 위젯초기화 1회 확인(lap759), 수확(V) paired PASS+ddraw override 반증
  (lap760)이며, 미니맵 라우터 게이트 근본원인은 이후 lap762(필터체인 특정)→lap763(게이트=로비
  game_type 플래그로 확정, 강제로 열면 히트테스트 6232회 호출)으로 이어졌다(아래 lap763 참고).
- [ ] **2026-09-28 lap754 middle 2단 판정(Claude Code `claude-opus-5-5`/high) — G5 v9 3단 사용자 milestone
  재상정(사용자 판정 대기).** 후보 v9 `18181cdef6c787a2be9a3cf78a2851eb4d764074c972e2b13690f27af0fd2017`
  (보호 원본 `b56986e0…`에서 결정적 재빌드 일치). 독립 확인: v8→v9 diff = hook(`0x4a3168`)+cave+헤더뿐,
  `0x4a3060` 호출자 rel32 3곳 전수(모두 `this=0x892410`, 절대참조 0)·hook 무조건 경로, this-상대 선택 disp
  2건뿐, lap753 raw(원본 CLEARED/v8 PERSISTED/v9 CLEARED, v9 S1/S2/S4 원본 패리티) 일치. 1단 `make check`
  1122 passed·5 skipped, `SAFETY_PASS`/`CONTEXT_PASS`. **A~H: A·B·C·D·F·H PASS, E 조건부, G `BLOCKED(env)`.**
  알려진 제한: G 멀티 BLOCKED(env), 부대 미지정 선택 로드 후 20기(원본 동일), 미니맵 우클릭·능력 v UNKNOWN
  (원본도 무반응), 건설·승선 N/A, 체력바 46/50 가림 PLAUSIBLE, S3 초기메뉴 UI env 미실측(초기화 주체는
  정적 전수+runtime 차분 커버), S5 정적 귀속, `FUN_004AE550` 간접호출 정적 미증명·R2, 부대 H1~H3 edge.
  **사용자 판정 필요: 승인(→G1 재개) / 반려(항목 지정).** 제출 양식 전문
  `../history/laps/20260928_lap754_middle_g5_f_s3_v9_review_pass_milestone_resubmit.md`.
- [ ] **2026-09-28 lap753 work tier 정보제공(middle 독립 검수 아님): v9 + H-NEWGAME-INIT falsification
  runtime 확정.** lap752 핸드오프 처리 — v9(`patches/selection/g5_selection_cap50_v9.py`, `0x4a3168`
  1지점 hook, 재빌드 SHA `18181cdef6c787a2be9a3cf78a2851eb4d764074c972e2b13690f27af0fd2017`, pytest 7개
  PASS, v1~v8 바이트 무변경) + `tools/g5_stale_tail_probe.py --newgame-stale-probe`(신규 게이트: 유닛
  selected-flag를 건드리지 않고 선택 배열에 직접 stale 주입 → dec 경로 개입 불가 상태에서 재시작).
  **원본 `NEWGAME_STALE_CLEARED`, v8 `NEWGAME_STALE_PERSISTED`, v9 `NEWGAME_STALE_CLEARED`**(사전
  등록한 세 갈래 그대로 확정, `source_unchanged=true` 4/4, `cleanup.ok=true` 4/4). v9 S1/S2/S4 회귀
  `PASS_NO_STALE_TAIL_EFFECT`·`S4_PASS_SELECTION_CLEARED`. `make check` 1122 passed·5 skipped
  (774.79s), ruff/mypy(0 issue)/`CONTEXT_PASS`/`SAFETY_PASS` 전부 PASS. `patches/population/
  runtime_driver.py`에 `write()` 추가(진단 전용, 기존 `read()`와 같은 격리 Wine 자식 프로세스 범위).
  **호출자 gdb 귀속(핸드오프 ②)은 의도적으로 생략** — 세 호출자(`0x41b9c0`/`0x41bc4f`/`0x4c3e59`) 모두
  동일한 `0x4a3060`을 호출하고 v9는 그 함수 내부 단일 명령을 hook하므로 어느 호출자가 불렸는지는 hook
  정확성과 무관하다는 work 판단(핸드오프 자신이 "귀속은 증거용"이라 명시); middle이 동의하지 않으면
  다음 lap에서 gdb 귀속을 보강한다. **middle이 이 새 runtime 증거로 (F)/S3를 재검수할 차례.** 상세
  `docs/history/laps/20260928_lap753_work_g5_f_s3_v9_newgame_init_falsified_confirmed.md`.
- [ ] **2026-09-28 lap752 middle 2단 판정(Claude Code `claude-opus-5-5`/high, v8 (F) 최종 재검수):
  G5 v8 = `HOLD(좁은 조건부)` 유지 — 사용자 milestone 재상정·G1 착수 안 함.** lap751 analogy(재시작=해체
  경로 → 새 게임도 안전) **수용 거부**. 근거(정적, 원본 `b56986e0…`·v8 재빌드 `ef46d1ac…` 일치): 원본 새 게임
  초기화 `0x4a3060`(호출자 `0x41b9c0`/`0x41bc4f`/`0x4c3e59`, `ecx=0x892410`)은 저장 창 전체 `rep stosd`
  (0x38e5f dword) 후 `0x4a3168 mov [esi+0x6c14],ebx`(레거시 선택 count=0)와 `0x4a31eb` 20칸 루프로 선택을
  **직접** 비운다. v8 새 배열 `0x0108C000..+0xCC`는 창 밖이라 이 보장에서 빠진다(H-NEWGAME-INIT) — 새 게임
  빈 선택이 직전 판 해체의 dec에만 의존. (A) 표는 절대주소만 세서 이 this-상대 쓰기 2건을 놓쳤다.
  **다음 work:** v9(`0x4a3168` 1지점 → cave에서 새 배열 51 dword 0) + 초기메뉴 없이 게임 시작/재시작 직전
  stale 주입 paired probe(v8 잔존 예상/v9 0/원본 레거시 0) + 회귀. 근거
  `../history/laps/20260928_lap752_middle_g5_f_s3_newgame_init_gap_v9_handoff.md`.
- [ ] **2026-09-28 lap751 work tier 정보제공(middle 독립 검수 아님):** lap750 핸드오프 ①②(S3 귀속·
  실측) 처리. `tools/g5_stale_tail_probe.py`에 `--restart-dump-only`·`--menu-exit-fresh` 게이트
  2개 추가(기존 S1~S5 분기 무변경). **① v7 restart-dump-only = `RESTART_DUMP_TAIL_CLEARED`**
  (드래그 50 후 저장/로드 없이 곧장 재시작(다시하기), `full_dump` 전/후 비교 — 재시작 전 count=50·
  nonzero=50, 재시작 후 count=0·nonzero=0·50칸 전부 0. v7의 `LOAD_WRAPPER`는 20칸만 0 채우므로
  재시작이 그 경로였다면 21~50칸이 남아야 했다 — 남지 않았으므로 **재시작은 유닛 해체(dec,
  `0x412ed2`) 경로**로 확정, 핸드오프가 사전 등록한 두 해석 중 하나를 확정). **② 원본·v8
  menu-exit-fresh(fixture/선택 생성 전, 순정 로비 시작 직후) = 둘 다
  `MENU_EXIT_FRESH_BLOCKED_SAME_AS_FIXTURED`**(`ps` 23→3 즉시 복귀, 메인 메뉴 `ps==9` 도달 없음) —
  lap747의 "원본도 동일 재현"이 fixture/선택 상태와 무관한 환경/원본 고유 제약임을 fixture 없는
  최소 조건에서도 재확인. **종합:** 핸드오프 branching(③)의 v9 트리거("①이 로드 경로이고 ②가
  불가")가 성립하지 않아(①이 정반대: 좁은 경로가 아닌 더 넓은 해체 경로) **v9 미착수**. 다만 이것은
  "S3가 재시작과 같은 함수를 탄다"는 직접 증거가 아니라 유추이며, S3 자체는 이 하네스에서 여전히
  실측 불가(`BLOCKED(env)`)로 남는다. `pytest` (v7/v8 selection) 9 passed, `make check` 1115
  passed·5 skipped(783.17s), ruff/mypy/`CONTEXT_PASS`/`SAFETY_PASS` 전부 PASS. 3회 실행 전부
  `source_unchanged=true`·`cleanup.ok=true`(고아 프로세스 0), 제품 코드 0 변경(도구 파일 1개만).
  **middle이 (F)를 이 새 증거로 최종 재검수할 차례** — analogy를 BLOCKED(env) 수용 근거로 받아들일지,
  재시작 핸들러/새게임 초기화가 같은 함수인지 정적 대조(gdb 워치포인트/xref)까지 요구할지 판정. 상세
  `docs/history/laps/20260928_lap751_work_g5_s3_restart_attribution_menu_exit_env_confirmed.md`.
- [ ] **2026-09-28 lap750 middle 2단 판정(Claude Code `claude-opus-5-5`/high, v8 기준 A~H 최종 독립 재검수):
  G5 v8 = `HOLD(좁은 조건부)` — 사용자 milestone 재상정·G1 착수 안 함.** 독립 확인: 보호 원본 `b56986e0…`
  에서 v7 `30efafa0…`/v8 `ef46d1ac…` 재빌드 일치, `cmp` 1바이트(`0x108f1bc mov ecx,0x14→0x32`), G5 pytest 9
  passed, `make check` 1115 passed·5 skipped, `SAFETY_PASS`/`CONTEXT_PASS`. 판정: A~E·H PASS(E 조건부 유지),
  G `BLOCKED(env)` 수용, 홀드버튼 PASS(0/50·3/50은 클릭 후 첫 샘플 전 transient 종료 race — lap749 원인
  설명 정정). **F HOLD:** S1/S2/S4 raw 일치 PASS, **lap748 S5는 S4 재시작 직후 selection_before=0·fixture
  소멸 상태에서 실행돼 50 선택 이월을 시험하지 않았다(공허; 저장 창 로드가 `0x4412dc` 한 곳뿐이라 정적
  귀속으로만 수용)**, **S3(초기메뉴→새 게임)는 새 배열 count 쓰기가 inc/dec/`LOAD_WRAPPER`뿐이라 이월
  가능성이 남는 실제 위험**. 다음 work: v7로 재시작 초기화 주체 귀속 + S3 실측(→필요 시 v9). 근거
  `../history/laps/20260928_lap750_middle_g5_v8_final_review_hold_s3_s5_gap.md`.
- **[압축 포인터] lap746~749 work tier 정보제공 계보(원문 38줄, SHA256
  `4a80650d6f7132ba4ce203921496d682b01f84f1337b67fec2af054def158db0`)** — 전문
  `docs/history/20260929_approvals_lap746_749_precompaction.md`. H-STALE-TAIL v8 수정(lap746),
  S3 대체경로 S4/S5 PASS(lap748), 홀드버튼 편차 타이밍 아티팩트 확정(lap747/749)이며 이후
  lap750/752/754 middle 재검수로 모두 해소·재분류됐다.
- **[압축 포인터] lap729~731 work tier 정보제공 계보(원문 63줄, SHA256
  `96123d3d55e5caa161c9af6c5d3dcf5240cb795f5a3c91a8df8f8af5d026ee44`)** — 전문
  `docs/history/20260928_approvals_lap729_731_precompaction.md`. 채집(lap729)·수리(lap730)
  broadcast PASS, 일꾼/HQ 커맨드그리드 전수 조사로 건설·승선하선 N/A·좌표일치 PASS 잠정(lap731,
  이후 lap736이 건설 N/A를 3개국 전수로 강화). (D) Ctrl+숫자/호출/저장로드는 이미 v5
  `PASS_UI_ROUNDTRIP`(lap724)로 커버됨을 lap731이 확인.
- **[압축 포인터] lap725~727 work tier G5 (A) 정적 전수 표·(B) 잔여 항목(Shift 제거/51번째 거부/더블클릭·ALT·Ctrl 선택/포트레이트 해제) PASS 계보(원문 51줄, SHA256 `6ac0a16048bac604fac3ab99e788310a2453f4bbf9e83cb0be8f5acf79b3c580`)** — 전문 `docs/history/20260928_approvals_lap725_727_precompaction.md`. lap727이 열어둔 05:15 Shift+클릭 개별 추가 관찰(잠정 비결함 판단, 격리 재확인 보류)은 아래 lap728이 해소.
- **[압축 포인터] lap728·732·733·738~743 work tier G5 체크리스트 (B)~(H) 정보제공 계보(원문 178줄, SHA256
  `e216b00aa95013c7782d61bb7919ba03012eeef04e2386e873d51769b358fc42`)** — 전문
  `docs/history/20260928_approvals_lap745_work_g5_checklist_precompaction.md`. Shift+클릭 추가 격리 PASS(lap728),
  (D) 사망 후 호출 v5 FAIL→v6 수정(lap732/733), (E) UI PASS(lap738), (F) raw 선택 저장/로드 v6 FAIL→v7
  앞20 미러링(lap739/740), (G) Wine dpwsockx stub·네이티브 IPXWrapper 4조합 `BLOCKED(env)`(lap741~743),
  (H) 8019 tick PASS(lap743). 운영자 판정 원문(09:05·10:06·14:05·14:45·15:05·15:23·15:55·16:35)은 본문에 그대로 둔다.
- **[압축 포인터] lap724 work tier G5 v5 ALT/Ctrl/Shift 드래그·부대저장로드·공격 직접 raw 재측정
  전부 PASS, lap723 미완결 해소(원문 19줄, SHA256
  `ee508556786f9d6b1e730598ce97cd152cdaddda7824487ea8866d8ab008df90`)** — 전문
  `docs/history/20260928_approvals_lap724_precompaction.md`. **열려 있는 middle 검수 요청(미해결,
  체크리스트 전체 완료 후 middle이 답할 문항):** 이 lap의 raw 3건이 lap717 v4 패턴과 일치하는지 재계산,
  coverage probe 목적지 오프셋 확장의 안전성, Xvfb 고아 프로세스 발견(제품 무관 관찰)을 안전 위험으로
  볼지. 근거 `docs/history/laps/20260928_lap724_work_g5_v5_direct_coverage_roundtrip_attack.md`.
- **[압축 포인터] lap723 work tier G5 R3 raw CONFIRMED·v5 수정 PASS(원문 20줄, SHA256
  `635e86c33226c4417fa99d50ef10a00b00685ce668b353e80c3351982bfa3ed8`)** — 전문
  `docs/history/20260928_approvals_lap723_precompaction.md`. middle 검수 요청분(ALT/Ctrl/Shift
  드래그·공격·부대저장로드 미완결)은 lap724가 같은 v5로 직접 재측정해 해소(아래 lap724 참고).
- **[압축 포인터] lap712~721 G4 생산 계측(H_AVAIL/PREREQ_OWN 히스토그램, H-CROWD v1 FALSIFIED)·G5 v4 middle·work tier 요청 계보(원문 140줄, SHA256 `4077e7d84cee6ea3fbeb62d4ac168c7dee7899d25eadeb0f8d9cbf21d81dbeb2`)** — 전문 `docs/history/20260928_approvals_lap712_721_g4g5v4_precompaction.md`. G4 트랙은 2026-09-27 12:05 판정으로 보류, G5 v4는 2026-09-28 02:35 지시로 v5로 교체되어 이 계보의 middle 검수 요청은 모두 v5 재측정(lap723/724)으로 해소됐다.
- [ ] **2026-09-27 lap707~711 work tier 정보제공 5건 압축(원문 79줄, SHA256 `a095d6ea2da22ec04a29725615fcd03f798aac75e0361926e3bfd71390ceb1e5`):** 전문은 `../history/20260927_approvals_lap707_711_precompaction.md`에 보존. G4-P1 길찾기 baseline·scenario probe·개선후보 v1/v2 반증·미니맵 BLOCKED·v3 타임아웃 반증(lap707~711) work tier 정보성 기록이며, 2026-09-27 12:05 운영자 판정으로 길찾기 트랙 자체가 종료돼 더 진행하지 않는다(STATUS/lap712 참고).
- **[압축 포인터] G4 W2 postload lap700/702 검수요청+lap701/703 middle 검수 완료(W2 종결)** — 원문 66줄 SHA256 `b7b4eeac6e44e55d0e708b68d3a467d9e22c1674785b2b5ee3c48782193e17f5`, 전문 `docs/history/20260927_approvals_lap719_precompaction.md`.
- [ ] **2026-09-27 lap695~699 G2 8인×10000 middle 검수요청 4건 압축(원문 44줄, SHA256 `2eea22c0c4af8101915dc323a6f4d829371ea155d82f8f01adcffb8fae99a824`):** 전문은 `../history/20260927_approvals_g2_supply10000_middle_requests_precompaction.md`에 보존. G2 8인×10000 전역풀4092/저장로드/전역열거 무결성/A·B 판정자료(lap695~699) middle 검수 요청이며, 2026-09-27 03:21 사용자 판단으로 이 트랙 자체가 종료돼 더 진행하지 않는다(STATUS 참고).
- **[압축 포인터] lap665·683~689 v3 명령범위/공격 검증 계보 6건(원문 18줄, SHA256
  `e06d2986fdde49d2cbcf398d21af75760efd61d9624d89e80b054d34329d5761`)** — 전문
  `docs/history/20260928_approvals_lap683_689_v3_command_range_precompaction.md`. v3 후보 대상
  검증이며 이후 v4/v5로 교체·재검증됨(아래 lap724, STATUS 참고).
- [ ] **G5 3단 사용자 milestone 판단 대기 전 선행:** work tier candidate50 대 original20 실제 공격 paired probe → 새 중간 tier 2단 재검수. 멀티 동기화는 `UNKNOWN`으로 별도 표시하며 사람 승인으로 바꾸지 않는다.
- **2026-09-24~26 위임 승인 22건 압축(원문 22줄, SHA256 `4ed30516913c8f39bd22caba434682f642dd96c231a9307af15633d31b13fb60`):** 전문은
  `docs/history/20260927_approvals_g5_g4_delegated_approvals_20260924_20260926_precompaction.md`에
  보존. G5 crash/스택 오버플로/hit-test/fixture 위임 승인 계열(모두 lap640~659에서 해소·G5
  드래그50 PASS로 종결)과 G4 W1/G2 Q12 관련 개별 위임 승인들이다.
- [ ] 2026-09-25 KST **G2 S5′ 3단 재제출 — 사용자 3단 확정 대기(Q12는 위임 결정 A·나·iv, 부록 B로 제출 확정).** 제출문 `../reports/20260925_G2_S5P_MILESTONE_RESUBMISSION_LAP589.md`. 결합 후보 `dfdc91ad…3883`의 혼합 24k·144k·판별형 저장/로드·F4 raw ACCEPT. 화면 미검증(W49/W49R REJECT, N214), S4 멀티 `UNKNOWN(harness_contract)`+Wine9.0 SP blocker, 교전 제외. G2 합격 아님.
- [x] 2026-09-24 23:05 KST Q11: Q11-2 **(나)** 사용자 선택, Q11-1 사용자 위임→**(A)** 부분 증거 인정(G2 PASS 아님, 남은 조건 1~7 유지).
- [ ] 2026-09-24 21:57 KST **G2 S5 3단 제출 — 사용자 판정 대기(Q11).** 제출문 `../reports/20260924_G2_S5_MILESTONE_SUBMISSION_LAP567.md`. 모델 판정: 부분 증거(W21·W26·W44R 24k 안정 동작) + W44R B4 FAIL(`REJECT`, N208) + 미충족 7항. G2 합격 아님.
- [x] 2026-09-24 19:02 KST 사용자 판정 Q10: **(마)** 도구 수리 후 fresh 1회, 실패 시 **(다)** 교전 트랙 중단(재질문 없음).
- [x] 2026-09-24 14:31 KST 사용자 승인: W42 op9용 가드 `op > 9` 확장과 op8 계약 핀 테스트 기대값 갱신(해당 1개 테스트만).
- [x] 2026-09-24 03:15 KST 사용자 판정: **S1 교전 = (라)** 원본 이동 명령 후 op8 공격 2단 입력. (가) AI 변경·(나) 사람 슬롯·(다) 중단 미선택.
- [x] 2026-09-23 18:43 KST 사용자 판정: **Q8 = (ㄱ)** — G2를 시딩 기반 cap 근접+안정 증거로 재정의. (ㄴ) AI 변경·(ㄷ) 보류 미선택.
- [!] 기존QHD 시야 확장 후보는 G1 요구 미충족 — 사용자 피드백2026-09-10.
  근거: `../history/20260910_VISUAL_GOAL_CORRECTION.md`. 새1600×1200 구도 유지 결과로 재검수해야 한다.

## 확정 (사람만 적는다)

- **2026-09-29 18:45 G5 v10 3단 승인·종료(사용자 18:4x 사전 승인, 운영자 적용):** lap769 middle `PASS_WITH_LIMITS`(FAIL 0, Fast 1136 passed·5 skipped, SAFETY_PASS) 확인. 후보 SHA `c3ceaa25dea98232234759a332b867d92a669f63a03c3f453d3199cc329ebfad`. 수용 제한: G 멀티 `BLOCKED(env)`, 미니맵은 진단 gate 조건 PASS(정상 game_type==3 UI 경로 미증명), E 체력바 46/50 조건부, 건설·탑승 N/A, 간접호출 정적증명 없음, H edge. 다음 G1, G2 전체 점검은 G1 뒤.

없음. 기존24k나 pytest 통과를 사람 승인으로 적지 않는다.

- **2026-09-29 18:4x 사용자 G5 사전 승인(운영자 대리 기록):** "다시 여쭙지 말고 G5 체크까지 다 하고 끝나면 G1 이어서 해". lap769 middle 재검수가 **PASS_WITH_LIMITS**(FAIL 없음, Fast PASS)로 끝나면 G5 v10(SHA `c3ceaa25…`)을 알려진 한계(멀티 BLOCKED(env), 미니맵 정상 game_type UI 경로 미증명, 체력바 46/50, N/A·edge, 간접호출 정적증명 없음)와 함께 **사용자 3단 승인으로 종료**한다. 재상정 질문 없음. lap769가 FAIL/HOLD면 이 승인은 효력 없고 G5 수정부터 한다.

## 실행 승인 (사람 판정)

- 2026-09-23 04:13 KST — 사용자가 되물음 2건을 마감했다. 원문: "전비가 일시적으로 5000을 넘어 보이는 표시를
  허용하고, 32비트도 괜찮아".
  - **lap404 = (가) 확정.** 일시 `used+reserved` 초과 표시를 허용하고 **라이브 `used` ≤5000만
    강제**한다. 승인 범위는 판정 기준의 변경이며, 이것으로 G2 제품 합격·마일스톤 승인이 되는 것은
    아니다. N19 단서(지속 시간 owner당 수 분·초과 표본 216건·대조군 귀속 미증명)는 고지 후 승인.
  - **F4 = (B) 확정.** 전비 장부 **32-bit 확장**을 채택한다(저장포맷 변경 동반). (C) 도달성 실측
    선행은 기각됐다. 착수 범위·순서는 strategy/middle이 카드로 정하며 이 승인만으로 원본 패치
    실행이 허가된 것은 아니다.
  - **여전히 사용자 전권 대기: Q7-A=(ㄴ) AI/설정 변경 예외 · Q7-B 3단 마일스톤 · (ㄱ) · (ㄷ).**

- 2026-09-12 01:03 KST — 사용자가 "승인. 루프 계속 돌아"라고 명시했다.
  승인 범위는 G1 카드2 Stage B의 격리된 원본/1600×1200 후보 실제 비교를 **증거가 성립할
  때까지 bounded repair → fresh validation으로 계속하는 것**과 그 독립 검수다. 실패를 보존하지
  않는 무변경 blind retry는 금지하며, 각 수리 뒤 검증 run은 handoff의 exact-once/fresh 규칙을
  지킨다. R5처럼 Stage B가 무엇을 증명하는지 조이는 변경은 포함한다. 제품 G1 합격·출시 승인,
  P6 착수, G2~G4 승인은 포함하지 않는다.

## 반려 (사람이 적는다 → 다음 바퀴 최우선)

QHD 해석 반려는 위 색인에 보존했으며 최신1600×1200 목표로 반영했다.

## 제출 양식

마일스톤/목표, 후보SHA, 기준·후보 캡처, 실제 입력·부하조건, 1단 결과,
2단 판정자(실제 모델), 다른 점/허용 오차, 남은 위험, 사용자 판정.
스크린샷 파일은 공유temp에 두고 해시/경로를 함께 남긴다.
- **G5 lap673~lap689 bisection 경과 압축(2026-09-26 10:31~20:23, 원문 18줄, SHA256 `4b7d2e030abb6ec8f2504c121da8d9ab97db16a09801de7f552b5ea9ed6e4194`):** 전문은 `docs/history/20260927_approvals_g5_bisection_block_precompaction.md`에 보존. G5는 아래 2026-09-26 21:54 사용자 판단으로 단일플레이 milestone 최종 승인·종결됐다.
- **[압축 포인터] lap690~719 G5 v3/v4 승인·G2 10000 트랙 전체(경로전환·종료)·G4 AI 생산게이트
  계측·보류 계보(원문 14줄, SHA256
  `92c4e75ac5d43001d70f164c49ac33343db41cabeb8f94606a44d8f680d50bd0`)** — 전문
  `docs/history/20260928_approvals_lap742_g2g4_tail_precompaction.md`. 핵심 결론만 남긴다:
  G5는 2026-09-26 21:54 단일플레이 승인(v3) 후 2026-09-27 17:25까지 v4로 조건부 유지; G2는
  2026-09-27 03:21 사용자 판단으로 전비5000 복귀·10000 트랙 종료(달성 인정, 더 진행 안 함);
  G4(길찾기/AI)는 2026-09-27 15:12 사용자 지시로 보류(생산게이트 히스토그램까지만 완료); G1은
  대기; 원본 기준 경로는 2026-09-26 22:52 결정대로 `[ESL]Syw2plus/`(SHA `b56986e0…` 동일).
- **2026-09-28 01:27 사용자 판단(AskUserQuestion 응답):** "v4 승인, 바로 G1". **G5 확정 후보를 v4(`patches/selection/g5_selection_cap50_v4.py`)로 교체·승인**(단일플레이; 정지·홀드·순찰 50/50, 이동·공격·그룹·저장로드·ALT/Ctrl/Shift 드래그 유지, 선택 축소 누출 0, 크래시 0). 미확인 메모: 멀티 동기화, 미니맵 우클릭(격리 환경 무반응), R2. 실사용 EXE는 나중에. **다음 최우선: G1 — 원본과 같은 화면 구성을 유지한 1600×1200 고해상도.** 다음 work는 기존 G1 기록(`docs/history/laps/*g1*`, `analysis/memory_maps/*g1*|*resolution*`)으로 현재 상태·막힌 지점을 요약하고, 구현 우선으로 가장 작은 다음 후보를 만들어 격리 실행 캡처로 원본(800×600) 대비 구도 동일성·HUD 배치·깨짐을 확인.
- **2026-09-28 01:30 사용자 지시:** "R3부터 해결해야겠는데?" **G5 R3를 G1보다 먼저 처리**(lap722 G1 중단). work(구현 우선): ① R3 probe — 50기 선택 후 앞쪽 엔트리 유닛들을 죽여(bridge로 제거/HP 0 등) 남은 수를 ≤20으로 만들되 생존 유닛이 배열 21번째 이후에 있게 하고, 이동·정지·공격을 내려 생존 유닛 전원이 명령을 받는지 원본 대응 조건과 paired로 측정, ② 실패(예상)하면 **v5**: 청크 게이트를 'count>20 **또는** entries[20:50]에 0 아닌 칸이 있으면 청크'로 바꿔 빌드, ③ R3 재측정 + 회귀(이동/정지·홀드·순찰/공격/그룹·저장로드/드래그 3종, 크래시 0, `make check`), ④ middle 재검수. 끝나면 G1 재개.
- **2026-09-28 01:31 사용자 지시:** "이런 사이드 이펙트 다 고려하고, 다 문제 없는 경우에야 G5 끝내야 할거 아냐". **G5 v4 승인은 '조건부'로 되돌린다. 아래 G5 완료 체크리스트가 전부 PASS(또는 원본과 동일 동작)여야 G5 종료, 그 전엔 G1 재개 금지.** G5 완료 체크리스트(원본 20 대 후보 50 paired, 크래시 0 포함): (A) 정적 전수: 선택 count/엔트리(옛 `0x899024/0x899028/..0x899078`, 새 `0x0108C000`)를 읽거나 쓰는 모든 코드와 `FUN_004AE550` 호출자 22곳+간접 호출을 표로 만들고 각각 20 전제·경계·재배치 누락 여부 판정; (B) 선택 변화: 드래그/Shift 추가/Shift 제거/ALT/Ctrl/더블클릭 같은 종류 전체 선택/포트레이트 클릭 해제/유닛 사망·건물 진입·변신으로 인한 자동 해제(R3 포함, 앞·중간·뒤 엔트리 사망)/51번째 거부; (C) 명령 전부: 이동·미니맵 우클릭(원본에서 작동하는 환경을 찾아 확인)·공격(지면/대상)·정지·홀드·순찰·채집/건설/수리 등 일꾼 명령·특수능력/변신·승선/하선 등 툴바에 있는 모든 버튼과 단축키, 명령 직후 대기열·목적지 좌표 일치; (D) 부대: Ctrl+숫자 지정, 숫자 호출, Shift+숫자 추가, 부대 안 사망 후 호출, 저장·로드 전후; (E) UI: 50기 선택 시 초상화/정보 패널 표시·클릭·스크롤, HUD 깨짐, 선택 표시(체력바) 50기; (F) 저장/로드: 50기 선택 상태·부대 상태 저장 후 로드, 원본 세이브 호환; (G) 멀티: 2인 LAN 격리 실행에서 50기 명령 동기화(패킷 최대 3배) 또는 불가 시 사유 명시; (H) 장시간: 50기 반복 명령 수천 tick 안정성. 진행: 먼저 R3(lap723) → 이후 이 체크리스트를 항목별로 work가 채우고 FAIL은 즉시 수정(v5+), 마지막에 middle이 체크리스트 전체 독립 재검수 → 사용자 milestone 재요청.
- **[압축 포인터] lap723~733 G5 체크리스트 v5/v6 운영자 지시 원문 9건(원문 9줄, SHA256
  `6c228495629c3e2fb6d7ca8acffe2b83e8f95269a6c532ce4c84614acfa40559`)** — 전문
  `docs/history/20260929_approvals_lap723_733_g5_checklist_v5_v6_precompaction.md`. v5 R3 수정
  착수부터 v6 채택까지(A 정적표, B 사망/Shift+클릭 추가 FAIL→수정, C 건설/특수능력, D
  사망후호출 FAIL→v6 수정)이며 이후 v7/v8/v9/v10으로 후보가 교체되며 전부 해소됐다.
- **[압축 포인터] lap734~737 work tier 정보제공 계보(원문 89줄, SHA256
  `ad5ee26fb93f7c2a112bc71a0d179aaf3b2c4d09b54c89c0c379ec575c8ed036`)** — 전문
  `docs/history/20260928_approvals_lap734_737_precompaction.md`. v6 핵심 회귀 전부 PASS(lap734),
  특수능력 paired 부분 완료(lap735), 건설 3개국 전수 N/A 강화(lap736), "v"/"i" 능력 유효 타겟
  탐색 완료·(C) 체크리스트 전체 완료 선언(lap737).
- **[압축 포인터] lap739~747 G5 v7/v8 체크리스트 진행·middle HOLD 판정 계보(원문 20줄, SHA256 `a0f1c7106e02e1983027e2c1eec692bf8d25f9f0f333a50363b402852c7b8d4f`)** — 전문 `docs/history/20260929_approvals_lap739_747_v7_v8_precompaction.md`. v7 F-2(미지정선택 save/load 앞20만) 발견→v8 H-STALE-TAIL 수정(lap739~746), 홀드버튼 편차 관측(lap747), lap745 middle HOLD(조건부, F 보류) 판정이며 이후 v9(lap753/754 PASS)·v10(lap756/757 항목(1) PASS)으로 전부 해소·대체됐다.
- **2026-09-29 00:59 사용자 판단(AskUserQuestion):** G5 v9 milestone **보류**. 추가 확인 항목: **(1) 부대 미지정 드래그 50기 선택이 저장/로드 후 50기 전부 복원**(현재 앞 20기만; 원본 세이브 형식과 양방향 호환 유지 조건 — 원본 EXE가 v10 세이브를 열어도 크래시 없이 앞 20기, v10이 원본 세이브를 열어도 정상), **(2) 미니맵 우클릭 이동과 특수능력 v를 실제로 동작하는 조건에서 원본20/후보50 paired 확인**(격리 환경에서 미니맵이 검게 그려지고 무반응인 원인 — 렌더/입력 좌표/미니맵 활성 조건 — 을 찾고, v는 설명서·툴팁·대상 조건 탐색). 멀티·초기메뉴 경로는 알려진 제한 유지. G1 재개 금지. 진행: work가 (1)을 먼저 구현(v10: 21~50번째 엔트리를 저장 창 안의 미사용 영역 또는 세이브 파일 뒤 추가 블록에 보존, 로드 시 복원) → paired 재측정 + 회귀, 그 다음 (2). 끝나면 middle 재검수 후 사용자 재상정.
- **2026-09-29 09:55 운영자 지시(lap756 v10 수용, 다음 work):** 기준 후보 **v10**. work가 이어서 한 lap에: ① v10 보완 측정 — 부대 미지정 선택 count 중간값(예: 25, 35) 저장/로드, 부대(Ctrl+숫자)와 섞인 상태 저장/로드, v10 핵심 회귀 1회(드래그4종·명령·공격·그룹·사망후호출·R3·Shift). ② 사용자 항목(2) 착수 — 미니맵이 격리 환경에서 검게 그려지는 원인(렌더 옵션/미니맵 토글 키/시야·탐색 상태)을 찾아 미니맵 우클릭 이동을 원본에서 먼저 작동시키고 원본20/v10 50 paired, 특수능력 v는 설명서·툴팁 텍스트로 대상 조건 확인 후 paired. 끝나면 middle이 v10 전체 재검수.
- **2026-09-29 10:35 운영자 지시(lap757 후속):** 이번 work는 **사용자 항목 (2) 미니맵 우클릭·특수능력 v만** 한 lap에 집중(v10 회귀는 diff가 저장/로드 hook 한정이라 middle 최종 검수 때 1회로 충분). ① 미니맵: 격리 환경에서 검게 그려지는 원인 규명(미니맵 토글 단축키·옵션 메뉴, 탐색/시야 상태, 렌더 경로), 원본에서 미니맵 우클릭 이동이 되는 조건을 먼저 만들고 원본20/v10 50 paired. ② 특수능력 v: 설명서·툴팁 텍스트로 기능과 대상 조건 확인(적/아군/지면/건물), 조건 충족 fixture로 원본20/v10 50 paired. 원본에서도 구조적으로 불가하면 그 근거를 명확히 기록.
- **2026-09-29 11:25 운영자 지시(항목 2 가속, 구현 우선):** 정적 추적을 줄이고 실측으로 간다. ① **수확(V=0x05)**: 일꾼 선택→V→자원(밭/나무 등 lap729 gather에서 채집이 된 타일)을 좌클릭, 원본20/v10 50 paired로 pending 수신 수 측정(원본 먼저 성공 조건 확보). ② **미니맵 검은 화면**: 원본 폴더의 `ddraw.dll`(2.3MB, DirectDraw 래퍼 추정)이 격리 사본에서 실제로 로드되는지(`WINEDLLOVERRIDES=ddraw=n,b`)와 미니맵 렌더 차이를 캡처로 비교 — 래퍼로 미니맵이 그려지면 그 상태에서 미니맵 우클릭 이동 원본20/v10 50 paired. 래퍼로도 안 되면 미니맵 클릭 입력 핸들러(미니맵 영역 좌표→월드 변환→이동 명령)를 브레이크포인트로 확인. 둘 다 한 lap 안에 원본 성공 조건을 못 찾으면 근거와 함께 UNKNOWN 유지 판단을 기록.
- **2026-09-29 12:37 운영자 지시(lap761 후속, 미니맵 마지막 1 lap):** 수확(V) paired PASS(원본20/20, v10 50/50) 수용. ddraw 네이티브 override는 미니맵 원인 아님(반증). 다음 work 1 lap 한정: 미니맵 클릭 입력 핸들러 — 미니맵 화면 영역 클릭 시 호출되는 함수(마우스 좌표→미니맵 영역 판정→월드 좌표 변환→이동/카메라)를 브레이크포인트로 찾고, 원본에서 입력이 도달하는지 확인. 도달하면 그 경로의 명령 발행이 선택 전원(원본20/v10 50)에 가는지 paired, 렌더와 무관하게 입력만 살아있으면 PASS 가능. 도달하지 않으면(격리 환경에서 미니맵 입력 비활성) 근거를 남기고 **UNKNOWN 확정**. 그 다음 middle이 사용자 항목 (1)+(2)와 v10 전체 재검수(v10 핵심 회귀 1회 포함).
- **2026-09-29 12:57 운영자 판정(lap762, 미니맵 1 lap 연장 — 원인 위치가 3지점으로 좁혀짐):** 미니맵 입력은 WM 핸들러 enqueue(24회)·라우터 dequeue까지 도달, 히트테스트 `FUN_004516A0`는 0회. 다음 work 1 lap: 필터 3지점(`0x41e332` 버튼타입, `0x41e365` 좌표 sentinel, `0x41e43d call 0x41c450` 게이트)에 브레이크포인트로 어느 분기에서 떨어지는지 확정. 격리 환경 탓(예: 게이트가 창 포커스/미니맵 표시 플래그를 요구)이면 그 플래그를 브리지로 켜서 원본 미니맵 우클릭 이동을 성립시킨 뒤 원본20/v10 50 paired. 이번 lap에서도 성립 못 하면 **UNKNOWN 확정·원인 지점 기록**하고 middle 재검수로 넘어간다(추가 연장 없음).
