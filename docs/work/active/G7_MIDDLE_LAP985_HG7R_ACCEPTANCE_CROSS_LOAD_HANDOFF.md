# G7 middle 검수 — lap984 H-G7r 수용(PASS partial, 기술) → 다음 work H-G7x(같은 프로세스·교차 로드 매트릭스) handoff (lap985)

- 작성: 2026-10-05, lap985 middle(Claude Code `claude-opus-5-5`, high). 게임 실행·source 변경·commit 0.
- 입력: `loop/ESCALATE_SOL`(lap984 work), 기록 `docs/history/laps/20261005_lap984_work_g7_title_load_seat_restore_hg7r.md`, 이전 카드 `G7_MIDDLE_LAP983_HG7O_ACCEPTANCE_SNAPSHOT_RESTORE_HANDOFF.md` §4.
- 이번 lap 산출물(공유 temp, 직접 생성): `temp/Syw2plus_patch/20261005_lap985_middle_review/`
  - `recalc_lap985.py`(SHA256 `69a9381e6a4591e262af1b69dfd86480c13e1205e5c6eb346bb568b24958bbac`) → `recalc_lap985.json`(`efc7959ae99cff3a268e5ad3c1778afffcc84ed687a5102466e00a5072d54141`)
  - `callers.py`(E8/E9 호출자 스캔)
- EXE: 이식판 normal `0e28ef57…d257`·fixed_start `703deaf4…6ea0` — 이번 lap 직접 sha256 MATCH.

## §1 독립 재계산 (제품 helper 미사용; G6+G7 확인에서만 lap978 수용된 G6 build를 base로 사용)

probe-result 4개 SHA256 앞 16자 기록과 일치(cand_s2 `8b1f6f87`·cand_s0 `7d77d0c6`·cand_oldsave `148e05e6`·cand67_s2 `44a66cee`).
각 stage `table_hex`(VA `0x632C9C`, 740 B)에서 ids `0x632CA0[0..7]`·행 `0x632CC0+6i`를 직접 풀고 `0x43AF40` 규칙(own id 첫 일치)으로 재계산 → 기록과 **불일치 0**(ids·first_match·table SHA·save SHA·private EXE SHA).

| run | 결과(재계산) | 판정 |
|---|---|---|
| cand_s2 | D 로드 전 local 0·ids 0 → 로드 뒤 **local 2**·ids `[1,1,0,…]`·첫 일치 2·행1/2 상태 5, 30초 ps `[3]`·locals `[2]`·선택 1개 owner 2. C(인게임) 동일 | **R-1·R-2 PASS** |
| cand_s0 | 표 `[1]*8`·own 0 → 첫 일치 없음 → local 불변 0, ps `[3]`·선택 owner 0 | **R-3 PASS**(아래 §3 주의) |
| cand_oldsave | 입력 save SHA `7e92e474…` 일치, 로드 뒤 local 2·ids `[1,1,0,…]`·ps `[3]`·owner 2 | **R-4 PASS** |
| cand67_s2 | C·D 모두 local 2·ps `[3]`·owner 2 | 스택 PASS(G6 동작은 미측정) |

- D 로드 뒤 live 표 앞 0x170 B = A 시작 표 = save 파일 offset 1,827,770의 스냅샷(세 run 모두 1곳). cand_oldsave도 같은 offset에서 일치.
  740 B 덤프 중 0x170 뒤(`0x632E0C~`, 로비 갱신 `0x4B7700`의 복사 원본 영역) 73 B는 A와 D가 다르다 — 스냅샷 범위 밖, 새 프로세스가 대기실을 거치지 않은 결과로 보이며 30초 ps `[3]`에 영향 없음(관찰 기록).
- 모든 stage solo flag `[0x4ED848]`=1, own id `[0xC0D11C]`=0(프로세스 4개 추가, 누적 9개).
- 캡처 대조: cand_s2 `d_watch_end.png` = 인게임 자기 마을·유닛, lap982 port `d_watch_end.png` = "패배했습니다." 결과 화면.

## §2 후보 바이트 독립 재조립

- 카드 lap983 §4 레이아웃으로 직접 조립(hook `E9 EB 69 46 01 90`, cave 56 B; call rel `0xFEB93218`→`0x43AF40`, jmp rel `0xFEB995DE`→`0x441316`)한 normal/fixed_start 후보 SHA = 기록 `1a209807…`·`5c79833d…` **일치**. 각 diff 54 B(전부 hook 6 B·cave 56 B 범위 안, 기존 값과 같은 바이트는 제외), 범위 file `267024`~`1084727`.
- G6 후보(normal `b50af2a6…`, fixed `7c891658…`) 위 같은 조립 = `2de1944e…`·`8b390817…` **일치**. private EXE SHA(run별)도 일치.
- capstone: `pushal; pushfd; cmp word [0x4ed848],1; jne +0x1f(→popfd); mov esi,0x632f7c; mov edi,0x632c9c; mov ecx,0x5c; cld; rep movsd; push 0xb63fc4; call 0x43af40; add esp,4; popfd; popal; mov ebp,[0xb3af2c]; jmp 0x441316`. 레지스터·플래그(DF 포함)·esp 균형 보존.
- hook 위치 문맥: `0x44130A push esi; call 0x10910D0`(fclose→G5SC 체인) 직후, 원래 `0x441316 add esp,4` 전. sidecar 로드가 cave보다 먼저 끝난다.
- 이식판 전 실행 섹션에서 `0x441311..0x441315`로 들어오는 rel8/rel32/jcc32 분기·abs32 참조 **0** → 5+1 바이트 hook 안전.
- 코드 검수: 입력 SHA 가드·G6 strip 재빌드 일치 검사·cave 0 영역 검사·rollback byte-exact·덮어쓰기 거부가 있고 테스트 15개가 이를 덮는다. 차단 결함 없음.

**판정: H-G7r PASS(partial, 기술) 수용.** DESIGN G7 사용자 합격 아님.

## §3 새 위험 — 첫 일치가 없으면 local이 이전 값으로 남는다

- `0x43AF40`은 첫 일치가 없으면 out(`[0xB63FC4]`)을 바꾸지 않는다(lap983). 1P 솔로 표는 ids `[1]*8`·own 0이라 **항상 일치 없음** → cand_s0의 local 0은 cave가 정한 값이 아니라 새 프로세스 부팅값 0이다.
- 따라서 local이 이미 0이 아닌 상태에서 1P 세이브를 로드하면 local이 그대로 남는다:
  - **인게임 교차 로드**: 자리 2 게임 중 인게임 불러오기로 1P 세이브 → local 2 유지 예상(원본도 로드가 local을 안 건드리므로 동일 결함일 가능성, UNKNOWN).
  - **같은 프로세스 타이틀 로드**: 게임 종료 경로 `0x41CA80`(`0x41CA85 mov [0xB63FC4],0`, E8 호출자 13곳: `0x41CA50`·`0x41CA6B`·`0x422FC4`·`0x42513E`·`0x42569B`·`0x4256F8`·`0x42574D`·`0x425798`·`0x4257B9`·`0x4257D4`·`0x4626B9`·`0x4A589E`·`0x4A6937`)가 타이틀 복귀에서 불리면 0으로 초기화되어 안전. 불리는지는 UNKNOWN.
- 반대 방향(1P 게임 중 자리 2 세이브 인게임 로드)은 R4가 표를 복원해 local 2를 줄 것으로 예상(원본은 표·local 불변 → 결함 예상).
- 후보 보강 R4b(솔로 게이트 안에서 `mov dword [0xB63FC4],0`을 `0x43AF40` 호출 전에 추가, cave +10 B): 솔로에서 "첫 일치 또는 0"으로 결정적이 된다. 솔로 기본 local은 0(혼자하기 초기화 `0x4B6355`·부팅값)이라 의미상 안전하지만 **런타임 증거 없이는 적용하지 않는다**(§4 분기).

## §4 다음 work H-G7x — 같은 프로세스·교차 로드 매트릭스 (사전등록, 1 work lap)

목표: R4 후보가 local이 이미 설정된 상태에서도 저장 당시 자리를 주는지 확인하고, 필요하면 R4b로 보강한다. 대상은 최종 스택 후보 **cand67**(G6+G7 normal `2de1944e…`)와 대조 **port**(`0e28ef57…`).

하네스(`tools/g7_save_load_probe.py` 확장만, 기존 경로 불변, 테스트 RED→GREEN): 두 번째 세이브 슬롯(예: save002)·인게임 로드에서 대상 세이브 선택·게임 종료→타이틀 복귀 단계를 추가한다. 1P 세이브는 같은 run에서 seat 0으로 만들거나 lap984 `cand_s0/save001.dat`(SHA는 probe-result의 `b_save.sha256`)를 입력 fixture로 명시한다.

측정(격리 사본·prefix·Xvfb, lobby-snapshot seat, 각 단계 local·own·solo·ids·ps 30초·드래그 선택 owner 기록):
- **X-1(R-1b)**: 같은 프로세스에서 자리 2 게임 → 저장 → 타이틀 복귀 → 그 세이브 타이틀 로드 → local 2·ps `[3]`·owner 2.
- **X-2**: 같은 프로세스에서 자리 2 게임 → 타이틀 복귀 → **1P 세이브** 타이틀 로드 → local 0·ps `[3]`·owner 0. 타이틀 복귀 직후 local 값도 기록(`0x41CA80` 경로 판별).
- **X-3**: 자리 2 게임 중 **인게임 로드로 1P 세이브** → 기대 local 0·owner 0. port 대조 값 함께 기록.
- **X-4**: 1P 게임 중 **인게임 로드로 자리 2 세이브** → 기대 local 2·ps `[3]`·owner 2. port 대조(결함 여부) 기록.
- 안전: 크래시 0, G5SC sidecar 로드 정상, game 사본 정리, 후보/입력 SHA 기록.

분기:
- 전부 PASS → H-G7x PASS(partial). 다음은 G6 재측정 on cand67(기존 `tools/g6_shift_click_probe.py --seat-method lobby-snapshot`에 cand67 EXE 입력만 추가) → fixed_start 런타임 1회 → 사용자 합격 요청 묶음.
- **X-2 또는 X-3에서 cand67 local≠0(이전 값 잔존)** → 같은 lap에서 R4b 구현(`patches/selection/g7_title_load_seat_restore.py`에 cave 보강, 테스트 갱신, 새 후보 SHA 기록) 후 X-2·X-3과 lap984 R-1·R-3 최소 재실행. port도 같은 잔존이면 원본 결함(교차 변형)으로 기록하되 G7 수리 범위에 포함한다(DESIGN "1P 세이브 회귀 없음").
- 크래시·R-1 회귀 → 불수용, 원인 추적 후 재실행(③ 반복 원칙). 근거 충돌이면 ESCALATE_SOL.

## §5 사용자 ↑/↓ 자리 동일성 처리

- 정적 근거상 `[0xB63FC4]`의 비0 값은 `0x43AF40`(호출 5곳)만 쓴다(직접 쓰기는 teardown `0x41CA85`의 0뿐, lap976). 게임 시작 때 스냅샷이 live 표를 복사하므로(`0x41B9CA`), R4는 **자리가 어떤 입력으로 정해졌든** 게임 시작 시점 표에서 `0x43AF40`이 계산한 자리를 다시 계산한다 — own id가 같고 마지막 `0x43AF40` 호출 뒤 표가 바뀌지 않았다는 조건에서.
- 그래서 ↑/↓ 경로 동일성은 G7 수리 메커니즘의 차단 요인이 아니다. 런타임 동일성은 UNKNOWN·비차단으로 두고, **최종 확인은 사용자 직접 플레이 합격 요청**(cand67 normal/fixed_start, 대기실 ↑/↓로 자리 이동 → 저장 → 게임 재시작 → 타이틀 불러오기)에 포함한다. APPROVALS lap981 질문은 열린 채 유지한다.
- 사용자 합격 요청은 마일스톤 경계이므로 H-G7x와 G6 재측정이 끝난 뒤 middle이 범위를 확정해 올린다.
