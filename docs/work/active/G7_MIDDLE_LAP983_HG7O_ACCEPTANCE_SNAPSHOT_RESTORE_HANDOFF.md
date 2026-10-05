# G7 middle 검수 — lap982 H-G7o 수용(관측 PASS), 수리 경로 R4(저장된 로비 스냅샷 복원+게임 자체 재계산) → 다음 work H-G7r handoff (lap983)

- 작성: 2026-10-05, lap983 middle(Claude Code `claude-opus-5-5`, high). 게임 실행·source 변경·commit 0.
- 입력: `loop/ESCALATE_SOL`(lap982 work), 기록 `docs/history/laps/20261005_lap982_work_g7_save_load_local_observe_hg7o.md`, 이전 카드 `G6_G7_MIDDLE_LAP980_HG6S_ACCEPTANCE_KEY_FOCUS_G7_OBSERVE_HANDOFF.md` §4.
- 이번 lap 산출물(공유 temp, 직접 생성): `temp/Syw2plus_patch/20261005_lap983_middle_review/`
  - `recalc_lap983.py`→`recalc_lap983.json`(SHA256 `14dc8474fff1d2e415e19e47842ebde709723984041f2150b3fdfebc5650931e`)
  - `save_parse.py`→`save_parse_lap983.json`(`e470b31b1ae419f09dc39bf50de3692a83bab46bac597dd845b377c929199c91`)
  - `port_bytes.py`→`port_bytes_lap983.json`(`08342c44f3d75166419f8218c47e56ad853fe7f86e08d8f5ef2fe7897ac37382`)
  - `cave_check_lap983.txt`(§4 cave 56 B 조립·역어셈블, `e6a6c5f5…dcbc6ff`)
  - `disr.py`·`xref.py`, 역어셈블 `orig_save_440C20.txt`(`ce20b93e…dbde5b`)·`orig_load_440FF0.txt`(`cc5f27f2…02f84`)
- EXE: 원본 `b56986e0…a8ac`, 이식판 normal `0e28ef57…d257` — 이번 lap 직접 sha256 MATCH.

## §1 독립 재계산 (제품 helper 미사용, stdlib만)

probe-result 두 개 SHA256(port `cb7b7151…df53f`, orig `92fea0ca…d927c`)이 lap982 기록 앞 16자와 일치. 각 stage의 `table_hex`(VA `0x632C9C`부터)를 직접 풀어
id 칸 `0x632CA0[0..7]`·행 `0x632CC0+6i`·`0x632CF0[i]`를 다시 읽고, `0x43AF40` 규칙(own id와 첫 일치 index)으로 local을 재계산했다. 기록과 **불일치 0**(ids·first_match·table SHA·save 파일 SHA).

| stage | P(이식판) = O(원본) |
|---|---|
| A 시작 | ids `[1,1,0,0,0,0,0,0]`, own 0 → 첫 일치 2 = local 2. 행1 `05 01 01 02 00 01`(컴퓨터), 행2 `05 02 00 04 00 02`(사람, `+2`=0), 행0 상태 0(빈 자리) |
| B 저장 | `save001.dat` SHA 기록과 일치(P 1,926,354 B·O 1,713,222 B) |
| C 인게임 로드 | ps `[3]`·local `[2]`·선택 owner `[2]`, 표 불변. bridge state ai: owner2만 0 |
| D 타이틀 로드(새 프로세스) | 로드 전·후 ids 전부 0, **행 상태 바이트 전부 0**, own 0 → 첫 일치 0 = local 0. ps `[3,27,29]` |

판정: **H-G7o PASS(관측) 수용.** 결함은 P·O 동일하게 재현(원본 결함), R1(로드 뒤 `0x43AF40`만 재호출)은 live 표가 비어 있어 local 0을 줄 뿐이므로 **불가** 확인.
DESIGN G7 사용자 합격 아님.

## §2 새 정적 근거 — 저장 스트림에 이미 로비 스냅샷이 있다 (원본 capstone, 이식판 바이트 대조)

- 저장 `0x440C20`/로드 `0x440FF0`은 같은 순서로 블록을 쓴다/읽는다. 마지막 고정 블록 두 개:
  `0x892410` 크기 `0xE397C`(플레이어 구조체 `0x956770`+owner×`0x3ABC` 포함) → **`0x632F7C` 크기 `0x170`(=0x5C dword)**. 이어 `0x4464D0`·`0x40F4F0` 가변부, fclose(`0x44130B`).
- `0x632F7C`는 **게임 시작 때 live 로비 표 `0x632C9C`를 그대로 복사한 스냅샷**이다: `0x41B9CA..0x41B9DB`·`0x41BC59..0x41BC6A`(`mov ecx,0x5C; esi=0x632C9C; edi=0x632F7C; rep movsd`), 호출자 ps 핸들러 `0x424D50`(→ ps3).
- 게임 자신도 반대 방향 복원을 쓴다: ps 핸들러 `0x424DA0`(dispatch `0x4234BB`)이 `[0x9E1DD8]==0`이면 `0x632F7C→0x632C9C` 0x5C dword 복사 후 ps=2. 로드 `0x440FF0`은 이 복사도 `0x43AF40`도 부르지 않는다.
- 로드 끝 `0x4414DA`가 `[0xB63FC4]`로 플레이어 구조체 byte 0(국가)을 읽어 `0x419B50`에 넘긴다 → 로드 뒤 UI가 local에 의존. 그 앞 `0x441448..0x441486`(`0x4A4280`·`0x42FAF0`·`0x416190`·`0x48EB90`·`0x420440`·`0x41FB60`)도 local 의존 가능 → **수리는 fclose 직후 `0x441310`에서** 해야 그 뒤 모든 처리가 올바른 local을 본다.
- `0x43AF40`: cdecl 1인자(out ptr), `0x439B90`(ecx=`0x632C08`, own id) → `0x632CA0[0..7]` 첫 일치 index를 out에 쓰고 1, 없으면 out 불변·0. 레지스터 eax/ecx/edx 파괴, esi/edi 보존.
- 저장 파일 직접 파싱(`save_parse_lap983.json`): 두 save 모두 스냅샷 0x170 B가 정확히 1곳(P off 1,827,770·O off 1,704,974) = A stage live 표와 byte 동일 → ids `[1,1,0,…]`, 행 상태 5(자리1·2), 행2 사람. own 0 기준 첫 일치 **2**. 헤더 뒤 `[0x4ED848]` word = 1(두 save), `[0x9E1DD8]`=0.
  O는 `0x892410` 블록 안 플레이어 구조체도 읽힘(tick 127, owner2 ai=0·나머지 1 = C state와 일치). P는 G2 fread 래퍼로 블록 배치가 달라 이번에 파싱하지 않음(UNKNOWN, 판단에 불필요).
- 이식판 대조(`port_bytes_lap983.json`): `0x440FF0..0x441500` 차이 13바이트 = fread 래퍼 2곳(`0x441041`·`0x4412DD`)·fclose→G5SC 체인(`0x44130C`)·풀 상한(`0x441444`)뿐. `0x43AF40`·`0x439B90`·`0x424DA0`·혼자하기 초기화 `0x4B6355..` 동일. **`0x441310` old bytes `8B 2D 2C AF B3 00`(`mov ebp,[0xB3AF2C]`) 원본=이식판.**
  `.g5code`(`0x18A7000`, 0x1000) 이식판 마지막 비0 = +0x8DA, G6 cave +0xC00. **+0xD00(`0x18A7D00`)~ 비어 있음.**
- 혼자하기 판별: 혼자하기 초기화 `0x4B6355`가 `cmp word [0x4ED848], bp`(ids도 같은 bp로 채움, 솔로 기본 ids=1)로 분기하고, 두 솔로 save의 `[0x4ED848]`=1. 쓰기는 `0x4397C9` 하나(로드 스트림 제외). 멀티에서의 값은 UNKNOWN.

## §3 수리 경로 판정 — R4 채택 (R2·R3는 대안으로 보존)

| 경로 | 내용 | 판단 |
|---|---|---|
| R1 | 로드 뒤 `0x43AF40`만 | **불가**(live 표 비어 있음, §1 D) |
| R2 | G5SC 뒤 태그+local DWORD 저장/복원 | 보류: 저장 형식 변경·G2/G5 sidecar 위상 위험, **기존 세이브는 계속 결함**(DESIGN “기존 세이브 호환”에 불리), 참가자 행은 여전히 빈 채 |
| R3 | 로드 뒤 플레이어 구조체 ai==0 owner로 local | 대안(fallback): 데이터는 저장됨(O 확인). 그러나 참가자 행(상태 0)이 빈 채라 ps27(떠남)이 남을 수 있고, 사람 여럿(멀티) 모호 |
| **R4** | 로드 끝(`0x441310`)에서 솔로이면 **저장 스냅샷 `0x632F7C`→live `0x632C9C` 0x5C dword 복사(게임 `0x424DB4`와 같은 복사) 뒤 `0x43AF40(&0xB63FC4)`** | **채택**: 저장 형식 불변(G2/G5 sidecar 무접촉), 기존 세이브에도 적용, 참가자 행까지 복원, local은 게임 자체 규칙. 인게임 로드는 같은 표를 다시 쓰므로 무변화 |

R4 위험(측정으로 판정): (a) 새 프로세스의 own id가 저장 당시와 다르면 첫 일치가 없어 local 불변(0) — lap982 A·D 모두 own 0(P·O, 프로세스 4개)이라 솔로에서는 상수로 보이나 1 자리 관측뿐. (b) 표 복원이 로비/네트워크 부작용을 낼 가능성 — 솔로 게이트로 한정. (c) ps27의 원인이 표/local 밖에 있을 가능성.

## §4 다음 work H-G7r — R4 최소 구현·격리 실행 (사전등록, 1 work lap)

구현(Sonnet work, 신규 파일만; 제품 기존 파일·G6 후보·bridge 불변):
- `patches/selection/g7_title_load_seat_restore.py`(가칭): 입력 이식판 normal `0e28ef57…`/fixed_start `703deaf4…` SHA 가드(G6 patch와 같은 방식), **G6 후보 위에 쌓은 입력도 허용**(G6 cave +0xC00과 비중첩 검사).
  - hook `0x441310` old `8B 2D 2C AF B3 00` → `E9 rel32(→0x18A7D00) 90`.
  - cave `0x18A7D00`(old 전부 0 확인):
    `60 9C`(pushad·pushfd) · `66 83 3D 48 D8 4E 00 01`(cmp word [0x4ED848],1) · `75 xx`(jne skip) ·
    `BE 7C 2F 63 00`·`BF 9C 2C 63 00`·`B9 5C 00 00 00`·`FC`·`F3 A5`(스냅샷→live) ·
    `68 C4 3F B6 00`·`E8 rel32(→0x43AF40)`·`83 C4 04` · skip: `9D 61`(popfd·popad) · `8B 2D 2C AF B3 00`(원래 명령) · `E9 rel32(→0x441316)`.
  - rollback: 후보 → 입력 SHA byte-exact. 테스트 RED→GREEN: SHA 가드·old bytes·cave 인코딩(capstone 역어셈블 일치)·0 영역·G6와 비중첩/순서 무관·rollback.
- 하네스: `tools/g7_save_load_probe.py`에 `--variant cand`(G7 후보, 선택적으로 G6+G7) 추가만. 기존 port/orig 경로 불변.

런타임(격리 사본·prefix·Xvfb, lobby-snapshot seat):
- **R-1 수정(주):** cand, seat 2 → 저장 → **새 프로세스 타이틀 로드** → ps3 진입 뒤 local=2, live ids = 저장 스냅샷(`[1,1,0,…]`)·행2 상태 5, 30초 ps `[3]`만(27/29 0), 전체 드래그 선택 ≥1이 모두 owner 2.
- **R-2 인게임 로드 대조:** cand에서 lap982 C와 같게 local `[2]`·ps `[3]`·선택 owner 2.
- **R-3 1P 회귀:** cand seat 0(기본 솔로, snapshot 미사용) 저장 → 새 프로세스 타이틀 로드 → local 0·ps `[3]`·선택 owner 0.
- **R-4 기존 세이브:** lap982 P가 만든 `save001.dat`(SHA `7e92e474…`, 미패치 이식판 저장)를 cand에 넣고 타이틀 로드 → local 2·ps `[3]`(형식 변경 없이 기존 세이브 수리).
- **R-5 안전:** 후보 SHA 기록, 원본/입력 EXE 불변, 변경 바이트 = hook 6 + cave, G5SC sidecar 로드 크래시 0, 게임 사본 정리.
- 기록할 값: 로드 직후 `[0x4ED848]`, own id `[0xC0D11C]`, live/스냅샷 ids·행, ps 순서.
- 선택(시간 남으면): **같은 프로세스**에서 타이틀로 나갔다가 로드(R-1b). 못 하면 UNKNOWN으로 남긴다.

반증/분기:
- (i) R-1에서 local 0 유지(첫 일치 없음 = own id 변동) → R4 FAIL, 다음 가설 R3(솔로 게이트 + ai==0 owner 단일일 때만 local)로 middle 판정.
- (ii) local 2인데 ps27/29 발생 → 표/local 밖 원인. ps 전이·행/플레이어 상태를 덤프하고 ESCALATE_SOL.
- (iii) 로드 크래시·R-2/R-3 회귀 → 후보 불수용, 원인 추적 후 재실행(③ 반복 원칙).
- O(원본)는 패치 대상이 아니다(lap982 D가 결함 기준).

이 work 결과는 다음 middle이 독립 재계산한다. 기술 PASS(partial)도 DESIGN G7 사용자 합격이 아니다(사용자 ↑/↓ 경로 동일성 UNKNOWN 유지).
