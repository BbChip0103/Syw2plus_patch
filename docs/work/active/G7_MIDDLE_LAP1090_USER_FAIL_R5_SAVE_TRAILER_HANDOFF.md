# G7 middle — 사용자 FAIL(2026-10-06 19:31) 재작업 계획: R4b 폐기 → R5(세이브 꼬리 G7 블록) work handoff (lap1090)

- 작성: 2026-10-07, lap1090 middle(Claude Code `claude-opus-5-5`, high). 게임 실행·source 변경·commit 0.
- 입력: INBOX 2026-10-06 19:31 사용자 결과, APPROVALS lap989 항목의 사용자 플레이 결과, 이전 카드 `G7_MIDDLE_LAP987_HG7X_R4B_ACCEPTANCE_G6_REMEASURE_HANDOFF.md`,
  `analysis/memory_maps/g6_g7_local_player_slot_bugs_20261004.md`.
- 이번 lap 정적 산출물(공유 temp, 읽기 전용 스캔): `temp/Syw2plus_patch/20261007_lap1090_middle_review/`
  - `scan_lobby_controls.py`(`72a0faf6…1f96`) → `scan_lobby_controls.json`(`633d64e3…4d05`)
  - `r5_site_bytes.py`(`80e85e1a…d6ef`) → `r5_site_bytes.json`(`88b8b16b…aace8`)
  - 역어셈블 `port_g5sc_7800_7960.txt`(`82f4e0eb…f0fb0`)·`port_g5sc_load_10910d0.txt`(`9cb509d3…35cd`)·`d_439520.txt`·`d_4b9580.txt`·`d_4b7f40.txt`(lap980 `disr.py`로 생성)
- EXE: 원본 `b56986e0…a8ac`, 이식판 normal `0e28ef57…d257`·fixed_start `703deaf4…6ea0`(이번 lap 직접 sha256 MATCH).

## §1 사용자 결과와 기존 증거의 충돌

- 사용자(일반판 `fb7c2131…`·시작자리고정판 `58b9b22a…` 둘 다): 대기실 ↑/↓로 1P 아닌 자리 → 시작 → 저장 → **타이틀 로드·게임 중 로드 둘 다** 1P(컴퓨터였던 자리) 유닛/건물로 로드. G6는 사용자 PASS.
- 격리 증거(lap984~988)는 실제 ↑/↓ 경로가 아니라 하네스 `lobby-snapshot`(seat 0↔K 교환 표를 `0x632E0C`에 쓰고 `[0xC0D0F4]`로 게임 자체 갱신 `0x4B7700`)으로 만든 자리 2에서 R-1~R-4·X-1~X-4 PASS였다. 실제 경로 재현은 lap981에서 채팅 EDIT 포커스로 BLOCKED.
- 판정: **H-G7x/R4b 기술 PASS(partial)는 사용자 실경로에 일반화되지 않았다(사용자 FAIL이 우선)**. 기존 기술 기록은 수정하지 않고 보존한다.

## §2 원인 좁히기 (정적, 이번 lap)

1. `[0xB63FC4]`(local) 쓰기는 원본 전체 `.text`에서 직접 `0x41CA85`(=0) 하나와 `push 0xB63FC4; call 0x43AF40` 5곳(`0x4219B5`·`0x439751`·`0x4B771D`·`0x4B774C`·`0x4B9653`)뿐이다(`scan_lobby_controls.json` local_refs, 읽기 다수·쓰기 그 외 0). → 사용자 게임 중 local=k(G6 결함이 보였으므로 local≠0)는 **`0x43AF40`이 그때 live 표 `0x632CA0`에서 own id 첫 일치를 k로 찾은 결과**다.
2. R4b 로드 뒤 local = "세이브 스냅샷 `0x632F7C` 표의 own id 첫 일치, 없으면 0". 사용자 증상(두 로드 모두 seat 0)은 **사용자 세이브의 스냅샷에서 첫 일치가 0이거나 없음**과 맞는다. 원래 인게임 로드는 local을 건드리지 않아 같은 자리면 정상이었으므로(원 보고·lap987 port_x3), **게임 중 로드 FAIL은 R4b가 만든 회귀**로 본다.
3. 왜 스냅샷이 실제 자리와 어긋나는지는 UNKNOWN(후보: 실경로가 `0x632F7C` 복사(`0x41B9CA`/`0x41BC59`, ps `0x424D50`) 뒤에 표를 바꾸거나, 게임 중 표를 고쳐 쓰거나(lap987 관찰 "writer UNKNOWN"), own id가 하네스(0)와 다름). 사용자 세이브 파일이 있으면 바로 판별되므로 APPROVALS에 비차단 요청을 올린다(공유 `260921_temp/save/`는 비어 있음, 19:44 생성).
4. 대기실 ↑/↓ 처리기는 여전히 미발견: 원본에 `LISTBOX`/`COMBOBOX` 클래스 문자열 0, 키 상태 word `0x61E0BC`/`0x61E0C0` 직접 참조 0(lap980), `0x439520`(own 행을 `0x6376B4..` 메시지로 복사·`0x439BA0` 송신)은 `[0x4ED848]==0`(비솔로) 분기 `0x4B7F97`에서만 호출. 더 정적 조사하지 않는다(구현 우선).

**결론:** 실제 자리 결정 방식에 의존하지 않는 수리가 필요하다. 저장 시점의 live 상태(local·live 표)를 세이브에 그대로 넣고, 로드 때 그대로 되돌린다.

## §3 R5 설계 (R4b 폐기)

- 기반: **이식판 + G6 cave(`0x18A7C00`)만**. R4b hook(`0x441310`)·cave(`0x18A7D00`)는 적용하지 않는다(`0x441310` 원래 바이트 유지).
- 저장 hook — `0x18A7832` old `E9 45 31 C3 FE`(G5SC 저장 `0x18A7800` 끝의 `jmp 0x4DA97C` fclose 꼬리, 두 이식판 동일): → `jmp` save cave.
  save cave: 레지스터·플래그 보존, `[esp+4]`=FILE*로 `fwrite`(`0x4DA39F`, cdecl `(buf,size,count,FILE*)`) 2회 — ① 헤더 16 B `'G7LS'`(0x534C3747)·version 1·`[0xB63FC4]`·`word [0x4ED848]` 확장, ② live 표 `0x632C9C` 0x170 B. 그다음 원래 `jmp 0x4DA97C`.
- 로드 hook — `0x18A78D6` old `E9 A1 30 C3 FE`(G5SC 로드 `0x18A7880` 끝의 fclose 꼬리; G5SC 태그 불일치 경로도 여기로 옴): → `jmp` load cave.
  load cave: `[0x18A68D0]=='G5SC'`(이번 파일에 G5SC가 있었음)일 때만 `fread`(`0x4DA4A9`) 헤더 16 B를 `.g5bss` 빈 칸(work가 0 범위 확인 후 지정)으로 읽고, 태그 `'G7LS'`·version 1·저장 solo=1·현재 `word [0x4ED848]==1`·local<8이 **모두** 참이면 표 0x170 B를 같은 임시 칸으로 읽어 끝까지 읽혔을 때만 → `0x632C9C`에 복사하고 `[0xB63FC4]`=저장 local. 하나라도 아니면 아무것도 바꾸지 않는다(`0x43AF40` 호출 없음). 그다음 원래 `jmp 0x4DA97C`.
- 위치: 로드 cave는 `0x44130B call 0x10910D0`(G2 PSN2) → `0x18A7880`(G5SC) 안에서 fclose 직전에 돌므로, local을 읽는 `0x441448..0x441486`·`0x4414DA`보다 앞이다(lap983과 같은 요구 충족).
- cave 위치: `.g5code` +0x8DA 뒤 전부 0(두 이식판 `r5_site_bytes.json`); G6 +0xC00(23 B) 회피, +0xD00~ 사용 가능. 크기·non-overlap·restore exact·version 거부는 기존 G6/G7 module 패턴을 따른다.
- 호환 기대: 새 세이브를 G7 없는 이식판으로 읽으면 G5SC 뒤 꼬리를 fclose가 무시(그 로더는 `0x18A78D6`에서 바로 닫음). 꼬리 없는 기존 세이브(G5SC만)는 fread 0 → 무변화 = 원래 동작(타이틀 로드 비1P 기존 세이브는 원래 결함 유지, 인게임 로드는 원래대로 정상). G5SC 없는 G2 이전 세이브는 게이트로 무접촉.
- 행동 정의: 새 세이브는 타이틀·인게임 어느 로드든 **저장 당시 자리**로 복원(lap989 "인게임 로드도 세이브 자리를 따름"과 같은 의미).

## §4 work H-G7s 사전등록 (다음 work 1 lap, Sonnet)

- W-0 정적·단위: `patches/selection/g7_save_trailer_local_restore.py`(새 파일, 기존 `g7_title_load_seat_restore.py`는 수정하지 않고 보존) + 테스트 RED→GREEN: old bytes 2곳·cave 0 범위·G6와 비중첩·restore exact·pinned 외 입력 거부·cave 역어셈블(스택 균형·FILE* 인자 위치) 테스트. G6+R5 normal/fixed_start 후보 SHA 기록. `tools/g7_save_load_probe.py`에 `cand-r5` variant 추가(기존 variant 불변).
- W-1 (진단, 사용자 증상 모형): cand67(R4b `fb7c2131…`)에서 `lobby-snapshot` 자리 2로 시작한 뒤 **저장 전에 `0x632F7C` 스냅샷을 자리 이동 전 표(시작 전 덤프)로 덮어써** 저장 → 같은 프로세스 인게임 로드 + 새 프로세스 타이틀 로드. 예상: 둘 다 local 0(사용자 증상 재현). 재현되면 "스냅샷 불일치" 계열 지지, 안 되면 그 사실과 실제 값 기록(가설 기각은 R5 진행을 막지 않음). 진단 주입이므로 제품 PASS 근거로 쓰지 않는다.
- W-2 (R5 핵심, 사전등록 PASS): cand-r5에서 `lobby-snapshot` 자리 2 + W-1과 같은 스냅샷 덮어쓰기 주입 상태로 저장(S2r) →
  - S-1 새 프로세스 타이틀 로드 S2r: local **2**·ps `[3]`(27/29 없음)·선택 owner 2·30초 유지·크래시 0.
  - S-2 같은 프로세스 인게임 로드 S2r(자리 2 게임 중): local 2·ps `[3]`.
  - S-3 주입 없이 저장한 S2(보통 경로)로 S-1·S-2 반복: 같은 PASS.
  - S-4 1P 게임 저장 S0r: 타이틀·인게임 로드 local 0·owner 0.
  - S-5 교차: 자리 2 게임 중 S0r 인게임 로드 → local 0, 1P 게임 중 S2r 인게임 로드 → local 2(둘 다 ps `[3]`).
  - S-6 기존 세이브(lap982/986 S2·S0 fixture, 꼬리 없음): 인게임 로드 local 유지(원본 동작), 타이틀 로드는 원본과 같은 결과(R5 무접촉 확인; 원래 결함은 남는 것이 정답).
  - S-7 호환: S2r을 이식판 `0e28ef57…`(G7 없음)으로 타이틀 로드 → 크래시 0·G5 선택 상한 50 유지·G2 sidecar 로드 정상(원래 seat 0 귀결은 예상 동작).
  - S-8 G6 비회귀: cand-r5 자리 2에서 Shift+클릭 추가 G6-1 `[1..6]`·cap 50.
  - 공통: 원본/이식판 SHA 불변·안전 0·game 사본 삭제·prefix 프로세스 0. fixed_start는 S-1·S-4만 1회.
  - FAIL: S-1~S-6 중 하나라도 local·ps 기대와 다르면 FAIL, 원인 추적·수리 후 재실행(③ 반복 원칙). S-7 크래시는 FAIL.
- W-3 (시간 상자 20분, 비차단): 실제 ↑/↓ 경로 재현 추가 시도 1종 — 대기실 자리 패널의 **자기 이름/행 클릭 직후** ↑/↓(lap981 미시도 변형). key word·`0x632CA0` 변화·local 기록. BLOCKED면 기록만.
- 산출물: probe-result·save SHA·캡처를 공유 temp `20261007_lap1091_g7_r5/`, 기록 `docs/history/laps/`. work는 자기 결과를 승인하지 않고 fresh Opus middle 독립 재계산으로 넘긴다. 사용자 시험판 스테이징은 middle 수용 뒤.

## §5 남은 위험

- 실제 ↑/↓ 경로가 저장 시점 live 표/local과 다른 무언가(예: 플레이어 구조체 외 per-seat 상태)를 쓰는지는 UNKNOWN — 사용자 재시험이 최종 판정이다.
- 멀티플레이는 게이트로 무접촉(저장은 꼬리를 쓰되 복원 안 함). LAN 멀티 비검증.
- 세이브 크기 +0x180 B. 다른 도구가 세이브 크기를 고정 가정하는지는 work가 `tools/` 검색으로 확인.
