# APPROVALS lap728·732·733·738~743 work tier G5 체크리스트 정보제공 계보 원문 보존 (2026-09-28, lap745 압축)

SHA256 `e216b00aa95013c7782d61bb7919ba03012eeef04e2386e873d51769b358fc42`(원문 178줄; 압축 전 APPROVALS 전체 293줄 SHA256 `2358dc1cd256fe858cef1cd9608902cefe41338b2566110ccb35919dd3f385fd`)

- [ ] **2026-09-28 lap728 work tier(Claude Code Sonnet, 정보 제공용 — 새 middle 검수 요청 아님, 2026-09-28 03:36 운영자 판정에 따라 middle은 체크리스트 전체가 채워진 뒤 한 번에 진행):** 05:36 운영자 판정(Shift+클릭 개별 추가 격리 재확인)을 수행. 신규 `tools/g5_shift_click_add_probe.py`가 worker 기준 맨해튼거리≥3 희소 오프셋(조밀 55기 fixture 대신)에 SEED_TYPE 유닛을 최대 10개 스폰하고, 각 후보를 단독 plain 클릭했을 때 정확히 그 슬롯 1개만 선택되는지 격리 확인(원본·v5 둘 다 9/9 PASS)한 뒤 통과분 6개로 plain 클릭 1회+Shift+클릭 5회 순서를 실행 — **원본·v5 둘 다 6단계 전부 PASS**(count 1→2→3→4→5→6, 매 단계 새 슬롯 포함·이전 슬롯 유지 전부 확인, 최종 6기 전원 이동 명령 수신). lap727 05:15 관찰(원본 2→3, v5 1→2)은 **조밀 fixture 스프라이트 겹침 아티팩트였음이 이번 격리 재현으로 확정**됐다(v5 결함 아님). 크래시0, `source_unchanged` 2/2, `cleanup.prefix_processes_after=[]` 2/2. `make check` **1106 passed(764.94s)**, ruff/mypy/`CONTEXT_PASS`/`SAFETY_PASS` 전부 PASS(신규 pytest 0개, 제품 코드 무변경). **이로써 (B) 체크리스트 전체 완료.** 다음 work: **(C) 명령 전부**(일꾼 채집/건설/수리 등 특수 명령, 특수능력/변신, 승선/하선 등 툴바 전체 버튼과 단축키, 명령 직후 대기열·목적지 좌표 일치). 근거 `../history/laps/20260928_lap728_work_g5_shift_click_add_isolated_pass.md`.
- [ ] **2026-09-28 lap732 work tier(Claude Code Sonnet, 정보 제공용 — 새 middle 검수 요청 아님, 2026-09-28 03:36 운영자 판정에 따라 middle은 체크리스트 전체가 채워진 뒤 한 번에 진행):** (D) 잔여 두 항목을 신규 `tools/g5_group_shift_add_death_recall_probe.py`(원본 1회·v5 1회, 한 fixture·한 실행)로 측정. **Shift+숫자 자체는 원본·v5 둘 다 무반응**(입력 전달 두 방식 모두 동일 결과, Ctrl+1·"1"은 같은 세션에서 정상 동작해 경로 검증됨) — 이 게임 번호-키 핸들러에 Shift 분기가 없는 것으로 판단(미지원, 회귀 아님, lap727의 ALT/Ctrl 같은종류선택과 같은 종류). **대안 메커니즘("1" 호출 → 마우스 Shift+클릭으로 선택에 추가 → Ctrl+1 재지정")은 원본·v5 둘 다 PASS**(+1 정확, 원본14→15/v5 40→41). **신규 발견(FAIL, 후보 v5 한정): 사망 후 그룹 호출 시 죽은 유닛 일부가 유령처럼 재선택됨** — 원본은 15명 중 3명 사망 후 호출에서 생존자 12명 정확(PASS), 후보 v5는 41명 중 10명 사망 후 호출에서 37명 선택(기대 31명), 죽은 10명 중 6명(앞 3명 전원+중간 3/4)이 유령 포함되고 나머지 4명만 정상 제외. 사망 처리 자체(`op10.dead_flag_after`)는 원본·v5 동일하게 성공, 사망 없는 상태의 그룹 호출도 정상(같은 실행에서 40명 정확 재현) — 결함은 "사망 후 호출" 경로에만 있음. R3(`SELECTION_BASE`, lap720~723)와는 별개 메모리 구조(`GROUP1_BASE_ADDRESS`/`unit+0x344`, lap724가 이미 정적 확인)이나 "20슬롯 한정 경로 vs 확장 경로"가 사망 필터링을 다르게 처리하는 것으로 추정(정적 미확인, 추측 표시). **(D)는 이 결함 때문에 미완료** — 마일스톤 경계라 `loop/ESCALATE_SOL` lap732 섹션에 올리고 임의로 v6를 만들지 않았다. 크래시 0(양쪽 실행 모두 완주), `source_unchanged` 2/2, `cleanup.prefix_processes_after=[]` 2/2. `make check` 결과는 상세 lap 참고. 상세 `docs/history/laps/20260928_lap732_work_g5_checklist_d_shift_add_death_recall.md`.
- [ ] **2026-09-28 lap733 work tier(Claude Code Sonnet, 정보 제공용 — 새 middle 검수 요청 아님, 2026-09-28 03:36 운영자 판정에 따라 middle은 체크리스트 전체가 채워진 뒤 한 번에 진행):** 09:05 지시를 수행. 보호 원본을 capstone/pefile로 직접 disasm — `FUN_00445E30`(recall) 레거시 20칸 루프는 `0x00416F40`(존재)+`FUN_0040F790(slot)==1`(`unit+0x31C` "selectable", H3 오버플로 스캔과 **동일 게이트**)로만 선택을 걸러내고, `FUN_00409C70`(사망)는 `+0x31C`를 건드리지 않으며 그룹 정리는 `FUN_00445A90(G, dword[unit+0x29C])` 1회(자기 그룹 20칸만, aux 포함 dword 정확 일치 검색)뿐이라 오버플로(`unit+0x344`만으로 존재하는 21~50번째 멤버)는 원래 그 검색 대상이 아님을 확인. lap732 자체 raw(`fixture_unit_group_snapshot`의 `handle=dword[unit+0x29C]`)로 "handle 드리프트" 가설은 반증. v2가 굽는 H1/H2/H3 실제 캐이브 바이트도 직접 disasm해 설계 문서와 일치·그 자체 결함 없음을 확인. **정확한 단일 근본원인(2단계 재배정 재정렬 vs 엔진 비동기 사망정리 타이밍)은 끝내 확정 못했으나, 원인 불문으로 안전한 수정을 구현**: 신규 `patches/selection/g5_selection_cap50_v6.py`(H4 훅, `0x00409CB8` 5바이트 콜사이트만 교체, 새 캐이브 `0x004E4F90..0x4E4FFA` 106바이트) — `FUN_00445A90` 호출 뒤 죽은 유닛 자신의 `unit+0x344`가 유효 그룹이면 **그 그룹 하나의 20칸만 slot(저word)만으로** 재검색해 지우고 `FUN_0040F750(slot,-1)`로 무조건 강제 클리어. v6는 v5 대비 정확히 이 훅 사이트+캐이브 두 구간만 다르고 나머지 전부 byte-identical(`test_only_the_h4_site_and_cave_differ_from_v5`로 고정, 신규 pytest 5개 전부 PASS). lap732와 동일 시나리오(41명 중 10명 사망)로 v6 재실행 → **`status=COMPLETE`, `structural_ok=true`, `death_recall_check.recall_ok=true`, 유령 0·생존31/31 정확**, `source_unchanged=true`, `cleanup.prefix_processes_after=[]`, 크래시 없이 완주. `make check` **1111 passed(776.51s)**(신규 v6 pytest 5개 포함), ruff/mypy/`CONTEXT_PASS` 전부 PASS, `checks/safety.sh check`: `SAFETY_PASS`. **(D) 체크리스트 전체 완료로 판단, 기준 후보 v5→v6 교체.** **미검증 위험(다음 work가 채워야 함): lap723~731이 확인한 드래그/이동/공격/정지·홀드·순찰/그룹저장로드 등 핵심 회귀를 v6로 직접 재실행하지 않았다** — byte-diff 스코프(H4 사이트/캐이브 외 무변경)에만 근거해 "회귀 없음"을 추론했을 뿐, 실측 재확인은 다음 work 권장 사항으로 남긴다. 다음 work: 여유가 되면 위 핵심 회귀를 v6로 1회 재확인 후 (E) UI → (F) 저장로드 → (G) 멀티 → (H) 장시간 순서로 진행. 근거 `../history/laps/20260928_lap733_work_g5_checklist_d_v6_death_recall_fix_pass.md`.
- [ ] **2026-09-28 lap738 work tier(Claude Code Sonnet, 정보 제공용 — 새 middle 검수 요청 아님,
  2026-09-28 03:36 운영자 판정에 따라 middle은 체크리스트 전체가 채워진 뒤 한 번에 진행):** (E) UI
  — 50기 선택 시 초상화/정보 패널 표시·클릭·스크롤, HUD 깨짐, 선택 표시(체력바) 확인을 수행,
  **PASS로 판단.** 신규 `tools/g5_ui_selection_hud_probe.py` — lap658/659가 "harness에 입력 경로
  없음"으로 SKIP 처리해 둔 항목에 실제 클릭·스크롤 입력을 추가했다. 원형 초상화 배지는 1기 선택 시
  실제 얼굴 렌더, 그룹(20/50) 선택 시 국가 문장/깃발 아이콘으로 전환(빈 화면이나 파손이 아니라
  원본·후보 동일한 대체 표시). 다이아몬드 슬롯(별도 위젯, 정확한 기능은 미상)은 클릭 시 깃발 커서
  아이콘이 뜨지만 `selection_unchanged_by_click/scroll=true` 원본·후보 둘 다(선택 count/slots
  불변), 스크롤(버튼4/5) 후에도 동일, 크래시 없음. 정보텍스트("체력/방어력")는 1기 선택시만 표시,
  그룹선택시 공백 — 원본·후보 동일(회귀 아님). HUD 새니티(F1-F11 행/명령그리드/다이아몬드 std)는
  전부 임계값 훨씬 위(파손된 빈 사각형 아님). **체력바**(그린 (0,188,0) 5-dot, radius=2 flood-fill
  — radius=1은 dot 사이 1px 간극으로 0을 오검출하는 버그를 이번 lap에서 직접 발견·수정):
  원본 20선택→**20/20(100%)**, 후보 50선택→**46/50(92%, 레거시 20캡을 명백히 초과해 하드캡 가설을
  반증)**, 동일밀도 부분선택 컨트롤(같은 fixture, 더 작은 드래그) 13선택→후보13/13·원본14/13(경계
  병합으로 인한 무해한 근소 과다계수) — 부분선택이 정확히 일치하므로 46/50 잔여 미표시분은 밀집
  나무/스프라이트 가림(lap726~728과 동일 부류 아티팩트)으로 설명되며, (A) 정적 표
  (`analysis/memory_maps/g5_selection_consumers_inventory_20260928.md`)의 UI/정보창 소비자
  (`0x498f*~0x4ae58c`) 전부 치환·잔여0 결론과도 일치한다. 크래시 0(원본1+후보1), `source_unchanged`
  2/2, `cleanup.prefix_processes_after=[]` 2/2. `make check` **1111 passed(803.95s)**,
  ruff/mypy/`CONTEXT_PASS` 전부 PASS, `checks/safety.sh check`: `SAFETY_PASS`(신규 pytest 0개,
  조사용 도구 1개만 추가, 제품 코드 무변경). **이로써 (E) 체크리스트 항목을 PASS로 판단한다.** 남은
  위험: 다이아몬드 슬롯의 정확한 기능은 UNKNOWN(선택/크래시에 영향 없어 판정에는 무관). 다음 work
  권장: (F) 저장/로드(50기 선택·부대 상태 저장 후 로드, 원본 세이브 호환 — Ctrl+숫자 자체는 lap724가
  이미 커버했으나 "50 선택 유지"를 명시 재확인). 끝나면 (G) 멀티 → (H) 장시간. 근거
  `../history/laps/20260928_lap738_work_g5_checklist_e_ui_portrait_hud_healthbar.md`.
- [ ] **2026-09-28 lap739 work tier(Claude Code Sonnet, 정보 제공용 — 새 middle 검수 요청 아님,
  2026-09-28 03:36 운영자 판정에 따라 middle은 체크리스트 전체가 채워진 뒤 한 번에 진행):** (F)
  저장/로드 — 50기 선택 상태 명시 재확인을 수행, **부분 FAIL 발견(마일스톤 경계, 승격).** 부대
  (Ctrl+숫자 그룹) 저장/로드는 lap724/734와 동일하게 재확인 PASS(checks 7/7). 그러나 **부대 지정
  없이 드래그로만 고른 raw 선택 자체는 후보 v6에서 저장→로드 시 항상 0으로 사라진다** — 원본은
  저장 시점 raw 선택(20)이 로드 후 그대로 복원됨을 직접 확인(로드 직전 라이브 값을 명시적으로
  0으로 디셀렉트해 뒀는데도 저장 당시 값으로 되돌아가 세이브 파일 자체가 raw 선택을 인코딩하는
  원본의 실제 기능임을 확증), 후보 v6는 저장 시점 50이었어도 로드 후 raw 선택이 항상 0(그룹1
  재호출 "1"로는 원본 20/후보 50 둘 다 정상 복원되므로 완전한 기능 손실은 아니고 우회로가 있음).
  **근본 원인 확정(정적):** `g5_selection_cap50_v1.py`가 레거시 선택 주소 `0x00899024`의 알려진
  읽기/쓰기 참조 10곳 전부를 새 `SELECTION_BASE`로 재배치해 레거시 주소를 완전히 방치한다 — 원본의
  세이브 직렬화가 그 주소를 그대로 디스크에 옮기는 방식이라면 v1~v6 전부에서 항상 0이 기록되는
  것이 관측과 일치. **원본 세이브 호환(별개 질문)은 PASS**: 완전 무패치 원본 실행 파일이 후보
  v6가 만든 세이브 파일을 자신의 저장 디렉터리에 주입받아 크래시 없이 정상 로드(`PASS_CROSSLOAD_
  NO_CRASH`), 로드 후 그룹1 스냅샷(`group1_count=20, group1_first_id=132270`)이 후보 자신의 로드
  결과와 완전히 일치해 레거시 20슬롯 데이터의 바이트 호환성도 교차 확인됨 — 세이브 "형식"은 깨지지
  않았다. 크래시 0(3/3), `source_unchanged` 3/3(두 소스 경로 모두), `make check` **1111
  passed(858.42s)**, ruff/mypy/`CONTEXT_PASS` 전부 PASS, `checks/safety.sh check`: `SAFETY_PASS`
  (신규 pytest 0개, 진단 드라이버는 `/tmp`에만 존재, 제품 코드 무변경). 이 결함은 R3/(D)
  사망-후-호출보다 범위가 넓다(원본은 0~20 전체가 세이브에서 살아남는데 후보는 0~50 전체가
  죽는다)는 점에서 마일스톤 경계라 v7을 임의로 만들지 않고 `loop/ESCALATE_SOL`에 lap739 섹션을
  추가했다. 상세
  `../history/laps/20260928_lap739_work_g5_checklist_f_saveload_selection_regression.md`.
- [ ] **2026-09-28 lap740 work tier(Claude Code Sonnet, 정보 제공용 — 새 middle 검수 요청 아님,
  2026-09-28 03:36 운영자 판정에 따라 middle은 체크리스트 전체가 채워진 뒤 한 번에 진행):** 14:05
  지시(v7, 구현 우선)를 수행. 신규 `patches/selection/g5_selection_cap50_v7.py`(v6 위에 저장/로드
  두 call-site만 훅, `.rsrc` 자신의 0-padding 128B 사용, 세이브 바이트 배치 무변경) — 저장 직전
  라이브 선택(≤20)을 레거시 `0x00899024`/`0x00899028`에 미러링, 로드 직후 역미러링. raw 50 선택 →
  저장 → 명시 디셀렉트(0) → 로드 → **count=20, slots가 원본 paired 결과와 완전 일치**
  (`[1198,1195,1194,...,1177]`). 그룹 저장/로드 재확인 **PASS**(7/7, 회귀 없음). 세이브 호환
  **양방향 PASS**: 원본이 v7 세이브를 크래시 없이 로드하고 레거시 영역 자체로 동일 20-슬롯을
  읽어내며, v7이 원본 세이브를 크래시 없이 로드하고 `SELECTION_BASE`가 동일 20-슬롯으로 정확히
  복원됨(운영자가 요구한 역방향 호환). entries 21~50은 명시적으로 미보존(원본과 동일 상한, 확장은
  세이브 스트림 끝 trailing block으로만 가능해 이번 lap은 시도 안 함). 정적 회귀 증명: v7·v6 바이트
  차이가 두 call-site(5B×2)+`.rsrc` 헤더+cave로만 한정됨을 신규 pytest로 고정. 크래시 0(4/4),
  `source_unchanged` 4/4, `make check` **1116 passed(808.52s)**, ruff/mypy/`CONTEXT_PASS` 전부
  PASS, `checks/safety.sh check`: `SAFETY_PASS`(신규 pytest 5개, 진단 드라이버는 `/tmp`에만 존재,
  제품 코드 무변경). 상세
  `../history/laps/20260928_lap740_work_g5_checklist_f_v7_saveload_selection_shadow_fix.md`.
- [ ] **2026-09-28 lap741 work tier(Claude Code Sonnet, 정보 제공용 — 새 middle 검수 요청 아님,
  2026-09-28 03:36 운영자 판정에 따라 middle은 체크리스트 전체가 채워진 뒤 한 번에 진행):** (G)
  멀티를 수행, **BLOCKED(env)로 완료 판정.** G2 S4 전송 트랙(`G2_STRATEGY_W48_DISPOSITION_LAP580.md`,
  N211)이 이미 정적으로 확인한 사실 — 이 환경의 Wine 9.0 `dpwsockx.dll`(DirectPlay Winsock SP)은
  `DPWSCB_*` 콜백 15개 중 GetCaps 하나만 구현되고 나머지 14개(EnumSessions/Open/Send/SendEx 등)가
  FIXME stub — 를 이번 lap이 현재 환경에서 직접 재해시해 재확인했다: 시스템 패키지
  `/usr/lib/i386-linux-gnu/wine/i386-windows/dpwsockx.dll`과 세 개의 서로 다른 wine prefix
  (`~/.wine`, `~/.wine_test`, `~/.wine_syw2_359`)의 syswow64 사본(이 32비트 게임이 실제로 로드하는
  경로) 전부가 N211이 기록한 SHA256 `3b4f6a9d355114fb78f1e2a3961f48324b654c7e246a1bcd0925f3cdbe7986c9`와
  완전 일치했다. 환경 동일성이 실측으로 확정됐으므로, G2가 이미 raw로 관측한 증상(host가
  `방만들기` 뒤 진행 못함, client가 세션 목록을 못 얻음)이 G5에서도 그대로 재현될 것이 기대되며
  **같은 EXE·같은 DirectPlay 로비 코드 경로이므로 새 2-인스턴스 실행을 하지 않았다**(PROMPT③ "같은
  추측 반복 금지", 신규 정보 없이 실패를 재현하는 실행 예산 낭비 방지). 판정은 `NOT_FEASIBLE`(제품에
  멀티 기능 자체가 없다는 뜻)이 아니라 `BLOCKED(env: wine9.0 dpwsockx stub)`이며, 다른 Wine
  버전/네이티브 DirectPlay 런타임/실제 Windows 호스트라면 다를 수 있으나 새 의존성이라 사용자 승인이
  필요하다(G2 lap580 §3의 대안 (i)~(iii)과 동일 성격, 이번 lap은 그 판단을 대신하지 않는다).
  **대안(체크리스트가 요구한 정적 패킷 대조)은 완료:** `analysis/memory_maps/g5_selection_consumers_inventory_20260928.md`가
  이미 확정한 대로 실제 유닛 명령 발행은 단일 호출부 `0x41F0A4`뿐이고, `patches/selection/g5_selection_cap50_v4.py:215`가
  문서화한 `"record_format": "unchanged; 60-byte record, 20-word unit-list, issued up to 3 times per order"`가
  기준 후보 v7까지 재정의 없이 그대로 이어짐을 이번 lap이 import 그래프로 신규 확인했다(v6는
  `g5_selection_cap50_v5`를, v7은 `g5_selection_cap50_v6`를 import하고 둘 다 청크 로직을 건드리지
  않는 별도 훅만 추가). 즉 원본과 동일한 레코드 포맷을 유지한 채 50기 주문당 최대 3배(⌈50/20⌉)만
  발행하도록 이미 확정돼 있다 — 다만 이 호출이 실제 DirectPlay Send로 직렬화되는 정확한 지점은
  전송계층이 BLOCKED라 와이어로 관측할 수 없어 **PLAUSIBLE(정적 구조 근거)로만 표시, CONFIRMED
  아님**. 멀티는 여전히 라이브 `UNKNOWN`이지만 (G) 항목 자체의 "불가 시 사유 명시" 완료 조건은
  충족했다고 판단한다. 제품 코드/EXE 0 변경, 게임 실행 0회(재사용 근거만). `make check`는 문서
  갱신 안전 확인용으로 1회 실행했다(결과는 상세 lap 참고). 다음 work: (H) 장시간(50기 반복 명령
  수천 tick 안정성, 단일플레이 격리 실행). 근거
  `../history/laps/20260928_lap741_work_g5_checklist_g_multiplayer_env_blocked.md`.
  - [x] 처리(lap741 work, 같은 lap 안 계속): 위 (G) BLOCKED 판정 직후 이 지시를 이어서 수행했다.
    `[ESL]Syw2plus/`의 네이티브 DLL 6개 전부 실측 확인, `Syw2plus/IPXWrapper+v0.6.0.7z`를 `/tmp`에서
    열람해 레지스트리 베이스(`Software\IPXWrapper`)와 인터페이스별 `enabled`/`primary`/`port` 값,
    이 0.6.0 버전엔 정적 peer 목록 기능이 없고 브로드캐스트/VPN 가상어댑터에 의존함을 확인. 신규
    `/tmp/lap741_ipx_native_smoke_driver.py`(`runtime_env.prepare()`+`_xvfb()` 재사용)로 단일
    인스턴스 부팅 스모크 — `IPXConfigWIN32.reg` 임포트 성공, `WINEDLLOVERRIDES="ddraw=b;dpwsockx,
    wsock32,mswsock,ipxwrapper=n,b"`(첫 시도는 세미콜론 누락으로 문법 오류 — 가설 실패 1/2, 수정해
    재시도)로 크래시 없이 12초 생존. 그러나 네이티브 `dpwsockx.dll`/`ipxwrapper.dll`은 멀티 로비
    진입 시에만 지연 초기화돼 단순 부팅으로는 활성화를 확인할 수 없었다(`ipxwrapper.log`가 배포
    당시 원본 PC의 과거 로그 그대로 무변화 — Realtek NIC·Radmin VPN 등 이 샌드박스와 무관한 구성).
    실제 2인스턴스 세션 성립을 확인하려면 메인 메뉴→멀티 모드 선택(`tools/runtime_env.py`의
    `G1_SETUP_POINTS`/`_g1_selector_flow`로 여기까진 재사용 가능)→DirectPlay 공급자 목록 화면까지
    UI 자동화가 더 필요한데, 그 화면의 클릭 경로는 G2 lap577~580이 `/tmp`에서만 만들어 저장소에
    보존되지 않았다 — 새로 구축하는 것은 그 자체로 별도 작업 규모(G2가 4개 lap을 썼다)라 이번 lap
    예산(가설 2회 한도) 안에서 만들지 못했다. **(G)를 `FEASIBLE`도 `BLOCKED`도 아닌 INCONCLUSIVE로
    정직하게 유지한다** — Wine-stub 경로의 `BLOCKED(env)` 판정 자체는 바뀌지 않지만, 네이티브
    override 경로는 "시도했으나 결론 못 냄"이 정확한 상태다. 크래시 0, 제품 코드 0 변경, 격리
    사본(810MB)은 스모크 종료 직후 삭제(디스크 위생). `make check` **1116 passed(793.43s)**,
    ruff/mypy/`CONTEXT_PASS`/`SAFETY_PASS` 전부 PASS. **다음 판단 필요(middle/운영자):** (가) 위
    UI 자동화를 새로 구축해 네이티브 override 재시도를 완결, 또는 (나) Wine-stub BLOCKED+정적
    패킷 대조(완료됨)를 (G)의 최종 답으로 수용하고 (H) 장시간으로 진행. 근거
    `../history/laps/20260928_lap741_work_g5_checklist_g_multiplayer_env_blocked.md`.
- [ ] **2026-09-28 lap742 work tier(Claude Code Sonnet, 같은 세션, 15:55 지시 ①②를 이어서 수행,
  정보 제공용 — middle 검수 요청 아님):** `WINEDEBUG="+seh,+loaddll"`(기존 `-all` 대신)로 크래시를
  재현해 로그를 그대로 보존했다. **근본 원인을 확정**: `0118:err:dplay:
  IDirectPlay4Impl_InitializeConnection Unable to load service provider {44eaa760-cb68-11cf-9c4e-
  00a0c905425e}`(Internet TCP/IP 표준 GUID)와 `{0f1d6860-88d9-11cf-9c4e-00a0c905425e}`(IPX 표준
  GUID) **둘 다** 로드 실패 → `err:dplay:DirectPlayCreate Failed to Initialize SP:
  DPERR_UNAVAILABLE` → 게임 자신의 실패 경로 버그로 **`Unhandled page fault on read access to
  00000000`**(널 포인터 역참조, "방만들기" 직후). 즉 크래시는 `dpwsockx.dll` 내부가 아니라 **Wine
  builtin `dplayx.dll`이 (native든 builtin이든 관계없이) 등록된 서비스 공급자 DLL을 LoadLibrary하지
  못해 DirectPlay 객체 생성 자체가 실패**하고, 게임이 그 실패를 널체크 없이 사용하는 조합이다.
  ② 조합 실험 1건 추가 수행: `dpwsockx=b`(Wine 빌트인 스텁 유지)+`wsock32,mswsock,ipxwrapper=n,b`
  (나머지만 native) → **크래시 없음**, 기존 builtin-stub 패턴(PS7 복귀)과 동일 — **크래시는
  `dpwsockx`를 native로 바꿀 때만** 발생함을 격리 확인(dplayx가 로드하는 대상이 바로 registry
  `Path=dpwsockx.dll`이기 때문, 원인과 정확히 부합). **③(ipxconfig.exe UDP/인터페이스 설정)은
  실행하지 않았다** — 실패가 DLL 로드 단계(어떤 네트워크 I/O도 시작되기 전)에서 이미 확정되므로
  ipxconfig 설정은 이 실패 경로에 영향을 줄 수 없다고 판단(이유를 기록하고 실행 생략, PROMPT③
  "같은 추측 반복 금지"에 준함). `dplayx.dll`은 이 배포물에 native 대체본이 없어(게임 폴더에
  `dplayx.dll` 파일 자체가 없음) "dplayx만 native로" 조합은 새 의존성 도입 없이는 시도 불가.
  **결론: (G) `BLOCKED(env: native ipxwrapper crashes on room creation, wine9.0)` 판정 유지·강화**
  — Wine의 builtin DirectPlay COM 계층이 이 배포물의 네이티브 서비스 공급자 DLL을 구조적으로 로드하지
  못하는 것이 원인이며, `WINEDLLOVERRIDES` 조합 조정으로 우회할 수 있는 문제가 아니다(둘 중 하나:
  네이티브 SP DLL을 쓰면 로드 자체가 실패해 크래시, builtin SP DLL을 쓰면 로드는 되지만 콜백이
  전부 stub이라 기능이 없음). `make check` **1116 passed(814.81s)**, ruff/mypy/`CONTEXT_PASS`/
  `SAFETY_PASS` 전부 PASS. 제품 코드/EXE 0 변경. 근거
  `docs/history/laps/20260928_lap742_work_g5_checklist_g_multiplayer_ipx_crash_blocked.md`
  (백트레이스 로그·조합실험 raw는 `temp/Syw2plus_patch/g5_multiplayer_lobby/
  20260928_lap742_crash_backtrace/`, `20260928_lap742_combo_dpwsockx_builtin/`).
  **다음 판단 필요(middle/운영자):** 이 판정을 (G)의 최종 답으로 수용하고 (H) 장시간으로 넘어갈지
  확인.
- [ ] **2026-09-28 lap743 work tier(Claude Code Sonnet, 같은 세션, 16:35 지시 수행, 정보 제공용 —
  middle 검수 요청 아님):** ① **(H) 장시간**: 신규 `tools/g5_long_run_stability_probe.py`(기존
  G5 probe 헬퍼 재사용, 제품 코드 0 변경)로 v7 후보 50기 드래그 선택 → 이동(A)/정지/이동(B)/보류/
  순찰/정지 6단 명령을 13회 주기 반복 → **8019 tick(목표 8000 초과, 약 401초) 동안
  `crash_detected=false`, `selection_regressions=0`**(387개 샘플 전부 `selection_count=50`·
  `selection_unique=50`), 최종 선택 slots가 초기 선택과 완전히 동일한 순서로 보존, 매 샘플
  `moving_count=50`(브로드캐스트 경로가 수천 tick 뒤에도 50기 전원에 작동). 후보 EXE SHA
  `30efafa067b6cb524bd68594dedee4d0d4c68e1efef348e2f16c211dc8229bef`가 lap740 기록 v7 SHA와
  완전 일치(빌드 재현성). **(H) PASS.** ② **(G) 마지막 1회 시도**: lap742의
  `WINEDEBUG=+seh,+loaddll` 로그를 재검토해 lap742가 명시하지 않은 사실을 발견 — 네이티브
  `dpwsockx.dll`이 게임 폴더에서 성공적으로 로드된 직후, `dplayx.dll`(Wine builtin) 자신의 내부
  `LoadLibrary("dpwsockx.dll")` 호출은 `C:\windows\system32\dpwsockx.dll` 경로로 재해석되어
  Wine의 **builtin stub**을 찾아 로드한다(같은 실행, 같은 파일명, 다른 로딩 결과) — 네이티브
  override DLL이 게임 폴더에만 있고 실제 `<prefix>/drive_c/windows/system32/`에는 없기 때문이라는
  가설을 세워, 신규 `/tmp/lap743_g_final_attempt_driver.py`(저장소 밖, 기존 헬퍼 재사용)로 네
  DLL을 system32에도 실제 배치한 뒤 2개 override 조합(`n,b` 폴백형/`n` 강제형)으로 재시도 —
  **2/2 모두 PS9 메인메뉴 도달 전에 크래시 로그조차 없이 조기 종료**(lap742의 "PS13까지 도달 후
  방만들기에서만 크래시"보다 더 이른 실패). 가설 반증, lap742와 합쳐 누적 **4개 조합 실험 전부
  실패**. `ipxconfig.exe`는 CLI 옵션이 없는 GUI 전용 도구임을 `strings`로 확인했고, 크래시가
  인터페이스 설정보다 먼저인 SP 로드 단계에서 일어나 이 경로에 영향을 줄 수 없다고 판단해 착수하지
  않았다(PROMPT③ 반복 추측 금지, 사유 기록). (나) 정적 대조(명령 레코드 60바이트/20-word 불변,
  청크 최대 3회)는 lap741이 이미 완료(재인용, 신규 조사 아님). **(G) `BLOCKED(env: native
  ipxwrapper crashes on room creation, wine9.0)` 최종 확정.** 크래시 0(제품 EXE 기준; 관측된
  조기종료는 환경 반응이며 회귀 아님), `source_unchanged` 3/3(H 1회 + G 조합 2회), `game` 사본
  (H 810MB + G 각 581MB) 실행 직후 삭제(output/manifest/prefix 보존, 디스크 위생 준수).
  `make check` **1116 passed(862.74s)**, ruff/mypy/`CONTEXT_PASS`/`SAFETY_PASS` 전부 PASS(신규
  pytest 0개, H용 진단 도구 1개만 저장소에 추가). **이로써 G5 체크리스트 A~H 전부 채워졌다.**
  근거 `docs/history/laps/20260928_lap743_work_g5_checklist_h_long_run_stability_pass.md`,
  `docs/history/laps/20260928_lap743_work_g5_checklist_g_final_attempt_blocked_confirmed.md`.
  **다음: middle(Opus5/Sol)이 A~H 전체를 한 번에 독립 재검수하고(2026-09-28 03:36 판정대로), 통과
  시 G5 milestone을 사용자에게 재상정(멀티는 `BLOCKED`로 명시), 이후 G1 착수.**
