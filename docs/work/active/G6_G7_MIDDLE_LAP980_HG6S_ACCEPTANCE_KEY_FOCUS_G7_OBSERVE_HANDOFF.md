# G6·G7 middle 검수 — lap979 H-G6s 수용(partial), 다음 work H-G6k(방향키 전달 판별)·H-G7o(불러오기 관측) handoff (lap980)

- 작성: 2026-10-05, lap980 middle(Claude Code `claude-opus-5-5`, high). 게임 실행·source 변경·commit 0.
- 입력: `loop/ESCALATE_SOL`(lap979 work), 기록 `docs/history/laps/20261005_lap979_work_g6_real_seat_lobby_snapshot_hg6s.md`, 이전 카드 `G6_MIDDLE_LAP978_HG6A_ACCEPTANCE_REAL_SEAT_HANDOFF.md`, INBOX 2026-10-05 04:45 사용자 답(대기실 ↑/↓).
- 이번 lap 산출물(공유 temp, 직접 생성): `temp/Syw2plus_patch/20261005_lap980_middle_review/`
  - `recalc_lap980.py`→`recalc_lap980.json`(SHA256 `296ca220895d4944b5392c5bea8bd2774f3e4c8747da2c5309a59ded364fedc1`)
  - `wm_keydown_switch.py`→`wm_keydown_switch.json`(`9b6fe16a…e4fea3`), `port_key_bytes.py`→`port_key_bytes.json`(`4a242464…78cd0`)
  - `keystate_readers.py`→`keystate_readers.json`(`abf971cd…b48703fc`), `dequeue_callers.py`→`dequeue_callers.json`, `subclass_scan.py`, `disr.py`, `wndproc_423dc0.txt`

## §1 독립 재계산 (제품 helper 미사용, stdlib+PIL)

probe-result 8개 SHA256이 lap979 기록 앞 8자와 모두 일치한다. 재계산 결과 기록과 **판정 불일치 0**.

| run | EXE | 결과 |
|---|---|---|
| s1_name / s1_number / s1_none | port `0e28ef57…` | 키 Right·Down·Left·Up 각 1회(0.25초 hold), 로비 표 5덤프 SHA 동일·flag 0·local 0. PNG(포커스 직후 대비) 자리 패널(x<190) 변화 0, 전체 화면 변화는 **채팅 입력줄 (241,509) 캐럿 깜빡임 2px뿐**(none·number), name은 0px |
| s2_port(첫 시도) | port | 사본 id `[2,2,1,1,1,1,1,1]`, 플래그 소비·표=사본, own id 0과 일치 칸 없음 → local 0 유지(BLOCKED). 재계산 local=None으로 일치 |
| s2_probe | port | 사본 id `[1,1,0,0,0,0,0,0]`, 행 `[0,0,1,1,0,0]`/`[5,1,1,2,0,1]`/`[5,2,0,4,0,2]`, 활성 `[0,1,1,0…]`. 재계산 local = 첫 일치 index **2** = 관측 2 |
| port2 | port | local 2(로비·before_start·ps3), 60초 locals `[2]`, owner2 유닛 2, 30초 변화 0. G6-1 `[1,1,1,1,1,1]` 클릭 합류 0/5, G6-2 1→3(쌍 합류·외부0), G6-3 3→2, G6-4 50→50(추가 slot 미포함·집합 불변) |
| orig2 | 원본 `b56986e0…` | local 2·안정 60초 같음. G6-1 `[1×6]` 0/5, G6-2 1→3, G6-3 3→2(G6-4 해당 없음, 원본 cap 20) |
| cand2 | 후보 `b50af2a6…` | local 2·안정 같음. G6-1 `[1,2,3,4,5,6]` 합류 5/5, G6-2·3 같음, G6-4 50→50 |

- 세 COMPLETE run 모두 `count==len(slots)`·중복 0, fixture/worker owner=2, cleanup 프로세스 0·game 제거.
- 화면 확인: port2 `s2_after` 패널 1행 "없음", 2·3행 사람/컴퓨터 버튼, 이름 글자 없음(기록된 한계와 같음), 채팅 줄 캐럿 표시. `ps3_stability_end` 정상 HUD(5000/5000·20/1500), 떠남 문구 없음.
- 전사 정정(기록만): lap979 기록의 "각 12회"는 **포커스 3종×키 4개=12회(각 키 3회)**다. 판정에는 영향 없음.
- 주의(기록): 사본은 id 칸 2~7을 모두 own id 0으로 둔다(행 3~7은 type 0·활성 0). local은 첫 일치라 2지만, 사용자가 방향키로 옮긴 실제 표와 같은지는 모른다. G7 수리 경로 선택(§4 R1)이 이 표 내용에 의존하므로 H-G6k가 먼저다.

**판정: H-G6s PASS(partial) 수용.** 게임 자체 로비 갱신 경로로 만든 실제 local=2에서 원본·이식판 결함 재현, 후보 수정 확인. DESIGN G6 사용자 합격은 아님(사용자 경로 동일성 UNKNOWN, 사람 플레이·fixed_start 미실행).

## §2 새 정적 근거 — 대기실 방향키가 안 먹은 이유 후보 (원본 `b56986e0…`, capstone)

- main WndProc는 `0x423DC0`(RegisterClassA `0x423C8B`의 lpfnWndProc). WM_KEYDOWN(`0x423FAF`)은 `lea eax,[wParam-9]; cmp eax,0x72` → byte 표 `0x42454C` → jump 표 `0x424530`.
  VK 0x25~0x28은 default `0x4241FE`로 간다: `0x421630(vk,1)`이 **키 상태 word `[0x61E070+vk*2]`=1**(VK_UP `0x61E0BC`, VK_DOWN `0x61E0C0`), 이어 `0x4216B0`이 입력 큐(`0x61DA30`+16·i, 개수 `[0x61E270]`≤100)에 넣는다. WM_KEYUP 경로 `0x424249`가 0으로 되돌린다.
  lap978 VK 스캔은 `lea …-9` 형태 switch를 못 잡았다(“처리기 없음”은 스캔 한계였다). 큐 소비 `0x4217B0` 호출자는 인게임 `0x41E299` 하나라 **대기실이 방향키를 읽는 곳은 아직 UNKNOWN**이다.
- 이식판 `0e28ef57…`의 `0x423FAF..0x424240`·두 표·`0x421630`·`0x4216B0` 바이트는 원본과 동일(`port_key_bytes.json`). 주소를 그대로 쓴다.
- 입력란 subclass(SetWindowLongA `0x4591D2`, CallWindowProcA 다수 `0x45C9E4`…)는 WM_KEYDOWN에서 Tab(9)·Enter(0xD)만 처리하고 나머지는 원래 EDIT proc으로 넘긴다. 즉 **채팅 EDIT가 키보드 포커스를 가지면 방향키는 main WndProc에 오지 않는다.** 일부 subclass는 WM_SYSKEYDOWN(0x104)에서 `SetFocus([0x639348])`(main)을 부른다(`0x45C8EB`). 대기실 채팅 줄이 어느 subclass인지는 미확정.
- lap979 S-1 캡처의 캐럿 깜빡임(채팅 줄)은 포커스가 채팅 EDIT에 있었다는 관측과 맞는다. 사용자 답(INBOX 04:45, “여전히 안 되면 키 전달 방식(포커스·keydown 유지·XTest vs SendEvent)을 의심”)의 포커스 단계는 아직 시험되지 않았다.

## §3 다음 work H-G6k — 대기실 ↑/↓ 전달 판별 (사전등록, 1 work lap)

목적: 사용자 경로(↑/↓)로 실제 자리를 옮길 수 있는지 판별한다. 제품 patch/bridge/EXE 불변, `tools/g6_shift_click_probe.py`에 `--seat-method keys-focus`(가칭)만 추가.

1. 이식판 normal, 혼자하기 대기실 진입 직후. 각 시도: `xdotool keydown Down`(또는 Up) → 0.3초 대기 → **키 상태 word `0x61E0C0`(Up은 `0x61E0BC`)·큐 개수 `[0x61E270]` 읽기** → keyup → 1초 뒤 표(`0x632C9C`)·`[0xB63FC4]`·자리 패널 캡처.
2. 포커스 변형(순서대로, 첫 PASS에서 멈춤): (f0) 그대로 / (f1) `Alt_L` 탭 뒤 / (f2) 빈 영역 클릭 뒤 — 큰 회색 메시지 판 (490,410)·좌측 패널 배경 (100,160) / (f3) 내 자리 행의 번호 버튼 (40,78) 클릭 뒤 / (f4) `xdotool key --window <wine top-level>`(XSendEvent). 각 변형에서 Down 3회·Up 3회.
3. 측정 판정:
   - **K-1 전달:** 해당 변형에서 hold 중 키 상태 word=1. 전 변형 0이면 = 키가 main WndProc에 오지 않음 → (f4)까지 실패 시 BLOCKED(전달).
   - **K-2 자리 이동(PASS):** 게임이 `[0xB63FC4]`를 바꾸고(직접 쓰기 0) 패널의 내 행이 바뀐다. 표 id/행/활성 덤프를 S-2 사본과 비교해 기록(G7 R1 판단용).
   - K-1은 1인데 K-2가 전 변형 0 → 대기실 방향키 처리기가 이 경로가 아님 → BLOCKED(처리기), lobby-snapshot을 G6/G7 기본으로 유지하고 사용자 경로 동일성 UNKNOWN 유지.
4. K-2 PASS면 같은 lap에서 그 방법으로 **C@k와 P@k G6-1~4 재측정**(slot0 poke 0, 기대 P `[1×6]`·C `[1..6]`, G6-4 50 상한). O는 선택.
5. 반증/중단: Alt 탭이 메뉴·창 상태를 바꿔 로비가 깨지면 그 변형만 FAIL로 적고 다음 변형. 로비 자동 시작·크래시는 숨기지 않고 기록.
6. 결과에 관계없이 이 work는 middle로 escalate하지 않는다(하네스 seat-method 선택일 뿐). 다음 lap은 바로 work H-G7o. 단, 근거 충돌(예: 키 상태 1인데 표가 다른 형태로 바뀌어 local이 깨짐)이면 ESCALATE_SOL.

## §4 그다음 work H-G7o — 저장/불러오기 local 관측 (사전등록, 1 work lap, 수리 없음)

자리 만들기: H-G6k PASS면 그 키 경로, 아니면 `--seat-method lobby-snapshot`(seat 2). 이식판 P 필수, 원본 O 필수(원본 결함 확인), 후보 C는 선택(G6 patch는 저장 경로 무관).
저장/불러오기 좌표는 기존 하네스 재사용: 일시정지 저장 `SAVE_SLOT_POINT (340,166)`·`SAVE_ACTION_POINT (316,372)`·일시정지 불러오기 `PAUSE_LOAD_POINT (400,272)`(`tools/g5_candidate_drag_probe.py`), 타이틀 불러오기 `LOAD_MENU (296,505)`·`LOAD_CONFIRM (316,372)`(`tools/g1_saved_scene_probe.py`). 타이틀 불러오기는 **새 격리 사본에 저장 파일을 미리 넣고 새 프로세스로**(`tools/g5_v10_foreign_save_load_probe.py`의 seeding 방식) 한다.

| 단계 | 기록 | 사전등록 PASS |
|---|---|---|
| A 게임 시작 | `[0xB63FC4]`, 표 `0x632C9C`+0x74, `[0xC0D11C]`, `0x632F7C`+0x80, owner별 유닛 수 | local=k(≠0) |
| B 일시정지 저장 | 저장 파일 크기·SHA256(사본을 artifact로 복사) | 파일 생성 |
| C 인게임 불러오기(대조) | 30초 local, owner k 일꾼 일반 클릭 선택 수·owner, 패배/떠남 문구 | local=k 유지·선택 1(owner k)·문구 0 |
| D 타이틀 불러오기(새 프로세스) | A와 같은 덤프, 30초 ps/화면, owner k·owner 0 유닛 클릭 결과 | **결함 재현 = local 0** 그리고 (패배/떠남 문구 또는 owner 0 조종 또는 owner k 클릭 선택 불가) |

- G7o-1~3 = P와 O 둘 다 B·C·D 기록. G7o-4(수리 경로 분류): D 직후 표 id와 own id로 첫 일치 index를 계산한다. **= k이면 R1**(불러오기 뒤 `0x43AF40(&0xB63FC4)` 재계산 hook, 세이브 포맷 불변) FEASIBLE, 아니면 **R2**(G5 sidecar 뒤 버전 태그+local DWORD) 필요.
- 반증: (i) D에서 local≠0 → 정적 분석(로드가 local을 안 건드림) 반증, G7 결함 재정의 필요 → ESCALATE_SOL. (ii) C에서도 local이 깨짐 → 결함은 부팅 상태가 아니라 로드 경로 → ESCALATE_SOL. (iii) 로드 크래시 → 결함과 분리해 기록.
- 이 work는 관측만 한다. 결과는 middle 독립 검수(ESCALATE_SOL) 뒤 R1/R2 수리 work로 간다.

## §5 정리·안전

- prefix 8개(약 4.6GB)는 archive하지 않는다: 루트 FS 여유 127GiB(기준 20GiB 초과). manifest/output/prefix 보존.
- 원본/참고/raw/golden 불변, G2/G5 sidecar·G5 50 상한 비회귀, 커밋/게시 0, 격리 사본/prefix/display만 사용, 다른 Xvfb(:78·:186·:187) 비접촉.
- INBOX 04:45 사용자 답 항목은 H-G6k 결과가 나올 때까지 미처리로 둔다.
