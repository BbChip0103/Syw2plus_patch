# G6·G7 — 로컬 플레이어가 1P가 아닐 때의 원본 결함 (2026-10-04)

## 사용자 보고

- 빌드: G2 ESL2608 + G5 이식판(단일플레이).
- 재현 조건: 혼자하기 대기실에서 방향키로 내 자리를 1P가 아닌 슬롯으로 옮긴다.
- G6: Shift+클릭으로 유닛을 선택에 추가할 수 없다.
- G7: 인게임에서 저장한 뒤 **타이틀 화면에서** 불러오면 곧바로 패배가 뜨거나, 1P의 유닛/건물을
  내 것으로 조종하게 된다. 인게임에서 불러오는 경우는 해당하지 않는다.

## 정적 분석 결과 (게임 실행 0, 런타임 미확정)

판정: 두 버그 모두 **원본 게임 결함**이며 G2/G5/ESL 이식 회귀가 아니다. 1P 자리에서는 드러나지
않고, G5 Shift 테스트(lap728/766/767)도 owner0으로만 수행했다.

- 로컬 플레이어 index는 DWORD `0xB63FC4`(bss, 부팅값 0)다.
  - 게임 종료 teardown `0x41CA85`에서 0으로 초기화된다.
  - 그 밖에는 `0x43AF40`이 슬롯 ID표 `0x632CA0`에서 자기 DPID 위치를 찾아 다시 계산한다.
  - G5 cave는 이 값을 읽기만 한다(`0x18A7033`/`0x18A7109`).

### G6 Shift+클릭 추가

- 경로: `FUN_0041DC40`. `0x41DD1E`에서 `[0xB93998]==1`이면 Shift 분기로 간다.
- 결함: `0x41DD82..0x41DDE7` 루프가 실제 선택 개수(`[esp+0x10]`)가 아니라 배열 칸 수 전체
  (원본 20, G5 50)를 돈다.
  - 빈 칸은 slot 0으로 읽혀 유닛 0번의 owner가 local과 비교된다(`0x41DD93`).
  - 둘이 다르면 `[esp+0x28]=1`이 되고 `0x41DE45`에서 추가가 중단된다.
- 원본과 G5의 이 함수 diff는 배열 크기와 주소 재배치뿐이다.
- Shift+드래그(`0x41DF59`)는 빈 칸을 건너뛰므로 정상일 것으로 추론한다.

### G7 타이틀 불러오기

- 저장 `0x440C20`과 로드 `0x440FF0`은 인게임 로드와 타이틀 로드가 함께 쓴다.
- 저장 스트림에 `0xB63FC4`가 없다. 로드도 이 값을 복원하거나 다시 계산하지 않는다
  (`0x43AF40`, `0x424DB4` 복사를 호출하지 않음).
- 인게임 로드: 현재 local이 남아 있으므로 같은 자리면 정상이다.
- 타이틀 로드: teardown에서 0으로 초기화된 local로 불러오므로 1P를 조종하게 된다.
  1P가 이미 패배했거나 빈 자리면 즉시 패배가 뜬다(이 연결은 추론).
- 패치 영향은 없다. G2 래퍼(`0x1895300`)와 G5 sidecar(`0x18A7800`/`0x18A7880`, fclose 직전)는
  local을 건드리지 않고 스트림 위상도 밀지 않는다.

### lap976 middle 역어셈블 재확인 (2026-10-05, 실행 0)

- 원본 `0x41DC64..0x41DC78`이 스택 배열 `[esp+0x30]`을 0으로 채운다(이식판 0x32칸). 그래서 빈 칸 = 유닛 id 0이며,
  owner 조회 `0x40F560`은 원본 `0x66B81E`, 이식판(배포 normal SHA `0e28ef57…`) `0x112E08E`의 0번 행을 읽는다.
- 두 번째 루프 머리 `0x41DD82` old bytes `66 8B 06 B9 6C E3 61 00`, 루프 끝 `0x41DDE4 cmp edi,0x14`(이식판 `0x32`), 루프 뒤 `0x41DDE9`.
- Shift+드래그 `0x41DF59`의 빈 칸 skip 확인. `[0xB63FC4]` 직접 쓰기는 `0x41CA85` 하나, 나머지는 `0x43AF40` 호출 5곳
  (`0x4219B5`·`0x439751`·`0x4B771D`·`0x4B774C`·`0x4B9653`).
- 원문·수리 계획: `docs/work/active/G6_MIDDLE_LAP976_SHIFT_CLICK_COUNT_BOUND_HANDOFF.md`.

## 해결 방향

- **G6(작음):** `0x41DD70` 부근을 `.g5code` cave로 바꿔 루프를 `i < [esp+0x10]`까지만 돌린다.
  선택 개수가 0이면 루프를 건너뛴다.
- **G7(중간):** G5SC sidecar 뒤에 버전 태그와 local DWORD를 기록하고, 로드할 때 태그가 있으면
  `0xB63FC4`에 복원한다. 태그가 없는 기존 세이브는 현행 동작을 유지한다.
  - 미결: `0x632CA0` 슬롯표나 local에서 파생된 UI/카메라 상태도 함께 복원해야 하는지.
  - 대안: 저장된 로비 스냅샷 `0x632F7C`에서 다시 계산한다. 다만 싱글플레이 DPID가 판마다
    같다는 근거가 없다.

## 런타임 확정 절차 (다음 작업)

격리 환경에서 원본 EXE와 이식판을 각각 실행해, 1P가 아닌 자리(local=1 이상)에서 확인한다.

- G6: A 클릭 → B Shift+클릭.
  - 선택 개수(이식판 `[0x18A6000]`, 원본 `[0x899024]`)가 늘지 않는지 본다.
  - `0x41DDB3`이 실행되는지 본다.
  - 대조: Shift+드래그 추가는 성공해야 한다.
- G7: 저장 전 `[0xB63FC4]=k`를 기록한다.
  - 타이틀로 나갈 때 0이 되는지 본다.
  - 타이틀 로드 뒤 0인지, 인게임 로드 뒤 k가 유지되는지 비교한다.
  - `0x632CA0[0..7]`과 `0x632F80[0..7]`을 함께 기록한다.

### lap977 work: H-G6a 패치·런타임 결과 (2026-10-05)

- 패치 `patches/selection/g6_shift_click_count_bound.py`: 이식판(normal `0e28ef57…`·fixed_start `703deaf4…`) 입력만 허용.
  지점 `0x41DD82` old `66 8B 06 B9 6C E3 61 00` → `E9 rel32` + `90 90 90`, cave `0x18A7C00`(`.g5code` +0xC00, 이식판 코드 끝 +0x8DA·+0x900~0x1000 전부 0):
  `3B 7C 24 10`(cmp edi,[esp+0x10]) · `0F 8D → 0x41DDE9` · 원래 2명령 · `E9 → 0x41DD8A`. 후보 SHA normal `b50af2a6…2f4f`, fixed_start `7c891658…64b5`.
- 대기실 방향키(좌우상하)·번호/유형 버튼 클릭으로는 `[0xB63FC4]`가 0에서 바뀌지 않았다(4회 시도, 로비는 확인 직후 약 1.5초 안에 자동 시작). 런타임에서
  local DWORD를 직접 1·3으로 덮으면 "게임을 떠나 나갔습니다"+ps27(local이 참가자 표에 없음, G7 즉시 패배와 같은 계열 관측)이고,
  local=1(컴퓨터 자리)은 AI가 fixture를 조종했다. 그래서 기본 하네스는 local 0을 두고 **미사용 풀 slot 0의 owner byte**
  (원본 `0x66B81E`, 이식판 `0x112E08E`)를 K로 써 `0x41DD93`의 빈 칸 owner≠local 비교를 재현한다(실제 자리 이동 아님).

### lap978 middle: 로비 local 갱신 경로·방향키 정적 스캔 (2026-10-05, 원본 `b56986e0…a8ac` capstone)

- 게임 생성 `0x4219A0..0x4219BA`: `0x439B90`(자기 DPID, `0xC0D110` 객체) → `0x43AE80`(첫 빈 `0x632CA0` 칸에 DPID, 행 `0x632CC0+6i`=5·`+2`=0(사람)·`0x632CF0[i]`=0·이름 `0x632D94+15i`)
  → `0x4B6AD0` → `0x43AF40(&0xB63FC4)`(첫 일치 칸 index). `0x43AEF0`은 DPID 칸 제거(행 `+2`=1).
- 로비 갱신 `0x4B7700`: `[0xC0D0F4]`≠0이면 `0x632E0C`→`0x632C9C` 0x5C dword 복사 → `0x43AF40(&0xB63FC4)` → 플래그 0. 대기실에서도 local이 바뀔 수 있는 경로다.
- 혼자하기 초기화 `0x4B6355..0x4B63C8`(`[0x4ED848]` 검사): `0x632CA0[0..7]`을 같은 값(ebp)으로 채우고 0행 `+2`=bl, 나머지 행 `+2`=1.
- `GetAsyncKeyState`(IAT `0x4E51DC`) 방향키 사용은 인게임 스크롤 `0x41D09F` 하나(원본·이식판 전 실행 섹션 동일). `0x4B8D69`는 F5+Shift 검사다.
  VK 0x25~0x28 비교·스위치에서 대기실 자리 이동 처리기는 찾지 못했다(UNKNOWN). 근거 스크립트·출력: `temp/Syw2plus_patch/20261005_lap978_middle_review/`.

### lap980 middle: 키 입력 경로·대기실 포커스 (2026-10-05, 원본 `b56986e0…a8ac` capstone, 실행 0)

- main WndProc `0x423DC0`(RegisterClassA `0x423C8B`). WM_KEYDOWN `0x423FAF`: `lea eax,[wParam-9]; cmp eax,0x72` → byte 표 `0x42454C` → jump 표 `0x424530`.
  처리 키는 Tab·Esc(0x1B)·Space·Home(0x24)·Insert(0x2D)·F12(0x7B)뿐, **방향키 0x25~0x28은 default `0x4241FE`**: `0x421630(vk,1)` → 키 상태 word `[0x61E070+vk*2]`=1(Up `0x61E0BC`, Down `0x61E0C0`), `0x4216B0` → 입력 큐(16바이트 레코드 `0x61DA30+16i`, 개수 `[0x61E270]`≤100). WM_KEYUP `0x424249`이 0으로 되돌린다.
- 큐 dequeue `0x4217B0` 호출자는 `0x41E299`(인게임) 하나. 대기실이 방향키를 읽는 지점은 UNKNOWN(lap978 VK 스캔은 `lea -9` switch를 못 잡음).
- 입력란 subclass(SetWindowLongA `0x4591D2`; CallWindowProcA 다수)는 WM_KEYDOWN에서 Tab/Enter만 처리, 나머지는 EDIT 기본 proc → EDIT 포커스면 방향키가 main에 오지 않는다. 일부 subclass는 WM_SYSKEYDOWN(0x104)에서 `SetFocus([0x639348])`.
- 이식판 `0e28ef57…`의 `0x423FAF..0x424240`·두 표·`0x421630`·`0x4216B0` 바이트는 원본과 동일.
- lap979 S-1 캡처의 채팅 줄 캐럿 깜빡임 → 포커스가 채팅 EDIT였을 가능성. 판별 절차: `docs/work/active/G6_G7_MIDDLE_LAP980_HG6S_ACCEPTANCE_KEY_FOCUS_G7_OBSERVE_HANDOFF.md` §3.
- S-2 사본 표(id `[1,1,0,0,0,0,0,0]`, own id `[0xC0D11C]`=0)는 칸 2~7이 모두 own id와 같다. 솔로 기본 표는 id 전부 1이라 `0x43AF40`이 일치 칸을 못 찾고 local은 부팅값 0을 유지한다.

### lap983 middle: 로드 스트림의 로비 스냅샷·G7 수리 지점 (2026-10-05, 원본 `b56986e0…a8ac` capstone, 이식판 `0e28ef57…` 바이트 대조, 실행 0)

- 저장 `0x440C20`/로드 `0x440FF0` 마지막 고정 블록: `0x892410`(0xE397C, 플레이어 구조체 `0x956770`+owner×`0x3ABC` 포함, ai flag = +2) → **`0x632F7C`(0x170 = 0x5C dword)**.
- `0x632F7C` = 게임 시작 때 live 로비 표 `0x632C9C`의 복사본(`0x41B9CA..0x41B9DB`·`0x41BC59..0x41BC6A`, 호출 ps 핸들러 `0x424D50`). 반대 복사 `0x632F7C→0x632C9C`는 ps 핸들러 `0x424DA0`(`[0x9E1DD8]==0`일 때, dispatch `0x4234BB`)에만 있고 로드는 부르지 않는다.
- 로드 끝 `0x4414DA`가 `[0xB63FC4]`로 플레이어 구조체 국가 byte를 읽어 `0x419B50` 호출; 그 앞 `0x441448..0x441486`도 local 의존 가능 → 수리 지점은 fclose 직후 **`0x441310`(old `8B 2D 2C AF B3 00`, 원본=이식판)**.
- lap982 save 두 개 직접 파싱: 스냅샷 1곳 = 시작 live 표와 byte 동일(ids `[1,1,0,…]`, own 0 첫 일치 2), 헤더 뒤 `[0x4ED848]`=1(솔로; 혼자하기 초기화 `0x4B6355`가 `cmp word [0x4ED848],bp`), `[0x9E1DD8]`=0.
- 이식판 `0x440FF0..0x441500` 차이는 fread 래퍼(`0x441041`·`0x4412DD`)·fclose→G5SC(`0x44130C`)·풀 상한(`0x441444`)뿐. `.g5code` +0xD00(`0x18A7D00`)~ 비어 있음(G6 cave +0xC00).
- 수리 경로 R4(스냅샷 복원 + `0x43AF40`) 채택, R2·R3 대안 보존. 근거·사전등록: `docs/work/active/G7_MIDDLE_LAP983_HG7O_ACCEPTANCE_SNAPSHOT_RESTORE_HANDOFF.md`, 스크립트·출력 `temp/Syw2plus_patch/20261005_lap983_middle_review/`.

### lap985 middle: G7 후보 검수·local 잔존 경로 (2026-10-05, 이식판 `0e28ef57…` capstone/바이트 스캔, 실행 0)

- hook `0x441310`은 `0x44130A push esi; call 0x10910D0`(fclose→G5SC) 직후, `0x441316 add esp,4` 전이다. 이식판 실행 섹션에서 `0x441311..0x441315`로 들어오는 분기·abs32 참조 0.
- `0x43AF40`은 첫 일치가 없으면 `[0xB63FC4]`를 바꾸지 않는다 → 1P 솔로 표(ids `[1]*8`, own 0)에서는 R4 cave 뒤에도 local이 이전 값으로 남는다.
- 게임 종료 초기화 `0x41CA80`(`0x41CA85 mov dword [0xB63FC4],0`) E8 호출자 13곳: `0x41CA50`·`0x41CA6B`·`0x422FC4`·`0x42513E`·`0x42569B`·`0x4256F8`·`0x42574D`·`0x425798`·`0x4257B9`·`0x4257D4`·`0x4626B9`·`0x4A589E`·`0x4A6937`. 타이틀 복귀가 이 중 무엇을 타는지는 UNKNOWN.
- 로비 덤프 `0x632C9C..0x632F80` 중 스냅샷 범위(0x170) 뒤 `0x632E0C~`는 새 프로세스 타이틀 로드 뒤 시작 때와 다르다(73 B, 복원 대상 아님). 근거·사전등록: `docs/work/active/G7_MIDDLE_LAP985_HG7R_ACCEPTANCE_CROSS_LOAD_HANDOFF.md`, 스크립트·출력 `temp/Syw2plus_patch/20261005_lap985_middle_review/`.

### lap987 middle: R4b 검수 (2026-10-05, lap986 probe-result 10개 재계산·후보 재조립, 실행 0)

- 인게임 로드는 원본계에서 로비 표 `0x632C9C`를 건드리지 않는다(port_x3: 로드 전후 표 byte 동일, local 유지 → 저장 자리와 다르면 ps 27→29 패배).
- 타이틀 복귀 직후 local 0·표 ids 유지 → 직접 쓰기 `0x41CA85`(`0x41CA80`) 경로로 본다(호출자 UNKNOWN).
- R4b cave(66 B): 솔로 로드 뒤 local = 스냅샷 표의 own id 첫 일치, 없으면 0. 근거·사전등록: `docs/work/active/G7_MIDDLE_LAP987_HG7X_R4B_ACCEPTANCE_G6_REMEASURE_HANDOFF.md`, 스크립트·출력 `temp/Syw2plus_patch/20261005_lap987_middle_review/`.
