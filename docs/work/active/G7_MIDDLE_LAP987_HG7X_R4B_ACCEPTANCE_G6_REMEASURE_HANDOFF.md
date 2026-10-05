# G7 middle 검수 — lap986 H-G7x/R4b 수용(PASS partial, 기술) → 다음 work H-G6r(G6 재측정 on cand67 R4b + fixed_start 런타임 1회) handoff (lap987)

- 작성: 2026-10-05, lap987 middle(Claude Code `claude-opus-5-5`, high). 게임 실행·source 변경·commit 0.
- 입력: `loop/ESCALATE_SOL`(lap986 work), 기록 `docs/history/laps/20261005_lap986_work_g7_cross_load_r4b_hg7x.md`, 이전 카드 `G7_MIDDLE_LAP985_HG7R_ACCEPTANCE_CROSS_LOAD_HANDOFF.md` §3·§4.
- 이번 lap 산출물(공유 temp, 직접 생성): `temp/Syw2plus_patch/20261005_lap987_middle_review/`
  - `recalc_lap987.py`(SHA256 `10c1b0bd5c2752c7578538a2eab363473cc4e133ec75590494a9c1f6ccfba2ba`) → `recalc_lap987.json`(`6b1a99a39ca75228574e97bcad29524f17b4c62dbd0f48591c6a6a3594f8a9f3`)
- EXE: 이식판 normal `0e28ef57…d257`·fixed_start `703deaf4…6ea0` — 이번 lap 직접 sha256 MATCH.

## §1 독립 재계산 (제품 helper 미사용; G6+G7 조립에서만 lap978 수용된 G6 module을 base로 사용)

probe-result 10개 SHA256 앞 16자 기록과 **전부 일치**. 각 단계 `table_hex`(VA `0x632C9C`, 740 B)에서 ids·own id 첫 일치·표 SHA를 직접 풀고, 세이브 fixture S2(`1c5acd27…`)·S0(`51c7e3e7…`) SHA를 재확인했다 → 기록 대비 **불일치 0**(ids·first_match·table SHA·save SHA·private EXE SHA·step verdict).

| run (EXE) | 단계 | 재계산 | 판정 |
|---|---|---|---|
| c67_x3 (R4 `2de1944e`) | 자리 2 게임 중 인게임 S0 | 로드 직후 local **2**, 30초 ps `[3,27,29]`·locals `[0,2]`·선택 0, 캡처 "패배했습니다." | X-3 FAIL(R4 결함 증거) |
| port_x3 (`0e28ef57`) | 같음 | 표 = 로드 전 표(byte 동일, 로드가 표를 안 건드림)·local 2·ps `[3,27,29]` | 원본계 결함 재현 |
| c67_x4 / r4b_x4 | 1P 게임 중 인게임 S2 | local 0→**2**·표 앞 0x170 = S2 스냅샷·ps `[3]`·owner 2 | X-4 PASS(둘 다) |
| port_x4 | 같음 | local 0·ps `[3,27,29]`·선택 0 | 원본계 결함 재현 |
| cand67_x12 (R4) / r4b_x12 | 자리 2 → 타이틀 복귀 → title S2, 다시 복귀 → title S0 | 타이틀 복귀 직후 local **0**(표 ids `[1,1,0,…]` 그대로) → S2 local 2·owner 2, S0 local 0·owner 0, ps `[3]` | X-1·X-2 PASS(둘 다) |
| **r4b_x3** (R4b `fb7c2131`) | 자리 2 게임 중 인게임 S0 | 로드 전 local 2 → 로드 뒤 **local 0**·ids `[1]*8`(= S0 스냅샷)·ps `[3]`·locals `[0]`·owner 0, 캡처 인게임 | **X-3 PASS** |
| r4b_r1 | 새 프로세스 타이틀 S2 | local 0→2·first_match 2·ps `[3]`·owner 2 | R-1 PASS |
| r4b_r3 | 새 프로세스 타이틀 S0 | local 0·ps `[3]`·owner 0 | R-3 PASS |

- R4b 실행(r4b_*)의 로드 직후 표 앞 0x170 B는 모두 해당 세이브 파일 안에 1곳 존재(스냅샷 복원 확인).
- 모든 단계 solo flag 1·own id 0, 10 run 모두 game 사본 제거·prefix 프로세스 0. port_x12는 status FAIL(`pause_for_exit timeout`, ps 29 패배 화면) — 기록과 같고 lap982 D에서 이미 기록된 결함이라 증거로 쓰지 않는다.
- 타이틀 복귀 local 0 해석: 복귀 직후 표 ids `[1,1,0,…]`·own 0이면 `0x43AF40`은 2를 주므로 0은 직접 쓰기다. 정적으로 `[0xB63FC4]` 직접 쓰기는 `0x41CA85`(=`0x41CA80` 안)뿐(lap976) → 타이틀 복귀가 `0x41CA80` 경로를 탄다는 lap986 해석과 일치(어느 호출자인지는 UNKNOWN, 비차단).
- 관찰(비차단): R4 c67_x3·port_x4의 "loaded" 표본 표는 로드 전 표도 세이브 스냅샷도 아니다(ids `[0,0,0,1,…]`·`[0,1,1,…]`). 둘 다 local과 유닛 owner가 어긋나 패배 처리로 가는 run이라, 표본 시점에 게임이 표를 이미 고쳐 쓴 것으로 본다(writer UNKNOWN). R4b run에는 해당 없음.

## §2 R4b 후보 바이트 독립 재조립

- lap985 카드 §3 설명(R4 레이아웃 + `rep movsd` 뒤·`push` 앞 `mov dword [0xB63FC4],0` 10 B)으로 직접 조립: cave 66 B, `jne rel8 0x29`(→`popfd` `0x18A7D35`), call offset 45(`call 0x43AF40`), jmp offset 61(`jmp 0x441316`).
- SHA 4개 **기록과 일치**: G7 normal `a75aa129…e08b`·fixed `7edcc078…6dfbb`, G6+G7 normal `fb7c2131…c56a`·fixed `58b9b22a…f078`. run의 private EXE SHA도 R4b run = `fb7c2131…`, R4 run = `2de1944e…`.
- diff 59 B(hook 6 + cave 66 범위 안, 원래 0과 같은 바이트 제외), file `267024`~`1084737`, 범위 밖 0. 제품 module의 `_cave_bytes()`/`_hook_bytes()`도 독립 조립과 byte 동일(보조 확인).
- capstone: `pushal; pushfd; cmp word [0x4ed848],1; jne 0x18a7d35; mov esi,0x632f7c; mov edi,0x632c9c; mov ecx,0x5c; cld; rep movsd; mov dword [0xb63fc4],0; push 0xb63fc4; call 0x43af40; add esp,4; popfd; popal; mov ebp,[0xb3af2c]; jmp 0x441316`. 레지스터·플래그·esp 균형 보존, 솔로 게이트 밖(멀티) 무접촉은 R4와 같다.
- 의미: 솔로 로드 뒤 local = "스냅샷 표에서 own id 첫 일치, 없으면 0". 솔로 기본 local은 0(혼자하기 초기화 `0x4B6355`·부팅값·타이틀 복귀 `0x41CA85`)이므로 1P 세이브 동작과 같다.

**판정: H-G7x PASS(partial, 기술) 수용 — R4b(cand67 `fb7c2131…`)를 G7 현행 후보로 채택, R4(`2de1944e…`)는 X-3 결함으로 대체.** DESIGN G7 사용자 합격 아님.

## §3 남은 위험 / 미검증

- G6 기능을 R4b cand67에서 아직 재측정하지 않았다(lap979 G6 수용은 G6 단독 후보 `b50af2a6…` 기준).
- fixed_start 후보(`58b9b22a…`/`7edcc078…`)는 바이트·SHA만 확인, 런타임 0회.
- 자리 2 한 곳·own id 0만, 멀티 `[0x4ED848]` 경로 UNKNOWN(게이트 밖 무접촉), 사용자 ↑/↓ 경로 런타임 동일성 UNKNOWN(lap985 §5: 메커니즘 비차단, 사용자 합격 요청에서 최종 확인).
- 새 관찰: 타이틀 도움말 화면에 "▲▼ : 방장만, 자리 변경"이 표시된다(r4b_x12 `x0_title_return.png`). 사용자 답(↑/↓로 자리 이동)과 일치하며 방장 전용 기능이다. 격리 키 전달 BLOCKED(lap981, 채팅 EDIT 포커스)는 그대로이고 APPROVALS lap981 질문은 열린 채 둔다.

## §4 다음 work H-G6r — G6 재측정 on cand67(R4b) + fixed_start 런타임 1회 (사전등록, 1 work lap)

목표: 최종 스택 후보에서 G6가 lap979 수준으로 유지되는지, fixed_start 스택이 실제로 돈다는 런타임 근거를 얻는다. 둘 다 끝나면 사용자 합격 요청 범위를 정할 수 있다.

하네스(기존 경로 불변, 회귀 테스트 RED→GREEN):
- `tools/g6_shift_click_probe.py`: variant `cand67` 추가 = port + G6 + G7(`g7_title_load_seat_restore.build_candidate(g6 candidate)`), LAYOUTS는 `cand`와 동일. build report·private EXE SHA 기록.
- `tools/g7_save_load_probe.py`: `--port {normal,fixed_start}`(기본 normal, SHA 가드 = `g6_patch.PORT_SHA256[...]`, 입력 경로는 `260921_temp`의 `…_시작자리고정_G2_개인500_공용4092_G5_선택50_시험용.exe`). 기존 normal 동작·결과 schema 불변.

측정(격리 사본·prefix·Xvfb, lobby-snapshot seat):
- **G6r-A**: g6 probe `--variant cand67 --seat 2 --seat-method lobby-snapshot` → private EXE `fb7c2131…`, G6-1 Shift+클릭 누적 `[1,2,3,4,5,6]`, G6-2 Shift+드래그 추가·G6-3 Shift+클릭 해제·G6-4 50 상한 거부 PASS, local 2 유지·ps `[3]`. (lap979 cand 결과와 같은 표 형식으로 비교)
- **G6r-B**: 같은 probe `--seat 0`(1P 대조) → G6-1 `[1..6]`·G6-2~4 PASS(1P 회귀 0).
- **F-1**: g7 probe `--port fixed_start --variant cand67 --seat 2`(observe: 시작→일시정지 저장→인게임 로드→새 프로세스 타이틀 로드) → private EXE `58b9b22a…`, C·D local 2·ps `[3]`·드래그 선택 owner 2, 크래시 0, G5SC sidecar 정상.
- 안전: 크래시 0, game 사본 정리, prefix 프로세스 0, 입력/후보 SHA 기록.

분기:
- 전부 PASS → H-G6r PASS(partial). 다음 middle이 독립 재계산 후 **사용자 합격 요청 범위 확정**(마일스톤 경계: cand67 normal/fixed_start EXE 경로·SHA, 사용자 확인 절차 = 대기실 ↑/↓ 자리 이동 → Shift+클릭/드래그 추가 → 저장 → 게임 재시작 → 타이틀 불러오기 → 1P 세이브 대조).
- G6r-A/B가 lap979 대비 회귀 → G7 cave와의 상호작용은 로드 경로에만 있어 예상 밖이다. 빌드 SHA·LAYOUTS부터 추적·수리 후 재실행(③ 반복 원칙). 3회 안에 설명 불가면 ESCALATE_SOL.
- F-1 실패 → fixed_start 입력 SHA·시작자리고정이 lobby-snapshot 자리와 충돌하는지(시작 위치 고정 ≠ 로비 자리 index) 기록하고 원인 추적. 자리 생성 자체가 fixed_start에서 불가하면 BLOCKED로 기록하고 seat 0 observe 1회로 스택 생존만 확인.
- G6 on fixed_start는 이번 범위 밖(시간이 남으면 G6r-A와 같은 명령 1회, 안 하면 SKIP으로 기록).
